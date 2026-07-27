#!/usr/bin/env python3
"""Run V3.6 spacetime common-junction routing experiments."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_suica_v8_incidence_incremental as base  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_spacetime_junction_flow import (  # noqa: E402
    JunctionFlowSpec,
    analyze_junction_world,
    simulate_junction_world,
)

POLICIES = ("pass_through", "random_branch", "cue_guided")
CONTROLS = (
    ("cue_shuffle", "cue_guided", "cue_shuffle"),
    ("pass_cue_shuffle", "pass_through", "cue_shuffle"),
    ("time_shuffle", "cue_guided", "time_shuffle"),
    ("tangent_view_shuffle", "cue_guided", "tangent_view_shuffle"),
    ("guided_near_miss", "cue_guided", "near_miss"),
)


def _spec(config: dict[str, Any]) -> JunctionFlowSpec:
    return JunctionFlowSpec(
        authors=int(config["authors"]),
        groups=int(config["groups"]),
        branches=int(config["branches"]),
        depth=int(config["depth"]),
        episodes=int(config["episodes"]),
        views=int(config["views"]),
        ambient=int(config["ambient"]),
        node_radius=float(config["node_radius"]),
        node_spread=float(config["node_spread"]),
        near_miss_spread=float(config["near_miss_spread"]),
        segment_length=float(config["segment_length"]),
        noise_sd=float(config["noise_sd"]),
        time_weight=float(config["time_weight"]),
        minimum_node_persistence=float(
            config["minimum_node_persistence"]
        ),
        minimum_time_tau=float(config["minimum_time_tau"]),
        minimum_view_ari=float(config["minimum_view_ari"]),
        target_information_threshold=float(
            config["target_information_threshold"]
        ),
        nontarget_information_threshold=float(
            config["nontarget_information_threshold"]
        ),
        residual_entropy_threshold=float(
            config["residual_entropy_threshold"]
        ),
    )


def _seed(
    config: dict[str, Any],
    *,
    stage: str,
    repetition: int,
) -> int:
    return (
        int(config["seed"])
        + (0 if stage == "discovery" else 50_000_000)
        + repetition
    )


def _worker(
    payload: tuple[
        dict[str, Any],
        str,
        str,
        str,
        str | None,
        int,
    ],
) -> dict[str, Any]:
    config, stage, name, policy, attack, repetition = payload
    seed = _seed(config, stage=stage, repetition=repetition)
    spec = _spec(config)
    sample = simulate_junction_world(
        seed=seed,
        policy=policy,
        attack=attack,
        spec=spec,
    )
    estimate = analyze_junction_world(sample, spec=spec)
    expected_policy = policy if attack is None else None
    row: dict[str, Any] = {
        "stage": stage,
        "name": name,
        "policy": policy,
        "attack": attack or "",
        "seed": seed,
        "repetition": repetition,
        "expected_policy": expected_policy or "",
        "correct_policy": bool(
            expected_policy is not None
            and estimate["status"] == "ESTIMATE_READY"
            and estimate["predicted_policy"] == expected_policy
        ),
    }
    static = estimate.pop("static_marginal_features")
    for index, value in enumerate(static):
        row[f"static_{index}"] = float(value)
    for key, value in estimate.items():
        if key == "selected_groups":
            row[key] = json.dumps(value, separators=(",", ":"))
        else:
            row[key] = value
    return row


def _parallel(
    payloads: list[Any],
    *,
    jobs: int,
) -> list[dict[str, Any]]:
    if jobs <= 1:
        return [_worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(_worker, payloads, chunksize=1))


def _run_primary(
    config: dict[str, Any],
    *,
    stage: str,
    repetitions: int,
) -> pd.DataFrame:
    payloads = [
        (config, stage, policy, policy, None, repetition)
        for repetition in range(repetitions)
        for policy in POLICIES
    ]
    return pd.DataFrame(_parallel(payloads, jobs=int(config["jobs"])))


def _run_controls(
    config: dict[str, Any],
    *,
    repetitions: int,
) -> pd.DataFrame:
    payloads = [
        (
            config,
            "confirmation",
            name,
            policy,
            attack,
            repetition,
        )
        for repetition in range(repetitions)
        for name, policy, attack in CONTROLS
    ]
    return pd.DataFrame(_parallel(payloads, jobs=int(config["jobs"])))


def _rate(values: pd.Series) -> dict[str, float | int]:
    vector = values.fillna(False).astype(bool)
    successes = int(vector.sum())
    trials = len(vector)
    return {
        "successes": successes,
        "trials": trials,
        "rate": successes / trials,
        "lower95": base._one_sided_lower(successes, trials),  # noqa: SLF001
        "upper95": base._one_sided_upper(successes, trials),  # noqa: SLF001
    }


def _static_marginal_accuracy(frame: pd.DataFrame) -> float:
    columns = [column for column in frame if column.startswith("static_")]
    features = frame[columns].to_numpy(dtype=float)
    labels = frame["policy"].to_numpy()
    groups = frame["repetition"].to_numpy()
    n_splits = min(5, int(np.unique(groups).size))
    if n_splits < 2:
        return float("nan")
    prediction = cross_val_predict(
        make_pipeline(
            StandardScaler(),
            LogisticRegression(
                max_iter=2_000,
            ),
        ),
        features,
        labels,
        groups=groups,
        cv=GroupKFold(n_splits=n_splits),
        method="predict",
    )
    return float(np.mean(prediction == labels))


def _policy_summary(group: pd.DataFrame) -> dict[str, Any]:
    policy = str(group["policy"].iloc[0])
    if policy == "cue_guided":
        target = group["cue_information"]
        nontarget = group[[
            "passthrough_information",
            "residual_entropy",
        ]].max(axis=1)
    elif policy == "pass_through":
        target = group["passthrough_information"]
        nontarget = group[[
            "cue_information",
            "residual_entropy",
        ]].max(axis=1)
    else:
        target = group["residual_entropy"]
        nontarget = group[[
            "cue_information",
            "passthrough_information",
        ]].max(axis=1)
    return {
        "policy": policy,
        "correct": _rate(group["correct_policy"]),
        "junction_f1_minimum": float(group["group_f1"].min()),
        "time_tau_minimum": float(group["time_tau"].min()),
        "view_ari_minimum": float(group["cross_view_ari"].min()),
        "target_information_minimum": float(target.min()),
        "nontarget_information_maximum": float(nontarget.max()),
        "branch_entropy_minimum": float(group["branch_entropy"].min()),
        "x_only_stage_accuracy_maximum": float(
            group["x_only_stage_accuracy"].max()
        ),
        "spacetime_stage_accuracy_minimum": float(
            group["spacetime_stage_accuracy"].min()
        ),
        "goal_path_accuracy_mean": float(
            group["goal_path_accuracy"].mean()
        ),
        "cue_channel_capacity_bits_mean": float(
            group["cue_channel_capacity_bits"].mean()
        ),
        "addressable_leaves_median": float(
            group["addressable_leaves"].median()
        ),
        "effective_leaf_fraction_mean": float(
            group["effective_leaf_fraction"].mean()
        ),
    }


def _decision(
    primary: pd.DataFrame,
    controls: pd.DataFrame,
    config: dict[str, Any],
    *,
    smoke: bool,
) -> dict[str, Any]:
    policies = [
        _policy_summary(group)
        for _, group in primary.groupby("policy", sort=True)
    ]
    control_groups = {
        name: group
        for name, group in controls.groupby("name", sort=True)
    }
    cue_attack = _rate(
        control_groups["cue_shuffle"]["cue_guided_claim"]
    )
    time_attack = _rate(
        control_groups["time_shuffle"]["cue_guided_claim"]
    )
    tangent_refusal = _rate(
        control_groups["tangent_view_shuffle"]["status"]
        == "REFUSE_VIEW_INSTABILITY"
    )
    near_miss_refusal = _rate(
        control_groups["guided_near_miss"]["status"]
        == "REFUSE_NO_JUNCTION"
    )
    pass_cue = control_groups["pass_cue_shuffle"]
    pass_reference = primary[primary["policy"] == "pass_through"]
    pass_cue_delta = abs(
        float(pass_cue["passthrough_information"].mean())
        - float(pass_reference["passthrough_information"].mean())
    )
    static_accuracy = _static_marginal_accuracy(primary)
    summary = {
        "policy_summary": policies,
        "static_marginal_accuracy": static_accuracy,
        "cue_shuffle_guided_claim": cue_attack,
        "time_shuffle_guided_claim": time_attack,
        "tangent_shuffle_refusal": tangent_refusal,
        "near_miss_refusal": near_miss_refusal,
        "near_miss_raw_cue_information_minimum": float(
            control_groups["guided_near_miss"][
                "cue_information"
            ].min()
        ),
        "pass_cue_shuffle_information_delta": pass_cue_delta,
    }
    if smoke:
        checks = {
            "primary": bool(primary["correct_policy"].all()),
            "junctions": bool(primary["group_claim"].all()),
            "time": bool(
                primary["time_tau"].min() >= 0.95
                and (
                    control_groups["time_shuffle"]["status"]
                    == "REFUSE_TIME_ORDER"
                ).all()
            ),
            "controls": bool(
                ~control_groups["cue_shuffle"]["cue_guided_claim"].any()
                and (
                    control_groups["tangent_view_shuffle"]["status"]
                    == "REFUSE_VIEW_INSTABILITY"
                ).all()
                and (
                    control_groups["guided_near_miss"]["status"]
                    == "REFUSE_NO_JUNCTION"
                ).all()
            ),
        }
        return {
            "status": (
                "V8_SPACETIME_JUNCTION_FLOW_V36_SMOKE_PASS"
                if all(checks.values())
                else "V8_SPACETIME_JUNCTION_FLOW_V36_SMOKE_STOP"
            ),
            "checks": checks,
            "summary": summary,
        }

    gates = config["gates"]
    checks = {
        "junction_recovery": all(
            row["junction_f1_minimum"]
            >= gates["minimum_junction_recovery_f1"]
            for row in policies
        ),
        "time_order": all(
            row["time_tau_minimum"] >= gates["minimum_time_tau"]
            for row in policies
        ),
        "tangent_views": all(
            row["view_ari_minimum"]
            >= gates["minimum_tangent_view_ari"]
            for row in policies
        ),
        "world_classification": all(
            row["correct"]["lower95"]
            >= gates["minimum_world_classification_rate"]
            for row in policies
        ),
        "target_information": all(
            row["target_information_minimum"]
            >= gates["minimum_target_information"]
            for row in policies
        ),
        "nontarget_information": all(
            row["nontarget_information_maximum"]
            <= gates["maximum_nontarget_information"]
            for row in policies
        ),
        "branch_entropy": all(
            row["branch_entropy_minimum"]
            >= gates["minimum_branch_entropy"]
            for row in policies
        ),
        "cue_attack": (
            cue_attack["upper95"]
            <= gates["maximum_cue_attack_claim_rate"]
        ),
        "time_attack": (
            time_attack["upper95"]
            <= gates["maximum_time_attack_claim_rate"]
        ),
        "tangent_attack": (
            tangent_refusal["lower95"]
            >= gates["minimum_tangent_attack_refusal_rate"]
        ),
        "near_miss": (
            near_miss_refusal["lower95"]
            >= gates["minimum_near_miss_refusal_rate"]
            and summary["near_miss_raw_cue_information_minimum"]
            >= gates["minimum_target_information"]
        ),
        "x_only_stage": all(
            row["x_only_stage_accuracy_maximum"]
            <= gates["maximum_x_only_stage_accuracy"]
            for row in policies
        ),
        "spacetime_stage": all(
            row["spacetime_stage_accuracy_minimum"]
            >= gates["minimum_spacetime_stage_accuracy"]
            for row in policies
        ),
        "static_marginals": (
            static_accuracy <= gates["maximum_static_marginal_accuracy"]
        ),
        "pass_cue_invariance": pass_cue_delta <= 0.05,
    }
    return {
        "status": (
            "V8_SPACETIME_JUNCTION_FLOW_V36_PASS"
            if all(checks.values())
            else "V8_SPACETIME_JUNCTION_FLOW_V36_STOP"
        ),
        "checks": checks,
        "summary": summary,
        "claim_boundary": config["claim_boundary"],
    }


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 Spacetime Junction-Flow V3.6

Decision: `{decision["status"]}`

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Summary

```json
{json.dumps(decision["summary"], indent=2)}
```

## Boundary

{decision.get("claim_boundary", "Smoke behavior only.")}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_spacetime_junction_flow_v36.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_spacetime_junction_flow/v36",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = base._read_json(args.config)  # noqa: SLF001
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 2
        config["confirmation_repetitions"] = 3
        config["control_repetitions"] = 3
    args.output_dir.mkdir(parents=True, exist_ok=True)

    discovery = _run_primary(
        config,
        stage="discovery",
        repetitions=int(config["discovery_repetitions"]),
    )
    primary = _run_primary(
        config,
        stage="confirmation",
        repetitions=int(config["confirmation_repetitions"]),
    )
    controls = _run_controls(
        config,
        repetitions=int(config["control_repetitions"]),
    )
    decision = _decision(
        primary,
        controls,
        config,
        smoke=args.smoke,
    )
    discovery.to_csv(
        args.output_dir / "discovery_metrics.csv",
        index=False,
    )
    primary.to_csv(
        args.output_dir / "confirmation_primary_metrics.csv",
        index=False,
    )
    controls.to_csv(
        args.output_dir / "confirmation_control_metrics.csv",
        index=False,
    )
    base._write_json(  # noqa: SLF001
        args.output_dir / "decision.json",
        decision,
    )
    base._write_json(  # noqa: SLF001
        args.output_dir / "config_effective.json",
        config,
    )
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
            ROOT / "suica_core/v8_incidence_multiplicity.py",
            ROOT / "suica_core/v8_incidence_incremental.py",
            ROOT / "suica_core/v8_spacetime_junction_flow.py",
            ROOT / "scripts/run_suica_v8_incidence_incremental.py",
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
        "output_dir": str(args.output_dir),
        "checks": decision["checks"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
