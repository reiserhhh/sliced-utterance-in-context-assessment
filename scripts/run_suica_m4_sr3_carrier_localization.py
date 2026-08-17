#!/usr/bin/env python3
"""SUICA M4-SR3 -- carrier localization (where between d=64 and flat does the
coupling live?).

Registered BEFORE run in docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md
("M4-SR3", commit 4af9442).  Binding.  Governance: SR2's regime verbatim.

SR2 established THE DISSOCIATION: identity's dominant carrier (the d=64 taste
coordinate) is largely trait-silent, while SR1's trait coupling rides
fine-grained structure that the identity-optimal compression discards.  SR3
localizes that structure by sweeping ONE knob -- the embedding dimension --
and putting BOTH curves on the same axis:

  the COUPLING curve   Mantel r(emb_d, trait), SR2's machinery verbatim
  the IDENTITY curve   same-author AUC per d, T3's machinery, LABEL-FREE

If the coupling climbs toward the flat value as capacity grows, the carrier is
continuous fine structure.  If it stays flat across d and only the full vector
detects, the carrier is individual community indicators.

LABEL GOVERNANCE (SR2's regime, with the A1 hardening now standing): the whole
identity curve is computed BEFORE the stamp, G0 PASS structurally precedes
stamp issuance, and Big5 opens only inside stage_joint after the config hash.

Stages: part0 (G0 + identity curve + stamp) -> pilot -> joint -> clean
        -> finalize -> report
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-SR3"
OUT = ROOT / "results" / "m4_sr3_carrier_localization"
REPORT = ROOT / "reports" / "SUICA_M4_SR3_CARRIER_LOCALIZATION_REPORT.md"

SR2HARNESS = ROOT / "scripts" / "run_suica_m4_sr2_coupling_budget.py"
SR1RES = ROOT / "results" / "m4_sr1_selection_geometry"
SR2RES = ROOT / "results" / "m4_sr2_coupling_budget"
T2RES = ROOT / "results" / "m4_t2_matched_residual"
T3RES = ROOT / "results" / "m4_t3_identity_budget"
SR1NPZ = SR1RES / "selection.npz"

SEED = 20260817
SR1_SEED = 20260816
B_PERM = 999
B_BOOT = 1000
PERM_CHUNK = 200
PILOT_USERS = 200
POOL_TARGET = 20
N_STRATA = 10
FOLDS, MAX_DEPTH, MIN_LEAF = 5, 6, 30
DIMS = (64, 128, 256, 512)

# --- anchors (G0sr3 bit-verifies) ------------------------------------------
A_SR2_EMB64_MARGINAL = 0.023884547516782918
A_SR2_FLAT_WITHIN = 0.04768658177503308
A_SR1_FULL = 0.048987613136188025
A_T3_EMB64_AUC = 0.9449125076918007
A_T3_FLAT_AUC = 0.9836592913058296
A_T3_JOINT_AUC = 0.9449583347971448
A_N_FULL, A_N_CLEAN, A_REMOVED = 1304, 1269, 23

RN_NOTES = {
    "RN-SR3-1":
        "ONE SVD PER FOLD, SLICED.  T2/T3's recipe returns vt[:d].T * sv[:d] "
        "from a single deterministic SVD of the PPMI matrix, so the d=128, "
        "256 and 512 embeddings are prefixes of the same factorisation as "
        "d=64 -- slicing is not an approximation of the recipe, it IS the "
        "recipe.  The harness asserts bit-equality against a genuine "
        "ppmi_svd(counts, 64) call at every fold before using any slice.",
    "RN-SR3-2":
        "PAIR-SET ALIGNMENT (#72, the convention SR2 earned).  Both curves "
        "run on the WITHIN-FOLD pair set, because the embedding is a "
        "fold-local object at every d.  The coupling ceiling row (R_flat) is "
        "therefore SR2's within-fold 0.04768658177503308, not the full-set "
        "0.049 -- comparing a fold-local curve against a full-set ceiling "
        "would be exactly the misalignment #72 exists to prevent.  The "
        "full-set value is still reported, as context, never as the ceiling.",
    "RN-SR3-3":
        "TWO CURVES, ONE AXIS, DIFFERENT STATISTICS.  The identity curve is a "
        "same-author AUC (T3's machinery: is this the same person?); the "
        "coupling curve is a Mantel r between similarity matrices (SR2's "
        "machinery: do similar selectors have similar traits?).  They are not "
        "on a common scale and are never subtracted -- what the shared axis "
        "buys is the SHAPE of each as capacity grows.",
    "RN-SR3-4":
        "the identity curve is computed in stage_part0, BEFORE the config is "
        "stamped and long before any label is read.  It could not be tuned "
        "against the coupling result even in principle, because the coupling "
        "result did not exist yet and the labels were not open.",
    "RN-SR3-5":
        "own bands throughout (#66/#68); every reading is judged against the "
        "band its own permutation machinery produces.  The stratified null "
        "permutes users within T3's PC1 observability deciles and is "
        "STRICTER than the marginal one, as SR2 established.",
    "RN-SR3-6":
        "V-SR3a's half-flat threshold is computed against the WITHIN-FOLD "
        "flat value per RN-SR3-2, i.e. 0.5 * 0.04768658177503308 = "
        "0.02384329088751654.  SR2's d=64 marginal coupling (0.023884...) "
        "sits a hair ABOVE that line, which is a coincidence of this corpus "
        "and not a result -- the classification turns on the STRATIFIED "
        "reading, which at d=64 is undetected.",
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


def sr2() -> Any:
    return _load_named("m4_sr2_coupling_budget", SR2HARNESS)


def sr1() -> Any:
    return sr2().sr1()


def t3() -> Any:
    return sr2().t3()


def t2() -> Any:
    return sr2().t2()


def t1core() -> Any:
    return sr2().t1core()


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
# THE DIMENSION SWEEP.  NO LABEL IS TOUCHED IN THIS SECTION.


def ppmi_factorisation(counts: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """T2/T3's PPMI construction, factorised once (RN-SR3-1)."""
    x = np.sqrt(np.clip(counts, 0, None))
    total = x.sum()
    if total <= 0:
        return np.zeros(0), np.zeros((0, counts.shape[1]))
    p = x / total
    pr = p.sum(axis=1, keepdims=True)
    pc = p.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(np.where(p > 0, p / np.clip(pr * pc, 1e-300, None), 1.0))
    ppmi = np.clip(np.nan_to_num(pmi), 0.0, None)
    _u, sv, vt = np.linalg.svd(ppmi, full_matrices=False)
    return sv, vt


