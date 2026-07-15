#!/usr/bin/env python
"""Run label-free J1 geometry for SUICA's natural joint-process object.

J1 asks whether two text-disjoint technical views of the same author retain a
reproducible joint selection-expression-transition geometry. It never reads
Big5, MBTI, clinical, or market labels, and it deliberately retains observed
subreddit selection as part of the natural process rather than residualizing it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.joint_process import (  # noqa: E402
    GAP_LABELS,
    alignment_permutation_test,
    cohort_from_bucket,
    disjoint_block_views,
    gap_bin,
    pairwise_cosine_geometry_correlation,
    row_l2_normalize,
    same_author_auc,
    stable_bucket,
)
from suica_core.suica import PERSONALITY_LEAK_RE  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse explicit local-source and artifact destinations."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True,
                        help="Local gitignored PANDORA Tier-U parquet.")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/v6_joint_process_stage_j1.json")
    parser.add_argument("--calibration", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_joint_process_stage_j1")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_JOINT_PROCESS_STAGE_J1_REPORT.md")
    return parser.parse_args()


def _group_mean(values: np.ndarray, codes: np.ndarray, n_groups: int) -> np.ndarray:
    """Average a dense event feature matrix by an integer group code."""
    array = np.asarray(values, dtype=np.float64)
    sums = np.zeros((n_groups, array.shape[1]), dtype=np.float64)
    np.add.at(sums, codes, array)
    counts = np.bincount(codes, minlength=n_groups).astype(float)
    return sums / np.maximum(counts[:, None], 1.0)


def _hashed_group_distribution(
    hash_codes: np.ndarray, group_codes: np.ndarray, *, n_groups: int, dimensions: int
) -> np.ndarray:
    """Return per-group distributions over a frozen selection hash space."""
    values = np.zeros((n_groups, dimensions), dtype=np.float64)
    np.add.at(values, (group_codes, hash_codes), 1.0)
    counts = np.bincount(group_codes, minlength=n_groups).astype(float)
    return values / np.maximum(counts[:, None], 1.0)


def _view_group_index(selected: pd.DataFrame) -> tuple[np.ndarray, pd.DataFrame]:
    """Factorize author/view pairs and retain only non-text group metadata."""
    keys = selected["author"].astype(str) + "\x1f" + selected["technical_view"].astype(str)
    codes, unique_keys = pd.factorize(keys, sort=True)
    metadata = (
        selected.assign(_view_key=keys)
        .drop_duplicates("_view_key")
        .set_index("_view_key")
        .loc[list(unique_keys), ["author", "technical_view", "cohort"]]
        .reset_index(drop=True)
    )
    return codes.astype(int), metadata


def _block_pairs(selected: pd.DataFrame, group_codes: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return source/destination rows and group/gap codes for within-block pairs."""
    ordered = (
        selected.reset_index(names="_row")
        .sort_values(["author", "technical_view", "technical_block", "within_block_index"], kind="stable")
        .copy()
    )
    block_keys = ["author", "technical_view", "technical_block"]
    ordered["_next_row"] = ordered.groupby(block_keys, observed=True, sort=False)["_row"].shift(-1)
    pairs = ordered.loc[ordered["_next_row"].notna()].copy()
    source = pairs["_row"].to_numpy(dtype=int)
    target = pairs["_next_row"].to_numpy(dtype=int)
    pair_groups = group_codes[source]
    if not np.array_equal(pair_groups, group_codes[target]):
        raise RuntimeError("a technical pair crossed an author/view boundary")
    gaps = selected["created_utc"].to_numpy(float)[target] - selected["created_utc"].to_numpy(float)[source]
    labels = gap_bin(np.maximum(gaps, 0.0))
    lookup = {label: index for index, label in enumerate(GAP_LABELS)}
    gap_codes = np.asarray([lookup[label] for label in labels], dtype=int)
    return source, target, pair_groups, gap_codes


