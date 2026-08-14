# SUICA M4-P3 — the natural gradient under frame refreshment — **INFEASIBLE_SPLIT**

**Outcome: INFEASIBLE_SPLIT (routing cell 1).** STOP / INFEASIBLE_SPLIT. Stopped at
G1p3(a) -- provably unsatisfiable through the existing constructor interface. **0 worlds drawn, no seal.** Ladder: none: the registration legislates STOP as INFEASIBLE_SPLIT and calls it an instrument finding, not a failure.

The registration anticipated this exact possibility and legislated the
response, calling it *an instrument finding, not a failure*. It is delivered as
one: the impossibility is **proven over the constructor's entire input space**,
not inferred from reading the code, and every Part-0 object that survives a
re-dispatch is computed and persisted.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit caba52f).
Every number below is generated from artifacts by code (rule 24).

---

## 1. What the leg needed, and why it cannot have it

P3 needs paired worlds A and B sharing the AUTHOR/TRAIT channel draws and
differing in the STATE/FRAME channel draws, achieved **by seeding alone through
the existing constructor interface** (k2b and `suica_core/` READ-ONLY).

Applying the registration's own channel rule (RN-P3-1): AUTHOR = trait, a_load;
FRAME = slow, slow_latent, common, int.

| property | value |
|---|---|
| constructor | build_k2b_world |
| module | `scripts/run_suica_m4_k2b_t4_branch.py` |
| **signature** | `build_k2b_world(world_seed: 'int', phi_slow: 'float') -> 'dict[str, np.ndarray]'` |
| number of parameters | 2 |
| has *args / **kwargs | False |
| any parameter defaults | False |
| input space | the pair (world_seed, phi_slow) -- there is nothing else to vary, so enumerating the effect of each argument is a PROOF over the whole interface (RN-P3-2) |
| parameter: world_seed | POSITIONAL_OR_KEYWORD, annotation int, default False |
| parameter: phi_slow | POSITIONAL_OR_KEYWORD, annotation float, default False |

The constructor takes **2 parameters**, no varargs (False) and no
defaults (False). Its input space is therefore the pair
`(world_seed, phi_slow)` and nothing else — which is what makes the following an
exhaustive proof rather than a sample.

## 2. The proof

8 trials, covering both axes and their combination. A split exists iff
some row has *author all identical* = True **and** *any frame differs* = True.

| axis | point | trait (A) | a_load (A) | slow (F) | slow_latent (F) | common (F) | int (F) | author all identical | any frame differs | SPLIT? |
|---|---|---|---|---|---|---|---|---|---|---|
| vary world_seed (fixed phi) | {'phi_slow': 0.05, 'world_seed': 1002} | False | False | False | False | False | False | False | True | no |
| vary world_seed (fixed phi) | {'phi_slow': 0.05, 'world_seed': 20260814} | False | False | False | False | False | False | False | True | no |
| vary world_seed (fixed phi) | {'phi_slow': 0.05, 'world_seed': 7} | False | False | False | False | False | False | False | True | no |
| vary phi_slow (fixed world_seed) | {'phi_slow': 0.3, 'world_seed': 1001} | True | True | False | False | True | True | True | True | **YES** |
| vary phi_slow (fixed world_seed) | {'phi_slow': 0.6, 'world_seed': 1001} | True | True | False | False | True | True | True | True | **YES** |
| vary phi_slow (fixed world_seed) | {'phi_slow': 0.85, 'world_seed': 1001} | True | True | False | False | True | True | True | True | **YES** |
| vary phi_slow (fixed world_seed) | {'phi_slow': 0.98, 'world_seed': 1001} | True | True | False | False | True | True | True | True | **YES** |
| vary both | {'phi_slow': 0.98, 'world_seed': 1002} | False | False | False | False | False | False | False | True | no |

**No row satisfies the registered split.** (False = split found under the
predicate that routes.)

A predicate subtlety was caught and pinned before any verdict existed
(RN-P3-6), and it is disclosed because a looser reading would have flipped the
outcome. Scoring "any frame object differs" makes the φ axis look like a split:
at fixed seed, varying φ leaves the author channel bit-identical and moves
`slow`. That reading is wrong on two independent grounds, both read off the
registration — **A and B must sit at the same φ** (φ is the ladder variable
being decomposed, so it cannot also be the refresher), and **`common` is
bit-identical across φ**, with only the recombination of the *same* innovation
draws changing, which is not a fresh draw. The tight predicate — at fixed φ, a
seed pair holding the author channel identical while `common` differs — is the
one that routes. Both are computed and reported below.

