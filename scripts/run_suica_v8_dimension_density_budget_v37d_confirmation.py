#!/usr/bin/env python3
"""Run the paired V3.7D recovery-versus-identification confirmation."""
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

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    sha256_file,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_dimension_density_budget import (  # noqa: E402
    DensityWorldSpec,
    evaluate_density_population,
    simulate_group_free_density_world,
    with_event_budget,
)
from suica_core.v8_group_free_routing_transport import (  # noqa: E402
    resample_routing_counts,
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=True)
        + "\n",
        encoding="utf-8",
    )


def _uint64(sequence: np.random.SeedSequence) -> int:
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def _fingerprint(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values).tobytes()).hexdigest()


def _worker(
    payload: tuple[dict[str, Any], int, tuple[int, ...]],
) -> list[dict[str, Any]]:
    config, repetition, spawn_key = payload
    root = np.random.SeedSequence(
        int(config["_active_seed"]),
        spawn_key=spawn_key,
    )
    latent_sequence, permutation_sequence, event_parent = root.spawn(3)
    latent_seed = _uint64(latent_sequence)
    permutation_rng = np.random.default_rng(permutation_sequence)
    training_authors = int(config["training_authors"])
    maximum_evaluation = int(config["maximum_evaluation_authors"])
    total_authors = training_authors + maximum_evaluation
    pool = np.arange(training_authors, total_authors)
    ordered_pool = permutation_rng.permutation(pool)
    event_sequences = iter(event_parent.spawn(
        len(config["latent_ranks"])
        * len(config["event_budgets"])
        * len(config["evaluation_author_counts"])
        * 3
    ))
    rows = []
    for rank in config["latent_ranks"]:
        latent_max = simulate_group_free_density_world(
            seed=latent_seed,
            spec=DensityWorldSpec(
                authors=total_authors,
                latent_rank=int(rank),
                author_basis_rank=int(config["maximum_latent_rank"]),
                events_per_context_session=max(config["event_budgets"]),
                author_rms=float(config["author_rms"]),
                discovery_contexts=int(config["discovery_contexts"]),
                confirmation_contexts=int(config["confirmation_contexts"]),
                extrapolation_contexts=int(config["extrapolation_contexts"]),
            ),
        )
        probability_fingerprint = _fingerprint(latent_max["probability"])
        for budget in config["event_budgets"]:
            latent = with_event_budget(latent_max, int(budget))
            for authors in config["evaluation_author_counts"]:
                reference_sequence = next(event_sequences)
                observed_sequence = next(event_sequences)
                metric_sequence = next(event_sequences)
                reference_seed = _uint64(reference_sequence)
                observed_seed = _uint64(observed_sequence)
                metric_seed = _uint64(metric_sequence)
                evaluation_indices = ordered_pool[: int(authors)]
                result = evaluate_density_population(
                    latent=latent,
                    reference_panel=resample_routing_counts(
                        latent,
                        np.random.default_rng(reference_sequence),
                    ),
                    observed_panel=resample_routing_counts(
                        latent,
                        np.random.default_rng(observed_sequence),
                    ),
                    primary_rank=int(config["primary_estimator_rank"]),
                    oracle_rank=int(rank),
                    neighbor_count=int(config["neighbor_count"]),
                    training_indices=np.arange(training_authors),
                    evaluation_indices=evaluation_indices,
                    random_seed=metric_seed,
                )
                recovery = (
                    result["truth_correlation"]
                    >= float(config["recovery_truth_threshold"])
                    and result["split_reliability"]
                    >= float(config["recovery_reliability_threshold"])
                )
                identity = (
                    result["local_neighbor_auc"]
                    >= float(config["identity_auc_threshold"])
                    and result["top1"]
                    >= float(config["identity_top1_threshold"])
                )
                rows.append({
                    "repetition": repetition,
                    "spawn_key": json.dumps(spawn_key),
                    "latent_seed": latent_seed,
                    "reference_seed": reference_seed,
                    "observed_seed": observed_seed,
                    "metric_seed": metric_seed,
                    "latent_rank": int(rank),
                    "authors": int(authors),
                    "event_budget": int(budget),
                    "probability_fingerprint": probability_fingerprint,
                    "evaluation_pool_fingerprint": _fingerprint(
                        ordered_pool
                    ),
                    "evaluation_index_fingerprint": _fingerprint(
                        evaluation_indices
                    ),
                    "training_evaluation_overlap": int(
                        np.intersect1d(
                            np.arange(training_authors),
                            evaluation_indices,
                        ).size
                    ),
                    "recovery_pass": recovery,
                    "identity_pass": identity,
                    "joint_recovery_without_identity": (
                        recovery and not identity
                    ),
                    "joint_identity_without_recovery": (
                        identity and not recovery
                    ),
                    "joint_recovery_and_identity": (
                        recovery and identity
                    ),
                    **result,
                })
    return rows


