# SUICA M4-K1b — Ownership of the composition effect: author-reading or frame-amplification?

Tier: **EXPLORATORY, label-free, synthetic.** Registered in
`docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md`, section "M4-K1b — Ownership of the
composition effect" (REGISTERED 2026-08-09, BEFORE RUN, commit `678b25a`;
P3's binding consequence). Theory under test: `docs/SUICA_IDENTITY_THEORY_V1.md`
§3 T3, dated appendix C (C.3 the F2 ownership annotation, C.4 T6″). Ledger row
`M4-K1b`. Script: `scripts/run_suica_m4_k1b_composition_ownership.py`.
Artifacts: `results/m4_k1b_composition_ownership/`.

Executor's standing: implementation and execution only. The registration text
is binding; everything below labelled "register-note" is an operationalization
of something the registration left as an implementation choice, or a standing
rule 9 instrument resolution, fixed and written here **before** any arm stage
ran.

---

## 0. Part 0 — gates and register-notes, written before any arm

**Part-0 gates computed 2026-08-09 (stage `part0` wall-time 29.1 s; stage
`part0_supp` 14.0 s), persisted in
`results/m4_k1b_composition_ownership/gates.json`.**
**This section was written to disk before the `arms_a`, `arms_b` and `sec`
stages were invoked. No number from the 32 adjudicated worlds existed at that
moment** — the only compute that had touched the deployed gauge was the
registered reserved-seed pilot (G3b, worlds 9101–9104) and the registered
liveness worlds (G4b, worlds 9201–9208), all of them Part-0 objects that are
never adjudicated.

### G0 — dims pinned to K1's, verified at the fresh seeds

Extracted from `results/m4_f1_panel_sizing/realtext_panel_reference.json`
through `f2.build_layout_common` (`scripts/run_suica_m4_f2_composition.py:205-222`)
and compared field-by-field against `results/m4_k1_issuer/gates.json` G0:

| pinned quantity | K1 | K1b | match |
|---|---|---|---|
| authors / world | 985 | **985** | ✔ |
| events allocated / world | 12,784 | **12,784** (raw 13,202) | ✔ |
| events / author multiset | {8:272, 12:200, 16:513} | **{8:272, 12:200, 16:513}** | ✔ |
| contexts | AskReddit, AskWomen, politics, worldnews | same 4 | ✔ |
| retained by the deployed gauge | 565 | **565** | ✔ |
| knobs | `k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80` | same (read from F1's `calibration_record.json`) | ✔ |

Fresh-seed structural check: world 0 of seed group `main`
(`world_seed = 7170869388831501161`) generated and every author's event block
verified at shape `(m_i, 64)` — generation only, no gauge. **G0 PASS.**

**Grain (rule 5).** The unit of the primary question is the **per-world paired
design contrast**; 32 worlds are the sample; authors are nested inside a world
and enter only through the gauge's own aggregation. The secondary question's
unit is the per-author probe card, authors nested in 8 worlds (K1's grain).
Justified against G3b's MDE below.

### G1b — K1's anchors re-derived bit-exactly, before any new arm

Reloaded `results/m4_k1_issuer/rel_cells.csv` and
`results/m4_k1_issuer/abs_probe_correct.npz` and re-derived through F2's own
`_paired_ci` (`f2:1008-1025`) and K1's own pooling:

- **L5 1×** (shared design, shifted − unshifted): mean
  **+0.09254304863282958**, sd 0.041580915483140586, se 0.014701073653036707,
  t = 6.294985714442261, CI [0.05778053334840726, 0.1273055639172519], n = 8.
  Every field `==` the persisted `decision.json` value (bit-exact, not within
  tolerance); rounds to the registration's quoted +0.092543049.
- **L2** (free design, reader B, oracle − est8): **+0.09695431472081219**,
  `==` the persisted pooled mean and `==` the registration's quoted value.

**G1b PASS.**

### G2b — surgical verification, and the designed identity it exposes

Two pilot worlds (9301, 9302), both designs, on the full 985-author layout.
The generator's three additive channels are recomputed exactly (line-for-line
mirror of `f2:151-197`, using f2's own `_orthonormal_loadings`,
`occasion_labels` and `shock_vector`), and:

| check | shared | free |
|---|---|---|
| three-channel reconstruction residual, max abs per event | **0.0** | **0.0** |
| subtraction vs twin generation (common channel zeroed), max abs | **1.11e-16** | **1.11e-16** |
| removed channel's spread across authors sharing a (context, occasion) | **0.0** | n/a |
| twin(shared) vs twin(free) at identical seeds, max abs | **0.0** | — |

Identical on both worlds. Additivity holds at 1e-12 by four orders of
magnitude → **the registered PRIMARY path is used: exact pre-map subtraction of
the generator's own common channel.** The pre-registered fallback (twin
generation) does not fire; P4b does not fire. **G2b PASS.**

