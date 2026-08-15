# SUICA M4-S1 — the choice-enabled generator

**Outcome: `INSTRUMENT_DEFECT(C_S1a)`** (rule-16 cell 5). Modifiers: COUPLING_PLACED_GAMMA1_POSITIVE_GAMMA0_NULL, SIGNATURE_STABLE_AT_BOTH_GAMMA.

Registered before the run in `docs/SUICA_M4_S_SELECTION_LINE_PLAN.md` ("M4-S1",
commit 21149bb). EXPLORATORY, synthetic, label-free. **An instrument leg**: the
coupling measured here is one this leg BUILDS. Nothing in it is evidence about
real people, and no real-data claim is made or implied.

## 1. What this had to establish

The owner's conjecture is that the gauge reads frames, but which frames a person
*chooses* is person-owned — so selection-proximity should imply
personality-proximity. That claim decomposes into (a) selection is a person-stable
signature, and (b) selection-similarity implies trait-similarity. (b) is not a
theorem: it is a coupling strength, and it is false when selection is driven by
something other than traits. This leg builds an apparatus in which (b) can be
dialled — γ = 1 trait-driven, γ = 0 identity-driven — and certifies it.

**The leg routes to a handback on C-S1a — but the defect is in that certificate's specification, not in the generator.** C-S1a demands uniform *selection* and baseline *exposure* at the same β = 0, and those are different neutralities; §5.1 shows the level shift is the apparatus behaving correctly, and gives the one-line fix. Everything the line actually needs was established.

**The apparatus does what the conjecture needs it to do.** Selection is a stable per-person signature in BOTH arms — split-half r 0.5629870740710835 at γ = 1 and 0.5564373726309412 at γ = 0 — but it carries trait information ONLY when traits drive it: Mantel r 0.23983432331725474 at γ = 1 against -4.1883473632534314e-05 at γ = 0. That is decomposition (b) made physical: **a perfectly stable selection signature can be completely uninformative about personality.** Stability is necessary and nowhere near sufficient, and the γ = 0 arm is the falsifier the real-data track will need.

## 2. The structural question: is endogenous exposure expressible at all?

It nearly is not. `emit_panel` (3.12.12 run, k2b:359-381) gives author *i* the
frame object `common[ctx_index[i], o]` at **every** occasion — one context per
author, fixed by the frozen layout. Per-occasion choice cannot be expressed
through it, and k2b is read-only, so the registered fallback was
**INFEASIBLE_CHOICE**.

The licensed path is minimal extraction with provenance. `emit_choice`
transcribes `emit_panel` with **exactly one change**: the first index of the
common term (k2b:377) becomes `choice[i, o]`. Everything else — the trait site,
the slow term, the interaction, the noise, the weights, the loop — is the same
code. The shared-frame object per context is preserved exactly: `common[k, o]`
is still the single frame vector for context *k* at occasion *o*, handed to every
author who chooses *k* there. The author's **nominal** context (which the gauge
uses to pool authors into per-context fields) stays `lay["ctx_index"]`; only the
author's **realized exposure** is chosen. The model is: authors nominally belong
to a community and choose which contexts they actually engage.

The transcription is certified, not asserted:

| check | result |
|---|---|
| emit_choice panel bit-exact vs emit_panel (layout exposure) | **True** |
| emit_choice truth panel bit-exact | True |
| field agreement identical | 0.11118696412429328 vs 0.11118696412429328 → True |
| every v2 object bit-identical after adding the choice machinery | **True** |
|   per object | common=True, int=True, noise=True, slow=True, style=True, trait=True, trait_pure=True |
| emit_panel source | scripts/run_suica_m4_k2b_t4_branch.py:359-381 (emit_panel) |
| the ONE changed line | scripts/run_suica_m4_k2b_t4_branch.py:377 (the common term) |
| contexts | 4 — AskReddit, AskWomen, politics, worldnews |
| authors / retained / t_max | 985 / 565 / 16 |

Setting `choice[i, o] = ctx_index[i]` reproduces `emit_panel` **bit-for-bit**,
panel and truth panel alike, down to an identical field agreement. That is the
whole feasibility argument, and it is checked by code rather than by reading.

## 3. Pins

