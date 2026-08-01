# SUICA M4-D Leg 8 — Bias Anatomy: the Law-Level Bias Is Largely the Ridge's Own; Alignment Inverts; De-Biased D Hurts Paired Transport

Date: 2026-08-02
Tier: EXPLORATORY (open-exploration phase; operator directive 2026-08-01:
defensive machinery deferred; design and leans registered in
`docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md` ("Leg 8",
2026-08-02 loop cycle 3, commit bc3a15a) before this run; no prospective
seal, no independent verification pass)

## Decision

```text
BIAS_ANATOMY_LEVERS_MOVE_1_OF_4_LEANS_HOLD
PIVOT NOT TRIGGERED (best lever moves .1151 >= .05)
```

**The headline (lean (a) HOLDS): the ~.376 law-level bias is SUBSTANTIALLY
the V2 ridge's own non-vanishing regularization bias.** Scaling the penalty
to vanish with n (`A_lam1n`: penalty = `hazard_ridge * I`, i.e. the V2
penalty divided by len(y)) cuts pooled oracle-own-error **.3756 → .2605**
at natural 1x and puts **4 of 5 worlds ≤ .25** (expansion .2154, gated
.1978, compensation .2352, rotated .2254). The sharper mechanistic result
is the budget response: under de-biasing the 1x→4x log-log slope goes from
the baseline's **−.005** (the Leg-4b "budget-flat floor") to **−.521**
(`A_lam1n`) / **−.505** (`A_unpen`) — the textbook estimator-limited
n^(−1/2) rate. **Leg 4b's floor was budget-flat because the V2 penalty
grows with n**: more events grew the penalty proportionally and froze the
bias; hold the penalty fixed and events buy resolution again (A_lam1n 4x
pooled **.1265**; four worlds reach ~.10). Only
`endogenous_source_partition_matched` resists (.5922 at 1x, .5657 at
de-biased 4x) — a world-specific structure, not a sample-size effect
(Leg 7 already flagged this world's reference-envelope offset; candidate
artifact, not adjudicated here).

