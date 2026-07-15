"""Text-blind construction of within-condition technical replicas.

These helpers split already selected text units into repeatable numerical views
without changing authors or condition support. They measure score sensitivity
to slice boundaries, not repeated-occasion or trait stability.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def assign_within_condition_replicates(units: pd.DataFrame, *, scheme: str) -> pd.DataFrame:
    """Assign two replicas within each user-half-condition time-ordered cell.

    Single-observation cells are excluded because they cannot provide both
    technical replicas. ``interleaved`` alternates observations; ``blocked``
    separates the earlier and later portions of each condition cell.
    """
    required = {"user_id", "half", "condition", "created_utc", "order"}
    missing = required - set(units.columns)
    if missing:
        raise ValueError(f"missing unit columns: {sorted(missing)}")
    if scheme not in {"interleaved", "blocked"}:
        raise ValueError("scheme must be 'interleaved' or 'blocked'")
    work = units.copy()
    work["technical_replica"] = -1
    for _, group in work.groupby(["user_id", "half", "condition"], observed=True, sort=False):
        ordered = group.sort_values(["created_utc", "order"], kind="stable")
        n = len(ordered)
        if n < 2:
            continue
        if scheme == "interleaved":
            assignment = np.arange(n, dtype=int) % 2
        else:
            assignment = (np.arange(n, dtype=int) >= n // 2).astype(int)
        work.loc[ordered.index, "technical_replica"] = assignment
    return work.loc[work["technical_replica"] >= 0].copy()


def aggregate_static_replicates(
    units: pd.DataFrame,
    residual: np.ndarray,
) -> pd.DataFrame:
    """Aggregate residual coordinates into user-half-technical-replica points."""
    residual = np.asarray(residual, dtype=float)
    if len(units) != len(residual):
        raise ValueError("residual rows must align with units")
    if "technical_replica" not in units:
        raise ValueError("technical_replica assignment is required")
    work = units.copy()
    columns = [f"static_{index:02d}" for index in range(residual.shape[1])]
    work[columns] = residual
    rows: list[dict[str, float | str | int]] = []
    groups = work.loc[work["technical_replica"] >= 0].groupby(
        ["user_id", "half", "technical_replica"], observed=True, sort=False,
    )
    for (user, half, replica), group in groups:
        by_condition = group.groupby("condition", observed=True)[columns].mean()
        if by_condition.empty:
            continue
        values = by_condition.mean(axis=0).to_numpy(float)
        rows.append({
            "user_id": str(user),
            "half": str(half),
            "technical_replica": int(replica),
            "n_comments": int(len(group)),
            "n_conditions": int(len(by_condition)),
            **{column: values[index] for index, column in enumerate(columns)},
        })
    return pd.DataFrame(rows)


def paired_replicate_matrices(
    frame: pd.DataFrame,
    *,
    half: str,
    discovery_users: set[str],
    confirmation_users: set[str],
) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """Return discovery-standardized, confirmation paired replica matrices."""
    columns = [column for column in frame if column.startswith("static_")]
    if not columns:
        raise ValueError("no static coordinate columns found")
    current = frame.loc[frame["half"].eq(half)]
    pivot = current.pivot(index="user_id", columns="technical_replica", values=columns)
    if 0 not in pivot.columns.get_level_values(1) or 1 not in pivot.columns.get_level_values(1):
        raise ValueError(f"missing technical replica for half={half}")
    left = pivot.xs(0, axis=1, level=1).dropna()
    right = pivot.xs(1, axis=1, level=1).dropna()
    users = sorted(set(left.index).intersection(right.index))
    discovery = [user for user in users if user in discovery_users]
    confirmation = [user for user in users if user in confirmation_users]
    if len(discovery) < 12 or len(confirmation) < 12:
        raise ValueError(f"insufficient paired technical replicas in half={half}")
    discovery_values = np.vstack([left.loc[discovery].to_numpy(float), right.loc[discovery].to_numpy(float)])
    center = discovery_values.mean(axis=0)
    scale = discovery_values.std(axis=0, ddof=1)
    scale[scale < 1e-8] = 1.0
    return (
        (left.loc[confirmation].to_numpy(float) - center) / scale,
        (right.loc[confirmation].to_numpy(float) - center) / scale,
        {"n_discovery": int(len(discovery)), "n_confirmation": int(len(confirmation))},
    )
