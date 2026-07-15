from __future__ import annotations

import numpy as np

from suica_core.diffusion_geometry import diffusion_embedding, diffusion_geometry_audit


def test_diffusion_embedding_has_requested_coordinates_on_a_connected_cloud() -> None:
    theta = np.linspace(0.0, 2.0 * np.pi, 80, endpoint=False)
    values = np.column_stack([np.cos(theta), np.sin(theta), 0.1 * np.cos(2.0 * theta)])
    result = diffusion_embedding(values, neighbours=10, dimensions=3)
    assert result.coordinates.shape == (80, 3)
    assert result.connected_components == 1
    assert np.isfinite(result.eigengap)


def test_diffusion_audit_detects_a_replicated_curved_cloud() -> None:
    rng = np.random.default_rng(201)
    theta = np.linspace(0.0, 2.0 * np.pi, 96, endpoint=False)
    latent = np.column_stack([np.cos(theta), np.sin(theta), np.cos(2.0 * theta)])
    early = latent + rng.normal(scale=0.02, size=latent.shape)
    late = latent + rng.normal(scale=0.02, size=latent.shape)
    metrics, _ = diffusion_geometry_audit(
        early, late, neighbours=12, dimensions=3, permutation_iterations=99, seed=202,
    )
    assert metrics["distance_spearman"] > 0.8
    assert metrics["distance_spearman_permutation_p"] <= 0.02
