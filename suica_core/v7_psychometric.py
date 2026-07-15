"""Frozen author-score construction for the label-free SUICA V7 pipeline.

This module deliberately separates three things that are often conflated in
text work: representation fitting, author aggregation, and factor scoring.
Only discovery authors fit these objects.  Calibration authors define norms;
confirmation authors are transformed by the frozen objects without refitting.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.linalg import subspace_angles
from sklearn.decomposition import FactorAnalysis, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer


@dataclass(frozen=True)
class RepresentationSpec:
    """Label-free unit representation settings frozen with an operator."""

    max_features: int = 5000
    ngram_min: int = 1
    ngram_max: int = 2
    svd_dimensions: int = 24
    factor_count: int = 4
    seed: int = 20260714

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RepresentationRuntime:
    """Fitted text transform.  Persisted locally beside a JSON factor bundle."""

    vectorizer: TfidfVectorizer
    svd: TruncatedSVD
    spec: RepresentationSpec

    def transform(self, texts: pd.Series | list[str]) -> np.ndarray:
        """Transform new text using only discovery-fitted vocabulary and SVD."""
        tfidf = self.vectorizer.transform(pd.Series(texts).fillna("").astype(str))
        return self.svd.transform(tfidf)


@dataclass
class FactorBundle:
    """JSON-serializable V7 factor bundle with frozen scoring and norms."""

    bundle_id: str
    version: str
    operator: dict[str, Any]
    representation: dict[str, Any]
    feature_names: list[str]
    feature_impute: list[float]
    feature_center: list[float]
    feature_scale: list[float]
    fa_mean: list[float]
    factor_loadings: list[list[float]]
    noise_variance: list[float]
    factor_signs: list[float]
    norm_mean: list[float]
    norm_scale: list[float]
    norm_quantiles: dict[str, list[float]]
    support_rule: dict[str, Any]
    runtime_artifact: dict[str, Any]
    reference_population: dict[str, Any]
    claim_boundary: str
    created_utc: str

    def to_dict(self) -> dict[str, Any]:
        """Return the manifest intentionally required for a reproducible score."""
        return asdict(self)

    def write_json(self, path: str | Path) -> None:
        """Write a human-auditable bundle manifest without source text."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = self.to_dict()
        validate_factor_bundle_payload(payload)
        destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "FactorBundle":
        """Reconstruct a frozen factor bundle without accessing its fit data."""
        validate_factor_bundle_payload(payload)
        return cls(**payload)


@dataclass
class FittedOperator:
    """In-memory runtime required to score a single observation operator."""

    bundle: FactorBundle
    representation: RepresentationRuntime | None
    feature_columns: list[str]


_FACTOR_BUNDLE_FIELDS = {
    "bundle_id", "version", "operator", "representation", "feature_names",
    "feature_impute", "feature_center", "feature_scale", "fa_mean",
    "factor_loadings", "noise_variance", "factor_signs", "norm_mean",
    "norm_scale", "norm_quantiles", "support_rule", "runtime_artifact",
    "reference_population", "claim_boundary", "created_utc",
}


def _finite_vector(value: Any, *, name: str, length: int | None = None, positive: bool = False) -> np.ndarray:
    """Validate one JSON-compatible finite numeric vector with a clear error."""
    vector = np.asarray(value, dtype=float)
    if vector.ndim != 1:
        raise ValueError(f"Factor bundle {name} must be a one-dimensional numeric vector.")
    if length is not None and len(vector) != int(length):
        raise ValueError(f"Factor bundle {name} length {len(vector)} does not match expected {length}.")
    if not np.isfinite(vector).all():
        raise ValueError(f"Factor bundle {name} contains non-finite values.")
    if positive and not np.all(vector > 0.0):
        raise ValueError(f"Factor bundle {name} must be strictly positive.")
    return vector


