# SUICA M4-P3b — the refresh gradient, certified instrument — **NON_PROJECTABLE**

**Outcome: NON_PROJECTABLE (routing cell 2); modifiers: none.**
NON_PROJECTABLE. Stopped at G3 (rule 25), after the registered once-only escalation. **0 measurement worlds.**

**The instrument P3 said was needed now exists and is certified.** What the leg
also establishes is that the registered estimand cannot be measured on it at any
feasible size: g_ratio's projected CI is 2.323228359818655 wide at the registered 192
pairs/φ and still 1.4117460845242706 at the escalated 384, against a 0.3 budget, and
**12288 pairs/φ — 64.0× the registered design — would be required.** The
reason is structural and is stated in §4.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit debc68e).
Every number below is generated from artifacts by code (rule 24).

---

## 1. The instrument, and its provenance

P3 proved generator-side frame refreshment impossible on k2b's published
two-parameter interface. The licensed remedy was minimal extraction with
provenance. `build_split_world(author_seed, frame_seed, phi_slow)` is that
extraction: **18 mapped entries covering k2b:321-349, and exactly
4 edits.**

| property | value |
|---|---|
| source | `scripts/run_suica_m4_k2b_t4_branch.py:321-349` |
| mapped entries | 18 |
| stream split | {'SPLIT': 1, 'author': 6, 'derived': 1, 'frame': 7, 'mixed': 2, 'return': 1} |
| **total edits** | **4** |
| edit 1 | rng -> rng_a / rng_f (k2b:321) |
| edit 2 | world_seed -> author_seed at k2b:338-340 (a_load) |
| edit 3 | world_seed -> frame_seed at k2b:333-336 (common) and k2b:342 (shocks) |
| edit 4 | the return dict gains 'loadings' (k2b does not expose it) |
| imported, never copied | K_LATENT, DIM, G_PROFILE, A_SCALE, SIGMA_ISO, _orthonormal_loadings, f2().shock_vector, k2a().shock_int_matrix, v8.stable_bucket, layout, emit_panel, field_from_vectors |

| k2b lines | k2b source | as extracted | stream | note |
|---|---|---|---|---|
| 321 | `rng = np.random.default_rng(world_seed)` | `rng_a = default_rng(author_seed); rng_f = default_rng(frame_seed)` | SPLIT | the one edit that makes the instrument: one stream becomes two |
| 322 | `loadings = _orthonormal_loadings(rng, DIM, k)` | `loadings = _orthonormal_loadings(rng_a, DIM, k)` | author | the shared basis; author-stream so an A/B pair shares it (RN-P3B-4) |
| 323 | `z = rng.normal(size=(n, k))` | `z = rng_a.normal(size=(n, k))` | author | the b-draw |
| 324 | `_zeta = rng.normal(size=(n, k))` | `_zeta = rng_a.normal(size=(n, k))` | author | unused in k2b and here; holds k2b's stream order (RN-P3B-3) |
| 325-326 | `xs = np.empty(...); xs[:, 0] = rng.normal(size=(n, k))` | `xs[:, 0] = rng_f.normal(size=(n, k))` | frame | the state's initial condition |
| 327 | `innovation_scale = math.sqrt(1.0 - phi_slow**2)` | `unchanged` | derived | phi enters here exactly as in k2b |
| 328-329 | `xs[:, t] = phi*xs[:, t-1] + iscale*rng.normal(size=(n, k))` | `... + iscale * rng_f.normal(size=(n, k))` | frame | the AR recursion |
| 330 | `noise = rng.normal(size=(n, t_max, DIM))` | `noise = rng_f.normal(size=(n, t_max, DIM))` | frame | pinned to the frame stream by the registration's taxonomy |
| 331 | `trait = A_SCALE * ((z * G_PROFILE) @ loadings.T)` | `unchanged` | author | author draw through the shared basis |
| 332 | `slow = A_SCALE * ((xs * G_PROFILE) @ loadings.T)` | `unchanged` | frame | frame state through the SHARED basis |
| 333-336 | `common_lat = stack(f2().shock_vector(world_seed, c, o, k))` | `... f2().shock_vector(frame_seed, c, o, k)` | frame | keyed call site #2: the frame channel proper |
| 337 | `common = A_SCALE * ((common_lat * G_PROFILE) @ loadings.T)` | `unchanged` | frame | frame content through the SHARED basis |
| 338-340 | `a_rng = default_rng(v8.stable_bucket(str(world_seed), salt='m4k2b-loading'))` | `... stable_bucket(str(author_seed), salt='m4k2b-loading')` | author | keyed call site #3: the per-author interaction carrier |
| 341 | `a_load = a_rng.normal(size=(n, k))` | `unchanged` | author | per-author-persistent |
| 342 | `shocks = stack(k2a().shock_int_matrix(world_seed, o, k))` | `... k2a().shock_int_matrix(frame_seed, o, k)` | frame | keyed call site #4: per-occasion interaction shocks |
| 343 | `u_int = einsum('ij,ojl->iol', a_load, shocks) / sqrt(k)` | `unchanged` | mixed | author carrier x frame shocks -- the interaction, correctly mixed |
| 344 | `s_int = A_SCALE * ((u_int * G_PROFILE) @ loadings.T)` | `unchanged` | mixed | through the SHARED basis |
| 345-353 | `return {trait, slow, int, common, noise, slow_latent, a_load}` | `same keys PLUS 'loadings' (k2b does not return it; C2c needs it)` | return | the one ADDITION: k2b withholds loadings, which is what made P3's channel surgery undetectable; exposing it here is what makes C2c possible |

