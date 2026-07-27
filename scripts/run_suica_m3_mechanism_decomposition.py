#!/usr/bin/env python3
"""Run independent pairwise superposition and knockout mechanism attacks."""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
from scipy.stats import rankdata, spearmanr

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.m3_mechanism_audit import same_author_auc  # noqa: E402
from suica_core.m3_mechanism_decomposition import (  # noqa: E402
    MECHANISM_TO_FAMILY,
    M3MechanismMixtureSpec,
    generate_m3_mechanism_pair_world,
)
from suica_core.m3_mechanism_stress_estimator import (  # noqa: E402
    fit_m3_mechanism_stress,
)


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _partial_spearman(
    feature_distance: np.ndarray,
    own_distance: np.ndarray,
    other_distance: np.ndarray,
) -> float:
    x_values = rankdata(feature_distance)
    y_values = rankdata(own_distance)
    z_values = np.column_stack([
        np.ones(len(other_distance)),
        rankdata(other_distance),
    ])
    x_residual = x_values - z_values @ np.linalg.lstsq(
        z_values,
        x_values,
        rcond=None,
    )[0]
    y_residual = y_values - z_values @ np.linalg.lstsq(
        z_values,
        y_values,
        rcond=None,
    )[0]
    if np.std(x_residual) <= 1e-12 or np.std(y_residual) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(x_residual, y_residual)[0, 1])


def _geometry(feature: np.ndarray, parameter: np.ndarray) -> float:
    value = spearmanr(pdist(feature), pdist(parameter)).statistic
    return float(value)


def _decision(metrics: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    gates = config["discovery_gates"]
    aggregate = metrics.groupby(
        ["pair", "mechanism", "family"],
        as_index=False,
    ).agg(
        own_partial_geometry=("own_partial_geometry", "mean"),
        cross_partial_geometry=("cross_partial_geometry", "mean"),
        knockout_geometry=("knockout_geometry", "mean"),
        same_author_auc=("same_author_auc", "mean"),
    )
    aggregate["own_over_crosstalk"] = (
        aggregate["own_partial_geometry"]
        - aggregate["cross_partial_geometry"]
    )
    aggregate["pass"] = (
        (aggregate["own_partial_geometry"]
         >= gates["minimum_own_partial_geometry"])
        & (aggregate["own_over_crosstalk"]
           >= gates["minimum_own_over_crosstalk"])
        & (aggregate["knockout_geometry"].abs()
           <= gates["maximum_knockout_geometry_abs"])
        & (aggregate["same_author_auc"]
           >= gates["minimum_same_author_auc"])
    )
    mechanism = aggregate.groupby("mechanism", as_index=False).agg(
        pair_pass_fraction=("pass", "mean"),
        mean_own_partial_geometry=("own_partial_geometry", "mean"),
        mean_cross_partial_geometry=("cross_partial_geometry", "mean"),
        mean_knockout_geometry=("knockout_geometry", "mean"),
        mean_same_author_auc=("same_author_auc", "mean"),
    )
    checks = {
        row["mechanism"]: bool(
            row["pair_pass_fraction"]
            >= gates["minimum_pair_pass_fraction"]
        )
        for _, row in mechanism.iterrows()
    }
    return {
        "estimand_id": config["estimand_id"],
        "decision": (
            "M3_MECHANISM_PAIR_DECOMPOSITION_DISCOVERY_PASS"
            if all(checks.values())
            else "M3_MECHANISM_PAIR_DECOMPOSITION_DISCOVERY_PARTIAL"
        ),
        "checks": checks,
        "mechanism_summary": mechanism.to_dict(orient="records"),
        "pair_summary": aggregate.to_dict(orient="records"),
        "claim_boundary": (
            "Independent pairwise synthetic decomposition only; no complete "
            "basis, human-text, or psychological construct claim."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "m3_mechanism_decomposition_discovery.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "m3_mechanism_decomposition",
    )
    args = parser.parse_args()
    config = _load(args.config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    pairs = list(itertools.combinations(config["mechanisms"], 2))
    rows: list[dict[str, Any]] = []
    for repetition in range(config["repetitions"]):
        for pair_index, pair in enumerate(pairs):
            seed = (
                int(config["seed"])
                + repetition * 10_007
                + pair_index * 101
            )
            observed, truth = generate_m3_mechanism_pair_world(
                pair=pair,
                spec=M3MechanismMixtureSpec(**config["base_spec"]),
                seed=seed,
            )
            full = fit_m3_mechanism_stress(observed, seed=seed + 701)
            truth_distance = {
                name: pdist(parameter)
                for name, parameter in truth.author_parameters.items()
            }
            for mechanism, other in (pair, pair[::-1]):
                family = MECHANISM_TO_FAMILY[mechanism]
                feature = full.train_features[family]
                feature_distance = pdist(feature)
                knockout_observed, _ = generate_m3_mechanism_pair_world(
                    pair=pair,
                    spec=M3MechanismMixtureSpec(**config["base_spec"]),
                    seed=seed,
                    disabled=frozenset({mechanism}),
                )
                knockout = fit_m3_mechanism_stress(
                    knockout_observed,
                    seed=seed + 701,
                )
                rows.append({
                    "repetition": repetition,
                    "seed": seed,
                    "pair": "+".join(pair),
                    "mechanism": mechanism,
                    "other_mechanism": other,
                    "family": family,
                    "own_partial_geometry": _partial_spearman(
                        feature_distance,
                        truth_distance[mechanism],
                        truth_distance[other],
                    ),
                    "cross_partial_geometry": _partial_spearman(
                        feature_distance,
                        truth_distance[other],
                        truth_distance[mechanism],
                    ),
                    "knockout_geometry": _geometry(
                        knockout.train_features[family],
                        truth.author_parameters[mechanism],
                    ),
                    "same_author_auc": same_author_auc(
                        full.train_features[family],
                        full.test_features[family],
                    ),
                })
    metrics = pd.DataFrame(rows)
    decision = _decision(metrics, config)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    pd.DataFrame(decision["mechanism_summary"]).to_csv(
        args.output_dir / "mechanism_summary.csv",
        index=False,
    )
    pd.DataFrame(decision["pair_summary"]).to_csv(
        args.output_dir / "pair_summary.csv",
        index=False,
    )
    with (args.output_dir / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    with (args.output_dir / "config.snapshot.json").open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(config, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    summary = pd.DataFrame(decision["mechanism_summary"])
    pair_summary = pd.DataFrame(decision["pair_summary"])
    report = f"""# SUICA M3 Independent Pairwise Mechanism Decomposition

Decision: `{decision["decision"]}`

## Mechanism summary

{summary.to_markdown(index=False)}

## Pairwise detail

{pair_summary.to_markdown(index=False)}

## Interpretation boundary

Independent author parameters, partial pairwise geometry, and counterfactual
knockout test whether an estimator tracks its own mechanism rather than merely
reidentifying authors from a correlated composite code. A pass remains a
synthetic decomposition result, not evidence of completeness, human-text
persistence, or personality meaning.
"""
    (
        ROOT
        / "reports"
        / "SUICA_M3_MECHANISM_PAIR_DECOMPOSITION_DISCOVERY.md"
    ).write_text(report, encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
