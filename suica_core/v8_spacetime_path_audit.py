"""Post-seal path-level scope diagnostics for V3.6 junction flow."""
from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

from suica_core.v8_spacetime_junction_flow import _entropy


def _path_ids(values: np.ndarray, branches: int) -> np.ndarray:
    """Encode one branch sequence per row as a base-K integer."""
    matrix = np.asarray(values, dtype=int).reshape(-1, values.shape[-1])
    powers = branches ** np.arange(matrix.shape[1], dtype=int)
    return matrix @ powers


def path_information(
    outgoing: np.ndarray,
    cues: np.ndarray,
    incoming: np.ndarray,
    groups: np.ndarray,
    *,
    branches: int,
) -> dict[str, float]:
    """Measure whole-path entropy and cue information without IID expansion."""
    depth = outgoing.shape[-1]
    output_path = _path_ids(outgoing, branches)
    cue_path = _path_ids(cues, branches)
    initial_branch = np.asarray(incoming[..., 0], dtype=int).ravel()
    group_grid = np.broadcast_to(
        np.asarray(groups, dtype=int)[:, None],
        outgoing.shape[:2],
    ).ravel()
    normalizer = depth * np.log(branches)
    output_entropy = _entropy(output_path)
    cue_entropy = _entropy(cue_path)
    joint_entropy = _entropy(output_path, cue_path)
    conditional_entropy = joint_entropy - cue_entropy
    conditioned_output = (
        _entropy(output_path, initial_branch, group_grid)
        - _entropy(initial_branch, group_grid)
    )
    conditioned_cue = (
        _entropy(cue_path, initial_branch, group_grid)
        - _entropy(initial_branch, group_grid)
    )
    conditioned_joint = (
        _entropy(output_path, cue_path, initial_branch, group_grid)
        - _entropy(initial_branch, group_grid)
    )
    conditional_information = (
        conditioned_output + conditioned_cue - conditioned_joint
    )
    residual = conditioned_joint - conditioned_cue
    return {
        "path_entropy": float(output_entropy / normalizer),
        "path_entropy_given_cue": float(conditional_entropy / normalizer),
        "path_cue_information": float(
            (output_entropy + cue_entropy - joint_entropy) / normalizer
        ),
        "path_cue_information_given_initial_group": float(
            conditional_information / normalizer
        ),
        "path_residual_given_cue_initial_group": float(
            residual / normalizer
        ),
        "effective_leaf_fraction_exact": float(
            np.exp(output_entropy) / branches**depth
        ),
        "cue_conditional_leaf_fraction_exact": float(
            np.exp(conditional_entropy) / branches**depth
        ),
    }


def conditional_path_information_permutation(
    outgoing: np.ndarray,
    cues: np.ndarray,
    incoming: np.ndarray,
    groups: np.ndarray,
    *,
    branches: int,
    seed: int,
    permutations: int,
) -> dict[str, float]:
    """Bias-audit conditional path MI with within-stratum cue permutations."""
    observed = path_information(
        outgoing,
        cues,
        incoming,
        groups,
        branches=branches,
    )["path_cue_information_given_initial_group"]
    initial = np.asarray(incoming[..., 0], dtype=int).ravel()
    group_grid = np.broadcast_to(
        np.asarray(groups, dtype=int)[:, None],
        outgoing.shape[:2],
    ).ravel()
    cue_rows = np.asarray(cues, dtype=int).reshape(-1, cues.shape[-1])
    strata = np.column_stack([initial, group_grid])
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(permutations):
        shuffled = cue_rows.copy()
        for stratum in np.unique(strata, axis=0):
            index = np.flatnonzero(np.all(strata == stratum, axis=1))
            shuffled[index] = cue_rows[rng.permutation(index)]
        null.append(path_information(
            outgoing,
            shuffled.reshape(cues.shape),
            incoming,
            groups,
            branches=branches,
        )["path_cue_information_given_initial_group"])
    null_array = np.asarray(null)
    return {
        "path_conditional_mi_raw": float(observed),
        "path_conditional_mi_null_mean": float(null_array.mean()),
        "path_conditional_mi_bias_adjusted": float(
            observed - null_array.mean()
        ),
        "path_conditional_mi_permutation_p": float(
            (1 + np.count_nonzero(null_array >= observed - 1e-12))
            / (permutations + 1)
        ),
    }


