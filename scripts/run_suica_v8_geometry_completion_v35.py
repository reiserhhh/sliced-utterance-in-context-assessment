#!/usr/bin/env python3
"""Run V3.5 scale/null/transversality/nonlinear-manifold completion."""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import run_suica_v8_incidence_incremental as base  # noqa: E402
from suica_core.v7_governance import (  # noqa: E402
    write_artifact_inventory,
    write_run_manifest,
)
from suica_core.v8_geometry_completion import (  # noqa: E402
    GeometryCompletionSpec,
    _candidate_edges,
    analyze_scale_world,
    classify_curve_relation,
    classify_surface_relation,
    exact_birth_profiles,
    scale_matching_features,
    simulate_curve_relation,
    simulate_scale_pair,
    simulate_surface_relation,
)

CURVE_WORLDS = (
    "transverse",
    "tangent",
    "coincident",
    "near_miss",
    "boundary",
)
SURFACE_WORLDS = (
    "transverse",
    "tangent",
    "coincident",
    "near_miss",
    "boundary",
    "sinusoidal_transverse",
    "rbf_transverse",
    "reparameterized_transverse",
)
EXPECTED = {
    "transverse": "TRANSVERSE",
    "tangent": "TANGENT",
    "coincident": "COINCIDENT",
    "near_miss": "NO_INTERSECTION",
    "boundary": "BOUNDARY",
    "sinusoidal_transverse": "TRANSVERSE",
    "rbf_transverse": "TRANSVERSE",
    "reparameterized_transverse": "TRANSVERSE",
}
EXPECTED_DIMENSION = {
    "transverse": 0.0,
    "coincident": 1.0,
}
EXPECTED_SURFACE_DIMENSION = {
    "transverse": 1.0,
    "coincident": 2.0,
    "sinusoidal_transverse": 1.0,
    "rbf_transverse": 1.0,
    "reparameterized_transverse": 1.0,
}


def _spec(config: dict[str, Any]) -> GeometryCompletionSpec:
    return GeometryCompletionSpec(
        authors=int(config["authors"]),
        groups=int(config["groups"]),
        conditions=int(config["conditions"]),
        views=int(config["views"]),
        active_conditions=int(config["active_conditions"]),
        ambient=int(config["ambient"]),
        radius_min=float(config["radius_min"]),
        radius_max=float(config["radius_max"]),
        shape_birth_radius=float(config["shape_birth_radius"]),
        noise_sd=float(config["noise_sd"]),
        continuous_persistence_threshold=float(
            config["continuous_persistence_threshold"]
        ),
        minimum_group_coverage=float(config["minimum_group_coverage"]),
        permutations=int(config["permutations"]),
        grid_sizes=tuple(int(item) for item in config["grid_sizes"]),
        curve_points=int(config["curve_points"]),
        surface_grid=int(config["surface_grid"]),
        jet_noise_sd=float(config["jet_noise_sd"]),
        rank_threshold=float(config["rank_threshold"]),
        rank_margin=float(config["rank_margin"]),
        intersection_tolerance=float(config["intersection_tolerance"]),
        hessian_threshold=float(config["hessian_threshold"]),
        bootstrap_repetitions=int(config["bootstrap_repetitions"]),
    )


def _seed(
    config: dict[str, Any],
    *,
    stage: str,
    family: str,
    world_index: int,
    repetition: int,
) -> int:
    return (
        int(config["seed"])
        + (0 if stage == "discovery" else 50_000_000)
        + {"scale": 0, "curve": 10_000_000, "surface": 20_000_000}[family]
        + world_index * 100_000
        + repetition
    )


def _matching_smd(first: np.ndarray, second: np.ndarray) -> float:
    differences = []
    for column in range(first.shape[1]):
        pooled = np.sqrt(
            0.5 * (
                np.var(first[:, column])
                + np.var(second[:, column])
            )
        )
        delta = abs(
            float(np.mean(first[:, column]))
            - float(np.mean(second[:, column]))
        )
        differences.append(delta / max(float(pooled), 1e-12))
    return float(max(differences, default=0.0))


