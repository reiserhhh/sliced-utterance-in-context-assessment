# SUICA M4-N1b — the response-transport seal — **CURVE_TRANSPORTS_TO_RESPONSE**

**Outcome: CURVE_TRANSPORTS_TO_RESPONSE (routing cell 4); modifiers: none.**
3/3 sealed predictions landed inside their bands, S3's
one-sided sign clause included. **The square-agreement mechanism survives its
first test.** 3072 fresh worlds (768/cell x 4),
sealed under `0b6a2713125ebee5…` with **0 fresh-world generations
before the stamp**.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_N_TAX_MECHANISM_LINE_PLAN.md` BEFORE run (commit 6eeec0d), a
re-registration of N1 after its cell-1 STOP. Every number below is generated
from artifacts by code (rule 24); none is hand-typed.

---

## 1. The result

The mechanism's claim is that a curve fitted to LEVELS transports to RESPONSE:
at a matched-attenuation pair straddling V̄, the difference cancels the channel
and the constant exactly, so κ̂ = −D/ΔV must read κ0 − κ2·V̄. Three numbers were
sealed from M3's persisted fit before any world existed. All three land.

| prediction | quantity | sealed prediction | measured | verdict |
|---|---|---|---|---|
| S1 | kappa_resp(0.0525) | 0.8781169374706213 | 0.9180647112012158 | **INSIDE** |
| S2 | kappa_resp(0.1875) | 0.6671284384567739 | 0.6670454850877494 | **INSIDE** |
| S3 | delta kappa = kappa_LO - kappa_HI | 0.21098849901384734 | 0.2510192261134664 | **INSIDE** |
| S3 sign clause | delta kappa-hat > 0 | one-sided, declared (L-3n1b) | 0.2510192261134664 | **True** |
| overall | 3/3 valid predictions inside | routing cell 4 | CURVE_TRANSPORTS_TO_RESPONSE | modifiers: none |

- **S1** κ_resp(0.0525): predicted 0.8781169374706213, measured **0.9180647112012158**
  (95% CI [0.863626452725556, 0.9749094012658702]), signed error 0.03994777373059455, at 0.37560947810709566 of the band half-width.
- **S2** κ_resp(0.1875): predicted 0.6671284384567739, measured **0.6670454850877494**
  (95% CI [0.618883540603541, 0.7141613816756263]), signed error **-8.295336902452988e-05** — a near-bullseye, at
  0.01835512745765127 of the half-width.
- **S3** the decline: predicted 0.21098849901384734, measured **0.2510192261134664**
  (95% CI [0.17991654115972247, 0.32623248423763684]), signed error 0.04003072709961905, at 0.2395707618248563. Δκ̂ > 0 is
  True and its CI excludes zero (True), so L-3n1b's conjunction
  fires in full.

### 1.1 The residual is not spread — it sits entirely at the LO pair

S2's error is -8.295336902452988e-05 while S1's is 0.03994777373059455 and S3's is 0.04003072709961905. S1 and
S3 miss by nearly the identical amount because S3 = S1 − S2 and S2 is
essentially exact: the HI pair (V̄ = 0.1875) reproduces the curve's prediction to
the fifth decimal, and the whole discrepancy lives at the LO pair
(V̄ = 0.0525), where the measured local tax runs ABOVE the curve. Both remain
well inside their bands, so this refines rather than qualifies the verdict, and
it is a directional fact the line should carry forward: at low base variance the
response-grade tax is if anything steeper than the level fit predicts.

| prediction | quantity | predicted | sealed band | measured | measured 95% CI | signed error | position in band | verdict |
|---|---|---|---|---|---|---|---|---|
| S1 | kappa_resp(0.0525) | 0.8781169374706213 | [0.7775155379703939, 0.9818601219059804] | 0.9180647112012158 | [0.863626452725556, 0.9749094012658702] | 0.03994777373059455 | 0.37560947810709566 | INSIDE |
| S2 | kappa_resp(0.1875) | 0.6671284384567739 | [0.5671907588419429, 0.7633005903799768] | 0.6670454850877494 | [0.618883540603541, 0.7141613816756263] | -8.295336902452988e-05 | 0.01835512745765127 | INSIDE |
| S3 | delta kappa = kappa_LO - kappa_HI | 0.21098849901384734 | [0.05313328751342827, 0.3724146786116126] | 0.2510192261134664 | [0.17991654115972247, 0.32623248423763684] | 0.04003072709961905 | 0.2395707618248563 | INSIDE (delta > 0: True) |

## 2. What was sealed, and when

| prediction | quantity | point | draws [2.5%, 97.5%] | SE_meas | sealed band | width | budget | status | A-sat co-prediction |
|---|---|---|---|---|---|---|---|---|---|
| S1 | kappa_resp(0.0525) | 0.8781169374706213 | [0.8385020225736461, 0.9208736373027281] | 0.03049324230162615 | [0.7775155379703939, 0.9818601219059804] | 0.20434458393558652 | 0.3 | within budget | 0.881063408640396 |
| S2 | kappa_resp(0.1875) | 0.6671284384567739 | [0.6281772434451952, 0.7023141057767245] | 0.03049324230162615 | [0.5671907588419429, 0.7633005903799768] | 0.19610983153803385 | 0.3 | within budget | 0.6719928884561107 |
| S3 | delta kappa = kappa_LO - kappa_HI | 0.21098849901384734 | [0.13938120116080563, 0.28616676496423527] | 0.04312395682368868 | [0.05313328751342827, 0.3724146786116126] | 0.3192813910981843 | 0.35 | within budget | 0.2090705201842853 |

The stamp went down at 2026-08-14T03:18:23.652217+00:00 with 0 fresh-world
generations recorded on 3 guarded `k2b` instances (9 wrapped
entry points), and the first world was permitted 37.565809 s later,
only after re-reading the stamp from disk and re-hashing `predictions.json` to a
match. Ordering is **enforced in code, not asserted**.

| quantity | value |
|---|---|
| predictions.json sha256 | 0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30d6d91cee39365c2 |
| bytes sealed | 5726 |
| salt embedded in the sealed bytes (D3) | True |
| stamp UTC | 2026-08-14T03:18:23.652217+00:00 |
| permit UTC | 2026-08-14T03:19:01.218024+00:00 |
| seconds stamp -> permit | 37.565809 |
| **fresh-world generations BEFORE the stamp** | **0** |
| generations before the permit | 0 |
| hash re-read from disk and re-hashed at permit time | True |
| re-hashed digest equals the stamp | True |
| k2b instances guarded | 3 |
| entry points wrapped | 9 |
| ENFORCED, not asserted | True |

### 2.1 The A-4 fix, as registered text

N1's harness wrote and hashed the predictions before acting on its G0 verdict.
This registration makes the corrected order binding, and RN-N1B-11 pins the
dependency the registration leaves implicit — the escalation moves n, and n
moves both the bands and the projection — so the executed order is: G0n1b, then
the bands and G3n1b's budgets (which decide n), then G2n1b at the DECIDED n,
then the stamp, and the stamp only if every pre-stamp gate passed.

| pre-stamp verdict | PASS |
|---|---|
| ALL_PASS | True |
| G0n1b | True |
| G2n1b (projection) | True |
| G3n1b (budgets) | True |
| worlds per cell decided BEFORE the stamp | 768 |
| executed order | G0n1b -> bands + G3n1b -> G2n1b at the decided n -> stamp |

## 3. Gate by gate

| gate | PASS | detail |
|---|---|---|
| G0n1b | True | pairs and roots; M3's numbers and CC's identities recomputed from the persisted parameters; sigma_w at source |
| G1n1b | True | rule-29 domain-pinned predicate held at all four cells (finite, \|x\| < 0.995, nonzero variance; NO positivity clause) |
| G2n1b | True | projection passed BEFORE the stamp under both truths |
| G3n1b | True | band widths against budgets; voided: none |
| G4n1b | True | 0 generations before the stamp; permit 37.566 s later by re-hash from disk; pilot passed |
| G5n1b | True | stages under estimate; routing reproduced; tables generated |

### 3.1 G0n1b — the corrected identities reproduce

Every M3 citation is bit-exact, and appendix CC.1-prime's corrected identities —
the ones this executor computed during N1 — recompute from M3's persisted fit
exactly, which is what rule 30 now demands of every published derived constant.

| clause | expected | persisted / recomputed | bit-exact |
|---|---|---|---|
| A-quad c | 0.21247398265278816 | 0.21247398265278816 | True |
| A-quad kappa0 | 0.9601680204204508 | 0.9601680204204508 | True |
| A-quad kappa2 | 1.562877770472943 | 1.562877770472943 | True |
| LOO A-lin | 0.003599294048156043 | 0.003599294048156043 | True |
| LOO A-quad | 0.001405398973367856 | 0.001405398973367856 | True |
| LOO A-sat | 0.0014509897412261284 | 0.0014509897412261284 | True |
| closure hits | 5 | 5 | True |
| kappa2 CI | [1.0324533419318935, 2.119753814549891] | [1.0324533419318935, 2.119753814549891] | True |
| projection P(lin) | 0.0575 | 0.0575 | True |
| projection P(quad) | 0.9935 | 0.9935 | True |
| M3 A-quad recompute from persisted worlds | [0.21247398265278816, 0.9601680204204508, 1.562877770472943] | [0.21247398265278816, 0.9601680204204508, 1.562877770472943] | True |
| CC V* | 0.6143589975880801 | 0.6143589975880801 | True |
| CC A0 | 0.2949439312708197 | 0.2949439312708197 | True |
| CC c' | -0.08246994861803153 | -0.08246994861803153 | True |
| A-sat theta | [-0.27493651728760515, 0.4878776246525967, 0.4983722810248614] | [-0.27493651728760515, 0.4878776246525967, 0.4983722810248614] | True |
| sigma_w | 0.026889438327132725 | 0.026889438327132725 | True |
| A-lin kappa (the CONSTANT truth) -- ANTICIPATED (RN-N1B-8; persisted controls, non-blocking) | 'delegated to alpha.json at full precision (no digits quoted) -- rule 30' | 0.7729279998877195 | differ by 0.0 |

### 3.2 G0n1b(i) — the roots re-derived identically

| cell | pair | side | share | phi | r | V | r interior |
|---|---|---|---|---|---|---|---|
| A | LO | low V | 0.1 | 0.8991793501377106 | 0.7850155393518391 | 0.03000000000000001 | True |
| B | LO | high V | 0.25 | 0.05 | 0.785015540293945 | 0.07500000000000002 | True |
| C | HI | low V | 0.55 | 0.6946928408741951 | 0.5967380565761603 | 0.16500000000000004 | True |
| D | HI | high V | 0.7 | 0.05 | 0.5967380569813433 | 0.21000000000000005 | True |

| root | share | target r | bracket | r at bracket ends | straddles | solved phi | realized r | \|residual\| | tol | iters | converged |
|---|---|---|---|---|---|---|---|---|---|---|---|
| phi_a (cell A) | 0.1 | 0.785015540293945 | [0.85, 0.98] | [0.7908869485651705, 0.7718092954224756] | True | 0.8991793501377106 | 0.7850155393518391 | 9.421059488090577e-10 | 1e-09 | 22 | True |
| phi_c (cell C) | 0.55 | 0.5967380569813433 | [0.6, 0.98] | [0.6180810655328032, 0.48710147666803805] | True | 0.6946928408741951 | 0.5967380565761603 | 4.051829982643085e-10 | 1e-09 | 25 | True |
| dV LO / HI (exact) | 0.04500000000000001 / 0.04500000000000001 | — | — | — | True | V_bar 0.05250000000000002 / 0.18750000000000006 | — | — | — | — | True |

φ_a = `0.8991793501377106` (22 bisections, |Δr| = 9.421059488090577e-10) and φ_c =
`0.6946928408741951` (25 bisections, |Δr| = 4.051829982643085e-10) — bit-identical to N1's
solved roots, as the deterministic protocol requires. The channel-cancellation
bias bound is 1.1132276787474298e-10, three orders below the root tolerance.

### 3.3 G3n1b — the budgets, at executed precision

| quantity | realized width | rule-27 budget | within |
|---|---|---|---|
| S1 width at n=768 | 0.20434458393558652 | 0.3 | True |
| S2 width at n=768 | 0.19610983153803385 | 0.3 | True |
| S3 width at n=768 | 0.3192813910981843 | 0.35 | True |
| escalation to 1152/cell fired | False | — | — |
| worlds per cell after budgets | 768 | — | — |
| over budget (final) | none | — | True |

S3's realized width is 0.3192813910981843 against its 0.35 budget — matching
the registration's own executed prediction of 0.3192813910981843 **to the last
bit**, which is what defect #51's convention was enacted to guarantee. The
once-only escalation to 1152/cell did not fire (False).

### 3.4 G2n1b — the projection at the decided n

| configuration | P(delta > 2 SE_diff) | true delta | SE_kappa | SE_diff |
|---|---|---|---|---|
| n=768 truth CONSTANT | 0.0165 | 0.0 | 0.03049324230162615 | 0.04312395682368868 |
| n=768 truth CONSTANT (registration-text reading) | 0.024 | 0.0 | 0.03049324230162615 | 0.04312395682368868 |
| n=768 truth CURVE | 0.9975 | 0.2109884990138473 | 0.03049324230162615 | 0.04312395682368868 |
| n=768 PASS | True | — | — | — |
| escalated | not run | — | — | — |

P(Δκ̂ > 2·SE_diff) = 0.9975 under CURVE (bar ≥ 0.8), up from 0.9245 at
n = 384, and 0.0165 under CONSTANT (bar ≤ 0.1). SE_κ = 0.03049324230162615,
SE_diff = 0.04312395682368868, from M1b's persisted σ_w = 0.026889438327132725.

### 3.5 G1n1b — the rule-29 regime predicate

| cell | n | min | max | finite | any saturated | nonzero var | PASS |
|---|---|---|---|---|---|---|---|
| A | 4 | 0.12246350903170755 | 0.17779547051383884 | True | False | True | True |
| D | 4 | 0.007675636181511309 | 0.06360514009624262 | True | False | True | True |

The predicate is pinned in the statistic's OWN domain (rule 29, which N1's
predecessor bought): `recovery_b_only` is a weighted mean of matrix cosines on
[−1, 1], so the check is finiteness, non-saturation at |x| ≥ 0.995 and nonzero
within-cell variance, with **no positivity clause**. It held at the pilot and at
all four full cells.

## 4. Per-cell measurements

| cell | pair | side | share | phi | r | V | n | mean | SEM | 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|
| A | LO | low V | 0.1 | 0.8991793501377106 | 0.7850155393518391 | 0.03000000000000001 | 768 | 0.16331335624785112 | 0.0009518683047234402 | [0.1613665276052781, 0.1652153028227323] |
| B | LO | high V | 0.25 | 0.05 | 0.785015540293945 | 0.07500000000000002 | 768 | 0.12200044424379641 | 0.0009131491292271307 | [0.12029314042880435, 0.1238157183958433] |
| C | HI | low V | 0.55 | 0.6946928408741951 | 0.5967380565761603 | 0.16500000000000004 | 768 | 0.06839745505784454 | 0.0008011570535819981 | [0.06679569957886612, 0.06991266607360211] |
| D | HI | high V | 0.7 | 0.05 | 0.5967380569813433 | 0.21000000000000005 | 768 | 0.038380408228895824 | 0.0007643823921706975 | [0.036867115043478914, 0.03990495805090718] |

Cell means run from 0.038380408228895824 to 0.16331335624785112 with SEMs between 0.0007643823921706975
and 0.0009518683047234402 — two orders below the differences they support. D_LO =
-0.04131291200405471 and D_HI = -0.03001704682894872; κ̂ = −D/ΔV with ΔV = 0.045 exact, giving
κ̂_LO = 0.9180647112012158 [0.863626452725556, 0.9749094012658702] and κ̂_HI = 0.6670454850877494 [0.618883540603541, 0.7141613816756263], and
Δκ̂ = **0.2510192261134664** [0.17991654115972247, 0.32623248423763684].

## 5. A-sat, and why FORM_SPLIT does not fire

| prediction | A-quad point | A-quad band | A-quad verdict | A-sat co-prediction | A-sat band (identical rule, same resamples) | A-sat verdict | verdicts agree |
|---|---|---|---|---|---|---|---|
| S1 | 0.8781169374706213 | [0.7775155379703939, 0.9818601219059804] | INSIDE | 0.881063408640396 | [0.7781919210449346, 0.9875253315714883] | INSIDE | **True** |
| S2 | 0.6671284384567739 | [0.5671907588419429, 0.7633005903799768] | INSIDE | 0.6719928884561107 | [0.5749551805684668, 0.7656600629049272] | INSIDE | **True** |
| S3 | 0.21098849901384734 | [0.05313328751342827, 0.3724146786116126] | INSIDE | 0.2090705201842853 | [0.0516894865409559, 0.3709878445227984] | INSIDE | **True** |

RN-N1B-10 pins what the modifier compares. The registration supplies A-sat only
as a POINT, and a point has no verdict, so A-sat's band is built by the
IDENTICAL rule from the IDENTICAL bootstrap resamples — each world-block draw
refits A-sat from its persisted optimum, M3's own bootstrap convention, and is
propagated through the same local-tax map. The refit reproduces M3's persisted
A-sat θ. All three verdicts agree, so **no FORM_SPLIT**. Two secondary readings
are reported and route nothing:

| prediction | primary: verdicts agree (routes) | secondary (a): A-sat point inside A-quad's band -- forms unseparated | secondary (b): measurement nearer to |
|---|---|---|---|
| S1 | True | True | A-sat |
| S2 | True | True | A-quad |
| S3 | True | True | A-quad |

Both forms' bands overlap almost completely, so this experiment does not
separate A-quad from A-sat — consistent with their LOO tie in M3. The proximity
reading splits (A-sat nearer at S1, A-quad nearer at S2 and S3) and is exactly
the kind of thing that must not be allowed to route.

## 6. Routing

| # | condition | outcome |
|---|---|---|
| 1 | any G0n1b mismatch | STOP (citation defect) |
| 2 | projection fails after escalation | NON_PROJECTABLE (handback; no worlds) |
| 3 | pilot regime failure | UNRESOLVED_SEAL (predictions on record, unmeasured) |
| 4 | 3 valid predictions AND 3/3 inside (S3 also requiring delta > 0) | **CURVE_TRANSPORTS_TO_RESPONSE -- the mechanism survives its first test; the sealed 0.722 difference-fit acquires its secant reading; N2 becomes registrable**  <-- THIS LEG |
| 5 | exactly 2 of the valid predictions inside | PARTIAL_TRANSPORT -- the miss names the break (level-vs-response or magnitude); theory note required |
| 6 | <= 1 inside | NO_TRANSPORT -- the curve is level-only; CC.1 dies as physics (CC.3); the line closes early |
| -- | any prediction VOID_FOR_WIDTH | modifier VOID_FOR_WIDTH(n); with < 3 valid, cell 4 unreachable and the best available is cell 5's grade |
| -- | A-quad/A-sat co-predictions disagree on any verdict | modifier FORM_SPLIT (reported; adjudicates per the tie rule) |

## 7. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G2n1b | P(delta > 2 SE_diff \| CURVE) >= 0.8 AND <= 0.1 under CONSTANT | — | one-sided each |
| G3n1b | band widths S1 <= 0.3, S2 <= 0.3, S3 <= 0.35 | — | one-sided |
| L-1n1b | S1 inside its sealed band | 0.6 | two-sided containment |
| L-2n1b | S2 inside its sealed band | 0.6 | two-sided containment |
| L-3n1b | S3 inside AND delta kappa-hat > 0 | 0.55 | two-sided containment plus a one-sided sign clause |

## 8. Pinned readings

| note | pinned reading |
|---|---|
| RN-N1B-1 | ordering enforced in code (K2f G1f + RN-K2F-4): the permit for ANY fresh world, pilot included, is issued only by re-reading the stamp from disk and re-hashing; guards on every reachable k2b instance; salt embedded in the sealed bytes (D3) |
| RN-N1B-10 | FORM_SPLIT compares like with like: A-sat's band is built by the identical rule from the identical bootstrap resamples (each draw refits A-sat from its persisted optimum), so both forms have a verdict; it fires iff the inside/outside verdicts differ. Separation and proximity readings are reported, never used to route |
| RN-N1B-11 | pre-stamp order forced by dependency: G0n1b, then bands and G3n1b budgets (which decide n), then G2n1b at the DECIDED n, then the stamp -- and only if every pre-stamp gate passed. The base-n projection is reported too |
| RN-N1B-2 | phi_a / phi_c by bisection on the pinned map to \|r - target\| <= 1e-9, from the registration's own brackets whose endpoints are re-derived and checked to straddle before the search |
| RN-N1B-3 | kappa-hat = -D/dV with D = field(HIGH V) - field(LOW V), so a field falling in V gives kappa-hat > 0; dV = 0.045 is exact arithmetic and carries no error |
| RN-N1B-4 | SE_kappa = sqrt(2)*sigma_w/(sqrt(n)*dV), SE_diff = sqrt(2)*SE_kappa, from M1b's persisted sigma_w -- PRIOR allowances fixed before the cells exist; realized SEMs reported beside them and never re-draw the bands |
| RN-N1B-5 | M3's pipeline recomputed deterministically (alpha at fixed theta*, A-quad refit, B=2000 world-block draws) with each draw's (c, kappa0, kappa2) propagated through all three predictions, so the bands inherit the parameter covariance; G0 demands bit-exact point parameters first |
| RN-N1B-6 | A-sat co-predictions from its local tax (A/tau)*exp(-V/tau), written INSIDE the hashed file; they adjudicate nothing unless a verdict differs, which reports FORM_SPLIT |
| RN-N1B-7 | the projection statistic is the ONE-SIDED event delta-kappa-hat > 2*SE_diff at both truths; under CONSTANT both local taxes equal M3's persisted A-lin kappa so the event is a pure false-positive rate |
| RN-N1B-8 | N1's A-lin chord divergence is RESOLVED AT SOURCE: this registration delegates the chord and A-sat's theta to alpha.json at full precision instead of quoting digits (defect #50 / rule 30), so no registered constant can diverge; persisted values are read and their provenance recorded, N1's numbers carried only as history |
| RN-N1B-9 | ONE once-only escalation to 1152/cell, shared by G2n1b and G3n1b because both consume n (#51's convention): it fires if EITHER fails at 768 and BOTH are re-evaluated at 1152; budgets failing at the ceiling -> NON_SEALABLE_AT_CEILING, projection failing -> NON_PROJECTABLE |

Four are new this leg. RN-N1B-8 records that N1's chord divergence is resolved
at source — this registration delegates to `alpha.json` instead of quoting
digits, so no registered constant can diverge. RN-N1B-9 reads #51's convention
as making the escalation a SHARED-KNOB ladder: one once-only escalation, fired
by either gate, with both re-evaluated at the landing point. RN-N1B-10 defines
the FORM_SPLIT comparison. RN-N1B-11 pins the pre-stamp order.

## 9. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine and the only `pandas` present belongs to CPython 3.9.6,
   which cannot import the machinery. A CPython 3.12.12 venv was built
   outside the repo from `requirements-lock-main.txt` verbatim and pinned.
   Resolved BEFORE any hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (sub-chunking; before any world).** At 768 worlds/cell
   the measured cost (~0.63 s/world) puts a whole cell at ~481 s, close enough
   to the 600 s ceiling to risk a truncated stage. Each cell was therefore run
   in two 384-world sub-chunks. This changes no number: every world's seed is a
   pure function of (cell, share, phi, world index, salt), so the rows are
   identical for any chunk boundary, and the assembled cell is verified to hold
   exactly the world indices 0…n−1 before it is written. Decided BEFORE any
   world was drawn.
4. **A-4 (inherited bug in MY N1 code, fixed before any measurement existed).**
   N1's harness hard-coded `a_sat_verdict_agrees = True`, which would have made
   FORM_SPLIT structurally unable to fire. It never executed — N1 stopped at
   G0 — but it would have executed here. Found while porting, and replaced with
   the real comparison of §5, pinned as RN-N1B-10 BEFORE the stamp. Had it
   survived, this leg would have reported "no FORM_SPLIT" as a tautology rather
   than as a finding. Resolved BEFORE any hypothesis-relevant number existed.
5. **A-5 (my own stale keys; after the verdict, before any number changed).**
   The port left two report-side references to the renamed A-sat key, which
   raised at `finalize` twice. Both are presentation-layer lookups; the verdict
   in `decision.json` was already written and did not change across the fixes.
   No hypothesis-relevant number was touched — the failures were loud, not
   silent, and are disclosed here for completeness.

## 10. Rule events

- **Rule 13:** no verdict sits near a boundary. The largest |position in band|
  is S1's at 0.37560947810709566, leaving a margin of 0.6243905218929043 of the
  half-width (62.439052189290436%) before any verdict would flip, so no
  containment call is unstable and no B = 20000 re-run was triggered.
- **Rule 26:** no bounded winner; nothing was fitted with active bounds.
- **Rule 29:** in force as the G1n1b predicate, domain-pinned to [−1, 1] with no
  positivity clause. Held everywhere.
- **Rule 30:** exercised in both directions — the corrected CC.1-prime constants
  reproduce bit-exactly from persisted inputs (§3.1), and this leg's own
  published constants are all generated, not transcribed.

## 11. What this licenses, and what it does not

CC.2's pre-registered honesty clause said a miss would kill CC.1 as physics. It
did not miss. What is licensed: the tax curve is not a fitting artefact of the
level pipeline — it transports to a response-grade experiment at two fresh
base-variance points outside the level fit's estimation space, and the decline
between them is real and signed. N2 (the frame-floor question, on the corrected
c′ = -0.08246994861803153) becomes registrable, and M3's sealed 0.722 difference-fit
acquires its reading as a secant of the curve at its design's V̄.

What is NOT licensed: this does not separate A-quad from A-sat (§5) — the square
form is one of at least two curved readings the data cannot tell apart here, and
CC.1's vertex V\* = 0.6143589975880801 remains unreachable arithmetic on-support. The
LO-pair residual (§1.1) is unexplained. And the grade is EXPLORATORY on a
synthetic, label-free instrument.

## 12. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

## 13. Ordering log

| utc | event | detail |
|---|---|---|
| 2026-08-14T03:18:03.822088+00:00 | part0_start |  |
| 2026-08-14T03:18:04.002998+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:18:23.653322+00:00 | predictions_stamped | S1=0.8781169374706213, S2=0.6671284384567739, S3=0.21098849901384734, generations_before_stamp=0, sha256='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30d6d91cee39365c2' |
| 2026-08-14T03:18:23.667021+00:00 | part0_done | G0n1_PASS=True, G2n1_PASS=True, n_valid=3, seconds=19.845941066741943 |
| 2026-08-14T03:19:01.217235+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:19:01.218039+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:19:01.218024+00:00', seconds_stamp_to_permit=37.565809, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30d |
| 2026-08-14T03:19:06.020174+00:00 | pilot_done | PASS=True, seconds=4.980885028839111 |
| 2026-08-14T03:19:12.844512+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:19:12.845168+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:19:12.845157+00:00', seconds_stamp_to_permit=49.192942, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30d |
| 2026-08-14T03:22:56.246893+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:22:56.247478+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:22:56.247466+00:00', seconds_stamp_to_permit=272.595251, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30 |
| 2026-08-14T03:26:50.793942+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:26:50.794782+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:26:50.794767+00:00', seconds_stamp_to_permit=507.142552, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30 |
| 2026-08-14T03:26:50.807883+00:00 | worlds_A_done | seconds=0.20214390754699707 |
| 2026-08-14T03:26:51.208597+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:26:51.209309+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:26:51.209297+00:00', seconds_stamp_to_permit=507.557082, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30 |
| 2026-08-14T03:30:39.398122+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:30:39.398820+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:30:39.398809+00:00', seconds_stamp_to_permit=735.746594, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30 |
| 2026-08-14T03:34:26.388324+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:34:26.389036+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:34:26.389024+00:00', seconds_stamp_to_permit=962.736809, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30 |
| 2026-08-14T03:34:26.401765+00:00 | worlds_B_done | seconds=0.1961967945098877 |
| 2026-08-14T03:34:35.262981+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:34:35.263783+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:34:35.263770+00:00', seconds_stamp_to_permit=971.611555, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30 |
| 2026-08-14T03:38:18.920452+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:38:18.921216+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:38:18.921200+00:00', seconds_stamp_to_permit=1195.268986, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea3 |
| 2026-08-14T03:42:08.854516+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:42:08.855394+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:42:08.855370+00:00', seconds_stamp_to_permit=1425.203166, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea3 |
| 2026-08-14T03:42:08.868256+00:00 | worlds_C_done | seconds=0.20302414894104004 |
| 2026-08-14T03:42:09.262095+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:42:09.262796+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:42:09.262785+00:00', seconds_stamp_to_permit=1425.61057, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea30 |
| 2026-08-14T03:45:58.707964+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:45:58.708701+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:45:58.708689+00:00', seconds_stamp_to_permit=1655.056475, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea3 |
| 2026-08-14T03:49:42.522528+00:00 | guard_armed | n_k2b_instances=3, n_wrapped=9 |
| 2026-08-14T03:49:42.523168+00:00 | permit_issued | generations_before_permit=0, permit_utc='2026-08-14T03:49:42.523155+00:00', seconds_stamp_to_permit=1878.870941, sha256_recomputed='0b6a2713125ebee513f3d32e8131a99486f8e9c652d25ea3 |
| 2026-08-14T03:49:42.535716+00:00 | worlds_D_done | seconds=0.20742416381835938 |
| 2026-08-14T03:49:49.718755+00:00 | measure_done | inside={'S1': True, 'S2': True, 'S3': True}, seconds=0.025058746337890625 |
| 2026-08-14T03:49:59.485904+00:00 | finalize_done | modifiers=[], seconds=0.00032210350036621094, slug='CURVE_TRANSPORTS_TO_RESPONSE' |
| 2026-08-14T03:50:22.840450+00:00 | finalize_done | modifiers=[], seconds=0.0002932548522949219, slug='CURVE_TRANSPORTS_TO_RESPONSE' |
| 2026-08-14T03:50:42.748937+00:00 | finalize_done | modifiers=[], seconds=0.0002951622009277344, slug='CURVE_TRANSPORTS_TO_RESPONSE' |
| 2026-08-14T03:53:23.977594+00:00 | finalize_done | modifiers=[], seconds=0.0003199577331542969, slug='CURVE_TRANSPORTS_TO_RESPONSE' |
| 2026-08-14T03:54:17.306955+00:00 | finalize_done | modifiers=[], seconds=0.0003452301025390625, slug='CURVE_TRANSPORTS_TO_RESPONSE' |

## 14. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 420 | 19.846 |
| pilot | 30 | 4.981 |
| worlds_A | 250 | 0.202 |
| worlds_B | 250 | 0.196 |
| worlds_C | 250 | 0.203 |
| worlds_D | 250 | 0.207 |
| measure | 120 | 0.025 |
| finalize | 60 | 0.000 |

---

*Artifacts: `results/m4_n1b_response_transport/` (gitignored) — `part0.json`,
`predictions.json`, `predictions.sha256.json`, `g4n1b_pilot.json`,
`cells/`, `measured.json`, `decision.json`, `prose_facts.json`,
`report_tables.md`, `ordering_log.jsonl`. Harness:
`scripts/run_suica_m4_n1b_response_transport.py`.*
