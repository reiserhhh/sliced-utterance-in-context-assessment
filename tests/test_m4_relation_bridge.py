"""Tests for the M4-D leg-2 relation-to-individual bridge.

Substantive coverage per the leg plan: planted-truth recovery (low-noise
individual worlds must be licensed and recovered), group-only refusal (the
vanishing-individuality trap must be refused despite high author AUC, for
both the pairwise analogue and the actual C2-machinery fields), gauge
invariance of the aligned error, and the spectral rank/noise-floor logic.
"""
from __future__ import annotations

import numpy as np
import pytest

from suica_core.m4_relation_bridge import (
    RelationBridgeConfig,
    c2_machinery_relation_world,
    classical_mds,
    evaluate_relation_world,
    gauge_aligned_error,
    gram_from_relation,
    planted_relation_world,
    reconstruction_vs_truth,
    relation_field_author_auc,
    rigidity_report,
    spectral_profile,
    squared_distance_field,
)

CONFIG = RelationBridgeConfig()


def test_planted_truth_recovery_low_noise():
    world = planted_relation_world("individual", noise=0.05, seed=101)
    record = evaluate_relation_world(world, config=CONFIG, seed=7)
    assert record["rigidity_status"] == "R_TO_V_LICENSED"
    assert record["rigidity_selected_rank"] == 3
    assert record["rigidity_rigidity_index"] > 0.7
    assert record["e_rec_oracle"] < 0.10
    assert record["gt_reconstructable"] is True or bool(
        record["gt_reconstructable"]
    )


def test_group_only_refusal_despite_high_author_auc():
    """The vanishing-individuality trap: high author AUC, zero individual
    structure -- the index must refuse and the truth label must be
    non-reconstructable by permutation invariance."""
    world = planted_relation_world("group_only", noise=0.1, seed=202)
    record = evaluate_relation_world(world, config=CONFIG, seed=7)
    assert record["rigidity_status"] == "R_TO_V_REFUSED"
    assert record["rigidity_rigidity_index"] < 0.35
    assert record["author_all_auc"] > 0.75
    assert abs(record["author_within_group_auc"] - 0.5) < 0.15
    assert not record["gt_reconstructable"]
    assert record["e_ratio_oracle"] == pytest.approx(1.0, abs=0.05)


def test_c2_machinery_group_only_refusal():
    """Fields built from the actual v8_vanishing_individuality simulator
    (empirical-logit, condition-centered halves) must also be refused."""
    world = c2_machinery_relation_world("group_only", seed=11)
    record = evaluate_relation_world(world, config=CONFIG, seed=3)
    assert record["rigidity_status"] == "R_TO_V_REFUSED"
    assert record["rigidity_rigidity_index"] < 0.1
    assert record["author_all_auc"] > 0.75
    assert record["individual_share"] == pytest.approx(0.0, abs=1e-9)
    assert not record["gt_reconstructable"]


def test_high_noise_world_is_refused_and_unreconstructable():
    world = planted_relation_world("individual", noise=2.5, seed=303)
    record = evaluate_relation_world(world, config=CONFIG, seed=7)
    assert record["rigidity_status"] == "R_TO_V_REFUSED"
    assert not record["gt_reconstructable"]


def test_gauge_invariance_of_aligned_error():
    """Rotation + reflection + translation + scale of the truth must not
    change the gauge-aligned reconstruction error."""
    rng = np.random.default_rng(5)
    world = planted_relation_world("individual", noise=0.1, seed=404)
    truth = world["truth"]
    gram = gram_from_relation(world["fields"][0])
    embedding = classical_mds(gram, 3)
    base_error = gauge_aligned_error(embedding, truth)
    rotation = np.linalg.qr(rng.normal(size=(3, 3)))[0]
    transformed = 1.7 * truth @ rotation + rng.normal(size=(1, 3))
    moved_error = gauge_aligned_error(embedding, transformed)
    assert moved_error == pytest.approx(base_error, abs=1e-8)


def test_spectral_profile_selects_planted_rank():
    world = planted_relation_world("individual", noise=0.0, seed=505)
    profile = spectral_profile(gram_from_relation(world["fields"][0]))
    assert profile["selected_rank"] == 3
    assert profile["spectral_margin"] > 0.99
    report = rigidity_report(world["fields"][0], config=CONFIG, seed=1)
    assert report["status"] == "R_TO_V_LICENSED"


def test_group_only_permutation_invariance_of_label():
    """Within-block permutation leaves group-only truth invariant, so the
    reconstruction can never beat the permuted baseline."""
    world = planted_relation_world("group_only", noise=0.05, seed=606)
    outcome = reconstruction_vs_truth(
        world["fields"][0],
        world["truth"],
        rank=3,
        group_labels=world["group_labels"],
        config=CONFIG,
        seed=9,
    )
    assert outcome["error_ratio"] == pytest.approx(1.0, abs=1e-6)
    assert not outcome["reconstructable"]


def test_similarity_kind_matches_squared_distance():
    rng = np.random.default_rng(6)
    points = rng.normal(size=(30, 3))
    similarity = points @ points.T
    from_similarity = gram_from_relation(similarity, kind="similarity")
    from_distance = gram_from_relation(
        squared_distance_field(points),
        kind="squared_distance",
    )
    assert np.allclose(from_similarity, from_distance, atol=1e-8)


def test_author_auc_without_labels():
    world = planted_relation_world("individual", noise=0.1, seed=707)
    metrics = relation_field_author_auc(
        world["fields"][0],
        world["fields"][1],
        None,
    )
    assert metrics["author_all_auc"] > 0.9
    assert np.isnan(metrics["author_within_group_auc"])
