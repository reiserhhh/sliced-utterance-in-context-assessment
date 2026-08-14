# M4-M3 — the tax curve

**Leg:** M4-M3 · **Registered** 2026-08-11 in
`docs/SUICA_M4_M_LEVEL_LAW_LINE_PLAN.md` (section "M4-M3 — the tax curve"),
commit `d552bd5`, BEFORE this run. The M-line's final chartered leg.
**Executor:** dispatched agent (implementation and execution only; the
registration text is binding).
**Harness:** `scripts/run_suica_m4_m3_tax_curve.py`.
**Artifacts:** `results/m4_m3_tax_curve/` (gitignored).
**Banner:** synthetic worlds on K2b's frozen instrument, exploratory, label-free;
the tax curve and the six-target retrodiction closure.

**Verdict: `TAX_IS_A_CURVE` (rule-16 cell 3); modifier(s) `[CLOSURE_EXPLAINED]`.**
Curve consumption status: **CONSUMABLE**. 3072 fresh worlds
(192 per cell across 16 cells).

The question was refined by rule 28 out of "is κ one number" into **is the local
tax κ(V) = −dα/dV constant, and does ONE law retrodict every published κ̂
through each representation's own estimator?** Both halves answer.

**The tax is not a constant — it is a curve, and the curve was predicted before
it was measured.** A-quad wins leave-one-share-out at `0.001405398973367856` against A-lin's
`0.003599294048156043`, and its curvature term `κ2 = 1.562877770472943` has a 95% interval
`[1.0324533419318935, 2.119753814549891]` that **excludes zero** — stable at B = 20000 (`[1.0132571446499121, 2.1165781162197774]`). Both of L-1m3's clauses fire
together (True), which is cell 3.

**And one law retrodicts five of the six published κ̂ values.**
5/6 hits → **CLOSURE_EXPLAINED**, with the pre-signed direction on target 6
holding (True): the representation that omits the r-channel is
retrodicted LOW, exactly as appendix AA said it would be. The constant-κ era
does not end because someone doubted it; it ends because a curve explains where
each of its six "constants" came from.

---

## Part 0 — before any world

### 0.1 Conventions pinned in writing

| note | pinned reading |
|---|---|
| RN-M3-1 | the projection's kappa2 interval is the OLS 95% t-interval (A-quad is exactly linear in (c, kappa0, kappa2)); the MAIN analysis uses the registered full-pipeline bootstrap -- disclosed |
| RN-M3-2 | alpha_s averages both phi-cells so its projection sd is sigma_w/sqrt(2n): sigma_w/sqrt(384) at n=192, sigma_w/sqrt(768) at 384 |
| RN-M3-3 | A-lin's truth intercept is the SSE-minimising c at the pinned chord kappa (the line through the four points' centroid); kappa2's null does not depend on c |
| RN-M3-4 | A-sat starts pinned (c x A x tau = 24); A-lin and A-quad solved in closed form with a least_squares witness agreeing to 1e-10 |
| RN-M3-5 | rule-27 budgets mapped across forms: A-quad (c, kappa0, kappa2) all budgeted; A-lin's single kappa held to the kappa0 bar; A-sat's (A, tau) reported without a declared budget; the 8 alpha widths always budgeted |
| RN-M3-6 | the closure's MC second reading uses B_MC = 200 per target at sigma_w/sqrt(n) per design point, seed = master; the NOISELESS run is the registered pinned link and is what scores |
| RN-M3-7 | the #49 retro-check scans every persisted per-world recovery_b_only in the M-line's pilot/smoke artifacts plus K2f's pilot; M2's own already-adjudicated C1 world is reported separately and REOPEN fires only on a breach outside it |
| RN-M3-8 | pair sides for targets 1-2 come from K2f's compiled_rows.csv by row_id, with the mapping and the sign convention (dvar = V_a - V_b, D = field_a - field_b, published kappa = MINUS the through-origin slope) VERIFIED bit-exactly against the persisted rows before any retrodiction |

### 0.2 G0m3 — the design, the citations, the targets, the retro-check

| share | V (planner) | V (re-derived) | r(phi=.05) | r(phi=.60) | bit-exact | both r interior |
|---|---|---|---|---|---|---|
| 0.1 | 0.03000000000000001 | 0.03000000000000001 | 0.8189581462487876 | 0.8075174172340943 | True | True |
| 0.175 | 0.05250000000000001 | 0.05250000000000001 | 0.8029938537206762 | 0.7827569526268938 | True | True |
| 0.25 | 0.07500000000000002 | 0.07500000000000002 | 0.785015540293945 | 0.7558507450373838 | True | True |
| 0.325 | 0.0975 | 0.0975 | 0.7645994805478157 | 0.7264504152667802 | True | True |
| 0.4 | 0.12000000000000004 | 0.12000000000000004 | 0.7411873080384952 | 0.6941115392115328 | True | True |
| 0.5 | 0.15000000000000002 | 0.15000000000000002 | 0.7039654030974909 | 0.6453873930804982 | True | True |
| 0.6 | 0.18000000000000005 | 0.18000000000000005 | 0.6573448847694047 | 0.5883719155687073 | True | True |
| 0.7 | 0.21000000000000005 | 0.21000000000000005 | 0.5967380569813433 | 0.5197539933932338 | True | True |

