"""Hierarchical, held-out measurement of context-selection identity.

The module treats a population selection profile as a nested sequence of
group-centroid innovations. Trees are fitted on one set of authors and applied
to held-out authors, so branch replay across text halves cannot be created by
placing the evaluated author into the tree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import KFold


def normalize_rows(values: np.ndarray) -> np.ndarray:
    """Return finite unit-length rows, leaving all-zero rows at zero."""

    array = np.asarray(values, dtype=float)
    if array.ndim != 2:
        raise ValueError("row normalization requires a 2D matrix")
    if not np.isfinite(array).all():
        raise ValueError("selection matrix contains non-finite values")
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    return np.divide(array, norms, out=np.zeros_like(array), where=norms > 0)


def hellinger_rows(frequencies: np.ndarray) -> np.ndarray:
    """Map non-negative frequency rows to the unit Hellinger sphere."""

    array = np.asarray(frequencies, dtype=float)
    if np.any(array < -1e-12):
        raise ValueError("Hellinger inputs must be non-negative")
    return normalize_rows(np.sqrt(np.clip(array, 0.0, None)))


def _spherical_binary_split(
    values: np.ndarray,
    *,
    random_state: int,
    n_init: int,
    max_iter: int = 100,
) -> tuple[np.ndarray, np.ndarray] | None:
    """Return a converged two-cluster cosine partition and unit centroids."""

    # Euclidean KMeans supplies a deterministic, multi-start initialization.
    labels = KMeans(
        n_clusters=2,
        n_init=n_init,
        random_state=random_state,
        algorithm="lloyd",
    ).fit_predict(values)
    for _ in range(max_iter):
        groups = [values[labels == label] for label in (0, 1)]
        if min(map(len, groups)) == 0:
            return None
        centers = normalize_rows(
            np.vstack([group.mean(axis=0) for group in groups])
        )
        updated = np.argmax(values @ centers.T, axis=1)
        if np.unique(updated).size < 2:
            return None
        if np.array_equal(updated, labels):
            return labels, centers
        labels = updated
    raise RuntimeError("spherical two-means did not converge")


@dataclass(frozen=True)
class SelectionTreeNode:
    """One frozen node in a binary selection hierarchy."""

    node_id: int
    depth: int
    n_train: int
    centroid: np.ndarray
    left: int | None = None
    right: int | None = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None or self.right is None


@dataclass
class HierarchicalSelectionTree:
    """A frozen binary tree fitted in Hellinger selection space."""

    nodes: dict[int, SelectionTreeNode]
    root_id: int
    max_depth: int

    def choose_child(self, parent_id: int, row: np.ndarray) -> int:
        """Choose between one frozen parent's children for an arbitrary row."""

        parent = self.nodes[parent_id]
        if parent.is_leaf:
            raise ValueError("cannot choose a child from a leaf")
        vector = np.asarray(row, dtype=float)
        left = self.nodes[int(parent.left)]
        right = self.nodes[int(parent.right)]
        left_distance = float(np.sum((vector - left.centroid) ** 2))
        right_distance = float(np.sum((vector - right.centroid) ** 2))
        return left.node_id if left_distance <= right_distance else right.node_id

    def route(self, row: np.ndarray) -> list[int]:
        """Return root-to-leaf node ids for one already transformed row."""

        vector = np.asarray(row, dtype=float)
        path = [self.root_id]
        node = self.nodes[self.root_id]
        while not node.is_leaf:
            child_id = self.choose_child(node.node_id, vector)
            path.append(child_id)
            node = self.nodes[child_id]
        return path

    def route_many(self, rows: np.ndarray) -> list[list[int]]:
        """Route each transformed row through the frozen tree."""

        return [self.route(row) for row in np.asarray(rows, dtype=float)]

    def increment_sum(self, path: Iterable[int]) -> np.ndarray:
        """Sum child-minus-parent centroid innovations along one path."""

        ids = list(path)
        if not ids:
            raise ValueError("a path must contain at least the root")
        total = np.zeros_like(self.nodes[ids[0]].centroid)
        for parent, child in zip(ids[:-1], ids[1:]):
            total += self.nodes[child].centroid - self.nodes[parent].centroid
        return total


