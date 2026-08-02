"""M4-D leg 13: heteroscedastic calibration of the R->V bridge rank selector.

Registered design (docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md,
Leg 13; ledger M4-D.15, registered before run 2026-08-02):

ANCHOR (reproduce-first gate): Leg 2's homoscedastic battery (seed 20260801,
20 replicates, 600 worlds) is re-run and its persisted headline numbers MUST
reproduce before any new arm is computed -- pooled license AUC .8691,
individual-family AUC .9439, group-only refusal 200/200 -- plus a per-row
comparison against results/m4_d_relation_bridge/relation_bridge_worlds.csv.

WORLD BATTERY (heteroscedastic extension; grids fixed here before the run):
- H1 ``pair_magnitude``: per-pair sd = noise * D2_uv (variance-matched to
  the homoscedastic battery at the same noise level).  individual and
  group_only on the full Leg-2 noise grid x 20; mixed at epsilon .2 x noise
  {.05, .2, .6} x 20.  420 worlds.
- H2 ``author_lognormal``: per-author factors exp(sigma z - sigma^2/2)
  (mean one), per-pair sd = noise * rms(D2) * sqrt(f_u f_v); registered
  sigma grid {0.5, 1.0, 1.5} x noise {.05, .2, .6} x {individual,
  group_only} x 20, plus mixed epsilon .2 at noise .2 x sigma grid x 20.
  420 worlds.
- H3 ``c2_empirical_logit``: the anchor battery's 60 C2-machinery worlds
  (identical seeds -> bit-identical fields and labels), the family where
  Leg 2's auto-rank capped with near-zero margin.

SELECTOR ARMS (one step each, no search; additive in
suica_core/m4_relation_bridge.py, default behavior byte-identical):
- baseline: negative-spectrum floor, selection at 2x floor (Leg 2 verbatim).
- variance_weighted (V1): rank-one row/col per-cell variance model from the
  replicate difference; floor = analytic weighted-null edge
  max_u sqrt(sum_v s_uv^2); same 2x selection multiplier as baseline (the
  floor reduces to the homoscedastic edge, so the baseline convention
  carries over unchanged).
- permutation (V2): within-row permutation null of the replicate
  difference, 199 draws, floor at the null 95th percentile, selection
  multiplier 1.0 (parallel-analysis convention; the empirical quantile is
  already a calibrated positive edge).

Ground-truth labeling rule: Leg 2's ``reconstruction_vs_truth`` at the
oracle rank with within-block permutation, label margin ratio .5 --
reused VERBATIM (same function, same seeds).  License threshold tau = .5
unchanged.  The stress-stability probe is unchanged in all arms: the arms
differ ONLY in the rank-selection floor.

LEANS (registered): (a) baseline license AUC <= .80 pooled over the
heteroscedastic families (H1+H2+H3); (b) >= 1 variant restores AUC >= .88
while keeping the designed-null (Leg 2 group-only, 200 worlds) refusal
>= 199/200; (c) the winning variant produces non-cap rank with positive
margin in >= 3/4 of baseline-capped C2 cases.  PIVOT-IF no variant restores
AUC without breaking group-only refusal -> the tau-grid refusal-safety vs
sensitivity trade-off frontier is recorded as the bridge's documented
operating curve (a valid deliverable).

Outputs (default results/m4_d_bridge_hetero/):
- bridge_hetero_rows.csv       : one row per world x arm (anchor + hetero)
- bridge_hetero_tau_frontier.csv : per-arm tau-grid operating table
- decision.json                : anchor gate, per-lean adjudication, tables
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Iterator

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from suica_core.m4_relation_bridge import (  # noqa: E402
    RelationBridgeConfig,
    c2_machinery_relation_world,
    evaluate_relation_world,
    heteroscedastic_relation_world,
    planted_relation_world,
    reconstruction_vs_truth,
    rigidity_report,
)


def _load_leg2_module():
    spec = importlib.util.spec_from_file_location(
        "run_suica_m4_d_relation_bridge_leg2",
        REPO / "scripts" / "run_suica_m4_d_relation_bridge_leg2.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LEG2 = _load_leg2_module()

# ---- registered constants (fixed before the run) -------------------------
ARMS = ("baseline", "variance_weighted", "permutation")
H1_NOISE_GRID = LEG2.NOISE_GRID                     # full Leg-2 grid
H1_MIXED_EPSILON = 0.2
H1_MIXED_NOISE = (0.05, 0.2, 0.6)
H2_SIGMA_GRID = (0.5, 1.0, 1.5)                     # registered sigma grid
H2_NOISE_GRID = (0.05, 0.2, 0.6)
H2_MIXED_EPSILON = 0.2
H2_MIXED_NOISE = 0.2
PERMUTATION_DRAWS = 199
PERMUTATION_QUANTILE = 0.95
LEAN_A_MAX_AUC = 0.80
LEAN_B_MIN_AUC = 0.88
LEAN_B_MIN_REFUSALS = 199
LEAN_C_FRACTION = 0.75
TAU_GRID = tuple(np.round(np.arange(0.025, 1.0, 0.025), 3))
# persisted Leg-2 headline numbers (the reproduce-first gate)
ANCHOR_POOLED_AUC = 0.8691390374980287
ANCHOR_INDIVIDUAL_AUC = 0.9438683127572017
ANCHOR_REFUSAL_ROWS = 200
HETERO_MECHANISMS = (
    "pair_magnitude",
    "author_lognormal",
    "c2_empirical_logit",
)


def iter_anchor_worlds(
    replicates: int,
    seed: int,
) -> Iterator[tuple[dict[str, Any], int, int]]:
    """Reproduce leg 2's run_battery world stream (identical seed order)."""
    index = 0

    def next_seed() -> int:
        nonlocal index
        index += 1
        return seed + 7919 * index

    for family in ("individual", "group_only"):
        for noise in LEG2.NOISE_GRID:
            for replicate in range(replicates):
                world_seed = next_seed()
                yield (
                    planted_relation_world(
                        family, noise=noise, seed=world_seed
                    ),
                    world_seed,
                    replicate,
                )
    for epsilon in LEG2.MIXED_EPSILONS:
        for noise in LEG2.MIXED_NOISE:
            for replicate in range(replicates):
                world_seed = next_seed()
                yield (
                    planted_relation_world(
                        "mixed",
                        noise=noise,
                        epsilon=epsilon,
                        seed=world_seed,
                    ),
                    world_seed,
                    replicate,
                )
    for world_kind, epsilon in LEG2.C2_SETTINGS:
        for replicate in range(replicates):
            world_seed = next_seed()
            yield (
                c2_machinery_relation_world(
                    world_kind, epsilon=epsilon, seed=world_seed
                ),
                world_seed,
                replicate,
            )