def heldout_local_route_accuracy(
    outgoing: np.ndarray,
    cues: np.ndarray,
    incoming: np.ndarray,
    groups: np.ndarray,
    *,
    branches: int,
) -> dict[str, float]:
    """Fit local transition tables and test unseen cue-path combinations."""
    episodes = outgoing.shape[1]
    train_episode = np.arange(episodes) % 2 == 0
    test_episode = ~train_episode
    depth = outgoing.shape[-1]
    train_rows = []
    test_rows = []
    for author in range(outgoing.shape[0]):
        for episode in range(episodes):
            target = train_rows if train_episode[episode] else test_rows
            for stage in range(depth):
                target.append((
                    int(groups[author]),
                    stage,
                    int(incoming[author, episode, stage]),
                    int(cues[author, episode, stage]),
                    int(outgoing[author, episode, stage]),
                    author,
                    episode,
                ))
    counts: dict[tuple[Any, ...], np.ndarray] = {}

    def add(key: tuple[Any, ...], branch_out: int) -> None:
        counts.setdefault(key, np.zeros(branches, dtype=int))[branch_out] += 1

    for group, stage, branch_in, cue, branch_out, _, _ in train_rows:
        add(("full", group, stage, branch_in, cue), branch_out)
        add(("stage_in_cue", stage, branch_in, cue), branch_out)
        add(("in_cue", branch_in, cue), branch_out)
        add(("stage_in", stage, branch_in), branch_out)
        add(("in", branch_in), branch_out)
        add(("stage_cue", stage, cue), branch_out)
        add(("cue", cue), branch_out)

    confusion = np.zeros((branches, branches), dtype=int)
    records = []
    for group, stage, branch_in, cue, branch_out, author, episode in test_rows:
        distribution = None
        for key in (
            ("full", group, stage, branch_in, cue),
            ("stage_in_cue", stage, branch_in, cue),
            ("in_cue", branch_in, cue),
            ("stage_in", stage, branch_in),
            ("in", branch_in),
            ("stage_cue", stage, cue),
            ("cue", cue),
        ):
            candidate = counts.get(key)
            if candidate is not None and candidate.sum() > 0:
                distribution = candidate
                break
        prediction = (
            int(np.argmax(distribution))
            if distribution is not None and distribution.sum() > 0
            else 0
        )
        confusion[prediction, branch_out] += 1
        records.append((author, episode, stage, prediction, branch_out))
    rows, columns = linear_sum_assignment(-confusion)
    predicted_to_observed = np.arange(branches, dtype=int)
    predicted_to_observed[rows] = columns
    point_correct = []
    path_correct: dict[tuple[int, int], list[bool]] = {}
    for author, episode, _, prediction, branch_out in records:
        correct = bool(predicted_to_observed[prediction] == branch_out)
        point_correct.append(correct)
        path_correct.setdefault((author, episode), []).append(correct)
    exact = [all(values) for values in path_correct.values()]
    return {
        "heldout_transition_accuracy": float(np.mean(point_correct)),
        "heldout_exact_path_accuracy": float(np.mean(exact)),
        "heldout_paths": int(len(exact)),
    }


def summarize_path_audit(
    metrics: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    """Aggregate repetition-level path metrics by policy."""
    output: dict[str, dict[str, float]] = {}
    for policy in sorted({str(row["policy"]) for row in metrics}):
        rows = [row for row in metrics if row["policy"] == policy]
        keys = [key for key in rows[0] if key != "policy"]
        output[policy] = {
            f"{key}_mean": float(np.mean([row[key] for row in rows]))
            for key in keys
        }
    return output