Constants and helpers are **imported from k2b, never copied**, so a change there
propagates here instead of silently diverging. k2b and `suica_core/` are
untouched and diff-verified.

### 1.1 The one addition, and why it matters

k2b does not return `loadings`. That omission is exactly what made P3's
channel-surgery route undetectable — a caller splicing two worlds could not see
it had mixed two orthonormal bases. The extracted builder returns `loadings`,
which is what makes C2c checkable at all.

### 1.2 The comparison against k2b is a positive verification

| object | split-world == k2b at equal seeds |
|---|---|
| a_load | True |
| common | True |
| int | True |
| noise | False |
| slow | False |
| slow_latent | False |
| trait | True |
| **identical** | a_load, common, int, trait |
| **differing** | noise, slow, slow_latent |
| author half reproduces k2b bit-exactly | True |
| only the sequential frame draws differ | True |
| reading | at equal seeds the AUTHOR half reproduces k2b BIT-EXACTLY -- loadings and z are the first draws of the author stream just as they are k2b's first draws, so trait matches; a_load, common and int are keyed on a seed rather than on stream position, so they match too. The ONLY divergence is the three objects the frame stream draws in sequence (slow, slow_latent, noise), which differ because that stream restarts at the seed's first draw instead of continuing after the author draws. This localises the divergence to the stream restart itself -- it is a POSITIVE verification of the transcription, not a caveat |
| gates the leg | False |

At equal seeds the **author half reproduces k2b bit-exactly**
(True): `loadings` and `z` are the first draws of the author stream
exactly as they are k2b's first draws, so `trait` matches, and `a_load`,
`common` and `int` are keyed on a seed rather than on stream position, so they
match too. The only divergence is noise, slow, slow_latent — the three objects the frame
stream draws in sequence, which differ because that stream restarts at the
seed's first draw instead of continuing after the author draws
(True). **The divergence is localised to the stream restart itself**,
which is inherent to splitting and gates nothing.

## 2. Certification — the split P3 proved impossible on the published interface

| object | stream | result across the 8 probe pairs |
|---|---|---|
| trait | author | bit-identical on every pair: True |
| a_load | author | bit-identical on every pair: True |
| loadings | author | bit-identical on every pair: True |
| slow | frame | differs on every pair; norm delta in [250.9186220787883, 251.6310585032786] |
| slow_latent | frame | differs on every pair; norm delta in [1229.0471669041528, 1232.475921191497] |
| noise | frame | differs on every pair; norm delta in [250.76248392701416, 251.26126326265268] |
| common | frame | differs on every pair; norm delta in [15.521348769823044, 16.262406409804694] |
| int | frame | differs on every pair; norm delta in [248.05669190330656, 251.93853774424574] |
| **C2a** | — | **PASS = True** |

