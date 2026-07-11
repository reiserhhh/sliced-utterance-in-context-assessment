#!/usr/bin/env python
"""V5PORT — score the trading-side SUICA v5 form battery on PANDORA and
compare against the v4 battery's purity results. Label-free (Tier-U dev
users only; no criterion labels touched anywhere).

Source of the v5 formulas (ported VERBATIM, with unit notes below):
  /Volumes/projects/trading-agent/trading-agent-claude/
    scripts/run_suica_v5_form_first_retest_285a_mu.py   (lines ~146-245)
    docs/SUICA_V5_FIELD_EVOLUTION_PROPOSAL_20260710.md  (design)
    docs/SUICA_V5_P1_FORM_FIRST_RESULTS_20260710.md     (their gate results)

Comparison design (frozen-convention rule):
  - Same slices as the v4 all-19 purity run (cached, count-verified
    phase2_passA_slicetext_s128_rebuild.parquet).
  - Same estimators, imported directly from
    scripts/run_suica_c2_purity_all19_v1 (component_series,
    estimands_from_series, crossfit_mix_share, corr) — identical halves,
    class map, share formula, and F-gate (class-disjoint >= .15 AND
    share < .30).
  - Unit deviation (documented): v5 scores per POST with occasion packing;
    here features are computed per 128-token SLICE (the v4 unit) so that
    the comparison against v4 rows is apples-to-apples. Length-habit
    features (log_tokens_mean, post_len_cv), which are degenerate on
    fixed-length slices, are computed per COMMENT within the same frozen
    user/condition/half windows instead.
  - Hurdle scoring (v5 proposal P2, untested there): each v2 construct is
    decomposed into hp_<c> = P(any signal in slice) and hi_<c> =
    intensity given signal; both run through the same estimator path.

Known port caveats (reported, not silently fixed):
  - laugh_rate's w-run alternative matches the "www" in URLs on Reddit.
  - JA features (hiragana/script shares, etc.) are expected to be
    degenerate on an English corpus; they are register-transport probes.
  - apostrophe_omission_rate_v5 is v5's 7-word IGNORECASE list, distinct
    from v4's wcl_60 (its natural reference row).
"""
from __future__ import annotations

import json
import re
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_suica_c2_purity_all19_v1 as a19  # noqa: E402
from project_persona.suica import TOKEN_RE  # noqa: E402

OUT_DIR = ROOT / "results" / "suica_v5port_form_battery"
V4_CSV = ROOT / "results" / "suica_c2_purity_all19_v1" / "all19_purity.csv"
GAP_DAYS = 90

# ---- v5 patterns, ported verbatim ------------------------------------------
HIRAGANA_P = r"[぀-ゟ]"
ASCII_VISIBLE_P = r"[\x21-\x7E]"
LAUGH_P = r"(?:[wW]{2,}|[Ｗｗ]{2,}|草|笑)"
EMOJI_KAOMOJI_P = (
    r"(?:[\U0001F300-\U0001FAFF☀-➿⭐❤️]"
    r"|\^_\^|\^-\^|>_<|T_T|;_;|:\)|:\(|:D|xD|XD|orz|OTL|OTZ)"
)
EXCLAIM_QUESTION_P = r"[！？!?]"
ELLIPSIS_P = r"(?:…|\.{3,})"
APOSTROPHE_OMIT_P = r"\b(?:im|dont|ive|cant|wont|didnt|isnt)\b"
ALLCAPS_P = r"\b[A-Z]{2,}\b"
ELONGATION_P = r"([a-z])\1{2,}"
PUNCT_P = r"""[!"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~]"""
FIRST_PERSON_P = r"(?:私|僕|俺|自分|わたし|ぼく|おれ|\bi\b|\bme\b|\bmy\b|\bmine\b|\bim\b|\bive\b)"
SECOND_PERSON_P = r"(?:あなた|君|お前|きみ|おまえ|\byou(?:r|rs)?\b)"
THIRD_PERSON_P = r"(?:彼女|彼|こいつ|あいつ|\bhe\b|\bshe\b|\bthey\b|\bthem\b)"

V2_HURDLE = ["tension_core_v2", "directive_action_v2",
             "first_person_usage_v2", "novelty_play_v2"]


