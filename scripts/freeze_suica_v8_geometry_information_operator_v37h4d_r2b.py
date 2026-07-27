#!/usr/bin/env python3
"""Freeze the R2B six-coordinate operator before R2C outcomes exist."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.analyze_suica_v8_geometry_information_operator_v37h4d_r2b import (  # noqa: E402
    _model,
    build_feature_frame,
    select_ridge_c,
)
from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _read,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)


DEFAULT_INPUT = (
    ROOT
    / "results"
    / "v8_geometry_information_operator"
    / "v37h4d_r2b_discovery_12600rows_20260727"
)
DEFAULT_CONFIG = (
    ROOT
    / "configs"
    / "v8_geometry_information_operator_v37h4d_r2b_analysis.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_geometry_information_operator"
    / "v37h4d_r2b_frozen_operator_20260727"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    config = _read(args.config)
    rows_path = args.input_dir / "geometry_rows.csv"
    rows = pd.read_csv(rows_path)
    frame = build_feature_frame(rows)
    feature_columns = [
        *map(str, config["scalar_features"]),
        *map(str, config["operator_features"]),
    ]
    features = frame[feature_columns].to_numpy(dtype=float)
    response = rows["crc_or_hc_detected"].to_numpy(dtype=int)
    groups = rows["base_id"].to_numpy()
    selected_c = select_ridge_c(
        features,
        response,
        groups,
        candidates=list(map(float, config["ridge_c_grid"])),
        folds=5,
    )
    model = _model(selected_c)
    model.fit(features, response)
    scaler = model.named_steps["standardscaler"]
    logistic = model.named_steps["logisticregression"]
    artifact = {
        "artifact_id": "V8_H4D_R2B_FROZEN_SIX_COORDINATE_OPERATOR",
        "status": "FROZEN_BEFORE_R2C_OUTCOMES",
        "feature_columns": feature_columns,
        "selected_c": float(selected_c),
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_scale": scaler.scale_.tolist(),
        "logistic_coefficient": logistic.coef_[0].tolist(),
        "logistic_intercept": float(logistic.intercept_[0]),
        "training_rows": int(len(rows)),
        "training_base_ids": int(rows["base_id"].nunique()),
        "training_geometry_sha256": _sha256(rows_path),
        "analysis_config_sha256": _sha256(args.config),
        "claim_boundary": (
            "Frozen synthetic detector-power comparator only. It is not an "
            "observable text measure or psychological model."
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = args.output_dir / "frozen_operator.json"
    _write(artifact_path, artifact)
    decision = {
        "status": "V8_H4D_R2B_SIX_COORDINATE_OPERATOR_FROZEN",
        "artifact_sha256": _sha256(artifact_path),
        "selected_c": float(selected_c),
        "feature_count": len(feature_columns),
    }
    _write(args.output_dir / "decision.json", decision)
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[rows_path],
        config_path=args.config,
        code_paths=[
            Path(__file__),
            ROOT
            / "scripts"
            / "analyze_suica_v8_geometry_information_operator_v37h4d_r2b.py",
        ],
        estimand_id="V8_H4D_R2B_FROZEN_OPERATOR_FOR_R2C",
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
