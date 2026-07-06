#!/usr/bin/env python
"""OP-22: blind-coding v2 item bank for the 15 OP-5 candidate constructs.

Design per Rulebook F5 + all audit lessons:
- Items drawn ONLY from B-half users (never used in feature fitting/selection).
- T1 label-identification task: 7-way forced choice (true label + 4 real
  foils + 2 distractors; chance = 1/7) + 0-3 salience rating.
- T2 intensity task: high-vs-low pairs (chance = 1/2).
- Clean exemplars: target z >= 97.5th pct AND margin over every other
  candidate >= 1.0 z; <= 1 item per user per construct; dedup; length bounds;
  personality-term masking (incl. MBTI type codes).
- The KEY (item -> construct) is written to a separate file that coders and
  the human coder must never see.
Human subsample: 8 items/construct = 120 (stratified from the 16).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_op5_construct_discovery_v3 import stable_fraction  # noqa: E402
from scripts.run_suica_op9_embedding_baseline_v3 import rederive_op5_scores, OP5_KEPT  # noqa: E402
from scripts.build_suica_independent_blind_validation_batch_v1 import mask_personality_terms  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
OUT_DIR = ROOT / "results" / "suica_op22_item_bank_v2"
SEED = 42
ITEMS_PER_CONSTRUCT = 16
HUMAN_PER_CONSTRUCT = 8
PAIRS_PER_CONSTRUCT = 6
Z_MIN_PCT = 97.5
MARGIN_Z = 1.0
MIN_WORDS, MAX_WORDS = 60, 130

LABELS = {
    "wcl_60": "Apostrophe-omitted contractions (writes dont / im / thats without apostrophes)",
    "wcl_03": "Positive enthusiasm vocabulary (love, great, awesome, definitely)",
    "wcl_36": "Family / personal-life narrative (family members, home life, personal relationships)",
    "wcl_11": "Technical / practical how-to vocabulary (using, fixing, versions, devices)",
    "wcl_45": "Epistemic argumentation (believe, true, fact, however, opinion; debating what is true)",
    "wcl_25": "Fiction / show / story discussion (characters, episodes, plots)",
    "wcl_02": "Competitive sports talk (teams, winning, seasons, fans)",
    "wcl_07": "Politics / government / news talk",
    "wcl_54": "Analytic-formal connective style (which, due to, likely, in this case)",
    "wcl_22": "Concrete scene narration (physical descriptions, places, events unfolding)",
    "wcl_13": "Negation-heavy argument style (not, don't, doesn't, why would)",
    "wcl_35": "Media consumption talk (videos, music, channels, favorites)",
    "wcl_15": "Casual interjection register (yeah, lol, gonna, kinda)",
    "wcl_23": "Profanity / intensity register (swearing, emphatic vulgarity)",
    "wcl_20": "Game-mechanics vocabulary (levels, damage, builds, hits)",
}
DISTRACTORS = {
    "dst_A": "Numerical/quantitative reasoning (calculations, statistics, measurements)",
    "dst_B": "Formal apology and politeness routines (thanking, apologizing, formal requests)",
    "dst_C": "Weather and season descriptions",
}


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.read_parquet(TIER_DIR / "op9_half_slices.parquet")
    b_mask = ~frame["user_id"].map(lambda u: stable_fraction("op5::" + u) < 0.5)
    rates = rederive_op5_scores(frame)
    z = (rates[OP5_KEPT] - rates[OP5_KEPT].mean()) / rates[OP5_KEPT].std()
    work = frame[["user_id", "slice_text"]].copy()
    work = pd.concat([work, z.add_suffix("__z")], axis=1)
    work = work.loc[b_mask.to_numpy()].reset_index(drop=True)
    words = work["slice_text"].str.split().str.len()
    work = work.loc[(words >= MIN_WORDS) & (words <= MAX_WORDS)]
    work = work.loc[~work["slice_text"].duplicated()]
    print(f"B-half candidate slices: {len(work)}")

    zcols = [f"{c}__z" for c in OP5_KEPT]
    zmat = work[zcols].to_numpy(float)
    items, lows = [], []
    used_users: dict[str, set] = {c: set() for c in OP5_KEPT}
    for ci, construct in enumerate(OP5_KEPT):
        target = zmat[:, ci]
        others = np.delete(zmat, ci, axis=1).max(axis=1)
        thresh = np.percentile(target, Z_MIN_PCT)
        elig = work.loc[(target >= thresh) & (target - others >= MARGIN_Z)].copy()
        elig["_t"] = target[(target >= thresh) & (target - others >= MARGIN_Z)]
        elig = elig.sort_values("_t", ascending=False)
        picked = []
        for _, row in elig.iterrows():
            if row["user_id"] in used_users[construct]:
                continue
            masked, n_masked = mask_personality_terms(row["slice_text"])
            picked.append({"construct": construct, "user_id": row["user_id"],
                           "text": masked, "n_masked": n_masked, "z": float(row["_t"])})
            used_users[construct].add(row["user_id"])
            if len(picked) >= ITEMS_PER_CONSTRUCT:
                break
        if len(picked) < ITEMS_PER_CONSTRUCT:
            print(f"WARNING: {construct} only {len(picked)} clean items")
        items.extend(picked)
        # low pool for T2
        low_elig = work.loc[target <= np.percentile(target, 10)].sample(
            n=min(200, int((target <= np.percentile(target, 10)).sum())), random_state=SEED + ci)
        low_rows = []
        seen_users = set()
        for _, row in low_elig.iterrows():
            if row["user_id"] in seen_users:
                continue
            masked, _ = mask_personality_terms(row["slice_text"])
            low_rows.append({"construct": construct, "text": masked, "user_id": row["user_id"]})
            seen_users.add(row["user_id"])
            if len(low_rows) >= PAIRS_PER_CONSTRUCT:
                break
        lows.extend(low_rows)

    # ---- T1 items with shuffled 7-option label sets ----
    real_ids = list(LABELS)
    t1_rows, key_rows = [], []
    for idx, item in enumerate(rng.permutation(np.array(items, dtype=object))):
        item_id = f"OP22_T1_{idx:04d}"
        foils = [c for c in real_ids if c != item["construct"]]
        opts = [item["construct"]] + list(rng.choice(foils, size=4, replace=False)) \
               + list(rng.choice(list(DISTRACTORS), size=2, replace=False))
        rng.shuffle(opts)
        letters = "ABCDEFG"
        row = {"item_id": item_id, "text": item["text"]}
        for L, opt in zip(letters, opts):
            row[f"opt_{L}"] = (LABELS | DISTRACTORS)[opt]
        t1_rows.append(row)
        key_rows.append({"item_id": item_id, "construct": item["construct"],
                         "correct_letter": letters[opts.index(item["construct"])],
                         "user_id": item["user_id"], "z": item["z"],
                         "options": json.dumps(opts)})
    t1 = pd.DataFrame(t1_rows)
    key = pd.DataFrame(key_rows)

    # ---- T2 pairs ----
    low_by_c: dict[str, list] = {}
    for row in lows:
        low_by_c.setdefault(row["construct"], []).append(row)
    pair_rows, pair_key = [], []
    high_by_c: dict[str, list] = {}
    for item in items:
        high_by_c.setdefault(item["construct"], []).append(item)
    pidx = 0
    for construct in OP5_KEPT:
        highs = high_by_c.get(construct, [])[:PAIRS_PER_CONSTRUCT]
        lows_c = low_by_c.get(construct, [])[:len(highs)]
        for h, l in zip(highs, lows_c):
            pair_id = f"OP22_T2_{pidx:04d}"
            pidx += 1
            if rng.random() < 0.5:
                a, b, ans = h["text"], l["text"], "A"
            else:
                a, b, ans = l["text"], h["text"], "B"
            pair_rows.append({"pair_id": pair_id, "construct_label": LABELS[construct],
                              "text_A": a, "text_B": b})
            pair_key.append({"pair_id": pair_id, "construct": construct, "higher": ans})
    pairs = pd.DataFrame(pair_rows)
    pkey = pd.DataFrame(pair_key)

    # ---- human subsample (stratified 8/construct) ----
    key_by_c = key.merge(t1, on="item_id")
    human_ids = (key_by_c.groupby("construct", group_keys=False)
                 .apply(lambda g: g.sample(n=min(HUMAN_PER_CONSTRUCT, len(g)), random_state=SEED))["item_id"])
    human = t1.loc[t1["item_id"].isin(set(human_ids))].sample(frac=1.0, random_state=SEED)
    human = human.assign(your_choice_A_to_G="", salience_0_to_3="", note="")

    t1.to_csv(OUT_DIR / "t1_items.csv", index=False)
    key.to_csv(OUT_DIR / "t1_KEY_do_not_show_coders.csv", index=False)
    pairs.to_csv(OUT_DIR / "t2_pairs.csv", index=False)
    pkey.to_csv(OUT_DIR / "t2_KEY_do_not_show_coders.csv", index=False)
    human.to_csv(OUT_DIR / "human_coding_sheet.csv", index=False)
    pd.DataFrame([{"label_id": k, "definition": v, "is_distractor": k.startswith("dst")}
                  for k, v in (LABELS | DISTRACTORS).items()]).to_csv(OUT_DIR / "label_definitions.csv", index=False)
    manifest = {"t1_items": len(t1), "t2_pairs": len(pairs), "human_items": len(human),
                "chance_t1": 1 / 7, "chance_t2": 0.5,
                "masked_item_rate": float((key["item_id"].isin(
                    [r["item_id"] for r, it in zip(key_rows, items) if it["n_masked"] > 0])).mean())}
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