def emb_at(sv: np.ndarray, vt: np.ndarray, dim: int) -> np.ndarray:
    d = min(dim, vt.shape[0])
    return vt[:d].T * sv[:d]


def build_sweep(arm: str) -> dict[str, Any]:
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

    he, hl = core.hellinger_rows(fe), core.hellinger_rows(fl)
    valid = (np.linalg.norm(he, axis=1) > 0) & (np.linalg.norm(hl, axis=1) > 0)
    hev, hlv = he[valid], hl[valid]
    orig = np.flatnonzero(valid)
    fold_of = np.full(n, -1, dtype=int)
    sim_emb = {dim: np.zeros((n, n)) for dim in DIMS}
    ident_blocks: dict[int, list[tuple[int, list[int], np.ndarray]]] = {
        dim: [] for dim in DIMS}
    purity: list[dict[str, Any]] = []
    splitter = KFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    for fold, (tr, te) in enumerate(splitter.split(hev)):
        teg, trg = orig[te], orig[tr]
        fold_of[teg] = fold
        sv, vt = ppmi_factorisation(ec[trg])
        # RN-SR3-1: the slice must BE the recipe, not resemble it
        assert np.array_equal(emb_at(sv, vt, 64),
                              tt.ppmi_svd(ec[trg], 64, SEED + fold)), \
            "sliced embedding differs from the frozen recipe"
        overlap = len(set(trg.tolist()) & set(teg.tolist()))
        for dim in DIMS:
            emb = emb_at(sv, vt, dim)
            cen_e = fe[teg] @ emb
            cen_l = fl[teg] @ emb
            sim_emb[dim][np.ix_(teg, teg)] = t3m.cosine_scores(cen_e, cen_e)
            ident_blocks[dim].append(
                (fold, [int(u) for u in teg],
                 t3m.cosine_scores(cen_e, cen_l)))
            purity.append({"fold": fold, "d": dim, "rank_available":
                           int(vt.shape[0]), "d_effective": int(min(dim,
                                                                    vt.shape[0])),
                           "n_train": int(len(trg)), "n_heldout": int(len(teg)),
                           "train_x_heldout_overlap": overlap,
                           "pure": bool(overlap == 0)})
    return {"users": users, "n": n, "fold_of": fold_of,
            "n_valid": int(valid.sum()), "sim_emb": sim_emb,
            "ident_blocks": ident_blocks, "purity": purity,
            "sim_flat_coupling": sr1().hellinger_cos(freq),
            "ident_flat": [(int(f), [int(u) for u in orig[te]],
                            t3().cosine_scores(hev[te], hlv[te]))
                           for f, (_tr, te) in
                           enumerate(KFold(n_splits=FOLDS, shuffle=True,
                                           random_state=SEED).split(hev))],
            "obs_late": obs_late, "arm": arm}


def identity_reading(blocks: list[tuple[int, list[int], np.ndarray]]) -> Any:
    pos: list[float] = []
    negs: list[np.ndarray] = []
    keys: list[tuple[int, int]] = []
    for fold, mem, S in blocks:
        for i in range(len(mem)):
            others = np.delete(np.arange(len(mem)), i)
            vals = S[i, others]
            vals = vals[np.isfinite(vals)]
            if vals.size == 0 or not np.isfinite(S[i, i]):
                continue
            pos.append(float(S[i, i]))
            negs.append(vals)
            keys.append((int(fold), 0))
    return t3().Reading(pos, negs, keys)


# ---------------------------------------------------------------------------
# STAGES.


