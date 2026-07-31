"""Applicability profiles and frozen fallback routing for M4-C.3.5-R2C."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist, pdist, squareform

from .m4_condition_manifold_contracts import M4ConditionObserved
from .m4_response_safe_rcca_chart import M4RCCAChartTransform


HELDOUT_ROLES = (
    "reference_selection",
    "mechanism_calibration",
    "mechanism_selection",
    "mechanism_evaluation",
)


@dataclass(frozen=True)
class M4CoverageProfile:
    """Continuous pre-response applicability evidence for one RCCA chart."""

    threshold: float
    role_coverage: dict[str, float]
    minimum_coverage: float
    minimum_margin: float


def rcca_coverage_profile(
    chart: M4RCCAChartTransform,
    observed: M4ConditionObserved,
    *,
    minimum_coverage: float,
) -> M4CoverageProfile:
    """Reproduce the RCCA kNN support check and retain each role margin."""
    reference = chart.transform_prototypes(
        observed.reference_calibration.pre_context
    )[:, 1:]
    distances = squareform(pdist(reference))
    np.fill_diagonal(distances, np.inf)
    neighbors = min(3, len(reference) - 1)
    calibration_knn = np.partition(
        distances,
        neighbors - 1,
        axis=1,
    )[:, neighbors - 1]
    threshold = float(np.quantile(calibration_knn, 0.99))
    role_coverage = {}
    for role in HELDOUT_ROLES:
        values = chart.transform_prototypes(
            getattr(observed, role).pre_context
        )[:, 1:]
        current = cdist(values, reference)
        neighbor_index = min(neighbors - 1, current.shape[1] - 1)
        heldout_knn = np.partition(
            current,
            neighbor_index,
            axis=1,
        )[:, neighbor_index]
        role_coverage[role] = float(np.mean(heldout_knn <= threshold))
    minimum = float(min(role_coverage.values()))
    return M4CoverageProfile(
        threshold=threshold,
        role_coverage=role_coverage,
        minimum_coverage=minimum,
        minimum_margin=minimum - float(minimum_coverage),
    )


def add_frozen_policy_arm(
    metrics: pd.DataFrame,
    policy_cells: pd.DataFrame,
    *,
    policy_arm: str = "Pi",
) -> pd.DataFrame:
    """Append a policy arm that uses R when accepted and B0 otherwise."""
    required = {"repetition", "world", "accepted"}
    if not required.issubset(policy_cells.columns):
        raise ValueError("policy cells lack repetition/world/accepted")
    cells = policy_cells[["repetition", "world", "accepted"]].copy()
    if cells.duplicated(["repetition", "world"]).any():
        raise ValueError("policy cells are not unique")
    source = metrics.merge(
        cells,
        on=["repetition", "world"],
        how="left",
        validate="many_to_one",
    )
    if source["accepted"].isna().any():
        raise ValueError("metrics contain cells absent from the policy seal")
    selected = source[
        (
            source["accepted"].astype(bool)
            & source["arm"].eq("R")
        )
        | (
            ~source["accepted"].astype(bool)
            & source["arm"].eq("B0")
        )
    ].copy()
    selected["arm"] = policy_arm
    selected = selected.drop(columns=["accepted"])
    output = pd.concat([metrics, selected], ignore_index=True)
    keys = ["repetition", "world", "world_type", "view", "arm"]
    if output.duplicated(keys).any():
        raise ValueError("policy routing created duplicate metric cells")
    return output


def verify_frozen_policy_identity(
    metrics: pd.DataFrame,
    policy_cells: pd.DataFrame,
    *,
    tolerance: float = 0.0,
) -> float:
    """Return the maximum Pi-versus-selected-arm numeric discrepancy."""
    values = add_frozen_policy_arm(metrics, policy_cells)
    numeric = [
        column
        for column in metrics.columns
        if column not in {
            "repetition",
            "world",
            "world_type",
            "view",
            "arm",
            "rcca_refusal_reasons",
        }
        and pd.api.types.is_numeric_dtype(metrics[column])
    ]
    policy = values[values["arm"].eq("Pi")].merge(
        policy_cells[["repetition", "world", "accepted"]],
        on=["repetition", "world"],
        validate="many_to_one",
    )
    source = values[
        values["arm"].isin(["R", "B0"])
    ].copy()
    source = source.merge(
        policy_cells[["repetition", "world", "accepted"]],
        on=["repetition", "world"],
        validate="many_to_one",
    )
    source = source[
        (
            source["accepted"].astype(bool)
            & source["arm"].eq("R")
        )
        | (
            ~source["accepted"].astype(bool)
            & source["arm"].eq("B0")
        )
    ]
    joined = policy.merge(
        source,
        on=["repetition", "world", "world_type", "view"],
        suffixes=("_policy", "_source"),
        validate="one_to_one",
    )
    differences = [
        np.max(np.abs(
            joined[f"{column}_policy"].to_numpy(dtype=float)
            - joined[f"{column}_source"].to_numpy(dtype=float)
        ))
        for column in numeric
    ]
    maximum = float(max(differences, default=0.0))
    if maximum > tolerance:
        raise ValueError(
            f"frozen policy identity failed: {maximum} > {tolerance}"
        )
    return maximum
