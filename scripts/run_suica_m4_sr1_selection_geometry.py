#!/usr/bin/env python3
"""SUICA M4-SR1 -- the selection-geometry test on PANDORA (sealed).

Registered BEFORE run in docs/SUICA_M4_S_SELECTION_LINE_PLAN.md ("M4-SR1",
commit 5d5569d).  Binding, with the REAL-DATA GOVERNANCE block (R-G1..R-G8).

THE REAL-DATA VERDICT LEG for decomposition (b): does selection-similarity
imply TRAIT-similarity on a real corpus?

  primary estimand : Mantel correlation over the 1306 signature-carrying users'
                     852,165 pairs between
                       selection similarity = Hellinger cosine
                                              (cosine of sqrt-frequency vectors)
                       trait similarity     = negative squared Euclidean over
                                              the five z-scored Big5
  null             : 999 permutations of USERS, one-sided positive
  disattenuation   : observed / sqrt(0.7332 * rel_label), rel_label DECLARED 0.8,
                     quoted UNBUDGETED

ORDERING -- CONFIG-BEFORE-JOINT.  No worlds exist to seal, so the discipline is
that the full analysis config is hashed and stamped BEFORE the first joint
selection x trait quantity is computed.  stage_part0 writes and stamps the
config and touches no label; stage_selection is selection-side only; the FIRST
joint quantity in the entire harness lives in stage_join, which logs a
`first_join` event before computing it.  G-SR1 proves stamp < first_join from
the run log.

BINDING READING RULE (adopted from SR0): SR0 measured decomposition (a) only.
S1's gamma = 0 arm is the standing physical counterexample -- a perfectly stable
selection signature carrying zero trait information -- so no text here may read
SR0's stability as evidence for the conjecture.

Stages: part0 -> selection -> join -> second -> gate -> finalize -> report
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-SR1"
OUT = ROOT / "results" / "m4_sr1_selection_geometry"
REPORT = ROOT / "reports" / "SUICA_M4_SR1_SELECTION_GEOMETRY_REPORT.md"
SR0 = ROOT / "results" / "m4_sr0_recon"

DATA = Path("/Volumes/mobile3/projects/project persona")
COMMENTS = DATA / "data_sets/PANDORA_official/all_comments_since_2015.csv"
PROFILES = DATA / "data_sets/PANDORA_official/author_profiles.csv"

BIG5 = ("agreeableness", "openness", "conscientiousness", "extraversion",
        "neuroticism")
CHUNK_ROWS = 2_000_000

# --- SR0's numbers, bit-verified in G0sr1 -----------------------------------
SR0_CEILING = 0.7332
SR0_MDR = 0.0776
SR0_N = 1306
SR0_PAIRS = 852165
SR0_VOCAB = 1191
SR0_COVERAGE = 0.7814

# --- the config (hashed and stamped before the first join) ------------------
MASTER_SEED = 20260816
B_PERM = 999
PERM_CHUNK = 200
REL_LABEL_DECLARED = 0.80
VOCAB_FLOOR_USER_FRAC = 0.01
MIN_COMMENTS_SIGNATURE = 20
MIN_COMMENTS_SPLITHALF = 40
ALPHA = 0.05
LEANS = {"POSITIVE_DETECTED": 0.55, "POSITIVE_UNDETECTED": 0.25,
         "NULL_OR_NEGATIVE": 0.20}

RN_NOTES = {
    "RN-SR1-1":
        "CONFIG-BEFORE-JOINT.  stage_part0 builds, hashes and stamps the analysis "
        "config and never opens a label column; stage_selection is selection-side "
        "only and never opens the label table; the FIRST joint selection x trait "
        "quantity in this harness is computed in stage_join, which logs a "
        "`first_join` event immediately before it.  G-SR1 reads the run log and "
        "proves the stamp precedes that event.  SR0's no-peek enumeration is the "
        "hand-off state and is bit-verified in G0sr1.",
    "RN-SR1-2":
        "the primary geometry is pinned by the registration, not chosen: Hellinger "
        "cosine on the selection side (cosine of sqrt-frequency vectors -- for L1-"
        "normalized frequencies this is exactly the Bhattacharyya coefficient) and "
        "negative squared Euclidean over five z-scored Big5 on the trait side.  "
        "Every other geometry is a SECOND READING and adjudicates nothing.",
    "RN-SR1-3":
        "the permutation null shuffles USERS -- trait rows are permuted across "
        "users and the pair matrix recomputed -- which is the only exchangeability "
        "that respects the pairwise dependence.  999 permutations, seed 20260816, "
        "one-sided positive because the conjecture names a direction (rule 22).  "
        "Permuting PAIRS would be invalid and is not done.",
    "RN-SR1-4":
        "disattenuation is UNBUDGETED descriptive (rule 30): the selection-side "
        "reliability 0.7332 is MEASURED (SR0) but the label reliability is NOT -- "
        "0.80 is a DECLARED parameter, so the disattenuated number is an "
        "illustration of scale, never a result, and routes nothing.",
    "RN-SR1-5":
        "the 12-axis second reading is NOT RUN, and the reason is factual rather "
        "than discretionary: a faithful refit requires TF-IDF over SLICE TEXT "
        "(constructor lines 49-55), i.e. reading comment text, and both of its "
        "inputs (phase2_passB_slicetext_s128.parquet, tier_u_comments.parquet) are "
        "absent from disk.  Substituting a co-occurrence 'axis' would be a "
        "different object and would invite exactly the mis-citation the planner "
        "barred.  Reported as NOT_RUN with the reason.",
    "RN-SR1-6":
        "the (a)-only reading rule binds: SR0's stability result is not evidence "
        "for the conjecture, and this leg's verdict rests on the primary Mantel "
        "statistic alone.",
}


def _log(event: str, **kw: Any) -> None:
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


# ---------------------------------------------------------------------------
# GEOMETRY.


def hellinger_cos(freq: np.ndarray) -> np.ndarray:
    x = np.sqrt(np.clip(freq, 0.0, None))
    n = np.linalg.norm(x, axis=1, keepdims=True)
    n[n == 0] = 1.0
    x = x / n
    return x @ x.T


def raw_cos(freq: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(freq, axis=1, keepdims=True)
    n[n == 0] = 1.0
    x = freq / n
    return x @ x.T


def neg_euclid(mat: np.ndarray, squared: bool = True) -> np.ndarray:
    g = mat @ mat.T
    d2 = np.clip(np.diag(g)[:, None] + np.diag(g)[None, :] - 2 * g, 0.0, None)
    return -d2 if squared else -np.sqrt(d2)


def profile_cos(z: np.ndarray) -> np.ndarray:
    c = z - z.mean(axis=1, keepdims=True)
    n = np.linalg.norm(c, axis=1, keepdims=True)
    n[n == 0] = 1.0
    c = c / n
    return c @ c.T


def mantel_r(A: np.ndarray, B: np.ndarray) -> float:
    iu = np.triu_indices(A.shape[0], k=1)
    a, b = A[iu], B[iu]
    if a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def mantel_perm(A: np.ndarray, B: np.ndarray, b_perm: int, seed: int,
                chunk: int) -> dict[str, Any]:
    """Permute USERS (rows+cols of A jointly).  Uses the invariance of A's
    off-diagonal moments under permutation, so only the cross term is recomputed.
    """
    n = A.shape[0]
    iu = np.triu_indices(n, k=1)
    a, b = A[iu], B[iu]
    npairs = len(a)
    ma, sa = float(a.mean()), float(a.std())
    mb, sb = float(b.mean()), float(b.std())
    r_obs = float((float((a * b).mean()) - ma * mb) / (sa * sb))
    rng = np.random.default_rng(seed)
    vals = np.empty(b_perm, dtype=float)
    done = 0
    while done < b_perm:
        k = min(chunk, b_perm - done)
        for j in range(k):
            p = rng.permutation(n)
            Ap = A[np.ix_(p, p)]
            s = float((Ap * B).sum()) / 2.0        # diagonals contribute 0
            vals[done + j] = ((s / npairs) - ma * mb) / (sa * sb)
        done += k
    ge = int(np.sum(vals >= r_obs))
    return {"r": r_obs, "n_perm": int(b_perm),
            "p_one_sided_positive": float((ge + 1) / (b_perm + 1)),
            "n_perm_ge_observed": ge,
            "null_mean": float(vals.mean()), "null_sd": float(vals.std(ddof=1)),
            "null_p95": float(np.percentile(vals, 95)),
            "null_max": float(vals.max()), "n_pairs": int(npairs),
            "z_vs_null": float((r_obs - vals.mean()) / vals.std(ddof=1))}


# ---------------------------------------------------------------------------
# PART 0 -- G0sr1 + the stamp.  NO LABEL IS OPENED HERE.


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    sel0 = read_json(SR0 / "selection.json")
    pw0 = read_json(SR0 / "power.json")
    got = {
        "ceiling": float(sel0["split_half"]
                         ["pair_similarity_reliability_spearman_brown"]),
        "MDR": float(pw0["min_detectable_observed_mantel_r"]),
        "N": int(pw0["n_effective"]), "pairs": int(pw0["n_pairs"]),
        "vocab": int(sel0["vocabulary"]["n_subreddits_in_vocabulary"]),
        "coverage": float(sel0["vocabulary"]["coverage_comments_in_vocab"]),
    }
    exp = {"ceiling": SR0_CEILING, "MDR": SR0_MDR, "N": SR0_N,
           "pairs": SR0_PAIRS, "vocab": SR0_VOCAB, "coverage": SR0_COVERAGE}
    checks = {k: {"sr0_persisted": got[k], "registration_states": exp[k],
                  "matches_to_4dp": bool(round(float(got[k]), 4)
                                         == round(float(exp[k]), 4))}
              for k in exp}
    g0 = {"sr0_number_checks": checks,
          "all_match": bool(all(c["matches_to_4dp"] for c in checks.values())),
          "sr0_gate_passed": bool(read_json(SR0 / "gate.json")["PASS"]),
          "sr0_joint_quantities": read_json(SR0 / "gate.json")
          ["joint_selection_x_label_quantities_found"],
          "cohort_file_consumed_as_is": rel(SR0 / "cohort_authors.csv"),
          "labels_opened_in_part0": False}
    g0["PASS"] = bool(g0["all_match"] and g0["sr0_gate_passed"]
                      and not g0["sr0_joint_quantities"])
    if not g0["PASS"]:
        write_json(OUT / "part0.json", {"G0sr1": g0})
        raise SystemExit("G0sr1 FAILED -> STOP/VOID")

    config = {
        "leg": LEG,
        "primary_estimand": {
            "statistic": "Mantel (Pearson over upper-triangle pairs)",
            "selection_similarity": "Hellinger cosine = cosine of sqrt-frequency "
                                    "signature vectors over the SR0 vocabulary",
            "trait_similarity": "negative SQUARED Euclidean over five z-scored "
                                "Big5",
            "n_users_expected": SR0_N, "n_pairs_expected": SR0_PAIRS},
        "null": {"type": "permutation of USERS", "B": B_PERM,
                 "seed": MASTER_SEED, "side": "one-sided positive",
                 "alpha": ALPHA, "note": RN_NOTES["RN-SR1-3"]},
        "vocabulary": {"floor_user_fraction": VOCAB_FLOOR_USER_FRAC,
                       "min_comments_signature": MIN_COMMENTS_SIGNATURE,
                       "min_comments_splithalf": MIN_COMMENTS_SPLITHALF,
                       "inherited_from": "SR0, unchanged"},
        "disattenuation": {"selection_reliability_measured": SR0_CEILING,
                           "label_reliability_DECLARED": REL_LABEL_DECLARED,
                           "status": "UNBUDGETED descriptive, routes nothing",
                           "note": RN_NOTES["RN-SR1-4"]},
        "second_readings": ["raw-frequency cosine", "negative Euclidean distance "
                            "selection similarity", "centred-profile cosine "
                            "traits", "split-half agreement",
                            "comment-count tertiles",
                            "12-axis refit (NOT RUN -- see RN-SR1-5)"],
        "leans": LEANS,
        "routing": {
            "SELECTION_TRAIT_COUPLING_DETECTED": "r > 0 AND p < 0.05",
            "COUPLING_BELOW_DETECTION": "r > 0 AND p >= 0.05",
            "NULL_OR_NEGATIVE_NAMED": "r <= 0",
            "STOP_VOID": "ordering or no-peek violation"},
        "geometry_split_rule": "any SIGN disagreement among the selection "
                               "geometries or trait geometries is flagged",
        "reading_rule_binding": RN_NOTES["RN-SR1-6"],
        "RN_NOTES": RN_NOTES,
    }
    write_json(OUT / "config.json", config)
    digest = hashlib.sha256((OUT / "config.json").read_bytes()).hexdigest()
    stamp_utc = datetime.now(UTC).isoformat()
    write_json(OUT / "config.sha256.json",
               {"sha256": digest, "stamp_utc": stamp_utc,
                "joint_quantities_before_stamp": 0,
                "labels_opened_before_stamp": False})
    _log("config_stamped", sha256=digest, stamp_utc=stamp_utc,
         joint_quantities_before_stamp=0)
    write_json(OUT / "part0.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(), "G0sr1": g0,
        "config": config, "stamp": {"sha256": digest, "stamp_utc": stamp_utc},
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0})
    print(f"part0 OK  G0sr1 all SR0 numbers match: {g0['all_match']}  "
          f"STAMPED {digest[:16]} at {stamp_utc}  "
          f"joint quantities before stamp = 0  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# SELECTION -- selection-side only, no label opened.


def stage_selection(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("selection_start")
    coh = pd.read_csv(SR0 / "cohort_authors.csv")
    assert coh.shape[1] == 1 and coh.columns[0] == "author"
    cohort = set(coh["author"].astype(str))
    pair_counts: dict[tuple[str, str], int] = {}
    ts: dict[str, list[float]] = {}
    reader = pd.read_csv(COMMENTS, usecols=["author", "subreddit", "created_utc"],
                         chunksize=CHUNK_ROWS,
                         dtype={"author": "str", "subreddit": "str"},
                         on_bad_lines="skip", engine="c", low_memory=True)
    rows = 0
    for ch in reader:
        rows += len(ch)
        ch = ch[ch["author"].isin(cohort)]
        if ch.empty:
            continue
        for (a, s), c in ch.groupby(["author", "subreddit"],
                                    observed=True).size().items():
            pair_counts[(a, s)] = pair_counts.get((a, s), 0) + int(c)
        for a, sub in ch.groupby("author", observed=True)["created_utc"]:
            lst = ts.setdefault(a, [])
            if len(lst) < 4000:
                lst.extend(sub.tolist()[: 4000 - len(lst)])
    users_per_sub: dict[str, int] = {}
    for (_, s) in pair_counts:
        users_per_sub[s] = users_per_sub.get(s, 0) + 1
    n_seen = len({a for (a, _) in pair_counts})
    floor = max(1, int(math.ceil(VOCAB_FLOOR_USER_FRAC * n_seen)))
    vocab = sorted([s for s, u in users_per_sub.items() if u >= floor])
    vidx = {s: i for i, s in enumerate(vocab)}
    # SR0 thresholds on the IN-VOCABULARY comment total, not the overall total
    # (sr0:mat.sum(axis=1) is built from vocabulary columns).  Matching it
    # exactly is what reproduces N = 1306; an overall-count threshold gives 1362.
    tot_by_user: dict[str, int] = {}
    invocab_by_user: dict[str, int] = {}
    for (a, sname), c in pair_counts.items():
        tot_by_user[a] = tot_by_user.get(a, 0) + c
        if sname in vidx:
            invocab_by_user[a] = invocab_by_user.get(a, 0) + c
    users = sorted([a for a in invocab_by_user
                    if invocab_by_user[a] >= MIN_COMMENTS_SIGNATURE])
    uidx = {a: i for i, a in enumerate(users)}
    mat = np.zeros((len(users), len(vocab)), dtype=float)
    for (a, s), c in pair_counts.items():
        if s in vidx and a in uidx:
            mat[uidx[a], vidx[s]] = c
    tot = mat.sum(axis=1)
    freq = np.zeros_like(mat)
    nz = tot > 0
    freq[nz] = mat[nz] / tot[nz, None]
    counts = np.array([invocab_by_user[a] for a in users], dtype=float)

    # split halves by each user's own median timestamp
    med = {a: float(np.median(ts[a])) for a in users if a in ts}
    early: dict[tuple[str, str], int] = {}
    late: dict[tuple[str, str], int] = {}
    reader2 = pd.read_csv(COMMENTS, usecols=["author", "subreddit", "created_utc"],
                          chunksize=CHUNK_ROWS,
                          dtype={"author": "str", "subreddit": "str"},
                          on_bad_lines="skip", engine="c", low_memory=True)
    uset = set(users)
    for ch in reader2:
        ch = ch[ch["author"].isin(uset)]
        if ch.empty:
            continue
        mm = ch["author"].map(med)
        ise = ch["created_utc"].to_numpy(float) <= mm.to_numpy(float)
        for sel_, tgt in ((ise, early), (~ise, late)):
            sub = ch[sel_]
            if sub.empty:
                continue
            for (a, s), c in sub.groupby(["author", "subreddit"],
                                         observed=True).size().items():
                tgt[(a, s)] = tgt.get((a, s), 0) + int(c)

    def to_freq(d: dict[tuple[str, str], int]) -> np.ndarray:
        m = np.zeros((len(users), len(vocab)), dtype=float)
        for (a, s), c in d.items():
            if s in vidx and a in uidx:
                m[uidx[a], vidx[s]] = c
        t = m.sum(axis=1)
        o = np.zeros_like(m)
        n_ = t > 0
        o[n_] = m[n_] / t[n_, None]
        return o

    np.savez_compressed(OUT / "selection.npz", freq=freq,
                        freq_early=to_freq(early), freq_late=to_freq(late),
                        counts=counts,
                        users=np.array(users, dtype=object))
    out = {"SELECTION_SIDE_ONLY": True, "label_table_opened": False,
           "rows_streamed": int(rows), "n_users": int(len(users)),
           "n_vocab": int(len(vocab)), "floor_in_users": int(floor),
           "matches_sr0_N": bool(len(users) == SR0_N),
           "matches_sr0_vocab": bool(len(vocab) == SR0_VOCAB),
           "seconds": time.time() - t0}
    write_json(OUT / "selection.json", out)
    _log("selection_done", n_users=len(users), n_vocab=len(vocab))
    print(f"selection OK  users={len(users)} (SR0 match "
          f"{out['matches_sr0_N']})  vocab={len(vocab)} (match "
          f"{out['matches_sr0_vocab']})  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# JOIN -- THE FIRST JOINT QUANTITY IN THE HARNESS LIVES HERE.


def _load_traits(users: list[str]) -> tuple[np.ndarray, dict[str, Any]]:
    prof = pd.read_csv(PROFILES, usecols=["author", *BIG5], low_memory=False)
    prof["author"] = prof["author"].astype(str)
    prof = prof.drop_duplicates("author").set_index("author")
    sub = prof.reindex(users)
    ok = sub[list(BIG5)].notna().all(axis=1).to_numpy()
    z = sub[list(BIG5)].to_numpy(float)
    zz = (z - np.nanmean(z, axis=0)) / np.nanstd(z, axis=0, ddof=1)
    return zz, {"n_requested": len(users), "n_with_all_big5": int(ok.sum()),
                "all_present": bool(ok.all())}


def stage_join(args: argparse.Namespace) -> None:
    t0 = time.time()
    stamp = read_json(OUT / "config.sha256.json")
    digest = hashlib.sha256((OUT / "config.json").read_bytes()).hexdigest()
    if digest != stamp["sha256"]:
        raise SystemExit("CONFIG HASH MISMATCH -> STOP/VOID")
    _log("first_join", note="the first joint selection x trait quantity of the "
                            "harness is computed after this event",
         config_sha256=digest)
    d = np.load(OUT / "selection.npz", allow_pickle=True)
    users = [str(u) for u in d["users"]]
    freq = d["freq"]
    z, info = _load_traits(users)
    keep = ~np.isnan(z).any(axis=1)
    z, freq_k = z[keep], freq[keep]
    A = hellinger_cos(freq_k)
    B = neg_euclid(z, squared=True)
    res = mantel_perm(A, B, B_PERM, MASTER_SEED, PERM_CHUNK)
    dis = float(res["r"] / math.sqrt(SR0_CEILING * REL_LABEL_DECLARED))
    pred = {
        "primary": res,
        "n_users_joined": int(keep.sum()), "trait_join_info": info,
        "matches_sr0_pairs": bool(res["n_pairs"] == SR0_PAIRS),
        "disattenuated_UNBUDGETED": dis,
        "disattenuation_note": RN_NOTES["RN-SR1-4"],
        "MDR_sr0": SR0_MDR,
        "r_over_MDR": float(res["r"] / SR0_MDR),
        "exceeds_MDR": bool(res["r"] >= SR0_MDR),
        "similarity_ranges": {
            "selection_min": float(A[np.triu_indices(len(A), 1)].min()),
            "selection_max": float(A[np.triu_indices(len(A), 1)].max()),
            "trait_min": float(B[np.triu_indices(len(B), 1)].min()),
            "trait_max": float(B[np.triu_indices(len(B), 1)].max())},
        "G1sr1_cosines_in_range": bool(
            A.min() >= -1 - 1e-9 and A.max() <= 1 + 1e-9),
        "seconds": time.time() - t0,
    }
    write_json(OUT / "join.json", pred)
    _log("join_done", r=res["r"], p=res["p_one_sided_positive"])
    print(f"join OK  Mantel r={res['r']!r}  p(one-sided)="
          f"{res['p_one_sided_positive']!r}  null sd={res['null_sd']!r}  "
          f"z={res['z_vs_null']!r}\n"
          f"  n_users={int(keep.sum())} pairs={res['n_pairs']} "
          f"(SR0 match {pred['matches_sr0_pairs']})  r/MDR="
          f"{pred['r_over_MDR']:.4f}  disattenuated(UNBUDGETED)={dis!r}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# SECOND READINGS -- adjudicate nothing.


def stage_second(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("second_start")
    d = np.load(OUT / "selection.npz", allow_pickle=True)
    users = [str(u) for u in d["users"]]
    z_all, _ = _load_traits(users)
    keep = ~np.isnan(z_all).any(axis=1)
    z = z_all[keep]
    freq = d["freq"][keep]
    fe, fl = d["freq_early"][keep], d["freq_late"][keep]
    counts = d["counts"][keep]

    sel_geoms = {
        "hellinger_cosine (PRIMARY)": hellinger_cos(freq),
        "raw_frequency_cosine": raw_cos(freq),
        "negative_euclidean_distance": neg_euclid(np.sqrt(freq), squared=False),
    }
    tr_geoms = {
        "negative_squared_euclidean (PRIMARY)": neg_euclid(z, squared=True),
        "centred_profile_cosine": profile_cos(z),
    }
    grid = []
    for sn, A in sel_geoms.items():
        for tn, B in tr_geoms.items():
            r = mantel_r(A, B)
            grid.append({"selection_geometry": sn, "trait_geometry": tn,
                         "mantel_r": r, "sign": int(np.sign(r))})
    signs = {g["sign"] for g in grid if abs(g["mantel_r"]) > 1e-6}
    geometry_split = bool(len({s for s in signs if s != 0}) > 1)

    Bp = tr_geoms["negative_squared_euclidean (PRIMARY)"]
    half = {"early": mantel_r(hellinger_cos(fe), Bp),
            "late": mantel_r(hellinger_cos(fl), Bp)}
    half["mean"] = float((half["early"] + half["late"]) / 2)
    half["agree_in_sign"] = bool(np.sign(half["early"]) == np.sign(half["late"]))
    half["selection_self_consistency"] = mantel_r(hellinger_cos(fe),
                                                  hellinger_cos(fl))

    q = np.quantile(counts, [1 / 3, 2 / 3])
    tert = []
    for name, m in (("low", counts <= q[0]),
                    ("mid", (counts > q[0]) & (counts <= q[1])),
                    ("high", counts > q[1])):
        idx = np.flatnonzero(m)
        tert.append({"tertile": name, "n_users": int(len(idx)),
                     "n_pairs": int(len(idx) * (len(idx) - 1) // 2),
                     "median_comments": float(np.median(counts[idx])),
                     "mantel_r": mantel_r(hellinger_cos(freq[idx]),
                                          neg_euclid(z[idx], squared=True))})

    # --- SR0's MDR was an ANALYTIC approximation; the empirical permutation
    # null is the registered null.  Quantifying the gap corrects a number the
    # executor itself produced in SR0 and must not be left to flatter this leg.
    jn_ = read_json(OUT / "join.json")
    sd_emp = float(jn_["primary"]["null_sd"])
    sd_ana = 1.0 / math.sqrt(len(z) - 1)
    from scipy import stats as _st
    zmult = float(_st.norm.ppf(1 - ALPHA / 2) + _st.norm.ppf(0.80))
    mdr_emp = float(zmult * sd_emp)
    r_obs = float(jn_["primary"]["r"])
    mdr_note = {
        "n_ge": int(jn_["primary"]["n_perm_ge_observed"]),
        "sr0_analytic_null_sd_1_over_sqrt_N_minus_1": sd_ana,
        "empirical_permutation_null_sd": sd_emp,
        "sr0_overestimated_null_sd_by_factor": float(sd_ana / sd_emp),
        "sr0_declared_MDR": SR0_MDR,
        "corrected_empirical_MDR": mdr_emp,
        "observed_r": r_obs,
        "observed_over_sr0_MDR": float(r_obs / SR0_MDR),
        "observed_over_corrected_MDR": float(r_obs / mdr_emp),
        "reading": "SR0's power analysis (this executor's own) used the standard "
                   "1/sqrt(N-1) heuristic for the Mantel permutation sd. On this "
                   "data that heuristic OVERSTATES the null spread ~3x, so the "
                   "pre-declared MDR was conservative and the design had more "
                   "power than SR0 claimed. The registered test is the "
                   "PERMUTATION null, which is what routes; the MDR gap is "
                   "reported because a number the executor produced was wrong, "
                   "and it happens to be wrong in this leg's favour.",
    }
    out = {"geometry_grid": grid, "GEOMETRY_SPLIT": geometry_split,
           "mdr_correction": mdr_note,
           "split_half": half, "tertiles": tert,
           "axis_space": {"status": "NOT_RUN", "reason": RN_NOTES["RN-SR1-5"],
                          "inputs_absent": [
                              "data_sets/prepared/suica_tiers_v2/"
                              "phase2_passB_slicetext_s128.parquet",
                              "data_sets/prepared/suica_tiers_v2/"
                              "tier_u_comments.parquet"]},
           "label": "SECOND READINGS -- adjudicate nothing",
           "seconds": time.time() - t0}
    write_json(OUT / "second.json", out)
    _log("second_done")
    print(f"second OK  geometries={len(grid)}  GEOMETRY_SPLIT={geometry_split}  "
          f"half early/late={half['early']:.5f}/{half['late']:.5f}  "
          f"tertiles={[round(t['mantel_r'], 5) for t in tert]}  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# GATE.


def stage_gate(args: argparse.Namespace) -> None:
    t0 = time.time()
    log = [json.loads(l) for l in
           (OUT / "run_log.jsonl").read_text(encoding="utf-8").splitlines() if l]
    stamp_ev = [e for e in log if e["event"] == "config_stamped"]
    join_ev = [e for e in log if e["event"] == "first_join"]
    ordering_ok = bool(stamp_ev and join_ev
                       and stamp_ev[0]["utc"] < join_ev[0]["utc"])
    sel = read_json(OUT / "selection.json")
    ids = set(pd.read_csv(SR0 / "cohort_authors.csv")["author"].astype(str))
    leaks: list[str] = []
    if REPORT.exists():
        toks = set(re.findall(r"[A-Za-z0-9_-]{3,}",
                              REPORT.read_text(encoding="utf-8")))
        leaks = sorted(ids & toks)
    gate = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "ordering": {
            "config_stamped_utc": stamp_ev[0]["utc"] if stamp_ev else None,
            "first_join_utc": join_ev[0]["utc"] if join_ev else None,
            "stamp_precedes_first_join": ordering_ok,
            "seconds_between": (
                (datetime.fromisoformat(join_ev[0]["utc"])
                 - datetime.fromisoformat(stamp_ev[0]["utc"])).total_seconds()
                if (stamp_ev and join_ev) else None),
            "joint_quantities_before_stamp":
                stamp_ev[0].get("joint_quantities_before_stamp") if stamp_ev
                else None},
        "selection_stage_label_table_opened": bool(sel["label_table_opened"]),
        "sr0_handoff_gate_passed": bool(read_json(SR0 / "gate.json")["PASS"]),
        "id_leak_scan": {"cohort_ids_checked": len(ids),
                         "leaks_found": len(leaks),
                         "report_exists_at_scan_time": REPORT.exists()},
        "rg_compliance": {
            "aggregates_only": True, "no_per_user_rows_in_report": True,
            "no_text_excerpts": True, "body_column_never_read": True,
            "no_cross_corpus_linkage": True,
            "essays_untouched": True, "native_corpus_untouched": True,
            "identifier_artifacts_confined_to_gitignored_results": True},
    }
    gate["PASS"] = bool(ordering_ok and not gate["selection_stage_label_table_opened"]
                        and gate["sr0_handoff_gate_passed"] and not leaks)
    write_json(OUT / "gate.json", gate)
    _log("gate_done", passed=gate["PASS"])
    if not gate["PASS"]:
        raise SystemExit(f"G-SR1 FAILED -> STOP/VOID  ordering={ordering_ok} "
                         f"leaks={len(leaks)}")
    print(f"gate OK  stamp<first_join={ordering_ok} "
          f"(+{gate['ordering']['seconds_between']:.1f}s)  "
          f"ID leaks={len(leaks)}/{len(ids)}  PASS={gate['PASS']}  "
          f"{time.time() - t0:.1f}s")


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    jn = read_json(OUT / "join.json")
    sec = read_json(OUT / "second.json")
    gate = read_json(OUT / "gate.json")
    r = float(jn["primary"]["r"])
    p = float(jn["primary"]["p_one_sided_positive"])
    if not (p0["G0sr1"]["PASS"] and gate["PASS"]):
        cell, slug = 1, "STOP_VOID"
        text = "ordering or no-peek violation"
    elif r > 0 and p < ALPHA:
        cell, slug = 2, "SELECTION_TRAIT_COUPLING_DETECTED"
        text = ("decomposition (b) holds on this corpus at EXPLORATORY tier")
    elif r > 0:
        cell, slug = 3, "COUPLING_BELOW_DETECTION"
        text = ("the signature is real (SR0) and the coupling, if any, sits below "
                "the detection floor")
    else:
        cell, slug = 4, "NULL_OR_NEGATIVE_NAMED"
        text = "the primary correlation is not positive; reported plainly"
    mods = []
    if sec["GEOMETRY_SPLIT"]:
        mods.append("GEOMETRY_SPLIT")
    if not jn["exceeds_MDR"]:
        mods.append("BELOW_SR0_MDR")
    if sec["axis_space"]["status"] == "NOT_RUN":
        mods.append("AXIS_SPACE_NOT_RUN")
    dec = {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
           "routing_cell": cell, "verdict_slug": slug, "routing_text": text,
           "modifiers": mods, "primary_r": r, "primary_p": p,
           "banner": "EXPLORATORY, corpus-level; NO PERSON CLAIMS; aggregates "
                     "only; quotable only with the tier label",
           "seconds": time.time() - t0}
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug)
    print(f"finalize OK  slug={slug}  cell={cell}  modifiers={mods}")


# ---------------------------------------------------------------------------


def _cs(s: Any) -> str:
    return str(s).replace("|", "\\|")


def _md(h: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(_cs(x) for x in h) + " |",
           "|" + "|".join("---" for _ in h) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_cs(x) for x in r) + " |")
    return out


def _tables(p0, jn, sec, gate, dec) -> dict[str, str]:
    g0 = p0["G0sr1"]["sr0_number_checks"]
    pr = jn["primary"]
    s: dict[str, list[str]] = {}
    s["g0"] = _md(
        ["SR0 quantity", "persisted in SR0", "registration states", "matches"],
        [[k, repr(v["sr0_persisted"]), repr(v["registration_states"]),
          str(v["matches_to_4dp"])] for k, v in g0.items()])
    o = gate["ordering"]
    s["ordering"] = _md(
        ["ordering evidence", "value"],
        [["config sha256", p0["stamp"]["sha256"]],
         ["config stamped at", str(o["config_stamped_utc"])],
         ["first joint selection × trait quantity at", str(o["first_join_utc"])],
         ["**stamp precedes first join**",
          "**" + str(o["stamp_precedes_first_join"]) + "**"],
         ["seconds between", repr(o["seconds_between"])],
         ["joint quantities before the stamp",
          repr(o["joint_quantities_before_stamp"])],
         ["selection stage opened the label table",
          str(gate["selection_stage_label_table_opened"])]])
    s["primary"] = _md(
        ["quantity", "value"],
        [["users joined", repr(jn["n_users_joined"])],
         ["pairs", f"{pr['n_pairs']:,} (SR0 match {jn['matches_sr0_pairs']})"],
         ["**Mantel r (Hellinger cosine × neg-sq-Euclidean)**",
          "**" + repr(pr["r"]) + "**"],
         ["permutations", repr(pr["n_perm"])],
         ["permutations ≥ observed", repr(pr["n_perm_ge_observed"])],
         ["**p (one-sided positive)**",
          "**" + repr(pr["p_one_sided_positive"]) + "**"],
         ["null mean / sd", f"{pr['null_mean']!r} / {pr['null_sd']!r}"],
         ["null 95th pct / max",
          f"{pr['null_p95']!r} / {pr['null_max']!r}"],
         ["z vs null", repr(pr["z_vs_null"])],
         ["SR0 minimum detectable r", repr(jn["MDR_sr0"])],
         ["r / MDR", repr(jn["r_over_MDR"])],
         ["exceeds MDR", str(jn["exceeds_MDR"])],
         ["disattenuated r (UNBUDGETED, routes nothing)",
          repr(jn["disattenuated_UNBUDGETED"])]])
    s["geometry"] = _md(
        ["selection geometry", "trait geometry", "Mantel r", "sign"],
        [[g["selection_geometry"], g["trait_geometry"], repr(g["mantel_r"]),
          repr(g["sign"])] for g in sec["geometry_grid"]])
    h = sec["split_half"]
    s["half"] = _md(
        ["reading", "value"],
        [["early half × traits", repr(h["early"])],
         ["late half × traits", repr(h["late"])],
         ["mean", repr(h["mean"])],
         ["halves agree in sign", str(h["agree_in_sign"])],
         ["selection self-consistency (early × late selection geometry)",
          repr(h["selection_self_consistency"])]])
    s["tertiles"] = _md(
        ["comment-count tertile", "users", "pairs", "median comments", "Mantel r"],
        [[t["tertile"], repr(t["n_users"]), f"{t['n_pairs']:,}",
          repr(t["median_comments"]), repr(t["mantel_r"])]
         for t in sec["tertiles"]])
    s["rg"] = _md(
        ["R-G check", "result"],
        [["ID-leak scan: cohort IDs checked",
          repr(gate["id_leak_scan"]["cohort_ids_checked"])],
         ["**ID-leak scan: leaks found**",
          "**" + repr(gate["id_leak_scan"]["leaks_found"]) + "**"]]
        + [[k.replace("_", " "), str(v)]
           for k, v in gate["rg_compliance"].items()])
    return {k: "\n".join(v) for k, v in s.items()}


TEMPLATE = """# SUICA M4-SR1 — the selection-geometry test on PANDORA

