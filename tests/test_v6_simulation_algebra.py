from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim.algebra import (conditional_innovation, endpoint_flow_variance,
                               stationary_mean_variance, three_point_mixed_moments)
from suica_sim.matrix import load_config, run_matrix
from suica_sim.worlds import (CRITERIA, flow_bonferroni_interval,
                              flow_parametric_bootstrap_interval,
                              flow_standard_error, m3_equivalent_samples,
                              opportunity_identifiable, recover_response)


def test_t1_stationary_mean_identity_matches_covariance_sum():
    gamma = np.array([1.0, 0.5, 0.25, 0.125])
    covariance = np.fromfunction(lambda i, j: gamma[np.abs(i-j).astype(int)], (4, 4))
    expected = np.ones(4) @ covariance @ np.ones(4) / 16
    assert stationary_mean_variance(gamma, 4) == expected


def test_t2_endpoint_and_three_point_identities():
    flow = np.array([[0.4]])
    gamma = np.array([[[1.0]], [[0.2]], [[0.1]]])
    assert np.allclose(endpoint_flow_variance(flow, gamma[0], gamma[2], 3), [[0.85]])
    ell, q, cross = three_point_mixed_moments(flow, gamma)
    assert np.allclose(ell, [[0.85]])
    assert np.allclose(q, [[23 / 30]])
    assert np.allclose(cross, 0)


def test_t8_schur_complement_conditional_rank():
    schur0, rank0 = conditional_innovation(np.array([[1., 1.], [1., 1.]]), [0], [1])
    schur1, rank1 = conditional_innovation(np.array([[1., .4], [.4, 1.]]), [0], [1])
    assert np.allclose(schur0, 0) and rank0 == 0
    assert rank1 == 1 and np.allclose(schur1, [[0.84]])


def test_m3_observational_equivalence_and_guard():
    a, b = m3_equivalent_samples(np.random.default_rng(4), 100_000)
    assert abs(a.var() - b.var()) < .02
    assert abs(a.mean() - b.mean()) < .02


def test_flow_standard_error_contains_both_independent_variance_terms():
    v_s, v_delta, n, m = .7, 1.2, 160, 5
    expected = np.sqrt(2*v_s**2/(n-1) + 2*(v_delta/(m-1)**2)**2/(n-1))
    assert flow_standard_error(v_s, v_delta, n, m) == expected
    slope_only = np.sqrt(2*v_s**2/(n-1))
    assert flow_standard_error(v_s, v_delta, n, m) > slope_only
    lo, hi = flow_bonferroni_interval(v_s, v_delta, n, m)
    assert lo < v_s-v_delta/(m-1)**2 < hi
    assert hi-lo > 2*1.96*slope_only


def test_flow_parametric_bootstrap_interval_is_ordered_and_reproducible():
    first = flow_parametric_bootstrap_interval(
        np.random.default_rng(91), .44, 1.2, 500, 5, 999)
    second = flow_parametric_bootstrap_interval(
        np.random.default_rng(91), .44, 1.2, 500, 5, 999)
    assert first == second
    assert first[0] < .44 - 1.2 / 16 < first[1]


def test_opportunity_nonidentifiability_and_positivity():
    assert opportunity_identifiable(False) is False
    assert opportunity_identifiable(True) is True


def test_response_operator_recovery_and_rank_guard():
    rng = np.random.default_rng(14)
    truth = np.array([[1.2, -0.3], [0.4, 0.8]])
    x = rng.standard_normal((200, 2)); y = x @ truth.T
    recovered, condition = recover_response(x, y)
    assert condition < 2 and np.allclose(recovered.T, truth)
    deficient = np.column_stack([x[:, 0], 2 * x[:, 0]])
    _, deficient_condition = recover_response(deficient, deficient @ truth.T)
    assert deficient_condition > 1e12


def test_matrix_fixed_seed_and_m3_guard():
    config, digest = load_config(ROOT / "configs/sim_v6/quick.json")
    first = run_matrix(config, digest)
    second = run_matrix(config, digest)
    assert first == second
    m3 = next(r for r in first["rows"] if r["world"] == "SIM-W3" and r["scenario"] == "m3_observational_equivalence")
    assert m3["metric_type"] == "classification_auc"
    assert m3["criterion_id"] == "auc_55"


def test_schema_and_verdicts_are_evaluator_derived():
    config, digest = load_config(ROOT / "configs/sim_v6/quick.json")
    result = run_matrix(config, digest)
    required = {"metric_type", "estimate", "truth", "bias", "mc_ci_low", "mc_ci_high",
                "ci_coverage", "fpr", "power", "guard_rate", "criterion_id", "theory_targets", "verdict"}
    assert all(required <= row.keys() for row in result["rows"])
    assert all(row["world"].startswith("SIM-W") for row in result["rows"])
    assert all(row["verdict"] == ("pass" if CRITERIA[row["criterion_id"]](row) else "fail") for row in result["rows"])
    assert all(len(row["theory_targets"]) == 1 for row in result["rows"])
    assert {"code_hash", "git_head", "python_version", "numpy_version"} <= result.keys()
    decay_nulls = [row for row in result["rows"] if row["world"] == "SIM-W2" and row["metric_type"] == "decay_guard_fpr"]
    assert {row["scenario"] for row in decay_nulls} == {"short_memory_iid", "short_memory_ar06"}
    assert all(row["fpr"] is not None and row["criterion_id"] == "fpr_10" for row in decay_nulls)
    coverage_rows = [row for row in result["rows"] if row["metric_type"] == "ci_coverage"]
    assert all(0 <= row["mc_ci_low"] <= row["estimate"] <= row["mc_ci_high"] <= 1 for row in coverage_rows)
    assert all(row["criterion_id"] == "coverage_nominal_95" for row in coverage_rows)


def test_core_code_hash_excludes_unrelated_simulation_modules(tmp_path):
    config, digest = load_config(ROOT / "configs/sim_v6/quick.json")
    before = run_matrix(config, digest)["code_hash"]
    unrelated = ROOT / "suica_sim/_temporary_unrelated_module.py"
    unrelated.write_text("VALUE = 1\n")
    try:
        after = run_matrix(config, digest)["code_hash"]
    finally:
        unrelated.unlink()
    assert before == after


def test_w6_has_no_period_oracle_and_w8_boundary_is_guarded():
    config, digest = load_config(ROOT / "configs/sim_v6/quick.json")
    rows = run_matrix(config, digest)["rows"]
    w6 = [row for row in rows if row["world"] == "SIM-W6"]
    assert all(row["metric_type"] != "alias_guard_rate" for row in w6)
    assert all("period" not in row["scenario"] for row in w6)
    alias = next(row for row in w6 if row["scenario"] == "above_Nyquist_alias_equivalence")
    assert alias["metric_type"] == "classification_auc" and alias["criterion_id"] == "auc_55"
    boundary = [row for row in rows if row["world"] == "SIM-W8" and row["metric_type"] == "innovation_boundary_guard_rate"]
    guarded = {row["scenario"] for row in boundary if row["guard_rate"] is not None}
    assert guarded == {"innovation_eigen_0.08", "innovation_eigen_0.12", "innovation_eigen_0.18"}


def test_quick_runner_smoke(tmp_path):
    proc = subprocess.run([sys.executable, str(ROOT / "scripts/run_v6_simulation_matrix.py"),
                           "--profile", "quick", "--output-dir", str(tmp_path)],
                          check=True, capture_output=True, text=True)
    payload = json.loads(proc.stdout)
    assert payload["rows"] >= 18
    for path in payload["outputs"].values():
        assert Path(path).is_file()