| clause | adjudication | persisted | bit-exact |
|---|---|---|---|
| C1 mean | 0.034417674625862156 | 0.034417674625862156 | True |
| C1 world sd | 0.018618930632302133 | 0.018618930632302133 | True |
| C2 mean | 0.04354391388413511 | 0.04354391388413511 | True |
| P1 measured | 0.009126239258272953 | 0.009126239258272953 | True |
| P1 position | 0.8671810125388784 | 0.8671810125388784 | True |
| P1 predicted | 0.003242277707985443 | 0.003242277707985443 | True |
| P2 position | -0.23801652307153248 | -0.23801652307153248 | True |
| P3 position | -0.3679279607468678 | -0.3679279607468678 | True |
| predictions sha256 | 'd03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2' | 'd03e180919e2e2b1f08c7bde77c835d48b8c59177220085f1de1d39765f46ef2' | True |
| replication bar | 0.005647466456046939 | 0.005647466456046939 | True |
| replication delta | 0.0007701504312663671 | 0.0007701504312663671 | True |
| seconds stamp to permit | 176.076157 | 176.076157 | True |
| stress band hi | 0.04211861836310243 | 0.04211861836310243 | True |
| stress band lo | 0.03435630613483847 | 0.03435630613483847 | True |
| alpha vector + theta* | [0.18560847593788873, 0.1456494891347315, 0.10934916761257428, 0.06667603971206824] | [0.18560847593788873, 0.1456494891347315, 0.10934916761257428, 0.06667603971206824] | True |
| pair mapping (dvar = V_a - V_b, D = level_a - level_b) | bit-exact | True | True |

| # | target | published | CI | persisted | bit-exact | typed | source |
|---|---|---|---|---|---|---|---|
| 1 | sealed difference-fit (K2d 6-pair OLS through origin) | 0.7220359963712748 | None | 0.7220359963712748 | True | point-only, tol 0.03 | results/m4_k2d_frontier_carrier/post_hoc_descriptive.json:kappa_ols_through_origin (negated) |
| 2 | K2e 9-pair refit | 0.7145934082034173 | None | 0.7145934082034173 | True | point-only, tol 0.03 | results/m4_k2e_double_matching/decision.json:kappa_refit_9pairs.kappa (negated) |
| 3 | K2f F2 | 0.750086268225045 | [0.5202855978239498, 0.8612166024267973] | 0.750086268225045 | True | CI | results/m4_k2f_level_law/fits.json:fits.F2 |
| 4 | M1c F1e | 0.7601952008701406 | [0.7356727662590873, 0.7846243216827854] | 0.7601952008701406 | True | CI | results/m4_m1c_r_at_level/fits.json:fits.F1e |
| 5 | M1d F0 | 0.7766770259880144 | [0.7482226203832176, 0.8064115044591174] | 0.7766770259880144 | True | CI | results/m4_m1d_form_completion/fits.json:fits.F0 |
| 6 | M1e E-tax-add | 0.6761549415814 | [0.6619291032569563, 0.6901486195533926] | 0.6761549415814 | True | CI | results/m4_m1e_shape/fits.json:fits.E-tax-add |

**G0m3(v), the #49 retro-check.** Rule 29 was bought by M2's unpinned
saturation predicate; the retroactive question was whether the latent
strictly-inside-(0,1) convention had ever been consequential before. Mechanical
scan of every persisted pilot and smoke world in the M-line and K2f:

