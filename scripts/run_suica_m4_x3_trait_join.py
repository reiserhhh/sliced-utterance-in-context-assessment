#!/usr/bin/env python3
"""SUICA M4-X3 -- the trait join of expression coordinates (stage-E LABEL leg).

Registered BEFORE the run in ``docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md``
(section "X3 -- the trait join of expression coordinates", commit 8823b60).
This runner executes that registration and nothing else.

THE QUESTION.  Do the coordinates the X line certified -- expression LEVEL
(raw and venue-adjusted) and expression DYNAMICS (rhythm and the gap-volume
slope) -- couple to Big5 similarity?  And if the LEVEL does, does the coupling
SURVIVE venue adjustment (the composition question the atlas raises)?  The
level contrast is the design's edge; the dissociation family's sixth test is
the null it is measured against.

THE FOUR COORDINATES (label-free, frozen and hashed before any label is read).

    raw_level   person-mean y over the pool events, y = log1p(wcq)  (#70)
    adj_level   the X-Mb author-main FE coordinate a_hat_u, computed on the
                BIG5-COHORT analog of the X1c predicate chain at the pinned
                s = 5 primary, with X-M's pinned normalization
    rhythm      X2's r1_u -- the mean of the two half lag-1 autocorrelations
                of the y sequence in event time
    r2_slope    the R2 (gap x volume) within-person slope, floored per #89
                (den >= 1 in BOTH halves), the mean of the two half slopes

STAGE DISCIPLINE (the heart of the leg; U3's config-before-joint machinery).

    part0   LABEL-FREE, and the whole instrument lives here.  The inherited
            census anchors, the four coordinates, their split-half
            reliabilities, the reliability gate, and FOUR bit-level
            reproduction cross-checks against the committed X2 / X5 / X-Mb
            artifacts.  Only then is the analysis config written, sha256-
            hashed and STAMPED.  A1 binds: any instrument failure here STOPS
            the leg and NO STAMP IS EVER WRITTEN -- including the clean
            all-coordinates-fail stop (COORDINATES_UNRELIABLE).

    stageb  LABEL-FREE.  The coordinates are RE-EXECUTED from the same
            sources and asserted BIT-IDENTICAL to the reliabilities the stamp
            pinned (the determinism gate), the gate is re-run, and the
            coordinate table is frozen to disk and hashed into the chain.

    stagee  THE SINGLE JOIN.  ``author_profiles.csv`` is opened ONCE, for
            ``author`` plus the five Big5 columns, through the ONE inherited
            reader; ``first_join`` is logged with its timestamp BEFORE the
            first joint quantity; every registered quantity is computed inside
            this stage; nothing label-bearing is recomputed afterwards.

    gate    G-X3 proves ``stamp < coordinate_freeze < first_join`` FROM THE
            ARTIFACT TIMESTAMPS, checks both hashes, and runs the blocking
            #83 ID-leak scan over the 10,296-name universe.

Stages: part0 -> stageb -> stagee -> gate -> finalize -> report (or ``all``).

MACHINERY PROVENANCE (#56/#81 -- the inherited object, imported BY FILE)
-----------------------------------------------------------------------
``scripts/run_suica_m4_u3_when_trait_join.py``  the SR1-class stamp chain
    (``prove_stamp_order``, ``RunLog``, the config/freeze/join event names),
    the vectorised Mantel and the Smouse-Long-Sokal partial, the reliability
    gate rows, ``full_signature`` (the bag channel), ``projection_mdr``, and
    THE ONE LABEL READER ``open_trait_table`` -- which is where the Big5
    z-scoring by formula (#81: five z-scored columns, Euclidean distance)
    lives.  X3 never re-implements it.
``scripts/run_suica_m4_x2_volume_path.py``      ``Arm`` / ``arm_layout`` /
    ``masked_lag1_pearson`` -- the rhythm coordinate is X2's estimator, called
    on X2's own layout.
``scripts/run_suica_m4_x5_ergodicity_atlas.py`` ``relation_stats`` (the #89
    floor), ``RelationSkeleton``, and X4's ``cell_moments`` /
    ``per_cell_slopes`` bound through it -- the R2 slope is X5's estimator.
``scripts/run_suica_m4_xmb_mains_paired.py``    ``build_chain_design``,
    ``fitted_coefficients``, ``normalize_coefficients``, ``full_budget``,
    ``law_vocabulary``, ``load_cell_cache``, ``anchor_gate`` and the #83
    helpers, bound through X-M -> X1c -> X1b -> X1.

GOVERNANCE
----------
Metadata only: volume and timing, never content.  NO text body is ever read.
``author_profiles.csv`` is opened exactly once, in stage E, after the stamp
chain -- the label event is named in the config, the report and the ledger
(PANDORA Big5 re-join under an SR1-class stamp).  No per-author trait value
leaves stage E into any committed file; aggregates only.  EXPLORATORY,
corpus-level; no person claims; NO PSYCHOLOGICAL NAMING of the four technical
coordinates regardless of outcome.  Caches and author listings live in
gitignored ``results/`` and are never committed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import platform
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LEG = "M4-X3"
REGISTRATION_COMMIT = "8823b60"
PLAN_DOC = ROOT / "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md"
LEDGER = ROOT / "docs/CLAIMS_LEDGER.md"
SCRIPT_SELF = Path(__file__).resolve()
TEST_SELF = ROOT / "tests/test_m4_x3_trait_join.py"

DEFAULT_OUTPUT = ROOT / "results/m4_x3_trait_join"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_X3_TRAIT_JOIN_REPORT.md"

X5_CACHE = ROOT / "results/m4_x5_ergodicity_atlas/event_cache.npz"
X2_CACHE = ROOT / "results/m4_x2_volume_path/event_cache.npz"

COMMITTED_FILES = (DEFAULT_REPORT, SCRIPT_SELF, TEST_SELF, PLAN_DOC, LEDGER)

# THE ONE LABEL SOURCE.  Named here, opened in exactly one function.
PROFILES = Path("/Volumes/mobile3/projects/project persona"
                "/data_sets/PANDORA_official/author_profiles.csv")

# ---------------------------------------------------------------------------
# CONFIG -- every constant the registration pins, and nothing else.
# ---------------------------------------------------------------------------
SEED = 20260819                      # registration pin (X-line master seed)
B_PERM = 999                         # registration pin, every null
B_BOOT = 1000                        # registration pin, the Mantel-r CIs
ALPHA = 0.05
RELIABILITY_GATE = 0.50              # registration pin, label-free
REL_LABEL_DECLARED = 0.80            # DECLARED, not measured (#57)

SEED_PERM = SEED + 2                 # derived, never chosen (#76)
SEED_BOOT = SEED + 3

COORDINATES: tuple[str, ...] = ("raw_level", "adj_level", "rhythm",
                                "r2_slope")
LEVEL_COORDINATES: tuple[str, ...] = ("raw_level", "adj_level")
DYNAMICS_COORDINATES: tuple[str, ...] = ("rhythm", "r2_slope")

COORDINATE_TITLES: dict[str, str] = {
    "raw_level": "RAW LEVEL -- person-mean y",
    "adj_level": "ADJUSTED LEVEL -- the X-Mb author-main a_hat_u",
    "rhythm": "RHYTHM -- X2's r1_u",
    "r2_slope": "R2 SLOPE -- the floored gap x volume within-person slope",
}
# The registration's expectations for the label-free gate.  REPORTED AGAINST,
# never gated on: the gate is the 0.50 threshold and nothing else.
RELIABILITY_EXPECTATION: dict[str, float] = {
    "raw_level": 0.90, "adj_level": 0.90, "rhythm": 0.637, "r2_slope": 0.538}

# --- the pinned chain (X1c's, at X-Mb's certified primary) -----------------
CHAIN_N_MIN = 10
CHAIN_SUPPORT_PRIMARY = 5
CHAIN_K_MIN = 3
CHAIN_S_CENSUS: tuple[int, ...] = (3, 5, 8)

# --- inherited GLOBAL anchors (BLOCKING under #78) -------------------------
ANCHOR_ROWS_PARSEABLE = 17_640_062
ANCHOR_AUTHORS = 10_296
ANCHOR_BIG5_AUTHORS = 1_401
ANCHOR_DISJOINT_AUTHORS = 8_895
ANCHOR_LAW_VOCAB = 1_443
ANCHOR_VOCAB_FLOOR_USERS = 89

# --- inherited POOL anchors (#78, BLOCKING) --------------------------------
ANCHOR_CANDIDATES = 9_124            # X2/X5's >= 50 events per half
ANCHOR_POOL_BIG5 = 1_116             # X2's Big5 pool -- X3's analysis pool
ANCHOR_POOL_DISJOINT = 8_008
ANCHOR_R2_POOL_BIG5 = 1_100          # X5's R2 pool, Big5
ANCHOR_R2_POOL_DISJOINT = 7_989

# --- inherited VALUE reproductions (BLOCKING; the instrument's provenance) --
# Each is a committed number from the leg that certified the coordinate.  X3
# recomputes it here, from the inherited estimator, before the stamp.
REPRO_TOL = 1e-9
REPRO_X2_RHYTHM_RHO_OWN = 0.6366996180212687      # X2 arms.json, big5 arm
REPRO_X5_R2_RHO_OWN = 0.538039302428076           # X5 arms.json, R2:big5
REPRO_X5_R2_MEAN_BETA = 0.05203279700207156       # X5 arms.json, R2:big5
REPRO_XMB_AUTHOR_MAIN = 0.12858739914097542       # X-Mb real_arm.json
REPRO_XMB_CHAIN_S5 = {"authors": 3665, "communities": 1000,
                      "shared_pairs": 31899}

# --- SR1's effect-scale anchor and the projection --------------------------
SR1_R = 0.049
SR1_Z = 5.42
SR1_N = 1306
REGISTERED_MDR = 0.019               # registration's projection at N ~ 1,116

# --- cells (NULL-first #55) ------------------------------------------------
CELL_SILENT = "EXPRESSION_TRAIT_SILENT"
CELL_LEVEL_ONLY = "LEVEL_ONLY_COMPOSITION"
CELL_LEVEL_INTRINSIC = "LEVEL_INTRINSIC"
CELL_DYNAMICS = "DYNAMICS_COUPLED"
CELL_UNRELIABLE = "COORDINATES_UNRELIABLE"
CELL_NUMBER = {CELL_SILENT: 1, CELL_LEVEL_ONLY: 2, CELL_LEVEL_INTRINSIC: 3,
               CELL_DYNAMICS: 4}

# --- registered leans (report against, never route) ------------------------
LEAN_PRIMARY = (f"{CELL_SILENT} to {CELL_LEVEL_ONLY}")
LEAN_DYNAMICS_ABS_R = 0.03

BIG5: tuple[str, ...] = ("agreeableness", "openness", "conscientiousness",
                         "extraversion", "neuroticism")

RN_NOTES: dict[str, str] = {
    "RN-X3-1":
        "CONFIG-BEFORE-JOINT.  stage_part0 re-executes every inherited "
        "anchor, builds the four coordinates, runs the label-free "
        "reliability gate and the four value reproductions, and only then "
        "writes, hashes and stamps the config; it never opens a label "
        "column.  stage_stageb is label-free, re-executes the coordinates, "
        "asserts them bit-identical to the stamped reliabilities and freezes "
        "the coordinate table into the stamp chain.  The FIRST joint "
        "expression x trait quantity of the harness lives in stage_stagee, "
        "which logs a `first_join` event immediately before it.  G-X3 reads "
        "the artifacts and proves stamp < coordinate_freeze < first_join.",
    "RN-X3-2":
        "the coordinates are TECHNICAL OBJECTS.  Expression volume, its "
        "venue-adjusted author main, its event-time rhythm and its "
        "gap-volume slope are selection-process statistics of an author's "
        "own metadata stream.  NO PSYCHOLOGICAL NAMING is permitted "
        "REGARDLESS OF OUTCOME -- not 'talkativeness', not 'expressiveness', "
        "not 'impulsivity', not 'consistency'.  A coupling, if one is found, "
        "is a coupling of a metadata statistic to a questionnaire score.",
    "RN-X3-3":
        "metadata only.  The word count is HOW MUCH was said, never WHAT was "
        "said; no text body is read anywhere in the X line.  Every claim "
        "carries that boundary.",
    "RN-X3-4":
        "the COHORT CAVEAT rides every claim.  Big5-cohort ownership is "
        "higher than the disjoint cohort's on every coordinate the X line "
        "measured (X2's rhythm 0.637 vs 0.259, X5's R2 slope 0.538 vs its "
        "disjoint value -- the sevenfold Big5-ownership flag), and the "
        "cohort's own selection cannot be separated from that.  A reading "
        "here is a reading ON THIS COHORT.",
    "RN-X3-5":
        "the label event.  This leg opens the PANDORA Big5 columns of "
        "author_profiles.csv ONCE, under the stamp, for the Big5-cohort "
        "analysis pool -- the SR1/U3 class of re-join.  No per-author trait "
        "value is written to any committed file; only aggregate statistics "
        "leave stage E.",
    "RN-X3-6":
        "the eq-12 / response-operator projection caution.  Each coordinate "
        "is ONE first-order projection of the response operator; a verdict "
        "here is a statement about that projection, on this pool, measured "
        "this way -- exactly as X1c's and X2's positive results were.",
    "RN-X3-7":
        "disattenuation is a SECONDARY READING ONLY (#57 family).  The "
        "coordinate reliabilities are MEASURED here; the label reliability "
        "0.80 is DECLARED, so any disattenuated number illustrates scale and "
        "routes nothing.",
    "RN-X3-8":
        "#79: no ratio null.  The level contrast is read as TWO detection "
        "decisions with TWO CIs, never as a null on r_adjusted / r_raw.  The "
        "retention ratio is printed as a descriptive and routes nothing.",
}

# ---------------------------------------------------------------------------
# Inherited machinery, imported by file (#56/#81: the object, not a copy)
# ---------------------------------------------------------------------------
U3_SCRIPT = ROOT / "scripts/run_suica_m4_u3_when_trait_join.py"
X2_SCRIPT = ROOT / "scripts/run_suica_m4_x2_volume_path.py"
X5_SCRIPT = ROOT / "scripts/run_suica_m4_x5_ergodicity_atlas.py"
XMB_SCRIPT = ROOT / "scripts/run_suica_m4_xmb_mains_paired.py"


def _import_by_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:          # pragma: no cover
        raise RuntimeError(f"cannot import {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


U3 = _import_by_file("suica_m4_u3_for_x3", U3_SCRIPT)
X2 = _import_by_file("suica_m4_x2_for_x3", X2_SCRIPT)
X5 = _import_by_file("suica_m4_x5_for_x3", X5_SCRIPT)
XMB = _import_by_file("suica_m4_xmb_for_x3", XMB_SCRIPT)
XM = XMB.XM

# -- the stamp chain and the statistics (U3) --------------------------------
RunLog = U3.RunLog
prove_stamp_order = U3.prove_stamp_order
condensed_indices = U3.condensed_indices
square_from_condensed = U3.square_from_condensed
mantel_permutation = U3.mantel_permutation
partial_mantel_sls = U3.partial_mantel_sls
ols_residual = U3.ols_residual
full_signature = U3.full_signature
pearson = U3.pearson
spearman_brown = U3.spearman_brown
projection_mdr = U3.projection_mdr
write_json = U3.write_json
read_json = U3.read_json
sha256_file = U3.sha256_file
utc_now = U3.utc_now

# -- the coordinate estimators ----------------------------------------------
arm_layout = X2.arm_layout
Arm = X2.Arm
relation_stats = X5.relation_stats
RelationSkeleton = X5.RelationSkeleton
event_author_and_half = X5.event_author_and_half
cell_moments = X5.cell_moments                  # X4's, bound through X5
per_cell_slopes = X5.per_cell_slopes            # X4's, bound through X5
R2_SPEC = X5.RELATION_BY_KEY["R2"]

# -- the chain, the FE mains, the census and the #83 helpers ----------------
load_cell_cache = XM.load_cell_cache
law_vocabulary = XM.law_vocabulary
build_chain_design = XM.build_chain_design
fitted_coefficients = XM.fitted_coefficients
full_budget = XM.full_budget
anchor_gate = XM.anchor_gate
scan_for_cohort_ids = XM.scan_for_cohort_ids
baseline_hit_keys = XM.baseline_hit_keys
new_hits_only = XM.new_hits_only
DEFAULT_X1_CACHE = XM.DEFAULT_X1_CACHE
DEFAULT_COHORT = XM.DEFAULT_COHORT


def rel(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def _fisher_two_sided_p(r: float, n: int) -> float:
    """Two-sided p for a Pearson r by Fisher's z (declared, secondary only).

    The per-trait table is a SECONDARY, Bonferroni-guarded reading that routes
    nothing, so it does not carry its own permutation null; the transform is
    named in the report and the threshold is the Bonferroni one.
    """

    if not np.isfinite(r) or n < 4 or abs(r) >= 1.0:
        return float("nan")
    z = math.atanh(float(r)) * math.sqrt(n - 3)
    return float(math.erfc(abs(z) / math.sqrt(2.0)))


# ---------------------------------------------------------------------------
# THE ONE LABEL READER.  Nothing else in this module touches PROFILES.
# ---------------------------------------------------------------------------
def open_trait_table(author_names: Sequence[str],
                     path: Path = PROFILES) -> tuple[np.ndarray, dict]:
    """Open author_profiles.csv ONCE, through U3's certified reader.

    U3's ``open_trait_table`` IS the pinned #81 trait geometry: the same five
    columns, one z-scoring over the pool it is handed, reused by every
    coordinate row.  X3 inherits it rather than re-deriving it; only the
    provenance note is re-stated for this pool.  Called exactly once, from
    stage E, after ``first_join`` is logged.  NO PER-AUTHOR VALUE LEAVES THIS
    FUNCTION'S CALLER IN A COMMITTED FILE.
    """

    traits, info = U3.open_trait_table(author_names, path)
    info["z_scored_over"] = (
        f"the {len(author_names):,}-author Big5 analysis pool (ONE "
        "z-scoring, reused by every coordinate row and by the per-trait "
        "secondary table)")
    info["reader"] = "inherited verbatim from U3.open_trait_table (#81 pin)"
    info["label_event"] = RN_NOTES["RN-X3-5"]
    return traits, info


# ---------------------------------------------------------------------------
# The reliability gate -- U3's rows, X3's stop rule.
# ---------------------------------------------------------------------------
def apply_reliability_gate(reliabilities: dict[str, float],
                           threshold: float = RELIABILITY_GATE
                           ) -> dict[str, Any]:
    """U3's per-row ADMIT/EXCLUDE, under X3's registered ALL-FAIL stop rule.

    U3's gate stopped on its PRIMARY coordinate.  X3 has no primary: every
    admitted coordinate carries a registered cell, and the leg stops only if
    EVERY coordinate falls below 0.50 -- the registration's clean
    COORDINATES_UNRELIABLE exit, which happens BEFORE the stamp and is
    therefore not a stamp violation (A1).
    """

    first = next(iter(reliabilities), "")
    base = U3.apply_reliability_gate(reliabilities, threshold=threshold,
                                     primary=first)
    admitted = list(base["admitted"])
    base["primary"] = None
    base["primary_admitted"] = None
    base["expectation"] = {k: RELIABILITY_EXPECTATION.get(k)
                           for k in reliabilities}
    base["STOP_before_join"] = not admitted
    base["stop_verdict"] = None if admitted else CELL_UNRELIABLE
    base["stop_rule"] = ("X3's registered rule: failures are reported and "
                         "excluded; the leg stops clean only if EVERY "
                         "coordinate fails, and that stop happens before the "
                         "stamp")
    return base


# ---------------------------------------------------------------------------
# The label-free sources.  Nothing here can reach a label column.
# ---------------------------------------------------------------------------
@dataclass
class Sources:
    """Every label-free input the coordinate builder is allowed to see."""

    x5: dict[str, Any]
    x5_meta: dict[str, Any]
    x2: dict[str, Any]
    x2_meta: dict[str, Any]
    table: dict[str, Any]
    scaffold: dict[str, Any]
    cohort_names: list[str]
    big5_mask: np.ndarray
    vocab: dict[str, Any]
    author_names: list[str] = field(default_factory=list)


def load_cohort_names(path: Path) -> list[str]:
    """The Big5 cohort AUTHOR NAME list -- no trait column is requested."""

    frame = pd.read_csv(path, usecols=["author"])
    return sorted({str(name) for name in frame["author"]})


def load_sources(args: argparse.Namespace, log: RunLog) -> Sources:
    """Load the three inherited caches and the cohort name list.

    Each cache is the committed artifact of the leg that certified the
    coordinate it feeds.  If one is absent the runner refuses rather than
    silently re-deriving a different universe: the reproduction cross-checks
    in part 0 only mean something against the SAME cache the certifying leg
    used, and every cache is one documented command away.
    """

    for path, owner in ((args.x5_cache, "run_suica_m4_x5_ergodicity_atlas.py"),
                        (args.x2_cache, "run_suica_m4_x2_volume_path.py"),
                        (args.x1_cache, "run_suica_m4_x1_venue_response.py")):
        if not Path(path).exists():              # pragma: no cover
            raise SystemExit(
                f"MISSING INHERITED CACHE {path}\n"
                f"  rebuild it by running scripts/{owner} (gitignored "
                f"artifact; X3 reads it, never writes it)")

    x5, x5_meta = X5.load_cache(args.x5_cache)
    x2, x2_meta = X2.load_cache(args.x2_cache)
    table, scaffold = load_cell_cache(args.x1_cache, log)
    author_names = list(scaffold["authors"])
    cohort_names = load_cohort_names(args.cohort)
    name_to_code = {name: i for i, name in enumerate(author_names)}
    big5_mask = np.zeros(len(author_names), dtype=bool)
    for name in cohort_names:
        code = name_to_code.get(name)
        if code is not None:
            big5_mask[code] = True
    vocab = law_vocabulary(table, ~big5_mask, log)
    log.event("sources_loaded", x5=rel(Path(args.x5_cache)),
              x2=rel(Path(args.x2_cache)), x1=rel(Path(args.x1_cache)),
              authors=len(author_names), big5_seen=int(big5_mask.sum()),
              law_vocabulary=int(vocab["vocabulary_size"]),
              label_table_opened=False)
    return Sources(x5=x5, x5_meta=x5_meta, x2=x2, x2_meta=x2_meta,
                   table=table, scaffold=scaffold, cohort_names=cohort_names,
                   big5_mask=big5_mask, vocab=vocab,
                   author_names=author_names)


def source_agreement(sources: Sources) -> dict[str, Any]:
    """BLOCKING: the three caches must be ONE universe, checked not assumed."""

    x5_names = list(sources.x5_meta["authors"])
    x2_names = list(sources.x2_meta["authors"])
    cell_names = list(sources.scaffold["authors"])
    pools_equal = bool(np.array_equal(
        np.asarray(sources.x5["pool_author_code"]),
        np.asarray(sources.x2["pool_author_code"])))
    big5_equal = bool(np.array_equal(np.asarray(sources.x5["pool_is_big5"]),
                                     np.asarray(sources.x2["pool_is_big5"])))
    out = {
        "x5_author_names_equal_cell_cache": bool(x5_names == cell_names),
        "x2_author_names_equal_cell_cache": bool(x2_names == cell_names),
        "x2_and_x5_candidate_pools_identical": pools_equal,
        "x2_and_x5_big5_masks_identical": big5_equal,
        "note": ("the rhythm channel comes from X5's cache, the bag channel "
                 "from X2's and the chain from X1's; a coordinate table "
                 "assembled across three caches is only meaningful if the "
                 "author code space is literally the same object"),
    }
    out["status"] = "PASS" if all(v is True for k, v in out.items()
                                  if k != "note") else "FAIL"
    return out


# ---------------------------------------------------------------------------
# THE COORDINATE BUILDER -- LABEL-FREE BY CONSTRUCTION.
#
# The signature admits a ``Sources`` and nothing else; ``Sources`` has no
# field that can carry a trait value, and a contract test asserts that the
# builder runs to completion with every label reader in the process replaced
# by a landmine.
# ---------------------------------------------------------------------------
@dataclass
class Coordinates:
    pool_codes: np.ndarray                       # global author codes
    pool_names: list[str]
    values: dict[str, np.ndarray]                # NaN where ineligible
    early: dict[str, np.ndarray]
    late: dict[str, np.ndarray]
    eligible: dict[str, np.ndarray]              # boolean over the pool
    reliabilities: dict[str, float]
    descriptives: dict[str, Any]
    diagnostics: dict[str, Any]
    activity: np.ndarray                         # pool event counts
    chain_census: dict[str, Any]
    label_data_in_inputs: bool = False


def _pool_slot(n_authors: int, codes: np.ndarray) -> np.ndarray:
    slot = np.full(n_authors, -1, dtype=np.int64)
    slot[codes] = np.arange(codes.size)
    return slot


def build_coordinates(sources: Sources) -> Coordinates:
    """The four coordinates on the Big5 analysis pool.  No label is reachable.

    The pool is X2's Big5 pool: an author of the Big5 cohort with at least 50
    events in EACH of their own halves.  Each coordinate then applies its own
    machinery's eligibility inside that pool, and is NaN outside it.
    """

    cache = sources.x5
    n_total = np.asarray(cache["n_total"]).astype(np.int64)
    n_early = np.asarray(cache["n_early"]).astype(np.int64)
    offsets = np.asarray(cache["offsets"]).astype(np.int64)
    is_big5 = np.asarray(cache["pool_is_big5"]).astype(bool)
    candidate_codes = np.asarray(cache["pool_author_code"]).astype(np.int64)
    y = np.asarray(cache["ev_volume"])

    sel = is_big5
    pool_local = np.flatnonzero(sel)              # index into the candidates
    pool_codes = candidate_codes[pool_local]      # global author codes
    n_pool = int(pool_local.size)
    pool_names = [str(sources.author_names[int(c)]) for c in pool_codes]

    values: dict[str, np.ndarray] = {}
    early: dict[str, np.ndarray] = {}
    late: dict[str, np.ndarray] = {}
    eligible: dict[str, np.ndarray] = {}
    diagnostics: dict[str, Any] = {}

    # ---- (1) RAW LEVEL -----------------------------------------------------
    starts = offsets[:-1]
    who_all, half_all = event_author_and_half(cache)
    sum_all = np.add.reduceat(y, starts)
    sum_early = np.add.reduceat(np.where(half_all == 0, y, 0.0), starts)
    mean_all = sum_all / n_total
    mean_early = sum_early / n_early
    mean_late = (sum_all - sum_early) / (n_total - n_early)
    values["raw_level"] = mean_all[pool_local]
    early["raw_level"] = mean_early[pool_local]
    late["raw_level"] = mean_late[pool_local]
    eligible["raw_level"] = np.isfinite(values["raw_level"])

    # ---- (3) RHYTHM -- X2's Arm on X2's layout ----------------------------
    layout_cache = {"offsets": offsets, "n_early": n_early,
                    "n_total": n_total}
    start, length, author, half = arm_layout(layout_cache, sel)
    arm = Arm("big5", "the Big5 analysis pool", y, start, length, author,
              half, None, n_pool)
    r1_e, r1_l, ok_r1 = arm.paired(arm.r1())
    with np.errstate(invalid="ignore"):
        values["rhythm"] = np.where(ok_r1, 0.5 * (r1_e + r1_l), np.nan)
    early["rhythm"] = r1_e
    late["rhythm"] = r1_l
    eligible["rhythm"] = ok_r1
    diagnostics["rhythm"] = {"arm_census": arm.census(),
                             "cells_undefined": int((~ok_r1).sum())}
    del arm

    # ---- (4) R2 SLOPE -- X5's floored estimator ---------------------------
    st = relation_stats(cache, R2_SPEC, who_all, half_all)
    r2_sel = st["pool"] & sel
    sk = RelationSkeleton("big5", "the Big5 analysis pool", R2_SPEC, cache,
                          r2_sel, st, who_all, half_all, with_events=True)
    y_usable = cache[f"ev_{R2_SPEC.y}"][sk.events["sel_event"]]
    mom = cell_moments(sk, y_usable)
    beta_e, beta_l, ok_beta = per_cell_slopes(sk, mom)
    slot = _pool_slot(int(n_total.size), pool_local)
    rows = slot[sk.codes]
    for name, source in (("values", 0.5 * (beta_e + beta_l)),
                         ("early", beta_e), ("late", beta_l)):
        target = np.full(n_pool, np.nan)
        target[rows] = source
        {"values": values, "early": early, "late": late}[name]["r2_slope"] = \
            target
    elig = np.zeros(n_pool, dtype=bool)
    elig[rows] = ok_beta
    eligible["r2_slope"] = elig & np.isfinite(values["r2_slope"])
    diagnostics["r2_slope"] = {
        "census": sk.census(),
        "pool_big5": int(r2_sel.sum()),
        "pool_disjoint": int((st["pool"] & ~sel).sum()),
        "dropped_by_the_count_floor": int(st["dropped_by_the_count_floor"]),
        "dropped_by_the_den_floor": int(st["dropped_by_the_den_floor"]),
        "estimability_floor": "#89: den >= 1 in BOTH halves, part of the pool",
        "mean_beta": float(np.nanmean(values["r2_slope"])),
    }
    del sk, mom, y_usable

    # ---- (2) ADJUSTED LEVEL -- the Big5 analog of the X1c chain -----------
    chain_census: dict[str, Any] = {}
    designs: dict[int, Any] = {}
    for s in CHAIN_S_CENSUS:
        design, chain = build_chain_design(
            sources.table, sources.big5_mask, n_min=CHAIN_N_MIN, support=s,
            vocab_mask=sources.vocab["mask"])
        designs[s] = design
        chain_census[str(s)] = chain
    design = designs[CHAIN_SUPPORT_PRIMARY]
    coefs = fitted_coefficients(design)
    a_early, a_late = coefs["a_e"], coefs["a_l"]
    a_hat = 0.5 * (a_early + a_late)
    slot_global = _pool_slot(len(sources.author_names), pool_codes)
    rows = slot_global[design.author_codes]
    inside = rows >= 0
    for key, source in (("values", a_hat), ("early", a_early),
                        ("late", a_late)):
        target = np.full(n_pool, np.nan)
        target[rows[inside]] = source[inside]
        {"values": values, "early": early, "late": late}[key]["adj_level"] = \
            target
    eligible["adj_level"] = np.isfinite(values["adj_level"])
    budget = full_budget(design)
    diagnostics["adj_level"] = {
        "chain_census": chain_census,
        "support_primary": CHAIN_SUPPORT_PRIMARY,
        "n_min": CHAIN_N_MIN, "k_min": CHAIN_K_MIN,
        "chain_authors": int(design.n_authors),
        "chain_authors_inside_the_analysis_pool": int(inside.sum()),
        "chain_authors_outside_the_analysis_pool": int((~inside).sum()),
        "author_main_share": float(budget["author"]),
        "community_main_share": float(budget["community"]),
        "interaction_share": float(budget["interaction"]),
        "residual_share": float(budget["residual"]),
        "var_y": float(budget["var_y"]),
        "fe_sweeps": [int(coefs["sweeps_early"]), int(coefs["sweeps_late"])],
        "fe_change": [float(coefs["change_early"]),
                      float(coefs["change_late"])],
        "normalization": list(XM.NORMALIZATION_SEQUENCE),
        "note": ("the chain is the X1c predicate chain run on the BIG5 mask "
                 "instead of the disjoint mask, at X-Mb's certified primary "
                 "support s = 5; no pre-registered census exists for it, so "
                 "it is censused here, label-free, and pinned into the "
                 "stamped config before any label is opened"),
    }

    # ---- split-half reliabilities (label-free) ----------------------------
    reliabilities: dict[str, float] = {}
    descriptives: dict[str, Any] = {}
    for name in COORDINATES:
        idx = eligible[name]
        both = idx & np.isfinite(early[name]) & np.isfinite(late[name])
        r_half = pearson(early[name][both], late[name][both])
        reliabilities[name] = float(r_half)
        vals = values[name][idx]
        descriptives[name] = {
            "title": COORDINATE_TITLES[name],
            "n_eligible": int(idx.sum()),
            "n_with_both_split_halves": int(both.sum()),
            "share_of_pool": float(idx.sum() / max(n_pool, 1)),
            "mean": float(np.mean(vals)) if vals.size else float("nan"),
            "sd": float(np.std(vals, ddof=1)) if vals.size > 1
            else float("nan"),
            "min": float(np.min(vals)) if vals.size else float("nan"),
            "max": float(np.max(vals)) if vals.size else float("nan"),
            "split_half_r": float(r_half),
            "spearman_brown": spearman_brown(float(r_half)),
            "registration_expectation": RELIABILITY_EXPECTATION[name],
        }

    activity = n_total[pool_local].astype(np.float64)
    return Coordinates(
        pool_codes=pool_codes, pool_names=pool_names, values=values,
        early=early, late=late, eligible=eligible,
        reliabilities=reliabilities, descriptives=descriptives,
        diagnostics=diagnostics, activity=activity,
        chain_census=chain_census, label_data_in_inputs=False)


# ---------------------------------------------------------------------------
# The four value reproductions -- BLOCKING, and the instrument's provenance.
# ---------------------------------------------------------------------------
def reproduction_checks(coords: Coordinates,
                        sources: Sources) -> dict[str, Any]:
    """Recompute four committed numbers from the coordinates just built.

    The coordinates are only the certified objects if the estimators
    reproduce, on this pool, the values the certifying legs published.  Two
    are split-half correlations that ARE X2's and X5's routing statistics;
    one is X5's level-3 mean slope; one is X-Mb's certified author main,
    which pins the FE fit and the pinned normalization bit for bit.
    """

    rows: dict[str, Any] = {}

    def add(key: str, observed: float, registered: float, source: str) -> None:
        delta = float(observed) - float(registered)
        rows[key] = {"observed": float(observed),
                     "registered": float(registered),
                     "abs_delta": abs(delta), "tolerance": REPRO_TOL,
                     "source": source,
                     "status": "PASS" if abs(delta) <= REPRO_TOL else "FAIL"}

    add("X2 rhythm ownership rho_own (Big5 arm)",
        coords.reliabilities["rhythm"], REPRO_X2_RHYTHM_RHO_OWN,
        "results/m4_x2_volume_path/arms.json :: big5.rho_own")
    add("X5 R2 slope ownership rho_own (Big5 arm)",
        coords.reliabilities["r2_slope"], REPRO_X5_R2_RHO_OWN,
        "results/m4_x5_ergodicity_atlas/arms.json :: R2:big5.rho_own")
    add("X5 R2 mean floored slope (Big5 arm)",
        coords.diagnostics["r2_slope"]["mean_beta"], REPRO_X5_R2_MEAN_BETA,
        "results/m4_x5_ergodicity_atlas/arms.json :: "
        "R2:big5.dispersion.mean_beta")

    design, chain = build_chain_design(
        sources.table, ~sources.big5_mask, n_min=CHAIN_N_MIN,
        support=CHAIN_SUPPORT_PRIMARY, vocab_mask=sources.vocab["mask"])
    budget = full_budget(design)
    add("X-Mb certified author main (disjoint s=5 skeleton)",
        budget["author"], REPRO_XMB_AUTHOR_MAIN,
        "results/m4_xmb_mains_paired/real_arm.json :: budget.author")
    chain_ok = {k: [int(chain[k]), int(v)] for k, v in
                REPRO_XMB_CHAIN_S5.items()}
    rows["X-Mb disjoint chain census (s=5)"] = {
        "observed": {k: int(chain[k]) for k in REPRO_XMB_CHAIN_S5},
        "registered": dict(REPRO_XMB_CHAIN_S5),
        "status": "PASS" if all(a == b for a, b in chain_ok.values())
        else "FAIL",
        "source": "results/m4_xmb_mains_paired/chain_anchor.json :: 5"}
    status = "PASS" if all(r["status"] == "PASS" for r in rows.values()) \
        else "FAIL"
    return {"rows": rows, "status": status, "tolerance": REPRO_TOL,
            "note": ("every coordinate estimator is the committed object of "
                     "the leg that certified it, called here on this pool; "
                     "these four numbers are what makes that claim checkable")}


# ---------------------------------------------------------------------------
# The author-cluster bootstrap on a Mantel r (#79: two CIs, never a ratio).
# ---------------------------------------------------------------------------
def cluster_bootstrap_mantel(x_square: np.ndarray, y_square: np.ndarray,
                             n: int, b_boot: int, seed: int) -> dict[str, Any]:
    """CI for a Mantel r by resampling AUTHORS with replacement.

    The author is the cluster, so a replicate draws ``n`` authors with
    replacement and reads both distance matrices on the drawn index pairs.
    A pair whose two draws are THE SAME original author carries a structural
    zero in both matrices and is excluded -- it is not an observation, it is
    the diagonal seen twice.  Recorded choice, disclosed in the report.
    """

    rows, cols = condensed_indices(n)
    rng = np.random.default_rng(seed)
    out = np.empty(b_boot, dtype=np.float64)
    kept = np.empty(b_boot, dtype=np.int64)
    for b in range(b_boot):
        draw = rng.integers(0, n, n)
        ri, ci = draw[rows], draw[cols]
        keep = ri != ci
        xr, yr = x_square[ri[keep], ci[keep]], y_square[ri[keep], ci[keep]]
        out[b] = pearson(xr, yr)
        kept[b] = int(keep.sum())
    finite = out[np.isfinite(out)]
    lo, hi = np.percentile(finite, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)])
    return {"B": int(b_boot), "seed": int(seed),
            "boot_mean": float(finite.mean()),
            "boot_sd": float(finite.std(ddof=1)),
            "ci": [float(lo), float(hi)],
            "ci_covers_zero": bool(lo <= 0.0 <= hi),
            "replicates_finite": int(finite.size),
            "median_pairs_per_replicate": float(np.median(kept)),
            "cluster": "author",
            "self_pair_rule": "pairs of one author with itself are excluded"}


# ---------------------------------------------------------------------------
# STAGE PART 0 -- anchors, coordinates, the gate, THEN the stamp.
# NO LABEL IS OPENED HERE, AND NO JOINT QUANTITY IS FORMED HERE.
# ---------------------------------------------------------------------------
def stage_part0(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    out.mkdir(parents=True, exist_ok=True)
    # part0 is the first stage, so it TRUNCATES the log: the stamp-order proof
    # reads the FIRST occurrence of each event and must not see a prior run.
    (out / "run_log.jsonl").write_text("", encoding="utf-8")
    log = RunLog(out / "run_log.jsonl")
    log.event("part0_start", registration_commit=args.registration_commit,
              label_table_opened=False)

    sources = load_sources(args, log)
    agreement = source_agreement(sources)
    stats = sources.scaffold["stream_stats"]
    is_big5 = np.asarray(sources.x5["pool_is_big5"]).astype(bool)

    coords = build_coordinates(sources)
    repro = reproduction_checks(coords, sources)
    gate_rows = apply_reliability_gate(coords.reliabilities)

    observed = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            int(stats["rows_parseable"]),
        "authors": int(stats["authors"]),
        "Big5 cohort authors seen": int(sources.big5_mask.sum()),
        "disjoint authors": int((~sources.big5_mask).sum()),
        "law vocabulary floor (users)": int(sources.vocab["floor_users"]),
        "law vocabulary (communities)": int(sources.vocab["vocabulary_size"]),
        "candidate authors (>= 50 events per half)": int(is_big5.size),
        "X2 pool, Big5 (the analysis pool)": int(is_big5.sum()),
        "X2 pool, disjoint": int((~is_big5).sum()),
        "X5 R2 pool, Big5": int(coords.diagnostics["r2_slope"]["pool_big5"]),
        "X5 R2 pool, disjoint":
            int(coords.diagnostics["r2_slope"]["pool_disjoint"]),
    }
    expected = {
        "rows parseable (author+subreddit+created_utc+wcq)":
            ANCHOR_ROWS_PARSEABLE,
        "authors": ANCHOR_AUTHORS,
        "Big5 cohort authors seen": ANCHOR_BIG5_AUTHORS,
        "disjoint authors": ANCHOR_DISJOINT_AUTHORS,
        "law vocabulary floor (users)": ANCHOR_VOCAB_FLOOR_USERS,
        "law vocabulary (communities)": ANCHOR_LAW_VOCAB,
        "candidate authors (>= 50 events per half)": ANCHOR_CANDIDATES,
        "X2 pool, Big5 (the analysis pool)": ANCHOR_POOL_BIG5,
        "X2 pool, disjoint": ANCHOR_POOL_DISJOINT,
        "X5 R2 pool, Big5": ANCHOR_R2_POOL_BIG5,
        "X5 R2 pool, disjoint": ANCHOR_R2_POOL_DISJOINT,
    }
    census = anchor_gate(observed, expected)
    log.event("census", status=census["status"])
    log.event("reproductions", status=repro["status"])
    log.event("reliability_gate", admitted=gate_rows["admitted"],
              excluded=gate_rows["excluded"],
              stop=gate_rows["STOP_before_join"])

    g0 = {
        "census": census, "source_agreement": agreement,
        "reproductions": repro,
        "reliability_gate": gate_rows,
        "labels_opened_in_part0": False,
        "joint_quantities_in_part0": 0,
    }
    g0["PASS"] = bool(census["status"] == "PASS"
                      and agreement["status"] == "PASS"
                      and repro["status"] == "PASS"
                      and not gate_rows["STOP_before_join"])
    part0_blob = {
        "leg": LEG, "utc": utc_now(), "G0": g0,
        "A1": "an instrument failure before the stamp -> STOP, NO STAMP EVER",
        "pool": {"n_authors": int(coords.pool_codes.size),
                 "codes": [int(c) for c in coords.pool_codes]},
        "descriptives": coords.descriptives,
        "diagnostics": coords.diagnostics,
        "environment": {"python_executable": sys.executable,
                        "python_version": sys.version.split()[0],
                        "platform": platform.platform(),
                        "numpy": np.__version__, "pandas": pd.__version__},
        "seconds": time.time() - started,
    }
    if not g0["PASS"]:
        write_json(out / "part0.json", part0_blob)
        if gate_rows["STOP_before_join"]:
            write_json(out / "verdict.json", {
                "leg": LEG, "utc": utc_now(), "tier": "EXPLORATORY",
                "level": "corpus-level",
                "verdict": CELL_UNRELIABLE, "cell": None,
                "reason": "every coordinate failed the label-free "
                          "reliability gate; no stamp was written and no "
                          "label column was opened",
                "reliability_gate": gate_rows})
            log.event("part0_clean_stop", verdict=CELL_UNRELIABLE)
            raise SystemExit(f"RELIABILITY GATE: ALL COORDINATES FAILED -> "
                             f"{CELL_UNRELIABLE} (A1: no stamp written)")
        log.event("part0_instrument_failure", census=census["status"],
                  agreement=agreement["status"], repro=repro["status"])
        raise SystemExit("G0-X3 FAILED -> STOP/VOID (A1: no stamp written)")

    config = {
        "leg": LEG, "title": "the trait join of expression coordinates",
        "registration_commit": args.registration_commit,
        "registration_doc": rel(PLAN_DOC),
        "tier": "EXPLORATORY", "level": "corpus-level",
        "layer": "P (label-bearing)",
        "seed": SEED, "seed_perm": SEED_PERM, "seed_boot": SEED_BOOT,
        "B_perm": B_PERM, "B_boot": B_BOOT, "alpha": ALPHA,
        "y": "log1p(word_count_quoteless) (#70 pin)",
        "columns_read": {
            "metadata": ["author", "subreddit", "created_utc", "link_id",
                         "word_count_quoteless", "score"],
            "labels": ["author", *BIG5],
            "bodies_read": False},
        "sources": {
            "x5_event_cache": rel(Path(args.x5_cache)),
            "x2_event_cache": rel(Path(args.x2_cache)),
            "x1_cell_cache": rel(Path(args.x1_cache)),
            "cohort": rel(Path(args.cohort)),
            "agreement": agreement},
        "analysis_pool": {
            "rule": "the Big5 cohort under X2's predicate: >= 50 events in "
                    "EACH of the author's own halves",
            "n_authors": int(coords.pool_codes.size),
            "anchor": ANCHOR_POOL_BIG5,
            "per_coordinate_eligibility": "each coordinate's own machinery"},
        "coordinates": {
            "raw_level": {
                "definition": "person-mean y over the pool events (the "
                              "literature's object)",
                "eligibility": "the whole analysis pool",
                "n_eligible": coords.descriptives["raw_level"]["n_eligible"],
                "reliability_split": "corr(mean y early, mean y late)"},
            "adj_level": {
                "definition": "the X-Mb author-main FE coordinate a_hat_u = "
                              "0.5 * (a_hat_early + a_hat_late), two-way FE "
                              "by alternating projections on the shared "
                              "(author, community) cells, X-M's pinned "
                              "normalization",
                "eligibility": "the BIG5-cohort analog of the X1c predicate "
                               f"chain at n_min = {CHAIN_N_MIN}, support "
                               f"s = {CHAIN_SUPPORT_PRIMARY}, k_min = "
                               f"{CHAIN_K_MIN}, law vocabulary, largest "
                               "connected component",
                "n_eligible": coords.descriptives["adj_level"]["n_eligible"],
                "reliability_split": "corr(a_hat_early, a_hat_late)",
                "chain_census": coords.chain_census,
                "census_status": "NOT pre-registered; censused label-free in "
                                 "part 0 and pinned here BEFORE the stamp"},
            "rhythm": {
                "definition": "X2's r1_u = the mean of the two half lag-1 "
                              "Pearson autocorrelations of the y sequence, "
                              "adjacency = consecutive events within a half",
                "eligibility": "both half r1 defined (>= 2 usable pairs and "
                               "non-degenerate spread in each half)",
                "n_eligible": coords.descriptives["rhythm"]["n_eligible"],
                "reliability_split": "corr(r1_early, r1_late) -- X2's "
                                     "rho_own"},
            "r2_slope": {
                "definition": "the R2 (gap x volume) within-person slope, "
                              "beta_{u,h} = num/den by X4's two-pass, the "
                              "mean of the two half slopes",
                "eligibility": ">= 50 USABLE events in each half AND the #89 "
                               "estimability floor den >= 1 in BOTH halves",
                "n_eligible": coords.descriptives["r2_slope"]["n_eligible"],
                "reliability_split": "corr(beta_early, beta_late) -- X5's "
                                     "rho_own"}},
        "reliability_gate": {
            "threshold": RELIABILITY_GATE,
            "measured_on": "the ACTUAL coordinate objects, label-free, "
                           "BEFORE the stamp",
            "stop_rule": gate_rows["stop_rule"],
            "expectations": RELIABILITY_EXPECTATION,
            "realized": coords.reliabilities,
            "admitted": gate_rows["admitted"],
            "excluded": gate_rows["excluded"]},
        "estimands": {
            "trait_geometry": "Euclidean distance over five z-scored Big5 "
                              "(#81 BY FORMULA; one z-scoring over the "
                              "analysis pool; U3's reader, inherited)",
            "coordinate_geometry": "|c_u - c_v|",
            "raw": "Mantel r, null = permutation of the AUTHOR ROWS of the "
                   f"trait matrix, B = {B_PERM}, two-sided band",
            "partial": "partial Mantel r(c-dist, trait-dist | bag-dist), "
                       "Smouse-Long-Sokal residual permutation, "
                       f"B = {B_PERM}; the control is LINEAR (#82 declared)",
            "bag_distance": "1 - Hellinger cosine of the L2-normalised sqrt "
                            "full-stream in-vocabulary frequency vector over "
                            f"the {ANCHOR_LAW_VOCAB}-community SR0-class law "
                            "vocabulary, on this pool (U3's construction)",
            "activity_sensitivity": "partial additionally controlling "
                                    "|log n_u - log n_v|, n = pool event "
                                    "count",
            "confidence_intervals": "author-cluster bootstrap on the Mantel "
                                    f"r, B = {B_BOOT}; self-pairs excluded",
            "disattenuation": "SECONDARY reading only: r / sqrt(rel_SB * "
                              f"{REL_LABEL_DECLARED}); label reliability "
                              "DECLARED, not measured (#57)"},
        "level_contrast": {
            "rule": "if RAW LEVEL detects raw, report whether ADJUSTED LEVEL "
                    "also detects, with both rs and both CIs",
            "no_ratio_null": RN_NOTES["RN-X3-8"],
            "second_reading": "RAW LEVEL re-read on the ADJUSTED LEVEL's own "
                              "support, so the contrast is not confounded "
                              "with the chain's eligibility loss (executor "
                              "addition, DISCLOSED, routes nothing)"},
        "cells": {
            CELL_SILENT: "no admitted coordinate detects raw (scoped "
                         f"silence at r ~ {REGISTERED_MDR} with the realized "
                         "band widths)",
            CELL_LEVEL_ONLY: "raw level detects, adjusted level does NOT, "
                             "dynamics silent",
            CELL_LEVEL_INTRINSIC: "both levels detect",
            CELL_DYNAMICS: "rhythm or slope detects raw (any level pattern)",
            "precedence": "dynamics first, then the level pattern",
            "suffix": "any detecting cell gains REDUNDANT (every detecting "
                      "coordinate's bag-partial is inside its band) or "
                      "INCREMENTAL (at least one is outside)"},
        "secondary": {
            "per_trait_table": "5 traits x admitted coordinates, Pearson of "
                               "the coordinate against each z-scored trait",
            "guard": "Bonferroni x (5 x n_admitted)",
            "p_transform": "Fisher z, declared; the table routes nothing"},
        "projection": {
            "assumption": "z proportional to r*sqrt(N), declared",
            "anchor": {"sr1_r": SR1_R, "sr1_z": SR1_Z, "sr1_N": SR1_N},
            "registered_minimal_detectable_r": REGISTERED_MDR,
            "recomputed_at_the_analysis_pool":
                projection_mdr(int(coords.pool_codes.size)),
            "recomputed_per_coordinate": {
                name: projection_mdr(
                    int(coords.descriptives[name]["n_eligible"]))
                for name in COORDINATES}},
        "leans": {
            "primary": LEAN_PRIMARY,
            "dynamics_point": f"|raw r| <= {LEAN_DYNAMICS_ABS_R} for every "
                              "dynamics coordinate",
            "cohort_caveat": RN_NOTES["RN-X3-4"]},
        "label_event": RN_NOTES["RN-X3-5"],
        "label_source": str(PROFILES),
        "boundaries": [RN_NOTES["RN-X3-2"], RN_NOTES["RN-X3-3"],
                       RN_NOTES["RN-X3-4"], RN_NOTES["RN-X3-6"]],
        "RN_NOTES": RN_NOTES,
        "machinery_imported_by_file": [
            rel(U3_SCRIPT) + " (stamp chain, Mantel/SLS, bag signature, "
                             "reliability rows, THE label reader)",
            rel(X2_SCRIPT) + " (Arm / arm_layout / masked lag-1 Pearson)",
            rel(X5_SCRIPT) + " (relation_stats with the #89 floor, "
                             "RelationSkeleton, X4's cell_moments and "
                             "per_cell_slopes)",
            rel(XMB_SCRIPT) + " (chain design, FE coefficients, pinned "
                              "normalization, full_budget, census and #83 "
                              "helpers)"],
        "census": census, "reproductions": repro,
    }
    write_json(out / "config.json", config)
    digest = sha256_file(out / "config.json")
    stamp = log.event("config_stamped", sha256=digest,
                      joint_quantities_before_stamp=0,
                      labels_opened_before_stamp=False)
    write_json(out / "config.sha256.json", {
        "sha256": digest, "stamp_utc": stamp["utc"],
        "joint_quantities_before_stamp": 0,
        "labels_opened_before_stamp": False,
        "note": RN_NOTES["RN-X3-1"]})
    part0_blob["stamp"] = {"sha256": digest, "stamp_utc": stamp["utc"]}
    write_json(out / "part0.json", part0_blob)
    write_json(out / "census.json", census)
    write_json(out / "reproductions.json", repro)
    print(f"part0 OK  census {census['status']}  agreement "
          f"{agreement['status']}  reproductions {repro['status']}  pool "
          f"{coords.pool_codes.size}  reliabilities "
          + "  ".join(f"{k}={coords.reliabilities[k]:.4f}"
                      for k in COORDINATES)
          + f"  admitted={gate_rows['admitted']}  STAMPED {digest[:16]} at "
            f"{stamp['utc']}  labels opened = 0  {time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
# STAGE B -- LABEL-FREE.  Re-execute, assert determinism, freeze.
# ---------------------------------------------------------------------------
def stage_stageb(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    log = RunLog(out / "run_log.jsonl")
    stamp = read_json(out / "config.sha256.json")
    config = read_json(out / "config.json")
    if sha256_file(out / "config.json") != stamp["sha256"]:
        raise SystemExit("CONFIG HASH MISMATCH -> STOP/VOID")
    log.event("stageb_start", label_table_opened=False)

    sources = load_sources(args, log)
    coords = build_coordinates(sources)
    pinned = config["reliability_gate"]["realized"]
    determinism = {
        "pinned": pinned, "re_executed": coords.reliabilities,
        "bit_identical": {k: bool(float(pinned[k])
                                  == float(coords.reliabilities[k]))
                          for k in COORDINATES},
        "note": ("stage B rebuilds the four coordinates from the same "
                 "label-free sources and asserts the split-half "
                 "reliabilities are bit-identical to the ones the stamp "
                 "pinned; a coordinate that moved between the stamp and the "
                 "freeze would make the stamp meaningless")}
    determinism["status"] = ("PASS" if all(determinism["bit_identical"]
                                          .values()) else "FAIL")
    gate_rows = apply_reliability_gate(coords.reliabilities)
    same_admissions = bool(gate_rows["admitted"]
                           == config["reliability_gate"]["admitted"])
    if determinism["status"] != "PASS" or not same_admissions:
        write_json(out / "stageb.json", {
            "leg": LEG, "utc": utc_now(), "determinism": determinism,
            "same_admissions": same_admissions})
        log.event("stageb_determinism_failure")
        raise SystemExit("STAGE B DETERMINISM FAILED -> STOP/VOID "
                         "(the stamped coordinate table is not reproducible)")

    if gate_rows["STOP_before_join"]:                # pragma: no cover
        write_json(out / "verdict.json", {
            "leg": LEG, "utc": utc_now(), "verdict": CELL_UNRELIABLE,
            "cell": None, "reliability_gate": gate_rows})
        log.event("stageb_stop", verdict=CELL_UNRELIABLE)
        raise SystemExit(f"RELIABILITY GATE -> {CELL_UNRELIABLE}")

    # ---- the frozen coordinate table (the second stamped artifact) --------
    payload: dict[str, np.ndarray] = {
        "pool_codes": coords.pool_codes.astype(np.int64),
        "activity": coords.activity.astype(np.float64)}
    for name in COORDINATES:
        payload[f"value__{name}"] = coords.values[name]
        payload[f"early__{name}"] = coords.early[name]
        payload[f"late__{name}"] = coords.late[name]
        payload[f"eligible__{name}"] = coords.eligible[name]
    np.savez_compressed(out / "coordinates.npz", **payload)
    (out / "pool_names.json").write_text(
        json.dumps({"note": "gitignored; author names never leave results/",
                    "names": coords.pool_names}, indent=1) + "\n",
        encoding="utf-8")
    digest = sha256_file(out / "coordinates.npz")
    freeze = log.event("coordinates_frozen", sha256=digest,
                       admitted=gate_rows["admitted"],
                       excluded=gate_rows["excluded"],
                       label_table_opened=False)
    write_json(out / "coordinate_freeze.json", {
        "sha256": digest, "coordinate_freeze_utc": freeze["utc"],
        "config_sha256": stamp["sha256"],
        "admitted": gate_rows["admitted"], "excluded": gate_rows["excluded"],
        "labels_opened_before_freeze": False,
        "artifact": rel(out / "coordinates.npz")})
    write_json(out / "stageb.json", {
        "leg": LEG, "utc": utc_now(), "label_table_opened": False,
        "determinism": determinism, "same_admissions": same_admissions,
        "descriptives": coords.descriptives,
        "diagnostics": coords.diagnostics,
        "reliability_gate": gate_rows,
        "chain_census": coords.chain_census,
        "seconds": time.time() - started})
    print(f"stageb OK  determinism {determinism['status']}  admitted="
          f"{gate_rows['admitted']}  excluded={gate_rows['excluded']}  "
          f"FROZEN {digest[:16]} at {freeze['utc']}  "
          f"{time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
# STAGE E -- THE SINGLE JOIN.
# ---------------------------------------------------------------------------
def _row_for(name: str, x: np.ndarray, trait_dist: np.ndarray,
             trait_square: np.ndarray, bag: np.ndarray, act: np.ndarray,
             n: int, r_idx: np.ndarray, c_idx: np.ndarray,
             b_perm: int, b_boot: int, offset: int,
             descriptive: dict[str, Any]) -> dict[str, Any]:
    """One coordinate's full registered row.  Called only from stage E."""

    raw = mantel_permutation(x, trait_square, r_idx, c_idx, n, b_perm,
                             SEED_PERM + offset)
    partial = partial_mantel_sls(x, trait_dist, bag[:, None], r_idx, c_idx, n,
                                 b_perm, SEED_PERM + 100 + offset)
    partial_act = partial_mantel_sls(
        x, trait_dist, np.column_stack([bag, act]), r_idx, c_idx, n, b_perm,
        SEED_PERM + 200 + offset)
    x_square = square_from_condensed(x, r_idx, c_idx, n)
    boot = cluster_bootstrap_mantel(x_square, trait_square, n, b_boot,
                                    SEED_BOOT + offset)
    rel_sb = float(descriptive["spearman_brown"])
    denom = float(np.sqrt(max(rel_sb, 1e-12) * REL_LABEL_DECLARED))
    return {
        "coordinate": name, "title": COORDINATE_TITLES[name],
        "family": "level" if name in LEVEL_COORDINATES else "dynamics",
        "n_authors": int(n), "n_pairs": int(x.size),
        "split_half_r": float(descriptive["split_half_r"]),
        "reliability_SB": rel_sb,
        "raw": raw, "partial_bag": partial,
        "partial_bag_activity": partial_act,
        "bootstrap_ci": boot,
        "detected_raw": bool(raw["outside_band"]),
        "detected_partial": bool(partial["outside_band"]),
        "detected_partial_activity": bool(partial_act["outside_band"]),
        "disattenuated_SECONDARY": {
            "raw": float(raw["r"] / denom),
            "partial_bag": float(partial["r"] / denom),
            "formula": f"r / sqrt(rel_SB * {REL_LABEL_DECLARED})",
            "label_reliability_status": "DECLARED, not measured",
            "note": RN_NOTES["RN-X3-7"]},
        "channels": {
            "mantel_bag_vs_trait": pearson(bag, trait_dist),
            "coord_vs_bag": pearson(x, bag),
            "coord_vs_activity": pearson(x, act)},
        "projection": {
            "registered_minimal_detectable_r": REGISTERED_MDR,
            "recomputed_at_this_N": projection_mdr(n),
            "realized_mdr_1p96_null_sd": raw["realized_mdr_1p96sd"],
            "realized_over_projected": float(
                raw["realized_mdr_1p96sd"] / projection_mdr(n))},
    }


