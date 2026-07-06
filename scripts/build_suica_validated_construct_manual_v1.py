#!/usr/bin/env python
"""Build a provisional manual for SUICA constructs with heldout support."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "results" / "suica_validated_construct_manual_v1"
REPORT_PATH = ROOT / "reports" / "suica_validated_construct_manual_v1.md"


CONSTRUCTS = [
    {
        "construct_id": "f05_novelty_play_core",
        "label": "Novelty-Play Core",
        "expected_dimension": "novelty_play",
        "source": "factor_05 repair",
        "construct_definition": "Exploratory, playful, task/interest engagement rather than routine or inert response.",
        "high_pole": "Playful novelty, experimentation, game/task-interest engagement, creative or exploratory stance.",
        "low_pole": "Low novelty/play engagement; neutral, procedural, or non-exploratory text.",
        "scoring_hint": "Use blind-coded novelty_play as the primary score; automated candidate anchor is novelty_play_rate.",
        "dev_summary": ROOT / "results" / "suica_construct_expansion_coding_eval_v1" / "development_acceptance_summary.csv",
        "heldout_summary": ROOT / "results" / "suica_construct_expansion_coding_eval_v1" / "heldout_acceptance_summary.csv",
        "key_path": ROOT / "results" / "suica_construct_expansion_readiness_v1" / "expanded_item_bank_key.csv",
    },
    {
        "construct_id": "f10_directive_action_core",
        "label": "Directive-Action Core",
        "expected_dimension": "directive_interpersonal",
        "source": "factor_10 split repair",
        "construct_definition": "Direct interpersonal guidance plus active action orientation.",
        "high_pole": "Second-person advising, recommendations, action instructions, active coping or task direction.",
        "low_pole": "Low directive stance; less action-directive and less interpersonal instruction.",
        "scoring_hint": "Use blind-coded directive_interpersonal as primary score; agency is a secondary descriptive correlate.",
        "dev_summary": ROOT / "results" / "suica_construct_expansion_coding_eval_v1" / "development_acceptance_summary.csv",
        "heldout_summary": ROOT / "results" / "suica_construct_expansion_coding_eval_v1" / "heldout_acceptance_summary.csv",
        "key_path": ROOT / "results" / "suica_construct_expansion_readiness_v1" / "expanded_item_bank_key.csv",
    },
    {
        "construct_id": "suica_adversity_recovery_core",
        "label": "Adversity-Recovery Core",
        "expected_dimension": "redemption_growth",
        "source": "directive-growth split repair",
        "construct_definition": "Redemptive or self-transformational recovery from difficulty, without requiring directive language.",
        "high_pole": "Recovery, healing, overcoming, moving on, learning from mistakes, or becoming a better person after difficulty.",
        "low_pole": "No strict recovery-growth cue; may include adversity or instrumental learning without redemptive recovery.",
        "scoring_hint": "Use blind-coded redemption_growth as primary score; automated candidate anchor is adversity_recovery_score.",
        "dev_summary": ROOT / "results" / "suica_adversity_recovery_core_eval_v1" / "development_acceptance_summary.csv",
        "heldout_summary": ROOT / "results" / "suica_adversity_recovery_core_eval_v1" / "heldout_acceptance_summary.csv",
        "key_path": ROOT / "results" / "suica_adversity_recovery_core_v1" / "adversity_recovery_key.csv",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA validated construct manual v1.")
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    return parser.parse_args()


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def summary_row(path: Path, construct_id: str) -> pd.Series:
    frame = load_csv(path)
    rows = frame.loc[frame["construct_id"].eq(construct_id)]
    if rows.empty:
        raise ValueError(f"{construct_id} not found in {path}")
    return rows.iloc[0]


def item_counts(path: Path, construct_id: str) -> dict[str, int]:
    key = load_csv(path)
    key = key.loc[key["construct_id"].eq(construct_id)].copy()
    return {
        "item_count": int(len(key)),
        "development_items": int(key["sample_role"].eq("development").sum()),
        "heldout_items": int(key["sample_role"].eq("heldout").sum()),
        "unique_users": int(key["user_id"].nunique()),
        "source_families": int(key["source_family"].nunique()),
    }


def build_registry() -> pd.DataFrame:
    rows: list[dict] = []
    for spec in CONSTRUCTS:
        dev = summary_row(spec["dev_summary"], spec["construct_id"])
        heldout = summary_row(spec["heldout_summary"], spec["construct_id"])
        counts = item_counts(spec["key_path"], spec["construct_id"])
        rows.append(
            {
                "construct_id": spec["construct_id"],
                "label": spec["label"],
                "source": spec["source"],
                "expected_dimension": spec["expected_dimension"],
                "construct_definition": spec["construct_definition"],
                "high_pole": spec["high_pole"],
                "low_pole": spec["low_pole"],
                "scoring_hint": spec["scoring_hint"],
                "development_decision": dev["decision"],
                "development_min_expected_delta": float(dev["min_expected_delta"]),
                "development_min_source_adjusted_delta": float(dev["min_source_adjusted_delta"]),
                "development_expected_agreement": float(dev["mean_expected_agreement"]),
                "heldout_decision": heldout["decision"],
                "heldout_min_expected_delta": float(heldout["min_expected_delta"]),
                "heldout_min_source_adjusted_delta": float(heldout["min_source_adjusted_delta"]),
                "heldout_expected_agreement": float(heldout["mean_expected_agreement"]),
                "release_status": (
                    "provisional_scale_component"
                    if dev["decision"] == "pass_development_gate" and heldout["decision"] == "pass_heldout_gate"
                    else "not_release_ready"
                ),
                **counts,
            }
        )
    return pd.DataFrame(rows)


def write_report(path: Path, registry: pd.DataFrame) -> None:
    lines = [
        "# SUICA Validated Construct Manual v1",
        "",
        "## Purpose",
        "",
        "This manual records SUICA constructs that passed both development and author-heldout blind-coding gates. It is a provisional measurement manual, not a final clinical or personality assessment instrument.",
        "",
        "## Validated Construct Registry",
        "",
        registry[
            [
                "construct_id",
                "label",
                "expected_dimension",
                "development_min_expected_delta",
                "heldout_min_expected_delta",
                "heldout_expected_agreement",
                "release_status",
            ]
        ].round(3).to_markdown(index=False),
        "",
        "## Construct Cards",
        "",
    ]
    for row in registry.itertuples(index=False):
        lines.extend(
            [
                f"### {row.label} (`{row.construct_id}`)",
                "",
                f"- source: `{row.source}`",
                f"- definition: {row.construct_definition}",
                f"- expected blind-coding dimension: `{row.expected_dimension}`",
                f"- high pole: {row.high_pole}",
                f"- low pole: {row.low_pole}",
                f"- scoring hint: {row.scoring_hint}",
                f"- development gate: `{row.development_decision}`, min delta `{row.development_min_expected_delta:.3f}`, source-adjusted `{row.development_min_source_adjusted_delta:.3f}`, agreement `{row.development_expected_agreement:.3f}`",
                f"- heldout gate: `{row.heldout_decision}`, min delta `{row.heldout_min_expected_delta:.3f}`, source-adjusted `{row.heldout_min_source_adjusted_delta:.3f}`, agreement `{row.heldout_expected_agreement:.3f}`",
                f"- item evidence: `{row.item_count}` items, `{row.unique_users}` users, `{row.source_families}` source families",
                "",
            ]
        )
    lines.extend(
        [
            "## Use Rules",
            "",
            "- Treat these constructs as provisional SUICA scale components.",
            "- Big5/MBTI are external validity anchors only; they are not part of the scoring objective here.",
            "- Do not merge these constructs back into a single broad factor unless a new interaction package passes development and heldout gates.",
            "- Next validation should increase item-bank size and add human coder or model-family reliability, not tune on heldout.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    report_path = Path(args.report_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    registry = build_registry()
    registry.to_csv(out_dir / "validated_construct_registry.csv", index=False)
    (out_dir / "manifest.json").write_text(
        json.dumps({"construct_ids": registry["construct_id"].tolist(), "construct_count": int(len(registry))}, indent=2),
        encoding="utf-8",
    )
    write_report(report_path, registry)
    print(registry[["construct_id", "label", "heldout_decision", "release_status"]].to_string(index=False))
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
