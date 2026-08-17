#!/usr/bin/env python3
"""SUICA M4-SR2 -- the trait-coupling budget (which component carries r = 0.049?).

Registered BEFORE run in docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md
("M4-SR2", commit a34f12c).  Binding.

THIS IS THE LINE'S EXTERNAL-CONNECTION LEG AND THE ONLY ONE THAT OPENS LABELS.
Every technical object it uses -- T1's tree, T2/T3's embeddings and
observability vectors, the budget itself -- was frozen LABEL-FREE in T1-T3.
Big5 values are read for the first time inside `stage_joint`, after the
analysis config has been hashed and stamped, and the run log carries the
proof (`config_stamped` strictly precedes `first_join`, and `first_join`
strictly precedes the first read of the profiles file).

SR1 detected a selection x trait Mantel coupling of r = 0.048987613136188025.
SR2 asks WHICH COMPONENT CARRIES IT, and runs the audit SR1 never ran: does
that coupling survive conditioning on observability?

  R_obs   the frozen late-side observability vector  (the confound check)
  R_tree  the frozen depth-weighted path code
  R_emb   the frozen per-fold taste centroid
  R_flat  SR1's own Hellinger cosine                 (the anchor)

The SR1 harness, the T2 harness and the T1 core are imported BY FILE through
ONE loader chain and are NOT modified; the anchor is reproduced by calling
SR1's own functions, not by re-implementing them.

Stages: part0 -> pilot -> joint -> clean -> finalize -> report
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import re
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-SR2"
OUT = ROOT / "results" / "m4_sr2_coupling_budget"
REPORT = ROOT / "reports" / "SUICA_M4_SR2_COUPLING_BUDGET_REPORT.md"

T1CORE = ROOT / "suica_core" / "hierarchical_selection_identity.py"
T2HARNESS = ROOT / "scripts" / "run_suica_m4_t2_matched_residual.py"
T3HARNESS = ROOT / "scripts" / "run_suica_m4_t3_identity_budget.py"
SR1HARNESS = ROOT / "scripts" / "run_suica_m4_sr1_selection_geometry.py"
SR1RES = ROOT / "results" / "m4_sr1_selection_geometry"
T2RES = ROOT / "results" / "m4_t2_matched_residual"
T3RES = ROOT / "results" / "m4_t3_identity_budget"
SR1NPZ = SR1RES / "selection.npz"
SR0COHORT = ROOT / "results" / "m4_sr0_recon" / "cohort_authors.csv"

SEED = 20260817          # the T-line seed (folds, representations)
SR1_SEED = 20260816      # SR1's master seed -- the anchor must use ITS seed
B_PERM = 999
PERM_CHUNK = 200
PILOT_USERS = 200
POOL_TARGET = 20
N_STRATA = 10
FOLDS, MAX_DEPTH, MIN_LEAF, EMB_DIM = 5, 6, 30, 64

# --- anchors ---------------------------------------------------------------
A_SR1_R = 0.048987613136188025
A_SR1_PAIRS = 852165
A_SR1_USERS = 1306
A_SR1_P = 0.001
A_SR1_NULL_SD = 0.009064019613144935
A_T3_OBS = 0.7293990670964055
A_T3_EMB_STRAT = 0.9311359256886822
A_N_FULL, A_N_CLEAN, A_REMOVED = 1304, 1269, 23

REPS = ("R_obs", "R_tree", "R_emb", "R_flat")

RN_NOTES = {
    "RN-SR2-1":
        "LABEL GOVERNANCE.  stage_part0 builds the whole analysis config, "
        "hashes it and stamps it, and opens NO label -- the profiles file is "
        "not read, and no joint selection x trait quantity exists anywhere in "
        "the harness before that stamp.  stage_pilot is also label-free: it "
        "calibrates achievable band widths against a SYNTHETIC standard-normal "
        "trait surrogate of the same construction, so the resolution question "
        "is settled before the real labels are touched.  stage_joint logs "
        "`first_join` and only then reads Big5.  The run log is the proof.",
    "RN-SR2-2":
        "THE PAIR SET IS NOT ONE SET, AND IT CANNOT BE.  SR1's pair set is all "
        "852165 pairs over 1306 users.  R_tree and R_emb are FOLD-LOCAL "
        "objects: two users in different folds were routed through different "
        "frozen trees and their taste centroids live in different SVD bases, "
        "so a cross-fold entry is not a small number, it is undefined.  The "
        "budget therefore runs on the WITHIN-FOLD pair mask, where all four "
        "representations are defined and comparable (T3's RN-T3-1 principle), "
        "while R_obs and R_flat -- which have no fold locality -- are ALSO "
        "reported on SR1's full pair set, where the anchor and V-SR2a/c live.  "
        "Both are in every table.  See RD-SR2-1.",
    "RN-SR2-3":
        "EACH REPRESENTATION BRINGS ITS OWN HALF, because each is the frozen "
        "object its own leg registered: R_flat is SR1's FULL-corpus Hellinger "
        "cosine (the anchor must be bit-exact, so nothing about it may move); "
        "R_obs is T3's LATE-side observability vector; R_tree and R_emb are "
        "EARLY-side, the half T1 fitted the tree on and T2 fitted the "
        "embedding on.  This is inherited, not chosen, and full-half "
        "sensitivities are reported for R_obs where they are cheap.  See "
        "RD-SR2-2.",
    "RN-SR2-4":
        "THE CONDITIONAL NULL PERMUTES USERS WITHIN OBSERVABILITY STRATA "
        "(T3's PC1 deciles).  A permuted user therefore has the same "
        "observability profile as the one it replaced, so ANY observability x "
        "trait coupling is preserved in the null.  What clears that null is "
        "selection x trait coupling BEYOND support.  This is the audit SR1 "
        "never ran.",
    "RN-SR2-5":
        "own bands throughout (#66/#68): every reading is judged against the "
        "band its own permutation machinery produces, never against a closed "
        "form and never against zero.  Mantel nulls under user permutation do "
        "sit near zero, but that is measured here, not assumed.",
    "RN-SR2-6":
        "#70 COMPLIANCE.  T3 raised, and the line adopted, that 'z-scored' "
        "underspecifies a transform for heavy-tailed observables.  R_obs is "
        "carried here in BOTH forms -- the registered raw-z one, which owns "
        "V-SR2a, and the log1p one, reported beside it in every table.",
    "RN-SR2-7":
        "EXPLORATORY, CORPUS-LEVEL.  Every quantity is a relation between "
        "similarity matrices over the cohort.  Nothing here is a statement "
        "about any person, no per-user trait value is reported or persisted "
        "outside the gitignored intermediates, and r = 0.049 is a corpus "
        "coupling far below any individual-level usefulness.",
}

_MODS: dict[str, Any] = {}


def _load_named(name: str, path: Path) -> Any:
    if name not in _MODS:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
        sys.modules[name] = mod
        spec.loader.exec_module(mod)                         # type: ignore[union-attr]
        _MODS[name] = mod
    return _MODS[name]


def t1core() -> Any:
    return _load_named("suica_core.hierarchical_selection_identity", T1CORE)


def t2() -> Any:
    return _load_named("m4_t2_matched_residual", T2HARNESS)


def t3() -> Any:
    return _load_named("m4_t3_identity_budget", T3HARNESS)


def sr1() -> Any:
    return _load_named("m4_sr1_selection_geometry", SR1HARNESS)


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


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# SELECTION-SIDE SIMILARITY MATRICES.  NO LABEL IS TOUCHED IN THIS SECTION.


def build_selection_side(arm: str) -> dict[str, Any]:
    """The four frozen representations as 1306 x 1306 similarity matrices."""
    tt, t3m, core = t2(), t3(), t1core()
    d = np.load(SR1NPZ, allow_pickle=True)
    users = [str(u) for u in d["users"]]
    n = len(users)
    freq = np.asarray(d["freq"], dtype=float).copy()
    fe = np.asarray(d["freq_early"], dtype=float).copy()
    fl = np.asarray(d["freq_late"], dtype=float).copy()
    c = np.load(T2RES / "counts.npz", allow_pickle=True)
    ec, lc = c["early_counts"].astype(float), c["late_counts"].astype(float)
    span_late = c["span_late_days"]
    if arm == "clean":
        rem = c["removed_indices"]
        for m in (freq, fe, fl, ec, lc):
            m[:, rem] = 0.0
        freq = tt.row_normalise(freq)
        fe, fl = tt.row_normalise(ec), tt.row_normalise(lc)
    obs_late = t3m.obs_matrix(lc, fl, span_late, log_scale=False)
    obs_late_log = t3m.obs_matrix(lc, fl, span_late, log_scale=True)

    # folds: T1's frozen structure, reproduced exactly
    he = core.hellinger_rows(fe)
    hl = core.hellinger_rows(fl)
    valid = (np.linalg.norm(he, axis=1) > 0) & (np.linalg.norm(hl, axis=1) > 0)
    hev = he[valid]
    orig = np.flatnonzero(valid)
    fold_of = np.full(n, -1, dtype=int)
    sim_tree = np.zeros((n, n))
    sim_emb = np.zeros((n, n))
    splitter = KFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    for fold, (tr, te) in enumerate(splitter.split(hev)):
        tree = core.fit_selection_tree(hev[tr], max_depth=MAX_DEPTH,
                                       min_leaf=MIN_LEAF,
                                       random_state=SEED + 1000 * fold)
        teg, trg = orig[te], orig[tr]
        fold_of[teg] = fold
        code, _c2, _lv = t3m.path_codes(tree, hev[te], hev[te])
        block = t3m.cosine_scores(code, code)
        sim_tree[np.ix_(teg, teg)] = block
        emb = tt.ppmi_svd(ec[trg], EMB_DIM, SEED + fold)
        cent = fe[teg] @ emb
        sim_emb[np.ix_(teg, teg)] = t3m.cosine_scores(cent, cent)
    return {
        "users": users, "n": n, "fold_of": fold_of, "n_valid": int(valid.sum()),
        "sim": {"R_obs": sr1().neg_euclid(obs_late, squared=False),
                "R_tree": sim_tree, "R_emb": sim_emb,
                "R_flat": sr1().hellinger_cos(freq)},
        "sim_obs_log": sr1().neg_euclid(obs_late_log, squared=False),
        "obs_late": obs_late, "arm": arm}


def pair_masks(sel: dict[str, Any]) -> dict[str, Any]:
    n = sel["n"]
    iu = np.triu_indices(n, k=1)
    same_fold = ((sel["fold_of"][iu[0]] == sel["fold_of"][iu[1]])
                 & (sel["fold_of"][iu[0]] >= 0))
    return {"full": (iu[0], iu[1]),
            "within_fold": (iu[0][same_fold], iu[1][same_fold]),
            "n_full": int(len(iu[0])), "n_within": int(same_fold.sum())}


def observability_strata(obs_late: np.ndarray) -> dict[str, Any]:
    xc = obs_late - obs_late.mean(axis=0)
    _u, sv, vt = np.linalg.svd(xc, full_matrices=False)
    pc1 = vt[0]
    if pc1.sum() < 0:
        pc1 = -pc1
    index = xc @ pc1
    edges = np.quantile(index, np.linspace(0, 1, N_STRATA + 1))
    assign = np.searchsorted(edges[1:-1], index, side="right")
    sizes = np.bincount(assign, minlength=N_STRATA)
    return {"assign": assign, "sizes": sizes.tolist(),
            "min_stratum": int(sizes.min()), "n_strata": N_STRATA,
            "explained_variance": float((sv ** 2 / (sv ** 2).sum())[0]),
            "loadings": pc1.tolist(),
            "dims": ["volume", "span", "entropy", "breadth"],
            "meets_pool_target": bool(sizes.min() - 1 >= POOL_TARGET),
            "median_pool": float(np.median(sizes) - 1)}


# ---------------------------------------------------------------------------
# MANTEL OVER A FIXED PAIR MASK, WITH USER PERMUTATION (free or stratified).


def _corr(a_centred: np.ndarray, b: np.ndarray) -> float:
    sb = b.std()
    if sb == 0:
        return 0.0
    return float(a_centred @ (b - b.mean()) / (len(b) * sb))


def _permute(n: int, rng: np.random.Generator,
             strata: np.ndarray | None) -> np.ndarray:
    if strata is None:
        return rng.permutation(n)
    p = np.arange(n)
    for s in np.unique(strata):
        idx = np.flatnonzero(strata == s)
        p[idx] = idx[rng.permutation(len(idx))]
    return p


def mantel_masked(A: np.ndarray, B: np.ndarray, mask: tuple[np.ndarray, ...],
                  b_perm: int, seed: int,
                  strata: np.ndarray | None = None) -> dict[str, Any]:
    i_idx, j_idx = mask
    a = A[i_idx, j_idx]
    sa = a.std()
    if sa == 0:
        return {"r": 0.0, "degenerate": True, "n_pairs": int(len(a))}
    a_c = (a - a.mean()) / sa
    r_obs = _corr(a_c, B[i_idx, j_idx])
    rng = np.random.default_rng(seed)
    vals = np.empty(b_perm)
    for k in range(b_perm):
        p = _permute(A.shape[0], rng, strata)
        vals[k] = _corr(a_c, B[p[i_idx], p[j_idx]])
    ge = int(np.sum(vals >= r_obs))
    sd = float(vals.std(ddof=1))
    return {"r": float(r_obs), "n_pairs": int(len(a)), "n_perm": int(b_perm),
            "p_one_sided_positive": float((ge + 1) / (b_perm + 1)),
            "n_perm_ge_observed": ge,
            "null_mean": float(vals.mean()), "null_sd": sd,
            "null_p95": float(np.percentile(vals, 95)),
            "null_band": [float(np.percentile(vals, 2.5)),
                          float(np.percentile(vals, 97.5))],
            "null_max": float(vals.max()),
            "z_vs_null": float((r_obs - vals.mean()) / sd) if sd > 0 else 0.0,
            "DETECTED": bool(r_obs > float(np.percentile(vals, 95))),
            "stratified": strata is not None,
            "degenerate": bool(sd <= 0)}


# ---------------------------------------------------------------------------
# STAGES.


def stage_part0(args: argparse.Namespace) -> None:
    """G0sr2 + THE STAMP.  NO LABEL IS OPENED HERE."""
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start", labels_opened=False)
    t3v = read_json(T3RES / "verdicts.json")
    t2a = read_json(T2RES / "arms_full.json")
    sr1j = read_json(SR1RES / "join.json")
    anchors = {
        "SR1 primary r": [sr1j["primary"]["r"], A_SR1_R],
        "SR1 pairs": [sr1j["primary"]["n_pairs"], A_SR1_PAIRS],
        "SR1 users joined": [sr1j["n_users_joined"], A_SR1_USERS],
        "SR1 p(one-sided)": [sr1j["primary"]["p_one_sided_positive"], A_SR1_P],
        "SR1 null sd": [sr1j["primary"]["null_sd"], A_SR1_NULL_SD],
        "T3 R_obs marginal": [t3v["V_T3a"]["numbers"]["auc"], A_T3_OBS],
        "T3 R_emb stratified": [t3v["V_T3b"]["numbers"]["auc"], A_T3_EMB_STRAT],
    }
    g0: dict[str, Any] = {
        "anchors": {k: {"persisted": v[0], "expected": v[1],
                        "match": bool(v[0] == v[1])}
                    for k, v in anchors.items()},
        "T2_embedding_purity": t2a["arm_b"]["embedding"]["all_folds_pure"],
        "sha256": {"t1_core": sha_file(T1CORE), "t2": sha_file(T2HARNESS),
                   "t3": sha_file(T3HARNESS), "sr1": sha_file(SR1HARNESS),
                   "sr1_selection_npz": sha_file(SR1NPZ)}}
    g0["all_anchors_match"] = bool(all(c["match"]
                                       for c in g0["anchors"].values()))
    sel = build_selection_side("full")
    masks = pair_masks(sel)
    strata = observability_strata(sel["obs_late"])
    g0["n_valid"] = sel["n_valid"]
    g0["n_valid_matches_T1"] = bool(sel["n_valid"] == A_N_FULL)
    g0["pair_sets"] = {"sr1_full_pairs": masks["n_full"],
                       "matches_sr1": bool(masks["n_full"] == A_SR1_PAIRS),
                       "within_fold_pairs": masks["n_within"],
                       "within_fold_share":
                           float(masks["n_within"] / masks["n_full"])}
    g0["strata"] = {k: v for k, v in strata.items() if k != "assign"}
    g0["PASS"] = bool(g0["all_anchors_match"] and g0["n_valid_matches_T1"]
                      and g0["pair_sets"]["matches_sr1"]
                      and g0["T2_embedding_purity"])

    if not g0["PASS"]:
        write_json(OUT / "part0_failed.json",
                   {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
                    "G0sr2": g0, "stamp_issued": False})
        _log("part0_failed", labels_opened=False, stamp_issued=False)
        raise SystemExit(f"G0sr2 FAILED -> STOP (no stamp issued) {g0}")

    config = {
        "leg": LEG, "registration": "M4-SR2, commit a34f12c",
        "seeds": {"t_line": SEED, "sr1_anchor": SR1_SEED},
        "b_perm": B_PERM, "pool_target": POOL_TARGET, "n_strata": N_STRATA,
        "representations": list(REPS),
        "similarities": {
            "R_obs": "negative Euclidean on the registered raw z-scored "
                     "4-dim late-side observability vector (log1p carried "
                     "as the #70 sensitivity)",
            "R_tree": "cosine of the depth-weighted prefix path code "
                      "(early-half routing through the frozen fold tree)",
            "R_emb": "cosine of the early-half taste centroid in the frozen "
                     "per-fold PPMI+SVD embedding, d=64",
            "R_flat": "SR1's Hellinger cosine over the FULL corpus frequency "
                      "matrix -- SR1's own primary, unchanged",
            "trait": "SR1's negative SQUARED Euclidean over five z-scored "
                     "Big5, loaded by SR1's own _load_traits"},
        "pair_sets": {"anchor_and_V_SR2a_V_SR2c": "SR1's full pair set",
                      "budget": "within-fold mask (RN-SR2-2)"},
        "nulls": {"marginal": "free user permutation, B=999",
                  "conditional": "user permutation WITHIN observability "
                                 "PC1 deciles, B=999"},
        "verdicts": {"V-SR2a": "R_obs x trait marginal: DETECTED / NULL",
                     "V-SR2b": "R_emb x trait marginal + stratified: "
                               "detected-and-SURVIVES / detected-but-DIES / "
                               "NULL_MARGINAL",
                     "V-SR2c": "SR1's own r under the stratified null: "
                               "SURVIVES / DIES"},
        "routing": ["SR1_RETYPED_SUPPORT_CONFOUND", "TASTE_CARRIES_THE_COUPLING",
                    "COUPLING_BEYOND_TASTE", "UNDERRESOLVED", "STOP"],
        "RN_NOTES": RN_NOTES,
        "G0sr2": g0,
    }
    write_json(OUT / "config.json", config)
    digest = sha_file(OUT / "config.json")
    stamp_utc = datetime.now(UTC).isoformat()
    write_json(OUT / "config.sha256.json",
               {"sha256": digest, "stamp_utc": stamp_utc,
                "joint_quantities_before_stamp": 0,
                "labels_opened_before_stamp": False,
                "profiles_read_before_stamp": False})
    _log("config_stamped", sha256=digest, stamp_utc=stamp_utc,
         joint_quantities_before_stamp=0, labels_opened=False)
    write_json(OUT / "part0.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(), "G0sr2": g0,
        "stamp": {"sha256": digest, "stamp_utc": stamp_utc},
        "environment": {"python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0})
    _log("part0_done", pass_=g0["PASS"], labels_opened=False)
    print(f"part0 OK  anchors={g0['all_anchors_match']} "
          f"n_valid={sel['n_valid']} pairs full={masks['n_full']} "
          f"(SR1 match {g0['pair_sets']['matches_sr1']}) "
          f"within-fold={masks['n_within']} "
          f"({100 * g0['pair_sets']['within_fold_share']:.1f}%)\n"
          f"  strata min={strata['min_stratum']} median pool="
          f"{strata['median_pool']:.0f} target {POOL_TARGET} "
          f"({strata['meets_pool_target']})\n"
          f"  STAMPED {digest[:16]} at {stamp_utc}  labels opened = False  "
          f"{time.time() - t0:.1f}s")


def stage_pilot(args: argparse.Namespace) -> None:
    """G2sr2 -- LABEL-FREE calibration against a synthetic trait surrogate."""
    t0 = time.time()
    _log("pilot_start", labels_opened=False)
    sel = build_selection_side("full")
    strata_all = observability_strata(sel["obs_late"])
    rng = np.random.default_rng(SEED + 7)
    pick = np.sort(rng.choice(sel["n"], size=PILOT_USERS, replace=False))
    sub_fold = sel["fold_of"][pick]
    iu = np.triu_indices(PILOT_USERS, k=1)
    same = (sub_fold[iu[0]] == sub_fold[iu[1]]) & (sub_fold[iu[0]] >= 0)
    masks = {"full": (iu[0], iu[1]),
             "within_fold": (iu[0][same], iu[1][same])}
    surrogate = rng.standard_normal((PILOT_USERS, 5))
    b_surrogate = sr1().neg_euclid(surrogate, squared=True)
    sub_strata = strata_all["assign"][pick]
    scale = float(np.sqrt(PILOT_USERS / sel["n"]))
    cal: dict[str, Any] = {}
    for name in REPS:
        A = sel["sim"][name][np.ix_(pick, pick)]
        for mode, strata in (("marginal", None), ("stratified", sub_strata)):
            key = f"{name}|{mode}"
            mk = masks["full"] if name in ("R_obs", "R_flat") else \
                masks["within_fold"]
            res = mantel_masked(A, b_surrogate, mk, 299, SEED + 11, strata)
            proj = res["null_sd"] * scale
            cal[key] = {
                "pilot_null_sd": res["null_sd"],
                "pilot_null_band": res["null_band"],
                "pilot_null_p95": res["null_p95"],
                "projected_full_null_sd": proj,
                "projected_full_p95": float(res["null_p95"] * scale),
                "n_pairs_pilot": res["n_pairs"],
                "non_degenerate": bool(res["null_sd"] > 1e-12),
                "detects_sr1_magnitude": bool(res["null_p95"] * scale
                                              < A_SR1_R)}
            print(f"  pilot {key}: sd={res['null_sd']:.5f} "
                  f"p95={res['null_p95']:.5f} -> full p95~"
                  f"{res['null_p95'] * scale:.5f} "
                  f"detects={cal[key]['detects_sr1_magnitude']}")
    verdict = "PASS" if all(c["detects_sr1_magnitude"] and c["non_degenerate"]
                            for c in cal.values()) \
        else "UNDERRESOLVED_BY_DESIGN"
    write_json(OUT / "pilot.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G2sr2": {"n_pilot_users": PILOT_USERS, "b_perm": 299,
                  "labels_opened": False,
                  "surrogate": "standard-normal 5-dim, SR1's neg-sq-Euclid "
                               "construction -- no real label is read",
                  "projection_rule": "Mantel null sd scales as sqrt(n_users); "
                                     f"pilot->full factor {1 / scale:.4f}",
                  "detection_reference": A_SR1_R,
                  "strata": {k: v for k, v in strata_all.items()
                             if k != "assign"},
                  "VERDICT": verdict, "note": RN_NOTES["RN-SR2-1"]},
        "calibration": cal, "seconds": time.time() - t0})
    _log("pilot_done", verdict=verdict, labels_opened=False)
    print(f"pilot {verdict}  (label-free)  {time.time() - t0:.1f}s")


def _budget(sel: dict[str, Any], B: np.ndarray, masks: dict[str, Any],
            strata: np.ndarray, seed0: int, b_perm: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for i, name in enumerate(REPS):
        A = sel["sim"][name]
        for j, (mode, st) in enumerate((("marginal", None),
                                        ("stratified", strata))):
            for pset in ("within_fold", "full"):
                if name in ("R_tree", "R_emb") and pset == "full":
                    continue
                key = f"{name}|{mode}|{pset}"
                res = mantel_masked(A, B, masks[pset], b_perm,
                                    seed0 + 31 * i + 7 * j
                                    + (3 if pset == "full" else 0), st)
                out[key] = res
                print(f"  {key}: r={res['r']:.6f} band="
                      f"[{res['null_band'][0]:.5f}, {res['null_band'][1]:.5f}] "
                      f"p={res['p_one_sided_positive']:.4f} "
                      f"z={res['z_vs_null']:.2f} pairs={res['n_pairs']}")
    for j, (mode, st) in enumerate((("marginal", None),
                                    ("stratified", strata))):
        res = mantel_masked(sel["sim_obs_log"], B, masks["full"], b_perm,
                            seed0 + 900 + j, st)
        out[f"R_obs_log|{mode}|full"] = res
        print(f"  R_obs_log|{mode}|full (#70 sensitivity): r={res['r']:.6f} "
              f"band=[{res['null_band'][0]:.5f}, {res['null_band'][1]:.5f}] "
              f"p={res['p_one_sided_positive']:.4f}")
    return out


def _run_arm(arm: str, seed_shift: int, z: np.ndarray) -> dict[str, Any]:
    sel = build_selection_side(arm)
    masks = pair_masks(sel)
    strata_info = observability_strata(sel["obs_late"])
    B = sr1().neg_euclid(z, squared=True)
    budget = _budget(sel, B, masks, strata_info["assign"],
                     SEED + seed_shift, B_PERM)
    return {"arm": arm, "n_valid": sel["n_valid"], "budget": budget,
            "pair_sets": {"full": masks["n_full"],
                          "within_fold": masks["n_within"]},
            "strata": {k: v for k, v in strata_info.items() if k != "assign"}}


def stage_joint(args: argparse.Namespace) -> None:
    """THE FIRST JOINT SELECTION x TRAIT QUANTITY OF THIS HARNESS LIVES HERE."""
    t0 = time.time()
    stamp = read_json(OUT / "config.sha256.json")
    digest = sha_file(OUT / "config.json")
    if digest != stamp["sha256"]:
        raise SystemExit("CONFIG HASH MISMATCH -> STOP/VOID")
    _log("first_join", config_sha256=digest,
         note="the first joint selection x trait quantity of the harness is "
              "computed after this event; Big5 is read on the next line")
    d = np.load(SR1NPZ, allow_pickle=True)
    users = [str(u) for u in d["users"]]
    z, info = sr1()._load_traits(users)
    _log("labels_opened", n_users=len(users), source=rel(sr1().PROFILES),
         n_with_all_big5=info["n_with_all_big5"])
    keep = ~np.isnan(z).any(axis=1)
    if not bool(keep.all()):
        raise SystemExit("SR1 joined all 1306; this run did not -> STOP")

    # --- G0: SR1's primary reproduced by SR1's OWN code -------------------
    A_sr1 = sr1().hellinger_cos(np.asarray(d["freq"], dtype=float)[keep])
    B_sr1 = sr1().neg_euclid(z[keep], squared=True)
    anchor = sr1().mantel_perm(A_sr1, B_sr1, B_PERM, SR1_SEED, PERM_CHUNK)
    anchor_ok = bool(anchor["r"] == A_SR1_R
                     and anchor["n_pairs"] == A_SR1_PAIRS
                     and anchor["p_one_sided_positive"] == A_SR1_P
                     and anchor["null_sd"] == A_SR1_NULL_SD)
    print(f"  G0 anchor: r={anchor['r']!r} (expected {A_SR1_R!r}) "
          f"bit-exact={anchor_ok}")
    if not anchor_ok:
        raise SystemExit(f"G0sr2 ANCHOR NOT BIT-EXACT -> STOP {anchor}")

    res = _run_arm("full", 0, z)
    res.update({"utc": datetime.now(UTC).isoformat(),
                "anchor": anchor, "anchor_bit_exact": anchor_ok,
                "trait_join_info": info,
                "stamp": stamp, "seconds": time.time() - t0})
    write_json(OUT / "joint_full.json", res)
    _log("joint_done", seconds=res["seconds"])
    print(f"joint(full) done  {time.time() - t0:.1f}s")


def stage_clean(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("clean_start")
    d = np.load(SR1NPZ, allow_pickle=True)
    users = [str(u) for u in d["users"]]
    z, _info = sr1()._load_traits(users)
    res = _run_arm("clean", 500, z)
    res["utc"] = datetime.now(UTC).isoformat()
    res["seconds"] = time.time() - t0
    res["n_valid_matches_T1_clean"] = bool(res["n_valid"] == A_N_CLEAN)
    write_json(OUT / "joint_clean.json", res)
    _log("clean_done", seconds=res["seconds"])
    print(f"clean done  n_valid={res['n_valid']} "
          f"(T1 {A_N_CLEAN}: {res['n_valid_matches_T1_clean']})  "
          f"{time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# VERDICTS (NULL-first, arm-level).


def verdict_a(r: dict[str, Any]) -> dict[str, Any]:
    if r.get("degenerate"):
        return {"verdict": "UNDERRESOLVED", "reason": "degenerate null"}
    if r["DETECTED"]:
        return {"verdict": "DETECTED",
                "reason": "the observed r exceeds the one-sided 95th "
                          "percentile of its own permutation null"}
    return {"verdict": "NULL",
            "reason": "the observed r does not clear its own null's one-sided "
                      "95th percentile"}


def verdict_b(marg: dict[str, Any], strat: dict[str, Any]) -> dict[str, Any]:
    if marg.get("degenerate") or strat.get("degenerate"):
        return {"verdict": "UNDERRESOLVED", "reason": "degenerate null"}
    if not marg["DETECTED"]:
        return {"verdict": "NULL_MARGINAL",
                "reason": "the taste coordinate shows no trait coupling even "
                          "marginally -- it is trait-silent on this corpus"}
    if strat["DETECTED"]:
        return {"verdict": "detected-and-SURVIVES",
                "reason": "detected marginally and still clears its own null "
                          "when users are permuted within observability strata"}
    return {"verdict": "detected-but-DIES",
            "reason": "detected marginally but does not clear the "
                      "observability-stratified null"}


def verdict_c(strat: dict[str, Any]) -> dict[str, Any]:
    if strat.get("degenerate"):
        return {"verdict": "UNDERRESOLVED", "reason": "degenerate null"}
    if strat["DETECTED"]:
        return {"verdict": "SURVIVES",
                "reason": "SR1's own coupling still clears its own null when "
                          "users are permuted within observability strata"}
    return {"verdict": "DIES",
            "reason": "SR1's coupling does not survive conditioning on "
                      "observability"}


def route(va: str, vb: str, vc: str) -> dict[str, Any]:
    modifiers = []
    if vc == "DIES":
        outcome = "SR1_RETYPED_SUPPORT_CONFOUND"
    elif vc == "SURVIVES" and vb == "detected-and-SURVIVES":
        outcome = "TASTE_CARRIES_THE_COUPLING"
    elif vc == "SURVIVES":
        outcome = "COUPLING_BEYOND_TASTE"
    else:
        outcome = "UNDERRESOLVED"
    modifiers.append("SUPPORT_TRAIT_COUPLING_DETECTED" if va == "DETECTED"
                     else "SUPPORT_TRAIT_COUPLING_NULL")
    under = [n for n, x in (("V-SR2a", va), ("V-SR2b", vb), ("V-SR2c", vc))
             if x == "UNDERRESOLVED"]
    if under:
        modifiers.append("UNDERRESOLVED:" + "+".join(under))
    return {"outcome": outcome, "modifiers": modifiers,
            "slug": outcome.lower().replace("_", "-"),
            "cells": {"V-SR2a": va, "V-SR2b": vb, "V-SR2c": vc}}


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("finalize_start")
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    full = read_json(OUT / "joint_full.json")
    clean = read_json(OUT / "joint_clean.json")
    b = full["budget"]
    va = verdict_a(b["R_obs|marginal|full"])
    vb = verdict_b(b["R_emb|marginal|within_fold"],
                   b["R_emb|stratified|within_fold"])
    vc = verdict_c(b["R_flat|stratified|full"])
    routing = route(va["verdict"], vb["verdict"], vc["verdict"])
    rs = [x["r"] for x in b.values()]
    g1 = {"r_spread": [float(min(rs)), float(max(rs))],
          "none_forced": bool(max(abs(x) for x in rs) < 0.999),
          "strata_non_degenerate": full["strata"]["meets_pool_target"],
          "min_stratum": full["strata"]["min_stratum"]}
    g1["PASS"] = bool(g1["none_forced"] and g1["strata_non_degenerate"])
    preds = []
    for arm_name, blob in (("full", full), ("clean", clean)):
        for k, r in sorted(blob["budget"].items()):
            preds.append({"what": f"{arm_name}:{k}",
                          "r_in_unit": bool(-1.0 <= r["r"] <= 1.0),
                          "own_band_used": True,
                          "null_non_degenerate": bool(not r.get("degenerate")),
                          "p_in_unit": bool(0.0 < r["p_one_sided_positive"]
                                            <= 1.0)})
    g3 = {"predicates": preds, "note": RN_NOTES["RN-SR2-5"],
          "stamp_before_join": None, "PASS": bool(
              all(p["r_in_unit"] and p["null_non_degenerate"]
                  and p["p_in_unit"] for p in preds))}
    events = [json.loads(x) for x in
              (OUT / "run_log.jsonl").read_text().splitlines() if x.strip()]
    cur_sha = sha_file(OUT / "config.json")
    stamp_e = next(e for e in events if e["event"] == "config_stamped"
                   and e["sha256"] == cur_sha)
    join_e = next(e for e in events if e["event"] == "first_join")
    label_e = next(e for e in events if e["event"] == "labels_opened")
    g3["stamp_before_join"] = {
        "config_stamped_utc": stamp_e["utc"], "first_join_utc": join_e["utc"],
        "labels_opened_utc": label_e["utc"],
        "stamp_precedes_join": bool(stamp_e["utc"] < join_e["utc"]),
        "join_precedes_labels": bool(join_e["utc"] <= label_e["utc"]),
        "events_before_join_all_label_free": bool(all(
            e.get("labels_opened", False) is False
            for e in events if e["utc"] < join_e["utc"])),
        "config_sha256": stamp_e["sha256"]}
    g3["PASS"] = bool(g3["PASS"] and g3["stamp_before_join"]["stamp_precedes_join"]
                      and g3["stamp_before_join"]["join_precedes_labels"])
    out = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "gates": {"G0sr2": p0["G0sr2"]["PASS"],
                  "anchor_bit_exact": full["anchor_bit_exact"],
                  "G1sr2": g1, "G2sr2": pil["G2sr2"]["VERDICT"], "G3sr2": g3},
        "V_SR2a": {**va, "reading": "R_obs|marginal|full",
                   "numbers": b["R_obs|marginal|full"],
                   "log_sensitivity": b["R_obs_log|marginal|full"]},
        "V_SR2b": {**vb, "marginal": b["R_emb|marginal|within_fold"],
                   "stratified": b["R_emb|stratified|within_fold"]},
        "V_SR2c": {**vc, "reading": "R_flat|stratified|full",
                   "marginal_anchor": full["anchor"],
                   "stratified": b["R_flat|stratified|full"],
                   "marginal_same_machinery": b["R_flat|marginal|full"]},
        "routing": routing,
        "readings": {
            "coupling_budget": {k: {f: r.get(f) for f in
                                    ("r", "null_band", "null_sd", "null_p95",
                                     "p_one_sided_positive", "z_vs_null",
                                     "n_pairs", "DETECTED")}
                                for k, r in sorted(b.items())},
            "carrier_ordering": sorted(
                [(n, b[f"{n}|marginal|within_fold"]["r"],
                  b[f"{n}|marginal|within_fold"]["z_vs_null"]) for n in REPS],
                key=lambda x: -x[1]),
            "clean_replication": {
                "n_valid": clean["n_valid"],
                "matches_T1_clean_n": clean.get("n_valid_matches_T1_clean"),
                "budget": {k: {f: r.get(f) for f in
                               ("r", "null_band", "p_one_sided_positive",
                                "DETECTED")}
                           for k, r in sorted(clean["budget"].items())},
                "V_SR2a_clean": verdict_a(
                    clean["budget"]["R_obs|marginal|full"]),
                "V_SR2b_clean": verdict_b(
                    clean["budget"]["R_emb|marginal|within_fold"],
                    clean["budget"]["R_emb|stratified|within_fold"]),
                "V_SR2c_clean": verdict_c(
                    clean["budget"]["R_flat|stratified|full"])},
            "pair_sets": full["pair_sets"], "strata": full["strata"]},
        "seconds": time.time() - t0}
    write_json(OUT / "verdicts.json", out)
    _log("finalize_done", slug=routing["slug"])
    print(f"V-SR2a={va['verdict']}  V-SR2b={vb['verdict']}  "
          f"V-SR2c={vc['verdict']}")
    print(f"  -> {routing['outcome']} mods={routing['modifiers']} "
          f"slug={routing['slug']}  G1={g1['PASS']} G3={g3['PASS']} "
          f"stamp<join={g3['stamp_before_join']['stamp_precedes_join']}")


def stage_report(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("report_start")
    tt = t2()
    fmt, tbl = tt._fmt, tt._table
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    full = read_json(OUT / "joint_full.json")
    clean = read_json(OUT / "joint_clean.json")
    v = read_json(OUT / "verdicts.json")
    g0, b = p0["G0sr2"], full["budget"]
    st = v["gates"]["G3sr2"]["stamp_before_join"]
    va, vb, vc = v["V_SR2a"], v["V_SR2b"], v["V_SR2c"]
    cl = v["readings"]["clean_replication"]

    anchors = tbl(["anchor", "persisted", "expected", "match"],
                  [[k, repr(c["persisted"]), repr(c["expected"]),
                    str(c["match"])] for k, c in sorted(g0["anchors"].items())])

    gates = tbl(["gate", "what it checks", "result"],
                [["G0sr2", "SR1's primary reproduced BIT-EXACTLY by SR1's own "
                  "code; T3 budget anchors; embedding purity; pair set",
                  f"**{'PASS' if g0['PASS'] else 'FAIL'}** "
                  f"(anchor bit-exact: {v['gates']['anchor_bit_exact']})"],
                 ["G1sr2", "#59: no coupling forced; strata non-degenerate",
                  f"**{'PASS' if v['gates']['G1sr2']['PASS'] else 'FAIL'}** "
                  f"(r spread {fmt(v['gates']['G1sr2']['r_spread'], 4)})"],
                 ["G2sr2", "LABEL-FREE pilot calibration before the joint "
                  "stage (#71); pool target 20",
                  f"**{v['gates']['G2sr2']}**"],
                 ["G3sr2", "config-before-joint stamp with run-log proof; "
                  "rule-29 own-null predicates",
                  f"**{'PASS' if v['gates']['G3sr2']['PASS'] else 'FAIL'}** "
                  f"({len(v['gates']['G3sr2']['predicates'])} predicates)"]])

    pilot_tbl = tbl(["reading", "pilot null sd", "pilot p95",
                     "projected full p95", "detects r = 0.049"],
                    [[k, fmt(c["pilot_null_sd"], 5), fmt(c["pilot_null_p95"], 5),
                      fmt(c["projected_full_p95"], 5),
                      f"**{c['detects_sr1_magnitude']}**"]
                     for k, c in sorted(pil["calibration"].items())])

    def budget_tbl(blob: dict[str, Any]) -> str:
        rows = []
        for key in sorted(blob):
            r = blob[key]
            name, mode, pset = key.split("|")
            rows.append([f"`{name}`", mode, pset.replace("_", "-"),
                         fmt(r["r"], 6), fmt(r["null_band"], 5),
                         fmt(r.get("null_sd"), 5),
                         fmt(r["p_one_sided_positive"], 4),
                         fmt(r.get("z_vs_null"), 2),
                         str(r["n_pairs"]),
                         f"**{r['DETECTED']}**"])
        return tbl(["representation", "null", "pair set", "Mantel r",
                    "own null band", "null sd", "p (1-sided)", "z", "pairs",
                    "detected"], rows)

    order = tbl(["rank", "representation", "marginal r (within-fold)", "z"],
                [[str(i + 1), f"`{n}`", fmt(r, 6), fmt(zz, 2)]
                 for i, (n, r, zz) in
                 enumerate(v["readings"]["carrier_ordering"])])

    body = f"""# SUICA M4-SR2 — the trait-coupling budget (which component carries r = 0.049?)