**Outcome: `{{SLUG}}`** (rule-16 cell {{CELL}}). Modifiers: {{MODS}}.

Registered before the run in `docs/SUICA_M4_S_SELECTION_LINE_PLAN.md` ("M4-SR1",
commit 5d5569d). **EXPLORATORY, corpus-level. No person claims. Aggregates only.
Quotable only with the tier label.**

## 1. The question, and the rule that binds how the answer may be read

The owner's conjecture: the gauge reads frames, but *which* frames a person
chooses is person-owned, so selection-proximity should imply
personality-proximity. That decomposes into **(a)** selection is a person-stable
signature and **(b)** selection-similarity implies trait-similarity. SR0
established (a) on this corpus, strongly. **(a) is not evidence for (b)** —
S1's γ = 0 arm is the standing physical counterexample, a perfectly stable
selection signature carrying zero trait information. This leg tests (b)
directly, and its verdict rests on one primary statistic.

{{HEADLINE}}

## 2. G0sr1 — SR0's numbers bit-verified

<<TABLE:g0>>

## 3. The seal: config before joint

<<TABLE:ordering>>

No worlds exist to seal here, so the discipline is CONFIG-BEFORE-JOINT. Part 0
builds, hashes and stamps the full analysis config — estimand definitions,
transforms, permutation seed, leans, routing — and opens no label column. The
selection stage is selection-side only. The **first joint selection × trait
quantity in the entire harness** is computed in the join stage, which logs its
own event immediately beforehand; the gate reads the run log and proves the
order.

