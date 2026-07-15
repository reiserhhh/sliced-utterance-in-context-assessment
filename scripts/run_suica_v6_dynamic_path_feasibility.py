#!/usr/bin/env python
"""Run the frozen Stage V1 metadata feasibility gate before endpoint fitting.

This script does not fit a text representation, inspect high-dynamic text, or
read external labels.  It asks only whether complete PANDORA runs can support
the predeclared four-subepoch design without pseudo-replication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_v6_factor_discovery_v2 import prepare_units  # noqa: E402
from suica_core.dynamic_path_objects import (  # noqa: E402
    RunSegment,
    condition_jaccard,
    split_four_subepochs,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=ROOT / "data_sets/prepared/suica_tiers_v2/tier_u_comments.parquet")
    parser.add_argument("--config", type=Path,
                        default=ROOT / "configs/v6_dynamic_path_stage_v1.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "results/v6_dynamic_path_stage_v1")
    parser.add_argument("--report", type=Path,
                        default=ROOT / "reports/V6_DYNAMIC_PATH_FEASIBILITY.md")
    return parser.parse_args()


def _stable_bucket(user_id: str, modulus: int) -> int:
    """Assign an author to a deterministic hash bucket."""
    digest = hashlib.sha256(f"v6-dynamic-path-stage-v1::{user_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big") % modulus


def _cohort(user_id: str, cfg: dict) -> str:
    """Reserve one confirmation bucket as the untouched prospective endpoint."""
    bucket = _stable_bucket(user_id, int(cfg["endpoint_hash_modulus"]))
    if bucket == int(cfg["endpoint_hash_residue"]):
        return "endpoint"
    if bucket == int(cfg["engineering_hash_residue"]):
        return "engineering"
    return "other_confirmation"


def _source_sha256(path: Path) -> str:
    """Hash a potentially large local parquet without reading it into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _extract_run_segments(units: pd.DataFrame) -> dict[tuple[str, str], list[RunSegment]]:
    """Recover continuous retained runs with both start and end timestamps."""
    output: dict[tuple[str, str], list[RunSegment]] = {}
    for (user, half), group in units.groupby(["user_id", "half"], observed=True, sort=False):
        segments: list[RunSegment] = []
        for run_id, run in group.groupby("run_id", observed=True, sort=False):
            ordered = run.sort_values("run_pos")
            positions = ordered["run_pos"].to_numpy(int)
            if len(positions) < 2 or not (positions[1:] - positions[:-1] == 1).all():
                continue
            segments.append(RunSegment(
                run_id=str(run_id),
                condition=str(ordered["condition"].iloc[0]),
                start_time=float(ordered["created_utc"].min()),
                end_time=float(ordered["created_utc"].max()),
                transitions=len(positions) - 1,
            ))
        output[(str(user), str(half))] = sorted(segments, key=lambda item: item.start_time)
    return output


