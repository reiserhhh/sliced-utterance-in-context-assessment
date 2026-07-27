#!/usr/bin/env python3
"""Diagnose the stopped V8 behavior-v2 pilot without new model calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_behavior_v2_pilot as pilot  # noqa: E402
import run_suica_v8_canonical_geometry_fresh_panel as fresh_stats  # noqa: E402
import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
import run_suica_v8_interpreter_stability as base  # noqa: E402
import run_suica_v8_spectral_geometry_audit as spectral  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_behavior_v2 import (  # noqa: E402
    EVENT_OPPORTUNITY,
    OPPORTUNITY_CODES,
    OpportunityBaseline,
    consensus_frame,
    observation_frame,
    validate_behavior_v2_payload,
)
from suica_core.v8_bridge import cross_modal_author_auc  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_behavior_v2_diagnostics.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_behavior_v2_diagnostics"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_ready(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    payload = _read_json(path)
    if payload.get("status") != "STRUCTURED_STAGE_READY":
        return None
    return payload["output"]


def _logical_outputs(
    source: Path,
    profiles: list[dict[str, Any]],
    *,
    repetitions: int,
    batch_size: int,
    schema: dict[str, Any],
) -> list[dict[str, Any]]:
    """Reconstruct complete repetitions from batch and singleton caches."""
    batches = base._batch_profiles(profiles, batch_size=batch_size)
    outputs = []
    for repetition in range(int(repetitions)):
        rows = []
        for batch_index, batch in enumerate(batches):
            prefix = f"primary-r{repetition:02d}-b{batch_index:03d}"
            cached = _load_ready(
                source / "cache" / "primary" / f"{prefix}.json"
            )
            if cached is not None:
                rows.extend(cached["profiles"])
                continue
            singleton_rows = []
            for singleton_index, _ in enumerate(batch):
                single = _load_ready(
                    source
                    / "cache"
                    / "primary"
                    / f"{prefix}-s{singleton_index:02d}.json"
                )
                if single is None:
                    raise RuntimeError(
                        f"missing ready singleton fallback for {prefix}"
                    )
                singleton_rows.extend(single["profiles"])
            rows.extend(singleton_rows)
        merged = {"profiles": rows}
        validate_behavior_v2_payload(
            merged,
            schema=schema,
            profiles=profiles,
        )
        outputs.append(merged)
    return outputs


def _soft_consensus(repeated: pd.DataFrame) -> pd.DataFrame:
    key = [
        "profile_id",
        "author_id",
        "side",
        "cohort_split",
        "segment_id",
        "segment_index",
        "condition",
        "token_count",
        "span_count",
    ]
    columns = [
        column
        for column in repeated
        if column.startswith("opportunity::") or column.startswith("event::")
    ]
    return (
        repeated.groupby(key, observed=True, sort=False)[columns]
        .mean()
        .reset_index()
    )


def _select_segments(frame: pd.DataFrame, resolution: int) -> pd.DataFrame:
    rows = []
    for _, group in frame.groupby("profile_id", observed=True, sort=False):
        ordered = group.sort_values("segment_index", kind="stable")
        indices = np.unique(
            np.linspace(
                0,
                len(ordered) - 1,
                num=min(int(resolution), len(ordered)),
                dtype=int,
            )
        )
        rows.append(ordered.iloc[indices])
    return pd.concat(rows, ignore_index=True)


def _profile_features(
    segments: pd.DataFrame,
    baseline: OpportunityBaseline,
    *,
    events: list[str],
    resolution: int,
) -> pd.DataFrame:
    selected = _select_segments(segments, resolution)
    rows = []
    for profile_id, group in selected.groupby(
        "profile_id",
        observed=True,
        sort=False,
    ):
        first = group.iloc[0]
        row: dict[str, Any] = {
            "profile_id": str(profile_id),
            "author_id": str(first["author_id"]),
            "side": str(first["side"]),
            "cohort_split": str(first["cohort_split"]),
        }
        for opportunity in OPPORTUNITY_CODES:
            row[f"opportunity_rate::{opportunity}"] = float(
                group[f"opportunity::{opportunity}"].mean()
            )
        for event in events:
            opportunity = EVENT_OPPORTUNITY[event]
            outcomes = group[f"event::{event}"].to_numpy(float)
            weights = group[f"opportunity::{opportunity}"].to_numpy(float)
            global_probability = float(baseline.global_probability[event])
            condition_probability = np.asarray([
                baseline.probability(event, str(condition))
                for condition in group["condition"]
            ])
            opportunity_count = float(weights.sum())
            row[f"raw_event::{event}"] = float(outcomes.mean())
            row[f"conditional_rate::{event}"] = (
                float(outcomes.sum() / opportunity_count)
                if opportunity_count > 0
                else float("nan")
            )
            global_residuals = outcomes - weights * global_probability
            condition_residuals = outcomes - weights * condition_probability
            global_variance = float(
                np.sum(
                    weights
                    * global_probability
                    * (1.0 - global_probability)
                )
            )
            condition_variance = float(
                np.sum(
                    weights
                    * condition_probability
                    * (1.0 - condition_probability)
                )
            )
            row[f"global_z::{event}"] = (
                float(global_residuals.sum() / np.sqrt(global_variance + 1e-8))
                if opportunity_count > 0
                else float("nan")
            )
            row[f"condition_z::{event}"] = (
                float(
                    condition_residuals.sum()
                    / np.sqrt(condition_variance + 1e-8)
                )
                if opportunity_count > 0
                else float("nan")
            )
            row[f"global_mean_residual::{event}"] = (
                float(global_residuals.sum() / opportunity_count)
                if opportunity_count > 0
                else float("nan")
            )
            row[f"condition_mean_residual::{event}"] = (
                float(condition_residuals.sum() / opportunity_count)
                if opportunity_count > 0
                else float("nan")
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _columns(frame: pd.DataFrame, prefix: str) -> list[str]:
    return [column for column in frame if column.startswith(f"{prefix}::")]


def _matrix(
    frame: pd.DataFrame,
    columns: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return pilot._standardized_matrix(frame, columns)


def _matched_auc(
    behavior: np.ndarray,
    condition: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    strangers: int,
) -> float:
    labels = []
    scores = []
    behavior_norm = np.linalg.norm(behavior, axis=1)
    for index in range(len(behavior)):
        opposite = np.flatnonzero(sides != sides[index])
        positive = opposite[authors[opposite] == authors[index]]
        negative = opposite[authors[opposite] != authors[index]]
        if len(positive) != 1 or not len(negative):
            continue
        source_norm = float(np.linalg.norm(condition[index]))
        target_norms = np.linalg.norm(condition[opposite], axis=1)
        condition_scores = np.divide(
            condition[opposite] @ condition[index],
            target_norms * source_norm,
            out=np.zeros(len(opposite), dtype=float),
            where=(target_norms * source_norm) > 1e-12,
        )
        positive_score = float(
            condition_scores[authors[opposite] == authors[index]][0]
        )
        negative_scores = condition_scores[
            authors[opposite] != authors[index]
        ]
        selected = negative[
            np.argsort(
                np.abs(negative_scores - positive_score),
                kind="stable",
            )[: int(strangers)]
        ]
        targets = np.concatenate([positive, selected])
        for target in targets:
            denominator = behavior_norm[index] * behavior_norm[target]
            similarity = (
                float(np.dot(behavior[index], behavior[target]) / denominator)
                if denominator > 1e-12
                else 0.0
            )
            labels.append(int(authors[target] == authors[index]))
            scores.append(similarity)
    if len(set(labels)) < 2:
        return float("nan")
    from sklearn.metrics import roc_auc_score

    return float(roc_auc_score(labels, scores))


def _safe_correlation(
    first: np.ndarray,
    second: np.ndarray,
    *,
    method: str,
) -> tuple[float, float]:
    if (
        len(first) < 4
        or np.std(first) < 1e-12
        or np.std(second) < 1e-12
    ):
        return float("nan"), float("nan")
    result = (
        pearsonr(first, second)
        if method == "pearson"
        else spearmanr(first, second)
    )
    return float(result.statistic), float(result.pvalue)


def _event_stability(
    frame: pd.DataFrame,
    *,
    families: list[str],
    events: list[str],
) -> pd.DataFrame:
    rows = []
    left = frame.loc[frame["side"].eq("left")].set_index("author_id")
    right = frame.loc[frame["side"].eq("right")].set_index("author_id")
    authors = left.index.intersection(right.index)
    for family in families:
        for event in events:
            column = f"{family}::{event}"
            first = left.loc[authors, column].to_numpy(float)
            second = right.loc[authors, column].to_numpy(float)
            finite = np.isfinite(first) & np.isfinite(second)
            pearson, pearson_p = _safe_correlation(
                first[finite],
                second[finite],
                method="pearson",
            )
            spearman, spearman_p = _safe_correlation(
                first[finite],
                second[finite],
                method="spearman",
            )
            rows.append({
                "family": family,
                "event_code": event,
                "n_authors": int(finite.sum()),
                "pearson_r": pearson,
                "pearson_p": pearson_p,
                "spearman_rho": spearman,
                "spearman_p": spearman_p,
            })
    return pd.DataFrame(rows)


def _report(
    decision: dict[str, Any],
    headline: pd.DataFrame,
) -> str:
    return f"""# SUICA V8 Behavior-v2 No-Call Diagnostics

