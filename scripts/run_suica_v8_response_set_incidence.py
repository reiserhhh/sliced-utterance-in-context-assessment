#!/usr/bin/env python3
"""Run the SUICA V8 planted affine response-set incidence battery."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.metrics import balanced_accuracy_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_response_set_incidence import (  # noqa: E402
    AffineMap,
    ResponseSetSpec,
    WORLD_LABELS,
    analyze_pair,
    bounded_affine_distance,
    box_count_dimension,
    condition_design,
    evaluate_affine,
    finite_direction_family,
    fit_affine_views,
    graph_edge_f1,
    pairwise_incidence_graph,
    planted_pair,
    principal_angle_degrees,
    rigid_transform,
    simulate_pair_observations,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _spec(config: dict[str, Any]) -> ResponseSetSpec:
    return ResponseSetSpec(**config["spec"])


def _seed(
    config: dict[str, Any],
    stage: str,
    world_index: int,
    repetition: int,
) -> int:
    offsets = {
        "discovery": 0,
        "calibration": 10_000_000,
        "confirmation": 20_000_000,
        "sensitivity": 30_000_000,
        "dimension": 40_000_000,
        "graph": 50_000_000,
    }
    return (
        int(config["seed"])
        + offsets[stage]
        + 100_000 * int(world_index)
        + int(repetition)
    )


def _pair_payload(
    payload: tuple[
        dict[str, Any], str, str, int, int, float,
    ],
) -> dict[str, Any]:
    config, stage, world, world_index, repetition, noise_sd = payload
    seed = _seed(config, stage, world_index, repetition)
    observed = simulate_pair_observations(
        seed=seed,
        world=world,
        spec=_spec(config),
        noise_sd=noise_sd,
    )
    result = analyze_pair(observed)
    row = {
        "stage": stage,
        "seed": seed,
        "repetition": repetition,
        "noise_sd": noise_sd,
        "world": world,
        **WORLD_LABELS[world],
        **result,
        "expected_same": bool(WORLD_LABELS[world]["same"]),
        "expected_free": bool(WORLD_LABELS[world]["free"]),
        "expected_overlap": bool(WORLD_LABELS[world]["overlap"]),
        "expected_attack": bool(WORLD_LABELS[world]["attack"]),
    }
    if result["status"] == "ESTIMATE_READY":
        left, right = observed["oracle_maps"]
        rng = np.random.default_rng(seed + 71_000_000)
        rotation, _ = np.linalg.qr(
            rng.normal(size=(
                left.ambient_dimensions,
                left.ambient_dimensions,
            ))
        )
        translation = rng.normal(
            size=left.ambient_dimensions,
        )
        original_same = bounded_affine_distance(
            left,
            right,
            same_condition=True,
        )["distance"]
        original_free = bounded_affine_distance(
            left,
            right,
            same_condition=False,
        )["distance"]
        transformed_left = rigid_transform(left, rotation, translation)
        transformed_right = rigid_transform(right, rotation, translation)
        transformed_same = bounded_affine_distance(
            transformed_left,
            transformed_right,
            same_condition=True,
        )["distance"]
        transformed_free = bounded_affine_distance(
            transformed_left,
            transformed_right,
            same_condition=False,
        )["distance"]
        row["rigid_invariant"] = bool(
            abs(original_same - transformed_same) <= 1e-8
            and abs(original_free - transformed_free) <= 1e-8
        )
    else:
        row["rigid_invariant"] = True
    return row


def _parallel(
    payloads: list[Any],
    worker: Any,
    *,
    jobs: int,
) -> list[dict[str, Any]]:
    if jobs <= 1:
        return [worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(worker, payloads, chunksize=8))


def _run_pair_stage(
    config: dict[str, Any],
    *,
    stage: str,
    repetitions: int,
    noise_sd: float,
) -> pd.DataFrame:
    payloads = [
        (
            config,
            stage,
            world,
            world_index,
            repetition,
            noise_sd,
        )
        for world_index, world in enumerate(config["worlds"])
        for repetition in range(repetitions)
    ]
    return pd.DataFrame(_parallel(
        payloads,
        _pair_payload,
        jobs=int(config["jobs"]),
    ))


def _thresholds(calibration: pd.DataFrame) -> dict[str, float]:
    ready = calibration[
        calibration["status"].eq("ESTIMATE_READY")
    ].copy()
    valid = ready[~ready["expected_attack"].astype(bool)]
    same_positive = valid[valid["expected_same"].astype(bool)]
    same_negative = valid[~valid["expected_same"].astype(bool)]
    free_positive = valid[valid["expected_free"].astype(bool)]
    free_negative = valid[~valid["expected_free"].astype(bool)]
    overlap = same_positive[
        same_positive["expected_overlap"].astype(bool)
    ]
    return {
        "maximum_residual_rmse": float(
            valid["residual_rmse"].quantile(0.995)
        ),
        "maximum_coefficient_instability": float(
            valid["coefficient_stability"].quantile(0.995)
        ),
        "same_intersection_ceiling": float(
            same_positive["same_z"].quantile(0.99)
        ),
        "same_disjoint_floor": float(
            same_negative["same_z"].quantile(0.01)
        ),
        "free_intersection_ceiling": float(
            free_positive["free_z"].quantile(0.99)
        ),
        "free_disjoint_floor": float(
            free_negative["free_z"].quantile(0.01)
        ),
        "overlap_coverage_floor": float(
            overlap["same_coverage"].quantile(0.01)
        ),
        "overlap_map_difference_ceiling": float(
            overlap["map_difference_z"].quantile(0.99)
        ),
    }


def _expected_relation(row: pd.Series) -> str:
    if bool(row["expected_attack"]):
        return "NOT_IDENTIFIABLE"
    if bool(row["expected_same"]):
        return (
            "SAME_CONDITION_OVERLAP"
            if bool(row["expected_overlap"])
            else "SAME_CONDITION_CROSSING"
        )
    if bool(row["expected_free"]):
        return "CROSS_CONDITION_ONLY"
    return "DISJOINT"


def _classify_row(
    row: pd.Series,
    thresholds: dict[str, float],
) -> tuple[str, str]:
    if row["status"] != "ESTIMATE_READY":
        return "NOT_IDENTIFIABLE", str(row["status"])
    if (
        float(row["residual_rmse"])
        > thresholds["maximum_residual_rmse"]
    ):
        return "NOT_IDENTIFIABLE", "INTERPOLATION_RESIDUAL_TOO_LARGE"
    if (
        float(row["coefficient_stability"])
        > thresholds["maximum_coefficient_instability"]
    ):
        return "NOT_IDENTIFIABLE", "CROSS_VIEW_COEFFICIENT_UNSTABLE"
    same = float(row["same_z"])
    free = float(row["free_z"])
    if same <= thresholds["same_intersection_ceiling"]:
        if (
            float(row["map_difference_z"])
            <= thresholds["overlap_map_difference_ceiling"]
        ):
            return "SAME_CONDITION_OVERLAP", ""
        return "SAME_CONDITION_CROSSING", ""
    if same < thresholds["same_disjoint_floor"]:
        return "NOT_IDENTIFIABLE", "SAME_CONDITION_GRAY_REGION"
    if free <= thresholds["free_intersection_ceiling"]:
        return "CROSS_CONDITION_ONLY", ""
    if free < thresholds["free_disjoint_floor"]:
        return "NOT_IDENTIFIABLE", "FREE_IMAGE_GRAY_REGION"
    return "DISJOINT", ""


def _apply_classifier(
    frame: pd.DataFrame,
    thresholds: dict[str, float],
) -> pd.DataFrame:
    result = frame.copy()
    result["expected_relation"] = result.apply(
        _expected_relation,
        axis=1,
    )
    decisions = result.apply(
        lambda row: _classify_row(row, thresholds),
        axis=1,
    )
    result["predicted_relation"] = [
        decision[0] for decision in decisions
    ]
    result["refusal_reason"] = [
        decision[1] for decision in decisions
    ]
    result["correct"] = (
        result["predicted_relation"]
        == result["expected_relation"]
    )
    result["false_same_edge"] = (
        ~result["expected_same"].astype(bool)
        & result["predicted_relation"].isin({
            "SAME_CONDITION_OVERLAP",
            "SAME_CONDITION_CROSSING",
        })
    )
    return result


def _one_sided_upper(successes: int, trials: int) -> float:
    if trials <= 0:
        return 1.0
    if successes >= trials:
        return 1.0
    return float(beta.ppf(
        0.95,
        successes + 1,
        trials - successes,
    ))


def _summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (stage, noise_sd, world), group in frame.groupby(
        ["stage", "noise_sd", "world"],
        dropna=False,
    ):
        dimension_values = np.abs(
            group["left_dimension"]
            - group["expected_dimension"]
        ).dropna()
        rows.append({
            "stage": stage,
            "noise_sd": noise_sd,
            "world": world,
            "expected_relation": group["expected_relation"].iloc[0],
            "repetitions": len(group),
            "correct_rate": float(group["correct"].mean()),
            "refusal_rate": float(
                group["predicted_relation"]
                .eq("NOT_IDENTIFIABLE")
                .mean()
            ),
            "false_same_edge_rate": float(
                group["false_same_edge"].mean()
            ),
            "same_z_median": float(group["same_z"].median()),
            "free_z_median": float(group["free_z"].median()),
            "same_coverage_median": float(
                group["same_coverage"].median()
            ),
            "principal_angle_error_median": float(
                group["principal_angle_error"].median()
            ),
            "dimension_error_median": (
                float(dimension_values.median())
                if len(dimension_values)
                else np.nan
            ),
        })
    return pd.DataFrame(rows)


def _dimension_payload(
    payload: tuple[dict[str, Any], str, int, int],
) -> dict[str, Any]:
    config, world, world_index, repetition = payload
    seed = _seed(config, "dimension", world_index, repetition)
    observed = simulate_pair_observations(
        seed=seed,
        world=world,
        spec=_spec(config),
        noise_sd=float(config["primary_noise_sd"]),
    )
    fit = fit_affine_views(
        observed["conditions"],
        observed["observations"][0],
    )
    estimate = box_count_dimension(
        fit["aggregate"],
        samples=100_000,
        seed=seed,
    )
    return {
        "seed": seed,
        "world": world,
        "ambient_dimensions": (
            fit["aggregate"].ambient_dimensions
        ),
        "expected_dimension": (
            fit["aggregate"].condition_dimensions
        ),
        "estimated_dimension": estimate["dimension"],
        "absolute_error": abs(
            estimate["dimension"]
            - fit["aggregate"].condition_dimensions
        ),
        "scaling_r2": estimate["r2"],
    }


def _run_dimensions(config: dict[str, Any]) -> pd.DataFrame:
    worlds = ["l2_same_cross", "l3_same_cross", "p3_same_line", "v3_coincident"]
    payloads = [
        (config, world, index, repetition)
        for index, world in enumerate(worlds)
        for repetition in range(int(config["dimension_repetitions"]))
    ]
    return pd.DataFrame(_parallel(
        payloads,
        _dimension_payload,
        jobs=int(config["jobs"]),
    ))


def _estimated_family(
    *,
    seed: int,
    world: str,
    authors: int,
    coefficient_noise: float,
) -> tuple[list[AffineMap], list[list[AffineMap]]]:
    rng = np.random.default_rng(seed)
    oracle = finite_direction_family(authors=authors, world=world)
    views: list[list[AffineMap]] = []
    aggregate: list[AffineMap] = []
    for model in oracle:
        current = [
            AffineMap(
                model.intercept + rng.normal(
                    scale=coefficient_noise,
                    size=model.intercept.shape,
                ),
                model.operator + rng.normal(
                    scale=coefficient_noise,
                    size=model.operator.shape,
                ),
            )
            for _ in range(4)
        ]
        views.append(current)
        aggregate.append(AffineMap(
            np.mean([item.intercept for item in current], axis=0),
            np.mean([item.operator for item in current], axis=0),
        ))
    return aggregate, views


def _threshold_graph(
    models: list[AffineMap],
    *,
    z_threshold: float,
    pair_uncertainty: float,
) -> np.ndarray:
    return pairwise_incidence_graph(
        models,
        distance_threshold=z_threshold * pair_uncertainty,
    )


def _graph_jaccard(left: np.ndarray, right: np.ndarray) -> float:
    upper = np.triu_indices(len(left), 1)
    a = left[upper]
    b = right[upper]
    union = int(np.sum(a | b))
    return float(np.sum(a & b) / union) if union else 1.0


def _excess_graph(
    models: list[AffineMap],
    *,
    pair_uncertainty: float,
    map_difference_ceiling: float,
) -> np.ndarray:
    n = len(models)
    graph = np.zeros((n, n), dtype=bool)
    for left in range(n):
        for right in range(left + 1, n):
            map_difference = float(np.sqrt(
                np.sum(
                    (
                        models[left].intercept
                        - models[right].intercept
                    ) ** 2
                )
                + np.sum(
                    (
                        models[left].operator
                        - models[right].operator
                    ) ** 2
                )
            ))
            graph[left, right] = graph[right, left] = (
                map_difference / max(pair_uncertainty, 1e-12)
                <= map_difference_ceiling
            )
    return graph


def _union_box_dimension(models: list[AffineMap]) -> float:
    axis = np.linspace(-1.0, 1.0, 257)[:, None]
    points = np.vstack([
        evaluate_affine(model, axis)
        for model in models
    ])
    centered = points - points.mean(axis=0, keepdims=True)
    scale = max(
        float(np.max(np.linalg.norm(centered, axis=1))),
        1e-12,
    )
    values = centered / scale
    epsilons = np.asarray([0.16, 0.13, 0.105, 0.085, 0.070, 0.058])
    counts = []
    for epsilon in epsilons:
        boxes = np.floor(values / epsilon).astype(np.int64)
        counts.append(len(np.unique(boxes, axis=0)))
    slope, _ = np.polyfit(
        np.log(1.0 / epsilons),
        np.log(np.maximum(counts, 1)),
        1,
    )
    return float(slope)


def _graph_payload(
    payload: tuple[dict[str, Any], dict[str, float], str, int, int],
) -> dict[str, Any]:
    config, thresholds, world, world_index, repetition = payload
    seed = _seed(config, "graph", world_index, repetition)
    authors = 16
    coefficient_noise = 0.002
    pair_uncertainty = 3.0 * coefficient_noise
    oracle = finite_direction_family(authors=authors, world=world)
    aggregate, views = _estimated_family(
        seed=seed,
        world=world,
        authors=authors,
        coefficient_noise=coefficient_noise,
    )
    oracle_raw = pairwise_incidence_graph(
        oracle,
        distance_threshold=1e-9,
    )
    predicted_raw = _threshold_graph(
        aggregate,
        z_threshold=thresholds["same_intersection_ceiling"],
        pair_uncertainty=pair_uncertainty,
    )
    view_excess_graphs = [
        _excess_graph(
            [author_views[index] for author_views in views],
            pair_uncertainty=pair_uncertainty,
            map_difference_ceiling=(
                thresholds["overlap_map_difference_ceiling"]
            ),
        )
        for index in range(4)
    ]
    predicted_excess = _excess_graph(
        aggregate,
        pair_uncertainty=pair_uncertainty,
        map_difference_ceiling=(
            thresholds["overlap_map_difference_ceiling"]
        ),
    )
    oracle_excess = np.zeros_like(oracle_raw)
    if world == "paired_overlaps":
        for index in range(0, authors, 2):
            oracle_excess[index, index + 1] = True
            oracle_excess[index + 1, index] = True
    upper = np.triu_indices(authors, 1)
    false_excess_edges = int(np.sum(
        predicted_excess[upper] & ~oracle_excess[upper]
    ))
    return {
        "seed": seed,
        "world": world,
        "raw_edge_f1": graph_edge_f1(
            oracle_raw,
            predicted_raw,
        ),
        "excess_edge_f1": graph_edge_f1(
            oracle_excess,
            predicted_excess,
        ),
        "false_excess_edges": false_excess_edges,
        "any_false_excess": bool(false_excess_edges),
        "cross_view_excess_jaccard": float(np.mean([
            _graph_jaccard(predicted_excess, graph)
            for graph in view_excess_graphs
        ])),
        "oracle_raw_edges": int(np.sum(oracle_raw[upper])),
        "predicted_raw_edges": int(np.sum(predicted_raw[upper])),
        "predicted_excess_edges": int(np.sum(
            predicted_excess[upper]
        )),
        "union_box_dimension": _union_box_dimension(oracle),
    }


def _run_graphs(
    config: dict[str, Any],
    thresholds: dict[str, float],
) -> pd.DataFrame:
    worlds = ["paired_overlaps", "common_anchor", "tangent_segments"]
    payloads = [
        (config, thresholds, world, index, repetition)
        for index, world in enumerate(worlds)
        for repetition in range(int(config["graph_repetitions"]))
    ]
    return pd.DataFrame(_parallel(
        payloads,
        _graph_payload,
        jobs=int(config["jobs"]),
    ))


def _headline(
    confirmation: pd.DataFrame,
    dimensions: pd.DataFrame,
    graphs: pd.DataFrame,
) -> dict[str, float]:
    ready = confirmation[
        confirmation["status"].eq("ESTIMATE_READY")
        & ~confirmation["expected_attack"].astype(bool)
    ]
    same_auc = float(roc_auc_score(
        ready["expected_same"].astype(int),
        -ready["same_z"],
    ))
    free_auc = float(roc_auc_score(
        ready["expected_free"].astype(int),
        -ready["free_z"],
    ))
    relation_balanced = float(balanced_accuracy_score(
        ready["expected_relation"],
        ready["predicted_relation"],
    ))
    negative = confirmation[
        ~confirmation["expected_same"].astype(bool)
    ]
    false_count = int(negative["false_same_edge"].sum())
    attack = confirmation[
        confirmation["expected_attack"].astype(bool)
    ]
    graph_primary = graphs[
        graphs["world"].eq("paired_overlaps")
    ]
    graph_controls = graphs[
        graphs["world"].isin({"common_anchor", "tangent_segments"})
    ]
    return {
        "same_condition_auc": same_auc,
        "free_image_auc": free_auc,
        "relation_balanced_accuracy": relation_balanced,
        "dimension_median_absolute_error": float(
            dimensions["absolute_error"].median()
        ),
        "principal_angle_median_absolute_error": float(
            ready["principal_angle_error"].median()
        ),
        "graph_edge_f1": float(
            graph_primary["excess_edge_f1"].mean()
        ),
        "cross_view_graph_jaccard": float(
            graph_primary["cross_view_excess_jaccard"].mean()
        ),
        "false_positive_upper_95": _one_sided_upper(
            false_count,
            len(negative),
        ),
        "attack_refusal_rate": float(
            attack["predicted_relation"]
            .eq("NOT_IDENTIFIABLE")
            .mean()
        ),
        "rigid_invariance_rate": float(
            confirmation["rigid_invariant"].mean()
        ),
        "common_condition_excess_false_run_rate": float(
            graph_controls["any_false_excess"].mean()
        ),
    }


def _decision(
    headline: dict[str, float],
    config: dict[str, Any],
) -> dict[str, Any]:
    gates = config["gates"]
    checks = {
        "same_condition_auc": (
            headline["same_condition_auc"]
            >= float(gates["minimum_same_auc"])
        ),
        "free_image_auc": (
            headline["free_image_auc"]
            >= float(gates["minimum_free_auc"])
        ),
        "relation_balanced_accuracy": (
            headline["relation_balanced_accuracy"]
            >= float(gates["minimum_relation_balanced_accuracy"])
        ),
        "dimension_error": (
            headline["dimension_median_absolute_error"]
            <= float(gates[
                "maximum_dimension_median_absolute_error"
            ])
        ),
        "principal_angle_error": (
            headline["principal_angle_median_absolute_error"]
            <= float(gates[
                "maximum_principal_angle_median_absolute_error"
            ])
        ),
        "graph_edge_f1": (
            headline["graph_edge_f1"]
            >= float(gates["minimum_graph_edge_f1"])
        ),
        "cross_view_graph_jaccard": (
            headline["cross_view_graph_jaccard"]
            >= float(gates["minimum_cross_view_graph_jaccard"])
        ),
        "false_positive_control": (
            headline["false_positive_upper_95"]
            <= float(gates["maximum_false_positive_upper_95"])
        ),
        "attack_refusal": (
            headline["attack_refusal_rate"]
            >= float(gates["minimum_attack_refusal_rate"])
        ),
        "rigid_invariance": (
            headline["rigid_invariance_rate"]
            >= float(gates["minimum_rigid_invariance_rate"])
        ),
        "common_condition_excess_control": (
            headline["common_condition_excess_false_run_rate"]
            <= 0.03
        ),
    }
    if all(checks.values()):
        status = "V8_RESPONSE_SET_INCIDENCE_PLANTED_PASS"
    elif (
        checks["false_positive_control"]
        and checks["attack_refusal"]
    ):
        status = "V8_RESPONSE_SET_INCIDENCE_PARTIAL_BOUNDARY"
    else:
        status = "V8_RESPONSE_SET_INCIDENCE_STOP"
    return {
        "status": status,
        "checks": checks,
        "headline": headline,
        "claim_boundary": config["claim_boundary"],
    }


def _markdown_report(
    decision: dict[str, Any],
    thresholds: dict[str, float],
    world_summary: pd.DataFrame,
    dimension_summary: pd.DataFrame,
    graph_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
) -> str:
    return f"""# V8 Response-Set Incidence Planted Battery

