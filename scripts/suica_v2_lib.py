#!/usr/bin/env python
"""Shared estimators for SUICA v2 validation (plan v2, Phases 1-2).

Design contract:
- Construct formulas are the frozen v2 set in docs/SUICA_CLAIMS_LEDGER.md.
- Condition centering uses leave-one-user-out population means (review fix).
- No function in this module reads Big5/MBTI label values.
- `fast_anchor_rates` must stay numerically equivalent to the frozen v1 scorer
  `score_text_anchors`; `check_scorer_equivalence` enforces this and P0 runs it.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_narrative_projective_anchor_validation_v2 import (  # noqa: E402
    ANCHOR_LEXICONS,
    TOKEN_RE,
    score_text_anchors,
)
from scripts.build_suica_adversity_recovery_core_v1 import adversity_recovery_features  # noqa: E402

V2_CONSTRUCTS = [
    "novelty_play_v2",
    "directive_action_v2",
    "adversity_recovery_v2",
    "first_person_usage_v2",
    "tension_core_v2",
]

_RATE_NAMES = sorted(ANCHOR_LEXICONS)
_WORD_TO_CATS: dict[str, list[str]] = {}
for _name, _words in ANCHOR_LEXICONS.items():
    for _w in _words:
        _WORD_TO_CATS.setdefault(_w, []).append(_name)


def fast_anchor_rates(text: str) -> dict[str, float]:
    """One-pass equivalent of the frozen v1 lexicon scorer (subset of columns)."""
    toks = [tok.lower() for tok in TOKEN_RE.findall(str(text or ""))]
    word_count = max(1, sum(tok != "?" for tok in toks))
    counts = Counter(toks)
    cat_counts: dict[str, int] = {name: 0 for name in _RATE_NAMES}
    for tok, n in counts.items():
        for cat in _WORD_TO_CATS.get(tok, ()):
            cat_counts[cat] += n
    out = {f"{name}_rate": 100.0 * cat_counts[name] / word_count for name in _RATE_NAMES}
    out["token_count_anchor"] = float(word_count)
    out["projective_tension_rate"] = (
        out["negative_affect_rate"] + out["conflict_threat_rate"] + out["uncertainty_rate"]
    )
    out["directive_interpersonal_blend"] = float(
        np.sqrt(max(0.0, out["directive_rate"]) * max(0.0, out["second_person_rate"]))
    )
    return out


def check_scorer_equivalence(texts: list[str], *, atol: float = 1e-9) -> float:
    """Max abs difference between fast scorer and frozen v1 scorer on shared keys."""
    worst = 0.0
    for text in texts:
        ref = score_text_anchors(text)
        fast = fast_anchor_rates(text)
        for key, val in fast.items():
            if key in ref:
                worst = max(worst, abs(float(ref[key]) - float(val)))
    if worst > atol:
        raise AssertionError(f"fast scorer diverges from frozen v1 scorer: max diff {worst}")
    return worst


def score_slices_v2(slice_frame: pd.DataFrame, *, adversity_context_window: int = 10) -> pd.DataFrame:
    """Compute the 5 frozen v2 construct scores per slice. Needs `slice_text`."""
    rates = pd.DataFrame([fast_anchor_rates(t) for t in slice_frame["slice_text"].fillna("")], index=slice_frame.index)
    adv = pd.DataFrame(
        [adversity_recovery_features(t, context_window=adversity_context_window) for t in slice_frame["slice_text"].fillna("")],
        index=slice_frame.index,
    )
    out = pd.concat([slice_frame, rates, adv[["adversity_recovery_score"]]], axis=1)
    out["novelty_play_v2"] = out["novelty_play_rate"]
    out["directive_action_v2"] = out["directive_interpersonal_blend"]
    out["adversity_recovery_v2"] = 0.6 * out["adversity_recovery_score"] + 0.4 * out["redemption_growth_rate"]
    out["first_person_usage_v2"] = out["self_focus_rate"]
    out["tension_core_v2"] = (
        0.40 * out["projective_tension_rate"] + 0.35 * out["uncertainty_rate"] + 0.25 * out["conflict_threat_rate"]
    )
    return out


def loo_condition_center(long: pd.DataFrame, value_col: str, *, group_cols: tuple[str, ...] = ("condition",)) -> pd.Series:
    """Leave-one-user-out condition centering of slice scores.

    For each slice, subtract the mean of `value_col` over all OTHER users'
    slices in the same condition group. Falls back to the plain group mean when
    the user is the only author in the group.
    """
    keys = list(group_cols)
    grp = long.groupby(keys)[value_col]
    g_sum = grp.transform("sum")
    g_cnt = grp.transform("count")
    ug = long.groupby(keys + ["user_id"])[value_col]
    u_sum = ug.transform("sum")
    u_cnt = ug.transform("count")
    loo_cnt = (g_cnt - u_cnt).clip(lower=0)
    loo_mean = np.where(loo_cnt > 0, (g_sum - u_sum) / loo_cnt.replace(0, np.nan), g_sum / g_cnt)
    return long[value_col] - pd.Series(loo_mean, index=long.index)


def base_from_slices(
    long: pd.DataFrame,
    value_col: str,
    *,
    centered: bool,
    condition_cols: tuple[str, ...] = ("condition",),
) -> pd.DataFrame:
    """Author base score: mean over conditions of (optionally LOO-centered) condition means."""
    work = long.copy()
    score_col = value_col
    if centered:
        work["_centered"] = loo_condition_center(work, value_col, group_cols=condition_cols)
        score_col = "_centered"
    cell = work.groupby(["user_id", *condition_cols], as_index=False)[score_col].mean()
    base = cell.groupby("user_id", as_index=False)[score_col].mean().rename(columns={score_col: "base_score"})
    n_cond = cell.groupby("user_id").size().rename("n_conditions").reset_index()
    return base.merge(n_cond, on="user_id")


def react_signature(
    long: pd.DataFrame,
    value_col: str,
    *,
    condition_cols: tuple[str, ...] = ("condition",),
) -> pd.DataFrame:
    """Per (user, condition) centered react score = condition mean - user base."""
    work = long.copy()
    work["_centered"] = loo_condition_center(work, value_col, group_cols=condition_cols)
    cell = work.groupby(["user_id", *condition_cols], as_index=False).agg(
        cond_mean=("_centered", "mean"), n_slices=("_centered", "size"), cond_var=("_centered", "var")
    )
    base = cell.groupby("user_id")["cond_mean"].transform("mean")
    cell["react_score"] = cell["cond_mean"] - base
    return cell


def noise_corrected_react_amplitude(cell: pd.DataFrame) -> pd.DataFrame:
    """Across-condition react variance minus expected sampling variance, floored at 0."""
    rows = []
    for user_id, group in cell.groupby("user_id"):
        if len(group) < 2:
            continue
        observed = float(group["react_score"].var(ddof=1))
        expected = float((group["cond_var"].fillna(0.0) / group["n_slices"].clip(lower=1)).mean())
        corrected = max(0.0, observed - expected)
        rows.append(
            {
                "user_id": user_id,
                "react_var_observed": observed,
                "react_var_expected_noise": expected,
                "react_amplitude_corrected": float(np.sqrt(corrected)),
            }
        )
    return pd.DataFrame(rows)


def cell_table(long: pd.DataFrame, value_col: str) -> pd.DataFrame:
    """Per (user, condition) cell means/vars/sizes for the MoM decomposition."""
    work = long[["user_id", "condition", value_col]].dropna()
    cell = work.groupby(["user_id", "condition"])[value_col].agg(["mean", "var", "size"]).reset_index()
    return cell.loc[cell["size"] >= 2]


def mom_variance_components(long: pd.DataFrame, value_col: str) -> dict[str, float]:
    """Unweighted-means crossed decomposition: person, condition, interaction, residual.

    Approximate method-of-moments for unbalanced user x condition designs with
    slice replicates. Validated against planted ground truth and MixedLM in P0;
    if P0 flags bias, use MixedLM instead.

    WARNING (round-4 audit, 2026-07-05): in thin-cell / high-residual regimes
    (2-8 slices per cell, residual ~0.9) this estimator is blind to interaction
    shares below ~0.05 and inflates the person share by ~+0.04. Use MixedLM for
    headline decompositions; treat MoM as a fast screen only.
    """
    cell = cell_table(long, value_col)
    return mom_from_cells(cell)


def mom_from_cells(cell: pd.DataFrame) -> dict[str, float]:
    if cell.empty or cell["user_id"].nunique() < 5 or cell["condition"].nunique() < 3:
        return {k: float("nan") for k in ("person", "condition", "interaction", "residual", "person_share")}
    sigma_e = float(np.average(cell["var"].fillna(0.0), weights=cell["size"] - 1))
    n_tilde = float(len(cell) / np.sum(1.0 / cell["size"]))
    m = cell.pivot_table(index="user_id", columns="condition", values="mean")
    grand = float(np.nanmean(m.to_numpy()))
    resid = m - grand
    for _ in range(3):
        resid = resid.sub(resid.mean(axis=1), axis=0)
        resid = resid.sub(resid.mean(axis=0), axis=1)
    row_eff = (m.sub(m.mean(axis=0), axis=1)).mean(axis=1)
    col_eff = (m.sub(m.mean(axis=1), axis=0)).mean(axis=0)
    ms_int = float(np.nanvar(resid.to_numpy(), ddof=1))
    sigma_g = max(0.0, ms_int - sigma_e / n_tilde)
    k_bar = float(m.notna().sum(axis=1).mean())
    u_bar = float(m.notna().sum(axis=0).mean())
    sigma_b = max(0.0, float(row_eff.var(ddof=1)) - (sigma_g + sigma_e / n_tilde) / k_bar)
    sigma_c = max(0.0, float(col_eff.var(ddof=1)) - (sigma_g + sigma_e / n_tilde) / u_bar)
    total = sigma_b + sigma_c + sigma_g + sigma_e
    return {
        "person": sigma_b,
        "condition": sigma_c,
        "interaction": sigma_g,
        "residual": sigma_e,
        "person_share": sigma_b / total if total > 0 else float("nan"),
        "condition_share": sigma_c / total if total > 0 else float("nan"),
        "interaction_share": sigma_g / total if total > 0 else float("nan"),
        "residual_share": sigma_e / total if total > 0 else float("nan"),
    }


def bootstrap_ci(values_fn, users: np.ndarray, *, n_boot: int = 1000, seed: int = 42) -> tuple[float, float, float]:
    """Cluster bootstrap over users. values_fn(user_subset) -> scalar."""
    rng = np.random.default_rng(seed)
    point = float(values_fn(users))
    draws = []
    for _ in range(n_boot):
        sample = rng.choice(users, size=len(users), replace=True)
        draws.append(float(values_fn(sample)))
    lo, hi = np.nanpercentile(draws, [2.5, 97.5])
    return point, float(lo), float(hi)


def spearman_brown(r: float) -> float:
    if not np.isfinite(r) or r <= -1.0:
        return float("nan")
    return 2.0 * r / (1.0 + r)