def v5_slice_features(text: pd.Series) -> pd.DataFrame:
    t = text.fillna("").astype(str).astype(object)
    chars = t.str.len().clip(lower=1)
    nonspace = t.str.replace(r"\s+", "", regex=True).str.len().clip(lower=1)
    tok = t.apply(lambda s: len(TOKEN_RE.findall(s))).astype(float).clip(lower=1)

    out = pd.DataFrame(index=t.index)
    out["v5_laugh_rate"] = 100.0 * t.str.count(LAUGH_P) / tok
    out["v5_emoji_kaomoji_rate"] = 100.0 * t.str.count(EMOJI_KAOMOJI_P) / tok
    out["v5_exclaim_question_density"] = 100.0 * t.str.count(EXCLAIM_QUESTION_P) / chars
    out["v5_ellipsis_rate"] = 100.0 * t.str.count(ELLIPSIS_P) / chars
    out["v5_apostrophe_omission_rate"] = 100.0 * t.str.count(APOSTROPHE_OMIT_P, flags=re.IGNORECASE) / tok
    out["v5_allcaps_rate"] = 100.0 * t.str.count(ALLCAPS_P) / tok
    out["v5_elongation_rate"] = 100.0 * t.str.count(ELONGATION_P) / tok
    out["v5_punct_density"] = 100.0 * t.str.count(PUNCT_P) / chars
    out["v5_first_person_rate"] = 100.0 * t.str.count(FIRST_PERSON_P, flags=re.IGNORECASE) / tok
    out["v5_second_person_rate"] = 100.0 * t.str.count(SECOND_PERSON_P, flags=re.IGNORECASE) / tok
    out["v5_third_person_rate"] = 100.0 * t.str.count(THIRD_PERSON_P, flags=re.IGNORECASE) / tok
    out["v5_ascii_share"] = t.str.count(ASCII_VISIBLE_P) / nonspace
    out["v5_hiragana_share"] = t.str.count(HIRAGANA_P) / nonspace
    return out


def comment_length_cells() -> pd.DataFrame:
    """Per (user, condition, half) length habits from comments, replicating
    the frozen half-split of rebuild_passA_with_text() verbatim."""
    comments = pd.read_parquet(a19.TIER_DIR / "tier_u_comments.parquet")
    comments["author"] = comments["author"].astype(str)
    comments["subreddit"] = comments["subreddit"].fillna("__missing__").astype(str)
    comments = comments.sort_values(["author", "created_utc"])
    rows = []
    for user_id, group in comments.groupby("author", sort=False):
        counts = group["subreddit"].value_counts()
        conds = counts.loc[counts >= 4].index.tolist()[:8]
        if len(conds) < 2:
            continue
        sub = group.loc[group["subreddit"].isin(conds)]
        t = sub["created_utc"].to_numpy(float)
        if len(t) < 12:
            continue
        t40, t60 = np.quantile(t, [0.40, 0.60])
        if (t60 - t40) / 86400.0 < GAP_DAYS:
            continue
        early = sub.loc[sub["created_utc"] <= t40]
        late = sub.loc[sub["created_utc"] >= t60]
        for half, part in [("early", early), ("late", late)]:
            for cond, cell in part.groupby("subreddit"):
                if len(cell) < 2:
                    continue
                tokc = cell["body"].astype(str).apply(
                    lambda s: len(TOKEN_RE.findall(s))).to_numpy(float)
                mean = float(tokc.mean())
                rows.append({"user_id": str(user_id), "condition": str(cond),
                             "half": half,
                             "v5_log_tokens_mean": float(np.log1p(tokc).mean()),
                             "v5_post_len_cv": float(tokc.std() / mean) if mean > 0 else 0.0})
    return pd.DataFrame(rows)


