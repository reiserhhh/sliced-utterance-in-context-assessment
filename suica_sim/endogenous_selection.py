"""Synthetic identifiability test for choice-preserving SUICA measurement.

The point of this world is not to simulate personality.  It demonstrates a
mathematical design fact: when an author's condition choice depends on their
latent author location, a population condition mean contains selection-linked
author variation.  Blindly subtracting that mean changes the estimand.  A
two-phase design keeps free choice as one object and estimates conditional
expression on independently assigned conditions as another.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class EndogenousSelectionWorld:
    """A free-choice plus fixed-condition world with known numeric truth."""

    true_author_level: np.ndarray
    true_response: np.ndarray
    selection_probability: np.ndarray
    free_condition: np.ndarray
    free_y: np.ndarray
    fixed_condition: np.ndarray
    fixed_y: np.ndarray


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - values.max(axis=1, keepdims=True)
    weights = np.exp(shifted)
    return weights / weights.sum(axis=1, keepdims=True)


def _corr(left: np.ndarray, right: np.ndarray) -> float:
    """Return a finite flattened Pearson correlation or NaN when undefined."""
    a, b = np.asarray(left, float).ravel(), np.asarray(right, float).ravel()
    if len(a) < 3 or np.std(a) < 1e-12 or np.std(b) < 1e-12:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def generate_endogenous_selection_world(
    seed: int,
    *,
    persons: int,
    features: int,
    conditions: int,
    free_trials: int,
    fixed_repeats: int,
    selection_strength: float,
    condition_scale: float,
    noise_scale: float,
) -> EndogenousSelectionWorld:
    r"""Generate free selected and independently assigned fixed observations.

    The free choice model is

    \[
    C_{ui} \sim \operatorname{Categorical}\{\operatorname{softmax}
       (\lambda L a_u + \eta_u)\},
    \]

    while expression is

    \[
    Y_{ui} = a_u + \mu_{C_{ui}} + B_{u,C_{ui}} + \epsilon_{ui}.
    \]

    In the fixed phase every author receives every condition equally often,
    independently of `a_u`.  Response slices are centered over conditions so
    the author intercept and response contrasts are separately defined.
    """
    rng = np.random.default_rng(seed)
    author = rng.normal(0.0, 0.65, size=(persons, features))
    response = rng.normal(0.0, 0.26, size=(persons, features, conditions))
    response -= response.mean(axis=2, keepdims=True)
    condition_mean = rng.normal(0.0, condition_scale, size=(conditions, features))
    condition_mean -= condition_mean.mean(axis=0, keepdims=True)

    loading = rng.normal(size=(conditions, features))
    loading -= loading.mean(axis=0, keepdims=True)
    loading /= np.maximum(np.linalg.norm(loading, axis=1, keepdims=True), 1e-12)
    preference = rng.normal(0.0, 0.25, size=(persons, conditions))
    selection_probability = _softmax(selection_strength * (author @ loading.T) + preference)
    free_condition = np.vstack([
        rng.choice(conditions, size=free_trials, replace=True, p=selection_probability[user])
        for user in range(persons)
    ])
    fixed_condition = np.vstack([
        np.concatenate([rng.permutation(conditions) for _ in range(fixed_repeats)])
        for _ in range(persons)
    ])

    def observe(condition: np.ndarray) -> np.ndarray:
        selected_response = np.take_along_axis(
            response,
            condition[:, None, :],
            axis=2,
        ).transpose(0, 2, 1)
        return (
            author[:, None, :]
            + condition_mean[condition]
            + selected_response
            + rng.normal(0.0, noise_scale, size=(persons, condition.shape[1], features))
        )

    return EndogenousSelectionWorld(
        true_author_level=author,
        true_response=response,
        selection_probability=selection_probability,
        free_condition=free_condition,
        free_y=observe(free_condition),
        fixed_condition=fixed_condition,
        fixed_y=observe(fixed_condition),
    )


def _discovery_mask(persons: int) -> np.ndarray:
    """Return a deterministic disjoint discovery/confirmation author split."""
    return np.arange(persons) % 2 == 0


def _condition_reference(y: np.ndarray, condition: np.ndarray, discovery: np.ndarray,
                         conditions: int) -> np.ndarray:
    """Fit condition means on discovery authors only."""
    reference = np.empty((conditions, y.shape[2]), dtype=float)
    for value in range(conditions):
        values = y[discovery][condition[discovery] == value]
        if not len(values):
            raise ValueError("Discovery split does not support every condition")
        reference[value] = values.mean(axis=0)
    return reference


def _author_level(y: np.ndarray, condition: np.ndarray, reference: np.ndarray) -> np.ndarray:
    return np.mean(y - reference[condition], axis=1)


def _response_contrasts(y: np.ndarray, condition: np.ndarray, reference: np.ndarray,
                        conditions: int) -> tuple[np.ndarray, np.ndarray]:
    """Estimate author x condition contrasts; refuse users without full support."""
    output = np.full((len(y), y.shape[2], conditions), np.nan)
    supported = np.zeros(len(y), dtype=bool)
    adjusted = y - reference[condition]
    for user in range(len(y)):
        means = np.empty((conditions, y.shape[2]))
        for value in range(conditions):
            values = adjusted[user][condition[user] == value]
            if not len(values):
                break
            means[value] = values.mean(axis=0)
        else:
            output[user] = (means - means.mean(axis=0, keepdims=True)).T
            supported[user] = True
    return output, supported


def _selection_metrics(world: EndogenousSelectionWorld, confirmation: np.ndarray) -> dict[str, float]:
    """Score a free-choice profile on held-out choices without labels."""
    conditions = world.selection_probability.shape[1]
    cut = world.free_condition.shape[1] // 2
    train, test = world.free_condition[:, :cut], world.free_condition[:, cut:]
    discovery = ~confirmation
    global_counts = np.bincount(train[discovery].ravel(), minlength=conditions).astype(float) + 1.0
    global_probability = global_counts / global_counts.sum()
    gains: list[float] = []
    fitted_profiles, truth = [], []
    for user in np.flatnonzero(confirmation):
        counts = np.bincount(train[user], minlength=conditions).astype(float) + 1.0
        profile = counts / counts.sum()
        gains.append(float(np.mean(np.log(profile[test[user]]) - np.log(global_probability[test[user]]))))
        fitted_profiles.append(profile)
        truth.append(world.selection_probability[user])
    return {
        "selection_holdout_logscore_gain": float(np.mean(gains)),
        "selection_profile_truth_r": _corr(np.asarray(fitted_profiles), np.asarray(truth)),
    }


def evaluate_endogenous_selection_world(world: EndogenousSelectionWorld) -> dict[str, float]:
    """Evaluate raw, naively centred, and two-phase estimands on held-out authors."""
    persons = len(world.true_author_level)
    conditions = world.selection_probability.shape[1]
    discovery = _discovery_mask(persons)
    confirmation = ~discovery

    free_reference = _condition_reference(world.free_y, world.free_condition, discovery, conditions)
    fixed_reference = _condition_reference(world.fixed_y, world.fixed_condition, discovery, conditions)
    raw_level = world.free_y.mean(axis=1)
    centered_free_level = _author_level(world.free_y, world.free_condition, free_reference)
    fixed_level = _author_level(world.fixed_y, world.fixed_condition, fixed_reference)
    free_response, free_supported = _response_contrasts(
        world.free_y, world.free_condition, free_reference, conditions
    )
    fixed_response, fixed_supported = _response_contrasts(
        world.fixed_y, world.fixed_condition, fixed_reference, conditions
    )
    result = {
        "raw_free_level_recovery_r": _corr(raw_level[confirmation], world.true_author_level[confirmation]),
        "free_condition_centered_level_recovery_r": _corr(
            centered_free_level[confirmation], world.true_author_level[confirmation]
        ),
        "fixed_condition_level_recovery_r": _corr(
            fixed_level[confirmation], world.true_author_level[confirmation]
        ),
        "free_response_support": float(np.mean(free_supported[confirmation])),
        "fixed_response_support": float(np.mean(fixed_supported[confirmation])),
        "free_response_recovery_r": _corr(
            free_response[confirmation & free_supported],
            world.true_response[confirmation & free_supported],
        ),
        "fixed_response_recovery_r": _corr(
            fixed_response[confirmation & fixed_supported],
            world.true_response[confirmation & fixed_supported],
        ),
    }
    result.update(_selection_metrics(world, confirmation))
    return result


def _summary(rows: list[dict[str, float]]) -> dict[str, dict[str, float]]:
    """Summarize repetition-level outcomes with a central 95% simulation interval."""
    keys = rows[0].keys()
    return {
        key: {
            "mean": float(np.nanmean([row[key] for row in rows])),
            "q025": float(np.nanquantile([row[key] for row in rows], 0.025)),
            "q975": float(np.nanquantile([row[key] for row in rows], 0.975)),
        }
        for key in keys
    }


def run_endogenous_selection_design(config: dict[str, Any]) -> dict[str, Any]:
    """Run the two complementary simulation worlds under frozen parameters."""
    common = {
        key: config[key]
        for key in ("persons", "features", "conditions", "free_trials", "fixed_repeats", "noise_scale")
    }
    worlds = {
        "selection_signal": {
            "selection_strength": config["selection_signal_strength"],
            "condition_scale": config["selection_signal_condition_scale"],
        },
        "condition_nuisance": {
            "selection_strength": config["condition_nuisance_selection_strength"],
            "condition_scale": config["condition_nuisance_condition_scale"],
        },
    }
    output: dict[str, Any] = {"profile": config["profile"], "config": config, "worlds": {}}
    for offset, (name, parameters) in enumerate(worlds.items()):
        rows = [
            evaluate_endogenous_selection_world(
                generate_endogenous_selection_world(
                    config["seed"] + offset * 100_000 + replicate,
                    **common,
                    **parameters,
                )
            )
            for replicate in range(config["repetitions"])
        ]
        output["worlds"][name] = {"summary": _summary(rows), "n_repetitions": len(rows)}

    selection = output["worlds"]["selection_signal"]["summary"]
    nuisance = output["worlds"]["condition_nuisance"]["summary"]
    output["gates"] = {
        "selection_channel_is_predictable": selection["selection_holdout_logscore_gain"]["q025"] > 0.0,
        "selection_linked_centering_changes_level": (
            selection["raw_free_level_recovery_r"]["q025"]
            > selection["free_condition_centered_level_recovery_r"]["q975"]
        ),
        "condition_only_centering_can_help": (
            nuisance["free_condition_centered_level_recovery_r"]["q025"]
            > nuisance["raw_free_level_recovery_r"]["q975"]
        ),
        "fixed_phase_recovers_response": (
            selection["fixed_response_support"]["q025"] >= 0.99
            and selection["fixed_response_recovery_r"]["q025"] >= config["minimum_fixed_response_recovery"]
            and nuisance["fixed_response_recovery_r"]["q025"] >= config["minimum_fixed_response_recovery"]
        ),
        "free_phase_has_incomplete_response_support": (
            selection["free_response_support"]["q975"] < config["maximum_free_response_support"]
        ),
    }
    return output
