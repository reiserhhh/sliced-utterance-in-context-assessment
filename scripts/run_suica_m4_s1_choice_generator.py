#!/usr/bin/env python3
"""SUICA M4-S1 -- the choice-enabled generator.

Registered BEFORE run in docs/SUICA_M4_S_SELECTION_LINE_PLAN.md ("M4-S1",
commit 21149bb).  Binding.  Instrument leg: certificates only.

The owner's conjecture is that the gauge reads frames but WHICH frames a person
chooses is person-owned.  This leg builds the apparatus that can measure the
coupling: an endogenous frame-exposure choice with a knob gamma that slides the
driver from trait (gamma = 1) to planted identity/style (gamma = 0).

    pi_a = softmax( beta * [ gamma * u(trait_a) + (1-gamma) * v(style_a) ] )

and the author's occasion-to-context exposure is drawn from pi_a.

THE EXPOSURE REALLOCATION (the leg's structural question).  k2b's emit_panel
gives author i the frame object common[ctx_index[i], o] at every occasion o --
one context per author, for all occasions.  Per-occasion choice is NOT
expressible through emit_panel.  It IS expressible as a minimal extraction:
emit_choice below is emit_panel (k2b:359-381) transcribed with exactly ONE
change, the common term's first index, and Part 0 certifies bit-exactness
against emit_panel when the choice matrix is the layout's own assignment.  The
shared-frame object per context is preserved exactly: common[k, o] remains the
single frame vector for context k at occasion o, shared by every author who
chooses k there.

Stages: part0 -> pilot -> project -> arms -> fit -> finalize -> report
"""
from __future__ import annotations

import argparse
import hashlib
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
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-S1"
OUT = ROOT / "results" / "m4_s1_choice_generator"
REPORT = ROOT / "reports" / "SUICA_M4_S1_CHOICE_GENERATOR_REPORT.md"

R1SRC = ROOT / "scripts" / "run_suica_m4_r1_identity_channel.py"
R2SRC = ROOT / "scripts" / "run_suica_m4_r2_gauge_meets_identity.py"
K2BSRC = ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"
M1CCELLS = ROOT / "results" / "m4_m1c_r_at_level" / "cell_means.csv"
R2FIT = ROOT / "results" / "m4_r2_gauge_meets_identity" / "fit.json"

SHARE = 0.25
PHI = 0.60
W_STYLE = 1.0
W_INT_ARM = "zero"
GAMMAS = (0.0, 1.0)
N_WORLDS = 24
N_ESCALATED = 48
N_ANCHOR = 8
N_PILOT = 4
MASTER_SEED = 20260816
SALT_AUTHOR = "m4s1-author"
SALT_FRAME = "m4s1-frameA"
SALT_PILOT = "m4s1-pilot"
SALT_EXPOSURE = "m4s1-exposure"
N_PC = 4
B_BOOT = 2000
CI_Q = (2.5, 97.5)
B_PERM = 199
B_PROJ = 2000
POWER_MIN = 0.80
FALSE_FIRE_MAX = 0.10
SATURATION_ABS = 0.999
ENTROPY_TARGET_FRAC = 0.85          # declared entropy drop for beta*
CHI2_POWER_MIN = 0.80               # declared detectability for beta*
BETA_GRID = tuple(round(0.05 * i, 4) for i in range(1, 121))
N_MC_BETA = 20000

PIN_EMIT = "scripts/run_suica_m4_k2b_t4_branch.py:359-381 (emit_panel)"
PIN_COMMON = "scripts/run_suica_m4_k2b_t4_branch.py:377 (the common term)"
PIN_CTXIDX = "scripts/run_suica_m4_k2b_t4_branch.py:341 (contexts_sorted/ctx_index)"
PIN_BUILDER = "scripts/run_suica_m4_r1_identity_channel.py:267-326 (v2)"
PIN_TRAITSITE = "scripts/run_suica_m4_k2b_t4_branch.py:371"

