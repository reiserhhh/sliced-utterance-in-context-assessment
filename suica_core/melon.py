"""SUICA melon API — the rind model's own vocabulary as code (2026-07-07).

A FACADE over the frozen machinery; it never reimplements scoring. Names
follow the theory's English watermelon metaphor (the same one the docs use:
rind / flesh / seeds), so the code finally speaks the theory's language:

    melon  = Melon.from_texts("user1", texts)          # 一玉
    slices = melon.slice()                             # 一切れ (frozen slicer + sticker peel)
    sheet  = ScoreSheet.v4()                           # 審査表 v4
    grades = sheet.grade(melon)                        # 採点
    grades.flesh                                       # 果肉系 (F-family)
    grades.rind_coupled                                # 皮系 (C-family constructs)
    grades.mixed                                       # 混合系 (composite)
    seed   = seed_pattern(grades, population_grades)   # 種模様 (distinctive residual)

Governance in code (G12): every Grades object carries its provenance
(regime, population); `compare_levels` REFUSES cross-regime/population
level comparisons (comparison licenses L0-L4, docs/SUICA_COMPARISON_
LICENSES_V1.md); `compare_direction` is always permitted. The forbidden
comparison is now a raised exception, not a guideline.

Equivalence guarantee: ScoreSheet.grade() user means are BIT-IDENTICAL to
the frozen pipeline (score_slices_v2 over fixed_token_slices_for_text with
prep defaults + PERSONALITY_LEAK_RE drop) — asserted in tests/test_melon.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import sys

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text  # noqa: E402

# frozen prep defaults (prepare_suica_v2_phase2_slices)
SLICE_TOKENS = 128
MIN_SLICE_TOKENS = 24
MAX_SLICES_PER_CELL = 10

# v4 family assignment (round-10 corrected, transported fit; registry)
FLESH_FAMILY = ["first_person_usage_v2"]            # + wcl_60/13/23 need the fitted wcl transform
RIND_COUPLED = ["novelty_play_v2", "directive_action_v2"]
MIXED = ["tension_core_v2", "adversity_recovery_v2"]  # tension: undetermined -> reported, never trait
V2_CONSTRUCTS = FLESH_FAMILY + RIND_COUPLED + MIXED


class LicenseError(RuntimeError):
    """Raised when a comparison exceeds its license (G12)."""


@dataclass
class Melon:
    """One person's spontaneous text — a whole melon (一玉)."""
    melon_id: str
    texts: list[str]
    condition: str | None = None       # venue/rind label if known
    regime: str = "free"               # 育ち: free / assigned / domain_locked
    population: str = "unspecified"

    @classmethod
    def from_texts(cls, melon_id: str, texts: list[str], **kw) -> "Melon":
        return cls(melon_id=melon_id, texts=[str(t) for t in texts], **kw)

    def slice(self) -> pd.DataFrame:
        """一切れ: frozen fixed-token slicing + sticker peel (leak mask)."""
        rows = []
        text = "\n".join(self.texts)
        for row in fixed_token_slices_for_text(
                text, slice_tokens=SLICE_TOKENS, stride=SLICE_TOKENS,
                min_slice_tokens=MIN_SLICE_TOKENS, max_slices=0):
            if PERSONALITY_LEAK_RE.search(row["slice_text"]):
                continue  # the sticker says the answer — peel it off
            rows.append({"user_id": self.melon_id, "slice_text": row["slice_text"]})
        return pd.DataFrame(rows)