def _scale_worker(
    payload: tuple[dict[str, Any], str, int],
) -> dict[str, Any]:
    config, stage, repetition = payload
    seed = _seed(
        config,
        stage=stage,
        family="scale",
        world_index=0,
        repetition=repetition,
    )
    spec = _spec(config)
    pair = simulate_scale_pair(seed=seed, spec=spec)
    positive = analyze_scale_world(
        pair["positive_views"],
        pair["labels"],
        seed=seed,
        spec=spec,
    )
    negative = analyze_scale_world(
        pair["negative_views"],
        pair["labels"],
        seed=seed + 1,
        spec=spec,
    )
    positive_match = scale_matching_features(
        pair["positive_views"],
        spec=spec,
    )
    negative_match = scale_matching_features(
        pair["negative_views"],
        spec=spec,
    )
    row: dict[str, Any] = {
        "stage": stage,
        "seed": seed,
        "repetition": repetition,
        "matching_smd": _matching_smd(
            positive_match,
            negative_match,
        ),
    }
    for side, estimate in (
        ("positive", positive),
        ("negative", negative),
    ):
        for key in (
            "status",
            "group_claim",
            "refused",
            "coverage",
            "p_fwer",
            "observed_max_persistence",
            "null_max_mean",
            "null_max_99",
            "candidate_count",
            "mean_candidate_size",
            "mean_active_birth",
            "group_f1",
            "group_ari",
        ):
            row[f"{side}_{key}"] = estimate[key]
        for grid, agreement in estimate["grid_agreement"].items():
            row[f"{side}_grid_{grid}_agreement"] = agreement
        row[f"{side}_selected_groups"] = json.dumps(
            estimate["selected_groups"],
            separators=(",", ":"),
        )
    return row


def _relation_worker(
    payload: tuple[dict[str, Any], str, str, int, int],
) -> dict[str, Any]:
    config, stage, family, world, repetition = payload
    worlds = CURVE_WORLDS if family == "curve" else SURFACE_WORLDS
    world_index = worlds.index(world)
    seed = _seed(
        config,
        stage=stage,
        family=family,
        world_index=world_index,
        repetition=repetition,
    )
    spec = _spec(config)
    if family == "curve":
        sample = simulate_curve_relation(
            seed=seed,
            world=world,
            spec=spec,
        )
        estimate = classify_curve_relation(
            sample,
            seed=seed,
            spec=spec,
        )
        expected_dimension = EXPECTED_DIMENSION.get(world, np.nan)
    else:
        sample = simulate_surface_relation(
            seed=seed,
            world=world,
            spec=spec,
        )
        estimate = classify_surface_relation(
            sample,
            seed=seed,
            spec=spec,
        )
        expected_dimension = EXPECTED_SURFACE_DIMENSION.get(
            world,
            np.nan,
        )
    return {
        "stage": stage,
        "family": family,
        "world": world,
        "seed": seed,
        "repetition": repetition,
        "expected_relation": EXPECTED[world],
        "correct": estimate["relation"] == EXPECTED[world],
        "expected_dimension": expected_dimension,
        **estimate,
    }


def _parallel(
    worker: Any,
    payloads: list[Any],
    *,
    jobs: int,
) -> list[dict[str, Any]]:
    if jobs <= 1:
        return [worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(worker, payloads, chunksize=1))