**Leg:** {LEG}. **Registered BEFORE run** in
`docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md` (§ "M4-SR2",
commit a34f12c). Generated by `{rel(Path(__file__))}` — every table is
written by the script from the persisted artifacts (rule 24).

**Type:** EXPLORATORY, corpus-level. Every quantity is a relation between
similarity matrices over the cohort; nothing here is a statement about any
person (RN-SR2-7).

## 1. Label governance — the point of the whole T-line ordering

This is the line's external-connection leg and **the only one that opens
labels**. T1's tree, T2's embedding, T3's observability vectors and the
entire identity budget were all frozen LABEL-FREE before this leg existed.

| event | UTC | config sha256 |
|---|---|---|
| `config_stamped` | {st['config_stamped_utc']} | `{st['config_sha256'][:16]}…` |
| `first_join` | {st['first_join_utc']} | `{st['config_sha256'][:16]}…` |
| `labels_opened` (Big5 read) | {st['labels_opened_utc']} | — |

Stamp precedes join: **{st['stamp_precedes_join']}**. Join precedes the
first label read: **{st['join_precedes_labels']}**. Every logged event
before the join is label-free: **{st['events_before_join_all_label_free']}**.
The G2 pilot is itself label-free — it calibrates against a synthetic
standard-normal trait surrogate, so the resolution question was settled
before any real Big5 value was touched (RN-SR2-1).