def _interval(
    values: np.ndarray,
    *,
    rng: np.random.Generator,
    draws: int = 20_000,
) -> dict[str, float]:
    vector = np.asarray(values, dtype=float)
    indices = rng.integers(0, len(vector), size=(draws, len(vector)))
    means = vector[indices].mean(axis=1)
    return {
        "mean": float(vector.mean()),
        "lower95": float(np.quantile(means, 0.025)),
        "upper95": float(np.quantile(means, 0.975)),
    }


def _cell_summary(frame: pd.DataFrame) -> pd.DataFrame:
    metrics = [
        "truth_correlation",
        "truth_nrmse",
        "split_reliability",
        "unseen_context_reliability",
        "local_neighbor_auc",
        "random_neighbor_auc",
        "top1",
        "relative_margin",
        "median_crowding_index",
        "oracle_rank_truth_correlation",
        "oracle_rank_truth_nrmse",
        "oracle_rank_local_neighbor_auc",
        "recovery_pass",
        "identity_pass",
        "joint_recovery_without_identity",
        "joint_identity_without_recovery",
        "joint_recovery_and_identity",
    ]
    return (
        frame.groupby(
            ["latent_rank", "authors", "event_budget"],
            as_index=False,
        )[metrics]
        .mean()
    )


def _paired_effects(
    frame: pd.DataFrame,
    *,
    seed: int,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed ^ 0xD37D)
    at128 = frame[frame["event_budget"] == 128]

    def density_delta(rank: int, metric: str) -> np.ndarray:
        subset = at128[at128["latent_rank"] == rank]
        pivot = subset.pivot(
            index="repetition",
            columns="authors",
            values=metric,
        )
        return (pivot[32] - pivot[192]).to_numpy()

    hard = {
        rank: density_delta(rank, "local_neighbor_auc")
        for rank in (2, 4, 8)
    }
    random_delta = density_delta(2, "random_neighbor_auc")
    interaction = hard[2] - hard[8]

    rank12 = at128[at128["latent_rank"] == 12].copy()
    fisher_delta = (
        np.arctanh(np.clip(
            rank12["oracle_rank_truth_correlation"].to_numpy(),
            -0.999999,
            0.999999,
        ))
        - np.arctanh(np.clip(
            rank12["truth_correlation"].to_numpy(),
            -0.999999,
            0.999999,
        ))
    )
    nrmse_improvement = (
        rank12["truth_nrmse"].to_numpy()
        - rank12["oracle_rank_truth_nrmse"].to_numpy()
    )

    budget = frame[frame["latent_rank"] <= 8].copy()
    budget["fisher_truth"] = np.arctanh(np.clip(
        budget["truth_correlation"],
        -0.999999,
        0.999999,
    ))
    pivot = budget.pivot(
        index=["repetition", "latent_rank", "authors"],
        columns="event_budget",
        values="fisher_truth",
    )
    pivot["delta"] = pivot[128] - pivot[64]
    budget_by_repetition = pivot["delta"].groupby("repetition").mean()
    cell_direction = pivot["delta"].groupby(
        ["latent_rank", "authors"]
    ).mean()

    return {
        "rank2_crowding_auc_delta": _interval(hard[2], rng=rng),
        "rank4_crowding_auc_delta": _interval(hard[4], rng=rng),
        "rank8_crowding_auc_delta": _interval(hard[8], rng=rng),
        "rank2_random_neighbor_delta": _interval(
            random_delta,
            rng=rng,
        ),
        "dimension_crowding_interaction": _interval(
            interaction,
            rng=rng,
        ),
        "rank2_minus_rank4_delta": _interval(
            hard[2] - hard[4],
            rng=rng,
        ),
        "rank4_minus_rank8_delta": _interval(
            hard[4] - hard[8],
            rng=rng,
        ),
        "rank12_oracle_fisher_improvement": _interval(
            fisher_delta,
            rng=rng,
        ),
        "rank12_oracle_nrmse_improvement": _interval(
            nrmse_improvement,
            rng=rng,
        ),
        "rank12_oracle_truth_mean": float(
            rank12["oracle_rank_truth_correlation"].mean()
        ),
        "budget_fisher_improvement": _interval(
            budget_by_repetition.to_numpy(),
            rng=rng,
        ),
        "positive_budget_cells": int((cell_direction > 0).sum()),
        "budget_cells_total": int(len(cell_direction)),
    }


