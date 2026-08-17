# SUICA M4-T1: Hierarchical Selection Identity

Status: exploratory mechanism discovery. This line is label-free by design.

## Question

Does an author's context-selection profile contain a reproducible hierarchy of
conditional innovations? In particular, can a residual left at one group level
become stable author information after the population is split at the next
level?

The proposed object is

\[
\pi_u-\bar\pi = \sum_{l=1}^{L} d_l(u)+r_L(u),
\qquad
d_l(u)=m_l(u)-m_{l-1}(u),
\]

where \(m_l(u)\) is the centroid of the nested selection group containing
author \(u\) at level \(l\). The terminal residual \(r_L\) is not declared
noise: it is tested for remaining same-author information.

## Design

1. Use the existing SR1 early/late subreddit-frequency matrices. No comment
   body and no personality label is read by the primary experiment.
2. Split authors into five folds. In each fold, fit a binary Hellinger-space
   selection tree using only the early vectors of the other four folds.
3. Freeze the tree and route both early and late vectors of held-out authors.
4. At each depth, test whether the child selected by the early half predicts
   the late vector better than its parent centroid.
5. Build a conditional null by permuting late vectors only among held-out
   authors sharing the same early parent node. This preserves the coarser group
   and tests the additional tail branch.
6. Compare flat Hellinger matching, hierarchical-path matching, and terminal
   within-leaf residual matching.
7. Repeat after removing explicitly named personality/typology communities.
   This is a sensitivity arm, not a redefinition of the primary object.

## Primary readings

- cross-half predictive gain by depth;
- within-parent permutation p-value by depth;
- early/late branch and prefix agreement above the conditional null;
- same-author AUC from hierarchical paths versus flat Hellinger AUC;
- terminal residual same-author AUC within frozen leaves.

## Interpretation rules

- A positive held-out branch gain means that a residual at the parent level
  contains reproducible structure at the child level.
- A rare branch is not identity merely because it is rare. It must replicate
  across halves and held-out authors.
- Positive terminal-residual AUC means the fitted depth has not exhausted the
  stable author structure.
- Results establish selection-based author information, not personality. A
  psychological interpretation requires a later, separately registered
  external-connection study.
- Failure of the cleaned arm means the apparent identity hierarchy is specific
  to explicit typology communities or their ecology.

## Controls

- planted hierarchical-choice simulation;
- author-null simulation with identical population choice probabilities;
- held-out-author tree fitting;
- within-parent permutation rather than unrestricted pair permutation;
- explicit-personality-community ablation;
- no Big5/MBTI labels during model construction or primary scoring.

## Outputs

- `results/m4_t1_hierarchical_selection_identity/summary.json`
- `results/m4_t1_hierarchical_selection_identity/metrics_by_depth.csv`
- `results/m4_t1_hierarchical_selection_identity/per_user_depth.csv`
- `reports/SUICA_M4_T1_HIERARCHICAL_SELECTION_IDENTITY_REPORT.md`

## Completed reading (2026-08-17)

The mechanism test completed on held-out PANDORA authors. The primary full arm
retained five stable conditional levels; the arm excluding explicitly named
personality/typology communities retained four. At each retained level, all
three criteria agreed: the early child centroid improved late-half fit over
the parent, the late half locally replayed the early child above a
within-parent permutation null, and the early child reduced uncertainty about
the late child by positive permutation-corrected conditional mutual
information. In the cleaned arm, levels five and six still showed branch
replay and excess information, but their centroid-gain confidence intervals
crossed zero. They are therefore recorded as reproducible categorical code,
not confirmed predictive innovations.

The result supports a mixed representation:

\[
\pi_u-\bar\pi
=\sum_{l=1}^{L}d_l(u)+r_L(u),
\qquad
I(C_{u,l}^{early};C_{u,l}^{late}\mid P_{u,l})>0,
\]

where the discrete innovations are reproducible but do not exhaust identity.
Terminal within-leaf residual AUC remained above `.94` in both arms and above
`.94` across all resolution checks. Increasing tree depth therefore does not
turn the tail into a finite list of ever-smaller types. The current evidence
is more consistent with **nested conditional choices plus a continuous or
higher-order author coordinate**.

This is a label-free author-identity result. It does not identify personality,
and it does not license naming branches. The next scientific leg must separate
stable identity carried by topic/community history from psychologically valid
person-level structure using condition-matched controls and an independently
specified external-connection analysis.
