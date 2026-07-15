#!/usr/bin/env python
"""Run the V6 text-blind residual geometry audit.

Raw text is used only once to apply the frozen discovery-side representation.
After that boundary, this script retains numeric residual matrices only.  It
does not export terms, comments, author identifiers, questionnaire labels, or
psychological names.
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
    build_objects,
    conditional_residual,
    crossfit_residuals,
    fit_representation,
    opportunity_axis,
    prepare_units,
    stable_user_split,
)
from scripts.run_suica_v6_residual_source_audit import family_matrices  # noqa: E402
from suica_core.residual_geometry import geometry_audit, geometry_status  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path,
        default=ROOT / "data_sets" / "prepared" / "suica_tiers_v2" / "tier_u_comments.parquet",
        help="Raw source used only to construct the frozen numeric representation.",
    )
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_residual_geometry")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_RESIDUAL_GEOMETRY_REPORT.md")
    parser.add_argument("--quick", action="store_true", help="Use a smaller permutation/subsample budget.")
    parser.add_argument("--permutation-iterations", type=int, default=None,
                        help="Override the fixed linkage-permutation budget.")
    parser.add_argument("--subsample-iterations", type=int, default=None,
                        help="Override the descriptive subsample budget.")
    parser.add_argument("--numeric-cache", type=Path, default=None,
                        help="Optional ID-free paired numeric object cache (.npz).")
    parser.add_argument("--cache-only", action="store_true",
                        help="Export the numeric cache and stop before all geometry tests.")
    return parser.parse_args()


def _make_numeric_objects(units: pd.DataFrame, cfg: dict):
    """Create V6 numeric author objects, then discard the unit text column."""
    users = sorted(units["user_id"].unique())
    discovery_users = {user for user in users if stable_user_split(user) == "discovery"}
    confirmation_users = set(users) - discovery_users
    _, _, representation = fit_representation(units, discovery_users, cfg)
    residual, supported_conditions = crossfit_residuals(units, representation, discovery_users, cfg)
    z_map, _ = opportunity_axis(units, discovery_users, supported_conditions)
    static, hybrid, dynamic_raw, _ = build_objects(units, residual, z_map, cfg)
    hybrid = conditional_residual(hybrid, [static], "hybrid::", discovery_users)
    dynamic = conditional_residual(
        dynamic_raw, [static] + ([hybrid] if len(hybrid) else []), "dynamic::", discovery_users
    )
    return static, hybrid, dynamic, discovery_users, confirmation_users


def _write_numeric_cache(path: Path, objects: dict[str, tuple[np.ndarray, np.ndarray, list[str]]]) -> None:
    """Write paired matrices without source text, terms, or author identifiers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, np.ndarray] = {}
    manifest_objects: dict[str, dict[str, int]] = {}
    for name, (early, late, users) in objects.items():
        if len(users) != len(early) or len(users) != len(late):
            raise RuntimeError(f"unaligned object cannot be cached: {name}")
        payload[f"{name}__early"] = early
        payload[f"{name}__late"] = late
        manifest_objects[name] = {"n_rows": int(len(early)), "n_features": int(early.shape[1])}
    cross_blocks: dict[str, dict[str, int]] = {}
    for left, right in (("static_full", "hybrid_full"), ("static_full", "dynamic_full"),
                        ("hybrid_full", "dynamic_full")):
        if left not in objects or right not in objects:
            continue
        left_early, left_late, left_users = objects[left]
        right_early, right_late, right_users = objects[right]
        right_positions = {user: position for position, user in enumerate(right_users)}
        left_positions = [position for position, user in enumerate(left_users) if user in right_positions]
        right_positions_aligned = [right_positions[left_users[position]] for position in left_positions]
        name = f"cross_{left.removesuffix('_full')}_{right.removesuffix('_full')}"
        payload[f"{name}__{left.removesuffix('_full')}__early"] = left_early[left_positions]
        payload[f"{name}__{left.removesuffix('_full')}__late"] = left_late[left_positions]
        payload[f"{name}__{right.removesuffix('_full')}__early"] = right_early[right_positions_aligned]
        payload[f"{name}__{right.removesuffix('_full')}__late"] = right_late[right_positions_aligned]
        cross_blocks[name] = {
            "n_rows": int(len(left_positions)),
            "left_features": int(left_early.shape[1]),
            "right_features": int(right_early.shape[1]),
        }
    np.savez_compressed(path, **payload)
    path.with_name(f"{path.stem}_manifest.json").write_text(json.dumps({
        "run": "SUICA_V6_NUMERIC_OBJECT_CACHE_V2",
        "contains_raw_text": False,
        "contains_tokens_or_terms": False,
        "contains_author_identifiers": False,
        "objects": manifest_objects,
        "cross_block_numeric_sets": cross_blocks,
    }, indent=2) + "\n")


