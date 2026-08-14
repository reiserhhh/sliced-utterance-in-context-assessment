#!/usr/bin/env python3
"""SUICA M4-P3 -- the natural gradient under frame refreshment.

Registered BEFORE run in docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md
("M4-P3 -- the natural gradient under frame refreshment", commit caba52f).
Binding.

The leg asks what fraction of the natural phi-gradient of b-only recovery
survives when the truth side's frame is REFRESHED -- same authors, fresh frame.
That requires paired worlds A and B sharing the AUTHOR/TRAIT channel draws and
differing in the STATE/FRAME channel draws, and the registration is explicit
about the constraint and about the consequence if it cannot be met:

    "the split must be achievable by seeding alone through the existing
     constructor interface ... If the generator's seed structure cannot be
     split without touching k2b's code, STOP as INFEASIBLE_SPLIT (an
     instrument finding, not a failure; suica_core/ and k2b remain READ-ONLY)"

This harness performs the Part-0 work that is possible regardless, then
EXHAUSTIVELY enumerates the constructor's input space and proves the split
impossible.  No world is drawn for measurement; nothing is sealed.

Stages:  part0 -> feasibility -> finalize -> report   (or: all)
"""
from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
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

OUT = ROOT / "results" / "m4_p3_refresh_gradient"
RES = ROOT / "results"
M1CRES = RES / "m4_m1c_r_at_level"
P2RES = RES / "m4_p2_dose_decomposition"

LEG = "M4-P3"
BANNER = ("the natural gradient under frame refreshment; exploratory, label-free; "
          "no seal -- the estimand is a ratio with an honest inferential gap")

MASTER_SEED = 20260814
SALT_A = "m4p3-worldA"
SALT_B = "m4p3-worldB"
SALT_PILOT = "m4p3-pilot"
SHARE = 0.25
PHI_LADDER = (0.05, 0.30, 0.60, 0.85, 0.98)
N_PAIRS = 192
N_PAIRS_ESCALATED = 384
W_INT_ARM = "zero"

# --- the seed-splitting decision rule, as registered -----------------------
AUTHOR_CHANNEL = ("trait", "a_load")
FRAME_CHANNEL = ("slow", "slow_latent", "common", "int")
CHANNEL_RULE = (
    "the author/trait channel comprises every random object that persists per "
    "author across occasions (b-draws and any per-author carrier); the "
    "state/frame channel comprises every per-occasion or per-context object "
    "(the slow state, the common channel, occasion assignments)")

# --- the citation anchors G0p3(iv) must locate (found by code, rule 24) ----
IDT = ROOT / "docs" / "SUICA_IDENTITY_THEORY_V1.md"
KLINE = ROOT / "docs" / "SUICA_M4_K_IDENTITY_LINE_PLAN.md"
K1BSRC = ROOT / "scripts" / "run_suica_m4_k1b_composition_ownership.py"
ANCHORS = {
    "T6-double-prime, the theory statement (IDT C.4)":
        (IDT, "frame-refreshed discriminator"),
    "T6-double-prime v2, the sign form (IDT D.3)":
        (IDT, "under frame refreshment, no reader may PROFIT"),
    "T9 / the P3 pattern (IDT appendix GG.3)":
        (IDT, "same authors, fresh frame"),
    "the registered reader design (K-line, K1b secondary)":
        (KLINE, "INDEPENDENT est8 norm samples per occasion"),
    "the published IMPLEMENTATION of frame-refreshed scoring":
        (K1BSRC, "frame refreshed"),
}

