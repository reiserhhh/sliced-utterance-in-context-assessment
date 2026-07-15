#!/usr/bin/env python
"""Test whether V6 static geometry survives residualization-strength perturbation.

The registered nuisance Ridge alpha is 10. This audit fixes a logarithmic local
grid (1, 10, 100), retains all outcomes, and compares same-half author
relations across alpha values. It is a scorer-perturbation test, not a
hyperparameter search or a construct-discovery procedure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v6_factor_discovery_v2 import (  # noqa: E402
    build_objects,
    crossfit_residuals,
    fit_representation,
    opportunity_axis,
    prepare_units,
    stable_user_split,
)
from suica_core.residual_geometry import aligned_geometry_permutation_test  # noqa: E402


ALPHAS = (1.0, 10.0, 100.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path,
        default=ROOT / "data_sets" / "prepared" / "suica_tiers_v2" / "tier_u_comments.parquet",
    )
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_nuisance_alpha_sensitivity")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_NUISANCE_ALPHA_SENSITIVITY_REPORT.md")
    parser.add_argument("--max-users", type=int, default=384)
    parser.add_argument("--permutation-iterations", type=int, default=999)
    parser.add_argument("--quick", action="store_true")
    return parser.parse_args()


def _stable_subsample(users: list[str], maximum: int, seed: int) -> np.ndarray:
    """Choose a reproducible internal subset without serializing identifiers."""
    if maximum < 12:
        raise ValueError("max-users must be at least 12")
    if len(users) <= maximum:
        return np.arange(len(users))
    values = np.asarray([
        int.from_bytes(hashlib.blake2b(f"{seed}:{user}".encode(), digest_size=8).digest(), "little")
        for user in users
    ], dtype=np.uint64)
    return np.argsort(values, kind="stable")[:maximum]


def _standardized_static_views(
    static: pd.DataFrame,
    discovery_users: set[str],
    confirmation_users: set[str],
) -> tuple[np.ndarray, np.ndarray, list[str], dict[str, float]]:
    """Return discovery-reference standardized static early/late matrices."""
    columns = [column for column in static if column.startswith("static::")]
    early = static.loc[static["half"].eq("early")].set_index("user_id")[columns]
    late = static.loc[static["half"].eq("late")].set_index("user_id")[columns]
    users = sorted(set(early.index).intersection(late.index))
    discovery = [user for user in users if user in discovery_users]
    confirmation = [user for user in users if user in confirmation_users]
    if len(discovery) < 12 or len(confirmation) < 12:
        raise ValueError("insufficient paired static users")
    reference = np.vstack([early.loc[discovery].to_numpy(float), late.loc[discovery].to_numpy(float)])
    center = reference.mean(axis=0)
    scale = reference.std(axis=0, ddof=1)
    scale[scale < 1e-8] = 1.0
    early_values = (early.loc[confirmation].to_numpy(float) - center) / scale
    late_values = (late.loc[confirmation].to_numpy(float) - center) / scale
    return early_values, late_values, confirmation, {
        "mean_norm_early": float(np.linalg.norm(early_values, axis=1).mean()),
        "mean_norm_late": float(np.linalg.norm(late_values, axis=1).mean()),
    }


def _report(results: pd.DataFrame, norms: pd.DataFrame, *, iterations: int, maximum: int,
            familywise_tests: int) -> str:
    columns = [
        "comparison", "n_users", "status", "linear_cka", "linear_cka_bonferroni_p",
        "rbf_cka", "rbf_cka_bonferroni_p", "distance_spearman", "distance_spearman_bonferroni_p",
        "neighbour_jaccard", "neighbour_jaccard_bonferroni_p",
    ]
    return f"""# SUICA V6 Nuisance-Alpha Sensitivity Audit

## Scope

This is a predeclared scorer-perturbation audit. The source representation is
fit once on discovery authors. The nuisance residualization is then rebuilt at
Ridge alpha `{ALPHAS}`; each resulting static configuration is standardized
against its own discovery reference. Same-half cross-alpha geometry is compared
under a row-linkage permutation null. No alpha is selected as a winner.

## Frozen settings

- nuisance Ridge alphas: `{ALPHAS}`
- tested comparisons: all pairwise alpha values in early and late halves
- confirmation rows per comparison: at most `{maximum}`
- linkage permutations: `{iterations}`
- familywise correction: Bonferroni across `{familywise_tests}` tests
- source text, terms, author IDs, and external labels: not exported or inspected after mapping

## Scale diagnostics

{norms.to_markdown(index=False, floatfmt='.4f')}

## Results

{results[columns].to_markdown(index=False, floatfmt='.4f')}

## Reading rule

