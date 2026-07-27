#!/usr/bin/env python3
"""Gate SUICA behavior-v2.1 against blind human coding."""
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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_behavior_v2 import (  # noqa: E402
    EVENT_CODES,
    OPPORTUNITY_CODES,
)
from suica_core.v8_human_coding import (  # noqa: E402
    binary_metrics,
    gwet_ac1_binary,
    span_set_f1,
)


DEFAULT_PACKET = (
    ROOT
    / "results"
    / "v8_behavior_v21_human_gold_packet"
    / "pandora_20260725"
)
DEFAULT_OUTPUT = ROOT / "results" / "v8_behavior_v21_human_gold_evaluation"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _hash_order(value: str, *, salt: str) -> str:
    return hashlib.sha256(f"{salt}::{value}".encode("utf-8")).hexdigest()


def _target_columns(
    groups: dict[str, list[str]],
) -> tuple[list[str], list[str]]:
    labels = [
        *(f"opportunity__{code}" for code in OPPORTUNITY_CODES),
        *(f"event__{code}" for code in EVENT_CODES),
        *(f"coarse__{code}" for code in groups),
    ]
    evidence = [
        *(f"opportunity_evidence__{code}" for code in OPPORTUNITY_CODES),
        *(f"event_evidence__{code}" for code in EVENT_CODES),
        *(f"coarse_evidence__{code}" for code in groups),
    ]
    return labels, evidence


def _split_spans(value: str) -> set[str]:
    return {
        item.strip()
        for item in str(value).split(";")
        if item.strip()
    }


def _validate_coder(
    frame: pd.DataFrame,
    *,
    expected_ids: set[str],
    hidden: pd.DataFrame,
    labels: list[str],
    evidence: list[str],
) -> list[str]:
    errors: list[str] = []
    required = {"blind_item_id", "abstain", *labels, *evidence}
    missing = required - set(frame.columns)
    if missing:
        return [f"missing columns: {sorted(missing)}"]
    identifiers = frame["blind_item_id"].astype(str)
    if identifiers.duplicated().any():
        errors.append("duplicate blind_item_id")
    observed_ids = set(identifiers)
    if observed_ids != expected_ids:
        errors.append(
            "item set mismatch: "
            f"missing={len(expected_ids - observed_ids)}, "
            f"extra={len(observed_ids - expected_ids)}"
        )
    if errors:
        return errors
    allowed_spans = {
        str(row.blind_item_id): {
            str(span["span_id"])
            for span in json.loads(str(row.spans_json))
        }
        for row in hidden.itertuples(index=False)
    }
    indexed = frame.set_index("blind_item_id", drop=False)
    for blind_item_id in sorted(expected_ids):
        row = indexed.loc[blind_item_id]
        for column in [*labels, "abstain"]:
            value = str(row[column]).strip()
            if value not in {"0", "1"}:
                errors.append(f"{blind_item_id}: {column} is not binary")
        for column in evidence:
            spans = _split_spans(str(row[column]))
            invalid = spans - allowed_spans[blind_item_id]
            if invalid:
                errors.append(
                    f"{blind_item_id}: {column} has invalid spans "
                    f"{sorted(invalid)}"
                )
        for label in labels:
            evidence_column = label.replace("__", "_evidence__", 1)
            value = str(row[label]).strip()
            spans = _split_spans(str(row[evidence_column]))
            if value == "1" and not spans:
                errors.append(
                    f"{blind_item_id}: {label}=1 lacks evidence"
                )
            if value == "0" and spans:
                errors.append(
                    f"{blind_item_id}: {label}=0 has evidence"
                )
        binary_values = {
            column: str(row[column]).strip()
            for column in [*labels, "abstain"]
        }
        if all(value in {"0", "1"} for value in binary_values.values()):
            event_or_coarse = [
                binary_values[column]
                for column in labels
                if column.startswith(("event__", "coarse__"))
            ]
            expected_abstain = str(
                int(not any(value == "1" for value in event_or_coarse))
            )
            if binary_values["abstain"] != expected_abstain:
                errors.append(
                    f"{blind_item_id}: abstain must equal "
                    f"{expected_abstain}"
                )
    return errors


