#!/usr/bin/env python3
"""M4-J2: is the harm boundary predictable, or is the basis-shrinkage repair
undeployable in principle?

EXPLORATORY (open-exploration phase, operator directive 2026-08-01; design and
leans registered in docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, "M4-J2
registration" (2026-08-03, BEFORE run); ledger row M4-J2). Machinery is
IMPORTED and REUSED wherever an existing seam exists. This leg adds NO new
basis-construction or estimator code: it calls, literally and unchanged,
h2._contexts_for_world, h2._ingredients_for_arm (the exact ingredients
function H3/H4's shrinkage dispatch consumes for every ladder arm),
h2._arm_offset_and_shares (M4-E2/M4-H2's own S1-S4 decomposition), and
e2._response_direction_machinery / _s1_patterns / _s2_patterns / _common_core
(M4-E2's own S1/S2 common-core machinery). The only NEW code this leg writes
is: (1) glue to run H2's own per-world S1/S2-pattern-then-shares recipe
(h2._run_arm, lines 943-969) on 5 worlds H2 itself never touched (H2 is a
3-world leg; M4-J1 already established the 8-world `D1_WORLDS` set as this
program's wider-world convention) -- the same "call certified per-world
machinery across a wider world set" pattern M4-J1 itself used for
`colstd_alpha_0.10`; (2) a condition-number/effective-rank statistic of the
SAME retained eigenspectrum H3's shrinkage repair already regularizes,
computed via a disclosed near-duplicate read of `ingredients["eigenvalues"]`/
`ingredients["retained"]`; and (3) rank-separation and bootstrap-Spearman
helpers for the across-WORLD (not across-repetition/author) analysis this
leg's leans require, a grain no earlier leg in this line used because no
earlier leg asked a question whose unit of analysis is "the world itself."
The deployed estimator and basis-construction paths
(`suica_core/m4_condition_manifold_estimator.py`,
`suica_core/m4_chart_ecology_estimator.py`) are READ-ONLY throughout.

===========================================================================
WHY THIS LEG EXISTS
===========================================================================
M4-J1 found the basis-shrinkage repair (M4-H3/H4) worsens recovery decisively
in exactly two of the eight `D1_WORLDS` -- `history_gated_ecology` and
`topology_mismatch` -- at both certified ratios (0.20, 1.00), both truth
budgets, 8/8 cells OUTSIDE the +/-0.02 margin by 2.68x-10.3x. Neither harm
world is a `HIGH_GAP_WORLDS` member, so the original 3-world certification
could not have surfaced this. M4-J1's own executing agent declined to
speculate about what the two harm worlds share. This leg asks the question
directly: is the harm boundary predictable from a property measurable BEFORE
applying the repair? If yes, the repair is salvageable behind a gating rule.
If no, one cannot know in advance whether a new corpus is a harm case, and
the repair is undeployable in principle -- a measured limit, not a shortfall.

===========================================================================
PART 0 -- DISCRIMINATOR INVENTORY (registered, fixed hypothesis space)
===========================================================================
Measured at `deployed` on all eight `D1_WORLDS`:
 (i)   baseline recovery error -- deployed `e_arm_true`, author-grain mean,
       c=1.0, per world, both TRUTH_BUDGETS (4.0 primary, matching M4-J1's
       own primary report table; 8.0 companion). SOURCE: read directly
       (NOT recomputed) from `results/m4_j1_repair_generalization/
       author_level_truth_rows.csv` -- identity by construction, the
       strongest possible form of "reproduces M4-J1's persisted value."
       `linear_null_ecology`/`fast_return_equal_marginal` carry M4-G2's own
       inherited near-zero-denominator pathology (~1e9); reported in the full
       inventory, EXCLUDED from every lean/correlation computation exactly as
       M4-J1's own lean (b)/(c) excluded them (VALID_TRUTH_WORLDS, 6 of 8).
 (ii)  baseline displacement magnitude -- deployed `disp_v2`, median over 8
       repetitions, per world. SOURCE: read directly (NOT recomputed) from
       `results/m4_j1_repair_generalization/disp_rows.csv`. No truth-budget
       pathology; defined on all 8 worlds.
 (iii) S3 share -- M4-E2's registered-order S3 (`S3_norm_scale_modes`) share
       of the discovery objective's offset `delta`, at `deployed`, per world.
       FRESH compute: `h2._arm_offset_and_shares(world, contexts, "deployed",
       s1_patterns, s2_patterns)["registered_shares"]["S3_norm_scale_modes"]`
       -- a world-level census statistic (GPA consensus across the world's 8
       repetitions), no CI, matching H3/H4's own "S1-S4 shares... WORLD-level
       census (n=3, no CI)" convention, extended here to n=8 worlds.
 (iv)  S4 share -- the same decomposition's residual share,
       `registered_shares["S4_residual"]`. Comes free from the same call.
 (v)   effective-rank / conditioning statistic of the basis -- the retained
       eigenspectrum `h2._ingredients_for_arm(context, "deployed")` builds is
       LITERALLY the object H3's `_whitening_for_shrinkage_ratio` regularizes
       (`lambda = ratio * median(eig_retained)`, `1/sqrt(eig + lambda)`); a
       basis whose retained eigenvalues are widely spread (high condition
       number) is shrunk non-uniformly by a fixed-lambda regularizer in a way
       a tightly-clustered spectrum is not -- a mechanistically motivated,
       measurable-before-the-repair candidate. PRIMARY: condition number
       kappa = max(eig_retained)/min(eig_retained), per repetition, median
       over 8 reps -> one number per world (matching this leg's and the
       line's own rep-to-world median-aggregation convention, e.g. M4-J1's
       own `deployed_disp_median_by_world`). COMPANION (same registered item,
       reported not separately scored): effective rank / participation ratio
       = (sum eig_retained)^2 / sum(eig_retained^2), same aggregation.
       Cross-checked per repetition against `leg10._freeze_ingredients`, an
       INDEPENDENTLY WRITTEN "follows freeze_m4_condition_transform line by
       line" copy of the identical eigendecomposition -- an internal
       consistency check, not a registered external anchor (no M4-J1 or H2
       artifact persists this exact quantity to anchor against).

Candidates discovered later are reported, never scored (registered rule).

--- Registered ambiguity resolution #1: world-scope for the Part 0 inventory
    vs the leans (disclosed, resolved BEFORE adjudicating any number) ------
Part 0's own text says "measure... on all eight worlds," but the PIVOT text
says "...separates the two harm worlds from the SIX SAFE ones" -- six, not
eight. `linear_null_ecology` and `fast_return_equal_marginal` were never
classified as safe OR harmful by M4-J1's lean (b) (they were EXCLUDED_TRUTH_
WORLDS, untested for safety, not confirmed-safe) -- including them in a
"harm vs safe" comparison is a category error, since "safe" is not a status
they hold. READING A (literal Part 0, n=8): report raw discriminator values
for all 8 worlds (done, in the full inventory table). READING B (the PIVOT's
own "six safe ones," n=6 = VALID_TRUTH_WORLDS): the population for every
rank-separation test, every correlation, and every adjudicated lean. This
leg ADOPTS READING B for all adjudication -- it is what "the two harm worlds
from the six safe ones" literally denotes, it is the only population where
"safe" is a status actually established (by M4-J1's own lean b), and "recovery
BENEFIT" (lean a's dependent variable) is only a non-pathological quantity on
VALID_TRUTH_WORLDS in the first place (M4-J1's own inherited restriction).
Reading A is still published in full (the inventory table) for transparency.

--- Registered ambiguity resolution #2: what "separates cleanly" means, and
    a disclosed, NOT-softened finding it produces (resolved BEFORE
    adjudicating any number; the finding itself only exists after computing,
    disclosed as found) --------------------------------------------------
Lean (b)'s own text defines "separates" as a pure RANK criterion: "the two
harm worlds are exactly the two lowest... -- a rank separation, not merely a
correlation." Lean (c) uses the same word ("does NOT separate") applied to
displacement. Applied literally and identically to both discriminators over
VALID_TRUTH_WORLDS, full-precision recomputation (not the report's rounded
2-decimal table) shows BOTH (i) baseline error AND (ii) baseline displacement
put `history_gated_ecology` and `topology_mismatch` as the exactly-two-lowest
world -- i.e., the pure rank criterion, applied honestly, does NOT cleanly
distinguish competence from displacement the way the registration's own
motivating text ("topology_mismatch is mid-range at 13.18") anticipated. This
leg reports this plainly (lean (c) MISSES under the literal rank test -- not
softened) and additionally reports, for every discriminator, a bootstrap-
Spearman correlation against recovery benefit -- the STRONGER test lean (a)
itself uses -- to see whether competence's relationship to benefit is any
tighter/more certain than displacement's, since a 2-of-6 rank coincidence is
a weak, small-n-prone criterion on its own (n=6 has only C(11,6)=462 distinct
6-of-6-with-replacement resamples; this is disclosed at G0).

===========================================================================
GATES (registered)
===========================================================================
G0 POWER: n=8 worlds (n=6 for every truth-derived quantity) is small; MDE and
what this design can/cannot detect stated explicitly before adjudicating.
G1 ANCHOR: disp_v2 (this leg's own recomputation, a side product of the S3/S4
machinery) reproduces M4-J1's persisted disp_v2 to <=1e-12 on ALL 8 worlds
(stronger than M4-J1's own 3-world self-anchor, since M4-J1's file already
covers all 8); S3/S4 shares and offset_norm reproduce H2's own persisted
`offset_shares_by_arm.csv` to <=1e-12 on the 3 `HIGH_GAP_WORLDS` (H2 never
computed the 5 FRESH_COMPANION_WORLDS, so this is what licenses them as an
EXTENSION); baseline error/displacement are READ, not recomputed, from
M4-J1's own files (identity by construction).
G2 DISCRIMINATOR LIVENESS: each of the 5 candidates must vary materially
across the 8 worlds (registered bar: range >= 5% of the median |value|) -- a
constant discriminator is VACUOUS, not a null.
G3 TRUTH-PATH INVARIANCE where applicable: N/A and stated as such -- this leg
introduces no new truth-recovery (flat-vs-regenerated) computation; every
truth-derived number is read from M4-J1's own files, which already passed
M4-J1's own G3 (max abs diff 0.0, 48 checks).
G4 MATERIALITY FORM: every gate/lean below is an equivalence, exactness,
rank-with-gap, or CI-exclusion bound; none is a nil-significance test on a
known-nonzero quantity; compliance stated per gate/lean in the report.

Chunked execution (process rule -- FOREGROUND, explicit long timeouts, no
background jobs, no monitors): `--world W --stage part0` computes S1/S2
patterns, S3/S4 shares, disp_v2 (G1 anchor side-product) and the conditioning
statistic for one world; `--assemble` combines every partial, reads M4-J1's
own persisted files for discriminators (i)/(ii)/benefit, runs the gates,
leans and full-inventory separation checks, and writes decision.json/
gates.json. `--smoke` runs a 1-world correctness+timing check before the full
sweep. Every stage is idempotent (skips if its partial already exists).
"""
from __future__ import annotations

