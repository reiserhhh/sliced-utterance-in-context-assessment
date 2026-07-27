# SUICA M3 Micro-to-Meso Mechanism Atlas

Status: discovery theory after a synthetic `PASS`; not sealed confirmation and
not a human-text or personality claim.

Overall decision:
`M3_INTERMEDIATE_MECHANISM_ATLAS_DISCOVERY_SUPPORTED`.

## 1. Why an intermediate layer is necessary

The earlier M3 notation allowed the microscopic event law to be projected
directly into an author response field. That is mathematically valid as a
projection, but it leaves the substantive coarse-graining mechanism
unspecified. The new working object is an atlas rather than a single bridge:

\[
\mathcal A_u
=
\left(
\mu_u,\,
\mathcal R_u,\,
\mathcal K_u,\,
\mathcal C_u,\,
\mathcal P_u
\right).
\]

- \(\mu_u\): distribution of expressed states under a declared opportunity
  measure;
- \(\mathcal R_u\): condition-to-response operator;
- \(\mathcal K_u\): temporal evolution operator and its slow modes;
- \(\mathcal C_u\): response to another actor or interactional input;
- \(\mathcal P_u\): higher-order path information not contained in a
  first-order transition.

These are competing or coexisting coarse-grainings. They are not five
mandatory modules to concatenate, and none is licensed as personality without
human-text persistence and external psychological or behavioral anchoring.

## 2. Interdisciplinary foundations

### Psychology

