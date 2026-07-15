#!/usr/bin/env python
"""Test whether V6 static geometry transports across text representations.

The source corpus is used only to create two discovery-fitted coordinate maps:
word/bigram TF-IDF and character n-gram TF-IDF.  Once author-by-coordinate
matrices are constructed, all statistics operate on numbers only.  The script
does not inspect, export, or report terms, raw text, author IDs, labels, or
psychological names.
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
    conditional_residual,
    crossfit_residuals,
    fit_representation,
    opportunity_axis,
    prepare_units,
    stable_user_split,
)
from scripts.run_suica_v6_residual_source_audit import family_matrices  # noqa: E402
from suica_core.residual_geometry import aligned_geometry_permutation_test  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path,
        default=ROOT / "data_sets" / "prepared" / "suica_tiers_v2" / "tier_u_comments.parquet",
    )
    parser.add_argument("--config", type=Path, default=ROOT / "configs/v6_factor_discovery_raw.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_representation_transport")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_REPRESENTATION_TRANSPORT_REPORT.md")
    parser.add_argument("--max-users", type=int, default=384,
                        help="Fixed confirmation subsample for tractable paired permutation tests.")
    parser.add_argument("--permutation-iterations", type=int, default=999)
    parser.add_argument("--quick", action="store_true", help="Use 128 authors and 99 permutations.")
    return parser.parse_args()


def fit_char_representation(units: pd.DataFrame, discovery_users: set[str], cfg: dict):
    """Fit a discovery-only character n-gram coordinate map without exporting its vocabulary."""
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer

    mask = units["user_id"].isin(discovery_users)
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        analyzer="char_wb",
        ngram_range=(3, 5),
        max_features=cfg["tfidf_max_features"],
        min_df=cfg["tfidf_min_df"],
        max_df=0.98,
        sublinear_tf=True,
        dtype=np.float32,
    )
    tf_discovery = vectorizer.fit_transform(units.loc[mask, "text"])
    svd = TruncatedSVD(n_components=cfg["representation_dimensions"], random_state=cfg["seed"] + 101)
    svd.fit(tf_discovery)
    coordinates = svd.transform(vectorizer.transform(units["text"])).astype(np.float64)
    return vectorizer, svd, coordinates


def _stable_subsample(users: list[str], maximum: int, seed: int) -> np.ndarray:
    """Select an ID-internal, reproducible subset without exporting identifiers."""
    if maximum < 12:
        raise ValueError("max-users must be at least 12")
    if len(users) <= maximum:
        return np.arange(len(users))
    digest = np.asarray([
        int.from_bytes(
            hashlib.blake2b(f"{seed}:{user}".encode("utf-8"), digest_size=8).digest(), "little"
        )
        for user in users
    ], dtype=np.uint64)
    return np.argsort(digest, kind="stable")[:maximum]


def _static_views(
    units: pd.DataFrame,
    discovery_users: set[str],
    confirmation_users: set[str],
    cfg: dict,
    *,
    representation: str,
) -> dict[str, tuple[np.ndarray, np.ndarray, list[str]]]:
    """Produce frozen confirmation static views for one representation family."""
    fitter = fit_representation if representation == "word" else fit_char_representation
    _, _, coordinates = fitter(units, discovery_users, cfg)
    residual, supported_conditions = crossfit_residuals(units, coordinates, discovery_users, cfg)
    opportunity, _ = opportunity_axis(units, discovery_users, supported_conditions)
    static, hybrid, dynamic_raw, _ = build_objects(units, residual, opportunity, cfg)
    # These calls preserve the registered static construction before extracting its views.
    hybrid = conditional_residual(hybrid, [static], "hybrid::", discovery_users)
    _ = conditional_residual(
        dynamic_raw, [static] + ([hybrid] if len(hybrid) else []), "dynamic::", discovery_users
    )
    return family_matrices(
        "static", static, discovery_users, confirmation_users, cfg,
        seed_offset=0 if representation == "word" else 101,
    )


def _transport_rows(
    word: dict[str, tuple[np.ndarray, np.ndarray, list[str]]],
    char: dict[str, tuple[np.ndarray, np.ndarray, list[str]]],
    *,
    maximum: int,
    iterations: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run row-linkage permutation tests for cross-representation geometry."""
    comparisons = (("word_early__char_early", 0, 0), ("word_late__char_late", 1, 1),
                   ("word_early__char_late", 0, 1), ("word_late__char_early", 1, 0))
    result_rows: list[dict[str, float | str]] = []
    null_rows: list[dict[str, float | str]] = []
    for view_number, view in enumerate(("full", "residual")):
        word_early, word_late, word_users = word[view]
        char_early, char_late, char_users = char[view]
        if word_users != char_users:
            raise RuntimeError("representation views do not preserve confirmation author alignment")
        index = _stable_subsample(word_users, maximum, seed + view_number)
        word_halves = (word_early[index], word_late[index])
        char_halves = (char_early[index], char_late[index])
        for comparison_number, (comparison, left_half, right_half) in enumerate(comparisons):
            metrics, null = aligned_geometry_permutation_test(
                word_halves[left_half], char_halves[right_half],
                neighbourhood_k=10,
                iterations=iterations,
                seed=seed + 1000 * view_number + comparison_number,
            )
            result_rows.append({
                "object": f"static_{view}",
                "comparison": comparison,
                "n_users": int(len(index)),
                "word_features": int(word_halves[left_half].shape[1]),
                "char_features": int(char_halves[right_half].shape[1]),
                **metrics,
            })
            null_rows.extend({
                "object": f"static_{view}", "comparison": comparison, **row
            } for row in null)
    results = pd.DataFrame(result_rows)
    familywise_tests = len(results) * 4
    for metric in ("linear_cka", "rbf_cka", "distance_spearman", "neighbour_jaccard"):
        results[f"{metric}_bonferroni_p"] = np.minimum(
            1.0, results[f"{metric}_permutation_p"] * familywise_tests,
        )
    required = ("linear_cka_bonferroni_p", "rbf_cka_bonferroni_p",
                "distance_spearman_bonferroni_p", "neighbour_jaccard_bonferroni_p")
    results["status"] = np.where(
        (results[list(required)] < 0.05).all(axis=1),
        "CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN",
        np.where(
            (results[list(required)] < 0.05).any(axis=1),
            "PARTIAL_CROSS_REPRESENTATION_GEOMETRY_ONLY",
            "NO_CROSS_REPRESENTATION_GEOMETRY_DETECTED",
        ),
    )
    return results, pd.DataFrame(null_rows)