import argparse
import json
import pickle
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_suica_m4_d_direction_anatomy_leg10 as leg10  # noqa: E402  independent eigendecomposition cross-check
import run_suica_m4_e2_offset_anatomy as e2  # noqa: E402  S1/S2/shares machinery
import run_suica_m4_h2_basis_normalization as h2  # noqa: E402  contexts, ingredients, offset+shares
import run_suica_m4_j1_repair_generalization as j1  # noqa: E402  world sets, arms, persisted anchors

from suica_core.m4_chart_ecology_generator import M4ChartEcologySpec  # noqa: E402

# ---------------------------------------------------------------------------
# registered world sets / arms -- literal reuse of M4-J1's own definitions
# ---------------------------------------------------------------------------

D1_WORLDS: tuple[str, ...] = j1.D1_WORLDS                          # 8
HIGH_GAP_WORLDS: tuple[str, ...] = j1.HIGH_GAP_WORLDS               # 3, G1 anchor worlds
FRESH_COMPANION_WORLDS: tuple[str, ...] = j1.FRESH_COMPANION_WORLDS  # 5
VALID_TRUTH_WORLDS: tuple[str, ...] = j1.VALID_TRUTH_WORLDS         # 6, inherited precedent (M4-G2)
EXCLUDED_TRUTH_WORLDS: tuple[str, ...] = j1.EXCLUDED_TRUTH_WORLDS   # 2

DEPLOYED_ARM = j1.DEPLOYED_ARM
SHRINK20_ARM = j1.SHRINK20_ARM
SHRINK100_ARM = j1.SHRINK100_ARM
TRUTH_BUDGETS: tuple[float, ...] = j1.TRUTH_BUDGETS

# M4-J1's own named finding (lean b): both certified ratios, both budgets,
# 8/8 cells OUTSIDE the margin by 2.68x-10.3x, in EXACTLY these two worlds.
HARM_WORLDS: tuple[str, ...] = ("history_gated_ecology", "topology_mismatch")
assert set(HARM_WORLDS) <= set(VALID_TRUTH_WORLDS)
SAFE_WORLDS: tuple[str, ...] = tuple(w for w in VALID_TRUTH_WORLDS if w not in HARM_WORLDS)  # 4, confirmed safe by M4-J1 lean b
assert len(SAFE_WORLDS) == 4

