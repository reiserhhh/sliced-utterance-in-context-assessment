"""Truth-open audit utilities for SUICA M3 cross-family confirmation."""
from __future__ import annotations

import numpy as np
from scipy.spatial.distance import pdist
from scipy.stats import rankdata, spearmanr
from sklearn.metrics import roc_auc_score

from .m3_cross_family_contracts import (
    M3CrossFamilyEstimate,
    M3CrossFamilyTruth,
)


TARGET_FAMILIES: dict[str, tuple[str, str]] = {
    "distribution": ("distribution_ecf", "moments_degree4"),
    "condition": ("condition_laplace", "condition_poly3"),
    "partner": ("partner_laplace", "partner_poly3"),
    "hazard": ("path_hazard", "path_second_order"),
    "direction": ("path_time_reversal", "path_second_order"),
    "nonlinear_dynamics": ("path_delay_vamp", "path_second_order"),
}


def same_author_auc(train: np.ndarray, test: np.ndarray) -> float:
    """Measure independent-view author matching without fitting labels."""
    distance = np.linalg.norm(
        train[:, None, :] - test[None, :, :],
        axis=2,
    ) / np.sqrt(max(train.shape[1], 1))
    labels = np.eye(len(train), dtype=int).ravel()
    return float(roc_auc_score(labels, -distance.ravel()))


def identity_margin(train: np.ndarray, test: np.ndarray) -> float:
    """Return the mean held-out other-minus-own distance margin."""
    distance = np.linalg.norm(
        train[:, None, :] - test[None, :, :],
        axis=2,
    ) / np.sqrt(max(train.shape[1], 1))
    own = np.diag(distance)
    mask = ~np.eye(len(train), dtype=bool)
    other = np.median(distance[mask].reshape(len(train), -1), axis=1)
    return float(np.mean(other - own))


def geometry_correlation(feature: np.ndarray, oracle: np.ndarray) -> float:
    """Compare author distance geometries without coordinate alignment."""
    feature_distance = pdist(np.asarray(feature, dtype=float))
    oracle_distance = pdist(np.asarray(oracle, dtype=float))
    if np.std(feature_distance) <= 1e-12 or np.std(oracle_distance) <= 1e-12:
        return float("nan")
    return float(spearmanr(feature_distance, oracle_distance).statistic)


def _residualize(values: np.ndarray, nuisance: np.ndarray) -> np.ndarray:
    design = np.column_stack([np.ones(len(values)), nuisance])
    return values - design @ np.linalg.lstsq(design, values, rcond=None)[0]


def partial_geometry_correlation(
    feature: np.ndarray,
    target: np.ndarray,
    nuisance: list[np.ndarray],
) -> float:
    """Rank partial correlation between feature and target geometries."""
    feature_distance = rankdata(pdist(np.asarray(feature, dtype=float)))
    target_distance = rankdata(pdist(np.asarray(target, dtype=float)))
    if not nuisance:
        if (
            np.std(feature_distance) <= 1e-12
            or np.std(target_distance) <= 1e-12
        ):
            return float("nan")
        return float(np.corrcoef(feature_distance, target_distance)[0, 1])
    nuisance_distance = np.column_stack([
        rankdata(pdist(np.asarray(item, dtype=float)))
        for item in nuisance
    ])
    feature_residual = _residualize(feature_distance, nuisance_distance)
    target_residual = _residualize(target_distance, nuisance_distance)
    if np.std(feature_residual) <= 1e-12 or np.std(target_residual) <= 1e-12:
        return float("nan")
    return float(np.corrcoef(feature_residual, target_residual)[0, 1])


def audit_m3_cross_family(
    estimate: M3CrossFamilyEstimate,
    truth: M3CrossFamilyTruth,
) -> list[dict[str, float | str | bool]]:
    """Open truth and score all registered targets and their cheap aliases."""
    rows: list[dict[str, float | str | bool]] = []
    active = list(truth.active_targets)
    for target in active:
        expected, cheap = TARGET_FAMILIES[target]
        oracle = truth.oracle_profiles.get(
            target,
            truth.author_parameters[target],
        )
        nuisance = [
            truth.oracle_profiles.get(
                other,
                truth.author_parameters[other],
            )
            for other in active
            if other != target
        ]
        expected_auc = same_author_auc(
            estimate.train_features[expected],
            estimate.test_features[expected],
        )
        cheap_auc = same_author_auc(
            estimate.train_features[cheap],
            estimate.test_features[cheap],
        )
        expected_geometry = partial_geometry_correlation(
            estimate.test_features[expected],
            oracle,
            nuisance,
        )
        cheap_geometry = partial_geometry_correlation(
            estimate.test_features[cheap],
            oracle,
            nuisance,
        )
        off_target = float("nan")
        if nuisance:
            off_target = max(
                abs(geometry_correlation(
                    estimate.test_features[expected],
                    other,
                ))
                for other in nuisance
            )
        heldout_increment = estimate.heldout_metrics.get(
            f"{expected}_score_gain",
            float("nan"),
        )
        rows.append({
            "world": truth.world,
            "target": target,
            "exact_alias": truth.exact_alias,
            "expected_family": expected,
            "cheap_family": cheap,
            "expected_auc": expected_auc,
            "cheap_auc": cheap_auc,
            "delta_auc": expected_auc - cheap_auc,
            "expected_geometry": expected_geometry,
            "cheap_geometry": cheap_geometry,
            "delta_geometry": expected_geometry - cheap_geometry,
            "heldout_increment": float(heldout_increment),
            "off_target_geometry": off_target,
            "refusal_count": len(estimate.refusals),
        })
    if not active:
        for family in (
            "distribution_ecf",
            "condition_laplace",
            "partner_laplace",
            "path_hazard",
            "path_time_reversal",
            "path_delay_vamp",
        ):
            rows.append({
                "world": truth.world,
                "target": "null",
                "exact_alias": False,
                "expected_family": family,
                "cheap_family": "",
                "expected_auc": same_author_auc(
                    estimate.train_features[family],
                    estimate.test_features[family],
                ),
                "cheap_auc": float("nan"),
                "delta_auc": float("nan"),
                "expected_geometry": float("nan"),
                "cheap_geometry": float("nan"),
                "delta_geometry": float("nan"),
                "heldout_increment": float("nan"),
                "off_target_geometry": float("nan"),
                "refusal_count": len(estimate.refusals),
            })
    return rows
