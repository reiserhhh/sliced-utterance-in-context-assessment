"""Nested-resolution profile mechanics for SUICA V8.3.7H.

This module operates on synthetic author-relative profile vectors. It creates
genuinely nested event prefixes and fits one jointly selected spectral rule
across all budgets. Synthetic latent truth is returned for scorer-side risk
audits only; selection and coherence prediction use observable panels.
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
    _psd,
    _scale_rms,
    _sqrt_and_inverse,
    apply_spectrum_operator,
    unresolved_channel,
)


CORE_WORLDS = (
    "exact_rank12_nested_gaussian",
    "dense_tail48_nested_gaussian",
    "broken_spectrum48_nested_gaussian",
    "long_memory_dense_nested",
)

STRESS_WORLDS = (
    "null_zero_author",
    "author_permutation",
    "state_alias_single_occasion",
    "state_two_occasion_identifiable",
    "informative_precision_dense",
    "student_t5_dense",
    "reference_panel_switch",
    "opportunity_schedule_drift",
)


@dataclass(frozen=True)
class ResolutionFiltrationWorldSpec:
    """One nested synthetic profile world."""

    world: str = "dense_tail48_nested_gaussian"
    dimension: int = 48
    sessions: int = 4
    budgets: tuple[int, ...] = (32, 64, 128, 256, 512)
    reference_authors: int = 256
    calibration_authors: int = 256
    probe_authors: int = 256
    interval_authors: int = 384
    evaluation_authors: int = 256
    stable_rms: float = 0.30
    event_rms_at_64: float = 0.40
    state_rms: float = 0.16
    long_memory_rho: float = 0.70
    opportunity_shift_rms: float = 0.18
    opportunity_shift_start: int = 128
    reference_shift_rms: float = 0.15
    student_df: float = 5.0


def _variance_spectrum(world: str, dimension: int) -> np.ndarray:
    index = np.arange(1, dimension + 1, dtype=float)
    if world in {"exact_rank12_nested_gaussian", "author_permutation"}:
        values = np.zeros(dimension, dtype=float)
        values[: min(12, dimension)] = 1.0
        return values
    if world == "null_zero_author":
        return np.zeros(dimension, dtype=float)
    if world == "broken_spectrum48_nested_gaussian":
        template = np.concatenate([
            np.full(4, 1.0),
            np.full(4, 0.35),
            np.full(8, 0.10),
            np.full(16, 0.025),
            np.full(max(dimension - 32, 0), 0.006),
        ])
        return template[:dimension]
    if world in {
        "dense_tail48_nested_gaussian",
        "long_memory_dense_nested",
        "state_alias_single_occasion",
        "state_two_occasion_identifiable",
        "informative_precision_dense",
        "student_t5_dense",
        "reference_panel_switch",
        "opportunity_schedule_drift",
    }:
        return (1.0 + index / 4.0) ** -1.50
    raise ValueError(f"unsupported V3.7H world: {world}")


def _draw_stable(
    rng: np.random.Generator,
    authors: int,
    basis: np.ndarray,
    variance: np.ndarray,
) -> np.ndarray:
    scores = rng.normal(size=(authors, len(variance)))
    return (scores * np.sqrt(variance)[None]) @ basis.T


def _state_array(
    *,
    rng: np.random.Generator,
    authors: int,
    sessions: int,
    dimension: int,
    rms: float,
    mode: str,
) -> np.ndarray:
    if mode == "none":
        return np.zeros((authors, sessions, dimension), dtype=float)
    basis = _haar(rng, dimension)[:, : min(8, dimension)]
    if mode == "single":
        score = rng.normal(size=(authors, 1, basis.shape[1]))
        score = np.repeat(score, sessions, axis=1)
    elif mode == "two":
        if sessions != 4:
            raise ValueError("two-occasion state requires four sessions")
        occasion = rng.normal(size=(authors, 2, basis.shape[1]))
        score = np.stack(
            [occasion[:, 0], occasion[:, 0], occasion[:, 1], occasion[:, 1]],
            axis=1,
        )
    else:
        raise ValueError(f"unknown state mode: {mode}")
    return _scale_rms(np.einsum("asr,dr->asd", score, basis), rms)


def _long_memory_scale(rho: float, budget: int) -> float:
    lags = np.arange(1, budget, dtype=float)
    inflation = 1.0 + 2.0 * float(np.sum(
        (1.0 - lags / float(budget)) * float(rho) ** lags
    ))
    return float(np.sqrt(max(inflation, 1e-12)))


def _nested_event_noise(
    *,
    rng: np.random.Generator,
    authors: int,
    sessions: int,
    budgets: tuple[int, ...],
    covariance_root: np.ndarray,
    event_rms_at_64: float,
    mode: str,
    stable: np.ndarray,
    long_memory_rho: float,
    student_df: float,
) -> tuple[np.ndarray, float]:
    """Generate cumulative event means from shared incremental blocks."""
    dimension = covariance_root.shape[0]
    maximum = int(budgets[-1])
    per_event_scale = float(event_rms_at_64) * np.sqrt(64.0)
    informative_scale = np.ones(authors, dtype=float)
    if mode == "informative":
        anchor = stable[:, 0]
        anchor = (
            anchor - anchor.mean()
        ) / max(float(anchor.std(ddof=1)), 1e-8)
        informative_scale = np.clip(np.exp(0.35 * anchor), 0.45, 2.20)

    snapshots: list[np.ndarray] = []
    block_sums: list[np.ndarray] = []
    cumulative = np.zeros((authors, sessions, dimension), dtype=float)
    previous = 0
    if mode == "long_memory":
        rho = float(long_memory_rho)
        innovation_scale = np.sqrt(max(1.0 - rho**2, 0.0))
        process = np.zeros_like(cumulative)
        unscaled = np.zeros_like(cumulative)
        budget_set = set(int(value) for value in budgets)
        adjustment = _long_memory_scale(rho, 64)
        for event in range(1, maximum + 1):
            process = (
                rho * process
                + innovation_scale
                * rng.normal(size=(authors, sessions, dimension))
            )
            unscaled += process
            if event in budget_set:
                transformed = (
                    unscaled @ covariance_root.T
                    * (per_event_scale / adjustment)
                )
                snapshots.append(transformed / float(event))
        prefix_means = np.stack(snapshots, axis=2)
        return prefix_means, 0.0

    for budget in budgets:
        block_size = int(budget) - previous
        if block_size <= 0:
            raise ValueError("budgets must be strictly increasing")
        if mode == "student_t":
            df = float(student_df)
            standardized = (
                rng.standard_t(
                    df,
                    size=(authors, sessions, dimension),
                )
                / np.sqrt(df / (df - 2.0))
            )
        else:
            standardized = rng.normal(
                size=(authors, sessions, dimension)
            )
        block = (
            standardized
            @ covariance_root.T
            * (per_event_scale * np.sqrt(float(block_size)))
        )
        block *= informative_scale[:, None, None]
        block_sums.append(block)
        cumulative = cumulative + block
        snapshots.append(cumulative / float(budget))
        previous = int(budget)
    reconstructed = np.cumsum(np.stack(block_sums, axis=2), axis=2)
    direct = np.stack(
        [
            snapshots[index] * float(budget)
            for index, budget in enumerate(budgets)
        ],
        axis=2,
    )
    identity_error = float(np.max(np.abs(reconstructed - direct)))
    return np.stack(snapshots, axis=2), identity_error


def simulate_resolution_filtration_world(
    *,
    latent_seed: int,
    event_seed: int,
    spec: ResolutionFiltrationWorldSpec,
) -> dict[str, Any]:
    """Generate disjoint panels with truly nested event prefixes."""
    budgets = tuple(int(value) for value in spec.budgets)
    if len(budgets) < 2 or budgets != tuple(sorted(set(budgets))):
        raise ValueError("budgets must be sorted and unique")
    if spec.sessions != 4:
        raise ValueError("V3.7H requires four technical streams")
    if spec.world not in set(CORE_WORLDS) | set(STRESS_WORLDS):
        raise ValueError(f"unsupported V3.7H world: {spec.world}")

    names = (
        "reference_a",
        "reference_b",
        "calibration_a",
        "calibration_b",
        "probe",
        "interval",
        "evaluation",
    )
    counts = {
        "reference_a": int(spec.reference_authors),
        "reference_b": int(spec.reference_authors),
        "calibration_a": int(spec.calibration_authors),
        "calibration_b": int(spec.calibration_authors),
        "probe": int(spec.probe_authors),
        "interval": int(spec.interval_authors),
        "evaluation": int(spec.evaluation_authors),
    }
    streams = np.random.SeedSequence(latent_seed).spawn(6 + len(names))
    rng_basis = np.random.default_rng(streams[0])
    rng_zero = np.random.default_rng(streams[1])
    rng_event_basis = np.random.default_rng(streams[2])
    rng_state_basis = np.random.default_rng(streams[3])
    rng_shift = np.random.default_rng(streams[4])
    basis = _haar(rng_basis, spec.dimension)
    variance = _variance_spectrum(spec.world, spec.dimension)
    true_zero = _scale_rms(
        rng_zero.normal(size=spec.dimension),
        0.20,
    )
    stable_scale = (
        float(spec.stable_rms)
        / max(float(np.sqrt(np.mean(variance))), 1e-12)
        if np.any(variance > 0.0)
        else 0.0
    )
    stable = {
        name: _draw_stable(
            np.random.default_rng(streams[6 + index]),
            counts[name],
            basis,
            variance,
        )
        * stable_scale
        for index, name in enumerate(names)
    }

    reference_shift = np.zeros(spec.dimension, dtype=float)
    if spec.world == "reference_panel_switch":
        reference_shift = _scale_rms(
            rng_shift.normal(size=spec.dimension),
            float(spec.reference_shift_rms),
        )
        stable["reference_b"] = (
            stable["reference_b"] + reference_shift[None]
        )

    event_basis = _haar(rng_event_basis, spec.dimension)
    event_values = np.linspace(0.55, 1.45, spec.dimension)
    event_root = (
        event_basis * np.sqrt(event_values)[None]
    ) @ event_basis.T
    opportunity_rotation = _haar(rng_shift, spec.dimension)
    event_streams = np.random.SeedSequence(event_seed).spawn(len(names))

    panels: dict[str, np.ndarray] = {}
    truths: dict[str, np.ndarray] = {}
    prefix_errors: list[float] = []
    for index, name in enumerate(names):
        value = stable[name]
        repeated = np.repeat(
            value[:, None],
            spec.sessions,
            axis=1,
        )
        if spec.world == "author_permutation":
            permutation_rng = np.random.default_rng(event_streams[index])
            for session in range(1, spec.sessions):
                repeated[:, session] = value[
                    permutation_rng.permutation(len(value))
                ]
            event_rng = permutation_rng
        else:
            event_rng = np.random.default_rng(event_streams[index])

        if spec.world == "state_alias_single_occasion":
            state_mode = "single"
        elif spec.world == "state_two_occasion_identifiable":
            state_mode = "two"
        else:
            state_mode = "none"
        state = _state_array(
            rng=np.random.default_rng(
                np.random.SeedSequence(
                    [latent_seed, index, 0x37]
                )
            ),
            authors=len(value),
            sessions=spec.sessions,
            dimension=spec.dimension,
            rms=float(spec.state_rms),
            mode=state_mode,
        )
        if spec.world == "long_memory_dense_nested":
            noise_mode = "long_memory"
        elif spec.world == "informative_precision_dense":
            noise_mode = "informative"
        elif spec.world == "student_t5_dense":
            noise_mode = "student_t"
        else:
            noise_mode = "gaussian"
        noise, prefix_error = _nested_event_noise(
            rng=event_rng,
            authors=len(value),
            sessions=spec.sessions,
            budgets=budgets,
            covariance_root=event_root,
            event_rms_at_64=float(spec.event_rms_at_64),
            mode=noise_mode,
            stable=value,
            long_memory_rho=float(spec.long_memory_rho),
            student_df=float(spec.student_df),
        )
        prefix_errors.append(prefix_error)

        drift = np.zeros(
            (len(value), spec.sessions, len(budgets), spec.dimension),
            dtype=float,
        )
        if spec.world == "opportunity_schedule_drift":
            response = _scale_rms(
                value @ opportunity_rotation.T,
                float(spec.opportunity_shift_rms),
            )
            for budget_index, budget in enumerate(budgets):
                fraction = max(
                    int(budget) - int(spec.opportunity_shift_start),
                    0,
                ) / float(budget)
                drift[:, :, budget_index] = (
                    fraction * response[:, None]
                )

        panels[name] = (
            true_zero[None, None, None]
            + repeated[:, :, None]
            + state[:, :, None]
            + drift
            + noise
        )
        truths[name] = true_zero[None] + value

    return {
        "world": spec.world,
        "budgets": budgets,
        "panels": panels,
        "truths": truths,
        "true_zero": true_zero,
        "stable_basis": basis,
        "stable_variance": variance * stable_scale**2,
        "reference_shift": reference_shift,
        "maximum_prefix_identity_error": float(max(prefix_errors)),
        "design": {
            "core_world": spec.world in CORE_WORLDS,
            "single_occasion_state_alias": (
                spec.world == "state_alias_single_occasion"
            ),
            "two_occasion_state_identifiable": (
                spec.world == "state_two_occasion_identifiable"
            ),
            "reference_switch": spec.world == "reference_panel_switch",
            "opportunity_schedule_drift": (
                spec.world == "opportunity_schedule_drift"
            ),
            "event_mode": (
                "ar1"
                if spec.world == "long_memory_dense_nested"
                else (
                    "student_t_block"
                    if spec.world == "student_t5_dense"
                    else "independent_increment_blocks"
                )
            ),
        },
    }


def resolution_candidates() -> list[dict[str, Any]]:
    """Return globally selected weight rules shared by all budgets."""
    candidates = [
        {
            "family": "wiener",
            "tau": tau,
            "name": f"wiener_tau_{tau:g}",
        }
        for tau in (0.25, 0.50, 1.0, 2.0, 4.0)
    ]
    candidates.extend(
        {
            "family": "hard_reliability",
            "threshold": threshold,
            "name": f"hard_q_{threshold:g}",
        }
        for threshold in (0.20, 0.40, 0.60, 0.80)
    )
    return candidates


def _stable_cross_moment(
    left: np.ndarray,
    right: np.ndarray,
    zero: np.ndarray,
) -> np.ndarray:
    x = np.asarray(left, dtype=float) - np.asarray(zero)
    y = np.asarray(right, dtype=float) - np.asarray(zero)
    return _psd((x.T @ y + y.T @ x) / (2.0 * len(x)))


def _spectrum_from_moments(
    stable: np.ndarray,
    left: np.ndarray,
    right: np.ndarray,
    *,
    external_zero: np.ndarray,
    noise_shrinkage: float,
    eigen_floor: float,
) -> dict[str, Any]:
    difference = np.asarray(left, dtype=float) - np.asarray(right, dtype=float)
    difference -= difference.mean(axis=0, keepdims=True)
    noise = difference.T @ difference / (2.0 * len(difference))
    average = max(float(np.trace(noise)) / len(noise), 1e-10)
    regularized = (
        (1.0 - float(noise_shrinkage)) * noise
        + float(noise_shrinkage) * average * np.eye(len(noise))
    )
    root, inverse = _sqrt_and_inverse(
        regularized,
        relative_floor=float(eigen_floor),
    )
    whitened = _psd(inverse @ stable @ inverse.T)
    eta, modes = np.linalg.eigh(whitened)
    order = np.argsort(eta)[::-1]
    return {
        "external_zero": np.asarray(external_zero, dtype=float),
        "stable_second_moment": np.asarray(stable, dtype=float),
        "event_second_moment": noise,
        "event_regularized": regularized,
        "event_root": root,
        "event_inverse": inverse,
        "modes": modes[:, order],
        "eta": np.maximum(eta[order], 0.0),
    }


def fit_resolution_spectra(
    sessions: np.ndarray,
    *,
    budgets: Iterable[int],
    external_zero: np.ndarray,
    noise_shrinkage: float = 0.25,
    eigen_floor: float = 1e-6,
) -> dict[int, dict[str, Any]]:
    """Fit one stable moment and a budget-specific event geometry."""
    values = np.asarray(sessions, dtype=float)
    budget_list = [int(value) for value in budgets]
    if values.ndim != 4 or values.shape[1] != 4:
        raise ValueError("sessions must be authors x four streams x budgets x dims")
    if values.shape[2] != len(budget_list):
        raise ValueError("budget count does not match the session tensor")
    left_max = values[:, :2, -1].mean(axis=1)
    right_max = values[:, 2:4, -1].mean(axis=1)
    stable = _stable_cross_moment(left_max, right_max, external_zero)
    output: dict[int, dict[str, Any]] = {}
    for index, budget in enumerate(budget_list):
        left = values[:, :2, index].mean(axis=1)
        right = values[:, 2:4, index].mean(axis=1)
        output[budget] = _spectrum_from_moments(
            stable,
            left,
            right,
            external_zero=external_zero,
            noise_shrinkage=noise_shrinkage,
            eigen_floor=eigen_floor,
        )
    return output


def resolution_operator(
    spectrum: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    """Construct one budget operator from a shared response rule."""
    eta = np.maximum(np.asarray(spectrum["eta"], dtype=float), 0.0)
    reliability = eta / np.maximum(eta + 1.0, 1e-12)
    if candidate["family"] == "wiener":
        tau = float(candidate["tau"])
        weights = eta / np.maximum(eta + tau, 1e-12)
    elif candidate["family"] == "hard_reliability":
        weights = (
            reliability >= float(candidate["threshold"])
        ).astype(float)
    else:
        raise ValueError(f"unknown resolution family: {candidate['family']}")
    modes = np.asarray(spectrum["modes"])
    operator = (
        np.asarray(spectrum["event_root"])
        @ modes
        @ np.diag(weights)
        @ modes.T
        @ np.asarray(spectrum["event_inverse"])
    )
    return {
        **spectrum,
        "candidate": dict(candidate),
        "weights": weights,
        "operator": operator,
        "effective_df": float(weights.sum()),
    }


def select_joint_resolution_candidate(
    sessions: np.ndarray,
    *,
    budgets: Iterable[int],
    external_zero: np.ndarray,
    candidates: Iterable[dict[str, Any]],
    folds: int,
    seed: int,
    noise_shrinkage: float,
) -> tuple[dict[str, Any], pd.DataFrame]:
    """Select one weight rule jointly across every registered budget."""
    values = np.asarray(sessions, dtype=float)
    budget_list = [int(value) for value in budgets]
    candidate_list = [dict(value) for value in candidates]
    order = np.random.default_rng(seed).permutation(len(values))
    partitions = np.array_split(order, int(folds))
    losses = {str(value["name"]): [] for value in candidate_list}
    dfs = {str(value["name"]): [] for value in candidate_list}
    for valid in partitions:
        train = np.setdiff1d(order, valid, assume_unique=True)
        spectra = fit_resolution_spectra(
            values[train],
            budgets=budget_list,
            external_zero=external_zero,
            noise_shrinkage=noise_shrinkage,
        )
        for candidate in candidate_list:
            fold_losses: list[float] = []
            fold_dfs: list[float] = []
            for index, budget in enumerate(budget_list):
                fitted = resolution_operator(spectra[budget], candidate)
                predictor = values[valid, :2, index].mean(axis=1)
                target = values[valid, 2:4, index].mean(axis=1)
                estimate = apply_spectrum_operator(predictor, fitted)
                denominator = max(
                    float(np.mean((target - external_zero) ** 2)),
                    1e-12,
                )
                fold_losses.append(
                    float(np.mean((estimate - target) ** 2) / denominator)
                )
                fold_dfs.append(float(fitted["effective_df"]))
            name = str(candidate["name"])
            losses[name].append(float(np.mean(fold_losses)))
            dfs[name].append(float(np.mean(fold_dfs)))
    rows: list[dict[str, Any]] = []
    lookup = {str(value["name"]): value for value in candidate_list}
    for name, vector in losses.items():
        values_loss = np.asarray(vector, dtype=float)
        rows.append({
            "name": name,
            "family": str(lookup[name]["family"]),
            "mean_loss": float(values_loss.mean()),
            "se_loss": float(
                values_loss.std(ddof=1) / np.sqrt(len(values_loss))
            ),
            "mean_effective_df": float(np.mean(dfs[name])),
        })
    table = pd.DataFrame(rows).sort_values(
        ["mean_loss", "mean_effective_df", "name"]
    ).reset_index(drop=True)
    selected = str(table.iloc[0]["name"])
    table["selected"] = table["name"] == selected
    return dict(lookup[selected]), table


def fit_joint_resolution_family(
    sessions: np.ndarray,
    *,
    budgets: Iterable[int],
    external_zero: np.ndarray,
    candidates: Iterable[dict[str, Any]],
    folds: int,
    seed: int,
    noise_shrinkage: float,
) -> tuple[dict[int, dict[str, Any]], dict[str, Any], pd.DataFrame]:
    """Select and fit one response rule for all budgets."""
    budget_list = [int(value) for value in budgets]
    selected, table = select_joint_resolution_candidate(
        sessions,
        budgets=budget_list,
        external_zero=external_zero,
        candidates=candidates,
        folds=folds,
        seed=seed,
        noise_shrinkage=noise_shrinkage,
    )
    spectra = fit_resolution_spectra(
        sessions,
        budgets=budget_list,
        external_zero=external_zero,
        noise_shrinkage=noise_shrinkage,
    )
    fitted = {
        budget: resolution_operator(spectra[budget], selected)
        for budget in budget_list
    }
    return fitted, selected, table


def history_features(
    sessions: np.ndarray,
    scores: list[np.ndarray],
    unresolved: list[np.ndarray],
    transition_index: int,
    *,
    external_zero: np.ndarray,
) -> np.ndarray:
    """Create observable history features through one budget."""
    values = np.asarray(sessions, dtype=float)
    index = int(transition_index)
    profiles = [
        values[:, :2, current].mean(axis=1) - external_zero
        for current in range(index + 1)
    ]
    dispersion = values[:, 0, index] - values[:, 1, index]
    return np.concatenate(
        [
            *profiles,
            scores[index] - external_zero,
            unresolved[index],
            dispersion,
        ],
        axis=1,
    )


def _mapped_features(
    train: np.ndarray,
    test: np.ndarray,
    *,
    family: str,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, StandardScaler, Any]:
    scaler = StandardScaler().fit(train)
    x_train = scaler.transform(train)
    x_test = scaler.transform(test)
    if family == "linear":
        return x_train, x_test, scaler, None
    if family == "quadratic_projection":
        rng = np.random.default_rng(seed)
        width = min(48, x_train.shape[1])
        projection = rng.normal(
            scale=1.0 / np.sqrt(x_train.shape[1]),
            size=(x_train.shape[1], width),
        )
        train_projection = x_train @ projection
        test_projection = x_test @ projection
        return (
            np.concatenate(
                [train_projection, train_projection**2],
                axis=1,
            ),
            np.concatenate(
                [test_projection, test_projection**2],
                axis=1,
            ),
            scaler,
            projection,
        )
    if family == "rbf_random":
        mapper = RBFSampler(
            gamma=1.0 / max(x_train.shape[1], 1),
            n_components=128,
            random_state=int(seed % (2**31 - 1)),
        )
        return (
            mapper.fit_transform(x_train),
            mapper.transform(x_test),
            scaler,
            mapper,
        )
    raise ValueError(f"unknown coherence predictor: {family}")


def fit_coherence_predictor(
    features: np.ndarray,
    updates: np.ndarray,
    *,
    seed: int,
    folds: int = 3,
    families: Iterable[str] = (
        "linear",
        "quadratic_projection",
        "rbf_random",
    ),
    alphas: Iterable[float] = (10.0,),
) -> dict[str, Any]:
    """Select a fixed predictor class inside the disjoint probe panel."""
    x = np.asarray(features, dtype=float)
    y = np.asarray(updates, dtype=float)
    candidates = [
        (family, alpha)
        for family in families
        for alpha in alphas
    ]
    if not candidates:
        raise ValueError("at least one coherence predictor is required")
    splitter = KFold(
        n_splits=folds,
        shuffle=True,
        random_state=int(seed % (2**32 - 1)),
    )
    rows: list[dict[str, Any]] = []
    for candidate_index, (family, alpha) in enumerate(candidates):
        numerator = 0.0
        denominator = 0.0
        for fold_index, (train, valid) in enumerate(splitter.split(x)):
            transformed_train, transformed_valid, _, _ = _mapped_features(
                x[train],
                x[valid],
                family=family,
                seed=seed + 101 * candidate_index,
            )
            model = Ridge(alpha=alpha).fit(transformed_train, y[train])
            prediction = model.predict(transformed_valid)
            numerator += float(np.sum((y[valid] - prediction) ** 2))
            denominator += float(np.sum(y[valid] ** 2))
        rows.append({
            "candidate_index": candidate_index,
            "family": family,
            "alpha": alpha,
            "cv_kappa": float(
                1.0 - numerator / max(denominator, 1e-12)
            ),
        })
    table = pd.DataFrame(rows).sort_values(
        ["cv_kappa", "alpha", "family"],
        ascending=[False, True, True],
    ).reset_index(drop=True)
    best = table.iloc[0]
    family = str(best["family"])
    alpha = float(best["alpha"])
    mapping_seed = seed + 101 * int(best["candidate_index"])
    transformed, _, scaler, mapper = _mapped_features(
        x,
        x,
        family=family,
        seed=mapping_seed,
    )
    model = Ridge(alpha=alpha).fit(transformed, y)
    return {
        "family": family,
        "alpha": alpha,
        "cv_kappa": float(best["cv_kappa"]),
        "scaler": scaler,
        "mapper": mapper,
        "model": model,
        "seed": int(mapping_seed),
        "table": table,
    }


def predict_coherence_update(
    fitted: dict[str, Any],
    features: np.ndarray,
) -> np.ndarray:
    """Apply a frozen probe-panel coherence predictor."""
    x = fitted["scaler"].transform(np.asarray(features, dtype=float))
    family = str(fitted["family"])
    if family == "linear":
        transformed = x
    elif family == "quadratic_projection":
        projection = np.asarray(fitted["mapper"])
        projected = x @ projection
        transformed = np.concatenate([projected, projected**2], axis=1)
    elif family == "rbf_random":
        transformed = fitted["mapper"].transform(x)
    else:
        raise ValueError(f"unknown fitted family: {family}")
    return np.asarray(fitted["model"].predict(transformed), dtype=float)


def coherence_kappa(update: np.ndarray, prediction: np.ndarray) -> float:
    """Return out-of-panel predictable update fraction against zero."""
    delta = np.asarray(update, dtype=float)
    estimate = np.asarray(prediction, dtype=float)
    return float(
        1.0
        - np.sum((delta - estimate) ** 2)
        / max(float(np.sum(delta**2)), 1e-12)
    )


def update_mean_energy_ratio(update: np.ndarray) -> float:
    """Return squared mean update relative to total update energy."""
    delta = np.asarray(update, dtype=float)
    return float(
        np.sum(delta.mean(axis=0) ** 2)
        / max(float(np.mean(np.sum(delta**2, axis=1))), 1e-12)
    )


def decompose_score_update(
    previous_profile: np.ndarray,
    next_profile: np.ndarray,
    previous_fit: dict[str, Any],
    next_fit: dict[str, Any],
) -> dict[str, Any]:
    """Separate event and operator contributions without additivity claims."""
    zero = np.asarray(previous_fit["external_zero"], dtype=float)
    if not np.allclose(zero, np.asarray(next_fit["external_zero"])):
        raise ValueError("reference origin changed inside a filtration path")
    x0 = np.asarray(previous_profile, dtype=float) - zero
    x1 = np.asarray(next_profile, dtype=float) - zero
    w0 = np.asarray(previous_fit["operator"], dtype=float)
    w1 = np.asarray(next_fit["operator"], dtype=float)
    event = (x1 - x0) @ w0.T
    operator = x1 @ (w1 - w0).T
    total = event + operator
    denominator = max(
        float(np.mean(np.sum(total**2, axis=1))),
        1e-12,
    )
    event_energy = float(np.mean(np.sum(event**2, axis=1)))
    operator_energy = float(np.mean(np.sum(operator**2, axis=1)))
    cross = float(2.0 * np.mean(np.sum(event * operator, axis=1)))
    direct = apply_spectrum_operator(
        next_profile,
        next_fit,
    ) - apply_spectrum_operator(previous_profile, previous_fit)
    return {
        "event": event,
        "operator": operator,
        "total": total,
        "event_energy_ratio": event_energy / denominator,
        "operator_energy_ratio": operator_energy / denominator,
        "cross_energy_ratio": cross / denominator,
        "reconstruction_error": float(np.max(np.abs(total - direct))),
    }


def operator_action_cosine(
    previous_fit: dict[str, Any],
    next_fit: dict[str, Any],
    covariance: np.ndarray,
) -> float:
    """Compare full operator actions, not individually named eigenvectors."""
    covariance_root, _ = _sqrt_and_inverse(
        _psd(np.asarray(covariance, dtype=float)),
        relative_floor=1e-8,
    )
    left = np.asarray(previous_fit["operator"]) @ covariance_root
    right = np.asarray(next_fit["operator"]) @ covariance_root
    return float(
        np.sum(left * right)
        / max(float(np.linalg.norm(left) * np.linalg.norm(right)), 1e-12)
    )


def oscillating_assay_scores(
    scores: list[np.ndarray],
    *,
    external_zero: np.ndarray,
    amplitude: float,
) -> list[np.ndarray]:
    """Inject a small predictable alternating operator perturbation."""
    output: list[np.ndarray] = []
    sign = np.where(
        np.arange(scores[0].shape[1]) % 2 == 0,
        1.0,
        -1.0,
    )
    for index, score in enumerate(scores):
        centered = np.asarray(score, dtype=float) - external_zero
        perturbation = (
            ((-1.0) ** index)
            * float(amplitude)
            * centered
            * sign[None]
        )
        output.append(external_zero + centered + perturbation)
    return output
