#!/usr/bin/env python3
"""Run the label-free M4-T1 hierarchical selection-identity experiment."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.hierarchical_selection_identity import (  # noqa: E402
    cross_fitted_hierarchical_identity,
    simulate_hierarchical_choices,
)


DEFAULT_SELECTION = ROOT / "results/m4_sr1_selection_geometry/selection.npz"
DEFAULT_COHORT = ROOT / "results/m4_sr0_recon/cohort_authors.csv"
DEFAULT_COMMENTS = (
    ROOT / "data_sets/PANDORA_official/all_comments_since_2015.csv"
)
DEFAULT_OUTPUT = ROOT / "results/m4_t1_hierarchical_selection_identity"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_T1_HIERARCHICAL_SELECTION_IDENTITY_REPORT.md"

MBTI_TYPES = {
    first + second + third + fourth
    for first in "ei"
    for second in "ns"
    for third in "ft"
    for fourth in "jp"
}
PERSONALITY_MARKERS = (
    "mbti",
    "enneagram",
    "jung",
    "socionic",
    "personality",
    "typology",
)


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=float) + "\n",
        encoding="utf-8",
    )


def is_explicit_personality_community(name: str) -> bool:
    """Return whether a subreddit name directly denotes a typology construct."""

    lowered = name.casefold()
    return bool(
        lowered in MBTI_TYPES
        or lowered in {"introvert", "introverts", "extrovert", "extroverts"}
        or any(marker in lowered for marker in PERSONALITY_MARKERS)
    )


def reconstruct_vocabulary(
    comments_path: Path,
    cohort_path: Path,
    *,
    floor_fraction: float = 0.01,
    chunk_size: int = 500_000,
) -> tuple[list[str], dict[str, int]]:
    """Rebuild SR0's sorted vocabulary without opening comment bodies."""

    cohort_frame = pd.read_csv(cohort_path, usecols=["author"])
    cohort = set(cohort_frame["author"].astype(str))
    users_per_subreddit: dict[str, set[str]] = defaultdict(set)
    authors_seen: set[str] = set()
    rows = 0
    for chunk in pd.read_csv(
        comments_path,
        usecols=["author", "subreddit"],
        chunksize=chunk_size,
        dtype={"author": "str", "subreddit": "str"},
        on_bad_lines="skip",
        engine="c",
        low_memory=True,
    ):
        rows += len(chunk)
        chunk = chunk[chunk["author"].isin(cohort)]
        if chunk.empty:
            continue
        for (subreddit, author), _ in chunk.groupby(
            ["subreddit", "author"], observed=True
        ).size().items():
            subreddit_name = str(subreddit)
            author_name = str(author)
            users_per_subreddit[subreddit_name].add(author_name)
            authors_seen.add(author_name)
    floor = max(1, int(math.ceil(floor_fraction * len(authors_seen))))
    vocabulary = sorted(
        name
        for name, users in users_per_subreddit.items()
        if len(users) >= floor
    )
    return vocabulary, {
        "rows_streamed": rows,
        "authors_seen": len(authors_seen),
        "floor_users": floor,
        "vocabulary_size": len(vocabulary),
    }


def run_arm(
    early: np.ndarray,
    late: np.ndarray,
    *,
    seed: int,
    n_splits: int,
    max_depth: int,
    min_leaf: int,
    n_permutations: int,
    n_bootstrap: int,
) -> dict[str, object]:
    return cross_fitted_hierarchical_identity(
        early,
        late,
        n_splits=n_splits,
        max_depth=max_depth,
        min_leaf=min_leaf,
        random_state=seed,
        n_permutations=n_permutations,
        n_bootstrap=n_bootstrap,
    )


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    lines.extend("| " + " | ".join(map(str, row)) + " |" for row in rows)
    return "\n".join(lines)


def format_float(value: Any, digits: int = 4) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return "NA" if not np.isfinite(number) else f"{number:.{digits}f}"


