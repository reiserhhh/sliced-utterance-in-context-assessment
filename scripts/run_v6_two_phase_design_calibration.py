#!/usr/bin/env python3
"""Run the frozen V6 two-phase design calibration simulation."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim.two_phase_design_power import run_two_phase_design_calibration  # noqa: E402


def _interval(summary: dict[str, float]) -> str:
    """Format a simulation summary interval for the Markdown report."""
    return f"{summary['mean']:.3f} [{summary['q025']:.3f}, {summary['q975']:.3f}]"


def _fixed_table(rows: list[dict]) -> str:
    """Render the fixed-phase calibration grid."""
    body = [
        "| conditions | repeats/condition | total observations | level r | response r | support | qualified |",
        "|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in rows:
        summary = row["summary"]
        body.append(
            "| {conditions} | {repeats} | {total} | {level} | {response} | {support} | {qualified} |".format(
                conditions=row["conditions"],
                repeats=row["fixed_repeats_per_condition"],
                total=row["fixed_total_observations"],
                level=_interval(summary["fixed_condition_level_recovery_r"]),
                response=_interval(summary["fixed_response_recovery_r"]),
                support=_interval(summary["fixed_response_support"]),
                qualified="yes" if row["qualified"] else "no",
            )
        )
    return "\n".join(body)


def _free_table(rows: list[dict]) -> str:
    """Render the free-phase calibration grid."""
    body = [
        "| conditions | free trials | selection-profile r | held-out log-score gain | accidental B support | qualified |",
        "|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in rows:
        summary = row["summary"]
        body.append(
            "| {conditions} | {trials} | {profile} | {gain} | {support} | {qualified} |".format(
                conditions=row["conditions"],
                trials=row["free_trials"],
                profile=_interval(summary["selection_profile_truth_r"]),
                gain=_interval(summary["selection_holdout_logscore_gain"]),
                support=_interval(summary["free_response_support"]),
                qualified="yes" if row["qualified"] else "no",
            )
        )
    return "\n".join(body)


def _design_line(row: dict | None, *, phase: str) -> str:
    """Render a chosen design without implying human-study adequacy."""
    if row is None:
        return f"- {phase}: no grid point met the frozen synthetic criterion."
    if phase == "fixed numeric minimum" or phase == "fixed breadth recommendation":
        return (
            f"- {phase}: {row['conditions']} conditions x "
            f"{row['fixed_repeats_per_condition']} repeats = "
            f"{row['fixed_total_observations']} fixed observations."
        )
    return f"- {phase}: {row['free_trials']} free observations across {row['conditions']} conditions."


def _report(result: dict, config_hash: str) -> str:
    """Build the bounded, non-human-claim report."""
    chosen = result["selection"]
    return fr"""# V6 Two-Phase Design Calibration

## Question

What information budget is required by the two distinct V6 estimands in the
registered endogenous-selection world? This is a synthetic calibration, not a
human participant power calculation.

The free phase estimates a selection profile \(\pi_u\); the balanced fixed
phase estimates response contrasts \(B_u\):

\[
R_\pi=\operatorname{{corr}}(\operatorname{{vec}}\hat{{\pi}}_u,
                              \operatorname{{vec}}\pi_u),\qquad
R_B=\operatorname{{corr}}(\operatorname{{vec}}\hat B_u,
                            \operatorname{{vec}}B_u).
\]

The frozen criterion uses lower 2.5% simulation quantiles, not observed human
effect sizes.

## Frozen setup

- profile: `{result['profile']}`
- config SHA-256: `{config_hash}`
- repetitions per grid point: `{result['config']['repetitions']}`
- planted free-choice strength: `{result['config']['selection_strength']}`
- no labels, raw text, human identifiers, or clinical outcomes used

## Fixed-phase grid

{_fixed_table(result['fixed_grid'])}

## Free-phase grid

{_free_table(result['free_grid'])}

## Frozen synthetic selections

{_design_line(chosen['minimum_numerically_adequate_fixed_design'], phase='fixed numeric minimum')}
{_design_line(chosen['minimum_breadth_qualified_fixed_design'], phase='fixed breadth recommendation')}
{_design_line(chosen['minimum_qualified_free_design'], phase='free selection minimum')}

The first fixed selection minimizes numerical observations. The breadth
recommendation additionally requires the predeclared condition breadth and is
therefore the appropriate architecture when one wants to estimate more than a
binary response contrast.

## Gates

```json
{json.dumps(result['gates'], indent=2, sort_keys=True)}
```

## Licensed conclusion

Inside this planted generator, free and fixed phases need separate budgets:
free observations improve recovery of a choice distribution but provide only
accidental and incomplete support for response contrasts; balanced fixed
conditions make contrast support complete and improve precision by repeated
within-condition observations. The report supplies a reproducible design
calibration for future protocol construction only. It does not give a required
human sample size, establish a SUICA factor, validate a psychological construct,
or license clinical use.
"""


def main() -> None:
    """Parse arguments, execute the frozen profile, and write public summaries."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v6_two_phase_design_calibration",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "reports/V6_TWO_PHASE_DESIGN_CALIBRATION.md",
    )
    args = parser.parse_args()
    config_path = ROOT / "configs/sim_v6" / f"two_phase_design_calibration_{args.profile}.json"
    raw = config_path.read_bytes()
    config = json.loads(raw)
    result = run_two_phase_design_calibration(config)
    config_hash = hashlib.sha256(raw).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / f"two_phase_design_calibration_{args.profile}.json").write_text(
        json.dumps({"config_hash": config_hash, **result}, indent=2, sort_keys=True) + "\n"
    )
    args.report.write_text(_report(result, config_hash))
    print(json.dumps(result["gates"], indent=2, sort_keys=True))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
