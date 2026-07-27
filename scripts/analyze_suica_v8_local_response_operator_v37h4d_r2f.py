#!/usr/bin/env python3
"""Analyze the H4D-R2F constrained local-response discovery."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
from suica_core.v8_local_response_operator import (  # noqa: E402
    cross_fitted_response_operators,
    ordered_eigensystem,
    richardson_gradient_hessian,
)


DEFAULT_CONFIG = (
    ROOT / "configs/v8_local_response_operator_v37h4d_r2f_discovery.json"
)
DEFAULT_INPUT = (
    ROOT / "results/v8_local_response_operator/r2f_discovery"
)
DEFAULT_PREFLIGHT = (
    ROOT / "results/v8_local_response_operator/r2f_geometry_preflight"
)
DEFAULT_OUTPUT = (
    ROOT / "results/v8_local_response_operator/r2f_discovery_analysis"
)


def _probability_table(
    outcomes: pd.DataFrame,
    *,
    outcome_replicates: int,
) -> pd.DataFrame:
    half_size = int(outcome_replicates) // 2
    if half_size < 2 or int(outcome_replicates) % 2:
        raise ValueError("outcome replicates must split into equal halves")
    rows = outcomes.copy()
    rows["half"] = np.where(
        rows["outcome_replicate"] < half_size,
        "A",
        "B",
    )
    return (
        rows.groupby(
            [
                "parent_id",
                "noise_mode",
                "geometry_id",
                "arm",
                "magnitude",
                "sign",
                "axis_left",
                "axis_right",
                "sign_left",
                "sign_right",
                "half",
            ],
            as_index=False,
        )["crc_or_hc_detected"]
        .mean()
        .rename(columns={"crc_or_hc_detected": "probability"})
    )


def _lookup(
    parent: pd.DataFrame,
    *,
    half: str,
    arm: str,
    magnitude: float | None = None,
    sign: int | None = None,
    axis_left: int | None = None,
    axis_right: int | None = None,
    sign_left: int | None = None,
    sign_right: int | None = None,
) -> float:
    selected = parent[
        (parent["half"] == half)
        & (parent["arm"] == arm)
    ]
    filters = {
        "magnitude": magnitude,
        "sign": sign,
        "axis_left": axis_left,
        "axis_right": axis_right,
        "sign_left": sign_left,
        "sign_right": sign_right,
    }
    for column, value in filters.items():
        if value is None:
            continue
        if column == "magnitude":
            selected = selected[np.isclose(selected[column], float(value))]
        else:
            selected = selected[selected[column] == value]
    if len(selected) != 1:
        raise ValueError(
            f"expected one {arm} row in half {half}, found {len(selected)}"
        )
    return float(selected.iloc[0]["probability"])


def _parent_derivatives(
    probabilities: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> tuple[
    list[str],
    list[str],
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    dimensions = int(config["tangent_dimensions"])
    step = float(config["finite_difference_step"])
    parent_ids: list[str] = []
    noise_modes: list[str] = []
    gradients_a = []
    gradients_b = []
    hessians_a = []
    hessians_b = []
    adequacy = []
    for parent_id, parent in probabilities.groupby("parent_id", sort=True):
        parent_ids.append(str(parent_id))
        noise_modes.append(str(parent.iloc[0]["noise_mode"]))
        derivatives = {}
        errors = {}
        for half in ("A", "B"):
            baseline = _lookup(parent, half=half, arm="baseline")
            axes: dict[tuple[int, float, int], float] = {}
            corners: dict[tuple[int, int, int, int], float] = {}
            for axis in range(dimensions):
                for magnitude in (step, 2.0 * step):
                    for sign in (-1, 1):
                        axes[(axis, magnitude, sign)] = _lookup(
                            parent,
                            half=half,
                            arm="axis",
                            magnitude=magnitude,
                            sign=sign,
                            axis_left=axis,
                        )
            for left in range(dimensions):
                for right in range(left + 1, dimensions):
                    for left_sign in (-1, 1):
                        for right_sign in (-1, 1):
                            corners[(
                                left,
                                right,
                                left_sign,
                                right_sign,
                            )] = _lookup(
                                parent,
                                half=half,
                                arm="corner",
                                axis_left=left,
                                axis_right=right,
                                sign_left=left_sign,
                                sign_right=right_sign,
                            )
            gradient, hessian = richardson_gradient_hessian(
                baseline,
                axes,
                corners,
                dimensions=dimensions,
                step=step,
            )
            derivatives[half] = (gradient, hessian)
            half_errors = []
            for axis in range(dimensions):
                p_plus = axes[(axis, step, 1)]
                p_minus = axes[(axis, step, -1)]
                local_gradient = (p_plus - p_minus) / (2.0 * step)
                local_curvature = (
                    p_plus - 2.0 * baseline + p_minus
                ) / (step**2)
                for sign in (-1, 1):
                    x = sign * 2.0 * step
                    predicted = (
                        baseline
                        + x * local_gradient
                        + 0.5 * x**2 * local_curvature
                    )
                    half_errors.append(
                        axes[(axis, 2.0 * step, sign)] - predicted
                    )
            errors[half] = np.asarray(half_errors)
        gradients_a.append(derivatives["A"][0])
        gradients_b.append(derivatives["B"][0])
        hessians_a.append(derivatives["A"][1])
        hessians_b.append(derivatives["B"][1])
        adequacy.append(float(np.mean(errors["A"] * errors["B"])))
    return (
        parent_ids,
        noise_modes,
        np.stack(gradients_a),
        np.stack(gradients_b),
        np.stack(hessians_a),
        np.stack(hessians_b),
        np.asarray(adequacy),
    )


def _paired_endpoint_contributions(
    outcomes: pd.DataFrame,
    *,
    arm: str,
    magnitude: float,
) -> pd.DataFrame:
    selected = outcomes[
        (outcomes["arm"] == arm)
        & np.isclose(outcomes["magnitude"], float(magnitude))
    ]
    rows = []
    for (parent_id, noise), group in selected.groupby(
        ["parent_id", "noise_mode"],
        sort=True,
    ):
        plus = (
            group[group["sign"] == 1]
            .sort_values("outcome_replicate")["crc_or_hc_detected"]
            .to_numpy(dtype=float)
        )
        minus = (
            group[group["sign"] == -1]
            .sort_values("outcome_replicate")["crc_or_hc_detected"]
            .to_numpy(dtype=float)
        )
        if plus.shape != minus.shape or len(plus) < 2:
            raise ValueError("paired endpoint block is incomplete")
        difference = plus - minus
        contribution = (
            difference.mean() ** 2
            - difference.var(ddof=1) / len(difference)
        ) / 4.0
        rows.append({
            "parent_id": str(parent_id),
            "noise_mode": str(noise),
            "arm": arm,
            "magnitude": float(magnitude),
            "j_contribution": float(contribution),
            "plus_rate": float(plus.mean()),
            "minus_rate": float(minus.mean()),
        })
    return pd.DataFrame(rows)


def _stratified_indices(
    noise_modes: np.ndarray,
    *,
    seed: int,
    draws: int,
) -> list[np.ndarray]:
    rng = np.random.default_rng(int(seed))
    groups = [
        np.flatnonzero(noise_modes == noise)
        for noise in sorted(set(map(str, noise_modes)))
    ]
    return [
        np.concatenate([
            rng.choice(group, size=len(group), replace=True)
            for group in groups
        ])
        for _ in range(int(draws))
    ]


def _principal_angle(left: np.ndarray, right: np.ndarray) -> float:
    cosine = float(
        abs(
            np.dot(left, right)
            / max(
                float(np.linalg.norm(left) * np.linalg.norm(right)),
                1e-12,
            )
        )
    )
    return float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))))


def _bootstrap_operator(
    gradient_a: np.ndarray,
    gradient_b: np.ndarray,
    hessian_a: np.ndarray,
    hessian_b: np.ndarray,
    adequacy: np.ndarray,
    noise_modes: np.ndarray,
    *,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    gradient_operator, curvature_operator = cross_fitted_response_operators(
        gradient_a,
        gradient_b,
        hessian_a,
        hessian_b,
    )
    gradient_values, gradient_vectors = ordered_eigensystem(
        gradient_operator
    )
    curvature_values, curvature_vectors = ordered_eigensystem(
        curvature_operator
    )
    gradient_direction = gradient_vectors[:, 0]
    curvature_direction = curvature_vectors[:, 0]
    endpoint = float(config["confirmation_endpoint"])
    gradient_strength = float(endpoint**2 * gradient_values[0])
    q_a = np.einsum(
        "i,nij,j->n",
        curvature_direction,
        hessian_a,
        curvature_direction,
    )
    q_b = np.einsum(
        "i,nij,j->n",
        curvature_direction,
        hessian_b,
        curvature_direction,
    )
    curvature_strength = float(
        endpoint**4 / 4.0 * np.mean(q_a * q_b)
    )
    indices = _stratified_indices(
        noise_modes,
        seed=int(config["analysis_seed"]),
        draws=int(config["bootstrap_draws"]),
    )
    records = []
    for draw, sampled in enumerate(indices):
        g_op, h_op = cross_fitted_response_operators(
            gradient_a[sampled],
            gradient_b[sampled],
            hessian_a[sampled],
            hessian_b[sampled],
        )
        g_values, g_vectors = ordered_eigensystem(g_op)
        h_values, h_vectors = ordered_eigensystem(h_op)
        g_direction = g_vectors[:, 0]
        h_direction = h_vectors[:, 0]
        h_qa = np.einsum(
            "i,nij,j->n",
            h_direction,
            hessian_a[sampled],
            h_direction,
        )
        h_qb = np.einsum(
            "i,nij,j->n",
            h_direction,
            hessian_b[sampled],
            h_direction,
        )
        records.append({
            "draw": draw,
            "gradient_strength": float(endpoint**2 * g_values[0]),
            "curvature_strength": float(
                endpoint**4 / 4.0 * np.mean(h_qa * h_qb)
            ),
            "gradient_angle_degrees": _principal_angle(
                g_direction,
                gradient_direction,
            ),
            "curvature_angle_degrees": _principal_angle(
                h_direction,
                curvature_direction,
            ),
            "quadratic_adequacy_mse": float(
                np.mean(adequacy[sampled])
            ),
        })
    bootstrap = pd.DataFrame(records)
    summary = {
        "gradient_operator": gradient_operator,
        "curvature_operator": curvature_operator,
        "gradient_eigenvalues": gradient_values,
        "curvature_eigenvalues": curvature_values,
        "gradient_direction": gradient_direction,
        "curvature_direction": curvature_direction,
        "gradient_strength": gradient_strength,
        "curvature_strength": curvature_strength,
        "gradient_strength_lower": float(
            bootstrap["gradient_strength"].quantile(0.025)
        ),
        "curvature_strength_lower": float(
            bootstrap["curvature_strength"].quantile(0.025)
        ),
        "gradient_angle_90": float(
            bootstrap["gradient_angle_degrees"].quantile(0.90)
        ),
        "curvature_angle_90": float(
            bootstrap["curvature_angle_degrees"].quantile(0.90)
        ),
        "quadratic_adequacy_mse": float(np.mean(adequacy)),
        "quadratic_adequacy_upper": float(
            bootstrap["quadratic_adequacy_mse"].quantile(0.95)
        ),
    }
    return bootstrap, summary


def _endpoint_intervals(
    normal: pd.DataFrame,
    tangent: pd.DataFrame,
    *,
    config: dict[str, Any],
) -> pd.DataFrame:
    rng = np.random.default_rng(
        int(config["analysis_seed"]) ^ 0x2F2F2F2F
    )
    rows = []
    for arm, table in [("normal", normal), ("registered_null", tangent)]:
        for noise, group in table.groupby("noise_mode", sort=True):
            values = group["j_contribution"].to_numpy(dtype=float)
            draws = np.mean(
                rng.choice(
                    values,
                    size=(int(config["bootstrap_draws"]), len(values)),
                    replace=True,
                ),
                axis=1,
            )
            alpha = 0.025
            rows.append({
                "arm": arm,
                "noise_mode": str(noise),
                "point": float(values.mean()),
                "lower": float(np.quantile(draws, alpha)),
                "upper": float(np.quantile(draws, 1.0 - alpha)),
                "plus_rate": float(group["plus_rate"].mean()),
                "minus_rate": float(group["minus_rate"].mean()),
            })
    return pd.DataFrame(rows)


def _candidate_payload(
    summary: dict[str, Any],
    *,
    config: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    threshold = float(config["gates"]["candidate_strength_threshold"])
    maximum_angle = float(
        config["gates"]["maximum_principal_angle_degrees"]
    )
    adequacy = bool(
        summary["quadratic_adequacy_upper"]
        <= float(config["gates"]["maximum_quadratic_mse"])
    )
    gradient_pass = bool(
        summary["gradient_strength"] > threshold
        and summary["gradient_strength_lower"] > 0.0
        and summary["gradient_angle_90"] <= maximum_angle
    )
    curvature_pass = bool(
        summary["curvature_strength"] > threshold
        and summary["curvature_strength_lower"] > 0.0
        and summary["curvature_angle_90"] <= maximum_angle
    )
    candidates = []
    if adequacy and gradient_pass:
        candidates.append({
            "candidate_id": "G1",
            "kind": "first_order",
            "coefficients": summary["gradient_direction"].tolist(),
            "strength": summary["gradient_strength"],
            "lower": summary["gradient_strength_lower"],
            "angle_90": summary["gradient_angle_90"],
        })
    if adequacy and curvature_pass:
        candidates.append({
            "candidate_id": "H1",
            "kind": "curvature",
            "coefficients": summary["curvature_direction"].tolist(),
            "strength": summary["curvature_strength"],
            "lower": summary["curvature_strength_lower"],
            "angle_90": summary["curvature_angle_90"],
        })
    merged = False
    if len(candidates) == 2:
        angle = _principal_angle(
            np.asarray(candidates[0]["coefficients"]),
            np.asarray(candidates[1]["coefficients"]),
        )
        if angle < float(config["gates"]["candidate_merge_angle_degrees"]):
            candidates[0]["also_curvature_candidate"] = True
            candidates[0]["gradient_curvature_angle_degrees"] = angle
            candidates = [candidates[0]]
            merged = True
    for candidate in candidates:
        payload = json.dumps(
            candidate["coefficients"],
            separators=(",", ":"),
        ).encode()
        candidate["coefficient_sha256"] = hashlib.sha256(payload).hexdigest()
    return candidates, {
        "quadratic_adequacy": adequacy,
        "gradient_candidate": gradient_pass,
        "curvature_candidate": curvature_pass,
        "candidates_merged": merged,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--preflight-dir", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    config = _read(args.config)
    outcomes_path = args.input_dir / "outcome_rows.csv"
    outcomes = pd.read_csv(outcomes_path)
    probability = _probability_table(
        outcomes,
        outcome_replicates=int(config["outcome_replicates"]),
    )
    (
        parent_ids,
        noise_modes,
        gradient_a,
        gradient_b,
        hessian_a,
        hessian_b,
        adequacy,
    ) = _parent_derivatives(probability, config=config)
    noise_array = np.asarray(noise_modes)
    bootstrap, summary = _bootstrap_operator(
        gradient_a,
        gradient_b,
        hessian_a,
        hessian_b,
        adequacy,
        noise_array,
        config=config,
    )
    normal = _paired_endpoint_contributions(
        outcomes,
        arm="normal",
        magnitude=float(config["normal_tau"]),
    )
    registered_null = _paired_endpoint_contributions(
        outcomes,
        arm="registered_null",
        magnitude=float(config["registered_null_phi"]),
    )
    endpoints = _endpoint_intervals(
        normal,
        registered_null,
        config=config,
    )
    candidates, candidate_checks = _candidate_payload(
        summary,
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
    input_decision = _read(args.input_dir / "decision.json")
    preflight_decision = _read(args.preflight_dir / "decision.json")
    normal_rows = endpoints[endpoints["arm"] == "normal"]
    null_rows = endpoints[endpoints["arm"] == "registered_null"]
    integrity = {
        "input_data_complete": bool(
            input_decision["status"] == "V8_R2F_DISCOVERY_DATA_COMPLETE"
            and all(input_decision["integrity_checks"].values())
        ),
        "preflight_pass": bool(
            preflight_decision["status"]
            == "V8_R2F_GEOMETRY_PREFLIGHT_PASS"
            and all(preflight_decision["integrity_checks"].values())
        ),
        "input_manifest": (
            input_manifest["status"] == "RUN_MANIFEST_PASS"
        ),
        "input_inventory": (
            input_inventory["status"] == "INVENTORY_PASS"
        ),
        "preflight_manifest": (
            preflight_manifest["status"] == "RUN_MANIFEST_PASS"
        ),
        "preflight_inventory": (
            preflight_inventory["status"] == "INVENTORY_PASS"
        ),
        "parent_count": (
            len(parent_ids)
            == len(config["noise_modes"]) * int(config["parents_per_noise"])
        ),
        "half_completeness": bool(
            len(probability)
            == len(parent_ids) * 45 * 2
        ),
        "numeric_integrity": bool(
            np.isfinite(gradient_a).all()
            and np.isfinite(gradient_b).all()
            and np.isfinite(hessian_a).all()
            and np.isfinite(hessian_b).all()
            and np.isfinite(adequacy).all()
        ),
    }
    normal_gate = bool(
        len(normal_rows) == len(config["noise_modes"])
        and (
            normal_rows["lower"]
            > float(config["gates"]["practical_effect_threshold"])
        ).all()
    )
    null_gate = bool(
        len(null_rows) == len(config["noise_modes"])
        and (
            null_rows["upper"]
            <= float(config["gates"]["practical_effect_threshold"])
        ).all()
    )
    gate_checks = {
        "normal_positive_control": normal_gate,
        "registered_tangent_null": null_gate,
        **candidate_checks,
    }
    if not all(integrity.values()):
        status = "V8_R2F_STOP_INVALID_ANALYSIS"
    elif not normal_gate:
        status = "V8_R2F_STOP_POSITIVE_CONTROL_FAILED"
    elif not null_gate:
        status = "V8_R2F_STOP_REGISTERED_NULL_NOT_REPLICATED"
    elif candidates:
        status = "V8_R2F_DISCOVERY_CANDIDATE_FROZEN"
    elif (
        candidate_checks["gradient_candidate"]
        or candidate_checks["curvature_candidate"]
    ) and not candidate_checks["quadratic_adequacy"]:
        status = "V8_R2F_STOP_LOCAL_QUADRATIC_INADEQUATE"
    else:
        status = "V8_R2F_STOP_NO_LOCAL_TANGENT_CANDIDATE"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output_dir / "parent_response_operators.npz",
        parent_ids=np.asarray(parent_ids),
        noise_modes=noise_array,
        gradient_a=gradient_a,
        gradient_b=gradient_b,
        hessian_a=hessian_a,
        hessian_b=hessian_b,
        quadratic_adequacy=adequacy,
        gradient_operator=summary["gradient_operator"],
        curvature_operator=summary["curvature_operator"],
    )
    eigen_rows = []
    for kind in ("gradient", "curvature"):
        for index, value in enumerate(summary[f"{kind}_eigenvalues"]):
            eigen_rows.append({
                "operator": kind,
                "eigen_index": index,
                "eigenvalue": float(value),
                **{
                    f"coefficient_{axis}": float(
                        summary[f"{kind}_direction"][axis]
                    )
                    if index == 0
                    else float("nan")
                    for axis in range(int(config["tangent_dimensions"]))
                },
            })
    pd.DataFrame(eigen_rows).to_csv(
        args.output_dir / "active_eigenvalues.csv",
        index=False,
    )
    bootstrap.to_csv(
        args.output_dir / "subspace_bootstrap.csv",
        index=False,
    )
    endpoints.to_csv(
        args.output_dir / "control_endpoints.csv",
        index=False,
    )
    candidate_artifact = {
        "status": status,
        "selection_is_discovery_only": True,
        "candidates": candidates,
        "candidate_checks": candidate_checks,
        "claim_boundary": str(config["claim_boundary"]),
    }
    _write(
        args.output_dir / "candidate_directions.json",
        candidate_artifact,
    )
    decision = {
        "status": status,
        "integrity_checks": integrity,
        "gate_checks": gate_checks,
        "gradient_strength": summary["gradient_strength"],
        "gradient_strength_lower": summary["gradient_strength_lower"],
        "gradient_angle_90": summary["gradient_angle_90"],
        "curvature_strength": summary["curvature_strength"],
        "curvature_strength_lower": summary["curvature_strength_lower"],
        "curvature_angle_90": summary["curvature_angle_90"],
        "quadratic_adequacy_mse": summary[
            "quadratic_adequacy_mse"
        ],
        "quadratic_adequacy_upper": summary[
            "quadratic_adequacy_upper"
        ],
        "gradient_eigenvalues": summary[
            "gradient_eigenvalues"
        ].tolist(),
        "curvature_eigenvalues": summary[
            "curvature_eigenvalues"
        ].tolist(),
        "candidates": candidates,
        "control_endpoints": endpoints.to_dict(orient="records"),
        "claim_boundary": str(config["claim_boundary"]),
    }
    _write(args.output_dir / "decision.json", decision)
    _write(args.output_dir / "config_effective.json", config)
    (args.output_dir / "report.md").write_text(
        "# H4D-R2F Local Response Operator Discovery\n\n"
        f"Decision: `{status}`\n\n"
        "This is a constrained synthetic detector-geometry discovery. "
        "Only a frozen candidate may proceed to fresh confirmation.\n",
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[
            outcomes_path,
            args.input_dir / "decision.json",
            args.preflight_dir / "decision.json",
            args.preflight_dir / "basis_rows.csv",
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
        "gate_checks": gate_checks,
        "gradient_strength": summary["gradient_strength"],
        "curvature_strength": summary["curvature_strength"],
        "quadratic_adequacy_upper": summary[
            "quadratic_adequacy_upper"
        ],
        "candidates": candidates,
        "output_dir": str(args.output_dir),
    }, indent=2))
    return 0 if all(integrity.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