## Decision

`{decision["status"]}`

## Registered object

```text
S_u = f_u(Z)
Gamma_u = {{(z, f_u(z))}}
d_same = inf_z ||f_u(z) - f_v(z)||
d_free = inf_z,z' ||f_u(z) - f_v(z')||
```

Same-condition and free-image incidence are separate estimands.

## Headline

```json
{json.dumps(decision["headline"], indent=2)}
```

## Frozen thresholds

```json
{json.dumps(thresholds, indent=2)}
```

## Primary worlds

{world_summary.to_markdown(index=False)}

## Finite-scale dimensions

{dimension_summary.to_markdown(index=False)}

## Direction-rich population graphs

{graph_summary.to_markdown(index=False)}

## Noise sensitivity

{sensitivity_summary.to_markdown(index=False)}

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Claim boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_response_set_incidence.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_response_set_incidence/v1",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = _read_json(args.config)
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 3
        config["calibration_repetitions"] = 6
        config["confirmation_repetitions"] = 8
        config["sensitivity_repetitions"] = 3
        config["dimension_repetitions"] = 1
        config["graph_repetitions"] = 3
        config["noise_scan"] = [0.03, 0.12]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    discovery = _run_pair_stage(
        config,
        stage="discovery",
        repetitions=int(config["discovery_repetitions"]),
        noise_sd=float(config["primary_noise_sd"]),
    )
    calibration = _run_pair_stage(
        config,
        stage="calibration",
        repetitions=int(config["calibration_repetitions"]),
        noise_sd=float(config["primary_noise_sd"]),
    )
    thresholds = _thresholds(calibration)
    confirmation_raw = _run_pair_stage(
        config,
        stage="confirmation",
        repetitions=int(config["confirmation_repetitions"]),
        noise_sd=float(config["primary_noise_sd"]),
    )
    confirmation = _apply_classifier(confirmation_raw, thresholds)
    sensitivity_parts = []
    for noise in config["noise_scan"]:
        raw = _run_pair_stage(
            config,
            stage="sensitivity",
            repetitions=int(config["sensitivity_repetitions"]),
            noise_sd=float(noise),
        )
        sensitivity_parts.append(_apply_classifier(raw, thresholds))
    sensitivity = pd.concat(sensitivity_parts, ignore_index=True)
    dimensions = _run_dimensions(config)
    graphs = _run_graphs(config, thresholds)
    headline = _headline(confirmation, dimensions, graphs)
    decision = _decision(headline, config)
    world_summary = _summary(confirmation)
    sensitivity_summary = _summary(sensitivity)
    dimension_summary = (
        dimensions.groupby(
            ["world", "ambient_dimensions", "expected_dimension"],
            as_index=False,
        )
        .agg(
            repetitions=("seed", "size"),
            estimated_dimension_median=("estimated_dimension", "median"),
            absolute_error_median=("absolute_error", "median"),
            scaling_r2_median=("scaling_r2", "median"),
        )
    )
    graph_summary = (
        graphs.groupby("world", as_index=False)
        .agg(
            repetitions=("seed", "size"),
            raw_edge_f1=("raw_edge_f1", "mean"),
            excess_edge_f1=("excess_edge_f1", "mean"),
            false_excess_run_rate=("any_false_excess", "mean"),
            cross_view_excess_jaccard=(
                "cross_view_excess_jaccard",
                "mean",
            ),
            oracle_raw_edges=("oracle_raw_edges", "mean"),
            predicted_raw_edges=("predicted_raw_edges", "mean"),
            predicted_excess_edges=("predicted_excess_edges", "mean"),
            union_box_dimension=("union_box_dimension", "mean"),
        )
    )
    discovery.to_csv(
        args.output_dir / "discovery_metrics.csv",
        index=False,
    )
    calibration.to_csv(
        args.output_dir / "calibration_metrics.csv",
        index=False,
    )
    confirmation.to_csv(
        args.output_dir / "confirmation_metrics.csv",
        index=False,
    )
    sensitivity.to_csv(
        args.output_dir / "sensitivity_metrics.csv",
        index=False,
    )
    dimensions.to_csv(
        args.output_dir / "dimension_metrics.csv",
        index=False,
    )
    graphs.to_csv(
        args.output_dir / "graph_metrics.csv",
        index=False,
    )
    world_summary.to_csv(
        args.output_dir / "world_summary.csv",
        index=False,
    )
    sensitivity_summary.to_csv(
        args.output_dir / "sensitivity_summary.csv",
        index=False,
    )
    dimension_summary.to_csv(
        args.output_dir / "dimension_summary.csv",
        index=False,
    )
    graph_summary.to_csv(
        args.output_dir / "graph_summary.csv",
        index=False,
    )
    _write_json(args.output_dir / "thresholds.json", thresholds)
    _write_json(args.output_dir / "decision.json", decision)
    _write_json(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _markdown_report(
            decision,
            thresholds,
            world_summary,
            dimension_summary,
            graph_summary,
            sensitivity_summary,
        ),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_response_set_incidence.py",
            Path(__file__),
        ],
        estimand_id="V8_RESPONSE_SET_INCIDENCE_PLANTED_AFFINE_V1",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps({
        "status": decision["status"],
        "output_dir": str(args.output_dir),
        "headline": headline,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
