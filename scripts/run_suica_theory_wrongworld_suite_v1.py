#!/usr/bin/env python
"""Wrong-world suite v1 — no-lock theory falsification (FALSIFIER_MATRIX rows
T2/T3/T4/T5/T10/T11).

Each world instantiates a VIOLATION of one theory assumption and asks whether
the SUICA estimator layer distinguishes truth from violation. Pre-committed
criteria live in docs/SUICA_FALSIFIER_MATRIX_V1.md and are restated per world
below. Feature-level worlds generate y directly under the model equation
(y = flesh + rind + gamma + e); W-E is text-level and exercises the real
slicer, leak mask, and scorer.

Estimator notes (disclosed):
- Choice AUC / retest reimplement the E3 math (share vectors, cosine,
  same-user vs random-pair AUC; log-ratio axis retest) on the simulated
  choice tables — same estimator definitions, compact implementation.
- The decomposition estimators validated here (shared-set vs
  condition-disjoint retest; cross-fitted venue-mix covariance share) are
  the SAME ones applied to real Tier-U data by
  run_suica_c2_purity_decomposition_v1.py. W-B/W-B2 are their license.

Key design fact (derived in THEORY_FORMAL_NOTES, Prop F2): with a SHARED
condition set, the choice-mediated mix term is identical in both halves and
survives as between-person variance — shared-set retest CANNOT purify flesh.
With DISJOINT condition sets, independent rind effects AND choice
independent of b (F3 as corrected in round 9), cov(mix_A, mix_B) = 0 — the
disjoint-set estimand isolates flesh (+ mean-gamma). Class-level correlation
of rind effects re-introduces mediation; W-B2c implements that world and
licenses the CLASS-disjoint estimand (the basis of the novelty relabel).

Round-9 hardening: each world draws from its OWN seeded generator
(SEED + fixed offset), so adding/reordering worlds can never shift another
world's stream (the v1 shared-stream design made W-E's survivor count
stream-fragile — audit finding).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_DIR = ROOT / "results" / "suica_theory_wrongworld_suite_v1"
REPORT = ROOT / "reports" / "suica_theory_wrongworld_suite_v1.md"
SEED = 42
N_USERS = 800
N_VENUES = 30
SLICES_PER_HALF = 24


# ---------------------------------------------------------------------------
# generators
# ---------------------------------------------------------------------------
def make_world(rng, *, n_users=N_USERS, n_venues=N_VENUES, n_half=SLICES_PER_HALF,
               flesh_sd=1.0, rind_sd=1.0, gamma_sd=0.0, noise_sd=2.0,
               choice_coupling="person", choice_conc=1.5, flesh_pref_kappa=0.0):
    """Return (long df with user, half, venue, y) + truth dict.

    choice_coupling:
      'person'  — each user has a stable Dirichlet preference (self-selection)
      'trend'   — venue distribution is a global drifting trend, identical for
                  all users within a period (W-A: choice-null)
    flesh_pref_kappa — Cov(f, m) coupling: preference weights tilted toward
      style-congruent venues, w_ur ∝ base_ur * exp(kappa * f_u * b_r) (W-B3).
    """
    flesh = rng.normal(0, flesh_sd, n_users)
    rind = rng.normal(0, rind_sd, n_venues)
    rows = []
    prefs = rng.dirichlet(np.full(n_venues, choice_conc / n_venues), size=n_users)
    if flesh_pref_kappa:
        tilt = np.exp(flesh_pref_kappa * np.outer(flesh, rind))
        prefs = prefs * tilt
        prefs = prefs / prefs.sum(axis=1, keepdims=True)
    for h, half in enumerate(["early", "late"]):
        if choice_coupling == "trend":
            trend = rng.dirichlet(np.full(n_venues, choice_conc / n_venues))
        for u in range(n_users):
            p = prefs[u] if choice_coupling == "person" else trend
            venues = rng.choice(n_venues, size=n_half, p=p)
            g = rng.normal(0, gamma_sd, n_venues) if gamma_sd else np.zeros(n_venues)
            y = flesh[u] + rind[venues] + g[venues] + rng.normal(0, noise_sd, n_half)
            for v, yy in zip(venues, y):
                rows.append((u, half, int(v), float(yy)))
    df = pd.DataFrame(rows, columns=["user", "half", "venue", "y"])
    return df, {"flesh": flesh, "rind": rind, "prefs": prefs}


# ---------------------------------------------------------------------------
# estimators (E3-math choice metrics; retest estimands; decomposition)
# ---------------------------------------------------------------------------
def choice_metrics(df, rng):
    tab = df.groupby(["user", "half", "venue"]).size().unstack(fill_value=0)
    e = tab.xs("early", level="half").reindex(columns=range(N_VENUES), fill_value=0)
    l = tab.xs("late", level="half").reindex(columns=range(N_VENUES), fill_value=0)
    common = e.index.intersection(l.index)
    E = (e.loc[common].T / e.loc[common].sum(1)).T.to_numpy()
    L = (l.loc[common].T / l.loc[common].sum(1)).T.to_numpy()

    def cos(a, b):
        d = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
        return np.where(d > 0, (a * b).sum(1) / d, np.nan)

    same = cos(E, L)
    perm = rng.permutation(len(common))
    perm = np.where(perm == np.arange(len(common)), (perm + 1) % len(common), perm)
    rand = cos(E, L[perm])
    # EXACT frozen E3 convention (run_suica_e3_e4...v2:123): strict pairwise
    # P(same > rand); ties count as losses (conservative). Suite defect log:
    # v1's first draft used tie-unsafe ranks and fabricated AUC on the
    # heavily-tied null world — suites must replicate frozen estimator
    # conventions exactly (same principle as the P0 scorer-equivalence gate).
    rand_sorted = np.sort(rand)
    auc_strict = float((same[:, None] > rand_sorted[None, :]).mean())
    auc_mid = auc_strict + 0.5 * float((same[:, None] == rand_sorted[None, :]).mean())
    eps = 1e-4
    SE = np.log((E + eps) / (E.mean(0) + eps)); SL = np.log((L + eps) / (L.mean(0) + eps))
    ax_r = [stats.pearsonr(SE[:, k], SL[:, k]).statistic for k in range(N_VENUES)
            if SE[:, k].std() > 0 and SL[:, k].std() > 0]
    return {"choice_auc_strict_frozen": auc_strict, "choice_auc_mid_tie": float(auc_mid),
            "axis_retest_median_abs": float(np.median(np.abs(ax_r)))}


def retest_estimands(df):
    """rho_raw (all slices), rho_shared (same condition-set), rho_disjoint
    (user's venues split into two disjoint sets, early set A vs late set B)."""
    um = df.groupby(["user", "half"])["y"].mean().unstack()
    rho_raw = float(um["early"].corr(um["late"]))

    cell = df.groupby(["user", "half", "venue"])["y"].mean().unstack("half")
    both = cell.dropna()
    shared_e = both["early"].groupby(level="user").mean()
    shared_l = both["late"].groupby(level="user").mean()
    rho_shared = float(shared_e.corr(shared_l))

    e_parts, l_parts = {}, {}
    for u, g in both.groupby(level="user"):
        venues = g.index.get_level_values("venue").to_numpy()
        if len(venues) < 2:
            continue
        setA, setB = venues[0::2], venues[1::2]
        e_parts[u] = g.loc[(u, setA), "early"].mean()
        l_parts[u] = g.loc[(u, setB), "late"].mean()
    sA, sB = pd.Series(e_parts), pd.Series(l_parts)
    rho_disjoint = float(sA.corr(sB))
    return {"rho_raw": rho_raw, "rho_shared_set": rho_shared, "rho_disjoint_set": rho_disjoint}


def crossfit_mix_share(df, n_folds=2, rng=None):
    """Covariance-accounting estimator: share of raw early-late covariance
    attributable to the venue-mix term, with venue effects cross-fitted on
    the OTHER user fold (no self-estimation leak, per the E1 lesson)."""
    users = df["user"].unique()
    rng = rng or np.random.default_rng(0)
    fold = pd.Series(rng.integers(0, n_folds, len(users)), index=users)
    mix = {}
    for f in range(n_folds):
        train = df[df["user"].map(fold) != f]
        vhat = train.groupby("venue")["y"].mean() - train["y"].mean()
        test = df[df["user"].map(fold) == f].copy()
        test["vhat"] = test["venue"].map(vhat).fillna(0.0)
        m = test.groupby(["user", "half"])["vhat"].mean().unstack()
        for u in m.index:
            mix[u] = (m.at[u, "early"], m.at[u, "late"])
    mixdf = pd.DataFrame(mix, index=["mix_e", "mix_l"]).T
    um = df.groupby(["user", "half"])["y"].mean().unstack()
    j = um.join(mixdf).dropna()
    j["f_e"] = j["early"] - j["mix_e"]; j["f_l"] = j["late"] - j["mix_l"]
    cov_raw = float(np.cov(j["early"], j["late"])[0, 1])
    cov_mix = float(np.cov(j["mix_e"], j["mix_l"])[0, 1])
    cov_flesh = float(np.cov(j["f_e"], j["f_l"])[0, 1])
    return {"cov_raw": cov_raw, "cov_mix": cov_mix, "cov_flesh_hat": cov_flesh,
            "mix_share": float(np.clip(cov_mix / cov_raw, 0, 1)) if cov_raw > 0 else np.nan,
            "mediated_total": float(np.clip(1 - cov_flesh / cov_raw, 0, 1)) if cov_raw > 0 else np.nan}


# ---------------------------------------------------------------------------
# worlds
# ---------------------------------------------------------------------------
def world_A(rng):
    """Choice-null: venue assignment is a global drifting trend. Two sparsity
    regimes (ultra-sparse alpha=0.05 and moderate alpha=0.5). Fabrication
    check on the tie-corrected mid AUC; the frozen strict AUC must never
    EXCEED the band (it may deflate under ties — conservative direction)."""
    out = {}
    ok = True
    for tag, conc in [("sparse", 1.5), ("moderate", 15.0)]:
        df, _ = make_world(rng, choice_coupling="trend", choice_conc=conc)
        m = choice_metrics(df, rng)
        m["pass"] = bool(0.45 <= m["choice_auc_mid_tie"] <= 0.55
                         and m["choice_auc_strict_frozen"] <= 0.55
                         and m["axis_retest_median_abs"] < 0.10)
        ok = ok and m["pass"]
        out[tag] = m
    out["criterion"] = ("mid-tie AUC in [0.45,0.55] AND frozen strict AUC <= 0.55 "
                        "AND axis median |r| < 0.10, at both sparsity levels")
    out["pass"] = ok
    return out


def world_B(rng):
    """Flesh-null: no person style at all; choice person-stable; venues styled."""
    df, _ = make_world(rng, flesh_sd=0.0, rind_sd=1.0, noise_sd=2.0)
    r = retest_estimands(df)
    c = crossfit_mix_share(df, rng=rng)
    r.update(c)
    r["criterion"] = ("EXPECT rho_raw AND rho_shared inflated (>0.15) while "
                      "rho_disjoint <= 0.10 and mix_share >= 0.80")
    r["pass"] = bool(r["rho_raw"] > 0.15 and r["rho_shared_set"] > 0.15
                     and abs(r["rho_disjoint_set"]) <= 0.10 and r["mix_share"] >= 0.80)
    return r


def world_B2(rng):
    """Mixed grid: recover planted flesh share within +/-0.10 (9 cells)."""
    cells = []
    for flesh_sd in (0.5, 1.0, 1.5):
        for conc in (0.8, 1.5, 3.0):
            df, truth = make_world(rng, flesh_sd=flesh_sd, rind_sd=1.0,
                                   noise_sd=2.0, choice_conc=conc)
            um = df.groupby(["user", "half"])["y"].mean().unstack()
            # planted decomposition of cov(raw_e, raw_l)
            prefs = truth["prefs"]; rind = truth["rind"]; flesh = truth["flesh"]
            planted_mix_cov = float(np.cov(prefs @ rind, prefs @ rind)[0, 1])
            # empirical realized mixes differ per half; use expectation as target
            var_flesh = float(np.var(flesh))
            target_share = planted_mix_cov / (planted_mix_cov + var_flesh)
            est = crossfit_mix_share(df, rng=rng)["mix_share"]
            cells.append({"flesh_sd": flesh_sd, "conc": conc,
                          "target_mix_share": round(target_share, 3),
                          "estimated_mix_share": round(float(est), 3),
                          "abs_err": round(abs(est - target_share), 3)})
    max_err = max(c["abs_err"] for c in cells)
    return {"grid": cells, "max_abs_err": max_err,
            "criterion": "max |est - target| <= 0.10 over 3x3 grid",
            "pass": bool(max_err <= 0.10)}


def world_B2c(rng):
    """Class-correlated venue effects: b_r = c_class(r) + v_r. Licenses the
    CLASS-disjoint estimand: with prefs independent of b, the class-disjoint
    arm covariance must read Var(f) (flesh), while the condition-disjoint
    arms retain the shared-class term and must over-read by a visible margin.
    Pre-committed: |cov_class_disjoint - Var(f)| <= 0.15 AND
    cov_cond_disjoint >= cov_class_disjoint + 0.05."""
    n_users, n_classes, per_class = N_USERS, 6, 5
    n_venues = n_classes * per_class
    flesh = rng.normal(0, 1.0, n_users)
    cls = np.repeat(np.arange(n_classes), per_class)
    b = rng.normal(0, 0.8, n_classes)[cls] + rng.normal(0, 0.6, n_venues)
    prefs = rng.dirichlet(np.full(n_venues, 3.0 / n_venues), size=n_users)
    rows = []
    for half in ("early", "late"):
        for u in range(n_users):
            venues = rng.choice(n_venues, size=SLICES_PER_HALF, p=prefs[u])
            y = flesh[u] + b[venues] + rng.normal(0, 2.0, SLICES_PER_HALF)
            rows += [(u, half, int(v), float(yy)) for v, yy in zip(venues, y)]
    df = pd.DataFrame(rows, columns=["user", "half", "venue", "y"])
    cell = df.groupby(["user", "half", "venue"])["y"].mean().unstack("half").dropna()

    def arm_cov(assign_by_class: bool) -> float:
        e1, l1, e2, l2 = {}, {}, {}, {}
        for u, g in cell.groupby(level=0):
            venues = g.index.get_level_values("venue").to_numpy()
            if assign_by_class:
                classes = sorted({int(cls[v]) for v in venues})
                if len(classes) < 2:
                    continue
                inA = {c for c in classes[0::2]}
                A = [v for v in venues if cls[v] in inA]
                B = [v for v in venues if cls[v] not in inA]
            else:
                A, B = list(venues[0::2]), list(venues[1::2])
            if not A or not B:
                continue
            gA = g.loc[[(u, v) for v in A]]; gB = g.loc[[(u, v) for v in B]]
            e1[u], l1[u] = gA["early"].mean(), gB["late"].mean()
            e2[u], l2[u] = gB["early"].mean(), gA["late"].mean()
        c1 = float(np.cov(pd.Series(e1), pd.Series(l1).reindex(pd.Series(e1).index))[0, 1])
        c2 = float(np.cov(pd.Series(e2), pd.Series(l2).reindex(pd.Series(e2).index))[0, 1])
        return (c1 + c2) / 2

    var_f = float(np.var(flesh))
    cov_cond = arm_cov(False)
    cov_cls = arm_cov(True)
    return {"planted_var_f": round(var_f, 3),
            "cov_cond_disjoint": round(cov_cond, 3),
            "cov_class_disjoint": round(cov_cls, 3),
            "class_mediation_bias_removed": round(cov_cond - cov_cls, 3),
            "criterion": "|cov_class_disjoint - Var(f)| <= 0.15 AND cov_cond >= cov_class + 0.05",
            "pass": bool(abs(cov_cls - var_f) <= 0.15 and cov_cond >= cov_cls + 0.05)}


def world_B3(rng):
    """Flesh-coupled choice (Cov(f,m) != 0, F3): tense people choose tense
    venues (kappa=0.7). Validates the fhat-based mediated_total estimator
    under correlation, and DEMONSTRATES the disjoint-set upper-bound bias."""
    df, truth = make_world(rng, flesh_sd=1.0, rind_sd=1.0, noise_sd=2.0,
                           choice_conc=3.0, flesh_pref_kappa=0.7)
    f, b, prefs = truth["flesh"], truth["rind"], truth["prefs"]
    m_true = prefs @ b
    var_f, var_m = float(np.var(f)), float(np.var(m_true))
    cov_fm = float(np.cov(f, m_true)[0, 1])
    target = (var_m + 2 * cov_fm) / (var_f + var_m + 2 * cov_fm)
    est = crossfit_mix_share(df, rng=rng)
    r = retest_estimands(df)
    pure_flesh_rho = var_f / (var_f + var_m + 2 * cov_fm + 0.0)  # vs raw stable var
    out = {"planted": {"var_f": round(var_f, 3), "var_m": round(var_m, 3),
                       "cov_fm": round(cov_fm, 3), "mediated_total_target": round(target, 3)},
           "estimated_mediated_total": round(float(est["mediated_total"]), 3),
           "abs_err": round(abs(est["mediated_total"] - target), 3),
           "rho_cond_disjoint_observed": round(r["rho_disjoint_set"], 3),
           "note_F3_bias": ("disjoint-set retains the 2Cov(f,m) cross-term -> expected to "
                            f"exceed the pure-flesh share {round(pure_flesh_rho,3)} of stable variance"),
           "criterion": "|estimated - target| <= 0.10 under Cov(f,m) != 0",
           "pass": bool(abs(est["mediated_total"] - target) <= 0.10)}
    return out


def world_PHASE(rng):
    """F4 phase diagram: centering effect sign must match the derivation
    -(Var(m) + 2Cov(f,m)) across regimes: exogenous (trend), person kappa=0,
    person kappa=0.7."""
    cells = []
    ok = True
    for tag, kwargs in [("exogenous", {"choice_coupling": "trend", "choice_conc": 15.0}),
                        ("person_k0", {"choice_conc": 3.0}),
                        ("person_k07", {"choice_conc": 3.0, "flesh_pref_kappa": 0.7})]:
        df, truth = make_world(rng, flesh_sd=1.0, rind_sd=1.0, noise_sd=2.0, **kwargs)
        est = crossfit_mix_share(df, rng=rng)
        # centered retest covariance = cov(fhat_e, fhat_l); raw = cov_raw
        delta = est["cov_flesh_hat"] - est["cov_raw"]
        if kwargs.get("choice_coupling") == "trend":
            pred = 0.0
        else:
            f, b, prefs = truth["flesh"], truth["rind"], truth["prefs"]
            m = prefs @ b
            pred = -(float(np.var(m)) + 2 * float(np.cov(f, m)[0, 1]))
        cell_ok = (abs(delta - pred) <= 0.10) and (delta < -0.02 if pred < -0.02 else abs(delta) <= 0.06)
        cells.append({"regime": tag, "delta_cov_centered_minus_raw": round(delta, 3),
                      "predicted_delta": round(pred, 3), "ok": bool(cell_ok)})
        ok = ok and cell_ok
    return {"cells": cells,
            "criterion": "sign and magnitude (+/-0.10) match -(Var(m)+2Cov(f,m)) per regime; ~0 under exogenous",
            "pass": bool(ok)}


def world_C(rng):
    """Timescale aliasing: weekly AR(1) states, no month-native process.
    Month machinery must not exceed the ANALYTIC aliased expectation band."""
    n_users, n_weeks, per_week = 300, 24, 6
    rho_w, state_sd, noise_sd = 0.5, 1.0, 2.0
    rows = []
    for u in range(n_users):
        s = np.zeros(n_weeks); s[0] = rng.normal(0, state_sd)
        for t in range(1, n_weeks):
            s[t] = rho_w * s[t - 1] + rng.normal(0, state_sd * np.sqrt(1 - rho_w**2))
        for w in range(n_weeks):
            for _ in range(per_week):
                rows.append((u, w // 4, w, s[w] + rng.normal(0, noise_sd)))
    df = pd.DataFrame(rows, columns=["user", "month", "week", "y"])
    dm = df.groupby(["user", "month"])["y"].mean().reset_index()
    dm["y"] = dm["y"] - dm.groupby("user")["y"].transform("mean")
    lag = dm.merge(dm.assign(month=dm["month"] + 1), on=["user", "month"], suffixes=("", "_prev"))
    obs_lag1 = float(lag["y"].corr(lag["y_prev"]))
    # analytic aliased expectation: month mean of 4 weekly AR(1) states + noise
    G = np.array([[rho_w ** abs(i - j) for j in range(8)] for i in range(8)]) * state_sd**2
    var_m = G[:4, :4].mean() + noise_sd**2 / (4 * per_week)
    cov_mm = G[:4, 4:].mean()
    exp_lag1 = cov_mm / var_m  # within-person centering shrinks both similarly; band below
    band = 0.12  # pre-committed tolerance for centering distortion + sampling
    fabricated = bool(obs_lag1 > exp_lag1 + band)
    return {"observed_month_lag1": round(obs_lag1, 3),
            "analytic_aliased_lag1": round(float(exp_lag1), 3), "band": band,
            "criterion": "observed <= analytic + band (no fabrication of month-native persistence)",
            "pass": (not fabricated)}


def world_D(rng):
    """Norm-only react world: gamma = class norms, zero person-specificity.
    Matched same-vs-stranger congruence increment must be null (FPR <= 0.05
    over 100 cohorts)."""
    n_users, n_classes, per_class = 60, 8, 10
    hits = 0
    n_coh = 100
    for _ in range(n_coh):
        norms = rng.normal(0, 1.0, n_classes)
        prof_e = norms + rng.normal(0, 1.0, (n_users, n_classes)) / np.sqrt(per_class)
        prof_l = norms + rng.normal(0, 1.0, (n_users, n_classes)) / np.sqrt(per_class)
        pe = prof_e - prof_e.mean(0); pl = prof_l - prof_l.mean(0)

        def cong(a, b):
            n = np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1)
            return np.where(n > 0, (a * b).sum(1) / n, np.nan)

        same = np.nanmedian(cong(pe, pl))
        perm = rng.permutation(n_users)
        perm = np.where(perm == np.arange(n_users), (perm + 1) % n_users, perm)
        strangers = np.nanmedian(cong(pe, pl[perm]))
        boots = []
        for _ in range(200):
            idx = rng.integers(0, n_users, n_users)
            p2 = rng.permutation(n_users)
            p2 = np.where(p2 == np.arange(n_users), (p2 + 1) % n_users, p2)
            boots.append(np.nanmedian(cong(pe[idx], pl[idx])) - np.nanmedian(cong(pe[idx], pl[p2][idx])))
        lo = np.percentile(boots, 2.5)
        if lo > 0:
            hits += 1
    return {"fpr_increment_ci_above_zero": hits / n_coh, "n_cohorts": n_coh,
            "criterion": "FPR <= 0.05", "pass": bool(hits / n_coh <= 0.05)}


def world_E(rng):
    """Leak-only world (text level, real slicer+mask+scorer): trait signal
    exists ONLY via PERSONALITY_LEAK_RE-matchable phrases."""
    from suica_core.suica import PERSONALITY_LEAK_RE, fixed_token_slices_for_text
    from scripts.suica_v2_lib import score_slices_v2

    neutral = ["the weather was fine and we walked to the station today",
               "dinner was curry again and the train ran a little late",
               "meeting starts at three so i printed the papers",
               "bought milk and bread at the store near the corner",
               "the game loaded slowly but the second match went fine"]
    leak = ["as an INTJ i plan everything early", "typical ENFP moment honestly",
            "my MBTI is INFP and it shows", "took the 16personalities test again",
            "fellow introverts will understand this", "being an extrovert helps here"]
    n_users, n_sent = 120, 60
    trait = rng.uniform(0, 0.5, n_users)
    rows = []
    for u in range(n_users):
        sents = [leak[rng.integers(len(leak))] if rng.random() < trait[u]
                 else neutral[rng.integers(len(neutral))] for _ in range(n_sent)]
        text = ". ".join(sents)
        for r in fixed_token_slices_for_text(text, slice_tokens=64, stride=64,
                                             min_slice_tokens=16, max_slices=40):
            rows.append({"user_id": u, "slice_text": r["slice_text"],
                         "leak_hit": bool(PERSONALITY_LEAK_RE.search(r["slice_text"]))})
    df = pd.DataFrame(rows)
    hit_rate = float(df.groupby("user_id")["leak_hit"].mean().mean())
    kept = df[~df["leak_hit"]].copy()
    scored_all = score_slices_v2(df[["user_id", "slice_text"]])
    scored_kept = score_slices_v2(kept[["user_id", "slice_text"]]) if len(kept) else None
    cols = ["first_person_usage_v2", "tension_core_v2", "novelty_play_v2", "directive_action_v2"]
    rec_unmasked = max(abs(float(np.corrcoef(trait, scored_all.groupby("user_id")[c].mean()
                                             .reindex(range(n_users)).fillna(0))[0, 1])) for c in cols)
    um = scored_kept.groupby("user_id")[cols].mean().reindex(range(n_users)) if scored_kept is not None else None
    n_surv = int(um.notna().all(1).sum()) if um is not None else 0
    if n_surv >= 60:
        mask_ok = um.notna().all(1)
        rec_masked = max(abs(float(np.corrcoef(trait[mask_ok], um.loc[mask_ok, c])[0, 1])) for c in cols)
        null95 = 2.0 / np.sqrt(n_surv)
    else:
        rec_masked, null95 = np.nan, np.nan
    return {"slice_leak_detection_rate": hit_rate, "n_surviving_users": n_surv,
            "recovery_unmasked_maxr": round(rec_unmasked, 3),
            "recovery_after_mask_maxr": round(float(rec_masked), 3),
            "null95_at_n_surv": round(float(null95), 3),
            "criterion": ("positive control unmasked > 0.30; after mask <= null95 among "
                          "surviving users (the production estimand: masked slices are dropped)"),
            "pass": bool(rec_unmasked > 0.30 and n_surv >= 60 and rec_masked <= null95)}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    worlds = [("W_A_choice_null", world_A), ("W_B_flesh_null", world_B),
              ("W_B2_recovery_grid", world_B2), ("W_B2c_class_correlated", world_B2c),
              ("W_B3_flesh_coupled_choice", world_B3),
              ("W_PHASE_centering_boundary", world_PHASE),
              ("W_C_timescale_alias", world_C),
              ("W_D_react_norm_only", world_D), ("W_E_leak_mask", world_E)]
    for offset, (name, fn) in enumerate(worlds):
        results[name] = fn(np.random.default_rng(SEED + 1000 * offset))
        print(f"[{name}] pass={results[name]['pass']}")
    results["ALL_PASS"] = all(v["pass"] for k, v in results.items() if k != "ALL_PASS")
    (OUT_DIR / "wrongworld_results.json").write_text(json.dumps(results, indent=2, default=float) + "\n")
    lines = ["# Wrong-world suite v1 (no-lock theory falsification)", ""]
    for k, v in results.items():
        if k == "ALL_PASS":
            continue
        lines.append(f"## {k}\n\n```json\n" + json.dumps(v, indent=2, default=float) + "\n```\n")
    lines.append(f"\n**ALL_PASS = {results['ALL_PASS']}**\n")
    REPORT.write_text("\n".join(lines))
    print("ALL_PASS =", results["ALL_PASS"])


if __name__ == "__main__":
    main()
