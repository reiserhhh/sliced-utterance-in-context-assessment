#!/usr/bin/env python3
"""Diagnose the SUICA V8 geometry-to-behavior bridge without new LLM calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
import run_suica_v8_interpreter_stability as interpreter  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_bridge import (  # noqa: E402
    EVENT_CODES,
    QuantileGeometryProjector,
    RidgeBehaviorBridge,
    cross_modal_author_auc,
    cross_modal_feature_metrics,
    distance_alignment,
    effective_rank,
    fit_opportunity_baseline,
    profile_repeated_behavior_features,
    segment_event_repetition_frame,
    select_behavior_columns,
    select_ridge_alpha,
    supported_profile_rate,
)
from suica_core.v8_realtext import DIRECTIVE_RE, FIRST_PERSON_RE  # noqa: E402


DEFAULT_CONFIG = ROOT / "configs" / "v8_geometry_behavior_bridge.json"
DEFAULT_OUTPUT = ROOT / "results" / "v8_geometry_behavior_bridge" / "pandora_primary"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _load_observer_runs(
    source: Path,
    *,
    repetitions: int,
) -> list[dict[str, Any]]:
    runs = []
    for repetition in range(int(repetitions)):
        events: dict[str, list[dict[str, Any]]] = {}
        ready_files = 0
        refused_files = 0
        paths = sorted(
            (source / "cache" / "observer").glob(
                f"pandora-r{repetition:02d}-observer-b*.json"
            )
        )
        if not paths:
            raise FileNotFoundError(
                f"observer cache repetition {repetition} is missing"
            )
        for path in paths:
            payload = _read_json(path)
            if payload.get("status") != "STRUCTURED_STAGE_READY":
                refused_files += 1
                continue
            ready_files += 1
            events.update(interpreter._events_by_profile(payload.get("output")))
        runs.append({
            "observer": events,
            "cache_files": len(paths),
            "ready_files": ready_files,
            "refused_files": refused_files,
        })
    return runs


def _rebuild_inputs(
    source_config: dict[str, Any],
    observer_runs: list[dict[str, Any]],
) -> tuple[
    pd.DataFrame,
    dict[str, np.ndarray],
    list[dict[str, Any]],
    dict[str, list[dict[str, Any]]],
    pd.DataFrame,
]:
    semantic, geometry_panel = pandora._load_panels(source_config)
    metadata, geometry, bundle = pandora._score_geometry(
        semantic,
        geometry_panel,
        max_authors=int(
            source_config["real_text"]["max_authors"]["pandora"]
        ),
    )
    complete_profile_ids = set.intersection(*[
        set(run["observer"]) for run in observer_runs
    ])
    complete_authors = {
        str(author)
        for author in metadata["author_id"].astype(str)
        if (
            f"{author}::left" in complete_profile_ids
            and f"{author}::right" in complete_profile_ids
        )
    }
    kept = np.asarray([
        index
        for index, author in enumerate(metadata["author_id"].astype(str))
        if author in complete_authors
    ])
    metadata = metadata.iloc[kept].reset_index(drop=True)
    geometry = {side: values[kept] for side, values in geometry.items()}
    semantic = semantic.loc[
        semantic["author_id"].isin(complete_authors)
    ].copy()
    thresholds = pandora._reference_thresholds(metadata, geometry)
    profiles = pandora._make_profiles(
        semantic,
        metadata,
        geometry,
        thresholds,
        bundle=bundle,
    )
    consensus = pandora._consensus_events(profiles, observer_runs)
    return metadata, geometry, profiles, consensus, semantic


def _profile_matrix(
    profiles: list[dict[str, Any]],
    behavior: pd.DataFrame,
) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
    profile_order = [str(profile["profile_id"]) for profile in profiles]
    lookup = behavior.set_index("profile_id")
    missing = sorted(set(profile_order) - set(lookup.index.astype(str)))
    if missing:
        raise ValueError(f"behavior profiles are missing: {missing[:3]}")
    aligned = lookup.loc[profile_order].reset_index()
    geometry = np.vstack([
        np.asarray(profile["geometry_vector"], dtype=float)
        for profile in profiles
    ])
    return aligned, geometry, np.asarray(profile_order, dtype=str)


def _mean_abs_correlation(values: np.ndarray) -> float:
    # Constant or nearly constant quantile columns are a diagnostic outcome,
    # not an exceptional condition.
    with np.errstate(divide="ignore", invalid="ignore"):
        correlation = np.corrcoef(values, rowvar=False)
    return float(
        np.abs(correlation[np.triu_indices_from(correlation, k=1)]).mean()
    )


def _principal_fraction(values: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh(np.cov(values, rowvar=False, ddof=1))
    eigenvalues = np.clip(eigenvalues, 0.0, None)
    return float(eigenvalues[-1] / eigenvalues.sum())


def _bh_adjust(p_values: list[float]) -> np.ndarray:
    values = np.asarray(p_values, dtype=float)
    order = np.argsort(values, kind="stable")
    adjusted = np.empty(len(values), dtype=float)
    running = 1.0
    for rank_index in range(len(values) - 1, -1, -1):
        original = order[rank_index]
        rank = rank_index + 1
        running = min(running, values[original] * len(values) / rank)
        adjusted[original] = running
    return np.clip(adjusted, 0.0, 1.0)


def _register_relations(
    geometry: np.ndarray,
    behavior: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    geometry_names: list[str],
    behavior_names: list[str],
    seed: int,
    draws: int = 500,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    unique_authors = np.unique(authors)
    geometry_width = geometry.shape[1]
    joined = np.column_stack([geometry, behavior])
    association = spearmanr(joined, axis=0)
    statistic = np.asarray(association.statistic)
    p_values = np.asarray(association.pvalue)
    correlation = statistic[:geometry_width, geometry_width:]
    relation_p = p_values[:geometry_width, geometry_width:]
    half_correlation = {}
    for side in ("left", "right"):
        mask = np.asarray(sides) == side
        half_statistic = np.asarray(
            spearmanr(joined[mask], axis=0).statistic
        )
        half_correlation[side] = half_statistic[
            :geometry_width, geometry_width:
        ]
    sign_matches = np.zeros_like(correlation, dtype=float)
    finite_draws = np.zeros_like(correlation, dtype=float)
    author_indices = {
        author: np.flatnonzero(authors == author) for author in unique_authors
    }
    for _ in range(int(draws)):
        sampled = rng.choice(
            unique_authors,
            size=len(unique_authors),
            replace=True,
        )
        indices = np.concatenate([author_indices[author] for author in sampled])
        boot_statistic = np.asarray(
            spearmanr(joined[indices], axis=0).statistic
        )
        boot = boot_statistic[:geometry_width, geometry_width:]
        finite = np.isfinite(boot)
        finite_draws += finite
        sign_matches += finite & (np.sign(boot) == np.sign(correlation))
    sign_stability = np.divide(
        sign_matches,
        finite_draws,
        out=np.zeros_like(sign_matches),
        where=finite_draws > 0,
    )
    rows: list[dict[str, Any]] = []
    for geometry_index, geometry_name in enumerate(geometry_names):
        for behavior_index, behavior_name in enumerate(behavior_names):
            value = float(correlation[geometry_index, behavior_index])
            left = float(half_correlation["left"][geometry_index, behavior_index])
            right = float(half_correlation["right"][geometry_index, behavior_index])
            side_agreement = bool(
                np.isfinite(value)
                and value != 0
                and np.isfinite(left)
                and np.isfinite(right)
                and np.sign(left) == np.sign(value)
                and np.sign(right) == np.sign(value)
            )
            rows.append({
                "geometry_feature": geometry_name,
                "behavior_feature": behavior_name,
                "spearman_r": value,
                "p_value": float(relation_p[geometry_index, behavior_index]),
                "left_spearman_r": left,
                "right_spearman_r": right,
                "bootstrap_sign_stability": float(
                    sign_stability[geometry_index, behavior_index]
                ),
                "cross_half_sign_agreement": side_agreement,
            })
    frame = pd.DataFrame(rows)
    frame["q_value"] = _bh_adjust(frame["p_value"].fillna(1.0).tolist())
    frame["eligible"] = (
        frame["spearman_r"].abs().ge(0.15)
        & frame["bootstrap_sign_stability"].ge(0.80)
        & frame["cross_half_sign_agreement"]
        & frame["q_value"].le(0.10)
    )
    return frame


def _opposite_lookup(authors: np.ndarray, sides: np.ndarray) -> np.ndarray:
    lookup = {
        (str(author), str(side)): index
        for index, (author, side) in enumerate(zip(authors, sides, strict=True))
    }
    return np.asarray([
        lookup[(str(author), "right" if str(side) == "left" else "left")]
        for author, side in zip(authors, sides, strict=True)
    ])


def _registered_candidate_rate(
    geometry: np.ndarray,
    behavior: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    relations: pd.DataFrame,
    *,
    geometry_names: list[str],
    behavior_names: list[str],
) -> float:
    eligible = relations.loc[relations["eligible"]]
    if eligible.empty:
        return 0.0
    geometry_lookup = {name: index for index, name in enumerate(geometry_names)}
    behavior_lookup = {name: index for index, name in enumerate(behavior_names)}
    opposite = _opposite_lookup(authors, sides)
    supported = []
    for row_index in range(len(geometry)):
        found = False
        for relation in eligible.itertuples(index=False):
            g = float(geometry[
                row_index, geometry_lookup[str(relation.geometry_feature)]
            ])
            b = float(behavior[
                opposite[row_index],
                behavior_lookup[str(relation.behavior_feature)],
            ])
            if abs(g) < 0.50 or abs(b) < 0.50:
                continue
            expected = np.sign(g) * np.sign(float(relation.spearman_r))
            if np.sign(b) == expected:
                found = True
                break
        supported.append(found)
    return float(np.mean(supported))


def _query_auc_values(
    predicted: np.ndarray,
    observed: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
) -> dict[str, float]:
    values: dict[str, list[float]] = {}
    for index, (author, side) in enumerate(zip(authors, sides, strict=True)):
        targets = np.flatnonzero(sides != side)
        labels = (authors[targets] == author).astype(int)
        if labels.sum() != 1 or len(labels) < 2:
            continue
        scores = -np.linalg.norm(
            observed[targets] - predicted[index][None, :],
            axis=1,
        )
        positive = float(scores[labels == 1][0])
        negatives = scores[labels == 0]
        query_auc = float(
            (np.sum(positive > negatives) + 0.5 * np.sum(positive == negatives))
            / len(negatives)
        )
        values.setdefault(str(author), []).append(query_auc)
    return {
        author: float(np.mean(author_values))
        for author, author_values in values.items()
    }


def _bootstrap_auc_interval(
    predicted: np.ndarray,
    observed: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    seed: int,
    draws: int = 5000,
) -> tuple[float, float, float]:
    per_author = _query_auc_values(predicted, observed, authors, sides)
    values = np.asarray(list(per_author.values()), dtype=float)
    if not len(values):
        return float("nan"), float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    samples = [
        float(rng.choice(values, size=len(values), replace=True).mean())
        for _ in range(int(draws))
    ]
    return (
        float(values.mean()),
        float(np.quantile(samples, 0.025)),
        float(np.quantile(samples, 0.975)),
    )


def _distance_permutation_p(
    geometry: np.ndarray,
    behavior: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    observed: float,
    seed: int,
    permutations: int = 5000,
) -> float:
    rng = np.random.default_rng(seed)
    unique_authors = np.unique(authors)
    author_rows = {
        author: np.flatnonzero(authors == author) for author in unique_authors
    }
    null = []
    for _ in range(int(permutations)):
        permuted_authors = rng.permutation(unique_authors)
        shuffled = np.empty(len(behavior), dtype=int)
        for source_author, target_author in zip(
            unique_authors,
            permuted_authors,
            strict=True,
        ):
            source_rows = author_rows[source_author]
            target_rows = author_rows[target_author]
            target_by_side = {
                str(sides[row]): row for row in target_rows
            }
            if len(source_rows) != len(target_rows):
                raise ValueError("paired permutation requires equal half counts")
            for source_row in source_rows:
                shuffled[source_row] = target_by_side[str(sides[source_row])]
        value = distance_alignment(
            geometry,
            behavior[shuffled],
            authors,
        )["distance_spearman"]
        if np.isfinite(value):
            null.append(value)
    return float(
        (1 + np.sum(np.asarray(null) >= float(observed))) / (len(null) + 1)
    )


def _evaluate(
    geometry: np.ndarray,
    behavior: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    bridge: RidgeBehaviorBridge,
    relations: pd.DataFrame,
    *,
    geometry_names: list[str],
    behavior_names: list[str],
    seed: int,
    full_inference: bool,
) -> dict[str, Any]:
    predicted = bridge.predict(geometry)
    observed = bridge.observed_z(behavior)
    result: dict[str, Any] = {
        "profiles": int(len(geometry)),
        "authors": int(len(np.unique(authors))),
        "cross_modal_author_auc": cross_modal_author_auc(
            predicted,
            observed,
            authors,
            sides,
        ),
        "cross_modal_author_auc_cosine": cross_modal_author_auc(
            predicted,
            observed,
            authors,
            sides,
            metric="cosine",
        ),
        "geometry_self_author_auc": cross_modal_author_auc(
            geometry,
            geometry,
            authors,
            sides,
        ),
        "behavior_self_author_auc": cross_modal_author_auc(
            observed,
            observed,
            authors,
            sides,
        ),
        **cross_modal_feature_metrics(
            predicted,
            observed,
            authors,
            sides,
        ),
        **distance_alignment(geometry, observed, authors),
        "technical_coverage": float(
            np.mean(
                np.isfinite(geometry).all(axis=1)
                & np.isfinite(observed).all(axis=1)
            )
        ),
        "evidence_supported_profile_rate": supported_profile_rate(
            predicted,
            observed,
            authors,
            sides,
        ),
        "registered_link_candidate_rate": _registered_candidate_rate(
            geometry,
            observed,
            authors,
            sides,
            relations,
            geometry_names=geometry_names,
            behavior_names=behavior_names,
        ),
    }
    if full_inference:
        auc = _bootstrap_auc_interval(
            predicted,
            observed,
            authors,
            sides,
            seed=seed,
        )
        result.update({
            "cross_modal_author_auc_cluster_estimate": auc[0],
            "cross_modal_author_auc_ci_lower": auc[1],
            "cross_modal_author_auc_ci_upper": auc[2],
            "distance_permutation_p": _distance_permutation_p(
                geometry,
                observed,
                authors,
                sides,
                observed=float(result["distance_spearman"]),
                seed=seed + 1,
            ),
        })
    return result


def _anchor_agreement(segments: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for event_code, pattern in (
        ("self_reference", FIRST_PERSON_RE),
        ("directive_expression", DIRECTIVE_RE),
    ):
        observed = segments[event_code].to_numpy(int)
        anchor = segments["text"].astype(str).map(
            lambda value: int(bool(pattern.search(value)))
        ).to_numpy(int)
        true_positive = int(np.sum((observed == 1) & (anchor == 1)))
        false_positive = int(np.sum((observed == 0) & (anchor == 1)))
        false_negative = int(np.sum((observed == 1) & (anchor == 0)))
        precision = true_positive / max(1, true_positive + false_positive)
        recall = true_positive / max(1, true_positive + false_negative)
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0.0
        )
        rows.append({
            "event_code": event_code,
            "deterministic_anchor": pattern.pattern,
            "llm_consensus_prevalence": float(observed.mean()),
            "anchor_prevalence": float(anchor.mean()),
            "precision_treating_llm_as_reference": precision,
            "recall_treating_llm_as_reference": recall,
            "f1_treating_llm_as_reference": f1,
            "claim_boundary": "agreement diagnostic, not observer accuracy",
        })
    return pd.DataFrame(rows)


def _report(
    *,
    decision: dict[str, Any],
    diagnostics: dict[str, Any],
    calibration: pd.DataFrame,
    confirmation: pd.DataFrame,
) -> str:
    selected = str(decision["selected_variant"])
    selected_row = confirmation.loc[
        confirmation["variant_id"].eq(selected)
    ].iloc[0]
    raw_row = confirmation.loc[
        confirmation["variant_id"].eq("raw_single")
    ].iloc[0]
    return f"""# SUICA V8 Geometry-Behavior Bridge Diagnostic

