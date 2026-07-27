#!/usr/bin/env python3
"""Run the registered SUICA V8 C2 topology-margin planted-world battery."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_topology_margin import (  # noqa: E402
    TopologySpec,
    aggregate_topology_features,
    analyze_topology_world,
    apply_stable_projection,
    calibrate_thresholds,
    classify_topology,
    fit_stable_projection,
    matching_diagnostics,
    simulate_topology_world,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_topology_margin_v11.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_topology_margin"
    / "v11_20260729"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _spec(
    config: dict[str, Any],
    *,
    confirmation_authors: int,
    noise_ratio: float,
    gap_ratio: float,
    bridge_mass: float,
) -> TopologySpec:
    return TopologySpec(
        confirmation_authors=int(confirmation_authors),
        latent_dimensions=int(config["latent_dimensions"]),
        operator_dimensions=int(config["operator_dimensions"]),
        observers=int(config["observers"]),
        halves=int(config["halves"]),
        groups=int(config["groups"]),
        landmarks=int(config["landmarks"]),
        noise_ratio=float(noise_ratio),
        gap_ratio=float(gap_ratio),
        bridge_mass=float(bridge_mass),
    )


def _matching_gates(config: dict[str, Any]) -> dict[str, float]:
    return {
        key: float(config["gates"][key])
        for key in (
            "maximum_matching_mean_abs",
            "maximum_matching_covariance_error",
            "maximum_matching_auc_gap",
        )
    }


def _matching_kwargs(config: dict[str, Any]) -> dict[str, float]:
    gates = _matching_gates(config)
    return {
        "maximum_mean_abs": gates["maximum_matching_mean_abs"],
        "maximum_covariance_error": gates[
            "maximum_matching_covariance_error"
        ],
        "maximum_auc_gap": gates["maximum_matching_auc_gap"],
    }


def _one_feature_row(
    *,
    seed: int,
    world_name: str,
    spec: TopologySpec,
    neighbors: int,
    config: dict[str, Any],
    thresholds: dict[str, float] | None,
) -> dict[str, Any]:
    world = simulate_topology_world(
        seed=seed,
        world=world_name,
        spec=spec,
    )
    return analyze_topology_world(
        world,
        neighbors=neighbors,
        thresholds=thresholds,
        groups=int(config["groups"]),
        landmarks=int(config["landmarks"]),
        matching_gates=_matching_gates(config),
    )


def _calibration_payload(
    payload: tuple[int, int, int, str, int, dict[str, Any], str],
) -> dict[str, Any]:
    (
        repetition,
        confirmation_authors,
        neighbors,
        world_name,
        seed,
        config,
        split,
    ) = payload
    spec = _spec(
        config,
        confirmation_authors=confirmation_authors,
        noise_ratio=float(config["primary_noise_ratio"]),
        gap_ratio=float(config["primary_gap_ratio"]),
        bridge_mass=0.0,
    )
    row = _one_feature_row(
        seed=seed,
        world_name=world_name,
        spec=spec,
        neighbors=neighbors,
        config=config,
        thresholds=None,
    )
    return {
        "stage": "threshold_calibration",
        "calibration_split": split,
        "repetition": repetition,
        "seed": seed,
        "neighbors": neighbors,
        "confirmation_authors": spec.confirmation_authors,
        "noise_ratio": spec.noise_ratio,
        "gap_ratio": spec.gap_ratio,
        "bridge_mass": spec.bridge_mass,
        **row,
    }


def _parallel_map(
    function: Any,
    payloads: list[Any],
    *,
    jobs: int,
) -> list[Any]:
    if jobs <= 1:
        return [function(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(function, payloads, chunksize=1))


def _calibrate(
    config: dict[str, Any],
    *,
    repetitions: int,
    jobs: int,
) -> tuple[
    int,
    dict[str, dict[str, float]],
    pd.DataFrame,
    pd.DataFrame,
]:
    worlds = (
        "separated_mixture",
        "continuous_ring",
        "continuous_curve",
        "high_overlap_mixture",
        "null_gaussian",
        "heavy_tailed_elliptical",
    )
    threshold_repetitions = max(8, int(round(repetitions * 2.0 / 3.0)))
    payloads = []
    for neighbors in map(int, config["knn_candidates"]):
        for repetition in range(repetitions):
            split = (
                "threshold"
                if repetition < threshold_repetitions
                else "selection"
            )
            for world_index, world_name in enumerate(worlds):
                seed = (
                    int(config["seed"])
                    + 10_000_019 * neighbors
                    + 1_000_003 * repetition
                    + 10_007 * world_index
                )
                payloads.append((
                    repetition,
                    160,
                    neighbors,
                    world_name,
                    seed,
                    config,
                    split,
                ))
    rows = _parallel_map(_calibration_payload, payloads, jobs=jobs)
    frame = pd.DataFrame(rows)
    selected_records = []
    thresholds_by_k: dict[int, dict[str, float]] = {}
    for neighbors in map(int, config["knn_candidates"]):
        threshold_rows = frame.loc[
            frame["neighbors"].eq(neighbors)
            & frame["calibration_split"].eq("threshold")
        ].to_dict("records")
        thresholds = calibrate_thresholds(threshold_rows)
        thresholds_by_k[neighbors] = thresholds
        selection = frame.loc[
            frame["neighbors"].eq(neighbors)
            & frame["calibration_split"].eq("selection")
        ].copy()
        predicted = []
        for row in selection.to_dict("records"):
            decision = classify_topology(
                row,
                thresholds,
                matching_pass=bool(row["matching_pass"]),
                bridge_count=int(row["bridge_count"]),
            )
            predicted.append(decision["predicted_class"])
        selection["predicted_class"] = predicted
        selection["correct"] = (
            selection["predicted_class"] == selection["expected_class"]
        )
        selection["wrong_decisive"] = (
            selection["predicted_class"]
            != "TOPOLOGY_NOT_IDENTIFIABLE"
        ) & (~selection["correct"])
        clear = selection["expected_class"].ne(
            "TOPOLOGY_NOT_IDENTIFIABLE"
        )
        ambiguous = ~clear
        clear_accuracy = float(selection.loc[clear, "correct"].mean())
        refusal_rate = float(selection.loc[ambiguous, "correct"].mean())
        wrong_rate = float(selection["wrong_decisive"].mean())
        objective = clear_accuracy + refusal_rate - 2.0 * wrong_rate
        selected_records.append({
            "row_type": "k_selection_n160",
            "confirmation_authors": 160,
            "neighbors": neighbors,
            "clear_accuracy": clear_accuracy,
            "ambiguous_refusal_rate": refusal_rate,
            "wrong_decisive_rate": wrong_rate,
            "objective": objective,
        })
    selection_summary = pd.DataFrame(selected_records).sort_values(
        ["objective", "wrong_decisive_rate", "neighbors"],
        ascending=[False, True, True],
    )
    selected_k = int(selection_summary.iloc[0]["neighbors"])
    extra_payloads = []
    for confirmation_authors in map(
        int,
        config.get(
            "calibration_confirmation_sizes",
            [80, 160, 320, 640],
        ),
    ):
        if confirmation_authors == 160:
            continue
        case_neighbors = max(
            4,
            int(round(selected_k * confirmation_authors / 160.0)),
        )
        for repetition in range(repetitions):
            split = (
                "threshold"
                if repetition < threshold_repetitions
                else "selection"
            )
            for world_index, world_name in enumerate(worlds):
                seed = (
                    int(config["seed"])
                    + 500_000_003
                    + confirmation_authors * 100_003
                    + case_neighbors * 10_000_019
                    + repetition * 1_000_003
                    + world_index * 10_007
                )
                extra_payloads.append((
                    repetition,
                    confirmation_authors,
                    case_neighbors,
                    world_name,
                    seed,
                    config,
                    split,
                ))
    if extra_payloads:
        extra_rows = _parallel_map(
            _calibration_payload,
            extra_payloads,
            jobs=jobs,
        )
        frame = pd.concat(
            [frame, pd.DataFrame(extra_rows)],
            ignore_index=True,
        )

    thresholds_by_n: dict[str, dict[str, float]] = {}
    size_records = []
    for confirmation_authors in map(
        int,
        config.get(
            "calibration_confirmation_sizes",
            [80, 160, 320, 640],
        ),
    ):
        size_frame = frame[
            frame["confirmation_authors"].eq(confirmation_authors)
        ]
        size_neighbors = max(
            4,
            int(round(selected_k * confirmation_authors / 160.0)),
        )
        size_frame = size_frame[size_frame["neighbors"].eq(size_neighbors)]
        threshold_rows = size_frame[
            size_frame["calibration_split"].eq("threshold")
        ].to_dict("records")
        size_thresholds = calibrate_thresholds(threshold_rows)
        thresholds_by_n[str(confirmation_authors)] = size_thresholds
        selection = size_frame[
            size_frame["calibration_split"].eq("selection")
        ].copy()
        decisions = [
            classify_topology(
                row,
                size_thresholds,
                matching_pass=bool(row["matching_pass"]),
                bridge_count=int(row["bridge_count"]),
            )["predicted_class"]
            for row in selection.to_dict("records")
        ]
        selection["predicted_class"] = decisions
        selection["correct"] = (
            selection["predicted_class"] == selection["expected_class"]
        )
        selection["wrong_decisive"] = (
            selection["predicted_class"]
            != "TOPOLOGY_NOT_IDENTIFIABLE"
        ) & (~selection["correct"])
        clear = selection["expected_class"].ne(
            "TOPOLOGY_NOT_IDENTIFIABLE"
        )
        size_records.append({
            "row_type": "size_specific_validation",
            "confirmation_authors": confirmation_authors,
            "neighbors": size_neighbors,
            "clear_accuracy": float(
                selection.loc[clear, "correct"].mean()
            ),
            "ambiguous_refusal_rate": float(
                selection.loc[~clear, "correct"].mean()
            ),
            "wrong_decisive_rate": float(
                selection["wrong_decisive"].mean()
            ),
            "objective": float(selection["correct"].mean()),
        })
    selection_summary = pd.concat(
        [selection_summary, pd.DataFrame(size_records)],
        ignore_index=True,
    )
    return (
        selected_k,
        thresholds_by_n,
        frame,
        selection_summary,
    )


def _case_payload(
    payload: tuple[
        dict[str, Any],
        int,
        dict[str, Any],
        int,
        dict[str, dict[str, float]],
    ],
) -> dict[str, Any]:
    case, repetition, config, neighbors, thresholds_by_n = payload
    spec = _spec(
        config,
        confirmation_authors=int(case["confirmation_authors"]),
        noise_ratio=float(case["noise_ratio"]),
        gap_ratio=float(case["gap_ratio"]),
        bridge_mass=float(case["bridge_mass"]),
    )
    case_neighbors = max(
        4,
        int(round(neighbors * spec.confirmation_authors / 160.0)),
    )
    thresholds = thresholds_by_n[str(spec.confirmation_authors)]
    seed = (
        int(config["seed"])
        + int(case["case_index"]) * 100_000_007
        + repetition * 1_000_003
    )
    row = _one_feature_row(
        seed=seed,
        world_name=str(case["world"]),
        spec=spec,
        neighbors=case_neighbors,
        config=config,
        thresholds=thresholds,
    )
    return {
        **case,
        "repetition": repetition,
        "seed": seed,
        "base_neighbors_n160": neighbors,
        "neighbors": case_neighbors,
        **row,
        "correct": row["predicted_class"] == row["expected_class"],
        "wrong_decisive": bool(
            row["predicted_class"] != "TOPOLOGY_NOT_IDENTIFIABLE"
            and row["predicted_class"] != row["expected_class"]
        ),
    }


def _primary_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for n in map(int, config["primary_confirmation_sizes"]):
        for world_name in config["primary_worlds"]:
            cases.append({
                "stage": "primary",
                "case_id": f"primary_n{n}_{world_name}",
                "world": str(world_name),
                "confirmation_authors": n,
                "noise_ratio": float(config["primary_noise_ratio"]),
                "gap_ratio": float(config["primary_gap_ratio"]),
                "bridge_mass": 0.0,
            })
    return cases


def _sensitivity_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for n in map(int, config["power_confirmation_sizes"]):
        for world_name in (
            "separated_mixture",
            "continuous_ring",
            "continuous_curve",
            "null_gaussian",
        ):
            cases.append({
                "stage": "power",
                "case_id": f"power_n{n}_{world_name}",
                "world": world_name,
                "confirmation_authors": n,
                "noise_ratio": float(config["primary_noise_ratio"]),
                "gap_ratio": float(config["primary_gap_ratio"]),
                "bridge_mass": 0.0,
            })
    for gap in map(float, config["gap_ratios"]):
        cases.append({
            "stage": "gap_scan",
            "case_id": f"gap_{gap:0.3f}",
            "world": "separated_mixture",
            "confirmation_authors": 320,
            "noise_ratio": float(config["primary_noise_ratio"]),
            "gap_ratio": gap,
            "bridge_mass": 0.0,
        })
    for noise in map(float, config["noise_ratios"]):
        for world_name in (
            "separated_mixture",
            "continuous_ring",
            "continuous_curve",
        ):
            cases.append({
                "stage": "noise_scan",
                "case_id": f"noise_{noise:0.3f}_{world_name}",
                "world": world_name,
                "confirmation_authors": 320,
                "noise_ratio": noise,
                "gap_ratio": float(config["primary_gap_ratio"]),
                "bridge_mass": 0.0,
            })
    for bridge in map(float, config["bridge_masses"]):
        cases.append({
            "stage": "bridge_scan",
            "case_id": f"bridge_{bridge:0.3f}",
            "world": "pearls_on_string",
            "confirmation_authors": 320,
            "noise_ratio": float(config["primary_noise_ratio"]),
            "gap_ratio": float(config["primary_gap_ratio"]),
            "bridge_mass": bridge,
        })
    return cases


def _run_cases(
    cases: list[dict[str, Any]],
    *,
    repetitions: int,
    config: dict[str, Any],
    neighbors: int,
    thresholds: dict[str, dict[str, float]],
    jobs: int,
) -> pd.DataFrame:
    indexed = []
    for case_index, case in enumerate(cases):
        indexed.append({**case, "case_index": case_index})
    payloads = [
        (case, repetition, config, neighbors, thresholds)
        for case in indexed
        for repetition in range(repetitions)
    ]
    return pd.DataFrame(
        _parallel_map(_case_payload, payloads, jobs=jobs)
    )


def _affine_permutation_payload(
    payload: tuple[
        int,
        int,
        str,
        dict[str, Any],
        int,
        dict[str, dict[str, float]],
    ],
) -> dict[str, Any]:
    (
        repetition,
        confirmation_authors,
        world_name,
        config,
        neighbors,
        thresholds_by_n,
    ) = payload
    spec = _spec(
        config,
        confirmation_authors=confirmation_authors,
        noise_ratio=float(config["primary_noise_ratio"]),
        gap_ratio=float(config["primary_gap_ratio"]),
        bridge_mass=0.0,
    )
    case_neighbors = max(
        4,
        int(round(neighbors * spec.confirmation_authors / 160.0)),
    )
    thresholds = thresholds_by_n[str(spec.confirmation_authors)]
    seed = (
        int(config["seed"])
        + 800_000_011
        + repetition * 1_000_003
        + confirmation_authors * 10_009
        + (
            0 if world_name == "separated_mixture"
            else 1 if world_name == "continuous_ring"
            else 2
        ) * 100_003
    )
    world = simulate_topology_world(seed=seed, world=world_name, spec=spec)
    splits = np.asarray(world["splits"])
    discovery = splits == "discovery"
    confirmation = splits == "confirmation"
    fitted = fit_stable_projection(world["views"], discovery)
    projected = apply_stable_projection(world["views"], fitted)
    baseline_features = aggregate_topology_features(
        projected[confirmation],
        neighbors=case_neighbors,
        groups=int(config["groups"]),
        landmarks=int(config["landmarks"]),
    )
    baseline_matching = matching_diagnostics(
        projected,
        discovery,
        confirmation,
        **_matching_kwargs(config),
    )
    baseline = classify_topology(
        baseline_features,
        thresholds,
        matching_pass=bool(baseline_matching["matching_pass"]),
        bridge_count=-1,
    )

    rng = np.random.default_rng(seed + 71)
    affine = rng.normal(size=(3, 3))
    u, singular, vt = np.linalg.svd(affine)
    affine = u @ np.diag(np.clip(singular, 0.5, 2.0)) @ vt
    transformed = projected @ affine + rng.normal(size=3)
    author_mean = transformed[discovery].mean(axis=(1, 2))
    center = author_mean.mean(axis=0)
    covariance = np.cov(author_mean, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    whitening = eigenvectors @ np.diag(
        1.0 / np.sqrt(np.maximum(eigenvalues, 1e-8))
    ) @ eigenvectors.T
    transformed = (transformed - center) @ whitening
    permutation = np.arange(len(transformed))
    for split in ("discovery", "calibration", "confirmation"):
        indices = np.flatnonzero(splits == split)
        permutation[indices] = rng.permutation(indices)
    transformed = transformed[permutation]
    transformed_splits = splits[permutation]
    transformed_discovery = transformed_splits == "discovery"
    transformed_confirmation = transformed_splits == "confirmation"
    transformed_features = aggregate_topology_features(
        transformed[transformed_confirmation],
        neighbors=case_neighbors,
        groups=int(config["groups"]),
        landmarks=int(config["landmarks"]),
    )
    transformed_matching = matching_diagnostics(
        transformed,
        transformed_discovery,
        transformed_confirmation,
        **_matching_kwargs(config),
    )
    transformed_decision = classify_topology(
        transformed_features,
        thresholds,
        matching_pass=bool(transformed_matching["matching_pass"]),
        bridge_count=-1,
    )
    return {
        "repetition": repetition,
        "seed": seed,
        "confirmation_authors": confirmation_authors,
        "world": world_name,
        "baseline_class": baseline["predicted_class"],
        "transformed_class": transformed_decision["predicted_class"],
        "invariant": (
            baseline["predicted_class"]
            == transformed_decision["predicted_class"]
        ),
        "baseline_expected": (
            baseline["predicted_class"] == world["expected_class"]
        ),
    }


def _run_invariance(
    config: dict[str, Any],
    *,
    repetitions: int,
    neighbors: int,
    thresholds: dict[str, dict[str, float]],
    jobs: int,
) -> pd.DataFrame:
    payloads = [
        (
            repetition,
            confirmation_authors,
            world_name,
            config,
            neighbors,
            thresholds,
        )
        for confirmation_authors in (320, 640)
        for world_name in (
            "separated_mixture",
            "continuous_ring",
            "continuous_curve",
        )
        for repetition in range(repetitions)
    ]
    return pd.DataFrame(
        _parallel_map(
            _affine_permutation_payload,
            payloads,
            jobs=jobs,
        )
    )


def _binomial_upper(successes: int, trials: int) -> float:
    if trials <= 0:
        return float("nan")
    if successes >= trials:
        return 1.0
    return float(beta.ppf(0.95, successes + 1, trials - successes))


def _summary(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = [
        "stage",
        "case_id",
        "world",
        "confirmation_authors",
        "noise_ratio",
        "gap_ratio",
        "bridge_mass",
        "expected_class",
    ]
    metrics = [
        "matching_pass",
        "correct",
        "wrong_decisive",
        "stable",
        "h0_k_gap",
        "h1_max_lifetime",
        "local_linearity",
        "laplacian_k4_eigengap",
        "minimum_conductance",
        "density_tree_k4_longest",
        "k4_silhouette",
        "hdbscan_k4_supported",
        "cycle_eigenpair_similarity",
        "h0_bottleneck",
        "h1_bottleneck",
        "neighborhood_jaccard",
        "author_matching_auc",
        "matching_covariance_error",
    ]
    for values, group in frame.groupby(keys, sort=False, observed=True):
        row = dict(zip(keys, values, strict=True))
        row["repetitions"] = int(len(group))
        for metric in metrics:
            row[f"mean_{metric}"] = float(group[metric].mean())
        for label in (
            "DISCRETE_K",
            "CONTINUOUS_RING",
            "CONTINUOUS_CURVE",
            "TOPOLOGY_NOT_IDENTIFIABLE",
        ):
            row[f"rate_{label.lower()}"] = float(
                group["predicted_class"].eq(label).mean()
            )
        wrong = int(group["wrong_decisive"].sum())
        row["wrong_decisive_upper_95"] = _binomial_upper(
            wrong,
            len(group),
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _decision(
    primary_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
    invariance: pd.DataFrame,
    config: dict[str, Any],
    thresholds: dict[str, dict[str, float]],
) -> dict[str, Any]:
    gates = config["gates"]
    clear = primary_summary[
        primary_summary["expected_class"].isin({
            "DISCRETE_K",
            "CONTINUOUS_RING",
            "CONTINUOUS_CURVE",
        })
    ]
    n320 = clear[clear["confirmation_authors"].eq(320)]
    n640 = clear[clear["confirmation_authors"].eq(640)]
    ambiguous = primary_summary[
        primary_summary["expected_class"].eq(
            "TOPOLOGY_NOT_IDENTIFIABLE"
        )
    ]
    null = primary_summary[
        primary_summary["world"].eq("null_gaussian")
    ]
    bridge_low = sensitivity_summary[
        sensitivity_summary["stage"].eq("bridge_scan")
        & (
            sensitivity_summary["bridge_mass"]
            * sensitivity_summary["confirmation_authors"]
            < float(gates["minimum_bridge_count_for_test"])
        )
    ]
    wrong_upper = float(primary_summary["wrong_decisive_upper_95"].max())
    null_claim_upper = float(
        max(
            _binomial_upper(
                int(
                    round(
                        row.repetitions
                        * (
                            1.0
                            - row.rate_topology_not_identifiable
                        )
                    )
                ),
                int(row.repetitions),
            )
            for row in null.itertuples(index=False)
        )
    )
    invariance_by_n: dict[int, dict[str, float]] = {}
    for n in (320, 640):
        selected = invariance[invariance["confirmation_authors"].eq(n)]
        eligible = selected[selected["baseline_expected"].astype(bool)]
        invariance_by_n[n] = {
            "eligible_rate": float(
                len(eligible) / max(len(selected), 1)
            ),
            "conditional_invariance_rate": (
                float(eligible["invariant"].mean())
                if len(eligible)
                else 0.0
            ),
        }
    invariance_rate = min(
        row["conditional_invariance_rate"]
        for row in invariance_by_n.values()
    )
    checks = {
        "n320_clear_correct": bool(
            len(n320)
            and n320["mean_correct"].min()
            >= float(gates["minimum_n320_correct_rate"])
        ),
        "n640_clear_correct": bool(
            len(n640)
            and n640["mean_correct"].min()
            >= float(gates["minimum_n640_correct_rate"])
        ),
        "ambiguous_refusal": bool(
            len(ambiguous)
            and ambiguous[
                "rate_topology_not_identifiable"
            ].min()
            >= float(gates["minimum_refusal_rate"])
        ),
        "low_bridge_refusal": bool(
            not len(bridge_low)
            or bridge_low[
                "rate_topology_not_identifiable"
            ].min()
            >= float(gates["minimum_refusal_rate"])
        ),
        "wrong_decisive_control": bool(
            wrong_upper
            <= float(gates["maximum_wrong_decisive_upper_95"])
        ),
        "null_fpr_control": bool(
            null_claim_upper
            <= float(gates["maximum_null_claim_fpr_upper_95"])
        ),
        "affine_permutation_invariance": bool(
            invariance_rate
            >= float(gates["minimum_invariance_rate"])
        ),
        "invariance_baseline_eligible_n320": bool(
            invariance_by_n[320]["eligible_rate"]
            >= float(gates["minimum_invariance_eligible_n320"])
        ),
        "invariance_baseline_eligible_n640": bool(
            invariance_by_n[640]["eligible_rate"]
            >= float(gates["minimum_invariance_eligible_n640"])
        ),
        "h1_open_set_separable": bool(
            all(
                float(values["h1_open_set_gap"]) > 0.0
                for values in thresholds.values()
            )
        ),
    }
    if all(checks.values()):
        status = "V8_C2_TOPOLOGY_MARGIN_PLANTED_PASS"
    elif checks["null_fpr_control"] and checks["wrong_decisive_control"]:
        status = "V8_C2_TOPOLOGY_MARGIN_PARTIAL_BOUNDARY"
    else:
        status = "V8_C2_TOPOLOGY_MARGIN_STOP"
    return {
        "status": status,
        "checks": checks,
        "headline": {
            "minimum_n320_clear_correct_rate": (
                float(n320["mean_correct"].min())
                if len(n320)
                else None
            ),
            "minimum_n640_clear_correct_rate": (
                float(n640["mean_correct"].min())
                if len(n640)
                else None
            ),
            "minimum_ambiguous_refusal_rate": (
                float(
                    ambiguous[
                        "rate_topology_not_identifiable"
                    ].min()
                )
                if len(ambiguous)
                else None
            ),
            "maximum_wrong_decisive_upper_95": wrong_upper,
            "maximum_null_claim_upper_95": null_claim_upper,
            "invariance_rate": invariance_rate,
            "invariance_n320": invariance_by_n[320],
            "invariance_n640": invariance_by_n[640],
            "h1_open_set_by_n": {
                key: {
                    "curve_h1_ceiling": float(
                        values["curve_h1_ceiling"]
                    ),
                    "ring_h1_floor": float(values["ring_h1_floor"]),
                    "h1_open_set_gap": float(
                        values["h1_open_set_gap"]
                    ),
                }
                for key, values in thresholds.items()
            },
        },
        "claim_boundary": str(config["claim_boundary"]),
    }


def _report(
    decision: dict[str, Any],
    selected_k: int,
    thresholds: dict[str, dict[str, float]],
    calibration_selection: pd.DataFrame,
    primary_summary: pd.DataFrame,
    sensitivity_summary: pd.DataFrame,
) -> str:
    headline_columns = [
        "case_id",
        "confirmation_authors",
        "expected_class",
        "mean_correct",
        "rate_discrete_k",
        "rate_continuous_ring",
        "rate_continuous_curve",
        "rate_topology_not_identifiable",
        "mean_author_matching_auc",
        "mean_neighborhood_jaccard",
    ]
    sensitivity_columns = [
        "stage",
        "case_id",
        "expected_class",
        "mean_correct",
        "rate_topology_not_identifiable",
        "mean_author_matching_auc",
    ]
    return f"""# V8 C2 Topology-Margin Planted-World Battery

