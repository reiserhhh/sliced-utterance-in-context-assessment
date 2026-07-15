from __future__ import annotations

import numpy as np

from scripts.run_suica_v7_operator_family_validation import _source_disjoint_alignment_auc


def test_source_disjoint_alignment_auc_separates_linked_from_random_pairing() -> None:
    rng = np.random.default_rng(31)
    latent = rng.normal(size=(36, 5))
    left = latent + rng.normal(scale=0.15, size=latent.shape)
    right = latent + rng.normal(scale=0.15, size=latent.shape)
    linked = _source_disjoint_alignment_auc(left, right)
    shuffled = _source_disjoint_alignment_auc(left, right, pairing=rng.permutation(len(left)))
    assert linked > 0.75
    assert linked > shuffled + 0.15
