# SUICA V6 Dynamic Path Stage V1: Feasibility Gate

## Frozen question

Can the current PANDORA extraction supply four disjoint whole-run subepochs per
author for the frozen nonlinear dynamic-path confirmation? This is a metadata
and run-structure gate. No text representation, event, external label, or
endpoint dynamic result is read here.

## Input

- source: local `data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet` (not redistributed)
- SHA-256: `532ffc13a5b1333265e0dc32f290894a28d6211fa98e0746cbe41bf3bf8d914a`
- retained units: `597933`
- comments read: `1540040`

## Results

| partition_mode      |   n_total_authors |   n_eligible_authors |   n_engineering_authors |   n_endpoint_authors |   endpoint_pair_count |   endpoint_condition_coverage |   endpoint_median_jaccard | pass_endpoint_authors   | pass_condition_coverage   | stage_gate   |
|:--------------------|------------------:|---------------------:|------------------------:|---------------------:|----------------------:|------------------------------:|--------------------------:|:------------------------|:--------------------------|:-------------|
| time_balanced       |              3213 |                 1047 |                     201 |                  197 |                   394 |                         0.548 |                     0.125 | False                   | False                     | STOP         |
| transition_balanced |              3213 |                 1903 |                     379 |                  382 |                   764 |                         0.593 |                     0.143 | True                    | False                     | STOP         |

## Decision

`STOP`. The endpoint gate requires at least
`300` fixed-hash endpoint authors and at least
`80%` pair-level condition coverage at
Jaccard `>= 0.10`. A `STOP` result forbids
endpoint fitting, estimator relaxation, or window fishing in this stage. It
means only that current PANDORA does not support this registered design.

## Artifacts

- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility_detail.csv`
- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility_summary.csv`
- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility.json`
