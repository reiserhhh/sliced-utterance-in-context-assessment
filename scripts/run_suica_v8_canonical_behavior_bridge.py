#!/usr/bin/env python3
"""Reconnect confirmed canonical geometry to the frozen behavior cache."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
for path in (ROOT, SCRIPT_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_suica_v8_geometry_behavior_bridge as bridge_run  # noqa: E402
import run_suica_v8_interpreter_pandora as pandora  # noqa: E402
import run_suica_v8_spectral_geometry_audit as spectral  # noqa: E402
from suica_core.v7_geometry import GeometryBundle  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_bridge import (  # noqa: E402
    RidgeBehaviorBridge,
    canonical_orbit_distance_signatures,
    fit_opportunity_baseline,
    profile_repeated_behavior_features,
    segment_event_repetition_frame,
    select_behavior_columns,
    select_ridge_alpha,
)


DEFAULT_CONFIG = ROOT / "configs" / "v8_canonical_behavior_bridge.json"
DEFAULT_OUTPUT = (
    ROOT / "results" / "v8_canonical_behavior_bridge" / "pandora"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _shape(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    return (
        values - values.mean(axis=1, keepdims=True)
    ) / np.maximum(values.std(axis=1, keepdims=True), 1e-12)


def _canonical_profile_matrix(
    metadata: pd.DataFrame,
    aligned: pd.DataFrame,
    geometry_panel: pd.DataFrame,
    *,
    relative_tolerance: float,
) -> tuple[np.ndarray, list[str], dict[str, Any]]:
    bundle = GeometryBundle.from_dict(
        _read_json(pandora.GEOMETRY_PATH)
    )
    points_by_side = spectral._whitened_author_points(
        geometry_panel,
        metadata,
        bundle,
    )
    point_lookup = {
        (str(author), side): points_by_side[side][index]
        for index, author in enumerate(metadata["author_id"].astype(str))
        for side in ("left", "right")
    }
    points = np.vstack([
        point_lookup[(str(row.author_id), str(row.side))]
        for row in aligned.itertuples(index=False)
    ])
    canonical, names, diagnostics = canonical_orbit_distance_signatures(
        points,
        np.asarray(bundle.reference_landmarks, dtype=float),
        relative_tolerance=relative_tolerance,
    )
    discovery = aligned["cohort_split"].astype(str).eq("discovery").to_numpy()
    scaler = StandardScaler().fit(_shape(canonical)[discovery])
    return scaler.transform(_shape(canonical)), names, diagnostics


def _report(
    decision: dict[str, Any],
    calibration: pd.DataFrame,
    confirmation: pd.DataFrame,
) -> str:
    selected = confirmation.iloc[0]
    return f"""# SUICA V8 Canonical Geometry-to-Behavior Bridge

Decision: `{decision["status"]}`

## Design

The internally confirmed canonical scale-residual author geometry replaced
the failed sorted-distance geometry. The existing observer cache, event
ontology, source-disjoint halves, cohort splits, feature filters, ridge search,
and confirmation gates were unchanged. No LLM calls or external labels were
added.

## Calibration

{calibration.to_markdown(index=False)}

## Frozen confirmation

{confirmation.to_markdown(index=False)}

- selected behavior view: `{selected["behavior_feature_set"]}`;
- cross-modal author AUC: {selected["cross_modal_author_auc"]:.3f};
- author-cluster interval:
  [{selected["cross_modal_author_auc_ci_lower"]:.3f},
  {selected["cross_modal_author_auc_ci_upper"]:.3f}];
- geometry self-author AUC: {selected["geometry_self_author_auc"]:.3f};
- behavior self-author AUC: {selected["behavior_self_author_auc"]:.3f};
- element Spearman: {selected["element_spearman"]:.3f};
- distance Spearman: {selected["distance_spearman"]:.3f};
- stable links / behavior targets:
  {int(selected["stable_links"])}/{int(selected["behavior_targets"])}.

## Interpretation

{decision["interpretation"]}

