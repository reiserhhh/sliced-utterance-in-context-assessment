#!/usr/bin/env python3
"""Audit invariant landmark-graph signatures against sorted V7 geometry."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_geometry_behavior_bridge as bridge_run  # noqa: E402
import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
from suica_core.v7_geometry import GeometryBundle  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v7_psychometric import author_features_from_embeddings  # noqa: E402
from suica_core.v8_bridge import (  # noqa: E402
    SpectralGeometryProjector,
    canonical_orbit_distance_signatures,
    cross_modal_author_auc,
    landmark_spectral_signatures,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_spectral_geometry_audit.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_spectral_geometry_audit" / "pandora"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _whitened_author_points(
    geometry_panel: pd.DataFrame,
    metadata: pd.DataFrame,
    bundle: GeometryBundle,
) -> dict[str, np.ndarray]:
    representation = joblib.load(pandora.REPRESENTATION_PATH)
    ordered = metadata["author_id"].astype(str).tolist()
    output = {}
    impute = np.asarray(bundle.feature_impute, dtype=float)
    center = np.asarray(bundle.feature_center, dtype=float)
    whitener = np.asarray(bundle.metric_whitener, dtype=float)
    for side in ("left", "right"):
        observations = geometry_panel.loc[
            geometry_panel["split"].eq(side)
            & geometry_panel["user_id"].astype(str).isin(ordered)
        ].reset_index(drop=True)
        embeddings = representation.transform(observations["text"])
        features = author_features_from_embeddings(
            observations,
            embeddings,
        ).set_index("user_id")
        values = features.loc[ordered, bundle.feature_names].to_numpy(float)
        complete = np.where(np.isfinite(values), values, impute[None, :])
        output[side] = (complete - center[None, :]) @ whitener
    return output


def _interleave(
    left: np.ndarray,
    right: np.ndarray,
    author_ids: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values = np.vstack([
        np.vstack([left[index], right[index]])
        for index in range(len(author_ids))
    ])
    authors = np.repeat(np.asarray(author_ids, dtype=str), 2)
    sides = np.tile(np.asarray(["left", "right"]), len(author_ids))
    return values, authors, sides


def _query_auc_by_author(
    values: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    metric: str,
) -> dict[str, float]:
    output: dict[str, list[float]] = {}
    for index, (author, side) in enumerate(zip(authors, sides, strict=True)):
        targets = np.flatnonzero(sides != side)
        if metric == "euclidean":
            scores = -np.linalg.norm(values[targets] - values[index], axis=1)
        elif metric == "cosine":
            numerator = values[targets] @ values[index]
            denominator = (
                np.linalg.norm(values[targets], axis=1)
                * max(np.linalg.norm(values[index]), 1e-12)
            )
            scores = np.divide(
                numerator,
                denominator,
                out=np.zeros(len(targets)),
                where=denominator > 1e-12,
            )
        else:
            raise ValueError(f"unsupported author metric: {metric}")
        labels = authors[targets] == author
        if labels.sum() != 1:
            continue
        positive = float(scores[labels][0])
        negative = scores[~labels]
        auc = float(
            (np.sum(positive > negative) + 0.5 * np.sum(positive == negative))
            / len(negative)
        )
        output.setdefault(str(author), []).append(auc)
    return {
        author: float(np.mean(author_values))
        for author, author_values in output.items()
    }


def _bootstrap_interval(
    values: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    metric: str,
    seed: int,
    draws: int,
) -> tuple[float, float, float]:
    per_author = np.asarray(
        list(_query_auc_by_author(
            values,
            authors,
            sides,
            metric=metric,
        ).values()),
        dtype=float,
    )
    rng = np.random.default_rng(seed)
    samples = [
        float(rng.choice(
            per_author,
            size=len(per_author),
            replace=True,
        ).mean())
        for _ in range(int(draws))
    ]
    return (
        float(per_author.mean()),
        float(np.quantile(samples, 0.025)),
        float(np.quantile(samples, 0.975)),
    )


def _permutation_p(
    values: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    metric: str,
    observed: float,
    seed: int,
    permutations: int,
) -> float:
    rng = np.random.default_rng(seed)
    left = np.flatnonzero(sides == "left")
    right = np.flatnonzero(sides == "right")
    null = []
    for _ in range(int(permutations)):
        permuted = values.copy()
        permuted[right] = values[rng.permutation(right)]
        null.append(cross_modal_author_auc(
            permuted,
            permuted,
            authors,
            sides,
            metric=metric,
        ))
    return float(
        (1 + np.sum(np.asarray(null) >= float(observed)))
        / (len(null) + 1)
    )


def _evaluate(
    values: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    seed: int,
    draws: int,
    permutations: int,
    inference: bool,
) -> dict[str, float]:
    euclidean = cross_modal_author_auc(
        values,
        values,
        authors,
        sides,
        metric="euclidean",
    )
    result = {
        "same_author_auc_euclidean": euclidean,
        "same_author_auc_cosine": cross_modal_author_auc(
            values,
            values,
            authors,
            sides,
            metric="cosine",
        ),
    }
    if inference:
        euclidean_interval = _bootstrap_interval(
            values,
            authors,
            sides,
            metric="euclidean",
            seed=seed,
            draws=draws,
        )
        cosine_interval = _bootstrap_interval(
            values,
            authors,
            sides,
            metric="cosine",
            seed=seed + 11,
            draws=draws,
        )
        result.update({
            "same_author_auc_cluster_estimate": euclidean_interval[0],
            "same_author_auc_ci_lower": euclidean_interval[1],
            "same_author_auc_ci_upper": euclidean_interval[2],
            "same_author_permutation_p": _permutation_p(
                values,
                authors,
                sides,
                metric="euclidean",
                observed=euclidean,
                seed=seed + 1,
                permutations=permutations,
            ),
            "same_author_cosine_cluster_estimate": cosine_interval[0],
            "same_author_cosine_ci_lower": cosine_interval[1],
            "same_author_cosine_ci_upper": cosine_interval[2],
            "same_author_cosine_permutation_p": _permutation_p(
                values,
                authors,
                sides,
                metric="cosine",
                observed=float(result["same_author_auc_cosine"]),
                seed=seed + 12,
                permutations=permutations,
            ),
        })
    return result


def _paired_auc_delta_interval(
    first: np.ndarray,
    second: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    metric: str,
    seed: int,
    draws: int,
) -> tuple[float, float, float]:
    first_values = _query_auc_by_author(
        first,
        authors,
        sides,
        metric=metric,
    )
    second_values = _query_auc_by_author(
        second,
        authors,
        sides,
        metric=metric,
    )
    shared = sorted(set(first_values).intersection(second_values))
    differences = np.asarray([
        first_values[author] - second_values[author] for author in shared
    ])
    rng = np.random.default_rng(seed)
    samples = [
        float(rng.choice(
            differences,
            size=len(differences),
            replace=True,
        ).mean())
        for _ in range(int(draws))
    ]
    return (
        float(differences.mean()),
        float(np.quantile(samples, 0.025)),
        float(np.quantile(samples, 0.975)),
    )


def _scale_matched_auc(
    values: np.ndarray,
    raw_distances: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    neighbor_count: int = 5,
) -> float:
    nuisance = np.column_stack([
        raw_distances.mean(axis=1),
        raw_distances.std(axis=1),
    ])
    nuisance = StandardScaler().fit_transform(nuisance)
    labels: list[int] = []
    scores: list[float] = []
    for index, (author, side) in enumerate(zip(authors, sides, strict=True)):
        opposite = np.flatnonzero(sides != side)
        positive = opposite[authors[opposite] == author]
        strangers = opposite[authors[opposite] != author]
        if len(positive) != 1 or not len(strangers):
            continue
        distance = np.linalg.norm(
            nuisance[strangers] - nuisance[index],
            axis=1,
        )
        matched = strangers[
            np.argsort(distance, kind="stable")[: int(neighbor_count)]
        ]
        targets = np.r_[positive, matched]
        numerator = values[targets] @ values[index]
        denominator = (
            np.linalg.norm(values[targets], axis=1)
            * max(np.linalg.norm(values[index]), 1e-12)
        )
        similarity = np.divide(
            numerator,
            denominator,
            out=np.zeros(len(targets)),
            where=denominator > 1e-12,
        )
        labels.extend([1, *([0] * len(matched))])
        scores.extend(similarity.tolist())
    return float(roc_auc_score(labels, scores))


def _topology_shuffle_control(
    raw_canonical: np.ndarray,
    scaler: StandardScaler,
    mask: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    row_scale_residual: bool,
    seed: int,
    draws: int = 500,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)

    def transform(source: np.ndarray) -> np.ndarray:
        values = np.asarray(source, dtype=float)
        if row_scale_residual:
            values = (
                values - values.mean(axis=1, keepdims=True)
            ) / np.maximum(values.std(axis=1, keepdims=True), 1e-12)
        return scaler.transform(values)

    values = transform(raw_canonical)[mask]
    observed = cross_modal_author_auc(
        values,
        values,
        authors[mask],
        sides[mask],
        metric="cosine",
    )
    null = []
    for _ in range(int(draws)):
        shuffled = raw_canonical.copy()
        for row in range(len(shuffled)):
            shuffled[row] = shuffled[row, rng.permutation(shuffled.shape[1])]
        transformed = transform(shuffled)[mask]
        null.append(cross_modal_author_auc(
            transformed,
            transformed,
            authors[mask],
            sides[mask],
            metric="cosine",
        ))
    return {
        "observed_cosine_auc": float(observed),
        "shuffle_mean_cosine_auc": float(np.mean(null)),
        "topology_shuffle_drop": float(observed - np.mean(null)),
        "shuffle_p": float(
            (1 + np.sum(np.asarray(null) >= observed)) / (len(null) + 1)
        ),
    }


def _invariance_audit(
    points: np.ndarray,
    landmarks: np.ndarray,
    *,
    modes: list[str],
    seed: int,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(len(landmarks))
    orthogonal, _ = np.linalg.qr(
        rng.normal(size=(landmarks.shape[1], landmarks.shape[1]))
    )
    translation = rng.normal(size=landmarks.shape[1])
    rows = []
    for mode in modes:
        baseline, names = landmark_spectral_signatures(
            points,
            landmarks,
            mode=mode,
        )
        permuted, permuted_names = landmark_spectral_signatures(
            points,
            landmarks[permutation],
            mode=mode,
        )
        transformed, transformed_names = landmark_spectral_signatures(
            points @ orthogonal + translation,
            landmarks @ orthogonal + translation,
            mode=mode,
        )
        rows.append({
            "mode": mode,
            "features": len(names),
            "schema_preserved": bool(
                names == permuted_names == transformed_names
            ),
            "landmark_permutation_max_abs_error": float(
                np.max(np.abs(baseline - permuted))
            ),
            "rotation_translation_max_abs_error": float(
                np.max(np.abs(baseline - transformed))
            ),
        })
    return pd.DataFrame(rows)


def _report(
    decision: dict[str, Any],
    calibration: pd.DataFrame,
    confirmation: pd.DataFrame,
    invariance: pd.DataFrame,
) -> str:
    selected = confirmation.loc[
        confirmation["variant_id"].eq(decision["selected_variant"])
    ].iloc[0]
    baseline = confirmation.loc[
        confirmation["variant_id"].eq("sorted_quantile")
    ].iloc[0]
    return f"""# SUICA V8 Invariant Spectral Geometry Audit

