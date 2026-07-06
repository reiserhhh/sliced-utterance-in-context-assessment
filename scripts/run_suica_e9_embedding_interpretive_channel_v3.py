#!/usr/bin/env python
"""E9: the embedding interpretive channel — anchor projection + neighbor reading.

The user's "translation" intuition, operationalized two ways on the audited
bge-large user-half vectors (OP-9 assets):

E9a ANCHOR PROJECTION (definition -> direction): each construct's operational
    definition is written as 4-6 anchor phrases; construct direction =
    mean(anchor embeddings) - corpus centroid; person score = user-vector
    projection. Tests (pre-committed):
      - stability: disjoint-occasion (early/late) r of anchor scores;
      - MTMM: convergent (anchor vs lexical, same construct) must exceed the
        best discriminant (anchor vs any other lexical construct);
      - falsifiability control: 3 scrambled-word anchor sets must NOT show
        comparable convergence.
    PASS rule: >= 8/19 constructs with stability r >= 0.30 AND
    convergent > discriminant; scrambled controls fail these bars.

E9b NEIGHBOR READING (position -> profile): for each user, take the k=50
    nearest OTHER users by EARLY-half embedding cosine; "interpret" the user
    as the mean of the neighbors' LATE-half lexical profiles; compare with
    the user's OWN late-half measured profile. Null: random neighbors.
    PASS rule: >= 8/19 constructs with borrowed-vs-own r exceeding the
    random-neighbor null by >= 0.15 (cluster bootstrap CI > 0).

Governance: bge-large-en-v1.5 frozen as the model id; anchors are frozen in
this file BEFORE running; no Big5/MBTI wording in anchors; guide rules G1-G10.
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

from scripts.run_suica_op9_embedding_baseline_v3 import rederive_op5_scores, OP5_KEPT, V3_BATTERY  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
PRE = ROOT / "results" / "suica_op9_embedding_baseline_v3" / "precomputed"
OUT_DIR = ROOT / "results" / "suica_e9_embedding_interpretive_v3"
REPORT = ROOT / "reports" / "suica_e9_embedding_interpretive_v3.md"
SEED = 42
K_NEIGHBORS = 50

ANCHORS: dict[str, list[str]] = {
    "first_person_usage_v2": [
        "I keep writing about myself and my own experience.",
        "In my case this happened to me personally.",
        "I think I did it because I wanted it myself.",
        "My own story, my feelings, my life.",
    ],
    "directive_action_v2": [
        "You should do it this way.",
        "Try this first, then you need to check the settings.",
        "Don't do that; you have to start with the basics.",
        "My advice to you: take the offer.",
    ],
    "tension_core_v2": [
        "I'm worried this might go wrong.",
        "It was a stressful, difficult situation and I wasn't sure what to do.",
        "There is a risk of losing everything and it scares people.",
        "Maybe it fails, maybe not; the conflict made everything uncertain.",
    ],
    "novelty_play_v2": [
        "Trying a new idea just for fun.",
        "It's a fresh, creative and interesting concept to explore.",
        "Playing around with different possibilities is exciting.",
        "A novel approach nobody tried before.",
    ],
    "wcl_60": [
        "dont worry im sure its fine thats how it goes",
        "cant believe he didnt say anything ill ask later",
        "im not sure but thats what youre getting wont change",
        "doesnt matter lets just go im ready",
    ],
    "wcl_03": [
        "This is so great, I absolutely love it!",
        "Awesome work, really happy for you, super cool.",
        "Definitely one of the best things ever, amazing.",
        "So glad this happened, wonderful news.",
    ],
    "wcl_36": [
        "My mom and dad visited and the kids loved it.",
        "Our family dinner with my brother and his wife.",
        "My daughter started school and my husband took photos.",
        "Growing up at home with my sister and our dog.",
    ],
    "wcl_11": [
        "Use the newer version and update the driver to fix it.",
        "The device works if you reset the settings and reinstall.",
        "Check the cable, then the card, then the screen.",
        "This tool works well; the app has a useful feature.",
    ],
    "wcl_45": [
        "That claim is simply not true; the facts say otherwise.",
        "I believe the evidence supports a different conclusion, however.",
        "It's a matter of what actually happened, not opinion.",
        "The argument fails because the premise is false.",
    ],
    "wcl_25": [
        "The character development in that episode was brilliant.",
        "The plot of the show got weaker in the last season.",
        "The movie's story and the main character's arc.",
        "That series finale changed how I see the whole story.",
    ],
    "wcl_02": [
        "Our team can win the season if the defense holds.",
        "Huge game tonight, the fans are ready.",
        "They lost the match but played well against a strong side.",
        "Best player in the league this year, no contest.",
    ],
    "wcl_07": [
        "The government's new policy will affect the country.",
        "Voters and parties are fighting over the law.",
        "The state should not decide this; it's a public issue.",
        "Political news dominated the debate this week.",
    ],
    "wcl_54": [
        "In this case, the outcome is likely due to several factors.",
        "The number of instances is common, which suggests a pattern.",
        "As far as the evidence goes, this is possible but not certain.",
        "Which, in most cases, is due to the same underlying cause.",
    ],
    "wcl_22": [
        "He walked inside, the door was open, the room was dark.",
        "There was a man standing near the old house by the road.",
        "She passed the gate and stopped; something moved nearby.",
        "The place was empty, one light on, footsteps outside.",
    ],
    "wcl_13": [
        "No, that's not why; it doesn't work like that.",
        "I don't think so, and I wouldn't say that at all.",
        "That's just not true, it's not what happened.",
        "Why would you not check? It isn't hard.",
    ],
    "wcl_35": [
        "Watched the video, the music was great, subscribed to the channel.",
        "My favorite song from that album, on repeat all week.",
        "That clip on the stream was hilarious, watch it.",
        "The sound quality of the new track is amazing.",
    ],
    "wcl_15": [
        "yeah lol i was gonna say that haha",
        "oh hey yep kinda figured, gotta go tho",
        "haha yeah nah it's fine dude",
        "yo that's wild lol ok gonna try it",
    ],
    "wcl_23": [
        "That's fucking ridiculous, what the hell.",
        "This shit is insane, damn.",
        "Holy crap that was brutal, hate it.",
        "What a load of bullshit, seriously.",
    ],
    "wcl_20": [
        "Level up fast, max the build, stack damage.",
        "Hit the boss, dodge, heal, repeat the run.",
        "The drop rate is low but the loot is worth it.",
        "Nerfed the weapon, so the meta build changed.",
    ],
}
SCRAMBLED = {
    "scr_1": ["table river seven walking blue idea", "cloud paper forty gates under", "green stone lamp between four"],
    "scr_2": ["window coffee eleven doors slowly", "chair road ninety above cold", "glass field twenty inside warm"],
    "scr_3": ["street garden thirty walls quickly", "box light fifty behind soft", "cup floor sixty beyond loud"],
}


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

    # ---- encode anchors (local; ~90 short phrases) ----
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-large-en-v1.5", device="cpu")
    all_sets = {**ANCHORS, **SCRAMBLED}
    phrases, owners = [], []
    for cid, plist in all_sets.items():
        phrases.extend(plist)
        owners.extend([cid] * len(plist))
    avec = model.encode(phrases, normalize_embeddings=True, convert_to_numpy=True)
    centroid = mat.mean(axis=0)
    directions = {}
    for cid in all_sets:
        v = avec[np.array(owners) == cid].mean(axis=0) - centroid
        directions[cid] = v / np.linalg.norm(v)

    # ---- E9a: anchor scores, stability + MTMM ----
    early = emb_half.xs("early", level="half")
    late = emb_half.xs("late", level="half")
    common = early.index.intersection(late.index)
    e_mat, l_mat = early.loc[common].to_numpy(), late.loc[common].to_numpy()
    lex_e = lex_half.xs("early", level="half").reindex(common)
    lex_l = lex_half.xs("late", level="half").reindex(common)
    lex_full = (lex_e + lex_l) / 2
    rows = []
    for cid in list(ANCHORS) + list(SCRAMBLED):
        d = directions[cid]
        s_e, s_l = e_mat @ d, l_mat @ d
        stab = float(np.corrcoef(s_e, s_l)[0, 1])
        s_full = (s_e + s_l) / 2
        if cid in ANCHORS:
            conv = float(np.corrcoef(s_full, lex_full[cid])[0, 1])
            disc = max(abs(float(np.corrcoef(s_full, lex_full[o])[0, 1]))
                       for o in constructs if o != cid)
            rows.append({"construct": cid, "kind": "real", "stability_r": stab,
                         "convergent_r": conv, "max_discriminant_r": disc,
                         "mtmm_ok": bool(conv > disc)})
        else:
            best = max(abs(float(np.corrcoef(s_full, lex_full[o])[0, 1])) for o in constructs)
            rows.append({"construct": cid, "kind": "scrambled", "stability_r": stab,
                         "convergent_r": np.nan, "max_discriminant_r": best, "mtmm_ok": False})
    e9a = pd.DataFrame(rows)
    real = e9a.loc[e9a["kind"] == "real"]
    e9a_pass_n = int(((real["stability_r"] >= 0.30) & real["mtmm_ok"]).sum())

    # ---- E9b: neighbor reading ----
    e_norm = e_mat / np.linalg.norm(e_mat, axis=1, keepdims=True)
    sims = e_norm @ e_norm.T
    np.fill_diagonal(sims, -np.inf)
    nn_idx = np.argsort(-sims, axis=1)[:, :K_NEIGHBORS]
    lex_l_mat = lex_l[constructs].to_numpy(float)
    borrowed = lex_l_mat[nn_idx].mean(axis=1)
    rand_idx = rng.integers(0, len(common), size=(len(common), K_NEIGHBORS))
    borrowed_rand = lex_l_mat[rand_idx].mean(axis=1)
    b_rows = []
    ids = np.arange(len(common))
    for j, cid in enumerate(constructs):
        own = lex_l_mat[:, j]
        r_nn = float(np.corrcoef(borrowed[:, j], own)[0, 1])
        r_rand = float(np.corrcoef(borrowed_rand[:, j], own)[0, 1])
        boots = []
        for _ in range(400):
            t = rng.choice(ids, size=len(ids), replace=True)
            if own[t].std() > 1e-12 and borrowed[t, j].std() > 1e-12:
                boots.append(np.corrcoef(borrowed[t, j], own[t])[0, 1] -
                             (np.corrcoef(borrowed_rand[t, j], own[t])[0, 1] if borrowed_rand[t, j].std() > 1e-12 else 0))
        lo, hi = np.percentile(boots, [2.5, 97.5])
        b_rows.append({"construct": cid, "neighbor_read_r": r_nn, "random_neighbor_r": r_rand,
                       "delta": r_nn - r_rand, "delta_ci_lo": float(lo), "delta_ci_hi": float(hi),
                       "e9b_ok": bool((r_nn - r_rand) >= 0.15 and lo > 0)})
    e9b = pd.DataFrame(b_rows)
    e9b_pass_n = int(e9b["e9b_ok"].sum())

    criteria = {
        "n_users": int(len(common)),
        "E9a_pass_count": e9a_pass_n, "E9a_pass": bool(e9a_pass_n >= 8),
        "E9a_scrambled_max_stability": float(e9a.loc[e9a['kind'] == 'scrambled', 'stability_r'].max()),
        "E9b_pass_count": e9b_pass_n, "E9b_pass": bool(e9b_pass_n >= 8),
        "k_neighbors": K_NEIGHBORS, "model": "BAAI/bge-large-en-v1.5",
    }
    e9a.to_csv(OUT_DIR / "e9a_anchor_projection.csv", index=False)
    e9b.to_csv(OUT_DIR / "e9b_neighbor_reading.csv", index=False)
    (OUT_DIR / "e9_results.json").write_text(json.dumps(criteria, indent=2, default=float) + "\n")
    REPORT.write_text("# SUICA E9 Embedding Interpretive Channel\n\n## E9a anchor projection (stability + MTMM)\n\n"
                      + e9a.round(3).to_markdown(index=False)
                      + "\n\n## E9b neighbor reading (k=50, vs random-neighbor null)\n\n"
                      + e9b.round(3).to_markdown(index=False)
                      + "\n\n```json\n" + json.dumps(criteria, indent=2, default=float) + "\n```\n")
    print(e9a.round(3).to_string(index=False))
    print()
    print(e9b.round(3).to_string(index=False))
    print(json.dumps(criteria, indent=2, default=float))


if __name__ == "__main__":
    main()
