#!/usr/bin/env python3
"""Run the fresh-root R2G.2A heavy-tail precision extension."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import t


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_hierarchical_society_limit import (  # noqa: E402
    HierarchicalSocietySpec,
    fit_independent_surface,
    fit_local_to_unity_surface,
    local_to_unity_limit,
    simulate_local_to_unity_surface,
)


DEFAULT_CONFIG = (
    ROOT
    / "configs/v8_hierarchical_society_limit_v37h4d_r2g2a.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results/v8_hierarchical_society_limit"
    / "v37h4d_r2g2a_t5_precision_80rep"
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )


def _spec(config: dict[str, Any]) -> HierarchicalSocietySpec:
    values = config["spec"]
    return HierarchicalSocietySpec(
        societies=int(values["societies"]),
        max_groups=int(values["max_groups"]),
        max_authors=int(values["max_authors"]),
        dimensions=int(values["dimensions"]),
        society_energy=float(values["society_energy"]),
        group_energy=float(values["group_energy"]),
        author_energy=float(values["author_energy"]),
        technical_energy=float(values["technical_energy"]),
        private_noise_energy=float(values["private_noise_energy"]),
        score_noise_energy=float(values["score_noise_energy"]),
        score_opportunities=int(values["score_opportunities"]),
        raw_society_loading=float(values["raw_society_loading"]),
        raw_group_loading=float(values["raw_group_loading"]),
        local_to_unity_c=float(values["local_to_unity_c"]),
        student_df=float(values["student_df"]),
    )


def _uint64(sequence: np.random.SeedSequence) -> int:
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def _worker(
    payload: tuple[dict[str, Any], int, int],
) -> dict[str, Any]:
    config, root_index, seed = payload
    spec = _spec(config)
    rows = simulate_local_to_unity_surface(
        seed=seed,
        spec=spec,
        noise_mode=str(config["noise_mode"]),
        group_sizes=config["group_sizes"],
        author_sizes=config["author_sizes"],
    )
    naive = fit_independent_surface(rows)
    corrected = fit_local_to_unity_surface(
        rows,
        c=float(spec.local_to_unity_c),
    )
    q_infinity = local_to_unity_limit(
        float(spec.local_to_unity_c)
    )
    return {
        "root_index": int(root_index),
        "source_seed": int(seed),
        "naive_society": float(naive["society"]),
        "naive_group": float(naive["group"]),
        "naive_author": float(naive["author"]),
        "naive_test_nrmse": float(naive["test"]["nrmse"]),
        "corrected_society": float(corrected["society"]),
        "corrected_group": float(corrected["group"]),
        "corrected_author": float(corrected["author"]),
        "corrected_test_nrmse": float(
            corrected["test"]["nrmse"]
        ),
        "theta_infinity": float(
            corrected["society"]
            + q_infinity * corrected["group"]
        ),
        "q_infinity": float(q_infinity),
    }


def _interval(
    values: np.ndarray,
    *,
    alpha: float,
    family_size: int,
) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    mean = float(array.mean())
    se = float(array.std(ddof=1) / np.sqrt(len(array)))
    critical = float(t.ppf(
        1.0 - alpha / (2.0 * family_size),
        df=len(array) - 1,
    ))
    return {
        "mean": mean,
        "se": se,
        "critical": critical,
        "ci_lo": mean - critical * se,
        "ci_hi": mean + critical * se,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read(args.config)
    repetitions = int(config["repetitions"])
    root = np.random.SeedSequence(int(config["seed"]))
    seeds = [_uint64(child) for child in root.spawn(repetitions)]
    payloads = [
        (config, index, seed)
        for index, seed in enumerate(seeds)
    ]
    if int(config["jobs"]) == 1:
        rows = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            rows = list(executor.map(_worker, payloads, chunksize=1))
    metrics = pd.DataFrame(rows)
    gates = config["gates"]
    alpha = float(gates["simultaneous_alpha"])
    family_size = int(gates["family_size"])
    summary = {
        column: _interval(
            metrics[column].to_numpy(dtype=float),
            alpha=alpha,
            family_size=family_size,
        )
        for column in (
            "naive_society",
            "naive_group",
            "naive_author",
            "naive_test_nrmse",
            "corrected_society",
            "corrected_group",
            "corrected_author",
            "corrected_test_nrmse",
            "theta_infinity",
        )
    }
    spec = _spec(config)
    q_infinity = local_to_unity_limit(
        float(spec.local_to_unity_c)
    )
    truth_theta = float(spec.group_energy) * q_infinity
    margin = float(gates["society_equivalence_margin"])
    checks = {
        "fresh_seed_uniqueness": len(seeds) == len(set(seeds)),
        "corrected_society_equivalent": bool(
            summary["corrected_society"]["ci_lo"] >= -margin
            and summary["corrected_society"]["ci_hi"] <= margin
        ),
        "naive_false_floor_persists": bool(
            summary["naive_society"]["ci_lo"]
            > float(gates["minimum_naive_false_floor"])
        ),
        "group_coefficient_recovered": bool(
            abs(
                summary["corrected_group"]["mean"]
                - float(spec.group_energy)
            ) <= float(gates["coefficient_absolute_error"])
        ),
        "author_coefficient_recovered": bool(
            abs(
                summary["corrected_author"]["mean"]
                - float(spec.author_energy)
            ) <= float(gates["coefficient_absolute_error"])
        ),
        "heldout_prediction_guardrail": bool(
            summary["corrected_test_nrmse"]["mean"]
            <= float(gates["maximum_test_nrmse"])
        ),
        "asymptotic_floor_recovered": bool(
            abs(summary["theta_infinity"]["mean"] - truth_theta)
            <= float(gates["asymptotic_floor_absolute_error"])
        ),
    }
    passed = all(checks.values())
    decision = {
        "status": (
            "V8_R2G2A_PASS_HEAVY_TAIL_PRECISION"
            if passed
            else "V8_R2G2A_REMAINS_INCONCLUSIVE"
        ),
        "scientific_decision": (
            "FRESH_ROOT_EQUIVALENCE_CONFIRMED"
            if passed
            else "FRESH_ROOT_EQUIVALENCE_UNRESOLVED"
        ),
        "created_utc": datetime.now(UTC).isoformat(),
        "root_seed": int(config["seed"]),
        "repetitions": repetitions,
        "old_r2g2_roots_combined": False,
        "checks": checks,
        "summary": summary,
        "truth": {
            "society": 0.0,
            "group": float(spec.group_energy),
            "author": float(spec.author_energy),
            "q_infinity": float(q_infinity),
            "theta_infinity": truth_theta,
        },
        "claim_boundary": str(config["claim_boundary"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.output_dir / "root_metrics.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "root_seed": int(config["seed"]),
        "source_seed_count": len(seeds),
        "unique_source_seed_count": len(set(seeds)),
        "all_source_seeds_unique": len(seeds) == len(set(seeds)),
        "old_r2g2_roots_combined": False,
    })
    (args.output_dir / "report.md").write_text(
        f"""# V8 R2G.2A Heavy-Tail Precision Extension

Decision: `{decision["status"]}`

The original R2G.2 decision remains `PARTIAL_INDEPENDENT_ONLY`.

Corrected society coefficient:
`{summary["corrected_society"]["mean"]:.6f}`
[`{summary["corrected_society"]["ci_lo"]:.6f}`,
`{summary["corrected_society"]["ci_hi"]:.6f}`].

Total asymptotic floor:
`{summary["theta_infinity"]["mean"]:.6f}`
(truth `{truth_theta:.6f}`).

The extension tests whether the explicit society coefficient is practically
zero. It does not test whether the total local-to-unity limit is zero.
""",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_hierarchical_society_limit.py",
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
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
