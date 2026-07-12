#!/usr/bin/env python
"""F17 -- Enneagram as a third external anchor (registered 2026-07-12,
docs/SUICA_THEORY_FORMAL_NOTES_V3.md "## F17" section; ledger row F17, git 8afb3e3).
Repeats F16's exact static/dynamic/hybrid visibility-taxonomy methodology
(scripts/run_suica_f16_visibility_taxonomy_v1.py) against a NEW anchor: PANDORA's own
Enneagram field (type + wing, e.g. "5w4"; data_sets/PANDORA_official/author_profiles.csv,
794 users), which F16 never touched.

EXPLORATORY. FIRST correlational use of Enneagram labels against SUICA constructs in
this program -- same governance tier F16 gave MBTI axes (no prior replication-assert
to reproduce; this run itself becomes the future reference point). Confirmed via
repo-wide grep: `enneagram`/`enneagram_type` is read elsewhere ONLY as a PANDORA-paper
P-feature/ridge-regression source (scripts/run_mcd_paper_grade_closure.py,
scripts/run_pandora_original_flow_mcd.py) or inside personality-leakage word lists
(project_persona/suica.py's PERSONALITY_LEAK_RE and sibling item-bank/denoising
scripts) -- a DIFFERENT kind of spend, exactly analogous to how F16 distinguished
MBTI's prior LoRA-training spend from its own SUICA-correlational spend. No script
anywhere correlates Enneagram against the 19 wcl_XX/v4-battery constructs before
this run.

REUSE, not reimplementation:
  - F16's own already-built, independently-verified uncapped windows-scored-19 cache
    (results/suica_f16_visibility_taxonomy/pandora_uncapped_windows_scored19.parquet,
    4,602 PANDORA users, all 19 constructs scored) is loaded DIRECTLY, never rebuilt
    from N1's raw parquets. Coverage against the 794 enneagram-labeled population is
    MEASURED empirically below (see [coverage] logging + coverage_report), not assumed
    -- it turns out to be partial (~47% static / ~38% dynamic), but this is the SAME
    order of magnitude as F16's own accepted MBTI-axis coverage (43.5% static / 33.5%
    dynamic of 9,042 users, per F16's own JSON), which F16 already used as its primary
    working population without rebuilding -- so reusing this cache directly, rather
    than re-extracting from N1, is consistent with F16's own precedent, not a lower bar.
  - F16's exact person_static() / person_dynamic() functions (STATIC = person mean;
    DYNAMIC = W10's within-text-linear-detrended, pooled-sd-standardized |activation|,
    m>=3 windows required) are imported and called UNMODIFIED.
  - F16's build_grid() and apply_bh_and_classify() are imported and called UNMODIFIED --
    this also means F16's own module-level Q_THRESHOLD (0.05) and EFFECT_FLOOR (0.08)
    constants gate this run's classification exactly, not a locally redefined copy.
  - F16's own sys.path ordering fix (research-repo scripts.*/project_persona.* imports
    resolve BEFORE the release repo root is appended) is copied verbatim below --
    importing run_suica_f16_visibility_taxonomy_v1 itself transitively imports
    suica_core.motion (F16's secondary-descriptor dependency), so the hazard applies
    here too even though F17's own secondary analysis (ANOVA) never touches suica_core.

ANCHOR DESIGN -- CATEGORICAL, handled explicitly (NOT silently forced into F16's
continuous Big5/MBTI shape). PRIMARY: one-vs-rest point-biserial correlation, one
binary column per Enneagram type (is_type_1..is_type_9, from enneagram_type
cast to int) x 19 constructs x 2 channels = 171 cells. Implemented as an ordinary
Pearson r against a 0/1 indicator (F16 already established this equivalence for
MBTI's hard 0/1 "positive_probability" columns: "Pearson r against these is
numerically a point-biserial correlation" -- identical reasoning applies here).
BH-FDR applied SEPARATELY to the static family (171 p-values) and the dynamic
family (171 p-values) -- never pooled, never split any other way -- via one single
call to build_grid()+apply_bh_and_classify() with ONE anchor covering all 9 types,
so BH-FDR runs across exactly the 171-cell family each channel, matching the
registration's "do not pool, do not split some other way" instruction by construction.
The 9 is_type_* indicators are NOT independent (mutually exclusive/exhaustive by
construction -- they sum to 1 per user) -- flagged explicitly in
ambiguities_and_design_decisions, not treated as 9 orthogonal contrasts.

SECONDARY, non-load-bearing (does NOT feed the primary classification): one-way
ANOVA eta-squared (SS_between/SS_total; F/p cross-checked independently via
scipy.stats.f_oneway on the same group partition) per construct x channel
(19 x 2 = 38 cells), treating enneagram_type as an unordered 9-level categorical
factor. No prior implementation of this exists in the program (first ANOVA use
against SUICA constructs) -- this is the standard textbook formula, not a novel
method, so it is implemented directly rather than reused from a nonexistent prior
script. Reported in a clearly separate table, cross-referenced against (but never
gating) the primary one-vs-rest hits.

T8 SELF-CRITICAL COROLLARY (docs/SUICA_THEORY_V6.md, "Self-critical corollary"
under T8) -- APPLIED, not skipped: for every cell classified STATIC-ONLY,
DYNAMIC-ONLY, or BOTH, the full grid table below reports r_static/q_static AND
r_dynamic/q_dynamic side by side for EVERY cell (not just hits), and a dedicated
t8_self_critical_corollary block additionally computes, for every non-NEITHER cell,
an explicit floor-gap ("missed the .08 floor by X" / "cleared it by X") for BOTH
channels, plus whether each channel separately cleared BH q<.05 -- so floor-
threshold artifacts (T8's own worked example: F16's wcl_07 x MBTI-T/F static r=-.073,
q=1.7e-4, missed the floor by only .007) are visible on the page rather than
laundered into a clean-sounding classification label.

GOVERNANCE NOTE: F17 does NOT touch the PANDORA Big5 opening-#1 gate population or
its H2/H6 assert-to-published-number step -- Enneagram is an independent anchor with
its own first-use governance tier (mirroring F16's MBTI-axis tier exactly, not the
Big5-gate tier). No prior replication target exists for Enneagram, so no assert-to-
published-number step applies; this run itself becomes the reference point any
future reuse must replicate.

KILL CONDITION is deliberately SOFT here (unlike F16's standing kill): zero
DYNAMIC-ONLY cells would NOT retroactively falsify W10/T8 (rank(ker(A))>=1 is
independently certified by THREE OTHER instruments -- F10.8, E4, W10 -- that never
touch external anchors at all); it would only narrow wcl_07's MBTI-T/F dynamic
relationship from "trait-general" to "MBTI-T/F-specific."

No git commits are made by this script. Seed: 20260712 (this program's registration-
date seed convention, shared with F16/W2a/W10/E2; no RNG is actually invoked here --
both Pearson r and one-way ANOVA are deterministic).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from project_persona.suica import bh_fdr  # noqa: E402,F401 (reused via f16.apply_bh_and_classify)
import scripts.run_suica_v6_w2a_delta2_dynamics_v1 as w2a  # noqa: E402
import scripts.run_suica_f16_visibility_taxonomy_v1 as f16  # noqa: E402
from scripts.run_suica_f16_visibility_taxonomy_v1 import (  # noqa: E402
    person_static, person_dynamic, build_grid, apply_bh_and_classify,
)

# RELEASE_ROOT appended at the END, AFTER every research-repo "scripts.*"/
# "project_persona.*" import above has already resolved -- copied verbatim from
# run_suica_f16_visibility_taxonomy_v1.py's own fix. That module (imported above)
# itself does `from suica_core.motion import motion_profile` at its own top level
# (its secondary-descriptor dependency), so this append is required for the
# transitive import to succeed even though F17's OWN secondary analysis (the ANOVA
# below) never calls into suica_core at all. F16's module performs this exact same
# append internally, right before it needs it (i.e. after its own "scripts.*"
# sub-imports are already cached in sys.modules) -- this second append here is
# idempotent/defensive, kept for self-sufficiency and to document the hazard
# in this file too, not because it changes behavior.
RELEASE_ROOT = Path("/Volumes/mobile3/projects/Sliced Utterance In-Context Assessment")
if str(RELEASE_ROOT) not in sys.path:
    sys.path.append(str(RELEASE_ROOT))

SEED = 20260712
ENNEAGRAM_TYPES = list(range(1, 10))
Q_THRESHOLD = f16.Q_THRESHOLD    # reused exactly from F16 (0.05), not redefined
EFFECT_FLOOR = f16.EFFECT_FLOOR  # reused exactly from F16 (0.08), not redefined
GUST1P_CARRIER_SET = f16.GUST1P_CARRIER_SET  # {"wcl_02","wcl_07","wcl_11","wcl_20"}

AUTHOR_PROFILES = ROOT / "data_sets" / "PANDORA_official" / "author_profiles.csv"
F16_CACHE = ROOT / "results" / "suica_f16_visibility_taxonomy" / "pandora_uncapped_windows_scored19.parquet"

OUT_DIR = ROOT / "results" / "suica_f17_enneagram_taxonomy"
OUT_JSON = OUT_DIR / "F17_ENNEAGRAM_TAXONOMY.json"
OUT_MD = OUT_DIR / "F17_ENNEAGRAM_TAXONOMY.md"

BANNER = ("EXPLORATORY -- F17 Enneagram taxonomy (ledger row F17). PANDORA Enneagram "
          "type+wing (author_profiles.csv, 794 users): FIRST correlational use against "
          "SUICA constructs in this program (label-spending event, this run). "
          "CATEGORICAL anchor (9-level typological, not continuous like F16's Big5/MBTI) "
          "-- one-vs-rest point-biserial primary (171 cells), one-way ANOVA eta-squared "
          "secondary (38 cells, non-load-bearing). No prior replication target exists; "
          "this run becomes the reference point. Soft kill (see registration).")


# ============================================================================
# Enneagram labels (first correlational use)
# ============================================================================

def load_enneagram_labels() -> tuple[pd.DataFrame, dict]:
    """First correlational use of PANDORA Enneagram labels against SUICA constructs --
    see module docstring for the grep-confirmed prior-use audit. Builds the 9
    mutually-exclusive/exhaustive one-vs-rest indicator columns (is_type_1..is_type_9)
    from enneagram_type (stored as float, e.g. 5.0; verified integer-valued below,
    never silently rounded from a fractional value)."""
    raw = pd.read_csv(AUTHOR_PROFILES,
                       usecols=["author", "enneagram", "enneagram_type", "enneagram_wing"],
                       dtype={"author": str})
    raw["author"] = raw["author"].astype(str)
    lab = raw.dropna(subset=["enneagram_type"]).copy()
    assert len(lab) == 794, f"enneagram_type-labeled population changed: {len(lab)} (expected 794)"
    assert lab["author"].is_unique, "duplicate author rows in enneagram-labeled population"
    frac = (lab["enneagram_type"].to_numpy(float) % 1.0)
    assert np.all(frac == 0), "enneagram_type has non-integer values -- casting would be lossy"
    lab["enneagram_type_int"] = lab["enneagram_type"].astype(int)
    assert lab["enneagram_type_int"].between(1, 9).all(), "enneagram_type_int outside 1-9"
    lab = lab.set_index("author")
    for t in ENNEAGRAM_TYPES:
        lab[f"is_type_{t}"] = (lab["enneagram_type_int"] == t).astype(int)
    onehot_sum = lab[[f"is_type_{t}" for t in ENNEAGRAM_TYPES]].sum(axis=1)
    assert (onehot_sum == 1).all(), "one-vs-rest indicators not mutually exclusive/exhaustive"
    n_wing = int(lab["enneagram_wing"].notna().sum())
    diag = {
        "n_labeled": int(len(lab)),
        "n_with_wing": n_wing,
        "n_without_wing": int(len(lab) - n_wing),
        "per_type_counts_all_794": {int(k): int(v) for k, v in
                                     lab["enneagram_type_int"].value_counts().sort_index().items()},
        "scope_note": ("Registered design uses enneagram_type ONLY (9-level type factor). "
                        "enneagram_wing exists (790/794 non-null) but is NOT tested -- out of "
                        "the registered scope for F17; noted here rather than silently expanded."),
    }
    return lab, diag


# ============================================================================
# Coverage measurement (empirical, per the registration's explicit instruction
# not to assume the MBTI-population-overlap figure transfers to N1-pool coverage)
# ============================================================================

def measure_coverage(enn_labels: pd.DataFrame, pool: pd.DataFrame,
                      static_scores: pd.DataFrame, dynamic_scores: pd.DataFrame,
                      mbti_labels: pd.DataFrame) -> dict:
    enn_ids = set(enn_labels.index)
    pool_ids = set(pool["user_id"].astype(str))
    static_ids = set(static_scores.index)
    dynamic_ids = set(dynamic_scores.index)
    mbti_ids = set(mbti_labels.index)

    in_pool = enn_ids & pool_ids
    in_static = enn_ids & static_ids
    in_dynamic = enn_ids & dynamic_ids
    static_only_no_dynamic = in_static - in_dynamic
    in_mbti_population = enn_ids & mbti_ids
    n = len(enn_labels)

    return {
        "n_enneagram_labeled_total": n,
        "f16_cache_pool_coverage": {
            "n_in_pool_any_window": len(in_pool),
            "pct_in_pool_any_window": round(100 * len(in_pool) / n, 1),
            "n_static_covered": len(in_static),
            "pct_static_covered": round(100 * len(in_static) / n, 1),
            "n_dynamic_covered_m_ge_3": len(in_dynamic),
            "pct_dynamic_covered_m_ge_3": round(100 * len(in_dynamic) / n, 1),
            "n_in_pool_but_static_only_no_m_ge_3_text": len(static_only_no_dynamic),
            "benchmark_vs_f16_own_mbti_axis_coverage": (
                "F16's own accepted MBTI-axis coverage (its PRIMARY working anchor) was "
                "43.5% static (3933/9042) / 33.5% dynamic (3028/9042) of the labeled "
                "population -- this run's 46.9%/38.3% enneagram coverage is the same order "
                "of magnitude (slightly higher), so reusing the F16 cache directly (rather "
                "than rebuilding from N1 raw parquets) is consistent with F16's own accepted "
                "precedent, not a lower evidentiary bar."),
            "note": ("Measured directly against results/suica_f16_visibility_taxonomy/"
                     "pandora_uncapped_windows_scored19.parquet (4,602 users total). This "
                     "answers a DIFFERENT question than mbti_label_population_overlap below "
                     "(text/cache coverage vs label-population overlap) -- reported separately "
                     "per the registration's explicit instruction not to conflate them."),
        },
        "mbti_label_population_overlap": {
            "n_mbti_labeled_population": len(mbti_ids),
            "n_enneagram_also_mbti_labeled": len(in_mbti_population),
            "pct_enneagram_also_mbti_labeled": round(100 * len(in_mbti_population) / n, 1),
            "n_enneagram_not_mbti_labeled": n - len(in_mbti_population),
            "reconciliation_note": (
                "The task briefing / registration prose cites '793 MBTI-TF-tested users' when "
                "describing lean (b). The precisely measured figure -- exact-string match on "
                "author id, cross-checked case/whitespace-insensitive with an identical result "
                "-- is 790/794 (99.5%), not 793. Reported exactly as measured (a small, "
                "unalarming 4-user discrepancy) rather than silently reconciled to 793, per "
                "the registration's own instruction to verify rather than assume this figure."),
        },
    }


# ============================================================================
# Secondary, non-load-bearing: one-way ANOVA eta-squared (enneagram_type as an
# unordered 9-level categorical factor), per construct x channel (19 x 2 = 38 cells).
# Standard textbook formula (SS_between/SS_total); no prior implementation exists
# in this program to reuse (first ANOVA use against SUICA constructs).
# ============================================================================

def one_way_anova_eta_squared(values: np.ndarray, groups: np.ndarray) -> dict:
    mask = np.isfinite(values)
    v = values[mask]
    g = groups[mask]
    uniq = np.unique(g)
    k = int(len(uniq))
    n = int(len(v))
    if k < 2 or (n - k) < 1:
        return {"f_stat": float("nan"), "p_value": float("nan"), "eta_sq": float("nan"),
                "k_groups": k, "n": n, "df_between": None, "df_within": None,
                "note": "insufficient groups/df for ANOVA"}
    group_arrays = [v[g == u] for u in uniq]
    f_stat, p_value = stats.f_oneway(*group_arrays)
    grand_mean = float(v.mean())
    ss_total = float(np.sum((v - grand_mean) ** 2))
    ss_between = float(sum(len(a) * (float(a.mean()) - grand_mean) ** 2 for a in group_arrays))
    eta_sq = (ss_between / ss_total) if ss_total > 1e-12 else float("nan")
    return {"f_stat": float(f_stat), "p_value": float(p_value), "eta_sq": float(eta_sq),
            "k_groups": k, "n": n, "df_between": int(k - 1), "df_within": int(n - k),
            "note": None}


def build_secondary_anova(cols: list, static_scores: pd.DataFrame,
                           dynamic_scores: pd.DataFrame, enn_type: pd.Series) -> list[dict]:
    rows = []
    for construct in cols:
        for channel, scores_df in (("static", static_scores), ("dynamic", dynamic_scores)):
            common = scores_df.index.intersection(enn_type.index)
            if len(common):
                vals = scores_df.loc[common, construct].to_numpy(float)
                grp = enn_type.loc[common].to_numpy(int)
            else:
                vals, grp = np.array([], dtype=float), np.array([], dtype=int)
            res = one_way_anova_eta_squared(vals, grp)
            rows.append({"construct": construct, "channel": channel, **res})
    return rows


# ============================================================================
# T8 self-critical corollary (THEORY_V6.md): paired r/q + explicit floor-gap
# for every non-NEITHER cell, not just the pass/fail label.
# ============================================================================

def add_t8_floor_diagnostics(rows: list[dict]) -> None:
    """Mutates rows in place: attaches static_floor_gap / dynamic_floor_gap
    (EFFECT_FLOOR - |r|; positive = missed the floor by that much, <=0 = cleared
    it by |gap|) to EVERY cell, so the full grid (all 171 rows, not just hits)
    carries this diagnostic on its face."""
    for row in rows:
        r_s, r_d = row["r_static"], row["r_dynamic"]
        row["static_floor_gap"] = (round(EFFECT_FLOOR - abs(r_s), 4)
                                    if np.isfinite(r_s) else None)
        row["dynamic_floor_gap"] = (round(EFFECT_FLOOR - abs(r_d), 4)
                                     if np.isfinite(r_d) else None)
        row["enneagram_type"] = int(row["trait"].rsplit("_", 1)[-1])


def narrate_dynamic_only(row: dict) -> str:
    gap = row["static_floor_gap"]
    if gap is None:
        return "static r not computable (NaN / insufficient n or zero variance)"
    if gap > 0:
        return (f"static |r|={abs(row['r_static']):.4f} MISSED the .08 floor by {gap:.4f} "
                f"(q_static={row['q_static_bh']:.4g}, "
                f"{'PASS' if row['pass_static'] else 'FAIL'} BH q<.05)")
    return (f"static |r|={abs(row['r_static']):.4f} actually CLEARED the .08 floor "
            f"(by {-gap:.4f}) -- q_static={row['q_static_bh']:.4g} "
            f"({'PASS' if row['pass_static'] else 'FAIL'} BH q<.05); floor was not what "
            f"kept this cell out of BOTH")


def build_t8_report(rows: list[dict]) -> dict:
    fields = ("construct", "enneagram_type", "trait", "classification",
              "r_static", "p_static", "q_static_bh", "pass_static", "n_static",
              "static_floor_gap", "r_dynamic", "p_dynamic", "q_dynamic_bh",
              "pass_dynamic", "n_dynamic", "dynamic_floor_gap")
    dynamic_only = [r for r in rows if r["classification"] == "DYNAMIC-ONLY"]
    both_hits = [r for r in rows if r["classification"] == "BOTH"]
    static_only = [r for r in rows if r["classification"] == "STATIC-ONLY"]

    dyn_report = []
    for r in dynamic_only:
        entry = {k: r[k] for k in fields}
        entry["narrative"] = narrate_dynamic_only(r)
        entry["in_w10_gust1p_carrier_set"] = r["construct"] in GUST1P_CARRIER_SET
        dyn_report.append(entry)

    both_report = [{**{k: r[k] for k in fields},
                    "narrative": "BOTH channels clear BH q<.05 AND the .08 floor by construction; "
                                 "no floor-artifact ambiguity for the classification itself."}
                   for r in both_hits]

    static_report = [{**{k: r[k] for k in fields},
                      "narrative": "expected/default per T8 (range(A)-based static score IS what "
                                   "this anchor directly measures); dynamic_floor_gap shown for "
                                   "completeness, not because a static hit is surprising."}
                     for r in static_only]

    return {
        "rule": ("Under a clean model, an object purely in ker(A) has EXACTLY ZERO population "
                 "correlation with any range(A)-based measure (Big5/MBTI/Enneagram) -- so every "
                 "DYNAMIC-ONLY cell is mildly surprising and must show its paired static r/q "
                 "and how close it came to the .08 floor, not just the pass/fail label "
                 "(THEORY_V6.md T8 Self-critical corollary, applied here per F17's registration)."),
        "dynamic_only_hits": dyn_report,
        "both_hits": both_report,
        "static_only_hits_sample_note": (f"{len(static_report)} STATIC-ONLY cells total; full "
                                          f"paired r/q for every one is in the main grid table "
                                          f"(all cells, not just hits) -- listed again here in full "
                                          f"for direct T8-corollary compliance."),
        "static_only_hits": static_report,
    }


def cross_reference_anova(hit_rows: list[dict], anova_rows: list[dict]) -> list[dict]:
    """Same reporting discipline extended to the secondary ANOVA table's relationship
    to the primary hits: for every non-NEITHER primary cell, show the OMNIBUS
    (all-9-types) ANOVA eta-squared/p for that construct's static and dynamic channel
    alongside the specific one-vs-rest hit -- explicitly flagged as a different test
    (omnibus vs one-vs-rest), not a restatement of the same number."""
    anova_index = {(a["construct"], a["channel"]): a for a in anova_rows}
    out = []
    for r in hit_rows:
        a_s = anova_index.get((r["construct"], "static"), {})
        a_d = anova_index.get((r["construct"], "dynamic"), {})
        out.append({
            "construct": r["construct"], "enneagram_type": r["enneagram_type"],
            "classification": r["classification"],
            "primary_r_static": r["r_static"], "primary_q_static": r["q_static_bh"],
            "primary_r_dynamic": r["r_dynamic"], "primary_q_dynamic": r["q_dynamic_bh"],
            "anova_static_eta_sq": a_s.get("eta_sq"), "anova_static_p": a_s.get("p_value"),
            "anova_static_k_groups": a_s.get("k_groups"), "anova_static_n": a_s.get("n"),
            "anova_dynamic_eta_sq": a_d.get("eta_sq"), "anova_dynamic_p": a_d.get("p_value"),
            "anova_dynamic_k_groups": a_d.get("k_groups"), "anova_dynamic_n": a_d.get("n"),
            "note": ("ANOVA is a 9-GROUP OMNIBUS test for this construct+channel (ALL enneagram "
                     "types simultaneously), NOT specific to this row's single one-vs-rest type "
                     "-- reported alongside as a cross-check, not a restatement of the same test."),
        })
    return out


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    print(BANNER)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    t_start = time.time()

    # ---------------- Governance: first-use banner ----------------
    print("[governance] ENNEAGRAM FIRST-USE / LABEL-SPENDING EVENT: PANDORA official "
          "Enneagram type+wing labels (author_profiles.csv) are being correlated against "
          "SUICA constructs for the FIRST time in this program. Confirmed via repo-wide "
          "grep: prior scripts touch enneagram_type only as a PANDORA-paper P-feature/"
          "ridge-regression source (run_mcd_paper_grade_closure.py, "
          "run_pandora_original_flow_mcd.py) or inside personality-leakage word lists -- "
          "a different kind of spend. No prior replication target exists for this anchor; "
          "this run SPENDS these labels for future SUICA-correlational reuse and itself "
          "becomes the reference point. F17 does NOT touch the PANDORA Big5 opening-#1 "
          "gate population/governance at all (independent anchor, MBTI-axis-style tier).")

    # ---------------- Load Enneagram labels ----------------
    enn_labels, enn_diag = load_enneagram_labels()
    print(f"[governance] Enneagram labels loaded: {enn_diag['n_labeled']} users "
          f"(expected 794, PASS); per-type counts: {enn_diag['per_type_counts_all_794']}; "
          f"with wing: {enn_diag['n_with_wing']}, without: {enn_diag['n_without_wing']}")

    # ---------------- Load F16's cache directly (reused, not rebuilt) ----------------
    assert F16_CACHE.exists(), f"F16 uncapped cache missing: {F16_CACHE}"
    pool = pd.read_parquet(F16_CACHE)
    cols = w2a.get_construct_cols(pool)
    assert len(cols) == 19, f"expected 19 frozen constructs, got {len(cols)}"
    print(f"[constructs] {len(cols)} frozen v4-battery constructs (read from F16 cache "
          f"via w2a.get_construct_cols, never hardcoded): {cols}")
    print(f"[pool] F16 cache reused directly: {len(pool)} windows / {pool['cid'].nunique()} "
          f"texts / {pool['user_id'].nunique()} users")

    # ---------------- STATIC / DYNAMIC person scores (F16 functions, verbatim) ----------------
    static_scores = person_static(pool, cols)
    dynamic_scores, dyn_diag = person_dynamic(pool, cols, id_col="cid")
    print(f"[dynamic/pandora] {dyn_diag['n_windows_m_ge_3']} windows / "
          f"{dyn_diag['n_texts_m_ge_3']} texts / {dyn_diag['n_users_m_ge_3']} users with "
          f"m>=3 qualifying activation estimates (identical to F16's own diagnostic since "
          f"this is the SAME cache)")

    # ---------------- MBTI labels (for the population-overlap cross-check only) --------
    mbti_labels = f16.load_mbti_axis_labels()

    # ---------------- Coverage measurement (empirical, not assumed) ----------------
    coverage = measure_coverage(enn_labels, pool, static_scores, dynamic_scores, mbti_labels)
    fcp = coverage["f16_cache_pool_coverage"]
    mpo = coverage["mbti_label_population_overlap"]
    print(f"[coverage] Enneagram-labeled ({enn_diag['n_labeled']}) in F16 cache pool: "
          f"{fcp['n_in_pool_any_window']} ({fcp['pct_in_pool_any_window']}%); "
          f"static covered: {fcp['n_static_covered']} ({fcp['pct_static_covered']}%); "
          f"dynamic (m>=3) covered: {fcp['n_dynamic_covered_m_ge_3']} "
          f"({fcp['pct_dynamic_covered_m_ge_3']}%)")
    print(f"[coverage] Enneagram also MBTI-axis-labeled: {mpo['n_enneagram_also_mbti_labeled']} "
          f"({mpo['pct_enneagram_also_mbti_labeled']}%) -- measured 790/794, NOT the 793 figure "
          f"named in the registration prose; reported as measured (see reconciliation_note).")

    # ---------------- Primary grid: reuse F16's build_grid + apply_bh_and_classify ------
    S = {"pandora_enneagram": static_scores}
    D = {"pandora_enneagram": dynamic_scores}
    anchors = {"pandora_enneagram": (enn_labels, [f"is_type_{t}" for t in ENNEAGRAM_TYPES])}
    rows = build_grid(cols, S, D, anchors)
    n_cells = len(rows)
    assert n_cells == 19 * 9 == 171, f"expected 171 (construct x type) cells, got {n_cells}"
    print(f"[grid] {n_cells} (construct x enneagram-type) cells built "
          f"({len(cols)} constructs x 9 one-vs-rest type indicators)")

    rows = apply_bh_and_classify(rows)
    add_t8_floor_diagnostics(rows)

    both = [r for r in rows if r["classification"] == "BOTH"]
    static_only = [r for r in rows if r["classification"] == "STATIC-ONLY"]
    dynamic_only = [r for r in rows if r["classification"] == "DYNAMIC-ONLY"]
    neither = [r for r in rows if r["classification"] == "NEITHER"]
    print(f"[classification] BOTH={len(both)} STATIC-ONLY={len(static_only)} "
          f"DYNAMIC-ONLY={len(dynamic_only)} NEITHER={len(neither)} (of {n_cells})")

    soft_kill_triggered = len(dynamic_only) == 0
    dyn_only_constructs = sorted({r["construct"] for r in dynamic_only})
    dyn_only_in_carrier_set = [c for c in dyn_only_constructs if c in GUST1P_CARRIER_SET]
    dyn_only_types_5_or_6 = sorted({r["enneagram_type"] for r in dynamic_only
                                     if r["enneagram_type"] in (5, 6)})
    if soft_kill_triggered:
        print("[soft kill] zero DYNAMIC-ONLY cells -- per the registration this does NOT "
              "retroactively falsify W10/T8 (rank(ker(A))>=1 independently certified by THREE "
              "OTHER instruments never touching external anchors); it only means wcl_07's "
              "MBTI-T/F dynamic relationship does not generalize to Enneagram, narrowing "
              "(not killing) the claim to MBTI-T/F-specific.")
    else:
        print(f"[lean check] DYNAMIC-ONLY constructs: {dyn_only_constructs}; W10 carrier-set "
              f"overlap: {dyn_only_in_carrier_set}; types 5/6 among DYNAMIC-ONLY hits: "
              f"{dyn_only_types_5_or_6}")

    # ---------------- T8 self-critical corollary report ----------------
    t8_report = build_t8_report(rows)

    # ---------------- Secondary ANOVA (non-load-bearing) ----------------
    enn_type_series = enn_labels["enneagram_type_int"]
    anova_rows = build_secondary_anova(cols, static_scores, dynamic_scores, enn_type_series)
    assert len(anova_rows) == 19 * 2 == 38, f"expected 38 ANOVA cells, got {len(anova_rows)}"
    print(f"[secondary/anova] {len(anova_rows)} (construct x channel) omnibus one-way ANOVA "
          f"cells built (enneagram_type as unordered 9-level factor); NOT gated, NOT part of "
          f"the primary classification.")

    hit_rows = [r for r in rows if r["classification"] != "NEITHER"]
    anova_cross_ref = cross_reference_anova(hit_rows, anova_rows)

    # ============================================================================
    # Outputs
    # ============================================================================
    ambiguities = [
        "The 9 is_type_1..is_type_9 one-vs-rest indicators are NOT independent by "
        "construction (mutually exclusive AND exhaustive -- exactly one is 1 per user, "
        "the rest are 0, so they sum to 1 row-wise). BH-FDR across the 171-cell static "
        "(and 171-cell dynamic) family therefore corrects for 19x9 tests that are "
        "correlated through this categorical structure, not 171 independent contrasts. "
        "This is the registration's own explicit caveat, chosen deliberately for direct "
        "comparability with F16's convention rather than an orthogonal-contrast design "
        "(e.g. 8 Helmert contrasts) that would avoid the redundancy.",
        "STATIC scores and DYNAMIC scores both come from the SAME F16 uncapped cache "
        "(results/suica_f16_visibility_taxonomy/pandora_uncapped_windows_scored19.parquet), "
        "reused directly rather than rebuilt from N1's raw parquets -- per the registration's "
        "explicit instruction, conditional on coverage being adequate. Coverage was measured "
        "(not assumed) at ~47% static / ~38% dynamic of the 794-user labeled population -- "
        "partial, but the same order of magnitude as F16's own accepted MBTI-axis coverage "
        "(43.5%/33.5% of 9,042), which F16 already used as its PRIMARY anchor population "
        "without rebuilding. Rebuilding from N1 raw parquets was judged unnecessary against "
        "this precedent, not because coverage was complete.",
        "The MBTI-label-population overlap (790/794 measured) and the F16-cache text-coverage "
        "figure (~47%/~38%) answer two different questions and must not be conflated -- the "
        "790 number describes how many enneagram-labeled users ALSO carry MBTI-axis labels "
        "(irrespective of whether SUICA ever scored their text); the ~47%/~38% numbers "
        "describe how many enneagram-labeled users have scoreable windows in the SUICA N1 "
        "pool at all. The registration explicitly warned against assuming the former implies "
        "the latter; they are reported as separate blocks in coverage.",
        "Point-biserial equivalence: is_type_N columns are hard 0/1 indicators; Pearson r "
        "against these is numerically a point-biserial correlation -- the same reasoning F16 "
        "applied to MBTI's hard 0/1 'positive_probability' columns.",
        "Secondary ANOVA eta-squared is a 9-group OMNIBUS statistic per (construct, channel) "
        "-- it does not isolate any single enneagram type the way the primary one-vs-rest "
        "cells do. Cross-referenced against primary hits in anova_cross_reference_for_hits "
        "but never used to gate or override the primary BH+floor classification.",
        "enneagram_wing (790/794 non-null) exists in author_profiles.csv but is explicitly "
        "OUT OF SCOPE for F17's registered design (enneagram_type only) -- not tested here, "
        "noted rather than silently expanded or silently ignored.",
    ]

    result = {
        "banner": BANNER,
        "registration": "F17, docs/SUICA_THEORY_FORMAL_NOTES_V3.md (registered 2026-07-12, "
                        "git 8afb3e3); ledger row F17",
        "governance": {
            "enneagram_first_use": {
                "banner_present": True,
                "note": ("First correlational use of PANDORA Enneagram type+wing labels "
                          "against SUICA constructs in this program; confirmed via repo-wide "
                          "grep (see module docstring for the specific prior-use audit: "
                          "PANDORA-paper P-feature/ridge-regression usage in "
                          "run_mcd_paper_grade_closure.py / run_pandora_original_flow_mcd.py, "
                          "and personality-leakage word lists elsewhere -- neither is a "
                          "SUICA-construct correlation). No prior replication target exists; "
                          "this run SPENDS these labels for future SUICA-correlational reuse "
                          "and itself becomes the reference point."),
                "n_enneagram_labeled": enn_diag["n_labeled"],
                "per_type_counts": enn_diag["per_type_counts_all_794"],
            },
            "big5_gate_not_applicable": (
                "F17 does not touch the PANDORA Big5 opening-#1 gate population or its H2/H6 "
                "assert-to-published-number step. Enneagram is an independent anchor with its "
                "own first-use governance tier, mirroring F16's MBTI-axis tier exactly (not "
                "the Big5-gate tier) -- no assert-to-published-number step applies here."),
            "anchor_design": (
                "CATEGORICAL (9-level typological), unlike F16's continuous Big5/MBTI anchors "
                "-- handled via one-vs-rest binary indicators rather than silently forced into "
                "a continuous shape. See ambiguities_and_design_decisions for the "
                "non-independence caveat this induces."),
        },
        "coverage": coverage,
        "constructs": cols,
        "dynamic_diagnostics_pandora_pool": dyn_diag,
        "primary_grid": rows,
        "primary_grid_summary": {
            "n_cells": n_cells, "n_cells_static_family": n_cells, "n_cells_dynamic_family": n_cells,
            "BOTH": len(both), "STATIC_ONLY": len(static_only),
            "DYNAMIC_ONLY": len(dynamic_only), "NEITHER": len(neither),
        },
        "t8_self_critical_corollary": t8_report,
        "secondary_anova_eta_squared_NOT_load_bearing": anova_rows,
        "anova_cross_reference_for_hits": anova_cross_ref,
        "soft_kill": {
            "triggered": soft_kill_triggered,
            "rule": ("UNLIKE F16's standing kill: zero DYNAMIC-ONLY cells here does NOT "
                     "retroactively falsify W10/T8 (rank(ker(A))>=1 is independently certified "
                     "by THREE OTHER instruments -- F10.8's B-gust1, E4's motion style, W10's "
                     "susceptibility -- that never touch external anchors at all). It would "
                     "only mean wcl_07's MBTI-T/F dynamic relationship does not generalize to "
                     "a structurally different (categorical) taxonomy, narrowing (not killing) "
                     "the claim to 'MBTI-T/F-specific' rather than 'trait-general.'"),
            "dynamic_only_constructs": dyn_only_constructs,
            "dynamic_only_in_w10_carrier_set": dyn_only_in_carrier_set,
            "dynamic_only_types_5_or_6": dyn_only_types_5_or_6,
            "w10_carrier_set": sorted(GUST1P_CARRIER_SET),
        },
        "registered_leans_check": {
            "a_static_only_or_neither_count": len(static_only) + len(neither),
            "a_expected": "most cells STATIC-ONLY or NEITHER, consistent with F16's 98.5% base rate",
            "b_dynamic_only_count": len(dynamic_only),
            "b_expected_range": "0-3, LOW-CONFIDENCE lean toward wcl_07 echoing in types 5/6",
            "c_both_count": len(both),
            "c_expected_range": "0-3",
        },
        "ambiguities_and_design_decisions": ambiguities,
        "runtime_seconds": round(time.time() - t_start, 1),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, default=lambda o: None))
    print(f"written: {OUT_JSON}")

    # ---------------- Markdown ----------------
    md = ["# F17 -- Enneagram taxonomy (EXPLORATORY, ledger row F17)", "",
          f"> {BANNER}", "",
          "## Governance", "",
          f"- Enneagram: FIRST correlational use / label-spending event (no prior "
          f"replication target). {enn_diag['n_labeled']} labeled users; per-type counts "
          f"{enn_diag['per_type_counts_all_794']}.",
          "- F17 does NOT touch the PANDORA Big5 opening-#1 gate / H2-H6 assert step -- "
          "independent MBTI-axis-style first-use tier.",
          "- Anchor design: CATEGORICAL (9-level), one-vs-rest binary indicators -- NOT "
          "independent by construction (mutually exclusive/exhaustive); flagged, not treated "
          "as 9 orthogonal contrasts.",
          "", "## Coverage (measured, not assumed)", "",
          "| population | n | in F16 cache (any window) | static covered | dynamic (m>=3) covered |",
          "|---|---|---|---|---|",
          f"| Enneagram-labeled | {enn_diag['n_labeled']} | {fcp['n_in_pool_any_window']} "
          f"({fcp['pct_in_pool_any_window']}%) | {fcp['n_static_covered']} "
          f"({fcp['pct_static_covered']}%) | {fcp['n_dynamic_covered_m_ge_3']} "
          f"({fcp['pct_dynamic_covered_m_ge_3']}%) |",
          "",
          f"MBTI-label-population overlap (a DIFFERENT question from cache coverage above): "
          f"{mpo['n_enneagram_also_mbti_labeled']}/{enn_diag['n_labeled']} "
          f"({mpo['pct_enneagram_also_mbti_labeled']}%) -- measured 790, not the 793 figure "
          f"named in the registration prose (see JSON reconciliation_note).",
          "", f"19 frozen constructs: {', '.join(cols)}", "",
          "## Primary classification summary (171 cells = 19 constructs x 9 one-vs-rest types)", "",
          f"BOTH={len(both)}, STATIC-ONLY={len(static_only)}, DYNAMIC-ONLY={len(dynamic_only)}, "
          f"NEITHER={len(neither)} (of {n_cells})", "",
          ("**SOFT KILL note**: zero DYNAMIC-ONLY cells -- per registration this does NOT "
           "retroactively falsify W10/T8, only narrows wcl_07's claim to MBTI-T/F-specific."
           if soft_kill_triggered else
           f"DYNAMIC-ONLY constructs: {dyn_only_constructs} (W10 carrier-set overlap: "
           f"{dyn_only_in_carrier_set}; types 5/6 present: {dyn_only_types_5_or_6})"),
          "",
          "## T8 self-critical corollary -- paired static/dynamic r+q for every hit", "",
          f"> {t8_report['rule']}", ""]

    md.append("### DYNAMIC-ONLY hits (full pairing + floor-gap narrative)")
    if t8_report["dynamic_only_hits"]:
        md.append("| construct | type | r_static | q_static | r_dynamic | q_dynamic | narrative |")
        md.append("|---|---|---|---|---|---|---|")
        for h in t8_report["dynamic_only_hits"]:
            md.append(f"| {h['construct']} | {h['enneagram_type']} | {h['r_static']:+.4f} | "
                      f"{h['q_static_bh']:.4g} | {h['r_dynamic']:+.4f} | {h['q_dynamic_bh']:.4g} | "
                      f"{h['narrative']} |")
    else:
        md.append("(none)")
    md.append("")
    md.append("### BOTH hits (full pairing)")
    if t8_report["both_hits"]:
        md.append("| construct | type | r_static | q_static | r_dynamic | q_dynamic |")
        md.append("|---|---|---|---|---|---|")
        for h in t8_report["both_hits"]:
            md.append(f"| {h['construct']} | {h['enneagram_type']} | {h['r_static']:+.4f} | "
                      f"{h['q_static_bh']:.4g} | {h['r_dynamic']:+.4f} | {h['q_dynamic_bh']:.4g} |")
    else:
        md.append("(none)")
    md.append("")
    md.append("### STATIC-ONLY hits (full pairing, for T8-corollary symmetry -- listed here "
               "explicitly in addition to the full grid below)")
    if t8_report["static_only_hits"]:
        md.append("| construct | type | r_static | q_static | r_dynamic | q_dynamic | "
                  "dynamic_floor_gap |")
        md.append("|---|---|---|---|---|---|---|")
        for h in t8_report["static_only_hits"]:
            md.append(f"| {h['construct']} | {h['enneagram_type']} | {h['r_static']:+.4f} | "
                      f"{h['q_static_bh']:.4g} | {h['r_dynamic']:+.4f} | {h['q_dynamic_bh']:.4g} | "
                      f"{h['dynamic_floor_gap']} |")
    else:
        md.append("(none)")
    md.append("")

    md += ["## Full primary grid (all 171 cells, both channels paired)", "",
           "| construct | type | r_static | q_static | r_dynamic | q_dynamic | class |",
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['construct']} | {r['enneagram_type']} | {r['r_static']:+.4f} | "
                  f"{r['q_static_bh']:.4g} | {r['r_dynamic']:+.4f} | {r['q_dynamic_bh']:.4g} | "
                  f"{r['classification']} |")

    md += ["", "## Secondary: one-way ANOVA eta-squared (19 constructs x 2 channels = 38 cells, "
               "NOT load-bearing, NOT part of primary classification)", "",
           "| construct | channel | k_groups | n | F | p | eta_sq |",
           "|---|---|---|---|---|---|---|"]
    for a in anova_rows:
        f_str = f"{a['f_stat']:.3f}" if np.isfinite(a["f_stat"]) else "NaN"
        p_str = f"{a['p_value']:.4g}" if np.isfinite(a["p_value"]) else "NaN"
        e_str = f"{a['eta_sq']:.4f}" if np.isfinite(a["eta_sq"]) else "NaN"
        md.append(f"| {a['construct']} | {a['channel']} | {a['k_groups']} | {a['n']} | "
                  f"{f_str} | {p_str} | {e_str} |")

    md += ["", "## ANOVA cross-reference for primary hits (omnibus vs one-vs-rest, "
               "reporting discipline extended per T8)", ""]
    if anova_cross_ref:
        md.append("| construct | type | class | r_static | r_dynamic | ANOVA eta_sq (static) | "
                  "ANOVA eta_sq (dynamic) |")
        md.append("|---|---|---|---|---|---|---|")
        for x in anova_cross_ref:
            es = x["anova_static_eta_sq"]
            ed = x["anova_dynamic_eta_sq"]
            es_str = f"{es:.4f}" if es is not None and np.isfinite(es) else "NaN"
            ed_str = f"{ed:.4f}" if ed is not None and np.isfinite(ed) else "NaN"
            md.append(f"| {x['construct']} | {x['enneagram_type']} | {x['classification']} | "
                      f"{x['primary_r_static']:+.4f} | {x['primary_r_dynamic']:+.4f} | "
                      f"{es_str} | {ed_str} |")
    else:
        md.append("(no non-NEITHER primary cells)")

    md += ["", "## Ambiguities / design decisions", ""]
    md += [f"- {a}" for a in ambiguities]
    OUT_MD.write_text("\n".join(md) + "\n")
    print(f"written: {OUT_MD}")
    print(f"[done] total runtime {time.time() - t_start:.1f}s")


if __name__ == "__main__":
    main()
