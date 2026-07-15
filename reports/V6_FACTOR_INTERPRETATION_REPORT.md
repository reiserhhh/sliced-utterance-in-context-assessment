# SUICA V6 Factor Interpretation Audit

## Question and decision

This audit asks whether information visible in Static, Dynamic, both blocks, or
neither accepted factor space can be interpreted without forcing every signal
into a named personality axis. The run used 1,540,040 PANDORA comments, sampled
597,933 comments from 3,213 authors, and held 1,640 authors out from discovery.
No personality labels or frozen SUICA constructs entered discovery.

**Decision:** no discrete factor family is transportable enough to name as a
psychological construct. Nevertheless, three distributed same-author signatures
are statistically detectable. Factor rejection and signal absence are therefore
not equivalent.

## Two-axis taxonomy

Every candidate must receive two separate labels:

1. `support_class`: `shared`, `static_dominant`, `dynamic_dominant`, or `residual`.
2. `source_class`: `author_level`, `condition_proxy`, `opportunity_response`,
   `state`, or `error_or_unidentified`.

`static_only` and `dynamic_only` are prohibited until the other block passes a
predefined equivalence test. The previous response object `B_u` is an
author-by-opportunity source, not the same thing as a score shared between Static
and Dynamic blocks.

## Empirical separation

| Object | Identity result, author bootstrap 95% CI | Effective rank | Interpretation license |
|---|---:|---:|---|
| Static accepted-factor projection | AUC .695 [.679, .707] | 7 projected axes | Stable author information, but axes do not transport |
| Static post-factor residual | AUC .614 [.603, .625] | 12.92 | High-dimensional distributed author signature |
| Opportunity-response factors | AUC .510 [.495, .523] | 2 axes | No reliable discrete response factor |
| Opportunity-response residual | AUC .523 [.511, .537] | 17.69 | Weak diffuse signal or unmodelled opportunity; unresolved |
| Dynamic factors | AUC .514 [.492, .536] | 4 axes | No reliable discrete motion factor |
| Dynamic full/residual space | .529 [.512, .547] / .528 [.513, .545] | residual 4.08 | Weak distributed motion signature |
| Static-dynamic shared scores | AUC .585 [.569, .605] | 3 discovery axes | Distributed cross-block author configuration; axes fail transport |

The AUCs use 20 deranged stranger matchings and 100 author bootstraps. They test
same-author discrimination, not clinical validity or personality prediction.

## What can be operationally explained

### Static-dominant configurations

The seven discovery axes are combinations of function words, pronouns,
acknowledgements, tense/deixis, questions, and link/register usage. Tentative
descriptions include second-person address, gratitude/acknowledgement register,
interrogative stance, personal versus impersonal reference, and temporal/narrative
register. These are valid descriptions of loadings, but none is a confirmed
construct: early/late reliabilities range only .215-.480 and every axis fails the
full transport gate. Some static signal may be author idiolect; some may be stable
topic/community choice or formatting opportunity.

### Dynamic-dominant mechanisms

The four discovery axes have clearer mathematical meanings than psychological
names:

- `dynamic_F1`: amplitude/variance regime with lag-2 persistence.
- `dynamic_F2`: change-point switching with secondary roughness.
- `dynamic_F3`: local roughness or abrupt trajectory movement.
- `dynamic_F4`: lagged persistence/oscillation mixed with variance and switching.

Their confirmation reliabilities are -0.023 to .086. They may encode motion that
only exists along a path, but current data do not support stable named factors.
Calling them emotion, flexibility, or personality would exceed the evidence.

### Shared static-dynamic configurations

The strongest discovery configuration links a second-person/address lexical
contrast to trajectory roughness and change points. Its cross-lag relation is
.148 and combined early/late reliability is .294 [.239,.357]. Two weaker
configurations link interrogative/copular or stance/deictic patterns to variance,
persistence, and switching. The combined shared-space AUC is non-chance, but the
static and dynamic subspaces reproduce poorly (.269 and .309), and no axis passes.
This licenses the statement that static expression and motion share distributed
author information, not that one named hybrid trait was discovered.

## What the residual means

The Static residual is not a rind to discard. Its AUC and effective rank show that
author information is spread over many weak directions not captured by the seven
rotated factors. Plausible sources are:

- distributed idiolect whose identity signal is rotation-invariant;
- nonlinear author manifolds that a linear factor catalog cannot aggregate;
- rare author-by-condition responses diluted by global factors;
- remaining social-niche, topic-choice, formatting, or opportunity structure;
- scorer/tokenization artifacts and ordinary error.

The matched-stranger screen narrows, but does not close, this question. Static
residual identity survives late-target opportunity/community sensitivity controls
(AUC .593 [.582,.602] in the weighted screen; .600 [.587,.611] at Jaccard >=.10,
79.5% coverage). Dynamic residual also survives a weaker community caliper
(.542 [.520,.563] at Jaccard >=.05, 99.4% coverage), whereas the discovered
dynamic-factor projection remains chance-like. Thus the best current label is
`unknown stable path candidate`, not a named dynamic factor.

However, an epoch x technical-replica feasibility audit finds only 9 authors who
can meet the registered two-run/twelve-transition criterion in all four replicas
across early and late halves. PANDORA therefore cannot distinguish persistent
state, author dynamics, and systematic scoring error at this resolution. The
current experiment rejects fully exchangeable iid noise, but not author-specific
systematic error, topic semantics, social role, tokenization artifacts, or a
long-lived state.

## Claim boundary and next falsification

The discovery supports a layered SUICA object: interpretable Static loading
patterns, mathematically interpretable Dynamic mechanisms, a distributed shared
configuration, and an unresolved residual identity field. It does not yet support
new personality-factor names.

The next no-new-label falsification should freeze this run and test residual source
classes in order: opportunity-matched stranger negatives; nonlinear residual
kernel/manifold recovery; leave-one-community-out identity; rare-condition
mixture recovery; scorer and token-window perturbations. A residual may enter a
future construct catalog only if it survives opportunity matching and corpus
transport. Otherwise it remains an author signature or condition proxy.
