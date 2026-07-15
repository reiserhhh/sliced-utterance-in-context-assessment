"""Design-first G-study/LST eligibility checks for future SUICA measurements.

The module deliberately does not estimate a human trait from historical text.
It asks a narrower question: does a repeated fixed-condition study contain the
crossed, versioned observations required before variance components or a
person-by-condition response operator can be estimated?
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


REQUIRED_REPEATED_COLUMNS = {
    "participant_id",
    "condition_id",
    "occasion_id",
    "session_id",
    "assignment_randomized",
    "scorer_hash",
    "operator_registry_version",
    "window_operator_id",
    "representation_hash",
    "component_id",
    "score_value",
}


def _as_bool(values: pd.Series) -> pd.Series:
    """Parse common boolean encodings while preserving missing values."""
    mapping = {
        "true": True, "1": True, "yes": True, "y": True,
        "false": False, "0": False, "no": False, "n": False,
    }
    return values.map(lambda value: mapping.get(str(value).strip().lower(), np.nan))


def _variance_component_plan() -> dict[str, Any]:
    """Return the declared G-study and latent-state-trait decompositions."""
    return {
        "g_study_model": (
            "Y[p,c,o,k] = mu[k] + P[p,k] + C[c,k] + O[o,k] + "
            "PC[p,c,k] + PO[p,o,k] + CO[c,o,k] + PCOe[p,c,o,k]"
        ),
        "lst_interpretation": (
            "P is a person-relative stable component only after repeated-occasion "
            "estimation; PC is person-by-condition specificity; PO is person-by-occasion "
            "state/occasion dependence; PCOe is residual/error."
        ),
        "required_facets": ["participant", "condition", "occasion", "component"],
        "not_estimated_here": [
            "variance_components",
            "generalizability_coefficient",
            "dependability_coefficient",
            "personality_or_clinical_construct",
        ],
        "claim_boundary": (
            "This is a design eligibility plan. A balanced table licenses a future "
            "variance-component fit; it does not establish trait stability."
        ),
    }


def _coverage_table(fixed: pd.DataFrame) -> pd.DataFrame:
    """Summarize cells without retaining participant identifiers in artifacts."""
    if fixed.empty:
        return pd.DataFrame(columns=["component_id", "n_participants", "n_conditions", "n_occasions", "expected_cells", "observed_cells", "coverage", "min_occasions_per_person_condition"])
    rows: list[dict[str, Any]] = []
    for component, group in fixed.groupby("component_id", observed=True, sort=True):
        participants = int(group["participant_id"].nunique())
        conditions = int(group["condition_id"].nunique())
        occasions = int(group["occasion_id"].nunique())
        cells = group[["participant_id", "condition_id", "occasion_id"]].drop_duplicates()
        expected = participants * conditions * occasions
        per_pc = cells.groupby(["participant_id", "condition_id"], observed=True)["occasion_id"].nunique()
        rows.append({
            "component_id": str(component),
            "n_participants": participants,
            "n_conditions": conditions,
            "n_occasions": occasions,
            "expected_cells": expected,
            "observed_cells": int(len(cells)),
            "coverage": float(len(cells) / expected) if expected else 0.0,
            "min_occasions_per_person_condition": int(per_pc.min()) if len(per_pc) else 0,
        })
    return pd.DataFrame(rows)


def validate_repeated_measurement_design(frame: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any]]:
    """Refuse incomplete repeated-measurement data before a G-study/LST fit.

    The required design is a randomized fixed-condition, repeated-occasion
    crossing. Scorer, representation and slice/window registry hashes are
    treated as measurement facets: version drift cannot be mistaken for a
    participant difference.
    """
    missing = sorted(REQUIRED_REPEATED_COLUMNS.difference(frame.columns))
    plan = _variance_component_plan()
    if missing:
        return {
            "status": "REFUSE_REPEATED_MEASUREMENT_SCHEMA",
            "missing_columns": missing,
            "claim_boundary": plan["claim_boundary"],
        }, pd.DataFrame(), plan

    data = frame.copy()
    for column in ("participant_id", "condition_id", "occasion_id", "session_id", "component_id"):
        data[column] = data[column].astype(str).str.strip()
    data["score_value"] = pd.to_numeric(data["score_value"], errors="coerce")
    if data["score_value"].isna().any():
        return {
            "status": "REFUSE_GSTUDY_NONNUMERIC_OR_MISSING_SCORE",
            "n_invalid_scores": int(data["score_value"].isna().sum()),
            "claim_boundary": plan["claim_boundary"],
        }, pd.DataFrame(), plan

    randomized = _as_bool(data["assignment_randomized"])
    if not randomized.eq(True).all():
        return {
            "status": "REFUSE_GSTUDY_NONRANDOMIZED_ASSIGNMENT",
            "n_nonrandomized_or_missing": int((~randomized.eq(True)).sum()),
            "claim_boundary": plan["claim_boundary"],
        }, pd.DataFrame(), plan

    version_columns = ("scorer_hash", "operator_registry_version", "window_operator_id", "representation_hash")
    version_counts = {column: int(data[column].dropna().astype(str).nunique()) for column in version_columns}
    missing_versions = [column for column in version_columns if data[column].isna().any() or version_counts[column] != 1]
    if missing_versions:
        return {
            "status": "REFUSE_GSTUDY_UNFROZEN_SCORING_RUNTIME",
            "unfrozen_or_missing_version_fields": missing_versions,
            "version_counts": version_counts,
            "claim_boundary": plan["claim_boundary"],
        }, pd.DataFrame(), plan

    duplicates = data.duplicated(["participant_id", "condition_id", "occasion_id", "component_id"], keep=False)
    if duplicates.any():
        return {
            "status": "REFUSE_GSTUDY_DUPLICATE_SCORE_CELLS",
            "n_duplicate_rows": int(duplicates.sum()),
            "claim_boundary": plan["claim_boundary"],
        }, pd.DataFrame(), plan

    coverage = _coverage_table(data)
    if coverage.empty or (coverage["n_participants"] < 2).any() or (coverage["n_conditions"] < 2).any() or (coverage["n_occasions"] < 2).any() or (coverage["min_occasions_per_person_condition"] < 2).any() or (coverage["coverage"] < 1.0).any():
        return {
            "status": "REFUSE_GSTUDY_INSUFFICIENT_CROSSED_REPLICATION",
            "coverage_requires_complete_participant_condition_occasion_crossing": True,
            "claim_boundary": plan["claim_boundary"],
        }, coverage, plan

    return {
        "status": "REPEATED_MEASUREMENT_DESIGN_READY_FOR_GSTUDY_LST",
        "n_rows": int(len(data)),
        "n_components": int(data["component_id"].nunique()),
        "n_participants": int(data["participant_id"].nunique()),
        "n_conditions": int(data["condition_id"].nunique()),
        "n_occasions": int(data["occasion_id"].nunique()),
        "runtime_versions": version_counts,
        "claim_boundary": plan["claim_boundary"],
    }, coverage, plan
