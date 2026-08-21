# SUICA M4-X5-T Temporal Transport Audit

**VERDICT: `POST_CLOSURE_TEMPORAL_DIAGNOSTIC_COMPLETE`.** This is a post-closure diagnostic of projection stability, not a rewrite of X5 and not a psychological claim.

Protocol commit: `b0b38c2`. Seed 20260822; B_boot=500; K=[2, 4, 8]; configuration sha256 `ce7d1da3de6ea856...`.

## Reproduction gate

| relation | cohort | authors | max abs error | status |
|---|---|---|---|---|
| R1 | disjoint | 8004 | 9.021e-17 | PASS |
| R1 | big5 | 1112 | 4.510e-17 | PASS |
| R2 | disjoint | 7989 | 5.551e-17 | PASS |
| R2 | big5 | 1100 | 8.327e-17 | PASS |
| R3 | disjoint | 8008 | 7.373e-18 | PASS |
| R3 | big5 | 1116 | 1.561e-17 | PASS |
| R4 | disjoint | 7986 | 1.561e-17 | PASS |
| R4 | big5 | 1096 | 4.510e-17 | PASS |
| R5 | disjoint | 7966 | 2.359e-16 | PASS |
| R5 | big5 | 1081 | 1.110e-16 | PASS |

Every committed K=2 early/late within-person slope must reproduce before multisegment estimates are licensed.

## Finest-resolution decision view

| cohort | K=8 within-slope classes | all 8 segment families match X5 | relations |
|---|---|---|---|
| disjoint | TEMPORALLY_EQUIVALENT_AT_0.02=4; TEMPORAL_HETEROGENEITY_UNRESOLVED=1 | 1 | 5 |
| big5 | TEMPORALLY_EQUIVALENT_AT_0.02=1; TEMPORAL_HETEROGENEITY_DETECTED=2; TEMPORAL_HETEROGENEITY_UNRESOLVED=2 | 3 | 5 |

K=2/4/8 are nested views of the same authors and events, not independent replications. The table above is therefore the main resolution-specific reading; the full table below is a sensitivity path.

## Temporal classifications

