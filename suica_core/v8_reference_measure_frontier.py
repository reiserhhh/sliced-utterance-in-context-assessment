"""Reference-measure transport and residual-shape primitives for V3.7H.4D."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.stats import norm

from suica_core.v8_misspecification_transport import (
    crc_permutation_p,
    holm_adjust,
    low_rank_permutation_p,
    residual_correlation,
)


@dataclass(frozen=True)
class ReferenceFrontierSpec:
    """Frozen balanced hierarchy and author split."""

    societies: int = 8
    groups_per_society: int = 4
    authors_per_group: int = 8
    conditions: int = 16
    dimensions: int = 6
    panels: int = 4

    @property
    def groups(self) -> int:
        return self.societies * self.groups_per_society

    @property
    def authors(self) -> int:
        return self.groups * self.authors_per_group

    @property
    def author_labels(self) -> tuple[np.ndarray, np.ndarray]:
        groups = np.repeat(
            np.arange(self.groups),
            self.authors_per_group,
        )
        societies = groups // self.groups_per_society
        return societies, groups

    @property
    def author_split(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        train: list[int] = []
        calibration: list[int] = []
        test: list[int] = []
        for group in range(self.groups):
            start = group * self.authors_per_group
            train.extend(range(start, start + 4))
            calibration.extend(range(start + 4, start + 6))
            test.extend(range(start + 6, start + 8))
        return (
            np.asarray(train, dtype=int),
            np.asarray(calibration, dtype=int),
            np.asarray(test, dtype=int),
        )


def softmax(values: np.ndarray, *, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax."""
    shifted = values - np.max(values, axis=axis, keepdims=True)
    exponential = np.exp(shifted)
    return exponential / exponential.sum(axis=axis, keepdims=True)


def jensen_shannon(left: np.ndarray, right: np.ndarray) -> float:
    """Natural-log Jensen-Shannon divergence."""
    p = np.asarray(left, dtype=float)
    q = np.asarray(right, dtype=float)
    midpoint = 0.5 * (p + q)

    def _kl(source: np.ndarray) -> float:
        mask = source > 0
        return float(
            np.sum(source[mask] * np.log(source[mask] / midpoint[mask]))
        )

    return 0.5 * (_kl(p) + _kl(q))


