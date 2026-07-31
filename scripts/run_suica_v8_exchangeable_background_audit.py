#!/usr/bin/env python3
"""Run the exchangeability-corrected V8 M background and spectrum audit."""
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
from suica_core.v8_conditional_concordance_spectrum import (  # noqa: E402
    ConcordanceSpectrumSpec,
    evaluate_conditional_concordance_spectrum,
)
from suica_core.v8_event_set_composition_knockout import (  # noqa: E402
    build_event_tensor,
)
from suica_core.v8_exchangeable_background_audit import (  # noqa: E402
    exchangeable_set_reallocation,
)
from suica_core.v8_marginal_background_quotient import (  # noqa: E402
    MarginalQuotientSpec,
    evaluate_marginal_background_quotient,
)
from suica_core.v8_realtext_relation_field import (  # noqa: E402
    RealTextRelationSpec,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_exchangeable_background_audit.json"
DEFAULT_OUTPUT = (
    ROOT / "results" / "v8_exchangeable_background_audit" / "audit_20260824"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_EXCHANGEABLE_BACKGROUND_AUDIT.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _comparison(
    marginal: pd.DataFrame,
    spectrum: pd.DataFrame,
    config: dict[str, Any],
) -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    old_marginal_path = _resolve(config["historical_marginal_cells"])
    if old_marginal_path.exists():
        old = pd.read_csv(old_marginal_path)
        old = old.loc[old["view"].eq("M_all")].copy()
        new = marginal.loc[marginal["view"].eq("M_all")].copy()
        keys = ["corpus", "split"]
        selected = old[
            keys
            + [
                "link_delta",
                "link_max_t_p",
                "link_bootstrap_lcb",
            ]
        ].merge(
            new[
                keys
                + [
                    "link_delta",
                    "link_max_t_p",
                    "link_bootstrap_lcb",
                ]
            ],
            on=keys,
            suffixes=("_cyclic", "_exchangeable"),
        )
        selected["family"] = "signed_link"
        rows.append(
            selected.rename(
                columns={
                    "link_delta_cyclic": "effect_cyclic",
                    "link_delta_exchangeable": "effect_exchangeable",
                    "link_max_t_p_cyclic": "max_t_p_cyclic",
                    "link_max_t_p_exchangeable": "max_t_p_exchangeable",
                    "link_bootstrap_lcb_cyclic": "bootstrap_lcb_cyclic",
                    "link_bootstrap_lcb_exchangeable": (
                        "bootstrap_lcb_exchangeable"
                    ),
                }
            )
        )
    old_spectrum_path = _resolve(config["historical_spectrum_cells"])
    if old_spectrum_path.exists() and not spectrum.empty:
        old = pd.read_csv(old_spectrum_path)
        old = old.loc[old["view"].eq("M_all")].copy()
        new = spectrum.loc[spectrum["view"].eq("M_all")].copy()
        keys = ["corpus", "split"]
        selected = old[
            keys + ["delta", "max_t_p", "bootstrap_lcb"]
        ].merge(
            new[keys + ["delta", "max_t_p", "bootstrap_lcb"]],
            on=keys,
            suffixes=("_cyclic", "_exchangeable"),
        )
        selected["family"] = "positive_spectrum"
        rows.append(
            selected.rename(
                columns={
                    "delta_cyclic": "effect_cyclic",
                    "delta_exchangeable": "effect_exchangeable",
                }
            )
        )
    columns = [
        "corpus",
        "split",
        "family",
        "effect_cyclic",
        "effect_exchangeable",
        "max_t_p_cyclic",
        "max_t_p_exchangeable",
        "bootstrap_lcb_cyclic",
        "bootstrap_lcb_exchangeable",
    ]
    return (
        pd.concat(rows, ignore_index=True, sort=False)[columns]
        if rows
        else pd.DataFrame(columns=columns)
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
    marginal_spec = MarginalQuotientSpec(**config["marginal_spec"])
    spectrum_spec = ConcordanceSpectrumSpec(**config["spectrum_spec"])
    if args.quick:
        marginal_spec = replace(
            marginal_spec,
            background_draws=49,
            null_draws=99,
            diagnostic_null_draws=49,
            bootstrap_draws=99,
            bootstrap_reference_worlds=16,
        )
        spectrum_spec = replace(
            spectrum_spec,
            background_draws=49,
            spectrum_null_draws=49,
            test_null_draws=99,
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
        tensors[corpus] = build_event_tensor(
            events,
            corpus=corpus,
            feature_spec=feature_spec,
        )
        schemas.append(schema)

    marginal = evaluate_marginal_background_quotient(
        tensors,
        feature_spec=feature_spec,
        spec=marginal_spec,
        reallocator=exchangeable_set_reallocation,
    )
    spectrum = evaluate_conditional_concordance_spectrum(
        tensors,
        feature_spec=feature_spec,
        spec=spectrum_spec,
        reallocator=exchangeable_set_reallocation,
    )
    # Quick mode deliberately truncates PANDORA/Essays author panels, so it
    # must not be compared numerically with the historical full-panel run.
    comparison = (
        pd.DataFrame()
        if args.quick
        else _comparison(marginal["cells"], spectrum["cells"], config)
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    marginal["cells"].to_csv(args.output_dir / "marginal_cells.csv", index=False)
    marginal["null_scores"].to_csv(
        args.output_dir / "marginal_null_scores.csv",
        index=False,
    )
    marginal["background_diagnostics"].to_csv(
        args.output_dir / "background_diagnostics.csv",
        index=False,
    )
    marginal["reallocation_diagnostics"].to_csv(
        args.output_dir / "reallocation_diagnostics.csv",
        index=False,
    )
    spectrum["spectrum"].to_csv(args.output_dir / "spectrum.csv", index=False)
    spectrum["cells"].to_csv(args.output_dir / "spectrum_cells.csv", index=False)
    spectrum["loadings"].to_csv(args.output_dir / "loadings.csv", index=False)
    spectrum["gamma_diagnostics"].to_csv(
        args.output_dir / "gamma_diagnostics.csv",
        index=False,
    )
    comparison.to_csv(args.output_dir / "historical_comparison.csv", index=False)
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    diagnostics = marginal["reallocation_diagnostics"]
    decision = {
        "status": (
            "EXCHANGEABLE_NULL_AUDIT_COMPLETED"
            if marginal["status"] and spectrum["status"]
            else "EXCHANGEABLE_NULL_AUDIT_FAILED"
        ),
        "marginal_status": marginal["status"],
        "marginal_corpus_status": marginal["corpus_status"],
        "spectrum_status": spectrum["status"],
        "spectrum_corpus_status": spectrum["corpus_status"],
        "mean_fixed_point_fraction": float(
            diagnostics["same_author"].sum()
            / diagnostics["total_assignments"].sum()
        ),
        "identity_blocks_observed": int(
            diagnostics["identity_blocks"].sum()
        ),
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_boundary": config["claim_boundary"],
    }
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = (
        "# V8 Exchangeable Background Audit\n\n"
        f"Status: `{decision['status']}`\n\n"
        "The historical no-self cyclic knockout is rerun with uniform "
        "within-block permutations. Fixed points and the natural identity "
        "assignment belong to the corrected null support.\n\n"
        "## Decision\n\n"
        f"```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n```\n\n"
        "## Historical comparison\n\n"
        f"{comparison.to_markdown(index=False) if len(comparison) else '_No historical comparison available._'}\n\n"
        "## Corrected marginal cells\n\n"
        f"{marginal['cells'].loc[marginal['cells']['view'].eq('M_all')].to_markdown(index=False)}\n\n"
        "## Corrected spectrum resolution\n\n"
        f"{spectrum['spectrum'].to_markdown(index=False)}\n\n"
        "## Corrected frozen spectrum cells\n\n"
        f"{spectrum['cells'].to_markdown(index=False) if len(spectrum['cells']) else '_No resolved spectrum cells._'}\n\n"
        "## Claim boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
