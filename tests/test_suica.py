from __future__ import annotations

import json
import math

import pandas as pd

from scripts.build_suica_policy_profile_scorer_v1 import build_profiles, entropy_norm
from scripts.build_suica_blind_construct_coding_package_v1 import (
    build_blind_items,
    build_alignment_summary,
    full_pole_anchor_contrast,
    select_extreme_examples,
    stable_text_hash,
)
from scripts.build_suica_rebalanced_repair_package_v1 import (
    build_repair_blind_items,
    select_within_source_pole,
    source_balance_summary,
    source_pole_counts,
)
from scripts.build_suica_independent_blind_validation_batch_v1 import (
    build_coder_order,
    build_factor_manifest,
    build_independent_blind_items,
    mask_personality_terms,
    select_formal_examples,
)
from scripts.run_suica_independent_llm_coder_v1 import (
    build_request_record,
    parse_llm_ratings_response,
)
from scripts.summarize_suica_independent_blind_validation_v1 import (
    agreement_summary,
    factor_acceptance_summary,
)
from scripts.build_suica_construct_candidate_manual_v1 import (
    build_dimension_contrast,
    build_repair_queue,
    evidence_tier,
)
from scripts.diagnose_suica_weak_factors_v1 import (
    DIMENSIONS,
    dimension_repair_diagnostics,
    factor_repair_plan,
    item_disagreement_diagnostics,
)
from scripts.evaluate_suica_repair_candidates_v1 import (
    CandidateSpec,
    candidate_agreement,
    candidate_coder_metrics,
    candidate_component_diagnostics,
    candidate_overlap,
    score_candidate_rows,
    summarize_candidates,
)
from scripts.build_suica_repair_candidate_blind_batch_v1 import (
    formal_feasibility,
    select_candidate_examples,
    source_pole_counts as repair_candidate_source_pole_counts,
)
from scripts.evaluate_suica_repair_candidate_llm_coding_v1 import (
    candidate_acceptance as repair_candidate_acceptance,
    expected_gate as repair_candidate_expected_gate,
    source_adjusted_delta as repair_candidate_source_adjusted_delta,
)
from scripts.analyze_suica_action_growth_revision_v1 import (
    source_adjusted_virtual_gate as action_growth_virtual_gate,
    virtual_summary as action_growth_virtual_summary,
)
from scripts.build_suica_action_growth_2x2_batch_v1 import (
    add_selection_scores as add_action_growth_2x2_selection_scores,
    prepare_anchor_frame as prepare_action_growth_2x2_anchor_frame,
    select_2x2_examples as select_action_growth_2x2_examples,
)
from scripts.evaluate_suica_action_growth_2x2_coding_v1 import (
    acceptance_summary as action_growth_2x2_acceptance_summary,
    add_fused_scores as add_action_growth_2x2_fused_scores,
    interaction_effects as action_growth_2x2_interaction_effects,
    source_adjusted_marginals as action_growth_2x2_source_adjusted_marginals,
)
from scripts.build_suica_construct_expansion_readiness_v1 import (
    CONSTRUCT_SPECS as EXPANSION_CONSTRUCT_SPECS,
    add_construct_scores as add_suica_expansion_construct_scores,
    assign_author_split as assign_suica_expansion_author_split,
    build_blind_package as build_suica_expansion_blind_package,
    prepare_anchor_frame as prepare_suica_expansion_anchor_frame,
    readiness_summary as suica_expansion_readiness_summary,
    select_expanded_item_bank,
    source_family_from_scenario as suica_expansion_source_family,
)
from scripts.evaluate_suica_construct_expansion_coding_v1 import (
    acceptance_summary as suica_expansion_acceptance_summary,
    add_fused_scores as add_suica_expansion_fused_scores,
    interaction_effects as suica_expansion_interaction_effects,
    interaction_source_adjusted_marginals as suica_expansion_interaction_marginals,
    pole_expected_gate as suica_expansion_pole_expected_gate,
    pole_separation as suica_expansion_pole_separation,
    pole_source_adjusted as suica_expansion_pole_source_adjusted,
)
from scripts.build_suica_directive_growth_coupled_repair_v1 import (
    add_quantiles_and_cells as add_directive_growth_coupled_cells,
    coupling_features as directive_growth_coupling_features,
    prepare_frame as prepare_directive_growth_coupled_frame,
    select_items as select_directive_growth_coupled_items,
)
from scripts.build_suica_directive_growth_strict_repair_v2 import (
    add_quantiles_and_cells as add_directive_growth_strict_cells,
    prepare_frame as prepare_directive_growth_strict_frame,
    select_items as select_directive_growth_strict_items,
    strict_coupling_features as directive_growth_strict_coupling_features,
)
from scripts.build_suica_adversity_recovery_core_v1 import (
    add_scores_and_poles as add_adversity_recovery_scores,
    adversity_recovery_features,
    prepare_frame as prepare_adversity_recovery_frame,
    select_items as select_adversity_recovery_items,
)
from scripts.build_suica_three_construct_reliability_package_v1 import readiness_summary as three_construct_readiness_summary
from scripts.build_suica_validated_construct_manual_v1 import CONSTRUCTS as VALIDATED_MANUAL_CONSTRUCTS
from scripts.build_suica_selective_condition_policy_v3 import choose_policy
from scripts.audit_suica_factor_repair_v1 import build_repair_decisions, classify_factor
from scripts.evaluate_suica_blind_construct_coding_v1 import (
    build_auto_control,
    evaluate_pole_separation,
    expected_dimension_summary,
    expected_source_adjusted_summary,
    inter_coder_agreement,
    source_adjusted_pole_effects,
)
from scripts.run_suica_choice_module_redesign_v1 import choice_shape_features, condition_distribution, distance_auc
from scripts.run_suica_external_anchor_validation_v1 import benjamini_hochberg, safe_corr as external_safe_corr
from scripts.run_suica_narrative_projective_anchor_validation_v2 import (
    aggregate_user_anchor_profiles,
    build_slice_anchor_frame,
    score_text_anchors,
)
from scripts.run_suica_profile_stability_validation_v1 import auc_probability, row_metrics
from suica_core.suica import (
    BIG5_TRAITS,
    MBTI_AXES,
    SuicaFactorConfig,
    SuicaSliceConfig,
    build_slices,
    build_slices_for_strategy,
    run_factor_method,
    summarize_run,
)


def synthetic_users(n: int = 20) -> pd.DataFrame:
    rows = []
    for idx in range(n):
        fold = idx % 5
        theme = "creative future design novelty" if idx % 2 else "routine careful schedule order"
        affect = "calm reflective supportive" if idx % 3 else "urgent worried intense"
        text = " ".join([theme, affect, "personal story response choice"] * 12)
        row = {
            "user_id": f"u{idx:03d}",
            "text": text,
            "official_fold": fold,
        }
        for trait_i, trait in enumerate(BIG5_TRAITS):
            row[trait] = float(((idx + trait_i) % n) / max(1, n - 1))
        rows.append(row)
    return pd.DataFrame(rows)


def synthetic_bridge(users: pd.DataFrame) -> pd.DataFrame:
    bridge = users[["user_id"]].copy()
    for axis_i, axis in enumerate(MBTI_AXES):
        bridge[axis] = [float((idx + axis_i) % 2) for idx in range(len(bridge))]
    return bridge


def synthetic_suica_anchor_rows() -> pd.DataFrame:
    rows = []
    for source in ["pandora", "essays"]:
        scenario = f"{source}_temporal"
        for user_idx in range(24):
            for cell_idx, (directive, growth, novelty) in enumerate(
                [
                    (10.0, 10.0, 9.0),
                    (10.0, 0.0, 8.0),
                    (0.0, 10.0, 2.0),
                    (0.0, 0.0, 1.0),
                ]
            ):
                rows.append(
                    {
                        "scenario": scenario,
                        "user_id": f"{source}_u{user_idx:03d}",
                        "condition": f"c{cell_idx}",
                        "slice_obs_id": f"{source}_{user_idx}_{cell_idx}",
                        "slice_index": cell_idx,
                        "token_count": 64,
                        "slice_text": " ".join(
                            [
                                source,
                                "directive" if directive else "observing",
                                "growth" if growth else "static",
                                "novel playful" if novelty > 5 else "ordinary routine",
                                f"user{user_idx}",
                                f"cell{cell_idx}",
                            ]
                            * 12
                        ),
                        "novelty_play_rate": novelty,
                        "directive_interpersonal_blend": directive,
                        "directive_rate": directive / 2.0,
                        "agency_rate": directive / 3.0,
                        "redemption_growth_rate": growth,
                    }
                )
    return pd.DataFrame(rows)


def synthetic_directive_growth_coupled_rows() -> pd.DataFrame:
    texts = {
        "directive_growth": "You should try to learn from this and get better. Make sure you work through it.",
        "directive_only": "You should try this method now. Make sure you do the task clearly.",
        "growth_only": "I learned from the problem and got better after working through it.",
        "low_both": "The room was quiet and the table was near the window.",
    }
    signals = {
        "directive_growth": (10.0, 10.0),
        "directive_only": (10.0, 0.0),
        "growth_only": (0.0, 10.0),
        "low_both": (0.0, 0.0),
    }
    rows = []
    for source in ["pandora", "essays"]:
        for user_idx in range(12):
            for cell_idx, cell in enumerate(["directive_growth", "directive_only", "growth_only", "low_both"]):
                directive, growth = signals[cell]
                rows.append(
                    {
                        "scenario": f"{source}_temporal",
                        "user_id": f"{source}_dg_u{user_idx:03d}",
                        "condition": f"c{cell_idx}",
                        "slice_obs_id": f"{source}_dg_{user_idx}_{cell}",
                        "slice_index": cell_idx,
                        "token_count": 72,
                        "slice_text": " ".join([texts[cell], f"unique {source} user {user_idx} cell {cell}."] * 4),
                        "directive_interpersonal_blend": directive,
                        "redemption_growth_rate": growth,
                    }
                )
    return pd.DataFrame(rows)