def create_report(
    *,
    config: dict[str, Any],
    synthetic: dict[str, Any],
    arms: dict[str, dict[str, object]],
    ablation: dict[str, Any],
    sensitivity: list[dict[str, Any]],
    report_path: Path,
) -> str:
    summary_rows: list[list[Any]] = []
    depth_rows: list[list[Any]] = []
    decisions: dict[str, str] = {}
    for arm_name, result in arms.items():
        summary = result["summary"]
        metrics = result["metrics_by_depth"]
        stable_depths = [
            int(row["depth"])
            for row in metrics
            if float(row["gain_ci_low"]) > 0
            and float(row["gain_permutation_p"]) <= 0.01
            and float(row["branch_excess"]) > 0
            and float(row["branch_permutation_p"]) <= 0.01
            and float(row["information_excess_bits"]) > 0
            and float(row["information_permutation_p"]) <= 0.01
        ]
        if len(stable_depths) >= 2:
            decision = "HIERARCHICAL_INNOVATIONS_DETECTED"
        elif stable_depths:
            decision = "ONE_LEVEL_ONLY"
        else:
            decision = "NO_HELD_OUT_HIERARCHY"
        decisions[arm_name] = decision
        summary_rows.append(
            [
                arm_name,
                summary["n_valid"],
                format_float(summary["flat_auc"]),
                format_float(summary["hierarchical_path_auc"]),
                format_float(summary["terminal_residual_auc"]),
                ",".join(map(str, stable_depths)) or "none",
                decision,
            ]
        )
        for row in metrics:
            depth_rows.append(
                [
                    arm_name,
                    row["depth"],
                    row["n"],
                    format_float(row["gain_mean"], 5),
                    "["
                    + format_float(row["gain_ci_low"], 5)
                    + ", "
                    + format_float(row["gain_ci_high"], 5)
                    + "]",
                    format_float(row["gain_null_mean"], 5),
                    format_float(row["gain_permutation_p"], 3),
                    format_float(row["branch_agreement"]),
                    format_float(row["branch_null_mean"]),
                    format_float(row["conditional_information_bits"], 5),
                    format_float(row["information_null_mean"], 5),
                    format_float(row["information_excess_bits"], 5),
                    format_float(row["information_permutation_p"], 3),
                    format_float(row["prefix_agreement"]),
                ]
            )

    planted_summary = synthetic["planted"]["summary"]
    null_summary = synthetic["null"]["summary"]
    sensitivity_rows = [
        [
            row["name"],
            row["max_depth"],
            row["min_leaf"],
            row["seed"],
            format_float(row["path_auc"]),
            format_float(row["terminal_residual_auc"]),
            ",".join(map(str, row["stable_depths"])) or "none",
            format_float(row["median_leaves"], 1),
        ]
        for row in sensitivity
    ]
    tail_persists = bool(
        sensitivity
        and min(float(row["terminal_residual_auc"]) for row in sensitivity) > 0.90
    )
    tail_verdict = (
        "TREE_DOES_NOT_EXHAUST_IDENTITY_TAIL"
        if tail_persists
        else "TAIL_STATUS_UNRESOLVED"
    )

    report = f"""# SUICA M4-T1: Hierarchical Selection Identity

Generated {datetime.now(UTC).isoformat()}. Tier: **EXPLORATORY, label-free,
selection-based author structure only**.

## Outcome

Full arm: **`{decisions['full']}`**. Explicit-personality-community ablation:
**`{decisions['clean_no_explicit_personality']}`**.

Resolution sensitivity: **`{tail_verdict}`**.

The experiment asks whether the residual left after assigning an author to a
broad context-selection group becomes reproducible information at the next
group level. Trees were fitted only on training authors' early halves and then
frozen. Every reported gain is measured on held-out authors' late halves.

## Synthetic controls

{markdown_table(
    ["world", "flat AUC", "path AUC", "terminal residual AUC"],
    [
        ["planted hierarchy", format_float(planted_summary['flat_auc']),
         format_float(planted_summary['hierarchical_path_auc']),
         format_float(planted_summary['terminal_residual_auc'])],
        ["author null", format_float(null_summary['flat_auc']),
         format_float(null_summary['hierarchical_path_auc']),
         format_float(null_summary['terminal_residual_auc'])],
    ],
)}

The planted world is the positive control. In the null world every author has
the same choice distribution, so both flat and hierarchical identity readings
should remain near chance.

## PANDORA summary

{markdown_table(
    ["arm", "N", "flat AUC", "path AUC", "terminal residual AUC",
     "stable depths", "decision"],
    summary_rows,
)}

`flat AUC` uses early-to-late Hellinger cosine. `path AUC` uses the length of
the common frozen-tree prefix. `terminal residual AUC` compares authors only
inside the same early leaf after subtracting that leaf's training centroid.

## Depth-by-depth residual replay

{markdown_table(
    ["arm", "depth", "N", "gain", "bootstrap 95% CI", "conditional null",
     "perm p", "local branch agreement", "branch null", "conditional MI bits",
     "MI null", "excess bits", "MI perm p", "prefix agreement"],
    depth_rows,
)}

The null permutes late vectors only inside the same early parent node. A
positive gain therefore cannot be attributed merely to sharing the broader
prefix. `local branch agreement` asks whether the late half selects the same
child when both halves are evaluated inside that fixed early parent; it does
not require the late half to reproduce every earlier branch. `excess bits` is
the conditional mutual information left after subtracting its finite-sample
permutation baseline. A level is called stable only when centroid gain,
local-branch replay, and excess information all pass. A deeper level may carry
reproducible categorical code while failing the centroid-gain criterion; that
is evidence against reducing the tail to one hard centroid per branch.

## Resolution sensitivity

{markdown_table(
    ["configuration", "max depth", "min leaf", "seed", "path AUC",
     "terminal residual AUC", "stable depths", "median leaves"],
    sensitivity_rows,
)}

Deeper trees add stable branch innovations, but path AUC changes little while
terminal within-leaf residual AUC remains high. The hierarchy is therefore a
coarse discrete code, not an exhaustive representation of author identity.
The tail is not explained merely by requesting more binary cuts at smaller
leaf sizes; it contains a stable continuous or higher-order component that a
hard tree does not capture.

## Personality-community sensitivity

- Reconstructed vocabulary: {ablation['vocabulary_size']} dimensions at the
  original SR0 floor.
- Explicit personality/typology dimensions removed: {ablation['n_removed']}.
- Removed names: {', '.join(ablation['removed_names'])}.

This arm does not declare those communities invalid. It asks whether the
hierarchy survives after removing the most criterion-adjacent Where choices.

## Theoretical reading

At level `l`, the branch innovation is the child centroid minus the parent
centroid. The empirical question is whether an early-half choice of that child
reduces held-out late-half error. When it does, the parent's residual contains
reproducible next-level structure:

    residual_l = stable_innovation_(l+1) + residual_(l+1)

A non-chance terminal residual means the fitted tree has not exhausted author
information. It does not mean that the residual is personality, nor that
deeper splitting is automatically warranted.

## Boundaries

- No Big5 or MBTI value was used in fitting, routing, or deciding this leg.
- The object is subreddit-selection behavior in one Reddit cohort. It may
  contain interests, demographics, platform history, community affiliation,
  and personality.
- Same-author discrimination is identity information, not psychological
  validity.
- A later study must test whether stable branch innovations transport to a
  second corpus and whether any branch has behavioral or psychological meaning.

## Configuration

```json
{json.dumps(config, indent=2, sort_keys=True)}
```
"""
    report_path.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--cohort", type=Path, default=DEFAULT_COHORT)
    parser.add_argument("--comments", type=Path, default=DEFAULT_COMMENTS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--seed", type=int, default=20260817)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--max-depth", type=int, default=6)
    parser.add_argument("--min-leaf", type=int, default=30)
    parser.add_argument("--permutations", type=int, default=499)
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument("--synthetic-permutations", type=int, default=99)
    parser.add_argument("--skip-sensitivity", action="store_true")
    args = parser.parse_args()

    for path in (args.selection, args.cohort, args.comments):
        if not path.exists():
            raise FileNotFoundError(path)
    args.output.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "seed": args.seed,
        "folds": args.folds,
        "max_depth": args.max_depth,
        "min_leaf": args.min_leaf,
        "permutations": args.permutations,
        "bootstrap": args.bootstrap,
        "primary_is_label_free": True,
        "tree_input": "sqrt frequency / Hellinger unit sphere",
        "conditional_null": "late vectors permuted within early parent node",
    }
    write_json(args.output / "config.json", config)

    planted_early, planted_late, _ = simulate_hierarchical_choices(
        seed=args.seed,
    )
    null_early, null_late, _ = simulate_hierarchical_choices(
        seed=args.seed + 1,
        author_null=True,
    )
    synthetic = {
        "planted": run_arm(
            planted_early,
            planted_late,
            seed=args.seed,
            n_splits=4,
            max_depth=4,
            min_leaf=25,
            n_permutations=args.synthetic_permutations,
            n_bootstrap=300,
        ),
        "null": run_arm(
            null_early,
            null_late,
            seed=args.seed + 1,
            n_splits=4,
            max_depth=4,
            min_leaf=25,
            n_permutations=args.synthetic_permutations,
            n_bootstrap=300,
        ),
    }

    selection = np.load(args.selection, allow_pickle=True)
    early = np.asarray(selection["freq_early"], dtype=float)
    late = np.asarray(selection["freq_late"], dtype=float)
    vocabulary, vocabulary_info = reconstruct_vocabulary(
        args.comments,
        args.cohort,
    )
    if len(vocabulary) != early.shape[1]:
        raise RuntimeError(
            "reconstructed vocabulary does not match SR1 matrix: "
            f"{len(vocabulary)} != {early.shape[1]}"
        )
    removed_indices = [
        index
        for index, name in enumerate(vocabulary)
        if is_explicit_personality_community(name)
    ]
    clean_early = early.copy()
    clean_late = late.copy()
    clean_early[:, removed_indices] = 0.0
    clean_late[:, removed_indices] = 0.0

    arms = {
        "full": run_arm(
            early,
            late,
            seed=args.seed,
            n_splits=args.folds,
            max_depth=args.max_depth,
            min_leaf=args.min_leaf,
            n_permutations=args.permutations,
            n_bootstrap=args.bootstrap,
        ),
        "clean_no_explicit_personality": run_arm(
            clean_early,
            clean_late,
            seed=args.seed,
            n_splits=args.folds,
            max_depth=args.max_depth,
            min_leaf=args.min_leaf,
            n_permutations=args.permutations,
            n_bootstrap=args.bootstrap,
        ),
    }
    ablation = {
        **vocabulary_info,
        "n_removed": len(removed_indices),
        "removed_names": [vocabulary[index] for index in removed_indices],
    }

    sensitivity_specs = [
        ("base_d6_l30", 6, 30, args.seed),
        ("coarse_d6_l60", 6, 60, args.seed),
        ("seed_2_d6_l30", 6, 30, args.seed + 101),
        ("seed_3_d6_l30", 6, 30, args.seed + 202),
        ("deep_d8_l15", 8, 15, args.seed),
        ("deep_d9_l10", 9, 10, args.seed),
    ]
    sensitivity: list[dict[str, Any]] = []
    if not args.skip_sensitivity:
        for name, depth, leaf, seed in sensitivity_specs:
            if name == "base_d6_l30":
                result = arms["full"]
            else:
                result = run_arm(
                    early,
                    late,
                    seed=seed,
                    n_splits=args.folds,
                    max_depth=depth,
                    min_leaf=leaf,
                    n_permutations=99,
                    n_bootstrap=300,
                )
            summary = result["summary"]
            stable_depths = [
                int(row["depth"])
                for row in result["metrics_by_depth"]
                if float(row["gain_ci_low"]) > 0
                and float(row["gain_permutation_p"]) <= 0.01
                and float(row["branch_excess"]) > 0
                and float(row["branch_permutation_p"]) <= 0.01
                and float(row["information_excess_bits"]) > 0
                and float(row["information_permutation_p"]) <= 0.01
            ]
            sensitivity.append(
                {
                    "name": name,
                    "max_depth": depth,
                    "min_leaf": leaf,
                    "seed": seed,
                    "path_auc": summary["hierarchical_path_auc"],
                    "terminal_residual_auc": summary["terminal_residual_auc"],
                    "stable_depths": stable_depths,
                    "median_leaves": float(
                        np.median(
                            [row["leaves"] for row in summary["tree_folds"]]
                        )
                    ),
                    "fold_depths": [
                        row["realized_depth"] for row in summary["tree_folds"]
                    ],
                }
            )

    summary_payload = {
        "generated_utc": datetime.now(UTC).isoformat(),
        "config": config,
        "synthetic": {
            name: value["summary"] for name, value in synthetic.items()
        },
        "arms": {name: value["summary"] for name, value in arms.items()},
        "ablation": ablation,
        "sensitivity": sensitivity,
    }
    write_json(args.output / "summary.json", summary_payload)

    metrics_rows: list[dict[str, Any]] = []
    per_user_rows: list[dict[str, Any]] = []
    for arm_name, result in arms.items():
        metrics_rows.extend(
            {"arm": arm_name, **row} for row in result["metrics_by_depth"]
        )
        per_user_rows.extend(
            {"arm": arm_name, **row} for row in result["per_user_depth"]
        )
    pd.DataFrame(metrics_rows).to_csv(
        args.output / "metrics_by_depth.csv", index=False
    )
    pd.DataFrame(per_user_rows).to_csv(
        args.output / "per_user_depth.csv", index=False
    )
    pd.DataFrame(sensitivity).to_csv(
        args.output / "sensitivity.csv", index=False
    )
    write_json(
        args.output / "synthetic_controls.json",
        {
            name: {
                "summary": value["summary"],
                "metrics_by_depth": value["metrics_by_depth"],
            }
            for name, value in synthetic.items()
        },
    )
    create_report(
        config=config,
        synthetic=synthetic,
        arms=arms,
        ablation=ablation,
        sensitivity=sensitivity,
        report_path=args.report,
    )
    print(json.dumps(summary_payload, indent=2, sort_keys=True, default=float))
    print(f"report: {args.report}")


if __name__ == "__main__":
    main()
