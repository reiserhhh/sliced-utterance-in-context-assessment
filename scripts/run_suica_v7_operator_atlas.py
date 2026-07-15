#!/usr/bin/env python3
"""Build a held-out directed atlas from frozen V7.1 E1 observation views."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_multiview import (  # noqa: E402
    common_feature_columns,
    fit_block_scalers,
    transform_feature_block,
)
from suica_core.v7_operator_atlas import (  # noqa: E402
    atlas_asymmetry,
    cycle_errors,
    evaluate_directed_atlas,
    fit_directed_maps,
)
from suica_core.v7_governance import verify_artifact_inventory, write_artifact_inventory  # noqa: E402


DEFAULT_E1_DIR = ROOT / "results" / "v7_multiview_projection" / "e1_full_20260714"


def parse_args() -> argparse.Namespace:
    """Parse a frozen-artifact atlas request with no raw text input."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--e1-dir", type=Path, default=DEFAULT_E1_DIR)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--ridge-alpha", type=float, default=None)
    return parser.parse_args()


def _feature_frames(e1_dir: Path) -> dict[str, pd.DataFrame]:
    files = sorted(e1_dir.glob("author_features_*.csv"))
    if len(files) < 3:
        raise FileNotFoundError(f"Expected at least three E1 feature views in {e1_dir}.")
    return {
        path.stem.removeprefix("author_features_"): pd.read_csv(path)
        for path in files
    }


def _aligned_user_ids(feature_frames: dict[str, pd.DataFrame], view_names: tuple[str, ...], split: str) -> list[str]:
    shared: set[str] | None = None
    for view in view_names:
        users = set(feature_frames[view].loc[feature_frames[view]["split"].eq(split), "user_id"].astype(str))
        shared = users if shared is None else shared.intersection(users)
    return sorted(shared or set())


def _blocks(feature_frames, scalers, view_names, user_ids):
    return {
        view: transform_feature_block(feature_frames[view], scaler=scalers[view], user_ids=user_ids)
        for view in view_names
    }


def _selected_alpha(e1_dir: Path, override: float | None) -> float:
    if override is not None:
        return float(override)
    selection_path = e1_dir / "rank_selection.csv"
    selection = pd.read_csv(selection_path)
    best = selection.sort_values(
        ["calibration_mean_consensus_global_r2", "shared_rank", "ridge_alpha"],
        ascending=[False, True, True],
    ).iloc[0]
    return float(best["ridge_alpha"])


