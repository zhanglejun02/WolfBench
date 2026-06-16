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
from wolfbench.defense.distilled import DistilledWolfGuardPolicy
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
    """Upper-bound baseline: reads explicitly supplied ground-truth harmful
    pressure and triggers proportional interventions.

    Excluded from the official leaderboard.
    """
    name: str = "Oracle-WolfGuard"
    config: WolfGuardConfig = field(default_factory=WolfGuardConfig)
    risk_warning: float = 0.001
    risk_cooldown: float = 0.005
    risk_block: float = 0.02
    clean_baseline: dict = field(default_factory=dict)

    def fit_baseline(self, baseline):
        self.clean_baseline = baseline

    def decide(self, day, summary):
        oracle = summary.get("oracle_view", {}) or {}
        out = {}
        for asset, info in oracle.items():
            pressure = max(
                float(info.get("active_harmful_share", 0.0)),
                float(info.get("harmful_agent_share", 0.0)),
                float(info.get("harmful_pressure", 0.0)),
            )
            if not info.get("is_attack_target", 0.0) and pressure <= 0.0:
                continue
            risk = min(1.0, pressure / max(self.risk_block, 1e-9))
            if pressure >= self.risk_block:
                action = "block"
            elif pressure >= self.risk_cooldown:
                action = "cooldown"
            elif pressure >= self.risk_warning:
                action = "warning"
            else:
                continue
            out[asset] = make_intervention(asset, action, risk=risk,
                                           reason="oracle",
                                           components={"oracle_pressure": pressure})
        return out


# ---------------------------------------------------------------- LLM
def _llm_policy_factory(model: str | None = None,
                        provider: str | None = None,
                        base_url: str | None = None,
                        api_key: str | None = None,
                        strict: bool | None = None,
                        display_name: str | None = None,
                        assisted: bool = False):
    """Return an ``LLMWolfGuardAgent`` wrapper. Imported lazily so users
    without an OpenAI client installed can still use rule baselines."""
    from wolfbench.agents.llm import (
        LLMRuleAssistWolfGuardAgent, LLMWolfGuardAgent,
        RuleFallbackBackend, make_chat_backend,
    )
    if model or provider or base_url or api_key:
        backend = make_chat_backend(
            provider=provider, model=model, base_url=base_url,
            api_key=api_key, strict=strict,
        )
    else:
        backend = RuleFallbackBackend()
    agent_cls = LLMRuleAssistWolfGuardAgent if assisted else LLMWolfGuardAgent
    agent = agent_cls(backend=backend, config=WolfGuardConfig())
    agent.name = display_name or f"LLM-WolfGuard({getattr(backend, 'model', 'rule_fallback')})"
    return agent


class LLMWolfGuardPolicy:
    """Factory shim for documentation; instantiate via ``get_policy('llm')``."""
    name: str = "LLM-WolfGuard"


class QwenVLLMWolfGuardPolicy:
    """Factory shim; instantiate via ``get_policy('qwen')``."""
    name: str = "Qwen3-vLLM-WolfGuard"


TRACKS = {
    "noguard": "control",
    "random": "control",
    "rule": "rule_baseline",
    "oracle": "oracle_upper_bound",
    "llm": "llm_from_scratch",
    "qwen": "llm_from_scratch",
    "llm_assisted": "llm_assisted_rule",
    "qwen_assisted": "llm_assisted_rule",
    "distilled": "simulator_trained_baseline",
}


def get_track(name: str) -> str:
    return TRACKS.get(name.lower(), "submission")


# ---------------------------------------------------------------- Registry
BASELINES = {
    "noguard": NoGuardPolicy,
    "random": RandomGuardPolicy,
    "rule": RuleWolfGuardPolicy,
    "oracle": OracleWolfGuardPolicy,
    "distilled": DistilledWolfGuardPolicy,
}


def get_policy(name: str, **kwargs):
    """Instantiate a baseline by short name.

    ``name`` ∈ ``{noguard, random, rule, oracle, distilled, llm, qwen,
    llm_assisted, qwen_assisted}``. ``llm`` accepts
    a ``model`` kwarg (defaults to the deterministic rule fallback). ``qwen``
    uses the local vLLM OpenAI-compatible endpoint by default. ``distilled``
    accepts ``model_path`` or reads ``WOLFBENCH_DISTILLED_MODEL``.
    """
    key = name.lower()
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    if key in {"llm", "llm_assisted"}:
        return _llm_policy_factory(
            model=kwargs.get("model"),
            provider=kwargs.get("provider"),
            base_url=kwargs.get("base_url"),
            api_key=kwargs.get("api_key"),
            strict=kwargs.get("strict"),
            assisted=key.endswith("_assisted"),
        )
    if key in {"qwen", "qwen_assisted"}:
        model = kwargs.get("model") or "qwen3-8b"
        return _llm_policy_factory(
            model=model,
            provider="vllm",
            base_url=kwargs.get("base_url"),
            api_key=kwargs.get("api_key"),
            strict=True if kwargs.get("strict") is None else kwargs.get("strict"),
            display_name=f"Qwen3-vLLM{'-assisted' if key.endswith('_assisted') else ''}({model})",
            assisted=key.endswith("_assisted"),
        )
    kwargs = {k: v for k, v in kwargs.items()
              if k not in {"model", "provider", "base_url", "api_key", "strict"}}
    if key not in BASELINES:
        raise ValueError(
            f"Unknown defense baseline '{name}'. "
            f"Available: {sorted(BASELINES) + ['llm', 'qwen', 'llm_assisted', 'qwen_assisted']}"
        )
    if key != "distilled":
        kwargs.pop("model_path", None)
    return BASELINES[key](**kwargs)
