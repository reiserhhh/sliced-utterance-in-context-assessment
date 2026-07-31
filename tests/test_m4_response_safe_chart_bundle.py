"""Tests for the pre-response chart serialization boundary."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from suica_core.m4_chart_ecology_generator import (
    M4ChartEcologySpec,
    generate_m4_chart_ecology_world,
    generate_m4_pre_response_condition,
)
from suica_core.m4_response_safe_chart_bundle import (
    pre_response_digest,
    read_basis_bundle,
    sanitize_pre_response,
    source_hash_manifest,
    verify_source_hash_manifest,
    write_basis_bundle,
)


def test_basis_bundle_hash_is_verified(tmp_path: Path) -> None:
    rng = np.random.default_rng(83)
    bases = {
        arm: {
            role: rng.normal(size=(16, 7))
            for role in ("calibration", "selection", "evaluation")
        }
        for arm in ("B0", "R")
    }
    path = tmp_path / "bundle.npz"
    digest = write_basis_bundle(path, bases)
    loaded = read_basis_bundle(path, expected_sha256=digest)
    assert np.array_equal(
        loaded["R"]["evaluation"],
        bases["R"]["evaluation"],
    )
    with pytest.raises(ValueError, match="hash mismatch"):
        read_basis_bundle(path, expected_sha256="0" * 64)


@pytest.mark.parametrize(
    "world",
    [
        "endogenous_creation_expansion",
        "endogenous_source_partition_matched",
        "source_rotated_feedback",
        "history_gated_ecology",
        "selection_creation_compensation",
        "linear_null_ecology",
        "evaluation_support_shift",
        "condition_alias_ecology",
    ],
)
def test_pre_response_generator_exactly_replays_full_world(
    world: str,
) -> None:
    spec = M4ChartEcologySpec(
        reference_authors=8,
        mechanism_authors=8,
        reference_calibration_points=16,
        reference_selection_points=16,
        categories=16,
        events=24,
    )
    pre_response = generate_m4_pre_response_condition(
        world=world,
        spec=spec,
        seed=91_003,
    )
    full, _ = generate_m4_chart_ecology_world(
        world=world,
        spec=spec,
        seed=91_003,
    )
    assert pre_response_digest(pre_response) == pre_response_digest(
        sanitize_pre_response(full.condition)
    )


def test_pre_response_generator_refuses_response_leakage_world() -> None:
    with pytest.raises(ValueError, match="no response-safe"):
        generate_m4_pre_response_condition(
            world="response_leakage_circular",
            spec=M4ChartEcologySpec(),
            seed=17,
        )


def test_source_manifest_detects_post_seal_change(tmp_path: Path) -> None:
    source = tmp_path / "source.py"
    source.write_text("value = 1\n", encoding="utf-8")
    manifest = source_hash_manifest(tmp_path, [source])
    verify_source_hash_manifest(tmp_path, manifest)
    source.write_text("value = 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sealed source changed"):
        verify_source_hash_manifest(tmp_path, manifest)
