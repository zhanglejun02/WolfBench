"""WolfBench environment: 30-day MAS episode loop."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Any

import numpy as np

from wolfbench.agents.wolfguard import WolfGuardAgent
from wolfbench.env.market import MarketEnv, Order, TradeRecord
from wolfbench.env.social import SocialEnv, SocialGraph, Message
from wolfbench.metrics.collapse import (
    EpisodeMetrics, compute_collapse_score, collapse_triggered,
)
from wolfbench.scenarios.base import ScenarioConfig
from wolfbench.scenarios.society import Society, build_society
from wolfbench.utils.logging import get_logger

log = get_logger(__name__)


@dataclass
class EpisodeResult:
    scenario_id: str
    n_society: int
    alpha: float
    seed: int
    metrics: EpisodeMetrics
    target_asset: str
    daily_log: list[dict[str, Any]] = field(default_factory=list)
    config_snapshot: dict[str, Any] = field(default_factory=dict)


class WolfBenchEnv:
    """Main 30-day environment.

    Usage::
        env = WolfBenchEnv(scenario, n_society=1000, alpha=0.02, seed=1)
        result = env.run()
    """

    def __init__(self, scenario: ScenarioConfig, n_society: int, alpha: float,
                 seed: int = 0,
                 wolfguard: WolfGuardAgent | None = None,
                 baseline: dict | None = None,
                 placement_override: str | None = None,
                 llm_backend=None,
                 n_llm_leaders: int = 0):
        self.scenario = scenario
        self.n_society = n_society
        self.alpha = alpha
        self.seed = seed
        self.rng = np.random.default_rng(seed)

        self.society: Society = build_society(
            scenario, n_society, alpha, self.rng,
            placement_override=placement_override,
            llm_backend=llm_backend,
            n_llm_leaders=n_llm_leaders,
        )
        # liquidity grows sub-linearly with society size; calibrated so that
        # at N=1000 we recover the YAML base liquidity.
        liquidity_scale = max(0.1, (n_society / 1000.0) ** 0.5)
        self.market = MarketEnv(scenario, np.random.default_rng(seed + 7),
                                liquidity_scale=liquidity_scale)

        self.graph = SocialGraph(
            n_agents=len(self.society.all_agents),
            mean_degree=int(scenario.social.get("mean_degree", 8)),
            rng=np.random.default_rng(seed + 13),
            graph_type=str(scenario.social.get("graph", "scale_free")),
        )
        agent_ids = [a.agent_id for a in self.society.all_agents]
        # placement: optionally swap harmful agent_ids onto top-degree nodes
        if self.society.placement == "high_degree" and self.society.attackers:
            agent_ids = self._place_harmful_on_hubs(agent_ids)
        self.graph.assign_ids(agent_ids)

        self.social = SocialEnv(self.graph, scenario, np.random.default_rng(seed + 23))
        self.wolfguard = wolfguard
        if self.wolfguard is not None and baseline is not None:
            self.wolfguard.fit_baseline(baseline)

        self.target_asset = self.society.target_asset
        self._initial_retail_wealth = sum(a.portfolio.initial_wealth for a in self.society.retail)
        self._initial_harmful_wealth = sum(a.portfolio.initial_wealth for a in self.society.attackers)
        self._intervention_cost = 0.0
        self._false_positive_count = 0
        self._intervention_count = 0
        self._utility_loss = 0.0

    # -----------------------------------------------------------------

    def _place_harmful_on_hubs(self, agent_ids: list[str]) -> list[str]:
        # find top-degree nodes; swap harmful ids into those positions
        n_harm = len(self.society.attackers)
        order = sorted(self.graph.g.degree, key=lambda x: x[1], reverse=True)
        hub_positions = [n for n, _ in order[:n_harm]]
        # node order in agent_ids matches self.graph.agent_nodes order
        node_index = {n: i for i, n in enumerate(self.graph.agent_nodes)}
        ids = list(agent_ids)
        harm_ids = [a.agent_id for a in self.society.attackers]
        # current indices of harmful ids
        current_idx = {ids[i]: i for i in range(len(ids))}
        for hid, hub_node in zip(harm_ids, hub_positions):
            target_pos = node_index[hub_node]
            cur_pos = current_idx[hid]
            if target_pos != cur_pos:
                ids[cur_pos], ids[target_pos] = ids[target_pos], ids[cur_pos]
                # update map
                current_idx[ids[cur_pos]] = cur_pos
                current_idx[ids[target_pos]] = target_pos
        return ids

    # -----------------------------------------------------------------

    def run(self) -> EpisodeResult:
        H = self.scenario.horizon_days
        metrics = EpisodeMetrics(horizon_days=H, target_asset=self.target_asset)
        daily_log: list[dict[str, Any]] = []
        recent_returns: dict[str, list[float]] = defaultdict(list)

        for day in range(H):
            self.market.begin_day()
            prices = {aid: s.price for aid, s in self.market.assets.items()}
            recent_ret = {aid: float(np.mean(recent_returns[aid][-3:])) if recent_returns[aid] else 0.0
                          for aid in self.market.assets}

            # --- WolfGuard chooses interventions BEFORE retail trades ---
            actions: dict[str, dict] = {}
            if self.wolfguard is not None:
                summary = self._system_summary(day, recent_ret)
                actions = self.wolfguard.decide(day, summary)
                self._apply_defense(day, actions)

            # --- agent decisions ---
            observation = self._build_observation(day, prices, recent_ret)
            orders: list[Order] = []
            messages: list[Message] = []
            for ag in self.society.all_agents:
                if hasattr(ag, "decide"):
                    o, m = ag.decide(day, observation)
                    orders.extend(o)
                    messages.extend(m)

            # --- market clearing (single intra-day step) ---
            trades = self.market.submit_orders(day, step=0, orders=orders)
            self._update_portfolios(trades)

            # --- social propagation ---
            market_returns = {}
            for aid, s in self.market.assets.items():
                market_returns[aid] = (s.price - s.last_price) / max(s.last_price, 1e-6)
                recent_returns[aid].append(market_returns[aid])
            self.social.step(day, messages, market_returns)

            self.market.end_day(day)

            # --- metrics ---
            comp = self._collapse_components(day)
            score = compute_collapse_score(comp)
            metrics.daily_collapse_score.append(score)
            metrics.daily_components.append(comp)
            metrics.max_collapse_score = max(metrics.max_collapse_score, score)
            metrics.price_dislocation_max = max(metrics.price_dislocation_max,
                                                comp.get("price_dislocation", 0.0))
            metrics.liquidity_stress_max = max(metrics.liquidity_stress_max,
                                               comp.get("liquidity_stress", 0.0))
            metrics.social_cascade_peak = max(metrics.social_cascade_peak,
                                              comp.get("social_cascade", 0.0))

            if metrics.collapse_day is None and collapse_triggered(comp):
                metrics.collapse_day = day
                metrics.collapse_rate = 1.0

            daily_log.append({
                "day": day,
                "prices": {a: float(s.price) for a, s in self.market.assets.items()},
                "fundamentals": {a: float(s.fundamental) for a, s in self.market.assets.items()},
                "components": comp,
                "collapse_score": score,
                "wolfguard_actions": actions,
            })

        # finalise metrics
        retail_wealth_now = sum(a.portfolio.mark_to_market(prices) for a in self.society.retail)
        metrics.retail_loss_30d = self._initial_retail_wealth - retail_wealth_now
        metrics.retail_loss_pct_30d = metrics.retail_loss_30d / max(self._initial_retail_wealth, 1e-6)
        harmful_now = sum(a.portfolio.mark_to_market(prices) for a in self.society.attackers)
        metrics.harmful_profit = harmful_now - self._initial_harmful_wealth
        if abs(metrics.retail_loss_30d) > 1e-6:
            metrics.wealth_transfer = metrics.harmful_profit / abs(metrics.retail_loss_30d)
        metrics.intervention_cost = self._intervention_cost
        metrics.utility_loss = self._utility_loss
        denom = max(self._intervention_count, 1)
        metrics.false_positive_rate = self._false_positive_count / denom

        return EpisodeResult(
            scenario_id=self.scenario.id,
            n_society=self.n_society,
            alpha=self.alpha,
            seed=self.seed,
            metrics=metrics,
            target_asset=self.target_asset,
            daily_log=daily_log,
            config_snapshot={
                "target_asset": self.target_asset,
                "n_harmful": self.society.n_harmful,
                "placement": self.society.placement,
            },
        )

    # ---------------------------------------------------------------- helpers

    def _build_observation(self, day, prices, recent_ret):
        market_view = self.market.snapshot()
        # volume_z relative to running mean
        volume_z: dict[str, float] = {}
        for aid, s in self.market.assets.items():
            hist = s.history["real_volume"]
            if len(hist) > 3:
                arr = np.array(hist, dtype=float)
                mu, sd = arr.mean(), arr.std() + 1e-6
                volume_z[aid] = float((s.real_volume_today - mu) / sd)
            else:
                volume_z[aid] = 0.0
        # social per-agent exposure is fetched lazily; precompute per asset for retail
        observation = {
            "day": day,
            "prices": prices,
            "market": market_view,
            "recent_return": recent_ret,
            "volume_z": volume_z,
            "social_env": self.social,
        }
        return observation

    def _update_portfolios(self, trades: list[TradeRecord]):
        # Build a mapping agent_id -> agent for fast access
        idx = {a.agent_id: a for a in self.society.all_agents}
        for t in trades:
            if t.is_wash:
                # wash trades happen between colluding accounts; they generate
                # observable volume but must be net-zero for total wealth.
                continue
            buyer = idx.get(t.buyer_id)
            seller = idx.get(t.seller_id)
            if buyer is not None:
                buyer.portfolio.cash -= t.quantity * t.price
                buyer.portfolio.holdings[t.asset] = buyer.portfolio.holdings.get(t.asset, 0.0) + t.quantity
            if seller is not None:
                seller.portfolio.cash += t.quantity * t.price
                seller.portfolio.holdings[t.asset] = seller.portfolio.holdings.get(t.asset, 0.0) - t.quantity

    def _system_summary(self, day, recent_ret) -> dict[str, Any]:
        market_view = self.market.snapshot()
        social_view = {a: self.social.asset_signal(a) for a in self.market.assets}
        oracle_view = self._oracle_view()
        return {
            "day": day,
            "market": market_view,
            "social": social_view,
            "recent_return": recent_ret,
            "oracle_view": oracle_view,
        }

    def _oracle_view(self) -> dict[str, dict[str, float]]:
        """Ground-truth per-asset harmful pressure. Used only by the Oracle
        defense baseline (upper bound); regular submissions ignore this key.
        """
        per_asset_harmful_eq = {a: 0.0 for a in self.market.assets}
        per_asset_total_eq = {a: 1e-9 for a in self.market.assets}
        prices = {aid: s.price for aid, s in self.market.assets.items()}
        for ag in self.society.all_agents:
            equity = ag.portfolio.mark_to_market(prices)
            asset = getattr(ag, "target_asset", self.target_asset)
            per_asset_total_eq[asset] += max(equity, 0.0)
            if getattr(ag, "is_harmful", False):
                per_asset_harmful_eq[asset] += max(equity, 0.0)
        return {
            a: {
                "harmful_pressure": float(
                    per_asset_harmful_eq[a] / per_asset_total_eq[a]
                ),
            }
            for a in self.market.assets
        }

    def _apply_defense(self, day: int, actions: dict[str, dict]) -> None:
        cfg = self.wolfguard.config
        for asset, act in actions.items():
            action = act["action"]
            if action == "none":
                continue
            self._intervention_count += 1
            cost = 0.0
            if action == "warning":
                cost = cfg.intervention_cost_warning
                for r in self.society.retail:
                    r.warning_level[asset] = max(r.warning_level.get(asset, 0.0), act["risk"])
            elif action == "cooldown":
                cost = cfg.intervention_cost_cooldown
                for r in self.society.retail:
                    r.cooldown_until[asset] = day  # skip just today
                    r.warning_level[asset] = max(r.warning_level.get(asset, 0.0), act["risk"])
            elif action == "block":
                cost = cfg.intervention_cost_block
                # Block only suspected erroneous trades: high harmful exposure
                for r in self.society.retail:
                    bb = r.last_belief_breakdown.get(asset, {})
                    if bb.get("harmful_exposure", 0.0) > cfg.err_trade_exposure_threshold:
                        r.blocked_today[asset] = True
                    else:
                        # over-blocked: false positive on this retail agent
                        if act["risk"] > 0.9:
                            self._false_positive_count += 1
            self._intervention_cost += cost
            self._utility_loss += cost

    def _collapse_components(self, day: int) -> dict[str, float]:
        s = self.market.assets[self.target_asset]
        price_disloc = abs(s.price - s.fundamental) / max(s.fundamental, 1e-6)
        spread_z = (s.spread_bps / max(self.market.base_spread_bps, 1e-6)) - 1.0

        prices = {aid: a.price for aid, a in self.market.assets.items()}
        retail_now = sum(a.portfolio.mark_to_market(prices) for a in self.society.retail)
        retail_loss_pct = max(0.0, (self._initial_retail_wealth - retail_now)
                              / max(self._initial_retail_wealth, 1e-6))

        n_retail = max(len(self.society.retail), 1)
        cascade = float(len(self.social.state.cascade_size.get(self.target_asset, set()))) / n_retail

        harmful_now = sum(a.portfolio.mark_to_market(prices) for a in self.society.attackers)
        harmful_profit = harmful_now - self._initial_harmful_wealth
        # Wealth transferred from retail population to harmful actors,
        # expressed as a fraction of total initial retail wealth.
        wt = harmful_profit / max(self._initial_retail_wealth, 1e-6)
        wt = float(np.clip(wt, -1.0, 1.0))

        return {
            "price_dislocation": float(price_disloc),
            "liquidity_stress": float(max(spread_z, 0.0)),
            "retail_loss": float(retail_loss_pct),
            "social_cascade": float(min(cascade, 1.0)),
            "wealth_transfer": float(wt),
        }
