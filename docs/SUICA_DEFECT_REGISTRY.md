# SUICA Defect Registry — every recorded planner registration defect (#1-#41)

Compiled by D5 (`scripts/run_suica_d5_rule_replay.py`), registered in
`docs/SUICA_DEFENSE_PHASE_PLAN.md` section D5 (commit eb972ea, BEFORE run).
This file is GENERATED — edit the DEFECTS table in the harness, not this document.

**Numbering.** The corpus numbers defects `#N` from #9 onward. The eight
earlier defects (the F/G/H/J-line era) are recorded ORDINALLY — 'the second
registration defect of this kind', 'Fifth planner registration defect',
'Eighth planner defect' — and by the rule each paid for. **#1-#8 are assigned
here in chronological order**, and the assignment is not free invention: the
record that opens the numbered era (`docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md`,
M4-J2) enumerates its predecessors as 'The first seven were defects in RULES —
aggregation, power, channel, materiality form, grain, winner definition, graded
levels', which fixes #1-#7 in order and makes the J2 evidence defect #8. The next
defect is recorded as 'ninth in the program's account', which closes the seam.

**Stage vocabulary** (used by the replay in
`reports/SUICA_D5_RULE_REPLAY_REPORT.md`): REGISTRATION-TIME < PART-0 <
POST-HOC < UNCOVERED.

**Rows:** 41. **G0R:** PASS — 
41 distinct defect numbers cited across the tracked
corpus, 118 citing lines; every cited number resolves to exactly
one row.

## The registry

