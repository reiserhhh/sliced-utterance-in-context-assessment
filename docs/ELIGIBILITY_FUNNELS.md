# Eligibility Funnels (OP-20)

Every analysis conditions on users with sufficient text. This table makes the
funnel explicit per experiment (source artifact in parentheses; all numbers
appear in the cited reports). Population: Tier U = 8,678 PANDORA MBTI-axis
users after lockbox exclusion; working extraction = 5,000 stable-hash sample
(cap 400 comments); deep extraction = 2,000 highest-volume users (cap 1,200).

| Analysis | Pool | Gate | Analyzed n |
|---|---|---|---|
| P1 disjoint retest (s128) | 5,000 sample -> 2,942 with 90d-gap slices | shared conditions >= 2, >= 6 slices/half | 1,437 users (suica_p1_disjoint_retest_v2_s128.md) |
| P1 deep (OP-12) | 2,000 deep | same | 1,351 (suica_p1_disjoint_retest_v2_deep128.md) |
| P2 centering value | 4,983 pass-B users | >= 4 conditions x >= 3 slices | 3,726 (suica_p2_condition_centering_v2_s128.md) |
| PRED-1 paired rind | 5,000 sample | top-sub >= 20 & others >= 20 comments & >= 4 other subs | 918 (suica_rind_regime_test_v3.md) |
| E5 spectrum (quarter/month) | 5,000 sample | top-sub >= 12; >= 4 occasions x >= 2 comments | 3,700 / 4,331 (suica_e5_* reports) |
| E6 react stranger-null | 2,000 deep -> 1,669 class-mapped | >= 5 shared thick classes (>= 6 slices/cell), 90d gap | 195 (suica_e6_react_stranger_null_v3.md) |
| E7 state discovery | 2,000 deep | top-sub >= 30 comments; >= 6 months x >= 4 slices | 1,175 (suica_e7_within_state_discovery_v3_month.md) |
| OP-5 discovery/confirm | 3,183 half-eligible (>= 6 slices both halves) | A/B user split | 1,589 discover / 1,594 confirm (suica_op5_construct_discovery_v3.md) |
| OP-6a choice holdout | 5,000 sample | >= 40 comments, 90d gap, >= 15/half | A 1,586 / B 1,615 (suica_op6a_choice_axes_holdout_v3.md) |
| OP-9 / E9 / E11 | half-eligible pool | both halves present | 3,183 (suica_op9 / e9 / e11 reports) |
| OP-22 item bank | 58,386 B-half clean slices | exemplar margin >= 1.0 z etc. | 240 items / 90 pairs (results manifest) |
| DEV-ANCHOR MBTI | battery users x Tier-D labels | intersection | 3,183 (suica_dev_anchor_performance_v1.md) |
| DEV-ANCHOR Essays | 2,467 essays -> 1,255 dev-half | dev-half membership | 1,255 (same) |
| Lockbox (sealed) | Big5 1,401 / bridge 375 | >= 4 conds x >= 4 comments & >= 12 est. slices (metadata-only count) | eligible 1,108 / 326 (PREREGISTRATION.md) |

Reading: all trait-level results describe users who write enough (medians
~44-372 comments in the respective pools). Generalization to light writers is
an open limitation (OPEN_PROBLEMS OP-20 note; volume-reliability curves in
the manual give the required-text floors).
