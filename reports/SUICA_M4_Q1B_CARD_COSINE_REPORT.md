# SUICA M4-Q1b — the cross-frame card cosine — **CARD_CARRIES_IDENTITY_BEYOND_TRAIT**

**Outcome: CARD_CARRIES_IDENTITY_BEYOND_TRAIT (routing cell 4); modifiers: none.**
CARD_CARRIES_IDENTITY_BEYOND_TRAIT -- the card transports author-stream content the trait does not span

**Pooled Δ = 0.012246206730484502 [0.012053582696489028, 0.012435850463701492] → POSITIVE** (ε_pooled =
0.0003503781564720198); per φ: 0.016075551641115206 [0.0158578307774135, 0.01630324747462172] → POSITIVE and 0.008416861819853795
[0.008103920437714027, 0.008729420310343553] → POSITIVE (ε_per-φ = 0.00039640763267361027). 1536 worlds
(384 A/B pairs per φ).

> ## ⚠ The slug's stated consequence is contradicted by this leg's own arithmetic
>
> Cell 4 says the card "transports author-stream content the trait does not
> span". **It does not.** The registered Δ scores each card's fidelity against
> the UNCENTRED trait, but the card contains the CENTRED trait
> (`full = w_mu·trait_c + …`, k2b:423). Against the reference the cards
> actually share, the per-author exact identity gives
> **Δ = -0.0001656789003926287 [-0.0003650943244942132, 3.669093307965161e-05] at φ = 0.05 and 7.851116734077825e-05
> [-0.0002247934983222993, 0.0003875548092894414] at φ = 0.98 — both straddling zero (UNDERPOWERED /
> UNDERPOWERED)**, i.e. **CARD_PURE_TRAIT**, the opposite cell.
>
> The registration is binding, so the literal reading routes and the slug
> stands as registered. But the entailment it asserts — "Δ POSITIVE is entailed
> to be author-stream content beyond the trait — no other shared channel
> exists" — is false: **no other channel is needed.** The trait channel alone
> produces Δ > 0 once the reference object is the uncentred trait. This is
> raised as the leg's primary registration-defect candidate (§3), and it was
> found on probe pairs and pinned as RN-Q1B-6 **before any measurement arm
> ran**.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_Q_TRANSPORT_LINE_PLAN.md` BEFORE run (commit 527d176). Every
number below is generated from artifacts by code (rule 24).

---

## 1. The question, and why it is not degenerate

Q1 failed because the object it swapped was shared by construction. **Here
nothing is swapped.** cos_AB, r̂_A and r̂_B are measurements of three *different*
vector pairs, and A's and B's cards genuinely differ because `slow`, `noise` and
`int` are frame-stream objects. C2a certifies that A and B share **only** the
author stream, so any excess of cos(A,B) over the trait-predicted product
r̂_A·r̂_B is author-stream content the trait does not span.

| clause | quantity | value |
|---|---|---|
| (a) card_A != card_B | every author of every probe pair differs | True |
| (a) | smallest per-author norm delta over all probes | 0.3250575821476801 |
| (a) probe 0 | n_authors 565, Frobenius | 12.152812714035603 |
| (a) probe 1 | n_authors 565, Frobenius | 12.079379317088529 |
| (a) probe 2 | n_authors 565, Frobenius | 12.064956849348473 |
| (a) probe 3 | n_authors 565, Frobenius | 12.121743167333141 |
| (b) control pair (SANITY ONLY) | cos_AB | 1.0 |
| (b) | expected cos_AB | 1.0 |
| (b) | Delta | 0.39327233738428 |
| (b) | expected 1 - r_A*r_B | 0.39327233738428 |
| (b) | Delta > 0 by construction | True |
| (b) | status | OPERATOR SANITY ONLY -- excluded from every band, projection and verdict (RN-Q1B-3) |
| (c) vectors contract to k2b | full_n | True |
| (c) | b_raw_n | True |
| (c) | full_b_dot_raw | True |
| (c) | r_cos_raw | True |
| (c) | meaning | the 64-dim vectors this leg forms contract EXACTLY to the columns k2b's own card_channel_frame emits -- so the cosines below are built from k2b's cards, not a lookalike |

card_A ≠ card_B for **every author of every probe pair** (True;
smallest per-author norm delta 0.3250575821476801), proven before any statistic
was read. The same-frame-seed control returns cos_AB = 1.0 and
Δ = 0.39327233738428 against the constructed expectation 0.39327233738428 — operator
sanity only, excluded from every band, projection and verdict (RN-Q1B-3). And
the 64-dim vectors this leg forms contract **exactly** to the columns k2b's own
`card_channel_frame` emits, so the cosines are built from k2b's cards.

## 2. Provenance

| property | value |
|---|---|
| instrument | `scripts/run_suica_m4_p3b_refresh_gradient.py` |
| instrument function sha256 | a7618a321752fc502d804745f2e83b7dd75af7e3f8a88868575c3afa632ed9bc |
| matches Q1's persisted | True |
| card path | `scripts/run_suica_m4_q1_card_transport.py:242` (`card_frame_xw`) |
| card path function sha256 | 4288aea0dce09fd9d2cbeef5f4cb5207e2f86a82742c080c1824591a971430d4 |
| card path proven bit-exact in Q1 | True |

| quantity | value |
|---|---|
| Q1 verdict | INEXPRESSIBLE |
| Q1 zero-point identity PASS | True (16 checks) |
| closed-form pin | `scripts/run_suica_m4_k2b_t4_branch.py:533` |
| closed-form value | 0.8271784593117322 |
| measured pin | `scripts/run_suica_m4_k2b_t4_branch.py:392-457` |
| measured value | 0.8266850143926395 |
| **reading B (what r_A / r_B use)** | **r_card_b_raw (the ratio of sums, k2b:486)** |

## 3. The reference-object confound — the leg's central finding

RN-Q1B-6, pinned in Part 0 from probe pairs, before any arm.

The card is `full = w_mu·trait_c + w_slow·slow_c̄ + w_noise·noise_c̄`
(k2b:423-427). Its trait component is **trait_c, the cell-centred trait**. The
only content A and B share is exactly `w_mu·trait_c` — `slow`, `noise` and `int`
are frame-stream and independent between them. So the disattenuation identity
that actually holds is

    cos(card_A, card_B) = cos(card_A, trait_c) · cos(card_B, trait_c)

with the **centred** reference. But `r_card_b_raw` and `r_card_b_cos` both score
the card against `trait`, the **uncentred** array (k2b:443/446). Scoring against
an object the card does not contain understates each card's alignment with what
it *does* share, so r̂·r̂ understates cos_AB and Δ comes out positive with no
content beyond the trait involved.

| phi | reference object | reading | point | 95% CI | epsilon | class |
|---|---|---|---|---|---|---|
| 0.05 | UNCENTRED trait | Delta (registered, r_raw) -- ROUTES | 0.016075551641115206 | [0.0158578307774135, 0.01630324747462172] | 0.00039640763267361027 | **POSITIVE** |
| 0.05 | UNCENTRED trait | Delta_cos (estimator-consistent) | 0.01614789263012024 | [0.01593183467218937, 0.01636680140882964] | 0.00037960234789003285 | POSITIVE |
| 0.05 | UNCENTRED trait | Delta_author (per-author) | 0.012972844117430165 | [0.012762615580740657, 0.013189427872246159] | 0.0003803545458761034 | POSITIVE |
| 0.05 | **CENTRED trait (what the card contains)** | Delta_cen (pooled r_card_b_cen) | 0.002727561595391776 | [0.002520988540301667, 0.0029437575581971825] | 0.00035774025836172297 | POSITIVE |
| 0.05 | **CENTRED trait** | **Delta_author_cen (per-author EXACT)** | **-0.0001656789003926287** | [-0.0003650943244942132, 3.669093307965161e-05] | 0.00034729713852521863 | **UNDERPOWERED** |
| 0.98 | UNCENTRED trait | Delta (registered, r_raw) -- ROUTES | 0.008416861819853795 | [0.008103920437714027, 0.008729420310343553] | 0.00039640763267361027 | **POSITIVE** |
| 0.98 | UNCENTRED trait | Delta_cos (estimator-consistent) | 0.012168845775779426 | [0.011857960836265934, 0.012485838090611179] | 0.00037960234789003285 | POSITIVE |
| 0.98 | UNCENTRED trait | Delta_author (per-author) | 0.009741441150286911 | [0.00943087058737368, 0.010048565498250745] | 0.0003803545458761034 | POSITIVE |
| 0.98 | **CENTRED trait (what the card contains)** | Delta_cen (pooled r_card_b_cen) | -0.0014934107591163624 | [-0.0017980773699117377, -0.00117679001449999] | 0.00035774025836172297 | NEGATIVE |
| 0.98 | **CENTRED trait** | **Delta_author_cen (per-author EXACT)** | **7.851116734077825e-05** | [-0.0002247934983222993, 0.0003875548092894414] | 0.00034729713852521863 | **UNDERPOWERED** |
| — | — | the three UNCENTRED readings agree | — | — | — | True |
| — | — | **centred agrees with registered** | — | — | — | **False** |

The three UNCENTRED readings agree with each other (True) — so the
estimator-family ambiguity of RN-Q1B-1 turns out not to matter. What matters is
the **reference object**, and the centred readings disagree with the registered
one (False): the per-author exact form lands at -0.0001656789003926287 and
7.851116734077825e-05, both inside noise.

## 3b. The estimator ambiguity, pinned before any number

**RN-Q1B-1 is the methodological heart of this leg.** cos_AB is a *mean of
per-author cosines*. `pooled_card_stats` emits **two** card-vs-trait statistics
from the same frame: `r_card_b_raw` (a ratio of sums — Q1's "reading B", the one
appendix N quotes) and `r_card_b_cos` (a mean of per-author cosines — the *same*
estimator family as cos_AB). The disattenuation identity is a **per-author**
statement, so mixing families leaves a bias of unknown sign in Δ.

The registration says "Q1's reading B, `pooled_card_stats` lineage", which
literally names `r_card_b_raw`. That reading routes. Two alternatives are
computed at equal precision and reported:

| phi | reference object | reading | point | 95% CI | epsilon | class |
|---|---|---|---|---|---|---|
| 0.05 | UNCENTRED trait | Delta (registered, r_raw) -- ROUTES | 0.016075551641115206 | [0.0158578307774135, 0.01630324747462172] | 0.00039640763267361027 | **POSITIVE** |
| 0.05 | UNCENTRED trait | Delta_cos (estimator-consistent) | 0.01614789263012024 | [0.01593183467218937, 0.01636680140882964] | 0.00037960234789003285 | POSITIVE |
| 0.05 | UNCENTRED trait | Delta_author (per-author) | 0.012972844117430165 | [0.012762615580740657, 0.013189427872246159] | 0.0003803545458761034 | POSITIVE |
| 0.05 | **CENTRED trait (what the card contains)** | Delta_cen (pooled r_card_b_cen) | 0.002727561595391776 | [0.002520988540301667, 0.0029437575581971825] | 0.00035774025836172297 | POSITIVE |
| 0.05 | **CENTRED trait** | **Delta_author_cen (per-author EXACT)** | **-0.0001656789003926287** | [-0.0003650943244942132, 3.669093307965161e-05] | 0.00034729713852521863 | **UNDERPOWERED** |
| 0.98 | UNCENTRED trait | Delta (registered, r_raw) -- ROUTES | 0.008416861819853795 | [0.008103920437714027, 0.008729420310343553] | 0.00039640763267361027 | **POSITIVE** |
| 0.98 | UNCENTRED trait | Delta_cos (estimator-consistent) | 0.012168845775779426 | [0.011857960836265934, 0.012485838090611179] | 0.00037960234789003285 | POSITIVE |
| 0.98 | UNCENTRED trait | Delta_author (per-author) | 0.009741441150286911 | [0.00943087058737368, 0.010048565498250745] | 0.0003803545458761034 | POSITIVE |
| 0.98 | **CENTRED trait (what the card contains)** | Delta_cen (pooled r_card_b_cen) | -0.0014934107591163624 | [-0.0017980773699117377, -0.00117679001449999] | 0.00035774025836172297 | NEGATIVE |
| 0.98 | **CENTRED trait** | **Delta_author_cen (per-author EXACT)** | **7.851116734077825e-05** | [-0.0002247934983222993, 0.0003875548092894414] | 0.00034729713852521863 | **UNDERPOWERED** |
| — | — | the three UNCENTRED readings agree | — | — | — | True |
| — | — | **centred agrees with registered** | — | — | — | **False** |

**All three UNCENTRED readings agree in classification: True** — the
family ambiguity is immaterial here. The reference-object ambiguity of §3 is
not.

## 4. Bands and projection

| quantity | value |
|---|---|
| sd(Delta) raw / df-inflated | 0.002354077014917388 / 0.00388398572077988 |
| pooled df / inflation | 6 / 1.6498974741130894 |
| SE(mean Delta) per phi at 384 | 0.00019820381633680513 |
| SE(mean Delta) pooled at 768 | 0.0001751890782360099 |
| independence margin (#57) | 1.25 |
| margin applied to | the POOLED SE only -- Delta is measured fully paired per world-pair, so its per-phi SE needs no covariance; pooling across phi would, so the 1.25 margin is applied there and stated (RN-Q1B-4) |
| **epsilon_Delta per phi** | **0.00039640763267361027** |
| **epsilon_Delta pooled** | **0.0003503781564720198** |

Δ is measured **fully paired** per world-pair, so its per-φ SE needs no
covariance at all; the #57 independence margin of 1.25 is applied only to
the pooled SE, where pooling across φ would otherwise require one, and is
stated there (RN-Q1B-4). No pilot correlation is consumed anywhere.

| pairs/phi | truth | role | SE(mean Delta) | fires at 2 SE | bar | PASS |
|---|---|---|---|---|---|---|
| 384 (registered) | Delta = 0 | false-fire | 0.00019820381633680513 | 0.043 | 0.1 | True |
| 384 (registered) | Delta = 0.05 | power | 0.00019820381633680513 | 1.0 | 0.8 | True |

At the registered 384 pairs/φ the null truth fires at 0.043 (bar 0.1) and the
material truth Δ = 0.05 at 1.0 (bar 0.8). Escalation did not fire (False).

## 5. The result

| phi | n | cos_AB | SEM | r_A-hat | r_B-hat | r-product | **Delta** | Delta 95% CI | classification |
|---|---|---|---|---|---|---|---|---|---|
| 0.05 | 384 | 0.632268201660647 | 0.00016234422886292333 | 0.7849957079536791 | 0.7849607498235519 | 0.6161926500195318 | **0.016075551641115206** | [0.0158578307774135, 0.01630324747462172] | **POSITIVE** |
| 0.98 | 384 | 0.46555383131801814 | 0.0002271934972021797 | 0.6761133955568276 | 0.6761203395837816 | 0.45713696949816435 | **0.008416861819853795** | [0.008103920437714027, 0.008729420310343553] | **POSITIVE** |
| **pooled** | 768 | — | — | — | — | — | **0.012246206730484502** | [0.012053582696489028, 0.012435850463701492] | **POSITIVE** |

cos_AB sits at 0.632268201660647 / 0.46555383131801814 against a trait-predicted product of
0.6161926500195318 / 0.45713696949816435. The φ's agree (True).

### 5.1 The identity share, UNBUDGETED

| phi | identity share Delta / cos_AB | 95% CI | label |
|---|---|---|---|
| 0.05 | 0.025416789784261696 | [0.025077600856962534, 0.025769072556218135] | UNBUDGETED -- descriptive, routes nothing |
| 0.98 | 0.01804087613811507 | [0.017379655935083557, 0.018705196875479547] | UNBUDGETED -- descriptive, routes nothing |

Quoted as a point with an honest CI and the label UNBUDGETED — it gates nothing
and routes nothing (the P3b lesson, kept visible).

### 5.2 What the sign means, stated before the measurement

RN-Q1B-5, pinned in Part 0: Δ > 0 would mean the two cards agree more than their
separate trait-fidelities can explain. C2a makes the author stream the only
shared content, and in this arm `w["int"] = 0`, so the `a_load` carrier — the
one author-stream object that is not the trait — reaches the card through **no
channel at all**. The registration's own consequence-entailment therefore
*predicts* Δ = 0, and a POSITIVE Δ would have indicated something the channel
accounting does not contain.

## 6. Routing

| # | condition | outcome |
|---|---|---|
| 1 | G0/G1 failure | STOP / INSTRUMENT_DEFECT |
| 2 | projection fails after escalation | NON_PROJECTABLE |
| 3 | Delta NULL (both phi) | CARD_PURE_TRAIT -- cards are trait plus frame-independent noise; the disattenuation identity holds at card level; the taxonomy completes: cards read the trait, the gauge reads the frame |
| 4 | Delta POSITIVE (both phi) | **CARD_CARRIES_IDENTITY_BEYOND_TRAIT -- the card transports author-stream content the trait does not span**  <-- THIS LEG |
| 5 | Delta NEGATIVE (both phi) | ANTI_CORRELATED_NAMED -- new phenomenon; theory note |
| 6 | phi's disagree in classification | PHI_SPLIT -- named; the phi-dependence itself becomes the finding |
| 7 | any UNDERPOWERED (no higher cell) | UNDERPOWERED (levels reported) |

## 7. Gates

| gate | PASS | detail |
|---|---|---|
| G0q1b | True | Q1's record and both 0.827 objects, the instrument hashes, and the disattenuation lineage |
| G1q1b | True | card_A != card_B for every author of every probe pair; the control pair gives cos = 1 and Delta = 1 - r^2 > 0; the 64-dim vectors contract EXACTLY to k2b's own card columns |
| C2 | True | 4 fresh probe pairs |
| G2q1b | True | rule-29 predicate on cos_AB and Delta; bands from variances only with the 1.25 margin stated |
| G3q1b | True | escalation fired: False |

## 8. C2 battery

| check | objects | result |
|---|---|---|
| author objects bit-identical | trait, a_load, loadings | True |
| frame norm delta: slow | frame | [250.9008347322852, 251.44734863085804] |
| frame norm delta: slow_latent | frame | [1229.3310439265902, 1231.6967470617149] |
| frame norm delta: noise | frame | [250.7183606095927, 251.150662222092] |
| frame norm delta: common | frame | [15.705458204568243, 16.266630548760027] |
| frame norm delta: int | frame | [250.0021296894254, 252.00211674929088] |
| determinism | all objects | True |
| shared basis | loadings | True |
| **C2** | — | **PASS = True** |

## 9. The disattenuation lineage

| anchor | located at | verbatim quote (extracted by code, rule 24) |
|---|---|---|
| T8 / the disattenuated distinctive cosine | `docs/SUICA_IDENTITY_THEORY_V1.md:223` (para 202-230) | - (a) **Decomposition (law of cosines).** ‖c_i − c_j‖² = (r_i − r_j)² + 2 r_i r_j (1 − cos θ_ij). Raw deviation distance conflates **magnitude mismatch** with **direction mismatch** — the profile-similarity elevation/scatter/shape problem (Cronbach–Gleser), restated in card space. - (b) **Anti-direction bound.** cos θ_ij < 0 ⟺ ‖c_i − c_j‖² > r_i² + r_j². An opposite-direction pair is therefore ALWAYS farther from each other than either is from the norm (‖c_i − c_j‖ > max(r_i, r_j)). Contrapositive: if two people are mutually closer than either is to the group norm, their directions cannot be opposite; for r_i = r_j = r, mutual distance < r forces θ < 60°. **The feared case — "distance-close … |
| k2b's own attenuation prediction (the identity's card-side factor) | `scripts/run_suica_m4_k2b_t4_branch.py:577` (para 533-584) | def arm_predictions(share: float, phi: float, w_int_arm: str) -> dict[str, float]: lay = layout() counts = lay["counts"] sh = arm_shares(share, w_int_arm) A, Bv, C, E = sh["mu"], sh["slow"], sh["int"], sh["noise"] sizes = retained_cell_sizes() ar_set_var = k2a().ar_set_var ar_cross_cov = k2a().ar_cross_cov num_b = den_full = den_braw = den_bcen = 0.0 gnum = {p: 0.0 for p in CARD_PAIRS} gd1 = {p: 0.0 for p in CARD_PAIRS} gd2 = {p: 0.0 for p in CARD_PAIRS} for key, n_cell in sizes.items(): m = int(key.split("\|m")[1]) kap = 1.0 - 1.0 / n_cell v_full = ar_set_var(np.arange(m), phi) var_card = A + Bv * v_full + C / m + E / m num_b += n_cell * kap * math.sqrt(A) den_full += n_cell * kap * var_card… |
| the K3-era distinctive-cosine statement (K-line) | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md:2887` (para 2870-2903) | - **L-1 (anti-direction bound, T8b) [designed identity + noise law; prior .90]** — in TRUE cards: violation count of {cosθ<0 ∧ ‖c_i−c_j‖² ≤ r_i²+r_j²} is EXACTLY 0 (theorem; any violation = implementation defect → P1). In ESTIMATED cards: per-stratum violation rate within CI of the Part-0 MC prediction computed from the validated noise model (ρ-derived), ≥5/6 strata (2 configs × 3 norm strata). - **L-2 (caricature vs rotation, T7) [prior .80]** — generator-level per-author manipulations on a designated random 10% of authors: α-scaling (α ∈ {1.5, 2}) of mean_part vs norm-preserving rotation (φ_rot ∈ {30°, 60°}, random 2-plane through c_i). Leans: (a) scaled authors' rank-1 hit rate non-decrea… |