**But the paired-transport wall does not move (leans b, c, d MISS).**
Excitation stacks additively on the law-level term (A_lam1n + excitation
**.1944**, missing the .18 bar by .0144); Procrustes alignment of the
discovered frame **worsens** the basis-mismatch gap (.1364 → .1546,
closed fraction **−13.4%**) — the gap is not orientation; and the full
stack **hurts** loop transport (.6248 vs Leg 5's .7605) — the
**third consecutive stacking failure** (excitation Leg 6, realization
averaging Leg 7, de-biasing here). The emerging pattern is now explicit:
**law-accuracy improvements consistently fail to improve — and typically
damage — the PAIRED disc-vs-oracle transport metric**, because the
transport endpoint (the V2-fitted oracle stack) carries the same ridge
bias the lever removes from the discovered side; the pairing rewards
shared estimator behavior, not truth-accuracy. Cycle-4 hypothesis to
test: the V2 ridge's bias-variance equilibrium is what the paired metric
rewards — de-biasing one side breaks bias cancellation and adds variance
the pairing cannot absorb (an oracle-de-biased endpoint comparison was
not registered here and is the missing arm).

## Registered arms and leans (from the plan, commit bc3a15a)

- **Arm A** (de-biased oracle refit at oracle basis + oracle-forced
  route): (i) `A_unpen` penalty → 0; (ii) `A_lam1n` penalty ~ 1/n.
  e_orc_true at 1x/4x.
- **Arm B** (family enlargement, ONE step, no search): all pairwise
  interaction products of the existing hazard design columns
  (`B_enlarged`, V2 penalty semantics); companion `AB_enlarged_unpen`
  (the pivot's "A and B together" arm) at 1x.
- **Arm C** (subspace alignment, DIAGNOSTIC): orthogonal Procrustes of
  the discovered frame onto the oracle frame; refit D at the aligned
  width-7 frame; how much of the .136 gap closes.
- **Arm D** (stacks): every lever on the Leg-6 C3.3-excited 1x panels;
  best-of-A/B/C + two-stage full battery vs Leg 5's .7605.
- **Leans:** (a) A alone ≤ .25 at 1x in ≥ 3/5 worlds; (b) A or B +
  excitation ≤ .18 pooled; (c) aligned gap ≤ .068; (d) stack ≥ .80.
  **Pivot-if:** A and B together move oracle-own-error < .05 →
  WORLD_IDENTIFIABILITY_LIMIT, next instrument = information-operator
  conditioning (profiled in-run regardless).
- **Registered selection rule** (coded before run): estimator lever =
  argmin pooled natural-1x e_orc_true over {baseline, A_unpen, A_lam1n,
  B, AB}; frame = aligned iff it reduces the pooled gap. Selected:
  **(A_lam1n, v2 frame)** — alignment lost to v2, compute guard not
  fired.

## Faithfulness chain (all gates passed)

| Gate | Result |
|---|---|
| Baseline V2 floor rows {1x, 4x} vs Leg 4 persisted `dleg_budget_rows.csv` | 2,560 rows, max abs diff **2.22e-16**, flags equal, asserted per world-rep BEFORE lever arms |
| Pooled 1x/4x baseline e_orc_true vs Leg 4 decision | equal (< 1e-9): .375623…, .372811… |
| Excited 1x V2 rows vs Leg 6 persisted excitation rows | 1,280 rows, max abs diff **2.22e-16**; pooled .292074… equal |
| Pooled 1x gap_v2 vs Leg 7 persisted R=1 gap (.136385…) | diff **5.55e-17** |
| Flex-fitter V2-mode identity (same design, same op order) | **0.0** on 40/40 world-reps |
| Enlarged zero-interaction probe identity | max **1.67e-15** (≤ 1e-12 gate; ULP-level BLAS blocked-summation wobble, disclosed) |
| Amplitude-0 excitation pipeline identity (rep 0, 5 worlds) | value-exact, 32 fields each |
| Stage-1 rows vs Leg 4 persisted arm-2 rows | scaled max **2.19e-16**, flips exactly **73** |
| two_stage rows vs Leg 5 persisted rows | scaled max **2.21e-16**, flags equal |
| V2 replay validation vs archived battery | 1.11e-16 |
| Assembly cell audit | 2,560 baseline + 1,280 excited-baseline + 14,080 lever + 1,280 alignment + 1,280 conditioning + 3,840 stack rows — no missing, no duplicates |

Instability guard (documented, registered clause "unpenalized where
numerically stable"): the oracle basis carries an **exact constant
column** (first column all ones, duplicating the intercept), so every
unpenalized normal system is exactly singular by construction. Guard
ladder per IRLS iteration: solve → lstsq(gelsd) → scipy gelsy (added
after gelsd's SVD failed to converge on ill-conditioned 704-feature
unpenalized enlarged systems — one mid-run crash before any partial was
persisted, fixed forward) → trace-scaled jitter. Fallbacks fired
**23,755** times on `A_unpen`, **73,248** on `AB_enlarged_unpen`, **0**
on both penalized arms (persisted per fit).

## The bias ledger — how much of .376 and .136 each lever removes

Law-level component (pooled author-level median e_orc_true; baseline
natural 1x = **.3756**):

| Arm | natural 1x | removed | natural 4x | removed | excited 1x | removed |
|---|---|---|---|---|---|---|
| baseline_v2 | .3756 | — | .3728 | .0028 | .2921 | .0835 |
| A_unpen | .3181 | .0575 | **.1580** | .2177 | .2416 | .1340 |
| **A_lam1n** | **.2605** | **.1151** | **.1265** | **.2491** | **.1944** | **.1813** |
| B_enlarged | .4804 | −.1047 | .3850 | −.0094 | .4234 | −.0478 |
| AB_enlarged_unpen | 3.0552 | −2.6796 | (1x only) | — | 2.3047 | −1.9291 |

1x→4x log-log slopes: baseline **−.005**, A_unpen **−.505**, A_lam1n
**−.521**, B **−.160**. The de-bias + excitation + 4x combination was not
run (not registered), but the ledger shows the two levers compose
additively at 1x: de-bias removes .115, excitation another .067 on top
(.376 → .261 → .194).

Basis-mismatch component (pooled author-level median gap at 1x):
**gap_v2 .1364 → gap_aligned .1546** (removed **−.0183**, closed fraction
**−13.4%** — alignment made it WORSE). Loop transport: Leg 5 two_stage
**.7605 → .6248** under the stack (gain **−.1357**).

## Per-lean adjudication

**(a) HOLD — the leg's positive result.** `A_lam1n` ≤ .25 in **4/5**
worlds (.2154/.1978/.2352/.2254; partition .5922 resists). `A_unpen`
alone passes 2/5 (.2039 gated, .2426 rotated) — full penalty removal
trips logistic separation: **102/1,268** natural-1x rows collapse to
D = 0 exactly (e_orc_true = 1.0) and 32 explode > 2, while `A_lam1n` has
**zero** such rows — the 1/n-scaled constant penalty is the well-posed
de-biasing; full removal is not.

**(b) MISS by .0144.** Best A-or-B + excitation = `A_lam1n` excited
**.1944** vs the .18 bar (A_unpen .2416, B .4234). Registered honestly:
close, not reached.

**(c) MISS — informative INVERSION.** Aligned gap **.1546** vs bar .068;
per-world the v2 gap concentrates in expansion/compensation/rotated
(.215/.210/.228, aligned .257/.233/.256) while gated/partition are tiny
(.026/.066). Procrustes residual range .098–1.373 across world-reps. The
basis-mismatch bias is **not an orientation defect** of the discovered
frame: projecting onto the oracle subspace discards discovered-frame
directions that were doing compensatory work — consistent with Leg 3's
"span must MATCH, not shrink" (width-7 truncation dropped mechanism
directions there too).

**(d) MISS badly — the third stacking failure.** `two_stage_lever`
(stage 2 refit with `A_lam1n` at the v2 frame, stage-1 routes asserted
identical, flips still 73) pools **.6248** vs Leg 5's .7605 — ALL five
worlds lose (−.084 to −.174); median stage-2 e_d_atom vs the V2 oracle
reference jumps .4481 → **.8778** while creation geometry drops
.8234 → .7063. Mechanism: the transport comparator is the V2-FITTED
oracle stack, which retains the ridge bias the lever removes — the
de-biased D moves toward the generator law (arm-A result) and away from
the biased endpoint the paired metric scores against. Same asymmetric-
reference structure as Leg 6's excited-stacking anomaly, now produced by
a pure estimator change at identical routes on identical panels.

**Pivot NOT triggered.** Best lever move .1151 ≥ .05 — the law-level
bias is NOT a world-identifiability limit; it is substantially removable
regularization bias. The pre-coded conditioning profile confirms from
the other side: at the oracle basis the creation estimand is
**information-rich** — effective condition number of the Fisher
information (structural intercept-aliasing null excluded) 218–519 across
worlds, CR-style sd proxy **0.16%** of ‖D_true‖ (IQR .12–.22%), estimand
Jacobian's near-null-space fraction **0.0** on all 1,268 rows. Neither
identifiability nor variance is the obstruction; bias was, and the ridge
supplied most of it.

## Honest anomalies and boundaries

- One mid-run crash (chunk 0-1, first attempt): `np.linalg.lstsq`'s SVD
  failed to converge on an ill-conditioned unpenalized enlarged system;
  no partial had been persisted; the gelsy/jitter rungs were added and
  the chunk rerun from scratch. Disclosed as instrument hardening, not a
  result change (all downstream asserts still 2.22e-16-level).
- `A_unpen`'s 102 zero-derivative separation rows (above) are persisted
  per row; medians absorb them honestly (they inflate A_unpen, not
  A_lam1n).
- Family enlargement (B) at V2 semantics WORSENS the oracle-side error
  at both budgets (+.105/+.012) and AB explodes (3.06 pooled) — one-step
  pairwise enlargement is variance-unstable at this design even under
  the guard ladder; "hazard-family misspecification" is not supported as
  the law-level mechanism by this lever.
- Partition (.5922 at 1x, .5657 at de-biased 4x, .632 under Leg-6
  excitation) resists every lever tested across three legs — flagged as
  a candidate reference-envelope artifact (Leg 7's note), not
  adjudicated here.
- The stack's oracle endpoint is V2-fitted by registration (needed for
  .7605 comparability); an oracle-de-biased endpoint was not registered
  and not computed — it is the natural cycle-4 arm, but it changes the
  comparator and must be registered as such, not slipped in.
- Truth-referenced diagnostic throughout (oracle basis, oracle-forced
  routes, generator-law derivatives, C3.3 generator-privileged
  excitation consumed as references); arm C consumes the oracle frame
  and is DIAGNOSTIC — not operationally available; nothing here reopens
  any gate: the V1/V2 and C3.3 NO-GO decisions stand; finite synthetic
  M4-C.2 worlds only; no natural-text, personality, emotion, or clinical
  claim; EXPLORATORY tier; no seal, no independent verification
  (operator directive 2026-08-01).

## Artifacts

- `scripts/run_suica_m4_d_bias_anatomy_leg8.py` (all machinery imported
  from Legs 3/4/5/6/7; chunked foreground execution; registered
  selection rule coded before the run)
- `results/m4_d_bias_anatomy/` — `decision.json`, per-row CSVs
  (baseline_replay, excited_baseline, lever, alignment, conditioning,
  stack per-loop/world-rep), crosscheck CSVs, `stack_composition.json`
- Ledger: `docs/CLAIMS_LEDGER.md` row M4-D.9 (result)
