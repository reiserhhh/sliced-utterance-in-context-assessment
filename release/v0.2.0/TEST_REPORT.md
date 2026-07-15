# SUICA v0.2.0 Test Report

Audit date: 2026-07-15

Environment: Python 3 with exact core dependencies in
`requirements-lock-v0.2.0.txt`.

| Check | Result |
| --- | --- |
| `python -m compileall -q suica_core suica_sim scripts tests` | PASS |
| `python -m pytest -q -p no:cacheprovider` | 302 passed in 29.58s |
| `python -m pytest -q -p no:cacheprovider tests/test_v7*.py` | 95 passed in 3.82s |
| `python scripts/verify_suica_v020_lockbox.py` | PASS after final manifest build |
| `git diff --check` | PASS |

These are code, simulation, schema, governance, and aggregate-evidence checks.
They are not a substitute for future reliability, external-validity, clinical,
language-invariance, or market-outcome data.