def _human_agreement(
    first: pd.DataFrame,
    second: pd.DataFrame,
    hidden: pd.DataFrame,
    *,
    labels: list[str],
) -> pd.DataFrame:
    first = first.set_index("blind_item_id")
    second = second.set_index("blind_item_id")
    rows = []
    for sample_role in ("natural", "enriched", "all"):
        identifiers = hidden.loc[
            hidden["sample_role"].ne("training")
            if sample_role == "all"
            else hidden["sample_role"].eq(sample_role),
            "blind_item_id",
        ].astype(str)
        for label in labels:
            left = first.loc[identifiers, label].astype(int).to_numpy()
            right = second.loc[identifiers, label].astype(int).to_numpy()
            rows.append({
                "sample_role": sample_role,
                "target_type": label.split("__", 1)[0],
                "code": label.split("__", 1)[1],
                "n": int(len(identifiers)),
                "coder_a_positive": int(left.sum()),
                "coder_b_positive": int(right.sum()),
                "raw_agreement": float(np.mean(left == right)),
                "gwet_ac1": gwet_ac1_binary(left, right),
            })
    return pd.DataFrame(rows)


def _adjudication_queue(
    first: pd.DataFrame,
    second: pd.DataFrame,
    hidden: pd.DataFrame,
    *,
    labels: list[str],
    evidence: list[str],
    seed: int,
    review_fraction: float,
) -> pd.DataFrame:
    first = first.set_index("blind_item_id")
    second = second.set_index("blind_item_id")
    hidden = hidden.set_index("blind_item_id")
    all_columns = [*labels, *evidence, "abstain"]
    rows = []
    for blind_item_id in first.index:
        disagreements = [
            column
            for column in all_columns
            if str(first.at[blind_item_id, column]).strip()
            != str(second.at[blind_item_id, column]).strip()
        ]
        review_draw = (
            int(
                _hash_order(
                    str(blind_item_id),
                    salt=f"v8b21-adjudication-{seed}",
                )[:12],
                16,
            )
            / float(16**12)
        )
        if not disagreements and review_draw >= review_fraction:
            continue
        row: dict[str, Any] = {
            "blind_item_id": blind_item_id,
            "review_reason": (
                "coder_disagreement"
                if disagreements
                else "agreement_quality_review"
            ),
            "disagreement_columns": ";".join(disagreements),
            "spans_json": str(hidden.at[blind_item_id, "spans_json"]),
        }
        for column in all_columns:
            row[f"coder_A__{column}"] = first.at[blind_item_id, column]
            row[f"coder_B__{column}"] = second.at[blind_item_id, column]
            row[f"final__{column}"] = ""
        row["adjudicator_notes"] = ""
        rows.append(row)
    return pd.DataFrame(rows)


def _validate_adjudication(
    frame: pd.DataFrame,
    queue: pd.DataFrame,
    hidden: pd.DataFrame,
    *,
    labels: list[str],
    evidence: list[str],
) -> list[str]:
    renamed = pd.DataFrame({
        "blind_item_id": frame["blind_item_id"],
        **{
            column: frame[f"final__{column}"]
            for column in [*labels, *evidence, "abstain"]
            if f"final__{column}" in frame
        },
    })
    return _validate_coder(
        renamed,
        expected_ids=set(queue["blind_item_id"].astype(str)),
        hidden=hidden.loc[
            hidden["blind_item_id"].astype(str).isin(
                set(queue["blind_item_id"].astype(str))
            )
        ],
        labels=labels,
        evidence=evidence,
    )


def _adjudicated_gold(
    first: pd.DataFrame,
    queue: pd.DataFrame,
    adjudicated: pd.DataFrame,
    *,
    labels: list[str],
    evidence: list[str],
) -> pd.DataFrame:
    gold = first.set_index("blind_item_id")[
        [*labels, *evidence, "abstain"]
    ].copy()
    reviewed = adjudicated.set_index("blind_item_id")
    for blind_item_id in queue["blind_item_id"].astype(str):
        for column in [*labels, *evidence, "abstain"]:
            gold.at[blind_item_id, column] = reviewed.at[
                blind_item_id,
                f"final__{column}",
            ]
    return gold.reset_index()