| check | detail | PASS |
|---|---|---|
| C2b determinism | same triple rebuilt; 8 objects | True |
| C2c shared basis | loadings bit-identical across all 8 pairs | True |

Across 8 probe pairs sharing an author seed, **every author object is
bit-identical and every frame object differs** — `common`, the frame channel
proper, by a norm delta in [15.521348769823044, 16.262406409804694]. C2b rebuilds a
world from the same triple bit-identically; C2c confirms the shared basis on
every pair. C2a = True, C2b = True, C2c = True.

**This is the leg's durable asset**: a certified split-seed instrument for the
K2b family, obtained without touching published machinery.

## 3. C3 — the sanity pilot and the bands

| phi | n | R_nat mean | R_refresh mean | R_deframe mean | PASS |
|---|---|---|---|---|---|
| 0.05 | 4 | 0.13326371171241497 | 0.011644843702809294 | 0.0007463605153870461 | True |
| 0.98 | 4 | 0.12786906781795995 | 0.0001461128493001931 | 0.012251647793290816 | True |

| quantity | value |
|---|---|
| sigma R_nat (raw / df-inflated) | 0.01995916781903592 / 0.032930580570026624 |
| sigma R_refresh (raw / df-inflated) | 0.028267841353526564 / 0.04663904004781301 |
| pooled df / inflation | 6 / 1.6498974741130894 |
| SE(range_ref) at 192 pairs | 0.0047600770920988265 |
| M1c realized natural range | -0.010391443071199338 |
| **V-P3b equivalence band on g_ratio** | **0.9161532348267848** |
| **V-P3c floor on R_refresh levels** | **0.006731765581587645** |

The V-P3b equivalence band (0.9161532348267848) and the V-P3c floor (0.006731765581587645) were
computed from realized pilot noise, df-inflated (df 6, factor 1.6498974741130894),
and written **before** any arm — exactly as registered. C3 = True.

The equivalence band is itself the first warning: **0.9161532348267848 spans nearly the
whole interesting range of g_ratio**, so at the registered size almost any ratio
would have been indistinguishable from zero.

## 4. G3 — the projection, and why it fails

| pairs/phi | truth g | SE(range_nat) | SE(range_ref) | projected g_ratio 95% CI | width | budget | within |
|---|---|---|---|---|---|---|---|
| 192 (registered) | 0.04 | 0.0033609633054239685 | 0.0047600770920988265 | [-1.0205225392166732, 1.3027058206019817] | 2.323228359818655 | 0.3 | False |
| 192 (registered) | 0.5 | 0.0033609633054239685 | 0.0047600770920988265 | [-0.4999284805257762, 1.9306216588125371] | 2.4305501393383135 | 0.3 | False |
| 384 (escalated) | 0.04 | 0.0023765599445844414 | 0.003365882790793822 | [-0.6267371454071723, 0.7850089391170982] | 1.4117460845242706 | 0.3 | False |
| 384 (escalated) | 0.5 | 0.0023765599445844414 | 0.003365882790793822 | [-0.15255945826573986, 1.3445368651754255] | 1.4970963234411654 | 0.3 | False |

| quantity | value |
|---|---|
| structure | g_ratio = range_ref / range_nat is a ratio whose DENOMINATOR is the natural gradient itself |
| M1c's realized natural range (the denominator) | 0.010391443071199338 |
| sigma R_nat (df-inflated) | 0.032930580570026624 |
| SE(range_nat) at 192 | 0.0033609633054239685 |
| **the denominator, in SE** | **3.091804975802469** |
| reading | the natural gradient this leg must divide by is roughly the size of a few standard errors at the registered design, so the ratio's sampling distribution is wide however precisely the numerator is measured; the equivalence band computed from the same noise is 0.9161532348267848, i.e. nearly the whole interesting range, which is the same fact seen from the other side |
| pairs/phi needed at truth g = 0.04 | 12288 = 64.0x the registered 192 |
| pairs/phi needed at truth g = 0.5 | 12288 = 64.0x the registered 192 |