| source | worlds | min | max | breaches of (0,1) | already adjudicated |
|---|---|---|---|---|---|
| K2f pilot | 2 | 0.09868106447957786 | 0.1122568775501732 | 0 | False |
| M1b pilot | 16 | 0.032980259309520595 | 0.1865514428385202 | 0 | False |
| M2 pilot (already adjudicated) | 8 | -0.0007988006295671071 | 0.14616608829944613 | 1 | True |
| M1c smoke cell_s0.10_p0.05_w000 | 1 | 0.17498114852708657 | 0.17498114852708657 | 0 | False |
| M1c smoke cell_s0.10_p0.30_w000 | 1 | 0.1569494929650918 | 0.1569494929650918 | 0 | False |
| M1c smoke cell_s0.10_p0.60_w000 | 1 | 0.16281859277546176 | 0.16281859277546176 | 0 | False |
| M1c smoke cell_s0.10_p0.85_w000 | 1 | 0.2185586200475063 | 0.2185586200475063 | 0 | False |
| M1c smoke cell_s0.10_p0.98_w000 | 1 | 0.1542650550061626 | 0.1542650550061626 | 0 | False |
| M1c smoke cell_s0.25_p0.05_w000 | 1 | 0.10348490302881162 | 0.10348490302881162 | 0 | False |
| M1c smoke cell_s0.25_p0.30_w000 | 1 | 0.07566730885223151 | 0.07566730885223151 | 0 | False |
| M1c smoke cell_s0.25_p0.60_w000 | 1 | 0.16168687582427954 | 0.16168687582427954 | 0 | False |
| M1c smoke cell_s0.25_p0.85_w000 | 1 | 0.09481201588281661 | 0.09481201588281661 | 0 | False |
| M1c smoke cell_s0.25_p0.98_w000 | 1 | 0.10299880595458599 | 0.10299880595458599 | 0 | False |
| M1c smoke cell_s0.40_p0.05_w000 | 1 | 0.05403679026035842 | 0.05403679026035842 | 0 | False |
| M1c smoke cell_s0.40_p0.30_w000 | 1 | 0.07825542431908399 | 0.07825542431908399 | 0 | False |
| M1c smoke cell_s0.40_p0.60_w000 | 1 | 0.11132157264961358 | 0.11132157264961358 | 0 | False |
| M1c smoke cell_s0.40_p0.85_w000 | 1 | 0.07872737096075372 | 0.07872737096075372 | 0 | False |
| M1c smoke cell_s0.40_p0.98_w000 | 1 | 0.055669178150385565 | 0.055669178150385565 | 0 | False |
| M1c smoke cell_s0.60_p0.05_w000 | 1 | 0.05960777371841888 | 0.05960777371841888 | 0 | False |
| M1c smoke cell_s0.60_p0.30_w000 | 1 | 0.04855869685788776 | 0.04855869685788776 | 0 | False |
| M1c smoke cell_s0.60_p0.60_w000 | 1 | 0.07120959804170686 | 0.07120959804170686 | 0 | False |
| M1c smoke cell_s0.60_p0.85_w000 | 1 | 0.049302373750007844 | 0.049302373750007844 | 0 | False |
| M1c smoke cell_s0.60_p0.98_w000 | 1 | 0.03435936982788742 | 0.03435936982788742 | 0 | False |
| **totals** | 46 | — | — | outside M2: 0 | REOPEN: False |

46 worlds across 23 sources; **0
breaches outside M2's own already-adjudicated case**, so **REOPEN =
False**. The convention was latent but never consequential until M2 walked
into the one cell extreme enough to expose it.

### 0.3 G3m3(b) — the projection gate, passed before any world

| configuration | P(kappa2 CI excludes 0) | alpha sd | truth theta |
|---|---|---|---|
| n=192 truth A-lin | 0.0575 | 0.0013721959035731767 | [0.2071001875517445, 0.7928829081721366] |
| n=192 truth A-quad | 0.9935 | 0.0013721959035731767 | [0.21429311564963677, 0.9833070071661382, 1.813410134121013] |
| n=192 PASS | True | — | — |
| escalated | not run | — | — |

At n = 192 the design has **P(κ2 CI excludes 0) = 0.9935**
under the A-quad truth (bar ≥ 0.8) and **0.0575** under the A-lin truth
(bar ≤ 0.1). Escalation fired: **False**. The two truths were computed
from M1e's own four α points, and they reproduce the planner's sanity values:
A-quad `[0.21429311564963677, 0.9833070071661382, 1.813410134121013]` against the planner's (0.983, 1.815), A-lin
`[0.2071001875517445, 0.7928829081721366]` against a chord of 0.7929.

This gate is the rule-25 discipline at its sharpest: it demanded not only power
to *detect* curvature but a bounded false-positive rate *against* the linear
truth. Both bars were met before a single world existed.

---

## The measurement