def iter_hetero_worlds(
    replicates: int,
    seed: int,
) -> Iterator[tuple[dict[str, Any], int, int]]:
    """H1 + H2 battery stream (grids registered in the module docstring)."""
    index = 0

    def next_seed() -> int:
        nonlocal index
        index += 1
        return seed + 7919 * index

    for family in ("individual", "group_only"):
        for noise in H1_NOISE_GRID:
            for replicate in range(replicates):
                world_seed = next_seed()
                yield (
                    heteroscedastic_relation_world(
                        family,
                        mechanism="pair_magnitude",
                        noise=noise,
                        seed=world_seed,
                    ),
                    world_seed,
                    replicate,
                )
    for noise in H1_MIXED_NOISE:
        for replicate in range(replicates):
            world_seed = next_seed()
            yield (
                heteroscedastic_relation_world(
                    "mixed",
                    mechanism="pair_magnitude",
                    noise=noise,
                    epsilon=H1_MIXED_EPSILON,
                    seed=world_seed,
                ),
                world_seed,
                replicate,
            )
    for sigma in H2_SIGMA_GRID:
        for family in ("individual", "group_only"):
            for noise in H2_NOISE_GRID:
                for replicate in range(replicates):
                    world_seed = next_seed()
                    yield (
                        heteroscedastic_relation_world(
                            family,
                            mechanism="author_lognormal",
                            noise=noise,
                            author_sigma=sigma,
                            seed=world_seed,
                        ),
                        world_seed,
                        replicate,
                    )
        for replicate in range(replicates):
            world_seed = next_seed()
            yield (
                heteroscedastic_relation_world(
                    "mixed",
                    mechanism="author_lognormal",
                    noise=H2_MIXED_NOISE,
                    author_sigma=sigma,
                    epsilon=H2_MIXED_EPSILON,
                    seed=world_seed,
                ),
                world_seed,
                replicate,
            )


