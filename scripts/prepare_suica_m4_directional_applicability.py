#!/usr/bin/env python3
"""Freeze outcome-blind M4 fixed-coverage directional cells."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _expanded_worlds,
    _load,
    _rcca_parameters,
)
from suica_core.m4_applicability_signature import (  # noqa: E402
    m4_applicability_signature,
)
from suica_core.m4_boundary_ecology import support_geometry  # noqa: E402
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_pre_response_condition,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
    freeze_m4_condition_transform,
)
from suica_core.m4_directional_applicability import (  # noqa: E402
    DIRECTION_MODES,
    intervene_evaluation_direction,
)
from suica_core.m4_response_safe_chart_bundle import (  # noqa: E402
    file_sha256,
    pre_response_digest,
    runtime_fingerprint,
    source_hash_manifest,
    write_basis_bundle,
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


def _variant(
    observed: Any,
    chart: Any,
    *,
    target_count: int | None,
    mode: str | None,
    amplitude: float,
) -> tuple[Any, tuple[int, ...], Any]:
    if target_count is None:
        return observed, (), support_geometry(chart, observed)
    result = intervene_evaluation_direction(
        observed,
        chart,
        target_count=target_count,
        mode=str(mode),
        amplitude_multiplier=amplitude,
    )
    return result.observed, result.selected_conditions, result.geometry


def _fit_pre_response_cell(
    *,
    world: str,
    spec: M4ChartEcologySpec,
    candidates: tuple[dict[str, Any], ...],
    config: dict[str, Any],
    initial_seed: int,
) -> tuple[int, int, Any, Any, Any, Any]:
    attempts = int(config.get("pre_response_seed_attempts", 25))
    for attempt in range(attempts):
        seed = initial_seed + attempt * 100_000_019
        observed = generate_m4_pre_response_condition(
            world=world,
            spec=spec,
            seed=seed,
        )
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
            **_rcca_parameters(config, seed=seed),
        )
        non_support = tuple(
            reason
            for reason in chart.refusal_reasons
            if reason != "SUPPORT_SHIFT"
        )
        native = support_geometry(chart, observed)
        native_count = int(np.sum(
            native.role_masks["mechanism_evaluation"]
        ))
        other_coverage = min(
            value
            for role, value in native.role_coverage.items()
            if role != "mechanism_evaluation"
        )
        if (
            not non_support
            and native_count
            >= int(config["minimum_native_evaluation_count"])
            and other_coverage
            >= float(config["minimum_native_other_role_coverage"])
        ):
            return (
                seed,
                attempt,
                observed,
                old_transform,
                chart,
                native,
            )
    raise ValueError(
        f"{world} has no outcome-blind support-sufficient seed in "
        f"{attempts} attempts"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path)
    args = parser.parse_args()
    config = _load(args.config)
    if tuple(config["direction_modes"]) != DIRECTION_MODES:
        raise ValueError("direction modes differ from the frozen implementation")
    output = args.output_directory or Path(config["chart_bundle_directory"])
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)

    r1_path = ROOT / config["r1_decision_path"]
    if _load(r1_path)["decision"] != "M4_C35_R1_CONFIRMATION_GO":
        raise ValueError("R1 confirmation GO is required")
    spec = M4ChartEcologySpec(**config["spec"])
    candidates = tuple(dict(value) for value in config["chart_candidates"])
    targets = tuple(int(value) for value in config["coverage_target_counts"])
    worlds = _expanded_worlds(config)
    cells: list[dict[str, Any]] = []
    for repetition in range(int(config["repetitions"])):
        for world_index, (world_type, generator_world, world) in enumerate(worlds):
            initial_seed = int(
                config["seed"]
                + repetition * 1_000_003
                + world_index * 10_003
            )
            (
                seed,
                seed_attempt,
                observed,
                old_transform,
                chart,
                native,
            ) = _fit_pre_response_cell(
                world=generator_world,
                spec=spec,
                candidates=candidates,
                config=config,
                initial_seed=initial_seed,
            )
            native_count = int(np.sum(
                native.role_masks["mechanism_evaluation"]
            ))
            definitions: list[tuple[str, int | None, str | None]] = [
                ("native", None, None)
            ]
            definitions.extend(
                (
                    f"count_{target:02d}__{mode}",
                    target,
                    mode,
                )
                for target in targets
                for mode in DIRECTION_MODES
            )
            for variant, target, mode in definitions:
                current, selected, geometry = _variant(
                    observed,
                    chart,
                    target_count=target,
                    mode=mode,
                    amplitude=float(config["support_intervention_amplitude"]),
                )
                bases = {
                    "B0": _old_basis(old_transform, current),
                    "R": build_response_safe_rcca_basis(chart, current),
                }
                signature = m4_applicability_signature(
                    current,
                    chart,
                    bases,
                )
                bundle_name = (
                    f"rep_{repetition:02d}__{world}__{variant}.npz"
                )
                bundle_hash = write_basis_bundle(
                    output / bundle_name,
                    bases,
                )
                count = int(np.sum(
                    geometry.role_masks["mechanism_evaluation"]
                ))
                cells.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "world_type": world_type,
                        "generator_world": generator_world,
                        "initial_seed": initial_seed,
                        "seed": seed,
                        "seed_attempt": seed_attempt,
                        "variant": variant,
                        "target_count": target,
                        "direction_mode": mode,
                        "native_evaluation_count": native_count,
                        "evaluation_count": count,
                        "selected_conditions": list(selected),
                        "minimum_coverage": geometry.minimum_coverage,
                        "role_coverage": geometry.role_coverage,
                        "historical_accept": (
                            geometry.minimum_coverage
                            >= float(config["coverage_threshold"])
                        ),
                        "shared_rank": int(chart.shared_rank),
                        "base_refusal_reasons": list(chart.refusal_reasons),
                        "pre_response_digest": pre_response_digest(current),
                        "signature": signature,
                        "bundle": bundle_name,
                        "bundle_sha256": bundle_hash,
                    }
                )

    protocol = ROOT / config["protocol_path"]
    source_paths = list((ROOT / "suica_core").glob("*.py"))
    source_paths.extend(
        ROOT / "scripts" / name
        for name in (
            "prepare_suica_m4_directional_applicability.py",
            "score_suica_m4_directional_applicability_shard.py",
            "analyze_suica_m4_directional_applicability.py",
        )
    )
    manifest = {
        "version": "suica-m4-c35-r2c-directional-applicability-manifest-v1",
        "estimand_id": config["estimand_id"],
        "config_path": str(args.config),
        "config_sha256": file_sha256(args.config),
        "protocol_path": config["protocol_path"],
        "protocol_sha256": file_sha256(protocol),
        "r1_decision_path": config["r1_decision_path"],
        "r1_decision_sha256": file_sha256(r1_path),
        "source_sha256": source_hash_manifest(ROOT, source_paths),
        "runtime": runtime_fingerprint(),
        "cells": cells,
        "boundary": (
            "All support counts, directions, B0/R bases, signatures, and "
            "digests were frozen before response or oracle endpoints opened."
        ),
    }
    manifest_path = output / "stage_a_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(
        {
            "manifest": str(manifest_path),
            "manifest_sha256": file_sha256(manifest_path),
            "cells": len(cells),
            "main_cells": sum(c["world_type"] == "main" for c in cells),
            "seed_retries": sum(c["seed_attempt"] > 0 for c in cells)
            // 9,
        },
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
