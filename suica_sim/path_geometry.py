"""A phase-coupled path world that defeats mean/covariance/linear-lag summaries.

Every author has the same marginal state distribution and zero linear lag
covariance.  Authors differ only in a nonlinear conditional transition phase:
``W[t + 1] = 2 * Z[t] + theta_u + noise (mod 2*pi)``.  A characteristic
conditional-output feature can recover the phase, while static and linear
transition summaries cannot in the population.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PhaseCoupledSpec:
    """Parameters for a replicated nonlinear path simulation."""

    n_authors: int = 80
    runs_per_half: int = 4
    points_per_run: int = 20
    kappa: float = 8.0


def simulate_phase_coupled_world(spec: PhaseCoupledSpec, *, seed: int) -> pd.DataFrame:
    """Generate two independent run collections per author from the same phase law."""
    if spec.points_per_run < 4:
        raise ValueError("points_per_run must be at least four")
    rng = np.random.default_rng(seed)
    phases = rng.uniform(0.0, 2.0 * np.pi, size=spec.n_authors)
    rows: list[dict[str, float | int | str]] = []
    for author, phase in enumerate(phases):
        for half in ("early", "late"):
            for run in range(spec.runs_per_half):
                z = rng.uniform(0.0, 2.0 * np.pi, size=spec.points_per_run)
                w = np.empty(spec.points_per_run)
                w[0] = rng.uniform(0.0, 2.0 * np.pi)
                w[1:] = (2.0 * z[:-1] + phase + rng.vonmises(0.0, spec.kappa,
                                                              size=spec.points_per_run - 1)) % (2.0 * np.pi)
                for position, (z_value, w_value) in enumerate(zip(z, w)):
                    rows.append({
                        "author": author,
                        "half": half,
                        "run": run,
                        "position": position,
                        "z": float(z_value),
                        "w": float(w_value),
                    })
    return pd.DataFrame(rows)


def _endpoint_preserving_indices(length: int, rng: np.random.Generator) -> np.ndarray:
    indices = np.arange(length)
    indices[1:-1] = indices[1:-1][rng.permutation(length - 2)]
    return indices


def _author_half_run_features(
    frame: pd.DataFrame,
    *,
    shuffle_interior: bool,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return linear and nonlinear per-run summaries from complete simulated paths."""
    rng = np.random.default_rng(seed)
    linear_rows: list[dict[str, float | int | str]] = []
    witness_rows: list[dict[str, float | int | str]] = []
    for (author, half, run), group in frame.groupby(["author", "half", "run"], observed=True, sort=False):
        group = group.sort_values("position").reset_index(drop=True)
        if shuffle_interior:
            group = group.iloc[_endpoint_preserving_indices(len(group), rng)].reset_index(drop=True)
        state = np.column_stack([
            np.cos(group["z"]), np.sin(group["z"]), np.cos(group["w"]), np.sin(group["w"]),
        ])
        lag = state[1:].T @ state[:-1] / (len(state) - 1)
        mean = state.mean(axis=0)
        centered = state - mean
        covariance = centered.T @ centered / len(state)
        linear_row: dict[str, float | int | str] = {"author": author, "half": half, "run": run}
        linear_row.update({f"mean_{index:02d}": float(value) for index, value in enumerate(mean)})
        linear_row.update({f"cov_{i:02d}_{j:02d}": float(covariance[i, j])
                           for i in range(4) for j in range(4)})
        linear_row.update({f"lag_{i:02d}_{j:02d}": float(lag[i, j])
                           for i in range(4) for j in range(4)})
        linear_rows.append(linear_row)
        phase = group["w"].to_numpy(float)[1:] - 2.0 * group["z"].to_numpy(float)[:-1]
        witness = np.exp(1j * phase).mean()
        witness_rows.append({"author": author, "half": half, "run": run,
                             "phase_real": float(witness.real), "phase_imag": float(witness.imag)})
    return pd.DataFrame(linear_rows), pd.DataFrame(witness_rows)


def aggregate_author_halves(frame: pd.DataFrame, prefix: str | None) -> tuple[np.ndarray, np.ndarray, list[int]]:
    """Equal-run aggregate a feature family and align early/late authors."""
    features = [column for column in frame if column not in {"author", "half", "run"}
                and (prefix is None or column.startswith(prefix))]
    grouped = frame.groupby(["author", "half"], observed=True)[features].mean().reset_index()
    early = grouped.loc[grouped["half"].eq("early")].set_index("author")
    late = grouped.loc[grouped["half"].eq("late")].set_index("author")
    authors = sorted(set(early.index) & set(late.index))
    return early.loc[authors, features].to_numpy(float), late.loc[authors, features].to_numpy(float), authors


def own_vs_stranger_auc(early: np.ndarray, late: np.ndarray) -> float:
    """AUC for paired author closeness against all mismatched author pairs."""
    from sklearn.metrics import roc_auc_score

    distance = np.linalg.norm(early[:, None, :] - late[None, :, :], axis=2)
    own = np.diag(distance)
    stranger = distance[~np.eye(len(distance), dtype=bool)]
    return float(roc_auc_score(np.r_[np.ones(len(own)), np.zeros(len(stranger))],
                               -np.r_[own, stranger]))


def evaluate_phase_coupled_world(spec: PhaseCoupledSpec, *, seed: int) -> dict[str, float]:
    """Evaluate the linear-null and conditional-witness estimands on one world."""
    world = simulate_phase_coupled_world(spec, seed=seed)
    linear, witness = _author_half_run_features(world, shuffle_interior=False, seed=seed + 1)
    _, shuffled_witness = _author_half_run_features(world, shuffle_interior=True, seed=seed + 2)
    # Include covariance and lag summaries in the same explicitly linear family.
    linear_early, linear_late, _ = aggregate_author_halves(linear, None)
    witness_early, witness_late, _ = aggregate_author_halves(witness, "phase_")
    shuffled_early, shuffled_late, _ = aggregate_author_halves(shuffled_witness, "phase_")
    return {
        "linear_summary_auc": own_vs_stranger_auc(linear_early, linear_late),
        "conditional_phase_witness_auc": own_vs_stranger_auc(witness_early, witness_late),
        "shuffled_phase_witness_auc": own_vs_stranger_auc(shuffled_early, shuffled_late),
    }
