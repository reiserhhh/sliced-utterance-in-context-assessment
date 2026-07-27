# V8 V3.7H.4D R2A Narrow Iid Confirmation

Date: 2026-07-27

Decision:
`V8_MINORITY_INFORMATION_FRONTIER_V37H4D_R2A_PASS_IID_FIXED_M8`

## Frozen scope

- active-cell SNR 15.0;
- fixed support;
- iid sparse block;
- eight active test authors and four active conditions;
- Gaussian and standardized heteroskedastic \(t_5\);
- K=128;
- unchanged R1 99-draw author wild-sign detector and Holm alpha .05.

The config froze the SHA-256 hashes of the R1 core, R2 planting module, and
R2 evaluator. All source locks matched.

## Fresh results

| Cell | Detections | Rate | Simultaneous interval |
| --- | ---: | ---: | ---: |
| W0 Gaussian | 28/1000 | .028 | [.0187, .0402] |
| W0 \(t_5\) | 28/1000 | .028 | [.0187, .0402] |
| IID m=8 Gaussian | 997/1000 | .997 | [.9913, .9994] |
| IID m=8 \(t_5\) | 998/1000 | .998 | [.9928, .9998] |

The W0 upper bounds were below .05 and both CRC-or-HC power lower bounds were
above .90.

All 4,000 rows, 12,000/12,000 unique seeds, numeric checks, source locks, and
projection compatibility checks passed.

## Interpretation

Confirmed:

> Under this exact iid synthetic family and observation budget, eight active
> test authors are sufficient for highly reliable detection by the frozen
> H4D-R1 detector.

Not confirmed:

- \(m=8\) for intrinsic-zero-sum or arbitrary minority geometry;
- a universal scalar information threshold;
- optimality of CRC or Higher Criticism;
- psychological, personality, semantic, causal, real-text, diagnostic, or
  clinical validity.

## Artifacts

- `configs/v8_minority_information_frontier_v37h4d_r2a_confirmation.json`
- `scripts/run_suica_v8_minority_information_frontier_v37h4d_r2a_confirmation.py`
- `results/v8_minority_information_frontier/v37h4d_r2a_confirmation_4000rep_20260727/`