3/3 anchors located and quoted by code.

## 10. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G3q1b | power >= 0.8 at Delta = 0.05 and false-fire <= 0.1 at Delta = 0 | — | one-sided each |
| L-1q1b | PURE_TRAIT / IDENTITY_BEYOND_TRAIT / ANTI_CORRELATED / underpowered | 0.40 / 0.40 / 0.05 / 0.15 | categorical |
| V-Q1b | mean Delta vs 0, NULL-first, per phi and pooled | — | two-sided |

## 11. Pinned readings

| note | pinned reading |
|---|---|
| RN-Q1B-1 | cos_AB is a mean of per-author cosines; pooled_card_stats emits BOTH r_card_b_raw (ratio of sums, k2b:486 -- Q1's 'reading B') and r_card_b_cos (mean of per-author cosines, k2b:488, the same family as cos_AB). The disattenuation identity is per-author, so mixing families biases Delta. PINNED: the literal reading (r_card_b_raw) routes; Delta_cos and the per-author-exact Delta_author are computed and reported; disagreement in classification is the finding |
| RN-Q1B-2 | nothing is swapped here -- cos_AB, r_A and r_B measure three different vector pairs -- so Q1's identity-forcing failure cannot recur; card_A != card_B is re-proven per pair and per author before any statistic |
| RN-Q1B-3 | the same-frame-seed control gives cos_AB = 1 and Delta = 1 - r^2 > 0 by construction; it is operator sanity, excluded from every band, projection and verdict |
| RN-Q1B-4 | no pilot correlation is consumed (#57); Delta is computed fully paired per world-pair so its variance is measured directly, and the 1.25 independence margin is applied only where a covariance would otherwise be needed, and stated where applied |
| RN-Q1B-5 | Delta > 0 means the cards agree more than their trait-fidelities explain; C2a makes the author stream the only shared content, and with w['int'] = 0 the a_load carrier reaches the card through NO channel -- so the registration's own entailment predicts Delta = 0 and a POSITIVE Delta would indicate something the channel accounting does not contain |
| RN-Q1B-6 | THE CONFOUND, found on probe pairs before any arm: the card carries trait_c (CENTRED, k2b:423) but r_card_b_raw/r_card_b_cos score it against the UNCENTRED trait (k2b:443/446). The shared content is w_mu*trait_c, so the identity that holds uses the CENTRED reference; the uncentred reference understates each card's alignment with what it shares and forces Delta > 0 with no content beyond the trait. The registration's stated entailment therefore FAILS for the registered reference. The literal reading still routes (binding); r_card_b_cen (k2b:487, the same pooled_card_stats call) and the per-author centred form are computed with their own bands and reported at equal precision |

## 12. Rule events

- **Rule 13:** 0 boundary event(s); bootstrap B = 2000.
- **Rule 25:** the projection gate passed at the registered size.
- **Rule 26:** no bounded winner.
- **Rule 27:** the identity share is explicitly UNBUDGETED and carries the label.
- **Rule 29:** the domain-pinned predicate ran on cos_AB and Δ at both pilot φ.
- **Rule 30:** every cited constant read from its persisted source; the card
  path carries file, line and sha256, and was proven bit-exact in Q1.
- **#57:** no pilot correlation consumed; the 1.25 margin applied only where a
  covariance would otherwise be needed, and stated there.

## 13. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine; a CPython 3.12.12 venv was built outside the repo
   from `requirements-lock-main.txt` verbatim and pinned. Resolved BEFORE any
   hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 14. Environment

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

## 15. Timing

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 150 | 0.474 |
| pilot | 60 | 0.485 |
| project | 30 | 0.000 |
| arm p0.05_0_192 | 230 | 10.970 |
| arm p0.05_192_384 | 230 | 10.979 |
| arm p0.98_0_192 | 230 | 10.975 |
| arm p0.98_192_384 | 230 | 11.001 |
| fit | 180 | 0.045 |
| finalize | 60 | 0.000 |

---

*Artifacts: `results/m4_q1b_card_cosine/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `projection.json`, `arms/`, `fit.json`,
`decision.json`, `prose_facts.json`, `report_tables.md`, `run_log.jsonl`.
Harness: `scripts/run_suica_m4_q1b_card_cosine.py`.*
