#!/usr/bin/env python3
"""Open and score one sealed directional-applicability repetition shard."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _creation_parameters,
    _load,
    _loop,
    _rcca_parameters,
    _route_parameters,
)
from suica_core.m4_applicability_signature import (  # noqa: E402
    m4_applicability_signature,
)
from suica_core.m4_boundary_ecology import support_geometry  # noqa: E402
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
    freeze_m4_condition_transform,
)
from suica_core.m4_creation_intervention import (  # noqa: E402
    author_relation_geometry,
)
from suica_core.m4_directional_applicability import (  # noqa: E402
    intervene_evaluation_direction,
)
from suica_core.m4_opportunity_excitation import (  # noqa: E402
    build_excited_observed,
    subset_opportunity_budget,
)
from suica_core.m4_physical_edge_composition import (  # noqa: E402
    fit_m4_physical_edge_route,
)
from suica_core.m4_response_safe_chart_bundle import (  # noqa: E402
    file_sha256,
    pre_response_digest,
    read_basis_bundle,
    runtime_fingerprint,
    sanitize_pre_response,
    verify_source_hash_manifest,
)
from suica_core.m4_response_safe_chart_replacement import (  # noqa: E402
    build_current_pooled_attribution_route,
)
from suica_core.m4_response_safe_rcca_chart import (  # noqa: E402
    build_response_safe_rcca_basis,
    fit_response_safe_rcca_chart,
)


def _old_basis(transform: Any, observed: Any) -> dict[str, np.ndarray]:
    return {
        role: transform.transform_prototypes(
            getattr(observed, f"mechanism_{role}").pre_context
        )
        for role in ("calibration", "selection", "evaluation")
    }


def _maximum_basis_error(
    expected: dict[str, dict[str, np.ndarray]],
    actual: dict[str, dict[str, np.ndarray]],
) -> float:
    return max(
        float(np.max(np.abs(
            np.asarray(expected[arm][role])
            - np.asarray(actual[arm][role])
        )))
        for arm in ("B0", "R")
        for role in ("calibration", "selection", "evaluation")
    )


def _maximum_signature_error(
    expected: dict[str, float],
    actual: dict[str, float],
) -> float:
    if set(expected) != set(actual):
        raise ValueError("applicability signature fields changed after seal")
    return max(abs(float(expected[key]) - float(actual[key])) for key in expected)


def _array_digest(values: list[np.ndarray]) -> str:
    digest = hashlib.sha256()
    for value in values:
        array = np.ascontiguousarray(np.asarray(value))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(str(array.shape).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def _truth_digest(passive: Any, truth: Any) -> str:
    arrays = [
        passive.ecology.train_calibration.response,
        passive.ecology.train_selection.response,
        passive.ecology.train_evaluation.response,
        passive.ecology.test_calibration.response,
        passive.ecology.test_selection.response,
        passive.ecology.test_evaluation.response,
    ]
    arrays.extend(truth.oracle_basis[role] for role in sorted(truth.oracle_basis))
    return _array_digest(arrays)


def _replay(observed: Any, chart: Any, metadata: dict[str, Any], config: dict[str, Any]):
    if metadata["target_count"] is None:
        current = observed
        selected: tuple[int, ...] = ()
        geometry = support_geometry(chart, observed)
    else:
        result = intervene_evaluation_direction(
            observed,
            chart,
            target_count=int(metadata["target_count"]),
            mode=str(metadata["direction_mode"]),
            amplitude_multiplier=float(config["support_intervention_amplitude"]),
        )
        current = result.observed
        selected = result.selected_conditions
        geometry = result.geometry
    if list(selected) != list(metadata["selected_conditions"]):
        raise ValueError("directional selection does not replay Phase A")
    if pre_response_digest(current) != metadata["pre_response_digest"]:
        raise ValueError("directional pre-response digest mismatch")
    if not np.isclose(
        geometry.minimum_coverage,
        float(metadata["minimum_coverage"]),
    ):
        raise ValueError("directional coverage does not replay Phase A")
    if not np.array_equal(
        current.mechanism_evaluation.response,
        observed.mechanism_evaluation.response,
    ):
        raise ValueError("directional intervention changed response data")
    return current, geometry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--chart-bundle-directory", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256", required=True)
    parser.add_argument("--repetition-start", type=int, required=True)
    parser.add_argument("--repetition-end", type=int, required=True)
    parser.add_argument("--output-directory", type=Path)
    args = parser.parse_args()
    config = _load(args.config)
    if not (0 <= args.repetition_start < args.repetition_end <= int(config["repetitions"])):
        raise ValueError("invalid repetition shard")
    bundle_root = args.chart_bundle_directory
    if not bundle_root.is_absolute():
        bundle_root = ROOT / bundle_root
    manifest_path = bundle_root / "stage_a_manifest.json"
    if file_sha256(manifest_path) != args.expected_manifest_sha256:
        raise ValueError("Stage-A directional manifest hash mismatch")
    manifest = _load(manifest_path)
    if manifest["config_sha256"] != file_sha256(args.config):
        raise ValueError("config changed after directional sealing")
    protocol = ROOT / manifest["protocol_path"]
    if manifest["protocol_sha256"] != file_sha256(protocol):
        raise ValueError("protocol changed after directional sealing")
    r1_path = ROOT / manifest["r1_decision_path"]
    if manifest["r1_decision_sha256"] != file_sha256(r1_path):
        raise ValueError("R1 decision changed after directional sealing")
    verify_source_hash_manifest(ROOT, manifest["source_sha256"])
    if manifest["runtime"] != runtime_fingerprint():
        raise ValueError("runtime changed after directional sealing")

    selected_cells = [
        cell
        for cell in manifest["cells"]
        if args.repetition_start
        <= int(cell["repetition"])
        < args.repetition_end
    ]
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for cell in selected_cells:
        key = (int(cell["repetition"]), str(cell["world"]))
        grouped.setdefault(key, []).append(cell)
    spec = M4ChartEcologySpec(**config["spec"])
    candidates = tuple(dict(value) for value in config["chart_candidates"])
    route_parameters = _route_parameters(config)
    creation_parameters = _creation_parameters(config)
    rows: list[dict[str, Any]] = []
    for _, cells in sorted(grouped.items()):
        first = cells[0]
        passive, truth = generate_m4_chart_ecology_world(
            world=first["generator_world"],
            spec=spec,
            seed=int(first["seed"]),
        )
        truth_before = _truth_digest(passive, truth)
        observed = sanitize_pre_response(passive.condition)
        old_chart = fit_m4_condition_chart(
            observed,
            candidates=candidates,
            **config["chart_thresholds"],
        )
        old_transform = freeze_m4_condition_transform(
            observed,
            old_chart,
            rank_tolerance=float(config["rank_tolerance"]),
            maximum_rank=int(config["maximum_rank"]),
        )
        chart = fit_response_safe_rcca_chart(
            observed,
            **_rcca_parameters(config, seed=int(first["seed"])),
        )
        excited = build_excited_observed(
            passive,
            truth,
            spec,
            seed=int(first["seed"]),
            amplitude=float(config["excitation_amplitude"]),
        )
        anchor_observed = subset_opportunity_budget(
            passive,
            calibration_occasions=int(config["anchor_budget"]["calibration"]),
            selection_occasions=int(config["anchor_budget"]["selection"]),
        )
        oracle_route = fit_m4_physical_edge_route(
            passive.ecology,
            truth.oracle_basis,
            basis_name="oracle_max_passive",
            **route_parameters,
        )
        oracle_estimated_route = build_current_pooled_attribution_route(
            excited.ecology,
            truth.oracle_basis,
            **creation_parameters,
        )
        target = oracle_route.test.jacobian_loop
        for metadata in sorted(cells, key=lambda value: value["variant"]):
            current, geometry = _replay(observed, chart, metadata, config)
            actual = {
                "B0": _old_basis(old_transform, current),
                "R": build_response_safe_rcca_basis(chart, current),
            }
            loaded = read_basis_bundle(
                bundle_root / metadata["bundle"],
                expected_sha256=metadata["bundle_sha256"],
            )
            basis_error = _maximum_basis_error(loaded, actual)
            signature = m4_applicability_signature(current, chart, loaded)
            signature_error = _maximum_signature_error(
                metadata["signature"],
                signature,
            )
            if basis_error > 1e-12 or signature_error > 1e-12:
                raise ValueError("directional basis/signature failed exact replay")
            anchor = fit_m4_physical_edge_route(
                anchor_observed.ecology,
                loaded["B0"],
                basis_name="anchor_old_response_safe",
                **route_parameters,
            )
            routes = {
                arm: build_current_pooled_attribution_route(
                    excited.ecology,
                    loaded[arm],
                    **creation_parameters,
                )
                for arm in ("B0", "R")
            }
            routes["Oest"] = oracle_estimated_route
            score = {
                arm: author_relation_geometry(
                    _loop(route, anchor, "test"),
                    target,
                )
                for arm, route in routes.items()
            }
            gain = score["R"] - score["B0"]
            row = {
                "repetition": int(metadata["repetition"]),
                "world": str(metadata["world"]),
                "world_type": str(metadata["world_type"]),
                "variant": str(metadata["variant"]),
                "target_count": metadata["target_count"],
                "direction_mode": metadata["direction_mode"],
                "evaluation_count": int(metadata["evaluation_count"]),
                "minimum_coverage": float(geometry.minimum_coverage),
                "historical_accept": bool(metadata["historical_accept"]),
                "geometry_B0": score["B0"],
                "geometry_R": score["R"],
                "geometry_Oest": score["Oest"],
                "forced_r_gain": gain,
                "oracle_error": score["Oest"] - score["R"],
                "harmful": gain < float(config["harm_threshold"]),
                "basis_replay_error": basis_error,
                "signature_replay_error": signature_error,
                "response_identity_error": 0.0,
                **signature,
            }
            rows.append(row)
        if _truth_digest(passive, truth) != truth_before:
            raise ValueError("scoring mutated response or oracle truth")

    output = args.output_directory or Path(config["shard_directory"])
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)
    path = output / (
        f"metrics_rep_{args.repetition_start:02d}_{args.repetition_end:02d}.csv"
    )
    pd.DataFrame(rows).to_csv(path, index=False)
    metadata_path = path.with_suffix(".json")
    metadata_path.write_text(
        json.dumps(
            {
                "manifest_sha256": args.expected_manifest_sha256,
                "repetition_start": args.repetition_start,
                "repetition_end": args.repetition_end,
                "rows": len(rows),
                "metrics_sha256": file_sha256(path),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(metadata_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
