from __future__ import annotations

from scripts.run_suica_v6_dynamic_replication_feasibility import Run, evaluate_half, split_two_epochs


def _runs(n: int, transitions: int = 6):
    return [Run(f"r{i}", f"c{i % 2}", float(i), transitions) for i in range(n)]


def test_epoch_split_respects_complete_chronological_runs() -> None:
    left, right = split_two_epochs(_runs(6))
    assert {run.run_id for run in left} | {run.run_id for run in right} == {f"r{i}" for i in range(6)}
    assert max(run.start_time for run in left) < min(run.start_time for run in right)


def test_four_replica_feasibility_requires_support_in_every_replica() -> None:
    assert evaluate_half(_runs(8), min_runs=1, min_transitions=3)["feasible"]
    assert not evaluate_half(_runs(4, transitions=2), min_runs=1, min_transitions=3)["feasible"]
