#!/usr/bin/env python3
"""Validate whether a dataset can estimate SUICA V7 free q and fixed B objects."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_validation import validate_fixed_free_observations  # noqa: E402


def _read(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        return pd.read_json(path, lines=True)
    return pd.read_csv(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary, q_table, b_table = validate_fixed_free_observations(_read(args.input))
    (args.output_dir / "fixed_free_validation.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    q_table.to_csv(args.output_dir / "free_choice_q_profile.csv", index=False)
    b_table.to_csv(args.output_dir / "fixed_response_design.csv", index=False)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "FIXED_FREE_DESIGN_READY_FOR_FUTURE_ESTIMATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