def _condition_overlap_masks(
    units: pd.DataFrame,
    objects: dict[str, tuple[np.ndarray, np.ndarray, list[str]]],
) -> dict[str, np.ndarray]:
    """Build ID-free early/late condition-overlap masks for numerical sensitivity checks."""
    sets = (units.groupby(["user_id", "half"], observed=True)["condition"]
            .agg(lambda values: set(map(str, values))).to_dict())
    masks: dict[str, np.ndarray] = {}
    for name, (_, _, users) in objects.items():
        overlap = []
        for user in users:
            early, late = sets.get((user, "early"), set()), sets.get((user, "late"), set())
            union = early | late
            overlap.append(len(early & late) / len(union) if union else 0.0)
        values = np.asarray(overlap, dtype=float)
        masks[f"{name}__condition_jaccard_ge_005"] = values >= 0.05
        masks[f"{name}__condition_jaccard_ge_010"] = values >= 0.10
    return masks


def _append_cache_masks(path: Path, masks: dict[str, np.ndarray]) -> None:
    """Append numeric-only condition masks and record only aggregate counts."""
    with np.load(path) as existing:
        payload = {key: existing[key] for key in existing.files}
    payload.update({key: value.astype(np.uint8) for key, value in masks.items()})
    np.savez_compressed(path, **payload)
    manifest_path = path.with_name(f"{path.stem}_manifest.json")
    manifest = json.loads(manifest_path.read_text())
    manifest["condition_overlap_masks"] = {
        key: {"n_rows": int(len(mask)), "n_kept": int(mask.sum())}
        for key, mask in masks.items()
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


def _report(rows: pd.DataFrame, *, cfg: dict, permutation_iterations: int,
            subsample_iterations: int, familywise_tests: int) -> str:
    display = rows[[
        "object", "n_users", "n_features", "status", "linear_cka",
        "linear_cka_bonferroni_p", "distance_spearman", "distance_spearman_bonferroni_p",
        "neighbour_jaccard", "neighbour_jaccard_bonferroni_p", "effective_rank_early",
        "effective_rank_late", "intrinsic_dimension_early", "intrinsic_dimension_late", "spectrum_cosine",
    ]].copy()
    template = r"""# SUICA V6 Residual Geometry Audit

## Scope

This is a numeric-only audit. A discovery-fitted representation maps source text
to coordinates once; immediately after that transformation, all analysis uses
only paired author-by-feature matrices. No token, term, raw text, author ID,
questionnaire, or psychological construct name is read or exported.

For author `u`, let `R_u^(E)` and `R_u^(L)` be early and late opportunity-
conditioned residual coordinates. The audit asks whether their **relational
geometry** reproduces:

\[
K^{(h)} = H R^{(h)}R^{(h)\top}H,
\qquad
\operatorname{CKA}(E,L)=
\frac{\langle K^{(E)},K^{(L)}\rangle_F}
{\lVert K^{(E)}\rVert_F\lVert K^{(L)}\rVert_F}.
\]

It also compares rank order of pairwise distances, top-`k` neighbourhood overlap,
covariance-spectrum similarity, and local intrinsic dimension. The null retains
both point clouds but permutes the early-to-late author linkage. Thus a positive
result says that author relations reproduce more than arbitrary linkage; it does
not establish personality, causality, or a named factor.

## Frozen settings

- representation dimensions: `__REPRESENTATION_DIMENSIONS__`
- dynamic residual coordinates: `__DYNAMIC_DIMENSIONS__`
- permutation draws: `__PERMUTATIONS__`
- subsample draws: `__SUBSAMPLES__`
- familywise correction: Bonferroni across `__FAMILYWISE_TESTS__` object-metric tests
- neighbourhood size: `10`
- no factor naming, lexical export, or external labels

## Results

__RESULT_TABLE__

## Reading rule

`LINKAGE_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN` requires all three paired-linkage
permutation tests (CKA, distance-rank concordance, and neighbourhood overlap) to
have Bonferroni-adjusted `p < .05`. It is a detection result, not a practical-strength acceptance:
this analysis did not preregister a material effect-size margin.
`PARTIAL_LINKAGE_GEOMETRY_ONLY` is descriptive and cannot support a construct claim. A positive
linkage geometry can still arise from idiolect, social niche, latent topic,
unobserved opportunity, or persistent state; these are not resolved by a linkage
permutation.

The static and dynamic objects remain subject to the V6 identification rule:
without repeated common conditions and independent technical replicas, a dynamic
configuration cannot be promoted to a stable author operator or personality
dimension.
"""
    return (template
            .replace("__REPRESENTATION_DIMENSIONS__", str(cfg["representation_dimensions"]))
            .replace("__DYNAMIC_DIMENSIONS__", str(cfg["dynamic_dimensions"]))
            .replace("__PERMUTATIONS__", str(permutation_iterations))
            .replace("__SUBSAMPLES__", str(subsample_iterations))
            .replace("__FAMILYWISE_TESTS__", str(familywise_tests))
            .replace("__RESULT_TABLE__", display.to_markdown(index=False, floatfmt=".4f")))


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(f"Missing input: {args.input}")
    cfg = json.loads(args.config.read_text())
    cfg["quick"] = args.quick
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, cfg)
    static, hybrid, dynamic, discovery_users, confirmation_users = _make_numeric_objects(units, cfg)

    objects: dict[str, tuple[np.ndarray, np.ndarray, list[str]]] = {}
    for family, frame, offset in (("static", static, 0), ("hybrid", hybrid, 500), ("dynamic", dynamic, 1000)):
        for view, matrices in family_matrices(family, frame, discovery_users, confirmation_users, cfg, offset).items():
            early, late, users = matrices
            if early.shape[1] > 0:
                objects[f"{family}_{view}"] = (early, late, users)

    if args.numeric_cache is not None:
        _write_numeric_cache(args.numeric_cache, objects)
        _append_cache_masks(args.numeric_cache, _condition_overlap_masks(units, objects))
    if args.cache_only:
        if args.numeric_cache is None:
            raise ValueError("--cache-only requires --numeric-cache")
        return

    permutation_iterations = args.permutation_iterations or (49 if args.quick else 199)
    subsample_iterations = args.subsample_iterations or (16 if args.quick else 64)
    result_rows: list[dict[str, float | str]] = []
    null_rows: list[dict[str, float | str]] = []
    for index, (name, (early, late, users)) in enumerate(objects.items()):
        metrics, null = geometry_audit(
            early, late, neighbourhood_k=10,
            permutation_iterations=permutation_iterations,
            subsample_iterations=subsample_iterations,
            seed=int(cfg["seed"]) + 2000 + index,
        )
        result_rows.append({
            "object": name,
            "n_users": len(users),
            "n_features": early.shape[1],
            **metrics,
        })
        null_rows.extend({"object": name, **row} for row in null)

    familywise_tests = len(result_rows) * 3
    for row in result_rows:
        for metric in ("linear_cka", "distance_spearman", "neighbour_jaccard"):
            row[f"{metric}_bonferroni_p"] = min(1.0, row[f"{metric}_permutation_p"] * familywise_tests)
        row["status"] = geometry_status(row)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = pd.DataFrame(result_rows)
    results.to_csv(args.output_dir / "geometry_metrics.csv", index=False)
    pd.DataFrame(null_rows).to_csv(args.output_dir / "linkage_permutation_null.csv", index=False)
    manifest = {
        "run": "SUICA_V6_RESIDUAL_GEOMETRY_V1",
        "numeric_only_after_representation": True,
        "n_input_comments": int(len(comments)),
        "n_sampled_comments": int(len(units)),
        "n_discovery_users": int(len(discovery_users)),
        "n_confirmation_users": int(len(confirmation_users)),
        "objects": [str(row["object"]) for row in result_rows],
        "permutation_iterations": permutation_iterations,
        "subsample_iterations": subsample_iterations,
        "familywise_tests": familywise_tests,
        "config": cfg,
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    args.report.write_text(_report(
        results, cfg=cfg, permutation_iterations=permutation_iterations,
        subsample_iterations=subsample_iterations, familywise_tests=familywise_tests,
    ))


if __name__ == "__main__":
    main()