| relation | cohort | K | authors | within-slope temporal class | signs | historical family | all segment families match | raw trend |
|---|---|---|---|---|---|---|---|---|
| R1 | disjoint | 2 | 7370 | TEMPORALLY_EQUIVALENT_AT_0.02 | -+ | SIGN_FLIP | no | +0.0077 |
| R1 | disjoint | 4 | 7370 | TEMPORALLY_EQUIVALENT_AT_0.02 | ---+ | SIGN_FLIP | no | +0.0107 |
| R1 | disjoint | 8 | 7370 | TEMPORAL_HETEROGENEITY_UNRESOLVED | -----++- | SIGN_FLIP | no | +0.0127 |
| R1 | big5 | 2 | 952 | TEMPORALLY_EQUIVALENT_AT_0.02 | -+ | GAP_SIGN_UNRESOLVED | no | +0.0131 |
| R1 | big5 | 4 | 952 | TEMPORAL_HETEROGENEITY_UNRESOLVED | ---+ | GAP_SIGN_UNRESOLVED | no | +0.0176 |
| R1 | big5 | 8 | 952 | TEMPORAL_HETEROGENEITY_DETECTED | ------++ | GAP_SIGN_UNRESOLVED | no | +0.0193 |
| R2 | disjoint | 2 | 7945 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++ | GAP_UNRESOLVED | no | -0.0048 |
| R2 | disjoint | 4 | 7945 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++++ | GAP_UNRESOLVED | no | -0.0059 |
| R2 | disjoint | 8 | 7945 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++++++++ | GAP_UNRESOLVED | no | -0.0064 |
| R2 | big5 | 2 | 1092 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++ | GAP_UNRESOLVED | yes | -0.0074 |
| R2 | big5 | 4 | 1092 | TEMPORAL_HETEROGENEITY_UNRESOLVED | ++++ | GAP_UNRESOLVED | no | -0.0092 |
| R2 | big5 | 8 | 1092 | TEMPORAL_HETEROGENEITY_DETECTED | ++++++++ | GAP_UNRESOLVED | no | -0.0090 |
| R3 | disjoint | 2 | 7955 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++ | GAP_UNRESOLVED | no | +0.0021 |
| R3 | disjoint | 4 | 7955 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++++ | GAP_UNRESOLVED | no | +0.0024 |
| R3 | disjoint | 8 | 7955 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++++++++ | GAP_UNRESOLVED | no | +0.0024 |
| R3 | big5 | 2 | 1105 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++ | GAP_UNRESOLVED | yes | -0.0001 |
| R3 | big5 | 4 | 1105 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++++ | GAP_UNRESOLVED | yes | +0.0010 |
| R3 | big5 | 8 | 1105 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++++++++ | GAP_UNRESOLVED | yes | +0.0010 |
| R4 | disjoint | 2 | 7370 | TEMPORALLY_EQUIVALENT_AT_0.02 | +- | GAP_SIGN_UNRESOLVED | no | -0.0031 |
| R4 | disjoint | 4 | 7370 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++-+ | GAP_SIGN_UNRESOLVED | no | -0.0031 |
| R4 | disjoint | 8 | 7370 | TEMPORALLY_EQUIVALENT_AT_0.02 | ++++---+ | GAP_SIGN_UNRESOLVED | no | -0.0030 |
| R4 | big5 | 2 | 952 | TEMPORALLY_EQUIVALENT_AT_0.02 | +- | GAP_UNRESOLVED | yes | -0.0105 |
| R4 | big5 | 4 | 952 | TEMPORALLY_EQUIVALENT_AT_0.02 | +++- | GAP_UNRESOLVED | yes | -0.0099 |
| R4 | big5 | 8 | 952 | TEMPORAL_HETEROGENEITY_UNRESOLVED | +++++--+ | GAP_UNRESOLVED | yes | -0.0100 |
| R5 | disjoint | 2 | 7353 | TEMPORALLY_EQUIVALENT_AT_0.02 | -- | SAME_SIGN_GAP | yes | +0.0026 |
| R5 | disjoint | 4 | 7353 | TEMPORALLY_EQUIVALENT_AT_0.02 | ---- | SAME_SIGN_GAP | yes | +0.0060 |
| R5 | disjoint | 8 | 7353 | TEMPORALLY_EQUIVALENT_AT_0.02 | -------- | SAME_SIGN_GAP | yes | +0.0084 |
| R5 | big5 | 2 | 941 | TEMPORALLY_EQUIVALENT_AT_0.02 | -- | SAME_SIGN_GAP | yes | +0.0044 |
| R5 | big5 | 4 | 941 | TEMPORAL_HETEROGENEITY_UNRESOLVED | ---- | SAME_SIGN_GAP | yes | +0.0078 |
| R5 | big5 | 8 | 941 | TEMPORAL_HETEROGENEITY_UNRESOLVED | -------- | SAME_SIGN_GAP | yes | +0.0090 |

## K=8 segment transport map

