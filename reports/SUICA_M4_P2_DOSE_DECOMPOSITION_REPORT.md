# SUICA M4-P2 — the dose-decomposition — **GENUINE_SCAFFOLD**

**Outcome: GENUINE_SCAFFOLD (routing cell 3); modifiers: none.**
GENUINE_SCAFFOLD -- frame content genuinely improves person-reading against a frame-fixed truth; f quantifies the split

Per cell on the R_cf slope: B1=POSITIVE, B2=POSITIVE (cross-cell agreement True).
1920 fresh worlds (192/arm × 10 arms), each built in two
variants. No seal — a decomposition, not a prediction.

**But the headline number is f.** 95.8470007021553% of P1's boost at B1 and
97.1270002747466% at B2 is **frame-vs-frame agreement**, not better person-reading.
The genuine component survives — that is why the routing says
GENUINE_SCAFFOLD — but it is **4.152999297844707% / 2.8729997252534%** of the effect P1
measured, and its slope clears the minimum-interesting bar by a hair.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit b61cc52).
Every number below is generated from artifacts by code (rule 24).

---

## 1. The decomposition

| symbol | definition |
|---|---|
| F(s) | [R_nat(s) - R_nat(0)] - G(s)  -- frame-vs-frame share |
| G(s) | R_cf(s) - R_cf(0)  -- genuine improvement |
| R_cf | the DOSED world's gauge output scored against the ZERO-DOSE world's truth panel (frame-fixed counterfactual) |
| R_nat | the DOSED world's gauge output scored against its OWN truth panel (P1's quantity) |
| f | F(1) / [R_nat(1) - R_nat(0)]  -- the frame fraction at s = 1 |
| one_calibration | R_nat and R_cf share ONE gauge pass and ONE calibration, scored against two truth panels; a second calibration would confound the truth swap with a calibration swap. G1p2(d) proves R_nat is bit-identical to k2b's own run_field_world |

Each world is built twice at the same index — dosed and zero-dose — and the
DOSED world's gauge output is scored against both truth panels off **one
calibration**. That is required, not merely cheaper: a second calibration would
make R_cf − R_nat confound the truth swap with a calibration swap (RN-P2-4).

## 2. The result

| cell | phi | b_cf (the verdict quantity) | 95% CI | classification | sign-first | agree | b_nat | b_nat 95% CI |
|---|---|---|---|---|---|---|---|---|
| B1 | 0.05 | 0.015370398353696113 | [0.009829531824123106, 0.02099405067675933] | **POSITIVE** | POSITIVE | True | 0.3063773429719756 | [0.29798309345778956, 0.3145094094028631] |
| B2 | 0.6 | 0.010909345621091282 | [0.00559827343632706, 0.016261954399254843] | **POSITIVE** | POSITIVE | True | 0.3317152396666109 | [0.32408785857830824, 0.3389402818801945] |

| cell | G(1) | G(1) 95% CI | F(1) | F(1) 95% CI | denominator R_nat(1) - R_nat(0) | **f** | f 95% CI | CI width | budget | within budget | f > 0.5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | 0.012940768948183565 | [0.006585015895802276, 0.01931243058373269] | 0.2986597881455648 | [0.29076271113972507, 0.30688958479858763] | 0.3116005570937484 | **0.9584700070215529** | [0.9386859990245562, 0.9784391977625343] | 0.03975319873797811 | 0.3 | True | True |
| B2 | 0.009828469499716663 | [0.004013107408011507, 0.0160057999823994] | 0.33226935297222154 | [0.32362912650735165, 0.3406333136533709] | 0.3420978224719382 | **0.971270002747466** | [0.9535253481648153, 0.9882217251532477] | 0.03469637698843242 | 0.3 | True | True |