def validate_factor_bundle_payload(payload: dict[str, Any]) -> None:
    """Validate the flat on-disk V7 factor-bundle contract without refitting.

    The project schema originally described a nested prototype that the actual
    runtime never emitted.  This native validator is deliberately dependency
    free and enforces the serialized runtime contract used by scoring.
    """
    if not isinstance(payload, dict):
        raise ValueError("Factor bundle payload must be an object.")
    missing = sorted(_FACTOR_BUNDLE_FIELDS.difference(payload))
    unknown = sorted(set(payload).difference(_FACTOR_BUNDLE_FIELDS))
    if missing:
        raise ValueError(f"Factor bundle missing required fields: {', '.join(missing)}")
    if unknown:
        raise ValueError(f"Factor bundle has unsupported fields: {', '.join(unknown)}")
    for field in ("bundle_id", "version", "claim_boundary", "created_utc"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise ValueError(f"Factor bundle {field} must be a non-empty string.")
    for field in ("operator", "representation", "support_rule", "runtime_artifact", "reference_population"):
        if not isinstance(payload[field], dict) or not payload[field]:
            raise ValueError(f"Factor bundle {field} must be a non-empty object.")
    feature_names = payload["feature_names"]
    if not isinstance(feature_names, list) or not feature_names or not all(isinstance(value, str) and value for value in feature_names):
        raise ValueError("Factor bundle feature_names must be a non-empty string list.")
    if len(set(feature_names)) != len(feature_names):
        raise ValueError("Factor bundle feature_names must be unique.")
    n_features = len(feature_names)
    _finite_vector(payload["feature_impute"], name="feature_impute", length=n_features)
    _finite_vector(payload["feature_center"], name="feature_center", length=n_features)
    _finite_vector(payload["feature_scale"], name="feature_scale", length=n_features, positive=True)
    _finite_vector(payload["fa_mean"], name="fa_mean", length=n_features)
    _finite_vector(payload["noise_variance"], name="noise_variance", length=n_features, positive=True)
    loadings = np.asarray(payload["factor_loadings"], dtype=float)
    if loadings.ndim != 2 or loadings.shape[0] < 1 or loadings.shape[1] != n_features or not np.isfinite(loadings).all():
        raise ValueError("Factor bundle factor_loadings must be finite [factor, feature] values.")
    n_factors = int(loadings.shape[0])
    _finite_vector(payload["factor_signs"], name="factor_signs", length=n_factors)
    _finite_vector(payload["norm_mean"], name="norm_mean", length=n_factors)
    _finite_vector(payload["norm_scale"], name="norm_scale", length=n_factors, positive=True)
    quantiles = payload["norm_quantiles"]
    if not isinstance(quantiles, dict) or set(quantiles) != {f"factor_{index + 1:02d}" for index in range(n_factors)}:
        raise ValueError("Factor bundle norm_quantiles must contain exactly one vector per factor.")
    for key, values in quantiles.items():
        _finite_vector(values, name=f"norm_quantiles.{key}")


def _hash_bundle_id(operator_name: str, feature_names: list[str], seed: int) -> str:
    token = f"{operator_name}|{seed}|{'|'.join(feature_names)}".encode("utf-8")
    return f"SU7-{operator_name.upper()}-{hashlib.sha256(token).hexdigest()[:10]}"


def _safe_scale(values: np.ndarray) -> np.ndarray:
    scale = np.nanstd(values, axis=0, ddof=0)
    return np.where(np.isfinite(scale) & (scale > 1e-9), scale, 1.0)


def _fa_posterior_scores(
    standardized_features: np.ndarray,
    *,
    fa_mean: np.ndarray,
    loadings: np.ndarray,
    noise_variance: np.ndarray,
) -> np.ndarray:
    r"""Calculate sklearn FactorAnalysis posterior means from frozen parameters.

    `loadings` has shape `(n_factors, n_features)`.  This explicit formula is
    included so a JSON bundle can be audited independently of a fitted Python
    estimator:

    \[
      E[z\mid x] = (x-\mu)\Psi^{-1}\Lambda^T
      (I+\Lambda\Psi^{-1}\Lambda^T)^{-1}.
    \]
    """
    x = np.asarray(standardized_features, dtype=float) - np.asarray(fa_mean, dtype=float)
    w = np.asarray(loadings, dtype=float)
    psi = np.maximum(np.asarray(noise_variance, dtype=float), 1e-12)
    weighted = w / psi[None, :]
    posterior_cov = np.linalg.inv(np.eye(w.shape[0]) + weighted @ w.T)
    return x @ weighted.T @ posterior_cov


def fit_representation(observations: pd.DataFrame, spec: RepresentationSpec) -> RepresentationRuntime:
    """Fit TF-IDF and SVD on discovery observations only."""
    if observations.empty:
        raise ValueError("Cannot fit a V7 representation on zero discovery observations.")
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        analyzer="word",
        ngram_range=(spec.ngram_min, spec.ngram_max),
        max_features=spec.max_features,
        min_df=1,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(observations["text"].fillna("").astype(str))
    max_components = min(matrix.shape[0] - 1, matrix.shape[1] - 1, spec.svd_dimensions)
    if max_components < 2:
        raise ValueError(
            f"Insufficient discovery text rank for V7 SVD: matrix={matrix.shape}, usable={max_components}."
        )
    svd = TruncatedSVD(n_components=int(max_components), random_state=spec.seed)
    svd.fit(matrix)
    return RepresentationRuntime(vectorizer=vectorizer, svd=svd, spec=spec)


def author_features_from_embeddings(
    observations: pd.DataFrame,
    embeddings: np.ndarray,
    *,
    prefix: str = "",
) -> pd.DataFrame:
    """Aggregate repeated unit vectors into mean/std author measurement inputs."""
    if len(observations) != len(embeddings):
        raise ValueError("Observation/embedding row counts differ.")
    if observations.empty:
        return pd.DataFrame(columns=["user_id", "split", "n_units", "n_tokens"])
    dim = int(embeddings.shape[1])
    frame = observations[["user_id", "split", "token_count"]].copy().reset_index(drop=True)
    for column in range(dim):
        frame[f"_embedding_{column}"] = embeddings[:, column]
    output: list[dict[str, Any]] = []
    embedding_columns = [f"_embedding_{column}" for column in range(dim)]
    for (user_id, split), group in frame.groupby(["user_id", "split"], observed=True, sort=False):
        values = group[embedding_columns].to_numpy(float)
        row: dict[str, Any] = {
            "user_id": str(user_id),
            "split": str(split),
            "n_units": int(len(group)),
            "n_tokens": int(group["token_count"].sum()),
        }
        mean = np.mean(values, axis=0)
        std = np.std(values, axis=0, ddof=0)
        for index in range(dim):
            row[f"{prefix}mean::svd_{index:03d}"] = float(mean[index])
            row[f"{prefix}std::svd_{index:03d}"] = float(std[index])
        output.append(row)
    return pd.DataFrame(output)


def combine_nested_author_features(
    sources: dict[str, pd.DataFrame],
    members: tuple[str, ...],
) -> pd.DataFrame:
    """Build a nested operator by joining already-frozen base author features.

    Nested aggregation does not re-read raw text.  It combines the feature
    views produced by named base operators, retaining their provenance through
    column prefixes.
    """
    if not members:
        raise ValueError("A nested V7 operator needs at least one base member.")
    output: pd.DataFrame | None = None
    support_columns: list[str] = []
    for member in members:
        if member not in sources:
            raise ValueError(f"Nested operator requires missing base member: {member}")
        source = sources[member].copy()
        feature_columns = [column for column in source if "::" in column]
        renamed = source[["user_id", "split", "n_units", "n_tokens", *feature_columns]].rename(
            columns={
                "n_units": f"n_units::{member}",
                "n_tokens": f"n_tokens::{member}",
                **{column: f"{member}::{column}" for column in feature_columns},
            }
        )
        support_columns.append(f"n_units::{member}")
        output = renamed if output is None else output.merge(renamed, on=["user_id", "split"], how="inner")
    assert output is not None
    output["n_units"] = output[support_columns].max(axis=1).astype(int)
    token_columns = [column for column in output if column.startswith("n_tokens::")]
    output["n_tokens"] = output[token_columns].max(axis=1).astype(int)
    return output


def _numeric_feature_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if "::" in column and not column.startswith(("n_units::", "n_tokens::"))]


