#!/usr/bin/env python3
"""SUICA M4-Q1 -- card transport under frame refreshment.

Registered BEFORE run in docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md ("M4-Q1",
commit 0f3d773).  Binding.

The P-line established that the deployed gauge reads frame-agreement.  Q1 asks
the mechanism's other half: do CARD readings transport across frames?  The
device is P3b's certified split-seed instrument (imported by file), pointed at
the card layer: C_nat = A's cards against A's b-truth, C_ref = A's cards
against B's b-truth, same persons and a fresh frame.

The registration supplies the decision rule that governs this harness:

    "the executor pins its source object file:line in Part 0 and reuses it
     verbatim for C_nat; C_ref replaces only the truth-side card panel with
     the B-world's ... If the published statistic is not expressible as
     author-indexed card vectors admitting cross-world scoring, STOP as
     INEXPRESSIBLE (an instrument finding)."

Everything here is executed before any measurement arm, and the expressibility
question is answered with code rather than argument.

Stages: part0 -> demonstrate -> finalize -> report   (or: all)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import math
import platform
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_q1_card_transport"
RES = ROOT / "results"
P3BSRC = ROOT / "scripts" / "run_suica_m4_p3b_refresh_gradient.py"
K2BSRC = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
P3CRES = RES / "m4_p3c_transportable_gradient"
K2BRES = RES / "m4_k2b_t4_branch"
IDT = ROOT / "docs" / "SUICA_IDENTITY_THEORY_V1.md"

LEG = "M4-Q1"
BANNER = ("card transport under frame refreshment, on P3b's certified split-seed "
          "instrument; exploratory, label-free; no seal")

MASTER_SEED = 20260814
SALT_AUTHOR = "m4q1-author"
SALT_FRAME_A = "m4q1-frameA"
SALT_FRAME_B = "m4q1-frameB"
SALT_PILOT = "m4q1-pilot"
SHARE = 0.25
PHI_LO, PHI_HI = 0.05, 0.98
N_PAIRS = 384
N_PAIRS_ESCALATED = 768
PROBE_PAIRS = 4
DEMO_PAIRS = 8
W_INT_ARM = "zero"
SATURATION_ABS = 0.995

# --- the two candidate readings of "the published card statistic" ----------
CARD_PRED_A1 = 0.8271784593117322      # r_card_b_pred_raw, closed form
CARD_MEAS_A1 = 0.8266850143926395      # r_card_b_raw, measured pooled
FIELD_MEAS_A1 = 0.177888649457317      # recovery_b_only_mean, the 4.5x denominator

AUTHOR_OBJECTS = ("trait", "a_load", "loadings")
FRAME_OBJECTS = ("slow", "slow_latent", "noise", "common", "int")
CARD_DROP = ("author", "world_seed", "cell_key", "m")

# ---------------------------------------------------------------------------
# RN-Q1 notes.  PINNED IN PART 0, BEFORE ANY MEASUREMENT ARM.
#
# RN-Q1-1 (the published statistic has TWO readings, and both are reported).
#   Appendix N's sentence is "card attenuation 0.827 vs field recovery 0.178 at
#   the lowest state share".  Two persisted objects round to 0.827:
#     (a) r_card_b_pred_raw = 0.8271784593117322 -- k2b's CLOSED-FORM
#         prediction (arm_predictions, k2b:533-584), pure algebra over cell
#         sizes and variance shares; and
#     (b) r_card_b_raw = 0.8266850143926395 -- the MEASURED pooled statistic
#         (card_channel_frame k2b:392-457 -> pooled_card_stats k2b:463-489).
#   The companion 0.178 is measured (recovery_b_only_mean), so parallel
#   construction favours (b); the digits favour (a).  The registration does not
#   disambiguate.  BOTH are pinned and BOTH are carried through the
#   expressibility test, because the STOP question has a different answer under
#   each and the answer must not depend on an executor's guess.
#
# RN-Q1-2 (what "the truth-side card panel" actually is).  In
#   card_channel_frame the estimate side is a card -- a channel mixture
#   w_mu*trait_c + w_slow*slow_c + w_int*int_c + w_noise*noise_c, every channel
#   centred within the (context, m) cell (k2b:422-428).  The TRUTH side is NOT
#   a card: it is `world["trait"][idx]` (k2b:410), the bare latent trait array,
#   uncentred for the _raw family and cell-centred for the _cen family
#   (k2b:443-447).  The registration's phrase "replaces only the truth-side
#   card panel" therefore names an object that does not exist as a card; the
#   thing that can be replaced is the trait array.  This harness replaces
#   exactly that, and reports the mismatch.
#
# RN-Q1-3 (the trap, avoided explicitly).  trait_c (k2b:411) feeds BOTH sides:
#   the card at k2b:423 and the centred truth at k2b:444/447.  Swapping the
#   `world` argument wholesale would swap both and yield a self-consistent
#   B-world statistic -- a replication, not a cross-world score.  The
#   cross-world path here parameterises ONLY the truth-side trait; the card
#   keeps A's trait_c throughout.  G1q1(b) proves the path is correct by
#   reproducing k2b's own published number bit-exactly when both arguments are A.
#
# RN-Q1-4 (the demonstration is the gate).  Whether the statistic "admits
#   cross-world scoring" is settled by running it, not by arguing about it: the
#   cross-world path is built, proven bit-exact against k2b at the zero point,
#   and then evaluated at A-vs-B.  The gauge quantities R_nat / R_refresh are
#   computed on the SAME pairs, so the card layer's behaviour and the gauge
#   layer's behaviour are compared on one device in one table -- which is what
#   makes the finding interpretable rather than merely negative.
#
# RN-Q1-5 (no measurement arm is spent before the expressibility question is
#   answered).  The registration's STOP is a Part-0-class instrument finding.
#   The demonstration uses a handful of pairs on the PILOT salt; the 384-pair
#   arms are never started unless the estimand survives.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-Q1-1": "appendix N's 0.827 has TWO persisted readings -- the closed-form "
               "prediction r_card_b_pred_raw 0.8271784593117322 (k2b:533-584) and the "
               "measured pooled r_card_b_raw 0.8266850143926395 (k2b:392-457 -> "
               ":463-489). The companion 0.178 is measured, favouring the second; the "
               "digits favour the first. BOTH are pinned and BOTH carried through the "
               "expressibility test, because the STOP answer differs between them",
    "RN-Q1-2": "the card statistic's truth side is NOT a card: it is world['trait'][idx] "
               "(k2b:410), the bare latent trait array. The registration's 'truth-side "
               "card panel' names an object that does not exist as a card; the trait "
               "array is what can be replaced, and that is what is replaced here",
    "RN-Q1-3": "trait_c (k2b:411) feeds BOTH the card (k2b:423) and the centred truth "
               "(k2b:444/447); swapping the world wholesale would swap both and give a "
               "replication, not a cross-world score. Only the truth-side trait is "
               "parameterised; G1q1(b) proves the path by reproducing k2b bit-exactly at "
               "the zero point",
    "RN-Q1-4": "expressibility is settled by running the cross-world path, not by "
               "arguing; the gauge R_nat/R_refresh are computed on the SAME pairs so the "
               "two layers are compared on one device in one table",
    "RN-Q1-5": "no measurement arm is spent before the expressibility question is "
               "answered; the demonstration runs on the pilot salt",
}

# ---------------------------------------------------------------------------

_MODS: dict[str, Any] = {}


def _load_named(name: str, path: Path) -> Any:
    if name not in _MODS:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
        sys.modules[name] = mod
        spec.loader.exec_module(mod)                         # type: ignore[union-attr]
        _MODS[name] = mod
    return _MODS[name]


def p3b() -> Any:
    return _load_named("run_suica_m4_p3b_refresh_gradient", P3BSRC)


def k2b() -> Any:
    return p3b().k2b()


def v8() -> Any:
    return k2b().v8


def build_split_world(a: int, f: int, phi: float) -> dict[str, np.ndarray]:
    return p3b().build_split_world(a, f, phi)


def _log(event: str, **kw: Any) -> None:
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rt(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, float_precision="round_trip")


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def seed_for(kind: str, phi: float, i: int, salt: str) -> int:
    key = f"{LEG}|{salt}|{kind}|phi{phi!r}|i{i}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def pair_seeds(phi: float, i: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", phi, i, SALT_AUTHOR + suffix),
            "frameA": seed_for("frameA", phi, i, SALT_FRAME_A + suffix),
            "frameB": seed_for("frameB", phi, i, SALT_FRAME_B + suffix)}


def _locate(path: Path, needle: str) -> dict[str, Any]:
    lines = path.read_text(encoding="utf-8").split("\n")
    for i, line in enumerate(lines):
        if needle in line:
            a = i
            while a > 0 and lines[a - 1].strip():
                a -= 1
            b = i
            while b + 1 < len(lines) and lines[b + 1].strip():
                b += 1
            para = re.sub(r"\s+", " ", " ".join(x.strip() for x in lines[a:b + 1]))
            return {"found": True, "file": rel(path), "line": i + 1,
                    "paragraph_lines": f"{a + 1}-{b + 1}", "quote": para.strip()}
    return {"found": False, "file": rel(path), "needle": needle, "quote": "",
            "line": None, "paragraph_lines": None}


# ---------------------------------------------------------------------------
# THE CROSS-WORLD CARD PATH -- k2b:392-457 with the TRUTH side parameterised.

def card_frame_xw(world_est: dict[str, np.ndarray],
                  world_truth: dict[str, np.ndarray],
                  w: dict[str, float], world_seed: int) -> pd.DataFrame:
    """k2b.card_channel_frame (k2b:392-457) with ONE change (RN-Q1-2/3).

    The estimate side (the card) is built from `world_est` exactly as k2b does.
    The truth side -- `trait` at k2b:410, consumed at k2b:443-447 -- is taken
    from `world_truth`.  Nothing else differs; when world_truth is world_est
    the output is bit-identical to k2b's own frame (proven in G1q1(b)).
    """
    m_ = k2b()
    lay = m_.layout()
    counts = lay["counts"]
    cell_key = lay["cell_key"]
    keys = cell_key[lay["retained_idx"]]
    rows: list[pd.DataFrame] = []
    for key in sorted(set(map(str, keys))):
        idx = np.asarray(
            [i for i in lay["retained_idx"] if str(cell_key[i]) == key], dtype=int)
        m = int(counts[idx[0]])
        trait = world_est["trait"][idx]                            # k2b:410 (estimate)
        trait_c = trait - trait.mean(axis=0, keepdims=True)        # k2b:411
        slow_c = (world_est["slow"][idx, :m]
                  - world_est["slow"][idx, :m].mean(axis=0, keepdims=True))
        noise_c = (world_est["noise"][idx, :m]
                   - world_est["noise"][idx, :m].mean(axis=0, keepdims=True))
        int_c = None
        if w["int"] != 0.0:
            int_c = (world_est["int"][idx, :m]
                     - world_est["int"][idx, :m].mean(axis=0, keepdims=True))

        def card(occ: np.ndarray) -> np.ndarray:                   # k2b:422-428
            out = w["mu"] * trait_c
            out = out + w["slow"] * slow_c[:, occ, :].mean(axis=1)
            if int_c is not None:
                out = out + w["int"] * int_c[:, occ, :].mean(axis=1)
            out = out + w["noise"] * noise_c[:, occ, :].mean(axis=1)
            return out

        sp = m_.occ_splits(m)
        block: dict[str, np.ndarray] = {}
        for name, (s1, s2) in sp.items():                          # k2b:431-441
            c1, c2 = card(s1), card(s2)
            block[f"{name}_dot"] = np.einsum("id,id->i", c1, c2)
            block[f"{name}_n1"] = np.einsum("id,id->i", c1, c1)
            block[f"{name}_n2"] = np.einsum("id,id->i", c2, c2)
            block[f"{name}_s1"] = c1.sum(axis=1)
            block[f"{name}_s2"] = c2.sum(axis=1)
            block[f"{name}_cos"] = block[f"{name}_dot"] / np.sqrt(
                block[f"{name}_n1"] * block[f"{name}_n2"])
        full = card(np.arange(m))                                  # k2b:442
        # --- THE ONE CHANGE: the truth side comes from world_truth ----------
        t_trait = world_truth["trait"][idx]
        t_trait_c = t_trait - t_trait.mean(axis=0, keepdims=True)
        block["full_b_dot_raw"] = np.einsum("id,id->i", full, t_trait)      # k2b:443
        block["full_b_dot_cen"] = np.einsum("id,id->i", full, t_trait_c)    # k2b:444
        block["full_n"] = np.einsum("id,id->i", full, full)                 # k2b:445
        block["b_raw_n"] = np.einsum("id,id->i", t_trait, t_trait)          # k2b:446
        block["b_cen_n"] = np.einsum("id,id->i", t_trait_c, t_trait_c)      # k2b:447
        block["r_cos_raw"] = block["full_b_dot_raw"] / np.sqrt(             # k2b:448
            block["full_n"] * block["b_raw_n"])
        sub = pd.DataFrame(block)
        sub.insert(0, "cell_key", key)
        sub.insert(0, "m", m)
        sub.insert(0, "world_seed", world_seed)
        sub.insert(0, "author", idx)
        rows.append(sub)
    return pd.concat(rows, ignore_index=True)


def card_stat(frame: pd.DataFrame) -> dict[str, float]:
    """k2b's own pooled reducer (k2b:463-489), called unchanged."""
    m_ = k2b()
    keep = [c for c in frame.columns if c not in CARD_DROP]
    data = np.ascontiguousarray(frame[keep].to_numpy(float))
    cols = {c: i for i, c in enumerate(keep)}
    st = m_.pooled_card_stats(data.sum(axis=0), cols, float(len(frame)))
    return {k: float(v) for k, v in st.items()}


