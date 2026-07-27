#!/usr/bin/env python3
"""Run V3.3 condition-aware pairwise fairness comparators."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_suica_v8_incidence_incremental as base  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_incidence_graph_fairness import (  # noqa: E402
    analyze_condition_pair_baselines,
)
from suica_core.v8_incidence_strong_chain import (  # noqa: E402
    condition_aligned_pair_matrix,
    simulate_strong_chain_pair,
)

METHODS = (
    "persistent_maximal_clique",
    "condition_complete_link",
    "aggregate_component_concurrency_gate",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _worker(
    payload: tuple[dict[str, Any], dict[str, Any], int],
) -> dict[str, Any]:
    config, source, repetition = payload
    seed = (
        int(config["seed"])
        + int(config["seed_offset"])
        + repetition
    )
    spec = base._spec(source)  # noqa: SLF001
    pair = simulate_strong_chain_pair(
        seed=seed,
        spec=spec,
        private_excursion_radius=float(
            source["private_excursion_radius"]
        ),
        anchor_scale=float(source["anchor_scale"]),
    )
    positive = analyze_condition_pair_baselines(
        pair["positive_views"],
        pair["labels"],
        spec=spec,
        node_cap=int(config["node_cap"]),
        candidate_cap=int(config["candidate_cap"]),
    )
    chain = analyze_condition_pair_baselines(
        pair["negative_views"],
        pair["labels"],
        spec=spec,
        node_cap=int(config["node_cap"]),
        candidate_cap=int(config["candidate_cap"]),
    )
    positive_aggregate = condition_aligned_pair_matrix(
        pair["positive_views"],
        spec=spec,
    )
    chain_aggregate = condition_aligned_pair_matrix(
        pair["negative_views"],
        spec=spec,
    )
    return {
        "seed": seed,
        "repetition": repetition,
        "aggregate_pair_mae": float(
            abs(positive_aggregate - chain_aggregate).mean()
        ),
        "positive": positive,
        "chain": chain,
    }


def _run(
    config: dict[str, Any],
    source: dict[str, Any],
) -> list[dict[str, Any]]:
    repetitions = int(config["confirmation_repetitions"])
    payloads = [
        (config, source, repetition)
        for repetition in range(repetitions)
    ]
    jobs = int(config["jobs"])
    if jobs <= 1:
        return [_worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(_worker, payloads, chunksize=1))


def _row(result: dict[str, Any]) -> dict[str, Any]:
    output = {
        "seed": result["seed"],
        "repetition": result["repetition"],
        "aggregate_pair_mae": result["aggregate_pair_mae"],
    }
    for method in METHODS:
        for side in ("positive", "chain"):
            estimate = result[side][method]
            for key in (
                "status",
                "refused",
                "group_claim",
                "coverage",
                "maximum_passing_size",
                "group_f1",
                "group_ari",
            ):
                output[f"{method}_{side}_{key}"] = estimate[key]
            output[f"{method}_{side}_groups"] = json.dumps(
                estimate["selected_groups"],
                separators=(",", ":"),
            )
    return output


def _rate(series: pd.Series) -> dict[str, float | int]:
    values = series.astype(bool)
    successes = int(values.sum())
    trials = len(values)
    return {
        "successes": successes,
        "trials": trials,
        "rate": successes / trials,
        "lower95": base._one_sided_lower(  # noqa: SLF001
            successes,
            trials,
        ),
        "upper95": base._one_sided_upper(  # noqa: SLF001
            successes,
            trials,
        ),
    }


def _decision(
    frame: pd.DataFrame,
    config: dict[str, Any],
    *,
    smoke: bool,
) -> dict[str, Any]:
    gates = config["gates"]
    summaries = []
    for method in METHODS:
        summaries.append({
            "method": method,
            "positive_claim": _rate(
                frame[f"{method}_positive_group_claim"]
            ),
            "chain_claim": _rate(
                frame[f"{method}_chain_group_claim"]
            ),
            "chain_ambiguity": _rate(
                frame[f"{method}_chain_refused"]
            ),
            "positive_f1_median": float(
                frame[f"{method}_positive_group_f1"].median()
            ),
            "positive_ari_median": float(
                frame[f"{method}_positive_group_ari"].median()
            ),
            "positive_maximum_passing_size_median": float(
                frame[
                    f"{method}_positive_maximum_passing_size"
                ].median()
            ),
            "chain_maximum_passing_size_median": float(
                frame[
                    f"{method}_chain_maximum_passing_size"
                ].median()
            ),
        })
    if smoke:
        checks = {
            "aggregate_pair_matched": bool(
                frame["aggregate_pair_mae"].max()
                <= gates["maximum_aggregate_pair_mae"]
            ),
            "positive_recovered": bool(all(
                frame[f"{method}_positive_group_claim"].all()
                for method in METHODS
            )),
            "chain_rejected": bool(all(
                ~frame[f"{method}_chain_group_claim"].any()
                for method in METHODS
            )),
        }
        return {
            "status": (
                "V8_INCIDENCE_GRAPH_FAIRNESS_SMOKE_PASS"
                if all(checks.values())
                else "V8_INCIDENCE_GRAPH_FAIRNESS_SMOKE_STOP"
            ),
            "checks": checks,
        }
    checks = {
        "aggregate_pair_matched": bool(
            frame["aggregate_pair_mae"].mean()
            <= gates["maximum_aggregate_pair_mae"]
        ),
        "positive_claim": bool(all(
            row["positive_claim"]["lower95"]
            >= gates["minimum_core_claim_rate"]
            for row in summaries
        )),
        "positive_f1": bool(all(
            row["positive_f1_median"]
            >= gates["minimum_core_group_f1"]
            for row in summaries
        )),
        "positive_ari": bool(all(
            row["positive_ari_median"]
            >= gates["minimum_core_group_ari"]
            for row in summaries
        )),
        "chain_claim": bool(all(
            row["chain_claim"]["upper95"]
            <= gates["maximum_chain_claim_rate"]
            for row in summaries
        )),
        "chain_ambiguity": bool(
            summaries[0]["chain_ambiguity"]["lower95"]
            >= gates["minimum_chain_ambiguity_rate"]
            and summaries[1]["chain_ambiguity"]["lower95"]
            >= gates["minimum_chain_ambiguity_rate"]
        ),
    }
    return {
        "status": (
            "V8_INCIDENCE_GRAPH_FAIRNESS_PASS"
            if all(checks.values())
            else "V8_INCIDENCE_GRAPH_FAIRNESS_STOP"
        ),
        "checks": checks,
        "method_summary": summaries,
        "aggregate_pair_mae_mean": float(
            frame["aggregate_pair_mae"].mean()
        ),
        "claim_boundary": config["claim_boundary"],
    }


def _flatten_summaries(
    summaries: list[dict[str, Any]],
) -> pd.DataFrame:
    output = []
    for summary in summaries:
        row: dict[str, Any] = {"method": summary["method"]}
        for key, value in summary.items():
            if key == "method":
                continue
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    row[f"{key}_{nested_key}"] = nested_value
            else:
                row[key] = value
        output.append(row)
    return pd.DataFrame(output)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_incidence_graph_fairness_v33.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_incidence_graph_fairness/v33",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = base._read_json(args.config)  # noqa: SLF001
    source_path = ROOT / config["source_config"]
    if _sha256(source_path) != config["source_config_sha256"]:
        raise RuntimeError("source V3.2 config hash mismatch")
    source = base._read_json(source_path)  # noqa: SLF001
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["confirmation_repetitions"] = 3
    args.output_dir.mkdir(parents=True, exist_ok=True)

    results = _run(config, source)
    frame = pd.DataFrame([_row(result) for result in results])
    decision = _decision(frame, config, smoke=args.smoke)
    frame.to_csv(
        args.output_dir / "confirmation_metrics.csv",
        index=False,
    )
    if not args.smoke:
        _flatten_summaries(decision["method_summary"]).to_csv(
            args.output_dir / "method_summary.csv",
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
        "# V8 Incidence Graph Fairness V3.3\n\n"
        f"Decision: `{decision['status']}`\n\n"
        "```json\n"
        f"{json.dumps(decision, indent=2)}\n"
        "```\n",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v7_governance.py",
            ROOT / "suica_core/v8_incidence_incremental.py",
            ROOT / "suica_core/v8_incidence_incremental_v31.py",
            ROOT / "suica_core/v8_incidence_multiplicity.py",
            ROOT / "suica_core/v8_incidence_strong_chain.py",
            ROOT / "suica_core/v8_incidence_graph_fairness.py",
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
