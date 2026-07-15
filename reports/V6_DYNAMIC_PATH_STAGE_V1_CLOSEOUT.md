# SUICA V6 Dynamic Path Stage V1: Closeout

Status: `STOP_AT_FEASIBILITY_GATE`
Date: 2026-07-14

## Frozen question

Can the existing PANDORA extraction support a four-disjoint-subepoch,
whole-run, condition-aware nonlinear dynamic-path confirmation without treating
windows or transitions as independent people?

The protocol was fixed in
[`V6_DYNAMIC_PATH_STAGE_V1_PROTOCOL.md`](../docs/V6_DYNAMIC_PATH_STAGE_V1_PROTOCOL.md)
before endpoint fitting. It requires at least 300 fixed-hash endpoint authors
and at least 80% early/late condition-pair coverage at Jaccard `>= .10`.

## Input and execution

- Source was the local Tier-U PANDORA parquet, SHA-256
  `532ffc13a5b1333265e0dc32f290894a28d6211fa98e0746cbe41bf3bf8d914a`.
- The metadata gate read 1,540,040 source comments and retained 597,933
  analysis units.
- It used no external scales, author labels in model fitting, text-event
  selection, embeddings, or raw-text interpretation.
- Complete same-condition runs remained intact; no transition crossed a run,
  condition, or sampling gap.

## Gate result

| Partition | Eligible authors | Endpoint authors | Endpoint pair coverage | Endpoint median Jaccard | Gate |
|:--|--:|--:|--:|--:|:--|
| `transition_balanced` | 1,903 | 382 | .593 | .143 | STOP |
| `time_balanced` | 1,047 | 197 | .548 | .125 | STOP |

`transition_balanced` clears the author-count requirement but fails the
condition-coverage requirement. `time_balanced` fails both. The stage result is
therefore a protocol-level refusal: current PANDORA cannot supply an adequately
matched four-subepoch confirmation of an author-conditioned dynamic path.

## What was not run

The following analyses are intentionally not run and must not be reconstructed
post hoc from this corpus:

- nonlinear endpoint retrieval for \(G_{u,b}\);
- ordered-minus-shuffled endpoint inference;
- representation/partition robustness selection;
- numeric-event to text correspondence;
- any named dynamic factor, individual response operator, causal, personality,
  or quantum-mechanics claim.

The refusal is informative. It localizes the bottleneck in experimental support
and matched condition coverage, not in a failure to try enough nonlinear models.

## MEPS branch

MEPS remains a separate fixed-condition, same-session pilot. It is not used to
rescue this PANDORA conclusion. A later local-only frozen multilingual-vector
profile run is recorded separately in
`reports/MEPS_V6_FIXED_CONDITION_PROFILE.md`; it is `NOT_PROMOTED` under its
own fixed-prompt correspondence gate. That single-session result neither
supplies PANDORA's missing four-subepoch condition coverage nor licenses a
dynamic response-operator claim. The Japanese lexical scorer remains
machinery-grade pending within-language longitudinal revalidation.

## Next data requirement

The next valid dynamic study needs the same participants at three occasions,
repeated common conditions and two independent elicited runs per condition, with
explicit opportunity metadata. Only that design can separately estimate a
context-dependent text path and test whether any author response operator
repeats. The protocol already specifies this future design; no further PANDORA
dynamic search is authorized by this stage.

## Artifacts

- `configs/v6_dynamic_path_stage_v1.json`
- `scripts/run_suica_v6_dynamic_path_feasibility.py`
- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility_detail.csv`
- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility_summary.csv`
- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility.json`
