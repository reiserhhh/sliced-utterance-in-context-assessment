#!/usr/bin/env python3
"""Run the R2G.2 hierarchical society-limit frontier."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import t


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_hierarchical_society_limit import (  # noqa: E402
    HierarchicalSocietySpec,
    correlated_hierarchy_truth,
    cross_view_surface,
    fit_ar1_surface,
    fit_independent_surface,
    fit_local_to_unity_surface,
    hierarchy_cross_level_covariances,
    local_to_unity_limit,
    residual_arms,
    simulate_hierarchical_panel,
    simulate_local_to_unity_surface,
    test_centered_full_mean_energy,
)


DEFAULT_CONFIG = (
    ROOT
    / "configs/v8_hierarchical_society_limit_v37h4d_r2g2.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results/v8_hierarchical_society_limit"
    / "v37h4d_r2g2_confirmation"
)


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def _uint64(sequence: np.random.SeedSequence) -> int:
    return int(sequence.generate_state(1, dtype=np.uint64)[0])


def _spec(config: dict[str, Any]) -> HierarchicalSocietySpec:
    values = config["spec"]
    return HierarchicalSocietySpec(
        societies=int(values["societies"]),
        max_groups=int(values["max_groups"]),
        max_authors=int(values["max_authors"]),
        dimensions=int(values["dimensions"]),
        society_energy=float(values["society_energy"]),
        group_energy=float(values["group_energy"]),
        author_energy=float(values["author_energy"]),
        technical_energy=float(values["technical_energy"]),
        private_noise_energy=float(values["private_noise_energy"]),
        score_noise_energy=float(values["score_noise_energy"]),
        score_opportunities=int(values["score_opportunities"]),
        raw_society_loading=float(values["raw_society_loading"]),
        raw_group_loading=float(values["raw_group_loading"]),
        local_to_unity_c=float(values["local_to_unity_c"]),
        student_df=float(values["student_df"]),
    )


def _cell_id(cell: dict[str, Any]) -> str:
    world = str(cell["world"])
    if "rho" in cell:
        suffix = str(float(cell["rho"])).replace("-", "m").replace(".", "p")
        return f"{world}_rho_{suffix}"
    return world


def _flatten_fit(
    fitted: dict[str, Any],
    *,
    root_index: int,
    cell_id: str,
    world: str,
    noise_mode: str,
    arm: str,
) -> dict[str, Any]:
    return {
        "root_index": int(root_index),
        "cell_id": cell_id,
        "world": world,
        "noise_mode": noise_mode,
        "arm": arm,
        "model": str(fitted["model"]),
        "society": float(fitted.get("society", np.nan)),
        "group": float(fitted.get("group", np.nan)),
        "author": float(fitted.get("author", np.nan)),
        "rho": float(fitted.get("rho", np.nan)),
        "test_rmse": float(fitted["test"]["rmse"]),
        "test_nrmse": float(fitted["test"]["nrmse"]),
        "test_max_abs_error": float(
            fitted["test"]["max_abs_error"]
        ),
        "test_normalized_max_error": float(
            fitted["test"]["normalized_max_error"]
        ),
    }


def _worker(
    payload: tuple[
        dict[str, Any],
        int,
        int,
        dict[str, Any],
        str,
    ],
) -> dict[str, Any]:
    config, root_index, seed, cell, noise_mode = payload
    spec = _spec(config)
    world = str(cell["world"])
    cell_id = _cell_id(cell)
    surface_rows: list[dict[str, Any]] = []
    fit_rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    if world == "local_to_unity":
        rows = simulate_local_to_unity_surface(
            seed=seed,
            spec=spec,
            noise_mode=noise_mode,
            group_sizes=config["group_sizes"],
            author_sizes=config["author_sizes"],
        )
        for row in rows:
            surface_rows.append({
                "root_index": root_index,
                "cell_id": cell_id,
                "world": world,
                "noise_mode": noise_mode,
                "arm": "raw",
                **row,
            })
        naive = fit_independent_surface(rows)
        correct = fit_local_to_unity_surface(
            rows,
            c=float(spec.local_to_unity_c),
        )
        fit_rows.extend([
            _flatten_fit(
                naive,
                root_index=root_index,
                cell_id=cell_id,
                world=world,
                noise_mode=noise_mode,
                arm="raw",
            ),
            _flatten_fit(
                correct,
                root_index=root_index,
                cell_id=cell_id,
                world=world,
                noise_mode=noise_mode,
                arm="raw",
            ),
        ])
        diagnostics.append({
            "root_index": root_index,
            "cell_id": cell_id,
            "world": world,
            "noise_mode": noise_mode,
            "diagnostic": "local_to_unity_limit",
            "value": local_to_unity_limit(
                float(spec.local_to_unity_c)
            ),
        })
        return {
            "surface_rows": surface_rows,
            "fit_rows": fit_rows,
            "diagnostics": diagnostics,
            "source_seeds": [int(seed)],
        }

    group_rho = float(cell.get("rho", 0.0))
    panel = simulate_hierarchical_panel(
        seed=seed,
        world=world,
        spec=spec,
        noise_mode=noise_mode,
        group_rho=group_rho,
    )
    for arm, values in residual_arms(panel).items():
        rows = cross_view_surface(
            *values,
            group_sizes=config["group_sizes"],
            author_sizes=config["author_sizes"],
        )
        for row in rows:
            surface_rows.append({
                "root_index": root_index,
                "cell_id": cell_id,
                "world": world,
                "noise_mode": noise_mode,
                "arm": arm,
                **row,
            })
        fit_rows.append(_flatten_fit(
            fit_independent_surface(rows),
            root_index=root_index,
            cell_id=cell_id,
            world=world,
            noise_mode=noise_mode,
            arm=arm,
        ))
        if world == "group_ar1" and arm == "raw":
            fit_rows.append(_flatten_fit(
                fit_ar1_surface(rows),
                root_index=root_index,
                cell_id=cell_id,
                world=world,
                noise_mode=noise_mode,
                arm=arm,
            ))

    if world == "correlated_hierarchy":
        for label, components in (
            ("raw", panel["raw_components"]),
            ("martingale", panel["martingale_components"]),
        ):
            values = hierarchy_cross_level_covariances(components)
            for name, value in values.items():
                diagnostics.append({
                    "root_index": root_index,
                    "cell_id": cell_id,
                    "world": world,
                    "noise_mode": noise_mode,
                    "diagnostic": (
                        f"{label}_cross_level_{name}"
                    ),
                    "value": float(value),
                })
        truth = correlated_hierarchy_truth(spec)
        for name, value in truth.items():
            diagnostics.append({
                "root_index": root_index,
                "cell_id": cell_id,
                "world": world,
                "noise_mode": noise_mode,
                "diagnostic": f"truth_{name}",
                "value": float(value),
            })

    if world == "unavailable_society_shock":
        values = test_centered_full_mean_energy(
            panel["target_a"],
            panel["target_b"],
        )
        for name, value in values.items():
            diagnostics.append({
                "root_index": root_index,
                "cell_id": cell_id,
                "world": world,
                "noise_mode": noise_mode,
                "diagnostic": f"centering_attack_{name}",
                "value": float(value),
            })

    return {
        "surface_rows": surface_rows,
        "fit_rows": fit_rows,
        "diagnostics": diagnostics,
        "source_seeds": [int(seed)],
    }


def _simultaneous_summary(
    frame: pd.DataFrame,
    *,
    group_columns: list[str],
    value_columns: list[str],
    alpha: float,
    family_size: int,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for keys, group in frame.groupby(
        group_columns,
        sort=True,
        observed=True,
        dropna=False,
    ):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_columns, keys, strict=True))
        row["repetitions"] = int(group["root_index"].nunique())
        for column in value_columns:
            values = group[column].to_numpy(dtype=float)
            values = values[np.isfinite(values)]
            if not len(values):
                row[f"{column}_mean"] = np.nan
                row[f"{column}_se"] = np.nan
                row[f"{column}_ci_lo"] = np.nan
                row[f"{column}_ci_hi"] = np.nan
                continue
            mean = float(np.mean(values))
            if len(values) == 1:
                se = 0.0
                critical = 0.0
            else:
                se = float(np.std(values, ddof=1) / np.sqrt(len(values)))
                critical = float(t.ppf(
                    1.0 - alpha / (2.0 * family_size),
                    df=len(values) - 1,
                ))
            row[f"{column}_mean"] = mean
            row[f"{column}_se"] = se
            row[f"{column}_ci_lo"] = mean - critical * se
            row[f"{column}_ci_hi"] = mean + critical * se
        rows.append(row)
    return pd.DataFrame(rows)


def _lookup(
    summary: pd.DataFrame,
    *,
    cell_id: str,
    noise_mode: str,
    arm: str,
    model: str,
    metric: str,
    statistic: str,
) -> float:
    match = summary[
        (summary["cell_id"] == cell_id)
        & (summary["noise_mode"] == noise_mode)
        & (summary["arm"] == arm)
        & (summary["model"] == model)
    ]
    if len(match) != 1:
        return float("nan")
    return float(match.iloc[0][f"{metric}_{statistic}"])


def _diagnostic_lookup(
    summary: pd.DataFrame,
    *,
    noise_mode: str,
    diagnostic: str,
    statistic: str = "mean",
) -> float:
    match = summary[
        (summary["noise_mode"] == noise_mode)
        & (summary["diagnostic"] == diagnostic)
    ]
    if len(match) != 1:
        return float("nan")
    return float(match.iloc[0][f"value_{statistic}"])


def _inside(value_lo: float, value_hi: float, tolerance: float) -> bool:
    return bool(value_lo >= -tolerance and value_hi <= tolerance)


def _decision(
    config: dict[str, Any],
    fit_summary: pd.DataFrame,
    diagnostic_summary: pd.DataFrame,
    *,
    seed_count: int,
    unique_seed_count: int,
) -> dict[str, Any]:
    gates = config["gates"]
    zero = float(gates["practical_zero"])
    coefficient_error = float(gates["coefficient_absolute_error"])
    positive = float(gates["minimum_positive_floor"])
    rho_error = float(gates["maximum_rho_error"])
    centered_max = float(gates["maximum_centered_cross_level"])
    raw_min = float(gates["minimum_raw_cross_level"])
    local_nrmse = float(gates["maximum_local_model_nrmse"])
    spec = _spec(config)
    correlated_truth = correlated_hierarchy_truth(spec)
    checks_by_noise: dict[str, dict[str, bool]] = {}

    def value(
        noise: str,
        cell: str,
        arm: str,
        model: str,
        metric: str,
        statistic: str,
    ) -> float:
        return _lookup(
            fit_summary,
            cell_id=cell,
            noise_mode=noise,
            arm=arm,
            model=model,
            metric=metric,
            statistic=statistic,
        )

    for noise in map(str, config["noise_modes"]):
        null_zero = all(
            _inside(
                value(
                    noise,
                    "pure_iid",
                    "raw",
                    "independent_hierarchy",
                    metric,
                    "ci_lo",
                ),
                value(
                    noise,
                    "pure_iid",
                    "raw",
                    "independent_hierarchy",
                    metric,
                    "ci_hi",
                ),
                zero,
            )
            for metric in ("society", "group", "author")
        )
        author_recovery = all([
            abs(value(
                noise,
                "author_iid",
                "raw",
                "independent_hierarchy",
                "society",
                "mean",
            )) <= coefficient_error,
            abs(value(
                noise,
                "author_iid",
                "raw",
                "independent_hierarchy",
                "group",
                "mean",
            )) <= coefficient_error,
            abs(
                value(
                    noise,
                    "author_iid",
                    "raw",
                    "independent_hierarchy",
                    "author",
                    "mean",
                )
                - float(spec.author_energy)
            ) <= coefficient_error,
        ])
        group_recovery = all([
            abs(value(
                noise,
                "group_iid",
                "raw",
                "independent_hierarchy",
                "society",
                "mean",
            )) <= coefficient_error,
            abs(
                value(
                    noise,
                    "group_iid",
                    "raw",
                    "independent_hierarchy",
                    "group",
                    "mean",
                )
                - float(spec.group_energy)
            ) <= coefficient_error,
            abs(
                value(
                    noise,
                    "group_iid",
                    "raw",
                    "independent_hierarchy",
                    "author",
                    "mean",
                )
                - float(spec.author_energy)
            ) <= coefficient_error,
        ])
        visible_raw = value(
            noise,
            "society_completable",
            "raw",
            "independent_hierarchy",
            "society",
            "ci_lo",
        ) > positive
        visible_admissible = _inside(
            value(
                noise,
                "society_completable",
                "admissible",
                "independent_hierarchy",
                "society",
                "ci_lo",
            ),
            value(
                noise,
                "society_completable",
                "admissible",
                "independent_hierarchy",
                "society",
                "ci_hi",
            ),
            zero,
        )
        ar_checks = []
        for rho in (0.5, 0.9):
            cell = f"group_ar1_rho_{str(rho).replace('.', 'p')}"
            ar_checks.append(
                abs(
                    value(
                        noise,
                        cell,
                        "raw",
                        "ar1_hierarchy",
                        "rho",
                        "mean",
                    )
                    - rho
                ) <= rho_error
                and value(
                    noise,
                    cell,
                    "raw",
                    "ar1_hierarchy",
                    "test_nrmse",
                    "mean",
                ) <= local_nrmse
            )
        raw_cross = _diagnostic_lookup(
            diagnostic_summary,
            noise_mode=noise,
            diagnostic="raw_cross_level_maximum_absolute",
            statistic="ci_lo",
        )
        centered_cross = _diagnostic_lookup(
            diagnostic_summary,
            noise_mode=noise,
            diagnostic="martingale_cross_level_maximum_absolute",
            statistic="ci_hi",
        )
        correlated_recovery = all(
            abs(
                value(
                    noise,
                    "correlated_hierarchy",
                    "raw",
                    "independent_hierarchy",
                    metric,
                    "mean",
                )
                - correlated_truth[f"martingale_{metric}"]
            ) <= coefficient_error
            for metric in ("society", "group", "author")
        )
        unavailable_persists = value(
            noise,
            "unavailable_society_shock",
            "admissible",
            "independent_hierarchy",
            "society",
            "ci_lo",
        ) > positive
        unavailable_oracle_zero = _inside(
            value(
                noise,
                "unavailable_society_shock",
                "structural_oracle",
                "independent_hierarchy",
                "society",
                "ci_lo",
            ),
            value(
                noise,
                "unavailable_society_shock",
                "structural_oracle",
                "independent_hierarchy",
                "society",
                "ci_hi",
            ),
            zero,
        )
        local_false_floor = value(
            noise,
            "local_to_unity",
            "raw",
            "independent_hierarchy",
            "society",
            "ci_lo",
        ) > positive
        local_corrected = (
            _inside(
                value(
                    noise,
                    "local_to_unity",
                    "raw",
                    "local_to_unity_known_c",
                    "society",
                    "ci_lo",
                ),
                value(
                    noise,
                    "local_to_unity",
                    "raw",
                    "local_to_unity_known_c",
                    "society",
                    "ci_hi",
                ),
                zero,
            )
            and value(
                noise,
                "local_to_unity",
                "raw",
                "local_to_unity_known_c",
                "test_nrmse",
                "mean",
            ) <= local_nrmse
        )
        technical_persists = value(
            noise,
            "correlated_view_noise",
            "structural_oracle",
            "independent_hierarchy",
            "society",
            "ci_lo",
        ) > positive
        technical_omniscient_zero = _inside(
            value(
                noise,
                "correlated_view_noise",
                "omniscient_oracle",
                "independent_hierarchy",
                "society",
                "ci_lo",
            ),
            value(
                noise,
                "correlated_view_noise",
                "omniscient_oracle",
                "independent_hierarchy",
                "society",
                "ci_hi",
            ),
            zero,
        )
        leaky_zero = abs(_diagnostic_lookup(
            diagnostic_summary,
            noise_mode=noise,
            diagnostic=(
                "centering_attack_"
                "leaky_test_centered_cross_energy"
            ),
            statistic="mean",
        )) <= 1e-12
        leaky_raw_positive = _diagnostic_lookup(
            diagnostic_summary,
            noise_mode=noise,
            diagnostic="centering_attack_raw_cross_energy",
            statistic="ci_lo",
        ) > positive
        checks_by_noise[noise] = {
            "pure_iid_practical_zero": null_zero,
            "author_scaling_recovered": author_recovery,
            "group_scaling_recovered": group_recovery,
            "score_visible_society_removed": (
                visible_raw and visible_admissible
            ),
            "ar1_covariance_sum_recovered": all(ar_checks),
            "conditional_projection_recovered": (
                raw_cross > raw_min
                and centered_cross <= centered_max
                and correlated_recovery
            ),
            "unavailable_society_persists": (
                unavailable_persists and unavailable_oracle_zero
            ),
            "local_to_unity_not_society": (
                local_false_floor and local_corrected
            ),
            "technical_common_nonidentifiability_detected": (
                technical_persists and technical_omniscient_zero
            ),
            "test_centering_false_zero_detected": (
                leaky_zero and leaky_raw_positive
            ),
        }

    all_checks = [
        result
        for checks in checks_by_noise.values()
        for result in checks.values()
    ]
    if all(all_checks):
        status = "V8_R2G2_PASS_HIERARCHICAL_LIMIT_IDENTIFICATION"
    elif all(
        checks["pure_iid_practical_zero"]
        and checks["author_scaling_recovered"]
        and checks["group_scaling_recovered"]
        for checks in checks_by_noise.values()
    ):
        status = "V8_R2G2_PARTIAL_INDEPENDENT_ONLY"
    else:
        status = "V8_R2G2_STOP_CORE_IDENTIFICATION_FAILURE"
    numeric_values = fit_summary.select_dtypes(
        include=[np.number]
    ).to_numpy()
    observed_numeric = numeric_values[~np.isnan(numeric_values)]
    return {
        "status": status,
        "scientific_decision": (
            "SYNTHETIC_HIERARCHICAL_IDENTIFICATION"
            if status == "V8_R2G2_PASS_HIERARCHICAL_LIMIT_IDENTIFICATION"
            else "BOUNDED_OR_FAILED_HIERARCHICAL_IDENTIFICATION"
        ),
        "checks_by_noise": checks_by_noise,
        "checks": {
            "numeric_integrity": bool(
                np.isfinite(observed_numeric).all()
            ),
            "seed_uniqueness": seed_count == unique_seed_count,
            "all_registered_gates": all(all_checks),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--jobs", type=int)
    args = parser.parse_args()
    config = _read(args.config)
    if args.repetitions is not None:
        config["repetitions"] = int(args.repetitions)
    if args.jobs is not None:
        config["jobs"] = int(args.jobs)

    cells = [
        (dict(cell), str(noise))
        for cell in config["cells"]
        for noise in config["noise_modes"]
    ]
    root = np.random.SeedSequence(int(config["seed"]))
    children = root.spawn(int(config["repetitions"]) * len(cells))
    payloads = []
    for repetition in range(int(config["repetitions"])):
        for index, (cell, noise) in enumerate(cells):
            payloads.append((
                config,
                repetition,
                _uint64(children[repetition * len(cells) + index]),
                cell,
                noise,
            ))
    if int(config["jobs"]) == 1:
        parts = [_worker(payload) for payload in payloads]
    else:
        with ProcessPoolExecutor(
            max_workers=int(config["jobs"]),
        ) as executor:
            parts = list(executor.map(_worker, payloads, chunksize=1))

    surface_rows: list[dict[str, Any]] = []
    fit_rows: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    source_seeds: list[int] = []
    for part in parts:
        surface_rows.extend(part["surface_rows"])
        fit_rows.extend(part["fit_rows"])
        diagnostics.extend(part["diagnostics"])
        source_seeds.extend(part["source_seeds"])
    surface = pd.DataFrame(surface_rows)
    fits = pd.DataFrame(fit_rows)
    diagnostic = pd.DataFrame(diagnostics)

    alpha = float(config["gates"]["simultaneous_alpha"])
    family_size = int(config["gates"]["primary_endpoint_count"])
    fit_summary = _simultaneous_summary(
        fits,
        group_columns=[
            "cell_id",
            "world",
            "noise_mode",
            "arm",
            "model",
        ],
        value_columns=[
            "society",
            "group",
            "author",
            "rho",
            "test_rmse",
            "test_nrmse",
            "test_max_abs_error",
            "test_normalized_max_error",
        ],
        alpha=alpha,
        family_size=family_size,
    )
    diagnostic_summary = _simultaneous_summary(
        diagnostic,
        group_columns=[
            "cell_id",
            "world",
            "noise_mode",
            "diagnostic",
        ],
        value_columns=["value"],
        alpha=alpha,
        family_size=family_size,
    )
    surface_summary = _simultaneous_summary(
        surface,
        group_columns=[
            "cell_id",
            "world",
            "noise_mode",
            "arm",
            "groups",
            "authors",
        ],
        value_columns=[
            "cross_energy",
            "self_energy",
        ],
        alpha=alpha,
        family_size=family_size,
    )
    decision = _decision(
        config,
        fit_summary,
        diagnostic_summary,
        seed_count=len(source_seeds),
        unique_seed_count=len(set(source_seeds)),
    )
    decision.update({
        "created_utc": datetime.now(UTC).isoformat(),
        "root_seed": int(config["seed"]),
        "repetitions": int(config["repetitions"]),
        "metric_rows": int(len(surface)),
        "fit_rows": int(len(fits)),
        "diagnostic_rows": int(len(diagnostic)),
        "source_seed_count": len(source_seeds),
        "unique_source_seed_count": len(set(source_seeds)),
        "claim_boundary": str(config["claim_boundary"]),
    })

    args.output_dir.mkdir(parents=True, exist_ok=True)
    surface.to_csv(args.output_dir / "surface_metrics.csv", index=False)
    surface_summary.to_csv(
        args.output_dir / "surface_summary.csv",
        index=False,
    )
    fits.to_csv(args.output_dir / "surface_fits.csv", index=False)
    fit_summary.to_csv(
        args.output_dir / "surface_fit_summary.csv",
        index=False,
    )
    diagnostic.to_csv(
        args.output_dir / "hierarchy_diagnostics.csv",
        index=False,
    )
    diagnostic_summary.to_csv(
        args.output_dir / "hierarchy_diagnostic_summary.csv",
        index=False,
    )
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    _write(args.output_dir / "seed_audit.json", {
        "root_seed": int(config["seed"]),
        "source_seed_count": len(source_seeds),
        "unique_source_seed_count": len(set(source_seeds)),
        "all_source_seeds_unique": (
            len(source_seeds) == len(set(source_seeds))
        ),
        "nested_prefixes_within_fixed_panel": True,
        "local_to_unity_is_registered_triangular_array": True,
    })
    _write(args.output_dir / "formula_contract.json", {
        "independent": (
            "M_x(G,n)=b_society+b_group/G+b_author/(G*n)"
        ),
        "general": (
            "M_x(G,n)=(G^2*n^2)^-1 sum_{g,h,i,j} "
            "Gamma_AB((g,i),(h,j))"
        ),
        "ar1": (
            "M_x(G,n)=b_society+b_group*[G+2*sum_{h=1}^{G-1}"
            "(G-h)rho^h]/G^2+b_author/(G*n)"
        ),
        "local_to_unity_limit": (
            "2*(c-1+exp(-c))/c^2"
        ),
        "conditional_projection": (
            "D_L=E[R|F_L]-E[R|F_{L-1}]"
        ),
        "claim_boundary": str(config["claim_boundary"]),
    })
    (args.output_dir / "report.md").write_text(
        f"""# V8 R2G.2 Hierarchical Society-Limit Frontier

Decision: `{decision["status"]}`

Scientific decision: `{decision["scientific_decision"]}`

```json
{json.dumps(decision["checks"], ensure_ascii=False, indent=2)}
```

The experiment distinguishes finite author, group, and society aggregation
terms. It also registers cases where dependence or shared technical noise
makes a positive limit non-psychological or non-identifiable.
""",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v8_hierarchical_society_limit.py",
            Path(__file__),
        ],
        estimand_id=str(config["estimand_id"]),
        external_labels_read=False,
        raw_identifiers_persisted=False,
    )
    write_artifact_inventory(
        args.output_dir,
        args.output_dir / "artifact_inventory.json",
    )
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
