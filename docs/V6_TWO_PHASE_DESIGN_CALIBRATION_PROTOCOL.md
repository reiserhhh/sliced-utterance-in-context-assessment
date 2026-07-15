# V6 Two-Phase Design Calibration Protocol

## Scope

This protocol calibrates the information budget of the two-phase V6 design in
a registered synthetic generator. It does not calculate a sample size for a
human study and it does not validate personality, state, clinical, or external
construct claims.

## Estimands

For a free phase, the target is an author's selected-condition distribution:

\[
\pi_u(c)=P(C_{ui}=c\mid u).
\]

For a balanced fixed phase, the target is the within-author conditional response
contrast:

\[
B_{u,c}=E(Y_{ui}\mid u,C_{ui}=c)-\frac{1}{K}\sum_{j=1}^{K}E(Y_{ui}\mid u,C_{ui}=j).
\]

They are deliberately not pooled into one score. The calibration reports
flattened recovery correlations \(R_\pi\) and \(R_B\) against simulation truth.

## Generator and split

The generator is the existing `EndogenousSelectionWorld`:

\[
C_{ui}\sim\operatorname{Categorical}\{\operatorname{softmax}(\lambda L a_u+\eta_u)\},
\quad Y_{ui}=a_u+\mu_{C_{ui}}+B_{u,C_{ui}}+\epsilon_{ui}.
\]

Condition references are learned from deterministic discovery authors only and
scored on disjoint confirmation authors. No labels or raw text are present.

## Grid and frozen decisions

The fixed grid varies condition breadth \(K\) and repeats per condition \(R\).
It records total fixed observations \(K R\), level recovery, response recovery,
and complete response support. The free grid varies free observations while
holding its condition count fixed and records choice-profile recovery, held-out
choice log-score gain, and accidental complete-condition support.

The full profile is qualified only when its lower 2.5% simulation quantile
meets all frozen thresholds in
`configs/sim_v6/two_phase_design_calibration_full.json`. Two selections are
reported:

1. the smallest numerically qualified fixed design;
2. the smallest qualified fixed design with predeclared condition breadth.

The second is not "better" in a general sense; it buys breadth at an observation
cost. The first is not sufficient for a rich response map merely because it
recovers a binary contrast numerically.

## Refusal boundaries

- Do not convert this output into a human sample size or a clinical protocol.
- Do not use the free-phase support rate to estimate `B_u`; free support reflects
  choices, not balanced excitation.
- Do not interpret condition-centering as universally beneficial or harmful.
- Any future human collection must pre-register the actual condition ontology,
  opportunities, prompt schedule, text-unit definition, and estimator before
  opening external outcomes.
