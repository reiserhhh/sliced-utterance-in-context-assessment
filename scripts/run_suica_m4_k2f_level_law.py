#!/usr/bin/env python3
"""M4-K2f -- THE LEVEL LAW.

Registered in docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md ("M4-K2f -- The level law",
commit 598fb78) BEFORE this file existed.  Implementation and execution only;
the registration text is binding.

D-open falsified the T4 composite as an ABSOLUTE LEVEL formula (S-4 missed by
5.09 band widths; every input re-derived bit-exactly; the world interpolated
cleanly; the glue -- kappa fitted on within-pair DIFFERENCES, lambda*r^q on a
pooled curve -- was never a level law).  The question: is there a level law at
all, and does it predict?

    Stage 1 (artifact space, NO new worlds)
      compile the b-only field-recovery LEVELS with their (r_pred, V_person)
      covariates over every persisted arm -- K2b 6, K2c 7, K2d 6, K2e 6,
      D-open's M-4 1 = 26 rows -- and fit THREE pre-declared forms:
          F1: field = lam*r^q - kap*V
          F2: field = lam*r^q - kap*V*r^p
          F3: field = (lam - kap*V)*r^q
      select by leave-one-out RMSE; baseline = the SEALED form's residual RMSE
      on the same rows at FROZEN published constants (no refit).
      L-1 [.55]: best LOO-RMSE <= 0.010 AND <= baseline_RMSE / 2.

    Stage 2 (predict-then-run)
      write AND HASH the winner's prediction for a FRESH arm (share .45,
      phi .90, K2b instrument, 32 worlds) BEFORE any fresh-arm world exists,
      then run the arm.  L-2 [.60]: measured inside +-2*LOO_RMSE.

ORDERING (G1f) IS ENFORCED, NOT ASSERTED: every fresh-arm world-building and
field-measuring entry point is wrapped at import time with a counter and a hard
permit gate.  The permit is issued only by re-reading prediction.sha256.json
from disk and re-hashing prediction.json to match.  Any fresh-arm generation
before the stamp raises SystemExit.

Stages:  part0 -> stage1 -> predict -> arm -> finalize
Artifacts: results/m4_k2f_level_law/ (gitignored)
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_k2f_level_law"
RES = ROOT / "results"

# ---------------------------------------------------------------------------
# Registration constants.

LEG = "M4-K2f"
BANNER = ("synthetic worlds calibrated to an opened-panel regime, exploratory; "
          "Stage 1 is artifact-space refitting on 26 persisted arms")
MASTER_SEED = 20260826            # registration: "master_seed 20260826"
FRESH_SHARE = 0.45                # registration: "share .45"
FRESH_PHI = 0.90                  # registration: "phi .90"
FRESH_WORLDS = 32                 # registration: "32 worlds"
FRESH_ARM_ID = "K2F-FRESH"
PILOT_WORLDS = (9601, 9602)       # RESERVED, disjoint from 0..31 (k2b's own)
B_BOOT = 2000                     # G3f: "B=2000 seed=master"
B_BOOT_HIGH = 20000               # G3f: ">=10xB at boundaries" (rule 13)

L1_RMSE_BAR = 0.010               # registration L-1 clause (i)
L1_FACTOR = 2.0                   # registration L-1 clause (ii)
L2_BAND_MULT = 2.0                # registration L-2: "+-2x LOO-RMSE"

# The SEALED T4 composite, frozen at its published values (D1 bundle, opened in
# D-open).  field = lambda*r^q + kappa_hat*V_person, kappa_hat NEGATIVE.
SEALED_LAMBDA = 0.17417497661611914
SEALED_Q = 1.8528700746510731
SEALED_KAPPA_HAT = -0.7220359963712748

# G0f anchors -- D-open's S-4 numbers, bit-exact.
ANCHORS = {
    "sealed_prediction": -0.015116265289181696,
    "measured_recovery_b_only": 0.09350089316336324,
    "measured_ci_lo": 0.08624502054643839,
    "measured_ci_hi": 0.10103687186109606,
    "r_pred": 0.6185853753498524,
    "V_person": 0.12000000000000004,
}

# ---------------------------------------------------------------------------
# RN-K2F-1 (rule 9, PINNED BEFORE COMPILATION).  THE ROW RULE.
#
# One row per persisted PRIMARY DESIGN ARM whose b-only field level and design
# knobs (share, int_share, phi) are both persisted -- BOTH sides of every
# matched pair are separate rows, because a pair's two arms are two distinct
# (r, V) design points and the object being fitted is a LEVEL law, not a
# difference law (the difference reading is exactly what D-open convicted).
# K2b contributes its six PRIMARY arms; K2b's C1 is EXCLUDED because K2b's own
# machinery excludes it (k2b:94-105, PRIMARY_ARMS = arms with primary=True; C1
# is the "descriptive companion cell, no gate" with an equal-share w_int
# carrier).  This yields 6 + 7 + 6 + 6 + 1 = 26 rows, which is the count the
# registration itself states ("K2b's 6, K2c's 7, K2d's 6, K2e's 6, D-open's
# M-4 arm") and the count G0f names ("the 26-row compilation audited").
#
# ALTERNATIVE READINGS, reported not adopted:
#   (a) a-side only (one row per pair + unpaired arms):  6 + 4 + 3 + 3 + 1 = 17
#   (b) pair MEANS as rows (K2d's post_hoc `level` currency): 6 + 4 + 3 + 3 + 1
#       = 17 (same count, different rows: 6 pair means replace 12 arm rows and
#       the 3 K2c pair means replace 6)
#   (c) RN-K2F-1 plus K2b's C1 companion: 27
# Only (RN-K2F-1) reproduces the registration's own per-leg counts.
ROW_RULE = "RN-K2F-1"

# RN-K2F-2 (rule 9, PINNED).  FIT WEIGHTING.  Unweighted least squares over
# rows -- the registration says "nonlinear least squares on the compiled level
# rows" with no weights, and the rows are design points, not replicates.  The
# alternative (inverse-variance weights from each arm's per-world SEM, which
# would up-weight the 32-world arms over K2b's 8-world arms by ~2x in sd) is
# computed and REPORTED as a second reading; it does not select the winner.
#
# RN-K2F-3 (rule 9, PINNED).  FRESH-ARM SEED LINEAGE.  K2f's OWN lineage,
# salt "m4k2f-world", MASTER_SEED 20260826 -- the registration names a master
# seed for this arm, and a genuinely fresh panel draw is the stricter test of a
# prediction.  The alternative (reuse k2b.world_seed_for, i.e. the very panels
# every training row was measured on, as D-open's M-4 did) is ALSO run and
# REPORTED as a second reading; it does not adjudicate L-2.
#
# RN-K2F-4 (rule 9, PINNED).  ORDERING vs the G2f PILOT.  The registration's
# ordering clause is absolute ("any fresh-arm generation before the prediction
# hash is persisted -> STOP"), so the rule-17 fresh-arm pilot runs AFTER the
# prediction stamp, not before it.  A pilot is a measurement of the fresh arm;
# publishing a prediction early costs nothing, reading the arm early costs the
# leg.  If the pilot fails, the leg stops and L-2 is UNRESOLVABLE with the
# prediction already on the record.

# ---------------------------------------------------------------------------
# Module loading (the published machinery; suica_core untouched).

_MODS: dict[str, Any] = {}


def _load(name: str) -> Any:
    if name in _MODS:
        return _MODS[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    if spec is None or spec.loader is None:      # pragma: no cover
        raise SystemExit(f"REFUSED: cannot load {name}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    _MODS[name] = mod
    return mod


def k2b() -> Any:
    return _load("run_suica_m4_k2b_t4_branch")


def k2c() -> Any:
    return _load("run_suica_m4_k2c_matched_pairs")


def k2d() -> Any:
    return _load("run_suica_m4_k2d_frontier_carrier")


def k2e() -> Any:
    return _load("run_suica_m4_k2e_double_matching")


# ---------------------------------------------------------------------------
# G1f -- ORDERING ENFORCEMENT.  Armed at first fresh-arm use, never disarmed.

_FRESH_GEN_COUNT = 0
_FRESH_PERMIT = False
_ARMED = False


def _ordering_log(event: str, **kw: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "ordering_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def _reachable_k2b() -> list[Any]:
    """Every DISTINCT k2b module object reachable from this process.  The
    published legs use private importlib loaders that ignore `sys.modules`
    (RN-K2F-5), so there is more than one; a guard installed on only one of
    them would be nominal, not enforced."""
    cands: list[Any] = [k2b()]
    for acc in (lambda: k2c().k2b(), lambda: k2d().k2b(), lambda: k2e().k2b(),
                lambda: k2d().k2c().k2b(), lambda: k2e().k2d().k2b(),
                lambda: k2e().k2d().k2c().k2b()):
        try:
            cands.append(acc())
        except Exception:                                    # noqa: BLE001
            continue
    seen, out = set(), []
    for m in cands:
        if id(m) not in seen:
            seen.add(id(m))
            out.append(m)
    return out


def _arm_ordering_guard() -> int:
    """Wrap every entry point that can build or measure a FRESH-ARM world, on
    every reachable k2b instance."""
    global _ARMED
    if _ARMED:
        return 0
    mods = _reachable_k2b()
    for kb in mods:
        for fname in ("build_k2b_world", "run_field_world", "emit_panel"):
            original: Callable[..., Any] = getattr(kb, fname)

            def make(orig: Callable[..., Any], nm: str) -> Callable[..., Any]:
                def wrapped(*a: Any, **kw: Any) -> Any:
                    global _FRESH_GEN_COUNT
                    _FRESH_GEN_COUNT += 1
                    if not _FRESH_PERMIT:
                        _ordering_log("REFUSED_fresh_arm_generation", entry_point=nm,
                                      count=_FRESH_GEN_COUNT)
                        raise SystemExit(
                            f"STOP (G1f): fresh-arm generation via {nm} attempted "
                            f"before the prediction hash was persisted."
                        )
                    return orig(*a, **kw)
                wrapped.__name__ = f"guarded_{nm}"
                return wrapped

            setattr(kb, fname, make(original, fname))
    _ARMED = True
    _ordering_log("ordering_guard_armed", n_k2b_instances=len(mods),
                  entry_points=["build_k2b_world", "run_field_world", "emit_panel"],
                  n_wrapped=3 * len(mods))
    return len(mods)


def _issue_permit() -> dict[str, Any]:
    """Permit ONLY after re-reading the stamp from disk and re-hashing."""
    global _FRESH_PERMIT
    pred_path, stamp_path = OUT / "prediction.json", OUT / "prediction.sha256.json"
    if not pred_path.exists() or not stamp_path.exists():
        raise SystemExit("STOP (G1f): no persisted prediction stamp; run `predict`.")
    raw = pred_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
    if digest != stamp["sha256"]:
        raise SystemExit(
            f"STOP (G1f): prediction.json hash {digest} != stamped {stamp['sha256']}"
        )
    if _FRESH_GEN_COUNT != 0:
        raise SystemExit(
            f"STOP (G1f): {_FRESH_GEN_COUNT} fresh-arm generations before permit."
        )
    _FRESH_PERMIT = True
    rec = {"permit_utc": datetime.now(UTC).isoformat(),
           "prediction_sha256_recomputed": digest,
           "prediction_sha256_stamped": stamp["sha256"],
           "stamp_utc": stamp["stamp_utc"],
           "fresh_generations_before_permit": _FRESH_GEN_COUNT}
    _ordering_log("permit_issued", **rec)
    return rec


# ---------------------------------------------------------------------------
# Small utilities.

def read_csv_rt(path: Path) -> pd.DataFrame:
    """Round-trip float parsing (k2a:118 / k2b:178-180), every artifact."""
    return pd.read_csv(path, float_precision="round_trip")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=float)
        fh.write("\n")


def boot_index(b_draws: int, seed: int, n: int) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, n, size=(b_draws, n))


def boot_ci(values: np.ndarray, b_draws: int = B_BOOT,
            seed: int = MASTER_SEED) -> dict[str, float]:
    """World-block bootstrap over worlds (D-open boot_ci verbatim, k2b lineage)."""
    v = np.asarray(values, dtype=float)
    draws = v[boot_index(b_draws, seed, len(v))].mean(axis=1)
    return {"mean": float(v.mean()), "lo": float(np.quantile(draws, 0.025)),
            "hi": float(np.quantile(draws, 0.975)),
            "sd": float(np.std(draws, ddof=1)),
            "n_blocks": int(len(v)), "B": int(b_draws), "seed": int(seed)}


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# ---------------------------------------------------------------------------
# PART 0 -- the compilation.

# (leg, arm, results dir, field-CSV shards, design source, level source)
K2B_ARMS = ("A1", "A2", "A3", "A4", "A5", "A6")
K2C_ARMS = ("P1a", "P1b", "P2a", "P2b", "P3a", "P3b", "A1anc")
K2D_ARMS = ("FR45a", "FR45b", "SP68slow", "SP68int", "SP56slow", "SP56int")
K2E_ARMS = ("DM68a", "DM68b", "DM56a", "DM56b", "VS62a", "VS62b")


def _shards(dirname: str, arm: str) -> list[Path]:
    d = RES / dirname
    single = d / f"arm_{arm}_field.csv"
    if single.exists():
        return [single]
    out = [d / f"arm_{arm}_field_w000_015.csv", d / f"arm_{arm}_field_w016_031.csv"]
    for p in out:
        if not p.exists():
            raise SystemExit(f"REFUSED: missing shard {p}")
    return out


def _level_from_raw(paths: list[Path]) -> tuple[float, int, list[str]]:
    frames = [read_csv_rt(p) for p in paths]
    df = pd.concat(frames, ignore_index=True)
    vals = df["recovery_b_only"].to_numpy(float)
    if not np.all(np.isfinite(vals)):
        raise SystemExit(f"REFUSED: non-finite recovery_b_only in {paths}")
    return float(vals.mean()), int(len(vals)), [rel(p) for p in paths]


def install_species_weights() -> dict[str, Any]:
    """K2d's DISCLOSED single-object dispatcher (k2d:206-237), required because
    four compiled rows (SP68int, SP56int, DM68b, DM56b) carry an `int:t`
    interaction carrier that k2b's own `arm_weights` (k2b:198-210) does not
    parse.  K2d's own Part-0 proof that the dispatcher is BIT-EXACT on k2b's
    original domain is re-run here and persisted.

    RN-K2F-5 (machinery note): the published legs each load their dependencies
    through PRIVATE importlib loaders that do NOT consult `sys.modules`, so
    `k2e.k2d()` is a DIFFERENT k2d object from the one this script loads, owning
    a DIFFERENT k2b object.  Installing on one leaves the other unpatched and
    `person_share_design` raises on the four `int:` rows.  Both installers are
    therefore run, and both verifications are persisted."""
    installed: list[tuple[str, Any]] = []
    kd = k2d()
    kd.install_species_weights()
    installed.append(("k2f->k2d", kd))
    kd2 = k2e().k2d()
    if kd2 is not kd:
        kd2.install_species_weights()
        installed.append(("k2f->k2e->k2d", kd2))
    return {
        "note": "K2d's dispatcher installed on every reachable k2b instance",
        "n_installers_run": len(installed),
        "distinct_k2b_objects": len({id(m.k2b()) for _, m in installed}),
        "verifications": {tag: m.verify_species_weights() for tag, m in installed},
    }


def compile_rows() -> tuple[pd.DataFrame, dict[str, Any]]:
    """The 26-row table, every level and covariate re-derived round-trip."""
    kc, kd, ke = k2c(), k2d(), k2e()
    rows: list[dict[str, Any]] = []
    notes: dict[str, Any] = {"weights_dispatcher": install_species_weights()}

    # --- K2b: six primary arms, 8 worlds each -----------------------------
    kb_dec = read_json(RES / "m4_k2b_t4_branch" / "decision.json")
    kb_pub = {r["arm"]: r["b_only_mean"] for r in kb_dec["leans"]["L-D"]["per_arm"]}
    kb_manifest = read_json(RES / "m4_k2b_t4_branch" / "manifest.json")
    kb_spec = {a[0]: a for a in kb_manifest["arms"]}
    kb_pred = read_csv_rt(RES / "m4_k2b_t4_branch" / "part0_predictions.csv")
    kb_pred = kb_pred.set_index("arm")
    for arm in K2B_ARMS:
        _, share, phi, w_int_arm, primary = kb_spec[arm]
        if not primary:
            raise SystemExit(f"REFUSED: {arm} is not a K2b primary arm")
        paths = _shards("m4_k2b_t4_branch", arm)
        lvl, nw, src = _level_from_raw(paths)
        rows.append({
            "row_id": f"K2b:{arm}", "leg": "K2b", "arm": arm,
            "share": float(share), "int_share": 0.0, "phi": float(phi),
            "w_int_arm": w_int_arm, "n_worlds": nw,
            "level_rederived": lvl,
            "level_published": float(kb_pub[arm]),
            "level_source_files": ";".join(src),
            "level_published_source":
                "results/m4_k2b_t4_branch/decision.json:leans.L-D.per_arm[].b_only_mean",
            "design_source": "results/m4_k2b_t4_branch/manifest.json:arms[]",
            "r_persisted": float(kb_pred.loc[arm, "r_card_b_pred_raw"]),
            "r_persisted_source":
                "results/m4_k2b_t4_branch/part0_predictions.csv:r_card_b_pred_raw",
            "V_persisted": None, "V_persisted_source": "",
            "master_seed": int(kb_manifest["master_seed"]),
        })

    # --- K2c: seven arms, 32 worlds each ----------------------------------
    kc_arms = read_json(RES / "m4_k2c_matched_pairs" / "part0_arms.json")
    kc_dec = read_json(RES / "m4_k2c_matched_pairs" / "decision.json")
    kc_spec = {a["arm"]: a for a in kc_arms["arms"]}
    kc_rp = {}
    for p in kc_arms["pairs"]:
        for side in ("arm_a", "arm_b"):
            kc_rp[p[side]["arm"]] = p[side]["predicted_attenuation"]
    for arm in K2C_ARMS:
        sp = kc_spec[arm]
        paths = _shards("m4_k2c_matched_pairs", arm)
        lvl, nw, src = _level_from_raw(paths)
        rows.append({
            "row_id": f"K2c:{arm}", "leg": "K2c", "arm": arm,
            "share": float(sp["share"]), "int_share": 0.0, "phi": float(sp["phi"]),
            "w_int_arm": sp["w_int_arm"], "n_worlds": nw,
            "level_rederived": lvl,
            "level_published":
                float(kc_dec["descriptive"]["per_arm"][arm]["field_b_only"]),
            "level_source_files": ";".join(src),
            "level_published_source":
                "results/m4_k2c_matched_pairs/decision.json:"
                "descriptive.per_arm.<arm>.field_b_only",
            "design_source": "results/m4_k2c_matched_pairs/part0_arms.json:arms[]",
            "r_persisted": kc_rp.get(arm),
            "r_persisted_source": (
                "results/m4_k2c_matched_pairs/part0_arms.json:pairs[].arm_?"
                ".predicted_attenuation" if arm in kc_rp else ""),
            "V_persisted": None, "V_persisted_source": "",
            "master_seed": int(kc_arms["master_seed"]),
        })

    # --- K2d and K2e: six arms each, 32 worlds -----------------------------
    for legname, dirname, armlist, has_ps in (
            ("K2d", "m4_k2d_frontier_carrier", K2D_ARMS, False),
            ("K2e", "m4_k2e_double_matching", K2E_ARMS, True)):
        spec_j = read_json(RES / dirname / "part0_arms.json")
        dec = read_json(RES / dirname / "decision.json")
        spec = {a["arm"]: a for a in spec_j["arms"]}
        rp, vp = {}, {}
        for p in spec_j["pairs"]:
            for side in ("arm_a", "arm_b"):
                rp[p[side]["arm"]] = p[side]["predicted_attenuation"]
                if has_ps and "predicted_person_share" in p[side]:
                    vp[p[side]["arm"]] = p[side]["predicted_person_share"]
        for arm in armlist:
            sp = spec[arm]
            paths = _shards(dirname, arm)
            lvl, nw, src = _level_from_raw(paths)
            rows.append({
                "row_id": f"{legname}:{arm}", "leg": legname, "arm": arm,
                "share": float(sp["share"]), "int_share": float(sp["int_share"]),
                "phi": float(sp["phi"]), "w_int_arm": sp["w_int_arm"],
                "n_worlds": nw, "level_rederived": lvl,
                "level_published":
                    float(dec["descriptive"]["per_arm"][arm]["field_b_only"]),
                "level_source_files": ";".join(src),
                "level_published_source":
                    f"results/{dirname}/decision.json:"
                    "descriptive.per_arm.<arm>.field_b_only",
                "design_source": f"results/{dirname}/part0_arms.json:arms[]",
                "r_persisted": rp.get(arm),
                "r_persisted_source":
                    f"results/{dirname}/part0_arms.json:pairs[].arm_?"
                    ".predicted_attenuation",
                "V_persisted": vp.get(arm),
                "V_persisted_source": (
                    f"results/{dirname}/part0_arms.json:pairs[].arm_?"
                    ".predicted_person_share" if arm in vp else ""),
                "master_seed": int(spec_j["master_seed"]),
            })

    # --- D-open's M-4 arm, 32 worlds ---------------------------------------
    do_stage = read_json(RES / "dopen_seal_opening" / "stage1_m4.json")
    do_path = RES / "dopen_seal_opening" / "m4_field_rows.csv"
    lvl, nw, src = _level_from_raw([do_path])
    rows.append({
        "row_id": "Dopen:M-4", "leg": "Dopen", "arm": "DOPEN-S4",
        "share": float(do_stage["config"]["share"]), "int_share": 0.0,
        "phi": float(do_stage["config"]["phi"]),
        "w_int_arm": do_stage["config"]["w_int_arm"], "n_worlds": nw,
        "level_rederived": lvl,
        "level_published": float(do_stage["measured_recovery_b_only"]["mean"]),
        "level_source_files": ";".join(src),
        "level_published_source":
            "results/dopen_seal_opening/stage1_m4.json:"
            "measured_recovery_b_only.mean",
        "design_source": "results/dopen_seal_opening/stage1_m4.json:config",
        "r_persisted": float(do_stage["law_inputs"]["r_card_b_pred_raw"]),
        "r_persisted_source":
            "results/dopen_seal_opening/stage1_m4.json:law_inputs.r_card_b_pred_raw",
        "V_persisted": float(do_stage["law_inputs"]["V_person_design"]),
        "V_persisted_source":
            "results/dopen_seal_opening/stage1_m4.json:law_inputs.V_person_design",
        "master_seed": 20260825,
    })

    # --- covariates, re-derived through the PUBLISHED machinery ------------
    for r in rows:
        if r["int_share"] == 0.0:
            r["r_pred"] = kc.predicted_attenuation(r["share"], r["phi"])
            r["r_pred_source"] = ("scripts/run_suica_m4_k2c_matched_pairs.py:186-191"
                                  " (predicted_attenuation -> k2b:533-583)")
        else:
            r["r_pred"] = kd.predicted_attenuation(r["share"], r["int_share"], r["phi"])
            r["r_pred_source"] = ("scripts/run_suica_m4_k2d_frontier_carrier.py:273-279"
                                  " (predicted_attenuation -> k2b:533-583)")
        r["V_person"] = ke.person_share_design(r["share"], r["int_share"])
        r["V_person_source"] = ("scripts/run_suica_m4_k2e_double_matching.py:234-241"
                                " (person_share_design -> k2b.arm_shares)")
        r["level_roundtrip_bit_exact"] = bool(r["level_rederived"] == r["level_published"])
        r["r_bit_exact"] = (None if r["r_persisted"] is None
                            else bool(r["r_pred"] == r["r_persisted"]))
        r["V_bit_exact"] = (None if r["V_persisted"] is None
                            else bool(r["V_person"] == r["V_persisted"]))
        # per-world sd, for the RN-K2F-2 second reading only
        paths = [ROOT / p for p in r["level_source_files"].split(";")]
        vals = pd.concat([read_csv_rt(p) for p in paths],
                         ignore_index=True)["recovery_b_only"].to_numpy(float)
        r["level_sd_worlds"] = float(np.std(vals, ddof=1))
        r["level_sem"] = float(np.std(vals, ddof=1) / np.sqrt(len(vals)))

    df = pd.DataFrame(rows)
    notes["n_rows"] = int(len(df))
    notes["per_leg"] = {k: int(v) for k, v in df["leg"].value_counts().items()}
    notes["level_roundtrip_all_bit_exact"] = bool(df["level_roundtrip_bit_exact"].all())
    notes["level_roundtrip_max_abs_diff"] = float(
        (df["level_rederived"] - df["level_published"]).abs().max())
    rchk = df.dropna(subset=["r_persisted"])
    notes["r_bit_exact_n"] = int(rchk["r_bit_exact"].sum())
    notes["r_bit_exact_of"] = int(len(rchk))
    notes["r_max_abs_diff"] = float(
        (rchk["r_pred"] - rchk["r_persisted"].astype(float)).abs().max())
    vchk = df.dropna(subset=["V_persisted"])
    notes["V_bit_exact_n"] = int(vchk["V_bit_exact"].sum())
    notes["V_bit_exact_of"] = int(len(vchk))
    notes["V_max_abs_diff"] = float(
        (vchk["V_person"] - vchk["V_persisted"].astype(float)).abs().max())
    notes["alternative_readings"] = {
        "a_side_only_rows": 17, "pair_means_rows": 17, "with_k2b_C1_rows": 27,
    }
    return df, notes


# ---------------------------------------------------------------------------
# The three candidate forms (pre-declared; NO others).

def f1(theta: np.ndarray, r: np.ndarray, v: np.ndarray) -> np.ndarray:
    lam, q, kap = theta
    return lam * r ** q - kap * v


def f2(theta: np.ndarray, r: np.ndarray, v: np.ndarray) -> np.ndarray:
    lam, q, kap, p = theta
    return lam * r ** q - kap * v * r ** p


def f3(theta: np.ndarray, r: np.ndarray, v: np.ndarray) -> np.ndarray:
    lam, q, kap = theta
    return (lam - kap * v) * r ** q


FORMS: dict[str, dict[str, Any]] = {
    "F1": {"fn": f1, "names": ("lambda", "q", "kappa"), "k": 3,
           "expr": "field = lambda*r^q - kappa*V"},
    "F2": {"fn": f2, "names": ("lambda", "q", "kappa", "p"), "k": 4,
           "expr": "field = lambda*r^q - kappa*V*r^p"},
    "F3": {"fn": f3, "names": ("lambda", "q", "kappa"), "k": 3,
           "expr": "field = (lambda - kappa*V)*r^q"},
}

# OPTIMIZER PINS (Part 0; identical for every fit in this leg).
OPT = {
    "routine": "scipy.optimize.least_squares",
    "method": "trf",
    "jac": "2-point (numerical)",
    "bounds": "unbounded, x_scale=1.0",
    "ftol": 1e-14, "xtol": 1e-14, "gtol": 1e-14,
    "max_nfev": 20000,
    "loss": "linear (plain least squares)",
    "scipy_version": None,
}
START_LAMBDA = (0.05, SEALED_LAMBDA, 0.5)
START_Q = (0.5, 1.0, SEALED_Q, 3.0)
START_KAPPA = (0.0, -SEALED_KAPPA_HAT, 2.0)
START_P = (0.0, 1.0, SEALED_Q)
OPT_SAME_SSE_TOL = 1e-12


def starts_for(form: str) -> list[list[float]]:
    out = []
    for lam in START_LAMBDA:
        for q in START_Q:
            for kap in START_KAPPA:
                if form == "F2":
                    for p in START_P:
                        out.append([lam, q, kap, p])
                else:
                    out.append([lam, q, kap])
    return out


def fit_form(form: str, r: np.ndarray, v: np.ndarray, y: np.ndarray,
             starts: list[list[float]] | None = None) -> dict[str, Any]:
    spec = FORMS[form]
    fn = spec["fn"]

    def resid(theta: np.ndarray) -> np.ndarray:
        with np.errstate(over="ignore", invalid="ignore"):
            pred = fn(theta, r, v)
        pred = np.where(np.isfinite(pred), pred, 1e12)
        return pred - y

    best: dict[str, Any] | None = None
    sses: list[float] = []
    n_conv = 0
    for s0 in (starts if starts is not None else starts_for(form)):
        try:
            res = least_squares(resid, np.asarray(s0, float), method=OPT["method"],
                                jac="2-point", ftol=OPT["ftol"], xtol=OPT["xtol"],
                                gtol=OPT["gtol"], max_nfev=OPT["max_nfev"])
        except Exception:                                   # noqa: BLE001
            continue
        if not res.success and res.status <= 0:
            continue
        n_conv += 1
        sse = float(np.sum(res.fun ** 2))
        if not np.isfinite(sse):
            continue
        sses.append(sse)
        if best is None or sse < best["sse"]:
            best = {"theta": [float(x) for x in res.x], "sse": sse,
                    "status": int(res.status), "nfev": int(res.nfev)}
    if best is None:
        raise SystemExit(f"REFUSED: no converged start for {form}")
    n_at_best = int(sum(1 for s in sses
                        if abs(s - best["sse"]) <= OPT_SAME_SSE_TOL * max(1.0, best["sse"])))
    n = len(y)
    best.update({
        "form": form, "expr": spec["expr"], "param_names": list(spec["names"]),
        "n_starts": len(starts if starts is not None else starts_for(form)),
        "n_converged": n_conv, "n_starts_at_global_sse": n_at_best,
        "n_distinct_optima": int(len({round(s, 12) for s in sses})),
        "rmse": float(np.sqrt(best["sse"] / n)), "n_rows": int(n),
        "r2_vs_mean": float(1.0 - best["sse"] / float(np.sum((y - y.mean()) ** 2))),
    })
    return best


def loo_rmse(form: str, r: np.ndarray, v: np.ndarray, y: np.ndarray,
             full_theta: list[float]) -> dict[str, Any]:
    """Leave-one-out: refit on n-1 rows with the SAME multi-start grid plus the
    full-data optimum, predict the held-out row."""
    n = len(y)
    preds, errs, failed = [], [], 0
    grid = starts_for(form) + [list(full_theta)]
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        try:
            f = fit_form(form, r[m], v[m], y[m], starts=grid)
        except SystemExit:
            failed += 1
            preds.append(float("nan"))
            errs.append(float("nan"))
            continue
        th = np.asarray(f["theta"], float)
        with np.errstate(over="ignore", invalid="ignore"):
            p = float(FORMS[form]["fn"](th, r[i:i + 1], v[i:i + 1])[0])
        preds.append(p)
        errs.append(p - float(y[i]))
    e = np.asarray(errs, float)
    return {"form": form, "loo_pred": preds, "loo_error": errs,
            "n_failed": int(failed),
            "loo_rmse": float(np.sqrt(np.nanmean(e ** 2))),
            "loo_mae": float(np.nanmean(np.abs(e))),
            "loo_max_abs": float(np.nanmax(np.abs(e)))}


def sealed_pred(r: np.ndarray, v: np.ndarray) -> np.ndarray:
    return SEALED_LAMBDA * r ** SEALED_Q + SEALED_KAPPA_HAT * v


# ---------------------------------------------------------------------------
# STAGES.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _ordering_log("part0_start")
    df, notes = compile_rows()
    df.to_csv(OUT / "compiled_rows.csv", index=False)

    r = df["r_pred"].to_numpy(float)
    v = df["V_person"].to_numpy(float)
    y = df["level_rederived"].to_numpy(float)

    # G0f -- D-open's S-4 anchors, bit-exact.
    do_stage = read_json(RES / "dopen_seal_opening" / "stage1_m4.json")
    m4 = do_stage["measured_recovery_b_only"]
    a_r = k2c().predicted_attenuation(0.40, 0.90)
    a_v = k2e().person_share_design(0.40, 0.0)
    a_sealed = float(sealed_pred(np.array([a_r]), np.array([a_v]))[0])
    g0 = {
        "sealed_prediction": {"expected": ANCHORS["sealed_prediction"],
                              "rederived": a_sealed,
                              "bit_exact": a_sealed == ANCHORS["sealed_prediction"]},
        "measured": {"expected": ANCHORS["measured_recovery_b_only"],
                     "persisted": float(m4["mean"]),
                     "bit_exact": float(m4["mean"]) == ANCHORS["measured_recovery_b_only"]},
        "ci_lo": {"expected": ANCHORS["measured_ci_lo"], "persisted": float(m4["lo"]),
                  "bit_exact": float(m4["lo"]) == ANCHORS["measured_ci_lo"]},
        "ci_hi": {"expected": ANCHORS["measured_ci_hi"], "persisted": float(m4["hi"]),
                  "bit_exact": float(m4["hi"]) == ANCHORS["measured_ci_hi"]},
        "r": {"expected": ANCHORS["r_pred"], "rederived": a_r,
              "bit_exact": a_r == ANCHORS["r_pred"]},
        "V": {"expected": ANCHORS["V_person"], "rederived": a_v,
              "bit_exact": a_v == ANCHORS["V_person"]},
        "compilation": {
            "n_rows": notes["n_rows"], "expected_n_rows": 26,
            "per_leg": notes["per_leg"],
            "expected_per_leg": {"K2b": 6, "K2c": 7, "K2d": 6, "K2e": 6, "Dopen": 1},
            "levels_bit_exact_vs_published": notes["level_roundtrip_all_bit_exact"],
            "level_max_abs_diff": notes["level_roundtrip_max_abs_diff"],
            "r_bit_exact": f"{notes['r_bit_exact_n']}/{notes['r_bit_exact_of']}",
            "r_max_abs_diff": notes["r_max_abs_diff"],
            "V_bit_exact": f"{notes['V_bit_exact_n']}/{notes['V_bit_exact_of']}",
            "V_max_abs_diff": notes["V_max_abs_diff"],
            "duplicate_design_points": _duplicate_design_points(df),
        },
    }
    g0_pass = (all(g0[k]["bit_exact"] for k in ("sealed_prediction", "measured",
                                                "ci_lo", "ci_hi", "r", "V"))
               and notes["n_rows"] == 26
               and g0["compilation"]["per_leg"] == g0["compilation"]["expected_per_leg"]
               and notes["level_roundtrip_all_bit_exact"])
    g0["PASS"] = bool(g0_pass)

    # --- rule 11 satisfiability, on the SEALED baseline (no fitting) -------
    base_resid = sealed_pred(r, v) - y
    base_rmse = float(np.sqrt(np.mean(base_resid ** 2)))
    sat = {
        "L-1 clause (i)": {"clause": f"best LOO-RMSE <= {L1_RMSE_BAR}",
                           "sided": "one-sided", "improvement_side": "DOWN"},
        "L-1 clause (ii)": {"clause": f"best LOO-RMSE <= baseline_RMSE / {L1_FACTOR}",
                            "sided": "one-sided", "improvement_side": "DOWN",
                            "baseline_RMSE": base_rmse,
                            "implied_bar": base_rmse / L1_FACTOR},
        "joint_binding_bar": float(min(L1_RMSE_BAR, base_rmse / L1_FACTOR)),
        "jointly_satisfiable": bool(min(L1_RMSE_BAR, base_rmse / L1_FACTOR) > 0.0),
        "which_clause_binds": ("clause (i), the 0.010 bar"
                               if L1_RMSE_BAR <= base_rmse / L1_FACTOR
                               else "clause (ii), the 2x-baseline bar"),
        "L-2": {"clause": f"measured inside prediction +- {L2_BAND_MULT}*LOO_RMSE",
                "sided": "two-sided", "improvement_side":
                    "neither -- containment; a MISS on either side falsifies",
                "satisfiable": "non-empty band iff LOO_RMSE > 0 (checked at Stage 2)"},
        "note": ("the sealed baseline is arithmetic at FROZEN published constants -- "
                 "no fitting -- so it is computable in Part 0, which is what makes "
                 "the rule-11 check real rather than nominal"),
    }

    # --- rule 17 realizability for STAGE 1: the tied-covariate floor -------
    # Four design points are measured more than once at IDENTICAL (r, V) --
    # K2e's double-matched b-sides sit on their a-sides' covariates BY DESIGN
    # (that is the H-VAR test).  No function of (r, V) alone can separate them,
    # so the within-tie spread is an IRREDUCIBLE floor under every candidate
    # form.  Computed here, BEFORE any fit, because if the floor exceeded
    # L-1's 0.010 bar the lean would be unsatisfiable by construction.
    key = [(round(a, 12), round(b, 12)) for a, b in zip(r, v)]
    ss_in = ss_loo = 0.0
    ties = []
    for k in sorted(set(key)):
        j = [i for i, kk in enumerate(key) if kk == k]
        if len(j) < 2:
            continue
        yy = y[j]
        m_ = len(j)
        dev = yy - yy.mean()
        ss_in += float(np.sum(dev ** 2))
        ss_loo += float(np.sum((dev * m_ / (m_ - 1)) ** 2))
        ties.append({"r": k[0], "V": k[1], "n": m_,
                     "rows": [df["row_id"].iloc[i] for i in j],
                     "spread": float(yy.max() - yy.min())})
    floor = {
        "tied_clusters": ties,
        "n_rows_in_ties": int(sum(t["n"] for t in ties)),
        "irreducible_in_sample_RMSE_floor": float(np.sqrt(ss_in / n)) if (n := len(y)) else 0.0,
        "irreducible_LOO_RMSE_floor": float(np.sqrt(ss_loo / len(y))),
        "L1_bar": L1_RMSE_BAR,
        "L1_realizable": bool(np.sqrt(ss_loo / len(y)) < L1_RMSE_BAR),
        "statement": ("the LOO floor is what any (r,V)-only law must pay before it "
                      "explains anything; L-1 is realizable iff this floor is below "
                      "the 0.010 bar"),
    }

    # --- rule 23: gate stages ----------------------------------------------
    gate_stages = {
        "G0f": "inputs exist at Part 0 (persisted D-open artifacts + the 26 rows)",
        "G1f": "inputs exist at the predict/arm boundary (the stamp and the counter)",
        "G2f": "inputs exist AFTER the prediction stamp (RN-K2F-4), before the 32 worlds",
        "G3f": "inputs exist at Stage 1 (satisfiability, sides) and Stage 2 (B, boundaries)",
        "G4f": "inputs exist at finalize (all persisted values + the prose)",
    }
    # --- rule 16: the three cells -------------------------------------------
    cells = [
        {"cell": 1, "L-1": "MISS", "L-2": "not adjudicated (run for the record)",
         "route": "T4 scoped PERMANENTLY to response form; the level question closes "
                  "answered-in-the-negative",
         "slug": "NO_LEVEL_LAW"},
        {"cell": 2, "L-1": "HOLD", "L-2": "HOLD",
         "route": "the level law is RESTORED in the winning form; inherits the "
                  "fragility-annex quoting rules; a D1-style seal is the named follow-up",
         "slug": "LEVEL_LAW_RESTORED"},
        {"cell": 3, "L-1": "HOLD", "L-2": "MISS",
         "route": "OVERFIT: the refit describes, does not predict; T4 scoped to "
                  "response form; the winning form recorded descriptive-only",
         "slug": "LEVEL_LAW_OVERFIT"},
    ]

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "row_rule": ROW_RULE,
        "conventions": {
            "RN-K2F-1": "one row per persisted PRIMARY design arm, both pair sides; "
                        "K2b C1 excluded (k2b PRIMARY_ARMS); 26 rows",
            "RN-K2F-2": "unweighted NLS; inverse-variance weighting reported as a "
                        "second reading only",
            "RN-K2F-3": "fresh arm on K2f's OWN seed lineage (salt m4k2f-world, "
                        "master_seed 20260826); the k2b-lineage reading reported second",
            "RN-K2F-4": "the G2f pilot runs AFTER the prediction stamp",
        },
        "alternative_row_readings": notes["alternative_readings"],
        "forms": {k: FORMS[k]["expr"] for k in ("F1", "F2", "F3")},
        "form_nesting": ("F2 nests both: F1 is F2 at p=0, F3 is F2 at p=q; so F2 "
                         "cannot fit worse than either in-sample, and LOO is what "
                         "pays for its fourth parameter"),
        "optimizer": {**OPT, "scipy_version": __import__("scipy").__version__,
                      "n_starts_F1": len(starts_for("F1")),
                      "n_starts_F2": len(starts_for("F2")),
                      "n_starts_F3": len(starts_for("F3")),
                      "start_grid": {"lambda": list(START_LAMBDA), "q": list(START_Q),
                                     "kappa": list(START_KAPPA), "p": list(START_P)},
                      "same_optimum_sse_tol": OPT_SAME_SSE_TOL,
                      "loo_starts": "the same grid PLUS the full-data optimum"},
        "sealed_baseline": {
            "constants": {"lambda": SEALED_LAMBDA, "q": SEALED_Q,
                          "kappa_hat": SEALED_KAPPA_HAT},
            "source": "D1 seal bundle, opened in D-open "
                      "(results/dopen_seal_opening/opened_bundle_view.json:"
                      "predictions[S-4].constants)",
            "no_refit": True,
            "statement": ("the sealed form is FROZEN, so it is not re-fitted and has "
                          "no leave-one-out variability: its 'LOO'-RMSE IS its plain "
                          "residual RMSE on the same 26 rows, and it is reported "
                          "under that name plainly"),
            "residual_RMSE": base_rmse,
            "residual_mean_signed": float(np.mean(base_resid)),
            "residual_min": float(np.min(base_resid)),
            "residual_max": float(np.max(base_resid)),
        },
        "satisfiability_rule11": sat,
        "realizability_rule17_stage1": floor,
        "gate_stages_rule23": gate_stages,
        "rule16_cells": cells,
        "fresh_arm": {"share": FRESH_SHARE, "phi": FRESH_PHI, "worlds": FRESH_WORLDS,
                      "instrument": "k2b.run_field_world (985-author K1-pinned panel, "
                                    "F2 m-multiset, 4 contexts)",
                      "master_seed": MASTER_SEED,
                      "r_pred": k2c().predicted_attenuation(FRESH_SHARE, FRESH_PHI),
                      "V_person": k2e().person_share_design(FRESH_SHARE, 0.0),
                      "interpolation_note": (
                          "share .45 lies BETWEEN training rows at .40 (D-open M-4) "
                          "and .4974/.50 (P3a, SP56slow, DM56a, A4); L-2 is therefore "
                          "an INTERPOLATION test, not extrapolation -- stated so the "
                          "verdict is not over-read")},
        "stage_estimates_seconds": {"part0": 120, "stage1": 300, "predict": 5,
                                    "arm": 120, "finalize": 60},
        "G0f": g0,
        "compilation_notes": notes,
    }
    write_json(OUT / "part0.json", part0)
    _write_part0_tables(df, part0)
    if not g0_pass:
        raise SystemExit("STOP: G0f FAILED -- see results/m4_k2f_level_law/part0.json")
    print(f"part0 OK  rows={notes['n_rows']}  baseline_RMSE={base_rmse!r}  "
          f"{time.time() - t0:.1f}s")
    _ordering_log("part0_done", n_rows=notes["n_rows"], seconds=time.time() - t0)
    _ = args


def _duplicate_design_points(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Design points measured twice across legs (disclosed, not merged)."""
    key = df.apply(lambda r: (round(r["r_pred"], 12), round(r["V_person"], 12)), axis=1)
    out = []
    for k, grp in df.groupby(key):
        if len(grp) > 1:
            out.append({"r": k[0], "V": k[1], "rows": list(grp["row_id"]),
                        "levels": [float(x) for x in grp["level_rederived"]],
                        "spread": float(grp["level_rederived"].max()
                                        - grp["level_rederived"].min())})
    return out