def _report(results: pd.DataFrame, *, cfg: dict, max_users: int, iterations: int) -> str:
    display_columns = [
        "object", "comparison", "n_users", "status", "linear_cka", "linear_cka_bonferroni_p",
        "rbf_cka", "rbf_cka_bonferroni_p", "distance_spearman", "distance_spearman_bonferroni_p",
        "neighbour_jaccard", "neighbour_jaccard_bonferroni_p",
    ]
    table = results[display_columns].to_markdown(index=False, floatfmt=".4f")
    return f"""# SUICA V6 Representation-Transport Audit

## Scope

This audit asks a restricted numerical question: after the same registered
opportunity conditioning and author aggregation, do author relations survive a
change from a word/bigram TF-IDF coordinate map to a character 3--5 gram TF-IDF
coordinate map? Raw text is used only to fit discovery-side maps. All tests
below operate on numeric confirmation matrices. No vocabulary, text, author ID,
external label, or construct name is exported or inspected.

For a representation `r` and half `h`, the object is a point cloud
`R^(r,h)`. Cross-representation correspondence is tested through linear and RBF
kernel alignment, pairwise-distance rank concordance, and top-10 neighbour
overlap. The null permutes only the row linkage between the two point clouds.

## Frozen settings

- representation dimensions per map: `{cfg['representation_dimensions']}`
- confirmation authors per comparison: at most `{max_users}` (fixed hash subset)
- linkage permutations: `{iterations}`
- familywise correction: Bonferroni across `{len(results) * 4}` tests
- examined views: complete static configuration and static residual configuration
- examined comparisons: same-half and cross-half word/character geometry

## Results

{table}

## Reading rule

`CROSS_REPRESENTATION_GEOMETRY_DETECTED_NO_MATERIAL_MARGIN` means that all four
numeric correspondence tests survive the stated familywise correction. It shows
only that a relational configuration is not tied to one coordinate basis. It
does not establish semantic invariance, causal source, stable author trait,
personality, or a usable score. Same-half results alone demonstrate mapping
correspondence; cross-half results are needed before calling the result a
representation-transport property.
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
    word = _static_views(units, discovery_users, confirmation_users, cfg, representation="word")
    char = _static_views(units, discovery_users, confirmation_users, cfg, representation="char")
    results, null = _transport_rows(
        word, char, maximum=maximum, iterations=iterations, seed=int(cfg["seed"]) + 4100,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output_dir / "representation_transport_metrics.csv", index=False)
    null.to_csv(args.output_dir / "representation_transport_permutation_null.csv", index=False)
    manifest = {
        "run": "SUICA_V6_REPRESENTATION_TRANSPORT_V1",
        "numeric_only_after_representation": True,
        "contains_raw_text": False,
        "contains_tokens_or_terms": False,
        "contains_author_identifiers": False,
        "n_input_comments": int(len(comments)),
        "n_sampled_comments": int(len(units)),
        "n_discovery_users": int(len(discovery_users)),
        "n_confirmation_users": int(len(confirmation_users)),
        "max_confirmation_users_per_comparison": int(maximum),
        "permutation_iterations": int(iterations),
        "familywise_tests": int(len(results) * 4),
        "config": cfg,
    }
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    args.report.write_text(_report(results, cfg=cfg, max_users=maximum, iterations=iterations))


if __name__ == "__main__":
    main()