def synthetic_directive_growth_strict_rows() -> pd.DataFrame:
    texts = {
        "directive_growth": (
            "You should work through the pain and learn from your mistakes. "
            "Try to heal after the problem and become a better person."
        ),
        "directive_only": (
            "You should study for the test and prepare the assignment. "
            "Make sure you follow the textbook and finish the homework."
        ),
        "growth_only": (
            "I worked through the trauma and recovered from the painful mistake. "
            "The struggle changed myself into a better person."
        ),
        "low_both": (
            "The room was quiet near the window while the table stayed beside the chair. "
            "People watched the afternoon light without giving advice."
        ),
    }
    signals = {
        "directive_growth": (10.0, 10.0),
        "directive_only": (10.0, 0.0),
        "growth_only": (0.0, 10.0),
        "low_both": (0.0, 0.0),
    }
    rows = []
    for source in ["pandora", "essays"]:
        for user_idx in range(16):
            for cell_idx, cell in enumerate(["directive_growth", "directive_only", "growth_only", "low_both"]):
                directive, growth = signals[cell]
                filler = (
                    f"unique {source} user {user_idx} cell {cell} "
                    "memory context response narrative detail reflection"
                )
                rows.append(
                    {
                        "scenario": f"{source}_temporal",
                        "user_id": f"{source}_dgs_u{user_idx:03d}",
                        "condition": f"c{cell_idx}",
                        "slice_obs_id": f"{source}_dgs_{user_idx}_{cell}",
                        "slice_index": cell_idx,
                        "token_count": 96,
                        "slice_text": " ".join([texts[cell], filler] * 3),
                        "directive_interpersonal_blend": directive,
                        "redemption_growth_rate": growth,
                    }
                )
    return pd.DataFrame(rows)


def test_build_slices_fixed_dispatch() -> None:
    users = synthetic_users(8)
    config = SuicaSliceConfig(strategy="fixed_8", slice_tokens=8, slice_stride=8, min_slice_tokens=4, max_slices_per_user=4)
    slices = build_slices(users, config)
    assert not slices.empty
    assert set(["user_id", "slice_text", "slice_strategy"]).issubset(slices.columns)
    assert slices["slice_strategy"].eq("fixed_8").all()


def test_build_slices_for_strategy_semantic_fallback_or_shift() -> None:
    users = synthetic_users(8)
    config = SuicaSliceConfig(strategy="semantic_shift", min_slice_tokens=4, max_slices_per_user=4)
    slices = build_slices_for_strategy(users, "semantic_shift", base_config=config)
    assert not slices.empty
    assert slices["user_id"].nunique() > 1


def test_suica_factor_run_and_summary() -> None:
    users = synthetic_users(24)
    bridge = synthetic_bridge(users)
    slice_config = SuicaSliceConfig(strategy="fixed_8", slice_tokens=8, slice_stride=8, min_slice_tokens=4, max_slices_per_user=5)
    slices = build_slices(users, slice_config)
    factor_config = SuicaFactorConfig(
        method="pca_varimax",
        tfidf_max_features=300,
        tfidf_min_df=1,
        svd_dims=6,
        flat_k=3,
        min_node_slices=4,
        factor_count=2,
        factor_min_reliability=-1.0,
        factor_min_features=2,
        random_seed=7,
    )
    artifacts = run_factor_method(slices, users, bridge, factor_config)
    assert not artifacts["node_table"].empty
    assert not artifacts["factor_scores"].empty
    assert not artifacts["big5_corr"].empty
    summary = summarize_run("fixed_8", "pca_varimax", slices, artifacts)
    assert 0.0 <= summary["suica_objective"] <= 1.0
    assert math.isfinite(summary["suica_objective"])


def test_suica_method_residual_control() -> None:
    users = synthetic_users(20)
    bridge = synthetic_bridge(users)
    users["text"] = users["text"] + " https://example.com reddit imgur youtube 123"
    slice_config = SuicaSliceConfig(strategy="fixed_8", slice_tokens=8, slice_stride=8, min_slice_tokens=4, max_slices_per_user=5)
    slices = build_slices(users, slice_config)
    factor_config = SuicaFactorConfig(
        method="gmm_soft",
        text_control="method_residual",
        tfidf_max_features=300,
        tfidf_min_df=1,
        svd_dims=6,
        gmm_k=3,
        min_node_slices=4,
        factor_count=2,
        factor_min_reliability=-1.0,
        factor_min_features=2,
        random_seed=11,
    )
    artifacts = run_factor_method(slices, users, bridge, factor_config)
    assert artifacts["vector_diag"]["text_control"] == "method_residual"
    assert "method_term_rate" in artifacts["vector_diag"]["control_columns"]
    assert 0.0 <= artifacts["vector_diag"]["residual_variance_retained"] <= 1.1


def test_suica_selective_condition_policy_branches() -> None:
    release = pd.Series(
        {
            "clarity_delta": 0.06,
            "delta_prop_residual": -0.02,
            "delta_prop_person": 0.01,
            "delta_prop_person_condition": 0.02,
        }
    )
    candidate = pd.Series(
        {
            "clarity_delta": 0.03,
            "delta_prop_residual": -0.01,
            "delta_prop_person": 0.02,
            "delta_prop_person_condition": 0.00,
        }
    )
    degradation = pd.Series(
        {
            "clarity_delta": -0.03,
            "delta_prop_residual": 0.00,
            "delta_prop_person": 0.00,
            "delta_prop_person_condition": 0.00,
        }
    )
    neutral = pd.Series(
        {
            "clarity_delta": 0.005,
            "delta_prop_residual": -0.001,
            "delta_prop_person": 0.00,
            "delta_prop_person_condition": 0.00,
        }
    )
    assert choose_policy(release)[1] == "centered_release"
    assert choose_policy(candidate)[1] == "centered_candidate"
    assert choose_policy(degradation)[1] == "raw_due_to_centering_degradation"
    assert choose_policy(neutral)[1] == "raw_default_neutral"


def test_suica_policy_profile_scorer_separates_base_react_choice() -> None:
    selected = pd.DataFrame(
        [
            {
                "scenario": "s",
                "user_id": "u1",
                "condition": "a",
                "slice_obs_id": "s1",
                "slice_index": 0,
                "token_count": 10,
                "selected_score": 1.0,
                "factor": "suica_factor_01",
                "selected_variant": "raw",
                "policy_class": "raw_default_neutral",
                "score_role": "base_score_candidate",
                "residual_quality": "lower_residual",
                "release_recommendation": "scale_like_candidate",
                "selected_relative_g_3x4": 0.8,
                "selected_absolute_g_3x4": 0.8,
                "provisional_name": "demo",
            },
            {
                "scenario": "s",
                "user_id": "u1",
                "condition": "a",
                "slice_obs_id": "s2",
                "slice_index": 1,
                "token_count": 10,
                "selected_score": 1.0,
                "factor": "suica_factor_01",
                "selected_variant": "raw",
                "policy_class": "raw_default_neutral",
                "score_role": "base_score_candidate",
                "residual_quality": "lower_residual",
                "release_recommendation": "scale_like_candidate",
                "selected_relative_g_3x4": 0.8,
                "selected_absolute_g_3x4": 0.8,
                "provisional_name": "demo",
            },
            {
                "scenario": "s",
                "user_id": "u1",
                "condition": "b",
                "slice_obs_id": "s3",
                "slice_index": 2,
                "token_count": 10,
                "selected_score": 3.0,
                "factor": "suica_factor_01",
                "selected_variant": "raw",
                "policy_class": "raw_default_neutral",
                "score_role": "base_score_candidate",
                "residual_quality": "lower_residual",
                "release_recommendation": "scale_like_candidate",
                "selected_relative_g_3x4": 0.8,
                "selected_absolute_g_3x4": 0.8,
                "provisional_name": "demo",
            },
        ]
    )
    profiles, react, choice = build_profiles(
        selected,
        min_slices=2,
        min_conditions=2,
        recommended_g=0.65,
        recommended_residual_sd=1.25,
    )
    row = profiles.iloc[0]
    assert math.isclose(row["base_score"], 2.0)
    assert math.isclose(row["observed_weighted_score"], 5.0 / 3.0)
    assert row["choice_influence_delta"] < 0
    assert set(react["react_score"].round(6)) == {-1.0, 1.0}
    assert math.isclose(float(choice.iloc[0]["choice_entropy_norm"]), entropy_norm(pd.Series([2, 1])))
    assert row["score_quality"] == "recommended"


