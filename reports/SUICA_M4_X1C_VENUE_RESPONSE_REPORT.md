# SUICA M4-X1c — the venue response, clause-separated gate

Run 2026-08-19T05:50:13.941456Z · registration `docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md` (X1c, commit 8fffaad) · seed 20260819 · B_perm 499 · B_boot 1000 · runtime 122.5 s.

**VERDICT — RESPONSE_TRACE.**

Part 0's five ROUTING clauses all passed, so the real arms ran. The primary arm's DF-CORRECTED reproducible interaction share is 0.0190 of comment-level Var(y) [0.0171, 0.0193] (raw 0.0162 [0.0146, 0.0165], #67 dual stamp), with R = 0.2788 against a permutation band [-0.0161, 0.0152] and a cluster-bootstrap CI [0.2598, 0.2934]. The MARGINAL author and community shares carry 0.1804 and 0.0928 with their design-composition annotations; the residual is 0.7106.

## Leg lineage

| leg | what it registered | outcome |
|---|---|---|
| M4-X1 (commit ebe4f5b) | the venue response of expression volume — double-centred v on the raw community universe, no support floor | A1_STOP__SYNTHETIC_GATE_FAILED — the null world read 0.0458, 2.3x the TRACE boundary; defect #85 |
| M4-X1b (commit e8c9040) | design repaired (law vocabulary + support floor s = 5) AND estimator repaired (exact two-way FE by alternating projections) | A1_STOP__SYNTHETIC_GATE_FAILED — 8 of 9 clauses PASS; the one failure was a DESCRIPTIVE with a solved mechanism; defect #86 |
| M4-X1c (this leg) | clause-separated gate (#86a) + df-corrected routing statistic (#86b/c); everything else inherits X1b | see the verdict above |

Third and final registration of this estimand. X1 stopped on an estimator whose zero was not zero; X1b repaired the estimator and the design, certified the routing machinery exact on the realized skeleton twice over, and stopped on a co-reported descriptive whose bias was design-predicted; X1c separates the two clause families, names the mains MARGINAL and scores them against marginal targets, pins the projection's degrees of freedom and routes the verdict on the corrected share. Nothing else moved: the same cache, the same chain, the same estimator, the same seeds, the same cells, the same leans, the same boundaries.

## Gates

| gate | status |
|---|---|
| Inherited census anchors (#78: 17,640,062 rows / 10,296 authors / 1,443 law communities and three more) | **PASS** |
| Predicate-chain census (#78: s = 3/5/8 exact; 0 singleton communities and LCC 1.000 at s = 5) | **PASS** |
| LCC assertion (the alternating projection is exact only on a connected design; coverage must be 1.000) | **PASS** |
| Big5 replication #69 floor (300 authors, IN-LEG census; below it the arm is underpowered-descriptive, not #73) | **PASS** |
| Part 0 ROUTING clauses (#86a; A1 stop on any failing clause) | **PASS** |
| Part 0 DESCRIPTIVE clauses (#86a; a failure ANNOTATES with a #67 dual-stamped bias note, never stops) | **PASS** |
| ID-leak scan (0 NEW hits of 10,296 author names over the committed files; 4 pre-existing dictionary collisions carried unchanged from HEAD) | **PASS** |

## Anchors — the inherited census (#78, BLOCKING)

| quantity (exact predicate) | registered | observed | status |
|---|---|---|---|
| rows parseable (author+subreddit+created_utc+wcq) | 17,640,062 | 17,640,062 | PASS |
| authors | 10,296 | 10,296 | PASS |
| Big5 cohort authors seen | 1,401 | 1,401 | PASS |
| disjoint authors | 8,895 | 8,895 | PASS |
| law vocabulary floor (users) | 89 | 89 | PASS |
| law vocabulary (communities) | 1,443 | 1,443 | PASS |

Read from X1's committed cell cache, whose 17,640,062-row single pass is the only time the comments file was touched in this line. No text body, no label file.

## The predicate chain (#78, BLOCKING) — X1b's, unchanged

| s | authors | communities | shared pairs | fill | median authors per community | singleton communities | LCC author coverage |
|---|---|---|---|---|---|---|---|
| 3 | 3,686 | 1,145 | 32,415 | 0.0077 | 11.0 | 1 | 1.000 |
| 5 (PRIMARY) | 3,665 | 1,000 | 31,899 | 0.0087 | 12.5 | 0 | 1.000 |
| 8 | 3,595 | 780 | 30,561 | 0.0109 | 16.0 | 0 | 1.000 |

| s | registered authors | registered communities | registered shared pairs | all three exact |
|---|---|---|---|---|
| 3 | 3,686 | 1,145 | 32,415 | PASS |
| 5 | 3,665 | 1,000 | 31,899 | PASS |
| 8 | 3,595 | 780 | 30,561 | PASS |

Attrition at the primary floor (s = 5): 140,026 eligible cells → 37,414 shared pairs → 36,612 after the support floor → 31,899 after the k ≥ 3 author floor → 31,899 in the largest connected component (1 component(s) before step 5).

## Part 0 — the CLAUSE-SEPARATED gate (#86a; A1 stop on a ROUTING failure only)

The battery is X1b's, on the inherited seeds: the real incidence carries WHOLLY SYNTHETIC y and no real y enters Part 0 at any point. What #86a changes is the scoring. ROUTING clauses gate the verdict and fire the A1 stop; DESCRIPTIVE clauses gate the REPORT — a failure attaches a dual-stamped bias annotation (#67) to the number and never stops the leg.

Tolerance rule: max(0.01, 3.0 x replicate sd) over 8 replicates. The floor of 0.01 of total variance is half the width of the registration's own RESPONSE_TRACE / IDIOSYNCRATIC_RESPONSE boundary at 0.02.

### ROUTING clauses (A1-stopping)

| # | clause | status |
|---|---|---|
| 1 | (i) recovery — DF-CORRECTED interaction share within max(0.01, 3 x replicate sd) | PASS |
| 2 | (ii) null world — the interaction share's cluster-bootstrap CI covers 0 AND its point sits inside the permutation band | PASS |
| 3 | (iii) null world — R inside its permutation band | PASS |
| 4 | (iv) ablation — author-only AND community-only leakage < 0.005 on the interaction share | PASS |
| 5 | (v) #85b bootstrap-zero — the null world's cluster-bootstrap CI covers 0 | PASS |

Routing status: **PASS** (5 of 5).

### DESCRIPTIVE clauses (report-gated — a failure ANNOTATES)

| # | clause | status |
|---|---|---|
| 1 | MARGINAL author share against its MARGINAL target (planted + design composition) | PASS |
| 2 | MARGINAL community share against its MARGINAL target (planted + design composition) | PASS |

Descriptive status: **PASS** (2 of 2 inside tolerance).

No descriptive annotation was triggered: both marginal shares land inside tolerance of their marginal targets.

### The df correction, pinned from the realized skeleton (#86c)

| quantity | value |
|---|---|
| P — shared pairs (cells per half) | 31,899 |
| A — authors | 3,665 |
| C — communities | 1,000 |
| rank removed by the two-way projection (A + C - 1) | 4,664 |
| residual degrees of freedom (P - A - C + 1) | 27,235 |
| retained fraction of a white interaction | 0.8538 |
| correction factor P / (P - A - C + 1) | 1.1713 |

`share_corr = share_raw * P / (P - A - C + 1)`. The factor is a property of the estimand's realized design, so the same pinned number rescales the point estimate, the permutation band and every cluster-bootstrap replicate; because it is positive, "the CI covers 0" is the same event on both scales and the NULL-first cell rule is untouched.

### ROUTING recovery — the interaction, both scales (#67)

| scale | planted | recovered (mean of 8) | replicate sd | tolerance | gap | routes |
|---|---|---|---|---|---|---|
| raw (co-reported) | 0.0200 | 0.0170 | 0.0005 | — | -0.0030 | no |
| **df-corrected** | 0.0200 | **0.0199** | 0.0005 | 0.0100 | -0.0001 | **yes — PASS** |

### DESCRIPTIVE recovery — the MARGINAL shares against MARGINAL TARGETS (#86b)

The derivation, pinned and printed. A unit's half-mean is a size-weighted mean of that unit's cell means, so it carries the unit's OWN COMPOSITION AVERAGE of the other components — and that average is the same in both halves, which is exactly what the cross-half covariance is built to keep. With `w[u,c,h] = n[u,c,h] / sum_c' n[u,c',h]` (author side), `t[u,c,h] = n[u,c,h] / sum_u' n[u',c,h]` (community side), `kappa_u = sum_c w[u,c,e] w[u,c,l]` (equal to 1/k_u when an author's cells are equally sized), `lambda_c = sum_u t[u,c,e] t[u,c,l]`, and `What_c` the normalized size weights `n[c,e] + n[c,l]` that `variance_budget` already uses:

```
T_a = v_a (1 - 1/A)
    + (v_c + v_g) * mean_u[kappa_u]
    - v_c * sum_c wbar[c,e] wbar[c,l]  -  v_g * mean_u[kappa_u] / A
T_c = v_c (1 - sum_c What_c^2)
    + v_a * (sum_c What_c lambda_c - sum_u phi[u,e] phi[u,l])
    + v_g * (sum_c What_c lambda_c - sum_c What_c^2 lambda_c)
  with wbar[c,h] = (1/A) sum_u w[u,c,h],  phi[u,h] = sum_c What_c t[u,c,h]
```

The leading terms are the planted component plus the composition term; the subtracted terms are the estimator's own mean removal (both covariances subtract a product of means), kept so the target is exact rather than first-order. Every symbol on the right is a function of the cell counts alone — no y, planted or real, enters.

| marginal share | planted component | design-composition term | mean-removal term | MARGINAL TARGET | recovered (mean of 8) | replicate sd | tolerance | gap | status |
|---|---|---|---|---|---|---|---|---|---|
| author | 0.3000 | 0.0290 | -0.0024 | **0.3267** | 0.3220 | 0.0060 | 0.0179 | -0.0047 | PASS |
| community | 0.0800 | 0.0300 | -0.0022 | **0.1077** | 0.1072 | 0.0141 | 0.0424 | -0.0006 | PASS |

For contrast, the same recoveries scored against the PLANTED variance components — the X1b clause that stopped the leg:

| marginal share | planted component | recovered | gap against the planted component | would that clause have passed? |
|---|---|---|---|---|
| author | 0.3000 | 0.3220 | 0.0220 | **no** |
| community | 0.0800 | 0.1072 | 0.0272 | yes |

The NULL world (interaction planted at 0) scores its own marginal targets as a free cross-check:

| marginal share | marginal target | recovered | gap | tolerance | status |
|---|---|---|---|---|---|
| author | 0.3209 | 0.3220 | 0.0012 | 0.0193 | PASS |
| community | 0.1059 | 0.1139 | 0.0081 | 0.0623 | PASS |

### The null world, scored with the full pipeline

| null-world clause (nothing planted in the interaction) | raw | df-corrected |
|---|---|---|
| interaction share (planted 0.0000) | -0.0001 | -0.0001 |
| cluster-bootstrap CI (FE recomputed per replicate) | [-0.0003, 0.0002] | [-0.0004, 0.0002] |
| permutation band | [-0.0011, 0.0010] | [-0.0012, 0.0012] |

| clause | value |
|---|---|
| CI covers 0 (#85b, the bootstrap-zero clause) | yes |
| CI covers its own point estimate | yes |
| share inside its own permutation band | yes |
| R | 0.0078 |
| R cluster-bootstrap CI | [-0.0131, 0.0246] |
| permutation band for R | [-0.0166, 0.0166] |
| R inside band | yes |
| marginal author share (planted 0.3000) | 0.3223 |
| marginal community share (planted 0.0800) | 0.0967 |

### Every synthetic world, point-wise

| synthetic world | planted interaction | recovered interaction, raw (mean ± sd) | recovered interaction, df-corrected | marginal author | marginal community | R |
|---|---|---|---|---|---|---|
| planted | 0.0200 | 0.0170 ± 0.0005 | 0.0199 | 0.3220 | 0.1072 | 0.4550 |
| null | 0.0000 | -0.0000 ± 0.0001 | -0.0000 | 0.3220 | 0.1139 | 0.0000 |
| author_only | 0.0000 | -0.0001 ± 0.0002 | -0.0001 | 0.3002 | 0.0263 | -0.0038 |
| community_only | 0.0000 | 0.0001 ± 0.0001 | 0.0001 | 0.0225 | 0.0817 | 0.0032 |

| ablation clause (ROUTING) | leakage, df-corrected | leakage, raw | maximum | R leakage | status |
|---|---|---|---|---|---|
| author_only | 0.0001 | 0.0001 | 0.0050 | -0.0038 | PASS |
| community_only | 0.0001 | 0.0001 | 0.0050 | 0.0032 | PASS |

### The alternating projection, verified on the real incidence

| quantity | early half | late half |
|---|---|---|
| sweeps to convergence | 28 | 28 |
| final max absolute change | 4.993e-11 | 5.353e-11 |
| max abs residual AUTHOR mean | 3.547e-11 | 3.805e-11 |
| max abs residual COMMUNITY mean | 2.220e-17 | 2.726e-17 |

## PRIMARY arm — disjoint cohort, law vocabulary, n ≥ 10, s = 5, k ≥ 3, y = log(1 + word_count_quoteless)

3,665 eligible authors · 1,000 communities · 31,899 shared pairs · 63,798 eligible cells · 6,811,576 comments · comment-level Var(y) = 1.2423.

| quantity | value | CI | permutation band |
|---|---|---|---|
| **reproducible interaction share, DF-CORRECTED (routes)** | **0.0190** | [0.0171, 0.0193] | [-0.0016, 0.0017] |
| reproducible interaction share, raw (#67 co-report) | 0.0162 | [0.0146, 0.0165] | [-0.0014, 0.0015] |
| R — mean per-author profile correlation | 0.2788 | [0.2598, 0.2934] | [-0.0161, 0.0152] |
| marginal author share | 0.1804 | [0.1729, 0.1882] | — |
| marginal community share | 0.0928 | [0.0898, 0.1075] | — |
| residual | 0.7106 | [0.6931, 0.7180] | — |

Cell: **RESPONSE_TRACE**. Cell 1's two conditions: R inside its band = no; the corrected share's CI includes 0 = no.

## The budget, per arm

Marginal shares are named MARGINAL because that is what their estimator targets (#86b); the interaction is reported on both scales under the #67 dual stamp, and the DF-CORRECTED row is the one the cell reads.

| arm | marginal author | marginal community | interaction, raw | **interaction, df-corrected** | residual | R [CI, band] | cell | #73 |
|---|---|---|---|---|---|---|---|---|
| PRIMARY — disjoint, law vocab, n=10, s=5, k=3, wcq | 0.1804 [0.1729, 0.1882] | 0.0928 [0.0898, 0.1075] | 0.0162 [0.0146, 0.0165] | **0.0190** [0.0171, 0.0193] [-0.0016, 0.0017] | 0.7106 | 0.2788 [0.2598, 0.2934] [-0.0161, 0.0152] | RESPONSE_TRACE | none |
| sensitivity — support floor s=8 | 0.1795 [0.1719, 0.1878] | 0.0909 [0.0872, 0.1060] | 0.0162 [0.0148, 0.0166] | **0.0189** [0.0172, 0.0193] [-0.0014, 0.0019] | 0.7134 | 0.2738 [0.2549, 0.2905] [-0.0164, 0.0166] | RESPONSE_TRACE | none |
| sensitivity — n_min=5 (same chain) | 0.1821 [0.1754, 0.1890] | 0.0936 [0.0904, 0.1061] | 0.0185 [0.0170, 0.0190] | **0.0208** [0.0192, 0.0214] [-0.0014, 0.0016] | 0.7058 | 0.2192 [0.2046, 0.2321] [-0.0142, 0.0119] | IDIOSYNCRATIC_RESPONSE (STRADDLE) | #73 — IDIOSYNCRATIC_RESPONSE vs primary RESPONSE_TRACE |
| sensitivity — y = log(1 + word_count) | 0.1811 [0.1729, 0.1886] | 0.0971 [0.0933, 0.1131] | 0.0161 [0.0145, 0.0163] | **0.0188** [0.0170, 0.0191] [-0.0016, 0.0016] | 0.7057 | 0.2777 [0.2581, 0.2925] [-0.0160, 0.0173] | RESPONSE_TRACE | none |
| REPLICATION — Big5 cohort, identical chain | 0.1882 [0.1625, 0.2151] | 0.1156 [0.0987, 0.1531] | 0.0142 [0.0105, 0.0152] | **0.0177** [0.0131, 0.0189] [-0.0052, 0.0057] | 0.6820 | 0.2823 [0.2177, 0.3418] [-0.0508, 0.0584] | RESPONSE_TRACE | none |

Straddles are reported as straddles, per the registration: **sensitivity — n_min=5 (same chain)** — the corrected CI [0.0192, 0.0214] touches RESPONSE_TRACE and IDIOSYNCRATIC_RESPONSE, and the point 0.0208 places it in IDIOSYNCRATIC_RESPONSE.

### Reading the cluster-bootstrap interval (an anomaly, calibrated)

| arm | point (raw) | bootstrap mean (raw) | shift | bootstrap sd |
|---|---|---|---|---|
| PRIMARY — disjoint, law vocab, n=10, s=5, k=3, wcq | 0.0162 | 0.0155 | -0.0007 | 0.0005 |
| sensitivity — support floor s=8 | 0.0162 | 0.0156 | -0.0005 | 0.0005 |
| sensitivity — n_min=5 (same chain) | 0.0185 | 0.0180 | -0.0005 | 0.0005 |
| sensitivity — y = log(1 + word_count) | 0.0161 | 0.0154 | -0.0006 | 0.0004 |
| REPLICATION — Big5 cohort, identical chain | 0.0142 | 0.0128 | -0.0014 | 0.0012 |

Every arm's point estimate sits near the UPPER edge of its own interval. The mechanism is the resample's sparsity: a cluster bootstrap over authors keeps about 63% of the distinct authors, so each replicate's projection removes a larger share of its own design than the full design's A + C - 1 of P, while the pinned correction factor stays at the realized skeleton's value (which is what the registration fixes). The direction is downward and it is CALIBRATED rather than argued: Part 0's planted world has a known truth of 0.0200 and shows the same asymmetry — point 0.0204, interval [0.0188, 0.0206] — and still covers the truth. The corpus intervals should be read the same way: as slightly conservative on the low side, never on the high side, so no cell assignment here is at risk from the effect.

### The df correction and the composition annotation, per arm

| arm | P | A | C | factor | mean_u[kappa_u] | size-weighted mean_c[lambda_c] | implied author main (annotation only) | implied community main (annotation only) |
|---|---|---|---|---|---|---|---|---|
| PRIMARY — disjoint, law vocab, n=10, s=5, k=3, wcq | 31,899 | 3,665 | 1,000 | 1.1713 | 0.2905 | 0.0937 | 0.1526 | 0.0767 |
| sensitivity — support floor s=8 | 30,561 | 3,595 | 780 | 1.1670 | 0.2930 | 0.0891 | 0.1518 | 0.0757 |
| sensitivity — n_min=5 (same chain) | 56,460 | 5,094 | 1,243 | 1.1264 | 0.2750 | 0.0810 | 0.1546 | 0.0794 |
| sensitivity — y = log(1 + word_count) | 31,899 | 3,665 | 1,000 | 1.1713 | 0.2905 | 0.0937 | 0.1521 | 0.0811 |
| REPLICATION — Big5 cohort, identical chain | 3,261 | 408 | 240 | 1.2475 | 0.3375 | 0.1787 | 0.1536 | 0.0849 |

The last two columns are an ANNOTATION, not a registered estimand and not a routing object: they invert the 2x2 composition mixing `marginal_a = V_a + kappa (V_c + V_g)`, `marginal_c = V_c + lambda (V_a + V_g)` with V_g taken as the df-corrected interaction share. They print how large the annotation is; nothing in this leg rests on them.

### The arm designs

| arm | eligible authors | communities | shared pairs | comments | median shared communities | median authors per community | singleton communities | LCC coverage |
|---|---|---|---|---|---|---|---|---|
| PRIMARY — disjoint, law vocab, n=10, s=5, k=3, wcq | 3,665 | 1,000 | 31,899 | 6,811,576 | 5.0 | 12.5 | 0 | 1.000 |
| sensitivity — support floor s=8 | 3,595 | 780 | 30,561 | 6,642,327 | 5.0 | 16.0 | 0 | 1.000 |
| sensitivity — n_min=5 (same chain) | 5,094 | 1,243 | 56,460 | 7,885,024 | 7.0 | 18.0 | 0 | 1.000 |
| sensitivity — y = log(1 + word_count) | 3,665 | 1,000 | 31,899 | 6,811,576 | 5.0 | 12.5 | 0 | 1.000 |
| REPLICATION — Big5 cohort, identical chain | 408 | 240 | 3,261 | 1,206,370 | 5.0 | 7.0 | 4 | 1.000 |

The Big5 replication arm carries 408 eligible authors under the identical chain, at or above the in-leg #69 floor of 300, so it carries a #73 comparison.

## Registered leans (report against; they never route)

| lean | scale | observed | outcome |
|---|---|---|---|
| R in (0.05, 0.30] | R (uncorrected by design) | 0.2788 | HELD |
| interaction share in (0.005, 0.05] | RAW — the scale the lean was registered on (X1) | 0.0162 | HELD |
| interaction share in (0.005, 0.05] — co-reported (#67) | DF-CORRECTED — the scale the VERDICT routes on (X1c) | 0.0190 | HELD |
| marginal author share in [0.15, 0.45] | MARGINAL (composition-annotated) | 0.1804 | HELD |
| marginal community share in [0.02, 0.15] | MARGINAL (composition-annotated) | 0.0928 | HELD |
| Big5 replication lands in the primary cell | cell (routed on the corrected share) | RESPONSE_TRACE | HELD |

## Headroom (#84 as restated by #85) — about the MEAN

The clause is about the MEAN over thousands of authors, not about the per-author correlation: at k_min = 3 a Pearson correlation over three points reaches ±1 whenever three points happen to line up, so saturation in the per-author distribution is EXPECTED and is not a ceiling on the estimand. The realized corpus distribution is reported beside Part 0's synthetic null world so the statement is a number.

| quantile | PRIMARY arm (corpus) | Part 0 null world (synthetic) |
|---|---|---|
| q00 | -0.9998 | -1.0000 |
| q05 | -0.7634 | -0.8907 |
| q10 | -0.4637 | -0.7442 |
| q25 | -0.0283 | -0.3596 |
| q50 | 0.3501 | 0.0057 |
| q75 | 0.6758 | 0.3778 |
| q90 | 0.8917 | 0.7520 |
| q95 | 0.9654 | 0.9297 |
| q100 | 1.0000 | 1.0000 |

Primary arm: 3,665 authors scored, 0 undefined; mean 0.2788, sd 0.5021; 0.0276 above 0.99, 0.0955 above 0.90, 0.7364 positive. Synthetic null world: mean 0.0078, sd 0.5259; 0.0180 above 0.99, 0.5029 positive. Per-author saturation is acknowledged and NOT treated as a ceiling; the mean is the bounded object and it is what R reports.

## What this leg reads

- **Crossing #2 has its first corpus reading, and it is a RESPONSE_TRACE.** On the primary arm — 3,665 disjoint-cohort authors across 1,000 law-vocabulary communities, 31,899 shared (author, community) pairs, 6,811,576 comments — the reproducible author x community interaction carries 0.0190 of comment-level Var(y) after the df correction [0.0171, 0.0193], against a raw 0.0162 [0.0146, 0.0165] (#67 dual stamp; the pinned factor is 1.1713 = 31,899 / (31,899 - 3,665 - 1,000 + 1)).
- **The persistence statistic agrees with the budget.** R, the mean per-author correlation of the early and late venue profiles, is 0.2788 with a cluster-bootstrap CI [0.2598, 0.2934] against a permutation band [-0.0161, 0.0152] — OUTSIDE its band, so the NULL-first cell is refused on both of its conditions rather than one.
- **The budget's two main components are MARGINAL, and the annotation is a number.** The marginal author share reads 0.1804 and the marginal community share 0.0928. This arm's composition weights are mean_u[kappa_u] = 0.2905 on the author side and the size-weighted mean_c[lambda_c] = 0.0937 on the community side, so each marginal carries roughly that fraction of the OTHER components. Inverting the 2x2 mixing as an annotation only (not a registered estimand, nothing routes on it) implies an author main near 0.1526 and a community main near 0.0767.
- **Headroom is reported about the MEAN, with per-author saturation acknowledged.** 3,665 authors are scored and 0 are undefined; the realized per-author correlation has mean 0.2788 and sd 0.5021, with 0.0276 above 0.99 and 0.7364 positive. At k_min = 3 a three-point Pearson correlation reaches +-1 whenever three points line up, so the tail mass is EXPECTED and is not a ceiling: the bounded object is the mean over thousands of authors, which sits at 0.2788 against a null-world mean of 0.0078.
- **The arms agree to within 0.0031 of total variance.** The corrected share runs from 0.0177 (REPLICATION — Big5 cohort, identical chain) to 0.0208 (sensitivity — n_min=5 (same chain)) across the support floor, the eligibility floor, the y-definition and the cohort. The entire spread lies within 0.0023 of the RESPONSE_TRACE / IDIOSYNCRATIC_RESPONSE boundary at 0.02, so what disagreement exists between arms is a boundary crossing and not a different reading of the corpus.
- **Arms that diverge from the primary cell (#73):** sensitivity — n_min=5 (same chain) — corrected share 0.0208 [0.0192, 0.0214], a STRADDLE across the 0.02 boundary (the CI touches RESPONSE_TRACE and IDIOSYNCRATIC_RESPONSE) → #73 — IDIOSYNCRATIC_RESPONSE vs primary RESPONSE_TRACE. The flag is raised as registered; the divergence is a boundary crossing by a few thousandths of total variance, not a different reading of the corpus.

## Boundaries

- **Metadata only, expression VOLUME and not content (permanent).** The only text-derived quantity in this leg is `word_count_quoteless`, the author's own-word count per comment. No body was read, no topic, no style, no sentiment. Every claim here is about HOW MUCH is written in a venue, never about WHAT is written.
- **The response-operator projection caution.** Profile persistence is ONE static projection of crossing #2's condition-response operator R_v. A null is a statement about this projection at this resolution, not about the operator; a detection is a lower bound on it.
- **No psychological naming.** Verbosity is a technical expression-volume object. Nothing here is a trait, a state, a disposition or a preference, and the leg is label-free: `author_profiles.csv` was never opened.
- **EXPLORATORY, corpus-level.** No person-level claim is licensed. The per-author correlations exist only as the population of a mean — which is the #85 restatement of the #84 headroom clause: the bounded object is the MEAN over thousands of authors, never the per-author correlation.
- **Cohort composition.** The disjoint cohort is TYPOLOGY-ENRICHED by construction (PANDORA's non-Big5 authors are MBTI-labelled users), so it is a platform sample with a selection, not a population sample.
- **The analysis universe is WELL-SHARED VENUES by construction (new in X1b).** The community universe is the law vocabulary (1,443 communities at floor 89) and the eligible grid carries a cross-author support floor of five authors per community. Whatever this design licenses, it licenses about venues that many cohort authors share — not about the long tail of small or private communities, which the chain removes by construction. The support conditioning is a PRIMARY design parameter (#85c), not a sensitivity.
- **The routing statistic is DF-CORRECTED and the mains are MARGINAL (new in X1c).** The verdict routes on share_corr = share_raw x P/(P - A - C + 1), the raw share is co-reported under the #67 dual stamp, and the two main shares are named MARGINAL because that is what their estimator targets: each carries the unit's own composition average of the other components, a term computed here from the design alone and printed beside every number. The mains were NOT re-registered as FE-borne objects, so they remain descriptive throughout and no claim rests on them.

## Configuration

```json
{
  "ablation_leak_max": 0.005,
  "ablation_worlds": {
    "author_only": {
      "author": 0.3,
      "community": 0.0,
      "interaction": 0.0
    },
    "community_only": {
      "author": 0.0,
      "community": 0.08,
      "interaction": 0.0
    }
  },
  "author_profiles_opened": false,
  "b_boot": 1000,
  "b_perm": 499,
  "big5_power_floor_69": 300,
  "bodies_read": false,
  "bootstrap_semantics": "cluster bootstrap over authors; the FE is RECOMPUTED inside every replicate (#85b), with author multiplicity as the projection weight; the df factor is the pinned constant of the realized design, so the corrected CI is the affine image of the raw CI",
  "cells": {
    "idiosyncratic_max": 0.1,
    "keyed_on": "the df-corrected interaction share",
    "trace_max": 0.02
  },
  "columns_read": [
    "author",
    "subreddit",
    "created_utc",
    "word_count_quoteless",
    "word_count"
  ],
  "deviations": [
    "X1b's X1-vs-X1b estimator-comparison grid is NOT re-run: it was a one-time demonstration of the repair, already adjudicated, and re-running it would add no information to a leg whose purpose is the corpus reading. X1b's artifact holds it."
  ],
  "estimator": "two-way fixed effects per half by ALTERNATING PROJECTIONS on the eligible shared cells; v = the FE residual of the cell mean (X1b, unchanged)",
  "fe_tolerance": 1e-10,
  "gate_structure": "#86a: five ROUTING clauses (A1-stopping) and two DESCRIPTIVE clauses (report-gated; a failure annotates with a #67 dual-stamped bias note)",
  "halves": "author's FULL-STREAM median created_utc, <= to early",
  "k_min": 3,
  "leans": {
    "R": [
      0.05,
      0.3
    ],
    "interaction_share": [
      0.005,
      0.05
    ],
    "interaction_share_registered_scale": "RAW (X1)",
    "marginal_author": [
      0.15,
      0.45
    ],
    "marginal_community": [
      0.02,
      0.15
    ]
  },
  "leg": "M4-X1c",
  "machinery_imported_by_file": [
    "scripts/run_suica_m4_x1b_venue_response_fe.py (chain, exact FE, gate worlds, bootstrap-FE)",
    "scripts/run_suica_m4_x1_venue_response.py (Design, variance_budget, synthetic_design, headroom, #83 helpers)"
  ],
  "mains_estimator": "cross-half covariances of author and community half-means, PRE-FE (X1's definition), now NAMED MARGINAL and scored against MARGINAL TARGETS derived from the realized skeleton (#86b)",
  "n_min_primary": 10,
  "n_min_sensitivity": 5,
  "null_shares": {
    "author": 0.3,
    "community": 0.08,
    "interaction": 0.0
  },
  "planted_shares": {
    "author": 0.3,
    "community": 0.08,
    "interaction": 0.02
  },
  "predecessors": [
    "M4-X1 (A1_STOP__SYNTHETIC_GATE_FAILED, commit ebe4f5b)",
    "M4-X1b (A1_STOP__SYNTHETIC_GATE_FAILED, commit e8c9040)"
  ],
  "predicate_chain": [
    "1. cells with n >= n_min comments, cohort authors, law vocabulary communities",
    "2. shared pairs: (author, community) with BOTH halves eligible",
    "3. community support floor: >= s authors holding a shared pair",
    "4. authors with >= k_min surviving shared communities",
    "5. largest connected component of the bipartite graph",
    "NO fixed-point iteration: the chain runs once, in this order"
  ],
  "registration": "docs/SUICA_M4_X_EXPRESSION_RESPONSE_PLAN.md@8fffaad (X1c)",
  "routing_statistic": "the DF-CORRECTED reproducible interaction share, share_corr = share_raw * P/(P - A - C + 1), with P/A/C pinned from each arm's realized skeleton (#86b/c); the raw share is co-reported (#67); R is uncorrected",
  "run_utc": "2026-08-19T05:50:13.941456Z",
  "seed": 20260819,
  "seed_boot": 20260822,
  "seed_part0": 20260820,
  "seed_perm": 20260821,
  "seeds_inherited": "the X1/X1b derivation; NOT re-chosen after either stop (#76 gate-shopping refusal)",
  "support_censused": [
    3,
    5,
    8
  ],
  "support_primary": 5,
  "support_sensitivity": 8,
  "synthetic_replicates": 8,
  "title": "the venue response, clause-separated gate",
  "tolerance_floor": 0.01,
  "tolerance_sd_multiple": 3.0,
  "var_y_denominator": "comment-level population variance of y over the analysis pool = the comments inside eligible cells",
  "vocabulary_floor_fraction": 0.01,
  "y": "log(1 + word_count_quoteless)",
  "y_sensitivity": "log(1 + word_count)"
}
```

