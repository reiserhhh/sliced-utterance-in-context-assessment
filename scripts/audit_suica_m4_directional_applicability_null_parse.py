#!/usr/bin/env python3
"""Audit the literal ``null`` CSV parsing defect in directional analysis.

The sealed analyzer used pandas' default NA vocabulary, which converts the
world-type string ``null`` to missing data. This wrapper changes that lexical
parse only, then invokes the unchanged sealed analyzer and annotates its
outputs. No model, feature, threshold, cell, or outcome is changed.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import analyze_suica_m4_directional_applicability as sealed  # noqa: E402


def _argument(name: str) -> Path:
    try:
        return Path(sys.argv[sys.argv.index(name) + 1])
    except (ValueError, IndexError) as error:
        raise ValueError(f"{name} is required for audited output") from error


def main() -> None:
    original = pd.read_csv

    def read_csv_without_default_na(*args, **kwargs):
        kwargs.setdefault("keep_default_na", False)
        return original(*args, **kwargs)

    sealed.pd.read_csv = read_csv_without_default_na
    sealed.main()

    output = _argument("--output-directory")
    report = _argument("--report-path")
    if not output.is_absolute():
        output = ROOT / output
    if not report.is_absolute():
        report = ROOT / report
    decision_path = output / "decision.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["audit_status"] = "POST_SEAL_LEXICAL_NULL_PARSE_CORRECTION"
    decision["audit_change"] = (
        "pandas.read_csv keep_default_na=False; no model, feature, threshold, "
        "cell, outcome, or gate changed"
    )
    decision["raw_parser_decision"] = "M4_C35_DIRECTIONAL_INTEGRITY_STOP"
    decision_path.write_text(
        json.dumps(decision, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    body = report.read_text(encoding="utf-8")
    note = (
        "> **Audit correction.** The sealed analyzer parsed the literal world "
        "type `null` as pandas NA and therefore reported zero null cells. This "
        "report changes only CSV parsing to `keep_default_na=False`; all frozen "
        "models, features, thresholds, cells, outcomes, and gates are unchanged. "
        "The raw parser-stop report is preserved separately.\n\n"
    )
    report.write_text(note + body, encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
