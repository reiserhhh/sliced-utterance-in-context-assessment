# SUICA M4-R2b — the channel-specific tax

**Outcome: `TAX_IS_CHANNEL_SPECIFIC`** (rule-16 cell 3). Modifiers: MU_TAX_FIRST_INTERVAL_CONSISTENT_WITH_R2, SLOW_OVER_MU_RATIO_11.9X.

Registered before the run in `docs/SUICA_M4_R_IDENTITY_CHANNEL_LINE_PLAN.md`
("M4-R2b", commit 4bece27). EXPLORATORY, synthetic, label-free. The mu channel
is **planted**; nothing here bears on the k2b family's own worlds.

## 1. The question

R2 found interference real but 11.65× cheaper than the N-line curve prices. The
hypothesis that forces: **the tax is channel-specific** — κ(V) is the tax on
STATE (slow-channel) person variance, while author-constant (mu-channel) person
variance is taxed an order lighter. This leg measures the two taxes apart and
tests the curve against its own channel.

**The curve holds on its own channel.** Measured against a secant fixed before any world existed, the slow-channel tax lands inside the band — so the N-line law is not broken; it was simply being asked about the wrong channel in R2. The discrimination is clear: the slow-channel tax is 11.931517127829927x the mu-channel tax, and D_channel's CI excludes zero. Author-constant person variance is taxed an order lighter than state variance.

## 2. Two registration defects, pinned before any number

**RN-R2B-1 — "four base cells" but only two named.** The registration's design
sentence says four base cells, eight arms, 192 worlds each, 1536 total; it names
two base cells, and two cells × two doses is four arms. The 2×2 factorial
{share 0.10, 0.25} × {φ_A, 0.05} is the unique reading satisfying all four
numbers at once while keeping the named matched-r pair as its diagonal. Every
registered estimand is computed on the diagonal exactly as specified; the two
off-diagonal cells route nothing. They also make S2's φ-transport SE_approx
estimable from pre-measurement objects, which the two-cell reading could not.

**RN-R2B-2 — the κ_slow operand order inverts the sealed sign.** The
registration writes κ_slow = −[R_T(0.10 cell) − R_T(0.25 cell)]/ΔV_slow. The
0.10 cell is the LOW-V cell, where α is higher, so that bracket is positive and
the formula returns a **negative** tax rate — while S1's own prediction (the
curve's secant) is positive, the cited N1b context value (0.918) is
positive, and κ_mu by the registration's own formula is positive. Under the
literal order, S3's `D_channel > 0` could not fire even under perfect channel
specificity. The pinned estimator is the standard secant orientation. Under the
literal orientation the same measurement reads -0.8916930095784603; it routes nothing.

## 3. The matched-r design and the channel coverage

| quantity | value | check |
|---|---|---|
| N1 root φ (share 0.10) | 0.8991793501377106 | persisted |
| N1 partner φ (share 0.25) | 0.05 | persisted |
| r recomputed, cell A | 0.7850155393518391 | bit-exact vs N1: True |
| r recomputed, cell B | 0.785015540293945 |  |
| **matched-r residual** | **9.421059488090577e-10** | bar 1e-9 → PASS True |
| ΔV_slow | 0.04500000000000001 | matches registration: True |
| V̄ | 0.05250000000000002 | matches registration: True |

Channel coverage is **named**, per defect #62:

| item | value |
|---|---|
| channels COUNTED in V_C | slow, int, mu_style |
| channels NOT counted | mu_trait, common, noise |
| denominator | sum over the split channel set {mu_trait, mu_style, slow, int, common, noise} of the pipeline's own emit_panel mean-square |
| ΔV_mu cell A (share 0.10, φ_A) | 0.11559817906203051 |
| ΔV_mu cell B (share 0.25, φ 0.05) | 0.0936937639492188 |
| ΔV_mu cell C (share 0.10, φ 0.05) | 0.11559260516359365 |
| ΔV_mu cell D (share 0.25, φ_A) | 0.09370518236340336 |
| R2's ΔV_mu, same convention | 0.09349932384036665 |

## 4. The sealed predictions

| # | quantity | prediction | SE_pred | SE_meas | SE_approx | half-width | band |
|---|---|---|---|---|---|---|---|
| S1 | kappa_slow(w=0) | 0.8781169374706214 | 0.018153303376024638 | 0.02837886038389424 | 0.11143041830656614 | 0.23282302518545592 | [0.6452939122851654, 1.1109399626560772] |
| S2 | kappa_mu(share 0.25) | 0.06611054147682188 | 0.010467885126418528 | 0.013220535408554501 | 0.009559166315632583 | 0.03876786484492857 | [0.027342676631893312, 0.10487840632175045] |

| sealed test | SE_approx component | value |
|---|---|---|
| S1 | r-channel gain | 0.11090563637241162 |
| S1 | gain spread between diagonal cells | 0.010801756561146904 |
| S1 | matched-r residual / ΔV_slow | 2.0935687751312393e-08 |
| S1 | gain (cell A / cell B / mean) | 0.8860016524682809 / 0.861399561106142 / 0.8737006067872115 |
| S2 | φ-transport (probe κ_mu at φ_A vs φ 0.05, same share) | 0.0095581776062717 |
| S2 | ΔV_mu design difference vs R2 | 0.0001374827148801085 |
| S3 | projected SE_D | 0.035681134281302054 |