def _prediction(
    payload: dict[str, Any],
    *,
    groups: dict[str, list[str]],
) -> dict[str, Any]:
    opportunities = {
        str(row["opportunity_code"]): set(map(str, row["evidence_span_ids"]))
        for row in payload["opportunities"]
    }
    events = {
        str(row["event_code"]): set(map(str, row["evidence_span_ids"]))
        for row in payload["events"]
    }
    values: dict[str, Any] = {}
    for code in OPPORTUNITY_CODES:
        values[f"opportunity__{code}"] = int(code in opportunities)
        values[f"opportunity_evidence__{code}"] = opportunities.get(
            code,
            set(),
        )
    for code in EVENT_CODES:
        values[f"event__{code}"] = int(code in events)
        values[f"event_evidence__{code}"] = events.get(code, set())
    for family, members in groups.items():
        present = [code for code in members if code in events]
        values[f"coarse__{family}"] = int(bool(present))
        values[f"coarse_evidence__{family}"] = set().union(
            *(events[code] for code in present)
        ) if present else set()
    return values


def _observer_frames(
    hidden: pd.DataFrame,
    *,
    groups: dict[str, list[str]],
) -> dict[str, pd.DataFrame]:
    rows: dict[str, list[dict[str, Any]]] = {
        "primary_rep0": [],
        "primary_rep1": [],
        "primary_soft_binary": [],
        "audit": [],
    }
    for source in hidden.itertuples(index=False):
        repetitions = [
            _prediction(
                json.loads(str(getattr(source, f"primary_rep{rep}_json"))),
                groups=groups,
            )
            for rep in (0, 1)
        ]
        for rep, values in enumerate(repetitions):
            rows[f"primary_rep{rep}"].append({
                "blind_item_id": str(source.blind_item_id),
                **values,
            })
        combined: dict[str, Any] = {
            "blind_item_id": str(source.blind_item_id)
        }
        for column in repetitions[0]:
            if "_evidence__" in column:
                combined[column] = (
                    repetitions[0][column] | repetitions[1][column]
                )
            else:
                combined[column] = int(
                    (
                        float(repetitions[0][column])
                        + float(repetitions[1][column])
                    )
                    / 2.0
                    >= 0.5
                )
        rows["primary_soft_binary"].append(combined)
        if str(source.audit_json).strip():
            rows["audit"].append({
                "blind_item_id": str(source.blind_item_id),
                **_prediction(
                    json.loads(str(source.audit_json)),
                    groups=groups,
                ),
            })
    return {
        name: pd.DataFrame(values)
        for name, values in rows.items()
    }


def _observer_metrics(
    gold: pd.DataFrame,
    predictions: dict[str, pd.DataFrame],
    hidden: pd.DataFrame,
    *,
    labels: list[str],
) -> pd.DataFrame:
    gold = gold.set_index("blind_item_id")
    hidden = hidden.set_index("blind_item_id")
    audit_ids = set(
        predictions["audit"]["blind_item_id"].astype(str)
    ) if not predictions["audit"].empty else set()
    rows = []
    for observer, frame in predictions.items():
        if frame.empty:
            continue
        frame = frame.set_index("blind_item_id")
        for sample_role in (
            "natural",
            "enriched",
            "all",
            "audit_natural",
        ):
            if sample_role == "audit_natural":
                eligible = hidden.index[
                    hidden["sample_role"].eq("natural")
                    & hidden.index.isin(audit_ids)
                ]
            else:
                eligible = hidden.index[
                    hidden["sample_role"].ne("training")
                    if sample_role == "all"
                    else hidden["sample_role"].eq(sample_role)
                ]
            identifiers = frame.index.intersection(eligible)
            if not len(identifiers):
                continue
            for label in labels:
                metrics = binary_metrics(
                    gold.loc[identifiers, label].astype(int),
                    frame.loc[identifiers, label].astype(int),
                )
                rows.append({
                    "observer": observer,
                    "sample_role": sample_role,
                    "target_type": label.split("__", 1)[0],
                    "code": label.split("__", 1)[1],
                    "n": int(len(identifiers)),
                    **metrics,
                })
    return pd.DataFrame(rows)


