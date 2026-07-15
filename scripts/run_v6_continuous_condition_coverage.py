#!/usr/bin/env python3
"""Run the V6 continuous condition-manifold coverage audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim.continuous_condition_coverage import run_continuous_condition_coverage  # noqa: E402


def _interval(values: dict[str, float]) -> str:
    """Format one simulation mean and central interval."""
    return f"{values['mean']:.3f} [{values['q025']:.3f}, {values['q975']:.3f}]"


def _report(result: dict, config_hash: str) -> str:
    """Render the bounded result report."""
    rows = [
        "| scenario | held-out response r | response MSE | level r | coverage radius | fixed observations |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, summary in result["scenarios"].items():
        rows.append(
            "| {name} | {response} | {mse} | {level} | {coverage} | {total} |".format(
                name=name,
                response=_interval(summary["response_function_recovery_r"]),
                mse=_interval(summary["response_function_mse"]),
                level=_interval(summary["author_level_recovery_r"]),
                coverage=_interval(summary["context_coverage_radius"]),
                total=_interval(summary["fixed_total_observations"]),
            )
        )
    return fr"""# V6 Continuous Condition-Manifold Coverage Audit

## Question

Does a balanced fixed schedule alone identify a conditional response function
when topic/situation/opportunity occupies a continuous multidimensional space?
This is a planted-world audit only.

The generator is

\[
Y_{{ui}}=a_u+m(z_{{ui}})+B_u\phi(z_{{ui}})+\epsilon_{{ui}},\qquad z\in\mathbb{{R}}^2.
\]

All arms have the same author count and the narrow and wide exact arms have the
same per-author fixed-observation budget. `wide_exact` observes a full smooth
condition map across the full grid. `narrow_exact_same_budget` spends that
budget repeatedly in one half of the manifold. `wide_coarse_proxy` covers the
full grid but its estimator sees only the first context coordinate.

## Frozen setup

- profile: `{result['profile']}`
- config SHA-256: `{config_hash}`
- repetitions per arm: `{result['config']['repetitions']}`
- no human text, labels, author IDs, or clinical outcomes used

## Results

{chr(10).join(rows)}

## Gates

```json
{json.dumps(result['gates'], indent=2, sort_keys=True)}
```

## Licensed conclusion

Within this planted family, balancing over a *coarse* or *narrowly covered*
condition representation is not equivalent to balancing over the full condition
manifold. Thus future V6 fixed-prompt work must predefine both condition
representation and coverage diagnostics; simply giving every participant the
same number of prompts is insufficient. This does not validate any human
condition ontology, author trait, factor, or clinical assessment.
"""


def main() -> None:
    """Run a registered profile and save JSON plus a public Markdown report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "results/v6_continuous_condition_coverage"
    )
    parser.add_argument(
        "--report", type=Path, default=ROOT / "reports/V6_CONTINUOUS_CONDITION_COVERAGE.md"
    )
    args = parser.parse_args()
    config_path = ROOT / "configs/sim_v6" / f"continuous_condition_coverage_{args.profile}.json"
    raw = config_path.read_bytes()
    result = run_continuous_condition_coverage(json.loads(raw))
    config_hash = hashlib.sha256(raw).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / f"continuous_condition_coverage_{args.profile}.json").write_text(
        json.dumps({"config_hash": config_hash, **result}, indent=2, sort_keys=True) + "\n"
    )
    args.report.write_text(_report(result, config_hash))
    print(json.dumps(result["gates"], indent=2, sort_keys=True))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