The estimand is a **ratio whose denominator is the natural gradient itself**.
M1c's realized natural range is 0.010391443071199338, and SE(range_nat) at 192 pairs is
0.0033609633054239685 — so the denominator sits at **3.091804975802469 SE**. Dividing by a
quantity known to three standard errors produces a wide ratio however precisely
the numerator is measured: widths 2.323228359818655 / 2.4305501393383135 at 192 and 1.4117460845242706 /
1.4970963234411654 at 384, against a 0.3 budget. The once-only escalation fired and
did not rescue it (True); 12288 pairs/φ (64.0×) would be needed.

Per rule 25 and the registration's routing, the leg stops here: **no measurement
world is spent against a failed feasibility gate.**

### 4.1 A named alternative, so the handback is actionable

| property | value |
|---|---|
| quantity | range_ref itself (or the DIFFERENCE range_nat - range_ref) instead of their RATIO |
| why it helps | a difference does not divide by a small, noisy denominator; all of the ratio's width comes from range_nat sitting at 3.09 SE |
| at 192 pairs/phi: SE(range_ref) / 2-SE half-width / range_nat in SE | 0.0047600770920988265 / 0.009520154184197653 / 2.1830409193262694 |
| at 384 pairs/phi: SE(range_ref) / 2-SE half-width / range_nat in SE | 0.003365882790793822 / 0.006731765581587644 / 3.0872860753266402 |
| **status** | **NAMED FOR THE PLANNER, NOT CHOSEN -- this leg's estimand is the registered ratio and the executor does not substitute estimands** |

A DIFFERENCE does not divide by a small noisy denominator. This is **named for
the planner, not chosen** — the executor does not substitute estimands.

## 5. What was not reached

C1′ (the M1c anchor as certificate) and the five measurement arms are not
reached: the rule-25 gate fires before them. C1′ therefore remains the right
first test on any re-dispatch, and the instrument is ready for it.

## 6. Routing

| # | condition | outcome |
|---|---|---|
| 1 | G0/C2/C3 failure, or C1' anchor fails | INSTRUMENT_DEFECT -- a stop about the extraction, never a finding about the world |
| 2 | projection fails after escalation | **NON_PROJECTABLE**  <-- THIS LEG |
| 3 | V-P3c fires | NO_TRANSPORTABLE_READING -- the natural gradient carries no frame-refreshed person signal at all; V-P3b N/A |
| 4 | g_ratio MOSTLY_FRAME or NO_TRANSPORTABLE_GRADIENT | NATURAL_GRADIENT_MOSTLY_FRAME -- the M-line law's r-channel is dominated by frame-agreement; the law stands as a law of the statistic; the theory's mechanism section re-types |
| 5 | g_ratio INTERMEDIATE | MIXED_GRADIENT -- quantified split; theory carries the number |
| 6 | g_ratio SUBSTANTIALLY_GENUINE | GENUINE_GRADIENT -- the r-channel transports across frames; the scaffold-gradient reading strengthens |
| 7 | budget unmet | UNDERPOWERED (+ UNQUANTIFIED modifier; levels reported) |

## 7. Gates

| gate | PASS | detail |
|---|---|---|
| G0 | True | M1c's share-0.25 row, P2's headline and the five ladder r values verified bit-exact |
| C2a | True | 8 probe pairs: author objects bit-identical, every frame object differs |
| C2b | True | same (author_seed, frame_seed, phi) rebuilt bit-identical |
| C2c | True | loadings bit-identical across every pair -- no basis mixing |
| C3 | True | rule-29 predicate on BOTH scorings; bands computed df-inflated and written before any arm |
| C1' | None | not reached -- the rule-25 gate fires before the measurement arms |
| G3 | False | g_ratio CI width 2.323228359818655 / 2.4305501393383135 at 192 and 1.4117460845242706 / 1.4970963234411654 at 384, against a 0.3 budget |

## 8. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G3 | g_ratio CI width <= 0.3 at truths [0.04, 0.5] | — | one-sided |
| L-1p3 | MOSTLY_FRAME / INTERMEDIATE / NO_TRANSPORTABLE_READING / other | 0.55 / 0.20 / 0.15 / 0.10 | categorical |
| V-P3a / C1' | R_nat's five levels within 2.8284271247461903*SEM of M1c's row | — | two-sided |
| V-P3b | g_ratio classification, NULL-first | — | categorical |

