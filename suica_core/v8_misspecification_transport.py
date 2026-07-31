"""Misspecification and held-out-condition transport tests for V3.7H.4."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .v8_multiscale_zero_identification import (
    decompose_balanced_panel,
)


@dataclass(frozen=True)
class MisspecificationSpec:
    """Dimensions for one four-panel misspecification world."""

    societies: int = 8
    groups_per_society: int = 4
    authors_per_group: int = 8
    conditions: int = 16
    train_conditions: int = 8
    calibration_conditions: int = 4
    test_conditions: int = 4
    panels: int = 4
    opportunities: int = 8
    technical_streams: int = 2
    dimensions: int = 6
    latent_dimensions: int = 3
    latent_subgroups: int = 4
    student_df: float = 5.0
    heteroskedastic_strength: float = 0.35

    @property
    def authors(self) -> int:
        return (
            self.societies
            * self.groups_per_society
            * self.authors_per_group
        )

    @property
    def condition_split(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        train = np.arange(self.train_conditions)
        calibration = np.arange(
            self.train_conditions,
            self.train_conditions + self.calibration_conditions,
        )
        test = np.arange(
            self.train_conditions + self.calibration_conditions,
            self.conditions,
        )
        if len(test) != self.test_conditions:
            raise ValueError("condition counts do not sum to conditions")
        return train, calibration, test


def _draw_standardized(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    noise_mode: str,
    student_df: float,
) -> np.ndarray:
    if noise_mode == "gaussian":
        return rng.normal(size=shape)
    if noise_mode == "heteroskedastic_t5":
        if student_df <= 2.0:
            raise ValueError("student_df must exceed two")
        return (
            rng.standard_t(student_df, size=shape)
            / np.sqrt(student_df / (student_df - 2.0))
        )
    raise ValueError(f"unsupported noise mode: {noise_mode}")


def _unit_rms(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    rms = float(np.sqrt(np.mean(array**2)))
    if rms <= 1e-12:
        raise ValueError("cannot normalize zero energy")
    return array / rms


def _unit_rms_per_dimension(values: np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    axes = tuple(range(array.ndim - 1))
    rms = np.sqrt(np.mean(array**2, axis=axes, keepdims=True))
    if np.any(rms <= 1e-12):
        raise ValueError("cannot normalize a zero-energy dimension")
    return array / rms


def _double_center(values: np.ndarray) -> np.ndarray:
    """Double-center authors x conditions x dimensions."""
    array = np.asarray(values, dtype=float)
    return (
        array
        - array.mean(axis=1, keepdims=True)
        - array.mean(axis=0, keepdims=True)
        + array.mean(axis=(0, 1), keepdims=True)
    )


def _author_metadata(
    spec: MisspecificationSpec,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    society = np.repeat(
        np.arange(spec.societies),
        spec.groups_per_society * spec.authors_per_group,
    )
    group_local = np.tile(
        np.repeat(
            np.arange(spec.groups_per_society),
            spec.authors_per_group,
        ),
        spec.societies,
    )
    group_global = (
        society * spec.groups_per_society + group_local
    )
    return society, group_local, group_global


def _balanced_main_components(
    rng: np.random.Generator,
    spec: MisspecificationSpec,
    *,
    amplitude: float,
) -> dict[str, np.ndarray]:
    s = spec.societies
    g = spec.groups_per_society
    u = spec.authors_per_group
    c = spec.conditions
    d = spec.dimensions
    social = rng.normal(size=(s, d))
    social -= social.mean(axis=0, keepdims=True)
    social = float(amplitude) * _unit_rms(social)
    group = rng.normal(size=(s, g, d))
    group -= group.mean(axis=1, keepdims=True)
    group = float(amplitude) * _unit_rms(group)
    author = rng.normal(size=(s, g, u, d))
    author -= author.mean(axis=2, keepdims=True)
    author = float(amplitude) * _unit_rms(author)
    condition = rng.normal(size=(c, d))
    condition -= condition.mean(axis=0, keepdims=True)
    condition = float(amplitude) * _unit_rms(condition)
    return {
        "social": social,
        "group": group,
        "author": author,
        "condition": condition,
    }


def _main_surface(
    components: dict[str, np.ndarray],
) -> np.ndarray:
    social = np.asarray(components["social"])
    group = np.asarray(components["group"])
    author = np.asarray(components["author"])
    condition = np.asarray(components["condition"])
    return (
        social[:, None, None, None, :]
        + group[:, :, None, None, :]
        + author[:, :, :, None, :]
        + condition[None, None, None, :, :]
    )


def _nonlinear_interaction(
    rng: np.random.Generator,
    spec: MisspecificationSpec,
    *,
    saturation: float,
) -> np.ndarray:
    q = spec.latent_dimensions
    d = spec.dimensions
    author_latent = rng.normal(size=(spec.authors, q))
    condition_latent = rng.normal(size=(spec.conditions, q))
    orthogonal, _ = np.linalg.qr(rng.normal(size=(q * q, d)))
    mappings = orthogonal[:, :d].T.reshape(d, q, q)
    bilinear = np.einsum(
        "ui,dij,cj->ucd",
        author_latent,
        mappings,
        condition_latent,
    )
    scale = np.maximum(
        bilinear.std(axis=(0, 1), ddof=1, keepdims=True),
        1e-12,
    )
    response = np.tanh(float(saturation) * bilinear / scale)
    return _unit_rms_per_dimension(_double_center(response))


def _latent_hierarchy_interaction(
    rng: np.random.Generator,
    spec: MisspecificationSpec,
) -> tuple[np.ndarray, np.ndarray]:
    _, _, registered_group = _author_metadata(spec)
    labels = np.empty(spec.authors, dtype=int)
    for group in np.unique(registered_group):
        members = np.flatnonzero(registered_group == group)
        block = np.resize(
            np.arange(spec.latent_subgroups),
            len(members),
        )
        rng.shuffle(block)
        labels[members] = block
    rank = 2
    condition_seed = rng.normal(size=(spec.conditions, rank))
    condition_seed -= condition_seed.mean(axis=0, keepdims=True)
    condition_basis, _ = np.linalg.qr(condition_seed)
    loading = rng.normal(
        size=(spec.latent_subgroups, rank, spec.dimensions)
    )
    loading -= loading.mean(axis=0, keepdims=True)
    response = np.einsum(
        "cr,qrd->qcd",
        condition_basis[:, :rank],
        loading,
    )[labels]
    response = _unit_rms_per_dimension(_double_center(response))
    return response, labels


def _nonergodic_interaction(
    rng: np.random.Generator,
    spec: MisspecificationSpec,
    author_component: np.ndarray,
    *,
    author_correlation: float,
    stable_fraction: float,
    regime_persistence: float,
) -> tuple[np.ndarray, np.ndarray]:
    author_anchor = np.asarray(author_component)[..., 0].reshape(-1)
    author_anchor = (
        author_anchor - author_anchor.mean()
    ) / max(float(author_anchor.std(ddof=1)), 1e-12)
    rho = float(author_correlation)
    permanent = (
        rho * author_anchor
        + np.sqrt(max(1.0 - rho**2, 0.0))
        * rng.normal(size=spec.authors)
    )
    regimes = np.empty((spec.panels, spec.authors), dtype=float)
    regimes[0] = rng.choice([-1.0, 1.0], size=spec.authors)
    for panel in range(1, spec.panels):
        retain = rng.uniform(size=spec.authors) < float(
            regime_persistence
        )
        replacement = rng.choice([-1.0, 1.0], size=spec.authors)
        regimes[panel] = np.where(
            retain,
            regimes[panel - 1],
            replacement,
        )
    condition_pattern = rng.normal(
        size=(spec.conditions, spec.dimensions)
    )
    condition_pattern -= condition_pattern.mean(
        axis=0,
        keepdims=True,
    )
    condition_pattern = _unit_rms_per_dimension(condition_pattern)
    coefficient = (
        np.sqrt(float(stable_fraction)) * permanent[None, :]
        + np.sqrt(1.0 - float(stable_fraction)) * regimes
    )
    response = (
        coefficient[:, :, None, None]
        * condition_pattern[None, None, :, :]
    )
    centered = np.stack([
        _double_center(response[panel])
        for panel in range(spec.panels)
    ])
    return _unit_rms(centered), regimes


def simulate_misspecification_world(
    *,
    seed: int,
    world: str,
    effect_share: float,
    noise_mode: str,
    spec: MisspecificationSpec,
    main_effect_amplitude: float,
    opportunity_amplitude: float,
    technical_amplitude: float,
    nonlinear_saturation: float,
    nonergodic_author_correlation: float,
    nonergodic_stable_fraction: float,
    nonergodic_regime_persistence: float,
) -> dict[str, Any]:
    """Generate one four-panel misspecification world."""
    if world not in {
        "additive",
        "nonlinear",
        "nonergodic",
        "latent_hierarchy",
    }:
        raise ValueError(f"unsupported world: {world}")
    streams = np.random.SeedSequence(int(seed)).spawn(7)
    rngs = [np.random.default_rng(stream) for stream in streams]
    components = _balanced_main_components(
        rngs[0],
        spec,
        amplitude=float(main_effect_amplitude),
    )
    main = _main_surface(components)
    base_energy = float(np.mean(main**2))
    gamma = (
        np.sqrt(
            float(effect_share)
            * base_energy
            / max(1.0 - float(effect_share), 1e-12)
        )
        if float(effect_share) > 0.0
        else 0.0
    )

    q = np.zeros(
        (spec.authors, spec.conditions, spec.dimensions),
        dtype=float,
    )
    persistent = np.zeros(
        (
            spec.panels,
            spec.authors,
            spec.conditions,
            spec.dimensions,
        ),
        dtype=float,
    )
    latent_labels = np.full(spec.authors, -1, dtype=int)
    regimes = np.zeros((spec.panels, spec.authors), dtype=float)
    if world == "nonlinear":
        q = gamma * _nonlinear_interaction(
            rngs[1],
            spec,
            saturation=float(nonlinear_saturation),
        )
    elif world == "latent_hierarchy":
        raw, latent_labels = _latent_hierarchy_interaction(
            rngs[1],
            spec,
        )
        q = gamma * raw
    elif world == "nonergodic":
        raw, regimes = _nonergodic_interaction(
            rngs[1],
            spec,
            components["author"],
            author_correlation=float(nonergodic_author_correlation),
            stable_fraction=float(nonergodic_stable_fraction),
            regime_persistence=float(nonergodic_regime_persistence),
        )
        persistent = gamma * raw

    p = spec.panels
    s = spec.societies
    g = spec.groups_per_society
    u = spec.authors_per_group
    c = spec.conditions
    k = spec.opportunities
    r = spec.technical_streams
    d = spec.dimensions
    opportunity = _draw_standardized(
        rngs[2],
        (p, s, g, u, c, k, d),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    technical = _draw_standardized(
        rngs[3],
        (p, s, g, u, c, k, r, d),
        noise_mode=noise_mode,
        student_df=float(spec.student_df),
    )
    if noise_mode == "heteroskedastic_t5":
        anchor = np.asarray(components["author"])[..., 0]
        scale = np.exp(
            float(spec.heteroskedastic_strength)
            * anchor
            / max(float(anchor.std(ddof=1)), 1e-12)
        )
        scale = np.clip(scale, 0.45, 2.20)
        opportunity *= scale[
            None, :, :, :, None, None, None
        ]
        technical *= scale[
            None, :, :, :, None, None, None, None
        ]
    opportunity /= np.sqrt(
        max(
            float(np.var(opportunity, axis=5, ddof=1).mean()),
            1e-12,
        )
    )
    technical /= np.sqrt(
        max(
            float(np.var(technical, axis=6, ddof=1).mean()),
            1e-12,
        )
    )

    q_nested = q.reshape(s, g, u, c, d)
    persistent_nested = persistent.reshape(p, s, g, u, c, d)
    observations = (
        main[None, :, :, :, :, None, None, :]
        + q_nested[
            None, :, :, :, :, None, None, :
        ]
        + persistent_nested[
            :, :, :, :, :, None, None, :
        ]
        + float(opportunity_amplitude)
        * opportunity[:, :, :, :, :, :, None, :]
        + float(technical_amplitude) * technical
    )
    stable_truth = main.reshape(spec.authors, c, d) + q
    oracle_panel_truth = (
        stable_truth[None, :, :, :]
        + persistent
    )
    alias_identity_error = 0.0
    if world == "nonergodic":
        response_label = stable_truth[None] + persistent
        opportunity_label = stable_truth[None] + persistent
        alias_identity_error = float(np.max(np.abs(
            response_label - opportunity_label
        )))
    return {
        "observations": observations,
        "main_components": components,
        "stable_truth": stable_truth,
        "oracle_panel_truth": oracle_panel_truth,
        "interaction_truth": q,
        "persistent_truth": persistent,
        "latent_labels": latent_labels,
        "regimes": regimes,
        "effect_scale": float(gamma),
        "base_stable_energy": base_energy,
        "achieved_interaction_energy": float(
            np.mean(q**2)
            if world != "nonergodic"
            else np.mean(persistent**2)
        ),
        "alias_identity_error": alias_identity_error,
        "society_labels": _author_metadata(spec)[0],
        "registered_group_labels": _author_metadata(spec)[2],
    }


def cell_means(
    observations: np.ndarray,
    *,
    opportunities: int,
) -> np.ndarray:
    """Collapse nested observations to panels x authors x conditions x dims."""
    values = np.asarray(observations, dtype=float)
    if not 1 <= int(opportunities) <= values.shape[5]:
        raise ValueError("invalid opportunity prefix")
    selected = values[:, :, :, :, :, :int(opportunities)]
    collapsed = selected.mean(axis=(5, 6))
    return collapsed.reshape(
        collapsed.shape[0],
        -1,
        collapsed.shape[-2],
        collapsed.shape[-1],
    )


def author_crossfit_masks(
    registered_group_labels: np.ndarray,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Return two anchor/target folds balanced inside registered groups."""
    labels = np.asarray(registered_group_labels)
    fold = np.zeros(len(labels), dtype=bool)
    for group in np.unique(labels):
        members = np.flatnonzero(labels == group)
        fold[members[::2]] = True
    return [(~fold, fold), (fold, ~fold)]


