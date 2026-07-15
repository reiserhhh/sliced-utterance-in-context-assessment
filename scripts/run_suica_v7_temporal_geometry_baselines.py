#!/usr/bin/env python3
"""Test registered V7 geometry against time, opportunity, and noise controls.

This is a label-free, within-PANDORA engineering analysis.  It neither trains a
personality predictor nor reads Big Five, MBTI, or other psychological labels.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v7_condition_opportunity import _eligible_users  # noqa: E402
from scripts.run_suica_v7_operator_smoke import DEFAULT_INPUT, _infer_column, _load_config, _read_table  # noqa: E402
from suica_core.v7_governance import append_ledger_event, write_artifact_inventory, write_run_manifest  # noqa: E402
from suica_core.v7_observations import canonicalize_comments, select_reference_authors  # noqa: E402
from suica_core.v7_temporal_geometry import (  # noqa: E402
    align_author_panels,
    alignment_auc,
    author_mean_deterministic_noise,
    author_mean_text_features,
    condition_transition_profiles,
    fit_feature_scaler,
    fit_opportunity_residualizer,
    fit_text_representation,
    linear_transport_r2,
    random_source_partition,
    relative_distance_spearman,
    structural_opportunity_profiles,
    summarize_numeric,
    temporal_source_partition,
)


DEFAULT_CONFIG = ROOT / "configs" / "v7_temporal_geometry_baselines.json"
DEFAULT_E0 = ROOT / "results" / "v7_operator_boundary_audit" / "e0_full_20260714" / "scores_native.csv"
DEFAULT_E1 = ROOT / "results" / "v7_multiview_projection" / "e1_full_20260714" / "author_features_native.csv"
DEFAULT_E2_CONFIG = ROOT / "configs" / "v7_condition_opportunity.json"
DEFAULT_E4_CONFIG = ROOT / "configs" / "v7_operator_family_registry.json"


def parse_args() -> argparse.Namespace:
    """Parse a frozen time-separated V7 control run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--e0-cohort", type=Path, default=DEFAULT_E0)
    parser.add_argument("--e1-cohort", type=Path, default=DEFAULT_E1)
    parser.add_argument("--e2-config", type=Path, default=DEFAULT_E2_CONFIG)
    parser.add_argument("--e4-config", type=Path, default=DEFAULT_E4_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _read_ids(path: Path) -> set[str]:
    """Read local prior-cohort IDs only to exclude them from the new cohort."""
    if not path.exists():
        raise FileNotFoundError(f"Required prior V7 cohort artifact is missing: {path}")
    return set(pd.read_csv(path, usecols=["user_id"])["user_id"].dropna().astype(str))


def _prior_exclusions(
    canonical: pd.DataFrame,
    *,
    e0_path: Path,
    e1_path: Path,
    e2_config_path: Path,
    e4_config_path: Path,
) -> set[str]:
    """Reconstruct E0--E4 selections without persisting their raw author IDs."""
    excluded = _read_ids(e0_path).union(_read_ids(e1_path))
    e2 = _load_config(e2_config_path)
    e2_eligible = _eligible_users(canonical, e2)
    e2_selected = select_reference_authors(
        canonical.loc[canonical["user_id"].astype(str).isin(e2_eligible)].copy(),
        min_comments_per_user=int(e2["min_comments_per_user"]),
        max_users=int(e2["max_users"]),
        seed=int(e2["seed"]),
        exclude_user_ids=excluded,
        cohort_salt="v7.1-e2-condition-opportunity-v1",
    )
    excluded = excluded.union(set(e2_selected["user_id"].astype(str)))
    e4 = _load_config(e4_config_path)
    e4_selected = select_reference_authors(
        canonical,
        min_comments_per_user=int(e4["min_comments_per_user"]),
        max_users=int(e4["max_users"]),
        seed=int(e4["seed"]),
        exclude_user_ids=excluded,
        cohort_salt="v7.2-registered-operator-family-1",
    )
    return excluded.union(set(e4_selected["user_id"].astype(str)))


def _split_arrays(frame: pd.DataFrame, *, feature_columns: list[str]) -> dict[str, np.ndarray]:
    """Extract identically ordered arrays from an author-panel frame."""
    values: dict[str, np.ndarray] = {}
    for split in ("discovery", "calibration", "confirmation"):
        values[split] = frame.loc[frame["split"].eq(split), feature_columns].to_numpy(float)
    return values


def _record(
    *,
    representation: str,
    variant: str,
    left: pd.DataFrame,
    right: pd.DataFrame,
    feature_columns: list[str],
) -> dict[str, Any]:
    """Construct train/confirmation arrays after asserting panel alignment."""
    if not left[["user_id", "split"]].equals(right[["user_id", "split"]]):
        raise RuntimeError("Early/late author alignment changed before metric construction.")
    left_parts = _split_arrays(left, feature_columns=feature_columns)
    right_parts = _split_arrays(right, feature_columns=feature_columns)
    return {
        "representation": representation,
        "variant": variant,
        "left_train": np.vstack([left_parts["discovery"], left_parts["calibration"]]),
        "right_train": np.vstack([right_parts["discovery"], right_parts["calibration"]]),
        "left_confirmation": left_parts["confirmation"],
        "right_confirmation": right_parts["confirmation"],
        "n_features": int(len(feature_columns)),
    }


def _actual_metrics(record: dict[str, Any], *, alpha: float) -> dict[str, float]:
    """Calculate registered metrics on the untouched confirmation authors."""
    return {
        "alignment_auc": alignment_auc(record["left_confirmation"], record["right_confirmation"]),
        "relative_distance_spearman": relative_distance_spearman(record["left_confirmation"], record["right_confirmation"]),
        "linear_transport_r2": linear_transport_r2(
            record["left_train"], record["right_train"], record["left_confirmation"], record["right_confirmation"], alpha=alpha,
        ),
    }


def _null_metrics(record: dict[str, Any], *, pairing_train: np.ndarray, pairing_confirmation: np.ndarray, alpha: float) -> dict[str, float]:
    """Break author correspondence while preserving each panel's marginal data."""
    return {
        "alignment_auc": alignment_auc(record["left_confirmation"], record["right_confirmation"], pairing=pairing_confirmation),
        "relative_distance_spearman": relative_distance_spearman(record["left_confirmation"], record["right_confirmation"], pairing=pairing_confirmation),
        "linear_transport_r2": linear_transport_r2(
            record["left_train"], record["right_train"][pairing_train],
            record["left_confirmation"], record["right_confirmation"], alpha=alpha,
        ),
    }


def _studentized_max_t(actual: pd.DataFrame, null: pd.DataFrame) -> pd.DataFrame:
    """Apply a synchronized studentized max-T correction across endpoints."""
    output = actual.copy()
    null_index = {
        (str(rep), str(variant), str(metric)): group.sort_values("permutation")
        for (rep, variant, metric), group in null.groupby(["representation", "variant", "metric"], observed=True, sort=False)
    }
    z_values: dict[tuple[str, str, str], float] = {}
    null_z: dict[tuple[str, str, str], pd.Series] = {}
    raw_p: dict[tuple[str, str, str], float] = {}
    for row in output.itertuples(index=False):
        key = (str(row.representation), str(row.variant), str(row.metric))
        values = null_index[key]["statistic"].to_numpy(float)
        center = float(np.mean(values))
        scale = max(float(np.std(values, ddof=1)), 1e-12)
        z_values[key] = float((row.statistic - center) / scale)
        null_z[key] = (null_index[key]["statistic"] - center) / scale
        raw_p[key] = float((1 + np.sum(values >= row.statistic)) / (len(values) + 1))
    permutations = sorted(null["permutation"].unique().tolist())
    max_z = []
    for iteration in permutations:
        max_z.append(max(float(series.loc[null_index[key]["permutation"].eq(iteration)].iloc[0]) for key, series in null_z.items()))
    max_z_array = np.asarray(max_z, dtype=float)
    output["observed_z"] = [z_values[(str(row.representation), str(row.variant), str(row.metric))] for row in output.itertuples(index=False)]
    output["raw_permutation_p"] = [raw_p[(str(row.representation), str(row.variant), str(row.metric))] for row in output.itertuples(index=False)]
    output["max_t_fwer_p"] = [float((1 + np.sum(max_z_array >= value)) / (len(max_z_array) + 1)) for value in output["observed_z"]]
    positive = np.select(
        [output["metric"].eq("alignment_auc"), output["metric"].eq("relative_distance_spearman"), output["metric"].eq("linear_transport_r2")],
        [output["statistic"].gt(0.5), output["statistic"].gt(0.0), output["statistic"].gt(0.0)],
        default=False,
    )
    output["positive_direction"] = positive.astype(bool)
    output["status"] = np.where(
        output["max_t_fwer_p"].le(0.05) & output["positive_direction"], "FWER_POSITIVE_SUPPORTED",
        np.where(output["max_t_fwer_p"].le(0.05), "FWER_NONPOSITIVE_DIFFERENCE", "UNRESOLVED"),
    )
    return output


def _decision(endpoints: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    """Make a bounded technical decision without psychological interpretation."""
    thresholds = config["thresholds"]
    raw = endpoints.loc[endpoints["variant"].eq("raw_text")].copy()
    supported_representations: list[str] = []
    for representation, group in raw.groupby("representation", observed=True):
        alignment = group.loc[group["metric"].eq("alignment_auc")].iloc[0]
        geometry = group.loc[group["metric"].eq("relative_distance_spearman")].iloc[0]
        if (
            float(alignment.statistic) >= float(thresholds["min_alignment_auc"])
            and float(geometry.statistic) >= float(thresholds["min_relative_distance_spearman"])
            and str(alignment.status) == "FWER_POSITIVE_SUPPORTED"
            and str(geometry.status) == "FWER_POSITIVE_SUPPORTED"
        ):
            supported_representations.append(str(representation))
    raw_auc = raw.loc[raw["metric"].eq("alignment_auc"), "statistic"]
    opportunity_auc = endpoints.loc[
        endpoints["variant"].eq("opportunity_only") & endpoints["metric"].eq("alignment_auc"), "statistic"
    ]
    best_raw_auc = float(raw_auc.max()) if len(raw_auc) else float("nan")
    opportunity_value = float(opportunity_auc.iloc[0]) if len(opportunity_auc) else float("nan")
    competitive = bool(np.isfinite(best_raw_auc) and np.isfinite(opportunity_value) and opportunity_value >= best_raw_auc - float(thresholds["opportunity_competitive_auc_margin"]))
    noise_rows = endpoints.loc[endpoints["variant"].eq("deterministic_noise")]
    noise_supported = bool(noise_rows["status"].eq("FWER_POSITIVE_SUPPORTED").any())
    status = "TECHNICAL_TEMPORAL_GEOMETRY_SUPPORTED" if supported_representations and not noise_supported else "TEMPORAL_GEOMETRY_UNRESOLVED"
    return {
        "status": status,
        "supported_raw_text_representations": supported_representations,
        "best_raw_text_alignment_auc": best_raw_auc,
        "opportunity_only_alignment_auc": opportunity_value,
        "opportunity_control_competitive": competitive,
        "deterministic_noise_has_fwer_supported_endpoint": noise_supported,
        "claim_boundary": "Within-PANDORA time-separated technical geometry only. The result cannot identify personality, eliminate context/selection, or establish cross-occasion psychological measurement.",
    }


def _summary_table(frame: pd.DataFrame, title: str) -> str:
    """Render a compact report table even when a support gate leaves it empty."""
    return f"### {title}\n\n{frame.to_markdown(index=False, floatfmt='.3f') if not frame.empty else 'No rows.'}\n"


def _write_report(path: Path, *, output_dir: Path, endpoints: pd.DataFrame, decision: dict[str, Any], panel_summary: pd.DataFrame, condition_summary: pd.DataFrame) -> None:
    """Write a bounded, readable report without raw text or author identifiers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "# SUICA V7 Time-Separated Geometry Baselines\n\n"
    text += "## Design\n\n"
    text += (
        "Each new author contributes an earliest and latest source-comment panel before any vectorization. "
        "The panels are source-disjoint and selected from a fresh cohort excluding E0--E4. "
        "TF-IDF/SVD representations are fit on discovery authors only; scaling, opportunity sensitivity surfaces, "
        "and linear transport maps are fit without confirmation authors.\n\n"
        "Subreddit/topic choice is retained as part of the text process. The opportunity-only and opportunity-adjusted "
        "arms concern text amount and format only; they are sensitivity controls, not a claim that selection is noise.\n\n"
    )
    text += _summary_table(panel_summary, "Time-Panel Support") + "\n"
    text += _summary_table(condition_summary, "Condition-Selection Descriptives (Not Residualized)") + "\n"
    text += _summary_table(endpoints, "Confirmation Endpoints") + "\n"
    text += "## Decision\n\n```json\n" + json.dumps(decision, ensure_ascii=False, indent=2) + "\n```\n\n"
    text += "## Interpretation Boundary\n\n"
    text += (
        "`FWER_POSITIVE_SUPPORTED` means only that a registered technical endpoint exceeded its correspondence-permuted family in its meaningful direction under this corpus and time split. `FWER_NONPOSITIVE_DIFFERENCE` is not positive evidence. "
        "It does not name a factor, prove an author core, or license personality/clinical interpretation. A competitive opportunity-only arm is a warning that expression opportunity remains an alternative explanation, not a reason to erase selection or language content.\n\n"
        f"Artifacts: `{output_dir}`\n"
    )
    path.write_text(text, encoding="utf-8")


def main() -> int:
    """Run one fresh, predeclared V7 temporal-control family."""
    args = parse_args()
    config = _load_config(args.config)
    if args.quick:
        config["max_users"] = min(int(config["max_users"]), 120)
        config["min_comments_per_user"] = min(int(config["min_comments_per_user"]), 32)
        config["min_comments_per_half"] = min(int(config["min_comments_per_half"]), 12)
        config["max_comments_per_half"] = min(int(config["max_comments_per_half"]), 12)
        config["permutation_iterations"] = min(int(config["permutation_iterations"]), 29)
        for spec in config["representations"]:
            spec["max_features"] = min(int(spec["max_features"]), 2000)
            spec["svd_dimensions"] = min(int(spec["svd_dimensions"]), 12)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "run_manifest.json", repository_root=ROOT,
        input_paths=[args.input, args.config, args.e0_cohort, args.e1_cohort, args.e2_config, args.e4_config],
        config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_core" / "v7_temporal_geometry.py", ROOT / "suica_core" / "v7_observations.py"],
        estimand_id="V7.3-W3-temporal-relative-geometry", external_labels_read=False, raw_identifiers_persisted=False,
    )
    raw = _read_table(args.input)
    columns = [str(column) for column in raw.columns]
    column_map = {
        "user": _infer_column(columns, ["author", "user_id", "participant_id", "user", "id"], None, required=True),
        "text": _infer_column(columns, ["body", "text", "comment", "content", "message"], None, required=True),
        "order": _infer_column(columns, ["created_utc", "timestamp", "time", "date", "created_at"], None, required=False),
        "condition": _infer_column(columns, ["subreddit", "condition", "platform", "task", "forum"], None, required=False),
    }
    canonical = canonicalize_comments(raw, user_col=str(column_map["user"]), text_col=str(column_map["text"]), order_col=column_map["order"], condition_col=column_map["condition"], min_tokens=int(config["min_tokens_per_comment"]))
    excluded = _prior_exclusions(canonical, e0_path=args.e0_cohort, e1_path=args.e1_cohort, e2_config_path=args.e2_config, e4_config_path=args.e4_config)
    selected = select_reference_authors(
        canonical, min_comments_per_user=int(config["min_comments_per_user"]), max_users=int(config["max_users"]),
        seed=int(config["seed"]), exclude_user_ids=excluded, cohort_salt="v7.3-w3-temporal-geometry-1",
    )
    early_source, late_source, support = temporal_source_partition(
        selected, min_comments_per_half=int(config["min_comments_per_half"]), max_comments_per_half=int(config["max_comments_per_half"]),
    )
    if early_source.empty or late_source.empty:
        raise RuntimeError("No fresh authors passed the declared time-panel support gate.")
    split_counts = support.groupby("split", observed=True)["user_id"].nunique().to_dict()
    if min(int(split_counts.get(split, 0)) for split in ("discovery", "calibration", "confirmation")) < 16:
        raise RuntimeError(f"Insufficient fresh temporal split support: {split_counts}")
    if set(early_source["source_row"].astype(int)).intersection(set(late_source["source_row"].astype(int))):
        raise RuntimeError("Temporal panels contain source-row overlap.")
    early_opportunity = structural_opportunity_profiles(early_source)
    late_opportunity = structural_opportunity_profiles(late_source)
    opportunity_columns = [column for column in early_opportunity.columns if column not in {"user_id", "split"}]
    early_opportunity, late_opportunity = align_author_panels(early_opportunity, late_opportunity, feature_columns=opportunity_columns)
    condition_profile = condition_transition_profiles(early_source, late_source)
    if not early_opportunity[["user_id", "split"]].equals(late_opportunity[["user_id", "split"]]):
        raise RuntimeError("Opportunity profiles lost early/late author alignment.")
    train_users = set(early_opportunity.loc[early_opportunity["split"].ne("confirmation"), "user_id"].astype(str))
    opportunity_scaler = fit_feature_scaler(early_opportunity, late_opportunity, feature_columns=opportunity_columns, train_user_ids=train_users)
    opportunity_left = opportunity_scaler.transform(early_opportunity[opportunity_columns].to_numpy(float))
    opportunity_right = opportunity_scaler.transform(late_opportunity[opportunity_columns].to_numpy(float))
    records: list[dict[str, Any]] = []
    for index, spec in enumerate(config["representations"]):
        discovery_text = pd.concat([
            early_source.loc[early_source["split"].eq("discovery"), "text"],
            late_source.loc[late_source["split"].eq("discovery"), "text"],
        ], ignore_index=True)
        runtime = fit_text_representation(discovery_text, spec, seed=int(config["seed"]) + index)
        early_features, feature_columns = author_mean_text_features(early_source, runtime)
        late_features, _ = author_mean_text_features(late_source, runtime)
        early_features, late_features = align_author_panels(early_features, late_features, feature_columns=feature_columns)
        if not early_features[["user_id", "split"]].equals(early_opportunity[["user_id", "split"]]):
            raise RuntimeError(f"Representation {runtime.name} has inconsistent author support.")
        scaler = fit_feature_scaler(early_features, late_features, feature_columns=feature_columns, train_user_ids=train_users)
        left = scaler.transform(early_features[feature_columns].to_numpy(float))
        right = scaler.transform(late_features[feature_columns].to_numpy(float))
        records.append(_record(representation=runtime.name, variant="raw_text", left=pd.DataFrame({"user_id": early_features["user_id"], "split": early_features["split"], **{column: left[:, position] for position, column in enumerate(feature_columns)}}), right=pd.DataFrame({"user_id": late_features["user_id"], "split": late_features["split"], **{column: right[:, position] for position, column in enumerate(feature_columns)}}), feature_columns=feature_columns))
        train_mask = early_features["split"].ne("confirmation").to_numpy(bool)
        residualizer = fit_opportunity_residualizer(left, right, opportunity_left, opportunity_right, train_mask=train_mask, alpha=float(config["opportunity_ridge_alpha"]))
        left_adjusted = residualizer.residualize(left, opportunity_left)
        right_adjusted = residualizer.residualize(right, opportunity_right)
        records.append(_record(representation=runtime.name, variant="opportunity_adjusted_text", left=pd.DataFrame({"user_id": early_features["user_id"], "split": early_features["split"], **{column: left_adjusted[:, position] for position, column in enumerate(feature_columns)}}), right=pd.DataFrame({"user_id": late_features["user_id"], "split": late_features["split"], **{column: right_adjusted[:, position] for position, column in enumerate(feature_columns)}}), feature_columns=feature_columns))
    records.append(_record(
        representation="STRUCTURAL_OPPORTUNITY", variant="opportunity_only", left=early_opportunity, right=late_opportunity, feature_columns=opportunity_columns,
    ))
    early_noise, noise_columns = author_mean_deterministic_noise(early_source, dimensions=int(config["noise_dimensions"]), seed=int(config["seed"]) + 991)
    late_noise, _ = author_mean_deterministic_noise(late_source, dimensions=int(config["noise_dimensions"]), seed=int(config["seed"]) + 991)
    early_noise, late_noise = align_author_panels(early_noise, late_noise, feature_columns=noise_columns)
    noise_scaler = fit_feature_scaler(early_noise, late_noise, feature_columns=noise_columns, train_user_ids=train_users)
    for frame in (early_noise, late_noise):
        frame.loc[:, noise_columns] = noise_scaler.transform(frame[noise_columns].to_numpy(float))
    records.append(_record(representation="DETERMINISTIC_SOURCE_NOISE", variant="deterministic_noise", left=early_noise, right=late_noise, feature_columns=noise_columns))
    actual_rows: list[dict[str, Any]] = []
    for record in records:
        for metric, statistic in _actual_metrics(record, alpha=float(config["ridge_alpha"])).items():
            actual_rows.append({"representation": record["representation"], "variant": record["variant"], "metric": metric, "statistic": statistic, "n_features": record["n_features"], "n_confirmation_authors": int(len(record["left_confirmation"]))})
    actual = pd.DataFrame(actual_rows)
    n_train = {len(record["left_train"]) for record in records}
    n_confirmation = {len(record["left_confirmation"]) for record in records}
    if len(n_train) != 1 or len(n_confirmation) != 1:
        raise RuntimeError("Registered endpoints do not share common author support for synchronized max-T.")
    rng = np.random.default_rng(int(config["seed"]) + 887)
    null_rows: list[dict[str, Any]] = []
    for iteration in range(int(config["permutation_iterations"])):
        pairing_train = rng.permutation(next(iter(n_train)))
        pairing_confirmation = rng.permutation(next(iter(n_confirmation)))
        for record in records:
            for metric, statistic in _null_metrics(record, pairing_train=pairing_train, pairing_confirmation=pairing_confirmation, alpha=float(config["ridge_alpha"])).items():
                null_rows.append({"permutation": int(iteration), "representation": record["representation"], "variant": record["variant"], "metric": metric, "statistic": statistic})
    null = pd.DataFrame(null_rows)
    endpoints = _studentized_max_t(actual, null)
    decision = _decision(endpoints, config)
    panel_summary = summarize_numeric(support.drop(columns=["user_id"]), columns=[column for column in support if column not in {"user_id", "split"}])
    condition_summary = summarize_numeric(condition_profile.drop(columns=["user_id"]), columns=[column for column in condition_profile if column not in {"user_id", "split"}])
    endpoints.to_csv(args.output_dir / "confirmation_endpoints.csv", index=False)
    null.to_parquet(args.output_dir / "studentized_max_t_null.parquet", index=False)
    panel_summary.to_csv(args.output_dir / "time_panel_support_summary.csv", index=False)
    condition_summary.to_csv(args.output_dir / "condition_transition_summary.csv", index=False)
    (args.output_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({
        "column_map": column_map,
        "n_prior_author_exclusions": int(len(excluded)),
        "n_selected_authors": int(selected["user_id"].nunique()),
        "n_time_panel_authors": int(support["user_id"].nunique()),
        "split_counts": {key: int(value) for key, value in split_counts.items()},
        "source_overlap_count": 0,
        "raw_identifiers_persisted": False,
        "multiplicity_family": str(config["multiplicity_family"]),
        "max_t_permutations": int(config["permutation_iterations"]),
        "claim_boundary": decision["claim_boundary"],
    })
    (args.output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_report(args.report, output_dir=args.output_dir, endpoints=endpoints, decision=decision, panel_summary=panel_summary, condition_summary=condition_summary)
    append_ledger_event(args.output_dir / "evidence_ledger.jsonl", {"estimand_id": manifest["estimand_id"], "status": decision["status"], "claim_boundary": decision["claim_boundary"]})
    inventory = write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    print(json.dumps({"output_dir": str(args.output_dir), "report": str(args.report), "status": decision["status"], "n_endpoints": int(len(endpoints)), "artifact_files": inventory["n_files"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