## 9. Pinned readings

| note | pinned reading |
|---|---|
| RN-P3B-1 | the extraction is a transcription: every line carries its k2b source line, the only edits are rng -> rng_a/rng_f and world_seed -> author_seed/frame_seed at the four keyed call sites, and all constants and helpers are IMPORTED from k2b rather than copied |
| RN-P3B-2 | build_split_world(s, s, phi) != build_k2b_world(s, phi) BY CONSTRUCTION -- two independent streams cannot reproduce one stream's sequence -- so that check is reported EXPECTED-DIFFERENT; the substantive equivalence test is C1', which demands the law, not the seeds |
| RN-P3B-3 | k2b's unused _zeta draw (k2b:324, 'stream order') is placed in the AUTHOR stream, preserving k2b's relative order among author draws; it is unused so it can affect only stream position, which is what 'preserves the sequence' means |
| RN-P3B-4 | loadings is drawn from the AUTHOR stream so an A/B pair shares its orthonormal basis bit-identically -- the trap P3 named; C2c proves it per probe pair |
| RN-P3B-5 | the b-only truth is w_mu*trait + w_common*common and A/B share author_seed, so B's trait is bit-identical to A's and the refreshed truth is exactly 'A's persons carrying B's frame'; checked in C2a, not assumed |
| RN-P3B-6 | R_deframe uses K-R1's transcription of K1b's ESTIMATED de-framing (mu_hat_field at k1b_literal/per_context, then deframe_panel) on A's panel scored against A's truth; its stride is measured and pinned in Part 0 before any measurement world, and it is descriptive and ungated |
| RN-P3B-7 | NULL-first classification per #55 and P3's registration; the equivalence band and the V-P3c floor are computed from realized pilot noise (df-inflated) and written before the main arms |
| RN-P3B-8 | R_nat, R_refresh and R_deframe at a world index share ONE corpus string, so P1's label noise cannot enter a within-world contrast; across phi the tag differs by necessity and the label note applies only to the distributional C1' anchor |

## 10. Rule events

- **Rule 13:** not reached — no verdict boundary exists without a measurement.
- **Rule 25:** fired as designed; this is the gate that stopped the leg.
- **Rule 26:** no bounded winner.
- **Rule 27:** the g_ratio budget is what rule 25 projected against; unmet at
  both the registered and the escalated size.
- **Rule 29:** the domain-pinned predicate ran on BOTH scorings at both pilot φ.
- **Rule 30:** every cited constant read from its persisted source; the
  provenance table is generated from the extraction's own line map.

## 11. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.
3. **A-3 (a wrong claim in my own draft, caught before the verdict).** The first
   draft of this harness asserted that the split builder would differ from k2b
   on *every* object at equal seeds. It does not: the author half matches
   bit-exactly (§1.2). The assertion was replaced with a generated per-object
   comparison before any gate consumed it, and the finding is stronger than the
   claim it replaced. No number changed.

| quantity | value |
|---|---|
| machinery | kr1.mu_hat_field(donor_channels='k1b_literal', pool_scheme='per_context') then kr1.deframe_panel -- K-R1's transcription of K1b's A4 into this world family |
| cost per pair, plain | 0.5978600978851318 |
| cost per pair, with de-framing | 0.9944519996643066 |
| stride pinned in Part 0 | 1 |
| status | not exercised on measurement worlds -- the leg stopped first |

R_deframe's stride was measured and pinned at 1 in Part 0
(plain 0.5978600978851318 s/pair, 0.9944519996643066 s/pair with de-framing), so the
secondary reading would have run on every measurement world had the leg
reached them.

## 12. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

## 13. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 (extraction + provenance + C2) | 180 | 2.010 |
| pilot (C3 + bands) | 60 | 7.950 |
| project (G3) | 30 | 0.003 |
| arms (5) | 260 each | -- not reached |
| fit | 180 | -- not reached |
| finalize | 60 | 0.000 |

---

*Artifacts: `results/m4_p3b_refresh_gradient/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `decision.json`,
`prose_facts.json`, `report_tables.md`, `run_log.jsonl`. Harness:
`scripts/run_suica_m4_p3b_refresh_gradient.py`.*
