#!/usr/bin/env python3
"""Run D0-frozen nuisance sensitivity on exchangeable V8 M quotients."""
from __future__ import annotations

import argparse
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
    bootstrap_link_interval,
    build_nuisance_profiles,
    cross_trace_decomposition,
    fit_nuisance_residualizer,
    signed_link,
    within_context_decomposition_null,
    within_context_link_null,
)
from suica_core.v8_realtext_relation_field import (  # noqa: E402
    RealTextRelationSpec,
    frozen_random_directions,
    stable_bucket,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_nuisance_filtration.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_nuisance_filtration" / "audit_20260825"
DEFAULT_REPORT = ROOT / "reports" / "V8_NUISANCE_FILTRATION.md"


def _json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve(path: str | Path) -> Path:
    value = Path(path).expanduser()
    return value if value.is_absolute() else (ROOT / value).resolve()


def _paired_change_interval(
    raw: np.ndarray,
    filtered: np.ndarray,
    contexts: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> tuple[float, float, float]:
    labels = np.asarray(contexts).astype(str)
    groups = {
        context: np.flatnonzero(labels == context)
        for context in np.unique(labels)
    }

    def link(values: np.ndarray) -> float:
        return signed_link(values)

    observed = link(filtered) - link(raw)
    samples = np.empty(draws, dtype=float)
    for draw in range(draws):
        indices = np.concatenate(
            [
                rng.choice(group, size=len(group), replace=True)
                for group in groups.values()
            ]
        )
        samples[draw] = link(filtered[indices]) - link(raw[indices])
    centered = samples - samples.mean()
    return (
        float(observed),
        float(observed + np.quantile(centered, 0.025)),
        float(observed + np.quantile(centered, 0.975)),
    )


def _maximum_t(rows: pd.DataFrame, nulls: dict[str, np.ndarray]) -> pd.DataFrame:
    output = rows.copy()
    output["max_t_p"] = np.nan
    for tier in output["tier"].unique():
        primary = output.loc[
            output["tier"].eq(tier) & output["view"].eq("M_all")
        ]
        if primary.empty:
            continue
        standardized = []
        observed_z = []
        for row in primary.itertuples():
            values = nulls[str(row.cell_id)]
            standard = max(float(values.std(ddof=1)), 1e-12)
            standardized.append((values - values.mean()) / standard)
            observed_z.append((float(row.observed_link) - values.mean()) / standard)
        maximum = np.max(np.vstack(standardized), axis=0)
        for cell_id, value in zip(primary["cell_id"], observed_z, strict=True):
            output.loc[output["cell_id"].eq(cell_id), "max_t_p"] = (
                1 + np.sum(maximum >= value)
            ) / (len(maximum) + 1)
    return output


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
    background_draws = int(config["background_draws"])
    null_draws = int(config["null_draws"])
    bootstrap_draws = int(config["bootstrap_draws"])
    if args.quick:
        background_draws = 49
        null_draws = 99
        bootstrap_draws = 99
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
        local_length_block=int(config["local_length_block"]),
        seed=int(config["seed"]),
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
    cell_rows: list[dict[str, Any]] = []
    residualizer_rows: list[dict[str, Any]] = []
    schema_rows = []
    nulls: dict[str, np.ndarray] = {}
    events_per_author = int(config["matched_events_per_author"])

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
            content_directions=int(config["content_directions"]),
        )
        schema["nuisance_columns"] = len(profiles.columns)
        schema["nuisance_groups"] = {
            group: len(indices)
            for group, indices in profiles.groups.items()
        }
        schema_rows.append(schema)
        background_rng = np.random.default_rng(
            int(config["seed"])
            + stable_bucket(
                corpus,
                salt="v8-nuisance-background",
                modulus=2**31 - 1,
            )
        )
        background, _ = fit_marginal_background(
            tensor,
            marginal_directions=directions,
            spec=background_spec,
            rng=background_rng,
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
        views = quotient_views(quotient, marginal_directions=directions)
        d0 = tensor.metadata["split"].eq("D0").to_numpy()
        tier_values: dict[tuple[str, str], np.ndarray] = {}
        for view in ("M_all", "strict_shape"):
            raw = views[view]
            tier_values[(view, "raw")] = raw
            raw_energy = float(np.mean(raw[d0] ** 2))
            for tier, groups in config["tiers"].items():
                if tier == "raw":
                    continue
                columns = sorted(
                    {
                        column
                        for group in groups
                        for column in profiles.groups[group]
                    }
                )
                residualizer = fit_nuisance_residualizer(
                    raw,
                    profiles.values,
                    d0,
                    columns=columns,
                    ridge_ratio=float(config["ridge_ratio"]),
                )
                filtered = residualizer.transform(raw, profiles.values)
                tier_values[(view, tier)] = filtered
                residualizer_rows.append(
                    {
                        "corpus": corpus,
                        "view": view,
                        "tier": tier,
                        "requested_columns": len(columns),
                        "active_columns": int(
                            len(residualizer.active_columns)
                        ),
                        "d0_explained_energy_fraction": float(
                            1
                            - np.mean(filtered[d0] ** 2)
                            / max(raw_energy, 1e-12)
                        ),
                    }
                )
        for split in ("D1", "D2"):
            mask = tensor.metadata["split"].eq(split).to_numpy()
            contexts = tensor.metadata.loc[
                mask,
                "context",
            ].astype(str).to_numpy()
            raw_lookup = {
                view: tier_values[(view, "raw")][mask]
                for view in ("M_all", "strict_shape")
            }
            for view in ("M_all", "strict_shape"):
                for tier in config["tiers"]:
                    values = tier_values[(view, tier)][mask]
                    rng_seed = (
                        int(config["seed"])
                        + stable_bucket(
                            f"{corpus}-{split}-{view}-{tier}",
                            salt="v8-nuisance-test",
                            modulus=2**31 - 1,
                        )
                    )
                    observed, null = within_context_link_null(
                        values,
                        contexts,
                        draws=null_draws,
                        rng=np.random.default_rng(rng_seed),
                    )
                    lower, upper = bootstrap_link_interval(
                        values,
                        contexts,
                        draws=bootstrap_draws,
                        rng=np.random.default_rng(rng_seed + 1),
                    )
                    change, change_lower, change_upper = _paired_change_interval(
                        raw_lookup[view],
                        values,
                        contexts,
                        draws=bootstrap_draws,
                        rng=np.random.default_rng(rng_seed + 2),
                    )
                    decomposition = cross_trace_decomposition(
                        raw_lookup[view],
                        values,
                    )
                    component_excess = {
                        "profile_predictable": float("nan"),
                        "residual": float("nan"),
                        "profile_to_residual": float("nan"),
                        "residual_to_profile": float("nan"),
                        "profile_involving": float("nan"),
                        "raw_link": float("nan"),
                        "closure_error": float("nan"),
                    }
                    if tier == config["primary_tier"] and view == "M_all":
                        decomposition, component_null = (
                            within_context_decomposition_null(
                                raw_lookup[view],
                                values,
                                contexts,
                                draws=null_draws,
                                rng=np.random.default_rng(rng_seed + 3),
                            )
                        )
                        names = (
                            "profile_predictable",
                            "residual",
                            "profile_to_residual",
                            "residual_to_profile",
                        )
                        for name in names:
                            component_excess[name] = float(
                                decomposition[name]
                                - component_null[name].mean()
                            )
                        component_excess["profile_involving"] = float(
                            component_excess["profile_predictable"]
                            + component_excess["profile_to_residual"]
                            + component_excess["residual_to_profile"]
                        )
                        component_excess["raw_link"] = float(
                            decomposition["observed_link"]
                            - component_null["observed_link"].mean()
                        )
                        component_excess["closure_error"] = float(
                            sum(component_excess[name] for name in names)
                            - component_excess["raw_link"]
                        )
                    cell_id = f"{corpus}::{split}::{view}::{tier}"
                    nulls[cell_id] = null
                    cell_rows.append(
                        {
                            "cell_id": cell_id,
                            "corpus": corpus,
                            "split": split,
                            "view": view,
                            "tier": tier,
                            "authors": int(mask.sum()),
                            "observed_link": observed,
                            "null_mean": float(null.mean()),
                            "link_excess": float(observed - null.mean()),
                            "raw_p": float(
                                (1 + np.sum(null >= observed))
                                / (len(null) + 1)
                            ),
                            "link_ci_lower": lower,
                            "link_ci_upper": upper,
                            "excess_ci_lower": float(lower - null.mean()),
                            "excess_ci_upper": float(upper - null.mean()),
                            "change_from_raw": change,
                            "change_ci_lower": change_lower,
                            "change_ci_upper": change_upper,
                            "component_profile_predictable": decomposition[
                                "profile_predictable"
                            ],
                            "component_residual": decomposition["residual"],
                            "component_profile_to_residual": decomposition[
                                "profile_to_residual"
                            ],
                            "component_residual_to_profile": decomposition[
                                "residual_to_profile"
                            ],
                            "component_closure_error": decomposition[
                                "closure_error"
                            ],
                            "component_excess_profile_predictable": (
                                component_excess["profile_predictable"]
                            ),
                            "component_excess_residual": component_excess[
                                "residual"
                            ],
                            "component_excess_profile_to_residual": (
                                component_excess["profile_to_residual"]
                            ),
                            "component_excess_residual_to_profile": (
                                component_excess["residual_to_profile"]
                            ),
                            "component_excess_profile_involving": (
                                component_excess["profile_involving"]
                            ),
                            "component_excess_raw_link": component_excess[
                                "raw_link"
                            ],
                            "component_excess_closure_error": (
                                component_excess["closure_error"]
                            ),
                        }
                    )
    cells = _maximum_t(pd.DataFrame(cell_rows), nulls)
    primary = cells.loc[
        cells["tier"].eq(config["primary_tier"])
        & cells["view"].eq("M_all")
    ].copy()
    corpus_status = {}
    for corpus, group in primary.groupby("corpus", observed=True):
        passed = bool(
            group["link_excess"].gt(0).all()
            and group["excess_ci_lower"].gt(0).all()
            and group["max_t_p"].le(0.05).all()
        )
        corpus_status[str(corpus)] = (
            "DECLARED_OPPORTUNITY_CONDITIONED_CONCORDANCE_DETECTED"
            if passed
            else "DECLARED_OPPORTUNITY_CONDITIONED_CONCORDANCE_NOT_DETECTED"
        )
    decision = {
        "status": "NUISANCE_FILTRATION_COMPLETED",
        "primary_tier": config["primary_tier"],
        "corpus_status": corpus_status,
        "all_corpora_primary_pass": bool(
            corpus_status
            and all(
                value
                == "DECLARED_OPPORTUNITY_CONDITIONED_CONCORDANCE_DETECTED"
                for value in corpus_status.values()
            )
        ),
        "version": config["version"],
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "claim_boundary": config["claim_boundary"],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "filtration_cells.csv", index=False)
    pd.DataFrame(residualizer_rows).to_csv(
        args.output_dir / "residualizer_diagnostics.csv",
        index=False,
    )
    (args.output_dir / "data_schema.json").write_text(
        json.dumps(schema_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report = (
        "# V8 Nuisance Sensitivity Filtration\n\n"
        f"Status: `{decision['status']}`\n\n"
        "Every residualizer is fit on D0 and applied unchanged to D1/D2. "
        "The declared-opportunity tier covers length, format, time, repeated "
        "templates, language, and symbol where available. The final content "
        "tier is an aggressive sensitivity analysis, not a noise definition. "
        "The primary `link_excess` normalizes the residual by its own energy. "
        "The four `component_excess_*` channels instead share the raw-Q "
        "denominator and reconstruct `component_excess_raw_link`; these two "
        "effect scales must not be numerically equated.\n\n"
        "## Decision\n\n"
        f"```json\n{json.dumps(decision, ensure_ascii=False, indent=2)}\n```\n\n"
        "## Primary cells\n\n"
        f"{primary.to_markdown(index=False)}\n\n"
        "## Full filtration\n\n"
        f"{cells.to_markdown(index=False)}\n\n"
        "## Claim boundary\n\n"
        f"{config['claim_boundary']}\n"
    )
    args.report.write_text(report, encoding="utf-8")
    (args.output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