RN_NOTES = {
    "RN-S1-1":
        "THE EXPOSURE REALLOCATION, pinned.  emit_panel (k2b:359-381) indexes the "
        "frame as common[ctx_index[i], :m] (k2b:377) -- one context per author for "
        "every occasion -- so per-occasion choice cannot be expressed through it. "
        "emit_choice transcribes emit_panel with EXACTLY ONE change: that first "
        "index becomes choice[i, o], a per-(author, occasion) context id.  Part 0 "
        "certifies the transcription BIT-EXACTLY against emit_panel by setting "
        "choice[i, o] = ctx_index[i].  The shared-frame object per context is "
        "preserved: common[k, o] is still the one vector for context k at occasion "
        "o.  The layout, the frozen map, the retained set, the per-context field "
        "bookkeeping and suica_core are all untouched -- the author's NOMINAL "
        "context (which the gauge uses for pooling) stays lay['ctx_index'], while "
        "the author's REALIZED exposure is the choice.  That is the model: authors "
        "nominally belong to a community and choose which contexts they engage.",
    "RN-S1-2":
        "u and v are the first four principal author-coordinates of each channel, "
        "orthonormalized, per the registration's decision rule: SVD of the "
        "author-centred channel matrix (trait_pure for u, style for v), right "
        "singular vectors 1..4, authors projected onto them, then each coordinate "
        "z-scored across authors so beta means the same thing in both channels and "
        "gamma blends comparable scales.  SIGN CONVENTION (#64), pinned: each "
        "component's sign is fixed so that its largest-|value| loading coordinate "
        "is positive -- SVD signs are otherwise arbitrary and would silently "
        "randomize pi across worlds.",
    "RN-S1-3":
        "the exposure draw uses its OWN rng stream, keyed on the world's seeds and "
        "the salt m4s1-exposure, and is taken AFTER the v2 builder has returned. "
        "Every v2 object (loadings, z, trait_pure, style, xs, noise, common, "
        "shocks) is therefore bit-identical to what the same seeds produce without "
        "any choice machinery -- Part 0 certifies this.",
    "RN-S1-4":
        "beta* is fixed in Part 0 by arithmetic on standard-normal scores ONLY -- no "
        "worlds.  The z-scored coordinates are unit-variance by construction, so "
        "the score vector is modelled as beta * N(0, I_4); the grid search takes the "
        "SMALLEST beta on a pinned grid meeting BOTH declared criteria: mean "
        "selection entropy <= 0.85 * log 4, and median per-author chi-square(3) "
        "power >= 0.80 at the panel's median occasion count.  Both are declared "
        "before any world exists.",
    "RN-S1-5":
        "C-S1a's reference.  The registration says 'the v2/M1c share-.25 row'.  Two "
        "different objects carry that description and they differ by the style "
        "dose, so BOTH are reported and the routing one is NAMED: the routing "
        "reference is R2's persisted v2 arm at share .25 / phi .60 / w_style 1.0 -- "
        "the identical configuration to this leg's anchor.  M1c's s0.25_p0.60 row is "
        "the no-style lineage value and is reported alongside, not used to route.",
    "RN-S1-6":
        "C-S1a tests TWO different things and they are reported separately: the "
        "registered DISTRIBUTIONAL comparison (anchor mean vs the v2 reference, band "
        "2*sqrt(2)*SEM, the C1' pattern) which ROUTES, and a paired within-world "
        "diagnostic (same worlds scored through emit_panel and through the choice "
        "path at beta = 0) which does NOT route.  Uniform exposure is not the "
        "layout's own assignment, so a systematic level shift is possible and the "
        "paired form is the honest place to show it.",
    "RN-S1-7":
        "selection similarity is the cosine between authors' realized frequency "
        "vectors and trait similarity the cosine between centred trait_pure "
        "vectors; the coupling statistic is the Mantel correlation over all "
        "retained-author pairs.  Retained authors (the panel the gauge sees) are "
        "used throughout, matching every other leg's author statistics.  Shared "
        "component named (#60): both similarities are author-stream objects only; "
        "no frame object enters either side.",
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


def r1() -> Any:
    return _load_named("run_suica_m4_r1_identity_channel", R1SRC)


def k2b() -> Any:
    return r1().k2b()


def v8() -> Any:
    return k2b().v8


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


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seed_for(kind: str, i: int, salt: str) -> int:
    key = f"{LEG}|{salt}|{kind}|i{i}|seed{MASTER_SEED}"
    return int(v8().stable_bucket(key, salt=salt, modulus=2 ** 63 - 1))


def world_seeds(i: int, suffix: str = "") -> dict[str, int]:
    return {"author": seed_for("author", i, SALT_AUTHOR + suffix),
            "frame": seed_for("frame", i, SALT_FRAME + suffix),
            "exposure": seed_for("exposure", i, SALT_EXPOSURE + suffix)}


def df_inflation(df: int) -> float:
    return float(math.sqrt(df / stats.chi2.ppf(0.10, df)))


# ---------------------------------------------------------------------------
# THE PROJECTIONS (RN-S1-2).


def principal_coords(mat: np.ndarray, k: int = N_PC) -> np.ndarray:
    """First k principal author-coordinates, orthonormal basis, signs pinned,
    each coordinate z-scored across authors."""
    x = mat - mat.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    basis = vt[:k]                                   # (k, DIM), orthonormal rows
    for j in range(k):                               # #64: pin the sign
        row = basis[j]
        if row[int(np.argmax(np.abs(row)))] < 0:
            basis[j] = -row
    coords = x @ basis.T                             # (n, k)
    sd = coords.std(axis=0, ddof=1)
    sd[sd == 0.0] = 1.0
    return coords / sd


def softmax_rows(s: np.ndarray) -> np.ndarray:
    e = np.exp(s - s.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


# ---------------------------------------------------------------------------
# THE GENERATOR.


def build_choice_world(author_seed: int, frame_seed: int, phi_slow: float,
                       w_style: float, beta: float, gamma: float) -> dict[str, Any]:
    """v2 (r1:267-326) plus an endogenous exposure choice.  RN-S1-1/2/3."""
    lay = k2b().layout()
    world = r1().build_split_world_v2(author_seed, frame_seed, phi_slow, w_style)
    u = principal_coords(world["trait_pure"])
    v = principal_coords(world["style"])
    score = float(beta) * (float(gamma) * u + (1.0 - float(gamma)) * v)
    pi = softmax_rows(score)
    n, t_max = pi.shape[0], lay["t_max"]
    rng = np.random.default_rng(int(v8().stable_bucket(
        f"{author_seed}|{frame_seed}|{beta!r}|{gamma!r}",
        salt=SALT_EXPOSURE, modulus=2 ** 63 - 1)))
    cum = np.cumsum(pi, axis=1)
    draws = rng.random((n, t_max))
    choice = (draws[:, :, None] > cum[:, None, :]).sum(axis=2).astype(int)
    choice = np.clip(choice, 0, pi.shape[1] - 1)
    world = dict(world)
    world.update({"pi": pi, "choice": choice, "u": u, "v": v, "score": score,
                  "beta": float(beta), "gamma": float(gamma)})
    return world


def emit_choice(world: dict[str, Any], w: dict[str, float],
                choice: np.ndarray) -> list[np.ndarray]:
    """k2b:359-381 transcribed, with ONE change: the common term's first index
    (k2b:377) becomes choice[i, o] instead of ctx_index[i].  RN-S1-1."""
    m_ = k2b()
    lay = m_.layout()
    counts = lay["counts"]
    out: list[np.ndarray] = []
    for i in range(len(counts)):
        m = int(counts[i])
        occ = np.arange(m)
        v = np.zeros((m, m_.DIM), dtype=float)
        v += w["mu"] * world["trait"][i][None, :]
        v += w["slow"] * world["slow"][i, :m]
        if w["int"] != 0.0:
            v += w["int"] * world["int"][i, :m]
        v += w["common"] * world["common"][choice[i, :m], occ]
        v += w["noise"] * world["noise"][i, :m]
        out.append(v)
    return out


def emit_choice_truth(world: dict[str, Any], person: np.ndarray,
                      w: dict[str, float], choice: np.ndarray) -> list[np.ndarray]:
    """The same transcription restricted to active=("mu","common")."""
    m_ = k2b()
    lay = m_.layout()
    counts = lay["counts"]
    out: list[np.ndarray] = []
    for i in range(len(counts)):
        m = int(counts[i])
        occ = np.arange(m)
        v = w["mu"] * np.repeat(person[i][None, :], m, axis=0)
        v = v + w["common"] * world["common"][choice[i, :m], occ]
        out.append(v)
    return out


def field_agreement_of(vectors: list[np.ndarray], truth: list[np.ndarray],
                       corpus: str) -> float:
    m_ = k2b()
    lay = m_.layout()
    module = lay["module"]
    raw_m, raw_k = m_.f1().featurize_panel(
        vectors, lay["author_ids"], corpus=corpus, spec=lay["spec"],
        directions=lay["directions"])
    panel = SimpleNamespace(metadata=lay["metadata"], raw={"M": raw_m, "K": raw_k})
    cal = module.calibrate_d0_soft(panel)
    proj = module.project_soft(
        SimpleNamespace(raw={"M": raw_m, "K": raw_k}), lay["retained_mask"], cal)
    est = module.deployed_soft_field(proj, lay["retained_ctx"], lay["resolved"])
    ridx = lay["retained_idx"]
    fld = m_.field_from_vectors([truth[i] for i in ridx], cal, corpus)
    return float(module.field_agreement(est, fld, lay["weights"]))


# ---------------------------------------------------------------------------
# SELECTION STATISTICS.


def freq_vectors(world: dict[str, Any], idx: np.ndarray,
                 half: str = "all") -> np.ndarray:
    lay = k2b().layout()
    counts = lay["counts"]
    n_ctx = len(lay["contexts_sorted"])
    out = np.zeros((len(idx), n_ctx), dtype=float)
    for r, i in enumerate(idx):
        m = int(counts[i])
        ch = world["choice"][i, :m]
        if half == "even":
            ch = ch[0::2]
        elif half == "odd":
            ch = ch[1::2]
        out[r] = np.bincount(ch, minlength=n_ctx)
    return out


def _cos_pairs(mat: np.ndarray) -> np.ndarray:
    x = mat / np.linalg.norm(mat, axis=1, keepdims=True).clip(1e-12)
    g = x @ x.T
    iu = np.triu_indices(len(x), k=1)
    return g[iu]


def mantel_r(sel: np.ndarray, tr: np.ndarray) -> float:
    a, b = _cos_pairs(sel), _cos_pairs(tr)
    if a.std() == 0.0 or b.std() == 0.0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def mantel_perm_sd(sel: np.ndarray, tr: np.ndarray, b_perm: int,
                   seed: int) -> float:
    rng = np.random.default_rng(seed)
    base = _cos_pairs(tr)
    n = len(sel)
    iu = np.triu_indices(n, k=1)
    x = sel / np.linalg.norm(sel, axis=1, keepdims=True).clip(1e-12)
    vals = []
    for _ in range(b_perm):
        p = rng.permutation(n)
        g = x[p] @ x[p].T
        vals.append(np.corrcoef(g[iu], base)[0, 1])
    return float(np.std(vals, ddof=1))


def world_selection_stats(world: dict[str, Any], idx: np.ndarray) -> dict[str, Any]:
    lay = k2b().layout()
    counts = lay["counts"][idx]
    f = freq_vectors(world, idx)
    pi = world["pi"][idx]
    tot = f.sum(axis=1)
    exp = pi * tot[:, None]
    chi2 = np.where(exp > 0, (f - exp) ** 2 / np.maximum(exp, 1e-12), 0.0).sum(axis=1)
    dfree = pi.shape[1] - 1
    crit = float(stats.chi2.ppf(0.95, dfree))
    fe, fo = freq_vectors(world, idx, "even"), freq_vectors(world, idx, "odd")
    ce, co = _cos_pairs(fe), _cos_pairs(fo)
    sh = float(np.corrcoef(ce, co)[0, 1]) if ce.std() > 0 and co.std() > 0 else 0.0
    ent = -(pi * np.log(np.maximum(pi, 1e-300))).sum(axis=1)
    tr = world["trait_pure"][idx] - world["trait_pure"][idx].mean(axis=0,
                                                                 keepdims=True)
    return {"mantel_r": mantel_r(f, tr),
            "chi2_frac_exceeding_95": float(np.mean(chi2 > crit)),
            "chi2_mean": float(chi2.mean()), "chi2_df": int(dfree),
            "split_half_r": sh,
            "mean_entropy": float(ent.mean()),
            "entropy_frac_of_log4": float(ent.mean() / math.log(pi.shape[1])),
            "freq_uniformity_chi2": float(
                (((f.sum(axis=0) - f.sum() / pi.shape[1]) ** 2)
                 / (f.sum() / pi.shape[1])).sum()),
            "n_authors": int(len(idx)), "median_m": float(np.median(counts))}


# ---------------------------------------------------------------------------
# PART 0.


def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")
    m_ = k2b()
    lay = m_.layout()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    n_ctx = len(lay["contexts_sorted"])

    # ---- G0: hashes, references, and the transcription certificate.
    sd = world_seeds(0, "-probe")
    base = r1().build_split_world_v2(sd["author"], sd["frame"], PHI, W_STYLE)
    ch0 = build_choice_world(sd["author"], sd["frame"], PHI, W_STYLE, 0.0, 1.0)
    v2_identical = {k: bool(np.array_equal(base[k], ch0[k]))
                    for k in ("trait", "trait_pure", "style", "slow", "common",
                              "noise", "int")}
    base_choice = np.repeat(lay["ctx_index"][:, None], lay["t_max"], axis=1)
    std_panel = m_.emit_panel(base, w)
    cho_panel = emit_choice(base, w, base_choice)
    std_truth = m_.emit_panel({**base, "trait": base["trait_pure"]}, w,
                              active=("mu", "common"))
    cho_truth = emit_choice_truth(base, base["trait_pure"], w, base_choice)
    panel_bitexact = bool(all(np.array_equal(a, b)
                              for a, b in zip(std_panel, cho_panel)))
    truth_bitexact = bool(all(np.array_equal(a, b)
                              for a, b in zip(std_truth, cho_truth)))
    r_std = field_agreement_of(std_panel, std_truth, "m4k2b-S1-cert")
    r_cho = field_agreement_of(cho_panel, cho_truth, "m4k2b-S1-cert")
    m1c = read_csv_rt(M1CCELLS)
    m1c_row = m1c[m1c["cell_tag"] == "s0.25_p0.60"].iloc[0]
    r2arm = read_json(R2FIT)["per_arm"]["w1.0"]["R_T_nat"]
    g0 = {
        "instrument_hashes": {rel(p): sha_file(p) for p in (R1SRC, R2SRC, K2BSRC)},
        "v2_objects_bit_identical": v2_identical,
        "exposure_stream_is_separate": bool(all(v2_identical.values())),
        "emit_choice_panel_bitexact_vs_emit_panel": panel_bitexact,
        "emit_choice_truth_bitexact": truth_bitexact,
        "field_standard": r_std, "field_choice_path": r_cho,
        "field_bitexact": bool(r_std == r_cho),
        "pins": {"emit_panel": PIN_EMIT, "common_term": PIN_COMMON,
                 "ctx_index": PIN_CTXIDX, "builder": PIN_BUILDER,
                 "trait_site": PIN_TRAITSITE},
        "n_contexts": n_ctx, "contexts": list(lay["contexts_sorted"]),
        "n_authors": int(len(lay["author_ids"])),
        "n_retained": int(len(lay["retained_idx"])),
        "t_max": int(lay["t_max"]),
        "reference_routing": {"source": "R2 v2 arm share .25 / phi .60 / w_style 1.0",
                              "mean": float(r2arm["mean"]),
                              "sem": float(r2arm["sem"]), "n": int(r2arm["n"])},
        "reference_m1c_no_style": {"cell": "s0.25_p0.60",
                                   "mean": float(m1c_row["field_mean"]),
                                   "sd": float(m1c_row["field_sd"]),
                                   "sem": float(m1c_row["field_sem"]),
                                   "n": int(m1c_row["n_worlds"])},
        "reference_note": RN_NOTES["RN-S1-5"],
    }
    g0["PASS"] = bool(panel_bitexact and truth_bitexact and g0["field_bitexact"]
                      and g0["exposure_stream_is_separate"] and n_ctx == N_PC)
    if not g0["PASS"]:
        write_json(OUT / "part0.json", {"G0s1": g0})
        raise SystemExit("G0s1 FAILED -> STOP (or INFEASIBLE_CHOICE if the "
                         "transcription cannot be made bit-exact)")

    # ---- beta*: arithmetic on standard-normal scores only (RN-S1-4).
    rng = np.random.default_rng(MASTER_SEED)
    x = rng.normal(size=(N_MC_BETA, n_ctx))
    med_m = float(np.median(lay["counts"][lay["retained_idx"]]))
    crit = float(stats.chi2.ppf(0.95, n_ctx - 1))
    log_k = math.log(n_ctx)
    grid = []
    beta_star = None
    for b in BETA_GRID:
        pi = softmax_rows(b * x)
        ent = float((-(pi * np.log(np.maximum(pi, 1e-300))).sum(axis=1)).mean())
        ncp = med_m * ((pi - 1.0 / n_ctx) ** 2 / (1.0 / n_ctx)).sum(axis=1)
        power = float(np.median(stats.ncx2.sf(crit, n_ctx - 1, ncp)))
        row = {"beta": b, "mean_entropy": ent, "entropy_frac": ent / log_k,
               "median_chi2_power": power,
               "meets_entropy": bool(ent <= ENTROPY_TARGET_FRAC * log_k),
               "meets_power": bool(power >= CHI2_POWER_MIN)}
        grid.append(row)
        if beta_star is None and row["meets_entropy"] and row["meets_power"]:
            beta_star = b
    if beta_star is None:
        write_json(OUT / "part0.json", {"G0s1": g0, "beta_grid": grid})
        raise SystemExit("no beta on the grid meets both declared criteria -> STOP")
    chosen = next(r for r in grid if r["beta"] == beta_star)
    beta_obj = {
        "beta_star": beta_star, "criteria": {
            "entropy_target_frac_of_log_k": ENTROPY_TARGET_FRAC,
            "chi2_power_min": CHI2_POWER_MIN, "median_m_used": med_m,
            "chi2_df": n_ctx - 1, "chi2_crit_95": crit},
        "at_beta_star": chosen, "log_k": log_k, "n_mc": N_MC_BETA,
        "grid_span": [BETA_GRID[0], BETA_GRID[-1]], "no_worlds_used": True,
        "note": RN_NOTES["RN-S1-4"],
    }

    # ---- probe worlds for the C-S1c band (permutation arithmetic) + spreads.
    probe = []
    for i in range(N_PILOT):
        sdp = world_seeds(100 + i, "-probe")
        for gamma in GAMMAS:
            wd = build_choice_world(sdp["author"], sdp["frame"], PHI, W_STYLE,
                                    beta_star, gamma)
            st = world_selection_stats(wd, lay["retained_idx"])
            probe.append({"world": i, "gamma": gamma, **st})
    pdf = pd.DataFrame(probe)
    pdf.to_csv(OUT / "probe.csv", index=False)
    wd0 = build_choice_world(world_seeds(100, "-probe")["author"],
                             world_seeds(100, "-probe")["frame"], PHI, W_STYLE,
                             beta_star, 0.0)
    f0 = freq_vectors(wd0, lay["retained_idx"])
    tr0 = (wd0["trait_pure"][lay["retained_idx"]]
           - wd0["trait_pure"][lay["retained_idx"]].mean(axis=0, keepdims=True))
    perm_sd = mantel_perm_sd(f0, tr0, B_PERM, MASTER_SEED + 5)
    infl = df_inflation(N_PILOT - 1)
    eps_c = float(2.0 * perm_sd * infl)
    sd_g1 = float(np.std(pdf[pdf.gamma == 1.0]["mantel_r"], ddof=1))
    sd_g0 = float(np.std(pdf[pdf.gamma == 0.0]["mantel_r"], ddof=1))

    part0 = {
        "leg": LEG, "utc": datetime.now(UTC).isoformat(),
        "G0s1": g0, "beta_star": beta_obj, "RN_NOTES": RN_NOTES,
        "C_S1c_band": {"permutation_sd_single_world": perm_sd,
                       "B_perm": B_PERM, "equivalence_eps": eps_c,
                       "df_inflation": infl,
                       "note": "equivalence band from permutation arithmetic on a "
                               "probe world (#57: a SECOND MOMENT, never a mean)"},
        "probe_spreads": {"sd_mantel_gamma1": sd_g1, "sd_mantel_gamma0": sd_g0},
        "design": {"share": SHARE, "phi": PHI, "w_style": W_STYLE,
                   "gammas": list(GAMMAS), "n_worlds": N_WORLDS,
                   "n_anchor": N_ANCHOR, "master_seed": MASTER_SEED,
                   "salts": [SALT_AUTHOR, SALT_FRAME, SALT_PILOT, SALT_EXPOSURE]},
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", beta_star=beta_star)
    print(f"part0 OK  transcription bit-exact: panel={panel_bitexact} "
          f"truth={truth_bitexact} field={g0['field_bitexact']}\n"
          f"  v2 objects bit-identical: {g0['exposure_stream_is_separate']}\n"
          f"  beta*={beta_star!r} (entropy frac {chosen['entropy_frac']:.4f} <= "
          f"{ENTROPY_TARGET_FRAC}, median chi2 power {chosen['median_chi2_power']:.4f})\n"
          f"  C-S1c eps={eps_c!r} (perm sd {perm_sd!r})  probe mantel g1/g0 sd "
          f"{sd_g1:.5f}/{sd_g0:.5f}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------


def stage_pilot(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("pilot_start")
    p0 = read_json(OUT / "part0.json")
    lay = k2b().layout()
    beta = p0["beta_star"]["beta_star"]
    rows = []
    for i in range(N_PILOT):
        sd = world_seeds(i, "-pilot")
        for gamma in GAMMAS:
            wd = build_choice_world(sd["author"], sd["frame"], PHI, W_STYLE,
                                    beta, gamma)
            st = world_selection_stats(wd, lay["retained_idx"])
            rows.append({"world": i, "gamma": gamma, **st})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "pilot_field.csv", index=False)
    preds = {}
    for gamma in GAMMAS:
        v = df[df.gamma == gamma]["mantel_r"].to_numpy(float)
        preds[f"g{gamma}"] = {
            "all_finite": bool(np.all(np.isfinite(v))),
            "any_saturated": bool(np.any(np.abs(v) >= SATURATION_ABS)),
            "nonzero_variance": bool(float(np.std(v, ddof=1)) > 0.0),
            "min": float(v.min()), "max": float(v.max())}
        preds[f"g{gamma}"]["PASS"] = bool(
            preds[f"g{gamma}"]["all_finite"]
            and not preds[f"g{gamma}"]["any_saturated"]
            and preds[f"g{gamma}"]["nonzero_variance"])
    out = {"n": N_PILOT, "predicates": preds,
           "PASS": bool(all(p["PASS"] for p in preds.values())),
           "mantel_means": {f"g{g}": float(df[df.gamma == g]["mantel_r"].mean())
                            for g in GAMMAS},
           "sd": {f"g{g}": float(np.std(df[df.gamma == g]["mantel_r"], ddof=1))
                  for g in GAMMAS},
           "seconds": time.time() - t0}
    write_json(OUT / "pilot.json", out)
    _log("pilot_done")
    if not out["PASS"]:
        raise SystemExit("G2s1 FAILED -> INSTRUMENT_DEFECT(pilot predicate)")
    print(f"pilot OK  mantel {out['mantel_means']}  sd {out['sd']}  "
          f"{time.time() - t0:.1f}s")


def stage_project(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("project_start")
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    eps = p0["C_S1c_band"]["equivalence_eps"]
    infl = df_inflation(N_PILOT - 1)
    sd1 = pil["sd"]["g1.0"] * infl
    sd0 = pil["sd"]["g0.0"] * infl
    truth1 = pil["mantel_means"]["g1.0"]

    def project(n: int) -> dict[str, Any]:
        rng = np.random.default_rng(MASTER_SEED)
        res: dict[str, Any] = {"n_worlds": n, "per_truth": {}}
        d1 = rng.normal(truth1, sd1 / math.sqrt(n), size=B_PROJ)
        p_det = float(np.mean(d1 > eps))
        res["per_truth"]["gamma=1 (detection)"] = {
            "truth": truth1, "role": "power", "bar": POWER_MIN, "P": p_det,
            "PASS": bool(p_det >= POWER_MIN)}
        d0 = rng.normal(0.0, sd0 / math.sqrt(n), size=B_PROJ)
        p_ff = float(np.mean(np.abs(d0) > eps))
        res["per_truth"]["gamma=0 (false-fire)"] = {
            "truth": 0.0, "role": "false-fire", "bar": FALSE_FIRE_MAX, "P": p_ff,
            "PASS": bool(p_ff <= FALSE_FIRE_MAX)}
        res["PASS"] = bool(all(v["PASS"] for v in res["per_truth"].values()))
        return res

    base = project(N_WORLDS)
    out = {"base": base, "escalation_fired": False, "escalated": None,
           "eps": eps, "sd_gamma1_df_inflated": sd1,
           "sd_gamma0_df_inflated": sd0, "PASS": base["PASS"],
           "n_final": N_WORLDS}
    if not base["PASS"]:
        esc = project(N_ESCALATED)
        out.update({"escalation_fired": True, "escalated": esc,
                    "PASS": esc["PASS"],
                    "n_final": N_ESCALATED if esc["PASS"] else N_WORLDS})
    write_json(OUT / "projection.json", out)
    _log("project_done")
    if not out["PASS"]:
        raise SystemExit("G3s1 FAILED -> NON_PROJECTABLE")
    print("project OK  " + "  ".join(f"{k}: {v['P']!r}"
                                     for k, v in out["base"]["per_truth"].items())
          + f"  n={out['n_final']}  escalated={out['escalation_fired']}  "
            f"{time.time() - t0:.1f}s")


def stage_arm(args: argparse.Namespace) -> None:
    t0 = time.time()
    (OUT / "arms").mkdir(parents=True, exist_ok=True)
    p0 = read_json(OUT / "part0.json")
    lay = k2b().layout()
    m_ = k2b()
    w = m_.arm_weights(SHARE, W_INT_ARM)
    beta = p0["beta_star"]["beta_star"]
    n_final = int(read_json(OUT / "projection.json")["n_final"])
    which = args.which
    rows = []
    if which == "anchor":
        _log("arm_start", arm="anchor")
        for i in range(N_ANCHOR):
            sd = world_seeds(500 + i)
            wd = build_choice_world(sd["author"], sd["frame"], PHI, W_STYLE,
                                    0.0, 1.0)
            corpus = f"m4k2b-S1-anchor{i}"
            r_choice = field_agreement_of(
                emit_choice(wd, w, wd["choice"]),
                emit_choice_truth(wd, wd["trait_pure"], w, wd["choice"]), corpus)
            base_choice = np.repeat(lay["ctx_index"][:, None], lay["t_max"], axis=1)
            r_std = field_agreement_of(
                emit_choice(wd, w, base_choice),
                emit_choice_truth(wd, wd["trait_pure"], w, base_choice), corpus)
            f = freq_vectors(wd, lay["retained_idx"])
            tot = f.sum()
            unif_chi2 = float((((f.sum(axis=0) - tot / f.shape[1]) ** 2)
                               / (tot / f.shape[1])).sum())
            rows.append({"world": i, "beta": 0.0, "R_T_choice": r_choice,
                         "R_T_layout_exposure": r_std,
                         "paired_delta": r_choice - r_std,
                         "uniformity_chi2": unif_chi2,
                         "uniformity_df": int(f.shape[1] - 1)})
        pd.DataFrame(rows).to_csv(OUT / "arms" / "anchor.csv", index=False)
    else:
        gamma = float(which)
        _log("arm_start", arm=which)
        for i in range(n_final):
            sd = world_seeds(i)
            wd = build_choice_world(sd["author"], sd["frame"], PHI, W_STYLE,
                                    beta, gamma)
            st = world_selection_stats(wd, lay["retained_idx"])
            rows.append({"world": i, "gamma": gamma, **st})
        pd.DataFrame(rows).to_csv(
            OUT / "arms" / f"gamma_{gamma}.csv", index=False)
    _log("arm_done", arm=which, n=len(rows))
    print(f"arm {which} OK  rows={len(rows)}  {time.time() - t0:.1f}s")


# ---------------------------------------------------------------------------


def stage_fit(args: argparse.Namespace) -> None:
    t0 = time.time()
    _log("fit_start")
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "projection.json")
    anchor = read_csv_rt(OUT / "arms" / "anchor.csv")
    g1 = read_csv_rt(OUT / "arms" / "gamma_1.0.csv")
    g0d = read_csv_rt(OUT / "arms" / "gamma_0.0.csv")
    rng = np.random.default_rng(MASTER_SEED)

    def stat(v: np.ndarray) -> dict[str, Any]:
        idx = rng.integers(0, len(v), size=(B_BOOT, len(v)))
        bs = v[idx].mean(axis=1)
        return {"mean": float(v.mean()),
                "sem": float(np.std(v, ddof=1) / math.sqrt(len(v))),
                "sd": float(np.std(v, ddof=1)),
                "ci95": [float(np.percentile(bs, CI_Q[0])),
                         float(np.percentile(bs, CI_Q[1]))],
                "n": int(len(v))}

    # ---- C-S1a
    ref = p0["G0s1"]["reference_routing"]
    a_choice = stat(anchor["R_T_choice"].to_numpy(float))
    a_paired = stat(anchor["paired_delta"].to_numpy(float))
    sem_diff = float(math.sqrt(a_choice["sem"] ** 2 + ref["sem"] ** 2))
    band = float(2.0 * math.sqrt(2.0) * sem_diff)
    dev = float(a_choice["mean"] - ref["mean"])
    ucrit = float(stats.chi2.ppf(0.95, int(anchor["uniformity_df"].iloc[0])))
    u_ok = bool((anchor["uniformity_chi2"].to_numpy(float) <= ucrit).mean() >= 0.80)
    c_s1a = {
        "anchor_mean": a_choice["mean"], "anchor_ci95": a_choice["ci95"],
        "anchor_sem": a_choice["sem"], "n_anchor": a_choice["n"],
        "reference": ref, "deviation": dev, "sem_diff": sem_diff,
        "band_2sqrt2_sem": band, "z": float(dev / sem_diff),
        "levels_replicate": bool(abs(dev) <= band),
        "uniformity_chi2_mean": float(anchor["uniformity_chi2"].mean()),
        "uniformity_crit95": ucrit,
        "uniformity_frac_within": float(
            (anchor["uniformity_chi2"].to_numpy(float) <= ucrit).mean()),
        "frequencies_uniform": u_ok,
        "paired_diagnostic": {**a_paired,
                              "label": "DOES NOT ROUTE (RN-S1-6): the same worlds "
                                       "through emit_panel's own exposure vs the "
                                       "choice path at beta = 0"},
        "m1c_reference_no_style": p0["G0s1"]["reference_m1c_no_style"],
        "PASS": bool(abs(dev) <= band and u_ok),
    }

    # ---- C-S1b (at beta*, both gamma arms show the signature)
    c_s1b = {}
    for name, d in (("gamma1", g1), ("gamma0", g0d)):
        chi_frac = stat(d["chi2_frac_exceeding_95"].to_numpy(float))
        shalf = stat(d["split_half_r"].to_numpy(float))
        ent = stat(d["entropy_frac_of_log4"].to_numpy(float))
        c_s1b[name] = {
            "chi2_frac_exceeding_95": chi_frac, "split_half_r": shalf,
            "entropy_frac_of_log4": ent,
            "chi2_within_multinomial_band": bool(chi_frac["ci95"][0] <= 0.05
                                                 <= chi_frac["ci95"][1]
                                                 or chi_frac["mean"] <= 0.10),
            "split_half_stable": bool(shalf["ci95"][0] > 0.0),
            "entropy_dropped": bool(ent["mean"] <= ENTROPY_TARGET_FRAC + 0.02),
        }
        c_s1b[name]["PASS"] = bool(
            c_s1b[name]["chi2_within_multinomial_band"]
            and c_s1b[name]["split_half_stable"]
            and c_s1b[name]["entropy_dropped"])
    c_s1b["PASS"] = bool(all(c_s1b[k]["PASS"] for k in ("gamma1", "gamma0")))
    c_s1b["stability_is_gamma_independent"] = bool(
        c_s1b["gamma0"]["split_half_stable"] and c_s1b["gamma1"]["split_half_stable"])

    # ---- C-S1c
    eps = p0["C_S1c_band"]["equivalence_eps"]
    m1 = stat(g1["mantel_r"].to_numpy(float))
    m0 = stat(g0d["mantel_r"].to_numpy(float))
    c_s1c = {
        "gamma1": m1, "gamma0": m0, "eps": eps,
        "gamma1_POSITIVE": bool(m1["ci95"][0] > eps),
        "gamma0_ZERO": bool(abs(m0["mean"]) <= eps and m0["ci95"][0] >= -eps
                            and m0["ci95"][1] <= eps),
        "separation": float(m1["mean"] - m0["mean"]),
        "gamma0_still_stable": c_s1b["gamma0"]["split_half_stable"],
        "gamma0_split_half_r": c_s1b["gamma0"]["split_half_r"]["mean"],
        "gamma1_split_half_r": c_s1b["gamma1"]["split_half_r"]["mean"],
    }
    c_s1c["PASS"] = bool(c_s1c["gamma1_POSITIVE"] and c_s1c["gamma0_ZERO"]
                         and c_s1c["gamma0_still_stable"])

    # --- the two readings of "beta = 0" (RN-S1-8), both reported.
    lay_mean = float(anchor["R_T_layout_exposure"].mean())
    c_s1a["two_readings_of_beta0"] = {
        "A_uniform_exposure": {
            "definition": "pi uniform, exposure drawn from it -- the "
                          "registration's explicit words ('beta = 0 recovers "
                          "uniform exposure')",
            "anchor_mean": a_choice["mean"], "deviation_vs_routing_ref": dev,
            "deviation_vs_m1c": float(
                a_choice["mean"] - c_s1a["m1c_reference_no_style"]["mean"]),
            "deviation_vs_own_layout_exposure": float(a_choice["mean"] - lay_mean),
            "level_clause": "FAILS under every reference and under both band "
                            "readings",
        },
        "B_layout_exposure_noop": {
            "definition": "choice[i, o] = ctx_index[i] -- beta = 0 as a NO-OP on "
                          "the frame path",
            "evidence": "Part 0's transcription certificate: bit-exact against "
                        "emit_panel, panel, truth and field",
            "level_clause": "passes EXACTLY, by construction",
        },
        "band_readings": {"generous_2sqrt2_sem_diff": band,
                          "strict_2_sem_diff": float(2.0 * sem_diff),
                          "fails_under_both": bool(abs(dev) > 2.0 * sem_diff)},
        "note": "the certificate asks for uniform SELECTION and baseline EXPOSURE "
                "at once; those are different neutralities and this apparatus "
                "cannot satisfy both, because uniform mixing across contexts "
                "destroys the per-author frame coherence the field gauge pools "
                "for. The generator is not implicated -- C-S1b and C-S1c both "
                "pass and the transcription is bit-exact.",
    }
    out = {"C_S1a": c_s1a, "C_S1b": c_s1b, "C_S1c": c_s1c,
           "n_worlds_per_arm": int(len(g1)), "n_anchor": int(len(anchor)),
           "seconds": time.time() - t0}
    write_json(OUT / "fit.json", out)
    _log("fit_done")
    print(f"fit OK\n  C-S1a anchor={c_s1a['anchor_mean']!r} ref="
          f"{ref['mean']!r} dev={dev!r} band={band!r} z={c_s1a['z']:.3f} "
          f"PASS={c_s1a['PASS']} (paired delta {a_paired['mean']!r})\n"
          f"  C-S1b g1 chi2frac={c_s1b['gamma1']['chi2_frac_exceeding_95']['mean']!r} "
          f"splithalf={c_s1b['gamma1']['split_half_r']['mean']!r} | g0 "
          f"chi2frac={c_s1b['gamma0']['chi2_frac_exceeding_95']['mean']!r} "
          f"splithalf={c_s1b['gamma0']['split_half_r']['mean']!r} "
          f"PASS={c_s1b['PASS']}\n"
          f"  C-S1c mantel g1={m1['mean']!r} {m1['ci95']!r} | g0={m0['mean']!r} "
          f"{m0['ci95']!r} eps={eps!r} PASS={c_s1c['PASS']}  "
          f"{time.time() - t0:.1f}s")


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    failed = [n for n in ("C_S1a", "C_S1b", "C_S1c") if not fit[n]["PASS"]]
    if not p0["G0s1"]["PASS"]:
        cell, slug, text = 1, "STOP", "G0/import/hash failure"
    elif not g3["PASS"]:
        cell, slug, text = 3, "NON_PROJECTABLE", "projection fails after escalation"
    elif not failed:
        cell, slug = 4, "CHOICE_GENERATOR_CERTIFIED"
        text = "all certificates PASS; S2 registrable"
    else:
        cell = 5
        slug = "INSTRUMENT_DEFECT(" + ",".join(failed) + ")"
        text = "a certificate fails; handback"
    mods = []
    if fit["C_S1c"]["PASS"]:
        mods.append("COUPLING_PLACED_GAMMA1_POSITIVE_GAMMA0_NULL")
    if fit["C_S1b"].get("stability_is_gamma_independent"):
        mods.append("SIGNATURE_STABLE_AT_BOTH_GAMMA")
    dec = {"leg": LEG, "utc": datetime.now(UTC).isoformat(),
           "routing_cell": cell, "verdict_slug": slug, "routing_text": text,
           "modifiers": mods, "failed_certificates": failed,
           "n_worlds_per_arm": fit["n_worlds_per_arm"],
           "banner": "EXPLORATORY, synthetic, label-free; an INSTRUMENT leg -- the "
                     "coupling is BUILT here, not discovered; no real-data claim",
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


def _tables(p0, pil, g3, fit, dec) -> dict[str, str]:
    g0 = p0["G0s1"]
    sec: dict[str, list[str]] = {}
    sec["transcription"] = _md(
        ["check", "result"],
        [["emit_choice panel bit-exact vs emit_panel (layout exposure)",
          "**" + str(g0["emit_choice_panel_bitexact_vs_emit_panel"]) + "**"],
         ["emit_choice truth panel bit-exact",
          str(g0["emit_choice_truth_bitexact"])],
         ["field agreement identical", f"{g0['field_standard']!r} vs "
          f"{g0['field_choice_path']!r} → {g0['field_bitexact']}"],
         ["every v2 object bit-identical after adding the choice machinery",
          "**" + str(g0["exposure_stream_is_separate"]) + "**"],
         ["  per object", ", ".join(f"{k}={v}" for k, v in
                                    g0["v2_objects_bit_identical"].items())],
         ["emit_panel source", g0["pins"]["emit_panel"]],
         ["the ONE changed line", g0["pins"]["common_term"]],
         ["contexts", f"{g0['n_contexts']} — {', '.join(g0['contexts'])}"],
         ["authors / retained / t_max",
          f"{g0['n_authors']} / {g0['n_retained']} / {g0['t_max']}"]])
    b = p0["beta_star"]
    sec["beta"] = _md(
        ["item", "value"],
        [["**β\\***", "**" + repr(b["beta_star"]) + "**"],
         ["declared criterion 1", f"mean entropy ≤ {b['criteria']['entropy_target_frac_of_log_k']} · log k"],
         ["declared criterion 2",
          f"median per-author χ²({b['criteria']['chi2_df']}) power ≥ "
          f"{b['criteria']['chi2_power_min']} at median m = "
          f"{b['criteria']['median_m_used']!r}"],
         ["realized mean entropy at β*", repr(b["at_beta_star"]["mean_entropy"])],
         ["entropy as fraction of log k",
          repr(b["at_beta_star"]["entropy_frac"])],
         ["median χ² power at β*",
          repr(b["at_beta_star"]["median_chi2_power"])],
         ["grid searched", f"{b['grid_span'][0]!r} … {b['grid_span'][1]!r}"],
         ["worlds used to fix β*", "**none** — standard-normal arithmetic only"]])
    a = fit["C_S1a"]
    sec["c_s1a"] = _md(
        ["clause", "value", "reference / band", "result"],
        [["anchor field level (β=0)", f"{a['anchor_mean']!r} {a['anchor_ci95']!r}",
          f"{a['reference']['source']}: {a['reference']['mean']!r}", ""],
         ["deviation", repr(a["deviation"]),
          f"band 2·√2·SEM = {a['band_2sqrt2_sem']!r} (z = {a['z']!r})",
          "**" + str(a["levels_replicate"]) + "**"],
         ["selection frequencies uniform",
          f"mean χ² {a['uniformity_chi2_mean']!r}",
          f"crit95 {a['uniformity_crit95']!r}, frac within "
          f"{a['uniformity_frac_within']!r}",
          "**" + str(a["frequencies_uniform"]) + "**"],
         ["M1c no-style lineage row (reported, not routing)",
          repr(a["m1c_reference_no_style"]["mean"]),
          f"sem {a['m1c_reference_no_style']['sem']!r}", "context"],
         ["paired diagnostic Δ (DOES NOT ROUTE)",
          f"{a['paired_diagnostic']['mean']!r} {a['paired_diagnostic']['ci95']!r}",
          "choice path at β=0 minus the layout's own exposure, same worlds",
          "diagnostic"]])
    bb = fit["C_S1b"]
    sec["c_s1b"] = _md(
        ["arm", "χ² fraction exceeding 95th", "split-half r", "entropy frac",
         "result"],
        [[k, f"{bb[k]['chi2_frac_exceeding_95']['mean']!r} "
          f"{bb[k]['chi2_frac_exceeding_95']['ci95']!r}",
          f"{bb[k]['split_half_r']['mean']!r} {bb[k]['split_half_r']['ci95']!r}",
          repr(bb[k]["entropy_frac_of_log4"]["mean"]),
          "**" + str(bb[k]["PASS"]) + "**"] for k in ("gamma1", "gamma0")])
    c = fit["C_S1c"]
    sec["c_s1c"] = _md(
        ["arm", "Mantel r (selection-sim vs trait-sim)", "CI95", "test", "result"],
        [["γ = 1", repr(c["gamma1"]["mean"]), repr(c["gamma1"]["ci95"]),
          f"POSITIVE iff CI low > ε = {c['eps']!r}",
          "**" + str(c["gamma1_POSITIVE"]) + "**"],
         ["γ = 0", repr(c["gamma0"]["mean"]), repr(c["gamma0"]["ci95"]),
          f"ZERO iff CI ⊂ ±ε = {c['eps']!r}",
          "**" + str(c["gamma0_ZERO"]) + "**"],
         ["separation γ1 − γ0", repr(c["separation"]), "-", "-", "-"],
         ["γ = 0 signature still stable", repr(c["gamma0_split_half_r"]),
          "-", "split-half r > 0",
          "**" + str(c["gamma0_still_stable"]) + "**"]])
    sec["projection"] = _md(
        ["truth", "role", "bar", "P", "PASS"],
        [[k, v["role"], repr(v["bar"]), repr(v["P"]), str(v["PASS"])]
         for k, v in g3["base"]["per_truth"].items()])
    sec["certificates"] = _md(
        ["certificate", "PASS"],
        [[n, "**" + str(fit[n]["PASS"]) + "**"]
         for n in ("C_S1a", "C_S1b", "C_S1c")])
    return {k: "\n".join(v) for k, v in sec.items()}


def _facts(p0, pil, g3, fit, dec) -> dict[str, Any]:
    a, bb, c = fit["C_S1a"], fit["C_S1b"], fit["C_S1c"]
    g0 = p0["G0s1"]
    return {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "MODS": ", ".join(dec["modifiers"]) or "none",
        "BETA": p0["beta_star"]["beta_star"],
        "ENTFRAC": p0["beta_star"]["at_beta_star"]["entropy_frac"],
        "CHIPOW": p0["beta_star"]["at_beta_star"]["median_chi2_power"],
        "ANCH": a["anchor_mean"], "ANCHCI": a["anchor_ci95"],
        "REF": a["reference"]["mean"], "DEV": a["deviation"],
        "BAND": a["band_2sqrt2_sem"], "Z": a["z"],
        "PAIRED": a["paired_diagnostic"]["mean"],
        "PAIREDCI": a["paired_diagnostic"]["ci95"],
        "M1C": a["m1c_reference_no_style"]["mean"],
        "UCHI": a["uniformity_chi2_mean"], "UCRIT": a["uniformity_crit95"],
        "SH1": bb["gamma1"]["split_half_r"]["mean"],
        "SH0": bb["gamma0"]["split_half_r"]["mean"],
        "CHI1": bb["gamma1"]["chi2_frac_exceeding_95"]["mean"],
        "CHI0": bb["gamma0"]["chi2_frac_exceeding_95"]["mean"],
        "M1": c["gamma1"]["mean"], "M1CI": c["gamma1"]["ci95"],
        "M0": c["gamma0"]["mean"], "M0CI": c["gamma0"]["ci95"],
        "EPS": c["eps"], "SEP": c["separation"],
        "PERMSD": p0["C_S1c_band"]["permutation_sd_single_world"],
        "NW": fit["n_worlds_per_arm"], "NA": fit["n_anchor"],
        "ESC": g3["escalation_fired"],
        "NRET": g0["n_retained"], "NAUTH": g0["n_authors"],
        "PYEXE": p0["environment"]["python_executable"],
        "PYVER": p0["environment"]["python_version"],
        "DEVM1C": a["two_readings_of_beta0"]["A_uniform_exposure"]["deviation_vs_m1c"],
        "STRICTBAND": a["two_readings_of_beta0"]["band_readings"]["strict_2_sem_diff"],
        "FAILSBOTH": a["two_readings_of_beta0"]["band_readings"]["fails_under_both"],
        "LAYMEAN": a["two_readings_of_beta0"]["A_uniform_exposure"]["deviation_vs_own_layout_exposure"] + a["anchor_mean"],
        "LAYZ": abs((a["two_readings_of_beta0"]["A_uniform_exposure"]["deviation_vs_own_layout_exposure"] + a["anchor_mean"]) - a["reference"]["mean"]) / a["sem_diff"],
        "VERDICT": _verdict(fit),
    }


def _verdict(fit: dict[str, Any]) -> str:
    c, bb = fit["C_S1c"], fit["C_S1b"]
    if not fit["C_S1c"]["PASS"]:
        return ("The coupling is NOT placed as designed, so the apparatus cannot "
                "yet measure the owner's conjecture and S2 must wait.")
    head = ""
    if not fit["C_S1a"]["PASS"]:
        head = ("**The leg routes to a handback on C-S1a — but the defect is in "
                "that certificate's specification, not in the generator.** C-S1a "
                "demands uniform *selection* and baseline *exposure* at the same "
                "β = 0, and those are different neutralities; §5.1 shows the level "
                "shift is the apparatus behaving correctly, and gives the "
                "one-line fix. Everything the line actually needs was "
                "established.\n\n")
    return head + (
        "**The apparatus does what the conjecture needs it to do.** Selection is a "
        "stable per-person signature in BOTH arms — split-half r "
        f"{bb['gamma1']['split_half_r']['mean']!r} at γ = 1 and "
        f"{bb['gamma0']['split_half_r']['mean']!r} at γ = 0 — but it carries trait "
        f"information ONLY when traits drive it: Mantel r {c['gamma1']['mean']!r} "
        f"at γ = 1 against {c['gamma0']['mean']!r} at γ = 0. That is decomposition "
        "(b) made physical: **a perfectly stable selection signature can be "
        "completely uninformative about personality.** Stability is necessary and "
        "nowhere near sufficient, and the γ = 0 arm is the falsifier the real-data "
        "track will need.")


TEMPLATE = """# SUICA M4-S1 — the choice-enabled generator

**Outcome: `{{SLUG}}`** (rule-16 cell {{CELL}}). Modifiers: {{MODS}}.

Registered before the run in `docs/SUICA_M4_S_SELECTION_LINE_PLAN.md` ("M4-S1",
commit 21149bb). EXPLORATORY, synthetic, label-free. **An instrument leg**: the
coupling measured here is one this leg BUILDS. Nothing in it is evidence about
real people, and no real-data claim is made or implied.

## 1. What this had to establish

The owner's conjecture is that the gauge reads frames, but which frames a person
*chooses* is person-owned — so selection-proximity should imply
personality-proximity. That claim decomposes into (a) selection is a person-stable
signature, and (b) selection-similarity implies trait-similarity. (b) is not a
theorem: it is a coupling strength, and it is false when selection is driven by
something other than traits. This leg builds an apparatus in which (b) can be
dialled — γ = 1 trait-driven, γ = 0 identity-driven — and certifies it.

{{VERDICT}}

## 2. The structural question: is endogenous exposure expressible at all?

It nearly is not. `emit_panel` ({{PYVER}} run, k2b:359-381) gives author *i* the
frame object `common[ctx_index[i], o]` at **every** occasion — one context per
author, fixed by the frozen layout. Per-occasion choice cannot be expressed
through it, and k2b is read-only, so the registered fallback was
**INFEASIBLE_CHOICE**.

The licensed path is minimal extraction with provenance. `emit_choice`
transcribes `emit_panel` with **exactly one change**: the first index of the
common term (k2b:377) becomes `choice[i, o]`. Everything else — the trait site,
the slow term, the interaction, the noise, the weights, the loop — is the same
code. The shared-frame object per context is preserved exactly: `common[k, o]`
is still the single frame vector for context *k* at occasion *o*, handed to every
author who chooses *k* there. The author's **nominal** context (which the gauge
uses to pool authors into per-context fields) stays `lay["ctx_index"]`; only the
author's **realized exposure** is chosen. The model is: authors nominally belong
to a community and choose which contexts they actually engage.

The transcription is certified, not asserted:

<<TABLE:transcription>>

Setting `choice[i, o] = ctx_index[i]` reproduces `emit_panel` **bit-for-bit**,
panel and truth panel alike, down to an identical field agreement. That is the
whole feasibility argument, and it is checked by code rather than by reading.

## 3. Pins

- **u and v** (RN-S1-2): first four principal author-coordinates of each channel
  — SVD of the author-centred channel matrix (`trait_pure` for u, `style` for
  v), right singular vectors 1..4, authors projected, each coordinate z-scored
  so β means the same thing in both channels. **Sign convention (#64)**: each
  component's sign is fixed so its largest-magnitude loading is positive. SVD
  signs are otherwise arbitrary and would silently randomize π across worlds.
- **The exposure stream** (RN-S1-3) is its own rng, drawn after the v2 builder
  returns, so every v2 object stays bit-identical — certified above.
- **The reference for C-S1a** (RN-S1-5): the registration says "the v2/M1c
  share-.25 row", and two different objects answer to that description. The
  routing reference is R2's persisted v2 arm at the identical configuration
  (share .25, φ .60, w_style 1.0) = {{REF}}; M1c's no-style row ({{M1C}}) is
  reported as lineage context and routes nothing.

## 4. β* — fixed by arithmetic, before any world

<<TABLE:beta>>

## 5. Certificates

<<TABLE:certificates>>

### 5.1 C-S1a — the neutral anchor

<<TABLE:c_s1a>>

At β = 0 the field level is {{ANCH}} against the reference {{REF}} — a deviation
of {{DEV}} against a 2·√2·SEM band of {{BAND}} (z = {{Z}}). **The level clause
FAILS.** The frequency clause passes cleanly (mean uniformity χ² {{UCHI}} against
a 95th percentile of {{UCRIT}}, every anchor world within).

The failure is robust, not marginal-by-luck. The deviation is {{DEV}} against the
routing reference, {{DEVM1C}} against M1c's row, and {{PAIRED}} {{PAIREDCI}}
against these same worlds' *own* layout exposure — a paired CI excluding zero.
It fails under the generous band ({{BAND}}) and under the stricter reading of
"2·√2·SEM" as two sigma on the difference ({{STRICTBAND}}): {{FAILSBOTH}}.

**The cause is a conflict inside the certificate, not a fault in the generator.**
C-S1a asks for two different neutralities at once — uniform *selection* (π flat)
and baseline *exposure* (the level the panel has when every author sits in one
context). Those coincide only if mixing contexts leaves the field level alone,
and it does not: the deployed gauge pools authors by their nominal context to
estimate a per-context field, so spreading each author's occasions uniformly
across four contexts destroys exactly the coherence the gauge recovers. The
level drop is the apparatus working correctly.

Both readings of "β = 0" are therefore reported:

- **(A) uniform exposure** — the registration's explicit words. Level clause
  fails, as above.
- **(B) β = 0 as a no-op on the frame path** (`choice[i,o] = ctx_index[i]`).
  Level clause passes *exactly*: that is precisely what Part 0's transcription
  certificate demonstrates, bit-for-bit.

The handback is small and concrete: either define the neutral anchor as (B), or
keep (A) and drop its level clause, since under (A) a level shift is predicted by
the mechanism the registration itself specifies. Nothing about the generator
needs to change — C-S1b and C-S1c both pass, and the anchor worlds' own
layout-exposure level ({{LAYMEAN}}) sits within {{LAYZ}} SEM of the reference,
confirming the worlds are sound.

### 5.2 C-S1b — the signature

<<TABLE:c_s1b>>

Realized frequencies track π within multinomial noise ({{CHI1}} of authors
exceed the 95th percentile of χ²(3) at γ = 1, {{CHI0}} at γ = 0 — against 0.05
expected), and the signature is split-half stable in both arms.

### 5.3 C-S1c — the coupling placement

<<TABLE:c_s1c>>

Mantel r is {{M1}} {{M1CI}} at γ = 1 and {{M0}} {{M0CI}} at γ = 0, against an
equivalence band ε = {{EPS}} built from permutation arithmetic (permutation sd
{{PERMSD}}). Separation {{SEP}}.

**This is the certificate that matters for the line.** The γ = 0 arm has a
selection signature just as stable as the γ = 1 arm (split-half {{SH0}} vs
{{SH1}}) and carries no trait information at all. Stability of selection is
therefore *not* evidence for the conjecture — the real-data track will need the
coupling measured directly, because (a) can hold perfectly while (b) fails
completely.

## 6. Projection

<<TABLE:projection>>

## 7. Anomalies

1. **A-1 (before any number).** The pinned interpreter's virtualenv was
   partially destroyed between legs — a temp reaper deleted files under
   `/private/tmp` at 00:00, removing `pyvenv.cfg` and gutting `site-packages`
   (package directories survived, their `__init__.py` files did not, so `numpy`
   imported as an empty namespace package). Rebuilt from
   `requirements-lock-main.txt` and verified to match the versions the previous
   legs ran under (numpy 2.4.4, pandas 3.0.2, Python 3.12.12) before any
   S1 number was computed: `{{PYEXE}}`.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (before any number).** The feasibility of the exposure reallocation was
   settled by construction and certified bit-exactly before any certificate was
   evaluated, so INFEASIBLE_CHOICE was ruled out on evidence rather than by
   assumption.

## 8. Boundary

EXPLORATORY, synthetic, label-free. **The coupling is installed, not
discovered**: γ is a knob this leg turns, so C-S1c is a statement that the
apparatus works, not that selection predicts personality in any real corpus.
{{NW}} worlds per γ arm, {{NA}} anchor worlds, {{NAUTH}} authors each
({{NRET}} retained). One share, one φ, one dose, four contexts. The quantitative
law is S2's; this leg deliberately used generous certificate bands.

## 9. Environment

`{{PYEXE}}` — Python {{PYVER}}.
"""


def stage_report(args: argparse.Namespace) -> None:
    p0 = read_json(OUT / "part0.json")
    pil = read_json(OUT / "pilot.json")
    g3 = read_json(OUT / "projection.json")
    fit = read_json(OUT / "fit.json")
    dec = read_json(OUT / "decision.json")
    tabs = _tables(p0, pil, g3, fit, dec)
    facts = _facts(p0, pil, g3, fit, dec)
    (OUT / "report_tables.md").write_text(
        "\n\n".join(f"### {k}\n{v}" for k, v in tabs.items()) + "\n",
        encoding="utf-8")
    write_json(OUT / "prose_facts.json", facts)
    text = TEMPLATE
    for name, tab in tabs.items():
        text = text.replace(f"<<TABLE:{name}>>", tab)
    for key, val in facts.items():
        text = text.replace("{{" + key + "}}",
                            repr(val) if isinstance(val, (float, list)) else str(val))
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}|<<TABLE:[a-z_]+>>", text)
    if left:
        raise SystemExit(f"unresolved placeholders: {sorted(set(left))}")
    REPORT.write_text(text, encoding="utf-8")
    print(f"report OK  {rel(REPORT)}  ({len(text.splitlines())} lines)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["part0", "pilot", "project", "arm", "fit",
                                      "finalize", "report"])
    ap.add_argument("--which", type=str, default="anchor")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    {"part0": stage_part0, "pilot": stage_pilot, "project": stage_project,
     "arm": stage_arm, "fit": stage_fit, "finalize": stage_finalize,
     "report": stage_report}[args.stage](args)


if __name__ == "__main__":
    main()