## 2. Gates

{gates}

### G0sr2 — anchors

{anchors}

**SR1's primary is reproduced bit-exactly by calling SR1's own functions**:
r = {full['anchor']['r']!r} against the persisted {A_SR1_R!r},
{full['anchor']['n_pairs']} pairs, p = {full['anchor']['p_one_sided_positive']},
null sd = {full['anchor']['null_sd']!r}. Nothing about SR1's primary was
re-implemented; the anchor is the same code path with the same seed.

Pair sets: SR1's full set **{g0['pair_sets']['sr1_full_pairs']}** pairs
(match {g0['pair_sets']['matches_sr1']}); the within-fold budget mask
**{g0['pair_sets']['within_fold_pairs']}** pairs
({100 * g0['pair_sets']['within_fold_share']:.1f}% of full) — see RN-SR2-2.
Observability strata: {g0['strata']['n_strata']} PC1 deciles, smallest
stratum {g0['strata']['min_stratum']}, median permutation pool
{fmt(g0['strata']['median_pool'], 0)} against the registered target of
{POOL_TARGET}.

## 3. Reading notes (pinned BEFORE the verdicts)

""" + "\n".join(f"- **{k}** — {t}" for k, t in sorted(RN_NOTES.items())) + f"""

## 4. Anomalies (disclosed with timing)

