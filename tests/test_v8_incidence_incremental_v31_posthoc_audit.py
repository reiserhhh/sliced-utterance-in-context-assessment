"""Post-confirmation exhaustive audit for V3.1 Apriori completeness."""
from __future__ import annotations

from itertools import combinations

import numpy as np

from suica_core.v8_incidence_incremental import _specificity
from suica_core.v8_incidence_incremental_v31 import (
    condition_aligned_core_scores,
)


def test_thresholded_apriori_matches_full_subset_search() -> None:
    rng = np.random.default_rng(127)
    authors = 7
    grids = []
    for _ in range(3):
        view = []
        for _ in range(4):
            condition = []
            for _ in range(2):
                edges = []
                for _ in range(3):
                    size = int(rng.integers(3, authors + 1))
                    edges.append(tuple(sorted(
                        int(item) for item in rng.choice(
                            authors,
                            size=size,
                            replace=False,
                        )
                    )))
                condition.append(edges)
            view.append(condition)
        grids.append(view)
    threshold = 0.08
    scores, _ = condition_aligned_core_scores(
        grids,
        authors=authors,
        closure_cap=10_000,
        threshold=threshold,
    )

    brute: dict[frozenset[int], float] = {}
    denominator = len(grids[0]) * len(grids[0][0])
    for size in range(3, authors + 1):
        for members in combinations(range(authors), size):
            candidate = frozenset(members)
            total = 0.0
            for condition in range(len(grids[0])):
                for radius_index in range(len(grids[0][0])):
                    support = []
                    for view in grids:
                        support.append(max(
                            (
                                _specificity(authors, len(edge))
                                for edge in view[condition][radius_index]
                                if candidate <= frozenset(edge)
                            ),
                            default=0.0,
                        ))
                    total += min(support)
            brute[candidate] = total / denominator

    expected = {
        candidate for candidate, score in brute.items()
        if score >= threshold
    }
    observed = {
        candidate for candidate, score in scores.items()
        if score >= threshold
    }
    assert observed == expected
    for candidate in expected:
        assert scores[candidate] == brute[candidate]
