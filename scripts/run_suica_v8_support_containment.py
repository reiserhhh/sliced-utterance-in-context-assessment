#!/usr/bin/env python3
"""Run the V8 capacity-matched soft-support containment audit."""
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
    corpus_pair_names,
)
from suica_core.v8_support_containment import (  # noqa: E402
    SupportContainmentSpec,
    classify_pair,
    evaluate_pair,
    fit_global_gauge,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_support_containment.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_support_containment" / "audit_20260806"
DEFAULT_REPORT = ROOT / "reports" / "V8_SUPPORT_CONTAINMENT_REPORT.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _report(
    decision: dict[str, Any],
    schemas: list[dict[str, Any]],
    summary: pd.DataFrame,
    classification: pd.DataFrame,
    claim_boundary: str,
) -> str:
    return (
        "# V8 Capacity-Matched Soft-Support Containment Audit\n\n"
        f"Status: `{decision['status']}`\n\n"
        "This audit tests whether the one-way frozen-source transport result is "
        "a reproducible support-coverage asymmetry rather than a sample-size or "
        "spectral-concentration artifact. It uses equal-author and equal-event "
        "panels, pair-symmetric and global robust diagonal gauges, D1/D2 "
        "confirmation, author bootstrap, Haar orientation nulls, and a complete "
        "eigenspectrum-matched sensitivity arm.\n\n"
        "## Mathematical estimand\n\n"
        "For trace-one replicated support density $\\rho_s$, $P_s(k,\\tau)$ "
        "maximizes $\\operatorname{tr}(P\\rho_s)-\\tau\\|P-kI/d\\|_F^2/2$ "
        "under $0\\preceq P\\preceq I$ and $\\operatorname{tr}P=k$. The "
        "directional ratio evaluates both source and target D0 filters on the "
        "same held-out target density. Its baseline is $k/d$, and results are "
        "integrated over a frozen $(k,\\tau)$ grid rather than selected post "
        "hoc. This is directional density coverage, not literal inclusion.\n\n"
        "## Data roles\n\n"
        f"{pd.DataFrame(schemas).to_markdown(index=False)}\n\n"
        "## D1/D2 pair estimates\n\n"
        f"{summary.to_markdown(index=False)}\n\n"
        "## Pair/family decisions\n\n"
        f"{classification.to_markdown(index=False)}\n\n"
        "## Claim boundary\n\n"
        f"{claim_boundary}\n"
    )


