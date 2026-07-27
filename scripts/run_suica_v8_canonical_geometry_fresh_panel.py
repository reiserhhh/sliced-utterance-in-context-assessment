#!/usr/bin/env python3
"""Confirm the frozen V8 canonical geometry on unused PANDORA authors."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_geometry_behavior_bridge as bridge_run  # noqa: E402
import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
import run_suica_v8_spectral_geometry_audit as spectral  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_realtext import load_pandora_source_disjoint_panels  # noqa: E402
from suica_core.v8_bridge import (  # noqa: E402
    SpectralGeometryProjector,
    canonical_orbit_distance_signatures,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_canonical_geometry_fresh_panel.json"
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_canonical_geometry_fresh_panel"
    / "pandora_internal_fresh"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _opened_metadata(
    source: Path,
    source_config: dict[str, Any],
    semantic: pd.DataFrame,
    geometry_panel: pd.DataFrame,
) -> pd.DataFrame:
    observer_runs = bridge_run._load_observer_runs(
        source,
        repetitions=int(source_config["real_text"]["observer_repetitions"]),
    )
    complete_profiles = set.intersection(*[
        set(run["observer"]) for run in observer_runs
    ])
    metadata, _, _ = pandora._score_geometry(
        semantic,
        geometry_panel,
        max_authors=int(
            source_config["real_text"]["max_authors"]["pandora"]
        ),
    )
    complete_authors = {
        str(author)
        for author in metadata["author_id"].astype(str)
        if (
            f"{author}::left" in complete_profiles
            and f"{author}::right" in complete_profiles
        )
    }
    return metadata.loc[
        metadata["author_id"].astype(str).isin(complete_authors)
    ].reset_index(drop=True)


def _panel_hash(author_ids: np.ndarray) -> str:
    payload = "\n".join(sorted(map(str, author_ids))).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _fresh_raw_author_panel(
    config: dict[str, Any],
    source_config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    eligible = set(
        pd.read_csv(
            pandora.ELIGIBLE_AUTHORS_PATH,
            usecols=["user_id"],
            dtype={"user_id": str},
        )["user_id"].astype(str)
    )
    raw_authors = set(
        pd.read_parquet(
            pandora.PANDORA_COMMENTS_PATH,
            columns=["author"],
        )["author"].astype(str)
    )
    ordered = sorted(
        raw_authors - eligible,
        key=lambda value: hashlib.sha256(
            f"v8-canonical-fresh::{config['seed']}::{value}".encode("utf-8")
        ).hexdigest(),
    )
    pool_size = int(config["fresh_candidate_pool"])
    candidates = ordered[:pool_size]
    if len(candidates) < pool_size:
        raise RuntimeError("fresh candidate pool is smaller than registered")
    scoring_split = str(config["scoring_split_alias"])
    frame = pd.DataFrame({
        "user_id": candidates,
        "split": scoring_split,
    })
    return load_pandora_source_disjoint_panels(
        pandora.PANDORA_COMMENTS_PATH,
        eligible_authors=frame,
        max_by_split={scoring_split: pool_size},
        semantic_segments_per_author=int(
            source_config["real_text"]["segments_per_author"]
        ),
        geometry_units_per_half=int(
            source_config["real_text"]["pandora_geometry_units_per_half"]
        ),
        seed=int(config["seed"]),
    )


def _shape(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return (
        values - values.mean(axis=1, keepdims=True)
    ) / np.maximum(values.std(axis=1, keepdims=True), 1e-12)


def _wilson_lower(successes: int, total: int, z: float = 1.959963984540054) -> float:
    if total <= 0:
        return float("nan")
    proportion = successes / total
    denominator = 1.0 + z**2 / total
    center = proportion + z**2 / (2.0 * total)
    spread = z * np.sqrt(
        proportion * (1.0 - proportion) / total
        + z**2 / (4.0 * total**2)
    )
    return float((center - spread) / denominator)


def _fast_pairing_permutation_p(
    values: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    metric: str,
    observed: float,
    seed: int,
    permutations: int,
) -> float:
    """Test author pairing by shuffling the right-side profile assignment."""
    left = np.flatnonzero(sides == "left")
    right = np.flatnonzero(sides == "right")
    left_authors = authors[left]
    right_lookup = {
        str(author): index for author, index in zip(authors[right], right, strict=True)
    }
    if set(map(str, left_authors)) != set(right_lookup):
        raise ValueError("left/right author sets differ")
    right = np.asarray([right_lookup[str(author)] for author in left_authors])
    left_values = np.asarray(values[left], dtype=float)
    right_values = np.asarray(values[right], dtype=float)
    if metric == "cosine":
        left_norm = left_values / np.maximum(
            np.linalg.norm(left_values, axis=1, keepdims=True),
            1e-12,
        )
        right_norm = right_values / np.maximum(
            np.linalg.norm(right_values, axis=1, keepdims=True),
            1e-12,
        )
        score_matrix = left_norm @ right_norm.T
    elif metric == "euclidean":
        score_matrix = -np.linalg.norm(
            left_values[:, None, :] - right_values[None, :, :],
            axis=2,
        )
    else:
        raise ValueError(f"unsupported metric: {metric}")
    n_authors = len(left_values)
    off_diagonal = ~np.eye(n_authors, dtype=bool)
    rng = np.random.default_rng(seed)
    exceedances = 0
    for _ in range(int(permutations)):
        permuted = score_matrix[:, rng.permutation(n_authors)]
        positive = np.diag(permuted)
        row_comparisons = (
            (positive[:, None] > permuted)
            + 0.5 * (positive[:, None] == permuted)
        )
        column_comparisons = (
            (positive[None, :] > permuted)
            + 0.5 * (positive[None, :] == permuted)
        )
        row_wins = (
            np.where(off_diagonal, row_comparisons, 0.0).sum(axis=1)
            / (n_authors - 1)
        )
        column_wins = (
            np.where(off_diagonal, column_comparisons, 0.0).sum(axis=0)
            / (n_authors - 1)
        )
        null_auc = float(np.r_[row_wins, column_wins].mean())
        exceedances += int(null_auc >= float(observed))
    return float((1 + exceedances) / (int(permutations) + 1))


def _evaluate_fresh(
    values: np.ndarray,
    authors: np.ndarray,
    sides: np.ndarray,
    *,
    seed: int,
    draws: int,
    permutations: int,
    inference: bool,
) -> dict[str, float]:
    result = spectral._evaluate(
        values,
        authors,
        sides,
        seed=seed,
        draws=draws,
        permutations=permutations,
        inference=False,
    )
    if not inference:
        return result
    euclidean_interval = spectral._bootstrap_interval(
        values,
        authors,
        sides,
        metric="euclidean",
        seed=seed,
        draws=draws,
    )
    cosine_interval = spectral._bootstrap_interval(
        values,
        authors,
        sides,
        metric="cosine",
        seed=seed + 11,
        draws=draws,
    )
    result.update({
        "same_author_auc_cluster_estimate": euclidean_interval[0],
        "same_author_auc_ci_lower": euclidean_interval[1],
        "same_author_auc_ci_upper": euclidean_interval[2],
        "same_author_permutation_p": _fast_pairing_permutation_p(
            values,
            authors,
            sides,
            metric="euclidean",
            observed=float(result["same_author_auc_euclidean"]),
            seed=seed + 1,
            permutations=permutations,
        ),
        "same_author_cosine_cluster_estimate": cosine_interval[0],
        "same_author_cosine_ci_lower": cosine_interval[1],
        "same_author_cosine_ci_upper": cosine_interval[2],
        "same_author_cosine_permutation_p": _fast_pairing_permutation_p(
            values,
            authors,
            sides,
            metric="cosine",
            observed=float(result["same_author_auc_cosine"]),
            seed=seed + 12,
            permutations=permutations,
        ),
    })
    return result


def _report(decision: dict[str, Any], metrics: pd.DataFrame) -> str:
    selected = metrics.loc[
        metrics["variant_id"].eq("canonical_orbit_scale_residual")
    ].iloc[0]
    baseline = metrics.loc[
        metrics["variant_id"].eq("sorted_quantile")
    ].iloc[0]
    return f"""# SUICA V8 Canonical Geometry Internal Fresh-Author Confirmation

