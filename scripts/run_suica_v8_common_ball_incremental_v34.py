#!/usr/bin/env python3
"""Run the frozen V3.4 common-ball incremental-information experiment."""
from __future__ import annotations

import argparse
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

from scripts import run_suica_v8_incidence_incremental as base  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_common_ball_incremental import (  # noqa: E402
    CommonBallSpec,
    analyze_common_ball_pair,
    simulate_common_ball_pair,
)

METHODS = (
    "persistent_maximal_clique",
    "condition_complete_link",
    "aggregate_component_concurrency_gate",
)
SCENARIOS = (
    "main",
    "both_feasible",
    "both_infeasible",
    "boundary",
    "adjacency_mismatch",
)


def _spec(config: dict[str, Any]) -> CommonBallSpec:
    return CommonBallSpec(
        authors=int(config["authors"]),
        groups=int(config["groups"]),
        conditions=int(config["conditions"]),
        views=int(config["views"]),
        ambient=int(config["ambient"]),
        active_conditions=int(config["active_conditions"]),
        fixed_radius=float(config["fixed_radius"]),
        epsilon_grid=tuple(float(item) for item in config["epsilon_grid"]),
        noise_sd=float(config["noise_sd"]),
        core_persistence_threshold=float(
            config["core_persistence_threshold"]
        ),
        minimum_group_coverage=float(config["minimum_group_coverage"]),
        margin_refusal=float(config["margin_refusal"]),
        enumeration_node_cap=int(config["enumeration_node_cap"]),
        candidate_cap=int(config["candidate_cap"]),
    )


def _scenario_geometry(
    config: dict[str, Any],
    scenario: str,
) -> tuple[str, float, str, float]:
    positive_radius = float(config["positive_shape_radius"])
    negative_radius = float(config["negative_shape_radius"])
    if scenario == "main":
        return "hexagon", positive_radius, "triangle", negative_radius
    if scenario == "both_feasible":
        return "hexagon", positive_radius, "hexagon", positive_radius
    if scenario == "both_infeasible":
        return "triangle", negative_radius, "triangle", negative_radius
    if scenario == "boundary":
        return (
            "hexagon",
            positive_radius,
            "triangle",
            float(config["boundary_shape_radius"]),
        )
    if scenario == "adjacency_mismatch":
        return (
            "hexagon",
            positive_radius,
            "triangle",
            float(config["mismatch_shape_radius"]),
        )
    raise ValueError(f"unsupported scenario: {scenario}")


def _seed(
    config: dict[str, Any],
    *,
    scenario: str,
    repetition: int,
) -> int:
    return (
        int(config["seed"])
        + 10_000_000 * SCENARIOS.index(scenario)
        + repetition
    )


def _worker(
    payload: tuple[dict[str, Any], str, int],
) -> dict[str, Any]:
    config, scenario, repetition = payload
    seed = _seed(config, scenario=scenario, repetition=repetition)
    positive_geometry, positive_radius, negative_geometry, negative_radius = (
        _scenario_geometry(config, scenario)
    )
    spec = _spec(config)
    pair = simulate_common_ball_pair(
        seed=seed,
        spec=spec,
        positive_geometry=positive_geometry,
        positive_shape_radius=positive_radius,
        negative_geometry=negative_geometry,
        negative_shape_radius=negative_radius,
    )
    return {
        "scenario": scenario,
        "seed": seed,
        "repetition": repetition,
        "positive_geometry": positive_geometry,
        "positive_radius": positive_radius,
        "negative_geometry": negative_geometry,
        "negative_radius": negative_radius,
        "result": analyze_common_ball_pair(pair, spec=spec),
    }


def _run_scenario(
    config: dict[str, Any],
    scenario: str,
    *,
    repetitions: int,
) -> list[dict[str, Any]]:
    payloads = [
        (config, scenario, repetition)
        for repetition in range(repetitions)
    ]
    jobs = int(config["jobs"])
    if jobs <= 1:
        return [_worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(_worker, payloads, chunksize=1))


def _estimate_fields(
    row: dict[str, Any],
    estimate: dict[str, Any],
    *,
    prefix: str,
) -> None:
    for key in (
        "status",
        "refused",
        "group_claim",
        "coverage",
        "maximum_passing_size",
        "group_f1",
        "group_ari",
    ):
        row[f"{prefix}_{key}"] = estimate.get(key)
    row[f"{prefix}_selected_groups"] = json.dumps(
        estimate.get("selected_groups", []),
        separators=(",", ":"),
    )
    row[f"{prefix}_passing_groups"] = json.dumps(
        estimate.get("passing_groups", []),
        separators=(",", ":"),
    )