def _write_report(path: Path, *, output_dir: Path, alpha: float, evidence_status: str, edges: pd.DataFrame, asymmetry: pd.DataFrame, cycles: pd.DataFrame) -> None:
    """Write a concise, non-psychological directed-atlas report."""
    edge_table = edges.to_markdown(index=False, floatfmt=".3f")
    asymmetry_table = asymmetry.to_markdown(index=False, floatfmt=".3f")
    cycle_summary = cycles.groupby("source_view", observed=True).agg(
        mean_cycle_r2=("cycle_global_r2", "mean"), mean_cycle_rmse=("cycle_rmse_standardized", "mean")
    ).reset_index()
    cycle_table = cycle_summary.to_markdown(index=False, floatfmt=".3f")
    text = f"""# SUICA V7.1 Operator Atlas

## Scope

This atlas uses only frozen author-feature artifacts from the fresh E1 cohort.
It fits directed Ridge maps on E1 discovery+calibration authors and evaluates
them on E1 confirmation authors. It contains no raw text, Big Five, MBTI, or
external labels.  Its evidence status is `{evidence_status}`: E1 already used
this confirmation cohort for its own cross-view endpoint, so this atlas is a
descriptive follow-up rather than an independent confirmation family.

It does not prove that views are coordinate charts, that maps are invertible,
or that any arrow represents a psychological hierarchy. It quantifies which
operator-conditioned feature spaces preserve information under a declared
linear transport.

- Ridge alpha inherited from E1 calibration: `{alpha}`

## Held-Out Directed Edges

{edge_table}

## Directional Asymmetry

{asymmetry_table}

## Cycle Diagnostics

Cycle results are deliberately stringent: three separately fitted maps must
return to their starting standardized feature space. Low cycle performance
means the views are not interchangeable coordinate systems under this map
family; it does not mean that the source author structure is absent.

{cycle_table}

## Interpretation Boundary

An edge above its broken-correspondence null establishes only that two
operator-indexed, author-aligned text representations share recoverable
structure in this corpus. Directional differences can arise from aggregation,
lossiness, opportunity structure, or model linearity. They are not named
constructs and do not establish personality, clinical, or cross-language
validity.

## Artifacts

- Edge table: `{output_dir / 'atlas_edges.csv'}`
- R2 matrix: `{output_dir / 'directed_r2_matrix.csv'}`
- Asymmetry table: `{output_dir / 'atlas_asymmetry.csv'}`
- Cycle table: `{output_dir / 'cycle_errors.csv'}`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    """Build an atlas from frozen E1 feature artifacts."""
    args = parse_args()
    if not args.e1_dir.exists():
        raise FileNotFoundError(f"E1 artifact directory does not exist: {args.e1_dir}")
    output_dir = args.output_dir or ROOT / "results" / "v7_operator_atlas" / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.report or ROOT / "reports" / "V7_OPERATOR_ATLAS.md"
    inventory_path = args.e1_dir / "artifact_inventory.json"
    runtime_path = args.e1_dir / "artifacts" / "multiview_runtime.joblib"
    if not inventory_path.exists() or not runtime_path.exists():
        raise FileNotFoundError(
            "E3 requires replayable E1 artifacts (artifact_inventory.json and "
            "artifacts/multiview_runtime.joblib). Re-run E1 under the V7.2 protocol first."
        )
    inventory_check = verify_artifact_inventory(inventory_path)
    if inventory_check["status"] != "INVENTORY_PASS":
        raise RuntimeError(f"E3 refuses altered E1 artifacts: {inventory_check['failures']}")
    runtime = joblib.load(runtime_path)
    feature_frames = _feature_frames(args.e1_dir)
    view_names = tuple(str(value) for value in runtime["view_names"])
    if set(view_names) != set(feature_frames):
        raise RuntimeError("E3 feature views do not match the frozen E1 runtime.")
    discovery_ids = _aligned_user_ids(feature_frames, view_names, "discovery")
    calibration_ids = _aligned_user_ids(feature_frames, view_names, "calibration")
    confirmation_ids = _aligned_user_ids(feature_frames, view_names, "confirmation")
    if min(len(discovery_ids), len(calibration_ids), len(confirmation_ids)) < 16:
        raise RuntimeError("Atlas cannot establish aligned E1 splits with at least 16 authors each.")
    scalers = runtime["scalers"]
    train_ids = [*discovery_ids, *calibration_ids]
    train = _blocks(feature_frames, scalers, view_names, train_ids)
    confirmation = _blocks(feature_frames, scalers, view_names, confirmation_ids)
    alpha = float(args.ridge_alpha) if args.ridge_alpha is not None else float(runtime["selected_alpha"])
    maps = fit_directed_maps(train, view_names=view_names, ridge_alpha=alpha)
    permuted_maps = fit_directed_maps(train, view_names=view_names, ridge_alpha=alpha, permutation_seed=20260714)
    edges = evaluate_directed_atlas(
        train, confirmation, view_names=view_names, maps=maps, permuted_maps=permuted_maps
    )
    asymmetry = atlas_asymmetry(edges)
    cycles = cycle_errors(confirmation, view_names=view_names, maps=maps)
    r2_matrix = edges.pivot(index="source_view", columns="target_view", values="direct_global_r2").reindex(
        index=view_names, columns=view_names
    )
    r2_matrix.to_csv(output_dir / "directed_r2_matrix.csv")
    edges.to_csv(output_dir / "atlas_edges.csv", index=False)
    asymmetry.to_csv(output_dir / "atlas_asymmetry.csv", index=False)
    cycles.to_csv(output_dir / "cycle_errors.csv", index=False)
    runtime_output = output_dir / "artifacts" / "operator_atlas_runtime.joblib"
    runtime_output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        "e1_runtime": str(runtime_path),
        "view_names": view_names,
        "ridge_alpha": alpha,
        "directed_maps": maps,
        "permuted_maps": permuted_maps,
        "evidence_status": "HOLDOUT_REUSED_EXPLORATORY",
    }, runtime_output)
    manifest = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "e1_dir": str(args.e1_dir),
        "view_names": list(view_names),
        "split_counts": {"discovery": len(discovery_ids), "calibration": len(calibration_ids), "confirmation": len(confirmation_ids)},
        "ridge_alpha": alpha,
        "evidence_status": "HOLDOUT_REUSED_EXPLORATORY",
        "e1_inventory_status": inventory_check["status"],
        "runtime_artifact": str(runtime_output),
        "claim_boundary": "Frozen E1 author features only; no external labels or raw text read. E3 reuses E1 confirmation authors and is exploratory, not an independent confirmation.",
    }
    (output_dir / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_report(report_path, output_dir=output_dir, alpha=alpha, evidence_status="HOLDOUT_REUSED_EXPLORATORY", edges=edges, asymmetry=asymmetry, cycles=cycles)
    inventory = write_artifact_inventory(output_dir, output_dir / "artifact_inventory.json")
    print(json.dumps({
        "output_dir": str(output_dir),
        "report": str(report_path),
        "mean_direct_r2": float(edges["direct_global_r2"].mean()),
        "mean_permuted_r2": float(edges["permuted_direct_global_r2"].mean()),
        "mean_cycle_r2": float(cycles["cycle_global_r2"].mean()),
        "evidence_status": "HOLDOUT_REUSED_EXPLORATORY",
        "artifact_files": inventory["n_files"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