Decision: `{decision["status"]}`

## Design

The candidate, metric, transforms, thresholds, and panel rule were fixed in
`configs/v8_canonical_geometry_fresh_panel.json` before this run. Authors used
in any frozen V7 eligible split were excluded before deterministic hash
sampling. The test authors therefore did not contribute to the V7 landmark
bundle or the opened V8 bridge and geometry audits.

No new LLM calls, raw identifiers, or external labels were used.

## Result

- fresh authors: {decision["fresh_panel"]["authors"]};
- canonical scale-residual cosine AUC:
  {selected["same_author_auc_cosine"]:.3f};
- author-cluster estimate and 95% interval:
  {selected["same_author_cosine_cluster_estimate"]:.3f}
  [{selected["same_author_cosine_ci_lower"]:.3f},
  {selected["same_author_cosine_ci_upper"]:.3f}];
- permutation p: {selected["same_author_cosine_permutation_p"]:.5f};
- sorted-distance cosine AUC:
  {baseline["same_author_auc_cosine"]:.3f};
- paired delta over sorted:
  {decision["paired_delta_over_sorted_cosine"]["estimate"]:+.3f}
  [{decision["paired_delta_over_sorted_cosine"]["ci_lower"]:.3f},
  {decision["paired_delta_over_sorted_cosine"]["ci_upper"]:.3f}];