def fit_selection_tree(
    transformed: np.ndarray,
    *,
    max_depth: int = 6,
    min_leaf: int = 30,
    random_state: int = 0,
    n_init: int = 10,
) -> HierarchicalSelectionTree:
    """Fit a recursive spherical two-means hierarchy.

    Hellinger rows have unit norm, so Euclidean two-means and cosine separation
    induce the same nearest-centroid ordering. A split is retained only when
    both children meet ``min_leaf``.
    """

    values = np.asarray(transformed, dtype=float)
    if values.ndim != 2 or len(values) < 2:
        raise ValueError("tree fitting requires at least two 2D rows")
    if max_depth < 1 or min_leaf < 2:
        raise ValueError("max_depth and min_leaf are out of range")
    if not np.isfinite(values).all():
        raise ValueError("tree input contains non-finite values")

    nodes: dict[int, SelectionTreeNode] = {}
    next_id = 0

    def build(indices: np.ndarray, depth: int) -> int:
        nonlocal next_id
        node_id = next_id
        next_id += 1
        centroid = normalize_rows(values[indices].mean(axis=0, keepdims=True))[0]
        nodes[node_id] = SelectionTreeNode(
            node_id=node_id,
            depth=depth,
            n_train=len(indices),
            centroid=centroid,
        )
        if depth >= max_depth or len(indices) < 2 * min_leaf:
            return node_id

        split = _spherical_binary_split(
            values[indices],
            random_state=random_state + node_id,
            n_init=n_init,
        )
        if split is None:
            return node_id
        labels, child_centroids = split
        child_indices = [indices[labels == label] for label in (0, 1)]
        if min(map(len, child_indices)) < min_leaf:
            return node_id

        # Give child numbering a deterministic geometric orientation.
        anchor = int(np.argmax(np.abs(child_centroids[0] - child_centroids[1])))
        if child_centroids[0][anchor] > child_centroids[1][anchor]:
            child_indices.reverse()
        left = build(child_indices[0], depth + 1)
        right = build(child_indices[1], depth + 1)
        nodes[node_id] = SelectionTreeNode(
            node_id=node_id,
            depth=depth,
            n_train=len(indices),
            centroid=centroid,
            left=left,
            right=right,
        )
        return node_id

    root = build(np.arange(len(values), dtype=int), 0)
    return HierarchicalSelectionTree(nodes=nodes, root_id=root, max_depth=max_depth)


def path_array(paths: list[list[int]], max_depth: int) -> np.ndarray:
    """Represent branch nodes at depths 1..max_depth, padding with -1."""

    output = np.full((len(paths), max_depth), -1, dtype=int)
    for row, path in enumerate(paths):
        branch = path[1 : max_depth + 1]
        output[row, : len(branch)] = branch
    return output


def common_prefix_scores(early: np.ndarray, late: np.ndarray) -> np.ndarray:
    """Pairwise count of equal consecutive branch nodes from the root."""

    if early.ndim != 2 or late.ndim != 2 or early.shape[1] != late.shape[1]:
        raise ValueError("path matrices must be 2D with equal depth")
    scores = np.zeros((len(early), len(late)), dtype=float)
    alive = np.ones_like(scores, dtype=bool)
    for depth in range(early.shape[1]):
        valid = (early[:, None, depth] >= 0) & (late[None, :, depth] >= 0)
        alive &= valid & (early[:, None, depth] == late[None, :, depth])
        scores += alive
    return scores


def _auc_from_square(scores: np.ndarray) -> float:
    labels = np.eye(len(scores), dtype=bool)
    y_true = labels.ravel().astype(int)
    return float(roc_auc_score(y_true, scores.ravel()))