G1_ANCHOR_TOLERANCE = j1.G1_ANCHOR_TOLERANCE  # 1e-12

J1_RESULTS = ROOT / "results" / "m4_j1_repair_generalization"
H2_RESULTS = ROOT / "results" / "m4_h2_basis_normalization"
J1_DISP_ROWS_PATH = J1_RESULTS / "disp_rows.csv"
J1_AUTHOR_TRUTH_PATH = J1_RESULTS / "author_level_truth_rows.csv"
J1_LEAN_B_PATH = J1_RESULTS / "lean_b_safety_rows.csv"
H2_OFFSET_SHARES_PATH = H2_RESULTS / "offset_shares_by_arm.csv"

# ---- this leg's own registered-now constants (fixed before any compute) ----
BOOTSTRAP_SEED = 20260803        # = the registration date; documented, fixed before any correlation was computed
N_BOOTSTRAP = 20000
G2_LIVENESS_RATIO = 0.05         # range / |median| must clear this for a discriminator to count as live, not constant
PRIMARY_BUDGET = 4.0             # matches M4-J1's own primary report table (section 6); 8.0 carried as companion
COMPANION_BUDGET = 8.0
PRIMARY_SHRINK_ARM = SHRINK100_ARM   # "the basis-shrinkage repair at ratio 1.0" -- M4-J1's own lean (a) representative
COMPANION_SHRINK_ARM = SHRINK20_ARM


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"required persisted anchor is missing: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


# ---------------------------------------------------------------------------
# discriminators (i)/(ii)/benefit: READ directly from M4-J1's own persisted
# files -- NOT recomputed. Identity by construction is the strongest possible
# G1 anchor for these two.
# ---------------------------------------------------------------------------


def _load_j1_baseline_error() -> pd.DataFrame:
    if not J1_AUTHOR_TRUTH_PATH.exists():
        raise RuntimeError(f"missing M4-J1 artifact: {J1_AUTHOR_TRUTH_PATH}")
    truth = pd.read_csv(J1_AUTHOR_TRUTH_PATH)
    scoped = truth[(truth["arm"] == DEPLOYED_ARM) & (truth["c"] == 1.0)]
    out = scoped.groupby(["world", "budget"])["e_arm_true"].mean().reset_index()
    return out.rename(columns={"e_arm_true": "baseline_recovery_error"})


def _load_j1_baseline_displacement() -> pd.DataFrame:
    if not J1_DISP_ROWS_PATH.exists():
        raise RuntimeError(f"missing M4-J1 artifact: {J1_DISP_ROWS_PATH}")
    disp = pd.read_csv(J1_DISP_ROWS_PATH)
    scoped = disp[disp["arm"] == DEPLOYED_ARM]
    out = scoped.groupby("world")["disp_v2"].median().reset_index()
    return out.rename(columns={"disp_v2": "baseline_displacement"})


def _load_j1_benefit() -> pd.DataFrame:
    """'the basis-shrinkage repair's recovery BENEFIT' = -1 * M4-J1's own
    persisted mean_diff_arm_minus_deployed (positive benefit = shrinkage
    REDUCES error relative to deployed = helps; negative = harms). Defined
    only on VALID_TRUTH_WORLDS (6 of 8) -- the same population M4-J1's own
    lean (b) used, for the same reason (the 2 excluded worlds' e_arm_true is
    an inherited near-zero-denominator pathology, unrelated to any arm)."""
    if not J1_LEAN_B_PATH.exists():
        raise RuntimeError(f"missing M4-J1 artifact: {J1_LEAN_B_PATH}")
    lb = pd.read_csv(J1_LEAN_B_PATH)
    scoped = lb[lb["arm"].isin([SHRINK20_ARM, SHRINK100_ARM])].copy()
    scoped["benefit"] = -scoped["mean_diff_arm_minus_deployed"]
    return scoped[["arm", "world", "budget", "benefit", "mean_diff_arm_minus_deployed", "classification"]]


# ---------------------------------------------------------------------------
# discriminators (iii)/(iv): FRESH compute, literal reuse of h2/e2 machinery.
# Disclosed near-duplicate of h2._run_arm's own s1/s2-then-shares recipe
# (run_suica_m4_h2_basis_normalization.py:943-969) -- new only because H2
# itself never ran it on the 5 FRESH_COMPANION_WORLDS (H2 is a 3-world leg).
# ---------------------------------------------------------------------------


def _s1_s2_patterns_for_world(world: str, contexts: list[dict[str, Any]], output: Path) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    cache_dir = output / "_context_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"s1s2_{world}.pkl"
    if cache_path.exists():
        with cache_path.open("rb") as handle:
            return pickle.load(handle)
    s1_per_rep = []
    s2_per_rep = []
    q_values = []
    for context in contexts:
        machinery = e2._response_direction_machinery(context)
        s1_per_rep.append(e2._s1_patterns(context, machinery))
        q_values.append(int(machinery["q"]))
        s2_per_rep.append(e2._s2_patterns(context))
    d1_target = int(np.median(q_values))
    s1_patterns, s1_captured, d1 = e2._common_core(s1_per_rep, retained_dim=d1_target)
    d2_target = int(s2_per_rep[0].shape[1])
    s2_patterns, s2_captured, d2 = e2._common_core(s2_per_rep, retained_dim=d2_target)
    meta = {"s1_captured": s1_captured, "s2_captured": s2_captured, "d1": d1, "d2": d2, "q_values": q_values}
    with cache_path.open("wb") as handle:
        pickle.dump((s1_patterns, s2_patterns, meta), handle)
    return s1_patterns, s2_patterns, meta


# ---------------------------------------------------------------------------
# discriminator (v): condition number / effective rank of the retained
# eigenspectrum h3's shrinkage repair regularizes. Literal reuse of
# h2._ingredients_for_arm(context, "deployed") -- the exact ingredients
# function H3/H4's shrinkage dispatch consumes for every ladder arm.
# ---------------------------------------------------------------------------


