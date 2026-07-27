# V8 V3.7H.1 Paired-Schedule Refusal R4 Power Report

Date: 2026-07-26

Decision:
`V8_SCHEDULE_REFUSAL_V37H1_R4_POWER_CANDIDATE_PASS`

Status: synthetic design and power calibration only. No confirmation seed has
been opened and no real-text or psychological claim is licensed.

## Question

V3.7H showed that a resolution operator can become more precise while moving
toward an author-specific opportunity-contaminated target. V3.7H.1 therefore
asks whether the same authors, observed under two registered opportunity
schedules, produce more score-space separation than can be explained by
independent technical-stream noise.

At budget \(m\), let \(M^{s,r}_{u,m}\) denote the frozen SUICA score for author
\(u\), schedule \(s\in\{A,B\}\), and technical stream \(r\in\{1,2\}\). Define

\[
\bar M^s_{u,m}
=
\frac{M^{s,1}_{u,m}+M^{s,2}_{u,m}}{2},
\]

\[
V_{\mathrm{stream},m}
=
\mathbb E\left\|
\frac{M^{A,1}_m-M^{A,2}_m}{2}
\right\|^2
+
\mathbb E\left\|
\frac{M^{B,1}_m-M^{B,2}_m}{2}
\right\|^2,
\]

and

\[
Q_m
=
\frac{
\mathbb E\|\bar M^B_m-\bar M^A_m\|^2
-V_{\mathrm{stream},m}
}{
d^{-1}\operatorname{tr}
\left(W_m\widehat\Sigma_GW_m^\top\right)
}.
\]

The signed numerator is retained. It may be negative in a finite null sample;
operational refusal is one-sided:

\[
Q_{512}\ge .01.
\]

The cumulative-path predictor is diagnostic only and cannot trigger refusal.

## Corrections before R4

Earlier design runs are permanently superseded:

1. R1 used different planted response maps in refusal, probe, and evaluation
   panels. This invalidated cross-panel cumulative transport interpretation.
2. R2 shared the response map, but incorrectly allowed the cumulative
   diagnostic to trigger operational refusal. Its null false-refusal result
   refuted that union rule.
3. R3 made paired \(Q\) the sole operational channel and normalized it in
   score space.
4. R4 added scorer-side score-space effect metadata, fresh seeds, and
   Bonferroni one-sided familywise intervals over all 15
   geometry-by-effect cells.

Synthetic raw and score-space effect sizes enter neither detector.

## Integrity

- 100 repetitions per cell;
- 3 response geometries and 5 planted raw effect levels;
- 1,500 metric rows;
- 6,200 unique RNG streams out of 6,200;
- maximum nested-prefix identity error: 0;
- all numeric outputs finite;
- run manifest: PASS;
- artifact inventory: PASS;
- 30 targeted V3.7G/H/H.1 tests passed before the R4 run.

## Familywise power result

Decision-facing one-sided bounds use Bonferroni cell confidence
\(1-.05/15=.996\overline6\). Lower and upper directions are separate
families; no joint two-sided 95% interval over all 30 reported tails is
claimed. The 5,000-draw tail bootstrap remains a design diagnostic, not a
confirmation-grade uncertainty procedure.

| Geometry | Raw \(\eta\) | Refusals | Familywise one-sided bound | Mean \(Q_{512}\) | Mean score-space \(\eta\) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Low-rank linear | .00 | 0/100 | upper .0554 | .00003 | .00000 |
| Random rotation | .00 | 0/100 | upper .0554 | -.00019 | .00000 |
| Nonlinear tanh | .00 | 0/100 | upper .0554 | -.00078 | .00000 |
| Low-rank linear | .10 | 100/100 | lower .9446 | .07581 | .07726 |
| Random rotation | .10 | 100/100 | lower .9446 | .07589 | .07636 |
| Nonlinear tanh | .10 | 100/100 | lower .9446 | .07555 | .07564 |
| Low-rank linear | .20 | 100/100 | lower .9446 | .15232 | .15244 |
| Random rotation | .20 | 100/100 | lower .9446 | .15335 | .15249 |
| Nonlinear tanh | .20 | 100/100 | lower .9446 | .15147 | .15164 |

The detector also reached:

- \(\eta=.02\): 89%, 97%, and 96% for low-rank, rotation, and nonlinear
  geometries;
- \(\eta=.05\): 100% in all three geometries.

Under simultaneous lower bounds, the minimum qualified raw effect was .05
for low rank and .02 for rotation and nonlinear response.

Across all 1,500 cells, \(Q_{512}\) tracked the scorer-side planted effect
with correlation .9958, mean bias -.00014, and RMSE .00503. The apparent
difference between raw \(\eta=.10\) and \(Q\approx.076\) is therefore the
frozen score operator's attenuation, not detector bias.

## Cumulative diagnostic

The cumulative detector still fired in 12 of 300 null cells. This confirms
the R2 audit: a learned cross-panel response map is useful as a mechanism
probe but is not calibrated as a safety decision. It remains excluded from
operational refusal.

## Theory update

R4 supports the following synthetic identification statement:

> Under two paired schedules, two independent technical streams per schedule,
> the frozen V3.7H score operator, and the registered Gaussian event process,
> excess schedule-response energy can be estimated in score space and can
> refuse a stable-author interpretation with high power.

This closes one design-level ambiguity exposed by V3.7H. It does not make
condition response disappear. It makes that response observable by design
instead of allowing it to alias stable author geometry.

The correct mathematical object remains:

\[
\text{score}
=
\text{stable author position}
+
\text{condition-response component}
+
\text{technical uncertainty}.
\]

The paired schedule supplies the counterfactual needed to separate the first
two components. A single observational schedule cannot generally do so.

## Unclosed adversarial boundary

R4 does not yet cover:

- correlated technical streams or common shocks;
- heteroskedastic, heavy-tailed, or serially dependent event noise;
- pairing errors, missing schedules, or informative missingness;
- response affecting only 5%, 10%, or 20% of authors;
- response concentrated near the score operator's kernel;
- transient or reversing responses whose endpoint returns to zero;
- global schedule shifts not coupled to author structure;
- alternative panel sizes, dimensions, or real token-routing errors.

Therefore R4 is a power candidate, not a confirmation-ready universal
refusal theorem. The next work package must adversarially map these
identifiability boundaries before any public seal or fresh confirmation run.

Likewise, `interval_claim_allowed=true` means only "not rejected by this
detector." It does not prove schedule invariance.

## Reproducibility

Artifacts:
`results/v8_schedule_refusal/v37h1_r4_familywise_score_space_power_100rep_20260726/`

Config:
`configs/v8_schedule_refusal_v37h1.json`

Core:
`suica_core/v8_resolution_filtration_h1.py`

Runner:
`scripts/run_suica_v8_schedule_refusal_v37h1.py`