def fit_factor_bundle(
    author_features: pd.DataFrame,
    *,
    operator: dict[str, Any],
    representation: RepresentationSpec,
    runtime_artifact: dict[str, Any],
    min_units_for_score: int,
    seed: int,
    version: str = "v7-operator-smoke-1",
) -> FittedOperator:
    """Fit feature scaling, factor loadings and reference norms on frozen splits.

    Discovery fits representation geometry and the factor model.  Calibration
    defines score norms.  Neither confirmation authors nor external labels are
    used to make the fitted object.
    """
    feature_columns = _numeric_feature_columns(author_features)
    discovery = author_features.loc[author_features["split"].eq("discovery")].copy()
    calibration = author_features.loc[author_features["split"].eq("calibration")].copy()
    if len(discovery) < max(12, representation.factor_count + 3):
        raise ValueError(f"Too few discovery authors for factor construction: {len(discovery)}")
    if calibration.empty:
        raise ValueError("V7 requires a calibration author set for reference norms.")
    raw_discovery = discovery[feature_columns].to_numpy(float)
    impute = np.nanmedian(raw_discovery, axis=0)
    raw_discovery = np.where(np.isfinite(raw_discovery), raw_discovery, impute)
    center = np.mean(raw_discovery, axis=0)
    scale = _safe_scale(raw_discovery)
    keep = np.std(raw_discovery, axis=0) > 1e-9
    if int(keep.sum()) < 2:
        raise ValueError("V7 author aggregation has fewer than two nonconstant discovery features.")
    feature_columns = [column for column, include in zip(feature_columns, keep, strict=True) if include]
    impute, center, scale = impute[keep], center[keep], scale[keep]
    x_discovery = (raw_discovery[:, keep] - center) / scale
    n_factors = min(int(representation.factor_count), x_discovery.shape[0] - 1, x_discovery.shape[1])
    if n_factors < 1:
        raise ValueError("No admissible factor count after discovery preprocessing.")
    estimator = FactorAnalysis(n_components=n_factors, random_state=seed, max_iter=1000, tol=1e-3)
    estimator.fit(x_discovery)
    calibration_scores_raw = _fa_posterior_scores(
        _prepare_matrix(calibration, feature_columns, impute, center, scale),
        fa_mean=estimator.mean_, loadings=estimator.components_, noise_variance=estimator.noise_variance_,
    )
    signs = _deterministic_factor_signs(estimator.components_)
    calibration_scores = calibration_scores_raw * signs[None, :]
    norm_mean = np.mean(calibration_scores, axis=0)
    norm_scale = _safe_scale(calibration_scores)
    quantile_grid = np.linspace(0.01, 0.99, 99)
    quantiles = np.quantile(calibration_scores, quantile_grid, axis=0).T
    bundle_id = _hash_bundle_id(str(operator["name"]), feature_columns, seed)
    bundle = FactorBundle(
        bundle_id=bundle_id,
        version=version,
        operator=operator,
        representation=representation.to_dict(),
        feature_names=feature_columns,
        feature_impute=impute.tolist(),
        feature_center=center.tolist(),
        feature_scale=scale.tolist(),
        fa_mean=estimator.mean_.tolist(),
        factor_loadings=estimator.components_.tolist(),
        noise_variance=estimator.noise_variance_.tolist(),
        factor_signs=signs.tolist(),
        norm_mean=norm_mean.tolist(),
        norm_scale=norm_scale.tolist(),
        norm_quantiles={f"factor_{index + 1:02d}": quantiles[index].tolist() for index in range(n_factors)},
        support_rule={
            "min_units_for_score": int(min_units_for_score),
            "whole_text_sem_policy": "SEM_UNAVAILABLE_WITH_ONE_UNIT",
            "refusal_code": "SCORE_REFUSE_INSUFFICIENT_OBSERVATIONS",
        },
        runtime_artifact=runtime_artifact,
        reference_population={
            "discovery_authors": int(discovery["user_id"].nunique()),
            "calibration_authors": int(calibration["user_id"].nunique()),
            "reference_norm_source": "author-disjoint calibration split",
        },
        claim_boundary=(
            "Label-free text-structure score. This bundle is not a personality, clinical, "
            "or external-scale measure without a separate validation study."
        ),
        created_utc=datetime.now(UTC).isoformat(),
    )
    return FittedOperator(bundle=bundle, representation=None, feature_columns=feature_columns)


