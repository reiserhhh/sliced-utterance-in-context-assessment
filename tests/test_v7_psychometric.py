from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from sklearn.decomposition import FactorAnalysis
from tempfile import TemporaryDirectory

from scripts.run_suica_v7_operator_smoke import _status_for_base, _summary_row

from suica_core.v7_observations import ObservationSpec
from suica_core.v7_psychometric import (
    FactorBundle,
    RepresentationSpec,
    _fa_posterior_scores,
    author_features_from_embeddings,
    combine_nested_author_features,
    confirmation_subspace_similarity,
    factor_content_sha256,
    fit_factor_bundle,
    read_factor_bundle,
    score_author_features,
    technical_view_consistency,
    unit_bootstrap_sem,
    validate_factor_bundle_payload,
)


def _unit_observations(seed: int = 3) -> tuple[pd.DataFrame, np.ndarray]:
    rng = np.random.default_rng(seed)
    rows = []
    vectors = []
    for user in range(90):
        split = "discovery" if user < 52 else "calibration" if user < 70 else "confirmation"
        latent = rng.normal(size=2)
        for unit in range(8):
            rows.append({
                "user_id": f"u{user:03d}", "split": split, "unit_id": f"u{user}:{unit}",
                "unit_index": unit, "token_count": 30 + unit, "text": "placeholder",
            })
            vectors.append(np.array([
                latent[0] + rng.normal(scale=0.20),
                0.7 * latent[0] + rng.normal(scale=0.20),
                latent[1] + rng.normal(scale=0.20),
                0.8 * latent[1] + rng.normal(scale=0.20),
            ]))
    return pd.DataFrame(rows), np.vstack(vectors)


def test_posterior_formula_matches_sklearn_factor_analysis_transform() -> None:
    rng = np.random.default_rng(17)
    values = rng.normal(size=(200, 7))
    estimator = FactorAnalysis(n_components=3, random_state=4).fit(values)
    expected = estimator.transform(values)
    actual = _fa_posterior_scores(
        values, fa_mean=estimator.mean_, loadings=estimator.components_, noise_variance=estimator.noise_variance_
    )
    assert np.allclose(actual, expected, atol=1e-8)


def test_frozen_bundle_scores_unseen_authors_without_refitting() -> None:
    observations, embeddings = _unit_observations()
    features = author_features_from_embeddings(observations, embeddings)
    spec = RepresentationSpec(svd_dimensions=4, factor_count=2, seed=2)
    fitted = fit_factor_bundle(
        features,
        operator=ObservationSpec(name="native", kind="native").to_dict(),
        representation=spec,
        runtime_artifact={"test": True},
        min_units_for_score=2,
        seed=2,
    )
    snapshot = fitted.bundle.to_dict()
    confirmation = features.loc[features["split"].eq("confirmation")]
    scores = score_author_features(fitted.bundle, confirmation)
    assert scores["score_status"].eq("SCORED").all()
    assert any(column.startswith("SU7-FC-") for column in scores)
    assert fitted.bundle.to_dict() == snapshot
    sem = unit_bootstrap_sem(observations, embeddings, fitted.bundle, repetitions=8, seed=4)
    assert sem["sem_status"].eq("BOOTSTRAP_SEM").all()
    consistency = technical_view_consistency(observations, embeddings, fitted.bundle)
    assert consistency["correlation"].notna().all()
    transport = confirmation_subspace_similarity(fitted.bundle, features, seed=5)
    assert transport["n_confirmation"] == 20


def test_factor_bundle_json_round_trip_preserves_scores() -> None:
    observations, embeddings = _unit_observations(seed=14)
    features = author_features_from_embeddings(observations, embeddings)
    fitted = fit_factor_bundle(
        features,
        operator=ObservationSpec(name="native", kind="native").to_dict(),
        representation=RepresentationSpec(svd_dimensions=4, factor_count=2),
        runtime_artifact={"test": True}, min_units_for_score=2, seed=8,
    )
    with TemporaryDirectory() as directory:
        path = f"{directory}/bundle.json"
        fitted.bundle.write_json(path)
        restored = read_factor_bundle(path)
        original = score_author_features(fitted.bundle, features)
        replay = score_author_features(restored, features)
    factor_columns = [column for column in original if column.startswith("SU7-FC-")]
    assert np.allclose(original[factor_columns], replay[factor_columns])


def test_factor_bundle_validator_rejects_schema_drift_and_dimension_mismatch() -> None:
    observations, embeddings = _unit_observations(seed=22)
    features = author_features_from_embeddings(observations, embeddings)
    fitted = fit_factor_bundle(
        features,
        operator=ObservationSpec(name="native", kind="native").to_dict(),
        representation=RepresentationSpec(svd_dimensions=4, factor_count=2),
        runtime_artifact={"test": True}, min_units_for_score=2, seed=9,
    )
    payload = fitted.bundle.to_dict()
    validate_factor_bundle_payload(payload)
    payload["feature_scale"] = payload["feature_scale"][:-1]
    try:
        validate_factor_bundle_payload(payload)
    except ValueError as error:
        assert "feature_scale length" in str(error)
    else:
        raise AssertionError("dimension-mismatched bundle was accepted")


