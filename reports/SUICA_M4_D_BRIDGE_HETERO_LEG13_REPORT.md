# SUICA M4-D Leg 13 — Bridge Heteroscedastic Calibration (rank selector)

## Decision

`M4_D_LEG13_BRIDGE_HETERO_PIVOT_TRADEOFF_FRONTIER`

Leans 0/3; the registered PIVOT FIRES: neither one-step floor recalibration
restores license AUC >= .88 on the heteroscedastic battery — while nothing
anywhere breaks the group-only refusal (200/200 designed-null and 360/360
heteroscedastic group-only, in EVERY arm). Per the registration, the
refusal-safety vs sensitivity trade-off frontier is recorded as the
bridge's documented operating curve (a valid deliverable, not a failure).
The substantive outcome is sharper than the leans anticipated: the two
calibration goals ANTI-CORRELATE across the variants — the variance-
weighted floor fixes the C2 rank cap completely (60/60 un-capped, median
margin .21) but starves rank elsewhere and loses ordering; the permutation
floor repairs ordering (anchor individual-family AUC .944 -> .995,
eliminating Leg 2's hard-zero band) but under-floors structured noise and
collapses the index's tau-scale. No single one-step recalibration serves
both. Tier: OPEN-EXPLORATION; nothing here may be cited above EXPLORATORY.

## Question

Leg 2's disclosed limitation (its honest-anomaly #3): the rigidity index's
auto-rank (negative-spectrum floor, eigenvalue > 2x|most negative|) hits
the rank cap with near-zero margin on the C2 empirical-logit fields, and
the floor is generally uncalibrated for heteroscedastic noise. Instrument
development: does a one-step variance-aware floor fix rank selection and
license quality on realistic noise fields without harming the designed-null
refusal?

## Anchor gate (reproduce-first, passed bit-tight)

Leg 2's battery re-run (seed 20260801, 20 replicates, 600 worlds) BEFORE
any new arm: pooled license AUC diff **0.0** (.8691390374980287),
individual-family AUC diff **0.0** (.9438683127572017), group-only refusal
**200/200** with 0 false licenses, per-row max |index diff| vs the
persisted CSV **1.11e-16** (e-ratio likewise). New-arm computation was
gated on these asserts (`reproduce_anchor` raises otherwise).

## Frozen design

- Script `scripts/run_suica_m4_d_bridge_hetero_leg13.py`; module additions
  ADDITIVE in `suica_core/m4_relation_bridge.py` (default selector path
  byte-identical; all 9 leg-2 tests untouched and passing).
- Hetero seed `20260802`, 20 replicates/cell; 1440 worlds x 3 arms = 4320
  rows; runtime 157 s. Ground-truth labeling rule reused VERBATIM
  (oracle-rank `reconstruction_vs_truth`, within-block permutation, margin
  ratio .5, identical seed offsets); license tau = .5 unchanged; the
  stress-stability probe unchanged in all arms — arms differ ONLY in the
  rank-selection floor.
- World battery (grids fixed before the run):
  - **H1 `pair_magnitude`**: per-pair sd `= noise * D2_uv` (exactly
    variance-matched to the homoscedastic battery at the same noise
    level). individual/group_only x full leg-2 grid x 20; mixed eps .2 x
    noise {.05,.2,.6} x 20. 420 worlds.
  - **H2 `author_lognormal`**: mean-one log-normal author factors,
    sd `= noise * rms(D2) * sqrt(f_u f_v)`; registered sigma grid
    {0.5, 1.0, 1.5} x noise {.05,.2,.6} x individual/group_only x 20 +
    mixed (eps .2, noise .2) x sigma grid x 20. 420 worlds.
  - **H3 `c2_empirical_logit`**: the anchor's 60 C2-machinery worlds
    (identical seeds, hence bit-identical to Leg 2's; all 60 baseline-cap).
- Arms (one step each, no search):
  - **baseline**: negative-spectrum floor, selection at 2x floor (leg 2
    verbatim).
  - **V1 `variance_weighted`**: rank-one row/col per-cell variance model
    from the replicate difference `(R1-R2)/sqrt(2)`; floor = analytic
    weighted-null edge `max_u sqrt(sum_v s_uv^2)` (reduces to the
    homoscedastic edge, so the baseline's 2x multiplier carries over).
  - **V2 `permutation`**: within-row permutation null of the replicate
    difference (row magnitude profiles preserved), 199 draws, floor at the
    null 95th percentile, multiplier 1.0 (parallel-analysis convention).

## Results — per family x arm (license AUC / refusal / rank)

License AUC is computable only where labels are mixed; group-only families
report refusal instead. `rank*` = mean selected rank (planted oracle 3).

| family (label rate) | arm | AUC | licensed | rank* | zero-rank | cap-hit |
|---|---|---|---|---|---|---|
| h1_individual (.65) | baseline | .9708 | .378 | 1.66 | .367 | 0 |
| | V1 | .8846 | .361 | 1.28 | .500 | 0 |
| | V2 | **.9810** | .100 | 3.18 | .000 | 0 |
| h2_individual (.87) | baseline | .9557 | .461 | 2.12 | .178 | 0 |
| | V1 | .8686 | .433 | 1.64 | .361 | 0 |
| | V2 | .8216 | .072 | 3.78 | .000 | 0 |
| h1_mixed (.33) | baseline | .9450 | .233 | 1.78 | 0 | 0 |
| | V1 | .9538 | .267 | 1.63 | 0 | 0 |
| | V2 | .8075 | .083 | 2.80 | 0 | 0 |
| h2_mixed (.13) | baseline | .5240 | .017 | 1.63 | 0 | 0 |
| | V1 | .5625 | .017 | 1.33 | .033 | 0 |
| | V2 | .5793 | .000 | 3.07 | 0 | 0 |
| h1_group_only (0) | all | — | 0 (refused 180/180 each) | 1.13–2.20 | | 0 |
| h2_group_only (0) | all | — | 0 (refused 180/180 each) | 1.32–2.98 | | 0 |

Pooled license AUC (H1+H2+H3, 900 rows/arm, 301 positives):
**baseline .8372, V1 .7268, V2 .8316**; H1+H2 only: .8275 / .7267 / .8289.
Per mechanism (baseline / V1 / V2): H1 .8747 / .7717 / .8444;
H2 .7764 / .6808 / .8128; **H3 = NaN by construction**: all 60 C2 worlds
carry ground-truth label 0 (at trials=6 granularity the oracle-rank
reconstruction never beats the 2x permuted-truth bar — Leg 2's
detection-vs-estimation finding, bit-identical here), so the family is
single-class and per-mechanism AUC is undefined. H3 therefore enters the
pooled leans only as easy negatives (its indices rank low), which makes
lean (a) HARDER to hold, and this is exactly why lean (c) was registered
as a rank/margin lean rather than an AUC lean for the C2 family.

Homoscedastic compatibility (anchor battery under the variants): pooled
AUC baseline .8691 / V1 .8313 / **V2 .8743**; individual-family .9439 /
.9407 / **.9949**. V2 keeps rank alive through the deep-noise band
(index>0 rate at noise 1.0/1.5/2.5: baseline .20/0/0 -> V2 1.0/1.0/.60),
which is precisely Leg 2's localized lean-(a) shortfall (the hard-zero
refusal band) repaired — prospectively, on the same worlds, by a floor
change alone.

Labels move with the mechanisms (truth, not instrument): at variance-
matched average noise, heteroscedasticity destroys true reconstructability
earlier — h1_individual label rate at noise 1.0 is .05 (homoscedastic
anchor: .75); h2_individual at noise .6 falls 1.00 -> .50 (sigma 1.0) ->
.35 (sigma 1.5).

## Refusal battery (non-negotiable) — INTACT in every arm

| battery | baseline | V1 | V2 |
|---|---|---|---|
| designed-null (leg-2 group_only + c2_group_only, 200) | 200/200 | 200/200 | 200/200 |
| heteroscedastic group-only (h1+h2, 360) | 360/360 | 360/360 | 360/360 |
| designed-null max index | .2680 | .2680 | .2680 |

The max-index world is a clean planted group_only cell where all arms
select the same rank, hence the identical maxima. Every tau > .268 is
null-safe for every arm on this battery.

## C2 cap analysis (all 60 anchor C2 worlds baseline-capped)

Mechanism finally identified exactly: the C2 field is an EXACT squared-
distance matrix of noisy empirical-logit profiles, so its Gram is PSD up
to float error — the negative spectrum is numerically empty (floor ~2e-9
at top eigenvalue ~2.3e3) and EVERYTHING clears 2x floor: the cap was a
total floor collapse, not mere underestimation (sharpens Leg 2 anomaly 3).
The profile-noise Gram `J E[ee^T] J` is a POSITIVE mean shift, invisible
to any negative-spectrum or replicate-difference fluctuation estimate.

| arm | non-cap & margin>0 (of 60) | cap-hit | mean rank | median margin |
|---|---|---|---|---|
| V1 variance_weighted | **60** | 0 | 2.28 | .2116 |
| V2 permutation | 40 | 20 (all c2_joint) | 5.82 | .0463 |

V1's worst-row analytic edge overshoots into the noise-lifted tail and
certifies a small rank with a real gap (c2_group_only 2.2, c2_joint 2.3);
V2's fluctuation-only null (floor ~296 vs tail 450–650) stays inside the
mean-shifted bulk on the joint worlds. All C2 worlds remain REFUSED in all
arms (as they must — E-ratio never clears the 2x label bar at trials=6).

## Lean adjudication (registered bars; 0/3)

- **Lean (a) — MISS.** Registered: baseline license AUC <= .80 under the
  heteroscedastic families. Result: pooled **.8372** (> .80). The
  degradation is real but localized: H2-pooled .7764 and the h2_mixed cell
  .5240, vs .944 homoscedastic individual-family; per-family ordering
  within H1/H2 stays high (.9557–.9708). The registered pooled bar
  overestimated how much additive heteroscedasticity hurts ordering; the
  genuinely broken piece was always the C2 floor collapse (H3, label-less).
- **Lean (b) — MISS (pivot condition).** No variant reaches AUC >= .88:
  V1 .7268 (WORSE than baseline — and NOT from variance-model
  misestimation: the rank-one model tracks realized per-row noise power at
  Spearman .975; the ANALYTIC EDGE itself is a worst-row upper bound, and
  with the 2x multiplier it zero-ranks 22.6% of reconstructable hetero
  worlds, pinning their index at 0 below cleanly-refused group-only
  worlds), V2 .8316
  (< .88; best per-mechanism H2 .8128 and best anchor numbers, but its
  under-floored ranks compress margins). Both keep refusal 200/200 —
  refusal safety was never the binding constraint; SCALE calibration is.
- **Lean (c) — MISS under the pre-fixed winner rule.** Winner = max
  hetero AUC among refusal-safe variants = V2: 40/60 non-cap with positive
  margin < 45 needed. The OTHER variant (V1) achieves 60/60 with median
  margin .21 — the cap fix and the ordering fix live in different arms.
  Adjudicated as registered: MISS; the anti-correlation is the finding.

## PIVOT deliverable — the operating frontier (tau grid .025–.975)

`results/m4_d_bridge_hetero/bridge_hetero_tau_frontier.csv` (39 taus x 3
arms): designed-null false licenses, hetero sensitivity (license rate on
gt-reconstructable rows), hetero false-license rate. Key points:

| arm | tau .5 (registered): sens / het-FPR / null-FL | best null-safe tau: sens / het-FPR |
|---|---|---|
| baseline | .545 / .003 / 0-200 | tau .275: **.708** / .047 |
| V1 | .525 / .003 / 0-200 | tau .275: .542 / .043 |
| V2 | .120 / .000 / 0-200 | tau .275: .209 / .013 |

Documented operating curve: on this battery the BASELINE selector at a
lower tau dominates both one-step recalibrations for sensitivity at fixed
designed-null safety (every tau > .268 gives 0/200 across arms; .275 sits
.007 above the observed null max — a razor margin, disclosed). This
prospectively reproduces, on new families, Leg 2's recorded-but-not-
adopted Youden observation (tau ~.23–.28 operating region). The variants
buy specific repairs instead: V1 buys C2 un-capping (60/60), V2 buys
deep-noise ordering (anchor individual .995); neither buys tau-scale
license calibration.

## Honest anomalies

1. **V1 underperforms the baseline it was meant to fix** (.727 < .837
   pooled). Cause is structural: `max_u sqrt(sum_v s_uv^2)` is an edge
   UPPER bound dominated by the worst author row; with 2x selection it
   starves rank (h1_individual zero-rank rate .50 vs baseline .37) even
   though its variance model is excellent (model-vs-realized row power
   Spearman .975 at sigma 1.5).
2. **V2's index-scale collapse**: label-1 hetero median index .097 vs
   baseline .537 — under-floored ranks (mean 3.78 on h2_individual vs
   oracle 3) drag the spectral margin down, so ordering survives while
   every fixed tau starves sensitivity. The within-row permutation null
   misses variance ALIGNMENT (H1: noise co-located with large distances;
   H2: row x col factor concentration; C2: PSD mean shift) — all three
   registered mechanisms defeat it in the same direction, an informative
   consistency.
3. The identical designed-null max index (.2680) across arms is benign:
   one clean group_only world where all floors agree on the rank; probe
   seeds are shared by construction.
4. h2_mixed AUC ~.52–.58 in ALL arms: that cell (eps .2, noise .2, 20% of
   labels positive at knife-edge E-ratios) is a label-margin artifact
   inherited from Leg 2's mixed-cell geometry, not a selector property.
5. Lean (a)'s pooled statistic hides that baseline PER-FAMILY ordering
   stays strong under H1/H2; the pooled number is dragged by cross-family
   index-scale mixing. Registered bar adjudicated as registered; the
   decomposition is reported alongside.
6. Wall-clock anomaly: none — 157 s total, no world failed, no NaNs; all
   4320 rows persisted.

## Boundary

EXPLORATORY tier; synthetic planted worlds only; no natural text, no
personality claim; no prospective seal. The frontier is the bridge's
documented operating curve for heteroscedastic fields; tau = .5 remains
the registered license and is NOT retuned here (the .275 point is
recorded, not adopted). Next-step candidates for the standing queue (not
registered here): a debiased C2 floor via cross-half Gram (targets the PSD
mean shift both variants miss), and a margin-preserving hybrid (V1 floor
for rank, V2 quantile for licensing scale).

## Artifacts

- `suica_core/m4_relation_bridge.py` (additive: `noise_floor_override`,
  `replicate_noise_sd_model`, `variance_weighted_floor`,
  `permutation_floor`, `heteroscedastic_relation_world`, selector arms in
  `rigidity_report`)
- `scripts/run_suica_m4_d_bridge_hetero_leg13.py`
- `results/m4_d_bridge_hetero/bridge_hetero_rows.csv` (4320 rows)
- `results/m4_d_bridge_hetero/bridge_hetero_tau_frontier.csv`
- `results/m4_d_bridge_hetero/decision.json`
- `tests/test_m4_bridge_hetero.py` (11 tests; leg-2's 9 untouched and
  passing; suite collection intact, 970 tests collected)
