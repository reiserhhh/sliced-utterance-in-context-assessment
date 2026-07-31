#!/usr/bin/env python3
"""Run the V8 conditional concordance spectrum audit."""
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
from suica_core.v8_conditional_concordance_spectrum import (  # noqa: E402
    ConcordanceSpectrumSpec,
    evaluate_conditional_concordance_spectrum,
)
from suica_core.v8_event_set_composition_knockout import (  # noqa: E402
    build_event_tensor,
)
from suica_core.v8_realtext_relation_field import RealTextRelationSpec  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_conditional_concordance_spectrum.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_conditional_concordance_spectrum"
    / "audit_20260818"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_CONDITIONAL_CONCORDANCE_SPECTRUM.md"


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
    spec = ConcordanceSpectrumSpec(
        **{
            **config["spec"],
            "gamma_grid": tuple(config["spec"]["gamma_grid"]),
        }
    )
    if args.quick:
        spec = replace(
            spec,
            background_draws=49,
            spectrum_null_draws=49,
            test_null_draws=99,
            bootstrap_draws=99,
            bootstrap_reference_worlds=16,
            maximum_rank=4,
        )
        base["data"]["pandora"]["maximum_authors_per_context"] = min(
            48,
            int(base["data"]["pandora"]["maximum_authors_per_context"]),
        )
        base["data"]["essays"]["maximum_authors"] = min(
            160,
            int(base["data"]["essays"]["maximum_authors"]),
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
        tensors[corpus] = build_event_tensor(
            events,
            corpus=corpus,
            feature_spec=feature_spec,
        )
        schemas.append(schema)

    result = evaluate_conditional_concordance_spectrum(
        tensors,
        feature_spec=feature_spec,
        spec=spec,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "spectrum",
        "gamma_diagnostics",
        "loadings",
        "cells",
        "null_scores",
    ):
        result[name].to_csv(args.output_dir / f"{name}.csv", index=False)
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
        "spectrum_null_draws": spec.spectrum_null_draws,
        "test_null_draws": spec.test_null_draws,
        "bootstrap_draws": spec.bootstrap_draws,
        "claim_boundary": config["claim_boundary"],
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = (
        "# V8 Conditional Concordance Spectrum\n\n"
        f"Status: `{result['status']}`\n\n"
        "This opened-panel follow-up asks whether the signed M concordance "
        "found by the background quotient is low-dimensionally compressible. "
        "Positive and negative generalized spectra are retained separately; "
        "no positive-part operator is used.\n\n"
        "## D0 spectrum resolution\n\n"
        f"{result['spectrum'].to_markdown(index=False) if len(result['spectrum']) else '_No resolved rows._'}\n\n"
        "## Frozen D1/D2 projections\n\n"
        f"{result['cells'].to_markdown(index=False) if len(result['cells']) else '_No frozen positive spectrum reached D1/D2._'}\n\n"
        "## Block attribution\n\n"
        f"{result['loadings'].to_markdown(index=False) if len(result['loadings']) else '_No stable positive loading space._'}\n\n"
        "## Claim boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