## Decision

`{decision["status"]}`

## Registered Estimand

The object is the topology of a stable technical C2 response-operator
population after discovery-only projection. Distances are transformed by

```text
d_star(i,j) = empirical_CDF(d(i,j))
```

before PH/graph analysis. This exactly matches the one-dimensional distance
CDF while preserving the Vietoris--Rips filtration order.

## Headline

```json
{json.dumps(decision["headline"], indent=2)}
```

## Frozen Calibration

Selected k: `{selected_k}`

```json
{json.dumps(thresholds, indent=2)}
```

{calibration_selection.to_markdown(index=False)}

## Primary Confirmation

{primary_summary[headline_columns].to_markdown(index=False)}

## Sensitivity and Boundary Scans

{sensitivity_summary[sensitivity_columns].to_markdown(index=False)}

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Interpretation Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--primary-repetitions", type=int)
    parser.add_argument("--sensitivity-repetitions", type=int)
    parser.add_argument("--calibration-repetitions", type=int)
    parser.add_argument("--jobs", type=int)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument(
        "--invariance-only",
        action="store_true",
        help="Recompute the affine/permutation audit from saved frozen outputs.",
    )
    args = parser.parse_args()
    config = _read_json(args.config)
    jobs = int(args.jobs or config.get("jobs", 1))
    if args.invariance_only:
        selected = _read_json(
            args.output_dir / "selected_thresholds.json"
        )
        selected_k = int(selected["selected_k"])
        thresholds = {
            str(n): {
                str(key): float(value)
                for key, value in values.items()
            }
            for n, values in selected["thresholds_by_n"].items()
        }
        primary_summary = pd.read_csv(
            args.output_dir / "primary_world_summary.csv"
        )
        sensitivity_summary = pd.read_csv(
            args.output_dir / "sensitivity_summary.csv"
        )
        calibration_selection = pd.read_csv(
            args.output_dir / "calibration_selection.csv"
        )
        invariance = _run_invariance(
            config,
            repetitions=int(config["sensitivity_repetitions"]),
            neighbors=selected_k,
            thresholds=thresholds,
            jobs=jobs,
        )
        decision = _decision(
            primary_summary,
            sensitivity_summary,
            invariance,
            config,
            thresholds,
        )
        invariance.to_csv(
            args.output_dir / "invariance_metrics.csv",
            index=False,
        )
        _write_json(args.output_dir / "decision.json", decision)
        (args.output_dir / "report.md").write_text(
            _report(
                decision,
                selected_k,
                thresholds,
                calibration_selection,
                primary_summary,
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
                ROOT / "suica_core" / "v8_topology_margin.py",
                Path(__file__),
            ],
            estimand_id="V8_C2_TOPOLOGY_MARGIN_PLANTED_V1_INVARIANCE_REPAIR",
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
            "invariance_recomputed": True,
            "headline": decision["headline"],
        }, ensure_ascii=False, indent=2))
        return 0
    if args.smoke:
        primary_repetitions = 2
        sensitivity_repetitions = 2
        calibration_repetitions = 12
        config = {
            **config,
            "primary_confirmation_sizes": [80],
            "power_confirmation_sizes": [80],
            "primary_worlds": [
                "separated_mixture",
                "continuous_ring",
                "continuous_curve",
                "null_gaussian",
                "half_shuffled",
            ],
            "bridge_masses": [0.0, 0.1],
            "gap_ratios": [2.0, 4.0],
            "noise_ratios": [0.5],
        }
    else:
        primary_repetitions = int(
            args.primary_repetitions
            or config["primary_repetitions"]
        )
        sensitivity_repetitions = int(
            args.sensitivity_repetitions
            or config["sensitivity_repetitions"]
        )
        calibration_repetitions = int(
            args.calibration_repetitions
            or config["calibration_repetitions"]
        )

    (
        selected_k,
        thresholds,
        calibration_rows,
        calibration_selection,
    ) = _calibrate(
        config,
        repetitions=calibration_repetitions,
        jobs=jobs,
    )
    if any(
        float(values["h1_open_set_gap"]) <= 0.0
        for values in thresholds.values()
    ):
        raise RuntimeError(
            "H1_OPEN_SET_NOT_SEPARABLE_STOP: calibration did not "
            "separate the curve ceiling from the ring floor"
        )
    primary = _run_cases(
        _primary_cases(config),
        repetitions=primary_repetitions,
        config=config,
        neighbors=selected_k,
        thresholds=thresholds,
        jobs=jobs,
    )
    sensitivity = _run_cases(
        _sensitivity_cases(config),
        repetitions=sensitivity_repetitions,
        config=config,
        neighbors=selected_k,
        thresholds=thresholds,
        jobs=jobs,
    )
    invariance = _run_invariance(
        config,
        repetitions=(
            2 if args.smoke else sensitivity_repetitions
        ),
        neighbors=selected_k,
        thresholds=thresholds,
        jobs=jobs,
    )
    primary_summary = _summary(primary)
    sensitivity_summary = _summary(sensitivity)
    decision = _decision(
        primary_summary,
        sensitivity_summary,
        invariance,
        config,
        thresholds,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    calibration_rows.to_csv(
        args.output_dir / "calibration_features.csv",
        index=False,
    )
    calibration_selection.to_csv(
        args.output_dir / "calibration_selection.csv",
        index=False,
    )
    primary.to_csv(args.output_dir / "primary_seed_metrics.csv", index=False)
    sensitivity.to_csv(
        args.output_dir / "sensitivity_seed_metrics.csv",
        index=False,
    )
    invariance.to_csv(
        args.output_dir / "invariance_metrics.csv",
        index=False,
    )
    primary_summary.to_csv(
        args.output_dir / "primary_world_summary.csv",
        index=False,
    )
    sensitivity_summary.to_csv(
        args.output_dir / "sensitivity_summary.csv",
        index=False,
    )
    _write_json(args.output_dir / "selected_thresholds.json", {
        "selected_k": selected_k,
        "thresholds_by_n": thresholds,
    })
    _write_json(args.output_dir / "decision.json", decision)
    _write_json(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _report(
            decision,
            selected_k,
            thresholds,
            calibration_selection,
            primary_summary,
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
            ROOT / "suica_core" / "v8_topology_margin.py",
            Path(__file__),
        ],
        estimand_id=(
            "V8_C2_TOPOLOGY_MARGIN_PLANTED_"
            + str(config["version"]).upper().replace("-", "_").replace(".", "_")
        ),
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
        "selected_k": selected_k,
        "headline": decision["headline"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
