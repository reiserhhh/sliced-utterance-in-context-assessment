#!/usr/bin/env python3
"""Calibrate the unchanged V3.7H.4 detector on fresh W0 worlds."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import beta, binom

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_misspecification_transport_v37h4 import (  # noqa: E402
    _evaluate_cell,
    _uint64,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


DEFAULT_CONFIG = ROOT / "configs/v8_w0_calibration_v37h4c.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_misspecification_w0_calibration"
    / "v37h4c_calibration"
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_detector_lock(config: dict[str, Any]) -> dict[str, Any]:
    """Verify that calibration uses the exact frozen H.4 detector."""
    lock = config["detector_lock"]
    checks: dict[str, bool] = {}
    config_path = ROOT / str(lock["config_path"])
    checks[str(lock["config_path"])] = (
        _sha256(config_path) == str(lock["config_sha256"])
    )
    for relative, expected in lock["code_sha256"].items():
        checks[str(relative)] = (
            _sha256(ROOT / str(relative)) == str(expected)
        )
    source_manifest = ROOT / str(lock["source_manifest"])
    checks[str(lock["source_manifest"])] = source_manifest.exists()
    detector = _read(config_path)
    checks["permutations"] = (
        int(detector["permutations"]) == int(config["permutations"])
    )
    checks["holm_alpha"] = bool(
        np.isclose(
            float(detector["holm_alpha"]),
            float(config["holm_alpha"]),
        )
    )
    return {
        "all_match": bool(all(checks.values())),
        "checks": checks,
        "detector_config": detector,
    }


def one_sided_exact_bounds(
    successes: int,
    trials: int,
    *,
    tail_alpha: float,
) -> tuple[float, float]:
    """Return exact one-sided lower and upper binomial bounds."""
    lower = (
        0.0
        if successes == 0
        else float(beta.ppf(
            float(tail_alpha),
            successes,
            trials - successes + 1,
        ))
    )
    upper = (
        1.0
        if successes == trials
        else float(beta.ppf(
            1.0 - float(tail_alpha),
            successes + 1,
            trials - successes,
        ))
    )
    return lower, upper


def decision_from_bounds(
    bounds: list[tuple[float, float]],
    *,
    target: float,
) -> str:
    """Apply the frozen three-state calibration decision."""
    if all(upper < float(target) for _, upper in bounds):
        return "CALIBRATED"
    if any(lower >= float(target) for lower, _ in bounds):
        return "MISCALIBRATED"
    return "INCONCLUSIVE"


def count_boundaries(
    trials: int,
    *,
    tail_alpha: float,
    target: float,
) -> tuple[int, int]:
    """Derive the largest pass and smallest fail counts."""
    calibrated = max(
        count
        for count in range(trials + 1)
        if one_sided_exact_bounds(
            count,
            trials,
            tail_alpha=tail_alpha,
        )[1] < target
    )
    miscalibrated = min(
        count
        for count in range(trials + 1)
        if one_sided_exact_bounds(
            count,
            trials,
            tail_alpha=tail_alpha,
        )[0] >= target
    )
    return calibrated, miscalibrated


def power_table(
    trials: int,
    *,
    calibrated_max: int,
    miscalibrated_min: int,
    rates: list[float],
) -> pd.DataFrame:
    """Return exact operating probabilities for frozen count rules."""
    rows = []
    for rate in rates:
        calibrated = float(
            binom.cdf(calibrated_max, trials, float(rate))
        )
        miscalibrated = float(
            binom.sf(miscalibrated_min - 1, trials, float(rate))
        )
        rows.append({
            "true_false_refusal_rate": float(rate),
            "p_calibrated": calibrated,
            "p_inconclusive": float(
                max(0.0, 1.0 - calibrated - miscalibrated)
            ),
            "p_miscalibrated": miscalibrated,
        })
    return pd.DataFrame(rows)


def _worker(
    payload: tuple[
        dict[str, Any],
        int,
        list[tuple[str, int, int]],
    ],
) -> dict[str, Any]:
    detector, repetition, assignments = payload
    rows: list[dict[str, Any]] = []
    seeds: list[int] = []
    for noise_mode, world_seed, diagnostic_seed in assignments:
        cell, _, _, _ = _evaluate_cell(
            repetition=repetition,
            world_name="additive",
            effect_share=0.0,
            noise_mode=noise_mode,
            world_seed=world_seed,
            diagnostic_seed=diagnostic_seed,
            config=detector,
        )
        rows.append(cell)
        seeds.extend([world_seed, diagnostic_seed])
    return {"rows": rows, "seeds": seeds}


def _build_payloads(
    detector: dict[str, Any],
    *,
    seed: int,
    repetitions: int,
    noise_modes: list[str],
) -> list[tuple[dict[str, Any], int, list[tuple[str, int, int]]]]:
    root = np.random.SeedSequence(int(seed))
    children = root.spawn(repetitions * len(noise_modes))
    payloads = []
    index = 0
    for repetition in range(repetitions):
        assignments = []
        for noise_mode in noise_modes:
            pair = children[index].spawn(2)
            index += 1
            assignments.append((
                str(noise_mode),
                _uint64(pair[0]),
                _uint64(pair[1]),
            ))
        payloads.append((detector, repetition, assignments))
    return payloads


def _summarize(
    metrics: pd.DataFrame,
    *,
    tail_alpha: float,
) -> pd.DataFrame:
    rows = []
    for noise_mode, group in metrics.groupby(
        "noise_mode",
        sort=True,
        observed=True,
    ):
        refusals = int(group["model_inadequate"].sum())
        lower, upper = one_sided_exact_bounds(
            refusals,
            len(group),
            tail_alpha=tail_alpha,
        )
        rows.append({
            "noise_mode": str(noise_mode),
            "trials": int(len(group)),
            "false_refusals": refusals,
            "false_refusal_rate": float(refusals / len(group)),
            "simultaneous_lower": lower,
            "simultaneous_upper": upper,
            "crc_holm_trigger_count": int(
                (group["crc_p_holm"] < 0.05).sum()
            ),
            "low_rank_holm_trigger_count": int(
                (group["low_rank_p_holm"] < 0.05).sum()
            ),
            "gain_holm_trigger_count": int(
                (group["gain_p_holm"] < 0.05).sum()
            ),
            "mean_crc": float(group["crc"].mean()),
            "mean_t_gen": float(group["t_gen"].mean()),
        })
    return pd.DataFrame(rows)


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 V3.7H.4C W0 Calibration

Decision: `{decision["status"]}`

## Checks

```json
{json.dumps(decision["checks"], indent=2)}
```

## Calibration

```json
{json.dumps(decision["calibration"], indent=2)}
```

## Boundary

This calibrates only the unchanged synthetic V3.7H.4 detector under the two
registered additive noise generators. It does not validate real-text
calibration, general misspecification awareness, causal localization,
personality interpretation, diagnosis, or clinical use.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--mode",
        choices=["smoke", "calibration"],
        default="calibration",
    )
    args = parser.parse_args()
    config = _read(args.config)
    source_lock = verify_detector_lock(config)
    detector = source_lock.pop("detector_config")
    detector["_active_permutations"] = int(config["permutations"])

    if args.mode == "smoke":
        seed = int(config["smoke_seed"])
        repetitions = int(config["smoke_repetitions_per_noise"])
    else:
        seed = int(config["seed"])
        repetitions = int(config["repetitions_per_noise"])
    noise_modes = [str(value) for value in config["noise_modes"]]
    payloads = _build_payloads(
        detector,
        seed=seed,
        repetitions=repetitions,
        noise_modes=noise_modes,
    )
    if int(config["jobs"]) == 1:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))

    metrics = pd.DataFrame([
        row for part in nested for row in part["rows"]
    ])
    seeds = [seed_value for part in nested for seed_value in part["seeds"]]
    summary = _summarize(
        metrics,
        tail_alpha=float(config["family_tail_alpha"]),
    )
    boundary_trials = int(config["repetitions_per_noise"])
    calibrated_max, miscalibrated_min = count_boundaries(
        boundary_trials,
        tail_alpha=float(config["family_tail_alpha"]),
        target=float(config["target_false_refusal"]),
    )
    frozen_counts_match = (
        calibrated_max == int(config["calibrated_max_count"])
        and miscalibrated_min
        == int(config["miscalibrated_min_count"])
    )
    numeric_columns = [
        "crc",
        "low_rank_ratio",
        "mean_author_mse_gain",
        "t_gen",
        "additive_mse",
        "structured_mse",
        "oracle_mse",
        "operation_gap",
    ]
    checks = {
        "detector_source_lock": bool(source_lock["all_match"]),
        "row_count": bool(
            len(metrics) == repetitions * len(noise_modes)
        ),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
        "numeric_integrity": bool(
            np.isfinite(
                metrics[numeric_columns].to_numpy(dtype=float)
            ).all()
        ),
        "frozen_count_boundaries": bool(frozen_counts_match),
    }
    integrity_pass = bool(all(checks.values()))
    bounds = [
        (
            float(row.simultaneous_lower),
            float(row.simultaneous_upper),
        )
        for row in summary.itertuples(index=False)
    ]
    if not integrity_pass:
        status = (
            "V8_MISSPECIFICATION_W0_CALIBRATION_V37H4C_"
            "STOP_INTEGRITY"
        )
    elif args.mode == "smoke":
        status = (
            "V8_MISSPECIFICATION_W0_CALIBRATION_V37H4C_"
            "SMOKE_COMPLETE"
        )
    else:
        state = decision_from_bounds(
            bounds,
            target=float(config["target_false_refusal"]),
        )
        status = (
            "V8_MISSPECIFICATION_W0_CALIBRATION_V37H4C_"
            f"{state}"
        )

    power = power_table(
        boundary_trials,
        calibrated_max=calibrated_max,
        miscalibrated_min=miscalibrated_min,
        rates=[float(value) for value in config["power_rates"]],
    )
    decision = {
        "status": status,
        "integrity_pass": integrity_pass,
        "checks": checks,
        "calibration": {
            "tail_alpha_per_noise": float(
                config["family_tail_alpha"]
            ),
            "target_false_refusal": float(
                config["target_false_refusal"]
            ),
            "calibrated_max_count": int(calibrated_max),
            "miscalibrated_min_count": int(miscalibrated_min),
            "by_noise": summary.to_dict(orient="records"),
        },
        "row_count": int(len(metrics)),
        "seed_count": int(len(seeds)),
        "unique_seed_count": int(len(set(seeds))),
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(
        args.output_dir / "calibration_metrics.csv",
        index=False,
    )
    summary.to_csv(
        args.output_dir / "calibration_summary.csv",
        index=False,
    )
    metrics[metrics["model_inadequate"]].to_csv(
        args.output_dir / "false_refusal_events.csv",
        index=False,
    )
    power.to_csv(args.output_dir / "power_table.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "detector_source_lock.json", source_lock)
    _write(args.output_dir / "seed_audit.json", {
        "seed_count": len(seeds),
        "unique_seed_count": len(set(seeds)),
        "all_unique": len(seeds) == len(set(seeds)),
    })
    (args.output_dir / "report.md").write_text(
        _report(decision),
        encoding="utf-8",
    )
    lock = config["detector_lock"]
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[ROOT / str(lock["source_manifest"])],
        config_path=args.config,
        code_paths=[
            ROOT / relative
            for relative in lock["code_sha256"]
        ] + [Path(__file__)],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps({
        "status": status,
        "repetitions_per_noise": repetitions,
        "cells": int(len(metrics)),
        "output_dir": str(args.output_dir),
        "checks": checks,
    }, indent=2))
    return 0 if integrity_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