def _prepare_matrix(
    frame: pd.DataFrame,
    feature_columns: list[str],
    impute: np.ndarray,
    center: np.ndarray,
    scale: np.ndarray,
) -> np.ndarray:
    raw = frame.reindex(columns=feature_columns).to_numpy(float)
    raw = np.where(np.isfinite(raw), raw, impute[None, :])
    return (raw - center[None, :]) / scale[None, :]


def _deterministic_factor_signs(loadings: np.ndarray) -> np.ndarray:
    signs = []
    for row in np.asarray(loadings, float):
        anchor = row[int(np.argmax(np.abs(row)))]
        signs.append(1.0 if anchor >= 0 else -1.0)
    return np.asarray(signs, float)


def score_author_features(bundle: FactorBundle, author_features: pd.DataFrame) -> pd.DataFrame:
    """Score author-level features with a fully frozen V7 bundle.

    This function never calls `fit`.  It makes the absence of adequate repeated
    observations explicit through `score_status` instead of converting it to a
    misleadingly precise zero-error score.
    """
    impute = np.asarray(bundle.feature_impute, float)
    center = np.asarray(bundle.feature_center, float)
    scale = np.asarray(bundle.feature_scale, float)
    standardized = _prepare_matrix(author_features, bundle.feature_names, impute, center, scale)
    raw_scores = _fa_posterior_scores(
        standardized,
        fa_mean=np.asarray(bundle.fa_mean, float),
        loadings=np.asarray(bundle.factor_loadings, float),
        noise_variance=np.asarray(bundle.noise_variance, float),
    )
    scores = raw_scores * np.asarray(bundle.factor_signs, float)[None, :]
    z_scores = (scores - np.asarray(bundle.norm_mean, float)[None, :]) / np.asarray(bundle.norm_scale, float)[None, :]
    output = author_features[["user_id", "split", "n_units", "n_tokens"]].copy().reset_index(drop=True)
    supported = output["n_units"].to_numpy(int) >= int(bundle.support_rule["min_units_for_score"])
    output["score_status"] = np.where(supported, "SCORED", bundle.support_rule["refusal_code"])
    for index in range(scores.shape[1]):
        output[f"SU7-FC-{index + 1:04d}@v1"] = scores[:, index]
        output[f"SU7-FC-{index + 1:04d}@v1_z"] = z_scores[:, index]
    return output


