#!/usr/bin/env python3
"""Build the blind SUICA behavior-v2.1 human-coding packet."""
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
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_behavior_v2 import (  # noqa: E402
    EVENT_CODES,
    OPPORTUNITY_CODES,
    observation_frame,
    validate_behavior_v2_payload,
)
from suica_core.v8_realtext import stable_digest  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_behavior_v21_human_gold.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_behavior_v21_human_gold_packet"


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


def _payload_segment_map(
    outputs: list[dict[str, Any]],
) -> dict[tuple[int, str], dict[str, Any]]:
    rows = {}
    for repetition, output in enumerate(outputs):
        for profile in output["profiles"]:
            for segment in profile["segments"]:
                rows[(repetition, str(segment["segment_id"]))] = segment
    return rows


def _cached_segment_map(cache_dir: Path) -> dict[str, dict[str, Any]]:
    """Load unique ready segment predictions from a structured-call cache."""
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted(cache_dir.glob("*.json")):
        if path.name.startswith("._"):
            continue
        result = _read_json(path)
        if result.get("status") != "STRUCTURED_STAGE_READY":
            continue
        for profile in result["output"]["profiles"]:
            for segment in profile["segments"]:
                segment_id = str(segment["segment_id"])
                if segment_id in rows and rows[segment_id] != segment:
                    raise RuntimeError(
                        f"conflicting cached predictions for {segment_id}"
                    )
                rows[segment_id] = segment
    return rows


def _codes(segment: dict[str, Any], field: str, code_field: str) -> set[str]:
    return {
        str(row[code_field])
        for row in segment[field]
    }


def _diagnostic_scores(
    profiles: list[dict[str, Any]],
    outputs: list[dict[str, Any]],
    *,
    groups: dict[str, list[str]],
) -> pd.DataFrame:
    payloads = _payload_segment_map(outputs)
    repeated = observation_frame(profiles, outputs)
    prevalence = {
        event: float(repeated[f"event::{event}"].mean())
        for event in EVENT_CODES
    }
    rows = []
    for profile in profiles:
        for source_segment in profile["segments"]:
            segment_id = str(source_segment["segment_id"])
            first = payloads[(0, segment_id)]
            second = payloads[(1, segment_id)]
            first_events = _codes(first, "events", "event_code")
            second_events = _codes(second, "events", "event_code")
            first_opportunities = _codes(
                first,
                "opportunities",
                "opportunity_code",
            )
            second_opportunities = _codes(
                second,
                "opportunities",
                "opportunity_code",
            )
            union = first_events | second_events
            rare_score = float(sum(
                1.0 / max(prevalence[event], 0.01)
                for event in union
            ))
            group_presence = {
                group: int(bool(union & set(events)))
                for group, events in groups.items()
            }
            rows.append({
                "profile_id": str(profile["profile_id"]),
                "author_id": str(profile["author_id"]),
                "side": str(profile["side"]),
                "cohort_split": str(profile["cohort_split"]),
                "segment_id": segment_id,
                "segment_index": int(source_segment["segment_index"]),
                "condition": str(source_segment["condition"]),
                "event_disagreement": int(
                    len(first_events ^ second_events)
                ),
                "opportunity_disagreement": int(
                    len(first_opportunities ^ second_opportunities)
                ),
                "rare_event_score": rare_score,
                "event_diversity": int(len(union)),
                **{
                    f"group::{group}": value
                    for group, value in group_presence.items()
                },
            })
    return pd.DataFrame(rows)


def _assign_roles(
    diagnostics_frame: pd.DataFrame,
    *,
    groups: list[str],
    seed: int,
) -> pd.DataFrame:
    """Assign 7 natural, 1 training, and 4 enriched items per profile."""
    rows = []
    for profile_id, group in diagnostics_frame.groupby(
        "profile_id",
        observed=True,
        sort=False,
    ):
        ordered = group.assign(
            _natural_order=group["segment_id"].map(
                lambda value: _hash_order(
                    str(value),
                    salt=f"v8b21-natural-{seed}",
                )
            )
        ).sort_values("_natural_order", kind="stable")
        natural_ids = set(ordered.head(7)["segment_id"].astype(str))
        remainder = ordered.loc[
            ~ordered["segment_id"].astype(str).isin(natural_ids)
        ].copy()
        target_index = int(
            _hash_order(
                str(profile_id),
                salt=f"v8b21-training-family-{seed}",
            )[:8],
            16,
        ) % len(groups)
        target = groups[target_index]
        remainder["_training_score"] = (
            10.0 * remainder[f"group::{target}"].astype(float)
            + remainder["event_diversity"].astype(float)
            - remainder["event_disagreement"].astype(float)
            - remainder["opportunity_disagreement"].astype(float)
        )
        training_id = str(
            remainder.sort_values(
                ["_training_score", "_natural_order"],
                ascending=[False, True],
                kind="stable",
            ).iloc[0]["segment_id"]
        )
        for row in group.itertuples(index=False):
            segment_id = str(row.segment_id)
            if segment_id in natural_ids:
                role = "natural"
            elif segment_id == training_id:
                role = "training"
            else:
                role = "enriched"
            values = row._asdict()
            values["sample_role"] = role
            values["training_target_family"] = (
                target if role == "training" else ""
            )
            rows.append(values)
    assigned = pd.DataFrame(rows)
    expected = {"training": 48, "natural": 336, "enriched": 192}
    observed = assigned["sample_role"].value_counts().to_dict()
    if observed != expected:
        raise RuntimeError(f"unexpected packet partition: {observed}")
    return assigned