- **A1 — the first G0sr2 run FAILED and stopped the leg (pre-stamp,
  pre-label).** Two T3 anchor constants had been transcribed from rounded
  display output (0.7293894993831059 / 0.9310795160963877) instead of the
  persisted values (0.7293990670964055 / 0.9311359256886822). The gate
  caught it, the run stopped, **no stamp was issued and no label was
  opened**. The harness was then changed so that a failed G0 can never
  issue a stamp at all — on the first run the stamp was written before the
  PASS check, which is the wrong order for a governance artifact even
  though nothing joined. Both the error and the ordering fix are pre-join.
- **A2 — the budget cannot run on SR1's pair set (pre-verdict, structural).**
  R_tree and R_emb are fold-local; cross-fold entries are undefined, not
  small. The budget therefore runs on the within-fold mask and R_obs /
  R_flat are additionally reported on SR1's full set. See RN-SR2-2 and
  RD-SR2-1.
- **A3 — the four representations bring three different halves
  (pre-verdict, inherited).** R_flat is full-corpus (SR1's frozen primary),
  R_obs late-side (T3's frozen vector), R_tree and R_emb early-side (T1's
  and T2's frozen objects). Each is the object its own leg registered; the
  heterogeneity is inherited rather than chosen. See RN-SR2-3, RD-SR2-2.

## 5. G2sr2 — label-free pilot calibration ({pil['G2sr2']['n_pilot_users']} users, B=299)

{pil['G2sr2']['projection_rule']}. Detection reference: SR1's own
r = {A_SR1_R}.

{pilot_tbl}

**G2sr2 verdict: {pil['G2sr2']['VERDICT']}.**

## 6. THE COUPLING BUDGET (full arm, B_perm={B_PERM})

{budget_tbl(b)}

### Carrier ordering (marginal, within-fold — like for like)

{order}

## 7. Verdicts (NULL-first, arm-level)

**V-SR2a — the confound check: {va['verdict']}**
— {va['reason']}. `R_obs` × trait on SR1's full pair set:
r = **{fmt(va['numbers']['r'], 6)}**, own null band
{fmt(va['numbers']['null_band'], 5)}, p = {fmt(va['numbers']['p_one_sided_positive'], 4)},
z = {fmt(va['numbers']['z_vs_null'], 2)}. #70 sensitivity (log1p
observables): r = {fmt(va['log_sensitivity']['r'], 6)}, band
{fmt(va['log_sensitivity']['null_band'], 5)}, p =
{fmt(va['log_sensitivity']['p_one_sided_positive'], 4)}, detected =
{va['log_sensitivity']['DETECTED']}.

**V-SR2b — the carrier question: {vb['verdict']}**
— {vb['reason']}. `R_emb` × trait, within-fold: marginal r =
**{fmt(vb['marginal']['r'], 6)}** (band {fmt(vb['marginal']['null_band'], 5)},
p = {fmt(vb['marginal']['p_one_sided_positive'], 4)}); under the
observability-stratified null r = **{fmt(vb['stratified']['r'], 6)}** (band
{fmt(vb['stratified']['null_band'], 5)}, p =
{fmt(vb['stratified']['p_one_sided_positive'], 4)}).

**V-SR2c — the audit SR1 never ran: {vc['verdict']}**
— {vc['reason']}. SR1's own coupling on SR1's own pair set: marginal
r = {fmt(vc['marginal_same_machinery']['r'], 6)} (band
{fmt(vc['marginal_same_machinery']['null_band'], 5)}, p =
{fmt(vc['marginal_same_machinery']['p_one_sided_positive'], 4)}); under
**user permutation within observability strata** r =
**{fmt(vc['stratified']['r'], 6)}**, band
{fmt(vc['stratified']['null_band'], 5)}, p =
{fmt(vc['stratified']['p_one_sided_positive'], 4)}, z =
{fmt(vc['stratified']['z_vs_null'], 2)}.

## 8. Routing (rule 16 — arm-level)

**{v['routing']['outcome']}** (slug `{v['routing']['slug']}`). Modifiers:
{', '.join(v['routing']['modifiers'])}.

| verdict | value |
|---|---|
| V-SR2a | {va['verdict']} |
| V-SR2b | {vb['verdict']} |
| V-SR2c | {vc['verdict']} |

## 9. Readings (no gates)

### 9.1 Clean-arm replication (T1's {A_REMOVED}-community ablation)

n_valid = {cl['n_valid']} (T1's clean arm {A_N_CLEAN}; match
{cl['matches_T1_clean_n']}). Clean verdicts: **V-SR2a
{cl['V_SR2a_clean']['verdict']}**, **V-SR2b {cl['V_SR2b_clean']['verdict']}**,
**V-SR2c {cl['V_SR2c_clean']['verdict']}**.

{budget_tbl(clean['budget'])}

### 9.2 Post-verdict observations (recorded AFTER the verdicts, marked as such)

- **The ablation costs 41% of SR1's headline, and this is the most
  consequential number in the leg after V-SR2c.** Removing the {A_REMOVED}
  communities that literally NAME personality types takes SR1's coupling
  from {fmt(vc['marginal_same_machinery']['r'], 6)} to
  {fmt(clean['budget']['R_flat|marginal|full']['r'], 6)} — a
  {100 * (1 - clean['budget']['R_flat|marginal|full']['r'] / vc['marginal_same_machinery']['r']):.0f}%
  reduction. It still detects (p =
  {fmt(clean['budget']['R_flat|marginal|full']['p_one_sided_positive'], 4)}) and
  still survives the stratified null (p =
  {fmt(clean['budget']['R_flat|stratified|full']['p_one_sided_positive'], 4)},
  z = {fmt(clean['budget']['R_flat|stratified|full']['z_vs_null'], 2)}), so the
  finding is not overturned. But a large minority of the S-line's headline
  is carried by subreddits whose whole subject is personality typology,
  where a selection-trait coupling is close to tautological. This is
  reported for adjudication, not resolved here.
- **The confound hypothesis is cleanly dead, in both transforms.** The
  registration's first falsifier was "R_obs DETECTED with R_emb dying →
  re-type SR1 as an activity/support correlate". R_obs × trait is
  {fmt(va['numbers']['r'], 6)} (p = {fmt(va['numbers']['p_one_sided_positive'], 4)})
  and the #70 log1p variant is {fmt(va['log_sensitivity']['r'], 6)}
  (p = {fmt(va['log_sensitivity']['p_one_sided_positive'], 4)}). Observability
  carries no trait coupling at all, so that falsifier never fires. Note the
  contrast with T3: observability is a MAJOR-adjacent carrier of IDENTITY
  (AUC 0.7294) and a null carrier of TRAIT. Those are different questions
  and this leg is the first to show they have different answers.
- **The trait coupling lives in the same residual T3 quantified.** T3 found
  tree ⊕ embedding falls {fmt(0.0387, 4)} short of the flat ceiling and
  typed it representation-capacity. Here the d = 64 taste coordinate
  captures {fmt(vb['marginal']['r'], 6)} of the coupling against `R_flat`'s
  {fmt(b['R_flat|marginal|within_fold']['r'], 6)} on the SAME pair set —
  roughly half, and none of it robust to conditioning. Two independent
  lines now point at the same object: the fine-grained community structure
  that the 64-dimensional compression discards.
- **The within-fold mask is representative.** `R_flat` reads
  {fmt(b['R_flat|marginal|within_fold']['r'], 6)} on the mask against
  {fmt(b['R_flat|marginal|full']['r'], 6)} on SR1's full set — a difference
  of {abs(b['R_flat|marginal|within_fold']['r'] - b['R_flat|marginal|full']['r']):.6f}.
  RN-SR2-2's compromise costs almost nothing.
- **The stratified null is STRICTER than the marginal one, not weaker.**
  Within-stratum permutation preserves observability-selection structure,
  which lifts the null's upper tail (R_emb: {fmt(vb['marginal']['null_band'], 5)}
  marginal versus {fmt(vb['stratified']['null_band'], 5)} stratified). That
  is why R_emb dies, and it is the correct behaviour: the conditional test
  is meant to be harder.

