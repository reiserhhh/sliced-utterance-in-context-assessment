#!/usr/bin/env python
"""Probe local, mesoscopic, and global residual geometry from numeric cache only."""
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

from suica_core.multiscale_geometry import multiscale_neighbour_profile  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path,
                        default=ROOT / "results/v6_residual_geometry/numeric_objects.npz")
    parser.add_argument("--objects", default="static_residual,dynamic_residual",
                        help="Comma-separated cached object names.")
    parser.add_argument("--mask-suffix", default=None,
                        help="Optional ID-free cache mask suffix, e.g. condition_jaccard_ge_010.")
    parser.add_argument("--scales", default="5,10,25,50,100,200")
    parser.add_argument("--permutation-iterations", type=int, default=1999)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_multiscale_geometry")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_MULTISCALE_GEOMETRY_REPORT.md")
    return parser.parse_args()


def _status(adjusted_p: float) -> str:
    return "SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN" if adjusted_p < 0.05 else "NO_SCALE_LINKAGE_DETECTED"


def _report(results: pd.DataFrame, *, iterations: int, familywise_tests: int, mask_suffix: str | None) -> str:
    display = results[[
        "object", "k", "neighbour_jaccard", "null_mean", "absolute_excess",
        "normalized_excess", "bonferroni_p", "status",
    ]]
    return rf"""# SUICA V6 Multiscale Residual Geometry

## Numeric object

This analysis reads only an ID-free `.npz` cache of paired numeric residual
matrices. It never opens source text, feature names, token lists, labels, or
author identifiers.

For each neighbourhood scale `k`, let `N_k^E(u)` and `N_k^L(u)` be the `k`
nearest numerical neighbours of author `u` in the early and late clouds. The
profile statistic is

\[
J_k=\frac{{1}}{{n}}\sum_u
\frac{{|N_k^E(u)\cap N_k^L(u)|}}{{|N_k^E(u)\cup N_k^L(u)|}}.
\]

The linkage null fixes both clouds and permutes only early-to-late author
correspondence. Small `k` tests local neighbourhoods; larger `k` tests broader,
mesoscopic affiliation. This is not evidence for a discrete cluster, a factor,
or a psychological construct.

## Frozen controls

- linkage permutations per object-scale: `{iterations}`
- Bonferroni family: `{familywise_tests}` object-scale tests
- condition-overlap mask: `{mask_suffix or 'none'}`
- report output contains no text or author identifiers

## Results

{display.to_markdown(index=False, floatfmt='.5f')}

## Reading rule

`SCALE_LINKAGE_DETECTED_NO_MATERIAL_MARGIN` requires adjusted `p < .05` only;
it has no preregistered practical-effect threshold. The `absolute_excess` and
`normalized_excess` columns must be read alongside p-values. A signal only at
large `k` is broad relational ordering, not a stable local group. A signal at
small `k` still requires opportunity, representation, and repeated-occasion
controls before it can be treated as an author property.
"""


def main() -> None:
    args = parse_args()
    if not args.cache.exists():
        raise FileNotFoundError(f"Missing numeric cache: {args.cache}")
    objects = tuple(part.strip() for part in args.objects.split(",") if part.strip())
    scales = tuple(int(part) for part in args.scales.split(",") if part.strip())
    cache = np.load(args.cache)
    rows: list[dict[str, float | str]] = []
    null_rows: list[dict[str, float | str]] = []
    for index, name in enumerate(objects):
        early_key, late_key = f"{name}__early", f"{name}__late"
        if early_key not in cache or late_key not in cache:
            raise KeyError(f"Object not in cache: {name}")
        early, late = cache[early_key], cache[late_key]
        if args.mask_suffix:
            mask_key = f"{name}__{args.mask_suffix}"
            if mask_key not in cache:
                raise KeyError(f"Mask not in cache: {mask_key}")
            mask = cache[mask_key].astype(bool)
            early, late = early[mask], late[mask]
        profile, null = multiscale_neighbour_profile(
            early, late, scales=scales,
            iterations=args.permutation_iterations, seed=7300 + index,
        )
        rows.extend({"object": name, **row} for row in profile)
        null_rows.extend({"object": name, **row} for row in null)
    familywise_tests = len(rows)
    for row in rows:
        row["bonferroni_p"] = min(1.0, float(row["permutation_p"]) * familywise_tests)
        row["status"] = _status(float(row["bonferroni_p"]))
    results = pd.DataFrame(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir / "multiscale_profile.csv", index=False)
    pd.DataFrame(null_rows).to_csv(args.output_dir / "multiscale_linkage_null.csv", index=False)
    (args.output_dir / "manifest.json").write_text(json.dumps({
        "run": "SUICA_V6_MULTISCALE_GEOMETRY_V1",
        "cache": str(args.cache.name),
        "source_text_read": False,
        "author_identifiers_read": False,
        "objects": list(objects),
        "mask_suffix": args.mask_suffix,
        "scales": list(scales),
        "permutation_iterations": args.permutation_iterations,
        "familywise_tests": familywise_tests,
    }, indent=2) + "\n")
    args.report.write_text(_report(
        results, iterations=args.permutation_iterations, familywise_tests=familywise_tests,
        mask_suffix=args.mask_suffix,
    ))


if __name__ == "__main__":
    main()
