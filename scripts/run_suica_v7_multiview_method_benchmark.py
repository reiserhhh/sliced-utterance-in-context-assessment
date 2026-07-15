#!/usr/bin/env python3
"""Compare registered V7 shared-subspace methods on a fresh author cohort.

Methods are mathematical baselines, not competing psychological theories.  The
script explicitly refuses to label JIVE/AJIVE results when their optional
dependencies are not installed instead of silently calling another method JIVE.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v7_operator_smoke import DEFAULT_INPUT, _infer_column, _load_config, _read_table  # noqa: E402
from scripts.run_suica_v7_temporal_geometry_baselines import (  # noqa: E402
    DEFAULT_CONFIG as W3_CONFIG, DEFAULT_E0, DEFAULT_E1, DEFAULT_E2_CONFIG, DEFAULT_E4_CONFIG, _prior_exclusions,
)
from suica_core.v7_governance import append_ledger_event, write_artifact_inventory, write_run_manifest  # noqa: E402
from suica_core.v7_multiview import (  # noqa: E402
    common_feature_columns, fit_block_scalers, fit_consensus_model, fit_direct_predictors,
    predict_target_from_source, transform_feature_block,
)
from suica_core.v7_multiview_baselines import evaluate_shared_model, fit_concat_pca, fit_rgcca_sumcor, global_r2, predict_target  # noqa: E402
from suica_core.v7_observations import ObservationSpec, build_observations, canonicalize_comments, prepare_source_panel, select_reference_authors  # noqa: E402
from suica_core.v7_psychometric import author_features_from_embeddings  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v7_multiview_method_benchmark.json"


def parse_args() -> argparse.Namespace:
    """Parse a fresh, no-label multiview benchmark."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--e0-cohort", type=Path, default=DEFAULT_E0)
    parser.add_argument("--e1-cohort", type=Path, default=DEFAULT_E1)
    parser.add_argument("--e2-config", type=Path, default=DEFAULT_E2_CONFIG)
    parser.add_argument("--e4-config", type=Path, default=DEFAULT_E4_CONFIG)
    parser.add_argument("--w3-config", type=Path, default=W3_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _operator_specs(config: dict[str, Any]) -> list[ObservationSpec]:
    """Create registered observation views over one common source panel."""
    defaults = {
        "min_tokens": int(config["min_tokens_per_unit"]),
        "max_units_per_user": int(config["max_units_per_user"]),
        "max_source_comments_per_user": int(config["max_source_comments_per_user"]),
        "max_source_tokens_per_user": int(config["max_source_tokens_per_user"]),
    }
    return [ObservationSpec(**{**defaults, **raw}) for raw in config["operators"]]


def _cohort_recipe(config: dict[str, Any]) -> dict[str, Any]:
    """Return the declared deterministic author-cohort selection recipe."""
    return {
        "cohort_id": str(config.get("cohort_id", "v7.3-w4-multiview-method-benchmark-1")),
        "seed": int(config["seed"]),
        "min_comments_per_user": int(config["min_comments_per_user"]),
        "max_users": int(config["max_users"]),
    }


def _select_declared_cohort(
    canonical: pd.DataFrame,
    *,
    exclusions: set[str],
    recipe: dict[str, Any],
) -> pd.DataFrame:
    """Replay one deterministic cohort without persisting raw user identifiers."""
    return select_reference_authors(
        canonical,
        min_comments_per_user=int(recipe["min_comments_per_user"]),
        max_users=int(recipe["max_users"]),
        seed=int(recipe["seed"]),
        exclude_user_ids=exclusions,
        cohort_salt=str(recipe["cohort_id"]),
    )


def _cohort_commitment(user_ids: pd.Series, *, recipe: dict[str, Any]) -> dict[str, Any]:
    """Commit to a cohort membership set without writing raw identifiers."""
    canonical_ids = "\n".join(sorted(set(user_ids.astype(str))))
    return {
        "cohort_recipe": recipe,
        "n_authors": int(user_ids.astype(str).nunique()),
        "membership_sha256": hashlib.sha256(canonical_ids.encode("utf-8")).hexdigest(),
        "raw_identifiers_persisted": False,
    }


def _rank_boundary_status(summary: pd.DataFrame, *, rank_grid: list[int]) -> str:
    """Flag rank selection at the registered grid boundary, never as a dimension."""
    maximum = max(int(value) for value in rank_grid)
    return (
        "RANK_UNRESOLVED_AT_REGISTERED_GRID_BOUNDARY"
        if bool(summary["selected_rank"].eq(maximum).any())
        else "RANK_RESOLVED_WITHIN_REGISTERED_GRID"
    )


def _fit_representation(texts: pd.Series, spec: dict[str, Any], *, seed: int) -> tuple[TfidfVectorizer, TruncatedSVD]:
    """Fit a discovery-only TF-IDF/SVD representation."""
    vectorizer = TfidfVectorizer(
        analyzer=str(spec["analyzer"]), lowercase=True, strip_accents="unicode",
        ngram_range=tuple(int(value) for value in spec["ngram_range"]), max_features=int(spec["max_features"]), min_df=1, sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts.fillna("").astype(str))
    dimensions = min(int(spec["svd_dimensions"]), matrix.shape[0] - 1, matrix.shape[1] - 1)
    if dimensions < 2:
        raise RuntimeError(f"Insufficient rank for representation {spec['name']}: {matrix.shape}")
    reducer = TruncatedSVD(n_components=dimensions, random_state=int(seed))
    reducer.fit(matrix)
    return vectorizer, reducer


def _transform(vectorizer: TfidfVectorizer, reducer: TruncatedSVD, texts: pd.Series) -> np.ndarray:
    """Apply a frozen discovery representation without refitting."""
    return reducer.transform(vectorizer.transform(texts.fillna("").astype(str)))


def _aligned_ids(frames: dict[str, pd.DataFrame], views: tuple[str, ...], split: str) -> list[str]:
    """Find authors retained by every registered view in one split."""
    shared: set[str] | None = None
    for view in views:
        ids = set(frames[view].loc[frames[view]["split"].eq(split), "user_id"].astype(str))
        shared = ids if shared is None else shared.intersection(ids)
    return sorted(shared or set())


def _blocks(frames: dict[str, pd.DataFrame], scalers: dict[str, Any], views: tuple[str, ...], user_ids: list[str]) -> dict[str, np.ndarray]:
    """Materialize aligned scaled feature blocks for one author split."""
    return {view: transform_feature_block(frames[view], scaler=scalers[view], user_ids=user_ids) for view in views}


def _fit_method(method: str, blocks: dict[str, np.ndarray], *, views: tuple[str, ...], rank: int, config: dict[str, Any]) -> Any:
    """Fit one declared shared-subspace method."""
    if method == "CONSENSUS_COVARIANCE":
        return fit_consensus_model(blocks, view_names=views, rank=rank, ridge_alpha=float(config["ridge_alpha"]))
    if method == "CONCAT_PCA":
        return fit_concat_pca(blocks, view_names=views, rank=rank, ridge_alpha=float(config["ridge_alpha"]))
    if method == "RGCCA_SUMCOR":
        return fit_rgcca_sumcor(blocks, view_names=views, rank=rank, ridge_alpha=float(config["rgcca_ridge"]))
    raise ValueError(f"Unknown method: {method}")


def _evaluate(method: str, model: Any, blocks: dict[str, np.ndarray], *, views: tuple[str, ...]) -> pd.DataFrame:
    """Score all directed held-out transports through one shared model."""
    if method != "CONSENSUS_COVARIANCE":
        return pd.DataFrame(evaluate_shared_model(model, blocks))
    rows: list[dict[str, Any]] = []
    for source in views:
        for target in views:
            if source == target:
                continue
            rows.append({
                "method": method, "source": source, "target": target, "n_authors": int(len(blocks[source])),
                "global_r2": global_r2(blocks[target], predict_target_from_source(model, source, target, blocks[source])),
            })
    return pd.DataFrame(rows)


def _mean_r2(method: str, model: Any, blocks: dict[str, np.ndarray], *, views: tuple[str, ...], indices: np.ndarray | None = None) -> float:
    """Calculate a mean directed held-out R2, optionally cluster-resampled."""
    if indices is None:
        subset = blocks
    else:
        subset = {view: values[indices] for view, values in blocks.items()}
    values = _evaluate(method, model, subset, views=views)["global_r2"].to_numpy(float)
    return float(np.nanmean(values))


def _calibration_stat(method: str, model: Any, calibration: dict[str, np.ndarray], *, views: tuple[str, ...], seed: int, iterations: int) -> tuple[float, float]:
    """Return calibration mean transport and author-bootstrap SE for rank selection."""
    point = _mean_r2(method, model, calibration, views=views)
    rng = np.random.default_rng(int(seed))
    n = len(next(iter(calibration.values())))
    values = [_mean_r2(method, model, calibration, views=views, indices=rng.integers(0, n, size=n)) for _ in range(int(iterations))]
    return point, float(np.nanstd(np.asarray(values, dtype=float), ddof=1))


def _select_rank(method: str, discovery: dict[str, np.ndarray], calibration: dict[str, np.ndarray], *, views: tuple[str, ...], config: dict[str, Any], seed: int) -> tuple[pd.DataFrame, int]:
    """Use calibration authors only and select the smallest rank within one SE."""
    rank_max = min(len(next(iter(discovery.values()))) - 2, *(values.shape[1] for values in discovery.values()))
    rows: list[dict[str, Any]] = []
    for rank in [int(value) for value in config["rank_grid"] if 1 <= int(value) <= rank_max]:
        model = _fit_method(method, discovery, views=views, rank=rank, config=config)
        mean, se = _calibration_stat(method, model, calibration, views=views, seed=seed + rank * 101, iterations=int(config["calibration_bootstrap_iterations"]))
        rows.append({"method": method, "rank": rank, "calibration_mean_r2": mean, "calibration_author_bootstrap_se": se})
    table = pd.DataFrame(rows)
    if table.empty:
        raise RuntimeError(f"No admissible rank for {method}.")
    best = table.sort_values(["calibration_mean_r2", "rank"], ascending=[False, True]).iloc[0]
    threshold = float(best.calibration_mean_r2 - best.calibration_author_bootstrap_se)
    candidates = table.loc[table["calibration_mean_r2"].ge(threshold)].sort_values(["rank", "calibration_mean_r2"], ascending=[True, False])
    selected = int(candidates.iloc[0]["rank"])
    table["one_se_threshold"] = threshold
    table["selected_by_one_se"] = table["rank"].eq(selected)
    return table, selected


def _direct_mean(train: dict[str, np.ndarray], confirmation: dict[str, np.ndarray], *, views: tuple[str, ...], alpha: float) -> tuple[float, pd.DataFrame]:
    """Fit direct Ridge maps as an unconstrained cross-view comparator."""
    models = fit_direct_predictors(train, view_names=views, ridge_alpha=float(alpha))
    rows: list[dict[str, Any]] = []
    for source in views:
        for target in views:
            if source == target:
                continue
            rows.append({"method": "DIRECT_RIDGE", "source": source, "target": target, "n_authors": int(len(confirmation[source])), "global_r2": global_r2(confirmation[target], models[(source, target)].predict(confirmation[source]))})
    table = pd.DataFrame(rows)
    return float(table["global_r2"].mean()), table


def _paired_method_differences(
    models: dict[str, Any],
    confirmation: dict[str, np.ndarray],
    *,
    views: tuple[str, ...],
    iterations: int,
    seed: int,
    material_threshold: float,
) -> pd.DataFrame:
    """Estimate paired author-bootstrap differences between frozen shared models.

    This is a within-confirmation comparison of frozen estimators. It does not
    select a universal method, factor count, or psychological theory.
    """
    names = sorted(models)
    n_authors = len(next(iter(confirmation.values())))
    rng = np.random.default_rng(int(seed))
    rows: list[dict[str, Any]] = []
    for first, second in combinations(names, 2):
        point = _mean_r2(first, models[first], confirmation, views=views) - _mean_r2(second, models[second], confirmation, views=views)
        draws = []
        for _ in range(int(iterations)):
            indices = rng.integers(0, n_authors, size=n_authors)
            draws.append(
                _mean_r2(first, models[first], confirmation, views=views, indices=indices)
                - _mean_r2(second, models[second], confirmation, views=views, indices=indices)
            )
        low, high = float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))
        rows.append({
            "first_method": first,
            "second_method": second,
            "mean_r2_difference_first_minus_second": float(point),
            "ci_low": low,
            "ci_high": high,
            "material_threshold": float(material_threshold),
            "status": (
                "MATERIAL_FIRST_OVER_SECOND_SUPPORTED" if low > float(material_threshold) else
                "MATERIAL_SECOND_OVER_FIRST_SUPPORTED" if high < -float(material_threshold) else
                "NO_MATERIAL_PAIRED_DIFFERENCE_SUPPORTED"
            ),
        })
    return pd.DataFrame(rows)


