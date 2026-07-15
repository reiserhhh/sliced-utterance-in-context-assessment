#!/usr/bin/env python
"""Create a privacy-preserving directory and reference map for MEPS + AI data.

Only the participant-code column of explicitly registered deidentified tables
is read to verify linkage. Questionnaire scale values, raw Qualtrics exports,
free-chat coding files, encrypted archives, keys, and application bundles are
not imported. The output is a routing document, not a validation analysis.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.meps_layout import directory_registry, reference_registry, resolve_meps_experiment_layout  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/meps_ai_conv_layout_audit")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/MEPS_AI_CONV_DATA_LAYOUT.md")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    layout = resolve_meps_experiment_layout(args.input_root)
    directories = directory_registry(layout)
    references = reference_registry(layout)
    participant_count = sum(
        1 for path in layout.text_export_root.iterdir()
        if path.is_dir() and not path.name.startswith((".", "._"))
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    directories.to_csv(args.output_dir / "directory_registry.csv", index=False)
    references.to_csv(args.output_dir / "reference_registry.csv", index=False)
    manifest = layout.public_manifest() | {"text_export_participants": participant_count}
    (args.output_dir / "layout_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(f"""# MEPS + AI Conversation: Data Layout and Reference Map

## Authoritative route

`{manifest['text_export_relative_path']}/` is the sole SUICA text source for
the fixed-condition pilot. It contains `{participant_count}` participant export
directories. The importer resolves this route automatically when given the
complete experiment bundle.

## Directory map

{directories.to_markdown(index=False)}

## Registered but withheld references

{references.to_markdown(index=False, floatfmt='.3f')}

## Binding use rules

1. Use only `decrypted_output/` user-authored text for the current SUICA
   fixed-condition verification.
2. Treat Research 2 pre/post questionnaires as registered, linked, **withheld**
   data. They are not training labels and are not external-validity outcomes in
   this phase.
3. Do not read `survey_rawdata/`: raw Qualtrics exports can contain direct
   identifiers. Do not use `coding/` as a duplicate text path.
4. Treat Research 1 as a different study. Its partial overlap cannot enter any
   SUICA analysis without a separately declared longitudinal design and merge
   audit.

This document records data routing only. It makes no psychometric or causal
claim and does not serialize participant IDs, text, or questionnaire values.
""", encoding="utf-8")
    print(f"text_export_participants={participant_count}")
    print(f"report={args.report}")
    print(f"output_dir={args.output_dir}")


if __name__ == "__main__":
    main()