def _conditioning_stats_for_world(contexts: list[dict[str, Any]]) -> dict[str, Any]:
    kappas: list[float] = []
    eff_ranks: list[float] = []
    k_retained: list[int] = []
    cross_check_max_abs_diff = 0.0
    for context in contexts:
        ingredients = h2._ingredients_for_arm(context, "deployed")
        eig = ingredients["eigenvalues"]
        retained = ingredients["retained"]
        eig_retained = eig[retained]
        kappa = float(eig_retained[0] / max(float(eig_retained[-1]), 1e-300))
        kappas.append(kappa)
        eff_ranks.append(float(np.sum(eig_retained) ** 2 / np.sum(eig_retained ** 2)))
        k_retained.append(int(len(retained)))
        cross = leg10._freeze_ingredients(context)
        cross_eig = cross["eigenvalues"][cross["retained"]]
        if len(cross_eig) == len(eig_retained):
            cross_check_max_abs_diff = max(cross_check_max_abs_diff, float(np.max(np.abs(cross_eig - eig_retained))))
        else:
            cross_check_max_abs_diff = float("nan")
    return {
        "condition_number_median": float(np.median(kappas)),
        "condition_number_per_rep": kappas,
        "effective_rank_median": float(np.median(eff_ranks)),
        "effective_rank_per_rep": eff_ranks,
        "k_retained_per_rep": k_retained,
        "leg10_cross_check_max_abs_diff": cross_check_max_abs_diff,
    }


# ---------------------------------------------------------------------------
# stage: part0 (S1/S2 patterns, offset+shares, disp_v2, conditioning; one world)
# ---------------------------------------------------------------------------


