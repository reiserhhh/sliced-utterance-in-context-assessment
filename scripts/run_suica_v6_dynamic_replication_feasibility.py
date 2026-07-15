#!/usr/bin/env python
"""Assess whether raw PANDORA supports V6 dynamic technical replication.

The current early/late design establishes temporal separation but cannot tell a
stable author component from a persistent state. This script does not estimate a
new factor. It asks a prior feasibility question: can each time half be split
into two chronological epochs, each with two independent *whole-run* replicas?
Runs are never split and no transition crosses a subreddit/run boundary.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v6_factor_discovery_v2 import prepare_units  # noqa: E402


@dataclass(frozen=True)
class Run:
    """A complete chronological same-condition run available for a dynamic view."""

    run_id: str
    condition: str
    start_time: float
    transitions: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_dynamic_replication_feasibility")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_DYNAMIC_REPLICATION_FEASIBILITY.md")
    return parser.parse_args()


def extract_runs(units: pd.DataFrame) -> dict[tuple[str, str], list[Run]]:
    """Return complete retained runs, enforcing continuity before eligibility."""
    output: dict[tuple[str, str], list[Run]] = {}
    for (user, half), group in units.groupby(["user_id", "half"], observed=True, sort=False):
        runs: list[Run] = []
        for run_id, run in group.groupby("run_id", observed=True, sort=False):
            ordered = run.sort_values("run_pos")
            positions = ordered["run_pos"].to_numpy(int)
            if len(positions) < 2 or not np.all(np.diff(positions) == 1):
                continue
            runs.append(Run(
                run_id=str(run_id), condition=str(ordered["condition"].iloc[0]),
                start_time=float(ordered["created_utc"].min()), transitions=len(positions) - 1,
            ))
        output[(str(user), str(half))] = sorted(runs, key=lambda item: item.start_time)
    return output


def split_two_epochs(runs: list[Run]) -> tuple[list[Run], list[Run]] | None:
    """Choose a chronological whole-run cut maximizing the weaker epoch's support."""
    if len(runs) < 2:
        return None
    totals = np.cumsum([run.transitions for run in runs])
    total = int(totals[-1])
    candidates = range(1, len(runs))
    cut = max(candidates, key=lambda i: min(int(totals[i - 1]), total - int(totals[i - 1])))
    return runs[:cut], runs[cut:]


def split_two_replicas(runs: list[Run]) -> tuple[list[Run], list[Run]] | None:
    """Assign complete runs to balanced independent replicas, preserving all runs."""
    if len(runs) < 2:
        return None
    left: list[Run] = []
    right: list[Run] = []
    left_total = right_total = 0
    for run in sorted(runs, key=lambda item: (-item.transitions, item.start_time)):
        if left_total <= right_total:
            left.append(run)
            left_total += run.transitions
        else:
            right.append(run)
            right_total += run.transitions
    return (left, right) if left and right else None


def replica_support(runs: list[Run], min_runs: int, min_transitions: int) -> bool:
    return len(runs) >= min_runs and sum(run.transitions for run in runs) >= min_transitions


def evaluate_half(runs: list[Run], min_runs: int, min_transitions: int) -> dict[str, object]:
    """Evaluate one user-half against an epoch x technical-replica design."""
    epochs = split_two_epochs(runs)
    if epochs is None:
        return {"feasible": False, "reason": "fewer_than_two_runs"}
    replicas = [split_two_replicas(epoch) for epoch in epochs]
    if any(pair is None for pair in replicas):
        return {"feasible": False, "reason": "epoch_cannot_split_into_two_runs"}
    assert replicas[0] is not None and replicas[1] is not None
    four = [replicas[0][0], replicas[0][1], replicas[1][0], replicas[1][1]]
    if not all(replica_support(rep, min_runs, min_transitions) for rep in four):
        return {"feasible": False, "reason": "insufficient_replica_support"}
    return {
        "feasible": True,
        "reason": "ok",
        "epoch_1_transitions": sum(run.transitions for run in epochs[0]),
        "epoch_2_transitions": sum(run.transitions for run in epochs[1]),
        "replica_transitions": ";".join(str(sum(run.transitions for run in rep)) for rep in four),
        "replica_conditions": ";".join(str(len({run.condition for run in rep})) for rep in four),
    }


def main() -> None:
    args = parse_args()
    cfg = json.loads(args.config.read_text())
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, cfg)
    runs = extract_runs(units)
    grids = [(1, 3), (1, 6), (1, 12), (2, 12)]
    records = []
    for (user, half), user_runs in runs.items():
        for min_runs, min_transitions in grids:
            result = evaluate_half(user_runs, min_runs, min_transitions)
            records.append({"user_id": user, "half": half, "min_runs": min_runs,
                            "min_transitions": min_transitions, "n_complete_runs": len(user_runs),
                            "total_transitions": sum(run.transitions for run in user_runs), **result})
    detail = pd.DataFrame(records)
    summary = (detail.groupby(["min_runs", "min_transitions"], observed=True)
               .agg(n_user_halves=("user_id", "size"), n_feasible=("feasible", "sum"),
                    median_runs=("n_complete_runs", "median"), median_transitions=("total_transitions", "median"))
               .reset_index())
    summary["feasible_rate"] = summary["n_feasible"] / summary["n_user_halves"]
    # A long-interval dynamic result requires both original early/late halves.
    pair_detail = (detail.loc[detail["feasible"]]
                   .groupby(["min_runs", "min_transitions", "user_id"], observed=True)["half"]
                   .nunique().reset_index(name="n_feasible_halves"))
    pair_counts = (pair_detail.assign(two_halves=pair_detail["n_feasible_halves"].eq(2))
                   .groupby(["min_runs", "min_transitions"], observed=True)["two_halves"].sum()
                   .rename("n_two_half_authors").reset_index())
    summary = summary.merge(pair_counts, on=["min_runs", "min_transitions"], how="left").fillna(0)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.output_dir / "dynamic_replication_feasibility_detail.csv", index=False)
    summary.to_csv(args.output_dir / "dynamic_replication_feasibility_summary.csv", index=False)
    official = summary.loc[(summary["min_runs"] == 2) & (summary["min_transitions"] == 12)].iloc[0]
    args.report.write_text(f"""# SUICA V6 Dynamic Replication Feasibility

## Question

Can the current raw PANDORA extraction identify a stable dynamic author-path
object separately from persistent state or measurement error? The required next
design uses each early/late half as two chronological epochs, and each epoch as
two independent replicas made from complete same-condition runs. No run or
transition is split.

## Feasibility table

{summary.to_markdown(index=False, floatfmt='.3f')}

## Interpretation

The registered current dynamic estimator requires at least two runs and twelve
transitions per view. Under that criterion, `{int(official.n_two_half_authors)}`
authors can supply all four replicas in both long-interval halves. If this count
is too small for a predeclared inferential target, PANDORA cannot resolve
author-level dynamics from persistent state; the correct conclusion is
`UNIDENTIFIABLE_WITH_CURRENT_CORPUS`, not a failed dynamic construct.

Relaxed rows are engineering feasibility only. They do not license an estimator
change or a psychological interpretation. Any follow-up must freeze run splitting,
time cut rules, and minimum transitions before estimating scores.
""")
    print(summary.to_string(index=False))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
