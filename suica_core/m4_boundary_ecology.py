"""Outcome-blind support interventions for M4-C.3.5 boundary ecology."""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
from scipy.spatial.distance import cdist, pdist, squareform

from .m4_condition_manifold_contracts import M4ConditionObserved
from .m4_response_safe_rcca_chart import M4RCCAChartTransform


HELDOUT_PANELS = (
    "reference_selection",
    "mechanism_calibration",
    "mechanism_selection",
    "mechanism_evaluation",
)


@dataclass(frozen=True)
class M4SupportGeometry:
    """Pre-response kNN support geometry under one frozen RCCA chart."""

    threshold: float
    role_masks: dict[str, np.ndarray]
    role_distances: dict[str, np.ndarray]
    role_coverage: dict[str, float]
    minimum_coverage: float


@dataclass(frozen=True)
class M4SupportIntervention:
    """One deterministic intervention and its realized support geometry."""

    observed: M4ConditionObserved
    selected_conditions: tuple[int, ...]
    target_count: int
    realized_count: int
    geometry: M4SupportGeometry


def support_geometry(
    chart: M4RCCAChartTransform,
    observed: M4ConditionObserved,
) -> M4SupportGeometry:
    """Return role-wise third-neighbor support masks and distances."""
    reference = chart.transform_prototypes(
        observed.reference_calibration.pre_context
    )[:, 1:]
    distances = squareform(pdist(reference))
    np.fill_diagonal(distances, np.inf)
    neighbors = min(3, len(reference) - 1)
    calibration_knn = np.partition(
        distances,
        neighbors - 1,
        axis=1,
    )[:, neighbors - 1]
    threshold = float(np.quantile(calibration_knn, 0.99))
    masks: dict[str, np.ndarray] = {}
    heldout_distances: dict[str, np.ndarray] = {}
    coverage: dict[str, float] = {}
    for role in HELDOUT_PANELS:
        values = chart.transform_prototypes(
            getattr(observed, role).pre_context
        )[:, 1:]
        current = cdist(values, reference)
        neighbor_index = min(neighbors - 1, current.shape[1] - 1)
        knn = np.partition(
            current,
            neighbor_index,
            axis=1,
        )[:, neighbor_index]
        mask = knn <= threshold
        masks[role] = mask
        heldout_distances[role] = knn
        coverage[role] = float(np.mean(mask))
    return M4SupportGeometry(
        threshold=threshold,
        role_masks=masks,
        role_distances=heldout_distances,
        role_coverage=coverage,
        minimum_coverage=float(min(coverage.values())),
    )


def intervene_evaluation_support(
    observed: M4ConditionObserved,
    chart: M4RCCAChartTransform,
    *,
    target_count: int,
    amplitude_multiplier: float = 16.0,
) -> M4SupportIntervention:
    """Move the least-supported in-domain evaluation points out of support.

    The RCCA map is frozen first. Only pre-response evaluation coordinates are
    moved, identically across authors and coherently across the two sources.
    Response arrays and every other panel remain byte-identical.
    """
    panel = observed.mechanism_evaluation
    categories = panel.pre_context.shape[2]
    if target_count < 0 or target_count > categories:
        raise ValueError("target_count is outside the evaluation support")
    before = support_geometry(chart, observed)
    mask = before.role_masks["mechanism_evaluation"]
    current_count = int(np.sum(mask))
    if target_count > current_count:
        raise ValueError(
            "boundary intervention cannot create missing native support"
        )
    remove = current_count - int(target_count)
    if remove == 0:
        return M4SupportIntervention(
            observed=observed,
            selected_conditions=(),
            target_count=int(target_count),
            realized_count=current_count,
            geometry=before,
        )

    distances = before.role_distances["mechanism_evaluation"]
    candidates = np.flatnonzero(mask)
    order = candidates[
        np.argsort(distances[candidates], kind="stable")[::-1]
    ]
    selected = tuple(int(value) for value in order[:remove])
    reference = chart.transform_prototypes(
        observed.reference_calibration.pre_context
    )[:, 1:]
    center = np.mean(reference, axis=0)
    evaluation = chart.transform_prototypes(panel.pre_context)[:, 1:]
    scale = max(
        float(before.threshold),
        float(np.max(np.linalg.norm(reference - center, axis=1))),
        1e-6,
    )
    pre = np.asarray(panel.pre_context, dtype=float).copy()
    inverses = tuple(
        np.linalg.pinv(np.asarray(source_map, dtype=float))
        for source_map in chart.source_maps
    )
    for condition in selected:
        direction = evaluation[condition] - center
        norm = float(np.linalg.norm(direction))
        if norm <= 1e-12:
            direction = np.zeros(chart.shared_rank, dtype=float)
            direction[condition % chart.shared_rank] = 1.0
        else:
            direction = direction / norm
        scaled_shift = (
            direction
            * scale
            * float(amplitude_multiplier)
        )
        canonical_shift = scaled_shift / max(chart.output_scale, 1e-12)
        for source in range(2):
            raw_shift = canonical_shift @ inverses[source]
            pre[source, :, condition, :] += raw_shift

    changed = replace(panel, pre_context=pre)
    result = replace(observed, mechanism_evaluation=changed)
    after = support_geometry(chart, result)
    realized = int(
        np.sum(after.role_masks["mechanism_evaluation"])
    )
    if realized != target_count:
        raise ValueError(
            "support intervention missed target: "
            f"requested {target_count}, realized {realized}"
        )
    return M4SupportIntervention(
        observed=result,
        selected_conditions=selected,
        target_count=int(target_count),
        realized_count=realized,
        geometry=after,
    )
