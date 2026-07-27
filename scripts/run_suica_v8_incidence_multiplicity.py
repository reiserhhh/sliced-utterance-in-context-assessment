#!/usr/bin/env python3
"""Run SUICA V8 persistent incidence-multiplicity planted worlds."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta
from sklearn.metrics import adjusted_rand_score, f1_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_incidence_multiplicity import (  # noqa: E402
    MultiplicitySpec,
    analyze_population,
    condition_reparameterization_consistency,
    simulate_population,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _spec(config: dict[str, Any], noise_sd: float) -> MultiplicitySpec:
    return MultiplicitySpec(
        authors=int(config["authors"]),
        groups=int(config["groups"]),
        conditions=int(config["conditions"]),
        halves=int(config["halves"]),
        observers=int(config["observers"]),
        noise_sd=float(noise_sd),
        ridge_alpha=float(config["ridge_alpha"]),
        epsilon_grid=tuple(
            float(item) for item in config["epsilon_grid"]
        ),
    )


def _all_primary_worlds(config: dict[str, Any]) -> list[str]:
    return [
        *config["clear_group_worlds"],
        *config["boundary_worlds"],
        *config["null_worlds"],
        *config["attack_worlds"],
    ]


def _seed(
    config: dict[str, Any],
    stage: str,
    world_index: int,
    repetition: int,
) -> int:
    offsets = {
        "discovery": 0,
        "calibration": 10_000_000,
        "confirmation": 20_000_000,
        "challenge": 30_000_000,
        "sensitivity": 40_000_000,
    }
    return (
        int(config["seed"])
        + offsets[stage]
        + 100_000 * int(world_index)
        + int(repetition)
    )


def _payload_worker(
    payload: tuple[
        dict[str, Any], str, str, int, int, float,
    ],
) -> dict[str, Any]:
    config, stage, world, world_index, repetition, noise_sd = payload
    seed = _seed(config, stage, world_index, repetition)
    spec = _spec(config, noise_sd)
    population = simulate_population(
        seed=seed,
        world=world,
        spec=spec,
        noise_sd=noise_sd,
    )
    result = analyze_population(
        population,
        ridge_alpha=spec.ridge_alpha,
        epsilon_grid=spec.epsilon_grid,
    )
    reparameterization = float("nan")
    if result["status"] == "ESTIMATE_READY" and stage in {
        "confirmation",
        "challenge",
    }:
        reparameterization = condition_reparameterization_consistency(
            population,
            ridge_alpha=spec.ridge_alpha,
        )
    return {
        "stage": stage,
        "seed": seed,
        "repetition": repetition,
        "noise_sd": noise_sd,
        "reparameterization_consistency": reparameterization,
        **result,
    }


def _parallel(
    payloads: list[Any],
    *,
    jobs: int,
) -> list[dict[str, Any]]:
    if jobs <= 1:
        return [_payload_worker(item) for item in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(
            _payload_worker,
            payloads,
            chunksize=2,
        ))


def _run_stage(
    config: dict[str, Any],
    *,
    stage: str,
    worlds: list[str],
    repetitions: int,
    noise_sd: float,
) -> list[dict[str, Any]]:
    payloads = [
        (
            config,
            stage,
            world,
            world_index,
            repetition,
            noise_sd,
        )
        for world_index, world in enumerate(worlds)
        for repetition in range(repetitions)
    ]
    return _parallel(payloads, jobs=int(config["jobs"]))


def _calibrate(
    calibration: list[dict[str, Any]],
    config: dict[str, Any],
) -> tuple[dict[str, float], pd.DataFrame]:
    ready = [
        row for row in calibration
        if row["status"] == "ESTIMATE_READY"
    ]
    clean = [
        row for row in ready
        if row["kind"] != "attack"
    ]
    diagnostics = _calibrate_population_threshold(
        calibration,
        authors=int(config["authors"]),
        minimum_coverage=float(
            config["minimum_group_coverage_for_claim"]
        ),
        gates=config["gates"],
        allow_small_sample_proxy=bool(config.get("_smoke", False)),
    )
    selected = diagnostics[diagnostics["selected"]]
    if len(selected) != 1:
        raise RuntimeError(
            "population-level hyperedge threshold calibration failed"
        )
    thresholds = {
        "maximum_residual_fraction": float(np.quantile(
            [row["residual_fraction"] for row in clean],
            0.999,
        )),
        "minimum_support": float(np.quantile(
            [row["minimum_support"] for row in clean],
            0.005,
        )),
        "minimum_cross_view_spearman": float(np.quantile(
            [row["cross_view_spearman"] for row in clean],
            0.005,
        )),
        "hyperedge_persistence_threshold": float(
            selected["threshold"].iloc[0]
        ),
        "minimum_group_coverage_for_claim": float(
            config["minimum_group_coverage_for_claim"]
        ),
    }
    return thresholds, diagnostics


def _true_partition(
    pair_labels: np.ndarray,
    authors: int,
) -> np.ndarray:
    adjacency = np.zeros((authors, authors), dtype=bool)
    upper = np.triu_indices(authors, 1)
    adjacency[upper] = np.asarray(pair_labels, dtype=bool)
    adjacency[(upper[1], upper[0])] = adjacency[upper]
    labels = np.zeros(authors, dtype=int)
    assigned = np.zeros(authors, dtype=bool)
    next_label = 0
    for author in range(authors):
        if assigned[author]:
            continue
        members = np.flatnonzero(
            adjacency[author] | (np.arange(authors) == author)
        )
        labels[members] = next_label
        assigned[members] = True
        next_label += 1
    return labels


def _threshold_row_metrics(
    row: dict[str, Any],
    *,
    threshold: float,
    authors: int,
    minimum_coverage: float,
) -> dict[str, float | bool]:
    selected = [
        item for item in row["hyperedges"]
        if (
            len(item["members"]) >= 3
            and float(item["persistence"]) >= threshold
        )
    ]
    predicted = _components(authors, selected)
    sizes = np.bincount(predicted)
    structured = sizes[sizes >= 3]
    coverage = (
        float(np.sum(structured) / authors)
        if len(structured)
        else 0.0
    )
    claim = bool(
        len(structured) >= 2 and coverage >= minimum_coverage
    )
    output: dict[str, float | bool] = {
        "claim": claim,
        "coverage": coverage,
        "f1": float("nan"),
        "ari": float("nan"),
    }
    if row["kind"] == "clear_group":
        pair_labels = np.asarray(row["pair_labels"], dtype=int)
        upper = np.triu_indices(authors, 1)
        predicted_pairs = (
            predicted[upper[0]] == predicted[upper[1]]
        ).astype(int)
        output["f1"] = float(f1_score(
            pair_labels,
            predicted_pairs,
            zero_division=0,
        ))
        output["ari"] = float(adjusted_rand_score(
            _true_partition(pair_labels, authors),
            predicted,
        ))
    return output


def _calibrate_population_threshold(
    calibration: list[dict[str, Any]],
    *,
    authors: int,
    minimum_coverage: float,
    gates: dict[str, Any],
    allow_small_sample_proxy: bool = False,
) -> pd.DataFrame:
    """Select a population-claim threshold, not a max local-edge threshold."""
    ready = [
        row for row in calibration
        if row["status"] == "ESTIMATE_READY"
        and row["kind"] in {"clear_group", "null"}
    ]
    values = np.asarray([
        float(item["persistence"])
        for row in ready
        for item in row["hyperedges"]
        if len(item["members"]) >= 3
    ])
    if not len(values):
        raise RuntimeError("no calibration hyperedges available")
    candidates = np.unique(np.concatenate([
        np.linspace(0.01, min(float(np.max(values)), 0.80), 100),
        np.quantile(values, np.linspace(0.05, 0.995, 80)),
    ]))
    rows = []
    clear_worlds = sorted({
        row["world"] for row in ready
        if row["kind"] == "clear_group"
    })
    null_worlds = sorted({
        row["world"] for row in ready
        if row["kind"] == "null"
    })
    null_rows = [row for row in ready if row["kind"] == "null"]
    for threshold in candidates:
        per_row = [
            (
                row,
                _threshold_row_metrics(
                    row,
                    threshold=float(threshold),
                    authors=authors,
                    minimum_coverage=minimum_coverage,
                ),
            )
            for row in ready
        ]
        null_claims = sum(
            bool(metrics["claim"])
            for row, metrics in per_row
            if row["kind"] == "null"
        )
        null_world_counts = {}
        null_world_uppers = {}
        for world in null_worlds:
            current = [
                bool(metrics["claim"])
                for row, metrics in per_row
                if row["world"] == world
            ]
            claims = int(sum(current))
            null_world_counts[world] = claims
            null_world_uppers[world] = _one_sided_upper(
                claims,
                len(current),
            )
        worst_null_world = max(
            null_world_uppers,
            key=null_world_uppers.get,
        )
        f1_by_world = []
        ari_by_world = []
        claim_by_world = []
        for world in clear_worlds:
            current = [
                metrics for row, metrics in per_row
                if row["world"] == world
            ]
            f1_by_world.append(float(np.median([
                item["f1"] for item in current
            ])))
            ari_by_world.append(float(np.median([
                item["ari"] for item in current
            ])))
            claim_by_world.append(float(np.mean([
                item["claim"] for item in current
            ])))
        rows.append({
            "threshold": float(threshold),
            "null_claims": int(null_claims),
            "null_trials": len(null_rows),
            "null_false_upper_95": _one_sided_upper(
                int(null_claims),
                len(null_rows),
            ),
            "maximum_null_world_upper_95": float(
                null_world_uppers[worst_null_world]
            ),
            "maximum_null_world_claim_rate": float(max(
                null_world_counts[world]
                / max(
                    sum(
                        row["world"] == world
                        for row in null_rows
                    ),
                    1,
                )
                for world in null_worlds
            )),
            "worst_null_world": worst_null_world,
            "null_claims_by_world": json.dumps(
                null_world_counts,
                sort_keys=True,
            ),
            "minimum_clear_world_f1_median": min(f1_by_world),
            "minimum_clear_world_ari_median": min(ari_by_world),
            "minimum_clear_world_claim_rate": min(claim_by_world),
        })
    frame = pd.DataFrame(rows)
    frame["null_control_pass"] = frame[
        "maximum_null_world_upper_95"
    ].le(
        float(gates["maximum_false_group_upper_95"])
    )
    if allow_small_sample_proxy:
        # Smoke runs cannot estimate a 3% binomial upper bound. Zero observed
        # claims is only a preflight proxy; the full run must pass the bound.
        frame["null_control_pass"] = (
            frame["null_control_pass"] | frame["null_claims"].eq(0)
        )
    frame["clear_recovery_pass"] = (
        frame["minimum_clear_world_f1_median"].ge(
            float(gates["minimum_group_f1"])
        )
        & frame["minimum_clear_world_ari_median"].ge(
            float(gates["minimum_group_ari"])
        )
        & frame["minimum_clear_world_claim_rate"].ge(0.80)
    )
    valid = frame[
        frame["null_control_pass"]
        & frame["clear_recovery_pass"]
    ]
    frame["selected"] = False
    if len(valid):
        best_f1 = float(valid["minimum_clear_world_f1_median"].max())
        finalists = valid[
            valid["minimum_clear_world_f1_median"].ge(best_f1 - 1e-12)
        ]
        best = finalists.sort_values("threshold").iloc[0]
    else:
        # Fail closed: retain the strictest tested threshold and let the
        # confirmation decision report the unresolved calibration.
        best = frame.sort_values("threshold", ascending=False).iloc[0]
    frame.loc[best.name, "selected"] = True
    return frame


def _quality_refusal(
    row: dict[str, Any],
    thresholds: dict[str, float],
) -> str:
    if row["status"] != "ESTIMATE_READY":
        return str(row["status"])
    if (
        float(row["residual_fraction"])
        > thresholds["maximum_residual_fraction"]
    ):
        return "RESIDUAL_TOO_LARGE"
    if float(row["minimum_support"]) < thresholds["minimum_support"]:
        return "CONDITION_SUPPORT_INSUFFICIENT"
    if (
        float(row["cross_view_spearman"])
        < thresholds["minimum_cross_view_spearman"]
    ):
        return "CROSS_VIEW_INCIDENCE_UNSTABLE"
    return ""


def _components(
    authors: int,
    hyperedges: list[dict[str, Any]],
) -> np.ndarray:
    parent = np.arange(authors, dtype=int)

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = int(parent[item])
        return item

    def union(left: int, right: int) -> None:
        root_left = find(left)
        root_right = find(right)
        if root_left != root_right:
            parent[root_right] = root_left

    for hyperedge in hyperedges:
        members = [int(item) for item in hyperedge["members"]]
        for member in members[1:]:
            union(members[0], member)
    roots = np.asarray([find(index) for index in range(authors)])
    _, labels = np.unique(roots, return_inverse=True)
    return labels


def _one_sided_upper(successes: int, trials: int) -> float:
    if trials <= 0:
        return 1.0
    if successes >= trials:
        return 1.0
    return float(beta.ppf(
        0.95,
        successes + 1,
        trials - successes,
    ))


def _validate_calibration_power(config: dict[str, Any]) -> None:
    """Reject a full run whose null panel cannot meet its own CI gate."""
    repetitions = int(config["calibration_repetitions"])
    target = float(config["gates"]["maximum_false_group_upper_95"])
    best_possible = _one_sided_upper(0, repetitions)
    if best_possible > target and not bool(config.get("_smoke", False)):
        raise ValueError(
            "calibration_repetitions cannot establish the registered "
            f"per-world false-claim bound: zero/{repetitions} gives "
            f"upper={best_possible:.6f} > {target:.6f}"
        )


def _evaluate_row(
    row: dict[str, Any],
    thresholds: dict[str, float],
    *,
    authors: int,
) -> dict[str, Any]:
    result = dict(row)
    refusal_reason = _quality_refusal(row, thresholds)
    result["refusal_reason"] = refusal_reason
    result["refused"] = bool(refusal_reason)
    selected: list[dict[str, Any]] = []
    if not refusal_reason:
        selected = [
            item for item in row["hyperedges"]
            if (
                len(item["members"]) >= 3
                and float(item["persistence"])
                >= thresholds["hyperedge_persistence_threshold"]
            )
        ]
    predicted_labels = _components(authors, selected)
    sizes = np.bincount(predicted_labels)
    structured_sizes = sizes[sizes >= 3]
    structured_coverage = (
        float(np.sum(structured_sizes) / authors)
        if len(structured_sizes)
        else 0.0
    )
    result["structured_coverage"] = structured_coverage
    result["group_claim"] = bool(
        len(structured_sizes) >= 2
        and structured_coverage
        >= thresholds["minimum_group_coverage_for_claim"]
    )
    result["selected_hyperedges"] = selected
    result["predicted_group_count"] = int(np.sum(sizes >= 3))
    result["predicted_max_multiplicity"] = int(
        max(sizes) if len(sizes) else 1
    )
    if row["status"] != "ESTIMATE_READY":
        result.update({
            "co_membership_auc": float("nan"),
            "co_membership_f1": float("nan"),
            "adjusted_rand_index": float("nan"),
            "multiplicity_absolute_error": float("nan"),
        })
        return result
    pair_labels = np.asarray(row["pair_labels"], dtype=int)
    pair_scores = np.asarray(row["pair_scores"], dtype=float)
    upper = np.triu_indices(authors, 1)
    true_labels = _true_partition(pair_labels, authors)
    predicted_pairs = (
        predicted_labels[upper[0]]
        == predicted_labels[upper[1]]
    ).astype(int)
    result["co_membership_auc"] = float(
        roc_auc_score(pair_labels, pair_scores)
    )
    result["co_membership_f1"] = float(f1_score(
        pair_labels,
        predicted_pairs,
        zero_division=0,
    ))
    result["adjusted_rand_index"] = float(adjusted_rand_score(
        true_labels,
        predicted_labels,
    ))
    expected = float(row["expected_multiplicity"])
    significant_sizes = sizes[sizes >= 3]
    estimate = (
        float(np.median(significant_sizes))
        if len(significant_sizes)
        else 1.0
    )
    result["multiplicity_absolute_error"] = abs(estimate - expected)
    return result


def _evaluate(
    rows: list[dict[str, Any]],
    thresholds: dict[str, float],
    *,
    authors: int,
) -> list[dict[str, Any]]:
    return [
        _evaluate_row(
            row,
            thresholds,
            authors=authors,
        )
        for row in rows
    ]


def _population_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    excluded = {
        "pair_scores",
        "raw_pair_scores",
        "tangent_pair_scores",
        "pair_labels",
        "hyperedges",
        "selected_hyperedges",
    }
    return pd.DataFrame([
        {
            key: (
                "null_control"
                if key == "kind" and value == "null"
                else value
            )
            for key, value in row.items()
            if key not in excluded
        }
        for row in rows
    ])


def _pair_frame(rows: list[dict[str, Any]], authors: int) -> pd.DataFrame:
    upper = np.triu_indices(authors, 1)
    parts = []
    for row in rows:
        if row["status"] != "ESTIMATE_READY":
            continue
        predicted_labels = _components(
            authors,
            row.get("selected_hyperedges", []),
        )
        parts.append(pd.DataFrame({
            "stage": row["stage"],
            "seed": row["seed"],
            "world": row["world"],
            "author_left": upper[0],
            "author_right": upper[1],
            "specific_score": row["pair_scores"],
            "raw_score": row["raw_pair_scores"],
            "tangent_score": row["tangent_pair_scores"],
            "true_co_member": row["pair_labels"],
            "predicted_co_member": (
                predicted_labels[upper[0]]
                == predicted_labels[upper[1]]
            ).astype(int),
        }))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def _hyperedge_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    output = []
    for row in rows:
        if row["status"] != "ESTIMATE_READY":
            continue
        threshold = {
            tuple(item["members"])
            for item in row.get("selected_hyperedges", [])
        }
        for item in row["hyperedges"]:
            members = tuple(int(value) for value in item["members"])
            output.append({
                "stage": row["stage"],
                "seed": row["seed"],
                "world": row["world"],
                "members": " ".join(str(value) for value in members),
                "multiplicity": len(members),
                "persistence": item["persistence"],
                "selected": members in threshold,
            })
    return pd.DataFrame(output)


def _multiplicity_profile(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Summarize how many author trajectories each incidence set connects."""
    output = []
    for row in rows:
        if row["status"] != "ESTIMATE_READY":
            continue
        selected = {
            tuple(item["members"])
            for item in row.get("selected_hyperedges", [])
        }
        for item in row["hyperedges"]:
            members = tuple(int(value) for value in item["members"])
            output.append({
                "stage": row["stage"],
                "world": row["world"],
                "seed": row["seed"],
                "multiplicity": len(members),
                "persistence": float(item["persistence"]),
                "selected": members in selected,
            })
    frame = pd.DataFrame(output)
    if frame.empty:
        return frame
    return (
        frame.groupby(
            ["stage", "world", "multiplicity"],
            as_index=False,
        )
        .agg(
            incidence_sets=("seed", "size"),
            populations_with_incidence=("seed", "nunique"),
            persistence_median=("persistence", "median"),
            persistence_q95=(
                "persistence",
                lambda values: float(np.quantile(values, 0.95)),
            ),
            selected_sets=("selected", "sum"),
        )
    )


