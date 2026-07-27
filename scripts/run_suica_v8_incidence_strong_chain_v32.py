#!/usr/bin/env python3
"""Run the frozen V3.2 strong-chain higher-order counterfactual."""
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
from suica_core.v8_incidence_incremental import (  # noqa: E402
    simulate_counterfactual_pair,
    simulate_null_population,
)
from suica_core.v8_incidence_incremental_v31 import (  # noqa: E402
    analyze_incidence_population_v31,
)
from suica_core.v8_incidence_strong_chain import (  # noqa: E402
    analyze_strong_chain_pair,
    simulate_strong_chain_pair,
)

GRAPH_METHODS = ("single_link", "complete_link", "spectral")
CAP_STATUSES = {
    "REFUSE_ENUMERATION_CAP",
    "REFUSE_CANDIDATE_CLOSURE_CAP",
}


def _seed(
    config: dict[str, Any],
    *,
    stage: str,
    index: int,
    repetition: int,
) -> int:
    offset = {
        "discovery": 0,
        "confirmation": 30_000_000,
        "attack": 60_000_000,
    }[stage]
    return int(config["seed"]) + offset + 100_000 * index + repetition


def _pair_worker(
    payload: tuple[dict[str, Any], str, int],
) -> dict[str, Any]:
    config, stage, repetition = payload
    seed = _seed(
        config,
        stage=stage,
        index=0,
        repetition=repetition,
    )
    spec = base._spec(config)  # noqa: SLF001
    pair = simulate_strong_chain_pair(
        seed=seed,
        spec=spec,
        private_excursion_radius=float(
            config["private_excursion_radius"]
        ),
        anchor_scale=float(config["anchor_scale"]),
    )
    result = analyze_strong_chain_pair(
        pair,
        spec=spec,
        candidate_closure_cap=int(
            config["candidate_closure_cap"]
        ),
        graph_config=config,
        seed=seed,
    )
    return {
        "stage": stage,
        "seed": seed,
        "repetition": repetition,
        **result,
    }


def _attack_worker(
    payload: tuple[dict[str, Any], str, int, int],
) -> dict[str, Any]:
    config, world, index, repetition = payload
    seed = _seed(
        config,
        stage="attack",
        index=index,
        repetition=repetition,
    )
    spec = base._spec(config)  # noqa: SLF001
    if world == "condition_shift":
        pair = simulate_counterfactual_pair(
            seed=seed,
            pair_id="CF1",
            spec=spec,
        )
        views = pair["negative_views"]
        labels = pair["labels"]
    elif world == "rotating_membership":
        pair = simulate_counterfactual_pair(
            seed=seed,
            pair_id="CF3",
            spec=spec,
        )
        views = pair["negative_views"]
        labels = pair["labels"]
    else:
        population = simulate_null_population(
            seed=seed,
            world=world,
            spec=spec,
        )
        views = population["views"]
        labels = population["labels"]
    estimate = analyze_incidence_population_v31(
        views,
        labels,
        spec=spec,
        candidate_closure_cap=int(
            config["candidate_closure_cap"]
        ),
    )
    return {
        "stage": "attack",
        "world": world,
        "seed": seed,
        "repetition": repetition,
        "status": (
            estimate["status"]
            if estimate["status"] in CAP_STATUSES
            else "ESTIMATE_READY"
        ),
        "estimate": estimate,
    }


def _run_parallel(
    worker: Any,
    payloads: list[Any],
    *,
    jobs: int,
) -> list[dict[str, Any]]:
    if jobs <= 1:
        return [worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(worker, payloads, chunksize=1))


def _run_pairs(
    config: dict[str, Any],
    *,
    stage: str,
    repetitions: int,
) -> list[dict[str, Any]]:
    return _run_parallel(
        _pair_worker,
        [
            (config, stage, repetition)
            for repetition in range(repetitions)
        ],
        jobs=int(config["jobs"]),
    )


