#!/usr/bin/env python3
"""SUICA M4-Q1b -- the cross-frame card cosine (identity beyond the trait).

Registered BEFORE run in docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md ("M4-Q1b",
commit 527d176).  Binding.

Q1 proved the card layer's b-TRUTH is frame-free, so truth-side refreshment is
degenerate there.  The properly-posed question swaps nothing: A and B share ONLY
the author stream (C2a certifies it), so the cross-frame card cosine
cos(card_A, card_B) can be compared against the disattenuation identity
r_A * r_B.  Any excess is author-stream content the trait does not span --
the ID-card question, asked directly in card space.

    cos_AB(w) = mean over authors of cos(card_A(a), card_B(a))
    r_A(w), r_B(w) = the measured card-vs-trait statistic (Q1's reading B)
    Delta(w) = cos_AB(w) - r_A(w) * r_B(w)

The card path is Q1's, imported by file: it was proven bit-exact against k2b's
own card_channel_frame at the zero point.  k2b, suica_core/ and the P3b
instrument are untouched.

Stages: part0 -> pilot -> project -> arm_<tag> (4) -> fit -> finalize -> report
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
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_q1b_card_cosine"
RES = ROOT / "results"
Q1SRC = ROOT / "scripts" / "run_suica_m4_q1_card_transport.py"
P3BSRC = ROOT / "scripts" / "run_suica_m4_p3b_refresh_gradient.py"
K2BSRC = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
Q1RES = RES / "m4_q1_card_transport"
IDT = ROOT / "docs" / "SUICA_IDENTITY_THEORY_V1.md"
KLINE = ROOT / "docs" / "SUICA_M4_K_IDENTITY_LINE_PLAN.md"

LEG = "M4-Q1b"
BANNER = ("the cross-frame card cosine against the disattenuation identity; "
          "exploratory, label-free; no seal")

MASTER_SEED = 20260814
SALT_AUTHOR = "m4q1b-author"
SALT_FRAME_A = "m4q1b-frameA"
SALT_FRAME_B = "m4q1b-frameB"
SALT_PILOT = "m4q1b-pilot"
SHARE = 0.25
PHI_LO, PHI_HI = 0.05, 0.98
N_PAIRS = 384
N_PAIRS_ESCALATED = 768
CHUNK = 192
PILOT_PAIRS = 4
PROBE_PAIRS = 4
W_INT_ARM = "zero"

READINGS = ("Delta", "Delta_cos", "Delta_author", "Delta_cen", "Delta_author_cen")
B_BOOT = 2000
B_BOOT_HIGH = 20000
B_PROJ = 2000
RULE13_FACTOR = 10.0
CHI2_Q = 0.10
INDEP_MARGIN = 1.25            # #57: no pilot correlations; independence + margin
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
DELTA_MATERIAL = 0.05          # the registered "material identity share" truth
SATURATION_ABS = 0.995

CARD_PRED_A1 = 0.8271784593117322
CARD_MEAS_A1 = 0.8266850143926395

AUTHOR_OBJECTS = ("trait", "a_load", "loadings")
FRAME_OBJECTS = ("slow", "slow_latent", "noise", "common", "int")
CARD_DROP = ("author", "world_seed", "cell_key", "m")

# ---------------------------------------------------------------------------
# RN-Q1B notes.  PINNED IN PART 0, BEFORE ANY STATISTIC.
#
# RN-Q1B-1 (the estimator families do not match, and the registration does not
#   say which to use -- PINNED BEFORE ANY NUMBER).  cos_AB is defined as a MEAN
#   OF PER-AUTHOR COSINES.  `pooled_card_stats` (k2b:463-489) emits TWO
#   card-vs-trait statistics from the same frame:
#     r_card_b_raw (k2b:486) -- a RATIO OF SUMS over authors, a norm-weighted
#         "grand cosine" over the stacked author x dim matrix; this is the
#         object Q1 pinned as "reading B" and the one appendix N quotes; and
#     r_card_b_cos (k2b:488) -- the MEAN OF PER-AUTHOR COSINES, which is the
#         SAME estimator family as cos_AB.
#   The disattenuation identity cos(A,B) = cos(A,t)*cos(B,t) is a PER-AUTHOR
#   statement, so mixing a mean-of-cosines with a product of ratio-of-sums
#   leaves a bias of unknown sign in Delta.  The registration says "Q1's
#   reading B, pooled_card_stats lineage", which literally names r_card_b_raw.
#   PINNED: the LITERAL reading routes (Delta_registered uses r_card_b_raw).
#   TWO alternatives are computed and reported at equal precision --
#   Delta_cos (both factors from r_card_b_cos, estimator-consistent) and
#   Delta_author (the identity applied PER AUTHOR and then averaged, which is
#   the only form in which it is exact).  If the three disagree in
#   CLASSIFICATION, that disagreement is the finding and a defect candidate;
#   if they agree, the verdict is robust to the ambiguity.
#
# RN-Q1B-2 (what makes this non-degenerate, checked not assumed).  Q1 failed
#   because the swapped object was shared by construction.  Here nothing is
#   swapped: cos_AB, r_A and r_B are measurements of three DIFFERENT vector
#   pairs, and A's and B's cards differ because slow/noise/int are
#   frame-stream.  G1q1b re-proves card_A != card_B per pair, per author,
#   BEFORE any statistic is read.
#
# RN-Q1B-3 (the control pair is sanity, never a verdict input).  With the SAME
#   frame seed, card_B IS card_A, so cos_AB = 1 exactly and
#   Delta = 1 - r^2 > 0 by construction.  It proves the operator computes what
#   it claims; it is not evidence about the world and is excluded from every
#   band, projection and verdict.
#
# RN-Q1B-4 (#57 compliance).  No pilot CORRELATION is consumed anywhere.  The
#   bands and the projection use per-pair variances only, with the registered
#   independence margin 1.25 applied to any SE that would otherwise need a
#   covariance.  Delta is computed FULLY PAIRED per world-pair, so its
#   per-pair variance is measured directly and needs no covariance at all --
#   the margin is applied only where a decomposition would have required one,
#   and where it is applied it is stated.
#
# RN-Q1B-6 (THE CONFOUND, found on probe pairs BEFORE any measurement arm and
#   pinned here).  The card is
#       full = w_mu * trait_c + w_slow * slow_c_bar + w_noise * noise_c_bar
#   (k2b:423-427) -- its trait component is trait_c, the CELL-CENTRED trait.
#   But r_card_b_raw and r_card_b_cos both score the card against `trait`,
#   the UNCENTRED array (k2b:443/446).  The shared content between A and B is
#   exactly w_mu * trait_c, so the disattenuation identity that actually holds
#   is cos(A,B) = cos(A, trait_c) * cos(B, trait_c) -- with the CENTRED
#   reference.  Scoring fidelity against the uncentred trait understates each
#   card's alignment with the object it actually shares, so r*r understates
#   cos_AB and Delta comes out POSITIVE for a reason that has nothing to do
#   with identity beyond the trait.
#   Measured on six probe pairs per phi BEFORE any arm: Delta_raw +0.0149 /
#   +0.0081, while the centred reading gives +0.0015 / -0.0022 and the
#   per-author centred form gives -0.0003 / -0.0030.
#   CONSEQUENCE FOR THE REGISTRATION: its stated entailment -- "A and B share
#   ONLY the author stream (C2a), so Delta POSITIVE is entailed to be
#   author-stream content beyond the trait -- no other shared channel exists"
#   -- does NOT hold for the registered reference.  No other CHANNEL is needed;
#   the trait channel alone produces a positive Delta when the reference object
#   is the uncentred trait.  PINNED: the literal reading still ROUTES (the
#   registration is binding), and `r_card_b_cen` -- which is emitted by the
#   SAME pooled_card_stats call, k2b:487, and is therefore equally "the
#   pooled_card_stats lineage" -- is computed alongside with its own band, as
#   is the per-author centred form.  All four are reported at equal precision
#   and the entailment failure is stated wherever the verdict is stated.
#
# RN-Q1B-5 (the sign the theory cares about).  Delta > 0 means the two cards
#   agree MORE than their separate trait-fidelities can explain.  Since C2a
#   certifies the author stream as the ONLY shared content, a positive Delta is
#   entailed to be author-stream structure beyond the trait -- in this family
#   the only candidate is a_load, the per-author interaction carrier.  Note
#   that w["int"] = 0 in this arm, so a_load reaches the card through NO
#   channel: the registration's own consequence-entailment therefore predicts
#   Delta = 0, and a POSITIVE Delta would indicate something the channel
#   accounting does not contain.  Stated in Part 0, before the measurement.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-Q1B-1": "cos_AB is a mean of per-author cosines; pooled_card_stats emits BOTH "
                "r_card_b_raw (ratio of sums, k2b:486 -- Q1's 'reading B') and "
                "r_card_b_cos (mean of per-author cosines, k2b:488, the same family as "
                "cos_AB). The disattenuation identity is per-author, so mixing families "
                "biases Delta. PINNED: the literal reading (r_card_b_raw) routes; "
                "Delta_cos and the per-author-exact Delta_author are computed and "
                "reported; disagreement in classification is the finding",
    "RN-Q1B-2": "nothing is swapped here -- cos_AB, r_A and r_B measure three different "
                "vector pairs -- so Q1's identity-forcing failure cannot recur; card_A "
                "!= card_B is re-proven per pair and per author before any statistic",
    "RN-Q1B-3": "the same-frame-seed control gives cos_AB = 1 and Delta = 1 - r^2 > 0 by "
                "construction; it is operator sanity, excluded from every band, "
                "projection and verdict",
    "RN-Q1B-4": "no pilot correlation is consumed (#57); Delta is computed fully paired "
                "per world-pair so its variance is measured directly, and the 1.25 "
                "independence margin is applied only where a covariance would otherwise "
                "be needed, and stated where applied",
    "RN-Q1B-6": "THE CONFOUND, found on probe pairs before any arm: the card carries "
                "trait_c (CENTRED, k2b:423) but r_card_b_raw/r_card_b_cos score it "
                "against the UNCENTRED trait (k2b:443/446). The shared content is "
                "w_mu*trait_c, so the identity that holds uses the CENTRED reference; "
                "the uncentred reference understates each card's alignment with what it "
                "shares and forces Delta > 0 with no content beyond the trait. The "
                "registration's stated entailment therefore FAILS for the registered "
                "reference. The literal reading still routes (binding); r_card_b_cen "
                "(k2b:487, the same pooled_card_stats call) and the per-author centred "
                "form are computed with their own bands and reported at equal precision",
    "RN-Q1B-5": "Delta > 0 means the cards agree more than their trait-fidelities "
                "explain; C2a makes the author stream the only shared content, and with "
                "w['int'] = 0 the a_load carrier reaches the card through NO channel -- "
                "so the registration's own entailment predicts Delta = 0 and a POSITIVE "
                "Delta would indicate something the channel accounting does not contain",
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


def q1() -> Any:
    return _load_named("run_suica_m4_q1_card_transport", Q1SRC)


def p3b() -> Any:
    return q1().p3b()


def k2b() -> Any:
    return q1().k2b()


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
# CARD VECTORS -- the same construction Q1's verified path uses (k2b:422-442).

def card_and_trait(world: dict[str, np.ndarray],
                   w: dict[str, float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per-author card vectors and their trait counterparts, in cell order.

    This is k2b:410-442's arithmetic, stopped one step earlier than
    card_channel_frame: it returns the 64-dim vectors instead of contracting
    them away.  Q1 proved the surrounding path bit-exact against k2b; the
    contraction of these vectors reproduces k2b's own columns (checked in
    G1q1b).
    """
    m_ = k2b()
    lay = m_.layout()
    counts = lay["counts"]
    cell_key = lay["cell_key"]
    keys = cell_key[lay["retained_idx"]]
    cards, traits, authors = [], [], []
    for key in sorted(set(map(str, keys))):
        idx = np.asarray(
            [i for i in lay["retained_idx"] if str(cell_key[i]) == key], dtype=int)
        m = int(counts[idx[0]])
        trait = world["trait"][idx]                                   # k2b:410
        trait_c = trait - trait.mean(axis=0, keepdims=True)           # k2b:411
        slow_c = (world["slow"][idx, :m]
                  - world["slow"][idx, :m].mean(axis=0, keepdims=True))
        noise_c = (world["noise"][idx, :m]
                   - world["noise"][idx, :m].mean(axis=0, keepdims=True))
        occ = np.arange(m)
        full = w["mu"] * trait_c                                      # k2b:423
        full = full + w["slow"] * slow_c[:, occ, :].mean(axis=1)      # k2b:424
        if w["int"] != 0.0:
            int_c = (world["int"][idx, :m]
                     - world["int"][idx, :m].mean(axis=0, keepdims=True))
            full = full + w["int"] * int_c[:, occ, :].mean(axis=1)    # k2b:425-426
        full = full + w["noise"] * noise_c[:, occ, :].mean(axis=1)    # k2b:427
        cards.append(full)
        traits.append(trait)
        authors.append(idx)
    return (np.concatenate(cards, axis=0), np.concatenate(traits, axis=0),
            np.concatenate(authors, axis=0))


