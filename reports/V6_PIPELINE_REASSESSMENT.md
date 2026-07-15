# V6 P0-P6 Pipeline Reassessment

Date: 2026-07-13.

The archived full numerical artifact is preserved unchanged at
`results/v6_pipeline_falsification/full/v6_pipeline_falsification_full.json` with SHA-256
`8cacfbc2f44239863e4d85c31b253eea37138481290af2b761ab9261ef6a7ecc`.

## Correction

The original acceptance code called the Wilson lower bound across seven heterogeneous
alternative scenarios `power`. That quantity is not statistical power. It has been
removed from the current code (hash
`5fbd3e4bfec5d4a399006d993eff4bb14dd1f86730be0958295ad1bad7018b84`).

## Reassessment from preserved sufficient results

- Scenario detection: 7/7 at `p_FWER <= .05` (all are `.0005`).
- Null calibration FPR: `.04952`, Wilson 95% CI `[.04605, .05324]`.
- Congruence in licensed worlds: `.967-.995`.
- Person-delta gate passes for the three person-amplitude scenarios.
- The P2 segmentation-artifact world correctly has no person delta; it is not counted
  as a person-response success.

Verdict: **scenario detection PASS; null calibration PASS; statistical power was not
estimated by this artifact**. Power is evaluated separately by repeated alternative DGP
draws in `results/v6_pipeline_power/`.
