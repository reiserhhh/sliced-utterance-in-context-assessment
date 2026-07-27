#!/usr/bin/env python3
"""Audit whether existing MEPS views can identify behavior-v2.1 C2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


DEFAULT_CONFIG = (
    ROOT / "configs" / "v8_behavior_v21_meps_c2_preflight.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_behavior_v21_meps_c2_preflight"
    / "meps_20260725"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    metadata_path = ROOT / str(config["source_metadata"])
    readiness_path = ROOT / str(config["source_readiness"])
    metadata = pd.read_csv(metadata_path)
    conditions = list(map(str, config["fixed_conditions"]))
    participant_count = int(metadata["participant_code"].nunique())
    slots = metadata.loc[
        metadata["view_type"].eq("meps_answer_slot")
        & metadata["condition"].isin(conditions)
    ].copy()
    slot_counts = (
        slots.groupby(
            ["participant_code", "condition"],
            observed=True,
        )
        .size()
        .unstack("condition", fill_value=0)
        .reindex(columns=conditions, fill_value=0)
    )
    ai_chat = metadata.loc[
        metadata["view_type"].eq("meps_ai_chat")
        & metadata["condition"].isin(conditions)
    ].copy()
    ai_turns = (
        ai_chat.pivot_table(
            index="participant_code",
            columns="condition",
            values="user_turns",
            aggfunc="max",
            fill_value=0,
        )
        .reindex(columns=conditions, fill_value=0)
        .reindex(slot_counts.index, fill_value=0)
        .astype(int)
    )
    minimum = int(config["minimum_opportunities_per_condition_family"])
    direct_complete = slot_counts.ge(minimum).all(axis=1)
    ai_complete = ai_turns.ge(minimum).all(axis=1)
    condition_rows = []
    for condition in conditions:
        condition_rows.append({
            "condition": condition,
            "participants_with_direct_answer": int(
                slot_counts[condition].gt(0).sum()
            ),
            "median_direct_answer_slots": float(
                slot_counts[condition].median()
            ),
            "participants_with_minimum_direct_slots": int(
                slot_counts[condition].ge(minimum).sum()
            ),
            "participants_with_ai_assistance": int(
                ai_turns[condition].gt(0).sum()
            ),
            "median_ai_user_turns_among_users": float(
                ai_turns.loc[
                    ai_turns[condition].gt(0),
                    condition,
                ].median()
            ),
            "participants_with_minimum_ai_turns": int(
                ai_turns[condition].ge(minimum).sum()
            ),
        })
    condition_support = pd.DataFrame(condition_rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    condition_support.to_csv(
        args.output_dir / "condition_support.csv",
        index=False,
    )
    complete_fraction = float(direct_complete.mean())
    ai_complete_fraction = float(ai_complete.mean())
    checks = {
        "shared_fixed_prompts_available": bool(
            (slot_counts.gt(0).all(axis=1)).all()
        ),
        "minimum_direct_opportunities": bool(direct_complete.all()),
        "minimum_ai_opportunities": bool(
            ai_complete_fraction
            >= float(config["minimum_complete_participant_fraction"])
        ),
        "independent_repeated_condition": False,
    }
    decision = {
        "status": "V8_BEHAVIOR_V21_MEPS_C2_IDENTIFIABILITY_PILOT_ONLY",
        "checks": checks,
        "participants": participant_count,
        "fixed_conditions": conditions,
        "direct_answer_slots_per_participant_condition": {
            condition: sorted(
                map(int, slot_counts[condition].unique())
            )
            for condition in conditions
        },
        "participants_meeting_direct_minimum_all_conditions": int(
            direct_complete.sum()
        ),
        "direct_minimum_complete_fraction": complete_fraction,
        "participants_meeting_ai_turn_minimum_all_conditions": int(
            ai_complete.sum()
        ),
        "ai_minimum_complete_fraction": ai_complete_fraction,
        "supports": [
            "shared-prompt observer ontology pilot",
            "condition contrast",
            "opportunity prevalence estimation",
            "same-session procedural feasibility",
        ],
        "does_not_support": [
            "formal C2 confirmation",
            "independent repeated-condition response",
            "cross-session stability",
            "personality or emotion validity",
            "clinical scoring",
        ],
        "new_llm_calls": 0,
        "raw_text_read": False,
        "external_labels_read": False,
        "raw_identifiers_persisted": False,
        "claim_boundary": str(config["claim_boundary"]),
    }
    _write_json(args.output_dir / "preflight_decision.json", decision)
    _write_json(args.output_dir / "config.resolved.json", config)
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[metadata_path, readiness_path],
        config_path=args.config,
        code_paths=[Path(__file__)],
        estimand_id="V8-I13-behavior-v21-meps-c2-support-preflight",
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
