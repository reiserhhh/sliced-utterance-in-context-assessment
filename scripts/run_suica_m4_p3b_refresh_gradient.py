#!/usr/bin/env python3
"""SUICA M4-P3b -- the refresh gradient on a certified split-seed instrument.

Registered BEFORE run in docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md
("M4-P3b", commit debc68e).  Binding.  P3's question, estimand, quantities,
verdicts, leans, budgets and routing are INHERITED VERBATIM; only the
instrument is new.

P3 proved that generator-side frame refreshment is impossible on k2b's
published two-parameter interface.  The licensed remedy is minimal extraction
with provenance: `build_split_world(author_seed, frame_seed, phi_slow)` is
extracted here from run_suica_m4_k2b_t4_branch.py:321-349 and split into two
RNG streams --

    author stream : loadings, z -> trait, a_load   (per-author-persistent
                    objects PLUS the shared basis, so an A/B pair cannot
                    silently mix two orthonormal bases -- the trap P3 named)
    frame  stream : slow state, noise, common (f2.shock_vector(frame_seed,...)),
                    shocks (k2a.shock_int_matrix(frame_seed,...))

-- with draw ORDER inside each stream preserving k2b's sequence.  k2b and
suica_core/ are untouched and diff-verified.  The instrument is certified by a
C2 battery and by M1c's anchor BEFORE any measurement world is scored.

Stages: part0 -> pilot -> project -> arm_phi<..> (5) -> fit -> finalize -> report
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import platform
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.stats import chi2

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT = ROOT / "results" / "m4_p3b_refresh_gradient"
RES = ROOT / "results"
M1CRES = RES / "m4_m1c_r_at_level"
P2RES = RES / "m4_p2_dose_decomposition"
K2BSRC = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"

LEG = "M4-P3b"
BANNER = ("the refresh gradient on a certified split-seed instrument; exploratory, "
          "label-free; no seal -- the estimand is a ratio with an honest inferential "
          "gap from P2's injection-f")

MASTER_SEED = 20260814
SALT_AUTHOR = "m4p3b-author"
SALT_FRAME_A = "m4p3b-frameA"
SALT_FRAME_B = "m4p3b-frameB"
SALT_PILOT = "m4p3b-pilot"
SHARE = 0.25
PHI_LADDER = (0.05, 0.30, 0.60, 0.85, 0.98)
N_PAIRS = 192
N_PAIRS_ESCALATED = 384
PILOT_PAIRS = 4
PILOT_PHI = (0.05, 0.98)
PROBE_PAIRS = 8
W_INT_ARM = "zero"

B_BOOT = 2000
B_BOOT_HIGH = 20000
RULE13_FACTOR = 10.0
CHI2_Q = 0.10
G_BUDGET = 0.30                 # rule-27: g_ratio CI width
PROJ_TRUTHS = (0.04, 0.5)
B_PROJ = 2000
ANCHOR_K = 2.0 * math.sqrt(2.0)  # V-P3a / C1' tolerance multiplier on SEM
SATURATION_ABS = 0.995
DEFRAME_STRIDE = 1              # set in Part 0 from the measured cost (RN-P3B-6)

AUTHOR_OBJECTS = ("trait", "a_load", "loadings")
FRAME_OBJECTS = ("slow", "slow_latent", "noise", "common", "int")

# ---------------------------------------------------------------------------
# RN-P3B notes.  PINNED IN PART 0, BEFORE ANY MEASUREMENT WORLD.
#
# RN-P3B-1 (the extraction is a transcription, not a rewrite).  Every line of
#   build_split_world below carries the k2b line it came from, and the
#   provenance table in the report is generated from that mapping.  The only
#   edits are (a) `rng` becomes `rng_a` or `rng_f` according to the pinned
#   channel taxonomy, and (b) `world_seed` becomes `author_seed` or
#   `frame_seed` at the four keyed call sites.  No expression is otherwise
#   altered; the constants (K_LATENT, DIM, G_PROFILE, A_SCALE, SIGMA_ISO) and
#   the helpers (_orthonormal_loadings, f2.shock_vector, k2a.shock_int_matrix,
#   v8.stable_bucket) are IMPORTED FROM k2b, never copied, so a change there
#   propagates here rather than silently diverging.
#
# RN-P3B-2 (why the split cannot reproduce k2b bit-exactly, and why that is
#   correct).  k2b draws loadings, z, _zeta, xs and noise from ONE stream.  Two
#   independent streams cannot reproduce a single stream's sequence even at
#   equal seeds: the frame stream restarts at the seed's first draw rather than
#   continuing where the author draws stopped.  So
#   build_split_world(s, s, phi) != build_k2b_world(s, phi), BY CONSTRUCTION,
#   and the check is reported as EXPECTED-DIFFERENT rather than as a failure.
#   The substantive equivalence test is C1' -- the extracted instrument must
#   reproduce M1c's MEASURED five-level row distributionally.  Plumbing changes
#   seeds; it must not change the law.
#
# RN-P3B-3 (_zeta's placement).  k2b draws an unused (n, k) normal between z
#   and the state (k2b:324, commented "stream order").  It is placed in the
#   AUTHOR stream here, keeping k2b's relative order among the author draws.
#   It is unused in k2b and unused here, so it cannot affect any output -- only
#   the stream position of the draws that follow it, which is exactly what
#   "preserves k2b's sequence" requires.
#
# RN-P3B-4 (the shared basis is the whole point).  loadings is drawn from the
#   AUTHOR stream, so an A/B pair sharing author_seed shares its orthonormal
#   basis bit-identically.  P3 named the trap: cross-scoring A's gauge against
#   B's truth is meaningless if A's trait and B's common live in different
#   bases.  C2c proves the basis is shared on every probe pair.
#
# RN-P3B-5 (what the refreshed truth panel actually is).  The b-only truth is
#   emit_panel(world, w, active=("mu", "common")) = w_mu*trait + w_common*common.
#   A and B share author_seed, so B's trait is BIT-IDENTICAL to A's, and the
#   refreshed truth panel is therefore exactly "A's persons carrying B's
#   frame".  This is checked, not assumed (C2a reports trait identity and
#   common difference separately).
#
# RN-P3B-6 (R_deframe's cost and its stride).  The secondary reading applies
#   K-R1's transcription of K1b's ESTIMATED de-framing --
#   kr1.mu_hat_field(...) then kr1.deframe_panel(...) at the leg's PRIMARY
#   readings (donor_channels="k1b_literal", pool_scheme="per_context") -- to
#   A's panel, and scores the de-framed gauge against A's truth.  It costs a
#   donor-pool build plus a second full gauge pass per world.  The stride at
#   which it is computed is measured in Part 0 and pinned there BEFORE any
#   measurement world; it is descriptive and ungated, so a stride > 1 costs
#   only precision on a quantity that adjudicates nothing, and the realized
#   n per phi is reported beside it.
#
# RN-P3B-7 (classification order, inherited).  NULL-first per #55 and P3's
#   registration: the equivalence band is computed in Part 0 from realized
#   noise, tested first, then the sign/level cuts, then UNDERPOWERED.  The
#   band and the V-P3c floor are written into the report BEFORE the main arms.
#
# RN-P3B-8 (corpus labels).  Arm tags carry no phi where the machinery permits.
#   R_nat, R_refresh and R_deframe at a given world index share ONE corpus
#   string by construction (they share one gauge pass or, for R_deframe, the
#   same tag), so P1's label-noise finding cannot enter any contrast computed
#   within a world.  Across phi the tag must differ because the arms are
#   separate files; that is the natural regime and the label note applies to
#   REPLICATION anchors only (C1'), which are distributional by design.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-P3B-1": "the extraction is a transcription: every line carries its k2b source "
                "line, the only edits are rng -> rng_a/rng_f and world_seed -> "
                "author_seed/frame_seed at the four keyed call sites, and all constants "
                "and helpers are IMPORTED from k2b rather than copied",
    "RN-P3B-2": "build_split_world(s, s, phi) != build_k2b_world(s, phi) BY "
                "CONSTRUCTION -- two independent streams cannot reproduce one stream's "
                "sequence -- so that check is reported EXPECTED-DIFFERENT; the "
                "substantive equivalence test is C1', which demands the law, not the "
                "seeds",
    "RN-P3B-3": "k2b's unused _zeta draw (k2b:324, 'stream order') is placed in the "
                "AUTHOR stream, preserving k2b's relative order among author draws; it "
                "is unused so it can affect only stream position, which is what "
                "'preserves the sequence' means",
    "RN-P3B-4": "loadings is drawn from the AUTHOR stream so an A/B pair shares its "
                "orthonormal basis bit-identically -- the trap P3 named; C2c proves it "
                "per probe pair",
    "RN-P3B-5": "the b-only truth is w_mu*trait + w_common*common and A/B share "
                "author_seed, so B's trait is bit-identical to A's and the refreshed "
                "truth is exactly 'A's persons carrying B's frame'; checked in C2a, not "
                "assumed",
    "RN-P3B-6": "R_deframe uses K-R1's transcription of K1b's ESTIMATED de-framing "
                "(mu_hat_field at k1b_literal/per_context, then deframe_panel) on A's "
                "panel scored against A's truth; its stride is measured and pinned in "
                "Part 0 before any measurement world, and it is descriptive and ungated",
    "RN-P3B-7": "NULL-first classification per #55 and P3's registration; the "
                "equivalence band and the V-P3c floor are computed from realized pilot "
                "noise (df-inflated) and written before the main arms",
    "RN-P3B-8": "R_nat, R_refresh and R_deframe at a world index share ONE corpus "
                "string, so P1's label noise cannot enter a within-world contrast; "
                "across phi the tag differs by necessity and the label note applies only "
                "to the distributional C1' anchor",
}

# ---------------------------------------------------------------------------
# ONE loader chain.

_MODS: dict[str, Any] = {}


def _load(name: str) -> Any:
    if name not in _MODS:
        spec = importlib.util.spec_from_file_location(
            name, ROOT / "scripts" / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
        sys.modules[name] = mod
        spec.loader.exec_module(mod)                         # type: ignore[union-attr]
        _MODS[name] = mod
    return _MODS[name]


def k2b() -> Any:
    return _load("run_suica_m4_k2b_t4_branch")


def k2c() -> Any:
    return _load("run_suica_m4_k2c_matched_pairs")


def kr1() -> Any:
    return _load("run_suica_m4_kr1_deframing_repair")


def v8() -> Any:
    return k2b().v8


# ---------------------------------------------------------------------------
# THE INSTRUMENT -- extracted from k2b:321-349 (RN-P3B-1).
#
# Provenance, line by line.  "stream" is the pinned channel taxonomy.
PROVENANCE = [
    ("321", "rng = np.random.default_rng(world_seed)",
     "rng_a = default_rng(author_seed); rng_f = default_rng(frame_seed)",
     "SPLIT", "the one edit that makes the instrument: one stream becomes two"),
    ("322", "loadings = _orthonormal_loadings(rng, DIM, k)",
     "loadings = _orthonormal_loadings(rng_a, DIM, k)", "author",
     "the shared basis; author-stream so an A/B pair shares it (RN-P3B-4)"),
    ("323", "z = rng.normal(size=(n, k))", "z = rng_a.normal(size=(n, k))", "author",
     "the b-draw"),
    ("324", "_zeta = rng.normal(size=(n, k))", "_zeta = rng_a.normal(size=(n, k))",
     "author", "unused in k2b and here; holds k2b's stream order (RN-P3B-3)"),
    ("325-326", "xs = np.empty(...); xs[:, 0] = rng.normal(size=(n, k))",
     "xs[:, 0] = rng_f.normal(size=(n, k))", "frame", "the state's initial condition"),
    ("327", "innovation_scale = math.sqrt(1.0 - phi_slow**2)", "unchanged", "derived",
     "phi enters here exactly as in k2b"),
    ("328-329", "xs[:, t] = phi*xs[:, t-1] + iscale*rng.normal(size=(n, k))",
     "... + iscale * rng_f.normal(size=(n, k))", "frame", "the AR recursion"),
    ("330", "noise = rng.normal(size=(n, t_max, DIM))",
     "noise = rng_f.normal(size=(n, t_max, DIM))", "frame",
     "pinned to the frame stream by the registration's taxonomy"),
    ("331", "trait = A_SCALE * ((z * G_PROFILE) @ loadings.T)", "unchanged", "author",
     "author draw through the shared basis"),
    ("332", "slow = A_SCALE * ((xs * G_PROFILE) @ loadings.T)", "unchanged", "frame",
     "frame state through the SHARED basis"),
    ("333-336", "common_lat = stack(f2().shock_vector(world_seed, c, o, k))",
     "... f2().shock_vector(frame_seed, c, o, k)", "frame",
     "keyed call site #2: the frame channel proper"),
    ("337", "common = A_SCALE * ((common_lat * G_PROFILE) @ loadings.T)", "unchanged",
     "frame", "frame content through the SHARED basis"),
    ("338-340", "a_rng = default_rng(v8.stable_bucket(str(world_seed), "
                "salt='m4k2b-loading'))",
     "... stable_bucket(str(author_seed), salt='m4k2b-loading')", "author",
     "keyed call site #3: the per-author interaction carrier"),
    ("341", "a_load = a_rng.normal(size=(n, k))", "unchanged", "author",
     "per-author-persistent"),
    ("342", "shocks = stack(k2a().shock_int_matrix(world_seed, o, k))",
     "... k2a().shock_int_matrix(frame_seed, o, k)", "frame",
     "keyed call site #4: per-occasion interaction shocks"),
    ("343", "u_int = einsum('ij,ojl->iol', a_load, shocks) / sqrt(k)", "unchanged",
     "mixed", "author carrier x frame shocks -- the interaction, correctly mixed"),
    ("344", "s_int = A_SCALE * ((u_int * G_PROFILE) @ loadings.T)", "unchanged", "mixed",
     "through the SHARED basis"),
    ("345-353", "return {trait, slow, int, common, noise, slow_latent, a_load}",
     "same keys PLUS 'loadings' (k2b does not return it; C2c needs it)", "return",
     "the one ADDITION: k2b withholds loadings, which is what made P3's channel "
     "surgery undetectable; exposing it here is what makes C2c possible"),
]


def build_split_world(author_seed: int, frame_seed: int,
                      phi_slow: float) -> dict[str, np.ndarray]:
    """k2b.build_k2b_world (k2b:321-349) with the author and frame streams split.

    Constants and helpers are imported from k2b, never copied (RN-P3B-1).
    """
    m = k2b()
    lay = m.layout()
    n = len(lay["author_ids"])
    t_max = int(lay["t_max"])
    k = m.K_LATENT

    rng_a = np.random.default_rng(author_seed)               # k2b:321 (author half)
    rng_f = np.random.default_rng(frame_seed)                # k2b:321 (frame half)

    loadings = m._orthonormal_loadings(rng_a, m.DIM, k)      # k2b:322
    z = rng_a.normal(size=(n, k))                            # k2b:323
    _zeta = rng_a.normal(size=(n, k))                        # k2b:324 (stream order)

    xs = np.empty((n, t_max, k), dtype=float)                # k2b:325
    xs[:, 0] = rng_f.normal(size=(n, k))                     # k2b:326
    innovation_scale = math.sqrt(1.0 - phi_slow ** 2)        # k2b:327
    for t in range(1, t_max):                                # k2b:328
        xs[:, t] = (phi_slow * xs[:, t - 1]
                    + innovation_scale * rng_f.normal(size=(n, k)))   # k2b:329
    noise = rng_f.normal(size=(n, t_max, m.DIM))             # k2b:330

    trait = m.A_SCALE * ((z * m.G_PROFILE) @ loadings.T)     # k2b:331
    slow = m.A_SCALE * ((xs * m.G_PROFILE) @ loadings.T)     # k2b:332
    common_lat = np.stack([                                  # k2b:333-336
        np.stack([m.f2().shock_vector(frame_seed, c, o, k) for o in range(t_max)])
        for c in lay["contexts_sorted"]
    ])
    common = m.A_SCALE * ((common_lat * m.G_PROFILE) @ loadings.T)    # k2b:337
    a_rng = np.random.default_rng(                           # k2b:338-340
        m.v8.stable_bucket(str(author_seed), salt="m4k2b-loading", modulus=2 ** 63 - 1)
    )
    a_load = a_rng.normal(size=(n, k))                       # k2b:341
    shocks = np.stack([m.k2a().shock_int_matrix(frame_seed, o, k)
                       for o in range(t_max)])               # k2b:342
    u_int = np.einsum("ij,ojl->iol", a_load, shocks) / math.sqrt(k)   # k2b:343
    s_int = m.A_SCALE * ((u_int * m.G_PROFILE) @ loadings.T)          # k2b:344
    return {                                                 # k2b:345-353
        "trait": trait,
        "slow": slow,
        "int": s_int,
        "common": common,
        "noise": m.SIGMA_ISO * noise,
        "slow_latent": xs,
        "a_load": a_load,
        "loadings": loadings,       # the one ADDITION (C2c needs it)
    }


# ---------------------------------------------------------------------------

def _log(event: str, **kw: Any) -> None:
    rec = {"utc": datetime.now(UTC).isoformat(), "event": event, **kw}
    with (OUT / "run_log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, default=float) + "\n")


def read_csv_rt(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, float_precision="round_trip")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=1, sort_keys=True, default=float) + "\n",
                    encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def r_of(share: float, phi: float) -> float:
    return k2c().predicted_attenuation(share, phi)


def seed_for(kind: str, phi: float, idx: int, salt: str) -> int:
    key = f"{LEG}|{salt}|{kind}|phi{phi!r}|i{idx}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def pair_seeds(phi: float, idx: int, salt_suffix: str = "") -> dict[str, int]:
    """A and B share the AUTHOR seed and differ in the FRAME seed."""
    a_salt = SALT_AUTHOR + salt_suffix
    fa_salt = SALT_FRAME_A + salt_suffix
    fb_salt = SALT_FRAME_B + salt_suffix
    return {"author": seed_for("author", phi, idx, a_salt),
            "frameA": seed_for("frameA", phi, idx, fa_salt),
            "frameB": seed_for("frameB", phi, idx, fb_salt)}


def _predicate(vals: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(vals)))
    sat = bool(np.any(np.abs(vals) >= SATURATION_ABS))
    nz = bool(float(np.std(vals, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated_abs_ge_0.995": sat,
            "nonzero_variance": nz, "min": float(vals.min()), "max": float(vals.max()),
            "PASS": bool(fin and (not sat) and nz)}


def score_pair(world_a: dict[str, np.ndarray], world_b: dict[str, np.ndarray],
               w: dict[str, float], arm_id: str, widx: int, phi: float,
               *, with_deframe: bool) -> dict[str, Any]:
    """ONE gauge pass on A, scored against A's truth and B's truth.

    R_deframe (secondary, descriptive) runs a SECOND gauge pass on the
    de-framed A panel, per K-R1's transcription of K1b's estimated repair.
    """
    m = k2b()
    lay = m.layout()
    module = lay["module"]
    corpus = f"m4k2b-{arm_id}-w{widx}"
    vectors = m.emit_panel(world_a, w)
    raw_m, raw_k = m.f1().featurize_panel(
        vectors, lay["author_ids"], corpus=corpus, spec=lay["spec"],
        directions=lay["directions"])
    panel = SimpleNamespace(metadata=lay["metadata"], raw={"M": raw_m, "K": raw_k})
    calibration = module.calibrate_d0_soft(panel)
    projected = module.project_soft(
        SimpleNamespace(raw={"M": raw_m, "K": raw_k}), lay["retained_mask"], calibration)
    field_est = module.deployed_soft_field(projected, lay["retained_ctx"],
                                           lay["resolved"])
    ridx = lay["retained_idx"]
    nat_full = m.emit_panel(world_a, w, active=("mu", "common"))
    ref_full = m.emit_panel(world_b, w, active=("mu", "common"))
    t_nat = [nat_full[i] for i in ridx]
    t_ref = [ref_full[i] for i in ridx]
    tnd = float(np.sqrt(sum(float(((a - b) ** 2).sum())
                            for a, b in zip(t_nat, t_ref))))
    f_nat = m.field_from_vectors(t_nat, calibration, corpus)
    f_ref = m.field_from_vectors(t_ref, calibration, corpus)
    out = {
        "R_nat": float(module.field_agreement(field_est, f_nat, lay["weights"])),
        "R_refresh": float(module.field_agreement(field_est, f_ref, lay["weights"])),
        "truth_norm_delta": tnd,
        "R_deframe": None,
    }
    if with_deframe:
        r = kr1()
        mu = r.mu_hat_field(world_a, w, int(world_a["_author_seed"]), phi,
                            donor_channels="k1b_literal", pool_scheme="per_context")
        dv = r.deframe_panel(vectors, mu)
        d_m, d_k = m.f1().featurize_panel(
            dv, lay["author_ids"], corpus=corpus, spec=lay["spec"],
            directions=lay["directions"])
        d_panel = SimpleNamespace(metadata=lay["metadata"], raw={"M": d_m, "K": d_k})
        d_cal = module.calibrate_d0_soft(d_panel)
        d_proj = module.project_soft(
            SimpleNamespace(raw={"M": d_m, "K": d_k}), lay["retained_mask"], d_cal)
        d_est = module.deployed_soft_field(d_proj, lay["retained_ctx"], lay["resolved"])
        d_truth = m.field_from_vectors(t_nat, d_cal, corpus)
        out["R_deframe"] = float(
            module.field_agreement(d_est, d_truth, lay["weights"]))
    return out


def run_pair(phi: float, idx: int, arm_id: str, salt_suffix: str = "",
             *, with_deframe: bool = False) -> dict[str, Any]:
    m = k2b()
    w = m.arm_weights(SHARE, W_INT_ARM)
    sd = pair_seeds(phi, idx, salt_suffix)
    wa = build_split_world(sd["author"], sd["frameA"], phi)
    wb = build_split_world(sd["author"], sd["frameB"], phi)
    wa["_author_seed"] = sd["author"]
    sc = score_pair(wa, wb, w, arm_id, idx, phi, with_deframe=with_deframe)
    return {"phi": phi, "share": SHARE, "pair": idx,
            "author_seed": sd["author"], "frameA_seed": sd["frameA"],
            "frameB_seed": sd["frameB"], **sc}


# ---------------------------------------------------------------------------
# PART 0 -- G0 anchors + provenance + the C2 battery.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    m = k2b()

    # --- G0(i): M1c's share-0.25 row (P3's verified anchor, reused) --------
    cm = read_csv_rt(M1CRES / "cell_means.csv")
    rowset = cm[cm["share"] == SHARE].sort_values("phi")
    m1c = [{"cell_tag": r["cell_tag"], "phi": float(r["phi"]),
            "r_pred": float(r["r_pred"]), "mean": float(r["field_mean"]),
            "sem": float(r["field_sem"]), "sd": float(r["field_sd"]),
            "n_worlds": int(r["n_worlds"])} for _, r in rowset.iterrows()]
    range_nat_m1c = float(m1c[0]["mean"] - m1c[-1]["mean"])
    g0i = {"source": rel(M1CRES / "cell_means.csv"), "rows": m1c,
           "range_nat_M1C": range_nat_m1c,
           "range_nat_M1C_matches_P3": bool(range_nat_m1c == -0.01039144307119933),
           "PASS": bool(len(m1c) == 5
                        and tuple(round(d["phi"], 10) for d in m1c) == PHI_LADDER)}

    # --- G0(ii): P2's headline (the projection truths) ---------------------
    p2 = read_json(P2RES / "decision.json")
    g0ii = {"source": rel(P2RES / "decision.json"), "verdict": p2["verdict_slug"],
            "f_B1": p2["per_cell"]["B1"]["f_fraction"],
            "f_B2": p2["per_cell"]["B2"]["f_fraction"],
            "one_minus_f_B1": float(1.0 - p2["per_cell"]["B1"]["f_fraction"]),
            "one_minus_f_B2": float(1.0 - p2["per_cell"]["B2"]["f_fraction"]),
            "PASS": bool(p2["verdict_slug"] == "GENUINE_SCAFFOLD")}

    # --- G0(iii): the ladder r values --------------------------------------
    ladder = []
    ok_r = True
    for phi in PHI_LADDER:
        got = r_of(SHARE, phi)
        want = next(d["r_pred"] for d in m1c if round(d["phi"], 10) == phi)
        ok_r &= bool(got == want)
        ladder.append({"phi": phi, "r_recomputed": got, "r_M1c": want,
                       "bit_exact": bool(got == want)})
    g0iii = {"ladder": ladder, "PASS": bool(ok_r)}

    # --- the extraction's provenance ---------------------------------------
    src = K2BSRC.read_text(encoding="utf-8").split("\n")
    prov = [{"k2b_lines": a, "k2b_source": b, "as_extracted": c, "stream": d,
             "note": e} for a, b, c, d, e in PROVENANCE]
    prov_summary = {
        "source_file": rel(K2BSRC), "source_span": "321-349",
        "n_mapped_entries": len(prov),
        "streams": {s: sum(1 for p in prov if p["stream"] == s)
                    for s in ("author", "frame", "mixed", "derived", "SPLIT",
                              "return")},
        "edits": ["rng -> rng_a / rng_f (k2b:321)",
                  "world_seed -> author_seed at k2b:338-340 (a_load)",
                  "world_seed -> frame_seed at k2b:333-336 (common) and "
                  "k2b:342 (shocks)",
                  "the return dict gains 'loadings' (k2b does not expose it)"],
        "n_edits": 4,
        "imported_not_copied": ["K_LATENT", "DIM", "G_PROFILE", "A_SCALE", "SIGMA_ISO",
                                "_orthonormal_loadings", "f2().shock_vector",
                                "k2a().shock_int_matrix", "v8.stable_bucket",
                                "layout", "emit_panel", "field_from_vectors"],
        "note": RN_NOTES["RN-P3B-1"],
    }

    # --- RN-P3B-2: the expected-different k2b comparison -------------------
    probe_phi = PHI_LADDER[0]
    kw = m.build_k2b_world(4242, probe_phi)
    sw = build_split_world(4242, 4242, probe_phi)
    same = {k: bool(np.array_equal(np.asarray(kw[k]).view(np.uint8),
                                   np.asarray(sw[k]).view(np.uint8)))
            for k in kw}
    seq_drawn = ("slow", "slow_latent", "noise")     # from the frame stream in order
    keyed_or_author = tuple(k for k in same if k not in seq_drawn)
    k2b_cmp = {
        "note": RN_NOTES["RN-P3B-2"], "identical_by_object": same,
        "identical_objects": sorted(k for k, v in same.items() if v),
        "differing_objects": sorted(k for k, v in same.items() if not v),
        "author_half_reproduces_k2b_bit_exactly": bool(
            all(same[k] for k in keyed_or_author)),
        "only_sequential_frame_draws_differ": bool(
            all(not same[k] for k in seq_drawn)),
        "reading": "at equal seeds the AUTHOR half reproduces k2b BIT-EXACTLY -- "
                   "loadings and z are the first draws of the author stream just as "
                   "they are k2b's first draws, so trait matches; a_load, common and "
                   "int are keyed on a seed rather than on stream position, so they "
                   "match too. The ONLY divergence is the three objects the frame "
                   "stream draws in sequence (slow, slow_latent, noise), which differ "
                   "because that stream restarts at the seed's first draw instead of "
                   "continuing after the author draws. This localises the divergence "
                   "to the stream restart itself -- it is a POSITIVE verification of "
                   "the transcription, not a caveat",
        "gates": False}

    # --- C2a: the split proof ----------------------------------------------
    c2a_rows = []
    for i in range(PROBE_PAIRS):
        sd = pair_seeds(probe_phi, i, "-probe")
        wa = build_split_world(sd["author"], sd["frameA"], probe_phi)
        wb = build_split_world(sd["author"], sd["frameB"], probe_phi)
        rec: dict[str, Any] = {"probe": i, "author_seed": sd["author"],
                               "frameA_seed": sd["frameA"],
                               "frameB_seed": sd["frameB"]}
        for k in AUTHOR_OBJECTS:
            rec[f"author::{k}::identical"] = bool(np.array_equal(
                np.asarray(wa[k]).view(np.uint8), np.asarray(wb[k]).view(np.uint8)))
        for k in FRAME_OBJECTS:
            d = float(np.linalg.norm(np.asarray(wa[k]) - np.asarray(wb[k])))
            rec[f"frame::{k}::norm_delta"] = d
            rec[f"frame::{k}::differs"] = bool(d > 0.0)
        c2a_rows.append(rec)
    c2a = {"n_probe_pairs": PROBE_PAIRS, "rows": c2a_rows,
           "all_author_identical": bool(all(
               r[f"author::{k}::identical"] for r in c2a_rows for k in AUTHOR_OBJECTS)),
           "all_frame_differ": bool(all(
               r[f"frame::{k}::differs"] for r in c2a_rows for k in FRAME_OBJECTS)),
           "norm_delta_min_by_object": {
               k: float(min(r[f"frame::{k}::norm_delta"] for r in c2a_rows))
               for k in FRAME_OBJECTS},
           "norm_delta_max_by_object": {
               k: float(max(r[f"frame::{k}::norm_delta"] for r in c2a_rows))
               for k in FRAME_OBJECTS}}
    c2a["PASS"] = bool(c2a["all_author_identical"] and c2a["all_frame_differ"])

    # --- C2b: determinism ---------------------------------------------------
    sd = pair_seeds(probe_phi, 0, "-probe")
    r1 = build_split_world(sd["author"], sd["frameA"], probe_phi)
    r2 = build_split_world(sd["author"], sd["frameA"], probe_phi)
    det = {k: bool(np.array_equal(np.asarray(r1[k]).view(np.uint8),
                                  np.asarray(r2[k]).view(np.uint8))) for k in r1}
    c2b = {"objects": det, "all_identical": bool(all(det.values()))}
    c2b["PASS"] = c2b["all_identical"]

    # --- C2c: the basis is shared ------------------------------------------
    c2c = {"n_pairs_checked": PROBE_PAIRS,
           "all_loadings_identical": bool(all(r["author::loadings::identical"]
                                              for r in c2a_rows)),
           "why": RN_NOTES["RN-P3B-4"]}
    c2c["PASS"] = c2c["all_loadings_identical"]

    # --- R_deframe cost, measured, and the stride pinned -------------------
    w = m.arm_weights(SHARE, W_INT_ARM)
    t_a = time.time()
    _ = run_pair(probe_phi, 0, "P3B-COST", "-probe", with_deframe=False)
    cost_plain = time.time() - t_a
    t_a = time.time()
    _ = run_pair(probe_phi, 0, "P3B-COST", "-probe", with_deframe=True)
    cost_deframe = time.time() - t_a
    budget_s = 260.0
    per_arm_plain = cost_plain * N_PAIRS
    extra = cost_deframe - cost_plain
    stride = 1
    while per_arm_plain + (extra * N_PAIRS / stride) > budget_s and stride < N_PAIRS:
        stride *= 2
    defr = {"cost_plain_seconds": cost_plain, "cost_with_deframe_seconds": cost_deframe,
            "extra_seconds": extra, "arm_budget_seconds": budget_s,
            "projected_arm_seconds_plain": per_arm_plain,
            "stride_pinned": int(stride),
            "n_deframe_per_arm": int(math.ceil(N_PAIRS / stride)),
            "projected_arm_seconds_at_stride":
                per_arm_plain + extra * math.ceil(N_PAIRS / stride),
            "machinery": "kr1.mu_hat_field(donor_channels='k1b_literal', "
                         "pool_scheme='per_context') then kr1.deframe_panel -- K-R1's "
                         "transcription of K1b's A4 into this world family",
            "gated": False, "note": RN_NOTES["RN-P3B-6"]}

    g0 = {"(i) M1c anchor row": g0i, "(ii) P2 headline": g0ii,
          "(iii) ladder r": g0iii,
          "PASS": bool(g0i["PASS"] and g0ii["PASS"] and g0iii["PASS"])}
    cert = {"C2a": c2a, "C2b": c2b, "C2c": c2c,
            "PASS": bool(c2a["PASS"] and c2b["PASS"] and c2c["PASS"])}

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md (M4-P3b, "
                        "BEFORE run, commit debc68e)",
        "master_seed": MASTER_SEED,
        "salts": {"author": SALT_AUTHOR, "frameA": SALT_FRAME_A,
                  "frameB": SALT_FRAME_B, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0": g0,
        "provenance": prov, "provenance_summary": prov_summary,
        "k2b_comparison_expected_different": k2b_cmp,
        "certification": cert, "deframe_cost": defr,
        "channel_taxonomy": {"author_stream": list(AUTHOR_OBJECTS),
                             "frame_stream": list(FRAME_OBJECTS),
                             "note": RN_NOTES["RN-P3B-5"]},
        "design": {"share": SHARE, "phi_ladder": list(PHI_LADDER),
                   "pairs_per_phi": N_PAIRS,
                   "total_worlds": 2 * N_PAIRS * len(PHI_LADDER)},
        "sides_rule22": {
            "L-1p3": {"clause": "MOSTLY_FRAME / INTERMEDIATE / "
                                "NO_TRANSPORTABLE_READING / other",
                      "prior": "0.55 / 0.20 / 0.15 / 0.10", "sided": "categorical"},
            "V-P3a / C1'": {"clause": f"R_nat's five levels within {ANCHOR_K}*SEM of "
                                      "M1c's row", "sided": "two-sided"},
            "V-P3b": {"clause": "g_ratio classification, NULL-first",
                      "sided": "categorical"},
            "G3": {"clause": f"g_ratio CI width <= {G_BUDGET} at truths "
                             f"{list(PROJ_TRUTHS)}", "sided": "one-sided"}},
        "stage_estimates_seconds": {"part0": 180, "pilot": 60, "project": 30,
                                    "arms_each": 260, "fit": 180, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", G0=g0["PASS"], cert=cert["PASS"], seconds=part0["seconds"])
    if not (g0["PASS"] and cert["PASS"]):
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "INSTRUMENT_DEFECT", "routing_cell": 1,
            "routing_text": "INSTRUMENT_DEFECT", "G0": g0, "certification": cert,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- G0/C2 failed, see part0.json")
    print(f"part0 OK  G0 PASS  C2a/C2b/C2c PASS  provenance {len(prov)} entries, "
          f"{prov_summary['n_edits']} edits  deframe stride={stride} "
          f"(plain {cost_plain:.2f}s, +{extra:.2f}s)  {time.time() - t0:.1f}s")
    _ = args, w


# ---------------------------------------------------------------------------
# C3 -- the sanity pilot and the bands.

def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0"]["PASS"]:
        raise SystemExit("STOP: G0 did not pass.")
    rows = []
    for phi in PILOT_PHI:
        for i in range(PILOT_PAIRS):
            rows.append(run_pair(phi, i, f"P3B-PILOT-p{phi}", "-pilot",
                                 with_deframe=True))
        print(f"  pilot phi={phi}: done ({time.time() - t0:.1f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)

    per, ok = [], True
    for phi, grp in df.groupby("phi"):
        cn = _predicate(grp["R_nat"].to_numpy(float))
        cr = _predicate(grp["R_refresh"].to_numpy(float))
        ok &= cn["PASS"] and cr["PASS"]
        per.append({"phi": float(phi), "n": int(len(grp)),
                    "R_nat_mean": float(grp["R_nat"].mean()),
                    "R_refresh_mean": float(grp["R_refresh"].mean()),
                    "R_deframe_mean": float(grp["R_deframe"].mean()),
                    "R_nat_regime": cn, "R_refresh_regime": cr,
                    "PASS": bool(cn["PASS"] and cr["PASS"])})

    # pooled within-phi sd, df-inflated, for both scorings
    def pooled(col: str) -> tuple[float, int, float, float]:
        ss, dfree = 0.0, 0
        for _, grp in df.groupby("phi"):
            v = grp[col].to_numpy(float)
            ss += float(np.sum((v - v.mean()) ** 2))
            dfree += len(v) - 1
        raw = float(np.sqrt(ss / dfree))
        infl = float(np.sqrt(dfree / float(chi2.ppf(CHI2_Q, dfree))))
        return raw, dfree, infl, raw * infl

    s_nat_raw, dfree, infl, s_nat = pooled("R_nat")
    s_ref_raw, _, _, s_ref = pooled("R_refresh")
    # V-P3b equivalence band and V-P3c floor, from realized noise (RN-P3B-7)
    se_range_ref = float(s_ref * math.sqrt(2.0 / N_PAIRS))
    se_level_ref = float(s_ref / math.sqrt(N_PAIRS))
    band = {
        "sigma_R_nat_raw": s_nat_raw, "sigma_R_nat_df_inflated": s_nat,
        "sigma_R_refresh_raw": s_ref_raw, "sigma_R_refresh_df_inflated": s_ref,
        "pooled_df": dfree, "inflation": infl, "chi2_quantile": CHI2_Q,
        "SE_range_ref_at_192": se_range_ref,
        "SE_level_ref_at_192": se_level_ref,
        "range_nat_M1C": p0["G0"]["(i) M1c anchor row"]["range_nat_M1C"],
        "V_P3b_equivalence_band_on_g_ratio": float(
            2.0 * se_range_ref
            / abs(p0["G0"]["(i) M1c anchor row"]["range_nat_M1C"])),
        "V_P3b_band_definition": "the g_ratio width corresponding to +/-2 SE of "
                                 "range_ref at 192 pairs, expressed as a fraction of "
                                 "M1c's realized natural range -- a NULL g_ratio is one "
                                 "whose CI lies inside this band",
        "V_P3c_floor_on_R_refresh_levels": float(2.0 * se_level_ref),
        "V_P3c_definition": "R_refresh is 'within the noise floor of zero' at a phi if "
                            "|mean| <= 2 * SE_level at that phi; the sub-case fires "
                            "only if this holds at EVERY phi",
        "note": RN_NOTES["RN-P3B-7"],
    }

    out = {"utc": datetime.now(UTC).isoformat(), "C3": {"per_phi": per, "PASS": bool(ok)},
           "bands": band, "n_pilot_pairs": int(len(df)),
           "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done", PASS=ok, seconds=out["seconds"])
    if not ok:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "INSTRUMENT_DEFECT", "routing_cell": 1,
            "routing_text": "INSTRUMENT_DEFECT", "C3": out["C3"],
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: INSTRUMENT_DEFECT -- C3 predicate failed")
    print(f"pilot OK  C3 PASS  sigma_nat={s_nat!r} sigma_ref={s_ref!r}  "
          f"equiv band={band['V_P3b_equivalence_band_on_g_ratio']!r}  "
          f"floor={band['V_P3c_floor_on_R_refresh_levels']!r}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# G3 -- the projection on g_ratio's CI width.

def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    b = pil["bands"]
    s_nat = b["sigma_R_nat_df_inflated"]
    s_ref = b["sigma_R_refresh_df_inflated"]
    rn = abs(b["range_nat_M1C"])

    def project(n: int) -> dict[str, Any]:
        se_rn = s_nat * math.sqrt(2.0 / n)
        se_rr = s_ref * math.sqrt(2.0 / n)
        rng = np.random.default_rng(MASTER_SEED)
        out = {}
        for g in PROJ_TRUTHS:
            num = rng.normal(g * rn, se_rr, size=B_PROJ)
            den = rng.normal(rn, se_rn, size=B_PROJ)
            with np.errstate(divide="ignore", invalid="ignore"):
                ratio = num / den
            lo, hi = (float(np.nanquantile(ratio, 0.025)),
                      float(np.nanquantile(ratio, 0.975)))
            out[str(g)] = {"truth_g": g, "SE_range_nat": float(se_rn),
                           "SE_range_ref": float(se_rr),
                           "ci95": [lo, hi], "width": float(hi - lo),
                           "within_budget": bool(hi - lo <= G_BUDGET)}
        return {"pairs_per_phi": n, "per_truth": out,
                "PASS": bool(all(d["within_budget"] for d in out.values()))}

    base = project(N_PAIRS)
    esc = None
    decided = N_PAIRS
    if not base["PASS"]:
        print(f"  G3 FAILED at n={N_PAIRS}; once-only escalation to "
              f"n={N_PAIRS_ESCALATED} (on the BUDGET gate)", flush=True)
        esc = project(N_PAIRS_ESCALATED)
        if esc["PASS"]:
            decided = N_PAIRS_ESCALATED
    # --- how many pairs WOULD suffice?  (diagnostic, from pilot noise only) ---
    need = {}
    for g in PROJ_TRUTHS:
        n_try = N_PAIRS
        found = None
        while n_try <= 2 ** 22:
            if project(n_try)["per_truth"][str(g)]["within_budget"]:
                found = n_try
                break
            n_try *= 2
        need[str(g)] = {"truth_g": g, "smallest_power_of_two_pairs": found,
                        "multiple_of_registered_192": (None if found is None
                                                       else found / N_PAIRS)}
    why = {
        "structure": "g_ratio = range_ref / range_nat is a ratio whose DENOMINATOR is "
                     "the natural gradient itself",
        "range_nat_M1C": rn,
        "sigma_R_nat_df_inflated": s_nat,
        "SE_range_nat_at_192": float(s_nat * math.sqrt(2.0 / N_PAIRS)),
        "range_nat_in_SE_at_192": float(rn / (s_nat * math.sqrt(2.0 / N_PAIRS))),
        "reading": "the natural gradient this leg must divide by is roughly the size of "
                   "a few standard errors at the registered design, so the ratio's "
                   "sampling distribution is wide however precisely the numerator is "
                   "measured; the equivalence band computed from the same noise is "
                   f"{pil['bands']['V_P3b_equivalence_band_on_g_ratio']!r}, i.e. nearly "
                   "the whole interesting range, which is the same fact seen from the "
                   "other side",
        "pairs_needed": need,
    }
    # A named alternative estimand, computed so the handback is actionable.
    # Naming is not choosing: this leg's estimand is the registered ratio.
    alt = {}
    for n_ in (N_PAIRS, N_PAIRS_ESCALATED):
        se_rr = float(s_ref * math.sqrt(2.0 / n_))
        alt[str(n_)] = {
            "pairs_per_phi": n_,
            "SE_range_ref": se_rr,
            "half_width_2SE": float(2.0 * se_rr),
            "range_ref_if_equal_to_range_nat_in_SE": float(rn / se_rr),
            "detects_range_ref_eq_0_vs_range_nat_at_2SE": bool(rn / se_rr >= 2.0),
        }
    why["named_alternative_estimand"] = {
        "quantity": "range_ref itself (or the DIFFERENCE range_nat - range_ref) "
                    "instead of their RATIO",
        "why_it_helps": "a difference does not divide by a small, noisy denominator; "
                        "all of the ratio's width comes from range_nat sitting at "
                        f"{rn / (s_nat * math.sqrt(2.0 / N_PAIRS)):.2f} SE",
        "power": alt,
        "status": "NAMED FOR THE PLANNER, NOT CHOSEN -- this leg's estimand is the "
                  "registered ratio and the executor does not substitute estimands",
    }
    g3 = {"budget": G_BUDGET, "truths": list(PROJ_TRUTHS),
          "why_it_fails": why,
          "range_nat_used": rn, "sigma_R_nat": s_nat, "sigma_R_refresh": s_ref,
          "base": base, "escalated": esc, "escalation_fired": bool(esc is not None),
          "pairs_per_phi_decided": decided,
          "PASS": bool(base["PASS"] or (esc is not None and esc["PASS"])),
          "on_fail": "NON_PROJECTABLE",
          "note": "g_ratio is a ratio of two noisy ranges; the projection draws both "
                  "and takes the ratio, so the width carries the denominator's noise",
          "seconds": time.time() - t0}
    write_json(OUT / "projection.json", g3)
    _log("project_done", PASS=g3["PASS"], seconds=g3["seconds"])
    if not g3["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "NON_PROJECTABLE", "routing_cell": 2,
            "routing_text": "NON_PROJECTABLE", "G3": g3,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"g={k}: width={d['width']!r}" for k, d in base["per_truth"].items())
        + f"  n={decided}  {time.time() - t0:.1f}s")
    _ = args, p0


# ---------------------------------------------------------------------------
# THE ARMS.

def _arm(phi: float) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: the projection did not pass.")
    n = int(g3["pairs_per_phi_decided"])
    stride = int(p0["deframe_cost"]["stride_pinned"])
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    path = OUT / "arms" / f"arm_phi{phi}.csv"
    if path.exists() and len(read_csv_rt(path)) == n:
        print(f"  phi={phi}: already complete, skipped", flush=True)
    else:
        rows = [run_pair(phi, i, f"P3B-p{phi}", "",
                         with_deframe=bool(i % stride == 0)) for i in range(n)]
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"  phi={phi}: n={len(rows)} ({time.time() - t0:.1f}s)", flush=True)
    _log(f"arm_phi{phi}_done", seconds=time.time() - t0)
    print(f"arm phi={phi} OK  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------
# THE FIT.

def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    n = int(g3["pairs_per_phi_decided"])
    band = pil["bands"]

    nat: dict[float, np.ndarray] = {}
    ref: dict[float, np.ndarray] = {}
    per_phi = []
    for phi in PHI_LADDER:
        d = read_csv_rt(OUT / "arms" / f"arm_phi{phi}.csv").sort_values("pair")
        if len(d) != n:
            raise SystemExit(f"REFUSED: phi={phi} has {len(d)}, expected {n}")
        a = d["R_nat"].to_numpy(float)
        b = d["R_refresh"].to_numpy(float)
        for nm, v in (("R_nat", a), ("R_refresh", b)):
            chk = _predicate(v)
            if not chk["PASS"]:
                raise SystemExit(f"REFUSED: rule-29 fails on {nm} at phi={phi}")
        nat[phi] = a
        ref[phi] = b
        dfr = d["R_deframe"].dropna().to_numpy(float)
        per_phi.append({
            "phi": phi, "r_pred": r_of(SHARE, phi), "n": int(len(a)),
            "R_nat_mean": float(a.mean()),
            "R_nat_sem": float(np.std(a, ddof=1) / np.sqrt(len(a))),
            "R_refresh_mean": float(b.mean()),
            "R_refresh_sem": float(np.std(b, ddof=1) / np.sqrt(len(b))),
            "R_deframe_mean": (float(dfr.mean()) if len(dfr) else None),
            "R_deframe_sem": (float(np.std(dfr, ddof=1) / np.sqrt(len(dfr)))
                              if len(dfr) > 1 else None),
            "R_deframe_n": int(len(dfr)),
            "truth_norm_delta_mean": float(d["truth_norm_delta"].mean())})

    # --- C1' / V-P3a: the anchor as certificate ----------------------------
    m1c = {round(d["phi"], 10): d for d in p0["G0"]["(i) M1c anchor row"]["rows"]}
    anchor = []
    anchor_ok = True
    for q in per_phi:
        ref_row = m1c[round(q["phi"], 10)]
        diff = float(q["R_nat_mean"] - ref_row["mean"])
        pooled_sem = float(math.sqrt(q["R_nat_sem"] ** 2 + ref_row["sem"] ** 2))
        tol = float(ANCHOR_K * ref_row["sem"])
        inside = bool(abs(diff) <= tol)
        anchor_ok &= inside
        anchor.append({"phi": q["phi"], "P3b_R_nat": q["R_nat_mean"],
                       "P3b_sem": q["R_nat_sem"], "M1c_mean": ref_row["mean"],
                       "M1c_sem": ref_row["sem"], "difference": diff,
                       "tolerance_2sqrt2_SEM": tol, "inside": inside,
                       "z_pooled": float(diff / pooled_sem)})
    c1 = {"rule": f"|P3b R_nat - M1c mean| <= {ANCHOR_K} * M1c SEM per level",
          "rows": anchor, "all_inside": bool(anchor_ok),
          "n_inside": int(sum(1 for a in anchor if a["inside"])),
          "consequence_on_fail": "INSTRUMENT_DEFECT (a stop about the extraction, never "
                                 "a finding about the world)",
          "PASS": bool(anchor_ok)}

    # --- the gradient objects ----------------------------------------------
    lo_phi, hi_phi = PHI_LADDER[0], PHI_LADDER[-1]
    range_nat = float(nat[lo_phi].mean() - nat[hi_phi].mean())
    range_ref = float(ref[lo_phi].mean() - ref[hi_phi].mean())
    g_ratio = float(range_ref / range_nat)

    rng = np.random.default_rng(MASTER_SEED)
    bidx = {phi: rng.integers(0, n, size=(B_BOOT_HIGH, n)) for phi in PHI_LADDER}

    def boot(B: int) -> dict[str, np.ndarray]:
        rn_ = np.empty(B, float)
        rr_ = np.empty(B, float)
        gr_ = np.empty(B, float)
        for j in range(B):
            a_lo = nat[lo_phi][bidx[lo_phi][j]].mean()
            a_hi = nat[hi_phi][bidx[hi_phi][j]].mean()
            b_lo = ref[lo_phi][bidx[lo_phi][j]].mean()
            b_hi = ref[hi_phi][bidx[hi_phi][j]].mean()
            rn_[j] = a_lo - a_hi
            rr_[j] = b_lo - b_hi
            gr_[j] = rr_[j] / rn_[j] if rn_[j] != 0.0 else np.nan
        return {"range_nat": rn_, "range_ref": rr_, "g": gr_}

    bb = boot(B_BOOT)
    g_lo, g_hi = (float(np.nanquantile(bb["g"], 0.025)),
                  float(np.nanquantile(bb["g"], 0.975)))
    g_width = float(g_hi - g_lo)

    # --- V-P3c: is R_refresh within the noise floor of zero at every phi? ---
    floor = band["V_P3c_floor_on_R_refresh_levels"]
    floor_rows = [{"phi": q["phi"], "R_refresh_mean": q["R_refresh_mean"],
                   "abs_mean": abs(q["R_refresh_mean"]), "floor": floor,
                   "within_floor": bool(abs(q["R_refresh_mean"]) <= floor)}
                  for q in per_phi]
    v_p3c = {"floor": floor, "rows": floor_rows,
             "fires": bool(all(r["within_floor"] for r in floor_rows)),
             "definition": band["V_P3c_definition"]}

    # --- V-P3b: NULL-first classification -----------------------------------
    eq = band["V_P3b_equivalence_band_on_g_ratio"]
    within_budget = bool(g_width <= G_BUDGET)
    if not within_budget:
        cls = "UNDERPOWERED"
    elif g_lo >= -eq and g_hi <= eq:
        cls = "NO_TRANSPORTABLE_GRADIENT"
    elif g_hi < 0.25:
        cls = "MOSTLY_FRAME"
    elif g_lo > 0.5:
        cls = "SUBSTANTIALLY_GENUINE"
    else:
        cls = "INTERMEDIATE"
    # rule 13: is any classification boundary within 1/(10B) of a CI tail?
    margin = 1.0 / (RULE13_FACTOR * B_BOOT)
    near = []
    for nm, bnd in (("equiv-", -eq), ("equiv+", eq), ("0.25", 0.25), ("0.5", 0.5)):
        frac = float(np.mean(bb["g"] <= bnd))
        if min(abs(frac - 0.025), abs(frac - 0.975)) < margin:
            near.append({"boundary": nm, "tail_frac": frac})
    rule13 = []
    if near:
        bb = boot(B_BOOT_HIGH)
        g_lo, g_hi = (float(np.nanquantile(bb["g"], 0.025)),
                      float(np.nanquantile(bb["g"], 0.975)))
        g_width = float(g_hi - g_lo)
        rule13.append({"triggers": near, "B": B_BOOT_HIGH, "ci_after": [g_lo, g_hi]})

    out = {
        "utc": datetime.now(UTC).isoformat(), "pairs_per_phi": n,
        "per_phi": per_phi, "C1_prime": c1,
        "range_nat": range_nat, "range_ref": range_ref,
        "range_nat_ci95": [float(np.quantile(bb["range_nat"], 0.025)),
                           float(np.quantile(bb["range_nat"], 0.975))],
        "range_ref_ci95": [float(np.quantile(bb["range_ref"], 0.025)),
                           float(np.quantile(bb["range_ref"], 0.975))],
        "g_ratio": g_ratio, "g_ratio_ci95": [g_lo, g_hi], "g_ratio_width": g_width,
        "g_budget": G_BUDGET, "within_budget": within_budget,
        "equivalence_band": eq, "classification": cls,
        "V_P3c": v_p3c, "rule13_events": rule13, "B": int(len(bb["g"])),
        "M1c_range_nat": band["range_nat_M1C"],
        "range_nat_vs_M1C": float(range_nat - band["range_nat_M1C"]),
        "seconds": time.time() - t0,
    }
    write_json(OUT / "fit.json", out)
    _log("fit_done", classification=cls, g=g_ratio, seconds=out["seconds"])
    print(f"fit OK  C1'={'PASS' if c1['PASS'] else 'FAIL'} ({c1['n_inside']}/5)  "
          f"range_nat={range_nat!r} range_ref={range_ref!r}  "
          f"g={g_ratio!r} [{g_lo!r}, {g_hi!r}] w={g_width!r}  {cls}  "
          f"V-P3c fires={v_p3c['fires']}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "G0/C2/C3 failure, or C1' anchor fails",
     "outcome": "INSTRUMENT_DEFECT",
     "text": "INSTRUMENT_DEFECT -- a stop about the extraction, never a finding about "
             "the world"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE"},
    {"n": "3", "condition": "V-P3c fires", "outcome": "NO_TRANSPORTABLE_READING",
     "text": "NO_TRANSPORTABLE_READING -- the natural gradient carries no "
             "frame-refreshed person signal at all; V-P3b N/A"},
    {"n": "4", "condition": "g_ratio MOSTLY_FRAME or NO_TRANSPORTABLE_GRADIENT",
     "outcome": "NATURAL_GRADIENT_MOSTLY_FRAME",
     "text": "NATURAL_GRADIENT_MOSTLY_FRAME -- the M-line law's r-channel is dominated "
             "by frame-agreement; the law stands as a law of the statistic; the "
             "theory's mechanism section re-types"},
    {"n": "5", "condition": "g_ratio INTERMEDIATE", "outcome": "MIXED_GRADIENT",
     "text": "MIXED_GRADIENT -- quantified split; theory carries the number"},
    {"n": "6", "condition": "g_ratio SUBSTANTIALLY_GENUINE",
     "outcome": "GENUINE_GRADIENT",
     "text": "GENUINE_GRADIENT -- the r-channel transports across frames; the "
             "scaffold-gradient reading strengthens"},
    {"n": "7", "condition": "budget unmet", "outcome": "UNDERPOWERED",
     "text": "UNDERPOWERED (+ UNQUANTIFIED modifier; levels reported)"},
]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        _finalize_nonprojectable(t0, p0, pil, g3)
        return
    fit = read_json(OUT / "fit.json")

    mods: list[str] = []
    if not fit["C1_prime"]["PASS"]:
        slug = "INSTRUMENT_DEFECT"
    elif fit["V_P3c"]["fires"]:
        slug = "NO_TRANSPORTABLE_READING"
    elif fit["classification"] == "UNDERPOWERED":
        slug = "UNDERPOWERED"
        mods.append("UNQUANTIFIED")
    elif fit["classification"] in ("MOSTLY_FRAME", "NO_TRANSPORTABLE_GRADIENT"):
        slug = "NATURAL_GRADIENT_MOSTLY_FRAME"
    elif fit["classification"] == "INTERMEDIATE":
        slug = "MIXED_GRADIENT"
    else:
        slug = "GENUINE_GRADIENT"
    cell_n = next(t["n"] for t in TRUTH_TABLE if t["outcome"] == slug)

    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": mods,
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "classification": fit["classification"],
        "g_ratio": fit["g_ratio"], "g_ratio_ci95": fit["g_ratio_ci95"],
        "g_ratio_width": fit["g_ratio_width"], "within_budget": fit["within_budget"],
        "range_nat": fit["range_nat"], "range_ref": fit["range_ref"],
        "equivalence_band": fit["equivalence_band"],
        "C1_prime": fit["C1_prime"], "V_P3c": fit["V_P3c"],
        "per_phi": fit["per_phi"], "pairs_per_phi": fit["pairs_per_phi"],
        "total_worlds": int(2 * fit["pairs_per_phi"] * len(PHI_LADDER)),
        "provenance_summary": p0["provenance_summary"],
        "certification": p0["certification"],
        "bands": pil["bands"], "projection": g3,
        "rule13_events": fit["rule13_events"],
        "gates": {
            "G0": {"PASS": p0["G0"]["PASS"],
                   "detail": "M1c's share-0.25 row, P2's headline and the five ladder r "
                             "values verified bit-exact"},
            "C2a": {"PASS": p0["certification"]["C2a"]["PASS"],
                    "detail": f"{PROBE_PAIRS} probe pairs: author objects "
                              "bit-identical, every frame object differs"},
            "C2b": {"PASS": p0["certification"]["C2b"]["PASS"],
                    "detail": "same (author_seed, frame_seed, phi) rebuilt bit-identical"},
            "C2c": {"PASS": p0["certification"]["C2c"]["PASS"],
                    "detail": "loadings bit-identical across every pair -- no basis "
                              "mixing"},
            "C3": {"PASS": pil["C3"]["PASS"],
                   "detail": "rule-29 predicate on BOTH scorings at both pilot phi; "
                             "bands computed df-inflated and written before the arms"},
            "C1'": {"PASS": fit["C1_prime"]["PASS"],
                    "detail": f"{fit['C1_prime']['n_inside']}/5 levels within "
                              f"{ANCHOR_K}*SEM of M1c's row"},
            "G3": {"PASS": g3["PASS"],
                   "detail": f"g_ratio CI width at truths {list(PROJ_TRUTHS)}; "
                             f"escalation fired: {g3['escalation_fired']}"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, pil, g3, fit, dec)
    _facts(p0, pil, g3, fit, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  modifiers={mods or 'none'}  "
          f"classification={fit['classification']}")
    _ = args


def _finalize_nonprojectable(t0: float, p0: dict[str, Any], pil: dict[str, Any],
                             g3: dict[str, Any]) -> None:
    """Routing cell 2: the rule-25 gate fired BEFORE any measurement world."""
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": "NON_PROJECTABLE", "routing_cell": "2", "modifiers": [],
        "routing_text": next(t["text"] for t in TRUTH_TABLE
                             if t["outcome"] == "NON_PROJECTABLE"),
        "stopped_at": "G3 (rule 25), after the registered once-only escalation",
        "worlds_drawn_for_measurement": 0,
        "instrument_certified": True,
        "provenance_summary": p0["provenance_summary"],
        "certification": p0["certification"],
        "k2b_comparison": p0["k2b_comparison_expected_different"],
        "bands": pil["bands"], "C3": pil["C3"], "projection": g3,
        "gates": {
            "G0": {"PASS": p0["G0"]["PASS"],
                   "detail": "M1c's share-0.25 row, P2's headline and the five ladder r "
                             "values verified bit-exact"},
            "C2a": {"PASS": p0["certification"]["C2a"]["PASS"],
                    "detail": f"{PROBE_PAIRS} probe pairs: author objects "
                              "bit-identical, every frame object differs"},
            "C2b": {"PASS": p0["certification"]["C2b"]["PASS"],
                    "detail": "same (author_seed, frame_seed, phi) rebuilt bit-identical"},
            "C2c": {"PASS": p0["certification"]["C2c"]["PASS"],
                    "detail": "loadings bit-identical across every pair -- no basis "
                              "mixing"},
            "C3": {"PASS": pil["C3"]["PASS"],
                   "detail": "rule-29 predicate on BOTH scorings; bands computed "
                             "df-inflated and written before any arm"},
            "C1'": {"PASS": None,
                    "detail": "not reached -- the rule-25 gate fires before the "
                              "measurement arms"},
            "G3": {"PASS": False,
                   "detail": f"g_ratio CI width {g3['base']['per_truth']['0.04']['width']!r}"
                             f" / {g3['base']['per_truth']['0.5']['width']!r} at 192 and "
                             f"{g3['escalated']['per_truth']['0.04']['width']!r} / "
                             f"{g3['escalated']['per_truth']['0.5']['width']!r} at 384, "
                             f"against a {G_BUDGET} budget"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug="NON_PROJECTABLE", seconds=dec["seconds"])
    _tables_np(p0, pil, g3, dec)
    _facts_np(p0, pil, g3, dec)
    print("finalize OK  slug=NON_PROJECTABLE  cell=2  measurement worlds=0  "
          "instrument CERTIFIED")


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
    sec["provenance"] = _md(
        ["k2b lines", "k2b source", "as extracted", "stream", "note"],
        [[p["k2b_lines"], "`" + p["k2b_source"] + "`", "`" + p["as_extracted"] + "`",
          p["stream"], p["note"]] for p in p0["provenance"]])
    ps = p0["provenance_summary"]
    sec["provsummary"] = _md(
        ["property", "value"],
        [["source", "`" + ps["source_file"] + ":" + ps["source_span"] + "`"],
         ["mapped entries", str(ps["n_mapped_entries"])],
         ["stream split", repr(ps["streams"])],
         ["**total edits**", "**" + str(ps["n_edits"]) + "**"],
         *[[f"edit {i + 1}", e] for i, e in enumerate(ps["edits"])],
         ["imported, never copied", ", ".join(ps["imported_not_copied"])]])
    kc = p0["k2b_comparison_expected_different"]
    sec["k2bcmp"] = _md(
        ["object", "split-world == k2b at equal seeds"],
        [[k, str(v)] for k, v in kc["identical_by_object"].items()]
        + [["**identical**", ", ".join(kc["identical_objects"])],
           ["**differing**", ", ".join(kc["differing_objects"])],
           ["author half reproduces k2b bit-exactly",
            str(kc["author_half_reproduces_k2b_bit_exactly"])],
           ["only the sequential frame draws differ",
            str(kc["only_sequential_frame_draws_differ"])],
           ["reading", kc["reading"]],
           ["gates the leg", str(kc["gates"])]])
    c2a = p0["certification"]["C2a"]
    sec["c2a"] = _md(
        ["object", "stream", "result across the " + str(c2a["n_probe_pairs"])
         + " probe pairs"],
        [[k, "author", "bit-identical on every pair: "
          + str(all(r[f"author::{k}::identical"] for r in c2a["rows"]))]
         for k in AUTHOR_OBJECTS]
        + [[k, "frame", f"differs on every pair; norm delta in "
            f"[{c2a['norm_delta_min_by_object'][k]!r}, "
            f"{c2a['norm_delta_max_by_object'][k]!r}]"] for k in FRAME_OBJECTS]
        + [["**C2a**", "—", "**PASS = " + str(c2a["PASS"]) + "**"]])
    c2b = p0["certification"]["C2b"]
    c2c = p0["certification"]["C2c"]
    sec["c2bc"] = _md(
        ["check", "detail", "PASS"],
        [["C2b determinism", "same (author_seed, frame_seed, phi) rebuilt; "
          + str(len(c2b["objects"])) + " objects compared", str(c2b["PASS"])],
         ["C2c shared basis", "loadings bit-identical across all "
          + str(c2c["n_pairs_checked"]) + " pairs", str(c2c["PASS"])]])
    dfc = p0["deframe_cost"]
    sec["deframe"] = _md(
        ["quantity", "value"],
        [["machinery", dfc["machinery"]],
         ["cost per pair, plain", repr(dfc["cost_plain_seconds"])],
         ["cost per pair, with de-framing", repr(dfc["cost_with_deframe_seconds"])],
         ["extra per pair", repr(dfc["extra_seconds"])],
         ["arm budget", repr(dfc["arm_budget_seconds"])],
         ["**stride pinned in Part 0**", "**" + str(dfc["stride_pinned"]) + "**"],
         ["de-framed pairs per arm", str(dfc["n_deframe_per_arm"])],
         ["gated", str(dfc["gated"])]])
    b = pil["bands"]
    sec["bands"] = _md(
        ["quantity", "value"],
        [["sigma R_nat (raw)", repr(b["sigma_R_nat_raw"])],
         ["sigma R_nat (df-inflated)", repr(b["sigma_R_nat_df_inflated"])],
         ["sigma R_refresh (raw)", repr(b["sigma_R_refresh_raw"])],
         ["sigma R_refresh (df-inflated)", repr(b["sigma_R_refresh_df_inflated"])],
         ["pooled df", str(b["pooled_df"])],
         ["inflation factor", repr(b["inflation"])],
         ["SE(range_ref) at 192 pairs", repr(b["SE_range_ref_at_192"])],
         ["M1c realized natural range", repr(b["range_nat_M1C"])],
         ["**V-P3b equivalence band on g_ratio**",
          "**" + repr(b["V_P3b_equivalence_band_on_g_ratio"]) + "**"],
         ["band definition", b["V_P3b_band_definition"]],
         ["**V-P3c floor on R_refresh levels**",
          "**" + repr(b["V_P3c_floor_on_R_refresh_levels"]) + "**"],
         ["floor definition", b["V_P3c_definition"]]])
    sec["projection"] = _md(
        ["truth g", "SE(range_nat)", "SE(range_ref)", "projected g_ratio 95% CI",
         "width", "budget", "within"],
        [[k, repr(d["SE_range_nat"]), repr(d["SE_range_ref"]), repr(d["ci95"]),
          repr(d["width"]), repr(G_BUDGET), str(d["within_budget"])]
         for k, d in g3["base"]["per_truth"].items()]
        + [["escalation fired", str(g3["escalation_fired"]), "—", "—", "—", "—",
            "pairs/phi decided: " + str(g3["pairs_per_phi_decided"])]])
    sec["dual"] = _md(
        ["phi", "r_pred", "n", "R_nat mean", "R_nat SEM", "R_refresh mean",
         "R_refresh SEM", "R_deframe mean", "R_deframe SEM", "R_deframe n",
         "||T-nat - T-ref|| mean"],
        [[repr(q["phi"]), repr(q["r_pred"]), str(q["n"]), repr(q["R_nat_mean"]),
          repr(q["R_nat_sem"]), repr(q["R_refresh_mean"]), repr(q["R_refresh_sem"]),
          repr(q["R_deframe_mean"]), repr(q["R_deframe_sem"]), str(q["R_deframe_n"]),
          repr(q["truth_norm_delta_mean"])] for q in fit["per_phi"]])
    sec["anchor"] = _md(
        ["phi", "P3b R_nat", "P3b SEM", "M1c mean", "M1c SEM", "difference",
         "tolerance 2*sqrt(2)*SEM", "inside", "pooled z"],
        [[repr(a["phi"]), repr(a["P3b_R_nat"]), repr(a["P3b_sem"]),
          repr(a["M1c_mean"]), repr(a["M1c_sem"]), repr(a["difference"]),
          repr(a["tolerance_2sqrt2_SEM"]), str(a["inside"]), repr(a["z_pooled"])]
         for a in fit["C1_prime"]["rows"]]
        + [["**C1'**", "—", "—", "—", "—", "—", "—",
            "**" + str(fit["C1_prime"]["n_inside"]) + "/5**",
            "PASS = " + str(fit["C1_prime"]["PASS"])]])
    sec["gradient"] = _md(
        ["quantity", "value", "95% CI"],
        [["range_nat = R_nat(.05) - R_nat(.98)", repr(fit["range_nat"]),
          repr(fit["range_nat_ci95"])],
         ["range_ref = R_refresh(.05) - R_refresh(.98)", repr(fit["range_ref"]),
          repr(fit["range_ref_ci95"])],
         ["M1c's realized natural range", repr(fit["M1c_range_nat"]), "—"],
         ["P3b range_nat minus M1c's", repr(fit["range_nat_vs_M1C"]), "—"],
         ["**g_ratio = range_ref / range_nat**", "**" + repr(fit["g_ratio"]) + "**",
          repr(fit["g_ratio_ci95"])],
         ["g_ratio CI width", repr(fit["g_ratio_width"]),
          "budget " + repr(fit["g_budget"]) + ", within: "
          + str(fit["within_budget"])],
         ["equivalence band (NULL tested first)", repr(fit["equivalence_band"]), "—"],
         ["**classification**", "**" + fit["classification"] + "**", "—"],
         ["bootstrap B", str(fit["B"]), "—"]])
    sec["floor"] = _md(
        ["phi", "R_refresh mean", "|mean|", "floor", "within floor"],
        [[repr(r["phi"]), repr(r["R_refresh_mean"]), repr(r["abs_mean"]),
          repr(r["floor"]), str(r["within_floor"])] for r in fit["V_P3c"]["rows"]]
        + [["**V-P3c fires (all phi within floor)**", "—", "—", "—",
            "**" + str(fit["V_P3c"]["fires"]) + "**"]])
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
    for phi in PHI_LADDER:
        trows.append([f"arm phi={phi}", str(est["arms_each"]),
                      "%.3f" % meas.get(f"arm_phi{phi}_done", float("nan"))])
    trows += [["fit", str(est["fit"]), "%.3f" % meas.get("fit_done", float("nan"))],
              ["finalize", str(est["finalize"]),
               "%.3f" % meas.get("finalize_done", float("nan"))]]
    sec["timing"] = _md(["stage", "estimate (s)", "measured (s)"], trows)
    body = ["# M4-P3b report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _tables_np(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
               dec: dict[str, Any]) -> None:
    """Tables for the NON_PROJECTABLE path (no measurement arms exist)."""
    sec: dict[str, list[str]] = {}
    sec["provenance"] = _md(
        ["k2b lines", "k2b source", "as extracted", "stream", "note"],
        [[q["k2b_lines"], "`" + q["k2b_source"] + "`", "`" + q["as_extracted"] + "`",
          q["stream"], q["note"]] for q in p0["provenance"]])
    ps = p0["provenance_summary"]
    sec["provsummary"] = _md(
        ["property", "value"],
        [["source", "`" + ps["source_file"] + ":" + ps["source_span"] + "`"],
         ["mapped entries", str(ps["n_mapped_entries"])],
         ["stream split", repr(ps["streams"])],
         ["**total edits**", "**" + str(ps["n_edits"]) + "**"],
         *[[f"edit {i + 1}", e] for i, e in enumerate(ps["edits"])],
         ["imported, never copied", ", ".join(ps["imported_not_copied"])]])
    kc = p0["k2b_comparison_expected_different"]
    sec["k2bcmp"] = _md(
        ["object", "split-world == k2b at equal seeds"],
        [[k, str(v)] for k, v in kc["identical_by_object"].items()]
        + [["**identical**", ", ".join(kc["identical_objects"])],
           ["**differing**", ", ".join(kc["differing_objects"])],
           ["author half reproduces k2b bit-exactly",
            str(kc["author_half_reproduces_k2b_bit_exactly"])],
           ["only the sequential frame draws differ",
            str(kc["only_sequential_frame_draws_differ"])],
           ["reading", kc["reading"]], ["gates the leg", str(kc["gates"])]])
    c2a = p0["certification"]["C2a"]
    sec["c2a"] = _md(
        ["object", "stream", f"result across the {c2a['n_probe_pairs']} probe pairs"],
        [[k, "author", "bit-identical on every pair: "
          + str(all(r[f"author::{k}::identical"] for r in c2a["rows"]))]
         for k in AUTHOR_OBJECTS]
        + [[k, "frame", f"differs on every pair; norm delta in "
            f"[{c2a['norm_delta_min_by_object'][k]!r}, "
            f"{c2a['norm_delta_max_by_object'][k]!r}]"] for k in FRAME_OBJECTS]
        + [["**C2a**", "—", "**PASS = " + str(c2a["PASS"]) + "**"]])
    c2b, c2c = p0["certification"]["C2b"], p0["certification"]["C2c"]
    sec["c2bc"] = _md(
        ["check", "detail", "PASS"],
        [["C2b determinism", f"same triple rebuilt; {len(c2b['objects'])} objects",
          str(c2b["PASS"])],
         ["C2c shared basis",
          f"loadings bit-identical across all {c2c['n_pairs_checked']} pairs",
          str(c2c["PASS"])]])
    dfc = p0["deframe_cost"]
    sec["deframe"] = _md(
        ["quantity", "value"],
        [["machinery", dfc["machinery"]],
         ["cost per pair, plain", repr(dfc["cost_plain_seconds"])],
         ["cost per pair, with de-framing", repr(dfc["cost_with_deframe_seconds"])],
         ["stride pinned in Part 0", str(dfc["stride_pinned"])],
         ["status", "not exercised on measurement worlds -- the leg stopped first"]])
    b = pil["bands"]
    sec["bands"] = _md(
        ["quantity", "value"],
        [["sigma R_nat (raw / df-inflated)",
          repr(b["sigma_R_nat_raw"]) + " / " + repr(b["sigma_R_nat_df_inflated"])],
         ["sigma R_refresh (raw / df-inflated)",
          repr(b["sigma_R_refresh_raw"]) + " / " + repr(b["sigma_R_refresh_df_inflated"])],
         ["pooled df / inflation", str(b["pooled_df"]) + " / " + repr(b["inflation"])],
         ["SE(range_ref) at 192 pairs", repr(b["SE_range_ref_at_192"])],
         ["M1c realized natural range", repr(b["range_nat_M1C"])],
         ["**V-P3b equivalence band on g_ratio**",
          "**" + repr(b["V_P3b_equivalence_band_on_g_ratio"]) + "**"],
         ["**V-P3c floor on R_refresh levels**",
          "**" + repr(b["V_P3c_floor_on_R_refresh_levels"]) + "**"]])
    sec["pilotarms"] = _md(
        ["phi", "n", "R_nat mean", "R_refresh mean", "R_deframe mean", "PASS"],
        [[repr(q["phi"]), str(q["n"]), repr(q["R_nat_mean"]),
          repr(q["R_refresh_mean"]), repr(q["R_deframe_mean"]), str(q["PASS"])]
         for q in pil["C3"]["per_phi"]])
    rows = []
    for label, blk in (("192 (registered)", g3["base"]),
                       ("384 (escalated)", g3["escalated"])):
        for k, d in blk["per_truth"].items():
            rows.append([label, k, repr(d["SE_range_nat"]), repr(d["SE_range_ref"]),
                         repr(d["ci95"]), repr(d["width"]), repr(G_BUDGET),
                         str(d["within_budget"])])
    sec["projection"] = _md(
        ["pairs/phi", "truth g", "SE(range_nat)", "SE(range_ref)",
         "projected g_ratio 95% CI", "width", "budget", "within"], rows)
    w = g3["why_it_fails"]
    sec["why"] = _md(
        ["quantity", "value"],
        [["structure", w["structure"]],
         ["M1c's realized natural range (the denominator)", repr(w["range_nat_M1C"])],
         ["sigma R_nat (df-inflated)", repr(w["sigma_R_nat_df_inflated"])],
         ["SE(range_nat) at 192", repr(w["SE_range_nat_at_192"])],
         ["**the denominator, in SE**", "**" + repr(w["range_nat_in_SE_at_192"]) + "**"],
         ["reading", w["reading"]]]
        + [[f"pairs/phi needed at truth g = {d['truth_g']}",
            f"{d['smallest_power_of_two_pairs']} = "
            f"{d['multiple_of_registered_192']}x the registered 192"]
           for d in w["pairs_needed"].values()])
    alt = w["named_alternative_estimand"]
    sec["alt"] = _md(
        ["property", "value"],
        [["quantity", alt["quantity"]], ["why it helps", alt["why_it_helps"]]]
        + [[f"at {k} pairs/phi: SE(range_ref) / 2-SE half-width / range_nat in SE",
            f"{d['SE_range_ref']!r} / {d['half_width_2SE']!r} / "
            f"{d['range_ref_if_equal_to_range_nat_in_SE']!r}"]
           for k, d in alt["power"].items()]
        + [["**status**", "**" + alt["status"] + "**"]])
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[q["n"], q["condition"],
          ("**" + q["text"] + "**  <-- THIS LEG")
          if q["outcome"] == dec["verdict_slug"] else q["text"]]
         for q in TRUTH_TABLE])
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
    sec["timing"] = _md(
        ["stage", "estimate (s)", "measured (s)"],
        [["part0 (extraction + provenance + C2)", str(est["part0"]),
          "%.3f" % meas.get("part0_done", float("nan"))],
         ["pilot (C3 + bands)", str(est["pilot"]),
          "%.3f" % meas.get("pilot_done", float("nan"))],
         ["project (G3)", str(est["project"]),
          "%.3f" % meas.get("project_done", float("nan"))],
         ["arms (5)", str(est["arms_each"]) + " each", "-- not reached"],
         ["fit", str(est["fit"]), "-- not reached"],
         ["finalize", str(est["finalize"]),
          "%.3f" % meas.get("finalize_done", float("nan"))]])
    body = ["# M4-P3b report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts_np(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
              dec: dict[str, Any]) -> None:
    b = pil["bands"]
    ps = p0["provenance_summary"]
    c2a = p0["certification"]["C2a"]
    w = g3["why_it_fails"]
    kc = p0["k2b_comparison_expected_different"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"], "STOPPED_AT": dec["stopped_at"],
        "MODIFIERS": ", ".join(dec["modifiers"]) or "none",
        "NPROV": ps["n_mapped_entries"], "NEDITS": ps["n_edits"],
        "PROBES": c2a["n_probe_pairs"],
        "C2A": c2a["PASS"], "C2B": p0["certification"]["C2b"]["PASS"],
        "C2C": p0["certification"]["C2c"]["PASS"], "C3": pil["C3"]["PASS"],
        "AUTHOR_EXACT": kc["author_half_reproduces_k2b_bit_exactly"],
        "ONLY_SEQ": kc["only_sequential_frame_draws_differ"],
        "IDENT": ", ".join(kc["identical_objects"]),
        "DIFFER": ", ".join(kc["differing_objects"]),
        "COMMON_MIN": c2a["norm_delta_min_by_object"]["common"],
        "COMMON_MAX": c2a["norm_delta_max_by_object"]["common"],
        "SIG_NAT": b["sigma_R_nat_df_inflated"],
        "SIG_REF": b["sigma_R_refresh_df_inflated"],
        "DF": b["pooled_df"], "INFL": b["inflation"],
        "EQBAND": b["V_P3b_equivalence_band_on_g_ratio"],
        "FLOOR": b["V_P3c_floor_on_R_refresh_levels"],
        "RANGE_NAT": w["range_nat_M1C"], "SE_RN": w["SE_range_nat_at_192"],
        "DENOM_SE": w["range_nat_in_SE_at_192"],
        "W04": g3["base"]["per_truth"]["0.04"]["width"],
        "W05": g3["base"]["per_truth"]["0.5"]["width"],
        "E04": g3["escalated"]["per_truth"]["0.04"]["width"],
        "E05": g3["escalated"]["per_truth"]["0.5"]["width"],
        "GBUD": G_BUDGET, "ESC": g3["escalation_fired"],
        "NEED": w["pairs_needed"]["0.04"]["smallest_power_of_two_pairs"],
        "NEEDX": w["pairs_needed"]["0.04"]["multiple_of_registered_192"],
        "STRIDE": p0["deframe_cost"]["stride_pinned"],
        "COST_PLAIN": p0["deframe_cost"]["cost_plain_seconds"],
        "COST_DEF": p0["deframe_cost"]["cost_with_deframe_seconds"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    write_json(OUT / "prose_facts.json", f)


def _facts(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
           fit: dict[str, Any], dec: dict[str, Any]) -> None:
    b = pil["bands"]
    ps = p0["provenance_summary"]
    c2a = p0["certification"]["C2a"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "MODIFIERS": ", ".join(dec["modifiers"]) or "none",
        "CLASS": fit["classification"],
        "NPAIRS": fit["pairs_per_phi"], "NWORLDS": dec["total_worlds"],
        "NPROV": ps["n_mapped_entries"], "NEDITS": ps["n_edits"],
        "PROBES": c2a["n_probe_pairs"],
        "C2A": c2a["PASS"], "C2B": p0["certification"]["C2b"]["PASS"],
        "C2C": p0["certification"]["C2c"]["PASS"],
        "NDMIN": repr(c2a["norm_delta_min_by_object"]),
        "NDMAX": repr(c2a["norm_delta_max_by_object"]),
        "STRIDE": p0["deframe_cost"]["stride_pinned"],
        "NDEFRAME": p0["deframe_cost"]["n_deframe_per_arm"],
        "SIG_NAT": b["sigma_R_nat_df_inflated"],
        "SIG_REF": b["sigma_R_refresh_df_inflated"],
        "DF": b["pooled_df"], "INFL": b["inflation"],
        "EQBAND": b["V_P3b_equivalence_band_on_g_ratio"],
        "FLOOR": b["V_P3c_floor_on_R_refresh_levels"],
        "ESC": g3["escalation_fired"],
        "W04": g3["base"]["per_truth"]["0.04"]["width"],
        "W05": g3["base"]["per_truth"]["0.5"]["width"],
        "RANGE_NAT": fit["range_nat"], "RANGE_NAT_CI": fit["range_nat_ci95"],
        "RANGE_REF": fit["range_ref"], "RANGE_REF_CI": fit["range_ref_ci95"],
        "M1C_RANGE": fit["M1c_range_nat"], "RANGE_DIFF": fit["range_nat_vs_M1C"],
        "G": fit["g_ratio"], "GCI": fit["g_ratio_ci95"], "GW": fit["g_ratio_width"],
        "GBUD": fit["g_budget"], "GOK": fit["within_budget"],
        "C1_N": fit["C1_prime"]["n_inside"], "C1_PASS": fit["C1_prime"]["PASS"],
        "C1_MAXZ": max(abs(a["z_pooled"]) for a in fit["C1_prime"]["rows"]),
        "V3C": fit["V_P3c"]["fires"],
        "NRULE13": len(fit["rule13_events"]), "B": fit["B"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    for q in fit["per_phi"]:
        tag = str(q["phi"]).replace(".", "")
        f[f"P{tag}_NAT"] = q["R_nat_mean"]
        f[f"P{tag}_REF"] = q["R_refresh_mean"]
        f[f"P{tag}_DEF"] = q["R_deframe_mean"]
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-P3b — the refresh gradient, certified instrument — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}); modifiers: {{MODIFIERS}}.**
{{ROUTING_TEXT}}. Stopped at {{STOPPED_AT}}. **0 measurement worlds.**

**The instrument P3 said was needed now exists and is certified.** What the leg
also establishes is that the registered estimand cannot be measured on it at any
feasible size: g_ratio's projected CI is {{W04}} wide at the registered 192
pairs/φ and still {{E04}} at the escalated 384, against a {{GBUD}} budget, and
**{{NEED}} pairs/φ — {{NEEDX}}× the registered design — would be required.** The
reason is structural and is stated in §4.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit debc68e).
Every number below is generated from artifacts by code (rule 24).

---

## 1. The instrument, and its provenance

P3 proved generator-side frame refreshment impossible on k2b's published
two-parameter interface. The licensed remedy was minimal extraction with
provenance. `build_split_world(author_seed, frame_seed, phi_slow)` is that
extraction: **{{NPROV}} mapped entries covering k2b:321-349, and exactly
{{NEDITS}} edits.**

<<TABLE:provsummary>>

<<TABLE:provenance>>

Constants and helpers are **imported from k2b, never copied**, so a change there
propagates here instead of silently diverging. k2b and `suica_core/` are
untouched and diff-verified.

### 1.1 The one addition, and why it matters

k2b does not return `loadings`. That omission is exactly what made P3's
channel-surgery route undetectable — a caller splicing two worlds could not see
it had mixed two orthonormal bases. The extracted builder returns `loadings`,
which is what makes C2c checkable at all.

### 1.2 The comparison against k2b is a positive verification

<<TABLE:k2bcmp>>

At equal seeds the **author half reproduces k2b bit-exactly**
({{AUTHOR_EXACT}}): `loadings` and `z` are the first draws of the author stream
exactly as they are k2b's first draws, so `trait` matches, and `a_load`,
`common` and `int` are keyed on a seed rather than on stream position, so they
match too. The only divergence is {{DIFFER}} — the three objects the frame
stream draws in sequence, which differ because that stream restarts at the
seed's first draw instead of continuing after the author draws
({{ONLY_SEQ}}). **The divergence is localised to the stream restart itself**,
which is inherent to splitting and gates nothing.

## 2. Certification — the split P3 proved impossible on the published interface

<<TABLE:c2a>>

<<TABLE:c2bc>>

Across {{PROBES}} probe pairs sharing an author seed, **every author object is
bit-identical and every frame object differs** — `common`, the frame channel
proper, by a norm delta in [{{COMMON_MIN}}, {{COMMON_MAX}}]. C2b rebuilds a
world from the same triple bit-identically; C2c confirms the shared basis on
every pair. C2a = {{C2A}}, C2b = {{C2B}}, C2c = {{C2C}}.

**This is the leg's durable asset**: a certified split-seed instrument for the
K2b family, obtained without touching published machinery.

## 3. C3 — the sanity pilot and the bands

<<TABLE:pilotarms>>

<<TABLE:bands>>

The V-P3b equivalence band ({{EQBAND}}) and the V-P3c floor ({{FLOOR}}) were
computed from realized pilot noise, df-inflated (df {{DF}}, factor {{INFL}}),
and written **before** any arm — exactly as registered. C3 = {{C3}}.

The equivalence band is itself the first warning: **{{EQBAND}} spans nearly the
whole interesting range of g_ratio**, so at the registered size almost any ratio
would have been indistinguishable from zero.

## 4. G3 — the projection, and why it fails

<<TABLE:projection>>

<<TABLE:why>>

The estimand is a **ratio whose denominator is the natural gradient itself**.
M1c's realized natural range is {{RANGE_NAT}}, and SE(range_nat) at 192 pairs is
{{SE_RN}} — so the denominator sits at **{{DENOM_SE}} SE**. Dividing by a
quantity known to three standard errors produces a wide ratio however precisely
the numerator is measured: widths {{W04}} / {{W05}} at 192 and {{E04}} /
{{E05}} at 384, against a {{GBUD}} budget. The once-only escalation fired and
did not rescue it ({{ESC}}); {{NEED}} pairs/φ ({{NEEDX}}×) would be needed.

Per rule 25 and the registration's routing, the leg stops here: **no measurement
world is spent against a failed feasibility gate.**

### 4.1 A named alternative, so the handback is actionable

<<TABLE:alt>>

A DIFFERENCE does not divide by a small noisy denominator. This is **named for
the planner, not chosen** — the executor does not substitute estimands.

## 5. What was not reached

C1′ (the M1c anchor as certificate) and the five measurement arms are not
reached: the rule-25 gate fires before them. C1′ therefore remains the right
first test on any re-dispatch, and the instrument is ready for it.

## 6. Routing

<<TABLE:truth_table>>

## 7. Gates

<<TABLE:gates>>

## 8. Sides declared (rule 22)

<<TABLE:sides>>

## 9. Pinned readings

<<TABLE:rn>>

## 10. Rule events

- **Rule 13:** not reached — no verdict boundary exists without a measurement.
- **Rule 25:** fired as designed; this is the gate that stopped the leg.
- **Rule 26:** no bounded winner.
- **Rule 27:** the g_ratio budget is what rule 25 projected against; unmet at
  both the registered and the escalated size.
- **Rule 29:** the domain-pinned predicate ran on BOTH scorings at both pilot φ.
- **Rule 30:** every cited constant read from its persisted source; the
  provenance table is generated from the extraction's own line map.

## 11. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython {{PYTHON}} venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (a wrong claim in my own draft, caught before the verdict).** The first
   draft of this harness asserted that the split builder would differ from k2b
   on *every* object at equal seeds. It does not: the author half matches
   bit-exactly (§1.2). The assertion was replaced with a generated per-object
   comparison before any gate consumed it, and the finding is stronger than the
   claim it replaced. No number changed.

<<TABLE:deframe>>

R_deframe's stride was measured and pinned at {{STRIDE}} in Part 0
(plain {{COST_PLAIN}} s/pair, {{COST_DEF}} s/pair with de-framing), so the
secondary reading would have run on every measurement world had the leg
reached them.

## 12. Environment

<<TABLE:env>>

## 13. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_p3b_refresh_gradient/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `decision.json`,
`prose_facts.json`, `report_tables.md`, `run_log.jsonl`. Harness:
`scripts/run_suica_m4_p3b_refresh_gradient.py`.*
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
        bad = re.findall(r"\{\{[A-Z0-9_']+\}\}|<<TABLE:[a-z0-9_]+>>", txt)
        raise SystemExit(f"REFUSED: unresolved placeholders: {sorted(set(bad))}")
    path = ROOT / "reports" / "SUICA_M4_P3B_REFRESH_GRADIENT_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("pilot", stage_pilot), ("project", stage_project)]
    for phi in PHI_LADDER:
        stages.append((f"arm_phi{phi}", (lambda pp: lambda a: _arm(pp))(phi)))
    stages += [("fit", stage_fit), ("finalize", stage_finalize),
               ("report", stage_report)]
    for name, fn in stages:
        sub.add_parser(name).set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
