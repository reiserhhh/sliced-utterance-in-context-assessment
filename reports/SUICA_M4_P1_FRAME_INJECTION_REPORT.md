# SUICA M4-P1 — the frame-injection sign probe — **SIGN_SCAFFOLD**

**Outcome: SIGN_SCAFFOLD (routing cell 3).** SIGN_SCAFFOLD -- the penalty's owner is frame-scaffolding; P2 doses it

Per base cell: B1=POSITIVE, B2=POSITIVE (cross-cell agreement: True). 1152 fresh
worlds (192/arm × 6 arms). No seal — the leans were registered honestly
split, so no sealable point prediction existed.

Tier EXPLORATORY, label-free, synthetic. Registered in
`docs/SUICA_M4_P_PENALTY_MECHANISM_LINE_PLAN.md` BEFORE run (commit 7589299).
Every number below is generated from artifacts by code (rule 24); none is
hand-typed.

---

## 1. The injection point

The registration's choice rule is its own sentence (rule 12): *the LAST common
per-occasion object every author's response shares before the frozen map*. In
the K2b family there is exactly one such object.

| property | value |
|---|---|
| choice rule | the registration's own sentence: 'the LAST common per-occasion object every author's response shares before the frozen map' (rule 12) |
| **the object** | **world['common']**  (4, 16, 64)  (n_contexts, t_max occasions, DIM) |
| built at | `scripts/run_suica_m4_k2b_t4_branch.py:337` |
| built source | `common = A_SCALE * ((common_lat * G_PROFILE) @ loadings.T)     # (n_ctx, t_max, 64)` |
| returned at | `scripts/run_suica_m4_k2b_t4_branch.py:349` |
| **LAST read before the frozen map** | **`scripts/run_suica_m4_k2b_t4_branch.py:377`** |
| that source line | `v += w["common"] * world["common"][ctx_index[i], :m]` |
| emit_panel called at | `scripts/run_suica_m4_k2b_t4_branch.py:615` |
| frozen map entry at | `scripts/run_suica_m4_k2b_t4_branch.py:616` |
| that source line | `raw_m, raw_k = f1().featurize_panel(` |
| why this object | it is the only object that is BOTH common (not author-specific) AND per-occasion that every author's response incorporates; the next line to touch the response is the frozen map's own entry |
| injection mechanics | delta(o) is added to common[c, o, :] for EVERY context c, so every author on occasion o receives the identical response-level shift w['common'] * delta(o) |
| k2b edited | False |
| suica_core edited | False |

**The object is `world['common']` (4, 16, 64), and the injection point is
`scripts/run_suica_m4_k2b_t4_branch.py:377`** — the line inside `emit_panel` that folds the common channel
into every author's response. That call sits at `scripts/run_suica_m4_k2b_t4_branch.py:615`, one line before
the frozen map's entry at `scripts/run_suica_m4_k2b_t4_branch.py:616`. Nothing between them is both common and
per-occasion.

δ(o) is added to `common[c, o, :]` for **every** context c, so every author on
occasion o receives the identical response-level shift `w["common"]·δ(o)` — which
is what "added to every author's response on occasion o" means. Neither
`suica_core/` nor `run_suica_m4_k2b_t4_branch.py` was edited: the harness calls
k2b's own `build_k2b_world`, perturbs the returned array, and hands the world to
k2b's own `run_field_world`.

## 2. G0p1 — the citations

| clause | expected | recomputed / persisted | bit-exact |
|---|---|---|---|
| base-cell r B1 (share 0.25, phi 0.05) | 0.785015540293945 | 0.785015540293945 | True |
| base-cell r B2 (share 0.25, phi 0.6) | 0.7558507450373838 | 0.7558507450373838 | True |
| M2 C4 mean | 0.12239759528671845 | 0.12239759528671845 | True |
| M2 C4 is the same base cell as B1 | True | True | True |

The cited sentences are **located and extracted by code**, not transcribed —
each anchor substring is found in its controlling document and the containing
paragraph is lifted verbatim, so rule 24 covers the quotes as well as the
tables:

