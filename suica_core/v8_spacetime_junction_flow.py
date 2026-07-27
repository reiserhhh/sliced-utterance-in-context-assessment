"""Spacetime common-junction and conditional routing estimators for V3.6."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Any

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import pdist
from scipy.stats import kendalltau
from sklearn.metrics import adjusted_rand_score, f1_score

from suica_core.v8_incidence_incremental import _predicted_labels
from suica_core.v8_incidence_multiplicity import minimum_enclosing_ball


@dataclass(frozen=True)
class JunctionFlowSpec:
    """Frozen V3.6 simulator and routing-estimator settings."""

    authors: int = 24
    groups: int = 4
    branches: int = 3
    depth: int = 3
    episodes: int = 27
    views: int = 4
    ambient: int = 2
    node_radius: float = 0.15
    node_spread: float = 0.06
    near_miss_spread: float = 0.30
    segment_length: float = 1.0
    noise_sd: float = 0.008
    time_weight: float = 4.0
    minimum_node_persistence: float = 0.95
    minimum_time_tau: float = 0.95
    minimum_view_ari: float = 0.90
    target_information_threshold: float = 0.80
    nontarget_information_threshold: float = 0.10
    residual_entropy_threshold: float = 0.80


def _balanced_labels(spec: JunctionFlowSpec, seed: int) -> np.ndarray:
    labels = np.arange(spec.authors, dtype=int) % spec.groups
    return labels[np.random.default_rng(seed).permutation(spec.authors)]


def _anchors() -> np.ndarray:
    return np.asarray([
        [-6.0, -6.0],
        [-6.0, 6.0],
        [6.0, -6.0],
        [6.0, 6.0],
    ])


def _cue_sequences(spec: JunctionFlowSpec) -> np.ndarray:
    sequences = np.asarray(
        list(product(range(spec.branches), repeat=spec.depth)),
        dtype=int,
    )
    if len(sequences) != spec.episodes:
        raise ValueError(
            "episodes must equal branches ** depth for the frozen design"
        )
    return sequences


def _branch_directions(spec: JunctionFlowSpec, seed: int) -> np.ndarray:
    phase = np.random.default_rng(seed).uniform(0.0, 2.0 * np.pi)
    angles = phase + 2.0 * np.pi * np.arange(spec.branches) / spec.branches
    return np.column_stack([np.cos(angles), np.sin(angles)])


def _balanced_random_outputs(
    spec: JunctionFlowSpec,
    seed: int,
) -> np.ndarray:
    total = spec.authors * spec.episodes
    base = np.tile(
        np.arange(spec.branches),
        total // spec.branches,
    )
    output = np.zeros(
        (spec.authors, spec.episodes, spec.depth),
        dtype=int,
    )
    for depth in range(spec.depth):
        values = np.random.default_rng(
            seed + 101 * depth
        ).permutation(base)
        output[:, :, depth] = values.reshape(
            spec.authors,
            spec.episodes,
        )
    return output


def _node_offsets(
    labels: np.ndarray,
    *,
    spread: float,
    spec: JunctionFlowSpec,
) -> np.ndarray:
    offsets = np.zeros((spec.authors, 2), dtype=float)
    for group in range(spec.groups):
        members = np.sort(np.flatnonzero(labels == group))
        angles = 2.0 * np.pi * np.arange(len(members)) / len(members)
        offsets[members] = spread * np.column_stack([
            np.cos(angles),
            np.sin(angles),
        ])
    return offsets


def simulate_junction_world(
    *,
    seed: int,
    policy: str,
    spec: JunctionFlowSpec,
    attack: str | None = None,
) -> dict[str, Any]:
    """Generate one matched spacetime routing population."""
    if policy not in {"pass_through", "random_branch", "cue_guided"}:
        raise ValueError(f"unsupported routing policy: {policy}")
    if attack not in {None, "cue_shuffle", "time_shuffle", "tangent_view_shuffle", "near_miss"}:
        raise ValueError(f"unsupported junction attack: {attack}")
    labels = _balanced_labels(spec, seed)
    cues = _cue_sequences(spec)
    directions = _branch_directions(spec, seed + 10_003)
    random_outputs = _balanced_random_outputs(spec, seed + 20_011)
    spread = (
        spec.near_miss_spread
        if attack == "near_miss"
        else spec.node_spread
    )
    node_offsets = _node_offsets(labels, spread=spread, spec=spec)
    anchors = _anchors()

    incoming = np.zeros(
        (spec.authors, spec.episodes, spec.depth),
        dtype=int,
    )
    outgoing = np.zeros_like(incoming)
    for author in range(spec.authors):
        for episode in range(spec.episodes):
            current = int(np.sum(cues[episode]) % spec.branches)
            for depth in range(spec.depth):
                incoming[author, episode, depth] = current
                if policy == "pass_through":
                    selected = current
                elif policy == "cue_guided":
                    selected = int(cues[episode, depth])
                else:
                    selected = int(random_outputs[author, episode, depth])
                outgoing[author, episode, depth] = selected
                current = selected

    nodes = np.zeros(
        (spec.authors, spec.episodes, spec.depth, spec.ambient),
        dtype=float,
    )
    for author in range(spec.authors):
        nodes[author] = (
            anchors[labels[author]]
            + node_offsets[author]
        )
    pre = (
        nodes
        - spec.segment_length
        * directions[incoming]
    )
    post = (
        nodes
        + spec.segment_length
        * directions[outgoing]
    )
    curve = 0.08 * np.column_stack([
        -directions[:, 1],
        directions[:, 0],
    ])
    pre += curve[incoming]
    post += curve[outgoing]
    clean = np.stack([pre, nodes, post], axis=3)

    observations = []
    rng = np.random.default_rng(seed + 30_013)
    for _ in range(spec.views):
        observations.append(
            clean
            + rng.normal(scale=spec.noise_sd, size=clean.shape)
        )
    observations = np.asarray(observations)

    observed_cues = np.broadcast_to(
        cues[None, :, :],
        (spec.authors, spec.episodes, spec.depth),
    ).copy()
    observed_times = np.broadcast_to(
        np.arange(spec.depth, dtype=float)[None, None, :],
        (spec.authors, spec.episodes, spec.depth),
    ).copy()
    if attack == "cue_shuffle":
        for depth in range(spec.depth):
            flat = observed_cues[:, :, depth].ravel()
            observed_cues[:, :, depth] = np.random.default_rng(
                seed + 40_009 + depth
            ).permutation(flat).reshape(spec.authors, spec.episodes)
    if attack == "time_shuffle":
        for author in range(spec.authors):
            for episode in range(spec.episodes):
                observed_times[author, episode] = np.random.default_rng(
                    seed + 50_021 + 101 * author + episode
                ).permutation(observed_times[author, episode])
    if attack == "tangent_view_shuffle":
        flat_post = observations[
            1,
            ...,
            2,
            :,
        ].reshape(-1, spec.ambient)
        permutation = np.random.default_rng(seed + 60_023).permutation(
            len(flat_post)
        )
        observations[1, ..., 2, :] = flat_post[permutation].reshape(
            observations[1, ..., 2, :].shape
        )

    return {
        "policy": policy,
        "attack": attack,
        "labels": labels,
        "cues": observed_cues,
        "true_cues": np.broadcast_to(
            cues[None, :, :],
            (spec.authors, spec.episodes, spec.depth),
        ).copy(),
        "incoming": incoming,
        "outgoing": outgoing,
        "observed_times": observed_times,
        "observations": observations,
        "directions": directions,
    }


def _cluster_author_nodes(
    node_points: np.ndarray,
    *,
    spec: JunctionFlowSpec,
) -> list[frozenset[int]]:
    author_centers = node_points.mean(axis=(1, 2))
    hierarchy = linkage(pdist(author_centers), method="complete")
    cluster_labels = fcluster(hierarchy, t=2.0, criterion="distance")
    return [
        frozenset(int(item) for item in np.flatnonzero(
            cluster_labels == cluster
        ))
        for cluster in np.unique(cluster_labels)
        if np.sum(cluster_labels == cluster) >= 3
    ]


def _node_estimate(
    observations: np.ndarray,
    truth: np.ndarray,
    *,
    spec: JunctionFlowSpec,
) -> dict[str, Any]:
    groups_by_view = [
        _cluster_author_nodes(view[..., 1, :], spec=spec)
        for view in observations
    ]
    first = groups_by_view[0]
    stable = [
        group for group in first
        if all(group in groups for groups in groups_by_view[1:])
    ]
    passing = []
    persistence: dict[frozenset[int], float] = {}
    for group in stable:
        members = sorted(group)
        successes = 0
        total = spec.views * spec.episodes * spec.depth
        for view in range(spec.views):
            for episode in range(spec.episodes):
                for depth in range(spec.depth):
                    _, radius = minimum_enclosing_ball(
                        observations[
                            view,
                            members,
                            episode,
                            depth,
                            1,
                        ]
                    )
                    successes += int(radius <= spec.node_radius)
        persistence[group] = successes / total
        if persistence[group] >= spec.minimum_node_persistence:
            passing.append(group)
    coverage = (
        len(set().union(*passing)) / spec.authors
        if passing else 0.0
    )
    predicted = _predicted_labels(spec.authors, passing)
    upper = np.triu_indices(spec.authors, 1)
    truth_pairs = (truth[upper[0]] == truth[upper[1]]).astype(int)
    predicted_pairs = (
        predicted[upper[0]] == predicted[upper[1]]
    ).astype(int)
    return {
        "group_claim": bool(
            len(passing) >= 2 and coverage >= 0.75
        ),
        "coverage": coverage,
        "selected_groups": [
            sorted(int(item) for item in group) for group in passing
        ],
        "minimum_persistence": min(
            (persistence[group] for group in passing),
            default=0.0,
        ),
        "group_f1": float(f1_score(
            truth_pairs,
            predicted_pairs,
            zero_division=0,
        )),
        "group_ari": float(adjusted_rand_score(truth, predicted)),
    }


def _angular_labels(
    vectors: np.ndarray,
    *,
    branches: int,
) -> np.ndarray:
    angles = np.arctan2(vectors[:, 1], vectors[:, 0])
    phase = np.angle(np.mean(np.exp(1j * branches * angles))) / branches
    prototypes = phase + 2.0 * np.pi * np.arange(branches) / branches
    difference = np.angle(
        np.exp(1j * (angles[:, None] - prototypes[None, :]))
    )
    return np.argmin(abs(difference), axis=1)


def _entropy(*variables: np.ndarray) -> float:
    if not variables:
        return 0.0
    stacked = np.column_stack([
        np.asarray(variable).ravel() for variable in variables
    ])
    _, counts = np.unique(stacked, axis=0, return_counts=True)
    probability = counts / counts.sum()
    return float(-np.sum(probability * np.log(probability)))


def _conditional_entropy(
    outcome: np.ndarray,
    *condition: np.ndarray,
) -> float:
    return _entropy(outcome, *condition) - _entropy(*condition)


def _conditional_mutual_information(
    first: np.ndarray,
    second: np.ndarray,
    *condition: np.ndarray,
) -> float:
    return (
        _entropy(first, *condition)
        + _entropy(second, *condition)
        - _entropy(*condition)
        - _entropy(first, second, *condition)
    )


def _branch_estimates(
    observations: np.ndarray,
    cues: np.ndarray,
    groups: np.ndarray,
    *,
    spec: JunctionFlowSpec,
) -> dict[str, Any]:
    incoming_labels = []
    outgoing_labels = []
    for view in observations:
        node = view[..., 1, :]
        incoming_vectors = node - view[..., 0, :]
        outgoing_vectors = view[..., 2, :] - node
        combined = np.concatenate([
            incoming_vectors.reshape(-1, spec.ambient),
            outgoing_vectors.reshape(-1, spec.ambient),
        ])
        labels = _angular_labels(combined, branches=spec.branches)
        split = incoming_vectors.size // spec.ambient
        incoming_labels.append(
            labels[:split].reshape(incoming_vectors.shape[:-1])
        )
        outgoing_labels.append(
            labels[split:].reshape(outgoing_vectors.shape[:-1])
        )
    incoming_labels = np.asarray(incoming_labels)
    outgoing_labels = np.asarray(outgoing_labels)
    ari = []
    for left, right in combinations(range(spec.views), 2):
        ari.append(adjusted_rand_score(
            outgoing_labels[left].ravel(),
            outgoing_labels[right].ravel(),
        ))

    group_grid = np.broadcast_to(
        groups[:, None, None],
        cues.shape,
    )
    depth_grid = np.broadcast_to(
        np.arange(spec.depth)[None, None, :],
        cues.shape,
    )
    log_k = np.log(spec.branches)
    cue_information = []
    passthrough_information = []
    residual_entropy = []
    branch_entropy = []
    for view in range(spec.views):
        incoming = incoming_labels[view].ravel()
        outgoing = outgoing_labels[view].ravel()
        cue = cues.ravel()
        group = group_grid.ravel()
        depth = depth_grid.ravel()
        cue_information.append(
            _conditional_mutual_information(
                outgoing,
                cue,
                incoming,
                group,
                depth,
            )
            / log_k
        )
        passthrough_information.append(
            _conditional_mutual_information(
                outgoing,
                incoming,
                cue,
                group,
                depth,
            )
            / log_k
        )
        residual_entropy.append(
            _conditional_entropy(
                outgoing,
                incoming,
                cue,
                group,
                depth,
            )
            / log_k
        )
        branch_entropy.append(
            _conditional_entropy(outgoing, group, depth) / log_k
        )
    return {
        "incoming_labels": incoming_labels,
        "outgoing_labels": outgoing_labels,
        "cue_information": float(np.median(cue_information)),
        "passthrough_information": float(
            np.median(passthrough_information)
        ),
        "residual_entropy": float(np.median(residual_entropy)),
        "branch_entropy": float(np.median(branch_entropy)),
        "cross_view_ari": float(np.median(ari)),
    }


def _classify_policy(
    branch: dict[str, Any],
    *,
    spec: JunctionFlowSpec,
) -> str:
    cue = branch["cue_information"]
    passthrough = branch["passthrough_information"]
    residual = branch["residual_entropy"]
    high = spec.target_information_threshold
    low = spec.nontarget_information_threshold
    if cue >= high and passthrough <= low and residual <= low:
        return "cue_guided"
    if passthrough >= high and cue <= low and residual <= low:
        return "pass_through"
    if residual >= spec.residual_entropy_threshold and cue <= low and passthrough <= low:
        return "random_branch"
    return "UNRESOLVED"


def _nearest_centroid_stage_accuracy(
    observations: np.ndarray,
    times: np.ndarray,
    *,
    include_time: bool,
    spec: JunctionFlowSpec,
) -> float:
    nodes = observations.mean(axis=0)[..., 1, :]
    train = np.arange(spec.episodes) % 2 == 0
    test = ~train
    train_features = nodes[:, train].reshape(-1, spec.ambient)
    test_features = nodes[:, test].reshape(-1, spec.ambient)
    train_labels = np.broadcast_to(
        np.arange(spec.depth)[None, None, :],
        (spec.authors, int(train.sum()), spec.depth),
    ).ravel()
    test_labels = np.broadcast_to(
        np.arange(spec.depth)[None, None, :],
        (spec.authors, int(test.sum()), spec.depth),
    ).ravel()
    if include_time:
        train_time = times[:, train].reshape(-1, 1) * spec.time_weight
        test_time = times[:, test].reshape(-1, 1) * spec.time_weight
        train_features = np.column_stack([train_features, train_time])
        test_features = np.column_stack([test_features, test_time])
    centroids = np.asarray([
        train_features[train_labels == stage].mean(axis=0)
        for stage in range(spec.depth)
    ])
    distance = np.linalg.norm(
        test_features[:, None, :] - centroids[None, :, :],
        axis=-1,
    )
    predicted = np.argmin(distance, axis=1)
    return float(np.mean(predicted == test_labels))


def _channel_capacity(channel: np.ndarray) -> float:
    """Blahut-Arimoto capacity in bits for one finite cue-output channel."""
    channel = np.maximum(channel, 1e-12)
    channel /= channel.sum(axis=1, keepdims=True)
    prior = np.full(channel.shape[0], 1.0 / channel.shape[0])
    for _ in range(200):
        output = prior @ channel
        divergence = np.sum(
            channel * np.log2(channel / output[None, :]),
            axis=1,
        )
        updated = 2.0**divergence
        updated /= updated.sum()
        if np.max(abs(updated - prior)) < 1e-12:
            prior = updated
            break
        prior = updated
    output = prior @ channel
    return float(np.sum(
        prior[:, None]
        * channel
        * np.log2(channel / output[None, :])
    ))


def _tree_metrics(
    outgoing: np.ndarray,
    cues: np.ndarray,
    *,
    spec: JunctionFlowSpec,
) -> dict[str, Any]:
    paths = outgoing.reshape(-1, spec.depth)
    cue_paths = cues.reshape(-1, spec.depth)
    path_entropy = _entropy(
        np.asarray([
            sum(
                int(value) * spec.branches**index
                for index, value in enumerate(path)
            )
            for path in paths
        ])
    )
    effective_fraction = float(
        np.exp(path_entropy) / spec.branches**spec.depth
    )
    episode_train = np.arange(spec.episodes) % 2 == 0
    episode_test = ~episode_train
    train_cue = cues[:, episode_train].ravel()
    train_out = outgoing[:, episode_train].ravel()
    channel = np.zeros((spec.branches, spec.branches), dtype=float)
    for cue in range(spec.branches):
        counts = np.bincount(
            train_out[train_cue == cue],
            minlength=spec.branches,
        )
        channel[cue] = counts / counts.sum()
    rows, columns = linear_sum_assignment(-channel)
    output_to_cue = np.full(spec.branches, -1, dtype=int)
    output_to_cue[columns] = rows
    decoded = output_to_cue[outgoing[:, episode_test]]
    goal_accuracy = float(np.mean(np.all(
        decoded == cues[:, episode_test],
        axis=-1,
    )))
    capacity = _channel_capacity(channel)
    addressable = 0
    for cue_path in product(range(spec.branches), repeat=spec.depth):
        probability = float(np.prod([
            channel[cue, columns[np.flatnonzero(rows == cue)[0]]]
            for cue in cue_path
        ]))
        addressable += int(probability >= 0.80)
    return {
        "effective_leaf_fraction": effective_fraction,
        "goal_path_accuracy": goal_accuracy,
        "cue_channel_capacity_bits": capacity,
        "addressable_leaves": addressable,
    }


def static_marginal_features(
    sample: dict[str, Any],
    *,
    spec: JunctionFlowSpec,
) -> np.ndarray:
    """Return summaries that intentionally omit event-level correspondence."""
    observations = sample["observations"]
    node = observations[..., 1, :]
    pre = observations[..., 0, :]
    post = observations[..., 2, :]
    incoming_length = np.linalg.norm(node - pre, axis=-1)
    outgoing_length = np.linalg.norm(post - node, axis=-1)
    features = []
    for values in (
        sample["cues"],
        sample["incoming"],
        sample["outgoing"],
    ):
        features.extend(
            np.bincount(values.ravel(), minlength=spec.branches)
            / values.size
        )
    features.extend([
        float(node.mean()),
        float(node.std()),
        float(incoming_length.mean()),
        float(incoming_length.std()),
        float(outgoing_length.mean()),
        float(outgoing_length.std()),
    ])
    return np.asarray(features, dtype=float)


def analyze_junction_world(
    sample: dict[str, Any],
    *,
    spec: JunctionFlowSpec,
) -> dict[str, Any]:
    """Estimate common junctions, routing regime, and tree behavior."""
    node = _node_estimate(
        sample["observations"],
        sample["labels"],
        spec=spec,
    )
    branch = _branch_estimates(
        sample["observations"],
        sample["cues"],
        sample["labels"],
        spec=spec,
    )
    true_depth = np.broadcast_to(
        np.arange(spec.depth)[None, None, :],
        sample["observed_times"].shape,
    ).ravel()
    tau = kendalltau(
        true_depth,
        sample["observed_times"].ravel(),
    ).statistic
    time_tau = float(0.0 if not np.isfinite(tau) else tau)
    predicted_policy = _classify_policy(branch, spec=spec)
    if not node["group_claim"]:
        status = "REFUSE_NO_JUNCTION"
    elif time_tau < spec.minimum_time_tau:
        status = "REFUSE_TIME_ORDER"
    elif branch["cross_view_ari"] < spec.minimum_view_ari:
        status = "REFUSE_VIEW_INSTABILITY"
    elif predicted_policy == "UNRESOLVED":
        status = "REFUSE_ROUTING_UNRESOLVED"
    else:
        status = "ESTIMATE_READY"
    tree = _tree_metrics(
        branch["outgoing_labels"][0],
        sample["cues"],
        spec=spec,
    )
    return {
        "status": status,
        "predicted_policy": predicted_policy,
        "cue_guided_claim": bool(
            status == "ESTIMATE_READY"
            and predicted_policy == "cue_guided"
        ),
        "time_tau": time_tau,
        "x_only_stage_accuracy": _nearest_centroid_stage_accuracy(
            sample["observations"],
            sample["observed_times"],
            include_time=False,
            spec=spec,
        ),
        "spacetime_stage_accuracy": _nearest_centroid_stage_accuracy(
            sample["observations"],
            sample["observed_times"],
            include_time=True,
            spec=spec,
        ),
        "static_marginal_features": static_marginal_features(
            sample,
            spec=spec,
        ),
        **node,
        **{
            key: value for key, value in branch.items()
            if key not in {"incoming_labels", "outgoing_labels"}
        },
        **tree,
    }
