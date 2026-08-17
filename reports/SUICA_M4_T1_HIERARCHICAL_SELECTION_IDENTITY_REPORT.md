# SUICA M4-T1: Hierarchical Selection Identity

Generated 2026-08-16T18:24:41.964657+00:00. Tier: **EXPLORATORY, label-free,
selection-based author structure only**.

## Outcome

Full arm: **`HIERARCHICAL_INNOVATIONS_DETECTED`**. Explicit-personality-community ablation:
**`HIERARCHICAL_INNOVATIONS_DETECTED`**.

Resolution sensitivity: **`TREE_DOES_NOT_EXHAUST_IDENTITY_TAIL`**.

The experiment asks whether the residual left after assigning an author to a
broad context-selection group becomes reproducible information at the next
group level. Trees were fitted only on training authors' early halves and then
frozen. Every reported gain is measured on held-out authors' late halves.

## Synthetic controls

| world | flat AUC | path AUC | terminal residual AUC |
|---|---|---|---|
| planted hierarchy | 0.9676 | 0.9407 | 0.7243 |
| author null | 0.5061 | 0.4957 | 0.5027 |

The planted world is the positive control. In the null world every author has
the same choice distribution, so both flat and hierarchical identity readings
should remain near chance.

## PANDORA summary

| arm | N | flat AUC | path AUC | terminal residual AUC | stable depths | decision |
|---|---|---|---|---|---|---|
| full | 1304 | 0.9837 | 0.7461 | 0.9552 | 1,2,3,4,5 | HIERARCHICAL_INNOVATIONS_DETECTED |
| clean_no_explicit_personality | 1269 | 0.9661 | 0.7317 | 0.9417 | 1,2,3,4 | HIERARCHICAL_INNOVATIONS_DETECTED |

`flat AUC` uses early-to-late Hellinger cosine. `path AUC` uses the length of
the common frozen-tree prefix. `terminal residual AUC` compares authors only
inside the same early leaf after subtracting that leaf's training centroid.

## Depth-by-depth residual replay

| arm | depth | N | gain | bootstrap 95% CI | conditional null | perm p | local branch agreement | branch null | conditional MI bits | MI null | excess bits | MI perm p | prefix agreement |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 1 | 1304 | 0.05442 | [0.04452, 0.06374] | -0.08089 | 0.002 | 0.8213 | 0.5291 | 0.29571 | 0.00277 | 0.29295 | 0.002 | 0.8213 |
| full | 2 | 1304 | 0.06845 | [0.05988, 0.07741] | -0.07416 | 0.002 | 0.8229 | 0.5147 | 0.34699 | 0.00548 | 0.34151 | 0.002 | 0.6894 |
| full | 3 | 1041 | 0.06011 | [0.04998, 0.06972] | -0.07824 | 0.002 | 0.8655 | 0.5892 | 0.34859 | 0.01148 | 0.33711 | 0.002 | 0.6436 |
| full | 4 | 679 | 0.04657 | [0.03659, 0.05575] | -0.05078 | 0.002 | 0.8233 | 0.5652 | 0.30795 | 0.01693 | 0.29101 | 0.002 | 0.5538 |
| full | 5 | 399 | 0.01727 | [0.00868, 0.02689] | -0.03487 | 0.002 | 0.7995 | 0.5917 | 0.24299 | 0.02433 | 0.21867 | 0.002 | 0.4637 |
| full | 6 | 26 | 0.00205 | [-0.00438, 0.00888] | -0.01149 | 0.002 | 0.8462 | 0.7416 | 0.09365 | 0.03434 | 0.05931 | 0.114 | 0.3846 |
| clean_no_explicit_personality | 1 | 1269 | 0.05040 | [0.03955, 0.06047] | -0.07522 | 0.002 | 0.8337 | 0.5555 | 0.29564 | 0.00292 | 0.29272 | 0.002 | 0.8337 |
| clean_no_explicit_personality | 2 | 1269 | 0.04694 | [0.03799, 0.05597] | -0.06855 | 0.002 | 0.8038 | 0.5153 | 0.28516 | 0.00581 | 0.27934 | 0.002 | 0.6903 |
| clean_no_explicit_personality | 3 | 993 | 0.02015 | [0.01373, 0.02683] | -0.03049 | 0.002 | 0.8540 | 0.6828 | 0.19207 | 0.01094 | 0.18112 | 0.002 | 0.6153 |
| clean_no_explicit_personality | 4 | 817 | 0.00729 | [0.00313, 0.01154] | -0.02674 | 0.002 | 0.7540 | 0.5376 | 0.17692 | 0.01483 | 0.16209 | 0.002 | 0.4774 |
| clean_no_explicit_personality | 5 | 464 | 0.00232 | [-0.00204, 0.00700] | -0.02110 | 0.002 | 0.7651 | 0.5765 | 0.16851 | 0.02023 | 0.14828 | 0.002 | 0.4030 |
| clean_no_explicit_personality | 6 | 106 | 0.00519 | [-0.00451, 0.01620] | -0.02111 | 0.002 | 0.7736 | 0.6083 | 0.15683 | 0.03568 | 0.12114 | 0.002 | 0.3491 |

