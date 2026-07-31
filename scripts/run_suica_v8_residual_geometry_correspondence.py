#!/usr/bin/env python3
"""Run V8 axis-free residual geometry correspondence on real text."""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

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
from suica_core.v8_exchangeable_background_audit import (  # noqa: E402
    exchangeable_set_reallocation,
)
from suica_core.v8_marginal_background_quotient import (  # noqa: E402
    MarginalQuotientSpec,
    fit_marginal_background,
    quotient_blocks,
    quotient_views,
    tensor_feature_blocks,
)
from suica_core.v8_nuisance_filtration import (  # noqa: E402
    build_nuisance_profiles,
    fit_nuisance_residualizer,
)
from suica_core.v8_realtext_relation_field import (  # noqa: E402
    RealTextRelationSpec,
    frozen_random_directions,
    stable_bucket,
)
from suica_core.v8_residual_geometry_correspondence import (  # noqa: E402
    ResidualGeometrySpec,
    evaluate_residual_geometry,
    frozen_bandwidth,
)


DEFAULT_CONFIG = (
    ROOT / "configs" / "v8_residual_geometry_correspondence.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_residual_geometry_correspondence"
    / "audit_20260827"
)
DEFAULT_REPORT = (
    ROOT / "reports" / "V8_RESIDUAL_GEOMETRY_CORRESPONDENCE.md"
)


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _overall_status(corpus_status: dict[str, str]) -> str:
    order = (
        "NONLINEAR_RESIDUAL_GEOMETRY",
        "DISTRIBUTED_LINEAR_GEOMETRY",
        "AXIS_FREE_MULTI_SCALE_KERNEL_CORRESPONDENCE",
        "AXIS_FREE_SHORT_SCALE_KERNEL_CORRESPONDENCE",
        "AXIS_FREE_SINGLE_SCALE_KERNEL_CORRESPONDENCE",
        "PERSISTENT_LOCAL_RESIDUAL_GEOMETRY",
    )
    for status in order:
        if status in corpus_status.values():
            return status
    return "SCALAR_CONCORDANCE_ONLY"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()

    config = _json(args.config)
    base = _json(_resolve(config["base_config"]))
    nuisance_config = _json(_resolve(config["nuisance_config"]))
    feature_spec = RealTextRelationSpec(**base["spec"])
    geometry_payload = dict(config["geometry_spec"])
    geometry_payload["bandwidth_multipliers"] = tuple(
        map(float, geometry_payload["bandwidth_multipliers"])
    )
    geometry_payload["neighborhood_fractions"] = tuple(
        map(float, geometry_payload["neighborhood_fractions"])
    )
    geometry_spec = ResidualGeometrySpec(**geometry_payload)
    background_draws = int(config["background_draws"])
    if args.quick:
        background_draws = 49
        geometry_spec = replace(
            geometry_spec,
            d0_null_draws=99,
            test_null_draws=99,
            bootstrap_draws=99,
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
    background_spec = MarginalQuotientSpec(
        background_draws=background_draws,
        null_draws=99,
        diagnostic_null_draws=99,
        bootstrap_draws=99,
        bootstrap_reference_worlds=8,
        local_length_block=int(nuisance_config["local_length_block"]),
        seed=geometry_spec.seed,
    )
    directions = frozen_random_directions(
        event_dimensions=2 * feature_spec.hash_dimensions,
        count=feature_spec.random_directions,
        seed=feature_spec.seed + 17,
    )[0]
    loaders = {
        "pandora": load_pandora_events,
        "essays": load_essays_events,
        "x_market": load_x_events,
    }
    events_per_author = int(config["matched_events_per_author"])
    declared_groups = nuisance_config["tiers"][
        nuisance_config["primary_tier"]
    ]
    panels = {}
    bandwidths = {}
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
        profiles = build_nuisance_profiles(
            events,
            tensor,
            feature_spec=feature_spec,
            content_directions=int(nuisance_config["content_directions"]),
        )
        columns = sorted(
            {
                column
                for group in declared_groups
                for column in profiles.groups[group]
            }
        )
        background, _ = fit_marginal_background(
            tensor,
            marginal_directions=directions,
            spec=background_spec,
            rng=np.random.default_rng(
                geometry_spec.seed
                + stable_bucket(
                    corpus,
                    salt="v8-rgc-background",
                    modulus=2**31 - 1,
                )
            ),
            reallocator=exchangeable_set_reallocation,
        )
        blocks = tensor_feature_blocks(
            tensor.vectors,
            marginal_directions=directions,
        )
        quotient = quotient_blocks(
            blocks,
            tensor.metadata["context"].astype(str).to_numpy(),
            background,
        )
        raw = quotient_views(
            quotient,
            marginal_directions=directions,
        )["M_all"]
        d0 = tensor.metadata["split"].eq("D0").to_numpy()
        residualizer = fit_nuisance_residualizer(
            raw,
            profiles.values,
            d0,
            columns=columns,
            ridge_ratio=float(nuisance_config["ridge_ratio"]),
        )
        residual = residualizer.transform(raw, profiles.values)
        nuisance = (
            profiles.values[..., residualizer.active_columns]
            - residualizer.center
        ) / residualizer.scale
        panels[corpus] = (
            tensor.metadata.copy(),
            residual,
            nuisance,
        )
        bandwidths[corpus] = frozen_bandwidth(
            residual,
            tensor.metadata,
        )
        schema["active_nuisance_columns"] = int(
            len(residualizer.active_columns)
        )
        schema["d0_frozen_bandwidth"] = bandwidths[corpus]
        schemas.append(schema)

    result = evaluate_residual_geometry(
        panels,
        bandwidth_by_corpus=bandwidths,
        spec=geometry_spec,
    )
    # Opened-panel diagnostic only: disaggregate the pooled block geometry
    # without changing the primary corpus-level decision.
    context_panels = {}
    context_bandwidths = {}
    context_lookup = []
    for corpus, (metadata, residual, nuisance) in panels.items():
        for context in metadata["context"].astype(str).unique():
            mask = metadata["context"].astype(str).eq(context).to_numpy()
            key = f"{corpus}::{context}"
            context_panels[key] = (
                metadata.loc[mask].reset_index(drop=True),
                residual[mask],
                nuisance[mask],
            )
            context_bandwidths[key] = bandwidths[corpus]
            context_lookup.append(
                {
                    "context_panel": key,
                    "corpus": corpus,
                    "context": context,
                    "authors": int(mask.sum()),
                    "bandwidth_source": corpus,
                }
            )
    context_result = evaluate_residual_geometry(
        context_panels,
        bandwidth_by_corpus=context_bandwidths,
        spec=geometry_spec,
    )
    context_status = {
        key: (
            "NO_CONTEXT_RELATION_GEOMETRY_RESOLVED"
            if value == "SCALAR_CONCORDANCE_ONLY"
            else value
        )
        for key, value in context_result["status"].items()
    }
    decision = {
        "status": "RESIDUAL_GEOMETRY_CORRESPONDENCE_COMPLETED",
        "overall_geometry_status": _overall_status(result["status"]),
        "corpus_status": result["status"],
        "context_disaggregation_status": context_status,
        "context_disaggregation_role": (
            "OPENED_PANEL_DIAGNOSTIC_NOT_A_PROMOTION_GATE"
        ),
        "filtered_linear_spectrum_status": (
            "NO_REPLICATED_LOW_DIMENSIONAL_AXIS"
        ),
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_boundary": config["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result["cells"].to_csv(args.output_dir / "geometry_cells.csv", index=False)
    context_result["cells"].to_csv(
        args.output_dir / "context_geometry_cells.csv",
        index=False,
    )
    pd.DataFrame(context_lookup).to_csv(
        args.output_dir / "context_geometry_panels.csv",
        index=False,
    )
    pd.DataFrame(
        [
            {"corpus": corpus, "d0_frozen_bandwidth": value}
            for corpus, value in bandwidths.items()
        ]
    ).to_csv(args.output_dir / "bandwidths.csv", index=False)
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    held = result["cells"].loc[
        result["cells"]["split"].isin(["D1", "D2"])
    ]
    discovery = result["cells"].loc[result["cells"]["split"].eq("D0")]
    report = (
        "# V8 Residual Geometry Correspondence\n\n"
        f"Status: `{decision['overall_geometry_status']}`\n\n"
        "The experiment compares author-by-author relation matrices after "
        "the exchangeable M background quotient, D0-frozen declared-"
        "opportunity coordinate filtration, and replicate-specific nuisance-"
        "kernel conditioning. The corpus statistic is a context-stratified "
        "block-diagonal aggregate weighted by retained within-context pair "
        "mass; it contains no cross-context author relation. It asks whether "
        "geometry survives without a stable global factor axis.\n\n"
        "## Decision\n\n"
        f"```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n```\n\n"
        "## D0 scale audit\n\n"
        f"{discovery.to_markdown(index=False)}\n\n"
        "## Held-out D1/D2\n\n"
        f"{held.to_markdown(index=False)}\n\n"
        "## Opened-panel context disaggregation\n\n"
        "This diagnostic reuses the opened authors and the corpus-level D0 "
        "bandwidth. It localizes the context-stratified block aggregate but "
        "cannot promote a context-specific claim or establish scalar "
        "concordance inside each context.\n\n"
        f"{pd.DataFrame([{'context_panel': key, 'status': value} for key, value in context_status.items()]).to_markdown(index=False)}\n\n"
        "## Reading rule\n\n"
        "`DISTRIBUTED_LINEAR_GEOMETRY` means linear author-relation kernels "
        "repeat despite the absence of a stable low-dimensional axis. "
        "`AXIS_FREE_SHORT_SCALE_KERNEL_CORRESPONDENCE` means one registered "
        "sub-median RBF scale repeats. "
        "`AXIS_FREE_MULTI_SCALE_KERNEL_CORRESPONDENCE` means at least two "
        "registered RBF scales repeat. Neither status is a nonlinear claim "
        "unless the paired gain over linear KRC also closes. "
        "`NONLINEAR_RESIDUAL_GEOMETRY` additionally requires one RBF scale "
        "to beat linear KRC in both held-out panels. "
        "`PERSISTENT_LOCAL_RESIDUAL_GEOMETRY` requires two adjacent "
        "neighborhood scales in both panels. All families use one maxT "
        "correction. The current panels are opened. Context disaggregation "
        "and downstream transport diagnostics reuse the same D1/D2 authors "
        "and are not independent confirmations; fresh D3 is required for "
        "promotion.\n\n"
        "## Boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    args.report.write_text(report, encoding="utf-8")
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