def _technical_components(
    selected: pd.DataFrame,
    text_embedding: np.ndarray,
    *,
    hash_dimensions: int,
    namespace: str,
) -> tuple[dict[str, tuple[np.ndarray, np.ndarray]], np.ndarray, np.ndarray]:
    """Estimate static, selection, transition, and joint view vectors.

    This uses the frozen linear feature-map estimator: event means retain text
    expression plus observed selection; pair means retain source/successor and
    gap distributions. It does not fit a factor model or learn a target head.
    """
    group_codes, group_meta = _view_group_index(selected)
    n_groups = len(group_meta)
    text = np.asarray(text_embedding, dtype=np.float64)
    selection_codes = np.fromiter(
        (stable_bucket(str(value), namespace=f"{namespace}::selection", modulus=hash_dimensions)
         for value in selected["subreddit"]),
        dtype=int,
        count=len(selected),
    )
    expression = _group_mean(text, group_codes, n_groups)
    selection = _hashed_group_distribution(
        selection_codes, group_codes, n_groups=n_groups, dimensions=hash_dimensions
    )
    source, target, pair_groups, gap_codes = _block_pairs(selected, group_codes)
    source_expression = _group_mean(text[source], pair_groups, n_groups)
    target_expression = _group_mean(text[target], pair_groups, n_groups)
    source_selection = _hashed_group_distribution(
        selection_codes[source], pair_groups, n_groups=n_groups, dimensions=hash_dimensions
    )
    target_selection = _hashed_group_distribution(
        selection_codes[target], pair_groups, n_groups=n_groups, dimensions=hash_dimensions
    )
    gap_distribution = _hashed_group_distribution(
        gap_codes, pair_groups, n_groups=n_groups, dimensions=len(GAP_LABELS)
    )
    event_joint = np.hstack([row_l2_normalize(expression), row_l2_normalize(selection)])
    transition_joint = np.hstack([
        row_l2_normalize(source_expression),
        row_l2_normalize(target_expression),
        row_l2_normalize(source_selection),
        row_l2_normalize(target_selection),
        row_l2_normalize(gap_distribution),
    ])
    joint = np.hstack([row_l2_normalize(event_joint), row_l2_normalize(transition_joint)])
    matrices = {
        "selection": selection,
        "expression": expression,
        "event_joint": event_joint,
        "transition_joint": transition_joint,
        "joint": joint,
    }
    left_rows = group_meta.loc[group_meta["technical_view"].eq("left")].copy()
    right_rows = group_meta.loc[group_meta["technical_view"].eq("right")].copy()
    left_lookup = dict(zip(left_rows["author"].astype(str), left_rows.index, strict=True))
    right_lookup = dict(zip(right_rows["author"].astype(str), right_rows.index, strict=True))
    authors = np.asarray(sorted(set(left_lookup).intersection(right_lookup)), dtype=object)
    cohorts = np.asarray(
        [str(group_meta.loc[left_lookup[author], "cohort"]) for author in authors], dtype=object
    )
    components = {
        name: (matrix[[left_lookup[author] for author in authors]], matrix[[right_lookup[author] for author in authors]])
        for name, matrix in matrices.items()
    }
    return components, authors, cohorts


def _vectorizer(name: str, *, max_features: int) -> TfidfVectorizer:
    """Build one of the two frozen, label-free text representation views."""
    common: dict[str, Any] = {
        "min_df": 2,
        "max_df": 0.95,
        "max_features": max_features,
        "sublinear_tf": True,
        "strip_accents": "unicode",
        "dtype": np.float32,
    }
    if name == "word_1to2_tfidf_svd":
        return TfidfVectorizer(analyzer="word", ngram_range=(1, 2), **common)
    if name == "char_3to5_tfidf_svd":
        return TfidfVectorizer(analyzer="char", ngram_range=(3, 5), **common)
    raise ValueError(f"unsupported frozen representation: {name}")


def _fit_text_embedding(selected: pd.DataFrame, *, name: str, spec: dict[str, Any], seed: int) -> tuple[np.ndarray, dict[str, Any]]:
    """Fit text vocabulary/SVD on discovery authors and transform all views."""
    discovery_mask = selected["cohort"].eq(str(spec["fit_cohort"])).to_numpy()
    if not discovery_mask.any():
        raise RuntimeError("J1 discovery cohort is empty")
    vectorizer = _vectorizer(name, max_features=int(spec["text_max_features"]))
    discovery_text = selected.loc[discovery_mask, "body"].tolist()
    train_matrix = vectorizer.fit_transform(discovery_text)
    n_components = min(
        int(spec["text_svd_dimensions"]),
        train_matrix.shape[0] - 1,
        train_matrix.shape[1] - 1,
    )
    if n_components < 2:
        raise RuntimeError(f"{name} vocabulary is too small for J1 SVD")
    svd = TruncatedSVD(n_components=n_components, n_iter=5, random_state=seed)
    discovery_embedding = svd.fit_transform(train_matrix)
    scaler = StandardScaler().fit(discovery_embedding)
    embedding = np.empty((len(selected), n_components), dtype=np.float32)
    embedding[discovery_mask] = scaler.transform(discovery_embedding).astype(np.float32)
    for cohort in ("calibration", "confirmation"):
        cohort_mask = selected["cohort"].eq(cohort).to_numpy()
        if cohort_mask.any():
            matrix = vectorizer.transform(selected.loc[cohort_mask, "body"].tolist())
            embedding[cohort_mask] = scaler.transform(svd.transform(matrix)).astype(np.float32)
    return embedding, {
        "representation": name,
        "vocabulary_size": int(len(vectorizer.vocabulary_)),
        "svd_dimensions": int(n_components),
        "explained_variance_ratio": float(np.sum(svd.explained_variance_ratio_)),
        "fit_cohort": str(spec["fit_cohort"]),
        "fit_documents": int(discovery_mask.sum()),
    }


