"""Synthetic error-theory worlds for SUICA measurement design."""
from __future__ import annotations

import hashlib
import json
import math
import platform
from pathlib import Path
from typing import Any

import numpy as np


def fixed_reference_shift(rng: np.random.Generator, n: int) -> dict[str, float]:
    """Compare immutable reference norms with score-dependent batch norms."""
    reference = rng.normal(size=5_000)
    focal = rng.normal(size=n)
    high_composition = np.r_[focal, rng.normal(2.0, 1.0, n)]
    low_composition = np.r_[focal, rng.normal(-2.0, 1.0, n)]
    ref_mean, ref_sd = reference.mean(), reference.std()
    fixed_a = (focal - ref_mean) / ref_sd
    fixed_b = (focal - ref_mean) / ref_sd
    batch_a = (focal - high_composition.mean()) / high_composition.std()
    batch_b = (focal - low_composition.mean()) / low_composition.std()
    return {
        "fixed_reference_mean_abs_shift": float(np.mean(abs(fixed_a - fixed_b))),
        "batch_norm_mean_abs_shift": float(np.mean(abs(batch_a - batch_b))),
    }


def _occasion_amplitudes(rng: np.random.Generator, kappa: float, occasions: int,
                         windows: int, noise: float) -> np.ndarray:
    phase = rng.uniform(0, 2 * np.pi)
    t = np.arange(windows)
    out = []
    for _ in range(occasions):
        path = kappa * np.sin(2 * np.pi * t / windows + phase)
        path += rng.normal(0, noise, windows)
        out.append(math.sqrt(max(2 * (np.var(path, ddof=1) - noise**2), 0)))
    return np.asarray(out)


def occasion_error_curve(rng: np.random.Generator, mc: int, persons: int,
                         windows: int) -> list[dict[str, float | int | str]]:
    rows = []
    for occasions in (1, 2, 4, 8, 16):
        errors, covered, half_widths = [], [], []
        for _ in range(mc):
            truth = rng.lognormal(mean=-.15, sigma=.35, size=persons)
            estimates = np.asarray([
                _occasion_amplitudes(rng, value, occasions, windows, .45).mean()
                for value in truth
            ])
            # Calibration is learned on a reference half and evaluated on a
            # disjoint focal half. This corrects nonlinear amplitude bias while
            # preserving the fixed-reference measurement design.
            fit_end = persons // 4
            calibration_end = persons // 2
            fit = np.arange(fit_end)
            calibration = np.arange(fit_end, calibration_end)
            focal = np.arange(calibration_end, persons)
            design = np.column_stack([np.ones(len(fit)), estimates[fit]])
            beta = np.linalg.lstsq(design, truth[fit], rcond=None)[0]
            calibrated_reference = beta[0] + beta[1] * estimates[calibration]
            residual = np.abs(truth[calibration] - calibrated_reference)
            # Split-conformal finite-sample quantile. ``higher`` prevents
            # interpolation from making the coverage guarantee anti-conservative.
            level = min(1.0, math.ceil((len(residual) + 1) * .95) / len(residual))
            half_width = float(np.quantile(residual, level, method="higher"))
            calibrated = beta[0] + beta[1] * estimates[focal]
            focal_error = calibrated - truth[focal]
            errors.extend(focal_error.tolist())
            if occasions >= 2:
                covered.extend((np.abs(focal_error) <= half_width).tolist())
                half_widths.append(half_width)
        if occasions == 1:
            rows.append({"occasions": occasions, "rmse": float(np.sqrt(np.mean(np.square(errors)))),
                         "coverage": math.nan, "mdd": math.nan,
                         "guard": "single-occasion uncertainty unidentifiable"})
        else:
            rows.append({"occasions": occasions, "rmse": float(np.sqrt(np.mean(np.square(errors)))),
                         "coverage": float(np.mean(covered)),
                         "mdd": float(math.sqrt(2) * np.mean(half_widths)),
                         "guard": "fixed-reference calibrated"})
    return rows


def scorer_perturbation_curve(rng: np.random.Generator, persons: int) -> list[dict[str, float]]:
    latent = rng.normal(size=(persons, 3))
    base_loading, _ = np.linalg.qr(rng.normal(size=(12, 3)))
    base = latent @ base_loading.T + rng.normal(0, .15, (persons, 12))
    rows = []
    for magnitude in (0.0, .02, .05, .10, .20):
        perturb = rng.normal(size=base_loading.shape)
        loading, _ = np.linalg.qr(base_loading + magnitude * perturb)
        changed = latent @ loading.T + rng.normal(0, .15, (persons, 12))
        score_r = np.mean([np.corrcoef(base[:, j], changed[:, j])[0, 1] for j in range(12)])
        singular = np.linalg.svd(base_loading.T @ loading, compute_uv=False)
        rows.append({"perturbation": magnitude, "score_retest": float(score_r),
                     "subspace_congruence": float(np.mean(singular))})
    return rows


