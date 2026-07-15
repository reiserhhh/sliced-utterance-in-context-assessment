# V6 Selection-Preserving Design Simulation

## Question

Can one statistical rule decide whether topic/situation selection should be
subtracted from an author's text? No. This planted-world audit tests the design
rule instead: free selection is a distinct author-conditioned object, while a
balanced fixed-condition phase is the object that identifies conditional
expression and response contrasts.

For free observations:

\[
C_{ui} \sim \operatorname{Categorical}\{\operatorname{softmax}(\lambda L a_u + \eta_u)\},\qquad
Y_{ui}=a_u+\mu_{C_{ui}}+B_{u,C_{ui}}+\epsilon_{ui}.
\]

When `lambda > 0`, the population free-condition mean contains
`E[a_u | C=c]`; subtracting it therefore changes the author-level estimand.
The fixed phase assigns every `C` independently and equally often, so it can
estimate condition contrasts without using selection-linked author variation as
a condition baseline.

## Frozen setup

- profile: `full`
- repetitions: `300` per world
- config SHA-256: `ba815081bd655182790673153d9e139f89c0c0a479d6e4912c8c6c8dad82c87a`
- external labels, raw text, and real author identifiers: not used

## Results

| world | raw free level r | free condition-centred level r | fixed-condition level r | free B support | free B r | fixed B support | fixed B r | held-out selection log-score gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| selection-linked choice | 0.978 [0.975, 0.981] | 0.960 [0.952, 0.966] | 0.991 [0.988, 0.994] | 0.539 [0.459, 0.622] | 0.686 [0.646, 0.723] | 1.000 [1.000, 1.000] | 0.878 [0.871, 0.884] | 0.316 [0.259, 0.364] |
| condition-only nuisance | 0.956 [0.934, 0.972] | 0.990 [0.987, 0.992] | 0.991 [0.988, 0.994] | 0.988 [0.969, 1.000] | 0.890 [0.882, 0.899] | 1.000 [1.000, 1.000] | 0.877 [0.870, 0.884] | -0.056 [-0.079, -0.033] |

## Gates

{
  "condition_only_centering_can_help": true,
  "fixed_phase_recovers_response": true,
  "free_phase_has_incomplete_response_support": true,
  "selection_channel_is_predictable": true,
  "selection_linked_centering_changes_level": true
}

## Licensed conclusion

The simulation supports only a **design theorem in its planted family**: selection,
conditional expression, and response contrast are different estimands. A free
collection phase is appropriate for estimating a selection profile; it is not a
substitute for a balanced fixed-condition phase when estimating an individual
response operator. Conversely, condition centering can help in a condition-only
world but may remove selection-linked author variation in an endogenous-choice
world. No result establishes a human trait, a named SUICA factor, a clinical
signal, or a universal rule about topic removal.