def _coding_columns(
    *,
    groups: list[str],
) -> list[str]:
    columns = []
    for code in OPPORTUNITY_CODES:
        columns.extend([
            f"opportunity__{code}",
            f"opportunity_evidence__{code}",
        ])
    for code in EVENT_CODES:
        columns.extend([
            f"event__{code}",
            f"event_evidence__{code}",
        ])
    for code in groups:
        columns.extend([
            f"coarse__{code}",
            f"coarse_evidence__{code}",
        ])
    return columns


def _coder_rows(
    assigned: pd.DataFrame,
    profiles: list[dict[str, Any]],
    *,
    groups: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    source = {
        str(segment["segment_id"]): {
            "profile": profile,
            "segment": segment,
        }
        for profile in profiles
        for segment in profile["segments"]
    }
    visible_rows = []
    hidden_rows = []
    coding_columns = _coding_columns(groups=groups)
    for row in assigned.itertuples(index=False):
        segment_id = str(row.segment_id)
        material = source[segment_id]
        blind_item_id = stable_digest(
            segment_id,
            salt="v8-behavior-human-item",
        )
        visible = {
            "blind_item_id": blind_item_id,
            "spans_json": json.dumps(
                material["segment"]["spans"],
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            **{column: "" for column in coding_columns},
            "abstain": "",
            "coder_notes": "",
        }
        hidden = {
            "blind_item_id": blind_item_id,
            "sample_role": str(row.sample_role),
            "training_target_family": str(row.training_target_family),
            "profile_id": str(material["profile"]["profile_id"]),
            "author_id": str(material["profile"]["author_id"]),
            "side": str(material["profile"]["side"]),
            "cohort_split": str(material["profile"]["cohort_split"]),
            "segment_id": segment_id,
            "segment_index": int(material["segment"]["segment_index"]),
            "condition": str(material["segment"]["condition"]),
            "token_count": int(material["segment"]["token_count"]),
            "spans_json": visible["spans_json"],
        }
        visible_rows.append(visible)
        hidden_rows.append(hidden)
    return pd.DataFrame(visible_rows), pd.DataFrame(hidden_rows)


def _prediction_key(
    hidden: pd.DataFrame,
    outputs: list[dict[str, Any]],
    *,
    audit_segments: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    payloads = _payload_segment_map(outputs)
    rows = []
    for row in hidden.itertuples(index=False):
        values = row._asdict()
        for repetition in range(len(outputs)):
            segment = payloads[(repetition, str(row.segment_id))]
            values[f"primary_rep{repetition}_json"] = json.dumps(
                segment,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        audit = audit_segments.get(str(row.segment_id))
        values["audit_json"] = (
            json.dumps(
                audit,
                ensure_ascii=False,
                separators=(",", ":"),
            )
            if audit is not None
            else ""
        )
        rows.append(values)
    return pd.DataFrame(rows)


def _shuffle(
    frame: pd.DataFrame,
    *,
    seed: int,
    coder_id: str,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(frame))
    result = frame.iloc[order].reset_index(drop=True).copy()
    result.insert(0, "coder_id", coder_id)
    result.insert(1, "coder_order", np.arange(1, len(result) + 1))
    return result


def _codebook(groups: dict[str, list[str]], boundary: str) -> str:
    group_lines = "\n".join(
        f"- `{group}`: any explicit atomic act in "
        + ", ".join(f"`{event}`" for event in events)
        for group, events in groups.items()
    )
    return f"""# SUICA V8 Behavior-v2.1 Human Coding Rubric

## Scope

Code explicit textual acts only. Do not infer personality, stable traits,
emotion state, diagnosis, motive, intention, severity, confidence, or an
author-level score.

Each `spans_json` cell contains the only permitted evidence spans. Enter:

- `1` when the code is explicitly supported;
- `0` when it is not;
- semicolon-separated exact span IDs in each corresponding evidence column;
- `abstain=1` only when every event and coarse-family code is 0.

Opportunity and atomic-event definitions are frozen in
`FROZEN_OBSERVER_RUBRIC.txt`, copied byte-for-byte from
`prompts/v8_behavior_observer_v2.txt`. Coarse families are:

{group_lines}

Coders must not discuss items. The adjudicator reviews all disagreements and a
random 10% of agreements after both files are locked.

## Training sequence

An expert first completes and adjudicates `training_key_template.csv`. Both
coders code the 48 `training_items.csv` rows, compare against that expert key,
and resolve rubric questions before opening their evaluation sheets. Training
items never enter accuracy or agreement estimates.

## Claim boundary

{boundary}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    source = ROOT / str(config["source_run"])
    if verify_artifact_inventory(
        source / "artifact_inventory.json"
    )["status"] != "INVENTORY_PASS":
        raise RuntimeError("behavior-v2 pilot inventory failed")
    candidate = _read_json(ROOT / str(config["candidate_config"]))
    groups = {
        str(code): list(map(str, events))
        for code, events in candidate["coarse_event_families"].items()
    }
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
    for output in outputs:
        validate_behavior_v2_payload(
            output,
            schema=schema,
            profiles=profiles,
        )
    diagnostic_frame = _diagnostic_scores(
        profiles,
        outputs,
        groups=groups,
    )
    assigned = _assign_roles(
        diagnostic_frame,
        groups=list(groups),
        seed=int(config["seed"]),
    )
    visible, hidden = _coder_rows(
        assigned,
        profiles,
        groups=list(groups),
    )
    audit_segments = _cached_segment_map(source / "cache" / "audit")
    key = _prediction_key(
        hidden,
        outputs,
        audit_segments=audit_segments,
    )
    training_ids = set(
        key.loc[key["sample_role"].eq("training"), "blind_item_id"]
    )
    evaluation_ids = set(key["blind_item_id"]) - training_ids
    training = visible.loc[
        visible["blind_item_id"].isin(training_ids)
    ].reset_index(drop=True)
    evaluation = visible.loc[
        visible["blind_item_id"].isin(evaluation_ids)
    ].reset_index(drop=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    training.to_csv(args.output_dir / "training_items.csv", index=False)
    training.to_csv(
        args.output_dir / "training_key_template.csv",
        index=False,
    )
    _shuffle(
        evaluation,
        seed=int(config["seed"]) + 1,
        coder_id="coder_A",
    ).to_csv(args.output_dir / "coder_A_items.csv", index=False)
    _shuffle(
        evaluation,
        seed=int(config["seed"]) + 2,
        coder_id="coder_B",
    ).to_csv(args.output_dir / "coder_B_items.csv", index=False)
    key.to_csv(args.output_dir / "HIDDEN_KEY_DO_NOT_SHARE.csv", index=False)
    (args.output_dir / "CODEBOOK.md").write_text(
        _codebook(groups, str(config["claim_boundary"])),
        encoding="utf-8",
    )
    rubric_path = ROOT / "prompts" / "v8_behavior_observer_v2.txt"
    (args.output_dir / "FROZEN_OBSERVER_RUBRIC.txt").write_bytes(
        rubric_path.read_bytes()
    )
    role_summary = (
        key.groupby("sample_role", observed=True)
        .agg(
            items=("blind_item_id", "count"),
            profiles=("profile_id", "nunique"),
            authors=("author_id", "nunique"),
            conditions=("condition", "nunique"),
        )
        .reset_index()
    )
    role_summary.to_csv(args.output_dir / "packet_summary.csv", index=False)
    _write_json(args.output_dir / "config.resolved.json", config)
    _write_json(args.output_dir / "packet_decision.json", {
        "status": "V8_BEHAVIOR_V21_HUMAN_PACKET_READY",
        "unique_segments": int(len(key)),
        "training_items": int(len(training)),
        "natural_items": int(
            key["sample_role"].eq("natural").sum()
        ),
        "enriched_items": int(
            key["sample_role"].eq("enriched").sum()
        ),
        "evaluation_items_per_coder": int(len(evaluation)),
        "coders": 2,
        "adjudicator_required": True,
        "expert_training_key_required": True,
        "audit_segments": int(key["audit_json"].ne("").sum()),
        "new_llm_calls": 0,
        "external_labels_read": False,
        "raw_identifiers_persisted": False,
        "pseudonymous_author_ids_persisted_in_hidden_key": True,
        "raw_text_local_only": True,
        "claim_boundary": str(config["claim_boundary"]),
    })
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            source / "artifact_inventory.json",
            ROOT / str(config["candidate_config"]),
            rubric_path,
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_behavior_v2.py",
            ROOT / "suica_core" / "v8_human_coding.py",
        ],
        estimand_id="V8-I10-behavior-v21-human-gold-packet",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(
        (args.output_dir / "packet_decision.json").read_text(
            encoding="utf-8"
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
