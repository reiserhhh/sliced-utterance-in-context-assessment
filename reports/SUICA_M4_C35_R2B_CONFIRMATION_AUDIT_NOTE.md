# SUICA M4-C.3.5-R2B Confirmation Audit Note

## Ruling

`M4_C35_R2B_PARTIAL_CONDITIONAL_EFFECT`

R2B is a meaningful confirmatory structural effect, but it is not a chart
replacement GO. Sixteen of seventeen conjunctive gates passed. The frozen
zero-native-refusal gate failed and cannot be changed after opening.

## Confirmed evidence

- Eligible `R-B0` gain: `.12266`, cluster LCB `.09338`
- Oracle-headroom recovery: `.81464`, LCB `.67984`
- Accessible efficiency: `.98739`, LCB `.98008`
- Eligible positive repetitions: `8/8`, `7/8`, `8/8`
- `R-Br_var` gain LCB: `.10827`
- `R-Br_rep` gain LCB: `.12447`
- Maximum main-cell CKA permutation p: `.005`
- History-sentinel gain LCB: `.00654`
- Compensation-boundary `R-Oest` LCB: `-.00026`
- Null false successes: `0/120`, Wilson upper `.03102`
- Basis, source shuffle, support shift, latent alias, author permutation,
  gauge, common shift, hazard, runtime, config, protocol, and bundle controls
  passed

The aggregate contains 1600 unique metric cells, 312 unique controls, all
repetitions `0..7`, 40 main cells, and 120 null cells.

## Failed gate

Native RCCA refusal rate was `.0125` rather than the frozen `0`:

1. repetition 3, `fast_return_equal_marginal__draw_01`, coverage `.6875`
2. repetition 7, `endogenous_creation_expansion`, coverage `.75`

Both retained shared rank 6 and failed only `SUPPORT_SHIFT`. The refused main
cell still had held-out CKA `.99836` and forced-score `R` geometry `.96875`
versus `Oest` `.96861`, but that truth-open observation cannot override the
pre-response refusal.

## Interpretation

RCCA identifies a useful chart, but the chart is partial rather than total.
The present effect is computed by forcing `R` in every cell; it is not the
value of an abstaining deployment policy. The next admissible object is

```text
A_i  = pre-response RCCA acceptance
Pi_i = R_i if A_i=1 else B0_i
Delta_Pi = E[A_i (Gamma_R - Gamma_B0)]
```

The primary target is full planned-population policy value. Accepted-stratum
performance is secondary and cannot replace it. Coverage thresholds and
fallback must be frozen before response opening.

## Prohibited reinterpretations

- Do not rename R2B as GO.
- Do not remove the refused cells and recompute.
- Do not lower the `.80` coverage threshold post hoc.
- Do not claim the refusal rule improves performance.
- Do not claim unconditional chart replacement, causal mechanism recovery,
  natural-text transport, personality validity, clinical use, or M4-D
  readiness.
