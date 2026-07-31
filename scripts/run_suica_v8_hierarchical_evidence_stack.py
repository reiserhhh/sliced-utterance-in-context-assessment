#!/usr/bin/env python3
"""Test source-selected routes through frozen V8 evidence layers on PANDORA."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_pandora_external_connection import (  # noqa: E402
    _eligible,
    _source_paths,
)
from suica_core.v8_external_connection import (  # noqa: E402
    BIG5_TRAITS,
    MBTI_AXES,
    bridge_permutation_p,
    matrix_alignment,
    relation_matrix,
    safe_pearson,
)
from suica_core.v8_hierarchical_routing import (  # noqa: E402
    EvidenceLayer,
    TaskRoute,
    fit_selected_route_predict,
    run_nested_route_cv,
    select_source_route,
    validate_hierarchy,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_hierarchical_evidence_stack.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_hierarchical_evidence_stack"
    / "pandora_ready_20260728"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_HIERARCHICAL_EVIDENCE_STACK_PANDORA.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(
            "/Volumes/mobile3/projects/project persona/"
            "data_sets/prepared/pandora_official"
        ),
    )
    parser.add_argument(
        "--bridge-permutations",
        type=int,
        default=0,
        help="Override the configured count for a bounded smoke run.",
    )
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _pseudonym(value: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}::{value}".encode("utf-8")).hexdigest()[:24]


def _pseudonymize(frame: pd.DataFrame, *, salt: str) -> pd.DataFrame:
    output = frame.copy()
    output["pseudonymous_id"] = output["user_id"].astype(str).map(
        lambda value: _pseudonym(value, salt)
    )
    return output.drop(columns="user_id")


def _load_source_labels_without_bridge_values(
    paths: dict[str, Path],
    *,
    salt: str,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, Any]]:
    """Load source labels while reading only bridge IDs for cohort exclusion."""
    bridge_ids = set(
        pd.read_csv(
            paths["bridge"],
            usecols=["user_id"],
            dtype={"user_id": str},
        )["user_id"].astype(str)
    )
    big5 = pd.read_csv(
        paths["big5"],
        usecols=["user_id", "official_fold", *BIG5_TRAITS],
        dtype={"user_id": str},
    )
    raw_big5_ids = set(big5["user_id"].astype(str))
    big5 = big5.loc[~big5["user_id"].isin(bridge_ids)].copy()
    mbti: dict[str, pd.DataFrame] = {}
    for axis in MBTI_AXES:
        frame = pd.read_csv(
            paths[axis],
            usecols=["user_id", "official_fold", "positive_probability"],
            dtype={"user_id": str},
        )
        frame = frame.loc[
            ~frame["user_id"].isin(raw_big5_ids | bridge_ids)
        ].copy()
        mbti[axis] = _pseudonymize(
            frame.rename(columns={"positive_probability": axis}),
            salt=salt,
        )
    return _pseudonymize(big5, salt=salt), mbti, {
        "bridge_file_columns_read": ["user_id"],
        "bridge_values_read": False,
        "big5_source_rows": int(len(big5)),
        "mbti_source_rows": {
            axis: int(len(frame))
            for axis, frame in mbti.items()
        },
    }


def _load_bridge_values_after_freeze(
    path: Path,
    *,
    salt: str,
) -> pd.DataFrame:
    frame = pd.read_csv(
        path,
        usecols=["user_id", "bridge_fold", *BIG5_TRAITS, *MBTI_AXES],
        dtype={"user_id": str},
    )
    return _pseudonymize(frame, salt=salt)


def _layers(score: pd.DataFrame) -> dict[str, EvidenceLayer]:
    upstream = tuple(
        sorted(column for column in score if column.startswith("v7_author_"))
    )
    canonical = tuple(
        sorted(column for column in score if column.startswith("v8_csr_"))
    )
    opportunity = tuple(
        sorted(column for column in score if column.startswith("nuisance_"))
    )
    layers = {
        "upstream48": EvidenceLayer(
            name="upstream48",
            level="L2_UPSTREAM_AUTHOR_REPRESENTATION",
            columns=upstream,
            estimand="Frozen upstream author representation before canonical contraction.",
        ),
        "canonical16": EvidenceLayer(
            name="canonical16",
            level="L2C_INVARIANT_RELATIONAL_GEOMETRY",
            columns=canonical,
            estimand="Frozen row-scale-invariant landmark-distance shape.",
        ),
        "opportunity": EvidenceLayer(
            name="opportunity",
            level="L2O_CONDITION_AND_OBSERVATION_SURFACE",
            columns=opportunity,
            estimand="Observed amount, unit distribution, and format opportunity.",
        ),
    }
    if not all(layer.columns for layer in layers.values()):
        raise RuntimeError("Frozen score table is missing a declared evidence layer.")
    return layers


def _routes(config: dict[str, Any]) -> list[TaskRoute]:
    return [
        TaskRoute(name=str(name), layers=tuple(layer_names))
        for name, layer_names in config["routes"].items()
    ]


def _aggregate_direct(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for (cohort, view, task), group in summary.groupby(
        ["cohort", "view", "task"],
        observed=True,
    ):
        row: dict[str, Any] = {
            "cohort": str(cohort),
            "view": str(view),
            "task": str(task),
            "targets": int(len(group)),
            "n_min": int(group["n"].min()),
            "n_max": int(group["n"].max()),
        }
        if task == "continuous":
            row["mean_pearson_r"] = float(group["pearson_r"].mean())
            row["mean_mae"] = float(group["mae"].mean())
            row["mean_rmse"] = float(group["rmse"].mean())
        else:
            row["mean_roc_auc"] = float(group["roc_auc"].mean())
            row["mean_balanced_accuracy"] = float(
                group["balanced_accuracy"].mean()
            )
            row["mean_macro_f1"] = float(group["macro_f1"].mean())
        rows.append(row)
    return pd.DataFrame(rows)


def _metric(
    truth: np.ndarray,
    prediction: np.ndarray,
    *,
    task: str,
) -> float:
    if task == "continuous":
        return float(safe_pearson(prediction, truth)[0])
    labels = truth.astype(int)
    return (
        float(roc_auc_score(labels, prediction))
        if len(np.unique(labels)) == 2
        else float("nan")
    )


def _prediction_arrays(
    predictions: pd.DataFrame,
    *,
    cohort: str,
    views: Iterable[str],
) -> tuple[list[str], list[str], dict[str, dict[str, tuple[np.ndarray, np.ndarray]]]]:
    frame = predictions.loc[predictions["cohort"].eq(cohort)].copy()
    targets = sorted(frame["target"].unique().tolist())
    view_names = list(views)
    identifiers: set[str] | None = None
    indexed: dict[tuple[str, str], pd.DataFrame] = {}
    for view in view_names:
        for target in targets:
            current = (
                frame.loc[
                    frame["view"].eq(view) & frame["target"].eq(target)
                ]
                .set_index("pseudonymous_id")
                .sort_index()
            )
            indexed[(view, target)] = current
            current_ids = set(current.index.astype(str))
            identifiers = (
                current_ids
                if identifiers is None
                else identifiers & current_ids
            )
    common = sorted(identifiers or [])
    if not common:
        raise RuntimeError(f"No common prediction authors for {cohort}.")
    arrays: dict[str, dict[str, tuple[np.ndarray, np.ndarray]]] = {}
    for view in view_names:
        arrays[view] = {}
        for target in targets:
            current = indexed[(view, target)].loc[common]
            arrays[view][target] = (
                current["true_value"].to_numpy(float),
                current["prediction"].to_numpy(float),
            )
    return common, targets, arrays


def _direct_bootstrap(
    predictions: pd.DataFrame,
    *,
    draws: int,
    seed: int,
) -> pd.DataFrame:
    comparisons = [("source_selected_router", "upstream_only")]
    rows: list[dict[str, Any]] = []
    for cohort, task in (
        ("big5_only_ready", "continuous"),
        ("mbti_only_ready", "binary"),
    ):
        identifiers, targets, arrays = _prediction_arrays(
            predictions,
            cohort=cohort,
            views={view for pair in comparisons for view in pair},
        )
        rng = np.random.default_rng(
            int(seed)
            + int(hashlib.sha256(cohort.encode()).hexdigest()[:8], 16)
        )
        for first, second in comparisons:
            first_point = np.nanmean([
                _metric(*arrays[first][target], task=task)
                for target in targets
            ])
            second_point = np.nanmean([
                _metric(*arrays[second][target], task=task)
                for target in targets
            ])
            values = []
            for _ in range(int(draws)):
                index = rng.integers(0, len(identifiers), len(identifiers))
                first_score = np.nanmean([
                    _metric(
                        arrays[first][target][0][index],
                        arrays[first][target][1][index],
                        task=task,
                    )
                    for target in targets
                ])
                second_score = np.nanmean([
                    _metric(
                        arrays[second][target][0][index],
                        arrays[second][target][1][index],
                        task=task,
                    )
                    for target in targets
                ])
                values.append(first_score - second_score)
            values_array = np.asarray(values, dtype=float)
            rows.append({
                "cohort": cohort,
                "task": task,
                "metric": (
                    "mean_pearson_r"
                    if task == "continuous"
                    else "mean_roc_auc"
                ),
                "view": first,
                "reference_view": second,
                "point_delta": float(first_point - second_point),
                "bootstrap_mean_delta": float(np.nanmean(values_array)),
                "ci_lower": float(np.nanquantile(values_array, 0.025)),
                "ci_upper": float(np.nanquantile(values_array, 0.975)),
                "draws": int(draws),
                "authors": int(len(identifiers)),
            })
    return pd.DataFrame(rows)


def _run_direct(
    *,
    scores: pd.DataFrame,
    big5: pd.DataFrame,
    mbti: dict[str, pd.DataFrame],
    layers: dict[str, EvidenceLayer],
    routes: list[TaskRoute],
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ready = _eligible(scores, "ready", minimum_units=12)
    big5_source = big5.merge(ready, on="pseudonymous_id", how="inner")
    route_views = [
        (route.name, [route])
        for route in routes
    ] + [("source_selected_router", routes)]
    summaries: list[dict[str, Any]] = []
    predictions: list[pd.DataFrame] = []
    selections: list[pd.DataFrame] = []
    for view, candidate_routes in route_views:
        for trait in BIG5_TRAITS:
            result = run_nested_route_cv(
                big5_source,
                layers=layers,
                routes=candidate_routes,
                target=trait,
                fold_column="official_fold",
                task="continuous",
                parameters=config["ridge_alphas"],
                view=view,
                cohort="big5_only_ready",
            )
            summaries.append(result.summary)
            predictions.append(result.predictions)
            selections.append(result.selections)
    for axis in MBTI_AXES:
        axis_source = mbti[axis].merge(
            ready,
            on="pseudonymous_id",
            how="inner",
        )
        for view, candidate_routes in route_views:
            result = run_nested_route_cv(
                axis_source,
                layers=layers,
                routes=candidate_routes,
                target=axis,
                fold_column="official_fold",
                task="binary",
                parameters=config["logistic_c"],
                view=view,
                cohort="mbti_only_ready",
            )
            summaries.append(result.summary)
            predictions.append(result.predictions)
            selections.append(result.selections)
    return (
        pd.DataFrame(summaries),
        pd.concat(predictions, ignore_index=True),
        pd.concat(selections, ignore_index=True),
    )


def _select_final_source_routes(
    *,
    scores: pd.DataFrame,
    big5: pd.DataFrame,
    mbti: dict[str, pd.DataFrame],
    layers: dict[str, EvidenceLayer],
    routes: list[TaskRoute],
    config: dict[str, Any],
) -> pd.DataFrame:
    """Freeze all source-only route choices before bridge values are loaded."""
    ready = _eligible(scores, "ready", minimum_units=12)
    big5_source = big5.merge(ready, on="pseudonymous_id", how="inner")
    mbti_source = {
        axis: frame.merge(ready, on="pseudonymous_id", how="inner")
        for axis, frame in mbti.items()
    }
    route_views = [
        (route.name, [route])
        for route in routes
    ] + [("source_selected_router", routes)]
    rows: list[dict[str, Any]] = []
    for view, candidate_routes in route_views:
        for trait in BIG5_TRAITS:
            selected, _ = select_source_route(
                big5_source,
                layers=layers,
                routes=candidate_routes,
                target=trait,
                fold_column="official_fold",
                task="continuous",
                parameters=config["ridge_alphas"],
            )
            rows.append({
                "view": view,
                "cohort": "strict_bridge_ready",
                "target": trait,
                "task": "continuous",
                "selected_route": str(selected["route"]),
                "selected_layers": str(selected["layers"]),
                "selected_parameter": float(selected["parameter"]),
                "inner_score": float(selected["inner_score"]),
                "source_n": int(selected["inner_n"]),
                "selection_scope": "big5_only_official_folds",
                "bridge_values_read": False,
            })
        for axis in MBTI_AXES:
            selected, _ = select_source_route(
                mbti_source[axis],
                layers=layers,
                routes=candidate_routes,
                target=axis,
                fold_column="official_fold",
                task="binary",
                parameters=config["logistic_c"],
            )
            rows.append({
                "view": view,
                "cohort": "strict_bridge_ready",
                "target": axis,
                "task": "binary",
                "selected_route": str(selected["route"]),
                "selected_layers": str(selected["layers"]),
                "selected_parameter": float(selected["parameter"]),
                "inner_score": float(selected["inner_score"]),
                "source_n": int(selected["inner_n"]),
                "selection_scope": "mbti_only_official_folds",
                "bridge_values_read": False,
            })
    return pd.DataFrame(rows)


def _correlation(first: np.ndarray, second: np.ndarray) -> float:
    return float(safe_pearson(first, second)[0])


def _run_bridge(
    *,
    scores: pd.DataFrame,
    big5: pd.DataFrame,
    mbti: dict[str, pd.DataFrame],
    bridge: pd.DataFrame,
    layers: dict[str, EvidenceLayer],
    routes: list[TaskRoute],
    final_routes: pd.DataFrame,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ready = _eligible(scores, "ready", minimum_units=12)
    big5_source = big5.merge(ready, on="pseudonymous_id", how="inner")
    mbti_source = {
        axis: frame.merge(ready, on="pseudonymous_id", how="inner")
        for axis, frame in mbti.items()
    }
    destination = bridge.merge(ready, on="pseudonymous_id", how="inner")
    route_map = {route.name: route for route in routes}
    route_views = [*route_map, "source_selected_router"]
    true_matrix = relation_matrix(
        destination,
        big5_columns=BIG5_TRAITS,
        mbti_columns=MBTI_AXES,
    )
    summary_rows: list[dict[str, Any]] = []
    matrix_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    for view in route_views:
        predicted = destination[
            ["pseudonymous_id", *BIG5_TRAITS, *MBTI_AXES]
        ].copy()
        for trait in BIG5_TRAITS:
            selection = final_routes.loc[
                final_routes["view"].eq(view)
                & final_routes["target"].eq(trait)
            ]
            if len(selection) != 1:
                raise RuntimeError(f"Missing frozen route for {view}/{trait}.")
            selected = selection.iloc[0]
            values = fit_selected_route_predict(
                big5_source,
                destination,
                layers=layers,
                route=route_map[str(selected["selected_route"])],
                target=trait,
                fold_column="official_fold",
                task="continuous",
                parameter=float(selected["selected_parameter"]),
            )
            predicted[f"pred_{trait}"] = values
        for axis in MBTI_AXES:
            selection = final_routes.loc[
                final_routes["view"].eq(view)
                & final_routes["target"].eq(axis)
            ]
            if len(selection) != 1:
                raise RuntimeError(f"Missing frozen route for {view}/{axis}.")
            selected = selection.iloc[0]
            values = fit_selected_route_predict(
                mbti_source[axis],
                destination,
                layers=layers,
                route=route_map[str(selected["selected_route"])],
                target=axis,
                fold_column="official_fold",
                task="binary",
                parameter=float(selected["selected_parameter"]),
            )
            predicted[f"pred_{axis}"] = values
        predicted_big5 = [f"pred_{trait}" for trait in BIG5_TRAITS]
        predicted_mbti = [f"pred_{axis}" for axis in MBTI_AXES]
        predicted_matrix = relation_matrix(
            predicted,
            big5_columns=predicted_big5,
            mbti_columns=predicted_mbti,
        )
        alignment = matrix_alignment(predicted_matrix, true_matrix)
        permutation_p = bridge_permutation_p(
            predicted,
            predicted_big5=predicted_big5,
            predicted_mbti=predicted_mbti,
            observed_matrix=true_matrix,
            observed_alignment=alignment["element_r"],
            permutations=int(config["bridge_permutations"]),
            seed=int(config["seed"]),
        )
        summary_rows.append({
            "cohort": "strict_bridge_ready",
            "view": view,
            "n": int(len(predicted)),
            **alignment,
            "permutation_p": permutation_p,
            "mean_bridge_big5_r": float(np.mean([
                _correlation(
                    predicted[trait].to_numpy(float),
                    predicted[f"pred_{trait}"].to_numpy(float),
                )
                for trait in BIG5_TRAITS
            ])),
            "mean_bridge_mbti_auc": float(np.mean([
                roc_auc_score(
                    predicted[axis].to_numpy(int),
                    predicted[f"pred_{axis}"].to_numpy(float),
                )
                for axis in MBTI_AXES
            ])),
        })
        for matrix_name, matrix in (
            ("true", true_matrix),
            ("predicted", predicted_matrix),
        ):
            for row, trait in enumerate(BIG5_TRAITS):
                for column, axis in enumerate(MBTI_AXES):
                    matrix_rows.append({
                        "cohort": "strict_bridge_ready",
                        "view": view,
                        "matrix": matrix_name,
                        "big5_trait": trait,
                        "mbti_axis": axis,
                        "pearson_r": float(matrix[row, column]),
                    })
        export = predicted.copy()
        export["view"] = view
        export["cohort"] = "strict_bridge_ready"
        prediction_frames.append(export)
    return (
        pd.DataFrame(summary_rows),
        pd.DataFrame(matrix_rows),
        pd.concat(prediction_frames, ignore_index=True),
    )


def _bridge_bootstrap(
    predictions: pd.DataFrame,
    summary: pd.DataFrame,
    *,
    draws: int,
    seed: int,
) -> pd.DataFrame:
    views = ("source_selected_router", "upstream_only")
    frames = {
        view: predictions.loc[predictions["view"].eq(view)]
        .sort_values("pseudonymous_id")
        .reset_index(drop=True)
        for view in views
    }
    identifiers = frames[views[0]]["pseudonymous_id"].astype(str).tolist()
    if frames[views[1]]["pseudonymous_id"].astype(str).tolist() != identifiers:
        raise RuntimeError("Bridge router and reference rows are not aligned.")
    columns = [
        *BIG5_TRAITS,
        *MBTI_AXES,
        *[f"pred_{value}" for value in (*BIG5_TRAITS, *MBTI_AXES)],
    ]
    arrays = {
        view: {
            column: frames[view][column].to_numpy(float)
            for column in columns
        }
        for view in views
    }

    def vector(
        values: dict[str, np.ndarray],
        index: np.ndarray,
        *,
        predicted: bool,
    ) -> np.ndarray:
        prefix = "pred_" if predicted else ""
        return np.asarray([
            _correlation(
                values[f"{prefix}{trait}"][index],
                values[f"{prefix}{axis}"][index],
            )
            for trait in BIG5_TRAITS
            for axis in MBTI_AXES
        ])

    rng = np.random.default_rng(seed)
    deltas = []
    for _ in range(int(draws)):
        index = rng.integers(0, len(identifiers), len(identifiers))
        truth = vector(arrays[views[0]], index, predicted=False)
        routed = vector(arrays[views[0]], index, predicted=True)
        upstream = vector(arrays[views[1]], index, predicted=True)
        deltas.append(
            _correlation(routed, truth) - _correlation(upstream, truth)
        )
    points = summary.set_index("view")["element_r"]
    values = np.asarray(deltas, dtype=float)
    return pd.DataFrame([{
        "cohort": "strict_bridge_ready",
        "metric": "element_r",
        "view": views[0],
        "reference_view": views[1],
        "point_delta": float(points.loc[views[0]] - points.loc[views[1]]),
        "bootstrap_mean_delta": float(np.nanmean(values)),
        "ci_lower": float(np.nanquantile(values, 0.025)),
        "ci_upper": float(np.nanquantile(values, 0.975)),
        "draws": int(draws),
        "authors": int(len(identifiers)),
        "uncertainty_scope": "bridge_authors_conditional_on_source_fitted_heads",
    }])


def _route_stability(
    outer_selections: pd.DataFrame,
    final_routes: pd.DataFrame,
) -> pd.DataFrame:
    """Summarize fold-to-fold route recurrence without hiding instability."""
    outer = outer_selections.loc[
        outer_selections["view"].eq("source_selected_router")
    ].copy()
    final = final_routes.loc[
        final_routes["view"].eq("source_selected_router")
    ].set_index(["task", "target"])
    rows: list[dict[str, Any]] = []
    for (task, target), group in outer.groupby(
        ["task", "target"],
        observed=True,
    ):
        counts = group["selected_route"].value_counts()
        modal_count = int(counts.max())
        modal_routes = sorted(
            counts.loc[counts.eq(modal_count)].index.astype(str).tolist()
        )
        modal_route = modal_routes[0]
        probabilities = counts.to_numpy(float) / float(counts.sum())
        entropy = float(
            -np.sum(probabilities * np.log2(np.maximum(probabilities, 1e-12)))
        )
        final_row = final.loc[(task, target)]
        rows.append({
            "task": str(task),
            "target": str(target),
            "outer_folds": int(len(group)),
            "distinct_outer_routes": int(len(counts)),
            "modal_route": modal_route,
            "modal_share": float(modal_count / len(group)),
            "route_entropy_bits": entropy,
            "outer_route_counts_json": json.dumps(
                {str(key): int(value) for key, value in counts.items()},
                sort_keys=True,
            ),
            "full_source_selected_route": str(final_row["selected_route"]),
            "full_source_matches_unique_modal": bool(
                len(modal_routes) == 1
                and str(final_row["selected_route"]) == modal_route
            ),
        })
    return pd.DataFrame(rows).sort_values(
        ["task", "target"]
    ).reset_index(drop=True)


def _bridge_head_refit_bootstrap(
    *,
    scores: pd.DataFrame,
    big5: pd.DataFrame,
    mbti: dict[str, pd.DataFrame],
    bridge: pd.DataFrame,
    layers: dict[str, EvidenceLayer],
    routes: list[TaskRoute],
    final_routes: pd.DataFrame,
    bridge_summary: pd.DataFrame,
    draws: int,
    seed: int,
) -> pd.DataFrame:
    """Refit frozen source routes under source and bridge author bootstrap."""
    ready = _eligible(scores, "ready", minimum_units=12)
    big5_source = (
        big5.merge(ready, on="pseudonymous_id", how="inner")
        .sort_values("pseudonymous_id")
        .reset_index(drop=True)
    )
    mbti_source = {
        axis: frame.merge(ready, on="pseudonymous_id", how="inner")
        .sort_values("pseudonymous_id")
        .reset_index(drop=True)
        for axis, frame in mbti.items()
    }
    common_mbti_ids = mbti_source[MBTI_AXES[0]][
        "pseudonymous_id"
    ].astype(str).tolist()
    if any(
        frame["pseudonymous_id"].astype(str).tolist() != common_mbti_ids
        for frame in mbti_source.values()
    ):
        raise RuntimeError("MBTI source axes are not author-aligned.")
    destination = (
        bridge.merge(ready, on="pseudonymous_id", how="inner")
        .sort_values("pseudonymous_id")
        .reset_index(drop=True)
    )
    route_map = {route.name: route for route in routes}
    selections = final_routes.set_index(["view", "target"])
    views = ("source_selected_router", "upstream_only")
    rng = np.random.default_rng(seed)
    samples = {view: [] for view in views}
    for _ in range(int(draws)):
        big5_index = rng.integers(
            0,
            len(big5_source),
            len(big5_source),
        )
        mbti_index = rng.integers(
            0,
            len(common_mbti_ids),
            len(common_mbti_ids),
        )
        bridge_index = rng.integers(
            0,
            len(destination),
            len(destination),
        )
        big5_boot = big5_source.iloc[big5_index].reset_index(drop=True)
        mbti_boot = {
            axis: frame.iloc[mbti_index].reset_index(drop=True)
            for axis, frame in mbti_source.items()
        }
        truth = relation_matrix(
            destination.iloc[bridge_index],
            big5_columns=BIG5_TRAITS,
            mbti_columns=MBTI_AXES,
        )
        for view in views:
            predicted = destination[
                ["pseudonymous_id", *BIG5_TRAITS, *MBTI_AXES]
            ].copy()
            for trait in BIG5_TRAITS:
                selected = selections.loc[(view, trait)]
                predicted[f"pred_{trait}"] = fit_selected_route_predict(
                    big5_boot,
                    destination,
                    layers=layers,
                    route=route_map[str(selected["selected_route"])],
                    target=trait,
                    fold_column="official_fold",
                    task="continuous",
                    parameter=float(selected["selected_parameter"]),
                )
            for axis in MBTI_AXES:
                selected = selections.loc[(view, axis)]
                predicted[f"pred_{axis}"] = fit_selected_route_predict(
                    mbti_boot[axis],
                    destination,
                    layers=layers,
                    route=route_map[str(selected["selected_route"])],
                    target=axis,
                    fold_column="official_fold",
                    task="binary",
                    parameter=float(selected["selected_parameter"]),
                )
            predicted_matrix = relation_matrix(
                predicted.iloc[bridge_index],
                big5_columns=[f"pred_{trait}" for trait in BIG5_TRAITS],
                mbti_columns=[f"pred_{axis}" for axis in MBTI_AXES],
            )
            samples[view].append(
                float(matrix_alignment(predicted_matrix, truth)["element_r"])
            )
    points = bridge_summary.set_index("view")["element_r"]
    rows: list[dict[str, Any]] = []
    for view in views:
        values = np.asarray(samples[view], dtype=float)
        rows.append({
            "kind": "absolute",
            "view": view,
            "reference_view": None,
            "point_estimate": float(points.loc[view]),
            "point_delta": None,
            "bootstrap_mean": float(np.nanmean(values)),
            "ci_lower": float(np.nanquantile(values, 0.025)),
            "ci_upper": float(np.nanquantile(values, 0.975)),
            "draws": int(draws),
            "bridge_authors": int(len(destination)),
            "big5_source_authors": int(len(big5_source)),
            "mbti_source_authors": int(len(common_mbti_ids)),
            "uncertainty_scope": (
                "source_head_refit_and_bridge_author_resample_"
                "conditional_on_frozen_route_and_parameter"
            ),
        })
    difference = (
        np.asarray(samples["source_selected_router"], dtype=float)
        - np.asarray(samples["upstream_only"], dtype=float)
    )
    rows.append({
        "kind": "paired_delta",
        "view": "source_selected_router",
        "reference_view": "upstream_only",
        "point_estimate": None,
        "point_delta": float(
            points.loc["source_selected_router"]
            - points.loc["upstream_only"]
        ),
        "bootstrap_mean": float(np.nanmean(difference)),
        "ci_lower": float(np.nanquantile(difference, 0.025)),
        "ci_upper": float(np.nanquantile(difference, 0.975)),
        "draws": int(draws),
        "bridge_authors": int(len(destination)),
        "big5_source_authors": int(len(big5_source)),
        "mbti_source_authors": int(len(common_mbti_ids)),
        "uncertainty_scope": (
            "source_head_refit_and_bridge_author_resample_"
            "conditional_on_frozen_route_and_parameter"
        ),
    })
    return pd.DataFrame(rows)


def _fmt(value: Any, digits: int = 3) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "NA"
    return f"{number:.{digits}f}" if np.isfinite(number) else "NA"


def _report(
    *,
    config: dict[str, Any],
    aggregate: pd.DataFrame,
    selections: pd.DataFrame,
    final_routes: pd.DataFrame,
    route_stability: pd.DataFrame,
    direct_bootstrap: pd.DataFrame,
    bridge_summary: pd.DataFrame,
    bridge_bootstrap: pd.DataFrame,
    bridge_head_refit: pd.DataFrame,
    decision: dict[str, Any],
) -> str:
    big5 = aggregate.loc[aggregate["task"].eq("continuous")].set_index("view")
    mbti = aggregate.loc[aggregate["task"].eq("binary")].set_index("view")
    bridge = bridge_summary.set_index("view")
    route_order = [
        *config["routes"].keys(),
        "source_selected_router",
    ]
    lines = [
        "# SUICA V8 Hierarchical Evidence Stack: PANDORA Routing",
        "",
        f"Status: `{decision['status']}`",
        "",
        "## Contract",
        "",
        "The experiment keeps three frozen evidence objects separate: the "
        "information-rich upstream author representation, invariant canonical "
        "geometry, and observation/opportunity surface. A task head may read "
        "more than one layer, but that design matrix is ephemeral and is not "
        "exported as a universal person score.",
        "",
        "Every outer-fold route and model parameter was selected by nested "
        "source-only official folds. Final bridge routes were selected on "
        "Big5-only or MBTI-only official folds, serialized, and hash-frozen. "
        "Bridge values were loaded only after that freeze existed.",
        "",
        f"Claim boundary: {config['claim_boundary']}",
        "",
        "## Direct source-task results",
        "",
        "| Route | Big5 mean r | MBTI mean AUC | Bridge element r | "
        "Bridge permutation p |",
        "|---|---:|---:|---:|---:|",
    ]
    for view in route_order:
        lines.append(
            f"| {view} | {_fmt(big5.loc[view, 'mean_pearson_r'])} | "
            f"{_fmt(mbti.loc[view, 'mean_roc_auc'])} | "
            f"{_fmt(bridge.loc[view, 'element_r'])} | "
            f"{_fmt(bridge.loc[view, 'permutation_p'], 4)} |"
        )
    lines.extend([
        "",
        "## Source-selected routes",
        "",
        "| Target | Task | Selected route | Layers | Source CV score |",
        "|---|---|---|---|---:|",
    ])
    routed = final_routes.loc[
        final_routes["view"].eq("source_selected_router")
    ].sort_values(["task", "target"])
    for row in routed.itertuples(index=False):
        lines.append(
            f"| {row.target} | {row.task} | {row.selected_route} | "
            f"{row.selected_layers} | {_fmt(row.inner_score)} |"
        )
    lines.extend([
        "",
        "## Route stability",
        "",
        "| Target | Distinct outer routes | Modal route | Modal share | "
        "Entropy (bits) | Full-source match |",
        "|---|---:|---|---:|---:|---|",
    ])
    for row in route_stability.itertuples(index=False):
        lines.append(
            f"| {row.target} | {row.distinct_outer_routes} | "
            f"{row.modal_route} | {_fmt(row.modal_share)} | "
            f"{_fmt(row.route_entropy_bits)} | "
            f"{str(bool(row.full_source_matches_unique_modal)).lower()} |"
        )
    lines.extend([
        "",
        "Route instability is measurement evidence rather than hidden by a "
        "majority vote.",
        "",
        "## Uncertainty and decision",
        "",
    ])
    for row in direct_bootstrap.itertuples(index=False):
        lines.append(
            f"- {row.cohort}: router minus upstream "
            f"{_fmt(row.point_delta)}, 95% paired-bootstrap CI "
            f"[{_fmt(row.ci_lower)}, {_fmt(row.ci_upper)}]."
        )
    bridge_delta = bridge_bootstrap.iloc[0]
    head_refit_router = bridge_head_refit.loc[
        (bridge_head_refit["kind"].eq("absolute"))
        & (bridge_head_refit["view"].eq("source_selected_router"))
    ].iloc[0]
    head_refit_delta = bridge_head_refit.loc[
        bridge_head_refit["kind"].eq("paired_delta")
    ].iloc[0]
    lines.extend([
        f"- Bridge structure: router minus upstream "
        f"{_fmt(bridge_delta['point_delta'])}, conditional author-bootstrap CI "
        f"[{_fmt(bridge_delta['ci_lower'])}, "
        f"{_fmt(bridge_delta['ci_upper'])}].",
        f"- Bridge with source-head refit: router absolute 95% CI "
        f"[{_fmt(head_refit_router['ci_lower'])}, "
        f"{_fmt(head_refit_router['ci_upper'])}]; router minus upstream "
        f"CI [{_fmt(head_refit_delta['ci_lower'])}, "
        f"{_fmt(head_refit_delta['ci_upper'])}].",
        f"- Distinct final source-selected routes: "
        f"{decision['gates']['distinct_final_routes']['observed']}.",
        f"- Decision: `{decision['status']}`.",
        "",
        "## Interpretation boundary",
        "",
        "- Route heterogeneity supports task-specific access to frozen evidence "
        "levels; it does not prove that the levels are psychological stages.",
        "- Concatenation occurs only inside a declared task head. No combined "
        "feature vector is promoted as the next SUICA score.",
        "- The upstream representation and canonical geometry are deterministic "
        "relatives, so a route comparison is about useful resolution, not "
        "independent causal channels.",
        "- PANDORA labels were already opened. This experiment is exploratory.",
        "- The conditional bridge-author bootstrap keeps source heads fixed. The "
        "separate 200-draw source-head-refit bootstrap includes source-fit and "
        "bridge-author uncertainty, but remains conditional on the frozen routes "
        "and model parameters.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/run_suica_v8_hierarchical_evidence_stack.py",
        "```",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    config_path = args.config if args.config.is_absolute() else ROOT / args.config
    output_dir = (
        args.output_dir if args.output_dir.is_absolute() else ROOT / args.output_dir
    )
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    config = _read_json(config_path)
    if args.bridge_permutations > 0:
        config["bridge_permutations"] = int(args.bridge_permutations)
    external_config_path = ROOT / config["external_connection_config"]
    external_config = _read_json(external_config_path)
    score_root = ROOT / config["score_output"]
    manifest_path = score_root / "score_manifest.json"
    manifest = _read_json(manifest_path)
    score_path = ROOT / manifest["score_table"]
    if _sha256(score_path) != manifest["score_table_sha256"]:
        raise RuntimeError("REFUSE_BUNDLE_HASH_MISMATCH")
    scores = pd.read_parquet(score_path)
    layers = _layers(scores)
    routes = _routes(config)
    validate_hierarchy(layers, routes)
    paths = _source_paths(args.data_root)
    salt = str(external_config["score"]["pseudonym_salt"])
    big5, mbti, source_load_audit = _load_source_labels_without_bridge_values(
        paths,
        salt=salt,
    )
    direct_summary, direct_predictions, outer_selections = _run_direct(
        scores=scores,
        big5=big5,
        mbti=mbti,
        layers=layers,
        routes=routes,
        config=config,
    )
    final_routes = _select_final_source_routes(
        scores=scores,
        big5=big5,
        mbti=mbti,
        layers=layers,
        routes=routes,
        config=config,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    route_path = output_dir / "source_final_route_selections.csv"
    final_routes.to_csv(route_path, index=False)
    route_freeze = {
        "version": config["version"],
        "stage": "SOURCE_ROUTES_FROZEN_BEFORE_BRIDGE_VALUES",
        "created_utc": datetime.now(UTC).isoformat(),
        "bridge_values_read": False,
        "source_load_audit": source_load_audit,
        "config_sha256": _sha256(config_path),
        "score_table_sha256": manifest["score_table_sha256"],
        "route_table": str(route_path.relative_to(ROOT)),
        "route_table_sha256": _sha256(route_path),
        "route_rows": int(len(final_routes)),
        "source_selected_route_rows": int(
            final_routes["view"].eq("source_selected_router").sum()
        ),
        "claim_boundary": config["claim_boundary"],
    }
    route_freeze_path = output_dir / "source_route_freeze.json"
    _write_json(route_freeze_path, route_freeze)
    route_freeze_sha256 = _sha256(route_freeze_path)
    bridge = _load_bridge_values_after_freeze(paths["bridge"], salt=salt)
    if _sha256(route_path) != route_freeze["route_table_sha256"]:
        raise RuntimeError("REFUSE_ROUTE_FREEZE_HASH_MISMATCH")
    big5_overlap = set(big5["pseudonymous_id"]) & set(
        bridge["pseudonymous_id"]
    )
    mbti_overlap = set().union(
        *[set(frame["pseudonymous_id"]) for frame in mbti.values()]
    ) & set(bridge["pseudonymous_id"])
    if big5_overlap or mbti_overlap:
        raise RuntimeError("Source heads overlap strict bridge users.")
    aggregate = _aggregate_direct(direct_summary)
    direct_bootstrap = _direct_bootstrap(
        direct_predictions,
        draws=int(config["direct_bootstrap_draws"]),
        seed=int(config["seed"]),
    )
    bridge_summary, bridge_matrices, bridge_predictions = _run_bridge(
        scores=scores,
        big5=big5,
        mbti=mbti,
        bridge=bridge,
        layers=layers,
        routes=routes,
        final_routes=final_routes,
        config=config,
    )
    bridge_bootstrap = _bridge_bootstrap(
        bridge_predictions,
        bridge_summary,
        draws=int(config["bridge_bootstrap_draws"]),
        seed=int(config["seed"]),
    )
    route_stability = _route_stability(outer_selections, final_routes)
    bridge_head_refit = _bridge_head_refit_bootstrap(
        scores=scores,
        big5=big5,
        mbti=mbti,
        bridge=bridge,
        layers=layers,
        routes=routes,
        final_routes=final_routes,
        bridge_summary=bridge_summary,
        draws=int(config["bridge_head_refit_draws"]),
        seed=int(config["seed"]) + 9091,
    )
    routed_final = final_routes.loc[
        final_routes["view"].eq("source_selected_router")
    ]
    direct_delta = direct_bootstrap.set_index("cohort")
    bridge_delta = bridge_bootstrap.iloc[0]
    head_refit_router = bridge_head_refit.loc[
        (bridge_head_refit["kind"].eq("absolute"))
        & (bridge_head_refit["view"].eq("source_selected_router"))
    ].iloc[0]
    margin = float(config["noninferiority_margin"])
    bridge_margin = float(config["bridge_noninferiority_margin"])
    gates = {
        "distinct_final_routes": {
            "observed": int(routed_final["selected_route"].nunique()),
            "threshold": 2,
            "pass": bool(routed_final["selected_route"].nunique() >= 2),
        },
        "big5_router_noninferior_to_upstream": {
            "observed_ci_lower": float(
                direct_delta.loc["big5_only_ready", "ci_lower"]
            ),
            "threshold": -margin,
            "pass": bool(
                direct_delta.loc["big5_only_ready", "ci_lower"] >= -margin
            ),
        },
        "mbti_router_noninferior_to_upstream": {
            "observed_ci_lower": float(
                direct_delta.loc["mbti_only_ready", "ci_lower"]
            ),
            "threshold": -margin,
            "pass": bool(
                direct_delta.loc["mbti_only_ready", "ci_lower"] >= -margin
            ),
        },
        "router_bridge_noninferior_to_upstream": {
            "observed_ci_lower": float(bridge_delta["ci_lower"]),
            "threshold": -bridge_margin,
            "pass": bool(bridge_delta["ci_lower"] >= -bridge_margin),
        },
        "router_bridge_relation_detected": {
            "observed_p": float(
                bridge_summary.set_index("view").loc[
                    "source_selected_router",
                    "permutation_p",
                ]
            ),
            "threshold": 0.05,
            "pass": bool(
                bridge_summary.set_index("view").loc[
                    "source_selected_router",
                    "permutation_p",
                ]
                < 0.05
            ),
        },
        "router_bridge_survives_source_head_refit": {
            "observed_ci_lower": float(head_refit_router["ci_lower"]),
            "threshold": 0.0,
            "pass": bool(head_refit_router["ci_lower"] > 0.0),
        },
    }
    passed = sum(bool(value["pass"]) for value in gates.values())
    status = (
        "LAYER_SPECIALIZATION_SUPPORTED_EXPLORATORY"
        if passed == len(gates)
        else "LAYER_SPECIALIZATION_PARTIAL_EXPLORATORY"
    )
    direct_summary.to_csv(output_dir / "direct_summary_by_target.csv", index=False)
    aggregate.to_csv(output_dir / "direct_aggregate.csv", index=False)
    direct_predictions.to_parquet(
        output_dir / "direct_predictions.parquet",
        index=False,
    )
    outer_selections.to_csv(
        output_dir / "outer_fold_route_selections.csv",
        index=False,
    )
    route_stability.to_csv(
        output_dir / "route_stability.csv",
        index=False,
    )
    direct_bootstrap.to_csv(
        output_dir / "direct_router_bootstrap.csv",
        index=False,
    )
    bridge_summary.to_csv(output_dir / "bridge_summary.csv", index=False)
    bridge_matrices.to_csv(
        output_dir / "bridge_relation_matrices.csv",
        index=False,
    )
    bridge_predictions.to_parquet(
        output_dir / "bridge_predictions.parquet",
        index=False,
    )
    if _sha256(route_path) != route_freeze["route_table_sha256"]:
        raise RuntimeError("REFUSE_ROUTE_FREEZE_CHANGED_DURING_BRIDGE")
    bridge_bootstrap.to_csv(
        output_dir / "bridge_router_bootstrap.csv",
        index=False,
    )
    bridge_head_refit.to_csv(
        output_dir / "bridge_head_refit_bootstrap.csv",
        index=False,
    )
    decision = {
        "version": config["version"],
        "status": status,
        "analysis_status": config["status"],
        "completed_utc": datetime.now(UTC).isoformat(),
        "score_table_sha256_verified": True,
        "score_manifest_sha256": _sha256(manifest_path),
        "source_route_freeze": str(route_freeze_path.relative_to(ROOT)),
        "source_route_freeze_sha256": route_freeze_sha256,
        "bridge_loaded_after_route_freeze": True,
        "source_bridge_overlap": {"big5": 0, "mbti": 0},
        "layers": {
            name: {
                "level": layer.level,
                "features": len(layer.columns),
                "estimand": layer.estimand,
            }
            for name, layer in layers.items()
        },
        "gates": gates,
        "direct_aggregate": aggregate.replace({np.nan: None}).to_dict("records"),
        "direct_router_bootstrap": direct_bootstrap.replace(
            {np.nan: None}
        ).to_dict("records"),
        "bridge_summary": bridge_summary.replace({np.nan: None}).to_dict("records"),
        "bridge_router_bootstrap": bridge_bootstrap.replace(
            {np.nan: None}
        ).to_dict("records"),
        "bridge_head_refit_bootstrap": bridge_head_refit.replace(
            {np.nan: None}
        ).to_dict("records"),
        "route_stability": route_stability.replace(
            {np.nan: None}
        ).to_dict("records"),
        "source_selected_routes": routed_final.replace(
            {np.nan: None}
        ).to_dict("records"),
        "claim_boundary": config["claim_boundary"],
        "report": str(report_path.relative_to(ROOT)),
    }
    report = _report(
        config=config,
        aggregate=aggregate,
        selections=outer_selections,
        final_routes=final_routes,
        route_stability=route_stability,
        direct_bootstrap=direct_bootstrap,
        bridge_summary=bridge_summary,
        bridge_bootstrap=bridge_bootstrap,
        bridge_head_refit=bridge_head_refit,
        decision=decision,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    (output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    _write_json(output_dir / "decision.json", decision)
    print(json.dumps(decision, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
