#!/usr/bin/env python3
"""Run the V8 order-free marginal-background quotient audit."""
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
    load_x_events,
)
from suica_core.v8_event_set_composition_knockout import (  # noqa: E402
    build_event_tensor,
)
from suica_core.v8_marginal_background_quotient import (  # noqa: E402
    MarginalQuotientSpec,
    evaluate_marginal_background_quotient,
)
from suica_core.v8_realtext_relation_field import RealTextRelationSpec  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_marginal_background_quotient.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_marginal_background_quotient"
    / "audit_20260817"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_MARGINAL_BACKGROUND_QUOTIENT.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _markdown_table(frame: Any) -> str:
    return frame.to_markdown(index=False) if len(frame) else "_No rows._"


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
    spec = MarginalQuotientSpec(**config["spec"])
    if args.quick:
        spec = replace(
            spec,
            background_draws=49,
            null_draws=99,
            diagnostic_null_draws=99,
            bootstrap_draws=99,
            bootstrap_reference_worlds=16,
        )
        base["data"]["pandora"]["maximum_authors_per_context"] = min(
            48,
            int(base["data"]["pandora"]["maximum_authors_per_context"]),
        )
        base["data"]["essays"]["maximum_authors"] = min(
            160,
            int(base["data"]["essays"]["maximum_authors"]),
        )
        base["data"]["x_market"]["maximum_authors_per_context"] = min(
            48,
            int(base["data"]["x_market"]["maximum_authors_per_context"]),
        )

    events_per_author = int(config["matched_events_per_author"])
    loaders = {
        "pandora": load_pandora_events,
        "essays": load_essays_events,
        "x_market": load_x_events,
    }
    tensors = {}
    schemas = []
    for corpus in config["corpora"]:
        data_config = dict(base["data"][corpus])
        if corpus == "essays":
            data_config["chunks"] = events_per_author
        else:
            data_config["minimum_events"] = events_per_author
            data_config["maximum_events"] = events_per_author
        events, schema = loaders[corpus](data_config)
        tensor = build_event_tensor(
            events,
            corpus=corpus,
            feature_spec=feature_spec,
        )
        schema["split_context_counts"] = {
            f"{split}::{context}": int(count)
            for (split, context), count in tensor.metadata.groupby(
                ["split", "context"],
                observed=True,
            ).size().items()
        }
        tensors[corpus] = tensor
        schemas.append(schema)

    result = evaluate_marginal_background_quotient(
        tensors,
        feature_spec=feature_spec,
        spec=spec,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result["cells"].to_csv(args.output_dir / "quotient_cells.csv", index=False)
    result["block_diagnostics"].to_csv(
        args.output_dir / "block_diagnostics.csv",
        index=False,
    )
    result["null_scores"].to_csv(
        args.output_dir / "quotient_null_scores.csv",
        index=False,
    )
    result["background_diagnostics"].to_csv(
        args.output_dir / "background_diagnostics.csv",
        index=False,
    )
    result["reallocation_diagnostics"].to_csv(
        args.output_dir / "reallocation_diagnostics.csv",
        index=False,
    )
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    decision = {
        "status": result["status"],
        "corpus_status": result["corpus_status"],
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "background_draws": spec.background_draws,
        "null_draws": spec.null_draws,
        "diagnostic_null_draws": spec.diagnostic_null_draws,
        "bootstrap_draws": spec.bootstrap_draws,
        "bootstrap_reference_worlds": spec.bootstrap_reference_worlds,
        "corpora": list(tensors),
        "claim_boundary": config["claim_boundary"],
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    primary = result["cells"].loc[result["cells"]["view"].eq("M_all")]
    diagnostic_columns = [
        "corpus",
        "split",
        "view",
        "frobenius_delta",
        "frobenius_raw_p",
        "observed_link",
        "link_raw_p",
        "observed_same_author_auc",
        "auc_raw_p",
    ]
    report = (
        "# V8 Marginal-Background Quotient\n\n"
        f"Status: `{result['status']}`\n\n"
        "Natural four-event author sets are compared with conditional "
        "pseudo-author orbits that preserve corpus, D-split, context, event "
        "slot, local length rank, and every 64-dimensional event vector. "
        "D0 pseudo worlds freeze blockwise centers and covariance whitening; "
        "D1/D2 are untouched audit panels. The signed replicated operator is "
        "never projected to a positive part.\n\n"
        "## Omnibus M result\n\n"
        f"{_markdown_table(primary)}\n\n"
        "## Location/shape diagnostics\n\n"
        f"{_markdown_table(result['cells'][diagnostic_columns])}\n\n"
        "The `strict_shape` view excludes raw quantiles because those "
        "quantiles retain location information; it contains variance and "
        "centered RFF blocks only. Diagnostic views do not promote a claim "
        "when the omnibus M gate fails.\n\n"
        "## Background diagnostics\n\n"
        f"{_markdown_table(result['background_diagnostics'])}\n\n"
        "## Claim boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