| anchor | located at | verbatim quote (extracted by code, rule 24) |
|---|---|---|
| K-R1 scaffold corollary | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md:3244` (para 3234-3246) | - **L-R1 → P-R1:** de-framing IMPROVES the trait instrument → an F16 adoption memo is DRAFTED for the program owner's decision (the third certified-unadopted repair, now with trait-instrument evidence); nothing is adopted by the planner. - **L-R2 → P-R2:** de-framing is HYGIENE, not enhancement — it changes what the gauge reads (composition collapse) without improving trait reading; T9's counter-operations are re-typed accordingly (licensing language only). - **L-R3 → P-R3:** de-framing HARMS trait reading — a deployment caution is added to the certified repair's record; the mechanism question… |
| K1 amplification (+0.0925) | `docs/SUICA_V8_IDT_INTEGRATION.md:36` (para 27-41) | - **The frame F = (P, O, h, U)** — issuer (reference sample), jurisdiction (occasion universe), expiry (horizon), units (representation). Every deviation-based object is typed by its frame; T1 (gauge trichotomy) proves magnitude is three-ways gauge-dependent while T2's invariant layer (centered configuration, shares, angles under scalar gauge) is the citable stratum. This SHARPENS V8's F03/F09 refusals: "no universal coordinate" now has a theorem-shaped reason. - **The reader is part of the measurement chain.** The deployed relation-field gauge is not a neutral window: it AMPLIFIES common-fram… |
| K1 amplification (3.54x F2) | `docs/SUICA_V8_IDT_INTEGRATION.md:36` (para 27-41) | - **The frame F = (P, O, h, U)** — issuer (reference sample), jurisdiction (occasion universe), expiry (horizon), units (representation). Every deviation-based object is typed by its frame; T1 (gauge trichotomy) proves magnitude is three-ways gauge-dependent while T2's invariant layer (centered configuration, shares, angles under scalar gauge) is the citable stratum. This SHARPENS V8's F03/F09 refusals: "no universal coordinate" now has a theorem-shaped reason. - **The reader is part of the measurement chain.** The deployed relation-field gauge is not a neutral window: it AMPLIFIES common-fram… |
| K1 implementation: the RMS definition (CONTROLS, RN-P1-2) | `scripts/run_suica_m4_k1_issuer_theorems.py:339` (para 337-361) | def _author_deviation_rms(vectors: list[np.ndarray], labels: list[np.ndarray], contexts: list[str]) -> float: """RMS over (author, dim) of the author's mean deviation from the within-(context,occasion) norm, at the RESPONSE level. Computed on the SHARED design's unshifted world (in the free design every occasion has one author and the quantity is identically 0).""" sums: dict[tuple[str, int], np.ndarray] = {} counts: dict[tuple[str, int], int] = {} for i, vec in enumerate(vectors): for t in range(len(vec)): key = (contexts[i], int(labels[i][t])) if key in sums: sums[key] += vec[t] counts[key] … |
| K1 implementation: the delta construction | `scripts/run_suica_m4_k1_issuer_theorems.py:383` (para 368-386) | def _generate_shifted(counts, contexts, knobs, kappa, occasion_mode, world_seed): # noqa: ANN001 vectors = _ORIG_GENERATE(counts, contexts, knobs, kappa, occasion_mode, world_seed) scale = float(_SHIFT_STATE.get("scale", 0.0)) if scale == 0.0: return vectors labels = _ORIG_OCCASION_LABELS_REL(counts, occasion_mode) shared_labels = _ORIG_OCCASION_LABELS_REL(counts, "shared") base = _ORIG_GENERATE(counts, contexts, knobs, kappa, "shared", world_seed) rms = _author_deviation_rms(base, shared_labels, contexts) n_lab = int(max(int(lab.max()) for lab in labels)) + 1 rng = np.random.default_rng( v8.s… |
| K1 recipe (author-deviation RMS) | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md:109` (para 106-112) | Common-shift arms (for L5, R-rel primary on the shared design; free design reported descriptively): pre-map occasion-level common perturbation δ(o) added to every author's response on occasion o; sizes {0.5×, 1×, 2×} of the world's author-deviation RMS at the response level (calibration reported); 2× is a stress arm, no gate. R-abs under the same shifts reported descriptively (its post-map card-space arms already isolate the issuer algebra). |
| K2b G4b frame-carried substrate | `docs/SUICA_M4_K_IDENTITY_LINE_PLAN.md:3401` (para 3398-3411) | **The mechanism is the finding (recorded by the executor as a finding, adopted here as the line's closing lesson — the SCAFFOLD COROLLARY):** in this family the trait has NO frame-free expression in the field — the b-only truth panel's only within-author occasion variation IS the frame (strict trait-only fields are degenerate at context norms ~7e-4). The reader reads the person THROUGH the person×frame interaction; bleach the paper and the watermark goes with the forgery. De-framing is therefore DIAGNOSTIC (contrast, refreshment — T9's counter-operations), never a preprocessing step, wherever … |

## 3. G1p1 — the instrument is live, calibrated, and inert at zero

| clause | quantity | value | PASS |
|---|---|---|---|
| (a) moves the pre-map object | worlds checked (s > 0) | 8 | True |
| (a) | min \|\|delta common\|\|_F | 14.227782891799846 |  |
| (a) | max \|\|delta common\|\|_F | 14.883213260576998 |  |
| (a) | every array bit-CHANGED | True |  |
| (b) realized RMS calibration | tolerance | 0.05 | True |
| (b) | max relative error | 1.8675090942348197e-16 |  |
| (c) s = 0 bit-identity | worlds checked | 8 | True |
| (c) | max \|recovery difference\| | 0.0 |  |
| (c) | common array bit-identical at s = 0 | True |  |

- **(a) The injection moves the pre-map object.** Frobenius norm of the change
  ranges over 14.227782891799846 … 14.883213260576998 across the s > 0 pilot worlds, and
  every perturbed array differs bit-wise from its unperturbed self.
- **(b) The calibration lands.** Worst relative error between the realized
  response-level RMS of δ and its target is **1.8675090942348197e-16**, against a
  0.05 tolerance. The calibration is solved in closed form and then
  *recomputed from the scaled δ* before being persisted (RN-P1-3), so this
  tests an executed number rather than an intended one.
- **(c) s = 0 is bit-identical.** The full injection path runs at s = 0 — δ is
  drawn and scaled to exactly zero — and the resulting field statistic is
  compared bit-for-bit against k2b's unperturbed construction on 8
  worlds: **True**, max |difference| 0.0. The path is proven
  inert at zero, so no arm is contaminated by the mere existence of the
  injection.

| cell | world | recovery via the injection path | recovery unperturbed | bit-identical | abs difference |
|---|---|---|---|---|---|
| B1 | 0 | 0.10089166477697556 | 0.10089166477697556 | True | 0.0 |
| B1 | 1 | 0.12627867321304642 | 0.12627867321304642 | True | 0.0 |
| B1 | 2 | 0.11968169973724069 | 0.11968169973724069 | True | 0.0 |
| B1 | 3 | 0.08488451948733887 | 0.08488451948733887 | True | 0.0 |
| B2 | 0 | 0.16218241281926193 | 0.16218241281926193 | True | 0.0 |
| B2 | 1 | 0.10102531251752749 | 0.10102531251752749 | True | 0.0 |
| B2 | 2 | 0.09219910746969805 | 0.09219910746969805 | True | 0.0 |
| B2 | 3 | 0.14066135898859805 | 0.14066135898859805 | True | 0.0 |

## 4. G2p1 — the pilot and the rule-29 predicate

| cell | s | n | mean | min | max | finite | any saturated | nonzero var | PASS |
|---|---|---|---|---|---|---|---|---|---|
| B1 | 0.0 | 4 | 0.1079341393036504 | 0.08488451948733887 | 0.12627867321304642 | True | False | True | True |
| B1 | 1.0 | 4 | 0.4039320933401762 | 0.3376922242093859 | 0.5044475725152401 | True | False | True | True |
| B2 | 0.0 | 4 | 0.12401704794877139 | 0.09219910746969805 | 0.16218241281926193 | True | False | True | True |
| B2 | 1.0 | 4 | 0.4245695963617907 | 0.40387125975794363 | 0.44147795914527665 | True | False | True | True |

Domain-pinned per rule 29: `recovery_b_only` is a weighted mean of matrix
cosines on [−1, 1], so the predicate is finiteness, non-saturation at
|x| ≥ 0.995 and nonzero variance, with **no positivity clause**.

## 5. G3p1 — the projection

| quantity | value |
|---|---|
| sigma source | the pilot's s = 0 worlds, pooled within base cell |
| pilot s = 0 cells | B1 (n=4, sd=0.018756407986154154), B2 (n=4, sd=0.03303850985420065) |
| pooled df | 6 |
| sigma_raw | 0.02686397191341203 |
| chi2 quantile | 0.1 |
| chi2 value | 2.2041306564986427 |
| inflation factor | 1.6498974741130894 |
| **sigma (df-inflated)** | **0.04432279940458349** |
| convention | sigma * sqrt(df / chi2.ppf(0.10, df)) -- M1b's G3m'(b) convention, the conservative upper bound |
| SE(b-hat) formula | SE(b-hat) = sigma / sqrt(n/2) (RN-P1-4) |
| SE(b-hat) at n = 192 | 0.004523676771373484 |
| **MDE(2 SE)** | **0.009047353542746968** |
| bar | 0.01 |
| **PASS** | **True** |
| escalation fired | False |
| worlds per arm decided | 192 |

σ comes from the pilot's s = 0 worlds pooled within base cell (df = 6),
df-inflated by 1.6498974741130894 on M1b's registered χ²(0.10) convention: σ_raw
0.02686397191341203 → **0.04432279940458349**. RN-P1-4 makes SE(b̂) exact for this design —
σ/√(n/2) — giving SE = 0.004523676771373484 and **MDE(2·SE) = 0.009047353542746968 ≤ 0.01**. The
once-only escalation to 384/arm did not fire (False).

## 6. The verdict

| cell | phi | r | b-hat | 95% CI | bootstrap SE | B | classification (pinned) | sign-first reading | agree | quadratic coef | quadratic 95% CI |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B1 | 0.05 | 0.785015540293945 | 0.3217400470171695 | [0.3125381894506993, 0.3316075999536289] | 0.004933658390212879 | 2000 | **POSITIVE** | POSITIVE | True | 0.40057861511636317 | [0.37583586015744497, 0.4257979348871747] |
| B2 | 0.6 | 0.7558507450373838 | 0.34654236945734695 | [0.3383230195793485, 0.3553320781635022] | 0.004431858848100128 | 2000 | **POSITIVE** | POSITIVE | True | 0.4530033122717317 | [0.4286407724120133, 0.47705825144020014] |

| cell | share | phi | s | n | mean | sd | SEM | mean realized delta RMS | max calibration error |
|---|---|---|---|---|---|---|---|---|---|
| B1 | 0.25 | 0.05 | 0.0 | 192 | 0.11873302020953876 | 0.024632389119551814 | 0.0017776895611196061 | 0.0 | 0.0 |
| B1 | 0.25 | 0.05 | 0.5 | 192 | 0.1794583899390327 | 0.030127001802162916 | 0.0021742290750443875 | 0.03720787207513443 | 1.876116147814573e-16 |
| B1 | 0.25 | 0.05 | 1.0 | 192 | 0.44047306722670826 | 0.06437497363716889 | 0.0046458635448118155 | 0.07443049350172602 | 1.8776521577460127e-16 |
| B2 | 0.25 | 0.6 | 0.0 | 192 | 0.12904388025689947 | 0.024001471865071365 | 0.001732157030280773 | 0.0 | 0.0 |
| B2 | 0.25 | 0.6 | 0.5 | 192 | 0.18906423691764004 | 0.0298574602881695 | 0.0021547765918366528 | 0.03864141541522801 | 1.8063659690881276e-16 |
| B2 | 0.25 | 0.6 | 1.0 | 192 | 0.47558624971424646 | 0.05666680883274166 | 0.004089574666712558 | 0.077341447932803 | 1.812749739343704e-16 |

### 6.1 The slope's algebra, proven not asserted

| cell | b-hat = mean(s=1) - mean(s=0) | OLS witness on all 3n points | identity holds | mean(s=0) | mean(s=0.5) | mean(s=1.0) |
|---|---|---|---|---|---|---|
| B1 | 0.3217400470171695 | 0.32174004701716924 | True | 0.11873302020953876 | 0.1794583899390327 | 0.44047306722670826 |
| B2 | 0.34654236945734695 | 0.34654236945734684 | True | 0.12904388025689947 | 0.18906423691764004 | 0.47558624971424646 |

With s ∈ {0, 0.5, 1.0} equally replicated the OLS slope reduces **exactly** to
mean(s = 1) − mean(s = 0); the midpoint arm contributes nothing to b̂ and
identifies only the descriptive quadratic. The identity is verified against a
full OLS witness on all 3n points at both cells.

### 6.2 The M2 anchor replicates

| quantity | value |
|---|---|
| M2 C4 mean (share 0.25, phi 0.05, n = 192) | 0.12239759528671845 |
| M2 C4 SEM | 0.001996680913797175 |
| P1 B1 s = 0 mean (n = 192) | 0.11873302020953876 |
| P1 B1 s = 0 SEM | 0.0017776895611196061 |
| difference | -0.0036645750771796964 |
| pooled SEM | 0.002673371438321944 |
| **z** | **-1.3707691436547715** |
| within 2 pooled SEM | True |
| note | same base cell (share 0.25, phi 0.05), DIFFERENT salt, so this is a distributional replication and not a bit-identity claim |

The s = 0 arm at B1 sits at 0.11873302020953876 against M2's C4 mean 0.12239759528671845 on the
same base cell — difference -0.0036645750771796964, z = -1.3707691436547715, within two pooled
SEM: True. Different salt, so this is a distributional replication and
not a bit-identity claim; it is reported because it is the cheapest available
check that the unperturbed arm is the same object M2 measured.

## 7. Routing

| # | condition | outcome |
|---|---|---|
| 1 | any G0p1/G1p1 failure | STOP (citation/instrument defect; no arms) |
| 2 | projection fails after escalation | NON_PROJECTABLE (handback) |
| 3 | both cells POSITIVE | **SIGN_SCAFFOLD -- the penalty's owner is frame-scaffolding; P2 doses it**  <-- THIS LEG |
| 4 | both cells NEGATIVE | SIGN_CONTAMINATION -- the gauge's amplification owns the penalty; P2 doses it; connects to K1's +0.0925 quantitatively |
| 5 | both cells NULL | FRAME_INSENSITIVE -- neither named mechanism owns the penalty at this scale; a third mechanism is named, not invented |
| 6 | cells disagree in classification (any mix incl. UNDERPOWERED on one side) | SPLIT_OR_UNDERPOWERED -- the phi-dependence or the power shortfall is named; P2's design inherits the diagnosis |

## 8. Gates

| gate | PASS | detail |
|---|---|---|
| G0p1 | True | base-cell r bit-exact from the pinned maps; all cited sentences located verbatim by code; M2's C4 mean bit-exact at source |
| G1p1 | True | injection moves the pre-map object; realized RMS within 5% of target; s = 0 bit-identical to the unperturbed construction |
| G2p1 | True | rule-29 domain-pinned predicate held at all pilot arms and all six full arms |
| G3p1 | True | MDE(2 SE) = 0.009047353542746968 <= 0.01 at n = 192; escalation fired: False |
| G4p1 | True | routing disjoint-and-covering; tables generated (rule 24); stages under estimate |

## 9. Sides declared (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G1p1 | norm delta > 0; realized RMS within 5%; s=0 bit-identical | — | one-sided |
| G3p1 | MDE(2 SE) <= 0.01 | — | one-sided |
| L-1p1 | scaffold(+) / contamination(-) / null-or-split | 0.45 / 0.40 / 0.15 | categorical, two-sided on the sign |

## 10. Pinned readings

| note | pinned reading |
|---|---|
| RN-P1-1 | the injection point is world['common'] (k2b:337 built, :349 returned, :377 last read inside emit_panel, called :615 one line before the frozen map at :616); delta(o) is added to common[c, o, :] for EVERY context so every author gets the identical response-level shift; k2b is not edited |
| RN-P1-2 | K1's OWN implementation controls (rules 9/12): centre each response on its (CONTEXT, OCCASION) cell mean, average each author's deviations over its occasions to one vector per author, RMS over (author x dim) -- transplanted literally from k1:337-361. Invariant to the injection because delta is identical across authors and cancels in the cell deviation. Two alternative readings are computed and REPORTED per world, never used to calibrate; only K1's sets the dose |
| RN-P1-3 | delta is drawn from a dedicated RNG (never the world stream) and rescaled in closed form to hit the target exactly; the realized RMS is recomputed after scaling and persisted, so the 5% gate tests an executed number |
| RN-P1-4 | with s in {0, 0.5, 1.0} equally replicated the OLS slope equals EXACTLY mean(s=1) - mean(s=0); the midpoint arm identifies only the descriptive quadratic c = 2*(y0 - 2*y1 + y2); SE(b-hat) = sigma/sqrt(n/2) |
| RN-P1-5 | the registered classification is NOT disjoint (a CI inside the margin and above 0 is both POSITIVE and NULL). PINNED: equivalence wins -- inside the margin is NULL whatever the sign (rule 4); else CI excluding 0 gives POSITIVE/NEGATIVE; else UNDERPOWERED. The sign-first ordering is also computed and reported |
| RN-P1-6 | worlds are independent across arms (the arm enters the seed), so the bootstrap resamples world indices independently within each arm, master-seeded, B=2000 (20000 at a rule-13 boundary) |
| RN-P1-7 | K1 SETS delta's per-component sigma to scale*rms; this registration says the REALIZED RMS must EQUAL the target, so delta is rescaled exactly. The two agree to ~2% at 1024 draws (both clear the 5% band); the P1 text is binding and exact rescaling makes G1p1(b) test the code |

## 11. Rule events

- **Rule 13:** 0 boundary event(s) triggered a B = 20000 re-run.
- **Rule 26:** no bounded winner; nothing was fitted with active bounds.
- **Rule 29:** in force as the G2p1 predicate, domain-pinned to [−1, 1] with no
  positivity clause. Held at every pilot arm and every full arm.
- **Rule 30:** every constant in this harness was verified against its persisted
  source before Part 0, and every quoted sentence is extracted by code.

## 12. Anomalies, with timing

1. **A-1 (environment; before any number).** The dispatched interpreter does not
   exist on this machine and the only `pandas` present belongs to CPython 3.9.6,
   which cannot import the machinery. A CPython 3.12.12 venv was built
   outside the repo from `requirements-lock-main.txt` verbatim and pinned.
   Resolved BEFORE any hypothesis-relevant number existed.
2. **A-2 (tooling; before any number).** `timeout(1)` is absent on macOS; every
   stage ran as its own foreground command under an explicit sub-600 s timeout.
   Resolved BEFORE any hypothesis-relevant number existed.

## 13. Registration-defect candidates

1. **The verdict classification is not disjoint** (RN-P1-5). POSITIVE (CI > 0)
   and NULL (CI inside ±0.01) overlap: a CI like (0.001, 0.005) satisfies
   both. Rule 16 is met on the routing table but not on the classification that
   feeds it. Pinned before any number — equivalence wins, per rule 4 — with the
   sign-first ordering also computed and reported. Non-blocking.

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
| part0 | 90 | 0.028 |
| pilot | 40 | 13.938 |
| project | 20 | 0.004 |
| arm B1 s=0.0 | 130 | 113.922 |
| arm B1 s=0.5 | 130 | 115.020 |
| arm B1 s=1.0 | 130 | 113.374 |
| arm B2 s=0.0 | 130 | 113.454 |
| arm B2 s=0.5 | 130 | 111.559 |
| arm B2 s=1.0 | 130 | 113.592 |
| fit | 120 | 0.082 |
| finalize | 60 | 0.000 |

---

*Artifacts: `results/m4_p1_frame_injection/` (gitignored) — `part0.json`,
`pilot.json`, `pilot_field.csv`, `pilot_calibration.csv`, `projection.json`,
`arms/`, `fit.json`, `decision.json`, `prose_facts.json`, `report_tables.md`,
`run_log.jsonl`. Harness: `scripts/run_suica_m4_p1_frame_injection.py`.*
