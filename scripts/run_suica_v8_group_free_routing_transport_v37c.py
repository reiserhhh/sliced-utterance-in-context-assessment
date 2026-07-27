#!/usr/bin/env python3
"""Run the V3.7C group-free routing transport correction experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    sha256_file,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_author_routing_operator import (  # noqa: E402
    AuthorRoutingSpec,
    fit_reference_router,
    multivariate_reliability,
    simulate_author_routing_world,
)
from suica_core.v8_group_free_routing_transport import (  # noqa: E402
    TransportPathSpec,
    apply_group_free_denoiser,
    apply_registered_missingness,
    estimate_fixed_reference_profile,
    evaluate_group_free_operator,
    fit_group_free_denoiser,
    localize_routing_counts,
    mnar_sensitivity_envelope,
    rank_lambda_cv_losses_group_free,
    resample_routing_counts,
    seed_sequence_int,
    transport_localization_metrics,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=True)
        + "\n",
        encoding="utf-8",
    )


def _root_child_keys(seed: int, count: int) -> list[tuple[int, ...]]:
    root = np.random.SeedSequence(seed)
    return [tuple(child.spawn_key) for child in root.spawn(count)]


def _child_sequences(
    entropy: int,
    spawn_key: tuple[int, ...],
    count: int,
) -> tuple[list[np.random.SeedSequence], list[int]]:
    parent = np.random.SeedSequence(entropy, spawn_key=spawn_key)
    children = parent.spawn(count)
    return children, [seed_sequence_int(child) for child in children]


def _operator_spec(
    config: dict[str, Any],
    *,
    arm: str,
    repetition: int,
) -> AuthorRoutingSpec:
    true_rank = (
        (2, 4, 6, 8)[repetition % 4]
        if arm == "core_lr" else 6
    )
    return AuthorRoutingSpec(
        groups=int(config["groups"]),
        authors=int(config["authors"]),
        discovery_contexts=int(config["discovery_contexts"]),
        confirmation_contexts=int(config["confirmation_contexts"]),
        extrapolation_contexts=int(config["extrapolation_contexts"]),
        sessions=int(config["sessions"]),
        events_per_context_session=(
            32 if arm == "low_budget"
            else int(config["events_per_context_session"])
        ),
        author_rank=true_rank,
        group_rms=0.25 if arm == "group_mix" else 0.0,
    )


def _path_spec(
    config: dict[str, Any],
    *,
    threshold: float,
) -> TransportPathSpec:
    return TransportPathSpec(
        path_points=int(config["path_points"]),
        locator_window=int(config["locator_window"]),
        threshold=float(threshold),
    )


def _mechanism(arm: str) -> str:
    if arm == "out_of_family":
        return "out_of_family"
    if arm == "high_noise":
        return "high_noise"
    return "core"


def _localization_discovery_worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> list[dict[str, Any]]:
    config, repetition, spawn_key = payload
    children, component_seeds = _child_sequences(
        int(config["seed"]),
        spawn_key,
        3,
    )
    rows = []
    for mechanism_index, mechanism in enumerate(
        ("core", "out_of_family", "high_noise")
    ):
        mechanism_seed = component_seeds[mechanism_index]
        for threshold in config["threshold_candidates"]:
            metrics = transport_localization_metrics(
                rng=np.random.default_rng(mechanism_seed),
                spec=_path_spec(config, threshold=float(threshold)),
                mechanism=mechanism,
                positive_count=int(config["discovery_positive_paths"]),
                negative_count=int(config["discovery_negative_paths"]),
            )
            rows.append({
                "stage": "discovery_locator",
                "repetition": repetition,
                "spawn_key": json.dumps(spawn_key),
                "mechanism": mechanism,
                "threshold": float(threshold),
                **metrics,
            })
    return rows


def _independent_panels(
    latent: dict[str, Any],
    children: list[np.random.SeedSequence],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    return tuple(
        resample_routing_counts(
            latent,
            np.random.default_rng(sequence),
        )
        for sequence in children
    )  # type: ignore[return-value]


def _operator_discovery_worker(
    payload: tuple[
        dict[str, Any],
        int,
        tuple[int, ...],
        float,
    ],
) -> list[dict[str, Any]]:
    config, repetition, spawn_key, threshold = payload
    children, component_seeds = _child_sequences(
        int(config["seed"]),
        spawn_key,
        7,
    )
    latent = simulate_author_routing_world(
        seed=component_seeds[0],
        world="stable_author",
        spec=_operator_spec(config, arm="core_lr", repetition=repetition),
    )
    reference, blind_source, oracle_train, oracle_valid = (
        _independent_panels(latent, children[1:5])
    )
    blind, _ = localize_routing_counts(
        blind_source,
        rng=np.random.default_rng(children[5]),
        spec=_path_spec(config, threshold=threshold),
        mechanism="core",
    )
    losses = rank_lambda_cv_losses_group_free(
        reference_train=reference,
        blind_train=blind,
        oracle_valid=oracle_valid,
        ranks=config["rank_candidates"],
        lambdas=config["lambda_candidates"],
    )
    discovery = np.arange(len(latent["contexts"]["discovery"]))
    reference_fit = fit_reference_router(reference, discovery)
    halves = tuple(
        estimate_fixed_reference_profile(
            blind,
            discovery,
            reference_fit=reference_fit,
            sessions=session,
        )
        for session in (0, 1)
    )
    rank_reliability = {}
    for rank in config["rank_candidates"]:
        denoiser = fit_group_free_denoiser(
            halves[0]["profile"],
            halves[1]["profile"],
            rank=int(rank),
        )
        cleaned = tuple(
            apply_group_free_denoiser(row["profile"], denoiser)
            for row in halves
        )
        rank_reliability[int(rank)] = multivariate_reliability(
            cleaned[0],
            cleaned[1],
        )
    return [
        {
            "stage": "discovery_operator",
            "repetition": repetition,
            "spawn_key": json.dumps(spawn_key),
            "component_seeds": json.dumps(component_seeds),
            "true_rank": latent["design"]["author_rank"],
            "rank": rank,
            "lambda_author": value,
            "heldout_log_loss": loss,
            "rank_reliability": rank_reliability[int(rank)],
        }
        for (rank, value), loss in sorted(losses.items())
    ]


def _strip_private(result: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in result.items()
        if not key.startswith("_")
    }


def _confirmation_worker(
    payload: tuple[
        dict[str, Any],
        str,
        int,
        tuple[int, ...],
        float,
        int,
        float,
    ],
) -> dict[str, Any]:
    (
        config,
        arm,
        repetition,
        spawn_key,
        threshold,
        selected_rank,
        selected_lambda,
    ) = payload
    children, component_seeds = _child_sequences(
        int(config["seed"]),
        spawn_key,
        12,
    )
    latent = simulate_author_routing_world(
        seed=component_seeds[0],
        world="stable_author",
        spec=_operator_spec(config, arm=arm, repetition=repetition),
    )
    reference, blind_source, oracle_train, oracle_test = (
        _independent_panels(latent, children[1:5])
    )
    mechanism = _mechanism(arm)
    blind_complete, event_metrics = localize_routing_counts(
        blind_source,
        rng=np.random.default_rng(children[5]),
        spec=_path_spec(config, threshold=threshold),
        mechanism=mechanism,
    )
    panel = transport_localization_metrics(
        rng=np.random.default_rng(children[6]),
        spec=_path_spec(config, threshold=threshold),
        mechanism=mechanism,
        positive_count=int(config["confirmation_positive_paths"]),
        negative_count=int(config["confirmation_negative_paths"]),
    )
    complete = evaluate_group_free_operator(
        latent=latent,
        reference_train=reference,
        blind_train=blind_complete,
        oracle_train=oracle_train,
        oracle_test=oracle_test,
        rank=selected_rank,
        lambda_author=selected_lambda,
        neighbor_count=int(config["local_neighbor_count"]),
    )
    primary = complete
    diagnostics: dict[str, Any] = {}

    if arm in {"mar", "mnar"}:
        masked = apply_registered_missingness(
            blind_complete,
            rng=np.random.default_rng(children[7]),
            kind=arm,
            base_probability=float(config["mar_base_probability"]),
            floor=float(config["mar_probability_floor"]),
            ceiling=float(config["mar_probability_ceiling"]),
            gamma=(
                float(config["mnar_true_gamma"])
                if arm == "mnar" else 0.0
            ),
        )
        available = evaluate_group_free_operator(
            latent=latent,
            reference_train=reference,
            blind_train=masked,
            oracle_train=oracle_train,
            oracle_test=oracle_test,
            rank=selected_rank,
            lambda_author=selected_lambda,
            neighbor_count=int(config["local_neighbor_count"]),
            method="available",
        )
        ipw = evaluate_group_free_operator(
            latent=latent,
            reference_train=reference,
            blind_train=masked,
            oracle_train=oracle_train,
            oracle_test=oracle_test,
            rank=selected_rank,
            lambda_author=selected_lambda,
            neighbor_count=int(config["local_neighbor_count"]),
            method="ipw",
        )
        aipw = evaluate_group_free_operator(
            latent=latent,
            reference_train=reference,
            blind_train=masked,
            oracle_train=oracle_train,
            oracle_test=oracle_test,
            rank=selected_rank,
            lambda_author=selected_lambda,
            neighbor_count=int(config["local_neighbor_count"]),
            method="aipw",
        )
        primary = aipw
        diagnostics = {
            "complete_truth_correlation": complete["truth_correlation"],
            "complete_truth_nrmse": complete["truth_nrmse"],
            "available_truth_correlation": available["truth_correlation"],
            "available_truth_nrmse": available["truth_nrmse"],
            "ipw_truth_correlation": ipw["truth_correlation"],
            "ipw_truth_nrmse": ipw["truth_nrmse"],
            "aipw_truth_correlation": aipw["truth_correlation"],
            "aipw_truth_nrmse": aipw["truth_nrmse"],
            "available_excess_nrmse": (
                available["truth_nrmse"] - complete["truth_nrmse"]
            ),
            "ipw_excess_nrmse": (
                ipw["truth_nrmse"] - complete["truth_nrmse"]
            ),
            "aipw_excess_nrmse": (
                aipw["truth_nrmse"] - complete["truth_nrmse"]
            ),
            "masked_available_fraction": aipw["mean_available_fraction"],
        }
        if arm == "mnar":
            diagnostics.update(mnar_sensitivity_envelope(
                masked=masked,
                reference_fit=aipw["_reference_fit"],
                truth_profile=aipw["_truth_profile"],
                rank=selected_rank,
                gamma_grid=config["mnar_gamma_grid"],
                floor=float(config["mar_probability_floor"]),
                ceiling=float(config["mar_probability_ceiling"]),
            ))
    return {
        "stage": "confirmation",
        "arm": arm,
        "repetition": repetition,
        "spawn_key": json.dumps(spawn_key),
        "component_seeds": json.dumps(component_seeds),
        "true_rank": latent["design"]["author_rank"],
        "selected_rank": selected_rank,
        "selected_lambda": selected_lambda,
        **panel,
        **event_metrics,
        **_strip_private(primary),
        **diagnostics,
    }


def _parallel(
    function: Any,
    payloads: list[Any],
    *,
    jobs: int,
) -> list[Any]:
    if jobs <= 1:
        return [function(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(function, payloads, chunksize=1))


def _mean_interval(
    values: pd.Series,
    *,
    rng: np.random.Generator,
    draws: int = 4000,
) -> dict[str, float | int]:
    vector = (
        pd.to_numeric(values, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
        .to_numpy()
    )
    if len(vector) == 0:
        return {
            "n": 0,
            "mean": float("nan"),
            "lower95": float("nan"),
            "upper95": float("nan"),
        }
    sampled = rng.choice(vector, size=(draws, len(vector)), replace=True)
    means = sampled.mean(axis=1)
    return {
        "n": len(vector),
        "mean": float(vector.mean()),
        "lower95": float(np.quantile(means, 0.025)),
        "upper95": float(np.quantile(means, 0.975)),
    }


SUMMARY_METRICS = (
    "precision",
    "recall",
    "f1",
    "unconditional_median_error",
    "unconditional_p95_error",
    "false_junction_rate",
    "incoming_accuracy_detected",
    "outgoing_accuracy_detected",
    "isomorphic_auc",
    "truth_correlation",
    "truth_nrmse",
    "independent_oracle_correlation",
    "split_session_reliability",
    "unseen_context_reliability",
    "same_author_auc",
    "local_neighbor_auc",
    "top1",
    "true_group_sensitivity_auc",
    "blind_log_loss_gain",
    "oracle_log_loss_gain",
    "predictive_gain_retention",
    "blind_ece",
    "mean_available_fraction",
    "complete_truth_correlation",
    "complete_truth_nrmse",
    "available_truth_correlation",
    "available_truth_nrmse",
    "ipw_truth_correlation",
    "ipw_truth_nrmse",
    "aipw_truth_correlation",
    "aipw_truth_nrmse",
    "available_excess_nrmse",
    "ipw_excess_nrmse",
    "aipw_excess_nrmse",
    "masked_available_fraction",
    "mnar_sensitivity_coverage",
    "mnar_sensitivity_mean_width",
    "mnar_sensitivity_min_truth_correlation",
    "mnar_sensitivity_max_truth_correlation",
)


def _summaries(
    confirmation: pd.DataFrame,
    *,
    seed: int,
) -> dict[str, Any]:
    root = np.random.SeedSequence(seed)
    children = iter(root.spawn(len(SUMMARY_METRICS) * 10))
    output = {}
    for arm, frame in confirmation.groupby("arm", sort=False):
        summary = {
            "arm": arm,
            "n": len(frame),
            "numeric_rate": float(frame["numeric_output"].mean()),
            "isomorphic_refusal_rate": float(
                frame["isomorphic_refusal"].mean()
            ),
        }
        for metric in SUMMARY_METRICS:
            if metric in frame and frame[metric].notna().any():
                summary[metric] = _mean_interval(
                    frame[metric],
                    rng=np.random.default_rng(next(children)),
                )
        if (
            "blind_log_loss_gain" in frame
            and "oracle_log_loss_gain" in frame
        ):
            blind = frame["blind_log_loss_gain"].to_numpy(dtype=float)
            oracle = frame["oracle_log_loss_gain"].to_numpy(dtype=float)
            oracle_mean = float(oracle.mean())
            if oracle_mean > 1e-12:
                rng = np.random.default_rng(next(children))
                indices = rng.integers(
                    0,
                    len(frame),
                    size=(4000, len(frame)),
                )
                oracle_boot = oracle[indices].mean(axis=1)
                valid = oracle_boot > 1e-12
                ratio = (
                    blind[indices][valid].mean(axis=1)
                    / oracle_boot[valid]
                )
                summary["gain_retention_ratio"] = {
                    "n": len(frame),
                    "mean": float(blind.mean() / oracle_mean),
                    "lower95": float(np.quantile(ratio, 0.025)),
                    "upper95": float(np.quantile(ratio, 0.975)),
                    "status": "INTERPRETABLE_POSITIVE_ORACLE_GAIN",
                }
            else:
                summary["gain_retention_ratio"] = {
                    "n": len(frame),
                    "mean": None,
                    "lower95": None,
                    "upper95": None,
                    "status": "UNDEFINED_NONPOSITIVE_ORACLE_GAIN",
                }
        output[str(arm)] = summary
    return output


def _seed_audit(frames: list[pd.DataFrame]) -> dict[str, Any]:
    spawn_keys = []
    component_seeds = []
    for frame in frames:
        if "spawn_key" in frame:
            spawn_keys.extend(frame["spawn_key"].drop_duplicates().tolist())
        if "component_seeds" in frame:
            for value in frame["component_seeds"].drop_duplicates():
                component_seeds.extend(json.loads(value))
    return {
        "spawn_keys": len(spawn_keys),
        "unique_spawn_keys": len(set(spawn_keys)),
        "component_seeds": len(component_seeds),
        "unique_component_seeds": len(set(component_seeds)),
        "pass": (
            len(spawn_keys) == len(set(spawn_keys))
            and len(component_seeds) == len(set(component_seeds))
        ),
    }


def _decision(
    confirmation: pd.DataFrame,
    *,
    config: dict[str, Any],
    selected_threshold: float,
    selected_rank: int,
    selected_lambda: float,
    seed_audit: dict[str, Any],
    smoke: bool,
) -> dict[str, Any]:
    summaries = _summaries(
        confirmation,
        seed=int(config["seed"]) ^ 0x7A31C,
    )
    if smoke:
        checks = {
            "numeric": all(
                row["numeric_rate"] == 1.0
                for row in summaries.values()
            ),
            "core_direction": (
                summaries["core_lr"]["truth_correlation"]["mean"] > 0.60
                and summaries["core_lr"]["local_neighbor_auc"]["mean"] > 0.65
            ),
            "transport_direction": (
                summaries["out_of_family"]["f1"]["mean"] > 0.50
                and summaries["high_noise"]["f1"]["mean"] > 0.40
            ),
            "seed_audit": seed_audit["pass"],
        }
        return {
            "status": (
                "V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_SMOKE_PASS"
                if all(checks.values())
                else "V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_SMOKE_STOP"
            ),
            "selected_threshold": selected_threshold,
            "selected_rank": selected_rank,
            "selected_lambda": selected_lambda,
            "checks": checks,
            "summary": summaries,
            "seed_audit": seed_audit,
            "claim_boundary": "Smoke behavior only.",
        }
    gates = config["gates"]
    core = summaries["core_lr"]
    group = summaries["group_mix"]
    low_budget = summaries["low_budget"]
    oof = summaries["out_of_family"]
    noise = summaries["high_noise"]
    mar = summaries["mar"]
    mnar = summaries["mnar"]
    max_p95 = (
        gates["maximum_unconditional_p95_fraction"]
        * int(config["path_points"])
    )
    checks = {
        "core_truth": (
            core["truth_correlation"]["lower95"]
            >= gates["minimum_core_truth_correlation"]
        ),
        "core_gain_retention": (
            core["gain_retention_ratio"]["lower95"]
            >= gates["minimum_core_gain_retention"]
        ),
        "core_local_auc": (
            core["local_neighbor_auc"]["lower95"]
            >= gates["minimum_core_local_auc"]
        ),
        "group_free_sensitivity": (
            group["true_group_sensitivity_auc"]["lower95"]
            >= gates["minimum_group_sensitivity_auc"]
        ),
        "low_budget_boundary": (
            low_budget["truth_correlation"]["upper95"]
            <= gates["maximum_low_budget_truth_correlation"]
        ),
        "out_of_family_operator": (
            oof["truth_correlation"]["lower95"]
            >= gates["minimum_stress_truth_correlation"]
            and oof["gain_retention_ratio"]["lower95"]
            >= gates["minimum_stress_gain_retention"]
            and oof["local_neighbor_auc"]["lower95"]
            >= gates["minimum_stress_local_auc"]
        ),
        "high_noise_operator": (
            noise["truth_correlation"]["lower95"]
            >= gates["minimum_stress_truth_correlation"]
            and noise["gain_retention_ratio"]["lower95"]
            >= gates["minimum_stress_gain_retention"]
            and noise["local_neighbor_auc"]["lower95"]
            >= gates["minimum_stress_local_auc"]
        ),
        "core_locator": (
            core["f1"]["lower95"] >= gates["minimum_core_f1"]
        ),
        "stress_locator": (
            min(oof["f1"]["lower95"], noise["f1"]["lower95"])
            >= gates["minimum_stress_f1"]
        ),
        "unconditional_location_error": all(
            row["unconditional_median_error"]["upper95"]
            <= gates["maximum_unconditional_median_error"]
            and row["unconditional_p95_error"]["upper95"] <= max_p95
            for row in (core, oof, noise)
        ),
        "negative_control": max(
            core["false_junction_rate"]["upper95"],
            oof["false_junction_rate"]["upper95"],
            noise["false_junction_rate"]["upper95"],
        ) <= gates["maximum_false_junction_rate"],
        "isomorphic_refusal": all(
            row["isomorphic_refusal_rate"] >= 0.95
            and row["isomorphic_auc"]["mean"]
            >= gates["minimum_isomorphic_auc"]
            and row["isomorphic_auc"]["mean"]
            <= gates["maximum_isomorphic_auc"]
            for row in (core, oof, noise)
        ),
        "mar_support": (
            mar["masked_available_fraction"]["lower95"]
            >= gates["minimum_mar_available_fraction"]
            and mar["masked_available_fraction"]["upper95"]
            <= gates["maximum_mar_available_fraction"]
        ),
        "mar_aipw_excess_nrmse": (
            mar["aipw_excess_nrmse"]["upper95"]
            <= gates["maximum_mar_aipw_excess_nrmse"]
        ),
        "mar_not_available_only": (
            mar["aipw_excess_nrmse"]["mean"]
            <= mar["available_excess_nrmse"]["mean"]
        ),
        "mnar_sensitivity": (
            mnar["mnar_sensitivity_coverage"]["lower95"]
            >= gates["minimum_mnar_sensitivity_coverage"]
        ),
        "seed_independence": seed_audit["pass"],
        "rank_not_upper_boundary": (
            selected_rank != max(config["rank_candidates"])
        ),
        "lambda_not_upper_boundary": (
            selected_lambda != max(config["lambda_candidates"])
        ),
        "threshold_not_boundary": (
            selected_threshold != min(config["threshold_candidates"])
            and selected_threshold != max(config["threshold_candidates"])
        ),
    }
    return {
        "status": (
            "V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_PASS"
            if all(checks.values())
            else "V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_STOP"
        ),
        "selected_threshold": selected_threshold,
        "selected_rank": selected_rank,
        "selected_lambda": selected_lambda,
        "checks": checks,
        "summary": summaries,
        "seed_audit": seed_audit,
        "claim_boundary": config["claim_boundary"],
    }


def _verify_parents(config: dict[str, Any]) -> dict[str, Any]:
    failures = []
    for relative, expected in config["parent_seals"].items():
        path = ROOT / relative
        got = sha256_file(path) if path.is_file() else None
        if got != expected:
            failures.append({
                "path": relative,
                "expected": expected,
                "actual": got,
            })
    if failures:
        raise RuntimeError(f"parent seal mismatch: {failures}")
    return {
        "status": "PARENT_SEALS_PASS",
        "files": config["parent_seals"],
    }


def _verify_own_seal(
    seal_path: Path | None,
    *,
    smoke: bool,
    preseal_power: bool,
) -> dict[str, Any]:
    if smoke or preseal_power:
        return {"status": "OWN_SEAL_NOT_REQUIRED_PRESEAL"}
    if seal_path is None or not seal_path.is_file():
        raise RuntimeError("canonical V3.7C requires a prospective seal")
    seal = _read_json(seal_path)
    failures = []
    for relative, expected in seal["files"].items():
        path = ROOT / relative
        if not path.is_file() or sha256_file(path) != expected:
            failures.append(relative)
    if failures:
        raise RuntimeError(f"V3.7C seal mismatch: {failures}")
    return {
        "status": "V37C_PROSPECTIVE_SEAL_PASS",
        "path": str(seal_path),
        "sha256": hashlib.sha256(seal_path.read_bytes()).hexdigest(),
    }


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 Group-Free Routing Transport V3.7C

Decision: `{decision["status"]}`

Selected threshold/rank/lambda:
`{decision["selected_threshold"]}` / `{decision["selected_rank"]}` /
`{decision["selected_lambda"]}`

## Gates

```json
{json.dumps(decision["checks"], ensure_ascii=False, indent=2)}
```

## Summary

```json
{json.dumps(decision["summary"], ensure_ascii=False, indent=2, allow_nan=True)}
```

## Seed audit

```json
{json.dumps(decision["seed_audit"], ensure_ascii=False, indent=2)}
```

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT
        / "configs/v8_group_free_routing_transport_v37c.json",
    )
    parser.add_argument(
        "--seal",
        type=Path,
        default=ROOT
        / "configs/v8_group_free_routing_transport_v37c_seal.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT
        / "results/v8_group_free_routing_transport/v37c",
    )
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--preseal-power", action="store_true")
    args = parser.parse_args()
    config = _read_json(args.config)
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 4
        config["confirmation_repetitions"] = 4
        config["discovery_positive_paths"] = 200
        config["discovery_negative_paths"] = 400
        config["confirmation_positive_paths"] = 200
        config["confirmation_negative_paths"] = 400
    if args.preseal_power:
        config = json.loads(json.dumps(config))
        config["discovery_repetitions"] = 12
        config["confirmation_repetitions"] = 20
        config["discovery_positive_paths"] = 400
        config["discovery_negative_paths"] = 800
        config["confirmation_positive_paths"] = 400
        config["confirmation_negative_paths"] = 800

    parent_status = _verify_parents(config)
    own_seal = _verify_own_seal(
        args.seal,
        smoke=args.smoke,
        preseal_power=args.preseal_power,
    )
    discovery_n = int(config["discovery_repetitions"])
    confirmation_n = int(config["confirmation_repetitions"])
    total_keys = (
        discovery_n
        + discovery_n
        + confirmation_n * len(config["arms"])
    )
    keys = _root_child_keys(int(config["seed"]), total_keys)
    cursor = 0
    locator_keys = keys[cursor : cursor + discovery_n]
    cursor += discovery_n
    locator_nested = _parallel(
        _localization_discovery_worker,
        [
            (config, repetition, locator_keys[repetition])
            for repetition in range(discovery_n)
        ],
        jobs=int(config["jobs"]),
    )
    locator = pd.DataFrame([
        row for rows in locator_nested for row in rows
    ])
    locator_summary = (
        locator.groupby(["threshold", "mechanism"], as_index=False)
        .agg({
            "f1": "mean",
            "recall": "mean",
            "false_junction_rate": "mean",
            "unconditional_p95_error": "mean",
        })
    )
    threshold_pivot = (
        locator_summary.groupby("threshold", as_index=False)
        .agg({
            "f1": "min",
            "recall": "min",
            "false_junction_rate": "max",
            "unconditional_p95_error": "max",
        })
    )
    eligible = threshold_pivot[
        threshold_pivot["false_junction_rate"]
        <= float(config["gates"]["maximum_false_junction_rate"])
    ]
    if len(eligible) == 0:
        raise RuntimeError("no locator threshold controls false positives")
    selected_threshold = float(
        eligible.sort_values(
            ["f1", "recall", "threshold"],
            ascending=[False, False, True],
        ).iloc[0]["threshold"]
    )

    operator_keys = keys[cursor : cursor + discovery_n]
    cursor += discovery_n
    operator_nested = _parallel(
        _operator_discovery_worker,
        [
            (
                config,
                repetition,
                operator_keys[repetition],
                selected_threshold,
            )
            for repetition in range(discovery_n)
        ],
        jobs=int(config["jobs"]),
    )
    operator = pd.DataFrame([
        row for rows in operator_nested for row in rows
    ])
    operator_summary = (
        operator.groupby(
            ["rank", "lambda_author"],
            as_index=False,
        )
        .agg({
            "heldout_log_loss": "mean",
            "rank_reliability": "mean",
        })
        .sort_values(
            ["heldout_log_loss", "rank", "lambda_author"],
        )
    )
    stable_operator = operator_summary[
        operator_summary["rank_reliability"]
        >= float(config["minimum_discovery_rank_reliability"])
    ]
    if len(stable_operator) == 0:
        raise RuntimeError("no discovery rank meets reliability floor")
    best_loss = float(stable_operator["heldout_log_loss"].min())
    near_optimal = stable_operator[
        stable_operator["heldout_log_loss"]
        <= best_loss + float(config["selection_loss_tolerance"])
    ]
    selected = near_optimal.sort_values(
        ["rank", "heldout_log_loss", "lambda_author"],
    ).iloc[0]
    selected_rank = int(selected["rank"])
    selected_lambda = float(selected["lambda_author"])

    confirmation_payloads = []
    for arm in config["arms"]:
        for repetition in range(confirmation_n):
            confirmation_payloads.append((
                config,
                str(arm),
                repetition,
                keys[cursor],
                selected_threshold,
                selected_rank,
                selected_lambda,
            ))
            cursor += 1
    confirmation = pd.DataFrame(
        _parallel(
            _confirmation_worker,
            confirmation_payloads,
            jobs=int(config["jobs"]),
        )
    )
    seed_audit = _seed_audit([operator, confirmation])
    decision = _decision(
        confirmation,
        config=config,
        selected_threshold=selected_threshold,
        selected_rank=selected_rank,
        selected_lambda=selected_lambda,
        seed_audit=seed_audit,
        smoke=args.smoke,
    )
    if args.preseal_power:
        decision["status"] = decision["status"].replace(
            "V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_",
            "V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_PRESEAL_POWER_",
        )
    decision["parent_seals"] = parent_status
    decision["prospective_seal"] = own_seal

    args.output_dir.mkdir(parents=True, exist_ok=True)
    locator.to_csv(
        args.output_dir / "discovery_locator_metrics.csv",
        index=False,
    )
    locator_summary.to_csv(
        args.output_dir / "discovery_locator_summary.csv",
        index=False,
    )
    operator.to_csv(
        args.output_dir / "discovery_operator_metrics.csv",
        index=False,
    )
    operator_summary.to_csv(
        args.output_dir / "discovery_operator_summary.csv",
        index=False,
    )
    confirmation.to_csv(
        args.output_dir / "confirmation_metrics.csv",
        index=False,
    )
    _write_json(args.output_dir / "decision.json", decision)
    _write_json(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _report(decision),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            ROOT / relative for relative in config["parent_seals"]
        ],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_author_routing_operator.py",
            ROOT / "suica_core/v8_blind_junction_localization.py",
            ROOT / "suica_core/v8_group_free_routing_transport.py",
            Path(__file__),
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps({
        "status": decision["status"],
        "selected_threshold": selected_threshold,
        "selected_rank": selected_rank,
        "selected_lambda": selected_lambda,
        "output_dir": str(args.output_dir),
        "checks": decision["checks"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