| cell | share | phi | r | V | n | mean | SEM |
|---|---|---|---|---|---|---|---|
| s0.100_p0.05 | 0.1 | 0.05 | 0.8189581462487876 | 0.03000000000000001 | 192 | 0.15503663245702132 | 0.0018881246773076444 |
| s0.100_p0.60 | 0.1 | 0.6 | 0.8075174172340943 | 0.03000000000000001 | 192 | 0.16050172447234926 | 0.001835339482567283 |
| s0.175_p0.05 | 0.175 | 0.05 | 0.8029938537206762 | 0.05250000000000001 | 192 | 0.14219691706919665 | 0.0019801362902652593 |
| s0.175_p0.60 | 0.175 | 0.6 | 0.7827569526268938 | 0.05250000000000001 | 192 | 0.1400357762199323 | 0.001986947059102197 |
| s0.250_p0.05 | 0.25 | 0.05 | 0.785015540293945 | 0.07500000000000002 | 192 | 0.12797234770298807 | 0.0019162976905865861 |
| s0.250_p0.60 | 0.25 | 0.6 | 0.7558507450373838 | 0.07500000000000002 | 192 | 0.1223167951631557 | 0.0019237016817914968 |
| s0.325_p0.05 | 0.325 | 0.05 | 0.7645994805478157 | 0.0975 | 192 | 0.1056883255581428 | 0.0017109816039548574 |
| s0.325_p0.60 | 0.325 | 0.6 | 0.7264504152667802 | 0.0975 | 192 | 0.10878503319046211 | 0.0018188991255204557 |
| s0.400_p0.05 | 0.4 | 0.05 | 0.7411873080384952 | 0.12000000000000004 | 192 | 0.08824684617320167 | 0.001863646937893989 |
| s0.400_p0.60 | 0.4 | 0.6 | 0.6941115392115328 | 0.12000000000000004 | 192 | 0.09507724679969569 | 0.0017853676975026682 |
| s0.500_p0.05 | 0.5 | 0.05 | 0.7039654030974909 | 0.15000000000000002 | 192 | 0.06988982238173076 | 0.001494625026185797 |
| s0.500_p0.60 | 0.5 | 0.6 | 0.6453873930804982 | 0.15000000000000002 | 192 | 0.07501665297939127 | 0.0015189975802614255 |
| s0.600_p0.05 | 0.6 | 0.05 | 0.6573448847694047 | 0.18000000000000005 | 192 | 0.05160862889492087 | 0.0015372352692916836 |
| s0.600_p0.60 | 0.6 | 0.6 | 0.5883719155687073 | 0.18000000000000005 | 192 | 0.062106356924006324 | 0.0015975195656201284 |
| s0.700_p0.05 | 0.7 | 0.05 | 0.5967380569813433 | 0.21000000000000005 | 192 | 0.03813671717357525 | 0.0013592014496704254 |
| s0.700_p0.60 | 0.7 | 0.6 | 0.5197539933932338 | 0.21000000000000005 | 192 | 0.039290404889435776 | 0.001456552705862797 |

### The α margin, with the channel held fixed

α̂_s is the mean over both φ-cells of `(per-world field − λ·r^q)` at the
M2-sealed transfer point θ* = (-0.057625974791364554, 3.863625377453229). Holding the
channel fixed is what makes α̂ a *measurement* of the margin rather than a
co-estimate entangled with the ridge.

| share | V | alpha | 95% CI | width | budget 0.012 |
|---|---|---|---|---|---|
| 0.1 | 0.03000000000000001 | 0.18370209590141692 | [0.18119627346170109, 0.18627669408475203] | 0.005080420623050946 | True |
| 0.175 | 0.05250000000000001 | 0.1646438076465816 | [0.1619985602228714, 0.16742077261016663] | 0.005422212387295233 | True |
| 0.25 | 0.07500000000000002 | 0.1462242742376615 | [0.14356464976955688, 0.14879276566912444] | 0.005228115899567565 | True |
| 0.325 | 0.0975 | 0.12583312476359476 | [0.12332717996363957, 0.128156091067781] | 0.004828911104141437 | True |
| 0.4 | 0.12000000000000004 | 0.10774977588095545 | [0.10518189313431744, 0.11031074932155709] | 0.0051288561872396415 | True |
| 0.5 | 0.15000000000000002 | 0.0851827816812592 | [0.08310944957945908, 0.08729802308383595] | 0.004188573504376875 | True |
| 0.6 | 0.18000000000000005 | 0.06626602979113068 | [0.06415096625389283, 0.06833943842683231] | 0.004188472172939481 | True |
| 0.7 | 0.21000000000000005 | 0.044932685277189494 | [0.0430021644650165, 0.046821180917192055] | 0.0038190164521755554 | True |

### The seven local slopes — the object the leg exists to measure

| adjacent pair | local tax -dalpha/dV | 95% CI | SE |
|---|---|---|---|
| V np.float64(0.03000000000000001) -> np.float64(0.05250000000000001) | 0.8470350335482366 | [0.6800807424013489, 1.008335293523524] | 0.08228827432703278 |
| V np.float64(0.05250000000000001) -> np.float64(0.07500000000000002) | 0.8186459292853376 | [0.6471779868223625, 0.9943388462246379] | 0.08852946654783284 |
| V np.float64(0.07500000000000002) -> np.float64(0.0975) | 0.9062733099585221 | [0.7478802146416385, 1.0710587566117746] | 0.08183935614656554 |
| V np.float64(0.0975) -> np.float64(0.12000000000000004) | 0.803704394783968 | [0.6431170331422652, 0.9534430316189673] | 0.08049581098851653 |
| V np.float64(0.12000000000000004) -> np.float64(0.15000000000000002) | 0.7522331399898755 | [0.6427816109645895, 0.8609620855529402] | 0.05489058747090618 |
| V np.float64(0.15000000000000002) -> np.float64(0.18000000000000005) | 0.6305583963376168 | [0.530477632229581, 0.7307573107450264] | 0.05099045778018744 |
| V np.float64(0.18000000000000005) -> np.float64(0.21000000000000005) | 0.7111114837980396 | [0.6129872669295084, 0.8084257788284175] | 0.049463026574777524 |