def _flatten(record: dict[str, Any]) -> dict[str, Any]:
    result = record["result"]
    row = {
        key: value
        for key, value in record.items()
        if key != "result"
    }
    row.update({
        "status": result["status"],
        "view_tensor_mismatch_count": result.get(
            "view_tensor_mismatch_count",
            0,
        ),
        "tensor_mismatch_count": result.get(
            "tensor_mismatch_count",
            0,
        ),
        "pairwise_output_match": result.get(
            "pairwise_output_match",
            False,
        ),
        "decision_delta": result.get("decision_delta", np.nan),
    })
    for side in ("positive", "negative"):
        estimate = result.get(f"{side}_meb", {})
        _estimate_fields(row, estimate, prefix=f"{side}_meb")
        for method in METHODS:
            pair_estimate = result.get(
                f"{side}_pairwise",
                {},
            ).get(method, {})
            _estimate_fields(
                row,
                pair_estimate,
                prefix=f"{side}_{method}",
            )
    return row


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


def _main_summary(
    frame: pd.DataFrame,
    *,
    seed: int,
) -> dict[str, Any]:
    delta = pd.to_numeric(frame["decision_delta"], errors="coerce").to_numpy()
    low, high = base._bootstrap_mean_interval(  # noqa: SLF001
        delta,
        seed=seed,
        confidence=0.95,
    )
    pairwise_matches = frame["pairwise_output_match"].fillna(False)
    return {
        "positive_claim": _rate(frame["positive_meb_group_claim"]),
        "negative_claim": _rate(frame["negative_meb_group_claim"]),
        "negative_refusal": _rate(frame["negative_meb_refused"]),
        "decision_delta": {
            "mean": float(np.nanmean(delta)),
            "ci95_low": low,
            "ci95_high": high,
        },
        "view_tensor_mismatch_total": int(
            frame["view_tensor_mismatch_count"].sum()
        ),
        "tensor_mismatch_total": int(
            frame["tensor_mismatch_count"].sum()
        ),
        "pairwise_output_match": _rate(pairwise_matches),
        "positive_f1_median": float(
            frame["positive_meb_group_f1"].median()
        ),
        "positive_ari_median": float(
            frame["positive_meb_group_ari"].median()
        ),
        "positive_maximum_passing_size_median": float(
            frame["positive_meb_maximum_passing_size"].median()
        ),
        "negative_maximum_passing_size_median": float(
            frame["negative_meb_maximum_passing_size"].median()
        ),
    }


def _control_summary(
    frames: dict[str, pd.DataFrame],
) -> dict[str, Any]:
    feasible = frames["both_feasible"]
    infeasible = frames["both_infeasible"]
    boundary = frames["boundary"]
    mismatch = frames["adjacency_mismatch"]
    feasible_agreement = (
        feasible["positive_meb_group_claim"].fillna(False)
        & feasible["negative_meb_group_claim"].fillna(False)
    )
    infeasible_agreement = (
        ~infeasible["positive_meb_group_claim"].fillna(False)
        & ~infeasible["negative_meb_group_claim"].fillna(False)
    )
    boundary_refusal = (
        boundary["negative_meb_status"] == "REFUSE_MARGIN"
    )
    mismatch_stop = (
        mismatch["status"] == "STOP_ADJACENCY_MISMATCH"
    )
    return {
        "both_feasible_agreement": _rate(feasible_agreement),
        "both_infeasible_agreement": _rate(infeasible_agreement),
        "boundary_refusal": _rate(boundary_refusal),
        "adjacency_mismatch_stop": _rate(mismatch_stop),
    }


def _cap_failures(frames: dict[str, pd.DataFrame]) -> int:
    failures = 0
    for frame in frames.values():
        for column in ("positive_meb_status", "negative_meb_status"):
            failures += int(
                frame[column]
                .fillna("")
                .str.contains("CAP", regex=False)
                .sum()
            )
    return failures


