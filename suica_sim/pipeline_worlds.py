"""Raw-like synthetic worlds for the SIM-P0..P6 falsification pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class PipelineData:
    person: np.ndarray
    occasion: np.ndarray
    window: np.ndarray
    counts: np.ndarray
    opportunity: np.ndarray
    format_covariates: np.ndarray
    context_covariates: np.ndarray
    truth_axis: np.ndarray
    world: str
    metadata: dict[str, Any]


def _orthonormal(rng: np.random.Generator, rows: int, rank: int) -> np.ndarray:
    q, _ = np.linalg.qr(rng.normal(size=(rows, rank)))
    return q[:, :rank]


def generate_pipeline_world(
    seed: int,
    world: str,
    *,
    persons: int = 72,
    occasions: int = 4,
    windows: int = 6,
    constructs: int = 4,
    segmentation: str = "fixed",
    jitter: float = 0.0,
    signal_scale: float = 1.0,
    static_scale: float = 0.45,
) -> PipelineData:
    """Generate person x occasion x window raw counts and opportunities.

    Nulls are genuine DGP worlds: they do not receive a planted person axis.
    Opportunity-only worlds change exposure while holding response probability
    person-invariant.  This distinction is intentionally made before fitting.
    """
    rng = np.random.default_rng(seed)
    if segmentation not in {"fixed", "equal_opportunity", "event"}:
        raise ValueError("unknown segmentation strategy")
    n = persons * occasions * windows
    person = np.repeat(np.arange(persons), occasions * windows)
    occasion = np.tile(np.repeat(np.arange(occasions), windows), persons)
    window = np.tile(np.arange(windows), persons * occasions)
    stable_format = rng.normal(scale=.55, size=(persons, 2))
    fmt = stable_format[person] + rng.normal(scale=.65, size=(n, 2))
    ctx_occ = rng.normal(size=(persons, occasions, 2))
    context = ctx_occ[person, occasion] + rng.normal(scale=.15, size=(n, 2))

    stable_opportunity = rng.normal(scale=.45, size=persons)
    base_opp = np.exp(2.0 + stable_opportunity[person] + .28 * fmt[:, 0] + .18 * context[:, 0])
    if segmentation == "equal_opportunity":
        base_opp[:] = np.median(base_opp)
    elif segmentation == "event":
        base_opp *= np.exp(.32 * np.sin((window + 1) * np.pi / windows))
    if world in {"P6_opportunity", "P2_artifact"}:
        exposure = rng.normal(scale=.75, size=persons)
        base_opp *= np.exp(exposure[person] * np.linspace(-.65, .65, windows)[window])
    opportunity = np.maximum(1, rng.poisson(base_opp)).astype(int)

    axis = _orthonormal(rng, constructs, min(2, constructs))
    dynamic = np.zeros((persons, occasions, windows, axis.shape[1]))
    person_amp = np.zeros((persons, axis.shape[1]))
    person_worlds = {"P0_alt", "P3_lowrank", "P4_person", "P5_alt", "P6_person"}
    if world in person_worlds:
        person_amp = rng.normal(scale=.85 * signal_scale, size=person_amp.shape)
        phase = rng.uniform(0, 2 * np.pi, size=(persons, axis.shape[1]))
        occasion_noise = rng.normal(scale=.10, size=(persons, occasions, axis.shape[1]))
        for o in range(occasions):
            for w in range(windows):
                dynamic[:, o, w, :] = (person_amp + occasion_noise[:, o, :]) * np.sin(
                    2 * np.pi * w / windows + phase
                )
    elif world == "P2_artifact":
        # Boundary jitter coupled to person exposure creates a detectable fake axis.
        artifact = rng.normal(size=(persons, axis.shape[1]))
        for w in range(windows):
            dynamic[:, :, w, :] = jitter * artifact[:, None, :] * ((-1.0) ** w)

    static = rng.normal(scale=static_scale, size=(persons, constructs))
    if world in {"P0_null", "P3_null", "P4_context", "P5_null", "P6_opportunity", "P1"}:
        person_amp[:] = 0.0
    logits = (-1.35 + static[person] + .30 * fmt[:, [0]] - .24 * context[:, [0]])
    logits += np.einsum("nr,cr->nc", dynamic[person, occasion, window], axis)
    prob = 1 / (1 + np.exp(-np.clip(logits, -8, 8)))
    counts = rng.binomial(opportunity[:, None], prob)
    return PipelineData(
        person, occasion, window, counts, opportunity, fmt, context, axis,
        world,
        {"seed": seed, "segmentation": segmentation, "jitter": jitter,
         "person_amplitude": float(np.mean(np.linalg.norm(person_amp, axis=1))),
         "opportunity_observed": world != "P1_hidden"},
    )


def matched_strangers(data: PipelineData, rng: np.random.Generator) -> np.ndarray:
    """Match each person to a different person with similar exposure/context."""
    ids = np.unique(data.person)
    support = np.column_stack([
        [data.opportunity[data.person == u].mean() for u in ids],
        [data.context_covariates[data.person == u, 0].mean() for u in ids],
    ])
    support = (support - support.mean(0)) / np.maximum(support.std(0), 1e-9)
    result = np.empty(len(ids), dtype=int)
    for i, u in enumerate(ids):
        distance = np.sum((support - support[i]) ** 2, axis=1)
        distance[i] = np.inf
        candidates = np.flatnonzero(distance <= np.quantile(distance[np.isfinite(distance)], .25))
        result[i] = ids[rng.choice(candidates)] if len(candidates) else ids[np.argmin(distance)]
    if np.any(result == ids):
        raise RuntimeError("matched-stranger support includes self matches")
    return result
