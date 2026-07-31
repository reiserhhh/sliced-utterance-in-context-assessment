#!/usr/bin/env python3
"""Decompose the frozen M4-C.3.3 information-frontier result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NUMERIC_COLUMNS = (
    "baseline_geometry",
    "oracle_swap_geometry",
    "creation_headroom",
    "fisher_geometry",
    "fisher_gain",
    "recovered_headroom",
    "permutation_gain",
    "selected_hazard_loss",
    "fisher_hazard_loss",
    "hazard_relative_degradation",
    "fisher_minimum_information",
)


def _cluster_interval(
    values: np.ndarray,
    *,
    seed: int,
    repetitions: int = 20_000,
) -> tuple[float, float]:
    """Return a repetition-cluster percentile interval for a mean."""
    vector = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(
        vector,
        size=(repetitions, len(vector)),
        replace=True,
    )
    means = np.mean(draws, axis=1)
    lower, upper = np.quantile(means, [0.025, 0.975])
    return float(lower), float(upper)


def _paired_repetition_values(
    frame: pd.DataFrame,
    column: str,
    *,
    high: tuple[int, str],
    low: tuple[int, str],
    ratio: bool = False,
) -> np.ndarray:
    """Pair arms within world, then average each contrast by repetition."""
    pivot = frame.pivot_table(
        index=["repetition", "world"],
        columns=["k", "intervention"],
        values=column,
        aggfunc="mean",
    )
    high_values = pivot[high].to_numpy(dtype=float)
    low_values = pivot[low].to_numpy(dtype=float)
    values = (
        high_values / np.maximum(low_values, 1e-12)
        if ratio
        else high_values - low_values
    )
    repeated = pd.DataFrame(
        {
            "repetition": pivot.index.get_level_values("repetition"),
            "value": values,
        }
    )
    return (
        repeated.groupby("repetition", sort=True)["value"]
        .mean()
        .to_numpy(dtype=float)
    )


def _contrast_rows(
    frame: pd.DataFrame,
    *,
    seed: int,
) -> pd.DataFrame:
    definitions = (
        ("total_K8exc_minus_K1pass", (8, "excitation"), (1, "passive")),
        ("opportunity_passive_K8_minus_K1", (8, "passive"), (1, "passive")),
        (
            "opportunity_excitation_K8_minus_K1",
            (8, "excitation"),
            (1, "excitation"),
        ),
        ("excitation_increment_K1", (1, "excitation"), (1, "passive")),
        ("excitation_increment_K2", (2, "excitation"), (2, "passive")),
        ("excitation_increment_K4", (4, "excitation"), (4, "passive")),
        ("excitation_increment_K8", (8, "excitation"), (8, "passive")),
    )
    rows: list[dict[str, Any]] = []
    for index, (name, high, low) in enumerate(definitions):
        geometry = _paired_repetition_values(
            frame,
            "fisher_geometry",
            high=high,
            low=low,
        )
        information = _paired_repetition_values(
            frame,
            "fisher_minimum_information",
            high=high,
            low=low,
            ratio=True,
        )
        lower, upper = _cluster_interval(
            geometry,
            seed=seed + index,
        )
        rows.append(
            {
                "contrast": name,
                "high_k": high[0],
                "high_intervention": high[1],
                "low_k": low[0],
                "low_intervention": low[1],
                "geometry_delta": float(np.mean(geometry)),
                "geometry_ci_lower": lower,
                "geometry_ci_upper": upper,
                "information_ratio": float(np.mean(information)),
                "positive_repetitions": int(np.sum(geometry > 0)),
                "total_repetitions": int(len(geometry)),
            }
        )
    return pd.DataFrame(rows)


def _world_rows(frame: pd.DataFrame) -> pd.DataFrame:
    low = frame[
        (frame["k"] == 1) & (frame["intervention"] == "passive")
    ]
    high = frame[
        (frame["k"] == 8) & (frame["intervention"] == "excitation")
    ]
    rows = []
    for world in sorted(frame["world"].unique()):
        low_world = low[low["world"] == world]
        high_world = high[high["world"] == world]
        gain = float(high_world["fisher_gain"].mean())
        headroom = float(high_world["creation_headroom"].mean())
        rows.append(
            {
                "world": world,
                "low_geometry": float(low_world["fisher_geometry"].mean()),
                "high_geometry": float(high_world["fisher_geometry"].mean()),
                "endpoint_delta": float(
                    high_world["fisher_geometry"].mean()
                    - low_world["fisher_geometry"].mean()
                ),
                "high_fisher_gain": gain,
                "high_creation_headroom": headroom,
                "high_recovered_headroom": (
                    gain / headroom if headroom > 1e-12 else float("nan")
                ),
            }
        )
    return pd.DataFrame(rows)


def _repetition_rows(frame: pd.DataFrame) -> pd.DataFrame:
    high = frame[
        (frame["k"] == 8) & (frame["intervention"] == "excitation")
    ]
    repeated = (
        high.groupby("repetition", sort=True)
        .agg(
            high_geometry=("fisher_geometry", "mean"),
            high_gain=("fisher_gain", "mean"),
            high_creation_headroom=("creation_headroom", "mean"),
        )
        .reset_index()
    )
    repeated["high_recovered_headroom"] = (
        repeated["high_gain"] / repeated["high_creation_headroom"]
    )
    repeated["frozen_repetition_gate"] = (
        (repeated["high_gain"] > 0)
        & (repeated["high_geometry"] >= 0.70)
    )
    return repeated


def _arm_rows(frame: pd.DataFrame) -> pd.DataFrame:
    return (
        frame.groupby(["k", "intervention"], sort=True)
        .agg(
            fisher_minimum_information=(
                "fisher_minimum_information",
                "mean",
            ),
            baseline_geometry=("baseline_geometry", "mean"),
            oracle_swap_geometry=("oracle_swap_geometry", "mean"),
            creation_headroom=("creation_headroom", "mean"),
            fisher_geometry=("fisher_geometry", "mean"),
            fisher_gain=("fisher_gain", "mean"),
            hazard_relative_degradation=(
                "hazard_relative_degradation",
                "mean",
            ),
        )
        .reset_index()
    )


def _report(
    *,
    contrasts: pd.DataFrame,
    worlds: pd.DataFrame,
    repetitions: pd.DataFrame,
    arms: pd.DataFrame,
) -> str:
    opportunity = contrasts[
        contrasts["contrast"] == "opportunity_passive_K8_minus_K1"
    ].iloc[0]
    excitation = contrasts[
        contrasts["contrast"] == "excitation_increment_K8"
    ].iloc[0]
    return f"""# SUICA M4-C.3.3 Mechanism Decomposition