The slopes run [0.8470350335482366, 0.8186459292853376, 0.9062733099585221, 0.803704394783968, 0.7522331399898755, 0.6305583963376168, 0.7111114837980396]. They decline from `0.8470350335482366` at the low-V end to `0.7111114837980396` at the
high-V end (minimum `0.6305583963376168`) — the decline the planner's pre-run arithmetic predicted from
M1e's four points. **NON_MONOTONE = False** (0
violations beyond joint 95% CIs): the sequence wobbles, but no adjacent increase
survives its own interval, so the decline is not contradicted anywhere.

### The three curve forms

| form | expression | parameters | 95% CI | in-sample RMSE | LOO-share RMSE | lstsq witness |
|---|---|---|---|---|---|---|
| A-lin | `alpha = c - kappa*V` | c = 0.20397046188463158, kappa = 0.7729279998877195 | c [0.2020720092911644, 0.20590156164311896], kappa [0.7592849554311365, 0.7862645893531095] | 0.002519055578163362 | 0.003599294048156043 | 1.16e-11 |
| **A-quad (winner)** | `alpha = c - kappa0*V + (kappa2/2)*V^2` | c = 0.21247398265278816, kappa0 = 0.9601680204204508, kappa2 = 1.562877770472943 | c [0.2089174011834685, 0.21623033411776654], kappa0 [0.8935297536704152, 1.0313114338425122], kappa2 [1.0324533419318935, 2.119753814549891] | 0.0008537645237249864 | 0.001405398973367856 | 7.03e-11 |
| A-sat | `alpha = c + A*exp(-V/tau)` | c = -0.27493651728760515, A = 0.4878776246525967, tau = 0.4983722810248614 | c [-0.4709831721670969, -0.1711401781832364], A [0.3874886249097597, 0.6812490681992006], tau [0.36462126155307284, 0.7547908644742626] | 0.0008758190781930637 | 0.0014509897412261284 | n/a (nonlinear) |

A-quad wins; A-sat is True-close (the tie rule is active between the two
**curved** forms, which cannot touch L-1m3's clause — that clause asks whether a
curved form beats A-lin, and both do). A-lin is 2.5610478706490034x worse on LOO. Note A-sat's
own parameters are far less interpretable (`c` negative, τ ≈ 0.5) and it carries
no declared budget for (A, τ) — the registered budgets attach to the quadratic
parameterisation, which is the one the theory table would quote.

| quantity | value | bar | scale | within 5% |
|---|---|---|---|---|
| LOO separation winner vs runner-up | 4.559076785827249e-05 | 0.0 | 0.001405398973367856 | True |
| A-quad kappa2 CI nearest endpoint vs 0 | 1.0324533419318935 | 0.0 | 1.562877770472943 | False |
| rule-27 budget: c | 0.00731293293429805 | 0.03 | 0.03 | False |
| rule-27 budget: kappa0 | 0.13778168017209702 | 0.25 | 0.25 | False |
| rule-27 budget: kappa2 | 1.0873004726179973 | 1.5 | 1.5 | False |
| rule-27 budget: alpha(share 0.1) | 0.005080420623050946 | 0.012 | 0.012 | False |
| rule-27 budget: alpha(share 0.175) | 0.005422212387295233 | 0.012 | 0.012 | False |
| rule-27 budget: alpha(share 0.25) | 0.005228115899567565 | 0.012 | 0.012 | False |
| rule-27 budget: alpha(share 0.325) | 0.004828911104141437 | 0.012 | 0.012 | False |
| rule-27 budget: alpha(share 0.4) | 0.0051288561872396415 | 0.012 | 0.012 | False |
| rule-27 budget: alpha(share 0.5) | 0.004188573504376875 | 0.012 | 0.012 | False |
| rule-27 budget: alpha(share 0.6) | 0.004188472172939481 | 0.012 | 0.012 | False |
| rule-27 budget: alpha(share 0.7) | 0.0038190164521755554 | 0.012 | 0.012 | False |

| form | 95% CI at B=20000 | at B=2000 |
|---|---|---|
| A-quad | {'c': [0.2087384851307659, 0.216205692791952], 'kappa0': [0.8910240748289984, 1.029453776586949], 'kappa2': [1.0132571446499121, 2.1165781162197774]} | {'c': [0.2089174011834685, 0.21623033411776654], 'kappa0': [0.8935297536704152, 1.0313114338425122], 'kappa2': [1.0324533419318935, 2.119753814549891]} |
| A-sat | {'A': [0.39173286878246694, 0.69376213954976], 'c': [-0.4840133130491904, -0.17532336516582703], 'tau': [0.36829620330897056, 0.7700030333057579]} | {'A': [0.3874886249097597, 0.6812490681992006], 'c': [-0.4709831721670969, -0.1711401781832364], 'tau': [0.36462126155307284, 0.7547908644742626]} |
| kappa2 still excludes 0 | True | True |
| **verdicts stable** | **True** | — |

Rule 13 fired on the A-quad/A-sat LOO proximity and the B = 20000 re-run left
every verdict unchanged (**stable: True**).

### Rule-27 consumption budgets