def decompose(src: pd.DataFrame, col: str, class_of: dict) -> dict:
    rng = np.random.default_rng(zlib.crc32(col.encode()) % (2**31))
    d = src[["user_id", "condition", "half", col]].dropna(subset=[col])
    um = d.groupby(["user_id", "half"])[col].mean().unstack().dropna()
    if len(um) < 50 or um["early"].std() < 1e-9 or um["late"].std() < 1e-9:
        return {"construct": col, "verdict": "insufficient variance",
                "n_users": int(len(um))}
    rho_raw = a19.corr(um["early"], um["late"])
    cell = (d.groupby(["user_id", "condition", "half"])[col].mean()
            .unstack("half").dropna())
    cell.index.names = ["user", "condition"]
    series = a19.component_series(cell, class_of)
    est = a19.estimands_from_series(series)
    mix = a19.crossfit_mix_share(d, col, rng)
    share = np.nan
    if est["rho_shared_matched"] and est["rho_shared_matched"] >= 0.10:
        share = float(np.clip(1 - est["rho_cond_disjoint"] / est["rho_shared_matched"], 0, 1))
    boot = []
    n = len(series)
    for _ in range(a19.N_BOOT):
        subb = series.iloc[rng.integers(0, n, n)]
        e2 = a19.estimands_from_series(subb)
        if e2["rho_shared_matched"] and e2["rho_shared_matched"] >= 0.10:
            boot.append(float(np.clip(1 - e2["rho_cond_disjoint"] / e2["rho_shared_matched"], 0, 1)))
    ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))) if len(boot) >= 100 else (np.nan, np.nan)
    if np.isnan(share):
        family = "undetermined"
        ci = (np.nan, np.nan)
    elif est["rho_class_disjoint"] >= 0.15 and share < 0.30:
        family = "F-family (flesh trait)"
    elif share > 0.30 and est["rho_class_disjoint"] < 0.10:
        family = "C-family (venue signature)"
    else:
        family = "composite"
    return {"construct": col, "rho_raw": rho_raw,
            "rho_shared_matched": est["rho_shared_matched"],
            "rho_cond_disjoint": est["rho_cond_disjoint"],
            "rho_class_disjoint": est["rho_class_disjoint"],
            "c1_share": share, "ci_lo": ci[0], "ci_hi": ci[1],
            "mediated_total_upper": mix["mediated_total"],
            "v4_family": family, "n_users": int(len(um)), "verdict": ""}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = a19.rebuild_passA_with_text()
    print(f"slices: {len(frame)}")
    cmap = pd.read_csv(a19.CLASS_MAP)
    class_of = dict(zip(cmap["condition"], cmap["class_id"]))

    print("scoring v5 slice features ...")
    feats = v5_slice_features(frame["slice_text"])
    src = pd.concat([frame[["user_id", "condition", "half"]].reset_index(drop=True),
                     feats.reset_index(drop=True)], axis=1)

    print("scoring v2 constructs for hurdle decomposition ...")
    scored = a19.score_slices_v2(frame[["user_id", "condition", "half", "slice_text"]])
    for c in V2_HURDLE:
        src[f"v5hp_{c}"] = (scored[c].to_numpy() > 0).astype(float)
        src[f"v5hi_{c}"] = np.where(scored[c].to_numpy() > 0, scored[c].to_numpy(), np.nan)

    print("computing comment-level length habits ...")
    lencells = comment_length_cells()

    rows = []
    for col in list(feats.columns) + [f"v5hp_{c}" for c in V2_HURDLE] + [f"v5hi_{c}" for c in V2_HURDLE]:
        r = decompose(src, col, class_of)
        rows.append(r)
        print(f"  {col}: {r.get('v4_family', r.get('verdict'))} "
              f"raw={r.get('rho_raw', float('nan'))}")
    for col in ["v5_log_tokens_mean", "v5_post_len_cv"]:
        r = decompose(lencells, col, class_of)
        rows.append(r)
        print(f"  {col}: {r.get('v4_family', r.get('verdict'))} "
              f"raw={r.get('rho_raw', float('nan'))}")

    df = pd.DataFrame(rows)
    df.round(4).to_csv(OUT_DIR / "v5port_purity.csv", index=False)

    ref = None
    if V4_CSV.exists():
        ref = pd.read_csv(V4_CSV)
    md = ["# V5PORT — trading-side SUICA v5 form battery scored on PANDORA (v4 conventions)", "",
          "Label-free Tier-U run; same slices/estimators/gate as the v4 all-19 table.",
          "Formulas ported verbatim from trading-agent-claude (see script docstring).", "",
          df.round(3).to_markdown(index=False), ""]
    if ref is not None:
        keep = ref[ref["construct"].isin(["first_person_usage_v2", "wcl_60", "wcl_13", "wcl_23",
                                          "tension_core_v2", "directive_action_v2", "novelty_play_v2"])]
        md += ["## v4 reference rows (all19, round-10 audited)", "",
               keep.round(3).to_markdown(index=False), ""]
    md += ["## Notes",
           "- Unit deviation: v5 native unit is post/occasion; here rates are per 128-token slice",
           "  (v4 unit) for comparability; length habits are per comment within the frozen halves.",
           "- laugh_rate counts URL 'www' on Reddit (ported as-is; interpret accordingly).",
           "- JA features on an EN corpus are register-transport probes, expected degenerate.",
           "- Hurdle rows: v5hp_* = P(any signal per slice), v5hi_* = intensity given signal;",
           "  plain-rate references are the v4 rows above (v5 proposal P2, first empirical test)."]
    (OUT_DIR / "V5PORT_RESULTS.md").write_text("\n".join(md))
    print("written:", OUT_DIR / "V5PORT_RESULTS.md")


if __name__ == "__main__":
    main()
