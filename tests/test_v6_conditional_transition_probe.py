from __future__ import annotations

import numpy as np
import pandas as pd

from scripts.run_suica_v6_conditional_transition_probe import paired_embeddings


def test_paired_embeddings_uses_sorted_common_authors() -> None:
    rows = []
    for user, half, value in (("b", "early", 1.0), ("b", "late", 2.0), ("a", "early", 3.0),
                              ("a", "late", 4.0), ("c", "early", 5.0)):
        rows.append({"user_id": user, "half": half, "ckte_000": value, "ckte_001": value + 10.0})
    early, late, users = paired_embeddings(pd.DataFrame(rows))
    assert users == ["a", "b"]
    assert np.allclose(early[:, 0], [3.0, 1.0])
    assert np.allclose(late[:, 0], [4.0, 2.0])
