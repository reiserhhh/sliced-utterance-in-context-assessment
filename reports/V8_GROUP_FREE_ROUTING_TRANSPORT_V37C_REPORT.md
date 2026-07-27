# V8 Group-Free Routing Transport V3.7C Report

Decision: `V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_PASS`

Independent ruling: `PASS_WITH_CAVEATS`

## Question

V3.7C tested whether the V3.7A author-relative routing operator survives after
removing true-group centering, separating blind and oracle event panels,
transporting the locator beyond its exact construction family, and introducing
registered missingness.

The fitted object is a group-free, cross-session stable routing deviation

\[
\widehat D_u
=
\widehat P_r\left[
\operatorname{ilr}(\widehat\Pi_u^{Q_{\rm ref}})
-\operatorname{ilr}(\widehat\Pi_{\rm ref}^{Q_{\rm ref}})
\right],
\]

where \(\widehat P_r\) is a PSD cross-session spectral-Wiener operator selected
only on discovery populations. True groups are unavailable to fitting and
primary scoring.

## Integrity

- The canonical run used unseen seed `20361123`.
- The V3.7C content seal and both parent seal hashes passed before simulation.
- All 20 frozen gates passed.
- The artifact inventory passed `9/9`; the effective configuration equals the
  sealed configuration.
- The external full-stream audit found `608/608` unique root streams and
  `6960/6960` unique component seeds, with zero overlap against the `1800`
  pre-seal component seeds.

## Canonical results

| Arm | Truth r | Split reliability | Unseen-context reliability | Hard-neighbor AUC | Locator F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Core low-rank | .963 | .740 | .936 | .932 | .999 |
| 32-event budget | .526 | .263 | .363 | .691 | .999 |
| Group mixture | .961 | .750 | .946 | .997 | .999 |
| Out-of-family paths | .963 | .712 | .932 | .991 | .984 |
| High-noise paths | .963 | .712 | .934 | .991 | .962 |
| MAR plus AIPW | .958 | .830 | .931 | .985 | .999 |
| MNAR sensitivity arm | .956 | .818 | .928 | .984 | .999 |

Core operator correlation with an independently sampled oracle estimator was
`.935`. Blind predictive-gain retention was `.999` with a 95% bootstrap
interval `[.996, 1.001]`. The observationally isomorphic random-label control
remained at AUC `.50` and was refused in at least 97.5% of repetitions in all
formally checked arms.

Under registered MAR, AIPW excess NRMSE was `.021`, compared with `.103` for
available-case estimation. AIPW beat available-case in `80/80` paired
populations. Under registered MNAR, the sensitivity envelope covered `.919`
of scorer coordinates, but its mean width was `.941`; this is a broad
sensitivity analysis, not point identification.

## New theoretical result: recovery is not identification

The core arm cycled through true ranks 2, 4, 6, and 8:

| True rank | Truth r | Split reliability | Hard-neighbor AUC | Top-1 |
| ---: | ---: | ---: | ---: | ---: |
| 2 | .967 | .797 | .777 | .199 |
| 4 | .958 | .725 | .961 | .715 |
| 6 | .965 | .717 | .992 | .908 |
| 8 | .960 | .722 | .998 | .970 |

Operator recovery stayed near `.96` at every rank, while local identity
resolution changed sharply. Let

\[
\epsilon_u=\|\widehat D_u-D_u\|,\qquad
m_u=\min_{v\ne u}\|D_u-D_v\|.
\]

Small \(\epsilon_u\) is enough for structural recovery; stable identification
additionally needs an author margin such as \(2\epsilon_u<m_u\). Low-dimensional
author spaces can therefore be measured accurately while remaining crowded.
Measurement reliability, structural validity, and identity resolution are
separate properties.

## Supported claim

Within the registered synthetic families, a group-free low-rank estimator can
recover an author-relative routing operator from blind geometry-localized
events, preserve it on independent oracle-test panels, transport across the
specified path perturbations, and correct the registered MAR mechanism.

This does not establish personality, thought nodes, intelligence, clinical
meaning, real-text junctions, arbitrary missingness, or open-world event
localization.

## Artifacts

- `results/v8_group_free_routing_transport/v37c_final_20260726/decision.json`
- `results/v8_group_free_routing_transport/v37c_final_20260726/confirmation_metrics.csv`
- `configs/v8_group_free_routing_transport_v37c_seal.json`
- `reports/V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_EXTERNAL_SEED_AUDIT.json`
- `reports/V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_INDEPENDENT_AUDIT.md`