def test_suica_profile_stability_metrics_detect_same_user_signal() -> None:
    users = [f"u{i}" for i in range(6)]
    factors = ["f1", "f2", "f3", "f4"]
    a = pd.DataFrame(
        [
            [1.0, 0.0, 0.0, 0.2],
            [0.0, 1.0, 0.0, 0.3],
            [0.0, 0.0, 1.0, 0.4],
            [1.0, 1.0, 0.0, 0.5],
            [0.0, 1.0, 1.0, 0.6],
            [1.0, 0.0, 1.0, 0.7],
        ],
        index=users,
        columns=factors,
        dtype=float,
    )
    b = a + 0.01
    metrics = row_metrics(a, b, min_dimensions=3)
    assert len(metrics) == 6
    assert metrics["profile_cosine"].min() > 0.99
    actual = metrics["profile_cosine"].to_numpy(float)
    shuffled_b = b.sample(frac=1.0, random_state=1).copy()
    shuffled_b.index = users
    random_values = row_metrics(a, shuffled_b, min_dimensions=3)["profile_cosine"].to_numpy(float)
    assert auc_probability(actual, random_values) > 0.5


def test_suica_choice_shape_features_and_distance_auc() -> None:
    slices = pd.DataFrame(
        [
            {"scenario": "pandora_cross_subreddit", "user_id": "u1", "condition": "top_subreddit", "slice_obs_id": "a"},
            {"scenario": "pandora_cross_subreddit", "user_id": "u1", "condition": "top_subreddit", "slice_obs_id": "b"},
            {"scenario": "pandora_cross_subreddit", "user_id": "u1", "condition": "other_subreddit", "slice_obs_id": "c"},
            {"scenario": "pandora_cross_subreddit", "user_id": "u2", "condition": "other_subreddit", "slice_obs_id": "d"},
            {"scenario": "pandora_cross_subreddit", "user_id": "u2", "condition": "other_subreddit", "slice_obs_id": "e"},
        ]
    )
    dist = condition_distribution(slices)
    features = choice_shape_features(dist)
    u1 = features.loc[features["user_id"].eq("u1")].iloc[0]
    assert u1["n_slices"] == 3
    assert u1["top_condition_share"] == 2 / 3
    assert u1["top_context_focus"] == 2 / 3
    assert features["choice_use"].eq("candidate_choice_construct").all()
    assert distance_auc(actual_dist=pd.Series([0.1, 0.2]).to_numpy(), random_dist=pd.Series([0.5, 0.8]).to_numpy()) == 1.0


def test_suica_external_anchor_bh_and_corr() -> None:
    q = benjamini_hochberg(pd.Series([0.001, 0.02, 0.04, float("nan")]))
    assert q.iloc[0] <= q.iloc[1] <= q.iloc[2]
    assert pd.isna(q.iloc[3])
    r, _p = external_safe_corr(pd.Series([1, 2, 3, 4]).to_numpy(float), pd.Series([2, 4, 6, 8]).to_numpy(float))
    assert r > 0.99


def test_suica_narrative_projective_anchor_scoring_and_profiles() -> None:
    anchors = score_text_anchors("I decided to help my friend because I want to grow and feel better.")
    assert anchors["agency_rate"] > 0
    assert anchors["communion_rate"] > 0
    assert anchors["mentalization_rate"] > 0
    assert anchors["causal_meaning_rate"] > 0
    assert anchors["redemption_growth_rate"] > 0
    assert anchors["narrative_integration_rate"] > anchors["causal_meaning_rate"]

    slices = pd.DataFrame(
        [
            {
                "scenario": "s",
                "user_id": "u1",
                "condition": "a",
                "slice_obs_id": "s1",
                "slice_index": 0,
                "token_count": 12,
                "slice_text": "I can help people because I understand them.",
            },
            {
                "scenario": "s",
                "user_id": "u1",
                "condition": "b",
                "slice_obs_id": "s2",
                "slice_index": 1,
                "token_count": 12,
                "slice_text": "Maybe this problem was hard but we learn.",
            },
        ]
    )
    slice_anchors = build_slice_anchor_frame(slices)
    profiles = aggregate_user_anchor_profiles(slice_anchors)
    row = profiles.iloc[0]
    assert row["n_slices"] == 2
    assert row["n_conditions"] == 2
    assert "agency_rate_mean" in profiles.columns
    assert "agency_rate_condition_amp" in profiles.columns


def test_suica_blind_construct_package_hides_factor_and_checks_alignment() -> None:
    rows = []
    for idx in range(24):
        high = idx >= 12
        text = (
            "she told her family because the story happened years ago"
            if high
            else "I can decide what to do and I want to grow"
        )
        rows.append(
            {
                "scenario": "pandora_temporal" if idx % 2 else "essays_random",
                "slice_obs_id": f"s{idx}",
                "user_id": f"u{idx}",
                "condition": "a" if idx % 2 else "b",
                "slice_index": idx,
                "token_count": 12,
                "slice_text": text,
                "suica_factor_04": float(idx),
                "suica_factor_04_centered": float(idx - 12),
            }
        )
    frame = pd.DataFrame(rows)
    status = pd.DataFrame(
        [
            {
                "factor": "suica_factor_04",
                "provisional_name": "third-person relational narrative focus",
                "measurement_role": "base",
            }
        ]
    )
    examples = select_extreme_examples(
        frame,
        ["suica_factor_04"],
        status,
        examples_per_pole=3,
        max_per_scenario=2,
        max_excerpt_chars=200,
    )
    coder, key = build_blind_items(examples, seed=1)
    assert "factor" not in coder.columns
    assert "pole" not in coder.columns
    assert {"factor", "pole", "blind_item_id"}.issubset(key.columns)
    assert stable_text_hash("A  text") == stable_text_hash("a text")

    contrast = full_pole_anchor_contrast(frame, ["suica_factor_04"], quantile=0.25)
    anchor_summary = pd.DataFrame(
        [
            {
                "factor": "suica_factor_04",
                "profile_component": "base_score",
                "anchor": "third_person_rate",
                "median_r": 0.5,
                "support_score": 0.5,
            }
        ]
    )
    alignment = build_alignment_summary(contrast, anchor_summary)
    assert alignment.iloc[0]["direction_match_rate"] == 1.0


def test_suica_blind_construct_evaluator_auto_control_and_agreement() -> None:
    auto_precode = pd.DataFrame(
        {
            "blind_item_id": list("abcdefgh"),
            "agency_rate": [0, 1, 0, 1, 5, 6, 5, 6],
            "communion_rate": [0] * 8,
            "mentalization_rate": [0, 1, 0, 1, 5, 6, 5, 6],
            "past_temporal_rate": [0] * 8,
            "future_temporal_rate": [0] * 8,
            "temporal_sequence_rate": [0] * 8,
            "directive_rate": [0, 1, 0, 1, 5, 6, 5, 6],
            "second_person_rate": [0, 1, 0, 1, 5, 6, 5, 6],
            "directive_interpersonal_blend": [0, 1, 0, 1, 5, 6, 5, 6],
            "self_focus_rate": [0] * 8,
            "third_person_rate": [0] * 8,
            "general_people_rate": [0] * 8,
            "negative_affect_rate": [0] * 8,
            "uncertainty_rate": [0] * 8,
            "conflict_threat_rate": [0] * 8,
            "projective_tension_rate": [0] * 8,
            "redemption_growth_rate": [0] * 8,
            "growth_after_tension_blend": [0] * 8,
            "social_evaluation_rate": [0] * 8,
            "novelty_play_rate": [0] * 8,
        }
    )
    coder = build_auto_control(auto_precode)
    assert "agency_0_to_3" in coder.columns
    assert coder["agency_0_to_3"].iloc[-1] > coder["agency_0_to_3"].iloc[0]

    key = pd.DataFrame(
        {
            "blind_item_id": list("abcdefgh"),
            "factor": ["suica_factor_10"] * 8,
            "pole": ["low", "low", "low", "low", "high", "high", "high", "high"],
            "source_family": ["s"] * 8,
        }
    )
    coded = coder.assign(coder_id="c1").merge(key, on="blind_item_id")
    pole = evaluate_pole_separation(coded)
    gate = expected_dimension_summary(pole)
    assert pole.loc[pole["dimension"].eq("agency"), "cohen_d"].iloc[0] > 0
    assert gate.iloc[0]["construct_gate"] == "support"

    adjusted = source_adjusted_pole_effects(coded)
    adjusted_gate = expected_source_adjusted_summary(adjusted)
    assert not adjusted.empty
    assert adjusted_gate.iloc[0]["source_adjusted_gate"] == "support"

    coded2 = pd.concat(
        [
            coded,
            coder.assign(coder_id="c2").merge(key, on="blind_item_id"),
        ],
        ignore_index=True,
    )
    agreement = inter_coder_agreement(coded2)
    assert not agreement.empty
    assert agreement.loc[agreement["dimension"].eq("agency"), "pearson_r"].iloc[0] > 0.99