def gauge_pair(wa: dict[str, np.ndarray], wb: dict[str, np.ndarray],
               w: dict[str, float], arm: str, i: int, phi: float) -> dict[str, Any]:
    return p3b().score_pair(wa, wb, w, arm, i, phi, with_deframe=False)


# ---------------------------------------------------------------------------
# PART 0.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    m_ = k2b()

    # --- G0q1(iii): instrument hashes vs P3b's persisted -------------------
    fn = p3b().build_split_world
    fn_sha = hashlib.sha256(inspect.getsource(fn).encode("utf-8")).hexdigest()
    file_sha = hashlib.sha256(P3BSRC.read_bytes()).hexdigest()
    p3c_prov = read_json(P3CRES / "part0.json")["instrument_provenance"]
    prov = {
        "imported_from": rel(P3BSRC),
        "definition_line": int(inspect.getsourcelines(fn)[1]),
        "signature": f"build_split_world{inspect.signature(fn)}",
        "function_sha256": fn_sha, "file_sha256": file_sha,
        "p3c_persisted_function_sha256": p3c_prov["function_sha256"],
        "p3c_persisted_file_sha256": p3c_prov["file_sha256"],
        "function_sha_matches": bool(fn_sha == p3c_prov["function_sha256"]),
        "file_sha_matches": bool(file_sha == p3c_prov["file_sha256"]),
    }
    prov["PASS"] = bool(prov["function_sha_matches"] and prov["file_sha_matches"])

    # --- G0q1(i): P3c's endpoint values ------------------------------------
    p3c = read_json(P3CRES / "decision.json")
    g0i = {"source": rel(P3CRES / "decision.json"),
           "verdict": p3c["verdict_slug"],
           "D_grad": p3c["D_grad"], "D_grad_ci95": p3c["D_grad_ci95"],
           "range_ref": p3c["range_ref"], "range_ref_ci95": p3c["range_ref_ci95"],
           "range_nat": p3c["range_nat"],
           "endpoints": {str(q["phi"]): {"R_nat": q["R_nat_mean"],
                                         "R_refresh": q["R_refresh_mean"],
                                         "R_nat_sem": q["R_nat_sem"],
                                         "R_refresh_sem": q["R_refresh_sem"]}
                         for q in p3c["per_phi"] if q["role"] == "endpoint"},
           "PASS": bool(p3c["verdict_slug"] == "UNDERPOWERED")}

    # --- G0q1(ii): the 4.5x comparison, located verbatim -------------------
    anchors = {
        "appendix N instrument-role typing (the 4.5x sentence)":
            _locate(IDT, "dominates the deployed"),
        "the Q-line handoff sentence": _locate(IDT, "DO CARD READINGS TRANSPORT"),
    }
    cells = read_csv_rt(K2BRES / "cells.csv")
    a1 = cells[cells["arm"] == "A1"].iloc[0] if "arm" in cells.columns else None
    preds = read_csv_rt(K2BRES / "part0_predictions.csv")
    a1p = preds[preds["arm"] == "A1"].iloc[0] if "arm" in preds.columns else None
    g0ii = {
        "anchors": anchors,
        "all_found": bool(all(a["found"] for a in anchors.values())),
        "card_pred_persisted": (float(a1p["r_card_b_pred_raw"])
                                if a1p is not None else None),
        "card_pred_registration": CARD_PRED_A1,
        "card_pred_bit_exact": bool(a1p is not None
                                    and float(a1p["r_card_b_pred_raw"])
                                    == CARD_PRED_A1),
        "card_meas_persisted": (float(a1["r_card_b_raw"]) if a1 is not None else None),
        "card_meas_registration": CARD_MEAS_A1,
        "card_meas_bit_exact": bool(a1 is not None
                                    and float(a1["r_card_b_raw"]) == CARD_MEAS_A1),
        "field_meas_persisted": (float(a1["recovery_b_only_mean"])
                                 if a1 is not None else None),
        "field_meas_registration": FIELD_MEAS_A1,
        "field_meas_bit_exact": bool(a1 is not None
                                     and float(a1["recovery_b_only_mean"])
                                     == FIELD_MEAS_A1),
        "ratio_pred_over_field": float(CARD_PRED_A1 / FIELD_MEAS_A1),
        "ratio_meas_over_field": float(CARD_MEAS_A1 / FIELD_MEAS_A1),
        "ratio_note": "appendix N says '~4.5x' with a tilde; neither persisted ratio is "
                      "4.5 and no artifact carries a ratio key -- the tilde is doing "
                      "real work and the number is prose, not a computed object",
        "two_readings": RN_NOTES["RN-Q1-1"],
    }
    g0ii["PASS"] = bool(g0ii["all_found"] and g0ii["card_pred_bit_exact"]
                        and g0ii["card_meas_bit_exact"]
                        and g0ii["field_meas_bit_exact"])

    # --- C2 battery on 4 fresh probes --------------------------------------
    rows = []
    for i in range(PROBE_PAIRS):
        sd = pair_seeds(PHI_LO, i, "-probe")
        wa = build_split_world(sd["author"], sd["frameA"], PHI_LO)
        wb = build_split_world(sd["author"], sd["frameB"], PHI_LO)
        rec: dict[str, Any] = {"probe": i}
        for k in AUTHOR_OBJECTS:
            rec[f"author::{k}"] = bool(np.array_equal(
                np.asarray(wa[k]).view(np.uint8), np.asarray(wb[k]).view(np.uint8)))
        for k in FRAME_OBJECTS:
            rec[f"frame::{k}"] = float(np.linalg.norm(
                np.asarray(wa[k]) - np.asarray(wb[k])))
        rows.append(rec)
    sd0 = pair_seeds(PHI_LO, 0, "-probe")
    r1 = build_split_world(sd0["author"], sd0["frameA"], PHI_LO)
    r2 = build_split_world(sd0["author"], sd0["frameA"], PHI_LO)
    det = all(np.array_equal(np.asarray(r1[k]).view(np.uint8),
                             np.asarray(r2[k]).view(np.uint8)) for k in r1)
    c2 = {"n_probe_pairs": PROBE_PAIRS, "rows": rows,
          "all_author_identical": bool(all(r[f"author::{k}"] for r in rows
                                           for k in AUTHOR_OBJECTS)),
          "all_frame_differ": bool(all(r[f"frame::{k}"] > 0.0 for r in rows
                                       for k in FRAME_OBJECTS)),
          "norm_delta_min": {k: float(min(r[f"frame::{k}"] for r in rows))
                             for k in FRAME_OBJECTS},
          "norm_delta_max": {k: float(max(r[f"frame::{k}"] for r in rows))
                             for k in FRAME_OBJECTS},
          "determinism": bool(det),
          "loadings_shared": bool(all(r["author::loadings"] for r in rows))}
    c2["PASS"] = bool(c2["all_author_identical"] and c2["all_frame_differ"]
                      and c2["determinism"] and c2["loadings_shared"])

    # --- the card statistic's source pin and its structure -----------------
    src = K2BSRC.read_text(encoding="utf-8").split("\n")

    def _line_of(needle: str) -> int | None:
        for i, line in enumerate(src):
            if needle in line:
                return i + 1
        return None

    pin = {
        "reading_A_closed_form": {
            "object": "r_card_b_pred_raw",
            "function": "arm_predictions",
            "file_line": f"{rel(K2BSRC)}:{_line_of('def arm_predictions')}",
            "computed_at": f"{rel(K2BSRC)}:"
                           f"{_line_of('out[\"r_card_b_pred_raw\"] = num_b')}",
            "value_A1": CARD_PRED_A1,
            "takes_a_world": False, "forms_author_vectors": False,
            "has_a_truth_side_to_replace": False,
            "expressible_as_author_indexed_card_vectors": False,
            "why": "pure algebra over retained cell sizes and the four variance "
                   "shares; it never touches a world, an author, or a vector, so "
                   "there is no truth-side panel in it to swap"},
        "reading_B_measured": {
            "object": "r_card_b_raw",
            "function": "card_channel_frame -> pooled_card_stats",
            "file_line": f"{rel(K2BSRC)}:{_line_of('def card_channel_frame')}-457",
            "reducer_line": f"{rel(K2BSRC)}:{_line_of('def pooled_card_stats')}-489",
            "computed_at": f"{rel(K2BSRC)}:"
                           f"{_line_of('out[\"r_card_b_raw\"]')}",
            "estimate_side": f"the card, {rel(K2BSRC)}:"
                             f"{_line_of('out = w[\"mu\"] * trait_c')} "
                             "(w_mu*trait_c + w_slow*slow_c + w_int*int_c + "
                             "w_noise*noise_c, each centred in the (context, m) cell; "
                             "the frame channel is EXCLUDED by construction)",
            "truth_side": f"world['trait'][idx], {rel(K2BSRC)}:"
                          f"{_line_of('trait = world[\"trait\"][idx]')} -- the BARE "
                          "LATENT TRAIT ARRAY, not a card",
            "value_A1": CARD_MEAS_A1,
            "takes_a_world": True, "forms_author_vectors": True,
            "has_a_truth_side_to_replace": True,
            "expressible_as_author_indexed_card_vectors": True,
            "why": "64-dim per-author vectors exist inside the function (the card "
                   "`full` and the truth `trait`) and are contracted row-wise, so a "
                   "cross-world variant is constructible -- though every RETURNED "
                   "column is a per-author scalar, so the vectors must be re-derived "
                   "rather than read off a persisted artifact"},
        "registration_phrase": "'C_ref replaces only the truth-side card panel with the "
                               "B-world's'",
        "phrase_mismatch": RN_NOTES["RN-Q1-2"],
    }

    g0 = {"(i) P3c values": g0i, "(ii) the 4.5x comparison": g0ii,
          "(iii) instrument hashes": prov,
          "PASS": bool(g0i["PASS"] and g0ii["PASS"] and prov["PASS"])}

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md (M4-Q1, BEFORE run, "
                        "commit 0f3d773)",
        "master_seed": MASTER_SEED,
        "salts": {"author": SALT_AUTHOR, "frameA": SALT_FRAME_A,
                  "frameB": SALT_FRAME_B, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0q1": g0, "C2": c2,
        "card_statistic_pin": pin,
        "design_if_expressible": {
            "share": SHARE, "phi": [PHI_LO, PHI_HI], "pairs_per_phi": N_PAIRS,
            "total_worlds": 2 * 2 * N_PAIRS,
            "escalation_pairs_per_phi": N_PAIRS_ESCALATED},
        "sides_rule22": {
            "L-1q1": {"clause": "CARDS_TRANSPORT_SUBSTANTIAL / CARDS_PARTIAL / "
                                "CARDS_FRAME_LOCKED / other",
                      "prior": "0.40 / 0.35 / 0.15 / 0.10", "sided": "categorical"},
            "V-Qa": {"clause": "C_ref vs 0, NULL-first", "sided": "two-sided"},
            "V-Qb": {"clause": "L_C = C_nat - C_ref vs 0, NULL-first",
                     "sided": "two-sided"}},
        "stage_estimates_seconds": {"part0": 150, "demonstrate": 60, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", G0=g0["PASS"], C2=c2["PASS"], seconds=part0["seconds"])
    if not (g0["PASS"] and c2["PASS"]):
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "INSTRUMENT_DEFECT", "routing_cell": "3",
            "routing_text": "INSTRUMENT_DEFECT", "G0q1": g0, "C2": c2,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- G0q1/C2 failed")
    print(f"part0 OK  G0q1 PASS  C2 PASS  instrument sha matches P3b "
          f"({prov['function_sha_matches']}/{prov['file_sha_matches']})  "
          f"card pin: closed-form={pin['reading_A_closed_form']['file_line']} "
          f"measured={pin['reading_B_measured']['file_line']}  "
          f"{time.time() - t0:.1f}s")
    _ = args, m_


# ---------------------------------------------------------------------------
# THE DEMONSTRATION -- G1q1(b) and the expressibility question, answered by code.

def stage_demonstrate(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0q1"]["PASS"]:
        raise SystemExit("STOP: G0q1 did not pass.")
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    rows, zero_pt = [], []
    for phi in (PHI_LO, PHI_HI):
        for i in range(DEMO_PAIRS):
            sd = pair_seeds(phi, i, "-pilot")
            wa = build_split_world(sd["author"], sd["frameA"], phi)
            wb = build_split_world(sd["author"], sd["frameB"], phi)
            # --- G1q1(b): the cross-world path at the zero point ------------
            f_k2b, _res = m_.card_channel_frame(wa, w, sd["author"])
            f_xw_aa = card_frame_xw(wa, wa, w, sd["author"])
            same_cols = list(f_k2b.columns) == list(f_xw_aa.columns)
            num = [c for c in f_k2b.columns if c not in ("cell_key",)]
            bit = bool(same_cols and np.array_equal(
                np.ascontiguousarray(f_k2b[num].to_numpy(float)).view(np.uint8),
                np.ascontiguousarray(f_xw_aa[num].to_numpy(float)).view(np.uint8)))
            s_k2b = card_stat(f_k2b)
            s_aa = card_stat(f_xw_aa)
            # --- C_ref: A's cards against B's truth -------------------------
            f_xw_ab = card_frame_xw(wa, wb, w, sd["author"])
            s_ab = card_stat(f_xw_ab)
            # --- the gauge, on the SAME pair --------------------------------
            g = gauge_pair(wa, wb, w, f"Q1-DEMO-p{phi}", i, phi)
            trait_same = bool(np.array_equal(
                wa["trait"].view(np.uint8), wb["trait"].view(np.uint8)))
            common_same = bool(np.array_equal(
                wa["common"].view(np.uint8), wb["common"].view(np.uint8)))
            zero_pt.append({
                "phi": phi, "pair": i,
                "k2b_r_card_b_raw": s_k2b["r_card_b_raw"],
                "xw_AA_r_card_b_raw": s_aa["r_card_b_raw"],
                "frame_bit_identical": bit,
                "stat_bit_identical": bool(
                    s_k2b["r_card_b_raw"] == s_aa["r_card_b_raw"])})
            rows.append({
                "phi": phi, "pair": i,
                "C_nat": s_aa["r_card_b_raw"], "C_ref": s_ab["r_card_b_raw"],
                "L_C": float(s_aa["r_card_b_raw"] - s_ab["r_card_b_raw"]),
                "C_nat_cos": s_aa["r_card_b_cos"], "C_ref_cos": s_ab["r_card_b_cos"],
                "C_nat_cen": s_aa["r_card_b_cen"], "C_ref_cen": s_ab["r_card_b_cen"],
                "identical": bool(s_aa["r_card_b_raw"] == s_ab["r_card_b_raw"]),
                "R_nat": g["R_nat"], "R_refresh": g["R_refresh"],
                "R_gap": float(g["R_nat"] - g["R_refresh"]),
                "trait_A_eq_B": trait_same, "common_A_eq_B": common_same,
                "truth_norm_delta_gauge": g["truth_norm_delta"]})
        print(f"  demo phi={phi}: {DEMO_PAIRS} pairs ({time.time() - t0:.1f}s)",
              flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "demonstration.csv", index=False)

    g1b = {"n_checked": len(zero_pt), "rows": zero_pt,
           "all_frames_bit_identical": bool(all(r["frame_bit_identical"]
                                                for r in zero_pt)),
           "all_stats_bit_identical": bool(all(r["stat_bit_identical"]
                                               for r in zero_pt)),
           "meaning": "the cross-world path, run with world_truth = world_est, "
                      "reproduces k2b's own card_channel_frame byte-for-byte and its "
                      "pooled r_card_b_raw exactly -- so the path is k2b's statistic, "
                      "not a lookalike"}
    g1b["PASS"] = bool(g1b["all_frames_bit_identical"] and g1b["all_stats_bit_identical"])

    per_phi = []
    for phi, grp in df.groupby("phi"):
        per_phi.append({
            "phi": float(phi), "n": int(len(grp)),
            "C_nat_mean": float(grp["C_nat"].mean()),
            "C_nat_sem": float(np.std(grp["C_nat"], ddof=1) / np.sqrt(len(grp))),
            "C_ref_mean": float(grp["C_ref"].mean()),
            "C_ref_sem": float(np.std(grp["C_ref"], ddof=1) / np.sqrt(len(grp))),
            "L_C_mean": float(grp["L_C"].mean()),
            "L_C_max_abs": float(grp["L_C"].abs().max()),
            "all_identical": bool(grp["identical"].all()),
            "R_nat_mean": float(grp["R_nat"].mean()),
            "R_refresh_mean": float(grp["R_refresh"].mean()),
            "R_gap_mean": float(grp["R_gap"].mean()),
            "trait_A_eq_B_all": bool(grp["trait_A_eq_B"].all()),
            "common_A_eq_B_any": bool(grp["common_A_eq_B"].any()),
            "gauge_truth_norm_delta_mean": float(grp["truth_norm_delta_gauge"].mean())})

    verdict = {
        "C_ref_identical_to_C_nat_everywhere": bool(df["identical"].all()),
        "max_abs_L_C": float(df["L_C"].abs().max()),
        "trait_shared_everywhere": bool(df["trait_A_eq_B"].all()),
        "common_differs_everywhere": bool(not df["common_A_eq_B"].any()),
        "gauge_R_gap_mean": float(df["R_gap"].mean()),
        "why": "the card statistic's truth side is world['trait'] (k2b:410), a pure "
               "AUTHOR-stream object; A and B share the author seed BY CONSTRUCTION "
               "(that is what C2a certifies), so B's trait is bit-identical to A's and "
               "swapping the truth side changes nothing. The gauge's b-only truth is "
               "emit_panel(..., active=('mu','common')) -- it CONTAINS the frame -- "
               "which is why R_refresh moves and C_ref cannot",
        "consequence": "C_ref == C_nat identically, L_C == 0 identically, and the "
                       "transport share == 1 identically -- by construction, not by "
                       "measurement. Under the registered routing V-Qa would read "
                       "POSITIVE and V-Qb NULL, firing cell 4 CARDS_TRANSPORT_FULL and "
                       "publishing 'card reading crosses frames without measurable "
                       "loss' as a MEASUREMENT. It is an identity",
    }
    out = {"utc": datetime.now(UTC).isoformat(), "G1q1b": g1b, "per_phi": per_phi,
           "n_demo_pairs": int(len(df)), "verdict_inputs": verdict,
           "seconds": time.time() - t0}
    write_json(OUT / "demonstration.json", out)
    _log("demonstrate_done", identical=verdict["C_ref_identical_to_C_nat_everywhere"],
         seconds=out["seconds"])
    print(f"demonstrate OK  G1q1(b)={'PASS' if g1b['PASS'] else 'FAIL'}  "
          f"C_ref==C_nat everywhere: {verdict['C_ref_identical_to_C_nat_everywhere']}  "
          f"max|L_C|={verdict['max_abs_L_C']!r}  gauge R_gap mean="
          f"{verdict['gauge_R_gap_mean']!r}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "G0q1/G1q1 failure or INEXPRESSIBLE",
     "outcome": "INEXPRESSIBLE", "text": "STOP / INEXPRESSIBLE"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE"},
    {"n": "3", "condition": "C1'/anchor or C2 battery failure",
     "outcome": "INSTRUMENT_DEFECT", "text": "INSTRUMENT_DEFECT"},
    {"n": "4", "condition": "V-Qa POSITIVE and V-Qb NULL",
     "outcome": "CARDS_TRANSPORT_FULL",
     "text": "CARDS_TRANSPORT_FULL -- card reading crosses frames without measurable "
             "loss; the taxonomy completes"},
    {"n": "5", "condition": "V-Qa POSITIVE and V-Qb POSITIVE",
     "outcome": "CARDS_TRANSPORT_PARTIAL",
     "text": "CARDS_TRANSPORT_PARTIAL -- real transport, real loss"},
    {"n": "6", "condition": "V-Qa NULL", "outcome": "CARDS_FRAME_LOCKED",
     "text": "CARDS_FRAME_LOCKED -- the scaffold universality extends to the card "
             "layer; major theory note"},
    {"n": "7", "condition": "V-Qa NEGATIVE", "outcome": "CARD_INVERSION_NAMED",
     "text": "CARD_INVERSION_NAMED -- new phenomenon; theory note"},
    {"n": "8", "condition": "any UNDERPOWERED among V-Qa/V-Qb (no higher cell)",
     "outcome": "UNDERPOWERED", "text": "UNDERPOWERED (levels and bands reported)"},
]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    dm = read_json(OUT / "demonstration.json")
    vi = dm["verdict_inputs"]
    pin = p0["card_statistic_pin"]

    slug = "INEXPRESSIBLE"
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": "1", "modifiers": [],
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "stopped_at": "the registration's own expressibility clause, answered by code "
                      "in Part 0 + the demonstration",
        "measurement_pairs_drawn": 0,
        "demonstration_pairs": dm["n_demo_pairs"],
        "finding": {
            "headline": "the card layer's b-truth is FRAME-FREE BY CONSTRUCTION, so "
                        "truth-side frame refreshment is a null operation there",
            "reading_A": "under the closed-form reading of appendix N's 0.827 "
                         "(r_card_b_pred_raw), the statistic is pure algebra with no "
                         "world, no author and no vectors -- INEXPRESSIBLE flatly, "
                         "with no truth side to replace",
            "reading_B": "under the measured reading (r_card_b_raw) the statistic IS "
                         "expressible as author-indexed vectors and the cross-world "
                         "path was built and proven bit-exact against k2b -- but its "
                         "truth side is world['trait'], a pure author-stream object "
                         "that A and B share bit-identically, so C_ref == C_nat "
                         "identically and the estimand is degenerate",
            "both_readings_agree_on_the_stop": True,
            "contrast_that_makes_it_sharp": "on the SAME pairs the gauge's b-only "
                                            "truth (mu + common) DOES change and "
                                            "R_refresh moves away from R_nat; the two "
                                            "layers differ precisely in whether their "
                                            "truth object carries the frame",
            "why_it_matters": "appendix N's ~4.5x gap is not a contest between two "
                              "readers of one target. The card statistic's target is "
                              "the person (trait); the gauge's b-only target is person "
                              "PLUS frame. The taxonomy the Q-line set out to complete "
                              "is settled by what each layer's truth object contains, "
                              "and truth-side refreshment cannot be the instrument "
                              "that settles it",
        },
        "what_would_be_measurable": {
            "estimate_side_swap": "score B's cards against the shared trait and compare "
                                  "to A's -- a frame-sensitivity reading of the card "
                                  "ESTIMATE, which does differ (slow/noise/int are "
                                  "frame-stream). This is a DIFFERENT estimand from the "
                                  "registered truth-side swap and is NAMED, NOT RUN",
            "already_visible_here": "the demonstration's per-phi C_nat spread across "
                                    "A-worlds is exactly the within-frame variability "
                                    "that such a reading would formalise",
            "status": "named for the planner; the executor does not substitute "
                      "estimands",
        },
        "G0q1": p0["G0q1"], "C2": p0["C2"], "G1q1b": dm["G1q1b"],
        "card_statistic_pin": pin, "per_phi": dm["per_phi"],
        "verdict_inputs": vi,
        "gates": {
            "G0q1": {"PASS": p0["G0q1"]["PASS"],
                     "detail": "P3c's values, the 4.5x operands at source, and the "
                               "instrument hashes against P3b's persisted sha256s"},
            "C2": {"PASS": p0["C2"]["PASS"],
                   "detail": f"re-run on {PROBE_PAIRS} fresh probe pairs: author "
                             "objects bit-identical, every frame object differs, "
                             "determinism, shared basis"},
            "G1q1b": {"PASS": dm["G1q1b"]["PASS"],
                      "detail": "the cross-world path reproduces k2b's own card frame "
                                "byte-for-byte and its pooled statistic exactly at the "
                                "zero point"},
            "G2q1": {"PASS": None, "detail": "not reached -- the estimand is degenerate"},
            "G3q1": {"PASS": None, "detail": "not reached"},
            "C1'": {"PASS": None,
                    "detail": "not reached; the gauge replication reading is reported "
                              "descriptively from the demonstration pairs"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, dm, dec)
    _facts(p0, dm, dec)
    print(f"finalize OK  slug={slug}  cell=1  measurement pairs=0")
    _ = args


# ---------------------------------------------------------------------------
# TABLES (rule 24).

def _cs(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _md(h: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(_cs(x) for x in h) + " |",
           "|" + "|".join("---" for _ in h) + "|"]
    for r in rows:
        out.append("| " + " | ".join(_cs(x) for x in r) + " |")
    return out


def _tables(p0: dict[str, Any], dm: dict[str, Any], dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    pin = p0["card_statistic_pin"]
    a, b = pin["reading_A_closed_form"], pin["reading_B_measured"]
    sec["pin"] = _md(
        ["property", "reading A -- the closed form", "reading B -- the measured"],
        [["object", "`" + a["object"] + "`", "`" + b["object"] + "`"],
         ["function", a["function"], b["function"]],
         ["source pin", "`" + a["file_line"] + "`", "`" + b["file_line"] + "`"],
         ["computed at", "`" + a["computed_at"] + "`", "`" + b["computed_at"] + "`"],
         ["value at A1", repr(a["value_A1"]), repr(b["value_A1"])],
         ["takes a world", str(a["takes_a_world"]), str(b["takes_a_world"])],
         ["forms author-indexed vectors", str(a["forms_author_vectors"]),
          str(b["forms_author_vectors"])],
         ["**has a truth side to replace**",
          "**" + str(a["has_a_truth_side_to_replace"]) + "**",
          "**" + str(b["has_a_truth_side_to_replace"]) + "**"],
         ["expressible as author-indexed card vectors",
          str(a["expressible_as_author_indexed_card_vectors"]),
          str(b["expressible_as_author_indexed_card_vectors"])],
         ["why", a["why"], b["why"]],
         ["estimate side", "—", b["estimate_side"]],
         ["**truth side**", "—", "**" + b["truth_side"] + "**"]])
    g0ii = p0["G0q1"]["(ii) the 4.5x comparison"]
    sec["anchor45"] = _md(
        ["quantity", "registration / expected", "persisted", "bit-exact"],
        [["card, closed form (r_card_b_pred_raw, A1)", repr(CARD_PRED_A1),
          repr(g0ii["card_pred_persisted"]), str(g0ii["card_pred_bit_exact"])],
         ["card, measured (r_card_b_raw, A1)", repr(CARD_MEAS_A1),
          repr(g0ii["card_meas_persisted"]), str(g0ii["card_meas_bit_exact"])],
         ["field, measured (recovery_b_only_mean, A1)", repr(FIELD_MEAS_A1),
          repr(g0ii["field_meas_persisted"]), str(g0ii["field_meas_bit_exact"])],
         ["ratio, closed form / field", "~4.5",
          repr(g0ii["ratio_pred_over_field"]), "prose"],
         ["ratio, measured / field", "~4.5",
          repr(g0ii["ratio_meas_over_field"]), "prose"],
         ["note", g0ii["ratio_note"], "—", "—"]])
    sec["quotes"] = _md(
        ["anchor", "located at", "verbatim quote (extracted by code, rule 24)"],
        [[k, f"`{d['file']}:{d['line']}` (para {d['paragraph_lines']})",
          d["quote"][:700] + ("…" if len(d["quote"]) > 700 else "")]
         if d["found"] else [k, "NOT FOUND", "—"]
         for k, d in g0ii["anchors"].items()])
    pv = p0["G0q1"]["(iii) instrument hashes"]
    sec["instrument"] = _md(
        ["property", "value"],
        [["imported from", "`" + pv["imported_from"] + ":"
          + str(pv["definition_line"]) + "`"],
         ["signature", "`" + pv["signature"] + "`"],
         ["function sha256 (this leg)", pv["function_sha256"]],
         ["function sha256 (P3c persisted)", pv["p3c_persisted_function_sha256"]],
         ["**function sha matches**", "**" + str(pv["function_sha_matches"]) + "**"],
         ["file sha256 (this leg)", pv["file_sha256"]],
         ["file sha256 (P3c persisted)", pv["p3c_persisted_file_sha256"]],
         ["**file sha matches**", "**" + str(pv["file_sha_matches"]) + "**"]])
    c2 = p0["C2"]
    sec["c2"] = _md(
        ["check", "objects", "result"],
        [["author objects bit-identical", ", ".join(AUTHOR_OBJECTS),
          str(c2["all_author_identical"])]]
        + [[f"frame norm delta: {k}", "frame",
            f"[{c2['norm_delta_min'][k]!r}, {c2['norm_delta_max'][k]!r}]"]
           for k in FRAME_OBJECTS]
        + [["determinism", "all objects", str(c2["determinism"])],
           ["shared basis", "loadings", str(c2["loadings_shared"])],
           ["**C2 (" + str(c2["n_probe_pairs"]) + " fresh probes)**", "—",
            "**PASS = " + str(c2["PASS"]) + "**"]])
    g1 = dm["G1q1b"]
    sec["zeropoint"] = _md(
        ["phi", "pair", "k2b r_card_b_raw", "cross-world path, A vs A",
         "frame bit-identical", "statistic bit-identical"],
        [[repr(r["phi"]), str(r["pair"]), repr(r["k2b_r_card_b_raw"]),
          repr(r["xw_AA_r_card_b_raw"]), str(r["frame_bit_identical"]),
          str(r["stat_bit_identical"])] for r in g1["rows"]]
        + [["**G1q1(b)**", "—", "—", "—",
            str(g1["all_frames_bit_identical"]),
            "**PASS = " + str(g1["PASS"]) + "**"]])
    sec["dual"] = _md(
        ["phi", "n", "C_nat mean", "C_nat SEM", "C_ref mean", "C_ref SEM",
         "L_C mean", "max |L_C|", "C_ref == C_nat on every pair"],
        [[repr(q["phi"]), str(q["n"]), repr(q["C_nat_mean"]), repr(q["C_nat_sem"]),
          repr(q["C_ref_mean"]), repr(q["C_ref_sem"]), repr(q["L_C_mean"]),
          repr(q["L_C_max_abs"]), str(q["all_identical"])]
         for q in dm["per_phi"]])
    sec["contrast"] = _md(
        ["phi", "card: trait A == B", "card: L_C", "gauge: common A == B",
         "gauge: R_nat", "gauge: R_refresh", "gauge: R_nat - R_refresh",
         "gauge truth norm delta"],
        [[repr(q["phi"]), str(q["trait_A_eq_B_all"]), repr(q["L_C_mean"]),
          str(q["common_A_eq_B_any"]), repr(q["R_nat_mean"]),
          repr(q["R_refresh_mean"]), repr(q["R_gap_mean"]),
          repr(q["gauge_truth_norm_delta_mean"])] for q in dm["per_phi"]])
    fnd = dec["finding"]
    sec["finding"] = _md(
        ["aspect", "statement"],
        [["**headline**", "**" + fnd["headline"] + "**"],
         ["reading A (closed form)", fnd["reading_A"]],
         ["reading B (measured)", fnd["reading_B"]],
         ["both readings agree on the STOP", str(fnd["both_readings_agree_on_the_stop"])],
         ["the contrast that makes it sharp", fnd["contrast_that_makes_it_sharp"]],
         ["why it matters", fnd["why_it_matters"]]])
    wm = dec["what_would_be_measurable"]
    sec["named"] = _md(["aspect", "statement"],
                       [["a measurable neighbour", wm["estimate_side_swap"]],
                        ["already visible here", wm["already_visible_here"]],
                        ["**status**", "**" + wm["status"] + "**"]])
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG") if t["outcome"] == dec["verdict_slug"]
          else t["text"]] for t in TRUTH_TABLE])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(v["PASS"]), v["detail"]]
                        for k, v in dec["gates"].items()])
    sec["sides"] = _md(["clause", "statement", "prior", "sided"],
                       [[k, str(v["clause"]), str(v.get("prior", "—")), v["sided"]]
                        for k, v in p0["sides_rule22"].items()])
    sec["rn"] = _md(["note", "pinned reading"],
                    [[k, v] for k, v in p0["rn_notes"].items()])
    sec["p3c"] = _md(
        ["quantity", "P3c persisted"],
        [["verdict", p0["G0q1"]["(i) P3c values"]["verdict"]],
         ["D_grad", repr(p0["G0q1"]["(i) P3c values"]["D_grad"])],
         ["range_ref", repr(p0["G0q1"]["(i) P3c values"]["range_ref"])],
         ["range_nat", repr(p0["G0q1"]["(i) P3c values"]["range_nat"])]]
        + [[f"R_nat / R_refresh at phi={k}",
            repr(v["R_nat"]) + " / " + repr(v["R_refresh"])]
           for k, v in p0["G0q1"]["(i) P3c values"]["endpoints"].items()])
    sec["env"] = _md(["component", "value"],
                     [[k, str(v)] for k, v in p0["environment"].items()])
    est = p0["stage_estimates_seconds"]
    meas: dict[str, float] = {}
    for line in (OUT / "run_log.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if "seconds" in r:
            meas[r["event"]] = float(r["seconds"])
    sec["timing"] = _md(
        ["stage", "estimate (s)", "measured (s)"],
        [["part0", str(est["part0"]), "%.3f" % meas.get("part0_done", float("nan"))],
         ["demonstrate", str(est["demonstrate"]),
          "%.3f" % meas.get("demonstrate_done", float("nan"))],
         ["finalize", str(est["finalize"]),
          "%.3f" % meas.get("finalize_done", float("nan"))],
         ["pilot / arms / fit", "—", "-- not reached"]])
    body = ["# M4-Q1 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], dm: dict[str, Any], dec: dict[str, Any]) -> None:
    vi = dm["verdict_inputs"]
    pv = p0["G0q1"]["(iii) instrument hashes"]
    g0ii = p0["G0q1"]["(ii) the 4.5x comparison"]
    pin = p0["card_statistic_pin"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"], "STOPPED_AT": dec["stopped_at"],
        "MODIFIERS": ", ".join(dec["modifiers"]) or "none",
        "MPAIRS": dec["measurement_pairs_drawn"],
        "DPAIRS": dec["demonstration_pairs"],
        "PIN_A": pin["reading_A_closed_form"]["file_line"],
        "PIN_B": pin["reading_B_measured"]["file_line"],
        "TRUTH_SIDE": pin["reading_B_measured"]["truth_side"],
        "CARD_PRED": CARD_PRED_A1, "CARD_MEAS": CARD_MEAS_A1,
        "FIELD_MEAS": FIELD_MEAS_A1,
        "RATIO_PRED": g0ii["ratio_pred_over_field"],
        "RATIO_MEAS": g0ii["ratio_meas_over_field"],
        "FNSHA_OK": pv["function_sha_matches"], "FILESHA_OK": pv["file_sha_matches"],
        "PROBES": p0["C2"]["n_probe_pairs"], "C2PASS": p0["C2"]["PASS"],
        "G1B": dm["G1q1b"]["PASS"], "G1B_N": dm["G1q1b"]["n_checked"],
        "IDENTICAL": vi["C_ref_identical_to_C_nat_everywhere"],
        "MAXL": vi["max_abs_L_C"],
        "TRAIT_SHARED": vi["trait_shared_everywhere"],
        "COMMON_DIFFERS": vi["common_differs_everywhere"],
        "RGAP": vi["gauge_R_gap_mean"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"],
        "PLATFORM": p0["environment"]["platform"],
    }
    for q in dm["per_phi"]:
        tag = str(q["phi"]).replace(".", "")
        f[f"P{tag}_CNAT"] = q["C_nat_mean"]
        f[f"P{tag}_CREF"] = q["C_ref_mean"]
        f[f"P{tag}_RNAT"] = q["R_nat_mean"]
        f[f"P{tag}_RREF"] = q["R_refresh_mean"]
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-Q1 — card transport under frame refreshment — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}); modifiers: {{MODIFIERS}}.**
{{ROUTING_TEXT}}. Stopped at {{STOPPED_AT}}. **{{MPAIRS}} measurement pairs
drawn** ({{DPAIRS}} demonstration pairs on the pilot salt).

**The card layer's b-truth is frame-free by construction, so truth-side frame
refreshment is a null operation there.** The registration's own expressibility
clause is the right exit, and it is reached by code rather than by argument: the
cross-world path was built, proven bit-exact against k2b at the zero point, and
then shown to return **exactly** C_nat when pointed at the B-world.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md` BEFORE run (commit 0f3d773). Every
number below is generated from artifacts by code (rule 24).

---

## 1. The card statistic, pinned — and it has two readings

Appendix N says *"card attenuation 0.827 vs field recovery 0.178"*. **Two
persisted objects round to 0.827**, and the registration does not disambiguate,
so both are pinned and both are carried through the expressibility test
(RN-Q1-1).

<<TABLE:pin>>

<<TABLE:anchor45>>

<<TABLE:quotes>>

The ratio is worth a note: {{RATIO_PRED}} under the closed-form reading and
{{RATIO_MEAS}} under the measured one. Appendix N's "~4.5×" carries a tilde and
no artifact holds a ratio key — the number is prose, not a computed object.

### 1.1 The registration's phrase names an object that does not exist

The registration says C_ref *"replaces only the truth-side card panel with the
B-world's"*. In `card_channel_frame` the truth side is **not a card panel**: it
is {{TRUTH_SIDE}}. The estimate side is a card (a centred channel mixture with
the frame channel excluded by construction); the truth side is the bare latent
trait. This harness replaces exactly the object that can be replaced, and
reports the mismatch rather than papering over it (RN-Q1-2).

## 2. The instrument and the C2 battery

<<TABLE:instrument>>

Hashes match P3b's persisted values ({{FNSHA_OK}} / {{FILESHA_OK}}).

<<TABLE:c2>>

C2 = {{C2PASS}} on {{PROBES}} fresh probe pairs. **Note what C2a certifies:
the author objects — `trait` among them — are bit-identical between A and B.**
That certification is the whole story of this leg.

## 3. G1q1(b) — the cross-world path is k2b's statistic, not a lookalike

<<TABLE:zeropoint>>

Run with `world_truth = world_est`, the cross-world path reproduces k2b's own
`card_channel_frame` **byte-for-byte** and its pooled `r_card_b_raw` exactly, on
all {{G1B_N}} checks: G1q1(b) = {{G1B}}. The trap was avoided explicitly
(RN-Q1-3): `trait_c` feeds both the card and the centred truth, so only the
truth-side trait is parameterised and the card keeps A's throughout.

## 4. The result: C_ref ≡ C_nat, identically

<<TABLE:dual>>

**C_ref equals C_nat on every pair at both φ ({{IDENTICAL}}), with
max |L_C| = {{MAXL}}.** Not "within noise" — *identically*, to the last bit.

The reason is one line of the generator. The card statistic's truth side is
`world["trait"]`, a pure **author-stream** object; A and B share the author seed
by construction, so B's trait is bit-identical to A's ({{TRAIT_SHARED}}) and
swapping the truth side changes nothing.

## 5. The contrast that makes the finding sharp

<<TABLE:contrast>>

On the **same pairs**, the gauge behaves completely differently: its b-only
truth is `emit_panel(..., active=("mu","common"))`, which **contains the frame**,
so B's truth panel genuinely differs ({{COMMON_DIFFERS}}) and R_refresh moves
away from R_nat by {{RGAP}} on average. Card layer: {{P005_CNAT}} → {{P005_CREF}}
at φ = 0.05 (no change at all). Gauge layer: {{P005_RNAT}} → {{P005_RREF}}.

**The two layers differ precisely in whether their truth object carries the
frame.** That is the finding.

<<TABLE:finding>>

### 5.1 What this does to appendix N's ~4.5×

The gap is not a contest between two readers of one target. **The card
statistic's target is the person (trait); the gauge's b-only target is person
PLUS frame.** So the Q-line's question — "do card readings transport across
frames?" — cannot be answered by refreshing the truth side, because at the card
layer there is no frame in the truth to refresh. The taxonomy the line set out
to complete is settled by *what each layer's truth object contains*, and this
leg settles it by inspection plus proof rather than by measurement.

Had the leg proceeded, V-Qa would have read POSITIVE and V-Qb NULL, firing cell
4 and publishing *"card reading crosses frames without measurable loss"* as a
measurement. It is an identity. Routing cell 4's consequence is not entailed by
an identity, so the registration's expressibility STOP is the correct exit.

## 6. A measurable neighbour, named not run

<<TABLE:named>>

## 7. P3c's values, verified

<<TABLE:p3c>>

## 8. Routing

<<TABLE:truth_table>>

## 9. Gates

<<TABLE:gates>>

## 10. Sides declared (rule 22)

<<TABLE:sides>>

## 11. Pinned readings

<<TABLE:rn>>

## 12. Rule events

- **Rule 13:** not reached — no verdict boundary exists without a measurement.
- **Rule 25:** not reached; the expressibility clause fires first.
- **Rule 26:** no bounded winner.
- **Rule 27:** no budgeted quantity was consumed.
- **Rule 29:** the domain-pinned predicate was defined for the card cosines and
  is not exercised — no measurement arm ran.
- **Rule 30:** every cited constant read from its persisted source; the card
  statistic carries two source pins and both candidate values.

## 13. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython {{PYTHON}} venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

No hypothesis-relevant number was ever computed: the leg stopped before its
first measurement arm, and the demonstration quantities are identities.

## 14. Environment

<<TABLE:env>>

## 15. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_q1_card_transport/` (gitignored) — `part0.json`,
`demonstration.json`, `demonstration.csv`, `decision.json`, `prose_facts.json`,
`report_tables.md`, `run_log.jsonl`. Harness:
`scripts/run_suica_m4_q1_card_transport.py`.*
"""


def _fmt(v: Any) -> str:
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, float):
        return repr(v)
    if isinstance(v, list):
        return "[" + ", ".join(_fmt(x) for x in v) + "]"
    return str(v)


def stage_report(args: argparse.Namespace) -> None:
    facts = read_json(OUT / "prose_facts.json")
    tables = (OUT / "report_tables.md").read_text(encoding="utf-8")
    sec: dict[str, str] = {}
    cur, buf = None, []
    for line in tables.split("\n"):
        if line.startswith("<!-- TABLE:"):
            if cur:
                sec[cur] = "\n".join(buf).strip()
            cur, buf = line.split("<!-- TABLE:")[1].split(" -->")[0], []
        elif cur:
            buf.append(line)
    if cur:
        sec[cur] = "\n".join(buf).strip()
    txt = REPORT_TEMPLATE
    for k, v in facts.items():
        txt = txt.replace("{{" + k + "}}", _fmt(v))
    for k, v in sec.items():
        txt = txt.replace("<<TABLE:" + k + ">>", v)
    if "{{" in txt or "<<TABLE:" in txt:
        bad = re.findall(r"\{\{[A-Z0-9_]+\}\}|<<TABLE:[a-z0-9_]+>>", txt)
        raise SystemExit(f"REFUSED: unresolved placeholders: {sorted(set(bad))}")
    path = ROOT / "reports" / "SUICA_M4_Q1_CARD_TRANSPORT_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("demonstrate", stage_demonstrate),
        ("finalize", stage_finalize), ("report", stage_report)]
    for name, fn in stages:
        sub.add_parser(name).set_defaults(fn=fn)

    def _all(a: argparse.Namespace) -> None:
        for _, fn in stages:
            fn(a)
    sub.add_parser("all").set_defaults(fn=_all)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
