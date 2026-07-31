#!/usr/bin/env python3
"""Seal the pre-response acceptance policy for M4-C.3.5-R2C."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _load,
    _rcca_parameters,
)
from suica_core.m4_abstention_routing import (  # noqa: E402
    rcca_coverage_profile,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_pre_response_condition,
)
from suica_core.m4_response_safe_chart_bundle import (  # noqa: E402
    file_sha256,
    read_basis_bundle,
    runtime_fingerprint,
    source_hash_manifest,
    verify_source_hash_manifest,
)
from suica_core.m4_response_safe_rcca_chart import (  # noqa: E402
    build_response_safe_rcca_basis,
    fit_response_safe_rcca_chart,
)


def _world_stratum(config: dict, world: str, world_type: str) -> str:
    if world_type == "null":
        return "null"
    for name in ("eligible", "sentinel", "boundary"):
        if world in config.get(f"{name}_worlds", []):
            return name
    raise ValueError(f"main world has no R2C stratum: {world}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--chart-bundle-directory", type=Path, required=True)
    parser.add_argument("--expected-stage-a-manifest-sha256", required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    args = parser.parse_args()
    config = _load(args.config)
    bundle_root = args.chart_bundle_directory
    if not bundle_root.is_absolute():
        bundle_root = ROOT / bundle_root
    stage_a_path = bundle_root / "stage_a_manifest.json"
    stage_a_hash = file_sha256(stage_a_path)
    if stage_a_hash != args.expected_stage_a_manifest_sha256:
        raise ValueError("Stage-A manifest does not match the requested seal")
    stage_a = _load(stage_a_path)
    if stage_a["config_sha256"] != file_sha256(args.config):
        raise ValueError("config changed after Stage-A chart sealing")
    verify_source_hash_manifest(ROOT, stage_a["source_sha256"])
    if stage_a["runtime"] != runtime_fingerprint():
        raise ValueError("runtime changed after Stage-A chart sealing")
    if stage_a.get("protocol_path") is not None:
        protocol = ROOT / stage_a["protocol_path"]
        if stage_a["protocol_sha256"] != file_sha256(protocol):
            raise ValueError("protocol changed after Stage-A chart sealing")

    spec = M4ChartEcologySpec(**config["spec"])
    threshold = float(config["rcca"]["minimum_coverage"])
    cells = []
    for metadata in stage_a["cells"]:
        observed = generate_m4_pre_response_condition(
            world=metadata["generator_world"],
            spec=spec,
            seed=int(metadata["seed"]),
        )
        chart = fit_response_safe_rcca_chart(
            observed,
            **_rcca_parameters(config, seed=int(metadata["seed"])),
        )
        profile = rcca_coverage_profile(
            chart,
            observed,
            minimum_coverage=threshold,
        )
        if not np.isclose(profile.minimum_coverage, chart.coverage):
            raise ValueError("continuous coverage does not replay chart")
        if bool(chart.refused) != bool(metadata["rcca_refused"]):
            raise ValueError("acceptance decision does not replay Stage A")
        if tuple(chart.refusal_reasons) != tuple(
            metadata["rcca_refusal_reasons"]
        ):
            raise ValueError("refusal reasons do not replay Stage A")
        loaded = read_basis_bundle(
            bundle_root / metadata["bundle"],
            expected_sha256=metadata["bundle_sha256"],
        )
        replay = build_response_safe_rcca_basis(chart, observed)
        basis_error = max(
            float(np.max(np.abs(replay[role] - loaded["R"][role])))
            for role in ("calibration", "selection", "evaluation")
        )
        if basis_error > 1e-12:
            raise ValueError("RCCA basis does not replay Stage A")
        cells.append(
            {
                "repetition": int(metadata["repetition"]),
                "world": str(metadata["world"]),
                "world_type": str(metadata["world_type"]),
                "stratum": _world_stratum(
                    config,
                    str(metadata["world"]),
                    str(metadata["world_type"]),
                ),
                "accepted": not bool(chart.refused),
                "minimum_coverage": profile.minimum_coverage,
                "minimum_margin": profile.minimum_margin,
                "coverage_threshold": threshold,
                "coverage_knn_threshold": profile.threshold,
                "role_coverage": profile.role_coverage,
                "refusal_reasons": list(chart.refusal_reasons),
                "shared_rank": int(chart.shared_rank),
                "basis_replay_error": basis_error,
            }
        )

    source_paths = list((ROOT / "suica_core").glob("*.py"))
    source_paths.extend(
        [
            ROOT / "scripts" / "prepare_suica_m4_abstention_policy.py",
            ROOT / "scripts" / "evaluate_suica_m4_abstention_policy.py",
            ROOT / "scripts" / "run_suica_m4_response_safe_chart_replacement_sealed.py",
            ROOT / "scripts" / "aggregate_suica_m4_response_safe_chart_replacement.py",
        ]
    )
    protocol_value = config.get("policy_protocol_path")
    protocol_path = ROOT / protocol_value if protocol_value else None
    if protocol_path is not None and not protocol_path.is_file():
        raise ValueError(f"policy protocol does not exist: {protocol_value}")
    manifest = {
        "version": "suica-m4-c35-r2c-abstention-policy-manifest-v1",
        "estimand_id": config["policy_estimand_id"],
        "config_path": str(args.config),
        "config_sha256": file_sha256(args.config),
        "stage_a_manifest_path": str(stage_a_path.relative_to(ROOT)),
        "stage_a_manifest_sha256": stage_a_hash,
        "policy_protocol_path": protocol_value,
        "policy_protocol_sha256": (
            file_sha256(protocol_path)
            if protocol_path is not None
            else None
        ),
        "source_sha256": source_hash_manifest(ROOT, source_paths),
        "runtime": runtime_fingerprint(),
        "cells": cells,
        "boundary": (
            "Acceptance, fallback, continuous coverage, and all chart bases "
            "were frozen from pre-response condition tensors before any "
            "R2C response or oracle endpoint was opened."
        ),
    }
    output = args.output_path
    if not output.is_absolute():
        output = ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(
        json.dumps(
            {
                "manifest": str(output),
                "manifest_sha256": file_sha256(output),
                "cells": len(cells),
                "accepted": sum(value["accepted"] for value in cells),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
