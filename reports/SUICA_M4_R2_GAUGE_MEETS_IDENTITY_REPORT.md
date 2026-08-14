# SUICA M4-R2 — the gauge meets the identity channel

**Outcome: `INTERFERENCE_MISPRICED`** (rule-16 cell 6). Modifiers: INTERFERENCE_REAL_BUT_SMALLER_THAN_PRICED.

Registered before the run in `docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md`
("M4-R2", commit 49b5161). EXPLORATORY, synthetic, label-free. The identity
channel here is **planted**, not discovered: nothing in this leg bears on the
k2b family's own worlds.

## 1. What was asked

R1/R1b certified a planted identity channel. This leg puts the gauge in front
of it and asks whether the program's own laws predict what happens.

1. **Interference (SEALED).** Does identity crowd out biography at the price
   the N-line tax curve names?
2. **Within-frame style reading (DESCRIPTIVE, #59).** At equal weights trait
   and style are exchangeable, so R_S ≈ R_T is a symmetry, not a finding.
3. **Cross-frame style reading (VERDICT, NULL-first).** Style is present in
   both worlds of a pair. Can the gauge read it across frames?

## 2. The registration defect that had to be pinned first

The registration derives V_eff from "the share accounting of
`person_share_design`'s own semantics". That function's **implementation**
(3.12.12 run, `scripts/run_suica_m4_k2e_double_matching.py:240`) is literally
`shares["slow"] + shares["int"]` — which excludes the `mu` channel where style
lives. Under that literal reading, adding style *raises the denominator* and
**lowers** V_eff, making the sealed prediction **positive** (0.006457447033500374). That
contradicts the registration's own mechanism sentence in the same paragraph —
style "adds author-persistent variance, **raising** the effective person share"
— and its sanity value (-0.06).

This was pinned as **RN-R2-1 before any hypothesis-relevant number existed**,
with all three readings computed and reported:

| reading | V_eff(w=1) | V at w=0 | reduces to V_design? | inside fitted domain? | prediction | routing? |
|---|---|---|---|---|---|---|
| A_literal_slow_int | 0.06739312791998867 | 0.07497350894214899 | True | True | 0.006457447033500374 | no |
| B_slow_int_mu | 0.269597162241333 | 0.18744244965979676 | False | False | -0.13444453250196647 | no |
| C_routing_slow_int_style | 0.16849932384036667 | 0.07497350894214899 | True | True | -0.07198402428539213 | **YES** |

The routing reading is **C**, on four independent grounds: it is the function's
*semantics* (the author-persistent share that is **not** the target trait —
`slow`+`int` were exactly that set before a style channel existed; #56,
inheritance is not exemption); it reduces to V_design exactly at w = 0; it lands
inside M3's fitted domain; and it is the only reading consistent with the
registration's stated mechanism. Reading A inverts the sign; reading B fails the
w = 0 reduction and extrapolates outside the fitted domain. The planner's sanity
value corroborates C but does **not** gate it (rule 30 — expressly approximate,
"executor recomputes"; the RN-Q2-6 precedent).

## 3. The sealed prediction and its band

α(V) = c − κ0·V + (κ2/2)·V² from M3's persisted A-quad, consumed not refitted.
α(0.07500000000000002) = 0.1448569748507095 → α(0.16849932384036667) = 0.07287295056531737.

| term | value | note |
|---|---|---|
| prediction alpha(V_eff) - alpha(V_design) | -0.07198402428539213 | V_design 0.07500000000000002 -> V_eff 0.16849932384036667 |
| SE_pred | 0.0006102321051948493 | M3 parameter covariance, c cancels |
| SE_meas | 0.0014077434928863272 | paired probe spread scaled to n=192 |
| SE_approx | 0.00613560574702563 | RN-R2-5, three parts below |
|   r-channel shift | 0.0061129257838192326 | gain g = 0.9150794104038479 (R_T probe w0 0.13255563513927227) |
|   V_eff spread | 6.0788117635513934e-05 | across probes |
|   mu non-additivity | 0.0005235466065273388 | realized trait/style cross term through the curve |
| combined SE | 0.006324538152854189 | root sum of squares |
| **half-width** | **0.012649076305708377** | 2 x combined (#61) |
| band | [-0.08463310059110052, -0.05933494797968376] | two-sided containment |

The **r-channel shift** is the honest part: this split-seed instrument reads
0.13255563513927227 at w = 0 where M3's own curve says 0.1448569748507095, a gain of 0.9150794104038479. The
curve's currency is not exactly ours, and the #61 convention requires that to
sit inside SE_approx rather than be wished away.

`prediction.json` was hashed `bb15b6104d302ebe…` and stamped 2026-08-14T09:05:07.805460+00:00 with
**0 fresh-arm worlds in existence** (64 probe worlds
necessarily precede it — they are the band's inputs). The arms re-read the stamp
from disk and re-hashed to a match at 2026-08-14T09:10:08.122166+00:00, 300.316706 s later.

## 4. Gates

| gate | PASS | detail |
|---|---|---|
| G0r2 | True | R1 INSTRUMENT_DEFECT(C-R1c); R1b IDENTITY_CHANNEL_CERTIFIED; curve A-quad CONSUMABLE; OLS refit agrees with persisted theta: True |
| G1r2 | True | C2-style battery on 4 fresh probes; truth panels differ (norm 75.95815947359351) |
| G2r2 | True | rule-29 predicate on all three scorings, 4 pilot pairs |
| G3r2 | True | escalation fired: False; n_final 192 |

| truth | role | value | bar | P | PASS |
|---|---|---|---|---|---|
| V-R2c: R_S_ref = 0 | false-fire | 0.0 | 0.1 | 0.0445 | True |
| V-R2c: R_S_ref = R_S_nat(w=1) | power | 0.11604558797607575 | 0.8 | 1.0 | True |
| curve truth | power | -0.07198402428539213 | 0.8 | 1.0 | True |
| no interference (dR_T = 0) | false-fire | 0.0 | 0.1 | 0.0 | True |

## 5. Results

| dose | quantity | mean | SEM | CI95 |
|---|---|---|---|---|
| w0.0 | R_S_nat | 0.08866022322041145 | 0.0018294537504199699 | [0.08511398931526398, 0.09221931103709924] |
| w0.0 | R_S_ref | 0.002162645511438138 | 0.0015933073704822631 | [-0.0010517556453162877, 0.005264892028748913] |
| w0.0 | R_T_nat | 0.12425035254824575 | 0.001917131635278812 | [0.1204021065903167, 0.12801440822541346] |
| w1.0 | R_S_nat | 0.11918288935300352 | 0.0017817614927814818 | [0.11571186797190161, 0.12272356761166413] |
| w1.0 | R_S_ref | -0.00023760593803822915 | 0.001678634713857152 | [-0.003466065037245123, 0.0030851230404383635] |
| w1.0 | R_T_nat | 0.11806906162144237 | 0.0018561779762658866 | [0.11451673565874035, 0.12162334526426907] |

| verdict | measured | CI95 | reference | result |
|---|---|---|---|---|
| V-R2a (sealed containment) | -0.00618129092680336 | [-0.008110727559547634, -0.004257287226729858] | band [-0.08463310059110052, -0.05933494797968376] | **OUTSIDE** |
| V-R2a position in band | 5.202176962826352 | - | inside iff \|pos\| <= 1 | False |
| V-R2c (R_S_ref at w=1, NULL-first) | -0.00023760593803822915 | [-0.003567179813180193, 0.0030463008905367156] | eps 0.003493124558101321 | **INDETERMINATE** |

### 5.1 The sealed test

Measured ΔR_T = -0.00618129092680336 [-0.008110727559547634, -0.004257287226729858] against a predicted -0.07198402428539213 — position
5.202176962826352 of the half-width, **OUTSIDE**. Against zero: the 2·SEM equivalence
scale is 0.0019574803627175267, so the null-first classification is not null — the effect is distinguishable from zero.

Interference is real and the gauge reads biography less well when identity is planted, but the curve OVERPRICES it by a factor of 11.64546777328575. R_T_nat moves 0.12425035254824575 → 0.11806906162144237.

| reading | prediction | signed error | position | would be inside? |
|---|---|---|---|---|
| A_literal_slow_int | 0.006457447033500374 | -0.012638737960303733 | -0.9991826798135466 | True |
| B_slow_int_mu | -0.13444453250196647 | 0.1282632415751631 | 10.140127110884725 | False |
| C_routing_slow_int_style | -0.07198402428539213 | 0.06580273335858877 | 5.202176962826352 | False |

**This is the disclosure that matters most in this leg.** The routing reading misses, but **A_literal_slow_int** (prediction 0.006457447033500374, position -0.9991826798135466, inside by only 0.0008173201864534185 of the half-width, and with the WRONG SIGN) would have contained the measurement. Had that reading been pinned, the leg would have routed to a different cell entirely. The pin was made in Part 0 before any hypothesis-relevant number existed, on four stated grounds, and all three readings were persisted then — which is the only reason this sentence can be written at all rather than discovered by a reader.

Two things keep that from rescuing reading A on the merits. Its prediction has the **opposite sign** to the measurement (0.006457447033500374 against a measured -0.00618129092680336, whose CI [-0.008110727559547634, -0.004257287226729858] excludes zero), so it is not describing the effect that occurred. And it clears the bar by grazing it: the half-width 0.012649076305708377 is 2.046348643915037 times the whole measured effect, so at this scale the band is too wide to discriminate a small negative interference from a small positive one. The honest reading is that BOTH candidate prices are wrong and the band is too coarse to adjudicate between them — not that the literal reading was right.

### 5.2 The cross-frame identity reading

R_S_ref(w=1) = -0.00023760593803822915 [-0.003567179813180193, 0.0030463008905367156] against ε = 0.003493124558101321 → **INDETERMINATE**.

The gauge reads essentially nothing of the planted identity across frames: the
point estimate is -0.00023760593803822915 against a null anchor of 0.002162645511438138, and identity
is unambiguously present in both worlds (C-R1b, re-certified in G1r2).

**A stability disclosure that cuts against the tidy reading.** The classification
sits on a knife edge. The lower CI edge misses −ε by -7.405525507887204e-05, which is
-0.7385675960969138 of the Monte-Carlo standard error of that percentile at the registered
B = 2000 (0.00010026875734899506). At B = 20000 the interval is [-0.003471613813457244, 0.0030552232664270047] and the
classification would be **NULL**. Q2's rule-13 trigger asks whether a
boundary's *tail fraction* is within Monte-Carlo noise and is silent here,
because this instability lives in the *percentile value* instead — it did not
fire (False). The registered B = 2000 classification is what is reported and
what routes; the high-B reading is a disclosed diagnostic, **not** a
re-resolution. Nothing turns on the choice: cell 6 fires on V-R2a alone,
so the outcome slug is identical under both. This is offered to the planner as a
convention candidate, not resolved here.

### 5.3 Descriptive readings (gate nothing)

| reading | value | CI95 | label |
|---|---|---|---|
| R_S_nat(w=1) | 0.11918288935300352 | - | descriptive |
| R_T_nat(w=1) | 0.11806906162144237 | - | descriptive |
| R_S_nat - R_T_nat (w=1) | 0.0011138277315611274 | [-0.0015157844324500396, 0.003842021426323359] | DESCRIPTIVE ONLY -- exchangeability, gates nothing (#59) |
| ratio R_S/R_T (w=1) | 1.0094336968234094 | - | exchangeability |
| R_S_nat(w=0) | 0.08866022322041145 | [0.08501723626019096, 0.09215060281288272] | null ANCHOR, not a verdict |
| R_S_ref(w=0) | 0.002162645511438138 | - | null anchor |

At w = 1 trait and style enter exchangeably, and the measured ratio R_S/R_T =
1.0094336968234094 is that symmetry, not a discovery (#59, RN-R2-6).

**The registration's expectation for the w = 0 anchor is not met, and the reason
is structural.** It expected R_S_nat(w = 0) ≈ 0 — style drawn but weightless, so
nothing to read. The measured anchor is 0.08866022322041145, close to R_T_nat's own
0.12425035254824575. The cause is the pipeline's truth-panel convention, which this leg
inherited unchanged and pinned in Part 0: truth panels are
`emit_panel(world, w, active=("mu","common"))`, so **they carry the frame**. At
w = 0 the gauge is shown no style whatsoever, yet the style truth panel still
contains that world's `common` channel, and the gauge agrees with *that*. The
anchor is measuring frame agreement, not style reading. It is an anchor and not
a verdict, so nothing routes on it — but the expectation was wrong and the
number should not be read as the registration framed it.

This matters for §5.2. `R_S_ref(w=1) vs 0` conflates "the gauge cannot read
style across frames" with "the frame does not transport" — the latter already
established by the whole P-line. The frame-controlled contrast is the paired
increment over the w = 0 arm, which holds the frame path fixed and varies only
whether the gauge was shown any style:

| contrast | mean | CI95 | excludes zero? | reading |
|---|---|---|---|---|
| R_S_ref(w=1) - R_S_ref(w=0)  [cross-frame, frame-controlled] | -0.002400251449476367 | [-0.004531674544523817, -0.00036827981268627977] | True | style bought across frames |
| R_S_nat(w=1) - R_S_nat(w=0)  [within-frame, same control] | 0.030522666132592052 | [0.02844019394597627, 0.032630214283184106] | True | style bought within frame |
| ratio cross / within | -0.07863832861289213 | - | - | fraction of the readable identity that survives a frame refresh |

The cross-frame increment is -0.002400251449476367 [-0.004531674544523817, -0.00036827981268627977] (excludes zero: True), against
a within-frame increment of 0.030522666132592052 [0.02844019394597627, 0.032630214283184106] — a ratio of -0.07863832861289213. Showing the
gauge a full-strength identity channel buys it **nothing** it can read through a
refreshed frame, while the same channel is plainly readable within frame. That
is the sharper statement of the P-line's limitation, and it is a diagnostic
offered alongside the registered verdict, not a replacement for it.

## 6. Anomalies

1. **A-1 (before any number).** The dispatched interpreter was absent; a pinned
   CPython venv was built from `requirements-lock-main.txt` and recorded:
   `/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python`.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-4 (disclosed ordering fact, before the stamp).** The band's SE_meas has
   to come from pre-measurement objects, so the 16 probe pairs were scored at
   *both* doses before `prediction.json` was sealed — which means a paired
   probe ΔR_T (-0.01589391381974946) existed before the stamp. It was **never consumed**:
   the prediction is `α(V_eff) − α(V_design)`, built from variance shares and
   M3's persisted θ with no R term in it at all; SE_meas takes only the probe
   difference's *standard deviation*; the gain g takes only the *w = 0 level*.
   The probe difference's **mean** enters no expression that routes (#57 —
   variances only). It is reported here rather than omitted, because the
   alternative to disclosing it is asking the reader to trust that it was not
   used.
4. **A-3 (before any number).** Two machinery hazards were caught while writing
   the harness, both from prior legs' scars: the corpus string must not encode
   the dose (RN-P1-8 — it enters the frozen map, and a w-dependent corpus would
   contaminate ΔR_T at its root), and seeds must depend on the pair index only
   so the doses are bit-paired (RN-R2-3). Both were fixed before any world was
   built.

## 7. Boundary

EXPLORATORY, synthetic, label-free. One share, one φ, two doses. The identity
channel is planted; appendix KK's structural boundary is unmoved. V-R2a's miss is a failure of the LAW'S TRANSPORT, not of the instrument — the channel is certified by R1/R1b and the r-channel shift is inside the band, so the curve is what did not carry. The
measurement itself is precise: 192 paired pairs, SEM 0.0009787401813587634.

## 8. Environment

`/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python` — Python 3.12.12.
