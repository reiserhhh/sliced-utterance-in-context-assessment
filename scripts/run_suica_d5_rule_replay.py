#!/usr/bin/env python3
"""
SUICA D5 — The rule machine, replayed.

Registered in docs/SUICA_DEFENSE_PHASE_PLAN.md, section
"D5 — The rule machine, replayed (the defense phase's closing leg)"
(registration commit eb972ea, BEFORE run).

WHAT THIS IS. The program has recorded 41 planner registration defects and
paid for 21 standing rules. This harness makes the COMPLETENESS half of the
replay mechanical: it greps every defect-number citation out of the tracked
documents, checks each cited number against the registry table below
(exactly one row per number — gate G0R), and emits both
`docs/SUICA_DEFECT_REGISTRY.md` and the coverage statistics used in
`reports/SUICA_D5_RULE_REPLAY_REPORT.md`.

The INTELLECTUAL half — which rule covers a defect today, at what stage it
would be caught, and whether that is earlier than the historical catch — is
authored by hand in the DEFECTS table below. The harness does not infer it;
it transports it, counts it, and refuses to disagree with the corpus about
which defect numbers exist.

STRUCTURED DATA FILE. The registration calls for "a structured data file you
author". It is the DEFECTS / RULES tables in this module: keeping the data
inside the harness holds the leg to its six committed deliverables and makes
the emitted markdown a pure function of one tracked file.

PURITY GATE (G1R, binding): document-space only. This harness reads tracked
`.md` files and writes two of them. It imports stdlib only, generates no
world, touches no `results/` tree, and never imports `suica_core`.

Deliverable 1 of six. Re-runnable:
  python scripts/run_suica_d5_rule_replay.py
"""

from __future__ import annotations

import os
import re
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, "docs")
REPORTS = os.path.join(REPO, "reports")
REGISTRY_PATH = os.path.join(DOCS, "SUICA_DEFECT_REGISTRY.md")

_T0 = time.time()

# --------------------------------------------------------------------------
# The rule set as it stands today (1-21), with the defect each was paid for.
# One line each; provenance is doc + the section that created the rule.
# --------------------------------------------------------------------------