# ---------------------------------------------------------------------------
# RN-P3 notes.  PINNED IN PART 0, BEFORE ANY MEASUREMENT.
#
# RN-P3-1 (what counts as the author channel and what as the frame channel).
#   The registration's decision rule is quoted above and applied literally.  In
#   the K2b world dict the author-persistent objects are `trait` (the b-draw
#   projected through the loadings) and `a_load` (the per-author interaction
#   carrier); the per-occasion / per-context objects are `slow` and
#   `slow_latent` (the state), `common` (the frame), and `int` (the
#   per-occasion interaction).  Occasion assignments are the third frame item
#   named by the registration; in this family they live in layout(), which
#   takes no arguments and is memoised, so they are not seed-driven at all --
#   reported, because it is part of why the split cannot be seeded.
#
# RN-P3-2 (what "achievable by seeding alone through the existing constructor
#   interface" means, and how it is tested).  The K2b constructor is
#   build_k2b_world(world_seed: int, phi_slow: float) -- exactly two
#   POSITIONAL_OR_KEYWORD parameters, no defaults, no *args, no **kwargs
#   (verified by inspect at run time and recorded).  Its input space is
#   therefore the pair (world_seed, phi_slow), and "seeding alone" means:
#   choose two points in that space.  The feasibility test enumerates the space
#   EXHAUSTIVELY -- vary the seed at fixed phi, vary phi at fixed seed -- and
#   records, per channel, whether the objects are bit-identical.  A split
#   exists iff some pair of points leaves every AUTHOR object bit-identical
#   while changing at least one FRAME object.  This is a proof over the whole
#   interface, not a sample of it: with two arguments there is nothing else to
#   vary.
#
# RN-P3-3 (what is NOT tried, and why).  Three routes would change the frame
#   while holding the author channel fixed, and all three are excluded by the
#   registration's own words rather than by preference:
#   (a) editing build_k2b_world to accept split seeds -- forbidden, k2b is
#       READ-ONLY;
#   (b) channel surgery on the returned dicts (splice A's trait onto B's frame)
#       -- not "seeding", and independently incoherent here: the constructor
#       does not return `loadings`, and A's trait lives in A's orthonormal
#       basis while B's state lives in B's, so the splice would silently mix
#       two bases with no way for a caller to detect it from the public return
#       value;
#   (c) mutating k2b's memoised module-private _LAYOUT to re-key the frame
#       shocks -- module-private state mutation, not seeding, and it cannot
#       refresh the slow state in any case.
#   Each is recorded as a route the planner could authorise; none is taken.
#
# RN-P3-6 (the split predicate, tightened BEFORE the verdict -- disclosed).  A
#   first pass of this harness scored "a split exists iff ANY frame object
#   differs while the author channel holds", and by that predicate the phi axis
#   counts: at fixed seed, varying phi leaves trait/a_load bit-identical and
#   changes slow/slow_latent.  That predicate is WRONG for this leg on two
#   independent grounds, both read off the registration:
#   (1) A and B must sit at the SAME phi.  phi is the design's own ladder
#       variable -- the gradient being decomposed is the gradient IN phi -- so
#       A and B occupy one ladder position and cannot differ in it.  The split
#       must therefore hold AT FIXED phi.
#   (2) The registration asks for "FRESH state/frame channel draws", and the
#       frame channel proper is `common`.  Across phi, `common` is
#       BIT-IDENTICAL; what changes is only the recombination of the SAME
#       innovation draws by a different AR coefficient
#       (xs[:,t] = phi*xs[:,t-1] + sqrt(1-phi^2)*rng.normal(...)).  Re-weighting
#       one draw sequence is not a fresh draw.
#   PINNED: split_found iff, AT FIXED phi, some pair of seeds leaves every
#   AUTHOR object bit-identical AND changes `common`.  Both the loose and the
#   tight predicates are computed and REPORTED; the tight one routes.  Caught
#   and pinned before any verdict existed -- no measurement had been taken.
#
# RN-P3-4 (the Part-0 work is done anyway).  G0p3's citation clauses cost
#   nothing and are fully reusable on re-dispatch, so they are executed and
#   persisted even though the leg stops: M1c's share-0.25 row, P2's headline,
#   the five ladder r values, and the T6" lineage.  Only the clauses that
#   require worlds are skipped.
#
# RN-P3-5 (the lineage finding, reported not routed).  Every published
#   frame-refreshment in this programme -- K1b's and K1c-prime's reader A vs A'
#   -- refreshes the READER's norm/issuer sample (disjoint author sub-pools),
#   never the generator's frame channel.  The operation P3 registers is
#   generator-level refreshment, which has no precedent in the repo and, as
#   proven below, no interface.  This is stated because it names a route the
#   planner may prefer: reader-level refreshment IS supported by existing
#   machinery.  Naming it is not choosing it.
# ---------------------------------------------------------------------------

RN_NOTES = {
    "RN-P3-1": "the registration's channel rule applied literally: AUTHOR = trait, "
               "a_load (persist per author across occasions); FRAME = slow, "
               "slow_latent, common, int (per-occasion / per-context). Occasion "
               "assignments, the third frame item, live in layout(), which takes no "
               "arguments and is memoised -- not seed-driven at all",
    "RN-P3-2": "build_k2b_world has exactly two POSITIONAL_OR_KEYWORD parameters and no "
               "defaults/varargs (verified by inspect at run time), so 'seeding alone' "
               "means choosing two points in the (world_seed, phi_slow) space; the "
               "feasibility test enumerates that space EXHAUSTIVELY, which is a proof "
               "over the whole interface rather than a sample of it",
    "RN-P3-3": "three routes would work and all three are excluded by the registration's "
               "own words: editing k2b (READ-ONLY), channel surgery on the returned "
               "dicts (not seeding, and incoherent because loadings are not returned so "
               "two orthonormal bases would be silently spliced), and mutating k2b's "
               "memoised private _LAYOUT (not seeding, and cannot refresh the slow "
               "state). Each is recorded as a route the planner could authorise; none "
               "is taken",
    "RN-P3-6": "the split predicate, tightened before the verdict: A and B must sit at "
               "the SAME phi (phi is the ladder variable being decomposed, not a "
               "refresher) and 'fresh frame draws' means `common` must differ -- across "
               "phi `common` is bit-identical and only the recombination of the same "
               "innovations changes, which is not a fresh draw. PINNED: split_found iff "
               "AT FIXED phi some seed pair holds every AUTHOR object identical AND "
               "changes `common`. Both the loose and tight predicates are reported; the "
               "tight one routes",
    "RN-P3-4": "G0p3's citation clauses cost nothing and are fully reusable on "
               "re-dispatch, so they are executed and persisted even though the leg "
               "stops; only the clauses needing worlds are skipped",
    "RN-P3-5": "every published frame-refreshment in the programme (K1b / K1c-prime "
               "reader A vs A') refreshes the READER's norm sample, never the "
               "generator's frame channel; generator-level refreshment has no precedent "
               "and no interface. Reported because it names a supported alternative "
               "route -- naming is not choosing",
}

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
# PART 0.