def _decision(
    frame: pd.DataFrame,
    summary: pd.DataFrame,
    effects: dict[str, Any],
    *,
    config: dict[str, Any],
    integrity: dict[str, Any],
    smoke: bool,
) -> dict[str, Any]:
    at128 = summary[summary["event_budget"] == 128]

    def minimum_rate(rank: int, metric: str, authors: list[int]) -> float:
        values = at128[
            (at128["latent_rank"] == rank)
            & (at128["authors"].isin(authors))
        ][metric]
        return float(values.min())

    gates = config["gates"]
    checks = {
        "numeric_integrity": integrity["numeric"],
        "author_disjointness": integrity["author_disjointness"],
        "event_seed_independence": integrity["event_seed_independence"],
        "nested_author_design": integrity["nested_author_design"],
        "paired_latent_design": integrity["paired_latent_design"],
        "rank2_forward_separation": (
            minimum_rate(
                2,
                "joint_recovery_without_identity",
                [96, 192],
            )
            >= gates[
                "minimum_rank2_joint_recovery_without_identity_rate"
            ]
        ),
        "rank2_crowding_effect": (
            effects["rank2_crowding_auc_delta"]["mean"]
            >= gates["minimum_mean_rank2_crowding_auc_delta"]
            and effects["rank2_crowding_auc_delta"]["lower95"] > 0
        ),
        "dimension_interaction": (
            effects["dimension_crowding_interaction"]["lower95"] > 0
            and effects["rank2_minus_rank4_delta"]["lower95"] > 0
            and effects["rank4_minus_rank8_delta"]["lower95"] > 0
        ),
        "random_neighbor_control": (
            abs(effects["rank2_random_neighbor_delta"]["mean"])
            <= gates["maximum_absolute_random_neighbor_density_delta"]
        ),
        "rank8_joint_positive_control": (
            minimum_rate(
                8,
                "joint_recovery_and_identity",
                [32, 96, 192],
            )
            >= gates["minimum_rank8_joint_recovery_and_identity_rate"]
        ),
        "rank12_reverse_separation": (
            minimum_rate(
                12,
                "joint_identity_without_recovery",
                [32, 96, 192],
            )
            >= gates[
                "minimum_rank12_joint_identity_without_recovery_rate"
            ]
        ),
        "rank12_capacity_diagnosis": (
            effects["rank12_oracle_truth_mean"]
            >= gates["minimum_oracle_rank12_truth_correlation"]
            and effects["rank12_oracle_fisher_improvement"]["lower95"] > 0
            and effects["rank12_oracle_nrmse_improvement"]["lower95"] > 0
        ),
        "budget_effect": (
            effects["budget_fisher_improvement"]["lower95"] > 0
            and effects["positive_budget_cells"]
            >= gates["minimum_positive_budget_cells"]
        ),
    }
    prefix = "V8_DIMENSION_DENSITY_EVENT_BUDGET_V37D_CONFIRMATION_"
    return {
        "status": prefix + (
            "SMOKE_PASS" if smoke and all(checks.values())
            else "SMOKE_STOP" if smoke
            else "PASS" if all(checks.values())
            else "STOP"
        ),
        "checks": {key: bool(value) for key, value in checks.items()},
        "paired_effects": effects,
        "integrity": integrity,
        "claim_boundary": config["claim_boundary"],
    }


