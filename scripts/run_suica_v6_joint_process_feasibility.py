#!/usr/bin/env python
"""Run metadata-only J0 feasibility for the natural Joint-Process stage.

This script does not fit embeddings, factor axes, personality predictions, or
labels. It tests only whether enough naturally selected PANDORA events and
ordered transitions exist after a synthetic support threshold is frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.joint_process import (  # noqa: E402
    author_support_summary,
    candidate_support_table,
    metadata_events,
)
from suica_core.suica import PERSONALITY_LEAK_RE  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet")
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_joint_process_stage_j1.json")
    parser.add_argument("--calibration", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_joint_process_stage_j1")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_JOINT_PROCESS_STAGE_J1_FEASIBILITY.md")
    return parser.parse_args()


def sha256(path: Path) -> str:
    """Hash local raw source in chunks for provenance."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1_048_576):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError("Pass the local, gitignored Tier-U PANDORA parquet with --input")
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    calibration_path = args.calibration or ROOT / cfg["j0"]["calibration_artifact"]
    if not calibration_path.exists():
        raise FileNotFoundError("Run synthetic calibration before J0 feasibility: " + str(calibration_path))
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    selected = calibration.get("selected_support")
    if not selected:
        raise RuntimeError("Synthetic calibration did not license any support threshold; J0 must refuse")
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    body = comments["body"].fillna("").astype(str)
    leak_mask = body.map(lambda value: bool(PERSONALITY_LEAK_RE.search(value)))
    comments = comments.loc[~leak_mask].copy()
    events = metadata_events(comments, min_characters=int(cfg["j0"]["minimum_body_characters"]))
    summary = author_support_summary(events)
    author_table, cohort_table, decision = candidate_support_table(
        summary,
        min_events=int(selected["min_events"]),
        min_transitions=int(selected["min_transitions"]),
        min_endpoint_authors=int(cfg["j0"]["minimum_endpoint_authors"]),
        namespace=str(cfg["namespace"]),
        replicate_views=int(cfg["j0"]["technical_replication"]["views"]),
        replication_block_size=int(cfg["j0"]["technical_replication"]["nonoverlap_block_size"]),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    # Never persist source IDs: author-level table is only kept locally and is
    # gitignored; report artifacts contain cohort aggregates only.
    author_table.to_csv(args.output_dir / "author_support_private.csv", index=False)
    cohort_table.to_csv(args.output_dir / "cohort_support_summary.csv", index=False)
    result = {
        "run_name": cfg["run_name"],
        "input_sha256": sha256(args.input),
        "n_source_comments": int(len(comments) + int(leak_mask.sum())),
        "n_comments_excluded_by_personality_leakage_guard": int(leak_mask.sum()),
        "n_metadata_events": int(len(events)),
        "calibration": calibration,
        "cohort_summary": cohort_table.to_dict(orient="records"),
        "decision": decision,
        "raw_text_persisted": False,
        "external_labels_read": False,
        "embedding_endpoint_fit": False,
    }
    (args.output_dir / "joint_process_feasibility.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(f"""# SUICA V6 Joint-Process J1: J0 Feasibility

## Frozen question

Does the local raw PANDORA source supply enough naturally selected events and
ordered transitions to estimate the **joint selection-expression-transition**
object? This is not a matched-topic test. `subreddit` remains an observed
selection component rather than a nuisance to remove.

## Provenance and data boundary

- source SHA-256: `{result['input_sha256']}`
- source comments: `{result['n_source_comments']}`
- excluded by explicit personality-report leakage guard: `{result['n_comments_excluded_by_personality_leakage_guard']}`
- retained metadata events: `{len(events)}`
- threshold selected by synthetic calibration: `{selected}`
- technical replication: `{decision['technical_replication_views']}` disjoint
  views made of consecutive `{decision['technical_replication_block_size']}`-event blocks
- total support required for those disjoint views: `{decision['minimum_total_events_for_disjoint_views']}`
  events and `{decision['minimum_total_transitions_for_disjoint_views']}` within-block transitions
- external labels read: `False`
- embeddings/factors/text endpoints fit: `False`
- raw text persisted: `False`

## Cohort support

{cohort_table.round(3).to_markdown(index=False)}

## Decision

`{decision['decision']}` — {decision['reason']}.

The raw PANDORA schema contains no independently observed global expression
opportunity variable. Therefore this gate licenses only a joint natural-process
object. It does **not** license separate conditional-expression, causal,
personality, clinical, or cross-language claims. Text length is recorded only
for later sensitivity analysis and is not residualized from the primary object.

## Next action

If `PROCEED_J1`, construct frozen joint-process objects in an author-disjoint
discovery/calibration/confirmation design. If `REFUSE_J1_SUPPORT`, do not lower
the calibration threshold or substitute artificial fixed-topic windows.
""", encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