def _holm(values: pd.Series) -> pd.Series:
    """Return Holm-adjusted p-values while preserving the original index."""
    observed = values.astype(float)
    finite = observed.loc[observed.notna()]
    order = finite.sort_values().index
    total = len(finite)
    adjusted = pd.Series(float("nan"), index=observed.index, dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        candidate = min(1.0, (total - rank) * float(finite.loc[index]))
        running = max(running, candidate)
        adjusted.loc[index] = running
    return adjusted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    config = _json(args.config)
    base_config = _json(_resolve(config["base_config"]))
    feature_spec = RealTextRelationSpec(**base_config["spec"])
    containment_spec = SupportContainmentSpec(
        **{
            **config["spec"],
            "capacities": tuple(config["spec"]["capacities"]),
            "tau_multipliers": tuple(config["spec"]["tau_multipliers"]),
        }
    )
    matched_events = int(config["matched_events_per_author"])
    for corpus in ("pandora", "x_market"):
        base_config["data"][corpus]["minimum_events"] = matched_events
        base_config["data"][corpus]["maximum_events"] = matched_events
    base_config["data"]["essays"]["chunks"] = matched_events
    if args.quick:
        feature_spec = replace(
            feature_spec,
            transition_null_draws=min(feature_spec.transition_null_draws, 4),
        )
        containment_spec = replace(
            containment_spec,
            capacities=(2, 4, 8, 12),
            tau_multipliers=(1.0, 2.0),
            bootstrap_draws=19,
            rotation_draws=19,
            calibration_subsamples=9,
            maximum_calibration_authors=96,
            maximum_confirmation_authors=72,
            minimum_authors=24,
        )
        for corpus in ("pandora", "x_market"):
            base_config["data"][corpus]["maximum_authors_per_context"] = min(
                48,
                int(base_config["data"][corpus]["maximum_authors_per_context"]),
            )
        base_config["data"]["essays"]["maximum_authors"] = min(
            192,
            int(base_config["data"]["essays"]["maximum_authors"]),
        )

    loaders = {
        "pandora": load_pandora_events,
        "essays": load_essays_events,
        "x_market": load_x_events,
    }
    panels = {}
    schemas = []
    for corpus, loader in loaders.items():
        events, schema = loader(base_config["data"][corpus])
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

    summary_rows = []
    curve_rows = []
    global_gauges = {
        family: fit_global_gauge(
            panels,
            family,
            maximum_authors=containment_spec.maximum_calibration_authors,
            salt=f"v8-coverage-global-{family}-{containment_spec.seed}",
        )
        for family in FAMILY_NAMES
    }
    for source, target in corpus_pair_names(panels):
        for family in FAMILY_NAMES:
            result = evaluate_pair(
                source,
                panels[source],
                target,
                panels[target],
                family,
                global_gauge=global_gauges[family],
                spec=containment_spec,
            )
            summary_rows.extend(result["summary"])
            curve_rows.extend(result["curves"])
    summary = pd.DataFrame(summary_rows)
    curves = pd.DataFrame(curve_rows)
    summary["forward_rotation_q"] = float("nan")
    summary["reverse_rotation_q"] = float("nan")
    for (_source, _target, _family), indices in summary.groupby(
        ["source", "target", "family"],
        sort=False,
    ).groups.items():
        group = summary.loc[indices]
        values = pd.concat(
            [
                group["forward_rotation_p"],
                group["reverse_rotation_p"],
            ],
            ignore_index=True,
        )
        adjusted = _holm(values)
        size = len(group)
        summary.loc[indices, "forward_rotation_q"] = adjusted.iloc[
            :size
        ].to_numpy()
        summary.loc[indices, "reverse_rotation_q"] = adjusted.iloc[
            size:
        ].to_numpy()
    classifications = []
    for (source, target, family), group in summary.groupby(
        ["source", "target", "family"],
        sort=True,
    ):
        classifications.append(
            {
                "source": source,
                "target": target,
                "family": family,
                **classify_pair(group, spec=containment_spec),
            }
        )
    classification = pd.DataFrame(classifications)
    directional = classification["decision"].isin(
        {
            "DIRECTIONAL_COVERAGE_ASYMMETRY",
            "APPROXIMATE_DIRECTIONAL_COVERAGE_CANDIDATE",
        }
    )
    if classification["decision"].eq(
        "APPROXIMATE_DIRECTIONAL_COVERAGE_CANDIDATE"
    ).any():
        status = "APPROXIMATE_SUPPORT_COVERAGE_CANDIDATE"
    elif directional.any():
        status = "SUPPORT_COVERAGE_ASYMMETRY_OBSERVED"
    elif classification["decision"].eq("SHARED_ORIENTATION_NO_DIRECTION").any():
        status = "SHARED_SUPPORT_WITHOUT_DIRECTION"
    else:
        status = "SUPPORT_COVERAGE_UNRESOLVED"
    decision = {
        "status": status,
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "directional_pair_families": classification.loc[
            directional,
            ["source", "target", "family", "direction", "decision"],
        ].to_dict(orient="records"),
        "claim_boundary": config["claim_boundary"],
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output_dir / "containment_summary.csv", index=False)
    curves.to_csv(args.output_dir / "capacity_curves.csv", index=False)
    classification.to_csv(args.output_dir / "pair_decisions.csv", index=False)
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
        summary,
        classification,
        config["claim_boundary"],
    )
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    args.report.write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
