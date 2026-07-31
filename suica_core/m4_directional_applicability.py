"""Fixed-coverage directional interventions for M4 chart applicability."""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

from .m4_boundary_ecology import M4SupportGeometry, support_geometry
from .m4_condition_manifold_contracts import M4ConditionObserved
from .m4_response_safe_rcca_chart import M4RCCAChartTransform


DIRECTION_MODES = (
    "radial_dispersed",
    "radial_concentrated",
    "tangential_rotation",
    "source_asymmetric",
)


@dataclass(frozen=True)
class M4DirectionalIntervention:
    """One outcome-blind directional support intervention."""

    observed: M4ConditionObserved
    mode: str
    selected_conditions: tuple[int, ...]
    target_count: int
    realized_count: int
    geometry: M4SupportGeometry


def _unit(values: np.ndarray, fallback: int) -> np.ndarray:
    vector = np.asarray(values, dtype=float)
    norm = float(np.linalg.norm(vector))
    if norm > 1e-12:
        return vector / norm
    result = np.zeros_like(vector)
    result[fallback % len(result)] = 1.0
    return result


def _dispersed_order(
    candidates: np.ndarray,
    directions: np.ndarray,
) -> np.ndarray:
    """Greedily maximize angular separation with deterministic tie breaks."""
    if len(candidates) <= 1:
        return candidates.copy()
    norms = np.linalg.norm(directions[candidates], axis=1)
    first = int(candidates[np.argmax(norms)])
    selected = [first]
    remaining = [int(value) for value in candidates if value != first]
    while remaining:
        scores = []
        for condition in remaining:
            direction = _unit(directions[condition], condition)
            maximum_similarity = max(
                abs(float(direction @ _unit(directions[other], other)))
                for other in selected
            )
            scores.append((maximum_similarity, condition))
        _, chosen = min(scores)
        selected.append(chosen)
        remaining.remove(chosen)
    return np.asarray(selected, dtype=int)


def _concentrated_order(
    candidates: np.ndarray,
    directions: np.ndarray,
) -> np.ndarray:
    """Order conditions around the highest-leverage canonical direction."""
    norms = np.linalg.norm(directions[candidates], axis=1)
    pole = int(candidates[np.argmax(norms)])
    pole_direction = _unit(directions[pole], pole)
    scored = []
    for condition in candidates:
        direction = _unit(directions[int(condition)], int(condition))
        similarity = float(direction @ pole_direction)
        scored.append((-similarity, -float(norms[np.where(candidates == condition)[0][0]]), int(condition)))
    return np.asarray([value[2] for value in sorted(scored)], dtype=int)


def _tangent(direction: np.ndarray, fallback: int) -> np.ndarray:
    """Return a deterministic unit vector orthogonal to ``direction``."""
    radial = _unit(direction, fallback)
    if len(radial) == 1:
        return -radial
    candidate = np.roll(radial, 1)
    candidate = candidate - float(candidate @ radial) * radial
    if float(np.linalg.norm(candidate)) <= 1e-12:
        candidate = np.zeros_like(radial)
        candidate[(int(np.argmax(np.abs(radial))) + 1) % len(radial)] = 1.0
        candidate = candidate - float(candidate @ radial) * radial
    return _unit(candidate, fallback + 1)


def intervene_evaluation_direction(
    observed: M4ConditionObserved,
    chart: M4RCCAChartTransform,
    *,
    target_count: int,
    mode: str,
    amplitude_multiplier: float = 16.0,
) -> M4DirectionalIntervention:
    """Hold support count fixed while changing departure geometry.

    Only the evaluation ``pre_context`` tensor is changed. The intervention is
    identical across authors. Three modes perturb both sources coherently;
    ``source_asymmetric`` perturbs source zero only, with a doubled canonical
    displacement so its fused magnitude is comparable.
    """
    if mode not in DIRECTION_MODES:
        raise ValueError(f"unknown directional intervention: {mode}")
    panel = observed.mechanism_evaluation
    categories = panel.pre_context.shape[2]
    if target_count < 0 or target_count > categories:
        raise ValueError("target_count is outside the evaluation support")
    before = support_geometry(chart, observed)
    mask = before.role_masks["mechanism_evaluation"]
    current_count = int(np.sum(mask))
    remove = current_count - int(target_count)
    if remove <= 0:
        raise ValueError(
            "directional intervention requires native support above target"
        )

    reference = chart.transform_prototypes(
        observed.reference_calibration.pre_context
    )[:, 1:]
    center = np.mean(reference, axis=0)
    evaluation = chart.transform_prototypes(panel.pre_context)[:, 1:]
    radial = evaluation - center
    candidates = np.flatnonzero(mask)
    if mode == "radial_concentrated":
        order = _concentrated_order(candidates, radial)
    else:
        order = _dispersed_order(candidates, radial)
    selected = tuple(int(value) for value in order[:remove])

    scale = max(
        float(before.threshold),
        float(np.max(np.linalg.norm(reference - center, axis=1))),
        1e-6,
    )
    pole = _unit(radial[selected[0]], selected[0])
    inverses = tuple(
        np.linalg.pinv(np.asarray(source_map, dtype=float))
        for source_map in chart.source_maps
    )
    pre = np.asarray(panel.pre_context, dtype=float).copy()
    for condition in selected:
        if mode == "radial_concentrated":
            direction = pole
        elif mode == "tangential_rotation":
            direction = _tangent(radial[condition], condition)
        else:
            direction = _unit(radial[condition], condition)
        canonical_shift = (
            direction
            * scale
            * float(amplitude_multiplier)
            / max(chart.output_scale, 1e-12)
        )
        sources = (0,) if mode == "source_asymmetric" else (0, 1)
        multiplier = 2.0 if mode == "source_asymmetric" else 1.0
        for source in sources:
            raw_shift = (multiplier * canonical_shift) @ inverses[source]
            pre[source, :, condition, :] += raw_shift

    changed = replace(panel, pre_context=pre)
    result = replace(observed, mechanism_evaluation=changed)
    after = support_geometry(chart, result)
    realized = int(np.sum(after.role_masks["mechanism_evaluation"]))
    if realized != target_count:
        raise ValueError(
            "directional intervention missed target: "
            f"requested {target_count}, realized {realized}"
        )
    return M4DirectionalIntervention(
        observed=result,
        mode=mode,
        selected_conditions=selected,
        target_count=int(target_count),
        realized_count=realized,
        geometry=after,
    )
