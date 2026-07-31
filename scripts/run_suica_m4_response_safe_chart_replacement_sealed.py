#!/usr/bin/env python3
"""Open outcomes only after M4-C.3.5-R2 chart bundles are sealed."""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _alias_mechanism_conditions,
    _arm_metric_rows,
    _creation_parameters,
    _decision,
    _expanded_worlds,
    _load,
    _loop,
    _max_loop_difference,
    _report,
    _route_parameters,
)
from suica_core.m4_chart_ecology_generator import (  # noqa: E402
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
)
from suica_core.m4_creation_intervention import (  # noqa: E402
    author_relation_geometry,
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
    linear_cka,
    rotate_spectral_block_basis,
)


def _rcca_proxy(metadata: dict[str, Any]) -> SimpleNamespace:
    return SimpleNamespace(
        support_ranks=tuple(metadata["rcca_support_ranks"]),
        shared_rank_lower=int(metadata["rcca_shared_rank_lower"]),
        shared_rank_upper=int(metadata["rcca_shared_rank_upper"]),
        shared_rank=int(metadata["rcca_shared_rank"]),
        spectral_blocks=tuple(
            tuple(value) for value in metadata["rcca_spectral_blocks"]
        ),
        refused=bool(metadata["rcca_refused"]),
        refusal_reasons=tuple(metadata["rcca_refusal_reasons"]),
    )