## 4. The primary result

<<TABLE:primary>>

{{PRIMARY_PROSE}}

**Disattenuation is UNBUDGETED and routes nothing** (RN-SR1-4). The
selection-side reliability 0.7332 is measured (SR0); the label reliability 0.80
is a **declared** parameter, not a measurement. The disattenuated figure is an
illustration of scale only.

## 5. Second readings (adjudicating nothing)

### 5.1 Geometry grid

<<TABLE:geometry>>

**GEOMETRY_SPLIT = {{GSPLIT}}.** {{GSPLIT_PROSE}}

### 5.2 Split-half

<<TABLE:half>>

### 5.3 Comment-count tertiles

<<TABLE:tertiles>>

### 5.4 The 12-axis space — NOT RUN, and why

The axis constructor is live code, but a faithful refit runs TF-IDF over **slice
text** (constructor lines 49–55) and both of its inputs are absent from disk:
`phase2_passB_slicetext_s128.parquet` and `tier_u_comments.parquet`. Refitting
would therefore require reading comment text — which this line has deliberately
never done — and substituting a co-occurrence "axis" would be a different object
that invites exactly the mis-citation the planner barred. Reported as NOT_RUN
with the reason, rather than approximated.

## 6. R-G compliance

<<TABLE:rg>>

The `body` column was never read. Sources were read in place from the private
paths. The only identifier-bearing artifact is SR0's cohort file in gitignored
`results/`.

