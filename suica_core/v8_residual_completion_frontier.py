"""Cross-view residual-completion frontier for SUICA V3.7H.4D-R2G.

The module asks whether a non-zero population residual floor can be explained
by a finite, out-of-sample factor model.  Four independent observations are
generated per unit: score/target observations in two super-views.  A factor
model may read only a score observation and is evaluated against its
independent target observation.  This prevents ``factor = observation`` from
manufacturing a zero residual.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np
from scipy.optimize import curve_fit
from sklearn.decomposition import PCA
from sklearn.kernel_approximation import RBFSampler
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.tree import DecisionTreeRegressor


WORLDS = (
    "pure_iid",
    "author_low_rank",
    "common_low_rank",
    "nonlinear_common",
    "irreducible_common_shock",
    "overfit_null",
)


def _sklearn_seed(seed: int) -> int:
    """Map a SeedSequence uint64 deterministically into sklearn's uint32."""
    return int(seed) % (2**32)


@dataclass(frozen=True)
class ResidualCompletionSpec:
    """Dimensions and signal convention for one R2G world."""

    dimensions: int = 32
    latent_rank: int = 4
    units_per_group: int = 128
    opportunities_per_observation: int = 4
    common_fraction: float = 0.75
    student_df: float = 5.0


@dataclass
class CompletionFamily:
    """One frozen score-to-target map with a rank-truncated output space."""

    family: str
    input_center: np.ndarray
    input_scale: np.ndarray
    target_center: np.ndarray
    ridge: Ridge | None
    output_basis: np.ndarray
    feature_map: Any | None


def _orthonormal(
    rng: np.random.Generator,
    rows: int,
    columns: int,
) -> np.ndarray:
    if columns > rows:
        raise ValueError("latent rank cannot exceed observed dimension")
    return np.linalg.qr(
        rng.normal(size=(rows, columns)),
        mode="reduced",
    )[0]


def _standard_noise(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    noise_mode: str,
    student_df: float,
) -> np.ndarray:
    if noise_mode == "gaussian":
        return rng.normal(size=shape)
    if noise_mode == "student_t5":
        if student_df <= 2.0:
            raise ValueError("student_df must exceed two")
        return (
            rng.standard_t(student_df, size=shape)
            / np.sqrt(student_df / (student_df - 2.0))
        )
    raise ValueError(f"unsupported noise mode: {noise_mode}")


