#!/usr/bin/env python3
"""Build and audit the no-call SUICA behavior-v2.1 candidate."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_behavior_v2_diagnostics as diagnostics  # noqa: E402
import run_suica_v8_behavior_v2_pilot as pilot  # noqa: E402
import run_suica_v8_canonical_geometry_fresh_panel as fresh_stats  # noqa: E402
import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
import run_suica_v8_spectral_geometry_audit as spectral  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_behavior_v2 import (  # noqa: E402
    EVENT_OPPORTUNITY,
    OPPORTUNITY_CODES,
    fit_leave_one_author_out_baseline,
    fit_weighted_opportunity_event_baseline,
    observation_frame,
    validate_behavior_v2_payload,
)
from suica_core.v8_bridge import cross_modal_author_auc  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_behavior_v21_candidate.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_behavior_v21_candidate"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _add_coarse_events(
    frame: pd.DataFrame,
    groups: dict[str, list[str]],
) -> pd.DataFrame:
    result = frame.copy()
    for group, events in groups.items():
        result[f"coarse::{group}"] = result[
            [f"event::{event}" for event in events]
        ].max(axis=1)
    return result


def _aggregate_repetitions(
    repeated: pd.DataFrame,
    *,
    mode: str,
) -> pd.DataFrame:
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
        if column.startswith("opportunity::")
        or column.startswith("event::")
        or column.startswith("coarse::")
    ]
    if mode.startswith("rep"):
        repetition = int(mode.removeprefix("rep"))
        return (
            repeated.loc[repeated["repetition"].eq(repetition), key + columns]
            .reset_index(drop=True)
        )
    means = (
        repeated.groupby(key, observed=True, sort=False)[columns]
        .mean()
        .reset_index()
    )
    if mode == "strict":
        means[columns] = means[columns].ge(1.0).astype(int)
    elif mode != "soft":
        raise ValueError(f"unsupported observer aggregation: {mode}")
    return means


def _binary_f1(first: np.ndarray, second: np.ndarray) -> float:
    left = np.asarray(first, dtype=int)
    right = np.asarray(second, dtype=int)
    true_positive = int(np.sum((left == 1) & (right == 1)))
    false_positive = int(np.sum((left == 0) & (right == 1)))
    false_negative = int(np.sum((left == 1) & (right == 0)))
    denominator = 2 * true_positive + false_positive + false_negative
    return (
        float(2.0 * true_positive / denominator)
        if denominator
        else float("nan")
    )


def _observer_reliability(
    repeated: pd.DataFrame,
    audit: pd.DataFrame,
    *,
    audit_authors: set[str],
    event_codes: list[str],
    coarse_codes: list[str],
) -> pd.DataFrame:
    keys = ["profile_id", "segment_id"]
    rep0 = repeated.loc[repeated["repetition"].eq(0)].set_index(keys)
    rep1 = repeated.loc[repeated["repetition"].eq(1)].set_index(keys)
    strict = _aggregate_repetitions(repeated, mode="strict")
    primary_audit = strict.loc[
        strict["author_id"].astype(str).isin(audit_authors)
    ].set_index(keys)
    audit_indexed = audit.set_index(keys)
    rows = []
    for level, codes, prefix in (
        ("atomic", event_codes, "event"),
        ("coarse", coarse_codes, "coarse"),
    ):
        for code in codes:
            column = f"{prefix}::{code}"
            repeated_index = rep0.index.intersection(rep1.index)
            cross_index = primary_audit.index.intersection(audit_indexed.index)
            rows.append({
                "level": level,
                "code": code,
                "repeated_f1": _binary_f1(
                    rep0.loc[repeated_index, column],
                    rep1.loc[repeated_index, column],
                ),
                "cross_model_f1": _binary_f1(
                    primary_audit.loc[cross_index, column],
                    audit_indexed.loc[cross_index, column],
                ),
                "primary_audit_positive": int(
                    primary_audit.loc[cross_index, column].sum()
                ),
                "audit_positive": int(
                    audit_indexed.loc[cross_index, column].sum()
                ),
            })
    return pd.DataFrame(rows)


def _selected(
    segments: pd.DataFrame,
    *,
    resolution: int,
) -> pd.DataFrame:
    return diagnostics._select_segments(segments, resolution)


def _feature_frame(
    selected: pd.DataFrame,
    *,
    events: list[str],
    coarse_groups: list[str],
    baseline,
    loao,
    posterior_strength: float,
) -> pd.DataFrame:
    rows = []
    for profile_id, group in selected.groupby(
        "profile_id",
        observed=True,
        sort=False,
    ):
        first = group.iloc[0]
        author_id = str(first["author_id"])
        row: dict[str, Any] = {
            "profile_id": str(profile_id),
            "author_id": author_id,
            "side": str(first["side"]),
            "cohort_split": str(first["cohort_split"]),
        }
        for opportunity in OPPORTUNITY_CODES:
            row[f"opportunity::{opportunity}"] = float(
                group[f"opportunity::{opportunity}"].mean()
            )
        for event in events:
            opportunity = EVENT_OPPORTUNITY[event]
            outcomes = group[f"event::{event}"].to_numpy(float)
            weights = group[f"opportunity::{opportunity}"].to_numpy(float)
            count = float(weights.sum())
            global_probability = float(
                loao.global_value(event, author_id)
            )
            probabilities = np.asarray([
                loao.probability(event, str(condition), author_id)
                for condition in group["condition"]
            ])
            residual = outcomes - weights * probabilities
            variance = float(
                np.sum(weights * probabilities * (1.0 - probabilities))
            )
            z_value = (
                float(residual.sum() / np.sqrt(variance + 1e-8))
                if count > 0
                else 0.0
            )
            row[f"raw::{event}"] = float(outcomes.mean())
            row[f"posterior::{event}"] = float(
                (
                    outcomes.sum()
                    + float(posterior_strength) * global_probability
                )
                / (count + float(posterior_strength))
            )
            row[f"loao_z::{event}"] = z_value
            row[f"loao_gated::{event}"] = float(
                z_value
                * np.sqrt(
                    count / (count + float(posterior_strength))
                )
            )
        for coarse in coarse_groups:
            row[f"coarse::{coarse}"] = float(
                group[f"coarse::{coarse}"].mean()
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _matrix(
    frame: pd.DataFrame,
    prefix: str,
    codes: list[str],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    values, authors, sides, _ = pilot._standardized_matrix(
        frame,
        [f"{prefix}::{code}" for code in codes],
    )
    return values, authors, sides


def _metric(
    values: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    seed: int,
    bootstrap_draws: int,
    permutations: int,
) -> dict[str, float]:
    auc = cross_modal_author_auc(
        values,
        values,
        authors,
        sides,
        metric="cosine",
    )
    estimate, lower, upper = spectral._bootstrap_interval(
        values,
        authors,
        sides,
        metric="cosine",
        seed=seed,
        draws=bootstrap_draws,
    )
    p_value = fresh_stats._fast_pairing_permutation_p(
        values,
        authors,
        sides,
        metric="cosine",
        observed=auc,
        seed=seed + 1000,
        permutations=permutations,
    )
    return {
        "self_auc": auc,
        "cluster_estimate": estimate,
        "ci_lower": lower,
        "ci_upper": upper,
        "permutation_p": p_value,
    }


def _nested_panel(
    frame: pd.DataFrame,
    *,
    draw: int,
    resolutions: list[int],
    seed: int,
) -> dict[int, pd.DataFrame]:
    selected: dict[int, list[pd.DataFrame]] = {
        resolution: [] for resolution in resolutions
    }
    for profile_id, group in frame.groupby(
        "profile_id",
        observed=True,
        sort=False,
    ):
        ordered = group.sort_values("segment_index", kind="stable")
        digest = hashlib.sha256(
            f"{seed}::{draw}::{profile_id}".encode("utf-8")
        ).digest()
        rng = np.random.default_rng(
            int.from_bytes(digest[:8], "big")
        )
        permutation = rng.permutation(len(ordered))
        for resolution in resolutions:
            chosen = np.sort(permutation[: int(resolution)])
            selected[resolution].append(ordered.iloc[chosen])
    return {
        resolution: pd.concat(rows, ignore_index=True)
        for resolution, rows in selected.items()
    }


def _report(
    decision: dict[str, Any],
    metrics: pd.DataFrame,
    reliability: pd.DataFrame,
    nested_summary: pd.DataFrame,
) -> str:
    return f"""# SUICA V8 Behavior-v2.1 Candidate Audit

