# SUICA M4-N4 — the target-2 forensic — **ATTRIBUTED_DISCREPANCY**

**Outcome: ATTRIBUTED_DISCREPANCY (routing cell 4).** Artifact-space; **no fresh
worlds, no seal**. The question was where M3's one closure miss lives: the K2e
9-pair refit published 0.7145934082034173 where the winner law, run through the same
pipeline, retrodicts 0.7490807810533479 — a gap of -0.03448737284993053 against a 0.03
point-tolerance.

**The forensic answer is not the one the routing anticipated.** The gap
decomposes as registered, and by magnitude H-c MICRO-DISCREPANCY dominates — but the same
executed arithmetic shows the gap is **-1.3663541854840218 standard errors** of the
pipeline's own estimator, and that M3's applied tolerance was only 1.1885690957930772 SE
wide. The miss was typed at a precision the estimator cannot deliver.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md` BEFORE run (commit 38b7614). Every
number below is generated from artifacts by code (rule 24); none is hand-typed.

---

## 1. G0n4 — the citation chain

The published target's pinned source, restated as the registration requires:

- **Pinned at:** `results/m4_m3_tax_curve/part0.json -> G0m3 -> '(iv) retrodiction targets' -> targets -> '2'`
- **Source path:** `results/m4_k2e_double_matching/decision.json:kappa_refit_9pairs.kappa (negated)`
- **Pipeline:** OLS through the origin of D on dvar over 9 pairs; kappa = -slope

| clause | registration / expected | persisted / recomputed | bit-exact |
|---|---|---|---|
| published target (M3 G0m3(iv) pinned) | 0.7145934082034173 | 0.7145934082034173 | True |
| same value at K2e, negated | 0.7145934082034173 | 0.7145934082034173 | True |
| source path as pinned | results/m4_k2e_double_matching/decision.json:kappa_refit_9pairs.kappa (negated) | results/m4_k2e_double_matching/decision.json:kappa_refit_9pairs.kappa (negated) | True |
| pipeline as pinned | OLS through the origin of D on dvar over 9 pairs; kappa = -slope | OLS through the origin of D on dvar over 9 pairs; kappa = -slope | True |
| M3's predicted | 0.7490807810533479 | 0.7490807810533479 | True |
| M3's delta | 0.03448737284993053 | 0.03448737284993053 | True |
| M3 HIT flag | False | False | True |
| A-quad theta | [0.21247398265278816, 0.9601680204204508, 1.562877770472943] | [0.21247398265278816, 0.9601680204204508, 1.562877770472943] | True |
| **published REPRODUCED by this harness** | 0.7145934082034173 | 0.7145934082034173 | **True** |
| **M3's prediction REPRODUCED (law fields through the pipeline)** | 0.7490807810533479 | 0.7490807810533479 | **True** |
| all 9 pair rows round-trip | True | True | True |

Both headline aggregates reproduce **bit-exactly** from the persisted pair
artifacts under RN-N4-1's pinned arithmetic — the published κ and M3's own
law-through-pipeline prediction. That is the whole basis for trusting everything
downstream.

## 2. The 9 pairs

| pair | arm a | arm b | V_a | V_b | V-bar | dvar | D | dvar bit-exact | D round-trip | species carrier | participates |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | K2c:P1a | K2c:P1b | 0.03276383049256658 | 0.026213597046502654 | 0.029488713769534616 | 0.0065502334460639244 | -0.0033349254353831808 | True | True | K2c | True |
| P2 | K2c:P2a | K2c:P2b | 0.0878023875209765 | 0.0732654021912562 | 0.08053389485611634 | 0.014536985329720295 | -0.012167516605861444 | True | True | K2c | True |
| P3 | K2c:P3a | K2c:P3b | 0.1492085286969757 | 0.13077023963353374 | 0.13998938416525472 | 0.01843828906344197 | -0.01355928388620139 | True | True | K2c | True |
| FR-45 | K2d:FR45a | K2d:FR45b | 0.19902623970550914 | 0.1818561904874539 | 0.19044121509648154 | 0.017170049218055233 | -0.009879385607257792 | True | True | K2d | True |
| SP-68 | K2d:SP68slow | K2d:SP68int | 0.0878023875209765 | 0.12810097738765003 | 0.10795168245431326 | -0.040298589866673534 | 0.030350909608369947 | True | True | int: | True |
| SP-56 | K2d:SP56slow | K2d:SP56int | 0.1492085286969757 | 0.18765930200411501 | 0.16843391535054536 | -0.03845077330713931 | 0.027060778175001646 | True | True | int: | True |
| DM-68 | K2e:DM68a | K2e:DM68b | 0.0878023875209765 | 0.08780238752097648 | 0.0878023875209765 | 1.3877787807814457e-17 | 0.006424123811148958 | True | True | K2e | False |
| DM-56 | K2e:DM56a | K2e:DM56b | 0.1492085286969757 | 0.1492085286969757 | 0.1492085286969757 | 0.0 | 0.008917886817207595 | True | True | K2e | False |
| VS-62 | K2e:VS62a | K2e:VS62b | 0.11927529709608865 | 0.10203306885813711 | 0.11065418297711288 | 0.017242228237951546 | -0.010598278269700216 | True | True | K2e | True |

### 2.1 The aggregation rule, found exactly

| quantity | value |
|---|---|
| aggregation rule found | origin-forced OLS: slope = sum(dvar_i * D_i) / sum(dvar_i^2), i.e. a dvar^2-WEIGHTED MEAN of the per-pair slopes D_i/dvar_i |
| exact form as executed by K2e | float((x9 @ y9) / (x9 @ x9)) |
| participating pairs | P1, P2, P3, FR-45, SP-68, SP-56, VS-62 |
| structurally inert pairs (dvar = 0) | DM-68, DM-56 |
| top-2 weighted pairs | SP-68, SP-56 |
| **their combined weight** | **72.34%** |
| identity | gap = sum_i w_i * gap_i exactly (origin-forced slope is a dvar^2-weighted mean of per-pair slopes) |
| identity residual | -2.0816681711721685e-16 |

The pipeline is an origin-forced OLS, and an origin-forced slope is
**algebraically a dvar²-weighted mean of the per-pair slopes**
`D_i/dvar_i`. Two consequences follow immediately, and both matter:

1. **The "9-pair refit" is arithmetically a 7-pair refit.** DM-68, DM-56
   sit at dvar = 0 by construction (V_a = V_b), so they contribute exactly
   nothing to both the numerator and the denominator. K2e says so itself and
   declines to define their per-pair κ. They are reported, not hidden.
2. **Two pairs carry 72.339099489729% of the weight** — SP-68, SP-56 — because weight goes
   as dvar² and their |dvar| is roughly 2.5× the rest.

This yields an exact identity the whole decomposition rests on:
gap = Σ wᵢ·gapᵢ, reproduced to -2.0816681711721685e-16.

## 3. Per-pair contributions

| pair | V-bar | weight (dvar^2) | weight % | published contribution kappa_i | law-predicted contribution kappa0 - kappa2*V-bar | gap_i | w_i * gap_i |
|---|---|---|---|---|---|---|---|
| P1 | 0.029488713769534616 | 4.290555819793447e-05 | 1.00% | 0.5091307756958124 | 0.9140807651902058 | -0.4049499894943933 | -0.00405121126522561 |
| P2 | 0.08053389485611634 | 0.0002113239424765031 | 4.93% | 0.8370041194844873 | 0.8343033863802213 | 0.0027007331042659954 | 0.0001330761767805082 |
| P3 | 0.13998938416525472 | 0.0003399705035870438 | 7.93% | 0.7353873149263996 | 0.7413817238063771 | -0.005994408879977486 | -0.00047517933413946577 |
| FR-45 | 0.19044121509648154 | 0.00029481059015043916 | 6.87% | 0.5753848158378652 | 0.6625316787643035 | -0.08714686292643836 | -0.005990523572818397 |
| SP-68 | 0.10795168245431326 | 0.0016239763452423628 | 37.87% | 0.7531506613205291 | 0.7914527356274506 | -0.03830207430692145 | -0.014503470523961197 |
| SP-56 | 0.16843391535054536 | 0.0014784619679170166 | 34.47% | 0.7037772155801393 | 0.696926398325362 | 0.006850817254777319 | 0.002361687784092786 |
| DM-68 | 0.0878023875209765 | 1.925929944387236e-34 | 0.00% | — | 0.8229436207694657 | — | 0.0 |
| DM-56 | 0.1492085286969757 | 0.0 | 0.00% | — | 0.7269733277549733 | — | 0.0 |
| VS-62 | 0.11065418297711288 | 0.0002972944346096137 | 6.93% | 0.6146698746495273 | 0.7872290576356755 | -0.17255918298614825 | -0.011961752114659366 |
| **aggregate** | weighted mean V-bar | — | 100.00% | **0.7145934082034173** | **0.7490807810533479** | **-0.03448737284993053** | -0.03448737284993074 |

## 4. The decomposition

| component | definition | amount | signed % of gap | magnitude share |
|---|---|---|---|---|
| H-a WEIGHTING | pipeline-weighted gap minus uniform-weighted gap over the participating pairs -- the law's per-pair secants re-aggregated under the pipeline's own weights vs uniform | 0.0654270511836174 | -189.71% | 39.57% |
| H-b SPECIES | the int:-species pairs' share of the uniform-weighted gap | -0.0044930367217348765 | 13.03% | 2.72% |
| H-c MICRO-DISCREPANCY | the residual after H-a and H-b -- the non-species pairs' share of the uniform-weighted gap | -0.09542138731181306 | 276.68% | 57.71% |
| **sum (exact additive identity)** | H-a + H-b + H-c | **-0.03448737284993054** | 100.00% | equals the gap to 6.938893903907228e-18 |
| **dominant by magnitude** | — | **H-c MICRO-DISCREPANCY** | — | — |

**H-a WEIGHTING = 0.0654270511836174.** Re-aggregating the same per-pair gaps under uniform
weights instead of the pipeline's own gives -0.09991442403354793 — nearly three times
the published miss. So the weighting is doing a great deal of work, and it is
working in the direction of making the closure look **better**, not worse: the
two heavily-weighted pairs happen to sit close to the law, while the pairs that
miss badly carry almost no weight.

**H-b SPECIES = -0.0044930367217348765**, the smallest component by magnitude (2.717428712809997%). The
registration's literal leave-species-out quantification agrees on direction and
sharpens it:

| quantity | value |
|---|---|
| pairs dropped | SP-68, SP-56 |
| pairs kept | 7 |
| published kappa without the species pairs | 0.6752909215512382 |
| law kappa without the species pairs | 0.7560749513472494 |
| gap without the species pairs | -0.08078402979601129 |
| gap with them (the published gap) | -0.03448737284993053 |
| **shift caused by dropping them** | **-0.04629665694608076** |
| reading | dropping the two int: pairs makes the miss LARGER, so the species pairs MASK the gap rather than cause it |

Dropping the two `int:` pairs moves the gap to -0.08078402979601129 — a shift of
-0.04629665694608076. **The species pairs mask the miss rather than cause it.**

**H-c MICRO-DISCREPANCY = -0.09542138731181306**, the residual after H-a and H-b and the
largest by magnitude (57.71170674900731%), split by pair V̄ as registered:

| quantity | value |
|---|---|
| split at the median V-bar of the non-species pairs | 0.11065418297711288 |
| low-V-bar pairs | P1, P2, VS-62 |
| low-V-bar amount | -0.08211549133946794 |
| high-V-bar pairs | P3, FR-45 |
| high-V-bar amount | -0.013305895972345121 |
| lowest-V-bar pair | P1 |
| its gap | -0.4049499894943933 |

## 5. Why the residual is not a discrepancy

The registration's decomposition presupposes that the gap is a signal to be
attributed. Before accepting that, the arithmetic of the estimator itself
(RN-N4-5, pinned before any component was read):

| quantity | value |
|---|---|
| residual sigma (K2e's own origin-forced residuals, participants, ddof=1) | 0.001652958116203901 |
| **SE of the aggregate kappa** | **0.025240434154130843** |
| the gap | -0.03448737284993053 |
| **the gap in SE** | **-1.3664** |
| M3's applied point-tolerance | 0.03 |
| **the tolerance in SE** | **1.1886** |
| chi2 of per-pair gaps | 7.536898714784121 |
| chi2 degrees of freedom | 7 |
| largest \|z\| over pairs | 1.7999880265777972 |
| at pair | VS-62 |
| reading | the applied point-tolerance is smaller than the estimator's own standard error, so the miss is inside the pipeline's noise |

The pipeline is a regression; it has a standard error. The per-pair κ of a pair
with small |dvar| is a ratio `D/dvar` whose noise scales as σ/|dvar|, so pairs
with small |dvar| have wildly noisy per-pair κ — and those are exactly the pairs
carrying the large gaps.

| pair | V-bar | \|dvar\| | weight % | gap_i | SE_i = sigma/\|dvar\| | z |
|---|---|---|---|---|---|---|
| P1 | 0.029488713769534616 | 0.0065502334460639244 | 1.00% | -0.4049499894943933 | 0.25235102379399527 | -1.6047 |
| P2 | 0.08053389485611634 | 0.014536985329720295 | 4.93% | 0.0027007331042659954 | 0.11370707741064395 | 0.0238 |
| P3 | 0.13998938416525472 | 0.01843828906344197 | 7.93% | -0.005994408879977486 | 0.08964812898400969 | -0.0669 |
| FR-45 | 0.19044121509648154 | 0.017170049218055233 | 6.87% | -0.08714686292643836 | 0.09626985311525645 | -0.9052 |
| SP-68 | 0.10795168245431326 | 0.040298589866673534 | 37.87% | -0.03830207430692145 | 0.04101776567549025 | -0.9338 |
| SP-56 | 0.16843391535054536 | 0.03845077330713931 | 34.47% | 0.006850817254777319 | 0.04298894336923491 | 0.1594 |
| VS-62 | 0.11065418297711288 | 0.017242228237951546 | 6.93% | -0.17255918298614825 | 0.0958668504669023 | -1.8000 |

- The aggregate gap is **-1.3663541854840218 SE**. Not significant.
- χ² = 7.536898714784121 on 7 pairs — almost exactly its expectation. The
  per-pair gaps are collectively indistinguishable from noise.
- The largest single |z| is 1.7999880265777972 at VS-62.
- M3's point-tolerance of 0.03 is **1.1885690957930772 SE** wide.

**The dvar²-weighting is not an artifact — it is the correct estimator.** If D
carries homoskedastic noise then Var(Dᵢ/dvarᵢ) = σ²/dvarᵢ², so weights ∝ dvarᵢ²
are exactly inverse-variance weights. H-a is large precisely because the
pipeline is doing the statistically right thing and the uniform comparator is
doing the wrong one. Read that way, H-a is not a defect in the closure; it is
the closure's estimator behaving correctly, and the "attribution" is an artifact
of comparing it against an inferior weighting.

## 6. The N1b direction check

H-c's registered motivation was N1b's low-V̄ residual. It does not survive
contact:

| quantity | value |
|---|---|
| N1b's LO residual | 0.03994777373059455 |
| N1b's direction | measured response tax ABOVE the level curve |
| N4's lowest-V-bar pair | P1 |
| its V-bar | 0.029488713769534616 |
| its gap | -0.4049499894943933 |
| N4's direction | measured level tax BELOW the law |
| **directions agree** | **False** |
| reading | H-c's low-Vbar discrepancy runs OPPOSITE in sign to N1b's LO residual, so it does NOT harden that lean |

N1b's LO residual had the measured response tax running **above** the level
curve. N4's lowest-V̄ pair (P1) has the measured level tax running
**below** the law, gap -0.4049499894943933. The directions are **opposite**
(False), so cell 4's stated consequence — "the LO whisper hardens" — is
**not supported by the arithmetic that routes there**. Reported as the leg's
central caution.

## 7. Verdict, under both readings

RN-N4-4 pins the accounting before any component was read, because the
registration leaves two things open: H-c is *defined* as the residual, so the
three components are exhaustive and the ≥80% bar cannot fail; and the components
take opposite signs, so signed shares exceed 100%.

| reading | verdict | slug | routes | why |
|---|---|---|---|---|
| literal (registration's own component set; H-c is named) | ATTRIBUTED | ATTRIBUTED_DISCREPANCY | True | H-c is defined as the residual, so the three components sum to the gap by construction and the bar cannot fail (RN-N4-4a) |
| mechanistic (only H-a and H-b can attribute; a residual explains nothing) | NOT ATTRIBUTED | UNATTRIBUTED | False | the named mechanisms leave a residual whose magnitude is 277% of the gap -- more unexplained than the gap itself |

The literal reading routes, and it gives ATTRIBUTED_DISCREPANCY at cell 4. The
mechanistic reading — that a residual explains nothing, so only H-a and H-b can
attribute — leaves 276.6849992518501% of the gap unexplained and would give
UNATTRIBUTED. Both are reported; neither is hidden behind the other.

### Does the closure upgrade?

**No.** Cell 2 is the only cell carrying the closure upgrade to explained-6/6,
and this leg routed to cell 4 (False). But the honest reason the
closure should not be upgraded on this evidence is not the routing — it is that
there is nothing to explain: a -1.3663541854840218-SE deviation against a tolerance
narrower than one SE is a tolerance-calibration fact, and re-typing that target
is the planner's call, not the executor's.

## 8. Routing

| # | condition | outcome |
|---|---|---|
| 1 | any G0n4 mismatch | STOP (citation defect) |
| 2 | ATTRIBUTED, dominant H-a | ATTRIBUTED_WEIGHTING -- the closure's miss is an aggregation artifact; the closure upgrades to explained-6/6 by dated note |
| 3 | ATTRIBUTED, dominant H-b | ATTRIBUTED_SPECIES -- the species question re-enters (K2d lineage); named for any successor |
| 4 | ATTRIBUTED, dominant H-c | **ATTRIBUTED_DISCREPANCY -- the LO whisper hardens; theory note; a micro-discrepancy leg becomes registrable**  <-- THIS LEG |
| 5 | < 80% attributed | UNATTRIBUTED -- the miss stands as measured; no upgrade |

## 9. Gates

| gate | PASS | detail |
|---|---|---|
| G0n4 | True | published target, M3's prediction and all 9 pairs bit-exact at their persisted sources; both headline aggregates reproduced bit-exactly |
| G1n4 | True | executed arithmetic only (rule 30); every component computed by code from persisted artifacts |
| G2n4 | True | no fresh world generated, nothing sealed |
| G3n4 | True | both verdict readings computed and reported (RN-N4-4); the literal one routes |

## 10. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G0n4 | every cited object bit-exact at its persisted source | — | one-sided |
| L-1n4 | ATTRIBUTED | 0.6 | one-sided |
| L-2n4 | dominant = H-a / H-b / H-c | 0.45 / 0.30 / 0.25 | categorical |

## 11. Pinned readings

| note | pinned reading |
|---|---|
| RN-N4-1 | every aggregation goes through K2e's own `(x @ y) / (x @ x)` form on arrays in K2e's pair order; a naive Python sum differs in the last 1-2 ULP. Both headline values reproduce BIT-EXACTLY under this rule |
| RN-N4-2 | D is oriented a-minus-b matching dvar = V_a - V_b; c cancels in every difference and a quadratic's secant equals its midpoint derivative exactly, so the law's per-pair kappa is kappa0 - kappa2*Vbar with no approximation; the aggregate still runs the law FIELDS through the pipeline, which reproduces M3's prediction bit-exactly |
| RN-N4-3 | pairs at dvar = 0 carry exactly zero weight in an origin-forced slope (K2e says so and declines to define their per-pair kappa); the per-pair and uniform-weight arithmetic runs over \|dvar\| > 1e-12, the aggregate over all 9. The '9-pair refit' is arithmetically a SEVEN-pair refit |
| RN-N4-4 | H-c is defined as the residual, so the three components are exhaustive and the >=80% test cannot fail -- the discriminating content is which dominates. Components take opposite signs, so 'dominant' is decided on MAGNITUDE share \|H\|/sum\|H\|. Both verdict readings are reported: literal (all three named -> ATTRIBUTED) and mechanistic (a residual explains nothing -> UNATTRIBUTED) |
| RN-N4-5 | the pipeline is a regression and therefore has a standard error, and a per-pair kappa at small \|dvar\| has noise sigma/\|dvar\|; this arithmetic is computed and reported because it decides whether the gap is a discrepancy at all, but it routes nothing |

## 12. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine and the only `pandas` present belongs to CPython 3.9.6,
   which cannot import the machinery. A CPython 3.12.12 venv was built
   outside the repo from `requirements-lock-main.txt` verbatim and pinned.
   Resolved BEFORE any hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (summation order; before any component).** A naive Python sum of the
   same nine terms reproduces the published κ only to the last 1–2 ULP. K2e's
   exact form is `float((x9 @ y9) / (x9 @ x9))` on arrays in its own pair order;
   pinning that (RN-N4-1) makes both headline aggregates bit-exact. Found and
   pinned BEFORE any decomposition number existed. Without it this leg would
   have opened with a spurious citation mismatch.

## 13. Registration-defect candidates

1. **The ≥80% bar cannot fail** (RN-N4-4a). H-c is defined as "the residual
   after H-a and H-b", so the three components sum to the gap by construction
   and 100% is always attributed. The bar carries no information; only the
   dominance question does. Non-blocking — pinned and both readings reported.
2. **No noise floor was declared.** The decomposition presupposes the gap is
   signal. The estimator's SE (0.025240434154130843) is computable from persisted
   artifacts and is **larger than the 0.03 tolerance the target was typed
   against**; the gap is -1.3663541854840218 SE. A forensic registration on a regression
   output should declare, before the components, whether the quantity is
   distinguishable from zero. This is the #43/#44/#51 genus again: a
   gate-consumed quantity that was computable at registration and not computed.
3. **Cell 4's stated consequence is contradicted by the arithmetic that reaches
   it** (§6): the low-V̄ discrepancy runs opposite in sign to the N1b lean whose
   hardening the cell prescribes.

## 14. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |

## 15. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 30 | 0.010 |
| decompose | 30 | 0.000 |
| finalize | 15 | 0.000 |
| report | 15 | (this stage) |

---

*Artifacts: `results/m4_n4_target2_forensic/` (gitignored) — `part0.json`,
`decomposition.json`, `per_pair.csv`, `decision.json`, `prose_facts.json`,
`report_tables.md`, `run_log.jsonl`. Harness:
`scripts/run_suica_m4_n4_target2_forensic.py`.*
