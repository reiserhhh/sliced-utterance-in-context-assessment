#!/usr/bin/env python3
"""Freeze M4-C.3.5-R2 chart arms before response/truth opening."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_m4_response_safe_chart_replacement import (  # noqa: E402
    _alias_mechanism_conditions,
    _expanded_worlds,
    _load,
    _rcca_parameters,
    _shift_condition,
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
from suica_core.m4_response_safe_chart_replacement import (  # noqa: E402
    match_nonmass_trace,
    nonmass_rank_and_trace,
    repeatability_projected_basis,
    truncate_whitened_basis,
)
from suica_core.m4_response_safe_rcca_chart import (  # noqa: E402
    build_response_safe_rcca_basis,
    fit_response_safe_rcca_chart,
)


def _old_basis(transform: Any, condition: Any) -> dict[str, Any]:
    return {
        role: transform.transform_prototypes(
            getattr(condition, f"mechanism_{role}").pre_context
        )
        for role in ("calibration", "selection", "evaluation")
    }


def _chart_arms(
    condition: Any,
    *,
    config: dict[str, Any],
    candidates: tuple[dict[str, Any], ...],
    seed: int,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any], Any]:
    old_chart = fit_m4_condition_chart(
        condition,
        candidates=candidates,
        **config["chart_thresholds"],
    )
    old_transform = freeze_m4_condition_transform(
        condition,
        old_chart,
        rank_tolerance=float(config["rank_tolerance"]),
        maximum_rank=int(config["maximum_rank"]),
    )
    baseline = _old_basis(old_transform, condition)
    rcca = fit_response_safe_rcca_chart(
        condition,
        **_rcca_parameters(config, seed=seed),
    )
    rcca_basis = build_response_safe_rcca_basis(rcca, condition)
    variance = match_nonmass_trace(
        truncate_whitened_basis(baseline, rank=rcca.shared_rank),
        rcca_basis,
    )
    repeatability = match_nonmass_trace(
        repeatability_projected_basis(
            old_transform,
            condition,
            baseline,
            rank=rcca.shared_rank,
            author_blocks=int(config["rcca"]["author_blocks"]),
        ),
        rcca_basis,
    )
    bases = {
        "B0": baseline,
        "Br_var": variance,
        "Br_rep": repeatability,
        "R": rcca_basis,
    }
    stats = {
        arm: nonmass_rank_and_trace(values)
        for arm, values in bases.items()
        if arm != "B0"
    }
    trace_error = max(
        abs(stats[arm][role][1] - stats["R"][role][1])
        / max(stats["R"][role][1], 1e-12)
        for arm in ("Br_var", "Br_rep")
        for role in ("calibration", "selection", "evaluation")
    )
    rank_contract = all(
        stats[arm][role][0] == rcca.shared_rank
        for arm in ("Br_var", "Br_rep", "R")
        for role in ("calibration", "selection", "evaluation")
    )
    metadata = {
        "old_rank": old_transform.effective_rank,
        "rcca_support_ranks": list(rcca.support_ranks),
        "rcca_shared_rank_lower": rcca.shared_rank_lower,
        "rcca_shared_rank_upper": rcca.shared_rank_upper,
        "rcca_shared_rank": rcca.shared_rank,
        "rcca_spectral_blocks": [list(value) for value in rcca.spectral_blocks],
        "rcca_refused": rcca.refused,
        "rcca_refusal_reasons": list(rcca.refusal_reasons),
        "basis_contract_passed": bool(
            rank_contract and trace_error <= 1e-10
        ),
        "basis_trace_error": trace_error,
    }
    return bases, metadata, rcca


def _pre_response_condition(
    *,
    world: str,
    spec: M4ChartEcologySpec,
    seed: int,
) -> Any:
    return generate_m4_pre_response_condition(
        world=world,
        spec=spec,
        seed=seed,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=(
            ROOT / "configs" / "m4_response_safe_chart_replacement.development.json"
        ),
    )
    parser.add_argument("--repetition-limit", type=int)
    parser.add_argument("--repetition-start", type=int, default=0)
    parser.add_argument("--output-directory")
    args = parser.parse_args()
    config = _load(args.config)
    if args.repetition_limit is not None:
        config["repetitions"] = int(args.repetition_limit)
    bundle_root = Path(
        args.output_directory
        or config.get(
            "chart_bundle_directory",
            "results/m4_response_safe_chart_replacement_chart_bundles",
        )
    )
    if not bundle_root.is_absolute():
        bundle_root = ROOT / bundle_root
    bundle_root.mkdir(parents=True, exist_ok=True)

    r1_path = ROOT / config.get(
        "r1_decision_path",
        "results/m4_response_safe_rcca_chart_confirmation/decision.json",
    )
    r1 = _load(r1_path)
    if r1["decision"] != "M4_C35_R1_CONFIRMATION_GO":
        raise ValueError("R1 confirmation GO is required before R2 charts")

    spec = M4ChartEcologySpec(**config["spec"])
    candidates = tuple(dict(value) for value in config["chart_candidates"])
    worlds = _expanded_worlds(config)
    cells = []
    support_controls = []
    alias_cells = []
    start = int(args.repetition_start)
    stop = start + int(config["repetitions"])
    for repetition in range(start, stop):
        for world_index, (world_type, generator_world, label) in enumerate(
            worlds
        ):
            seed = int(
                config["seed"]
                + repetition * 1_000_003
                + world_index * 10_003
            )
            condition = _pre_response_condition(
                world=generator_world,
                spec=spec,
                seed=seed,
            )
            bases, metadata, rcca = _chart_arms(
                condition,
                config=config,
                candidates=candidates,
                seed=seed,
            )
            extra = {}
            if world_index == 0:
                shifted = _shift_condition(condition, value=23.75)
                shifted_chart = fit_response_safe_rcca_chart(
                    shifted,
                    **_rcca_parameters(config, seed=seed),
                )
                extra["R_shifted"] = build_response_safe_rcca_basis(
                    shifted_chart,
                    shifted,
                )
            if world_type == "main":
                shuffled = fit_response_safe_rcca_chart(
                    condition,
                    shuffle_source_two=True,
                    **_rcca_parameters(config, seed=seed + 500_009),
                )
                metadata["source_shuffle_passed"] = bool(
                    shuffled.shared_rank_lower == 0 or shuffled.refused
                )
                metadata["source_shuffle_rank_lower"] = (
                    shuffled.shared_rank_lower
                )
                metadata["source_shuffle_reasons"] = list(
                    shuffled.refusal_reasons
                )
            bundle_name = f"rep_{repetition:02d}__{label}.npz"
            bundle_path = bundle_root / bundle_name
            bundle_hash = write_basis_bundle(
                bundle_path,
                bases,
                extra_bases=extra,
            )
            cells.append(
                {
                    "repetition": repetition,
                    "world_type": world_type,
                    "generator_world": generator_world,
                    "world": label,
                    "seed": seed,
                    "pre_response_digest": pre_response_digest(condition),
                    "bundle": bundle_name,
                    "bundle_sha256": bundle_hash,
                    **metadata,
                }
            )

        support_seed = int(
            config["seed"] + repetition * 1_000_003 + 80_000_009
        )
        support = _pre_response_condition(
            world="evaluation_support_shift",
            spec=spec,
            seed=support_seed,
        )
        support_chart = fit_response_safe_rcca_chart(
            support,
            **_rcca_parameters(config, seed=support_seed),
        )
        support_controls.append(
            {
                "repetition": repetition,
                "seed": support_seed,
                "refused": support_chart.refused,
                "refusal_reasons": list(support_chart.refusal_reasons),
            }
        )

        alias_seed = int(
            config["seed"] + repetition * 1_000_003 + 90_000_011
        )
        alias = _pre_response_condition(
            world="condition_alias_ecology",
            spec=spec,
            seed=alias_seed,
        )
        alias = _alias_mechanism_conditions(alias)
        alias_bases, alias_metadata, _ = _chart_arms(
            alias,
            config=config,
            candidates=candidates,
            seed=alias_seed,
        )
        alias_name = f"rep_{repetition:02d}__latent_alias.npz"
        alias_path = bundle_root / alias_name
        alias_hash = write_basis_bundle(alias_path, alias_bases)
        alias_cells.append(
            {
                "repetition": repetition,
                "seed": alias_seed,
                "pre_response_digest": pre_response_digest(alias),
                "bundle": alias_name,
                "bundle_sha256": alias_hash,
                **alias_metadata,
            }
        )

    source_paths = list((ROOT / "suica_core").glob("*.py"))
    source_paths.extend(
        [
            ROOT / "scripts" / "prepare_suica_m4_response_safe_chart_replacement.py",
            ROOT / "scripts" / "run_suica_m4_response_safe_chart_replacement.py",
            ROOT / "scripts" / "run_suica_m4_response_safe_chart_replacement_sealed.py",
            ROOT / "scripts" / "aggregate_suica_m4_response_safe_chart_replacement.py",
        ]
    )
    protocol_value = config.get("protocol_path")
    protocol_path = ROOT / protocol_value if protocol_value else None
    if protocol_path is not None and not protocol_path.is_file():
        raise ValueError(f"protocol does not exist: {protocol_value}")
    manifest = {
        "version": "suica-m4-c35-r2-pre-response-chart-manifest-v1",
        "config_path": str(args.config),
        "config_sha256": file_sha256(args.config),
        "r1_decision_path": str(r1_path.relative_to(ROOT)),
        "r1_decision_sha256": file_sha256(r1_path),
        "r1_decision": r1["decision"],
        "protocol_path": protocol_value,
        "protocol_sha256": (
            file_sha256(protocol_path)
            if protocol_path is not None
            else None
        ),
        "repetition_start": start,
        "repetition_stop": stop,
        "source_sha256": source_hash_manifest(ROOT, source_paths),
        "runtime": runtime_fingerprint(),
        "cells": cells,
        "support_controls": support_controls,
        "alias_cells": alias_cells,
        "boundary": (
            "Only sanitized pre-response condition tensors were exposed to "
            "chart estimators. No ecology, mechanism endpoint, author truth, "
            "or oracle basis is serialized in this manifest."
        ),
    }
    manifest_path = bundle_root / "stage_a_manifest.json"
    with manifest_path.open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(
        json.dumps(
            {
                "manifest": str(manifest_path),
                "manifest_sha256": file_sha256(manifest_path),
                "cells": len(cells),
                "alias_cells": len(alias_cells),
                "support_controls": len(support_controls),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