def _run_stage(
    config: dict[str, Any],
    *,
    stage: str,
    repetitions: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    scale_rows = _parallel(
        _scale_worker,
        [(config, stage, repetition) for repetition in range(repetitions)],
        jobs=int(config["jobs"]),
    )
    relation_payloads = [
        (config, stage, family, world, repetition)
        for family, worlds in (
            ("curve", CURVE_WORLDS),
            ("surface", SURFACE_WORLDS),
        )
        for world in worlds
        for repetition in range(repetitions)
    ]
    relation_rows = _parallel(
        _relation_worker,
        relation_payloads,
        jobs=int(config["jobs"]),
    )
    return pd.DataFrame(scale_rows), pd.DataFrame(relation_rows)


def _rate(values: pd.Series) -> dict[str, float | int]:
    vector = values.fillna(False).astype(bool)
    successes = int(vector.sum())
    trials = len(vector)
    return {
        "successes": successes,
        "trials": trials,
        "rate": successes / trials,
        "lower95": base._one_sided_lower(successes, trials),  # noqa: SLF001
        "upper95": base._one_sided_upper(successes, trials),  # noqa: SLF001
    }


def _birth_error(config: dict[str, Any]) -> float:
    spec = _spec(config)
    pair = simulate_scale_pair(
        seed=int(config["seed"]) + 90_001,
        spec=spec,
        noiseless=True,
    )
    candidates = _candidate_edges(pair["positive_views"], spec=spec)
    profiles = exact_birth_profiles(
        pair["positive_views"],
        candidates,
        spec=spec,
    )
    values = [
        value
        for birth in profiles.values()
        for value in birth[: spec.active_conditions]
    ]
    return float(
        max(
            (
                abs(value - spec.shape_birth_radius)
                for value in values
            ),
            default=np.inf,
        )
    )


def _auc_interval(
    frame: pd.DataFrame,
    *,
    seed: int,
) -> dict[str, float]:
    labels = frame["nonlinear_label"].to_numpy(dtype=int)
    scores = frame["rank_score"].to_numpy(dtype=float)
    auc = float(roc_auc_score(labels, scores))
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(999):
        indices = rng.integers(0, len(frame), size=len(frame))
        if len(np.unique(labels[indices])) < 2:
            continue
        draws.append(roc_auc_score(labels[indices], scores[indices]))
    return {
        "auc": auc,
        "lower95": float(np.quantile(draws, 0.025)),
        "upper95": float(np.quantile(draws, 0.975)),
    }


def _decision(
    scale: pd.DataFrame,
    relations: pd.DataFrame,
    config: dict[str, Any],
    *,
    smoke: bool,
) -> dict[str, Any]:
    grid_columns = [
        column for column in scale
        if column.endswith("_agreement")
    ]
    grid_rate = float(
        scale[grid_columns].astype(bool).to_numpy().mean()
    )
    nonboundary = relations[
        relations["world"] != "boundary"
    ]
    boundary = relations[
        relations["world"] == "boundary"
    ]
    dimension = nonboundary[
        np.isfinite(nonboundary["expected_dimension"])
    ].copy()
    dimension["dimension_error"] = abs(
        dimension["intersection_dimension"]
        - dimension["expected_dimension"]
    )
    nonlinear_worlds = {
        "sinusoidal_transverse",
        "rbf_transverse",
        "reparameterized_transverse",
    }
    nonlinear = relations[
        (relations["family"] == "surface")
        & relations["world"].isin(
            nonlinear_worlds | {"tangent", "coincident"}
        )
    ].copy()
    nonlinear["nonlinear_label"] = nonlinear["world"].isin(
        nonlinear_worlds
    ).astype(int)
    nonlinear_auc = _auc_interval(
        nonlinear,
        seed=int(config["seed"]) + 91_003,
    )
    summary = {
        "birth_error": _birth_error(config),
        "grid_decision_agreement": grid_rate,
        "positive_claim": _rate(scale["positive_group_claim"]),
        "negative_claim": _rate(scale["negative_group_claim"]),
        "positive_fwer": _rate(
            scale["positive_p_fwer"]
            <= float(config["gates"]["maximum_fwer_pvalue"])
        ),
        "maximum_matching_smd": float(scale["matching_smd"].max()),
        "relation_accuracy": _rate(nonboundary["correct"]),
        "boundary_refusal": _rate(
            boundary["status"] == "REFUSE_GEOMETRY_BOUNDARY"
        ),
        "intersection_dimension_mae": float(
            dimension["dimension_error"].mean()
        ),
        "nonlinear_auc": nonlinear_auc,
    }
    if smoke:
        checks = {
            "birth": summary["birth_error"] <= 1e-5,
            "scale_contrast": bool(
                scale["positive_group_claim"].all()
                and ~scale["negative_group_claim"].any()
            ),
            "grid": grid_rate == 1.0,
            "relations": bool(nonboundary["correct"].all()),
            "boundary": bool(
                (
                    boundary["status"]
                    == "REFUSE_GEOMETRY_BOUNDARY"
                ).all()
            ),
        }
        status = (
            "V8_SCALE_NULL_TRANSVERSAL_MANIFOLD_V35_SMOKE_PASS"
            if all(checks.values())
            else "V8_SCALE_NULL_TRANSVERSAL_MANIFOLD_V35_SMOKE_STOP"
        )
        return {"status": status, "checks": checks, "summary": summary}

    gates = config["gates"]
    checks = {
        "birth_error": (
            summary["birth_error"] <= gates["maximum_birth_error"]
        ),
        "grid_decision_agreement": (
            summary["grid_decision_agreement"]
            >= gates["minimum_grid_decision_agreement"]
        ),
        "positive_claim": (
            summary["positive_claim"]["lower95"]
            >= gates["minimum_positive_claim_rate"]
        ),
        "negative_claim": (
            summary["negative_claim"]["upper95"]
            <= gates["maximum_null_claim_rate"]
        ),
        "positive_fwer": (
            summary["positive_fwer"]["lower95"]
            >= gates["minimum_positive_claim_rate"]
        ),
        "matching": (
            summary["maximum_matching_smd"]
            <= gates["maximum_matching_smd"]
        ),
        "relation_accuracy": (
            summary["relation_accuracy"]["lower95"]
            >= gates["minimum_relation_accuracy"]
        ),
        "dimension": (
            summary["intersection_dimension_mae"]
            <= gates["maximum_intersection_dimension_mae"]
        ),
        "nonlinear_auc": (
            summary["nonlinear_auc"]["lower95"]
            >= gates["minimum_nonlinear_auc"]
        ),
        "boundary_refusal": (
            summary["boundary_refusal"]["lower95"]
            >= gates["minimum_boundary_refusal_rate"]
        ),
    }
    return {
        "status": (
            "V8_SCALE_NULL_TRANSVERSAL_MANIFOLD_V35_PASS"
            if all(checks.values())
            else "V8_SCALE_NULL_TRANSVERSAL_MANIFOLD_V35_STOP"
        ),
        "checks": checks,
        "summary": summary,
        "claim_boundary": config["claim_boundary"],
    }


def _report(decision: dict[str, Any]) -> str:
    return f"""# V8 Scale/Null/Transversality/Manifold V3.5

Decision: `{decision["status"]}`

## Gates

```json
{json.dumps(decision["checks"], indent=2)}
```

## Summary

```json
{json.dumps(decision["summary"], indent=2)}
```

## Boundary

{decision.get("claim_boundary", "Smoke behavior only.")}
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/v8_scale_null_transversal_manifold_v35.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "results/v8_geometry_completion/v35",
    )
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    config = base._read_json(args.config)  # noqa: SLF001
    if args.smoke:
        config = json.loads(json.dumps(config))
        config["jobs"] = 1
        config["discovery_repetitions"] = 2
        config["confirmation_repetitions"] = 3
        config["permutations"] = 199
        config["bootstrap_repetitions"] = 49
    args.output_dir.mkdir(parents=True, exist_ok=True)

    discovery_scale, discovery_relations = _run_stage(
        config,
        stage="discovery",
        repetitions=int(config["discovery_repetitions"]),
    )
    scale, relations = _run_stage(
        config,
        stage="confirmation",
        repetitions=int(config["confirmation_repetitions"]),
    )
    decision = _decision(
        scale,
        relations,
        config,
        smoke=args.smoke,
    )
    for name, frame in (
        ("discovery_scale_metrics.csv", discovery_scale),
        ("discovery_relation_metrics.csv", discovery_relations),
        ("confirmation_scale_metrics.csv", scale),
        ("confirmation_relation_metrics.csv", relations),
    ):
        frame.to_csv(args.output_dir / name, index=False)
    base._write_json(  # noqa: SLF001
        args.output_dir / "decision.json",
        decision,
    )
    base._write_json(  # noqa: SLF001
        args.output_dir / "config_effective.json",
        config,
    )
    (args.output_dir / "report.md").write_text(
        _report(decision),
        encoding="utf-8",
    )
    write_run_manifest(
        args.output_dir / "run_manifest.json",
        repository_root=ROOT,
        input_paths=[],
        config_path=args.config,
        code_paths=[
            ROOT / "suica_core/v7_governance.py",
            ROOT / "suica_core/v8_incidence_multiplicity.py",
            ROOT / "suica_core/v8_incidence_incremental.py",
            ROOT / "suica_core/v8_geometry_completion.py",
            ROOT / "scripts/run_suica_v8_incidence_incremental.py",
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
    print(json.dumps({
        "status": decision["status"],
        "output_dir": str(args.output_dir),
        "checks": decision["checks"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
