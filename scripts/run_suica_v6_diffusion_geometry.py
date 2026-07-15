#!/usr/bin/env python
"""Run a preregistered nonlinear-geometry probe on V6 numeric residual objects.

Only ID-free early/late matrices are read. The test is deliberately a fixed
grid, not a manifold search: it asks whether a small set of self-tuning
diffusion-map resolutions recovers stable geometry missed by linear axes.
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

from suica_core.diffusion_geometry import diffusion_geometry_audit  # noqa: E402


FIXED_GRID = ((10, 3), (25, 3), (50, 3), (25, 5))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--numeric-cache", type=Path,
                        default=ROOT / "results/v6_residual_geometry/numeric_objects.npz")
    parser.add_argument("--object", action="append", default=None,
                        help="Numeric cache object; defaults to static_residual and dynamic_residual.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_diffusion_geometry")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_DIFFUSION_GEOMETRY_REPORT.md")
    parser.add_argument("--max-users", type=int, default=384)
    parser.add_argument("--permutation-iterations", type=int, default=999)
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _even_subsample(n: int, maximum: int) -> np.ndarray:
    if maximum < 12:
        raise ValueError("max-users must be at least 12")
    return np.arange(n) if n <= maximum else np.linspace(0, n - 1, num=maximum, dtype=int)


def _report(results: pd.DataFrame, *, iterations: int, maximum: int, familywise_tests: int) -> str:
    columns = [
        "object", "diffusion_neighbours", "diffusion_dimensions", "n_users", "status",
        "linear_cka", "linear_cka_bonferroni_p", "rbf_cka", "rbf_cka_bonferroni_p",
        "distance_spearman", "distance_spearman_bonferroni_p", "neighbour_jaccard",
        "neighbour_jaccard_bonferroni_p", "early_connected_components", "late_connected_components",
        "early_eigengap", "late_eigengap",
    ]
    return f"""# SUICA V6 Diffusion-Geometry Audit

## Scope

This is a numeric-only nonlinear alternative to the rejected stable-axis story.
For each fixed `(k, m)` pair, a self-tuning kNN diffusion map is independently
built for early and late residual clouds, then compared under a row-linkage
permutation null. The grid is fixed before inspecting outcomes; no text,
vocabulary, author ID, scale label, or qualitative interpretation is used.

## Frozen settings

- fixed diffusion grid `(neighbours, dimensions)`: `{FIXED_GRID}`
- numeric rows per object: at most `{maximum}`
- linkage permutations per grid cell: `{iterations}`
- familywise correction: Bonferroni across `{familywise_tests}` tests
- density normalization: alpha = 0.5; diffusion time = 1

## Results

{results[columns].to_markdown(index=False, floatfmt='.4f')}

## Reading rule

A passing row means only that the corresponding **pre-specified nonlinear
geometry** reproduces above a linkage-permutation null. It is not evidence for
a named dynamic axis, personality, causal response operator, or general
manifold. A failed grid does not prove no nonlinear structure exists; it rules
out recovery by this fixed, local diffusion construction at the available
sample and two-half design.
"""


def main() -> None:
    args = parse_args()
    if not args.numeric_cache.exists():
        raise FileNotFoundError(f"Missing numeric cache: {args.numeric_cache}")
    objects = args.object or ["static_residual", "dynamic_residual"]
    maximum = 128 if args.quick else args.max_users
    iterations = 99 if args.quick else args.permutation_iterations
    if iterations < 99:
        raise ValueError("at least 99 linkage permutations are required")
    rows: list[dict[str, float | str]] = []
    null_rows: list[dict[str, float | str]] = []
    with np.load(args.numeric_cache) as cache:
        for object_number, object_name in enumerate(objects):
            early_key, late_key = f"{object_name}__early", f"{object_name}__late"
            if early_key not in cache.files or late_key not in cache.files:
                raise KeyError(f"Missing cached object: {object_name}")
            early, late = np.asarray(cache[early_key], dtype=float), np.asarray(cache[late_key], dtype=float)
            index = _even_subsample(len(early), maximum)
            for grid_number, (neighbours, dimensions) in enumerate(FIXED_GRID):
                metrics, null = diffusion_geometry_audit(
                    early[index], late[index], neighbours=neighbours, dimensions=dimensions,
                    permutation_iterations=iterations, seed=8200 + 100 * object_number + grid_number,
                )
                rows.append({"object": object_name, "n_users": int(len(index)), **metrics})
                null_rows.extend({
                    "object": object_name, "diffusion_neighbours": neighbours,
                    "diffusion_dimensions": dimensions, **row,
                } for row in null)
    results = pd.DataFrame(rows)
    familywise_tests = len(results) * 4
    metrics = ("linear_cka", "rbf_cka", "distance_spearman", "neighbour_jaccard")
    for metric in metrics:
        results[f"{metric}_bonferroni_p"] = np.minimum(
            1.0, results[f"{metric}_permutation_p"] * familywise_tests,
        )
    adjusted = [f"{metric}_bonferroni_p" for metric in metrics]
    results["status"] = np.where(
        (results[adjusted] < 0.05).all(axis=1),
        "NONLINEAR_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN",
        np.where(
            (results[adjusted] < 0.05).any(axis=1),
            "PARTIAL_NONLINEAR_GEOMETRY_ONLY",
            "NO_NONLINEAR_GEOMETRY_DETECTED",
        ),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir / "diffusion_geometry_metrics.csv", index=False)
    pd.DataFrame(null_rows).to_csv(args.output_dir / "diffusion_geometry_permutation_null.csv", index=False)
    (args.output_dir / "manifest.json").write_text(json.dumps({
        "run": "SUICA_V6_DIFFUSION_GEOMETRY_V1",
        "numeric_only": True,
        "contains_raw_text": False,
        "contains_tokens_or_terms": False,
        "contains_author_identifiers": False,
        "objects": objects,
        "fixed_grid": [{"neighbours": k, "dimensions": m} for k, m in FIXED_GRID],
        "max_users": int(maximum),
        "permutation_iterations": int(iterations),
        "familywise_tests": int(familywise_tests),
    }, indent=2) + "\n")
    args.report.write_text(_report(
        results, iterations=iterations, maximum=maximum, familywise_tests=familywise_tests,
    ))


if __name__ == "__main__":
    main()