{decision["claim_boundary"]}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read_json(args.config)
    source = ROOT / str(config["source_run"])
    geometry_confirmation = ROOT / str(config["geometry_confirmation_run"])
    for run in (source, geometry_confirmation):
        inventory = verify_artifact_inventory(run / "artifact_inventory.json")
        if inventory["status"] != "INVENTORY_PASS":
            raise RuntimeError(f"source inventory failed: {run}")
    geometry_decision = _read_json(geometry_confirmation / "decision.json")
    if geometry_decision["status"] != (
        "V8_CANONICAL_SCALE_RESIDUAL_INTERNAL_FRESH_PASS"
    ):
        raise RuntimeError("canonical geometry fresh-author gate is not closed")

    source_config = _read_json(source / "config.resolved.json")
    observer_runs = bridge_run._load_observer_runs(
        source,
        repetitions=int(source_config["real_text"]["observer_repetitions"]),
    )
    metadata, _, profiles, _, semantic = bridge_run._rebuild_inputs(
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
    aligned, _, _ = bridge_run._profile_matrix(profiles, behavior)
    semantic_panel, geometry_panel = pandora._load_panels(source_config)
    del semantic_panel
    geometry, geometry_names, canonical_diagnostics = (
        _canonical_profile_matrix(
            metadata,
            aligned,
            geometry_panel,
            relative_tolerance=float(config["relative_tolerance"]),
        )
    )
    split = aligned["cohort_split"].astype(str).to_numpy()
    authors = aligned["author_id"].astype(str).to_numpy()
    sides = aligned["side"].astype(str).to_numpy()
    discovery = split == "discovery"
    calibration = split == "calibration"
    confirmation = split == "confirmation"

    calibration_rows = []
    relation_frames = []
    states: dict[str, dict[str, Any]] = {}
    for index, feature_set in enumerate(config["behavior_feature_sets"]):
        columns = select_behavior_columns(
            behavior,
            feature_set=str(feature_set),
            discovery_mask=discovery,
            minimum_nonzero_profiles=int(config["minimum_nonzero_profiles"]),
            maximum_nonzero_fraction=float(config["maximum_nonzero_fraction"]),
        )
        values = aligned[columns].to_numpy(float)
        alpha, alpha_scores = select_ridge_alpha(
            geometry[discovery],
            values[discovery],
            authors[discovery],
            sides[discovery],
            alphas=config["ridge_alphas"],
            folds=int(config["inner_group_folds"]),
        )
        bridge = RidgeBehaviorBridge(alpha=alpha).fit(
            geometry[discovery],
            values[discovery],
        )
        relations = bridge_run._register_relations(
            geometry[discovery],
            bridge.observed_z(values[discovery]),
            authors[discovery],
            sides[discovery],
            geometry_names=geometry_names,
            behavior_names=columns,
            seed=int(config["seed"]) + index * 101,
        )
        relations.insert(0, "behavior_feature_set", str(feature_set))
        relation_frames.append(relations)
        result = bridge_run._evaluate(
            geometry[calibration],
            values[calibration],
            authors[calibration],
            sides[calibration],
            bridge,
            relations,
            geometry_names=geometry_names,
            behavior_names=columns,
            seed=int(config["seed"]) + 1000 + index,
            full_inference=False,
        )
        eligible = relations.loc[relations["eligible"]]
        result.update({
            "behavior_feature_set": str(feature_set),
            "geometry_dimensions": int(geometry.shape[1]),
            "behavior_dimensions": int(len(columns)),
            "ridge_alpha": float(alpha),
            "inner_cv_auc": float(alpha_scores[alpha]),
            "stable_links": int(len(eligible)),
            "behavior_targets": int(eligible["behavior_feature"].nunique()),
        })
        calibration_rows.append(result)
        states[str(feature_set)] = {
            "columns": columns,
            "values": values,
            "bridge": bridge,
            "relations": relations,
        }

    calibration_frame = pd.DataFrame(calibration_rows)
    selection = config["selection"]
    selected = calibration_frame.sort_values(
        [
            str(selection["primary_metric"]),
            *map(str, selection["tie_breakers"]),
            "behavior_feature_set",
        ],
        ascending=[False, False, False, True],
        kind="stable",
    ).iloc[0]
    selected_feature_set = str(selected["behavior_feature_set"])
    state = states[selected_feature_set]
    final = bridge_run._evaluate(
        geometry[confirmation],
        state["values"][confirmation],
        authors[confirmation],
        sides[confirmation],
        state["bridge"],
        state["relations"],
        geometry_names=geometry_names,
        behavior_names=state["columns"],
        seed=int(config["seed"]) + 3000,
        full_inference=True,
    )
    eligible = state["relations"].loc[state["relations"]["eligible"]]
    final.update({
        "behavior_feature_set": selected_feature_set,
        "geometry_dimensions": int(geometry.shape[1]),
        "behavior_dimensions": int(len(state["columns"])),
        "ridge_alpha": float(state["bridge"].alpha),
        "stable_links": int(len(eligible)),
        "behavior_targets": int(eligible["behavior_feature"].nunique()),
    })
    confirmation_frame = pd.DataFrame([final])

    gates = config["confirmation_gates"]
    checks = {
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
        "stable_links": (
            int(final["stable_links"]) >= int(gates["minimum_stable_links"])
        ),
        "behavior_target_diversity": (
            int(final["behavior_targets"])
            >= int(gates["minimum_behavior_targets"])
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
    if all(checks.values()):
        status = "V8_CANONICAL_BEHAVIOR_BRIDGE_PASS"
        interpretation = (
            "The confirmed canonical geometry recovered a source-disjoint "
            "mapping to the frozen explicit behavior view."
        )
    elif checks["geometry_self_auc"] and not checks["behavior_self_auc"]:
        status = "V8_CANONICAL_GEOMETRY_PASS_BEHAVIOR_VIEW_STOP"
        interpretation = (
            "Canonical author geometry is stable, but the current "
            "three-segment explicit behavior view is not author-stable enough "
            "to support the bridge. Stop this behavior object; do not tune "
            "the renderer."
        )
    else:
        status = "V8_CANONICAL_BEHAVIOR_BRIDGE_NOT_CLOSED"
        interpretation = (
            "The canonical geometry-to-behavior mapping did not close every "
            "registered gate. No renderer or personality claim is licensed."
        )
    old_decision = _read_json(
        ROOT
        / "results"
        / "v8_geometry_behavior_bridge"
        / "pandora_method_audit_v2_replay_20260725"
        / "decision.json"
    )
    decision = {
        "status": status,
        "checks": checks,
        "selected_behavior_feature_set": selected_feature_set,
        "confirmation": final,
        "delta_vs_old_bridge": {
            "cross_modal_author_auc": float(
                final["cross_modal_author_auc"]
                - old_decision["selected_confirmation"]["cross_modal_author_auc"]
            ),
            "geometry_self_author_auc": float(
                final["geometry_self_author_auc"]
                - old_decision["selected_confirmation"]["geometry_self_author_auc"]
            ),
            "behavior_self_author_auc": float(
                final["behavior_self_author_auc"]
                - old_decision["selected_confirmation"]["behavior_self_author_auc"]
            ),
        },
        "canonical_orbit_diagnostics": canonical_diagnostics,
        "new_llm_calls": 0,
        "external_labels_read": False,
        "interpretation": interpretation,
        "claim_boundary": str(config["claim_boundary"]),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(args.output_dir / "config.resolved.json", config)
    _write_json(args.output_dir / "decision.json", decision)
    calibration_frame.to_csv(
        args.output_dir / "calibration_metrics.csv",
        index=False,
    )
    confirmation_frame.to_csv(
        args.output_dir / "confirmation_metrics.csv",
        index=False,
    )
    pd.concat(relation_frames, ignore_index=True).to_csv(
        args.output_dir / "registered_relation_audit.csv",
        index=False,
    )
    (args.output_dir / "report.md").write_text(
        _report(decision, calibration_frame, confirmation_frame),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            source / "artifact_inventory.json",
            source / "config.resolved.json",
            geometry_confirmation / "artifact_inventory.json",
            geometry_confirmation / "decision.json",
            pandora.PANDORA_COMMENTS_PATH,
            pandora.ELIGIBLE_AUTHORS_PATH,
            pandora.REPRESENTATION_PATH,
            pandora.GEOMETRY_PATH,
        ],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT / "suica_core" / "v8_bridge.py",
            ROOT / "scripts" / "run_suica_v8_geometry_behavior_bridge.py",
            ROOT / "scripts" / "run_suica_v8_spectral_geometry_audit.py",
        ],
        estimand_id="V8-I6-pandora-canonical-geometry-behavior-bridge",
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
