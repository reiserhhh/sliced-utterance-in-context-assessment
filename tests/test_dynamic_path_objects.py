from __future__ import annotations

import numpy as np

from suica_core.dynamic_path_objects import (
    RunSegment,
    condition_jaccard,
    equal_run_weighted_mean,
    lagged_pairs,
    second_order_run_summary,
    split_complete_runs,
    split_four_subepochs,
    standardized_norm,
    top_quantile_event_mask,
)


def _run(index: int, transitions: int, condition: str = "c") -> RunSegment:
    return RunSegment(str(index), condition, float(index * 10), float(index * 10 + 4), transitions)


def test_transition_and_time_partitions_keep_runs_whole() -> None:
    runs = [_run(0, 6), _run(1, 2), _run(2, 7), _run(3, 3)]
    transition = split_complete_runs(runs, mode="transition_balanced")
    time = split_complete_runs(runs, mode="time_balanced")
    assert transition is not None and time is not None
    assert {item.run_id for part in transition for item in part} == {"0", "1", "2", "3"}
    assert {item.run_id for part in time for item in part} == {"0", "1", "2", "3"}
    assert not ({item.run_id for item in transition[0]} & {item.run_id for item in transition[1]})


def test_four_subepochs_enforce_whole_half_and_subepoch_support() -> None:
    early = [_run(0, 6, "a"), _run(1, 6, "b")]
    late = [_run(2, 6, "a"), _run(3, 6, "b")]
    subepochs = split_four_subepochs(
        early, late, mode="transition_balanced", whole_half_min_runs=2,
        whole_half_min_transitions=12, subepoch_min_runs=1, subepoch_min_transitions=6,
    )
    assert subepochs is not None
    assert condition_jaccard(subepochs["early_0"], subepochs["late_0"]) == 1.0
    assert split_four_subepochs(
        [_run(0, 8), _run(1, 4)], late, mode="transition_balanced",
        whole_half_min_runs=2, whole_half_min_transitions=12,
        subepoch_min_runs=1, subepoch_min_transitions=6,
    ) is None


def test_numeric_path_summaries_are_run_weighted_and_lagged() -> None:
    path = np.array([[0.0, 0.0], [1.0, 2.0], [3.0, 2.0]])
    source, target = lagged_pairs(path, 1)
    assert source.shape == target.shape == (2, 2)
    summary = second_order_run_summary(path, 1)
    assert summary.shape == (4,)
    assert np.allclose(equal_run_weighted_mean([np.array([1.0, 3.0]), np.array([3.0, 5.0])]), [2.0, 4.0])


def test_standardized_norm_and_event_quantile_are_deterministic() -> None:
    values = np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0]])
    norms = standardized_norm(values, np.zeros(2), np.eye(2))
    assert np.allclose(norms, [0.0, 5.0, 10.0])
    assert top_quantile_event_mask(norms, quantile=0.5).tolist() == [False, True, True]