def test_suica_factor_repair_audit_classifies_priority_mixed_and_weak() -> None:
    priority = pd.Series(
        {
            "construct_gate": "support",
            "source_adjusted_gate": "support",
            "stable_anchor_count": 3,
            "median_expected_abs_d": 0.8,
            "median_expected_abs_adjusted_beta": 0.6,
            "has_length_anchor_risk": False,
            "has_method_or_adapter_status": False,
            "has_two_source_families": True,
        }
    )
    assert classify_factor(priority, 0.3)[0] == "priority_independent_blind_coding"
    mixed = priority.copy()
    mixed["has_length_anchor_risk"] = True
    assert classify_factor(mixed, 0.3)[0] == "mixed_method_audit"
    weak = priority.copy()
    weak["construct_gate"] = "weak_or_needs_review"
    weak["source_adjusted_gate"] = "weak_or_source_sensitive"
    assert classify_factor(weak, 0.3)[0] == "repair_or_downgrade"

    factor_status = pd.DataFrame(
        [
            {
                "factor": "suica_factor_04",
                "provisional_name": "third-person",
                "measurement_role": "base",
                "class": "base",
            }
        ]
    )
    anchors = pd.DataFrame(
        [
            {
                "factor": "suica_factor_04",
                "profile_component": "base_score",
                "anchor": "third_person_rate_mean",
                "scenario_count": 6,
                "support_score": 0.5,
                "direction_agreement": 1.0,
                "measurement_role": "base",
                "class": "base",
            },
            {
                "factor": "suica_factor_04",
                "profile_component": "base_score",
                "anchor": "temporal_balance_mean",
                "scenario_count": 6,
                "support_score": 0.4,
                "direction_agreement": 1.0,
                "measurement_role": "base",
                "class": "base",
            }
        ]
    )
    blind_gate = pd.DataFrame(
        [
            {
                "factor": "suica_factor_04",
                "construct_gate": "support",
                "expected_dimensions": "other_focus",
                "median_expected_abs_d": 0.8,
                "max_expected_abs_d": 1.0,
                "strongest_expected_dimension": "other_focus",
                "strongest_expected_d": 1.0,
            }
        ]
    )
    source_gate = pd.DataFrame(
        [
            {
                "factor": "suica_factor_04",
                "source_adjusted_gate": "support",
                "median_expected_abs_adjusted_beta": 0.5,
                "max_expected_abs_adjusted_beta": 0.8,
                "source_adjusted_large_effect_count_abs_beta_ge_0p3": 1,
            }
        ]
    )
    blind_key = pd.DataFrame(
        [
            {"factor": "suica_factor_04", "pole": "high", "source_family": "pandora"},
            {"factor": "suica_factor_04", "pole": "low", "source_family": "essays"},
        ]
    )
    decisions = build_repair_decisions(
        factor_status,
        anchors,
        blind_gate,
        source_gate,
        blind_key,
        pd.DataFrame(),
        pd.DataFrame(),
        stable_anchor_threshold=0.3,
        source_support_threshold=0.3,
    )
    assert decisions.iloc[0]["repair_decision"] == "priority_independent_blind_coding"


def test_suica_rebalanced_repair_package_balances_source_and_pole() -> None:
    rows = []
    for source in ["pandora", "essays"]:
        for idx in range(8):
            rows.append(
                {
                    "scenario": f"{source}_scenario",
                    "source_family": source,
                    "slice_obs_id": f"{source}_{idx}",
                    "user_id": f"{source}_u{idx}",
                    "condition": "a",
                    "slice_index": idx,
                    "token_count": 12,
                    "slice_text": f"{source} text {idx}",
                    "suica_factor_09_centered": float(idx - 4),
                }
            )
    frame = pd.DataFrame(rows)
    selected = select_within_source_pole(
        frame,
        "suica_factor_09",
        {"suica_factor_09": {"provisional_name": "demo", "measurement_role": "repair"}},
        source_families=["pandora", "essays"],
        examples_per_source_pole=2,
        max_per_scenario=10,
        max_excerpt_chars=120,
    )
    coder, key = build_repair_blind_items(selected, seed=1)
    counts = source_pole_counts(key)
    balance = source_balance_summary(counts)
    assert len(coder) == 8
    assert set(counts["count"]) == {2}
    assert balance.iloc[0]["balanced_source_pole"] is True or bool(balance.iloc[0]["balanced_source_pole"])


def test_suica_independent_blind_validation_batch_balances_and_hides_key() -> None:
    rows = []
    for factor_i, factor in enumerate(["suica_factor_01", "suica_factor_02"]):
        for source in ["pandora", "essays"]:
            for idx in range(10):
                rows.append(
                    {
                        "scenario": f"{source}_scenario",
                        "source_family": source,
                        "slice_obs_id": f"{factor}_{source}_{idx}",
                        "user_id": f"{source}_u{factor_i}_{idx}",
                        "condition": "a",
                        "slice_index": idx,
                        "token_count": 12,
                        "slice_text": f"{source} {factor} independent text {idx}",
                        f"{factor}_centered": float(idx - 5),
                    }
                )
    frame = pd.DataFrame(rows)
    status_lookup = {
        "suica_factor_01": {
            "provisional_name": "demo one",
            "measurement_role": "base",
            "repair_decision": "priority_independent_blind_coding",
            "construct_gate": "support",
            "source_adjusted_gate": "support",
            "stable_anchor_count": 3,
        },
        "suica_factor_02": {
            "provisional_name": "demo two",
            "measurement_role": "repaired",
            "repair_decision": "mixed_or_source_limited_audit",
            "construct_gate": "support",
            "source_adjusted_gate": "support",
            "stable_anchor_count": 2,
        },
    }
    selected = select_formal_examples(
        frame,
        ["suica_factor_01", "suica_factor_02"],
        status_lookup,
        source_families=["pandora", "essays"],
        examples_per_source_pole=2,
        max_per_scenario=20,
        max_excerpt_chars=120,
    )
    coder, key = build_independent_blind_items(selected, seed=3)
    counts = source_pole_counts(key)
    balance = source_balance_summary(counts)
    manifest = build_factor_manifest(key)
    coder_a = build_coder_order(coder, coder_id="coder_A", seed=10)
    coder_b = build_coder_order(coder, coder_id="coder_B", seed=11)

    assert len(coder) == 16
    assert "factor" not in coder.columns
    assert "pole" not in coder.columns
    assert key["text_hash"].nunique() == len(key)
    assert set(counts["count"]) == {2}
    assert balance["balanced_source_pole"].astype(bool).all()
    assert set(manifest["formal_inclusion_status"]) == {
        "priority_independent_blind_coding",
        "source_balanced_repair_passed",
    }
    assert coder_a["coder_order"].iloc[0] == 1
    assert coder_b["coder_id"].eq("coder_B").all()


def test_suica_independent_blind_masks_personality_terms_and_builds_requests() -> None:
    masked, count = mask_personality_terms("I post in /r/ENTP and took a Big Five personality test.")
    assert count >= 2
    assert "ENTP" not in masked
    assert "Big Five" not in masked

    items = pd.DataFrame(
        [
            {"blind_item_id": "SUICA-IB-0001", "text_excerpt": masked},
            {"blind_item_id": "SUICA-IB-0002", "text_excerpt": "I decided to help because she seemed worried."},
        ]
    )
    request = build_request_record(items, batch_index=1, coder_id="coder", model="dry", temperature=0.0)
    prompt = request["messages"][1]["content"]
    assert "suica_factor_" not in prompt
    assert "source_family" not in prompt
    assert "Big Five" not in prompt

    response = {
        "items": [
            {
                "blind_item_id": "SUICA-IB-0001",
                "rating": {
                    "agenacy": 4,
                    "communication": 1,
                    "mentalization": 2,
                    "temporal_integration": 0,
                    "directive_interpersonal": 0,
                    "self_focus": 1,
                    "other_focus": 0,
                    "affect_tension": 0,
                    "redemption_growth": 0,
                    "social_evaluation": 0,
                    "novelty_play": 0,
                },
                "coder_notes": "clipped agency",
            },
            {
                "blind_item_id": "SUICA-IB-0002",
                "ratings": {
                    "agency": 1,
                    "communion": 3,
                    "mentalization": 2,
                    "temporal_integration": 0,
                    "directive_interpersonal": 0,
                    "self_focus": 1,
                    "other_focus": 2,
                    "affect_tension": 1,
                    "redemption_growth": 0,
                    "social_evaluation": 0,
                    "novelty_play": 0,
                },
            },
        ]
    }
    rows, errors = parse_llm_ratings_response(json.dumps(response), expected_ids={"SUICA-IB-0001", "SUICA-IB-0002"})
    assert any(error["error"] == "schema_alias_normalized" for error in errors)
    assert len(rows) == 2
    assert rows[0]["agency_0_to_3"] == 3.0
    assert rows[0]["communion_0_to_3"] == 1.0


def test_suica_independent_blind_summary_classifies_pass_partial_and_hold() -> None:
    expected_gate = pd.DataFrame(
        [
            {"coder_id": "a", "factor": "f_pass", "construct_gate": "support", "median_expected_abs_d": 1.0},
            {"coder_id": "b", "factor": "f_pass", "construct_gate": "support", "median_expected_abs_d": 0.9},
            {"coder_id": "a", "factor": "f_partial", "construct_gate": "support", "median_expected_abs_d": 0.8},
            {"coder_id": "b", "factor": "f_partial", "construct_gate": "weak_or_needs_review", "median_expected_abs_d": 0.4},
            {"coder_id": "a", "factor": "f_hold", "construct_gate": "support", "median_expected_abs_d": 0.8},
            {"coder_id": "b", "factor": "f_hold", "construct_gate": "weak_or_needs_review", "median_expected_abs_d": 0.4},
        ]
    )
    source_gate = pd.DataFrame(
        [
            {"coder_id": "a", "factor": "f_pass", "source_adjusted_gate": "support", "median_expected_abs_adjusted_beta": 0.7},
            {"coder_id": "b", "factor": "f_pass", "source_adjusted_gate": "support", "median_expected_abs_adjusted_beta": 0.6},
            {"coder_id": "a", "factor": "f_partial", "source_adjusted_gate": "support", "median_expected_abs_adjusted_beta": 0.7},
            {"coder_id": "b", "factor": "f_partial", "source_adjusted_gate": "support", "median_expected_abs_adjusted_beta": 0.4},
            {"coder_id": "a", "factor": "f_hold", "source_adjusted_gate": "support", "median_expected_abs_adjusted_beta": 0.7},
            {"coder_id": "b", "factor": "f_hold", "source_adjusted_gate": "weak_or_source_sensitive", "median_expected_abs_adjusted_beta": 0.2},
        ]
    )
    manifest = pd.DataFrame(
        [
            {"factor": "f_pass", "provisional_name": "pass", "formal_inclusion_status": "priority"},
            {"factor": "f_partial", "provisional_name": "partial", "formal_inclusion_status": "repair"},
            {"factor": "f_hold", "provisional_name": "hold", "formal_inclusion_status": "priority"},
        ]
    )
    summary = factor_acceptance_summary(expected_gate, source_gate, manifest)
    decisions = dict(zip(summary["factor"], summary["decision"], strict=True))
    assert decisions["f_pass"] == "pass_independent_blind_gate"
    assert decisions["f_partial"] == "partial_construct_gate_revise_or_add_items"
    assert decisions["f_hold"] == "hold_or_repair_factor"

    agreement = pd.DataFrame(
        {
            "dimension": ["x", "y"],
            "pearson_r": [0.56, 0.7],
            "mean_abs_diff": [0.4, 0.3],
        }
    )
    assert agreement_summary(agreement, min_agreement_r=0.55).iloc[0]["agreement_gate"] == "support"


