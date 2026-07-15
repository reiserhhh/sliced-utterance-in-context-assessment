from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_v7_condition_opportunity import (
    OperatorData,
    _author_cluster_r2,
    _build_matched_strata,
    _component_auc,
    _component_frame,
    _decision,
    _matched_stratified_metric,
)
from suica_core.v7_condition_opportunity import fit_comment_context_encoder, fit_matrix_scaler, global_r2, transform_comment_context


def _comments() -> pd.DataFrame:
    return pd.DataFrame({
        "user_id": ["discovery", "discovery", "confirmation", "confirmation"],
        "text": [
            "A sufficient discovery example with words and punctuation.",
            "Another discovery example with enough text to inspect.",
            "Confirmation uses an unseen community but still has content.",
            "A second confirmation record also contains a few words.",
        ],
        "order": [1_700_000_000, 1_700_086_400, 1_700_172_800, 1_700_259_200],
        "condition": ["known_a", "known_b", "unseen", "unseen"],
        "split": ["discovery", "discovery", "confirmation", "confirmation"],
    })


def test_comment_context_vocabulary_is_discovery_fitted_and_unseen_condition_is_other() -> None:
    comments = _comments()
    encoder = fit_comment_context_encoder(comments, discovery_user_ids=["discovery"], max_conditions=2)
    transformed = transform_comment_context(comments, encoder=encoder)
    assert set(encoder.condition_vocabulary) == {"known_a", "known_b"}
    confirmation = transformed.loc[transformed["user_id"].eq("confirmation")]
    assert confirmation["ctx::condition_other"].eq(1.0).all()
    assert confirmation["length_bin"].between(0, 9).all()


def test_component_frame_has_exact_t_equals_k_plus_a_identity() -> None:
    frame = pd.DataFrame({
        "user_id": ["u1", "u1", "u2", "u2"],
        "split": ["confirmation"] * 4,
    })
    values = np.array([[1.0, 2.0], [3.0, 4.0], [2.0, 0.0], [0.0, 2.0]])
    prediction = np.array([[0.5, 1.0], [1.5, 2.0], [1.0, 0.0], [0.0, 1.0]])
    data = OperatorData(frame=frame, embeddings=values, contexts={"primary": np.ones((4, 1)), "format_enriched": np.ones((4, 1))})
    result = _component_frame(
        data,
        prediction,
        baseline_y=values.mean(axis=0),
        baseline_k=prediction.mean(axis=0),
        baseline_a=(values - prediction).mean(axis=0),
    )
    assert result["identity_max_abs_error"].max() < 1e-12


def test_component_auc_uses_broken_author_pairing_not_reordered_own_distances() -> None:
    rng = np.random.default_rng(7)
    users = [f"u{index:02d}" for index in range(48)]
    left_values = rng.normal(size=(len(users), 5))
    right_values = left_values + rng.normal(scale=0.08, size=left_values.shape)
    def frame(values: np.ndarray) -> pd.DataFrame:
        output = pd.DataFrame({"user_id": users, "split": "confirmation"})
        for index in range(values.shape[1]):
            output[f"T_{index:02d}"] = values[:, index]
        return output
    result = _component_auc(
        frame(left_values), frame(right_values), users=users, prefix="T",
        seed=11, bootstrap_iterations=99, permutation_iterations=99, draws=8,
    )
    assert result["auc"] > 0.9
    assert result["permutation_p"] < 0.05


def test_author_cluster_r2_interval_contains_full_sample_estimate() -> None:
    rng = np.random.default_rng(13)
    users = np.repeat([f"u{index}" for index in range(16)], 3)
    values = rng.normal(size=(len(users), 3))
    prediction = values + rng.normal(scale=0.2, size=values.shape)
    data = OperatorData(
        frame=pd.DataFrame({"user_id": users, "split": "confirmation"}),
        embeddings=values,
        contexts={"primary": np.ones((len(users), 1)), "format_enriched": np.ones((len(users), 1))},
    )
    low, high = _author_cluster_r2(data, prediction, seed=17, repetitions=199)
    observed = global_r2(values, prediction)
    assert low <= observed <= high


