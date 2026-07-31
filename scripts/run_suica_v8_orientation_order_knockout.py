#!/usr/bin/env python3
"""Run the paired within-replicate order-shuffle knockout for K orientation."""
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
from suica_core.v8_orientation_order_knockout import (  # noqa: E402
    OrderKnockoutSpec,
    evaluate_order_knockout,
    shuffle_within_replicate,
)
from suica_core.v8_realtext_relation_field import (  # noqa: E402
    RealTextRelationSpec,
    build_feature_panel,
)
from suica_core.v8_support_containment import _split_raw  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_orientation_order_knockout.json"
DEFAULT_OUTPUT = (
    ROOT / "results" / "v8_orientation_order_knockout" / "audit_20260811"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_ORIENTATION_ORDER_KNOCKOUT.md"


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
    spec = OrderKnockoutSpec(**config["spec"])
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

    native_panels = {}
    shuffled_panels = {}
    schemas = []
    for corpus, loader in (
        ("pandora", load_pandora_events),
        ("essays", load_essays_events),
    ):
        events, schema = loader(base["data"][corpus])
        native = build_feature_panel(
            events,
            corpus=corpus,
            context_role=schema["context_role"],
            replicate_type=schema["replicate_type"],
            spec=feature_spec,
        )
        shuffled = build_feature_panel(
            shuffle_within_replicate(
                events,
                seed=spec.seed,
                corpus=corpus,
            ),
            corpus=corpus,
            context_role=schema["context_role"],
            replicate_type=schema["replicate_type"],
            spec=feature_spec,
        )
        schema["split_counts"] = native.metadata["split"].value_counts().to_dict()
        schemas.append(schema)
        native_panels[corpus] = native
        shuffled_panels[corpus] = shuffled

    native = {
        corpus: {
            split: _split_raw(panel, "K", split)
            for split in ("D0", "D1", "D2")
        }
        for corpus, panel in native_panels.items()
    }
    shuffled = {
        corpus: {
            split: _split_raw(panel, "K", split)
            for split in ("D0", "D1", "D2")
        }
        for corpus, panel in shuffled_panels.items()
    }
    result = evaluate_order_knockout(
        native["pandora"],
        native["essays"],
        shuffled["pandora"],
        shuffled["essays"],
        spec=spec,
    )
    decision = {
        "status": result["status"],
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "epsilon": result["epsilon"],
        "rank": result["rank"],
        "claim_boundary": config["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result["cells"].to_csv(args.output_dir / "order_knockout_cells.csv", index=False)
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = (
        "# V8 K-Family Orientation Order Knockout\n\n"
        f"Status: `{decision['status']}`\n\n"
        "The author, event set, technical replicate membership, event count, "
        "and corpus are fixed. Text order is independently permuted inside "
        "each even/odd replicate before rebuilding K.\n\n"
        "## Paired result\n\n"
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