RULES: dict[int, dict[str, str]] = {
    1: dict(
        text="Designed-null gates state their aggregation rule (per-cell vs trend) and multiplicity treatment BEFORE the run.",
        paid_by="#1",
        origin="docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F4 outcome/adjudication",
    ),
    2: dict(
        text="Every leg pre-states the scale at which its target is measurably non-zero and its minimum detectable effect; a noise-floor null is UNDERPOWERED, not a null.",
        paid_by="#2",
        origin="docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F6 adjudication ('Standing rule added')",
    ),
    3: dict(
        text="Verify a non-zero causal channel at every tested parameter value from the generator; a null on an inert knob is VACUOUS.",
        paid_by="#3",
        origin="docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F7 adjudication ('Standing rule added (third)')",
    ),
    4: dict(
        text="Every gate bounds MATERIALITY via an equivalence form (CI inside a justified margin) — never nil significance on a known-nonzero quantity.",
        paid_by="#4",
        origin="docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F8 adjudication ('Standing rule added (fourth), and it subsumes the others')",
    ),
    5: dict(
        text="Justify the analysis grain for power against the registered bar; do not inherit the line's default grain.",
        paid_by="#5",
        origin="docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-G3 adjudication ('Standing rule (fifth)')",
    ),
    6: dict(
        text="Define the winner jointly over target AND safety — the best arm among those passing both — never by the target's extremum.",
        paid_by="#6",
        origin="docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-H2 adjudication ('Standing rule (sixth)')",
    ),
    7: dict(
        text="Where the anti-cosmetic check has graded levels, the registration states which level qualifies and the leg reports the best arm at EACH level.",
        paid_by="#7",
        origin="docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-H3 adjudication ('Standing rule (seventh)')",
    ),
    8: dict(
        text="Every factual claim cited to motivate a lean is checked against the persisted artifacts at full precision before the registration is committed.",
        paid_by="#8",
        origin="docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-J2 adjudication ('Eighth planner defect, and a new kind')",
    ),
    9: dict(
        text="A registration introducing a constructed instrument pins every convention that changes its hypothesis-relevance, or pre-delegates the choice with an explicit decision rule; an ambiguity found mid-leg is resolved before any hypothesis-relevant number exists and ALL readings are reported.",
        paid_by="#9",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1 adjudication (ninth defect)",
    ),
    10: dict(
        text="A registered manipulation is derived from generator SOURCE so it preserves the design's defining contrast, and Part 0 proves non-degeneracy before arms.",
        paid_by="#11",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication (#10-#12 block)",
    ),
    11: dict(
        text="Every registered gate is checked for arithmetic satisfiability under the cited anchor statistics at registration time.",
        paid_by="#12",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication (#10-#12 block)",
    ),
    12: dict(
        text="Registered manipulations and channels are specified by generator SOURCE OBJECT (file:function/variable), never by knob names or natural-language channel descriptions alone.",
        paid_by="#10 + K1c's two rule-9 ambiguities",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1c adjudication",
    ),
    13: dict(
        text="Every registered interval clause names its resampling spec (B, seed policy); at adjudication verdict stability is checked at >=10x B, and a clause boundary inside achievable Monte-Carlo error scores BOUNDARY, not HOLD/MISS.",
        paid_by="none (paid for by L-1's fragility, not by a numbered defect)",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1d adjudication",
    ),
    14: dict(
        text="When a lean compares quantities across scales or instruments, the registration pins the LINK function and its justification; absent that, the lean is re-designed to be within-instrument.",
        paid_by="#20",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2b adjudication",
    ),
    15: dict(
        text="The registered adjudication space is a PARTITION of the outcome space, verified by ENUMERATION at registration time (a truth table with every combination assigned to exactly one named outcome).",
        paid_by="#17 + #21",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2c adjudication",
    ),
    16: dict(
        text="The rule-15 enumeration extends over the FULL adjudication object — cells, lean predicates and pivot routing — as one truth table, every realizable combination routed to exactly one outcome.",
        paid_by="#22",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2d adjudication",
    ),
    17: dict(
        text="Every registered stratum and task carries either a generator-derived realizability argument or a Part-0 realizability check with a pre-declared fallback ladder.",
        paid_by="#25 + #26",
        origin="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K3 adjudication",
    ),
    18: dict(
        text="Rule-11 satisfiability is checked JOINTLY across all clauses sharing generative knobs, not per-clause.",
        paid_by="#27",
        origin="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication",
    ),
    19: dict(
        text="Every lean bar is derived from the theorem's OWN quantity and scale, with the registration stating which theorem-quantity the bar shadows; a bar on a different quantity is a defect regardless of outcome.",
        paid_by="#30",
        origin="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication",
    ),
    20: dict(
        text="When the rule-18 joint check finds ANY lean's condition-set empty, the leg STOPS before arms as a registration defect, unless empty-set was pre-declared adjudicable.",
        paid_by="#31 + #32",
        origin="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication",
    ),
    21: dict(
        text="CI-containment bars on instrument validations carry a registered absolute-error budget; an instrument may not fail validation because its precision exposes a residual smaller than the budget.",
        paid_by="#37",
        origin="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L3 adjudication",
    ),
}

CONVENTIONS: list[tuple[str, str]] = [
    ("round-trip parsing", "all artifact re-derivations parse CSV with float_precision='round_trip' (K1c' anomaly 1; pandas 3.0.2's default parser does not round-trip float64)"),
    ("4-world pilots, df-aware", "pilot-sd MDE gates use >=4 pilot worlds or a registered df-based inflation factor (K2d anomaly A-5; standing for all sd-based gates from K2e)"),
    ("Part-0 bit-identity verification", "any bit-identity claim stated in Part 0 is VERIFIED in Part 0, not asserted (K2a anomaly vi)"),
    ("chunked foreground stages", "no background jobs or monitors; foreground chunked stages with explicit timeouts; Part 0 written into the report BEFORE any arm runs"),
    ("aggregation provenance", "every future leg's decision.json aggregates name their computing function (file:line) (D2 adjudication)"),
    ("salt embedding", "every sealed artifact EMBEDS its salt within the sealed bytes, so any later manifest/backup hash stays guess-proof (D3 adjudication)"),
    ("legacy-anchor parser naming", "a bit-exact anchor against a pre-round-trip artifact names the parser that produced the legacy number (K1d)"),
]

# --------------------------------------------------------------------------
# The registry. One row per defect. `today` is the replay classification.
# stage vocabulary: REGISTRATION-TIME < PART-0 < POST-HOC < UNCOVERED
# --------------------------------------------------------------------------

REG = "REGISTRATION-TIME"
P0 = "PART-0"
PH = "POST-HOC"
UN = "UNCOVERED"
STAGE_ORDER = {REG: 0, P0: 1, PH: 2, UN: 3}

DEFECTS: list[dict] = [
    dict(n=1, era="F/G-line (pre-#9)", leg="M4-F4",
         where="docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F4 outcome ~L1120-1131",
         desc="G0's designed-null gate text mixed a per-cell rule with a trend rule; multiplicity unstated, so the reading was chosen after the numbers.",
         rule_paid="1", family="aggregation",
         today_rules="1", today_stage=REG, hist_stage=PH,
         note="Ordinally recorded ('the standing rule added after M4-F4's G0 ambiguity'); numbered #1 here by chronology."),
    dict(n=2, era="F/G-line (pre-#9)", leg="M4-F6",
         where="docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F6 adjudication ~L1485-1502",
         desc="Base scale left free and no power statement required, so a null was measured at the target's noise floor (CI half-width ~ the quantity itself).",
         rule_paid="2", family="power",
         today_rules="2, 5", today_stage=REG, hist_stage=PH,
         note="Recorded as 'the second registration defect of this kind'."),
    dict(n=3, era="F/G-line (pre-#9)", leg="M4-F7",
         where="docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F7 adjudication ~L1665-1685",
         desc="A design dimension was economized away without checking which of its values carried the causal channel — justified by citing the arm that was in fact the underpowered one.",
         rule_paid="3", family="channel-liveness",
         today_rules="3, 8", today_stage=P0, hist_stage=PH,
         note="Recorded as 'my third registration defect of the same family'."),
    dict(n=4, era="F/G-line (pre-#9)", leg="M4-F8",
         where="docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F8 adjudication ~L1830-1850",
         desc="A gate written as a nil-significance test on a residual nonzero by construction (phi^41 = 1.06e-4), so its failure probability grew with sample size; voided a leg on effects 2-3 orders larger.",
         rule_paid="4", family="materiality",
         today_rules="4", today_stage=REG, hist_stage=PH,
         note="Recorded as 'Fourth planner registration defect of the same family'."),
    dict(n=5, era="F/G-line (pre-#9)", leg="M4-G3",
         where="docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-G3 adjudication ~L617-622",
         desc="G0 required a pre-stated MDE but not a GRAIN, so the line's default (n=6-8 worlds) was inherited though >4x under the bar while the author grain (n~745) was available.",
         rule_paid="5", family="grain",
         today_rules="5, 2", today_stage=REG, hist_stage=PH,
         note="Recorded as 'Fifth planner registration defect, and its rule'. Historical catch was mid-leg (flagged before the adaptive arms) but the leg still fit no registered branch."),
    dict(n=6, era="F/G-line (pre-#9)", leg="M4-H2",
         where="docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-H2 adjudication ~L1749-1768",
         desc="The 'winner' was defined as the arm with the largest target reduction, then safety tested there — target-only selection systematically picks the most cosmetic arm (and did).",
         rule_paid="6", family="winner-definition",
         today_rules="6", today_stage=REG, hist_stage=PH,
         note="Recorded as 'the sixth of its family'. Same defect had already cost M4-G1 its best arm (shrinkage .1, missed the 25% bar by .14 points) — recorded there as a critique with no rule."),
    dict(n=7, era="F/G-line (pre-#9)", leg="M4-H3",
         where="docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-H3 adjudication ~L1948-1961",
         desc="The joint winner rule was still target-priority within the qualifying set, so it picked the most aggressive qualifying arm and hid the arm that cleared the STRONGER safety level.",
         rule_paid="7", family="graded-safety",
         today_rules="7, 6", today_stage=REG, hist_stage=PH,
         note="Recorded as the seventh; the 8th-defect note enumerates it as 'graded levels'."),
    dict(n=8, era="F/G-line (pre-#9)", leg="M4-J2",
         where="docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-J2 adjudication ~L2901-2910",
         desc="A factual claim used to motivate a lean was not verified against persisted data at full precision before the registration was committed — so the control tested the wrong thing.",
         rule_paid="8", family="fact-verification",
         today_rules="8", today_stage=REG, hist_stage=PH,
         note="Recorded as 'Eighth planner defect, and a new kind' — the first defect in EVIDENCE rather than in a RULE."),
    dict(n=9, era="K-line", leg="M4-K1",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1 adjudication ~L284-296",
         desc="The registration underdetermined R-abs's norm convention: T3(c)'s one-common-norm hypothesis and the deployable per-half estimated norms are inequivalent readers, and one name covered two.",
         rule_paid="9", family="instrument-pinning",
         today_rules="9, 12", today_stage=REG, hist_stage=P0,
         note="Recorded as 'ninth in the program's account' — the first defect carrying a program number in the text."),
    dict(n=10, era="K-line", leg="M4-K1 (found in K1b)",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication ~L572-580",
         desc="The registration asserted 'the generator exposes an explicit occasion-mean channel (w_mu = 0.15)'. FALSE: w_mu weights the AUTHOR mean channel (f2:178) — a code claim cited from a knob NAME.",
         rule_paid="12 (with K1c's ambiguities)", family="fact-verification",
         today_rules="8, 12", today_stage=REG, hist_stage=PH,
         note="Explicitly typed a rule-8 violation instance: claims about code are factual claims."),
    dict(n=11, era="K-line", leg="M4-K1b",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication ~L581-586",
         desc="The registered decomposition was degenerate by construction at the registered knob (S_frame == 1 as an arithmetic identity of the generator at kappa=1.0).",
         rule_paid="10", family="degeneracy",
         today_rules="10, 12", today_stage=P0, hist_stage=PH,
         note=""),
    dict(n=12, era="K-line", leg="M4-K1b",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication ~L587-590",
         desc="G4b demanded a CI-excludes-zero clause at n=3 that the anchor's own sd makes arithmetically unsatisfiable.",
         rule_paid="11", family="satisfiability",
         today_rules="11", today_stage=REG, hist_stage=P0,
         note=""),
    dict(n=13, era="K-line", leg="M4-K1c",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1c adjudication ~L853-859",
         desc="G2c's stated rationale ('sqrt(1-kappa) > 0 keeps the author AR state in the panel, so common-removal must not collapse the contrast') is a non-sequitur: the retained state is design-INVARIANT.",
         rule_paid="none (rule 10 caught it)", family="degeneracy",
         today_rules="10, 12", today_stage=P0, hist_stage=P0,
         note="The first time a standing rule caught the planner BEFORE compute: a 74-second stop, zero adjudicated worlds."),
    dict(n=14, era="K-line", leg="M4-K1c'",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1c' adjudication ~L1130-1136",
         desc="G0''s anchor location misstated (decision.json cited for two families that live in gates.json).",
         rule_paid="none", family="fact-verification",
         today_rules="8", today_stage=REG, hist_stage=P0,
         note="Typed 'rule-8 hygiene family'; the gate was satisfied in the stronger raw-row form."),
    dict(n=15, era="K-line", leg="M4-K1c'",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1c' adjudication ~L1137-1142",
         desc="G3''s 'within 2x' sd clause was TWO-SIDED, so it fails when the fresh variance is SMALLER — an equivalence band that punishes improvement. One-sided (<= 2x) was the intent.",
         rule_paid="none", family="clause-direction",
         today_rules="none (rule 11 checks satisfiability, not clause DIRECTION — stated in the record itself)",
         today_stage=UN, hist_stage=P0,
         note="UNCOVERED. Absorbed historically by a registered fallback and carried forward only as a 'lesson' (K1d report; K2a plan L1210), never as a rule. Motivates proposal P1."),
    dict(n=16, era="K-line", leg="M4-K1d",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1d adjudication ~L1413-1417",
         desc="G1d was listed among 'Part 0 gates' though it is unmeasurable before the intact arm exists — a gate assigned to a stage where its inputs do not yet exist.",
         rule_paid="none", family="gate-stage-feasibility",
         today_rules="none (rules 11/18/20 check arithmetic and joint satisfiability, not stage feasibility)",
         today_stage=UN, hist_stage=P0,
         note="UNCOVERED. Repaired in place by the executor's R-0.6 stage-with-enforced-stop. Motivates proposal P2."),
    dict(n=17, era="K-line", leg="M4-K1d",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1d adjudication ~L1418-1421",
         desc="The pivot space had a GAP: P2d covered 'L-1 MISS and gamma DISJOINT' but not 'MISS and OVERLAPPING' — and the measurement sat exactly on that boundary.",
         rule_paid="15 (with #21)", family="partition",
         today_rules="15, 16", today_stage=REG, hist_stage=PH,
         note=""),
    dict(n=18, era="K-line", leg="M4-K2a",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2a adjudication ~L1645-1648",
         desc="G2a's ACF clause pinned neither CI level nor multiplicity.",
         rule_paid="none", family="aggregation",
         today_rules="1, 13", today_stage=REG, hist_stage=P0,
         note="Executor resolved to family-wise 95% over 6 before arms; both readings reported."),
    dict(n=19, era="K-line", leg="M4-K2a",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2a adjudication ~L1648-1652",
         desc="'Shares within 1% of design' was ambiguous (absolute vs relative) and, read relatively, UNSATISFIABLE for the common channel at n_occ draws.",
         rule_paid="none", family="satisfiability",
         today_rules="11, 9, 18", today_stage=REG, hist_stage=P0,
         note="Typed 'a rule-11-family miss'; resolved to absolute before arms."),
    dict(n=20, era="K-line", leg="M4-K2b",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2b adjudication ~L1934-1946",
         desc="The registration compared quantities on two different scales (card attenuation vs field agreement) without pinning the link function — and the branch verdict is link-sensitive.",
         rule_paid="14", family="link",
         today_rules="14", today_stage=REG, hist_stage=P0,
         note="Executor's RN-6 (identity link PRIMARY, declared before arms) preserved adjudicability."),
    dict(n=21, era="K-line", leg="M4-K2c",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2c adjudication ~L2217-2228",
         desc="The K2c adjudication space was declared partitioned and is not: L-1 (equivalence-within-margin) and L-2 (significance+sign) are independent axes and significant-but-sub-material satisfies both.",
         rule_paid="15 (with #17)", family="partition",
         today_rules="15, 16", today_stage=REG, hist_stage=PH,
         note="Second partition failure — #17 was a gap, this one an overlap."),
    dict(n=22, era="K-line", leg="M4-K2d",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2d adjudication ~L2527-2536",
         desc="Rule 15 was applied at the CELL level only, not to lean predicates and pivot routing — 8 overlaps + 4 gaps at the lean level, one unrouted cell class at the pivot level.",
         rule_paid="16", family="partition",
         today_rules="16, 15", today_stage=REG, hist_stage=P0,
         note="Caught by the executor's own extended enumeration in Part 0; did not bind."),
    dict(n=23, era="K-line", leg="M4-K2e",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2e adjudication ~L2840-2844",
         desc="L-SPEC lumped MAT-SIG and SUB-SIG cells while P-SPEC's consequence text presumed the material grade — a rule-7 instance at the ROUTING level.",
         rule_paid="none", family="graded-safety",
         today_rules="7, 16", today_stage=REG, hist_stage=PH,
         note="Executor executed graded. Rule-9 ambiguity: 'executed graded, as above' also reads as a pre-arms resolution (PART-0); the record places the defect in the planner's adjudication, so POST-HOC is used and the PART-0 reading is disclosed."),
    dict(n=24, era="K-line", leg="M4-K2e",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2e adjudication ~L2844-2849",
         desc="The registration's premise that K2e's w_int 'exceeds K2a's validated range' was factually WRONG for its own solved shares (0.0857/0.1458 vs ceilings 0.2644/0.2161).",
         rule_paid="none", family="fact-verification",
         today_rules="8", today_stage=REG, hist_stage=P0,
         note="Typed 'rule-8 family'; conservative direction, no impact. Solved shares are Part-0 objects (K2e report L163)."),
    dict(n=25, era="K-line", leg="M4-K3",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K3 adjudication ~L3144-3156",
         desc="The UNEQUAL stratum is UNREALIZABLE in this world family at every registered rung (0 pairs at ratio>3 and >2.5; 19 of 1.57M at >2) — F2-family trait latents are one N(0,I_48) draw.",
         rule_paid="17 (with #26)", family="realizability",
         today_rules="17", today_stage=P0, hist_stage=P0,
         note="Absorbed by the pre-declared UNEQUAL-Q fallback ladder. Rule 17 permits a registration-time generator-derived argument; the GUARANTEED catch is the Part-0 check."),
    dict(n=26, era="K-line", leg="M4-K3",
         where="docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K3 adjudication ~L3144-3156",
         desc="The split-half rank-1 identification task sits at CEILING (0 misses in the pilot), making three leans unscorable as posed.",
         rule_paid="17 (with #25)", family="realizability",
         today_rules="17", today_stage=P0, hist_stage=P0,
         note="Absorbed by the pre-declared PA->PB->PC protocol ladder."),
    dict(n=27, era="L-line", leg="M4-L1",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication ~L306-315",
         desc="G2L's mid-band clause and V-1's 0.95 bar are JOINTLY unsatisfiable on the ISO arm because rho_id ties sigma_b to Delta; individually each clause was satisfiable.",
         rule_paid="18", family="joint-satisfiability",
         today_rules="18, 11, 20", today_stage=REG, hist_stage=P0,
         note="PROVED by the executor; handled by RN-10's pre-declared guard."),
    dict(n=28, era="L-line", leg="M4-L1",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication ~L313-315",
         desc="V-3(d) was a designed identity (removal == rho_id=0 card at 3.1e-16) — a construction certificate scored as a lean, i.e. a test that cannot fail.",
         rule_paid="none", family="degeneracy",
         today_rules="10, 3", today_stage=P0, hist_stage=PH,
         note="Typed 'rule-3 family, vacuous-pass'."),
    dict(n=29, era="L-line", leg="M4-L1",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication ~L315-316",
         desc="A floor clause with no registered comparand — the bar named a quantity but nothing to compare it against.",
         rule_paid="none", family="instrument-pinning",
         today_rules="9, 19", today_stage=REG, hist_stage=P0,
         note="Executor (RN-7) pinned the noise-free TRUE-card rate before arms, under rule 9."),
    dict(n=30, era="L-line", leg="M4-L1",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication ~L316-321",
         desc="V-3(c)'s bar tests a proposition R2 does not make — an energy threshold standing in for an achieved-ARI claim (oracle projection restored only 13.5%).",
         rule_paid="19", family="shadow-fidelity",
         today_rules="19", today_stage=REG, hist_stage=PH,
         note="Head of the #30/#33/#36 family."),
    dict(n=31, era="L-line", leg="M4-L2",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L598-608",
         desc="W-1's two conditions are jointly unsatisfiable on the Delta axis — the lean's condition set is EMPTY (gap factor 1.571), so the leg 'missed on a window my own conditions made empty'.",
         rule_paid="20 (with #32)", family="empty-set",
         today_rules="20, 18", today_stage=REG, hist_stage=P0,
         note="PROVED before the arms by rule 18's first application; L2's registration had not pre-declared empty-set as adjudicable, which is the gap rule 20 closes."),
    dict(n=32, era="L-line", leg="M4-L2",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L598-608",
         desc="The design clause 'oracle-S floor < 0.005 everywhere' is jointly unsatisfiable with the bracket's low end.",
         rule_paid="20 (with #31)", family="empty-set",
         today_rules="20, 18", today_stage=REG, hist_stage=P0,
         note="Same family as #31."),
    dict(n=33, era="L-line", leg="M4-L2",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L593-600",
         desc="W-2's bar sat on an ARI where the BBP/spiked-PCA law owns the subspace OVERLAP — a bar on a quantity the theorem does not predict.",
         rule_paid="none", family="shadow-fidelity",
         today_rules="19", today_stage=REG, hist_stage=P0,
         note="Typed 'rule-19 class, same family as #30'; the theorem-faithful companion was pinned before arms."),
    dict(n=34, era="L-line", leg="M4-L2",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L598-604 (evidence ~L526-528)",
         desc="W-4's registration had no clause able to distinguish 'the constant is wrong' from 'the partition is wrong' — the lean's two named alternatives are confounded by design.",
         rule_paid="none", family="lean-identifiability",
         today_rules="none (rule 19 fixes the bar's QUANTITY, not whether the contrast can separate the alternatives it names)",
         today_stage=UN, hist_stage=PH,
         note="UNCOVERED. Diagnosed only by a post-hoc TRUE-groups control (10/10 with true labels). Motivates proposal P2."),
    dict(n=35, era="L-line", leg="M4-L2",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L598-604 (evidence ~L500-506)",
         desc="W-3's containment clause is unresolvable at eta=0 — 1536 Bernoulli tests against a 3.5e-7 prediction, i.e. the design's quantum is coarser than the predicted effect.",
         rule_paid="none", family="precision-budget",
         today_rules="2, 21", today_stage=REG, hist_stage=PH,
         note="Rule 2's MDE requirement is the registration-time refusal; rule 21 covers the adjudication-side twin."),
    dict(n=36, era="L-line", leg="M4-L3",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L3 adjudication ~L730-734, ~L849-855",
         desc="X-1's pole clause demanded tolerance ZERO on the same quantity X-2 declares resolvable only to 0.125 — a nil-significance test standing in for an equivalence claim.",
         rule_paid="none", family="materiality",
         today_rules="4, 21, 19", today_stage=REG, hist_stage=PH,
         note="Rule-9 ambiguity in the corpus's own typing: the L doc types #36 'rule-19 class, third of the #30/#33 family' (wrong-quantity bar); the replay reads it as squarely rule-4 (nil form on a known-nonzero quantity). Both readings give REGISTRATION-TIME."),
    dict(n=37, era="L-line", leg="M4-L3",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L3 adjudication ~L773-778, ~L858-866",
         desc="Clause (c) has no precision budget: it gets HARDER the better the correction works (CIs sharpened 6-39x), conflating 'the correction is right' with 'the residual is below the resolution the correction creates'.",
         rule_paid="21", family="precision-budget",
         today_rules="21, 4", today_stage=REG, hist_stage=PH,
         note=""),
    dict(n=38, era="L-line", leg="M4-L3",
         where="docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L3 anomalies ~L809-814, adjudication ~L878",
         desc="Executor-side: the registration says 'regressed on (1-ARI) across cells' without stating the observation grain; the first draft used (cell, world), where per-panel B_cal noise attenuates R^2 from 0.892 to 0.040.",
         rule_paid="none", family="grain",
         today_rules="5", today_stage=REG, hist_stage=P0,
         note="The only executor-side defect in the registry; corrected pre-arms, both grains reported."),
    dict(n=39, era="defense", leg="D1",
         where="docs/SUICA_DEFENSE_PHASE_PLAN.md — D1 planner adjudication ~L169-174",
         desc="The registration cited kappa at the wrong path AND with the wrong sign convention while building the sealed prediction set.",
         rule_paid="none", family="fact-verification",
         today_rules="8, 12", today_stage=REG, hist_stage=P0,
         note="Typed 'rule-8 family'; executor corrected with disclosure and re-derived bit-exactly from the true sources."),
    dict(n=40, era="defense", leg="D2",
         where="docs/SUICA_DEFENSE_PHASE_PLAN.md — D2 planner adjudication ~L342-352; docs/SUICA_IDENTITY_THEORY_V1.md appendix T ~L1204",
         desc="Four wrong factual claims in PUBLISHED PROSE (appendix C.1's 'five arms' = four; C.2's '<= 0.0045' vs 0.004512746557818383; K-R1's '0/32 worlds' vs 0/192 arm-worlds; the floor law's 'every reading' vs pooled Spearman 0.985).",
         rule_paid="none", family="prose-citation",
         today_rules="none (rule 8 binds facts cited to MOTIVATE A LEAN in a registration; these are synthesis/appendix prose)",
         today_stage=UN, hist_stage=PH,
         note="UNCOVERED. Found only because D2 was a dedicated adversarial pass; typed in the corpus itself as 'rule-8-in-prose', an extension never enacted. Motivates proposal P3."),
    dict(n=41, era="defense", leg="D3",
         where="docs/SUICA_DEFENSE_PHASE_PLAN.md — D3 outcome ~L424-430 and adjudication ~L529-534",
         desc="The D3 registration's scope arithmetic was wrong twice in one section ('thirteen trees ... the fifteen'); the true scope is 17 trees.",
         rule_paid="none", family="prose-citation",
         today_rules="none under the strict reading of rule 8 (a scope count motivates no lean); rule 8 under a broad reading",
         today_stage=UN, hist_stage=P0,
         note="UNCOVERED with a rule-9 both-readings note: the executor reconciled it in Part 0 and archived the superset, but no rule mandated that reconciliation. Motivates proposal P3."),
]

# --------------------------------------------------------------------------
# G0R — grep the corpus for every defect-number citation.
# --------------------------------------------------------------------------

# "defect #12", "Defects #36-#38", "(#31-#35)", "#25, #26", "defect #1-#41"
DASH = "–—-"
# NB: no whitespace after '#', and '#' not preceded by '#' — otherwise markdown
# headings ("### 0.2 ... registration defect ...") register as a citation of #0.
NUM_RE = re.compile(r"(?<!#)#(\d{1,3})")
RANGE_RE = re.compile(r"(?<!#)#(\d{1,3})\s*[" + DASH + r"]\s*#?(\d{1,3})")
# a citation context is a line mentioning defect(s); bare "#17" elsewhere is not counted
CONTEXT_RE = re.compile(r"defect", re.IGNORECASE)

ORDINALS = {
    1: [r"M4-F4'?s? G0 ambiguity", r"M4-F4: G0'?s? aggregation rule", r"F4: aggregation\s+rule unstated"],
    2: [r"second registration defect of this kind"],
    3: [r"third registration defect of the same family"],
    4: [r"Fourth planner registration defect"],
    5: [r"Fifth planner registration defect"],
    6: [r"sixth of its family"],
    7: [r"Standing rule \(seventh\)"],
    8: [r"Eighth planner defect"],
}


def iter_docs():
    for root in (DOCS, REPORTS):
        if not os.path.isdir(root):
            continue
        for dirpath, _dirnames, filenames in os.walk(root):
            for fn in sorted(filenames):
                if fn.endswith(".md"):
                    yield os.path.join(dirpath, fn)


def scan_citations():
    """Return (cited_numbers -> {file: count}), total mention lines, range-expanded set."""
    cited: dict[int, dict[str, int]] = {}
    lines_with_mentions = 0
    range_lines = []
    for path in iter_docs():
        rel = os.path.relpath(path, REPO)
        if rel.endswith("SUICA_DEFECT_REGISTRY.md"):
            continue  # the registry itself is the answer key, not a citation source
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        for ln, line in enumerate(text.splitlines(), 1):
            if not CONTEXT_RE.search(line):
                continue
            nums: set[int] = set()
            consumed: list[tuple[int, int]] = []
            for m in RANGE_RE.finditer(line):
                lo, hi = int(m.group(1)), int(m.group(2))
                if 1 <= lo <= hi <= 999:
                    nums.update(range(lo, hi + 1))
                    consumed.append((m.start(), m.end()))
                    range_lines.append((rel, ln, f"#{lo}-#{hi}"))
            for m in NUM_RE.finditer(line):
                if any(s <= m.start() < e for s, e in consumed):
                    continue
                nums.add(int(m.group(1)))
            if nums:
                lines_with_mentions += 1
            for n in nums:
                cited.setdefault(n, {}).setdefault(rel, 0)
                cited[n][rel] += 1
    return cited, lines_with_mentions, range_lines


def scan_ordinals():
    """Pre-#9 era: the records number RULES and ordinal defects, not '#N'."""
    found: dict[int, list[str]] = {}
    for path in iter_docs():
        rel = os.path.relpath(path, REPO)
        if rel.endswith("SUICA_DEFECT_REGISTRY.md"):
            continue
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
        for n, pats in ORDINALS.items():
            for pat in pats:
                for m in re.finditer(pat, text):
                    ln = text[: m.start()].count("\n") + 1
                    found.setdefault(n, []).append(f"{rel}:{ln}")
    return found


def gate_g0r():
    cited, mention_lines, range_lines = scan_citations()
    ordinals = scan_ordinals()
    reg_nums = [d["n"] for d in DEFECTS]
    dupes = sorted({n for n in reg_nums if reg_nums.count(n) > 1})
    missing = sorted(n for n in cited if n not in reg_nums)
    never_cited = sorted(n for n in reg_nums if n not in cited)
    contiguous = reg_nums == list(range(1, len(reg_nums) + 1))
    ok = not dupes and not missing and contiguous
    return dict(
        ok=ok,
        registry_rows=len(reg_nums),
        contiguous=contiguous,
        duplicate_rows=dupes,
        distinct_numbers_cited=len(cited),
        mention_lines=mention_lines,
        range_citations=range_lines,
        cited_not_in_registry=missing,
        registry_never_cited_numerically=never_cited,
        ordinal_hits={k: sorted(set(v)) for k, v in sorted(ordinals.items())},
        per_number={n: sum(cited.get(n, {}).values()) for n in reg_nums},
    )


# --------------------------------------------------------------------------
# Coverage statistics
# --------------------------------------------------------------------------

def coverage():
    stages: dict[str, int] = {REG: 0, P0: 0, PH: 0, UN: 0}
    hist: dict[str, int] = {REG: 0, P0: 0, PH: 0, UN: 0}
    improved = 0
    same = 0
    regressed = 0
    per_era: dict[str, int] = {}
    per_family: dict[str, int] = {}
    for d in DEFECTS:
        stages[d["today_stage"]] += 1
        hist[d["hist_stage"]] += 1
        per_era[d["era"]] = per_era.get(d["era"], 0) + 1
        per_family[d["family"]] = per_family.get(d["family"], 0) + 1
        delta = STAGE_ORDER[d["hist_stage"]] - STAGE_ORDER[d["today_stage"]]
        if delta > 0:
            improved += 1
        elif delta == 0:
            same += 1
        else:
            regressed += 1
    return dict(today=stages, historical=hist, improved=improved, same=same,
                regressed=regressed, per_era=per_era, per_family=per_family,
                covered=len(DEFECTS) - stages[UN])


# --------------------------------------------------------------------------
# Emit the registry document
# --------------------------------------------------------------------------

def emit_registry(g0r, cov) -> str:
    out: list[str] = []
    w = out.append
    w("# SUICA Defect Registry — every recorded planner registration defect (#1-#41)")
    w("")
    w("Compiled by D5 (`scripts/run_suica_d5_rule_replay.py`), registered in")
    w("`docs/SUICA_DEFENSE_PHASE_PLAN.md` section D5 (commit eb972ea, BEFORE run).")
    w("This file is GENERATED — edit the DEFECTS table in the harness, not this document.")
    w("")
    w("**Numbering.** The corpus numbers defects `#N` from #9 onward. The eight")
    w("earlier defects (the F/G/H/J-line era) are recorded ORDINALLY — 'the second")
    w("registration defect of this kind', 'Fifth planner registration defect',")
    w("'Eighth planner defect' — and by the rule each paid for. **#1-#8 are assigned")
    w("here in chronological order**, and the assignment is not free invention: the")
    w("record that opens the numbered era (`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`,")
    w("M4-J2) enumerates its predecessors as 'The first seven were defects in RULES —")
    w("aggregation, power, channel, materiality form, grain, winner definition, graded")
    w("levels', which fixes #1-#7 in order and makes the J2 evidence defect #8. The next")
    w("defect is recorded as 'ninth in the program's account', which closes the seam.")
    w("")
    w("**Stage vocabulary** (used by the replay in")
    w("`reports/SUICA_D5_RULE_REPLAY_REPORT.md`): REGISTRATION-TIME < PART-0 <")
    w("POST-HOC < UNCOVERED.")
    w("")
    w(f"**Rows:** {len(DEFECTS)}. **G0R:** {'PASS' if g0r['ok'] else 'FAIL'} — ")
    w(f"{g0r['distinct_numbers_cited']} distinct defect numbers cited across the tracked")
    w(f"corpus, {g0r['mention_lines']} citing lines; every cited number resolves to exactly")
    w("one row.")
    w("")
    w("## The registry")
    w("")
    w("| # | era / leg | where recorded | one-line description | rule it paid for | family |")
    w("|---|---|---|---|---|---|")
    for d in DEFECTS:
        paid = d["rule_paid"] if d["rule_paid"] != "none" else "none"
        w("| #{n} | {era} / {leg} | `{where}` | {desc} | {paid} | {fam} |".format(
            n=d["n"], era=d["era"], leg=d["leg"], where=d["where"],
            desc=d["desc"].replace("|", "\\|"), paid=paid, fam=d["family"]))
    w("")
    w("## Family counts")
    w("")
    w("| family | n | defects |")
    w("|---|---|---|")
    fams: dict[str, list[int]] = {}
    for d in DEFECTS:
        fams.setdefault(d["family"], []).append(d["n"])
    for fam in sorted(fams, key=lambda f: (-len(fams[f]), f)):
        w(f"| {fam} | {len(fams[fam])} | " + ", ".join(f"#{n}" for n in fams[fam]) + " |")
    w("")
    w("## The rule set the defects bought (1-21)")
    w("")
    w("| rule | paid for by | one line | origin |")
    w("|---|---|---|---|")
    for k in sorted(RULES):
        r = RULES[k]
        w(f"| {k} | {r['paid_by']} | {r['text']} | `{r['origin']}` |")
    w("")
    w("## Conventions in force (unnumbered, binding on dispatched agents)")
    w("")
    for name, text in CONVENTIONS:
        w(f"- **{name}** — {text}")
    w("")
    w("## Provenance")
    w("")
    w("Sources read (document space only, gate G1R): the M4-D and M4-G plan docs")
    w("(#1-#8 era), the M4-K plan doc (#9-#26), the M4-L plan doc (#27-#38), the")
    w("defense phase plan (#39-#41), the M4-F and M4-G line syntheses,")
    w("`docs/SUICA_DISPLACEMENT_PROBLEM_RESOLVED.md`,")
    w("`docs/SUICA_IDENTITY_THEORY_V1.md` appendices, `docs/CLAIMS_LEDGER.md`, and the")
    w("leg reports under `reports/`. No `results/` tree was opened.")
    w("")
    return "\n".join(out) + "\n"


def main() -> int:
    assert not any(m.startswith("suica") for m in sys.modules), "G1R: suica_core must not be imported"
    g0r = gate_g0r()
    cov = coverage()

    print("=" * 72)
    print("SUICA D5 — rule replay harness")
    print("=" * 72)
    print(f"registry rows              : {g0r['registry_rows']} (contiguous 1..N: {g0r['contiguous']})")
    print(f"distinct numbers cited     : {g0r['distinct_numbers_cited']}")
    print(f"citing lines               : {g0r['mention_lines']}")
    print(f"range citations expanded   : {len(g0r['range_citations'])}")
    print(f"cited but not in registry  : {g0r['cited_not_in_registry'] or 'none'}")
    print(f"registry rows never cited numerically: {g0r['registry_never_cited_numerically'] or 'none'}")
    print(f"duplicate registry rows    : {g0r['duplicate_rows'] or 'none'}")
    print(f"G0R                        : {'PASS' if g0r['ok'] else 'FAIL'}")
    print("-" * 72)
    print("pre-#9 ordinal anchors found:")
    for n, hits in g0r["ordinal_hits"].items():
        print(f"  #{n}: {', '.join(hits)}")
    print("-" * 72)
    print("citations per defect number:")
    row = []
    for n in sorted(g0r["per_number"]):
        row.append(f"#{n}={g0r['per_number'][n]}")
        if len(row) == 8:
            print("  " + "  ".join(row))
            row = []
    if row:
        print("  " + "  ".join(row))
    print("-" * 72)
    print("TODAY's catch stage:")
    for k in (REG, P0, PH, UN):
        print(f"  {k:<20}: {cov['today'][k]}")
    print("HISTORICAL catch stage:")
    for k in (REG, P0, PH, UN):
        print(f"  {k:<20}: {cov['historical'][k]}")
    print(f"improved / same / later    : {cov['improved']} / {cov['same']} / {cov['regressed']}")
    print(f"covered (non-UNCOVERED)    : {cov['covered']}/{len(DEFECTS)}")
    print("per era: " + ", ".join(f"{k}={v}" for k, v in sorted(cov["per_era"].items())))
    print("-" * 72)

    text = emit_registry(g0r, cov)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote {os.path.relpath(REGISTRY_PATH, REPO)} ({len(text)} bytes)")
    print(f"elapsed {time.time() - _T0:.2f} s")
    assert not any(m.startswith("suica") for m in sys.modules), "G1R: suica_core must not be imported"
    return 0 if g0r["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