## Status

Post-hoc decomposition of the frozen C3.3 endpoint. It does not alter the
preregistered `M4_C33_NO_GO_INFORMATION_LIMIT` decision.

## Main decomposition

- Passive opportunity, `K=8 - K=1`: geometry delta
  `{opportunity["geometry_delta"]:.4f}`
  [{opportunity["geometry_ci_lower"]:.4f},
  {opportunity["geometry_ci_upper"]:.4f}].
- Orthogonal excitation at `K=8`: geometry delta
  `{excitation["geometry_delta"]:.4f}`
  [{excitation["geometry_ci_lower"]:.4f},
  {excitation["geometry_ci_upper"]:.4f}].
- Most endpoint improvement therefore comes from repeated observable
  opportunity. Excitation contributes a smaller conditional increment.
- The arm mean peaks at `K=4 excitation`; the `K=8` arm does not improve
  further, so the observed frontier is saturating rather than unlimited.

## Arm means

{arms.to_markdown(index=False, floatfmt=".4f")}

## Paired contrasts

{contrasts.to_markdown(index=False, floatfmt=".4f")}

## World heterogeneity

{worlds.to_markdown(index=False, floatfmt=".4f")}

## Repetition endpoints

{repetitions.to_markdown(index=False, floatfmt=".4f")}

## Interpretation boundary

Observable creation information is causally useful in these synthetic worlds,
but it is not sufficient for uniform loop reconstruction. The residual is
mechanism-dependent: `history_gated_ecology` remains negative while
`selection_creation_compensation` recovers most oracle headroom. The next
experiment should therefore target heterogeneous creation laws or latent
history state, not merely increase `K` or replace the embedding/kernel.

This is a synthetic mechanism result. It is not personality validity, natural
text validity, or authorization for M4-D.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metrics",
        type=Path,
        default=(
            ROOT
            / "results"
            / "m4_opportunity_excitation_frontier"
            / "metrics.csv"
        ),
    )
    parser.add_argument("--bootstrap-seed", type=int, default=271828182)
    args = parser.parse_args()

    metrics = pd.read_csv(args.metrics, keep_default_na=False)
    for column in NUMERIC_COLUMNS:
        metrics[column] = pd.to_numeric(metrics[column], errors="coerce")
    frame = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == "main")
    ].copy()

    contrasts = _contrast_rows(frame, seed=args.bootstrap_seed)
    worlds = _world_rows(frame)
    repetitions = _repetition_rows(frame)
    arms = _arm_rows(frame)

    output = args.metrics.parent
    contrasts.to_csv(output / "mechanism_contrasts.csv", index=False)
    worlds.to_csv(output / "world_heterogeneity.csv", index=False)
    repetitions.to_csv(output / "repetition_endpoints.csv", index=False)
    arms.to_csv(output / "arm_summary.csv", index=False)

    peak = arms.loc[arms["fisher_geometry"].idxmax()]
    summary = {
        "status": "POST_HOC_DECOMPOSITION",
        "frozen_decision": "M4_C33_NO_GO_INFORMATION_LIMIT",
        "peak_arm": {
            "k": int(peak["k"]),
            "intervention": str(peak["intervention"]),
            "geometry": float(peak["fisher_geometry"]),
        },
        "contrasts": contrasts.to_dict(orient="records"),
        "claim_boundary": (
            "Synthetic mechanism decomposition only; no personality, natural "
            "text, or M4-D claim."
        ),
    }
    with (output / "mechanism_decomposition.json").open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")

    report_path = ROOT / "reports" / "SUICA_M4_C33_MECHANISM_DECOMPOSITION.md"
    report_path.write_text(
        _report(
            contrasts=contrasts,
            worlds=worlds,
            repetitions=repetitions,
            arms=arms,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
