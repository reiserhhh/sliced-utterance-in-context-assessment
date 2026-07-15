#!/usr/bin/env python
"""Quantify undirected geometry shared between cached V6 object families.

This is a numeric-only test of whether static, opportunity-response (hybrid),
and dynamic point clouds place the same rows in related configurations. It does
not identify a causal direction: two temporal halves are insufficient to infer
leading, inhibition, or a person-level response operator.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.residual_geometry import aligned_geometry_permutation_test  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--numeric-cache", type=Path,
                        default=ROOT / "results/v6_residual_geometry/numeric_objects.npz")
    parser.add_argument("--pair", action="append", required=True,
                        help="Cached pair name, e.g. static_hybrid.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--max-users", type=int, default=384)
    parser.add_argument("--permutation-iterations", type=int, default=999)
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _even_subsample(n: int, maximum: int) -> np.ndarray:
    """Select numeric row positions only; no author identifier is loaded or exported."""
    if maximum < 12:
        raise ValueError("max-users must be at least 12")
    if n <= maximum:
        return np.arange(n)
    return np.linspace(0, n - 1, num=maximum, dtype=int)


def _load_pair(cache: np.lib.npyio.NpzFile, pair: str) -> tuple[str, np.ndarray, np.ndarray, str, np.ndarray, np.ndarray]:
    """Load the four numeric half-matrices of one internally aligned pair."""
    prefix = f"cross_{pair}"
    names = pair.split("_")
    if len(names) != 2:
        raise ValueError("pair must have exactly two family names separated by one underscore")
    left_name, right_name = names
    keys = {
        f"{left_name}_early": f"{prefix}__{left_name}__early",
        f"{left_name}_late": f"{prefix}__{left_name}__late",
        f"{right_name}_early": f"{prefix}__{right_name}__early",
        f"{right_name}_late": f"{prefix}__{right_name}__late",
    }
    missing = [key for key in keys.values() if key not in cache.files]
    if missing:
        raise KeyError(f"Missing cached cross-block numeric set for {pair}: {missing}")
    return (
        left_name,
        np.asarray(cache[keys[f"{left_name}_early"]], dtype=float),
        np.asarray(cache[keys[f"{left_name}_late"]], dtype=float),
        right_name,
        np.asarray(cache[keys[f"{right_name}_early"]], dtype=float),
        np.asarray(cache[keys[f"{right_name}_late"]], dtype=float),
    )


def _report(results: pd.DataFrame, *, iterations: int, max_users: int, familywise_tests: int) -> str:
    columns = [
        "pair", "comparison", "n_users", "status", "linear_cka", "linear_cka_bonferroni_p",
        "rbf_cka", "rbf_cka_bonferroni_p", "distance_spearman", "distance_spearman_bonferroni_p",
        "neighbour_jaccard", "neighbour_jaccard_bonferroni_p",
    ]
    return f"""# SUICA V6 Cross-Block Geometry Audit

## Scope

This audit tests **undirected** relational correspondence between numeric V6
object families. It uses only internally aligned arrays from the ID-free cache.
For point clouds `A^(h)` and `B^(h')`, it asks whether their row-to-row kernels,
distance order, and local neighbour graphs correspond more than after permuting
the linkage of `B`. It cannot identify whether one object leads, inhibits, or
causes another; the present two-half design does not support such a claim.

## Frozen settings

- numeric rows per comparison: at most `{max_users}`
- linkage permutations: `{iterations}`
- familywise correction: Bonferroni across `{familywise_tests}` tests
- source text, terms, author IDs, and external labels: not read

## Results

{results[columns].to_markdown(index=False, floatfmt='.4f')}

## Reading rule

All-four-metric support is labelled
`CROSS_BLOCK_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN`; partial support remains
descriptive. Same-half coupling can be mechanically induced because these
objects originate from the same underlying text-path coordinates. Cross-half
coupling is therefore the stronger result, but still not evidence of a causal
or psychological relation.
"""


def main() -> None:
    args = parse_args()
    if not args.numeric_cache.exists():
        raise FileNotFoundError(f"Missing numeric cache: {args.numeric_cache}")
    maximum = 128 if args.quick else args.max_users
    iterations = 99 if args.quick else args.permutation_iterations
    if iterations < 99:
        raise ValueError("at least 99 linkage permutations are required")
    comparisons = (("left_early__right_early", 0, 0), ("left_late__right_late", 1, 1),
                   ("left_early__right_late", 0, 1), ("left_late__right_early", 1, 0))
    rows: list[dict[str, float | str]] = []
    null_rows: list[dict[str, float | str]] = []
    with np.load(args.numeric_cache) as cache:
        for pair_number, pair in enumerate(args.pair):
            left_name, left_early, left_late, right_name, right_early, right_late = _load_pair(cache, pair)
            index = _even_subsample(len(left_early), maximum)
            left, right = (left_early[index], left_late[index]), (right_early[index], right_late[index])
            for comparison_number, (comparison, left_half, right_half) in enumerate(comparisons):
                metrics, null = aligned_geometry_permutation_test(
                    left[left_half], right[right_half], neighbourhood_k=10,
                    iterations=iterations, seed=7300 + 100 * pair_number + comparison_number,
                )
                rows.append({
                    "pair": f"{left_name}__{right_name}",
                    "comparison": comparison,
                    "n_users": int(len(index)),
                    "left_features": int(left[left_half].shape[1]),
                    "right_features": int(right[right_half].shape[1]),
                    **metrics,
                })
                null_rows.extend({
                    "pair": f"{left_name}__{right_name}", "comparison": comparison, **row
                } for row in null)
    results = pd.DataFrame(rows)
    familywise_tests = len(results) * 4
    metric_keys = ("linear_cka", "rbf_cka", "distance_spearman", "neighbour_jaccard")
    for metric in metric_keys:
        results[f"{metric}_bonferroni_p"] = np.minimum(
            1.0, results[f"{metric}_permutation_p"] * familywise_tests,
        )
    adjusted = [f"{metric}_bonferroni_p" for metric in metric_keys]
    results["status"] = np.where(
        (results[adjusted] < 0.05).all(axis=1),
        "CROSS_BLOCK_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN",
        np.where(
            (results[adjusted] < 0.05).any(axis=1),
            "PARTIAL_CROSS_BLOCK_GEOMETRY_ONLY",
            "NO_CROSS_BLOCK_GEOMETRY_DETECTED",
        ),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir / "crossblock_geometry_metrics.csv", index=False)
    pd.DataFrame(null_rows).to_csv(args.output_dir / "crossblock_geometry_permutation_null.csv", index=False)
    (args.output_dir / "manifest.json").write_text(json.dumps({
        "run": "SUICA_V6_CROSSBLOCK_GEOMETRY_V1",
        "numeric_only": True,
        "contains_raw_text": False,
        "contains_tokens_or_terms": False,
        "contains_author_identifiers": False,
        "pairs": args.pair,
        "max_users": int(maximum),
        "permutation_iterations": int(iterations),
        "familywise_tests": int(familywise_tests),
    }, indent=2) + "\n")
    args.report.write_text(_report(
        results, iterations=iterations, max_users=maximum, familywise_tests=familywise_tests,
    ))


if __name__ == "__main__":
    main()