def _span_metrics(
    gold: pd.DataFrame,
    predictions: dict[str, pd.DataFrame],
    hidden: pd.DataFrame,
    *,
    groups: dict[str, list[str]],
) -> pd.DataFrame:
    gold = gold.set_index("blind_item_id")
    hidden = hidden.set_index("blind_item_id")
    natural = set(
        hidden.index[hidden["sample_role"].eq("natural")]
    )
    rows = []
    for observer in ("primary_soft_binary", "audit"):
        frame = predictions[observer]
        if frame.empty:
            continue
        frame = frame.set_index("blind_item_id")
        identifiers = sorted(natural & set(frame.index))
        for family in groups:
            label = f"coarse__{family}"
            evidence = f"coarse_evidence__{family}"
            instance_scores = []
            for blind_item_id in identifiers:
                if (
                    int(gold.at[blind_item_id, label]) == 1
                    and int(frame.at[blind_item_id, label]) == 1
                ):
                    instance_scores.append(span_set_f1(
                        _split_spans(str(gold.at[blind_item_id, evidence])),
                        frame.at[blind_item_id, evidence],
                    ))
            rows.append({
                "observer": observer,
                "sample_role": "natural",
                "code": family,
                "true_positive_instances": int(len(instance_scores)),
                "mean_span_f1": (
                    float(np.mean(instance_scores))
                    if instance_scores
                    else float("nan")
                ),
            })
    return pd.DataFrame(rows)


def _metric_lookup(
    metrics: pd.DataFrame,
    *,
    observer: str,
    target_type: str,
    sample_role: str = "natural",
) -> pd.DataFrame:
    return metrics.loc[
        metrics["observer"].eq(observer)
        & metrics["sample_role"].eq(sample_role)
        & metrics["target_type"].eq(target_type)
    ].set_index("code")


def _gate_decision(
    agreement: pd.DataFrame,
    metrics: pd.DataFrame,
    spans: pd.DataFrame,
    gold: pd.DataFrame,
    hidden: pd.DataFrame,
    *,
    groups: dict[str, list[str]],
    gates: dict[str, float],
) -> dict[str, Any]:
    coarse_agreement = agreement.loc[
        agreement["sample_role"].eq("natural")
        & agreement["target_type"].eq("coarse")
    ].set_index("code")
    primary_coarse = _metric_lookup(
        metrics,
        observer="primary_soft_binary",
        target_type="coarse",
    )
    primary_opportunities = _metric_lookup(
        metrics,
        observer="primary_soft_binary",
        target_type="opportunity",
    )
    audit_coarse = _metric_lookup(
        metrics,
        observer="audit",
        target_type="coarse",
    )
    primary_audit_subset = _metric_lookup(
        metrics,
        observer="primary_soft_binary",
        target_type="coarse",
        sample_role="audit_natural",
    )
    gold_indexed = gold.set_index("blind_item_id")
    evaluation_ids = hidden.loc[
        hidden["sample_role"].ne("training"),
        "blind_item_id",
    ].astype(str)
    support = {
        family: int(
            gold_indexed.loc[evaluation_ids, f"coarse__{family}"]
            .astype(int)
            .sum()
        )
        for family in groups
    }
    primary_macro = float(primary_coarse["f1"].mean())
    opportunity_macro = float(primary_opportunities["f1"].mean())
    audit_macro = float(audit_coarse["f1"].mean())
    primary_audit_subset_macro = float(
        primary_audit_subset["f1"].mean()
    )
    primary_span_rows = spans.loc[
        spans["observer"].eq("primary_soft_binary")
    ]
    span_macro = float(
        np.average(
            primary_span_rows["mean_span_f1"],
            weights=primary_span_rows["true_positive_instances"],
        )
    )
    checks = {
        "human_coarse_ac1": bool(
            (coarse_agreement["gwet_ac1"]
             >= float(gates["minimum_coarse_gwet_ac1"])).all()
        ),
        "primary_coarse_macro_f1": (
            primary_macro
            >= float(gates["minimum_primary_coarse_macro_f1"])
        ),
        "primary_coarse_precision": bool(
            (primary_coarse["precision"]
             >= float(gates["minimum_coarse_precision"])).all()
        ),
        "primary_coarse_recall": bool(
            (primary_coarse["recall"]
             >= float(gates["minimum_coarse_recall"])).all()
        ),
        "primary_coarse_f1": bool(
            (primary_coarse["f1"]
             >= float(gates["minimum_coarse_f1"])).all()
        ),
        "opportunity_macro_f1": (
            opportunity_macro
            >= float(gates["minimum_opportunity_macro_f1"])
        ),
        "opportunity_family_f1": bool(
            (primary_opportunities["f1"]
             >= float(gates["minimum_opportunity_family_f1"])).all()
        ),
        "evidence_span_f1": (
            span_macro >= float(gates["minimum_evidence_span_f1"])
        ),
        "audit_coarse_macro_f1": (
            audit_macro >= float(gates["minimum_audit_coarse_macro_f1"])
        ),
        "primary_audit_gap": (
            abs(primary_audit_subset_macro - audit_macro)
            <= float(gates["maximum_primary_audit_macro_f1_gap"])
        ),
        "coarse_positive_support": all(
            value
            >= int(gates["minimum_adjudicated_positives_per_coarse_family"])
            for value in support.values()
        ),
    }
    ontology_stop = bool(
        (
            coarse_agreement["gwet_ac1"]
            < float(gates["ontology_stop_gwet_ac1"])
        ).any()
    )
    atomic = _metric_lookup(
        metrics,
        observer="primary_soft_binary",
        target_type="event",
    )
    independent_atomic = sorted(
        atomic.index[
            atomic["f1"]
            >= float(gates["minimum_atomic_independent_scoring_f1"])
        ].astype(str)
    )
    status = (
        "V8_BEHAVIOR_V21_HUMAN_ONTOLOGY_STOP"
        if ontology_stop
        else (
            "V8_BEHAVIOR_V21_HUMAN_GATE_PASS"
            if all(checks.values())
            else "V8_BEHAVIOR_V21_HUMAN_GATE_STOP"
        )
    )
    return {
        "status": status,
        "checks": checks,
        "headline": {
            "primary_coarse_macro_f1": primary_macro,
            "opportunity_macro_f1": opportunity_macro,
            "evidence_span_f1": span_macro,
            "audit_coarse_macro_f1": audit_macro,
            "primary_coarse_macro_f1_on_audit_items": (
                primary_audit_subset_macro
            ),
            "primary_audit_macro_f1_gap": abs(
                primary_audit_subset_macro - audit_macro
            ),
            "minimum_human_coarse_gwet_ac1": float(
                coarse_agreement["gwet_ac1"].min()
            ),
        },
        "coarse_positive_support": support,
        "independently_scoreable_atomic_events": independent_atomic,
        "claim_boundary": (
            "A pass licenses a fresh author replication of the frozen "
            "explicit-behavior hierarchy only. It does not validate "
            "personality, emotion, diagnosis, clinical use, or a geometry "
            "bridge."
        ),
    }