def test_suica_construct_candidate_manual_tiers_and_dimension_direction() -> None:
    pole = pd.DataFrame(
        [
            {"factor": "f", "dimension": "agency", "cohen_d": 0.8, "high_minus_low": 1.0},
            {"factor": "f", "dimension": "agency", "cohen_d": 0.6, "high_minus_low": 0.8},
            {"factor": "f", "dimension": "other_focus", "cohen_d": -0.7, "high_minus_low": -1.0},
            {"factor": "f", "dimension": "other_focus", "cohen_d": -0.9, "high_minus_low": -1.2},
            {"factor": "f", "dimension": "novelty_play", "cohen_d": 0.2, "high_minus_low": 0.1},
            {"factor": "f", "dimension": "novelty_play", "cohen_d": -0.1, "high_minus_low": -0.1},
        ]
    )
    contrast = build_dimension_contrast(pole, effect_threshold=0.5)
    directions = dict(zip(contrast["dimension"], contrast["direction"], strict=True))
    assert directions["agency"] == "high_pole"
    assert directions["other_focus"] == "low_pole"
    assert directions["novelty_play"] == "weak_or_mixed"

    assert evidence_tier("pass_independent_blind_gate") == "construct_candidate"
    assert evidence_tier("partial_construct_gate_revise_or_add_items") == "repair_candidate"
    assert evidence_tier("hold_or_repair_factor") == "hold_or_split"

    cards = pd.DataFrame(
        [
            {
                "factor": "f",
                "evidence_tier": "repair_candidate",
                "recommended_construct_label": "demo",
            }
        ]
    )
    queue = build_repair_queue(cards)
    assert queue.iloc[0]["action"] == "add_items_and_retest_expected_dimensions"


def test_suica_weak_factor_diagnosis_flags_weak_expected_and_stable_alternative() -> None:
    pole = pd.DataFrame(
        [
            {"coder_id": "a", "factor": "suica_factor_05", "dimension": "novelty_play", "cohen_d": 0.9, "high_minus_low": 1.0},
            {"coder_id": "b", "factor": "suica_factor_05", "dimension": "novelty_play", "cohen_d": 0.8, "high_minus_low": 0.8},
            {"coder_id": "a", "factor": "suica_factor_05", "dimension": "agency", "cohen_d": 0.2, "high_minus_low": 0.2},
            {"coder_id": "b", "factor": "suica_factor_05", "dimension": "agency", "cohen_d": 0.1, "high_minus_low": 0.1},
        ]
    )
    source = pd.DataFrame(
        [
            {
                "coder_id": "a",
                "factor": "suica_factor_05",
                "dimension": "novelty_play",
                "high_minus_low_source_adjusted": 0.8,
            },
            {
                "coder_id": "b",
                "factor": "suica_factor_05",
                "dimension": "novelty_play",
                "high_minus_low_source_adjusted": 0.7,
            },
            {
                "coder_id": "a",
                "factor": "suica_factor_05",
                "dimension": "agency",
                "high_minus_low_source_adjusted": 0.2,
            },
            {
                "coder_id": "b",
                "factor": "suica_factor_05",
                "dimension": "agency",
                "high_minus_low_source_adjusted": 0.1,
            },
        ]
    )
    diag = dimension_repair_diagnostics(
        pole,
        source,
        targets=["suica_factor_05"],
        blind_d_threshold=0.5,
        source_beta_threshold=0.3,
    )
    statuses = dict(zip(diag["dimension"], diag["status"], strict=True))
    assert statuses["novelty_play"] == "stable_candidate_dimension"
    assert statuses["agency"] == "expected_dimension_weak"

    acceptance = pd.DataFrame(
        [{"factor": "suica_factor_05", "decision": "partial_construct_gate_revise_or_add_items"}]
    )
    cards = pd.DataFrame(
        [{"factor": "suica_factor_05", "recommended_construct_label": "playful task/interest engagement"}]
    )
    plan = factor_repair_plan(diag, acceptance, cards, targets=["suica_factor_05"])
    assert plan.iloc[0]["diagnosis"] == "expected_dimension_overbroad"
    assert plan.iloc[0]["stable_candidate_dimensions"] == "novelty_play"

    coded = pd.DataFrame(
        [
            {
                "coder_id": "a",
                "blind_item_id": "i1",
                "factor": "suica_factor_05",
                "pole": "high",
                "source_family": "pandora",
                "scenario": "s",
                "factor_score": 1.0,
                "text_excerpt": "demo",
                **{f"{dimension}_0_to_3": 0 for dimension in DIMENSIONS},
            },
            {
                "coder_id": "b",
                "blind_item_id": "i1",
                "factor": "suica_factor_05",
                "pole": "high",
                "source_family": "pandora",
                "scenario": "s",
                "factor_score": 1.0,
                "text_excerpt": "demo",
                **{f"{dimension}_0_to_3": 1 for dimension in DIMENSIONS},
            },
        ]
    )
    disagreement = item_disagreement_diagnostics(coded, targets=["suica_factor_05"], top_n=1)
    assert disagreement.iloc[0]["mean_abs_diff_all_dimensions"] == 1.0


def test_suica_repair_candidate_rescoring_detects_component_masking() -> None:
    rows = []
    for coder in ["a", "b"]:
        for idx in range(12):
            high = idx >= 6
            row = {
                "coder_id": coder,
                "blind_item_id": f"i{idx}",
                "factor": "suica_factor_05",
                "pole": "high" if high else "low",
                "source_family": "pandora" if idx % 2 else "essays",
                "scenario": "s",
                "factor_score": float(idx),
                "text_excerpt": "demo",
            }
            for dimension in DIMENSIONS:
                row[f"{dimension}_0_to_3"] = 0.0
            row["novelty_play_0_to_3"] = (1.5 + 0.1 * (idx - 6)) if high else (0.1 * idx)
            row["agency_0_to_3"] = 1.0 + 0.02 * (idx % 3)
            rows.append(row)
    coded = pd.DataFrame(rows)
    specs = [
        CandidateSpec("broad", "suica_factor_05", "broad", {"novelty_play": 0.5, "agency": 0.5}, ""),
        CandidateSpec("core", "suica_factor_05", "core", {"novelty_play": 1.0}, ""),
    ]
    scored = score_candidate_rows(coded, specs)
    metrics = candidate_coder_metrics(scored)
    agreement = candidate_agreement(scored)
    pole = pd.DataFrame(
        [
            {"factor": "suica_factor_05", "coder_id": "a", "dimension": "novelty_play", "cohen_d": 3.0},
            {"factor": "suica_factor_05", "coder_id": "b", "dimension": "novelty_play", "cohen_d": 3.0},
            {"factor": "suica_factor_05", "coder_id": "a", "dimension": "agency", "cohen_d": 0.0},
            {"factor": "suica_factor_05", "coder_id": "b", "dimension": "agency", "cohen_d": 0.0},
            {"factor": "suica_factor_06", "coder_id": "a", "dimension": "novelty_play", "cohen_d": 0.0},
            {"factor": "suica_factor_06", "coder_id": "b", "dimension": "novelty_play", "cohen_d": 0.0},
            {"factor": "suica_factor_06", "coder_id": "a", "dimension": "agency", "cohen_d": 1.0},
            {"factor": "suica_factor_06", "coder_id": "b", "dimension": "agency", "cohen_d": 1.0},
        ]
    )
    source = pd.DataFrame(
        [
            {
                "factor": "suica_factor_05",
                "coder_id": coder,
                "dimension": dimension,
                "high_minus_low_source_adjusted": beta,
            }
            for coder in ["a", "b"]
            for dimension, beta in [("novelty_play", 2.0), ("agency", 0.0)]
        ]
    )
    components = candidate_component_diagnostics(
        specs,
        pole,
        source,
        d_threshold=0.5,
        source_beta_threshold=0.3,
    )
    overlap = candidate_overlap(specs, pole, reference_factor="suica_factor_06")
    summary = summarize_candidates(
        metrics,
        agreement,
        overlap,
        components,
        d_threshold=0.5,
        source_beta_threshold=0.3,
        agreement_threshold=0.5,
    )
    decisions = dict(zip(summary["candidate_id"], summary["repair_rescoring_decision"], strict=True))
    coverage = dict(zip(summary["candidate_id"], summary["component_coverage_ratio"], strict=True))
    assert decisions["core"] == "repair_candidate_promote_for_new_blind_batch"
    assert decisions["broad"] == "composite_support_but_component_masking"
    assert coverage["broad"] == 0.5


