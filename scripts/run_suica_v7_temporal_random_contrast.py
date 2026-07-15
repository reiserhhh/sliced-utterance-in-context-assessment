#!/usr/bin/env python3
"""Contrast time-separated V7 geometry with random source-half sampling.

The same fresh authors and source budget are used in both arms.  This isolates
the extra cost of chronological separation from ordinary source-sampling
variation.  It is a technical within-corpus contrast, not a trait-retest test.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v7_operator_smoke import DEFAULT_INPUT, _infer_column, _load_config, _read_table  # noqa: E402
from scripts.run_suica_v7_temporal_geometry_baselines import (  # noqa: E402
    DEFAULT_E0, DEFAULT_E1, DEFAULT_E2_CONFIG, DEFAULT_E4_CONFIG, _prior_exclusions,
)
from suica_core.v7_governance import append_ledger_event, write_artifact_inventory, write_run_manifest  # noqa: E402
from suica_core.v7_observations import canonicalize_comments, select_reference_authors  # noqa: E402
from suica_core.v7_temporal_geometry import (  # noqa: E402
    FeatureScaler, align_author_panels, alignment_auc, alignment_contributions,
    author_mean_text_features, fit_text_representation, linear_transport_r2,
    random_source_partition, relative_distance_spearman, temporal_source_partition,
)


DEFAULT_CONFIG = ROOT / "configs" / "v7_temporal_geometry_baselines.json"


def parse_args() -> argparse.Namespace:
    """Parse a same-author temporal-versus-random contrast request."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--e0-cohort", type=Path, default=DEFAULT_E0)
    parser.add_argument("--e1-cohort", type=Path, default=DEFAULT_E1)
    parser.add_argument("--e2-config", type=Path, default=DEFAULT_E2_CONFIG)
    parser.add_argument("--e4-config", type=Path, default=DEFAULT_E4_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=999)
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _shared_training_scaler(frames: list[pd.DataFrame], columns: list[str]) -> FeatureScaler:
    """Fit one coordinate scale across both panel designs using non-test authors."""
    values = np.vstack([
        frame.loc[frame["split"].ne("confirmation"), columns].to_numpy(float)
        for frame in frames
    ])
    return FeatureScaler(mean=values.mean(axis=0, keepdims=True), scale=np.maximum(values.std(axis=0, keepdims=True), 1e-12))


def _arrays(frame: pd.DataFrame, columns: list[str], split: str) -> np.ndarray:
    """Extract one ordered author split after all alignment checks."""
    return frame.loc[frame["split"].eq(split), columns].to_numpy(float)


def _paired_sign_flip(deltas: dict[str, np.ndarray], *, seed: int, iterations: int) -> dict[str, float]:
    """Use a shared author-level sign-flip family for AUC contrast only.

    Rank contributions share strangers, so this is intentionally reported as a
    paired descriptive randomization control rather than a population theorem.
    """
    names = sorted(deltas)
    rng = np.random.default_rng(int(seed))
    observed = {name: float(np.mean(deltas[name])) for name in names}
    maximum: list[float] = []
    for _ in range(int(iterations)):
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=len(next(iter(deltas.values()))))
        maximum.append(max(abs(float(np.mean(deltas[name] * signs))) for name in names))
    maximum_array = np.asarray(maximum, dtype=float)
    return {name: float((1 + np.sum(maximum_array >= abs(value))) / (len(maximum_array) + 1)) for name, value in observed.items()}