def test_decision_does_not_conflate_selection_recurrence_with_context_transport() -> None:
    primary = {
        "total_auc": 0.80,
        "total_auc_ci_low": 0.70,
        "total_auc_q": 0.01,
        "selection_gain_ci_low": 0.10,
        "selection_gain_q": 0.01,
        "context_r2": 0.005,
        "context_r2_ci_low": 0.001,
        "context_r2_q": 0.01,
        "k_to_t_r2": 0.021,
        "k_to_t_ci_low": -0.01,
        "k_to_t_q": 0.01,
        "partial_auc": 0.70,
        "partial_auc_ci_low": 0.60,
        "partial_auc_q": 0.01,
        "partial_null_exchangeable": True,
    }
    decision, _ = _decision(
        primary,
        matched_available=True,
        config={"screen_thresholds": {"minimum_auc": 0.55, "minimum_context_r2": 0.02, "alpha": 0.05}},
    )
    assert decision == "TOTAL_SELECTION_AND_PARTIAL_STRUCTURE_SUPPORTED_WITH_UNRESOLVED_CONTEXT_TRANSPORT"


def _three_strata() -> tuple[np.ndarray, list[set[str]], list[str]]:
    metadata = np.asarray([[group * 10.0 + offset * 0.01] for group in range(3) for offset in range(4)])
    condition_sets = [{f"c{group}"} for group in range(3) for _ in range(4)]
    exact_classes = [f"class_{group}" for group in range(3) for _ in range(4)]
    return metadata, condition_sets, exact_classes


def test_matched_strata_enforce_pairwise_recorded_condition_balance() -> None:
    metadata, condition_sets, exact_classes = _three_strata()
    strata = _build_matched_strata(
        metadata,
        condition_sets,
        exact_classes,
        metadata_scaler=fit_matrix_scaler(metadata),
        numeric_caliper=0.10,
        minimum_jaccard=1.0,
        min_size=4,
        max_size=4,
    )
    used = np.concatenate(strata.groups)
    assert len(strata.groups) == 3
    assert len(np.unique(used)) == len(used) == 12
    for group in strata.groups:
        mask = ~np.eye(len(group), dtype=bool)
        numeric = strata.numeric_distance[np.ix_(group, group)]
        jaccard = strata.jaccard[np.ix_(group, group)]
        assert np.all(numeric[mask] <= strata.numeric_caliper)
        assert np.all(jaccard[mask] >= strata.minimum_jaccard)
        assert len({strata.exact_class[index] for index in group}) == 1


def test_stratified_permutation_null_recomputes_linked_and_stranger_ranks() -> None:
    rng = np.random.default_rng(31)
    left = rng.normal(size=(12, 3))
    right = rng.normal(size=(12, 3))
    metadata, condition_sets, exact_classes = _three_strata()
    strata = _build_matched_strata(
        metadata,
        condition_sets,
        exact_classes,
        metadata_scaler=fit_matrix_scaler(metadata),
        numeric_caliper=0.10,
        minimum_jaccard=1.0,
        min_size=4,
        max_size=4,
    )
    metric, null, _, balance = _matched_stratified_metric(
        left,
        right,
        strata,
        bootstrap_iterations=99,
        permutation_iterations=199,
        seed=33,
    )
    # Each null permutes B identities within a stratum and recomputes both the
    # linked and stranger rank. Its expected statistic is one half.
    assert abs(float(null["conditional_rank_auc"].mean()) - 0.5) < 0.06
    assert 0.0 <= metric["auc"] <= 1.0
    assert 0.0 <= metric["permutation_p"] <= 1.0
    assert balance["all_numeric_pairs_within_caliper"].all()
    assert balance["all_condition_pairs_within_caliper"].all()


def test_decision_refuses_a_matched_screen_without_exchangeable_null() -> None:
    primary = {
        "total_auc": 0.80,
        "total_auc_ci_low": 0.70,
        "total_auc_q": 0.01,
        "selection_gain_ci_low": 0.10,
        "selection_gain_q": 0.01,
        "context_r2": 0.005,
        "context_r2_ci_low": 0.001,
        "context_r2_q": 0.01,
        "k_to_t_r2": 0.021,
        "k_to_t_ci_low": -0.01,
        "k_to_t_q": 0.01,
        "partial_auc": 0.70,
        "partial_auc_ci_low": 0.60,
        "partial_auc_q": 0.01,
        "partial_null_exchangeable": False,
    }
    decision, _ = _decision(
        primary,
        matched_available=True,
        config={"screen_thresholds": {"minimum_auc": 0.55, "minimum_context_r2": 0.02, "alpha": 0.05}},
    )
    assert decision == "REFUSE_INVALID_MATCHED_NULL"
