#!/usr/bin/env python3
"""Run the V8 natural event-set composition knockout."""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_realtext_relation_field import (  # noqa: E402
    load_essays_events,
    load_pandora_events,
)
from suica_core.v8_event_set_composition_knockout import (  # noqa: E402
    CompositionKnockoutSpec,
    build_event_tensor,
    evaluate_composition_knockout,
)
from suica_core.v8_order_statistic_null import (  # noqa: E402
    build_exact_permutation_panel,
)
from suica_core.v8_permutation_orbit_phase import (  # noqa: E402
    fit_shared_orbit_scale,
)
from suica_core.v8_realtext_relation_field import RealTextRelationSpec  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_event_set_composition_knockout.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_event_set_composition_knockout"
    / "audit_20260815"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_EVENT_SET_COMPOSITION_KNOCKOUT.md"


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
    orbit_config = _json(_resolve(config["orbit_config"]))
    feature_spec = RealTextRelationSpec(**base["spec"])
    spec = CompositionKnockoutSpec(**config["spec"])
    if args.quick:
        spec = replace(spec, draws=99, rank=2)
        base["data"]["pandora"]["maximum_authors_per_context"] = min(
            48,
            int(base["data"]["pandora"]["maximum_authors_per_context"]),
        )
        base["data"]["essays"]["maximum_authors"] = min(
            160,
            int(base["data"]["essays"]["maximum_authors"]),
        )
    events_per_author = int(config["matched_events_per_author"])
    base["data"]["pandora"]["minimum_events"] = events_per_author
    base["data"]["pandora"]["maximum_events"] = events_per_author
    base["data"]["essays"]["chunks"] = events_per_author

    events = {}
    tensors = {}
    exact = {}
    schemas = []
    for corpus, loader in (
        ("pandora", load_pandora_events),
        ("essays", load_essays_events),
    ):
        event_rows, schema = loader(base["data"][corpus])
        events[corpus] = event_rows
        tensors[corpus] = build_event_tensor(
            event_rows,
            corpus=corpus,
            feature_spec=feature_spec,
        )
        exact[corpus] = build_exact_permutation_panel(
            event_rows,
            corpus=corpus,
            feature_spec=feature_spec,
        )
        schemas.append(schema)

    k_scale = fit_shared_orbit_scale(
        exact["pandora"],
        exact["essays"],
        salt=f"v8-orbit-phase-{spec.reference_orbit_seed}",
    )
    result = evaluate_composition_knockout(
        tensors["pandora"],
        tensors["essays"],
        feature_spec=feature_spec,
        feature_scale=k_scale,
        spec=spec,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result["cells"].to_csv(args.output_dir / "composition_cells.csv", index=False)
    result["null_scores"].to_csv(
        args.output_dir / "composition_null_scores.csv",
        index=False,
    )
    result["diagnostics"].to_csv(
        args.output_dir / "reallocation_diagnostics.csv",
        index=False,
    )
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    decision = {
        "status": result["status"],
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "draws": spec.draws,
        "rank": spec.rank,
        "local_length_block": spec.local_length_block,
        "orbit_ridge_ratio_reference": orbit_config["orbit_spec"]["ridge_ratio"],
        "claim_boundary": config["claim_boundary"],
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = (
        "# V8 Event-Set Composition Knockout\n\n"
        f"Status: `{result['status']}`\n\n"
        "Pseudo event sets preserve corpus, split, context, event position, "
        "all event marginals, and local text-length rank, while independently "
        "breaking within-author event co-occurrence at every order slot.\n\n"
        "## Result\n\n"
        f"{result['cells'].to_markdown(index=False)}\n\n"
        "## Reallocation quality\n\n"
        f"{result['diagnostics'].groupby(['corpus', 'split']).agg({'same_author': 'sum', 'mean_absolute_length_difference': 'mean'}).reset_index().to_markdown(index=False)}\n\n"
        "## Claim boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
