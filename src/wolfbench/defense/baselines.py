"""Canonical defense baselines shipped with WolfBench v1.

Run any of these by name through the CLI::

    wolfbench evaluate --defense rule --scenario s1 --alpha 0.05

or programmatically::

    from wolfbench.defense import get_policy
    pol = get_policy("rule")
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from wolfbench.agents.wolfguard import WolfGuardAgent, WolfGuardConfig
from wolfbench.defense.policy import make_intervention


# ---------------------------------------------------------------- NoGuard
@dataclass
class NoGuardPolicy:
    """Reference baseline: never intervenes. Used to compute ΔH for scoring."""
    name: str = "NoGuard"
    config: WolfGuardConfig = field(default_factory=lambda: WolfGuardConfig(mode="off"))
    clean_baseline: dict = field(default_factory=dict)

    def fit_baseline(self, baseline):
        self.clean_baseline = baseline

    def decide(self, day, summary):
        return {}


# ---------------------------------------------------------------- Random
@dataclass
class RandomGuardPolicy:
    """Sanity-check baseline: each day issues random warnings/cooldowns.

    Should score near (or below) NoGuard because it pays utility cost without
    information.
    """
    name: str = "RandomGuard"
    config: WolfGuardConfig = field(default_factory=WolfGuardConfig)
    seed: int = 0
    p_warn: float = 0.15
    p_cooldown: float = 0.05
    clean_baseline: dict = field(default_factory=dict)
    _rng: np.random.Generator = field(init=False)

    def __post_init__(self):
        self._rng = np.random.default_rng(self.seed)

    def fit_baseline(self, baseline):
        self.clean_baseline = baseline

    def decide(self, day, summary):
        out = {}
        for asset in summary["market"]:
            r = float(self._rng.random())
            if r < self.p_cooldown:
                out[asset] = make_intervention(asset, "cooldown", risk=0.7,
                                               reason="random")
            elif r < self.p_cooldown + self.p_warn:
                out[asset] = make_intervention(asset, "warning", risk=0.5,
                                               reason="random")
        return out


# ---------------------------------------------------------------- Rule
class RuleWolfGuardPolicy(WolfGuardAgent):
    """The z-score rule detector originally shipped as ``WolfGuardAgent``.

    It is the canonical non-learning baseline that defense submissions must
    beat to claim contribution.
    """
    name: str = "Rule-WolfGuard"


# ---------------------------------------------------------------- Oracle
@dataclass
class OracleWolfGuardPolicy:
    """Upper-bound baseline: reads ``summary['oracle_view']`` (ground-truth
    harmful pressure leaked by the env) and triggers proportional interventions.

    Excluded from the official leaderboard.
    """
    name: str = "Oracle-WolfGuard"
    config: WolfGuardConfig = field(default_factory=WolfGuardConfig)
    risk_warning: float = 0.10
    risk_cooldown: float = 0.25
    risk_block: float = 0.40
    clean_baseline: dict = field(default_factory=dict)

    def fit_baseline(self, baseline):
        self.clean_baseline = baseline

    def decide(self, day, summary):
        oracle = summary.get("oracle_view", {}) or {}
        out = {}
        for asset, info in oracle.items():
            risk = float(info.get("harmful_pressure", 0.0))
            if risk >= self.risk_block:
                action = "block"
            elif risk >= self.risk_cooldown:
                action = "cooldown"
            elif risk >= self.risk_warning:
                action = "warning"
            else:
                continue
            out[asset] = make_intervention(asset, action, risk=risk,
                                           reason="oracle",
                                           components={"oracle": risk})
        return out


# ---------------------------------------------------------------- LLM
def _llm_policy_factory(model: str | None):
    """Return an ``LLMWolfGuardAgent`` wrapper. Imported lazily so users
    without an OpenAI client installed can still use rule baselines."""
    from wolfbench.agents.llm import (
        LLMWolfGuardAgent, OpenAIChatBackend, RuleFallbackBackend,
    )
    backend = OpenAIChatBackend(model=model) if model else RuleFallbackBackend()
    agent = LLMWolfGuardAgent(backend=backend, config=WolfGuardConfig())
    agent.name = f"LLM-WolfGuard({model or 'rule_fallback'})"
    return agent


class LLMWolfGuardPolicy:
    """Factory shim for documentation; instantiate via ``get_policy('llm')``."""
    name: str = "LLM-WolfGuard"


# ---------------------------------------------------------------- Registry
BASELINES = {
    "noguard": NoGuardPolicy,
    "random": RandomGuardPolicy,
    "rule": RuleWolfGuardPolicy,
    "oracle": OracleWolfGuardPolicy,
}


def get_policy(name: str, **kwargs):
    """Instantiate a baseline by short name.

    ``name`` ∈ ``{noguard, random, rule, oracle, llm}``. ``llm`` accepts a
    ``model`` kwarg (defaults to the deterministic rule fallback).
    """
    key = name.lower()
    if key == "llm":
        return _llm_policy_factory(kwargs.get("model"))
    kwargs = {k: v for k, v in kwargs.items() if k != "model"}
    if key not in BASELINES:
        raise ValueError(
            f"Unknown defense baseline '{name}'. "
            f"Available: {sorted(BASELINES) + ['llm']}"
        )
    return BASELINES[key](**kwargs)
