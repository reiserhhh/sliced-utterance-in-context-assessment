#!/usr/bin/env python
"""E11 v2: quantified adjective interpretation — fixed per the v1 failure list.

Fixes over v1 (all four specified in the ledger):
  F1 BIPOLAR scoring: 5 marker axes (E/A/C/N/O) built as mean(+pole) -
     mean(-pole); adjective-level scores are CONTRAST scores
     c(adj) = z_proj(adj) - mean z_proj(opposite pole). Antonym proximity
     neutralized by construction.
  F2 PERMUTATION calibration: 200 random unit directions give the null for
     (a) marker-axis |projection| (per-axis 99th pct) and (b) top-20 pole
     enrichment (max-odds 95th pct). No analytic Fisher.
  F3 DIRECTION stabilization: direction = ridge fit on ALL users; stability
     via 50 user-bootstrap refits -> per-adjective/axis CIs and bootstrap
     rank stability (bar: median rank-r >= 0.70).
  F4 SENSE-COLLISION screen: top adjectives whose literal token usage in the
     corpus correlates with the construct score (|r| > 0.30) are flagged
     "lexical coupling — interpret cautiously".

Modes: default = 19 trait constructs (vertical cut); --state = E7 month
state modes f1/f3/f5 (horizontal cut) using month-cell embeddings encoded on
the CUDA box, within-person centered, cross-referenced to the frozen E7
loadings.

Pre-committed v2 criteria:
  V2-1 median bootstrap rank stability >= 0.70;
  V2-2 >= 8 traits (>= 1 state mode in --state) with at least one marker axis
       beyond the permutation 99th percentile and CI excluding 0;
  V2-3 pairwise top-20 Jaccard <= 0.20;
  V2-4 empirical null axis-hit rate at the 99th-pct threshold <= 0.02.
"""
from __future__ import annotations

import json
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_e11_adjective_projection_v3 import MARKERS, STYLE_SUPP, TEMPLATE  # noqa: E402
from scripts.run_suica_op9_embedding_baseline_v3 import rederive_op5_scores, OP5_KEPT, V3_BATTERY  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2, fast_anchor_rates  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
PRE = ROOT / "results" / "suica_op9_embedding_baseline_v3" / "precomputed"
STATE_EMB = TIER_DIR / "e11_state_month_emb.npy"
STATE_IDX = TIER_DIR / "e11_state_month_index.csv"
E7_LOADINGS = ROOT / "results" / "suica_e7_within_state_discovery_v3_month" / "e7_within_loadings.csv"
MODE_STATE = "--state" in sys.argv
TAG = "state" if MODE_STATE else "trait"
OUT_DIR = ROOT / "results" / f"suica_e11v2_adjective_{TAG}"
REPORT = ROOT / "reports" / f"suica_e11v2_adjective_{TAG}.md"
SEED = 42
N_BOOT = 50
N_PERM = 200
TOP_K = 20
STATE_FACTORS = ["state_f1", "state_f3", "state_f5"]
OPP = {"E+": "E-", "E-": "E+", "A+": "A-", "A-": "A+", "C+": "C-", "C-": "C+",
       "N+": "N-", "N-": "N+", "O+": "O-", "O-": "O+"}


def embed_lexicon():
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cpu")
    adjectives = [w for words in MARKERS.values() for w in words] + STYLE_SUPP
    tags = {w: pole for pole, words in MARKERS.items() for w in words}
    avec = model.encode([TEMPLATE.format(w) for w in adjectives], normalize_embeddings=True, convert_to_numpy=True)
    avec = avec - avec.mean(axis=0, keepdims=True)
    axes = {}
    for dim in "EACNO":
        plus = avec[[i for i, w in enumerate(adjectives) if tags.get(w) == f"{dim}+"]].mean(axis=0)
        minus = avec[[i for i, w in enumerate(adjectives) if tags.get(w) == f"{dim}-"]].mean(axis=0)
        ax = plus - minus
        axes[dim] = ax / np.linalg.norm(ax)
    return adjectives, tags, avec, axes


def contrast_scores(direction, avec, adjectives, tags):
    z = stats.zscore(avec @ direction)
    pole_mean = {pole: np.mean([z[i] for i, w in enumerate(adjectives) if tags.get(w) == pole])
                 for pole in MARKERS}
    out = np.array([z[i] - pole_mean[OPP[tags[w]]] if w in tags else z[i]
                    for i, w in enumerate(adjectives)])
    return out, z


