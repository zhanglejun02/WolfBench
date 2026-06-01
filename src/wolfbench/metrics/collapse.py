"""CollapseScore + episode-level metrics."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class EpisodeMetrics:
    horizon_days: int
    target_asset: str
    daily_collapse_score: list[float] = field(default_factory=list)
    daily_components: list[dict[str, float]] = field(default_factory=list)
    collapse_day: int | None = None        # first day collapse triggered
    collapse_rate: float = 0.0             # 1.0 if collapsed in episode else 0.0
    max_collapse_score: float = 0.0
    retail_loss_30d: float = 0.0
    retail_loss_pct_30d: float = 0.0
    price_dislocation_max: float = 0.0
    liquidity_stress_max: float = 0.0
    social_cascade_peak: float = 0.0
    wealth_transfer: float = 0.0           # harmful_profit / |retail_loss|
    harmful_profit: float = 0.0
    intervention_cost: float = 0.0
    false_positive_rate: float = 0.0
    utility_loss: float = 0.0


def compute_collapse_score(components: dict[str, float],
                           weights: dict[str, float] | None = None) -> float:
    w = weights or {
        "retail_loss": 1.0,
        "price_dislocation": 0.8,
        "liquidity_stress": 0.6,
        "social_cascade": 0.5,
        "wealth_transfer": 0.7,
    }
    return float(sum(w[k] * components.get(k, 0.0) for k in w))


def collapse_triggered(components: dict[str, float],
                       thresholds: dict[str, float] | None = None) -> bool:
    t = thresholds or {
        "retail_loss": 0.10,        # 10% retail wealth loss
        "price_dislocation": 0.30,  # 30% deviation from fundamental
        "liquidity_stress": 3.0,    # 3 sigma over clean spread
        "social_cascade": 0.40,     # 40% retail exposed/adopted
        "wealth_transfer": 0.05,    # 5% of retail wealth captured by harmful
    }
    return any(components.get(k, 0.0) >= v for k, v in t.items())
