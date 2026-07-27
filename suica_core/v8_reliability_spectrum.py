"""Observable reliability-spectrum operators for SUICA V8.3.7G.

The module works on already constructed author-relative profile vectors. It
does not read text or psychological labels. Synthetic truth is returned only
for scorer-side validation; estimator selection uses technical replicates.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from scipy.stats import binom
from sklearn.covariance import LedoitWolf

from .v8_external_zero_uncertainty import paired_similarity_metrics


@dataclass(frozen=True)
class ReliabilitySpectrumWorldSpec:
    """Profile-level world for reliability-spectrum falsification."""

    world: str = "exact_rank12"
    dimension: int = 48
    sessions: int = 4
    event_budget: int = 128
    reference_authors: int = 256
    calibration_authors: int = 128
    interval_authors: int = 96
    evaluation_authors: int = 96
    stable_rms: float = 0.30
    event_rms_at_64: float = 0.18
    state_rms: float = 0.16
    state_correlation: float = 0.80
    slow_variance_exponent: float = 0.50
    population_shift_rms: float = 0.15


def _haar(
    rng: np.random.Generator,
    dimension: int,
) -> np.ndarray:
    return np.linalg.qr(
        rng.normal(size=(dimension, dimension)),
    )[0]


def _scale_rms(values: np.ndarray, target: float) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    rms = float(np.sqrt(np.mean(array**2)))
    if target <= 0.0 or rms <= 1e-12:
        return np.zeros_like(array)
    return array * (float(target) / rms)


def _psd(
    matrix: np.ndarray,
    *,
    floor: float = 0.0,
) -> np.ndarray:
    symmetric = 0.5 * (
        np.asarray(matrix, dtype=float)
        + np.asarray(matrix, dtype=float).T
    )
    values, vectors = np.linalg.eigh(symmetric)
    values = np.maximum(values, float(floor))
    return (vectors * values[None]) @ vectors.T


def _sqrt_and_inverse(
    matrix: np.ndarray,
    *,
    relative_floor: float,
) -> tuple[np.ndarray, np.ndarray]:
    symmetric = 0.5 * (
        np.asarray(matrix, dtype=float)
        + np.asarray(matrix, dtype=float).T
    )
    values, vectors = np.linalg.eigh(symmetric)
    scale = max(float(np.mean(np.maximum(values, 0.0))), 1e-10)
    values = np.maximum(values, relative_floor * scale)
    root = (vectors * np.sqrt(values)[None]) @ vectors.T
    inverse = (vectors * (1.0 / np.sqrt(values))[None]) @ vectors.T
    return root, inverse


def _regularized_psd_geometry(
    matrix: np.ndarray,
    *,
    relative_floor: float,
) -> dict[str, Any]:
    """Return a fixed-floor PSD matrix and its geometric diagnostics."""
    symmetric = 0.5 * (
        np.asarray(matrix, dtype=float)
        + np.asarray(matrix, dtype=float).T
    )
    values, vectors = np.linalg.eigh(symmetric)
    scale = max(float(np.mean(np.maximum(values, 0.0))), 1e-10)
    floor = float(relative_floor) * scale
    values = np.maximum(values, floor)
    root = (vectors * np.sqrt(values)[None]) @ vectors.T
    inverse_root = (
        vectors * (1.0 / np.sqrt(values))[None]
    ) @ vectors.T
    regularized = (vectors * values[None]) @ vectors.T
    effective_rank = float(
        values.sum() ** 2 / max(float(np.sum(values**2)), 1e-12)
    )
    return {
        "matrix": regularized,
        "root": root,
        "inverse_root": inverse_root,
        "values": values,
        "condition_number": float(values.max() / values.min()),
        "effective_rank": effective_rank,
        "log_determinant": float(np.log(values).sum()),
    }


def stable_variance_spectrum(
    world: str,
    dimension: int,
) -> np.ndarray:
    """Return the planted stable-author variance spectrum."""
    index = np.arange(1, dimension + 1, dtype=float)
    if world in {"exact_rank12", "author_permutation"}:
        values = np.zeros(dimension, dtype=float)
        values[: min(12, dimension)] = 1.0
        return values
    if world in {
        "dense_tail48",
        "dense_state_alias",
        "slow_variance_decay",
        "informative_precision_dense",
        "reference_shift_dense",
    }:
        # V3.7F planted a power law in author-loading amplitude. This module
        # represents variances, so the registered amplitude must be squared.
        return (1.0 + index / 4.0) ** -1.50
    if world == "broken_spectrum48":
        template = np.concatenate([
            np.full(4, 1.0),
            np.full(4, 0.35),
            np.full(8, 0.10),
            np.full(16, 0.025),
            np.full(max(dimension - 32, 0), 0.006),
        ])
        return template[:dimension]
    raise ValueError(f"unsupported V3.7G world: {world}")


def _draw_stable(
    rng: np.random.Generator,
    authors: int,
    basis: np.ndarray,
    variance: np.ndarray,
) -> np.ndarray:
    score = rng.normal(size=(authors, len(variance)))
    return (score * np.sqrt(variance)[None]) @ basis.T


def _event_noise(
    *,
    rng: np.random.Generator,
    stable: np.ndarray,
    sessions: int,
    covariance_root: np.ndarray,
    scale: float,
    informative_precision: bool,
) -> np.ndarray:
    authors, dimension = stable.shape
    noise = (
        rng.normal(size=(authors, sessions, dimension))
        @ covariance_root.T
    )
    if informative_precision:
        anchor = stable[:, 0]
        anchor = (
            anchor - anchor.mean()
        ) / max(float(anchor.std(ddof=1)), 1e-8)
        author_scale = np.clip(np.exp(0.35 * anchor), 0.45, 2.20)
        noise *= author_scale[:, None, None]
    return float(scale) * noise


def _state_process(
    *,
    rng: np.random.Generator,
    authors: int,
    sessions: int,
    dimension: int,
    basis: np.ndarray,
    rms: float,
    correlation: float,
) -> np.ndarray:
    rank = min(8, dimension)
    state_basis = np.asarray(basis, dtype=float)
    if state_basis.shape != (dimension, rank):
        raise ValueError("state basis has the wrong shape")
    common = rng.normal(size=(authors, rank))
    innovation = rng.normal(size=(authors, sessions, rank))
    score = (
        float(correlation) * common[:, None]
        + np.sqrt(max(1.0 - float(correlation) ** 2, 0.0))
        * innovation
    )
    state = np.einsum("asr,dr->asd", score, state_basis)
    return _scale_rms(state, rms)


def simulate_reliability_spectrum_world(
    *,
    latent_seed: int,
    event_seed: int,
    spec: ReliabilitySpectrumWorldSpec,
) -> dict[str, Any]:
    """Generate disjoint reference, calibration, interval, and test panels."""
    if spec.sessions < 4:
        raise ValueError("V3.7G requires at least four technical sessions")
    latent_streams = np.random.SeedSequence(latent_seed).spawn(8)
    (
        rng_basis,
        rng_zero,
        rng_reference,
        rng_calibration,
        rng_interval,
        rng_evaluation,
        rng_event_basis,
        rng_state,
    ) = (np.random.default_rng(item) for item in latent_streams)
    event_rng = np.random.default_rng(event_seed)

    basis = _haar(rng_basis, spec.dimension)
    variance = stable_variance_spectrum(spec.world, spec.dimension)
    zero = _scale_rms(
        rng_zero.normal(size=spec.dimension),
        0.20,
    )
    stable = {
        "reference": _draw_stable(
            rng_reference,
            spec.reference_authors,
            basis,
            variance,
        ),
        "calibration": _draw_stable(
            rng_calibration,
            spec.calibration_authors,
            basis,
            variance,
        ),
        "interval": _draw_stable(
            rng_interval,
            spec.interval_authors,
            basis,
            variance,
        ),
        "evaluation": _draw_stable(
            rng_evaluation,
            spec.evaluation_authors,
            basis,
            variance,
        ),
    }
    # The population covariance, not realized panel samples, defines scale.
    # This keeps the four disjoint panels statistically independent.
    scale = float(spec.stable_rms) / max(
        float(np.sqrt(np.mean(variance))),
        1e-12,
    )
    stable = {key: value * scale for key, value in stable.items()}

    planted_shift = np.zeros(spec.dimension, dtype=float)
    if spec.world == "reference_shift_dense":
        planted_shift = basis[:, 0].copy()
        planted_shift *= float(spec.population_shift_rms) / max(
            float(np.sqrt(np.mean(planted_shift**2))),
            1e-12,
        )
        stable["evaluation"] += planted_shift[None]

    event_basis = _haar(rng_event_basis, spec.dimension)
    event_values = np.linspace(0.55, 1.45, spec.dimension)
    event_root = (
        event_basis * np.sqrt(event_values)[None]
    ) @ event_basis.T
    if spec.world == "slow_variance_decay":
        exponent = float(spec.slow_variance_exponent)
        event_scale = float(spec.event_rms_at_64) * (
            64.0 / float(spec.event_budget)
        ) ** (0.5 * exponent)
    else:
        event_scale = float(spec.event_rms_at_64) * np.sqrt(
            64.0 / float(spec.event_budget)
        )

    panels: dict[str, np.ndarray] = {}
    truths: dict[str, np.ndarray] = {}
    state_enabled = spec.world == "dense_state_alias"
    reference_shifted = spec.world == "reference_shift_dense"
    informative = spec.world == "informative_precision_dense"
    state_basis = (
        _haar(rng_state, spec.dimension)[
            :, : min(8, spec.dimension)
        ]
        if state_enabled
        else None
    )
    for panel_name, stable_value in stable.items():
        author_count = len(stable_value)
        repeated = np.repeat(
            stable_value[:, None],
            spec.sessions,
            axis=1,
        )
        if spec.world == "author_permutation":
            for session in range(1, spec.sessions):
                repeated[:, session] = stable_value[
                    event_rng.permutation(author_count)
                ]
        state = (
            _state_process(
                rng=rng_state,
                authors=author_count,
                sessions=spec.sessions,
                dimension=spec.dimension,
                basis=np.asarray(state_basis),
                rms=spec.state_rms,
                correlation=spec.state_correlation,
            )
            if state_enabled
            else np.zeros_like(repeated)
        )
        noise = _event_noise(
            rng=event_rng,
            stable=stable_value,
            sessions=spec.sessions,
            covariance_root=event_root,
            scale=event_scale,
            informative_precision=informative,
        )
        panels[panel_name] = zero[None, None] + repeated + state + noise
        truths[panel_name] = zero[None] + stable_value

    return {
        "world": spec.world,
        "panels": panels,
        "truths": truths,
        "true_zero": zero,
        "stable_basis": basis,
        "stable_variance": variance * scale**2,
        "event_covariance": (
            event_scale**2 * event_root @ event_root.T
        ),
        "population_shift": planted_shift,
        "design": {
            "event_budget": int(spec.event_budget),
            "dimension": int(spec.dimension),
            "sessions": int(spec.sessions),
            "event_scale": float(event_scale),
            "interval_claim_allowed": bool(
                not state_enabled and not reference_shifted
            ),
            "interval_claim_status": (
                "MODEL_ASSISTED_CONDITIONAL"
                if not state_enabled and not reference_shifted
                else (
                    "UNRESOLVED_NO_STATE_SEPARATED_OCCASION"
                    if state_enabled
                    else "UNRESOLVED_REFERENCE_TRANSPORT_UNCALIBRATED"
                )
            ),
        },
    }


def estimate_external_origin(reference_sessions: np.ndarray) -> np.ndarray:
    """Estimate the score origin from a disjoint external reference panel."""
    values = np.asarray(reference_sessions, dtype=float)
    if values.ndim != 3:
        raise ValueError("reference sessions must be authors by sessions by dims")
    return values.mean(axis=(0, 1))


def fit_reliability_spectrum(
    left: np.ndarray,
    right: np.ndarray,
    *,
    external_zero: np.ndarray,
    noise_shrinkage: float = 0.25,
    eigen_floor: float = 1e-6,
) -> dict[str, np.ndarray | float]:
    """Fit an external-origin stable-to-event second-moment spectrum."""
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    zero = np.asarray(external_zero, dtype=float)
    if x.shape != y.shape or x.ndim != 2 or x.shape[1:] != zero.shape:
        raise ValueError("paired profiles and external zero are incompatible")
    xc = x - zero
    yc = y - zero
    denominator = max(len(x), 1)
    stable_raw = (
        xc.T @ yc + yc.T @ xc
    ) / (2.0 * denominator)
    stable = _psd(stable_raw)
    difference = x - y
    difference -= difference.mean(axis=0, keepdims=True)
    noise = difference.T @ difference / (2.0 * denominator)
    average_noise = max(
        float(np.trace(noise)) / max(noise.shape[0], 1),
        1e-10,
    )
    shrinkage = float(noise_shrinkage)
    noise_regularized = (
        (1.0 - shrinkage) * noise
        + shrinkage * average_noise * np.eye(noise.shape[0])
    )
    noise_root, noise_inverse = _sqrt_and_inverse(
        noise_regularized,
        relative_floor=eigen_floor,
    )
    whitened = _psd(noise_inverse @ stable @ noise_inverse.T)
    eta, modes = np.linalg.eigh(whitened)
    order = np.argsort(eta)[::-1]
    eta = np.maximum(eta[order], 0.0)
    modes = modes[:, order]
    return {
        "external_zero": zero,
        "stable_second_moment": stable,
        "event_second_moment": noise,
        "event_regularized": noise_regularized,
        "event_root": noise_root,
        "event_inverse": noise_inverse,
        "modes": modes,
        "eta": eta,
        "noise_shrinkage": shrinkage,
    }


def default_spectrum_candidates(
    dimension: int,
) -> list[dict[str, Any]]:
    """Return the registered hard and smooth reliability-weight families."""
    ranks = sorted(set(
        [0, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, dimension]
    ))
    ranks = [rank for rank in ranks if rank <= dimension]
    candidates: list[dict[str, Any]] = [
        {"family": "hard", "rank": rank, "name": f"hard_r{rank}"}
        for rank in ranks
    ]
    for tau in (0.25, 0.50, 1.0, 2.0, 4.0):
        candidates.append({
            "family": "wiener",
            "tau": tau,
            "name": f"wiener_t{tau:g}",
        })
    for tau in (0.50, 1.0, 2.0):
        for power in (0.50, 1.50, 2.0):
            candidates.append({
                "family": "power",
                "tau": tau,
                "power": power,
                "name": f"power_t{tau:g}_p{power:g}",
            })
    templates = {
        "spline_conservative": [0.0, 0.01, 0.10, 0.45, 0.85, 1.0],
        "spline_balanced": [0.0, 0.05, 0.30, 0.70, 0.93, 1.0],
        "spline_preserving": [0.02, 0.18, 0.55, 0.85, 0.98, 1.0],
    }
    for name, levels in templates.items():
        candidates.append({
            "family": "monotone_spline",
            "levels": levels,
            "name": name,
        })
    return candidates


def spectrum_weights(
    eta: np.ndarray,
    candidate: dict[str, Any],
) -> np.ndarray:
    """Map a stable-to-event spectrum to bounded monotone weights."""
    values = np.maximum(np.asarray(eta, dtype=float), 0.0)
    family = str(candidate["family"])
    if family == "hard":
        weights = np.zeros_like(values)
        weights[: int(candidate["rank"])] = 1.0
    elif family == "wiener":
        tau = float(candidate["tau"])
        weights = values / np.maximum(values + tau, 1e-12)
    elif family == "power":
        tau = float(candidate["tau"])
        power = float(candidate["power"])
        weights = (
            values / np.maximum(values + tau, 1e-12)
        ) ** power
    elif family == "monotone_spline":
        base = values / np.maximum(values + 1.0, 1e-12)
        knots = np.asarray([0.0, 0.05, 0.20, 0.50, 0.80, 1.0])
        levels = np.asarray(candidate["levels"], dtype=float)
        if np.any(np.diff(levels) < 0.0):
            raise ValueError("spline levels must be monotone")
        weights = PchipInterpolator(
            knots,
            levels,
            extrapolate=True,
        )(np.clip(base, 0.0, 1.0))
    else:
        raise ValueError(f"unsupported spectrum family: {family}")
    return np.clip(weights, 0.0, 1.0)


def spectrum_operator(
    spectrum: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    """Construct the original-coordinate spectral operator."""
    weights = spectrum_weights(
        np.asarray(spectrum["eta"]),
        candidate,
    )
    modes = np.asarray(spectrum["modes"])
    noise_root = np.asarray(spectrum["event_root"])
    noise_inverse = np.asarray(spectrum["event_inverse"])
    operator = (
        noise_root
        @ modes
        @ np.diag(weights)
        @ modes.T
        @ noise_inverse
    )
    return {
        **spectrum,
        "candidate": dict(candidate),
        "weights": weights,
        "operator": operator,
        "effective_df": float(weights.sum()),
    }


def apply_spectrum_operator(
    profiles: np.ndarray,
    fitted: dict[str, Any],
) -> np.ndarray:
    """Apply a fitted column-space operator to row-wise profiles."""
    values = np.asarray(profiles, dtype=float)
    zero = np.asarray(fitted["external_zero"], dtype=float)
    operator = np.asarray(fitted["operator"], dtype=float)
    return zero + (values - zero) @ operator.T


def unresolved_channel(
    profiles: np.ndarray,
    fitted: dict[str, Any],
) -> np.ndarray:
    """Return the complementary channel without deleting it."""
    values = np.asarray(profiles, dtype=float)
    zero = np.asarray(fitted["external_zero"], dtype=float)
    operator = np.asarray(fitted["operator"], dtype=float)
    return (values - zero) @ (
        np.eye(values.shape[-1]) - operator.T
    )


def normalized_mse(
    estimate: np.ndarray,
    truth: np.ndarray,
    *,
    origin: np.ndarray,
) -> float:
    """Return MSE normalized by scorer-only truth energy around the origin."""
    values = np.asarray(estimate, dtype=float)
    target = np.asarray(truth, dtype=float)
    zero = np.asarray(origin, dtype=float)
    scale = float(np.mean((target - zero) ** 2))
    return float(np.mean((values - target) ** 2) / max(scale, 1e-12))


def select_spectrum_candidate(
    calibration_sessions: np.ndarray,
    *,
    external_zero: np.ndarray,
    candidates: Iterable[dict[str, Any]],
    folds: int,
    seed: int,
    noise_shrinkage: float,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Select a weight rule using author folds and later technical sessions."""
    sessions = np.asarray(calibration_sessions, dtype=float)
    if sessions.ndim != 3 or sessions.shape[1] < 4:
        raise ValueError("candidate selection requires four sessions")
    candidate_list = [dict(item) for item in candidates]
    order = np.random.default_rng(seed).permutation(len(sessions))
    partitions = np.array_split(order, int(folds))
    losses = {str(item["name"]): [] for item in candidate_list}
    effective = {str(item["name"]): [] for item in candidate_list}
    for valid in partitions:
        train = np.setdiff1d(order, valid, assume_unique=True)
        spectrum = fit_reliability_spectrum(
            sessions[train, 0],
            sessions[train, 1],
            external_zero=external_zero,
            noise_shrinkage=noise_shrinkage,
        )
        predictor = sessions[valid, :2].mean(axis=1)
        target = sessions[valid, 2:4].mean(axis=1)
        denominator = float(np.mean(
            (target - external_zero) ** 2
        ))
        for candidate in candidate_list:
            fitted = spectrum_operator(spectrum, candidate)
            predicted = apply_spectrum_operator(predictor, fitted)
            loss = float(
                np.mean((predicted - target) ** 2)
                / max(denominator, 1e-12)
            )
            name = str(candidate["name"])
            losses[name].append(loss)
            effective[name].append(float(fitted["effective_df"]))
    rows = []
    lookup = {str(item["name"]): item for item in candidate_list}
    for name, values in losses.items():
        vector = np.asarray(values, dtype=float)
        rows.append({
            "name": name,
            "family": str(lookup[name]["family"]),
            "mean_loss": float(vector.mean()),
            "se_loss": float(
                vector.std(ddof=1) / np.sqrt(len(vector))
            ),
            "mean_effective_df": float(np.mean(effective[name])),
        })
    table = pd.DataFrame(rows).sort_values(
        ["mean_loss", "mean_effective_df", "name"],
    ).reset_index(drop=True)
    selected_name = str(table.iloc[0]["name"])
    table["selected"] = table["name"] == selected_name
    return dict(lookup[selected_name]), table


