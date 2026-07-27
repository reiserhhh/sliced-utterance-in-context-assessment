#!/usr/bin/env python3
"""Run the primary real-text gate for the SUICA V8 interpreter."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_interpreter_stability as base  # noqa: E402
from suica_core.v7_geometry import GeometryBundle, score_geometry_bundle  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    append_ledger_event,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v7_psychometric import author_features_from_embeddings  # noqa: E402
from suica_core.v8_interpreter import (  # noqa: E402
    consensus_set,
    evidence_edge_set,
    fleiss_kappa_multilabel,
    idf_weights,
    interpretation_atom_key,
    interpretation_forbidden_count,
    mean_pairwise_set_f1,
    mean_pairwise_weighted_jaccard,
    pairwise_nominal_kappa,
    set_f1,
    set_jaccard,
    validate_behavior_payload,
)
from suica_core.v8_realtext import load_pandora_source_disjoint_panels  # noqa: E402
from suica_core.v8_semantic import OpenAICompatibleProvider  # noqa: E402


DEFAULT_DATA_ROOT = Path("/Volumes/mobile3/projects/project persona/data_sets")
PANDORA_COMMENTS_PATH = (
    DEFAULT_DATA_ROOT / "prepared" / "suica_tiers_v2" / "tier_u_comments.parquet"
)
ELIGIBLE_AUTHORS_PATH = (
    ROOT
    / "results"
    / "v7_multiview_projection"
    / "e1_v72_full_20260715"
    / "author_features_native.csv"
)
REPRESENTATION_PATH = (
    ROOT
    / "results"
    / "v7_multiview_projection"
    / "e1_v72_full_20260715"
    / "artifacts"
    / "common_source_comment_representation.joblib"
)
GEOMETRY_PATH = (
    ROOT
    / "results"
    / "v7_geometry"
    / "g1_corrected_v2_full_20260715"
    / "geometry_bundle.json"
)


def _load_panels(
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    real = config["real_text"]
    eligible = pd.read_csv(
        ELIGIBLE_AUTHORS_PATH,
        usecols=["user_id", "split"],
        dtype={"user_id": str},
    )
    split_limits = {
        str(split): int(len(group))
        for split, group in eligible.groupby("split", observed=True)
    }
    semantic, geometry = load_pandora_source_disjoint_panels(
        PANDORA_COMMENTS_PATH,
        eligible_authors=eligible,
        max_by_split=split_limits,
        semantic_segments_per_author=int(real["segments_per_author"]),
        geometry_units_per_half=int(real["pandora_geometry_units_per_half"]),
        seed=int(config["seed"]),
    )
    return semantic, geometry


def _score_geometry(
    semantic: pd.DataFrame,
    geometry: pd.DataFrame,
    *,
    max_authors: int,
) -> tuple[pd.DataFrame, dict[str, np.ndarray], GeometryBundle]:
    representation = joblib.load(REPRESENTATION_PATH)
    bundle = GeometryBundle.from_dict(json.loads(GEOMETRY_PATH.read_text(encoding="utf-8")))
    side_profiles: dict[str, pd.DataFrame] = {}
    side_status: dict[str, np.ndarray] = {}
    for side in ("left", "right"):
        observations = geometry.loc[geometry["split"].eq(side)].reset_index(drop=True)
        embeddings = representation.transform(observations["text"])
        features = author_features_from_embeddings(observations, embeddings).set_index(
            "user_id"
        )
        result = score_geometry_bundle(
            bundle,
            features[bundle.feature_names].to_numpy(float),
            unit_counts=features["n_units"].to_numpy(int),
        )
        dimensions = [
            f"D{index + 1:03d}"
            for index in range(np.asarray(result["landmark_distance_profile"]).shape[1])
        ]
        frame = pd.DataFrame(
            np.asarray(result["landmark_distance_profile"]),
            index=features.index.astype(str),
            columns=dimensions,
        )
        side_profiles[side] = frame
        side_status[side] = np.asarray(result["status"], dtype=object)
        side_profiles[side]["_ready"] = side_status[side] == "GEOMETRY_PROFILE_READY"

    metadata = semantic[["author_id", "split"]].drop_duplicates()
    ready_ids = set(side_profiles["left"].index[side_profiles["left"]["_ready"]])
    ready_ids &= set(side_profiles["right"].index[side_profiles["right"]["_ready"]])
    metadata = metadata.loc[metadata["author_id"].isin(ready_ids)].copy()
    metadata["_order"] = metadata["author_id"].map(
        lambda value: hashlib.sha256(
            f"pandora-interpreter::{value}".encode("utf-8")
        ).hexdigest()
    )
    split_targets = {
        "discovery": int(np.ceil(max_authors * 0.50)),
        "calibration": int(np.floor(max_authors * 0.25)),
        "confirmation": int(max_authors)
        - int(np.ceil(max_authors * 0.50))
        - int(np.floor(max_authors * 0.25)),
    }
    pieces = []
    for split, group in metadata.groupby("split", observed=True, sort=False):
        pieces.append(
            group.sort_values("_order", kind="stable").head(
                max(1, split_targets.get(str(split), 1))
            )
        )
    metadata = pd.concat(pieces, ignore_index=True).drop(columns="_order")
    ordered = metadata["author_id"].astype(str).tolist()
    profiles = {
        side: side_profiles[side].loc[ordered].drop(columns="_ready").to_numpy(float)
        for side in ("left", "right")
    }
    return metadata.reset_index(drop=True), profiles, bundle


def _reference_thresholds(
    metadata: pd.DataFrame,
    profiles: dict[str, np.ndarray],
) -> dict[str, dict[str, float]]:
    discovery = metadata["split"].astype(str).eq("discovery").to_numpy()
    combined = np.vstack([
        profiles["left"][discovery],
        profiles["right"][discovery],
    ])
    thresholds = {}
    for dimension in range(combined.shape[1]):
        values = combined[:, dimension]
        thresholds[f"D{dimension + 1:03d}"] = {
            "lower": float(np.quantile(values, 1 / 3)),
            "upper": float(np.quantile(values, 2 / 3)),
            "clear_lower": float(np.quantile(values, 0.20)),
            "clear_upper": float(np.quantile(values, 0.80)),
        }
    return thresholds


def _geometry_band(value: float, thresholds: dict[str, float]) -> tuple[str, str]:
    if value <= thresholds["lower"]:
        return (
            "lower_reference_band",
            "clear" if value <= thresholds["clear_lower"] else "borderline",
        )
    if value >= thresholds["upper"]:
        return (
            "upper_reference_band",
            "clear" if value >= thresholds["clear_upper"] else "borderline",
        )
    return "central_reference_band", "central"


def _make_profiles(
    semantic: pd.DataFrame,
    metadata: pd.DataFrame,
    geometry: dict[str, np.ndarray],
    thresholds: dict[str, dict[str, float]],
    *,
    bundle: GeometryBundle,
) -> list[dict[str, Any]]:
    metadata_lookup = metadata.set_index("author_id")["split"].astype(str).to_dict()
    row_lookup = {
        str(author): index
        for index, author in enumerate(metadata["author_id"].astype(str))
    }
    profiles = []
    for author_id in metadata["author_id"].astype(str):
        author_rows = semantic.loc[semantic["author_id"].eq(author_id)].sort_values(
            "unit_index",
            kind="stable",
        )
        for side, parity in (("left", 0), ("right", 1)):
            selected = author_rows.loc[author_rows["unit_index"].mod(2).eq(parity)]
            dimensions = []
            vector = geometry[side][row_lookup[author_id]]
            for dimension_index, value in enumerate(vector):
                dimension_id = f"D{dimension_index + 1:03d}"
                band, uncertainty = _geometry_band(
                    float(value),
                    thresholds[dimension_id],
                )
                dimensions.append({
                    "dimension_id": dimension_id,
                    "reference_band": band,
                    "uncertainty_band": uncertainty,
                    "support_status": "supported",
                })
            profile_id = f"{author_id}::{side}"
            segments = [
                {
                    "segment_id": str(row.segment_id),
                    "spans": [{
                        "span_id": str(row.span_id),
                        "text": str(row.text),
                    }],
                }
                for row in selected.itertuples(index=False)
            ]
            condition_hashes = sorted({
                hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]
                for value in selected["condition"].astype(str)
            })
            segment_token_counts = [
                len(str(value).split()) for value in selected["text"]
            ]
            profiles.append({
                "profile_id": profile_id,
                "author_id": author_id,
                "side": side,
                "cohort_split": metadata_lookup[author_id],
                "segments": segments,
                "suica_packet": {
                    "reference_population_id": bundle.bundle_id,
                    "measurement_channel": "frozen_suica_v7_geometry",
                    "overall_support": "supported",
                    "dimensions": dimensions,
                },
                "registered_links": [],
                "expected_events": [],
                "target_event_code": "",
                "target_dimension_id": "",
                "geometry_vector": vector.tolist(),
                "nuisance_signature": {
                    "condition_hashes": condition_hashes,
                    "mean_segment_tokens": float(np.mean(segment_token_counts)),
                    "std_segment_tokens": float(np.std(segment_token_counts)),
                },
            })
    return profiles


def _run_observer_repetition(
    *,
    profiles: list[dict[str, Any]],
    repetition: int,
    output_dir: Path,
    provider: OpenAICompatibleProvider,
    observer_spec,
    batch_size: int,
    concurrency: int,
) -> dict[str, Any]:
    batches = base._batch_profiles(profiles, batch_size=batch_size)
    jobs = []
    for batch_index, batch in enumerate(batches):
        expected, spans, segments = base._behavior_validation_context(batch)
        validator = lambda value, e=expected, s=spans, p=segments: validate_behavior_payload(
            value,
            schema=observer_spec.schema,
            expected_profiles=e,
            spans_by_segment=s,
            segments_by_profile=p,
            return_audit=True,
        )
        run_id = f"pandora-r{repetition:02d}-observer-b{batch_index:03d}"
        jobs.append({
            "cache_path": output_dir / "cache" / "observer" / f"{run_id}.json",
            "provider": provider,
            "spec": observer_spec,
            "payload": base._observer_payload(batch),
            "run_id": run_id,
            "validator": validator,
        })
    results = base._stage_jobs(jobs, concurrency=concurrency)
    events: dict[str, list[dict[str, Any]]] = {}
    for result in results:
        events.update(base._events_by_profile(result.get("output")))
    return {"observer": events, "stage_results": results}


def _consensus_events(
    profiles: list[dict[str, Any]],
    observer_runs: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    threshold = int(np.ceil(len(observer_runs) * 2 / 3))
    for profile in profiles:
        profile_id = str(profile["profile_id"])
        records: dict[str, list[dict[str, Any]]] = {}
        for run in observer_runs:
            for event in run["observer"].get(profile_id, []):
                records.setdefault(str(event["event_id"]), []).append(event)
        selected = []
        for event_id, appearances in records.items():
            if len(appearances) < threshold:
                continue
            first = appearances[0]
            selected.append({
                "event_id": event_id,
                "segment_id": str(first["segment_id"]),
                "event_code": str(first["event_code"]),
                "evidence_span_ids": sorted(set().union(*[
                    set(map(str, event["evidence_span_ids"]))
                    for event in appearances
                ])),
            })
        output[profile_id] = sorted(
            selected,
            key=lambda row: (row["segment_id"], row["event_code"]),
        )
    return output


def _fit_links(
    profiles: list[dict[str, Any]],
    events: dict[str, list[dict[str, Any]]],
    *,
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], pd.DataFrame]:
    real = config["real_text"]
    rows = []
    for profile in profiles:
        row: dict[str, Any] = {
            "profile_id": profile["profile_id"],
            "author_id": profile["author_id"],
            "side": profile["side"],
            "cohort_split": profile["cohort_split"],
        }
        for index, value in enumerate(profile["geometry_vector"]):
            row[f"D{index + 1:03d}"] = float(value)
        summary = {
            item["event_code"]: item["observed_segment_rate"]
            for item in base._event_summary(
                events.get(str(profile["profile_id"]), []),
                segments_per_profile=len(profile["segments"]),
            )
        }
        row.update({f"event::{key}": value for key, value in summary.items()})
        rows.append(row)
    frame = pd.DataFrame(rows)
    discovery = frame.loc[frame["cohort_split"].eq("discovery")].copy()
    authors = discovery["author_id"].drop_duplicates().astype(str).to_numpy()
    rng = np.random.default_rng(int(config["seed"]) + 311)
    links = []
    audit_rows = []
    for dimension in [
        column for column in discovery if column.startswith("D")
    ]:
        candidates = []
        for event_code in base.EVENT_ORDER:
            event_column = f"event::{event_code}"
            if discovery[dimension].nunique() < 2 or discovery[event_column].nunique() < 2:
                correlation = float("nan")
                sign_stability = 0.0
            else:
                correlation = float(spearmanr(
                    discovery[dimension],
                    discovery[event_column],
                ).statistic)
                signs = []
                for _ in range(300):
                    sampled = rng.choice(authors, size=len(authors), replace=True)
                    pieces = [
                        discovery.loc[discovery["author_id"].eq(author)]
                        for author in sampled
                    ]
                    boot = pd.concat(pieces, ignore_index=True)
                    if boot[dimension].nunique() < 2 or boot[event_column].nunique() < 2:
                        continue
                    value = float(spearmanr(
                        boot[dimension],
                        boot[event_column],
                    ).statistic)
                    if np.isfinite(value):
                        signs.append(np.sign(value))
                sign_stability = (
                    float(np.mean(np.asarray(signs) == np.sign(correlation)))
                    if signs and np.isfinite(correlation) and correlation != 0
                    else 0.0
                )
            half_correlations = {}
            for side in ("left", "right"):
                half = discovery.loc[discovery["side"].eq(side)]
                if (
                    half[dimension].nunique() < 2
                    or half[event_column].nunique() < 2
                ):
                    half_correlations[side] = float("nan")
                else:
                    half_correlations[side] = float(spearmanr(
                        half[dimension],
                        half[event_column],
                    ).statistic)
            finite_half_correlations = [
                value for value in half_correlations.values() if np.isfinite(value)
            ]
            half_sign_agreement = bool(
                len(finite_half_correlations) == 2
                and np.sign(finite_half_correlations[0])
                == np.sign(finite_half_correlations[1])
                == np.sign(correlation)
            )
            threshold = float(max(
                1 / max(1, int(real["segments_per_author"]) // 2),
                discovery[event_column].quantile(0.60),
            ))
            eligible = bool(
                np.isfinite(correlation)
                and abs(correlation) >= float(real["association_min_abs_r"])
                and sign_stability >= float(real["association_min_sign_stability"])
                and (
                    not bool(real["require_cross_half_sign_agreement"])
                    or half_sign_agreement
                )
            )
            audit = {
                "dimension_id": dimension,
                "event_code": event_code,
                "spearman_r": correlation,
                "bootstrap_sign_stability": sign_stability,
                "left_half_spearman_r": half_correlations["left"],
                "right_half_spearman_r": half_correlations["right"],
                "cross_half_sign_agreement": half_sign_agreement,
                "event_rate_threshold": threshold,
                "eligible": eligible,
            }
            audit_rows.append(audit)
            if eligible:
                candidates.append(audit)
        candidates.sort(key=lambda row: abs(row["spearman_r"]), reverse=True)
        for candidate in candidates[: int(real["max_links_per_dimension"])]:
            links.append({
                "dimension_id": dimension,
                "event_code": candidate["event_code"],
                "association_direction": (
                    "positive" if candidate["spearman_r"] > 0 else "negative"
                ),
                "registration_source": "pandora_discovery_only",
                "event_rate_threshold": candidate["event_rate_threshold"],
                "discovery_spearman_r": candidate["spearman_r"],
                "bootstrap_sign_stability": candidate["bootstrap_sign_stability"],
                "left_half_spearman_r": candidate["left_half_spearman_r"],
                "right_half_spearman_r": candidate["right_half_spearman_r"],
                "cross_half_sign_agreement": candidate[
                    "cross_half_sign_agreement"
                ],
            })
    return links, pd.DataFrame(audit_rows)


def _attach_links(
    profiles: list[dict[str, Any]],
    links: list[dict[str, Any]],
    events: dict[str, list[dict[str, Any]]],
) -> None:
    for profile in profiles:
        profile["registered_links"] = links
        candidates = base._candidate_atoms(
            profile,
            events.get(str(profile["profile_id"]), []),
        )
        if candidates:
            target = max(
                candidates,
                key=lambda row: len(row["evidence_event_ids"]),
            )
            profile["target_dimension_id"] = target["target_dimension_ids"][0]
            profile["target_event_code"] = target["registered_event_code"]


def _atom_set(profile: dict[str, Any] | None) -> set[str]:
    return base._atom_set(profile)


def _bootstrap_auc(
    positives: np.ndarray,
    negatives: np.ndarray,
    *,
    draws: int,
    seed: int,
) -> tuple[float, float, float]:
    if not len(positives) or not len(negatives):
        return float("nan"), float("nan"), float("nan")
    labels = np.r_[np.ones(len(positives)), np.zeros(len(negatives))]
    scores = np.r_[positives, negatives]
    estimate = float(roc_auc_score(labels, scores))
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(int(draws)):
        positive = positives[rng.integers(0, len(positives), size=len(positives))]
        negative = negatives[rng.integers(0, len(negatives), size=len(negatives))]
        samples.append(roc_auc_score(
            np.r_[np.ones(len(positive)), np.zeros(len(negative))],
            np.r_[positive, negative],
        ))
    return estimate, float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def _information_jaccard(first: set[str], second: set[str]) -> float:
    """Treat two unsupported/empty interpretations as no similarity evidence."""
    return set_jaccard(first, second) if first or second else 0.0


def _nuisance_match(
    source: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> tuple[dict[str, Any], float, float]:
    """Select a stranger by condition overlap, then by text-volume similarity."""
    source_signature = source["nuisance_signature"]
    source_conditions = set(source_signature["condition_hashes"])
    source_tokens = float(source_signature["mean_segment_tokens"])
    ranked = []
    for candidate in candidates:
        signature = candidate["nuisance_signature"]
        candidate_conditions = set(signature["condition_hashes"])
        union = source_conditions.union(candidate_conditions)
        overlap = (
            len(source_conditions.intersection(candidate_conditions)) / len(union)
            if union else 1.0
        )
        token_delta = abs(
            source_tokens - float(signature["mean_segment_tokens"])
        ) / max(source_tokens, float(signature["mean_segment_tokens"]), 1.0)
        ranked.append((
            -overlap,
            token_delta,
            str(candidate["author_id"]),
            candidate,
        ))
    if not ranked:
        raise ValueError("nuisance matching requires at least one stranger")
    negative_overlap, token_delta, _, selected = min(
        ranked,
        key=lambda row: row[:3],
    )
    overlap = -negative_overlap
    return selected, float(overlap), float(token_delta)


def _same_author_metrics(
    profiles: list[dict[str, Any]],
    interpreter_runs: list[dict[str, Any]],
    *,
    draws: int,
    seed: int,
) -> tuple[dict[str, float], dict[str, set[str]], dict[str, set[str]]]:
    heldout = sorted({
        str(profile["author_id"])
        for profile in profiles
        if profile["cohort_split"] != "discovery"
    })
    half_consensus: dict[str, set[str]] = {}
    for profile in profiles:
        if profile["cohort_split"] == "discovery":
            continue
        profile_id = str(profile["profile_id"])
        half_consensus[profile_id] = consensus_set(
            [
                _atom_set(run["interpretation"].get(profile_id))
                for run in interpreter_runs
            ],
            minimum_fraction=0.80,
        )
    author_split = {
        str(profile["author_id"]): str(profile["cohort_split"])
        for profile in profiles
    }
    positives = []
    negatives = []
    deltas = []
    nuisance_condition_overlap = []
    nuisance_token_delta = []
    left_sets: dict[str, set[str]] = {}
    right_sets: dict[str, set[str]] = {}
    profile_lookup = {
        str(profile["profile_id"]): profile for profile in profiles
    }
    for split in sorted(set(author_split.values()) - {"discovery"}):
        authors = [
            author for author in heldout if author_split[author] == split
        ]
        if len(authors) < 2:
            continue
        for author in authors:
            left = half_consensus.get(f"{author}::left", set())
            right = half_consensus.get(f"{author}::right", set())
            left_profile = profile_lookup[f"{author}::left"]
            stranger_profile, condition_overlap, token_delta = _nuisance_match(
                left_profile,
                [
                    profile_lookup[f"{candidate}::right"]
                    for candidate in authors
                    if candidate != author
                ],
            )
            stranger = half_consensus.get(
                str(stranger_profile["profile_id"]),
                set(),
            )
            if not left and not right:
                continue
            same = _information_jaccard(left, right)
            other = _information_jaccard(left, stranger)
            positives.append(same)
            negatives.append(other)
            deltas.append(same - other)
            nuisance_condition_overlap.append(condition_overlap)
            nuisance_token_delta.append(token_delta)
            left_sets[author] = left
            right_sets[author] = right
    positive_values = np.asarray(positives, dtype=float)
    negative_values = np.asarray(negatives, dtype=float)
    auc = _bootstrap_auc(
        positive_values,
        negative_values,
        draws=draws,
        seed=seed,
    )
    delta = base._bootstrap_stat_interval(
        deltas,
        draws=draws,
        seed=seed + 1,
        statistic="mean",
    )
    return {
        "same_author_n": len(positive_values),
        "same_author_auc": auc[0],
        "same_author_auc_ci_lower": auc[1],
        "same_author_auc_ci_upper": auc[2],
        "same_similarity_mean": float(positive_values.mean()),
        "stranger_similarity_mean": float(negative_values.mean()),
        "same_minus_stranger": delta[0],
        "same_minus_stranger_ci_lower": delta[1],
        "same_minus_stranger_ci_upper": delta[2],
        "nuisance_match_condition_overlap_mean": float(
            np.mean(nuisance_condition_overlap)
        ),
        "nuisance_match_relative_token_delta_mean": float(
            np.mean(nuisance_token_delta)
        ),
    }, left_sets, right_sets


def _pairwise_uncertainty_distance(
    means: np.ndarray,
    uncertainty: np.ndarray,
    discovery_means: np.ndarray,
) -> np.ndarray:
    covariance = np.atleast_2d(np.cov(discovery_means, rowvar=False, ddof=1))
    regularization = max(float(np.trace(covariance) / covariance.shape[0]) * 1e-3, 1e-8)
    output = np.zeros((len(means), len(means)), dtype=float)
    for left in range(len(means)):
        for right in range(left + 1, len(means)):
            metric = covariance + np.diag(
                uncertainty[left] + uncertainty[right] + regularization
            )
            difference = means[left] - means[right]
            value = float(np.sqrt(max(
                difference @ np.linalg.pinv(metric) @ difference,
                0.0,
            )))
            output[left, right] = output[right, left] = value
    return output


def _neighborhood_metrics(
    metadata: pd.DataFrame,
    geometry: dict[str, np.ndarray],
    left_sets: dict[str, set[str]],
    right_sets: dict[str, set[str]],
    *,
    config: dict[str, Any],
) -> dict[str, float]:
    real = config["real_text"]
    heldout_mask = ~metadata["split"].eq("discovery").to_numpy()
    heldout_authors = metadata.loc[heldout_mask, "author_id"].astype(str).tolist()
    discovery_mask = metadata["split"].eq("discovery").to_numpy()
    means_all = (geometry["left"] + geometry["right"]) / 2
    uncertainty_all = ((geometry["left"] - geometry["right"]) ** 2) / 2
    means = means_all[heldout_mask]
    uncertainty = uncertainty_all[heldout_mask]
    distances = _pairwise_uncertainty_distance(
        means,
        uncertainty,
        means_all[discovery_mask],
    )
    author_sets = [
        left_sets.get(author, set()).union(right_sets.get(author, set()))
        for author in heldout_authors
    ]
    similarities = np.eye(len(author_sets), dtype=float)
    for left in range(len(author_sets)):
        for right in range(left + 1, len(author_sets)):
            value = _information_jaccard(author_sets[left], author_sets[right])
            similarities[left, right] = similarities[right, left] = value
    neighbor_count = min(
        max(
            int(real["neighbor_minimum"]),
            int(np.ceil(float(real["neighbor_fraction"]) * len(author_sets))),
        ),
        max(1, (len(author_sets) - 1) // 2),
    )
    far_count = max(1, int(np.ceil(float(real["far_fraction"]) * len(author_sets))))
    rng = np.random.default_rng(int(config["seed"]) + 909)
    neighbor_means = []
    random_means = []
    far_means = []
    for index in range(len(author_sets)):
        order = np.argsort(distances[index], kind="stable")
        order = order[order != index]
        neighbors = order[:neighbor_count]
        far = order[-far_count:]
        middle = order[neighbor_count: max(neighbor_count + 1, len(order) - far_count)]
        if len(middle) < neighbor_count:
            middle = order[neighbor_count:]
        random_indices = rng.choice(
            middle,
            size=neighbor_count,
            replace=len(middle) < neighbor_count,
        )
        neighbor_means.append(float(similarities[index, neighbors].mean()))
        random_means.append(float(similarities[index, random_indices].mean()))
        far_means.append(float(similarities[index, far].mean()))
    deltas = np.asarray(neighbor_means) - np.asarray(random_means)
    draws = int(real["bootstrap_draws"])
    delta = base._bootstrap_stat_interval(
        deltas.tolist(),
        draws=draws,
        seed=int(config["seed"]) + 910,
        statistic="mean",
    )
    auc = _bootstrap_auc(
        np.asarray(neighbor_means),
        np.asarray(far_means),
        draws=draws,
        seed=int(config["seed"]) + 911,
    )
    upper = np.triu_indices(len(author_sets), k=1)
    correlation = float(spearmanr(
        distances[upper],
        1.0 - similarities[upper],
    ).statistic)
    permutations = int(real["permutations"])
    null = []
    for _ in range(permutations):
        shuffled = rng.permutation(len(author_sets))
        shuffled_similarity = similarities[np.ix_(shuffled, shuffled)]
        null.append(spearmanr(
            distances[upper],
            1.0 - shuffled_similarity[upper],
        ).statistic)
    permutation_p = float(
        (1 + np.sum(np.asarray(null) >= correlation)) / (permutations + 1)
    )
    vocabulary = set().union(*author_sets) if author_sets else set()
    prevalence = max(
        (
            sum(atom in values for values in author_sets) / len(author_sets)
            for atom in vocabulary
        ),
        default=0.0,
    )
    return {
        "neighborhood_n": len(author_sets),
        "neighbor_count": neighbor_count,
        "neighbor_similarity_mean": float(np.mean(neighbor_means)),
        "random_similarity_mean": float(np.mean(random_means)),
        "far_similarity_mean": float(np.mean(far_means)),
        "neighbor_minus_random": delta[0],
        "neighbor_minus_random_ci_lower": delta[1],
        "neighbor_minus_random_ci_upper": delta[2],
        "neighbor_auc": auc[0],
        "neighbor_auc_ci_lower": auc[1],
        "neighbor_auc_ci_upper": auc[2],
        "distance_spearman": correlation,
        "distance_permutation_p": permutation_p,
        "max_atom_prevalence": float(prevalence),
    }


def _interpreter_stability(
    profiles: list[dict[str, Any]],
    events: dict[str, list[dict[str, Any]]],
    runs: list[dict[str, Any]],
    *,
    config: dict[str, Any],
) -> tuple[dict[str, float], pd.DataFrame]:
    heldout = [
        profile for profile in profiles if profile["cohort_split"] != "discovery"
    ]
    documents = [
        _atom_set(profile)
        for run in runs
        for profile in run["interpretation"].values()
    ]
    weights = idf_weights(documents)
    rows = []
    runs_by_profile = {}
    critic_maps_by_run: list[dict[str, str]] = [
        {} for _ in runs
    ]
    for profile in heldout:
        profile_id = str(profile["profile_id"])
        candidate_eligible = bool(base._candidate_atoms(
            profile,
            events.get(profile_id, []),
        ))
        if not candidate_eligible:
            continue
        atom_runs = [
            _atom_set(run["interpretation"].get(profile_id))
            for run in runs
        ]
        edge_runs = [
            evidence_edge_set(run["interpretation"].get(profile_id) or {})
            for run in runs
        ]
        interpreted_any = bool(set().union(*atom_runs))
        interpreted_consensus = bool(
            consensus_set(atom_runs, minimum_fraction=0.80)
        )
        runs_by_profile[profile_id] = atom_runs
        for run_index, run in enumerate(runs):
            verdicts = base._verdict_map(
                run["interpretation"].get(profile_id),
                run["critique"].get(profile_id),
            )
            critic_maps_by_run[run_index].update({
                f"{profile_id}|{key}": value for key, value in verdicts.items()
            })
        rows.append({
            "profile_id": profile_id,
            "interpreted_any": interpreted_any,
            "interpreted_consensus": interpreted_consensus,
            "weighted_jaccard": (
                mean_pairwise_weighted_jaccard(atom_runs, weights=weights)
                if interpreted_any else 0.0
            ),
            "evidence_edge_f1": (
                mean_pairwise_set_f1(edge_runs) if interpreted_any else 0.0
            ),
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {
            "same_input_weighted_jaccard_median": float("nan"),
            "same_input_weighted_jaccard_ci_lower": float("nan"),
            "same_input_weighted_jaccard_ci_upper": float("nan"),
            "evidence_edge_f1_mean": float("nan"),
            "evidence_edge_f1_ci_lower": float("nan"),
            "evidence_edge_f1_ci_upper": float("nan"),
            "multilabel_fleiss_kappa": float("nan"),
            "critic_kappa": float("nan"),
            "candidate_eligible_profiles": 0,
            "interpreted_profile_rate": 0.0,
        }, frame
    draws = int(config["real_text"]["bootstrap_draws"])
    atom = base._bootstrap_stat_interval(
        frame["weighted_jaccard"].tolist(),
        draws=draws,
        seed=int(config["seed"]) + 120,
        statistic="median",
    )
    edge = base._bootstrap_stat_interval(
        frame["evidence_edge_f1"].tolist(),
        draws=draws,
        seed=int(config["seed"]) + 121,
        statistic="mean",
    )
    universe = set().union(*[
        values
        for profile_runs in runs_by_profile.values()
        for values in profile_runs
    ]) if runs_by_profile else set()
    multilabel_kappa = (
        fleiss_kappa_multilabel(runs_by_profile, universe=universe)
        if universe else float("nan")
    )
    return {
        "same_input_weighted_jaccard_median": atom[0],
        "same_input_weighted_jaccard_ci_lower": atom[1],
        "same_input_weighted_jaccard_ci_upper": atom[2],
        "evidence_edge_f1_mean": edge[0],
        "evidence_edge_f1_ci_lower": edge[1],
        "evidence_edge_f1_ci_upper": edge[2],
        "multilabel_fleiss_kappa": float(multilabel_kappa),
        "critic_kappa": pairwise_nominal_kappa(critic_maps_by_run),
        "candidate_eligible_profiles": int(len(frame)),
        "interpreted_profile_rate": float(
            frame["interpreted_consensus"].mean()
        ) if len(frame) else 0.0,
    }, frame


def _candidate_diagnostics(
    profiles: list[dict[str, Any]],
    events: dict[str, list[dict[str, Any]]],
    runs: list[dict[str, Any]],
) -> tuple[dict[str, float], pd.DataFrame]:
    """Separate deterministic candidate coverage from LLM selection behavior."""
    rows: list[dict[str, Any]] = []
    for profile in profiles:
        if profile["cohort_split"] == "discovery":
            continue
        profile_id = str(profile["profile_id"])
        candidates = base._candidate_atoms(profile, events.get(profile_id, []))
        candidate_ids = {
            str(candidate["candidate_id"]) for candidate in candidates
        }
        for run_index, run in enumerate(runs):
            interpretation = run["interpretation"].get(profile_id) or {}
            emitted_ids = {
                str(atom["atom_id"])
                for atom in interpretation.get("interpretation_atoms", [])
            }
            verdicts = base._verdict_map(
                interpretation,
                run["critique"].get(profile_id),
            )
            rows.append({
                "profile_id": profile_id,
                "run_index": run_index,
                "candidate_count": len(candidate_ids),
                "emitted_count": len(emitted_ids),
                "candidate_eligible": bool(candidate_ids),
                "exact_candidate_set": bool(
                    candidate_ids and emitted_ids == candidate_ids
                ),
                "retained_candidate_fraction": (
                    len(candidate_ids.intersection(emitted_ids)) / len(candidate_ids)
                    if candidate_ids else float("nan")
                ),
                "critic_pass_count": sum(
                    verdict == "pass" for verdict in verdicts.values()
                ),
                "critic_qualify_count": sum(
                    verdict == "qualify" for verdict in verdicts.values()
                ),
                "critic_reject_count": sum(
                    verdict == "reject" for verdict in verdicts.values()
                ),
            })
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {
            "candidate_eligible_profile_rate": 0.0,
            "mean_candidate_count": 0.0,
            "mean_emitted_atom_count": 0.0,
            "candidate_retention_rate": float("nan"),
            "exact_candidate_set_rate": float("nan"),
            "critic_pass_rate": float("nan"),
            "critic_qualify_rate": float("nan"),
            "critic_reject_rate": float("nan"),
        }, frame
    eligible = frame.loc[frame["candidate_eligible"]]
    verdict_total = int(
        frame[[
            "critic_pass_count",
            "critic_qualify_count",
            "critic_reject_count",
        ]].to_numpy().sum()
    )
    profile_eligibility = frame.groupby("profile_id", observed=True)[
        "candidate_eligible"
    ].first()
    return {
        "candidate_eligible_profile_rate": float(profile_eligibility.mean()),
        "mean_candidate_count": float(frame["candidate_count"].mean()),
        "mean_emitted_atom_count": float(frame["emitted_count"].mean()),
        "candidate_retention_rate": float(
            eligible["retained_candidate_fraction"].mean()
        ) if not eligible.empty else float("nan"),
        "exact_candidate_set_rate": float(
            eligible["exact_candidate_set"].mean()
        ) if not eligible.empty else float("nan"),
        "critic_pass_rate": float(
            frame["critic_pass_count"].sum() / verdict_total
        ) if verdict_total else float("nan"),
        "critic_qualify_rate": float(
            frame["critic_qualify_count"].sum() / verdict_total
        ) if verdict_total else float("nan"),
        "critic_reject_rate": float(
            frame["critic_reject_count"].sum() / verdict_total
        ) if verdict_total else float("nan"),
    }, frame


def _variant_metrics(
    profiles: list[dict[str, Any]],
    baseline: dict[str, Any],
    irrelevant: dict[str, Any],
    targeted: dict[str, Any],
    random_control: dict[str, Any],
    *,
    config: dict[str, Any],
) -> tuple[dict[str, float], pd.DataFrame]:
    rows = []
    for profile in profiles:
        if profile["cohort_split"] == "discovery":
            continue
        profile_id = str(profile["profile_id"])
        original = baseline["interpretation"].get(profile_id)
        perturb = irrelevant["interpretation"].get(profile_id)
        target = targeted["interpretation"].get(profile_id)
        random = random_control["interpretation"].get(profile_id)
        if not all(value is not None for value in (original, perturb, target, random)):
            continue
        original_atoms = _atom_set(original)
        perturb_atoms = _atom_set(perturb)
        target_atoms = _atom_set(target)
        random_atoms = _atom_set(random)
        target_event_code = str(profile["target_event_code"])
        original_by_key = {
            interpretation_atom_key(atom): atom
            for atom in original.get("interpretation_atoms", [])
        }
        target_by_key = {
            interpretation_atom_key(atom): atom
            for atom in target.get("interpretation_atoms", [])
        }
        baseline_target = {
            atom_key
            for atom_key, atom in original_by_key.items()
            if (
                target_event_code
                and str(atom["atom_id"]).endswith(f"::{target_event_code}")
            )
        }
        after_target = {
            atom_key
            for atom_key, atom in target_by_key.items()
            if (
                target_event_code
                and str(atom["atom_id"]).endswith(f"::{target_event_code}")
            )
        }
        original_verdict = base._verdict_map(
            original,
            baseline["critique"].get(profile_id),
        )
        perturb_verdict = base._verdict_map(
            perturb,
            irrelevant["critique"].get(profile_id),
        )
        keys = set(original_verdict).union(perturb_verdict)
        rows.append({
            "profile_id": profile_id,
            "irrelevant_atom_jaccard": set_jaccard(original_atoms, perturb_atoms),
            "irrelevant_evidence_f1": set_f1(
                evidence_edge_set(original),
                evidence_edge_set(perturb),
            ),
            "irrelevant_critic_invariance": (
                float(np.mean([
                    original_verdict.get(key, "<missing>")
                    == perturb_verdict.get(key, "<missing>")
                    for key in keys
                ]))
                if keys else 1.0
            ),
            "irrelevant_support_flip": (
                original["assessment_status"] != perturb["assessment_status"]
            ),
            "baseline_target_present": bool(baseline_target),
            "target_response": bool(
                baseline_target and after_target != baseline_target
            ),
            "nontarget_retention": set_f1(
                original_atoms - baseline_target,
                target_atoms - after_target,
            ),
            "targeted_minus_random": (
                set_jaccard(original_atoms, random_atoms)
                - set_jaccard(original_atoms, target_atoms)
            ),
        })
    frame = pd.DataFrame(rows)
    eligible = frame.loc[frame["baseline_target_present"]]
    effect = base._bootstrap_stat_interval(
        eligible["targeted_minus_random"].tolist(),
        draws=int(config["real_text"]["bootstrap_draws"]),
        seed=int(config["seed"]) + 700,
        statistic="mean",
    )
    return {
        "irrelevant_atom_jaccard": float(frame["irrelevant_atom_jaccard"].mean()),
        "irrelevant_evidence_f1": float(frame["irrelevant_evidence_f1"].mean()),
        "irrelevant_critic_invariance": float(
            frame["irrelevant_critic_invariance"].mean()
        ),
        "irrelevant_support_flip_rate": float(
            frame["irrelevant_support_flip"].mean()
        ),
        "key_evidence_eligible_profiles": int(len(eligible)),
        "key_evidence_response_rate": float(eligible["target_response"].mean()),
        "key_evidence_nontarget_retention": float(
            eligible["nontarget_retention"].mean()
        ),
        "targeted_minus_random_effect": effect[0],
        "targeted_minus_random_ci_lower": effect[1],
        "targeted_minus_random_ci_upper": effect[2],
    }, frame


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs" / "v8_interpreter_stability.json",
    )
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results" / "v8_interpreter_stability" / "pandora_primary",
    )
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    config = base._read_json(args.config)
    base._source_env(args.env_file)
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is missing")
    real = config["real_text"]
    runtime = config["runtime"]
    if args.quick:
        real = dict(real)
        real["max_authors"] = dict(real["max_authors"])
        real["max_authors"]["pandora"] = min(24, int(real["max_authors"]["pandora"]))
        real["observer_repetitions"] = min(2, int(real["observer_repetitions"]))
        real["interpreter_repetitions"] = min(3, int(real["interpreter_repetitions"]))
        real["bootstrap_draws"] = min(1000, int(real["bootstrap_draws"]))
        real["permutations"] = min(1000, int(real["permutations"]))
        config = dict(config)
        config["real_text"] = real

    semantic, geometry_panel = _load_panels(config)
    metadata, geometry, bundle = _score_geometry(
        semantic,
        geometry_panel,
        max_authors=int(real["max_authors"]["pandora"]),
    )
    semantic = semantic.loc[semantic["author_id"].isin(metadata["author_id"])].copy()
    thresholds = _reference_thresholds(metadata, geometry)
    profiles = _make_profiles(
        semantic,
        metadata,
        geometry,
        thresholds,
        bundle=bundle,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base._write_json(args.output_dir / "config.resolved.json", config)
    manifest = write_run_manifest(
        args.output_dir / "manifest.json",
        repository_root=ROOT,
        input_paths=[
            args.config,
            PANDORA_COMMENTS_PATH,
            ELIGIBLE_AUTHORS_PATH,
            REPRESENTATION_PATH,
            GEOMETRY_PATH,
            ROOT
            / "results"
            / "v7_multiview_projection"
            / "e1_v72_full_20260715"
            / "run_manifest.json",
            ROOT / "prompts" / "v8_behavior_observer_v1.txt",
            ROOT / "prompts" / "v8_interpreter_v1.txt",
            ROOT / "prompts" / "v8_interpreter_critic_v1.txt",
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "scripts" / "run_suica_v8_interpreter_stability.py",
            ROOT / "suica_core" / "v8_interpreter.py",
        ],
        estimand_id="V8-I2-pandora-source-disjoint-interpreter-validity",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    provider = OpenAICompatibleProvider(base_url=base_url, api_key=api_key)
    observer_spec, interpreter_spec, critic_spec = base._make_specs(config)
    batch_size = int(runtime.get("quick_batch_size", 2))
    observer_runs = [
        _run_observer_repetition(
            profiles=profiles,
            repetition=repetition,
            output_dir=args.output_dir,
            provider=provider,
            observer_spec=observer_spec,
            batch_size=batch_size,
            concurrency=int(runtime["concurrency"]),
        )
        for repetition in range(int(real["observer_repetitions"]))
    ]
    complete_profile_ids = set.intersection(*[
        set(run["observer"]) for run in observer_runs
    ]) if observer_runs else set()
    complete_authors = {
        str(profile["author_id"])
        for profile in profiles
        if (
            f"{profile['author_id']}::left" in complete_profile_ids
            and f"{profile['author_id']}::right" in complete_profile_ids
        )
    }
    original_metadata = metadata.copy()
    original_index = {
        str(author): index
        for index, author in enumerate(original_metadata["author_id"].astype(str))
    }
    kept_indices = [
        original_index[str(author)]
        for author in original_metadata["author_id"].astype(str)
        if str(author) in complete_authors
    ]
    metadata = original_metadata.loc[
        original_metadata["author_id"].isin(complete_authors)
    ].reset_index(drop=True)
    geometry = {
        side: values[np.asarray(kept_indices, dtype=int)]
        for side, values in geometry.items()
    }
    profiles = [
        profile
        for profile in profiles
        if str(profile["author_id"]) in complete_authors
    ]
    consensus_events = _consensus_events(profiles, observer_runs)
    links, link_audit = _fit_links(profiles, consensus_events, config=config)
    _attach_links(profiles, links, consensus_events)
    link_audit.to_csv(args.output_dir / "registered_link_audit.csv", index=False)
    pd.DataFrame(links).to_csv(args.output_dir / "registered_links.csv", index=False)
    base._write_json(args.output_dir / "reference_thresholds.json", thresholds)
    base._write_json(
        args.output_dir / "data_schema.json",
        {
            "corpus": "pandora",
            "authors_before_observer_completeness": int(len(original_metadata)),
            "authors_after_observer_completeness": int(len(metadata)),
            "split_counts": {
                str(key): int(value)
                for key, value in metadata["split"].value_counts().items()
            },
            "profiles": int(len(profiles)),
            "segments_per_profile": int(real["segments_per_author"]) // 2,
            "anonymous_geometry_dimensions": int(geometry["left"].shape[1]),
            "raw_text_persisted": False,
            "external_personality_labels_read": False,
        },
    )
    heldout_profiles = [
        profile for profile in profiles if profile["cohort_split"] != "discovery"
    ]
    interpreter_runs = [
        base._run_interpreter_variant(
            variant=f"pandora_baseline_r{repetition:02d}",
            profiles=heldout_profiles,
            events=consensus_events,
            output_dir=args.output_dir,
            provider=provider,
            interpreter_spec=interpreter_spec,
            critic_spec=critic_spec,
            batch_size=batch_size,
            concurrency=int(runtime["concurrency"]),
        )
        for repetition in range(int(real["interpreter_repetitions"]))
    ]
    stability, stability_frame = _interpreter_stability(
        profiles,
        consensus_events,
        interpreter_runs,
        config=config,
    )
    candidate_metrics, candidate_frame = _candidate_diagnostics(
        profiles,
        consensus_events,
        interpreter_runs,
    )
    same_author, left_sets, right_sets = _same_author_metrics(
        profiles,
        interpreter_runs,
        draws=int(real["bootstrap_draws"]),
        seed=int(config["seed"]) + 500,
    )
    neighborhood = _neighborhood_metrics(
        metadata,
        geometry,
        left_sets,
        right_sets,
        config=config,
    )
    targeted_events, random_events = base._variant_event_sets(
        heldout_profiles,
        consensus_events,
        seed=int(config["seed"]) + 600,
    )
    irrelevant = base._run_interpreter_variant(
        variant="pandora_irrelevant",
        profiles=heldout_profiles,
        events=consensus_events,
        output_dir=args.output_dir,
        provider=provider,
        interpreter_spec=interpreter_spec,
        critic_spec=critic_spec,
        batch_size=batch_size,
        concurrency=int(runtime["concurrency"]),
        irrelevant_note=True,
    )
    targeted = base._run_interpreter_variant(
        variant="pandora_targeted",
        profiles=heldout_profiles,
        events=targeted_events,
        output_dir=args.output_dir,
        provider=provider,
        interpreter_spec=interpreter_spec,
        critic_spec=critic_spec,
        batch_size=batch_size,
        concurrency=int(runtime["concurrency"]),
    )
    random_control = base._run_interpreter_variant(
        variant="pandora_random",
        profiles=heldout_profiles,
        events=random_events,
        output_dir=args.output_dir,
        provider=provider,
        interpreter_spec=interpreter_spec,
        critic_spec=critic_spec,
        batch_size=batch_size,
        concurrency=int(runtime["concurrency"]),
    )
    variants, variant_frame = _variant_metrics(
        heldout_profiles,
        interpreter_runs[0],
        irrelevant,
        targeted,
        random_control,
        config=config,
    )
    stage_results = [
        result for run in observer_runs for result in run["stage_results"]
    ]
    stage_results += [
        result for run in interpreter_runs for result in run["stage_results"]
    ]
    stage_results += irrelevant["stage_results"]
    stage_results += targeted["stage_results"]
    stage_results += random_control["stage_results"]
    parse_rate = float(np.mean([
        result["status"] == "STRUCTURED_STAGE_READY" for result in stage_results
    ]))
    first_attempt_rate = float(np.mean([
        result["status"] == "STRUCTURED_STAGE_READY"
        and result["ledger"].get("attempt_history", [{}])[0].get("status") == "VALID"
        for result in stage_results
    ]))
    normalized_calls = sum(
        any(
            int(result["ledger"].get("validator_metadata", {}).get(key, 0)) > 0
            for key in (
                "canonicalized_event_ids",
                "merged_duplicate_events",
                "dropped_abstain_markers",
                "corrected_abstain_flags",
            )
        )
        for result in stage_results
    )
    normalization_call_rate = float(normalized_calls / len(stage_results))
    forbidden = sum(
        interpretation_forbidden_count({
            "profiles": list(run["interpretation"].values())
        })
        for run in interpreter_runs + [irrelevant, targeted, random_control]
    )
    metrics = {
        "authors": int(len(metadata)),
        "heldout_authors": int((~metadata["split"].eq("discovery")).sum()),
        "profiles": int(len(profiles)),
        "registered_links": int(len(links)),
        "observer_complete_authors": int(len(complete_authors)),
        "observer_complete_author_rate": float(
            len(metadata) / len(original_metadata)
        ) if len(original_metadata) else 0.0,
        "registered_link_cross_half_sign_agreement_rate": float(
            pd.Series([
                bool(row["cross_half_sign_agreement"])
                for row in links
            ]).mean()
        ) if links else float("nan"),
        "parse_rate": parse_rate,
        "first_attempt_valid_rate": first_attempt_rate,
        "bookkeeping_normalization_call_rate": normalization_call_rate,
        "forbidden_field_count": int(forbidden),
        **stability,
        **candidate_metrics,
        **same_author,
        **neighborhood,
        **variants,
    }
    gates = config["gates"]
    checks = {
        "runtime": (
            parse_rate >= float(gates["min_parse_rate"])
            and first_attempt_rate >= float(gates["min_first_attempt_valid_rate"])
            and normalization_call_rate
            <= float(gates["max_bookkeeping_normalization_call_rate"])
            and metrics["observer_complete_author_rate"]
            >= float(gates["min_observer_complete_author_rate"])
        ),
        "safety": forbidden == 0,
        "registered_links_available": len(links) > 0,
        "same_input": (
            stability["same_input_weighted_jaccard_ci_lower"]
            >= float(gates["min_same_input_weighted_jaccard_lcb"])
            and stability["multilabel_fleiss_kappa"]
            >= float(gates["min_multilabel_fleiss_kappa"])
            and stability["evidence_edge_f1_ci_lower"]
            >= float(gates["min_evidence_edge_f1_lcb"])
            and stability["critic_kappa"] >= float(gates["min_critic_kappa"])
            and stability["interpreted_profile_rate"]
            >= float(gates["min_interpreted_profile_rate"])
        ),
        "same_author": (
            same_author["same_author_auc"] >= float(gates["min_same_author_auc"])
            and same_author["same_author_auc_ci_lower"]
            >= float(gates["min_same_author_auc_lcb"])
            and same_author["same_minus_stranger_ci_lower"]
            > float(gates["min_same_minus_stranger_lcb"])
        ),
        "neighborhood": (
            neighborhood["neighbor_minus_random"]
            >= float(gates["min_neighbor_delta"])
            and neighborhood["neighbor_minus_random_ci_lower"]
            > float(gates["min_neighbor_delta_lcb"])
            and neighborhood["neighbor_auc"] >= float(gates["min_neighbor_auc"])
            and neighborhood["neighbor_auc_ci_lower"]
            >= float(gates["min_neighbor_auc_lcb"])
            and neighborhood["distance_spearman"]
            >= float(gates["min_distance_spearman"])
            and neighborhood["distance_permutation_p"]
            < float(gates["max_distance_permutation_p"])
            and neighborhood["max_atom_prevalence"]
            <= float(gates["max_atom_prevalence"])
            and same_author["same_similarity_mean"]
            > neighborhood["neighbor_similarity_mean"]
            > neighborhood["far_similarity_mean"]
        ),
        "irrelevant_robustness": (
            variants["irrelevant_atom_jaccard"]
            >= float(gates["min_irrelevant_atom_jaccard"])
            and variants["irrelevant_evidence_f1"]
            >= float(gates["min_irrelevant_evidence_f1"])
            and variants["irrelevant_critic_invariance"]
            >= float(gates["min_irrelevant_critic_invariance"])
            and variants["irrelevant_support_flip_rate"]
            <= float(gates["max_irrelevant_support_flip"])
        ),
        "key_evidence": (
            variants["key_evidence_eligible_profiles"] > 0
            and variants["key_evidence_response_rate"]
            >= float(gates["min_key_evidence_response_rate"])
            and variants["key_evidence_nontarget_retention"]
            >= float(gates["min_key_evidence_nontarget_retention"])
            and variants["targeted_minus_random_effect"]
            >= float(gates["min_targeted_minus_random_effect"])
            and variants["targeted_minus_random_ci_lower"]
            > float(gates["min_targeted_minus_random_lcb"])
        ),
    }
    quick_technical_checks = (
        checks["runtime"]
        and checks["safety"]
        and checks["registered_links_available"]
        and checks["same_input"]
        and checks["irrelevant_robustness"]
        and checks["key_evidence"]
    )
    if args.quick:
        status = (
            "V8_INTERPRETER_PANDORA_QUICK_RUNTIME_PASS"
            if quick_technical_checks
            else "V8_INTERPRETER_PANDORA_QUICK_RUNTIME_NOT_CLOSED"
        )
    elif all(checks.values()):
        status = "V8_INTERPRETER_PANDORA_GATE_PASS"
    elif (
        checks["runtime"]
        and checks["safety"]
        and checks["same_input"]
        and checks["irrelevant_robustness"]
        and checks["key_evidence"]
    ):
        status = "V8_INTERPRETER_RENDERER_ONLY"
    else:
        status = "V8_INTERPRETER_PANDORA_GATE_NOT_CLOSED"
    decision = {
        "status": status,
        "quick": bool(args.quick),
        "metrics": metrics,
        "checks": checks,
        "claim_boundary": config["claim_boundary"],
    }
    stability_frame.to_csv(args.output_dir / "stability_by_profile.csv", index=False)
    candidate_frame.to_csv(
        args.output_dir / "candidate_selection_by_profile.csv",
        index=False,
    )
    variant_frame.to_csv(args.output_dir / "variant_metrics_by_profile.csv", index=False)
    pd.DataFrame([metrics]).to_csv(args.output_dir / "metrics.csv", index=False)
    with (args.output_dir / "execution_ledger.jsonl").open("w", encoding="utf-8") as handle:
        for result in stage_results:
            handle.write(json.dumps(result["ledger"], ensure_ascii=False) + "\n")
    manifest.update({
        "status": status,
        "authors": int(len(metadata)),
        "heldout_authors": int((~metadata["split"].eq("discovery")).sum()),
        "geometry_bundle_id": bundle.bundle_id,
    })
    base._write_json(args.output_dir / "manifest.json", manifest)
    base._write_json(args.output_dir / "decision.json", decision)
    append_ledger_event(
        args.output_dir / "evidence_ledger.jsonl",
        {"estimand_id": manifest["estimand_id"], **decision},
    )
    report = (
        "# SUICA V8 Interpreter: PANDORA Primary Gate\n\n"
        f"Status: `{status}`\n\n"
        f"{pd.DataFrame([metrics]).round(4).T.to_markdown()}\n\n"
        "## Checks\n\n"
        + "\n".join(
            f"- `{name}`: {'PASS' if value else 'FAIL'}"
            for name, value in checks.items()
        )
        + "\n\n## Boundary\n\n"
        + config["claim_boundary"]
        + "\n"
    )
    (args.output_dir / "report.md").write_text(report, encoding="utf-8")
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