def _condition_profile(
    anchor_source: np.ndarray,
    fit_conditions: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    baseline = anchor_source[:, fit_conditions].mean(
        axis=1,
        keepdims=True,
    )
    profile = (anchor_source - baseline).mean(
        axis=0,
        keepdims=True,
    )
    residual = anchor_source - baseline - profile
    return profile, residual


def crossfit_additive_prediction(
    source_cell: np.ndarray,
    target_cell: np.ndarray,
    *,
    registered_group_labels: np.ndarray,
    fit_conditions: np.ndarray,
    eval_conditions: np.ndarray,
) -> np.ndarray:
    """Predict target authors in held-out conditions using anchor profiles."""
    prediction = np.empty(
        (
            len(target_cell),
            len(eval_conditions),
            target_cell.shape[-1],
        ),
        dtype=float,
    )
    for anchor_mask, target_mask in author_crossfit_masks(
        registered_group_labels
    ):
        profile, _ = _condition_profile(
            source_cell[anchor_mask],
            fit_conditions,
        )
        target_baseline = target_cell[
            target_mask
        ][:, fit_conditions].mean(axis=1, keepdims=True)
        prediction[target_mask] = (
            target_baseline
            + profile[:, eval_conditions]
        )
    return prediction


def _structured_fold_prediction(
    anchor_source: np.ndarray,
    target_cell: np.ndarray,
    *,
    fit_conditions: np.ndarray,
    eval_conditions: np.ndarray,
    rank: int,
) -> np.ndarray:
    profile, anchor_residual = _condition_profile(
        anchor_source,
        fit_conditions,
    )
    matrix = anchor_residual.reshape(len(anchor_residual), -1)
    _, _, right = np.linalg.svd(matrix, full_matrices=False)
    selected = right[:int(rank)]
    d = anchor_source.shape[-1]
    fit_columns = np.concatenate([
        np.arange(condition * d, (condition + 1) * d)
        for condition in fit_conditions
    ])
    eval_columns = np.concatenate([
        np.arange(condition * d, (condition + 1) * d)
        for condition in eval_conditions
    ])
    target_baseline = target_cell[:, fit_conditions].mean(
        axis=1,
        keepdims=True,
    )
    target_residual = (
        target_cell[:, fit_conditions]
        - target_baseline
        - profile[:, fit_conditions]
    ).reshape(len(target_cell), -1)
    design = selected[:, fit_columns].T
    score = np.linalg.lstsq(
        design,
        target_residual.T,
        rcond=None,
    )[0].T
    predicted_residual = (
        score @ selected[:, eval_columns]
    ).reshape(len(target_cell), len(eval_conditions), d)
    return (
        target_baseline
        + profile[:, eval_conditions]
        + predicted_residual
    )


def crossfit_structured_prediction(
    source_cell: np.ndarray,
    target_cell: np.ndarray,
    *,
    registered_group_labels: np.ndarray,
    fit_conditions: np.ndarray,
    eval_conditions: np.ndarray,
    rank: int,
) -> np.ndarray:
    """Predict held-out conditions from anchor-derived low-rank structure."""
    prediction = np.empty(
        (
            len(target_cell),
            len(eval_conditions),
            target_cell.shape[-1],
        ),
        dtype=float,
    )
    for anchor_mask, target_mask in author_crossfit_masks(
        registered_group_labels
    ):
        prediction[target_mask] = _structured_fold_prediction(
            source_cell[anchor_mask],
            target_cell[target_mask],
            fit_conditions=fit_conditions,
            eval_conditions=eval_conditions,
            rank=int(rank),
        )
    return prediction


def select_structured_rank(
    source_cell: np.ndarray,
    target_cell: np.ndarray,
    *,
    registered_group_labels: np.ndarray,
    train_conditions: np.ndarray,
    calibration_conditions: np.ndarray,
    rank_candidates: tuple[int, ...],
) -> tuple[int, dict[int, float]]:
    """Select response rank on calibration conditions only."""
    truth = target_cell[:, calibration_conditions]
    losses: dict[int, float] = {}
    for rank in rank_candidates:
        prediction = crossfit_structured_prediction(
            source_cell,
            target_cell,
            registered_group_labels=registered_group_labels,
            fit_conditions=train_conditions,
            eval_conditions=calibration_conditions,
            rank=int(rank),
        )
        losses[int(rank)] = float(np.mean((truth - prediction) ** 2))
    selected = min(losses, key=lambda rank: (losses[rank], rank))
    return int(selected), losses


def crossfit_residual(
    source_cell: np.ndarray,
    target_cell: np.ndarray,
    *,
    registered_group_labels: np.ndarray,
    fit_conditions: np.ndarray,
    eval_conditions: np.ndarray,
) -> np.ndarray:
    prediction = crossfit_additive_prediction(
        source_cell,
        target_cell,
        registered_group_labels=registered_group_labels,
        fit_conditions=fit_conditions,
        eval_conditions=eval_conditions,
    )
    return target_cell[:, eval_conditions] - prediction


def residual_correlation(
    left: np.ndarray,
    right: np.ndarray,
) -> float:
    a = np.asarray(left, dtype=float)
    b = np.asarray(right, dtype=float)
    denominator = float(
        np.linalg.norm(a) * np.linalg.norm(b)
    )
    return float(np.sum(a * b) / max(denominator, 1e-12))


def _within_group_permutation(
    rng: np.random.Generator,
    labels: np.ndarray,
) -> np.ndarray:
    permutation = np.arange(len(labels))
    for group in np.unique(labels):
        members = np.flatnonzero(labels == group)
        permutation[members] = rng.permutation(members)
    return permutation


def crc_permutation_p(
    left: np.ndarray,
    right: np.ndarray,
    labels: np.ndarray,
    *,
    seed: int,
    permutations: int,
) -> tuple[float, float]:
    """One-sided author-block permutation p-value for residual replication."""
    observed = residual_correlation(left, right)
    rng = np.random.default_rng(int(seed))
    null = np.empty(int(permutations), dtype=float)
    for draw in range(int(permutations)):
        permuted = _within_group_permutation(rng, labels)
        null[draw] = residual_correlation(left, right[permuted])
    p_value = float(
        (1 + np.sum(null >= observed)) / (len(null) + 1)
    )
    return observed, p_value


def low_rank_ratio(residual: np.ndarray, *, rank: int) -> float:
    matrix = np.asarray(residual, dtype=float).reshape(len(residual), -1)
    singular = np.linalg.svd(
        matrix,
        full_matrices=False,
        compute_uv=False,
    )
    energy = singular**2
    return float(
        energy[:int(rank)].sum() / max(float(energy.sum()), 1e-12)
    )


def low_rank_permutation_p(
    residual: np.ndarray,
    *,
    rank: int,
    seed: int,
    permutations: int,
) -> tuple[float, float]:
    """Condition-block permutation p-value for residual concentration."""
    values = np.asarray(residual, dtype=float)
    observed = low_rank_ratio(values, rank=int(rank))
    rng = np.random.default_rng(int(seed))
    null = np.empty(int(permutations), dtype=float)
    for draw in range(int(permutations)):
        permuted = np.empty_like(values)
        for author in range(len(values)):
            order = rng.permutation(values.shape[1])
            permuted[author] = values[author, order]
        null[draw] = low_rank_ratio(permuted, rank=int(rank))
    p_value = float(
        (1 + np.sum(null >= observed)) / (len(null) + 1)
    )
    return observed, p_value


def gain_signflip_p(
    gain_by_author: np.ndarray,
    *,
    seed: int,
    permutations: int,
) -> tuple[float, float]:
    """One-sided sign-flip p-value for held-out structured gain."""
    gain = np.asarray(gain_by_author, dtype=float)
    observed = float(gain.mean())
    rng = np.random.default_rng(int(seed))
    null = np.empty(int(permutations), dtype=float)
    for draw in range(int(permutations)):
        signs = rng.choice([-1.0, 1.0], size=len(gain))
        null[draw] = float(np.mean(signs * gain))
    p_value = float(
        (1 + np.sum(null >= observed)) / (len(null) + 1)
    )
    return observed, p_value


def holm_adjust(p_values: dict[str, float]) -> dict[str, float]:
    """Return Holm familywise adjusted p-values."""
    names = list(p_values)
    raw = np.asarray([float(p_values[name]) for name in names])
    order = np.argsort(raw)
    adjusted_sorted = np.empty(len(raw), dtype=float)
    running = 0.0
    for position, index in enumerate(order):
        value = min(
            1.0,
            (len(raw) - position) * raw[index],
        )
        running = max(running, value)
        adjusted_sorted[position] = running
    adjusted = np.empty(len(raw), dtype=float)
    for position, index in enumerate(order):
        adjusted[index] = adjusted_sorted[position]
    return {
        name: float(adjusted[index])
        for index, name in enumerate(names)
    }


def operation_gap(
    observations: np.ndarray,
    *,
    opportunities: int,
) -> float:
    """Compare opportunity-first and pooling-first linear projections."""
    values = np.asarray(observations, dtype=float)[:2, ..., :opportunities, :, :]
    pooled = decompose_balanced_panel(values)
    per_opportunity = [
        decompose_balanced_panel(
            values[..., index:index + 1, :, :]
        )
        for index in range(int(opportunities))
    ]
    denominator = max(
        float(np.sqrt(np.mean(pooled["cell_mean"] ** 2))),
        1e-12,
    )
    maximum = 0.0
    for component in ("social", "group", "author", "condition", "response"):
        first = np.mean(
            [np.asarray(item[component]) for item in per_opportunity],
            axis=0,
        )
        gap = float(
            np.sqrt(np.mean((first - pooled[component]) ** 2))
            / denominator
        )
        maximum = max(maximum, gap)
    return maximum


def _r2(truth: np.ndarray, estimate: np.ndarray) -> float:
    target = np.asarray(truth, dtype=float).ravel()
    predicted = np.asarray(estimate, dtype=float).ravel()
    denominator = float(np.sum((target - target.mean()) ** 2))
    return float(
        1.0 - np.sum((target - predicted) ** 2)
        / max(denominator, 1e-12)
    )


def _correlation(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=float).ravel()
    b = np.asarray(right, dtype=float).ravel()
    if a.std(ddof=1) <= 1e-12 or b.std(ddof=1) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def main_component_recovery(
    observations: np.ndarray,
    components: dict[str, np.ndarray],
    *,
    opportunities: int,
) -> list[dict[str, float | str]]:
    """Recover registered main components from two independent panels."""
    values = np.asarray(observations, dtype=float)[
        :2, ..., :int(opportunities), :, :
    ]
    fitted = decompose_balanced_panel(values)
    rows: list[dict[str, float | str]] = []
    for component in ("social", "group", "author", "condition"):
        estimate = np.asarray(fitted[component])
        truth = np.asarray(components[component])
        rows.append({
            "component": component,
            "recovery_r2": _r2(truth, estimate.mean(axis=0)),
            "split_panel_correlation": _correlation(
                estimate[0],
                estimate[1],
            ),
        })
    return rows