| relation | cohort | K | segment | beta_B | beta_W | Delta_T | family |
|---|---|---|---|---|---|---|---|
| R1 | disjoint | 8 | 1 | +0.0255 | -0.0239 | +0.0494 | SIGN_FLIP |
| R1 | disjoint | 8 | 2 | +0.0364 | -0.0166 | +0.0530 | SIGN_FLIP |
| R1 | disjoint | 8 | 3 | +0.0432 | -0.0109 | +0.0541 | SIGN_FLIP |
| R1 | disjoint | 8 | 4 | +0.0343 | -0.0088 | +0.0431 | SIGN_FLIP |
| R1 | disjoint | 8 | 5 | +0.0484 | -0.0024 | +0.0508 | GAP_SIGN_UNRESOLVED |
| R1 | disjoint | 8 | 6 | +0.0567 | +0.0020 | +0.0547 | GAP_SIGN_UNRESOLVED |
| R1 | disjoint | 8 | 7 | +0.0432 | +0.0021 | +0.0411 | GAP_SIGN_UNRESOLVED |
| R1 | disjoint | 8 | 8 | +0.0638 | -0.0002 | +0.0640 | GAP_SIGN_UNRESOLVED |
| R1 | big5 | 8 | 1 | +0.0426 | -0.0210 | +0.0636 | GAP_SIGN_UNRESOLVED |
| R1 | big5 | 8 | 2 | +0.0369 | -0.0291 | +0.0660 | GAP_SIGN_UNRESOLVED |
| R1 | big5 | 8 | 3 | +0.0542 | -0.0105 | +0.0647 | GAP_UNRESOLVED |
| R1 | big5 | 8 | 4 | +0.0317 | -0.0101 | +0.0417 | GAP_UNRESOLVED |
| R1 | big5 | 8 | 5 | +0.0509 | -0.0018 | +0.0527 | GAP_UNRESOLVED |
| R1 | big5 | 8 | 6 | +0.0525 | -0.0013 | +0.0538 | GAP_UNRESOLVED |
| R1 | big5 | 8 | 7 | +0.0878 | +0.0090 | +0.0788 | GAP_SIGN_UNRESOLVED |
| R1 | big5 | 8 | 8 | +0.0631 | +0.0129 | +0.0502 | GAP_UNRESOLVED |
| R2 | disjoint | 8 | 1 | +0.0538 | +0.0582 | -0.0044 | GAP_UNRESOLVED |
| R2 | disjoint | 8 | 2 | +0.0856 | +0.0632 | +0.0224 | SAME_SIGN_GAP |
| R2 | disjoint | 8 | 3 | +0.0964 | +0.0631 | +0.0333 | SAME_SIGN_GAP |
| R2 | disjoint | 8 | 4 | +0.0789 | +0.0618 | +0.0171 | GAP_UNRESOLVED |
| R2 | disjoint | 8 | 5 | +0.0677 | +0.0599 | +0.0077 | GAP_UNRESOLVED |
| R2 | disjoint | 8 | 6 | +0.0652 | +0.0582 | +0.0070 | GAP_UNRESOLVED |
| R2 | disjoint | 8 | 7 | +0.0541 | +0.0555 | -0.0013 | GAP_UNRESOLVED |
| R2 | disjoint | 8 | 8 | +0.0224 | +0.0442 | -0.0218 | SAME_SIGN_GAP |
| R2 | big5 | 8 | 1 | +0.0608 | +0.0758 | -0.0151 | GAP_UNRESOLVED |
| R2 | big5 | 8 | 2 | +0.1109 | +0.0872 | +0.0237 | GAP_UNRESOLVED |
| R2 | big5 | 8 | 3 | +0.1394 | +0.0908 | +0.0486 | GAP_UNRESOLVED |
| R2 | big5 | 8 | 4 | +0.1204 | +0.0964 | +0.0241 | GAP_UNRESOLVED |
| R2 | big5 | 8 | 5 | +0.1606 | +0.0856 | +0.0750 | SAME_SIGN_GAP |
| R2 | big5 | 8 | 6 | +0.1265 | +0.0806 | +0.0459 | GAP_UNRESOLVED |
| R2 | big5 | 8 | 7 | +0.0859 | +0.0753 | +0.0106 | GAP_UNRESOLVED |
| R2 | big5 | 8 | 8 | +0.0588 | +0.0595 | -0.0007 | GAP_UNRESOLVED |
| R3 | disjoint | 8 | 1 | +0.0117 | +0.0040 | +0.0077 | GAP_UNRESOLVED |
| R3 | disjoint | 8 | 2 | +0.0112 | +0.0043 | +0.0069 | GAP_UNRESOLVED |
| R3 | disjoint | 8 | 3 | +0.0078 | +0.0043 | +0.0035 | GAP_UNRESOLVED |
| R3 | disjoint | 8 | 4 | +0.0010 | +0.0056 | -0.0046 | GAP_UNRESOLVED |
| R3 | disjoint | 8 | 5 | -0.0067 | +0.0072 | -0.0139 | GAP_SIGN_UNRESOLVED |
| R3 | disjoint | 8 | 6 | -0.0119 | +0.0076 | -0.0195 | GAP_SIGN_UNRESOLVED |
| R3 | disjoint | 8 | 7 | -0.0088 | +0.0092 | -0.0180 | GAP_SIGN_UNRESOLVED |
| R3 | disjoint | 8 | 8 | -0.0207 | +0.0069 | -0.0276 | SIGN_FLIP |
| R3 | big5 | 8 | 1 | -0.0165 | +0.0121 | -0.0285 | GAP_UNRESOLVED |
| R3 | big5 | 8 | 2 | -0.0096 | +0.0114 | -0.0209 | GAP_UNRESOLVED |
| R3 | big5 | 8 | 3 | -0.0015 | +0.0206 | -0.0221 | GAP_UNRESOLVED |
| R3 | big5 | 8 | 4 | -0.0088 | +0.0190 | -0.0278 | GAP_UNRESOLVED |
| R3 | big5 | 8 | 5 | +0.0123 | +0.0159 | -0.0036 | GAP_UNRESOLVED |
| R3 | big5 | 8 | 6 | +0.0090 | +0.0137 | -0.0048 | GAP_UNRESOLVED |
| R3 | big5 | 8 | 7 | +0.0094 | +0.0167 | -0.0073 | GAP_UNRESOLVED |
| R3 | big5 | 8 | 8 | +0.0268 | +0.0150 | +0.0118 | GAP_UNRESOLVED |
| R4 | disjoint | 8 | 1 | +0.0185 | +0.0079 | +0.0106 | SAME_SIGN_GAP |
| R4 | disjoint | 8 | 2 | +0.0056 | +0.0075 | -0.0019 | GAP_UNRESOLVED |
| R4 | disjoint | 8 | 3 | -0.0052 | +0.0025 | -0.0077 | GAP_UNRESOLVED |
| R4 | disjoint | 8 | 4 | -0.0114 | +0.0003 | -0.0118 | GAP_SIGN_UNRESOLVED |
| R4 | disjoint | 8 | 5 | -0.0190 | -0.0017 | -0.0173 | GAP_SIGN_UNRESOLVED |
| R4 | disjoint | 8 | 6 | -0.0270 | -0.0001 | -0.0268 | GAP_SIGN_UNRESOLVED |
| R4 | disjoint | 8 | 7 | -0.0349 | -0.0006 | -0.0343 | GAP_SIGN_UNRESOLVED |
| R4 | disjoint | 8 | 8 | -0.0301 | +0.0047 | -0.0348 | SIGN_FLIP |
| R4 | big5 | 8 | 1 | +0.0147 | +0.0143 | +0.0004 | GAP_UNRESOLVED |
| R4 | big5 | 8 | 2 | -0.0038 | +0.0137 | -0.0175 | GAP_UNRESOLVED |
| R4 | big5 | 8 | 3 | +0.0073 | +0.0160 | -0.0087 | GAP_UNRESOLVED |
| R4 | big5 | 8 | 4 | +0.0016 | +0.0148 | -0.0132 | GAP_UNRESOLVED |
| R4 | big5 | 8 | 5 | +0.0110 | +0.0053 | +0.0056 | GAP_UNRESOLVED |
| R4 | big5 | 8 | 6 | -0.0074 | -0.0016 | -0.0058 | GAP_UNRESOLVED |
| R4 | big5 | 8 | 7 | -0.0121 | -0.0063 | -0.0058 | GAP_UNRESOLVED |
| R4 | big5 | 8 | 8 | -0.0133 | +0.0032 | -0.0165 | GAP_UNRESOLVED |
| R5 | disjoint | 8 | 1 | -0.1834 | -0.0773 | -0.1061 | SAME_SIGN_GAP |
| R5 | disjoint | 8 | 2 | -0.2113 | -0.0711 | -0.1402 | SAME_SIGN_GAP |
| R5 | disjoint | 8 | 3 | -0.2114 | -0.0685 | -0.1429 | SAME_SIGN_GAP |
| R5 | disjoint | 8 | 4 | -0.2266 | -0.0674 | -0.1591 | SAME_SIGN_GAP |
| R5 | disjoint | 8 | 5 | -0.2241 | -0.0643 | -0.1599 | SAME_SIGN_GAP |
| R5 | disjoint | 8 | 6 | -0.2251 | -0.0598 | -0.1653 | SAME_SIGN_GAP |
| R5 | disjoint | 8 | 7 | -0.2269 | -0.0570 | -0.1699 | SAME_SIGN_GAP |
| R5 | disjoint | 8 | 8 | -0.2432 | -0.0627 | -0.1805 | SAME_SIGN_GAP |
| R5 | big5 | 8 | 1 | -0.2964 | -0.0799 | -0.2165 | SAME_SIGN_GAP |
| R5 | big5 | 8 | 2 | -0.3162 | -0.0873 | -0.2289 | SAME_SIGN_GAP |
| R5 | big5 | 8 | 3 | -0.3198 | -0.0782 | -0.2415 | SAME_SIGN_GAP |
| R5 | big5 | 8 | 4 | -0.3286 | -0.0696 | -0.2590 | SAME_SIGN_GAP |
| R5 | big5 | 8 | 5 | -0.2984 | -0.0680 | -0.2304 | SAME_SIGN_GAP |
| R5 | big5 | 8 | 6 | -0.2900 | -0.0698 | -0.2201 | SAME_SIGN_GAP |
| R5 | big5 | 8 | 7 | -0.3236 | -0.0671 | -0.2565 | SAME_SIGN_GAP |
| R5 | big5 | 8 | 8 | -0.2439 | -0.0673 | -0.1766 | SAME_SIGN_GAP |

