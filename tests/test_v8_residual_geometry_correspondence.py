"""Tests for V8 axis-free residual geometry correspondence."""
from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.v8_residual_geometry_correspondence import (
    ResidualGeometrySpec,
    _alignment,
    _center_kernel,
    _permutation_order,
    _u_center_kernel,
    evaluate_residual_geometry,
    frozen_bandwidth,
    relational_matrices,
)


def _metadata(authors: int = 180) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "author_id": [f"u{index}" for index in range(authors)],
            "context": np.resize(["a", "b", "c"], authors),
            "split": np.resize(
                ["D0"] * 80 + ["D1"] * 50 + ["D2"] * 50,
                authors,
            ),
        }
    )


def test_centered_kernel_and_exchangeable_order() -> None:
    matrix = np.arange(25, dtype=float).reshape(5, 5)
    centered = _center_kernel(matrix)
    assert np.allclose(centered.mean(axis=0), 0.0)
    assert np.allclose(centered.mean(axis=1), 0.0)
    symmetric = matrix + matrix.T
    u_centered = _u_center_kernel(symmetric)
    assert np.allclose(np.diag(u_centered), 0.0)
    assert np.allclose(u_centered.sum(axis=0), 0.0)
    contexts = np.asarray(["a", "a", "a", "b", "b"])
    rng = np.random.default_rng(7)
    fixed_points = []
    for _ in range(100):
        order = _permutation_order(contexts, rng=rng)
        assert set(order[:3]) == {0, 1, 2}
        assert set(order[3:]) == {3, 4}
        fixed_points.append(int(np.sum(order == np.arange(5))))
    assert max(fixed_points) > 0


def test_relational_matrices_preserve_identity_geometry() -> None:
    rng = np.random.default_rng(11)
    values = rng.normal(size=(60, 2, 8))
    values[:, 1] = values[:, 0]
    nuisance = rng.normal(size=(60, 2, 4))
    nuisance[:, 1] = nuisance[:, 0]
    contexts = np.resize(["a", "b"], 60)
    matrices = relational_matrices(
        values,
        nuisance,
        contexts,
        bandwidth=2.0,
        spec=ResidualGeometrySpec(
            d0_null_draws=99,
            test_null_draws=99,
            bootstrap_draws=99,
        ),
    )
    assert _alignment(*matrices["linear_krc"]) > 0.999
    assert _alignment(*matrices["rbf_krc_1"]) > 0.999
    assert _alignment(*matrices["local_overlap_0.1"]) > 0.999


def test_frozen_bandwidth_reads_d0_only() -> None:
    rng = np.random.default_rng(13)
    metadata = _metadata()
    values = rng.normal(size=(len(metadata), 2, 5))
    baseline = frozen_bandwidth(values, metadata)
    values[metadata["split"].ne("D0").to_numpy()] *= 1_000
    assert np.isclose(frozen_bandwidth(values, metadata), baseline)


def test_axis_free_geometry_detects_distributed_correspondence() -> None:
    rng = np.random.default_rng(17)
    metadata = _metadata()
    latent = rng.normal(size=(len(metadata), 24))
    left = latent + rng.normal(scale=0.5, size=latent.shape)
    right = latent + rng.normal(scale=0.5, size=latent.shape)
    values = np.stack([left, right], axis=1)
    nuisance = rng.normal(size=(len(metadata), 2, 5))
    result = evaluate_residual_geometry(
        {"synthetic": (metadata, values, nuisance)},
        bandwidth_by_corpus={
            "synthetic": frozen_bandwidth(values, metadata)
        },
        spec=ResidualGeometrySpec(
            d0_null_draws=99,
            test_null_draws=99,
            bootstrap_draws=99,
            seed=71,
        ),
    )
    assert result["status"]["synthetic"] in {
        "DISTRIBUTED_LINEAR_GEOMETRY",
        "NONLINEAR_RESIDUAL_GEOMETRY",
        "AXIS_FREE_MULTI_SCALE_KERNEL_CORRESPONDENCE",
        "AXIS_FREE_SHORT_SCALE_KERNEL_CORRESPONDENCE",
        "AXIS_FREE_SINGLE_SCALE_KERNEL_CORRESPONDENCE",
    }
    linear = result["cells"].loc[
        result["cells"]["metric"].eq("linear_krc")
        & result["cells"]["split"].isin(["D1", "D2"])
    ]
    assert linear["excess"].gt(0).all()


def test_axis_free_geometry_refuses_independent_views() -> None:
    rng = np.random.default_rng(19)
    metadata = _metadata()
    values = rng.normal(size=(len(metadata), 2, 12))
    nuisance = rng.normal(size=(len(metadata), 2, 4))
    result = evaluate_residual_geometry(
        {"synthetic": (metadata, values, nuisance)},
        bandwidth_by_corpus={
            "synthetic": frozen_bandwidth(values, metadata)
        },
        spec=ResidualGeometrySpec(
            d0_null_draws=99,
            test_null_draws=99,
            bootstrap_draws=99,
            seed=73,
        ),
    )
    assert result["status"]["synthetic"] == "SCALAR_CONCORDANCE_ONLY"
    d0_linear = result["cells"].loc[
        result["cells"]["metric"].eq("linear_krc")
        & result["cells"]["split"].eq("D0")
    ].iloc[0]
    assert abs(float(d0_linear["null_mean"])) < 0.10


def test_axis_free_geometry_detects_nonlinear_correspondence() -> None:
    rng = np.random.default_rng(101)
    authors = 240
    metadata = pd.DataFrame(
        {
            "author_id": [f"u{index}" for index in range(authors)],
            "context": np.resize(["a", "b", "c"], authors),
            "split": np.resize(
                ["D0"] * 100 + ["D1"] * 70 + ["D2"] * 70,
                authors,
            ),
        }
    )
    latent = rng.uniform(-2, 2, size=(authors, 1))
    left = np.column_stack(
        [latent, rng.normal(scale=0.1, size=(authors, 3))]
    )
    right = np.column_stack(
        [latent**2, rng.normal(scale=0.1, size=(authors, 3))]
    )
    values = np.stack([left, right], axis=1)
    nuisance = rng.normal(size=(authors, 2, 3))
    result = evaluate_residual_geometry(
        {"synthetic": (metadata, values, nuisance)},
        bandwidth_by_corpus={
            "synthetic": frozen_bandwidth(values, metadata)
        },
        spec=ResidualGeometrySpec(
            d0_null_draws=99,
            test_null_draws=99,
            bootstrap_draws=99,
            seed=105,
        ),
    )
    assert result["status"]["synthetic"] == (
        "NONLINEAR_RESIDUAL_GEOMETRY"
    )
