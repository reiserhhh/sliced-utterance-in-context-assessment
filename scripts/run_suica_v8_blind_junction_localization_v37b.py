#!/usr/bin/env python3
"""Run the V3.7B geometry-only blind junction localization experiment."""
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
from scipy.stats import beta

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
    simulate_author_routing_world,
)
from suica_core.v8_blind_junction_localization import (  # noqa: E402
    BlindJunctionSpec,
    compare_blind_and_oracle_operator,
    localization_panel_metrics,
    localize_routing_sample,
    simulate_junction_trajectories,
    simulate_no_junction_trajectories,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=True)
        + "\n",
        encoding="utf-8",
    )


def _blind_spec(
    config: dict[str, Any],
    *,
    threshold: float,
) -> BlindJunctionSpec:
    return BlindJunctionSpec(
        path_points=int(config["path_points"]),
        junction_min=int(config["junction_min"]),
        junction_max=int(config["junction_max"]),
        locator_window=int(config["locator_window"]),
        threshold=float(threshold),
        trajectory_noise_sd=float(config["trajectory_noise_sd"]),
        cue_distractor_rate=float(config["cue_distractor_rate"]),
        cusp_amplitude_min=float(config["cusp_amplitude_min"]),
        cusp_amplitude_max=float(config["cusp_amplitude_max"]),
        pause_inner_min=float(config["pause_inner_min"]),
        pause_inner_max=float(config["pause_inner_max"]),
        branch_angle_jitter_sd=float(
            config["branch_angle_jitter_sd"]
        ),
    )


def _operator_spec(config: dict[str, Any]) -> AuthorRoutingSpec:
    return AuthorRoutingSpec(
        author_rank=int(config["operator_rank"]),
        events_per_context_session=int(
            config["operator_events_per_context_session"]
        ),
    )