**The identity this gate exposes, stated before any arm.** `occasion_mode`
enters `f2.generate_world_composed` at exactly one place — `labels =
occasion_labels(counts, occasion_mode)` (`f2:180`), whose only consumer is the
common-shock fill (`f2:184-193`). At κ = 1.0, `blended_x = math.sqrt(max(0.0,
1.0 - 1.0)) * x + math.sqrt(1.0) * shock_x` is **exactly** `shock_x` (`f2:195`),
so the author channel (`f2:178`) and the noise channel (`f2:197`) do not depend
on the design at all. **Removing the common channel therefore makes the shared
and the free panel the same panel** — measured here as
`twin(shared) − twin(free) == 0.0` exactly. Consequently the registered
`Δ1 = A1 − A3` is **identically zero by construction**, and the registered share
`Ŝ = (Δ0 − Δ1)/Δ0` is **identically 1**. This is a property of F2's generator,
not a measurement, and it holds for *any* operationalization of "remove the
common structure": deleting the channel gives the identity above, and
"de-commonizing at preserved variance" is literally F2's own free design, which
gives `A1 ≡ A2` and again `Δ1 = A1 − A3 = A2 − A3 = 0`. The registered
decomposition cannot separate a frame-amplification share from a
jurisdiction-alignment share in this generator. The arms still run exactly as
registered, the leans are still adjudicated mechanically by the registered
rules, and the degeneracy is reported as the leg's principal structural
finding — see register-notes R-0.2 and R-0.3.

### G3b — power (rule 2), reserved 4-world pilot

Pilot worlds 9101–9104, seed group `pilot`, never adjudicated. Per-world
`Δ0 = A0 − A2` and `Δ1 = A1 − A3` computed through the full deployed gauge:

- pilot Δ0: 0.019942440940295056, 0.025473401164121102, 0.003003561340634748,
  0.009783692454312615
- pilot Δ1: 7.11e-17, −2.13e-17, 6.94e-17, 2.15e-17 — **the designed identity
  above, confirmed end-to-end through the gauge on reserved seeds**
- sd of per-world (Δ0 − Δ1): **0.010073679288543762**
- 80 %-power multiplier at n = 32: t(.975,31) + t(.80,31) = 2.8928837420933524
- **MDE(80 %, α = .05, paired t, n = 32) = 0.005151623455652202**

Requirement MDE ≤ **0.0130816**: **PASS** (2.5× inside the bar). The
aspirational resolution 0.0065408 is **also met**. No escalation to 64 worlds;
no tiering of claims to a degraded resolution. **G3b PASS.**

### G4b — channel liveness (rule 3), and a registration defect in its CI clause

*As registered* (3 fresh worlds 9201–9203, shared design, K1's own 1× pre-map
common shift, `k1:368-386` verbatim):

- per-world Δagreement: +0.12732063123746168, +0.039706652998214846,
  +0.07505666220469298 — **3/3 positive**, mean **+0.0806946488134565**
  (K1's persisted 1× value: +0.09254304863282958)
- paired-t CI at n = 3: **[−0.02880180392831297, +0.19019110155522598]** —
  does **not** exclude 0 → **the registered CI clause FAILS**
- shift calibration σ = 0.0805664376642747; author-deviation RMS at the
  response level 0.08030088223924457
- native common channel RMS **0.06849558941675903** over distinct (context,
  occasion) pairs (0.06819126976086362 event-weighted) → ratio to the
  author-deviation RMS **0.8529867606271943 ∈ [0.5, 2]** → the
  scale-comparability premise **holds**

**Registration defect, recorded not repaired (and detected before any arm).**
The clause "sign + CI excluding 0" at n = 3 is **unsatisfiable at the anchor's
own effect size**: with K1's persisted per-world sd 0.041580915483140586, the
n = 3 paired-t half-width is **0.10329** > the anchor mean 0.09254304863282958.
An exact reproduction of K1's L5 result would have failed this gate. The
smallest n at which the clause becomes satisfiable at the anchor is **n = 4**.

**Pre-declared remedy, fixed here before any arm:** read the same gate at the
**anchor's own n = 8** (K1's L5 design), a target fixed by the anchor's
arithmetic rather than by running until the gate passes. Worlds 9204–9208 added
to the three registered ones:

- per-world Δ: +0.12732063123746168, +0.0397066529982148, +0.075056662204693,
  +0.08608902621350671, +0.055145861004543356, +0.06074372438436322,
  +0.13709075085161906, +0.2227748074368826 — **8/8 positive**
