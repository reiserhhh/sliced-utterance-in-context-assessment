"""Creation-only estimator interventions for SUICA M4-C.3.2."""
from __future__ import annotations

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import spearmanr

from .m4_physical_edge_composition import M4PhysicalEdgeView


def compose_creation_only_loop(
    creation: np.ndarray,
    frozen_route: M4PhysicalEdgeView,
) -> np.ndarray:
    """Compose one candidate creation edge with frozen response and choice."""
    values = np.asarray(creation, dtype=float)
    if values.shape != frozen_route.creation.shape:
        raise ValueError(
            "candidate creation must match the frozen physical edge shape"
        )
    return np.einsum(
        "acd,adk,akj->acj",
        values,
        frozen_route.response,
        frozen_route.choice,
        optimize=True,
    )


def author_relation_geometry(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    """Compare author pairwise geometry after flattening each operator."""
    left = np.asarray(first, dtype=float).reshape(len(first), -1)
    right = np.asarray(second, dtype=float).reshape(len(second), -1)
    left_distance = pdist(left)
    right_distance = pdist(right)
    if (
        np.std(left_distance) <= 1e-12
        or np.std(right_distance) <= 1e-12
    ):
        return 0.0
    value = float(spearmanr(left_distance, right_distance).statistic)
    return value if np.isfinite(value) else 0.0


def relative_headroom_recovery(
    baseline: float,
    candidate: float,
    oracle_swap: float,
    *,
    tolerance: float = 1e-12,
) -> float:
    """Return the candidate fraction of oracle creation-swap headroom."""
    headroom = float(oracle_swap - baseline)
    if headroom <= tolerance:
        return float("nan")
    return float((candidate - baseline) / headroom)
