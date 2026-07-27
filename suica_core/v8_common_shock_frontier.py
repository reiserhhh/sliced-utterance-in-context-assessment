"""Repeated-opportunity common-shock frontier for SUICA V3.7H.2.

The module separates technical streams within one opportunity occasion from
repeated opportunity occasions. It operates on synthetic endpoint profiles
and preserves the frozen V3.7H score operator.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .v8_reliability_spectrum import _haar, apply_spectrum_operator
from .v8_resolution_filtration import _draw_stable


@dataclass(frozen=True)
class CommonShockSpec:
    """Synthetic repeated-opportunity endpoint design."""

    dimension: int = 48
    endpoint_budget: int = 512
    panel_authors: int = 256
    event_rms_at_64: float = 0.40
    student_df: float = 5.0
    heteroskedastic_strength: float = 0.35


def score_stable_energy(fitted: dict[str, Any]) -> float:
    """Return stable-author second moment after the frozen score operator."""
    operator = np.asarray(fitted["operator"], dtype=float)
    stable = np.asarray(fitted["stable_second_moment"], dtype=float)
    return max(
        float(np.trace(operator @ stable @ operator.T))
        / operator.shape[0],
        1e-12,
    )


def prepare_response_geometry(
    context: dict[str, Any],
    fitted: dict[str, Any],
    *,
    geometry: str,
    seed: int,
) -> dict[str, Any]:
    """Freeze one response map and calibrate its unit score-space energy."""
    rng = np.random.default_rng(int(seed))
    dimension = int(np.asarray(context["basis"]).shape[0])
    calibration = np.asarray(context["calibration_stable"], dtype=float)
    if geometry == "random_rotation":
        mapping = _haar(rng, dimension)
        parameters: dict[str, Any] = {"mapping": mapping}
        raw = calibration @ mapping.T
    elif geometry == "low_rank_linear":
        rank = min(4, dimension)
        left = _haar(rng, dimension)[:, :rank]
        right = _haar(rng, dimension)[:, :rank]
        parameters = {"left": left, "right": right}
        raw = (calibration @ left) @ right.T
    elif geometry == "nonlinear_tanh":
        rank = min(8, dimension)
        left = _haar(rng, dimension)[:, :rank]
        right = _haar(rng, dimension)[:, :rank]
        hidden = calibration @ left
        hidden_scale = np.maximum(hidden.std(axis=0, ddof=1), 1e-8)
        parameters = {
            "left": left,
            "right": right,
            "hidden_scale": hidden_scale,
        }
        raw = np.tanh(hidden / hidden_scale) @ right.T
    else:
        raise ValueError(f"unsupported response geometry: {geometry}")
    center = raw.mean(axis=0)
    raw = raw - center
    operator = np.asarray(fitted["operator"], dtype=float)
    raw_score_energy = max(
        float(np.mean((raw @ operator.T) ** 2)),
        1e-12,
    )
    return {
        "geometry": geometry,
        "parameters": parameters,
        "center": center,
        "unit_scale": float(np.sqrt(
            score_stable_energy(fitted) / raw_score_energy
        )),
    }


def apply_response_geometry(
    stable: np.ndarray,
    response_geometry: dict[str, Any],
    *,
    score_eta: float,
) -> np.ndarray:
    """Apply one frozen response map at a requested score-space effect."""
    values = np.asarray(stable, dtype=float)
    geometry = str(response_geometry["geometry"])
    parameters = response_geometry["parameters"]
    if geometry == "random_rotation":
        raw = values @ np.asarray(parameters["mapping"]).T
    elif geometry == "low_rank_linear":
        raw = (
            values @ np.asarray(parameters["left"])
        ) @ np.asarray(parameters["right"]).T
    elif geometry == "nonlinear_tanh":
        hidden = values @ np.asarray(parameters["left"])
        raw = np.tanh(
            hidden / np.asarray(parameters["hidden_scale"])
        ) @ np.asarray(parameters["right"]).T
    else:
        raise ValueError(f"unsupported response geometry: {geometry}")
    centered = raw - np.asarray(response_geometry["center"])
    return (
        np.sqrt(max(float(score_eta), 0.0))
        * float(response_geometry["unit_scale"])
        * centered
    )


def _standardized_draw(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    noise_mode: str,
    student_df: float,
) -> np.ndarray:
    if noise_mode == "gaussian":
        return rng.normal(size=shape)
    if noise_mode == "heteroskedastic_t5":
        df = float(student_df)
        if df <= 2.0:
            raise ValueError("student_df must exceed two")
        return rng.standard_t(df, size=shape) / np.sqrt(df / (df - 2.0))
    raise ValueError(f"unsupported noise mode: {noise_mode}")


def _author_noise_scale(
    stable: np.ndarray,
    *,
    noise_mode: str,
    strength: float,
) -> np.ndarray:
    if noise_mode == "gaussian":
        return np.ones(len(stable), dtype=float)
    anchor = np.asarray(stable, dtype=float)[:, 0]
    anchor = (
        anchor - anchor.mean()
    ) / max(float(anchor.std(ddof=1)), 1e-8)
    return np.clip(np.exp(float(strength) * anchor), 0.45, 2.20)


def _score_calibrated_random_vector(
    rng: np.random.Generator,
    fitted: dict[str, Any],
    *,
    score_eta: float,
) -> np.ndarray:
    dimension = int(np.asarray(fitted["operator"]).shape[0])
    raw = rng.normal(size=dimension)
    operator = np.asarray(fitted["operator"], dtype=float)
    raw_energy = max(float(np.mean((raw @ operator.T) ** 2)), 1e-12)
    return raw * np.sqrt(
        float(score_eta) * score_stable_energy(fitted) / raw_energy
    )


def simulate_common_shock_panel(
    context: dict[str, Any],
    fitted: dict[str, Any],
    response_geometry: dict[str, Any],
    *,
    seed: int,
    spec: CommonShockSpec,
    opportunity_repeats: int,
    stream_correlation: float,
    common_shock_score_energy: float,
    noise_mode: str,
    response_score_eta: float,
    effect_source: str = "author_response",
    global_shift_score_eta: float = 0.0,
) -> dict[str, Any]:
    """Generate schedules x occasions x streams for the same authors."""
    repeats = int(opportunity_repeats)
    if repeats < 1:
        raise ValueError("opportunity_repeats must be positive")
    rho = float(stream_correlation)
    if not 0.0 <= rho < 1.0:
        raise ValueError("stream_correlation must be in [0, 1)")
    if effect_source not in {
        "author_response",
        "persistent_schedule_confound",
    }:
        raise ValueError(f"unsupported effect_source: {effect_source}")

    streams = np.random.SeedSequence(int(seed)).spawn(5)
    stable = _draw_stable(
        np.random.default_rng(streams[0]),
        int(spec.panel_authors),
        np.asarray(context["basis"], dtype=float),
        np.asarray(context["variance"], dtype=float),
    ) * float(context["stable_scale"])
    response = apply_response_geometry(
        stable,
        response_geometry,
        score_eta=float(response_score_eta),
    )
    operator = np.asarray(fitted["operator"], dtype=float)
    stable_energy = score_stable_energy(fitted)
    achieved_response_eta = float(
        np.mean((response @ operator.T) ** 2) / stable_energy
    )

    count = len(stable)
    dimension = int(spec.dimension)
    author_scale = _author_noise_scale(
        stable,
        noise_mode=noise_mode,
        strength=float(spec.heteroskedastic_strength),
    )
    event_root = np.asarray(context["event_root"], dtype=float)
    covariance = event_root @ event_root.T
    base_score_energy = max(
        float(np.trace(operator @ covariance @ operator.T)) / dimension,
        1e-12,
    )

    common_standard = _standardized_draw(
        np.random.default_rng(streams[1]),
        (count, 2, repeats, dimension),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    common_scale = 0.0
    if float(common_shock_score_energy) > 0.0:
        common_scale = float(np.sqrt(
            float(common_shock_score_energy)
            * stable_energy
            / (
                base_score_energy
                * max(float(np.mean(author_scale**2)), 1e-12)
            )
        ))
    common = (
        common_standard @ event_root.T
        * common_scale
        * author_scale[:, None, None, None]
    )

    shared_standard = _standardized_draw(
        np.random.default_rng(streams[2]),
        (count, 2, repeats, dimension),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    individual_standard = _standardized_draw(
        np.random.default_rng(streams[3]),
        (count, 2, repeats, 2, dimension),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    combined = (
        np.sqrt(rho) * shared_standard[:, :, :, None]
        + np.sqrt(1.0 - rho) * individual_standard
    )
    endpoint_scale = (
        float(spec.event_rms_at_64)
        * np.sqrt(64.0 / float(spec.endpoint_budget))
    )
    technical = (
        combined @ event_root.T
        * endpoint_scale
        * author_scale[:, None, None, None, None]
    )

    origin = np.asarray(context["origin"], dtype=float)
    values = (
        origin[None, None, None, None]
        + stable[:, None, None, None]
        + common[:, :, :, None]
        + technical
    )
    values[:, 1] += response[:, None, None]

    global_shift = np.zeros(dimension, dtype=float)
    if float(global_shift_score_eta) > 0.0:
        global_shift = _score_calibrated_random_vector(
            np.random.default_rng(streams[4]),
            fitted,
            score_eta=float(global_shift_score_eta),
        )
        values[:, 1] += global_shift[None, None, None]

    achieved_common_eta = float(
        np.mean((common.reshape(-1, dimension) @ operator.T) ** 2)
        / stable_energy
    )
    achieved_global_eta = float(
        np.mean((global_shift @ operator.T) ** 2) / stable_energy
    )
    return {
        "values": values,
        "stable": stable,
        "response": response,
        "global_shift": global_shift,
        "effect_source": effect_source,
        "achieved_response_score_eta": achieved_response_eta,
        "achieved_common_shock_score_energy": achieved_common_eta,
        "achieved_global_shift_score_eta": achieved_global_eta,
    }


def score_common_shock_panel(
    panel: np.ndarray,
    fitted: dict[str, Any],
) -> np.ndarray:
    """Apply one frozen endpoint score operator to all observations."""
    values = np.asarray(panel, dtype=float)
    if values.ndim != 5 or values.shape[1] != 2 or values.shape[3] != 2:
        raise ValueError(
            "panel must be authors x two schedules x occasions x two streams x dims"
        )
    flat = values.reshape(-1, values.shape[-1])
    return apply_spectrum_operator(flat, fitted).reshape(values.shape)


def _schedule_energies(scores: np.ndarray) -> dict[str, float | np.ndarray]:
    values = np.asarray(scores, dtype=float)
    schedule_mean = values.mean(axis=(2, 3))
    difference = schedule_mean[:, 1] - schedule_mean[:, 0]
    total = float(np.mean(difference**2))
    author = float(np.var(difference, axis=0, ddof=1).mean())
    mean_shift = float(np.mean(difference.mean(axis=0) ** 2))
    return {
        "difference": difference,
        "total_energy": total,
        "author_energy": author,
        "mean_shift_energy": mean_shift,
    }


def legacy_stream_excess(
    scores: np.ndarray,
    fitted: dict[str, Any],
) -> dict[str, float]:
    """Estimate schedule excess using only within-occasion stream contrasts."""
    values = np.asarray(scores, dtype=float)
    repeats = int(values.shape[2])
    energies = _schedule_energies(values)
    half_difference = (values[:, :, :, 0] - values[:, :, :, 1]) / 2.0
    correction = float(
        sum(
            np.mean(half_difference[:, schedule] ** 2)
            for schedule in range(2)
        )
        / repeats
    )
    scale = score_stable_energy(fitted)
    return {
        "identified": 1.0,
        "total_energy": float(energies["total_energy"]),
        "author_energy": float(energies["author_energy"]),
        "mean_shift_energy": float(energies["mean_shift_energy"]),
        "noise_correction": correction,
        "q_total": float(
            (float(energies["total_energy"]) - correction) / scale
        ),
        "q_author": float(
            (float(energies["author_energy"]) - correction) / scale
        ),
    }


def repeated_opportunity_excess(
    scores: np.ndarray,
    fitted: dict[str, Any],
) -> dict[str, float]:
    """Estimate schedule excess from repeated opportunity occasions."""
    values = np.asarray(scores, dtype=float)
    repeats = int(values.shape[2])
    energies = _schedule_energies(values)
    if repeats < 2:
        return {
            "identified": 0.0,
            "total_energy": float(energies["total_energy"]),
            "author_energy": float(energies["author_energy"]),
            "mean_shift_energy": float(energies["mean_shift_energy"]),
            "noise_correction": float("nan"),
            "q_total": float("nan"),
            "q_author": float("nan"),
        }
    replicate_mean = values.mean(axis=3)
    within = np.var(replicate_mean, axis=2, ddof=1)
    correction = float(
        sum(np.mean(within[:, schedule]) for schedule in range(2))
        / repeats
    )
    scale = score_stable_energy(fitted)
    return {
        "identified": 1.0,
        "total_energy": float(energies["total_energy"]),
        "author_energy": float(energies["author_energy"]),
        "mean_shift_energy": float(energies["mean_shift_energy"]),
        "noise_correction": correction,
        "q_total": float(
            (float(energies["total_energy"]) - correction) / scale
        ),
        "q_author": float(
            (float(energies["author_energy"]) - correction) / scale
        ),
    }