| parameter | 95% CI width | budget | met |
|---|---|---|---|
| c | 0.00731293293429805 | 0.03 | True |
| kappa0 | 0.13778168017209702 | 0.25 | True |
| kappa2 | 1.0873004726179973 | 1.5 | True |
| alpha(share 0.1) | 0.005080420623050946 | 0.012 | True |
| alpha(share 0.175) | 0.005422212387295233 | 0.012 | True |
| alpha(share 0.25) | 0.005228115899567565 | 0.012 | True |
| alpha(share 0.325) | 0.004828911104141437 | 0.012 | True |
| alpha(share 0.4) | 0.0051288561872396415 | 0.012 | True |
| alpha(share 0.5) | 0.004188573504376875 | 0.012 | True |
| alpha(share 0.6) | 0.004188472172939481 | 0.012 | True |
| alpha(share 0.7) | 0.0038190164521755554 | 0.012 | True |
| **all budgeted met** | — | — | **True** |

All budgeted widths are met, so the curve is **CONSUMABLE** — it may enter
the theory table rather than being reported descriptive-only.

---

## The retrodiction closure — the centrepiece

Noiseless fields were generated from the winning curve plus the fixed channel at
**each legacy estimator's own persisted design points**, then run through **each
estimator's own pipeline** — the rule-14 link the registration pinned. No
estimator was re-implemented in a common form; each is its own code path on
law-generated data.

| # | target | published | CI / tolerance | predicted by the law | delta | HIT | estimator pipeline |
|---|---|---|---|---|---|---|---|
| 1 | sealed difference-fit (K2d 6-pair OLS through origin) | 0.7220359963712748 | \|delta\| <= 0.03 (point-only) | 0.746239389222837 | 0.024203392851562144 | **HIT** | OLS through the origin of D on dvar over 6 pairs; kappa = -slope |
| 2 | K2e 9-pair refit | 0.7145934082034173 | \|delta\| <= 0.03 (point-only) | 0.7490807810533479 | 0.03448737284993053 | miss | OLS through the origin of D on dvar over 9 pairs; kappa = -slope |
| 3 | K2f F2 | 0.750086268225045 | [0.5202855978239498, 0.8612166024267973] | 0.7679919131618126 | 0.017905644936767606 | **HIT** | F2 = lam*r^q - kap*V*r^p, NLS with K2f's start grid, 26 rows |
| 4 | M1c F1e | 0.7601952008701406 | [0.7356727662590873, 0.7846243216827854] | 0.7626119165106452 | 0.0024167156405046075 | **HIT** | F1e = lam*r^q - kap*V - eps, eps in [0, 0.05], 20 cells |
| 5 | M1d F0 | 0.7766770259880144 | [0.7482226203832176, 0.8064115044591174] | 0.7813000334879925 | 0.004623007499978127 | **HIT** | F0 = c + lam*r^q - kap*V, 20 cells |
| 6 | M1e E-tax-add | 0.6761549415814 | [0.6619291032569563, 0.6901486195533926] | 0.6795535093252197 | 0.003398567743819747 | **HIT** | c - kap*V + g_phi (sum-to-zero), OLS, 20 cells |
|  | **totals** |  |  |  |  | **5/6** | CLOSURE_EXPLAINED |

**5/6 → CLOSURE_EXPLAINED.** The one miss is target 2, the K2e 9-pair refit,
at `0.7490807810533479` against a published `0.7145934082034173` — a delta of
`0.03448737284993053` against a `0.03` point-only tolerance, so it misses by
`0.004487372849930532`. It is the *tightest* of the misses available: the same law
hits its 6-pair sibling (target 1) and every CI-typed target.

**Target 6's pre-signed direction held (True).** The M1e
tax-additive representation — which omits the r-channel — is retrodicted at
`0.6795535093252197`, the lowest of all six predictions, exactly as appendix AA
predicted from the channel-covariance loading. This is the mechanism claim
paying out: the spread among the six published κ̂ values is not six different
taxes, it is one curve seen through six estimators with different amounts of
channel leakage.

| # | noiseless (scored) | MC mean (B=200) | MC 95% CI |
|---|---|---|---|
| 1 | 0.746239389222837 | 0.7533129105056446 | [0.5197368823591441, 0.9537327091161142] |
| 2 | 0.7490807810533479 | 0.7468741437972305 | [0.5570519732430409, 0.9512707969804508] |
| 3 | 0.7679919131618126 | 0.7729791663438625 | [0.6383437886904714, 0.9139313292750456] |
| 4 | 0.7626119165106452 | 0.7649796420604426 | [0.7378403502528511, 0.7909071405549613] |
| 5 | 0.7813000334879925 | 0.779910354218849 | [0.7513177306275127, 0.8155532259031973] |
| 6 | 0.6795535093252197 | 0.679216368762612 | [0.6627332552584536, 0.6932511213849943] |

The Monte-Carlo second reading (B_MC = 200) reproduces every noiseless
value closely; the noiseless run is the registered pinned link and is what
scores.

---