def _fitted_bundle(seed: int = 33) -> FactorBundle:
    observations, embeddings = _unit_observations(seed=seed)
    features = author_features_from_embeddings(observations, embeddings)
    fitted = fit_factor_bundle(
        features,
        operator=ObservationSpec(name="native", kind="native").to_dict(),
        representation=RepresentationSpec(svd_dimensions=4, factor_count=2),
        runtime_artifact={"test": True}, min_units_for_score=2, seed=seed,
    )
    return fitted.bundle


def test_factor_content_hash_binds_score_definition_and_rejects_tampering() -> None:
    bundle = _fitted_bundle()
    payload = bundle.to_dict()
    assert isinstance(payload["factor_content_sha256"], str) and payload["factor_content_sha256"]
    assert validate_factor_bundle_payload(payload) == {"tamper_binding": "VERIFIED"}
    # Mirrors tests/test_v7_geometry.py: mutate one score-defining value.
    payload["factor_loadings"][0][0] += 0.1
    with pytest.raises(ValueError, match="does not match"):
        FactorBundle.from_dict(payload)
    # Norms and operator metadata are also hash-bound.
    for field, mutate in (
        ("norm_mean", lambda p: p["norm_mean"].__setitem__(0, p["norm_mean"][0] + 0.5)),
        ("operator", lambda p: p["operator"].update(name="swapped")),
    ):
        fresh = _fitted_bundle().to_dict()
        mutate(fresh)
        with pytest.raises(ValueError, match="does not match"):
            validate_factor_bundle_payload(fresh)


def test_pre_binding_factor_bundle_without_hash_still_validates() -> None:
    bundle = _fitted_bundle(seed=34)
    payload = bundle.to_dict()
    del payload["factor_content_sha256"]
    # Stored artifacts predating tamper binding must keep loading.
    assert validate_factor_bundle_payload(payload) == {"tamper_binding": "ABSENT_PRE_BINDING_BUNDLE"}
    restored = FactorBundle.from_dict(payload)
    assert restored.factor_content_sha256 is None
    # The recomputed hash of the untampered content matches the fitted one.
    assert factor_content_sha256(payload) == bundle.factor_content_sha256


def test_unit_bootstrap_sem_rejects_non_default_index() -> None:
    observations, embeddings = _unit_observations()
    bundle = _fitted_bundle(seed=35)
    shifted = observations.copy()
    shifted.index = shifted.index + 5
    with pytest.raises(ValueError, match="RangeIndex"):
        unit_bootstrap_sem(shifted, embeddings, bundle, repetitions=2, seed=4)


def test_one_unit_operator_reports_missing_sem_instead_of_zero() -> None:
    observations, embeddings = _unit_observations()
    first = observations.groupby("user_id", observed=True).head(1).reset_index(drop=True)
    first_indices = observations.groupby("user_id", observed=True).head(1).index.to_numpy(int)
    features = author_features_from_embeddings(first, embeddings[first_indices])
    fitted = fit_factor_bundle(
        features,
        operator=ObservationSpec(name="whole", kind="whole").to_dict(),
        representation=RepresentationSpec(svd_dimensions=4, factor_count=2),
        runtime_artifact={"test": True},
        min_units_for_score=1,
        seed=7,
    )
    sem = unit_bootstrap_sem(first, embeddings[first_indices], fitted.bundle, repetitions=8, seed=4)
    assert sem["sem_status"].eq("SEM_UNAVAILABLE_WITH_ONE_UNIT").all()


def test_nested_feature_join_keeps_source_provenance() -> None:
    observations, embeddings = _unit_observations()
    native = author_features_from_embeddings(observations, embeddings)
    fixed = author_features_from_embeddings(observations, embeddings * 0.8, prefix="fixed_")
    nested = combine_nested_author_features({"native": native, "fixed": fixed}, ("native", "fixed"))
    assert "native::mean::svd_000" in nested
    assert "fixed::fixed_mean::svd_000" in nested
    assert nested["n_units"].min() == 8


def test_runner_status_handles_empty_object_consistency_column() -> None:
    scores = pd.DataFrame({"split": ["confirmation"], "score_status": ["SCORED"]})
    sem = pd.DataFrame({"sem_status": ["BOOTSTRAP_SEM"]})
    status, _ = _status_for_base(sem, pd.DataFrame({"correlation": pd.Series([], dtype=object)}), scores)
    assert status == "L1_POPULATION_STRUCTURE"


def test_summary_does_not_count_sem_columns_as_factors() -> None:
    scores = pd.DataFrame({
        "user_id": ["u"], "split": ["confirmation"], "n_units": [3], "n_tokens": [100], "score_status": ["SCORED"],
        "SU7-FC-0001@v1": [0.2], "SU7-FC-0001@v1_z": [0.1], "SU7-FC-0001@v1_sem": [0.03],
    })
    row = _summary_row(
        spec=ObservationSpec(name="native", kind="native"),
        features=pd.DataFrame({"user_id": ["u"], "split": ["confirmation"], "n_units": [3], "n_tokens": [100], "mean::x": [0.1]}),
        scores=scores, sem=pd.DataFrame({"SU7-FC-0001@v1_sem": [0.03]}),
        consistency=pd.DataFrame({"correlation": [0.2]}), transport={}, status="L2_SCOREABLE_CANDIDATE", note="test",
    )
    assert row["n_factors"] == 1