- mean **+0.10049101454141054**, sd 0.05999736567293886, t = 4.7373998530470285,
  **CI [+0.0503319615961654, +0.1506500674866557]** — excludes 0

**Verdict: the registered G4b FAILS its CI clause at n = 3 and PASSES every
other clause; the supplementary reading at the anchor's own n = 8 passes
outright.** The registration attaches no stop or pivot to G4b, and rule 3's
purpose — never to interpret a null on an inert channel — is served: the
amplification channel is live at these fresh seeds, at 8/8 positive signs and a
point estimate within 9 % of K1's. The leg proceeds; both readings are reported
everywhere G4b is cited.

### G5 — hygiene

`results/m4_k1b_composition_ownership/manifest.json`: master_seed **20260811**;
seed recipe `v8.stable_bucket(f'{MASTER_SEED}-{group}-w{world}-{knob_tag}',
salt='m4k1b-world', modulus=2**63-1)` — the same recipe `f2.run_axis1_world`
computes internally (`f2:288-291`), so every arm of a world shares one world
seed and the design contrasts are exactly paired. Groups: `main` (worlds 0–31,
all seven arms), `pilot` (9101–9104, reserved), `g2b` (9301–9302), `g4b`
(9201–9208), `abs` (0–7, the secondary question). A4's norm pool:
`stable_bucket(f'{world_seed}-normpool', salt='m4k1b-normpool')`. Shift arms
reuse K1's own `stable_bucket(f'{world_seed}-{occasion_mode}',
salt='m4k1-shift')`. Bootstrap seeds are listed per statistic in the manifest.
All stages foreground with explicit timeouts; **zero background jobs, zero
monitors, zero sleep-and-poll**. **G5 PASS.**

**Part-0 stage estimates, for the registration's stop-at-2× rule:** `arms_a`
≤ 300 s, `arms_b` ≤ 800 s, `sec` ≤ 200 s, `finalize` ≤ 120 s.

---

### Part-0 register-notes (fixed before any arm)

**R-0.1 — standing rule 9: which channel is "the generator's own common
channel".** The registration names the removed channel two ways that pick out
**different objects** in F2's generator:

- by **semantics** — "common structure", "shared arms contain NATIVE common
  structure", arm A1 = "shared, common structure REMOVED", and L-b reading Δ1
  as the *surviving jurisdiction-alignment share* — the occasion-level content
  shared across authors, which at κ = 1.0 is the state slot
  `math.sqrt(w_x) * a * ((shock_x * g) @ loadings.T)` (`f2:195-196`), carried at
  weight √w_x with w_x = 0.15;
- by **name** — "(w_mu = 0.15 — the same scale class as the author channel
  w_x = 0.15)" and the fallback "twin generation with **w_mu = 0**". In the code
  `w_mu` weights `mean_part = math.sqrt(w_mu) * a * ((z * g) @ loadings.T)`
  (`f2:178`), which is **per-author and constant across occasions** (broadcast
  at `f2:197`) — the AUTHOR channel, not a common one. At κ = 1.0 the author's
  own AR(1) state is fully replaced by the shock (`f2:195`), so w_x is not "the
  author channel" either.

**Decision rule, written before any hypothesis-relevant number existed:** the
registered arm is the **semantic** one — A1/A3 remove the occasion-common
channel — because the lean texts (L-b's "jurisdiction-alignment share", L-c's
free-design specificity) are only coherent under that reading. The literal
`w_mu` reading is computed in full as a **disclosed second reading** (R-0.3),
adjudicating nothing. Standing rule 9 requires all readings; both are reported
for every cell. (The literal fallback "twin generation with w_mu = 0" is in any
case not runnable as stated: `f2:159-160` raises unless the three variance
shares sum to 1, so zeroing w_mu would require renormalizing — i.e. changing
the other channels — which exact subtraction avoids.)

**R-0.2 — the registered decomposition is degenerate in F2's generator.**
Derived in G2b above and verified there at machine precision, before any arm:
`Δ1 ≡ 0`, `Ŝ ≡ 1`, for any removal of the common channel. Consequences fixed in
advance: (i) L-a, L-b, L-e and P2b are still adjudicated **mechanically** by
their registered rules on the measured numbers — no rescue, no re-scoping;
(ii) every statement of Ŝ in this report carries the words "by construction";
(iii) the leg's answer to the *question* ("author-reading or frame
amplification?") is carried by the disclosed second reading below, which is the
only arm in the design capable of dissociating the two.

**R-0.3 — the disclosed second reading (A1′, A3′), and what it measures.**
A1′/A3′ subtract the **author channel** `mean_part` (`f2:178`) instead, at the
same seeds, leaving worlds whose only structured content is the occasion
channel plus iid noise — i.e. **no author identity at all**. `Δ1′ = A1′ − A3′`
is then the shared-minus-free composition contrast in a world containing no
author to read:

- Δ1′ ≈ Δ0 → the composition effect needs no author content → it is
  **frame-owned** (K1-L5's amplification mechanism operating on native
  structure);
- Δ1′ ≈ 0 → the effect requires the author channel → the shared design is
  improving **author reading** (common-mode rejection of the occasion content
  by the gauge's between-author centering, `v8:376-382`).

Reported quantities: Δ1′ with CI and sign count, `Δ0 − Δ1′` (the author-reading
share in absolute units), `(Δ0 − Δ1′)/Δ0` and `Δ1′/Δ0`. These adjudicate no
registered lean and fire no registered pivot; they are the disclosed reading
demanded by standing rule 9, and they are labelled as such wherever they appear.
They must **not** be relabelled "jurisdiction-alignment share": under this
reading a surviving Δ1′ means the opposite of what L-b's Δ1 would have meant.

**R-0.4 — A4's estimated norm.** "Per-occasion μ̂(o) from 32 disjoint authors'
responses": the generator's shock is per **(context, occasion)** (`f2:120-126`),
so a norm is only defined within a context (K1's R-0.3 made the same call).
A4 therefore uses **32 disjoint authors per context** (128 in total), each
observed on the full shared occasion grid (16 occasions), generated in a
**separate** generator call at
`stable_bucket(f'{world_seed}-normpool', salt='m4k1b-normpool')` — separate
because appending authors to the panel's own call would shift the RNG stream and
change the panel, breaking the pairing with A0. Their own occasion channel is
replaced by the **panel's** exact common channel `C(c, o)` so that they carry the
same frame the panel carries; what they contribute beyond it is their own author
means and noise. μ̂(c, o) is their per-occasion mean; A4 subtracts μ̂ event by
event. Disclosed consequence of the separate call: the norm authors' author
effects live in their own loadings realization, which changes nothing about the
magnitude of the estimation error (the quantity L-e prices) but is not the same
48-dim subspace as the panel's.

**R-0.5 — arms and pairing.** All seven arms of a world (A0, A1, A2, A3, A4,
A1′, A3′) share one world seed and one corpus tag, so the deployed gauge's
half-split indices (`f1:235-247`, seeded by corpus × author × draw) are
**identical across arms** — every contrast is exactly paired at the draw level,
as F2's own axis-1 cells were (`f2:948-950`, one `seed_group` for all cells).
20 draws per world, F2's `MIN_RETAINED_EVENTS = 8` floor, the deployed gauge
path unchanged.

**R-0.6 — the secondary question's two readers.** K1's R-abs construction
verbatim (`k1:150-250`): 985-author panel, 8 occasions/author drawn from a
common universe of 64, one context, free design, 8 worlds (indices 0–7 of the
32, seed group `abs`). The norm pool is **1024** authors per world, split into
two **disjoint** 512-author sub-pools P_a, P_b:

- **reader A** (K1's T3(c)-hypothesis reader, one norm shared across the two
  occasion halves): oracle norm = mean(P_a); est8 norm = mean(P_a[0:8]);
- **reader A′** (frame-refreshed): the gallery half uses a norm from P_a and the
  probe half an **independent** norm from P_b — oracle: mean(P_a) vs mean(P_b);
  est8: mean(P_a[0:8]) vs mean(P_b[0:8]).

Pool size 1024 rather than K1's 512 is forced by A′: the oracle arm also has to
be frame-refreshed, or L-d's second clause ("oracle rank-1 moves < 0.01 between
A and A′") would be vacuous by construction. Both sub-pools are 512, so the
oracle norm quality matches K1's exactly. Contrast tracked, as registered:
rank-1(est8) − rank-1(oracle) under each reader, pooled by K1's own
author-stratified bootstrap (`k1:832-854`, 2000 draws, authors resampled within
world, worlds as strata).

**R-0.7 — aggregation.** Registered rule: 32 worlds; per-world signs clean
≥ 26/32, qualified ≥ 21/32, else fail; pooled paired bootstrap 2000 draws, 95 %
percentile CI. Implemented as a **world-level paired bootstrap**: world indices
are resampled with replacement, all arms of a resampled world travel together,
2000 draws, percentile interval. F2's own paired-t interval (`f2:1008-1025`) is
computed for every contrast and reported alongside as a second reading. Ratios
(Ŝ, R_est/R_or, Δ1′/Δ0) are formed **inside** each bootstrap draw from the same
resampled worlds. **G1's overlap verdict is taken on the registered bootstrap
CI**; the paired-t CI is reported and any disagreement between the two readings
is disclosed.

**R-0.8 — G4b's power remedy** is declared in G4b above: the target n = 8 is
fixed by the anchor's own sd before the extra worlds ran, and the registered
3-world reading stands as the registered gate.

**R-0.9 — what is *not* being done.** No re-run of a failed arm, no seed
search, no escalation beyond the one G3b pre-authorizes (not needed), no
alteration of the deployed gauge, no writes to `suica_core/`. Results that fit
no registered branch will be reported as such.

**R-0.10 — anomalies and disclosures, with timing.**

1. **The channel-naming ambiguity (R-0.1)** was found while reading `f2:151-197`
   to write the subtraction, **before the script was first executed** — before
   Part 0, before the pilot, before any number existed. Resolved by the written
   decision rule in R-0.1, with both readings computed.
2. **The degeneracy of the registered decomposition (R-0.2)** was derived from
   the same code reading, **before any execution**, and then verified by G2b and
   by the reserved G3b pilot. It is a construction fact, not a result.
3. **The G4b CI-clause defect** was found when the registered gate returned
   `pass=false` in the Part-0 stage — i.e. before any of the 32 adjudicated
   worlds existed. The remedy's target n was computed from K1's persisted sd
   before the supplementary worlds ran.
4. **No smoke run touching the hypothesis channel preceded this Part 0.** The
   only pre-Part-0 executions were an import/availability check
   (`knobs_and_tag`, module attribute presence) and the Part-0 gates themselves.
   The construction checks that could have been a smoke test (three-channel
   reconstruction, twin equivalence, within-occasion constancy) are **inside**
   G2b, as the tightened convention requires.

---

## 1. Design as executed

Fresh `master_seed = 20260811`, **32 worlds**, F2's knobs
`k48-r0.50-mu0.15-x0.15-e0.70-p0.20_0.80`, κ = 1.0, F2's designs and the
deployed gauge unchanged, 20 draws per world, 565 authors retained per run
(constant across all 224 adjudicated runs).

| stage | cells | wall | Part-0 estimate |
|---|---|---|---|
| `part0` | G0, G1b, G2b, G3b (16 gauge runs), G4b (6) | **28.4 s** | — |
| `part0_supp` | G4b power remedy (10 gauge runs) | **13.3 s** | — |
| `arms_a` | A0, A2 × 32 worlds = 64 gauge runs | **75.1 s** | ≤ 300 s |
| `gate_g1` | the replication stop gate | **0.011 s** | — |
| `arms_b` | A1, A3, A4, A1′, A3′ × 32 worlds = 160 gauge runs | **185.7 s** | ≤ 800 s |
| `sec` | reader A vs A′, 8 worlds, R-abs | **1.3 s** | ≤ 200 s |
| `finalize` | adjudication | **0.3 s** | — |

**Total compute 303.9 s (5.1 min).** All stages foreground with explicit
timeouts, six worker processes on the gauge stages; **no background jobs, no
monitors, no sleep-and-poll**. No stage came near 2× its Part-0 estimate. Every
stage completed clean on its first attempt. Environment: Python 3.14.3, numpy
2.4.4, pandas 3.0.2, scipy 1.17.1.

### G1 — the replication gate (evaluated immediately after A0/A2, before anything else)

| quantity | value |
|---|---|
| A0 (shared, intact) pooled | +0.02324733090355507 |
| A2 (free, intact) pooled | −0.0009172094306603171 |
| **Δ0 = A0 − A2** | **+0.02416454033421539** |
| bootstrap 95 % CI (registered reading) | **[0.02115502110256099, 0.027207370259371894]** |
| paired-t 95 % CI (second reading) | [0.020951696576987606, 0.027377384091443174], t = 15.339651928839972, sd = 0.008911237576364854 |
| F2's persisted CI | [0.01953599084902978, 0.032790535764422674] |
| per-world signs | **32/32 positive (clean)** |

**Both readings overlap F2's interval; they agree. G1 PASS — F2's composition
effect replicates at fresh seeds and four times the world count.** P1b does not
fire. (Context, from persisted artifacts: K1's own 8 fresh-seed unshifted worlds
gave Δ0 = 0.023533094021404237, CI [0.015333957022132822, 0.031732231020675655].)

---

## 2. The registered decomposition, as measured

Per-world arm means, n = 32 worlds:

| arm | construction | pooled agreement |
|---|---|---|
| A0 | shared, intact | +0.023247330903555 |
| A2 | free, intact | −0.000917209430660 |
| A1 | shared, common channel removed (exact pre-map subtraction) | −0.000224758977851 |
| A3 | free, common channel removed | −0.000224758977851 |
| A4 | shared, ESTIMATED subtraction (32 disjoint authors/context) | +0.001092255420663 |
| A1′ | shared, AUTHOR channel removed — *disclosed second reading* | +0.046253703793940 |
| A3′ | free, AUTHOR channel removed — *disclosed second reading* | −0.000836899183804 |

| contrast | pooled | bootstrap 95 % CI | signs | band |
|---|---|---|---|---|
| Δ0 = A0 − A2 | +0.02416454033421539 | [0.02115502110256099, 0.027207370259371894] | 32/32 + | clean |
| **Δ1 = A1 − A3** | **−6.2680438096818225e-18** | [−2.499e-17, +1.249e-17] | 4 +/6 − | fail |
| Δ0 − Δ1 | +0.024164540334215393 | [0.021084538897884433, 0.027214453148165344] | 32/32 + | clean |
| **Ŝ = (Δ0−Δ1)/Δ0** | **1.0000000000000002** | [0.9999999999999994, 1.000000000000001] | — | — |

Largest per-world |Δ1| across the 32 worlds: **1.0061396160665481e-16**. This is
the designed identity derived and stated in Part 0 (§G2b, R-0.2), now confirmed
end-to-end through the deployed gauge on the adjudicated worlds: **A1 and A3 are
the same panel**, so Δ1 is zero as arithmetic, not as a null. Ŝ = 1 is therefore
**true by construction and carries no information about ownership.**

### Lean adjudications (mechanical, by the registered rules)

**L-a [prior .70] — HOLD.** (Δ0 − Δ1) bootstrap CI [0.021084538897884433,
0.027214453148165344] excludes 0, 32/32 signs (clean), and Ŝ = 1.0000000000000002
≥ 0.25. *Held by construction*: since Δ1 ≡ 0, this lean reduces to "Δ0 ≠ 0",
which is G1's replication statement. It carries no evidence about the
amplification share beyond that.

**L-b [prior .60] — MISS.** Δ1's CI is [−2.499102948238033e-17,
+1.2488653774317404e-17]; it does not exclude 0 on the positive side. *Missed by
construction*, for the same reason.

**L-c [prior .75] — HOLD.** A3 − A2 = +0.0006924504528088422, bootstrap CI
[−0.0012007858348831182, +0.002624154951447348], paired-t CI [−0.001352952697715,
+0.002737853603333] — inside the registered ±0.006540815826681557 by a factor of
2.5. Removing the occasion channel from the free design is **materially inert**,
as the specificity control predicted. (Per-world signs 18 +/14 − = "fail" by the
generic sign rule; L-c is an equivalence lean whose registered rule is the CI
containment only, and signs on a designed null are uninformative. Reported, not
scored.)

**L-e [prior .55] — APPLICABLE (the (Δ0 − Δ1) CI excludes 0) and HOLD.**

| removal | pooled | bootstrap 95 % CI | signs |
|---|---|---|---|
| R_or = A0 − A1 (oracle subtraction) | +0.02347208988140655 | [0.020699778192917094, 0.026399521942678278] | 32/32 + |
| R_est = A0 − A4 (estimated subtraction) | +0.022155075482892434 | [0.019464560887616736, 0.024830430727009353] | 32/32 + |
| **R_est / R_or** | **0.943890194474869** | [0.902330511257102, 0.9879058376381377] | — |

R_est excludes 0 and the ratio is ≥ 0.5 by a wide margin: **a per-occasion norm
estimated from 32 disjoint authors removes 94.4 % of what the oracle subtraction
removes.** The deployable repair works. This is the one registered lean whose
HOLD is a measurement rather than an identity.

**Pivot P2b — FIRES** by its registered trigger (L-a HOLD, L-b MISS, Ŝ = 1.0000
≥ 0.75). Its evidential basis, stated plainly: the trigger is satisfied by a
construction identity, not by a powered contrast. What *does* support P2b's
substantive content is §3 below, which measures the same ownership question on a
live channel and reaches the same conclusion more strongly. The planner
adjudicates whether the registered consequence stands on that basis.

---

## 3. The disclosed second reading: what happens when the AUTHOR channel is deleted

Registered under standing rule 9 (Part 0, R-0.1/R-0.3): the registration names
the removed channel "w_mu", which in f2's generator is the **author** channel
(`f2:178`), not the occasion-common one. A1′/A3′ delete it at the same seeds,
leaving worlds with occasion content and iid noise but **no author identity at
all**. These arms adjudicate no registered lean.

| contrast | pooled | bootstrap 95 % CI | signs |
|---|---|---|---|
| **Δ1′ = A1′ − A3′** (composition contrast with no author to read) | **+0.04709060297774369** | [0.042167168538819556, 0.052023150832290276] | 32/32 + |
| Δ0 − Δ1′ (the author-reading share, absolute units) | −0.022926062643528297 | [−0.026931371845796803, −0.01909874083349493] | 1 +/31 − |
| (Δ0 − Δ1′)/Δ0 — author-reading share | −0.9487481378268351 | [−1.1583888879836097, −0.7532210144189037] | — |
| Δ1′/Δ0 — frame share | **+1.948748137826835** | [1.7631609956850758, 2.1520391802330505] | — |

Disclosed descriptive contrasts from the same arms:

| contrast | pooled | bootstrap 95 % CI | signs |
|---|---|---|---|
| A1′ − A0 (shared: gain from deleting the author channel) | +0.023006372890384656 | [0.018958716925446557, 0.026933761216768787] | 31/32 + |
| A2 − A3′ (free: cost of deleting the author channel) | −8.031024685635767e-05 | [−0.0017286641331209188, +0.0013853958352737117] | 19 +/13 − |

**Reading.** The composition effect does not merely survive the deletion of
every trace of author identity — it **doubles**: Δ1′ = +0.0471 against Δ0 =
+0.0242, a frame share of 1.95 [1.76, 2.15] of the whole effect, with the
author-reading share landing at −0.95 [−1.16, −0.75]. In the free design the
gauge's split-half agreement is statistically indistinguishable from zero
whether or not authors exist (A2 −0.00092, A3′ −0.00084, difference
−0.00008 with CI straddling 0). In the shared design, deleting the authors
*raises* agreement by +0.0230 [0.0190, 0.0269], 31/32 worlds.

Mechanistically consistent with K1's Branch-B audit and L5 amplification
(interpretation, flagged as such): with authors deleted, every retained author's
feature row is driven by the same occasion trajectory, so the relation field
becomes maximally reproducible across halves; author content, being independent
across authors, *competes* with that common-mode signal rather than adding to it.
At F2's dimensions the deployed gauge's shared-vs-free composition effect
contains **no author-reading component that this design can detect** — the
composition effect is frame-owned, and then some.

---

## 4. The secondary question: T6″ under frame refreshment (L-d)

K1's R-abs machinery, free design, 8 worlds, 985-author panel, 1024-author norm
pool split into two disjoint 512-author sub-pools (Part 0, R-0.6). Contrast:
rank-1(est8) − rank-1(oracle).

| reader | pooled contrast | author-stratified bootstrap 95 % CI | per-world signs | inside ±0.0251 |
|---|---|---|---|---|
| **A** (one norm shared across halves; K1's T3(c) reader) | **+0.058756345177664974** | [+0.05228426395939086, +0.06535532994923858] | 8/8 positive | no |
| **A′** (frame-refreshed: independent norms per half) | **−0.06230964467005076** | [−0.07106916243654822, −0.05418781725888325] | 0/8 positive | no |

| rank-1 | reader A | reader A′ | move |
|---|---|---|---|
| oracle | 0.30355329949238574 | 0.30101522842639594 | **0.0025380710659898** (< 0.01 ✔) |
| est8 | 0.3623096446700508 | 0.23870558375634512 | −0.1236 |

**L-d [prior .65] — MISS**, by the registered rule: under A′ the contrast's CI is
not inside ±0.0251.

**But the miss is an overshoot, not a survival, and it fits no registered
branch.** K1's forged advantage reproduces exactly as reported under reader A
(+0.0588 here vs K1's +0.050127, 8/8 worlds). Under frame refreshment it does not
shrink toward zero — it **inverts** into a penalty of −0.0623, i.e. est8 goes
from beating the oracle by 0.059 to losing to it by 0.062, while the oracle's own
rank-1 barely moves (0.0025 < the registered 0.01 bar: frame refreshment does not
damage genuine identity). The magnitude of the penalty under A′ (−0.062) sits
between K1's reader-B deployable price (−0.09695431472081219) and zero.

**P3b — FIRES mechanically (its trigger is "L-d MISS"), while its stated
antecedent is FALSE.** The pivot's own gloss reads "(forged advantage survives
frame refreshment) → T6″ is wrong as stated; the forged component is not
issuer-sampling content". The forged advantage did **not** survive: it was
destroyed and replaced by the genuine issuer penalty, which is exactly what T6″
predicts qualitatively. What fails is the registered *equivalence form* — T6″ was
operationalized as "collapses to |CI| ⊂ ±0.0251 around zero", and frame
refreshment overshoots that band on the correct side. The substantive content of
T6″ (reproducibility measured under a shared frame is forgeable; reproducibility
under frame refreshment is the licensed discriminator) is **supported in
direction and in the oracle-stability clause**, and refuted only as a
zero-equivalence statement. This is reported as fitting no registered branch;
the planner adjudicates.

---

## 5. Gate summary, pivots, verdict

| gate | verdict | key numbers |
|---|---|---|
| G0 dims | **PASS** | 985 authors, 12,784 events, {8:272, 12:200, 16:513}, 4 contexts, 565 retained — all `==` K1's |
| G1 replication | **PASS** | Δ0 CI [0.021155, 0.027207] overlaps F2's [0.019536, 0.032791]; both readings agree |
| G1b anchors | **PASS** | K1 L5-1× +0.09254304863282958 and L2 +0.09695431472081219 re-derived bit-exactly |
| G2b surgery | **PASS** | reconstruction residual 0.0; subtraction vs twin 1.11e-16; twin(shared) − twin(free) = 0.0 → **PRIMARY exact-subtraction path** |
| G3b power | **PASS** | MDE(n=32) = 0.005151623455652202 ≤ bar 0.0130816, and ≤ aspirational 0.0065408 |
| G4b liveness | **SPLIT** | 3/3 positive, +0.0806946488134565, ratio to author-deviation RMS 0.8529867606271943 ∈ [0.5,2]; n=3 CI [−0.0288, +0.1902] fails a clause that is **unsatisfiable at the anchor's own effect size**; at the anchor's n=8: 8/8 positive, +0.10049101454141054, CI [+0.0503319615961654, +0.1506500674866557] |
| G5 hygiene | **PASS** | manifest, per-stage seeds, wall-times, all foreground |

| lean | prior | verdict | basis |
|---|---|---|---|
| L-a amplification share material | .70 | **HOLD** | by construction (Ŝ ≡ 1) |
| L-b alignment share survives | .60 | **MISS** | by construction (Δ1 ≡ 0) |
| L-c free-design specificity | .75 | **HOLD** | measured: +0.000692, CI ⊂ ±0.006541 |
| L-d T6″ collapse | .65 | **MISS** | measured: A′ contrast −0.0623, CI ⊄ ±0.0251 — overshoot, not survival |
| L-e deployable repair | .55 | **HOLD** | measured: R_est/R_or = 0.9439 [0.9023, 0.9879] |

| pivot | fires | note |
|---|---|---|
| P1b non-replication → VOID | **no** | G1 passed |
| P2b retrospective downgrade | **yes** | trigger satisfied by a construction identity; the live evidence for its content is §3 |
| P3b T6″ wrong as stated | **yes (mechanically)** | its stated antecedent is false — see §4 |
| P4b channels not separable | **no** | G2b passed on the primary path |

**Verdict slug** (produced by the recipe fixed in the script before any arm ran):

`REGISTERED_DECOMPOSITION_DEGENERATE_BY_CONSTRUCTION__SHARE_IS_UNITY_BY_IDENTITY__COMPOSITION_EFFECT_SURVIVES_AUTHOR_DELETION__FRAME_OWNED__T6dd_MISS__P2B_FIRES`

### What this leg establishes, in one paragraph

F2's composition effect replicates (Δ0 = +0.0242, 32/32 worlds, overlapping F2's
own interval). The registered decomposition of it cannot work in F2's generator,
because at κ = 1.0 the design manipulation and the common channel are the same
object — a fact derived and disclosed before any arm ran, and confirmed at
machine precision. The question it was registered to answer is nevertheless
answered, by the disclosed second reading: with every trace of author identity
deleted, the shared-vs-free contrast is **+0.0471, roughly twice the intact
effect**, and the free design reads zero with or without authors. On the deployed
gauge, at F2's dimensions, "composition improves reading" is frame amplification;
no author-reading share is detectable, and the point estimate of that share is
negative. A deployable per-occasion norm estimated from 32 disjoint authors
removes 94 % of what an oracle subtraction removes, so the frame content is
practically strippable. On the secondary question, K1's forged identity
reproduces under the shared-norm reader (+0.0588, 8/8) and is destroyed by frame
refreshment (−0.0623, 0/8) while genuine identity is untouched (oracle moves
0.0025) — T6″'s direction is vindicated and its registered zero-equivalence form
is not.

### Claim boundary

Synthetic decomposition of a synthetic composition effect in a world calibrated
to the opened PANDORA D-panel regime, through the deployed frozen machinery.
Licenses IDT grammar (typing rules, design priors, reader constructions) only.
No claim about any corpus, construct, person, or diagnosis. Label-free, all
synthetic, EXPLORATORY tier, no seal, no independent verification
(open-exploration phase rules).
