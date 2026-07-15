#!/usr/bin/env python
"""Run the label-free V6 selection-preserving design simulation."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_sim.endogenous_selection import run_endogenous_selection_design  # noqa: E402


def _summary_value(result: dict, world: str, metric: str) -> str:
    values = result["worlds"][world]["summary"][metric]
    return f"{values['mean']:.3f} [{values['q025']:.3f}, {values['q975']:.3f}]"


def _report(result: dict, config_hash: str) -> str:
    selection, nuisance = result["worlds"]["selection_signal"], result["worlds"]["condition_nuisance"]
    return fr"""# V6 Selection-Preserving Design Simulation

## Question

Can one statistical rule decide whether topic/situation selection should be
subtracted from an author's text? No. This planted-world audit tests the design
rule instead: free selection is a distinct author-conditioned object, while a
balanced fixed-condition phase is the object that identifies conditional
expression and response contrasts.

For free observations:

\[
C_{{ui}} \sim \operatorname{{Categorical}}\{{\operatorname{{softmax}}(\lambda L a_u + \eta_u)\}},\qquad
Y_{{ui}}=a_u+\mu_{{C_{{ui}}}}+B_{{u,C_{{ui}}}}+\epsilon_{{ui}}.
\]

When `lambda > 0`, the population free-condition mean contains
`E[a_u | C=c]`; subtracting it therefore changes the author-level estimand.
The fixed phase assigns every `C` independently and equally often, so it can
estimate condition contrasts without using selection-linked author variation as
a condition baseline.

## Frozen setup

- profile: `{result['profile']}`
- repetitions: `{selection['n_repetitions']}` per world
- config SHA-256: `{config_hash}`
- external labels, raw text, and real author identifiers: not used

## Results

| world | raw free level r | free condition-centred level r | fixed-condition level r | free B support | free B r | fixed B support | fixed B r | held-out selection log-score gain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| selection-linked choice | {_summary_value(result, 'selection_signal', 'raw_free_level_recovery_r')} | {_summary_value(result, 'selection_signal', 'free_condition_centered_level_recovery_r')} | {_summary_value(result, 'selection_signal', 'fixed_condition_level_recovery_r')} | {_summary_value(result, 'selection_signal', 'free_response_support')} | {_summary_value(result, 'selection_signal', 'free_response_recovery_r')} | {_summary_value(result, 'selection_signal', 'fixed_response_support')} | {_summary_value(result, 'selection_signal', 'fixed_response_recovery_r')} | {_summary_value(result, 'selection_signal', 'selection_holdout_logscore_gain')} |
| condition-only nuisance | {_summary_value(result, 'condition_nuisance', 'raw_free_level_recovery_r')} | {_summary_value(result, 'condition_nuisance', 'free_condition_centered_level_recovery_r')} | {_summary_value(result, 'condition_nuisance', 'fixed_condition_level_recovery_r')} | {_summary_value(result, 'condition_nuisance', 'free_response_support')} | {_summary_value(result, 'condition_nuisance', 'free_response_recovery_r')} | {_summary_value(result, 'condition_nuisance', 'fixed_response_support')} | {_summary_value(result, 'condition_nuisance', 'fixed_response_recovery_r')} | {_summary_value(result, 'condition_nuisance', 'selection_holdout_logscore_gain')} |

## Gates

{json.dumps(result['gates'], indent=2, sort_keys=True)}

## Licensed conclusion

The simulation supports only a **design theorem in its planted family**: selection,
conditional expression, and response contrast are different estimands. A free
collection phase is appropriate for estimating a selection profile; it is not a
substitute for a balanced fixed-condition phase when estimating an individual
response operator. Conversely, condition centering can help in a condition-only
world but may remove selection-linked author variation in an endogenous-choice
world. No result establishes a human trait, a named SUICA factor, a clinical
signal, or a universal rule about topic removal.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results/v6_endogenous_selection_design")
    parser.add_argument("--report", type=Path, default=ROOT / "reports/V6_SELECTION_PRESERVING_DESIGN.md")
    args = parser.parse_args()
    config_path = ROOT / "configs/sim_v6" / f"endogenous_selection_{args.profile}.json"
    raw = config_path.read_bytes()
    result = run_endogenous_selection_design(json.loads(raw))
    config_hash = hashlib.sha256(raw).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / f"endogenous_selection_{args.profile}.json").write_text(
        json.dumps({"config_hash": config_hash, **result}, indent=2, sort_keys=True) + "\n"
    )
    args.report.write_text(_report(result, config_hash))
    print(json.dumps(result["gates"], indent=2, sort_keys=True))
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
