#!/usr/bin/env python3
"""Run the opportunity-filtered M-all concordance spectrum falsification."""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

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
from suica_core.v8_filtered_concordance_spectrum import (  # noqa: E402
    FilteredSpectrumSpec,
    evaluate_filtered_spectrum,
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


DEFAULT_CONFIG = ROOT / "configs" / "v8_filtered_concordance_spectrum.json"
DEFAULT_OUTPUT = (
    ROOT / "results" / "v8_filtered_concordance_spectrum" / "audit_20260826"
)
DEFAULT_REPORT = ROOT / "reports" / "V8_FILTERED_CONCORDANCE_SPECTRUM.md"


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
    nuisance_config = _json(_resolve(config["nuisance_config"]))
    feature_spec = RealTextRelationSpec(**base["spec"])
    spectrum_spec = FilteredSpectrumSpec(**config["spectrum_spec"])
    background_draws = int(config["background_draws"])
    if args.quick:
        background_draws = 49
        spectrum_spec = replace(
            spectrum_spec,
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
        seed=int(nuisance_config["seed"]),
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
                spectrum_spec.seed
                + stable_bucket(
                    corpus,
                    salt="v8-filtered-spectrum-background",
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
        panels[corpus] = (
            tensor.metadata.copy(),
            residualizer.transform(raw, profiles.values),
        )
        schema["active_nuisance_columns"] = int(
            len(residualizer.active_columns)
        )
        schemas.append(schema)

    result = evaluate_filtered_spectrum(
        panels,
        gamma_by_corpus={
            str(key): float(value)
            for key, value in config["gamma_by_corpus"].items()
        },
        spec=spectrum_spec,
    )
    decision = {
        "status": result["status"],
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "strict_shape_status": (
            "STOPPED_BEFORE_SPECTRUM__FILTERED_OMNIBUS_NOT_REPLICATED"
        ),
        "claim_boundary": config["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    result["discovery"].to_csv(
        args.output_dir / "discovery.csv",
        index=False,
    )
    result["cells"].to_csv(args.output_dir / "cells.csv", index=False)
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schemas, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = (
        "# V8 Opportunity-Filtered Concordance Spectrum\n\n"
        f"Status: `{decision['status']}`\n\n"
        "The M-all quotient is first residualized by the D0-frozen declared "
        "opportunity map. D0 author correspondence permutations define the "
        "spectrum null; D1/D2 are used only after axes are frozen. "
        "Strict-shape is stopped before spectrum discovery because its "
        "filtered omnibus relation did not replicate.\n\n"
        "## Decision\n\n"
        f"```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n```\n\n"
        "## D0 discovery\n\n"
        f"{result['discovery'].to_markdown(index=False)}\n\n"
        "## D1/D2 frozen tests\n\n"
        f"{result['cells'].to_markdown(index=False) if len(result['cells']) else '_No axis reached held-out testing._'}\n\n"
        "## Boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    args.report.write_text(report, encoding="utf-8")
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
