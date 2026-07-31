"""Response-safe chart discovery and frozen conditional-response evaluation."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, shortest_path
from scipy.spatial.distance import cdist, pdist, squareform
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap, trustworthiness

from .m3_mechanism_audit import same_author_auc
from .m4_condition_manifold_contracts import (
    M4ConditionChart,
    M4ConditionEstimate,
    M4ConditionObserved,
    M4ConditionPanel,
    forbidden_provenance_fields,
    validate_condition_observed,
)


PANEL_NAMES = (
    "reference_calibration",
    "reference_selection",
    "mechanism_calibration",
    "mechanism_selection",
    "mechanism_evaluation",
)


@dataclass
class _SourceRepresentation:
    family: str
    center: np.ndarray
    scale: np.ndarray
    calibration_standardized: np.ndarray
    calibration_representation: np.ndarray
    estimator: Any
    graph_distances: np.ndarray | None
    neighbors: int


@dataclass
class _Candidate:
    family: str
    parameters: dict[str, int]
    models: tuple[_SourceRepresentation, ...]
    landmarks: np.ndarray
    bandwidths: np.ndarray


@dataclass(frozen=True)
class FrozenConditionTransform:
    """Reusable response-safe chart followed by reference whitening.

    The leading output coordinate is a constant mass coordinate. The
    remaining coordinates are whitened on the reference-calibration panel,
    so equivalent full-rank linear chart reparameterizations differ only by
    an orthogonal gauge on the retained support.
    """

    selected_family: str
    selected_parameters: dict[str, int]
    effective_rank: int
    provenance_hash: str
    whitening_center: np.ndarray
    whitening_matrix: np.ndarray
    _candidate: _Candidate

    def transform_prototypes(self, pre_context: np.ndarray) -> np.ndarray:
        """Transform source prototypes or a full source-author panel.

        Accepted shapes are ``source x point x feature`` and
        ``source x author x point x feature``. Author observations are
        averaged before the frozen response-safe chart is applied.
        """
        values = np.asarray(pre_context, dtype=float)
        if values.ndim == 4:
            values = np.mean(values, axis=1)
        if values.ndim != 3:
            raise ValueError(
                "pre_context must be source/point/feature or "
                "source/author/point/feature"
            )
        raw = np.mean(_candidate_features(self._candidate, values), axis=0)
        whitened = (
            (raw - self.whitening_center)
            @ self.whitening_matrix
        )
        return np.column_stack([np.ones(len(raw)), whitened])


def _safe_spearman(first: np.ndarray, second: np.ndarray) -> float:
    x = np.asarray(first, dtype=float).ravel()
    y = np.asarray(second, dtype=float).ravel()
    if np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return 0.0
    value = float(spearmanr(x, y).statistic)
    return value if np.isfinite(value) else 0.0


def _robust_scale(
    values: np.ndarray,
    *,
    center: np.ndarray | None = None,
    scale: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    matrix = np.asarray(values, dtype=float)
    fitted_center = (
        np.median(matrix, axis=0)
        if center is None
        else np.asarray(center, dtype=float)
    )
    if scale is None:
        lower, upper = np.quantile(matrix, [0.25, 0.75], axis=0)
        fitted_scale = upper - lower
    else:
        fitted_scale = np.asarray(scale, dtype=float)
    fitted_scale = np.where(fitted_scale <= 1e-8, 1.0, fitted_scale)
    return (
        (matrix - fitted_center) / fitted_scale,
        fitted_center,
        fitted_scale,
    )


def _knn_graph_distances(
    values: np.ndarray,
    neighbors: int,
) -> tuple[np.ndarray, int]:
    distances = squareform(pdist(values))
    np.fill_diagonal(distances, np.inf)
    ids = np.argpartition(distances, neighbors, axis=1)[:, :neighbors]
    graph = np.full_like(distances, np.inf)
    rows = np.arange(len(values))[:, None]
    graph[rows, ids] = distances[rows, ids]
    graph = np.minimum(graph, graph.T)
    np.fill_diagonal(graph, 0.0)
    components, _ = connected_components(
        csr_matrix(np.isfinite(graph) & (graph > 0.0)),
        directed=False,
        return_labels=True,
    )
    geodesic = shortest_path(
        csr_matrix(np.where(np.isfinite(graph), graph, 0.0)),
        directed=False,
        unweighted=False,
    )
    return np.asarray(geodesic, dtype=float), int(components)


def _fit_source(
    values: np.ndarray,
    *,
    family: str,
    dimensions: int,
    neighbors: int,
) -> _SourceRepresentation:
    standardized, center, scale = _robust_scale(values)
    if family == "linear_pca":
        estimator = PCA(
            n_components=dimensions,
            svd_solver="full",
        ).fit(standardized)
        representation = estimator.transform(standardized)
        graph_distances = None
    elif family == "global_isomap":
        _, components = _knn_graph_distances(standardized, neighbors)
        if components != 1:
            raise ValueError("global Isomap calibration graph is disconnected")
        estimator = Isomap(
            n_neighbors=neighbors,
            n_components=dimensions,
            # Dense eigendecomposition is deterministic at the registered
            # reference-panel size. ARPACK produced occasional chart drift
            # under an otherwise response-identical refit.
            eigen_solver="dense",
        ).fit(standardized)
        representation = estimator.transform(standardized)
        graph_distances = None
    elif family == "landmark_atlas":
        graph_distances, components = _knn_graph_distances(
            standardized,
            neighbors,
        )
        if components != 1 or not np.isfinite(graph_distances).all():
            raise ValueError("landmark atlas calibration graph is disconnected")
        estimator = None
        representation = graph_distances
    else:
        raise ValueError(f"unknown chart family: {family}")
    return _SourceRepresentation(
        family=family,
        center=center,
        scale=scale,
        calibration_standardized=standardized,
        calibration_representation=np.asarray(
            representation,
            dtype=float,
        ),
        estimator=estimator,
        graph_distances=graph_distances,
        neighbors=neighbors,
    )


def _transform_representation(
    model: _SourceRepresentation,
    values: np.ndarray,
) -> np.ndarray:
    standardized, _, _ = _robust_scale(
        values,
        center=model.center,
        scale=model.scale,
    )
    if model.family in {"linear_pca", "global_isomap"}:
        return np.asarray(model.estimator.transform(standardized), dtype=float)
    direct = cdist(
        standardized,
        model.calibration_standardized,
    )
    nearest = np.argpartition(
        direct,
        model.neighbors,
        axis=1,
    )[:, : model.neighbors]
    rows = np.arange(len(standardized))[:, None]
    edge = direct[rows, nearest]
    candidate = (
        edge[:, :, None]
        + model.graph_distances[nearest]
    )
    return np.min(candidate, axis=1)


def _representation_distance(
    model: _SourceRepresentation,
    representation: np.ndarray,
    landmarks: np.ndarray,
) -> np.ndarray:
    if model.family == "landmark_atlas":
        return np.asarray(representation[:, landmarks], dtype=float)
    return cdist(
        representation,
        model.calibration_representation[landmarks],
    )


def _farthest_landmarks(
    distances: np.ndarray,
    count: int,
) -> np.ndarray:
    count = min(int(count), len(distances))
    center = int(np.argmin(np.mean(distances, axis=1)))
    selected = [center]
    minimum = distances[center].copy()
    while len(selected) < count:
        candidate = int(np.argmax(minimum))
        selected.append(candidate)
        minimum = np.minimum(minimum, distances[candidate])
    return np.asarray(selected, dtype=int)


def _candidate_features(
    candidate: _Candidate,
    prototypes: np.ndarray,
) -> np.ndarray:
    output = []
    for source, model in enumerate(candidate.models):
        representation = _transform_representation(
            model,
            prototypes[source],
        )
        distance = _representation_distance(
            model,
            representation,
            candidate.landmarks,
        )
        bandwidth = max(float(candidate.bandwidths[source]), 1e-8)
        output.append(np.exp(-0.5 * (distance / bandwidth) ** 2))
    return np.stack(output)


def _panel_prototypes(panel: M4ConditionPanel) -> np.ndarray:
    return np.mean(np.asarray(panel.pre_context, dtype=float), axis=1)


def _fit_candidate(
    calibration: M4ConditionPanel,
    *,
    family: str,
    dimensions: int,
    neighbors: int,
    landmarks: int,
) -> _Candidate:
    prototypes = _panel_prototypes(calibration)
    models = tuple(
        _fit_source(
            prototypes[source],
            family=family,
            dimensions=dimensions,
            neighbors=min(neighbors, len(prototypes[source]) - 2),
        )
        for source in range(len(prototypes))
    )
    first = models[0]
    if first.family == "landmark_atlas":
        metric = np.asarray(first.graph_distances, dtype=float)
    else:
        metric = squareform(pdist(first.calibration_representation))
    selected = _farthest_landmarks(metric, landmarks)
    bandwidths = []
    for model in models:
        distance = _representation_distance(
            model,
            model.calibration_representation,
            selected,
        )
        positive = distance[distance > 1e-10]
        bandwidths.append(
            float(np.median(positive)) if len(positive) else 1.0
        )
    return _Candidate(
        family=family,
        parameters={
            "dimensions": int(dimensions),
            "neighbors": int(neighbors),
            "landmarks": int(len(selected)),
        },
        models=models,
        landmarks=selected,
        bandwidths=np.asarray(bandwidths),
    )


def _author_split_features(
    candidate: _Candidate,
    panel: M4ConditionPanel,
) -> tuple[np.ndarray, np.ndarray]:
    authors = panel.pre_context.shape[1]
    midpoint = authors // 2
    first = np.mean(panel.pre_context[:, :midpoint], axis=1)
    second = np.mean(panel.pre_context[:, midpoint:], axis=1)
    return (
        np.mean(_candidate_features(candidate, first), axis=0),
        np.mean(_candidate_features(candidate, second), axis=0),
    )


def _coverage(
    candidate: _Candidate,
    prototypes: np.ndarray,
) -> float:
    rates = []
    for source, model in enumerate(candidate.models):
        values, _, _ = _robust_scale(
            prototypes[source],
            center=model.center,
            scale=model.scale,
        )
        calibration = model.calibration_standardized
        within = squareform(pdist(calibration))
        np.fill_diagonal(within, np.inf)
        threshold = 2.0 * float(
            np.quantile(np.min(within, axis=1), 0.95)
        )
        rates.append(float(np.mean(
            np.min(cdist(values, calibration), axis=1) <= threshold
        )))
    return float(np.mean(rates))


def _candidate_diagnostics(
    candidate: _Candidate,
    panel: M4ConditionPanel,
) -> dict[str, float]:
    prototypes = _panel_prototypes(panel)
    features = _candidate_features(candidate, prototypes)
    fused = np.mean(features, axis=0)
    source_geometry = _safe_spearman(
        pdist(features[0]),
        pdist(features[1]),
    )
    split_first, split_second = _author_split_features(candidate, panel)
    split_geometry = _safe_spearman(
        pdist(split_first),
        pdist(split_second),
    )
    raw, _, _ = _robust_scale(
        prototypes[0],
        center=candidate.models[0].center,
        scale=candidate.models[0].scale,
    )
    neighbors = min(10, max(2, (len(raw) - 1) // 3))
    trust = float(
        trustworthiness(raw, fused, n_neighbors=neighbors)
    )
    continuity = float(
        trustworthiness(fused, raw, n_neighbors=neighbors)
    )
    coverage = _coverage(candidate, prototypes)
    return {
        "cross_source_geometry": source_geometry,
        "author_split_geometry": split_geometry,
        "trustworthiness": trust,
        "continuity": continuity,
        "coverage": coverage,
    }


def _author_fingerprint(panel: M4ConditionPanel) -> np.ndarray:
    values = np.asarray(panel.pre_context, dtype=float)
    residual = values - values.mean(axis=1, keepdims=True)
    fingerprint = residual.mean(axis=2)
    return np.transpose(fingerprint, (1, 0, 2)).reshape(len(residual[0]), -1)


def _chart_complexity(candidate: _Candidate) -> float:
    family_penalty = {
        "linear_pca": 0.0,
        "global_isomap": 0.005,
        "landmark_atlas": 0.010,
    }[candidate.family]
    return (
        family_penalty
        + 0.002 * candidate.parameters["dimensions"]
        + 0.0002 * candidate.parameters["landmarks"]
    )


def _chart_score(diagnostics: dict[str, float], candidate: _Candidate) -> float:
    core = min(
        diagnostics["cross_source_geometry"],
        diagnostics["author_split_geometry"],
        diagnostics["trustworthiness"],
        diagnostics["continuity"],
    )
    return core + 0.10 * diagnostics["coverage"] - _chart_complexity(candidate)


def fit_m4_condition_chart(
    observed: M4ConditionObserved,
    *,
    candidates: tuple[dict[str, int | str], ...],
    minimum_cross_source_geometry: float = 0.65,
    minimum_split_geometry: float = 0.65,
    minimum_trustworthiness: float = 0.85,
    minimum_continuity: float = 0.85,
    minimum_coverage: float = 0.85,
    maximum_author_leakage_auc: float = 0.72,
) -> M4ConditionChart:
    """Fit a chart using only declared pre-response variables."""
    validate_condition_observed(observed)
    fitted: list[
        tuple[float, _Candidate, dict[str, float]]
    ] = []
    for spec in candidates:
        try:
            candidate = _fit_candidate(
                observed.reference_calibration,
                family=str(spec["family"]),
                dimensions=int(spec["dimensions"]),
                neighbors=int(spec["neighbors"]),
                landmarks=int(spec["landmarks"]),
            )
            diagnostics = _candidate_diagnostics(
                candidate,
                observed.reference_selection,
            )
        except (ValueError, RuntimeError, np.linalg.LinAlgError):
            continue
        fitted.append((_chart_score(diagnostics, candidate), candidate, diagnostics))
    if not fitted:
        raise RuntimeError("all registered condition-chart candidates failed")
    _, selected, selection_diagnostics = max(fitted, key=lambda item: item[0])
    panel_features = {
        name: _candidate_features(
            selected,
            _panel_prototypes(getattr(observed, name)),
        )
        for name in PANEL_NAMES
    }
    evaluation_diagnostics = _candidate_diagnostics(
        selected,
        observed.mechanism_evaluation,
    )
    leakage_auc = same_author_auc(
        _author_fingerprint(observed.reference_calibration),
        _author_fingerprint(observed.reference_selection),
    )
    forbidden = forbidden_provenance_fields(observed)
    reasons: list[str] = []
    if forbidden:
        reasons.append("forbidden_provenance:" + ",".join(forbidden))
    if leakage_auc > maximum_author_leakage_auc:
        reasons.append("author_dominant_pre_context")
    gates = (
        (
            "cross_source_geometry",
            selection_diagnostics["cross_source_geometry"],
            minimum_cross_source_geometry,
        ),
        (
            "author_split_geometry",
            selection_diagnostics["author_split_geometry"],
            minimum_split_geometry,
        ),
        (
            "trustworthiness",
            selection_diagnostics["trustworthiness"],
            minimum_trustworthiness,
        ),
        (
            "continuity",
            selection_diagnostics["continuity"],
            minimum_continuity,
        ),
        (
            "coverage",
            selection_diagnostics["coverage"],
            minimum_coverage,
        ),
    )
    for name, value, threshold in gates:
        if value < threshold:
            reasons.append(f"underresolved_{name}")
    return M4ConditionChart(
        selected_family=selected.family,
        selected_parameters=dict(selected.parameters),
        panel_features=panel_features,
        selection_diagnostics=selection_diagnostics,
        evaluation_diagnostics=evaluation_diagnostics,
        author_leakage_auc=float(leakage_auc),
        refused=bool(reasons),
        refusal_reasons=tuple(reasons),
    )


def freeze_m4_condition_transform(
    observed: M4ConditionObserved,
    chart: M4ConditionChart,
    *,
    rank_tolerance: float = 1e-6,
    maximum_rank: int | None = None,
) -> FrozenConditionTransform:
    """Rebuild the selected chart and freeze a reusable whitened transform."""
    if rank_tolerance <= 0.0:
        raise ValueError("rank_tolerance must be positive")
    parameters = chart.selected_parameters
    candidate = _fit_candidate(
        observed.reference_calibration,
        family=chart.selected_family,
        dimensions=int(parameters["dimensions"]),
        neighbors=int(parameters["neighbors"]),
        landmarks=int(parameters["landmarks"]),
    )
    prototypes = _panel_prototypes(observed.reference_calibration)
    raw = np.mean(_candidate_features(candidate, prototypes), axis=0)
    center = np.mean(raw, axis=0)
    centered = raw - center
    covariance = (
        centered.T @ centered / max(len(centered) - 1, 1)
    )
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    threshold = rank_tolerance * max(float(eigenvalues[0]), 1e-12)
    retained = np.flatnonzero(eigenvalues > threshold)
    if maximum_rank is not None:
        retained = retained[: max(int(maximum_rank), 1)]
    if len(retained) == 0:
        retained = np.asarray([0])
    whitening = (
        eigenvectors[:, retained]
        / np.sqrt(np.maximum(eigenvalues[retained], 1e-12))[None]
    )
    digest = hashlib.sha256()
    digest.update(chart.selected_family.encode("utf-8"))
    digest.update(
        json.dumps(
            parameters,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )
    for values in (
        candidate.landmarks,
        candidate.bandwidths,
        center,
        whitening,
    ):
        digest.update(np.ascontiguousarray(values).view(np.uint8))
    return FrozenConditionTransform(
        selected_family=chart.selected_family,
        selected_parameters=dict(parameters),
        effective_rank=int(len(retained)),
        provenance_hash=digest.hexdigest(),
        whitening_center=center,
        whitening_matrix=whitening,
        _candidate=candidate,
    )


def _fit_response_coefficients(
    features: np.ndarray,
    response: np.ndarray,
    *,
    ridge: float,
) -> np.ndarray:
    design = np.column_stack([np.ones(len(features)), features])
    penalty = ridge * np.eye(design.shape[1])
    penalty[0, 0] = 0.0
    inverse = np.linalg.solve(
        design.T @ design + penalty,
        design.T,
    )
    target = np.transpose(response, (1, 0, 2)).reshape(len(features), -1)
    coefficient = inverse @ target
    return coefficient.reshape(
        design.shape[1],
        response.shape[0],
        response.shape[2],
    )


def _predict_response(
    features: np.ndarray,
    coefficient: np.ndarray,
) -> np.ndarray:
    design = np.column_stack([np.ones(len(features)), features])
    prediction = np.einsum("np,pud->nud", design, coefficient)
    return np.transpose(prediction, (1, 0, 2))


def _response_loss(
    prediction: np.ndarray,
    response: np.ndarray,
) -> float:
    return float(np.mean((prediction - response) ** 2))


def fit_m4_condition_manifold(
    observed: M4ConditionObserved,
    *,
    candidates: tuple[dict[str, int | str], ...],
    ridge_grid: tuple[float, ...] = (0.01, 0.10, 1.0),
    **chart_thresholds: float,
) -> M4ConditionEstimate:
    """Freeze a response-safe chart, then evaluate conditional response."""
    chart = fit_m4_condition_chart(
        observed,
        candidates=candidates,
        **chart_thresholds,
    )
    calibration = np.mean(
        chart.panel_features["mechanism_calibration"],
        axis=0,
    )
    selection = np.mean(
        chart.panel_features["mechanism_selection"],
        axis=0,
    )
    evaluation = np.mean(
        chart.panel_features["mechanism_evaluation"],
        axis=0,
    )
    response_calibration = observed.mechanism_calibration.response
    response_selection = observed.mechanism_selection.response
    losses = []
    for ridge in ridge_grid:
        coefficient = _fit_response_coefficients(
            calibration,
            response_calibration,
            ridge=float(ridge),
        )
        losses.append(_response_loss(
            _predict_response(selection, coefficient),
            response_selection,
        ))
    selected_ridge = float(ridge_grid[int(np.argmin(losses))])
    combined_features = np.vstack([calibration, selection])
    combined_response = np.concatenate(
        [response_calibration, response_selection],
        axis=1,
    )
    coefficient = _fit_response_coefficients(
        combined_features,
        combined_response,
        ridge=selected_ridge,
    )
    prediction = _predict_response(evaluation, coefficient)
    baseline = np.mean(combined_response, axis=1, keepdims=True)
    baseline = np.broadcast_to(
        baseline,
        observed.mechanism_evaluation.response.shape,
    ).copy()
    target = observed.mechanism_evaluation.response
    denominator = float(np.sum((target - baseline) ** 2))
    r2 = (
        1.0 - float(np.sum((target - prediction) ** 2)) / denominator
        if denominator > 1e-12
        else float("nan")
    )
    return M4ConditionEstimate(
        chart=chart,
        selected_ridge=selected_ridge,
        response_predictions=prediction,
        response_baseline=baseline,
        response_r2=float(r2),
        response_mae=float(np.mean(np.abs(target - prediction))),
    )