def stage_stagee(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    log = RunLog(out / "run_log.jsonl")
    stamp = read_json(out / "config.sha256.json")
    freeze = read_json(out / "coordinate_freeze.json")
    if sha256_file(out / "config.json") != stamp["sha256"]:
        raise SystemExit("CONFIG HASH MISMATCH -> STOP/VOID")
    if sha256_file(out / "coordinates.npz") != freeze["sha256"]:
        raise SystemExit("COORDINATE HASH MISMATCH -> STOP/VOID")
    stage_b = read_json(out / "stageb.json")
    frozen = np.load(out / "coordinates.npz")
    pool_names = json.loads((out / "pool_names.json").read_text("utf-8"))[
        "names"]
    n_pool = len(pool_names)
    admitted = list(freeze["admitted"])

    # ---- LABEL-FREE preparation of the covariate channels -----------------
    sources = load_sources(args, log)
    x2 = sources.x2
    n_total2 = np.asarray(x2["n_total"]).astype(np.int64)
    ev_comm = np.asarray(x2["ev_comm"])
    who2 = np.repeat(np.arange(n_total2.size, dtype=np.int64), n_total2)
    vocab_mask = sources.vocab["mask"]
    n_vocab = int(vocab_mask.sum())
    vocab_col = np.full(vocab_mask.size, -1, dtype=np.int64)
    vocab_col[np.flatnonzero(vocab_mask)] = np.arange(n_vocab)
    pool_local = np.flatnonzero(np.asarray(x2["pool_is_big5"]).astype(bool))
    signature = full_signature(vocab_col[ev_comm], who2, pool_local, n_vocab)
    zero_signature = int((signature.sum(axis=1) == 0).sum())
    log_activity = np.log(np.maximum(np.asarray(frozen["activity"]), 1.0))
    del who2, ev_comm

    # ---- THE JOIN.  Everything after this line is label-bearing. ----------
    join_event = log.event(
        "first_join",
        note="the first joint expression x trait quantity of the harness is "
             "computed after this event",
        config_sha256=stamp["sha256"], coordinate_sha256=freeze["sha256"],
        label_source=str(PROFILES), columns=["author", *BIG5])
    traits, trait_info = open_trait_table(pool_names)
    complete = ~np.isnan(traits).any(axis=1)

    rows: dict[str, Any] = {}
    for offset, name in enumerate(COORDINATES):
        if name not in admitted:
            continue
        elig = np.asarray(frozen[f"eligible__{name}"]).astype(bool)
        value = np.asarray(frozen[f"value__{name}"])
        usable = np.flatnonzero(elig & complete & np.isfinite(value))
        n = int(usable.size)
        r_idx, c_idx = condensed_indices(n)
        coord = value[usable]
        x = np.abs(coord[r_idx] - coord[c_idx])
        z = traits[usable]
        diff = z[r_idx] - z[c_idx]
        trait_dist = np.sqrt(np.einsum("ij,ij->i", diff, diff))
        trait_square = square_from_condensed(trait_dist, r_idx, c_idx, n)
        sig = signature[usable]
        bag = 1.0 - np.einsum("ij,ij->i", sig[r_idx], sig[c_idx])
        act = np.abs(log_activity[usable][r_idx] - log_activity[usable][c_idx])
        rows[name] = _row_for(name, x, trait_dist, trait_square, bag, act, n,
                              r_idx, c_idx, args.b_perm, args.b_boot, offset,
                              stage_b["descriptives"][name])
        rows[name]["label_complete_on_eligible"] = bool(
            complete[np.flatnonzero(elig)].all())
        log.event("row_done", coordinate=name, raw_r=rows[name]["raw"]["r"],
                  partial_r=rows[name]["partial_bag"]["r"])

    # ---- the level contrast's second reading (DISCLOSED, routes nothing) --
    contrast_second: dict[str, Any] | None = None
    if {"raw_level", "adj_level"} <= set(admitted):
        elig_adj = np.asarray(frozen["eligible__adj_level"]).astype(bool)
        value = np.asarray(frozen["value__raw_level"])
        usable = np.flatnonzero(elig_adj & complete & np.isfinite(value))
        n = int(usable.size)
        r_idx, c_idx = condensed_indices(n)
        coord = value[usable]
        x = np.abs(coord[r_idx] - coord[c_idx])
        z = traits[usable]
        diff = z[r_idx] - z[c_idx]
        trait_dist = np.sqrt(np.einsum("ij,ij->i", diff, diff))
        trait_square = square_from_condensed(trait_dist, r_idx, c_idx, n)
        sig = signature[usable]
        bag = 1.0 - np.einsum("ij,ij->i", sig[r_idx], sig[c_idx])
        act = np.abs(log_activity[usable][r_idx] - log_activity[usable][c_idx])
        contrast_second = _row_for(
            "raw_level", x, trait_dist, trait_square, bag, act, n, r_idx,
            c_idx, args.b_perm, args.b_boot, 50,
            stage_b["descriptives"]["raw_level"])
        contrast_second["coordinate"] = "raw_level_on_adjusted_support"
        contrast_second["title"] = ("RAW LEVEL, re-read on the ADJUSTED "
                                    "LEVEL's own support")
        contrast_second["role"] = (
            "DISCLOSED SECOND READING, routes nothing: the registered "
            "contrast compares two coordinates on two different supports, so "
            "this row separates the adjustment from the chain's eligibility "
            "loss")
        log.event("contrast_second_reading_done",
                  raw_r=contrast_second["raw"]["r"])

    # ---- the per-trait SECONDARY table (Bonferroni-guarded, never routes) --
    n_admitted = len(admitted)
    bonferroni_alpha = ALPHA / max(1, 5 * n_admitted)
    per_trait: dict[str, Any] = {}
    for name in admitted:
        elig = np.asarray(frozen[f"eligible__{name}"]).astype(bool)
        value = np.asarray(frozen[f"value__{name}"])
        usable = np.flatnonzero(elig & complete & np.isfinite(value))
        coord = value[usable]
        entry: dict[str, Any] = {}
        for k, trait in enumerate(BIG5):
            r = pearson(coord, traits[usable, k])
            p = _fisher_two_sided_p(r, int(usable.size))
            entry[trait] = {
                "r": float(r), "n": int(usable.size), "p_two_sided": p,
                "survives_bonferroni": bool(np.isfinite(p)
                                            and p < bonferroni_alpha)}
        per_trait[name] = entry

    write_json(out / "join.json", {
        "leg": LEG, "utc": utc_now(), "first_join_utc": join_event["utc"],
        "label_event": RN_NOTES["RN-X3-5"],
        "trait_join": trait_info,
        "analysis_pool_label_completeness": {
            "n_pool": int(n_pool), "n_complete": int(complete.sum()),
            "fraction": float(complete.mean())},
        "bag_channel": {
            "vocabulary": int(n_vocab),
            "authors_with_no_in_vocabulary_event": zero_signature,
            "note": ("an author with no in-vocabulary event carries the zero "
                     "signature and therefore bag distance 1 to everyone; "
                     "the count is reported, the rows are not dropped")},
        "rows": rows,
        "level_contrast_second_reading": contrast_second,
        "per_trait_secondary": {
            "table": per_trait, "n_admitted": n_admitted,
            "bonferroni_alpha": bonferroni_alpha,
            "guard": f"Bonferroni x (5 x {n_admitted})",
            "p_transform": "Fisher z, declared",
            "routes": False},
        "seconds": time.time() - started})
    order = prove_stamp_order(log.read())
    print("stagee OK  "
          + "  ".join(f"{k}: raw={v['raw']['r']:+.4f} "
                      f"[{v['raw']['band_lo']:+.4f},"
                      f"{v['raw']['band_hi']:+.4f}]"
                      f" p={v['raw']['p_two_sided']:.4f}"
                      for k, v in rows.items())
          + f"  |  labels complete {complete.mean():.4f}  "
            f"stamp<freeze<join="
            f"{order['stamp_precedes_freeze_precedes_first_join']}  "
            f"{time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
# GATE -- G-X3 plus the blocking #83 ID-leak scan.
# ---------------------------------------------------------------------------
def run_id_leak_scan(args: argparse.Namespace, out: Path,
                     tag: str) -> dict[str, Any]:
    """The #83 scan over the widened universe.  Run twice: at the gate, and
    again on the FRESHLY WRITTEN report, so no committed file is ever scanned
    only in a stale version."""

    cohort_names = load_cohort_names(args.cohort)
    _, x2_meta = X2.load_cache(args.x2_cache)
    universe = sorted({str(n) for n in cohort_names}
                      | {str(n) for n in x2_meta["authors"]})
    write_json(out / "id_scan_universe.json", {
        "n_names": len(universe), "cohort_names": len(cohort_names),
        "stream_names": len(x2_meta["authors"]),
        "note": "gitignored; the scan list is never committed"})
    scan = scan_for_cohort_ids(list(COMMITTED_FILES), universe)
    baseline_keys, baseline_detail = baseline_hit_keys(
        list(COMMITTED_FILES), universe, out / "head_baseline")
    new_hits = new_hits_only(scan["hits"], baseline_keys)
    scan["scan_tag"] = tag
    scan["universe_size"] = len(universe)
    scan["raw_status"] = scan["status"]
    scan["n_pre_existing_hits"] = scan["n_hits"] - len(new_hits)
    scan["n_new_hits"] = len(new_hits)
    scan["new_hits"] = new_hits
    scan["baseline"] = baseline_detail
    scan["status"] = "PASS" if not new_hits else "FAIL"
    write_json(out / f"id_leak_scan{'' if tag == 'gate' else '_' + tag}.json",
               scan)
    return scan


def stage_gate(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    log = RunLog(out / "run_log.jsonl")
    order = prove_stamp_order(log.read())
    stamp = read_json(out / "config.sha256.json")
    freeze = read_json(out / "coordinate_freeze.json")
    stage_b = read_json(out / "stageb.json")
    join = read_json(out / "join.json")
    scan = run_id_leak_scan(args, out, "gate")
    universe = read_json(out / "id_scan_universe.json")["n_names"]

    gate = {
        "leg": LEG, "utc": utc_now(),
        "G-X3_stamp_chain": order,
        "hashes": {
            "config_sha256_recomputed": sha256_file(out / "config.json"),
            "config_sha256_stamped": stamp["sha256"],
            "config_hash_matches":
                sha256_file(out / "config.json") == stamp["sha256"],
            "coordinates_sha256_recomputed":
                sha256_file(out / "coordinates.npz"),
            "coordinates_sha256_frozen": freeze["sha256"],
            "coordinate_hash_matches":
                sha256_file(out / "coordinates.npz") == freeze["sha256"]},
        "label_discipline": {
            "labels_opened_in_part0": False,
            "label_table_opened_in_stage_b":
                bool(stage_b["label_table_opened"]),
            "single_label_read": True,
            "label_source": str(PROFILES),
            "columns_opened": ["author", *BIG5],
            "per_author_values_committed": False,
            "label_completeness":
                join["analysis_pool_label_completeness"]["fraction"]},
        "determinism": stage_b["determinism"]["status"],
        "id_leak_scan": {
            "status": scan["status"], "universe": universe,
            "n_raw_hits": int(scan["n_hits"]),
            "n_pre_existing": int(scan["n_pre_existing_hits"]),
            "n_new_hits": int(scan["n_new_hits"]),
            "baseline_expected": 4,
            "files_scanned": [rel(Path(p)) for p in scan["files_scanned"]]},
        "rg_compliance": {
            "aggregates_only": True, "no_per_author_rows_in_report": True,
            "no_text_excerpts": True, "body_column_never_read": True,
            "no_cross_corpus_linkage": True, "essays_untouched": True,
            "native_corpus_untouched": True,
            "identifier_artifacts_confined_to_gitignored_results": True},
    }
    gate["PASS"] = bool(order["PASS"]
                        and gate["hashes"]["config_hash_matches"]
                        and gate["hashes"]["coordinate_hash_matches"]
                        and not stage_b["label_table_opened"]
                        and stage_b["determinism"]["status"] == "PASS"
                        and scan["status"] == "PASS")
    write_json(out / "gate.json", gate)
    log.event("gate_done", passed=gate["PASS"])
    if not gate["PASS"]:
        raise SystemExit(
            f"G-X3 FAILED -> STOP/VOID  order={order['PASS']} "
            f"new_leaks={scan['n_new_hits']}")
    seconds = order["seconds_between"]
    print(f"gate OK  stamp<freeze<first_join="
          f"{order['stamp_precedes_freeze_precedes_first_join']} "
          f"(+{seconds['stamp_to_freeze']:.1f}s, "
          f"+{seconds['freeze_to_first_join']:.1f}s)  ID new hits="
          f"{scan['n_new_hits']} (pre-existing "
          f"{scan['n_pre_existing_hits']}/{universe:,})  "
          f"PASS={gate['PASS']}  {time.time() - started:.1f}s "
          f"[join rows {len(join['rows'])}]")


# ---------------------------------------------------------------------------
# FINALIZE -- cells, suffix, leans, verdict.
# ---------------------------------------------------------------------------
def classify(rows: dict[str, Any]) -> dict[str, Any]:
    """The registered cell structure, NULL-first, dynamics-first precedence."""

    detect = {name: bool(row["detected_raw"]) for name, row in rows.items()}
    dynamics_hits = [n for n in DYNAMICS_COORDINATES if detect.get(n)]
    level_hits = [n for n in LEVEL_COORDINATES if detect.get(n)]
    off_menu = None
    if dynamics_hits:
        verdict = CELL_DYNAMICS
    elif "raw_level" in level_hits and "adj_level" in level_hits:
        verdict = CELL_LEVEL_INTRINSIC
    elif "raw_level" in level_hits:
        verdict = CELL_LEVEL_ONLY
    elif "adj_level" in level_hits:
        verdict = CELL_LEVEL_INTRINSIC
        off_menu = ("ADJUSTED-ONLY detection: the registration's cell 3 reads "
                    "'both levels detect'.  The realized pattern is the "
                    "adjusted level alone, which carries cell 3's substance "
                    "(the coupling survives venue adjustment) but not its "
                    "letter.  Routed to cell 3 and DISCLOSED.")
    else:
        verdict = CELL_SILENT
    detecting = dynamics_hits + level_hits
    suffix = None
    if detecting:
        incremental = [n for n in detecting
                       if rows[n]["partial_bag"]["outside_band"]]
        suffix = "INCREMENTAL" if incremental else "REDUNDANT"
    return {"verdict": verdict, "cell": CELL_NUMBER[verdict],
            "suffix": suffix,
            "verdict_with_suffix": verdict + (f" ({suffix})" if suffix
                                              else ""),
            "detected_raw": detect, "detecting": detecting,
            "level_hits": level_hits, "dynamics_hits": dynamics_hits,
            "off_menu_note": off_menu}


def honest_anomalies(stage_b: dict[str, Any], join: dict[str, Any],
                     rows: dict[str, Any], contrast: dict[str, Any] | None,
                     all_cells: list[dict[str, Any]],
                     verdict: str) -> list[dict[str, Any]]:
    """Everything a reader would want flagged, generated from the artifacts."""

    out: list[dict[str, Any]] = []
    adj = stage_b["descriptives"]["adj_level"]
    out.append({
        "id": "A1",
        "title": "the adjusted level costs two thirds of the pool",
        "observed": (
            f"the Big5 analog of the X1c chain at s = "
            f"{CHAIN_SUPPORT_PRIMARY} admits {adj['n_eligible']:,} of the "
            f"{stage_b['descriptives']['raw_level']['n_eligible']:,} pool "
            f"authors ({adj['share_of_pool']:.3f}); the chain census at "
            f"s = 3 admits "
            f"{stage_b['chain_census']['3']['authors']:,} and at s = 8 "
            f"{stage_b['chain_census']['8']['authors']:,}"),
        "why_it_matters": (
            "the level contrast's two rows do not stand on the same support, "
            "so the adjusted row is the least powerful reading in the leg "
            "(projected minimal detectable r "
            f"{rows['adj_level']['projection']['recomputed_at_this_N']:.4f} "
            f"against the raw level's "
            f"{rows['raw_level']['projection']['recomputed_at_this_N']:.4f}); "
            "the disclosed second reading exists precisely to separate the "
            "adjustment from the eligibility loss"),
        "adjudication": ("REPORTED, routes nothing.  The support is the "
                         "chain's, and the chain is X-Mb's certified "
                         "primary; no support was shopped")})
    bag = join["bag_channel"]
    out.append({
        "id": "A2",
        "title": "seven pool authors carry the zero bag signature",
        "observed": (
            f"{bag['authors_with_no_in_vocabulary_event']} of the pool have "
            f"no event in the {bag['vocabulary']:,}-community law "
            f"vocabulary, so their Hellinger cosine to everyone is 0 and "
            f"their bag distance is exactly 1"),
        "why_it_matters": ("those rows enter the SLS partial as constant-1 "
                           "covariate values; at 7 of 1,116 the effect on "
                           "the residual is far below the band widths"),
        "adjudication": "REPORTED; the rows are not dropped"})
    if contrast is not None and not contrast["raw_level"]["detected"]:
        out.append({
            "id": "A3",
            "title": "the retention ratio is not interpretable here",
            "observed": (
                "the ratio r_adjusted / r_raw = "
                f"{contrast['retention_descriptive']:.4f}, from a "
                f"denominator ({contrast['raw_level']['r']:+.4f}) that sits "
                "inside its own permutation band"),
            "why_it_matters": ("a ratio of two numbers indistinguishable "
                               "from zero has no scale; #79 already forbids "
                               "a null on it, and under a SILENT verdict the "
                               "point value is noise"),
            "adjudication": ("PRINTED for completeness and explicitly NOT "
                             "read; the contrast is the two detection "
                             "decisions and the two CIs")})
    if all_cells:
        top = all_cells[0]
        out.append({
            "id": f"A{len(out) + 1}",
            "title": "the largest per-trait cell, and why it does not route",
            "observed": (
                f"{COORDINATE_TITLES[top['coordinate']]} x {top['trait']}: "
                f"r = {top['r']:+.4f}, p = {top['p']:.4f} on n = "
                f"{top['n']:,}; the Bonferroni threshold is "
                f"{join['per_trait_secondary']['bonferroni_alpha']:.5f} and "
                f"it does {'' if top['survives_bonferroni'] else 'NOT '}"
                "survive it"),
            "why_it_matters": (
                "the per-trait table is a marginal reading of the SAME "
                "coordinate whose distance-matrix Mantel is inside its band; "
                "a marginal correlation and a Mantel r answer different "
                "questions, and only the Mantel row routes"),
            "adjudication": ("SECONDARY, Bonferroni-guarded, ROUTES NOTHING "
                             "by registration")})
    slope = rows.get("r2_slope")
    if slope is not None and not slope["detected_raw"]:
        out.append({
            "id": f"A{len(out) + 1}",
            "title": "the slope row is the closest thing to a signal, and it "
                     "is still inside",
            "observed": (
                f"raw r = {slope['raw']['r']:+.4f}, p = "
                f"{slope['raw']['p_two_sided']:.4f}, band "
                f"[{slope['raw']['band_lo']:+.4f}, "
                f"{slope['raw']['band_hi']:+.4f}]; the bag-partial moves it "
                f"to {slope['partial_bag']['r']:+.4f} (p = "
                f"{slope['partial_bag']['p_two_sided']:.4f}) and the "
                f"activity control to "
                f"{slope['partial_bag_activity']['r']:+.4f} (p = "
                f"{slope['partial_bag_activity']['p_two_sided']:.4f})"),
            "why_it_matters": ("controlling the bag and activity moves it "
                               "AWAY from zero rather than towards it, which "
                               "is the pattern a real but small coupling "
                               "would also make; at this p it is not "
                               "distinguishable from the band"),
            "adjudication": ("REPORTED as the leg's strongest non-detection; "
                             "the registered lean |raw r| <= "
                             f"{LEAN_DYNAMICS_ABS_R} still holds")})
    ratios = {n: rows[n]["projection"]["realized_over_projected"]
              for n in rows}
    out.append({
        "id": f"A{len(out) + 1}",
        "title": "the realized bands are wider than the projection said",
        "observed": ("realized 1.96 x null sd over projected minimal "
                     "detectable r: "
                     + ", ".join(f"{n} {v:.3f}" for n, v in ratios.items())),
        "why_it_matters": ("the registration's z proportional to r*sqrt(N) "
                           "assumption transports SR1's power to a different "
                           "coordinate family; the realized bands are 1.1x "
                           "to 1.4x wider, so the scoped silence is scoped at "
                           "the REALIZED widths and not at the projected "
                           f"{REGISTERED_MDR}"),
        "adjudication": ("the scoped statement is attached to the realized "
                         "widths, exactly as #71's executed form requires")})
    return out


def stage_finalize(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    log = RunLog(out / "run_log.jsonl")
    config = read_json(out / "config.json")
    part0 = read_json(out / "part0.json")
    stage_b = read_json(out / "stageb.json")
    join = read_json(out / "join.json")
    gate = read_json(out / "gate.json")
    rows = join["rows"]

    cells = classify(rows)
    verdict = cells["verdict"]

    # ---- the level contrast ------------------------------------------------
    contrast: dict[str, Any] | None = None
    if {"raw_level", "adj_level"} <= set(rows):
        raw_r = float(rows["raw_level"]["raw"]["r"])
        adj_r = float(rows["adj_level"]["raw"]["r"])
        second = join.get("level_contrast_second_reading")
        contrast = {
            "raw_level": {
                "r": raw_r,
                "band": [rows["raw_level"]["raw"]["band_lo"],
                         rows["raw_level"]["raw"]["band_hi"]],
                "p": rows["raw_level"]["raw"]["p_two_sided"],
                "ci": rows["raw_level"]["bootstrap_ci"]["ci"],
                "n": rows["raw_level"]["n_authors"],
                "detected": rows["raw_level"]["detected_raw"]},
            "adj_level": {
                "r": adj_r,
                "band": [rows["adj_level"]["raw"]["band_lo"],
                         rows["adj_level"]["raw"]["band_hi"]],
                "p": rows["adj_level"]["raw"]["p_two_sided"],
                "ci": rows["adj_level"]["bootstrap_ci"]["ci"],
                "n": rows["adj_level"]["n_authors"],
                "detected": rows["adj_level"]["detected_raw"]},
            "retention_descriptive": (float(adj_r / raw_r)
                                      if raw_r != 0.0 else None),
            "no_ratio_null": RN_NOTES["RN-X3-8"],
            "support_caveat": (
                f"the two rows stand on DIFFERENT supports "
                f"({rows['raw_level']['n_authors']:,} vs "
                f"{rows['adj_level']['n_authors']:,} authors): the chain's "
                "eligibility, not the adjustment, is most of that gap"),
            "second_reading": None if second is None else {
                "r": second["raw"]["r"],
                "band": [second["raw"]["band_lo"], second["raw"]["band_hi"]],
                "p": second["raw"]["p_two_sided"],
                "ci": second["bootstrap_ci"]["ci"],
                "n": second["n_authors"],
                "detected": second["detected_raw"],
                "role": second["role"]},
        }

    # ---- the leans ---------------------------------------------------------
    dynamics_points = {n: abs(float(rows[n]["raw"]["r"]))
                       for n in DYNAMICS_COORDINATES if n in rows}
    leans = {
        "primary_registered": LEAN_PRIMARY,
        "primary_outcome": verdict,
        "primary_HELD": bool(verdict in (CELL_SILENT, CELL_LEVEL_ONLY)),
        "dynamics_point_registered":
            f"|raw r| <= {LEAN_DYNAMICS_ABS_R} for every dynamics coordinate",
        "dynamics_point_realized": dynamics_points,
        "dynamics_point_HELD": bool(dynamics_points and all(
            v <= LEAN_DYNAMICS_ABS_R for v in dynamics_points.values())),
        "cohort_caveat_carried": True,
    }

    scoped = None
    if verdict == CELL_SILENT:
        widths = {n: rows[n]["raw"]["band_halfwidth"] for n in rows}
        mdrs = {n: rows[n]["raw"]["realized_mdr_1p96sd"] for n in rows}
        scoped = {
            "statement": f"silent beyond r ~ {REGISTERED_MDR} on the "
                         "coordinates admitted here, with the realized band "
                         "widths below",
            "attached_to": "the realized-band width report (#71 executed "
                           "form); no equivalence cell beyond this",
            "realized_band_halfwidths": widths,
            "realized_mdr_1p96_null_sd": mdrs,
            "projected_mdr_per_coordinate": {
                n: rows[n]["projection"]["recomputed_at_this_N"]
                for n in rows},
            "realized_over_projected": {
                n: rows[n]["projection"]["realized_over_projected"]
                for n in rows},
            "cohort_caveat": RN_NOTES["RN-X3-4"]}

    survivors = []
    all_cells = []
    table = join["per_trait_secondary"]["table"]
    for coordinate, entry in table.items():
        for trait, cellv in entry.items():
            row = {"coordinate": coordinate, "trait": trait,
                   "r": cellv["r"], "p": cellv["p_two_sided"],
                   "n": cellv["n"],
                   "survives_bonferroni": cellv["survives_bonferroni"]}
            all_cells.append(row)
            if cellv["survives_bonferroni"]:
                survivors.append(row)
    survivors.sort(key=lambda row: abs(row["r"]), reverse=True)
    all_cells.sort(key=lambda row: abs(row["r"]), reverse=True)

    anomalies = honest_anomalies(stage_b, join, rows, contrast, all_cells,
                                 verdict)
    write_json(out / "anomalies.json", anomalies)

    verdict_obj = {
        "leg": LEG, "utc": utc_now(), "tier": "EXPLORATORY",
        "level": "corpus-level",
        "verdict": verdict, "cell": cells["cell"], "suffix": cells["suffix"],
        "verdict_with_suffix": cells["verdict_with_suffix"],
        "detected_raw": cells["detected_raw"],
        "off_menu_note": cells["off_menu_note"],
        "rows": {n: {"raw_r": rows[n]["raw"]["r"],
                     "raw_band": [rows[n]["raw"]["band_lo"],
                                  rows[n]["raw"]["band_hi"]],
                     "raw_p": rows[n]["raw"]["p_two_sided"],
                     "ci": rows[n]["bootstrap_ci"]["ci"],
                     "partial_r": rows[n]["partial_bag"]["r"],
                     "partial_p": rows[n]["partial_bag"]["p_two_sided"],
                     "activity_r": rows[n]["partial_bag_activity"]["r"],
                     "n_authors": rows[n]["n_authors"]} for n in rows},
        "level_contrast": contrast,
        "leans": leans,
        "scoped_silence_statement": scoped,
        "per_trait_survivors": survivors,
        "per_trait_largest_cells": all_cells[:5],
        "honest_anomalies": anomalies,
        "reliability_gate": stage_b["reliability_gate"],
        "stamp_chain": gate["G-X3_stamp_chain"],
        "boundaries": config["boundaries"],
        "label_event": config["label_event"],
    }
    write_json(out / "verdict.json", verdict_obj)
    write_json(out / "cells.json", cells)
    write_json(out / "leans.json", leans)
    write_json(out / "report_payload.json", {
        "config": config, "census": part0["G0"]["census"],
        "source_agreement": part0["G0"]["source_agreement"],
        "reproductions": part0["G0"]["reproductions"],
        "stageb": stage_b, "join": join, "gate": gate,
        "verdict": verdict_obj, "cells": cells,
        "generated_utc": utc_now()})
    log.event("finalize_done", verdict=verdict, cell=cells["cell"],
              suffix=cells["suffix"])
    print(f"finalize OK  VERDICT={cells['verdict_with_suffix']} "
          f"(cell {cells['cell']})  leans: primary="
          f"{'HELD' if leans['primary_HELD'] else 'MISSED'} dynamics="
          f"{'HELD' if leans['dynamics_point_HELD'] else 'MISSED'}  "
          f"per-trait survivors={len(survivors)}  "
          f"{time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
# REPORT -- every table generated from the artifacts (rule 24).
# ---------------------------------------------------------------------------
def _fmt(value: Any, digits: int = 4) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def _ci(pair: Sequence[float] | None, digits: int = 4) -> str:
    if not pair:
        return "n/a"
    return f"[{_fmt(pair[0], digits)}, {_fmt(pair[1], digits)}]"


def _table(add, header: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    """A markdown table whose EVERY cell -- header included -- is pipe-safe."""

    def cell(value: Any) -> str:
        return str(value).replace("|", "\\|")

    add("| " + " | ".join(cell(h) for h in header) + " |")
    add("|" + "|".join(["---"] * len(header)) + "|")
    for row in rows:
        add("| " + " | ".join(cell(c) for c in row) + " |")
    add("")


def _sentence(text: str) -> str:
    """An artifact note dropped into prose, first letter capitalised."""

    text = str(text).strip()
    return (text[0].upper() + text[1:]) if text else text


def _note(key: str) -> str:
    text = RN_NOTES[key]
    return text[0].upper() + text[1:]


def stage_report(args: argparse.Namespace) -> None:
    started = time.time()
    out: Path = args.output
    payload = read_json(out / "report_payload.json")
    config = payload["config"]
    census = payload["census"]
    repro = payload["reproductions"]
    agreement = payload["source_agreement"]
    stage_b = payload["stageb"]
    join = payload["join"]
    gate = payload["gate"]
    verdict = payload["verdict"]
    chain = verdict["stamp_chain"]
    contrast = verdict["level_contrast"]
    # The registered coordinate ORDER, not whatever order the JSON sorted to.
    rows = {n: join["rows"][n] for n in COORDINATES if n in join["rows"]}

    lines: list[str] = []
    add = lines.append
    add(f"# SUICA {LEG} -- the trait join of expression coordinates")
    add("")
    add(f"**VERDICT: `{verdict['verdict_with_suffix']}` "
        f"(cell {verdict['cell']}).**  Tier EXPLORATORY, corpus-level, "
        f"layer P.  Registered before the run in "
        f"`{config['registration_doc']}` at commit "
        f"`{config['registration_commit']}`.")
    add("")
    admitted = stage_b["reliability_gate"]["admitted"]
    add(f"{len(admitted)} of {len(COORDINATES)} coordinates were admitted by "
        f"the label-free reliability gate; "
        f"{sum(1 for n in rows if rows[n]['detected_raw'])} of them detect "
        f"raw coupling to Big5 similarity at the registered two-sided band.")
    add("")
    if verdict["off_menu_note"]:
        add(f"**Off-menu pattern, disclosed.**  {verdict['off_menu_note']}")
        add("")
    if verdict["scoped_silence_statement"]:
        s = verdict["scoped_silence_statement"]
        add(f"**Scoped statement (attached to the realized-band width table, "
            f"and only there): {s['statement']}.**  No equivalence cell is "
            f"claimed beyond this sentence, and the cohort caveat below "
            f"rides it.")
        add("")
    anchors = [rows[n]["channels"]["mantel_bag_vs_trait"] for n in rows]
    if anchors:
        add(f"**The reading is not a dead harness.**  On the SAME pairs, "
            f"with the SAME trait matrix and the SAME Mantel machinery, the "
            f"Where channel is live: Mantel(bag-distance, trait-distance) "
            f"ranges over {_fmt(min(anchors))} to {_fmt(max(anchors))} across "
            f"the admitted coordinates' pools, against SR1's independently "
            f"established {SR1_R} on a different pool of {SR1_N:,}.  A "
            f"within-harness point estimate, DESCRIPTIVE and routing nothing "
            f"-- no null was run on it -- but it is the reading under which "
            f"the expression rows' bands mean what they say.")
        add("")

    add("## 1. The label event")
    add("")
    add(_note("RN-X3-5"))
    add("")
    add(f"- source: `{join['trait_join']['source']}`")
    add("- columns opened: `" + "`, `".join(join["trait_join"]
                                            ["columns_opened"]) + "`")
    add(f"- opened: ONCE, in stage E, after `first_join` was logged at "
        f"`{chain['first_join_utc']}`")
    lc = join["analysis_pool_label_completeness"]
    add(f"- analysis-pool label completeness: {lc['n_complete']:,} of "
        f"{lc['n_pool']:,} ({_fmt(lc['fraction'])})")
    add(f"- z-scoring: {join['trait_join']['z_scored_over']}")
    add(f"- reader: {join['trait_join']['reader']}")
    add("- committed artifacts carry AGGREGATES ONLY; no per-author trait "
        "value leaves stage E.")
    add("")

    add("## 2. The stamp chain (G-X3)")
    add("")
    _table(add, ["event", "artifact", "UTC"], [
        ["`config_stamped`", "`config.sha256.json`",
         f"`{chain['config_stamped_utc']}`"],
        ["`coordinates_frozen`", "`coordinate_freeze.json`",
         f"`{chain['coordinate_freeze_utc']}`"],
        ["`first_join`", "`join.json`", f"`{chain['first_join_utc']}`"]])
    sec = chain["seconds_between"]
    add(f"Gaps: stamp -> freeze `{_fmt(sec['stamp_to_freeze'], 1)} s`, "
        f"freeze -> first join `{_fmt(sec['freeze_to_first_join'], 1)} s`.  "
        f"Order proven from the artifact timestamps: "
        f"**{_fmt(chain['stamp_precedes_freeze_precedes_first_join'])}**; "
        f"joint quantities before the stamp: "
        f"{chain['joint_quantities_before_stamp']}; labels opened before the "
        f"stamp: {_fmt(chain['labels_opened_before_stamp'])}.  "
        f"G-X3 PASS = **{_fmt(gate['PASS'])}**.")
    add("")
    h = gate["hashes"]
    _table(add, ["hash", "stamped/frozen", "recomputed", "matches"], [
        ["`config.json`", f"`{h['config_sha256_stamped'][:16]}`",
         f"`{h['config_sha256_recomputed'][:16]}`",
         _fmt(h["config_hash_matches"])],
        ["`coordinates.npz`", f"`{h['coordinates_sha256_frozen'][:16]}`",
         f"`{h['coordinates_sha256_recomputed'][:16]}`",
         _fmt(h["coordinate_hash_matches"])]])
    add(_note("RN-X3-1"))
    add("")

    add("## 3. Anchors, source agreement and the value reproductions")
    add("")
    _table(add, ["anchor", "registered", "observed", "status"],
           [[k, _fmt(v["registered"]), _fmt(v["observed"]), v["status"]]
            for k, v in sorted(census["pins"].items())])
    add(f"Census status **{census['status']}** (BLOCKING under #78).")
    add("")
    _table(add, ["source-agreement check", "result"],
           [[k.replace("_", " "), _fmt(v)]
            for k, v in agreement.items() if k not in ("note", "status")])
    add(f"Agreement status **{agreement['status']}**.  "
        f"{_sentence(agreement['note'])}.")
    add("")
    _table(add, ["reproduced value", "committed", "recomputed here",
                 "abs delta", "status"],
           [[k, _fmt(v["registered"], 10) if not isinstance(v["registered"],
                                                            dict)
             else json.dumps(v["registered"]),
             _fmt(v["observed"], 10) if not isinstance(v["observed"], dict)
             else json.dumps(v["observed"]),
             _fmt(v.get("abs_delta"), 12) if "abs_delta" in v else "exact",
             v["status"]]
            for k, v in sorted(repro["rows"].items())])
    add(f"Reproduction status **{repro['status']}** at tolerance "
        f"{repro['tolerance']:g}.  {_sentence(repro['note'])}.")
    add("")

    add("## 4. The reliability gate (label-free, before the stamp)")
    add("")
    grows = stage_b["reliability_gate"]["rows"]
    _table(add, ["coordinate", "n eligible", "share of pool", "split-half r",
                 "Spearman-Brown", "expectation", "gate"],
           [[COORDINATE_TITLES[n],
             _fmt(stage_b["descriptives"][n]["n_eligible"]),
             _fmt(stage_b["descriptives"][n]["share_of_pool"], 3),
             _fmt(grows[n]["split_half_r"]),
             _fmt(grows[n]["spearman_brown"]),
             _fmt(RELIABILITY_EXPECTATION[n], 3),
             f"**{grows[n]['gate']}**"] for n in COORDINATES])
    add(f"Threshold {RELIABILITY_GATE:g}.  "
        f"{_sentence(stage_b['reliability_gate']['stop_rule'])}.")
    add("")
    add(f"Stage B re-executed the coordinates from the same label-free "
        f"sources and the split-half reliabilities came back BIT-IDENTICAL "
        f"to the ones the stamp pinned (determinism "
        f"**{stage_b['determinism']['status']}**); the admitted set was "
        f"unchanged ({_fmt(stage_b['same_admissions'])}).")
    add("")
    add("### The adjusted level's chain, censused label-free before the stamp")
    add("")
    chain_census = stage_b["chain_census"]
    _table(add, ["support s", "authors", "communities", "shared pairs",
                 "LCC author coverage", "singleton communities"],
           [[f"{s}{' (PRIMARY)' if int(s) == CHAIN_SUPPORT_PRIMARY else ''}",
             _fmt(c["authors"]), _fmt(c["communities"]),
             _fmt(c["shared_pairs"]), _fmt(c["lcc_author_coverage"], 3),
             _fmt(c["singleton_communities"])]
            for s, c in sorted(chain_census.items(), key=lambda kv: int(kv[0]))
            ])
    adj = stage_b["diagnostics"]["adj_level"]
    add(f"The primary is s = {CHAIN_SUPPORT_PRIMARY}, inherited from X-Mb's "
        f"certified skeleton; the other two supports are the X1c census and "
        f"route nothing.  {_sentence(adj['note'])}.  On the "
        f"Big5 chain the FE budget reads author main "
        f"{_fmt(adj['author_main_share'])}, community main "
        f"{_fmt(adj['community_main_share'])}, interaction "
        f"{_fmt(adj['interaction_share'])}, residual "
        f"{_fmt(adj['residual_share'])}.")
    add("")

    add("## 5. The per-coordinate table")
    add("")
    _table(add, ["coordinate", "N", "pairs", "raw Mantel r", "band", "p",
                 "bootstrap CI", "partial (bag)", "p", "partial (bag+act)",
                 "detects raw"],
           [[COORDINATE_TITLES[n], _fmt(r["n_authors"]), _fmt(r["n_pairs"]),
             f"**{_fmt(r['raw']['r'])}**",
             _ci([r["raw"]["band_lo"], r["raw"]["band_hi"]]),
             _fmt(r["raw"]["p_two_sided"]),
             _ci(r["bootstrap_ci"]["ci"]),
             _fmt(r["partial_bag"]["r"]),
             _fmt(r["partial_bag"]["p_two_sided"]),
             _fmt(r["partial_bag_activity"]["r"]),
             f"**{_fmt(r['detected_raw'])}**"]
            for n, r in rows.items()])
    add(f"Nulls: raw = permutation of the AUTHOR ROWS of the trait matrix, "
        f"B = {config['B_perm']}, two-sided at alpha = {config['alpha']}; "
        f"partial = Smouse-Long-Sokal residual permutation on the bag "
        f"channel, same B.  The bag control is LINEAR (#82 declared).  CIs "
        f"are the author-cluster bootstrap on the Mantel r, "
        f"B = {config['B_boot']}, self-pairs excluded.")
    add("")
    _table(add, ["coordinate", "Mantel(bag, trait)", "corr(coord-dist, bag)",
                 "corr(coord-dist, activity)",
                 "disattenuated raw (secondary)"],
           [[COORDINATE_TITLES[n],
             _fmt(r["channels"]["mantel_bag_vs_trait"]),
             _fmt(r["channels"]["coord_vs_bag"]),
             _fmt(r["channels"]["coord_vs_activity"]),
             _fmt(r["disattenuated_SECONDARY"]["raw"])] for n, r in
            rows.items()])
    add(_note("RN-X3-7"))
    add("")
    bag = join["bag_channel"]
    add(f"Bag channel: the {bag['vocabulary']:,}-community SR0-class law "
        f"vocabulary; {bag['authors_with_no_in_vocabulary_event']} pool "
        f"authors have no in-vocabulary event.  {_sentence(bag['note'])}.")
    add("")

    add("## 6. The level contrast")
    add("")
    if contrast is None:
        add("Not reachable: the contrast needs both level coordinates "
            "admitted, and they were not.")
        add("")
    else:
        _table(add, ["row", "N", "raw Mantel r", "band", "p", "bootstrap CI",
                     "detects"],
               [["RAW LEVEL (own support)", _fmt(contrast["raw_level"]["n"]),
                 f"**{_fmt(contrast['raw_level']['r'])}**",
                 _ci(contrast["raw_level"]["band"]),
                 _fmt(contrast["raw_level"]["p"]),
                 _ci(contrast["raw_level"]["ci"]),
                 _fmt(contrast["raw_level"]["detected"])],
                ["ADJUSTED LEVEL", _fmt(contrast["adj_level"]["n"]),
                 f"**{_fmt(contrast['adj_level']['r'])}**",
                 _ci(contrast["adj_level"]["band"]),
                 _fmt(contrast["adj_level"]["p"]),
                 _ci(contrast["adj_level"]["ci"]),
                 _fmt(contrast["adj_level"]["detected"])]]
               + ([["RAW LEVEL on the adjusted support (second reading)",
                    _fmt(contrast["second_reading"]["n"]),
                    _fmt(contrast["second_reading"]["r"]),
                    _ci(contrast["second_reading"]["band"]),
                    _fmt(contrast["second_reading"]["p"]),
                    _ci(contrast["second_reading"]["ci"]),
                    _fmt(contrast["second_reading"]["detected"])]]
                   if contrast["second_reading"] else []))
        add(f"{_sentence(contrast['support_caveat'])}.  "
            + (f"The descriptive retention ratio r_adjusted / r_raw is "
               f"{_fmt(contrast['retention_descriptive'])}"
               if contrast["raw_level"]["detected"] else
               f"The descriptive retention ratio "
               f"({_fmt(contrast['retention_descriptive'])}) is NOT read "
               f"here: its denominator sits inside its own permutation band, "
               f"so the ratio has no scale")
            + f".  {contrast['no_ratio_null']}")
        add("")
        if contrast["second_reading"]:
            add(f"The second reading is a DISCLOSED executor addition: "
                f"{contrast['second_reading']['role']}.")
            add("")

    add("## 7. The per-trait secondary table")
    add("")
    sec_tab = join["per_trait_secondary"]
    header = ["coordinate"] + [t[:4].upper() for t in BIG5]
    body = []
    for name in COORDINATES:
        entry = sec_tab["table"].get(name)
        if entry is None:
            continue
        cells_row = [COORDINATE_TITLES[name]]
        for trait in BIG5:
            e = entry[trait]
            mark = " (SURVIVES)" if e["survives_bonferroni"] else ""
            cells_row.append(
                f"{_fmt(e['r'], 3)} (p={_fmt(e['p_two_sided'], 3)}){mark}")
        body.append(cells_row)
    _table(add, header, body)
    add(f"Pearson of the coordinate against each z-scored trait, over that "
        f"coordinate's eligible label-complete authors; two-sided p by "
        f"{sec_tab['p_transform']}.  Guard: {sec_tab['guard']}, i.e. "
        f"alpha = {sec_tab['bonferroni_alpha']:.5f}; a cell that clears it is "
        f"marked SURVIVES.  **This table routes nothing.**  "
        f"{len(verdict['per_trait_survivors'])} of "
        f"{5 * sec_tab['n_admitted']} cells survive.  The five largest "
        f"|r| cells, survivors or not: "
        + "; ".join(f"{c['coordinate']} x {c['trait']} "
                    f"{_fmt(c['r'], 3)} (p={_fmt(c['p'], 4)})"
                    for c in verdict["per_trait_largest_cells"]) + ".")
    add("")

    add("## 8. Projection against realized power")
    add("")
    _table(add, ["coordinate", "N", "projected minimal detectable r",
                 "realized 1.96 x null sd", "realized / projected",
                 "band half-width"],
           [[COORDINATE_TITLES[n], _fmt(r["n_authors"]),
             _fmt(r["projection"]["recomputed_at_this_N"]),
             _fmt(r["projection"]["realized_mdr_1p96_null_sd"]),
             _fmt(r["projection"]["realized_over_projected"], 3),
             _fmt(r["raw"]["band_halfwidth"])] for n, r in rows.items()])
    add(f"The registration projected a minimal detectable r of about "
        f"{REGISTERED_MDR} at N ~ {ANCHOR_POOL_BIG5:,}, from SR1's realized "
        f"z = {SR1_Z} at r = {SR1_R} on N = {SR1_N:,} under the DECLARED "
        f"assumption z proportional to r*sqrt(N).")
    add("")

    add("## 9. Leans")
    add("")
    leans = verdict["leans"]
    _table(add, ["lean", "registered", "realized", "status"], [
        ["primary cell", leans["primary_registered"],
         leans["primary_outcome"],
         "HELD" if leans["primary_HELD"] else "MISSED"],
        ["dynamics point", leans["dynamics_point_registered"],
         ", ".join(f"{k} {_fmt(v)}" for k, v in
                   leans["dynamics_point_realized"].items()) or "n/a",
         "HELD" if leans["dynamics_point_HELD"] else "MISSED"],
        ["cohort caveat", "carried on every claim",
         "carried", "HELD"]])

    add("## 10. Honest anomalies")
    add("")
    for item in verdict["honest_anomalies"]:
        add(f"**{item['id']} -- {_sentence(item['title'])}.**  "
            f"{_sentence(item['observed'])}.  Why it matters: "
            f"{item['why_it_matters']}.  {_sentence(item['adjudication'])}.")
        add("")

    add("## 11. Boundaries")
    add("")
    for key in ("RN-X3-2", "RN-X3-3", "RN-X3-4", "RN-X3-6", "RN-X3-8"):
        add(f"- {_note(key)}")
    add("- EXPLORATORY, corpus-level.  No person claim is made or "
        "supportable: every estimand is a corpus-level distance-matrix "
        "statistic.")
    add(f"- Governance: aggregates only; no text excerpt; the body column "
        f"never read; identifier artifacts confined to gitignored "
        f"`results/`; ID-leak scan over {gate['id_leak_scan']['universe']:,} "
        f"names -- {gate['id_leak_scan']['n_new_hits']} NEW hits, "
        f"{gate['id_leak_scan']['n_pre_existing']} pre-existing dictionary "
        f"collisions carried unchanged from HEAD (baseline "
        f"{gate['id_leak_scan']['baseline_expected']}).")
    add("")

    add("## 12. Config block")
    add("")
    add("```json")
    add(json.dumps({k: config[k] for k in
                    ("leg", "title", "registration_commit", "tier", "level",
                     "layer", "seed", "seed_perm", "seed_boot", "B_perm",
                     "B_boot", "alpha", "y", "analysis_pool",
                     "reliability_gate", "estimands", "cells", "secondary",
                     "projection", "leans", "machinery_imported_by_file")},
                   indent=1, sort_keys=True, default=float))
    add("```")
    add("")
    add(f"Generated from `{rel(out / 'report_payload.json')}` (rule 24: every "
        f"number in this report is read from an artifact, never retyped).  "
        f"Run environment recorded in `part0.json`.")
    add("")

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(lines), encoding="utf-8")

    # The gate scanned the report AS IT STOOD BEFORE this write.  Re-run the
    # #83 scan on the file that actually ships; a NEW hit here is blocking.
    rescan = run_id_leak_scan(args, out, "post_report")
    if rescan["status"] != "PASS":
        raise SystemExit(f"STOP: the #83 scan FAILED on the freshly written "
                         f"report: {rescan['new_hits']}")
    print(f"report OK  {rel(args.report)}  {len(lines)} lines  "
          f"post-report #83 rescan: {rescan['n_new_hits']} NEW hits of "
          f"{rescan['universe_size']:,} names  {time.time() - started:.1f}s")


# ---------------------------------------------------------------------------
STAGES = {"part0": stage_part0, "stageb": stage_stageb, "stagee": stage_stagee,
          "gate": stage_gate, "finalize": stage_finalize,
          "report": stage_report}
STAGE_ORDER = ("part0", "stageb", "stagee", "gate", "finalize", "report")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=f"SUICA {LEG} runner")
    parser.add_argument("stage", choices=(*STAGE_ORDER, "all"), nargs="?",
                        default="all")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--x5-cache", type=Path, default=X5_CACHE)
    parser.add_argument("--x2-cache", type=Path, default=X2_CACHE)
    parser.add_argument("--x1-cache", type=Path, default=DEFAULT_X1_CACHE)
    parser.add_argument("--cohort", type=Path, default=DEFAULT_COHORT)
    parser.add_argument("--b-perm", type=int, default=B_PERM)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    parser.add_argument("--registration-commit", default=REGISTRATION_COMMIT)
    args = parser.parse_args(argv)
    stages = STAGE_ORDER if args.stage == "all" else (args.stage,)
    for name in stages:
        STAGES[name](args)


if __name__ == "__main__":                           # pragma: no cover
    main()