def load_targets():
    """Return (X rows-units embedding matrix, Y dict target->values, unit user ids for bootstrap)."""
    if not MODE_STATE:
        mat = np.load(PRE / "emb_userhalf.npy")
        index = pd.read_csv(PRE / "userhalf_index.csv", dtype={"user_id": str})
        emb_half = pd.DataFrame(mat, index=pd.MultiIndex.from_frame(index[["user_id", "half"]]))
        frame = pd.read_parquet(TIER_DIR / "op9_half_slices.parquet")
        v3 = score_slices_v2(frame[["user_id", "slice_text"]].assign(half=frame["half"]))
        lex_half = v3.groupby(["user_id", "half"])[V3_BATTERY].mean().join(
            rederive_op5_scores(frame).groupby(["user_id", "half"]).mean())
        early, late = emb_half.xs("early", level="half"), emb_half.xs("late", level="half")
        common = early.index.intersection(late.index)
        x = ((early.loc[common] + late.loc[common]) / 2).to_numpy(float)
        lex = ((lex_half.xs("early", level="half") + lex_half.xs("late", level="half")) / 2).reindex(common)
        y = {c: lex[c].to_numpy(float) for c in V3_BATTERY + OP5_KEPT}
        return x, y, np.array(common), frame
    emb = np.load(STATE_EMB)
    idx = pd.read_csv(STATE_IDX, dtype={"user_id": str})
    slices = pd.read_parquet(TIER_DIR / "e11_state_month_slices.parquet")
    feats = pd.DataFrame([fast_anchor_rates(t) for t in slices["slice_text"]])
    fcols = [c for c in feats.columns if c.endswith("_rate") and c != "token_count_anchor"
             and "__" not in c and c not in ("projective_tension_rate",)]
    fcols = sorted([c for c in fcols if not c.startswith("directive_interpersonal")])
    cellf = pd.concat([slices[["user_id", "month"]], feats[fcols]], axis=1).groupby(
        ["user_id", "month"], as_index=False)[fcols].mean()
    load = pd.read_csv(E7_LOADINGS, index_col=0)
    fcols = [c for c in load.index if c in cellf.columns]
    w = cellf.copy()
    w[fcols] = w[fcols] - w.groupby("user_id")[fcols].transform("mean")
    z = (w[fcols] - w[fcols].mean()) / w[fcols].std().replace(0, 1)
    scores = z.to_numpy(float) @ load.loc[fcols, STATE_FACTORS].to_numpy(float)
    key = cellf[["user_id", "month"]]
    emb_df = pd.DataFrame(emb)
    emb_df[["user_id", "month"]] = idx[["user_id", "month"]]
    emb_cell = emb_df.groupby(["user_id", "month"], as_index=False).mean()
    merged = key.merge(emb_cell, on=["user_id", "month"])
    ecols = [c for c in merged.columns if isinstance(c, int) or str(c).isdigit()]
    x = merged[ecols].to_numpy(float)
    x = x - pd.DataFrame(x).groupby(merged["user_id"].to_numpy()).transform("mean").to_numpy()
    aligned = key.merge(cellf[["user_id", "month"]].assign(row=np.arange(len(cellf))), on=["user_id", "month"])
    y = {f: scores[aligned["row"].to_numpy(), j] for j, f in enumerate(STATE_FACTORS)}
    return x, y, merged["user_id"].to_numpy(), None