## 9.3 Registration-defect candidates (flagged, never repaired)

- **RD-SR2-1 — "SR1's exact pair set" is not available to two of the four
  representations.** R_tree and R_emb are fold-local; a cross-fold entry is
  undefined, not small. Handled by running the budget on the within-fold
  mask and reporting R_obs / R_flat on both (the mask costs 0.0013 of r, so
  nothing material turns on it), but a future registration must either
  register the mask or specify a pooled representation.
- **RD-SR2-2 — the four representations bring three different halves.**
  R_flat full-corpus, R_obs late, R_tree and R_emb early. Each is the
  frozen object its own leg registered, so the heterogeneity is inherited
  rather than chosen — but the registration should say so, because a
  coupling budget invites the reader to compare rows that are not
  half-aligned.
- **RD-SR2-3 — no convention exists for full-versus-clean disagreement
  INSIDE one verdict.** V-SR2b is detected-but-DIES on the full arm
  (marginal p = {fmt(vb['marginal']['p_one_sided_positive'], 4)}) and
  NULL_MARGINAL on the clean arm (p =
  {fmt(clean['budget']['R_emb|marginal|within_fold']['p_one_sided_positive'], 4)}).
  Arm-level routing (the T2 lesson) separates the three VERDICTS from each
  other but says nothing about which arm owns a verdict when the full and
  clean readings disagree. The full arm owns it here, as the registered
  primary, and the disagreement is reported — but the line should pin the
  rule rather than leave it to the executor. Both readings agree on the
  thing that matters: the taste coordinate is not a surviving carrier.