def _observation_noise(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    spec: ResidualCompletionSpec,
    noise_mode: str,
    opportunities: int | None = None,
) -> np.ndarray:
    count = (
        int(spec.opportunities_per_observation)
        if opportunities is None
        else int(opportunities)
    )
    if count < 0:
        raise ValueError("opportunities cannot be negative")
    if count == 0:
        return np.zeros(shape, dtype=float)
    draws = _standard_noise(
        rng,
        (
            count,
            *shape,
        ),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    return draws.mean(axis=0)


def make_world_parameters(
    *,
    seed: int,
    spec: ResidualCompletionSpec,
    effect_share: float,
) -> dict[str, Any]:
    """Freeze loadings and signal amplitude before panel generation."""
    eta = float(effect_share)
    if not 0.0 < eta < 1.0:
        raise ValueError("effect_share must lie in (0, 1)")
    rng = np.random.default_rng(int(seed))
    target_noise_energy = 1.0 / float(
        spec.opportunities_per_observation
    )
    signal_energy = eta / (1.0 - eta) * target_noise_energy
    amplitude = np.sqrt(
        signal_energy
        * float(spec.dimensions)
        / float(spec.latent_rank)
    )
    return {
        "score_loading": _orthonormal(
            rng,
            int(spec.dimensions),
            int(spec.latent_rank),
        ),
        "target_loading": _orthonormal(
            rng,
            int(spec.dimensions),
            int(spec.latent_rank),
        ),
        "amplitude": float(amplitude),
        "effect_share": eta,
    }


def simulate_completion_panel(
    *,
    seed: int,
    world: str,
    groups: int,
    spec: ResidualCompletionSpec,
    parameters: dict[str, Any],
    noise_mode: str,
    score_opportunities: int | None = None,
    target_opportunities: int | None = None,
) -> dict[str, np.ndarray]:
    """Generate score/target A/B panels and oracle target components."""
    if world not in WORLDS:
        raise ValueError(f"unsupported R2G world: {world}")
    streams = np.random.SeedSequence(int(seed)).spawn(12)
    rngs = [np.random.default_rng(stream) for stream in streams]
    g = int(groups)
    n = int(spec.units_per_group)
    p = int(spec.dimensions)
    q = int(spec.latent_rank)
    amplitude = float(parameters["amplitude"])
    score_loading = np.asarray(
        parameters["score_loading"],
        dtype=float,
    )
    target_loading = np.asarray(
        parameters["target_loading"],
        dtype=float,
    )

    group_latent = rngs[0].normal(size=(g, q))
    author_latent = rngs[1].normal(size=(g, n, q))
    common_weight = np.sqrt(float(spec.common_fraction))
    author_weight = np.sqrt(1.0 - float(spec.common_fraction))
    score_system = np.zeros((g, n, p), dtype=float)
    target_system = np.zeros_like(score_system)
    predictable_target = np.zeros_like(score_system)

    if world == "author_low_rank":
        latent = author_latent
        score_system = amplitude * (latent @ score_loading.T)
        target_system = amplitude * (latent @ target_loading.T)
        predictable_target = target_system.copy()
    elif world == "common_low_rank":
        latent = (
            common_weight * group_latent[:, None, :]
            + author_weight * author_latent
        )
        score_system = amplitude * (latent @ score_loading.T)
        target_system = amplitude * (latent @ target_loading.T)
        predictable_target = target_system.copy()
    elif world == "nonlinear_common":
        latent = (
            common_weight * group_latent[:, None, :]
            + author_weight * author_latent
        )
        nonlinear = (latent**2 - 1.0) / np.sqrt(2.0)
        score_system = amplitude * (latent @ score_loading.T)
        target_system = amplitude * (
            nonlinear @ target_loading.T
        )
        predictable_target = target_system.copy()
    elif world == "irreducible_common_shock":
        shock = amplitude * (
            group_latent @ target_loading.T
        )
        target_system = np.repeat(shock[:, None, :], n, axis=1)
        # The shock is shared by the two target views but absent from both
        # score views.  It is systematic to an omniscient observer but not
        # admissibly predictable under the registered score-only contract.
        predictable_target = np.zeros_like(target_system)

    score_a = score_system + _observation_noise(
        rngs[2],
        score_system.shape,
        spec=spec,
        noise_mode=noise_mode,
        opportunities=score_opportunities,
    )
    target_a = target_system + _observation_noise(
        rngs[3],
        target_system.shape,
        spec=spec,
        noise_mode=noise_mode,
        opportunities=target_opportunities,
    )
    score_b = score_system + _observation_noise(
        rngs[4],
        score_system.shape,
        spec=spec,
        noise_mode=noise_mode,
        opportunities=score_opportunities,
    )
    target_b = target_system + _observation_noise(
        rngs[5],
        target_system.shape,
        spec=spec,
        noise_mode=noise_mode,
        opportunities=target_opportunities,
    )
    return {
        "score_a": score_a,
        "target_a": target_a,
        "score_b": score_b,
        "target_b": target_b,
        "predictable_target_a": predictable_target.copy(),
        "predictable_target_b": predictable_target.copy(),
        "all_systematic_target_a": target_system.copy(),
        "all_systematic_target_b": target_system.copy(),
    }


def _pooled(
    panel: dict[str, np.ndarray],
    prefix: str,
) -> np.ndarray:
    return np.concatenate(
        [
            np.asarray(panel[f"{prefix}_a"], dtype=float).reshape(
                -1,
                panel[f"{prefix}_a"].shape[-1],
            ),
            np.asarray(panel[f"{prefix}_b"], dtype=float).reshape(
                -1,
                panel[f"{prefix}_b"].shape[-1],
            ),
        ],
        axis=0,
    )


def fit_completion_family(
    panel: dict[str, np.ndarray],
    *,
    family: str,
    ridge_alpha: float,
    maximum_rank: int,
    rff_components: int,
    rff_gamma: float,
    quadratic_input_rank: int,
    seed: int,
) -> CompletionFamily:
    """Fit one bounded score-to-target family on training groups only."""
    if family not in {"linear", "quadratic", "rff"}:
        raise ValueError(f"unsupported completion family: {family}")
    score = _pooled(panel, "score")
    target = _pooled(panel, "target")
    input_center = score.mean(axis=0)
    input_scale = np.maximum(score.std(axis=0, ddof=0), 1e-8)
    target_center = target.mean(axis=0)
    standardized = (score - input_center) / input_scale
    feature_map: Any | None = None
    features = standardized
    if family == "rff":
        feature_map = RBFSampler(
            gamma=float(rff_gamma),
            n_components=int(rff_components),
            random_state=_sklearn_seed(seed),
        )
        features = feature_map.fit_transform(standardized)
    elif family == "quadratic":
        feature_map = Pipeline([
            (
                "pca",
                PCA(
                    n_components=min(
                        int(quadratic_input_rank),
                        standardized.shape[1],
                        standardized.shape[0] - 1,
                    ),
                    svd_solver="full",
                ),
            ),
            (
                "quadratic",
                PolynomialFeatures(
                    degree=2,
                    include_bias=False,
                ),
            ),
        ])
        features = feature_map.fit_transform(standardized)
    ridge = Ridge(
        alpha=float(ridge_alpha),
        fit_intercept=True,
    ).fit(features, target - target_center)
    fitted = np.asarray(ridge.predict(features), dtype=float)
    _, _, right = np.linalg.svd(
        fitted - fitted.mean(axis=0, keepdims=True),
        full_matrices=False,
    )
    rank = min(
        int(maximum_rank),
        right.shape[0],
        target.shape[1],
    )
    return CompletionFamily(
        family=family,
        input_center=input_center,
        input_scale=input_scale,
        target_center=target_center,
        ridge=ridge,
        output_basis=right[:rank].T,
        feature_map=feature_map,
    )


def predict_completion(
    model: CompletionFamily,
    score: np.ndarray,
    *,
    rank: int,
) -> np.ndarray:
    """Predict an independent target observation at a frozen output rank."""
    values = np.asarray(score, dtype=float)
    original_shape = values.shape
    flat = values.reshape(-1, original_shape[-1])
    if int(rank) == 0:
        predicted = np.repeat(
            model.target_center[None, :],
            len(flat),
            axis=0,
        )
        return predicted.reshape(original_shape)
    if int(rank) > model.output_basis.shape[1]:
        raise ValueError("requested rank exceeds the fitted output basis")
    features = (flat - model.input_center) / model.input_scale
    if model.feature_map is not None:
        features = model.feature_map.transform(features)
    raw = np.asarray(model.ridge.predict(features), dtype=float)
    basis = model.output_basis[:, : int(rank)]
    predicted = model.target_center + (raw @ basis) @ basis.T
    return predicted.reshape(original_shape)


def _group_losses(
    panel: dict[str, np.ndarray],
    prediction_a: np.ndarray,
    prediction_b: np.ndarray,
) -> np.ndarray:
    error_a = np.asarray(panel["target_a"]) - prediction_a
    error_b = np.asarray(panel["target_b"]) - prediction_b
    return 0.5 * (
        np.mean(error_a**2, axis=(1, 2))
        + np.mean(error_b**2, axis=(1, 2))
    )


def select_completion_candidate(
    panel: dict[str, np.ndarray],
    models: dict[str, CompletionFamily],
    *,
    ranks: Iterable[int],
    minimum_gain: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Use a calibration one-SE rule to select the simplest candidate."""
    candidates: list[dict[str, Any]] = []
    baseline_center = next(iter(models.values())).target_center
    baseline_a = np.broadcast_to(
        baseline_center,
        panel["target_a"].shape,
    )
    baseline_b = np.broadcast_to(
        baseline_center,
        panel["target_b"].shape,
    )
    baseline_losses = _group_losses(panel, baseline_a, baseline_b)
    candidates.append({
        "family": "none",
        "rank": 0,
        "mean_loss": float(baseline_losses.mean()),
        "se_loss": float(
            baseline_losses.std(ddof=1)
            / np.sqrt(len(baseline_losses))
        ),
        "relative_gain": 0.0,
        "complexity": 0,
    })
    for family, model in models.items():
        for rank in sorted(set(map(int, ranks))):
            if rank <= 0 or rank > model.output_basis.shape[1]:
                continue
            prediction_a = predict_completion(
                model,
                panel["score_a"],
                rank=rank,
            )
            prediction_b = predict_completion(
                model,
                panel["score_b"],
                rank=rank,
            )
            losses = _group_losses(
                panel,
                prediction_a,
                prediction_b,
            )
            candidates.append({
                "family": family,
                "rank": rank,
                "mean_loss": float(losses.mean()),
                "se_loss": float(
                    losses.std(ddof=1) / np.sqrt(len(losses))
                ),
                "relative_gain": float(
                    1.0 - losses.mean() / baseline_losses.mean()
                ),
                "complexity": int(
                    rank
                    + (50 if family == "quadratic" else 0)
                    + (100 if family == "rff" else 0)
                ),
            })
    best = min(candidates, key=lambda row: row["mean_loss"])
    if float(best["relative_gain"]) < float(minimum_gain):
        return candidates[0], candidates
    admissible = [
        row
        for row in candidates
        if row["mean_loss"]
        <= float(best["mean_loss"]) + float(best["se_loss"])
        and (
            row["rank"] == 0
            or row["relative_gain"] >= float(minimum_gain)
        )
    ]
    selected = min(
        admissible,
        key=lambda row: (
            int(row["complexity"]),
            float(row["mean_loss"]),
        ),
    )
    return selected, candidates


def cross_view_residual_phi(
    residual_a: np.ndarray,
    residual_b: np.ndarray,
) -> float:
    """Return the normalized Hilbert-Schmidt cross-view residual norm."""
    left = np.asarray(residual_a, dtype=float).reshape(
        -1,
        residual_a.shape[-1],
    )
    right = np.asarray(residual_b, dtype=float).reshape(
        -1,
        residual_b.shape[-1],
    )
    n = float(len(left))
    cross = (left.T @ right + right.T @ left) / (2.0 * n)
    self_left = left.T @ left / n
    self_right = right.T @ right / n
    denominator = np.sqrt(
        max(float(np.trace(self_left)), 1e-12)
        * max(float(np.trace(self_right)), 1e-12)
    )
    return float(np.linalg.norm(cross, ord="fro") / denominator)


def global_cross_view_r2(
    panel: dict[str, np.ndarray],
    prediction_a: np.ndarray,
    prediction_b: np.ndarray,
    *,
    target_center: np.ndarray,
) -> float:
    """Return pooled target R2 around the training-frozen target center."""
    target = np.concatenate(
        [
            panel["target_a"].reshape(-1, panel["target_a"].shape[-1]),
            panel["target_b"].reshape(-1, panel["target_b"].shape[-1]),
        ],
        axis=0,
    )
    prediction = np.concatenate(
        [
            prediction_a.reshape(-1, prediction_a.shape[-1]),
            prediction_b.reshape(-1, prediction_b.shape[-1]),
        ],
        axis=0,
    )
    denominator = float(
        np.sum((target - target_center[None, :]) ** 2)
    )
    if denominator <= 1e-12:
        return float("nan")
    return float(
        1.0 - np.sum((target - prediction) ** 2) / denominator
    )


def residual_scaling_curve(
    residual_a: np.ndarray,
    residual_b: np.ndarray,
    *,
    sizes: Iterable[int],
    seed: int,
) -> list[dict[str, float | int]]:
    """Measure self and cross-view group-mean energy across group sizes."""
    left = np.asarray(residual_a, dtype=float)
    right = np.asarray(residual_b, dtype=float)
    if left.shape != right.shape or left.ndim != 3:
        raise ValueError("residuals must share groups x units x dimensions")
    rng = np.random.default_rng(int(seed))
    permutations = np.stack(
        [rng.permutation(left.shape[1]) for _ in range(left.shape[0])],
        axis=0,
    )
    rows: list[dict[str, float | int]] = []
    for size in map(int, sizes):
        if size < 1 or size > left.shape[1]:
            raise ValueError("group size exceeds available units")
        index = permutations[:, :size]
        selected_left = np.take_along_axis(
            left,
            index[:, :, None],
            axis=1,
        )
        selected_right = np.take_along_axis(
            right,
            index[:, :, None],
            axis=1,
        )
        mean_left = selected_left.mean(axis=1)
        mean_right = selected_right.mean(axis=1)
        self_energy = float(
            0.5 * np.mean(mean_left**2 + mean_right**2)
        )
        cross_energy = float(np.mean(mean_left * mean_right))
        rows.append({
            "size": size,
            "self_energy": self_energy,
            "cross_energy": cross_energy,
        })
    return rows


def fit_scaling_models(
    curve_rows: list[dict[str, float | int]],
    *,
    energy_key: str,
) -> dict[str, Any]:
    """Fit a/n, b+a/n, and b+a*n^-alpha scaling models."""
    sizes = np.asarray(
        [row["size"] for row in curve_rows],
        dtype=float,
    )
    energy = np.asarray(
        [row[energy_key] for row in curve_rows],
        dtype=float,
    )

    def score(prediction: np.ndarray, parameters: int) -> dict[str, float]:
        residual = energy - prediction
        rss = max(float(np.sum(residual**2)), 1e-20)
        count = len(energy)
        aic = count * np.log(rss / count) + 2.0 * parameters
        if count > parameters + 1:
            aic += (
                2.0 * parameters * (parameters + 1)
                / (count - parameters - 1)
            )
        return {
            "rmse": float(np.sqrt(rss / count)),
            "aicc": float(aic),
        }

    inverse = 1.0 / sizes
    amplitude_zero = float(
        np.dot(inverse, energy) / max(np.dot(inverse, inverse), 1e-12)
    )
    prediction_zero = amplitude_zero * inverse
    zero_stats = score(prediction_zero, 1)

    design = np.column_stack([np.ones_like(sizes), inverse])
    floor_linear, amplitude_linear = np.linalg.lstsq(
        design,
        energy,
        rcond=None,
    )[0]
    prediction_linear = floor_linear + amplitude_linear * inverse
    linear_stats = score(prediction_linear, 2)

    def power_curve(
        size: np.ndarray,
        floor: float,
        amplitude: float,
        alpha: float,
    ) -> np.ndarray:
        return floor + amplitude * size ** (-alpha)

    try:
        parameter, _ = curve_fit(
            power_curve,
            sizes,
            energy,
            p0=(
                max(0.0, float(floor_linear)),
                max(1e-8, float(amplitude_linear)),
                1.0,
            ),
            bounds=([-np.inf, -np.inf, 0.25], [np.inf, np.inf, 1.25]),
            maxfev=20_000,
        )
        prediction_power = power_curve(sizes, *parameter)
        power_stats = score(prediction_power, 3)
        power = {
            "floor": float(parameter[0]),
            "amplitude": float(parameter[1]),
            "alpha": float(parameter[2]),
            **power_stats,
        }
    except (RuntimeError, ValueError):
        power = {
            "floor": float("nan"),
            "amplitude": float("nan"),
            "alpha": float("nan"),
            "rmse": float("nan"),
            "aicc": float("inf"),
        }
    models = {
        "a_over_n": {
            "floor": 0.0,
            "amplitude": amplitude_zero,
            "alpha": 1.0,
            **zero_stats,
        },
        "floor_plus_a_over_n": {
            "floor": float(floor_linear),
            "amplitude": float(amplitude_linear),
            "alpha": 1.0,
            **linear_stats,
        },
        "floor_plus_power": power,
    }
    selected = min(models, key=lambda name: models[name]["aicc"])
    return {
        "selected_model": selected,
        "models": models,
    }


def evaluate_residual_arm(
    residual_a: np.ndarray,
    residual_b: np.ndarray,
    *,
    sizes: Iterable[int],
    seed: int,
) -> dict[str, Any]:
    """Evaluate cross-view structure and population residual limits."""
    left = np.asarray(residual_a, dtype=float)
    right = np.asarray(residual_b, dtype=float)
    unit_energy = float(0.5 * np.mean(left**2 + right**2))
    curve = residual_scaling_curve(
        left,
        right,
        sizes=sizes,
        seed=seed,
    )
    self_fit = fit_scaling_models(curve, energy_key="self_energy")
    cross_fit = fit_scaling_models(curve, energy_key="cross_energy")
    self_floor = float(
        self_fit["models"]["floor_plus_a_over_n"]["floor"]
    )
    cross_floor = float(
        cross_fit["models"]["floor_plus_a_over_n"]["floor"]
    )
    return {
        "phi_cross_view": cross_view_residual_phi(left, right),
        "unit_energy": unit_energy,
        "self_floor": self_floor,
        "cross_floor": cross_floor,
        "self_floor_ratio": float(self_floor / max(unit_energy, 1e-12)),
        "cross_floor_ratio": float(
            cross_floor / max(unit_energy, 1e-12)
        ),
        "self_selected_model": self_fit["selected_model"],
        "cross_selected_model": cross_fit["selected_model"],
        "self_power_alpha": float(
            self_fit["models"]["floor_plus_power"]["alpha"]
        ),
        "cross_power_alpha": float(
            cross_fit["models"]["floor_plus_power"]["alpha"]
        ),
        "curve": curve,
    }


def overfit_trap_metrics(
    training: dict[str, np.ndarray],
    confirmation: dict[str, np.ndarray],
    *,
    seed: int,
) -> dict[str, float]:
    """Show that an unrestricted memorizer creates only an in-sample zero."""
    train_score = _pooled(training, "score")
    train_target = _pooled(training, "target")
    confirm_score = _pooled(confirmation, "score")
    confirm_target = _pooled(confirmation, "target")
    model = DecisionTreeRegressor(
        random_state=_sklearn_seed(seed),
        min_samples_leaf=1,
    ).fit(train_score, train_target)
    train_prediction = model.predict(train_score)
    confirm_prediction = model.predict(confirm_score)

    def r2(target: np.ndarray, prediction: np.ndarray) -> float:
        denominator = float(
            np.sum((target - train_target.mean(axis=0)) ** 2)
        )
        return float(
            1.0 - np.sum((target - prediction) ** 2)
            / max(denominator, 1e-12)
        )

    return {
        "training_r2": r2(train_target, train_prediction),
        "confirmation_r2": r2(confirm_target, confirm_prediction),
        "training_residual_energy": float(
            np.mean((train_target - train_prediction) ** 2)
        ),
        "confirmation_residual_energy": float(
            np.mean((confirm_target - confirm_prediction) ** 2)
        ),
    }
