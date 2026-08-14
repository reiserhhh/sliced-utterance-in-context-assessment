# SUICA M4-N1 — the response-transport seal — **STOP**

**Outcome: STOP (routing cell 1) — STOP (citation defect).** The leg halted
at **G0n1(ii)** with **3** clauses failing at full precision:
appendix CC identity A0, appendix CC identity V*, appendix CC identity c'. Ladder: none declared -- the registration's text is 'Mismatch -> STOP'. **No seal was issued and no world was ever
drawn** (0 worlds; 0 fresh-world generations across
3 guarded `k2b` instances).

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md` BEFORE run (commit 76060e7);
prospective response-transport seal on K2b's frozen instrument, exploratory, label-free; predictions hashed before any fresh world.

Every number below is generated from artifacts by code (rule 24); none is
hand-typed. Floats are printed at `repr` precision, so a value quoted in the
registration as `0.29489267237567145` appears here as `0.29489267237567146` —
the same IEEE double, shortest-repr.

---

## 1. What stopped the leg

Appendix CC.1 states three identities "at M3's central values":
V\* = κ0/κ2, A0 = κ0²/(2κ2), c′ = c − A0. G0n1(ii) requires them to be
**recomputed from the persisted parameters**, and the registration's response to
a mismatch is unconditional: *"Mismatch → STOP."* They do not recompute.

| failing clause | registration / appendix quotes | recomputed from the persisted parameters | absolute difference |
|---|---|---|---|
| appendix CC identity V* | 0.6143507762088093 | 0.6143589975880801 | 8.221379270811902e-06 |
| appendix CC identity A0 | 0.29489267237567146 | 0.2949439312708197 | 5.125889514823179e-05 |
| appendix CC identity c' | -0.08241868972288328 | -0.08246994861803153 | 5.1258895148245665e-05 |

The gaps are far above floating point: V\* differs by 8.221379270811902e-06, A0 and c′ by
5.125889514823179e-05 and 5.1258895148245665e-05. The recomputation is invariant across four
arithmetic orderings (`k0**2/(2*k2)`, `k0*V*/2`, `k0*(k0/k2)/2`, `0.5*k0*k0/k2`
all give the identical double), and M3's A-quad parameters themselves reproduce
**bit-exactly** from M3's persisted per-world corpus — so the discrepancy is not
in the inputs and not in the arithmetic.

## 2. Diagnosis — one wrong parameter pair, not three wrong identities

CC's three quoted values are **jointly self-consistent with a single
(κ0, κ2) pair** that is not M3's fit:

| quantity | value |
|---|---|
| kappa0 implied by CC's own V* and A0 | 0.9600139978514214 |
| kappa2 implied by CC's own V* and A0 | 1.5626479773912192 |
| that pair reproduces CC's A0 to machine precision | True |
| M3's persisted kappa0 | 0.9601680204204508 |
| M3's persisted kappa2 | 1.562877770472943 |
| difference in kappa0 | -0.00015402256902941058 |
| difference in kappa2 | -0.00022979308172388357 |
| CC's c' uses M3's persisted c bit-exactly | True |
| **corrected V\*** | **0.6143589975880801** |
| **corrected A0** | **0.2949439312708197** |
| **corrected c'** | **-0.08246994861803153** |

Reading: CC's V\* and A0 are exactly the identities evaluated at
κ0 = 0.9600139978514214, κ2 = 1.5626479773912192, which differ from M3's persisted A-quad fit by
-0.00015402256902941058 and -0.00022979308172388357. That pair appears nowhere in `results/m4_m3_tax_curve/`.
Meanwhile c′ = c − A0 uses M3's **persisted c bit-exactly**
(True), so c′'s error is exactly A0's with the sign
flipped and is not an independent mismatch. Rounding M3's persisted parameters
to 3…9 decimals reproduces none of the three. The most economical explanation is
that CC.1's reparametrization constants were evaluated against a κ-pair that did
not survive into M3's committed fit, while c was taken from the committed fit.

**Corrected values, from M3's persisted parameters:**
V\* = `0.6143589975880801`, A0 = `0.2949439312708197`, c′ = `-0.08246994861803153`.

### Why this is worth a STOP even though it changes no sealed number

The three sealed quantities S1, S2, S3 are functions of (κ0, κ2) **directly**
and never of (V\*, A0, c′); CC.2's own sanity values 0.8781 / 0.6671 / 0.2110
reproduce correctly from the persisted parameters (§5). So for *this* leg the
error is inert. It is not inert downstream: the N-line charter registers **N2**
on this very constant — *"is c′ = −0.0824 the frame-carried baseline?"* — and
the corrected c′ is -0.08246994861803153, which changes the charter's own rounded
quote in the 4th decimal. A gate that catches a planner-derivation error before
the next leg inherits it is the gate working, not the gate misfiring.

## 3. What G0n1 *did* verify

Everything else passed. (i) pairs and roots: PASS. (iii) σ_w at source: PASS.

| clause | expected | persisted / recomputed | bit-exact |
|---|---|---|---|
| A-quad c | 0.21247398265278816 | 0.21247398265278816 | True |
| A-quad kappa0 | 0.9601680204204508 | 0.9601680204204508 | True |
| A-quad kappa2 | 1.562877770472943 | 1.562877770472943 | True |
| kappa2 CI | [1.0324533419318935, 2.119753814549891] | [1.0324533419318935, 2.119753814549891] | True |
| closure hits | 5 | 5 | True |
| projection P(quad) | 0.9935 | 0.9935 | True |
| projection P(lin) | 0.0575 | 0.0575 | True |
| LOO A-lin | 0.003599294048156043 | 0.003599294048156043 | True |
| LOO A-quad | 0.001405398973367856 | 0.001405398973367856 | True |
| LOO A-sat | 0.0014509897412261284 | 0.0014509897412261284 | True |
| M3 A-quad recompute from persisted worlds | [0.21247398265278816, 0.9601680204204508, 1.562877770472943] | [0.21247398265278816, 0.9601680204204508, 1.562877770472943] | True |
| **appendix CC V\*** | 0.6143507762088093 | 0.6143589975880801 | **False** |
| **appendix CC A0** | 0.29489267237567146 | 0.2949439312708197 | **False** |
| **appendix CC c'** | -0.08241868972288328 | -0.08246994861803153 | **False** |
| A-sat theta | [-0.27493651728760515, 0.4878776246525967, 0.4983722810248614] | [-0.27493651728760515, 0.4878776246525967, 0.4983722810248614] | True |
| sigma_w | 0.026889438327132725 | 0.026889438327132725 | True |
| A-lin kappa (the CONSTANT truth) -- ANTICIPATED (RN-N1-8; persisted controls, non-blocking) | 0.7729284648259515 | 0.7729279998877195 | differ by 4.649382319144024e-07 |

## 4. The pair design is sound — the roots solved

G0n1(i) passed in full and is reported because it is reusable as-is on
re-dispatch: both roots exist, both brackets straddle, both converge inside
tolerance, ΔV is exact and all four realized r are interior.

| cell | pair | side | share | phi | r | V | r interior |
|---|---|---|---|---|---|---|---|
| A | LO | low V | 0.1 | 0.8991793501377106 | 0.7850155393518391 | 0.03000000000000001 | True |
| B | LO | high V | 0.25 | 0.05 | 0.785015540293945 | 0.07500000000000002 | True |
| C | HI | low V | 0.55 | 0.6946928408741951 | 0.5967380565761603 | 0.16500000000000004 | True |
| D | HI | high V | 0.7 | 0.05 | 0.5967380569813433 | 0.21000000000000005 | True |

| root | share | target r | bracket | r at bracket ends | straddles | solved phi | realized r | abs residual | tol | iters | converged |
|---|---|---|---|---|---|---|---|---|---|---|---|
| phi_a (cell A) | 0.1 | 0.785015540293945 | [0.85, 0.98] | [0.7908869485651705, 0.7718092954224756] | True | 0.8991793501377106 | 0.7850155393518391 | 9.421059488090577e-10 | 1e-09 | 22 | True |
| phi_c (cell C) | 0.55 | 0.5967380569813433 | [0.6, 0.98] | [0.6180810655328032, 0.48710147666803805] | True | 0.6946928408741951 | 0.5967380565761603 | 4.051829982643085e-10 | 1e-09 | 25 | True |
| dV LO / HI (exact arithmetic) | 0.04500000000000001 / 0.04500000000000001 | — | — | — | True | V_bar 0.05250000000000002 / 0.18750000000000006 | — | — | — | — | True |

φ_a = `0.8991793501377106` (22 bisections, |Δr| = 9.421059488090577e-10) and
φ_c = `0.6946928408741951` (25 bisections, |Δr| = 4.051829982643085e-10), both inside the
registered 1e-9. ΔV = 0.04500000000000001 / 0.04500000000000001 and V̄ = 0.05250000000000002 / 0.18750000000000006
are exact to the last bit of the design arithmetic. The registered
channel-cancellation bias bound evaluates to 1.1132276787474298e-10, three orders below
the 1e-9 root tolerance, so matched-r cancellation is clean.

## 5. Diagnostic annex — the preserved first reading

**Disclosure and timing.** This harness's first execution computed Part 0
end-to-end before the STOP branch existed, and therefore wrote and hashed the
predictions before the G0n1 verdict was acted on. Those artifacts are preserved
verbatim under `results/m4_n1_response_transport/first_reading/`. They are
reported here because they cost nothing and are decision-relevant, and they are
safe to report because **they contain no hypothesis-relevant number**: every
response-grade quantity in this leg (κ̂_LO, κ̂_HI, Δκ̂) requires fresh worlds,
and the ordering guard records 0 fresh-world generations before the
stamp and 0 in total. Everything in this annex is a deterministic
function of already-persisted M3 data. The live run issues **no** seal; the
preserved stamp is `d305171fb1392d17b0e19dace4ab489a8ec08927ed6240b9bfcfde226d892e4b` and is inert.

### 5.1 The predictions that would have been sealed

| prediction | quantity | point | draws [2.5%, 97.5%] | SE_meas | band | width | budget | status | A-sat co-prediction |
|---|---|---|---|---|---|---|---|---|---|
| S1 | kappa_resp(0.0525) | 0.8781169374706213 | [0.8385020225736461, 0.9208736373027281] | 0.04312395682368867 | [0.7522541089262688, 1.0071215509501055] | 0.2548674420238367 | 0.3 | within budget | 0.881063408640396 |
| S2 | kappa_resp(0.1875) | 0.6671284384567739 | [0.6281772434451952, 0.7023141057767245] | 0.04312395682368867 | [0.5419293297978178, 0.7885620194241019] | 0.24663268962628404 | 0.3 | within budget | 0.6719928884561107 |
| S3 | delta kappa = kappa_LO - kappa_HI | 0.21098849901384734 | [0.13938120116080563, 0.28616676496423527] | 0.0609864846032523 | [0.017408231954301023, 0.4081397341707399] | 0.3907315022164389 | 0.35 | **VOID_FOR_WIDTH** | 0.2090705201842853 |

S1 = 0.8781169374706213 and S2 = 0.6671284384567739 reproduce CC.2's quoted 0.8781 and
0.6671; S3 = 0.21098849901384734 reproduces the quoted decline 0.2110. **The
predictions themselves are correct** — which is precisely why the CC.1 constants
being wrong is a bookkeeping defect rather than a substantive one.

### 5.2 A second, independent blocker: S3 exceeds its rule-27 budget

| quantity | value |
|---|---|
| S3 draw span (M3 parameter uncertainty) | 0.14678556380342964 |
| S3 measurement allowance 4 x SE_diff | 0.2439459384130092 |
| S3 band width | 0.3907315022164389 |
| S3 rule-27 budget | 0.35 |
| **S3 over budget** | **True** |
| S3 overrun | 0.0407315022164389 |
| SE_diff needed to fit the budget | 0.050803609049142585 |
| worlds per cell needed | 553.361951765724 |
| worlds per cell needed (ceiling) | 554 |
| registered escalation n | 768 |
| SE_diff at the registered escalation | 0.04312395682368867 |
| S3 width at the registered escalation | 0.3192813910981843 |
| **the registered escalation would fix S3** | **True** |
| but the escalation is wired to | G2n1 (the projection), which PASSES at 384 -- so the declared ladder cannot fire for the gate that needs it |

S3's band is **0.3907315022164389** wide against a registered budget of
0.35 — an overrun of 0.0407315022164389. Under G3n1 that voids S3, leaving
2 valid predictions, and the registration's own note then applies: *"with < 3
valid, cell 4 unreachable and the best available is cell 5's grade."* **The
leg's success outcome CURVE_TRANSPORTS_TO_RESPONSE would have been unreachable
before a single world was drawn.**

The arithmetic decomposes the width: 0.14678556380342964 from M3's parameter uncertainty
(the bootstrap draw span, irreducible without new level-side data) and
0.2439459384130092 from the 4 × SE_diff measurement allowance
(62.43313810870556% of the width). Only the second term responds to worlds.
Fitting the budget needs SE_diff ≤ 0.050803609049142585, i.e. **554 worlds per
cell** (553.361951765724 exactly), against the registered 384.

The registered once-only escalation to 768/side **would** fix it
(S3 width 0.3192813910981843 ≤ 0.35: True) — but that ladder is
wired to **G2n1**, the projection, which passes comfortably at 384. As
registered the two gates are not jointly satisfiable at n = 384, and the only
declared ladder cannot fire for the gate that needs it.

### 5.3 The projection passes

| configuration | P(delta > 2 SE_diff) | true delta | SE_kappa | SE_diff |
|---|---|---|---|---|
| truth CONSTANT | 0.0165 | 0.0 | 0.04312395682368867 | 0.0609864846032523 |
| truth CONSTANT (registration-text reading) | 0.024 | 0.0 | 0.04312395682368867 | 0.0609864846032523 |
| truth CURVE | 0.9245 | 0.2109884990138473 | 0.04312395682368867 | 0.0609864846032523 |
| PASS at n=384 | True | — | — | — |
| PASS under RN-N1-8's second reading | True | — | — | — |

P(Δκ̂ > 2·SE_diff) = 0.9245 under CURVE (bar ≥ 0.8) and 0.0165 under
CONSTANT (bar ≤ 0.1); SE_κ = 0.04312395682368867, SE_diff = 0.0609864846032523. Under
RN-N1-8's second reading of the CONSTANT truth the rate is 0.024 and the
verdict is unchanged. **The instrument has the power it was designed to have.**

## 6. Routing

| # | condition | outcome |
|---|---|---|
| 1 | any G0n1 mismatch | **STOP (citation defect)**  <-- THIS LEG |
| 2 | projection fails after escalation | NON_PROJECTABLE (handback; no worlds) |
| 3 | pilot regime failure | UNRESOLVED_SEAL (predictions on record, unmeasured) |
| 4 | 3 valid predictions AND 3/3 inside (S3 also requiring delta > 0) | CURVE_TRANSPORTS_TO_RESPONSE -- the mechanism survives its first test; the sealed 0.722 difference-fit acquires its secant reading; N2 becomes registrable |
| 5 | exactly 2 of the valid predictions inside | PARTIAL_TRANSPORT -- the miss names the break (level-vs-response or magnitude); theory note required |
| 6 | <= 1 inside | NO_TRANSPORT -- the curve is level-only; CC.1 dies as physics (CC.3); the line closes early |
| -- | any prediction VOID_FOR_WIDTH | modifier VOID_FOR_WIDTH(n); with < 3 valid, cell 4 unreachable and the best available is cell 5's grade |
| -- | A-quad/A-sat co-predictions disagree on any verdict | modifier FORM_SPLIT (reported; adjudicates per the tie rule) |

## 7. Gates

| gate | PASS | detail |
|---|---|---|
| G0n1 | False | 3 clause(s) fail at full precision; (i) pairs and roots PASS, (iii) sigma_w PASS |
| G1n1 | None | not reached (no world drawn) |
| G2n1 | None | not reached in this reading; the preserved first reading passed it (annex) |
| G3n1 | None | not reached in this reading; the preserved first reading shows S3 over budget (annex) |
| G4n1 | True | guard armed on 3 k2b instance(s), 9 entry points; 0 fresh-world generations ever; no seal issued for a stopped leg |
| G5n1 | True | stopped inside the part0 estimate; tables generated (rule 24) |

## 8. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| L-1n1 | S1 inside its sealed band | 0.6 | two-sided containment |
| L-2n1 | S2 inside its sealed band | 0.6 | two-sided containment |
| L-3n1 | S3 inside AND delta kappa-hat > 0 | 0.55 | two-sided containment plus a one-sided sign clause |
| G2n1 | P(delta > 2 SE_diff \| CURVE) >= 0.8 AND <= 0.1 under CONSTANT | — | one-sided each |
| G3n1 | band widths S1 <= 0.3, S2 <= 0.3, S3 <= 0.35 | — | one-sided |

## 9. Pinned readings

| note | pinned reading |
|---|---|
| RN-N1-1 | ordering enforced in code (K2f G1f + RN-K2F-4): the permit for ANY fresh world, pilot included, is issued only by re-reading the stamp from disk and re-hashing; guards on every reachable k2b instance; salt embedded in the sealed bytes (D3) |
| RN-N1-2 | phi_a / phi_c by bisection on the pinned map to \|r - target\| <= 1e-9, from the registration's own brackets whose endpoints are re-derived and checked to straddle before the search |
| RN-N1-3 | kappa-hat = -D/dV with D = field(HIGH V) - field(LOW V), so a field falling in V gives kappa-hat > 0; dV = 0.045 is exact arithmetic and carries no error |
| RN-N1-4 | SE_kappa = sqrt(2)*sigma_w/(sqrt(n)*dV), SE_diff = sqrt(2)*SE_kappa, from M1b's persisted sigma_w -- PRIOR allowances fixed before the cells exist; realized SEMs reported beside them and never re-draw the bands |
| RN-N1-5 | M3's pipeline recomputed deterministically (alpha at fixed theta*, A-quad refit, B=2000 world-block draws) with each draw's (c, kappa0, kappa2) propagated through all three predictions, so the bands inherit the parameter covariance; G0 demands bit-exact point parameters first |
| RN-N1-6 | A-sat co-predictions from its local tax (A/tau)*exp(-V/tau), written INSIDE the hashed file; they adjudicate nothing unless a verdict differs, which reports FORM_SPLIT |
| RN-N1-7 | the projection statistic is the ONE-SIDED event delta-kappa-hat > 2*SE_diff at both truths; under CONSTANT both local taxes equal M3's persisted A-lin kappa so the event is a pure false-positive rate |
| RN-N1-8 | REGISTRATION-ANTICIPATED DIVERGENCE, pinned before the stamp: G2n1 quotes the A-lin chord as 0.7729284648259515, alpha.json holds 0.7729279998877195 (4.649e-7 apart). The registration's own text makes the persisted value control, so it is used and the clause is recorded as ANTICIPATED rather than failing G0n1; both readings reported. The projection is insensitive by construction -- under CONSTANT both local taxes take the same value, so the true difference is exactly 0 either way |

RN-N1-8 is the one registration divergence that did **not** stop the leg. G2n1
quotes the A-lin chord as 0.7729284648259515; `alpha.json` holds 0.7729279998877195
(4.649382319144024e-07 apart). The registration legislates its own resolution — *"if its
persisted value differs, the persisted value controls"* — so the persisted value
was used, the clause was recorded as ANTICIPATED and non-blocking, and both
readings were carried through the projection (§5.3), where they agree. This was
pinned in Part 0 before the stamp and before any world.

## 10. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine, and the only `pandas` present belongs to
   `/usr/bin/python3` (CPython 3.9.6), which cannot import the machinery
   (`from datetime import UTC` needs 3.11+). A CPython 3.12.12 venv was built
   outside the repo from `requirements-lock-main.txt` verbatim and pinned; see
   §12. Resolved BEFORE any hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage was run as its own foreground command under an explicit tool timeout
   below 600 s. Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (my own transcription; before any number).** Two constants embedded in
   this harness from M3's *rounded report prose* were wrong in trailing digits:
   A-sat's θ and the A-lin chord. Both were caught by reading
   `results/m4_m3_tax_curve/alpha.json` at full precision **before** Part 0 was
   run for the first time, and corrected. Had they survived, A-sat's θ would
   have raised a FALSE citation defect. Resolved BEFORE any hypothesis-relevant
   number existed. (This is the third leg on which pre-flighting embedded
   constants against artifacts has caught an error; it is now reflexive.)
4. **A-4 (my own code ordering; before any number, disclosed in full).** The
   harness's first version evaluated G0n1 but wrote and hashed the predictions
   *before* acting on the verdict, so the first execution issued a stamp for a
   leg that had already failed its first gate. No world was drawn — the guard
   log shows 0 generations before that stamp — so nothing was
   contaminated, but the ordering was wrong and is fixed: the STOP now fires
   before the seal. The first reading is preserved under `first_reading/` and
   reported as §5 rather than discarded. Resolved BEFORE any
   hypothesis-relevant number existed, and no hypothesis-relevant number was
   ever computed in either reading.

## 11. What the planner must decide

Two independent things are wrong, and only the first is a citation defect.

1. **Appendix CC.1's constants** (the STOP): correct V\*, A0 and c′ to
   0.6143589975880801, 0.2949439312708197, -0.08246994861803153, and correct the
   N-line charter's rounded quote of c′. CC.2's testable content is untouched.
2. **G3n1 vs G2n1 at n = 384** (a design defect, not a citation defect): the S3
   budget of 0.35 and the S3 band rule are not jointly satisfiable at
   384 worlds/cell, and the once-only escalation that would satisfy them is
   attached to the gate that passes. A re-dispatch needs one of: n = 554+
   per cell (the registered 768 suffices), a re-wired ladder that lets
   G3n1 trigger the escalation, an S3 budget ≥ 0.3907315022164389, or a band rule for
   S3 that does not add 4 × SE_diff on top of the full joint draw span. Note
   that 0.14678556380342964 of the width is M3's parameter uncertainty and no number of
   fresh worlds will reduce it.

Everything else in the leg is ready: the roots are solved and reusable, the
projection passes, the pilot cells are chosen, and the guard is enforced.

## 12. Environment

| component | value |
|---|---|
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| platform | macOS-26.4.1-arm64-arm-64bit |
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| scipy | 1.17.1 |

## 13. Ordering log

| utc | event | detail |
|---|---|---|
| 2026-08-14T03:01:17.036688+00:00 | part0_start |  |
| 2026-08-14T03:01:17.228229+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:01:17.477729+00:00 | STOP_G0n1 | failing=['appendix CC identity A0', 'appendix CC identity V*', "appendix CC identity c'"], seconds=0.4407651424407959 |

## 14. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 (to the STOP) | 360 | 0.441 |
| pilot | 30 | -- not reached |
| worlds_A | 230 | -- not reached |
| worlds_B | 230 | -- not reached |
| worlds_C | 230 | -- not reached |
| worlds_D | 230 | -- not reached |
| measure | 120 | -- not reached |
| finalize | 60 | -- not reached |

---

*Artifacts: `results/m4_n1_response_transport/` (gitignored) — `part0.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `ordering_log.jsonl`,
`first_reading/`. Harness:
`scripts/run_suica_m4_n1_response_transport.py`.*
