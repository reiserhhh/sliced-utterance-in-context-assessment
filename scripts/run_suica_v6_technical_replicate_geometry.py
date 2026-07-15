#!/usr/bin/env python
"""Test real-text sensitivity of V6 static scores to within-condition slicing.

Source text is transformed once through the registered discovery-fitted map.
The actual tests then use only residual coordinate matrices. Two fixed technical
splits preserve author and condition membership: interleaved comments and
within-condition temporal blocks. This is a measurement-error check, not a
repeated-occasion or personality validation.
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

from scripts.run_suica_v6_factor_discovery_v2 import (  # noqa: E402
    crossfit_residuals,
    fit_representation,
    prepare_units,
    stable_user_split,
)
from suica_core.residual_geometry import geometry_audit, geometry_status  # noqa: E402
from suica_core.technical_replicates import (  # noqa: E402
    aggregate_static_replicates,
    assign_within_condition_replicates,
    paired_replicate_matrices,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path,
        default=ROOT / "data_sets" / "prepared" / "suica_tiers_v2" / "tier_u_comments.parquet",
    )
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_technical_replicate_geometry")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_TECHNICAL_REPLICATE_GEOMETRY_REPORT.md")
    parser.add_argument("--max-users", type=int, default=384)
    parser.add_argument("--permutation-iterations", type=int, default=999)
    parser.add_argument("--subsample-iterations", type=int, default=128)
    parser.add_argument("--subsample-max-users", type=int, default=256,
                        help="Rows per descriptive subsample; kept below the primary confirmation cap.")
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _even_subsample(n: int, maximum: int) -> np.ndarray:
    if maximum < 12:
        raise ValueError("max-users must be at least 12")
    return np.arange(n) if n <= maximum else np.linspace(0, n - 1, num=maximum, dtype=int)


def _report(results: pd.DataFrame, coverage: pd.DataFrame, *, iterations: int, subsamples: int,
            subsample_maximum: int, maximum: int, familywise_tests: int) -> str:
    columns = [
        "scheme", "half", "n_users", "status", "linear_cka", "linear_cka_bonferroni_p",
        "distance_spearman", "distance_spearman_bonferroni_p", "neighbour_jaccard",
        "neighbour_jaccard_bonferroni_p", "effective_rank_early", "effective_rank_late",
        "intrinsic_dimension_early", "intrinsic_dimension_late", "spectrum_cosine",
    ]
    return f"""# SUICA V6 Technical-Replicate Geometry Audit

## Scope

This audit measures robustness to slice boundaries inside the same author,
half, and condition cell. Each cell with at least two observations is split by
two predeclared procedures: alternating (interleaved) comments and temporal
blocks. The source map and nuisance residualization are discovery-fitted. After
that boundary, all tests operate on numeric residual matrices only.

This is a **technical-replica** result: it measures scoring sensitivity to
which comments land in a slice. It does not establish independent occasions,
cross-context transfer, individual response operators, or a personality trait.

## Frozen settings

- technical split schemes: interleaved, blocked
- confirmation rows per comparison: at most `{maximum}`
- linkage permutations: `{iterations}`
- descriptive subsamples: `{subsamples}` of at most `{subsample_maximum}` authors
- familywise correction: Bonferroni across `{familywise_tests}` object-metric tests
- text, terms, author IDs, and external labels: not exported or inspected after mapping

## Coverage

{coverage.to_markdown(index=False)}

## Results

{results[columns].to_markdown(index=False, floatfmt='.4f')}

## Reading rule

A passing row means that the relational geometry of opportunity-conditioned
static configurations survives that particular within-condition slice boundary.
It says nothing about whether the configuration is stable across days, tasks,
or people. A blocked failure with an interleaved pass would indicate sensitivity
to short-run temporal state; neither outcome may be promoted to personality.
"""


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(f"Missing input: {args.input}")
    cfg = json.loads(args.config.read_text())
    cfg["quick"] = args.quick
    maximum = 128 if args.quick else args.max_users
    iterations = 99 if args.quick else args.permutation_iterations
    subsamples = 16 if args.quick else args.subsample_iterations
    if iterations < 99:
        raise ValueError("at least 99 linkage permutations are required")
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, cfg)
    users = sorted(units["user_id"].unique())
    discovery_users = {user for user in users if stable_user_split(user) == "discovery"}
    confirmation_users = set(users) - discovery_users
    _, _, representation = fit_representation(units, discovery_users, cfg)
    residual, _ = crossfit_residuals(units, representation, discovery_users, cfg)

    result_rows: list[dict[str, float | str]] = []
    null_rows: list[dict[str, float | str]] = []
    coverage_rows: list[dict[str, int | str]] = []
    for scheme_number, scheme in enumerate(("interleaved", "blocked")):
        replicated = assign_within_condition_replicates(units, scheme=scheme)
        replicated_residual = residual[replicated.index.to_numpy()]
        # Index is preserved from the original units frame, so the numeric rows remain aligned.
        frame = aggregate_static_replicates(replicated, replicated_residual)
        for half_number, half in enumerate(("early", "late")):
            early, late, counts = paired_replicate_matrices(
                frame, half=half, discovery_users=discovery_users, confirmation_users=confirmation_users,
            )
            index = _even_subsample(len(early), maximum)
            metrics, null = geometry_audit(
                early[index], late[index], neighbourhood_k=10,
                permutation_iterations=iterations, subsample_iterations=subsamples,
                subsample_max_rows=args.subsample_max_users,
                seed=9100 + 100 * scheme_number + half_number,
            )
            result_rows.append({
                "scheme": scheme,
                "half": half,
                "n_users": int(len(index)),
                **metrics,
            })
            coverage_rows.append({
                "scheme": scheme,
                "half": half,
                "n_discovery_paired": counts["n_discovery"],
                "n_confirmation_paired_before_subsample": counts["n_confirmation"],
                "n_confirmation_used": int(len(index)),
            })
            null_rows.extend({"scheme": scheme, "half": half, **row} for row in null)

    familywise_tests = len(result_rows) * 3
    for row in result_rows:
        for metric in ("linear_cka", "distance_spearman", "neighbour_jaccard"):
            row[f"{metric}_bonferroni_p"] = min(1.0, row[f"{metric}_permutation_p"] * familywise_tests)
        row["status"] = geometry_status(row)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results, coverage = pd.DataFrame(result_rows), pd.DataFrame(coverage_rows)
    results.to_csv(args.output_dir / "technical_replicate_geometry_metrics.csv", index=False)
    coverage.to_csv(args.output_dir / "technical_replicate_coverage.csv", index=False)
    pd.DataFrame(null_rows).to_csv(args.output_dir / "technical_replicate_permutation_null.csv", index=False)
    (args.output_dir / "manifest.json").write_text(json.dumps({
        "run": "SUICA_V6_TECHNICAL_REPLICATE_GEOMETRY_V1",
        "numeric_only_after_representation": True,
        "contains_raw_text": False,
        "contains_tokens_or_terms": False,
        "contains_author_identifiers": False,
        "schemes": ["interleaved", "blocked"],
        "permutation_iterations": int(iterations),
        "subsample_iterations": int(subsamples),
        "subsample_max_users": int(args.subsample_max_users),
        "max_users": int(maximum),
        "familywise_tests": int(familywise_tests),
        "config": cfg,
    }, indent=2) + "\n")
    args.report.write_text(_report(
        results, coverage, iterations=iterations, subsamples=subsamples,
        subsample_maximum=args.subsample_max_users,
        maximum=maximum, familywise_tests=familywise_tests,
    ))


if __name__ == "__main__":
    main()