- **B1** (φ 0.05): b_cf = **0.015370398353696113** [0.009829531824123106, 0.02099405067675933] → POSITIVE;
  against b_nat = 0.3063773429719756 [0.29798309345778956, 0.3145094094028631]. G(1) = 0.012940768948183565 [0.006585015895802276, 0.01931243058373269],
  F(1) = 0.2986597881455648 [0.29076271113972507, 0.30688958479858763], denominator 0.3116005570937484 → **f = 0.9584700070215529**
  [0.9386859990245562, 0.9784391977625343] (width 0.03975319873797811 ≤ 0.3: True).
- **B2** (φ 0.6): b_cf = **0.010909345621091282** [0.00559827343632706, 0.016261954399254843] → POSITIVE;
  against b_nat = 0.3317152396666109 [0.32408785857830824, 0.3389402818801945]. G(1) = 0.009828469499716663 [0.004013107408011507, 0.0160057999823994],
  F(1) = 0.33226935297222154 [0.32362912650735165, 0.3406333136533709], denominator 0.3420978224719382 → **f = 0.971270002747466**
  [0.9535253481648153, 0.9882217251532477] (width 0.03469637698843242 ≤ 0.3: True).

b_nat reproduces P1's finding on a fresh salt (0.3063773429719756 / 0.3317152396666109 here
against P1's 0.3217400470171695 / 0.34654236945734695), so the object being decomposed is the same
object P1 measured.

### 2.1 The honest magnitude caveat

b_cf is POSITIVE at both cells by the registered classification — the CI
excludes zero and is not wholly inside the ±0.01 equivalence margin — but
at B1 the CI **straddles** that margin ([0.009829531824123106, 0.02099405067675933] against a margin edge of
0.01), and at B2 it sits mostly inside it ([0.00559827343632706, 0.016261954399254843]). So the genuine
scaffold is real and signed, and its size is at the very edge of what this leg
declared interesting. L-1p2's "genuine-survives" resolves YES; it resolves
narrowly.

## 3. The curves

| cell | s | R_nat | R_cf | G(s) = R_cf(s) - R_cf(0) | F(s) = [R_nat(s) - R_nat(0)] - G(s) |
|---|---|---|---|---|---|
| B1 | 0.0 | 0.1235343574492067 | 0.1235343574492067 | 0.0 | 0.0 |
| B1 | 0.25 | 0.13229270870621257 | 0.11948277133284631 | -0.0040515861163603895 | 0.012809937373366262 |
| B1 | 0.5 | 0.17943166001336808 | 0.12571327258079104 | 0.002178915131584344 | 0.053718387432577036 |
| B1 | 0.75 | 0.27503495194865474 | 0.13202722932071947 | 0.008492871871512778 | 0.14300772262793526 |
| B1 | 1.0 | 0.4351349145429551 | 0.13647512639739026 | 0.012940768948183565 | 0.2986597881455648 |
| B2 | 0.0 | 0.127872827136617 | 0.127872827136617 | 0.0 | 0.0 |
| B2 | 0.25 | 0.14541045794189092 | 0.13056657450706122 | 0.002693747370444227 | 0.014843883434829702 |
| B2 | 0.5 | 0.1925347409657412 | 0.1314681944399098 | 0.0035953673032928235 | 0.06106654652583138 |
| B2 | 0.75 | 0.29050291216454177 | 0.1381829995603561 | 0.010310172423739106 | 0.15231991260418568 |
| B2 | 1.0 | 0.4699706496085552 | 0.13770129663633365 | 0.009828469499716663 | 0.33226935297222154 |

R_nat climbs steeply and convexly; **R_cf is nearly flat**. At B1 R_cf runs
0.1235343574492067 → 0.13647512639739026 while R_nat runs 0.1235343574492067 → 0.4351349145429551; at B2
R_cf runs 0.127872827136617 → 0.13770129663633365 against R_nat 0.127872827136617 → 0.4699706496085552.
The gap between the two curves IS F(s), and it grows with dose.

