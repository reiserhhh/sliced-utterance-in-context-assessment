#!/usr/bin/env python3
"""Run the exact-inner, statistic-level order null for K orientation."""
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
from suica_core.v8_order_statistic_null import (  # noqa: E402
    OrderStatisticNullSpec,
    build_exact_permutation_panel,
    evaluate_statistic_level_order_null,
)
from suica_core.v8_realtext_relation_field import RealTextRelationSpec  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_order_statistic_null.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_order_statistic_null" / "audit_20260812"
DEFAULT_REPORT = ROOT / "reports" / "V8_ORDER_STATISTIC_NULL.md"


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
    spec = OrderStatisticNullSpec(**config["spec"])
    events_per_author = int(config["matched_events_per_author"])
    base["data"]["pandora"]["minimum_events"] = events_per_author
    base["data"]["pandora"]["maximum_events"] = events_per_author
    base["data"]["essays"]["chunks"] = events_per_author
    if args.quick:
        spec = replace(spec, calibration_draws=19, outer_draws=99, rank=2)
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
        panel = build_exact_permutation_panel(
            events,
            corpus=corpus,
            feature_spec=feature_spec,
        )
        schema["split_counts"] = panel.metadata["split"].value_counts().to_dict()
        schema["inner_permutations"] = 24
        schemas.append(schema)
        panels[corpus] = panel

    result = evaluate_statistic_level_order_null(
        panels["pandora"],
        panels["essays"],
        spec=spec,
    )
    decision = {
        "status": result["status"],
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "epsilon": result["epsilon"],
        "rank": result["rank"],
        "outer_draws": spec.outer_draws,
        "claim_boundary": config["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result["cells"].to_csv(args.output_dir / "order_null_cells.csv", index=False)
    result["null_scores"].to_csv(
        args.output_dir / "order_null_scores.csv",
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
    report = (
        "# V8 Statistic-Level Conditional Order Null\n\n"
        f"Status: `{decision['status']}`\n\n"
        "Each four-event technical replicate is centered by all 4!=24 "
        "permutations. The outer null independently permutes the two technical "
        "replicates, authors, and corpora, then rebuilds replicated density and "
        "the final matched-spectrum orientation statistic.\n\n"
        "## Result\n\n"
        f"{result['cells'].to_markdown(index=False)}\n\n"
        "## Claim boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