def variant_record(
    world: dict[str, Any],
    arm: str,
    world_seed: int,
    config: RelationBridgeConfig,
) -> dict[str, Any]:
    """Variant rigidity + selected-rank reconstruction for one world."""
    field = world["fields"][0]
    rigidity = rigidity_report(
        field,
        config=config,
        seed=world_seed + 1,
        selector=arm,
        replicate_field=world["fields"][1],
        permutation_draws=PERMUTATION_DRAWS,
        permutation_quantile=PERMUTATION_QUANTILE,
        permutation_seed=world_seed + 13,
    )
    selected = reconstruction_vs_truth(
        field,
        world["truth"],
        rank=rigidity["selected_rank"],
        group_labels=world["group_labels"],
        config=config,
        seed=world_seed + 2,
    )
    return {
        "selected_rank": rigidity["selected_rank"],
        "auto_rank": rigidity["auto_rank"],
        "noise_floor": rigidity["noise_floor"],
        "floor_multiplier_used": rigidity["floor_multiplier_used"],
        "lambda_rank": rigidity["lambda_rank"],
        "lambda_next": rigidity["lambda_next"],
        "spectral_margin": rigidity["spectral_margin"],
        "status": rigidity["status"],
        "refusal_reason": rigidity["refusal_reason"],
        "stability": rigidity["stability"],
        "dispersion_ratio": rigidity["dispersion_ratio"],
        "probe_sigma": rigidity["probe_sigma"],
        "rigidity_index": rigidity["rigidity_index"],
        "e_rec_selected": selected["reconstruction_error"],
        "e_ratio_selected": selected["error_ratio"],
    }


def baseline_record_from_row(row: dict[str, Any]) -> dict[str, Any]:
    """Reshape an evaluate_relation_world row into the long-arm schema."""
    return {
        "selected_rank": row["rigidity_selected_rank"],
        "auto_rank": row["rigidity_auto_rank"],
        "noise_floor": row["rigidity_noise_floor"],
        "floor_multiplier_used": 2.0,
        "lambda_rank": row["rigidity_lambda_rank"],
        "lambda_next": row["rigidity_lambda_next"],
        "spectral_margin": row["rigidity_spectral_margin"],
        "status": row["rigidity_status"],
        "refusal_reason": row["rigidity_refusal_reason"],
        "stability": row["rigidity_stability"],
        "dispersion_ratio": row["rigidity_dispersion_ratio"],
        "probe_sigma": row["rigidity_probe_sigma"],
        "rigidity_index": row["rigidity_rigidity_index"],
        "e_rec_selected": row["e_rec_selected"],
        "e_ratio_selected": row["e_ratio_selected"],
    }


def shared_columns(
    row: dict[str, Any],
    *,
    battery: str,
    mechanism: str,
    author_sigma: float,
    world_seed: int,
    replicate: int,
) -> dict[str, Any]:
    return {
        "battery": battery,
        "family": row["family"],
        "mechanism": mechanism,
        "author_sigma": author_sigma,
        "noise": row["noise"],
        "epsilon": row["epsilon"],
        "replicate": replicate,
        "seed": world_seed,
        "authors": row["authors"],
        "oracle_rank": row["oracle_rank"],
        "individual_share": row["individual_share"],
        "gt_reconstructable": row["gt_reconstructable"],
        "e_rec_oracle": row["e_rec_oracle"],
        "e_perm_median": row["e_perm_median"],
        "e_ratio_oracle": row["e_ratio_oracle"],
        "author_all_auc": row["author_all_auc"],
        "author_within_group_auc": row["author_within_group_auc"],
        "group_auc": row["group_auc"],
    }