| # | era / leg | where recorded | one-line description | rule it paid for | family |
|---|---|---|---|---|---|
| #1 | F/G-line (pre-#9) / M4-F4 | `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F4 outcome ~L1120-1131` | G0's designed-null gate text mixed a per-cell rule with a trend rule; multiplicity unstated, so the reading was chosen after the numbers. | 1 | aggregation |
| #2 | F/G-line (pre-#9) / M4-F6 | `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F6 adjudication ~L1485-1502` | Base scale left free and no power statement required, so a null was measured at the target's noise floor (CI half-width ~ the quantity itself). | 2 | power |
| #3 | F/G-line (pre-#9) / M4-F7 | `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F7 adjudication ~L1665-1685` | A design dimension was economized away without checking which of its values carried the causal channel — justified by citing the arm that was in fact the underpowered one. | 3 | channel-liveness |
| #4 | F/G-line (pre-#9) / M4-F8 | `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F8 adjudication ~L1830-1850` | A gate written as a nil-significance test on a residual nonzero by construction (phi^41 = 1.06e-4), so its failure probability grew with sample size; voided a leg on effects 2-3 orders larger. | 4 | materiality |
| #5 | F/G-line (pre-#9) / M4-G3 | `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-G3 adjudication ~L617-622` | G0 required a pre-stated MDE but not a GRAIN, so the line's default (n=6-8 worlds) was inherited though >4x under the bar while the author grain (n~745) was available. | 5 | grain |
| #6 | F/G-line (pre-#9) / M4-H2 | `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-H2 adjudication ~L1749-1768` | The 'winner' was defined as the arm with the largest target reduction, then safety tested there — target-only selection systematically picks the most cosmetic arm (and did). | 6 | winner-definition |
| #7 | F/G-line (pre-#9) / M4-H3 | `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-H3 adjudication ~L1948-1961` | The joint winner rule was still target-priority within the qualifying set, so it picked the most aggressive qualifying arm and hid the arm that cleared the STRONGER safety level. | 7 | graded-safety |
| #8 | F/G-line (pre-#9) / M4-J2 | `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-J2 adjudication ~L2901-2910` | A factual claim used to motivate a lean was not verified against persisted data at full precision before the registration was committed — so the control tested the wrong thing. | 8 | fact-verification |
| #9 | K-line / M4-K1 | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1 adjudication ~L284-296` | The registration underdetermined R-abs's norm convention: T3(c)'s one-common-norm hypothesis and the deployable per-half estimated norms are inequivalent readers, and one name covered two. | 9 | instrument-pinning |
| #10 | K-line / M4-K1 (found in K1b) | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication ~L572-580` | The registration asserted 'the generator exposes an explicit occasion-mean channel (w_mu = 0.15)'. FALSE: w_mu weights the AUTHOR mean channel (f2:178) — a code claim cited from a knob NAME. | 12 (with K1c's ambiguities) | fact-verification |
| #11 | K-line / M4-K1b | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication ~L581-586` | The registered decomposition was degenerate by construction at the registered knob (S_frame == 1 as an arithmetic identity of the generator at kappa=1.0). | 10 | degeneracy |
| #12 | K-line / M4-K1b | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication ~L587-590` | G4b demanded a CI-excludes-zero clause at n=3 that the anchor's own sd makes arithmetically unsatisfiable. | 11 | satisfiability |
| #13 | K-line / M4-K1c | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1c adjudication ~L853-859` | G2c's stated rationale ('sqrt(1-kappa) > 0 keeps the author AR state in the panel, so common-removal must not collapse the contrast') is a non-sequitur: the retained state is design-INVARIANT. | none (rule 10 caught it) | degeneracy |
| #14 | K-line / M4-K1c' | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1c' adjudication ~L1130-1136` | G0''s anchor location misstated (decision.json cited for two families that live in gates.json). | none | fact-verification |
| #15 | K-line / M4-K1c' | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1c' adjudication ~L1137-1142` | G3''s 'within 2x' sd clause was TWO-SIDED, so it fails when the fresh variance is SMALLER — an equivalence band that punishes improvement. One-sided (<= 2x) was the intent. | none | clause-direction |
| #16 | K-line / M4-K1d | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1d adjudication ~L1413-1417` | G1d was listed among 'Part 0 gates' though it is unmeasurable before the intact arm exists — a gate assigned to a stage where its inputs do not yet exist. | none | gate-stage-feasibility |
| #17 | K-line / M4-K1d | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1d adjudication ~L1418-1421` | The pivot space had a GAP: P2d covered 'L-1 MISS and gamma DISJOINT' but not 'MISS and OVERLAPPING' — and the measurement sat exactly on that boundary. | 15 (with #21) | partition |
| #18 | K-line / M4-K2a | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2a adjudication ~L1645-1648` | G2a's ACF clause pinned neither CI level nor multiplicity. | none | aggregation |
| #19 | K-line / M4-K2a | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2a adjudication ~L1648-1652` | 'Shares within 1% of design' was ambiguous (absolute vs relative) and, read relatively, UNSATISFIABLE for the common channel at n_occ draws. | none | satisfiability |
| #20 | K-line / M4-K2b | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2b adjudication ~L1934-1946` | The registration compared quantities on two different scales (card attenuation vs field agreement) without pinning the link function — and the branch verdict is link-sensitive. | 14 | link |
| #21 | K-line / M4-K2c | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2c adjudication ~L2217-2228` | The K2c adjudication space was declared partitioned and is not: L-1 (equivalence-within-margin) and L-2 (significance+sign) are independent axes and significant-but-sub-material satisfies both. | 15 (with #17) | partition |
| #22 | K-line / M4-K2d | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2d adjudication ~L2527-2536` | Rule 15 was applied at the CELL level only, not to lean predicates and pivot routing — 8 overlaps + 4 gaps at the lean level, one unrouted cell class at the pivot level. | 16 | partition |
| #23 | K-line / M4-K2e | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2e adjudication ~L2840-2844` | L-SPEC lumped MAT-SIG and SUB-SIG cells while P-SPEC's consequence text presumed the material grade — a rule-7 instance at the ROUTING level. | none | graded-safety |
| #24 | K-line / M4-K2e | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2e adjudication ~L2844-2849` | The registration's premise that K2e's w_int 'exceeds K2a's validated range' was factually WRONG for its own solved shares (0.0857/0.1458 vs ceilings 0.2644/0.2161). | none | fact-verification |
| #25 | K-line / M4-K3 | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K3 adjudication ~L3144-3156` | The UNEQUAL stratum is UNREALIZABLE in this world family at every registered rung (0 pairs at ratio>3 and >2.5; 19 of 1.57M at >2) — F2-family trait latents are one N(0,I_48) draw. | 17 (with #26) | realizability |
| #26 | K-line / M4-K3 | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K3 adjudication ~L3144-3156` | The split-half rank-1 identification task sits at CEILING (0 misses in the pilot), making three leans unscorable as posed. | 17 (with #25) | realizability |
| #27 | L-line / M4-L1 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication ~L306-315` | G2L's mid-band clause and V-1's 0.95 bar are JOINTLY unsatisfiable on the ISO arm because rho_id ties sigma_b to Delta; individually each clause was satisfiable. | 18 | joint-satisfiability |
| #28 | L-line / M4-L1 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication ~L313-315` | V-3(d) was a designed identity (removal == rho_id=0 card at 3.1e-16) — a construction certificate scored as a lean, i.e. a test that cannot fail. | none | degeneracy |
| #29 | L-line / M4-L1 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication ~L315-316` | A floor clause with no registered comparand — the bar named a quantity but nothing to compare it against. | none | instrument-pinning |
| #30 | L-line / M4-L1 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication ~L316-321` | V-3(c)'s bar tests a proposition R2 does not make — an energy threshold standing in for an achieved-ARI claim (oracle projection restored only 13.5%). | 19 | shadow-fidelity |
| #31 | L-line / M4-L2 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L598-608` | W-1's two conditions are jointly unsatisfiable on the Delta axis — the lean's condition set is EMPTY (gap factor 1.571), so the leg 'missed on a window my own conditions made empty'. | 20 (with #32) | empty-set |
| #32 | L-line / M4-L2 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L598-608` | The design clause 'oracle-S floor < 0.005 everywhere' is jointly unsatisfiable with the bracket's low end. | 20 (with #31) | empty-set |
| #33 | L-line / M4-L2 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L593-600` | W-2's bar sat on an ARI where the BBP/spiked-PCA law owns the subspace OVERLAP — a bar on a quantity the theorem does not predict. | none | shadow-fidelity |
| #34 | L-line / M4-L2 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L598-604 (evidence ~L526-528)` | W-4's registration had no clause able to distinguish 'the constant is wrong' from 'the partition is wrong' — the lean's two named alternatives are confounded by design. | none | lean-identifiability |
| #35 | L-line / M4-L2 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication ~L598-604 (evidence ~L500-506)` | W-3's containment clause is unresolvable at eta=0 — 1536 Bernoulli tests against a 3.5e-7 prediction, i.e. the design's quantum is coarser than the predicted effect. | none | precision-budget |
| #36 | L-line / M4-L3 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L3 adjudication ~L730-734, ~L849-855` | X-1's pole clause demanded tolerance ZERO on the same quantity X-2 declares resolvable only to 0.125 — a nil-significance test standing in for an equivalence claim. | none | materiality |
| #37 | L-line / M4-L3 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L3 adjudication ~L773-778, ~L858-866` | Clause (c) has no precision budget: it gets HARDER the better the correction works (CIs sharpened 6-39x), conflating 'the correction is right' with 'the residual is below the resolution the correction creates'. | 21 | precision-budget |
| #38 | L-line / M4-L3 | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L3 anomalies ~L809-814, adjudication ~L878` | Executor-side: the registration says 'regressed on (1-ARI) across cells' without stating the observation grain; the first draft used (cell, world), where per-panel B_cal noise attenuates R^2 from 0.892 to 0.040. | none | grain |
| #39 | defense / D1 | `docs/SUICA_DEFENSE_PHASE_PLAN.md — D1 planner adjudication ~L169-174` | The registration cited kappa at the wrong path AND with the wrong sign convention while building the sealed prediction set. | none | fact-verification |
| #40 | defense / D2 | `docs/SUICA_DEFENSE_PHASE_PLAN.md — D2 planner adjudication ~L342-352; docs/SUICA_IDENTITY_THEORY_V1.md appendix T ~L1204` | Four wrong factual claims in PUBLISHED PROSE (appendix C.1's 'five arms' = four; C.2's '<= 0.0045' vs 0.004512746557818383; K-R1's '0/32 worlds' vs 0/192 arm-worlds; the floor law's 'every reading' vs pooled Spearman 0.985). | none | prose-citation |
| #41 | defense / D3 | `docs/SUICA_DEFENSE_PHASE_PLAN.md — D3 outcome ~L424-430 and adjudication ~L529-534` | The D3 registration's scope arithmetic was wrong twice in one section ('thirteen trees ... the fifteen'); the true scope is 17 trees. | none | prose-citation |