def unit_bootstrap_sem(
    observations: pd.DataFrame,
    embeddings: np.ndarray,
    bundle: FactorBundle,
    *,
    repetitions: int = 24,
    seed: int = 20260714,
) -> pd.DataFrame:
    """Estimate technical score error by resampling observed units within author.

    This is not a cross-day reliability estimate.  It quantifies the precision
    available from the observed text units under the same operator.
    """
    if observations.empty:
        return pd.DataFrame(columns=["user_id"])
    rng = np.random.default_rng(seed)
    factor_columns = [f"SU7-FC-{index + 1:04d}@v1" for index in range(len(bundle.factor_loadings))]
    rows: list[dict[str, Any]] = []
    for user_id, group in observations.groupby("user_id", observed=True, sort=False):
        indices = group.index.to_numpy(int)
        row: dict[str, Any] = {"user_id": str(user_id), "bootstrap_unit_count": int(len(indices))}
        if len(indices) < 2:
            row["sem_status"] = "SEM_UNAVAILABLE_WITH_ONE_UNIT"
            for factor in factor_columns:
                row[f"{factor}_sem"] = float("nan")
            rows.append(row)
            continue
        draws: list[np.ndarray] = []
        for _ in range(int(repetitions)):
            chosen = rng.choice(indices, size=len(indices), replace=True)
            sampled = observations.loc[chosen].copy().reset_index(drop=True)
            features = author_features_from_embeddings(sampled, embeddings[chosen])
            score = score_author_features(bundle, features)
            draws.append(score[factor_columns].iloc[0].to_numpy(float))
        sem = np.std(np.vstack(draws), axis=0, ddof=1)
        row["sem_status"] = "BOOTSTRAP_SEM"
        for factor, value in zip(factor_columns, sem, strict=True):
            row[f"{factor}_sem"] = float(value)
        rows.append(row)
    return pd.DataFrame(rows)


