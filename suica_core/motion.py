"""SUICA motion layer: operational estimators from THEORY V6 / formal notes
F12 (v6.1). Label-free descriptive coordinates; no trait inference.

Windows (frozen convention, shared with the V6-E2/W2b research scripts):
tokenize the text, cut fixed ``win``-token windows, and if there are more
than ``max_windows`` of them take an endpoint-preserving even subsample
(``unique(round(linspace(0, m-1, max_windows)))``) so the first and last
window are always kept. Any kept window matching the package's
personality-leak sticker (``PERSONALITY_LEAK_RE``) drops the WHOLE text,
position-neutral (we do not selectively peel individual windows here, since
that would bias which parts of the path survive).

Moments (F12.1 identities + F12.4 finite-n correction,
``docs/THEORY_FORMAL_NOTES_V3.md``, registered commit da07462): second
differences D2_k = w_{k+1} - 2*w_k + w_{k-1} kill level and linear drift per
triple. S0 = Cov(D2) and symS1 = sym Cov(D2_k, D2_{k+1}) are estimated from
per-text-CENTERED D2 rows, pooled over eligible texts (no subsample gaps,
5 <= m <= 12 -- the registered W2b corridor). Centering biases the sample
moments relative to the raw F12.1 identities (S0 = 6*Gamma0 - 8*B,
symS1 = -4*Gamma0 + 7*B), so the DEFAULT inversion is the F12.4 exact map:
solve, entrywise, the centered-moment system

    E[S0]    = a(n)*Gamma0 + b(n)*B     (n = m - 2 second-difference rows)
    E[symS1] = c(n)*Gamma0 + d(n)*B

with the per-n coefficients of ``_centered_moment_coefficients`` pooled
over the actual texts used -- row weights n_t for the S0 equation,
adjacent-pair weights n_t - 1 for the symS1 equation. The naive F12.1
inversion (Gamma0_hat = (7*S0 + 8*symS1)/10, B_hat = (6*Gamma0_hat - S0)/8)
remains available behind ``naive_inversion=True``; the output key
``"inversion"`` records which map produced the estimates
("corrected_f12_4" | "naive").

Memory (primary dynamic output): ``memory_by_construct`` is the SIGNED
per-construct ratio r_c = B_hat_cc / Gamma0_hat_cc -- positive = carry-over
/ persistence, negative = bounce / anti-persistence. The corpus finding
(Essays re-inversion under F12.4) is a mildly POSITIVE average memory with
sparse-construct bounce exceptions, so the signed coefficient is the honest
primary; ``theta_by_construct`` -- the [0, 1] MA(1) inversion of r_c (root
of r = -theta/(1+theta**2)), meaningful only where r_c < 0 -- is kept for
continuity.

Period-2 energy (F12.6.3/F12.7): lag COORDINATES beyond the (Gamma0, B)
pair are ill-posed under within-text centering (the centered lag map is
severely ill-conditioned, and for pure m=5 support it is exactly singular:
every text satisfies 3*s0 + 4*s1 + 2*s2 = 0 identically), but linear
FUNCTIONALS whose left-solves are well-conditioned remain estimable. The
one-number dynamics fingerprint is the normalized Nyquist ratio
rho_pi = f(pi)/gamma0, with f(pi) = gamma0 - 2*gamma1 + 2*gamma2 -
2*gamma3 + 2*gamma4 (spectral density at period 2, truncated at lag 4).
Reference values: white gusts = 1; MA(1) bounce theta ->
(1+theta)**2/(1+theta**2) (bounce piles energy at period 2); AR(1)
carry-over phi -> (1-phi)/(1+phi); AR(2)-even a2 -> (1+a2)/(1-a2).
Estimated per construct as w^T s over the pooled centered lag moments
s = (S0, symS1, ..., symS4), with w = solve(M^T, c), c = (1,-2,2,-2,2),
and M the exact centered lag map built by unit-band enumeration
(``_centered_lag_map``) -- the estimable-functional replacement for lag
coordinates. Reported as "period2_energy_by_construct" with
"period2_mode" = "full5" | "truncated3" (a lag-2-truncated 3x3 fallback
when lag-3/lag-4 pairs are thin) and "period2_reason" when neither is
estimable (thin pairs, or a singular m-composition). MEASURED CAVEAT: the
FIVE-band gamma0 left-solve is the map's ill-conditioned direction
(|w| ~ 39 at m = 8), noise-hungry and leaky in unmodeled bands beyond
lag 4. Treat rho_pi as a register fingerprint, not a process parameter.

F12.8 refinements (research commit eabc17b): (i) HYBRID DENOMINATOR --
left-solve conditioning is per-functional, so in full5 mode the gamma0
denominator comes from the truncated-3 left-solve (3x3 top-left of M,
c0 = (1, 0, 0); |w| ~ 4 vs ~ 39 for the 5-band gamma0 solve at m = 8),
which both stabilizes and de-leaks the ratio -- AR(2)-even a2 = 0.4 at
m = 8 reads 1.75 hybrid vs 1.41 non-hybrid against the 2.33 process
value; "period2_denominator" records which solve normalized the ratio.
(ii) SHAPE PAIR -- f(pi/2), the spectral density at the quarter
frequency, via c = (1, 0, -2, 0, 2) (truncated-3 fallback c = (1, 0, -2)
whenever the 5-band left-solve norm exceeds 20; "shape_mode" flags the
solve used, "shape_w_norm" reports its norm). "spectral_shape_by_construct"
= per-construct [rho_pihalf, rho_pi] pairs over the hybrid gamma0, and
"delta_shape_by_construct" = rho_pihalf - rho_pi. Reference shapes:
white (1, 1), delta 0; MA(1) ANY theta: rho_pihalf = 1 EXACTLY (MA(1) is
flat at the quarter frequency -- the sharpest invariant); AR(1) phi:
((1-phi**2)/(1+phi**2), (1-phi)/(1+phi)), delta > 0; AR(2)-even a2:
((1-a2)/(1+a2), (1+a2)/(1-a2)), delta strongly < 0.

Flow (T2-prime): the wide difference d = (w_last - w_first)/(m-1) has
Cov(d) = Sigma_flow + (2*Gamma0-Gamma_(m-1)-Gamma_(m-1).T)/(m-1)**2.
Callers may supply independently estimated complete endpoint-gust covariance
corrections per m-stratum. Without them the historical 2*Gamma0 correction is retained only
as an explicitly flagged short-memory endpoint approximation; it is not an
exact correction for AR/long-memory gusts.

Finite-sample bias (closed, F12.4): the centering bias is now corrected by
default via the F12.4 exact map above -- verified analytically and by
Monte Carlo; the historical naive inversion's bias was ~ +0.04 on
theta_hat at theta = 0.4, m = 8 (reproducible via ``naive_inversion=True``).

Estimability guard (T4, measurement economics -- occasions vs tokens):
gust-structure variance is token-limited (~1/(N*(m-2))), not
occasion-limited, so with too few within-text second-difference rows the
inversion is not worth reporting; Gamma0_hat/B_hat/theta are set to None
with an explicit reason instead of returned as noise.

Everything here is Tier-U (see ``licenses`` in the ``motion_profile``
return value): descriptive motion coordinates, sample-standardized and
register-anchored (T6) -- never trait-inferential.

Dependency-light by design: numpy plus the package's own tokenizer/leak
regex only.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from suica_core.suica import PERSONALITY_LEAK_RE, tokenize  # noqa: E402

# F12.3 registered corridor for the second-difference (gust) estimator.
D2_M_LO, D2_M_HI = 5, 12
# T4 estimability guard: minimum pooled second-difference rows before the
# MA(1) inversion is reported at all.
MIN_D2_ROWS = 30

LICENSES: tuple[str, ...] = (
    "Tier-U descriptive coordinates; no trait (Big5/MBTI/clinical) inference is licensed (V6 4.2).",
    "Level values are sample-standardized, NOT norm-referenced (T4: level traits are occasion-limited).",
    "Motion coordinates are register-anchored; do not transport across registers (T6).",
    "On 3-point support flow and gust-memory are not separable (F12.2); corrected flow requires m>=5 texts.",
)

GAMMA0_UNESTIMABLE_REASON = (
    "insufficient within-text tokens (need >= 30 second-difference rows; "
    "motion structure is token-limited)"
)
FLOW_UNCORRECTED_FLAG = "uncorrected: gust moments not estimable"
FLOW_ENDPOINT_APPROX_FLAG = (
    "short-memory endpoint approximation: Gamma_(m-1) assumed zero"
)

# F12.7 period-2 (Nyquist) functional: band depth, pair thresholds, guards.
PERIOD2_MAX_LAG = 4
PERIOD2_MIN_LAG_PAIRS = 100
PERIOD2_COND_MIN = 1e-8  # relative sigma_min below this = singular composition
PERIOD2_C_FULL = (1.0, -2.0, 2.0, -2.0, 2.0)  # f(pi) band weights, lags 0..4
PERIOD2_UNESTIMABLE_REASON = (
    "insufficient lag-2 pairs (need >= 100; the period-2 functional is "
    "token-limited)"
)
PERIOD2_SINGULAR_REASON = (
    "centered lag map is singular for this m-composition (pure m=5 support "
    "carries the exact within-text constraint 3*s0 + 4*s1 + 2*s2 = 0; the "
    "period-2 functional is unidentifiable)"
)

# F12.8 shape pair: f(pi/2) band weights and the left-solve norm guard.
SHAPE_C_FULL = (1.0, 0.0, -2.0, 0.0, 2.0)   # f(pi/2), lags 0..4
SHAPE_C_TRUNCATED = (1.0, 0.0, -2.0)        # f(pi/2) truncated at lag 2
SHAPE_W_NORM_MAX = 20.0


def text_window_frames(
    text: str,
    *,
    win: int = 128,
    max_windows: int = 12,
    drop_leaks: bool = True,
) -> tuple[list[str], np.ndarray, int] | None:
    """Slice ``text`` into fixed token windows, keeping adjacency metadata.

    Returns ``(window_texts, j_indices, m)`` where ``m`` is the ORIGINAL
    window count (``len(tokens) // win``) and ``j_indices`` are the original
    (pre-subsample) window positions kept -- always including 0 and m-1, so
    downstream wide-difference contrasts (``w[j_indices[-1]] - w[j_indices[0]]``
    over ``m-1``) stay well-defined even when subsampled. Returns None if
    there are fewer than 2 windows, or (when ``drop_leaks``) if ANY kept
    window trips the personality-leak sticker -- the whole text is dropped,
    not just the leaking window, so position is never selectively censored.
    """
    tokens = tokenize(text)
    m = len(tokens) // win
    if m < 2:
        return None
    j_indices = (
        np.unique(np.round(np.linspace(0, m - 1, max_windows)).astype(int))
        if m > max_windows
        else np.arange(m)
    )
    window_texts: list[str] = []
    for j in j_indices:
        wtext = " ".join(tokens[j * win:(j + 1) * win])
        if drop_leaks and PERSONALITY_LEAK_RE.search(wtext):
            return None  # sticker found -- drop the whole text, position-neutral
        window_texts.append(wtext)
    return window_texts, j_indices, m


def text_windows(
    text: str,
    *,
    win: int = 128,
    max_windows: int = 12,
    drop_leaks: bool = True,
) -> list[str] | None:
    """Window texts only (see ``text_window_frames`` for the j/m adjacency
    metadata that motion contrasts need)."""
    frames = text_window_frames(text, win=win, max_windows=max_windows, drop_leaks=drop_leaks)
    return None if frames is None else frames[0]


def _theta_from_ratio(r_c: float) -> float:
    """Implied MA(1) theta from the diagonal ratio r_c = B_hat_cc/Gamma0_hat_cc,
    i.e. the root in [0, 1] of r = -theta/(1+theta**2) (F12.1.i). r_c >= 0
    (no measured anti-persistence on this construct) reads as theta = 0;
    r_c <= -0.5 saturates the MA(1) boundary at theta = 1."""
    if r_c >= 0:
        return 0.0
    disc = 1.0 - 4.0 * r_c ** 2
    if disc < 0:
        return 1.0
    return float(np.clip((-1.0 + np.sqrt(disc)) / (2.0 * r_c), 0.0, 1.0))


def _centered_moment_coefficients(n_list: list[int]) -> tuple[float, float, float, float]:
    """Pooled F12.4 coefficients (A, B_coef, C, D_coef) of the centered-
    moment system E[S0] = A*Gamma0 + B_coef*B, E[symS1] = C*Gamma0 +
    D_coef*B, for texts contributing n_t = m_t - 2 centered second-
    difference rows each (n_t >= 3 inside the corridor).

    Per-text exact coefficients (within-text centering of the D2 series,
    whose autocovariances under MA(1) gusts are gamma_D(0..3) =
    (6, -4, 1, 0)*Gamma0 + (-8, 7, -4, 1)*B):

        a(n) = 6 - 4/n**2
        b(n) = -8 + 4/n**2
        c(n) = -4 + 2*(n - 2)/(n**2*(n - 1))
        d(n) = 7 - 4/n**2                     for n >= 4
        d(3) = 56/9                           n = 3 boundary case: the lag-3
                                              term gamma_D(3) = B cannot
                                              occur on 3 rows, lowering d by
                                              2/(n*(n-1)) = 1/3 relative to
                                              the n >= 4 formula (verified
                                              analytically + Monte Carlo)

    All coefficients tend to the raw F12.1 identity values (6, -8, -4, 7)
    as n grows. Pooling matches how S0/symS1 are pooled: row weights n_t
    for the S0 equation, adjacent-pair weights n_t - 1 for the symS1
    equation.
    """
    n_arr = np.asarray(n_list, dtype=float)
    a = 6.0 - 4.0 / n_arr ** 2
    b = -8.0 + 4.0 / n_arr ** 2
    c = -4.0 + 2.0 * (n_arr - 2.0) / (n_arr ** 2 * (n_arr - 1.0))
    d = 7.0 - 4.0 / n_arr ** 2
    d = np.where(n_arr == 3.0, 56.0 / 9.0, d)  # exact n=3 boundary (see docstring)
    w_rows = n_arr
    w_pairs = n_arr - 1.0
    pooled_a = float((w_rows * a).sum() / w_rows.sum())
    pooled_b = float((w_rows * b).sum() / w_rows.sum())
    pooled_c = float((w_pairs * c).sum() / w_pairs.sum())
    pooled_d = float((w_pairs * d).sum() / w_pairs.sum())
    return pooled_a, pooled_b, pooled_c, pooled_d


def _invert_moments(
    s0: np.ndarray,
    sym_s1: np.ndarray,
    n_list: list[int],
    naive_inversion: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Invert pooled centered moments (S0, symS1) to (Gamma0_hat, B_hat).

    Default: the F12.4 corrected inversion -- solve the pooled 2x2
    centered-moment system entrywise (det = A*D_coef - B_coef*C; Gamma0 =
    (D_coef*S0 - B_coef*symS1)/det; B = (A*symS1 - C*S0)/det).
    ``naive_inversion=True`` applies the raw F12.1 identities, which ignore
    the within-text centering (kept for history/comparison).
    """
    if naive_inversion:
        gamma0 = (7.0 * s0 + 8.0 * sym_s1) / 10.0
        return gamma0, (6.0 * gamma0 - s0) / 8.0
    pooled_a, pooled_b, pooled_c, pooled_d = _centered_moment_coefficients(n_list)
    det = pooled_a * pooled_d - pooled_b * pooled_c
    gamma0 = (pooled_d * s0 - pooled_b * sym_s1) / det
    b = (pooled_a * sym_s1 - pooled_c * s0) / det
    return gamma0, b


def _centered_lag_map(
    n_list: list[int],
    max_lag: int = PERIOD2_MAX_LAG,
) -> tuple[np.ndarray, np.ndarray]:
    """Exact centered lag map M for a pooled n-composition (F12.7).

    M[h, j] is the coefficient of gust band gamma_j in E[symS_h] (h, j =
    0..max_lag), built by unit-band enumeration: for each distinct n (=
    m - 2 rows), place gamma_j = 1 on the +-j bands of the m x m gust
    Toeplitz, push it through the D2 filter rows [1, -2, 1] and the
    within-text centering projection P = I - J/n, and read the mean lag-h
    products of the resulting covariance; rows are pooled over texts with
    pair weights n - h (exactly how the empirical symS_h pool). The 2x2
    top-left equals the ``_centered_moment_coefficients`` system (asserted
    in tests). Rows with no pairs anywhere (all n <= h) come back as nan
    with pooled weight 0.

    Returns (M, row_pair_weights).
    """
    counts: dict[int, int] = {}
    for n_val in n_list:
        counts[int(n_val)] = counts.get(int(n_val), 0) + 1
    num = np.zeros((max_lag + 1, max_lag + 1))
    weights = np.zeros(max_lag + 1)
    for n_val, cnt in counts.items():
        m = n_val + 2
        filt = np.zeros((n_val, m))
        for k in range(n_val):
            filt[k, k], filt[k, k + 1], filt[k, k + 2] = 1.0, -2.0, 1.0
        proj = np.eye(n_val) - np.ones((n_val, n_val)) / n_val
        a_mat = proj @ filt
        for j in range(max_lag + 1):
            toep = (np.eye(m) if j == 0
                    else np.diag(np.ones(m - j), j) + np.diag(np.ones(m - j), -j))
            cov = a_mat @ toep @ a_mat.T
            for h in range(max_lag + 1):
                if n_val - h >= 1:
                    num[h, j] += cnt * np.trace(cov, offset=h)
        for h in range(max_lag + 1):
            if n_val - h >= 1:
                weights[h] += cnt * (n_val - h)
    lag_map = np.full((max_lag + 1, max_lag + 1), np.nan)
    for h in range(max_lag + 1):
        if weights[h] > 0:
            lag_map[h] = num[h] / weights[h]
    return lag_map, weights


def _top_eig(matrix: np.ndarray) -> tuple[float, np.ndarray]:
    """Largest eigenvalue/eigenvector of a symmetric matrix."""
    vals, vecs = np.linalg.eigh(matrix)
    order = np.argsort(vals)[::-1]
    top = order[0]
    return float(vals[top]), vecs[:, top]


def motion_from_window_arrays(
    window_arrays: list[np.ndarray],
    orig_m: list[int] | None = None,
    naive_inversion: bool = False,
    flow_gust_corrections: dict[int, np.ndarray] | None = None,
) -> dict[str, Any]:
    """Internal moment/flow pipeline over already-scored (and, in
    ``motion_profile``, already pooled-sd-standardized) per-text window
    score matrices -- the numeric core that the F12.1/F12.4 formulas are
    checked against directly in tests.

    ``window_arrays[i]`` is an ``(m_i, p)`` matrix of window scores for one
    text, IN ORIGINAL WINDOW ORDER. ``orig_m`` is the pre-subsample window
    count per text (defaults to ``window_arrays[i].shape[0]``, i.e. "assume
    no subsampling happened" -- the right default both for direct numeric
    testing and for texts short enough to never hit ``max_windows``). A
    text is only eligible for the second-difference (gust) moments when its
    kept rows equal its original m (no subsample gaps) AND
    ``D2_M_LO <= m <= D2_M_HI`` (the F12.3 registered corridor); every text
    with m >= 2 still contributes to level/slope and to the flow moment.

    ``flow_gust_corrections[m]`` may provide an independently estimated full
    ``2*Gamma0-Gamma_(m-1)-Gamma_(m-1).T`` matrix. This is intentionally the
    complete correction: combining a true endpoint lag with a Gamma0 estimate
    obtained under a misspecified gust model is not exact. When absent, flow uses the historical
    short-memory approximation ``Gamma_(m-1)=0`` and reports this assumption
    in ``flow_flag``. ``naive_inversion=False`` (default) applies the F12.4 finite-n
    corrected inversion; ``True`` applies the historical F12.1 identities.
    The primary dynamic output is ``memory_by_construct`` (signed r_c;
    positive = carry-over, negative = bounce); ``theta_by_construct`` is
    the continuity [0, 1] MA(1) reading, meaningful only where r_c < 0.
    ``period2_energy_by_construct`` is the F12.7 normalized Nyquist ratio
    (always from the exact centered lag map, independent of the flag).
    """
    inversion_mode = "naive" if naive_inversion else "corrected_f12_4"
    n_texts = len(window_arrays)
    if n_texts == 0:
        return {
            "level_mean": None, "slope_mean": None,
            "Gamma0": None, "B": None, "gamma0_reason": "no texts",
            "memory_by_construct": None, "theta_by_construct": None,
            "inversion": inversion_mode,
            "period2_energy_by_construct": None, "period2_mode": None,
            "period2_reason": "no texts", "period2_denominator": None,
            "spectral_shape_by_construct": None, "delta_shape_by_construct": None,
            "shape_mode": None, "shape_w_norm": None, "lag_pair_counts": {},
            "flow_lambda1": None, "flow_top_vector": None, "flow_flag": None,
        }
    if orig_m is None:
        orig_m = [int(arr.shape[0]) for arr in window_arrays]
    p = window_arrays[0].shape[1]

    # ---- group texts by (kept rows, original m) and stack once per group
    # (identical math to a per-text loop; vectorized so large-N batches
    # stay fast) ----
    groups: dict[tuple[int, int], list[np.ndarray]] = {}
    for arr, m_orig in zip(window_arrays, orig_m):
        groups.setdefault((int(arr.shape[0]), int(m_orig)), []).append(arr)

    level_sum = np.zeros(p)
    slope_sum = np.zeros(p)
    strata: dict[int, list[np.ndarray]] = {}
    lag_sums = {h: np.zeros((p, p)) for h in range(PERIOD2_MAX_LAG + 1)}
    lag_pairs = {h: 0 for h in range(PERIOD2_MAX_LAG + 1)}
    n_rows_list: list[int] = []
    for (m_kept, m_orig_g), arrs in sorted(groups.items()):
        stack = np.stack(arrs)                                  # (n_g, m_kept, p)
        n_g = stack.shape[0]
        # level (mean window vector) and wide difference d, per text
        level_sum += stack.mean(axis=1).sum(axis=0)
        slopes_g = (stack[:, -1, :] - stack[:, 0, :]) / (m_orig_g - 1)
        slope_sum += slopes_g.sum(axis=0)
        strata.setdefault(m_orig_g, []).append(slopes_g)
        # second differences, centered within text (F12.1.ii/F12.4/F12.7)
        if m_kept != m_orig_g:
            continue  # subsample gaps -- D2 would span skipped windows
        if not (D2_M_LO <= m_kept <= D2_M_HI):
            continue
        n_i = m_kept - 2
        d2 = stack[:, 2:, :] - 2.0 * stack[:, 1:-1, :] + stack[:, :-2, :]
        d2c = d2 - d2.mean(axis=1, keepdims=True)               # center within text
        n_rows_list.extend([n_i] * n_g)
        for h in range(PERIOD2_MAX_LAG + 1):
            if n_i - h >= 1:
                lag_sums[h] += np.einsum("tkp,tkq->pq",
                                         d2c[:, :n_i - h, :], d2c[:, h:, :])
                lag_pairs[h] += n_g * (n_i - h)

    n_d2 = lag_pairs[0]
    if n_d2 < MIN_D2_ROWS:
        gamma0_hat: np.ndarray | None = None
        b_hat: np.ndarray | None = None
        memory_by_construct: list[float] | None = None
        theta_by_construct: list[float] | None = None
        gamma0_reason: str | None = GAMMA0_UNESTIMABLE_REASON
    else:
        s0 = lag_sums[0] / lag_pairs[0]
        s1 = lag_sums[1] / lag_pairs[1]
        sym_s1 = (s1 + s1.T) / 2.0
        gamma0_hat, b_hat = _invert_moments(s0, sym_s1, n_rows_list,
                                            naive_inversion=naive_inversion)
        gamma0_reason = None
        memory_by_construct = []
        theta_by_construct = []
        for i in range(p):
            g0_ii = gamma0_hat[i, i]
            r_c = float(b_hat[i, i] / g0_ii) if g0_ii != 0 else 0.0
            memory_by_construct.append(r_c)
            theta_by_construct.append(_theta_from_ratio(r_c))

    # ---- period-2 energy + spectral shape pair via exact left-functionals (F12.7/F12.8) ----
    period2_energy: list[float] | None = None
    period2_mode: str | None = None
    period2_reason: str | None = None
    period2_denominator: str | None = None
    spectral_shape: list[list[float]] | None = None
    delta_shape: list[float] | None = None
    shape_mode: str | None = None
    shape_w_norm: float | None = None
    if lag_pairs[2] < PERIOD2_MIN_LAG_PAIRS:
        period2_reason = PERIOD2_UNESTIMABLE_REASON
    else:
        full5 = (lag_pairs[3] >= PERIOD2_MIN_LAG_PAIRS
                 and lag_pairs[4] >= PERIOD2_MIN_LAG_PAIRS)
        n_bands = 5 if full5 else 3  # truncated: assume gamma3 = gamma4 = 0
        lag_map, _map_weights = _centered_lag_map(n_rows_list)
        map3 = lag_map[:3, :3]
        map_num = lag_map[:n_bands, :n_bands]
        sv3 = np.linalg.svd(map3, compute_uv=False)
        sv_num = np.linalg.svd(map_num, compute_uv=False)
        if (sv3[-1] < PERIOD2_COND_MIN * sv3[0]
                or sv_num[-1] < PERIOD2_COND_MIN * sv_num[0]):
            period2_reason = PERIOD2_SINGULAR_REASON
        else:
            s_diag = np.stack([np.diagonal(lag_sums[h]) / lag_pairs[h]
                               for h in range(n_bands)])         # (n_bands, p)
            # numerator: f(pi) over the mode's full band depth
            w_pi = np.linalg.solve(map_num.T, np.asarray(PERIOD2_C_FULL[:n_bands]))
            f_pi = w_pi @ s_diag
            # denominator: gamma0 ALWAYS from the truncated-3 left-solve --
            # the F12.8 hybrid (|w| ~ 4 vs ~ 39 for the 5-band solve at m=8)
            w_g0 = np.linalg.solve(map3.T, np.array([1.0, 0.0, 0.0]))
            g0_f = w_g0 @ s_diag[:3]
            # shape numerator: f(pi/2), with the |w| > 20 truncation guard
            w_ph5 = np.linalg.solve(map_num.T, np.asarray(SHAPE_C_FULL[:n_bands]))
            if full5 and float(np.linalg.norm(w_ph5)) > SHAPE_W_NORM_MAX:
                w_ph = np.linalg.solve(map3.T, np.asarray(SHAPE_C_TRUNCATED))
                f_ph = w_ph @ s_diag[:3]
                shape_mode = "truncated3"
            else:
                w_ph = w_ph5
                f_ph = w_ph @ s_diag
                shape_mode = "full5" if full5 else "truncated3"
            shape_w_norm = float(np.linalg.norm(w_ph))
            period2_energy = [float(f / g) if g != 0 else 0.0
                              for f, g in zip(f_pi, g0_f)]
            rho_ph = [float(f / g) if g != 0 else 0.0
                      for f, g in zip(f_ph, g0_f)]
            spectral_shape = [[ph, pi] for ph, pi in zip(rho_ph, period2_energy)]
            delta_shape = [ph - pi for ph, pi in zip(rho_ph, period2_energy)]
            period2_mode = "full5" if full5 else "truncated3"
            period2_denominator = "truncated3_hybrid" if full5 else "truncated3"

    # ---- flow: per m-stratum wide-difference covariance, gust-corrected when possible (F12.1.iii) ----
    sig_sum = np.zeros((p, p))
    n_total = 0
    corrected = gamma0_hat is not None
    for m_val, slope_groups in strata.items():
        rows_arr = np.vstack(slope_groups)
        n_sel = rows_arr.shape[0]
        if n_sel < 2:
            continue  # cross-text covariance undefined on a single observation
        cov_m = np.cov(rows_arr, rowvar=False)
        if corrected:
            supplied = None if flow_gust_corrections is None else flow_gust_corrections.get(m_val)
            if supplied is None:
                correction = 2.0 * gamma0_hat
            else:
                correction = np.asarray(supplied, dtype=float)
                if correction.shape != gamma0_hat.shape:
                    raise ValueError(
                        f"flow_gust_corrections[{m_val}] must have shape {gamma0_hat.shape}"
                    )
            sigma_m = cov_m - correction / (m_val - 1) ** 2
        else:
            sigma_m = cov_m
        sig_sum += n_sel * sigma_m
        n_total += n_sel

    if n_total == 0:
        flow_lambda1: float | None = None
        flow_top_vector: list[float] | None = None
        flow_flag: str | None = None
    else:
        sigma_flow = sig_sum / n_total
        flow_lambda1, top_vec = _top_eig(sigma_flow)
        flow_top_vector = top_vec.tolist()
        if not corrected:
            flow_flag = FLOW_UNCORRECTED_FLAG
        elif flow_gust_corrections is None or any(
            m not in flow_gust_corrections for m in strata
        ):
            flow_flag = FLOW_ENDPOINT_APPROX_FLAG
        else:
            flow_flag = None

    return {
        "level_mean": (level_sum / n_texts).tolist(),
        "slope_mean": (slope_sum / n_texts).tolist(),
        "Gamma0": gamma0_hat.tolist() if gamma0_hat is not None else None,
        "B": b_hat.tolist() if b_hat is not None else None,
        "gamma0_reason": gamma0_reason,
        "memory_by_construct": memory_by_construct,
        "theta_by_construct": theta_by_construct,
        "inversion": inversion_mode,
        "period2_energy_by_construct": period2_energy,
        "period2_mode": period2_mode,
        "period2_reason": period2_reason,
        "period2_denominator": period2_denominator,
        "spectral_shape_by_construct": spectral_shape,
        "delta_shape_by_construct": delta_shape,
        "shape_mode": shape_mode,
        "shape_w_norm": shape_w_norm,
        "lag_pair_counts": {h: int(lag_pairs[h]) for h in range(PERIOD2_MAX_LAG + 1)},
        "flow_lambda1": flow_lambda1,
        "flow_top_vector": flow_top_vector,
        "flow_flag": flow_flag,
    }


def _empty_motion_profile(n_dropped: int, inversion_mode: str) -> dict[str, Any]:
    return {
        "n_texts_used": 0, "n_texts_dropped": n_dropped, "n_windows": 0, "m_counts": {},
        "level_mean": None, "slope_mean": None,
        "Gamma0": None, "B": None, "gamma0_reason": "no texts",
        "memory_by_construct": None, "theta_by_construct": None,
        "inversion": inversion_mode,
        "period2_energy_by_construct": None, "period2_mode": None,
        "period2_reason": "no texts", "period2_denominator": None,
        "spectral_shape_by_construct": None, "delta_shape_by_construct": None,
        "shape_mode": None, "shape_w_norm": None, "lag_pair_counts": {},
        "flow_lambda1": None, "flow_top_vector": None, "flow_flag": None,
        "axis_series": None, "axis_mean_abs_projection": None,
        "licenses": list(LICENSES),
    }


def motion_profile(
    texts: list[str],
    scorer: Callable[[list[str]], np.ndarray],
    axis: np.ndarray | None = None,
    win: int = 128,
    max_windows: int = 12,
    naive_inversion: bool = False,
) -> dict[str, Any]:
    """Label-free motion coordinates for a batch of texts (F12, THEORY V6).

    ``scorer`` maps a list of window texts to an ``(n_windows, p)`` battery
    score matrix; it is called ONCE over every kept window from every text
    (batch), then the result is split back per text -- so callers using an
    LLM or vectorizer as ``scorer`` pay for one request/pass, not one per
    text. Columns are then standardized by the pooled window sd over THESE
    texts only (guard sd > 0): the resulting coordinates are
    sample-standardized and register-anchored, never norm-referenced (see
    ``licenses``).

    The primary dynamic output is ``memory_by_construct`` -- the signed
    r_c = B_hat_cc/Gamma0_hat_cc (positive = carry-over/persistence,
    negative = bounce/anti-persistence); see the module docstring for why
    the signed coefficient, not the theta clip, is the honest primary.
    ``naive_inversion=True`` switches the moment inversion back to the
    historical F12.1 map (the ``"inversion"`` key records the mode used).

    ``axis``, if given, is a length-p register gust/motion axis; each
    text's per-window projections onto ``axis / ||axis||`` are returned
    (descriptive only -- not part of the F12 moment machinery).
    """
    inversion_mode = "naive" if naive_inversion else "corrected_f12_4"
    frames: list[tuple[list[str], np.ndarray, int]] = []
    n_dropped = 0
    for text in texts:
        frame = text_window_frames(text, win=win, max_windows=max_windows, drop_leaks=True)
        if frame is None:
            n_dropped += 1
            continue
        frames.append(frame)
    if not frames:
        return _empty_motion_profile(n_dropped, inversion_mode)

    window_texts_all: list[str] = []
    counts: list[int] = []
    orig_m: list[int] = []
    for window_texts, _j_indices, m in frames:
        window_texts_all.extend(window_texts)
        counts.append(len(window_texts))
        orig_m.append(m)

    scores = np.asarray(scorer(window_texts_all), dtype=float)
    p = scores.shape[1]

    pooled_sd = scores.std(axis=0)
    pooled_sd = np.where(pooled_sd > 0, pooled_sd, 1.0)
    scores = scores / pooled_sd  # sample-standardized, register-anchored (T6)

    window_arrays: list[np.ndarray] = []
    offset = 0
    for count in counts:
        window_arrays.append(scores[offset:offset + count])
        offset += count

    axis_series: list[list[float]] | None = None
    axis_mean_abs_projection: list[float] | None = None
    if axis is not None:
        axis_vec = np.asarray(axis, dtype=float)
        norm = float(np.linalg.norm(axis_vec))
        unit_axis = axis_vec / norm if norm > 0 else axis_vec
        axis_series = [(arr @ unit_axis).tolist() for arr in window_arrays]
        axis_mean_abs_projection = [float(np.mean(np.abs(series))) for series in axis_series]

    core = motion_from_window_arrays(window_arrays, orig_m=orig_m,
                                     naive_inversion=naive_inversion)

    m_counts: dict[int, int] = {}
    for m_val in orig_m:
        m_counts[m_val] = m_counts.get(m_val, 0) + 1

    return {
        "n_texts_used": len(frames),
        "n_texts_dropped": n_dropped,
        "n_windows": int(sum(counts)),
        "m_counts": m_counts,
        "level_mean": core["level_mean"],
        "slope_mean": core["slope_mean"],
        "Gamma0": core["Gamma0"],
        "B": core["B"],
        "gamma0_reason": core["gamma0_reason"],
        "memory_by_construct": core["memory_by_construct"],
        "theta_by_construct": core["theta_by_construct"],
        "inversion": core["inversion"],
        "period2_energy_by_construct": core["period2_energy_by_construct"],
        "period2_mode": core["period2_mode"],
        "period2_reason": core["period2_reason"],
        "period2_denominator": core["period2_denominator"],
        "spectral_shape_by_construct": core["spectral_shape_by_construct"],
        "delta_shape_by_construct": core["delta_shape_by_construct"],
        "shape_mode": core["shape_mode"],
        "shape_w_norm": core["shape_w_norm"],
        "lag_pair_counts": core["lag_pair_counts"],
        "flow_lambda1": core["flow_lambda1"],
        "flow_top_vector": core["flow_top_vector"],
        "flow_flag": core["flow_flag"],
        "axis_series": axis_series,
        "axis_mean_abs_projection": axis_mean_abs_projection,
        "licenses": list(LICENSES),
        "p": p,
    }