Decision: `{decision["status"]}`

## Scope

- existing cached observer outputs only;
- no new LLM calls;
- no psychological, clinical, market, or geometry labels;
- author-level scores compiled deterministically.

## Headline resolution

{headline.to_markdown(index=False)}

## Interpretation

{decision["interpretation"]}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    source = ROOT / str(config["source_run"])
    inventory = verify_artifact_inventory(source / "artifact_inventory.json")
    if inventory["status"] != "INVENTORY_PASS":
        raise RuntimeError("behavior pilot inventory failed")
    pilot_config = _read_json(source / "config.resolved.json")
    original_source = ROOT / str(pilot_config["source_run"])
    source_config = _read_json(original_source / "config.resolved.json")
    metadata = pilot._select_metadata(
        source_config,
        pilot_config["pilot"]["split_counts"],
        seed=int(pilot_config["seed"]),
    )
    profiles = pilot._build_profiles(
        metadata,
        segments_per_half=int(pilot_config["segments_per_half"]),
        units_per_half=int(pilot_config["geometry_units_per_half"]),
        max_spans=int(pilot_config["max_spans_per_segment"]),
    )
    schema = _read_json(
        ROOT / "schemas" / "v8_behavior_observation_v2.schema.json"
    )
    outputs = _logical_outputs(
        source,
        profiles,
        repetitions=int(pilot_config["pilot"]["observer_repetitions"]),
        batch_size=int(pilot_config["runtime"]["batch_size"]),
        schema=schema,
    )
    repeated = observation_frame(profiles, outputs)
    strict = consensus_frame(
        repeated,
        required_fraction=float(pilot_config["consensus_required_fraction"]),
    )
    soft = _soft_consensus(repeated)
    usable_events = (
        pd.read_csv(source / "event_inventory.csv")
        .loc[lambda frame: frame["usable_for_rate_pilot"].astype(bool), "event_code"]
        .astype(str)
        .tolist()
    )
    baseline = pilot.fit_opportunity_event_baseline(
        strict.loc[strict["cohort_split"].eq("discovery")],
        shrinkage=float(pilot_config["opportunity_shrinkage"]),
    )
    families = [
        "raw_event",
        "conditional_rate",
        "global_z",
        "condition_z",
        "global_mean_residual",
        "condition_mean_residual",
    ]
    representation_rows = []
    feature_frames: dict[tuple[str, int], pd.DataFrame] = {}
    matrix_cache: dict[tuple[str, str, int], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for aggregation, segments in (("strict", strict), ("soft", soft)):
        for resolution in map(int, config["resolutions"]):
            features = _profile_features(
                segments,
                baseline,
                events=usable_events,
                resolution=resolution,
            )
            feature_frames[(aggregation, resolution)] = features
            condition = pilot._condition_features(
                strict,
                resolution=resolution,
                top_dimensions=int(
                    pilot_config["condition_control_dimensions"]
                ),
            )
            condition_columns = [
                column
                for column in condition
                if column.startswith("condition::")
                or column in {
                    "mean_token_count",
                    "std_token_count",
                    "mean_span_count",
                }
            ]
            condition_values, condition_authors, condition_sides, discovery = (
                _matrix(condition, condition_columns)
            )
            condition_auc = cross_modal_author_auc(
                condition_values,
                condition_values,
                condition_authors,
                condition_sides,
                metric="cosine",
            )
            representation_rows.append({
                "aggregation": aggregation,
                "resolution": resolution,
                "family": "condition_control",
                "self_auc": condition_auc,
                "condition_matched_auc": _matched_auc(
                    condition_values,
                    condition_values,
                    condition_authors,
                    condition_sides,
                    strangers=int(config["condition_matched_strangers"]),
                ),
                "dimensions": int(condition_values.shape[1]),
            })
            matrix_cache[(aggregation, "condition_control", resolution)] = (
                condition_values,
                condition_authors,
                condition_sides,
            )
            family_columns = {
                family: _columns(features, family) for family in families
            }
            family_columns["opportunity_rate"] = _columns(
                features,
                "opportunity_rate",
            )
            for family, columns in family_columns.items():
                values, authors, sides, _ = _matrix(features, columns)
                if not (
                    np.array_equal(authors, condition_authors)
                    and np.array_equal(sides, condition_sides)
                ):
                    raise RuntimeError("feature and condition order differ")
                auc = cross_modal_author_auc(
                    values,
                    values,
                    authors,
                    sides,
                    metric="cosine",
                )
                matched = _matched_auc(
                    values,
                    condition_values,
                    authors,
                    sides,
                    strangers=int(config["condition_matched_strangers"]),
                )
                representation_rows.append({
                    "aggregation": aggregation,
                    "resolution": resolution,
                    "family": family,
                    "self_auc": auc,
                    "condition_matched_auc": matched,
                    "dimensions": len(columns),
                })
                matrix_cache[(aggregation, family, resolution)] = (
                    values,
                    authors,
                    sides,
                )

            raw_values, authors, sides = matrix_cache[
                (aggregation, "raw_event", resolution)
            ]
            model = Ridge(alpha=float(config["ridge_alpha"])).fit(
                condition_values[discovery],
                raw_values[discovery],
            )
            residual = raw_values - model.predict(condition_values)
            combined = np.column_stack([condition_values, raw_values])
            for family, values in (
                ("raw_event_residualized_on_condition", residual),
                ("condition_plus_raw_event", combined),
            ):
                auc = cross_modal_author_auc(
                    values,
                    values,
                    authors,
                    sides,
                    metric="cosine",
                )
                matched = _matched_auc(
                    values,
                    condition_values,
                    authors,
                    sides,
                    strangers=int(config["condition_matched_strangers"]),
                )
                representation_rows.append({
                    "aggregation": aggregation,
                    "resolution": resolution,
                    "family": family,
                    "self_auc": auc,
                    "condition_matched_auc": matched,
                    "dimensions": int(values.shape[1]),
                })
                matrix_cache[(aggregation, family, resolution)] = (
                    values,
                    authors,
                    sides,
                )
    metrics = pd.DataFrame(representation_rows)
    headline_resolution = int(config["headline_resolution"])
    headline = metrics.loc[
        metrics["resolution"].eq(headline_resolution)
    ].copy()
    interval_rows = []
    for row in headline.itertuples(index=False):
        values, authors, sides = matrix_cache[
            (str(row.aggregation), str(row.family), headline_resolution)
        ]
        estimate, lower, upper = spectral._bootstrap_interval(
            values,
            authors,
            sides,
            metric="cosine",
            seed=int(config["seed"]) + len(interval_rows),
            draws=int(config["bootstrap_draws"]),
        )
        p_value = fresh_stats._fast_pairing_permutation_p(
            values,
            authors,
            sides,
            metric="cosine",
            observed=float(row.self_auc),
            seed=int(config["seed"]) + 1000 + len(interval_rows),
            permutations=int(config["permutations"]),
        )
        interval_rows.append({
            "aggregation": str(row.aggregation),
            "family": str(row.family),
            "resolution": headline_resolution,
            "cluster_estimate": estimate,
            "ci_lower": lower,
            "ci_upper": upper,
            "permutation_p": p_value,
        })
    intervals = pd.DataFrame(interval_rows)
    headline = headline.merge(
        intervals,
        on=["aggregation", "family", "resolution"],
        validate="one_to_one",
    )
    full_features = feature_frames[("soft", headline_resolution)]
    stability = _event_stability(
        full_features,
        families=families,
        events=usable_events,
    )
    thresholds = config["diagnostic_thresholds"]
    behavior_only = headline.loc[
        headline["family"].isin(families)
    ]
    best = behavior_only.sort_values(
        ["self_auc", "condition_matched_auc"],
        ascending=False,
        kind="stable",
    ).iloc[0]
    condition_plus = headline.loc[
        (headline["aggregation"] == best["aggregation"])
        & (headline["family"] == "condition_plus_raw_event")
    ].iloc[0]
    condition_control = headline.loc[
        (headline["aggregation"] == best["aggregation"])
        & (headline["family"] == "condition_control")
    ].iloc[0]
    opportunity = headline.loc[
        (headline["aggregation"] == best["aggregation"])
        & (headline["family"] == "opportunity_rate")
    ].iloc[0]
    behavior_pass = bool(
        float(best["self_auc"])
        >= float(thresholds["minimum_behavior_self_auc"])
        and float(best["permutation_p"])
        <= float(thresholds["maximum_permutation_p"])
        and float(best["condition_matched_auc"])
        >= float(thresholds["minimum_condition_matched_auc"])
    )
    increment = float(
        condition_plus["self_auc"] - condition_control["self_auc"]
    )
    if behavior_pass:
        status = "V8_BEHAVIOR_V2_DIAGNOSTIC_CANDIDATE_FRESH_GATE_REQUIRED"
        interpretation = (
            "At least one behavior-only representation survived the opened "
            "self and condition-matched screens. It requires a frozen fresh "
            "author replication before any geometry bridge."
        )
    else:
        status = "V8_BEHAVIOR_V2_OBJECT_STOP"
        interpretation = (
            "No behavior-only representation met the joint self-AUC, "
            "condition-matched, and permutation gates. Stable opportunity/"
            "condition choice must remain a separate C1 channel; the current "
            "explicit event object does not establish a C2 author channel."
        )
    decision = {
        "status": status,
        "authors": int(metadata["author_id"].nunique()),
        "events": usable_events,
        "headline_resolution": headline_resolution,
        "best_behavior_only": {
            key: (
                value.item() if isinstance(value, np.generic) else value
            )
            for key, value in best.to_dict().items()
        },
        "opportunity_self_auc": float(opportunity["self_auc"]),
        "condition_control_self_auc": float(condition_control["self_auc"]),
        "condition_plus_behavior_self_auc": float(condition_plus["self_auc"]),
        "condition_plus_behavior_increment_over_condition": increment,
        "behavior_gate_pass": behavior_pass,
        "new_llm_calls": 0,
        "external_labels_read": False,
        "interpretation": interpretation,
        "claim_boundary": str(config["claim_boundary"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.output_dir / "config.resolved.json", config)
    _write_json(args.output_dir / "decision.json", decision)
    metrics.to_csv(args.output_dir / "resolution_curve.csv", index=False)
    headline.to_csv(args.output_dir / "headline_metrics.csv", index=False)
    stability.to_csv(args.output_dir / "event_stability.csv", index=False)
    (args.output_dir / "report.md").write_text(
        _report(decision, headline),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            source / "artifact_inventory.json",
            source / "decision.json",
            source / "event_inventory.csv",
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "scripts" / "run_suica_v8_behavior_v2_pilot.py",
            ROOT / "suica_core" / "v8_behavior_v2.py",
        ],
        estimand_id="V8-I8-pandora-behavior-v2-no-call-diagnostics",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
