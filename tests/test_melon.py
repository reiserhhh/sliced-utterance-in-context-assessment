"""melon API tests — the facade must be bit-identical to the frozen pipeline
and must ENFORCE the comparison licenses (G12 in code)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.melon import (  # noqa: E402
    Melon, ScoreSheet, Grades, LicenseError, seed_pattern, distinctive_similarity,
    SLICE_TOKENS, MIN_SLICE_TOKENS, V2_CONSTRUCTS)
from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TEXTS_A = ["i think we should try the new plan because it might work and i hope so " * 6,
           "the game was fun but the team lost again which made everyone worried " * 6]
TEXTS_B = ["you must not ignore the risk here, please check the schedule again soon " * 6,
           "she said the movie was great and they enjoyed the story together " * 6]


def _frozen_user_means(melon_id: str, texts: list[str]) -> pd.DataFrame:
    rows = []
    text = "\n".join(texts)
    for r in fixed_token_slices_for_text(text, slice_tokens=SLICE_TOKENS, stride=SLICE_TOKENS,
                                         min_slice_tokens=MIN_SLICE_TOKENS, max_slices=0):
        if PERSONALITY_LEAK_RE.search(r["slice_text"]):
            continue
        rows.append({"user_id": melon_id, "slice_text": r["slice_text"]})
    scored = score_slices_v2(pd.DataFrame(rows))
    return scored.groupby("user_id")[V2_CONSTRUCTS].mean()


def test_grade_bit_identical_to_frozen_pipeline():
    m1 = Melon.from_texts("u1", TEXTS_A, population="test")
    m2 = Melon.from_texts("u2", TEXTS_B, population="test")
    grades = ScoreSheet.v3_frozen().grade(m1, m2)
    frozen = pd.concat([_frozen_user_means("u1", TEXTS_A), _frozen_user_means("u2", TEXTS_B)])
    diff = (grades.scores.sort_index() - frozen.sort_index()).abs().max().max()
    assert diff == 0.0


def test_v4_battery_equals_v3_battery():
    m1 = Melon.from_texts("u1", TEXTS_A, population="test")
    g3 = ScoreSheet.v3_frozen().grade(m1)
    g4 = ScoreSheet.v4().grade(m1)
    assert (g3.scores - g4.scores).abs().max().max() == 0.0  # scorer-v4 selftest S2, via the facade


def test_sticker_peel_drops_leak_slices():
    leaky = ["as an INTJ i plan everything early and my mbti explains it " * 8]
    m = Melon.from_texts("u3", leaky)
    assert len(m.slice()) == 0  # every slice carries the sticker -> all peeled


def test_license_enforcement_blocks_cross_regime_levels():
    a = Grades(pd.DataFrame({"x": [1.0]}, index=["u1"]), regime="free", population="reddit")
    b = Grades(pd.DataFrame({"x": [2.0]}, index=["u2"]), regime="assigned", population="students")
    with pytest.raises(LicenseError):
        a.compare_levels(b)
    assert a.compare_direction(b)["x"] == -1.0  # direction always licensed


def test_seed_pattern_is_population_centered():
    rng = np.random.default_rng(0)
    pop = Grades(pd.DataFrame(rng.normal(size=(50, 3)), columns=list("abc")),
                 regime="free", population="p")
    dev = seed_pattern(pop, pop)
    assert abs(dev[list("abc")].mean().mean()) < 1e-12
    assert "distinctiveness" in dev.columns
    s = distinctive_similarity(dev.iloc[0], dev.iloc[0])
    assert s == pytest.approx(1.0)