def test_suica_repair_candidate_blind_batch_balances_source_and_flags_fallback() -> None:
    rows = []
    for source in ["pandora", "essays"]:
        for pole in ["high", "low"]:
            role = f"retain_{pole}_anchor"
            rows.append(
                {
                    "candidate_id": "c1",
                    "parent_factor": "f1",
                    "candidate_label": "candidate one",
                    "blind_item_id": f"c1_{source}_{pole}_retain",
                    "pole": pole,
                    "source_family": source,
                    "scenario": "s",
                    "factor_score": 1.0 if pole == "high" else -1.0,
                    "candidate_score_mean": 2.0 if pole == "high" else 0.0,
                    "candidate_score_std": 0.0,
                    "item_repair_role": role,
                    "excerpt": "demo text",
                }
            )
    rows.append(
        {
            "candidate_id": "c2",
            "parent_factor": "f2",
            "candidate_label": "candidate two",
                "blind_item_id": "c2_pandora_low_middle",
            "pole": "low",
            "source_family": "pandora",
            "scenario": "s",
            "factor_score": -1.0,
            "candidate_score_mean": 0.2,
            "candidate_score_std": 0.0,
            "item_repair_role": "middle_or_secondary_item",
            "excerpt": "fallback text",
        }
    )
    for source, pole in [("pandora", "high"), ("essays", "high"), ("essays", "low")]:
        rows.append(
            {
                "candidate_id": "c2",
                "parent_factor": "f2",
                "candidate_label": "candidate two",
                "blind_item_id": f"c2_{source}_{pole}_retain",
                "pole": pole,
                "source_family": source,
                "scenario": "s",
                "factor_score": 1.0 if pole == "high" else -1.0,
                "candidate_score_mean": 2.0 if pole == "high" else 0.0,
                "candidate_score_std": 0.0,
                "item_repair_role": f"retain_{pole}_anchor",
                "excerpt": "demo text",
            }
        )
    item_roles = pd.DataFrame(rows)
    selected, gaps = select_candidate_examples(
        item_roles,
        candidates=["c1", "c2"],
        source_families=["pandora", "essays"],
        examples_per_source_pole=1,
    )
    counts = repair_candidate_source_pole_counts(selected)
    assert len(selected) == 8
    assert counts["items"].eq(1).all()
    fallback = gaps.loc[
        gaps["candidate_id"].eq("c2")
        & gaps["source_family"].eq("pandora")
        & gaps["pole"].eq("low"),
        "used_fallback_rows",
    ].iloc[0]
    assert bool(fallback)

    feasibility = formal_feasibility(item_roles, ["c1", "c2"], ["pandora", "essays"], target=2)
    assert feasibility["needs_item_bank_expansion"].any()


def test_suica_repair_candidate_llm_eval_requires_component_coverage() -> None:
    rows = []
    for coder_id in ["a", "b"]:
        for candidate_id, label in [
            ("f05_novelty_play_core", "novelty"),
            ("f10_action_growth_channel", "action-growth"),
        ]:
            for source in ["pandora", "essays"]:
                for pole in ["high", "low"]:
                    row = {
                        "coder_id": coder_id,
                        "blind_item_id": f"{coder_id}_{candidate_id}_{source}_{pole}",
                        "candidate_id": candidate_id,
                        "candidate_label": label,
                        "pole": pole,
                        "source_family": source,
                    }
                    for dimension in DIMENSIONS:
                        row[f"{dimension}_0_to_3"] = 0.0
                    if candidate_id == "f05_novelty_play_core":
                        row["novelty_play_0_to_3"] = 2.0 if pole == "high" else 0.0
                    else:
                        row["directive_interpersonal_0_to_3"] = 2.0 if pole == "high" else 0.0
                        row["redemption_growth_0_to_3"] = 1.0 if pole == "high" else 0.0
                        row["communion_0_to_3"] = 0.0 if pole == "high" else 1.0
                    rows.append(row)
    coded = pd.DataFrame(rows)
    pole = repair_candidate_source_adjusted_delta(coded)
    # Build a minimal pole table with the same high-minus-low schema expected by the gate.
    pole_rows = []
    for (coder_id, candidate_id), group in coded.groupby(["coder_id", "candidate_id"]):
        for dimension in DIMENSIONS:
            col = f"{dimension}_0_to_3"
            high = pd.to_numeric(group.loc[group["pole"].eq("high"), col], errors="coerce")
            low = pd.to_numeric(group.loc[group["pole"].eq("low"), col], errors="coerce")
            pole_rows.append(
                {
                    "coder_id": coder_id,
                    "candidate_id": candidate_id,
                    "candidate_label": group["candidate_label"].iloc[0],
                    "dimension": dimension,
                    "high_minus_low": float(high.mean() - low.mean()),
                }
            )
    pole_table = pd.DataFrame(pole_rows)
    gate = repair_candidate_expected_gate(pole_table, pole, delta_threshold=0.3)
    acceptance = repair_candidate_acceptance(gate, pd.DataFrame(), agreement_threshold=0.5)
    decisions = dict(zip(acceptance["candidate_id"], acceptance["decision"], strict=True))
    assert decisions["f05_novelty_play_core"] == "pass_micro_confirmation"
    assert decisions["f10_action_growth_channel"] == "needs_item_bank_repair_or_larger_batch"


def test_suica_action_growth_revision_passes_without_communion() -> None:
    pole = pd.DataFrame(
        [
            {
                "coder_id": coder_id,
                "candidate_id": "f10_action_growth_channel",
                "candidate_label": "action-growth",
                "dimension": dimension,
                "high_minus_low": delta,
            }
            for coder_id in ["a", "b"]
            for dimension, delta in [
                ("directive_interpersonal", 2.0),
                ("redemption_growth", 1.0),
                ("communion", -1.0),
            ]
        ]
    )
    source = pd.DataFrame(
        [
            {
                "coder_id": coder_id,
                "candidate_id": "f10_action_growth_channel",
                "candidate_label": "action-growth",
                "dimension": dimension,
                "source_adjusted_high_minus_low": delta,
            }
            for coder_id in ["a", "b"]
            for dimension, delta in [
                ("directive_interpersonal", 2.0),
                ("redemption_growth", 1.0),
                ("communion", -1.0),
            ]
        ]
    )
    agreement = pd.DataFrame(
        [
            {"dimension": "directive_interpersonal", "pearson_r": 0.8},
            {"dimension": "redemption_growth", "pearson_r": 0.7},
            {"dimension": "communion", "pearson_r": 0.9},
        ]
    )
    gate = action_growth_virtual_gate(
        pole,
        source,
        agreement,
        delta_threshold=0.3,
        agreement_threshold=0.5,
    )
    original = pd.DataFrame(
        [
            {
                "candidate_id": "f10_action_growth_channel",
                "candidate_label": "action-growth",
                "expected_dimensions": "directive_interpersonal; redemption_growth; communion",
                "coder_count": 2,
                "support_coder_count": 0,
                "min_expected_delta_across_coders": -1.0,
                "min_source_adjusted_delta_across_coders": -1.0,
                "mean_expected_dimension_agreement": 0.8,
                "decision": "needs_item_bank_repair_or_larger_batch",
            }
        ]
    )
    summary = action_growth_virtual_summary(gate, original)
    decisions = dict(zip(summary["candidate_id"], summary["decision"], strict=True))
    assert decisions["f10_action_growth_channel"] == "needs_item_bank_repair_or_larger_batch"
    assert decisions["f10_action_growth_v2_no_communion"] == "pass_virtual_micro_confirmation"


def test_suica_action_growth_2x2_builder_selects_balanced_quadrants() -> None:
    rows = []
    idx = 0
    for source in ["pandora", "essays"]:
        for quadrant, directive, growth in [
            ("directive_growth", 2.0, 2.0),
            ("directive_only", 2.0, 0.0),
            ("growth_only", 0.0, 2.0),
            ("low_both", 0.0, 0.0),
        ]:
            for rep in range(3):
                rows.append(
                    {
                        "scenario": f"{source}_scenario",
                        "slice_obs_id": f"s{idx}",
                        "user_id": f"u{idx}",
                        "condition": "c",
                        "slice_index": idx,
                        "token_count": 80,
                        "slice_text": f"{source} {quadrant} unique text {idx} with enough words for selection and no repeated token problem",
                        "directive_interpersonal_blend": directive + (rep * 0.1 if directive > 0 else 0.0),
                        "redemption_growth_rate": growth + (rep * 0.1 if growth > 0 else 0.0),
                    }
                )
                idx += 1
    anchors = pd.DataFrame(rows)
    frame = prepare_action_growth_2x2_anchor_frame(
        anchors,
        directive_column="directive_interpersonal_blend",
        growth_column="redemption_growth_rate",
        min_token_count=40,
        max_top_token_share=0.3,
    )
    frame = add_action_growth_2x2_selection_scores(frame)
    selected, gaps = select_action_growth_2x2_examples(
        frame,
        source_families=["pandora", "essays"],
        examples_per_source_cell=2,
        seed=1,
        max_excerpt_chars=200,
    )
    assert len(selected) == 16
    assert gaps["selection_complete"].all()
    counts = selected.groupby(["source_family", "quadrant"]).size()
    assert counts.nunique() == 1
    assert counts.iloc[0] == 2