## Exploratory drift-energy decomposition

This post-registered mechanism readout does not change the temporal classification. For centered K=8 paths, let `b=beta_B-mean(beta_B)` and `w=beta_W-mean(beta_W)`. Then `||b-w||^2 = ||b||^2 + ||w||^2 - 2<b,w>`. Ratios can be negative or exceed one because the cross term records cancellation or amplification; they are not variance shares.

| relation | cohort | range beta_B | range beta_W | range Delta_T | corr paths | B/E_D | W/E_D | cross/E_D |
|---|---|---|---|---|---|---|---|---|
| R1 | big5 | +0.0562 | +0.0420 | +0.0371 | +0.7523 | 2.28 | 1.51 | -2.79 |
| R1 | disjoint | +0.0383 | +0.0260 | +0.0229 | +0.8156 | 2.97 | 1.74 | -3.71 |
| R2 | big5 | +0.1018 | +0.0369 | +0.0901 | +0.7450 | 1.58 | 0.15 | -0.73 |
| R2 | disjoint | +0.0740 | +0.0191 | +0.0551 | +0.9465 | 1.78 | 0.13 | -0.91 |
| R3 | big5 | +0.0433 | +0.0092 | +0.0404 | +0.1362 | 1.01 | 0.05 | -0.06 |
| R3 | disjoint | +0.0324 | +0.0052 | +0.0353 | -0.8163 | 0.78 | 0.02 | 0.20 |
| R4 | big5 | +0.0280 | +0.0223 | +0.0232 | +0.6609 | 1.71 | 1.11 | -1.82 |
| R4 | disjoint | +0.0534 | +0.0096 | +0.0454 | +0.7257 | 1.34 | 0.05 | -0.39 |
| R5 | big5 | +0.0846 | +0.0202 | +0.0824 | +0.2971 | 1.10 | 0.08 | -0.18 |
| R5 | disjoint | +0.0598 | +0.0203 | +0.0745 | -0.8135 | 0.57 | 0.08 | 0.35 |

The decomposition distinguishes two gates that the old wording compressed: temporal persistence of the average within-person response and temporal persistence of the cross-level transport family. Either can hold while the other changes.

## Reading boundary

- `TEMPORAL_HETEROGENEITY_DETECTED` means the X5 aggregate within-person slope is a horizon average. It is not personality change.
- `TEMPORALLY_EQUIVALENT_AT_0.02` is equivalence only for this projection, pool, horizon, and nested partition family.
- Segments are equal usable-event-count blocks, so every reported trend is an event-order trend, not a calendar-time trend. Boundaries can differ across relations when their usable events differ.
- Segment family changes narrow the cross-level transport claim; they do not invalidate the observed aggregate relation. Family retention uses pointwise intervals and is descriptive, not a second familywise test.
- Metadata only, aggregate only, no text bodies, no external labels, no person-level output.

## Files

- `results/m4_x5_temporal_transport_audit/reproduction.json`
- `results/m4_x5_temporal_transport_audit/summary.json`
- `results/m4_x5_temporal_transport_audit/temporal_classifications.csv`
- `results/m4_x5_temporal_transport_audit/segment_estimates.csv`
- `results/m4_x5_temporal_transport_audit/drift_decomposition.csv`