| axis | result |
|---|---|
| vary world_seed | changing world_seed changes EVERY channel, the author channel included -- so G1p3(a) (author objects bit-identical per pair) fails at every seed pair |
| vary phi_slow | changing phi_slow holds the author channel bit-identical but refreshes only ['slow', 'slow_latent'] -- `common`, the frame channel proper, is BIT-IDENTICAL across phi, so G1p3(b) fails on the object the leg is about; and phi is this design's own treatment axis, so it could not serve as the refresher even if it did move `common` |
| occasion assignments | the registration's third frame item lives in k2b.layout(), which takes no arguments and is memoised in a module-private global -- not seed-driven at all |
| frame objects refreshable by seeding | ['slow', 'slow_latent'] |
| frame objects NOT refreshable by seeding | ['common', 'int'] |
| split under the TIGHT predicate (routes) | **False** |
| split under the LOOSE predicate (reported only) | True -- satisfied by ['vary phi_slow (fixed world_seed)', 'vary phi_slow (fixed world_seed)', 'vary phi_slow (fixed world_seed)', 'vary phi_slow (fixed world_seed)'] |
| why the loose predicate is wrong | A and B must sit at the SAME phi (phi is the ladder variable being decomposed), and across phi `common` is bit-identical -- only the recombination of the same innovations changes, which is not a fresh draw |
| **conclusion** | **the constructor's input space contains NO pair of points at which every author object is bit-identical and any frame object differs; the split is impossible by seeding alone** |

Two facts do the work:

- **Changing `world_seed` changes everything, the author channel included.**
  `trait` is built from `z` and `loadings`, both drawn from
  `default_rng(world_seed)` *before* any frame object, so G1p3(a) — author
  objects bit-identical per pair — fails at every seed pair.
- **Changing `phi_slow` holds the author channel bit-identical but does not
  refresh the frame.** Only slow, slow_latent move; **common, int are
  bit-identical across φ** — and `common`, the frame channel proper and the
  object this leg is about, is among them. φ is also this design's own treatment
  axis, so it could not serve as the refresher even if it did move `common`.

the registration's third frame item lives in k2b.layout(), which takes no arguments and is memoised in a module-private global -- not seed-driven at all

## 3. Routes that would work, and why none is taken

| route | why it is not taken |
|---|---|
| editing build_k2b_world to accept split seeds | k2b is READ-ONLY by the registration |
| channel surgery on the returned dicts | not 'seeding'; and the constructor does not return `loadings`, so a splice would silently mix two orthonormal bases with no way for a caller to detect it |
| mutating k2b's memoised private _LAYOUT | module-private state mutation, not seeding, and it cannot refresh the slow state |

Each is excluded by the registration's own words, not by preference. Recording
them is the useful part of a STOP: they are the menu the planner chooses from.

| question | answer |
|---|---|
| minimal interface change | build_k2b_world would need to accept the frame stream's seed separately from the author stream's -- e.g. an optional frame_seed defaulting to world_seed, which would leave every existing call bit-identical |
| why that suffices | trait and a_load are drawn before any frame object and depend only on the author stream; common, int and the state would then key on frame_seed |
| cost | an edit to k2b, which this leg is forbidden to make |
| alternative needing no edit | reader-level refreshment (K1b / K1c-prime's reader A vs A', disjoint norm sub-pools) is the programme's OWN published form of the T6-double-prime operation and is fully supported by existing machinery -- a different estimand, named for the planner, not chosen here (RN-P3-5) |

The minimal change is small and backward-compatible — build_k2b_world would need to accept the frame stream's seed separately from the author stream's -- e.g. an optional frame_seed defaulting to world_seed, which would leave every existing call bit-identical — but it is an
edit to k2b, which this leg is forbidden to make. **The alternative needing no
edit is worth the planner's attention:** reader-level refreshment (K1b / K1c-prime's reader A vs A', disjoint norm sub-pools) is the programme's OWN published form of the T6-double-prime operation and is fully supported by existing machinery -- a different estimand, named for the planner, not chosen here (RN-P3-5)