def _cosine_matrix(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return normalize_rows(left) @ normalize_rows(right).T


def _bootstrap_mean_interval(
    values: np.ndarray,
    *,
    seed: int,
    repetitions: int,
) -> tuple[float, float]:
    if len(values) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    draws = np.empty(repetitions, dtype=float)
    for index in range(repetitions):
        draws[index] = rng.choice(values, size=len(values), replace=True).mean()
    return tuple(float(v) for v in np.percentile(draws, [2.5, 97.5]))


def _mutual_information_bits(left: np.ndarray, right: np.ndarray) -> float:
    """Empirical mutual information in bits for two discrete vectors."""

    first = np.asarray(left)
    second = np.asarray(right)
    if first.shape != second.shape or first.ndim != 1:
        raise ValueError("mutual-information inputs must be equal 1D vectors")
    if not len(first):
        return 0.0
    _, first_codes = np.unique(first, return_inverse=True)
    _, second_codes = np.unique(second, return_inverse=True)
    table = np.zeros(
        (int(first_codes.max()) + 1, int(second_codes.max()) + 1),
        dtype=float,
    )
    np.add.at(table, (first_codes, second_codes), 1.0)
    joint = table / table.sum()
    first_marginal = joint.sum(axis=1, keepdims=True)
    second_marginal = joint.sum(axis=0, keepdims=True)
    expected = first_marginal @ second_marginal
    nonzero = joint > 0
    return float(np.sum(joint[nonzero] * np.log2(joint[nonzero] / expected[nonzero])))


def cross_fitted_hierarchical_identity(
    early_frequencies: np.ndarray,
    late_frequencies: np.ndarray,
    *,
    n_splits: int = 5,
    max_depth: int = 6,
    min_leaf: int = 30,
    random_state: int = 20260817,
    n_permutations: int = 499,
    n_bootstrap: int = 1000,
) -> dict[str, object]:
    """Measure held-out branch replay and terminal residual identity.

    The conditional permutation shuffles late vectors only among held-out
    authors that share the same early parent node. It therefore asks whether
    the next branch adds information beyond the already shared prefix.
    """

    early = hellinger_rows(early_frequencies)
    late = hellinger_rows(late_frequencies)
    if early.shape != late.shape:
        raise ValueError("early and late selection matrices must have equal shape")
    valid = (np.linalg.norm(early, axis=1) > 0) & (np.linalg.norm(late, axis=1) > 0)
    early, late = early[valid], late[valid]
    original_indices = np.flatnonzero(valid)
    if len(early) < n_splits * max(2, min_leaf // 2):
        raise ValueError("too few valid authors for the requested cross-fitting")

    splitter = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    rng = np.random.default_rng(random_state + 97)
    depth_records: list[dict[str, float | int | bool]] = []
    flat_positive: list[float] = []
    flat_negative: list[float] = []
    path_positive: list[float] = []
    path_negative: list[float] = []
    residual_positive: list[float] = []
    residual_negative: list[float] = []
    permutation_gain = np.zeros((max_depth, n_permutations), dtype=float)
    permutation_agreement = np.zeros((max_depth, n_permutations), dtype=float)
    observed_information_sum = np.zeros(max_depth, dtype=float)
    permutation_information = np.zeros((max_depth, n_permutations), dtype=float)
    permutation_counts = np.zeros(max_depth, dtype=int)
    tree_rows: list[dict[str, int]] = []

    for fold, (train_index, test_index) in enumerate(splitter.split(early)):
        tree = fit_selection_tree(
            early[train_index],
            max_depth=max_depth,
            min_leaf=min_leaf,
            random_state=random_state + 1000 * fold,
        )
        early_paths = tree.route_many(early[test_index])
        late_paths = tree.route_many(late[test_index])
        early_path_array = path_array(early_paths, max_depth)
        late_path_array = path_array(late_paths, max_depth)
        tree_rows.append(
            {
                "fold": fold,
                "nodes": len(tree.nodes),
                "leaves": sum(node.is_leaf for node in tree.nodes.values()),
                "realized_depth": max(node.depth for node in tree.nodes.values()),
            }
        )

        flat_scores = early[test_index] @ late[test_index].T
        path_scores = common_prefix_scores(early_path_array, late_path_array)
        diagonal = np.eye(len(test_index), dtype=bool)
        flat_positive.extend(flat_scores[diagonal].tolist())
        flat_negative.extend(flat_scores[~diagonal].tolist())
        path_positive.extend(path_scores[diagonal].tolist())
        path_negative.extend(path_scores[~diagonal].tolist())

        # Terminal residuals are compared only inside the same early leaf.
        leaves = np.array([path[-1] for path in early_paths], dtype=int)
        for leaf_id in np.unique(leaves):
            local = np.flatnonzero(leaves == leaf_id)
            if len(local) < 2:
                continue
            centroid = tree.nodes[int(leaf_id)].centroid
            residual_early = early[test_index[local]] - centroid
            residual_late = late[test_index[local]] - centroid
            residual_scores = _cosine_matrix(residual_early, residual_late)
            local_diagonal = np.eye(len(local), dtype=bool)
            valid_scores = np.isfinite(residual_scores)
            residual_positive.extend(
                residual_scores[local_diagonal & valid_scores].tolist()
            )
            residual_negative.extend(
                residual_scores[(~local_diagonal) & valid_scores].tolist()
            )

        for depth in range(1, max_depth + 1):
            local_depth = depth - 1
            available = np.flatnonzero(early_path_array[:, local_depth] >= 0)
            if not len(available):
                continue
            groups: dict[int, list[int]] = {}
            for local_index in available:
                parent_id = (
                    tree.root_id
                    if depth == 1
                    else int(early_path_array[local_index, local_depth - 1])
                )
                groups.setdefault(parent_id, []).append(int(local_index))

            for local_index in available:
                parent_id = (
                    tree.root_id
                    if depth == 1
                    else int(early_path_array[local_index, local_depth - 1])
                )
                child_id = int(early_path_array[local_index, local_depth])
                parent = tree.nodes[parent_id].centroid
                child = tree.nodes[child_id].centroid
                late_row = late[test_index[local_index]]
                late_local_child = tree.choose_child(parent_id, late_row)
                gain = float(
                    np.sum((late_row - parent) ** 2)
                    - np.sum((late_row - child) ** 2)
                )
                prefix_agreement = bool(
                    np.array_equal(
                        early_path_array[local_index, : local_depth + 1],
                        late_path_array[local_index, : local_depth + 1],
                    )
                )
                depth_records.append(
                    {
                        "author_index": int(original_indices[test_index[local_index]]),
                        "fold": fold,
                        "depth": depth,
                        "parent_id": parent_id,
                        "child_id": child_id,
                        "gain": gain,
                        "late_local_child_id": late_local_child,
                        "branch_agreement": bool(late_local_child == child_id),
                        "prefix_agreement": prefix_agreement,
                    }
                )

            permutation_counts[local_depth] += len(available)
            for parent_id, local_members in groups.items():
                members = np.asarray(local_members, dtype=int)
                early_children = early_path_array[members, local_depth]
                late_children = np.array(
                    [
                        tree.choose_child(parent_id, late[test_index[index]])
                        for index in members
                    ],
                    dtype=int,
                )
                observed_information_sum[local_depth] += len(members) * (
                    _mutual_information_bits(early_children, late_children)
                )
            for permutation in range(n_permutations):
                gain_sum = 0.0
                agreement_sum = 0.0
                for parent_id, local_members in groups.items():
                    members = np.asarray(local_members, dtype=int)
                    shuffled = rng.permutation(members)
                    parent = tree.nodes[parent_id].centroid
                    early_children: list[int] = []
                    late_children: list[int] = []
                    for source, target in zip(members, shuffled):
                        child_id = int(early_path_array[source, local_depth])
                        child = tree.nodes[child_id].centroid
                        late_row = late[test_index[target]]
                        late_local_child = tree.choose_child(parent_id, late_row)
                        gain_sum += float(
                            np.sum((late_row - parent) ** 2)
                            - np.sum((late_row - child) ** 2)
                        )
                        agreement_sum += float(late_local_child == child_id)
                        early_children.append(child_id)
                        late_children.append(late_local_child)
                    permutation_information[local_depth, permutation] += len(
                        members
                    ) * _mutual_information_bits(
                        np.asarray(early_children), np.asarray(late_children)
                    )
                permutation_gain[local_depth, permutation] += gain_sum
                permutation_agreement[local_depth, permutation] += agreement_sum

    def binary_auc(positive: list[float], negative: list[float]) -> float:
        if not positive or not negative:
            return float("nan")
        labels = np.r_[np.ones(len(positive)), np.zeros(len(negative))]
        scores = np.r_[positive, negative]
        return float(roc_auc_score(labels, scores))

    depth_rows: list[dict[str, float | int]] = []
    for depth in range(1, max_depth + 1):
        records = [row for row in depth_records if row["depth"] == depth]
        if not records:
            continue
        gains = np.array([float(row["gain"]) for row in records])
        agreements = np.array([bool(row["branch_agreement"]) for row in records])
        prefixes = np.array([bool(row["prefix_agreement"]) for row in records])
        null_gain = permutation_gain[depth - 1] / permutation_counts[depth - 1]
        null_agreement = (
            permutation_agreement[depth - 1] / permutation_counts[depth - 1]
        )
        information = (
            observed_information_sum[depth - 1]
            / permutation_counts[depth - 1]
        )
        null_information = (
            permutation_information[depth - 1]
            / permutation_counts[depth - 1]
        )
        gain_ci = _bootstrap_mean_interval(
            gains,
            seed=random_state + depth,
            repetitions=n_bootstrap,
        )
        depth_rows.append(
            {
                "depth": depth,
                "n": len(records),
                "gain_mean": float(gains.mean()),
                "gain_ci_low": gain_ci[0],
                "gain_ci_high": gain_ci[1],
                "gain_null_mean": float(null_gain.mean()),
                "gain_null_sd": float(null_gain.std(ddof=1)),
                "gain_permutation_p": float(
                    (np.sum(null_gain >= gains.mean()) + 1)
                    / (n_permutations + 1)
                ),
                "branch_agreement": float(agreements.mean()),
                "branch_null_mean": float(null_agreement.mean()),
                "branch_excess": float(agreements.mean() - null_agreement.mean()),
                "branch_permutation_p": float(
                    (np.sum(null_agreement >= agreements.mean()) + 1)
                    / (n_permutations + 1)
                ),
                "conditional_information_bits": float(information),
                "information_null_mean": float(null_information.mean()),
                "information_excess_bits": float(
                    information - null_information.mean()
                ),
                "information_permutation_p": float(
                    (np.sum(null_information >= information) + 1)
                    / (n_permutations + 1)
                ),
                "prefix_agreement": float(prefixes.mean()),
            }
        )

    summary = {
        "n_input": int(len(valid)),
        "n_valid": int(valid.sum()),
        "n_features": int(early.shape[1]),
        "flat_auc": binary_auc(flat_positive, flat_negative),
        "hierarchical_path_auc": binary_auc(path_positive, path_negative),
        "terminal_residual_auc": binary_auc(residual_positive, residual_negative),
        "flat_same_mean": float(np.mean(flat_positive)),
        "flat_other_mean": float(np.mean(flat_negative)),
        "path_same_mean": float(np.mean(path_positive)),
        "path_other_mean": float(np.mean(path_negative)),
        "terminal_residual_same_mean": float(np.mean(residual_positive)),
        "terminal_residual_other_mean": float(np.mean(residual_negative)),
        "n_terminal_positive": len(residual_positive),
        "n_terminal_negative": len(residual_negative),
        "tree_folds": tree_rows,
    }
    return {
        "summary": summary,
        "metrics_by_depth": depth_rows,
        "per_user_depth": depth_records,
    }


def simulate_hierarchical_choices(
    *,
    n_authors: int = 480,
    n_contexts: int = 48,
    depth: int = 4,
    events_per_half: int = 500,
    strength: float = 1.4,
    decay: float = 0.72,
    seed: int = 0,
    author_null: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate two selection halves with a planted nested-choice hierarchy."""

    rng = np.random.default_rng(seed)
    base = rng.normal(0.0, 0.35, size=n_contexts)
    paths = rng.integers(0, 2, size=(n_authors, depth))
    effects: dict[tuple[int, ...], np.ndarray] = {}
    for level in range(depth):
        for prefix_number in range(2**level):
            prefix = tuple((prefix_number >> bit) & 1 for bit in range(level))
            direction = rng.normal(size=n_contexts)
            direction -= direction.mean()
            direction /= max(np.linalg.norm(direction), 1e-12)
            effects[prefix] = direction * strength * (decay**level) * np.sqrt(
                n_contexts
            )

    probabilities = np.empty((n_authors, n_contexts), dtype=float)
    for author in range(n_authors):
        logits = base.copy()
        if not author_null:
            for level in range(depth):
                prefix = tuple(int(value) for value in paths[author, :level])
                sign = 1.0 if paths[author, level] else -1.0
                logits += sign * effects[prefix]
        logits -= logits.max()
        exp_logits = np.exp(logits)
        probabilities[author] = exp_logits / exp_logits.sum()

    early = np.vstack(
        [rng.multinomial(events_per_half, row) for row in probabilities]
    ).astype(float)
    late = np.vstack(
        [rng.multinomial(events_per_half, row) for row in probabilities]
    ).astype(float)
    early /= early.sum(axis=1, keepdims=True)
    late /= late.sum(axis=1, keepdims=True)
    return early, late, paths