def _decision(
    frames: dict[str, pd.DataFrame],
    config: dict[str, Any],
    *,
    smoke: bool,
) -> dict[str, Any]:
    main = _main_summary(
        frames["main"],
        seed=int(config["seed"]) + 90_001,
    )
    controls = _control_summary(frames)
    cap_failures = _cap_failures(frames)
    if smoke:
        checks = {
            "main_tensor_matched": bool(
                main["view_tensor_mismatch_total"] == 0
                and main["tensor_mismatch_total"] == 0
            ),
            "main_pairwise_matched": bool(
                main["pairwise_output_match"]["rate"] == 1.0
            ),
            "main_contrast": bool(
                main["positive_claim"]["rate"] == 1.0
                and main["negative_claim"]["rate"] == 0.0
            ),
            "controls": bool(all(
                item["rate"] == 1.0
                for item in controls.values()
            )),
            "no_caps": cap_failures == 0,
        }
        return {
            "status": (
                "V8_COMMON_BALL_INCREMENTAL_V34_SMOKE_PASS"
                if all(checks.values())
                else "V8_COMMON_BALL_INCREMENTAL_V34_SMOKE_STOP"
            ),
            "checks": checks,
            "main_summary": main,
            "control_summary": controls,
        }

    gates = config["gates"]
    checks = {
        "tensor_matched": bool(
            main["view_tensor_mismatch_total"] == 0
            and main["tensor_mismatch_total"] == 0
        ),
        "pairwise_outputs_matched": bool(
            1.0 - main["pairwise_output_match"]["rate"]
            <= gates["maximum_pairwise_output_mismatch_rate"]
        ),
        "positive_claim": bool(
            main["positive_claim"]["lower95"]
            >= gates["minimum_positive_claim_rate"]
        ),
        "negative_claim": bool(
            main["negative_claim"]["upper95"]
            <= gates["maximum_negative_claim_rate"]
        ),
        "decision_delta": bool(
            main["decision_delta"]["ci95_low"]
            >= gates["minimum_decision_delta"]
        ),
        "both_feasible_control": bool(
            controls["both_feasible_agreement"]["lower95"]
            >= gates["minimum_control_agreement_rate"]
        ),
        "both_infeasible_control": bool(
            controls["both_infeasible_agreement"]["lower95"]
            >= gates["minimum_control_agreement_rate"]
        ),
        "boundary_refusal": bool(
            controls["boundary_refusal"]["lower95"]
            >= gates["minimum_boundary_refusal_rate"]
        ),
        "adjacency_mismatch_stop": bool(
            controls["adjacency_mismatch_stop"]["lower95"]
            >= gates["minimum_mismatch_stop_rate"]
        ),
        "no_caps": cap_failures == 0,
    }
    return {
        "status": (
            "V8_COMMON_BALL_INCREMENTAL_V34_PASS"
            if all(checks.values())
            else "V8_COMMON_BALL_INCREMENTAL_V34_STOP"
        ),
        "checks": checks,
        "main_summary": main,
        "control_summary": controls,
        "cap_failures": cap_failures,
        "claim_boundary": config["claim_boundary"],
    }


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 Common-Ball Incremental V3.4

## Decision

`{decision["status"]}`

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Main paired counterfactual

```json
{json.dumps(decision["main_summary"], indent=2)}
```

## Controls

```json
{json.dumps(decision["control_summary"], indent=2)}
```

## Claim boundary

{decision.get("claim_boundary", "Smoke behavior only.")}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_common_ball_incremental_v34.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_common_ball_incremental/v34",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = base._read_json(args.config)  # noqa: SLF001
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["confirmation_repetitions"] = 2
        config["control_repetitions"] = 2
    args.output_dir.mkdir(parents=True, exist_ok=True)

    frames: dict[str, pd.DataFrame] = {}
    for scenario in SCENARIOS:
        repetitions = (
            int(config["confirmation_repetitions"])
            if scenario == "main"
            else int(config["control_repetitions"])
        )
        records = _run_scenario(
            config,
            scenario,
            repetitions=repetitions,
        )
        frame = pd.DataFrame([_flatten(record) for record in records])
        frames[scenario] = frame
        frame.to_csv(
            args.output_dir / f"{scenario}_metrics.csv",
            index=False,
        )

    decision = _decision(frames, config, smoke=args.smoke)
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
            ROOT / "suica_core/v8_incidence_incremental_v31.py",
            ROOT / "suica_core/v8_incidence_graph_fairness.py",
            ROOT / "suica_core/v8_common_ball_incremental.py",
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
