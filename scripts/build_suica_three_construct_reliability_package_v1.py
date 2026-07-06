#!/usr/bin/env python
"""Build a unified reliability package for the validated SUICA constructs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_suica_construct_expansion_readiness_v1 import build_coder_order  # noqa: E402


OUT_DIR = ROOT / "results" / "suica_three_construct_reliability_package_v1"
REPORT_PATH = ROOT / "reports" / "suica_three_construct_reliability_package_v1.md"
EXPANSION_KEY = ROOT / "results" / "suica_construct_expansion_readiness_v1" / "expanded_item_bank_key.csv"
EXPANSION_BLIND = ROOT / "results" / "suica_construct_expansion_readiness_v1" / "expanded_blind_items.csv"
AR_KEY = ROOT / "results" / "suica_adversity_recovery_core_v1" / "adversity_recovery_key.csv"
AR_BLIND = ROOT / "results" / "suica_adversity_recovery_core_v1" / "adversity_recovery_blind_items.csv"

VALIDATED_CONSTRUCTS = [
    "f05_novelty_play_core",
    "f10_directive_action_core",
    "suica_adversity_recovery_core",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build SUICA three-construct reliability package v1.")
    parser.add_argument("--output-dir", default=str(OUT_DIR))
    parser.add_argument("--report-path", default=str(REPORT_PATH))
    parser.add_argument("--seed", type=int, default=8484)
    return parser.parse_args()


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def load_construct_items() -> tuple[pd.DataFrame, pd.DataFrame]:
    exp_key = load_csv(EXPANSION_KEY)
    exp_blind = load_csv(EXPANSION_BLIND)
    ar_key = load_csv(AR_KEY)
    ar_blind = load_csv(AR_BLIND)
    exp_key = exp_key.loc[exp_key["construct_id"].isin(["f05_novelty_play_core", "f10_directive_action_core"])].copy()
    exp_blind = exp_blind.loc[exp_blind["blind_item_id"].isin(exp_key["blind_item_id"])].copy()
    ar_key = ar_key.loc[ar_key["construct_id"].eq("suica_adversity_recovery_core")].copy()
    ar_blind = ar_blind.loc[ar_blind["blind_item_id"].isin(ar_key["blind_item_id"])].copy()
    key = pd.concat([exp_key, ar_key], ignore_index=True, sort=False)
    blind = pd.concat([exp_blind, ar_blind], ignore_index=True, sort=False)
    duplicate_ids = key["blind_item_id"].duplicated().sum()
    if duplicate_ids:
        raise ValueError(f"duplicate blind_item_id count={duplicate_ids}")
    return blind, key


def package_summary(key: pd.DataFrame) -> pd.DataFrame:
    return (
        key.groupby(["construct_id", "sample_role", "source_family", "cell"], as_index=False)
        .agg(
            items=("blind_item_id", "count"),
            unique_users=("user_id", "nunique"),
            conditions=("condition", "nunique"),
        )
        .sort_values(["construct_id", "sample_role", "source_family", "cell"])
    )


def readiness_summary(key: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for construct_id, group in key.groupby("construct_id", sort=True):
        for role, role_rows in group.groupby("sample_role", sort=True):
            by_cell = role_rows.groupby(["source_family", "cell"]).size()
            rows.append(
                {
                    "construct_id": construct_id,
                    "sample_role": role,
                    "items": int(len(role_rows)),
                    "unique_users": int(role_rows["user_id"].nunique()),
                    "source_families": int(role_rows["source_family"].nunique()),
                    "cells": int(role_rows["cell"].nunique()),
                    "min_items_per_source_cell": int(by_cell.min()) if not by_cell.empty else 0,
                    "ready_for_reliability_coding": bool(
                        len(role_rows) >= 24
                        and role_rows["source_family"].nunique() >= 2
                        and role_rows["cell"].nunique() >= 2
                        and (int(by_cell.min()) if not by_cell.empty else 0) >= 6
                    ),
                }
            )
    return pd.DataFrame(rows)


def split_role_files(blind: pd.DataFrame, key: pd.DataFrame, out_dir: Path, *, seed: int) -> None:
    blind_with_role = blind.merge(key[["blind_item_id", "sample_role"]], on="blind_item_id", how="left", validate="one_to_one")
    for role in ["development", "heldout"]:
        role_items = blind_with_role.loc[blind_with_role["sample_role"].eq(role)].drop(columns=["sample_role"]).reset_index(drop=True)
        role_items.to_csv(out_dir / f"{role}_blind_items.csv", index=False)
        build_coder_order(role_items, coder_id=f"{role}_coder_A", seed=seed + 11).to_csv(out_dir / f"{role}_coder_A_items.csv", index=False)
        build_coder_order(role_items, coder_id=f"{role}_coder_B", seed=seed + 12).to_csv(out_dir / f"{role}_coder_B_items.csv", index=False)


def write_report(path: Path, *, summary: pd.DataFrame, readiness: pd.DataFrame, key: pd.DataFrame) -> None:
    lines = [
        "# SUICA Three-Construct Reliability Package v1",
        "",
        "## Purpose",
        "",
        "Build a unified blind-coding package for the three SUICA constructs that passed development and heldout gates.",
        "",
        "## Package Scope",
        "",
        f"- constructs: `{', '.join(VALIDATED_CONSTRUCTS)}`",
        f"- total items: `{len(key)}`",
        f"- development items: `{key['sample_role'].eq('development').sum()}`",
        f"- heldout items: `{key['sample_role'].eq('heldout').sum()}`",
        "",
        "## Readiness Summary",
        "",
        readiness.to_markdown(index=False),
        "",
        "## Source/Cell Balance",
        "",
        summary.to_markdown(index=False),
        "",
        "## Next Use",
        "",
        "- Use development items for larger reliability coding or human coder calibration.",
        "- Use heldout items only after coder/rubric rules are fixed.",
        "- Do not use Big5/MBTI labels in this package; they remain later external validity anchors.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    blind, key = load_construct_items()
    summary = package_summary(key)
    readiness = readiness_summary(key)
    blind.to_csv(out_dir / "three_construct_blind_items.csv", index=False)
    key.to_csv(out_dir / "three_construct_key.csv", index=False)
    summary.to_csv(out_dir / "source_cell_summary.csv", index=False)
    readiness.to_csv(out_dir / "readiness_summary.csv", index=False)
    build_coder_order(blind, coder_id="coder_A", seed=args.seed + 1).to_csv(out_dir / "coder_A_items.csv", index=False)
    build_coder_order(blind, coder_id="coder_B", seed=args.seed + 2).to_csv(out_dir / "coder_B_items.csv", index=False)
    split_role_files(blind, key, out_dir, seed=args.seed)
    (out_dir / "manifest.json").write_text(
        json.dumps(
            {
                "constructs": VALIDATED_CONSTRUCTS,
                "total_items": int(len(key)),
                "development_items": int(key["sample_role"].eq("development").sum()),
                "heldout_items": int(key["sample_role"].eq("heldout").sum()),
                "seed": int(args.seed),
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    write_report(Path(args.report_path), summary=summary, readiness=readiness, key=key)
    print(readiness.to_string(index=False))
    print(f"Report: {Path(args.report_path)}")


if __name__ == "__main__":
    main()