| cell | quadratic coefficient on R_nat | quadratic coefficient on R_cf | linear slope b_nat | linear slope b_cf | note |
|---|---|---|---|---|---|
| B1 | 0.4013115009173945 | 0.01952276786062412 | 0.3063773429719756 | 0.015370398353696113 | descriptive, no verdict |
| B2 | 0.4282332588027763 | -0.0006145318872409868 | 0.3317152396666109 | 0.010909345621091282 | descriptive, no verdict |

The dose forms differ qualitatively, which is the clearest statement of the
finding: R_nat is strongly convex (quadratic 0.4013115009173945 / 0.4282332588027763) while
R_cf is essentially linear-to-flat (0.01952276786062412 / -0.0006145318872409868). P1's convexity was
a property of frame-vs-frame agreement, not of person-reading. Descriptive
only — no verdict rides on the form (RN-P2-10).

### 3.1 The slope algebra, proven not asserted

| cell | b_cf from arm means | OLS witness on all 5n points | identity holds | b_nat from arm means | OLS witness |
|---|---|---|---|---|---|
| B1 | 0.015370398353696113 | 0.015370398353695105 | True | 0.3063773429719756 | 0.30637734297197566 |
| B2 | 0.010909345621091282 | 0.010909345621090144 | True | 0.3317152396666109 | 0.3317152396666109 |

## 4. G0p2 — the citations

| clause | expected | persisted / recomputed | bit-exact |
|---|---|---|---|
| base-cell r B1 (share 0.25, phi 0.05) | 0.785015540293945 | 0.785015540293945 | True |
| base-cell r B2 (share 0.25, phi 0.6) | 0.7558507450373838 | 0.7558507450373838 | True |
| P1 B1 CI | [0.3125381894506993, 0.3316075999536289] | [0.3125381894506993, 0.3316075999536289] | True |
| P1 B1 slope | 0.3217400470171695 | 0.3217400470171695 | True |
| P1 B2 CI | [0.3383230195793485, 0.3553320781635022] | [0.3383230195793485, 0.3553320781635022] | True |
| P1 B2 slope | 0.34654236945734695 | 0.34654236945734695 | True |
| P1 arm B1 s=0.0 mean | 0.11873302020953876 | 0.11873302020953876 | True |
| P1 arm B1 s=1.0 mean | 0.44047306722670826 | 0.44047306722670826 | True |
| P1 arm B2 s=0.0 mean | 0.12904388025689947 | 0.12904388025689947 | True |
| P1 arm B2 s=1.0 mean | 0.47558624971424646 | 0.47558624971424646 | True |
| P1 calibration worst error | 1.8675090942348197e-16 | 1.8675090942348197e-16 | True |
| P1 injection pin | 'scripts/run_suica_m4_k2b_t4_branch.py:377' | 'scripts/run_suica_m4_k2b_t4_branch.py:377' | True |
| P1 s=0 bit-identity held | True | True | True |
| P1 verdict | 'SIGN_SCAFFOLD' | 'SIGN_SCAFFOLD' | True |
| M2 C4 mean | 0.12239759528671845 | 0.12239759528671845 | True |

| property | value |
|---|---|
| the object | world['common']  (4, 16, 64) |
| **LAST read before the frozen map** | **`scripts/run_suica_m4_k2b_t4_branch.py:377`** |
| that source line | `v += w["common"] * world["common"][ctx_index[i], :m]` |
| emit_panel called at | `scripts/run_suica_m4_k2b_t4_branch.py:615` |
| frozen map entry at | `scripts/run_suica_m4_k2b_t4_branch.py:616` |
| matches P1's pin | True |
| k2b edited | False |
| suica_core edited | False |

## 5. G1p2 — the instrument

