#!/usr/bin/env python3
"""Run the V3.7A anonymous author-routing operator experiment."""
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
    analyze_author_routing_world,
    rank_lambda_cv_losses,
    simulate_author_routing_world,
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=True)
        + "\n",
        encoding="utf-8",
    )


def _spec(
    config: dict[str, Any],
    scenario: dict[str, Any] | None = None,
) -> AuthorRoutingSpec:
    scenario = scenario or {}
    return AuthorRoutingSpec(
        branches=int(config["branches"]),
        groups=int(config["groups"]),
        authors=int(config["authors"]),
        discovery_contexts=int(config["discovery_contexts"]),
        confirmation_contexts=int(config["confirmation_contexts"]),
        extrapolation_contexts=int(config["extrapolation_contexts"]),
        sessions=int(config["sessions"]),
        events_per_context_session=int(
            scenario.get("events", config["events_per_context_session"])
        ),
        context_dimensions=int(config["context_dimensions"]),
        author_rank=int(
            scenario.get("author_rank", config["author_rank"])
        ),
        group_rank=int(config["group_rank"]),
        context_rank=int(config["context_rank"]),
        session_rank=int(config["session_rank"]),
        shared_rms=float(config["shared_rms"]),
        context_rms=float(config["context_rms"]),
        group_rms=float(config["group_rms"]),
        author_rms=float(config["author_rms"]),
        session_rms=float(config["session_rms"]),
        minimum_marginal_probability=float(
            config["minimum_marginal_probability"]
        ),
        maximum_marginal_probability=float(
            config["maximum_marginal_probability"]
        ),
        minimum_normalized_entropy=float(
            config["minimum_normalized_entropy"]
        ),
    )


def _seed(
    config: dict[str, Any],
    *,
    stage: str,
    scenario_name: str,
    repetition: int,
) -> int:
    scenarios = [
        str(row["name"]) for row in config["scenarios"]
    ]
    return (
        int(config["seed"])
        + (0 if stage == "discovery" else 50_000_000)
        + 1_000_000 * scenarios.index(scenario_name)
        + repetition
    )


def _lambda_worker(
    payload: tuple[dict[str, Any], int],
) -> list[dict[str, Any]]:
    config, repetition = payload
    scenario = config["scenarios"][0]
    world = str(scenario["world"])
    seed = _seed(
        config,
        stage="discovery",
        scenario_name=str(scenario["name"]),
        repetition=repetition,
    )
    sample = simulate_author_routing_world(
        seed=seed,
        world=world,
        spec=_spec(config, scenario),
    )
    losses = rank_lambda_cv_losses(
        sample,
        config["rank_candidates"],
        config["lambda_candidates"],
        seed=seed,
    )
    return [
        {
            "stage": "discovery",
            "scenario": str(scenario["name"]),
            "world": world,
            "repetition": repetition,
            "seed": seed,
            "rank": rank,
            "lambda_author": candidate,
            "heldout_log_loss": loss,
        }
        for (rank, candidate), loss in sorted(losses.items())
    ]


def _confirmation_worker(
    payload: tuple[
        dict[str, Any],
        dict[str, Any],
        int,
        float,
        int,
    ],
) -> dict[str, Any]:
    config, scenario, repetition, selected_lambda, selected_rank = payload
    world = str(scenario["world"])
    scenario_name = str(scenario["name"])
    seed = _seed(
        config,
        stage="confirmation",
        scenario_name=scenario_name,
        repetition=repetition,
    )
    sample = simulate_author_routing_world(
        seed=seed,
        world=world,
        spec=_spec(config, scenario),
    )
    estimator_rank = (
        _spec(config, scenario).cells
        * (_spec(config, scenario).branches - 1)
        if scenario["estimator"] == "full_rank"
        else selected_rank
    )
    result = analyze_author_routing_world(
        sample,
        selected_lambda=selected_lambda,
        selected_rank=estimator_rank,
        denoiser_seed=seed + 701,
        claim_thresholds=config["claim_thresholds"],
    )
    row: dict[str, Any] = {
        "stage": "confirmation",
        "scenario": scenario_name,
        "world": world,
        "repetition": repetition,
        "seed": seed,
    }
    for key, value in result.items():
        if isinstance(value, dict):
            row[key] = json.dumps(
                value,
                separators=(",", ":"),
                allow_nan=True,
            )
        else:
            row[key] = value
    return row


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
    sampled = rng.choice(vector, size=(draws, len(vector)), replace=True)
    means = sampled.mean(axis=1)
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
    if trials == 0:
        return {
            "successes": 0,
            "trials": 0,
            "rate": float("nan"),
            "lower95": float("nan"),
            "upper95": float("nan"),
        }
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
        "rate": successes / trials,
        "lower95": lower,
        "upper95": upper,
    }