def _studentized_max_t(observed: pd.DataFrame, null: pd.DataFrame) -> pd.DataFrame:
    """Correct three shared methods across representations using max standardized nulls."""
    output = observed.copy()
    groups = {key: value.sort_values("permutation") for key, value in null.groupby(["representation", "method"], observed=True)}
    z_observed: dict[tuple[str, str], float] = {}
    z_null: dict[tuple[str, str], pd.Series] = {}
    for row in output.itertuples(index=False):
        key = (str(row.representation), str(row.method))
        values = groups[key]["mean_r2"].to_numpy(float)
        center, scale = float(values.mean()), max(float(values.std(ddof=1)), 1e-12)
        z_observed[key] = float((row.confirmation_mean_r2 - center) / scale)
        z_null[key] = (groups[key]["mean_r2"] - center) / scale
    maxima = []
    for iteration in sorted(null["permutation"].unique()):
        maxima.append(max(float(series.loc[groups[key]["permutation"].eq(iteration)].iloc[0]) for key, series in z_null.items()))
    maximum = np.asarray(maxima, dtype=float)
    output["observed_z"] = [z_observed[(str(row.representation), str(row.method))] for row in output.itertuples(index=False)]
    output["max_t_fwer_p"] = [float((1 + np.sum(maximum >= value)) / (len(maximum) + 1)) for value in output["observed_z"]]
    output["status"] = np.where(output["confirmation_mean_r2"].gt(0) & output["max_t_fwer_p"].le(0.05), "FWER_POSITIVE_SUPPORTED", np.where(output["max_t_fwer_p"].le(0.05), "FWER_NONPOSITIVE_DIFFERENCE", "UNRESOLVED"))
    return output