Fleeson's density-distribution account treats a trait-relevant behavioral
profile as a distribution of states, including central tendency and
variability rather than one observation
([Fleeson, 2001](https://doi.org/10.1037/0022-3514.80.6.1011)).
Whole Trait Theory subsequently separates descriptive state distributions
from explanatory mechanisms
([Fleeson & Jayawickreme, 2015](https://doi.org/10.1016/j.jrp.2014.10.009)).
This supports \(\mu_u\), but does not imply that any text-vector distribution
is a personality trait.

CAPS describes stable person information as situation-behavior `if-then`
patterns rather than context-free behavior
([Mischel & Shoda, 1995](https://doi.org/10.1037/0033-295X.102.2.246)).
This is the closest psychological precedent for \(\mathcal R_u\). It also
implies that opportunity must be fixed or explicitly modeled; otherwise
condition selection and conditional response are not identifiable.

Idiographic psychology warns that between-person structure and within-person
dynamics are not interchangeable unless restrictive ergodic conditions hold
([Molenaar, 2004](https://doi.org/10.1207/s15366359mea0204_1)).
Dynamic structural equation modeling similarly separates within-person lagged
effects, between-person differences, and random effects
([Asparouhov, Hamaker, & Muthen, 2018](https://www.statmodel.com/download/DSEM.pdf)).

### Linguistics and sociology

Interactive alignment and communication accommodation show that an utterance
is partly a response to the interlocutor, at multiple representational levels
([Pickering & Garrod, 2004](https://doi.org/10.1017/S0140525X04000056);
[Danescu-Niculescu-Mizil et al., 2011](https://doi.org/10.1145/1963405.1963509)).
Consequently, stable coupling or resistance to partner input belongs to
\(\mathcal C_u\), while the partner's style itself is a condition.

Relational-event models treat social action as ordered events whose hazard
depends on recency, persistence, participation shifts, and network history
([Butts, 2008](https://doi.org/10.1111/j.1467-9531.2008.00203.x)).
This supports a separate event-history mechanism rather than reducing
interaction to author means.

### Mathematics and statistics

Kernel mean embeddings represent probability distributions as elements of an
RKHS and permit nonparametric comparison of marginal and conditional laws
([Muandet et al., 2017](https://doi.org/10.1561/2200000060)).
They motivate the current distribution summary and a future conditional-law
operator beyond linear regression.

Koopman theory studies nonlinear dynamics through a linear operator acting on
observables. Extended dynamic mode decomposition estimates finite
approximations to that operator
([Williams, Kevrekidis, & Rowley, 2015](https://doi.org/10.1007/s00332-015-9258-5)).
The present experiment estimates only a low-order linear lag operator; the
name `koopman_spectrum` is therefore an engineering label, not evidence that a
nonlinear Koopman-invariant subspace has been recovered.

Path signatures encode ordered path geometry through iterated integrals and
can retain information absent from unordered summaries
([Chevyrev & Kormilitzin, 2016](https://arxiv.org/abs/1603.03788)).
The current `higher_order_path` estimator is only a lag-two memory residual,
not a full path signature.

## 3. Discovery experiment

The atlas generates independent train/test event panels for the same authors.
Each positive world isolates one mechanism while suppressing simpler author
means where possible:

| World | Planted object | Registered estimator |
| --- | --- | --- |
| density | symmetric mixture weight | residual-response kernel mean |
| conditional | author rotation of condition input | condition-response slope |
| metastable | author persistence | lag-one operator spectrum |
| interaction | author rotation of partner input | partner-response slope |
| higher order | lag-two persistence with null lag-one dependence | lag-two memory spectrum |
| opportunity | author condition exposure only | condition profile |
| null | no author law | all methods should be chance |

The primary score is cross-panel same-author AUC. Pairwise-distance Spearman
correlation checks whether the recovered author geometry matches the planted
parameter without requiring coordinate alignment. A mechanism is selective
only when its registered estimator wins the matching world and the null and
opportunity controls remain calibrated.

## 4. Discovery result

At 96 events per occasion and 10 independent seeds:

| Mechanism | AUC | Truth-geometry rho | Win fraction |
| --- | ---: | ---: | ---: |
| state distribution | 0.759 | 0.789 | 1.00 |
| conditional response | 0.940 | 0.830 | 1.00 |
| lag-one persistence | 0.632 | 0.461 | 0.90 |
| interactional coupling | 0.938 | 0.831 | 1.00 |
| lag-two memory | 0.679 | 0.616 | 1.00 |

The null maximum mean AUC is 0.506. Opportunity profile AUC is 0.839. After
removing regression intercepts from operator features, the largest
opportunity-only response-residual AUC is 0.516. This correction matters:
including the intercept had allowed condition exposure to masquerade as an
interaction coefficient.

## 5. Licensed conclusion

The synthetic result establishes an existence proof for a mechanism-selection
layer between event vectors and author geometry:

\[
\mathcal N_u
\xrightarrow{\text{candidate coarse-graining}}
\mathcal A_u^{(m)}
\xrightarrow{\text{independent-view audit}}
\widehat{\mathcal A}_u^{(m)}.
\]

It shows that an author can be stable for different mathematical reasons:
distribution shape, conditional response, temporal persistence,
interactional coupling, or higher-order memory. It also shows that opportunity
exposure is a separately measurable author-associated object and must not be
silently absorbed into a response operator.

It does not establish that these mechanisms exist in human text, are
psychological constructs, form a complete basis, or are identifiable from
uncontrolled corpora.

## 6. Remaining attacks

1. **Pure distribution shape**: hold both mean and covariance fixed while
   varying modality or tails. The current density world can be partly solved
   by covariance.
2. **Nonlinear slow modes**: keep simple lag-one statistics matched and vary
   hidden metastable dynamics. Use EDMD/VAMP dictionaries selected on train
   data and test implied timescales.
3. **Exact path aliases**: match occupancy and the complete first-order edge
   multiset, then vary triadic motifs, loops, or path signature.
4. **Dyadic identifiability**: add multiple partners and separate actor,
   partner, dyad, and occasion effects. A single partner-input stream is not a
   Social Relations Model.
5. **Composite decomposition**: a high union AUC only proves useful combined
   representation. It does not prove that the planted mechanisms can be
   independently recovered when superposed.
6. **Actual data attacks**: inject MNAR, technical dependence, reference
   drift, mixed coarsening, and support failure as value-generating processes,
   not metadata flags.

## 7. Follow-up discoveries

The low-order-matched V2A attack retained only three of five mechanisms:
nonlinear condition response, AR(2) dynamics beyond matched lag one, and
nonlinear partner response. The original single-bandwidth KME failed the
equal-covariance shape world, and the generic lag-three spectrum failed pure
lag-three memory.

V2B replaced those two summaries with an author-whitened multiscale empirical
characteristic function and a lag-three partial operator. All five
low-order-matched attacks then passed. V3 independently permuted all five
author parameters, ran every pairwise superposition, and removed each
mechanism counterfactually. Own-truth partial geometry remained high,
cross-talk stayed low, and knockout geometry returned near zero.

The complete numerical record and the stricter claim boundary are in
`reports/SUICA_M3_MECHANISM_ATLAS_SYNTHESIS.md`. These follow-ups remain
matched-family discovery: they establish recoverability and pairwise
decomposability under known mechanism classes, not universal mechanism
discovery.

## 8. Formal discovery object

The current finite discovery object is:

\[
\mathfrak M_u^{\mathrm{disc}}
=
\Delta_{P_0}\left[
D_u^\Omega
\oplus R_u^{\mathcal B}
\oplus K_u^{(2)}
\oplus C_u^{\mathcal B}
\oplus P_{u,3\mid1:2}
\right].
\]

The components are deliberately narrow:

\[
D_u^\Omega
=
\left\{
\Re\varphi_u^\circ(\omega),
\Im\varphi_u^\circ(\omega)
\right\}_{\omega\in\Omega},
\qquad
\varphi_u^\circ(\omega)
=
\mathbb E[
\exp(i\omega^\top W_u(X-\mu_u))
],
\]

\[
R_u^{\mathcal B}
=
\Pi_{\mathcal B_{\mathrm{NL}}}
\mathbb E[X\mid Z,u],
\qquad
C_u^{\mathcal B}
=
\Pi_{\mathcal B_{\mathrm{NL}}}
\mathbb E[X\mid P,u],
\]

\[
K_u^{(2)}
=
\operatorname{spec}
\begin{pmatrix}
A_{u,1} & A_{u,2}\\
I & 0
\end{pmatrix},
\]

\[
P_{u,3\mid1:2}
=
\arg\min_{A_3}
\mathbb E\left\|
X_t-A_1X_{t-1}-A_2X_{t-2}-A_3X_{t-3}
\right\|^2.
\]

These are finite projections chosen for discovery. They must not be renamed
as a complete distribution, general Koopman operator, full interaction
mechanism, or general path signature until cross-family confirmation passes.