def window_perturbation_curve(rng: np.random.Generator, persons: int) -> list[dict[str, float | int | str]]:
    rows = []
    length = 512
    amplitudes = rng.lognormal(-.1, .3, persons)
    paths = np.array([a * np.sin(2*np.pi*np.arange(length)/32 + rng.uniform(0, 2*np.pi))
                      + rng.normal(0, .4, length) for a in amplitudes])
    reference = paths.reshape(persons, -1, 32).std(axis=2).mean(axis=1)
    for window in (16, 32, 64, 128):
        for offset in (0, window // 2):
            usable = paths[:, offset:offset + ((length-offset)//window)*window]
            if usable.shape[1] < 4 * window:
                rows.append({"window": window, "offset": offset, "retest": math.nan,
                             "guard": "fewer than four windows"})
                continue
            score = usable.reshape(persons, -1, window).std(axis=2).mean(axis=1)
            rows.append({"window": window, "offset": offset,
                         "retest": float(np.corrcoef(reference, score)[0, 1]), "guard": "ok"})
    return rows


def response_excitation_world(rng: np.random.Generator, persons: int) -> dict[str, float]:
    truth = rng.normal(.6, .2, persons)
    estimates, single_context_rank = [], []
    for u in range(persons):
        z = np.tile([-1., 1.], 8)
        y = .4 + truth[u] * z + rng.normal(0, .25, len(z))
        design = np.column_stack([np.ones(len(z)), z])
        estimates.append(np.linalg.lstsq(design, y, rcond=None)[0][1])
        single_context_rank.append(np.linalg.matrix_rank(design[z > 0]))
    return {"response_rmse": float(np.sqrt(np.mean((np.asarray(estimates)-truth)**2))),
            "single_context_refusal_rate": float(np.mean(np.asarray(single_context_rank) < 2))}


def dialogue_response_world(rng: np.random.Generator, persons: int, sessions: int,
                            turns: int) -> dict[str, float]:
    inertia = rng.uniform(.15, .65, persons)
    accommodation = rng.uniform(.1, .5, persons)
    fixed_errors, omitted_errors = [], []
    for u in range(persons):
        x_rows, y_rows, omitted_x = [], [], []
        for s in range(sessions):
            x = rng.normal(); agent_style = rng.normal(0, .7)
            for _ in range(turns):
                reply = .55 * x + agent_style + rng.normal(0, .35)
                nxt = inertia[u] * x + accommodation[u] * reply + rng.normal(0, .35)
                x_rows.append([x, reply]); omitted_x.append([x]); y_rows.append(nxt)
                x = nxt
        full = np.linalg.lstsq(np.asarray(x_rows), y_rows, rcond=None)[0]
        omitted = np.linalg.lstsq(np.asarray(omitted_x), y_rows, rcond=None)[0]
        fixed_errors.append(np.linalg.norm(full - [inertia[u], accommodation[u]]))
        omitted_errors.append(abs(omitted[0] - inertia[u]))
    return {"observed_partner_input_error": float(np.mean(fixed_errors)),
            "unobserved_partner_input_bias": float(np.mean(omitted_errors))}


def run_measurement_error(config: dict[str, Any], config_hash: str) -> dict[str, Any]:
    rng = np.random.default_rng(config["seed"])
    result = {
        "schema_version": 1, "profile": config["profile"], "seed": config["seed"],
        "config_hash": config_hash, "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "fixed_reference": fixed_reference_shift(rng, config["persons"]),
        "occasion_curve": occasion_error_curve(rng, config["mc"], config["persons"], config["windows"]),
        "scorer_curve": scorer_perturbation_curve(rng, config["persons"]),
        "window_curve": window_perturbation_curve(rng, config["persons"]),
        "response_excitation": response_excitation_world(rng, config["persons"]),
        "dialogue_response": dialogue_response_world(rng, config["persons"], config["sessions"], config["turns"]),
    }
    source = Path(__file__).read_bytes()
    result["code_hash"] = hashlib.sha256(source).hexdigest()
    result["gates"] = {
        "fixed_reference": result["fixed_reference"]["fixed_reference_mean_abs_shift"] < .01,
        "batch_norm_detected": result["fixed_reference"]["batch_norm_mean_abs_shift"] > .25,
        "occasion_error_decreases": result["occasion_curve"][-1]["rmse"] < result["occasion_curve"][1]["rmse"],
        "occasion_ci_calibrated": .93 <= result["occasion_curve"][-1]["coverage"] <= .97,
        "scorer_small_perturbation_stable": min(
            row["subspace_congruence"] for row in result["scorer_curve"]
            if row["perturbation"] <= .10) >= .95,
        "scorer_large_perturbation_detected": (
            result["scorer_curve"][-1]["subspace_congruence"] < .90
            or result["scorer_curve"][-1]["score_retest"] < .50),
        "window_stability": min(
            row["retest"] for row in result["window_curve"] if row["guard"] == "ok") >= .65,
        "window_support_refused": any(
            row["guard"] != "ok" for row in result["window_curve"]),
        "single_occasion_refused": result["occasion_curve"][0]["guard"] != "ok",
        "response_excitation": result["response_excitation"]["response_rmse"] < .10,
        "single_context_refused": result["response_excitation"]["single_context_refusal_rate"] >= .95,
        "dialogue_input_required": result["dialogue_response"]["observed_partner_input_error"] < result["dialogue_response"]["unobserved_partner_input_bias"],
    }
    return result


def write_measurement_report(result: dict[str, Any], out: Path) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"v6_measurement_error_{result['profile']}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return path