## L-3m3 — the transfer check, and an honest caveat

| quantity | joint refit | fixed theta* / M1e | verdict |
|---|---|---|---|
| lambda | -0.061459553709837474 CI [-30.615714683654733, -0.039429381031983984] | -0.057625974791364554 ; M1e CI [-0.0843564122153383, -0.042724477794351616] | overlap |
| q | 1.4750960800018156 CI [0.0015341219029510228, 3.8439727902667573] | 3.863625377453229 | reported |

The joint refit's λ interval `[-30.615714683654733, -0.039429381031983984]` overlaps M1e's
`[-0.0843564122153383, -0.042724477794351616]`, so the registered verdict is **overlap** and no
`TRANSFER_BREAK` modifier fires. **But the overlap is close to vacuous and the
report says so:** the joint interval runs to `-30.615714683654733` at its lower end. Freeing
(λ, q) alongside eight α margins on 16 cell means re-creates exactly the ridge
appendix Y named — the joint fit cannot pin the channel, which is *why* the
primary estimation holds it fixed at the M2-sealed point. The transfer check
passes, and it passes weakly; a successor wanting a real transfer test needs a
design that identifies the channel independently.

## The α(0.70) triangle (reading, no gate)

| reading | alpha(0.70) | inside M3's CI |
|---|---|---|
| from M2's C1 cell | 0.04225793772553886 | False |
| from M2's C2 cell | 0.04814189927582637 | False |
| M2 spread between them | 0.00588396155028751 | — |
| **M3 fresh estimate** | **0.044932685277189494** CI [0.0430021644650165, 0.046821180917192055] | — |

M2's two cell-derived readings **bracket** M3's fresh estimate — C1 gives
`0.04225793772553886` (below), C2 gives `0.04814189927582637` (above), M3 measures
`0.044932685277189494` with CI `[0.0430021644650165, 0.046821180917192055]`, and neither M2 reading is inside
(False / False). The spread between them is `0.00588396155028751`.
The triangle does **not** close, and it fails in an informative direction: this
is the same discrepancy M2's P1 flagged when its measured contrast came in at
0.8671810125388784 of the band. At share 0.70 the channel does slightly more work than the
fixed θ* assigns it, so the two single-cell α readings straddle the truth. A
reading, adjudicating nothing — but the clearest surviving pointer for a
successor.

---

## Routing

| # | condition | outcome |
|---|---|---|
| 1 | any G0m3 mismatch | STOP (citation defect) |
| 2 | projection fails after escalation | NON_PROJECTABLE (handback; no worlds) |
| 3 | LOO prefers a curved form AND kappa2 CI excludes 0 | **TAX_IS_A_CURVE -- the constant-kappa era closes by dated note; the curve is the object**  <-- THIS LEG |
| 4 | LOO prefers A-lin AND kappa2 CI contains 0 | TAX_CONSTANT_RETAINED -- the representation spread needs a different owner (named) |
| 5 | the two clauses disagree | CURVATURE_UNSETTLED -- which clause failed is stated (power vs form); no curve claim |
| -- | closure hits >=5/6 / 3-4 / <=2 | **modifier CLOSURE_EXPLAINED / CLOSURE_PARTIAL / CLOSURE_FAILED (runs in cells 3-5 regardless)**  <-- THIS LEG |
| -- | adjacent slopes non-monotone beyond joint 95% CIs | modifier NON_MONOTONE |
| -- | L-3m3 disjoint | modifier TRANSFER_BREAK |
| -- | #49 retro-check breach | modifier REOPEN |

## Gates

| gate | PASS | detail |
|---|---|---|
| G0m3 | True | design table, M2 citations, alpha and theta*, the six targets at source, the #49 retro-check, and the pair mapping verified bit-exactly |
| G1m3 | True | rule-29 domain-pinned predicate held at all 16 cells: finite, \|x\| < 0.995, nonzero variance; NO positivity clause |
| G2m3 | True | both corners pass |
| G3m3 | True | projection gate passed before any world |
| G4m3 | True | routing reproduced verbatim; tables generated |

| cell | n | min | max | finite | any saturated | nonzero var | PASS |
|---|---|---|---|---|---|---|---|
| s0.100_p0.05 | 4 | 0.13909843411862025 | 0.21143094803031584 | True | False | True | True |
| s0.700_p0.60 | 4 | 0.01126247998639383 | 0.06715002466646873 | True | False | True | True |

G1m3 is the first gate written under **rule 29**: the predicate is pinned in the
statistic's own domain — finite, `|recovery_b_only| < 0.995`, nonzero
within-cell variance, and **no positivity clause**. It held at all 16 cells.

## Sides declared in Part 0 (rule 22)

| clause | statement | prior | sided |
|---|---|---|---|
| G3m3(b) | P(kappa2 excl 0 \| A-quad) >= 0.8 AND P(. \| A-lin) <= 0.1 | — | one-sided each |
| L-1m3 | A-lin loses LOO to a curved form AND A-quad's kappa2 CI excludes 0 | 0.65 | one-sided each |
| L-2m3 | >= 5/6 retrodiction hits | 0.5 | one-sided |
| L-3m3 | the joint-refit lambda CI overlaps M1e's [-0.0843564122153383, -0.042724477794351616] | 0.7 | two-sided overlap |