def _finalize(
    output_dir: Path,
    *,
    decision: dict[str, Any],
    packet_dir: Path,
    input_paths: list[Path],
) -> None:
    _write_json(output_dir / "human_gate_decision.json", decision)
    write_run_manifest(
        output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=input_paths,
        config_path=packet_dir / "config.resolved.json",
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_human_coding.py",
        ],
        estimand_id="V8-I11-behavior-v21-human-observer-gate",
        external_labels_read=decision["status"]
        not in {"V8_BEHAVIOR_V21_WAITING_FOR_HUMAN_CODING"},
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        output_dir,
        output_dir / "artifact_inventory.json",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-dir", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--coder-a", type=Path)
    parser.add_argument("--coder-b", type=Path)
    parser.add_argument("--adjudicated", type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    packet_dir = args.packet_dir
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    config = _read_json(packet_dir / "config.resolved.json")
    candidate = _read_json(ROOT / str(config["candidate_config"]))
    groups = {
        str(code): list(map(str, events))
        for code, events in candidate["coarse_event_families"].items()
    }
    labels, evidence = _target_columns(groups)
    hidden = pd.read_csv(
        packet_dir / "HIDDEN_KEY_DO_NOT_SHARE.csv",
        dtype=str,
        keep_default_na=False,
    )
    evaluation_hidden = hidden.loc[
        hidden["sample_role"].ne("training")
    ].copy()
    expected_ids = set(evaluation_hidden["blind_item_id"].astype(str))
    coder_a_path = args.coder_a or packet_dir / "coder_A_items.csv"
    coder_b_path = args.coder_b or packet_dir / "coder_B_items.csv"
    coder_a = pd.read_csv(coder_a_path, dtype=str, keep_default_na=False)
    coder_b = pd.read_csv(coder_b_path, dtype=str, keep_default_na=False)
    errors_a = _validate_coder(
        coder_a,
        expected_ids=expected_ids,
        hidden=evaluation_hidden,
        labels=labels,
        evidence=evidence,
    )
    errors_b = _validate_coder(
        coder_b,
        expected_ids=expected_ids,
        hidden=evaluation_hidden,
        labels=labels,
        evidence=evidence,
    )
    if errors_a or errors_b:
        decision = {
            "status": "V8_BEHAVIOR_V21_WAITING_FOR_HUMAN_CODING",
            "coder_a_errors": errors_a[:100],
            "coder_b_errors": errors_b[:100],
            "coder_a_error_count": len(errors_a),
            "coder_b_error_count": len(errors_b),
            "claim_boundary": (
                "No observer-accuracy result exists until both blind coder "
                "files are complete and valid."
            ),
        }
        _finalize(
            output_dir,
            decision=decision,
            packet_dir=packet_dir,
            input_paths=[coder_a_path, coder_b_path],
        )
        print(json.dumps(decision, indent=2))
        return 0
    agreement = _human_agreement(
        coder_a,
        coder_b,
        evaluation_hidden,
        labels=labels,
    )
    agreement.to_csv(output_dir / "human_agreement.csv", index=False)
    queue = _adjudication_queue(
        coder_a,
        coder_b,
        evaluation_hidden,
        labels=labels,
        evidence=evidence,
        seed=int(config["seed"]),
        review_fraction=float(config["consensus_review_fraction"]),
    )
    queue.to_csv(output_dir / "adjudicator_items.csv", index=False)
    if args.adjudicated is None:
        decision = {
            "status": "V8_BEHAVIOR_V21_WAITING_FOR_ADJUDICATION",
            "adjudication_items": int(len(queue)),
            "coder_disagreements": int(
                queue["review_reason"].eq("coder_disagreement").sum()
            ),
            "agreement_quality_reviews": int(
                queue["review_reason"].eq(
                    "agreement_quality_review"
                ).sum()
            ),
            "claim_boundary": (
                "Human-human agreement is descriptive only; observer "
                "accuracy is unopened until adjudication is complete."
            ),
        }
        _finalize(
            output_dir,
            decision=decision,
            packet_dir=packet_dir,
            input_paths=[coder_a_path, coder_b_path],
        )
        print(json.dumps(decision, indent=2))
        return 0
    adjudicated = pd.read_csv(
        args.adjudicated,
        dtype=str,
        keep_default_na=False,
    )
    adjudication_errors = _validate_adjudication(
        adjudicated,
        queue,
        evaluation_hidden,
        labels=labels,
        evidence=evidence,
    )
    if adjudication_errors:
        decision = {
            "status": "V8_BEHAVIOR_V21_WAITING_FOR_ADJUDICATION",
            "adjudication_errors": adjudication_errors[:100],
            "adjudication_error_count": len(adjudication_errors),
            "claim_boundary": "No observer-accuracy result is opened.",
        }
        _finalize(
            output_dir,
            decision=decision,
            packet_dir=packet_dir,
            input_paths=[coder_a_path, coder_b_path, args.adjudicated],
        )
        print(json.dumps(decision, indent=2))
        return 0
    gold = _adjudicated_gold(
        coder_a,
        queue,
        adjudicated,
        labels=labels,
        evidence=evidence,
    )
    gold.to_csv(output_dir / "adjudicated_gold_blind.csv", index=False)
    predictions = _observer_frames(evaluation_hidden, groups=groups)
    metrics = _observer_metrics(
        gold,
        predictions,
        evaluation_hidden,
        labels=labels,
    )
    spans = _span_metrics(
        gold,
        predictions,
        evaluation_hidden,
        groups=groups,
    )
    metrics.to_csv(output_dir / "observer_metrics.csv", index=False)
    spans.to_csv(output_dir / "evidence_span_metrics.csv", index=False)
    decision = _gate_decision(
        agreement,
        metrics,
        spans,
        gold,
        evaluation_hidden,
        groups=groups,
        gates=config["gates"],
    )
    _finalize(
        output_dir,
        decision=decision,
        packet_dir=packet_dir,
        input_paths=[coder_a_path, coder_b_path, args.adjudicated],
    )
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