Execution decision: `{decision["status"]}`

## Question

Can the frozen, anonymous SUICA distance distribution recover explicit
behavior patterns across source-disjoint halves after removing its dominant
common distance mode?

This run made **no new LLM calls** and read **no personality, diagnosis,
clinical, or market labels**. Existing source-bound observer caches were
reused exactly.

## Mathematical object

The V7 profile is a sorted distance function
`Q_u(p_j) = d_(j)(u)`, not a coordinate vector with identified landmarks.
Variants therefore compare the raw quantile profile with discovery-fitted
location/scale/shape, tangent-FPCA, shape-FPCA, and gap-FPCA views.

Behavior is represented as single-event rates, context-conditioned residuals,
within-segment co-occurrences, and adjacent-segment transitions. The
opportunity baseline is fitted on discovery contexts only:

`R_uk = mean_s [I(event k in s) - P_discovery(k | condition_s)]`.

## Diagnosis before modeling

- raw geometry mean absolute inter-column correlation:
  {diagnostics["raw_geometry_mean_abs_correlation"]:.3f}
- raw geometry effective rank:
  {diagnostics["raw_geometry_effective_rank"]:.3f} / 16
- first principal variance share:
  {diagnostics["raw_geometry_pc1_fraction"]:.3f}
- profiles/authors:
  {diagnostics["profiles"]}/{diagnostics["authors"]}