def _panel(
    *,
    seed: int,
    positive_count: int,
    negative_count: int,
    spec: BlindJunctionSpec,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    rng = np.random.default_rng(seed)
    positive = simulate_junction_trajectories(
        rng.integers(0, spec.branches, size=positive_count),
        rng.integers(0, spec.branches, size=positive_count),
        rng.integers(0, spec.branches, size=positive_count),
        seed=seed + 11,
        spec=spec,
    )
    negative = simulate_no_junction_trajectories(
        seed=seed + 23,
        count=negative_count,
        spec=spec,
    )
    return positive, negative


def _discovery_worker(
    payload: tuple[dict[str, Any], int],
) -> list[dict[str, Any]]:
    config, repetition = payload
    seed = int(config["seed"]) + repetition
    spec = _blind_spec(config, threshold=0.0)
    positive, negative = _panel(
        seed=seed,
        positive_count=int(config["discovery_positive_paths"]),
        negative_count=int(config["discovery_negative_paths"]),
        spec=spec,
    )
    rows = []
    for threshold in config["threshold_candidates"]:
        rows.append({
            "stage": "discovery",
            "repetition": repetition,
            "seed": seed,
            "threshold": float(threshold),
            **localization_panel_metrics(
                positive,
                negative,
                window=spec.locator_window,
                threshold=float(threshold),
            ),
        })
    return rows


def _claim_thresholds() -> dict[str, float]:
    return {
        "minimum_within_group_auc": 0.65,
        "minimum_multivariate_reliability": 0.60,
        "minimum_log_loss_gain": 0.005,
    }


def _confirmation_worker(
    payload: tuple[dict[str, Any], int, float],
) -> dict[str, Any]:
    config, repetition, threshold = payload
    seed = int(config["seed"]) + 50_000_000 + repetition
    spec = _blind_spec(config, threshold=threshold)
    positive, negative = _panel(
        seed=seed,
        positive_count=int(config["confirmation_positive_paths"]),
        negative_count=int(config["confirmation_negative_paths"]),
        spec=spec,
    )
    panel = localization_panel_metrics(
        positive,
        negative,
        window=spec.locator_window,
        threshold=threshold,
    )
    operator_spec = _operator_spec(config)
    oracle = simulate_author_routing_world(
        seed=seed + 101,
        world="stable_author",
        spec=operator_spec,
    )
    blind, routing = localize_routing_sample(
        oracle,
        seed=seed + 211,
        spec=spec,
    )
    operator = compare_blind_and_oracle_operator(
        oracle,
        blind,
        rank=int(config["operator_rank"]),
        selected_lambda=float(config["operator_lambda"]),
        seed=seed + 307,
        claim_thresholds=_claim_thresholds(),
    )
    cue_oracle = simulate_author_routing_world(
        seed=seed + 401,
        world="cue_leakage",
        spec=operator_spec,
    )
    cue_blind, _ = localize_routing_sample(
        cue_oracle,
        seed=seed + 503,
        spec=spec,
    )
    cue_operator = compare_blind_and_oracle_operator(
        cue_oracle,
        cue_blind,
        rank=int(config["operator_rank"]),
        selected_lambda=float(config["operator_lambda"]),
        seed=seed + 601,
        claim_thresholds=_claim_thresholds(),
    )
    return {
        "stage": "confirmation",
        "repetition": repetition,
        "seed": seed,
        "threshold": threshold,
        **panel,
        **routing,
        **operator,
        "cue_leak_author_claim": cue_operator["blind_author_claim"],
        "cue_leak_operator_correlation": cue_operator[
            "operator_correlation"
        ],
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
    seed: int,
    draws: int = 4_000,
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
    rng = np.random.default_rng(seed)
    means = rng.choice(
        vector,
        size=(draws, len(vector)),
        replace=True,
    ).mean(axis=1)
    return {
        "n": len(vector),
        "mean": float(vector.mean()),
        "lower95": float(np.quantile(means, 0.025)),
        "upper95": float(np.quantile(means, 0.975)),
    }


def _rate(values: pd.Series) -> dict[str, float | int]:
    vector = values.fillna(False).astype(bool)
    successes = int(vector.sum())
    trials = len(vector)
    lower = (
        0.0
        if successes == 0
        else float(beta.ppf(0.05, successes, trials - successes + 1))
    )
    upper = (
        1.0
        if successes == trials
        else float(beta.ppf(0.95, successes + 1, trials - successes))
    )
    return {
        "successes": successes,
        "trials": trials,
        "rate": successes / max(trials, 1),
        "lower95": lower,
        "upper95": upper,
    }


METRICS = (
    "precision",
    "recall",
    "f1",
    "median_location_error",
    "p95_location_error",
    "false_junctions_per_1000",
    "detection_rate",
    "correct_location_rate",
    "incoming_accuracy_detected",
    "outgoing_accuracy_detected",
    "operator_correlation",
    "oracle_log_loss_gain",
    "blind_log_loss_gain",
    "predictive_gain_retention",
    "blind_truth_correlation",
    "blind_split_session_reliability",
    "blind_unseen_context_reliability",
    "blind_within_group_auc",
    "blind_available_fraction",
)


def _decision(
    confirmation: pd.DataFrame,
    *,
    threshold: float,
    config: dict[str, Any],
    smoke: bool,
) -> dict[str, Any]:
    summary = {
        metric: _mean_interval(
            confirmation[metric],
            seed=int(config["seed"]) + index,
        )
        for index, metric in enumerate(METRICS)
    }
    summary["blind_author_claim"] = _rate(
        confirmation["blind_author_claim"]
    )
    summary["cue_leak_author_claim"] = _rate(
        confirmation["cue_leak_author_claim"]
    )
    if smoke:
        checks = {
            "localization": (
                summary["f1"]["mean"] > 0.80
                and summary["false_junctions_per_1000"]["mean"] <= 5.0
            ),
            "route_recovery": (
                summary["incoming_accuracy_detected"]["mean"] > 0.95
                and summary["outgoing_accuracy_detected"]["mean"] > 0.95
            ),
            "operator_direction": (
                summary["operator_correlation"]["mean"] > 0.80
                and summary["predictive_gain_retention"]["mean"] > 0.80
            ),
            "cue_control": (
                summary["cue_leak_author_claim"]["successes"] == 0
            ),
        }
        return {
            "status": (
                "V8_BLIND_JUNCTION_LOCALIZATION_V37B_SMOKE_PASS"
                if all(checks.values())
                else "V8_BLIND_JUNCTION_LOCALIZATION_V37B_SMOKE_STOP"
            ),
            "selected_threshold": threshold,
            "checks": checks,
            "summary": summary,
            "claim_boundary": "Smoke behavior only.",
        }
    gates = config["gates"]
    checks = {
        "precision": (
            summary["precision"]["lower95"]
            >= gates["minimum_precision"]
        ),
        "recall": (
            summary["recall"]["lower95"] >= gates["minimum_recall"]
        ),
        "f1": summary["f1"]["lower95"] >= gates["minimum_f1"],
        "median_location_error": (
            summary["median_location_error"]["upper95"]
            <= gates["maximum_median_location_error"]
        ),
        "p95_location_error": (
            summary["p95_location_error"]["upper95"]
            <= gates["maximum_p95_location_error"]
        ),
        "false_junction_rate": (
            summary["false_junctions_per_1000"]["upper95"]
            <= gates["maximum_false_junctions_per_1000"]
        ),
        "operator_correlation": (
            summary["operator_correlation"]["lower95"]
            >= gates["minimum_operator_correlation"]
        ),
        "predictive_gain_retention": (
            summary["predictive_gain_retention"]["lower95"]
            >= gates["minimum_predictive_gain_retention"]
        ),
        "cue_leak_control": (
            summary["cue_leak_author_claim"]["upper95"]
            <= gates["maximum_cue_leak_author_claim_rate"]
        ),
        "blind_author_claim_rate": (
            summary["blind_author_claim"]["lower95"]
            >= gates["minimum_blind_author_claim_rate"]
        ),
        "masked_opportunity_coverage": (
            summary["blind_available_fraction"]["lower95"]
            >= gates["minimum_blind_available_fraction"]
        ),
        "threshold_not_boundary": (
            threshold != min(config["threshold_candidates"])
            and threshold != max(config["threshold_candidates"])
        ),
    }
    return {
        "status": (
            "V8_BLIND_JUNCTION_LOCALIZATION_V37B_PASS"
            if all(checks.values())
            else "V8_BLIND_JUNCTION_LOCALIZATION_V37B_STOP"
        ),
        "selected_threshold": threshold,
        "checks": checks,
        "summary": summary,
        "claim_boundary": config["claim_boundary"],
    }


def _verify_seals(
    *,
    seal_path: Path | None,
    smoke: bool,
    preseal_power: bool,
) -> dict[str, Any]:
    a_seal_path = ROOT / "configs/v8_author_routing_operator_v37a_seal.json"
    a_seal = _read_json(a_seal_path)
    failures = []
    for relative, expected in a_seal["files"].items():
        if sha256_file(ROOT / relative) != expected:
            failures.append(f"V3.7A:{relative}")
    if not smoke and not preseal_power:
        if seal_path is None or not seal_path.exists():
            raise RuntimeError("canonical V3.7B requires its prospective seal")
        b_seal = _read_json(seal_path)
        for relative, expected in b_seal["files"].items():
            if sha256_file(ROOT / relative) != expected:
                failures.append(f"V3.7B:{relative}")
    if failures:
        raise RuntimeError(f"prospective seal mismatch: {failures}")
    return {
        "status": (
            "V37A_AND_V37B_SEALS_PASS"
            if not smoke and not preseal_power
            else "V37A_SEAL_PASS_V37B_PRESEAL"
        ),
        "v37a_seal_sha256": hashlib.sha256(
            a_seal_path.read_bytes()
        ).hexdigest(),
        "v37b_seal": (
            str(seal_path)
            if seal_path is not None and seal_path.exists()
            else None
        ),
    }


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 Blind Junction Localization V3.7B

Decision: `{decision["status"]}`

Selected threshold: `{decision["selected_threshold"]}`

## Gates

```json
{json.dumps(decision["checks"], ensure_ascii=False, indent=2)}
```

## Summary

```json
{json.dumps(decision["summary"], ensure_ascii=False, indent=2, allow_nan=True)}
```

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_blind_junction_localization_v37b.json",
    )
    parser.add_argument(
        "--seal",
        type=Path,
        default=ROOT / "configs/v8_blind_junction_localization_v37b_seal.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_blind_junction_localization/v37b",
    )
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--preseal-power", action="store_true")
    args = parser.parse_args()
    config = _read_json(args.config)
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 3
        config["confirmation_repetitions"] = 3
    if args.preseal_power:
        config = json.loads(json.dumps(config))
        config["discovery_repetitions"] = 20
        config["confirmation_repetitions"] = 60
    seals = _verify_seals(
        seal_path=args.seal,
        smoke=args.smoke,
        preseal_power=args.preseal_power,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    discovery_nested = _parallel(
        _discovery_worker,
        [
            (config, repetition)
            for repetition in range(int(config["discovery_repetitions"]))
        ],
        jobs=int(config["jobs"]),
    )
    discovery = pd.DataFrame([
        row for rows in discovery_nested for row in rows
    ])
    threshold_summary = (
        discovery.groupby("threshold", as_index=False)
        .agg({
            "f1": "mean",
            "precision": "mean",
            "recall": "mean",
            "false_junctions_per_1000": "mean",
        })
    )
    eligible = threshold_summary[
        threshold_summary["false_junctions_per_1000"]
        <= float(config["gates"]["maximum_false_junctions_per_1000"])
    ]
    if len(eligible) == 0:
        raise RuntimeError("no discovery threshold controls false junctions")
    selected = eligible.sort_values(
        ["f1", "recall", "threshold"],
        ascending=[False, False, True],
    ).iloc[0]
    threshold = float(selected["threshold"])

    confirmation = pd.DataFrame(
        _parallel(
            _confirmation_worker,
            [
                (config, repetition, threshold)
                for repetition in range(
                    int(config["confirmation_repetitions"])
                )
            ],
            jobs=int(config["jobs"]),
        )
    )
    decision = _decision(
        confirmation,
        threshold=threshold,
        config=config,
        smoke=args.smoke,
    )
    if args.preseal_power:
        decision["status"] = decision["status"].replace(
            "V8_BLIND_JUNCTION_LOCALIZATION_V37B_",
            "V8_BLIND_JUNCTION_LOCALIZATION_V37B_PRESEAL_POWER_",
        )
    decision["prospective_seals"] = seals
    discovery.to_csv(
        args.output_dir / "discovery_threshold_metrics.csv",
        index=False,
    )
    threshold_summary.to_csv(
        args.output_dir / "discovery_threshold_summary.csv",
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
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v7_governance.py",
            ROOT / "suica_core/v8_author_routing_operator.py",
            ROOT / "suica_core/v8_blind_junction_localization.py",
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
        "selected_threshold": threshold,
        "output_dir": str(args.output_dir),
        "checks": decision["checks"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