@dataclass
class Grades:
    """One melon's (or cohort's) score sheet results, with provenance."""
    scores: pd.DataFrame               # index: melon_id; columns: constructs
    regime: str
    population: str
    families: dict = field(default_factory=dict)

    @property
    def flesh(self) -> pd.DataFrame:
        return self.scores[[c for c in self.scores.columns if self.families.get(c) == "flesh"]]

    @property
    def rind_coupled(self) -> pd.DataFrame:
        return self.scores[[c for c in self.scores.columns if self.families.get(c) == "rind"]]

    @property
    def mixed(self) -> pd.DataFrame:
        return self.scores[[c for c in self.scores.columns if self.families.get(c) == "mixed"]]

    def compare_levels(self, other: "Grades") -> pd.DataFrame:
        """Level comparison — licensed ONLY within the same regime AND
        population (L0-L2). Cross-regime levels are forbidden (F4 + PRED-4:
        no covariate shortcut exists)."""
        if self.regime != other.regime or self.population != other.population:
            raise LicenseError(
                f"level comparison across regimes/populations is out of license "
                f"({self.regime}/{self.population} vs {other.regime}/{other.population}); "
                "allowed cross-regime claims: direction and within-population rank "
                "(see COMPARISON LICENSES L3)")
        common = [c for c in self.scores.columns if c in other.scores.columns]
        return self.scores[common].mean() - other.scores[common].mean()

    def compare_direction(self, other: "Grades") -> pd.Series:
        """Direction comparison — always licensed (the strongest transportable
        claim; H2 survived two document types at T4)."""
        common = [c for c in self.scores.columns if c in other.scores.columns]
        return np.sign(self.scores[common].mean() - other.scores[common].mean())


class ScoreSheet:
    """審査表: the frozen scorer + v4 family annotations."""

    def __init__(self, scorer, families: dict):
        self._scorer = scorer
        self.families = families

    @classmethod
    def v4(cls) -> "ScoreSheet":
        from scripts.suica_v4_lib import score_slices_v4
        fams = {c: "flesh" for c in FLESH_FAMILY}
        fams |= {c: "rind" for c in RIND_COUPLED}
        fams |= {c: "mixed" for c in MIXED}
        return cls(score_slices_v4, fams)

    @classmethod
    def v3_frozen(cls) -> "ScoreSheet":
        from scripts.suica_v2_lib import score_slices_v2
        fams = {c: "flesh" for c in FLESH_FAMILY}
        fams |= {c: "rind" for c in RIND_COUPLED}
        fams |= {c: "mixed" for c in MIXED}
        return cls(score_slices_v2, fams)

    def grade(self, *melons: Melon) -> Grades:
        regimes = {m.regime for m in melons}
        pops = {m.population for m in melons}
        assert len(regimes) == 1 and len(pops) == 1, \
            "grade one regime/population at a time (then compare under license)"
        frames = [m.slice() for m in melons]
        long = pd.concat(frames, ignore_index=True)
        scored = self._scorer(long)
        user_means = scored.groupby("user_id")[V2_CONSTRUCTS].mean()
        return Grades(scores=user_means, regime=regimes.pop(), population=pops.pop(),
                      families=self.families)


def seed_pattern(grades: Grades, population: Grades) -> pd.DataFrame:
    """種模様: the distinctive residual — what remains of each melon after
    subtracting the population's normative profile (Furr decomposition;
    OP-32: stability median r=0.505 across >=90-day occasions, 0.684 on
    flesh constructs alone). Returns per-melon deviation profiles (z within
    the population) plus the distinctiveness magnitude."""
    cols = [c for c in grades.scores.columns if c in population.scores.columns]
    mu = population.scores[cols].mean()
    sd = population.scores[cols].std().replace(0, np.nan)
    dev = (grades.scores[cols] - mu) / sd
    dev["distinctiveness"] = np.sqrt((dev[cols] ** 2).sum(axis=1))
    return dev


def distinctive_similarity(seed_a: pd.Series, seed_b: pd.Series) -> float:
    """Similarity of two seed patterns (profile r over shared constructs) —
    the fingerprint-matching primitive. Always compare against the stranger
    null (よその玉比べ) before claiming identity-grade similarity."""
    common = [c for c in seed_a.index if c in seed_b.index and c != "distinctiveness"]
    a, b = seed_a[common].astype(float), seed_b[common].astype(float)
    return float(np.corrcoef(a, b)[0, 1])