def _world_summary(rows: list[dict[str, Any]]) -> pd.DataFrame:
    frame = _population_frame(rows)
    return (
        frame.groupby(["stage", "noise_sd", "world", "kind"], as_index=False)
        .agg(
            repetitions=("seed", "size"),
            refusal_rate=("refused", "mean"),
            group_claim_rate=("group_claim", "mean"),
            auc_median=("co_membership_auc", "median"),
            f1_median=("co_membership_f1", "median"),
            ari_median=("adjusted_rand_index", "median"),
            raw_multiplicity_median=("max_raw_multiplicity", "median"),
            predicted_multiplicity_median=(
                "predicted_max_multiplicity",
                "median",
            ),
            multiplicity_error_median=(
                "multiplicity_absolute_error",
                "median",
            ),
            localization_error_median=(
                "condition_localization_error",
                "median",
            ),
            cross_view_spearman_median=(
                "cross_view_spearman",
                "median",
            ),
        )
    )


def _headline(
    confirmation: list[dict[str, Any]],
    challenge: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    clear_summary = _world_summary([
        row for row in confirmation
        if row["kind"] == "clear_group"
    ])
    null = [
        row for row in confirmation
        if row["kind"] == "null"
    ]
    attacks = [
        row for row in confirmation
        if row["kind"] == "attack"
    ]
    boundary = [
        row for row in confirmation
        if row["kind"] == "boundary"
    ]
    challenge_summary = _world_summary([
        row for row in challenge
        if row["kind"] == "challenge_group"
    ])
    false_claims = int(sum(bool(row["group_claim"]) for row in null))
    null_worlds = sorted({row["world"] for row in null})
    null_world_statistics = []
    for world in null_worlds:
        current = [row for row in null if row["world"] == world]
        claims = int(sum(bool(row["group_claim"]) for row in current))
        null_world_statistics.append({
            "world": world,
            "claims": claims,
            "trials": len(current),
            "rate": claims / max(len(current), 1),
            "upper": _one_sided_upper(claims, len(current)),
        })
    worst_null = max(
        null_world_statistics,
        key=lambda item: item["upper"],
    )
    return {
        "minimum_clear_world_auc_median": float(
            clear_summary["auc_median"].min()
        ),
        "minimum_clear_world_f1_median": float(
            clear_summary["f1_median"].min()
        ),
        "minimum_clear_world_ari_median": float(
            clear_summary["ari_median"].min()
        ),
        "minimum_clear_world_group_claim_rate": float(
            clear_summary["group_claim_rate"].min()
        ),
        "multiplicity_median_absolute_error": float(
            clear_summary["multiplicity_error_median"].median()
        ),
        "condition_localization_error": float(
            clear_summary["localization_error_median"].median()
        ),
        "minimum_cross_view_spearman": float(
            clear_summary["cross_view_spearman_median"].min()
        ),
        "pooled_false_group_upper_95": _one_sided_upper(
            false_claims,
            len(null),
        ),
        "false_group_upper_95": float(worst_null["upper"]),
        "maximum_null_world_claim_rate": float(worst_null["rate"]),
        "worst_null_world": str(worst_null["world"]),
        "boundary_group_upper_95": _one_sided_upper(
            int(sum(bool(row["group_claim"]) for row in boundary)),
            len(boundary),
        ),
        "attack_refusal_rate": float(np.mean([
            row["refused"] for row in attacks
        ])),
        "minimum_challenge_auc_median": float(
            challenge_summary["auc_median"].min()
        ),
        "minimum_challenge_nonrefusal_rate": float(
            1.0 - challenge_summary["refusal_rate"].max()
        ),
        "minimum_reparameterization_consistency": float(np.nanmin([
            row["reparameterization_consistency"]
            for row in [*confirmation, *challenge]
            if row["kind"] in {"clear_group", "challenge_group"}
        ])),
        "global_anchor_raw_multiplicity_median": float(np.median([
            row["max_raw_multiplicity"]
            for row in confirmation
            if row["world"] == "global_common_anchor_2d"
        ])),
        "global_anchor_group_claim_rate": float(np.mean([
            row["group_claim"]
            for row in confirmation
            if row["world"] == "global_common_anchor_2d"
        ])),
    }


def _decision(
    headline: dict[str, Any],
    config: dict[str, Any],
    *,
    calibration_valid: bool,
) -> dict[str, Any]:
    gates = config["gates"]
    checks = {
        "population_threshold_calibration": calibration_valid,
        "clear_group_auc": (
            headline["minimum_clear_world_auc_median"]
            >= gates["minimum_group_auc"]
        ),
        "clear_group_f1": (
            headline["minimum_clear_world_f1_median"]
            >= gates["minimum_group_f1"]
        ),
        "clear_group_ari": (
            headline["minimum_clear_world_ari_median"]
            >= gates["minimum_group_ari"]
        ),
        "clear_group_claim_rate": (
            headline["minimum_clear_world_group_claim_rate"]
            >= gates.get("minimum_clear_group_claim_rate", 0.80)
        ),
        "multiplicity_error": (
            headline["multiplicity_median_absolute_error"]
            <= gates["maximum_multiplicity_median_absolute_error"]
        ),
        "condition_localization": (
            headline["condition_localization_error"]
            <= gates["maximum_condition_localization_error"]
        ),
        "cross_view_stability": (
            headline["minimum_cross_view_spearman"]
            >= gates["minimum_cross_view_spearman"]
        ),
        "null_false_group_control": (
            headline["false_group_upper_95"]
            <= gates["maximum_false_group_upper_95"]
        ),
        "isolated_intersection_boundary": (
            headline["boundary_group_upper_95"]
            <= gates.get("maximum_boundary_group_upper_95", 0.03)
        ),
        "attack_refusal": (
            headline["attack_refusal_rate"]
            >= gates["minimum_attack_refusal_rate"]
        ),
        "fresh_challenge_auc": (
            headline["minimum_challenge_auc_median"]
            >= gates["minimum_challenge_auc"]
        ),
        "fresh_challenge_nonrefusal": (
            headline["minimum_challenge_nonrefusal_rate"]
            >= gates["minimum_challenge_nonrefusal_rate"]
        ),
        "condition_reparameterization": (
            headline["minimum_reparameterization_consistency"]
            >= gates["minimum_reparameterization_consistency"]
        ),
    }
    if all(checks.values()):
        status = "V8_INCIDENCE_MULTIPLICITY_PLANTED_PASS"
    elif checks["null_false_group_control"] and checks["attack_refusal"]:
        status = "V8_INCIDENCE_MULTIPLICITY_PARTIAL_BOUNDARY"
    else:
        status = "V8_INCIDENCE_MULTIPLICITY_STOP"
    return {
        "status": status,
        "checks": checks,
        "headline": headline,
        "claim_boundary": config["claim_boundary"],
    }


def _report(
    decision: dict[str, Any],
    thresholds: dict[str, float],
    confirmation_summary: pd.DataFrame,
    challenge_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
) -> str:
    return f"""# V8 Incidence Multiplicity Planted Battery

## Decision

`{decision["status"]}`

## Estimand

```text
T_u(z, epsilon) = uncertainty tube
H is a hyperedge iff intersection_u in H T_u is nonempty
P_uv = persistent same-condition co-incidence weighted against
       population-wide common anchors
```

## Headline

```json
{json.dumps(decision["headline"], indent=2)}
```

## Calibration-only thresholds

```json
{json.dumps(thresholds, indent=2)}
```

## Confirmation worlds

{confirmation_summary.to_markdown(index=False)}

## Fresh nonlinear challenge

{challenge_summary.to_markdown(index=False)}

## Noise sensitivity

{sensitivity_summary.to_markdown(index=False)}

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Claim boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_incidence_multiplicity.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_incidence_multiplicity/v2",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = _read_json(args.config)
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["_smoke"] = True
        config["jobs"] = 1
        config["discovery_repetitions"] = 2
        config["calibration_repetitions"] = 4
        config["confirmation_repetitions"] = 5
        config["challenge_repetitions"] = 5
        config["sensitivity_repetitions"] = 2
        config["noise_scan"] = [0.03, 0.06]
    _validate_calibration_power(config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    worlds = _all_primary_worlds(config)
    discovery = _run_stage(
        config,
        stage="discovery",
        worlds=worlds,
        repetitions=int(config["discovery_repetitions"]),
        noise_sd=float(config["noise_sd"]),
    )
    calibration = _run_stage(
        config,
        stage="calibration",
        worlds=worlds,
        repetitions=int(config["calibration_repetitions"]),
        noise_sd=float(config["noise_sd"]),
    )
    thresholds, threshold_diagnostics = _calibrate(calibration, config)
    confirmation = _evaluate(
        _run_stage(
            config,
            stage="confirmation",
            worlds=worlds,
            repetitions=int(config["confirmation_repetitions"]),
            noise_sd=float(config["noise_sd"]),
        ),
        thresholds,
        authors=int(config["authors"]),
    )
    challenge = _evaluate(
        _run_stage(
            config,
            stage="challenge",
            worlds=config["challenge_worlds"],
            repetitions=int(config["challenge_repetitions"]),
            noise_sd=float(config["noise_sd"]),
        ),
        thresholds,
        authors=int(config["authors"]),
    )
    sensitivity = []
    for noise in config["noise_scan"]:
        sensitivity.extend(_evaluate(
            _run_stage(
                config,
                stage="sensitivity",
                worlds=config["sensitivity_worlds"],
                repetitions=int(config["sensitivity_repetitions"]),
                noise_sd=float(noise),
            ),
            thresholds,
            authors=int(config["authors"]),
        ))
    headline = _headline(confirmation, challenge, config)
    selected_calibration = threshold_diagnostics[
        threshold_diagnostics["selected"]
    ].iloc[0]
    calibration_valid = bool(
        selected_calibration["null_control_pass"]
        and selected_calibration["clear_recovery_pass"]
    )
    decision = _decision(
        headline,
        config,
        calibration_valid=calibration_valid,
    )
    confirmation_summary = _world_summary(confirmation)
    challenge_summary = _world_summary(challenge)
    sensitivity_summary = _world_summary(sensitivity)

    for name, rows in {
        "discovery": discovery,
        "calibration": calibration,
        "confirmation": confirmation,
        "challenge": challenge,
        "sensitivity": sensitivity,
    }.items():
        _population_frame(rows).to_csv(
            args.output_dir / f"{name}_population_metrics.csv",
            index=False,
        )
    _pair_frame(
        [*confirmation, *challenge],
        int(config["authors"]),
    ).to_csv(
        args.output_dir / "confirmation_pair_metrics.csv.gz",
        index=False,
        compression="gzip",
    )
    _hyperedge_frame(
        [*confirmation, *challenge],
    ).to_csv(
        args.output_dir / "confirmation_hyperedges.csv.gz",
        index=False,
        compression="gzip",
    )
    confirmation_summary.to_csv(
        args.output_dir / "confirmation_world_summary.csv",
        index=False,
    )
    challenge_summary.to_csv(
        args.output_dir / "challenge_world_summary.csv",
        index=False,
    )
    sensitivity_summary.to_csv(
        args.output_dir / "sensitivity_world_summary.csv",
        index=False,
    )
    _multiplicity_profile(
        [*confirmation, *challenge],
    ).to_csv(
        args.output_dir / "incidence_multiplicity_profile.csv",
        index=False,
    )
    threshold_diagnostics.to_csv(
        args.output_dir / "threshold_calibration_diagnostics.csv",
        index=False,
    )
    _write_json(args.output_dir / "thresholds.json", thresholds)
    _write_json(args.output_dir / "decision.json", decision)
    _write_json(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _report(
            decision,
            thresholds,
            confirmation_summary,
            challenge_summary,
            sensitivity_summary,
        ),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_incidence_multiplicity.py",
            Path(__file__),
        ],
        estimand_id=str(config.get(
            "estimand_id",
            "V8_INCIDENCE_MULTIPLICITY_PLANTED_V2",
        )),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps({
        "status": decision["status"],
        "output_dir": str(args.output_dir),
        "headline": headline,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