## 10. Compliance (R-G block)

- **Label governance:** labels opened once, inside `stage_joint`, after the
  config hash was stamped; run-log proof in §1. No per-user trait value is
  reported here or persisted outside the gitignored intermediates.
- **Corpus-level only:** no person claim. r ≈ 0.05 is a cohort-level
  coupling orders of magnitude below individual-level usefulness.
- **Interpreter:** {p0['environment']['python_version']} / numpy
  {p0['environment']['numpy']} / pandas {p0['environment']['pandas']} on
  {p0['environment']['platform']}.
- **Provenance:** SR1 harness `{g0['sha256']['sr1'][:16]}…`, T2
  `{g0['sha256']['t2'][:16]}…`, T3 `{g0['sha256']['t3'][:16]}…`, T1 core
  `{g0['sha256']['t1_core'][:16]}…`, selection.npz
  `{g0['sha256']['sr1_selection_npz'][:16]}…`.
- **Stage wall time (s):** part0 {p0['seconds']:.1f}, pilot
  {pil['seconds']:.1f}, joint {full['seconds']:.1f}, clean
  {clean['seconds']:.1f}, finalize {v['seconds']:.1f} — all under the
  600 s ceiling.
"""
    scan = tt.id_leak_scan(body)
    body += (f"- **ID-leak scan:** {scan['n_tokens_scanned']} tokens checked "
             f"against all {scan['n_cohort_ids']} cohort identifiers — "
             f"{scan['n_hits']} hits, "
             f"**{'PASS' if scan['PASS'] else 'FAIL'}**.\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(body, encoding="utf-8")
    write_json(OUT / "report_scan.json", {"id_leak_scan": scan,
                                          "report": rel(REPORT),
                                          "chars": len(body)})
    _log("report_done", id_leak_pass=scan["PASS"])
    print(f"report written {rel(REPORT)}  chars={len(body)}  "
          f"id_leak_hits={scan['n_hits']} PASS={scan['PASS']}  "
          f"{time.time() - t0:.1f}s")
    if not scan["PASS"]:
        raise SystemExit("ID-leak scan FAILED")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["part0", "pilot", "joint", "clean",
                                      "finalize", "report"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": stage_part0, "pilot": stage_pilot, "joint": stage_joint,
     "clean": stage_clean, "finalize": stage_finalize,
     "report": stage_report}[args.stage](args)


if __name__ == "__main__":
    main()