`prediction.json` hashed `4d7ad4473c153df6…`, stamped 2026-08-14T09:31:33.321809+00:00 with **0 fresh
worlds in existence** (128 probe worlds precede it by necessity — they are
the bands' inputs). Arms re-read the stamp and re-hashed to a match at
2026-08-14T09:40:59.905069+00:00, 566.58326 s later.

## 5. Gates

| gate | PASS | detail |
|---|---|---|
| G0r2b | True | N1 roots bit-exact (True), matched-r residual 9.421059488090577e-10 <= 1e-9, M3 A-quad CONSUMABLE, OLS refit agrees (True), R2 numbers at source |
| G1r2b | True | probe battery on 16 worlds x 8 arms; ΔV_mu realized and all positive (True); channel coverage named |
| G2r2b | True | rule-29 predicate, 4 pilot worlds |
| G3r2b | True | escalation fired: False; n_final 192 |

| truth | role | value | bar | P(S3 clear) | PASS |
|---|---|---|---|---|---|
| R2-based truth (secant - R2 kappa_mu) | power | 0.8120063959937995 | 0.8 | 1.0 | True |
| uniform tax (D = 0) | false-fire | 0.0 | 0.1 | 0.023 | True |

## 6. Results

| arm | cell | share | φ | V_design | w_style | role | R_T mean | SEM | CI95 |
|---|---|---|---|---|---|---|---|---|---|
| A_w0.0 | A | 0.1 | 0.8991793501377106 | 0.03000000000000001 | 0.0 | matched-r diagonal (V lo) | 0.164672289417317 | 0.0017868998871530593 | [0.1612335849890764, 0.16822160030049538] |
| A_w1.0 | A | 0.1 | 0.8991793501377106 | 0.03000000000000001 | 1.0 | matched-r diagonal (V lo) | 0.15379590097977083 | 0.0017234826724551594 | [0.15053636454268765, 0.15717092425262852] |
| B_w0.0 | B | 0.25 | 0.05 | 0.07500000000000002 | 0.0 | matched-r diagonal (V hi) | 0.1245461039862863 | 0.0017730233009208623 | [0.12109773530677781, 0.12794580742934708] |
| B_w1.0 | B | 0.25 | 0.05 | 0.07500000000000002 | 1.0 | matched-r diagonal (V hi) | 0.11754397060630366 | 0.00177304295710994 | [0.11420136412324544, 0.12099319550527216] |
| C_w0.0 | C | 0.1 | 0.05 | 0.03000000000000001 | 0.0 | off-diagonal (diagnostic) | 0.16188985458273378 | 0.0018507415142690364 | [0.15827421462382915, 0.16553862523009355] |
| C_w1.0 | C | 0.1 | 0.05 | 0.03000000000000001 | 1.0 | off-diagonal (diagnostic) | 0.15001501736373749 | 0.0018105732516768866 | [0.14652029557514612, 0.15354859637038035] |
| D_w0.0 | D | 0.25 | 0.8991793501377106 | 0.07500000000000002 | 0.0 | off-diagonal (diagnostic) | 0.13148070068787887 | 0.001698535531561973 | [0.12826213338394463, 0.134780477242385] |
| D_w1.0 | D | 0.25 | 0.8991793501377106 | 0.07500000000000002 | 1.0 | off-diagonal (diagnostic) | 0.12584818971005984 | 0.0016475059785898368 | [0.12267730533641687, 0.12906474081084682] |

| estimand | mean | SEM | CI95 | role |
|---|---|---|---|---|
| κ_slow(w=0) | 0.8916930095784603 | 0.022089156605046813 | [0.8502517263399952, 0.9350975324766414] | **routes (S1, S3)** |
| κ_slow(w=1) | 0.8055984527437156 | 0.021820303677394126 | [0.7635291763629583, 0.8475386564029389] | consistency reading |
| κ_mu(share 0.25, cell B) | 0.07473425215127182 | 0.010745690639154886 | [0.05386916320637429, 0.09553678214715175] | **routes (S2, S3)** |
| κ_mu(share 0.10, cell A) | 0.09408788724699418 | 0.009615167312579788 | [0.07563755345934248, 0.11248055877183495] | consistency reading |
| κ_mu(cell C, off-diagonal) | 0.10273007691270834 | 0.009653743676393177 | [0.08391829762695768, 0.12162253281913721] | diagnostic (RN-R2B-1) |
| κ_mu(cell D, off-diagonal) | 0.06010885242157973 | 0.010687497886351111 | [0.03936564266171661, 0.0809412505186524] | diagnostic (RN-R2B-1) |
| κ_slow(w=0), registration's literal orientation | -0.8916930095784603 | - | [-0.9350975324766414, -0.8502517263399952] | RN-R2B-2, routes nothing |
| **D_channel** | **0.8169587574271885** | 0.02517573809457751 | [0.770561523979914, 0.8692603102466345] | **routes (S3)** |

| test | measured | CI95 | prediction / bar | position | result |
|---|---|---|---|---|---|
| S1 κ_slow(w=0) containment | 0.8916930095784603 | [0.8502517263399952, 0.9350975324766414] | 0.8781169374706214, band [0.6452939122851654, 1.1109399626560772] | 0.058310693699752815 | **INSIDE** |
| S2 κ_mu(0.25) containment (first-interval) | 0.07473425215127182 | [0.05386916320637429, 0.09553678214715175] | 0.06611054147682188, band [0.027342676631893312, 0.10487840632175045] | 0.22244481889690776 | **INSIDE** |
| S3 D_channel > 0 and outside 2·SE_D | 0.8169587574271885 | [0.770561523979914, 0.8692603102466345] | 2·SE_D = 0.05035147618915502 | positive True, outside True | **CLEAR** |

### 6.1 S1 — the curve on its own channel

κ_slow(w=0) = 0.8916930095784603 [0.8502517263399952, 0.9350975324766414] against the sealed secant 0.8781169374706214, band
[0.6452939122851654, 1.1109399626560772] — position 0.058310693699752815, **INSIDE**. The r-channel gain is 0.8737006067872115,
and it is inside SE_approx rather than wished away (#61).

### 6.2 S2 — the mu-channel tax's first interval

κ_mu(0.25) = 0.07473425215127182 [0.05386916320637429, 0.09553678214715175] against 0.06611054147682188, band [0.027342676631893312, 0.10487840632175045] — position
0.22244481889690776, **INSIDE**. The mu-channel tax's first registered interval is consistent with R2's independent estimate. This is descriptive-grade by construction (the band carries R2's own CI) and routes nothing, but the two legs agree.

### 6.3 S3 — the discrimination

D_channel = 0.8169587574271885 [0.770561523979914, 0.8692603102466345], SE_D 0.02517573809457751 (2·SE_D 0.05035147618915502) → **CLEAR =
True**. The ratio κ_slow/κ_mu is 11.931517127829927.

### 6.4 The closure with R2

R2's mispricing factor was 11.64546777328575×; this leg's measured channel ratio
κ_slow/κ_mu is 11.931517127829927× — a difference of 0.28604935454417735. **This is not an
independent confirmation and should not be read as one:** once S1 places the
measured slow tax on the curve and S2 places the measured mu tax on R2's
estimate, the ratio *must* reproduce R2's factor. The content is that both
landed. R2's mispricing was never a broken law — it was the channel ratio,
measured through a curve that only ever priced one of the two channels.

Consistency readings: κ_slow(w=1) = 0.8055984527437156 [0.7635291763629583, 0.8475386564029389] (the slow tax with a
full-strength identity channel also present), κ_mu(0.10) = 0.09408788724699418 [0.07563755345934248, 0.11248055877183495].
Off-diagonal diagnostics: κ_mu(cell C) = 0.10273007691270834, κ_mu(cell D) = 0.06010885242157973.

### 6.5 φ-dependence: a self-check and an un-entailed cross-leg check

The off-diagonal cells make κ_mu's φ-dependence visible. At share 0.25 it is
0.07473425215127182 at φ = 0.05 and 0.06010885242157973 at φ_A — a realized difference of
0.014625399729692089.

**Self-check, against me.** The φ-transport component I put into S2's SE_approx
was measured on probe worlds and came to 0.0095581776062717. The realized difference
is 1.5301452151397015× larger. My SE_approx term was undersized. S2 lands inside anyway
(position 0.22244481889690776), so nothing changes, but the band was narrower than the
approximation it was meant to cover, and a leg with less margin would have paid
for it.

**Un-entailed cross-leg check.** R2 measured κ_mu at φ = 0.60 — a value this leg
never runs. Interpolating R2b's two φ points linearly to 0.60 predicts
0.06526161265523818; R2 measured 0.06611054147682188, an error of -0.0008489288215837026. Unlike §6.4, this
is *not* entailed by S1 and S2: it uses the φ slope, which no sealed prediction
touches.

## 7. Anomalies

1. **A-1 (before any number).** The dispatched interpreter was absent; a pinned
   CPython venv was built and recorded: `/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python`.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (disclosed ordering fact, before the stamp).** The bands need probe
   spreads, so all eight arms were scored on 128 probe worlds before the
   seal — which means probe values of κ_slow (0.8572082694309165), κ_mu (0.078437268499968)
   and D_channel (0.7787710009309485) existed beforehand. They were **not consumed**: S1
   comes from M3's persisted curve, S2 from R2's persisted measurement, and only
   *spreads* and the w = 0 *gain* enter the bands (#57, variances only). They are
   reported rather than omitted.

## 8. Boundary

EXPLORATORY, synthetic, label-free. The mu channel is planted, so this measures
how the gauge prices a channel we installed, not one discovered in data. Two
shares, two φ, two doses, one instrument. S2 is a first-interval claim by
construction — its band carries R2's own CI and it routes nothing (V-b3). Rule
13: 0 event(s). 192 worlds per arm.

## 9. Environment

`/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python` — Python 3.12.12.
