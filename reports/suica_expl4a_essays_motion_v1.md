# EXPL-4a -- motion-layer x questionnaire test (Essays DEV half, EXPLORATORY T1)

> EXPLORATORY (Essays dev half, T1)
> F14, research-repo commit 97ecca2. No git commits made by this run.

## Split rule

docs/SUICA_CLAIMS_LEDGER.md L90-92: "Governance note: Essays used dev-half TEXT only (stable-hash 50/50; frozen at data_sets/prepared/suica_tiers_v2/essays_regime_dev_half.csv); Big5 label columns never loaded; Essays confirm-half untouched for P5." L455-456 audit: "Essays governance verified clean (labels never loaded; 50/50 split exact)."

Frozen file: `data_sets/prepared/suica_tiers_v2/essays_regime_dev_half.csv` (1255 user_ids). Confirm-half labels were never loaded (two-pass skiprows-filtered read; see script docstring).

## Coverage

Dev-half ids: 1255. With Essays window cache coverage (m>=2): 1160. With BOTH cache coverage and labels: 1160.

m distribution (dev-half cache):

```
count    1160.000000
mean        5.217241
std         2.264109
min         2.000000
25%         4.000000
50%         5.000000
75%         7.000000
max        20.000000
```
m>=3: 1053; m>=5: 663; m==5 exactly: 194.

## Arms (per-trait RidgeCV, KFold(5, shuffle, rs=42); r = mean of per-fold r)

| arm | E | N | A | C | O | mean |
|---|---|---|---|---|---|---|
| L: level-19 | +0.128 | +0.150 | +0.154 | +0.113 | +0.200 | +0.1487 |
| LM: level+motion-34 | +0.107 | +0.130 | +0.126 | +0.141 | +0.192 | +0.1391 |
| M: motion-15 alone | +0.019 | -0.009 | -0.022 | +0.074 | +0.048 | +0.0217 |

Delta(L->LM): mean -0.0096; per trait Extraversion -0.0208, Neuroticism -0.0199, Agreeableness -0.0283, Conscientiousness +0.0287, Openness -0.0080.

## Single-feature screen (|r| >= 0.08 flagged)

d_novelty->Conscientiousness r=+0.088, open_first_person->Extraversion r=+0.089, open_first_person->Openness r=-0.084

## Registered-lean check (F14, docs/SUICA_THEORY_FORMAL_NOTES_V3.md, git 97ecca2)

> LEANS: any single motion feature |r| >= .08 in <= 3 of 50 cells; incremental over a level-feature baseline in [+.00, +.02]; honest coin-flip overall. STANDING KILL: if 4a and 4b both land <= 0, the conclusion 'questionnaire-criterion insensitivity to the motion layer' becomes the recorded verdict pending BEHAVIORAL criteria (the native corpus's job).

- Single-feature lean (<=3 of 50 cells at |r|>=.08): **MET** -- 3 of 75 cells observed.
- Delta(L->LM) lean ([+.00, +.02]): **NOT MET** -- actual -0.0096.
- Standing-kill status: EXPL-4a lands <= 0 (-0.0096) -- HALF of the standing-kill condition is met; full kill requires EXPL-4b to also land <= 0 (not run by this script).

## Ambiguities / design decisions

- D-comp1/D-comp2 recomputed AFTER restricting the E2 cache to dev-half users only (not on the full label-free cache) -- reading 'restrict to DEV-half users once the rule is known' (section A) as applying transitively to every downstream recomputation, including the axis recipe.
- gust1_E vector taken as-is from the existing V6_E2_ESSAYS_MOTION.json (not recomputed on dev-half-only data), per the literal instruction to pull 'vector from ... ["C_motion"]["gusts"][0]["vector"]'; this axis was estimated label-free on the full 2,309-essay cache (dev+confirm text, no labels), so reuse here has no label-governance implication.
- proj_dcomp1/2 use the raw slope vector d dotted with the (correlation-space) eigenvectors, without an extra per-column standardization of d -- the final global z-score step normalizes the resulting scalar feature regardless; this mirrors the 'simpler' framing used for the q-projection in the registration text.
- q = (w0-2wm+wl)/sqrt(6) computed WITHOUT the E2 script's extra /sd_w column normalization -- the registration text gives this exact formula with no sd term; taken literally rather than importing E2's normalization.
- 'set NaN -> mean-impute + indicator' was stated explicitly only for the D2 features (point 4); the same structural-missingness logic was generalized to the q-contrast features (point 3, m<3), since both are undefined below a window-count threshold and Ridge/Pearson cannot consume NaNs. This adds 2 indicator columns on top of the ~12 specified (13 substantive + 2 indicators = 15 motion features).
- D2 second differences use POSITIONALLY adjacent cache rows. For m<=12 essays (1153 of 1160 dev-covered essays; 99.4%) these are true consecutive 128-token windows. For the 7 dev-covered essays with m>12 (of 12 such essays in the full 2,309-essay corpus), the frozen cache stores only 12 linspace-subsampled representative windows, so 'lag-1' there spans a larger and uneven token gap -- an inherited property of reusing the cache as instructed, not a new choice.
- Lag-1 D2 autocorrelation is close to mathematically degenerate for the median essay: m==5 (the modal value, 194 of 1160 dev-covered essays) gives exactly 3 D2 points -> 2 correlation pairs, which is always +-1 or NaN by construction. Of the 663 m>=5 covered essays, 0 produced a degenerate (zero-variance) NaN autocorrelation, mean-imputed along with the structural m<5 NaNs. Reported honestly (see the m distribution above) rather than smoothed over.
- Section D 'mean Pearson r across folds' was read literally: Pearson r is computed WITHIN each of the 5 held-out folds and then averaged per trait -- NOT the 'pool out-of-fold predictions, compute one r' convention used by run_suica_dev_anchor_performance_v1.py and run_suica_expl3_motion_weightfit_v1.py. Per-fold r values are reported alongside the mean for full transparency.
- RidgeCV alpha grid np.logspace(-2, 3, 11) reused from the closest sibling script (run_suica_expl3_motion_weightfit_v1.py / EXPL-2), since none was specified here.
- log_tokens uses an exact re-tokenization of the raw essay text (label-free, user_id/text-only read) rather than a m*128 proxy, to avoid near-perfect collinearity with the 'm' feature (m*WIN and m differ only by a constant offset in log-space under floor division).
