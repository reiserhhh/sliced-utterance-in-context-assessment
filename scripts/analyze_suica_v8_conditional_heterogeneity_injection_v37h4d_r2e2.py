#!/usr/bin/env python3
"""Analyze the fresh H4D-R2E.2 endpoint confirmation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import (  # noqa: E402
    run_suica_v8_conditional_heterogeneity_injection_v37h4d_r2e as r2e,
)
from scripts.run_suica_v8_reference_measure_frontier_v37h4d import (  # noqa: E402
    _read,
    _write,
)
from suica_core.v7_governance import (  # noqa: E402
    verify_artifact_inventory,
    verify_run_manifest,
    write_artifact_inventory,
    write_run_manifest,
)


DEFAULT_CONFIG = (
    ROOT
    / "configs"
    / "v8_conditional_heterogeneity_injection_v37h4d_r2e2.json"
)
DEFAULT_INPUT = (
    ROOT
    / "results"
    / "v8_conditional_heterogeneity_injection"
    / "v37h4d_r2e2_fresh_endpoint_confirmation"
)
DEFAULT_PREFLIGHT = (
    ROOT
    / "results"
    / "v8_conditional_heterogeneity_injection"
    / "v37h4d_r2e2_geometry_preflight"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results"
    / "v8_conditional_heterogeneity_injection"
    / "v37h4d_r2e2_confirmation_analysis"
)


def _bootstrap_endpoint_data(
    outcomes: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, np.ndarray]]:
    records = []
    bootstrap: dict[str, np.ndarray] = {}
    streams = np.random.SeedSequence(
        int(config["analysis_seed"])
    ).spawn(len(config["noise_modes"]))
    normal_magnitude = float(config["normal_tau_grid"][0])
    tangent_magnitude = float(config["tangent_phi_grid"][0])
    for stream, noise in zip(
        streams,
        map(str, config["noise_modes"]),
        strict=True,
    ):
        baseline, parents = r2e._outcome_matrix(
            outcomes,
            noise_mode=noise,
            arm="baseline",
            magnitude=0.0,
            sign=0,
        )
        indices = r2e._bootstrap_indices(
            seed=int(stream.generate_state(1, dtype=np.uint64)[0]),
            draws=int(config["bootstrap_draws"]),
            parents=len(parents),
        )
        baseline_bootstrap = r2e._bootstrap_baseline_variance(
            baseline,
            indices,
        )
        baseline_point = r2e._baseline_variance(baseline)
        for arm, magnitude in [
            ("normal", normal_magnitude),
            ("tangent", tangent_magnitude),
        ]:
            plus, plus_parents = r2e._outcome_matrix(
                outcomes,
                noise_mode=noise,
                arm=arm,
                magnitude=magnitude,
                sign=1,
            )
            minus, minus_parents = r2e._outcome_matrix(
                outcomes,
                noise_mode=noise,
                arm=arm,
                magnitude=magnitude,
                sign=-1,
            )
            if parents != plus_parents or parents != minus_parents:
                raise ValueError("fresh confirmation pairing mismatch")
            point = r2e._paired_total_variance(plus, minus)
            j_bootstrap, delta_bootstrap = (
                r2e._bootstrap_paired_statistics(
                    plus,
                    minus,
                    baseline_bootstrap,
                    indices,
                )
            )
            j_name = f"j|{arm}|{noise}"
            delta_name = f"delta_v|{arm}|{noise}"
            bootstrap[j_name] = j_bootstrap
            bootstrap[delta_name] = delta_bootstrap
            records.extend([
                {
                    "endpoint": j_name,
                    "noise_mode": noise,
                    "arm": arm,
                    "metric": "direction_sensitivity_j",
                    "point": point["direction_sensitivity_j"],
                    "baseline_variance": baseline_point,
                    "plus_minus_rate_gap": point[
                        "plus_minus_rate_gap"
                    ],
                },
                {
                    "endpoint": delta_name,
                    "noise_mode": noise,
                    "arm": arm,
                    "metric": "delta_variance",
                    "point": (
                        point["total_side_variance"]
                        - baseline_point
                    ),
                    "baseline_variance": baseline_point,
                    "plus_minus_rate_gap": point[
                        "plus_minus_rate_gap"
                    ],
                },
            ])
    pooled_name = "delta_v|tangent|pooled"
    bootstrap[pooled_name] = np.mean([
        bootstrap[f"delta_v|tangent|{noise}"]
        for noise in map(str, config["noise_modes"])
    ], axis=0)
    tangent_points = [
        record["point"]
        for record in records
        if record["arm"] == "tangent"
        and record["metric"] == "delta_variance"
    ]
    records.append({
        "endpoint": pooled_name,
        "noise_mode": "pooled",
        "arm": "tangent",
        "metric": "delta_variance",
        "point": float(np.mean(tangent_points)),
        "baseline_variance": float("nan"),
        "plus_minus_rate_gap": float("nan"),
    })
    return pd.DataFrame(records), bootstrap


def _confirmation_intervals(
    endpoints: pd.DataFrame,
    bootstrap: dict[str, np.ndarray],
    *,
    config: dict[str, Any],
) -> pd.DataFrame:
    normal_names = [
        f"j|normal|{noise}"
        for noise in map(str, config["noise_modes"])
    ]
    tangent_names = [
        *[
            f"j|tangent|{noise}"
            for noise in map(str, config["noise_modes"])
        ],
        *[
            f"delta_v|tangent|{noise}"
            for noise in map(str, config["noise_modes"])
        ],
        "delta_v|tangent|pooled",
    ]
    normal_alpha = float(
        config["confirmation"]["normal_family_alpha"]
    ) / len(normal_names)
    tangent_alpha = float(
        config["confirmation"]["tangent_family_alpha"]
    ) / len(tangent_names)
    rows = endpoints.copy()
    rows["family"] = "support"
    rows["one_sided_alpha"] = np.nan
    rows["bonferroni_lower"] = np.nan
    rows["bonferroni_upper"] = np.nan
    for index, record in rows.iterrows():
        name = str(record["endpoint"])
        values = bootstrap[name]
        if name in normal_names:
            rows.loc[index, "family"] = "normal_positive_control"
            rows.loc[index, "one_sided_alpha"] = normal_alpha
            rows.loc[index, "bonferroni_lower"] = float(
                np.quantile(values, normal_alpha)
            )
            rows.loc[index, "bonferroni_upper"] = float(
                np.quantile(values, 1.0 - normal_alpha)
            )
        elif name in tangent_names:
            rows.loc[index, "family"] = "tangent_practical_null"
            rows.loc[index, "one_sided_alpha"] = tangent_alpha
            rows.loc[index, "bonferroni_lower"] = float(
                np.quantile(values, tangent_alpha)
            )
            rows.loc[index, "bonferroni_upper"] = float(
                np.quantile(values, 1.0 - tangent_alpha)
            )

    tangent_points = rows[
        rows["endpoint"].isin(tangent_names)
    ].set_index("endpoint")["point"].reindex(tangent_names).to_numpy()
    tangent_bootstrap = np.column_stack([
        bootstrap[name] for name in tangent_names
    ])
    standard_error = tangent_bootstrap.std(axis=0, ddof=1)
    standardized = (
        tangent_bootstrap - tangent_points[None, :]
    ) / np.maximum(standard_error[None, :], 1e-12)
    max_t = np.max(standardized, axis=1)
    critical = float(np.quantile(
        max_t,
        1.0 - float(
            config["confirmation"]["tangent_family_alpha"]
        ),
    ))
    max_t_upper = tangent_points + critical * standard_error
    for name, upper in zip(tangent_names, max_t_upper, strict=True):
        rows.loc[
            rows["endpoint"] == name,
            "studentized_max_t_upper",
        ] = float(upper)
    rows["studentized_max_t_upper"] = rows[
        "studentized_max_t_upper"
    ].astype(float)
    return rows


def _decision(
    intervals: pd.DataFrame,
    *,
    config: dict[str, Any],
    integrity: dict[str, bool],
) -> tuple[str, dict[str, bool]]:
    threshold = float(
        config["gates"]["practical_variance_threshold"]
    )
    normal = intervals[
        intervals["family"] == "normal_positive_control"
    ]
    tangent = intervals[
        intervals["family"] == "tangent_practical_null"
    ]
    normal_pass = bool(
        (normal["bonferroni_lower"] > threshold).all()
    )
    tangent_excluded = bool(
        (tangent["bonferroni_upper"] <= threshold).all()
    )
    tangent_superior = bool(
        (tangent["bonferroni_lower"] > threshold).all()
    )
    sensitivity_agrees = bool(
        (
            tangent["studentized_max_t_upper"]
            <= threshold
        ).all()
    )
    checks = {
        "normal_positive_control_confirmed": normal_pass,
        "tangent_practical_effect_excluded": tangent_excluded,
        "tangent_practical_effect_confirmed": tangent_superior,
        "studentized_max_t_sensitivity_agrees": sensitivity_agrees,
    }
    if not all(integrity.values()):
        status = "V8_R2E2_STOP_INVALID_CONFIRMATION"
    elif normal_pass and tangent_excluded:
        status = "V8_R2E2_CONFIRMED_NORMAL_ONLY"
    elif normal_pass and tangent_superior:
        status = "V8_R2E2_REFUTED_NORMAL_ONLY_TANGENT_CHANNEL"
    elif not normal_pass:
        status = "V8_R2E2_STOP_POSITIVE_CONTROL_NOT_CONFIRMED"
    else:
        status = "V8_R2E2_INCONCLUSIVE_CONFIRMATION"
    return status, checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument(
        "--preflight-dir",
        type=Path,
        default=DEFAULT_PREFLIGHT,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read(args.config)
    outcomes_path = args.input_dir / "outcome_rows.csv"
    geometry_path = args.input_dir / "geometry_rows.csv"
    run_decision_path = args.input_dir / "decision.json"
    preflight_decision_path = args.preflight_dir / "decision.json"
    outcomes = pd.read_csv(outcomes_path)
    geometry = pd.read_csv(geometry_path)
    run_decision = _read(run_decision_path)
    preflight_decision = _read(preflight_decision_path)
    endpoints, bootstrap = _bootstrap_endpoint_data(
        outcomes,
        config=config,
    )
    intervals = _confirmation_intervals(
        endpoints,
        bootstrap,
        config=config,
    )
    input_manifest = verify_run_manifest(
        args.input_dir / "run_manifest.json"
    )
    input_inventory = verify_artifact_inventory(
        args.input_dir / "artifact_inventory.json"
    )
    preflight_manifest = verify_run_manifest(
        args.preflight_dir / "run_manifest.json"
    )
    preflight_inventory = verify_artifact_inventory(
        args.preflight_dir / "artifact_inventory.json"
    )
    expected_parents = (
        len(config["noise_modes"]) * int(config["parents_per_noise"])
    )
    expected_geometries = expected_parents * 5
    expected_outcomes = (
        expected_geometries * int(config["outcome_replicates"])
    )
    integrity = {
        "input_run_integrity": bool(
            all(run_decision["integrity_checks"].values())
        ),
        "preflight_pass": bool(
            preflight_decision["status"]
            == "V8_R2E1_GEOMETRY_PREFLIGHT_PASS"
            and all(
                preflight_decision["integrity_checks"].values()
            )
        ),
        "input_manifest": bool(
            input_manifest["status"] == "RUN_MANIFEST_PASS"
        ),
        "input_inventory": bool(
            input_inventory["status"] == "INVENTORY_PASS"
        ),
        "preflight_manifest": bool(
            preflight_manifest["status"] == "RUN_MANIFEST_PASS"
        ),
        "preflight_inventory": bool(
            preflight_inventory["status"] == "INVENTORY_PASS"
        ),
        "row_counts": bool(
            geometry["parent_id"].nunique() == expected_parents
            and len(geometry) == expected_geometries
            and len(outcomes) == expected_outcomes
        ),
        "fresh_endpoint_only": bool(
            set(geometry["arm"]) == {"baseline", "normal", "tangent"}
            and len(geometry["geometry_id"].unique()) == 5
            and set(
                geometry.loc[
                    geometry["arm"] == "normal",
                    "magnitude",
                ]
            ) == {float(config["normal_tau_grid"][0])}
            and set(
                geometry.loc[
                    geometry["arm"] == "tangent",
                    "magnitude",
                ]
            ) == {float(config["tangent_phi_grid"][0])}
        ),
    }
    status, checks = _decision(
        intervals,
        config=config,
        integrity=integrity,
    )
    decision = {
        "status": status,
        "integrity_checks": integrity,
        "gate_checks": checks,
        "practical_variance_threshold": float(
            config["gates"]["practical_variance_threshold"]
        ),
        "normal_family_endpoint_alpha": float(
            config["confirmation"]["normal_family_alpha"]
            / 2.0
        ),
        "tangent_family_endpoint_alpha": float(
            config["confirmation"]["tangent_family_alpha"]
            / 5.0
        ),
        "endpoints": intervals.to_dict(orient="records"),
        "claim_boundary": str(config["claim_boundary"]),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    intervals.to_csv(
        args.output_dir / "confirmation_endpoints.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        "# H4D-R2E.2 Fresh Endpoint Confirmation\n\n"
        f"Decision: `{status}`\n\n"
        "Normal and tangent endpoints use prospectively separated "
        "Bonferroni families. Studentized max-t is sensitivity only.\n",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            outcomes_path,
            geometry_path,
            run_decision_path,
            preflight_decision_path,
        ],
        config_path=args.config,
        code_paths=[Path(__file__)],
        estimand_id=str(config["analysis_estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps({
        "status": status,
        "integrity_checks": integrity,
        "gate_checks": checks,
        "endpoints": intervals.to_dict(orient="records"),
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