def reproduce_anchor(
    config: RelationBridgeConfig,
    *,
    replicates: int,
    smoke: bool,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    table = LEG2.run_battery(
        replicates=replicates, seed=20260801, config=config
    )
    decision = LEG2.adjudicate(table, config=config)
    gate: dict[str, Any] = {
        "pooled_auc": decision["lean_a_separation"]["pooled_auc"],
        "individual_auc": decision["lean_a_separation"]["per_family_auc"][
            "individual"
        ],
        "group_only_rows": decision["lean_b_group_only_refusal"]["rows"],
        "group_only_refusal_rate": decision["lean_b_group_only_refusal"][
            "refusal_rate"
        ],
        "false_license_rows": decision["lean_b_group_only_refusal"][
            "false_license_rows"
        ],
    }
    if smoke:
        gate["checked"] = False
        gate["note"] = "smoke run: persisted-value asserts skipped"
        return table, gate
    persisted = pd.read_csv(
        REPO / "results" / "m4_d_relation_bridge" / "relation_bridge_worlds.csv"
    )
    if len(persisted) != len(table):
        raise AssertionError("anchor row count mismatch vs persisted CSV")
    if not (persisted["seed"].to_numpy() == table["seed"].to_numpy()).all():
        raise AssertionError("anchor seed sequence mismatch vs persisted CSV")
    index_diff = float(
        np.max(
            np.abs(
                persisted["rigidity_rigidity_index"].to_numpy()
                - table["rigidity_rigidity_index"].to_numpy()
            )
        )
    )
    ratio_diff = float(
        np.max(
            np.abs(
                persisted["e_ratio_oracle"].to_numpy()
                - table["e_ratio_oracle"].to_numpy()
            )
        )
    )
    checks = {
        "pooled_auc_diff": abs(gate["pooled_auc"] - ANCHOR_POOLED_AUC),
        "individual_auc_diff": abs(
            gate["individual_auc"] - ANCHOR_INDIVIDUAL_AUC
        ),
        "max_abs_index_diff_vs_persisted": index_diff,
        "max_abs_e_ratio_diff_vs_persisted": ratio_diff,
    }
    gate.update(checks)
    if checks["pooled_auc_diff"] > 1e-9:
        raise AssertionError("anchor pooled AUC failed to reproduce")
    if checks["individual_auc_diff"] > 1e-9:
        raise AssertionError("anchor individual-family AUC failed to reproduce")
    if gate["group_only_rows"] != ANCHOR_REFUSAL_ROWS:
        raise AssertionError("anchor designed-null battery size mismatch")
    if gate["group_only_refusal_rate"] != 1.0 or gate["false_license_rows"]:
        raise AssertionError("anchor group-only refusal failed to reproduce")
    if index_diff > 1e-9 or ratio_diff > 1e-9:
        raise AssertionError("anchor per-row values failed to reproduce")
    gate["checked"] = True
    return table, gate


def family_arm_summary(rows: pd.DataFrame, rank_cap: int) -> list[dict]:
    summary = []
    for (family, arm), block in rows.groupby(["family", "arm"], sort=True):
        labels = block["gt_reconstructable"].astype(int)
        auc = (
            float(roc_auc_score(labels, block["rigidity_index"]))
            if labels.nunique() == 2
            else float("nan")
        )
        summary.append({
            "family": family,
            "arm": arm,
            "rows": int(len(block)),
            "label_rate": float(labels.mean()),
            "license_auc": auc,
            "refusal_rate": float(
                (block["status"] == "R_TO_V_REFUSED").mean()
            ),
            "licensed_rate": float(
                (block["status"] == "R_TO_V_LICENSED").mean()
            ),
            "mean_selected_rank": float(block["selected_rank"].mean()),
            "rank_exact_rate": float(
                (block["selected_rank"] == block["oracle_rank"]).mean()
            ),
            "mean_abs_rank_error": float(
                (block["selected_rank"] - block["oracle_rank"]).abs().mean()
            ),
            "cap_hit_rate": float(
                (block["selected_rank"] == rank_cap).mean()
            ),
            "zero_rank_rate": float((block["selected_rank"] == 0).mean()),
            "mean_margin": float(block["spectral_margin"].mean()),
            "median_index": float(block["rigidity_index"].median()),
        })
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260802)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/m4_d_bridge_hetero"),
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    replicates = 4 if args.smoke else args.replicates
    config = RelationBridgeConfig()
    started = time.time()

    # ---- phase A: anchor reproduce-first gate ---------------------------
    anchor_table, anchor_gate = reproduce_anchor(
        config, replicates=replicates, smoke=args.smoke
    )
    print(json.dumps({"anchor_gate": anchor_gate}, indent=2, default=float))

    # ---- phase B: anchor worlds under the calibrated variants -----------
    long_rows: list[dict[str, Any]] = []
    anchor_rows = anchor_table.to_dict(orient="records")
    stream = list(iter_anchor_worlds(replicates, 20260801))
    if [seed for _, seed, _ in stream] != [
        int(row["seed"]) for row in anchor_rows
    ]:
        raise AssertionError("anchor world stream diverged from phase A")
    for (world, world_seed, replicate), row in zip(stream, anchor_rows):
        battery = (
            "anchor_c2" if str(row["family"]).startswith("c2_") else "anchor"
        )
        mechanism = (
            "c2_empirical_logit"
            if battery == "anchor_c2"
            else "homoscedastic"
        )
        shared = shared_columns(
            row,
            battery=battery,
            mechanism=mechanism,
            author_sigma=float("nan"),
            world_seed=world_seed,
            replicate=replicate,
        )
        long_rows.append(
            {**shared, "arm": "baseline", **baseline_record_from_row(row)}
        )
        for arm in ARMS[1:]:
            long_rows.append({
                **shared,
                "arm": arm,
                **variant_record(world, arm, world_seed, config),
            })
    print(
        f"[leg13] anchor arms done: {len(long_rows)} rows "
        f"({time.time() - started:.1f}s)"
    )

    # ---- phase C: heteroscedastic battery (H1 + H2), all arms -----------
    for world, world_seed, replicate in iter_hetero_worlds(
        replicates, args.seed
    ):
        row = evaluate_relation_world(
            world, config=config, seed=world_seed + 1
        )
        shared = shared_columns(
            {**row},
            battery="hetero",
            mechanism=world["mechanism"],
            author_sigma=world["author_sigma"],
            world_seed=world_seed,
            replicate=replicate,
        )
        long_rows.append(
            {**shared, "arm": "baseline", **baseline_record_from_row(row)}
        )
        for arm in ARMS[1:]:
            long_rows.append({
                **shared,
                "arm": arm,
                **variant_record(world, arm, world_seed, config),
            })
    rows = pd.DataFrame(long_rows)
    print(
        f"[leg13] hetero battery done: {len(rows)} total rows "
        f"({time.time() - started:.1f}s)"
    )

    # ---- phase D: adjudication ------------------------------------------
    hetero_pool = rows[rows["mechanism"].isin(HETERO_MECHANISMS)]
    designed_null = rows[
        ((rows["battery"] == "anchor") & (rows["family"] == "group_only"))
        | (
            (rows["battery"] == "anchor_c2")
            & (rows["family"] == "c2_group_only")
        )
    ]
    hetero_null = rows[
        rows["family"].isin(["h1_group_only", "h2_group_only"])
    ]

    def pool_auc(block: pd.DataFrame) -> float:
        labels = block["gt_reconstructable"].astype(int)
        if labels.nunique() < 2:
            return float("nan")
        return float(roc_auc_score(labels, block["rigidity_index"]))

    arm_stats: dict[str, dict[str, Any]] = {}
    for arm in ARMS:
        pool = hetero_pool[hetero_pool["arm"] == arm]
        null_block = designed_null[designed_null["arm"] == arm]
        hetero_null_block = hetero_null[hetero_null["arm"] == arm]
        additive = pool[
            pool["mechanism"].isin(["pair_magnitude", "author_lognormal"])
        ]
        anchor_block = rows[
            (rows["arm"] == arm)
            & (rows["battery"].isin(["anchor", "anchor_c2"]))
        ]
        arm_stats[arm] = {
            "hetero_pooled_auc": pool_auc(pool),
            "hetero_h1_h2_auc": pool_auc(additive),
            "per_mechanism_auc": {
                mechanism: pool_auc(
                    pool[pool["mechanism"] == mechanism]
                )
                for mechanism in HETERO_MECHANISMS
            },
            "designed_null_refusals": int(
                (null_block["status"] == "R_TO_V_REFUSED").sum()
            ),
            "designed_null_rows": int(len(null_block)),
            "designed_null_max_index": float(
                null_block["rigidity_index"].max()
            ),
            "hetero_group_only_refusals": int(
                (hetero_null_block["status"] == "R_TO_V_REFUSED").sum()
            ),
            "hetero_group_only_rows": int(len(hetero_null_block)),
            "anchor_pooled_auc": pool_auc(anchor_block),
            "anchor_individual_auc": pool_auc(
                anchor_block[anchor_block["family"] == "individual"]
            ),
        }

    lean_a = {
        "baseline_hetero_auc": arm_stats["baseline"]["hetero_pooled_auc"],
        "baseline_h1_h2_auc": arm_stats["baseline"]["hetero_h1_h2_auc"],
        "per_mechanism": arm_stats["baseline"]["per_mechanism_auc"],
        "threshold": LEAN_A_MAX_AUC,
        "hold": bool(
            arm_stats["baseline"]["hetero_pooled_auc"] <= LEAN_A_MAX_AUC
        ),
    }

    variant_verdicts = {}
    for arm in ARMS[1:]:
        stats = arm_stats[arm]
        variant_verdicts[arm] = {
            "hetero_auc": stats["hetero_pooled_auc"],
            "designed_null_refusals": stats["designed_null_refusals"],
            "restores_auc": bool(
                stats["hetero_pooled_auc"] >= LEAN_B_MIN_AUC
            ),
            "refusal_safe": bool(
                stats["designed_null_refusals"] >= LEAN_B_MIN_REFUSALS
            ),
            "qualifies": bool(
                stats["hetero_pooled_auc"] >= LEAN_B_MIN_AUC
                and stats["designed_null_refusals"] >= LEAN_B_MIN_REFUSALS
            ),
        }
    lean_b = {
        "criteria": {
            "auc_min": LEAN_B_MIN_AUC,
            "refusals_min": LEAN_B_MIN_REFUSALS,
        },
        "variants": variant_verdicts,
        "hold": bool(
            any(v["qualifies"] for v in variant_verdicts.values())
        ),
    }
    refusal_safe = [
        arm for arm in ARMS[1:] if variant_verdicts[arm]["refusal_safe"]
    ]
    winner = (
        max(
            refusal_safe,
            key=lambda arm: arm_stats[arm]["hetero_pooled_auc"],
        )
        if refusal_safe
        else None
    )

    baseline_c2 = rows[
        (rows["battery"] == "anchor_c2") & (rows["arm"] == "baseline")
    ]
    capped_seeds = baseline_c2[
        baseline_c2["auto_rank"] == config.rank_cap
    ]["seed"].tolist()
    c2_cap: dict[str, Any] = {
        "baseline_capped_cases": len(capped_seeds),
        "baseline_cap_rate": float(
            (baseline_c2["auto_rank"] == config.rank_cap).mean()
        ),
        "per_arm": {},
    }
    for arm in ARMS[1:]:
        block = rows[
            (rows["battery"] == "anchor_c2")
            & (rows["arm"] == arm)
            & (rows["seed"].isin(capped_seeds))
        ]
        uncapped = (
            (block["selected_rank"] < config.rank_cap)
            & (block["spectral_margin"] > 0.0)
        )
        c2_cap["per_arm"][arm] = {
            "non_cap_positive_margin": int(uncapped.sum()),
            "cap_hit": int(
                (block["selected_rank"] == config.rank_cap).sum()
            ),
            "zero_rank": int((block["selected_rank"] == 0).sum()),
            "mean_selected_rank": float(block["selected_rank"].mean()),
            "median_margin": float(block["spectral_margin"].median()),
            "min_margin": float(block["spectral_margin"].min()),
        }
    needed = int(np.ceil(LEAN_C_FRACTION * max(len(capped_seeds), 1)))
    lean_c = {
        "winning_variant": winner,
        "baseline_capped_cases": len(capped_seeds),
        "needed": needed,
        "achieved": (
            c2_cap["per_arm"][winner]["non_cap_positive_margin"]
            if winner
            else None
        ),
        "hold": bool(
            winner is not None
            and c2_cap["per_arm"][winner]["non_cap_positive_margin"]
            >= needed
            and len(capped_seeds) > 0
        ),
    }

    pivot_fired = not lean_b["hold"]
    frontier_rows = []
    hetero_positive = hetero_pool[
        hetero_pool["gt_reconstructable"].astype(bool)
    ]
    hetero_negative = hetero_pool[
        ~hetero_pool["gt_reconstructable"].astype(bool)
    ]
    for arm in ARMS:
        null_idx = designed_null[designed_null["arm"] == arm][
            "rigidity_index"
        ].to_numpy()
        pos_idx = hetero_positive[hetero_positive["arm"] == arm][
            "rigidity_index"
        ].to_numpy()
        neg_idx = hetero_negative[hetero_negative["arm"] == arm][
            "rigidity_index"
        ].to_numpy()
        for tau in TAU_GRID:
            frontier_rows.append({
                "arm": arm,
                "tau": float(tau),
                "designed_null_false_licenses": int(
                    (null_idx >= tau).sum()
                ),
                "designed_null_rows": int(len(null_idx)),
                "hetero_sensitivity": float((pos_idx >= tau).mean()),
                "hetero_false_license_rate": float(
                    (neg_idx >= tau).mean()
                ),
            })
    frontier = pd.DataFrame(frontier_rows)

    holds = [lean_a["hold"], lean_b["hold"], lean_c["hold"]]
    if pivot_fired:
        status = "M4_D_LEG13_BRIDGE_HETERO_PIVOT_TRADEOFF_FRONTIER"
    elif all(holds):
        status = "M4_D_LEG13_BRIDGE_HETERO_CALIBRATION_LEANS_HELD"
    elif any(holds):
        status = "M4_D_LEG13_BRIDGE_HETERO_CALIBRATION_PARTIAL"
    else:
        status = "M4_D_LEG13_BRIDGE_HETERO_CALIBRATION_LEANS_MISSED"

    decision = {
        "status": status,
        "pre_fixed": {
            "license_threshold": config.license_threshold,
            "label_margin_ratio": config.label_margin_ratio,
            "rank_cap": config.rank_cap,
            "floor_multiplier_baseline_and_v1": config.floor_multiplier,
            "floor_multiplier_v2": 1.0,
            "permutation_draws": PERMUTATION_DRAWS,
            "permutation_quantile": PERMUTATION_QUANTILE,
            "h1_noise_grid": list(H1_NOISE_GRID),
            "h1_mixed": {
                "epsilon": H1_MIXED_EPSILON,
                "noise": list(H1_MIXED_NOISE),
            },
            "h2_sigma_grid": list(H2_SIGMA_GRID),
            "h2_noise_grid": list(H2_NOISE_GRID),
            "h2_mixed": {
                "epsilon": H2_MIXED_EPSILON,
                "noise": H2_MIXED_NOISE,
            },
            "tau_grid": [float(t) for t in TAU_GRID],
            "lean_thresholds": {
                "a_max_auc": LEAN_A_MAX_AUC,
                "b_min_auc": LEAN_B_MIN_AUC,
                "b_min_refusals": LEAN_B_MIN_REFUSALS,
                "c_fraction": LEAN_C_FRACTION,
            },
        },
        "anchor_reproduction": anchor_gate,
        "battery": {
            "total_rows": int(len(rows)),
            "worlds": int(len(rows)) // len(ARMS),
            "per_battery": rows[rows["arm"] == "baseline"][
                "battery"
            ].value_counts().to_dict(),
            "per_family": rows[rows["arm"] == "baseline"][
                "family"
            ].value_counts().to_dict(),
            "hetero_pool_rows_per_arm": int(
                len(hetero_pool) // len(ARMS)
            ),
            "hetero_pool_label_rate": float(
                hetero_pool[hetero_pool["arm"] == "baseline"][
                    "gt_reconstructable"
                ].mean()
            ),
        },
        "arm_stats": arm_stats,
        "lean_a_problem_is_real": lean_a,
        "lean_b_calibrated_restoration": lean_b,
        "lean_c_c2_uncap": lean_c,
        "c2_cap_analysis": c2_cap,
        "pivot": {
            "fired": pivot_fired,
            "definition": (
                "no variant restores AUC >= .88 without breaking the "
                "designed-null refusal >= 199/200"
            ),
            "frontier_csv": "bridge_hetero_tau_frontier.csv",
        },
        "family_arm_summary": family_arm_summary(rows, config.rank_cap),
        "run": {
            "replicates": replicates,
            "hetero_seed": args.seed,
            "anchor_seed": 20260801,
            "smoke": bool(args.smoke),
            "runtime_seconds": float(time.time() - started),
        },
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    rows.to_csv(args.output_dir / "bridge_hetero_rows.csv", index=False)
    frontier.to_csv(
        args.output_dir / "bridge_hetero_tau_frontier.csv", index=False
    )
    with open(args.output_dir / "decision.json", "w") as handle:
        json.dump(decision, handle, indent=2, default=float)
    print(json.dumps(
        {
            "status": status,
            "lean_a": lean_a,
            "lean_b": lean_b,
            "lean_c": lean_c,
            "c2_cap_analysis": c2_cap,
            "arm_stats": arm_stats,
        },
        indent=2,
        default=float,
    ))


if __name__ == "__main__":
    main()
