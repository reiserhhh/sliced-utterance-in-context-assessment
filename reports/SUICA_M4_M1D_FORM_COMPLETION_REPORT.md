# M4-M1d — the completion and the coordinate

**Leg:** M4-M1d · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M1d — the completion and
the coordinate"), commit `54afc77`, BEFORE this run.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m1d_form_completion.py`.
**Artifacts:** `results/m4_m1d_form_completion/` (gitignored).
**Banner:** artifact-space form comparison on M1c's persisted 3840-world corpus;
no new worlds, exploratory, label-free.

**Verdict: `COMPLETED_BUT_INCOMPLETE` (rule-16 cell 6).** COMPLETED_BUT_INCOMPLETE -- M2 deferred; M1e named
L-1d **HOLD**, L-2d **F0**, L-3d **overlap**, L-4d **fires**. Modifier:
none.

Appendix W.1 named a gap and prescribed a form extension. M1d ran it. Three
things came back, and only the first is the one the registration asked for.

**One: the intercept is real, and the coordinate is r.** `F0` —
`field = c + lambda*r^q - kappa*V` — wins leave-one-cell-out at `0.0030682764618814033` against the best
incumbent's `0.0031856515917748638` (F1e), so **L-1d HOLDS**: an
extension beats all four incumbents. `Fφ` — the state-dynamics coordinate — does
**not** merely lose to `F0`, it loses to the best incumbent too
(`0.0032498223469787663`). **L-2d answers `F0`**, and the mechanism hypothesis of
appendix X.4 (an occasion-structure consumer, φ as the natural argument) is not
supported by this corpus.

**Two: κ appears a fifth time.** `0.7766770259880144`, CI `[0.7482226203832176, 0.8064115044591174]`, overlapping
M1c's `[0.7356727662590873, 0.7846243216827854]` — **L-3d overlap**, no `TAX_SHIFT`. It is the one
parameter in this leg that is sharply identified, at width `0.05818888407589973`.

**Three, and it is the finding the registration did not ask for: the winning
form cannot report an exponent.** `F0`'s intercept buys its LOO win by trading
against the power term, and the three of them are jointly non-identified:
`c` CI `[0.20818746052333, 1.6803368132111625]` (width `1.4721493526878324`), `λ` CI `[-1.5059828481846496, -0.04256154549067277]` (width
`1.4634213026939769`), `q` CI `[0.021913588793404413, 2.6445200496694605]` — **width `2.622606460876056`**.
Worse for the previous leg's headline: `F0`'s point estimates are
`λ = -0.055190882521519` (NEGATIVE) with `q = 1.372031438858951` (POSITIVE), which describes
the *same* falling-in-r field as M1c's `q = -0.15040108849226472` with positive λ.
**M1c's negative exponent was the family's only way to bend the field downward
in r without an intercept.** Give it an intercept and it re-parameterises to a
positive exponent with a negative amplitude. The monotone direction is robust;
the exponent is not a structural constant of this world, it is a coordinate on a
ridge.

And the family is still not closed: the within-share r² residual **fires** at
`-0.12563681892698172`, CI `[-0.1772060912696028, -0.07219090437007022]`. The intercept shrank it by 36.90141692114467%
from M1c's `-0.19911194958208703` — real progress — but did not kill it. Hence cell 6:
**M2 is deferred and M1e is named.**

---

## Part 0 — written before any fit

### 0.1 Rule 9 / rule 12 — conventions pinned in writing