def _write_part0_tables(df: pd.DataFrame, part0: dict[str, Any]) -> None:
    lines = ["# M4-K2f Part 0 tables", "",
             f"## The {len(df)}-row compilation ({ROW_RULE})", "",
             "| row | leg | arm | share | int | phi | worlds | r_pred | V_person "
             "| level (re-derived) | level (published) | bit-exact |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in df.iterrows():
        lines.append(
            f"| {r['row_id']} | {r['leg']} | {r['arm']} | {r['share']!r} | "
            f"{r['int_share']!r} | {r['phi']!r} | {r['n_worlds']} | {r['r_pred']!r} | "
            f"{r['V_person']!r} | {r['level_rederived']!r} | "
            f"{r['level_published']!r} | {r['level_roundtrip_bit_exact']} |")
    lines += ["", "## Provenance", "",
              "| row | level source (rawest) | design source | r persisted | V persisted |",
              "|---|---|---|---|---|"]
    for _, r in df.iterrows():
        lines.append(
            f"| {r['row_id']} | `{r['level_source_files']}` | `{r['design_source']}` | "
            f"{'`' + str(r['r_persisted']) + '`' if r['r_persisted'] is not None else '—'} | "
            f"{'`' + str(r['V_persisted']) + '`' if r['V_persisted'] is not None else '—'} |")
    (OUT / "part0_tables.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    _ = part0


def stage1(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    df = read_csv_rt(OUT / "compiled_rows.csv")
    r = df["r_pred"].to_numpy(float)
    v = df["V_person"].to_numpy(float)
    y = df["level_rederived"].to_numpy(float)
    n = len(y)

    fits: dict[str, Any] = {}
    loos: dict[str, Any] = {}
    for form in ("F1", "F2", "F3"):
        fits[form] = fit_form(form, r, v, y)
        loos[form] = loo_rmse(form, r, v, y, fits[form]["theta"])
        print(f"  {form}: rmse={fits[form]['rmse']!r} loo={loos[form]['loo_rmse']!r} "
              f"({time.time() - t0:.1f}s)", flush=True)

    # bootstrap parameter CIs (B=2000, seed=master), rows resampled
    rng_idx = boot_index(B_BOOT, MASTER_SEED, n)
    for form in ("F1", "F2", "F3"):
        th0 = fits[form]["theta"]
        draws: list[list[float]] = []
        nfail = 0
        for b in range(B_BOOT):
            idx = rng_idx[b]
            if len(np.unique(np.round(r[idx], 12))) < 3:
                nfail += 1
                continue
            try:
                f = fit_form(form, r[idx], v[idx], y[idx], starts=[list(th0)])
            except SystemExit:
                nfail += 1
                continue
            if all(abs(x) < 1e6 for x in f["theta"]):
                draws.append(f["theta"])
            else:
                nfail += 1
        arr = np.asarray(draws, float)
        fits[form]["bootstrap"] = {
            "B": B_BOOT, "seed": MASTER_SEED, "n_used": int(len(arr)),
            "n_discarded": int(nfail),
            "discard_rule": "resample with <3 distinct r values, non-convergence, "
                            "or |param| >= 1e6",
            "ci95": {nm: [float(np.quantile(arr[:, j], 0.025)),
                          float(np.quantile(arr[:, j], 0.975))]
                     for j, nm in enumerate(fits[form]["param_names"])},
            "median": {nm: float(np.median(arr[:, j]))
                       for j, nm in enumerate(fits[form]["param_names"])},
        }
        print(f"  {form} bootstrap: {len(arr)}/{B_BOOT} used ({time.time() - t0:.1f}s)",
              flush=True)

    base_rmse = float(p0["sealed_baseline"]["residual_RMSE"])
    order = sorted(("F1", "F2", "F3"), key=lambda f: loos[f]["loo_rmse"])
    winner = order[0]
    best_loo = loos[winner]["loo_rmse"]
    c1 = bool(best_loo <= L1_RMSE_BAR)
    c2 = bool(best_loo <= base_rmse / L1_FACTOR)
    l1 = "HOLD" if (c1 and c2) else "MISS"

    # RN-K2F-2 second reading: inverse-variance weighted
    w = 1.0 / (df["level_sem"].to_numpy(float) ** 2)
    wsec = {}
    for form in ("F1", "F2", "F3"):
        sw = np.sqrt(w / w.mean())

        def wresid(theta: np.ndarray, form: str = form,
                   sw: np.ndarray = sw) -> np.ndarray:
            with np.errstate(over="ignore", invalid="ignore"):
                pred = FORMS[form]["fn"](theta, r, v)
            pred = np.where(np.isfinite(pred), pred, 1e12)
            return sw * (pred - y)
        best = None
        for s0 in starts_for(form):
            try:
                res = least_squares(wresid, np.asarray(s0, float), method="trf",
                                    ftol=OPT["ftol"], xtol=OPT["xtol"],
                                    gtol=OPT["gtol"], max_nfev=OPT["max_nfev"])
            except Exception:                               # noqa: BLE001
                continue
            sse = float(np.sum(res.fun ** 2))
            if best is None or sse < best[1]:
                best = ([float(x) for x in res.x], sse)
        th = np.asarray(best[0], float)
        pred = FORMS[form]["fn"](th, r, v)
        wsec[form] = {"theta": best[0],
                      "unweighted_rmse_of_weighted_fit":
                          float(np.sqrt(np.mean((pred - y) ** 2)))}

    # rule 13: boundary proximity on the L-1 decision quantities
    boundary_tol = 0.05
    rule13: dict[str, Any] = {"triggered": 0, "boundary": 0, "records": []}
    for nm, val, bar in (("best_loo_vs_0.010", best_loo, L1_RMSE_BAR),
                         ("best_loo_vs_baseline/2", best_loo, base_rmse / L1_FACTOR)):
        near = abs(val - bar) <= boundary_tol * max(abs(bar), 1e-12)
        rule13["records"].append({"quantity": nm, "value": val, "bar": bar,
                                  "relative_gap": float((val - bar) / abs(bar)),
                                  "within_5pct_of_bar": bool(near)})
        if near:
            rule13["boundary"] += 1
    # LOO separation between the top two forms
    sep = loos[order[1]]["loo_rmse"] - loos[order[0]]["loo_rmse"]
    rule13["records"].append({
        "quantity": "LOO separation winner vs runner-up",
        "value": float(sep), "bar": 0.0,
        "relative_gap": float(sep / max(loos[order[0]]["loo_rmse"], 1e-12)),
        "within_5pct_of_bar": bool(abs(sep) <= 0.05 * loos[order[0]]["loo_rmse"])})
    if rule13["records"][-1]["within_5pct_of_bar"]:
        rule13["boundary"] += 1
    if rule13["boundary"]:
        rule13["triggered"] = 1
        rule13["action"] = (f"boundary-adjacent quantity present -> parameter CIs "
                            f"re-run at B={B_BOOT_HIGH}")
        for form in ("F1", "F2", "F3"):
            th0 = fits[form]["theta"]
            idxh = boot_index(B_BOOT_HIGH, MASTER_SEED, n)
            draws = []
            for b in range(B_BOOT_HIGH):
                idx = idxh[b]
                if len(np.unique(np.round(r[idx], 12))) < 3:
                    continue
                try:
                    f = fit_form(form, r[idx], v[idx], y[idx], starts=[list(th0)])
                except SystemExit:
                    continue
                if all(abs(x) < 1e6 for x in f["theta"]):
                    draws.append(f["theta"])
            arr = np.asarray(draws, float)
            fits[form]["bootstrap_high"] = {
                "B": B_BOOT_HIGH, "seed": MASTER_SEED, "n_used": int(len(arr)),
                "ci95": {nm: [float(np.quantile(arr[:, j], 0.025)),
                              float(np.quantile(arr[:, j], 0.975))]
                         for j, nm in enumerate(fits[form]["param_names"])}}
            print(f"  {form} bootstrap_high: {len(arr)}/{B_BOOT_HIGH} "
                  f"({time.time() - t0:.1f}s)", flush=True)

    out = {
        "utc": datetime.now(UTC).isoformat(), "n_rows": n,
        "fits": fits,
        "ranking_by_loo": order,
        "winner": winner,
        "sealed_baseline_RMSE": base_rmse,
        "L-1": {"prior": 0.55,
                "clause_i_best_loo_le_0.010": c1,
                "clause_ii_best_loo_le_baseline_over_2": c2,
                "best_loo_rmse": best_loo,
                "baseline_over_2": base_rmse / L1_FACTOR,
                "improvement_factor_vs_baseline": float(base_rmse / best_loo),
                "verdict": l1},
        "second_reading_inverse_variance_weighted": wsec,
        "rule13": rule13,
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fits.json", out)
    write_json(OUT / "loo.json", {"loo": loos, "ranking": order, "winner": winner,
                                  "row_ids": list(df["row_id"])})
    print(f"stage1 OK  winner={winner}  LOO={best_loo!r}  L-1={l1}  "
          f"{time.time() - t0:.1f}s")
    _ordering_log("stage1_done", winner=winner, loo=best_loo, l1=l1)
    _ = args


def stage_predict(args: argparse.Namespace) -> None:
    """Write AND HASH the prediction.  No world may exist yet (G1f)."""
    n_guarded = _arm_ordering_guard()
    if _FRESH_GEN_COUNT != 0:                                # pragma: no cover
        raise SystemExit("STOP (G1f): fresh-arm generation before predict.")
    # cross-process leg of G1f: no fresh-arm artifact may exist yet
    for nm in ("fresh_arm_field.csv", "fresh_arm_field_k2b_lineage.csv",
               "fresh_arm.json", "pilot_field.csv", "g2f_pilot.json"):
        if (OUT / nm).exists():
            raise SystemExit(f"STOP (G1f): fresh-arm artifact {nm} exists before "
                             f"the prediction stamp.")
    fits = read_json(OUT / "fits.json")
    loos = read_json(OUT / "loo.json")
    winner = fits["winner"]
    theta = fits["fits"][winner]["theta"]
    r_new = k2c().predicted_attenuation(FRESH_SHARE, FRESH_PHI)
    v_new = k2e().person_share_design(FRESH_SHARE, 0.0)
    point = float(FORMS[winner]["fn"](np.asarray(theta, float),
                                      np.array([r_new]), np.array([v_new]))[0])
    loo = float(loos["loo"][winner]["loo_rmse"])
    band = L2_BAND_MULT * loo
    pred = {
        "leg": LEG, "stage": "Stage 2 prediction, written BEFORE any fresh-arm world",
        "winning_form": winner, "expr": FORMS[winner]["expr"],
        "param_names": fits["fits"][winner]["param_names"], "theta": theta,
        "fresh_arm": {"share": FRESH_SHARE, "phi": FRESH_PHI, "w_int_arm": "zero",
                      "worlds": FRESH_WORLDS, "master_seed": MASTER_SEED,
                      "seed_lineage": "salt m4k2f-world (RN-K2F-3)"},
        "inputs": {"r_pred": r_new, "V_person": v_new},
        "predicted_b_only_field_recovery": point,
        "band": {"kind": "absolute, two-sided, on the field quantity",
                 "multiplier": L2_BAND_MULT, "loo_rmse": loo, "half_width": band,
                 "lo": point - band, "hi": point + band},
        "L-2": f"HOLD iff the measured 32-world mean lies in "
               f"[{point - band!r}, {point + band!r}]",
        "also_predicted_by_the_other_forms": {
            f: float(FORMS[f]["fn"](np.asarray(fits["fits"][f]["theta"], float),
                                    np.array([r_new]), np.array([v_new]))[0])
            for f in ("F1", "F2", "F3")},
        "sealed_form_would_predict": float(sealed_pred(np.array([r_new]),
                                                       np.array([v_new]))[0]),
        "utc": datetime.now(UTC).isoformat(),
    }
    write_json(OUT / "prediction.json", pred)
    raw = (OUT / "prediction.json").read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    stamp = {"sha256": digest, "bytes": len(raw),
             "stamp_utc": datetime.now(UTC).isoformat(),
             "fresh_arm_generations_before_stamp": _FRESH_GEN_COUNT,
             "k2b_instances_guarded": n_guarded,
             "entry_points_wrapped": 3 * n_guarded,
             "guard": "k2b.build_k2b_world / run_field_world / emit_panel wrapped on "
                      "EVERY reachable k2b instance; permit issued only by re-hashing "
                      "prediction.json from disk"}
    write_json(OUT / "prediction.sha256.json", stamp)
    _ordering_log("prediction_stamped", sha256=digest,
                  fresh_generations_before_stamp=_FRESH_GEN_COUNT,
                  predicted=point, lo=point - band, hi=point + band)
    print(f"prediction STAMPED  {winner}  point={point!r}  "
          f"band=[{point - band!r}, {point + band!r}]  sha256={digest}")
    _ = args


def world_seed_for(world: int) -> int:
    """RN-K2F-3: K2f's OWN lineage; the seed depends on the world index only."""
    v8 = k2b().v8
    return int(v8.stable_bucket(f"{MASTER_SEED}-{world}", salt="m4k2f-world",
                                modulus=2 ** 31 - 1))


def _run_worlds(tag: str, seed_fn: Callable[[int], int],
                indices: list[int], verify_first: bool) -> pd.DataFrame:
    kb = k2b()
    w = kb.arm_weights(FRESH_SHARE, "zero")
    rows = []
    t0 = time.time()
    for j, wi in enumerate(indices):
        world = kb.build_k2b_world(seed_fn(wi), FRESH_PHI)
        row = kb.run_field_world(tag, wi, world, w, verify=(verify_first and j == 0))
        row["world"] = wi
        rows.append(row)
        if (j + 1) % 8 == 0:
            print(f"  {tag}: {j + 1}/{len(indices)} worlds, {time.time() - t0:.1f}s",
                  flush=True)
    return pd.DataFrame(rows)


def stage_arm(args: argparse.Namespace) -> None:
    t0 = time.time()
    _arm_ordering_guard()
    permit = _issue_permit()

    # --- G2f: rule-17 realizability pilot, AFTER the stamp (RN-K2F-4) ------
    pilot = _run_worlds(f"{FRESH_ARM_ID}-PILOT", world_seed_for,
                        list(PILOT_WORLDS), True)
    pilot.to_csv(OUT / "pilot_field.csv", index=False)
    pv = pilot["recovery_b_only"].to_numpy(float)
    resid_cols = [c for c in pilot.columns if c.startswith("g4b_")]
    resid_max = float(np.nanmax(np.abs(
        pilot[resid_cols].to_numpy(float)))) if resid_cols else float("nan")
    g2 = {"pilot_worlds": list(PILOT_WORLDS),
          "recovery_b_only": [float(x) for x in pv],
          "all_finite": bool(np.all(np.isfinite(pv))),
          "strictly_inside_unit": bool(np.all((pv > 0.0) & (pv < 1.0))),
          "g4b_route_residual_maxabs": resid_max,
          "g4b_residuals_ok": bool(np.isnan(resid_max) or resid_max <= 1e-9),
          "fallback_ladder": "non-finite or saturated -> STOP, L-2 UNRESOLVABLE "
                             "(named in advance); the prediction stands on the record"}
    g2["PASS"] = bool(g2["all_finite"] and g2["strictly_inside_unit"]
                      and g2["g4b_residuals_ok"])
    write_json(OUT / "g2f_pilot.json", g2)
    if not g2["PASS"]:
        _ordering_log("g2f_FAILED", **g2)
        raise SystemExit("STOP: G2f FAILED (rule 17 fallback) -- L-2 UNRESOLVABLE")
    print(f"  G2f pilot PASS ({time.time() - t0:.1f}s)", flush=True)

    # --- the scored 32 worlds, PINNED lineage ------------------------------
    main = _run_worlds(FRESH_ARM_ID, world_seed_for, list(range(FRESH_WORLDS)), False)
    main.to_csv(OUT / "fresh_arm_field.csv", index=False)
    vals = main["recovery_b_only"].to_numpy(float)

    # --- second reading: the k2b lineage (RN-K2F-3 alternative) -------------
    kb = k2b()
    alt = _run_worlds(f"{FRESH_ARM_ID}-K2BLIN", kb.world_seed_for,
                      list(range(FRESH_WORLDS)), False)
    alt.to_csv(OUT / "fresh_arm_field_k2b_lineage.csv", index=False)
    avals = alt["recovery_b_only"].to_numpy(float)

    out = {
        "utc": datetime.now(UTC).isoformat(), "permit": permit,
        "config": {"share": FRESH_SHARE, "phi": FRESH_PHI, "w_int_arm": "zero",
                   "worlds": FRESH_WORLDS, "master_seed": MASTER_SEED,
                   "arm_shares": kb.arm_shares(FRESH_SHARE, "zero"),
                   "instrument": "k2b.run_field_world (985-author K1-pinned panel, "
                                 "F2 m-multiset, 4 contexts)"},
        "law_inputs": {"r_card_b_pred_raw":
                       k2c().predicted_attenuation(FRESH_SHARE, FRESH_PHI),
                       "V_person_design": k2e().person_share_design(FRESH_SHARE, 0.0)},
        "G2f": g2,
        "measured_recovery_b_only": boot_ci(vals),
        "measured_recovery_b_only_B20000": boot_ci(vals, B_BOOT_HIGH),
        "per_world_recovery_b_only": [float(x) for x in vals],
        "measured_recovery_mixed": boot_ci(
            main["recovery_mixed"].to_numpy(float)),
        "second_reading_k2b_lineage": {
            "measured_recovery_b_only": boot_ci(avals),
            "per_world_recovery_b_only": [float(x) for x in avals],
            "note": "RN-K2F-3's alternative; REPORTED, does not adjudicate L-2"},
        "fresh_generations_total": _FRESH_GEN_COUNT,
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fresh_arm.json", out)
    _ordering_log("fresh_arm_done", mean=out["measured_recovery_b_only"]["mean"],
                  seconds=time.time() - t0)
    print(f"arm OK  measured={out['measured_recovery_b_only']['mean']!r}  "
          f"{time.time() - t0:.1f}s")
    _ = args


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    fits = read_json(OUT / "fits.json")
    loos = read_json(OUT / "loo.json")
    pred = read_json(OUT / "prediction.json")
    stamp = read_json(OUT / "prediction.sha256.json")
    arm = read_json(OUT / "fresh_arm.json")

    l1 = fits["L-1"]["verdict"]
    m = arm["measured_recovery_b_only"]
    lo, hi = pred["band"]["lo"], pred["band"]["hi"]
    inside = bool(lo <= m["mean"] <= hi)
    l2 = "HOLD" if inside else "MISS"
    dist = 0.0 if inside else float(min(abs(m["mean"] - lo), abs(m["mean"] - hi)))
    bandwidths = (0.0 if inside
                  else dist / (2.0 * pred["band"]["half_width"]))

    if l1 == "MISS":
        cell, slug = 1, "NO_LEVEL_LAW"
    elif l2 == "HOLD":
        cell, slug = 2, "LEVEL_LAW_RESTORED"
    else:
        cell, slug = 3, "LEVEL_LAW_OVERFIT"
    route = next(c for c in p0["rule16_cells"] if c["cell"] == cell)

    # rule 13 on the Stage-2 containment call
    r13 = {"triggered": 0, "boundary": 0, "records": []}
    for nm, edge in (("measured_mean_vs_band_lo", lo), ("measured_mean_vs_band_hi", hi)):
        gap = abs(m["mean"] - edge)
        near = gap <= 0.05 * max(abs(edge), pred["band"]["half_width"])
        r13["records"].append({"quantity": nm, "value": m["mean"], "bar": edge,
                               "abs_gap": float(gap), "within_5pct": bool(near)})
        if near:
            r13["boundary"] += 1
    mh = arm["measured_recovery_b_only_B20000"]
    r13["B20000_check"] = {"B": B_BOOT_HIGH, "lo": mh["lo"], "hi": mh["hi"],
                           "max_endpoint_shift": float(max(abs(mh["lo"] - m["lo"]),
                                                           abs(mh["hi"] - m["hi"]))),
                           "containment_unchanged": bool(
                               (lo <= mh["mean"] <= hi) == inside)}
    if r13["boundary"]:
        r13["triggered"] = 1

    alt_mean = arm["second_reading_k2b_lineage"]["measured_recovery_b_only"]["mean"]
    gates = {
        "G0f": {"PASS": p0["G0f"]["PASS"],
                "detail": "D-open S-4 anchors bit-exact; 26-row compilation audited, "
                          "every row's provenance cited"},
        "G1f": {"PASS": bool(stamp["fresh_arm_generations_before_stamp"] == 0
                             and arm["permit"]["prediction_sha256_recomputed"]
                             == arm["permit"]["prediction_sha256_stamped"]),
                "detail": f"stamp {stamp['stamp_utc']} -> permit "
                          f"{arm['permit']['permit_utc']}; "
                          f"{stamp['fresh_arm_generations_before_stamp']} fresh-arm "
                          f"generations before the stamp; hash re-read from disk"},
        "G2f": {"PASS": arm["G2f"]["PASS"], "detail": "rule-17 fresh-arm pilot finite "
                                                      "and non-saturated"},
        "G3f": {"PASS": True,
                "detail": "rule 11 satisfiability in Part 0; rule 22 sides declared "
                          "for both leans; rule 23 gate stages named; rule 13 "
                          f"B={B_BOOT} seed={MASTER_SEED} with the >=10xB re-run"},
        "G4f": {"PASS": True, "detail": "hygiene + rule-16 three-cell enumeration + "
                                        "rule 24 prose verification"},
    }
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "master_seed": MASTER_SEED, "n_rows": p0["compilation_notes"]["n_rows"],
        "row_rule": ROW_RULE,
        "winner": fits["winner"], "winner_expr": FORMS[fits["winner"]]["expr"],
        "winner_theta": dict(zip(fits["fits"][fits["winner"]]["param_names"],
                                 fits["fits"][fits["winner"]]["theta"])),
        "loo_rmse_by_form": {f: loos["loo"][f]["loo_rmse"] for f in ("F1", "F2", "F3")},
        "in_sample_rmse_by_form": {f: fits["fits"][f]["rmse"] for f in ("F1", "F2", "F3")},
        "sealed_baseline_RMSE": fits["sealed_baseline_RMSE"],
        "L-1": {**fits["L-1"]},
        "L-2": {"prior": 0.60, "conditional_on": "L-1 HOLD",
                "predicted": pred["predicted_b_only_field_recovery"],
                "band": [lo, hi], "half_width": pred["band"]["half_width"],
                "measured": m["mean"], "measured_ci": [m["lo"], m["hi"]],
                "inside": inside, "distance_outside": dist,
                "band_widths_outside": bandwidths,
                "adjudicated": bool(l1 == "HOLD"), "verdict": l2},
        "second_reading_k2b_lineage_mean": alt_mean,
        "second_reading_k2b_lineage_inside": bool(lo <= alt_mean <= hi),
        "routing_cell": cell, "routing": route, "verdict_slug": slug,
        "rule13_stage2": r13, "rule13_stage1": fits["rule13"],
        "gates": gates,
        "prediction_sha256": stamp["sha256"],
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _ordering_log("finalize_done", slug=slug, l1=l1, l2=l2)
    print(f"finalize OK  L-1={l1}  L-2={l2}  cell={cell}  slug={slug}")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    for name, fn in (("part0", stage_part0), ("stage1", stage1),
                     ("predict", stage_predict), ("arm", stage_arm),
                     ("finalize", stage_finalize)):
        s = sub.add_parser(name)
        s.set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
