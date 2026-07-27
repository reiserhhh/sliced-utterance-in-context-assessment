"""V3.7H.1 projection and cumulative-path diagnostics.

These functions keep scorer-only projection checks separate from observable
drift diagnostics. Synthetic truth may enter ``scorer_projection_metrics``
only. Cumulative predictors receive observable budget-32 history.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler

from .v8_reliability_spectrum import (
    _haar,
    _scale_rms,
    apply_spectrum_operator,
    unresolved_channel,
)
from .v8_resolution_filtration import (
    _draw_stable,
    _nested_event_noise,
    _variance_spectrum,
)


@dataclass(frozen=True)
class PairedScheduleSpec:
    """Synthetic paired-opportunity schedule design."""

    dimension: int = 48
    budgets: tuple[int, ...] = (32, 64, 128, 256, 512)
    reference_authors: int = 256
    calibration_authors: int = 256
    panel_authors: int = 256
    stable_rms: float = 0.30
    event_rms_at_64: float = 0.40
    opportunity_start: int = 32


def scorer_projection_metrics(
    truth: np.ndarray,
    left_score: np.ndarray,
    right_score: np.ndarray,
    *,
    origin: np.ndarray,
) -> dict[str, float]:
    """Return the scorer-only posterior projection identity terms."""
    target = np.asarray(truth, dtype=float)
    left = np.asarray(left_score, dtype=float)
    right = np.asarray(right_score, dtype=float)
    zero = np.asarray(origin, dtype=float)
    scale = max(float(np.mean((target - zero) ** 2)), 1e-12)
    left_nmse = float(np.mean((target - left) ** 2) / scale)
    right_nmse = float(np.mean((target - right) ** 2) / scale)
    update = right - left
    update_nmse = float(np.mean(update**2) / scale)
    defect = float(right_nmse - left_nmse + update_nmse)
    orthogonality = float(
        -2.0 * np.mean((target - right) * update) / scale
    )
    return {
        "true_nmse_left": left_nmse,
        "true_nmse_right": right_nmse,
        "true_nmse_delta": float(right_nmse - left_nmse),
        "update_nmse": update_nmse,
        "projection_defect": defect,
        "posterior_orthogonality": orthogonality,
        "projection_algebra_error": float(abs(defect - orthogonality)),
    }


def initial_observable_history(
    sessions: np.ndarray,
    score: np.ndarray,
    unresolved: np.ndarray,
    *,
    external_zero: np.ndarray,
) -> np.ndarray:
    """Build a non-redundant observable history at the first budget."""
    values = np.asarray(sessions, dtype=float)
    if values.ndim != 4 or values.shape[1] < 2:
        raise ValueError(
            "sessions must be authors x at-least-two-streams x budgets x dims"
        )
    centered_score = np.asarray(score, dtype=float) - np.asarray(
        external_zero,
        dtype=float,
    )
    residual = np.asarray(unresolved, dtype=float)
    dispersion = values[:, 0, 0] - values[:, 1, 0]
    if centered_score.shape != residual.shape or (
        centered_score.shape != dispersion.shape
    ):
        raise ValueError("score, unresolved, and dispersion must align")
    return np.concatenate(
        [centered_score, residual, dispersion],
        axis=1,
    )


def cumulative_predictor_candidates(
    *,
    alphas: Iterable[float] = (1.0, 10.0, 100.0, 1000.0),
    ranks: Iterable[int] = (4, 8, 16, 32),
) -> list[dict[str, Any]]:
    """Return the registered cumulative-path predictor candidates."""
    output: list[dict[str, Any]] = []
    for alpha in alphas:
        output.append({
            "family": "linear_ridge",
            "alpha": float(alpha),
            "rank": 0,
            "name": f"linear_a{float(alpha):g}",
        })
        output.append({
            "family": "random_fourier_ridge",
            "alpha": float(alpha),
            "rank": 0,
            "name": f"rff256_a{float(alpha):g}",
        })
        for rank in ranks:
            output.append({
                "family": "reduced_rank_ridge",
                "alpha": float(alpha),
                "rank": int(rank),
                "name": f"rrr_r{int(rank)}_a{float(alpha):g}",
            })
    return output


def _fit_candidate(
    features: np.ndarray,
    target: np.ndarray,
    candidate: dict[str, Any],
    *,
    seed: int,
    rff_components: int,
) -> dict[str, Any]:
    scaler = StandardScaler().fit(features)
    mapped = scaler.transform(features)
    mapper: RBFSampler | None = None
    if candidate["family"] == "random_fourier_ridge":
        mapper = RBFSampler(
            gamma=1.0 / max(mapped.shape[1], 1),
            n_components=int(rff_components),
            random_state=int(seed % (2**31 - 1)),
        )
        mapped = mapper.fit_transform(mapped)
    model = Ridge(alpha=float(candidate["alpha"])).fit(mapped, target)
    output_center: np.ndarray | None = None
    output_basis: np.ndarray | None = None
    if candidate["family"] == "reduced_rank_ridge":
        raw = np.asarray(model.predict(mapped), dtype=float)
        output_center = np.asarray(target, dtype=float).mean(axis=0)
        _, _, right = np.linalg.svd(
            raw - output_center[None],
            full_matrices=False,
        )
        rank = min(int(candidate["rank"]), right.shape[0])
        output_basis = right[:rank].T
    return {
        "candidate": dict(candidate),
        "scaler": scaler,
        "mapper": mapper,
        "model": model,
        "output_center": output_center,
        "output_basis": output_basis,
        "rff_components": int(rff_components),
    }


def _predict_candidate(
    fitted: dict[str, Any],
    features: np.ndarray,
) -> np.ndarray:
    mapped = fitted["scaler"].transform(np.asarray(features, dtype=float))
    if fitted["mapper"] is not None:
        mapped = fitted["mapper"].transform(mapped)
    prediction = np.asarray(fitted["model"].predict(mapped), dtype=float)
    basis = fitted["output_basis"]
    if basis is not None:
        center = np.asarray(fitted["output_center"], dtype=float)
        prediction = (
            center[None]
            + (prediction - center[None]) @ basis @ basis.T
        )
    return prediction


def _horizon_kappas(
    target: np.ndarray,
    prediction: np.ndarray,
    *,
    horizons: int,
) -> np.ndarray:
    width = target.shape[1] // int(horizons)
    if width * int(horizons) != target.shape[1]:
        raise ValueError("target width must divide evenly across horizons")
    values: list[float] = []
    for index in range(int(horizons)):
        start = index * width
        stop = start + width
        truth = target[:, start:stop]
        estimate = prediction[:, start:stop]
        values.append(float(
            1.0
            - np.sum((truth - estimate) ** 2)
            / max(float(np.sum(truth**2)), 1e-12)
        ))
    return np.asarray(values, dtype=float)


def fit_joint_cumulative_predictor(
    features: np.ndarray,
    cumulative_targets: Iterable[np.ndarray],
    *,
    seed: int,
    folds: int = 3,
    alphas: Iterable[float] = (1.0, 10.0, 100.0, 1000.0),
    ranks: Iterable[int] = (4, 8, 16, 32),
    rff_components: int = 256,
) -> dict[str, Any]:
    """Select one predictor specification jointly across all horizons."""
    x = np.asarray(features, dtype=float)
    target_list = [
        np.asarray(value, dtype=float) for value in cumulative_targets
    ]
    if not target_list:
        raise ValueError("at least one cumulative target is required")
    width = target_list[0].shape[1]
    if any(value.shape != target_list[0].shape for value in target_list):
        raise ValueError("all cumulative targets must share one shape")
    y = np.concatenate(target_list, axis=1)
    candidates = cumulative_predictor_candidates(
        alphas=alphas,
        ranks=ranks,
    )
    splitter = KFold(
        n_splits=int(folds),
        shuffle=True,
        random_state=int(seed % (2**32 - 1)),
    )
    rows: list[dict[str, Any]] = []
    for candidate_index, candidate in enumerate(candidates):
        fold_kappas: list[np.ndarray] = []
        for train, valid in splitter.split(x):
            fitted = _fit_candidate(
                x[train],
                y[train],
                candidate,
                seed=seed + 1009 * candidate_index,
                rff_components=rff_components,
            )
            prediction = _predict_candidate(fitted, x[valid])
            fold_kappas.append(_horizon_kappas(
                y[valid],
                prediction,
                horizons=len(target_list),
            ))
        horizon_values = np.mean(np.stack(fold_kappas), axis=0)
        rows.append({
            "candidate_index": int(candidate_index),
            "name": str(candidate["name"]),
            "family": str(candidate["family"]),
            "alpha": float(candidate["alpha"]),
            "rank": int(candidate["rank"]),
            "cv_kappa_pooled": float(horizon_values.mean()),
            **{
                f"cv_kappa_horizon_{index + 1}": float(value)
                for index, value in enumerate(horizon_values)
            },
        })
    table = pd.DataFrame(rows).sort_values(
        ["cv_kappa_pooled", "alpha", "rank", "name"],
        ascending=[False, True, True, True],
    ).reset_index(drop=True)
    selected_row = table.iloc[0]
    selected = candidates[int(selected_row["candidate_index"])]
    final = _fit_candidate(
        x,
        y,
        selected,
        seed=seed + 1009 * int(selected_row["candidate_index"]),
        rff_components=rff_components,
    )
    return {
        **final,
        "table": table,
        "cv_kappa_pooled": float(selected_row["cv_kappa_pooled"]),
        "horizons": int(len(target_list)),
        "target_width": int(width),
    }


def predict_joint_cumulative(
    fitted: dict[str, Any],
    features: np.ndarray,
) -> list[np.ndarray]:
    """Predict cumulative score movement at every registered horizon."""
    combined = _predict_candidate(fitted, np.asarray(features, dtype=float))
    width = int(fitted["target_width"])
    return [
        combined[:, index * width:(index + 1) * width]
        for index in range(int(fitted["horizons"]))
    ]


def fit_fixed_linear_cumulative_predictor(
    features: np.ndarray,
    cumulative_targets: Iterable[np.ndarray],
    *,
    alpha: float,
) -> dict[str, Any]:
    """Fit a frozen linear cumulative detector without model selection."""
    target_list = [
        np.asarray(value, dtype=float) for value in cumulative_targets
    ]
    if not target_list:
        raise ValueError("at least one cumulative target is required")
    y = np.concatenate(target_list, axis=1)
    candidate = {
        "family": "linear_ridge",
        "alpha": float(alpha),
        "rank": 0,
        "name": f"linear_a{float(alpha):g}",
    }
    fitted = _fit_candidate(
        np.asarray(features, dtype=float),
        y,
        candidate,
        seed=0,
        rff_components=0,
    )
    return {
        **fitted,
        "horizons": len(target_list),
        "target_width": target_list[0].shape[1],
    }


def cumulative_kappa(
    target: np.ndarray,
    prediction: np.ndarray,
) -> float:
    """Return observable cumulative displacement predictability."""
    truth = np.asarray(target, dtype=float)
    estimate = np.asarray(prediction, dtype=float)
    return float(
        1.0
        - np.sum((truth - estimate) ** 2)
        / max(float(np.sum(truth**2)), 1e-12)
    )


def simulate_schedule_calibration_context(
    *,
    seed: int,
    spec: PairedScheduleSpec,
) -> dict[str, Any]:
    """Create one observable reference/calibration context for paired tests."""
    streams = np.random.SeedSequence(int(seed)).spawn(8)
    basis = _haar(np.random.default_rng(streams[0]), spec.dimension)
    event_basis = _haar(
        np.random.default_rng(streams[1]),
        spec.dimension,
    )
    event_values = np.linspace(0.55, 1.45, spec.dimension)
    event_root = (
        event_basis * np.sqrt(event_values)[None]
    ) @ event_basis.T
    origin = _scale_rms(
        np.random.default_rng(streams[2]).normal(size=spec.dimension),
        0.20,
    )
    variance = _variance_spectrum(
        "dense_tail48_nested_gaussian",
        spec.dimension,
    )
    stable_scale = float(spec.stable_rms) / max(
        float(np.sqrt(np.mean(variance))),
        1e-12,
    )

    def panel(
        authors: int,
        stable_sequence: np.random.SeedSequence,
        event_sequence: np.random.SeedSequence,
    ) -> tuple[np.ndarray, float, np.ndarray]:
        stable = _draw_stable(
            np.random.default_rng(stable_sequence),
            authors,
            basis,
            variance,
        ) * stable_scale
        noise, prefix_error = _nested_event_noise(
            rng=np.random.default_rng(event_sequence),
            authors=authors,
            sessions=4,
            budgets=spec.budgets,
            covariance_root=event_root,
            event_rms_at_64=float(spec.event_rms_at_64),
            mode="gaussian",
            stable=stable,
            long_memory_rho=0.0,
            student_df=5.0,
        )
        return (
            origin[None, None, None]
            + stable[:, None, None]
            + noise,
            prefix_error,
            stable,
        )

    reference, reference_error, reference_stable = panel(
        int(spec.reference_authors),
        streams[3],
        streams[4],
    )
    calibration, calibration_error, calibration_stable = panel(
        int(spec.calibration_authors),
        streams[5],
        streams[6],
    )
    return {
        "spec": spec,
        "origin": origin,
        "basis": basis,
        "variance": variance,
        "stable_scale": stable_scale,
        "event_root": event_root,
        "reference": reference,
        "calibration": calibration,
        "reference_stable": reference_stable,
        "calibration_stable": calibration_stable,
        "maximum_prefix_identity_error": float(max(
            reference_error,
            calibration_error,
        )),
    }


def _matched_response(
    stable: np.ndarray,
    *,
    reference_stable: np.ndarray,
    geometry: str,
    eta: float,
    final_fraction: float,
    seed: int,
) -> tuple[np.ndarray, float]:
    rng = np.random.default_rng(int(seed))
    dimension = stable.shape[1]
    if float(eta) <= 0.0:
        return np.zeros_like(stable), 0.0
    if geometry == "low_rank_linear":
        left = _haar(rng, dimension)[:, : min(4, dimension)]
        right = _haar(rng, dimension)[:, : min(4, dimension)]
        raw = (stable @ left) @ right.T
        raw_reference = (reference_stable @ left) @ right.T
    elif geometry == "random_rotation":
        rotation = _haar(rng, dimension)
        raw = stable @ rotation.T
        raw_reference = reference_stable @ rotation.T
    elif geometry == "nonlinear_tanh":
        rank = min(8, dimension)
        left = _haar(rng, dimension)[:, :rank]
        right = _haar(rng, dimension)[:, :rank]
        hidden = stable @ left
        reference_hidden = reference_stable @ left
        hidden_scale = np.maximum(
            reference_hidden.std(axis=0, ddof=1),
            1e-8,
        )
        hidden /= hidden_scale
        reference_hidden /= hidden_scale
        raw = np.tanh(hidden) @ right.T
        raw_reference = np.tanh(reference_hidden) @ right.T
    else:
        raise ValueError(f"unsupported opportunity geometry: {geometry}")
    reference_center = raw_reference.mean(axis=0, keepdims=True)
    raw = raw - reference_center
    raw_reference = raw_reference - reference_center
    stable_energy_reference = max(
        float(np.mean(reference_stable**2)),
        1e-12,
    )
    raw_endpoint_energy_reference = max(
        float(np.mean((float(final_fraction) * raw_reference) ** 2)),
        1e-12,
    )
    response = raw * np.sqrt(
        float(eta)
        * stable_energy_reference
        / raw_endpoint_energy_reference
    )
    stable_energy = max(float(np.mean(stable**2)), 1e-12)
    achieved = float(
        np.mean((float(final_fraction) * response) ** 2)
        / stable_energy
    )
    return response, achieved


def simulate_paired_schedule_panel(
    context: dict[str, Any],
    *,
    seed: int,
    geometry: str,
    eta: float,
    drift_schedule_b: bool,
    authors: int | None = None,
    response_seed: int | None = None,
) -> dict[str, Any]:
    """Generate same-author A/B schedules with independent event streams."""
    spec: PairedScheduleSpec = context["spec"]
    count = int(authors or spec.panel_authors)
    streams = np.random.SeedSequence(int(seed)).spawn(3)
    stable = _draw_stable(
        np.random.default_rng(streams[0]),
        count,
        np.asarray(context["basis"], dtype=float),
        np.asarray(context["variance"], dtype=float),
    ) * float(context["stable_scale"])
    noise, prefix_error = _nested_event_noise(
        rng=np.random.default_rng(streams[1]),
        authors=count,
        sessions=4,
        budgets=spec.budgets,
        covariance_root=np.asarray(context["event_root"], dtype=float),
        event_rms_at_64=float(spec.event_rms_at_64),
        mode="gaussian",
        stable=stable,
        long_memory_rho=0.0,
        student_df=5.0,
    )
    values = (
        np.asarray(context["origin"])[None, None, None]
        + stable[:, None, None]
        + noise
    ).reshape(
        count,
        2,
        2,
        len(spec.budgets),
        spec.dimension,
    )
    final_fraction = max(
        int(spec.budgets[-1]) - int(spec.opportunity_start),
        0,
    ) / float(spec.budgets[-1])
    response, achieved_eta = _matched_response(
        stable,
        reference_stable=np.asarray(
            context["calibration_stable"],
            dtype=float,
        ),
        geometry=geometry,
        eta=float(eta),
        final_fraction=final_fraction,
        seed=(
            int(response_seed)
            if response_seed is not None
            else int(streams[2].generate_state(1, dtype=np.uint64)[0])
        ),
    )
    fractions = np.asarray([
        max(int(budget) - int(spec.opportunity_start), 0)
        / float(budget)
        for budget in spec.budgets
    ])
    if drift_schedule_b:
        values[:, 1] += (
            fractions[None, None, :, None]
            * response[:, None, None]
        )
    return {
        "values": values,
        "truth": np.asarray(context["origin"])[None] + stable,
        "response": response,
        "fractions": fractions,
        "achieved_eta": float(achieved_eta if drift_schedule_b else 0.0),
        "prefix_identity_error": float(prefix_error),
    }


def score_paired_schedule_panel(
    panel: np.ndarray,
    fitted: dict[int, dict[str, Any]],
    *,
    budgets: Iterable[int],
) -> np.ndarray:
    """Score every schedule and technical stream with one frozen operator."""
    values = np.asarray(panel, dtype=float)
    budget_list = [int(value) for value in budgets]
    if values.ndim != 5 or values.shape[1:3] != (2, 2):
        raise ValueError(
            "panel must be authors x two schedules x two streams x budgets x dims"
        )
    output = np.empty_like(values)
    for index, budget in enumerate(budget_list):
        flat = values[:, :, :, index].reshape(-1, values.shape[-1])
        output[:, :, :, index] = apply_spectrum_operator(
            flat,
            fitted[budget],
        ).reshape(values.shape[0], 2, 2, values.shape[-1])
    return output


def paired_schedule_excess(
    scores: np.ndarray,
    fitted: dict[int, dict[str, Any]],
    *,
    budget_index: int,
    budget: int,
) -> dict[str, float]:
    """Estimate observable schedule excess after stream-noise correction."""
    values = np.asarray(scores, dtype=float)
    index = int(budget_index)
    schedule_a = values[:, 0, :, index]
    schedule_b = values[:, 1, :, index]
    mean_difference = schedule_b.mean(axis=1) - schedule_a.mean(axis=1)
    between = float(np.mean(mean_difference**2))
    stream_variance = float(
        np.mean(((schedule_a[:, 0] - schedule_a[:, 1]) / 2.0) ** 2)
        + np.mean(((schedule_b[:, 0] - schedule_b[:, 1]) / 2.0) ** 2)
    )
    stable_second_moment = np.asarray(
        fitted[int(budget)]["stable_second_moment"],
        dtype=float,
    )
    operator = np.asarray(fitted[int(budget)]["operator"], dtype=float)
    raw_stable_scale = max(
        float(np.trace(stable_second_moment))
        / values.shape[-1],
        1e-12,
    )
    score_stable_scale = max(
        float(np.trace(
            operator @ stable_second_moment @ operator.T
        ))
        / values.shape[-1],
        1e-12,
    )
    excess = float((between - stream_variance) / score_stable_scale)
    return {
        "schedule_difference_energy": between,
        "stream_noise_energy": stream_variance,
        "observable_raw_stable_scale": raw_stable_scale,
        "observable_score_stable_scale": score_stable_scale,
        "schedule_excess_q": excess,
    }


def score_space_response_ratio(
    response: np.ndarray,
    fitted: dict[str, Any],
    *,
    fraction: float,
) -> float:
    """Return scorer-only planted response energy in score-space units.

    This synthetic-truth quantity is calibration metadata. It must not enter
    either the paired refusal detector or its operational threshold.
    """
    values = np.asarray(response, dtype=float)
    operator = np.asarray(fitted["operator"], dtype=float)
    stable_second_moment = np.asarray(
        fitted["stable_second_moment"],
        dtype=float,
    )
    if values.ndim != 2 or values.shape[1] != operator.shape[1]:
        raise ValueError("response and fitted operator are incompatible")
    score_stable_scale = max(
        float(np.trace(
            operator @ stable_second_moment @ operator.T
        ))
        / values.shape[1],
        1e-12,
    )
    transformed = float(fraction) * values @ operator.T
    return float(np.mean(transformed**2) / score_stable_scale)


def paired_schedule_score_path(
    panel: np.ndarray,
    fitted: dict[int, dict[str, Any]],
    *,
    budgets: Iterable[int],
    schedule_index: int,
) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    """Return mean profile, score, and unresolved paths for one schedule."""
    values = np.asarray(panel, dtype=float)
    budget_list = [int(value) for value in budgets]
    profiles: list[np.ndarray] = []
    scores: list[np.ndarray] = []
    residuals: list[np.ndarray] = []
    for index, budget in enumerate(budget_list):
        profile = values[:, int(schedule_index), :, index].mean(axis=1)
        profiles.append(profile)
        scores.append(apply_spectrum_operator(profile, fitted[budget]))
        residuals.append(unresolved_channel(profile, fitted[budget]))
    return profiles, scores, residuals