def fit_direction(x, yv, sub_idx, alpha=100.0):
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    sc = StandardScaler().fit(x[sub_idx])
    w = Ridge(alpha=alpha).fit(sc.transform(x[sub_idx]), yv[sub_idx]).coef_
    return w / max(1e-12, np.linalg.norm(w))


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    adjectives, tags, avec, axes = embed_lexicon()
    x, targets, units, frame = load_targets()
    unit_ids = np.array(units)
    uniq_units = np.unique(unit_ids)

    # permutation nulls
    null_axis = {d: [] for d in "EACNO"}
    null_top_odds = []
    for _ in range(N_PERM):
        d = rng.normal(size=x.shape[1]); d /= np.linalg.norm(d)
        c, z = contrast_scores(d, avec, adjectives, tags)
        for dim in "EACNO":
            null_axis[dim].append(abs(float(axes[dim] @ d)))
        top = np.argsort(-c)[:TOP_K]
        counts = {}
        for i in top:
            t = tags.get(adjectives[i])
            if t:
                counts[t] = counts.get(t, 0) + 1
        null_top_odds.append(max(counts.values()) if counts else 0)
    axis_thr = {d: float(np.percentile(null_axis[d], 99)) for d in "EACNO"}
    odds_thr = float(np.percentile(null_top_odds, 95))
    null_hit_rate = float(np.mean([[abs(axes[d] @ (v := rng.normal(size=x.shape[1])) / np.linalg.norm(v)) > axis_thr[d]
                                    for d in "EACNO"] for _ in range(100)]))

    # adjective token usage per unit (sense-collision screen; trait mode only)
    usage = None
    if frame is not None:
        texts = frame.groupby("user_id")["slice_text"].apply(lambda s: " ".join(s)[:30000].lower())
        usage = pd.DataFrame({w: texts.str.contains(rf"\b{w}\b", regex=True).astype(float) for w in adjectives})

    rows, tops = [], {}
    for name, yv in targets.items():
        d_full = fit_direction(x, yv, np.arange(len(x)))
        c_full, _ = contrast_scores(d_full, avec, adjectives, tags)
        boot_cs, boot_ax = [], []
        for b in range(N_BOOT):
            brng = np.random.default_rng(1000 + b)
            take = brng.choice(uniq_units, size=len(uniq_units), replace=True)
            mask_idx = np.concatenate([np.where(unit_ids == u)[0] for u in take])
            try:
                d_b = fit_direction(x, yv, mask_idx)
            except Exception:
                continue
            cb, _ = contrast_scores(d_b, avec, adjectives, tags)
            boot_cs.append(cb)
            boot_ax.append([float(axes[dim] @ d_b) for dim in "EACNO"])
        boot_cs = np.array(boot_cs); boot_ax = np.array(boot_ax)
        rank_stab = float(np.median([stats.spearmanr(boot_cs[i], c_full).statistic for i in range(len(boot_cs))]))
        ax_summary = {}
        n_sig_axes = 0
        for j, dim in enumerate("EACNO"):
            val = float(axes[dim] @ d_full)
            lo, hi = np.percentile(boot_ax[:, j], [2.5, 97.5])
            sig = bool(abs(val) > axis_thr[dim] and (lo > 0 or hi < 0))
            n_sig_axes += int(sig)
            ax_summary[dim] = f"{val:+.3f}[{lo:+.2f},{hi:+.2f}]{'*' if sig else ''}"
        order = np.argsort(-c_full)
        tops[name] = set(adjectives[i] for i in order[:TOP_K])
        top_list = []
        for i in order[:10]:
            lo, hi = np.percentile(boot_cs[:, i], [2.5, 97.5])
            flag = ""
            if usage is not None and adjectives[i] in usage.columns:
                ur = float(np.corrcoef(usage[adjectives[i]].reindex(uniq_units).fillna(0),
                                        pd.Series(yv, index=unit_ids).groupby(level=0).mean().reindex(uniq_units))[0, 1]) if not MODE_STATE else 0.0
                if abs(ur) > 0.30:
                    flag = "!lex"
            top_list.append(f"{adjectives[i]}({c_full[i]:+.1f}[{lo:+.1f},{hi:+.1f}]{flag})")
        top_counts = {}
        for i in order[:TOP_K]:
            t = tags.get(adjectives[i])
            if t:
                top_counts[t] = top_counts.get(t, 0) + 1
        enr_ok = bool(top_counts and max(top_counts.values()) > odds_thr)
        rows.append({"target": name, "rank_stability": rank_stab, "n_sig_axes": n_sig_axes,
                     **{f"axis_{d}": ax_summary[d] for d in "EACNO"},
                     "enrichment_beyond_null": enr_ok, "top10": ", ".join(top_list)})
    out = pd.DataFrame(rows)
    jac = [len(tops[a] & tops[b]) / len(tops[a] | tops[b]) for a, b in combinations(tops, 2)] if len(tops) > 1 else [0]
    sig_targets = int((out["n_sig_axes"] >= 1).sum())
    criteria = {
        "mode": TAG, "n_units": int(len(uniq_units)),
        "V2_1_median_rank_stability": float(out["rank_stability"].median()),
        "V2_1_pass": bool(out["rank_stability"].median() >= 0.70),
        "V2_2_targets_with_sig_axis": sig_targets,
        "V2_2_pass": bool(sig_targets >= (1 if MODE_STATE else 8)),
        "V2_3_mean_jaccard": float(np.mean(jac)), "V2_3_pass": bool(np.mean(jac) <= 0.20),
        "V2_4_null_axis_hit_rate": null_hit_rate, "V2_4_pass": bool(null_hit_rate <= 0.02),
        "axis_thresholds_99pct": axis_thr, "enrichment_odds_thr_95pct": odds_thr,
    }
    out.to_csv(OUT_DIR / "e11v2_profiles.csv", index=False)
    (OUT_DIR / "e11v2_results.json").write_text(json.dumps(criteria, indent=2, default=float) + "\n")
    REPORT.write_text(f"# SUICA E11 v2 Adjective Projection ({TAG})\n\n"
                      + out.drop(columns=["top10"]).round(3).to_markdown(index=False)
                      + "\n\n## Top-10 contrast adjectives (value [bootstrap CI], !lex = lexical-coupling flag)\n\n"
                      + "\n".join(f"- **{r['target']}**: {r['top10']}" for _, r in out.iterrows())
                      + "\n\n```json\n" + json.dumps(criteria, indent=2, default=float) + "\n```\n")
    print(out.drop(columns=["top10"]).round(3).to_string(index=False))
    print(json.dumps({k: v for k, v in criteria.items() if not isinstance(v, dict)}, indent=2, default=float))


if __name__ == "__main__":
    main()
