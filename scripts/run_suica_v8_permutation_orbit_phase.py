#!/usr/bin/env python3
"""Run V8 event-set susceptibility and observed permutation-phase analysis."""
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
from suica_core.v8_order_statistic_null import (  # noqa: E402
    OrderStatisticNullSpec,
    build_exact_permutation_panel,
    evaluate_statistic_level_order_null,
)
from suica_core.v8_permutation_orbit_phase import (  # noqa: E402
    OrbitPhaseSpec,
    build_orbit_phase_panel,
    evaluate_set_geometry_overlap,
    fit_shared_orbit_scale,
)
from suica_core.v8_realtext_relation_field import RealTextRelationSpec  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_permutation_orbit_phase.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_permutation_orbit_phase" / "audit_20260813"
DEFAULT_REPORT = ROOT / "reports" / "V8_PERMUTATION_ORBIT_PHASE.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


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
    orbit_spec = OrbitPhaseSpec(**config["orbit_spec"])
    null_spec = OrderStatisticNullSpec(**config["order_null_spec"])
    events_per_author = int(config["matched_events_per_author"])
    base["data"]["pandora"]["minimum_events"] = events_per_author
    base["data"]["pandora"]["maximum_events"] = events_per_author
    base["data"]["essays"]["chunks"] = events_per_author
    if args.quick:
        orbit_spec = replace(
            orbit_spec,
            rank=2,
            bootstrap_draws=19,
            rotation_draws=19,
        )
        null_spec = replace(
            null_spec,
            calibration_draws=19,
            outer_draws=99,
            rank=2,
        )
        base["data"]["pandora"]["maximum_authors_per_context"] = min(
            96,
            int(base["data"]["pandora"]["maximum_authors_per_context"]),
        )
        base["data"]["essays"]["maximum_authors"] = min(
            320,
            int(base["data"]["essays"]["maximum_authors"]),
        )

    exact = {}
    schemas = []
    for corpus, loader in (
        ("pandora", load_pandora_events),
        ("essays", load_essays_events),
    ):
        events, schema = loader(base["data"][corpus])
        panel = build_exact_permutation_panel(
            events,
            corpus=corpus,
            feature_spec=feature_spec,
        )
        exact[corpus] = panel
        schema["split_counts"] = panel.metadata["split"].value_counts().to_dict()
        schema["inner_permutations"] = 24
        schemas.append(schema)

    scale = fit_shared_orbit_scale(
        exact["pandora"],
        exact["essays"],
        salt=f"v8-orbit-phase-{orbit_spec.seed}",
    )
    panels = {
        corpus: build_orbit_phase_panel(
            panel,
            scale=scale,
            ridge_ratio=orbit_spec.ridge_ratio,
        )
        for corpus, panel in exact.items()
    }
    set_result = evaluate_set_geometry_overlap(
        panels["pandora"].standardized,
        panels["essays"].standardized,
        spec=orbit_spec,
    )
    phase_result = evaluate_statistic_level_order_null(
        panels["pandora"].phase,
        panels["essays"].phase,
        spec=null_spec,
    )
    if (
        set_result["status"] == "CROSS_CORPUS_SET_GEOMETRY_OVERLAP_DETECTED"
        and phase_result["status"] == "STATISTIC_LEVEL_ORDER_EXCESS_DETECTED"
    ):
        status = "SET_AND_PHASE_GEOMETRY_DETECTED"
    elif set_result["status"] == "CROSS_CORPUS_SET_GEOMETRY_OVERLAP_DETECTED":
        status = "SET_GEOMETRY_ONLY__PHASE_NOT_DETECTED"
    elif phase_result["status"] == "STATISTIC_LEVEL_ORDER_EXCESS_DETECTED":
        status = "PHASE_ONLY_DETECTED"
    else:
        status = "SET_AND_PHASE_GEOMETRY_NOT_DETECTED"

    args.output_dir.mkdir(parents=True, exist_ok=True)
    set_result["cells"].to_csv(
        args.output_dir / "set_geometry_cells.csv",
        index=False,
    )
    phase_result["cells"].to_csv(
        args.output_dir / "phase_order_null_cells.csv",
        index=False,
    )
    phase_result["null_scores"].to_csv(
        args.output_dir / "phase_order_null_scores.csv",
        index=False,
    )
    diagnostics = []
    for corpus, panel in panels.items():
        values = panel.diagnostics.copy()
        values["corpus"] = corpus
        diagnostics.append(values)
    diagnostic_frame = pd.concat(diagnostics, ignore_index=True)
    diagnostic_frame.to_csv(
        args.output_dir / "orbit_diagnostics.csv",
        index=False,
    )
    (args.output_dir / "shared_scale.json").write_text(
        json.dumps(scale.tolist()) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    decision = {
        "status": status,
        "set_status": set_result["status"],
        "phase_status": phase_result["status"],
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "ridge_ratio": orbit_spec.ridge_ratio,
        "rank": orbit_spec.rank,
        "claim_boundary": config["claim_boundary"],
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = (
        "# V8 Permutation-Orbit Set/Phase Decomposition\n\n"
        f"Status: `{status}`\n\n"
        "The set arm measures the geometry generated by all 24 orderings of "
        "each fixed four-event multiset. The phase arm applies a shared D0 "
        "feature gauge and regularized within-orbit whitening before testing "
        "the observed order against the complete statistic-level null.\n\n"
        "## Event-set susceptibility geometry\n\n"
        f"{set_result['cells'].to_markdown(index=False)}\n\n"
        "## Observed permutation phase\n\n"
        f"{phase_result['cells'].to_markdown(index=False)}\n\n"
        "## Claim boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