def _load_selected_comments(input_path: Path, cfg: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load local raw text only in memory and construct J1 technical views."""
    if not input_path.exists():
        raise FileNotFoundError(f"missing local PANDORA source: {input_path}")
    comments = pd.read_parquet(input_path, columns=["author", "body", "created_utc", "subreddit"])
    source_rows = len(comments)
    comments["body"] = comments["body"].fillna("").astype(str)
    leak_mask = comments["body"].map(lambda text: bool(PERSONALITY_LEAK_RE.search(text)))
    min_chars = int(cfg["j0"]["minimum_body_characters"])
    valid = comments.loc[~leak_mask & comments["body"].str.len().ge(min_chars)].copy()
    valid["created_utc"] = pd.to_numeric(valid["created_utc"], errors="coerce")
    valid = valid.dropna(subset=["created_utc"])
    selected = disjoint_block_views(
        valid,
        min_events_per_view=int(cfg["calibration"]["candidate_support_pairs"][0]["min_events"]),
        min_transitions_per_view=int(cfg["calibration"]["candidate_support_pairs"][0]["min_transitions"]),
        block_size=int(cfg["j0"]["technical_replication"]["nonoverlap_block_size"]),
    ).reset_index(drop=True)
    selected["cohort"] = selected["author"].astype(str).map(
        lambda author: cohort_from_bucket(stable_bucket(author, namespace=str(cfg["namespace"])))
    )
    expected_per_view = int(cfg["calibration"]["candidate_support_pairs"][0]["min_events"])
    counts = selected.groupby(["author", "technical_view"], observed=True).size()
    if counts.empty or not counts.eq(expected_per_view).all():
        raise RuntimeError("technical view construction did not retain the calibrated event count")
    provenance = {
        "n_source_comments": int(source_rows),
        "n_excluded_personality_leakage": int(leak_mask.sum()),
        "n_after_text_guard": int(len(valid)),
        "n_selected_events": int(len(selected)),
        "n_selected_authors": int(selected["author"].nunique()),
        "technical_events_per_author_view": expected_per_view,
        "raw_text_persisted": False,
        "external_labels_read": False,
    }
    return selected, provenance


def _metrics_for_representation(
    components: dict[str, tuple[np.ndarray, np.ndarray]],
    cohorts: np.ndarray,
    *,
    representation: str,
) -> pd.DataFrame:
    """Compute same-author geometry AUCs in each author-disjoint cohort."""
    rows: list[dict[str, Any]] = []
    for cohort in ("discovery", "calibration", "confirmation"):
        mask = cohorts == cohort
        for component, (left, right) in components.items():
            if int(mask.sum()) < 4:
                continue
            rows.append({
                "representation": representation,
                "cohort": cohort,
                "component": component,
                "n_authors": int(mask.sum()),
                "same_author_auc": float(same_author_auc(left[mask], right[mask])),
            })
    return pd.DataFrame(rows)


def main() -> None:
    """Execute J1 with no endpoint labels and emit aggregate-only artifacts."""
    args = parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    calibration_path = args.calibration or ROOT / cfg["j0"]["calibration_artifact"]
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    if calibration.get("decision") != "CALIBRATED" or not calibration.get("selected_support"):
        raise RuntimeError("J1 requires a completed synthetic calibration")
    selected_support = calibration["selected_support"]
    expected = cfg["calibration"]["candidate_support_pairs"][0]
    if selected_support != expected:
        raise RuntimeError("J1 implementation currently requires the predeclared 24/8 calibration support")
    selected, provenance = _load_selected_comments(args.input, cfg)
    j1 = cfg["j1_preview"]
    cohort_sizes = selected.groupby("cohort", observed=True)["author"].nunique().to_dict()
    if int(cohort_sizes.get("confirmation", 0)) < int(j1["minimum_confirmation_authors"]):
        raise RuntimeError("confirmation cohort does not meet the J1 frozen author minimum")
    all_metrics: list[pd.DataFrame] = []
    representation_metadata: list[dict[str, Any]] = []
    confirmation_midpoints: dict[str, np.ndarray] = {}
    alignment_rows: list[dict[str, Any]] = []
    for representation_index, representation in enumerate(j1["representations"]):
        embedding, metadata = _fit_text_embedding(
            selected, name=str(representation), spec=j1,
            seed=int(cfg["seed"]) + representation_index,
        )
        components, authors, cohorts = _technical_components(
            selected, embedding, hash_dimensions=int(j1["selection_hash_dimensions"]),
            namespace=str(cfg["namespace"]),
        )
        metrics = _metrics_for_representation(components, cohorts, representation=str(representation))
        all_metrics.append(metrics)
        confirmation = cohorts == "confirmation"
        left_joint, right_joint = components["joint"]
        alignment = alignment_permutation_test(
            left_joint[confirmation], right_joint[confirmation],
            permutations=int(j1["permutations"]), seed=int(cfg["seed"]) + 10_000 + representation_index,
        )
        alignment_rows.append({"representation": representation, "n_confirmation_authors": int(confirmation.sum()), **alignment})
        confirmation_midpoints[str(representation)] = row_l2_normalize(
            (left_joint[confirmation] + right_joint[confirmation]) / 2.0
        )
        representation_metadata.append(metadata)
    metrics_frame = pd.concat(all_metrics, ignore_index=True)
    alignment_frame = pd.DataFrame(alignment_rows)
    first, second = [str(value) for value in j1["representations"]]
    cross_rep_r = pairwise_cosine_geometry_correlation(
        confirmation_midpoints[first], confirmation_midpoints[second]
    )
    promotion = j1["promotion"]
    joint_confirmation = metrics_frame.loc[
        metrics_frame["cohort"].eq("confirmation") & metrics_frame["component"].eq("joint")
    ].set_index("representation")
    both_auc_pass = all(
        float(joint_confirmation.loc[representation, "same_author_auc"]) >= float(promotion["minimum_joint_auc"])
        for representation in j1["representations"]
    )
    both_randomization_pass = bool(
        alignment_frame["permutation_p"].le(float(promotion["maximum_alignment_permutation_p"])).all()
    )
    cross_rep_pass = bool(np.isfinite(cross_rep_r) and cross_rep_r >= float(promotion["minimum_cross_rep_geometry_r"]))
    decision = "J1_GEOMETRY_REPLICATES" if all([both_auc_pass, both_randomization_pass, cross_rep_pass]) else "J1_NOT_PROMOTED"
    result = {
        "run_name": cfg["run_name"],
        "stage": "J1",
        "calibration": calibration,
        "provenance": provenance,
        "cohort_author_counts": {name: int(value) for name, value in cohort_sizes.items()},
        "representation_metadata": representation_metadata,
        "alignment": alignment_rows,
        "cross_representation_confirmation_geometry_r": float(cross_rep_r),
        "decision": decision,
        "promotion_criteria": promotion,
        "external_labels_read": False,
        "raw_text_persisted": False,
        "claim_boundary": "reproducible_natural_joint_process_geometry_only",
        "ordered_dependence_tested": False,
        "ordered_dependence_boundary": (
            "The transition_joint component retains source and successor marginals. "
            "It cannot show that chronological ordering contributes beyond those marginals."
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metrics_frame.to_csv(args.output_dir / "j1_component_auc.csv", index=False)
    alignment_frame.to_csv(args.output_dir / "j1_alignment_permutation.csv", index=False)
    (args.output_dir / "j1_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(f"""# SUICA V6 Joint-Process J1: Label-Free Geometry

## Question

Can two text-disjoint technical views of each author reproduce the same
**natural joint selection-expression-transition geometry**? Observed subreddit
selection remains in the object. This is neither a topic-removal experiment nor
a personality prediction test.

## Frozen data boundary

- source comments seen in memory: `{provenance['n_source_comments']}`
- excluded by explicit personality-report guard: `{provenance['n_excluded_personality_leakage']}`
- selected technical-view events: `{provenance['n_selected_events']}`
- selected authors: `{provenance['n_selected_authors']}`
- events per author per disjoint view: `{provenance['technical_events_per_author_view']}`
- external labels read: `False`
- raw text persisted: `False`

## Same-author geometry

{metrics_frame.round(4).to_markdown(index=False)}

## Primary confirmation randomization test

{alignment_frame.round(4).to_markdown(index=False)}

## Cross-representation confirmation geometry

- word/character joint-geometry correlation: `{cross_rep_r:.4f}`

## Frozen decision

`{decision}`.

J1 promotion requires both independent text representations to reach
same-author AUC >= `{promotion['minimum_joint_auc']}`, each shuffled-alignment
randomization p <= `{promotion['maximum_alignment_permutation_p']}`, and
cross-representation confirmation geometry r >= `{promotion['minimum_cross_rep_geometry_r']}`.

## Interpretation boundary

Passing J1 supports a representation-bounded, author-conditioned natural
text-process geometry under this corpus and this technical split. It does not
identify a personality factor, causal condition effect, clinical state,
cross-language invariant, or a real repeated human occasion. In particular,
`transition_joint` contains source and successor **marginals**; its high AUC
does not yet show that chronological order adds stable author information.
The next valid step is a separately frozen, centred ordered-transition operator
against a within-block order-shuffle null; it is not an external-scale analysis.
""", encoding="utf-8")
    print(json.dumps({"decision": decision, "cross_representation_r": cross_rep_r}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