def test_suica_action_growth_2x2_eval_distinguishes_marginal_from_interaction() -> None:
    rows = []
    for coder_id in ["a", "b"]:
        for source in ["pandora", "essays"]:
            for quadrant, directive_flag, growth_flag in [
                ("directive_growth", True, True),
                ("directive_only", True, False),
                ("growth_only", False, True),
                ("low_both", False, False),
            ]:
                for rep in range(2):
                    row = {
                        "coder_id": coder_id,
                        "blind_item_id": f"{coder_id}_{source}_{quadrant}_{rep}",
                        "source_family": source,
                        "quadrant": quadrant,
                        "directive_flag": directive_flag,
                        "growth_flag": growth_flag,
                    }
                    for dimension in DIMENSIONS:
                        row[f"{dimension}_0_to_3"] = 0.0
                    row["directive_interpersonal_0_to_3"] = 2.0 if directive_flag else 0.0
                    row["redemption_growth_0_to_3"] = 2.0 if growth_flag else 0.0
                    rows.append(row)
    coded = add_action_growth_2x2_fused_scores(pd.DataFrame(rows))
    marginals = action_growth_2x2_source_adjusted_marginals(coded)
    interactions = action_growth_2x2_interaction_effects(coded)
    agreement = pd.DataFrame(
        [
            {"metric": "directive_interpersonal", "pearson_r": 1.0},
            {"metric": "redemption_growth", "pearson_r": 1.0},
            {"metric": "directive_growth_min_score", "pearson_r": 1.0},
        ]
    )
    summary = action_growth_2x2_acceptance_summary(
        marginals,
        interactions,
        agreement,
        marginal_threshold=0.5,
        fused_threshold=0.5,
        interaction_threshold=0.25,
    )
    assert summary["marginal_gate"].all()
    assert summary["interaction_gate"].all()
    assert summary["overall_decision"].iloc[0] == "supports_directive_growth_interaction"


def test_suica_construct_expansion_source_family_and_author_split_are_stable() -> None:
    assert suica_expansion_source_family("pandora_temporal") == "pandora"
    assert suica_expansion_source_family("essays_random") == "essays"
    assert suica_expansion_source_family("x_market_posts") == "x_market"
    frame = pd.DataFrame(
        {
            "source_family": ["pandora", "pandora", "essays"],
            "user_id": ["same_user", "same_user", "same_user"],
        }
    )
    split = assign_suica_expansion_author_split(frame, dev_share=0.5)
    assert split.iloc[0] == split.iloc[1]
    assert set(split).issubset({"development", "heldout"})


def test_suica_construct_expansion_builds_heldout_item_bank() -> None:
    anchors = synthetic_suica_anchor_rows()
    prepared = prepare_suica_expansion_anchor_frame(
        anchors,
        min_token_count=40,
        max_top_token_share=0.3,
        max_excerpt_chars=240,
        dev_share=0.5,
    )
    scored = add_suica_expansion_construct_scores(prepared, high_quantile=0.75, low_quantile=0.25)
    selected, gaps = select_expanded_item_bank(
        scored,
        EXPANSION_CONSTRUCT_SPECS,
        source_families=["pandora", "essays"],
        examples_per_source_role_pole=1,
        interaction_examples_per_source_role_cell=1,
        seed=3,
    )
    assert not selected.empty
    assert gaps["selection_complete"].all()
    coder, key, mask_audit = build_suica_expansion_blind_package(selected, seed=5)
    assert len(coder) == len(key)
    assert len(mask_audit) == len(key)
    assert key["sample_role"].nunique() == 2
    summary = suica_expansion_readiness_summary(key, gaps, min_unique_users=2, min_conditions=2)
    assert not summary.empty
    assert summary["construct_readiness_decision"].eq("ready_for_development_and_heldout_blind_coding").all()


def test_suica_construct_expansion_evaluator_accepts_expected_pattern() -> None:
    rows = []
    for coder_id in ["a", "b"]:
        for source in ["pandora", "essays"]:
            for construct_id, label, high_dim in [
                ("f05_novelty_play_core", "novelty-play core", "novelty_play"),
                ("f10_directive_action_core", "directive action core", "directive_interpersonal"),
            ]:
                for cell in ["high", "low"]:
                    for rep in range(3):
                        row = {
                            "coder_id": coder_id,
                            "blind_item_id": f"{coder_id}_{source}_{construct_id}_{cell}_{rep}",
                            "construct_id": construct_id,
                            "construct_label": label,
                            "construct_type": "pole_contrast",
                            "source_family": source,
                            "cell": cell,
                        }
                        for dimension in DIMENSIONS:
                            row[f"{dimension}_0_to_3"] = 0.0
                        row[f"{high_dim}_0_to_3"] = 2.0 if cell == "high" else 0.0
                        if construct_id == "f10_directive_action_core":
                            row["agency_0_to_3"] = 1.0 if cell == "high" else 0.0
                        rows.append(row)
            for cell, directive, growth in [
                ("directive_growth", 2.0, 2.0),
                ("directive_only", 2.0, 0.0),
                ("growth_only", 0.0, 2.0),
                ("low_both", 0.0, 0.0),
            ]:
                for rep in range(2):
                    row = {
                        "coder_id": coder_id,
                        "blind_item_id": f"{coder_id}_{source}_interaction_{cell}_{rep}",
                        "construct_id": "f10_directive_growth_interaction",
                        "construct_label": "directive-growth interaction",
                        "construct_type": "interaction_2x2",
                        "source_family": source,
                        "cell": cell,
                    }
                    for dimension in DIMENSIONS:
                        row[f"{dimension}_0_to_3"] = 0.0
                    row["directive_interpersonal_0_to_3"] = directive
                    row["redemption_growth_0_to_3"] = growth
                    rows.append(row)
    coded = add_suica_expansion_fused_scores(pd.DataFrame(rows))
    pole = suica_expansion_pole_separation(coded)
    source = suica_expansion_pole_source_adjusted(coded)
    pole_gate = suica_expansion_pole_expected_gate(pole, source, delta_threshold=0.3)
    marginals = suica_expansion_interaction_marginals(coded)
    interactions = suica_expansion_interaction_effects(coded)
    agreement = pd.DataFrame(
        [
            {"metric": "novelty_play", "pearson_r": 1.0},
            {"metric": "directive_interpersonal", "pearson_r": 1.0},
            {"metric": "redemption_growth", "pearson_r": 1.0},
            {"metric": "directive_growth_min_score", "pearson_r": 1.0},
        ]
    )
    summary = suica_expansion_acceptance_summary(
        pole_gate,
        marginals,
        interactions,
        agreement,
        marginal_threshold=0.5,
        fused_threshold=0.5,
        interaction_threshold=0.25,
        agreement_threshold=0.5,
    )
    assert summary["decision"].eq("pass_development_gate").all()


def test_suica_construct_expansion_evaluator_allows_no_interaction_subset() -> None:
    rows = []
    for coder_id in ["a", "b"]:
        for source in ["pandora", "essays"]:
            for cell in ["high", "low"]:
                row = {
                    "coder_id": coder_id,
                    "blind_item_id": f"{coder_id}_{source}_{cell}",
                    "construct_id": "f05_novelty_play_core",
                    "construct_label": "novelty-play core",
                    "construct_type": "pole_contrast",
                    "source_family": source,
                    "cell": cell,
                }
                for dimension in DIMENSIONS:
                    row[f"{dimension}_0_to_3"] = 0.0
                row["novelty_play_0_to_3"] = 2.0 if cell == "high" else 0.0
                rows.append(row)
    coded = add_suica_expansion_fused_scores(pd.DataFrame(rows))
    pole = suica_expansion_pole_separation(coded)
    source = suica_expansion_pole_source_adjusted(coded)
    pole_gate = suica_expansion_pole_expected_gate(pole, source, delta_threshold=0.3)
    marginals = suica_expansion_interaction_marginals(coded)
    interactions = suica_expansion_interaction_effects(coded)
    agreement = pd.DataFrame([{"metric": "novelty_play", "pearson_r": 1.0}])
    summary = suica_expansion_acceptance_summary(
        pole_gate,
        marginals,
        interactions,
        agreement,
        marginal_threshold=0.5,
        fused_threshold=0.5,
        interaction_threshold=0.25,
        agreement_threshold=0.5,
    )
    assert marginals.empty
    assert interactions.empty
    assert summary["construct_id"].tolist() == ["f05_novelty_play_core"]
    assert summary["decision"].iloc[0] == "pass_development_gate"


def test_suica_construct_expansion_evaluator_allows_interaction_only_subset() -> None:
    rows = []
    for coder_id in ["a", "b"]:
        for source in ["pandora", "essays"]:
            for cell, directive, growth in [
                ("directive_growth", 2.0, 2.0),
                ("directive_only", 2.0, 0.0),
                ("growth_only", 0.0, 2.0),
                ("low_both", 0.0, 0.0),
            ]:
                for rep in range(2):
                    row = {
                        "coder_id": coder_id,
                        "blind_item_id": f"{coder_id}_{source}_{cell}_{rep}",
                        "construct_id": "f10_directive_growth_interaction",
                        "construct_label": "directive-growth interaction",
                        "construct_type": "interaction_2x2",
                        "source_family": source,
                        "cell": cell,
                    }
                    for dimension in DIMENSIONS:
                        row[f"{dimension}_0_to_3"] = 0.0
                    row["directive_interpersonal_0_to_3"] = directive
                    row["redemption_growth_0_to_3"] = growth
                    rows.append(row)
    coded = add_suica_expansion_fused_scores(pd.DataFrame(rows))
    pole = suica_expansion_pole_separation(coded)
    source = suica_expansion_pole_source_adjusted(coded)
    pole_gate = suica_expansion_pole_expected_gate(pole, source, delta_threshold=0.3)
    marginals = suica_expansion_interaction_marginals(coded)
    interactions = suica_expansion_interaction_effects(coded)
    agreement = pd.DataFrame(
        [
            {"metric": "directive_interpersonal", "pearson_r": 1.0},
            {"metric": "redemption_growth", "pearson_r": 1.0},
            {"metric": "directive_growth_min_score", "pearson_r": 1.0},
        ]
    )
    summary = suica_expansion_acceptance_summary(
        pole_gate,
        marginals,
        interactions,
        agreement,
        marginal_threshold=0.5,
        fused_threshold=0.5,
        interaction_threshold=0.25,
        agreement_threshold=0.5,
    )
    assert pole.empty
    assert source.empty
    assert pole_gate.empty
    assert summary["construct_id"].tolist() == ["f10_directive_growth_interaction", "f10_directive_growth_interaction"]
    assert summary["decision"].eq("pass_development_gate").all()


