#!/usr/bin/env python3
"""Run V7.1 fresh-author shared/private multiview projection analysis.

The experiment treats different slice designs as parallel observation views.
It never reads Big Five, MBTI, or other external criteria. Its only question is
whether anonymous author-relative feature structure is shared between views,
private to a view, or no better than broken author correspondence.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v7_operator_smoke import (  # noqa: E402
    DEFAULT_INPUT,
    _infer_column,
    _load_config,
    _read_table,
    _schema_report,
    _write_json,
)
from suica_core.v7_observations import (  # noqa: E402
    ObservationSpec,
    build_observations,
    canonicalize_comments,
    prepare_source_panel,
    select_reference_authors,
)
from suica_core.v7_operator_controls import source_disjoint_partition  # noqa: E402
from suica_core.v7_multiview import (  # noqa: E402
    common_feature_columns,
    evaluate_cross_view,
    fit_block_scalers,
    fit_consensus_model,
    fit_direct_predictors,
    linear_cka,
    mean_row_cosine,
    predict_target_from_source,
    transform_feature_block,
)
from suica_core.v7_psychometric import (  # noqa: E402
    RepresentationSpec,
    author_features_from_embeddings,
    bundle_sha256,
    fit_representation,
)
from suica_core.v7_governance import (  # noqa: E402
    sha256_file,
    write_artifact_inventory,
)


DEFAULT_CONFIG = ROOT / "configs" / "v7_multiview_projection.json"
DEFAULT_EXCLUDE = ROOT / "results" / "v7_operator_boundary_audit" / "e0_full_20260714" / "scores_native.csv"


def parse_args() -> argparse.Namespace:
    """Parse a fresh-cohort, label-free V7.1 multiview request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--exclude-cohort", type=Path, default=DEFAULT_EXCLUDE)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--max-users", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--user-col", default=None)
    parser.add_argument("--text-col", default=None)
    parser.add_argument("--order-col", default=None)
    parser.add_argument("--condition-col", default=None)
    return parser.parse_args()


def _operator_specs(config: dict[str, Any]) -> list[ObservationSpec]:
    defaults = {
        "min_tokens": int(config["min_tokens_per_unit"]),
        "max_units_per_user": int(config["max_units_per_user"]),
        "max_source_comments_per_user": int(config["max_source_comments_per_user"]),
        "max_source_tokens_per_user": int(config["max_source_tokens_per_user"]),
    }
    return [ObservationSpec(**{**defaults, **raw}) for raw in config["operators"]]


def _read_excluded_users(path: Path) -> set[str]:
    """Read only author IDs from an earlier engineering cohort artifact."""
    if not path.exists():
        raise FileNotFoundError(
            f"Fresh-cohort exclusion artifact is required but missing: {path}. "
            "Run E0 first or pass an explicit prior-cohort score file."
        )
    frame = pd.read_csv(path, usecols=["user_id"])
    return set(frame["user_id"].dropna().astype(str))


def _aligned_user_ids(feature_frames: dict[str, pd.DataFrame], view_names: tuple[str, ...], split: str) -> list[str]:
    common: set[str] | None = None
    for view in view_names:
        frame = feature_frames[view]
        users = set(frame.loc[frame["split"].eq(split), "user_id"].astype(str))
        common = users if common is None else common.intersection(users)
    return sorted(common or set())


def _blocks(
    feature_frames: dict[str, pd.DataFrame],
    *,
    scalers: dict[str, Any],
    view_names: tuple[str, ...],
    user_ids: list[str],
) -> dict[str, np.ndarray]:
    return {
        view: transform_feature_block(feature_frames[view], scaler=scalers[view], user_ids=user_ids)
        for view in view_names
    }


def _global_r2(target: np.ndarray, prediction: np.ndarray) -> float:
    """Return global held-out R2 with the same convention as the atlas."""
    truth = np.asarray(target, dtype=float)
    estimated = np.asarray(prediction, dtype=float)
    denominator = float(np.sum((truth - np.mean(truth, axis=0, keepdims=True)) ** 2))
    if denominator <= 1e-14:
        return float("nan")
    return float(1.0 - np.sum((truth - estimated) ** 2) / denominator)