This confirms that the earlier 14 nominal dimension links mostly repeated one
common radial/quantile mode.

## Calibration selection

The selected variant was `{selected}`. Variant selection used calibration
only; confirmation was not used to choose representation, behavior features,
or ridge strength.

{calibration.to_markdown(index=False)}

## Frozen confirmation

{confirmation.to_markdown(index=False)}

Selected versus raw-single confirmation:

- cross-modal same-author AUC:
  {selected_row["cross_modal_author_auc"]:.3f} versus
  {raw_row["cross_modal_author_auc"]:.3f};
- element-wise opposite-half Spearman:
  {selected_row["element_spearman"]:.3f} versus
  {raw_row["element_spearman"]:.3f};
- geometry/behavior distance Spearman:
  {selected_row["distance_spearman"]:.3f} versus
  {raw_row["distance_spearman"]:.3f};
- supported profile rate:
  {selected_row["evidence_supported_profile_rate"]:.3f} versus
  {raw_row["evidence_supported_profile_rate"]:.3f}.

## Interpretation boundary

`{decision["interpretation"]}`

These are geometry-to-explicit-behavior results, not personality validity.
Even a passing bridge would only justify a constrained behavior renderer.
Psychological construct interpretation still requires external behavioral or
psychometric validation.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    source = ROOT / str(config["source_run"])
    source_config_path = source / "config.resolved.json"
    source_config = _read_json(source_config_path)
    source_inventory = verify_artifact_inventory(source / "artifact_inventory.json")
    if source_inventory["status"] != "INVENTORY_PASS":
        raise RuntimeError("source V8 interpreter artifact inventory failed")

    observer_runs = _load_observer_runs(
        source,
        repetitions=int(source_config["real_text"]["observer_repetitions"]),
    )
    metadata, geometry_by_side, profiles, consensus, semantic = _rebuild_inputs(
        source_config,
        observer_runs,
    )
    condition_by_segment = semantic.set_index("segment_id")[
        "condition"
    ].astype(str).to_dict()
    segment_frame = segment_event_repetition_frame(
        profiles,
        observer_runs,
        condition_by_segment=condition_by_segment,
    )
    segment_text = {
        str(profile["profile_id"]): {
            str(segment["segment_id"]): " ".join(
                str(span.get("text", "")) for span in segment.get("spans", [])
            )
            for segment in profile["segments"]
        }
        for profile in profiles
    }
    segment_frame["text"] = [
        segment_text[str(row.profile_id)][str(row.segment_id)]
        for row in segment_frame.itertuples(index=False)
    ]
    discovery_segments = segment_frame.loc[
        segment_frame["cohort_split"].eq("discovery")
    ]
    opportunity = fit_opportunity_baseline(
        discovery_segments,
        shrinkage=float(config["opportunity_shrinkage"]),
    )
    behavior = profile_repeated_behavior_features(
        segment_frame,
        opportunity=opportunity,
    )
    aligned, raw_geometry, profile_ids = _profile_matrix(profiles, behavior)
    split = aligned["cohort_split"].astype(str).to_numpy()
    authors = aligned["author_id"].astype(str).to_numpy()
    sides = aligned["side"].astype(str).to_numpy()
    discovery_mask = split == "discovery"
    calibration_mask = split == "calibration"
    confirmation_mask = split == "confirmation"

    discovery_raw = raw_geometry[discovery_mask]
    diagnostics = {
        "authors": int(len(metadata)),
        "profiles": int(len(profiles)),
        "split_authors": {
            str(key): int(value)
            for key, value in metadata["split"].value_counts().items()
        },
        "raw_geometry_dimensions": int(raw_geometry.shape[1]),
        "raw_geometry_mean_abs_correlation": _mean_abs_correlation(discovery_raw),
        "raw_geometry_effective_rank": effective_rank(discovery_raw),
        "raw_geometry_pc1_fraction": _principal_fraction(discovery_raw),
        "observer_cache_repetitions": int(len(observer_runs)),
        "observer_cache_files": int(sum(
            run["cache_files"] for run in observer_runs
        )),
        "observer_cache_ready_files": int(sum(
            run["ready_files"] for run in observer_runs
        )),
        "observer_cache_refused_files": int(sum(
            run["refused_files"] for run in observer_runs
        )),
        "event_profile_prevalence": {
            code: float(
                segment_frame.groupby(
                    "profile_id",
                    observed=True,
                )[code].max().mean()
            )
            for code in EVENT_CODES
        },
        "source_inventory_status": source_inventory["status"],
        "external_labels_read": False,
        "new_llm_calls": 0,
    }

    variant_state: dict[str, dict[str, Any]] = {}
    calibration_rows: list[dict[str, Any]] = []
    relation_frames: list[pd.DataFrame] = []
    for variant in config["variants"]:
        variant_id = str(variant["variant_id"])
        projector = QuantileGeometryProjector(
            family=str(variant["geometry_family"]),
            variance_target=float(config["geometry_variance_target"]),
            max_components=int(config["geometry_max_components"]),
        )
        projector.fit(
            discovery_raw,
            authors=authors[discovery_mask],
            sides=sides[discovery_mask],
        )
        geometry_values = projector.transform(raw_geometry)
        behavior_columns = select_behavior_columns(
            behavior,
            feature_set=str(variant["behavior_feature_set"]),
            discovery_mask=discovery_mask,
            minimum_nonzero_profiles=int(config["minimum_nonzero_profiles"]),
            maximum_nonzero_fraction=float(
                config["maximum_nonzero_fraction"]
            ),
        )
        if not behavior_columns:
            raise RuntimeError(f"variant {variant_id} has no behavior features")
        behavior_values = aligned[behavior_columns].to_numpy(float)
        alpha, alpha_scores = select_ridge_alpha(
            geometry_values[discovery_mask],
            behavior_values[discovery_mask],
            authors[discovery_mask],
            sides[discovery_mask],
            alphas=config["ridge_alphas"],
            folds=int(config["inner_group_folds"]),
        )
        bridge = RidgeBehaviorBridge(alpha=alpha).fit(
            geometry_values[discovery_mask],
            behavior_values[discovery_mask],
        )
        discovery_behavior_z = bridge.observed_z(
            behavior_values[discovery_mask]
        )
        relations = _register_relations(
            geometry_values[discovery_mask],
            discovery_behavior_z,
            authors[discovery_mask],
            sides[discovery_mask],
            geometry_names=list(projector.output_names),
            behavior_names=behavior_columns,
            seed=int(config["seed"]) + len(calibration_rows) * 101,
        )
        relations.insert(0, "variant_id", variant_id)
        relation_frames.append(relations)
        metrics = _evaluate(
            geometry_values[calibration_mask],
            behavior_values[calibration_mask],
            authors[calibration_mask],
            sides[calibration_mask],
            bridge,
            relations,
            geometry_names=list(projector.output_names),
            behavior_names=behavior_columns,
            seed=int(config["seed"]) + 1000 + len(calibration_rows),
            full_inference=False,
        )
        eligible = relations.loc[relations["eligible"]]
        metrics.update({
            "variant_id": variant_id,
            "geometry_family": str(variant["geometry_family"]),
            "behavior_feature_set": str(variant["behavior_feature_set"]),
            "geometry_dimensions": int(geometry_values.shape[1]),
            "behavior_dimensions": int(len(behavior_columns)),
            "ridge_alpha": float(alpha),
            "inner_cv_auc": float(alpha_scores[alpha]),
            "stable_links": int(len(eligible)),
            "behavior_targets": int(eligible["behavior_feature"].nunique()),
        })
        calibration_rows.append(metrics)
        variant_state[variant_id] = {
            "projector": projector,
            "geometry": geometry_values,
            "behavior_columns": behavior_columns,
            "behavior": behavior_values,
            "bridge": bridge,
            "relations": relations,
        }

    calibration_frame = pd.DataFrame(calibration_rows)
    selected_row = calibration_frame.sort_values(
        [
            str(config["selection"]["primary_metric"]),
            *map(str, config["selection"]["tie_breakers"]),
            "variant_id",
        ],
        ascending=[False, False, False, True],
        kind="stable",
    ).iloc[0]
    selected_variant = str(selected_row["variant_id"])
    confirmation_variants = list(dict.fromkeys([
        "raw_single",
        selected_variant,
    ]))
    confirmation_rows = []
    for offset, variant_id in enumerate(confirmation_variants):
        state = variant_state[variant_id]
        metrics = _evaluate(
            state["geometry"][confirmation_mask],
            state["behavior"][confirmation_mask],
            authors[confirmation_mask],
            sides[confirmation_mask],
            state["bridge"],
            state["relations"],
            geometry_names=list(state["projector"].output_names),
            behavior_names=state["behavior_columns"],
            seed=int(config["seed"]) + 3000 + offset,
            full_inference=True,
        )
        eligible = state["relations"].loc[state["relations"]["eligible"]]
        metrics.update({
            "variant_id": variant_id,
            "geometry_family": state["projector"].family,
            "behavior_feature_set": next(
                str(row["behavior_feature_set"])
                for row in config["variants"]
                if str(row["variant_id"]) == variant_id
            ),
            "geometry_dimensions": int(state["geometry"].shape[1]),
            "behavior_dimensions": int(len(state["behavior_columns"])),
            "ridge_alpha": float(state["bridge"].alpha),
            "stable_links": int(len(eligible)),
            "behavior_targets": int(eligible["behavior_feature"].nunique()),
        })
        confirmation_rows.append(metrics)
    confirmation_frame = pd.DataFrame(confirmation_rows)
    final = confirmation_frame.loc[
        confirmation_frame["variant_id"].eq(selected_variant)
    ].iloc[0]
    gates = config["confirmation_gates"]
    multivariate_checks = {
        "cross_modal_author_auc": (
            float(final["cross_modal_author_auc"])
            >= float(gates["minimum_cross_modal_author_auc"])
        ),
        "auc_cluster_lower": (
            float(final["cross_modal_author_auc_ci_lower"])
            >= float(gates["minimum_auc_bootstrap_lower"])
        ),
        "element_spearman": (
            float(final["element_spearman"])
            >= float(gates["minimum_element_spearman"])
        ),
        "distance_alignment": (
            float(final["distance_spearman"])
            >= float(gates["minimum_distance_spearman"])
            and float(final["distance_permutation_p"])
            <= float(gates["maximum_distance_permutation_p"])
        ),
        "technical_coverage": (
            float(final["technical_coverage"])
            >= float(gates["minimum_technical_coverage"])
        ),
        "evidence_supported_profile_rate": (
            float(final["evidence_supported_profile_rate"])
            >= float(gates["minimum_evidence_supported_profile_rate"])
        ),
        "geometry_self_auc": (
            float(final["geometry_self_author_auc"])
            >= float(gates["minimum_geometry_self_auc"])
        ),
        "behavior_self_auc": (
            float(final["behavior_self_author_auc"])
            >= float(gates["minimum_behavior_self_auc"])
        ),
    }
    interpretable_checks = {
        "stable_links": (
            int(final["stable_links"])
            >= int(gates["minimum_stable_links"])
        ),
        "behavior_target_diversity": (
            int(final["behavior_targets"])
            >= int(gates["minimum_behavior_targets"])
        ),
        "registered_candidate_coverage": (
            float(final["registered_link_candidate_rate"])
            >= float(gates["minimum_evidence_supported_profile_rate"])
        ),
    }
    multivariate_pass = all(multivariate_checks.values())
    interpretable_pass = all(interpretable_checks.values())
    if (
        not multivariate_checks["geometry_self_auc"]
        and not multivariate_checks["behavior_self_auc"]
    ):
        root_cause = "BOTH_VIEWS_INSUFFICIENT_AT_CURRENT_RESOLUTION"
    elif not multivariate_checks["geometry_self_auc"]:
        root_cause = "SORTED_QUANTILE_GEOMETRY_INSUFFICIENT"
    elif not multivariate_checks["behavior_self_auc"]:
        root_cause = "OBSERVER_BEHAVIOR_VIEW_INSUFFICIENT"
    elif not multivariate_pass:
        root_cause = "CROSS_MODAL_MAP_NOT_CONFIRMED"
    elif not interpretable_pass:
        root_cause = "DISTRIBUTED_RELATION_NOT_SPARSELY_RENDERABLE"
    else:
        root_cause = "NO_FAILURE_AT_CURRENT_GATE"
    if multivariate_pass and interpretable_pass:
        status = "V8_GEOMETRY_BEHAVIOR_BRIDGE_PASS"
        interpretation_text = (
            "A source-disjoint, multivariate and sparsely interpretable "
            "geometry-to-behavior bridge survived confirmation."
        )
    elif multivariate_pass:
        status = "V8_DISTRIBUTED_BRIDGE_ONLY"
        interpretation_text = (
            "A distributed geometry-to-behavior relation survived, but it "
            "did not reduce to enough stable behavior links for rendering."
        )
    else:
        status = "V8_BRIDGE_STOP_NO_CONFIRMATION"
        interpretation_text = (
            "Decorrelation and behavior-pattern expansion did not produce a "
            "confirmed source-disjoint bridge. Do not spend new LLM calls on "
            "renderer tuning; revise the measured intermediate object."
        )
    raw_final = confirmation_frame.loc[
        confirmation_frame["variant_id"].eq("raw_single")
    ].iloc[0]
    decision = {
        "status": status,
        "selected_variant": selected_variant,
        "root_cause": root_cause,
        "selection_split": "calibration",
        "final_split": "confirmation",
        "multivariate_checks": multivariate_checks,
        "interpretable_checks": interpretable_checks,
        "selected_confirmation": final.to_dict(),
        "raw_single_confirmation": raw_final.to_dict(),
        "delta_vs_raw_single": {
            key: float(final[key] - raw_final[key])
            for key in (
                "cross_modal_author_auc",
                "element_spearman",
                "distance_spearman",
                "evidence_supported_profile_rate",
            )
        },
        "interpretation": interpretation_text,
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.output_dir / "config.resolved.json", config)
    _write_json(args.output_dir / "geometry_diagnostics.json", diagnostics)
    _write_json(args.output_dir / "decision.json", decision)
    calibration_frame.to_csv(
        args.output_dir / "variant_calibration_metrics.csv",
        index=False,
    )
    confirmation_frame.to_csv(
        args.output_dir / "confirmation_metrics.csv",
        index=False,
    )
    relation_frame = pd.concat(relation_frames, ignore_index=True)
    relation_frame.to_csv(
        args.output_dir / "registered_relation_audit.csv",
        index=False,
    )
    inventory_rows = []
    for variant_id, state in variant_state.items():
        for column in state["behavior_columns"]:
            inventory_rows.append({
                "variant_id": variant_id,
                "behavior_feature": column,
            })
    pd.DataFrame(inventory_rows).to_csv(
        args.output_dir / "behavior_feature_inventory.csv",
        index=False,
    )
    anchor_frame = _anchor_agreement(segment_frame)
    anchor_frame.to_csv(
        args.output_dir / "observer_anchor_agreement.csv",
        index=False,
    )
    report = _report(
        decision=decision,
        diagnostics=diagnostics,
        calibration=calibration_frame,
        confirmation=confirmation_frame,
    )
    (args.output_dir / "report.md").write_text(report, encoding="utf-8")
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            source / "artifact_inventory.json",
            source / "decision.json",
            source_config_path,
            pandora.PANDORA_COMMENTS_PATH,
            pandora.ELIGIBLE_AUTHORS_PATH,
            pandora.REPRESENTATION_PATH,
            pandora.GEOMETRY_PATH,
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_bridge.py",
            ROOT / "scripts" / "run_suica_v8_interpreter_pandora.py",
        ],
        estimand_id="V8-I3-pandora-quantile-geometry-behavior-bridge",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0 if status != "V8_BRIDGE_STOP_NO_CONFIRMATION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
