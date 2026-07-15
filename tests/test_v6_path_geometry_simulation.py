from __future__ import annotations

from suica_sim.path_geometry import PhaseCoupledSpec, evaluate_phase_coupled_world


def test_nonlinear_phase_witness_recovers_planted_author_configuration() -> None:
    result = evaluate_phase_coupled_world(
        PhaseCoupledSpec(n_authors=40, runs_per_half=4, points_per_run=20, kappa=8.0), seed=12
    )
    assert result["conditional_phase_witness_auc"] > 0.9
    assert result["linear_summary_auc"] < 0.65
    assert result["shuffled_phase_witness_auc"] < 0.65
