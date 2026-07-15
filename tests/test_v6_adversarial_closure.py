from __future__ import annotations
import numpy as np
from suica_sim.adversarial_closure import (crossed_interaction_world,irregular_sampling_world,multiparty_world,
 nonlinear_timevarying_world,opportunity_error_world,sparse_coupling_world)
def test_irregular_time_uses_elapsed_time_and_refuses_mnar():
    r=irregular_sampling_world(np.random.default_rng(1),20);assert r["dt_aware_relative_error"]<r["naive_relative_error"];assert r["mnar_refusal_rate"]>.8
def test_opportunity_error_degrades_operator_recovery():
    r=opportunity_error_world(np.random.default_rng(2),20)["curve"];assert r[0]["operator_recovery_r"]>r[-1]["operator_recovery_r"]
def test_nonlinearity_and_time_change_need_explicit_bases():
    r=nonlinear_timevarying_world(np.random.default_rng(3),20);assert r["heldout_mse_gain"]>.05;assert r["time_change_recovery_rate"]>.7
def test_partner_input_and_identity_matter():
    r=multiparty_world(np.random.default_rng(4),20);assert r["partner_heldout_gain"]>.05;assert r["partner_permutation_loss"]>.05
def test_sparse_graph_recovers_support():
    r=sparse_coupling_world(np.random.default_rng(5),20);assert r["support_f1"]>.7;assert r["offdiag_fpr"]<.1
def test_crossed_actor_partner_roles_identify_author_response():
    r=crossed_interaction_world(np.random.default_rng(6),10);assert r["actor_operator_recovery_r"]>.8;assert r["own_vs_stranger_dyad_delta"]>.02;assert r["graph_support_rate"]==1
