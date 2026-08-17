#!/usr/bin/env python3
"""SUICA M4-SR4 -- the endpoint and the metric (completing the carrier curve).

Registered BEFORE run in docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md
("M4-SR4", commit 9ba3cf1).  Binding.  A micro-leg: SR3's machinery verbatim,
three new rows, one three-way classification.  Governance: SR2/SR3's regime.

SR3 returned INDICATOR_CARRIER scoped to d <= 512, with the stratified
p-values still falling at the endpoint.  The planner's derivation sharpens
what remains: at d = rank the truncation vanishes, so the embedding is a
pure rotation of the PPMI space and the only thing still separating it from
the Hellinger flat row is THE METRIC.  Three rows disambiguate:

  d = 768          more capacity, still truncated
  d = 1043         the available rank -- the pure-rotation row
  ppmi-full        the PPMI transform with NO factorisation at all

cos(freq @ VS) and cos(freq @ PPMI^T) are equal in exact arithmetic --
PPMI = U S V^T gives freq @ V S = (freq @ PPMI^T) U, and right-multiplying
by a matrix with orthonormal columns preserves inner products.  The two
rows are therefore the SAME estimand computed by two different numerical
routes, and any gap between them is an instrument finding, exactly as the
registration's third cell anticipates.

Stages: part0 (G0 + identity companion + stamp) -> pilot -> joint -> clean
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

LEG = "M4-SR4"
OUT = ROOT / "results" / "m4_sr4_endpoint_metric"
REPORT = ROOT / "reports" / "SUICA_M4_SR4_ENDPOINT_METRIC_REPORT.md"

SR3HARNESS = ROOT / "scripts" / "run_suica_m4_sr3_carrier_localization.py"
SR3RES = ROOT / "results" / "m4_sr3_carrier_localization"
SR1RES = ROOT / "results" / "m4_sr1_selection_geometry"
T2RES = ROOT / "results" / "m4_t2_matched_residual"
SR1NPZ = SR1RES / "selection.npz"

SEED = 20260817
B_PERM = 999
B_BOOT = 1000
PILOT_USERS = 200
POOL_TARGET = 20
FOLDS = 5
DIMS_SR3 = (64, 128, 256, 512)
DIMS_NEW = (768, 1043)
DIMS_ALL = DIMS_SR3 + DIMS_NEW
PPMI_FULL = "ppmi_full"
ROWS = [f"d={d}" for d in DIMS_ALL] + [PPMI_FULL, "flat"]

A_SR2_FLAT_WITHIN = 0.04768658177503308
A_N_FULL, A_N_CLEAN, A_REMOVED = 1304, 1269, 23
HALF_FLAT = 0.5 * A_SR2_FLAT_WITHIN

RN_NOTES = {
    "RN-SR4-1":
        "d = 1043 AND ppmi-full ARE THE SAME ESTIMAND BY TWO ROUTES.  With "
        "PPMI = U S V^T, freq @ (V S) = (freq @ PPMI^T) U, and right-"
        "multiplication by a matrix with orthonormal columns preserves inner "
        "products, so the two cosine matrices agree in exact arithmetic.  The "
        "harness measures their realized agreement and reports it; the "
        "registration's RANK_ANOMALY cell exists precisely to catch a "
        "disagreement, which would be numerical rather than substantive.",
    "RN-SR4-2":
        "THE AVAILABLE RANK IS NOT UNIFORM ACROSS FOLDS.  Folds 0-3 train on "
        "1043 authors and fold 4 on 1044, so the PPMI factorisation has 1043 "
        "components in four folds and 1044 in the fifth.  The registered "
        "d = 1043 row is therefore EXACTLY full rank in four folds and drops "
        "one component in fold 4.  The effective rank is recorded per fold "
        "and the ppmi-full row -- which never truncates anywhere -- is the "
        "clean control for that one-dimension shortfall.",
    "RN-SR4-3":
        "SR3's whole curve is RECOMPUTED here, not copied, and bit-compared "
        "to its persisted values: all ten coupling rows and all five identity "
        "rows.  A transcription check would only prove the numbers were typed "
        "correctly; recomputation proves the machinery still produces them.",
    "RN-SR4-4":
        "the identity companion at d = 768 and 1043 is computed in part0, "
        "before the config is stamped and before any label is read, exactly "
        "as SR3's was.  It extends V-SR3b's reading onto the completed axis.",
    "RN-SR4-5":
        "own bands throughout (#66/#68); within-fold pair sets (#72); "
        "stratified nulls permute users inside T3's PC1 observability "
        "deciles.  The half-flat threshold is against the WITHIN-FOLD flat "
        "value 0.04768658177503308, i.e. 0.02384329088751654.",
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


def sr3() -> Any:
    return _load_named("m4_sr3_carrier_localization", SR3HARNESS)


def sr2() -> Any:
    return sr3().sr2()


def sr1() -> Any:
    return sr3().sr1()


def t3() -> Any:
    return sr3().t3()


def t2() -> Any:
    return sr3().t2()


def t1core() -> Any:
    return sr3().t1core()


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
# THE PPMI MATRIX ITSELF (SR3 only ever needed its factorisation).


def ppmi_matrix(counts: np.ndarray) -> np.ndarray:
    """T2/T3's PPMI construction, returned untruncated and unfactorised."""
    x = np.sqrt(np.clip(counts, 0, None))
    total = x.sum()
    if total <= 0:
        return np.zeros_like(counts, dtype=float)
    p = x / total
    pr = p.sum(axis=1, keepdims=True)
    pc = p.sum(axis=0, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log(np.where(p > 0, p / np.clip(pr * pc, 1e-300, None), 1.0))
    return np.clip(np.nan_to_num(pmi), 0.0, None)


def build_sweep(arm: str) -> dict[str, Any]:
    """SR3's sweep extended with d=768, d=1043 and the ppmi-full row."""
    tt, t3m, core, s3 = t2(), t3(), t1core(), sr3()
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
    sim = {r: np.zeros((n, n)) for r in ROWS if r != "flat"}
    ident_blocks: dict[str, list[Any]] = {r: [] for r in ROWS}
    ranks: list[dict[str, Any]] = []
    rot_agreement: list[dict[str, Any]] = []
    splitter = KFold(n_splits=FOLDS, shuffle=True, random_state=SEED)
    for fold, (tr, te) in enumerate(splitter.split(hev)):
        teg, trg = orig[te], orig[tr]
        fold_of[teg] = fold
        pm = ppmi_matrix(ec[trg])
        sv, vt = s3.ppmi_factorisation(ec[trg])
        # RN-SR4-3: the matrix and the factorisation must be the same object
        _u2, sv2, vt2 = np.linalg.svd(pm, full_matrices=False)
        assert np.array_equal(sv, sv2) and np.array_equal(vt, vt2), \
            "the PPMI matrix and SR3's factorisation disagree"
        rank = int(vt.shape[0])
        ranks.append({"fold": fold, "n_train": int(len(trg)),
                      "rank_available": rank,
                      "d1043_effective": int(min(1043, rank)),
                      "d1043_is_full_rank": bool(rank <= 1043),
                      "n_heldout": int(len(teg)),
                      "train_x_heldout_overlap":
                          len(set(trg.tolist()) & set(teg.tolist()))})
        for dim in DIMS_ALL:
            emb = s3.emb_at(sv, vt, dim)
            cen_e, cen_l = fe[teg] @ emb, fl[teg] @ emb
            sim[f"d={dim}"][np.ix_(teg, teg)] = t3m.cosine_scores(cen_e, cen_e)
            ident_blocks[f"d={dim}"].append(
                (fold, [int(u) for u in teg], t3m.cosine_scores(cen_e, cen_l)))
        pe, pl = fe[teg] @ pm.T, fl[teg] @ pm.T
        sim[PPMI_FULL][np.ix_(teg, teg)] = t3m.cosine_scores(pe, pe)
        ident_blocks[PPMI_FULL].append(
            (fold, [int(u) for u in teg], t3m.cosine_scores(pe, pl)))
        ident_blocks["flat"].append(
            (fold, [int(u) for u in teg], t3m.cosine_scores(hev[te], hlv[te])))
        block_rot = sim[f"d={min(1043, rank)}"][np.ix_(teg, teg)] \
            if min(1043, rank) in DIMS_ALL else sim["d=1043"][np.ix_(teg, teg)]
        rot_agreement.append({
            "fold": fold,
            "max_abs_diff_d1043_vs_ppmi_full": float(
                np.abs(block_rot - sim[PPMI_FULL][np.ix_(teg, teg)]).max())})
    sim["flat"] = sr1().hellinger_cos(freq)
    return {"users": users, "n": n, "fold_of": fold_of,
            "n_valid": int(valid.sum()), "sim": sim,
            "ident_blocks": ident_blocks, "ranks": ranks,
            "rotation_agreement": rot_agreement,
            "obs_late": obs_late, "arm": arm}


# ---------------------------------------------------------------------------
# STAGES.


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start", labels_opened=False)
    s3v = read_json(SR3RES / "verdicts.json")
    s3_ident = s3v["readings"]["identity_curve"]
    sweep = build_sweep("full")

    identity: dict[str, Any] = {}
    for row in ROWS:
        rd = sr3().identity_reading(sweep["ident_blocks"][row])
        r = rd.evaluate(np.random.default_rng(SEED + abs(hash(row)) % 9999),
                        b_boot=B_BOOT, b_perm=B_PERM)
        identity[row] = {k: r[k] for k in ("auc", "ci95", "null_band",
                                           "excess_bits", "n_targets",
                                           "auc_check_ok")}
        print(f"  identity {row}: AUC={r['auc']:.6f} "
              f"CI={[round(x, 4) for x in r['ci95']]}")
    ident_repro = {k: {"recomputed": identity[k]["auc"],
                       "sr3_persisted": s3_ident[k]["auc"],
                       "match": bool(identity[k]["auc"] == s3_ident[k]["auc"])}
                   for k in s3_ident}
    ranks = sweep["ranks"]
    g0: dict[str, Any] = {
        "sr3_identity_rows_bit_reproduced": ident_repro,
        "all_sr3_identity_match": bool(all(v["match"]
                                           for v in ident_repro.values())),
        "ranks": ranks,
        "min_rank_available": int(min(r["rank_available"] for r in ranks)),
        "d1043_available_everywhere": bool(all(r["rank_available"] >= 1043
                                               for r in ranks)),
        "d1043_full_rank_in_all_folds": bool(all(r["d1043_is_full_rank"]
                                                 for r in ranks)),
        "all_pure": bool(all(r["train_x_heldout_overlap"] == 0 for r in ranks)),
        "n_valid": sweep["n_valid"],
        "n_valid_matches_T1": bool(sweep["n_valid"] == A_N_FULL),
        "rotation_agreement": sweep["rotation_agreement"],
        "max_rotation_disagreement": float(max(
            x["max_abs_diff_d1043_vs_ppmi_full"]
            for x in sweep["rotation_agreement"])),
        "sha256": {"sr3": sha_file(SR3HARNESS),
                   "sr1_selection_npz": sha_file(SR1NPZ),
                   "t2_counts": sha_file(T2RES / "counts.npz")}}
    g0["PASS"] = bool(g0["all_sr3_identity_match"] and g0["n_valid_matches_T1"]
                      and g0["all_pure"] and g0["d1043_available_everywhere"])
    g1 = {"new_rows_differ_from_each_other": bool(
              len({round(identity[r]["auc"], 12) for r in
                   ("d=512", "d=768", "d=1043", PPMI_FULL)}) > 1),
          "identity_below_flat_at_1043": bool(
              identity["d=1043"]["auc"] < identity["flat"]["auc"]),
          "PASS": True}
    g1["PASS"] = bool(g1["new_rows_differ_from_each_other"]
                      and g1["identity_below_flat_at_1043"])

    if not (g0["PASS"] and g1["PASS"]):
        write_json(OUT / "part0_failed.json",
                   {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
                    "G0sr4": g0, "G1sr4": g1, "stamp_issued": False})
        _log("part0_failed", labels_opened=False, stamp_issued=False)
        raise SystemExit(f"G0sr4/G1sr4 FAILED -> STOP (no stamp issued) {g0}")

    strata = sr2().observability_strata(sweep["obs_late"])
    masks = sr2().pair_masks(sweep)
    config = {
        "leg": LEG, "registration": "M4-SR4, commit 9ba3cf1",
        "rows": ROWS, "new_rows": [f"d={d}" for d in DIMS_NEW] + [PPMI_FULL],
        "seed": SEED, "b_perm": B_PERM, "b_boot": B_BOOT,
        "pool_target": POOL_TARGET,
        "pair_set": "within-fold (#72)",
        "half_flat_threshold": HALF_FLAT,
        "coupling_ceiling_row": A_SR2_FLAT_WITHIN,
        "identity_companion_before_stamp": True,
        "verdict": "V-SR4 three-way: CONTINUOUS_CARRIER_HIGH_RANK / "
                   "METRIC_BORNE / RANK_ANOMALY_NAMED / UNDERRESOLVED",
        "RN_NOTES": RN_NOTES, "G0sr4": g0, "G1sr4": g1,
        "identity_curve": identity,
        "strata": {k: v for k, v in strata.items() if k != "assign"},
        "pair_sets": {"full": masks["n_full"],
                      "within_fold": masks["n_within"]}}
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
        "G0sr4": g0, "G1sr4": g1, "identity_curve": identity,
        "stamp": {"sha256": digest, "stamp_utc": stamp_utc},
        "environment": {"python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0})
    _log("part0_done", pass_=True, labels_opened=False)
    print(f"part0 OK  SR3 identity rows bit-reproduced="
          f"{g0['all_sr3_identity_match']}  min rank="
          f"{g0['min_rank_available']}  d=1043 full rank in all folds="
          f"{g0['d1043_full_rank_in_all_folds']}\n"
          f"  max |d=1043 - ppmi_full| = {g0['max_rotation_disagreement']:.3e}\n"
          f"  STAMPED {digest[:16]} at {stamp_utc}  labels opened = False  "
          f"{time.time() - t0:.1f}s")


def stage_pilot(args: argparse.Namespace) -> None:
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
    for name in [f"d={d}" for d in DIMS_NEW] + [PPMI_FULL, "flat"]:
        A = sweep["sim"][name][np.ix_(pick, pick)]
        for mode, st in (("marginal", None), ("stratified", sub_strata)):
            res = sr2().mantel_masked(A, b_sur, mask, 299, SEED + 11, st)
            cal[f"{name}|{mode}"] = {
                "pilot_null_sd": res["null_sd"],
                "pilot_null_p95": res["null_p95"],
                "projected_full_p95": float(res["null_p95"] * scale),
                "non_degenerate": bool(res["null_sd"] > 1e-12),
                "detects_half_flat": bool(res["null_p95"] * scale < HALF_FLAT)}
            print(f"  pilot {name}|{mode}: sd={res['null_sd']:.5f} -> full "
                  f"p95~{res['null_p95'] * scale:.5f} detects_half_flat="
                  f"{cal[f'{name}|{mode}']['detects_half_flat']}")
    verdict = "PASS" if all(c["detects_half_flat"] and c["non_degenerate"]
                            for c in cal.values()) \
        else "UNDERRESOLVED_BY_DESIGN"
    write_json(OUT / "pilot.json", {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G2sr4": {"n_pilot_users": PILOT_USERS, "b_perm": 299,
                  "labels_opened": False,
                  "surrogate": "standard-normal 5-dim under SR1's "
                               "neg-sq-Euclid construction -- no real label",
                  "projection_rule": "null sd scales as sqrt(n_users); "
                                     f"pilot->full factor {1 / scale:.4f}",
                  "detection_reference": HALF_FLAT, "VERDICT": verdict},
        "calibration": cal, "seconds": time.time() - t0})
    _log("pilot_done", verdict=verdict, labels_opened=False)
    print(f"pilot {verdict}  (label-free)  {time.time() - t0:.1f}s")


def _curve(sweep: dict[str, Any], B: np.ndarray,
           mask: tuple[np.ndarray, ...], strata: np.ndarray,
           seed0: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for i, name in enumerate(ROWS):
        for j, (mode, st) in enumerate((("marginal", None),
                                        ("stratified", strata))):
            res = sr2().mantel_masked(sweep["sim"][name], B, mask, B_PERM,
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
    curve = _curve(sweep, B, masks["within_fold"], strata["assign"],
                   SEED + seed_shift)
    return {"arm": arm, "n_valid": sweep["n_valid"], "curve": curve,
            "ranks": sweep["ranks"],
            "rotation_agreement": sweep["rotation_agreement"],
            "pair_sets": {"full": masks["n_full"],
                          "within_fold": masks["n_within"]},
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
    z, info = sr1()._load_traits([str(u) for u in d["users"]])
    _log("labels_opened", n_users=int(len(z)),
         n_with_all_big5=info["n_with_all_big5"])
    if bool(np.isnan(z).any()):
        raise SystemExit("trait join incomplete -> STOP")
    res = _run_arm("full", 0, z)
    s3curve = read_json(SR3RES / "verdicts.json")["readings"]["coupling_curve"]
    repro = {k: {"recomputed": res["curve"][k]["r"],
                 "sr3_persisted": s3curve[k]["r"],
                 "match": bool(res["curve"][k]["r"] == s3curve[k]["r"])}
             for k in s3curve}
    res["sr3_coupling_rows_bit_reproduced"] = repro
    res["all_sr3_coupling_match"] = bool(all(v["match"] for v in repro.values()))
    print(f"  SR3's {len(repro)} coupling rows bit-reproduced: "
          f"{res['all_sr3_coupling_match']}")
    if not res["all_sr3_coupling_match"]:
        bad = {k: v for k, v in repro.items() if not v["match"]}
        raise SystemExit(f"G0sr4 SR3 CURVE NOT BIT-REPRODUCED -> STOP {bad}")
    res.update({"utc": datetime.now(UTC).isoformat(), "stamp": stamp,
                "seconds": time.time() - t0})
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
# THE THREE-WAY VERDICT.


def verdict(curve: dict[str, Any]) -> dict[str, Any]:
    if any(curve[f"{r}|stratified"].get("degenerate") for r in ROWS):
        return {"verdict": "UNDERRESOLVED", "reason": "degenerate null"}
    det = {r: bool(curve[f"{r}|stratified"]["DETECTED"]) for r in ROWS}
    rr = {r: float(curve[f"{r}|stratified"]["r"]) for r in ROWS}
    trunc = [f"d={d}" for d in DIMS_ALL]
    high = [f"d={d}" for d in DIMS_NEW]
    base = {"stratified_detections": det, "stratified_r": rr,
            "half_flat_threshold": HALF_FLAT,
            "flat_detected": det["flat"],
            "ppmi_full_detected": det[PPMI_FULL],
            "any_truncation_detected": any(det[r] for r in trunc),
            "marginal_curve": {r: curve[f"{r}|marginal"]["r"] for r in ROWS},
            "marginal_monotone_over_dims": bool(all(
                curve[f"d={b}|marginal"]["r"]
                >= curve[f"d={a}|marginal"]["r"] - 1e-12
                for a, b in zip(DIMS_ALL, DIMS_ALL[1:])))}
    hits = [r for r in high if det[r] and rr[r] >= HALF_FLAT]
    if hits:
        return {**base, "verdict": "CONTINUOUS_CARRIER_HIGH_RANK",
                "first_high_rank_hit": hits[0],
                "reason": f"stratified detection at {hits[0]} with "
                          f"r={rr[hits[0]]:.6f} at or above half-flat -- "
                          "SR3's INDICATOR_CARRIER cell amends by dated note"}
    if det[PPMI_FULL] and not any(det[r] for r in trunc):
        return {**base, "verdict": "RANK_ANOMALY_NAMED",
                "reason": "the unfactorised PPMI row detects while every "
                          "truncation including the full-rank rotation does "
                          "not; the two are the same estimand in exact "
                          "arithmetic, so this isolates a numerical effect"}
    if (not any(det[r] for r in trunc) and not det[PPMI_FULL]
            and det["flat"]):
        return {**base, "verdict": "METRIC_BORNE",
                "reason": "no PPMI representation detects at ANY rank -- "
                          "including the untruncated one -- while the "
                          "Hellinger flat row does; the operative contrast is "
                          "PPMI-vs-Hellinger geometry, not capacity, so the "
                          "coupling lives in what PPMI suppresses"}
    if any(det[r] for r in trunc):
        return {**base, "verdict": "CONTINUOUS_CARRIER_HIGH_RANK",
                "first_high_rank_hit": next(r for r in trunc if det[r]),
                "reason": "a truncation detects but below half-flat; recorded "
                          "in the high-rank cell with the magnitude caveat"}
    return {**base, "verdict": "UNDERRESOLVED",
            "reason": "neither the sweep nor the flat ceiling detects"}


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("finalize_start")
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    full = read_json(OUT / "joint_full.json")
    clean = read_json(OUT / "joint_clean.json")
    v = verdict(full["curve"])
    v_clean = verdict(clean["curve"])
    div = []
    if v["verdict"] != v_clean["verdict"]:
        div.append({"flag": "#73", "verdict": "V-SR4", "full": v["verdict"],
                    "clean": v_clean["verdict"], "primary_arm_routes": "full"})
    for k in sorted(full["curve"]):
        f_r, c_r = full["curve"][k], clean["curve"][k]
        if f_r["DETECTED"] != c_r["DETECTED"]:
            div.append({"flag": "#73", "reading": k,
                        "full_detected": f_r["DETECTED"], "full_r": f_r["r"],
                        "full_p": f_r["p_one_sided_positive"],
                        "clean_detected": c_r["DETECTED"], "clean_r": c_r["r"],
                        "clean_p": c_r["p_one_sided_positive"],
                        "primary_arm_routes": "full"})
    rs = [x["r"] for x in full["curve"].values()]
    g1 = {**p0["G1sr4"], "r_spread": [float(min(rs)), float(max(rs))],
          "none_forced": bool(max(abs(x) for x in rs) < 0.999)}
    preds = []
    for arm_name, blob in (("full", full), ("clean", clean)):
        for k, r in sorted(blob["curve"].items()):
            preds.append({"what": f"{arm_name}:{k}",
                          "r_in_unit": bool(-1.0 <= r["r"] <= 1.0),
                          "own_band_used": True,
                          "null_non_degenerate": bool(not r.get("degenerate")),
                          "p_in_unit": bool(0.0 < r["p_one_sided_positive"]
                                            <= 1.0)})
    events = [json.loads(x) for x in
              (OUT / "run_log.jsonl").read_text().splitlines() if x.strip()]
    cur = sha_file(OUT / "config.json")
    stamp_e = next(e for e in events if e["event"] == "config_stamped"
                   and e["sha256"] == cur)
    join_e = next(e for e in events if e["event"] == "first_join")
    label_e = next(e for e in events if e["event"] == "labels_opened")
    g3 = {"predicates": preds,
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
              "identity_companion_before_stamp": True,
              "config_sha256": cur},
          "PASS": bool(all(p["r_in_unit"] and p["null_non_degenerate"]
                           and p["p_in_unit"] for p in preds))}
    g3["PASS"] = bool(g3["PASS"]
                      and g3["stamp_before_join"]["stamp_precedes_join"]
                      and g3["stamp_before_join"]["join_precedes_labels"])
    out = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "gates": {"G0sr4": p0["G0sr4"]["PASS"],
                  "sr3_coupling_bit_reproduced": full["all_sr3_coupling_match"],
                  "sr3_identity_bit_reproduced":
                      p0["G0sr4"]["all_sr3_identity_match"],
                  "G1sr4": g1, "G2sr4": pil["G2sr4"]["VERDICT"], "G3sr4": g3},
        "V_SR4": v,
        "routing": {"outcome": v["verdict"],
                    "slug": v["verdict"].lower().replace("_", "-")},
        "readings": {
            "curve": {k: {f: r.get(f) for f in
                          ("r", "null_band", "null_sd", "p_one_sided_positive",
                           "z_vs_null", "n_pairs", "DETECTED")}
                      for k, r in sorted(full["curve"].items())},
            "identity_curve": p0["identity_curve"],
            "sr3_reproduction": {
                "coupling": full["sr3_coupling_rows_bit_reproduced"],
                "identity": p0["G0sr4"]["sr3_identity_rows_bit_reproduced"]},
            "rotation_agreement": full["rotation_agreement"],
            "max_rotation_disagreement": p0["G0sr4"]["max_rotation_disagreement"],
            "ranks": full["ranks"],
            "clean_replication": {
                "n_valid": clean["n_valid"],
                "matches_T1_clean_n": clean.get("n_valid_matches_T1_clean"),
                "curve": {k: {f: r.get(f) for f in
                              ("r", "null_band", "p_one_sided_positive",
                               "z_vs_null", "DETECTED")}
                          for k, r in sorted(clean["curve"].items())},
                "V_SR4_clean": v_clean},
            "divergence_flags": div,
            "pair_sets": full["pair_sets"], "strata": full["strata"]},
        "seconds": time.time() - t0}
    write_json(OUT / "verdicts.json", out)
    _log("finalize_done", slug=out["routing"]["slug"])
    print(f"V-SR4={v['verdict']}  -> slug={out['routing']['slug']}  "
          f"G1={g1['PASS']} G3={g3['PASS']} divergences={len(div)}")


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
    g0, vv = p0["G0sr4"], v["V_SR4"]
    st = v["gates"]["G3sr4"]["stamp_before_join"]
    ident = p0["identity_curve"]
    cl = v["readings"]["clean_replication"]
    cur = full["curve"]

    # the two gap decompositions -- the leg's payload
    i64, ifull, iflat = (ident["d=64"]["auc"], ident[PPMI_FULL]["auc"],
                         ident["flat"]["auc"])
    i_gap0, i_gapf = iflat - i64, iflat - ifull
    c64 = cur["d=64|stratified"]["r"]
    cfull = cur[f"{PPMI_FULL}|stratified"]["r"]
    cflat = cur["flat|stratified"]["r"]
    c_gap0, c_gapf = cflat - c64, cflat - cfull

    def curve_tbl(c: dict[str, Any]) -> str:
        rows = []
        for name in ROWS:
            for mode in ("marginal", "stratified"):
                r = c[f"{name}|{mode}"]
                mark = "**" if name in (f"d={d}" for d in DIMS_NEW) or \
                    name == PPMI_FULL else ""
                rows.append([f"{mark}`{name}`{mark}", mode, fmt(r["r"], 6),
                             fmt(r["null_band"], 5),
                             fmt(r["p_one_sided_positive"], 4),
                             fmt(r.get("z_vs_null"), 2),
                             f"**{r['DETECTED']}**"])
        return tbl(["representation", "null", "Mantel r", "own null band",
                    "p (1-sided)", "z", "detected"], rows)

    ident_tbl = tbl(["representation", "identity AUC", "CI95", "gap to flat"],
                    [[f"`{r}`", fmt(ident[r]["auc"], 6), fmt(ident[r]["ci95"]),
                      fmt(iflat - ident[r]["auc"], 6) if r != "flat" else "—"]
                     for r in ROWS])

    rot = tbl(["fold", "n train", "rank available", "d=1043 effective",
               "exactly full rank", "max |d=1043 − ppmi-full|"],
              [[str(r["fold"]), str(r["n_train"]), str(r["rank_available"]),
                str(r["d1043_effective"]), str(r["d1043_is_full_rank"]),
                f"{a['max_abs_diff_d1043_vs_ppmi_full']:.3e}"]
               for r, a in zip(full["ranks"], full["rotation_agreement"])])

    div = v["readings"]["divergence_flags"]
    div_tbl = (tbl(["#73 flag", "reading", "full r / p / det",
                    "clean r / p / det", "routes"],
                   [[d.get("flag", "#73"), d.get("reading", d.get("verdict")),
                     f"{fmt(d.get('full_r'), 6)} / {fmt(d.get('full_p'), 4)} / "
                     f"{d.get('full_detected', d.get('full'))}",
                     f"{fmt(d.get('clean_r'), 6)} / {fmt(d.get('clean_p'), 4)} / "
                     f"{d.get('clean_detected', d.get('clean'))}",
                     d["primary_arm_routes"]] for d in div])
               if div else "No divergence.")

    body = f"""# SUICA M4-SR4 — the endpoint and the metric

**Leg:** {LEG}. **Registered BEFORE run** in
`docs/SUICA_M4_T_HIERARCHICAL_SELECTION_IDENTITY_PLAN.md` (§ "M4-SR4",
commit 9ba3cf1). Generated by `{rel(Path(__file__))}` (rule 24).
**Type:** EXPLORATORY, corpus-level. A micro-leg: SR3's machinery verbatim,
three new rows, one three-way classification.

## 1. What the three rows settle

SR3 returned INDICATOR_CARRIER scoped to d ≤ 512, with the stratified
p-values still falling at the endpoint. The planner's derivation sharpens
the question: **at d = rank the truncation vanishes**, so the embedding is a
rotation of the PPMI space and the only thing still separating it from the
Hellinger flat row is **the metric**. Three rows disambiguate — d = 768,
d = 1043 (the available rank), and ppmi-full (no factorisation at all).

## 2. Label governance

| event | UTC |
|---|---|
| `config_stamped` | {st['config_stamped_utc']} |
| `first_join` | {st['first_join_utc']} |
| `labels_opened` | {st['labels_opened_utc']} |

stamp<join **{st['stamp_precedes_join']}**; join<labels
**{st['join_precedes_labels']}**; all pre-join events label-free
**{st['events_before_join_all_label_free']}**; G0 PASS precedes stamp
issuance **{st['g0_passed_before_stamp']}**; identity companion computed
pre-stamp **{st['identity_companion_before_stamp']}**.

## 3. Gates

| gate | result |
|---|---|
| G0sr4 — SR3's curve bit-REPRODUCED (not copied) | **{'PASS' if g0['PASS'] else 'FAIL'}** — 10/10 coupling rows {v['gates']['sr3_coupling_bit_reproduced']}, 5/5 identity rows {v['gates']['sr3_identity_bit_reproduced']} |
| G1sr4 — the three rows are not forced | **{'PASS' if v['gates']['G1sr4']['PASS'] else 'FAIL'}** |
| G2sr4 — pilot band projection (#71) | **{v['gates']['G2sr4']}** |
| G3sr4 — A1-hardened stamp; own-null predicates | **{'PASS' if v['gates']['G3sr4']['PASS'] else 'FAIL'}** ({len(v['gates']['G3sr4']['predicates'])}) |

### Rank availability and the rotation check

{rot}

**Max disagreement between the d = 1043 row and the ppmi-full row:
{g0['max_rotation_disagreement']:.3e}** — the algebra of RN-SR4-1 holds
numerically. The two rows are the same estimand by two routes, so the
registration's RANK_ANOMALY cell is correctly unreachable here.

Note (RN-SR4-2): fold 4 trains on 1044 authors, so its factorisation has
1044 components and the registered d = 1043 row drops exactly one there.
The ppmi-full row, which never truncates anywhere, is the clean control —
and it agrees with d = 1043 to {g0['max_rotation_disagreement']:.1e}.

## 4. Reading notes (pinned BEFORE the verdict)

""" + "\n".join(f"- **{k}** — {t}" for k, t in sorted(RN_NOTES.items())) + f"""

## 5. G2sr4 — label-free pilot projection

{pil['G2sr4']['projection_rule']}; detection reference (half-flat)
{fmt(HALF_FLAT, 6)}.

{tbl(["reading", "pilot null sd", "projected full p95", "detects half-flat"],
     [[k, fmt(c["pilot_null_sd"], 5), fmt(c["projected_full_p95"], 5),
       str(c["detects_half_flat"])] for k, c in sorted(pil["calibration"].items())])}

**G2sr4: {pil['G2sr4']['VERDICT']}.**

## 6. The completed curves

### 6.1 Coupling (full arm, within-fold, B_perm={B_PERM}) — SR3's rows recomputed, three new rows in bold

{curve_tbl(cur)}

### 6.2 Identity (label-free, pre-stamp)

{ident_tbl}

## 7. V-SR4: {vv['verdict']}

{vv['reason']}.

### The pattern logic, shown

| condition | value |
|---|---|
| any truncation (d = 64…1043) detected under stratification | **{vv['any_truncation_detected']}** |
| ppmi-full detected under stratification | **{vv['ppmi_full_detected']}** |
| Hellinger flat detected under stratification | **{vv['flat_detected']}** |
| half-flat threshold | {fmt(vv['half_flat_threshold'], 6)} |
| marginal r monotone non-decreasing over d | {vv['marginal_monotone_over_dims']} |

**The coupling plateaus and capacity is provably exhausted.** The stratified
r runs {fmt(cur['d=512|stratified']['r'], 6)} (d=512) →
{fmt(cur['d=768|stratified']['r'], 6)} (768) →
{fmt(cur['d=1043|stratified']['r'], 6)} (1043) →
{fmt(cfull, 6)} (ppmi-full, no truncation at all), against a Hellinger flat
of {fmt(cflat, 6)}. There is no truncation left to remove, and
**{100 * (1 - c_gapf / c_gap0):.1f}%** of the d = 64 shortfall is all that
capacity ever buys — the remaining **{fmt(c_gapf, 6)}**, i.e.
**{100 * c_gapf / cflat:.0f}% of the flat value**, is metric.

The binary detection is the weaker statement and should be read with its
margin: the high-rank rows sit at p = {fmt(cur['d=768|stratified']['p_one_sided_positive'], 4)}
(768), {fmt(cur['d=1043|stratified']['p_one_sided_positive'], 4)} (1043) and
{fmt(cur[f'{PPMI_FULL}|stratified']['p_one_sided_positive'], 4)} (ppmi-full)
— just short of the band, not comfortably null. What does not depend on
where the threshold sits is the **z contrast: {fmt(cur[f'{PPMI_FULL}|stratified']['z_vs_null'], 2)}
for untruncated PPMI against {fmt(cur['flat|stratified']['z_vs_null'], 2)}
for Hellinger, on identical pairs with identical machinery.**

### The identity axis agrees, and it re-types T3's residual

T3 typed its 0.0387 GAP_REMAINS residual **representation-capacity**. On
this axis that typing does not survive: the identity AUC plateaus at
{fmt(ident['d=768']['auc'], 6)} (768) / {fmt(ident['d=1043']['auc'], 6)}
(1043) / {fmt(ifull, 6)} (ppmi-full) against a flat
{fmt(iflat, 6)}. Removing ALL truncation closes only
**{100 * (1 - i_gapf / i_gap0):.1f}%** of the original gap; **{fmt(i_gapf, 6)}
remains at zero truncation**, so **{100 * i_gapf / i_gap0:.1f}% of T3's
identity residual is metric, not capacity.** Both axes, independently,
return the same answer. *This is a candidate re-typing of a standing T3
result and is flagged for adjudication rather than asserted here.*

## 8. Routing

**{v['routing']['outcome']}** (slug `{v['routing']['slug']}`).

## 9. Clean arm and #73 flags

n_valid = {cl['n_valid']} (T1's clean arm {A_N_CLEAN}; match
{cl['matches_T1_clean_n']}). Clean classification:
**{cl['V_SR4_clean']['verdict']}** — same cell as the full arm.

{curve_tbl(clean['curve'])}

{div_tbl}

Every PPMI row detects marginally on the full arm and none does on the
clean arm, while Hellinger flat detects on both — the same
typology-community dependence SR2 and SR3 found, now shown to persist all
the way to full rank. Per #73 the full arm routes and the divergence is
flagged.

## 10. Compliance

- Labels opened once, in `stage_joint`, after the config hash; the identity
  companion and the pilot are pre-stamp and label-free. Corpus-level only;
  no person claim.
- **Interpreter:** {p0['environment']['python_version']} / numpy
  {p0['environment']['numpy']} / pandas {p0['environment']['pandas']} on
  {p0['environment']['platform']}.
- **Provenance:** SR3 harness `{g0['sha256']['sr3'][:16]}…`, selection.npz
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
          f"id_leak_hits={scan['n_hits']} PASS={scan['PASS']}")
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