def _bootstrap_ci(delta: np.ndarray, *, seed: int, iterations: int) -> tuple[float, float]:
    """Return a paired author-cluster bootstrap interval for a mean contrast."""
    rng = np.random.default_rng(int(seed))
    values = []
    for _ in range(int(iterations)):
        indices = rng.integers(0, len(delta), size=len(delta))
        values.append(float(np.mean(delta[indices])))
    return float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def _nested_partition_author_bootstrap_ci(delta_by_partition: np.ndarray, *, seed: int, iterations: int) -> tuple[float, float]:
    """Resample both random partitions and authors for the design contrast.

    One random half split underestimates uncertainty because the baseline itself
    is a random design realization. This nested interval treats its registered
    random partition family and confirmation authors as separate uncertainty
    sources. It remains a descriptive Monte Carlo interval, not a trait test.
    """
    values = np.asarray(delta_by_partition, dtype=float)
    if values.ndim != 2 or values.shape[0] < 2 or values.shape[1] < 2:
        raise ValueError("Nested temporal contrast needs >=2 random partitions and >=2 authors.")
    rng = np.random.default_rng(int(seed))
    draws: list[float] = []
    for _ in range(int(iterations)):
        partitions = rng.integers(0, values.shape[0], size=values.shape[0])
        authors = rng.integers(0, values.shape[1], size=values.shape[1])
        draws.append(float(values[np.ix_(partitions, authors)].mean()))
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def _report(path: Path, *, output_dir: Path, table: pd.DataFrame, support: dict[str, int]) -> None:
    """Write a narrowly interpreted same-author contrast report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# SUICA V7 Temporal vs Random-Half Contrast\n\n"
        "## Design\n\n"
        "The same fresh authors and the same fixed number of source comments per panel are evaluated twice: chronological earliest-versus-latest and random source halves. TF-IDF/SVD is fitted only on discovery authors. A shared scaler is fitted only on discovery/calibration panels. No external labels are read.\n\n"
        f"- Time-panel authors: `{support['temporal']}`\n"
        f"- Random-panel authors: `{support['random']}`\n"
        f"- Confirmation authors: `{support['confirmation']}`\n\n"
        "## Results\n\n"
        f"{table.to_markdown(index=False, floatfmt='.4f')}\n\n"
        "## Boundary\n\n"
        "A negative temporal-minus-random AUC means chronological separation made same-author matching harder than ordinary random sampling for this corpus and source budget. It does not prove a personality change, identify a psychological factor, or say that random halves are a clinically meaningful occasion. The paired sign-flip p-value is a descriptive family control over author-level rank contributions.\n\n"
        f"Artifacts: `{output_dir}`\n",
        encoding="utf-8",
    )


def main() -> int:
    """Run the same-author temporal/rand-half contrast without psychological labels."""
    args = parse_args()
    config = _load_config(args.config)
    if args.quick:
        config["max_users"] = min(int(config["max_users"]), 120)
        config["min_comments_per_user"] = min(int(config["min_comments_per_user"]), 32)
        config["min_comments_per_half"] = min(int(config["min_comments_per_half"]), 12)
        config["max_comments_per_half"] = min(int(config["max_comments_per_half"]), 12)
        for spec in config["representations"]:
            spec["max_features"] = min(int(spec["max_features"]), 2000)
            spec["svd_dimensions"] = min(int(spec["svd_dimensions"]), 12)
        config["random_partition_repetitions"] = min(int(config["random_partition_repetitions"]), 5)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    manifest = write_run_manifest(
        args.output_dir / "run_manifest.json", repository_root=ROOT,
        input_paths=[args.input, args.config, args.e0_cohort, args.e1_cohort, args.e2_config, args.e4_config], config_path=args.config,
        code_paths=[Path(__file__), ROOT / "suica_core" / "v7_temporal_geometry.py", ROOT / "scripts" / "run_suica_v7_temporal_geometry_baselines.py"],
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
    if "order_observed" not in canonical or not bool(canonical["order_observed"].all()):
        missing = int((~canonical.get("order_observed", pd.Series(False, index=canonical.index)).astype(bool)).sum())
        decision = {
            "status": "REFUSE_TEMPORAL_ORDER_PROVENANCE",
            "n_records_without_observed_numeric_order": missing,
            "claim_boundary": "Input row order may support deterministic slicing but cannot support a temporal V7 contrast.",
        }
        (args.output_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest.update({"temporal_order_provenance": "REFUSED", "raw_identifiers_persisted": False, "claim_boundary": decision["claim_boundary"]})
        (args.output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text("# SUICA V7 Temporal vs Random-Half Contrast\n\nStatus: REFUSE_TEMPORAL_ORDER_PROVENANCE. Input row order was not accepted as a time variable.\n", encoding="utf-8")
        write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
        print(json.dumps(decision, ensure_ascii=False, indent=2))
        return 2
    excluded = _prior_exclusions(canonical, e0_path=args.e0_cohort, e1_path=args.e1_cohort, e2_config_path=args.e2_config, e4_config_path=args.e4_config)
    selected = select_reference_authors(canonical, min_comments_per_user=int(config["min_comments_per_user"]), max_users=int(config["max_users"]), seed=int(config["seed"]), exclude_user_ids=excluded, cohort_salt="v7.3-w3-temporal-geometry-1")
    temporal_left, temporal_right, temporal_support = temporal_source_partition(selected, min_comments_per_half=int(config["min_comments_per_half"]), max_comments_per_half=int(config["max_comments_per_half"]))
    random_panels: list[tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]] = []
    for partition_index in range(int(config["random_partition_repetitions"])):
        random_panels.append(random_source_partition(selected, seed=int(config["seed"]) + 313 + partition_index, min_comments_per_half=int(config["min_comments_per_half"]), max_comments_per_half=int(config["max_comments_per_half"])))
    for name, left, right in [("temporal", temporal_left, temporal_right), *[(f"random_{index:03d}", left, right) for index, (left, right, _) in enumerate(random_panels)]]:
        if left.empty or right.empty or set(left["source_row"].astype(int)).intersection(set(right["source_row"].astype(int))):
            raise RuntimeError(f"{name} panel failed its source-disjoint support gate.")
    for left, _, _ in random_panels:
        if set(temporal_left["user_id"].astype(str)) != set(left["user_id"].astype(str)):
            raise RuntimeError("Temporal and random panels do not retain the same author cohort.")
    discovery_text = selected.loc[selected["split"].eq("discovery"), "text"]
    rows: list[dict[str, Any]] = []
    deltas: dict[str, np.ndarray] = {}
    random_metric_rows: list[dict[str, Any]] = []
    for index, spec in enumerate(config["representations"]):
        runtime = fit_text_representation(discovery_text, spec, seed=int(config["seed"]) + index)
        temporal_raw_left, feature_columns = author_mean_text_features(temporal_left, runtime)
        temporal_raw_right, _ = author_mean_text_features(temporal_right, runtime)
        temporal_frame_left, temporal_frame_right = align_author_panels(temporal_raw_left, temporal_raw_right, feature_columns=feature_columns)
        scaler = _shared_training_scaler([temporal_frame_left, temporal_frame_right], feature_columns)
        temporal_left_scaled = scaler.transform(temporal_frame_left[feature_columns].to_numpy(float))
        temporal_right_scaled = scaler.transform(temporal_frame_right[feature_columns].to_numpy(float))
        temporal_arrays = {
            "left_train": temporal_left_scaled[temporal_frame_left["split"].ne("confirmation").to_numpy(bool)],
            "right_train": temporal_right_scaled[temporal_frame_right["split"].ne("confirmation").to_numpy(bool)],
            "left_confirmation": temporal_left_scaled[temporal_frame_left["split"].eq("confirmation").to_numpy(bool)],
            "right_confirmation": temporal_right_scaled[temporal_frame_right["split"].eq("confirmation").to_numpy(bool)],
        }
        temporal_contribution = alignment_contributions(temporal_arrays["left_confirmation"], temporal_arrays["right_confirmation"])
        random_deltas: list[np.ndarray] = []
        random_metrics: list[dict[str, float]] = []
        for partition_index, (random_left, random_right, _) in enumerate(random_panels):
            random_raw_left, _ = author_mean_text_features(random_left, runtime)
            random_raw_right, _ = author_mean_text_features(random_right, runtime)
            random_frame_left, random_frame_right = align_author_panels(random_raw_left, random_raw_right, feature_columns=feature_columns)
            if not temporal_frame_left[["user_id", "split"]].equals(random_frame_left[["user_id", "split"]]) or not temporal_frame_left[["user_id", "split"]].equals(random_frame_right[["user_id", "split"]]):
                raise RuntimeError(f"{runtime.name} random partition author alignment diverged.")
            random_left_scaled = scaler.transform(random_frame_left[feature_columns].to_numpy(float))
            random_right_scaled = scaler.transform(random_frame_right[feature_columns].to_numpy(float))
            random_arrays = {
                "left_train": random_left_scaled[random_frame_left["split"].ne("confirmation").to_numpy(bool)],
                "right_train": random_right_scaled[random_frame_right["split"].ne("confirmation").to_numpy(bool)],
                "left_confirmation": random_left_scaled[random_frame_left["split"].eq("confirmation").to_numpy(bool)],
                "right_confirmation": random_right_scaled[random_frame_right["split"].eq("confirmation").to_numpy(bool)],
            }
            contribution = alignment_contributions(random_arrays["left_confirmation"], random_arrays["right_confirmation"])
            random_deltas.append(temporal_contribution - contribution)
            metrics = {
                "alignment_auc": alignment_auc(random_arrays["left_confirmation"], random_arrays["right_confirmation"]),
                "relative_distance_spearman": relative_distance_spearman(random_arrays["left_confirmation"], random_arrays["right_confirmation"]),
                "linear_transport_r2": linear_transport_r2(random_arrays["left_train"], random_arrays["right_train"], random_arrays["left_confirmation"], random_arrays["right_confirmation"], alpha=float(config["ridge_alpha"])),
            }
            random_metrics.append(metrics)
            random_metric_rows.append({"representation": runtime.name, "random_partition": partition_index, **metrics})
        delta_matrix = np.vstack(random_deltas)
        deltas[runtime.name] = delta_matrix.mean(axis=0)
        row = {"representation": runtime.name, "n_features": len(feature_columns), "n_confirmation_authors": len(temporal_contribution), "n_random_partitions": int(len(random_deltas))}
        row["temporal_alignment_auc"] = alignment_auc(temporal_arrays["left_confirmation"], temporal_arrays["right_confirmation"])
        row["temporal_relative_distance_spearman"] = relative_distance_spearman(temporal_arrays["left_confirmation"], temporal_arrays["right_confirmation"])
        row["temporal_linear_transport_r2"] = linear_transport_r2(temporal_arrays["left_train"], temporal_arrays["right_train"], temporal_arrays["left_confirmation"], temporal_arrays["right_confirmation"], alpha=float(config["ridge_alpha"]))
        for metric in ("alignment_auc", "relative_distance_spearman", "linear_transport_r2"):
            values = np.asarray([entry[metric] for entry in random_metrics], dtype=float)
            row[f"random_{metric}_mean"] = float(values.mean())
            row[f"random_{metric}_q025"] = float(np.quantile(values, 0.025))
            row[f"random_{metric}_q975"] = float(np.quantile(values, 0.975))
        row["temporal_minus_random_alignment_auc_mean"] = float(delta_matrix.mean())
        row["alignment_delta_ci_low"], row["alignment_delta_ci_high"] = _nested_partition_author_bootstrap_ci(delta_matrix, seed=int(config["seed"]) + index, iterations=int(args.bootstrap))
        rows.append(row)
    p_values = _paired_sign_flip(deltas, seed=int(config["seed"]) + 707, iterations=int(args.bootstrap))
    table = pd.DataFrame(rows)
    table["pooled_author_sign_flip_max_t_p"] = table["representation"].map(p_values)
    table.to_csv(args.output_dir / "temporal_random_contrast.csv", index=False)
    pd.DataFrame(random_metric_rows).to_csv(args.output_dir / "random_partition_metrics.csv", index=False)
    random_counts = [int(support["user_id"].nunique()) for _, _, support in random_panels]
    support = {"temporal": int(temporal_support["user_id"].nunique()), "random": int(min(random_counts)), "confirmation": int((temporal_support["split"] == "confirmation").sum()), "random_partitions": int(len(random_panels))}
    decision = {"status": "DESCRIPTIVE_TEMPORAL_RANDOM_MULTIPARTITION_COMPLETE", "support": support, "temporal_order_provenance": "OBSERVED_NUMERIC_FOR_ALL_INCLUDED_RECORDS", "claim_boundary": "Same-author within-PANDORA sampling contrast only; nested random-partition uncertainty included; no personality or clinical inference."}
    (args.output_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({"n_prior_author_exclusions": int(len(excluded)), "n_selected_authors": int(selected["user_id"].nunique()), "support": support, "temporal_order_provenance": "OBSERVED_NUMERIC_FOR_ALL_INCLUDED_RECORDS", "raw_identifiers_persisted": False, "claim_boundary": decision["claim_boundary"]})
    (args.output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _report(args.report, output_dir=args.output_dir, table=table, support=support)
    append_ledger_event(args.output_dir / "evidence_ledger.jsonl", {"estimand_id": manifest["estimand_id"], "status": decision["status"], "claim_boundary": manifest["claim_boundary"]})
    inventory = write_artifact_inventory(args.output_dir, args.output_dir / "artifact_inventory.json")
    print(json.dumps({"output_dir": str(args.output_dir), "report": str(args.report), "n_representations": int(len(table)), "artifact_files": inventory["n_files"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
