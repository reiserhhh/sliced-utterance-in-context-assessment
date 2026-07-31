#!/usr/bin/env python3
"""Evaluate the frozen M4-C.3.5-R2C RCCA/B0 routing policy."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.aggregate_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _validate,
)
from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _cluster_lcb,
    _cluster_ratio_lcb,
    _cluster_ucb,
    _load,
    _wilson_upper,
)
from suica_core.m4_abstention_routing import (  # noqa: E402
    add_frozen_policy_arm,
    verify_frozen_policy_identity,
)
from suica_core.m4_response_safe_chart_bundle import (  # noqa: E402
    file_sha256,
    runtime_fingerprint,
    verify_source_hash_manifest,
)


def _coerce_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    values = frame.copy()
    categories = {
        "world",
        "world_type",
        "view",
        "arm",
        "rcca_refused",
        "rcca_refusal_reasons",
    }
    for column in values.columns:
        if column not in categories:
            values[column] = pd.to_numeric(values[column], errors="raise")
    values["rcca_refused"] = (
        values["rcca_refused"].astype(str).str.lower().eq("true")
    )
    return values


def _paired_policy_frame(
    metrics: pd.DataFrame,
    *,
    world_type: str,
) -> pd.DataFrame:
    frame = metrics[
        (metrics["view"] == "test")
        & (metrics["world_type"] == world_type)
    ]
    keys = ["repetition", "world"]
    geometry = frame.pivot(index=keys, columns="arm", values="geometry")
    loss = frame.pivot(
        index=keys,
        columns="arm",
        values="comparable_hazard_loss",
    )
    oracle_swap = frame.groupby(keys)["oracle_swap_geometry"].first()
    output = pd.DataFrame(index=geometry.index)
    for arm in ("B0", "R", "Oest", "Pi"):
        output[f"geometry_{arm}"] = geometry[arm]
        output[f"loss_{arm}"] = loss[arm]
    output["oracle_swap_geometry"] = oracle_swap
    output["headroom"] = oracle_swap - output["geometry_B0"]
    output["gain_policy"] = output["geometry_Pi"] - output["geometry_B0"]
    output["gain_forced_R"] = output["geometry_R"] - output["geometry_B0"]
    output["routing_gain_over_forced_R"] = (
        output["geometry_Pi"] - output["geometry_R"]
    )
    output["gain_oracle_estimator"] = (
        output["geometry_Oest"] - output["geometry_B0"]
    )
    output["policy_oracle_fidelity"] = (
        output["geometry_Pi"] - output["geometry_Oest"]
    )
    return output.reset_index()


def _decision(
    metrics: pd.DataFrame,
    policy_cells: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> dict[str, Any]:
    main = _paired_policy_frame(metrics, world_type="main")
    null = _paired_policy_frame(metrics, world_type="null")
    main = main.merge(
        policy_cells,
        on=["repetition", "world"],
        validate="one_to_one",
    )
    null = null.merge(
        policy_cells,
        on=["repetition", "world"],
        validate="one_to_one",
    )
    eligible = main[main["stratum"].eq("eligible")]
    sentinel = main[main["stratum"].eq("sentinel")]
    boundary = main[main["stratum"].eq("boundary")]
    seed = int(config["policy_bootstrap_seed"])
    repetitions = int(config["policy_bootstrap_repetitions"])
    by_repetition = eligible.groupby(
        "repetition",
        sort=True,
    ).mean(numeric_only=True)
    gain = float(eligible["gain_policy"].mean())
    headroom = float(eligible["headroom"].mean())
    oracle_gain = float(eligible["gain_oracle_estimator"].mean())
    recovery = gain / headroom if headroom > 0 else float("nan")
    efficiency = gain / oracle_gain if oracle_gain > 0 else float("nan")
    recovery_lcb, recovery_valid = _cluster_ratio_lcb(
        by_repetition["gain_policy"].to_numpy(),
        by_repetition["headroom"].to_numpy(),
        seed=seed + 1,
        repetitions=repetitions,
    )
    efficiency_lcb, efficiency_valid = _cluster_ratio_lcb(
        by_repetition["gain_policy"].to_numpy(),
        by_repetition["gain_oracle_estimator"].to_numpy(),
        seed=seed + 2,
        repetitions=repetitions,
    )
    eligible_worlds = {}
    for index, (world, values) in enumerate(
        eligible.groupby("world", sort=True)
    ):
        repeated = values.groupby(
            "repetition",
            sort=True,
        ).mean(numeric_only=True)
        ratio_lcb, valid = _cluster_ratio_lcb(
            repeated["gain_policy"].to_numpy(),
            repeated["headroom"].to_numpy(),
            seed=seed + 100 + index,
            repetitions=repetitions,
        )
        eligible_worlds[str(world)] = {
            "policy_gain": float(values["gain_policy"].mean()),
            "policy_gain_lcb": _cluster_lcb(
                repeated["gain_policy"].to_numpy(),
                seed=seed + 200 + index,
                repetitions=repetitions,
            ),
            "headroom_lcb": _cluster_lcb(
                repeated["headroom"].to_numpy(),
                seed=seed + 300 + index,
                repetitions=repetitions,
            ),
            "recovery_lcb": ratio_lcb,
            "ratio_valid_bootstrap_rate": valid,
            "positive_repetitions": int(
                np.sum(repeated["gain_policy"] > 0.0)
            ),
            "acceptance_rate": float(values["accepted"].mean()),
        }
    sentinel_repeated = sentinel.groupby(
        "repetition",
        sort=True,
    )["gain_policy"].mean().to_numpy()
    boundary_repeated = boundary.groupby(
        "repetition",
        sort=True,
    )["policy_oracle_fidelity"].mean().to_numpy()
    null_false = (
        null["gain_policy"]
        >= config["policy_targets"]["null_gain_threshold"]
    )
    accepted = eligible[eligible["accepted"].astype(bool)]
    refused = eligible[~eligible["accepted"].astype(bool)]
    hazard = (
        main.groupby("repetition", sort=True)["loss_Pi"].mean()
        / np.maximum(
            main.groupby("repetition", sort=True)["loss_B0"].mean(),
            1e-12,
        )
        - 1.0
    )
    acceptance = (
        pd.concat([main, null], ignore_index=True)
        .groupby("stratum", sort=True)["accepted"]
        .mean()
        .to_dict()
    )
    diagnostics = {
        "policy_gain": gain,
        "policy_gain_lcb": _cluster_lcb(
            by_repetition["gain_policy"].to_numpy(),
            seed=seed,
            repetitions=repetitions,
        ),
        "policy_recovery": recovery,
        "policy_recovery_lcb": recovery_lcb,
        "policy_recovery_valid_rate": recovery_valid,
        "policy_accessible_efficiency": efficiency,
        "policy_accessible_efficiency_lcb": efficiency_lcb,
        "policy_efficiency_valid_rate": efficiency_valid,
        "policy_oracle_noninferiority_lcb": _cluster_lcb(
            (
                by_repetition["gain_policy"]
                - by_repetition["gain_oracle_estimator"]
            ).to_numpy(),
            seed=seed + 3,
            repetitions=repetitions,
        ),
        "positive_repetitions": int(
            np.sum(by_repetition["gain_policy"] > 0.0)
        ),
        "eligible_worlds": eligible_worlds,
        "history_policy_gain_lcb": _cluster_lcb(
            sentinel_repeated,
            seed=seed + 4,
            repetitions=repetitions,
        ),
        "boundary_policy_oracle_fidelity_lcb": _cluster_lcb(
            boundary_repeated,
            seed=seed + 5,
            repetitions=repetitions,
        ),
        "hazard_relative_degradation_ucb": _cluster_ucb(
            hazard.to_numpy(),
            seed=seed + 6,
            repetitions=repetitions,
        ),
        "null_false_successes": int(np.sum(null_false)),
        "null_trials": int(len(null_false)),
        "null_false_success_wilson_upper": _wilson_upper(
            int(np.sum(null_false)),
            int(len(null_false)),
        ),
        "acceptance_rate_by_stratum": {
            str(key): float(value)
            for key, value in acceptance.items()
        },
        "main_acceptance_rate": float(main["accepted"].mean()),
        "eligible_acceptance_rate": float(eligible["accepted"].mean()),
        "eligible_accepted_cells": int(eligible["accepted"].sum()),
        "eligible_refused_cells": int((~eligible["accepted"]).sum()),
        "forced_r_gain": float(eligible["gain_forced_R"].mean()),
        "routing_gain_over_forced_r": float(
            eligible["routing_gain_over_forced_R"].mean()
        ),
        "accepted_stratum_forced_gain": (
            float(accepted["gain_forced_R"].mean())
            if len(accepted)
            else float("nan")
        ),
        "refused_stratum_forced_gain": (
            float(refused["gain_forced_R"].mean())
            if len(refused)
            else float("nan")
        ),
        "refused_cells": [
            {
                "repetition": int(row.repetition),
                "world": str(row.world),
                "stratum": str(row.stratum),
                "minimum_coverage": float(row.minimum_coverage),
                "minimum_margin": float(row.minimum_margin),
                "refusal_reasons": list(row.refusal_reasons),
            }
            for row in pd.concat([main, null], ignore_index=True)
            .loc[lambda frame: ~frame["accepted"].astype(bool)]
            .itertuples()
        ],
        "minimum_coverage": float(
            policy_cells["minimum_coverage"].min()
        ),
        "minimum_margin": float(policy_cells["minimum_margin"].min()),
        "maximum_basis_replay_error": float(
            policy_cells["basis_replay_error"].max()
        ),
    }
    targets = config["policy_targets"]
    candidate_checks = {
        "policy_gain": (
            diagnostics["policy_gain"] >= targets["minimum_policy_gain"]
            and diagnostics["policy_gain_lcb"] > 0.0
        ),
        "policy_recovery": (
            diagnostics["policy_recovery"]
            >= targets["minimum_policy_recovery"]
            and diagnostics["policy_recovery_lcb"]
            >= targets["minimum_policy_recovery_lcb"]
        ),
        "policy_efficiency": (
            diagnostics["policy_accessible_efficiency"]
            >= targets["minimum_policy_efficiency"]
            and diagnostics["policy_accessible_efficiency_lcb"]
            >= targets["minimum_policy_efficiency_lcb"]
            and diagnostics["policy_oracle_noninferiority_lcb"]
            >= -targets["maximum_oracle_noninferiority_margin"]
        ),
        "history_safety": (
            diagnostics["history_policy_gain_lcb"]
            >= -targets["maximum_history_degradation"]
        ),
        "boundary_fidelity": (
            diagnostics["boundary_policy_oracle_fidelity_lcb"]
            >= -targets["maximum_boundary_oracle_degradation"]
        ),
        "hazard_safety": (
            diagnostics["hazard_relative_degradation_ucb"]
            <= targets["maximum_hazard_relative_degradation"]
        ),
        "null_specificity": (
            diagnostics["null_false_success_wilson_upper"]
            <= targets["maximum_null_false_success_wilson_upper"]
        ),
    }
    integrity = diagnostics["maximum_basis_replay_error"] <= 1e-12
    decision = (
        "M4_C35_R2C_DEVELOPMENT_COMPLETE"
        if integrity
        else "M4_C35_R2C_INVALID_POLICY_REPLAY"
    )
    return {
        "estimand_id": config["policy_estimand_id"],
        "phase": "development",
        "decision": decision,
        "integrity_passed": integrity,
        "candidate_checks_not_confirmation": candidate_checks,
        "diagnostics": diagnostics,
        "confirmation_budget_status": "NOT_REGISTERED",
        "claim_boundary": (
            "Fresh-seed finite-synthetic R2C development only. This run "
            "characterizes a pre-response RCCA/B0 fallback policy and may "
            "design, but cannot confirm, an external abstention budget. It "
            "licenses no natural-text, personality, clinical, or M4-D claim."
        ),
    }


def _report(decision: dict[str, Any]) -> str:
    checks = "\n".join(
        f"- {'PASS' if passed else 'FAIL'}: `{name}`"
        for name, passed in decision[
            "candidate_checks_not_confirmation"
        ].items()
    )
    diagnostics = "\n".join(
        f"- `{name}`: {json.dumps(value, sort_keys=True)}"
        for name, value in decision["diagnostics"].items()
    )
    return f"""# SUICA M4-C.3.5-R2C Abstention-Aware Policy Development