- scale-matched cosine AUC:
  {decision["scale_matched_cosine_auc"]:.3f};
- topology-shuffle drop:
  {decision["topology_shuffle_control"]["topology_shuffle_drop"]:.3f}.
- ready support:
  {decision["fresh_panel"]["ready_authors"]}/
  {decision["fresh_panel"]["source_eligible_authors"]}
  (Wilson lower {decision["fresh_panel"]["support_wilson_lower"]:.3f});
- paired delta over spectral energy:
  {decision["independent_audit"]["paired_delta_over_spectral_energy_cosine"]["estimate"]:+.3f}
  [{decision["independent_audit"]["paired_delta_over_spectral_energy_cosine"]["ci_lower"]:.3f},
  {decision["independent_audit"]["paired_delta_over_spectral_energy_cosine"]["ci_upper"]:.3f}].

## Boundary

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    source = ROOT / str(config["source_run"])
    opened_run = ROOT / str(config["opened_audit_run"])
    for run in (source, opened_run):
        inventory = verify_artifact_inventory(run / "artifact_inventory.json")
        if inventory["status"] != "INVENTORY_PASS":
            raise RuntimeError(f"source inventory failed: {run}")
    opened_decision = _read_json(opened_run / "decision.json")
    if opened_decision["selected_variant"] != str(config["candidate"]):
        raise RuntimeError("registered candidate differs from opened audit")

    source_config = _read_json(source / "config.resolved.json")
    semantic, geometry_panel = pandora._load_panels(source_config)
    opened_metadata = _opened_metadata(
        source,
        source_config,
        semantic,
        geometry_panel,
    )
    fresh_semantic, fresh_geometry_panel = _fresh_raw_author_panel(
        config,
        source_config,
    )
    source_eligible_authors = int(fresh_semantic["author_id"].nunique())
    target_fresh = int(config["target_fresh_authors"])
    fresh_metadata, fresh_sorted_by_side, bundle = pandora._score_geometry(
        fresh_semantic,
        fresh_geometry_panel,
        max_authors=4 * target_fresh,
    )
    fresh_split = str(config["fresh_panel_split"])
    if len(fresh_metadata) < int(config["minimum_fresh_authors"]):
        raise RuntimeError(
            f"fresh panel has {len(fresh_metadata)} authors; "
            f"minimum is {config['minimum_fresh_authors']}"
        )

    opened_points_by_side = spectral._whitened_author_points(
        geometry_panel,
        opened_metadata,
        bundle,
    )
    opened_ids_array = opened_metadata["author_id"].astype(str).to_numpy()
    opened_points, opened_authors, _ = spectral._interleave(
        opened_points_by_side["left"],
        opened_points_by_side["right"],
        opened_ids_array,
    )
    opened_split_by_author = (
        opened_metadata.set_index("author_id")["split"].astype(str)
    )
    opened_splits = np.asarray([
        opened_split_by_author[author] for author in opened_authors
    ])
    reference_mask = opened_splits == str(config["reference_fit_split"])
    if not reference_mask.any():
        raise RuntimeError("reference-fit split is empty")

    fresh_points_by_side = spectral._whitened_author_points(
        fresh_geometry_panel,
        fresh_metadata,
        bundle,
    )
    fresh_ids = fresh_metadata["author_id"].astype(str).to_numpy()
    fresh_points, fresh_authors, fresh_sides = spectral._interleave(
        fresh_points_by_side["left"],
        fresh_points_by_side["right"],
        fresh_ids,
    )
    fresh_sorted, _, _ = spectral._interleave(
        fresh_sorted_by_side["left"],
        fresh_sorted_by_side["right"],
        fresh_ids,
    )

    landmarks = np.asarray(bundle.reference_landmarks, dtype=float)
    opened_canonical, _, diagnostics = canonical_orbit_distance_signatures(
        opened_points,
        landmarks,
        relative_tolerance=float(config["relative_tolerance"]),
    )
    fresh_canonical, _, fresh_diagnostics = canonical_orbit_distance_signatures(
        fresh_points,
        landmarks,
        relative_tolerance=float(config["relative_tolerance"]),
    )
    if diagnostics != fresh_diagnostics:
        raise RuntimeError("canonical landmark schema drifted across panels")
    shape_scaler = StandardScaler().fit(
        _shape(opened_canonical)[reference_mask]
    )
    fresh_scale_residual = shape_scaler.transform(_shape(fresh_canonical))

    spectral_projector = SpectralGeometryProjector(
        landmarks=landmarks,
        mode="energy",
        variance_target=0.95,
        max_components=16,
    ).fit(opened_points[reference_mask])
    fresh_spectral = spectral_projector.transform(fresh_points)

    variants = {
        "sorted_quantile": fresh_sorted,
        "spectral_energy_16": fresh_spectral,
        "canonical_orbit_scale_residual": fresh_scale_residual,
    }
    metric_rows = []
    for index, (variant_id, values) in enumerate(variants.items()):
        result = _evaluate_fresh(
            values,
            fresh_authors,
            fresh_sides,
            seed=int(config["seed"]) + index,
            draws=int(config["bootstrap_draws"]),
            permutations=int(config["permutations"]),
            inference=variant_id == str(config["candidate"]),
        )
        metric_rows.append({
            "variant_id": variant_id,
            "dimensions": int(values.shape[1]),
            **result,
        })
    metrics = pd.DataFrame(metric_rows)
    selected = metrics.loc[
        metrics["variant_id"].eq("canonical_orbit_scale_residual")
    ].iloc[0]
    baseline = metrics.loc[
        metrics["variant_id"].eq("sorted_quantile")
    ].iloc[0]

    delta_sorted = spectral._paired_auc_delta_interval(
        fresh_scale_residual,
        fresh_sorted,
        fresh_authors,
        fresh_sides,
        metric="cosine",
        seed=int(config["seed"]) + 100,
        draws=int(config["bootstrap_draws"]),
    )
    delta_spectral = spectral._paired_auc_delta_interval(
        fresh_scale_residual,
        fresh_spectral,
        fresh_authors,
        fresh_sides,
        metric="cosine",
        seed=int(config["seed"]) + 104,
        draws=int(config["bootstrap_draws"]),
    )
    raw_fresh_distances = cdist(fresh_points, landmarks, metric="euclidean")
    scale_matched_auc = spectral._scale_matched_auc(
        fresh_scale_residual,
        raw_fresh_distances,
        fresh_authors,
        fresh_sides,
        neighbor_count=int(config["scale_matched_neighbors"]),
    )
    shuffle_control = spectral._topology_shuffle_control(
        fresh_canonical,
        shape_scaler,
        np.ones(len(fresh_canonical), dtype=bool),
        fresh_authors,
        fresh_sides,
        row_scale_residual=True,
        seed=int(config["seed"]) + 101,
        draws=int(config["topology_shuffle_draws"]),
    )
    invariance = spectral._invariance_audit(
        fresh_points[: min(8, len(fresh_points))],
        landmarks,
        modes=["energy"],
        seed=int(config["seed"]) + 102,
    )
    canonical_baseline, baseline_names, _ = (
        canonical_orbit_distance_signatures(
            fresh_points[: min(8, len(fresh_points))],
            landmarks,
            relative_tolerance=float(config["relative_tolerance"]),
        )
    )
    rng = np.random.default_rng(int(config["seed"]) + 103)
    permutation = rng.permutation(len(landmarks))
    canonical_permuted, permuted_names, _ = (
        canonical_orbit_distance_signatures(
            fresh_points[: min(8, len(fresh_points))],
            landmarks[permutation],
            relative_tolerance=float(config["relative_tolerance"]),
        )
    )
    canonical_error = float(
        np.max(np.abs(canonical_baseline - canonical_permuted))
    )
    max_invariance_error = max(
        canonical_error,
        float(invariance["landmark_permutation_max_abs_error"].max()),
        float(invariance["rotation_translation_max_abs_error"].max()),
    )
    gates = config["gates"]
    checks = {
        "same_author_cosine_auc": (
            float(selected["same_author_auc_cosine"])
            >= float(gates["minimum_same_author_cosine_auc"])
        ),
        "cosine_auc_lower": (
            float(selected["same_author_cosine_ci_lower"])
            > float(gates["minimum_cosine_auc_lower"])
        ),
        "permutation_p": (
            float(selected["same_author_cosine_permutation_p"])
            <= float(gates["maximum_permutation_p"])
        ),
        "delta_over_sorted": (
            float(delta_sorted[0])
            >= float(gates["minimum_delta_over_sorted_quantile"])
            and float(delta_sorted[1])
            > float(gates["minimum_delta_ci_lower"])
        ),
        "scale_conditioned": (
            scale_matched_auc
            >= float(gates["minimum_scale_conditioned_auc"])
        ),
        "topology_shuffle": (
            float(shuffle_control["topology_shuffle_drop"])
            >= float(gates["minimum_topology_shuffle_drop"])
        ),
        "invariance": (
            max_invariance_error
            <= float(gates["maximum_invariance_error"])
            and bool(invariance["schema_preserved"].all())
            and baseline_names == permuted_names
        ),
    }
    if all(checks.values()):
        status = "V8_CANONICAL_SCALE_RESIDUAL_INTERNAL_FRESH_PASS"
        interpretation = (
            "The frozen canonical scale-residual representation retained "
            "source-disjoint author structure in PANDORA authors excluded "
            "from the full V7 eligible set. External-corpus and psychological "
            "validation remain open."
        )
    else:
        status = "V8_CANONICAL_SCALE_RESIDUAL_INTERNAL_FRESH_NOT_CLOSED"
        interpretation = (
            "The opened-panel mechanism did not satisfy every registered "
            "internal fresh-author gate. Do not reconnect the behavior "
            "interpreter or change the frozen V7 geometry."
        )
    decision = {
        "status": status,
        "candidate": str(config["candidate"]),
        "checks": checks,
        "fresh_panel": {
            "authors": int(len(fresh_metadata)),
            "ready_authors": int(len(fresh_metadata)),
            "source_eligible_authors": source_eligible_authors,
            "support_rate": float(len(fresh_metadata) / source_eligible_authors),
            "support_wilson_lower": _wilson_lower(
                len(fresh_metadata),
                source_eligible_authors,
            ),
            "profiles": int(2 * len(fresh_metadata)),
            "original_split": fresh_split,
            "panel_hash": _panel_hash(fresh_ids),
            "full_v7_eligible_authors_excluded": int(
                pd.read_csv(
                    pandora.ELIGIBLE_AUTHORS_PATH,
                    usecols=["user_id"],
                )["user_id"].nunique()
            ),
            "raw_identifiers_persisted": False,
        },
        "selected_metrics": selected.to_dict(),
        "sorted_metrics": baseline.to_dict(),
        "paired_delta_over_sorted_cosine": {
            "estimate": delta_sorted[0],
            "ci_lower": delta_sorted[1],
            "ci_upper": delta_sorted[2],
        },
        "scale_matched_cosine_auc": scale_matched_auc,
        "topology_shuffle_control": shuffle_control,
        "independent_audit": {
            "status": (
                "STRICT_AUDIT_PASS"
                if (
                    len(fresh_metadata) >= 60
                    and float(selected["same_author_cosine_permutation_p"]) <= 0.01
                    and float(delta_spectral[0]) >= 0.03
                    and float(delta_spectral[1]) > 0
                    and _wilson_lower(
                        len(fresh_metadata),
                        source_eligible_authors,
                    ) > 0.40
                )
                else "STRICT_AUDIT_NOT_CLOSED"
            ),
            "applied_after_primary_protocol_registration": True,
            "minimum_ready_authors": 60,
            "maximum_permutation_p": 0.01,
            "minimum_delta_over_spectral_energy": 0.03,
            "minimum_support_wilson_lower": 0.40,
            "paired_delta_over_spectral_energy_cosine": {
                "estimate": delta_spectral[0],
                "ci_lower": delta_spectral[1],
                "ci_upper": delta_spectral[2],
            },
        },
        "maximum_invariance_error": max_invariance_error,
        "confirmation_status": str(config["confirmation_status"]),
        "new_llm_calls": 0,
        "external_labels_read": False,
        "interpretation": interpretation,
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.output_dir / "config.resolved.json", config)
    _write_json(args.output_dir / "decision.json", decision)
    _write_json(args.output_dir / "canonical_orbit_diagnostics.json", diagnostics)
    metrics.to_csv(args.output_dir / "metrics.csv", index=False)
    invariance.to_csv(args.output_dir / "invariance_audit.csv", index=False)
    (args.output_dir / "report.md").write_text(
        _report(decision, metrics),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            source / "artifact_inventory.json",
            source / "decision.json",
            source / "config.resolved.json",
            opened_run / "artifact_inventory.json",
            opened_run / "decision.json",
            pandora.PANDORA_COMMENTS_PATH,
            pandora.ELIGIBLE_AUTHORS_PATH,
            pandora.REPRESENTATION_PATH,
            pandora.GEOMETRY_PATH,
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_bridge.py",
            ROOT / "scripts" / "run_suica_v8_spectral_geometry_audit.py",
            ROOT / "scripts" / "run_suica_v8_interpreter_pandora.py",
        ],
        estimand_id="V8-I5-pandora-canonical-geometry-internal-fresh-author",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0 if status.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