Decision: `{decision["status"]}`

## Question

Does the V7 sorted distance multiset discard author-relevant landmark topology,
and can a landmark-permutation / Euclidean-isometry invariant graph or
canonical-orbit signature recover it?

No personality labels or new LLM calls were used. This is an exploratory
method audit on an already opened PANDORA author panel, not a new lockbox.

## Representation

For query point `x`, query-to-landmark affinities form a signal on the frozen
landmark graph. The audit records:

- signal energy within graph-Laplacian eigenspaces;
- heat-diffused signal moments and graph variation;
- heat-trace shifts after adding the query node.
- intrinsic landmark distance fingerprints that define anonymous canonical
  orbits, with sorting only inside unresolved symmetric orbits.

Energy is summed inside degenerate eigenspaces. Therefore eigenvector sign,
basis rotation inside a degenerate space, landmark permutation, and common
rotation/translation do not define the score.

## Invariance

{invariance.to_markdown(index=False)}

## Calibration

{calibration.to_markdown(index=False)}

## Opened-panel confirmation audit

{confirmation.to_markdown(index=False)}

Selected `{decision["selected_variant"]}`:
cosine AUC {selected["same_author_auc_cosine"]:.3f},
95% author-cluster interval [{selected["same_author_cosine_ci_lower"]:.3f},
{selected["same_author_cosine_ci_upper"]:.3f}].
Sorted-quantile baseline:
{baseline["same_author_auc_cosine"]:.3f}.

