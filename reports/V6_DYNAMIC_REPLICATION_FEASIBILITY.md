# SUICA V6 Dynamic Replication Feasibility

## Question

Can the current raw PANDORA extraction identify a stable dynamic author-path
object separately from persistent state or measurement error? The required next
design uses each early/late half as two chronological epochs, and each epoch as
two independent replicas made from complete same-condition runs. No run or
transition is split.

## Feasibility table

|   min_runs |   min_transitions |   n_user_halves |   n_feasible |   median_runs |   median_transitions |   feasible_rate |   n_two_half_authors |
|-----------:|------------------:|----------------:|-------------:|--------------:|---------------------:|----------------:|---------------------:|
|      1.000 |             3.000 |        6426.000 |     3874.000 |         9.000 |               22.000 |           0.603 |             1403.000 |
|      1.000 |             6.000 |        6426.000 |     2093.000 |         9.000 |               22.000 |           0.326 |              531.000 |
|      1.000 |            12.000 |        6426.000 |      282.000 |         9.000 |               22.000 |           0.044 |               16.000 |
|      2.000 |            12.000 |        6426.000 |      201.000 |         9.000 |               22.000 |           0.031 |                9.000 |

## Interpretation

The registered current dynamic estimator requires at least two runs and twelve
transitions per view. Under that criterion, `9`
authors can supply all four replicas in both long-interval halves. If this count
is too small for a predeclared inferential target, PANDORA cannot resolve
author-level dynamics from persistent state; the correct conclusion is
`UNIDENTIFIABLE_WITH_CURRENT_CORPUS`, not a failed dynamic construct.

Relaxed rows are engineering feasibility only. They do not license an estimator
change or a psychological interpretation. Any follow-up must freeze run splitting,
time cut rules, and minimum transitions before estimating scores.