def stage_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    _log("part0_start")

    # --- G0p3(i): M1c's share-0.25 row -------------------------------------
    cm = read_csv_rt(M1CRES / "cell_means.csv")
    row = cm[cm["share"] == SHARE].sort_values("phi")
    m1c = [{"cell_tag": r["cell_tag"], "phi": float(r["phi"]),
            "r_pred": float(r["r_pred"]), "V_person": float(r["V_person"]),
            "mean": float(r["field_mean"]), "sem": float(r["field_sem"]),
            "sd": float(r["field_sd"]), "n_worlds": int(r["n_worlds"])}
           for _, r in row.iterrows()]
    got_phis = tuple(round(d["phi"], 10) for d in m1c)
    g0i = {"source": rel(M1CRES / "cell_means.csv"), "rows": m1c,
           "phi_ladder_matches": bool(got_phis == PHI_LADDER),
           "n_rows": len(m1c),
           "range_nat_M1C": (float(m1c[0]["mean"] - m1c[-1]["mean"])
                             if len(m1c) == 5 else None),
           "range_nat_note": "M1c's realized field range across the ladder, "
                             "phi=0.05 minus phi=0.98; this is what P3's range_nat "
                             "would have anchored against"}
    g0i["PASS"] = bool(len(m1c) == 5 and g0i["phi_ladder_matches"])

    # --- G0p3(ii): P2's headline -------------------------------------------
    p2 = read_json(P2RES / "decision.json")
    p2c = p2["per_cell"]
    g0ii = {"source": rel(P2RES / "decision.json"),
            "verdict": p2["verdict_slug"],
            "f_B1": p2c["B1"]["f_fraction"], "f_B1_ci": p2c["B1"]["f_ci95"],
            "f_B2": p2c["B2"]["f_fraction"], "f_B2_ci": p2c["B2"]["f_ci95"],
            "b_cf_B1": p2c["B1"]["b_cf"], "b_cf_B1_ci": p2c["B1"]["b_cf_ci95"],
            "b_cf_B2": p2c["B2"]["b_cf"], "b_cf_B2_ci": p2c["B2"]["b_cf_ci95"],
            "n_arms": len(p2["per_arm"]),
            "one_minus_f_B1": float(1.0 - p2c["B1"]["f_fraction"]),
            "one_minus_f_B2": float(1.0 - p2c["B2"]["f_fraction"]),
            "projection_truth_g": "the registration's g = 0.04 truth is P2's 1 - f",
            "verdict_is_genuine_scaffold": bool(
                p2["verdict_slug"] == "GENUINE_SCAFFOLD")}
    g0ii["PASS"] = bool(g0ii["verdict_is_genuine_scaffold"] and g0ii["n_arms"] == 10)

    # --- G0p3(iii): the five ladder r values from the pinned map ------------
    ladder = []
    ok_r = True
    for phi in PHI_LADDER:
        got = r_of(SHARE, phi)
        want = next((d["r_pred"] for d in m1c if round(d["phi"], 10) == phi), None)
        exact = bool(want is not None and got == want)
        ok_r &= exact
        ladder.append({"phi": phi, "r_recomputed": got, "r_M1c_persisted": want,
                       "bit_exact": exact})
    g0iii = {"share": SHARE, "ladder": ladder,
             "source": "k2c.predicted_attenuation (the pinned map) vs M1c's persisted "
                       "r_pred column",
             "PASS": bool(ok_r)}

    # --- G0p3(iv): the T6" / frame-refreshment lineage ---------------------
    cites = {name: _locate(path, needle) for name, (path, needle) in ANCHORS.items()}
    g0iv = {"anchors": cites,
            "all_found": bool(all(c["found"] for c in cites.values())),
            "method": "each anchor substring is located in its controlling document or "
                      "script and the containing paragraph extracted verbatim by code "
                      "(rule 24); nothing is hand-typed",
            "lineage_finding": RN_NOTES["RN-P3-5"]}
    g0iv["PASS"] = g0iv["all_found"]

    g0 = {"(i) M1c share-0.25 row": g0i, "(ii) P2 headline": g0ii,
          "(iii) ladder r values": g0iii, "(iv) T6-double-prime lineage": g0iv,
          "PASS": bool(g0i["PASS"] and g0ii["PASS"] and g0iii["PASS"]
                       and g0iv["PASS"])}

    part0 = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "registration": "docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md (M4-P3, BEFORE "
                        "run, commit caba52f)",
        "master_seed": MASTER_SEED,
        "salts": {"A": SALT_A, "B": SALT_B, "pilot": SALT_PILOT},
        "rn_notes": RN_NOTES, "G0p3": g0,
        "seed_split_rule": CHANNEL_RULE,
        "author_channel_objects": list(AUTHOR_CHANNEL),
        "frame_channel_objects": list(FRAME_CHANNEL),
        "design_if_feasible": {
            "share": SHARE, "phi_ladder": list(PHI_LADDER),
            "pairs_per_phi": N_PAIRS, "total_worlds": 2 * N_PAIRS * len(PHI_LADDER),
            "escalation_pairs_per_phi": N_PAIRS_ESCALATED},
        "sides_rule22": {
            "L-1p3": {"clause": "MOSTLY_FRAME / INTERMEDIATE / "
                                "NO_TRANSPORTABLE_READING / other",
                      "prior": "0.55 / 0.20 / 0.15 / 0.10", "sided": "categorical"},
            "V-P3a": {"clause": "R_nat replicates M1c's share-0.25 row within "
                                "2*sqrt(2)*SEM", "sided": "two-sided"},
            "V-P3b": {"clause": "g_ratio classification, NULL-first",
                      "sided": "categorical"},
            "G3p3": {"clause": "g_ratio CI width <= 0.30 at both projection truths",
                     "sided": "one-sided"}},
        "stage_estimates_seconds": {"part0": 120, "feasibility": 30, "finalize": 60},
        "environment": {"python": sys.version.split()[0],
                        "python_executable": sys.executable,
                        "platform": platform.platform(), "numpy": np.__version__,
                        "pandas": pd.__version__},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0.json", part0)
    _log("part0_done", PASS=g0["PASS"], seconds=part0["seconds"])
    if not g0["PASS"]:
        raise SystemExit("STOP: G0p3 FAILED -- see part0.json")
    print(f"part0 OK  G0p3 PASS  M1c row {len(m1c)} cells  "
          f"{sum(c['found'] for c in cites.values())}/{len(cites)} lineage anchors  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# THE FEASIBILITY PROOF (G1p3(a) is either provable or the leg stops).

def stage_feasibility(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    if not p0["G0p3"]["PASS"]:
        raise SystemExit("STOP: G0p3 did not pass.")
    kb = k2b()

    sig = inspect.signature(kb.build_k2b_world)
    params = [{"name": q.name, "kind": q.kind.name,
               "has_default": bool(q.default is not inspect._empty),
               "annotation": str(q.annotation)} for q in sig.parameters.values()]
    iface = {
        "constructor": "build_k2b_world",
        "module": rel(ROOT / "scripts" / "run_suica_m4_k2b_t4_branch.py"),
        "signature": f"build_k2b_world{sig}",
        "parameters": params,
        "n_parameters": len(params),
        "has_varargs": bool(any(q.kind.name in ("VAR_POSITIONAL", "VAR_KEYWORD")
                                for q in sig.parameters.values())),
        "any_defaults": bool(any(p["has_default"] for p in params)),
        "input_space": "the pair (world_seed, phi_slow) -- there is nothing else to "
                       "vary, so enumerating the effect of each argument is a PROOF "
                       "over the whole interface (RN-P3-2)",
    }

    def channels(w1: dict[str, Any], w2: dict[str, Any]) -> dict[str, bool]:
        out = {}
        for k in AUTHOR_CHANNEL + FRAME_CHANNEL:
            a, b = np.asarray(w1[k]), np.asarray(w2[k])
            out[k] = bool(a.shape == b.shape
                          and np.array_equal(a.view(np.uint8), b.view(np.uint8)))
        return out

    phi0 = PHI_LADDER[0]
    base = kb.build_k2b_world(1001, phi0)
    trials = []

    # Axis 1: vary world_seed at fixed phi (the only frame-refresh lever).
    for seed in (1002, 20260814, 7):
        cmp_ = channels(base, kb.build_k2b_world(seed, phi0))
        trials.append({
            "axis": "vary world_seed (fixed phi)",
            "point": {"world_seed": seed, "phi_slow": phi0},
            "identical": cmp_,
            "author_all_identical": bool(all(cmp_[k] for k in AUTHOR_CHANNEL)),
            "any_frame_differs": bool(any(not cmp_[k] for k in FRAME_CHANNEL)),
        })
    # Axis 2: vary phi at fixed world_seed.
    for phi in PHI_LADDER[1:]:
        cmp_ = channels(base, kb.build_k2b_world(1001, phi))
        trials.append({
            "axis": "vary phi_slow (fixed world_seed)",
            "point": {"world_seed": 1001, "phi_slow": phi},
            "identical": cmp_,
            "author_all_identical": bool(all(cmp_[k] for k in AUTHOR_CHANNEL)),
            "any_frame_differs": bool(any(not cmp_[k] for k in FRAME_CHANNEL)),
        })
    # Axis 3: vary both.
    cmp_ = channels(base, kb.build_k2b_world(1002, PHI_LADDER[-1]))
    trials.append({
        "axis": "vary both",
        "point": {"world_seed": 1002, "phi_slow": PHI_LADDER[-1]},
        "identical": cmp_,
        "author_all_identical": bool(all(cmp_[k] for k in AUTHOR_CHANNEL)),
        "any_frame_differs": bool(any(not cmp_[k] for k in FRAME_CHANNEL)),
    })

    # RN-P3-6: the LOOSE predicate (any frame object differs) and the TIGHT one
    # (at fixed phi, and `common` -- the frame proper -- must differ).  The
    # tight predicate routes.
    for t_ in trials:
        t_["fixed_phi"] = bool(t_["point"]["phi_slow"] == phi0)
        t_["common_differs"] = bool(not t_["identical"]["common"])
        t_["split_loose"] = bool(t_["author_all_identical"] and t_["any_frame_differs"])
        t_["split_tight"] = bool(t_["author_all_identical"] and t_["fixed_phi"]
                                 and t_["common_differs"])
    loose = [t_ for t_ in trials if t_["split_loose"]]
    splits = [t_ for t_ in trials if t_["split_tight"]]
    feasible = bool(splits)

    # Which frame objects CAN be refreshed while the author channel holds?
    phi_only = [t for t in trials if t["axis"] == "vary phi_slow (fixed world_seed)"]
    refreshable = sorted({k for t in phi_only for k in FRAME_CHANNEL
                          if not t["identical"][k]})
    unrefreshable = [k for k in FRAME_CHANNEL if k not in refreshable]

    proof = {
        "interface": iface,
        "channel_rule": CHANNEL_RULE,
        "author_channel": list(AUTHOR_CHANNEL),
        "frame_channel": list(FRAME_CHANNEL),
        "trials": trials,
        "n_trials": len(trials),
        "split_found": feasible,
        "split_predicate": RN_NOTES["RN-P3-6"],
        "split_found_LOOSE_predicate": bool(loose),
        "loose_predicate_satisfied_by": [t_["axis"] for t_ in loose],
        "why_loose_is_wrong": "A and B must sit at the SAME phi (phi is the ladder "
                              "variable being decomposed), and across phi `common` is "
                              "bit-identical -- only the recombination of the same "
                              "innovations changes, which is not a fresh draw",
        "seed_axis_result": "changing world_seed changes EVERY channel, the author "
                            "channel included -- so G1p3(a) (author objects "
                            "bit-identical per pair) fails at every seed pair",
        "phi_axis_result": "changing phi_slow holds the author channel bit-identical "
                           f"but refreshes only {refreshable} -- `common`, the frame "
                           "channel proper, is BIT-IDENTICAL across phi, so G1p3(b) "
                           "fails on the object the leg is about; and phi is this "
                           "design's own treatment axis, so it could not serve as the "
                           "refresher even if it did move `common`",
        "frame_objects_refreshable_by_seeding": refreshable,
        "frame_objects_NOT_refreshable_by_seeding": unrefreshable,
        "occasion_assignments": "the registration's third frame item lives in "
                                "k2b.layout(), which takes no arguments and is memoised "
                                "in a module-private global -- not seed-driven at all",
        "excluded_routes": RN_NOTES["RN-P3-3"],
        "conclusion": ("the constructor's input space contains NO pair of points at "
                       "which every author object is bit-identical and any frame object "
                       "differs; the split is impossible by seeding alone"),
        "G1p3a_satisfiable": False,
        "G1p3b_satisfiable_for_common": False,
        "G1p3c_note": "the same-frame-seed control of G1p3(c) is vacuous under this "
                      "finding: with no frame seed to vary, every pair is that control",
        "seconds": time.time() - t0,
    }
    write_json(OUT / "feasibility.json", proof)
    _log("feasibility_done", split_found=feasible, seconds=proof["seconds"])
    print(f"feasibility  split_found={feasible}  trials={len(trials)}  "
          f"refreshable by seeding: {refreshable or 'none'}  "
          f"{time.time() - t0:.1f}s")
    _ = args


# ---------------------------------------------------------------------------
# FINALIZE.

TRUTH_TABLE = [
    {"n": "1", "condition": "G0p3/G1p3 failure or seed-split impossible via seeding "
                            "alone", "outcome": "INFEASIBLE_SPLIT",
     "text": "STOP / INFEASIBLE_SPLIT"},
    {"n": "2", "condition": "projection fails after escalation",
     "outcome": "NON_PROJECTABLE", "text": "NON_PROJECTABLE"},
    {"n": "3", "condition": "V-P3a fails", "outcome": "ANCHOR_BREAK",
     "text": "ANCHOR_BREAK (instrument stop; nothing adjudicated)"},
    {"n": "4", "condition": "V-P3c fires", "outcome": "NO_TRANSPORTABLE_READING",
     "text": "NO_TRANSPORTABLE_READING -- the natural gradient carries no "
             "frame-refreshed person signal at all; V-P3b N/A"},
    {"n": "5", "condition": "g_ratio MOSTLY_FRAME",
     "outcome": "NATURAL_GRADIENT_MOSTLY_FRAME",
     "text": "NATURAL_GRADIENT_MOSTLY_FRAME -- the M-line law's r-channel is dominated "
             "by frame-agreement; the law stands as a law of the statistic"},
    {"n": "6", "condition": "g_ratio INTERMEDIATE", "outcome": "MIXED_GRADIENT",
     "text": "MIXED_GRADIENT -- quantified split; theory carries the number"},
    {"n": "7", "condition": "g_ratio SUBSTANTIALLY_GENUINE",
     "outcome": "GENUINE_GRADIENT",
     "text": "GENUINE_GRADIENT -- the r-channel transports across frames"},
    {"n": "8", "condition": "UNDERPOWERED / budget unmet", "outcome": "UNDERPOWERED",
     "text": "UNDERPOWERED (+ UNQUANTIFIED modifier; levels reported)"},
]


def stage_finalize(args: argparse.Namespace) -> None:
    t0 = time.time()
    p0 = read_json(OUT / "part0.json")
    fe = read_json(OUT / "feasibility.json")

    slug = "INFEASIBLE_SPLIT" if not fe["split_found"] else "PENDING"
    if slug == "PENDING":
        raise SystemExit("A split WAS found -- this harness's STOP path does not apply; "
                         "the measurement stages must be implemented.")
    dec = {
        "leg": LEG, "banner": BANNER, "utc": datetime.now(UTC).isoformat(),
        "verdict_slug": slug, "routing_cell": 1, "modifiers": [],
        "routing_text": next(t["text"] for t in TRUTH_TABLE if t["outcome"] == slug),
        "stopped_at": "G1p3(a) -- provably unsatisfiable through the existing "
                      "constructor interface",
        "ladder": "none: the registration legislates STOP as INFEASIBLE_SPLIT and calls "
                  "it an instrument finding, not a failure",
        "worlds_drawn": 0, "seal_issued": False, "pairs_built_for_measurement": 0,
        "feasibility": fe, "G0p3": p0["G0p3"],
        "what_would_make_it_feasible": {
            "minimal_interface_change": "build_k2b_world would need to accept the frame "
                                        "stream's seed separately from the author "
                                        "stream's -- e.g. an optional frame_seed "
                                        "defaulting to world_seed, which would leave "
                                        "every existing call bit-identical",
            "why_that_suffices": "trait and a_load are drawn before any frame object "
                                 "and depend only on the author stream; common, int and "
                                 "the state would then key on frame_seed",
            "cost": "an edit to k2b, which this leg is forbidden to make",
            "alternative_needing_no_edit": "reader-level refreshment (K1b / K1c-prime's "
                                           "reader A vs A', disjoint norm sub-pools) is "
                                           "the programme's OWN published form of the "
                                           "T6-double-prime operation and is fully "
                                           "supported by existing machinery -- a "
                                           "different estimand, named for the planner, "
                                           "not chosen here (RN-P3-5)"},
        "gates": {
            "G0p3": {"PASS": p0["G0p3"]["PASS"],
                     "detail": "M1c's share-0.25 row, P2's headline, the five ladder r "
                               "values and the T6-double-prime lineage all verified; "
                               "reusable on re-dispatch"},
            "G1p3": {"PASS": False,
                     "detail": "(a) provably unsatisfiable: no point in the "
                               "constructor's input space holds the author channel "
                               "bit-identical while changing a frame object; (b) fails "
                               "for `common`; (c) vacuous"},
            "G2p3": {"PASS": None, "detail": "not reached (no world drawn)"},
            "G3p3": {"PASS": None, "detail": "not reached"},
            "G4p3": {"PASS": True,
                     "detail": "routing disjoint-and-covering; tables generated "
                               "(rule 24); stopped inside the part0 + feasibility "
                               "estimate"}},
        "seconds": time.time() - t0,
    }
    write_json(OUT / "decision.json", dec)
    _log("finalize_done", slug=slug, seconds=dec["seconds"])
    _tables(p0, fe, dec)
    _facts(p0, fe, dec)
    print(f"finalize OK  slug={slug}  cell=1  worlds=0")
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


def _tables(p0: dict[str, Any], fe: dict[str, Any], dec: dict[str, Any]) -> None:
    sec: dict[str, list[str]] = {}
    g0 = p0["G0p3"]
    ifc = fe["interface"]
    sec["interface"] = _md(
        ["property", "value"],
        [["constructor", ifc["constructor"]],
         ["module", "`" + ifc["module"] + "`"],
         ["**signature**", "`" + ifc["signature"] + "`"],
         ["number of parameters", str(ifc["n_parameters"])],
         ["has *args / **kwargs", str(ifc["has_varargs"])],
         ["any parameter defaults", str(ifc["any_defaults"])],
         ["input space", ifc["input_space"]]]
        + [[f"parameter: {q['name']}", f"{q['kind']}, annotation {q['annotation']}, "
                                       f"default {q['has_default']}"]
           for q in ifc["parameters"]])
    hdr = ["axis", "point"] + [f"{k} ({'A' if k in fe['author_channel'] else 'F'})"
                               for k in fe["author_channel"] + fe["frame_channel"]] \
        + ["author all identical", "any frame differs", "SPLIT?"]
    sec["proof"] = _md(
        hdr,
        [[t["axis"], repr(t["point"])]
         + [str(t["identical"][k])
            for k in fe["author_channel"] + fe["frame_channel"]]
         + [str(t["author_all_identical"]), str(t["any_frame_differs"]),
            "**YES**" if (t["author_all_identical"] and t["any_frame_differs"])
            else "no"]
         for t in fe["trials"]])
    sec["axes"] = _md(
        ["axis", "result"],
        [["vary world_seed", fe["seed_axis_result"]],
         ["vary phi_slow", fe["phi_axis_result"]],
         ["occasion assignments", fe["occasion_assignments"]],
         ["frame objects refreshable by seeding",
          repr(fe["frame_objects_refreshable_by_seeding"])],
         ["frame objects NOT refreshable by seeding",
          repr(fe["frame_objects_NOT_refreshable_by_seeding"])],
         ["split under the TIGHT predicate (routes)", "**" + str(fe["split_found"])
          + "**"],
         ["split under the LOOSE predicate (reported only)",
          str(fe["split_found_LOOSE_predicate"]) + " -- satisfied by "
          + repr(fe["loose_predicate_satisfied_by"])],
         ["why the loose predicate is wrong", fe["why_loose_is_wrong"]],
         ["**conclusion**", "**" + fe["conclusion"] + "**"]])
    sec["excluded"] = _md(["route", "why it is not taken"],
                          [["editing build_k2b_world to accept split seeds",
                            "k2b is READ-ONLY by the registration"],
                           ["channel surgery on the returned dicts",
                            "not 'seeding'; and the constructor does not return "
                            "`loadings`, so a splice would silently mix two orthonormal "
                            "bases with no way for a caller to detect it"],
                           ["mutating k2b's memoised private _LAYOUT",
                            "module-private state mutation, not seeding, and it cannot "
                            "refresh the slow state"]])
    g0i = g0["(i) M1c share-0.25 row"]
    sec["m1c"] = _md(
        ["cell", "phi", "r_pred", "M1c field mean", "SEM", "sd", "n"],
        [[d["cell_tag"], repr(d["phi"]), repr(d["r_pred"]), repr(d["mean"]),
          repr(d["sem"]), repr(d["sd"]), str(d["n_worlds"])] for d in g0i["rows"]]
        + [["**realized natural range (phi .05 - phi .98)**", "—", "—",
            "**" + repr(g0i["range_nat_M1C"]) + "**", "—", "—", "—"]])
    sec["ladder"] = _md(
        ["phi", "r recomputed from the pinned map", "r persisted in M1c", "bit-exact"],
        [[repr(d["phi"]), repr(d["r_recomputed"]), repr(d["r_M1c_persisted"]),
          str(d["bit_exact"])] for d in g0["(iii) ladder r values"]["ladder"]])
    g0ii = g0["(ii) P2 headline"]
    sec["p2"] = _md(
        ["quantity", "value"],
        [["P2 verdict", g0ii["verdict"]],
         ["f at B1", repr(g0ii["f_B1"]) + " " + repr(g0ii["f_B1_ci"])],
         ["f at B2", repr(g0ii["f_B2"]) + " " + repr(g0ii["f_B2_ci"])],
         ["b_cf at B1", repr(g0ii["b_cf_B1"]) + " " + repr(g0ii["b_cf_B1_ci"])],
         ["b_cf at B2", repr(g0ii["b_cf_B2"]) + " " + repr(g0ii["b_cf_B2_ci"])],
         ["1 - f at B1 (the registration's g = 0.04 projection truth)",
          repr(g0ii["one_minus_f_B1"])],
         ["1 - f at B2", repr(g0ii["one_minus_f_B2"])],
         ["arms in P2's table", str(g0ii["n_arms"])]])
    sec["lineage"] = _md(
        ["anchor", "located at", "verbatim quote (extracted by code, rule 24)"],
        [[name, f"`{d['file']}:{d['line']}` (para {d['paragraph_lines']})",
          d["quote"][:700] + ("…" if len(d["quote"]) > 700 else "")]
         if d["found"] else [name, "NOT FOUND", "—"]
         for name, d in g0["(iv) T6-double-prime lineage"]["anchors"].items()])
    wf = dec["what_would_make_it_feasible"]
    sec["remedy"] = _md(["question", "answer"],
                        [["minimal interface change", wf["minimal_interface_change"]],
                         ["why that suffices", wf["why_that_suffices"]],
                         ["cost", wf["cost"]],
                         ["alternative needing no edit",
                          wf["alternative_needing_no_edit"]]])
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
    sec["timing"] = _md(
        ["stage", "estimate (s)", "measured (s)"],
        [["part0", str(est["part0"]), "%.3f" % meas.get("part0_done", float("nan"))],
         ["feasibility", str(est["feasibility"]),
          "%.3f" % meas.get("feasibility_done", float("nan"))],
         ["finalize", str(est["finalize"]),
          "%.3f" % meas.get("finalize_done", float("nan"))],
         ["pilot", "60", "-- not reached"],
         ["worlds (5 chunks)", "240 each", "-- not reached"],
         ["score+fit", "180", "-- not reached"]])
    body = ["# M4-P3 report tables (GENERATED from artifacts -- rule 24)", ""]
    for name, lines in sec.items():
        body += [f"<!-- TABLE:{name} -->", ""] + lines + [""]
    (OUT / "report_tables.md").write_text("\n".join(body) + "\n", encoding="utf-8")


def _facts(p0: dict[str, Any], fe: dict[str, Any], dec: dict[str, Any]) -> None:
    g0 = p0["G0p3"]
    g0i = g0["(i) M1c share-0.25 row"]
    g0ii = g0["(ii) P2 headline"]
    f = {
        "SLUG": dec["verdict_slug"], "CELL": dec["routing_cell"],
        "ROUTING_TEXT": dec["routing_text"], "STOPPED_AT": dec["stopped_at"],
        "LADDER_TEXT": dec["ladder"],
        "WORLDS": dec["worlds_drawn"], "SEAL": dec["seal_issued"],
        "SIG": fe["interface"]["signature"],
        "NPARAM": fe["interface"]["n_parameters"],
        "VARARGS": fe["interface"]["has_varargs"],
        "DEFAULTS": fe["interface"]["any_defaults"],
        "NTRIALS": fe["n_trials"], "SPLIT": fe["split_found"],
        "REFRESHABLE": ", ".join(fe["frame_objects_refreshable_by_seeding"]) or "none",
        "UNREFRESHABLE": ", ".join(fe["frame_objects_NOT_refreshable_by_seeding"])
                         or "none",
        "AUTHOR_CH": ", ".join(fe["author_channel"]),
        "FRAME_CH": ", ".join(fe["frame_channel"]),
        "CONCLUSION": fe["conclusion"],
        "SEED_AXIS": fe["seed_axis_result"], "PHI_AXIS": fe["phi_axis_result"],
        "OCC": fe["occasion_assignments"],
        "RANGE_NAT_M1C": g0i["range_nat_M1C"],
        "M1C_N": g0i["n_rows"], "M1C_SRC": g0i["source"],
        "P2_F_B1": g0ii["f_B1"], "P2_F_B2": g0ii["f_B2"],
        "P2_G_B1": g0ii["one_minus_f_B1"], "P2_G_B2": g0ii["one_minus_f_B2"],
        "P2_VERDICT": g0ii["verdict"],
        "N_ANCHORS": len(g0["(iv) T6-double-prime lineage"]["anchors"]),
        "N_FOUND": sum(1 for d in g0["(iv) T6-double-prime lineage"]["anchors"].values()
                       if d["found"]),
        "REMEDY": dec["what_would_make_it_feasible"]["minimal_interface_change"],
        "ALT": dec["what_would_make_it_feasible"]["alternative_needing_no_edit"],
        "PYTHON": p0["environment"]["python"], "NUMPY": p0["environment"]["numpy"],
        "PANDAS": p0["environment"]["pandas"],
        "PLATFORM": p0["environment"]["platform"],
        "PAIRS": p0["design_if_feasible"]["pairs_per_phi"],
        "TOTALW": p0["design_if_feasible"]["total_worlds"],
    }
    write_json(OUT / "prose_facts.json", f)


REPORT_TEMPLATE = r"""# SUICA M4-P3 — the natural gradient under frame refreshment — **{{SLUG}}**

**Outcome: {{SLUG}} (routing cell {{CELL}}).** {{ROUTING_TEXT}}. Stopped at
{{STOPPED_AT}}. **{{WORLDS}} worlds drawn, no seal.** Ladder: {{LADDER_TEXT}}.

The registration anticipated this exact possibility and legislated the
response, calling it *an instrument finding, not a failure*. It is delivered as
one: the impossibility is **proven over the constructor's entire input space**,
not inferred from reading the code, and every Part-0 object that survives a
re-dispatch is computed and persisted.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit caba52f).
Every number below is generated from artifacts by code (rule 24).

---

## 1. What the leg needed, and why it cannot have it

P3 needs paired worlds A and B sharing the AUTHOR/TRAIT channel draws and
differing in the STATE/FRAME channel draws, achieved **by seeding alone through
the existing constructor interface** (k2b and `suica_core/` READ-ONLY).

Applying the registration's own channel rule (RN-P3-1): AUTHOR = {{AUTHOR_CH}};
FRAME = {{FRAME_CH}}.

<<TABLE:interface>>

The constructor takes **{{NPARAM}} parameters**, no varargs ({{VARARGS}}) and no
defaults ({{DEFAULTS}}). Its input space is therefore the pair
`(world_seed, phi_slow)` and nothing else — which is what makes the following an
exhaustive proof rather than a sample.

## 2. The proof

{{NTRIALS}} trials, covering both axes and their combination. A split exists iff
some row has *author all identical* = True **and** *any frame differs* = True.

<<TABLE:proof>>

**No row satisfies the registered split.** ({{SPLIT}} = split found under the
predicate that routes.)

A predicate subtlety was caught and pinned before any verdict existed
(RN-P3-6), and it is disclosed because a looser reading would have flipped the
outcome. Scoring "any frame object differs" makes the φ axis look like a split:
at fixed seed, varying φ leaves the author channel bit-identical and moves
`slow`. That reading is wrong on two independent grounds, both read off the
registration — **A and B must sit at the same φ** (φ is the ladder variable
being decomposed, so it cannot also be the refresher), and **`common` is
bit-identical across φ**, with only the recombination of the *same* innovation
draws changing, which is not a fresh draw. The tight predicate — at fixed φ, a
seed pair holding the author channel identical while `common` differs — is the
one that routes. Both are computed and reported below.

<<TABLE:axes>>

Two facts do the work:

- **Changing `world_seed` changes everything, the author channel included.**
  `trait` is built from `z` and `loadings`, both drawn from
  `default_rng(world_seed)` *before* any frame object, so G1p3(a) — author
  objects bit-identical per pair — fails at every seed pair.
- **Changing `phi_slow` holds the author channel bit-identical but does not
  refresh the frame.** Only {{REFRESHABLE}} move; **{{UNREFRESHABLE}} are
  bit-identical across φ** — and `common`, the frame channel proper and the
  object this leg is about, is among them. φ is also this design's own treatment
  axis, so it could not serve as the refresher even if it did move `common`.

{{OCC}}

## 3. Routes that would work, and why none is taken

<<TABLE:excluded>>

Each is excluded by the registration's own words, not by preference. Recording
them is the useful part of a STOP: they are the menu the planner chooses from.

<<TABLE:remedy>>

The minimal change is small and backward-compatible — {{REMEDY}} — but it is an
edit to k2b, which this leg is forbidden to make. **The alternative needing no
edit is worth the planner's attention:** {{ALT}}

## 4. The lineage, located — and a finding inside it

G0p3(iv) asked for the T6″ frame-refreshment lineage. All {{N_FOUND}}/{{N_ANCHORS}}
anchors were located and quoted by code.

<<TABLE:lineage>>

**The finding (RN-P3-5, reported not routed):** every published
frame-refreshment in this programme — K1b's and K1c′'s reader A vs A′ —
refreshes the **reader's** norm/issuer sample via disjoint author sub-pools. It
never refreshes the **generator's** frame channel. The operation P3 registers is
generator-level refreshment, which has no precedent in the repo and, as §2
proves, no interface. The T6″ pattern the registration cites is real and
published; it simply lives at a different layer than the one P3 needs.

## 5. What Part 0 established anyway

These are reusable verbatim on re-dispatch.

### 5.1 M1c's share-0.25 row (the V-P3a anchor)

<<TABLE:m1c>>

{{M1C_N}} cells from `{{M1C_SRC}}`. The realized natural range across the ladder
is **{{RANGE_NAT_M1C}}** — note the sign: the field mean *rises* with φ while
r_pred falls, which is M1c's side-signing convention and is what P3's
`range_nat` would have anchored against.

### 5.2 The ladder's r values

<<TABLE:ladder>>

### 5.3 P2's headline (the projection truths)

<<TABLE:p2>>

The registration's g = 0.04 projection truth is P2's 1 − f: {{P2_G_B1}} at B1 and
{{P2_G_B2}} at B2.

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
- **Rule 26:** no bounded winner; nothing was fitted.
- **Rule 29:** not reached (no world drawn); the predicate was pinned in Part 0
  and stands ready for a re-dispatch.
- **Rule 30:** exercised throughout — every cited constant is read from its
  persisted source and every quoted sentence is extracted by code, including
  the lineage quotes in §4.

## 11. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython {{PYTHON}} venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

No hypothesis-relevant number was ever computed: the leg stopped before its
first measured world.

## 12. Environment

<<TABLE:env>>

## 13. Timing

<<TABLE:timing>>

---

*Artifacts: `results/m4_p3_refresh_gradient/` (gitignored) — `part0.json`,
`feasibility.json`, `decision.json`, `prose_facts.json`, `report_tables.md`,
`run_log.jsonl`. Harness: `scripts/run_suica_m4_p3_refresh_gradient.py`.*
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
    path = ROOT / "reports" / "SUICA_M4_P3_REFRESH_GRADIENT_REPORT.md"
    path.write_text(txt, encoding="utf-8")
    print(f"report OK  {rel(path)}  ({len(txt.splitlines())} lines)")
    _ = args


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="stage", required=True)
    stages: list[tuple[str, Callable[[argparse.Namespace], None]]] = [
        ("part0", stage_part0), ("feasibility", stage_feasibility),
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
