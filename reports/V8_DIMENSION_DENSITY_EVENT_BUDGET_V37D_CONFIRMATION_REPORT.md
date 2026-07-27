# V8 Dimension-Density-Event-Budget V3.7D Confirmation Report

Decision: `V8_DIMENSION_DENSITY_EVENT_BUDGET_V37D_CONFIRMATION_PASS`

Independent methodology ruling: `PASS_WITH_CAVEATS`

## Registered question

V3.7D tested whether author-operator recovery and cross-session author
identification are nested properties or can fail in opposite directions. The
registered joint outcomes were

\[
R=\mathbf 1(r_{\rm truth}\ge .80,\ R_{\rm split}\ge .50),
\]

\[
I=\mathbf 1(\mathrm{AUC}_{\rm hard}\ge .80,\ \mathrm{Top1}\ge .50).
\]

The decisive events were \(R=1,I=0\) and \(R=0,I=1\), not separate marginal
metric passes.

## Design and integrity

- Forty fresh latent worlds used canonical seed `20400131`.
- Each world used 96 authors to fit the reference router and stable basis.
- The 32/96/192 evaluation sets were nested subsets of 192 entirely new
  authors.
- Ranks 2/4/8/12 used nested columns of one rank-12 basis under fixed total
  author RMS.
- The 64- and 128-event conditions reused latent probabilities and used
  independent event samples.
- All 960 result rows were finite; all 2,880 event/metric seeds were unique.
- Training/evaluation overlap was zero in every row.
- The V3.7D content seal and V3.7C parent seal passed.
- The artifact inventory passed 6/6.
- An isolated same-seed rerun reproduced `paired_metrics.csv`,
  `cell_summary.csv`, `decision.json`, and `config_effective.json` byte for
  byte.

All 13 frozen gates passed.

## Joint phase results

At 128 events:

| True rank | Authors | Truth r | Split rel. | Hard AUC | Top-1 | Dominant joint state |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 32 | .976 | .880 | .892 | .315 | recovery only: .975 |
| 2 | 96 | .978 | .889 | .717 | .145 | recovery only: 1.000 |
| 2 | 192 | .977 | .884 | .605 | .082 | recovery only: 1.000 |
| 8 | 32 | .958 | .839 | .990 | .902 | recovery and identity: 1.000 |
| 8 | 96 | .959 | .851 | .980 | .833 | recovery and identity: 1.000 |
| 8 | 192 | .956 | .845 | .969 | .768 | recovery and identity: 1.000 |
| 12 | 32 | .775 | .799 | .986 | .845 | identity only: .925 |
| 12 | 96 | .773 | .788 | .958 | .713 | identity only: .975 |
| 12 | 192 | .771 | .787 | .935 | .616 | identity only: .975 |

Rank 4 formed the transition region: recovery passed in all 128-event cells,
while joint identity declined from .975 at 32 authors to zero at 192 authors.

## Paired effects

Increasing the evaluation population from 32 to 192 authors changed
hard-neighbor AUC by:

| True rank | Mean AUC loss | Bootstrap 95% interval |
| ---: | ---: | ---: |
| 2 | .288 | [.281, .294] |
| 4 | .104 | [.098, .111] |
| 8 | .022 | [.019, .025] |

The registered rank-by-density interaction was `.266 [.259, .273]`.
Rank-2 random-neighbor AUC changed by only `.006 [.001, .010]`, showing that
the large hard-neighbor loss was local crowding rather than a generic
same-author score collapse.

For rank 12, changing only the scoring basis from the frozen rank-8 estimator
to the true-rank sensitivity restored mean truth correlation to `.940`. The
paired Fisher-z gain was `.713 [.703, .724]`, and paired NRMSE improved by
`.292 [.288, .296]`. Recomputing these intervals with repetition-level
cluster bootstrap produced the same conclusion.

For ranks at most 8, moving from 64 to 128 events improved truth recovery in
all 9 cells. The mean paired Fisher-z gain was `.717 [.699, .734]`.

## Mathematical result

Let

\[
e_u=\|\widehat D_u-D_u\|,
\qquad
m_u=\min_{v\ne u}\|D_u-D_v\|.
\]

Recovery is governed by operator error relative to total signal. Identity
also requires local separation, approximately \(2e_u<m_u\). In a regular
\(K\)-dimensional population, nearest-neighbor margin contracts with local
population density, approximately \(m_u=O(U^{-1/K})\). This explains the
rank-2 forward separation: adding authors changes local margin without
changing whether the shared operator surface is recovered.

Conversely, when the true operator dimension exceeds estimator capacity
\(r\),

\[
\|D_u-\widehat D_u\|^2
=
\|(I-P_r)D_u\|^2
+
\|P_rD_u-\widehat D_u\|^2,
\]

when \(\widehat D_u\) lies in the fitted subspace. The retained projection can
still distinguish authors even when omitted coordinates prevent full
operator recovery. This explains the registered rank-12 reverse separation.

The finite-sample state space is therefore genuinely four-valued:

\[
(R,I)\in\{(0,0),(1,0),(0,1),(1,1)\}.
\]

Operator recovery, repeated-measurement reliability, and author
identifiability are neither equivalent nor linearly ordered.

## Licensed conclusion

Within the registered synthetic, author-inductive design, recovery and
cross-session identification are bidirectionally separable. Dimension,
local author density, event budget, and estimator capacity control different
parts of the phase diagram.

This result does not identify personality, a real-text dynamic factor,
intelligence, a thought node, a clinical state, a universal dimension, or a
universal sample-size threshold.

## Canonical artifacts

- `results/v8_dimension_density_budget/v37d_confirmation_final_20260726/decision.json`
- `results/v8_dimension_density_budget/v37d_confirmation_final_20260726/paired_metrics.csv`
- `results/v8_dimension_density_budget/v37d_confirmation_final_20260726/cell_summary.csv`
- `configs/v8_dimension_density_budget_v37d_confirmation_seal.json`
- `reports/V8_DIMENSION_DENSITY_EVENT_BUDGET_V37D_INDEPENDENT_AUDIT.md`