def _calibration_cross_r2(
    blocks: dict[str, np.ndarray],
    model: Any,
    *,
    bootstrap_iterations: int,
    seed: int,
) -> tuple[float, float]:
    """Return calibration mean R2 and author-bootstrap standard error.

    The model is discovery-fitted.  The bootstrap resamples calibration authors
    together across all views, preserving their cross-view correspondence and
    avoiding a false independence assumption across directed view pairs.
    """
    view_names = model.view_names

    def statistic(indices: np.ndarray) -> float:
        values: list[float] = []
        for source in view_names:
            for target in view_names:
                if source == target:
                    continue
                prediction = predict_target_from_source(model, source, target, blocks[source][indices])
                values.append(_global_r2(blocks[target][indices], prediction))
        finite = np.asarray(values, dtype=float)
        return float(np.nanmean(finite)) if np.isfinite(finite).any() else float("nan")

    point = statistic(np.arange(len(next(iter(blocks.values()))), dtype=int))
    if int(bootstrap_iterations) < 2:
        return point, float("nan")
    rng = np.random.default_rng(seed)
    n_authors = len(next(iter(blocks.values())))
    bootstrap = np.asarray(
        [statistic(rng.integers(0, n_authors, size=n_authors)) for _ in range(int(bootstrap_iterations))],
        dtype=float,
    )
    return point, float(np.nanstd(bootstrap, ddof=1))


def _admissible_rank_max(discovery: dict[str, np.ndarray]) -> int:
    """Return the largest shared rank admissible in every discovery block."""
    matrices = [np.asarray(values, dtype=float) for values in discovery.values()]
    if not matrices:
        raise ValueError("Cannot derive an admissible rank without discovery blocks.")
    n_authors, n_features = matrices[0].shape
    return int(min(n_authors - 2, n_features, *(np.linalg.matrix_rank(matrix) for matrix in matrices)))


def _selection_table(
    discovery: dict[str, np.ndarray],
    calibration: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    ranks: list[int],
    alphas: list[float],
    bootstrap_iterations: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.Series]:
    """Select shared rank with a calibration-author one-standard-error rule."""
    rows: list[dict[str, Any]] = []
    for rank in ranks:
        for alpha in alphas:
            model = fit_consensus_model(discovery, view_names=view_names, rank=int(rank), ridge_alpha=float(alpha))
            mean_r2, sem = _calibration_cross_r2(
                calibration,
                model,
                bootstrap_iterations=bootstrap_iterations,
                seed=seed + int(rank) * 1009 + int(round(float(alpha) * 10)),
            )
            rows.append({
                "shared_rank": int(rank),
                "ridge_alpha": float(alpha),
                "calibration_mean_consensus_global_r2": mean_r2,
                "calibration_consensus_global_r2_se": sem,
            })
    table = pd.DataFrame(rows)
    best = table.sort_values(
        ["calibration_mean_consensus_global_r2", "shared_rank", "ridge_alpha"],
        ascending=[False, True, True],
    ).iloc[0]
    threshold = float(best["calibration_mean_consensus_global_r2"] - best["calibration_consensus_global_r2_se"])
    table["one_se_threshold"] = threshold
    table["within_one_se"] = table["calibration_mean_consensus_global_r2"] >= threshold
    selected = table.loc[table["within_one_se"]].sort_values(
        ["shared_rank", "calibration_mean_consensus_global_r2", "ridge_alpha"],
        ascending=[True, False, True],
    ).iloc[0]
    table["selected_by_one_se"] = False
    table.loc[selected.name, "selected_by_one_se"] = True
    return table, selected


def _decoder_basis(model: Any, view: str) -> np.ndarray:
    """Return an orthonormal feature-space basis for one shared decoder."""
    if int(model.rank) == 0:
        return np.zeros((model.decoders[view].shape[1], 0), dtype=float)
    decoder = np.asarray(model.decoders[view], dtype=float)
    basis, _ = np.linalg.qr(decoder.T, mode="reduced")
    return basis[:, : int(model.rank)]