def _summary(detail: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Summarize eligibility and condition overlap by frozen partition scheme."""
    records: list[dict[str, object]] = []
    for mode, group in detail.groupby("partition_mode", observed=True):
        eligible = group.loc[group["eligible"]].copy()
        endpoint = eligible.loc[eligible["cohort"].eq("endpoint")]
        pair_values = endpoint[["pair_0_jaccard", "pair_1_jaccard"]].to_numpy(float).ravel()
        coverage = float((pair_values >= float(cfg["condition_jaccard_threshold"])).mean()) if len(pair_values) else 0.0
        endpoint_authors = int(endpoint["user_id"].nunique())
        pass_authors = endpoint_authors >= int(cfg["minimum_endpoint_authors"])
        pass_coverage = coverage >= float(cfg["minimum_condition_coverage"])
        records.append({
            "partition_mode": mode,
            "n_total_authors": int(group["user_id"].nunique()),
            "n_eligible_authors": int(eligible["user_id"].nunique()),
            "n_engineering_authors": int(eligible.loc[eligible["cohort"].eq("engineering"), "user_id"].nunique()),
            "n_endpoint_authors": endpoint_authors,
            "endpoint_pair_count": int(len(pair_values)),
            "endpoint_condition_coverage": coverage,
            "endpoint_median_jaccard": float(pd.Series(pair_values).median()) if len(pair_values) else 0.0,
            "pass_endpoint_authors": pass_authors,
            "pass_condition_coverage": pass_coverage,
            "stage_gate": "PASS" if pass_authors and pass_coverage else "STOP",
        })
    return pd.DataFrame(records)


def main() -> None:
    args = parse_args()
    if not args.input.exists():
        raise FileNotFoundError(
            f"Input not found: {args.input}. Pass the local, gitignored PANDORA "
            "Tier-U parquet explicitly with --input."
        )
    cfg = json.loads(args.config.read_text())
    base_config = ROOT / cfg["base_config"]
    base = json.loads(base_config.read_text())
    merged_cfg = {**base, **cfg}
    comments = pd.read_parquet(args.input, columns=["author", "body", "created_utc", "subreddit"])
    units = prepare_units(comments, merged_cfg)
    runs = _extract_run_segments(units)
    records: list[dict[str, object]] = []
    for user_id in sorted({user for user, _ in runs}):
        early_runs = runs.get((user_id, "early"), [])
        late_runs = runs.get((user_id, "late"), [])
        for mode in cfg["partition_modes"]:
            subepochs = split_four_subepochs(
                early_runs, late_runs, mode=mode,
                whole_half_min_runs=int(cfg["whole_half_min_runs"]),
                whole_half_min_transitions=int(cfg["whole_half_min_transitions"]),
                subepoch_min_runs=int(cfg["subepoch_min_runs"]),
                subepoch_min_transitions=int(cfg["subepoch_min_transitions"]),
            )
            record: dict[str, object] = {
                "user_id": user_id,
                "cohort": _cohort(user_id, cfg),
                "partition_mode": mode,
                "early_complete_runs": len(early_runs),
                "late_complete_runs": len(late_runs),
                "early_transitions": sum(run.transitions for run in early_runs),
                "late_transitions": sum(run.transitions for run in late_runs),
                "eligible": subepochs is not None,
            }
            if subepochs is None:
                record.update({
                    "pair_0_jaccard": float("nan"), "pair_1_jaccard": float("nan"),
                    "subepoch_transitions": "",
                    "subepoch_conditions": "",
                })
            else:
                record.update({
                    "pair_0_jaccard": condition_jaccard(subepochs["early_0"], subepochs["late_0"]),
                    "pair_1_jaccard": condition_jaccard(subepochs["early_1"], subepochs["late_1"]),
                    "subepoch_transitions": ";".join(
                        str(sum(run.transitions for run in subepochs[key]))
                        for key in ("early_0", "early_1", "late_0", "late_1")
                    ),
                    "subepoch_conditions": ";".join(
                        str(len({run.condition for run in subepochs[key]}))
                        for key in ("early_0", "early_1", "late_0", "late_1")
                    ),
                })
            records.append(record)
    detail = pd.DataFrame(records)
    summary = _summary(detail, cfg)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    detail.to_csv(args.output_dir / "dynamic_path_feasibility_detail.csv", index=False)
    summary.to_csv(args.output_dir / "dynamic_path_feasibility_summary.csv", index=False)
    source_hash = _source_sha256(args.input)
    result = {
        "run": cfg["run_name"],
        "input": str(args.input),
        "input_sha256": source_hash,
        "config": cfg,
        "n_comments": int(len(comments)),
        "n_units": int(len(units)),
        "summary": summary.to_dict(orient="records"),
        "decision": "PROCEED" if bool(summary["stage_gate"].eq("PASS").any()) else "STOP",
        "labels_used": False,
    }
    (args.output_dir / "dynamic_path_feasibility.json").write_text(json.dumps(result, indent=2) + "\n")
    args.report.write_text(f"""# SUICA V6 Dynamic Path Stage V1: Feasibility Gate

## Frozen question

Can the current PANDORA extraction supply four disjoint whole-run subepochs per
author for the frozen nonlinear dynamic-path confirmation? This is a metadata
and run-structure gate. No text representation, event, external label, or
endpoint dynamic result is read here.

## Input

- source: `{args.input}`
- SHA-256: `{source_hash}`
- retained units: `{len(units)}`
- comments read: `{len(comments)}`

## Results

{summary.to_markdown(index=False, floatfmt='.3f')}

## Decision

`{result["decision"]}`. The endpoint gate requires at least
`{cfg["minimum_endpoint_authors"]}` fixed-hash endpoint authors and at least
`{cfg["minimum_condition_coverage"]:.0%}` pair-level condition coverage at
Jaccard `>= {cfg["condition_jaccard_threshold"]:.2f}`. A `STOP` result forbids
endpoint fitting, estimator relaxation, or window fishing in this stage. It
means only that current PANDORA does not support this registered design.

## Artifacts

- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility_detail.csv`
- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility_summary.csv`
- `results/v6_dynamic_path_stage_v1/dynamic_path_feasibility.json`
""")
    print(summary.to_string(index=False))
    print(f"decision={result['decision']}")
    print(f"report={args.report}")


if __name__ == "__main__":
    main()
