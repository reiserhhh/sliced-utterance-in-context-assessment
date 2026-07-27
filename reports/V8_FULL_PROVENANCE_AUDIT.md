# SUICA V8 Full Provenance Audit

Status: `V8_FULL_PROVENANCE_PASS`

Checked frozen inputs, code, and inventoried artifacts: 70; failures: 0.

Historical shared-config commitments are resolved through exact content-addressed snapshots in `configs/archive/`.

| phase                       | expected_status                       | decision_status                       | manifest_status                       | status_ok   |
|:----------------------------|:--------------------------------------|:--------------------------------------|:--------------------------------------|:------------|
| v8_1_semantic               | V8_1_DOWNGRADE_RENDERER_ONLY          | V8_1_DOWNGRADE_RENDERER_ONLY          | V8_1_DOWNGRADE_RENDERER_ONLY          | True        |
| v8_1_semantic_attempt1_8192 | V8_1_DOWNGRADE_RENDERER_ONLY          | V8_1_DOWNGRADE_RENDERER_ONLY          | V8_1_DOWNGRADE_RENDERER_ONLY          | True        |
| v8_2_evidence               | V8_2_EXPLANATION_FIDELITY_PASS        | V8_2_EXPLANATION_FIDELITY_PASS        | V8_2_EXPLANATION_FIDELITY_PASS        | True        |
| v8_3_simulation             | V8_3_ORACLE_IDENTIFICATION_PASS       | V8_3_ORACLE_IDENTIFICATION_PASS       | V8_3_ORACLE_IDENTIFICATION_PASS       | True        |
| v8_4_realtext               | V8_4_SEMANTIC_CANDIDATE_RENDERER_ONLY | V8_4_SEMANTIC_CANDIDATE_RENDERER_ONLY | V8_4_SEMANTIC_CANDIDATE_RENDERER_ONLY | True        |
