"""Tests for the M4 noncommuting transition-kernel experiment."""
from __future__ import annotations

import numpy as np

from suica_core.m4_dynamic_kernel_audit import audit_m4_dynamic_kernel
from suica_core.m4_dynamic_kernel_estimator import fit_m4_dynamic_kernel
from suica_core.m4_dynamic_kernel_generator import (
    M4DynamicKernelSpec,
    generate_m4_dynamic_kernel_world,
)


def _run(world: str, seed: int) -> dict[str, object]:
    observed, truth = generate_m4_dynamic_kernel_world(
        world=world,
        spec=M4DynamicKernelSpec(
            authors=14,
            occasions=4,
            events=120,
            noise=0.045,
        ),
        seed=seed,
    )
    estimate = fit_m4_dynamic_kernel(
        observed,
        minimum_calibration_events=8,
    )
    return audit_m4_dynamic_kernel(
        estimate,
        truth,
        minimum_order_margin=0.02,
        minimum_resolvable_commutator=0.04,
        maximum_commuting_commutator=0.08,
    )


def test_dynamic_generator_is_reproducible() -> None:
    spec = M4DynamicKernelSpec(
        authors=10,
        occasions=3,
        events=96,
    )
    first, truth = generate_m4_dynamic_kernel_world(
        world="noncommuting_forward_gate",
        spec=spec,
        seed=901,
    )
    second, repeated_truth = generate_m4_dynamic_kernel_world(
        world="noncommuting_forward_gate",
        spec=spec,
        seed=901,
    )
    assert np.allclose(first.post_train, second.post_train)
    assert np.allclose(
        truth.author_parameters["commutator"],
        repeated_truth.author_parameters["commutator"],
    )


def test_forward_and_reverse_kernel_orders_are_recovered() -> None:
    forward = _run("noncommuting_forward_gate", 911)
    reverse = _run("noncommuting_reverse_gate", 912)
    assert forward["order_accuracy"] >= 0.75
    assert reverse["order_accuracy"] >= 0.75
    assert forward["mean_order_margin"] > 0.0
    assert reverse["mean_order_margin"] < 0.0


def test_gate_direction_and_path_score_are_positive() -> None:
    result = _run("noncommuting_forward_gate", 921)
    assert result["mean_gate_h_to_c"] > result["mean_gate_c_to_h"]
    assert result["mean_gate_direction_margin"] > 0.20
    assert result["mean_path_logscore_gain"] > 0.0


def test_commuting_and_alias_controls_are_distinguished() -> None:
    commuting = _run("commuting_null", 931)
    alias = _run("gate_role_alias", 932)
    assert commuting["commuting_control_pass"] is True
    assert alias["alias_refused"] is True
    assert alias["refusal_rate"] >= 0.80