| clause | quantity | value | PASS |
|---|---|---|---|
| (a) zero-dose IS the plain construction | worlds checked | 16 | True |
| (a) | max \|difference\| in common | 0.0 |  |
| (b) T-cf differs from T-nat at s > 0 | worlds checked | 8 | True |
| (b) | min \|\|T-nat - T-cf\|\| | 50.7748011282207 |  |
| (b) | max \|\|T-nat - T-cf\|\| | 52.72388384718147 |  |
| (c) R_cf(0) == R_nat(0) | worlds checked | 8 | True |
| (c) | all bit-exact | True |  |
| (c) | all truth panels identical at s = 0 | True |  |
| (d) R_nat reproduces k2b's run_field_world | worlds checked | 8 | True |
| (d) | max \|difference\| | 0.0 |  |

All four clauses hold. (a) The zero-dose variant of every pilot world is
bit-identical to a fresh plain `build_k2b_world` at the same seed
(16 worlds, max |difference| 0.0). (b) At s > 0 the two truth
panels provably differ: ‖T-nat − T-cf‖ ∈ [50.7748011282207, 52.72388384718147]. (c) The
zero-point identity R_cf(0) ≡ R_nat(0) holds bit-exactly on all 8 worlds
— the hinge that makes G(0) = F(0) = 0. (d) This harness's reassembled gauge
path returns **exactly** what k2b's own `run_field_world` returns
(True, max |difference| 0.0).

| cell | world | R_nat | R_cf | bit-exact | k2b run_field_world | matches k2b |
|---|---|---|---|---|---|---|
| B1 | 0 | 0.14164901592891674 | 0.14164901592891674 | True | 0.14164901592891674 | True |
| B1 | 1 | 0.13551845334960413 | 0.13551845334960413 | True | 0.13551845334960413 | True |
| B1 | 2 | 0.06605973899243922 | 0.06605973899243922 | True | 0.06605973899243922 | True |
| B1 | 3 | 0.08299451610574286 | 0.08299451610574286 | True | 0.08299451610574286 | True |
| B2 | 0 | 0.12415152845390957 | 0.12415152845390957 | True | 0.12415152845390957 | True |
| B2 | 1 | 0.121081160997642 | 0.121081160997642 | True | 0.121081160997642 | True |
| B2 | 2 | 0.09982680757300594 | 0.09982680757300594 | True | 0.09982680757300594 | True |
| B2 | 3 | 0.15657829401685475 | 0.15657829401685475 | True | 0.15657829401685475 | True |

## 6. G2p2 — the pilot and the regime disclosure

| cell | s | n | R_nat mean | R_cf mean | variance ratio (mean) | variance ratio (max) | PASS |
|---|---|---|---|---|---|---|---|
| B1 | 0.0 | 4 | 0.10655543109417574 | 0.10655543109417574 | 0.12973397615232352 | 0.13382720799753453 | True |
| B1 | 1.0 | 4 | 0.41166671817244593 | 0.15002594327517194 | 0.3134936711052227 | 0.31927813864521354 | True |
| B2 | 0.0 | 4 | 0.12540944776035307 | 0.12540944776035307 | 0.12857355880070254 | 0.13104839240361138 | True |
| B2 | 1.0 | 4 | 0.4481988124839972 | 0.10113893698863484 | 0.33248729263121546 | 0.3487370371692805 | True |

| quantity | value |
|---|---|
| max variance ratio over all arms | 0.35097712055652686 |
| bar | 10.0 |
| **REGIME_NOTE modifier** | **False** |
| definition | variance ratio = mean((context,occasion cell mean - grand mean)^2) / mean(author deviation^2) over every (author, occasion, dim) cell, the same centring K1's calibration uses; > 10 at any arm sets REGIME_NOTE |

The largest common-to-author response-level variance ratio over every arm is
0.35097712055652686, far below the 10.0 bar, so **no REGIME_NOTE**: even at s = 1.0
the author-specific variance still dominates the common component. The dosed
regime is not a degenerate one.

## 7. G3p2 — the projection

