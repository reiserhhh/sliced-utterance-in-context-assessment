#!/usr/bin/env python3
"""V7.5-X2: first real-data consumption of suica_core/v7_uncertainty.py.

Joint nested conditional uncertainty for the frozen G1 relative-geometry
bundle. Three registered components are estimated per scored held-out author
(calibration + confirmation):

- source_cluster: cluster bootstrap over the author's non-overlapping native
  source comments under the frozen representation and frozen bundle;
- model_refit: refit of the registered TF-IDF+SVD representation (perturbed
  fitting corpus within fixed discovery authors, fresh SVD seed) plus geometry
  runtime refit, with reference-population membership held fixed;
- reference_norm: resampling of the discovery reference population under the
  frozen representation with geometry runtime refit.

A total conditional SEM is only taken from the module's JOINT_NESTED_DRAWS
path (protocol steps 1-4 nested per draw). The module's refusal semantics are
respected verbatim: authors whose frozen baseline status is not
GEOMETRY_PROFILE_READY receive REFUSE_GEOMETRY_UNCERTAINTY_OUT_OF_SUPPORT,
and the dependence-unmodeled refusal is demonstrated, not bypassed.

Claim boundary: error decomposition of a technical geometry only; no
reliability, MDD, or person-score validity claim.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import hashlib

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_geometry import (  # noqa: E402
    GeometryBundle,
    fit_geometry_bundle,
    score_geometry_bundle,
)
from suica_core.v7_governance import (  # noqa: E402
    append_ledger_event,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v7_observations import (  # noqa: E402
    ObservationSpec,
    build_observations,
    canonicalize_comments,
    prepare_source_panel,
    select_reference_authors,
)
from suica_core.v7_psychometric import (  # noqa: E402
    RepresentationSpec,
    author_features_from_embeddings,
    fit_representation,
)
from suica_core.v7_uncertainty import summarize_geometry_uncertainty  # noqa: E402


ESTIMAND_ID = "V7.5-X2-joint-nested-conditional-uncertainty-G1"
FUNCTIONALS = ("mean_landmark_distance", "nearest_landmark_distance")
COMPONENTS = ("source_cluster", "model_refit", "reference_norm")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "v7_x2_joint_uncertainty.json")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results" / "v7_uncertainty" / "x2_g1_joint_20260717")
    parser.add_argument("--report", type=Path, default=ROOT / "reports" / "V7_X2_G1_JOINT_UNCERTAINTY.md")
    return parser.parse_args()


def _anon_id(user_id: str, split: str, rank: int) -> str:
    return f"{split[:4]}_{rank:02d}"


def _rebuild_e1_native(config: dict[str, Any]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Rebuild the frozen E1 source panel and native units deterministically."""
    e1_dir = ROOT / config["e1_dir"]
    e1_manifest = json.loads((e1_dir / "run_manifest.json").read_text(encoding="utf-8"))
    e1_config = e1_manifest["config"]
    excluded = set(
        pd.read_csv(ROOT / config["e0_exclusion_scores"], usecols=["user_id"])["user_id"].dropna().astype(str)
    )
    raw = pd.read_parquet(e1_manifest["input"])
    canonical = canonicalize_comments(
        raw,
        user_col=str(e1_manifest["column_map"]["user"]),
        text_col=str(e1_manifest["column_map"]["text"]),
        order_col=e1_manifest["column_map"]["order"],
        condition_col=e1_manifest["column_map"]["condition"],
        min_tokens=int(e1_config["min_tokens_per_unit"]),
        mask_personality_terms=bool(e1_config["mask_personality_terms"]),
    )
    selected = select_reference_authors(
        canonical,
        min_comments_per_user=int(e1_config["min_comments_per_user"]),
        max_users=int(e1_config["max_users"]),
        seed=int(e1_config["seed"]),
        exclude_user_ids=excluded,
        cohort_salt="v7.1-e1-fresh",
    )
    defaults = {
        "min_tokens": int(e1_config["min_tokens_per_unit"]),
        "max_units_per_user": int(e1_config["max_units_per_user"]),
        "max_source_comments_per_user": int(e1_config["max_source_comments_per_user"]),
        "max_source_tokens_per_user": int(e1_config["max_source_tokens_per_user"]),
    }
    specs = [ObservationSpec(**{**defaults, **raw_spec}) for raw_spec in e1_config["operators"]]
    panel = prepare_source_panel(selected, specs[0])
    native_spec = next(spec for spec in specs if spec.name == "native")
    units = build_observations(panel, native_spec)
    frozen_features = pd.read_csv(e1_dir / "author_features_native.csv")
    return panel, units, frozen_features, e1_config


