#!/usr/bin/env python
"""SUICA scorer v4 — lexicon disjointification (OP-18 completion, OP-23 fix).

Design fact discovered at build time: the four battery-feeding lexicons
(self_focus, second_person, directive, negative_affect, conflict_threat,
uncertainty, novelty_play) were ALREADY mutually disjoint in v3; all 20
shared words cross into NON-battery categories. Assignment policy therefore
gives battery lexicons priority (they keep their members), which makes the
five frozen v2 construct scores BIT-IDENTICAL under v4 — the frozen
validation chain does not restart. What v4 changes is the WIDER 23-anchor
space: the manufactured between-category covariance (know/must/could shared
across categories) is removed, which is the OP-23 concern for E7 state
analyses and PRED-3 structure correlations.

Every reassignment is logged in WORD_MOVES with a one-line rationale
(primary-sense rule; battery-priority where applicable). Token-level
disjointness only: morphological variants (plan vs planning/plans) remain
in different categories where v3 put them — logged as K1 limitation.

Selftest (`python scripts/suica_v4_lib.py`):
  S1 disjointness: no word in two v4 lexicons (hard assert);
  S2 battery equivalence: v3 vs v4 scores on 500 real Tier-U slices —
     max |diff| over the 5 v2 constructs must be exactly 0.0;
  S3 changed-rate report: which derived anchor rates move, and by how much
     (population mean shift on the same 500 slices).
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_narrative_projective_anchor_validation_v2 import (  # noqa: E402
    ANCHOR_LEXICONS as ANCHOR_LEXICONS_V3,
    TOKEN_RE,
)

# word -> (winner category, rationale). Losers drop the word.
WORD_MOVES: dict[str, tuple[str, str]] = {
    "before": ("temporal_sequence", "sequence connective; past_temporal keeps deictic past (was/ago/years)"),
    "better": ("redemption_growth", "comparative improvement is the growth frame's core"),
    "could": ("uncertainty", "epistemic possibility modal (battery priority: uncertainty feeds tension)"),
    "failed": ("conflict_threat", "battery priority; adversity frame reads it via context features"),
    "fun": ("novelty_play", "battery priority; play vocabulary core"),
    "hope": ("mentalization", "future-directed mental-state verb"),
    "hurt": ("negative_affect", "battery priority; primary affective sense"),
    "know": ("certainty", "epistemic-certainty assertion; mentalization keeps think/believe/feel"),
    "lost": ("conflict_threat", "battery priority; loss-as-threat"),
    "love": ("communion", "relational core sense"),
    "must": ("directive", "battery priority; deontic core"),
    "need": ("directive", "battery priority; interpersonal necessity in the blend"),
    "plan": ("achievement_order", "task/schedule frame; future_temporal keeps planning/plans variants (K1)"),
    "remember": ("mentalization", "mental act, not temporal deixis"),
    "should": ("directive", "battery priority; deontic core"),
    "then": ("temporal_sequence", "sequence connective"),
    "try": ("directive", "battery priority; advice imperative in the blend"),
    "when": ("temporal_sequence", "sequence connective"),
    "worry": ("negative_affect", "battery priority; affect core"),
    "worse": ("negative_affect", "battery priority; comparative negative affect"),
}

ANCHOR_LEXICONS_V4: dict[str, list[str]] = {}
for _name, _words in ANCHOR_LEXICONS_V3.items():
    kept = [w for w in _words if w not in WORD_MOVES or WORD_MOVES[w][0] == _name]
    ANCHOR_LEXICONS_V4[_name] = sorted(kept)

_V4_SETS = {name: set(words) for name, words in ANCHOR_LEXICONS_V4.items()}


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall((text or "").lower())


def score_text_anchors_v4(text: str) -> dict[str, float]:
    """v4 anchor rates: identical formulas to the frozen v3 scorer
    (run_suica_narrative_projective_anchor_validation_v2.score_text_anchors),
    computed over the DISJOINT v4 lexicons."""
    import numpy as np
    toks = tokenize(text)
    word_count = max(1, sum(tok != "?" for tok in toks))
    counts = {name: 0 for name in _V4_SETS}
    for tok in toks:
        for name, words in _V4_SETS.items():
            if tok in words:
                counts[name] += 1
    out = {f"{name}_rate": 100.0 * c / word_count for name, c in counts.items()}
    out["question_mark_rate"] = 100.0 * toks.count("?") / word_count
    out["token_count_anchor"] = float(word_count)
    other = out["second_person_rate"] + out["third_person_rate"] + out["general_people_rate"]
    out["self_other_balance"] = out["self_focus_rate"] - other
    out["agency_communion_balance"] = out["agency_rate"] - out["communion_rate"]
    out["affect_balance"] = out["positive_affect_rate"] - out["negative_affect_rate"]
    out["temporal_balance"] = out["past_temporal_rate"] - out["future_temporal_rate"]
    out["certainty_balance"] = out["certainty_rate"] - out["uncertainty_rate"]
    out["narrative_integration_rate"] = (
        out["mentalization_rate"] + out["temporal_sequence_rate"] + out["causal_meaning_rate"])
    out["projective_tension_rate"] = (
        out["negative_affect_rate"] + out["conflict_threat_rate"] + out["uncertainty_rate"])
    out["directive_interpersonal_blend"] = float(
        np.sqrt(max(0.0, out["directive_rate"]) * max(0.0, out["second_person_rate"])))
    out["growth_after_tension_blend"] = float(np.sqrt(
        max(0.0, out["redemption_growth_rate"]) * max(0.0, out["conflict_threat_rate"] + out["negative_affect_rate"])))
    return out


def score_slices_v4(slice_frame, *, adversity_context_window: int = 10):
    """v4 twin of suica_v2_lib.score_slices_v2 (same construct formulas)."""
    import pandas as pd
    from scripts.build_suica_adversity_recovery_core_v1 import adversity_recovery_features
    rates = pd.DataFrame([score_text_anchors_v4(t) for t in slice_frame["slice_text"].fillna("")],
                         index=slice_frame.index)
    adv = pd.DataFrame(
        [adversity_recovery_features(t, context_window=adversity_context_window)
         for t in slice_frame["slice_text"].fillna("")], index=slice_frame.index)
    out = pd.concat([slice_frame, rates, adv[["adversity_recovery_score"]]], axis=1)
    out["novelty_play_v2"] = out["novelty_play_rate"]
    out["directive_action_v2"] = out["directive_interpersonal_blend"]
    out["adversity_recovery_v2"] = 0.6 * out["adversity_recovery_score"] + 0.4 * out["redemption_growth_rate"]
    out["first_person_usage_v2"] = out["self_focus_rate"]
    out["tension_core_v2"] = (
        0.40 * out["projective_tension_rate"] + 0.35 * out["uncertainty_rate"] + 0.25 * out["conflict_threat_rate"])
    return out


def selftest() -> dict:
    import json
    import numpy as np
    import pandas as pd
    from scripts.suica_v2_lib import score_slices_v2

    # S1 disjointness
    seen: dict[str, str] = {}
    for name, words in ANCHOR_LEXICONS_V4.items():
        for w in words:
            assert w not in seen, f"{w} in both {seen[w]} and {name}"
            seen[w] = name
    # S2 battery equivalence on real slices
    frame = pd.read_parquet(ROOT / "data_sets" / "prepared" / "suica_tiers_v2" / "op9_half_slices.parquet")
    sub = frame.head(500)[["user_id", "slice_text"]].reset_index(drop=True)
    v3 = score_slices_v2(sub.copy())
    v4 = score_slices_v4(sub.copy())
    battery = ["first_person_usage_v2", "directive_action_v2", "tension_core_v2",
               "novelty_play_v2", "adversity_recovery_v2"]
    max_diff = float(max((v3[c] - v4[c]).abs().max() for c in battery))
    # S3 changed derived rates
    rate_cols = [c for c in v3.columns if c.endswith("_rate") and c in v4.columns]
    shifts = {c: float((v4[c] - v3[c]).mean()) for c in rate_cols
              if float((v4[c] - v3[c]).abs().max()) > 0}
    res = {"S1_disjoint": True, "n_words_v3": sum(len(v) for v in ANCHOR_LEXICONS_V3.values()),
           "n_words_v4": sum(len(v) for v in ANCHOR_LEXICONS_V4.values()),
           "n_moves": len(WORD_MOVES),
           "S2_battery_max_abs_diff": max_diff, "S2_pass_bit_identical": bool(max_diff == 0.0),
           "S3_changed_rates_mean_shift": {k: round(v, 5) for k, v in sorted(shifts.items())}}
    out_dir = ROOT / "results" / "suica_v4_scorer"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "v4_selftest.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    r = selftest()
    sys.exit(0 if r["S2_pass_bit_identical"] else 1)