def _run_part0(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    started = time.time()
    partial_path = output / f"partial_part0_{world}.json"
    if partial_path.exists():
        print(f"[m4j2] SKIP (partial exists): {world}", flush=True)
        return
    # reuse M4-J1's own cached contexts -- read-only (cache already populated by M4-J1's own run)
    contexts = h2._contexts_for_world(world, config, spec, J1_RESULTS)

    s1_patterns, s2_patterns, s1s2_meta = _s1_s2_patterns_for_world(world, contexts, output)
    offset_shares = h2._arm_offset_and_shares(world, contexts, DEPLOYED_ARM, s1_patterns, s2_patterns)
    conditioning = _conditioning_stats_for_world(contexts)

    disp_df = pd.DataFrame(offset_shares["disp_rows"])
    disp_df.to_csv(output / f"partial_disp_{world}.csv", index=False)

    summary = {
        "world": world,
        "s1s2_meta": s1s2_meta,
        "offset_norm": offset_shares["offset_norm"],
        "registered_shares": offset_shares["registered_shares"],
        "reverse_shares": offset_shares["reverse_shares"],
        "standalone_shares": offset_shares["standalone_shares"],
        "s3_family_shares": offset_shares["s3_family_shares"],
        "gpa_v2_basins": offset_shares["gpa_v2_basins"],
        "gpa_swap_basins": offset_shares["gpa_swap_basins"],
        "disp_v2_median_recomputed": float(disp_df["disp_v2"].median()),
        "conditioning": conditioning,
    }
    output.mkdir(parents=True, exist_ok=True)
    with partial_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    s3 = offset_shares["registered_shares"]["S3_norm_scale_modes"]
    s4 = offset_shares["registered_shares"]["S4_residual"]
    print(
        f"[m4j2] part0 done: {world} S3={s3:.4f} S4={s4:.4f} "
        f"kappa_med={conditioning['condition_number_median']:.2f} "
        f"disp_v2_med={summary['disp_v2_median_recomputed']:.4f} "
        f"({time.time() - started:.1f}s total)",
        flush=True,
    )


# ---------------------------------------------------------------------------
# smoke stage
# ---------------------------------------------------------------------------


def _run_smoke(world: str, config: dict[str, Any], spec: M4ChartEcologySpec, output: Path) -> None:
    t0 = time.time()
    contexts = h2._contexts_for_world(world, config, spec, J1_RESULTS)
    print(f"[m4j2 smoke] contexts loaded from M4-J1 cache ({time.time() - t0:.1f}s), n={len(contexts)}", flush=True)

    t1 = time.time()
    s1_patterns, s2_patterns, meta = _s1_s2_patterns_for_world(world, contexts, output)
    print(f"[m4j2 smoke] s1/s2 patterns built ({time.time() - t1:.1f}s) meta={meta}", flush=True)

    t2 = time.time()
    offset_shares = h2._arm_offset_and_shares(world, contexts, DEPLOYED_ARM, s1_patterns, s2_patterns)
    s3 = offset_shares["registered_shares"]["S3_norm_scale_modes"]
    s4 = offset_shares["registered_shares"]["S4_residual"]
    print(f"[m4j2 smoke] offset_and_shares ({time.time() - t2:.1f}s) S3={s3:.4f} S4={s4:.4f}", flush=True)

    disp_df = pd.DataFrame(offset_shares["disp_rows"])
    recomputed_median = float(disp_df["disp_v2"].median())
    j1_disp = pd.read_csv(J1_DISP_ROWS_PATH)
    j1_median = float(j1_disp[(j1_disp["arm"] == DEPLOYED_ARM) & (j1_disp["world"] == world)]["disp_v2"].median())
    print(
        f"[m4j2 smoke] disp_v2 median recomputed={recomputed_median:.6f} vs M4-J1 persisted={j1_median:.6f} "
        f"diff={abs(recomputed_median - j1_median):.3e}",
        flush=True,
    )

    t3 = time.time()
    conditioning = _conditioning_stats_for_world(contexts)
    print(
        f"[m4j2 smoke] conditioning ({time.time() - t3:.1f}s) kappa_med={conditioning['condition_number_median']:.3f} "
        f"leg10_cross_check_max_abs_diff={conditioning['leg10_cross_check_max_abs_diff']:.3e}",
        flush=True,
    )
    print(f"[m4j2 smoke] TOTAL ({time.time() - t0:.1f}s)", flush=True)


# ---------------------------------------------------------------------------
# rank-separation + bootstrap-Spearman helpers (across-WORLD grain)
# ---------------------------------------------------------------------------


def _rank_separation(values: dict[str, float], harm_worlds: tuple[str, ...]) -> dict[str, Any]:
    """Does a threshold exist strictly separating harm_worlds from the rest,
    in EITHER direction? Literal implementation of lean (b)'s own words: "the
    two harm worlds are exactly the two lowest... -- a rank separation.\""""
    worlds = list(values.keys())
    harm_vals = {w: float(values[w]) for w in harm_worlds}
    safe_vals = {w: float(values[w]) for w in worlds if w not in harm_worlds}
    max_harm, min_harm = max(harm_vals.values()), min(harm_vals.values())
    max_safe, min_safe = max(safe_vals.values()), min(safe_vals.values())
    gap_low = min_safe - max_harm    # >0 : harm worlds are strictly the LOWEST
    gap_high = min_harm - max_safe   # >0 : harm worlds are strictly the HIGHEST
    separates_low = gap_low > 0
    separates_high = gap_high > 0
    return {
        "harm_values": harm_vals, "safe_values": safe_vals,
        "max_harm": max_harm, "min_harm": min_harm, "max_safe": max_safe, "min_safe": min_safe,
        "gap_low_absolute": gap_low, "gap_high_absolute": gap_high,
        "gap_low_ratio": (min_safe / max_harm) if (separates_low and max_harm != 0) else None,
        "gap_high_ratio": (min_harm / max_safe) if (separates_high and max_safe != 0) else None,
        "separates_low": bool(separates_low), "separates_high": bool(separates_high),
        "separates_either_direction": bool(separates_low or separates_high),
    }


def _bootstrap_spearman_ci(x: np.ndarray, y: np.ndarray, *, seed: int, n_boot: int) -> dict[str, Any]:
    """Nonparametric bootstrap CI for Spearman's rho, resampling WORLDS with
    replacement -- same family of method as this codebase's own
    `_cluster_bootstrap_lcb` (scripts/run_suica_m4_relational_error_budget.py
    :145-174), adapted here to resample the unit of analysis itself (worlds)
    since there is no larger cluster structure at this grain."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = len(x)
    rho = float(stats.spearmanr(x, y).statistic) if n >= 2 else float("nan")
    rng = np.random.default_rng(seed)
    boot: list[float] = []
    degenerate = 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        xb, yb = x[idx], y[idx]
        if np.std(xb) <= 1e-12 or np.std(yb) <= 1e-12:
            degenerate += 1
            continue
        r = stats.spearmanr(xb, yb).statistic
        if np.isfinite(r):
            boot.append(float(r))
    boot_arr = np.array(boot, dtype=float)
    if len(boot_arr) >= 20:
        ci_lo, ci_hi = (float(v) for v in np.quantile(boot_arr, [0.025, 0.975]))
    else:
        ci_lo, ci_hi = float("nan"), float("nan")
    excludes_zero = bool(np.isfinite(ci_lo) and np.isfinite(ci_hi) and (ci_lo > 0.0 or ci_hi < 0.0))
    direction = "positive" if (np.isfinite(rho) and rho > 0) else ("negative" if (np.isfinite(rho) and rho < 0) else "zero_or_nan")
    return {
        "n": n, "rho": rho, "n_boot_requested": n_boot, "n_boot_valid": len(boot_arr), "n_boot_degenerate": degenerate,
        "ci_lo": ci_lo, "ci_hi": ci_hi, "excludes_zero": excludes_zero, "direction": direction,
    }


# ---------------------------------------------------------------------------
# assemble + adjudicate
# ---------------------------------------------------------------------------


def _assemble(output: Path) -> None:
    worlds = list(D1_WORLDS)
    valid = list(VALID_TRUTH_WORLDS)

    for w in worlds:
        p = output / f"partial_part0_{w}.json"
        if not p.exists():
            raise RuntimeError(f"missing Part 0 partial (world not yet computed): {p}")
        dp = output / f"partial_disp_{w}.csv"
        if not dp.exists():
            raise RuntimeError(f"missing disp partial: {dp}")

    part0: dict[str, dict[str, Any]] = {}
    for w in worlds:
        part0[w] = _load_json(output / f"partial_part0_{w}.json")

    disp_recomputed = pd.concat([pd.read_csv(output / f"partial_disp_{w}.csv") for w in worlds], ignore_index=True)

    # ==== discriminators (i)/(ii)/benefit: read from M4-J1's own files ====
    baseline_error_df = _load_j1_baseline_error()
    baseline_disp_df = _load_j1_baseline_displacement()
    benefit_df = _load_j1_benefit()

    baseline_error_b4 = baseline_error_df[baseline_error_df["budget"] == PRIMARY_BUDGET].set_index("world")["baseline_recovery_error"].to_dict()
    baseline_error_b8 = baseline_error_df[baseline_error_df["budget"] == COMPANION_BUDGET].set_index("world")["baseline_recovery_error"].to_dict()
    baseline_disp = baseline_disp_df.set_index("world")["baseline_displacement"].to_dict()

    # ==== discriminators (iii)/(iv)/(v): fresh compute, assembled from partials ====
    s3_share = {w: float(part0[w]["registered_shares"]["S3_norm_scale_modes"]) for w in worlds}
    s4_share = {w: float(part0[w]["registered_shares"]["S4_residual"]) for w in worlds}
    conditioning_number = {w: float(part0[w]["conditioning"]["condition_number_median"]) for w in worlds}
    effective_rank = {w: float(part0[w]["conditioning"]["effective_rank_median"]) for w in worlds}

    # =========================================================================
    # G1 ANCHOR
    # =========================================================================
    j1_disp = pd.read_csv(J1_DISP_ROWS_PATH)
    j1_disp_dep = j1_disp[j1_disp["arm"] == DEPLOYED_ARM][["world", "repetition", "disp_v2"]].rename(columns={"disp_v2": "disp_v2_j1"})
    mine_disp = disp_recomputed[["world", "repetition", "disp_v2"]].rename(columns={"disp_v2": "disp_v2_mine"})
    joined = mine_disp.merge(j1_disp_dep, on=["world", "repetition"], how="inner")
    if len(joined) != len(worlds) * 8:
        raise RuntimeError(f"G1 disp anchor join incomplete: {len(joined)} != {len(worlds) * 8}")
    disp_anchor_diff = (joined["disp_v2_mine"] - joined["disp_v2_j1"]).abs()
    disp_anchor_max = float(disp_anchor_diff.max())

    h2_shares = pd.read_csv(H2_OFFSET_SHARES_PATH)
    h2_dep = h2_shares[h2_shares["arm"] == "deployed"].set_index("world")
    share_anchor_rows = []
    for w in HIGH_GAP_WORLDS:
        d_s3 = abs(s3_share[w] - float(h2_dep.loc[w, "registered_S3_norm_scale_modes"]))
        d_s4 = abs(s4_share[w] - float(h2_dep.loc[w, "registered_S4_residual"]))
        d_offset = abs(float(part0[w]["offset_norm"]) - float(h2_dep.loc[w, "offset_norm"]))
        share_anchor_rows.append({"world": w, "abs_diff_S3": d_s3, "abs_diff_S4": d_s4, "abs_diff_offset_norm": d_offset})
    share_anchor_max = max(max(r["abs_diff_S3"], r["abs_diff_S4"], r["abs_diff_offset_norm"]) for r in share_anchor_rows)

    leg10_cross_check_max = max(float(part0[w]["conditioning"]["leg10_cross_check_max_abs_diff"]) for w in worlds)

    g1_anchor = {
        "statement": "disp_v2 (this leg's own recomputation, a side product of the S3/S4 machinery) reproduces M4-J1's persisted disp_v2 to <=1e-12 on ALL 8 worlds; S3/S4 shares and offset_norm reproduce H2's own persisted offset_shares_by_arm.csv to <=1e-12 on the 3 HIGH_GAP_WORLDS (H2 never computed the 5 FRESH_COMPANION_WORLDS -- this is what licenses them as an EXTENSION); baseline error/displacement/benefit are READ, not recomputed, from M4-J1's own files (identity by construction, not approximate reproduction)",
        "disp_v2_vs_m4j1_all_8_worlds": {
            "n_checks": int(len(joined)), "max_abs_diff": disp_anchor_max, "tolerance": G1_ANCHOR_TOLERANCE,
            "pass": bool(disp_anchor_max <= G1_ANCHOR_TOLERANCE),
        },
        "s3_s4_offset_vs_h2_3_high_gap_worlds": {
            "rows": share_anchor_rows, "max_abs_diff": share_anchor_max, "tolerance": G1_ANCHOR_TOLERANCE,
            "pass": bool(share_anchor_max <= G1_ANCHOR_TOLERANCE),
        },
        "leg10_vs_h2_ingredients_independent_cross_check": {
            "max_abs_diff": leg10_cross_check_max,
            "note": "internal consistency check between two independently-written eigendecomposition implementations that both claim to reproduce freeze_m4_condition_transform; not a registered external anchor (no M4-J1 or H2 artifact persists this exact quantity)",
        },
        "baseline_error_displacement_benefit_source": "read directly (not recomputed) from results/m4_j1_repair_generalization/{author_level_truth_rows.csv, disp_rows.csv, lean_b_safety_rows.csv}",
        "pass": bool(disp_anchor_max <= G1_ANCHOR_TOLERANCE and share_anchor_max <= G1_ANCHOR_TOLERANCE),
    }

    # =========================================================================
    # G2 DISCRIMINATOR LIVENESS
    # =========================================================================
    def _liveness(name: str, values_dict: dict[str, float]) -> dict[str, Any]:
        vals = np.array([values_dict[w] for w in worlds], dtype=float)
        rng_ = float(np.max(vals) - np.min(vals))
        med = float(np.median(np.abs(vals)))
        ratio = rng_ / med if med > 0 else float("inf")
        return {
            "discriminator": name, "min": float(np.min(vals)), "max": float(np.max(vals)), "median": float(np.median(vals)),
            "range": rng_, "range_over_median_ratio": ratio, "live": bool(ratio >= G2_LIVENESS_RATIO),
        }

    g2_rows = [
        _liveness("baseline_recovery_error_budget4", baseline_error_b4),
        _liveness("baseline_displacement", baseline_disp),
        _liveness("S3_share", s3_share),
        _liveness("S4_share", s4_share),
        _liveness("conditioning_number_kappa", conditioning_number),
    ]
    g2_all_live = all(bool(r["live"]) for r in g2_rows)
    g2 = {
        "statement": f"each of the 5 registered discriminators must vary across the 8 D1_WORLDS by range >= {G2_LIVENESS_RATIO:.0%} of the median |value| -- a constant discriminator is VACUOUS, not a null",
        "materiality_ratio": G2_LIVENESS_RATIO, "rows": g2_rows, "all_live": bool(g2_all_live),
    }

    # =========================================================================
    # Part 0 full inventory table (all 8 worlds, Reading A)
    # =========================================================================
    inventory_rows = []
    for w in worlds:
        inventory_rows.append({
            "world": w, "is_harm_world": w in HARM_WORLDS, "is_excluded_truth_world": w in EXCLUDED_TRUTH_WORLDS,
            "baseline_recovery_error_budget4": baseline_error_b4.get(w),
            "baseline_recovery_error_budget8": baseline_error_b8.get(w),
            "baseline_displacement": baseline_disp[w],
            "S3_share": s3_share[w], "S4_share": s4_share[w],
            "conditioning_number_median": conditioning_number[w],
            "effective_rank_median": effective_rank[w],
        })
    inventory_df = pd.DataFrame(inventory_rows).sort_values("baseline_recovery_error_budget4")

    # =========================================================================
    # LEANS (adjudicated over VALID_TRUTH_WORLDS, n=6 -- ambiguity resolution #1)
    # =========================================================================
    def _benefit_vec(world_list: list[str], arm: str, budget: float) -> np.ndarray:
        rows = benefit_df[(benefit_df["arm"] == arm) & (benefit_df["budget"] == budget)].set_index("world")["benefit"]
        return np.array([float(rows[w]) for w in world_list])

    x_error_valid_b4 = np.array([baseline_error_b4[w] for w in valid])
    x_error_valid_b8 = np.array([baseline_error_b8[w] for w in valid])
    x_disp_valid = np.array([baseline_disp[w] for w in valid])
    y_benefit_100_b4 = _benefit_vec(valid, PRIMARY_SHRINK_ARM, PRIMARY_BUDGET)
    y_benefit_100_b8 = _benefit_vec(valid, PRIMARY_SHRINK_ARM, COMPANION_BUDGET)
    y_benefit_020_b4 = _benefit_vec(valid, COMPANION_SHRINK_ARM, PRIMARY_BUDGET)

    # ---- lean (a): BASELINE COMPETENCE PREDICTS HARM ----
    ci_a_primary = _bootstrap_spearman_ci(x_error_valid_b4, y_benefit_100_b4, seed=BOOTSTRAP_SEED, n_boot=N_BOOTSTRAP)
    ci_a_budget8 = _bootstrap_spearman_ci(x_error_valid_b8, y_benefit_100_b8, seed=BOOTSTRAP_SEED, n_boot=N_BOOTSTRAP)
    ci_a_ratio020 = _bootstrap_spearman_ci(x_error_valid_b4, y_benefit_020_b4, seed=BOOTSTRAP_SEED, n_boot=N_BOOTSTRAP)
    lean_a_held = bool(ci_a_primary["excludes_zero"] and ci_a_primary["direction"] == "positive")
    lean_a = {
        "statement": "baseline recovery error at deployed correlates with the basis-shrinkage repair's recovery BENEFIT across VALID_TRUTH_WORLDS (Spearman, bootstrap CI excluding zero), in the direction meaning the repair helps where the objective does badly (high error) and harms where it already does well (low error) -- i.e. a POSITIVE correlation between baseline error and benefit",
        "population": "VALID_TRUTH_WORLDS (n=6)", "primary": {"budget": PRIMARY_BUDGET, "shrink_arm": PRIMARY_SHRINK_ARM, **ci_a_primary},
        "companion_budget8": {"budget": COMPANION_BUDGET, "shrink_arm": PRIMARY_SHRINK_ARM, **ci_a_budget8},
        "companion_ratio020": {"budget": PRIMARY_BUDGET, "shrink_arm": COMPANION_SHRINK_ARM, **ci_a_ratio020},
        "held": lean_a_held,
    }

    # ---- lean (b): IT SEPARATES CLEANLY ----
    baseline_error_valid = {w: baseline_error_b4[w] for w in valid}
    rank_b = _rank_separation(baseline_error_valid, HARM_WORLDS)
    lean_b_held = bool(rank_b["separates_low"])  # registered direction: harm worlds are the two LOWEST
    lean_b = {
        "statement": "the two harm worlds are exactly the two lowest-baseline-error worlds among VALID_TRUTH_WORLDS -- a rank separation, not merely a correlation",
        "population": "VALID_TRUTH_WORLDS (n=6)", "rank_table": rank_b, "held": lean_b_held,
    }

    # ---- lean (c): DISPLACEMENT MAGNITUDE IS NOT THE DISCRIMINATOR (specificity check) ----
    baseline_disp_valid = {w: baseline_disp[w] for w in valid}
    rank_c = _rank_separation(baseline_disp_valid, HARM_WORLDS)
    lean_c_rank_held = bool(not rank_c["separates_low"] and not rank_c["separates_high"])
    ci_c_primary = _bootstrap_spearman_ci(x_disp_valid, y_benefit_100_b4, seed=BOOTSTRAP_SEED, n_boot=N_BOOTSTRAP)
    lean_c = {
        "statement": "baseline displacement does NOT separate the harm worlds -- a specificity check that the discriminator is competence rather than displacement size",
        "population": "VALID_TRUTH_WORLDS (n=6)",
        "rank_test": {"rank_table": rank_c, "held_by_literal_rank_criterion": lean_c_rank_held},
        "correlation_companion": {"statement": "companion check beyond the literal registered rank test: does displacement correlate with benefit as strongly/certainly as baseline error does (lean a)?", "budget": PRIMARY_BUDGET, "shrink_arm": PRIMARY_SHRINK_ARM, **ci_c_primary},
        "held": lean_c_rank_held,
        "held_note": "adjudicated on the LITERAL rank criterion (mirroring lean (b)'s own method, applied to displacement) -- see report for the disclosed, not-softened finding that this criterion, applied honestly, does not in fact separate baseline error from displacement in this 6-world sample",
    }

    # =========================================================================
    # FULL-INVENTORY separation check, all 5 discriminators (for the PIVOT)
    # exploratory/diagnostic beyond the 3 named leans -- both directions,
    # rank AND correlation, no individual pass/fail claim beyond feeding the
    # PIVOT's existential condition; multiplicity is disclosed, not corrected
    # for, because the PIVOT is already resolved by lean (b) alone (n=1
    # pre-registered, primary, directional test).
    # =========================================================================
    full_sep: dict[str, Any] = {}
    discriminator_values = {
        "baseline_recovery_error_budget4": baseline_error_valid,
        "baseline_displacement": baseline_disp_valid,
        "S3_share": {w: s3_share[w] for w in valid},
        "S4_share": {w: s4_share[w] for w in valid},
        "conditioning_number_kappa": {w: conditioning_number[w] for w in valid},
        "effective_rank_companion": {w: effective_rank[w] for w in valid},
    }
    for name, values_dict in discriminator_values.items():
        rank_result = _rank_separation(values_dict, HARM_WORLDS)
        x_vals = np.array([values_dict[w] for w in valid])
        corr_result = _bootstrap_spearman_ci(x_vals, y_benefit_100_b4, seed=BOOTSTRAP_SEED, n_boot=N_BOOTSTRAP)
        full_sep[name] = {
            "rank": rank_result, "correlation_vs_benefit_shrink100_budget4": corr_result,
            "separates_by_rank": bool(rank_result["separates_either_direction"]),
            "separates_by_correlation": bool(corr_result["excludes_zero"]),
            "separates_by_either_test": bool(rank_result["separates_either_direction"] or corr_result["excludes_zero"]),
        }
    # effective_rank_companion is a companion reading of registered item (v), not a 6th independent item
    scored_items = [k for k in full_sep if k != "effective_rank_companion"]
    any_scored_item_separates = any(full_sep[k]["separates_by_either_test"] for k in scored_items)
    pivot_fires = not any_scored_item_separates
    pivot = {
        "registered": "no discriminator in the registered inventory separates the two harm worlds from the six safe ones -> THE HARM BOUNDARY IS NOT PREDICTABLE from any measured world property available before applying the repair; the basis-shrinkage repair is then undeployable in principle, not merely unsupported as specified",
        "scored_items": scored_items, "any_scored_item_separates": bool(any_scored_item_separates), "fires": bool(pivot_fires),
        "resolving_item": "baseline_recovery_error_budget4 (lean b) alone already separates by rank -- a single, pre-registered, primary, directional test -- so the pivot's existential condition is resolved without needing the other 4 items' both-direction/multiplicity-exposed checks",
    }

    # =========================================================================
    # G0 POWER (stated from realized results, per the second standing rule)
    # =========================================================================
    g0 = {
        "statement": "n=8 D1_WORLDS is small; every truth-derived quantity (baseline error, benefit) is further restricted to VALID_TRUTH_WORLDS (n=6) by inherited precedent. A 6-point nonparametric bootstrap over Spearman's rho has only C(11,6)=462 distinct with-replacement resamples -- disclosed explicitly, not hidden behind a large n_boot count. What this design CAN detect: an EXACT rank-2 separation (lean b/c's own criterion) is a fully powered, deterministic fact at n=6 -- there is no sampling uncertainty in whether 2 specific values are the top/bottom 2 of 6 once all 6 are measured; this leg reports exact 2026-08-08-recomputed values, not estimates. What this design CANNOT detect at useful power: a Spearman correlation's SIGN and CI-exclusion-of-zero at n=6 is coarse -- a bootstrap CI at this n is wide by construction and easily includes zero even for a moderately strong true relationship; a CI that includes zero is reported UNDERPOWERED for that comparison, not as a null, per the second standing rule. MDE is not separately modeled (no prior-leg persisted effect-size table exists for a cross-world correlation, since no earlier leg in this line used the world as its unit of analysis) -- realized CI half-widths are reported per comparison instead, and the reader can see directly how wide they are.",
        "n_worlds_total": len(worlds), "n_valid_truth_worlds": len(valid), "n_harm_worlds": len(HARM_WORLDS), "n_safe_worlds": len(SAFE_WORLDS),
        "n_distinct_bootstrap_resamples_at_n6": 462,
        "g4_materiality_form_compliance": "G1 exact <=1e-12 reproduction; G2 range/median ratio bound; lean (a)/full-inventory correlations are CI-exclusion-of-zero bounds (not raw p-values); lean (b)/(c) and the full-inventory rank checks are exact gap bounds (not nil-significance); none is a nil-significance test on a known-nonzero quantity",
    }

    # =========================================================================
    # G3 (N/A, stated as such)
    # =========================================================================
    g3 = {
        "statement": "N/A -- this leg introduces no new truth-recovery (flat-vs-regenerated) computation; every truth-derived number (baseline error, benefit) is read directly from M4-J1's own persisted files, which already passed M4-J1's own G3 (max abs diff 0.0 over 48 checks, all 8 worlds)",
        "applicable": False,
    }

    verdict = "PIVOT_FIRES_HARM_BOUNDARY_NOT_PREDICTABLE" if pivot_fires else "HARM_BOUNDARY_PARTIALLY_PREDICTABLE__SPECIFICITY_NOT_CLEANLY_ESTABLISHED"
    if not pivot_fires and lean_a_held and lean_b_held and lean_c_rank_held:
        verdict = "HARM_BOUNDARY_PREDICTABLE__COMPETENCE_SPECIFICALLY__GATEABLE"
    elif not pivot_fires and lean_a_held and lean_b_held and not lean_c_rank_held:
        verdict = "HARM_BOUNDARY_PREDICTABLE_BUT_NOT_SPECIFIC_TO_COMPETENCE__PROVISIONAL_GATE_ONLY"

    decision = {
        "estimand_id": "M4-J2",
        "tier": "EXPLORATORY",
        "registered_in": "docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md, M4-J2 registration (2026-08-03, BEFORE run)",
        "worlds": worlds, "high_gap_anchor_worlds": list(HIGH_GAP_WORLDS), "fresh_companion_worlds": list(FRESH_COMPANION_WORLDS),
        "valid_truth_worlds": valid, "excluded_truth_worlds": list(EXCLUDED_TRUTH_WORLDS),
        "harm_worlds": list(HARM_WORLDS), "safe_worlds": list(SAFE_WORLDS),
        "ambiguity_resolutions": {
            "world_scope_for_adjudication": "READING B adopted: VALID_TRUTH_WORLDS (n=6), per the PIVOT text's own 'six safe ones' -- see script docstring for both readings",
            "separates_cleanly_criterion": "literal pure-rank test (lean b's own wording), applied identically to every discriminator; found to NOT cleanly distinguish competence from displacement by rank alone in this sample -- see script docstring and lean (c)",
        },
        "gates": {"g0_power": g0, "g1_anchor": g1_anchor, "g2_discriminator_liveness": g2, "g3_truth_path_invariance": g3},
        "part0_inventory": inventory_rows,
        "lean_a_baseline_competence_predicts_harm": lean_a,
        "lean_b_separates_cleanly": lean_b,
        "lean_c_displacement_not_the_discriminator": lean_c,
        "full_inventory_separation_check": full_sep,
        "pivot": pivot,
        "verdict": verdict,
        "claim_boundary": "EXPLORATORY, synthetic, label-free. Tests whether the basis-shrinkage repair's 2-world harm boundary (M4-J1) is predictable from a property measurable before applying the repair, across a synthetic world set. Licenses no claim about any real corpus, construct, person, or diagnosis.",
    }

    gates_out = {"g0_power": g0, "g1_anchor": g1_anchor, "g2_discriminator_liveness": g2, "g3_truth_path_invariance": g3, "g4_materiality_form": g0["g4_materiality_form_compliance"]}

    output.mkdir(parents=True, exist_ok=True)
    with (output / "decision.json").open("w", encoding="utf-8") as handle:
        json.dump(decision, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")
    with (output / "gates.json").open("w", encoding="utf-8") as handle:
        json.dump(gates_out, handle, indent=2, sort_keys=True, default=str)
        handle.write("\n")

    inventory_df.to_csv(output / "part0_inventory.csv", index=False)
    disp_recomputed.to_csv(output / "disp_v2_recomputed_rows.csv", index=False)
    pd.DataFrame(share_anchor_rows).to_csv(output / "g1_share_anchor_rows.csv", index=False)
    benefit_df.to_csv(output / "benefit_rows.csv", index=False)

    full_sep_rows = []
    for name, payload in full_sep.items():
        full_sep_rows.append({
            "discriminator": name,
            "separates_low": payload["rank"]["separates_low"], "separates_high": payload["rank"]["separates_high"],
            "gap_low_absolute": payload["rank"]["gap_low_absolute"], "gap_high_absolute": payload["rank"]["gap_high_absolute"],
            "gap_low_ratio": payload["rank"]["gap_low_ratio"], "gap_high_ratio": payload["rank"]["gap_high_ratio"],
            "spearman_rho_vs_benefit": payload["correlation_vs_benefit_shrink100_budget4"]["rho"],
            "ci_lo": payload["correlation_vs_benefit_shrink100_budget4"]["ci_lo"], "ci_hi": payload["correlation_vs_benefit_shrink100_budget4"]["ci_hi"],
            "correlation_excludes_zero": payload["correlation_vs_benefit_shrink100_budget4"]["excludes_zero"],
            "separates_by_rank": payload["separates_by_rank"], "separates_by_correlation": payload["separates_by_correlation"],
        })
    pd.DataFrame(full_sep_rows).to_csv(output / "full_inventory_separation_table.csv", index=False)

    print(f"[m4j2] ASSEMBLE done. verdict={verdict} pivot_fires={pivot_fires}", flush=True)
    print(f"[m4j2] lean_a held={lean_a_held} rho={ci_a_primary['rho']:.4f} CI=[{ci_a_primary['ci_lo']:.4f},{ci_a_primary['ci_hi']:.4f}]", flush=True)
    print(f"[m4j2] lean_b held={lean_b_held} gap_low={rank_b['gap_low_absolute']:.4f}", flush=True)
    print(f"[m4j2] lean_c held(rank)={lean_c_rank_held} displacement gap_low={rank_c['gap_low_absolute']:.4f} separates_low={rank_c['separates_low']}", flush=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs" / "m4_chart_ecology.json")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "m4_j2_harm_boundary")
    parser.add_argument("--world", type=str, default=None)
    parser.add_argument("--stage", type=str, default=None, choices=["part0"])
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--assemble", action="store_true")
    args = parser.parse_args()

    with args.config.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    spec = M4ChartEcologySpec(**config["base_spec"])

    if args.assemble:
        _assemble(args.output)
        return

    if args.world is None:
        raise SystemExit("--world is required unless --assemble")
    if args.world not in D1_WORLDS:
        raise SystemExit(f"not a registered D1_WORLDS world: {args.world}")

    if args.smoke:
        _run_smoke(args.world, config, spec, args.output)
        return
    if args.stage == "part0" or args.stage is None:
        _run_part0(args.world, config, spec, args.output)
        return


if __name__ == "__main__":
    main()
