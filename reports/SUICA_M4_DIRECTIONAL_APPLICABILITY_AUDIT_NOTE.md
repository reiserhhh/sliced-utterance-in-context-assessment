# M4 Directional Applicability Null-Parse Audit

## Defect

The sealed analyzer used pandas' default missing-value vocabulary. The literal
CSV value `null` in `world_type` was therefore parsed as missing, yielding
`null_cells=0` and the raw decision `M4_C35_DIRECTIONAL_INTEGRITY_STOP`.

## Correction

The raw stop report is preserved as
`reports/SUICA_M4_DIRECTIONAL_APPLICABILITY_DEVELOPMENT_RAW_PARSER_STOP.md`.
The independent audit wrapper
`scripts/audit_suica_m4_directional_applicability_null_parse.py` changes only
CSV parsing to `keep_default_na=False`, invokes the unchanged sealed analyzer,
and annotates the corrected outputs.

It does not change a model, feature, threshold, intervention, cell, response,
oracle endpoint, bootstrap, or gate. The original Stage-A manifest remains:

`907674b0d0d452e7ba937b3f92f1c170adde44023121b110faee1f9298c35a6c`

## Audited integrity

- sealed cells: `432`
- main cells: `360`
- null cells: `72`
- maximum B0/R basis replay error: `0`
- maximum signature replay error: `0`
- maximum response identity error: `0`
- maximum absolute null gain: `0`

## Audited decision

`M4_C35_PRE_RESPONSE_DOMAIN_NOT_IDENTIFIED`

The correction restores the registered null audit but does not rescue the
vector policy. LOWO and LORO both fail the prospective domain gates. Because
this is a post-seal lexical correction, the result remains development
evidence and cannot be promoted to confirmation.
