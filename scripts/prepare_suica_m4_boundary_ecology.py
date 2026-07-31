#!/usr/bin/env python3
"""Freeze outcome-blind M4-C.3.5 support-boundary interventions."""
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
    _expanded_worlds,
    _load,
    _rcca_parameters,
)
from suica_core.m4_boundary_ecology import (  # noqa: E402
    intervene_evaluation_support,
    support_geometry,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_pre_response_condition,
)
from suica_core.m4_condition_manifold_estimator import (  # noqa: E402
    fit_m4_condition_chart,
    freeze_m4_condition_transform,
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


def _old_basis(transform, observed):
    return {
        role: transform.transform_prototypes(
            getattr(observed, f"mechanism_{role}").pre_context
        )
        for role in ("calibration", "selection", "evaluation")
    }


def _variant_observed(observed, chart, target, config):
    if target is None:
        geometry = support_geometry(chart, observed)
        return observed, (), geometry
    intervention = intervene_evaluation_support(
        observed,
        chart,
        target_count=int(target),
        amplitude_multiplier=float(
            config["support_intervention_amplitude"]
        ),
    )
    return (
        intervention.observed,
        intervention.selected_conditions,
        intervention.geometry,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path)
    args = parser.parse_args()
    config = _load(args.config)
    output = (
        args.output_directory
        if args.output_directory is not None
        else Path(config["chart_bundle_directory"])
    )
    if not output.is_absolute():
        output = ROOT / output
    output.mkdir(parents=True, exist_ok=True)

    r1_path = ROOT / config["r1_decision_path"]
    r1 = _load(r1_path)
    if r1["decision"] != "M4_C35_R1_CONFIRMATION_GO":
        raise ValueError("R1 confirmation GO is required")

    spec = M4ChartEcologySpec(**config["spec"])
    candidates = tuple(dict(value) for value in config["chart_candidates"])
    threshold = float(config["coverage_threshold"])
    targets = tuple(int(value) for value in config["coverage_target_counts"])
    cells = []
    worlds = _expanded_worlds(config)
    for repetition in range(int(config["repetitions"])):
        for world_index, (world_type, generator_world, world) in enumerate(
            worlds
        ):
            seed = int(
                config["seed"]
                + repetition * 1_000_003
                + world_index * 10_003
            )
            observed = generate_m4_pre_response_condition(
                world=generator_world,
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
            rcca = fit_response_safe_rcca_chart(
                observed,
                **_rcca_parameters(config, seed=seed),
            )
            non_boundary_reasons = tuple(
                reason
                for reason in rcca.refusal_reasons
                if reason != "SUPPORT_SHIFT"
            )
            if non_boundary_reasons:
                raise ValueError(
                    f"{repetition}/{world} has non-boundary refusal: "
                    f"{non_boundary_reasons}"
                )
            native = support_geometry(rcca, observed)
            native_count = int(np.sum(
                native.role_masks["mechanism_evaluation"]
            ))
            if native_count < int(
                config["minimum_native_evaluation_count"]
            ):
                raise ValueError(
                    f"{repetition}/{world} native evaluation support "
                    f"is only {native_count}/{spec.categories}"
                )
            other_coverage = min(
                value
                for role, value in native.role_coverage.items()
                if role != "mechanism_evaluation"
            )
            if other_coverage < float(
                config["minimum_native_other_role_coverage"]
            ):
                raise ValueError(
                    f"{repetition}/{world} non-evaluation coverage "
                    f"is only {other_coverage}"
                )

            statuses = []
            for variant, target in (
                ("native", None),
                *((f"evaluation_count_{value:02d}", value) for value in targets),
            ):
                current, selected, geometry = _variant_observed(
                    observed,
                    rcca,
                    target,
                    config,
                )
                evaluation_count = int(np.sum(
                    geometry.role_masks["mechanism_evaluation"]
                ))
                accepted = geometry.minimum_coverage >= threshold
                bases = {
                    "B0": _old_basis(old_transform, current),
                    "R": build_response_safe_rcca_basis(rcca, current),
                }
                bundle_name = (
                    f"rep_{repetition:02d}__{world}__{variant}.npz"
                )
                bundle_path = output / bundle_name
                bundle_hash = write_basis_bundle(bundle_path, bases)
                cells.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "world_type": world_type,
                        "generator_world": generator_world,
                        "seed": seed,
                        "variant": variant,
                        "target_count": target,
                        "native_evaluation_count": native_count,
                        "evaluation_count": evaluation_count,
                        "selected_conditions": list(selected),
                        "minimum_coverage": geometry.minimum_coverage,
                        "minimum_margin": (
                            geometry.minimum_coverage - threshold
                        ),
                        "role_coverage": geometry.role_coverage,
                        "accepted": accepted,
                        "shared_rank": int(rcca.shared_rank),
                        "base_refusal_reasons": list(
                            rcca.refusal_reasons
                        ),
                        "pre_response_digest": pre_response_digest(current),
                        "bundle": bundle_name,
                        "bundle_sha256": bundle_hash,
                    }
                )
                statuses.append(accepted)
            if not any(statuses) or all(statuses):
                raise ValueError(
                    f"{repetition}/{world} does not cross the frozen "
                    "coverage boundary"
                )

    protocol = ROOT / config["protocol_path"]
    source_paths = list((ROOT / "suica_core").glob("*.py"))
    source_paths.extend(
        [
            ROOT / "scripts" / "prepare_suica_m4_boundary_ecology.py",
            ROOT / "scripts" / "run_suica_m4_boundary_ecology_sealed.py",
        ]
    )
    manifest = {
        "version": "suica-m4-c35-r2c-boundary-ecology-manifest-v1",
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
            "All interventions, coverage decisions, and B0/R bases were "
            "frozen from pre-response tensors before any response or oracle "
            "endpoint was opened."
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
            "accepted": sum(cell["accepted"] for cell in cells),
            "refused": sum(not cell["accepted"] for cell in cells),
        },
        indent=2,
        sort_keys=True,
    ))


if __name__ == "__main__":
    main()
