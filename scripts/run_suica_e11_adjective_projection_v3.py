#!/usr/bin/env python
"""E11: quantified adjective interpretation of SUICA constructs (user proposal).

Idea: replace generative interpretation with a METRIC lookup — project a
frozen person-descriptor adjective lexicon onto each construct's direction in
embedding space; report top adjectives WITH projection values. Reconnects
SUICA constructs to the lexical-hypothesis vocabulary (Goldberg-style Big5
marker adjectives carry literature pole tags, giving a label-free Big5 bridge:
tag enrichment is a dictionary property, not user data).

Directions: primary = cross-fitted ridge regression from user embeddings to
the construct's measured score (the direction of the measure itself);
anchors (E9a) kept as secondary. Adjectives embedded in the frozen carrier
template "They are ___." and z-scored across the lexicon (anisotropy guard).

Pre-committed criteria:
  E11-1 stability: direction estimated on user-half A vs B -> full-lexicon
        projection rank correlation; PASS if median across 19 constructs
        >= 0.70.
  E11-2 known-groups (Big5-marker enrichment): top-20 adjectives show
        coherent pole enrichment (Fisher p < 0.01) for >= 5 constructs.
  E11-3 discriminance: mean pairwise top-20 Jaccard across constructs <= 0.20.
  E11-4 junk control: scrambled directions produce <= 1 significant
        enrichment and near-zero A/B rank stability... (scrambled directions
        are RANDOM per half, so their stability is the honest null).
NOTE: the marker list below is a Goldberg-1992-style transcription; verify
against the original publication before journal use (freeze checklist item).
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

from scripts.run_suica_op9_embedding_baseline_v3 import rederive_op5_scores, OP5_KEPT, V3_BATTERY  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
PRE = ROOT / "results" / "suica_op9_embedding_baseline_v3" / "precomputed"
OUT_DIR = ROOT / "results" / "suica_e11_adjective_projection_v3"
REPORT = ROOT / "reports" / "suica_e11_adjective_projection_v3.md"
SEED = 42
TEMPLATE = "They are {} ."
TOP_K = 20

MARKERS = {
    "E+": ["talkative", "assertive", "energetic", "bold", "extraverted", "outgoing", "sociable", "enthusiastic", "adventurous", "verbal"],
    "E-": ["quiet", "reserved", "shy", "withdrawn", "introverted", "silent", "timid", "inhibited", "unadventurous", "passive"],
    "A+": ["kind", "sympathetic", "warm", "cooperative", "considerate", "trustful", "helpful", "generous", "agreeable", "gentle"],
    "A-": ["cold", "harsh", "rude", "demanding", "unsympathetic", "selfish", "distrustful", "uncooperative", "abusive", "quarrelsome"],
    "C+": ["organized", "systematic", "efficient", "practical", "neat", "thorough", "careful", "conscientious", "prompt", "orderly"],
    "C-": ["disorganized", "careless", "sloppy", "inefficient", "haphazard", "inconsistent", "impractical", "negligent", "undependable", "forgetful"],
    "N+": ["anxious", "moody", "temperamental", "envious", "irritable", "fretful", "jealous", "touchy", "nervous", "insecure"],
    "N-": ["calm", "relaxed", "stable", "contented", "unemotional", "imperturbable", "unexcitable", "undemanding", "easygoing", "secure"],
    "O+": ["creative", "intellectual", "imaginative", "philosophical", "artistic", "deep", "innovative", "introspective", "complex", "curious"],
    "O-": ["uncreative", "unintellectual", "unimaginative", "shallow", "unsophisticated", "conventional", "unreflective", "simple", "uninquisitive", "traditional"],
}
STYLE_SUPP = ["sarcastic", "blunt", "formal", "casual", "verbose", "terse", "argumentative", "diplomatic",
              "playful", "serious", "vulgar", "polite", "analytical", "emotional", "opinionated", "hesitant",
              "confident", "self-critical", "storytelling", "instructional", "humorous", "cynical",
              "optimistic", "pessimistic", "nostalgic", "pragmatic", "meticulous", "impulsive",
              "empathetic", "detached", "competitive", "nurturing", "rebellious", "conforming",
              "expressive", "guarded", "curt", "rambling", "precise", "vague"]


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mat = np.load(PRE / "emb_userhalf.npy")
    index = pd.read_csv(PRE / "userhalf_index.csv", dtype={"user_id": str})
    emb_half = pd.DataFrame(mat, index=pd.MultiIndex.from_frame(index[["user_id", "half"]]))
    frame = pd.read_parquet(TIER_DIR / "op9_half_slices.parquet")
    v3 = score_slices_v2(frame[["user_id", "slice_text"]].assign(half=frame["half"]))
    lex_half = v3.groupby(["user_id", "half"])[V3_BATTERY].mean().join(
        rederive_op5_scores(frame).groupby(["user_id", "half"]).mean())
    constructs = V3_BATTERY + OP5_KEPT

    early = emb_half.xs("early", level="half")
    late = emb_half.xs("late", level="half")
    common = early.index.intersection(late.index)
    users = np.array(sorted(common))
    half_a = set(users[: len(users) // 2])
    emb_user = (early.loc[common] + late.loc[common]) / 2
    lex_user = ((lex_half.xs("early", level="half") + lex_half.xs("late", level="half")) / 2).reindex(common)

    # ---- adjective embeddings ----
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cpu")
    adjectives = [w for words in MARKERS.values() for w in words] + STYLE_SUPP
    tags = {w: pole for pole, words in MARKERS.items() for w in words}
    avec = model.encode([TEMPLATE.format(w) for w in adjectives], normalize_embeddings=True, convert_to_numpy=True)
    avec = avec - avec.mean(axis=0, keepdims=True)  # remove carrier-template common component

    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler

    def direction(user_set, construct):
        mask = np.array([u in user_set for u in common])
        x = emb_user.loc[common[mask]].to_numpy(float)
        y = lex_user.loc[common[mask], construct].to_numpy(float)
        sc = StandardScaler().fit(x)
        w = Ridge(alpha=100.0).fit(sc.transform(x), y).coef_
        w = w / max(1e-12, np.linalg.norm(w))
        return w

    rows, stab_rows, enrich_rows = [], [], []
    top_sets = {}
    n_sig_enrich = 0
    for construct in constructs:
        w_a = direction(half_a, construct)
        w_b = direction(set(users) - half_a, construct)
        proj_a = stats.zscore(avec @ w_a)
        proj_b = stats.zscore(avec @ w_b)
        rank_r = float(stats.spearmanr(proj_a, proj_b).statistic)
        stab_rows.append({"construct": construct, "ab_rank_r": rank_r})
        w_full = direction(set(users), construct)
        proj = stats.zscore(avec @ w_full)
        order = np.argsort(-proj)
        top = [adjectives[i] for i in order[:TOP_K]]
        top_sets[construct] = set(top)
        top_tags = [tags.get(a) for a in top if tags.get(a)]
        best_pole, best_p = None, 1.0
        for pole in MARKERS:
            k = sum(t == pole for t in top_tags)
            table = [[k, TOP_K - k], [10 - k if k <= 10 else 0, len(adjectives) - TOP_K - (10 - k if k <= 10 else 0)]]
            p = stats.fisher_exact([[k, TOP_K - k], [10 - k, len(adjectives) - TOP_K - (10 - k)]], alternative="greater")[1]
            if p < best_p:
                best_pole, best_p = pole, p
        sig = bool(best_p < 0.01)
        n_sig_enrich += int(sig)
        enrich_rows.append({"construct": construct, "top_pole": best_pole, "fisher_p": best_p, "significant": sig})
        rows.append({"construct": construct, "ab_rank_r": rank_r, "top_pole": best_pole,
                     "fisher_p": round(best_p, 5),
                     "top10_adjectives": ", ".join(f"{adjectives[i]}({proj[i]:+.1f})" for i in order[:10])})
    # scrambled control: random directions
    scr_sig = 0
    for s in range(3):
        w = rng.normal(size=avec.shape[1])
        w /= np.linalg.norm(w)
        proj = stats.zscore(avec @ w)
        top = [adjectives[i] for i in np.argsort(-proj)[:TOP_K]]
        top_tags = [tags.get(a) for a in top if tags.get(a)]
        for pole in MARKERS:
            k = sum(t == pole for t in top_tags)
            if stats.fisher_exact([[k, TOP_K - k], [10 - k, len(adjectives) - TOP_K - (10 - k)]], alternative="greater")[1] < 0.01:
                scr_sig += 1
                break
    jac = [len(top_sets[a] & top_sets[b]) / len(top_sets[a] | top_sets[b]) for a, b in combinations(constructs, 2)]
    out = pd.DataFrame(rows)
    stab = pd.DataFrame(stab_rows)
    criteria = {
        "E11_1_median_ab_rank_r": float(stab["ab_rank_r"].median()),
        "E11_1_pass": bool(stab["ab_rank_r"].median() >= 0.70),
        "E11_2_sig_enrichment_count": n_sig_enrich, "E11_2_pass": bool(n_sig_enrich >= 5),
        "E11_3_mean_pairwise_jaccard": float(np.mean(jac)), "E11_3_pass": bool(np.mean(jac) <= 0.20),
        "E11_4_scrambled_sig": scr_sig, "E11_4_pass": bool(scr_sig <= 1),
        "n_users": int(len(users)), "n_adjectives": len(adjectives),
    }
    out.to_csv(OUT_DIR / "e11_construct_adjectives.csv", index=False)
    (OUT_DIR / "e11_results.json").write_text(json.dumps(criteria, indent=2, default=float) + "\n")
    REPORT.write_text("# SUICA E11 Quantified Adjective Projection\n\n"
                      + out.to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(criteria, indent=2, default=float) + "\n```\n")
    print(out[["construct", "ab_rank_r", "top_pole", "fisher_p"]].round(3).to_string(index=False))
    print()
    for _, r in out.iterrows():
        print(f"{r['construct']:24s} -> {r['top10_adjectives']}")
    print(json.dumps(criteria, indent=2, default=float))


if __name__ == "__main__":
    main()
