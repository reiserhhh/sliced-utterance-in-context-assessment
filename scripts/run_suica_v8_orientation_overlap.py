#!/usr/bin/env python3
"""Run the shared-gauge spectrum-matched orientation-overlap audit."""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_realtext_relation_field import (  # noqa: E402
    load_essays_events,
    load_pandora_events,
)
from suica_core.v8_orientation_overlap import (  # noqa: E402
    OrientationOverlapSpec,
    add_max_haar_adjustment,
    evaluate_orientation_family,
)
from suica_core.v8_realtext_relation_field import (  # noqa: E402
    FAMILY_NAMES,
    RealTextRelationSpec,
    build_feature_panel,
)
from suica_core.v8_support_containment import _split_raw  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_orientation_overlap.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_orientation_overlap" / "audit_20260810"
DEFAULT_REPORT = ROOT / "reports" / "V8_ORIENTATION_OVERLAP_AUDIT.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _report(
    decision: dict[str, Any],
    schemas: list[dict[str, Any]],
    family_summary: pd.DataFrame,
    primary: pd.DataFrame,
    boundary: str,
) -> str:
    return (
        "# V8 Spectrum-Matched Orientation-Overlap Audit\n\n"
        f"Status: `{decision['status']}`\n\n"
        "This exploratory audit separates spectral concentration from "
        "orientation. It subtracts the isotropic floor, freezes an identifiable "
        "D0 rank, matches PANDORA/Essays spectra by geometric-mean weights, "
        "and compares orientation with spectrum-preserving Haar rotations.\n\n"
        "## Data roles\n\n"
        f"{pd.DataFrame(schemas).to_markdown(index=False)}\n\n"
        "## D0 identification\n\n"
        f"{family_summary.to_markdown(index=False)}\n\n"
        "## Primary matched-spectrum HS cells\n\n"
        f"{primary.to_markdown(index=False)}\n\n"
        "Root fidelity is a secondary view of distributed weak overlap. "
        "Principal-angle affinity and exact-intersection rank are diagnostics. "
        "Parallel sum is not used as an approximate-overlap test because noisy "
        "low-rank subspaces generically have a zero exact intersection.\n\n"
        "## Claim boundary\n\n"
        f"{boundary}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    config = _json(args.config)
    base = _json(_resolve(config["base_config"]))
    feature_spec = RealTextRelationSpec(**base["spec"])
    spec = OrientationOverlapSpec(**config["spec"])
    events_per_author = int(config["matched_events_per_author"])
    base["data"]["pandora"]["minimum_events"] = events_per_author
    base["data"]["pandora"]["maximum_events"] = events_per_author
    base["data"]["essays"]["chunks"] = events_per_author
    if args.quick:
        feature_spec = replace(
            feature_spec,
            transition_null_draws=min(4, feature_spec.transition_null_draws),
        )
        spec = replace(
            spec,
            calibration_draws=19,
            bootstrap_draws=19,
            rotation_draws=19,
        )
        base["data"]["pandora"]["maximum_authors_per_context"] = min(
            96,
            int(base["data"]["pandora"]["maximum_authors_per_context"]),
        )
        base["data"]["essays"]["maximum_authors"] = min(
            320,
            int(base["data"]["essays"]["maximum_authors"]),
        )

    panels = {}
    schemas = []
    for corpus, loader in (
        ("pandora", load_pandora_events),
        ("essays", load_essays_events),
    ):
        events, schema = loader(base["data"][corpus])
        panel = build_feature_panel(
            events,
            corpus=corpus,
            context_role=schema["context_role"],
            replicate_type=schema["replicate_type"],
            spec=feature_spec,
        )
        schema["split_counts"] = panel.metadata["split"].value_counts().to_dict()
        schemas.append(schema)
        panels[corpus] = panel

    family_results = []
    for family in FAMILY_NAMES:
        raw = {
            corpus: {
                split: _split_raw(panel, family, split)
                for split in ("D0", "D1", "D2")
            }
            for corpus, panel in panels.items()
        }
        family_results.append(
            evaluate_orientation_family(
                family,
                raw["pandora"],
                raw["essays"],
                spec=spec,
            )
        )
    cells = add_max_haar_adjustment(family_results)
    summaries = []
    d0_rows = []
    rank_sensitivity_frames = []
    for result in family_results:
        summaries.append(
            {
                "family": result["family"],
                "status": result["status"],
                "epsilon": result.get("epsilon"),
                "rank": result.get("rank"),
                "effective_rank_template": result.get("effective_rank_template"),
            }
        )
        for row in result.get("d0_internal", []):
            d0_rows.append({"family": result["family"], **row})
        if not result.get("rank_sensitivity", pd.DataFrame()).empty:
            rank_sensitivity_frames.append(result["rank_sensitivity"])
    summary_frame = pd.DataFrame(summaries)
    d0_frame = pd.DataFrame(d0_rows)
    rank_sensitivity = (
        pd.concat(rank_sensitivity_frames, ignore_index=True)
        if rank_sensitivity_frames
        else pd.DataFrame()
    )
    primary = cells.loc[
        cells["arm"].eq("matched_spectrum") & cells["metric"].eq("hs")
    ].copy()
    primary["detected"] = (
        primary["max_haar_p"].le(0.05)
        & primary["bootstrap_delta_low"].gt(0)
    )
    d0_ready = summary_frame["status"].eq("ORIENTATION_AUDIT_READY").all()
    d1_detected = primary.loc[primary["split"].eq("D1"), "detected"].all()
    d2_replayed = primary.loc[primary["split"].eq("D2"), "detected"].all()
    persistent_families = []
    for family, group in primary.groupby("family"):
        by_split = group.set_index("split")["detected"]
        if bool(by_split.get("D1", False) and by_split.get("D2", False)):
            persistent_families.append(str(family))
    if not d0_ready:
        status = "ORIENTATION_UNDERRESOLVED"
    elif len(persistent_families) == len(FAMILY_NAMES):
        status = "EXPLORATORY_MATCHED_SPECTRUM_ORIENTATION_OVERLAP"
    elif persistent_families:
        status = "EXPLORATORY_ORIENTATION_OVERLAP_PARTIAL"
    else:
        status = "ORIENTATION_OVERLAP_NOT_DETECTED"
    decision = {
        "status": status,
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "d0_ready": bool(d0_ready),
        "d1_all_families_detected": bool(d1_detected),
        "d2_all_families_replayed": bool(d2_replayed),
        "persistent_families": persistent_families,
        "claim_boundary": config["claim_boundary"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "orientation_cells.csv", index=False)
    summary_frame.to_csv(args.output_dir / "family_summary.csv", index=False)
    d0_frame.to_csv(args.output_dir / "d0_internal_orientation.csv", index=False)
    rank_sensitivity.to_csv(
        args.output_dir / "rank_sensitivity.csv",
        index=False,
    )
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = _report(
        decision,
        schemas,
        summary_frame,
        primary,
        config["claim_boundary"],
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