| quantity | value |
|---|---|
| sigma source | the pilot's zero-dose (s = 0) worlds, R_cf, pooled within base cell |
| pooled df | 6 |
| sigma_raw | 0.031389273730078826 |
| inflation factor (chi2 q = 0.1) | 1.6498974741130894 |
| **sigma (df-inflated)** | **0.051789083441501405** |
| sum (s_j - s_bar)^2 | 0.625 |
| SE(b-hat) formula | SE(b-hat) = sigma / sqrt(n * 0.625) (RN-P2-8) |
| SE(b-hat) at n = 192 | 0.004727674872237933 |
| **MDE(2 SE)** | **0.009455349744475866** |
| bar | 0.01 |
| **PASS** | **True** |
| escalation fired | False |
| worlds per arm decided | 192 |

σ from the pilot's zero-dose worlds (df 6), df-inflated ×1.6498974741130894:
0.031389273730078826 → 0.051789083441501405. Five equally-replicated levels give
Σ(s_j − s̄)² = 0.625, so SE(b̂) = σ/√(n·0.625) = 0.004727674872237933 and
**MDE(2·SE) = 0.009455349744475866 ≤ 0.01**. Escalation did not fire (False).

## 8. Routing

| # | condition | outcome |
|---|---|---|
| 1 | any G0p2/G1p2 failure | STOP |
| 2 | projection fails after escalation | NON_PROJECTABLE (handback) |
| 3 | both cells POSITIVE on R_cf | **GENUINE_SCAFFOLD -- frame content genuinely improves person-reading against a frame-fixed truth; f quantifies the split**  <-- THIS LEG |
| 4 | both cells NULL on R_cf | PURE_FRAME_AGREEMENT -- the P1 boost is entirely frame-vs-frame; the gauge does not read the person better, it reads the frame; the penalty's mechanism re-types accordingly (major theory note) |
| 5 | both cells NEGATIVE on R_cf | SCAFFOLD_TRADEOFF -- frame content actively costs person-reading while inflating apparent recovery; theory note |
| 6 | cells disagree or any UNDERPOWERED | SPLIT_OR_UNDERPOWERED -- named; P3 inherits the diagnosis |

## 9. Gates

| gate | PASS | detail |
|---|---|---|
| G0p2 | True | P1's slopes, CIs, arm means, calibration record and injection pin bit-exact; base-cell r bit-exact; M2's C4 bit-exact |
| G1p2 | True | zero-dose variant IS the plain construction; T-cf differs from T-nat at s > 0; R_cf(0) == R_nat(0) bit-exactly; R_nat reproduces k2b's run_field_world |
| G2p2 | True | rule-29 predicate on BOTH R_nat and R_cf at every pilot and full arm; variance ratios disclosed per arm |
| G3p2 | True | MDE(2 SE) on the R_cf slope = 0.009455349744475866 <= 0.01; escalation fired: False |
| G4p2 | True | routing disjoint-and-covering; classification disjointness pinned NULL-first per #55; rule-27 budget on f applied; tables generated |

## 10. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G3p2 | MDE(2 SE) on the R_cf slope <= 0.01 | — | one-sided |
| L-1p2 | genuine-survives(+) / all-frame(NULL) / other | 0.55 / 0.30 / 0.15 | categorical |
| L-2p2 | f > 0.5 at s = 1.0 | 0.55 | one-sided |
| rule27 | f's 95% CI width <= 0.3 | — | one-sided |

## 11. Pinned readings

