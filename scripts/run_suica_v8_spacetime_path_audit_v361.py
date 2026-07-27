#!/usr/bin/env python3
"""Run the post-seal V3.6.1 path-level scope correction."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_suica_v8_incidence_incremental as base  # noqa: E402
from suica_core.v8_spacetime_junction_flow import (  # noqa: E402
    _branch_estimates,
    JunctionFlowSpec,
    simulate_junction_world,
)
from suica_core.v8_spacetime_path_audit import (  # noqa: E402
    conditional_path_information_permutation,
    heldout_local_route_accuracy,
    path_information,
    summarize_path_audit,
)

POLICIES = ("pass_through", "random_branch", "cue_guided")


def _static_predictions(
    frame: pd.DataFrame,
    labels: np.ndarray,
) -> np.ndarray:
    columns = [column for column in frame if column.startswith("static_")]
    features = frame[columns].to_numpy(dtype=float)
    groups = frame["repetition"].to_numpy()
    return cross_val_predict(
        make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=2_000),
        ),
        features,
        labels,
        groups=groups,
        cv=GroupKFold(n_splits=5),
        method="predict",
    )


def _static_audit(
    frame: pd.DataFrame,
    *,
    seed: int,
    permutations: int,
    bootstraps: int,
) -> dict[str, Any]:
    labels = frame["policy"].to_numpy()
    groups = frame["repetition"].to_numpy()
    prediction = _static_predictions(frame, labels)
    observed = float(np.mean(prediction == labels))
    rng = np.random.default_rng(seed)
    unique_groups = np.unique(groups)
    draws = []
    for _ in range(bootstraps):
        sampled = rng.choice(
            unique_groups,
            size=len(unique_groups),
            replace=True,
        )
        correct = []
        for group in sampled:
            index = groups == group
            correct.extend(prediction[index] == labels[index])
        draws.append(float(np.mean(correct)))

    null = []
    for _ in range(permutations):
        shuffled = labels.copy()
        for group in unique_groups:
            index = np.flatnonzero(groups == group)
            shuffled[index] = rng.permutation(shuffled[index])
        permuted_prediction = _static_predictions(frame, shuffled)
        null.append(float(np.mean(permuted_prediction == shuffled)))
    null_array = np.asarray(null)
    return {
        "accuracy": observed,
        "cluster_bootstrap_ci95": [
            float(np.quantile(draws, 0.025)),
            float(np.quantile(draws, 0.975)),
        ],
        "permutation_null_mean": float(null_array.mean()),
        "permutation_p_greater": float(
            (1 + np.count_nonzero(null_array >= observed))
            / (permutations + 1)
        ),
        "permutations": permutations,
        "bootstraps": bootstraps,
    }


def _path_audit(
    config: dict[str, Any],
    *,
    repetitions: int,
    permutations: int,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, float]]]:
    spec = JunctionFlowSpec(
        authors=int(config["authors"]),
        groups=int(config["groups"]),
        branches=int(config["branches"]),
        depth=int(config["depth"]),
        episodes=int(config["episodes"]),
        views=int(config["views"]),
        ambient=int(config["ambient"]),
        node_radius=float(config["node_radius"]),
        node_spread=float(config["node_spread"]),
        near_miss_spread=float(config["near_miss_spread"]),
        segment_length=float(config["segment_length"]),
        noise_sd=float(config["noise_sd"]),
        time_weight=float(config["time_weight"]),
        minimum_node_persistence=float(
            config["minimum_node_persistence"]
        ),
        minimum_time_tau=float(config["minimum_time_tau"]),
        minimum_view_ari=float(config["minimum_view_ari"]),
        target_information_threshold=float(
            config["target_information_threshold"]
        ),
        nontarget_information_threshold=float(
            config["nontarget_information_threshold"]
        ),
        residual_entropy_threshold=float(
            config["residual_entropy_threshold"]
        ),
    )
    rows = []
    for repetition in range(repetitions):
        seed = int(config["seed"]) + 50_000_000 + repetition
        for policy in POLICIES:
            sample = simulate_junction_world(
                seed=seed,
                policy=policy,
                spec=spec,
            )
            branch = _branch_estimates(
                sample["observations"],
                sample["cues"],
                sample["labels"],
                spec=spec,
            )
            information = path_information(
                branch["outgoing_labels"][0],
                sample["cues"],
                branch["incoming_labels"][0],
                sample["labels"],
                branches=spec.branches,
            )
            heldout = heldout_local_route_accuracy(
                branch["outgoing_labels"][0],
                sample["cues"],
                branch["incoming_labels"][0],
                sample["labels"],
                branches=spec.branches,
            )
            corrected = conditional_path_information_permutation(
                branch["outgoing_labels"][0],
                sample["cues"],
                branch["incoming_labels"][0],
                sample["labels"],
                branches=spec.branches,
                seed=seed + 110_003,
                permutations=permutations,
            )
            rows.append({
                "policy": policy,
                "repetition": repetition,
                "seed": seed,
                **information,
                **heldout,
                **corrected,
            })
    return rows, summarize_path_audit(rows)


def main() -> int:
    """Run static-null and whole-path scope diagnostics."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_spacetime_junction_flow_v36.json",
    )
    parser.add_argument(
        "--frozen-results",
        type=Path,
        default=(
            ROOT
            / "results/v8_spacetime_junction_flow"
            / "v36_final_20260726"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=(
            ROOT
            / "results/v8_spacetime_junction_flow"
            / "v361_posthoc_scope_audit_20260726"
        ),
    )
    parser.add_argument("--repetitions", type=int, default=200)
    parser.add_argument("--permutations", type=int, default=999)
    parser.add_argument("--bootstraps", type=int, default=2_000)
    parser.add_argument("--path-permutations", type=int, default=99)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    primary = pd.read_csv(
        args.frozen_results / "confirmation_primary_metrics.csv"
    )
    static = _static_audit(
        primary,
        seed=int(config["seed"]) + 90_001,
        permutations=args.permutations,
        bootstraps=args.bootstraps,
    )
    rows, path_summary = _path_audit(
        config,
        repetitions=args.repetitions,
        permutations=args.path_permutations,
    )
    decision = {
        "status": "V8_SPACETIME_JUNCTION_FLOW_V361_SCOPE_CORRECTION_COMPLETE",
        "static_marginal_audit": static,
        "path_summary": path_summary,
        "interpretation": (
            "Whole-path metrics characterize the registered deterministic "
            "and random generators. They do not establish planning, "
            "intelligence, personality, or real-text routing."
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(
        args.output_dir / "path_metrics.csv",
        index=False,
    )
    base._write_json(args.output_dir / "decision.json", decision)  # noqa: SLF001
    (args.output_dir / "report.md").write_text(
        "# V3.6.1 Post-seal Scope Correction\n\n"
        f"Decision: `{decision['status']}`\n\n"
        "```json\n"
        f"{json.dumps(decision, indent=2)}\n"
        "```\n",
        encoding="utf-8",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
