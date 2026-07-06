#!/usr/bin/env python
"""Zero-data demo: run the synthetic estimator validations (P0 + P0-B).

These verify the SUICA estimator layer against planted ground truth without
any real dataset. Expected: P0_verdict pass, P0B_verdict pass.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for script in ("scripts/run_suica_synthetic_ground_truth_v2.py",
               "scripts/run_suica_p0b_thin_cell_regime_v3.py"):
    print(f"\n=== {script} ===")
    subprocess.run([sys.executable, str(ROOT / script)], check=True, cwd=ROOT)