## Decision

`{decision["decision"]}`

The frozen policy uses RCCA (`R`) only when the pre-response applicability
check accepts; otherwise it uses the old chart (`B0`). The primary development
estimand is full-population policy value, not accepted-stratum performance.

## Diagnostics

{diagnostics}

## Candidate gates (not confirmation)

{checks}

No abstention budget is registered in this development run. These checks may
design a fresh confirmation but cannot themselves produce GO.

## Boundary

{decision["claim_boundary"]}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--raw-output-directory", type=Path, required=True)
    parser.add_argument("--policy-manifest", type=Path, required=True)
    parser.add_argument("--expected-policy-manifest-sha256", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--report-path", type=Path, required=True)
    args = parser.parse_args()
    config = _load(args.config)
    policy_path = args.policy_manifest
    if not policy_path.is_absolute():
        policy_path = ROOT / policy_path
    if file_sha256(policy_path) != args.expected_policy_manifest_sha256:
        raise ValueError("policy manifest does not match the frozen seal")
    policy = _load(policy_path)
    if policy["config_sha256"] != file_sha256(args.config):
        raise ValueError("config changed after policy sealing")
    verify_source_hash_manifest(ROOT, policy["source_sha256"])
    if policy["runtime"] != runtime_fingerprint():
        raise ValueError("runtime changed after policy sealing")
    if policy.get("policy_protocol_path") is not None:
        protocol = ROOT / policy["policy_protocol_path"]
        if policy["policy_protocol_sha256"] != file_sha256(protocol):
            raise ValueError("policy protocol changed after sealing")

    raw = args.raw_output_directory
    if not raw.is_absolute():
        raw = ROOT / raw
    metrics = _coerce_metrics(
        pd.read_csv(raw / "metrics.csv", keep_default_na=False)
    )
    controls = pd.read_csv(raw / "controls.csv", keep_default_na=False)
    controls["repetition"] = pd.to_numeric(controls["repetition"])
    controls["value"] = pd.to_numeric(controls["value"])
    controls["passed"] = (
        controls["passed"].astype(str).str.lower().eq("true")
    )
    _validate(metrics, controls, config=config)
    policy_cells = pd.DataFrame(policy["cells"])
    identity_error = verify_frozen_policy_identity(
        metrics,
        policy_cells,
        tolerance=0.0,
    )
    routed = add_frozen_policy_arm(metrics, policy_cells)
    decision = _decision(routed, policy_cells, config=config)
    decision["diagnostics"]["maximum_policy_identity_error"] = identity_error

    output = args.output_directory
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)
    routed.to_csv(output / "metrics_with_policy.csv", index=False)
    policy_cells.to_csv(output / "policy_cells.csv", index=False)
    controls.to_csv(output / "controls.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = args.report_path
    if not report.is_absolute():
        report = ROOT / report
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