def _cellmean(x: np.ndarray) -> np.ndarray:
    """Cell means, broadcast back -- the same (context, m) centring k2b uses."""
    m_ = k2b()
    lay = m_.layout()
    ck = lay["cell_key"]
    ridx = lay["retained_idx"]
    keys = [str(ck[i]) for i in ridx]
    order = sorted(set(keys))
    out = np.empty_like(x)
    pos = 0
    for key in order:
        n = sum(1 for k in keys if k == key)
        blk = x[pos:pos + n]
        out[pos:pos + n] = blk.mean(axis=0, keepdims=True)
        pos += n
    return out


def _rowcos(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    num = np.einsum("id,id->i", a, b)
    den = np.sqrt(np.einsum("id,id->i", a, a) * np.einsum("id,id->i", b, b))
    return num / den


def pooled_r(world: dict[str, np.ndarray], w: dict[str, float],
             seed: int) -> dict[str, float]:
    """Q1's verified path -> k2b's own reducer.  Both r columns are returned."""
    frame = q1().card_frame_xw(world, world, w, seed)
    return q1().card_stat(frame)


def run_pair(phi: float, i: int, suffix: str = "",
             *, control: bool = False) -> dict[str, Any]:
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    sd = pair_seeds(phi, i, suffix)
    fb = sd["frameA"] if control else sd["frameB"]
    wa = build_split_world(sd["author"], sd["frameA"], phi)
    wb = build_split_world(sd["author"], fb, phi)
    ca, ta, _ = card_and_trait(wa, w)
    cb, tb, _ = card_and_trait(wb, w)
    cos_ab = _rowcos(ca, cb)
    cos_at = _rowcos(ca, ta)
    cos_bt = _rowcos(cb, tb)
    tca = ta - _cellmean(ta)
    tcb = tb - _cellmean(tb)
    cos_atc = _rowcos(ca, tca)
    cos_btc = _rowcos(cb, tcb)
    sa = pooled_r(wa, w, sd["author"])
    sb = pooled_r(wb, w, sd["author"])
    cos_AB = float(cos_ab.mean())
    r_raw_a, r_raw_b = sa["r_card_b_raw"], sb["r_card_b_raw"]
    r_cos_a, r_cos_b = sa["r_card_b_cos"], sb["r_card_b_cos"]
    r_cen_a, r_cen_b = sa["r_card_b_cen"], sb["r_card_b_cen"]
    return {
        "phi": phi, "pair": i, "control": control,
        "author_seed": sd["author"], "frameA_seed": sd["frameA"], "frameB_seed": fb,
        "cos_AB": cos_AB,
        "r_raw_A": r_raw_a, "r_raw_B": r_raw_b,
        "r_cos_A": r_cos_a, "r_cos_B": r_cos_b,
        "r_cen_A": r_cen_a, "r_cen_B": r_cen_b,
        "r_raw_product": float(r_raw_a * r_raw_b),
        "r_cos_product": float(r_cos_a * r_cos_b),
        "r_cen_product": float(r_cen_a * r_cen_b),
        # the three readings of Delta (RN-Q1B-1); the first routes
        "Delta": float(cos_AB - r_raw_a * r_raw_b),
        "Delta_cos": float(cos_AB - r_cos_a * r_cos_b),
        "Delta_author": float(np.mean(cos_ab - cos_at * cos_bt)),
        # RN-Q1B-6: the CENTRED reference -- the object the cards actually share
        "Delta_cen": float(cos_AB - r_cen_a * r_cen_b),
        "Delta_author_cen": float(np.mean(cos_ab - cos_atc * cos_btc)),
        "cos_AB_min": float(cos_ab.min()), "cos_AB_max": float(cos_ab.max()),
        "n_authors": int(len(cos_ab)),
        "card_norm_delta": float(np.linalg.norm(ca - cb)),
        "cards_differ_all_authors": bool(np.all(
            np.linalg.norm(ca - cb, axis=1) > 0.0)),
    }


# ---------------------------------------------------------------------------
# PART 0.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")

    # --- G0(ii): instrument + Q1 path hashes -------------------------------
    fn = p3b().build_split_world
    fn_sha = hashlib.sha256(inspect.getsource(fn).encode("utf-8")).hexdigest()
    file_sha = hashlib.sha256(P3BSRC.read_bytes()).hexdigest()
    q1p0 = read_json(Q1RES / "part0.json")
    q1prov = q1p0["G0q1"]["(iii) instrument hashes"]
    xw = q1().card_frame_xw
    prov = {
        "instrument_from": rel(P3BSRC),
        "instrument_function_sha256": fn_sha,
        "instrument_file_sha256": file_sha,
        "q1_persisted_function_sha256": q1prov["function_sha256"],
        "q1_persisted_file_sha256": q1prov["file_sha256"],
        "instrument_sha_matches": bool(fn_sha == q1prov["function_sha256"]
                                       and file_sha == q1prov["file_sha256"]),
        "card_path_from": rel(Q1SRC),
        "card_path_function": "card_frame_xw",
        "card_path_line": int(inspect.getsourcelines(xw)[1]),
        "card_path_function_sha256": hashlib.sha256(
            inspect.getsource(xw).encode("utf-8")).hexdigest(),
        "card_path_file_sha256": hashlib.sha256(Q1SRC.read_bytes()).hexdigest(),
        "card_path_proven_bit_exact_in_Q1": None,
    }

    # --- G0(i): Q1's record -------------------------------------------------
    q1d = read_json(Q1RES / "decision.json")
    q1dm = read_json(Q1RES / "demonstration.json")
    prov["card_path_proven_bit_exact_in_Q1"] = bool(q1dm["G1q1b"]["PASS"])
    pin = q1p0["card_statistic_pin"]
    g0i = {
        "source": rel(Q1RES / "decision.json"),
        "q1_verdict": q1d["verdict_slug"],
        "q1_zero_point_PASS": q1dm["G1q1b"]["PASS"],
        "q1_zero_point_n": q1dm["G1q1b"]["n_checked"],
        "card_pred_pin": pin["reading_A_closed_form"]["file_line"],
        "card_pred_value": pin["reading_A_closed_form"]["value_A1"],
        "card_meas_pin": pin["reading_B_measured"]["file_line"],
        "card_meas_value": pin["reading_B_measured"]["value_A1"],
        "card_pred_bit_exact": bool(
            pin["reading_A_closed_form"]["value_A1"] == CARD_PRED_A1),
        "card_meas_bit_exact": bool(
            pin["reading_B_measured"]["value_A1"] == CARD_MEAS_A1),
        "reading_B_is": "r_card_b_raw (the ratio of sums, k2b:486)",
    }
    g0i["PASS"] = bool(q1d["verdict_slug"] == "INEXPRESSIBLE"
                       and q1dm["G1q1b"]["PASS"]
                       and g0i["card_pred_bit_exact"]
                       and g0i["card_meas_bit_exact"])

    # --- G0(iii): the disattenuation-identity lineage -----------------------
    anchors = {
        "T8 / the disattenuated distinctive cosine":
            _locate(IDT, "disattenuat"),
        "the K3-era distinctive-cosine statement (K-line)":
            _locate(KLINE, "disattenuat"),
        "k2b's own attenuation prediction (the identity's card-side factor)":
            _locate(K2BSRC, 'out["r_card_b_pred_raw"]'),
    }
    g0iii = {"anchors": anchors,
             "n_found": int(sum(1 for a in anchors.values() if a["found"])),
             "n_total": len(anchors),
             "method": "each anchor substring located in its controlling document or "
                       "script and the containing paragraph extracted verbatim by code "
                       "(rule 24)"}
    g0iii["PASS"] = bool(g0iii["n_found"] >= 2)

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
    d1 = build_split_world(sd0["author"], sd0["frameA"], PHI_LO)
    d2 = build_split_world(sd0["author"], sd0["frameA"], PHI_LO)
    c2 = {"n_probe_pairs": PROBE_PAIRS, "rows": rows,
          "all_author_identical": bool(all(r[f"author::{k}"] for r in rows
                                           for k in AUTHOR_OBJECTS)),
          "all_frame_differ": bool(all(r[f"frame::{k}"] > 0.0 for r in rows
                                       for k in FRAME_OBJECTS)),
          "norm_delta_min": {k: float(min(r[f"frame::{k}"] for r in rows))
                             for k in FRAME_OBJECTS},
          "norm_delta_max": {k: float(max(r[f"frame::{k}"] for r in rows))
                             for k in FRAME_OBJECTS},
          "determinism": bool(all(np.array_equal(
              np.asarray(d1[k]).view(np.uint8), np.asarray(d2[k]).view(np.uint8))
              for k in d1)),
          "loadings_shared": bool(all(r["author::loadings"] for r in rows))}
    c2["PASS"] = bool(c2["all_author_identical"] and c2["all_frame_differ"]
                      and c2["determinism"] and c2["loadings_shared"])

    # --- G1q1b(a): card_A != card_B, per pair AND per author ---------------
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    diff_rows = []
    for i in range(PROBE_PAIRS):
        sd = pair_seeds(PHI_LO, i, "-probe")
        wa = build_split_world(sd["author"], sd["frameA"], PHI_LO)
        wb = build_split_world(sd["author"], sd["frameB"], PHI_LO)
        ca, _, _ = card_and_trait(wa, w)
        cb, _, _ = card_and_trait(wb, w)
        per = np.linalg.norm(ca - cb, axis=1)
        diff_rows.append({"probe": i, "n_authors": int(len(per)),
                          "min_author_norm_delta": float(per.min()),
                          "max_author_norm_delta": float(per.max()),
                          "all_authors_differ": bool(np.all(per > 0.0)),
                          "frobenius": float(np.linalg.norm(ca - cb))})
    g1a = {"rows": diff_rows,
           "all_pairs_all_authors_differ": bool(all(r["all_authors_differ"]
                                                    for r in diff_rows)),
           "min_over_all": float(min(r["min_author_norm_delta"] for r in diff_rows)),
           "note": RN_NOTES["RN-Q1B-2"]}
    g1a["PASS"] = g1a["all_pairs_all_authors_differ"]

    # --- G1q1b(b): the same-frame-seed control (sanity only) ---------------
    ctl = run_pair(PHI_LO, 0, "-probe", control=True)
    r_raw = ctl["r_raw_A"]
    g1b = {"cos_AB": ctl["cos_AB"], "r_raw_A": r_raw, "r_raw_B": ctl["r_raw_B"],
           "Delta": ctl["Delta"],
           "expected_cos_AB": 1.0,
           "expected_Delta": float(1.0 - r_raw * r_raw),
           "cos_is_one": bool(abs(ctl["cos_AB"] - 1.0) < 1e-12),
           "Delta_matches_1_minus_r2": bool(
               abs(ctl["Delta"] - (1.0 - r_raw * ctl["r_raw_B"])) < 1e-12),
           "Delta_positive": bool(ctl["Delta"] > 0.0),
           "status": "OPERATOR SANITY ONLY -- excluded from every band, projection "
                     "and verdict (RN-Q1B-3)"}
    g1b["PASS"] = bool(g1b["cos_is_one"] and g1b["Delta_matches_1_minus_r2"]
                       and g1b["Delta_positive"])

    # --- G1q1b(c): the vectors contract back to k2b's own columns ----------
    sd = pair_seeds(PHI_LO, 0, "-probe")
    wv = build_split_world(sd["author"], sd["frameA"], PHI_LO)
    cv, tv, _ = card_and_trait(wv, w)
    fr, _res = m_.card_channel_frame(wv, w, sd["author"])
    contract = {
        "full_n_matches": bool(np.allclose(
            np.einsum("id,id->i", cv, cv), fr["full_n"].to_numpy(float), rtol=0,
            atol=0)),
        "b_raw_n_matches": bool(np.allclose(
            np.einsum("id,id->i", tv, tv), fr["b_raw_n"].to_numpy(float), rtol=0,
            atol=0)),
        "dot_matches": bool(np.allclose(
            np.einsum("id,id->i", cv, tv), fr["full_b_dot_raw"].to_numpy(float),
            rtol=0, atol=0)),
        "cos_matches": bool(np.allclose(
            _rowcos(cv, tv), fr["r_cos_raw"].to_numpy(float), rtol=0, atol=0)),
        "meaning": "the 64-dim vectors this leg forms contract EXACTLY to the columns "
                   "k2b's own card_channel_frame emits -- so the cosines below are "
                   "built from k2b's cards, not a lookalike"}
    contract["PASS"] = bool(all(v for k, v in contract.items()
                                if k.endswith("_matches")))

    g0 = {"(i) Q1 record": g0i, "(ii) hashes": prov, "(iii) lineage": g0iii,
          "PASS": bool(g0i["PASS"] and prov["instrument_sha_matches"]
                       and g0iii["PASS"])}
    g1 = {"(a) card_A != card_B": g1a, "(b) control pair": g1b,
          "(c) vectors contract to k2b": contract,
          "PASS": bool(g1a["PASS"] and g1b["PASS"] and contract["PASS"])}

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md (M4-Q1b, BEFORE run, "
                        "commit 527d176)",
        "master_seed": MASTER_SEED,
        "salts": {"author": SALT_AUTHOR, "frameA": SALT_FRAME_A,
                  "frameB": SALT_FRAME_B, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0q1b": g0, "G1q1b": g1, "C2": c2,
        "estimands": {
            "cos_AB": "mean over authors of cos(card_A(a), card_B(a))",
            "r_A, r_B": "the measured card-vs-trait statistic; PINNED to Q1's reading "
                        "B = r_card_b_raw (k2b:486). See RN-Q1B-1",
            "Delta": "cos_AB - r_A * r_B, fully paired per world-pair",
            "Delta_cos": "cos_AB - r_cos_A * r_cos_B (estimator-consistent, reported)",
            "Delta_author": "mean over authors of [cos(A,B) - cos(A,t)cos(B,t)] "
                            "(per-author exact, reported)",
            "identity_share": "Delta / cos_AB -- UNBUDGETED descriptive"},
        "design": {"share": SHARE, "phi": [PHI_LO, PHI_HI],
                   "pairs_per_phi": N_PAIRS, "chunk": CHUNK,
                   "total_worlds": 2 * 2 * N_PAIRS},
        "sides_rule22": {
            "L-1q1b": {"clause": "PURE_TRAIT / IDENTITY_BEYOND_TRAIT / "
                                 "ANTI_CORRELATED / underpowered",
                       "prior": "0.40 / 0.40 / 0.05 / 0.15",
                       "sided": "categorical"},
            "V-Q1b": {"clause": "mean Delta vs 0, NULL-first, per phi and pooled",
                      "sided": "two-sided"},
            "G3q1b": {"clause": f"power >= {POWER_MIN} at Delta = {DELTA_MATERIAL} and "
                                f"false-fire <= {FALSE_FIRE_MAX} at Delta = 0",
                      "sided": "one-sided each"}},
        "stage_estimates_seconds": {"part0": 150, "pilot": 60, "project": 30,
                                    "arms_each": 230, "fit": 180, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", G0=g0["PASS"], G1=g1["PASS"], C2=c2["PASS"],
         seconds=part0["seconds"])
    if not (g0["PASS"] and g1["PASS"] and c2["PASS"]):
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "INSTRUMENT_DEFECT", "routing_cell": "1",
            "routing_text": "STOP / INSTRUMENT_DEFECT", "G0q1b": g0, "G1q1b": g1,
            "C2": c2, "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- G0/G1/C2 failed")
    print(f"part0 OK  G0 PASS  G1 PASS (cards differ, control cos={g1b['cos_AB']!r} "
          f"Delta={g1b['Delta']!r}, vectors contract to k2b)  C2 PASS  "
          f"lineage {g0iii['n_found']}/{g0iii['n_total']}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# PILOT.

def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0q1b"]["PASS"]:
        raise SystemExit("STOP: G0 did not pass.")
    rows = []
    for phi in (PHI_LO, PHI_HI):
        for i in range(PILOT_PAIRS):
            rows.append(run_pair(phi, i, "-pilot"))
        print(f"  pilot phi={phi}: done ({time.time() - t0:.1f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)

    def _pred(v: np.ndarray) -> dict[str, Any]:
        fin = bool(np.all(np.isfinite(v)))
        sat = bool(np.any(np.abs(v) >= SATURATION_ABS))
        nz = bool(float(np.std(v, ddof=1)) > 0.0)
        return {"all_finite": fin, "any_saturated": sat, "nonzero_variance": nz,
                "min": float(v.min()), "max": float(v.max()),
                "PASS": bool(fin and (not sat) and nz)}

    per, ok = [], True
    for phi, grp in df.groupby("phi"):
        c = _pred(grp["cos_AB"].to_numpy(float))
        d = _pred(grp["Delta"].to_numpy(float))
        ok &= c["PASS"] and d["PASS"]
        per.append({"phi": float(phi), "n": int(len(grp)),
                    "cos_AB_mean": float(grp["cos_AB"].mean()),
                    "r_raw_product_mean": float(grp["r_raw_product"].mean()),
                    "Delta_mean": float(grp["Delta"].mean()),
                    "Delta_cos_mean": float(grp["Delta_cos"].mean()),
                    "Delta_author_mean": float(grp["Delta_author"].mean()),
                    "Delta_cen_mean": float(grp["Delta_cen"].mean()),
                    "Delta_author_cen_mean": float(grp["Delta_author_cen"].mean()),
                    "cos_regime": c, "Delta_regime": d,
                    "PASS": bool(c["PASS"] and d["PASS"])})

    # bands: variances only, #57 (RN-Q1B-4); ONE BAND PER READING (RN-Q1B-6)
    per_reading = {}
    for col in READINGS:
        ss_, dfree_ = 0.0, 0
        for _, grp in df.groupby("phi"):
            v = grp[col].to_numpy(float)
            ss_ += float(np.sum((v - v.mean()) ** 2))
            dfree_ += len(v) - 1
        raw_ = float(np.sqrt(ss_ / dfree_))
        infl_ = float(np.sqrt(dfree_ / float(chi2.ppf(CHI2_Q, dfree_))))
        sdv = raw_ * infl_
        per_reading[col] = {
            "sd_raw": raw_, "df": dfree_, "inflation": infl_,
            "sd_df_inflated": sdv,
            "SE_per_phi": float(sdv / math.sqrt(N_PAIRS)),
            "SE_pooled": float(sdv / math.sqrt(2 * N_PAIRS) * INDEP_MARGIN),
            "epsilon_per_phi": float(2.0 * sdv / math.sqrt(N_PAIRS)),
            "epsilon_pooled": float(2.0 * sdv / math.sqrt(2 * N_PAIRS)
                                    * INDEP_MARGIN)}
    ss = sum(float(np.sum((grp["Delta"].to_numpy(float)
                           - grp["Delta"].to_numpy(float).mean()) ** 2))
             for _, grp in df.groupby("phi"))
    dfree = per_reading["Delta"]["df"]
    sd_raw = per_reading["Delta"]["sd_raw"]
    infl = per_reading["Delta"]["inflation"]
    sd_d = per_reading["Delta"]["sd_df_inflated"]
    se_phi = per_reading["Delta"]["SE_per_phi"]
    se_pool = per_reading["Delta"]["SE_pooled"]
    bands = {
        "sd_Delta_raw": sd_raw, "pooled_df": dfree, "inflation": infl,
        "chi2_quantile": CHI2_Q, "sd_Delta_df_inflated": sd_d,
        "SE_Delta_per_phi_at_384": se_phi,
        "SE_Delta_pooled_at_768": se_pool,
        "independence_margin": INDEP_MARGIN,
        "margin_applied_to": "the POOLED SE only -- Delta is measured fully paired per "
                             "world-pair, so its per-phi SE needs no covariance; "
                             "pooling across phi would, so the 1.25 margin is applied "
                             "there and stated (RN-Q1B-4)",
        "epsilon_Delta_per_phi": float(2.0 * se_phi),
        "epsilon_Delta_pooled": float(2.0 * se_pool),
        "per_reading": per_reading,
        "readings_note": RN_NOTES["RN-Q1B-6"],
        "band_definition": "eps = 2 * SE of mean Delta at the decided pairs/phi; a NULL "
                           "verdict is a CI lying inside +/- eps",
    }
    out = {"utc": datetime.now(UTC).isoformat(),
           "G2q1b": {"per_phi": per, "PASS": bool(ok)}, "bands": bands,
           "n_pilot_pairs": int(len(df)), "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done", PASS=ok, seconds=out["seconds"])
    if not ok:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "INSTRUMENT_DEFECT", "routing_cell": "1",
            "routing_text": "STOP / INSTRUMENT_DEFECT", "G2q1b": out["G2q1b"],
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- pilot predicate failed")
    print(f"pilot OK  sd_Delta={sd_d!r}  eps_phi={bands['epsilon_Delta_per_phi']!r}  "
          f"eps_pooled={bands['epsilon_Delta_pooled']!r}  "
          f"Delta means {[round(q['Delta_mean'], 6) for q in per]}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# G3q1b -- the projection.

def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    pil = read_json(OUT / "pilot.json")
    sd_d = pil["bands"]["sd_Delta_df_inflated"]

    def project(n: int) -> dict[str, Any]:
        se = float(sd_d / math.sqrt(n))
        rg = np.random.default_rng(MASTER_SEED)
        out = {}
        for name, truth in (("Delta = 0", 0.0),
                            (f"Delta = {DELTA_MATERIAL}", DELTA_MATERIAL)):
            draws = rg.normal(truth, se, size=B_PROJ)
            fires = float(np.mean(np.abs(draws) > 2.0 * se))
            out[name] = {"truth": truth, "SE": se,
                         "fires_at_2SE": fires,
                         "role": "false-fire" if truth == 0.0 else "power",
                         "bar": (FALSE_FIRE_MAX if truth == 0.0 else POWER_MIN),
                         "PASS": bool(fires <= FALSE_FIRE_MAX) if truth == 0.0
                         else bool(fires >= POWER_MIN)}
        return {"pairs_per_phi": n, "SE_mean_Delta": se, "per_truth": out,
                "PASS": bool(all(d["PASS"] for d in out.values()))}

    base = project(N_PAIRS)
    esc = None
    decided = N_PAIRS
    if not base["PASS"]:
        print(f"  G3q1b FAILED at n={N_PAIRS}; once-only escalation to "
              f"n={N_PAIRS_ESCALATED}", flush=True)
        esc = project(N_PAIRS_ESCALATED)
        if esc["PASS"]:
            decided = N_PAIRS_ESCALATED
    g3 = {"truths": {"null": 0.0, "material": DELTA_MATERIAL},
          "B_proj": B_PROJ, "base": base, "escalated": esc,
          "escalation_fired": bool(esc is not None),
          "pairs_per_phi_decided": decided,
          "PASS": bool(base["PASS"] or (esc is not None and esc["PASS"])),
          "on_fail": "NON_PROJECTABLE", "seconds": time.time() - t0}
    write_json(OUT / "projection.json", g3)
    _log("project_done", PASS=g3["PASS"], seconds=g3["seconds"])
    if not g3["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "NON_PROJECTABLE", "routing_cell": "2",
            "routing_text": "NON_PROJECTABLE", "G3q1b": g3,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"{k}: fires={d['fires_at_2SE']!r}" for k, d in base["per_truth"].items())
        + f"  n={decided}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# ARMS.

def _arm_specs(n: int) -> list[tuple[str, float, int, int]]:
    out = []
    for phi in (PHI_LO, PHI_HI):
        for lo in range(0, n, CHUNK):
            out.append((f"p{phi}_{lo}_{min(lo + CHUNK, n)}", phi, lo,
                        min(lo + CHUNK, n)))
    return out


def _arm(tag: str) -> None:
    t0 = time.time()
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: the projection did not pass.")
    n = int(g3["pairs_per_phi_decided"])
    spec = next((s for s in _arm_specs(n) if s[0] == tag), None)
    if spec is None:
        raise SystemExit(f"REFUSED: unknown arm {tag!r} at n={n}")
    _, phi, lo, hi = spec
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    path = OUT / "arms" / f"arm_{tag}.csv"
    if path.exists() and len(read_csv_rt(path)) == hi - lo:
        print(f"  {tag}: already complete, skipped", flush=True)
    else:
        rows = [run_pair(phi, i, "") for i in range(lo, hi)]
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"  {tag}: n={len(rows)} ({time.time() - t0:.1f}s)", flush=True)
    _log(f"arm_{tag}_done", seconds=time.time() - t0)
    print(f"arm {tag} OK  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# FIT.

def _classify(lo: float, hi: float, eps: float) -> tuple[str, str]:
    inside = bool(lo >= -eps and hi <= eps)
    excl0 = bool(lo > 0.0 or hi < 0.0)
    if inside:
        pinned = "NULL"
    elif excl0:
        pinned = "POSITIVE" if lo > 0.0 else "NEGATIVE"
    else:
        pinned = "UNDERPOWERED"
    if excl0:
        sf = "POSITIVE" if lo > 0.0 else "NEGATIVE"
    elif inside:
        sf = "NULL"
    else:
        sf = "UNDERPOWERED"
    return pinned, sf


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    n = int(g3["pairs_per_phi_decided"])
    eps_phi = pil["bands"]["epsilon_Delta_per_phi"]
    eps_pool = pil["bands"]["epsilon_Delta_pooled"]

    frames = {}
    for phi in (PHI_LO, PHI_HI):
        parts = [read_csv_rt(OUT / "arms" / f"arm_{s[0]}.csv")
                 for s in _arm_specs(n) if s[1] == phi]
        d = pd.concat(parts, ignore_index=True).sort_values("pair")
        if len(d) != n or sorted(d["pair"].tolist()) != list(range(n)):
            raise SystemExit(f"REFUSED: phi={phi} assembled {len(d)}, want {n}")
        if not bool(d["cards_differ_all_authors"].all()):
            raise SystemExit(f"REFUSED: card_A == card_B somewhere at phi={phi}")
        frames[phi] = d

    rng = np.random.default_rng(MASTER_SEED)
    idx = {phi: rng.integers(0, n, size=(B_BOOT_HIGH, n)) for phi in frames}

    def ci_of(vals: np.ndarray, phi: float, B: int) -> tuple[list[float], np.ndarray]:
        bs = vals[idx[phi][:B]].mean(axis=1)
        return [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))], bs

    per_phi, boots = [], {}
    for phi in (PHI_LO, PHI_HI):
        d = frames[phi]
        rec: dict[str, Any] = {"phi": phi, "n": int(len(d))}
        for col in ("cos_AB", "r_raw_A", "r_raw_B", "r_cen_A", "r_cen_B",
                    "r_raw_product", "r_cos_product", "r_cen_product",
                    "Delta", "Delta_cos", "Delta_author", "Delta_cen",
                    "Delta_author_cen"):
            v = d[col].to_numpy(float)
            rec[f"{col}_mean"] = float(v.mean())
            rec[f"{col}_sem"] = float(np.std(v, ddof=1) / np.sqrt(len(v)))
        for col in READINGS:
            c, bs = ci_of(d[col].to_numpy(float), phi, B_BOOT)
            rec[f"{col}_ci95"] = c
            boots[(phi, col)] = bs
            e = pil["bands"]["per_reading"][col]["epsilon_per_phi"]
            rec[f"{col}_epsilon"] = e
            rec[f"{col}_class"] = _classify(c[0], c[1], e)[0]
        cls, sf = _classify(rec["Delta_ci95"][0], rec["Delta_ci95"][1], eps_phi)
        rec["classification"] = cls
        rec["classification_sign_first"] = sf
        rec["readings_agree"] = bool(cls == sf)
        rec["classification_Delta_cos"] = rec["Delta_cos_class"]
        rec["classification_Delta_author"] = rec["Delta_author_class"]
        rec["classification_Delta_cen"] = rec["Delta_cen_class"]
        rec["classification_Delta_author_cen"] = rec["Delta_author_cen_class"]
        sh = d["Delta"].to_numpy(float) / d["cos_AB"].to_numpy(float)
        rec["identity_share_mean"] = float(sh.mean())
        shb = sh[idx[phi][:B_BOOT]].mean(axis=1)
        rec["identity_share_ci95"] = [float(np.quantile(shb, 0.025)),
                                      float(np.quantile(shb, 0.975))]
        per_phi.append(rec)

    pooled_vals = np.concatenate([frames[p]["Delta"].to_numpy(float)
                                  for p in (PHI_LO, PHI_HI)])
    pooled_mean = float(pooled_vals.mean())
    pb = np.concatenate([boots[(PHI_LO, "Delta")][:, None],
                         boots[(PHI_HI, "Delta")][:, None]], axis=1).mean(axis=1)
    pooled_ci = [float(np.quantile(pb, 0.025)), float(np.quantile(pb, 0.975))]
    pooled_cls, pooled_sf = _classify(pooled_ci[0], pooled_ci[1], eps_pool)

    # rule 13
    margin = 1.0 / (RULE13_FACTOR * B_BOOT)
    near = []
    for nm, arr, e in (("pooled Delta", pb, eps_pool),):
        for bnd in (0.0, e, -e):
            frac = float(np.mean(arr <= bnd))
            if min(abs(frac - 0.025), abs(frac - 0.975)) < margin:
                near.append({"quantity": nm, "boundary": bnd, "tail_frac": frac})
    rule13 = []
    if near:
        pb2 = np.concatenate(
            [frames[PHI_LO]["Delta"].to_numpy(float)[idx[PHI_LO]].mean(axis=1)[:, None],
             frames[PHI_HI]["Delta"].to_numpy(float)[idx[PHI_HI]].mean(axis=1)[:, None]],
            axis=1).mean(axis=1)
        pooled_ci = [float(np.quantile(pb2, 0.025)), float(np.quantile(pb2, 0.975))]
        pooled_cls, pooled_sf = _classify(pooled_ci[0], pooled_ci[1], eps_pool)
        rule13.append({"triggers": near, "B": B_BOOT_HIGH, "ci_after": pooled_ci})

    classes = {str(q["phi"]): q["classification"] for q in per_phi}
    out = {"utc": datetime.now(UTC).isoformat(), "pairs_per_phi": n,
           "per_phi": per_phi, "classes": classes,
           "phi_agree": bool(len(set(classes.values())) == 1),
           "pooled_Delta": pooled_mean, "pooled_Delta_ci95": pooled_ci,
           "pooled_classification": pooled_cls,
           "pooled_classification_sign_first": pooled_sf,
           "epsilon_per_phi": eps_phi, "epsilon_pooled": eps_pool,
           "uncentred_readings_agree": bool(
               len({q["classification"] for q in per_phi}
                   | {q["classification_Delta_cos"] for q in per_phi}
                   | {q["classification_Delta_author"] for q in per_phi}) == 1),
           "centred_classes": {str(q["phi"]): [q["classification_Delta_cen"],
                                               q["classification_Delta_author_cen"]]
                               for q in per_phi},
           "centred_vs_registered_agree": bool(
               {q["classification"] for q in per_phi}
               == {q["classification_Delta_author_cen"] for q in per_phi}),
           "three_readings_agree": bool(
               len({q["classification"] for q in per_phi}
                   | {q["classification_Delta_cos"] for q in per_phi}
                   | {q["classification_Delta_author"] for q in per_phi}) == 1),
           "rule13_events": rule13, "B": B_BOOT,
           "control_pair": read_json(OUT / "part0.json")["G1q1b"]["(b) control pair"],
           "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done", classes=classes, pooled=pooled_cls, seconds=out["seconds"])
    print(f"fit OK  " + "  ".join(
        f"phi={q['phi']}: Delta={q['Delta_mean']:+.6f} {q['Delta_ci95']} "
        f"{q['classification']}" for q in per_phi)
        + f"  pooled={pooled_mean:+.6f} {pooled_ci} {pooled_cls}  "
          f"3-readings-agree={out['three_readings_agree']}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "G0/G1 failure", "outcome": "INSTRUMENT_DEFECT",
     "text": "STOP / INSTRUMENT_DEFECT"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE"},
    {"n": "3", "condition": "Delta NULL (both phi)", "outcome": "CARD_PURE_TRAIT",
     "text": "CARD_PURE_TRAIT -- cards are trait plus frame-independent noise; the "
             "disattenuation identity holds at card level; the taxonomy completes: "
             "cards read the trait, the gauge reads the frame"},
    {"n": "4", "condition": "Delta POSITIVE (both phi)",
     "outcome": "CARD_CARRIES_IDENTITY_BEYOND_TRAIT",
     "text": "CARD_CARRIES_IDENTITY_BEYOND_TRAIT -- the card transports author-stream "
             "content the trait does not span"},
    {"n": "5", "condition": "Delta NEGATIVE (both phi)",
     "outcome": "ANTI_CORRELATED_NAMED",
     "text": "ANTI_CORRELATED_NAMED -- new phenomenon; theory note"},
    {"n": "6", "condition": "phi's disagree in classification", "outcome": "PHI_SPLIT",
     "text": "PHI_SPLIT -- named; the phi-dependence itself becomes the finding"},
    {"n": "7", "condition": "any UNDERPOWERED (no higher cell)",
     "outcome": "UNDERPOWERED", "text": "UNDERPOWERED (levels reported)"},
]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    cls = list(fit["classes"].values())
    if not fit["phi_agree"]:
        slug = ("UNDERPOWERED" if "UNDERPOWERED" in cls else "PHI_SPLIT")
    elif cls[0] == "NULL":
        slug = "CARD_PURE_TRAIT"
    elif cls[0] == "POSITIVE":
        slug = "CARD_CARRIES_IDENTITY_BEYOND_TRAIT"
    elif cls[0] == "NEGATIVE":
        slug = "ANTI_CORRELATED_NAMED"
    else:
        slug = "UNDERPOWERED"
    cell_n = next(t["n"] for t in TRUTH_TABLE if t["outcome"] == slug)

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": [],
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "classes": fit["classes"], "phi_agree": fit["phi_agree"],
        "pooled_Delta": fit["pooled_Delta"],
        "pooled_Delta_ci95": fit["pooled_Delta_ci95"],
        "pooled_classification": fit["pooled_classification"],
        "epsilon_per_phi": fit["epsilon_per_phi"],
        "epsilon_pooled": fit["epsilon_pooled"],
        "three_readings_agree": fit["three_readings_agree"],
        "per_phi": fit["per_phi"], "pairs_per_phi": fit["pairs_per_phi"],
        "total_worlds": int(2 * 2 * fit["pairs_per_phi"]),
        "control_pair": fit["control_pair"],
        "G0q1b": p0["G0q1b"], "G1q1b": p0["G1q1b"], "C2": p0["C2"],
        "bands": pil["bands"], "projection": g3,
        "rule13_events": fit["rule13_events"],
        "gates": {
            "G0q1b": {"PASS": p0["G0q1b"]["PASS"],
                      "detail": "Q1's record and both 0.827 objects, the instrument "
                                "hashes, and the disattenuation lineage"},
            "G1q1b": {"PASS": p0["G1q1b"]["PASS"],
                      "detail": "card_A != card_B for every author of every probe "
                                "pair; the control pair gives cos = 1 and "
                                "Delta = 1 - r^2 > 0; the 64-dim vectors contract "
                                "EXACTLY to k2b's own card columns"},
            "C2": {"PASS": p0["C2"]["PASS"],
                   "detail": f"{PROBE_PAIRS} fresh probe pairs"},
            "G2q1b": {"PASS": pil["G2q1b"]["PASS"],
                      "detail": "rule-29 predicate on cos_AB and Delta; bands from "
                                "variances only with the 1.25 margin stated"},
            "G3q1b": {"PASS": g3["PASS"],
                      "detail": f"escalation fired: {g3['escalation_fired']}"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, pil, g3, fit, dec)
    _facts(p0, pil, g3, fit, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  classes={fit['classes']}")
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


def _tables(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
            fit: dict[str, Any], dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    pv = p0["G0q1b"]["(ii) hashes"]
    sec["provenance"] = _md(
        ["property", "value"],
        [["instrument", "`" + pv["instrument_from"] + "`"],
         ["instrument function sha256", pv["instrument_function_sha256"]],
         ["matches Q1's persisted", str(pv["instrument_sha_matches"])],
         ["card path", "`" + pv["card_path_from"] + ":"
          + str(pv["card_path_line"]) + "` (`" + pv["card_path_function"] + "`)"],
         ["card path function sha256", pv["card_path_function_sha256"]],
         ["card path proven bit-exact in Q1",
          str(pv["card_path_proven_bit_exact_in_Q1"])]])
    g0i = p0["G0q1b"]["(i) Q1 record"]
    sec["q1record"] = _md(
        ["quantity", "value"],
        [["Q1 verdict", g0i["q1_verdict"]],
         ["Q1 zero-point identity PASS", str(g0i["q1_zero_point_PASS"])
          + f" ({g0i['q1_zero_point_n']} checks)"],
         ["closed-form pin", "`" + g0i["card_pred_pin"] + "`"],
         ["closed-form value", repr(g0i["card_pred_value"])],
         ["measured pin", "`" + g0i["card_meas_pin"] + "`"],
         ["measured value", repr(g0i["card_meas_value"])],
         ["**reading B (what r_A / r_B use)**", "**" + g0i["reading_B_is"] + "**"]])
    sec["lineage"] = _md(
        ["anchor", "located at", "verbatim quote (extracted by code, rule 24)"],
        [[k, f"`{d['file']}:{d['line']}` (para {d['paragraph_lines']})",
          d["quote"][:700] + ("…" if len(d["quote"]) > 700 else "")]
         if d["found"] else [k, "NOT FOUND", "—"]
         for k, d in p0["G0q1b"]["(iii) lineage"]["anchors"].items()])
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
           ["**C2**", "—", "**PASS = " + str(c2["PASS"]) + "**"]])
    g1 = p0["G1q1b"]
    ga, gb, gc = (g1["(a) card_A != card_B"], g1["(b) control pair"],
                  g1["(c) vectors contract to k2b"])
    sec["g1"] = _md(
        ["clause", "quantity", "value"],
        [["(a) card_A != card_B", "every author of every probe pair differs",
          str(ga["all_pairs_all_authors_differ"])],
         ["(a)", "smallest per-author norm delta over all probes",
          repr(ga["min_over_all"])]]
        + [[f"(a) probe {r['probe']}",
            f"n_authors {r['n_authors']}, Frobenius", repr(r["frobenius"])]
           for r in ga["rows"]]
        + [["(b) control pair (SANITY ONLY)", "cos_AB", repr(gb["cos_AB"])],
           ["(b)", "expected cos_AB", repr(gb["expected_cos_AB"])],
           ["(b)", "Delta", repr(gb["Delta"])],
           ["(b)", "expected 1 - r_A*r_B", repr(gb["expected_Delta"])],
           ["(b)", "Delta > 0 by construction", str(gb["Delta_positive"])],
           ["(b)", "status", gb["status"]],
           ["(c) vectors contract to k2b", "full_n", str(gc["full_n_matches"])],
           ["(c)", "b_raw_n", str(gc["b_raw_n_matches"])],
           ["(c)", "full_b_dot_raw", str(gc["dot_matches"])],
           ["(c)", "r_cos_raw", str(gc["cos_matches"])],
           ["(c)", "meaning", gc["meaning"]]])
    b = pil["bands"]
    sec["bands"] = _md(
        ["quantity", "value"],
        [["sd(Delta) raw / df-inflated",
          repr(b["sd_Delta_raw"]) + " / " + repr(b["sd_Delta_df_inflated"])],
         ["pooled df / inflation", str(b["pooled_df"]) + " / " + repr(b["inflation"])],
         ["SE(mean Delta) per phi at 384", repr(b["SE_Delta_per_phi_at_384"])],
         ["SE(mean Delta) pooled at 768", repr(b["SE_Delta_pooled_at_768"])],
         ["independence margin (#57)", repr(b["independence_margin"])],
         ["margin applied to", b["margin_applied_to"]],
         ["**epsilon_Delta per phi**", "**" + repr(b["epsilon_Delta_per_phi"]) + "**"],
         ["**epsilon_Delta pooled**", "**" + repr(b["epsilon_Delta_pooled"]) + "**"]])
    rows = []
    for label, blk in (("384 (registered)", g3["base"]),
                       ("768 (escalated)", g3["escalated"])):
        if blk is None:
            continue
        for k, d in blk["per_truth"].items():
            rows.append([label, k, d["role"], repr(d["SE"]), repr(d["fires_at_2SE"]),
                         repr(d["bar"]), str(d["PASS"])])
    sec["projection"] = _md(
        ["pairs/phi", "truth", "role", "SE(mean Delta)", "fires at 2 SE", "bar",
         "PASS"], rows)
    sec["dual"] = _md(
        ["phi", "n", "cos_AB", "SEM", "r_A-hat", "r_B-hat", "r-product",
         "**Delta**", "Delta 95% CI", "classification"],
        [[repr(q["phi"]), str(q["n"]), repr(q["cos_AB_mean"]), repr(q["cos_AB_sem"]),
          repr(q["r_raw_A_mean"]), repr(q["r_raw_B_mean"]),
          repr(q["r_raw_product_mean"]), "**" + repr(q["Delta_mean"]) + "**",
          repr(q["Delta_ci95"]), "**" + q["classification"] + "**"]
         for q in fit["per_phi"]]
        + [["**pooled**", str(2 * fit["pairs_per_phi"]), "—", "—", "—", "—", "—",
            "**" + repr(fit["pooled_Delta"]) + "**",
            repr(fit["pooled_Delta_ci95"]),
            "**" + fit["pooled_classification"] + "**"]])
    sec["readings"] = _md(
        ["phi", "reference object", "reading", "point", "95% CI", "epsilon", "class"],
        [row for q in fit["per_phi"] for row in (
            [repr(q["phi"]), "UNCENTRED trait", "Delta (registered, r_raw) -- ROUTES",
             repr(q["Delta_mean"]), repr(q["Delta_ci95"]), repr(q["Delta_epsilon"]),
             "**" + q["classification"] + "**"],
            [repr(q["phi"]), "UNCENTRED trait", "Delta_cos (estimator-consistent)",
             repr(q["Delta_cos_mean"]), repr(q["Delta_cos_ci95"]),
             repr(q["Delta_cos_epsilon"]), q["classification_Delta_cos"]],
            [repr(q["phi"]), "UNCENTRED trait", "Delta_author (per-author)",
             repr(q["Delta_author_mean"]), repr(q["Delta_author_ci95"]),
             repr(q["Delta_author_epsilon"]), q["classification_Delta_author"]],
            [repr(q["phi"]), "**CENTRED trait (what the card contains)**",
             "Delta_cen (pooled r_card_b_cen)", repr(q["Delta_cen_mean"]),
             repr(q["Delta_cen_ci95"]), repr(q["Delta_cen_epsilon"]),
             q["classification_Delta_cen"]],
            [repr(q["phi"]), "**CENTRED trait**",
             "**Delta_author_cen (per-author EXACT)**",
             "**" + repr(q["Delta_author_cen_mean"]) + "**",
             repr(q["Delta_author_cen_ci95"]), repr(q["Delta_author_cen_epsilon"]),
             "**" + q["classification_Delta_author_cen"] + "**"])]
        + [["—", "—", "the three UNCENTRED readings agree", "—", "—", "—",
            str(fit["uncentred_readings_agree"])],
           ["—", "—", "**centred agrees with registered**", "—", "—", "—",
            "**" + str(fit["centred_vs_registered_agree"]) + "**"]])
    sec["share"] = _md(
        ["phi", "identity share Delta / cos_AB", "95% CI", "label"],
        [[repr(q["phi"]), repr(q["identity_share_mean"]),
          repr(q["identity_share_ci95"]),
          "UNBUDGETED -- descriptive, routes nothing"] for q in fit["per_phi"]])
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
    sec["env"] = _md(["component", "value"],
                     [[k, str(v)] for k, v in p0["environment"].items()])
    est = p0["stage_estimates_seconds"]
    meas: dict[str, float] = {}
    for line in (OUT / "run_log.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if "seconds" in r:
            meas[r["event"]] = float(r["seconds"])
    trows = [["part0", str(est["part0"]),
              "%.3f" % meas.get("part0_done", float("nan"))],
             ["pilot", str(est["pilot"]),
              "%.3f" % meas.get("pilot_done", float("nan"))],
             ["project", str(est["project"]),
              "%.3f" % meas.get("project_done", float("nan"))]]
    for tag, _, _, _ in _arm_specs(fit["pairs_per_phi"]):
        trows.append([f"arm {tag}", str(est["arms_each"]),
                      "%.3f" % meas.get(f"arm_{tag}_done", float("nan"))])
    trows += [["fit", str(est["fit"]), "%.3f" % meas.get("fit_done", float("nan"))],
              ["finalize", str(est["finalize"]),
               "%.3f" % meas.get("finalize_done", float("nan"))]]
    sec["timing"] = _md(["stage", "estimate (s)", "measured (s)"], trows)
    body = ["# M4-Q1b report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
           fit: dict[str, Any], dec: dict[str, Any]) -> None:
    b = pil["bands"]
    gb = p0["G1q1b"]["(b) control pair"]
    ga = p0["G1q1b"]["(a) card_A != card_B"]
    lin = p0["G0q1b"]["(iii) lineage"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "MODIFIERS": ", ".join(dec["modifiers"]) or "none",
        "NPAIRS": fit["pairs_per_phi"], "NWORLDS": dec["total_worlds"],
        "POOLED": fit["pooled_Delta"], "POOLED_CI": fit["pooled_Delta_ci95"],
        "POOLED_CLASS": fit["pooled_classification"],
        "EPS_PHI": fit["epsilon_per_phi"], "EPS_POOL": fit["epsilon_pooled"],
        "AGREE3": fit["three_readings_agree"],
        "UNCEN_AGREE": fit["uncentred_readings_agree"],
        "CEN_AGREE": fit["centred_vs_registered_agree"],
        "PHI_AGREE": fit["phi_agree"],
        "CTL_COS": gb["cos_AB"], "CTL_DELTA": gb["Delta"],
        "CTL_EXP": gb["expected_Delta"], "CTL_POS": gb["Delta_positive"],
        "CARDS_DIFFER": ga["all_pairs_all_authors_differ"],
        "MIN_DELTA_NORM": ga["min_over_all"],
        "LIN_FOUND": lin["n_found"], "LIN_TOTAL": lin["n_total"],
        "SD_D": b["sd_Delta_df_inflated"], "MARGIN": b["independence_margin"],
        "SE_PHI": b["SE_Delta_per_phi_at_384"], "SE_POOL": b["SE_Delta_pooled_at_768"],
        "ESC": g3["escalation_fired"],
        "FF": g3["base"]["per_truth"]["Delta = 0"]["fires_at_2SE"],
        "PW": g3["base"]["per_truth"][f"Delta = {DELTA_MATERIAL}"]["fires_at_2SE"],
        "NRULE13": len(fit["rule13_events"]), "B": fit["B"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    for q in fit["per_phi"]:
        t = str(q["phi"]).replace(".", "")
        f[f"P{t}_COS"] = q["cos_AB_mean"]
        f[f"P{t}_RPROD"] = q["r_raw_product_mean"]
        f[f"P{t}_D"] = q["Delta_mean"]
        f[f"P{t}_DCI"] = q["Delta_ci95"]
        f[f"P{t}_CLASS"] = q["classification"]
        f[f"P{t}_DCOS"] = q["Delta_cos_mean"]
        f[f"P{t}_DAUT"] = q["Delta_author_mean"]
        f[f"P{t}_DCEN"] = q["Delta_cen_mean"]
        f[f"P{t}_DCENCI"] = q["Delta_cen_ci95"]
        f[f"P{t}_DCENCL"] = q["classification_Delta_cen"]
        f[f"P{t}_DACEN"] = q["Delta_author_cen_mean"]
        f[f"P{t}_DACENCI"] = q["Delta_author_cen_ci95"]
        f[f"P{t}_DACENCL"] = q["classification_Delta_author_cen"]
        f[f"P{t}_RCENPROD"] = q["r_cen_product_mean"]
        f[f"P{t}_SHARE"] = q["identity_share_mean"]
        f[f"P{t}_SHARECI"] = q["identity_share_ci95"]
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-Q1b — the cross-frame card cosine — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}); modifiers: {{MODIFIERS}}.**
{{ROUTING_TEXT}}

**Pooled Δ = {{POOLED}} {{POOLED_CI}} → {{POOLED_CLASS}}** (ε_pooled =
{{EPS_POOL}}); per φ: {{P005_D}} {{P005_DCI}} → {{P005_CLASS}} and {{P098_D}}
{{P098_DCI}} → {{P098_CLASS}} (ε_per-φ = {{EPS_PHI}}). {{NWORLDS}} worlds
({{NPAIRS}} A/B pairs per φ).

> ## ⚠ The slug's stated consequence is contradicted by this leg's own arithmetic
>
> Cell 4 says the card "transports author-stream content the trait does not
> span". **It does not.** The registered Δ scores each card's fidelity against
> the UNCENTRED trait, but the card contains the CENTRED trait
> (`full = w_mu·trait_c + …`, k2b:423). Against the reference the cards
> actually share, the per-author exact identity gives
> **Δ = {{P005_DACEN}} {{P005_DACENCI}} at φ = 0.05 and {{P098_DACEN}}
> {{P098_DACENCI}} at φ = 0.98 — both straddling zero ({{P005_DACENCL}} /
> {{P098_DACENCL}})**, i.e. **CARD_PURE_TRAIT**, the opposite cell.
>
> The registration is binding, so the literal reading routes and the slug
> stands as registered. But the entailment it asserts — "Δ POSITIVE is entailed
> to be author-stream content beyond the trait — no other shared channel
> exists" — is false: **no other channel is needed.** The trait channel alone
> produces Δ > 0 once the reference object is the uncentred trait. This is
> raised as the leg's primary registration-defect candidate (§3), and it was
> found on probe pairs and pinned as RN-Q1B-6 **before any measurement arm
> ran**.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md` BEFORE run (commit 527d176). Every
number below is generated from artifacts by code (rule 24).

---

## 1. The question, and why it is not degenerate

Q1 failed because the object it swapped was shared by construction. **Here
nothing is swapped.** cos_AB, r̂_A and r̂_B are measurements of three *different*
vector pairs, and A's and B's cards genuinely differ because `slow`, `noise` and
`int` are frame-stream objects. C2a certifies that A and B share **only** the
author stream, so any excess of cos(A,B) over the trait-predicted product
r̂_A·r̂_B is author-stream content the trait does not span.

<<TABLE:g1>>

card_A ≠ card_B for **every author of every probe pair** ({{CARDS_DIFFER}};
smallest per-author norm delta {{MIN_DELTA_NORM}}), proven before any statistic
was read. The same-frame-seed control returns cos_AB = {{CTL_COS}} and
Δ = {{CTL_DELTA}} against the constructed expectation {{CTL_EXP}} — operator
sanity only, excluded from every band, projection and verdict (RN-Q1B-3). And
the 64-dim vectors this leg forms contract **exactly** to the columns k2b's own
`card_channel_frame` emits, so the cosines are built from k2b's cards.

## 2. Provenance

<<TABLE:provenance>>

<<TABLE:q1record>>

## 3. The reference-object confound — the leg's central finding

RN-Q1B-6, pinned in Part 0 from probe pairs, before any arm.

The card is `full = w_mu·trait_c + w_slow·slow_c̄ + w_noise·noise_c̄`
(k2b:423-427). Its trait component is **trait_c, the cell-centred trait**. The
only content A and B share is exactly `w_mu·trait_c` — `slow`, `noise` and `int`
are frame-stream and independent between them. So the disattenuation identity
that actually holds is

    cos(card_A, card_B) = cos(card_A, trait_c) · cos(card_B, trait_c)

with the **centred** reference. But `r_card_b_raw` and `r_card_b_cos` both score
the card against `trait`, the **uncentred** array (k2b:443/446). Scoring against
an object the card does not contain understates each card's alignment with what
it *does* share, so r̂·r̂ understates cos_AB and Δ comes out positive with no
content beyond the trait involved.

<<TABLE:readings>>

The three UNCENTRED readings agree with each other ({{UNCEN_AGREE}}) — so the
estimator-family ambiguity of RN-Q1B-1 turns out not to matter. What matters is
the **reference object**, and the centred readings disagree with the registered
one ({{CEN_AGREE}}): the per-author exact form lands at {{P005_DACEN}} and
{{P098_DACEN}}, both inside noise.

## 3b. The estimator ambiguity, pinned before any number

**RN-Q1B-1 is the methodological heart of this leg.** cos_AB is a *mean of
per-author cosines*. `pooled_card_stats` emits **two** card-vs-trait statistics
from the same frame: `r_card_b_raw` (a ratio of sums — Q1's "reading B", the one
appendix N quotes) and `r_card_b_cos` (a mean of per-author cosines — the *same*
estimator family as cos_AB). The disattenuation identity is a **per-author**
statement, so mixing families leaves a bias of unknown sign in Δ.

The registration says "Q1's reading B, `pooled_card_stats` lineage", which
literally names `r_card_b_raw`. That reading routes. Two alternatives are
computed at equal precision and reported:

<<TABLE:readings>>

**All three UNCENTRED readings agree in classification: {{AGREE3}}** — the
family ambiguity is immaterial here. The reference-object ambiguity of §3 is
not.

## 4. Bands and projection

<<TABLE:bands>>

Δ is measured **fully paired** per world-pair, so its per-φ SE needs no
covariance at all; the #57 independence margin of {{MARGIN}} is applied only to
the pooled SE, where pooling across φ would otherwise require one, and is
stated there (RN-Q1B-4). No pilot correlation is consumed anywhere.

<<TABLE:projection>>

At the registered 384 pairs/φ the null truth fires at {{FF}} (bar 0.1) and the
material truth Δ = 0.05 at {{PW}} (bar 0.8). Escalation did not fire ({{ESC}}).

## 5. The result

<<TABLE:dual>>

cos_AB sits at {{P005_COS}} / {{P098_COS}} against a trait-predicted product of
{{P005_RPROD}} / {{P098_RPROD}}. The φ's agree ({{PHI_AGREE}}).

### 5.1 The identity share, UNBUDGETED

<<TABLE:share>>

Quoted as a point with an honest CI and the label UNBUDGETED — it gates nothing
and routes nothing (the P3b lesson, kept visible).

### 5.2 What the sign means, stated before the measurement

RN-Q1B-5, pinned in Part 0: Δ > 0 would mean the two cards agree more than their
separate trait-fidelities can explain. C2a makes the author stream the only
shared content, and in this arm `w["int"] = 0`, so the `a_load` carrier — the
one author-stream object that is not the trait — reaches the card through **no
channel at all**. The registration's own consequence-entailment therefore
*predicts* Δ = 0, and a POSITIVE Δ would have indicated something the channel
accounting does not contain.

## 6. Routing

<<TABLE:truth_table>>

## 7. Gates

<<TABLE:gates>>

## 8. C2 battery

<<TABLE:c2>>

## 9. The disattenuation lineage

<<TABLE:lineage>>

{{LIN_FOUND}}/{{LIN_TOTAL}} anchors located and quoted by code.

## 10. Sides declared (rule 22)

<<TABLE:sides>>

## 11. Pinned readings

<<TABLE:rn>>

## 12. Rule events

- **Rule 13:** {{NRULE13}} boundary event(s); bootstrap B = {{B}}.
- **Rule 25:** the projection gate passed at the registered size.
- **Rule 26:** no bounded winner.
- **Rule 27:** the identity share is explicitly UNBUDGETED and carries the label.
- **Rule 29:** the domain-pinned predicate ran on cos_AB and Δ at both pilot φ.
- **Rule 30:** every cited constant read from its persisted source; the card
  path carries file, line and sha256, and was proven bit-exact in Q1.
- **#57:** no pilot correlation consumed; the 1.25 margin applied only where a
  covariance would otherwise be needed, and stated there.

## 13. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython {{PYTHON}} venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 14. Environment

<<TABLE:env>>

## 15. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_q1b_card_cosine/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`, `fit.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `run_log.jsonl`.
Harness: `scripts/run_suica_m4_q1b_card_cosine.py`.*
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
    path = ROOT / "reports" / "SUICA_M4_Q1B_CARD_COSINE_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("pilot", stage_pilot), ("project", stage_project)]
    seen = {n for n, _ in stages}
    for tag, _, _, _ in (_arm_specs(N_PAIRS) + _arm_specs(N_PAIRS_ESCALATED)):
        if f"arm_{tag}" in seen:
            continue
        seen.add(f"arm_{tag}")
        stages.append((f"arm_{tag}", (lambda tt: lambda a: _arm(tt))(tag)))
    stages += [("fit", stage_fit), ("finalize", stage_finalize),
               ("report", stage_report)]
    for name, fn in stages:
        sub.add_parser(name).set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