def _axis_alignment(reference: np.ndarray, candidate: np.ndarray) -> tuple[float, float]:
    """Align anonymous decoder rows without assigning a construct name."""
    ref = np.asarray(reference, dtype=float)
    boot = np.asarray(candidate, dtype=float)
    if ref.shape != boot.shape or ref.shape[0] == 0:
        return float("nan"), float("nan")
    ref = ref / np.maximum(np.linalg.norm(ref, axis=1, keepdims=True), 1e-12)
    boot = boot / np.maximum(np.linalg.norm(boot, axis=1, keepdims=True), 1e-12)
    similarity = np.abs(ref @ boot.T)
    rows, columns = linear_sum_assignment(-similarity)
    matched = similarity[rows, columns]
    margins: list[float] = []
    for row, column, value in zip(rows, columns, matched, strict=True):
        alternatives = np.delete(similarity[row], column)
        margins.append(float(value - (np.max(alternatives) if len(alternatives) else 0.0)))
    return float(np.mean(matched)), float(np.min(margins))


def _bootstrap_alignment(
    discovery: dict[str, np.ndarray],
    *,
    view_names: tuple[str, ...],
    rank: int,
    ridge_alpha: float,
    iterations: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bootstrap shared loading subspaces and anonymous-axis alignment.

    Subspace congruence is rotation-invariant:
    ``gamma = ||U^T U_b||_F^2 / r``.  Axis alignment is reported separately and
    cannot promote a named factor by itself.
    """
    if rank == 0:
        columns = [
            "operator", "subspace_congruence_lower", "subspace_congruence_median",
            "random_subspace_null_upper", "axis_mean_cosine_lower",
            "axis_min_assignment_margin_median", "subspace_status", "axis_status",
        ]
        return pd.DataFrame(), pd.DataFrame(columns=columns)
    reference = fit_consensus_model(discovery, view_names=view_names, rank=rank, ridge_alpha=ridge_alpha)
    reference_bases = {view: _decoder_basis(reference, view) for view in view_names}
    rng = np.random.default_rng(seed)
    n_authors = len(next(iter(discovery.values())))
    rows: list[dict[str, Any]] = []
    for replicate in range(int(iterations)):
        indices = rng.integers(0, n_authors, size=n_authors)
        resampled = {view: values[indices] for view, values in discovery.items()}
        candidate = fit_consensus_model(resampled, view_names=view_names, rank=rank, ridge_alpha=ridge_alpha)
        for view in view_names:
            base = reference_bases[view]
            boot = _decoder_basis(candidate, view)
            if base.shape[1] != rank or boot.shape[1] != rank:
                gamma = float("nan")
                random_gamma = float("nan")
            else:
                gamma = float(np.linalg.norm(base.T @ boot, ord="fro") ** 2 / rank)
                random_matrix, _ = np.linalg.qr(rng.normal(size=base.shape), mode="reduced")
                random_gamma = float(np.linalg.norm(base.T @ random_matrix[:, :rank], ord="fro") ** 2 / rank)
            axis_cosine, axis_margin = _axis_alignment(reference.decoders[view], candidate.decoders[view])
            rows.append({
                "bootstrap": int(replicate),
                "operator": view,
                "subspace_congruence": gamma,
                "random_subspace_congruence": random_gamma,
                "axis_mean_cosine": axis_cosine,
                "axis_min_assignment_margin": axis_margin,
            })
    detail = pd.DataFrame(rows)
    summaries: list[dict[str, Any]] = []
    for view, group in detail.groupby("operator", observed=True, sort=True):
        lower = float(group["subspace_congruence"].quantile(0.025))
        null_upper = float(group["random_subspace_congruence"].quantile(0.975))
        axis_lower = float(group["axis_mean_cosine"].quantile(0.025))
        margin_median = float(group["axis_min_assignment_margin"].median())
        subspace_status = "SUBSPACE_RECURS" if lower > null_upper else "SUBSPACE_NOT_IDENTIFIED"
        axis_status = (
            "ANONYMOUS_AXES_ALIGNMENT_CANDIDATE"
            if subspace_status == "SUBSPACE_RECURS" and axis_lower > 0.5 and margin_median > 0.05
            else "FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY"
        )
        summaries.append({
            "operator": view,
            "subspace_congruence_lower": lower,
            "subspace_congruence_median": float(group["subspace_congruence"].median()),
            "random_subspace_null_upper": null_upper,
            "axis_mean_cosine_lower": axis_lower,
            "axis_min_assignment_margin_median": margin_median,
            "subspace_status": subspace_status,
            "axis_status": axis_status,
        })
    return detail, pd.DataFrame(summaries)


def _source_disjoint_feature_control(
    source_panel: pd.DataFrame,
    *,
    specs: list[ObservationSpec],
    representation: Any,
    scalers: dict[str, Any],
    confirmation_ids: list[str],
    seed: int,
) -> pd.DataFrame:
    """Use source-disjoint raw comments as a technical positive control.

    Agreement is a matched-author cosine in standardized feature space, with a
    randomly permuted author pairing as a null. It is not a personality
    reliability coefficient.
    """
    left_comments, right_comments = source_disjoint_partition(source_panel, seed=seed)
    rng = np.random.default_rng(seed + 1)
    rows: list[dict[str, Any]] = []
    for spec in specs:
        left_units = build_observations(left_comments, spec)
        right_units = build_observations(right_comments, spec)
        left_features = author_features_from_embeddings(left_units, representation.transform(left_units["text"]))
        right_features = author_features_from_embeddings(right_units, representation.transform(right_units["text"]))
        shared_ids = sorted(set(confirmation_ids).intersection(left_features["user_id"].astype(str)).intersection(right_features["user_id"].astype(str)))
        if len(shared_ids) < 8:
            rows.append({"operator": spec.name, "n_authors": len(shared_ids), "matched_mean_cosine": float("nan"), "permuted_mean_cosine": float("nan")})
            continue
        left = transform_feature_block(left_features, scaler=scalers[spec.name], user_ids=shared_ids)
        right = transform_feature_block(right_features, scaler=scalers[spec.name], user_ids=shared_ids)
        rows.append({
            "operator": spec.name,
            "n_authors": int(len(shared_ids)),
            "matched_mean_cosine": mean_row_cosine(left, right),
            "permuted_mean_cosine": mean_row_cosine(left, right[rng.permutation(len(right))]),
            "source_overlap_count": 0,
        })
    return pd.DataFrame(rows)


def _write_report(
    path: Path,
    *,
    output_dir: Path,
    selected_rank: int,
    selected_alpha: float,
    rank_status: str,
    selection: pd.DataFrame,
    cross_view: pd.DataFrame,
    variance: pd.DataFrame,
    control: pd.DataFrame,
    alignment: pd.DataFrame,
) -> None:
    """Write a bounded claim report for the fresh-cohort multiview experiment."""
    selection_table = selection.to_markdown(index=False, floatfmt=".3f")
    cross_table = cross_view.to_markdown(index=False, floatfmt=".3f")
    variance_table = variance.to_markdown(index=False, floatfmt=".3f")
    control_table = control.to_markdown(index=False, floatfmt=".3f")
    alignment_table = alignment.to_markdown(index=False, floatfmt=".3f") if not alignment.empty else "No nonzero shared rank was selected."
    text = f"""# SUICA V7.1 Fresh-Cohort Multiview Projection

## Scope

This is a label-free, fresh-author follow-up to the V7.1 boundary audit. The
E0 author cohort was explicitly excluded. Big Five, MBTI, clinical labels, and
external criteria were not loaded. Different slicing rules are treated as
parallel observation views rather than competing claims about one true cut.

## Selection

- Selected shared rank: `{selected_rank}`
- Selected encoder Ridge alpha: `{selected_alpha}`
- Selection metric: calibration-author bootstrap mean cross-view global R2,
  with the common source-comment representation fit on discovery authors only.
- Selection rule: the smallest rank within one bootstrap standard error of the
  calibration optimum.
- Rank status: `{rank_status}`. A boundary status is a lower bound within the
  admissible grid, not evidence that the true shared dimension is exactly the
  selected rank.

{selection_table}

## Confirmation Cross-View Results

`consensus_global_r2` predicts target-view features through only the fitted
shared subspace. `direct_global_r2` is a flexible direct Ridge reference.
`permuted_direct_global_r2` trains on broken discovery author correspondence.
The quantities assess author-aligned text structure, not personality.

{cross_table}

## Training Shared/Private Decomposition

Shared variance is an in-sample structural fraction after fitting the frozen
rank. Private effective rank is calculated on the remaining operator residual.
They describe operator-indexed text geometry and require confirmation
cross-view prediction above for any generalization interpretation.

{variance_table}

## Bootstrap Loading-Subspace Audit

Loading subspaces are compared in feature space under discovery-author
bootstrap resampling. `subspace_congruence_lower` must exceed the random
subspace null upper bound before a shared *subspace* is called recurrent.
Axis matching is deliberately stricter and remains anonymous; an axis that
does not survive the alignment margin is recorded as
`FACTOR_AXES_NOT_IDENTIFIED_SUBSPACE_ONLY`, not renamed or discarded.

{alignment_table}

## Source-Disjoint Technical Control

The matched cosine compares raw source-comment halves before slicing. It is a
technical positive control, not a trait-reliability estimate.

{control_table}

## Claim Boundary

The experiment may identify shared and operator-private **anonymous
author-relative text structure**. It does not identify psychological factors,
show a human trait, establish cross-language transport, or justify a clinical
score. The next step is operator-atlas mapping only if the confirmation and
permutation results show a nontrivial shared component.

## Artifacts

- Manifest: `{output_dir / 'run_manifest.json'}`
- Rank selection: `{output_dir / 'rank_selection.csv'}`
- Confirmation cross-view results: `{output_dir / 'cross_view_confirmation.csv'}`
- Shared/private summary: `{output_dir / 'shared_private_training_summary.csv'}`
- Source-disjoint control: `{output_dir / 'source_disjoint_feature_control.csv'}`
- Bootstrap alignment detail: `{output_dir / 'bootstrap_alignment.csv'}`
- Bootstrap alignment summary: `{output_dir / 'bootstrap_alignment_summary.csv'}`
- Frozen runtime: `{output_dir / 'artifacts/multiview_runtime.joblib'}`
- Replay fixture: `{output_dir / 'replay_fixture.json'}`
- Replay expected values: `{output_dir / 'replay_expected.npz'}`
- Artifact hash inventory: `{output_dir / 'artifact_inventory.json'}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    """Execute fresh-cohort E1 shared/private multiview analysis."""
    args = parse_args()
    config = _load_config(args.config)
    if args.seed is not None:
        config["seed"] = int(args.seed)
    if args.max_users is not None:
        config["max_users"] = int(args.max_users)
    if args.quick:
        config["max_users"] = min(int(config["max_users"]), 120)
        config["max_source_comments_per_user"] = min(int(config["max_source_comments_per_user"]), 16)
        config["max_source_tokens_per_user"] = min(int(config["max_source_tokens_per_user"]), 2048)
        config["max_units_per_user"] = min(int(config["max_units_per_user"]), 64)
        config["representation"]["max_features"] = min(int(config["representation"]["max_features"]), 2000)
        config["calibration_bootstrap_iterations"] = min(int(config.get("calibration_bootstrap_iterations", 99)), 19)
        config["alignment_bootstrap_iterations"] = min(int(config.get("alignment_bootstrap_iterations", 199)), 19)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir = args.output_dir or ROOT / "results" / "v7_multiview_projection" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report or ROOT / "reports" / "V7_MULTIVIEW_PROJECTION.md"
    excluded_users = _read_excluded_users(args.exclude_cohort)

    raw = _read_table(args.input)
    columns = [str(column) for column in raw.columns]
    column_map = {
        "user": _infer_column(columns, ["author", "user_id", "participant_id", "user", "id"], args.user_col, required=True),
        "text": _infer_column(columns, ["body", "text", "comment", "content", "message"], args.text_col, required=True),
        "order": _infer_column(columns, ["created_utc", "timestamp", "time", "date", "created_at"], args.order_col, required=False),
        "condition": _infer_column(columns, ["subreddit", "condition", "platform", "task", "forum"], args.condition_col, required=False),
    }
    canonical = canonicalize_comments(
        raw,
        user_col=str(column_map["user"]),
        text_col=str(column_map["text"]),
        order_col=column_map["order"],
        condition_col=column_map["condition"],
        min_tokens=int(config["min_tokens_per_unit"]),
        mask_personality_terms=bool(config["mask_personality_terms"]),
    )
    selected = select_reference_authors(
        canonical,
        min_comments_per_user=int(config["min_comments_per_user"]),
        max_users=int(config["max_users"]),
        seed=int(config["seed"]),
        exclude_user_ids=excluded_users,
        cohort_salt="v7.1-e1-fresh",
    )
    specs = _operator_specs(config)
    source_panel = prepare_source_panel(selected, specs[0])
    split_counts = source_panel.groupby("split", observed=True)["user_id"].nunique().to_dict()
    if any(int(split_counts.get(name, 0)) < 16 for name in ("discovery", "calibration", "confirmation")):
        raise RuntimeError(f"Fresh E1 cohort cannot support 3-way author split: {split_counts}")
    if set(source_panel["user_id"].astype(str)).intersection(excluded_users):
        raise RuntimeError("Fresh-cohort selection leaked an E0 author.")
    _schema_report(
        output_dir / "data_schema.md",
        source=args.input,
        raw=raw,
        column_map=column_map,
        canonical=canonical,
        selected=source_panel,
        mask_personality_terms=bool(config["mask_personality_terms"]),
        min_comments_per_user=int(config["min_comments_per_user"]),
        max_comments_per_user=int(config["max_source_comments_per_user"]),
    )
    _write_json(output_dir / "run_manifest.json", {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "input": str(args.input),
        "column_map": column_map,
        "excluded_e0_authors": int(len(excluded_users)),
        "fresh_e1_authors": int(source_panel["user_id"].nunique()),
        "author_split_counts": {key: int(value) for key, value in split_counts.items()},
        "claim_boundary": "No external labels were loaded. E1 measures anonymous multiview text structure only.",
    })

    representation_spec = RepresentationSpec(
        max_features=int(config["representation"]["max_features"]),
        ngram_min=int(config["representation"]["ngram_range"][0]),
        ngram_max=int(config["representation"]["ngram_range"][1]),
        svd_dimensions=int(config["representation"]["svd_dimensions"]),
        factor_count=1,
        seed=int(config["seed"]),
    )
    representation = fit_representation(
        source_panel.loc[source_panel["split"].eq("discovery")], representation_spec
    )
    runtime_path = output_dir / "artifacts" / "common_source_comment_representation.joblib"
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(representation, runtime_path)
    representation = joblib.load(runtime_path)

    feature_frames: dict[str, pd.DataFrame] = {}
    for spec in specs:
        units = build_observations(source_panel, spec)
        if units.empty:
            raise RuntimeError(f"E1 operator produced no units: {spec.name}")
        features = author_features_from_embeddings(units, representation.transform(units["text"]))
        feature_frames[spec.name] = features
        features.to_csv(output_dir / f"author_features_{spec.name}.csv", index=False)
    view_names = tuple(spec.name for spec in specs)
    discovery_ids = _aligned_user_ids(feature_frames, view_names, "discovery")
    calibration_ids = _aligned_user_ids(feature_frames, view_names, "calibration")
    confirmation_ids = _aligned_user_ids(feature_frames, view_names, "confirmation")
    if min(len(discovery_ids), len(calibration_ids), len(confirmation_ids)) < 16:
        raise RuntimeError("E1 operator alignment left too few authors in a split.")
    feature_names = common_feature_columns(feature_frames, view_names)
    scalers = fit_block_scalers(
        feature_frames,
        view_names=view_names,
        feature_names=feature_names,
        discovery_user_ids=discovery_ids,
    )
    discovery_blocks = _blocks(feature_frames, scalers=scalers, view_names=view_names, user_ids=discovery_ids)
    calibration_blocks = _blocks(feature_frames, scalers=scalers, view_names=view_names, user_ids=calibration_ids)
    admissible_rank_max = _admissible_rank_max(discovery_blocks)
    if admissible_rank_max < 1:
        raise RuntimeError(f"E1 discovery blocks have no nonzero admissible shared rank: {admissible_rank_max}.")
    if bool(config.get("full_admissible_rank_search", True)):
        rank_grid = list(range(admissible_rank_max + 1))
    else:
        rank_grid = sorted({int(value) for value in config["rank_grid"] if 0 <= int(value) <= admissible_rank_max})
    if not rank_grid:
        raise RuntimeError("E1 rank grid contains no admissible rank.")
    selection, selected_row = _selection_table(
        discovery_blocks,
        calibration_blocks,
        view_names=view_names,
        ranks=rank_grid,
        alphas=[float(value) for value in config["ridge_alpha_grid"]],
        bootstrap_iterations=int(config.get("calibration_bootstrap_iterations", 99)),
        seed=int(config["seed"]) + 313,
    )
    selected_rank = int(selected_row["shared_rank"])
    selected_alpha = float(selected_row["ridge_alpha"])
    rank_status = (
        "RANK_UNRESOLVED_AT_ADMISSIBLE_BOUNDARY"
        if selected_rank == admissible_rank_max
        else "RANK_SELECTED_BY_CALIBRATION_ONE_SE"
    )
    train_ids = [*discovery_ids, *calibration_ids]
    train_blocks = _blocks(feature_frames, scalers=scalers, view_names=view_names, user_ids=train_ids)
    final_model = fit_consensus_model(
        train_blocks, view_names=view_names, rank=selected_rank, ridge_alpha=selected_alpha
    )
    direct = fit_direct_predictors(train_blocks, view_names=view_names, ridge_alpha=selected_alpha)
    permuted = fit_direct_predictors(
        train_blocks,
        view_names=view_names,
        ridge_alpha=selected_alpha,
        permutation_seed=int(config["seed"]) + 77,
    )
    confirmation_blocks = _blocks(feature_frames, scalers=scalers, view_names=view_names, user_ids=confirmation_ids)
    cross_view = evaluate_cross_view(
        confirmation_blocks,
        model=final_model,
        direct_models=direct,
        permuted_models=permuted,
    )
    rng = np.random.default_rng(int(config["seed"]) + 88)
    cross_view["permuted_linear_cka"] = [
        linear_cka(confirmation_blocks[row.source_view], confirmation_blocks[row.target_view][rng.permutation(len(confirmation_ids))])
        for row in cross_view.itertuples(index=False)
    ]
    variance = pd.DataFrame([
        {
            "operator": view,
            "shared_variance_ratio_training": final_model.shared_variance_ratio[view],
            "private_effective_rank_training": final_model.private_effective_rank[view],
            "selected_shared_rank": selected_rank,
        }
        for view in view_names
    ])
    alignment_detail, alignment_summary = _bootstrap_alignment(
        discovery_blocks,
        view_names=view_names,
        rank=selected_rank,
        ridge_alpha=selected_alpha,
        iterations=int(config.get("alignment_bootstrap_iterations", 199)),
        seed=int(config["seed"]) + 617,
    )
    if selected_rank:
        view_shared = []
        for view in view_names:
            value = np.asarray(final_model.encoders[view].predict(confirmation_blocks[view]), dtype=float)
            view_shared.append(value[:, None] if value.ndim == 1 else value)
        shared_predictions = np.mean(view_shared, axis=0)
    else:
        shared_predictions = np.zeros((len(confirmation_ids), 0), dtype=float)
    shared_scores = pd.DataFrame({"user_id": confirmation_ids, "split": "confirmation"})
    for index in range(selected_rank):
        shared_scores[f"SU7-MS-{index + 1:04d}@v7.1"] = shared_predictions[:, index]
    shared_scores.to_csv(output_dir / "confirmation_shared_configuration.csv", index=False)
    control = _source_disjoint_feature_control(
        source_panel,
        specs=specs,
        representation=representation,
        scalers=scalers,
        confirmation_ids=confirmation_ids,
        seed=int(config["seed"]) + 99,
    )

    selection.to_csv(output_dir / "rank_selection.csv", index=False)
    cross_view.to_csv(output_dir / "cross_view_confirmation.csv", index=False)
    variance.to_csv(output_dir / "shared_private_training_summary.csv", index=False)
    control.to_csv(output_dir / "source_disjoint_feature_control.csv", index=False)
    alignment_detail.to_csv(output_dir / "bootstrap_alignment.csv", index=False)
    alignment_summary.to_csv(output_dir / "bootstrap_alignment_summary.csv", index=False)
    multiview_runtime_path = output_dir / "artifacts" / "multiview_runtime.joblib"
    joblib.dump({
        "representation": representation,
        "scalers": scalers,
        "final_model": final_model,
        "direct_models": direct,
        "permuted_models": permuted,
        "view_names": view_names,
        "feature_names": feature_names,
        "selected_rank": selected_rank,
        "selected_alpha": selected_alpha,
        "rank_status": rank_status,
        "config": config,
    }, multiview_runtime_path)
    replay_fixture = {
        "runtime_artifact": str(multiview_runtime_path),
        "confirmation_user_ids": confirmation_ids,
        "view_names": list(view_names),
        "feature_files": {
            view: {
                "path": str(output_dir / f"author_features_{view}.csv"),
                "sha256": sha256_file(output_dir / f"author_features_{view}.csv"),
            }
            for view in view_names
        },
        "expected_file": str(output_dir / "replay_expected.npz"),
        "comparison": {"rtol": 1e-8, "atol": 1e-10},
    }
    _write_json(output_dir / "replay_fixture.json", replay_fixture)
    replay_expected = cross_view.sort_values(["source_view", "target_view"], kind="stable").reset_index(drop=True)
    np.savez(
        output_dir / "replay_expected.npz",
        source_view=replay_expected["source_view"].to_numpy(str),
        target_view=replay_expected["target_view"].to_numpy(str),
        consensus_global_r2=replay_expected["consensus_global_r2"].to_numpy(float),
        direct_global_r2=replay_expected["direct_global_r2"].to_numpy(float),
        permuted_direct_global_r2=replay_expected["permuted_direct_global_r2"].to_numpy(float),
    )
    final_manifest = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "input": str(args.input),
        "column_map": column_map,
        "excluded_e0_authors": int(len(excluded_users)),
        "fresh_e1_authors": int(source_panel["user_id"].nunique()),
        "author_split_counts": {key: int(value) for key, value in split_counts.items()},
        "admissible_rank_max": admissible_rank_max,
        "selected_rank": selected_rank,
        "selected_alpha": selected_alpha,
        "rank_status": rank_status,
        "axis_statuses": alignment_summary[["operator", "subspace_status", "axis_status"]].to_dict(orient="records"),
        "runtime_artifact": str(multiview_runtime_path),
        "claim_boundary": "No external labels were loaded. E1 measures anonymous multiview text structure only; named axes require separate evidence.",
    }
    _write_json(output_dir / "run_manifest.json", final_manifest)
    _write_report(
        report_path,
        output_dir=output_dir,
        selected_rank=selected_rank,
        selected_alpha=selected_alpha,
        rank_status=rank_status,
        selection=selection,
        cross_view=cross_view,
        variance=variance,
        control=control,
        alignment=alignment_summary,
    )
    inventory = write_artifact_inventory(output_dir, output_dir / "artifact_inventory.json")
    print(json.dumps({
        "output_dir": str(output_dir),
        "report": str(report_path),
        "selected_rank": selected_rank,
        "selected_alpha": selected_alpha,
        "rank_status": rank_status,
        "artifact_files": inventory["n_files"],
        "confirmation_mean_consensus_r2": float(cross_view["consensus_global_r2"].mean()),
        "confirmation_mean_permuted_direct_r2": float(cross_view["permuted_direct_global_r2"].mean()),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
