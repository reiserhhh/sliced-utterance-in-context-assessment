#!/usr/bin/env python3
"""Run the narrow fresh H4D-R2A iid minority confirmation."""
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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v8_minority_information_frontier_v37h4d_r2 import (  # noqa: E402
    _evaluate,
    _summaries,
)
from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _read,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


DEFAULT_CONFIG = (
    ROOT
    / "configs"
    / "v8_minority_information_frontier_v37h4d_r2a_confirmation.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_minority_information_frontier"
    / "v37h4d_r2a_confirmation_4000rep"
)


def _definitions(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the four frozen W0/signal confirmation cells."""
    definitions: list[dict[str, Any]] = []
    for noise_mode in config["noise_modes"]:
        definitions.append({
            "cell_kind": "w0_confirmation",
            "scaling_arm": "w0",
            "support_scheme": "none",
            "interaction_shape": "none",
            "noise_mode": str(noise_mode),
            "active_test_authors": 0,
            "repetitions": int(
                config["w0_confirmation_repetitions"]
            ),
        })
        definitions.append({
            "cell_kind": "signal_confirmation",
            "scaling_arm": str(config["scaling_arm"]),
            "support_scheme": str(config["support_scheme"]),
            "interaction_shape": str(config["interaction_shape"]),
            "noise_mode": str(noise_mode),
            "active_test_authors": int(
                config["confirmation_active_test_authors"]
            ),
            "repetitions": int(config["confirmation_repetitions"]),
        })
    return definitions


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_lock(config: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for relative, expected in config["frozen_source_sha256"].items():
        observed = _sha256(ROOT / relative)
        rows.append({
            "path": relative,
            "expected_sha256": str(expected),
            "observed_sha256": observed,
            "match": observed == str(expected),
        })
    return {
        "pass": bool(all(row["match"] for row in rows)),
        "files": rows,
    }


def _worker(
    payload: tuple[
        dict[str, Any],
        dict[str, Any],
        int,
        int,
        int,
        int,
    ],
) -> dict[str, Any]:
    config, definition, repetition, world_seed, plant_seed, diagnostic_seed = (
        payload
    )
    return _evaluate(
        definition=definition,
        repetition=repetition,
        world_seed=world_seed,
        plant_seed=plant_seed,
        diagnostic_seed=diagnostic_seed,
        config=config,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read(args.config)
    config["_active_permutations"] = int(config["permutations"])
    source_lock = _source_lock(config)
    definitions = _definitions(config)
    tasks = [
        (definition, repetition)
        for definition in definitions
        for repetition in range(int(definition["repetitions"]))
    ]
    streams = np.random.SeedSequence(
        int(config["confirmation_seed"])
    ).spawn(3 * len(tasks))
    seeds = [
        int(stream.generate_state(1, dtype=np.uint64)[0])
        for stream in streams
    ]
    payloads = [
        (
            config,
            definition,
            repetition,
            seeds[3 * index],
            seeds[3 * index + 1],
            seeds[3 * index + 2],
        )
        for index, (definition, repetition) in enumerate(tasks)
    ]
    if int(config["jobs"]) == 1:
        rows = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            rows = list(executor.map(_worker, payloads, chunksize=1))
    cells = pd.DataFrame(rows)
    summary, slopes, _ = _summaries(cells, config={
        **config,
        "discovery_target_power": 0.93,
        "active_test_author_grid": [
            int(config["confirmation_active_test_authors"])
        ],
        "scaling_arms": [str(config["scaling_arm"])],
        "main_interaction_shape": str(config["interaction_shape"]),
        "noise_modes": list(config["noise_modes"]),
    })

    w0 = summary[summary["scaling_arm"] == "w0"]
    signal = summary[
        (summary["scaling_arm"] == str(config["scaling_arm"]))
        & (
            summary["support_scheme"]
            == str(config["support_scheme"])
        )
        & (
            summary["interaction_shape"]
            == str(config["interaction_shape"])
        )
    ]
    integrity = {
        "source_lock": bool(source_lock["pass"]),
        "row_count": bool(len(cells) == len(tasks) == 4000),
        "seed_uniqueness": bool(len(seeds) == len(set(seeds))),
        "numeric_integrity": bool(
            np.isfinite(
                cells[[
                    "crc",
                    "cross_low_rank_ratio",
                    "hc",
                    "information_budget_residual",
                    "centering_retention_ratio",
                    "centering_leakage_ratio",
                ]].to_numpy(dtype=float)
            ).all()
        ),
        "projection_compatibility": bool(
            cells[
                "projection_grand_mean_compatibility_error"
            ].max()
            <= float(
                config["gates"][
                    "maximum_projection_compatibility_error"
                ]
            )
        ),
    }
    gates = {
        "w0_calibration": bool(
            len(w0) == len(config["noise_modes"])
            and w0["detection_upper"].max()
            < float(
                config["gates"][
                    "maximum_w0_false_refusal_upper"
                ]
            )
        ),
        "iid_m8_power": bool(
            len(signal) == len(config["noise_modes"])
            and signal["crc_or_hc_detection_lower"].min()
            > float(
                config["gates"][
                    "minimum_confirmation_power_lower"
                ]
            )
        ),
    }
    checks = {**integrity, **gates}
    if not all(integrity.values()):
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2A_"
            "STOP_INTEGRITY"
        )
    elif gates["w0_calibration"] and gates["iid_m8_power"]:
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2A_"
            "PASS_IID_FIXED_M8"
        )
    elif not gates["w0_calibration"]:
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2A_"
            "STOP_W0_CALIBRATION"
        )
    else:
        status = (
            "V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2A_"
            "REFUTED_IID_FIXED_M8"
        )
    decision = {
        "status": status,
        "checks": checks,
        "source_lock": source_lock,
        "row_count": int(len(cells)),
        "seed_count": int(len(seeds)),
        "unique_seed_count": int(len(set(seeds))),
        "confirmed_scope": {
            "scaling_arm": str(config["scaling_arm"]),
            "support_scheme": str(config["support_scheme"]),
            "interaction_shape": str(config["interaction_shape"]),
            "active_test_authors": int(
                config["confirmation_active_test_authors"]
            ),
        },
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cells.to_csv(args.output_dir / "cell_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "cell_summary.csv", index=False)
    slopes.to_csv(args.output_dir / "information_slopes.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "seed_count": len(seeds),
        "unique_seed_count": len(set(seeds)),
        "all_unique": len(seeds) == len(set(seeds)),
    })
    (args.output_dir / "report.md").write_text(
        "# H4D-R2A Narrow Iid Confirmation\n\n"
        f"Decision: `{status}`\n\n"
        "This confirmation is restricted to active-SNR, fixed-support, "
        "iid-block, m=8. It does not confirm a cross-geometry scalar "
        "information threshold.\n",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_reference_measure_frontier.py",
            ROOT / "suica_core/v8_minority_information_frontier.py",
            ROOT
            / "scripts"
            / "run_suica_v8_minority_information_frontier_v37h4d_r2.py",
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
        "status": status,
        "checks": checks,
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
