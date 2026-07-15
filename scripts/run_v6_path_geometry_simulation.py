#!/usr/bin/env python
"""Run the V6 nonlinear path-geometry simulation proof matrix."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim.path_geometry import PhaseCoupledSpec, evaluate_phase_coupled_world  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_path_geometry_simulation")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_PATH_GEOMETRY_SIMULATION.md")
    return parser.parse_args()


def summarize(values: np.ndarray) -> tuple[float, float, float]:
    return float(values.mean()), float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def main() -> None:
    args = parse_args()
    n_seeds = min(args.seeds, 20) if args.quick else args.seeds
    spec = PhaseCoupledSpec()
    rows = [{"seed": seed, **evaluate_phase_coupled_world(spec, seed=seed)} for seed in range(n_seeds)]
    output = pd.DataFrame(rows)
    summary_rows = []
    for column in ("linear_summary_auc", "conditional_phase_witness_auc", "shuffled_phase_witness_auc"):
        mean, lo, hi = summarize(output[column].to_numpy(float))
        summary_rows.append({"object": column, "mean_auc": mean, "q025": lo, "q975": hi})
    summary = pd.DataFrame(summary_rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output_dir / "seed_results.csv", index=False)
    summary.to_csv(args.output_dir / "summary.csv", index=False)
    payload = {"run": "SUICA_V6_PATH_GEOMETRY_SIMULATION_V1", "spec": spec.__dict__,
               "n_seeds": n_seeds, "summary": summary_rows}
    (args.output_dir / "result.json").write_text(json.dumps(payload, indent=2) + "\n")
    args.report.write_text(f"""# V6 Nonlinear Path-Geometry Simulation

## Planted world

For author phase `theta_u`, independent runs obey

\\[
Z_t\\sim Uniform(0,2\\pi),\\qquad
W_{{t+1}}=2Z_t+\\theta_u+\\eta_{{t+1}}\\pmod{{2\\pi}},
\\]

with `eta ~ von Mises(0, kappa={spec.kappa})`. Every author has the same marginal
state distribution, mean, covariance, and **linear** lag covariance. The author
signal is only the nonlinear conditional transition phase:

\\[
M_u=\\mathbb{{E}}\\left[e^{{i(W_{{t+1}}-2Z_t)}}\\right]
=\\frac{{I_1(\\kappa)}}{{I_0(\\kappa)}}e^{{i\\theta_u}}.
\\]

This is an explicit counterexample to the claim that mean/covariance/linear-AR
summaries exhaust path information. It is not a model of human language.

## Results across {n_seeds} independently generated worlds

{summary.to_markdown(index=False, floatfmt='.3f')}

## Interpretation

The linear family is expected to stay at chance because its population moments do
not contain `theta_u`. The conditional circular-kernel witness is expected to
recover it; endpoint-preserving interior shuffling must destroy that recovery.
The simulation therefore licenses only `SUPPORTED-SYNTHETIC`: a nonlinear
conditional transition object can capture a real, order-dependent author
configuration that linear factor-style summaries provably omit.
""")
    print(summary.to_string(index=False))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