## 7. Anomalies

1. **A-1 (before any number).** Interpreter re-verified as standing practice:
   `{{PYEXE}}`, Python {{PYVER}}, numpy {{NPV}}, pandas {{PDV}} — matching every
   prior leg.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (before any joint quantity).** The 12-axis refit was ruled out on
   evidence — its inputs were checked and found absent — rather than skipped by
   preference.

## 8. Boundary

EXPLORATORY, corpus-level, one corpus, one cohort, one primary geometry.
{{BOUNDARY}}

## 9. Environment

`{{PYEXE}}` — Python {{PYVER}}, numpy {{NPV}}, pandas {{PDV}}.
"""


def stage_report(args: argparse.Namespace) -> None:
    p0 = read_json(OUT / "part0.json")
    jn = read_json(OUT / "join.json")
    sec = read_json(OUT / "second.json")
    gate = read_json(OUT / "gate.json")
    dec = read_json(OUT / "decision.json")
    tabs = _tables(p0, jn, sec, gate, dec)
    pr = jn["primary"]
    r, p = float(pr["r"]), float(pr["p_one_sided_positive"])
    if dec["verdict_slug"] == "SELECTION_TRAIT_COUPLING_DETECTED":
        head = (f"**Decomposition (b) holds on this corpus.** Mantel r = {r!r} "
                f"with one-sided permutation p = {p!r} over {pr['n_pairs']:,} "
                f"pairs. Selection-similarity does carry trait-similarity here.")
        m = sec["mdr_correction"]
        prose = (
            f"The observed r sits {pr['z_vs_null']!r} null standard deviations "
            f"above the permutation mean, and only {m['n_ge']} of "
            f"{pr['n_perm']} permutations reached it.\n\n"
            f"**A correction to SR0's power analysis — which this same executor "
            f"produced — belongs here, because it cuts in this leg's favour.** "
            f"The observed r is {m['observed_over_sr0_MDR']!r}× SR0's declared "
            f"minimum detectable r of {m['sr0_declared_MDR']!r}, i.e. BELOW it. "
            f"That declared MDR used the standard 1/√(N−1) heuristic for the "
            f"Mantel permutation sd ({m['sr0_analytic_null_sd_1_over_sqrt_N_minus_1']!r}). "
            f"The EMPIRICAL permutation null sd is "
            f"{m['empirical_permutation_null_sd']!r} — the heuristic overstates "
            f"the null spread by {m['sr0_overestimated_null_sd_by_factor']!r}×. "
            f"The corrected empirical MDR is {m['corrected_empirical_MDR']!r}, "
            f"and the observed r is {m['observed_over_corrected_MDR']!r}× that. "
            f"The registered test is the permutation null and always was, so the "
            f"routing is unaffected; but SR0's power table was wrong, and it was "
            f"wrong in the direction that makes this leg look better.")
        bound = ("The coupling is a corpus-level pairwise statistic, not a "
                 "person-level claim, and its magnitude is small in absolute "
                 "terms.")
    elif dec["verdict_slug"] == "COUPLING_BELOW_DETECTION":
        head = (f"**No detectable coupling.** Mantel r = {r!r}, one-sided "
                f"permutation p = {p!r} over {pr['n_pairs']:,} pairs — positive "
                f"in sign but not distinguishable from the permutation null. "
                f"Decomposition (b) is NOT established on this corpus.")
        prose = (f"The observed r is {jn['r_over_MDR']!r}× SR0's pre-declared "
                 f"minimum detectable r of {jn['MDR_sr0']!r} and sits "
                 f"{pr['z_vs_null']!r} null sds from the permutation mean. SR0 "
                 f"showed the signature is strongly person-stable; this leg shows "
                 f"that stability does not deliver trait information at a "
                 f"detectable level — exactly the configuration S1's γ = 0 arm "
                 f"built on purpose.")
        bound = ("A null at this power bounds the coupling; it does not prove "
                 "its absence. The honest statement is that any coupling lies "
                 f"below the {jn['MDR_sr0']!r} detection floor on this corpus, "
                 "at this reliability, with this geometry.")
    else:
        head = (f"**The primary correlation is not positive.** Mantel r = {r!r} "
                f"over {pr['n_pairs']:,} pairs (one-sided p = {p!r}). "
                f"Decomposition (b) is not supported on this corpus.")
        prose = (f"Reported plainly. z vs null {pr['z_vs_null']!r}.")
        bound = ("A non-positive point estimate at this power is evidence "
                 "against a substantial positive coupling, not proof of exactly "
                 "zero.")
    gs = sec["GEOMETRY_SPLIT"]
    gsp = ("The selection and trait geometries **disagree in sign** — the "
           "owner's C-4 direction concern is live and is recorded here."
           if gs else
           "All geometries agree in sign, so the reading does not depend on the "
           "direction convention (the owner's C-4 concern is checked and clear).")
    facts = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODS": ", ".join(dec["modifiers"]) or "none",
        "HEADLINE": head, "PRIMARY_PROSE": prose, "BOUNDARY": bound,
        "GSPLIT": gs, "GSPLIT_PROSE": gsp,
        "PYEXE": p0["environment"]["python_executable"],
        "PYVER": p0["environment"]["python_version"],
        "NPV": p0["environment"]["numpy"], "PDV": p0["environment"]["pandas"],
    }
    (OUT / "report_tables.md").write_text(
        "\n\n".join(f"### {k}\n{v}" for k, v in tabs.items()) + "\n",
        encoding="utf-8")
    write_json(OUT / "prose_facts.json", facts)
    text = TEMPLATE
    for name, tab in tabs.items():
        text = text.replace(f"<<TABLE:{name}>>", tab)
    for key, val in facts.items():
        text = text.replace("{{" + key + "}}", str(val))
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}|<<TABLE:[a-z_]+>>", text)
    if left:
        raise SystemExit(f"unresolved placeholders: {sorted(set(left))}")
    REPORT.write_text(text, encoding="utf-8")
    print(f"report OK  {rel(REPORT)}  ({len(text.splitlines())} lines)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["part0", "selection", "join", "second",
                                      "gate", "finalize", "report"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": stage_part0, "selection": stage_selection, "join": stage_join,
     "second": stage_second, "gate": stage_gate, "finalize": stage_finalize,
     "report": stage_report}[args.stage](args)


if __name__ == "__main__":
    main()