## Boundary

{decision["interpretation"]}

This result concerns source-disjoint author geometry only. It is neither a
personality construct nor evidence of clinical or cross-domain validity.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    source = ROOT / str(config["source_run"])
    source_config = _read_json(source / "config.resolved.json")
    inventory = verify_artifact_inventory(source / "artifact_inventory.json")
    if inventory["status"] != "INVENTORY_PASS":
        raise RuntimeError("source interpreter artifact inventory failed")
    observer_runs = bridge_run._load_observer_runs(
        source,
        repetitions=int(source_config["real_text"]["observer_repetitions"]),
    )
    complete_profiles = set.intersection(*[
        set(run["observer"]) for run in observer_runs
    ])
    semantic, geometry_panel = pandora._load_panels(source_config)
    metadata, sorted_geometry, bundle = pandora._score_geometry(
        semantic,
        geometry_panel,
        max_authors=int(
            source_config["real_text"]["max_authors"]["pandora"]
        ),
    )
    complete_authors = {
        str(author)
        for author in metadata["author_id"].astype(str)
        if (
            f"{author}::left" in complete_profiles
            and f"{author}::right" in complete_profiles
        )
    }
    kept = np.asarray([
        index
        for index, author in enumerate(metadata["author_id"].astype(str))
        if author in complete_authors
    ])
    metadata = metadata.iloc[kept].reset_index(drop=True)
    sorted_geometry = {
        side: values[kept] for side, values in sorted_geometry.items()
    }
    points = _whitened_author_points(
        geometry_panel,
        metadata,
        bundle,
    )
    author_ids = metadata["author_id"].astype(str).to_numpy()
    query_values, authors, sides = _interleave(
        points["left"],
        points["right"],
        author_ids,
    )
    sorted_values, _, _ = _interleave(
        sorted_geometry["left"],
        sorted_geometry["right"],
        author_ids,
    )
    split_by_author = metadata.set_index("author_id")["split"].astype(str)
    split = np.asarray([split_by_author[author] for author in authors])
    discovery = split == "discovery"
    calibration = split == "calibration"
    confirmation = split == "confirmation"
    landmarks = np.asarray(bundle.reference_landmarks, dtype=float)

    representations: dict[str, np.ndarray] = {
        "sorted_quantile": sorted_values,
        "distance_scale": sorted_values.std(axis=1, keepdims=True),
    }
    unsorted_distance = cdist(query_values, landmarks, metric="euclidean")
    unsorted_scaler = StandardScaler().fit(unsorted_distance[discovery])
    point_scaler = StandardScaler().fit(query_values[discovery])
    representations["unsorted_distance_identity_upper_bound"] = (
        unsorted_scaler.transform(unsorted_distance)
    )
    representations["whitened_point_coordinate_upper_bound"] = (
        point_scaler.transform(query_values)
    )
    canonical_values, canonical_names, canonical_diagnostics = (
        canonical_orbit_distance_signatures(
            query_values,
            landmarks,
            relative_tolerance=float(
                config["canonical_orbit"]["relative_tolerance"]
            ),
        )
    )
    canonical_scaler = StandardScaler().fit(canonical_values[discovery])
    representations["canonical_orbit_distance"] = (
        canonical_scaler.transform(canonical_values)
    )
    canonical_shape = (
        canonical_values - canonical_values.mean(axis=1, keepdims=True)
    ) / np.maximum(
        canonical_values.std(axis=1, keepdims=True),
        1e-12,
    )
    canonical_shape_scaler = StandardScaler().fit(
        canonical_shape[discovery]
    )
    representations["canonical_orbit_scale_residual"] = (
        canonical_shape_scaler.transform(canonical_shape)
    )
    projectors = {}
    for candidate in config["candidates"]:
        projector = SpectralGeometryProjector(
            landmarks=landmarks,
            mode=str(candidate["mode"]),
            variance_target=float(config["variance_target"]),
            max_components=int(candidate["max_components"]),
        ).fit(query_values[discovery])
        variant_id = str(candidate["variant_id"])
        representations[variant_id] = projector.transform(query_values)
        projectors[variant_id] = projector

    modes = sorted({str(candidate["mode"]) for candidate in config["candidates"]})
    invariance = _invariance_audit(
        query_values[discovery][:8],
        landmarks,
        modes=modes,
        seed=int(config["seed"]),
    )
    rng = np.random.default_rng(int(config["seed"]) + 77)
    audit_points = query_values[discovery][:8]
    canonical_baseline, _, _ = canonical_orbit_distance_signatures(
        audit_points,
        landmarks,
        relative_tolerance=float(
            config["canonical_orbit"]["relative_tolerance"]
        ),
    )
    permutation = rng.permutation(len(landmarks))
    canonical_permuted, permuted_names, _ = canonical_orbit_distance_signatures(
        audit_points,
        landmarks[permutation],
        relative_tolerance=float(
            config["canonical_orbit"]["relative_tolerance"]
        ),
    )
    orthogonal, _ = np.linalg.qr(
        rng.normal(size=(landmarks.shape[1], landmarks.shape[1]))
    )
    translation = rng.normal(size=landmarks.shape[1])
    canonical_transformed, transformed_names, _ = (
        canonical_orbit_distance_signatures(
            audit_points @ orthogonal + translation,
            landmarks @ orthogonal + translation,
            relative_tolerance=float(
                config["canonical_orbit"]["relative_tolerance"]
            ),
        )
    )
    invariance = pd.concat([
        invariance,
        pd.DataFrame([{
            "mode": "canonical_orbit_distance",
            "features": len(canonical_names),
            "schema_preserved": bool(
                canonical_names == permuted_names == transformed_names
            ),
            "landmark_permutation_max_abs_error": float(
                np.max(np.abs(canonical_baseline - canonical_permuted))
            ),
            "rotation_translation_max_abs_error": float(
                np.max(np.abs(canonical_baseline - canonical_transformed))
            ),
        }]),
    ], ignore_index=True)
    invariant_candidates = set(projectors)
    if bool(config["canonical_orbit"]["enabled"]):
        invariant_candidates.update({
            "canonical_orbit_distance",
            "canonical_orbit_scale_residual",
        })
    calibration_rows = []
    for index, (variant_id, values) in enumerate(representations.items()):
        metrics = _evaluate(
            values[calibration],
            authors[calibration],
            sides[calibration],
            seed=int(config["seed"]) + index,
            draws=int(config["bootstrap_draws"]),
            permutations=int(config["permutations"]),
            inference=False,
        )
        calibration_rows.append({
            "variant_id": variant_id,
            "dimensions": int(values.shape[1]),
            "eligible_invariant_candidate": variant_id in invariant_candidates,
            **metrics,
        })
    calibration_frame = pd.DataFrame(calibration_rows)
    eligible = calibration_frame.loc[
        calibration_frame["eligible_invariant_candidate"]
    ]
    selected_variant = str(config["primary_candidate"])
    if selected_variant not in set(eligible["variant_id"].astype(str)):
        raise ValueError("primary_candidate is not an eligible invariant representation")
    confirmation_ids = [
        "sorted_quantile",
        "distance_scale",
        "unsorted_distance_identity_upper_bound",
        "whitened_point_coordinate_upper_bound",
        "canonical_orbit_scale_residual",
        "spectral_energy_16",
        selected_variant,
    ]
    confirmation_rows = []
    inferential_variants = {
        "sorted_quantile",
        "spectral_energy_16",
        selected_variant,
    }
    for index, variant_id in enumerate(dict.fromkeys(confirmation_ids)):
        values = representations[variant_id]
        metrics = _evaluate(
            values[confirmation],
            authors[confirmation],
            sides[confirmation],
            seed=int(config["seed"]) + 1000 + index,
            draws=int(config["bootstrap_draws"]),
            permutations=int(config["permutations"]),
            inference=variant_id in inferential_variants,
        )
        confirmation_rows.append({
            "variant_id": variant_id,
            "dimensions": int(values.shape[1]),
            "eligible_invariant_candidate": variant_id in invariant_candidates,
            **metrics,
        })
    confirmation_frame = pd.DataFrame(confirmation_rows)
    selected = confirmation_frame.loc[
        confirmation_frame["variant_id"].eq(selected_variant)
    ].iloc[0]
    baseline = confirmation_frame.loc[
        confirmation_frame["variant_id"].eq("sorted_quantile")
    ].iloc[0]
    gates = config["gates"]
    max_invariance_error = float(max(
        invariance["landmark_permutation_max_abs_error"].max(),
        invariance["rotation_translation_max_abs_error"].max(),
    ))
    selected_values = representations[selected_variant][confirmation]
    sorted_confirmation_values = representations["sorted_quantile"][
        confirmation
    ]
    spectral_confirmation_values = representations["spectral_energy_16"][
        confirmation
    ]
    delta_sorted = _paired_auc_delta_interval(
        selected_values,
        sorted_confirmation_values,
        authors[confirmation],
        sides[confirmation],
        metric="cosine",
        seed=int(config["seed"]) + 5000,
        draws=int(config["bootstrap_draws"]),
    )
    delta_spectral = _paired_auc_delta_interval(
        selected_values,
        spectral_confirmation_values,
        authors[confirmation],
        sides[confirmation],
        metric="cosine",
        seed=int(config["seed"]) + 5001,
        draws=int(config["bootstrap_draws"]),
    )
    scale_matched_auc = _scale_matched_auc(
        selected_values,
        canonical_values[confirmation],
        authors[confirmation],
        sides[confirmation],
    )
    shuffle_control = _topology_shuffle_control(
        canonical_values,
        (
            canonical_shape_scaler
            if selected_variant == "canonical_orbit_scale_residual"
            else canonical_scaler
        ),
        confirmation,
        authors,
        sides,
        row_scale_residual=(
            selected_variant == "canonical_orbit_scale_residual"
        ),
        seed=int(config["seed"]) + 5002,
    )
    indexed_equivalence_error = float(abs(
        calibration_frame.loc[
            calibration_frame["variant_id"].eq("canonical_orbit_distance"),
            "same_author_auc_cosine",
        ].iloc[0]
        - calibration_frame.loc[
            calibration_frame["variant_id"].eq(
                "unsorted_distance_identity_upper_bound"
            ),
            "same_author_auc_cosine",
        ].iloc[0]
    ))
    checks = {
        "same_author_cosine_auc": (
            float(selected["same_author_auc_cosine"])
            >= float(gates["minimum_same_author_cosine_auc"])
        ),
        "cosine_auc_lower": (
            float(selected["same_author_cosine_ci_lower"])
            > float(gates["minimum_cosine_auc_lower"])
        ),
        "permutation_p": (
            float(selected["same_author_cosine_permutation_p"])
            <= float(gates["maximum_permutation_p"])
        ),
        "delta_over_sorted": (
            float(delta_sorted[0])
            >= float(gates["minimum_delta_over_sorted_quantile"])
            and float(delta_sorted[1]) > 0
        ),
        "delta_over_spectral_energy": (
            float(delta_spectral[0])
            >= float(gates["minimum_delta_over_spectral_energy"])
            and float(delta_spectral[1]) > 0
        ),
        "scale_conditioned": (
            scale_matched_auc
            >= float(gates["minimum_scale_conditioned_auc"])
        ),
        "topology_shuffle": (
            float(shuffle_control["topology_shuffle_drop"])
            >= float(gates["minimum_topology_shuffle_drop"])
        ),
        "indexed_equivalence": (
            indexed_equivalence_error
            <= float(gates["maximum_indexed_equivalence_error"])
        ),
        "invariance": (
            max_invariance_error
            <= float(gates["maximum_invariance_error"])
            and bool(invariance["schema_preserved"].all())
        ),
    }
    if all(checks.values()):
        status = (
            "V8_CANONICAL_SCALE_RESIDUAL_EXPLORATORY_PASS"
            if selected_variant == "canonical_orbit_scale_residual"
            else "V8_SPECTRAL_GEOMETRY_EXPLORATORY_PASS"
        )
        interpretation = (
            "The invariant canonical geometry recovered source-disjoint "
            "author structure lost by the sorted distance multiset and "
            "survived topology-specific controls. A fresh registered author "
            "panel is required before changing the frozen V7 object."
        )
    elif (
        checks["same_author_cosine_auc"]
        and checks["delta_over_sorted"]
        and checks["invariance"]
        and checks["indexed_equivalence"]
    ):
        status = "V8_CANONICAL_ORBIT_MECHANISM_SUPPORTED_UNDERPOWERED"
        interpretation = (
            "Canonical structural landmark identity recovered the indexed "
            "distance geometry and materially exceeded the sorted multiset, "
            "but one or more inferential or topology-specific gates remain "
            "open. Freeze this as a candidate and confirm on a fresh panel "
            "before reconnecting the behavior bridge."
        )
    else:
        status = "V8_SPECTRAL_GEOMETRY_STOP"
        interpretation = (
            "The invariant graph signature did not recover a sufficiently "
            "stable source-disjoint author object. Do not reconnect the LLM "
            "behavior bridge; inspect the upstream author representation and "
            "source budget first."
        )
    decision = {
        "status": status,
        "selected_variant": selected_variant,
        "checks": checks,
        "selected_confirmation": selected.to_dict(),
        "sorted_confirmation": baseline.to_dict(),
        "delta_over_sorted": float(
            selected["same_author_auc_cosine"]
            - baseline["same_author_auc_cosine"]
        ),
        "paired_delta_over_sorted_cosine": {
            "estimate": delta_sorted[0],
            "ci_lower": delta_sorted[1],
            "ci_upper": delta_sorted[2],
        },
        "paired_delta_over_spectral_energy_cosine": {
            "estimate": delta_spectral[0],
            "ci_lower": delta_spectral[1],
            "ci_upper": delta_spectral[2],
        },
        "scale_matched_cosine_auc": scale_matched_auc,
        "topology_shuffle_control": shuffle_control,
        "indexed_equivalence_error": indexed_equivalence_error,
        "maximum_invariance_error": max_invariance_error,
        "confirmation_status": (
            "OPENED_PANEL_EXPLORATORY_METHOD_AUDIT_NOT_LOCKBOX"
        ),
        "new_llm_calls": 0,
        "external_labels_read": False,
        "canonical_orbit_candidate_status": (
            "POSTHOC_SCALE_RESIDUAL_FOLLOWUP_AFTER_OPENED_CANONICAL_V3"
        ),
        "interpretation": interpretation,
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.output_dir / "config.resolved.json", config)
    _write_json(args.output_dir / "decision.json", decision)
    _write_json(
        args.output_dir / "canonical_orbit_diagnostics.json",
        canonical_diagnostics,
    )
    calibration_frame.to_csv(
        args.output_dir / "calibration_metrics.csv",
        index=False,
    )
    confirmation_frame.to_csv(
        args.output_dir / "confirmation_audit_metrics.csv",
        index=False,
    )
    invariance.to_csv(
        args.output_dir / "invariance_audit.csv",
        index=False,
    )
    (args.output_dir / "report.md").write_text(
        _report(
            decision,
            calibration_frame,
            confirmation_frame,
            invariance,
        ),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            source / "artifact_inventory.json",
            source / "decision.json",
            source / "config.resolved.json",
            pandora.PANDORA_COMMENTS_PATH,
            pandora.ELIGIBLE_AUTHORS_PATH,
            pandora.REPRESENTATION_PATH,
            pandora.GEOMETRY_PATH,
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_bridge.py",
            ROOT / "scripts" / "run_suica_v8_interpreter_pandora.py",
        ],
        estimand_id="V8-I4-pandora-invariant-landmark-spectral-geometry",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