SUMMARY_METRICS = (
    "truth_correlation",
    "probability_rmse",
    "split_session_reliability",
    "unseen_context_reliability",
    "same_author_auc",
    "within_group_auc",
    "top1",
    "within_group_top1",
    "log_loss_gain",
    "ece",
    "operator_interval_coverage",
    "maximum_variance_share_error",
    "subspace_score",
    "operator_hessian_condition_number",
    "median_operator_ci_width",
)


def _scenario_summary(
    frame: pd.DataFrame,
    *,
    seed: int,
) -> dict[str, Any]:
    scenario = str(frame["scenario"].iloc[0])
    summary: dict[str, Any] = {
        "scenario": scenario,
        "world": str(frame["world"].iloc[0]),
        "author_claim": _rate(frame["author_claim"]),
        "refusal": _rate(frame["status"] == "REFUSE_NONOVERLAP"),
        "numeric_output": _rate(frame["numeric_output"]),
    }
    for offset, metric in enumerate(SUMMARY_METRICS):
        if metric in frame:
            summary[metric] = _mean_interval(
                frame[metric],
                seed=seed + offset,
            )
    if "probability_audit_pass" in frame:
        summary["probability_audit_pass"] = _rate(
            frame["probability_audit_pass"]
        )
    return summary


def _decision(
    confirmation: pd.DataFrame,
    *,
    config: dict[str, Any],
    selected_lambda: float,
    selected_rank: int,
    smoke: bool,
) -> dict[str, Any]:
    summaries = {
        scenario: _scenario_summary(
            group,
            seed=int(config["seed"]) + 100 * index,
        )
        for index, (scenario, group) in enumerate(
            confirmation.groupby("scenario", sort=False)
        )
    }
    stable = summaries["stable_author_lr6"]
    if smoke:
        checks = {
            "stable_numeric": (
                stable["numeric_output"]["rate"] == 1.0
            ),
            "stable_direction": (
                stable["within_group_auc"]["mean"] > 0.75
                and stable["log_loss_gain"]["mean"] > 0.0
                and stable["truth_correlation"]["mean"] > 0.60
            ),
            "controls_no_claim": all(
                summaries[world]["author_claim"]["successes"] == 0
                for world in (
                    "context_only",
                    "group_only",
                    "session_unstable",
                    "opportunity_only",
                    "cue_leakage",
                    "random",
                )
            ),
            "nonoverlap_refuses": (
                summaries["opportunity_nonoverlap"]["refusal"]["rate"]
                == 1.0
            ),
        }
        return {
            "status": (
                "V8_AUTHOR_ROUTING_OPERATOR_V37A_SMOKE_PASS"
                if all(checks.values())
                else "V8_AUTHOR_ROUTING_OPERATOR_V37A_SMOKE_STOP"
            ),
            "selected_lambda": selected_lambda,
            "selected_rank": selected_rank,
            "checks": checks,
            "worlds": summaries,
            "claim_boundary": "Smoke behavior only.",
        }

    gates = config["gates"]
    controls = (
        "context_only",
        "group_only",
        "session_unstable",
        "opportunity_only",
        "cue_leakage",
        "random",
    )
    checks = {
        "truth_correlation": (
            stable["truth_correlation"]["lower95"]
            >= gates["minimum_truth_correlation"]
        ),
        "probability_rmse": (
            stable["probability_rmse"]["upper95"]
            <= gates["maximum_probability_rmse"]
        ),
        "split_session_reliability": (
            stable["split_session_reliability"]["lower95"]
            >= gates["minimum_split_session_reliability"]
        ),
        "unseen_context_reliability": (
            stable["unseen_context_reliability"]["lower95"]
            >= gates["minimum_unseen_context_reliability"]
        ),
        "same_author_auc": (
            stable["same_author_auc"]["lower95"]
            >= gates["minimum_same_author_auc"]
        ),
        "top1": (
            stable["top1"]["lower95"]
            >= gates["minimum_top1_retrieval"]
        ),
        "within_group_top1": (
            stable["within_group_top1"]["lower95"]
            >= gates["minimum_within_group_top1"]
        ),
        "log_loss_gain": (
            stable["log_loss_gain"]["lower95"]
            >= gates["minimum_log_loss_gain"]
        ),
        "calibration": (
            stable["ece"]["upper95"] <= gates["maximum_ece"]
        ),
        "interval_coverage": (
            stable["operator_interval_coverage"]["mean"]
            >= gates["minimum_ci_coverage"]
            and stable["operator_interval_coverage"]["mean"]
            <= gates["maximum_ci_coverage"]
        ),
        "variance_shares": (
            stable["maximum_variance_share_error"]["upper95"]
            <= gates["maximum_variance_share_error"]
        ),
        "stable_claim_rate": (
            stable["author_claim"]["lower95"]
            >= gates["minimum_stable_claim_rate"]
        ),
        "control_claim_rates": all(
            summaries[world]["author_claim"]["upper95"]
            <= gates["maximum_control_claim_rate"]
            for world in controls
        ),
        "group_only_within_auc": (
            summaries["group_only"]["within_group_auc"]["upper95"]
            <= gates["maximum_group_only_within_auc"]
        ),
        "unstable_reliability": (
            summaries["session_unstable"][
                "split_session_reliability"
            ]["upper95"]
            <= gates["maximum_unstable_reliability"]
        ),
        "nonoverlap_refusal": (
            summaries["opportunity_nonoverlap"]["refusal"]["lower95"]
            >= gates["minimum_nonoverlap_refusal_rate"]
        ),
        "probability_audit": (
            stable["probability_audit_pass"]["rate"] == 1.0
        ),
        "subspace_recovery": (
            stable["subspace_score"]["lower95"]
            >= gates["minimum_subspace_score"]
        ),
        "full_rank_high_budget": (
            summaries["full_rank_high_budget"][
                "split_session_reliability"
            ]["lower95"]
            >= gates["minimum_full_rank_high_budget_reliability"]
        ),
        "full_rank_low_budget_refusal": (
            summaries["full_rank_low_budget"][
                "split_session_reliability"
            ]["upper95"]
            <= gates["maximum_full_rank_low_budget_reliability"]
            and summaries["full_rank_low_budget"][
                "author_claim"
            ]["successes"] == 0
        ),
        "rank_not_boundary": (
            selected_rank in {4, 6, 8}
            and selected_rank != max(config["rank_candidates"])
        ),
        "lambda_not_boundary": (
            selected_lambda != min(config["lambda_candidates"])
            and selected_lambda != max(config["lambda_candidates"])
        ),
    }
    return {
        "status": (
            "V8_AUTHOR_ROUTING_OPERATOR_V37A_PASS"
            if all(checks.values())
            else "V8_AUTHOR_ROUTING_OPERATOR_V37A_STOP"
        ),
        "selected_lambda": selected_lambda,
        "selected_rank": selected_rank,
        "checks": checks,
        "worlds": summaries,
        "claim_boundary": config["claim_boundary"],
    }