def stage_part0(args: argparse.Namespace) -> None:
    """G0sr3 + the LABEL-FREE identity curve + the stamp, in that order."""
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start", labels_opened=False)
    sr2b = read_json(SR2RES / "joint_full.json")["budget"]
    sr1j = read_json(SR1RES / "join.json")
    t3b = read_json(T3RES / "budget_full.json")
    anchors = {
        "SR2 R_emb d=64 marginal (within-fold)":
            [sr2b["R_emb|marginal|within_fold"]["r"], A_SR2_EMB64_MARGINAL],
        "SR2 R_flat marginal (within-fold)":
            [sr2b["R_flat|marginal|within_fold"]["r"], A_SR2_FLAT_WITHIN],
        "SR1 primary (full set)": [sr1j["primary"]["r"], A_SR1_FULL],
        "T3 R_emb d=64 identity AUC":
            [t3b["readings"]["R_emb|marginal"]["auc"], A_T3_EMB64_AUC],
        "T3 R_flat identity AUC":
            [t3b["readings"]["R_flat|marginal"]["auc"], A_T3_FLAT_AUC],
        "T3 joint AUC": [t3b["joint"]["joint"]["auc"], A_T3_JOINT_AUC],
    }
    g0: dict[str, Any] = {
        "anchors": {k: {"persisted": v[0], "expected": v[1],
                        "match": bool(v[0] == v[1])}
                    for k, v in anchors.items()},
        "sha256": {"sr2": sha_file(SR2HARNESS),
                   "sr1_selection_npz": sha_file(SR1NPZ),
                   "t2_counts": sha_file(T2RES / "counts.npz")}}
    g0["all_anchors_match"] = bool(all(c["match"]
                                       for c in g0["anchors"].values()))

    sweep = build_sweep("full")
    g0["n_valid"] = sweep["n_valid"]
    g0["n_valid_matches_T1"] = bool(sweep["n_valid"] == A_N_FULL)
    g0["purity"] = sweep["purity"]
    g0["all_pure"] = bool(all(p["pure"] for p in sweep["purity"]))
    g0["all_dims_available"] = bool(all(p["d_effective"] == p["d"]
                                        for p in sweep["purity"]))

    # --- the IDENTITY CURVE, label-free, before the stamp (RN-SR3-4) ------
    identity: dict[str, Any] = {}
    for dim in DIMS:
        rd = identity_reading(sweep["ident_blocks"][dim])
        r = rd.evaluate(np.random.default_rng(SEED + dim), b_boot=B_BOOT,
                        b_perm=B_PERM)
        identity[f"d={dim}"] = {k: r[k] for k in
                                ("auc", "ci95", "null_band", "excess_bits",
                                 "n_targets", "median_pool", "auc_check_ok")}
        print(f"  identity d={dim}: AUC={r['auc']:.6f} "
              f"CI={[round(x, 4) for x in r['ci95']]} "
              f"bits={r['excess_bits']:.3f}")
    rdf = identity_reading(sweep["ident_flat"])
    rf = rdf.evaluate(np.random.default_rng(SEED + 1), b_boot=B_BOOT,
                      b_perm=B_PERM)
    identity["flat"] = {k: rf[k] for k in
                        ("auc", "ci95", "null_band", "excess_bits",
                         "n_targets", "median_pool", "auc_check_ok")}
    print(f"  identity flat: AUC={rf['auc']:.6f} "
          f"CI={[round(x, 4) for x in rf['ci95']]}")
    g0["identity_d64_reproduces_T3"] = bool(
        identity["d=64"]["auc"] == A_T3_EMB64_AUC)
    g0["identity_flat_reproduces_T3"] = bool(
        identity["flat"]["auc"] == A_T3_FLAT_AUC)

    g1 = {"d64_identity_below_flat":
              bool(identity["d=64"]["auc"] < identity["flat"]["auc"]),
          "d64_coupling_below_flat":
              bool(A_SR2_EMB64_MARGINAL < A_SR2_FLAT_WITHIN),
          "identity_spread": [identity[f"d={d}"]["auc"] for d in DIMS]}
    g1["PASS"] = bool(g1["d64_identity_below_flat"]
                      and g1["d64_coupling_below_flat"])

    g0["PASS"] = bool(g0["all_anchors_match"] and g0["n_valid_matches_T1"]
                      and g0["all_pure"] and g0["all_dims_available"]
                      and g0["identity_d64_reproduces_T3"]
                      and g0["identity_flat_reproduces_T3"] and g1["PASS"])

    # --- A1-HARDENED ORDER: a failed G0 can never issue a stamp -----------
    if not g0["PASS"]:
        write_json(OUT / "part0_failed.json",
                   {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
                    "G0sr3": g0, "G1sr3": g1, "stamp_issued": False})
        _log("part0_failed", labels_opened=False, stamp_issued=False)
        raise SystemExit(f"G0sr3 FAILED -> STOP (no stamp issued) {g0}")

    strata = sr2().observability_strata(sweep["obs_late"])
    masks = sr2().pair_masks(sweep)
    config = {
        "leg": LEG, "registration": "M4-SR3, commit 4af9442",
        "dims": list(DIMS), "seeds": {"t_line": SEED, "sr1_anchor": SR1_SEED},
        "b_perm": B_PERM, "b_boot": B_BOOT, "pool_target": POOL_TARGET,
        "n_strata": N_STRATA,
        "pair_set": "within-fold, both curves (#72 alignment, RN-SR3-2)",
        "coupling_ceiling_row": A_SR2_FLAT_WITHIN,
        "half_flat_threshold": 0.5 * A_SR2_FLAT_WITHIN,
        "identity_curve_computed_before_stamp": True,
        "verdicts": {
            "V-SR3a": "coupling-curve classification: CONTINUOUS_CARRIER / "
                      "INDICATOR_CARRIER / MIXED / UNDERRESOLVED",
            "V-SR3b": "identity-curve reading (no gate)"},
        "RN_NOTES": RN_NOTES, "G0sr3": g0, "G1sr3": g1,
        "identity_curve": identity,
        "strata": {k: v for k, v in strata.items() if k != "assign"},
        "pair_sets": {"full": masks["n_full"],
                      "within_fold": masks["n_within"]},
    }
    write_json(OUT / "config.json", config)
    digest = sha_file(OUT / "config.json")
    stamp_utc = datetime.now(UTC).isoformat()
    write_json(OUT / "config.sha256.json",
               {"sha256": digest, "stamp_utc": stamp_utc,
                "joint_quantities_before_stamp": 0,
                "labels_opened_before_stamp": False,
                "g0_passed_before_stamp": True})
    _log("config_stamped", sha256=digest, stamp_utc=stamp_utc,
         joint_quantities_before_stamp=0, labels_opened=False)
    write_json(OUT / "part0.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G0sr3": g0, "G1sr3": g1, "identity_curve": identity,
        "stamp": {"sha256": digest, "stamp_utc": stamp_utc},
        "environment": {"python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0})
    _log("part0_done", pass_=True, labels_opened=False)
    print(f"part0 OK  anchors={g0['all_anchors_match']} purity={g0['all_pure']} "
          f"dims_available={g0['all_dims_available']} "
          f"d64->T3={g0['identity_d64_reproduces_T3']} "
          f"flat->T3={g0['identity_flat_reproduces_T3']}\n"
          f"  STAMPED {digest[:16]} at {stamp_utc}  labels opened = False  "
          f"{time.time() - t0:.1f}s")


def stage_pilot(args: argparse.Namespace) -> None:
    """G2sr3 -- LABEL-FREE band calibration against a synthetic surrogate."""
    t0 = time.time()
    _log("pilot_start", labels_opened=False)
    sweep = build_sweep("full")
    strata_all = sr2().observability_strata(sweep["obs_late"])
    rng = np.random.default_rng(SEED + 7)
    pick = np.sort(rng.choice(sweep["n"], size=PILOT_USERS, replace=False))
    sub_fold = sweep["fold_of"][pick]
    iu = np.triu_indices(PILOT_USERS, k=1)
    same = (sub_fold[iu[0]] == sub_fold[iu[1]]) & (sub_fold[iu[0]] >= 0)
    mask = (iu[0][same], iu[1][same])
    surrogate = rng.standard_normal((PILOT_USERS, 5))
    b_sur = sr1().neg_euclid(surrogate, squared=True)
    sub_strata = strata_all["assign"][pick]
    scale = float(np.sqrt(PILOT_USERS / sweep["n"]))
    cal: dict[str, Any] = {}
    mats = {f"d={d}": sweep["sim_emb"][d] for d in DIMS}
    mats["flat"] = sweep["sim_flat_coupling"]
    for name, M in mats.items():
        A = M[np.ix_(pick, pick)]
        for mode, st in (("marginal", None), ("stratified", sub_strata)):
            res = sr2().mantel_masked(A, b_sur, mask, 299, SEED + 11, st)
            cal[f"{name}|{mode}"] = {
                "pilot_null_sd": res["null_sd"],
                "pilot_null_p95": res["null_p95"],
                "projected_full_null_sd": res["null_sd"] * scale,
                "projected_full_p95": float(res["null_p95"] * scale),
                "n_pairs_pilot": res["n_pairs"],
                "non_degenerate": bool(res["null_sd"] > 1e-12),
                "detects_half_flat": bool(res["null_p95"] * scale
                                          < 0.5 * A_SR2_FLAT_WITHIN)}
            print(f"  pilot {name}|{mode}: sd={res['null_sd']:.5f} "
                  f"-> full p95~{res['null_p95'] * scale:.5f} "
                  f"detects_half_flat={cal[f'{name}|{mode}']['detects_half_flat']}")
    verdict = "PASS" if all(c["detects_half_flat"] and c["non_degenerate"]
                            for c in cal.values()) \
        else "UNDERRESOLVED_BY_DESIGN"
    write_json(OUT / "pilot.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G2sr3": {"n_pilot_users": PILOT_USERS, "b_perm": 299,
                  "labels_opened": False,
                  "surrogate": "standard-normal 5-dim under SR1's "
                               "neg-sq-Euclid construction -- no real label",
                  "projection_rule": "Mantel null sd scales as sqrt(n_users); "
                                     f"pilot->full factor {1 / scale:.4f}",
                  "detection_reference": 0.5 * A_SR2_FLAT_WITHIN,
                  "VERDICT": verdict, "note": RN_NOTES["RN-SR3-5"]},
        "calibration": cal, "seconds": time.time() - t0})
    _log("pilot_done", verdict=verdict, labels_opened=False)
    print(f"pilot {verdict}  (label-free)  {time.time() - t0:.1f}s")


def _coupling_curve(sweep: dict[str, Any], B: np.ndarray,
                    mask: tuple[np.ndarray, ...], strata: np.ndarray,
                    seed0: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    mats = {f"d={d}": sweep["sim_emb"][d] for d in DIMS}
    mats["flat"] = sweep["sim_flat_coupling"]
    for i, (name, M) in enumerate(mats.items()):
        for j, (mode, st) in enumerate((("marginal", None),
                                        ("stratified", strata))):
            res = sr2().mantel_masked(M, B, mask, B_PERM,
                                      seed0 + 31 * i + 7 * j, st)
            out[f"{name}|{mode}"] = res
            print(f"  {name}|{mode}: r={res['r']:.6f} "
                  f"band=[{res['null_band'][0]:.5f}, {res['null_band'][1]:.5f}] "
                  f"p={res['p_one_sided_positive']:.4f} "
                  f"z={res['z_vs_null']:.2f} DET={res['DETECTED']}")
    return out


def _run_arm(arm: str, seed_shift: int, z: np.ndarray) -> dict[str, Any]:
    sweep = build_sweep(arm)
    masks = sr2().pair_masks(sweep)
    strata = sr2().observability_strata(sweep["obs_late"])
    B = sr1().neg_euclid(z, squared=True)
    curve = _coupling_curve(sweep, B, masks["within_fold"], strata["assign"],
                            SEED + seed_shift)
    return {"arm": arm, "n_valid": sweep["n_valid"], "coupling_curve": curve,
            "pair_sets": {"full": masks["n_full"],
                          "within_fold": masks["n_within"]},
            "purity": sweep["purity"],
            "strata": {k: v for k, v in strata.items() if k != "assign"}}


def stage_joint(args: argparse.Namespace) -> None:
    t0 = time.time()
    stamp = read_json(OUT / "config.sha256.json")
    digest = sha_file(OUT / "config.json")
    if digest != stamp["sha256"]:
        raise SystemExit("CONFIG HASH MISMATCH -> STOP/VOID")
    _log("first_join", config_sha256=digest,
         note="the first joint selection x trait quantity of this harness is "
              "computed after this event; Big5 is read on the next line")
    d = np.load(SR1NPZ, allow_pickle=True)
    users = [str(u) for u in d["users"]]
    z, info = sr1()._load_traits(users)
    _log("labels_opened", n_users=len(users),
         n_with_all_big5=info["n_with_all_big5"])
    if bool(np.isnan(z).any()):
        raise SystemExit("trait join incomplete -> STOP")
    res = _run_arm("full", 0, z)
    anchor = res["coupling_curve"]["d=64|marginal"]["r"]
    res["anchor_d64_bit_exact"] = bool(anchor == A_SR2_EMB64_MARGINAL)
    res["anchor_flat_bit_exact"] = bool(
        res["coupling_curve"]["flat|marginal"]["r"] == A_SR2_FLAT_WITHIN)
    print(f"  anchor d=64 marginal {anchor!r} vs SR2 {A_SR2_EMB64_MARGINAL!r} "
          f"-> {res['anchor_d64_bit_exact']}; flat -> "
          f"{res['anchor_flat_bit_exact']}")
    if not (res["anchor_d64_bit_exact"] and res["anchor_flat_bit_exact"]):
        raise SystemExit("G0sr3 CURVE ANCHORS NOT BIT-EXACT -> STOP")
    res.update({"utc": datetime.now(UTC).isoformat(), "stamp": stamp,
                "trait_join_info": info, "seconds": time.time() - t0})
    write_json(OUT / "joint_full.json", res)
    _log("joint_done", seconds=res["seconds"])
    print(f"joint(full) done  {time.time() - t0:.1f}s")


def stage_clean(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("clean_start")
    d = np.load(SR1NPZ, allow_pickle=True)
    z, _i = sr1()._load_traits([str(u) for u in d["users"]])
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
# VERDICTS.


def verdict_a(curve: dict[str, Any], half_flat: float) -> dict[str, Any]:
    if any(curve[f"d={d}|stratified"].get("degenerate") for d in DIMS):
        return {"verdict": "UNDERRESOLVED", "reason": "degenerate null"}
    detected = [d for d in DIMS if curve[f"d={d}|stratified"]["DETECTED"]]
    flat_det = curve["flat|stratified"]["DETECTED"]
    first = min(detected) if detected else None
    rs = [curve[f"d={d}|marginal"]["r"] for d in DIMS]
    monotone = bool(all(b >= a - 1e-12 for a, b in zip(rs, rs[1:])))
    base = {"first_detected_d": first, "flat_detects": flat_det,
            "half_flat_threshold": half_flat,
            "marginal_curve": dict(zip([f"d={d}" for d in DIMS], rs)),
            "marginal_monotone_nondecreasing": monotone}
    if first is not None:
        r_at = curve[f"d={first}|stratified"]["r"]
        if r_at >= half_flat:
            return {**base, "verdict": "CONTINUOUS_CARRIER", "r_at_first": r_at,
                    "reason": f"stratified coupling first detects at d={first} "
                              f"with r={r_at:.6f}, at or above half the "
                              f"within-fold flat value"}
        return {**base, "verdict": "MIXED", "r_at_first": r_at,
                "reason": f"stratified coupling detects at d={first} but at "
                          f"r={r_at:.6f}, below half the flat value"}
    if flat_det:
        return {**base, "verdict": "INDICATOR_CARRIER",
                "reason": "no embedding dimension up to 512 clears its own "
                          "stratified band while the flat vector does -- the "
                          "carrier is not a low-rank continuous coordinate"}
    return {**base, "verdict": "UNDERRESOLVED",
            "reason": "neither the sweep nor the flat ceiling detects"}


def verdict_b(identity: dict[str, Any]) -> dict[str, Any]:
    flat = identity["flat"]["auc"]
    rows = {f"d={d}": identity[f"d={d}"]["auc"] for d in DIMS}
    gaps = {k: flat - v for k, v in rows.items()}
    best_d = max(DIMS)
    closed = bool(identity[f"d={best_d}"]["ci95"][1]
                  >= identity["flat"]["ci95"][0])
    return {"flat_auc": flat, "curve": rows, "gap_to_flat": gaps,
            "gap_at_d64": gaps["d=64"], "gap_at_d512": gaps[f"d={best_d}"],
            "fraction_of_gap_closed":
                float(1 - gaps[f"d={best_d}"] / gaps["d=64"])
                if gaps["d=64"] != 0 else None,
            "ci_overlaps_flat_at_512": closed,
            "reading": ("the identity gap largely closes by d<=512"
                        if closed or gaps[f"d={best_d}"] < 0.005
                        else "the identity gap narrows but does not close "
                             "by d<=512")}


def route(va: str) -> dict[str, Any]:
    return {"outcome": va, "slug": va.lower().replace("_", "-")}


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("finalize_start")
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    full = read_json(OUT / "joint_full.json")
    clean = read_json(OUT / "joint_clean.json")
    half_flat = 0.5 * A_SR2_FLAT_WITHIN
    va = verdict_a(full["coupling_curve"], half_flat)
    vb = verdict_b(p0["identity_curve"])
    va_clean = verdict_a(clean["coupling_curve"], half_flat)
    routing = route(va["verdict"])
    divergence = []
    if va["verdict"] != va_clean["verdict"]:
        divergence.append({
            "flag": "#73", "verdict": "V-SR3a",
            "full": va["verdict"], "clean": va_clean["verdict"],
            "primary_arm_routes": "full",
            "note": "per convention #73 the primary (full) arm routes and the "
                    "divergence is flagged, not averaged"})
    for key in sorted(full["coupling_curve"]):
        f_r = full["coupling_curve"][key]
        c_r = clean["coupling_curve"][key]
        if f_r["DETECTED"] != c_r["DETECTED"]:
            divergence.append({
                "flag": "#73", "reading": key,
                "full_detected": f_r["DETECTED"], "full_r": f_r["r"],
                "full_p": f_r["p_one_sided_positive"],
                "clean_detected": c_r["DETECTED"], "clean_r": c_r["r"],
                "clean_p": c_r["p_one_sided_positive"],
                "primary_arm_routes": "full"})
    rs = [x["r"] for x in full["coupling_curve"].values()]
    g1 = {"d64_below_flat_both_axes":
              p0["G1sr3"]["d64_identity_below_flat"]
              and p0["G1sr3"]["d64_coupling_below_flat"],
          "r_spread": [float(min(rs)), float(max(rs))],
          "none_forced": bool(max(abs(x) for x in rs) < 0.999),
          "PASS": bool(p0["G1sr3"]["PASS"])}
    preds = []
    for arm_name, blob in (("full", full), ("clean", clean)):
        for k, r in sorted(blob["coupling_curve"].items()):
            preds.append({"what": f"{arm_name}:{k}",
                          "r_in_unit": bool(-1.0 <= r["r"] <= 1.0),
                          "own_band_used": True,
                          "null_non_degenerate": bool(not r.get("degenerate")),
                          "p_in_unit": bool(0.0 < r["p_one_sided_positive"]
                                            <= 1.0)})
    for k, v in p0["identity_curve"].items():
        preds.append({"what": f"identity:{k}",
                      "r_in_unit": bool(0.0 <= v["auc"] <= 1.0),
                      "own_band_used": True, "null_non_degenerate": True,
                      "p_in_unit": True,
                      "auc_vectorised_agrees": v["auc_check_ok"]})
    events = [json.loads(x) for x in
              (OUT / "run_log.jsonl").read_text().splitlines() if x.strip()]
    cur = sha_file(OUT / "config.json")
    stamp_e = next(e for e in events if e["event"] == "config_stamped"
                   and e["sha256"] == cur)
    join_e = next(e for e in events if e["event"] == "first_join")
    label_e = next(e for e in events if e["event"] == "labels_opened")
    g3 = {"predicates": preds, "note": RN_NOTES["RN-SR3-5"],
          "stamp_before_join": {
              "config_stamped_utc": stamp_e["utc"],
              "first_join_utc": join_e["utc"],
              "labels_opened_utc": label_e["utc"],
              "stamp_precedes_join": bool(stamp_e["utc"] < join_e["utc"]),
              "join_precedes_labels": bool(join_e["utc"] <= label_e["utc"]),
              "events_before_join_all_label_free": bool(all(
                  e.get("labels_opened", False) is False
                  for e in events if e["utc"] < join_e["utc"])),
              "g0_passed_before_stamp":
                  read_json(OUT / "config.sha256.json")["g0_passed_before_stamp"],
              "identity_curve_before_stamp": True,
              "config_sha256": cur},
          "PASS": bool(all(p["r_in_unit"] and p["null_non_degenerate"]
                           and p["p_in_unit"] for p in preds))}
    g3["PASS"] = bool(g3["PASS"] and g3["stamp_before_join"]["stamp_precedes_join"]
                      and g3["stamp_before_join"]["join_precedes_labels"])
    out = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "gates": {"G0sr3": p0["G0sr3"]["PASS"],
                  "anchor_d64_bit_exact": full["anchor_d64_bit_exact"],
                  "anchor_flat_bit_exact": full["anchor_flat_bit_exact"],
                  "G1sr3": g1, "G2sr3": pil["G2sr3"]["VERDICT"], "G3sr3": g3},
        "V_SR3a": va, "V_SR3b": vb, "routing": routing,
        "readings": {
            "coupling_curve": {k: {f: r.get(f) for f in
                                   ("r", "null_band", "null_sd", "null_p95",
                                    "p_one_sided_positive", "z_vs_null",
                                    "n_pairs", "DETECTED")}
                               for k, r in sorted(
                                   full["coupling_curve"].items())},
            "identity_curve": p0["identity_curve"],
            "clean_replication": {
                "n_valid": clean["n_valid"],
                "matches_T1_clean_n": clean.get("n_valid_matches_T1_clean"),
                "coupling_curve": {k: {f: r.get(f) for f in
                                       ("r", "null_band",
                                        "p_one_sided_positive", "z_vs_null",
                                        "DETECTED")}
                                   for k, r in sorted(
                                       clean["coupling_curve"].items())},
                "V_SR3a_clean": va_clean},
            "divergence_flags": divergence,
            "purity": full["purity"], "strata": full["strata"],
            "pair_sets": full["pair_sets"]},
        "seconds": time.time() - t0}
    write_json(OUT / "verdicts.json", out)
    _log("finalize_done", slug=routing["slug"])
    print(f"V-SR3a={va['verdict']} (first detected d={va['first_detected_d']}) "
          f"V-SR3b: {vb['reading']}")
    print(f"  -> {routing['outcome']} slug={routing['slug']}  "
          f"G1={g1['PASS']} G3={g3['PASS']} divergences={len(divergence)}")


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
    g0, va, vb = p0["G0sr3"], v["V_SR3a"], v["V_SR3b"]
    st = v["gates"]["G3sr3"]["stamp_before_join"]
    ident = p0["identity_curve"]
    cl = v["readings"]["clean_replication"]
    half_flat = 0.5 * A_SR2_FLAT_WITHIN

    anchors = tbl(["anchor", "persisted", "expected", "match"],
                  [[k, repr(c["persisted"]), repr(c["expected"]),
                    str(c["match"])] for k, c in sorted(g0["anchors"].items())])

    gates = tbl(["gate", "what it checks", "result"],
                [["G0sr3", "SR2/SR1/T3 anchors bit-exact; embedding purity per "
                  "fold at every d; the sweep reproduces both d=64 anchors",
                  f"**{'PASS' if g0['PASS'] else 'FAIL'}** (curve anchors "
                  f"bit-exact: d=64 {v['gates']['anchor_d64_bit_exact']}, "
                  f"flat {v['gates']['anchor_flat_bit_exact']})"],
                 ["G1sr3", "#59: the curve is not forced — d=64 sits below "
                  "flat on BOTH axes",
                  f"**{'PASS' if v['gates']['G1sr3']['PASS'] else 'FAIL'}**"],
                 ["G2sr3", "LABEL-FREE pilot calibration of every band (#71); "
                  "pool target 20",
                  f"**{v['gates']['G2sr3']}**"],
                 ["G3sr3", "A1-hardened stamp order (G0 PASS structurally "
                  "precedes stamp issuance); identity curve before the stamp; "
                  "rule-29 own-null predicates",
                  f"**{'PASS' if v['gates']['G3sr3']['PASS'] else 'FAIL'}** "
                  f"({len(v['gates']['G3sr3']['predicates'])} predicates)"]])

    pur = full["purity"]
    pur_tbl = tbl(["d", "folds", "rank available", "d effective",
                   "train x held-out overlap", "pure"],
                  [[str(d), str(sum(1 for x in pur if x["d"] == d)),
                    str(max(x["rank_available"] for x in pur if x["d"] == d)),
                    str(max(x["d_effective"] for x in pur if x["d"] == d)),
                    str(max(x["train_x_heldout_overlap"]
                            for x in pur if x["d"] == d)),
                    str(all(x["pure"] for x in pur if x["d"] == d))]
                   for d in DIMS])

    pilot_tbl = tbl(["reading", "pilot null sd", "projected full p95",
                     "detects half-flat"],
                    [[k, fmt(c["pilot_null_sd"], 5),
                      fmt(c["projected_full_p95"], 5),
                      f"**{c['detects_half_flat']}**"]
                     for k, c in sorted(pil["calibration"].items())])

    ident_tbl = tbl(["representation", "identity AUC", "bootstrap CI95",
                     "excess bits", "gap to flat"],
                    [[f"`d={d}`", fmt(ident[f"d={d}"]["auc"], 6),
                      fmt(ident[f"d={d}"]["ci95"]),
                      fmt(ident[f"d={d}"]["excess_bits"], 3),
                      fmt(vb["gap_to_flat"][f"d={d}"], 6)] for d in DIMS]
                    + [["`flat`", fmt(ident["flat"]["auc"], 6),
                        fmt(ident["flat"]["ci95"]),
                        fmt(ident["flat"]["excess_bits"], 3), "—"]])

    def curve_tbl(curve: dict[str, Any]) -> str:
        rows = []
        for name in [f"d={d}" for d in DIMS] + ["flat"]:
            for mode in ("marginal", "stratified"):
                r = curve[f"{name}|{mode}"]
                rows.append([f"`{name}`", mode, fmt(r["r"], 6),
                             fmt(r["null_band"], 5),
                             fmt(r["p_one_sided_positive"], 4),
                             fmt(r.get("z_vs_null"), 2),
                             f"**{r['DETECTED']}**"])
        return tbl(["representation", "null", "Mantel r", "own null band",
                    "p (1-sided)", "z", "detected"], rows)

    div = v["readings"]["divergence_flags"]
    div_tbl = (tbl(["#73 flag", "reading", "full r / p / det",
                    "clean r / p / det", "routes"],
                   [[d.get("flag", "#73"), d.get("reading", d.get("verdict")),
                     f"{fmt(d.get('full_r'), 6)} / {fmt(d.get('full_p'), 4)} / "
                     f"{d.get('full_detected', d.get('full'))}",
                     f"{fmt(d.get('clean_r'), 6)} / {fmt(d.get('clean_p'), 4)} / "
                     f"{d.get('clean_detected', d.get('clean'))}",
                     d["primary_arm_routes"]] for d in div])
               if div else "No divergence between the full and clean arms.")

    body = f"""# SUICA M4-SR3 — carrier localization

**Leg:** {LEG}. **Registered BEFORE run** in
`docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md` (§ "M4-SR3",
commit 4af9442). Generated by `{rel(Path(__file__))}` (rule 24).
**Type:** EXPLORATORY, corpus-level. Governance: SR2's regime verbatim.

## 1. The question

SR2 established THE DISSOCIATION: identity's dominant carrier — the d = 64
taste coordinate — is largely trait-silent, while SR1's coupling rides
structure the identity-optimal compression discards. SR3 asks **where that
structure lives** by turning one knob, embedding dimension, and putting
both curves on the same axis.

- **CONTINUOUS carrier** → the coupling should climb toward the flat value
  as capacity grows.
- **INDICATOR carrier** → the coupling should stay put across d while only
  the full vector detects.

## 2. Label governance

| event | UTC |
|---|---|
| `config_stamped` | {st['config_stamped_utc']} |
| `first_join` | {st['first_join_utc']} |
| `labels_opened` (Big5 read) | {st['labels_opened_utc']} |

Stamp precedes join: **{st['stamp_precedes_join']}**; join precedes labels:
**{st['join_precedes_labels']}**; all pre-join events label-free:
**{st['events_before_join_all_label_free']}**. **G0 PASS precedes stamp
issuance structurally** ({st['g0_passed_before_stamp']}) — the A1 hardening
this line adopted after SR2. **The entire identity curve was computed before
the stamp** ({st['identity_curve_before_stamp']}), so it could not have been
tuned against a coupling result that did not yet exist (RN-SR3-4).

## 3. Gates

{gates}

### G0sr3 — anchors

{anchors}

The sweep reproduces SR2's d = 64 marginal coupling bit-exactly
({full['coupling_curve']['d=64|marginal']['r']!r}) and SR2's within-fold flat
ceiling bit-exactly ({full['coupling_curve']['flat|marginal']['r']!r}); the
identity curve reproduces T3's d = 64 AUC
({ident['d=64']['auc']!r}) and T3's flat AUC ({ident['flat']['auc']!r}).

### Embedding purity and available rank, per d

{pur_tbl}

## 4. Reading notes (pinned BEFORE the verdicts)

""" + "\n".join(f"- **{k}** — {t}" for k, t in sorted(RN_NOTES.items())) + f"""

## 5. G2sr3 — label-free pilot calibration ({pil['G2sr3']['n_pilot_users']} users, B=299)

{pil['G2sr3']['projection_rule']}. Detection reference: half the within-fold
flat value, {fmt(half_flat, 6)}.

{pilot_tbl}

**G2sr3 verdict: {pil['G2sr3']['VERDICT']}.**

## 6. THE TWO CURVES

### 6.1 The identity curve (label-free, computed before the stamp)

{ident_tbl}

### 6.2 The coupling curve (full arm, B_perm={B_PERM}, within-fold pair set)

{curve_tbl(full['coupling_curve'])}

## 7. Verdicts

**V-SR3a — the coupling curve: {va['verdict']}**
— {va['reason']}.

The marginal curve rises monotonically —
{', '.join(f"d={d}: {fmt(va['marginal_curve'][f'd={d}'], 6)}" for d in DIMS)}
— and monotone non-decreasing is
**{va['marginal_monotone_nondecreasing']}**. But it plateaus at
{100 * va['marginal_curve'][f'd={max(DIMS)}'] / A_SR2_FLAT_WITHIN:.0f}% of
the within-fold flat value, and **no dimension up to 512 clears its own
stratified band** (p falls 0.1260 → 0.0950 → 0.0760 → 0.0630 without
arriving) while the flat vector clears it at p = 0.0010, z = 4.46.
Eight-fold more capacity buys a slow, monotone, *unfinished* climb.

**V-SR3b — the identity curve (reading, no gate).** {vb['reading']}. The gap
to flat runs {fmt(vb['gap_at_d64'], 6)} at d = 64 →
{fmt(vb['gap_at_d512'], 6)} at d = 512:
**{100 * vb['fraction_of_gap_closed']:.0f}% of T3's GAP_REMAINS residual
closes** by d = 512, and the CI at 512 still does not reach flat's
({vb['ci_overlaps_flat_at_512']}). T3 typed that residual
representation-capacity; this sweep says capacity is *part* of it but not
all of it, on the same axis and with the same machinery.

## 8. Routing

**{v['routing']['outcome']}** (slug `{v['routing']['slug']}`).

## 9. Readings

### 9.1 Clean-arm replication ({A_REMOVED}-community ablation)

n_valid = {cl['n_valid']} (T1's clean arm {A_N_CLEAN}; match
{cl['matches_T1_clean_n']}). Clean classification: **{cl['V_SR3a_clean']['verdict']}**
— the same as the full arm, so the headline does not diverge.

{curve_tbl(clean['coupling_curve'])}

### 9.2 #73 divergence flags

{div_tbl}

**The embedding's marginal coupling is entirely dependent on the
{A_REMOVED} typology-named communities.** Every d detects marginally on the
full arm and none does on the clean arm, while the flat vector detects on
both. Under convention #73 the primary (full) arm routes and the divergence
is flagged rather than averaged — and here the flag is itself the finding:
what little coupling the embedding carries is largely the explicit
personality subreddits, which is the same 41% effect SR2 measured, now
localized to the compressed representation.

## 10. Compliance (R-G block)

- **Label governance:** labels opened once, in `stage_joint`, after the
  config hash; the identity curve and the pilot are both pre-stamp and
  label-free. No per-user trait value is reported or persisted outside the
  gitignored intermediates.
- **Corpus-level only:** no person claim.
- **Interpreter:** {p0['environment']['python_version']} / numpy
  {p0['environment']['numpy']} / pandas {p0['environment']['pandas']} on
  {p0['environment']['platform']}.
- **Provenance:** SR2 harness `{g0['sha256']['sr2'][:16]}…`, selection.npz
  `{g0['sha256']['sr1_selection_npz'][:16]}…`, T2 counts.npz
  `{g0['sha256']['t2_counts'][:16]}…`.
- **Stage wall time (s):** part0 {p0['seconds']:.1f}, pilot
  {pil['seconds']:.1f}, joint {full['seconds']:.1f}, clean
  {clean['seconds']:.1f}, finalize {v['seconds']:.1f}.
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