def _run_attacks(
    config: dict[str, Any],
    *,
    repetitions: int,
) -> list[dict[str, Any]]:
    payloads = [
        (config, world, index, repetition)
        for index, world in enumerate(config["attacks"])
        for repetition in range(repetitions)
    ]
    return _run_parallel(
        _attack_worker,
        payloads,
        jobs=int(config["jobs"]),
    )


def _estimate_scalars(
    output: dict[str, Any],
    estimate: dict[str, Any],
    *,
    prefix: str,
) -> None:
    for key in (
        "status",
        "refused",
        "group_claim",
        "coverage",
        "candidate_core_count",
        "incidence_auc",
        "whole_map_auc",
        "group_f1",
        "group_ari",
        "cross_view_core_jaccard",
        "enumeration_nodes",
    ):
        output[f"{prefix}_{key}"] = estimate.get(key)
    output[f"{prefix}_selected_cores"] = json.dumps(
        estimate.get("selected_cores", []),
        separators=(",", ":"),
    )


def _pair_row(row: dict[str, Any]) -> dict[str, Any]:
    output = {
        "stage": row["stage"],
        "seed": row["seed"],
        "repetition": row["repetition"],
        "status": row["status"],
        "chain_triplet_min_persistence": row[
            "chain_triplet_min_persistence"
        ],
        "chain_triplet_max_persistence": row[
            "chain_triplet_max_persistence"
        ],
        "chain_all_triplets_pass": row[
            "chain_all_triplets_pass"
        ],
        "permutation_auc": row["permutation_auc"],
    }
    output.update(row["matching"])
    _estimate_scalars(output, row["positive"], prefix="positive_hyper")
    _estimate_scalars(output, row["chain"], prefix="chain_hyper")
    output["chain_hyper_ambiguity_refusal"] = bool(
        row["chain"].get("status") == "REFUSE_CORE_AMBIGUITY"
    )
    for method in GRAPH_METHODS:
        for side, source in (
            ("positive", row["positive_graphs"][method]),
            ("chain", row["chain_graphs"][method]),
        ):
            for key in (
                "refused",
                "group_claim",
                "coverage",
                "recovered_six_groups",
                "six_group_claim",
                "group_f1",
                "group_ari",
                "selected_k",
                "eigengap",
                "silhouette",
            ):
                output[f"{method}_{side}_{key}"] = source.get(key)
        output[f"{method}_false_claim_delta"] = (
            int(row["chain_graphs"][method]["six_group_claim"])
            - int(row["chain"].get("group_claim", False))
        )
    return output


def _attack_row(row: dict[str, Any]) -> dict[str, Any]:
    output = {
        "world": row["world"],
        "seed": row["seed"],
        "repetition": row["repetition"],
        "status": row["status"],
    }
    _estimate_scalars(output, row["estimate"], prefix="estimate")
    return output