def minimum_risk_hard_candidate(table: pd.DataFrame) -> str:
    """Return the CV-minimum-risk hard comparator."""
    hard = table[table["family"] == "hard"].sort_values(
        ["mean_loss", "mean_effective_df", "name"],
    )
    if hard.empty:
        raise ValueError("selection table has no hard candidate")
    return str(hard.iloc[0]["name"])


def one_se_hard_candidate(table: pd.DataFrame) -> str:
    """Return the one-SE, lowest-capacity operational hard comparator.

    This matches the adaptive hard-rank convention used in V3.7E-F rather
    than the fair minimum-risk comparator used for the V3.7G primary effect.
    """
    hard = table[table["family"] == "hard"].sort_values(
        ["mean_loss", "mean_effective_df", "name"],
    )
    if hard.empty:
        raise ValueError("selection table has no hard candidate")
    best = hard.iloc[0]
    threshold = float(best["mean_loss"] + best["se_loss"])
    eligible = hard[hard["mean_loss"] <= threshold].sort_values(
        ["mean_effective_df", "mean_loss", "name"],
    )
    return str(eligible.iloc[0]["name"])


def _fit_me_tolerance_mapping(
    panel: np.ndarray,
    *,
    fitted: dict[str, Any],
    score_pair: tuple[int, int],
    proxy_pair: tuple[int, int],
    eigen_floor: float,
    maximum_negative_mass_ratio: float,
    maximum_condition: float,
) -> dict[str, Any]:
    """Fit the measurement-error radial map on one author panel."""
    values = np.asarray(panel, dtype=float)
    score = apply_spectrum_operator(
        values[:, score_pair].mean(axis=1),
        fitted,
    )
    proxy = values[:, proxy_pair].mean(axis=1)
    observed_error = proxy - score
    bias = observed_error.mean(axis=0)
    observed_covariance = LedoitWolf().fit(
        observed_error - bias
    ).covariance_
    proxy_noise = LedoitWolf().fit(
        (
            values[:, proxy_pair[0]]
            - values[:, proxy_pair[1]]
        )
        / 2.0
    ).covariance_
    raw_latent = 0.5 * (
        observed_covariance - proxy_noise
        + (observed_covariance - proxy_noise).T
    )
    raw_values = np.linalg.eigvalsh(raw_latent)
    negative_mass = float(
        np.abs(raw_values[raw_values < 0.0]).sum()
    )
    observed_trace = max(
        float(np.trace(observed_covariance)),
        1e-12,
    )
    negative_mass_ratio = negative_mass / observed_trace
    if negative_mass_ratio > float(maximum_negative_mass_ratio):
        return {
            "status": "UNRESOLVED_DECONVOLUTION_NEGATIVE_MASS",
            "negative_mass_ratio": negative_mass_ratio,
        }
    latent_covariance = _psd(raw_latent)
    positive_values = np.maximum(
        np.linalg.eigvalsh(latent_covariance),
        0.0,
    )
    latent_effective_rank = float(
        positive_values.sum() ** 2
        / max(float(np.sum(positive_values**2)), 1e-12)
    )
    truncation_trace_ratio = float(
        (float(np.trace(latent_covariance)) - float(np.trace(raw_latent)))
        / observed_trace
    )
    fit_count = len(values)
    target_covariance = (
        latent_covariance
        + observed_covariance / float(fit_count)
    )
    proxy_prediction_covariance = (
        (1.0 + 1.0 / float(fit_count)) * observed_covariance
    )
    target_geometry = _regularized_psd_geometry(
        target_covariance,
        relative_floor=eigen_floor,
    )
    proxy_geometry = _regularized_psd_geometry(
        proxy_prediction_covariance,
        relative_floor=eigen_floor,
    )
    condition_number = float(proxy_geometry["condition_number"])
    if condition_number > float(maximum_condition):
        return {
            "status": "UNRESOLVED_INTERVAL_CONDITION_NUMBER",
            "condition_number": condition_number,
        }
    mapping = (
        np.asarray(target_geometry["root"])
        @ np.asarray(proxy_geometry["inverse_root"])
    )
    if not np.isfinite(mapping).all():
        return {"status": "UNRESOLVED_NONFINITE_ME_MAPPING"}
    return {
        "status": "ME_MAPPING_READY",
        "bias": bias,
        "mapping": mapping,
        "target_covariance": target_covariance,
        "negative_mass_ratio": negative_mass_ratio,
        "psd_truncation_trace_ratio": truncation_trace_ratio,
        "latent_effective_rank": latent_effective_rank,
        "condition_number": condition_number,
        "mapping_operator_norm": float(np.linalg.norm(mapping, ord=2)),
    }


