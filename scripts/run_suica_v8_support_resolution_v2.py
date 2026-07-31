#!/usr/bin/env python3
"""Run the scale-free D1-discovery/D2-confirmation resolution frontier."""
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
    load_x_events,
)
from suica_core.v8_realtext_relation_field import (  # noqa: E402
    FAMILY_NAMES,
    RealTextRelationSpec,
    build_feature_panel,
)
from suica_core.v8_support_resolution_v2 import (  # noqa: E402
    ScaleFreeResolutionSpec,
    evaluate_scale_free_resolution,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_support_resolution_v2.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_support_resolution_v2" / "full_20260808"
DEFAULT_REPORT = ROOT / "reports" / "V8_SUPPORT_RESOLUTION_SCALE_FREE.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _report(
    decision: dict[str, Any],
    schemas: list[dict[str, Any]],
    summaries: pd.DataFrame,
    frontier: pd.DataFrame,
    boundary: str,
) -> str:
    return (
        "# V8 Scale-Free Replicated-Density Resolution Region\n\n"
        f"Status: `{decision['status']}`\n\n"
        "This supersedes the tau-indexed development frontier for claims. "
        "It computes the complete capacity path k=1,...,d-1 and a frozen "
        "sharpness grid q. D1 discovers the region; D2 confirms it once. "
        "Bootstrap bands and Haar nulls are simultaneous over the complete "
        "capacity-sharpness path.\n\n"
        "## Data roles\n\n"
        f"{pd.DataFrame(schemas).to_markdown(index=False)}\n\n"
        "## Corpus/family summary\n\n"
        f"{summaries.to_markdown(index=False)}\n\n"
        "## Capacity frontier\n\n"
        f"{frontier.to_markdown(index=False)}\n\n"
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
    spec = ScaleFreeResolutionSpec(
        **{
            **config["spec"],
            "sharpness": tuple(config["spec"]["sharpness"]),
        }
    )
    events_per_author = int(config["matched_events_per_author"])
    for corpus in ("pandora", "x_market"):
        base["data"][corpus]["minimum_events"] = events_per_author
        base["data"][corpus]["maximum_events"] = events_per_author
    base["data"]["essays"]["chunks"] = events_per_author
    if args.quick:
        feature_spec = replace(
            feature_spec,
            transition_null_draws=min(4, feature_spec.transition_null_draws),
        )
        spec = replace(
            spec,
            sharpness=(0.25, 0.5, 1.0),
            bootstrap_draws=19,
            rotation_draws=19,
            minimum_d0_half_authors=12,
            minimum_confirmation_authors=20,
        )
        for corpus in ("pandora", "x_market"):
            base["data"][corpus]["maximum_authors_per_context"] = min(
                64,
                int(base["data"][corpus]["maximum_authors_per_context"]),
            )
        base["data"]["essays"]["maximum_authors"] = min(
            256,
            int(base["data"]["essays"]["maximum_authors"]),
        )

    loaders = {
        "pandora": load_pandora_events,
        "essays": load_essays_events,
        "x_market": load_x_events,
    }
    panels = {}
    schemas = []
    for corpus, loader in loaders.items():
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

    cell_frames = []
    frontier_frames = []
    summaries = []
    for corpus, panel in panels.items():
        for family in FAMILY_NAMES:
            result = evaluate_scale_free_resolution(
                corpus,
                panel,
                family,
                spec=spec,
            )
            summary = {
                "corpus": corpus,
                "family": family,
                **{
                    key: value
                    for key, value in result.items()
                    if key not in {"cells", "frontier"}
                },
            }
            summaries.append(summary)
            if not result["cells"].empty:
                cell_frames.append(result["cells"])
            if not result["frontier"].empty:
                frontier_frames.append(result["frontier"])
    cells = pd.concat(cell_frames, ignore_index=True) if cell_frames else pd.DataFrame()
    frontier = (
        pd.concat(frontier_frames, ignore_index=True)
        if frontier_frames
        else pd.DataFrame()
    )
    summary_frame = pd.DataFrame(summaries)
    confirmed = summary_frame["status"].eq(
        "SCALE_FREE_RESOLUTION_REGION_CONFIRMED"
    )
    underpowered = summary_frame["status"].str.contains("UNDERPOWERED")
    if confirmed.all():
        status = "ALL_SCALE_FREE_RESOLUTION_REGIONS_CONFIRMED"
    elif confirmed.any():
        status = "SCALE_FREE_RESOLUTION_PARTIAL"
    elif underpowered.all():
        status = "SCALE_FREE_RESOLUTION_SAMPLE_UNDERPOWERED"
    else:
        status = "SCALE_FREE_RESOLUTION_NOT_CONFIRMED"
    decision = {
        "status": status,
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "confirmed_corpus_families": summary_frame.loc[
            confirmed,
            ["corpus", "family", "confirmed_cell_count"],
        ].to_dict(orient="records"),
        "underpowered_corpus_families": summary_frame.loc[
            underpowered,
            ["corpus", "family", "status"],
        ].to_dict(orient="records"),
        "claim_boundary": config["claim_boundary"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "resolution_cells.csv", index=False)
    frontier.to_csv(args.output_dir / "capacity_frontier.csv", index=False)
    summary_frame.to_csv(args.output_dir / "corpus_family_summary.csv", index=False)
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
        frontier,
        config["claim_boundary"],
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
