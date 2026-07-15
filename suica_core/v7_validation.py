"""Refusing validators for V7 fixed/free and external-anchor protocols.

These functions do not fit psychological models.  They only establish whether
a proposed dataset has the logged design information needed to estimate the
separate objects in the V7 design: free-choice opportunity `q` and fixed
condition response `B`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta


def sha256_path(path: str | Path) -> str:
    """Return the SHA-256 digest of a file without exposing its content."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _bool_series(values: pd.Series) -> pd.Series:
    """Parse common boolean encodings while leaving unknown values missing."""
    mapping = {
        "true": True, "1": True, "yes": True, "y": True,
        "false": False, "0": False, "no": False, "n": False,
    }
    return values.map(lambda value: mapping.get(str(value).strip().lower(), np.nan))


def validate_fixed_free_observations(frame: pd.DataFrame) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    """Validate fixed/free design eligibility and compute only licensed q summaries.

    Required free-phase rows are exposure records, not merely observed text:
    every row represents an offered condition and states whether it was chosen.
    Fixed rows need independently randomized condition assignments and at least
    two sessions per person-condition before a response operator can be fitted.
    """
    required = {"participant_id", "phase", "session_id", "condition_id"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        return {
            "status": "REFUSE_SCHEMA_MISSING_COLUMNS",
            "missing_columns": missing,
            "q_status": "REFUSE_Q_OPPORTUNITY_UNOBSERVED",
            "b_status": "REFUSE_B_INSUFFICIENT_INDEPENDENT_REPLICATION",
        }, pd.DataFrame(), pd.DataFrame()
    data = frame.copy()
    data["participant_id"] = data["participant_id"].astype(str)
    data["phase"] = data["phase"].astype(str).str.lower().str.strip()
    invalid_phase = sorted(set(data.loc[~data["phase"].isin({"free", "fixed"}), "phase"]))
    if invalid_phase:
        return {
            "status": "REFUSE_SCHEMA_INVALID_PHASE",
            "invalid_phase": invalid_phase,
            "q_status": "REFUSE_Q_OPPORTUNITY_UNOBSERVED",
            "b_status": "REFUSE_B_INSUFFICIENT_INDEPENDENT_REPLICATION",
        }, pd.DataFrame(), pd.DataFrame()

    free = data.loc[data["phase"].eq("free")].copy()
    fixed = data.loc[data["phase"].eq("fixed")].copy()
    q_required = {"opportunity_id", "selected", "exposure_recorded"}
    q_missing = sorted(q_required.difference(free.columns)) if not free.empty else sorted(q_required)
    q_table = pd.DataFrame()
    if q_missing:
        q_status = "REFUSE_Q_OPPORTUNITY_UNOBSERVED"
    else:
        exposure = _bool_series(free["exposure_recorded"])
        selected = _bool_series(free["selected"])
        valid = exposure.eq(True) & selected.notna() & free["opportunity_id"].notna()
        if not valid.any():
            q_status = "REFUSE_Q_OPPORTUNITY_UNOBSERVED"
        else:
            grouped = free.loc[valid].assign(_selected=selected.loc[valid].astype(int)).groupby(
                ["participant_id", "condition_id"], observed=True
            )["_selected"].agg(["sum", "count"]).reset_index()
            grouped = grouped.rename(columns={"sum": "n_selected", "count": "n_exposed"})
            grouped["q_jeffreys_mean"] = (grouped["n_selected"] + 0.5) / (grouped["n_exposed"] + 1.0)
            grouped["q_ci_low"] = beta.ppf(0.025, grouped["n_selected"] + 0.5, grouped["n_exposed"] - grouped["n_selected"] + 0.5)
            grouped["q_ci_high"] = beta.ppf(0.975, grouped["n_selected"] + 0.5, grouped["n_exposed"] - grouped["n_selected"] + 0.5)
            q_table = grouped
            q_status = "Q_OPPORTUNITY_PROFILE_ESTIMABLE"

    b_rows: list[dict[str, Any]] = []
    if fixed.empty:
        b_status = "REFUSE_B_INSUFFICIENT_INDEPENDENT_REPLICATION"
    elif "assignment_randomized" not in fixed:
        b_status = "REFUSE_B_NONRANDOMIZED_ASSIGNMENT"
    else:
        randomized = _bool_series(fixed["assignment_randomized"])
        if not randomized.eq(True).all():
            b_status = "REFUSE_B_NONRANDOMIZED_ASSIGNMENT"
        else:
            for participant, group in fixed.groupby("participant_id", observed=True, sort=True):
                sessions = group.groupby("condition_id", observed=True)["session_id"].nunique()
                n_conditions = int(group["condition_id"].nunique())
                design = pd.get_dummies(group["condition_id"].astype(str), dtype=float).to_numpy(float)
                rank = int(np.linalg.matrix_rank(design)) if len(design) else 0
                condition_number = float(np.linalg.cond(design)) if rank else float("inf")
                residual_df = int(len(group) - rank)
                b_rows.append({
                    "participant_id": str(participant),
                    "n_fixed_observations": int(len(group)),
                    "n_conditions": n_conditions,
                    "min_sessions_per_condition": int(sessions.min()) if len(sessions) else 0,
                    "design_rank": rank,
                    "design_condition_number": condition_number,
                    "residual_df": residual_df,
                    "b_eligible": bool(len(sessions) and sessions.min() >= 2 and residual_df > 0 and rank == n_conditions),
                })
            b_table = pd.DataFrame(b_rows)
            b_status = "B_RESPONSE_OPERATOR_ESTIMABLE" if bool(b_table["b_eligible"].all()) and not b_table.empty else "REFUSE_B_INSUFFICIENT_INDEPENDENT_REPLICATION"
    b_table = pd.DataFrame(b_rows)
    status = "FIXED_FREE_DESIGN_READY_FOR_FUTURE_ESTIMATION" if q_status == "Q_OPPORTUNITY_PROFILE_ESTIMABLE" and b_status == "B_RESPONSE_OPERATOR_ESTIMABLE" else "FIXED_FREE_DESIGN_REFUSED_OR_PARTIAL"
    return {
        "status": status,
        "q_status": q_status,
        "b_status": b_status,
        "n_rows": int(len(data)),
        "n_free_rows": int(len(free)),
        "n_fixed_rows": int(len(fixed)),
        "n_participants": int(data["participant_id"].nunique()),
        "q_missing_columns": q_missing,
    }, q_table, b_table


def validate_external_anchor_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the no-label-leakage preconditions for an anchor analysis."""
    required = {
        "bundle_path", "bundle_sha256", "pre_freeze_label_access",
        "score_cohort_id", "anchor_cohort_id", "cohort_overlap_count",
        "multiplicity_plan", "hypotheses",
    }
    missing = sorted(required.difference(payload))
    if missing:
        return {"status": "REFUSE_MULTIPLICITY_PLAN", "missing_fields": missing}
    if bool(payload["pre_freeze_label_access"]):
        return {"status": "REFUSE_PRE_FREEZE_LABEL_ACCESS"}
    bundle_path = Path(str(payload["bundle_path"]))
    if not bundle_path.exists() or sha256_path(bundle_path) != str(payload["bundle_sha256"]):
        return {"status": "REFUSE_BUNDLE_HASH_MISMATCH"}
    if str(payload["score_cohort_id"]) == str(payload["anchor_cohort_id"]) or int(payload["cohort_overlap_count"]) > 0:
        return {"status": "REFUSE_ANCHOR_COHORT_OVERLAP"}
    if not isinstance(payload["multiplicity_plan"], dict) or not payload["multiplicity_plan"] or not isinstance(payload["hypotheses"], list) or not payload["hypotheses"]:
        return {"status": "REFUSE_MULTIPLICITY_PLAN"}
    return {
        "status": "EXTERNAL_ANCHOR_PROTOCOL_READY",
        "n_hypotheses": len(payload["hypotheses"]),
        "bundle_sha256": str(payload["bundle_sha256"]),
        "claim_boundary": "Protocol eligibility only. No label association is computed by this validator.",
    }


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load an external-anchor manifest as a JSON object."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("External-anchor manifest must be a JSON object.")
    return payload
