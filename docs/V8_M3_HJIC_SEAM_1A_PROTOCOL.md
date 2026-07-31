# V8-M3-HJIC-SEAM-1A Between-Operator Null Protocol

Status:
`TARGETED_BETWEEN_NULL_REPAIR_SUPPORTED__OVERALL_PARTIAL`

The original SEAM-1 formal run remains `PARTIAL`: nine of ten gate families
passed, while ecological detection reached `51/60=.85` with zero false
individual licenses. SEAM-1A is an independent correction experiment. It does
not overwrite that result. Its 60x999 formal run raised ecological detection
to `.967` with zero individual, held-out-null, or mismatch false ecological
licenses. The overall suite remained partial because alias and cancellation
rates were each `.933` under the intentionally retained support drift.

## 1. Registered defect

SEAM-1 used the local statistic

\[
T_W^{\max}=\max_s \operatorname{RMS}(\widehat J_s)
\]

to threshold the single between-context statistic

\[
T_B=\operatorname{RMS}(\widehat J_B).
\]

Their null distributions differ: \(T_W^{\max}\) includes a four-context
maximum penalty, while \(T_B\) is one aggregate matrix. Reusing the former is
not a conservative version of the same test; it is a different test.

## 2. D0 between null

For each D0 permutation \(b\), the same author permutation \(\pi_b\) is
applied to both right-family replicates. With D0 context weights
\(\widehat p_s\),

\[
\widehat C_{B,0}^{(b)}
=
\frac12\sum_s\widehat p_s
\left[
\Delta\bar L_s^{(1)}
\Delta\bar R_{s,\pi_b}^{(2)\top}
+
\Delta\bar L_s^{(2)}
\Delta\bar R_{s,\pi_b}^{(1)\top}
\right].
\]

\[
T_{B,0}^{(b)}
=
\frac{\|W_L\widehat C_{B,0}^{(b)}W_R\|_F}
{\sqrt{d_Ld_R}},
\qquad
\tau_B=\max\{.065,Q_{.99}(T_{B,0})\}.
\]

There is no maximum over contexts because \(\widehat J_B\) is already one
weighted aggregate. Both independent confirmation splits must exceed
\(\tau_B\), retain direction cosine at least `.80`, and have no individual
relation license before `ECOLOGICAL_ONLY` is emitted.

## 3. Isolation constraint

Only the ecological threshold changes. The following remain identical to
SEAM-1:

- event feature map, M3 quotient, whitening, relation matrices, and covariance
  decomposition;
- local max-context null and all local relation decisions;
- planted worlds, author/event budgets, `.065` material floor, and `.80`
  direction floor;
- the intentional D0-to-confirmation loading drift;
- all original success gates.

`HELDOUT_D0_NULL` is added only as a safety world. Its left and right author
coordinates are independent and it contains no context offset.

## 4. Frozen confirmation

- Independent seed `20260803`.
- 60 repetitions.
- 999 local-null and between-null permutations per repetition.
- 999 primary and nested bootstrap draws per repetition.
- Ecological detection at least `57/60`.
- Ecological individual false relation at most `3/60`.
- Held-out-null false ecological classification at most `3/60`.
- Mechanism-family-mismatch false ecological classification at most `3/60`.
- Every other SEAM-1 gate must remain passing.
- Observable truth usage remains exactly zero.

## 5. Boundary

Passing identifies and repairs a statistic-specific null-calibration defect.
It does not establish measurement-support invariance. SEAM-1B must separately
test whether D0 and confirmation share a comparable replicated feature
support, and must refuse comparison when they do not.
