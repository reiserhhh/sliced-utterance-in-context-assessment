from __future__ import annotations

from pathlib import Path

import numpy as np

from scripts.run_suica_v7_representation_transport import ROOT, _build_parser, _default_report_path
from suica_sim.v7_representation_transport import evaluate_transport_world, generate_transport_world, run_transport_matrix


def test_report_default_stays_out_of_tracked_reports_tree() -> None:
    args = _build_parser().parse_args([])
    # No implicit tracked-path default: the report path is resolved from the
    # (gitignored) results/ output directory unless passed explicitly.
    assert args.report is None
    output_dir = ROOT / "results" / "v7_representation_transport" / "some_run"
    default = _default_report_path(output_dir)
    assert default == output_dir / "V7_REPRESENTATION_TRANSPORT_CALIBRATION.md"
    assert (ROOT / "reports") not in default.parents
    report_action = next(action for action in _build_parser()._actions if "--report" in action.option_strings)
    assert "untracked" in (report_action.help or "")
    assert isinstance(default, Path)


def test_rotation_preserves_within_geometry_but_needs_paired_alignment() -> None:
    world = generate_transport_world("unknown_rotation", seed=10, persons=140, features=8, noise_scale=0.03, anchor_fraction=0.5)
    result = evaluate_transport_world(world)
    assert float(result["paired_relative_distance_spearman"]) > 0.95
    assert float(result["procrustes_retrieval_accuracy"]) > float(result["naive_retrieval_accuracy"])
    assert float(result["procrustes_coordinate_r2"]) > 0.8


def test_unpaired_isotropic_world_refuses_coordinate_transport() -> None:
    world = generate_transport_world("unpaired_isotropic_orientation_ambiguity", seed=11, persons=120, features=8, noise_scale=0.04, anchor_fraction=0.5)
    result = evaluate_transport_world(world)
    assert result["paired_available"] is False
    assert result["cross_domain_coordinate_status"] == "REFUSE_UNPAIRED_ORIENTATION_NOT_IDENTIFIED"
    assert np.isnan(float(result["naive_coordinate_r2"]))


def test_transport_matrix_runs_all_declared_worlds() -> None:
    rows = run_transport_matrix({
        "seed": 1,
        "repetitions": 2,
        "persons": 60,
        "features": 5,
        "noise_scale": 0.05,
        "anchor_fraction": 0.5,
        "worlds": ["common_coordinate", "unknown_rotation"],
    })
    assert len(rows) == 4