| note | pinned reading |
|---|---|
| RN-P2-1 | injection point inherited from P1: world['common'], k2b:337 built, :349 returned, :377 last read inside emit_panel, called :615 one line before the frozen map at :616; delta added for EVERY context; k2b unedited |
| RN-P2-10 | linear and quadratic dose-form fits are descriptive with no verdict attached -- nothing downstream consumes the form yet (the N-line lesson) |
| RN-P2-2 | K1's own (context, occasion)-centred author-mean deviation RMS controls (k1:337-361); delta rescaled so the REALIZED response-level RMS equals s x that quantity exactly |
| RN-P2-3 | arm tags carry NO s, so every dose arm shares the identical corpus string at a matched world index -- the registration's pinned requirement after P1's machinery finding |
| RN-P2-4 | R_nat and R_cf share ONE gauge pass and ONE calibration, scored against two truth panels; a second calibration would confound the truth swap with a calibration swap. G1p2(d) proves R_nat is bit-identical to k2b's own run_field_world |
| RN-P2-5 | at s = 0 the two variants are the same array, so R_cf(0) == R_nat(0) must hold bit-exactly; checked on every pilot world because it is the hinge that makes G(0) = F(0) = 0 |
| RN-P2-6 | variance ratio = mean((context,occasion cell mean - grand mean)^2) / mean(author deviation^2) over every (author, occasion, dim) cell, the same centring K1's calibration uses; > 10 at any arm sets REGIME_NOTE |
| RN-P2-7 | NULL is tested FIRST (CI inside the equivalence margin, rule 4), then sign, then UNDERPOWERED -- #55's convention, now in the registration; the sign-first ordering is still computed and reported |
| RN-P2-8 | five equally-replicated levels give sum (s_j - 0.5)^2 = 0.625, so b-hat = sum_j (s_j - 0.5) * ybar_j / 0.625 and SE = sigma / sqrt(n*0.625); every arm contributes |
| RN-P2-9 | f is bootstrapped jointly with its denominator (one resample drives both) so the ratio's correlation is preserved; rule-27 budget is a 95% CI width <= 0.30, else DESCRIPTIVE-ONLY and UNQUANTIFIED |

## 12. Rule events

- **Rule 13:** 0 boundary events; no B = 20000 re-run.
- **Rule 26:** no bounded winner.
- **Rule 27:** f's budget is a 95% CI width ≤ 0.3; realized 0.03975319873797811
  and 0.03469637698843242, so f is QUANTIFIED at both cells and no UNQUANTIFIED modifier
  applies.
- **Rule 29:** in force as G2p2, applied to BOTH R_nat and R_cf at every arm.
- **Rule 30:** every cited constant verified against its persisted source before
  Part 0; all twelve P1 citations bit-exact.

## 13. What this does and does not license

**Licensed.** The scaffold mechanism P1 named is genuine but small: holding the
truth side frame-fixed, more common-frame content still improves person-reading,
at both φ levels, with CIs excluding zero. P1's SIGN_SCAFFOLD stands as a sign.

**Not licensed — and this qualifies P1 substantially.** The magnitude P1
reported was overwhelmingly frame-vs-frame agreement: 95.8470007021553% and
97.1270002747466% of the boost disappears the moment the truth panel is held
frame-fixed. Any reading of P1 that treated +0.32 as "how much better the gauge
reads people under more frame" is wrong by a factor of about twenty. The
convexity P1 reported is likewise a property of F, not of G.

## 14. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 15. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

## 16. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 90 | 0.025 |
| pilot | 60 | 14.061 |
| project | 20 | 0.003 |
| arm B1 s=0.0 | 150 | 112.334 |
| arm B1 s=0.25 | 150 | 115.695 |
| arm B1 s=0.5 | 150 | 115.851 |
| arm B1 s=0.75 | 150 | 112.832 |
| arm B1 s=1.0 | 150 | 113.686 |
| arm B2 s=0.0 | 150 | 114.753 |
| arm B2 s=0.25 | 150 | 112.323 |
| arm B2 s=0.5 | 150 | 112.644 |
| arm B2 s=0.75 | 150 | 115.910 |
| arm B2 s=1.0 | 150 | 114.073 |
| fit | 120 | 0.158 |
| finalize | 60 | 0.001 |

---

*Artifacts: `results/m4_p2_dose_decomposition/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`, `fit.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `run_log.jsonl`.
Harness: `scripts/run_suica_m4_p2_dose_decomposition.py`.*