The null permutes late vectors only inside the same early parent node. A
positive gain therefore cannot be attributed merely to sharing the broader
prefix. `local branch agreement` asks whether the late half selects the same
child when both halves are evaluated inside that fixed early parent; it does
not require the late half to reproduce every earlier branch. `excess bits` is
the conditional mutual information left after subtracting its finite-sample
permutation baseline. A level is called stable only when centroid gain,
local-branch replay, and excess information all pass. A deeper level may carry
reproducible categorical code while failing the centroid-gain criterion; that
is evidence against reducing the tail to one hard centroid per branch.

## Resolution sensitivity

| configuration | max depth | min leaf | seed | path AUC | terminal residual AUC | stable depths | median leaves |
|---|---|---|---|---|---|---|---|
| base_d6_l30 | 6 | 30 | 20260817 | 0.7461 | 0.9552 | 1,2,3,4,5 | 11.0 |
| coarse_d6_l60 | 6 | 60 | 20260817 | 0.7428 | 0.9650 | 1,2,3,4 | 8.0 |
| seed_2_d6_l30 | 6 | 30 | 20260918 | 0.7469 | 0.9543 | 1,2,3,4,5 | 15.0 |
| seed_3_d6_l30 | 6 | 30 | 20261019 | 0.7504 | 0.9541 | 1,2,3,4,5 | 15.0 |
| deep_d8_l15 | 8 | 15 | 20260817 | 0.7577 | 0.9465 | 1,2,3,4,5,6 | 29.0 |
| deep_d9_l10 | 9 | 10 | 20260817 | 0.7613 | 0.9473 | 1,2,3,4,5,6,7,8,9 | 38.0 |

Deeper trees add stable branch innovations, but path AUC changes little while
terminal within-leaf residual AUC remains high. The hierarchy is therefore a
coarse discrete code, not an exhaustive representation of author identity.
The tail is not explained merely by requesting more binary cuts at smaller
leaf sizes; it contains a stable continuous or higher-order component that a
hard tree does not capture.

## Personality-community sensitivity

- Reconstructed vocabulary: 1191 dimensions at the
  original SR0 floor.
- Explicit personality/typology dimensions removed: 23.
- Removed names: ENFP, ESFJ, ESFP, ESTJ, Enneagram, INTP, ISTJ, Jung, JungianTypology, MbtiTypeMe, enfj, entj, entp, estp, infj, infp, intj, introvert, isfj, isfp, istp, mbti, shittyMBTI.

This arm does not declare those communities invalid. It asks whether the
hierarchy survives after removing the most criterion-adjacent Where choices.

## Theoretical reading

At level `l`, the branch innovation is the child centroid minus the parent
centroid. The empirical question is whether an early-half choice of that child
reduces held-out late-half error. When it does, the parent's residual contains
reproducible next-level structure:

    residual_l = stable_innovation_(l+1) + residual_(l+1)

A non-chance terminal residual means the fitted tree has not exhausted author
information. It does not mean that the residual is personality, nor that
deeper splitting is automatically warranted.

## Boundaries

- No Big5 or MBTI value was used in fitting, routing, or deciding this leg.
- The object is subreddit-selection behavior in one Reddit cohort. It may
  contain interests, demographics, platform history, community affiliation,
  and personality.
- Same-author discrimination is identity information, not psychological
  validity.
- A later study must test whether stable branch innovations transport to a
  second corpus and whether any branch has behavioral or psychological meaning.

## Configuration

```json
{
  "bootstrap": 1000,
  "conditional_null": "late vectors permuted within early parent node",
  "folds": 5,
  "max_depth": 6,
  "min_leaf": 30,
  "permutations": 499,
  "primary_is_label_free": true,
  "seed": 20260817,
  "tree_input": "sqrt frequency / Hellinger unit sphere"
}
```