def _write_report(path: Path, *, output_dir: Path, availability: pd.DataFrame, selection: pd.DataFrame, summary: pd.DataFrame, differences: pd.DataFrame, direct: pd.DataFrame, decision: dict[str, Any]) -> None:
    """Write a bounded, no-label method-comparison report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# SUICA V7 Multiview Method Benchmark\n\n"
        "## Scope\n\n"
        "A fresh author cohort, excluding E0--E4 and W3, compares mathematical multiview methods. Rank selection uses calibration authors only; confirmation remains held out. No psychological labels are loaded.\n\n"
        f"### Method Availability\n\n{availability.to_markdown(index=False)}\n\n"
        f"### Calibration Rank Selection\n\n{selection.to_markdown(index=False, floatfmt='.3f')}\n\n"
        f"### Confirmation Shared-Method Summary\n\n{summary.to_markdown(index=False, floatfmt='.3f')}\n\n"
        f"### Paired Confirmation Method Differences\n\n{differences.to_markdown(index=False, floatfmt='.3f')}\n\n"
        f"### Direct Ridge Comparator\n\n{direct.to_markdown(index=False, floatfmt='.3f')}\n\n"
        f"## Decision\n\n```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n```\n\n"
        "## Boundary\n\n"
        "This is a comparison of anonymous shared-text representations. A method outperforming broken correspondence does not identify an axis, author core, psychological construct, or clinical score. A selected rank at the registered grid maximum is explicitly unresolved: a transport criterion must not be extended indefinitely and reinterpreted as a factor count. The declared boundary action determines whether a fresh capacity check or a separate effective-rank diagnostic is appropriate. `JIVE_AJIVE` is explicitly unavailable unless its actual optional dependency is present; no surrogate is renamed as JIVE.\n\n"
        f"Artifacts: `{output_dir}`\n",
        encoding="utf-8",
    )


def main() -> int:
    """Execute a fresh-cohort V7 multiview baseline benchmark."""
    args = parse_args()
    config = _load_config(args.config)
    if args.quick:
        config["max_users"] = min(int(config["max_users"]), 120)
        config["max_source_comments_per_user"] = min(int(config["max_source_comments_per_user"]), 16)
        config["max_source_tokens_per_user"] = min(int(config["max_source_tokens_per_user"]), 2048)
        config["max_units_per_user"] = min(int(config["max_units_per_user"]), 64)
        config["calibration_bootstrap_iterations"] = min(int(config["calibration_bootstrap_iterations"]), 19)
        config["broken_correspondence_iterations"] = min(int(config["broken_correspondence_iterations"]), 29)
        config["confirmation_pair_bootstrap_iterations"] = min(int(config["confirmation_pair_bootstrap_iterations"]), 99)
        for representation in config["representations"]:
            representation["max_features"] = min(int(representation["max_features"]), 2000)
            representation["svd_dimensions"] = min(int(representation["svd_dimensions"]), 12)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "run_manifest.json", repository_root=ROOT,
        input_paths=[args.input, args.config, args.e0_cohort, args.e1_cohort, args.e2_config, args.e4_config, args.w3_config], config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_core" / "v7_multiview.py", ROOT / "suica_core" / "v7_multiview_baselines.py"],
        estimand_id="V7.3-W4-multiview-baseline", external_labels_read=False, raw_identifiers_persisted=False,
    )
    raw = _read_table(args.input)
    columns = [str(column) for column in raw.columns]
    column_map = {
        "user": _infer_column(columns, ["author", "user_id", "participant_id", "user", "id"], None, required=True),
        "text": _infer_column(columns, ["body", "text", "comment", "content", "message"], None, required=True),
        "order": _infer_column(columns, ["created_utc", "timestamp", "time", "date", "created_at"], None, required=False),
        "condition": _infer_column(columns, ["subreddit", "condition", "platform", "task", "forum"], None, required=False),
    }
    canonical = canonicalize_comments(raw, user_col=str(column_map["user"]), text_col=str(column_map["text"]), order_col=column_map["order"], condition_col=column_map["condition"], min_tokens=int(config["min_tokens_per_unit"]))
    excluded = _prior_exclusions(canonical, e0_path=args.e0_cohort, e1_path=args.e1_cohort, e2_config_path=args.e2_config, e4_config_path=args.e4_config)
    w3 = _load_config(args.w3_config)
    w3_selected = select_reference_authors(canonical, min_comments_per_user=int(w3["min_comments_per_user"]), max_users=int(w3["max_users"]), seed=int(w3["seed"]), exclude_user_ids=excluded, cohort_salt="v7.3-w3-temporal-geometry-1")
    excluded = excluded.union(set(w3_selected["user_id"].astype(str)))
    prior_recipes = list(config.get("exclude_w4_cohorts", []))
    for raw_recipe in prior_recipes:
        prior = _select_declared_cohort(canonical, exclusions=excluded, recipe=dict(raw_recipe))
        excluded = excluded.union(set(prior["user_id"].astype(str)))
    recipe = _cohort_recipe(config)
    selected = _select_declared_cohort(canonical, exclusions=excluded, recipe=recipe)
    specs = _operator_specs(config)
    source_panel = prepare_source_panel(selected, specs[0])
    split_counts = source_panel.groupby("split", observed=True)["user_id"].nunique().to_dict()
    if min(int(split_counts.get(split, 0)) for split in ("discovery", "calibration", "confirmation")) < 16:
        raise RuntimeError(f"Fresh W4 cohort cannot support 3-way split: {split_counts}")
    views = tuple(spec.name for spec in specs)
    units = {spec.name: build_observations(source_panel, spec) for spec in specs}
    methods = ("CONSENSUS_COVARIANCE", "CONCAT_PCA", "RGCCA_SUMCOR")
    availability = pd.DataFrame([
        *[{"method": method, "status": "AVAILABLE_BUILTIN", "detail": "Implemented and compared in this run."} for method in methods],
        {"method": "JIVE_AJIVE", "status": "AVAILABLE_OPTIONAL" if importlib.util.find_spec("mvlearn") or importlib.util.find_spec("jive") else "REFUSE_OPTIONAL_DEPENDENCY_MISSING", "detail": "Not substituted by a differently named implementation."},
    ])
    selection_tables: list[pd.DataFrame] = []
    summary_rows: list[dict[str, Any]] = []
    directed_rows: list[pd.DataFrame] = []
    direct_rows: list[pd.DataFrame] = []
    null_rows: list[dict[str, Any]] = []
    difference_rows: list[pd.DataFrame] = []
    for rep_index, rep in enumerate(config["representations"]):
        vectorizer, reducer = _fit_representation(source_panel.loc[source_panel["split"].eq("discovery"), "text"], rep, seed=int(config["seed"]) + rep_index)
        frames = {view: author_features_from_embeddings(units[view], _transform(vectorizer, reducer, units[view]["text"])) for view in views}
        feature_names = common_feature_columns(frames, views)
        ids = {split: _aligned_ids(frames, views, split) for split in ("discovery", "calibration", "confirmation")}
        if min(len(value) for value in ids.values()) < 16:
            raise RuntimeError(f"Insufficient W4 support for {rep['name']}: { {key: len(value) for key, value in ids.items()} }")
        scalers = fit_block_scalers(frames, view_names=views, feature_names=feature_names, discovery_user_ids=ids["discovery"])
        discovery = _blocks(frames, scalers, views, ids["discovery"])
        calibration = _blocks(frames, scalers, views, ids["calibration"])
        confirmation = _blocks(frames, scalers, views, ids["confirmation"])
        train = {view: np.vstack([discovery[view], calibration[view]]) for view in views}
        selected_ranks: dict[str, int] = {}
        fitted_models: dict[str, Any] = {}
        for method_index, method in enumerate(methods):
            table, rank = _select_rank(method, discovery, calibration, views=views, config=config, seed=int(config["seed"]) + 1000 * rep_index + 100 * method_index)
            table["representation"] = rep["name"]
            selection_tables.append(table)
            selected_ranks[method] = rank
            model = _fit_method(method, train, views=views, rank=rank, config=config)
            fitted_models[method] = model
            directed = _evaluate(method, model, confirmation, views=views)
            directed["representation"] = rep["name"]
            directed_rows.append(directed)
            summary_rows.append({"representation": rep["name"], "method": method, "selected_rank": rank, "confirmation_mean_r2": float(directed["global_r2"].mean())})
        differences = _paired_method_differences(
            fitted_models,
            confirmation,
            views=views,
            iterations=int(config["confirmation_pair_bootstrap_iterations"]),
            seed=int(config["seed"]) + 7000 + rep_index,
            material_threshold=float(config["material_mean_r2_difference"]),
        )
        differences["representation"] = rep["name"]
        difference_rows.append(differences)
        direct_mean, direct = _direct_mean(train, confirmation, views=views, alpha=float(config["ridge_alpha"]))
        direct["representation"] = rep["name"]
        direct["confirmation_mean_r2"] = direct_mean
        direct_rows.append(direct)
        rng = np.random.default_rng(int(config["seed"]) + 5000 + rep_index)
        for iteration in range(int(config["broken_correspondence_iterations"])):
            broken = {views[0]: train[views[0]]}
            for view in views[1:]:
                broken[view] = train[view][rng.permutation(len(train[view]))]
            for method in methods:
                model = _fit_method(method, broken, views=views, rank=selected_ranks[method], config=config)
                null_rows.append({"permutation": iteration, "representation": rep["name"], "method": method, "mean_r2": _mean_r2(method, model, confirmation, views=views)})
    selection = pd.concat(selection_tables, ignore_index=True)
    summary = _studentized_max_t(pd.DataFrame(summary_rows), pd.DataFrame(null_rows))
    directed = pd.concat(directed_rows, ignore_index=True)
    direct = pd.concat(direct_rows, ignore_index=True)
    method_differences = pd.concat(difference_rows, ignore_index=True)
    best = summary.loc[summary["status"].eq("FWER_POSITIVE_SUPPORTED")].sort_values("confirmation_mean_r2", ascending=False)
    rank_status = _rank_boundary_status(summary, rank_grid=[int(value) for value in config["rank_grid"]])
    cohort_commitment = _cohort_commitment(source_panel["user_id"], recipe=recipe)
    boundary_action = str(config.get("rank_boundary_action", "REFUSE_FACTOR_COUNT_USE_EFFECTIVE_RANK_DIAGNOSTIC"))
    top_endpoint = None if best.empty else {
        "representation": str(best.iloc[0].representation),
        "method": str(best.iloc[0].method),
        "confirmation_mean_r2": float(best.iloc[0].confirmation_mean_r2),
    }
    decision = {
        "status": "SUBSPACE_COMPARISON_SUPPORTED" if len(best) else "SUBSPACE_COMPARISON_UNRESOLVED",
        "highest_supported_endpoint_descriptive_only": top_endpoint,
        "method_superiority_status": (
            "WITHIN_COHORT_MATERIAL_DIFFERENCE_SUPPORTED"
            if bool(method_differences["status"].ne("NO_MATERIAL_PAIRED_DIFFERENCE_SUPPORTED").any())
            else "NO_MATERIAL_PAIRED_METHOD_DIFFERENCE_SUPPORTED"
        ),
        "direct_ridge_is_comparator_not_shared_subspace": True,
        "rank_status": rank_status,
        "rank_boundary_action": boundary_action if rank_status == "RANK_UNRESOLVED_AT_REGISTERED_GRID_BOUNDARY" else "NOT_APPLICABLE",
        "rank_selection_role": "TRANSPORT_CAPACITY_PARAMETER_NOT_FACTOR_COUNT",
        "cohort_commitment": cohort_commitment,
        "claim_boundary": "Mathematical multiview comparison only; no factor naming, personality, causal, or clinical claim.",
    }
    availability.to_csv(args.output_dir / "method_availability.csv", index=False)
    selection.to_csv(args.output_dir / "rank_selection.csv", index=False)
    summary.to_csv(args.output_dir / "confirmation_method_summary.csv", index=False)
    directed.to_csv(args.output_dir / "confirmation_directed_edges.csv", index=False)
    direct.to_csv(args.output_dir / "direct_ridge_comparator.csv", index=False)
    method_differences.to_csv(args.output_dir / "paired_method_differences.csv", index=False)
    pd.DataFrame(null_rows).to_parquet(args.output_dir / "broken_correspondence_null.parquet", index=False)
    (args.output_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output_dir / "cohort_commitment.json").write_text(json.dumps(cohort_commitment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({"column_map": column_map, "n_prior_author_exclusions": int(len(excluded)), "n_selected_authors": int(source_panel["user_id"].nunique()), "split_counts": {key: int(value) for key, value in split_counts.items()}, "external_labels_read": False, "raw_identifiers_persisted": False, "multiplicity_family": config["multiplicity_family"], "cohort_commitment": cohort_commitment, "prior_w4_cohort_recipes": prior_recipes, "claim_boundary": decision["claim_boundary"]})
    (args.output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_report(args.report, output_dir=args.output_dir, availability=availability, selection=selection, summary=summary, differences=method_differences, direct=direct.groupby(["representation", "method"], observed=True)["global_r2"].mean().reset_index(name="mean_directed_r2"), decision=decision)
    append_ledger_event(args.output_dir / "evidence_ledger.jsonl", {"estimand_id": manifest["estimand_id"], "status": decision["status"], "claim_boundary": decision["claim_boundary"]})
    inventory = write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    print(json.dumps({"output_dir": str(args.output_dir), "report": str(args.report), "status": decision["status"], "n_method_rows": int(len(summary)), "artifact_files": inventory["n_files"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