def _manifest_index(
    manifest: dict[str, Any],
    name: str,
) -> dict[Any, dict[str, Any]]:
    if name == "cells":
        return {
            (int(value["repetition"]), str(value["world"])): value
            for value in manifest[name]
        }
    return {
        int(value["repetition"]): value
        for value in manifest[name]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=(
            ROOT / "configs" / "m4_response_safe_chart_replacement.development.json"
        ),
    )
    parser.add_argument("--chart-bundle-directory", type=Path, required=True)
    parser.add_argument("--expected-manifest-sha256")
    parser.add_argument("--repetition-limit", type=int)
    parser.add_argument("--repetition-start", type=int)
    parser.add_argument("--output-directory")
    parser.add_argument("--report-path")
    args = parser.parse_args()
    config = _load(args.config)
    bundle_root = args.chart_bundle_directory
    if not bundle_root.is_absolute():
        bundle_root = ROOT / bundle_root
    manifest_path = bundle_root / "stage_a_manifest.json"
    manifest_sha256 = file_sha256(manifest_path)
    if (
        args.expected_manifest_sha256 is not None
        and manifest_sha256 != args.expected_manifest_sha256
    ):
        raise ValueError(
            "Stage-A manifest hash does not match the preregistered seal"
        )
    if (
        config["phase"] == "confirmation"
        and args.expected_manifest_sha256 is None
    ):
        raise ValueError(
            "confirmation requires --expected-manifest-sha256"
        )
    manifest = _load(manifest_path)
    if manifest["config_sha256"] != file_sha256(args.config):
        raise ValueError("config changed after pre-response chart sealing")
    r1_path = ROOT / manifest["r1_decision_path"]
    if manifest["r1_decision_sha256"] != file_sha256(r1_path):
        raise ValueError("R1 decision changed after chart sealing")
    if manifest["r1_decision"] != "M4_C35_R1_CONFIRMATION_GO":
        raise ValueError("R1 confirmation GO is required")
    if manifest.get("protocol_path") is not None:
        protocol_path = ROOT / manifest["protocol_path"]
        if manifest["protocol_sha256"] != file_sha256(protocol_path):
            raise ValueError("protocol changed after chart sealing")
    verify_source_hash_manifest(ROOT, manifest["source_sha256"])
    if manifest["runtime"] != runtime_fingerprint():
        raise ValueError("numerical runtime changed after chart sealing")

    cells = _manifest_index(manifest, "cells")
    support_controls = _manifest_index(manifest, "support_controls")
    alias_cells = _manifest_index(manifest, "alias_cells")
    manifest_start = int(manifest["repetition_start"])
    manifest_stop = int(manifest["repetition_stop"])
    start = (
        manifest_start
        if args.repetition_start is None
        else int(args.repetition_start)
    )
    stop = (
        manifest_stop
        if args.repetition_limit is None
        else start + int(args.repetition_limit)
    )
    if start < manifest_start or stop > manifest_stop or stop <= start:
        raise ValueError(
            "requested repetition shard is outside the sealed manifest"
        )
    spec = M4ChartEcologySpec(**config["spec"])
    route_parameters = _route_parameters(config)
    creation_parameters = _creation_parameters(config)
    rows: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    worlds = _expanded_worlds(config)

    for repetition in range(start, stop):
        for world_index, (world_type, generator_world, world) in enumerate(
            worlds
        ):
            metadata = cells[(repetition, world)]
            passive, truth = generate_m4_chart_ecology_world(
                world=generator_world,
                spec=spec,
                seed=int(metadata["seed"]),
            )
            condition_digest = pre_response_digest(
                sanitize_pre_response(passive.condition)
            )
            if condition_digest != metadata["pre_response_digest"]:
                raise ValueError(
                    f"pre-response replay mismatch for {repetition}/{world}"
                )
            loaded = read_basis_bundle(
                bundle_root / metadata["bundle"],
                expected_sha256=metadata["bundle_sha256"],
            )
            bases = {
                arm: loaded[arm]
                for arm in ("B0", "Br_var", "Br_rep", "R")
            }
            bases["Oest"] = truth.oracle_basis
            excited = build_excited_observed(
                passive,
                truth,
                spec,
                seed=int(metadata["seed"]),
                amplitude=float(config["excitation_amplitude"]),
            )
            anchor_observed = subset_opportunity_budget(
                passive,
                calibration_occasions=int(
                    config["anchor_budget"]["calibration"]
                ),
                selection_occasions=int(
                    config["anchor_budget"]["selection"]
                ),
            )
            anchor = fit_m4_physical_edge_route(
                anchor_observed.ecology,
                bases["B0"],
                basis_name="anchor_old_response_safe",
                **route_parameters,
            )
            oracle_route = fit_m4_physical_edge_route(
                passive.ecology,
                truth.oracle_basis,
                basis_name="oracle_max_passive",
                **route_parameters,
            )
            routes = {
                arm: build_current_pooled_attribution_route(
                    excited.ecology,
                    basis,
                    **creation_parameters,
                )
                for arm, basis in bases.items()
            }
            rcca = _rcca_proxy(metadata)
            rows.extend(
                _arm_metric_rows(
                    repetition=repetition,
                    world=world,
                    world_type=world_type,
                    routes=routes,
                    bases=bases,
                    anchor=anchor,
                    oracle={
                        "route": oracle_route,
                        "basis": truth.oracle_basis,
                    },
                    old_rank=int(metadata["old_rank"]),
                    rcca=rcca,
                )
            )
            controls.append(
                {
                    "repetition": repetition,
                    "world": world,
                    "control": "basis_contract",
                    "value": float(metadata["basis_trace_error"]),
                    "passed": bool(metadata["basis_contract_passed"]),
                    "details": "",
                }
            )

            if world_type == "main":
                cka_rng = np.random.default_rng(
                    int(config["cka_permutation_seed"])
                    + int(metadata["seed"])
                )
                observed_cka = linear_cka(
                    bases["R"]["evaluation"][:, 1:],
                    truth.oracle_basis["evaluation"][:, 1:],
                )
                exceedances = 0
                repetitions = int(config["cka_permutation_repetitions"])
                for _ in range(repetitions):
                    permutation = cka_rng.permutation(spec.categories)
                    null_cka = linear_cka(
                        bases["R"]["evaluation"][:, 1:],
                        truth.oracle_basis["evaluation"][permutation, 1:],
                    )
                    exceedances += int(null_cka >= observed_cka)
                cka_p = (exceedances + 1) / (repetitions + 1)
                controls.append(
                    {
                        "repetition": repetition,
                        "world": world,
                        "control": "cka_permutation",
                        "value": cka_p,
                        "passed": bool(
                            cka_p
                            <= config["targets"][
                                "maximum_cka_permutation_p"
                            ]
                        ),
                        "details": "",
                    }
                )
                rng = np.random.default_rng(
                    int(config["permutation_seed"]) + int(metadata["seed"])
                )
                permutation = rng.permutation(spec.mechanism_authors)
                permuted = build_current_pooled_attribution_route(
                    excited.ecology,
                    bases["R"],
                    **creation_parameters,
                    second_permutation=permutation,
                )
                native_geometry = author_relation_geometry(
                    _loop(routes["R"], anchor, "test"),
                    oracle_route.test.jacobian_loop,
                )
                permuted_geometry = author_relation_geometry(
                    _loop(permuted, anchor, "test"),
                    oracle_route.test.jacobian_loop,
                )
                controls.extend(
                    [
                        {
                            "repetition": repetition,
                            "world": world,
                            "control": "author_permutation",
                            "value": permuted_geometry - native_geometry,
                            "passed": bool(
                                permuted_geometry - native_geometry
                                <= config["targets"][
                                    "maximum_author_permutation_gain"
                                ]
                            ),
                            "details": "",
                        },
                        {
                            "repetition": repetition,
                            "world": world,
                            "control": "source_shuffle",
                            "value": float(
                                metadata["source_shuffle_rank_lower"]
                            ),
                            "passed": bool(
                                metadata["source_shuffle_passed"]
                            ),
                            "details": "|".join(
                                metadata["source_shuffle_reasons"]
                            ),
                        },
                    ]
                )

            if world_index == 0:
                rotated = rotate_spectral_block_basis(
                    bases["R"],
                    rcca.spectral_blocks,
                    seed=int(metadata["seed"]) + 700_001,
                )
                rotated_route = build_current_pooled_attribution_route(
                    excited.ecology,
                    rotated,
                    **creation_parameters,
                )
                shifted_route = build_current_pooled_attribution_route(
                    excited.ecology,
                    loaded["R_shifted"],
                    **creation_parameters,
                )
                controls.extend(
                    [
                        {
                            "repetition": repetition,
                            "world": world,
                            "control": "block_gauge",
                            "value": _max_loop_difference(
                                routes["R"],
                                rotated_route,
                                anchor,
                            ),
                            "passed": True,
                            "details": "",
                        },
                        {
                            "repetition": repetition,
                            "world": world,
                            "control": "common_shift",
                            "value": _max_loop_difference(
                                routes["R"],
                                shifted_route,
                                anchor,
                            ),
                            "passed": True,
                            "details": "",
                        },
                    ]
                )

        support = support_controls[repetition]
        controls.append(
            {
                "repetition": repetition,
                "world": "evaluation_support_shift",
                "control": "support_shift",
                "value": float(support["refused"]),
                "passed": bool(support["refused"]),
                "details": "|".join(support["refusal_reasons"]),
            }
        )

        alias = alias_cells[repetition]
        alias_passive, alias_truth = generate_m4_chart_ecology_world(
            world="condition_alias_ecology",
            spec=spec,
            seed=int(alias["seed"]),
        )
        aliased_condition = _alias_mechanism_conditions(
            sanitize_pre_response(alias_passive.condition)
        )
        if (
            pre_response_digest(aliased_condition)
            != alias["pre_response_digest"]
        ):
            raise ValueError(f"latent-alias replay mismatch for {repetition}")
        alias_bases = read_basis_bundle(
            bundle_root / alias["bundle"],
            expected_sha256=alias["bundle_sha256"],
        )
        alias_passive = replace(
            alias_passive,
            condition=aliased_condition,
        )
        alias_excited = build_excited_observed(
            alias_passive,
            alias_truth,
            spec,
            seed=int(alias["seed"]),
            amplitude=float(config["excitation_amplitude"]),
        )
        alias_route = build_current_pooled_attribution_route(
            alias_excited.ecology,
            alias_bases["R"],
            **creation_parameters,
        )
        alias_distance = float(np.max(np.linalg.norm(
            alias_route.test.creation[:, 0]
            - alias_route.test.creation[:, 1],
            axis=1,
        )))
        latent_distance = float(np.linalg.norm(
            alias_truth.oracle_basis["evaluation"][0, 1:]
            - alias_truth.oracle_basis["evaluation"][1, 1:]
        ))
        controls.append(
            {
                "repetition": repetition,
                "world": "condition_alias_ecology",
                "control": "latent_alias",
                "value": alias_distance,
                "passed": bool(
                    alias["rcca_refused"]
                    or (
                        latent_distance
                        >= config["targets"]["minimum_latent_alias_distance"]
                        and alias_distance
                        <= config["targets"][
                            "maximum_latent_alias_recovery"
                        ]
                    )
                ),
                "details": json.dumps(
                    {
                        "latent_distance": latent_distance,
                        "refusal_reasons": alias["rcca_refusal_reasons"],
                    },
                    sort_keys=True,
                ),
            }
        )

    metrics = pd.DataFrame(rows)
    control_frame = pd.DataFrame(controls)
    decision = _decision(metrics, control_frame, config=config)
    output_value = args.output_directory or config["output_directory"]
    report_value = args.report_path or config["report_path"]
    output = ROOT / output_value
    output.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(output / "metrics.csv", index=False)
    control_frame.to_csv(output / "controls.csv", index=False)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True)
        handle.write("\n")
    report = ROOT / report_value
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(_report(decision, metrics), encoding="utf-8")
    print(json.dumps(decision, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