- **u and v** (RN-S1-2): first four principal author-coordinates of each channel
  — SVD of the author-centred channel matrix (`trait_pure` for u, `style` for
  v), right singular vectors 1..4, authors projected, each coordinate z-scored
  so β means the same thing in both channels. **Sign convention (#64)**: each
  component's sign is fixed so its largest-magnitude loading is positive. SVD
  signs are otherwise arbitrary and would silently randomize π across worlds.
- **The exposure stream** (RN-S1-3) is its own rng, drawn after the v2 builder
  returns, so every v2 object stays bit-identical — certified above.
- **The reference for C-S1a** (RN-S1-5): the registration says "the v2/M1c
  share-.25 row", and two different objects answer to that description. The
  routing reference is R2's persisted v2 arm at the identical configuration
  (share .25, φ .60, w_style 1.0) = 0.11806906162144237; M1c's no-style row (0.12714790436588774) is
  reported as lineage context and routes nothing.

## 4. β* — fixed by arithmetic, before any world

| item | value |
|---|---|
| **β\*** | **1.7** |
| declared criterion 1 | mean entropy ≤ 0.85 · log k |
| declared criterion 2 | median per-author χ²(3) power ≥ 0.8 at median m = 12.0 |
| realized mean entropy at β* | 0.8593617886843593 |
| entropy as fraction of log k | 0.6198984954321972 |
| median χ² power at β* | 0.8069427664188857 |
| grid searched | 0.05 … 6.0 |
| worlds used to fix β* | **none** — standard-normal arithmetic only |

## 5. Certificates

| certificate | PASS |
|---|---|
| C_S1a | **False** |
| C_S1b | **True** |
| C_S1c | **True** |

### 5.1 C-S1a — the neutral anchor

| clause | value | reference / band | result |
|---|---|---|---|
| anchor field level (β=0) | 0.09262907190295885 [0.07652910892609367, 0.10785388737580495] | R2 v2 arm share .25 / phi .60 / w_style 1.0: 0.11806906162144237 |  |
| deviation | -0.02543998971848352 | band 2·√2·SEM = 0.024972074968206703 (z = -2.8814248341250366) | **False** |
| selection frequencies uniform | mean χ² 3.0881948266373147 | crit95 7.8147279032511765, frac within 1.0 | **True** |
| M1c no-style lineage row (reported, not routing) | 0.12714790436588774 | sem 0.0017053615065044834 | context |
| paired diagnostic Δ (DOES NOT ROUTE) | -0.03191225113985062 [-0.05123843785467711, -0.011515406750239305] | choice path at β=0 minus the layout's own exposure, same worlds | diagnostic |

At β = 0 the field level is 0.09262907190295885 against the reference 0.11806906162144237 — a deviation
of -0.02543998971848352 against a 2·√2·SEM band of 0.024972074968206703 (z = -2.8814248341250366). **The level clause
FAILS.** The frequency clause passes cleanly (mean uniformity χ² 3.0881948266373147 against
a 95th percentile of 7.8147279032511765, every anchor world within).

The failure is robust, not marginal-by-luck. The deviation is -0.02543998971848352 against the
routing reference, -0.03451883246292889 against M1c's row, and -0.03191225113985062 [-0.05123843785467711, -0.011515406750239305]
against these same worlds' *own* layout exposure — a paired CI excluding zero.
It fails under the generous band (0.024972074968206703) and under the stricter reading of
"2·√2·SEM" as two sigma on the difference (0.017657923550317797): True.

**The cause is a conflict inside the certificate, not a fault in the generator.**
C-S1a asks for two different neutralities at once — uniform *selection* (π flat)
and baseline *exposure* (the level the panel has when every author sits in one
context). Those coincide only if mixing contexts leaves the field level alone,
and it does not: the deployed gauge pools authors by their nominal context to
estimate a per-context field, so spreading each author's occasions uniformly
across four contexts destroys exactly the coherence the gauge recovers. The
level drop is the apparatus working correctly.

Both readings of "β = 0" are therefore reported:

- **(A) uniform exposure** — the registration's explicit words. Level clause
  fails, as above.
- **(B) β = 0 as a no-op on the frame path** (`choice[i,o] = ctx_index[i]`).
  Level clause passes *exactly*: that is precisely what Part 0's transcription
  certificate demonstrates, bit-for-bit.

The handback is small and concrete: either define the neutral anchor as (B), or
keep (A) and drop its level clause, since under (A) a level shift is predicted by
the mechanism the registration itself specifies. Nothing about the generator
needs to change — C-S1b and C-S1c both pass, and the anchor worlds' own
layout-exposure level (0.06071682076310822) sits within 6.495921300701515 SEM of the reference,
confirming the worlds are sound.

### 5.2 C-S1b — the signature

| arm | χ² fraction exceeding 95th | split-half r | entropy frac | result |
|---|---|---|---|---|
| gamma1 | 0.06460176991150442 [0.06025073746312685, 0.06843842182890854] | 0.5629870740710835 [0.5556645865206762, 0.5703783652507874] | 0.6206019143671101 | **True** |
| gamma0 | 0.06718289085545723 [0.0633480825958702, 0.07123893805309735] | 0.5564373726309412 [0.5477653655574023, 0.5647096208307433] | 0.6200953845046425 | **True** |

Realized frequencies track π within multinomial noise (0.06460176991150442 of authors
exceed the 95th percentile of χ²(3) at γ = 1, 0.06718289085545723 at γ = 0 — against 0.05
expected), and the signature is split-half stable in both arms.

### 5.3 C-S1c — the coupling placement

| arm | Mantel r (selection-sim vs trait-sim) | CI95 | test | result |
|---|---|---|---|---|
| γ = 1 | 0.23983432331725474 | [0.23709290162316124, 0.24284340944183067] | POSITIVE iff CI low > ε = 0.010125436066679785 | **True** |
| γ = 0 | -4.1883473632534314e-05 | [-0.001165090846688084, 0.001053439915639846] | ZERO iff CI ⊂ ±ε = 0.010125436066679785 | **True** |
| separation γ1 − γ0 | 0.23987620679088728 | - | - | - |
| γ = 0 signature still stable | 0.5564373726309412 | - | split-half r > 0 | **True** |

Mantel r is 0.23983432331725474 [0.23709290162316124, 0.24284340944183067] at γ = 1 and -4.1883473632534314e-05 [-0.001165090846688084, 0.001053439915639846] at γ = 0, against an
equivalence band ε = 0.010125436066679785 built from permutation arithmetic (permutation sd
0.0022344399846873217). Separation 0.23987620679088728.

**This is the certificate that matters for the line.** The γ = 0 arm has a
selection signature just as stable as the γ = 1 arm (split-half 0.5564373726309412 vs
0.5629870740710835) and carries no trait information at all. Stability of selection is
therefore *not* evidence for the conjecture — the real-data track will need the
coupling measured directly, because (a) can hold perfectly while (b) fails
completely.

## 6. Projection

| truth | role | bar | P | PASS |
|---|---|---|---|---|
| gamma=0 (false-fire) | false-fire | 0.1 | 0.0 | True |
| gamma=1 (detection) | power | 0.8 | 1.0 | True |

## 7. Anomalies

1. **A-1 (before any number).** The pinned interpreter's virtualenv was
   partially destroyed between legs — a temp reaper deleted files under
   `/private/tmp` at 00:00, removing `pyvenv.cfg` and gutting `site-packages`
   (package directories survived, their `__init__.py` files did not, so `numpy`
   imported as an empty namespace package). Rebuilt from
   `requirements-lock-main.txt` and verified to match the versions the previous
   legs ran under (numpy 2.4.4, pandas 3.0.2, Python 3.12.12) before any
   S1 number was computed: `/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv2/bin/python`.
2. **A-2 (before any number).** `timeout(1)` is absent on macOS; every stage ran
   as its own foreground command under an explicit tool timeout.
3. **A-3 (before any number).** The feasibility of the exposure reallocation was
   settled by construction and certified bit-exactly before any certificate was
   evaluated, so INFEASIBLE_CHOICE was ruled out on evidence rather than by
   assumption.

## 8. Boundary

EXPLORATORY, synthetic, label-free. **The coupling is installed, not
discovered**: γ is a knob this leg turns, so C-S1c is a statement that the
apparatus works, not that selection predicts personality in any real corpus.
24 worlds per γ arm, 8 anchor worlds, 985 authors each
(565 retained). One share, one φ, one dose, four contexts. The quantitative
law is S2's; this leg deliberately used generous certificate bands.

## 9. Environment

`/private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv2/bin/python` — Python 3.12.12.
