"""Same-author transport tests for opportunity-filtered relation geometry.

The experiment asks whether an author-by-author relation geometry that
replicates inside two contexts also survives between those contexts. It does
not align feature coordinates. Instead, it compares the complete relation
matrices induced by the same authors in contexts A and B.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from suica_core.v8_realtext_relation_field import stable_bucket
from suica_core.v8_residual_geometry_correspondence import (
    ResidualGeometrySpec,
    _alignment,
    _u_center_kernel,
    relational_matrices,
)


COMPONENTS = ("within_a", "within_b", "cross")


@dataclass(frozen=True)
class ContextTransportSpec:
    """Frozen inference budget and transport gates."""

    d0_null_draws: int = 999
    test_null_draws: int = 1999
    bootstrap_draws: int = 999
    nuisance_kernel_ridge: float = 0.10
    minimum_held_authors: int = 24
    normalized_cross_excess_floor: float = 0.25
    seed: int = 20260828

    def __post_init__(self) -> None:
        if min(self.d0_null_draws, self.test_null_draws) < 99:
            raise ValueError("Null budgets must be at least 99.")
        if self.bootstrap_draws < 99:
            raise ValueError("bootstrap_draws must be at least 99.")
        if self.nuisance_kernel_ridge <= 0:
            raise ValueError("nuisance_kernel_ridge must be positive.")
        if self.minimum_held_authors < 8:
            raise ValueError("minimum_held_authors must be at least eight.")
        if self.normalized_cross_excess_floor <= 0:
            raise ValueError(
                "normalized_cross_excess_floor must be positive."
            )


def _recenter_sample(matrix: np.ndarray, indices: np.ndarray) -> np.ndarray:
    sampled = np.asarray(matrix)[np.ix_(indices, indices)]
    return _u_center_kernel(sampled)


def _observed_components(
    a0: np.ndarray,
    a1: np.ndarray,
    b0: np.ndarray,
    b1: np.ndarray,
) -> dict[str, float]:
    return {
        "within_a": _alignment(a0, a1),
        "within_b": _alignment(b0, b1),
        "cross": 0.5 * (_alignment(a0, b1) + _alignment(a1, b0)),
    }


def _null_components(
    a0: np.ndarray,
    a1: np.ndarray,
    b0: np.ndarray,
    b1: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    """Break technical and cross-context author correspondence.

    The cross-context null applies one synchronous author permutation to both
    B relation matrices. This preserves B's internal geometry while breaking
    only the A-to-B author correspondence.
    """
    count = len(a0)
    result = {
        component: np.empty(draws, dtype=float)
        for component in COMPONENTS
    }
    for draw in range(draws):
        order_a = rng.permutation(count)
        order_b = rng.permutation(count)
        order_cross = rng.permutation(count)
        permuted_a1 = a1[np.ix_(order_a, order_a)]
        permuted_b1 = b1[np.ix_(order_b, order_b)]
        cross_b0 = b0[np.ix_(order_cross, order_cross)]
        cross_b1 = b1[np.ix_(order_cross, order_cross)]
        result["within_a"][draw] = _alignment(a0, permuted_a1)
        result["within_b"][draw] = _alignment(b0, permuted_b1)
        result["cross"][draw] = 0.5 * (
            _alignment(a0, cross_b1) + _alignment(a1, cross_b0)
        )
    return result


def _bootstrap_components(
    a0: np.ndarray,
    a1: np.ndarray,
    b0: np.ndarray,
    b1: np.ndarray,
    *,
    draws: int,
    rng: np.random.Generator,
) -> dict[str, np.ndarray]:
    count = len(a0)
    result = {
        component: np.empty(draws, dtype=float)
        for component in COMPONENTS
    }
    for draw in range(draws):
        indices = rng.integers(0, count, size=count)
        sampled = [
            _recenter_sample(matrix, indices)
            for matrix in (a0, a1, b0, b1)
        ]
        values = _observed_components(*sampled)
        for component, value in values.items():
            result[component][draw] = value
    return result


def _holm_family_adjustment(cells: pd.DataFrame) -> pd.DataFrame:
    """Holm-adjust exact cellwise permutation p-values.

    Context pairs overlap in authors and contexts. Combining independently
    generated pairwise null draws by draw index would therefore not form a
    valid joint maximum-T randomization distribution. Holm adjustment controls
    the family-wise error rate without requiring independence between cells.
    """
    output = cells.copy()
    output["holm_p"] = np.nan
    if output.empty:
        return output
    selected = output.loc[output["split"].isin(["D1", "D2"])]
    if selected.empty:
        return output
    ordered = selected.sort_values(
        ["raw_p", "cell_id"],
        kind="stable",
    )
    count = len(ordered)
    running = 0.0
    for rank, row in enumerate(ordered.itertuples(), start=1):
        adjusted = min(1.0, (count - rank + 1) * float(row.raw_p))
        running = max(running, adjusted)
        output.loc[output["cell_id"].eq(row.cell_id), "holm_p"] = running
    return output


def _conditional_bootstrap_lcb(
    excess: float,
    samples: np.ndarray,
) -> float:
    finite = np.asarray(samples, dtype=float)
    finite = finite[np.isfinite(finite)]
    if len(finite) < max(20, int(0.90 * len(samples))):
        return float("nan")
    return float(excess + np.quantile(finite - finite.mean(), 0.025))


def _normalized_cross_excess_summary(
    excess: dict[str, float],
    bootstrap: dict[str, np.ndarray],
) -> tuple[float, float]:
    denominator = np.sqrt(
        max(excess["within_a"], 0.0)
        * max(excess["within_b"], 0.0)
    )
    point = (
        float(excess["cross"] / denominator)
        if denominator > 1e-12
        else float("nan")
    )
    centered = {
        key: excess[key] + values - np.nanmean(values)
        for key, values in bootstrap.items()
    }
    denominator_samples = np.sqrt(
        np.maximum(centered["within_a"], 0.0)
        * np.maximum(centered["within_b"], 0.0)
    )
    ratios = np.divide(
        centered["cross"],
        denominator_samples,
        out=np.full_like(centered["cross"], np.nan),
        where=denominator_samples > 1e-12,
    )
    finite = ratios[np.isfinite(ratios)]
    lower = (
        float(np.quantile(finite, 0.025))
        if len(finite) >= max(20, int(0.90 * len(ratios)))
        else float("nan")
    )
    return point, lower


def _pair_status(
    cells: pd.DataFrame,
    pair_id: str,
    *,
    scales: tuple[float, ...],
    normalized_cross_excess_floor: float,
) -> tuple[str, list[float]]:
    selected = cells.loc[
        cells["pair_id"].eq(pair_id)
        & cells["split"].isin(["D1", "D2"])
    ]
    within_resolved = False
    transport_scales: list[float] = []
    for scale in scales:
        rows = selected.loc[np.isclose(selected["scale"], scale)]
        if len(rows) != 6:
            continue

        def passes(component: str) -> bool:
            part = rows.loc[rows["component"].eq(component)]
            return bool(
                len(part) == 2
                and part["excess"].gt(0).all()
                and part["holm_p"].le(0.05).all()
                and part["bootstrap_lcb"].gt(0).all()
            )

        within = passes("within_a") and passes("within_b")
        within_resolved = within_resolved or within
        cross = rows.loc[rows["component"].eq("cross")]
        retained = bool(
            len(cross) == 2
            and cross["normalized_cross_excess"]
            .ge(normalized_cross_excess_floor)
            .all()
            and cross["normalized_cross_excess_lcb"].gt(0).all()
        )
        if within and passes("cross") and retained:
            transport_scales.append(float(scale))
    if transport_scales:
        return "CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY", transport_scales
    if within_resolved:
        return "CROSS_CONTEXT_UNDERRESOLVED", []
    return "WITHIN_CONTEXT_GEOMETRY_UNDERRESOLVED", []


def evaluate_context_transport(
    pairs: dict[str, dict[str, Any]],
    *,
    spec: ContextTransportSpec,
) -> dict[str, Any]:
    """Evaluate same-author relation transport for registered context pairs."""
    rows: list[dict[str, Any]] = []
    pair_scales: dict[str, tuple[float, ...]] = {}
    for pair_id, panel in pairs.items():
        metadata = panel["metadata"].reset_index(drop=True)
        values_a = np.asarray(panel["values_a"], dtype=float)
        values_b = np.asarray(panel["values_b"], dtype=float)
        nuisance_a = np.asarray(panel["nuisance_a"], dtype=float)
        nuisance_b = np.asarray(panel["nuisance_b"], dtype=float)
        scales = tuple(map(float, panel["scales"]))
        pair_scales[pair_id] = scales
        for split in ("D0", "D1", "D2"):
            mask = metadata["split"].eq(split).to_numpy()
            count = int(mask.sum())
            if split != "D0" and count < spec.minimum_held_authors:
                continue
            if count < 8:
                continue
            context_a = np.repeat(str(panel["context_a"]), count)
            context_b = np.repeat(str(panel["context_b"]), count)
            relation_spec = ResidualGeometrySpec(
                d0_null_draws=spec.d0_null_draws,
                test_null_draws=spec.test_null_draws,
                bootstrap_draws=spec.bootstrap_draws,
                bandwidth_multipliers=scales,
                neighborhood_fractions=(0.10,),
                nuisance_kernel_ridge=spec.nuisance_kernel_ridge,
                minimum_context_authors=8,
                seed=spec.seed,
            )
            matrices_a = relational_matrices(
                values_a[mask],
                nuisance_a[mask],
                context_a,
                bandwidth=float(panel["bandwidth_a"]),
                spec=relation_spec,
            )
            matrices_b = relational_matrices(
                values_b[mask],
                nuisance_b[mask],
                context_b,
                bandwidth=float(panel["bandwidth_b"]),
                spec=relation_spec,
            )
            draws = (
                spec.d0_null_draws
                if split == "D0"
                else spec.test_null_draws
            )
            seed = (
                spec.seed
                + stable_bucket(
                    f"{pair_id}-{split}",
                    salt="v8-context-transport",
                    modulus=2**31 - 1,
                )
            )
            for scale in scales:
                metric = f"rbf_krc_{scale:g}"
                a0, a1 = matrices_a[metric]
                b0, b1 = matrices_b[metric]
                observed = _observed_components(a0, a1, b0, b1)
                null = _null_components(
                    a0,
                    a1,
                    b0,
                    b1,
                    draws=draws,
                    rng=np.random.default_rng(seed + int(scale * 10_000)),
                )
                bootstrap = (
                    {}
                    if split == "D0"
                    else _bootstrap_components(
                        a0,
                        a1,
                        b0,
                        b1,
                        draws=spec.bootstrap_draws,
                        rng=np.random.default_rng(
                            seed + int(scale * 10_000) + 1
                        ),
                    )
                )
                excess = {
                    component: float(
                        observed[component] - null[component].mean()
                    )
                    for component in COMPONENTS
                }
                normalized_cross_excess = (
                    (float("nan"), float("nan"))
                    if split == "D0"
                    else _normalized_cross_excess_summary(
                        excess,
                        bootstrap,
                    )
                )
                for component in COMPONENTS:
                    cell_id = (
                        f"{pair_id}::{split}::{scale:g}::{component}"
                    )
                    rows.append(
                        {
                            "cell_id": cell_id,
                            "pair_id": pair_id,
                            "corpus": str(panel["corpus"]),
                            "context_a": str(panel["context_a"]),
                            "context_b": str(panel["context_b"]),
                            "split": split,
                            "scale": float(scale),
                            "component": component,
                            "authors": count,
                            "observed": float(observed[component]),
                            "null_mean": float(null[component].mean()),
                            "excess": excess[component],
                            "raw_p": float(
                                (
                                    1
                                    + np.sum(
                                        null[component]
                                        >= observed[component]
                                    )
                                )
                                / (len(null[component]) + 1)
                            ),
                            "bootstrap_lcb": (
                                float("nan")
                                if split == "D0"
                                else _conditional_bootstrap_lcb(
                                    excess[component],
                                    bootstrap[component],
                                )
                            ),
                            "normalized_cross_excess": (
                                normalized_cross_excess[0]
                                if component == "cross"
                                else float("nan")
                            ),
                            "normalized_cross_excess_lcb": (
                                normalized_cross_excess[1]
                                if component == "cross"
                                else float("nan")
                            ),
                        }
                    )
    cells = _holm_family_adjustment(pd.DataFrame(rows))
    status_rows = []
    for pair_id, scales in pair_scales.items():
        status, passed_scales = _pair_status(
            cells,
            pair_id,
            scales=scales,
            normalized_cross_excess_floor=(
                spec.normalized_cross_excess_floor
            ),
        )
        status_rows.append(
            {
                "pair_id": pair_id,
                "status": status,
                "transport_scales": "|".join(map(str, passed_scales)),
            }
        )
    status = pd.DataFrame(status_rows)
    transportable = status["status"].eq(
        "CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY"
    )
    if transportable.all() and len(status):
        overall = "CONTEXT_TRANSPORTABLE_RELATION_GEOMETRY"
    elif transportable.any():
        overall = "PARTIAL_CONTEXT_TRANSPORT"
    elif status["status"].eq("CROSS_CONTEXT_UNDERRESOLVED").any():
        overall = "CROSS_CONTEXT_UNDERRESOLVED"
    else:
        overall = "CONTEXT_TRANSPORT_UNDERRESOLVED"
    return {
        "overall_status": overall,
        "cells": cells,
        "pair_status": status,
    }