def reference_pair(
    conditions: int,
    target_jsd: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Construct a symmetric full-support reference pair at target JSD."""
    reference = np.full(int(conditions), 1.0 / int(conditions))
    if target_jsd <= 0:
        return reference.copy(), reference.copy(), 0.0
    direction = np.linspace(-1.0, 1.0, int(conditions))
    direction -= direction.mean()
    low, high = 0.0, 20.0
    for _ in range(80):
        middle = 0.5 * (low + high)
        left = softmax(-middle * direction)
        right = softmax(middle * direction)
        if jensen_shannon(left, right) < target_jsd:
            low = middle
        else:
            high = middle
    scale = 0.5 * (low + high)
    left = softmax(-scale * direction)
    right = softmax(scale * direction)
    return left, right, jensen_shannon(left, right)


def effective_rank(values: np.ndarray) -> float:
    """Entropy-free participation-ratio effective rank."""
    matrix = np.asarray(values, dtype=float).reshape(len(values), -1)
    singular = np.linalg.svd(
        matrix,
        full_matrices=False,
        compute_uv=False,
    )
    return float(
        singular.sum() ** 2
        / max(float(np.sum(singular**2)), 1e-12)
    )


def reference_score(
    cell_truth: np.ndarray,
    reference: np.ndarray,
) -> np.ndarray:
    """Return author score under a fixed condition reference."""
    values = np.asarray(cell_truth, dtype=float)
    centered = values - values.mean(axis=0, keepdims=True)
    return np.einsum(
        "c,ucd->ud",
        np.asarray(reference, dtype=float),
        centered,
    )


def _normalize_energy(
    values: np.ndarray,
    target_energy: float,
) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    energy = float(np.mean(result**2))
    if energy <= 1e-12 or target_energy <= 0:
        return np.zeros_like(result)
    return result * np.sqrt(float(target_energy) / energy)


def _double_center(values: np.ndarray) -> np.ndarray:
    result = np.asarray(values, dtype=float)
    return (
        result
        - result.mean(axis=0, keepdims=True)
        - result.mean(axis=1, keepdims=True)
        + result.mean(axis=(0, 1), keepdims=True)
    )


def _interaction(
    rng: np.random.Generator,
    *,
    world: str,
    effect_share: float,
    near_kernel_fraction: float,
    minority_author_fraction: float,
    minority_condition_fraction: float,
    spec: ReferenceFrontierSpec,
    base_energy: float,
    contrast_direction: np.ndarray | None = None,
) -> tuple[np.ndarray, dict[str, float]]:
    n, c, d = spec.authors, spec.conditions, spec.dimensions
    if world == "additive":
        return np.zeros((n, c, d)), {
            "effective_rank": 0.0,
            "score_fraction": 0.0,
        }
    target = (
        float(effect_share)
        / max(1.0 - float(effect_share), 1e-12)
        * float(base_energy)
    )
    direction = rng.normal(size=d)
    direction /= max(float(np.linalg.norm(direction)), 1e-12)

    if world in {
        "noncentered",
        "reference_shift",
        "support_violation",
        "aq_alias",
    }:
        author = rng.normal(size=n)
        author -= author.mean()
        condition = 1.0 + 0.8 * np.sin(
            np.linspace(0.0, 2.0 * np.pi, c, endpoint=False)
        )
        raw = (
            author[:, None, None]
            * condition[None, :, None]
            * direction[None, None, :]
        )
    elif world == "contrast_sensitive":
        if contrast_direction is None:
            raise ValueError("contrast_sensitive requires contrast_direction")
        author = rng.normal(size=n)
        author -= author.mean()
        condition = np.asarray(contrast_direction, dtype=float)
        condition /= max(float(np.linalg.norm(condition)), 1e-12)
        raw = (
            author[:, None, None]
            * condition[None, :, None]
            * direction[None, None, :]
        )
    elif world == "contrast_kernel":
        if contrast_direction is None:
            raise ValueError("contrast_kernel requires contrast_direction")
        contrast = np.asarray(contrast_direction, dtype=float)
        denominator = max(float(np.dot(contrast, contrast)), 1e-12)
        raw = rng.normal(size=(n, c, d))
        coefficient = np.einsum(
            "ucd,c->ud",
            raw,
            contrast,
        ) / denominator
        raw -= coefficient[:, None, :] * contrast[None, :, None]
        raw -= raw.mean(axis=(0, 1), keepdims=True)
    elif world == "full_rank":
        rank = min(48, n, c * d)
        left, _ = np.linalg.qr(rng.normal(size=(n, rank)))
        right, _ = np.linalg.qr(rng.normal(size=(c * d, rank)))
        raw = (left @ right.T).reshape(n, c, d)
        raw = _double_center(raw)
    elif world == "minority_local":
        raw = np.zeros((n, c, d))
        n_author = max(2, int(round(n * minority_author_fraction)))
        n_condition = max(2, int(round(c * minority_condition_fraction)))
        selected_author = rng.choice(n, size=n_author, replace=False)
        selected_condition = rng.choice(
            c,
            size=n_condition,
            replace=False,
        )
        local = rng.normal(size=(n_author, n_condition, d))
        raw[np.ix_(selected_author, selected_condition, np.arange(d))] = (
            local
        )
        raw -= raw.mean(axis=(0, 1), keepdims=True)
    elif world == "near_kernel":
        perpendicular = rng.normal(size=(n, c, d))
        perpendicular -= perpendicular.mean(axis=1, keepdims=True)
        perpendicular = _normalize_energy(perpendicular, 1.0)
        parallel = rng.normal(size=(n, 1, d))
        parallel -= parallel.mean(axis=0, keepdims=True)
        parallel = np.repeat(parallel, c, axis=1)
        parallel = _normalize_energy(parallel, 1.0)
        raw = (
            np.sqrt(float(near_kernel_fraction)) * parallel
            + np.sqrt(1.0 - float(near_kernel_fraction))
            * perpendicular
        )
    else:
        raise ValueError(f"unknown world: {world}")

    interaction = _normalize_energy(raw, target)
    reference = np.full(c, 1.0 / c)
    score = reference_score(interaction, reference)
    score_fraction = float(
        np.mean(score**2)
        / max(float(np.mean(interaction**2)), 1e-12)
    )
    return interaction, {
        "effective_rank": effective_rank(interaction),
        "score_fraction": score_fraction,
    }


def _noise(
    rng: np.random.Generator,
    shape: tuple[int, ...],
    *,
    mode: str,
    student_df: float,
) -> np.ndarray:
    if mode == "gaussian":
        return rng.normal(size=shape)
    if mode == "heteroskedastic_t5":
        scale = np.sqrt(float(student_df) / (float(student_df) - 2.0))
        return rng.standard_t(float(student_df), size=shape) / scale
    raise ValueError(f"unknown noise mode: {mode}")


def _condition_probabilities(
    *,
    world: str,
    target_jsd: float,
    support_coverage: float,
    author_tilt: float,
    author_covariate: np.ndarray,
    group_labels: np.ndarray,
    spec: ReferenceFrontierSpec,
    acquisition_reference_shift: bool = False,
) -> tuple[np.ndarray, float, float]:
    base_left, base_right, achieved_jsd = reference_pair(
        spec.conditions,
        target_jsd
        if world == "reference_shift" or acquisition_reference_shift
        else 0.0,
    )
    condition_axis = np.cos(
        np.linspace(
            0.0,
            2.0 * np.pi,
            spec.conditions,
            endpoint=False,
        )
    )
    probabilities = np.empty(
        (spec.panels, spec.authors, spec.conditions),
        dtype=float,
    )
    bases = [base_left, base_right, base_left, base_right]
    for panel, base in enumerate(bases):
        logits = (
            np.log(np.maximum(base, 1e-15))[None, :]
            + float(author_tilt)
            * author_covariate[:, None]
            * condition_axis[None, :]
        )
        probabilities[panel] = softmax(logits, axis=1)

    achieved_coverage = 1.0
    if world == "support_violation":
        keep = max(
            1,
            min(
                spec.conditions,
                int(round(spec.conditions * support_coverage)),
            ),
        )
        achieved_coverage = keep / spec.conditions
        missing = spec.conditions - keep
        if missing > 0:
            for author, group in enumerate(group_labels):
                start = (int(group) * max(missing, 1)) % spec.conditions
                blocked = (
                    start + np.arange(missing)
                ) % spec.conditions
                probabilities[:, author, blocked] = 0.0
            probabilities /= probabilities.sum(axis=2, keepdims=True)
    return probabilities, achieved_jsd, achieved_coverage


def simulate_reference_world(
    *,
    seed: int,
    world: str,
    effect_share: float,
    reference_jsd: float,
    support_coverage: float,
    near_kernel_fraction: float,
    noise_mode: str,
    opportunity_prefixes: tuple[int, ...],
    author_tilt: float,
    author_amplitude: float,
    condition_amplitude: float,
    society_amplitude: float,
    group_amplitude: float,
    panel_noise_amplitude: float,
    technical_noise_amplitude: float,
    student_df: float,
    heteroskedastic_strength: float,
    minority_author_fraction: float,
    minority_condition_fraction: float,
    spec: ReferenceFrontierSpec,
    acquisition_reference_shift: bool = False,
) -> dict[str, Any]:
    """Simulate one registered H.4D world."""
    rng = np.random.default_rng(int(seed))
    societies, groups = spec.author_labels
    n, c, d, p = (
        spec.authors,
        spec.conditions,
        spec.dimensions,
        spec.panels,
    )
    reference = np.full(c, 1.0 / c)
    author_covariate = rng.normal(size=n)
    society_effect = rng.normal(
        scale=society_amplitude,
        size=(spec.societies, d),
    )
    group_effect = rng.normal(
        scale=group_amplitude,
        size=(spec.groups, d),
    )
    author_effect = rng.normal(scale=author_amplitude, size=(n, d))
    author_effect -= author_effect.mean(axis=0, keepdims=True)
    condition_effect = rng.normal(
        scale=condition_amplitude,
        size=(c, d),
    )
    condition_effect -= condition_effect.mean(axis=0, keepdims=True)
    main = (
        society_effect[societies, None, :]
        + group_effect[groups, None, :]
        + author_effect[:, None, :]
        + condition_effect[None, :, :]
    )
    contrast_left, contrast_right, _ = reference_pair(
        c,
        reference_jsd if reference_jsd > 0 else 0.15,
    )
    contrast_direction = contrast_right - contrast_left
    interaction, interaction_info = _interaction(
        rng,
        world=world,
        effect_share=effect_share,
        near_kernel_fraction=near_kernel_fraction,
        minority_author_fraction=minority_author_fraction,
        minority_condition_fraction=minority_condition_fraction,
        spec=spec,
        base_energy=float(np.mean(main**2)),
        contrast_direction=contrast_direction,
    )
    cell_truth = main + interaction
    theta_star = reference_score(cell_truth, reference)
    probabilities, achieved_jsd, achieved_coverage = (
        _condition_probabilities(
            world=world,
            target_jsd=reference_jsd,
            support_coverage=support_coverage,
            author_tilt=author_tilt,
            author_covariate=author_covariate,
            group_labels=groups,
            spec=spec,
            acquisition_reference_shift=acquisition_reference_shift,
        )
    )

    prefixes = tuple(sorted(map(int, opportunity_prefixes)))
    increments = np.diff((0, *prefixes))
    cumulative_counts = np.zeros((p, n, c), dtype=int)
    cumulative_sums = np.zeros((p, n, c, d), dtype=float)
    counts_by_k: dict[int, np.ndarray] = {}
    means_by_k: dict[int, np.ndarray] = {}
    panel_shock = rng.normal(
        scale=panel_noise_amplitude,
        size=(p, n, c, d),
    )
    hetero = 1.0 + float(heteroskedastic_strength) * (
        0.5
        + np.abs(author_covariate[:, None])
        + np.linspace(0.0, 1.0, c)[None, :]
    ) / 2.5

    for increment, prefix in zip(increments, prefixes, strict=True):
        for panel in range(p):
            added = rng.multinomial(
                int(increment),
                probabilities[panel],
            )
            technical = _noise(
                rng,
                (n, c, d),
                mode=noise_mode,
                student_df=student_df,
            )
            noise_scale = (
                float(technical_noise_amplitude)
                * hetero[:, :, None]
                / np.sqrt(2.0)
            )
            noise_sum = (
                np.sqrt(added[:, :, None])
                * noise_scale
                * technical
            )
            cumulative_sums[panel] += (
                added[:, :, None]
                * (
                    cell_truth
                    + panel_shock[panel]
                )
                + noise_sum
            )
            cumulative_counts[panel] += added
        counts_by_k[int(prefix)] = cumulative_counts.copy()
        means = np.full((p, n, c, d), np.nan)
        valid = cumulative_counts > 0
        means[valid] = (
            cumulative_sums[valid]
            / cumulative_counts[valid][:, None]
        )
        means_by_k[int(prefix)] = means

    alias_error = 0.0
    if world == "aq_alias":
        shift = rng.normal(size=(n, d))
        left = author_effect[:, None, :] + interaction
        right = (
            (author_effect + shift)[:, None, :]
            + interaction
            - shift[:, None, :]
        )
        alias_error = float(np.max(np.abs(left - right)))

    return {
        "cell_truth": cell_truth,
        "main": main,
        "interaction": interaction,
        "theta_star": theta_star,
        "reference": reference,
        "contrast_reference_0": contrast_left,
        "contrast_reference_1": contrast_right,
        "contrast_direction": contrast_direction,
        "author_covariate": author_covariate,
        "society_labels": societies,
        "group_labels": groups,
        "probabilities": probabilities,
        "counts_by_k": counts_by_k,
        "means_by_k": means_by_k,
        "achieved_jsd": float(achieved_jsd),
        "achieved_support_coverage": float(achieved_coverage),
        "alias_identity_error": alias_error,
        **interaction_info,
    }


def fit_propensity(
    counts: np.ndarray,
    author_covariate: np.ndarray,
    train_authors: np.ndarray,
    *,
    pseudocount: float,
) -> np.ndarray:
    """Fit a fast multinomial log-ratio model from two train panels."""
    rows = []
    targets = []
    reference_condition = counts.shape[-1] - 1
    for panel in (0, 1):
        environment = float(panel % 2)
        selected = counts[panel, train_authors]
        x = author_covariate[train_authors]
        design = np.column_stack([
            np.ones(len(train_authors)),
            np.full(len(train_authors), environment),
            x,
            environment * x,
        ])
        log_ratio = np.log(
            (selected[:, :-1] + float(pseudocount))
            / (
                selected[:, reference_condition, None]
                + float(pseudocount)
            )
        )
        rows.append(design)
        targets.append(log_ratio)
    matrix = np.vstack(rows)
    response = np.vstack(targets)
    ridge = 1e-6 * np.eye(matrix.shape[1])
    return np.linalg.solve(
        matrix.T @ matrix + ridge,
        matrix.T @ response,
    )


def predict_propensity(
    coefficients: np.ndarray,
    author_covariate: np.ndarray,
    *,
    environment: int,
) -> np.ndarray:
    """Predict condition probabilities for an author environment."""
    x = np.asarray(author_covariate, dtype=float)
    env = float(environment)
    design = np.column_stack([
        np.ones(len(x)),
        np.full(len(x), env),
        x,
        env * x,
    ])
    logits = design @ coefficients
    logits = np.column_stack([logits, np.zeros(len(x))])
    return softmax(logits, axis=1)


def condition_profile(
    means: np.ndarray,
    train_authors: np.ndarray,
) -> np.ndarray:
    """Estimate population condition profile on train panels/authors."""
    values = means[:2, train_authors]
    profile = np.nanmean(values, axis=(0, 1))
    if not np.isfinite(profile).all():
        fallback = np.nanmean(values, axis=(0, 1, 2))
        missing = ~np.isfinite(profile)
        profile[missing] = np.broadcast_to(
            fallback,
            profile.shape,
        )[missing]
    return profile


def score_panel(
    counts: np.ndarray,
    means: np.ndarray,
    propensity: np.ndarray,
    profile: np.ndarray,
    reference: np.ndarray,
    authors: np.ndarray,
) -> dict[str, np.ndarray]:
    """Compute naive and stabilized common-reference author scores."""
    selected_counts = counts[authors].astype(float)
    selected_means = means[authors]
    valid = selected_counts > 0
    residual = selected_means - profile[None, :, :]
    residual = np.where(valid[:, :, None], residual, 0.0)
    naive_denominator = np.maximum(
        selected_counts.sum(axis=1),
        1.0,
    )
    naive = np.einsum(
        "uc,ucd->ud",
        selected_counts,
        residual,
    ) / naive_denominator[:, None]

    probability = np.maximum(propensity[authors], 1e-8)
    weights = reference[None, :] / probability
    weighted_counts = selected_counts * weights
    denominator = np.maximum(weighted_counts.sum(axis=1), 1e-12)
    common = np.einsum(
        "uc,ucd->ud",
        weighted_counts,
        residual,
    ) / denominator[:, None]
    ess = (
        denominator**2
        / np.maximum(
            np.sum(selected_counts * weights**2, axis=1),
            1e-12,
        )
    )
    coverage = np.sum(
        reference[None, :] * (probability > 1e-8),
        axis=1,
    )
    return {
        "naive": naive,
        "common": common,
        "ess": ess,
        "coverage": coverage,
    }


def empirical_structural_zero(
    counts: np.ndarray,
    authors: np.ndarray,
    group_labels: np.ndarray,
) -> bool:
    """Detect a group-condition zero in train acquisition."""
    for group in np.unique(group_labels[authors]):
        members = authors[group_labels[authors] == group]
        total = counts[:2, members].sum(axis=(0, 1))
        if np.any(total == 0):
            return True
    return False


def additive_residual(
    means: np.ndarray,
    counts: np.ndarray,
    authors: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Double-center observed test cells without oracle quantities."""
    values = means[authors].copy()
    valid = counts[authors] > 0
    values[~valid] = np.nan
    author_mean = np.nanmean(values, axis=1, keepdims=True)
    values = values - author_mean
    condition_mean = np.nanmean(values, axis=0, keepdims=True)
    values = values - condition_mean
    values[~valid] = 0.0
    return values, valid


def _residualize_masked(
    values: np.ndarray,
    valid: np.ndarray,
) -> np.ndarray:
    """Apply the registered row/column residualization to fixed masks."""
    result = np.asarray(values, dtype=float).copy()
    mask = np.asarray(valid, dtype=bool)
    result[~mask] = np.nan
    author_mean = np.nanmean(result, axis=1, keepdims=True)
    result -= author_mean
    condition_mean = np.nanmean(result, axis=0, keepdims=True)
    result -= condition_mean
    result[~mask] = 0.0
    return result


def cross_low_rank_ratio(
    left: np.ndarray,
    right: np.ndarray,
    *,
    rank: int,
) -> float:
    """Low-rank energy ratio of the cross-panel feature covariance."""
    x = np.asarray(left, dtype=float).reshape(len(left), -1)
    y = np.asarray(right, dtype=float).reshape(len(right), -1)
    cross = x.T @ y / max(len(x), 1)
    singular = np.linalg.svd(
        cross,
        full_matrices=False,
        compute_uv=False,
    )
    energy = singular**2
    return float(
        energy[:int(rank)].sum()
        / max(float(energy.sum()), 1e-12)
    )


def higher_criticism_stat(
    left: np.ndarray,
    right: np.ndarray,
    shared_mask: np.ndarray,
) -> float:
    """Higher-Criticism statistic over cellwise replicated products."""
    mask = np.asarray(shared_mask, dtype=bool)
    if not np.any(mask):
        return 0.0
    a = np.asarray(left, dtype=float)[mask]
    b = np.asarray(right, dtype=float)[mask]
    scale_a = np.maximum(a.std(axis=0, ddof=1), 1e-8)
    scale_b = np.maximum(b.std(axis=0, ddof=1), 1e-8)
    products = np.sum(
        (a / scale_a) * (b / scale_b),
        axis=1,
    ) / np.sqrt(a.shape[1])
    p_values = np.clip(norm.sf(products), 1e-12, 1.0 - 1e-12)
    ordered = np.sort(p_values)
    total = len(ordered)
    ranks = np.arange(1, total + 1, dtype=float) / total
    eligible = (ordered >= 1.0 / total) & (ordered <= 0.10)
    if not np.any(eligible):
        return 0.0
    statistic = (
        np.sqrt(total)
        * (ranks[eligible] - ordered[eligible])
        / np.sqrt(
            ordered[eligible] * (1.0 - ordered[eligible])
        )
    )
    return float(np.max(statistic))


def higher_criticism_permutation_p(
    left: np.ndarray,
    right: np.ndarray,
    shared_mask: np.ndarray,
    *,
    seed: int,
    permutations: int,
) -> tuple[float, float]:
    """Condition-permutation p-value for sparse replicated structure."""
    observed = higher_criticism_stat(left, right, shared_mask)
    rng = np.random.default_rng(int(seed))
    null = np.empty(int(permutations))
    for draw in range(int(permutations)):
        permuted = np.empty_like(right)
        permuted_mask = np.empty_like(shared_mask)
        for author in range(len(right)):
            order = rng.permutation(right.shape[1])
            permuted[author] = right[author, order]
            permuted_mask[author] = shared_mask[author, order]
        null[draw] = higher_criticism_stat(
            left,
            permuted,
            shared_mask & permuted_mask,
        )
    p_value = float(
        (1 + np.sum(null >= observed)) / (len(null) + 1)
    )
    return observed, p_value


def residual_diagnostics(
    left: np.ndarray,
    right: np.ndarray,
    left_mask: np.ndarray,
    right_mask: np.ndarray,
    group_labels: np.ndarray,
    *,
    rank: int,
    seed: int,
    permutations: int,
    alpha: float,
) -> dict[str, Any]:
    """Run CRC, low-rank, and sparse residual diagnostics."""
    shared = left_mask & right_mask
    left_used = np.where(shared[:, :, None], left, 0.0)
    right_used = np.where(shared[:, :, None], right, 0.0)
    streams = np.random.SeedSequence(int(seed)).spawn(3)

    def _seed(sequence: np.random.SeedSequence) -> int:
        return int(sequence.generate_state(1, dtype=np.uint64)[0])

    crc, crc_p = crc_permutation_p(
        left_used,
        right_used,
        group_labels,
        seed=_seed(streams[0]),
        permutations=permutations,
    )
    low_rank, low_rank_p = low_rank_permutation_p(
        0.5 * (left_used + right_used),
        rank=rank,
        seed=_seed(streams[1]),
        permutations=permutations,
    )
    hc, hc_p = higher_criticism_permutation_p(
        left_used,
        right_used,
        shared,
        seed=_seed(streams[2]),
        permutations=permutations,
    )
    adjusted = holm_adjust({
        "crc": crc_p,
        "low_rank": low_rank_p,
        "hc": hc_p,
    })
    detected = bool(min(adjusted.values()) < float(alpha))
    average = 0.5 * (left_used + right_used)
    projection = average.mean(axis=1)
    projection_ratio = float(
        np.mean(projection**2)
        / max(float(np.mean(average**2)), 1e-12)
    )
    return {
        "crc": float(crc),
        "crc_p": float(crc_p),
        "crc_p_holm": float(adjusted["crc"]),
        "low_rank_ratio": float(low_rank),
        "low_rank_p": float(low_rank_p),
        "low_rank_p_holm": float(adjusted["low_rank"]),
        "hc": float(hc),
        "hc_p": float(hc_p),
        "hc_p_holm": float(adjusted["hc"]),
        "structure_detected": detected,
        "non_low_rank_detected": bool(
            adjusted["crc"] < alpha or adjusted["hc"] < alpha
        ),
        "score_projection_ratio": projection_ratio,
    }


def wild_residual_diagnostics(
    left: np.ndarray,
    right: np.ndarray,
    left_mask: np.ndarray,
    right_mask: np.ndarray,
    *,
    rank: int,
    seed: int,
    permutations: int,
    alpha: float,
) -> dict[str, Any]:
    """Run three diagnostics against a shared author-level wild-sign null."""
    shared = np.asarray(left_mask, dtype=bool) & np.asarray(
        right_mask,
        dtype=bool,
    )
    left_used = _residualize_masked(left, shared)
    right_used = _residualize_masked(right, shared)
    observed = {
        "crc": residual_correlation(left_used, right_used),
        "low_rank": cross_low_rank_ratio(
            left_used,
            right_used,
            rank=rank,
        ),
        "hc": higher_criticism_stat(
            left_used,
            right_used,
            shared,
        ),
    }
    rng = np.random.default_rng(int(seed))
    null = {
        name: np.empty(int(permutations), dtype=float)
        for name in observed
    }
    for draw in range(int(permutations)):
        signs = rng.choice(
            [-1.0, 1.0],
            size=(len(right_used), 1, 1),
        )
        wild_right = _residualize_masked(
            right_used * signs,
            shared,
        )
        null["crc"][draw] = residual_correlation(
            left_used,
            wild_right,
        )
        null["low_rank"][draw] = cross_low_rank_ratio(
            left_used,
            wild_right,
            rank=rank,
        )
        null["hc"][draw] = higher_criticism_stat(
            left_used,
            wild_right,
            shared,
        )
    raw_p = {
        name: float(
            (1 + np.sum(null[name] >= statistic))
            / (int(permutations) + 1)
        )
        for name, statistic in observed.items()
    }
    adjusted = holm_adjust(raw_p)
    detected = bool(min(adjusted.values()) < float(alpha))
    return {
        "crc": float(observed["crc"]),
        "crc_p": raw_p["crc"],
        "crc_p_holm": float(adjusted["crc"]),
        "cross_low_rank_ratio": float(observed["low_rank"]),
        "cross_low_rank_p": raw_p["low_rank"],
        "cross_low_rank_p_holm": float(adjusted["low_rank"]),
        "hc": float(observed["hc"]),
        "hc_p": raw_p["hc"],
        "hc_p_holm": float(adjusted["hc"]),
        "structure_detected": detected,
        "non_low_rank_detected": bool(
            adjusted["crc"] < alpha or adjusted["hc"] < alpha
        ),
    }


def contrast_bootstrap_interval(
    delta_left: np.ndarray,
    delta_right: np.ndarray,
    theta_left: np.ndarray,
    theta_right: np.ndarray,
    *,
    seed: int,
    draws: int,
) -> dict[str, float]:
    """Estimate gauge-invariant contrast magnitude by author bootstrap."""
    left = np.asarray(delta_left, dtype=float)
    right = np.asarray(delta_right, dtype=float)
    theta = 0.5 * (
        np.asarray(theta_left, dtype=float)
        + np.asarray(theta_right, dtype=float)
    )

    def _statistic(index: np.ndarray) -> float:
        cross_energy = float(
            np.mean(left[index] * right[index])
        )
        denominator = max(
            float(np.std(theta[index])),
            1e-12,
        )
        return float(np.sqrt(max(cross_energy, 0.0)) / denominator)

    authors = len(left)
    base_index = np.arange(authors)
    point = _statistic(base_index)
    rng = np.random.default_rng(int(seed))
    samples = np.empty(int(draws), dtype=float)
    for draw in range(int(draws)):
        index = rng.integers(0, authors, size=authors)
        samples[draw] = _statistic(index)
    return {
        "d_contrast": point,
        "d_contrast_lower_95": float(np.quantile(samples, 0.05)),
        "d_contrast_upper_90": float(np.quantile(samples, 0.90)),
        "contrast_split_correlation": correlation(left, right),
    }


def correlation(left: np.ndarray, right: np.ndarray) -> float:
    """Flattened Pearson correlation with a zero-variance guard."""
    a = np.asarray(left, dtype=float).reshape(-1)
    b = np.asarray(right, dtype=float).reshape(-1)
    a -= a.mean()
    b -= b.mean()
    denominator = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denominator <= 1e-12:
        return 0.0
    return float(np.dot(a, b) / denominator)
