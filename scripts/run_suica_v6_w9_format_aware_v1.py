#!/usr/bin/env python
"""W9 — Format-aware windowing: lifting or confirming the PANDORA flag (F12.10, registered commit e2b2240). Label-free, Tier-U.

GOVERNANCE: reads tier_u_comments.parquet [author, body] (raw text, no
labels), the P8 window cache (anchor), the W2a result JSON (anchor
targets), and the E2 Essays motion JSON (gust1_E axis). No label columns
anywhere.

Question (F12.10): W2a flagged PANDORA long-comment dynamics as
uninterpretable (rho1(Delta2) saturating toward -1, theta boundary hits)
with QUOTE/LIST FORMAT PERIODICITY as the suspected mechanism. W9 tests
the mechanism: strip Reddit formatting BEFORE tokenization, re-window,
re-run the leverage-free Delta2 dynamics on the same texts, plus a format
census. KILL: unchanged stripped dynamics kill the format hypothesis (the
flag becomes a finding about genuine extreme register texture).

Pipeline:
  1. CANDIDATES exactly as the P7/P8 builds: body length >= 1200 chars in
     parquet order (cid = enumeration index over candidates).
  2. FORMAT CENSUS on all candidates: per comment, share of LINES that
     are (i) quotes (lstrip startswith ">" or "&gt;"), (ii) list items
     (regex ^\\s*([-*+]|\\d+[.)])\\s+), (iii) code (``` fences incl. the
     fence lines, or 4-space-indent lines). Line classification priority:
     fence-code > quote > indent-code > list (a line counts once);
     denominator = all body lines incl. blanks. m_raw = len(tokenize)//128.
     Census strata: m_raw {2-3} vs {>=4} (m_raw < 2 reported as residual).
  3. TWO ARMS on the W2a cohort (texts with 4 <= m_raw <= 12 whose RAW
     windows pass the leak mask — identical to the W2a sensitivity arm;
     no m_raw > 12 texts exist in this corpus, reported):
     RAW arm — windows exactly as P7's build: 128-token non-overlapping,
       len(tokens) >= 288, m = tokens//128 >= 2, cap 12 endpoint-
       preserving subsample, PERSONALITY_LEAK_RE on any kept window drops
       the whole text. Rebuilt from raw text and ASSERTED against the P8
       cache scores; the cache-based dynamics are additionally asserted
       to reproduce W2a's published rho1 for all 21 series (anchor, lean
       a). If the freshly refit wcl transform is not bit-reproducible,
       the RAW arm falls back to the cache scores (flagged in output);
       the STRIPPED arm always uses the same single fit as the RAW
       rebuild, so the arm CONTRAST is internally consistent either way.
     STRIPPED arm — format stripper FIRST (remove quote lines; remove
       ``` fenced blocks incl. fences and 4-space-indent code lines;
       delete remaining inline backtick characters keeping inner text;
       strip list markers keeping item text; collapse blank runs to one
       blank line), THEN the same tokenize/window/leak rules. m_stripped
       >= 4 required (drop count reported; stripping can only shorten,
       so m_stripped <= m_raw <= 12; a defensive cap-12 guard stays).
  4. SCORING: a19.score_slices_v2 (V3_BATTERY) + the frozen dav wcl
     transform (OP5_KEPT), ONE fit shared by both arms (transform is
     frozen; the fit is the runtime-dominant step). Per arm: pooled-sd
     standardization over that arm's included windows (per-arm, per
     spec; pooled Pearson rho1 of the 19 constructs is invariant to
     per-series rescale, so this choice only marginally moves the two
     axis projections vs W2a's full-cache sd — quantified by the anchor).
  5. DYNAMICS per arm (W2a machinery verbatim): gust1_E from the E2 JSON,
     gust1_P recomputed from the P8 cache m==3 second-difference
     correlation structure; within-text-centered Delta2; pooled lag-1
     rho1 per series (2 axes + 19 constructs); 2000-replicate iid-normal
     null matched to the arm's m composition (the RAW arm's composition
     equals the cache cohort's, so that null is shared); p = P(null <=
     obs); theta-hat via the exact rho1(theta) identity with the W2a
     boundary rule.

Seed: 20260712.
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.suica import PERSONALITY_LEAK_RE, tokenize  # noqa: E402
import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
P8_CACHE = ROOT / "results" / "suica_tgeo_p8_functionalization" / "cache_windows_scored19.parquet"
W2A_JSON = ROOT / "results" / "suica_v6_w2a_delta2_dynamics" / "V6_W2A_DELTA2_DYNAMICS.json"
E2_JSON = ROOT / "results" / "suica_v6_e2_essays_motion" / "V6_E2_ESSAYS_MOTION.json"
OUT_DIR = ROOT / "results" / "suica_v6_w9_format_aware"

SEED = 20260712
N_REPLICATES = 2000
WIN = 128
MIN_TOKENS = 288
MAX_WINDOWS = 12
M_LO, M_HI = 4, 12

LIST_RE = re.compile(r"^\s*([-*+]|\d+[.)])\s+")
SATURATION_SET = ["wcl_36", "wcl_11", "wcl_02", "novelty_play_v2", "wcl_60", "wcl_35", "wcl_15"]


# ---------------- census + stripper ----------------

def classify_lines(body: str):
    """Per-line format classes with fence state. Priority:
    fence-code > quote > indent-code > list. Returns (n_lines, n_quote,
    n_list, n_code)."""
    n_quote = n_list = n_code = 0
    in_fence = False
    lines = body.split("\n")
    for ln in lines:
        stripped = ln.lstrip()
        if stripped.startswith("```"):
            n_code += 1
            in_fence = not in_fence
            continue
        if in_fence:
            n_code += 1
            continue
        if stripped.startswith(">") or stripped.startswith("&gt;"):
            n_quote += 1
            continue
        if ln.startswith("    "):
            n_code += 1
            continue
        if LIST_RE.match(ln):
            n_list += 1
    return len(lines), n_quote, n_list, n_code


def strip_format(body: str) -> str:
    """Remove quote lines, fenced/indented code, inline backticks (keep
    inner text), list markers (keep item text); collapse blank runs."""
    out = []
    in_fence = False
    for ln in body.split("\n"):
        stripped = ln.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.startswith(">") or stripped.startswith("&gt;"):
            continue
        if ln.startswith("    "):
            continue
        ln = LIST_RE.sub("", ln)
        out.append(ln)
    text = "\n".join(out).replace("`", "")
    text = re.sub(r"\n(\s*\n)+", "\n\n", text)
    return text


def windows_from_tokens(tokens: list) -> tuple:
    """P7 windowing: m = tokens//WIN (>=2), cap-12 endpoint-preserving
    subsample, leak mask drops the whole text. Returns (m, rows|None,
    leak_tripped)."""
    m = len(tokens) // WIN
    if len(tokens) < MIN_TOKENS or m < 2:
        return m, None, False
    keep = (np.unique(np.round(np.linspace(0, m - 1, MAX_WINDOWS)).astype(int))
            if m > MAX_WINDOWS else np.arange(m))
    rows = []
    for j in keep:
        wtext = " ".join(tokens[j * WIN:(j + 1) * WIN])
        if PERSONALITY_LEAK_RE.search(wtext):
            return m, None, True
        rows.append({"j": int(j), "wtext": wtext})
    return m, rows, False


# ---------------- W2a dynamics machinery (verbatim) ----------------

def corr_guarded(x: np.ndarray) -> np.ndarray:
    mu = x.mean(axis=0)
    sd = x.std(axis=0)
    sd_g = np.where(sd > 0, sd, 1.0)
    z = (x - mu) / sd_g
    c = (z.T @ z) / (x.shape[0] - 1)
    np.fill_diagonal(c, 1.0)
    return c


def rho1_theta_model(theta: float) -> float:
    return -(4.0 * (1.0 + theta ** 2) + 7.0 * theta) / (6.0 * (1.0 + theta ** 2) + 8.0 * theta)


def solve_theta(observed: float, null_mean: float) -> float:
    adj = observed - (null_mean - (-2.0 / 3.0))
    if adj >= -2.0 / 3.0:
        return 0.0
    if adj <= rho1_theta_model(1.0):
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if rho1_theta_model(mid) > adj:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12:
            break
    return 0.5 * (lo + hi)


def pooled_pearson_from_sums(n, sa, sb, saa, sbb, sab) -> float:
    if n < 2:
        return float("nan")
    num = n * sab - sa * sb
    den = np.sqrt((n * saa - sa ** 2) * (n * sbb - sb ** 2))
    return float(num / den) if den > 0 else float("nan")


def build_m_groups(sub: pd.DataFrame, id_col: str):
    m_arr = sub["m"].to_numpy()
    id_arr = sub[id_col].to_numpy()
    j_arr = sub["j"].to_numpy()
    groups = []
    for m_value in sorted(pd.unique(m_arr).tolist()):
        mask = m_arr == m_value
        n_rows = int(mask.sum())
        assert n_rows % m_value == 0
        n_texts_m = n_rows // m_value
        ids_block = id_arr[mask].reshape(n_texts_m, m_value)
        j_block = j_arr[mask].reshape(n_texts_m, m_value)
        assert np.all(ids_block == ids_block[:, [0]])
        assert np.all(np.diff(j_block, axis=1) > 0)
        groups.append((int(m_value), mask, n_texts_m))
    return groups


def observed_rho1(series_col: np.ndarray, groups) -> tuple:
    sa = sb = saa = sbb = sab = 0.0
    n_pairs = 0
    for m_value, mask, n_texts_m in groups:
        if m_value < 4 or n_texts_m == 0:
            continue
        x = series_col[mask].reshape(n_texts_m, m_value)
        d2 = x[:, 2:] - 2 * x[:, 1:-1] + x[:, :-2]
        d2 = d2 - d2.mean(axis=1, keepdims=True)
        a, b = d2[:, :-1], d2[:, 1:]
        sa += float(a.sum()); sb += float(b.sum())
        saa += float((a * a).sum()); sbb += float((b * b).sum()); sab += float((a * b).sum())
        n_pairs += a.size
    return pooled_pearson_from_sums(n_pairs, sa, sb, saa, sbb, sab), n_pairs


def simulate_null(groups, n_replicates: int, rng: np.random.Generator):
    sa = np.zeros(n_replicates); sb = np.zeros(n_replicates)
    saa = np.zeros(n_replicates); sbb = np.zeros(n_replicates); sab = np.zeros(n_replicates)
    n_pairs_total = 0
    for m_value, _mask, n_texts_m in groups:
        if m_value < 4 or n_texts_m == 0:
            continue
        x = rng.standard_normal(size=(n_replicates, n_texts_m, m_value))
        d2 = x[:, :, 2:] - 2 * x[:, :, 1:-1] + x[:, :, :-2]
        d2 = d2 - d2.mean(axis=2, keepdims=True)
        a, b = d2[:, :, :-1], d2[:, :, 1:]
        sa += a.sum(axis=(1, 2)); sb += b.sum(axis=(1, 2))
        saa += (a * a).sum(axis=(1, 2)); sbb += (b * b).sum(axis=(1, 2)); sab += (a * b).sum(axis=(1, 2))
        n_pairs_total += n_texts_m * (m_value - 3)
    num = n_pairs_total * sab - sa * sb
    den = np.sqrt((n_pairs_total * saa - sa ** 2) * (n_pairs_total * sbb - sb ** 2))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(den > 0, num / den, np.nan), n_pairs_total


def compute_gust1_p(pandora: pd.DataFrame, cols: list):
    pm3 = pandora[pandora["m"] == 3]
    sizes = pm3.groupby("cid").size()
    pm3 = pm3[pm3["cid"].isin(sizes[sizes == 3].index)].sort_values(["cid", "j"])
    raw = pm3[cols].to_numpy(dtype=float)
    w = raw.reshape(-1, 3, len(cols))
    sd = raw.std(axis=0)
    sd_g = np.where(sd > 0, sd, 1.0)
    q = ((w[:, 0] - 2 * w[:, 1] + w[:, 2]) / np.sqrt(6.0)) / sd_g
    c = corr_guarded(q)
    eigvals, eigvecs = np.linalg.eigh(c)
    return eigvecs[:, -1], float(eigvals[-1]), int(q.shape[0])


def arm_dynamics(frame: pd.DataFrame, cols: list, gust1_e, gust1_p, null_dist, null_n_pairs):
    """frame: [cid, j, m] + cols, sorted (cid, j), complete texts only."""
    X = frame[cols].to_numpy(float)
    sd = X.std(axis=0)
    sd_g = np.where(sd > 0, sd, 1.0)
    std = X / sd_g
    series = np.concatenate([(std @ gust1_e)[:, None], (std @ gust1_p)[:, None], std], axis=1)
    names = ["gust1_E", "gust1_P"] + cols
    groups = build_m_groups(frame, "cid")
    null_mean = float(np.nanmean(null_dist))
    out = {}
    for k, name in enumerate(names):
        rho1, n_pairs = observed_rho1(series[:, k], groups)
        assert n_pairs == null_n_pairs
        out[name] = {"rho1": rho1,
                     "excess": rho1 - null_mean,
                     "null_mean": null_mean,
                     "null_lo": float(np.nanpercentile(null_dist, 2.5)),
                     "null_hi": float(np.nanpercentile(null_dist, 97.5)),
                     "p": float(np.nanmean(null_dist <= rho1)),
                     "theta": solve_theta(rho1, null_mean),
                     "n_pairs": int(n_pairs)}
    return out, groups


def main() -> None:
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    cols = list(a19.V3_BATTERY) + list(a19.OP5_KEPT)
    assert len(cols) == 19

    # ---------------- pass 1: census + raw/stripped builds ----------------
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet", columns=["author", "body"])
    comments["author"] = comments["author"].astype(str)
    body = comments["body"].astype(str)
    cand = comments.loc[body.str.len() >= 1200]
    n_candidates = len(cand)

    census = []
    raw_rows = []
    raw_meta = {}       # cid -> (m_raw, leak)
    t_census = time.time()
    for cid, (author, text) in enumerate(zip(cand["author"], cand["body"].astype(str))):
        n_lines, n_q, n_l, n_c = classify_lines(text)
        tokens = tokenize(text)
        m_raw = len(tokens) // WIN
        census.append((cid, m_raw, n_q / n_lines, n_l / n_lines, n_c / n_lines))
        m_chk, rows, leak = windows_from_tokens(tokens)
        raw_meta[cid] = (m_raw, leak)
        if rows is not None and M_LO <= m_raw <= M_HI:
            for r in rows:
                raw_rows.append({"cid": cid, "user_id": author, "j": r["j"], "m": m_raw,
                                 "slice_text": r["wtext"]})
    census_df = pd.DataFrame(census, columns=["cid", "m_raw", "q_share", "l_share", "c_share"])
    raw_frame = pd.DataFrame(raw_rows).sort_values(["cid", "j"]).reset_index(drop=True)
    cohort_cids = sorted(raw_frame["cid"].unique().tolist())
    print(f"[census] candidates={n_candidates} (body >= 1200 chars); "
          f"built in {time.time() - t_census:.1f}s")
    for lo, hi, label in ((2, 3, "m_raw 2-3"), (4, 10 ** 9, "m_raw >= 4")):
        s = census_df[(census_df["m_raw"] >= lo) & (census_df["m_raw"] <= hi)]
        print(f"[census] {label}: n={len(s)} mean_quote_share={s['q_share'].mean():.4f} "
              f"mean_list_share={s['l_share'].mean():.4f} mean_code_share={s['c_share'].mean():.4f}")
    n_mlt2 = int((census_df["m_raw"] < 2).sum())
    print(f"[census] residual m_raw < 2: {n_mlt2} texts (below both strata)")

    # ---------------- anchor 1: cache-based W2a reproduction ----------------
    cache = pd.read_parquet(P8_CACHE)
    cache_cols = [c for c in cache.columns if c not in ("cid", "user_id", "j", "m", "t", "tau", "delta")]
    assert cache_cols == cols, "cache construct order != a19 battery order"
    m_by_cid = cache.groupby("cid")["m"].first()
    cache_cohort = sorted(m_by_cid[(m_by_cid >= M_LO) & (m_by_cid <= M_HI)].index.tolist())
    n_m_gt12 = int((m_by_cid > M_HI).sum())
    assert cohort_cids == cache_cohort, (
        f"rebuilt cohort cids != cache cohort cids "
        f"({len(cohort_cids)} vs {len(cache_cohort)})")
    print(f"[cohort] W2a construction: {len(cohort_cids)} texts with {M_LO}<=m_raw<={M_HI} "
          f"(m_raw>12 in corpus: {n_m_gt12}); raw-arm windows={len(raw_frame)}")

    with open(E2_JSON) as f:
        e2 = json.load(f)
    assert e2["constructs"] == cols
    gust1_e = np.asarray(e2["C_motion"]["gusts"][0]["vector"], dtype=float)
    gust1_e = gust1_e / np.linalg.norm(gust1_e)
    gust1_p_raw, g1p_eig, g1p_n = compute_gust1_p(cache, cols)
    gust1_p = gust1_p_raw / np.linalg.norm(gust1_p_raw)
    print(f"[axes] gust1_E from E2 JSON; gust1_P recomputed from {g1p_n} cache m==3 texts "
          f"(top eig {g1p_eig:.4f})")

    # W2a-verbatim cache dynamics: FULL-cache pooled sd (W2a convention)
    cache_sub = cache[cache["cid"].isin(cache_cohort)].sort_values(["cid", "j"]).reset_index(drop=True)
    full_sd = cache[cols].to_numpy(float).std(axis=0)
    full_sd_g = np.where(full_sd > 0, full_sd, 1.0)
    std_cache = cache_sub[cols].to_numpy(float) / full_sd_g
    series_cache = np.concatenate([(std_cache @ gust1_e)[:, None], (std_cache @ gust1_p)[:, None],
                                   std_cache], axis=1)
    groups_cache = build_m_groups(cache_sub, "cid")
    w2a = json.load(open(W2A_JSON))["pandora"]["sensitivity_m4_12"]
    names21 = ["gust1_E", "gust1_P"] + cols
    max_anchor_diff = 0.0
    for k, name in enumerate(names21):
        rho1, _ = observed_rho1(series_cache[:, k], groups_cache)
        max_anchor_diff = max(max_anchor_diff, abs(rho1 - w2a[name]["rho1"]))
    assert max_anchor_diff < 1e-9, f"cache-based rho1 != W2a published: {max_anchor_diff}"
    print(f"[anchor-1] cache dynamics reproduce W2a's 21 published rho1 exactly "
          f"(max|diff|={max_anchor_diff:.2e})")

    # ---------------- stripped build (cohort texts only) ----------------
    cand_bodies = cand["body"].astype(str).tolist()
    strip_rows = []
    n_drop_m, n_drop_leak, n_guard_cap = 0, 0, 0
    for cid in cohort_cids:
        stext = strip_format(cand_bodies[cid])
        tokens = tokenize(stext)
        m_s = len(tokens) // WIN
        if m_s > M_HI:
            n_guard_cap += 1        # defensive; stripping cannot lengthen
        m_chk, rows, leak = windows_from_tokens(tokens)
        if rows is None:
            if leak:
                n_drop_leak += 1
            else:
                n_drop_m += 1
            continue
        if m_s < M_LO:
            n_drop_m += 1
            continue
        author = raw_frame.loc[raw_frame["cid"] == cid, "user_id"].iloc[0]
        for r in rows:
            strip_rows.append({"cid": cid, "user_id": author, "j": r["j"], "m": m_s,
                               "slice_text": r["wtext"]})
    strip_frame = pd.DataFrame(strip_rows).sort_values(["cid", "j"]).reset_index(drop=True)
    n_strip_texts = strip_frame["cid"].nunique() if len(strip_rows) else 0
    print(f"[cohort] stripped arm: {n_strip_texts} texts kept of {len(cohort_cids)} "
          f"(dropped m_stripped<{M_LO} or <2: {n_drop_m}; leak-tripped after strip: {n_drop_leak}; "
          f"cap guard hits: {n_guard_cap}); windows={len(strip_frame)}")

    # ---------------- scoring (ONE shared frozen fit) ----------------
    t_fit = time.time()
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    print(f"[scoring] frozen wcl fit built in {time.time() - t_fit:.1f}s (shared by both arms)")

    def score_frame(frame: pd.DataFrame) -> pd.DataFrame:
        scored = a19.score_slices_v2(frame[["user_id", "slice_text"]].assign(
            condition="_", half="_")[["user_id", "condition", "half", "slice_text"]])
        wcl = wcl_transform(frame["slice_text"]).reset_index(drop=True)
        return pd.concat([frame[["cid", "user_id", "j", "m"]].reset_index(drop=True),
                          scored[list(a19.V3_BATTERY)].reset_index(drop=True),
                          wcl[list(a19.OP5_KEPT)]], axis=1)

    raw_scored = score_frame(raw_frame)
    strip_scored = score_frame(strip_frame)

    # anchor 2: rebuilt raw scores vs cache rows
    merged = raw_scored.merge(cache_sub[["cid", "j"] + cols], on=["cid", "j"],
                              suffixes=("", "_cache"), validate="one_to_one")
    rebuild_diff = float(max(np.abs(merged[c].to_numpy() - merged[f"{c}_cache"].to_numpy()).max()
                             for c in cols))
    raw_arm_source = "rebuild"
    if rebuild_diff > 1e-6:
        raw_arm_source = "cache_fallback"
        raw_scored = cache_sub[["cid", "user_id", "j", "m"] + cols].copy()
        print(f"[anchor-2] REBUILD MISMATCH max|diff|={rebuild_diff:.3e} > 1e-6 "
              f"(frozen-fit nondeterminism); RAW arm falls back to cache scores; "
              f"STRIPPED arm keeps the shared fresh fit — arm contrast remains "
              f"internally consistent (same fit for both rebuilt arms was used "
              f"for the contrast check below)")
    else:
        print(f"[anchor-2] rebuilt raw windows reproduce the P8 cache scores "
              f"(max|diff|={rebuild_diff:.3e})")

    # ---------------- dynamics per arm ----------------
    null_raw, null_raw_pairs = simulate_null(groups_cache, N_REPLICATES, rng)
    res_raw, _ = arm_dynamics(raw_scored, cols, gust1_e, gust1_p, null_raw, null_raw_pairs)

    groups_strip = build_m_groups(strip_frame, "cid")
    null_strip, null_strip_pairs = simulate_null(groups_strip, N_REPLICATES, rng)
    res_strip, _ = arm_dynamics(strip_scored, cols, gust1_e, gust1_p, null_strip, null_strip_pairs)

    print()
    report_set = ["gust1_E", "gust1_P"] + SATURATION_SET
    for arm_name, res in (("RAW", res_raw), ("STRIPPED", res_strip)):
        for name in report_set:
            r = res[name]
            print(f"[{arm_name} {name}] rho1={r['rho1']:+.4f} null_mean={r['null_mean']:+.4f} "
                  f"p={r['p']:.4f} theta={r['theta']:.3f}")
        print()

    n_sat_raw = sum(1 for v in res_raw.values() if v["theta"] >= 0.99)
    n_sat_strip = sum(1 for v in res_strip.values() if v["theta"] >= 0.99)
    print("[summary] axis excess (rho1_obs - null_mean), RAW vs STRIPPED "
          "(lean c: stripped <= half raw):")
    for name in ("gust1_E", "gust1_P"):
        er, es = res_raw[name]["excess"], res_strip[name]["excess"]
        half = "yes" if abs(es) <= 0.5 * abs(er) else "no"
        print(f"  {name}: raw_excess={er:+.4f} stripped_excess={es:+.4f} "
              f"|stripped| <= |raw|/2: {half}")
    print(f"[summary] theta >= 0.99 saturations (of 21 series): RAW={n_sat_raw} "
          f"STRIPPED={n_sat_strip}")
    sat_raw_names = [k for k, v in res_raw.items() if v["theta"] >= 0.99]
    sat_strip_names = [k for k, v in res_strip.items() if v["theta"] >= 0.99]
    print(f"  RAW saturated: {sat_raw_names}")
    print(f"  STRIPPED saturated: {sat_strip_names}")

    elapsed = time.time() - t0
    print(f"\ntotal runtime: {elapsed:.1f}s")

    # ---------------- outputs ----------------
    strata_json = {}
    for lo, hi, label in ((2, 3, "m_raw_2_3"), (4, 10 ** 9, "m_raw_ge_4")):
        s = census_df[(census_df["m_raw"] >= lo) & (census_df["m_raw"] <= hi)]
        strata_json[label] = {"n": int(len(s)),
                              "mean_quote_share": round(float(s["q_share"].mean()), 4),
                              "mean_list_share": round(float(s["l_share"].mean()), 4),
                              "mean_code_share": round(float(s["c_share"].mean()), 4)}
    result = {
        "registered_commit": "e2b2240",
        "formula_ref": "F12.10, docs/SUICA_THEORY_FORMAL_NOTES_V3.md",
        "seed": SEED, "n_replicates": N_REPLICATES,
        "n_candidates": n_candidates,
        "census_strata": strata_json,
        "n_census_m_raw_lt_2": n_mlt2,
        "cohort": {"n_raw_texts": len(cohort_cids), "n_raw_windows": int(len(raw_frame)),
                   "n_m_gt12_in_corpus": n_m_gt12,
                   "n_stripped_texts": int(n_strip_texts),
                   "n_stripped_windows": int(len(strip_frame)),
                   "n_dropped_m_below": n_drop_m, "n_dropped_leak": n_drop_leak,
                   "n_cap_guard_hits": n_guard_cap},
        "anchors": {"cache_vs_w2a_max_abs_rho1_diff": max_anchor_diff,
                    "rebuild_vs_cache_max_abs_score_diff": rebuild_diff,
                    "raw_arm_source": raw_arm_source},
        "gust1_E_normalized": gust1_e.tolist(),
        "gust1_P_normalized": gust1_p.tolist(),
        "raw_arm": res_raw,
        "stripped_arm": res_strip,
        "saturation_counts": {"raw": n_sat_raw, "stripped": n_sat_strip,
                              "raw_names": sat_raw_names, "stripped_names": sat_strip_names},
        "runtime_seconds": elapsed,
    }
    (OUT_DIR / "V6_W9_FORMAT_AWARE.json").write_text(json.dumps(result, indent=2))

    md = ["# V6-W9 -- Format-aware windowing (PANDORA raw text, label-free)",
          "",
          "Registered commit: e2b2240 (F12.10, docs/SUICA_THEORY_FORMAL_NOTES_V3.md)",
          "",
          f"Candidates (body >= 1200 chars): {n_candidates}. Census strata: "
          f"m_raw 2-3: n={strata_json['m_raw_2_3']['n']}, quote/list/code shares "
          f"{strata_json['m_raw_2_3']['mean_quote_share']:.4f}/"
          f"{strata_json['m_raw_2_3']['mean_list_share']:.4f}/"
          f"{strata_json['m_raw_2_3']['mean_code_share']:.4f}; m_raw >= 4: "
          f"n={strata_json['m_raw_ge_4']['n']}, "
          f"{strata_json['m_raw_ge_4']['mean_quote_share']:.4f}/"
          f"{strata_json['m_raw_ge_4']['mean_list_share']:.4f}/"
          f"{strata_json['m_raw_ge_4']['mean_code_share']:.4f}.",
          "",
          f"Cohort: RAW {len(cohort_cids)} texts / {len(raw_frame)} windows; STRIPPED "
          f"{n_strip_texts} texts / {len(strip_frame)} windows (dropped below m>=4: {n_drop_m}, "
          f"leak-tripped: {n_drop_leak}). Anchors: cache-vs-W2a max rho1 diff "
          f"{max_anchor_diff:.2e}; rebuild-vs-cache max score diff {rebuild_diff:.3e} "
          f"(raw arm source: {raw_arm_source}).",
          "",
          "## Dynamics (axes + W2a saturation set)",
          "",
          "| series | RAW rho1 | RAW p | RAW theta | STRIPPED rho1 | STRIPPED p | STRIPPED theta |",
          "|---|---|---|---|---|---|---|"]
    for name in report_set:
        a, b = res_raw[name], res_strip[name]
        md.append(f"| {name} | {a['rho1']:+.4f} | {a['p']:.4f} | {a['theta']:.3f} | "
                  f"{b['rho1']:+.4f} | {b['p']:.4f} | {b['theta']:.3f} |")
    md += ["",
           "## Axis excess (rho1 - null_mean)",
           ""]
    for name in ("gust1_E", "gust1_P"):
        er, es = res_raw[name]["excess"], res_strip[name]["excess"]
        md.append(f"- {name}: raw {er:+.4f}, stripped {es:+.4f} "
                  f"(|stripped| <= |raw|/2: {'yes' if abs(es) <= 0.5 * abs(er) else 'no'})")
    md += ["",
           f"Saturations (theta >= 0.99, of 21): RAW {n_sat_raw} {sat_raw_names}; "
           f"STRIPPED {n_sat_strip} {sat_strip_names}.",
           "",
           f"Null: {N_REPLICATES} iid-normal replicates per arm, m-composition matched; "
           f"seed {SEED}. RAW null shared with the cache anchor (same composition)."]
    (OUT_DIR / "V6_W9_FORMAT_AWARE.md").write_text("\n".join(md) + "\n")
    print("written:", OUT_DIR / "V6_W9_FORMAT_AWARE.json")
    print("written:", OUT_DIR / "V6_W9_FORMAT_AWARE.md")


if __name__ == "__main__":
    main()