def technical_view_consistency(
    observations: pd.DataFrame,
    embeddings: np.ndarray,
    bundle: FactorBundle,
) -> pd.DataFrame:
    """Compare even/odd observation views under an already frozen score map.

    This is intentionally called *technical view consistency*, not trait
    reliability: alternating comments/windows are not independent life
    occasions or matched clinical prompts.
    """
    if observations.empty:
        return pd.DataFrame(columns=["factor", "n_users", "correlation"])
    left_mask = observations["unit_index"].to_numpy(int) % 2 == 0
    right_mask = ~left_mask
    left = author_features_from_embeddings(observations.loc[left_mask].reset_index(drop=True), embeddings[left_mask])
    right = author_features_from_embeddings(observations.loc[right_mask].reset_index(drop=True), embeddings[right_mask])
    if left.empty or right.empty:
        return pd.DataFrame(columns=["factor", "n_users", "correlation"])
    left_scores = score_author_features(bundle, left)
    right_scores = score_author_features(bundle, right)
    factor_columns = [column for column in left_scores if column.startswith("SU7-FC-") and not column.endswith("_z")]
    merged = left_scores.merge(right_scores, on="user_id", suffixes=("_left", "_right"))
    rows: list[dict[str, Any]] = []
    for factor in factor_columns:
        left_values = merged[f"{factor}_left"].to_numpy(float)
        right_values = merged[f"{factor}_right"].to_numpy(float)
        valid = np.isfinite(left_values) & np.isfinite(right_values)
        correlation = float("nan")
        if valid.sum() >= 8 and np.std(left_values[valid]) > 1e-12 and np.std(right_values[valid]) > 1e-12:
            correlation = float(np.corrcoef(left_values[valid], right_values[valid])[0, 1])
        rows.append({"factor": factor, "n_users": int(valid.sum()), "correlation": correlation})
    return pd.DataFrame(rows)


def confirmation_subspace_similarity(bundle: FactorBundle, author_features: pd.DataFrame, *, seed: int) -> dict[str, float]:
    """Refit a diagnostic confirmation factor space without modifying the bundle."""
    confirmation = author_features.loc[author_features["split"].eq("confirmation")].copy()
    if len(confirmation) < max(8, len(bundle.factor_loadings) + 3):
        return {"subspace_similarity": float("nan"), "max_principal_angle_deg": float("nan"), "n_confirmation": int(len(confirmation))}
    x = _prepare_matrix(
        confirmation,
        bundle.feature_names,
        np.asarray(bundle.feature_impute, float),
        np.asarray(bundle.feature_center, float),
        np.asarray(bundle.feature_scale, float),
    )
    k = min(len(bundle.factor_loadings), x.shape[0] - 1, x.shape[1])
    if k < 1:
        return {"subspace_similarity": float("nan"), "max_principal_angle_deg": float("nan"), "n_confirmation": int(len(confirmation))}
    diagnostic = FactorAnalysis(n_components=k, random_state=seed, max_iter=1000, tol=1e-3).fit(x)
    reference_basis, _ = np.linalg.qr(np.asarray(bundle.factor_loadings, float).T)
    diagnostic_basis, _ = np.linalg.qr(diagnostic.components_.T)
    angles = subspace_angles(reference_basis[:, :k], diagnostic_basis[:, :k])
    return {
        "subspace_similarity": float(np.mean(np.cos(angles))),
        "max_principal_angle_deg": float(np.degrees(np.max(angles))),
        "n_confirmation": int(len(confirmation)),
    }


def bundle_sha256(path: str | Path) -> str:
    """Return a stable local artifact checksum for the discovery ledger."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_factor_bundle(path: str | Path) -> FactorBundle:
    """Load an auditable JSON bundle for scoring, never for refitting."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return FactorBundle.from_dict(payload)