def _mapped_radius_values(
    panel: np.ndarray,
    *,
    fitted: dict[str, Any],
    mapping: dict[str, Any],
    score_pair: tuple[int, int],
    proxy_pair: tuple[int, int],
) -> tuple[np.ndarray, np.ndarray]:
    """Return corrected and raw proxy-error radii."""
    values = np.asarray(panel, dtype=float)
    score = apply_spectrum_operator(
        values[:, score_pair].mean(axis=1),
        fitted,
    )
    proxy = values[:, proxy_pair].mean(axis=1)
    centered = proxy - score - np.asarray(mapping["bias"])
    corrected = centered @ np.asarray(mapping["mapping"]).T
    return (
        np.linalg.norm(corrected, axis=1),
        np.linalg.norm(centered, axis=1),
    )


def _tolerance_order(
    sample_count: int,
    *,
    content: float,
    confidence: float,
) -> tuple[int, float]:
    """Return a one-sided nonparametric tolerance order and its confidence."""
    order = int(binom.ppf(confidence, sample_count, content)) + 1
    if order > sample_count:
        return order, 0.0
    achieved = float(binom.cdf(
        order - 1,
        sample_count,
        content,
    ))
    return order, achieved


def _mapping_bootstrap_stability(
    *,
    fit_panel: np.ndarray,
    radius_panel: np.ndarray,
    fitted: dict[str, Any],
    order: int,
    replicates: int,
    seed: int,
    eigen_floor: float,
    maximum_negative_mass_ratio: float,
    maximum_condition: float,
) -> dict[str, float]:
    """Bootstrap fit authors and quantify tolerance-radius stability."""
    rng = np.random.default_rng(seed)
    radii: list[float] = []
    for _ in range(int(replicates)):
        sampled = rng.integers(0, len(fit_panel), size=len(fit_panel))
        mapping = _fit_me_tolerance_mapping(
            fit_panel[sampled],
            fitted=fitted,
            score_pair=(0, 1),
            proxy_pair=(2, 3),
            eigen_floor=eigen_floor,
            maximum_negative_mass_ratio=maximum_negative_mass_ratio,
            maximum_condition=maximum_condition,
        )
        if mapping["status"] != "ME_MAPPING_READY":
            continue
        corrected, _ = _mapped_radius_values(
            radius_panel,
            fitted=fitted,
            mapping=mapping,
            score_pair=(0, 1),
            proxy_pair=(2, 3),
        )
        radii.append(float(np.sort(corrected)[order - 1]))
    vector = np.asarray(radii, dtype=float)
    valid_rate = float(len(vector) / max(int(replicates), 1))
    if not len(vector):
        return {
            "valid_rate": valid_rate,
            "radius_cv": float("inf"),
            "radius_quantile_ratio": float("inf"),
        }
    q05, q95 = np.quantile(vector, [0.05, 0.95])
    return {
        "valid_rate": valid_rate,
        "radius_cv": float(
            vector.std(ddof=1) / max(float(vector.mean()), 1e-12)
        ),
        "radius_quantile_ratio": float(q95 / max(q05, 1e-12)),
    }


