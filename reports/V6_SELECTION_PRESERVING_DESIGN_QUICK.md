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

- profile: `quick`
- repetitions: `20` per world
- config SHA-256: `f7acb5b23d317d3e2ed19485719e9cc29c7f0a584b56f8a286fdb241b5cc9f0a`
- external labels, raw text, and real author identifiers: not used

## Results

| world | raw free level r | free condition-centred level r | fixed-condition level r | free B support | free B r | fixed B support | fixed B r | held-out selection log-score gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| selection-linked choice | 0.976 [0.972, 0.981] | 0.947 [0.935, 0.960] | 0.985 [0.973, 0.992] | 0.401 [0.299, 0.518] | 0.638 [0.567, 0.709] | 1.000 [1.000, 1.000] | 0.844 [0.825, 0.860] | 0.280 [0.235, 0.346] |
| condition-only nuisance | 0.945 [0.909, 0.966] | 0.983 [0.970, 0.990] | 0.986 [0.973, 0.991] | 0.938 [0.891, 0.983] | 0.831 [0.805, 0.852] | 1.000 [1.000, 1.000] | 0.842 [0.823, 0.858] | -0.069 [-0.094, -0.048] |

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