Passing all four tests means the corresponding same-half relational geometry is
robust to this local residualization-strength perturbation. It does not mean
the nuisance model is causal, complete, or optimized, and it cannot establish
cross-time or cross-context stability.
"""


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(f"Missing input: {args.input}")
    cfg = json.loads(args.config.read_text())
    cfg["quick"] = args.quick
    maximum = 128 if args.quick else args.max_users
    iterations = 99 if args.quick else args.permutation_iterations
    if iterations < 99:
        raise ValueError("at least 99 linkage permutations are required")
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, cfg)
    users = sorted(units["user_id"].unique())
    discovery_users = {user for user in users if stable_user_split(user) == "discovery"}
    confirmation_users = set(users) - discovery_users
    _, _, representation = fit_representation(units, discovery_users, cfg)

    views: dict[float, tuple[np.ndarray, np.ndarray, list[str]]] = {}
    norm_rows: list[dict[str, float]] = []
    supported_reference: set[str] | None = None
    for alpha in ALPHAS:
        alpha_cfg = {**cfg, "nuisance_ridge_alpha": alpha}
        residual, supported = crossfit_residuals(units, representation, discovery_users, alpha_cfg)
        if supported_reference is None:
            supported_reference = supported
        elif supported != supported_reference:
            raise RuntimeError("condition support changed across alpha values")
        opportunity, _ = opportunity_axis(units, discovery_users, supported)
        static, _, _, _ = build_objects(units, residual, opportunity, alpha_cfg)
        early, late, aligned_users, norms = _standardized_static_views(
            static, discovery_users, confirmation_users,
        )
        views[alpha] = (early, late, aligned_users)
        norm_rows.append({"nuisance_ridge_alpha": alpha, **norms})

    base_users = views[10.0][2]
    if any(users_alpha != base_users for _, _, users_alpha in views.values()):
        raise RuntimeError("confirmation author alignment changed across alpha values")
    index = _stable_subsample(base_users, maximum, int(cfg["seed"]) + 10100)
    comparisons = []
    for left, right in ((1.0, 10.0), (10.0, 100.0), (1.0, 100.0)):
        for half, half_index in (("early", 0), ("late", 1)):
            comparisons.append((f"alpha_{left:g}__alpha_{right:g}__{half}", left, right, half_index))

    rows: list[dict[str, float | str]] = []
    null_rows: list[dict[str, float | str]] = []
    for comparison_number, (name, left_alpha, right_alpha, half_index) in enumerate(comparisons):
        metrics, null = aligned_geometry_permutation_test(
            views[left_alpha][half_index][index], views[right_alpha][half_index][index],
            neighbourhood_k=10, iterations=iterations, seed=10200 + comparison_number,
        )
        rows.append({"comparison": name, "n_users": int(len(index)), **metrics})
        null_rows.extend({"comparison": name, **row} for row in null)
    results = pd.DataFrame(rows)
    familywise_tests = len(results) * 4
    metric_names = ("linear_cka", "rbf_cka", "distance_spearman", "neighbour_jaccard")
    for metric in metric_names:
        results[f"{metric}_bonferroni_p"] = np.minimum(
            1.0, results[f"{metric}_permutation_p"] * familywise_tests,
        )
    adjusted = [f"{metric}_bonferroni_p" for metric in metric_names]
    results["status"] = np.where(
        (results[adjusted] < 0.05).all(axis=1),
        "SCORER_PERTURBATION_ROBUST_NO_MATERIAL_MARGIN",
        np.where(
            (results[adjusted] < 0.05).any(axis=1),
            "PARTIAL_SCORER_PERTURBATION_ROBUSTNESS_ONLY",
            "NO_SCORER_PERTURBATION_ROBUSTNESS_DETECTED",
        ),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    norms = pd.DataFrame(norm_rows)
    results.to_csv(args.output_dir / "nuisance_alpha_geometry_metrics.csv", index=False)
    norms.to_csv(args.output_dir / "nuisance_alpha_norm_diagnostics.csv", index=False)
    pd.DataFrame(null_rows).to_csv(args.output_dir / "nuisance_alpha_permutation_null.csv", index=False)
    (args.output_dir / "manifest.json").write_text(json.dumps({
        "run": "SUICA_V6_NUISANCE_ALPHA_SENSITIVITY_V1",
        "numeric_only_after_representation": True,
        "contains_raw_text": False,
        "contains_tokens_or_terms": False,
        "contains_author_identifiers": False,
        "nuisance_ridge_alphas": list(ALPHAS),
        "max_users": int(maximum),
        "permutation_iterations": int(iterations),
        "familywise_tests": int(familywise_tests),
        "config": cfg,
    }, indent=2) + "\n")
    args.report.write_text(_report(
        results, norms, iterations=iterations, maximum=maximum, familywise_tests=familywise_tests,
    ))


if __name__ == "__main__":
    main()
