# M4-C.3.2 Fisher-Wiener Confirmation Audit Note

## Frozen result

The sealed decision remains:

```text
M4_C32_NO_GO_FISHER_WIENER_CREATION
```

The main estimator produced a real but incomplete improvement:

- loop geometry: `.7198 -> .7699`;
- gain: `.0501`, repetition-cluster LCB `.0051`;
- creation geometry: `.7347 -> .8054`;
- oracle creation headroom: `.1974`, LCB `.1359`;
- recovered headroom: `.2537`;
- qualifying repetitions: `5/8`;
- held-out hazard-loss degradation: `1.30%`;
- split-half author-permutation gain: `-.4363`; and
- no-creation false success rate: `0`.

The gain, absolute geometry, predictive-risk, permutation, specificity, gauge,
and implementation gates passed. The predeclared 50% headroom-recovery and
`6/8` repetition gates failed, independently establishing the NO-GO.

## Audit finding 1: common-shift degeneracy

The common physical-creation shift has zero geometry error in every main
world and in two of three no-creation controls. In
`linear_exogenous_selection`, every Fisher creation estimate is identical, so
all author-pair distances are zero and Spearman geometry is undefined. The
generic helper returns zero geometry for a degenerate vector, which the
registered `abs(1-rho)` check converts to error `1`.

This is a control-definition failure at a zero-variance boundary, not evidence
that a common shift changes a nondegenerate author geometry. The frozen failed
check is retained and not rewritten.

## Audit finding 2: incompatible alias interfaces

Four refusal families were rejected in all `8/8` repetitions:

- hidden opportunity source alias;
- evaluation support shift;
- author provenance leakage; and
- response leakage.

`condition_alias_ecology` was not refused by the ordinary chart-estimator
interface. In M4-C.2 it is identified by a separate truth-open proper-loss
information-gap audit, not by `fit_m4_chart_ecology.refused`. Combining that
truth-open test with four observable refusal tests into one generic refusal
mean forced the observed rate to `4/5=.8`.

The frozen refusal check remains failed. Future protocols must route
noninjective condition aliases to their proper-loss audit rather than treating
them as an observable chart refusal.

## Scientific interpretation

The confirmation supports a partial estimation-noise mechanism:
cross-author split-half shrinkage improves both the creation edge and the
composite author-relation geometry without using the oracle endpoint, without
improving under author permutation, and without triggering no-creation worlds.
It does not support complete recovery at the current opportunity budget.

The remaining question is therefore whether the unrecovered headroom is an
information-budget limit or a structural chart-identification limit. Further
relation-kernel or embedding replacement is not justified.

## Artifact hashes

```text
8a31b5ad18a447a9143b5121ffab00c14759cefc63fa5dfbebe7564fb9cca532  results/m4_fisher_wiener_creation_confirmation/decision.json
75649de37c00fef3439ce71e7a04fed327bf41321f3664d7088add8638a40227  results/m4_fisher_wiener_creation_confirmation/metrics.csv
4d175eef2c4ae7fc00abb29aa040c548cb9fda6bbba0aa2ee93cfd5dadaa2434  results/m4_fisher_wiener_creation_confirmation/refusal_controls.csv
9ff0751859476a11ff08c95b074470095dd110dd1df09530e7a6dbcb5666a2a8  reports/SUICA_M4_FISHER_WIENER_CREATION_CONFIRMATION.md
```