| note | pinned reading |
|---|---|
| RN-M1D-1 | machinery COPIED, then PROVEN bit-exact in Part 0 against the imported M1c harness -- the four incumbents are verified frozen in their M1c roles rather than asserted to be |
| RN-M1D-2 | L-4d's probe inherits M1c's RN-M1C-6 estimator unchanged (OLS of cell residuals on [1, r, r^2] with share fixed effects; CI from the same world-block bootstrap draws; fires = CI excludes 0), so the number is comparable to M1c's; a phi^2 companion is reported and routes nothing |
| RN-M1D-3 | V-shadow start grid pinned to the F0 grid's own lambda and q axes (18 starts) |
| RN-M1D-4 | legacy retrodiction = the winner's M1d-fitted parameters evaluated on K2f's 26 rows with NO refit (comparable to the sealed form's own no-refit RMSE); K2f's 0.0061559195350209 is a REFIT reference, not a like-for-like rival |
| RN-M1D-5 | rule-26 surveillance: no bounds exist on F0/Fphi so the trigger cannot fire there; F1e's inherited epsilon bound and a 'numerical limit' test (\|param\| >= 1e3, or termination at max_nfev) are checked and reported either way |
| RN-M1D-6 | bootstrap draws generated in batches from ONE master-seeded rng in draw order -- identical stream to the unbatched form |

### 0.2 The six forms, and the nesting statement (G1d)

| form | expression | params | starts | bounded | role |
|---|---|---|---|---|---|
| F1 | field = lambda*r^q - kappa*V | ['lambda', 'q', 'kappa'] | 54 | False | M1c incumbent (M1c runner-up) |
| F1e | field = lambda*r^q - kappa*V - epsilon, epsilon in [0, 0.05] | ['lambda', 'q', 'kappa', 'epsilon'] | 162 | True | M1c incumbent (M1c winner; bound was ACTIVE) |
| F2 | field = lambda*r^q - kappa*V*r^p | ['lambda', 'q', 'kappa', 'p'] | 162 | False | M1c incumbent |
| F3 | field = (lambda - kappa*V)*r^q | ['lambda', 'q', 'kappa'] | 54 | False | M1c incumbent |
| F0 | field = c + lambda*r^q - kappa*V | ['c', 'lambda', 'q', 'kappa'] | 162 | False | EXTENSION -- the W.1 gap made a form; nests F1 at c = 0 |
| Fphi | field = c + a*phi^m - kappa*V | ['c', 'a', 'm', 'kappa'] | 108 | False | EXTENSION -- the coordinate alternative; nests no incumbent |

### 0.3 RN-M1D-1 — the four incumbents proven frozen in their M1c roles

The incumbents are not merely *said* to be unchanged: Part 0 imports the M1c
harness and refits all four on M1c's own cell means, demanding bit-exact
agreement on every parameter and on the SSE.

| incumbent | theta (this leg) | theta (M1c harness) | starts | bit-exact |
|---|---|---|---|---|
| F1 | [0.17505204234174737, -0.1888182542137735, 0.7596295789070726] | [0.17505204234174737, -0.1888182542137735, 0.7596295789070726] | 54 | True |
| F1e | [0.2249206339499495, -0.15040108849226472, 0.7601952008701406, 0.049999999999999996] | [0.2249206339499495, -0.15040108849226472, 0.7601952008701406, 0.049999999999999996] | 162 | True |
| F2 | [0.17810271708703745, -0.12421609491451265, 0.7831856742623807, 0.10816742886000663] | [0.17810271708703745, -0.12421609491451265, 0.7831856742623807, 0.10816742886000663] | 162 | True |
| F3 | [0.1675744937183866, -0.3141204190367959, 0.6658456569673928] | [0.1675744937183866, -0.3141204190367959, 0.6658456569673928] | 54 | True |

### 0.4 G0d(i) — the 20 cell means, re-derived from the rawest artifacts

No new worlds. Every cell mean and SEM is recomputed from M1c's per-world CSVs
(192 worlds per cell, round-trip parsed) and matched bit-for-bit against M1c's
persisted `cell_means.csv`.

| cell | n | mean re-derived | mean persisted | bit-exact | SEM re-derived | bit-exact |
|---|---|---|---|---|---|---|
| s0.10_p0.05 | 192 | 0.1585891652101896 | 0.1585891652101896 | True | 0.0018743992250782693 | True |
| s0.10_p0.30 | 192 | 0.16035538669822857 | 0.16035538669822857 | True | 0.0020066026535869932 | True |
| s0.10_p0.60 | 192 | 0.16156034289722412 | 0.16156034289722412 | True | 0.0019744651453781504 | True |
| s0.10_p0.85 | 192 | 0.16512469544098618 | 0.16512469544098618 | True | 0.001983741777975856 | True |
| s0.10_p0.98 | 192 | 0.15987119532439534 | 0.15987119532439534 | True | 0.0018913572625018093 | True |
| s0.25_p0.05 | 192 | 0.12162744485545209 | 0.12162744485545209 | True | 0.0017778785791358425 | True |
| s0.25_p0.30 | 192 | 0.12295515685269942 | 0.12295515685269942 | True | 0.001799144985921348 | True |
| s0.25_p0.60 | 192 | 0.12714790436588774 | 0.12714790436588774 | True | 0.0017053615065044834 | True |
| s0.25_p0.85 | 192 | 0.13204663807737851 | 0.13204663807737851 | True | 0.0018782693723257374 | True |
| s0.25_p0.98 | 192 | 0.13201888792665142 | 0.13201888792665142 | True | 0.0018133362157806163 | True |
| s0.40_p0.05 | 192 | 0.09025343262511598 | 0.09025343262511598 | True | 0.0017452922267459832 | True |
| s0.40_p0.30 | 192 | 0.09132685344495504 | 0.09132685344495504 | True | 0.0016796177194939308 | True |
| s0.40_p0.60 | 192 | 0.0980498887620882 | 0.0980498887620882 | True | 0.0015916871722070262 | True |
| s0.40_p0.85 | 192 | 0.0992713149259878 | 0.0992713149259878 | True | 0.0017741240206580028 | True |
| s0.40_p0.98 | 192 | 0.10169041646048367 | 0.10169041646048367 | True | 0.0017444660987341613 | True |
| s0.60_p0.05 | 192 | 0.05410832013119198 | 0.05410832013119198 | True | 0.001773830076330116 | True |
| s0.60_p0.30 | 192 | 0.057429784543359674 | 0.057429784543359674 | True | 0.0015865768513429728 | True |
| s0.60_p0.60 | 192 | 0.06031911254293101 | 0.06031911254293101 | True | 0.0016085232676605703 | True |
| s0.60_p0.85 | 192 | 0.061787884770662806 | 0.061787884770662806 | True | 0.0015046764572937737 | True |
| s0.60_p0.98 | 192 | 0.063796931786496 | 0.063796931786496 | True | 0.0016195393028748909 | True |

### 0.5 G0d(ii)–(iii) — every number the adjudication quotes

| clause | adjudication | persisted / re-derived | bit-exact |
|---|---|---|---|
| F1 q | -0.1888182542137735 | -0.1888182542137735 | True |
| F1 q CI hi | -0.14900957557344477 | -0.14900957557344477 | True |
| F1 q CI lo | -0.22686946646111852 | -0.22686946646111852 | True |
| F1e epsilon CI lower gap from bound | 9.037909309839165e-14 | 9.037909309839165e-14 | True |
| F1e kappa | 0.7601952008701406 | 0.7601952008701406 | True |
| F1e kappa CI hi | 0.7846243216827854 | 0.7846243216827854 | True |
| F1e kappa CI lo | 0.7356727662590873 | 0.7356727662590873 | True |
| F1e lambda | 0.2249206339499495 | 0.2249206339499495 | True |
| F1e lambda CI hi | 0.2267740781729326 | 0.2267740781729326 | True |
| F1e lambda CI lo | 0.2226976852269149 | 0.2226976852269149 | True |
| F1e q | -0.15040108849226472 | -0.15040108849226472 | True |
| F1e q CI hi | -0.11871900002844447 | -0.11871900002844447 | True |
| F1e q CI lo | -0.18322395953281184 | -0.18322395953281184 | True |
| F1e q CI width | 0.06450495950436737 | 0.06450495950436737 | True |
| LOO F1 | 0.003198131708377386 | 0.003198131708377386 | True |
| LOO F1e | 0.0031856515917748638 | 0.0031856515917748638 | True |
| LOO F2 | 0.0034019365713125944 | 0.0034019365713125944 | True |
| LOO F3 | 0.003877604046883495 | 0.003877604046883495 | True |
| field SEM max | 0.0020066026535869932 | 0.0020066026535869932 | True |
| field SEM min | 0.0015046764572937737 | 0.0015046764572937737 | True |
| field mean max | 0.16512469544098618 | 0.16512469544098618 | True |
| field mean min | 0.05410832013119198 | 0.05410832013119198 | True |
| projection width q_truth 1.0 | 0.24923889216646022 | 0.24923889216646022 | True |
| projection width q_truth 1.8528700746510731 | 0.46602037304504784 | 0.46602037304504784 | True |
| r2 residual CI hi | -0.10706476050455438 | -0.10706476050455438 | True |
| r2 residual CI lo | -0.2879978718649799 | -0.2879978718649799 | True |
| r2 residual coef (within-share) | -0.19911194958208703 | -0.19911194958208703 | True |
| share-.60 field at phi hi | 0.063796931786496 | 0.063796931786496 | True |
| share-.60 field at phi lo | 0.05410832013119198 | 0.05410832013119198 | True |
| tie margin | 1.2480116602522386e-05 | 1.2480116602522386e-05 | True |
| Spearman vector | [0.0, 0.8999999999999998, 0.6, -0.6] | [0.0, 0.8999999999999998, 0.6, -0.6] | True |
| L-4 readings (A/B) | [2, 0] | [2, 0] | True |
| share-.60 rise in pooled SEM (adjudication rounds to 2dp) | 4.03 | 4.03363828257993 | True |
| theory band `[1.71, 1.98]` in `docs/SUICA_IDENTITY_THEORY_V1.md` | [1.71, 1.98] | lines [805, 841, 1386] | True |

30 enumerated citations, the Spearman vector, both L-4 readings, the
share-.60 rise (whose full-precision multiple must round to the adjudication's
2-dp quote), and the theory band — all bit-exact.

---

## Selection

| form | expression | parameters | 95% CI (bootstrapped forms only) | in-sample RMSE | LOO-RMSE | R^2 vs mean | distinct optima |
|---|---|---|---|---|---|---|---|
| F1 | `field = lambda*r^q - kappa*V` | lambda = 0.17505204234174737, q = -0.1888182542137735, kappa = 0.7596295789070726 | lambda [0.17322592761078637, 0.17688885617490216], q [-0.22686946646111852, -0.14900957557344477], kappa [0.735240940068321, 0.7838667424719438] | 0.0026264051166751978 | 0.003198131708377386 | 0.9951610947688201 | 1 |
| F1e | `field = lambda*r^q - kappa*V - epsilon, epsilon in [0, 0.05]` | lambda = 0.2249206339499495, q = -0.15040108849226472, kappa = 0.7601952008701406, epsilon = 0.049999999999999996 | lambda [0.2226976852269149, 0.2267740781729326], q [-0.18322395953281184, -0.11871900002844447], kappa [0.7356727662590873, 0.7846243216827854], epsilon [0.049999999999909624, 0.049999999999999996] | 0.002621078709438027 | 0.0031856515917748638 | 0.9951807016791032 | 1 |
| F2 | `field = lambda*r^q - kappa*V*r^p` | lambda = 0.17810271708703745, q = -0.12421609491451265, kappa = 0.7831856742623807, p = 0.10816742886000663 | — | 0.002591249722764473 | 0.0034019365713125944 | 0.9952897688274347 | 1 |
| F3 | `field = (lambda - kappa*V)*r^q` | lambda = 0.1675744937183866, q = -0.3141204190367959, kappa = 0.6658456569673928 | — | 0.0033903747201612703 | 0.003877604046883495 | 0.9919365836062832 | 1 |
| **F0 (winner)** | `field = c + lambda*r^q - kappa*V` | c = 0.2234421078663232, lambda = -0.055190882521519, q = 1.372031438858951, kappa = 0.7766770259880144 | c [0.20818746052333, 1.6803368132111625], lambda [-1.5059828481846496, -0.04256154549067277], q [0.021913588793404413, 2.6445200496694605], kappa [0.7482226203832176, 0.8064115044591174] | 0.0025054232543959215 | 0.0030682764618814033 | 0.9955966227616307 | 109 |
| Fphi | `field = c + a*phi^m - kappa*V` | c = 0.17381627567461747, a = 0.009836800123892235, m = 0.9290334268399131, kappa = 0.6761549413795372 | — | 0.002538699623241356 | 0.0032498223469787663 | 0.9954788770029874 | 7 |

| quantity | value |
|---|---|
| LOO ranking | F0 < F1e < F1 < Fphi < F2 < F3 |
| winner | F0 |
| runner-up | F1e |
| winner vs runner-up LOO separation | 0.00011737512989346043 |
| … as a fraction of the winner's LOO | 0.03825441786346998 |
| tie rule active (< 5%) | True |
| best incumbent | F1e at 0.0031856515917748638 |
| best extension | F0 at 0.0030682764618814033 |
| extension beats ALL incumbents (L-1d) | True |
| F0 vs Fphi LOO separation | 0.000181545885097363 |
| F0/Fphi tie => CO_WINNERS | False |

`F0` improves on the best incumbent by a factor of 1.03825441786347 in
LOO. Its margin over the runner-up `F1e` is `0.00011737512989346043` =
3.8254417863469983% — **inside the 5% tie band**, so the tie rule fired and every
verdict had to agree across `F0` and `F1e`; they do (L-3d overlap under
both), so nothing reports SPLIT. L-4d also agrees across the pair: `F1e`'s
own within-share r² was measured in M1c at `-0.19911194958208703` `[-0.2879978718649799, -0.10706476050455438]` under the
same estimator, and it fires too — the routing is unchanged whichever member of
the tie is read.

**The CO_WINNERS call was close and the registered rule decided it.** `F0` vs
`Fφ` separate by `0.000181545885097363` = 5.916868553169516% of the smaller LOO,
against a 5.0% bar. Under 5% the leg would have routed to
`CO_WINNERS` and sealed both coordinates. It is 0.92 percentage points the other
side of that line. Disclosed rather than smoothed: the coordinate verdict is
real but it is not comfortable, and a successor should not quote L-2d as though
`Fφ` were refuted.

### Rule 26 — the enacted co-adjudication, exercised

| form | declared bounds | bound active | presses numeric limit | max \|param\| | starts at max_nfev | co-adjudication required |
|---|---|---|---|---|---|---|
| F0 | False | None | False | 1.372031438858951 | 0 | False |
| F1e | True | True | False | 0.7601952008701406 | 0 | True |
| F1 | False | None | False | 0.7596295789070726 | 0 | False |

Rule 26 **fired**, exactly as it was written to. `F1e` reaches the
bootstrap set as runner-up with its ε bound ACTIVE, so its unbounded relaxation
`F1` was co-adjudicated automatically rather than by the tie rule's luck — which
is precisely the failure mode M1c's non-blocking candidate flagged. `F0` and
`Fφ` carry no declared bounds, so the bound trigger cannot fire on them; the
numerical-limit test (RN-M1D-5) was checked on every bootstrapped form and did
not fire (largest |parameter| `1.372031438858951`, no start terminating at
`max_nfev`).

### Rule 13

| quantity | value | bar | scale | within 5% |
|---|---|---|---|---|
| F0: kappa_hi vs M1c ci95 lo | 0.8064115044591174 | 0.7356727662590873 | 0.7356727662590873 | False |
| F0: kappa_lo vs M1c ci95 hi | 0.7482226203832176 | 0.7846243216827854 | 0.7846243216827854 | True |
| F1e: kappa_hi vs M1c ci95 lo | 0.7846243216827854 | 0.7356727662590873 | 0.7356727662590873 | False |
| F1e: kappa_lo vs M1c ci95 hi | 0.7356727662590873 | 0.7846243216827854 | 0.7846243216827854 | False |
| LOO separation winner vs runner-up | 0.00011737512989346043 | 0.0 | 0.0030682764618814033 | True |
| F0 vs Fphi LOO separation (L-2d / CO_WINNERS) | 0.000181545885097363 | 0.0 | 0.0030682764618814033 | False |

Rule 13 triggered on both proximities and the B = 20000 re-run left L-3d and
L-4d unchanged (**L-4d stable: True**, CI `[-0.17935555262608965, -0.07097803090981235]`).

---

## Verdicts

| lean | clause | sided | prior | measured | verdict |
|---|---|---|---|---|---|
| L-1d | an EXTENSION (F0 or Fphi) beats ALL FOUR incumbents on leave-one-cell-out RMSE | one-sided | 0.70 | best extension 0.0030682764618814033 vs best incumbent 0.0031856515917748638 | **HOLD** |
| L-2d | Fphi vs F0 as the LOO winner -- the coordinate question | two-sided; either answer re-types theory (appendix X.4) | 0.50 / 0.50 | F0 0.0030682764618814033 vs Fphi 0.0032498223469787663, separation 0.000181545885097363 | **F0** |
| L-3d | the winner's kappa CI overlaps M1c's [0.7356727662590873, 0.7846243216827854] -- the fifth appearance | two-sided overlap | 0.75 | winner kappa CI [0.7482226203832176, 0.8064115044591174] vs M1c [0.7356727662590873, 0.7846243216827854] | **overlap** |
| L-4d | the winner's within-share r^2-residual CI contains 0 => the family is COMPLETE (routes M2); fires => M2 is DEFERRED | reading that ROUTES | — | r^2 coef -0.12563681892698172 CI [-0.1772060912696028, -0.07219090437007022] | **fires** → M2 DEFERRED -- sealing an incomplete family is sealing glue |

## L-4d — the routing reading

| statistic | coefficient | 95% CI | fires? |
|---|---|---|---|
| r^2 residual, share fixed effects (**the registered probe**) | -0.12563681892698172 | [-0.1772060912696028, -0.07219090437007022] | True |
| r^2 residual, pooled | 0.001054754288525179 | [-0.010339263255536255, 0.014815973510193174] | — |
| phi^2 residual, share fixed effects (companion, routes nothing) | -0.012377098889152529 | [-0.021250484030500706, -0.0035455613757951142] | — |
| M1c's own r^2 under ITS winner, same estimator | -0.19911194958208703 | [-0.2879978718649799, -0.10706476050455438] | True (M1c) |
| r^2 residual at B=20000 (rule 13) | — | [-0.17935555262608965, -0.07097803090981235] | True |

| share | Spearman(residual, phi) | residuals in phi order |
|---|---|---|
| 0.1 | 0.0 | 0.00040970577496413085, 0.0019371257875289427, 0.002578683995600961, 0.004984474546814749, -0.0015869443353383472 |
| 0.25 | 0.7 | -0.0039691913748272495, -0.0032550649311818836, -0.00045295521658011983, 0.0018119437956124196, -0.0008968534754936475 |
| 0.4 | 0.6 | -0.0033938916938938274, -0.0033167150237825294, 0.0012518757961933885, -0.0012611594807709903, -0.0022540119789751234 |
| 0.6 | -0.7 | 0.0015046670808402038, 0.0033680953206026154, 0.003336561672722109, 0.00036071538536978226, -0.0011570616455126997 |

The registered probe fires: within-share r² residual `-0.12563681892698172`, CI
`[-0.1772060912696028, -0.07219090437007022]`, excluding zero and stable at B = 20000. The **pooled** reading
does not fire (`0.001054754288525179`, `[-0.010339263255536255, 0.014815973510193174]`), exactly as in M1c — the
leftover curvature is a within-stratum phenomenon, not a between-share one.

The φ² companion (executor-added, routes nothing) also fires at `-0.012377098889152529`
`[-0.021250484030500706, -0.0035455613757951142]`. That is expected and carries no coordinate information: *within* a
share stratum r and φ are monotone re-parametrisations of each other, so
curvature in one implies curvature in the other. The coordinate question is
settled **across** shares, and that is exactly what the `F0`-vs-`Fφ` LOO
comparison does.

**Routing: M2 DEFERRED -- sealing an incomplete family is sealing glue.**

---

## The two pre-signed readings

### The V-shadow demonstration — pre-signed positive, and it is

| quantity | value |
|---|---|
| form | `field = lambda*r^q (no V term, no intercept)` |
| starts | 18 |
| lambda_shadow | 0.24130152947263367 |
| lambda_shadow 95% CI | [0.23605675907190182, 0.24699380206781016] |
| **q_shadow** | **2.24488769944643** |
| **q_shadow 95% CI** | **[2.1768337883424214, 2.318980336007031]** |
| pre-signed direction | q_shadow > 0 |
| pre-signed direction CONFIRMED | True |
| the winner's own exponent, for contrast | 1.372031438858951 |
| in-sample RMSE of the shadow | 0.02157946817434354 |

Fit `field = λ·r^q` on M1c's own 20 cells with **no tax term and no
intercept** and the exponent comes back at **`2.24488769944643`**, CI
`[2.1768337883424214, 2.318980336007031]` — strongly positive, pre-signed direction **confirmed**, and
in fact *above* the response band `[1.71, 1.98]` on the high side. The winner's
own exponent on the same 20 cells is `1.372031438858951`, and M1c's was `-0.15040108849226472`.

This is the re-attribution in one number, in-corpus: omit the variance tax and
the same data produce a large positive exponent. The response-grade band was
measured where r and V move in lockstep, and this is what that does. The shadow
fits badly on its own terms (RMSE `0.02157946817434354` against the winner's `0.0025054232543959215`) — it is a demonstration, not a rival, and it
adjudicates nothing.

### Legacy retrodiction — and it is better than K2f's own refit

| form / reference | no-refit RMSE on K2f's 26 rows |
|---|---|
| F1 | 0.0056954308382002605 |
| F1e | 0.005699989746733798 |
| F2 | 0.005604357102432524 |
| F3 | 0.006428578997454841 |
| F0 (**winner**) | 0.0059526106645589934 |
| Fphi | 0.006280786394748213 |
| the SEALED T4 composite (no refit, K2f's baseline) | 0.11259090547752257 |
| K2f's own REFIT LOO (a refit reference, not a like-for-like rival) | 0.0061559195350209 |
| winner's improvement factor vs the sealed form | 18.914542176909535 |

The winner, with **no refit**, predicts K2f's 26 legacy compiled rows at RMSE
`0.0059526106645589934` against the sealed T4 composite's `0.11259090547752257` — a
factor of **18.914542176909535**. It also comes in **below K2f's own refit LOO of
`0.0061559195350209`** (True), which is the stronger
statement: parameters estimated on a decollinearized factorial transfer to a
different corpus, on a different design, without adjustment, and beat what that
corpus could do by fitting itself. Scoped as the registration scopes it —
same-instrument extrapolation across corpora, descriptive, adjudicating nothing.

---

## Routing — the rule-16 table, reproduced verbatim

| # | condition | outcome |
|---|---|---|
| 1 | any G0d mismatch | STOP (citation defect; no fit) |
| 2 | incumbents stand AND winner r^2 quiet | FAMILY_STANDS -- M2 seals the M1c pair (F1e+F1 co-sealed per rule 26) |
| 3 | incumbents stand AND r^2 fires | INCOMPLETE_UNREPAIRED -- M2 deferred; M1e (shape study) named |
| 4 | F0 wins AND r^2 quiet | COMPLETED_IN_R -- T4 keeps the r-coordinate with an intercept; M2 seals F0 |
| 5 | Fphi wins AND r^2 quiet | COORDINATE_RETYPED_TO_PHI -- the level law's second argument is state dynamics, not card readability; M2 seals Fphi |
| 6 | an extension wins AND r^2 fires | **COMPLETED_BUT_INCOMPLETE -- M2 deferred; M1e named**  <-- THIS LEG |
| -- | F0/Fphi tie (<5% LOO) | CO_WINNERS -- both sealed in M2 (multiple predictions inside one hashed file, K2f precedent); verdicts co-adjudicated, disagreements SPLIT |
| -- | L-3d disjoint | modifier TAX_SHIFT -> M3's charter |

## Gates

| gate | PASS | detail |
|---|---|---|
| G0d | True | (i) all 20 cell means and SEMs re-derived bit-exactly from the rawest per-world artifacts; (ii) 30 adjudication citations + the Spearman vector + the share-.60 rise; (iii) the theory band |
| G1d | True | six-form table with the nesting statement written before any fit; rule-22 sides declared; every report table generated |
| G3d | True | stage estimates written in Part 0; no stage approached its 2x threshold |

## Sides declared in Part 0 (rule 22)

| clause | statement | sided | improvement side |
|---|---|---|---|
| L-1d | an EXTENSION (F0 or Fphi) beats ALL FOUR incumbents on leave-one-cell-out RMSE | one-sided | the extension wins |
| L-2d | Fphi vs F0 as the LOO winner -- the coordinate question | two-sided; either answer re-types theory (appendix X.4) | neither |
| L-3d | the winner's kappa CI overlaps M1c's [0.7356727662590873, 0.7846243216827854] -- the fifth appearance | two-sided overlap | neither |
| L-4d | the winner's within-share r^2-residual CI contains 0 => the family is COMPLETE (routes M2); fires => M2 is DEFERRED | reading that ROUTES | contains 0 is complete |
| reading: V-shadow | field = lambda*r^q with NO V and NO intercept; pre-signed q_shadow > 0 | pre-signed direction, adjudicates nothing | n/a |
| reading: legacy retrodiction | the winner's no-refit RMSE on K2f's 26 compiled rows vs the sealed 0.11259090547752257 and K2f's refit LOO 0.0061559195350209 | descriptive, adjudicates nothing | n/a |

## The cells and the winner's residuals

| cell | share | phi | r_pred | V_person | mean field | SEM | residual (winner) |
|---|---|---|---|---|---|---|---|
| s0.10_p0.05 | 0.1 | 0.05 | 0.8189581462487876 | 0.03000000000000001 | 0.1585891652101896 | 0.0018743992250782693 | 0.00040970577496413085 |
| s0.10_p0.30 | 0.1 | 0.3 | 0.8155586799827954 | 0.03000000000000001 | 0.16035538669822857 | 0.0020066026535869932 | 0.0019371257875289427 |
| s0.10_p0.60 | 0.1 | 0.6 | 0.8075174172340943 | 0.03000000000000001 | 0.16156034289722412 | 0.0019744651453781504 | 0.002578683995600961 |
| s0.10_p0.85 | 0.1 | 0.85 | 0.7908869485651705 | 0.03000000000000001 | 0.16512469544098618 | 0.001983741777975856 | 0.004984474546814749 |
| s0.10_p0.98 | 0.1 | 0.98 | 0.7718092954224756 | 0.03000000000000001 | 0.15987119532439534 | 0.0018913572625018093 | -0.0015869443353383472 |
| s0.25_p0.05 | 0.25 | 0.05 | 0.785015540293945 | 0.07500000000000002 | 0.12162744485545209 | 0.0017778785791358425 | -0.0039691913748272495 |
| s0.25_p0.30 | 0.25 | 0.3 | 0.7761302864207245 | 0.07500000000000002 | 0.12295515685269942 | 0.001799144985921348 | -0.0032550649311818836 |
| s0.25_p0.60 | 0.25 | 0.6 | 0.7558507450373838 | 0.07500000000000002 | 0.12714790436588774 | 0.0017053615065044834 | -0.00045295521658011983 |
| s0.25_p0.85 | 0.25 | 0.85 | 0.7168731389294273 | 0.07500000000000002 | 0.13204663807737851 | 0.0018782693723257374 | 0.0018119437956124196 |
| s0.25_p0.98 | 0.25 | 0.98 | 0.6763691758553391 | 0.07500000000000002 | 0.13201888792665142 | 0.0018133362157806163 | -0.0008968534754936475 |
| s0.40_p0.05 | 0.4 | 0.05 | 0.7411873080384952 | 0.12000000000000004 | 0.09025343262511598 | 0.0017452922267459832 | -0.0033938916938938274 |
| s0.40_p0.30 | 0.4 | 0.3 | 0.726425348215848 | 0.12000000000000004 | 0.09132685344495504 | 0.0016796177194939308 | -0.0033167150237825294 |
| s0.40_p0.60 | 0.4 | 0.6 | 0.6941115392115328 | 0.12000000000000004 | 0.0980498887620882 | 0.0015916871722070262 | 0.0012518757961933885 |
| s0.40_p0.85 | 0.4 | 0.85 | 0.6367206581308248 | 0.12000000000000004 | 0.0992713149259878 | 0.0017741240206580028 | -0.0012611594807709903 |
| s0.40_p0.98 | 0.4 | 0.98 | 0.5825497814736654 | 0.12000000000000004 | 0.10169041646048367 | 0.0017444660987341613 | -0.0022540119789751234 |
| s0.60_p0.05 | 0.6 | 0.05 | 0.6573448847694047 | 0.18000000000000005 | 0.05410832013119198 | 0.001773830076330116 | 0.0015046670808402038 |
| s0.60_p0.30 | 0.6 | 0.3 | 0.6346912945232521 | 0.18000000000000005 | 0.057429784543359674 | 0.0015865768513429728 | 0.0033680953206026154 |
| s0.60_p0.60 | 0.6 | 0.6 | 0.5883719155687073 | 0.18000000000000005 | 0.06031911254293101 | 0.0016085232676605703 | 0.003336561672722109 |
| s0.60_p0.85 | 0.6 | 0.85 | 0.5151304058057474 | 0.18000000000000005 | 0.061787884770662806 | 0.0015046764572937737 | 0.00036071538536978226 |
| s0.60_p0.98 | 0.6 | 0.98 | 0.4541409476972356 | 0.18000000000000005 | 0.063796931786496 | 0.0016195393028748909 | -0.0011570616455126997 |

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

This leg drew no worlds, so the hypothesis-relevant boundary is the `fit` stage;
Part 0 is entirely verification of already-published numbers, and every RN note
was pinned there.

- **A-1 — the interpreter (before Part 0).** The environment pinned in M4-M1 and
  reused since is reused again verbatim: CPython 3.12.12 from
  `requirements-lock-main.txt` (numpy `2.4.4`, pandas `3.0.2`, scipy
  `1.17.1`), platform `macOS-26.4.1-arm64-arm-64bit`.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage ran
  as its own foreground command under an explicit harness-level timeout.
- **A-3 — the winner's parameters are jointly non-identified (at the fit).** The
  headline caveat above, reported in full rather than buried: `q` CI width
  `2.622606460876056`, `λ` width `1.4634213026939769`, `c` width `1.4721493526878324`,
  while κ stays tight at `0.05818888407589973`. Found when the winner's bootstrap
  CIs were first read, and it changes no verdict — L-4d defers M2 on independent
  grounds — but it is the single most consequential number in this report.
- **A-4 — the CO_WINNERS call landed 0.92 points outside its bar (at the fit).**
  5.916868553169516% against a 5.0% tie bar. Decided by the
  registered rule; disclosed because a slightly different corpus would have
  routed to `CO_WINNERS`.
- **A-5 — rule 26 fired on its first opportunity (at the fit).** Not an anomaly
  in the defect sense; recorded because a rule enacted one leg earlier changed
  this leg's bootstrap set automatically, and that is worth having on the record.
- **A-6 — no stage approached its 2× stop-and-report threshold.** Part 0
  `1.201097011566162` s against 120 s; the fit and the rule-13 re-run inside
  their estimates.

| stage | registration estimate (s) | executor estimate (s) | measured (s) |
|---|---|---|---|
| part0 | 120 | 120 | 1.201 |
| fit | 240 | 240 | 117.773 |
| rule13 | -- | 240 | 71.449 |
| finalize | 60 | 60 | 0.025 |

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

---

## What the planner should carry forward

**The completion question is answered YES, and the coordinate question is
answered r.** One free intercept beats the whole incumbent family, and the
state-dynamics coordinate `Fφ` loses even to the incumbents. Appendix X.4's
occasion-structure hypothesis gets no support here; the level law's second
argument is card readability, with a constant.

**The exponent claim from M1c must be weakened, and this leg is why.** M1c
reported `q = -0.15040108849226472` `[-0.18322395953281184, -0.11871900002844447]` and the record should now read: *the
field falls monotonically in r at fixed V — that is robust across every form
tried — but the exponent that describes the fall is not identified once the
family is allowed the constant it demonstrably wants.* `F0` reaches the same
monotone shape from the opposite corner (`λ = -0.055190882521519`, `q = 1.372031438858951`),
and its `q` interval `[0.021913588793404413, 2.6445200496694605]` spans nearly the whole plausible range.
The dissociation verdict (`LEVEL_RESPONSE_DISSOCIATION`) survives — it rests on
the *sign* of the r-dependence and on the V-shadow contrast, not on the
exponent's value — but any sentence quoting a level exponent as a constant
should be re-scoped.

**κ is the durable object.** Fifth independent appearance, `0.7766770259880144`
`[0.7482226203832176, 0.8064115044591174]`, and the only sharply identified parameter in the winning form.
M3's one-κ question is the best-supplied question in the line.

**M2 is deferred, correctly.** L-4d fires, so sealing now would seal an
incomplete family — the D-open lesson the registration cites. M1e (the shape
study) is named. Two concrete inputs for it: the leftover curvature is
**within-share only** (pooled r² quiet at `0.001054754288525179` `[-0.010339263255536255, 0.014815973510193174]`),
and it survived the intercept at 36.90141692114467% reduced amplitude, so the
missing term is a within-stratum shape in r, not a between-share effect.

**Registration-defect candidate: one, non-blocking.** Cells 4 and 5 route a
winning extension straight to "M2 seals F0 / seals Fφ" **with no identification
requirement on the sealed parameters**. Had the r² probe come back quiet, this
leg would have routed to `COMPLETED_IN_R` and handed M2 a form whose exponent
interval is `[0.021913588793404413, 2.6445200496694605]` — a seal on a ridge. Nothing turned on it because
L-4d fired independently, but the routing selects on predictive accuracy (LOO)
while the downstream use (a prospective seal) needs identified parameters, and
those are different properties. This is the same shape as the defects that
bought rules 25 and 26: a gate that does not check the property its consumer
requires. A successor registration should either add an identification clause to
the sealing cells or state explicitly that a seal may be issued on a
non-identified parameterisation.
