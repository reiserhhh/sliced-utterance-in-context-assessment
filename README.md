# Sliced Utterance In-Context Assessment (SUICA)

**English** | [日本語](README.ja.md) | [简体中文](README.zh.md)

SUICA is a text-behavior measurement framework: it treats a person's
spontaneous writing as many small behavioral observations ("sliced
utterances") measured inside their naturally occurring contexts, and builds
auditable, reference-relative coordinates from them — a methodological
foundation for future text-based assessment between questionnaires and
free-response methods, not a completed personality scale.

*Suica (スイカ) is Japanese for watermelon: the method's core "rind model"
holds that topic/situation is not noise to strip away but the rind that
carries person signal through self-selection — a claim this project first
falsified in its naive form (statistical condition-centering destroys
signal) and then rebuilt as a design principle (control context by design;
measure choice as a channel).*

## What is in the latest sealed release (v0.2.1)

- **V7 technical core** — operator-indexed relative text geometry, frozen
  geometry bundles, refusal rules, multiview calibration, uncertainty and
  future-data gates. The highest supported claim is
  `OPERATOR_INDEXED_RELATIVE_TEXT_GEOMETRY_WITHIN_DECLARED_DOMAIN`; it is not a
  personality, reliability, clinical, universal-language, or market claim.
- **Method** — `docs/THEORY.md` (rind model, three channels: choice / style /
  react), `docs/RULEBOOK.md` (binding experiment-design rules, each traced to
  measured evidence), `docs/VALIDATION_PLAN.md` (the P0-P5 falsification
  framework).
- **Worked example** — `docs/WORKED_EXAMPLE_MANUAL.md`: the complete,
  audited construction of a 19-construct battery + 12 choice axes on PANDORA
  (Reddit), with development-tier anchor performance (e.g., MBTI
  thinking-feeling ridge CV r = 0.346; Essays Big5 transport mean r ~ 0.144
  from 19 interpretable scores) and score-interpretation rules.
- **Audit trail** — `docs/CLAIMS_LEDGER.md`: every claim with status, seven
  adversarial audit rounds, retractions included. The ledger is the
  authoritative record; prose may not exceed ledger status.
- **AI operating standard** — `docs/AI_ANALYST_GUIDE.md`: role separation
  (scorer/builder/coder/auditor/interpreter/human), fixed prompts, guardrails
  G1-G11 (each traceable to a caught failure).
- **Sealed preregistration** — `docs/PREREGISTRATION.md`: the seal is the
  initial commit hash of this repository. **Opening #1 was performed on
  2026-07-07** under the frozen rules (commit-pinned script, adversarial
  pre-audit): the preregistered success rule **FAILED** (2/7 hypotheses at
  BH-FDR q<.05; the rule required >=4/7) — recorded in full in
  `reports/suica_lockbox_opening_1.md`. H2 (first-person -> Neuroticism,
  r=+0.111, q=.002) and H6 (politics/news choice -> Openness, r=+0.096,
  q=.006) confirmed at lockbox tier. One opening remains; the Essays
  confirm-half labels are still untouched.
- **Code** — `suica_core/` + `suica_sim/` + `scripts/` + `tests/`. The V7
  release lockbox is independently verifiable without restricted corpora.

## Quickstart (no data required)

```bash
pip install -r requirements.txt
python -m pytest -q tests/test_suica.py          # 39 passed
python -m pytest -q -p no:cacheprovider          # release audit: 302 passed
python scripts/verify_suica_v021_lockbox.py       # portable v0.2.1 seal
python scripts/run_suica_synthetic_ground_truth_v2.py   # P0: estimator
python scripts/run_suica_p0b_thin_cell_regime_v3.py     # P0-B: thin cells
```

These synthetic harnesses verify the entire estimator layer against planted
ground truth without any real data. To reproduce the worked example, obtain
the datasets per `docs/DATA_ACCESS.md` (this release ships no user text, no
user IDs; SHA-256 manifests allow byte-identical preparation checks).

## Honest summary of evidence status

Confirmed at held-out grade (T3): choice-axis stability (5/5 axes,
shrinkage 0.027), 15/15 discovered constructs on unseen users, react
signatures for 2 constructs under the stranger null. Falsified and retired:
condition-mean centering (three independent ways), affect word-rates as
trait or occasion-state measures, attention-weight interpretation as
measurement evidence. Confirmatory (T4, lockbox opening #1, 2026-07-07):
the preregistered success rule FAILED (2/7; recorded in full, no
re-analysis) — first-person -> Neuroticism (r=+0.111) and politics/news
choice -> Openness (r=+0.096) are the two lockbox-confirmed relations;
tension, novelty, directive, venue entropy and gaming choice did not
confirm. One opening remains sealed. Scope: English, one platform + student
essays; dialogue and clinical use are designed but untested (OPEN_PROBLEMS
OP-7/8/14 — OP-7a register-proxy and OP-8 stage 1 closed 2026-07-07, see
CLAIMS_LEDGER).

V6 raw-text factor rediscovery (2026-07-13) did **not** promote a new factor
inventory. A discovery-only, label-free 24-dimensional text basis retained
distributed author information after opportunity control (Static
own-vs-stranger AUC 0.691), but Static, Hybrid, and Dynamic factor spaces all
failed author-disjoint confirmation. This is recorded as a boundary result,
not converted into post-hoc named constructs; see
`reports/V6_FACTOR_DISCOVERY_REPORT.md`.

V6 nonlinear-path audit (2026-07-14): a phase-coupled synthetic world proves
that linear mean/covariance/lag summaries need not exhaust path information;
however, neither the degree-two/three path-signature screen nor a held-out RFF
conditional-transition embedding detected an order-stable signal in unseen
PANDORA authors. The nonlinear object is therefore a validated **theoretical
candidate**, not a detected human-text construct. See
`docs/V6_NONLINEAR_PATH_OBJECTS.md`.

V7.2 operator-indexed multiview audit (2026-07-15): fixed cross-comment
slicing did not show a robust universal precision advantage, so slicing is
retained as one observation view rather than promoted as a universal best
operator. On a fresh 600-author, label-free condition/opportunity audit, total
source-disjoint author geometry (AUC .916 [.890, .938]), observed context
selection recurrence, and a **within-stratum exchangeable** matched partial
screen (AUC .834 [.766, .896], 86/109 retained authors) reproduced. The
matched screen’s selected Jaccard caliper was 0.0, so it is conditional on
metadata balance rather than proof of literal same-topic equivalence. The
recorded primary subreddit/time surface itself explained only R2=.0045
[.00024, .00768] and did not robustly transport to the total configuration.
This is evidence for operator-indexed author-relative text geometry with
unresolved condition accounting, **not** a personality factor, causal context
effect, or clinical score. See
`docs/V7_OPERATOR_INDEXED_MULTIVIEW_V71.md` and
`reports/V7_CONDITION_OPPORTUNITY.md`.

V7.2 registered operator family (2026-07-15): on 240 new authors excluding
all 1,020 earlier V7 authors, five operators and word/char representations
showed same-source transport in a synchronized max-T family. The decisive
boundary is source-disjoint replication: fine-grained linear coordinate maps
did not transport, but source-disjoint own-vs-stranger position alignment did
(AUC .719--.805; 48-comment sensitivity .791--.862). SUICA therefore has
evidence for reproducible **relative text geometry**, not fixed named axes or
personality measurement. See `reports/V7_OPERATOR_FAMILY.md`.

V7.3 theoretical closure audit (2026-07-15): the primary object is no longer
an unidentified factor coordinate. It is a frozen, identifier-free landmark
distance profile under an operator- and reference-indexed regularized
Mahalanobis geometry. A real held-out smoke scored 98.6% of discovery, 92.2%
of calibration, and 79.2% of confirmation authors; out-of-reference rows are
explicit radial-envelope refusals, not a general OOD diagnosis. Corrected W2 simulations separate nonlinear geometry from
linear coordinates, W3 uses 25 random partitions, W4 uses split-specific null
spectra and paired method-difference intervals, and W7 proves that unpaired
cross-domain coordinates are not identified. All six corrected evidence
bundles passed their original run-manifest/inventory audit and are distributed
as deidentified aggregate snapshots with source hashes. Version 0.2.1 seals
`V7_THEORETICAL_CORE_CLOSED_WITH_EMPIRICAL_GATES`. Reliability, external
construct validity, and paired cross-domain transport remain separate
future-data gates. See `reports/V7_THEORY_CLOSURE_AUDIT.md`,
`docs/V7_EVIDENCE_STATUS_LATTICE.md`, and `docs/V7_LOCKBOX_V020.md`.

## V8 development line

V8 development has started on `main` after the sealed `v0.2.1` remediation
release. Its target is an **LLM-native, evidence-carrying assessment
framework**, not direct LLM personality judgment. A frozen LLM may become an
observation-level semantic transducer, while deterministic code remains the
final aggregator. Human-readable explanations must bind to numerical
artifacts, positive and counterevidence, counterfactual tests, support status,
joint uncertainty, and an explicit claim license. Adaptation agents may
propose new versioned candidates but cannot mutate or validate the active
instrument.

The authoritative integration map for the complete V8 mathematical line,
including V3.7G/H, the H.4D/R2 residual-completion sequence, and M3, is
`docs/V8_MATHEMATICAL_RESEARCH_ROUTE.md`. It distinguishes opened development,
sealed confirmation, real-text technical evidence, psychological construct
validity, and clinical use. The current integrated status is
`V8_TECHNICAL_MATHEMATICAL_FRAMEWORK_INTEGRATED__M3_V4_AWAITING_CLEAN_SEAL__HUMAN_CONSTRUCT_VALIDITY_OPEN`.

M3-V4 mathematical development (2026-07-28) has reached
`M3_CROSS_FAMILY_V4_READY_FOR_CLEAN_SEAL`. A generator-blind battery recovered
author-dependent distribution, nonlinear response-operator, renewal-hazard,
time-reversal-current, and nonlinear-dynamics objects across a 12-seed
synthetic preflight while low-order controls, target knockouts, exact
observational aliases, and null worlds remained controlled. This is a
development-power result only: the 32-repeat external-randomness confirmation
is not sealed or opened, and it makes no human-text or psychological claim.
See `docs/SUICA_M3_CROSS_FAMILY_CONFIRMATION_PROTOCOL_V4.md` and
`reports/SUICA_M3_CROSS_FAMILY_PREFLIGHT_V4.md`.

The current mathematical measurement object is formalized in
`docs/V8_CONDITIONAL_RESPONSE_GEOMETRY_THEORY.md`. It separates C1 opportunity
selection, C2 shared-condition response, population hierarchy/topology,
stable residual structure, uncertainty, and evidence. Anonymous technical
objects are not personality constructs until a later external-validity
mapping is supported.

The initial V8.0 theory and executable refusal contract are documented in
`docs/V8_LLM_NATIVE_ASSESSMENT_THEORY.md` and
`docs/V8_EXECUTION_PLAN.md`. This is a technical development scaffold; it
adds no personality, state, reliability, clinical, or external-validity
result. The dev3 contract binds the prompt, semantic event schema,
deterministic aggregator, active/candidate manifests, promotion ledger, and
auditor attestation to verified hashes and an external active-bundle trust
root. Auditor, language-license, evidence-ledger, and clinical-signoff
artifacts require Ed25519 verification against a caller-supplied authority
registry, with signatures scoped to the exact contract, bundle, evidence root,
certificate, and claims they authorize. Its explanation certificate uses
typed evidence nodes, closed provenance links, paired counterfactual tests,
controlled language templates, and artifact-bound evidence licenses.
The V8.0 scaffold passed its independent adversarial contract audit; this
closes the technical boundary only and does not establish psychological or
clinical validity.

The full currently executable V8.1-V8.4 battery was completed on 2026-07-24.
The overall decision is `V8_TECHNICAL_CORE_NOT_CLOSED`. V8.2 explanation
fidelity and V8.3 planted-world component identification passed. V8.1 achieved
200/200 valid outputs, macro-F1 0.9981, minimum ICC 0.9734, and cross
prompt/model CKA 0.9992, but failed the frozen run-drift gate
(0.1196 > 0.10), so the LLM remains renderer-only. In V8.4, the semantic
channel did not improve frozen PANDORA V7 geometry
(\(\Delta\)AUC=-0.0368, 95% CI [-0.1658, 0.0895]) and all four real-text run
CKAs were below 0.70. MEPS showed a local +0.1061 AUC increment
[0.0076, 0.2273], but its run CKA was only 0.5534 and the result is not
promoted. See `reports/V8_FULL_TECHNICAL_EXPERIMENT_REPORT.md` and
`reports/V8_FULL_PROVENANCE_AUDIT.md`; the provenance audit passed 70/70
checks. See also `docs/V8_EXECUTION_PLAN.md`. V8.5 human repeated-measurement
and external construct validation were not run.

A subsequent constrained-interpreter experiment implemented the corrected
role split in which SUICA is the sole numerical channel and the LLM only
observes explicit behavior, renders compiled evidence-bound atoms, and audits
them. The 200-profile planted formal gate passed (observer macro-F1 0.943,
Fleiss kappa 0.988, interpretation coverage 0.988, evidence-edge F1 lower
bound 0.967). PANDORA runtime and repeated-input checks also passed, but the
formal real-text decision remained `V8_INTERPRETER_RENDERER_ONLY`: all 14
discovery links collapsed to `novelty_expression`, only 3/80 held-out
half-profiles had candidates, same-author AUC was 0.500, and neighbor AUC was
0.525. The interpreter exactly passed through the deterministic candidate set,
so it added no demonstrated selection information. Secondary corpora were
stopped after the primary gate failed. See
`reports/V8_INTERPRETER_STABILITY_REPORT.md`.

The next label-free method audit localized an upstream geometry bottleneck.
The frozen sorted landmark-distance profile had effective rank 1.446 and
discarded which structurally distinct landmark generated each distance. A
permutation- and Euclidean-isometry-invariant canonical coordinate was built
from intrinsic landmark-distance fingerprints; all 16 current landmarks had
unique fingerprints. Its scale-residual form reached source-disjoint
same-author cosine AUC 0.774, with author-cluster estimate 0.796
[0.687, 0.886], versus 0.498 for sorted distances. The paired delta was
+0.280 [0.154, 0.387], scale-matched AUC was 0.754, and topology-coupling
shuffle reduced AUC by 0.271 to 0.503. This is an opened-panel exploratory
mechanism result, not a personality or clinical-validity result. A fresh
registered author panel is required before changing the frozen V7 geometry or
reconnecting the behavior interpreter. See
`reports/V8_CANONICAL_ORBIT_GEOMETRY_REPORT.md`.

That fresh internal gate has now been run. All 240 V7 eligible authors were
excluded before deterministic sampling from the PANDORA raw-comment pool.
Among 156 source-eligible authors, 89 passed frozen geometry support.
Canonical scale-residual cosine AUC was 0.691, with author-cluster estimate
0.689 [0.636, 0.740] and permutation p=0.00010; sorted distance was 0.497.
The paired gain was +0.190 [0.118, 0.261], the gain over spectral energy was
+0.109 [0.056, 0.161], and topology shuffling removed 0.190 AUC. Decision:
`V8_CANONICAL_SCALE_RESIDUAL_INTERNAL_FRESH_PASS`. This confirms the
author-geometry mechanism within PANDORA; it still does not establish a
personality construct, cross-corpus transport, or clinical validity. The next
bounded step is to reconnect this frozen geometry to the existing behavior
cache without new LLM calls.

That reconnection is complete. Canonical geometry self-author AUC was 0.735,
but the unchanged three-segment/six-event behavior view remained at 0.556.
Cross-modal AUC was 0.547 [0.447, 0.616], distance alignment was 0.143
(p=0.073), and no stable registered links survived. Decision:
`V8_CANONICAL_GEOMETRY_PASS_BEHAVIOR_VIEW_STOP`. The geometry mechanism is no
longer the active bottleneck; the current explicit behavior object is. Prompt
or renderer tuning is not justified. See
`reports/V8_CANONICAL_BEHAVIOR_BRIDGE_REPORT.md`.

The behavior bottleneck has now been decomposed. A 24-author,
12-comment-per-half high-resolution observer pilot achieved repeated atomic
event macro-F1 0.849, but the preregistered condition-residual object failed
(AUC 0.385 at twelve comments). No-call diagnostics showed that strict
observer intersection and sparse exact-subreddit residualization removed the
stable author structure. A deterministic five-family hierarchy over the same
explicit evidence reached opened-panel AUC 0.699 [0.554, 0.798], p=0.0010;
the two observer repetitions were 0.669/0.683 and cross-model macro-F1 was
0.771. Its nested 3/6/9/12-comment curve rose
0.589/0.639/0.679/0.699.

Decision:
`V8_BEHAVIOR_V21_CANDIDATE_FROZEN_CONDITION_UNRESOLVED`. The result supports
a technical author-relative choice-and-expression candidate, not personality,
emotion, diagnosis, or condition-invariant response. Human coding and a fresh
author panel are required before any geometry bridge. See
`reports/V8_BEHAVIOR_V21_CANDIDATE_REPORT.md`.

The next gate is executable without more model calls. Its blind human-coding
packet contains 48 training, 336 natural-prevalence, and 192
boundary-enriched segments; each coder receives 528 opaque items, and 192
segments have hidden independent-model predictions for audit. The evaluator
has explicit waiting, adjudication, pass, and stop states and cannot calculate
observer accuracy from blank files. Fresh-author and C1/C2 thresholds are
frozen in `configs/v8_behavior_v21_fresh_protocol.json`. Human coding has not
yet been performed, so the scientific result remains the opened technical
candidate. See `docs/V8_BEHAVIOR_V21_HUMAN_AND_FRESH_PROTOCOL.md`.

A no-call fresh-panel preflight also passed the author/thread support gate:
300/300 scanned candidates supported two `link_id`-disjoint 32-comment
halves, and 190 authors were frozen as 60/20/80/30
discovery/calibration/confirmation/reserve. However, exact-condition C2 is not
identifiable in Reddit: only five supported subreddits covered 15.8% of
discovery segments, and confirmation structural completeness under those
shared conditions was 0%. The fresh run may therefore test only the joint/C1
object after human coding; C2 requires fixed-condition material. See
`reports/V8_BEHAVIOR_V21_FRESH_PREFLIGHT_REPORT.md`.

The available 46-person MEPS material was also audited without reading raw
text. It has three shared prompts and exactly three direct-answer slots per
participant/condition, but no independent repeat of a condition. Zero
participants meet the six-opportunity minimum across all prompts; only 2/46
meet six AI-chat turns across all prompts. MEPS is therefore an ontology and
procedure pilot only, not C2 confirmation. See
`reports/V8_BEHAVIOR_V21_MEPS_C2_SUPPORT_AUDIT.md`.

The C2 estimator itself has now passed an independent final planted-world
battery: `V8_BEHAVIOR_C2_PLANTED_WORLD_PASS` (70/70 registered checks).
The frozen binary score used exactly six observations per condition and
excluded author-specific standard errors. At SNR 0.50 it achieved same-author
AUC 0.951, while the separate Firth link-scale inference track recovered the
planted operator with median cosine 0.843, author-distance Spearman 0.660,
recovery slope 0.993, analytic CI coverage 0.968, and bootstrap-t coverage
0.904. C1-only information remained null on the C2 score (AUC 0.499), and
unshared, insufficient, or inconsistent condition coordinates refused
output. This is a technical identification result only; human observer
accuracy and real fixed-condition C2 remain open. See
`reports/V8_BEHAVIOR_C2_PLANTED_WORLD_REPORT.md`.

A further hierarchical limit experiment tested whether apparent author
structure survives when within-group individuality tends to zero:

\[
B_u=B_0+G_{k(u)}+\varepsilon D_u.
\]

All registered core checks passed. In the group-only world, ordinary
same-author AUC remained 0.864 but within-group same-author AUC was 0.500,
proving that ordinary author matching can be entirely explained by group
membership. In the individual-only world, within-group AUC was 0.866. Stable
residual energy followed the expected square law at the oracle level
(\(\varepsilon^{1.999}\)) and a compressed but monotone law in the estimated
score (\(\varepsilon^{1.687}\)); the current design's minimum detectable
individuality was \(\varepsilon=0.50\). C1-only group structure and
single-observer artifacts were both correctly separated from C2 individual
structure. That experiment left the discrete-versus-continuous topology
comparison unresolved. See `reports/V8_VANISHING_INDIVIDUALITY_REPORT.md`.

That topology question has now been closed in planted space, but not in real
text. The first topology-margin rule stopped after ring-to-curve errors; the
revised independent-seed open-set rule passed at its registered low-noise
margin. Minimum clear-world accuracy was 0.894 at N=320 and 0.926 at N=640,
all registered ambiguous primary worlds were refused, and the primary
wrong-decisive/null one-sided 95% upper bounds were 0.00597. Conditional
affine/permutation invariance was 0.974-0.982. Sensitivity is deliberately
reported as a boundary: at noise ratio 0.25 every clear world was refused.
Decision: `V8_C2_TOPOLOGY_MARGIN_PLANTED_PASS`. This distinguishes technical
population geometries in simulation; it does not discover personality types
or establish real-text topology. See `reports/V8_TOPOLOGY_MARGIN_REPORT.md`
and `reports/V8_TOPOLOGY_MARGIN_INDEPENDENT_AUDIT.md`.

The next affine response-set experiment represented each author as a bounded
line, surface, or volume under shared conditions rather than one point. Its
audited code gate passed: same-condition/free-image AUC 1.000/1.000, relation
balanced accuracy 0.9657, finite-scale dimension error 0.0863,
map-equivalence graph F1 1.000, cross-view Jaccard 0.9979, and attack refusal
1.000. A shared condition anchor generated a complete 120-edge raw graph but
zero pair-specific map-equivalence edges, so geometric intersection alone
cannot be interpreted as interpersonal affinity. Independent methodology
decision: `PARTIAL`; the gate covers fixed low-noise affine templates only,
and nonlinear persistence, transversality, real text, and psychological
interpretation remain closed. See
`reports/V8_RESPONSE_SET_INCIDENCE_REPORT.md`.

The nonlinear incidence-multiplicity extension has now passed its final
V2.3 planted battery. Four clear response-group worlds had minimum median
AUC/F1/ARI 1.000/1.000/1.000 and minimum claim rate 0.950; five null worlds
each had 0/160 group claims (worst one-sided upper 0.0185), isolated
transverse contacts had 0/160 claims, and all registered attacks refused.
A global common anchor connected all 24 author trajectories but produced no
group claim, while true groups were recovered at multiplicity 6. Thus
intersection degree alone is not similarity; the candidate object is a
condition-matched, scale-persistent, cross-view-stable, population-specific
incidence hyperedge. Decision:
`V8_INCIDENCE_MULTIPLICITY_PLANTED_PASS`. This remains a simulated technical
code-gate result, not evidence that real-text intersections are personality
similarity. Independent methodology decision is `PARTIAL`: a fitted
whole-map distance baseline also obtained AUC 1.0 in every clear and
challenge world, so incidence has not yet shown incremental information.
See `reports/V8_INCIDENCE_MULTIPLICITY_REPORT.md` and
`reports/V8_INCIDENCE_MULTIPLICITY_INDEPENDENT_AUDIT.md`.

The distance-matched V3/V3.1 battery has now isolated what that object adds.
Positive and counterfactual path populations were constructed with identical
whole-map distance geometry: whole-map AUC was 0.501-0.504, while
condition-aligned persistent-subset AUC, F1, and ARI were all 1.000 in three
registered positive worlds. Positive group claims were 600/600;
asynchronous, overlap-chain, rotating-membership, and two null worlds each
had 0/200 group claims (one-sided 95% upper 0.01487). V3.1 also repaired
hidden persistent-subset recovery and required cross-view support at the same
condition and radius. Independent decision:
`PASS_TECHNICAL_PLANTED_ONLY`.

The result is narrower than “intersections are personality similarity.”
Minimum same-condition distance and a soft local kernel also achieved AUC
approximately 1.0 in the positive worlds. What is established is that local
condition-aligned structure can survive after integrated whole-path distance
has been neutralized, and that a no-chaining hypergraph can express a
simultaneous multi-author core. Raw line count is not informative: a common
anchor can connect all authors without a group-specific claim. See
`reports/V8_INCIDENCE_INCREMENTAL_V31_REPORT.md`.

The V3.2/V3.3 strong-chain sequence then separated higher-order geometry from
simple information loss. V3.2 showed that collapsing condition-indexed
recurrence into one aggregate pair matrix destroys concurrency information.
V3.3 gave three pairwise comparators the complete condition-radius adjacency
tensor; all three recovered 500/500 simultaneous cores and rejected 500/500
strong chains. The accepted theorem is therefore about retaining condition
indices, not generic hypergraph superiority. See
`reports/V8_INCIDENCE_STRONG_CHAIN_V32_INDEPENDENT_AUDIT.md` and
`reports/V8_INCIDENCE_GRAPH_FAIRNESS_V33_INDEPENDENT_AUDIT.md`.

V3.4 isolated one genuinely higher-order object. Two paired worlds had
exactly the same author-pair adjacency in every condition, radius, and
observer view. In one, each planted six-author set fit inside one common
ball; in the other, all pairs were still adjacent but the six points had no
common ball. Over 500 fresh pairs, tensor mismatches were 0, pairwise outputs
matched 500/500, the common-ball estimator recovered the feasible six-author
sets 500/500, and made 0/500 six-author claims in the infeasible world
(one-sided 95% upper 0.00597). All four 200-run controls passed.
Decision: `V8_COMMON_BALL_INCREMENTAL_V34_PASS`.

This gives a precise meaning to an intersection: it is a recurring
multi-author joint-feasibility relation, not a count of incident lines.
Multiplicity alone is not similarity, and even this stronger relation is
not yet personality similarity. Full continuous pairwise distances already
determine minimum-enclosing-ball geometry; the incremental result is only
beyond a finite thresholded binary adjacency tensor in the registered
two-dimensional simulator. Real-text existence and psychological validity
remain closed. See `reports/V8_COMMON_BALL_INCREMENTAL_V34_REPORT.md` and
`reports/V8_COMMON_BALL_INCREMENTAL_V34_INDEPENDENT_AUDIT.md`.

V3.5 executed the previously missing planted-world geometry controls.
Exact common-ball birth scales agreed with numerical truth to
`8.88e-16`; continuous decisions agreed with 9/17/33-point radius grids in
all cases; persistent groups were recovered 200/200 while matched nulls
produced 0/200 group claims. Local curve/surface relations were correctly
classified 2200/2200, all 400 boundary cases were refused, and held-out
nonlinear sheets had AUC 1.000. Decision:
`V8_SCALE_NULL_TRANSVERSAL_MANIFOLD_V35_PASS`; independent decision:
`PARTIAL_TECHNICAL_PASS`. The nonlinear AUC is a local transversality score,
not general manifold reconstruction, and intersection dimension was not
independently recovered. These perfect low-noise planted results validate a
narrow estimator battery, not real-text geometry.
See `reports/V8_SCALE_NULL_TRANSVERSAL_MANIFOLD_V35_REPORT.md`.

V3.6 then separated a junction's geometry from its temporal routing kernel.
The same spacetime junctions supported pass-through, random, and cue-guided
routing, each recovered 500/500. Static marginals could not identify the
world (accuracy 0.316), while event-level transition information did.
Spatial coordinates alone collapsed three repeated stages (accuracy 0.333);
adding time recovered their order perfectly. Cue-guided routing made all 27
depth-three leaves addressable; random routing visited almost the whole tree
but had near-zero channel capacity and goal accuracy near `1/27`. A guided
near-miss retained perfect cue routing while failing the common-junction
gate. The tree/addressability result is partly entailed by the deterministic
generator, and explicit time recovery is a construction check. The supported
statement is that the registered common-ball criterion and cue routing are
logically independent; it is not a thought or intelligence claim. Frozen
decision: `V8_SPACETIME_JUNCTION_FLOW_V36_PASS`; independent decision:
`REGISTERED_DGP_TECHNICAL_PASS / TREE_CAPACITY_PARTIAL`. See
`reports/V8_SPACETIME_JUNCTION_FLOW_V36_REPORT.md`. The V3.6.1 post-seal
scope audit removed sparse path-MI bias: random raw conditional MI 0.411
became -0.0001 after matched permutation correction, while cue-guided routing
retained adjusted MI 0.451 and generalized perfectly to held-out cue-path
combinations. This remains deterministic simulator evidence, not planning or
intelligence; see
`reports/V8_SPACETIME_JUNCTION_FLOW_V361_SCOPE_CORRECTION_REPORT.md`.

V3.7A then made routing author-specific. In a sealed hidden-low-rank synthetic
world, the anonymous author-relative routing operator reached truth
correlation 0.862, split-session reliability 0.650, unseen-context reliability
0.824, and within-group AUC 0.963 across 200 confirmation populations.
Group-only structure raised ordinary author AUC to 0.848 but left within-group
AUC at 0.500, demonstrating why group-conditioned scoring is necessary.
Independent decision: `PASS_WITH_MAJOR_CAVEATS`. The core low-rank recovery
result stands, but variance-source attribution, formal single-author
confidence intervals, fully group-free recovery, and an information-theoretic
sample limit remain open. See
`reports/V8_AUTHOR_ROUTING_OPERATOR_V37A_REPORT.md`.

V3.7B removed the oracle junction window. A geometry-and-order-only locator
recovered the registered pause-plus-perpendicular-cusp family with F1 0.9996
and P95 location error one sample. The blind operator correlated 0.959 with
the oracle-window operator and retained 1.001 of its held-out predictive gain;
cue-leak author claims were 0/200. Canonical decision:
`V8_BLIND_JUNCTION_LOCALIZATION_V37B_PASS`; independent decision:
`PASS_WITH_CAVEATS`. This is a narrow synthetic signature-localization
result. The oracle/blind comparison reused the same events, mask stress was
negligible, and the planted signature closely matched the locator. It is not
open-world event discovery or evidence for thought nodes, intelligence,
personality, clinical meaning, or real text. See
`reports/V8_BLIND_JUNCTION_LOCALIZATION_V37B_REPORT.md` and
`reports/V8_BLIND_JUNCTION_LOCALIZATION_V37B_INDEPENDENT_AUDIT.md`.

V3.7C then removed true-group centering, separated blind and oracle event
panels, added transported path families, and registered MAR/MNAR analyses.
All 20 sealed canonical gates passed. In the core arm, group-free operator
truth correlation was 0.963, independent-oracle correlation 0.935,
split-session reliability 0.740, unseen-context reliability 0.936, and
hard-neighbor author AUC 0.932. A 32-event arm fell to truth correlation
0.526 and unseen-context reliability 0.363, establishing a finite-budget
boundary. Out-of-family and high-noise locator F1 remained 0.984 and 0.962.
Under registered MAR, AIPW excess NRMSE was 0.021 versus 0.103 for
available-case estimation.

The key V3.7C result is a separation between operator recovery and individual
identification. Across true ranks 2/4/6/8, truth correlation stayed near 0.96,
while hard-neighbor AUC changed from 0.777 to 0.961, 0.992, and 0.998.
Low-dimensional author spaces can therefore be measured accurately yet remain
locally crowded. Independent decision: `PASS_WITH_CAVEATS`. Rank 8 and lambda
0.3 are working hyperparameters, MNAR remains a broad sensitivity envelope,
and transport is limited to registered synthetic path families. See
`reports/V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_REPORT.md` and
`reports/V8_GROUP_FREE_ROUTING_TRANSPORT_V37C_INDEPENDENT_AUDIT.md`.

V3.7D mapped the finite-sample boundary between recovery and identity. An
initial in-cohort analysis was rejected after showing mean hard-AUC optimism
of 0.098. The corrected exploration and sealed 40-world confirmation fitted
the stable basis on 96 authors and evaluated entirely disjoint, nested author
sets. All 13 confirmation gates passed. At 128 events, rank-2 truth
correlation stayed near 0.98 while hard-neighbor AUC fell from 0.892 to 0.605
as evaluation authors increased from 32 to 192; the paired AUC loss was
0.288 [0.281, 0.294]. Conversely, a fixed rank-8 estimator retained rank-12
identity AUC above 0.93 while truth correlation stayed near 0.77; a
true-rank sensitivity restored truth correlation to 0.940. At rank 8,
recovery and identity both passed in every 128-event population. Recovery and
identity are therefore bidirectionally separable, not nested, in the
registered synthetic design. This is not personality or real-text evidence.
See
`reports/V8_DIMENSION_DENSITY_EVENT_BUDGET_V37D_CONFIRMATION_REPORT.md` and
`reports/V8_DIMENSION_DENSITY_EVENT_BUDGET_V37D_INDEPENDENT_AUDIT.md`.

V3.7E then tested the strongest alternative explanation for the reverse
rank-12 result: fixed estimator under-capacity. A four-fold author-level
one-standard-error selector used 128 calibration authors, while 256
external-reference and 96 evaluation authors remained disjoint. All 16
sealed gates passed. In 60 flat-spectrum worlds, rank 4/8/12/16 was selected
exactly. At rank 12, fixed rank8 truth correlation was 0.783 and
identity-without-recovery occurred in 93.3% of worlds; adaptive rank raised
truth correlation to 0.952 and changed all worlds to
recovery-plus-identity. Opportunity standardization reduced eight-panel
systematic drift by 0.686 [0.669, 0.703], and a planted population shift was
recovered with direction cosine 0.998 and projected amplitude 1.006. Decision:
`PASS_MISSPECIFICATION_EXPLAINED`. The V3.7D reverse example was a valid
fixed-rank counterexample but did not persist under adaptive capacity. The
external router supports contrast transport; because the projection center
still comes from calibration authors, absolute external norms and
single-author uncertainty remain open. See
`reports/V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_REPORT.md` and
`reports/V8_ADAPTIVE_RANK_FIXED_REFERENCE_V37E_INDEPENDENT_AUDIT.md`.

V3.7F replaced the calibration-cohort origin with disjoint router and
zero/norm reference panels, then added event/reference/rank-subspace
uncertainty and an explicit residual-sufficiency test. All 25 sealed gates
passed across 30 fresh four-world populations. Event-only and full-pipeline
Monte Carlo coverage were 0.944 and 0.952. In an exact rank-12 control, the
scorer-only omitted-space AUC was 0.498; in a 48-direction power-law world,
the finite-budget residual AUC was 0.863 [0.844, 0.882]. A registered
full-space-or-soft rule reduced dense hard capacity floor by 35.0%, while
event-only asymptotic error was 0.0035 and a planted state-alias world retained
a 0.243 positive floor. Decision:
`PASS_EVENT_NOISE_ZERO_TOTAL_FLOOR_POSITIVE`; independent ruling:
`PASS_WITH_MAJOR_CAVEATS`. This supports information-preserving reliability
weighting, not the claims that every token contains personality or that total
prediction error is zero. See
`reports/V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_REPORT.md` and
`reports/V8_EXTERNAL_ZERO_UNCERTAINTY_V37F_INDEPENDENT_AUDIT.md`.

## Provenance

Frozen from the private development repository `project persona` at commits
`154822a`, `05be394`, `cad83d5`, `c27727b`, `1c417fa`, `8447541`, `5189168`,
`b9f65a6`, `0650936`, `5485a02` (+ the freeze commit recorded in
`docs/FREEZE_NOTES.md`). Built with AI-assisted research under the
builder/auditor protocol documented in the guide; seven audit rounds caught
and corrected real artifacts in five of them — the audit trail is part of
the method.