def test_directive_growth_coupling_features_require_local_pairing() -> None:
    coupled = directive_growth_coupling_features("You should try to learn from this and get better.", window=8)
    separate = directive_growth_coupling_features(
        "You should try this now and follow the steps. The table is blue. Much later I learned from history.",
        window=4,
    )
    assert coupled["coupled_pair_count"] > 0
    assert coupled["same_sentence_pair_count"] > 0
    assert coupled["local_coupling_score"] > separate["local_coupling_score"]


def test_directive_growth_coupled_repair_selects_balanced_2x2_cells() -> None:
    anchors = synthetic_directive_growth_coupled_rows()
    prepared = prepare_directive_growth_coupled_frame(
        anchors,
        dev_share=0.5,
        min_token_count=40,
        max_top_token_share=0.3,
        max_excerpt_chars=240,
        coupling_window=10,
    )
    scored = add_directive_growth_coupled_cells(prepared, high_quantile=0.75, low_quantile=0.25)
    selected, gaps = select_directive_growth_coupled_items(
        scored,
        source_families=["pandora", "essays"],
        examples_per_source_role_cell=1,
        seed=9,
    )
    assert gaps["selection_complete"].all()
    counts = selected.groupby(["sample_role", "source_family", "cell"]).size()
    assert counts.nunique() == 1
    assert counts.iloc[0] == 1
    dg = selected.loc[selected["cell"].eq("directive_growth")]
    controls = selected.loc[~selected["cell"].eq("directive_growth")]
    assert dg["local_coupling_score"].min() > controls["local_coupling_score"].max()


def test_directive_growth_strict_features_exclude_instrumental_learning() -> None:
    redemptive = directive_growth_strict_coupling_features(
        "You should learn from your mistakes and work through the pain.",
        coupling_window=12,
        context_window=8,
    )
    instrumental = directive_growth_strict_coupling_features(
        "You should study for the test and learn the textbook before class.",
        coupling_window=12,
        context_window=8,
    )
    assert redemptive["strict_growth_term_count"] > 0
    assert redemptive["strict_redemptive_coupling_score"] > 0
    assert instrumental["strict_growth_term_count"] == 0
    assert instrumental["strict_redemptive_coupling_score"] == 0


def test_directive_growth_strict_repair_selects_balanced_2x2_cells() -> None:
    anchors = synthetic_directive_growth_strict_rows()
    prepared = prepare_directive_growth_strict_frame(
        anchors,
        dev_share=0.5,
        min_token_count=40,
        max_top_token_share=0.3,
        max_excerpt_chars=320,
        coupling_window=12,
        context_window=8,
    )
    scored = add_directive_growth_strict_cells(prepared, high_quantile=0.75, low_quantile=0.25)
    selected, gaps = select_directive_growth_strict_items(
        scored,
        source_families=["pandora", "essays"],
        examples_per_source_role_cell=1,
        seed=17,
    )
    assert gaps["selection_complete"].all()
    counts = selected.groupby(["sample_role", "source_family", "cell"]).size()
    assert counts.nunique() == 1
    assert counts.iloc[0] == 1
    dg = selected.loc[selected["cell"].eq("directive_growth")]
    directive_only = selected.loc[selected["cell"].eq("directive_only")]
    growth_only = selected.loc[selected["cell"].eq("growth_only")]
    assert dg["strict_redemptive_coupling_score"].min() > directive_only["strict_redemptive_coupling_score"].max()
    assert dg["strict_redemptive_coupling_score"].min() > growth_only["strict_redemptive_coupling_score"].max()
    assert directive_only["instrumental_context_count"].min() > 0


def test_adversity_recovery_features_exclude_instrumental_learning() -> None:
    redemptive = adversity_recovery_features(
        "I worked through the pain, recovered from the mistake, and became a better person.",
        context_window=8,
    )
    instrumental = adversity_recovery_features(
        "I studied the textbook for the test and learned the class material.",
        context_window=8,
    )
    assert redemptive["ar_strict_growth_term_count"] > 0
    assert redemptive["adversity_recovery_score"] > 0
    assert instrumental["ar_strict_growth_term_count"] == 0
    assert instrumental["adversity_recovery_score"] == 0


def test_adversity_recovery_package_selects_balanced_high_low_poles() -> None:
    anchors = synthetic_directive_growth_strict_rows()
    prepared = prepare_adversity_recovery_frame(
        anchors,
        dev_share=0.5,
        min_token_count=40,
        max_top_token_share=0.3,
        max_excerpt_chars=320,
        context_window=8,
    )
    scored = add_adversity_recovery_scores(prepared, high_quantile=0.75, low_quantile=0.25)
    selected, gaps = select_adversity_recovery_items(
        scored,
        source_families=["pandora", "essays"],
        examples_per_source_role_pole=1,
        seed=23,
    )
    assert gaps["selection_complete"].all()
    counts = selected.groupby(["sample_role", "source_family", "cell"]).size()
    assert counts.nunique() == 1
    assert counts.iloc[0] == 1
    high = selected.loc[selected["cell"].eq("high")]
    low = selected.loc[selected["cell"].eq("low")]
    assert high["adversity_recovery_score"].min() > low["adversity_recovery_score"].max()


def test_suica_construct_evaluator_accepts_adversity_recovery_core_mapping() -> None:
    rows = []
    for coder_id in ["a", "b"]:
        for source in ["pandora", "essays"]:
            for cell, growth in [("high", 2.5), ("low", 0.5)]:
                for rep in range(2):
                    row = {
                        "coder_id": coder_id,
                        "blind_item_id": f"{coder_id}_{source}_{cell}_{rep}",
                        "construct_id": "suica_adversity_recovery_core",
                        "construct_label": "adversity-recovery core",
                        "construct_type": "pole_contrast",
                        "source_family": source,
                        "cell": cell,
                    }
                    for dimension in DIMENSIONS:
                        row[f"{dimension}_0_to_3"] = 0.0
                    row["redemption_growth_0_to_3"] = growth
                    rows.append(row)
    coded = add_suica_expansion_fused_scores(pd.DataFrame(rows))
    pole = suica_expansion_pole_separation(coded)
    source = suica_expansion_pole_source_adjusted(coded)
    pole_gate = suica_expansion_pole_expected_gate(pole, source, delta_threshold=0.3)
    agreement = pd.DataFrame([{"metric": "redemption_growth", "pearson_r": 1.0}])
    summary = suica_expansion_acceptance_summary(
        pole_gate,
        pd.DataFrame(columns=["coder_id"]),
        pd.DataFrame(columns=["coder_id"]),
        agreement,
        marginal_threshold=0.5,
        fused_threshold=0.5,
        interaction_threshold=0.25,
        agreement_threshold=0.5,
    )
    row = summary.loc[summary["construct_id"].eq("suica_adversity_recovery_core")].iloc[0]
    assert row["decision"] == "pass_development_gate"
    assert row["expected_dimensions"] == "redemption_growth"


def test_suica_validated_construct_manual_lists_three_provisional_components() -> None:
    construct_ids = {spec["construct_id"] for spec in VALIDATED_MANUAL_CONSTRUCTS}
    assert construct_ids == {
        "f05_novelty_play_core",
        "f10_directive_action_core",
        "suica_adversity_recovery_core",
    }
    expected = {spec["construct_id"]: spec["expected_dimension"] for spec in VALIDATED_MANUAL_CONSTRUCTS}
    assert expected["f05_novelty_play_core"] == "novelty_play"
    assert expected["f10_directive_action_core"] == "directive_interpersonal"
    assert expected["suica_adversity_recovery_core"] == "redemption_growth"


def test_suica_three_construct_reliability_readiness_requires_source_cell_balance() -> None:
    rows = []
    for construct_id in ["f05_novelty_play_core", "f10_directive_action_core", "suica_adversity_recovery_core"]:
        for role in ["development", "heldout"]:
            for source in ["pandora", "essays"]:
                for cell in ["high", "low"]:
                    for idx in range(6):
                        rows.append(
                            {
                                "construct_id": construct_id,
                                "sample_role": role,
                                "source_family": source,
                                "cell": cell,
                                "blind_item_id": f"{construct_id}_{role}_{source}_{cell}_{idx}",
                                "user_id": f"{source}_{role}_{cell}_{idx}",
                            }
                        )
    key = pd.DataFrame(rows)
    readiness = three_construct_readiness_summary(key)
    assert readiness["ready_for_reliability_coding"].all()
    assert readiness["min_items_per_source_cell"].min() == 6