def _integrity(frame: pd.DataFrame, config: dict[str, Any]) -> dict[str, Any]:
    event_seeds = np.concatenate([
        frame["reference_seed"].unique(),
        frame["observed_seed"].unique(),
        frame["metric_seed"].unique(),
    ])
    nested = True
    paired_latent = True
    for repetition, group in frame.groupby("repetition"):
        paired_latent &= bool(group["latent_seed"].nunique() == 1)
        for rank, rank_group in group.groupby("latent_rank"):
            paired_latent &= bool(
                rank_group["probability_fingerprint"].nunique() == 1
            )
        nested &= bool(
            group["evaluation_pool_fingerprint"].nunique() == 1
            and set(group["authors"].unique())
            == set(config["evaluation_author_counts"])
        )
    numeric_columns = [
        "truth_correlation",
        "truth_nrmse",
        "split_reliability",
        "unseen_context_reliability",
        "local_neighbor_auc",
        "random_neighbor_auc",
        "top1",
        "oracle_rank_truth_correlation",
        "oracle_rank_truth_nrmse",
    ]
    return {
        "numeric": bool(
            np.isfinite(frame[numeric_columns].to_numpy()).all()
        ),
        "author_disjointness": bool(
            (frame["training_evaluation_overlap"] == 0).all()
        ),
        "event_seed_independence": bool(
            len(event_seeds) == len(np.unique(event_seeds))
        ),
        "event_seed_count": int(len(event_seeds)),
        "nested_author_design": nested,
        "paired_latent_design": paired_latent,
        "rows": int(len(frame)),
    }


def _verify_parent(config: dict[str, Any]) -> dict[str, Any]:
    parent = config["required_parent_seal"]
    path = ROOT / parent["path"]
    got = sha256_file(path)
    if got != parent["sha256"]:
        raise RuntimeError("V3.7C parent seal mismatch")
    return {"status": "PARENT_SEAL_PASS", "sha256": got}


def _verify_own_seal(path: Path, *, smoke: bool) -> dict[str, Any]:
    if smoke:
        return {"status": "OWN_SEAL_NOT_REQUIRED_FOR_SMOKE"}
    if not path.is_file():
        raise RuntimeError("canonical confirmation requires V3.7D seal")
    seal = _read(path)
    failures = [
        relative
        for relative, expected in seal["files"].items()
        if not (ROOT / relative).is_file()
        or sha256_file(ROOT / relative) != expected
    ]
    if failures:
        raise RuntimeError(f"V3.7D seal mismatch: {failures}")
    return {
        "status": "V37D_PROSPECTIVE_SEAL_PASS",
        "sha256": sha256_file(path),
    }


def _report(decision: dict[str, Any], summary: pd.DataFrame) -> str:
    return f"""# V8 Dimension-Density-Budget V3.7D Confirmation

Decision: `{decision["status"]}`

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Paired effects

```json
{json.dumps(decision["paired_effects"], indent=2)}
```

## Cell summary

{summary.to_markdown(index=False)}

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT
        / "configs/v8_dimension_density_budget_v37d_confirmation.json",
    )
    parser.add_argument(
        "--seal",
        type=Path,
        default=ROOT
        / "configs/v8_dimension_density_budget_v37d_confirmation_seal.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT
        / "results/v8_dimension_density_budget/v37d_confirmation",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = _read(args.config)
    config["_active_seed"] = (
        int(config["smoke_seed"])
        if args.smoke else int(config["canonical_seed"])
    )
    repetitions = 4 if args.smoke else int(config["repetitions"])
    parent = _verify_parent(config)
    own_seal = _verify_own_seal(args.seal, smoke=args.smoke)
    root = np.random.SeedSequence(int(config["_active_seed"]))
    spawn_keys = [tuple(child.spawn_key) for child in root.spawn(repetitions)]
    payloads = [
        (config, repetition, spawn_keys[repetition])
        for repetition in range(repetitions)
    ]
    if args.smoke:
        nested = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"])
        ) as executor:
            nested = list(executor.map(_worker, payloads, chunksize=1))
    frame = pd.DataFrame([row for rows in nested for row in rows])
    summary = _cell_summary(frame)
    integrity = _integrity(frame, config)
    effects = _paired_effects(
        frame,
        seed=int(config["_active_seed"]),
    )
    decision = _decision(
        frame,
        summary,
        effects,
        config=config,
        integrity=integrity,
        smoke=args.smoke,
    )
    decision["parent_seal"] = parent
    decision["prospective_seal"] = own_seal

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_dir / "paired_metrics.csv", index=False)
    summary.to_csv(args.output_dir / "cell_summary.csv", index=False)
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        _report(decision, summary),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            ROOT / config["required_parent_seal"]["path"],
        ],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_dimension_density_budget.py",
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
        "rows": len(frame),
        "checks": decision["checks"],
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