## Family counts

| family | n | defects |
|---|---|---|
| fact-verification | 5 | #8, #10, #14, #24, #39 |
| degeneracy | 3 | #11, #13, #28 |
| partition | 3 | #17, #21, #22 |
| aggregation | 2 | #1, #18 |
| empty-set | 2 | #31, #32 |
| graded-safety | 2 | #7, #23 |
| grain | 2 | #5, #38 |
| instrument-pinning | 2 | #9, #29 |
| materiality | 2 | #4, #36 |
| precision-budget | 2 | #35, #37 |
| prose-citation | 2 | #40, #41 |
| realizability | 2 | #25, #26 |
| satisfiability | 2 | #12, #19 |
| shadow-fidelity | 2 | #30, #33 |
| channel-liveness | 1 | #3 |
| clause-direction | 1 | #15 |
| gate-stage-feasibility | 1 | #16 |
| joint-satisfiability | 1 | #27 |
| lean-identifiability | 1 | #34 |
| link | 1 | #20 |
| power | 1 | #2 |
| winner-definition | 1 | #6 |

## The rule set the defects bought (1-21)

| rule | paid for by | one line | origin |
|---|---|---|---|
| 1 | #1 | Designed-null gates state their aggregation rule (per-cell vs trend) and multiplicity treatment BEFORE the run. | `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F4 outcome/adjudication` |
| 2 | #2 | Every leg pre-states the scale at which its target is measurably non-zero and its minimum detectable effect; a noise-floor null is UNDERPOWERED, not a null. | `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F6 adjudication ('Standing rule added')` |
| 3 | #3 | Verify a non-zero causal channel at every tested parameter value from the generator; a null on an inert knob is VACUOUS. | `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F7 adjudication ('Standing rule added (third)')` |
| 4 | #4 | Every gate bounds MATERIALITY via an equivalence form (CI inside a justified margin) — never nil significance on a known-nonzero quantity. | `docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md — M4-F8 adjudication ('Standing rule added (fourth), and it subsumes the others')` |
| 5 | #5 | Justify the analysis grain for power against the registered bar; do not inherit the line's default grain. | `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-G3 adjudication ('Standing rule (fifth)')` |
| 6 | #6 | Define the winner jointly over target AND safety — the best arm among those passing both — never by the target's extremum. | `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-H2 adjudication ('Standing rule (sixth)')` |
| 7 | #7 | Where the anti-cosmetic check has graded levels, the registration states which level qualifies and the leg reports the best arm at EACH level. | `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-H3 adjudication ('Standing rule (seventh)')` |
| 8 | #8 | Every factual claim cited to motivate a lean is checked against the persisted artifacts at full precision before the registration is committed. | `docs/SUICA_M4_G_OBJECTIVE_REDESIGN_PLAN.md — M4-J2 adjudication ('Eighth planner defect, and a new kind')` |
| 9 | #9 | A registration introducing a constructed instrument pins every convention that changes its hypothesis-relevance, or pre-delegates the choice with an explicit decision rule; an ambiguity found mid-leg is resolved before any hypothesis-relevant number exists and ALL readings are reported. | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1 adjudication (ninth defect)` |
| 10 | #11 | A registered manipulation is derived from generator SOURCE so it preserves the design's defining contrast, and Part 0 proves non-degeneracy before arms. | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication (#10-#12 block)` |
| 11 | #12 | Every registered gate is checked for arithmetic satisfiability under the cited anchor statistics at registration time. | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1b adjudication (#10-#12 block)` |
| 12 | #10 + K1c's two rule-9 ambiguities | Registered manipulations and channels are specified by generator SOURCE OBJECT (file:function/variable), never by knob names or natural-language channel descriptions alone. | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1c adjudication` |
| 13 | none (paid for by L-1's fragility, not by a numbered defect) | Every registered interval clause names its resampling spec (B, seed policy); at adjudication verdict stability is checked at >=10x B, and a clause boundary inside achievable Monte-Carlo error scores BOUNDARY, not HOLD/MISS. | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K1d adjudication` |
| 14 | #20 | When a lean compares quantities across scales or instruments, the registration pins the LINK function and its justification; absent that, the lean is re-designed to be within-instrument. | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2b adjudication` |
| 15 | #17 + #21 | The registered adjudication space is a PARTITION of the outcome space, verified by ENUMERATION at registration time (a truth table with every combination assigned to exactly one named outcome). | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2c adjudication` |
| 16 | #22 | The rule-15 enumeration extends over the FULL adjudication object — cells, lean predicates and pivot routing — as one truth table, every realizable combination routed to exactly one outcome. | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K2d adjudication` |
| 17 | #25 + #26 | Every registered stratum and task carries either a generator-derived realizability argument or a Part-0 realizability check with a pre-declared fallback ladder. | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md — K3 adjudication` |
| 18 | #27 | Rule-11 satisfiability is checked JOINTLY across all clauses sharing generative knobs, not per-clause. | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication` |
| 19 | #30 | Every lean bar is derived from the theorem's OWN quantity and scale, with the registration stating which theorem-quantity the bar shadows; a bar on a different quantity is a defect regardless of outcome. | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L1 adjudication` |
| 20 | #31 + #32 | When the rule-18 joint check finds ANY lean's condition-set empty, the leg STOPS before arms as a registration defect, unless empty-set was pre-declared adjudicable. | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L2 adjudication` |
| 21 | #37 | CI-containment bars on instrument validations carry a registered absolute-error budget; an instrument may not fail validation because its precision exposes a residual smaller than the budget. | `docs/SUICA_M4_L_TYPOLOGY_LINE_PLAN.md — L3 adjudication` |

## Conventions in force (unnumbered, binding on dispatched agents)

- **round-trip parsing** — all artifact re-derivations parse CSV with float_precision='round_trip' (K1c' anomaly 1; pandas 3.0.2's default parser does not round-trip float64)
- **4-world pilots, df-aware** — pilot-sd MDE gates use >=4 pilot worlds or a registered df-based inflation factor (K2d anomaly A-5; standing for all sd-based gates from K2e)
- **Part-0 bit-identity verification** — any bit-identity claim stated in Part 0 is VERIFIED in Part 0, not asserted (K2a anomaly vi)
- **chunked foreground stages** — no background jobs or monitors; foreground chunked stages with explicit timeouts; Part 0 written into the report BEFORE any arm runs
- **aggregation provenance** — every future leg's decision.json aggregates name their computing function (file:line) (D2 adjudication)
- **salt embedding** — every sealed artifact EMBEDS its salt within the sealed bytes, so any later manifest/backup hash stays guess-proof (D3 adjudication)
- **legacy-anchor parser naming** — a bit-exact anchor against a pre-round-trip artifact names the parser that produced the legacy number (K1d)

## Provenance

Sources read (document space only, gate G1R): the M4-D and M4-G plan docs
(#1-#8 era), the M4-K plan doc (#9-#26), the M4-L plan doc (#27-#38), the
defense phase plan (#39-#41), the M4-F and M4-G line syntheses,
`docs/SUICA_DISPLACEMENT_PROBLEM_RESOLVED.md`,
`docs/SUICA_IDENTITY_THEORY_V1.md` appendices, `docs/CLAIMS_LEDGER.md`, and the
leg reports under `reports/`. No `results/` tree was opened.


## Dated additions (2026-08-11 — M-line era; append-only)

| # | era / leg | where recorded | one-line description | rule it paid for | family |
|---|---|---|---|---|---|
| #43 | M-line / M4-M1 | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M1 outcome + planner adjudication` | G1m(d) was deterministic arithmetic from pinned source objects, computable at registration time; the planner did not compute it and extrapolated φ leverage from two published points into a saturating region — the gate was unsatisfiable by construction (infimum 2.496× the bar, proven by the executor's diagnostic). | none (rule-11 violation; bought the planner-arithmetic convention) | satisfiability |
| #44 | M-line / M4-M1 | same | Gates (b)/(c)/(d) shared the `share` knob and pulled in opposite directions; the rule-18 joint check was not run — (b)+(d) jointly empty at ANY admissible shares (best 0.5208 ≥ the 0.30 bar); (c) unknowingly demanded the only two share levels that can ever comply. | 25 | joint-satisfiability |

### Rules addendum (append-only; the table above at "1-21" is unchanged)

| rule | paid for by | one line | origin |
|---|---|---|---|
| 25 | #43 + #44 | Every design-feasibility gate is stated in the quantity the leg's estimand requires (identification width, power, a registered projection); marginal or proxy statistics of the design are REPORTED, never gating. | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M1 planner adjudication (2026-08-11)` |

Convention added (unnumbered, planner-side): when every input to a
registered gate is deterministic arithmetic from pinned source objects,
the planner RUNS the gate before committing the registration and embeds
the computed table in the registration text (M1 adjudication,
2026-08-11).

## Dated additions (2026-08-11, second note — M1b/M1c; append-only)

M1b and M1c completed with ZERO new numbered defects (registrations
survived contact whole; M1b validated rule 25 in both directions).
M1c's one non-blocking candidate — a bounded form winning with its
bound ACTIVE, verdicts saved only by the tie rule's luck — bought a
rule without a defect number, rule-13-style:

| rule | paid for by | one line | origin |
|---|---|---|---|
| 26 | M1c's bounded-winner fragility (no numbered defect) | When a bounded form wins selection with any bound ACTIVE at its optimum, every verdict is co-adjudicated on its unbounded relaxation (or nearest registered unbounded form); disagreement reports SPLIT; bound-activity is itself a reported finding and the active-bound CI is flagged one-sided-by-construction. | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M1c planner adjudication (2026-08-11)` |

## Dated additions (2026-08-11, third note — M1d; append-only)

| # | era / leg | where recorded | one-line description | rule it paid for | family |
|---|---|---|---|---|---|
| #45 | M-line / M4-M1d | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M1d outcome + planner adjudication` | Routing cells 4/5 handed a winning extension to "M2 seals it" with no identification requirement on the sealed parameters; had the residual been quiet, a ridge (q width 2.62) would have been sealed. Non-blocking only because L-4d deferred M2 independently. | 27 | consumption-identification |

| rule | paid for by | one line | origin |
|---|---|---|---|
| 27 | #45 | A route that hands a fitted object to a downstream consumer (seal, adoption, cross-leg comparison) carries an explicit identification budget on every parameter the consumer will quote; selection wins (LOO or otherwise) never alone qualify an object for consumption. | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M1d planner adjudication (2026-08-11)` |

## Dated additions (2026-08-11, fourth note — M1e; append-only)

| # | era / leg | where recorded | one-line description | rule it paid for | family |
|---|---|---|---|---|---|
| #46 | M-line / M4-M1e | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M1e outcome + planner adjudication` | The routing table's cells overlapped (4/5 and 5/6 both reachable) — the rule-15/16 enumeration was not a partition; immaterial only because the overlapping cells shared one route; executor precedence-pin RN-M1E-5 was the in-leg repair. | none (rules 15/16 violated; #43 convention extended: planner mechanically verifies disjoint-and-covering) | partition |
| #47 | M-line / M4-M1e | same | Rule 27's first budget list omitted α_s and λ — parameters any seal would quote; the budget attaches to whatever the consumer quotes, parameters or predictions. | none (rule 27 misapplied at first use; repaired in M2 by budgeting the predictions) | consumption-identification |
| #48 | M-line / M4-M1e | same | The TAX_SHIFT modifier was not conditioned on its host representation being competitive — it fired on the leg's worst model's κ, and unconditioned it would have polluted M3's charter. | 28 | representation-licensing |

| rule | paid for by | one line | origin |
|---|---|---|---|
| 28 | #48 | Cross-leg parameter comparisons (leans or modifiers) are licensed only on representations competitive in the comparing leg (the winner or its tie band); on any other representation the comparison is typed REPRESENTATION-CONDITIONED and adjudicates nothing. | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M1e planner adjudication (2026-08-11)` |

## Dated additions (2026-08-11, fifth note — M2; append-only)

| # | era / leg | where recorded | one-line description | rule it paid for | family |
|---|---|---|---|---|---|
| #49 | M-line / M4-M2 | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M2 outcome + planner adjudication` | G2m2's "non-saturated" predicate was left unpinned while three prior legs carried a conflicting strictly-inside-(0,1) code convention; the two readings route to DIFFERENT outcomes (PREDICTIVE_SCOPED vs UNRESOLVED_SEAL) — the entire leg turned on an unpinned word. Executor's RN-M2-8 (registered text controls; the statistic's null is 0, not its floor) upheld at adjudication. | 29 | predicate-domain |

| rule | paid for by | one line | origin |
|---|---|---|---|
| 29 | #49 | Every regime/sanity gate pins its predicate in the measured statistic's OWN domain (bounds, null, saturation points), named per statistic; any divergence between registered text and an inherited code-form is disclosed and adjudicated before an outcome-relevant consequence. | `docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md — M2 planner adjudication (2026-08-11)` |

## Dated additions (2026-08-11, sixth note — M3; append-only)

M3 closed with **zero registration-defect candidates** — the M-line's
first fully clean leg (planner and executor). The #49 retroactive
check ran mechanically (46 pilot/smoke worlds across 23 persisted
sources): ZERO (0,1)-breaches beyond M2's known case — the latent
convention never bit a published number; #49's retroactive question
is closed. Rules 25, 26, 27, 13 all fired at least once during the
M-line and behaved as written.

## Dated additions (2026-08-11, seventh note — N1; append-only)

| # | era / leg | where recorded | one-line description | rule it paid for | family |
|---|---|---|---|---|---|
| #50 | N-line / M4-N1 | `docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md — N1 outcome + planner adjudication` | Appendix CC.1's V*/A0/c′ (and the registration's A-lin chord) were published at 16-digit precision without executed arithmetic — all three identities jointly consistent with a (κ0, κ2) pair absent from every persisted artifact; caught by G0 with corrected values supplied; zero worlds spent. | 30 | fabricated-precision |
| #51 | N-line / M4-N1 | same | S3's sealed-band width at the registered n (0.391 vs budget 0.35) was computable at registration and never computed; the only escalation ladder was attached to the gate that PASSES (the projection), leaving no path to the success cell — rules 11/18 violated, third of the #43/#44 genus. | none (rules 11/18; #43 convention extended: planner-run covers every gate-consumed quantity incl. persisted-pipeline recomputes; ladders checked against every gate sharing the knob) | joint-satisfiability |

| rule | paid for by | one line | origin |
|---|---|---|---|
| 30 | #50 | Every published derived constant carries EXECUTED provenance — computed by code from persisted inputs at full precision, or quoted expressly as approximate with its precision stated; digits beyond the planner's actual executed arithmetic are a defect regardless of numerical proximity. | `docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md — N1 planner adjudication (2026-08-11)` |

## Dated additions (2026-08-14, eighth note — N1b/N4; append-only)

N1b closed with zero registration-defect candidates (and the
executor's own pre-stamp self-catch, RN-N1B-10, recorded as #50's
mirror). N4's three candidates are all planner defects:

| # | era / leg | where recorded | one-line description | rule it paid for | family |
|---|---|---|---|---|---|
| #52 | N-line / M4-N4 | `docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md — N4 outcome + planner adjudication` | The ≥80% attribution bar could not fail: H-c was defined as the residual, making the decomposition exhaustive by construction — a bar with one reachable side adjudicates nothing. | 31 | bar-reachability |
| #53 | N-line / M4-N4 | same | No noise floor declared though the target-estimator's SE (0.0252) was computable from persisted artifacts at registration and EXCEEDED the meaning of the 0.03 tolerance the target was typed against (1.19 SE) — fourth of the #43/#44/#51 genus; origin case for rule 32; M3's closure re-typed 5 hits / 1 within-noise / 0 discrepant by dated note. | 32 | noise-floor |
| #54 | N-line / M4-N4 | same | Cell 4's consequence clause ("the LO whisper hardens") was not entailed by its condition and was contradicted in sign by the data that reached the cell — consequence voided at adjudication; routing-consequence ENTAILMENT added to the #46 mechanical check. | none (convention) | consequence-entailment |

| rule | paid for by | one line | origin |
|---|---|---|---|
| 31 | #52 | Every registered verdict bar is checked at registration for two-sided reachability — both PASS and FAIL attainable under the registered construction; a residual-defined component never counts toward an attribution or explanation bar. | `docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md — N4 planner adjudication (2026-08-14)` |
| 32 | #53 | A forensic or comparison registration on an estimator's output declares that estimator's own sampling noise as its floor (computed at registration from persisted artifacts); gaps are reported in SE units alongside raw units; a gap within the declared k·SE routes to WITHIN-NOISE, never to attribution or discrepancy. | same |