def _frames(
    pairs: list[dict[str, Any]],
    attacks: list[dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    return (
        pd.DataFrame([_pair_row(row) for row in pairs]),
        pd.DataFrame([_attack_row(row) for row in attacks]),
    )


def _metric_interval(
    frame: pd.DataFrame,
    column: str,
    *,
    seed: int,
    confidence: float = 0.90,
) -> dict[str, float]:
    values = pd.to_numeric(frame[column], errors="coerce").to_numpy()
    low, high = base._bootstrap_mean_interval(  # noqa: SLF001
        values,
        seed=seed,
        confidence=confidence,
    )
    return {
        "mean": float(np.nanmean(values)),
        "median": float(np.nanmedian(values)),
        f"ci{int(confidence * 100)}_low": low,
        f"ci{int(confidence * 100)}_high": high,
        "minimum": float(np.nanmin(values)),
        "maximum": float(np.nanmax(values)),
    }


def _rate(
    values: pd.Series,
) -> dict[str, float | int]:
    vector = values.astype(bool)
    successes = int(vector.sum())
    trials = len(vector)
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


def _summaries(
    pairs: pd.DataFrame,
    attacks: pd.DataFrame,
    *,
    seed: int,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    matching_columns = (
        "observed_pair_matrix_mae",
        "observed_pair_matrix_correlation",
        "pair_auc_difference",
        "normalized_wasserstein",
        "degree_strength_relative_error",
        "laplacian_spectrum_relative_error",
        "oracle_pair_matrix_max_error",
        "oracle_distance_relative_error",
        "fitted_distance_relative_error",
        "opportunity_max_error",
        "permutation_auc",
    )
    matching = {
        column: _metric_interval(
            pairs,
            column,
            seed=seed + index,
        )
        for index, column in enumerate(matching_columns)
    }
    hypergraph = {
        "core_claim": _rate(pairs["positive_hyper_group_claim"]),
        "core_f1": _metric_interval(
            pairs,
            "positive_hyper_group_f1",
            seed=seed + 100,
        ),
        "core_ari": _metric_interval(
            pairs,
            "positive_hyper_group_ari",
            seed=seed + 101,
        ),
        "triplets_pass": _rate(pairs["chain_all_triplets_pass"]),
        "chain_claim": _rate(pairs["chain_hyper_group_claim"]),
        "chain_ambiguity": _rate(
            pairs["chain_hyper_ambiguity_refusal"]
        ),
    }
    graph_rows = []
    for index, method in enumerate(GRAPH_METHODS):
        delta = _metric_interval(
            pairs,
            f"{method}_false_claim_delta",
            seed=seed + 200 + index,
            confidence=0.95,
        )
        graph_rows.append({
            "method": method,
            "core_recovery": _rate(
                pairs[f"{method}_positive_six_group_claim"]
            ),
            "chain_false_claim": _rate(
                pairs[f"{method}_chain_six_group_claim"]
            ),
            "false_claim_delta": delta,
            "core_f1_median": float(
                pairs[f"{method}_positive_group_f1"].median()
            ),
            "chain_f1_median": float(
                pairs[f"{method}_chain_group_f1"].median()
            ),
        })
    attack_rows = []
    for world, group in attacks.groupby("world", sort=True):
        attack_rows.append({
            "world": world,
            "claims": _rate(group["estimate_group_claim"]),
            "refusal_rate": float(group["estimate_refused"].mean()),
            "cap_failures": int(
                group["status"].isin(CAP_STATUSES).sum()
            ),
        })
    return matching, hypergraph, graph_rows, attack_rows


def _decision(
    pairs: pd.DataFrame,
    attacks: pd.DataFrame,
    config: dict[str, Any],
    *,
    smoke: bool,
) -> dict[str, Any]:
    matching, hypergraph, graphs, attack_rows = _summaries(
        pairs,
        attacks,
        seed=int(config["seed"]) + 80_001,
    )
    gates = config["gates"]
    ready = bool(
        pairs["status"].eq("ESTIMATE_READY").all()
        and attacks["status"].eq("ESTIMATE_READY").all()
    )
    if smoke:
        checks = {
            "estimate_ready": ready,
            "pairwise_matched": bool(
                pairs["oracle_pair_matrix_max_error"].max()
                <= gates["maximum_oracle_pair_matrix_error"]
                and pairs["observed_pair_matrix_mae"].max()
                <= gates["maximum_observed_pair_matrix_mae"]
                and pairs[
                    "observed_pair_matrix_correlation"
                ].min()
                >= gates[
                    "minimum_observed_pair_matrix_correlation"
                ]
                and pairs["normalized_wasserstein"].max()
                <= gates["maximum_normalized_wasserstein"]
            ),
            "hypergraph_contrast": bool(
                pairs["positive_hyper_group_claim"].all()
                and ~pairs["chain_hyper_group_claim"].any()
                and pairs["chain_hyper_ambiguity_refusal"].all()
                and pairs["chain_all_triplets_pass"].all()
            ),
            "graph_false_merge": bool(all(
                pairs[f"{method}_positive_six_group_claim"].all()
                and pairs[f"{method}_chain_six_group_claim"].all()
                for method in GRAPH_METHODS
            )),
            "attacks_safe": bool(
                ~attacks["estimate_group_claim"].any()
            ),
        }
        return {
            "status": (
                "V8_INCIDENCE_STRONG_CHAIN_SMOKE_PASS"
                if all(checks.values())
                else "V8_INCIDENCE_STRONG_CHAIN_SMOKE_STOP"
            ),
            "checks": checks,
        }

    matching_checks = {
        "oracle_pair_matrix": bool(
            matching["oracle_pair_matrix_max_error"]["maximum"]
            <= gates["maximum_oracle_pair_matrix_error"]
        ),
        "observed_pair_mae": bool(
            matching["observed_pair_matrix_mae"]["ci90_high"]
            <= gates["maximum_observed_pair_matrix_mae"]
        ),
        "observed_pair_correlation": bool(
            matching["observed_pair_matrix_correlation"]["ci90_low"]
            >= gates["minimum_observed_pair_matrix_correlation"]
        ),
        "pair_auc_equivalence": bool(
            matching["pair_auc_difference"]["ci90_low"]
            >= -gates["maximum_pair_auc_difference"]
            and matching["pair_auc_difference"]["ci90_high"]
            <= gates["maximum_pair_auc_difference"]
        ),
        "distance_distribution": bool(
            matching["normalized_wasserstein"]["ci90_high"]
            <= gates["maximum_normalized_wasserstein"]
        ),
        "degree_strength": bool(
            matching["degree_strength_relative_error"]["ci90_high"]
            <= gates["maximum_degree_strength_relative_error"]
        ),
        "laplacian_spectrum": bool(
            matching[
                "laplacian_spectrum_relative_error"
            ]["ci90_high"]
            <= gates[
                "maximum_laplacian_spectrum_relative_error"
            ]
        ),
        "whole_map_oracle": bool(
            matching["oracle_distance_relative_error"]["maximum"]
            <= gates["maximum_oracle_distance_relative_error"]
        ),
        "whole_map_fitted": bool(
            matching["fitted_distance_relative_error"]["maximum"]
            <= gates["maximum_fitted_distance_relative_error"]
        ),
        "opportunity": bool(
            matching["opportunity_max_error"]["maximum"] == 0
        ),
        "permutation": bool(
            matching["permutation_auc"]["ci90_low"]
            >= gates["minimum_permutation_auc"]
            and matching["permutation_auc"]["ci90_high"]
            <= gates["maximum_permutation_auc"]
        ),
    }
    structure_checks = {
        "estimate_ready": ready,
        "hypergraph_core_claim": bool(
            hypergraph["core_claim"]["lower95"]
            >= gates["minimum_hypergraph_core_claim_rate"]
        ),
        "hypergraph_core_f1": bool(
            hypergraph["core_f1"]["median"]
            >= gates["minimum_hypergraph_group_f1"]
        ),
        "hypergraph_core_ari": bool(
            hypergraph["core_ari"]["median"]
            >= gates["minimum_hypergraph_group_ari"]
        ),
        "triplets_persistent": bool(
            hypergraph["triplets_pass"]["lower95"]
            >= gates["minimum_triplet_pass_rate"]
        ),
        "chain_claim_safe": bool(
            hypergraph["chain_claim"]["upper95"]
            <= gates["maximum_chain_hypergraph_claim_rate"]
        ),
        "chain_ambiguity": bool(
            hypergraph["chain_ambiguity"]["lower95"]
            >= gates["minimum_chain_ambiguity_rate"]
        ),
        "graph_core_recovery": bool(all(
            row["core_recovery"]["lower95"]
            >= gates["minimum_graph_core_recovery_rate"]
            for row in graphs
        )),
        "graph_chain_false_claim": bool(all(
            row["chain_false_claim"]["lower95"]
            >= gates["minimum_graph_chain_false_claim_rate"]
            for row in graphs
        )),
        "graph_delta": bool(all(
            row["false_claim_delta"]["ci95_low"]
            >= gates["minimum_graph_minus_hypergraph_delta"]
            for row in graphs
        )),
        "attacks_safe": bool(all(
            row["claims"]["upper95"]
            <= gates["maximum_attack_claim_rate"]
            for row in attack_rows
        )),
        "no_caps": bool(
            not pairs["status"].isin(CAP_STATUSES).any()
            and all(row["cap_failures"] == 0 for row in attack_rows)
        ),
    }
    checks = {**matching_checks, **structure_checks}
    if not all(matching_checks.values()):
        status = "V8_INCIDENCE_STRONG_CHAIN_STOP_PAIRWISE_NOT_MATCHED"
    elif all(structure_checks.values()):
        status = "V8_INCIDENCE_STRONG_CHAIN_PLANTED_PASS"
    else:
        status = "V8_INCIDENCE_STRONG_CHAIN_STOP_NOT_IDENTIFIED"
    return {
        "status": status,
        "checks": checks,
        "matching_summary": matching,
        "hypergraph_summary": hypergraph,
        "graph_summary": graphs,
        "attack_summary": attack_rows,
        "claim_boundary": config["claim_boundary"],
    }


def _flatten_summary_rows(
    rows: list[dict[str, Any]],
) -> pd.DataFrame:
    flattened = []
    for row in rows:
        output: dict[str, Any] = {}
        for key, value in row.items():
            if isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    output[f"{key}_{nested_key}"] = nested_value
            else:
                output[key] = value
        flattened.append(output)
    return pd.DataFrame(flattened)


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 Incidence Strong-Chain V3.2

## Decision

`{decision["status"]}`

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Matching summary

```json
{json.dumps(decision.get("matching_summary", {}), indent=2)}
```

## Hypergraph summary

```json
{json.dumps(decision.get("hypergraph_summary", {}), indent=2)}
```

## Graph summary

```json
{json.dumps(decision.get("graph_summary", []), indent=2)}
```

## Attack summary

```json
{json.dumps(decision.get("attack_summary", []), indent=2)}
```

## Claim boundary

{decision.get("claim_boundary", "Smoke behavior only.")}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_incidence_strong_chain_v32.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_incidence_strong_chain/v32",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = base._read_json(args.config)  # noqa: SLF001
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 1
        config["confirmation_repetitions"] = 3
        config["attack_repetitions"] = 3
    args.output_dir.mkdir(parents=True, exist_ok=True)

    discovery = _run_pairs(
        config,
        stage="discovery",
        repetitions=int(config["discovery_repetitions"]),
    )
    confirmation = _run_pairs(
        config,
        stage="confirmation",
        repetitions=int(config["confirmation_repetitions"]),
    )
    attacks = _run_attacks(
        config,
        repetitions=int(config["attack_repetitions"]),
    )
    discovery_frame, _ = _frames(discovery, [])
    pair_frame, attack_frame = _frames(confirmation, attacks)
    decision = _decision(
        pair_frame,
        attack_frame,
        config,
        smoke=args.smoke,
    )

    discovery_frame.to_csv(
        args.output_dir / "discovery_pair_metrics.csv",
        index=False,
    )
    pair_frame.to_csv(
        args.output_dir / "confirmation_pair_metrics.csv",
        index=False,
    )
    attack_frame.to_csv(
        args.output_dir / "confirmation_attack_metrics.csv",
        index=False,
    )
    if not args.smoke:
        pd.DataFrame([
            {"metric": key, **value}
            for key, value in decision["matching_summary"].items()
        ]).to_csv(
            args.output_dir / "matching_summary.csv",
            index=False,
        )
        pd.DataFrame([
            {"metric": key, **value}
            for key, value in decision["hypergraph_summary"].items()
        ]).to_csv(
            args.output_dir / "hypergraph_summary.csv",
            index=False,
        )
        _flatten_summary_rows(decision["graph_summary"]).to_csv(
            args.output_dir / "graph_summary.csv",
            index=False,
        )
        _flatten_summary_rows(decision["attack_summary"]).to_csv(
            args.output_dir / "attack_summary.csv",
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
            ROOT / "suica_core/v8_incidence_incremental_v31.py",
            ROOT / "suica_core/v8_incidence_strong_chain.py",
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