## 4. The lineage, located — and a finding inside it

G0p3(iv) asked for the T6″ frame-refreshment lineage. All 5/5
anchors were located and quoted by code.

| anchor | located at | verbatim quote (extracted by code, rule 24) |
|---|---|---|
| T6-double-prime v2, the sign form (IDT D.3) | `docs/SUICA_IDENTITY_THEORY_V1.md:489` (para 486-493) | **D.3 — T6″ v2 (sign form).** The v1 operationalization (zero-equivalence band after refreshment) was a planner rule-4 violation: under refreshment the expected value is NOT zero but the honest issuer-noise penalty. Correct form: **under frame refreshment, no reader may PROFIT from frame error** — est-frame minus oracle must be ≤ 0 within tolerance; a positive advantage under refreshed frames is the forgery signature. The measured inversion (−0.0623) with oracle stability 0.00254 vindicates the direction and the do-no-harm clause. Confirmatory lean at the live knob rides K1c (L-e″). |
| T6-double-prime, the theory statement (IDT C.4) | `docs/SUICA_IDENTITY_THEORY_V1.md:431` (para 431-442) | **C.4 — T6″ (frame-refreshed discriminator).** K1's disclosed by-product: under the T3(c)-hypothesis reader in the free design, issuer sampling error becomes a person-specific, occasion-half-REPRODUCIBLE component that IMPROVES re-identification (est8 beats oracle: pooled −0.050127, CI [−0.056726, −0.043782], 0/8 in the registered direction, monotone the wrong way) — **a forged identity that passes T6's own discriminator**, manufactured by issuer error interacting with person-specific occasion sampling. Patch, now part of the theory and under test as K1b lean L-d: **Id(i\|F) requires stability under JOINT resampling of occasions AND frame** (the issuer re-estimated independently per replicate… |
| T9 / the P3 pattern (IDT appendix GG.3) | `docs/SUICA_IDENTITY_THEORY_V1.md:1826` (para 1820-1831) | **GG.3 — What this asks of the M-line's law.** The sealed level law is untouched AS A LAW OF THE STATISTIC (its predictions were and remain sealed hits). What P2 opens is the DECOMPOSITION of its natural φ-gradient: injection moved the statistic mostly through frame-agreement — does the natural gradient decompose the same way? P3 answers with the theory's own licensed counter-operation (T9 frame REFRESHMENT, the T6″ pattern): same authors, fresh frame, g_ratio = refreshed gradient / natural gradient. MOSTLY_FRAME re-types the mechanism section; SUBSTANTIALLY_GENUINE strengthens the scaffold-gradient; NO_TRANSPORTABLE_READING is K-R1's picture at natural regimes. All three are live; the lean … |
| the published IMPLEMENTATION of frame-refreshed scoring | `scripts/run_suica_m4_k1b_composition_ownership.py:891` (para 869-899) | def run_sec_world(world: int, knobs: dict[str, Any], knob_tag: str) -> dict[str, Any]: module = k1() module.N_ORACLE = SEC_NORM_POOL seed = world_seed_for("abs", world, knob_tag) reference = json.loads(REF_PATH.read_text(encoding="utf-8")) n_panel = len(f2().build_layout_common(reference)[0]) panel, norm_events, labels = module.build_abs_world("free", n_panel, knobs, seed) half = SEC_NORM_POOL // 2 pool_a, pool_b = norm_events[:half], norm_events[half:] mus = { ("oracle", "a"): pool_a.mean(axis=0), ("oracle", "b"): pool_b.mean(axis=0), ("est8", "a"): pool_a[:SEC_EST].mean(axis=0), ("est8", "b"): pool_b[:SEC_EST].mean(axis=0), } out: dict[str, Any] = {"world": int(world), "world_seed": int(se… |
| the registered reader design (K-line, K1b secondary) | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md:355` (para 353-356) | Secondary (card level, K1's R-abs machinery, free design, first 8 of the 32 worlds): reader A (T3(c)-hypothesis, one norm shared across halves) vs reader A′ (frame-refreshed: INDEPENDENT est8 norm samples per occasion half). Contrast tracked: rank-1(est8) − rank-1(oracle) under each reader. |

**The finding (RN-P3-5, reported not routed):** every published
frame-refreshment in this programme — K1b's and K1c′'s reader A vs A′ —
refreshes the **reader's** norm/issuer sample via disjoint author sub-pools. It
never refreshes the **generator's** frame channel. The operation P3 registers is
generator-level refreshment, which has no precedent in the repo and, as §2
proves, no interface. The T6″ pattern the registration cites is real and
published; it simply lives at a different layer than the one P3 needs.

## 5. What Part 0 established anyway

These are reusable verbatim on re-dispatch.

### 5.1 M1c's share-0.25 row (the V-P3a anchor)

| cell | phi | r_pred | M1c field mean | SEM | sd | n |
|---|---|---|---|---|---|---|
| s0.25_p0.05 | 0.05 | 0.785015540293945 | 0.12162744485545209 | 0.0017778785791358425 | 0.02463500823001315 | 192 |
| s0.25_p0.30 | 0.3 | 0.7761302864207245 | 0.12295515685269942 | 0.001799144985921348 | 0.024929684206388535 | 192 |
| s0.25_p0.60 | 0.6 | 0.7558507450373838 | 0.12714790436588774 | 0.0017053615065044834 | 0.02363018219630374 | 192 |
| s0.25_p0.85 | 0.85 | 0.7168731389294273 | 0.13204663807737851 | 0.0018782693723257374 | 0.026026063865349454 | 192 |
| s0.25_p0.98 | 0.98 | 0.6763691758553391 | 0.13201888792665142 | 0.0018133362157806163 | 0.025126323655493665 | 192 |
| **realized natural range (phi .05 - phi .98)** | — | — | **-0.010391443071199338** | — | — | — |

5 cells from `results/m4_m1c_r_at_level/cell_means.csv`. The realized natural range across the ladder
is **-0.010391443071199338** — note the sign: the field mean *rises* with φ while
r_pred falls, which is M1c's side-signing convention and is what P3's
`range_nat` would have anchored against.

### 5.2 The ladder's r values

| phi | r recomputed from the pinned map | r persisted in M1c | bit-exact |
|---|---|---|---|
| 0.05 | 0.785015540293945 | 0.785015540293945 | True |
| 0.3 | 0.7761302864207245 | 0.7761302864207245 | True |
| 0.6 | 0.7558507450373838 | 0.7558507450373838 | True |
| 0.85 | 0.7168731389294273 | 0.7168731389294273 | True |
| 0.98 | 0.6763691758553391 | 0.6763691758553391 | True |

### 5.3 P2's headline (the projection truths)

| quantity | value |
|---|---|
| P2 verdict | GENUINE_SCAFFOLD |
| f at B1 | 0.9584700070215529 [0.9386859990245562, 0.9784391977625343] |
| f at B2 | 0.971270002747466 [0.9535253481648153, 0.9882217251532477] |
| b_cf at B1 | 0.015370398353696113 [0.009829531824123106, 0.02099405067675933] |
| b_cf at B2 | 0.010909345621091282 [0.00559827343632706, 0.016261954399254843] |
| 1 - f at B1 (the registration's g = 0.04 projection truth) | 0.04152999297844706 |
| 1 - f at B2 | 0.028729997252534 |
| arms in P2's table | 10 |

The registration's g = 0.04 projection truth is P2's 1 − f: 0.04152999297844706 at B1 and
0.028729997252534 at B2.

## 6. Routing

| # | condition | outcome |
|---|---|---|
| 1 | G0p3/G1p3 failure or seed-split impossible via seeding alone | **STOP / INFEASIBLE_SPLIT**  <-- THIS LEG |
| 2 | projection fails after escalation | NON_PROJECTABLE |
| 3 | V-P3a fails | ANCHOR_BREAK (instrument stop; nothing adjudicated) |
| 4 | V-P3c fires | NO_TRANSPORTABLE_READING -- the natural gradient carries no frame-refreshed person signal at all; V-P3b N/A |
| 5 | g_ratio MOSTLY_FRAME | NATURAL_GRADIENT_MOSTLY_FRAME -- the M-line law's r-channel is dominated by frame-agreement; the law stands as a law of the statistic |
| 6 | g_ratio INTERMEDIATE | MIXED_GRADIENT -- quantified split; theory carries the number |
| 7 | g_ratio SUBSTANTIALLY_GENUINE | GENUINE_GRADIENT -- the r-channel transports across frames |
| 8 | UNDERPOWERED / budget unmet | UNDERPOWERED (+ UNQUANTIFIED modifier; levels reported) |

## 7. Gates

| gate | PASS | detail |
|---|---|---|
| G0p3 | True | M1c's share-0.25 row, P2's headline, the five ladder r values and the T6-double-prime lineage all verified; reusable on re-dispatch |
| G1p3 | False | (a) provably unsatisfiable: no point in the constructor's input space holds the author channel bit-identical while changing a frame object; (b) fails for `common`; (c) vacuous |
| G2p3 | None | not reached (no world drawn) |
| G3p3 | None | not reached |
| G4p3 | True | routing disjoint-and-covering; tables generated (rule 24); stopped inside the part0 + feasibility estimate |

## 8. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G3p3 | g_ratio CI width <= 0.30 at both projection truths | — | one-sided |
| L-1p3 | MOSTLY_FRAME / INTERMEDIATE / NO_TRANSPORTABLE_READING / other | 0.55 / 0.20 / 0.15 / 0.10 | categorical |
| V-P3a | R_nat replicates M1c's share-0.25 row within 2*sqrt(2)*SEM | — | two-sided |
| V-P3b | g_ratio classification, NULL-first | — | categorical |

## 9. Pinned readings

| note | pinned reading |
|---|---|
| RN-P3-1 | the registration's channel rule applied literally: AUTHOR = trait, a_load (persist per author across occasions); FRAME = slow, slow_latent, common, int (per-occasion / per-context). Occasion assignments, the third frame item, live in layout(), which takes no arguments and is memoised -- not seed-driven at all |
| RN-P3-2 | build_k2b_world has exactly two POSITIONAL_OR_KEYWORD parameters and no defaults/varargs (verified by inspect at run time), so 'seeding alone' means choosing two points in the (world_seed, phi_slow) space; the feasibility test enumerates that space EXHAUSTIVELY, which is a proof over the whole interface rather than a sample of it |
| RN-P3-3 | three routes would work and all three are excluded by the registration's own words: editing k2b (READ-ONLY), channel surgery on the returned dicts (not seeding, and incoherent because loadings are not returned so two orthonormal bases would be silently spliced), and mutating k2b's memoised private _LAYOUT (not seeding, and cannot refresh the slow state). Each is recorded as a route the planner could authorise; none is taken |
| RN-P3-4 | G0p3's citation clauses cost nothing and are fully reusable on re-dispatch, so they are executed and persisted even though the leg stops; only the clauses needing worlds are skipped |
| RN-P3-5 | every published frame-refreshment in the programme (K1b / K1c-prime reader A vs A') refreshes the READER's norm sample, never the generator's frame channel; generator-level refreshment has no precedent and no interface. Reported because it names a supported alternative route -- naming is not choosing |
| RN-P3-6 | the split predicate, tightened before the verdict: A and B must sit at the SAME phi (phi is the ladder variable being decomposed, not a refresher) and 'fresh frame draws' means `common` must differ -- across phi `common` is bit-identical and only the recombination of the same innovations changes, which is not a fresh draw. PINNED: split_found iff AT FIXED phi some seed pair holds every AUTHOR object identical AND changes `common`. Both the loose and tight predicates are reported; the tight one routes |

## 10. Rule events

- **Rule 13:** not reached — no verdict boundary exists without a measurement.
- **Rule 26:** no bounded winner; nothing was fitted.
- **Rule 29:** not reached (no world drawn); the predicate was pinned in Part 0
  and stands ready for a re-dispatch.
- **Rule 30:** exercised throughout — every cited constant is read from its
  persisted source and every quoted sentence is extracted by code, including
  the lineage quotes in §4.

## 11. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

No hypothesis-relevant number was ever computed: the leg stopped before its
first measured world.

## 12. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |

## 13. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 120 | 0.400 |
| feasibility | 30 | 0.185 |
| finalize | 60 | 0.000 |
| pilot | 60 | -- not reached |
| worlds (5 chunks) | 240 each | -- not reached |
| score+fit | 180 | -- not reached |

---

*Artifacts: `results/m4_p3_refresh_gradient/` (gitignored) — `part0.json`,
`feasibility.json`, `decision.json`, `prose_facts.json`, `report_tables.md`,
`run_log.jsonl`. Harness: `scripts/run_suica_m4_p3_refresh_gradient.py`.*
