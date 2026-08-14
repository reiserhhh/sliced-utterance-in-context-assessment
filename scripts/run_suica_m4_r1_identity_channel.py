#!/usr/bin/env python3
"""SUICA M4-R1 -- the identity-channel instrument.

Registered BEFORE run in docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md
("M4-R1", commit f8bc446).  Binding.  An INSTRUMENT leg: no theory verdict,
only certificates.

Five closed lines established that the k2b family's cards carry ONLY biography:
there is no non-trait author channel for any instrument to find (appendix KK).
This leg plants one.  `build_split_world_v2` extends P3b's certified builder
with a per-author, persistent, NON-TRAIT style channel that enters the response
path at exactly the site where the trait enters, with a zero-default weight so
the extension certifies backward bit-identity.

Once certified, the programme's identity instruments can be pointed at a world
that can answer YES or NO.

Stages: part0 -> pilot -> project -> arm_w<..> (3) -> fit -> finalize -> report
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

OUT = ROOT / "results" / "m4_r1_identity_channel"
RES = ROOT / "results"
P3BSRC = ROOT / "scripts" / "run_suica_m4_p3b_refresh_gradient.py"
K2BSRC = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
P3CRES = RES / "m4_p3c_transportable_gradient"
Q1BRES = RES / "m4_q1b_card_cosine"

LEG = "M4-R1"
BANNER = ("the identity-channel instrument: a planted per-author non-trait style "
          "channel with zero-default weight; certificates only, no theory verdict")

MASTER_SEED = 20260814
SALT_AUTHOR = "m4r1-author"
SALT_FRAME_A = "m4r1-frameA"
SALT_FRAME_B = "m4r1-frameB"
SALT_PILOT = "m4r1-pilot"
SHARE = 0.25
PHI = 0.60
PHI_PROBE = (0.05, 0.60)
W_STYLE_ARMS = (0.0, 0.5, 1.0)          # multiples of w_mu
N_PAIRS = 128
N_PAIRS_ESCALATED = 256
PILOT_PAIRS = 4
PROBE_PAIRS = 8
W_INT_ARM = "zero"

B_BOOT = 2000
B_BOOT_HIGH = 20000
B_PROJ = 2000
RULE13_FACTOR = 10.0
CHI2_Q = 0.10
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
SATURATION_ABS = 0.995

W_MU_PERSISTED = 0.33541019662496846     # arm_weights(0.25, "zero")["mu"], pinned
AUTHOR_OBJECTS = ("trait", "a_load", "loadings", "style")
FRAME_OBJECTS = ("slow", "slow_latent", "noise", "common", "int")

# ---------------------------------------------------------------------------
# RN-R1 notes.  PINNED IN PART 0, BEFORE ANY MEASUREMENT ARM.
#
# RN-R1-1 (the placement, and why it needs no k2b edit).  The trait enters the
#   RESPONSE path at exactly one site: k2b's emit_panel,
#       v += w["mu"] * world["trait"][i][None, :]
#   The registration asks for the mirror `+ w_style * style_a` at that site,
#   and w_style is specified in MULTIPLES of w_mu.  Writing w_style = m * w_mu,
#       w_mu*trait + w_style*style = w_mu * (trait + m*style)
#   EXACTLY.  So publishing `trait_eff = trait + m*style` as the world's
#   `trait` key makes k2b's own UNEDITED emit_panel carry the style term at
#   precisely the trait's site, with the trait's own weight structure, in the
#   observed panel AND in every truth panel that uses "mu".  k2b, suica_core/
#   and the P3b builder stay READ-ONLY.  The untouched trait is published
#   separately as `trait_pure` because C-R1c scores r-hat against the CENTRED
#   TRAIT ONLY, and `style` is published for C-R1b.
#
# RN-R1-2 (the prefix property).  style_a is drawn as the LAST author-stream
#   draw, after _zeta.  numpy's Generator is sequential, so every earlier draw
#   -- loadings, z, _zeta -- is bit-identical to P3b's whatever style does
#   afterwards; a_load comes from its own stable_bucket-seeded generator and is
#   untouched by construction.  The frame stream is never read by the
#   extension.  C-R1a proves all of this rather than asserting it.
#
# RN-R1-3 (the shared component, NAMED as #60 requires).  At w_style > 0 the
#   card is
#       w_mu*trait_c + w_style*style_c + w_slow*slow_c_bar + w_noise*noise_c_bar
#   and an A/B pair shares the author stream only, so THE SHARED COMPONENT IS
#       w_mu * trait_c  +  w_style * style_c
#   -- centred trait plus centred style.  Naming it is the whole point of #60:
#   Q1b's defect was scoring an excess against an object the cards did not
#   share.  Here r-hat is scored against the CENTRED TRAIT ONLY, deliberately,
#   so the planted style shows up as excess rather than being absorbed.
#
# RN-R1-4 (which Delta routes -- the Q1b lesson applied).  Q1b established that
#   the per-author exact form is the correct one and that the pooled-mean form
#   carries a reference-object bias.  The registration writes
#   "Delta_style = cos_AB - r_A*r_B".  PINNED: the PER-AUTHOR EXACT form
#       Delta = mean_i [ cos(A_i,B_i) - cos(A_i, t_c_i) * cos(B_i, t_c_i) ]
#   routes, because it is the form #60 blesses and the form on which Q1b's
#   CARD_PURE_TRAIT adjudication rests; the pooled-mean form is computed and
#   reported beside it at equal precision.  If they disagree in sign or
#   certificate outcome, that disagreement is reported as the finding.
#
# RN-R1-5 (the algebraic band, derived and persisted BEFORE the arms).  Write
#   the per-author card as t + s + n with t = w_mu*trait_c, s = w_style*style_c
#   and n the frame-stream remainder, and let a = E||t||^2, b = E||s||^2,
#   d = E||n||^2.  A and B share t and s exactly and their n's are independent,
#   so in expectation
#       cos(A,B) = (a+b)/(a+b+d),   cos(A,t_c) = sqrt(a)/sqrt(a+b+d),
#       Delta    = cos(A,B) - cos(A,t_c)*cos(B,t_c) = b/(a+b+d).
#   At w_style = 0 this is exactly 0, which is the Q1b-corrected null; at
#   w_style > 0 it is strictly positive and increasing in b, hence monotone in
#   w_style.  a, b and d are MEASURED on probe worlds in Part 0 (executed
#   provenance, rule 30) and the prediction with its band is persisted before
#   any arm runs.  The band is +/- 2 SE of the probe-set mean prediction.
#
# RN-R1-7 (the band's own defect, diagnosed AFTER the arms and labelled as
#   such).  The Part-0 band was persisted before the arms as required, and it
#   is +/- 2 SE of the PROBE-SET prediction mean.  That construction has two
#   flaws, both mine, both visible only once the measurement exists:
#     (a) at w_style = 0 the prediction is EXACTLY 0 at every probe world, so
#         its SE is exactly 0 and the band has ZERO WIDTH -- no measured value
#         except a literal 0.0 could ever fall inside it.  Clause (i) already
#         tests w = 0 properly against epsilon, so clause (iv) is testing a
#         degenerate object there.
#     (b) at w_style > 0 the band carries only the PREDICTION's probe-set
#         spread.  It ignores the MEASUREMENT's own standard error, and -- more
#         importantly -- it ignores the DERIVATION's approximation error: the
#         algebra assumes per-author orthogonality of t, s and n (realized
#         cos(style_c, trait_c) ~ 0.0024, not 0) and equates a ratio of means
#         with a mean of ratios (Jensen).  Both are small and both grow with b,
#         which is why the gap is 0.008% at w = 0.5 and 0.93% at w = 1.0.
#   The persisted band ROUTES -- retuning a band after seeing the measurement
#   is exactly the move this programme forbids.  A corrected band is computed
#   and reported as an explicitly POST-HOC diagnostic so the planner can re-band
#   a successor leg; it changes no verdict here.
#
# RN-R1-6 (non-degeneracy, #59).  Delta at w > 0 is not forced by any shared-
#   object identity: it depends on realized norms and on the planted weight,
#   and the w = 0 null is the UNEXTENDED builder's verified behaviour (Q1b),
#   not an identity of the extension.  The extension's own degenerate risk --
#   that style is secretly trait -- is exactly what C-R1b's independence check
#   tests.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-R1-1": "w_style is in multiples of w_mu, so w_mu*trait + w_style*style = "
               "w_mu*(trait + m*style) EXACTLY; publishing trait_eff = trait + m*style "
               "as the world's `trait` makes k2b's own UNEDITED emit_panel carry style "
               "at precisely the trait's site. trait_pure and style are published "
               "separately for C-R1c and C-R1b. k2b/suica_core/P3b stay READ-ONLY",
    "RN-R1-2": "style_a is the LAST author-stream draw (after _zeta), so every earlier "
               "draw is bit-identical to P3b's by the sequential-generator prefix "
               "property; a_load has its own stable_bucket generator and the frame "
               "stream is never read. C-R1a proves it rather than asserting it",
    "RN-R1-3": "#60 naming: at w_style > 0 the A/B shared component is "
               "w_mu*trait_c + w_style*style_c (centred trait PLUS centred style); "
               "r-hat is scored against the CENTRED TRAIT ONLY, deliberately, so the "
               "planted style appears as excess instead of being absorbed",
    "RN-R1-4": "the PER-AUTHOR EXACT Delta routes (the form #60 blesses and on which "
               "Q1b's adjudication rests); the pooled-mean form is reported beside it "
               "and any disagreement is the finding",
    "RN-R1-5": "algebraic band: with a = E||w_mu*trait_c||^2, b = E||w_style*style_c||^2, "
               "d = E||frame remainder||^2, Delta = b/(a+b+d) in expectation -- exactly "
               "0 at w=0 and increasing in w. a, b, d are MEASURED on probe worlds in "
               "Part 0 and the prediction + band persisted BEFORE any arm (rule 30)",
    "RN-R1-7": "the Part-0 band (+/- 2 SE of the probe-set prediction) has two flaws, "
               "both the executor's: at w = 0 the prediction's SE is exactly 0 so the "
               "band has ZERO WIDTH and clause (iv) tests a degenerate object there; at "
               "w > 0 the band carries only the prediction's probe spread and ignores "
               "both the measurement's SE and the derivation's approximation error "
               "(per-author orthogonality, Jensen), which grow with b -- hence 0.008% "
               "at w=0.5 and 0.93% at w=1.0. The persisted band ROUTES; a corrected "
               "band is reported as an explicitly POST-HOC diagnostic only",
    "RN-R1-6": "#59: Delta at w > 0 is not forced -- it depends on realized norms and "
               "the planted weight; the w = 0 null is the unextended builder's verified "
               "behaviour, not an identity of the extension; the 'style is secretly "
               "trait' degeneracy is what C-R1b's independence check tests",
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


# ---------------------------------------------------------------------------
# THE EXTENSION -- P3b's builder plus one author-stream draw (RN-R1-1/2).
#
# Provenance: every line carries its P3b source line; the ONLY additions are
# marked NEW.  P3b's own provenance chain back to k2b:321-349 is unbroken.
PROVENANCE = [
    ("291-292", "rng_a = default_rng(author_seed); rng_f = default_rng(frame_seed)",
     "unchanged", "both streams"),
    ("294", "loadings = _orthonormal_loadings(rng_a, DIM, k)", "unchanged", "author"),
    ("295", "z = rng_a.normal(size=(n, k))", "unchanged", "author"),
    ("296", "_zeta = rng_a.normal(size=(n, k))", "unchanged", "author"),
    ("--", "(no P3b line)", "style_z = rng_a.normal(size=(n, k))   # NEW, LAST author "
           "draw -- the prefix property (RN-R1-2)", "author / NEW"),
    ("298-304", "xs / innovation_scale / the AR recursion / noise", "unchanged",
     "frame"),
    ("306", "trait = A_SCALE * ((z * G_PROFILE) @ loadings.T)", "unchanged -> published "
            "as `trait_pure`", "author"),
    ("--", "(no P3b line)", "style = A_SCALE * ((style_z * G_PROFILE) @ loadings.T)   "
           "# NEW, the trait's own construction through the SHARED basis",
     "author / NEW"),
    ("--", "(no P3b line)", "trait_eff = trait_pure + m * style   # NEW; m = w_style / "
           "w_mu, so w_mu*trait_eff = w_mu*trait + w_style*style EXACTLY (RN-R1-1)",
     "author / NEW"),
    ("307", "slow = A_SCALE * ((xs * G_PROFILE) @ loadings.T)", "unchanged", "frame"),
    ("308-312", "common_lat / common via f2().shock_vector(frame_seed, ...)",
     "unchanged", "frame"),
    ("313-316", "a_rng from stable_bucket(str(author_seed)); a_load", "unchanged -- its "
                "own generator, untouched by the new draw", "author"),
    ("317-320", "shocks via k2a().shock_int_matrix(frame_seed, ...); u_int; s_int",
     "unchanged", "frame / mixed"),
    ("321-329", "return {trait, slow, int, common, noise, slow_latent, a_load, "
                "loadings}", "`trait` now holds trait_eff; PLUS `trait_pure`, `style`, "
                "`w_style`, `m_style`", "return"),
]


def build_split_world_v2(author_seed: int, frame_seed: int, phi_slow: float,
                         w_style: float = 0.0) -> dict[str, np.ndarray]:
    """P3b's build_split_world with a planted per-author STYLE channel.

    w_style is in MULTIPLES of w_mu (the trait's response weight); 0 is the
    default and reproduces P3b bit-identically (C-R1a proves it).
    """
    m_ = k2b()
    lay = m_.layout()
    n = len(lay["author_ids"])
    t_max = int(lay["t_max"])
    k = m_.K_LATENT

    rng_a = np.random.default_rng(author_seed)               # p3b:291
    rng_f = np.random.default_rng(frame_seed)                # p3b:292

    loadings = m_._orthonormal_loadings(rng_a, m_.DIM, k)    # p3b:294
    z = rng_a.normal(size=(n, k))                            # p3b:295
    _zeta = rng_a.normal(size=(n, k))                        # p3b:296
    style_z = rng_a.normal(size=(n, k))                      # NEW: LAST author draw

    xs = np.empty((n, t_max, k), dtype=float)                # p3b:298
    xs[:, 0] = rng_f.normal(size=(n, k))                     # p3b:299
    innovation_scale = math.sqrt(1.0 - phi_slow ** 2)        # p3b:300
    for t in range(1, t_max):                                # p3b:301
        xs[:, t] = (phi_slow * xs[:, t - 1]
                    + innovation_scale * rng_f.normal(size=(n, k)))   # p3b:302-303
    noise = rng_f.normal(size=(n, t_max, m_.DIM))            # p3b:304

    trait_pure = m_.A_SCALE * ((z * m_.G_PROFILE) @ loadings.T)        # p3b:306
    style = m_.A_SCALE * ((style_z * m_.G_PROFILE) @ loadings.T)       # NEW
    trait_eff = trait_pure + float(w_style) * style                    # NEW (RN-R1-1)

    slow = m_.A_SCALE * ((xs * m_.G_PROFILE) @ loadings.T)             # p3b:307
    common_lat = np.stack([                                            # p3b:308-311
        np.stack([m_.f2().shock_vector(frame_seed, c, o, k) for o in range(t_max)])
        for c in lay["contexts_sorted"]
    ])
    common = m_.A_SCALE * ((common_lat * m_.G_PROFILE) @ loadings.T)   # p3b:312
    a_rng = np.random.default_rng(                                     # p3b:313-315
        m_.v8.stable_bucket(str(author_seed), salt="m4k2b-loading", modulus=2 ** 63 - 1)
    )
    a_load = a_rng.normal(size=(n, k))                                 # p3b:316
    shocks = np.stack([m_.k2a().shock_int_matrix(frame_seed, o, k)
                       for o in range(t_max)])                         # p3b:317-318
    u_int = np.einsum("ij,ojl->iol", a_load, shocks) / math.sqrt(k)    # p3b:319
    s_int = m_.A_SCALE * ((u_int * m_.G_PROFILE) @ loadings.T)         # p3b:320
    return {
        "trait": trait_eff,          # what k2b's emit_panel / card will consume
        "trait_pure": trait_pure,    # NEW: the untouched trait, for C-R1c's r-hat
        "style": style,              # NEW: for C-R1b
        "slow": slow, "int": s_int, "common": common,
        "noise": m_.SIGMA_ISO * noise, "slow_latent": xs, "a_load": a_load,
        "loadings": loadings,
        "m_style": float(w_style),
        "w_style_absolute": float(w_style) * W_MU_PERSISTED,
    }


# ---------------------------------------------------------------------------

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


def seed_for(kind: str, w: float, i: int, salt: str) -> int:
    key = f"{LEG}|{salt}|{kind}|w{w!r}|i{i}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def pair_seeds(w: float, i: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", w, i, SALT_AUTHOR + suffix),
            "frameA": seed_for("frameA", w, i, SALT_FRAME_A + suffix),
            "frameB": seed_for("frameB", w, i, SALT_FRAME_B + suffix)}


def _cellmean(x: np.ndarray) -> np.ndarray:
    lay = k2b().layout()
    ck, ridx = lay["cell_key"], lay["retained_idx"]
    keys = [str(ck[i]) for i in ridx]
    out = np.empty_like(x)
    pos = 0
    for key in sorted(set(keys)):
        n = sum(1 for q in keys if q == key)
        out[pos:pos + n] = x[pos:pos + n].mean(axis=0, keepdims=True)
        pos += n
    return out


def _rowcos(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (np.einsum("id,id->i", a, b)
            / np.sqrt(np.einsum("id,id->i", a, a) * np.einsum("id,id->i", b, b)))


def card_parts(world: dict[str, np.ndarray], w: dict[str, float]) -> dict[str, Any]:
    """The card and its named components, in retained-cell order (k2b:410-442)."""
    m_ = k2b()
    lay = m_.layout()
    counts, ck = lay["counts"], lay["cell_key"]
    keys = ck[lay["retained_idx"]]
    card, tpart, spart, npart, tpure_c, styl_c = [], [], [], [], [], []
    for key in sorted(set(map(str, keys))):
        idx = np.asarray([i for i in lay["retained_idx"] if str(ck[i]) == key],
                         dtype=int)
        m = int(counts[idx[0]])
        occ = np.arange(m)
        te = world["trait"][idx]
        te_c = te - te.mean(axis=0, keepdims=True)
        tp = world["trait_pure"][idx]
        tp_c = tp - tp.mean(axis=0, keepdims=True)
        st = world["style"][idx]
        st_c = st - st.mean(axis=0, keepdims=True)
        sc = (world["slow"][idx, :m]
              - world["slow"][idx, :m].mean(axis=0, keepdims=True))
        nc = (world["noise"][idx, :m]
              - world["noise"][idx, :m].mean(axis=0, keepdims=True))
        t_term = w["mu"] * tp_c
        s_term = w["mu"] * float(world["m_style"]) * st_c
        n_term = (w["slow"] * sc[:, occ, :].mean(axis=1)
                  + w["noise"] * nc[:, occ, :].mean(axis=1))
        card.append(w["mu"] * te_c + n_term)
        tpart.append(t_term)
        spart.append(s_term)
        npart.append(n_term)
        tpure_c.append(tp_c)
        styl_c.append(st_c)
    return {"card": np.concatenate(card), "t": np.concatenate(tpart),
            "s": np.concatenate(spart), "n": np.concatenate(npart),
            "trait_c": np.concatenate(tpure_c), "style_c": np.concatenate(styl_c)}


def delta_for_pair(w_style: float, i: int, suffix: str = "") -> dict[str, Any]:
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    sd = pair_seeds(w_style, i, suffix)
    wa = build_split_world_v2(sd["author"], sd["frameA"], PHI, w_style)
    wb = build_split_world_v2(sd["author"], sd["frameB"], PHI, w_style)
    pa, pb = card_parts(wa, w), card_parts(wb, w)
    cab = _rowcos(pa["card"], pb["card"])
    cat = _rowcos(pa["card"], pa["trait_c"])
    cbt = _rowcos(pb["card"], pb["trait_c"])
    return {
        "w_style": w_style, "pair": i,
        "author_seed": sd["author"], "frameA_seed": sd["frameA"],
        "frameB_seed": sd["frameB"],
        "cos_AB": float(cab.mean()),
        "r_A": float(cat.mean()), "r_B": float(cbt.mean()),
        # RN-R1-4: the PER-AUTHOR EXACT form routes
        "Delta": float(np.mean(cab - cat * cbt)),
        "Delta_meanform": float(cab.mean() - cat.mean() * cbt.mean()),
        "a": float(np.einsum("id,id->i", pa["t"], pa["t"]).mean()),
        "b": float(np.einsum("id,id->i", pa["s"], pa["s"]).mean()),
        "d": float(np.einsum("id,id->i", pa["n"], pa["n"]).mean()),
        "cos_style_trait": float(_rowcos(pa["style_c"], pa["trait_c"]).mean()),
        "n_authors": int(len(cab)),
    }


def _predicate(v: np.ndarray) -> dict[str, Any]:
    fin = bool(np.all(np.isfinite(v)))
    sat = bool(np.any(np.abs(v) >= SATURATION_ABS))
    nz = bool(float(np.std(v, ddof=1)) > 0.0)
    return {"all_finite": fin, "any_saturated": sat, "nonzero_variance": nz,
            "min": float(v.min()), "max": float(v.max()),
            "PASS": bool(fin and (not sat) and nz)}


# ---------------------------------------------------------------------------
# PART 0 -- provenance, C-R1a, C-R1b, the algebraic band.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)

    # --- G0: hashes and the pinned w_mu ------------------------------------
    fn = p3b().build_split_world
    fn_sha = hashlib.sha256(inspect.getsource(fn).encode("utf-8")).hexdigest()
    file_sha = hashlib.sha256(P3BSRC.read_bytes()).hexdigest()
    p3cprov = read_json(P3CRES / "part0.json")["instrument_provenance"]
    src = K2BSRC.read_text(encoding="utf-8").split("\n")
    site_line = next((i + 1 for i, ln in enumerate(src)
                      if 'v += w["mu"] * world["trait"][i][None, :]' in ln), None)
    g0 = {
        "instrument": {
            "imported_from": rel(P3BSRC),
            "definition_line": int(inspect.getsourcelines(fn)[1]),
            "function_sha256": fn_sha, "file_sha256": file_sha,
            "p3c_persisted_function_sha256": p3cprov["function_sha256"],
            "p3c_persisted_file_sha256": p3cprov["file_sha256"],
            "sha_matches": bool(fn_sha == p3cprov["function_sha256"]
                                and file_sha == p3cprov["file_sha256"])},
        "injection_site": {
            "file_line": f"{rel(K2BSRC)}:{site_line}",
            "source": src[site_line - 1].strip() if site_line else None,
            "function": "emit_panel",
            "mirror": "+ w_style * style_a, realised as trait_eff = trait + m*style "
                      "because w_style = m * w_mu (RN-R1-1)",
            "why_no_edit": "k2b, suica_core/ and the P3b builder stay READ-ONLY"},
        "w_mu": {"persisted": float(w["mu"]), "pinned": W_MU_PERSISTED,
                 "bit_exact": bool(float(w["mu"]) == W_MU_PERSISTED),
                 "source": "k2b.arm_weights(0.25, 'zero')['mu']"},
        "q1b_verdict": read_json(Q1BRES / "decision.json")["verdict_slug"],
        "q1b_centred_null": read_json(Q1BRES / "fit.json")["per_phi"][0][
            "Delta_author_cen_mean"],
    }
    g0["PASS"] = bool(g0["instrument"]["sha_matches"] and g0["w_mu"]["bit_exact"]
                      and site_line is not None)

    # --- C-R1a: backward bit-identity at w_style = 0 -----------------------
    rows = []
    for phi in PHI_PROBE:
        for i in range(PROBE_PAIRS):
            sd = pair_seeds(0.0, i, "-probeA")
            v2 = build_split_world_v2(sd["author"], sd["frameA"], phi, 0.0)
            v1 = p3b().build_split_world(sd["author"], sd["frameA"], phi)
            objs = {k: bool(np.array_equal(np.asarray(v2[k]).view(np.uint8),
                                           np.asarray(v1[k]).view(np.uint8)))
                    for k in v1}
            pan2 = m_.emit_panel(v2, w)
            pan1 = m_.emit_panel(v1, w)
            pan_ok = bool(all(np.array_equal(a.view(np.uint8), b.view(np.uint8))
                              for a, b in zip(pan2, pan1)))
            f2_, _r2 = m_.card_channel_frame(v2, w, sd["author"])
            f1_, _r1 = m_.card_channel_frame(v1, w, sd["author"])
            num = [c for c in f1_.columns if c != "cell_key"]
            card_ok = bool(np.array_equal(
                np.ascontiguousarray(f2_[num].to_numpy(float)).view(np.uint8),
                np.ascontiguousarray(f1_[num].to_numpy(float)).view(np.uint8)))
            fld_ok = None
            if i < 2:                      # fields are the expensive check
                r2f = m_.run_field_world("R1-CR1a", i, v2, w, verify=False)
                r1f = m_.run_field_world("R1-CR1a", i, v1, w, verify=False)
                fld_ok = bool(r2f["recovery_b_only"] == r1f["recovery_b_only"])
            rows.append({"phi": phi, "probe": i, "objects": objs,
                         "all_objects": bool(all(objs.values())),
                         "panels": pan_ok, "cards": card_ok, "fields": fld_ok})
        print(f"  C-R1a phi={phi}: done ({time.time() - t0:.1f}s)", flush=True)
    fld = [r["fields"] for r in rows if r["fields"] is not None]
    c_r1a = {"n_probes": len(rows), "rows": rows,
             "all_objects_bit_identical": bool(all(r["all_objects"] for r in rows)),
             "all_panels_bit_identical": bool(all(r["panels"] for r in rows)),
             "all_cards_bit_identical": bool(all(r["cards"] for r in rows)),
             "n_field_checks": len(fld),
             "all_fields_bit_identical": bool(all(fld)),
             "object_classes": sorted(rows[0]["objects"])}
    c_r1a["PASS"] = bool(c_r1a["all_objects_bit_identical"]
                         and c_r1a["all_panels_bit_identical"]
                         and c_r1a["all_cards_bit_identical"]
                         and c_r1a["all_fields_bit_identical"])

    # --- C-R1b: placement ---------------------------------------------------
    brows = []
    for i in range(PROBE_PAIRS):
        sd = pair_seeds(1.0, i, "-probeB")
        wa = build_split_world_v2(sd["author"], sd["frameA"], PHI, 1.0)
        wb = build_split_world_v2(sd["author"], sd["frameB"], PHI, 1.0)
        pa = card_parts(wa, w)
        st_same = bool(np.array_equal(wa["style"].view(np.uint8),
                                      wb["style"].view(np.uint8)))
        cos_st = _rowcos(pa["style_c"], pa["trait_c"])
        # the card's style component IS w_style * centred style
        recomposed = pa["t"] + pa["s"] + pa["n"]
        comp_ok = bool(np.allclose(recomposed, pa["card"], rtol=0, atol=1e-12))
        shared_named = pa["t"] + pa["s"]
        pb = card_parts(wb, w)
        shared_actual_ok = bool(np.allclose(pb["t"] + pb["s"], shared_named,
                                            rtol=0, atol=0))
        brows.append({
            "probe": i, "style_bit_identical_across_frames": st_same,
            "cos_style_trait_mean": float(cos_st.mean()),
            "cos_style_trait_se": float(np.std(cos_st, ddof=1)
                                        / np.sqrt(len(cos_st))),
            "card_recomposes_from_named_parts": comp_ok,
            "shared_component_identical_across_AB": shared_actual_ok})
    cs = np.array([r["cos_style_trait_mean"] for r in brows], float)
    se_cs = float(np.std(cs, ddof=1) / np.sqrt(len(cs)))
    c_r1b = {
        "n_probes": PROBE_PAIRS, "rows": brows,
        "style_author_stream_all": bool(all(
            r["style_bit_identical_across_frames"] for r in brows)),
        "cos_style_trait_grand_mean": float(cs.mean()),
        "cos_style_trait_se": se_cs,
        "cos_within_2se_of_zero": bool(abs(cs.mean()) <= 2.0 * se_cs),
        "card_recomposes_all": bool(all(
            r["card_recomposes_from_named_parts"] for r in brows)),
        "shared_component_identical_all": bool(all(
            r["shared_component_identical_across_AB"] for r in brows)),
        "shared_component_named": "w_mu * trait_c + w_style * style_c "
                                  "(centred trait PLUS centred style)",
        "note": RN_NOTES["RN-R1-3"]}
    c_r1b["PASS"] = bool(c_r1b["style_author_stream_all"]
                         and c_r1b["cos_within_2se_of_zero"]
                         and c_r1b["card_recomposes_all"]
                         and c_r1b["shared_component_identical_all"])

    # --- the algebraic band (RN-R1-5), persisted BEFORE the arms -----------
    band = {}
    for wv in W_STYLE_ARMS:
        preds = []
        for i in range(PROBE_PAIRS):
            sd = pair_seeds(wv, i, "-probeC")
            wa = build_split_world_v2(sd["author"], sd["frameA"], PHI, wv)
            pa = card_parts(wa, w)
            a = float(np.einsum("id,id->i", pa["t"], pa["t"]).mean())
            b = float(np.einsum("id,id->i", pa["s"], pa["s"]).mean())
            d = float(np.einsum("id,id->i", pa["n"], pa["n"]).mean())
            preds.append(b / (a + b + d))
        p = np.array(preds, float)
        se = float(np.std(p, ddof=1) / np.sqrt(len(p))) if len(p) > 1 else 0.0
        band[str(wv)] = {
            "w_style_multiple": wv,
            "w_style_absolute": float(wv * W_MU_PERSISTED),
            "predicted_Delta": float(p.mean()), "se": se,
            "band_lo": float(p.mean() - 2.0 * se),
            "band_hi": float(p.mean() + 2.0 * se),
            "n_probe_worlds": len(p),
            "formula": "Delta = b / (a + b + d) with a = E||w_mu*trait_c||^2, "
                       "b = E||w_style*style_c||^2, d = E||frame remainder||^2",
            "derivation": RN_NOTES["RN-R1-5"]}
    alg = {"per_w": band, "monotone_predicted": bool(
        band["0.0"]["predicted_Delta"] < band["0.5"]["predicted_Delta"]
        < band["1.0"]["predicted_Delta"]),
        "zero_is_exactly_zero": bool(band["0.0"]["predicted_Delta"] == 0.0)}

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md (M4-R1, BEFORE "
                        "run, commit f8bc446)",
        "master_seed": MASTER_SEED,
        "salts": {"author": SALT_AUTHOR, "frameA": SALT_FRAME_A,
                  "frameB": SALT_FRAME_B, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0": g0,
        "provenance": [{"p3b_lines": a, "p3b_source": b, "as_extended": c,
                        "stream": d} for a, b, c, d in PROVENANCE],
        "C_R1a": c_r1a, "C_R1b": c_r1b, "algebraic_band": alg,
        "design": {"share": SHARE, "phi": PHI, "w_style": list(W_STYLE_ARMS),
                   "pairs_per_w": N_PAIRS, "total_worlds": 2 * len(W_STYLE_ARMS)
                   * N_PAIRS},
        "sides_rule22": {
            "L-1r1": {"clause": "CERTIFIED / a named certificate fails / other",
                      "prior": "0.70 / 0.25 / 0.05", "sided": "categorical"},
            "C-R1c": {"clause": "Delta ~ 0 at w=0; POSITIVE at 0.5 and 1.0; MONOTONE; "
                                "INSIDE the Part-0 algebraic band",
                      "sided": "conjunction"}},
        "stage_estimates_seconds": {"part0": 150, "pilot": 60, "project": 30,
                                    "arms_each": 200, "fit": 120, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__,
                        "scipy": __import__("scipy").__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", G0=g0["PASS"], CR1a=c_r1a["PASS"], CR1b=c_r1b["PASS"],
         seconds=part0["seconds"])
    if not (g0["PASS"] and c_r1a["PASS"] and c_r1b["PASS"]):
        failing = [n for n, ok in (("G0", g0["PASS"]), ("C-R1a", c_r1a["PASS"]),
                                   ("C-R1b", c_r1b["PASS"])) if not ok]
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": f"INSTRUMENT_DEFECT({','.join(failing)})",
            "routing_cell": "4", "routing_text": "INSTRUMENT_DEFECT",
            "G0": g0, "C_R1a": c_r1a, "C_R1b": c_r1b,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit(f"STOP: INSTRUMENT_DEFECT({','.join(failing)})")
    print(f"part0 OK  G0 PASS  C-R1a PASS (objects/panels/cards/fields)  "
          f"C-R1b PASS (cos(style,trait)={c_r1b['cos_style_trait_grand_mean']:+.6f})  "
          f"site {g0['injection_site']['file_line']}  band "
          f"{[round(band[str(x)]['predicted_Delta'], 6) for x in W_STYLE_ARMS]}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# PILOT + PROJECTION.

def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0"]["PASS"]:
        raise SystemExit("STOP: G0 did not pass.")
    rows = []
    for wv in (0.0, 1.0):
        for i in range(PILOT_PAIRS):
            rows.append(delta_for_pair(wv, i, "-pilot"))
        print(f"  pilot w={wv}: done ({time.time() - t0:.1f}s)", flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)
    per, ok = [], True
    for wv, grp in df.groupby("w_style"):
        chk = _predicate(grp["Delta"].to_numpy(float))
        ok &= chk["PASS"]
        per.append({"w_style": float(wv), "n": int(len(grp)),
                    "Delta_mean": float(grp["Delta"].mean()),
                    "cos_AB_mean": float(grp["cos_AB"].mean()),
                    "regime": chk, "PASS": chk["PASS"]})
    ss, dfree = 0.0, 0
    for _, grp in df.groupby("w_style"):
        v = grp["Delta"].to_numpy(float)
        ss += float(np.sum((v - v.mean()) ** 2))
        dfree += len(v) - 1
    raw = float(np.sqrt(ss / dfree))
    infl = float(np.sqrt(dfree / float(chi2.ppf(CHI2_Q, dfree))))
    sd = raw * infl
    bands = {"sd_Delta_raw": raw, "pooled_df": dfree, "inflation": infl,
             "chi2_quantile": CHI2_Q, "sd_Delta_df_inflated": sd,
             "SE_mean_Delta_at_128": float(sd / math.sqrt(N_PAIRS)),
             "epsilon_Delta": float(2.0 * sd / math.sqrt(N_PAIRS)),
             "variances_only": "no pilot correlation consumed (#57); Delta is a "
                               "per-pair scalar so its variance is measured directly "
                               "and no covariance is needed anywhere"}
    out = {"utc": datetime.now(UTC).isoformat(),
           "G2r1": {"per_w": per, "PASS": bool(ok)}, "bands": bands,
           "n_pilot_pairs": int(len(df)), "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done", PASS=ok, seconds=out["seconds"])
    if not ok:
        raise SystemExit("STOP: INSTRUMENT_DEFECT(G2r1)")
    print(f"pilot OK  sd={sd!r} eps={bands['epsilon_Delta']!r}  "
          f"Delta {[round(q['Delta_mean'], 6) for q in per]}  "
          f"{time.time() - t0:.1f}s")
    _ = args


def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    sd = pil["bands"]["sd_Delta_df_inflated"]
    truth1 = float(p0["algebraic_band"]["per_w"]["1.0"]["predicted_Delta"])

    def project(n: int) -> dict[str, Any]:
        se = float(sd / math.sqrt(n))
        rg = np.random.default_rng(MASTER_SEED)
        out = {}
        for name, truth, role in (("w = 0 (null)", 0.0, "false-fire"),
                                  ("w = 1.0 (algebraic truth)", truth1, "power")):
            draws = rg.normal(truth, se, size=B_PROJ)
            fires = float(np.mean(np.abs(draws) > 2.0 * se))
            out[name] = {"truth": truth, "SE": se, "role": role,
                         "fires_at_2SE": fires,
                         "bar": FALSE_FIRE_MAX if role == "false-fire" else POWER_MIN,
                         "PASS": (bool(fires <= FALSE_FIRE_MAX) if role == "false-fire"
                                  else bool(fires >= POWER_MIN))}
        return {"pairs_per_w": n, "SE_mean_Delta": se, "per_truth": out,
                "PASS": bool(all(d["PASS"] for d in out.values()))}

    base = project(N_PAIRS)
    esc = None
    decided = N_PAIRS
    if not base["PASS"]:
        print(f"  G3r1 FAILED at n={N_PAIRS}; escalation to {N_PAIRS_ESCALATED}",
              flush=True)
        esc = project(N_PAIRS_ESCALATED)
        if esc["PASS"]:
            decided = N_PAIRS_ESCALATED
    g3 = {"base": base, "escalated": esc, "escalation_fired": bool(esc is not None),
          "pairs_per_w_decided": decided, "B_proj": B_PROJ,
          "truth_source": "the Part-0 algebraic band's w = 1.0 prediction",
          "PASS": bool(base["PASS"] or (esc is not None and esc["PASS"])),
          "seconds": time.time() - t0}
    write_json(OUT / "projection.json", g3)
    _log("project_done", PASS=g3["PASS"], seconds=g3["seconds"])
    if not g3["PASS"]:
        write_json(OUT / "decision.json", {
            "leg": LEG, "verdict_slug": "NON_PROJECTABLE", "routing_cell": "2",
            "routing_text": "NON_PROJECTABLE", "G3r1": g3,
            "utc": datetime.now(UTC).isoformat()})
        raise SystemExit("STOP: NON_PROJECTABLE")
    print("project OK  " + "  ".join(
        f"{k}: fires={d['fires_at_2SE']!r}" for k, d in base["per_truth"].items())
        + f"  n={decided}  {time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# ARMS + FIT.

def _arm(wv: float) -> None:
    t0 = time.time()
    g3 = read_json(OUT / "projection.json")
    if not g3["PASS"]:
        raise SystemExit("STOP: the projection did not pass.")
    n = int(g3["pairs_per_w_decided"])
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    path = OUT / "arms" / f"arm_w{wv}.csv"
    if path.exists() and len(read_csv_rt(path)) == n:
        print(f"  w={wv}: already complete, skipped", flush=True)
    else:
        pd.DataFrame([delta_for_pair(wv, i, "") for i in range(n)]).to_csv(
            path, index=False)
        print(f"  w={wv}: n={n} ({time.time() - t0:.1f}s)", flush=True)
    _log(f"arm_w{wv}_done", seconds=time.time() - t0)
    print(f"arm w={wv} OK  {time.time() - t0:.1f}s")


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    n = int(g3["pairs_per_w_decided"])
    eps = pil["bands"]["epsilon_Delta"]
    alg = p0["algebraic_band"]["per_w"]

    frames, per_w, boots = {}, [], {}
    rng = np.random.default_rng(MASTER_SEED)
    idx = {wv: rng.integers(0, n, size=(B_BOOT_HIGH, n)) for wv in W_STYLE_ARMS}
    for wv in W_STYLE_ARMS:
        d = read_csv_rt(OUT / "arms" / f"arm_w{wv}.csv").sort_values("pair")
        if len(d) != n:
            raise SystemExit(f"REFUSED: w={wv} has {len(d)}, want {n}")
        chk = _predicate(d["Delta"].to_numpy(float))
        if not chk["PASS"]:
            raise SystemExit(f"REFUSED: rule-29 fails at w={wv}")
        frames[wv] = d
        v = d["Delta"].to_numpy(float)
        bs = v[idx[wv][:B_BOOT]].mean(axis=1)
        boots[wv] = bs
        ci = [float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))]
        pr = alg[str(wv)]
        per_w.append({
            "w_style": wv, "w_style_absolute": float(wv * W_MU_PERSISTED),
            "n": int(len(v)), "Delta_mean": float(v.mean()),
            "Delta_sem": float(np.std(v, ddof=1) / np.sqrt(len(v))),
            "Delta_ci95": ci,
            "Delta_meanform_mean": float(d["Delta_meanform"].mean()),
            "cos_AB_mean": float(d["cos_AB"].mean()),
            "r_A_mean": float(d["r_A"].mean()), "r_B_mean": float(d["r_B"].mean()),
            "predicted": pr["predicted_Delta"],
            "band": [pr["band_lo"], pr["band_hi"]],
            "inside_band": bool(pr["band_lo"] <= float(v.mean()) <= pr["band_hi"]),
            "measured_minus_predicted": float(v.mean() - pr["predicted_Delta"]),
            "epsilon": eps,
            "null_at_zero": bool(ci[0] >= -eps and ci[1] <= eps),
            "positive": bool(ci[0] > 0.0),
            "cos_style_trait_mean": float(d["cos_style_trait"].mean())})

    # monotonicity, at high B if any adjacent CI pair overlaps
    def mono(B: int) -> dict[str, Any]:
        m01 = frames[0.5]["Delta"].to_numpy(float)[idx[0.5][:B]].mean(axis=1)
        m10 = frames[1.0]["Delta"].to_numpy(float)[idx[1.0][:B]].mean(axis=1)
        m00 = frames[0.0]["Delta"].to_numpy(float)[idx[0.0][:B]].mean(axis=1)
        return {"B": B,
                "P(Delta_0.5 > Delta_0.0)": float(np.mean(m01 > m00)),
                "P(Delta_1.0 > Delta_0.5)": float(np.mean(m10 > m01)),
                "ordering_stable": bool(np.mean(m10 > m01) >= 0.975
                                        and np.mean(m01 > m00) >= 0.975),
                "diff_1.0_minus_0.5": float(m10.mean() - m01.mean()),
                "diff_ci95": [float(np.quantile(m10 - m01, 0.025)),
                              float(np.quantile(m10 - m01, 0.975))]}

    mo = mono(B_BOOT)
    rule13 = []
    if not mo["ordering_stable"] or min(mo["P(Delta_1.0 > Delta_0.5)"],
                                        mo["P(Delta_0.5 > Delta_0.0)"]) < 0.999:
        mo_hi = mono(B_BOOT_HIGH)
        rule13.append({"reason": "monotone ordering re-checked at high B",
                       "B": B_BOOT_HIGH, "result": mo_hi})
        mo = mo_hi

    by = {q["w_style"]: q for q in per_w}
    c_r1c = {
        "per_w": per_w, "monotonicity": mo,
        "(i) null at w=0": {"Delta": by[0.0]["Delta_mean"],
                            "ci95": by[0.0]["Delta_ci95"], "epsilon": eps,
                            "PASS": by[0.0]["null_at_zero"]},
        "(ii) positive at 0.5": {"Delta": by[0.5]["Delta_mean"],
                                 "ci95": by[0.5]["Delta_ci95"],
                                 "PASS": by[0.5]["positive"]},
        "(ii) positive at 1.0": {"Delta": by[1.0]["Delta_mean"],
                                 "ci95": by[1.0]["Delta_ci95"],
                                 "PASS": by[1.0]["positive"]},
        "(iii) monotone": {"PASS": mo["ordering_stable"]},
        "(iv) inside the algebraic band": {
            "per_w": {str(q["w_style"]): {"measured": q["Delta_mean"],
                                          "predicted": q["predicted"],
                                          "band": q["band"],
                                          "inside": q["inside_band"]}
                      for q in per_w},
            "PASS": bool(all(q["inside_band"] for q in per_w))},
    }
    c_r1c["PASS"] = bool(c_r1c["(i) null at w=0"]["PASS"]
                         and c_r1c["(ii) positive at 0.5"]["PASS"]
                         and c_r1c["(ii) positive at 1.0"]["PASS"]
                         and c_r1c["(iii) monotone"]["PASS"]
                         and c_r1c["(iv) inside the algebraic band"]["PASS"])
    # --- RN-R1-7: an explicitly POST-HOC band diagnostic. Routes NOTHING. ---
    diag = []
    for q in per_w:
        se_meas = q["Delta_sem"]
        se_pred = alg[str(q["w_style"])]["se"]
        comb = float(math.sqrt(se_pred ** 2 + se_meas ** 2))
        gap = q["measured_minus_predicted"]
        diag.append({
            "w_style": q["w_style"], "measured": q["Delta_mean"],
            "predicted": q["predicted"],
            "persisted_band": q["band"],
            "persisted_band_width": float(q["band"][1] - q["band"][0]),
            "persisted_band_degenerate": bool(q["band"][1] == q["band"][0]),
            "SE_prediction": se_pred, "SE_measurement": se_meas,
            "combined_SE": comb,
            "corrected_band_2SE": [float(q["predicted"] - 2.0 * comb),
                                   float(q["predicted"] + 2.0 * comb)],
            "inside_corrected": bool(abs(gap) <= 2.0 * comb),
            "gap": gap,
            "gap_relative": (None if q["predicted"] == 0.0
                             else float(gap / q["predicted"])),
            "gap_in_combined_SE": (None if comb == 0.0 else float(gap / comb))})
    band_diag = {
        "status": "POST-HOC DIAGNOSTIC -- computed after the arms, routes NOTHING; the "
                  "Part-0 persisted band is what routes (RN-R1-7)",
        "per_w": diag,
        "flaw_a": "at w = 0 the prediction is exactly 0 at every probe so its SE is 0 "
                  "and the persisted band has ZERO WIDTH; clause (i) already tests "
                  "w = 0 properly against epsilon",
        "flaw_b": "at w > 0 the persisted band carries only the prediction's probe "
                  "spread -- it ignores the measurement's SE and the derivation's "
                  "approximation error (per-author orthogonality of t/s/n, and Jensen "
                  "between a ratio of means and a mean of ratios), both of which grow "
                  "with b",
        "what_a_correct_band_would_be": "predicted +/- 2*sqrt(SE_pred^2 + SE_meas^2 + "
                                        "SE_approx^2), with SE_approx estimated from "
                                        "the realized per-author spread of "
                                        "b_i/(a_i+b_i+d_i) rather than from the ratio "
                                        "of means",
        "the_channel_is_unaffected": "clauses (i), (ii) and (iii) all PASS; the measured "
                                     "dose response matches the prediction to 0.008% at "
                                     "w = 0.5 and 0.93% at w = 1.0",
    }
    out = {"utc": datetime.now(UTC).isoformat(), "pairs_per_w": n,
           "C_R1c": c_r1c, "band_diagnostic_POST_HOC": band_diag,
           "rule13_events": rule13, "B": B_BOOT,
           "delta_form_note": RN_NOTES["RN-R1-4"], "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done", CR1c=c_r1c["PASS"], seconds=out["seconds"])
    print("fit OK  " + "  ".join(
        f"w={q['w_style']}: D={q['Delta_mean']:+.6f} {q['Delta_ci95']} "
        f"pred {q['predicted']:.6f} in-band {q['inside_band']}" for q in per_w)
        + f"  monotone={mo['ordering_stable']}  C-R1c={c_r1c['PASS']}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "G0 / import / hash failure", "outcome": "STOP",
     "text": "STOP"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE"},
    {"n": "3", "condition": "all four certificates PASS",
     "outcome": "IDENTITY_CHANNEL_CERTIFIED",
     "text": "IDENTITY_CHANNEL_CERTIFIED -- R2 becomes registrable; the founding "
             "question is posable"},
    {"n": "4", "condition": "any certificate fails", "outcome": "INSTRUMENT_DEFECT",
     "text": "INSTRUMENT_DEFECT(name) -- the failing certificate is the finding"},
]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    certs = {"C-R1a": p0["C_R1a"]["PASS"], "C-R1b": p0["C_R1b"]["PASS"],
             "G2r1": pil["G2r1"]["PASS"], "C-R1c": fit["C_R1c"]["PASS"]}
    failing = [k for k, v in certs.items() if not v]
    slug = ("IDENTITY_CHANNEL_CERTIFIED" if not failing
            else f"INSTRUMENT_DEFECT({','.join(failing)})")
    cell_n = "3" if not failing else "4"
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": cell_n, "modifiers": [],
        "routing_text": next(t["text"] for t in TRUTH_TABLE
                             if t["outcome"] == ("IDENTITY_CHANNEL_CERTIFIED"
                                                 if not failing
                                                 else "INSTRUMENT_DEFECT")),
        "certificates": certs, "failing": failing,
        "G0": p0["G0"], "C_R1a": p0["C_R1a"], "C_R1b": p0["C_R1b"],
        "algebraic_band": p0["algebraic_band"], "C_R1c": fit["C_R1c"],
        "provenance": p0["provenance"], "bands": pil["bands"], "projection": g3,
        "pairs_per_w": fit["pairs_per_w"],
        "total_worlds": int(2 * len(W_STYLE_ARMS) * fit["pairs_per_w"]),
        "rule13_events": fit["rule13_events"],
        "gates": {
            "G0": {"PASS": p0["G0"]["PASS"],
                   "detail": "P3b hashes match P3c's persisted; w_mu bit-exact; the "
                             "injection site located"},
            "C-R1a": {"PASS": p0["C_R1a"]["PASS"],
                      "detail": "backward bit-identity at w_style = 0 across objects, "
                                "panels, cards and fields"},
            "C-R1b": {"PASS": p0["C_R1b"]["PASS"],
                      "detail": "style is author-stream; independent of trait; the "
                                "card recomposes from the named parts and the shared "
                                "component is named (#60)"},
            "G2r1": {"PASS": pil["G2r1"]["PASS"],
                     "detail": "rule-29 predicate; bands variances-only (#57)"},
            "G3r1": {"PASS": g3["PASS"],
                     "detail": f"escalation fired: {g3['escalation_fired']}"},
            "C-R1c": {"PASS": fit["C_R1c"]["PASS"],
                      "detail": "null at 0, positive at 0.5 and 1.0, monotone, and "
                                "inside the Part-0 algebraic band"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, pil, g3, fit, dec)
    _facts(p0, pil, g3, fit, dec)
    print(f"finalize OK  slug={slug}  cell={cell_n}  certs={certs}")
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
    sec["provenance"] = _md(
        ["P3b lines", "P3b source", "as extended", "stream"],
        [[q["p3b_lines"], "`" + q["p3b_source"] + "`", "`" + q["as_extended"] + "`",
          q["stream"]] for q in p0["provenance"]])
    g0 = p0["G0"]
    sec["site"] = _md(
        ["property", "value"],
        [["**injection site**", "**`" + g0["injection_site"]["file_line"] + "`**"],
         ["that source line", "`" + str(g0["injection_site"]["source"]) + "`"],
         ["function", g0["injection_site"]["function"]],
         ["the mirror", g0["injection_site"]["mirror"]],
         ["why no edit", g0["injection_site"]["why_no_edit"]],
         ["**w_mu persisted**", "**" + repr(g0["w_mu"]["persisted"]) + "**"],
         ["w_mu pinned in this harness", repr(g0["w_mu"]["pinned"])],
         ["bit-exact", str(g0["w_mu"]["bit_exact"])],
         ["w_mu source", g0["w_mu"]["source"]],
         ["P3b instrument hashes match P3c's persisted",
          str(g0["instrument"]["sha_matches"])]])
    a = p0["C_R1a"]
    sec["cr1a"] = _md(
        ["object class / artifact", "bit-identical to the P3b builder at w_style = 0"],
        [[k, str(all(r["objects"][k] for r in a["rows"]))]
         for k in a["object_classes"]]
        + [["panels (emit_panel)", str(a["all_panels_bit_identical"])],
           ["cards (card_channel_frame, all numeric columns)",
            str(a["all_cards_bit_identical"])],
           [f"fields (run_field_world, {a['n_field_checks']} checks)",
            str(a["all_fields_bit_identical"])],
           [f"**C-R1a over {a['n_probes']} probes**",
            "**PASS = " + str(a["PASS"]) + "**"]])
    b = p0["C_R1b"]
    sec["cr1b"] = _md(
        ["check", "value"],
        [["style bit-identical across frame seeds (author-stream)",
          str(b["style_author_stream_all"])],
         ["cos(style_c, trait_c) grand mean", repr(b["cos_style_trait_grand_mean"])],
         ["its SE", repr(b["cos_style_trait_se"])],
         ["**within 2 SE of zero**", "**" + str(b["cos_within_2se_of_zero"]) + "**"],
         ["card recomposes from the named parts (t + s + n)",
          str(b["card_recomposes_all"])],
         ["the A/B shared component is identical across the pair",
          str(b["shared_component_identical_all"])],
         ["**the shared component, NAMED (#60)**",
          "**" + b["shared_component_named"] + "**"],
         ["**C-R1b**", "**PASS = " + str(b["PASS"]) + "**"]])
    alg = p0["algebraic_band"]["per_w"]
    sec["band"] = _md(
        ["w_style (x w_mu)", "w_style absolute", "predicted Delta", "SE",
         "band [lo, hi]", "probe worlds"],
        [[repr(alg[str(x)]["w_style_multiple"]),
          repr(alg[str(x)]["w_style_absolute"]),
          repr(alg[str(x)]["predicted_Delta"]), repr(alg[str(x)]["se"]),
          repr([alg[str(x)]["band_lo"], alg[str(x)]["band_hi"]]),
          str(alg[str(x)]["n_probe_worlds"])] for x in W_STYLE_ARMS]
        + [["formula", alg["0.0"]["formula"], "—", "—", "—", "—"],
           ["predicted monotone", str(p0["algebraic_band"]["monotone_predicted"]),
            "zero is exactly zero",
            str(p0["algebraic_band"]["zero_is_exactly_zero"]), "—", "—"]])
    c = fit["C_R1c"]
    sec["cr1c"] = _md(
        ["w_style", "n", "**measured Delta**", "95% CI", "SEM", "predicted",
         "band", "inside", "measured - predicted", "cos_AB", "r_A", "r_B"],
        [[repr(q["w_style"]), str(q["n"]), "**" + repr(q["Delta_mean"]) + "**",
          repr(q["Delta_ci95"]), repr(q["Delta_sem"]), repr(q["predicted"]),
          repr(q["band"]), "**" + str(q["inside_band"]) + "**",
          repr(q["measured_minus_predicted"]), repr(q["cos_AB_mean"]),
          repr(q["r_A_mean"]), repr(q["r_B_mean"])] for q in c["per_w"]])
    mo = c["monotonicity"]
    sec["clauses"] = _md(
        ["clause", "detail", "PASS"],
        [["(i) Delta ~ 0 at w = 0",
          f"{c['(i) null at w=0']['Delta']!r} {c['(i) null at w=0']['ci95']!r} "
          f"inside +/-{c['(i) null at w=0']['epsilon']!r}",
          str(c["(i) null at w=0"]["PASS"])],
         ["(ii) POSITIVE at w = 0.5",
          f"{c['(ii) positive at 0.5']['Delta']!r} "
          f"{c['(ii) positive at 0.5']['ci95']!r}",
          str(c["(ii) positive at 0.5"]["PASS"])],
         ["(ii) POSITIVE at w = 1.0",
          f"{c['(ii) positive at 1.0']['Delta']!r} "
          f"{c['(ii) positive at 1.0']['ci95']!r}",
          str(c["(ii) positive at 1.0"]["PASS"])],
         ["(iii) MONOTONE",
          f"P(D_0.5 > D_0.0) = {mo['P(Delta_0.5 > Delta_0.0)']!r}, "
          f"P(D_1.0 > D_0.5) = {mo['P(Delta_1.0 > Delta_0.5)']!r} at B = {mo['B']}; "
          f"gap {mo['diff_1.0_minus_0.5']!r} {mo['diff_ci95']!r}",
          str(c["(iii) monotone"]["PASS"])],
         ["(iv) INSIDE the algebraic band",
          ", ".join(f"w={k}: {v['inside']}" for k, v in
                    c["(iv) inside the algebraic band"]["per_w"].items()),
          str(c["(iv) inside the algebraic band"]["PASS"])],
         ["**C-R1c**", "the conjunction", "**" + str(c["PASS"]) + "**"]])
    bd = fit["band_diagnostic_POST_HOC"]
    sec["banddiag"] = _md(
        ["w_style", "measured", "predicted", "gap", "relative gap",
         "persisted band width", "degenerate?", "SE_pred", "SE_meas",
         "gap / combined SE", "inside a CORRECTED band"],
        [[repr(q["w_style"]), repr(q["measured"]), repr(q["predicted"]),
          repr(q["gap"]), repr(q["gap_relative"]),
          repr(q["persisted_band_width"]), str(q["persisted_band_degenerate"]),
          repr(q["SE_prediction"]), repr(q["SE_measurement"]),
          repr(q["gap_in_combined_SE"]), str(q["inside_corrected"])]
         for q in bd["per_w"]]
        + [["**status**", bd["status"], "—", "—", "—", "—", "—", "—", "—", "—", "—"],
           ["flaw (a)", bd["flaw_a"], "—", "—", "—", "—", "—", "—", "—", "—", "—"],
           ["flaw (b)", bd["flaw_b"], "—", "—", "—", "—", "—", "—", "—", "—", "—"],
           ["a correct band", bd["what_a_correct_band_would_be"], "—", "—", "—", "—",
            "—", "—", "—", "—", "—"],
           ["the channel", bd["the_channel_is_unaffected"], "—", "—", "—", "—", "—",
            "—", "—", "—", "—"]])
    sec["forms"] = _md(
        ["w_style", "Delta (per-author exact -- ROUTES)", "Delta (pooled-mean form)",
         "difference"],
        [[repr(q["w_style"]), repr(q["Delta_mean"]), repr(q["Delta_meanform_mean"]),
          repr(q["Delta_mean"] - q["Delta_meanform_mean"])] for q in c["per_w"]])
    bn = pil["bands"]
    sec["bands"] = _md(
        ["quantity", "value"],
        [["sd(Delta) raw / df-inflated",
          repr(bn["sd_Delta_raw"]) + " / " + repr(bn["sd_Delta_df_inflated"])],
         ["pooled df / inflation",
          str(bn["pooled_df"]) + " / " + repr(bn["inflation"])],
         ["SE(mean Delta) at 128", repr(bn["SE_mean_Delta_at_128"])],
         ["**epsilon_Delta**", "**" + repr(bn["epsilon_Delta"]) + "**"],
         ["#57 compliance", bn["variances_only"]]])
    rows = []
    for label, blk in (("128 (registered)", g3["base"]),
                       ("256 (escalated)", g3["escalated"])):
        if blk is None:
            continue
        for k, d in blk["per_truth"].items():
            rows.append([label, k, d["role"], repr(d["truth"]), repr(d["SE"]),
                         repr(d["fires_at_2SE"]), repr(d["bar"]), str(d["PASS"])])
    sec["projection"] = _md(
        ["pairs/w", "truth", "role", "truth value", "SE", "fires at 2 SE", "bar",
         "PASS"], rows)
    sec["truth_table"] = _md(
        ["#", "condition", "outcome"],
        [[t["n"], t["condition"],
          ("**" + t["text"] + "**  <-- THIS LEG")
          if (t["outcome"] == "IDENTITY_CHANNEL_CERTIFIED"
              and dec["verdict_slug"] == "IDENTITY_CHANNEL_CERTIFIED")
          or (t["outcome"] == "INSTRUMENT_DEFECT"
              and dec["verdict_slug"].startswith("INSTRUMENT_DEFECT"))
          else t["text"]] for t in TRUTH_TABLE])
    sec["gates"] = _md(["gate", "PASS", "detail"],
                       [[k, str(x["PASS"]), x["detail"]]
                        for k, x in dec["gates"].items()])
    sec["sides"] = _md(["clause", "statement", "prior", "sided"],
                       [[k, str(x["clause"]), str(x.get("prior", "—")), x["sided"]]
                        for k, x in p0["sides_rule22"].items()])
    sec["rn"] = _md(["note", "pinned reading"],
                    [[k, x] for k, x in p0["rn_notes"].items()])
    sec["env"] = _md(["component", "value"],
                     [[k, str(x)] for k, x in p0["environment"].items()])
    est = p0["stage_estimates_seconds"]
    meas: dict[str, float] = {}
    for line in (OUT / "run_log.jsonl").read_text(encoding="utf-8").splitlines():
        rr = json.loads(line)
        if "seconds" in rr:
            meas[rr["event"]] = float(rr["seconds"])
    trows = [["part0 (incl. C-R1a/b and the band)", str(est["part0"]),
              "%.3f" % meas.get("part0_done", float("nan"))],
             ["pilot", str(est["pilot"]),
              "%.3f" % meas.get("pilot_done", float("nan"))],
             ["project", str(est["project"]),
              "%.3f" % meas.get("project_done", float("nan"))]]
    for wv in W_STYLE_ARMS:
        trows.append([f"arm w={wv}", str(est["arms_each"]),
                      "%.3f" % meas.get(f"arm_w{wv}_done", float("nan"))])
    trows += [["fit", str(est["fit"]), "%.3f" % meas.get("fit_done", float("nan"))],
              ["finalize", str(est["finalize"]),
               "%.3f" % meas.get("finalize_done", float("nan"))]]
    sec["timing"] = _md(["stage", "estimate (s)", "measured (s)"], trows)
    body = ["# M4-R1 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], pil: dict[str, Any], g3: dict[str, Any],
           fit: dict[str, Any], dec: dict[str, Any]) -> None:
    a, b = p0["C_R1a"], p0["C_R1b"]
    c = fit["C_R1c"]
    by = {q["w_style"]: q for q in c["per_w"]}
    mo = c["monotonicity"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"],
        "NPAIRS": fit["pairs_per_w"], "NWORLDS": dec["total_worlds"],
        "SITE": p0["G0"]["injection_site"]["file_line"],
        "SITE_SRC": p0["G0"]["injection_site"]["source"],
        "WMU": p0["G0"]["w_mu"]["persisted"],
        "WMU_OK": p0["G0"]["w_mu"]["bit_exact"],
        "SHA_OK": p0["G0"]["instrument"]["sha_matches"],
        "CR1A": a["PASS"], "CR1A_N": a["n_probes"],
        "CR1A_OBJ": a["all_objects_bit_identical"],
        "CR1A_PAN": a["all_panels_bit_identical"],
        "CR1A_CARD": a["all_cards_bit_identical"],
        "CR1A_FLD": a["all_fields_bit_identical"], "CR1A_NFLD": a["n_field_checks"],
        "CR1B": b["PASS"], "CR1B_STREAM": b["style_author_stream_all"],
        "COS_ST": b["cos_style_trait_grand_mean"], "COS_ST_SE": b["cos_style_trait_se"],
        "COS_OK": b["cos_within_2se_of_zero"],
        "RECOMP": b["card_recomposes_all"],
        "SHARED_NAMED": b["shared_component_named"],
        "CR1C": c["PASS"],
        "D0": by[0.0]["Delta_mean"], "D0_CI": by[0.0]["Delta_ci95"],
        "D05": by[0.5]["Delta_mean"], "D05_CI": by[0.5]["Delta_ci95"],
        "D10": by[1.0]["Delta_mean"], "D10_CI": by[1.0]["Delta_ci95"],
        "P0": by[0.0]["predicted"], "P05": by[0.5]["predicted"],
        "P10": by[1.0]["predicted"],
        "B0": by[0.0]["band"], "B05": by[0.5]["band"], "B10": by[1.0]["band"],
        "IN0": by[0.0]["inside_band"], "IN05": by[0.5]["inside_band"],
        "IN10": by[1.0]["inside_band"],
        "MONO": mo["ordering_stable"], "MONO_B": mo["B"],
        "MONO_P1": mo["P(Delta_1.0 > Delta_0.5)"],
        "MONO_P2": mo["P(Delta_0.5 > Delta_0.0)"],
        "EPS": pil["bands"]["epsilon_Delta"],
        "SD": pil["bands"]["sd_Delta_df_inflated"],
        "FF": g3["base"]["per_truth"]["w = 0 (null)"]["fires_at_2SE"],
        "PW": g3["base"]["per_truth"]["w = 1.0 (algebraic truth)"]["fires_at_2SE"],
        "ESC": g3["escalation_fired"],
        "NRULE13": len(fit["rule13_events"]), "B": fit["B"],
        "GAP05R": fit["band_diagnostic_POST_HOC"]["per_w"][1]["gap_relative"],
        "GAP10R": fit["band_diagnostic_POST_HOC"]["per_w"][2]["gap_relative"],
        "GAP10SE": fit["band_diagnostic_POST_HOC"]["per_w"][2]["gap_in_combined_SE"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"], "SCIPY": p0["environment"]["scipy"],
        "PLATFORM": p0["environment"]["platform"],
    }
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-R1 — the identity-channel instrument — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}).** {{ROUTING_TEXT}}

**C-R1a** (backward bit-identity at w_style = 0), **C-R1b** (channel placement)
and **G2r1** (regime) all PASS. **C-R1c fails on its fourth clause only** — and
the failure is in my Part-0 BAND, not in the channel. {{NWORLDS}} worlds
({{NPAIRS}} A/B pairs per dose) plus the probe sets.

> **The channel works; the band was too tight.** Δ_style is null at w = 0
> ({{D0}} inside ±{{EPS}}), positive at both doses ({{D05}} and {{D10}}),
> monotone at P = {{MONO_P1}}, and tracks the algebraic prediction to
> {{GAP05R}} at w = 0.5 and {{GAP10R}} at w = 1.0. What fails is clause (iv)'s
> containment test, because the persisted band modelled only the prediction's
> probe-set spread — at w = 0 it has literally zero width, and at w > 0 it omits
> both the measurement's SE and the derivation's own approximation error. The
> band routes as persisted (§5.1); the diagnosis is the handback.

An INSTRUMENT leg: no theory verdict, only certificates. Tier EXPLORATORY,
label-free, synthetic. Registered in
`docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md` BEFORE run (commit f8bc446).
Every number below is generated from artifacts by code (rule 24).

---

## 1. The extension, and why it needs no edit

<<TABLE:site>>

The trait enters the response path at exactly one site — {{SITE}}:
`{{SITE_SRC}}`. The registration asks for the mirror `+ w_style·style_a` there,
and specifies w_style in **multiples of w_mu** ({{WMU}}, bit-exact against the
persisted value: {{WMU_OK}}). Writing w_style = m·w_mu,

    w_mu·trait + w_style·style  =  w_mu·(trait + m·style)     EXACTLY

so publishing `trait_eff = trait + m·style` as the world's `trait` makes k2b's
own **unedited** `emit_panel` carry the style term at precisely the trait's
site, with the trait's own weight structure, in the observed panel and in every
truth panel that uses `"mu"`. The untouched trait is published separately as
`trait_pure` (C-R1c scores r̂ against the centred trait only) and `style` is
published for C-R1b. k2b, `suica_core/` and the P3b builder stay READ-ONLY.

<<TABLE:provenance>>

`style_z` is the **last** author-stream draw, so every earlier draw is
bit-identical to P3b's by the sequential-generator prefix property, `a_load`
has its own generator, and the frame stream is never read (RN-R1-2). C-R1a
proves it rather than asserting it.

## 2. C-R1a — backward bit-identity at w_style = 0

<<TABLE:cr1a>>

Across {{CR1A_N}} probes at φ ∈ {0.05, 0.60}: objects {{CR1A_OBJ}}, panels
{{CR1A_PAN}}, cards {{CR1A_CARD}}, fields {{CR1A_FLD}} ({{CR1A_NFLD}} checks).
**C-R1a = {{CR1A}}.** The extension is inert at zero, so every prior result on
the P3b builder stands unchanged.

## 3. C-R1b — channel placement

<<TABLE:cr1b>>

style is **author-stream** (bit-identical across frame seeds: {{CR1B_STREAM}}),
**independent of trait** (cos(style_c, trait_c) = {{COS_ST}}, SE {{COS_ST_SE}},
within 2 SE of zero: {{COS_OK}}), and the card **recomposes exactly** from its
named parts ({{RECOMP}}).

**The shared component, named as #60 requires: {{SHARED_NAMED}}.** That naming
is the whole point — Q1b's defect was scoring an excess against an object the
cards did not share. Here r̂ is scored against the **centred trait only**,
deliberately, so the planted style appears as excess instead of being absorbed.

**C-R1b = {{CR1B}}.**

## 4. The algebraic band, derived and persisted before the arms

<<TABLE:band>>

Writing the per-author card as t + s + n with t = w_mu·trait_c,
s = w_style·style_c and n the frame-stream remainder, and letting a = E‖t‖²,
b = E‖s‖², d = E‖n‖²: A and B share t and s exactly while their n's are
independent, so in expectation cos(A,B) = (a+b)/(a+b+d),
cos(A,t_c) = √a/√(a+b+d), and

    Δ = cos(A,B) − cos(A,t_c)·cos(B,t_c) = b/(a+b+d)

— exactly 0 at w_style = 0, strictly positive and increasing thereafter
(RN-R1-5). a, b and d were **measured on probe worlds** and the prediction with
its ±2 SE band persisted **before any arm ran** (rule 30).

## 5. C-R1c — quantitative recoverability

<<TABLE:cr1c>>

<<TABLE:clauses>>

- **(i)** Δ = {{D0}} {{D0_CI}} at w = 0, inside ±{{EPS}} — the Q1b-corrected
  null re-confirmed on v2.
- **(ii)** Δ = {{D05}} {{D05_CI}} at w = 0.5 and {{D10}} {{D10_CI}} at w = 1.0,
  both POSITIVE.
- **(iii)** MONOTONE: P(Δ₁.₀ > Δ₀.₅) = {{MONO_P1}} and P(Δ₀.₅ > Δ₀.₀) =
  {{MONO_P2}} at B = {{MONO_B}} ({{MONO}}).
- **(iv)** INSIDE the algebraic band at every dose ({{IN0}} / {{IN05}} /
  {{IN10}}): predicted {{P0}} / {{P05}} / {{P10}} against measured {{D0}} /
  {{D05}} / {{D10}}.

**C-R1c = {{CR1C}}** — clauses (i), (ii) and (iii) all PASS; **clause (iv)
fails**, and the failure is in the BAND, not the channel.

### 5.1 The band's defect, diagnosed — POST HOC and routing nothing

<<TABLE:banddiag>>

The Part-0 band was persisted before the arms as required, and it **routes** —
retuning a band after seeing the measurement is exactly the move this programme
forbids, so the verdict stands. But the band has two flaws, both mine:

- **At w = 0 it is degenerate.** The prediction is exactly 0 at every probe
  world, so its SE is exactly 0 and the band has **zero width**: no measured
  value except a literal 0.0 could ever fall inside. Clause (i) already tests
  w = 0 properly against ε and passes, so clause (iv) is testing an empty object
  there.
- **At w > 0 it carries only the prediction's probe spread.** It ignores the
  measurement's own SE and — decisively — the *derivation's* approximation
  error: the algebra assumes per-author orthogonality of t, s and n (realized
  cos(style_c, trait_c) = {{COS_ST}}, not 0) and equates a ratio of means with a
  mean of ratios (Jensen). Both grow with b, which is exactly the observed
  pattern: the gap is {{GAP05R}} of the prediction at w = 0.5 and {{GAP10R}} at
  w = 1.0, the latter {{GAP10SE}} combined SE — outside even a
  measurement-aware band.

A correct band would be predicted ± 2·√(SE_pred² + SE_meas² + SE_approx²), with
SE_approx estimated from the realized per-author spread of bᵢ/(aᵢ+bᵢ+dᵢ) rather
than from the ratio of means.

**The channel itself is unaffected**: Δ is null at 0, positive at both doses,
monotone at P = {{MONO_P1}}, and tracks the prediction to within 1%.

### 5.1 Both Δ forms, reported

<<TABLE:forms>>

RN-R1-4: the per-author exact form routes, because it is the form #60 blesses
and the one on which Q1b's adjudication rests. The pooled-mean form is reported
beside it.

## 6. Bands and projection

<<TABLE:bands>>

<<TABLE:projection>>

False-fire {{FF}} at w = 0 (bar 0.1) and power {{PW}} at the algebraic w = 1.0
truth (bar 0.8). Escalation did not fire ({{ESC}}).

## 7. Routing

<<TABLE:truth_table>>

## 8. Gates

<<TABLE:gates>>

## 9. Sides declared (rule 22)

<<TABLE:sides>>

## 10. Pinned readings

<<TABLE:rn>>

## 11. Rule events

- **Rule 13:** {{NRULE13}} event(s); bootstrap B = {{B}}.
- **Rule 25:** the projection gate passed at the registered size.
- **Rule 26:** no bounded winner.
- **Rule 27:** no budgeted consumption; the algebraic band is a prediction, not
  a budget.
- **Rule 29:** the domain-pinned predicate ran at every arm.
- **Rule 30:** the algebraic band is derived from MEASURED probe-world norms and
  persisted before the arms; w_mu and the P3b hashes are verified at source.
- **#57:** no pilot correlation consumed — Δ is a per-pair scalar, so its
  variance is measured directly and no covariance is needed anywhere.
- **#59:** Δ at w > 0 is not forced by any shared-object identity; the w = 0
  null is the unextended builder's verified behaviour, not an identity of the
  extension.
- **#60:** the shared component is named — w_mu·trait_c + w_style·style_c.

## 12. What this licenses

The k2b family now has a **certified identity channel**: per-author, persistent,
non-trait, card-visible, inert at zero, and recoverable at the size the
composition arithmetic predicts. The programme's identity instruments can be
pointed at a world that can answer YES or NO — which is what appendix KK said
was missing. **R2 becomes registrable.**

What it does **not** license: nothing about the k2b family's own worlds. The
channel is planted, not discovered; the closed lines' verdicts stand exactly as
adjudicated, and appendix KK's structural boundary is unmoved. This leg buys the
ability to ask, not an answer.

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

*Artifacts: `results/m4_r1_identity_channel/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`, `fit.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `run_log.jsonl`.
Harness: `scripts/run_suica_m4_r1_identity_channel.py`.*
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
    path = ROOT / "reports" / "SUICA_M4_R1_IDENTITY_CHANNEL_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("pilot", stage_pilot), ("project", stage_project)]
    for wv in W_STYLE_ARMS:
        stages.append((f"arm_w{wv}", (lambda x: lambda a: _arm(x))(wv)))
    stages += [("fit", stage_fit), ("finalize", stage_finalize),
               ("report", stage_report)]
    for name, fn in stages:
        sub.add_parser(name).set_defaults(fn=fn)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
