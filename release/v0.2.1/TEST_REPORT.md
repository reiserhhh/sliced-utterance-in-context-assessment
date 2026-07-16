# SUICA v0.2.1 Test Report

Audit date: 2026-07-17

v0.2.1 is the remediation release following the 2026-07-15 adversarial process
audit of v0.2.0. See `docs/RELEASE_NOTES_V021.md` for the full change list,
`docs/V7_PROCESS_AUDIT_20260717.md` for the permanent process record, and
`docs/V7_W10_AUDIT.md` for the W10/E4 audit grounds. `release/v0.2.0/` is the
immutable historical record of the prior release; its manifest, test report,
and evidence snapshots are sealed (hashed) inside this release's
`LOCKBOX_MANIFEST.json`.

Environment: Python 3 with exact core dependencies in
`requirements-lock-v0.2.0.txt` (lock unchanged for v0.2.1).

| Check | Result |
| --- | --- |
| `python -m compileall -q suica_core suica_sim scripts tests` | PASS |
| `python -m pytest -q -p no:cacheprovider` | 318 passed in 31.27s |
| `python -m pytest -q -p no:cacheprovider tests/test_v7*.py` | 111 passed in 4.47s |
| `python scripts/verify_suica_v020_lockbox.py --content-only` | FAIL as expected on the corrected tree: exactly the 23 lockboxed files changed by the 2026-07-17 remediation mismatch; verifiable only at the v0.2.0 tag checkout |
| `python scripts/verify_suica_v021_lockbox.py --content-only` | PASS after final manifest build |
| `git diff --check` | PASS |

Evidence pointers (same frozen 2026-07-15 source runs as v0.2.0; the
remediation corrected process, labels, and documentation — no evidence
artifact was recomputed):

| Evidence | Source run |
| --- | --- |
| W2_IDENTIFICATION | `results/v7_identification/w2_corrected_full_20260715` |
| W3_TEMPORAL_RANDOM | `results/v7_temporal_geometry/w3_temporal_random_corrected_full_20260715` |
| W4_MULTIVIEW_METHODS | `results/v7_multiview_benchmark/w4b_corrected_full_20260715` |
| W4B_EFFECTIVE_RANK | `results/v7_multiview_spectrum/w4b_effective_rank_corrected_20260715` |
| W7_REPRESENTATION_TRANSPORT | `results/v7_representation_transport/w7_full_20260715` |
| G1_REAL_DATA_GEOMETRY | `results/v7_geometry/g1_corrected_v2_full_20260715` |

These are code, simulation, schema, governance, and aggregate-evidence checks.
They are not a substitute for future reliability, external-validity, clinical,
language-invariance, or market-outcome data.