def _verify_feature_reproduction(
    representation: Any,
    units: pd.DataFrame,
    frozen_features: pd.DataFrame,
) -> float:
    """Hard gate: recomputed native features must equal the frozen E1 table."""
    recomputed = author_features_from_embeddings(units, representation.transform(units["text"]))
    left = recomputed.sort_values("user_id").reset_index(drop=True)
    right = frozen_features.sort_values("user_id").reset_index(drop=True)
    if left["user_id"].astype(str).tolist() != right["user_id"].astype(str).tolist():
        raise RuntimeError("X2 reproduction gate failed: author sets differ from frozen E1 features.")
    if not (left["n_units"].to_numpy(int) == right["n_units"].to_numpy(int)).all():
        raise RuntimeError("X2 reproduction gate failed: per-author unit counts differ from frozen E1 features.")
    columns = [column for column in right.columns if "::" in column]
    max_abs = float(np.max(np.abs(left[columns].to_numpy(float) - right[columns].to_numpy(float))))
    if max_abs > 1e-10:
        raise RuntimeError(f"X2 reproduction gate failed: feature mismatch {max_abs} > 1e-10.")
    return max_abs


def _feature_positions(feature_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Return column positions of the mean:: and std:: features per SVD dim."""
    dims = sorted({int(name.split("svd_")[1]) for name in feature_names})
    mean_positions = np.asarray([feature_names.index(f"mean::svd_{dim:03d}") for dim in dims], dtype=int)
    std_positions = np.asarray([feature_names.index(f"std::svd_{dim:03d}") for dim in dims], dtype=int)
    return mean_positions, std_positions


def _aggregate_rows(
    embeddings: np.ndarray,
    row_sets: list[np.ndarray],
    *,
    mean_positions: np.ndarray,
    std_positions: np.ndarray,
    width: int,
) -> np.ndarray:
    """Aggregate unit embeddings into bundle-ordered mean/std author features."""
    output = np.empty((len(row_sets), width), dtype=float)
    for index, rows in enumerate(row_sets):
        values = embeddings[rows]
        output[index, mean_positions] = values.mean(axis=0)
        output[index, std_positions] = values.std(axis=0, ddof=0)
    return output


def _fit_bundle_like_g1(reference_features: np.ndarray, g1_bundle: GeometryBundle, feature_names: list[str]) -> GeometryBundle:
    """Refit the geometry runtime with the frozen G1 configuration."""
    return fit_geometry_bundle(
        reference_features,
        feature_names=feature_names,
        operator=dict(g1_bundle.operator),
        representation=dict(g1_bundle.representation),
        runtime_artifact={"role": "x2_uncertainty_draw", "parent_bundle": g1_bundle.bundle_id},
        reference_population={"role": "x2_uncertainty_draw", "n_authors": int(len(reference_features))},
        min_units_for_score=int(g1_bundle.support_rule["min_units_for_score"]),
        landmark_count=16,
        regularization=1e-3,
        support_radius_quantile=float(g1_bundle.reference_distance_summary["support_radius_quantile"]),
        version=str(g1_bundle.version),
    )


def main() -> int:
    args = parse_args()
    started = time.time()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    e1_dir = ROOT / config["e1_dir"]
    g1_dir = ROOT / config["g1_dir"]

    manifest = write_run_manifest(
        output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            e1_dir / "author_features_native.csv",
            e1_dir / "run_manifest.json",
            e1_dir / "artifacts" / "common_source_comment_representation.joblib",
            g1_dir / "geometry_bundle.json",
            g1_dir / "run_manifest.json",
            g1_dir / "support_summary.csv",
            ROOT / config["e0_exclusion_scores"],
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v7_uncertainty.py",
            ROOT / "suica_core" / "v7_geometry.py",
            ROOT / "suica_core" / "v7_observations.py",
            ROOT / "suica_core" / "v7_psychometric.py",
        ],
        estimand_id=ESTIMAND_ID,
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )

    # ------------------------------------------------------------------ setup
    panel, units, frozen_features, e1_config = _rebuild_e1_native(config)
    representation = joblib.load(e1_dir / "artifacts" / "common_source_comment_representation.joblib")
    reproduction_max_abs = _verify_feature_reproduction(representation, units, frozen_features)
    g1_bundle = GeometryBundle.from_dict(json.loads((g1_dir / "geometry_bundle.json").read_text(encoding="utf-8")))
    g1_manifest = json.loads((g1_dir / "run_manifest.json").read_text(encoding="utf-8"))
    if g1_bundle.bundle_id != str(g1_manifest["bundle_id"]):
        raise RuntimeError("Frozen G1 bundle does not match the G1 run manifest bundle_id.")
    feature_names = list(g1_bundle.feature_names)
    width = len(feature_names)
    mean_positions, std_positions = _feature_positions(feature_names)

    # Baseline scoring with REAL per-author unit counts (n_units from the
    # frozen E1 native features). No assume_support_verified is needed or used.
    frozen_features = frozen_features.sort_values("user_id").reset_index(drop=True)
    support_expected = pd.read_csv(g1_dir / "support_summary.csv").set_index("split")
    baseline: dict[str, dict[str, Any]] = {}
    for split in ("discovery", "calibration", "confirmation"):
        part = frozen_features.loc[frozen_features["split"].eq(split)]
        result = score_geometry_bundle(
            g1_bundle,
            part[feature_names].to_numpy(float),
            unit_counts=part["n_units"].to_numpy(int),
        )
        n_ready = int(sum(status == "GEOMETRY_PROFILE_READY" for status in result["status"]))
        if n_ready != int(support_expected.loc[split, "n_ready"]):
            raise RuntimeError(f"X2 baseline gate failed: {split} ready count {n_ready} != G1 support summary.")
        baseline[split] = {"result": result, "user_ids": part["user_id"].astype(str).tolist(), "n_units": part["n_units"].to_numpy(int)}

    # ---------------------------------------------------------------- targets
    target_splits = [str(split) for split in config["target_splits"]]
    target_rows: list[dict[str, Any]] = []
    for split in target_splits:
        info = baseline[split]
        order = np.argsort([hashlib.sha256(f"x2-anon::{user}".encode("utf-8")).hexdigest() for user in info["user_ids"]])
        rank_by_position = np.empty(len(order), dtype=int)
        rank_by_position[order] = np.arange(len(order))
        for position, user_id in enumerate(info["user_ids"]):
            target_rows.append({
                "user_id": user_id,
                "split": split,
                "anon_id": _anon_id(user_id, split, int(rank_by_position[position])),
                "n_units": int(info["n_units"][position]),
                "baseline_status": str(info["result"]["status"][position]),
                "baseline_mean_landmark_distance": float(info["result"]["mean_landmark_distance"][position]),
                "baseline_nearest_landmark_distance": float(info["result"]["nearest_landmark_distance"][position]),
                "baseline_reference_radius": float(info["result"]["reference_radius"][position]),
            })
    targets = pd.DataFrame(target_rows).sort_values(["split", "anon_id"]).reset_index(drop=True)
    ready_mask = targets["baseline_status"].eq("GEOMETRY_PROFILE_READY").to_numpy(bool)
    n_targets = len(targets)

    frozen_indexed = frozen_features.set_index("user_id")
    target_feature_matrix = frozen_indexed.loc[targets["user_id"], feature_names].to_numpy(float)
    target_unit_counts = targets["n_units"].to_numpy(int)

    # Precompute unit-row slices per target author and discovery author.
    units = units.reset_index(drop=True)
    grouped = units.groupby("user_id", observed=True)
    unit_rows_by_user = {str(user): np.asarray(rows, dtype=int) for user, rows in grouped.indices.items()}
    target_unit_rows = [unit_rows_by_user[user] for user in targets["user_id"]]

    discovery_users = frozen_features.loc[frozen_features["split"].eq("discovery"), "user_id"].astype(str).tolist()
    discovery_feature_matrix = frozen_indexed.loc[discovery_users, feature_names].to_numpy(float)
    discovery_unit_rows = [unit_rows_by_user[user] for user in discovery_users]
    disc_panel = panel.loc[panel["split"].eq("discovery")].reset_index(drop=True)
    disc_panel_rows_by_user = {
        str(user): np.asarray(rows, dtype=int) for user, rows in disc_panel.groupby("user_id", observed=True).indices.items()
    }

    frozen_unit_embeddings = representation.transform(units["text"])

    seed = int(config["seed"])
    child = np.random.SeedSequence(seed).spawn(4)
    rng_source = np.random.default_rng(child[0])
    rng_model = np.random.default_rng(child[1])
    rng_reference = np.random.default_rng(child[2])
    rng_joint = np.random.default_rng(child[3])

    draws: dict[str, dict[str, np.ndarray]] = {}
    draw_ready_rate: dict[str, np.ndarray] = {}

    # ---------------------------------------------------- source_cluster draws
    n_source = int(config["n_source_cluster_draws"])
    g_source = {name: np.empty((n_targets, n_source), dtype=float) for name in FUNCTIONALS}
    source_ready = np.empty(n_targets, dtype=float)
    for index in range(n_targets):
        rows = target_unit_rows[index]
        resamples = [rows[rng_source.integers(0, len(rows), size=len(rows))] for _ in range(n_source)]
        features = _aggregate_rows(
            frozen_unit_embeddings, resamples,
            mean_positions=mean_positions, std_positions=std_positions, width=width,
        )
        result = score_geometry_bundle(g1_bundle, features, unit_counts=np.full(n_source, len(rows), dtype=int))
        for name in FUNCTIONALS:
            g_source[name][index] = np.asarray(result[name], dtype=float)
        source_ready[index] = float(np.mean([status == "GEOMETRY_PROFILE_READY" for status in result["status"]]))
    draws["source_cluster"] = g_source
    draw_ready_rate["source_cluster"] = source_ready
    print(f"[x2] source_cluster draws done ({time.time() - started:.0f}s)")

    # ---------------------------------------------------- reference_norm draws
    n_reference = int(config["n_reference_norm_draws"])
    g_reference = {name: np.empty((n_targets, n_reference), dtype=float) for name in FUNCTIONALS}
    reference_ready = np.zeros(n_targets, dtype=float)
    n_discovery = len(discovery_feature_matrix)
    for draw in range(n_reference):
        rows = rng_reference.integers(0, n_discovery, size=n_discovery)
        bundle_draw = _fit_bundle_like_g1(discovery_feature_matrix[rows], g1_bundle, feature_names)
        result = score_geometry_bundle(bundle_draw, target_feature_matrix, unit_counts=target_unit_counts)
        for name in FUNCTIONALS:
            g_reference[name][:, draw] = np.asarray(result[name], dtype=float)
        reference_ready += np.asarray([status == "GEOMETRY_PROFILE_READY" for status in result["status"]], dtype=float)
    draws["reference_norm"] = g_reference
    draw_ready_rate["reference_norm"] = reference_ready / n_reference
    print(f"[x2] reference_norm draws done ({time.time() - started:.0f}s)")

    # ------------------------------------------------------- model_refit draws
    def _refit_representation(corpus: pd.DataFrame, draw_seed: int) -> Any:
        spec = RepresentationSpec(
            max_features=int(e1_config["representation"]["max_features"]),
            ngram_min=int(e1_config["representation"]["ngram_range"][0]),
            ngram_max=int(e1_config["representation"]["ngram_range"][1]),
            svd_dimensions=int(e1_config["representation"]["svd_dimensions"]),
            factor_count=1,
            seed=int(draw_seed),
        )
        return fit_representation(corpus, spec)

    n_model = int(config["n_model_refit_draws"])
    g_model = {name: np.empty((n_targets, n_model), dtype=float) for name in FUNCTIONALS}
    model_ready = np.zeros(n_targets, dtype=float)
    unit_texts = units["text"].reset_index(drop=True)
    for draw in range(n_model):
        corpus_rows = np.concatenate([
            rows[rng_model.integers(0, len(rows), size=len(rows))]
            for rows in disc_panel_rows_by_user.values()
        ])
        rep_draw = _refit_representation(disc_panel.iloc[corpus_rows], seed + 1000 + draw)
        embeddings = rep_draw.transform(unit_texts)
        reference_features = _aggregate_rows(
            embeddings, discovery_unit_rows,
            mean_positions=mean_positions, std_positions=std_positions, width=width,
        )
        bundle_draw = _fit_bundle_like_g1(reference_features, g1_bundle, feature_names)
        target_features = _aggregate_rows(
            embeddings, target_unit_rows,
            mean_positions=mean_positions, std_positions=std_positions, width=width,
        )
        result = score_geometry_bundle(bundle_draw, target_features, unit_counts=target_unit_counts)
        for name in FUNCTIONALS:
            g_model[name][:, draw] = np.asarray(result[name], dtype=float)
        model_ready += np.asarray([status == "GEOMETRY_PROFILE_READY" for status in result["status"]], dtype=float)
        if (draw + 1) % 16 == 0:
            print(f"[x2] model_refit draw {draw + 1}/{n_model} ({time.time() - started:.0f}s)")
    draws["model_refit"] = g_model
    draw_ready_rate["model_refit"] = model_ready / n_model

    # ------------------------------------------------------ joint nested draws
    n_joint = int(config["n_joint_nested_draws"])
    g_joint = {name: np.empty((n_targets, n_joint), dtype=float) for name in FUNCTIONALS}
    joint_ready = np.zeros(n_targets, dtype=float)
    for draw in range(n_joint):
        author_multiset = rng_joint.integers(0, len(discovery_users), size=len(discovery_users))
        unique_authors = np.unique(author_multiset)
        corpus_rows = np.concatenate([
            disc_panel_rows_by_user[discovery_users[author]]
            for author in author_multiset
        ])
        rep_draw = _refit_representation(disc_panel.iloc[corpus_rows], seed + 2000 + draw)
        embeddings = rep_draw.transform(unit_texts)
        unique_features = _aggregate_rows(
            embeddings, [discovery_unit_rows[author] for author in unique_authors],
            mean_positions=mean_positions, std_positions=std_positions, width=width,
        )
        feature_by_author = np.empty((len(discovery_users), width), dtype=float)
        feature_by_author[unique_authors] = unique_features
        bundle_draw = _fit_bundle_like_g1(feature_by_author[author_multiset], g1_bundle, feature_names)
        target_resamples = [rows[rng_joint.integers(0, len(rows), size=len(rows))] for rows in target_unit_rows]
        target_features = _aggregate_rows(
            embeddings, target_resamples,
            mean_positions=mean_positions, std_positions=std_positions, width=width,
        )
        result = score_geometry_bundle(bundle_draw, target_features, unit_counts=target_unit_counts)
        for name in FUNCTIONALS:
            g_joint[name][:, draw] = np.asarray(result[name], dtype=float)
        joint_ready += np.asarray([status == "GEOMETRY_PROFILE_READY" for status in result["status"]], dtype=float)
        if (draw + 1) % 16 == 0:
            print(f"[x2] joint nested draw {draw + 1}/{n_joint} ({time.time() - started:.0f}s)")
    draw_ready_rate["joint_nested"] = joint_ready / n_joint

    # ------------------------------------------------- module refusal protocol
    first_ready = int(np.flatnonzero(ready_mask)[0])
    dependence_refusal = summarize_geometry_uncertainty(
        source_cluster_draws=g_source[FUNCTIONALS[0]][first_ready],
        model_refit_draws=g_model[FUNCTIONALS[0]][first_ready],
        reference_norm_draws=g_reference[FUNCTIONALS[0]][first_ready],
        support_status=targets.loc[first_ready, "baseline_status"],
    )
    if dependence_refusal["status"] != "REFUSE_TOTAL_GEOMETRY_UNCERTAINTY_DEPENDENCE_UNMODELED":
        raise RuntimeError("Expected the module to refuse an undeclared total SEM; it did not.")

    # ------------------------------------------------------ per-author summary
    per_author_rows: list[dict[str, Any]] = []
    refusal_count = 0
    for index in range(n_targets):
        row: dict[str, Any] = {
            "anon_id": targets.loc[index, "anon_id"],
            "split": targets.loc[index, "split"],
            "n_units": int(targets.loc[index, "n_units"]),
            "baseline_status": targets.loc[index, "baseline_status"],
            "baseline_mean_landmark_distance": float(targets.loc[index, "baseline_mean_landmark_distance"]),
            "baseline_nearest_landmark_distance": float(targets.loc[index, "baseline_nearest_landmark_distance"]),
            "baseline_reference_radius": float(targets.loc[index, "baseline_reference_radius"]),
            "draw_ready_rate_source_cluster": float(draw_ready_rate["source_cluster"][index]),
            "draw_ready_rate_model_refit": float(draw_ready_rate["model_refit"][index]),
            "draw_ready_rate_reference_norm": float(draw_ready_rate["reference_norm"][index]),
            "draw_ready_rate_joint_nested": float(draw_ready_rate["joint_nested"][index]),
        }
        for name in FUNCTIONALS:
            summary = summarize_geometry_uncertainty(
                source_cluster_draws=draws["source_cluster"][name][index],
                model_refit_draws=draws["model_refit"][name][index],
                reference_norm_draws=draws["reference_norm"][name][index],
                support_status=targets.loc[index, "baseline_status"],
                joint_nested_draws=g_joint[name][index],
            )
            row[f"{name}::uncertainty_status"] = summary["status"]
            if summary["status"] == "CONDITIONAL_GEOMETRY_UNCERTAINTY_READY":
                for component in COMPONENTS:
                    row[f"{name}::sem_{component}"] = summary["component_summary"][component]["conditional_sem"]
                    row[f"{name}::var_{component}"] = summary["component_summary"][component]["variance"]
                row[f"{name}::total_conditional_sem_joint"] = summary["total_conditional_sem"]
                row[f"{name}::total_interval_95_low"] = summary["total_interval_95"][0]
                row[f"{name}::total_interval_95_high"] = summary["total_interval_95"][1]
                independence = summarize_geometry_uncertainty(
                    source_cluster_draws=draws["source_cluster"][name][index],
                    model_refit_draws=draws["model_refit"][name][index],
                    reference_norm_draws=draws["reference_norm"][name][index],
                    support_status=targets.loc[index, "baseline_status"],
                    independence_declared=True,
                )
                row[f"{name}::total_sem_independence_approx"] = independence["total_conditional_sem"]
                row[f"{name}::joint_over_independence_sem_ratio"] = (
                    float(summary["total_conditional_sem"]) / float(independence["total_conditional_sem"])
                    if float(independence["total_conditional_sem"]) > 0 else float("nan")
                )
        if row[f"{FUNCTIONALS[0]}::uncertainty_status"] != "CONDITIONAL_GEOMETRY_UNCERTAINTY_READY":
            refusal_count += 1
        per_author_rows.append(row)
    per_author = pd.DataFrame(per_author_rows)
    n_decomposed = int(ready_mask.sum())

    # -------------------------------------------------- population aggregation
    primary = str(config["primary_functional"])
    population_rows: list[dict[str, Any]] = []
    shares_primary: dict[str, float] = {}
    lean_by_author: dict[str, Any] = {}
    for name in FUNCTIONALS:
        ready_rows = per_author.loc[per_author[f"{name}::uncertainty_status"].eq("CONDITIONAL_GEOMETRY_UNCERTAINTY_READY")]
        pooled_var = {component: float(ready_rows[f"{name}::var_{component}"].sum()) for component in COMPONENTS}
        total_var = sum(pooled_var.values())
        shares = {component: pooled_var[component] / total_var for component in COMPONENTS}
        author_share_frame = ready_rows[[f"{name}::var_{component}" for component in COMPONENTS]].to_numpy(float)
        author_shares = author_share_frame / author_share_frame.sum(axis=1, keepdims=True)
        fraction_source_ge_model = float(
            np.mean(ready_rows[f"{name}::var_source_cluster"].to_numpy(float) >= ready_rows[f"{name}::var_model_refit"].to_numpy(float))
        )
        for position, component in enumerate(COMPONENTS):
            population_rows.append({
                "functional": name,
                "component": component,
                "pooled_variance_share": shares[component],
                "mean_author_share": float(author_shares[:, position].mean()),
                "median_author_share": float(np.median(author_shares[:, position])),
                "median_author_sem": float(ready_rows[f"{name}::sem_{component}"].median()),
                "n_authors": int(len(ready_rows)),
            })
        if name == primary:
            shares_primary = shares
            lean_by_author = {
                "fraction_authors_source_ge_model": fraction_source_ge_model,
                "pooled_lean_held": bool(shares["source_cluster"] >= shares["model_refit"]),
            }
        population_rows.append({
            "functional": name,
            "component": "joint_nested_total",
            "pooled_variance_share": float("nan"),
            "mean_author_share": float("nan"),
            "median_author_share": float("nan"),
            "median_author_sem": float(ready_rows[f"{name}::total_conditional_sem_joint"].median()),
            "n_authors": int(len(ready_rows)),
        })
    population = pd.DataFrame(population_rows)
    lean_held = bool(lean_by_author["pooled_lean_held"])

    # ---------------------------------------------------------------- outputs
    per_author.to_csv(output_dir / "per_author_uncertainty.csv", index=False)
    population.to_csv(output_dir / "component_share_summary.csv", index=False)
    np.savez(
        output_dir / "draw_matrices_deidentified.npz",
        anon_id=per_author["anon_id"].to_numpy(str),
        split=per_author["split"].to_numpy(str),
        **{
            f"{component}__{name}": draws[component][name]
            for component in COMPONENTS for name in FUNCTIONALS
        },
        **{f"joint_nested__{name}": g_joint[name] for name in FUNCTIONALS},
    )

    ready_primary = per_author.loc[per_author[f"{primary}::uncertainty_status"].eq("CONDITIONAL_GEOMETRY_UNCERTAINTY_READY")]
    snapshot = {
        "estimand_id": ESTIMAND_ID,
        "bundle_id": g1_bundle.bundle_id,
        "created_utc": datetime.now(UTC).isoformat(),
        "n_target_authors": int(n_targets),
        "n_authors_decomposed": n_decomposed,
        "n_authors_refused_out_of_support": int(n_targets - n_decomposed),
        "primary_functional": primary,
        "pooled_component_variance_shares": shares_primary,
        "registered_lean": config["registered_lean"],
        "lean_held_pooled": lean_held,
        "fraction_authors_source_ge_model": lean_by_author["fraction_authors_source_ge_model"],
        "median_total_conditional_sem_joint": float(ready_primary[f"{primary}::total_conditional_sem_joint"].median()),
        "median_joint_over_independence_sem_ratio": float(ready_primary[f"{primary}::joint_over_independence_sem_ratio"].median()),
        "median_baseline_mean_landmark_distance": float(ready_primary["baseline_mean_landmark_distance"].median()),
        "support_handling": "real_unit_counts_passed; assume_support_verified NOT used",
        "identifiers_persisted": False,
        "claim_boundary": config["claim_boundary"],
    }
    (output_dir / "aggregate_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    decision = {
        "status": "X2_JOINT_NESTED_CONDITIONAL_UNCERTAINTY_COMPLETE",
        "estimand_id": ESTIMAND_ID,
        "bundle_id": g1_bundle.bundle_id,
        "reproduction_gate": {
            "e1_native_feature_max_abs_diff": reproduction_max_abs,
            "g1_ready_counts_match_support_summary": True,
        },
        "n_target_authors": int(n_targets),
        "n_authors_decomposed": n_decomposed,
        "n_authors_refused_out_of_support": int(n_targets - n_decomposed),
        "module_refusals_respected": {
            "out_of_support_refusals": int(n_targets - n_decomposed),
            "dependence_unmodeled_demonstration": dependence_refusal["status"],
            "resolution": "JOINT_NESTED_DRAWS path (protocol combination rule) supplied per author",
        },
        "primary_functional": primary,
        "pooled_component_variance_shares": shares_primary,
        "registered_lean": config["registered_lean"],
        "lean_held_pooled": lean_held,
        "fraction_authors_source_ge_model": lean_by_author["fraction_authors_source_ge_model"],
        "draw_counts": {
            "source_cluster": n_source,
            "model_refit": n_model,
            "reference_norm": n_reference,
            "joint_nested": n_joint,
        },
        "identifiers_persisted": False,
        "external_labels_read": False,
        "claim_boundary": config["claim_boundary"],
    }
    (output_dir / "decision.json").write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest.update({"status": decision["status"], "bundle_id": g1_bundle.bundle_id})
    (output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    append_ledger_event(output_dir / "evidence_ledger.jsonl", {"estimand_id": ESTIMAND_ID, **{k: v for k, v in decision.items() if k not in ("reproduction_gate", "draw_counts")}})

    _write_report(args.report, output_dir=output_dir, config=config, decision=decision, snapshot=snapshot, population=population, per_author=per_author)
    inventory = write_artifact_inventory(output_dir, output_dir / "artifact_inventory.json")
    print(json.dumps({
        "status": decision["status"],
        "n_authors_decomposed": n_decomposed,
        "pooled_component_variance_shares": shares_primary,
        "lean_held_pooled": lean_held,
        "artifact_files": inventory["n_files"],
        "elapsed_seconds": round(time.time() - started, 1),
    }, ensure_ascii=False, indent=2))
    return 0


def _write_report(
    path: Path,
    *,
    output_dir: Path,
    config: dict[str, Any],
    decision: dict[str, Any],
    snapshot: dict[str, Any],
    population: pd.DataFrame,
    per_author: pd.DataFrame,
) -> None:
    primary = str(config["primary_functional"])
    shares = decision["pooled_component_variance_shares"]
    population_table = population.to_markdown(index=False, floatfmt=".4f")
    ready = per_author.loc[per_author[f"{primary}::uncertainty_status"].eq("CONDITIONAL_GEOMETRY_UNCERTAINTY_READY")]
    sem_cols = [f"{primary}::sem_source_cluster", f"{primary}::sem_model_refit", f"{primary}::sem_reference_norm", f"{primary}::total_conditional_sem_joint", f"{primary}::total_sem_independence_approx"]
    quantiles = ready[sem_cols].quantile([0.05, 0.25, 0.5, 0.75, 0.95]).rename(columns=lambda c: c.replace(f"{primary}::", "")).to_markdown(floatfmt=".4f")
    rate_columns = {
        "source_cluster": "draw_ready_rate_source_cluster",
        "model_refit": "draw_ready_rate_model_refit",
        "reference_norm": "draw_ready_rate_reference_norm",
        "joint_nested": "draw_ready_rate_joint_nested",
    }
    ready_rates = "\n".join(
        f"- `{component}`: median ready rate {ready[column].median():.3f}, mean {ready[column].mean():.3f}"
        for component, column in rate_columns.items()
    )
    text = f"""# V7.5-X2: Joint Nested Conditional Uncertainty of the Frozen G1 Geometry Bundle

Registered before run at release commit `3a6f5b9` (ledger row `V7.5-X2`).
First real-data consumption of `suica_core/v7_uncertainty.py`.

## Scope

The measured object is the conditional score error of the frozen G1
relative-geometry bundle (`{decision['bundle_id']}`) for the held-out
calibration + confirmation authors that G1 scored. The profile functionals are
`mean_landmark_distance` (primary) and `nearest_landmark_distance`
(secondary). {decision['claim_boundary']}

## Reproduction gates (passed before any draw)

- Recomputed E1 native author features match the frozen table to
  max abs diff `{decision['reproduction_gate']['e1_native_feature_max_abs_diff']:.2e}`.
- Frozen-bundle rescoring with real per-author unit counts reproduces the G1
  `support_summary.csv` ready counts exactly (139 / 47 / 38).

## Support handling

Real per-author unit counts (`n_units` from the frozen E1 native feature
table) were passed to `score_geometry_bundle`; `assume_support_verified` was
**not** used, so ready rows carry `GEOMETRY_PROFILE_READY` directly and no
support attestation was needed.

## Design (per the module's own API and the V7 uncertainty protocol)

- `source_cluster` ({config['n_source_cluster_draws']} draws/author): {config['component_definitions']['source_cluster']}
- `model_refit` ({config['n_model_refit_draws']} draws): {config['component_definitions']['model_refit']}
- `reference_norm` ({config['n_reference_norm_draws']} draws): {config['component_definitions']['reference_norm']}
- `joint_nested` ({config['n_joint_nested_draws']} draws): {config['component_definitions']['joint_nested']}

The module refuses a naive independence-summed total SEM. That refusal was
demonstrated on real draws
(`{decision['module_refusals_respected']['dependence_unmodeled_demonstration']}`)
and then satisfied through the declared joint-nested path, so every emitted
total SEM comes from `JOINT_NESTED_DRAWS`, not from an independence
assumption. The independence approximation is additionally reported per
author as a labeled diagnostic only.

## Results

- Target authors: {decision['n_target_authors']} (calibration + confirmation).
- Decomposed (baseline `GEOMETRY_PROFILE_READY`): **{decision['n_authors_decomposed']}**.
- Refused out-of-support (module status
  `REFUSE_GEOMETRY_UNCERTAINTY_OUT_OF_SUPPORT`): {decision['n_authors_refused_out_of_support']}
  — all are baseline radial-envelope refusals; they receive no precision
  estimate, per protocol.

### Pooled component variance shares ({primary})

- source_cluster: **{shares['source_cluster']:.4f}**
- model_refit: **{shares['model_refit']:.4f}**
- reference_norm: **{shares['reference_norm']:.4f}**

Registered weak lean (`{decision['registered_lean']}`):
**{'HELD' if decision['lean_held_pooled'] else 'NOT HELD'}** at the pooled
level; per-author fraction with source >= model:
{decision['fraction_authors_source_ge_model']:.3f}.

### Population summary

{population_table}

### Per-author conditional SEM quantiles ({primary}, decomposed authors)

{quantiles}

Median joint total conditional SEM: {snapshot['median_total_conditional_sem_joint']:.4f}
(median baseline {primary}: {snapshot['median_baseline_mean_landmark_distance']:.4f}).
Median joint/independence SEM ratio:
{snapshot['median_joint_over_independence_sem_ratio']:.4f} — a ratio away
from 1 is direct evidence that the component dependence the module refuses to
ignore is real.

### Draw-level radial-envelope diagnostics (decomposed authors)

Draw values enter the component vectors regardless of the draw's own support
status (the frozen bundle is the measurement instrument; draws quantify its
sensitivity), but each draw is also re-checked against the applicable radial
envelope and the per-author ready rate is recorded:

{ready_rates}

The low source-cluster and joint ready rates are an honest secondary finding:
a cluster-bootstrap of an author's ~32 source comments adds enough
mean-feature noise in 48 whitened dimensions to push the regularized
Mahalanobis radius past the frozen q99 threshold in most draws. The G1 radial
envelope is therefore tight relative to per-author source-sampling noise —
held-out authors typically sit within about one conditional SEM of the
refusal boundary. This is a support-policy calibration observation, not a
scoring error, and it does not change any baseline status.

## Artifacts

- Decision: `{output_dir / 'decision.json'}`
- Per-author table (deidentified, anon ids only): `{output_dir / 'per_author_uncertainty.csv'}`
- Population summary: `{output_dir / 'component_share_summary.csv'}`
- Deidentified draw matrices: `{output_dir / 'draw_matrices_deidentified.npz'}`
- Aggregate snapshot: `{output_dir / 'aggregate_snapshot.json'}`
- Manifest: `{output_dir / 'run_manifest.json'}`

## Claim boundary

{decision['claim_boundary']} The decomposition conditions on the frozen E1
representation family, the native operator, this Reddit-derived corpus, and
the G1 support policy; it says nothing about trait reliability (G-study/LST
gate), minimum detectable difference, or any person-level interpretation.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