def _verify_seal(
    path: Path | None,
    *,
    smoke: bool,
    preseal_power: bool,
) -> dict[str, Any]:
    if smoke:
        return {"status": "SMOKE_UNSEALED"}
    if preseal_power:
        return {"status": "PRESEAL_POWER_UNSEALED"}
    if path is None or not path.exists():
        raise RuntimeError("full confirmation requires --seal with frozen hashes")
    payload = _read_json(path)
    failures = []
    for relative, expected in payload["files"].items():
        candidate = ROOT / relative
        if not candidate.is_file():
            failures.append({"path": relative, "reason": "missing"})
        elif sha256_file(candidate) != expected:
            failures.append({"path": relative, "reason": "sha256_mismatch"})
    if failures:
        raise RuntimeError(f"prospective seal mismatch: {failures}")
    return {
        "status": "PROSPECTIVE_SEAL_PASS",
        "seal": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 Author Routing Operator V3.7A

Decision: `{decision["status"]}`

## Frozen gates

```json
{json.dumps(decision["checks"], ensure_ascii=False, indent=2)}
```

## World summaries

```json
{json.dumps(decision["worlds"], ensure_ascii=False, indent=2, allow_nan=True)}
```

## Claim boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_author_routing_operator_v37a.json",
    )
    parser.add_argument(
        "--seal",
        type=Path,
        default=ROOT / "configs/v8_author_routing_operator_v37a_seal.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_author_routing_operator/v37a",
    )
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--preseal-power", action="store_true")
    args = parser.parse_args()
    config = _read_json(args.config)
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 3
        config["confirmation_repetitions"] = 4
    if args.preseal_power:
        config = json.loads(json.dumps(config))
        config["discovery_repetitions"] = 20
        config["confirmation_repetitions"] = 60
    seal = _verify_seal(
        args.seal,
        smoke=args.smoke,
        preseal_power=args.preseal_power,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)

    lambda_payloads = [
        (config, repetition)
        for repetition in range(int(config["discovery_repetitions"]))
    ]
    nested = _parallel(
        _lambda_worker,
        lambda_payloads,
        jobs=int(config["jobs"]),
    )
    lambda_rows = [row for rows in nested for row in rows]
    lambda_frame = pd.DataFrame(lambda_rows)
    lambda_summary = (
        lambda_frame.groupby(
            ["rank", "lambda_author"],
            as_index=False,
        )[
            "heldout_log_loss"
        ]
        .mean()
        .sort_values(
            ["heldout_log_loss", "rank", "lambda_author"]
        )
    )
    selected_rank = int(lambda_summary.iloc[0]["rank"])
    selected_lambda = float(lambda_summary.iloc[0]["lambda_author"])

    payloads = [
        (
            config,
            scenario,
            repetition,
            selected_lambda,
            selected_rank,
        )
        for scenario in config["scenarios"]
        for repetition in range(int(config["confirmation_repetitions"]))
    ]
    confirmation = pd.DataFrame(
        _parallel(
            _confirmation_worker,
            payloads,
            jobs=int(config["jobs"]),
        )
    )
    decision = _decision(
        confirmation,
        config=config,
        selected_lambda=selected_lambda,
        selected_rank=selected_rank,
        smoke=args.smoke,
    )
    if args.preseal_power:
        decision["status"] = decision["status"].replace(
            "V8_AUTHOR_ROUTING_OPERATOR_V37A_",
            "V8_AUTHOR_ROUTING_OPERATOR_V37A_PRESEAL_POWER_",
        )
    decision["prospective_seal"] = seal
    lambda_frame.to_csv(
        args.output_dir / "discovery_lambda_metrics.csv",
        index=False,
    )
    lambda_summary.to_csv(
        args.output_dir / "discovery_lambda_summary.csv",
        index=False,
    )
    confirmation.to_csv(
        args.output_dir / "confirmation_population_metrics.csv",
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
        "selected_rank": selected_rank,
        "selected_lambda": selected_lambda,
        "output_dir": str(args.output_dir),
        "checks": decision["checks"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
