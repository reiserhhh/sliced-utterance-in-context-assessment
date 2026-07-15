#!/usr/bin/env python
"""Audit a selected paired V6 numeric object from the ID-free geometry cache.

This runner never opens raw text, token lists, feature names, author IDs, or
external labels. It loads only numeric early/late matrices written by the V6
residual-geometry construction boundary and tests their paired relational
geometry against row-linkage permutations.
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

from suica_core.residual_geometry import geometry_audit, geometry_status  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--numeric-cache", type=Path,
        default=ROOT / "results/v6_residual_geometry/numeric_objects.npz",
    )
    parser.add_argument("--object", action="append", required=True,
                        help="Cached object base name, e.g. hybrid_full or hybrid_residual.")
    parser.add_argument("--mask-suffix", default=None,
                        help="Optional paired boolean mask stored in the numeric cache.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--permutation-iterations", type=int, default=999)
    parser.add_argument("--subsample-iterations", type=int, default=128)
    parser.add_argument("--quick", action="store_true", help="Use 99 / 16 draws for an execution smoke test.")
    return parser.parse_args()


def _load_object(cache: np.lib.npyio.NpzFile, object_name: str, mask_suffix: str | None) -> tuple[np.ndarray, np.ndarray]:
    """Load a finite paired numeric object and, optionally, one cached boolean mask."""
    early_key, late_key = f"{object_name}__early", f"{object_name}__late"
    if early_key not in cache.files or late_key not in cache.files:
        raise KeyError(f"Missing cached object: {object_name}")
    early, late = np.asarray(cache[early_key], dtype=float), np.asarray(cache[late_key], dtype=float)
    if mask_suffix:
        mask_key = f"{object_name}__{mask_suffix}"
        if mask_key not in cache.files:
            raise KeyError(f"Missing cached mask: {mask_key}")
        mask = np.asarray(cache[mask_key], dtype=bool)
        if len(mask) != len(early):
            raise ValueError(f"Misaligned cached mask: {mask_key}")
        early, late = early[mask], late[mask]
    return early, late


def _report(results: pd.DataFrame, *, iterations: int, subsamples: int, familywise_tests: int,
            mask_suffix: str | None) -> str:
    display = results[[
        "object", "n_users", "n_features", "status", "linear_cka", "linear_cka_bonferroni_p",
        "distance_spearman", "distance_spearman_bonferroni_p", "neighbour_jaccard",
        "neighbour_jaccard_bonferroni_p", "effective_rank_early", "effective_rank_late",
        "intrinsic_dimension_early", "intrinsic_dimension_late", "spectrum_cosine",
    ]]
    mask_line = f"- cached sensitivity mask: `{mask_suffix}`\n" if mask_suffix else "- cached sensitivity mask: none\n"
    return f"""# SUICA V6 Cached Numeric Geometry Audit

## Scope

This is an ID-free numeric audit of already constructed V6 objects. The tested
quantity is relational geometry, not a named factor, trait, or personality
score. The null retains both early and late point clouds but permutes the row
linkage between them.

## Frozen settings

- linkage permutations: `{iterations}`
- descriptive subsamples: `{subsamples}`
- familywise correction: Bonferroni across `{familywise_tests}` object-metric tests
{mask_line}- raw text, tokens, terms, author IDs, and external labels: not read

## Results

{display.to_markdown(index=False, floatfmt='.4f')}

## Reading rule

`LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN` requires all three linkage
metrics to survive the stated familywise correction. It means only that the
numeric relation among rows reproduces above an arbitrary pairing; it does not
identify the source of that relation or promote the object to a psychological
construct. `PARTIAL_LINKAGE_GEOMETRY_ONLY` is descriptive, not confirmatory.
"""


def main() -> None:
    args = parse_args()
    if not args.numeric_cache.exists():
        raise FileNotFoundError(f"Missing numeric cache: {args.numeric_cache}")
    iterations = 99 if args.quick else args.permutation_iterations
    subsamples = 16 if args.quick else args.subsample_iterations
    if iterations < 99:
        raise ValueError("at least 99 linkage permutations are required")
    rows: list[dict[str, float | str]] = []
    null_rows: list[dict[str, float | str]] = []
    with np.load(args.numeric_cache) as cache:
        for index, object_name in enumerate(args.object):
            early, late = _load_object(cache, object_name, args.mask_suffix)
            metrics, null = geometry_audit(
                early, late,
                neighbourhood_k=10,
                permutation_iterations=iterations,
                subsample_iterations=subsamples,
                seed=6400 + index,
            )
            rows.append({
                "object": object_name,
                "n_users": int(len(early)),
                "n_features": int(early.shape[1]),
                **metrics,
            })
            null_rows.extend({"object": object_name, **row} for row in null)

    familywise_tests = len(rows) * 3
    for row in rows:
        for metric in ("linear_cka", "distance_spearman", "neighbour_jaccard"):
            row[f"{metric}_bonferroni_p"] = min(1.0, row[f"{metric}_permutation_p"] * familywise_tests)
        row["status"] = geometry_status(row)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = pd.DataFrame(rows)
    results.to_csv(args.output_dir / "geometry_metrics.csv", index=False)
    pd.DataFrame(null_rows).to_csv(args.output_dir / "linkage_permutation_null.csv", index=False)
    manifest = {
        "run": "SUICA_V6_CACHED_NUMERIC_GEOMETRY_V1",
        "numeric_only": True,
        "contains_raw_text": False,
        "contains_tokens_or_terms": False,
        "contains_author_identifiers": False,
        "objects": args.object,
        "mask_suffix": args.mask_suffix,
        "permutation_iterations": int(iterations),
        "subsample_iterations": int(subsamples),
        "familywise_tests": int(familywise_tests),
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    args.report.write_text(_report(
        results, iterations=iterations, subsamples=subsamples,
        familywise_tests=familywise_tests, mask_suffix=args.mask_suffix,
    ))


if __name__ == "__main__":
    main()
