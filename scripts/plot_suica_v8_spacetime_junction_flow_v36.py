#!/usr/bin/env python3
"""Plot the frozen V3.6 spacetime junction-flow confirmation summary."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """Render information, tree, and time-axis diagnostics."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--decision",
        type=Path,
        default=(
            ROOT
            / "results/v8_spacetime_junction_flow"
            / "v36_final_20260726/decision.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            ROOT
            / "reports/figures"
            / "v8_spacetime_junction_flow_v36.png"
        ),
    )
    parser.add_argument(
        "--path-audit",
        type=Path,
        default=(
            ROOT
            / "results/v8_spacetime_junction_flow"
            / "v361_posthoc_scope_audit_r2_20260726/decision.json"
        ),
    )
    args = parser.parse_args()
    decision = json.loads(args.decision.read_text(encoding="utf-8"))
    path_audit = json.loads(args.path_audit.read_text(encoding="utf-8"))
    summaries = {
        row["policy"]: row
        for row in decision["summary"]["policy_summary"]
    }
    policies = ["pass_through", "random_branch", "cue_guided"]
    labels = ["Pass-through", "Random branch", "Cue-guided"]
    colors = ["#355c7d", "#c06c50", "#2a9d8f"]
    x = np.arange(len(policies))

    figure, axes = plt.subplots(1, 3, figsize=(14.5, 4.7))
    information = [
        [summaries[item]["target_information_minimum"] for item in policies],
        [
            summaries[item]["nontarget_information_maximum"]
            for item in policies
        ],
    ]
    width = 0.34
    axes[0].bar(
        x - width / 2,
        information[0],
        width,
        color=colors,
        label="Registered target channel",
    )
    axes[0].bar(
        x + width / 2,
        information[1],
        width,
        color=colors,
        alpha=0.28,
        hatch="//",
        label="Largest non-target channel",
    )
    axes[0].set_title("Transition information")
    axes[0].set_ylim(0, 1.08)
    axes[0].set_ylabel("Normalized information")
    axes[0].legend(frameon=False, fontsize=8)

    effective = [
        summaries[item]["effective_leaf_fraction_mean"]
        for item in policies
    ]
    heldout = [
        path_audit["path_summary"][item][
            "heldout_exact_path_accuracy_mean"
        ]
        for item in policies
    ]
    corrected_mi = [
        path_audit["path_summary"][item][
            "path_conditional_mi_bias_adjusted_mean"
        ]
        for item in policies
    ]
    axes[1].bar(
        x - width,
        effective,
        width,
        color=colors,
        alpha=0.38,
        label="Effective leaf fraction",
    )
    axes[1].bar(
        x,
        heldout,
        width,
        color=colors,
        alpha=0.68,
        label="Held-out exact-path accuracy",
    )
    axes[1].bar(
        x + width,
        corrected_mi,
        width,
        color=colors,
        label="Bias-adjusted cue-path MI",
    )
    axes[1].set_title("Depth-3 ternary tree")
    axes[1].set_ylim(0, 1.08)
    axes[1].set_ylabel("Fraction")
    axes[1].legend(frameon=False, fontsize=8)

    x_only = [
        summaries[item]["x_only_stage_accuracy_maximum"]
        for item in policies
    ]
    spacetime = [
        summaries[item]["spacetime_stage_accuracy_minimum"]
        for item in policies
    ]
    axes[2].bar(
        x - width / 2,
        x_only,
        width,
        color="#9aa0a6",
        label="Representation space X",
    )
    axes[2].bar(
        x + width / 2,
        spacetime,
        width,
        color=colors,
        label="Spacetime X x T",
    )
    axes[2].axhline(
        1 / 3,
        color="#222222",
        linestyle="--",
        linewidth=1,
        label="Three-stage chance",
    )
    axes[2].set_title("Repeated-node stage recovery")
    axes[2].set_ylim(0, 1.08)
    axes[2].set_ylabel("Accuracy")
    axes[2].legend(frameon=False, fontsize=8)

    for axis in axes:
        axis.set_xticks(x, labels, rotation=12, ha="right")
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", alpha=0.18)
    figure.suptitle(
        "SUICA V3.6: geometry permits paths; transition kernels select them",
        fontsize=14,
        fontweight="bold",
    )
    figure.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=220, bbox_inches="tight")
    figure.savefig(args.output.with_suffix(".svg"), bbox_inches="tight")
    plt.close(figure)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