---

## Anomaly log — every anomaly, with pre/post-hypothesis timing

The hypothesis-relevant boundary is the first world. Part 0 — gates, targets,
projection — is arithmetic on published numbers, and every RN note was pinned
there.

- **A-1 — the interpreter (before Part 0).** The environment pinned in M4-M1 and
  used through the whole line: CPython 3.12.12 from
  `requirements-lock-main.txt` (numpy `2.4.4`, pandas `3.0.2`, scipy
  `1.17.1`), platform `macOS-26.4.1-arm64-arm-64bit`.
- **A-2 — `timeout(1)` absent on this platform (before Part 0).** Every stage ran
  as its own foreground command under an explicit harness-level timeout.
- **A-3 — the MC second reading overran its stage and was made cheaper (after
  the noiseless closure, before anything was written).** The first `retro`
  attempt re-ran each estimator's FULL start grid on all 200 MC replicates
  and exceeded its foreground timeout; nothing was persisted. It was rewritten
  to refit MC replicates from the noiseless optimum — the program's standing
  bootstrap convention — and the MC means agree with the killed run's partial
  output to ~9 decimal places (target 3: 0.7729791656805954 then
  0.7729791663438625; target 4: 0.7649796415507697 then 0.7649796420604426), so
  the change is a speed-up and not a different estimator. **The noiseless run,
  which is what scores, was never affected.**
- **A-4 — a rule-13 stage was missing from the first harness and was added
  (after `alpha`, before `finalize` consumed it).** The registration says
  "B = 2000; 20000 at rule-13 boundaries", and the A-quad/A-sat LOO separation
  falls inside the 5% tie band, which is such a boundary. The omission was mine;
  the re-run at B = 20000 was performed and every verdict is unchanged.
- **A-5 — L-3m3's overlap is nearly vacuous.** Reported above rather than
  claimed as a clean transfer.
- **A-6 — the α(0.70) triangle does not close.** Reported above.
- **A-7 — no stage approached its 2× stop-and-report threshold.** Part 0
  `0.05594515800476074` s against 300 s; the four world chunks inside their 460 s
  estimates.

| stage | estimate (s) | measured (s) |
|---|---|---|
| part0 | 300 | 0.056 |
| pilot | 30 | 4.643 |
| worlds_1 | 460 | 444.431 |
| worlds_2 | 460 | 448.295 |
| worlds_3 | 460 | 444.378 |
| worlds_4 | 460 | 445.506 |
| alpha | 300 | 30.729 |
| retro | 300 | 5.510 |
| finalize | 60 | 0.000 |

| component | value |
|---|---|
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| platform | macOS-26.4.1-arm64-arm-64bit |
| python | 3.12.12 |
| python_executable | /private/tmp/claude-501/-Volumes-mobile3-projects-project-persona/582bb33b-a072-47a1-a24f-93e8ae8a88a1/scratchpad/m1venv/bin/python |
| scipy | 1.17.1 |

---

## What the line has established, and what it has not

**The tax is a curve.** `α(V) = c − κ0·V + (κ2/2)·V²` with
c = `0.21247398265278816`, κ0 = `0.9601680204204508`, κ2 = `1.562877770472943`, κ2's interval `[1.0324533419318935, 2.119753814549891]`
excluding zero and stable at ten times the bootstrap. The local tax **declines**
across the measured range — the reader's marginal price for person-variance is
highest where person-variance is scarcest. The budgets are met, so this is a
consumable object, not a description.

**The six "constants" were one curve all along.** 5 of six published κ̂
values are retrodicted by a single law run through each estimator's own code,
including the pre-signed low reading for the channel-omitting representation.
Rule 28 asked for representation-conditioned comparison; this is the constructive
version of that answer — not "the comparisons were illegitimate" but "here is the
one object that generates all of them."

**What is not established.** (i) Target 2 misses by 0.0045 on a 0.03 tolerance;
the closure is 5/6, not 6/6, and the report does not round that up. (ii) The
joint-refit transfer check passes only weakly — the channel is not
independently identified by this design, which is precisely why the primary
estimation fixes it. (iii) The α(0.70) triangle does not close, and the
direction of its failure says the channel does slightly more work at exterior
share than θ* assigns. (iv) Everything remains scoped to this world family,
this instrument, and r interior to the trained window.

**Registration-defect candidates: none.** Every clause was satisfiable, the
projection gate did its job before any world was drawn, the routing table was
disjoint and covering as the planner's #46 convention now requires, the rule-27
budgets attached to the consumed object, and rule 29's domain-pinned predicate
worked without incident at all 16 cells. The two anomalies that mattered (A-3,
A-4) were both mine and both were repaired before any outcome-relevant number
was written.
