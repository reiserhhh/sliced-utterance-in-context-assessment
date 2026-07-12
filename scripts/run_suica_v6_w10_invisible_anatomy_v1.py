#!/usr/bin/env python
"""V6-W10 — anatomy of the motion-only ("invisible") gust factor (F15, registered
commit 52421ea, docs/SUICA_THEORY_FORMAL_NOTES_V3.md). Label-free (Tier-U + Essays
TEXT only; no label column is EVER read — the Essays loader uses usecols=[user_id,
text] exclusively, same governance as run_suica_v6_e2_essays_motion_v1.py).

Known properties going in (F15 registration): the gust1_P factor is stable
(person-disjoint replication .78-.83), theorem-invisible to averaging instruments,
register-local (Essays hosts no invisible gust factor), and carried by the
recurring construct cluster {wcl_02, wcl_07, wcl_11, wcl_20, ...}. NEW HYPOTHESIS
under test here: the invisible factor is a SHARED-RHYTHM component — the
cross-construct face of individual spectral anomalies, rather than a single
construct's own texture.

This script runs three preregistered sub-analyses on the EXISTING (capped) window
caches:

  A. ACTIVATION ANATOMY (PANDORA, texts with m >= 3, all kept windows). Per text,
     each of the 19 construct columns is linearly detrended on [1, j]; residuals
     are standardized by their pooled sd and projected onto the unit gust1_P axis
     to give a per-window activation a_w. a_w and |a_w| are correlated against nine
     window markers (six from raw text: question-mark/quote/digit/comma density,
     ALL-CAPS token share, token count; plus novelty_play_v2 level and its
     window-to-window jump; plus position t), pooled two ways (within-text-centered
     and raw), with a within-text permutation p-value (500 draws) attached to the
     centered statistic (the natural exchangeability null for a within-text-demeaned
     correlation; the raw pooled statistic is NOT null-invariant under a
     within-text-only shuffle because between-text covariance survives it).

  B. PERSON SUSCEPTIBILITY (PANDORA). Users with >= 2 qualifying (m>=3) texts:
     per-text mean |a_w| (susceptibility) and mean signed a_w (direction) are
     split odd/even by each user's own ascending-cid text order (see ambiguity
     note below), then correlated across users (split-half r). An ICC-style
     variance share (between-user / total, on the same per-text |a| pool) is
     also reported.

  C. ESSAYS CONTRAST. The identical activation machinery (A's residual +
     standardize + project) is applied to Essays m>=3 windows. Both corpora's
     per-window activation variance is compared to a MATCHED within-text
     column-shuffle null (200 draws: each of the 19 standardized-residual
     columns is independently permuted within its own text, which destroys
     cross-construct co-movement but preserves each construct's own marginal
     within-text variance) — this is the direct test of the shared-rhythm
     hypothesis. Expectation per the F15 registration: PANDORA ratio >> 1
     (real cross-construct coordination), Essays ratio ~ 1 (no invisible
     factor to coordinate).

DATA / GOVERNANCE NOTE (capped corpus): both window caches come from the CURRENT
CAPPED Tier-U / Essays extraction (docs F14/N1: the existing comment extraction
truncates long bodies, which caps m low — see the m-distribution printed below).
An uncapped re-extraction (tier_u_comments_uncapped_v1.parquet) is registered as
a follow-up AFTER N1 completes; this script's population sizes and window-count
ceiling are expected to grow once that lands. This run is the CAPPED-corpus
version of W10; results here are not the final uncapped read.

Only reads: results/suica_tgeo_p8_functionalization/cache_windows_scored19.parquet,
results/suica_v6_e2_essays_motion/cache_essays_windows_scored19.parquet,
data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet (author, body columns
only, via the P7 build_windows() import), data_sets/prepared/big5/
essays_original_prepared.csv (user_id, text columns ONLY). No label column is
ever read from either corpus. No git commits are made by this script.

Seed: 20260712 (same registration-date seed used by the sibling W2a/W6/E2 scripts).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_persona.suica import PERSONALITY_LEAK_RE, tokenize  # noqa: E402
from scripts.run_suica_tgeo_p7_flow_curve_v1 import build_windows  # noqa: E402
import scripts.run_suica_v6_e2_essays_motion_v1 as e2mod  # noqa: E402
import scripts.run_suica_v6_w2a_delta2_dynamics_v1 as w2a  # noqa: E402

SEED = 20260712
N_PERM = 500
N_NULL_VAR = 200
DRIFT_GUARD = frozenset({"wcl_02", "wcl_11"})

PANDORA_CACHE = ROOT / "results" / "suica_tgeo_p8_functionalization" / "cache_windows_scored19.parquet"
ESSAYS_CACHE = ROOT / "results" / "suica_v6_e2_essays_motion" / "cache_essays_windows_scored19.parquet"
OUT_DIR = ROOT / "results" / "suica_v6_w10_invisible_anatomy"
OUT_JSON = OUT_DIR / "V6_W10_INVISIBLE_ANATOMY.json"
OUT_MD = OUT_DIR / "V6_W10_INVISIBLE_ANATOMY.md"

QUOTE_CHARS = "\"'‘’“”‹›«»"
MARKER_KEYS = ["qmark_per100", "quote_per100", "digit_per100", "comma_per100",
               "allcaps_token_share", "token_count", "novelty_level",
               "novelty_jump", "position_t"]


# --------------------------------------------------------------------------
# Text reconstruction (caches carry no text) + row-for-row alignment
# --------------------------------------------------------------------------

def build_essays_windows_with_text() -> pd.DataFrame:
    """Mirror run_suica_v6_e2_essays_motion_v1.essays_windows()'s internal frame
    build EXACTLY (same WIN/MAX_WINDOWS constants, same leak-mask rule), but keep
    slice_text (the cached parquet drops it before saving). Reads ONLY
    [user_id, text] from the Essays CSV -- no label column is ever touched."""
    df = pd.read_csv(e2mod.ESSAYS, usecols=["user_id", "text"])  # LABELS NEVER LOADED
    df = df.dropna(subset=["text"])
    rows = []
    for eid, (uid, text) in enumerate(zip(df["user_id"], df["text"].astype(str))):
        tokens = tokenize(text)
        m = len(tokens) // e2mod.WIN
        if m < 2:
            continue
        keep = (np.unique(np.round(np.linspace(0, m - 1, e2mod.MAX_WINDOWS)).astype(int))
                if m > e2mod.MAX_WINDOWS else np.arange(m))
        wrows, ok = [], True
        for j in keep:
            wtext = " ".join(tokens[j * e2mod.WIN:(j + 1) * e2mod.WIN])
            if PERSONALITY_LEAK_RE.search(wtext):
                ok = False
                break
            wrows.append({"eid": eid, "user_id": str(uid), "j": int(j), "m": int(m),
                          "t": float(j / (m - 1)), "slice_text": wtext})
        if ok:
            rows.extend(wrows)
    return pd.DataFrame(rows)


def align_with_text(cache_df: pd.DataFrame, text_df: pd.DataFrame, id_col: str) -> tuple:
    """Merge slice_text into the scored cache by (id_col, j); assert a clean
    row-for-row match on (id_col, j, m). Returns (merged_df, diagnostics)."""
    n_cache, n_rebuilt = len(cache_df), len(text_df)
    assert n_cache == n_rebuilt, (
        f"[{id_col}] row-count mismatch: cache={n_cache} rebuilt={n_rebuilt}")
    merge_cols = text_df[[id_col, "j", "m", "slice_text"]].rename(columns={"m": "_m_rebuilt"})
    merged = cache_df.merge(merge_cols, on=[id_col, "j"], how="left", validate="one_to_one")
    n_unmatched = int(merged["slice_text"].isna().sum())
    assert n_unmatched == 0, (
        f"[{id_col}] {n_unmatched} cache rows unmatched by ({id_col},j) rebuild")
    mism = merged["m"] != merged["_m_rebuilt"]
    n_mismatch = int(mism.sum())
    assert n_mismatch == 0, (
        f"[{id_col}] m mismatch on {n_mismatch} rows after ({id_col},j) alignment")
    merged = merged.drop(columns=["_m_rebuilt"])
    diag = {"cache_rows": n_cache, "rebuilt_rows": n_rebuilt,
            "unmatched": n_unmatched, "m_mismatches": n_mismatch}
    return merged, diag


# --------------------------------------------------------------------------
# Window markers from the raw window text
# --------------------------------------------------------------------------

def is_allcaps_token(tok: str) -> bool:
    """>=2 alphabetic chars, all uppercase -- excludes bare punctuation tokens
    and single-letter words (e.g. the pronoun 'I') from inflating the share."""
    letters = [c for c in tok if c.isalpha()]
    return len(letters) >= 2 and all(c.isupper() for c in letters)


def text_markers(text: str) -> dict:
    n = len(text)
    denom = n if n > 0 else 1
    toks = tokenize(text)
    n_tok = len(toks) if toks else 1
    return {
        "qmark_per100": 100.0 * text.count("?") / denom,
        "quote_per100": 100.0 * sum(text.count(ch) for ch in QUOTE_CHARS) / denom,
        "digit_per100": 100.0 * sum(ch.isdigit() for ch in text) / denom,
        "comma_per100": 100.0 * text.count(",") / denom,
        "allcaps_token_share": sum(is_allcaps_token(t) for t in toks) / n_tok,
        "token_count": float(len(toks)),
    }


# --------------------------------------------------------------------------
# Within-text linear detrend -> pooled-sd-standardized residuals
# --------------------------------------------------------------------------

def within_text_linear_residuals(sub: pd.DataFrame, id_col: str, cols: list) -> tuple:
    """`sub` MUST already be sorted by (id_col, j). Per-text OLS residual of each
    construct column on design [1, j] (vectorized via grouped sums / np.add.at),
    then standardized by the pooled residual sd computed over `sub`'s own
    population. Returns (resid_std, pooled_sd)."""
    codes, _ = pd.factorize(sub[id_col].to_numpy())
    n_groups = int(codes.max()) + 1
    j = sub["j"].to_numpy(dtype=float)
    cnt = np.bincount(codes, minlength=n_groups).astype(float)
    assert (cnt >= 2).all(), "a text has < 2 rows; linear detrend on [1,j] is undefined"

    sum_j = np.bincount(codes, weights=j, minlength=n_groups)
    mean_j = sum_j / cnt
    jc = j - mean_j[codes]
    denom = np.bincount(codes, weights=jc ** 2, minlength=n_groups)
    assert (denom > 0).all(), "a text has zero within-text variance in j (degenerate design)"

    Y = sub[cols].to_numpy(dtype=float)
    sum_Y = np.zeros((n_groups, len(cols)))
    np.add.at(sum_Y, codes, Y)
    mean_Y = sum_Y / cnt[:, None]
    Yc = Y - mean_Y[codes]

    num = np.zeros((n_groups, len(cols)))
    np.add.at(num, codes, jc[:, None] * Yc)
    slope = num / denom[:, None]
    resid = Yc - slope[codes] * jc[:, None]

    pooled_sd = resid.std(axis=0)
    pooled_sd_g = np.where(pooled_sd > 0, pooled_sd, 1.0)
    resid_std = resid / pooled_sd_g
    return resid_std, pooled_sd


# --------------------------------------------------------------------------
# Vectorized within-group shuffle (P7-style lexsort trick)
# --------------------------------------------------------------------------

def shuffle_within_group_1d(values: np.ndarray, group_keys: np.ndarray, rng) -> np.ndarray:
    """`values`/`group_keys` must be row-aligned to a frame already sorted so
    same-group rows are CONTIGUOUS (e.g. sorted by (id_col, j)). Returns a
    within-group-permuted copy of `values` (every group individually shuffled,
    all groups shuffled simultaneously via a single lexsort)."""
    keys = rng.random(len(values))
    perm = np.lexsort((keys, group_keys))
    out = np.empty_like(values)
    out[perm] = values
    return out


# --------------------------------------------------------------------------
# Correlation helpers
# --------------------------------------------------------------------------

def masked_pearson(x: np.ndarray, y: np.ndarray) -> tuple:
    mask = np.isfinite(x) & np.isfinite(y)
    n = int(mask.sum())
    if n < 3:
        return float("nan"), n
    xf, yf = x[mask], y[mask]
    if xf.std() == 0 or yf.std() == 0:
        return float("nan"), n
    r = float(np.corrcoef(xf, yf)[0, 1])
    return r, n


def demean_within_group(values: np.ndarray, group_keys: np.ndarray) -> np.ndarray:
    s = pd.Series(values)
    means = s.groupby(group_keys).transform("mean")  # skips NaN (pandas default)
    return (s - means).to_numpy()


def jf(x) -> float | None:
    """JSON-safe float: NaN/inf -> None."""
    if x is None:
        return None
    xf = float(x)
    return round(xf, 6) if np.isfinite(xf) else None


# --------------------------------------------------------------------------
# Section A: marker correlation table (+ within-text permutation on r_centered)
# --------------------------------------------------------------------------

def marker_correlation_table(a_series: np.ndarray, markers: dict, group_keys: np.ndarray,
                              rng: np.random.Generator, n_perm: int = N_PERM) -> list:
    a_centered = demean_within_group(a_series, group_keys)
    marker_centered = {k: demean_within_group(v, group_keys) for k, v in markers.items()}

    obs_centered, obs_raw = {}, {}
    for k, v in markers.items():
        obs_centered[k] = masked_pearson(a_centered, marker_centered[k])
        obs_raw[k] = masked_pearson(a_series, v)

    null_r = {k: np.empty(n_perm) for k in markers}
    for b in range(n_perm):
        a_shuf = shuffle_within_group_1d(a_centered, group_keys, rng)
        for k in markers:
            r_b, _ = masked_pearson(a_shuf, marker_centered[k])
            null_r[k][b] = r_b

    rows = []
    for k in markers:
        r_c, n_c = obs_centered[k]
        r_r, n_r = obs_raw[k]
        draws = null_r[k]
        valid = np.isfinite(draws)
        if valid.sum() > 0 and np.isfinite(r_c):
            p = float((np.abs(draws[valid]) >= abs(r_c)).mean())
        else:
            p = float("nan")
        rows.append({"marker": k, "r_centered": jf(r_c), "n_centered": n_c,
                     "r_raw": jf(r_r), "n_raw": n_r, "perm_p_centered": jf(p),
                     "perm_draws_valid": int(valid.sum())})
    rows.sort(key=lambda row: -(abs(row["r_centered"]) if row["r_centered"] is not None else -1.0))
    return rows


# --------------------------------------------------------------------------
# Section C: matched within-text column-shuffle variance-ratio null
# --------------------------------------------------------------------------

def variance_ratio_null(resid_std: np.ndarray, group_keys: np.ndarray, gust_unit: np.ndarray,
                         rng: np.random.Generator, n_draws: int = N_NULL_VAR) -> dict:
    obs_a = resid_std @ gust_unit
    obs_var = float(np.var(obs_a, ddof=0))
    n, p = resid_std.shape
    null_vars = np.empty(n_draws)
    for b in range(n_draws):
        shuffled = np.empty_like(resid_std)
        for c in range(p):
            shuffled[:, c] = shuffle_within_group_1d(resid_std[:, c], group_keys, rng)
        a_null = shuffled @ gust_unit
        null_vars[b] = np.var(a_null, ddof=0)
    null_mean = float(null_vars.mean())
    ratio = obs_var / null_mean if null_mean > 0 else float("nan")
    p_ge = float((null_vars >= obs_var).mean())
    return {"obs_var": jf(obs_var), "null_mean": jf(null_mean),
            "null_lo2p5": jf(np.percentile(null_vars, 2.5)),
            "null_hi97p5": jf(np.percentile(null_vars, 97.5)),
            "ratio": jf(ratio), "p_null_ge_obs": jf(p_ge),
            "n_windows": int(n), "n_draws": n_draws}


# --------------------------------------------------------------------------
# Section B: person susceptibility split-half
# --------------------------------------------------------------------------

def person_susceptibility(sub_m3: pd.DataFrame, a_w: np.ndarray, id_col: str) -> dict:
    df = sub_m3[["user_id", id_col]].copy()
    df["a"] = a_w
    df["abs_a"] = np.abs(a_w)
    per_text = (df.groupby(["user_id", id_col], sort=False)
                  .agg(mean_abs_a=("abs_a", "mean"), mean_signed_a=("a", "mean"))
                  .reset_index())
    # Order = ascending id_col (the pipeline's own sequential assignment order,
    # i.e. each user's texts in their original tier_u_comments.parquet row order).
    # No timestamp is loaded anywhere in this label/metadata-minimal pipeline, so
    # this is a documented ASSUMPTION, not a verified chronological order -- see
    # the ambiguity note in the final report.
    per_text = per_text.sort_values(["user_id", id_col]).reset_index(drop=True)
    per_text["rank_in_user"] = per_text.groupby("user_id").cumcount()
    counts = per_text.groupby("user_id").size()
    qualifying_users = counts.index[counts >= 2]
    pt = per_text[per_text["user_id"].isin(qualifying_users)].copy()

    even = (pt[pt["rank_in_user"] % 2 == 0].groupby("user_id")
              .agg(abs_even=("mean_abs_a", "mean"), sign_even=("mean_signed_a", "mean")))
    odd = (pt[pt["rank_in_user"] % 2 == 1].groupby("user_id")
             .agg(abs_odd=("mean_abs_a", "mean"), sign_odd=("mean_signed_a", "mean")))
    joined = even.join(odd, how="inner")
    n_users = len(joined)
    assert n_users == len(qualifying_users), (
        f"split-half join lost users: {n_users} vs {len(qualifying_users)} qualifying")

    r_susc, _ = masked_pearson(joined["abs_even"].to_numpy(), joined["abs_odd"].to_numpy())
    r_dir, _ = masked_pearson(joined["sign_even"].to_numpy(), joined["sign_odd"].to_numpy())

    user_level_means = pt.groupby("user_id")["mean_abs_a"].mean().to_numpy()
    var_user_means = float(np.var(user_level_means, ddof=0))
    var_all = float(np.var(pt["mean_abs_a"].to_numpy(), ddof=0))
    icc_share = var_user_means / var_all if var_all > 0 else float("nan")

    return {"n_users": int(n_users), "r_susceptibility": jf(r_susc), "r_direction": jf(r_dir),
            "icc_share_abs_a": jf(icc_share), "n_texts_pooled": int(len(pt)),
            "var_user_means": jf(var_user_means), "var_all": jf(var_all)}


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # ---------------- load caches ----------------
    pandora_scored = pd.read_parquet(PANDORA_CACHE)
    essays_scored = pd.read_parquet(ESSAYS_CACHE)

    cols_p = w2a.get_construct_cols(pandora_scored)
    cols_e = w2a.get_construct_cols(essays_scored)
    assert cols_p == cols_e, "construct column lists differ between PANDORA and Essays caches"
    cols = cols_p
    assert len(cols) == 19, f"expected 19 construct columns, got {len(cols)}"
    print(f"loaded caches: PANDORA {len(pandora_scored)} windows / "
          f"{pandora_scored['cid'].nunique()} texts; Essays {len(essays_scored)} windows / "
          f"{essays_scored['eid'].nunique()} texts; {len(cols)} constructs")

    # ---------------- rebuild + align window text ----------------
    frame_p_text = build_windows()
    pandora_full, diag_p = align_with_text(pandora_scored, frame_p_text, "cid")
    print(f"[align] PANDORA (cid,j): cache={diag_p['cache_rows']} "
          f"rebuilt={diag_p['rebuilt_rows']} unmatched={diag_p['unmatched']} "
          f"m_mismatches={diag_p['m_mismatches']}")

    frame_e_text = build_essays_windows_with_text()
    essays_full, diag_e = align_with_text(essays_scored, frame_e_text, "eid")
    print(f"[align] Essays (eid,j): cache={diag_e['cache_rows']} "
          f"rebuilt={diag_e['rebuilt_rows']} unmatched={diag_e['unmatched']} "
          f"m_mismatches={diag_e['m_mismatches']} "
          f"(reconstructed/verified per governance; not used numerically beyond "
          f"this point since Sections A-C need Essays markers nowhere)")

    # ---------------- axis: gust1_P (W2a/W6 recipe, reused verbatim) ----------------
    gust1_p_raw, gust1_p_eigval, gust1_p_n = w2a.compute_gust1_p(pandora_scored, cols)
    gust1_p_unit = gust1_p_raw / np.linalg.norm(gust1_p_raw)

    order = np.argsort(-np.abs(gust1_p_unit))
    sorted_loadings = [{"construct": cols[i], "loading": jf(gust1_p_unit[i])} for i in order]
    top2_names = {cols[i] for i in order[:2]}
    novelty_idx = cols.index("novelty_play_v2")
    novelty_loading = float(gust1_p_unit[novelty_idx])

    print(f"\n[axis] gust1_P (unit, from {gust1_p_n} PANDORA m==3 texts, "
          f"top eigenvalue={gust1_p_eigval:.4f}):")
    print("  " + ", ".join(f"{r['construct']}:{r['loading']:+.4f}" for r in sorted_loadings))
    print(f"  top-2 |loading| constructs: {sorted(top2_names)} "
          f"(drift guard expects {sorted(DRIFT_GUARD)})")
    assert top2_names == DRIFT_GUARD, (
        f"DRIFT GUARD FAILED: top-2 |loading| constructs are {sorted(top2_names)}, "
        f"expected exactly {sorted(DRIFT_GUARD)}")
    print("  drift guard: PASS")
    print(f"  novelty_play_v2 loading on gust1_P: {novelty_loading:+.4f} "
          f"(novelty is one of the 19 axis-defining constructs -> its correlation "
          f"with activation is partly definitional/endogenous; the 6 raw-text "
          f"markers and position_t are fully exogenous to the axis)")

    # ==================================================================
    # A. ACTIVATION ANATOMY (PANDORA, m>=3, all kept windows)
    # ==================================================================
    sub = pandora_full[pandora_full["m"] >= 3].sort_values(["cid", "j"]).reset_index(drop=True)
    n_windows_a = len(sub)
    n_texts_a = sub["cid"].nunique()
    print(f"\n=== A. ACTIVATION ANATOMY (PANDORA m>=3): "
          f"{n_windows_a} windows, {n_texts_a} texts ===")
    print("  m distribution (per text):",
          sub.groupby("cid")["m"].first().value_counts().sort_index().to_dict())

    resid_std, pooled_resid_sd = within_text_linear_residuals(sub, "cid", cols)
    a_w = resid_std @ gust1_p_unit
    group_keys_a = sub["cid"].to_numpy()

    tm_rows = [text_markers(t) for t in sub["slice_text"]]
    tm_df = pd.DataFrame(tm_rows)
    novelty_jump = sub.groupby("cid")["novelty_play_v2"].diff().abs().to_numpy()
    markers = {
        "qmark_per100": tm_df["qmark_per100"].to_numpy(),
        "quote_per100": tm_df["quote_per100"].to_numpy(),
        "digit_per100": tm_df["digit_per100"].to_numpy(),
        "comma_per100": tm_df["comma_per100"].to_numpy(),
        "allcaps_token_share": tm_df["allcaps_token_share"].to_numpy(),
        "token_count": tm_df["token_count"].to_numpy(),
        "novelty_level": sub["novelty_play_v2"].to_numpy(dtype=float),
        "novelty_jump": novelty_jump,
        "position_t": sub["t"].to_numpy(dtype=float),
    }

    table_abs = marker_correlation_table(np.abs(a_w), markers, group_keys_a, rng)
    table_signed = marker_correlation_table(a_w, markers, group_keys_a, rng)

    print("\n  [A |a_w| marker table] sorted by |r_centered| desc "
          "(marker, r_centered, r_raw, perm_p_centered, n_centered):")
    for r in table_abs:
        print(f"    {r['marker']:22s} r_c={r['r_centered']!s:>8} r_raw={r['r_raw']!s:>8} "
              f"perm_p={r['perm_p_centered']!s:>7} n={r['n_centered']}")
    print("\n  [A signed a_w marker table] sorted by |r_centered| desc:")
    for r in table_signed:
        print(f"    {r['marker']:22s} r_c={r['r_centered']!s:>8} r_raw={r['r_raw']!s:>8} "
              f"perm_p={r['perm_p_centered']!s:>7} n={r['n_centered']}")

    # ==================================================================
    # B. PERSON SUSCEPTIBILITY (PANDORA)
    # ==================================================================
    b_res = person_susceptibility(sub, a_w, "cid")
    print(f"\n=== B. PERSON SUSCEPTIBILITY (PANDORA, users with >=2 m>=3 texts) ===")
    print(f"  n_users={b_res['n_users']} n_texts_pooled={b_res['n_texts_pooled']}")
    print(f"  r_susceptibility (|a| split-half) = {b_res['r_susceptibility']}")
    print(f"  r_direction (signed a split-half)  = {b_res['r_direction']}")
    print(f"  ICC-style share var(user means)/var(all) for |a| = {b_res['icc_share_abs_a']}")

    # ==================================================================
    # C. ESSAYS CONTRAST (matched within-text column-shuffle variance ratio)
    # ==================================================================
    sub_e = essays_full[essays_full["m"] >= 3].sort_values(["eid", "j"]).reset_index(drop=True)
    n_windows_e = len(sub_e)
    n_texts_e = sub_e["eid"].nunique()
    resid_std_e, pooled_resid_sd_e = within_text_linear_residuals(sub_e, "eid", cols)
    group_keys_e = sub_e["eid"].to_numpy()

    print(f"\n=== C. ESSAYS CONTRAST: PANDORA (m>=3, {n_windows_a} win) "
          f"vs Essays (m>=3, {n_windows_e} win / {n_texts_e} texts) "
          f"-- matched within-text column-shuffle null ({N_NULL_VAR} draws) ===")
    ratio_p = variance_ratio_null(resid_std, group_keys_a, gust1_p_unit, rng)
    ratio_e = variance_ratio_null(resid_std_e, group_keys_e, gust1_p_unit, rng)
    print(f"  PANDORA: obs_var={ratio_p['obs_var']} null_mean={ratio_p['null_mean']} "
          f"[{ratio_p['null_lo2p5']}, {ratio_p['null_hi97p5']}] "
          f"ratio={ratio_p['ratio']} p(null>=obs)={ratio_p['p_null_ge_obs']}")
    print(f"  Essays:  obs_var={ratio_e['obs_var']} null_mean={ratio_e['null_mean']} "
          f"[{ratio_e['null_lo2p5']}, {ratio_e['null_hi97p5']}] "
          f"ratio={ratio_e['ratio']} p(null>=obs)={ratio_e['p_null_ge_obs']}")
    print(f"  (expectation per F15 registration: PANDORA ratio >> 1, Essays ratio ~ 1)")

    # ==================================================================
    # Write outputs
    # ==================================================================
    capped_corpus_note = (
        "Both caches derive from the CURRENT CAPPED Tier-U / Essays extraction "
        "(docs/SUICA_THEORY_FORMAL_NOTES_V3.md F14/N1): comment bodies are capped, "
        "which limits observed m (mostly m=3 in the PANDORA m>=3 slice used here). "
        "An uncapped re-extraction (tier_u_comments_uncapped_v1.parquet) is "
        "registered to follow N1; this is the CAPPED-corpus version of W10.")

    order_assumption_note = (
        "Section B 'text order' for the odd/even split-half is taken as ascending "
        "cid -- the pipeline's own sequential assignment order (each user's texts "
        "in their original tier_u_comments.parquet row order). No timestamp column "
        "is loaded anywhere in this script (label/metadata-minimal, text-only "
        "governance), so this order is a documented ASSUMPTION, not a verified "
        "chronological order.")

    sign_convention_note = (
        "gust1_P's sign is whatever np.linalg.eigh returns for this data (arbitrary "
        "but deterministic/reproducible); 'signed a_w' / 'direction' readings "
        "inherit that fixed sign convention, consistent with prior W2a/W6 usage of "
        "the same axis.")

    permutation_note = (
        "perm_p_centered tests r_centered specifically: a within-text shuffle of "
        "a_w is the natural exchangeability null for the within-text-demeaned "
        "correlation. It is NOT a valid null for r_raw, whose between-text "
        "covariance component survives a within-text-only shuffle; r_raw is "
        "reported for transparency/comparison only, without a matching p-value."
    )

    essays_text_note = (
        "Essays window text was reconstructed and row-for-row aligned to the "
        "cache per the DATA governance spec (see [align] Essays log line), but is "
        "not used numerically in Sections A-C: Section A's marker analysis is "
        "PANDORA-only per the registration, and Section C only needs Essays' "
        "numeric residual/activation, not its markers."
    )

    result = {
        "meta": {
            "registered_ref": "F15, registered commit 52421ea, "
                               "docs/SUICA_THEORY_FORMAL_NOTES_V3.md",
            "seed": SEED, "n_perm_marker": N_PERM, "n_null_variance": N_NULL_VAR,
            "construct_cols": cols,
            "capped_corpus_note": capped_corpus_note,
            "text_alignment": {"pandora": diag_p, "essays": diag_e},
            "gust1_P": {
                "vector": [jf(x) for x in gust1_p_unit],
                "top_eigenvalue": jf(gust1_p_eigval),
                "n_source_texts": int(gust1_p_n),
                "sorted_loadings": sorted_loadings,
                "top2_constructs": sorted(top2_names),
                "drift_guard_expected": sorted(DRIFT_GUARD),
                "drift_guard_pass": True,
                "novelty_play_v2_loading": jf(novelty_loading),
            },
        },
        "A_activation_anatomy": {
            "n_windows": n_windows_a, "n_texts": n_texts_a,
            "m_distribution": {int(k): int(v) for k, v in
                               sub.groupby("cid")["m"].first().value_counts().items()},
            "marker_table_abs_a": table_abs,
            "marker_table_signed_a": table_signed,
            "permutation_note": permutation_note,
        },
        "B_person_susceptibility": b_res | {"order_assumption_note": order_assumption_note},
        "C_essays_contrast": {
            "pandora": ratio_p, "essays": ratio_e,
            "expectation": "PANDORA ratio >> 1 (shared-rhythm coordination present); "
                           "Essays ratio ~ 1 (no invisible factor to coordinate)",
        },
        "notes_ambiguities": [
            capped_corpus_note, order_assumption_note, sign_convention_note,
            permutation_note, essays_text_note,
            f"ALL-CAPS token share requires >=2 alphabetic chars per token (excludes "
            f"single-letter words such as the pronoun 'I' from inflating the share); "
            f"this is a reasonable but not spec-dictated convention.",
            "token_count is a STRUCTURALLY DEGENERATE marker in this design: windows "
            "are built as exactly WIN=128-token slices (run_suica_tgeo_p7_flow_curve_v1 "
            "/ run_suica_v6_e2_essays_motion_v1), and re-tokenizing the joined window "
            "text deterministically returns exactly 128 tokens every time (verified), "
            "so token_count has zero variance across all windows and its correlation "
            "with a_w is undefined (reported as null/None rather than a misleading 0).",
        ],
    }
    OUT_JSON.write_text(json.dumps(result, indent=2))

    md = ["# V6-W10 -- Anatomy of the invisible (motion-only) gust factor",
          "", "F15, registered commit 52421ea, docs/SUICA_THEORY_FORMAL_NOTES_V3.md. "
              "Label-free (Tier-U + Essays TEXT only).", "",
          f"CAPPED-CORPUS RUN: {capped_corpus_note}", "",
          "## Axis: gust1_P", "",
          f"Top eigenvalue {gust1_p_eigval:.4f} from {gust1_p_n} PANDORA m==3 texts. "
          f"Drift guard (top-2 |loading| in {{wcl_02, wcl_11}}): PASS "
          f"({sorted(top2_names)}). novelty_play_v2 loading: {novelty_loading:+.4f}.",
          "", "| construct | loading |", "|---|---|"]
    md += [f"| {r['construct']} | {r['loading']:+.4f} |" for r in sorted_loadings]

    md += ["", "## A. Activation anatomy (PANDORA, m>=3)", "",
           f"{n_windows_a} windows, {n_texts_a} texts.", "",
           "### |a_w| (magnitude) marker table", "",
           "| marker | r_centered | r_raw | perm_p (centered) | n |",
           "|---|---|---|---|---|"]
    for r in table_abs:
        md.append(f"| {r['marker']} | {r['r_centered']} | {r['r_raw']} | "
                  f"{r['perm_p_centered']} | {r['n_centered']} |")
    md += ["", "### signed a_w (direction) marker table", "",
           "| marker | r_centered | r_raw | perm_p (centered) | n |",
           "|---|---|---|---|---|"]
    for r in table_signed:
        md.append(f"| {r['marker']} | {r['r_centered']} | {r['r_raw']} | "
                  f"{r['perm_p_centered']} | {r['n_centered']} |")

    md += ["", "## B. Person susceptibility (PANDORA)", "",
           f"n_users={b_res['n_users']} (>=2 qualifying m>=3 texts), "
           f"n_texts_pooled={b_res['n_texts_pooled']}", "",
           f"- r_susceptibility (|a| split-half): {b_res['r_susceptibility']}",
           f"- r_direction (signed a split-half): {b_res['r_direction']}",
           f"- ICC-style share var(user means)/var(all) for |a|: {b_res['icc_share_abs_a']}",
           "", f"Order assumption: {order_assumption_note}"]

    md += ["", "## C. Essays contrast (matched within-text column-shuffle null, "
               f"{N_NULL_VAR} draws)", "",
           "| corpus | n_windows | obs_var | null_mean | null [2.5%,97.5%] | ratio | p(null>=obs) |",
           "|---|---|---|---|---|---|---|",
           f"| PANDORA | {ratio_p['n_windows']} | {ratio_p['obs_var']} | "
           f"{ratio_p['null_mean']} | [{ratio_p['null_lo2p5']}, {ratio_p['null_hi97p5']}] | "
           f"{ratio_p['ratio']} | {ratio_p['p_null_ge_obs']} |",
           f"| Essays | {ratio_e['n_windows']} | {ratio_e['obs_var']} | "
           f"{ratio_e['null_mean']} | [{ratio_e['null_lo2p5']}, {ratio_e['null_hi97p5']}] | "
           f"{ratio_e['ratio']} | {ratio_e['p_null_ge_obs']} |",
           "", "Expectation: PANDORA ratio >> 1, Essays ratio ~ 1.", ""]

    md += ["## Notes / ambiguities", ""]
    md += [f"- {n}" for n in result["notes_ambiguities"]]
    OUT_MD.write_text("\n".join(md) + "\n")

    print(f"\nwritten: {OUT_JSON}")
    print(f"written: {OUT_MD}")


if __name__ == "__main__":
    main()
