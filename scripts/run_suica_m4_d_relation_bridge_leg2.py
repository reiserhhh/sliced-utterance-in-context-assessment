"""M4-D leg 2 world battery: when does a relation field license individual coordinates.

Runs the planted battery (individual / group-only / mixed families plus the
vanishing-individuality C2-machinery fields), evaluates the rigidity index
against ground-truth reconstructability, and adjudicates the three
pre-registered leans from docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md.

Outputs (default results/m4_d_relation_bridge/):
- relation_bridge_worlds.csv : one row per generated world replicate
- decision.json              : lean adjudication with exact numbers
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from suica_core.m4_relation_bridge import (  # noqa: E402
    RelationBridgeConfig,
    c2_machinery_relation_world,
    evaluate_relation_world,
    planted_relation_world,
)

NOISE_GRID = (0.02, 0.05, 0.1, 0.2, 0.35, 0.6, 1.0, 1.5, 2.5)
MIXED_EPSILONS = (0.1, 0.2, 0.4)
MIXED_NOISE = (0.05, 0.2, 0.6)
C2_SETTINGS = (
    ("group_only", 0.0),
    ("joint", 0.5),
    ("joint", 1.5),
)
GAP_CLOSE_MARGIN = 0.25  # pre-fixed: "gap closed" when mean margin drops below
LEAN_A_THRESHOLD = 0.90
LEAN_B_REFUSAL_RATE = 0.90
LEAN_B_AUTHOR_AUC = 0.80


def run_battery(
    *,
    replicates: int,
    seed: int,
    config: RelationBridgeConfig,
) -> pd.DataFrame:
    rows: list[dict] = []
    index = 0

    def next_seed() -> int:
        nonlocal index
        index += 1
        return seed + 7919 * index

    for family in ("individual", "group_only"):
        for noise in NOISE_GRID:
            for replicate in range(replicates):
                world_seed = next_seed()
                world = planted_relation_world(
                    family,
                    noise=noise,
                    seed=world_seed,
                )
                record = evaluate_relation_world(
                    world,
                    config=config,
                    seed=world_seed + 1,
                )
                record.update({
                    "replicate": replicate,
                    "seed": world_seed,
                })
                rows.append(record)
    for epsilon in MIXED_EPSILONS:
        for noise in MIXED_NOISE:
            for replicate in range(replicates):
                world_seed = next_seed()
                world = planted_relation_world(
                    "mixed",
                    noise=noise,
                    epsilon=epsilon,
                    seed=world_seed,
                )
                record = evaluate_relation_world(
                    world,
                    config=config,
                    seed=world_seed + 1,
                )
                record.update({
                    "replicate": replicate,
                    "seed": world_seed,
                })
                rows.append(record)
    for world_kind, epsilon in C2_SETTINGS:
        for replicate in range(replicates):
            world_seed = next_seed()
            world = c2_machinery_relation_world(
                world_kind,
                epsilon=epsilon,
                seed=world_seed,
            )
            record = evaluate_relation_world(
                world,
                config=config,
                seed=world_seed + 1,
            )
            record.update({
                "replicate": replicate,
                "seed": world_seed,
            })
            rows.append(record)
    return pd.DataFrame(rows)


def adjudicate(
    table: pd.DataFrame,
    *,
    config: RelationBridgeConfig,
) -> dict:
    labels = table["gt_reconstructable"].astype(int).to_numpy()
    scores = table["rigidity_rigidity_index"].to_numpy()
    pooled_auc = float(roc_auc_score(labels, scores))
    per_family_auc: dict[str, float] = {}
    for family, block in table.groupby("family"):
        block_labels = block["gt_reconstructable"].astype(int)
        if block_labels.nunique() == 2:
            per_family_auc[family] = float(
                roc_auc_score(
                    block_labels,
                    block["rigidity_rigidity_index"],
                )
            )
    planted_only = table[
        table["family"].isin(["individual", "group_only", "mixed"])
    ]
    planted_auc = float(
        roc_auc_score(
            planted_only["gt_reconstructable"].astype(int),
            planted_only["rigidity_rigidity_index"],
        )
    )
    lean_a = {
        "pooled_auc": pooled_auc,
        "planted_families_auc": planted_auc,
        "per_family_auc": per_family_auc,
        "threshold": LEAN_A_THRESHOLD,
        "hold": bool(pooled_auc >= LEAN_A_THRESHOLD),
    }

    group_only = table[
        table["family"].isin(["group_only", "c2_group_only"])
    ]
    refused = group_only["rigidity_status"] == "R_TO_V_REFUSED"
    lean_b = {
        "rows": int(len(group_only)),
        "refusal_rate": float(refused.mean()),
        "false_license_rows": int((~refused).sum()),
        "median_rigidity_index": float(
            group_only["rigidity_rigidity_index"].median()
        ),
        "median_author_all_auc": float(
            group_only["author_all_auc"].median()
        ),
        "median_author_within_group_auc": float(
            group_only["author_within_group_auc"].median()
        ),
        "median_gt_error_ratio": float(
            group_only["e_ratio_oracle"].median()
        ),
        "criteria": {
            "refusal_rate_min": LEAN_B_REFUSAL_RATE,
            "author_all_auc_min": LEAN_B_AUTHOR_AUC,
        },
        "hold": bool(
            refused.mean() >= LEAN_B_REFUSAL_RATE
            and group_only["author_all_auc"].median() >= LEAN_B_AUTHOR_AUC
        ),
    }

    individual = table[table["family"] == "individual"]
    by_noise = individual.groupby("noise").agg(
        mean_margin=("rigidity_spectral_margin", "mean"),
        mean_stability=("rigidity_stability", "mean"),
        mean_index=("rigidity_rigidity_index", "mean"),
        mean_e_rec=("e_rec_oracle", "mean"),
        mean_e_ratio=("e_ratio_oracle", "mean"),
        label_rate=("gt_reconstructable", "mean"),
        licensed_rate=(
            "rigidity_status",
            lambda s: float((s == "R_TO_V_LICENSED").mean()),
        ),
        mean_selected_rank=("rigidity_selected_rank", "mean"),
    ).reset_index()
    log_error = np.log(by_noise["mean_e_rec"].to_numpy())
    log_noise = np.log(by_noise["noise"].to_numpy())
    slopes = np.diff(log_error) / np.diff(log_noise)
    knee_position = int(np.argmax(np.diff(slopes))) + 1
    knee_sigma = float(by_noise["noise"].iloc[knee_position])
    below = np.flatnonzero(
        by_noise["mean_margin"].to_numpy() < GAP_CLOSE_MARGIN
    )
    gap_position = int(below[0]) if len(below) else int(len(by_noise) - 1)
    gap_sigma = float(by_noise["noise"].iloc[gap_position])
    lean_c = {
        "noise_profile": by_noise.to_dict(orient="records"),
        "gap_close_margin": GAP_CLOSE_MARGIN,
        "gap_close_sigma": gap_sigma,
        "error_knee_sigma": knee_sigma,
        "grid_step_distance": int(abs(knee_position - gap_position)),
        "hold": bool(abs(knee_position - gap_position) <= 1),
    }

    licensed = table["rigidity_status"] == "R_TO_V_LICENSED"
    truth = table["gt_reconstructable"].astype(bool)
    confusion = {
        "licensed_and_reconstructable": int((licensed & truth).sum()),
        "licensed_not_reconstructable": int((licensed & ~truth).sum()),
        "refused_but_reconstructable": int((~licensed & truth).sum()),
        "refused_not_reconstructable": int((~licensed & ~truth).sum()),
    }
    holds = [lean_a["hold"], lean_b["hold"], lean_c["hold"]]
    if all(holds):
        status = "M4_D_LEG2_R_TO_V_BRIDGE_LEANS_HELD"
    elif any(holds):
        status = "M4_D_LEG2_R_TO_V_BRIDGE_PARTIAL"
    else:
        status = "M4_D_LEG2_R_TO_V_BRIDGE_LEANS_MISSED"
    return {
        "status": status,
        "pre_fixed": {
            "license_threshold": config.license_threshold,
            "label_margin_ratio": config.label_margin_ratio,
            "rank_cap": config.rank_cap,
            "floor_multiplier": config.floor_multiplier,
            "probe_replicates": config.probe_replicates,
            "probe_floor_fraction": config.probe_floor_fraction,
            "permutation_draws": config.permutation_draws,
            "gap_close_margin": GAP_CLOSE_MARGIN,
        },
        "battery": {
            "rows": int(len(table)),
            "per_family": table["family"].value_counts().to_dict(),
            "noise_grid": list(NOISE_GRID),
            "mixed_epsilons": list(MIXED_EPSILONS),
            "mixed_noise": list(MIXED_NOISE),
        },
        "lean_a_separation": lean_a,
        "lean_b_group_only_refusal": lean_b,
        "lean_c_noise_threshold": lean_c,
        "license_confusion_at_threshold": confusion,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260801)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/m4_d_relation_bridge"),
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    replicates = 4 if args.smoke else args.replicates
    config = RelationBridgeConfig()
    table = run_battery(
        replicates=replicates,
        seed=args.seed,
        config=config,
    )
    decision = adjudicate(table, config=config)
    decision["run"] = {
        "replicates": replicates,
        "seed": args.seed,
        "smoke": bool(args.smoke),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(
        args.output_dir / "relation_bridge_worlds.csv",
        index=False,
    )
    with open(args.output_dir / "decision.json", "w") as handle:
        json.dump(decision, handle, indent=2, default=float)
    print(json.dumps(
        {
            "status": decision["status"],
            "lean_a": decision["lean_a_separation"],
            "lean_b": {
                key: value
                for key, value in decision[
                    "lean_b_group_only_refusal"
                ].items()
                if key != "criteria"
            },
            "lean_c": {
                key: value
                for key, value in decision[
                    "lean_c_noise_threshold"
                ].items()
                if key != "noise_profile"
            },
            "confusion": decision["license_confusion_at_threshold"],
        },
        indent=2,
        default=float,
    ))


if __name__ == "__main__":
    main()
