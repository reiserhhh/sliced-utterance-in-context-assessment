#!/usr/bin/env python3
"""Run the V8 corpus-local replicated-support resolution frontier."""
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
from suica_core.v8_support_resolution import (  # noqa: E402
    SupportResolutionSpec,
    classify_frontier,
    evaluate_local_resolution,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_support_resolution.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_support_resolution" / "frontier_20260807"
DEFAULT_REPORT = ROOT / "reports" / "V8_SUPPORT_RESOLUTION_FRONTIER.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _report(
    decision: dict[str, Any],
    schemas: list[dict[str, Any]],
    frontier: pd.DataFrame,
    classifications: pd.DataFrame,
    boundary: str,
) -> str:
    return (
        "# V8 Corpus-Local Support Resolution Frontier\n\n"
        f"Status: `{decision['status']}`\n\n"
        "This experiment separates replicated support existence from "
        "capacity-limited compressibility. D0-fit filters are admitted only "
        "when they beat isotropic support in a disjoint D0 calibration half; "
        "D1 and D2 then test the full admitted tau set at each capacity.\n\n"
        "## Data roles\n\n"
        f"{pd.DataFrame(schemas).to_markdown(index=False)}\n\n"
        "## Resolution frontier\n\n"
        f"{frontier.to_markdown(index=False)}\n\n"
        "## Corpus/family decisions\n\n"
        f"{classifications.to_markdown(index=False)}\n\n"
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
    spec = SupportResolutionSpec(
        **{
            **config["spec"],
            "capacities": tuple(config["spec"]["capacities"]),
            "tau_multipliers": tuple(config["spec"]["tau_multipliers"]),
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
            capacities=(2, 4, 8, 16, 24, 32),
            tau_multipliers=(0.5, 1.0, 2.0),
            bootstrap_draws=19,
            rotation_draws=19,
            minimum_fit_authors=12,
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

    cells = []
    frontiers = []
    for corpus, panel in panels.items():
        for family in FAMILY_NAMES:
            result = evaluate_local_resolution(
                corpus,
                panel,
                family,
                spec=spec,
            )
            cells.extend(result["cells"])
            frontiers.extend(result["frontier"])
    cells_frame = pd.DataFrame(cells)
    frontier = pd.DataFrame(frontiers)
    # Each p-value already uses a synchronized max-capacity rotation null
    # within its corpus/family/split family.
    frontier["rotation_q"] = frontier["rotation_p"]
    decisions = []
    eligible = frontier.loc[frontier["split"].isin(["D1", "D2"])]
    for (corpus, family), group in eligible.groupby(
        ["corpus", "family"],
        sort=True,
    ):
        decisions.append(
            {
                "corpus": corpus,
                "family": family,
                **classify_frontier(group),
            }
        )
    classifications = pd.DataFrame(decisions)
    if classifications["decision"].eq("REPLICATED_CAPACITY_FRONTIER").all():
        status = "ALL_CORPORA_CAPACITY_FRONTIERS_RESOLVED"
    elif classifications["decision"].eq("REPLICATED_CAPACITY_FRONTIER").any():
        status = "CAPACITY_FRONTIER_PARTIAL"
    else:
        status = "DISTRIBUTED_SUPPORT_NONCOMPRESSIBLE_AT_TESTED_RESOLUTIONS"
    decision = {
        "status": status,
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "resolved_corpus_families": classifications.loc[
            classifications["decision"].eq("REPLICATED_CAPACITY_FRONTIER"),
            ["corpus", "family", "confirmed_capacities"],
        ].to_dict(orient="records"),
        "claim_boundary": config["claim_boundary"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells_frame.to_csv(args.output_dir / "resolution_cells.csv", index=False)
    frontier.to_csv(args.output_dir / "capacity_frontier.csv", index=False)
    classifications.to_csv(args.output_dir / "frontier_decisions.csv", index=False)
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
        frontier,
        classifications,
        config["claim_boundary"],
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