def model_assisted_conditional_region(
    *,
    interval_sessions: np.ndarray,
    evaluation_sessions: np.ndarray,
    fitted: dict[str, Any],
    level: float = 0.95,
    tolerance_confidence: float = 0.95,
    bootstrap_replicates: int = 1_000,
    bootstrap_seed: int = 0,
    eigen_floor: float = 1e-6,
    minimum_fit_per_dimension: float = 4.0,
    maximum_negative_mass_ratio: float = 0.25,
    maximum_condition: float = 1e6,
    minimum_bootstrap_replicates: int = 1_000,
    minimum_bootstrap_valid_rate: float = 0.99,
    maximum_bootstrap_radius_cv: float = 0.10,
    maximum_bootstrap_radius_quantile_ratio: float = 1.25,
    minimum_pair_swap_radius_ratio: float = 0.80,
    maximum_pair_swap_radius_ratio: float = 1.25,
) -> dict[str, Any]:
    """Fit a 95/95 model-assisted measurement-error tolerance ball.

    Interval authors provide a score from sessions 0/1 and an independent
    proxy from sessions 2/3. A fit-author map corrects proxy-error covariance;
    a disjoint radius panel supplies a nonparametric content/confidence order
    statistic. The strict tolerance guarantee applies to the mapped proxy
    radius distribution. Transfer to latent error remains model-assisted.
    """
    interval = np.asarray(interval_sessions, dtype=float)
    evaluation = np.asarray(evaluation_sessions, dtype=float)
    if interval.ndim != 3 or evaluation.ndim != 3:
        raise ValueError("sessions must be authors by sessions by dimensions")
    if interval.shape[1] < 4 or evaluation.shape[1] < 2:
        raise ValueError("insufficient technical sessions")
    fit_count = max(interval.shape[0] // 2, 4)
    if interval.shape[0] - fit_count < 4:
        return {"status": "UNRESOLVED_INTERVAL_RADIUS_TOO_SMALL"}
    dimension = interval.shape[2]
    if fit_count < int(np.ceil(
        float(minimum_fit_per_dimension) * dimension
    )):
        return {"status": "UNRESOLVED_INTERVAL_FIT_TOO_SMALL"}
    radius_count = interval.shape[0] - fit_count
    order, achieved_confidence = _tolerance_order(
        radius_count,
        content=level,
        confidence=tolerance_confidence,
    )
    if order > radius_count:
        return {"status": "UNRESOLVED_INTERVAL_RADIUS_TOO_SMALL"}
    if int(bootstrap_replicates) < int(minimum_bootstrap_replicates):
        return {"status": "UNRESOLVED_BOOTSTRAP_TOO_SMALL"}
    fit_panel = interval[:fit_count]
    radius_panel = interval[fit_count:]
    mapping = _fit_me_tolerance_mapping(
        fit_panel,
        fitted=fitted,
        score_pair=(0, 1),
        proxy_pair=(2, 3),
        eigen_floor=eigen_floor,
        maximum_negative_mass_ratio=maximum_negative_mass_ratio,
        maximum_condition=maximum_condition,
    )
    if mapping["status"] != "ME_MAPPING_READY":
        return mapping
    corrected_radius, raw_radius = _mapped_radius_values(
        radius_panel,
        fitted=fitted,
        mapping=mapping,
        score_pair=(0, 1),
        proxy_pair=(2, 3),
    )
    radius = float(np.sort(corrected_radius)[order - 1])
    raw_tolerance_radius = float(np.sort(raw_radius)[order - 1])
    swapped_mapping = _fit_me_tolerance_mapping(
        fit_panel,
        fitted=fitted,
        score_pair=(2, 3),
        proxy_pair=(0, 1),
        eigen_floor=eigen_floor,
        maximum_negative_mass_ratio=maximum_negative_mass_ratio,
        maximum_condition=maximum_condition,
    )
    if swapped_mapping["status"] != "ME_MAPPING_READY":
        return {"status": "UNRESOLVED_PAIR_SWAP_MAPPING"}
    swapped_radius_values, _ = _mapped_radius_values(
        radius_panel,
        fitted=fitted,
        mapping=swapped_mapping,
        score_pair=(2, 3),
        proxy_pair=(0, 1),
    )
    swapped_radius = float(np.sort(swapped_radius_values)[order - 1])
    pair_swap_ratio = swapped_radius / max(radius, 1e-12)
    if not (
        float(minimum_pair_swap_radius_ratio)
        <= pair_swap_ratio
        <= float(maximum_pair_swap_radius_ratio)
    ):
        return {
            "status": "UNRESOLVED_PAIR_SWAP_INSTABILITY",
            "pair_swap_radius_ratio": pair_swap_ratio,
        }
    bootstrap = _mapping_bootstrap_stability(
        fit_panel=fit_panel,
        radius_panel=radius_panel,
        fitted=fitted,
        order=order,
        replicates=bootstrap_replicates,
        seed=bootstrap_seed,
        eigen_floor=eigen_floor,
        maximum_negative_mass_ratio=maximum_negative_mass_ratio,
        maximum_condition=maximum_condition,
    )
    if bootstrap["valid_rate"] < float(minimum_bootstrap_valid_rate):
        return {
            "status": "UNRESOLVED_BOOTSTRAP_VALID_RATE",
            **bootstrap,
        }
    if bootstrap["radius_cv"] > float(maximum_bootstrap_radius_cv):
        return {
            "status": "UNRESOLVED_BOOTSTRAP_RADIUS_CV",
            **bootstrap,
        }
    if (
        bootstrap["radius_quantile_ratio"]
        > float(maximum_bootstrap_radius_quantile_ratio)
    ):
        return {
            "status": "UNRESOLVED_BOOTSTRAP_RADIUS_SPREAD",
            **bootstrap,
        }
    evaluation_score = apply_spectrum_operator(
        evaluation[:, :2].mean(axis=1),
        fitted,
    )
    center = evaluation_score + np.asarray(mapping["bias"])
    target_trace = max(
        float(np.trace(mapping["target_covariance"])),
        1e-12,
    )
    return {
        "status": "ME_TOLERANCE_BALL_95_95",
        "center": center,
        "bias": mapping["bias"],
        "inverse_root": np.eye(dimension),
        "threshold": float(radius**2),
        "tolerance_radius": radius,
        "raw_proxy_tolerance_radius": raw_tolerance_radius,
        "tolerance_order": int(order),
        "achieved_tolerance_confidence": achieved_confidence,
        "bootstrap_valid_rate": float(bootstrap["valid_rate"]),
        "bootstrap_radius_cv": float(bootstrap["radius_cv"]),
        "bootstrap_radius_quantile_ratio": float(
            bootstrap["radius_quantile_ratio"]
        ),
        "pair_swap_radius_ratio": pair_swap_ratio,
        "negative_mass_ratio": mapping["negative_mass_ratio"],
        "psd_truncation_trace_ratio": mapping[
            "psd_truncation_trace_ratio"
        ],
        "condition_number": mapping["condition_number"],
        "effective_rank": mapping["latent_effective_rank"],
        "mapping_operator_norm": mapping["mapping_operator_norm"],
        "minimum_axis": radius,
        "maximum_axis": radius,
        "radius_scale_ratio": float(radius / np.sqrt(target_trace)),
        "radius_to_raw_proxy_ratio": float(
            radius / max(raw_tolerance_radius, 1e-12)
        ),
        "log_volume_proxy": float(
            dimension * np.log(max(radius, 1e-12))
        ),
    }


def paired_channel_metrics(
    sessions: np.ndarray,
    *,
    fitted: dict[str, Any],
    neighbor_count: int,
) -> dict[str, float]:
    """Measure repeated-author information in score and unresolved channels."""
    values = np.asarray(sessions, dtype=float)
    score_left = (
        apply_spectrum_operator(values[:, 0], fitted)
        - np.asarray(fitted["external_zero"])
    )
    score_right = (
        apply_spectrum_operator(values[:, 1], fitted)
        - np.asarray(fitted["external_zero"])
    )
    residual_left = unresolved_channel(values[:, 0], fitted)
    residual_right = unresolved_channel(values[:, 1], fitted)
    score = paired_similarity_metrics(
        score_left,
        score_right,
        neighbor_count=neighbor_count,
    )
    residual = paired_similarity_metrics(
        residual_left,
        residual_right,
        neighbor_count=neighbor_count,
        discovery=score_left,
    )
    return {
        "score_same_author_auc": float(score["same_author_auc"]),
        "score_hard_neighbor_auc": float(score["hard_neighbor_auc"]),
        "residual_same_author_auc": float(
            residual["same_author_auc"]
        ),
        "residual_hard_neighbor_auc": float(
            residual["hard_neighbor_auc"]
        ),
        "score_top1": float(score["top1"]),
        "residual_top1": float(residual["top1"]),
    }