Decision: `{decision["status"]}`

## Frozen boundary

- existing observer cache only; new LLM calls: 0;
- external labels read: false;
- the current 24-author panel is opened;
- geometry bridge remains stopped.

## Candidate metrics

{metrics.to_markdown(index=False)}

## Observer hierarchy

{reliability.to_markdown(index=False)}

## Nested resolution

{nested_summary.to_markdown(index=False)}

## Interpretation

{decision["interpretation"]}

## Claim boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    source = ROOT / str(config["source_run"])
    source_inventory = verify_artifact_inventory(
        source / "artifact_inventory.json"
    )
    if source_inventory["status"] != "INVENTORY_PASS":
        raise RuntimeError("behavior-v2 pilot inventory failed")
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
    outputs = diagnostics._logical_outputs(
        source,
        profiles,
        repetitions=int(pilot_config["pilot"]["observer_repetitions"]),
        batch_size=int(pilot_config["runtime"]["batch_size"]),
        schema=schema,
    )
    repeated = observation_frame(profiles, outputs)
    groups = {
        str(code): list(map(str, events))
        for code, events in config["coarse_event_families"].items()
    }
    repeated = _add_coarse_events(repeated, groups)

    audit_authors = sorted({
        str(profile["author_id"]) for profile in profiles
    })[: int(pilot_config["pilot"]["audit_authors"])]
    audit_profiles = [
        profile for profile in profiles
        if str(profile["author_id"]) in set(audit_authors)
    ]
    audit_rows = []
    for batch_index, batch in enumerate(
        diagnostics.base._batch_profiles(
            audit_profiles,
            batch_size=int(pilot_config["runtime"]["batch_size"]),
        )
    ):
        cached = diagnostics._load_ready(
            source
            / "cache"
            / "audit"
            / f"audit-r00-b{batch_index:03d}.json"
        )
        if cached is None:
            raise RuntimeError("audit cache is incomplete")
        audit_rows.extend(cached["profiles"])
    audit_payload = {"profiles": audit_rows}
    validate_behavior_v2_payload(
        audit_payload,
        schema=schema,
        profiles=audit_profiles,
    )
    audit = _add_coarse_events(
        observation_frame(audit_profiles, [audit_payload]),
        groups,
    )
    event_codes = list(map(str, config["frozen_events"]))
    reliability = _observer_reliability(
        repeated,
        audit,
        audit_authors=set(audit_authors),
        event_codes=event_codes,
        coarse_codes=list(groups),
    )
    reliable_events = (
        reliability.loc[
            (reliability["level"] == "atomic")
            & (
                reliability["repeated_f1"]
                >= float(config["reliability_event_f1_threshold"])
            ),
            "code",
        ]
        .astype(str)
        .tolist()
    )
    frames = {
        mode: _aggregate_repetitions(repeated, mode=mode)
        for mode in ("rep0", "rep1", "strict", "soft")
    }
    feature_frames: dict[str, pd.DataFrame] = {}
    baselines = {}
    loao_baselines = {}
    target_authors = metadata["author_id"].astype(str).tolist()
    for mode, frame in frames.items():
        discovery = frame.loc[frame["cohort_split"].eq("discovery")]
        baselines[mode] = fit_weighted_opportunity_event_baseline(
            discovery,
            shrinkage=float(config["opportunity_shrinkage"]),
        )
        loao_baselines[mode] = fit_leave_one_author_out_baseline(
            discovery,
            target_authors=target_authors,
            shrinkage=float(config["opportunity_shrinkage"]),
        )
        feature_frames[mode] = _feature_frame(
            _selected(
                frame,
                resolution=int(config["headline_resolution"]),
            ),
            events=event_codes,
            coarse_groups=list(groups),
            baseline=baselines[mode],
            loao=loao_baselines[mode],
            posterior_strength=float(config["posterior_strength"]),
        )

    candidate_specs = [
        ("rep0_raw_atomic", "rep0", "raw", event_codes),
        ("rep1_raw_atomic", "rep1", "raw", event_codes),
        ("strict_raw_atomic", "strict", "raw", event_codes),
        ("soft_raw_atomic", "soft", "raw", event_codes),
        ("soft_posterior_atomic", "soft", "posterior", event_codes),
        ("soft_loao_z_atomic", "soft", "loao_z", event_codes),
        ("soft_loao_gated_atomic", "soft", "loao_gated", event_codes),
        ("soft_raw_reliable", "soft", "raw", reliable_events),
        ("rep0_coarse", "rep0", "coarse", list(groups)),
        ("rep1_coarse", "rep1", "coarse", list(groups)),
        ("soft_coarse", "soft", "coarse", list(groups)),
        (
            "soft_opportunity",
            "soft",
            "opportunity",
            list(OPPORTUNITY_CODES),
        ),
    ]
    metric_rows = []
    matrices = {}
    for index, (name, mode, prefix, codes) in enumerate(candidate_specs):
        values, authors, sides = _matrix(
            feature_frames[mode],
            prefix,
            codes,
        )
        matrices[name] = (values, authors, sides)
        metric_rows.append({
            "candidate": name,
            "dimensions": len(codes),
            **_metric(
                values,
                authors,
                sides,
                seed=int(config["seed"]) + index,
                bootstrap_draws=int(config["bootstrap_draws"]),
                permutations=int(config["permutations"]),
            ),
        })
    metrics = pd.DataFrame(metric_rows)

    soft = frames["soft"]
    condition = pilot._condition_features(
        soft,
        resolution=int(config["headline_resolution"]),
        top_dimensions=int(pilot_config["condition_control_dimensions"]),
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
    condition_values, condition_authors, condition_sides, _ = (
        pilot._standardized_matrix(condition, condition_columns)
    )
    coarse_values, authors, sides = matrices["soft_coarse"]
    if not (
        np.array_equal(authors, condition_authors)
        and np.array_equal(sides, condition_sides)
    ):
        raise RuntimeError("condition and behavior profiles differ")
    combined = np.column_stack([condition_values, coarse_values])
    condition_auc = cross_modal_author_auc(
        condition_values,
        condition_values,
        authors,
        sides,
        metric="cosine",
    )
    combined_auc = cross_modal_author_auc(
        combined,
        combined,
        authors,
        sides,
        metric="cosine",
    )
    delta = spectral._paired_auc_delta_interval(
        combined,
        condition_values,
        authors,
        sides,
        metric="cosine",
        seed=int(config["seed"]) + 5000,
        draws=int(config["bootstrap_draws"]),
    )
    condition_match_control = diagnostics._matched_auc(
        condition_values,
        condition_values,
        authors,
        sides,
        strangers=int(config["condition_matched_strangers"]),
    )
    coarse_matched_auc = diagnostics._matched_auc(
        coarse_values,
        condition_values,
        authors,
        sides,
        strangers=int(config["condition_matched_strangers"]),
    )
    condition_increment = pd.DataFrame([{
        "condition_self_auc": condition_auc,
        "condition_plus_coarse_auc": combined_auc,
        "paired_delta": delta[0],
        "delta_ci_lower": delta[1],
        "delta_ci_upper": delta[2],
        "condition_match_control_auc": condition_match_control,
        "coarse_condition_matched_auc": coarse_matched_auc,
    }])

    nested_rows = []
    nested_resolutions = list(map(int, config["nested_resolutions"]))
    for draw in range(int(config["nested_draws"])):
        panels = _nested_panel(
            soft,
            draw=draw,
            resolutions=nested_resolutions,
            seed=int(config["seed"]),
        )
        for resolution, panel in panels.items():
            features = _feature_frame(
                panel,
                events=event_codes,
                coarse_groups=list(groups),
                baseline=baselines["soft"],
                loao=loao_baselines["soft"],
                posterior_strength=float(config["posterior_strength"]),
            )
            for family, codes in (
                ("raw_atomic", event_codes),
                ("posterior_atomic", event_codes),
                ("loao_gated_atomic", event_codes),
                ("coarse", list(groups)),
            ):
                prefix = family.replace("_atomic", "")
                values, draw_authors, draw_sides = _matrix(
                    features,
                    prefix,
                    codes,
                )
                nested_rows.append({
                    "draw": draw,
                    "resolution": resolution,
                    "family": family,
                    "self_auc": cross_modal_author_auc(
                        values,
                        values,
                        draw_authors,
                        draw_sides,
                        metric="cosine",
                    ),
                })
    nested = pd.DataFrame(nested_rows)
    summary_rows = []
    for family, group in nested.groupby("family", observed=True):
        means = group.groupby("resolution", observed=True)["self_auc"].mean()
        slope = float(
            np.polyfit(
                np.log(means.index.to_numpy(float)),
                means.to_numpy(float),
                deg=1,
            )[0]
        )
        for resolution, values in group.groupby(
            "resolution",
            observed=True,
        )["self_auc"]:
            summary_rows.append({
                "family": str(family),
                "resolution": int(resolution),
                "mean_auc": float(values.mean()),
                "ci_lower": float(values.quantile(0.025)),
                "ci_upper": float(values.quantile(0.975)),
                "slope_auc_log_resolution": slope,
            })
    nested_summary = pd.DataFrame(summary_rows)

    gates = config["gates"]
    coarse = metrics.loc[metrics["candidate"].eq("soft_coarse")].iloc[0]
    rep0 = metrics.loc[metrics["candidate"].eq("rep0_coarse")].iloc[0]
    rep1 = metrics.loc[metrics["candidate"].eq("rep1_coarse")].iloc[0]
    coarse_reliability = reliability.loc[
        (reliability["level"] == "coarse")
        & reliability["code"].isin(groups)
    ]
    cross_macro = float(coarse_reliability["cross_model_f1"].mean())
    coarse_slope = float(
        nested_summary.loc[
            nested_summary["family"].eq("coarse"),
            "slope_auc_log_resolution",
        ].iloc[0]
    )
    core_checks = {
        "coarse_auc": (
            float(coarse["self_auc"])
            >= float(gates["minimum_candidate_auc"])
        ),
        "coarse_ci": (
            float(coarse["ci_lower"])
            > float(gates["minimum_ci_lower"])
        ),
        "coarse_permutation": (
            float(coarse["permutation_p"])
            <= float(gates["maximum_permutation_p"])
        ),
        "both_repetitions": (
            min(float(rep0["self_auc"]), float(rep1["self_auc"]))
            >= float(gates["minimum_repetition_auc"])
        ),
        "repetition_gap": (
            abs(float(rep0["self_auc"]) - float(rep1["self_auc"]))
            <= float(gates["maximum_repetition_auc_gap"])
        ),
        "cross_model_macro_f1": (
            cross_macro
            >= float(gates["minimum_cross_model_macro_f1"])
        ),
        "nested_slope": (
            coarse_slope >= float(gates["minimum_nested_slope"])
        ),
    }
    condition_match_valid = bool(
        condition_match_control
        <= float(gates["maximum_matched_condition_control_auc"])
    )
    if all(core_checks.values()):
        status = (
            "V8_BEHAVIOR_V21_CANDIDATE_FROZEN_FRESH_GATE_REQUIRED"
            if condition_match_valid
            else
            "V8_BEHAVIOR_V21_CANDIDATE_FROZEN_CONDITION_UNRESOLVED"
        )
        interpretation = (
            "The opened panel supports a coarse, soft-aggregated behavior "
            "candidate, while atomic condition residualization is rejected. "
            "The candidate requires a fresh author panel and human coding; "
            "the geometry bridge remains stopped."
        )
    else:
        status = "V8_BEHAVIOR_V21_CANDIDATE_STOP"
        interpretation = (
            "The proposed coarse hierarchy did not survive all technical "
            "self-reliability gates. No fresh behavior or geometry run is "
            "licensed."
        )
    loao_row = metrics.loc[
        metrics["candidate"].eq("soft_loao_gated_atomic")
    ].iloc[0]
    decision = {
        "status": status,
        "core_checks": core_checks,
        "condition_match_valid": condition_match_valid,
        "authors": int(metadata["author_id"].nunique()),
        "frozen_atomic_events": event_codes,
        "reliable_atomic_events": reliable_events,
        "coarse_event_families": groups,
        "soft_coarse_auc": float(coarse["self_auc"]),
        "soft_coarse_ci": [
            float(coarse["ci_lower"]),
            float(coarse["ci_upper"]),
        ],
        "soft_coarse_permutation_p": float(coarse["permutation_p"]),
        "rep0_coarse_auc": float(rep0["self_auc"]),
        "rep1_coarse_auc": float(rep1["self_auc"]),
        "coarse_cross_model_macro_f1": cross_macro,
        "coarse_nested_slope": coarse_slope,
        "loao_gated_atomic_auc": float(loao_row["self_auc"]),
        "condition_match_control_auc": condition_match_control,
        "coarse_condition_matched_auc": coarse_matched_auc,
        "condition_plus_coarse_delta": float(delta[0]),
        "new_llm_calls": 0,
        "external_labels_read": False,
        "geometry_bridge_licensed": False,
        "human_gold_available": False,
        "interpretation": interpretation,
        "claim_boundary": str(config["claim_boundary"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.output_dir / "config.resolved.json", config)
    _write_json(args.output_dir / "decision.json", decision)
    reliability.to_csv(
        args.output_dir / "observer_event_reliability.csv",
        index=False,
    )
    metrics.to_csv(args.output_dir / "candidate_metrics.csv", index=False)
    condition_increment.to_csv(
        args.output_dir / "condition_increment.csv",
        index=False,
    )
    nested.to_csv(args.output_dir / "nested_resolution_draws.csv", index=False)
    nested_summary.to_csv(
        args.output_dir / "nested_resolution_summary.csv",
        index=False,
    )
    (args.output_dir / "report.md").write_text(
        _report(decision, metrics, reliability, nested_summary),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            source / "artifact_inventory.json",
            source / "decision.json",
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "scripts" / "run_suica_v8_behavior_v2_diagnostics.py",
            ROOT / "suica_core" / "v8_behavior_v2.py",
        ],
        estimand_id="V8-I9-pandora-behavior-v21-opened-candidate",
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
