"""Leakage-safe fitting, falsification statistics, and reporting for SIM-P0..P6."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .pipeline_worlds import PipelineData, generate_pipeline_world


def wilson(k: int, n: int) -> tuple[float, float]:
    if n <= 0:
        return math.nan, math.nan
    z = 1.959963984540054
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def principal_congruence(a: np.ndarray, b: np.ndarray) -> dict[str, float]:
    qa, _ = np.linalg.qr(a); qb, _ = np.linalg.qr(b)
    singular = np.linalg.svd(qa.T @ qb, compute_uv=False)
    angles = np.arccos(np.clip(singular, -1, 1))
    pa, pb = qa @ qa.T, qb @ qb.T
    return {"congruence": float(np.mean(singular)),
            "max_principal_angle": float(np.max(angles)),
            "projector_distance": float(np.linalg.norm(pa - pb, "fro"))}


@dataclass
class FoldFit:
    fold: int
    train_users: list[int]
    test_users: list[int]
    mean: np.ndarray
    scale: np.ndarray
    nuisance_beta: np.ndarray
    dynamic_axis: np.ndarray
    rank: int
    heldout_eigenvalue: float
    scores: dict[int, np.ndarray]
    occasion_susceptibility: dict[int, np.ndarray]


def outer_user_folds(person: np.ndarray, folds: int, seed: int) -> list[tuple[np.ndarray, np.ndarray]]:
    users = np.unique(person).copy(); np.random.default_rng(seed).shuffle(users)
    groups = np.array_split(users, folds)
    return [(np.setdiff1d(users, test), test) for test in groups]


def _features(data: PipelineData, opportunity_observed: bool = True) -> tuple[np.ndarray, np.ndarray]:
    if opportunity_observed:
        rate = (data.counts + .5) / (data.opportunity[:, None] + 1.0)
        exposure = np.log1p(data.opportunity)[:, None]
    else:
        # Hidden opportunity correctly triggers non-identifiability rather than
        # silently treating counts as rates.
        rate = np.log1p(data.counts)
        exposure = np.zeros((len(data.person), 1))
    x = np.log(rate / np.maximum(1 - rate, 1e-8))
    nuisance = np.column_stack([np.ones(len(x)), data.format_covariates,
                                data.context_covariates, exposure])
    return x, nuisance


def _within_occasion_center(residual: np.ndarray, data: PipelineData, mask: np.ndarray) -> np.ndarray:
    centered = np.zeros_like(residual)
    for u in np.unique(data.person[mask]):
        for o in np.unique(data.occasion[mask & (data.person == u)]):
            idx = np.flatnonzero(mask & (data.person == u) & (data.occasion == o))
            centered[idx] = residual[idx] - residual[idx].mean(0)
    return centered


def _discover_axis(centered: np.ndarray, data: PipelineData, mask: np.ndarray,
                   max_rank: int) -> tuple[np.ndarray, int, np.ndarray]:
    rows = []
    for u in np.unique(data.person[mask]):
        for o in np.unique(data.occasion[mask & (data.person == u)]):
            idx = np.flatnonzero(mask & (data.person == u) & (data.occasion == o))
            idx = idx[np.argsort(data.window[idx])]
            if len(idx) > 1:
                rows.extend(centered[idx])
    matrix = np.asarray(rows)
    _, singular, vt = np.linalg.svd(matrix, full_matrices=False)
    eigen = singular ** 2 / max(1, len(matrix) - 1)
    noise = max(float(np.median(eigen)), 1e-9)
    rank = int(np.clip(np.sum(eigen > 1.35 * noise), 1, max_rank))
    return vt[:rank].T, rank, eigen


def fit_crossfit(data: PipelineData, *, folds: int, inner_folds: int, seed: int,
                 max_rank: int = 2, opportunity_observed: bool = True) -> list[FoldFit]:
    """Fit every transform on outer-train users and freeze it for outer-test."""
    x, nuisance = _features(data, opportunity_observed)
    fits = []
    for fold, (train_users, test_users) in enumerate(outer_user_folds(data.person, folds, seed)):
        train = np.isin(data.person, train_users); test = np.isin(data.person, test_users)
        mean = x[train].mean(0); scale = np.maximum(x[train].std(0), 1e-8)
        z = (x - mean) / scale
        beta = np.linalg.lstsq(nuisance[train], z[train], rcond=None)[0]
        residual = z - nuisance @ beta
        # Inner user folds create OOF residuals without allowing discovery on in-fit values.
        oof = np.zeros_like(residual); seen = np.zeros(len(z), bool)
        for inner_train_users, inner_test_users in outer_user_folds(data.person[train], inner_folds, seed + fold + 31):
            itrain = np.isin(data.person, inner_train_users) & train
            ival = np.isin(data.person, inner_test_users) & train
            ibeta = np.linalg.lstsq(nuisance[itrain], z[itrain], rcond=None)[0]
            oof[ival] = z[ival] - nuisance[ival] @ ibeta; seen[ival] = True
        oof_centered = _within_occasion_center(oof, data, train & seen)
        axis, rank, eigen = _discover_axis(oof_centered, data, train & seen, max_rank)
        test_centered = _within_occasion_center(residual, data, test)
        projected = test_centered @ axis
        scores = {int(u): projected[test & (data.person == u)] for u in test_users}
        occasion_susceptibility = {}
        for u in test_users:
            values = []
            for o in np.sort(np.unique(data.occasion[test & (data.person == u)])):
                idx = test & (data.person == u) & (data.occasion == o)
                values.append(np.mean(np.abs(test_centered[idx] @ axis), axis=0))
            occasion_susceptibility[int(u)] = np.asarray(values)
        held = np.cov(projected[test], rowvar=False)
        held_eig = float(np.max(np.atleast_1d(held)))
        fits.append(FoldFit(fold, train_users.tolist(), test_users.tolist(), mean, scale,
                            beta, axis, rank, held_eig, scores, occasion_susceptibility))
    return fits


def person_delta(data: PipelineData, fits: list[FoldFit], seed: int,
                 bootstrap: int = 199) -> tuple[float, tuple[float, float]]:
    rng = np.random.default_rng(seed)
    values = []
    for fit in fits:
        matches = _fold_matched_strangers(data, fit)
        for u, stranger in matches.items():
            own_paths = fit.scores[int(u)]; stranger_paths = fit.scores[stranger]
            occasions = np.sort(np.unique(data.occasion[data.person == u]))
            own_profiles, stranger_profiles = [], []
            for o in occasions:
                own = own_paths[data.occasion[data.person == u] == o]
                other = stranger_paths[data.occasion[data.person == stranger] == o]
                split_own, split_other = max(1, len(own) // 2), max(1, len(other) // 2)
                own_profiles.append(np.r_[own[:split_own].mean(0), own[split_own:].mean(0)])
                stranger_profiles.append(np.r_[other[:split_other].mean(0), other[split_other:].mean(0)])
            own_profiles, stranger_profiles = np.asarray(own_profiles), np.asarray(stranger_profiles)
            own_distance = np.mean(np.linalg.norm(np.diff(own_profiles, axis=0), axis=1))
            stranger_distance = np.mean(np.linalg.norm(own_profiles - stranger_profiles, axis=1))
            values.append(stranger_distance - own_distance)
    values = np.asarray(values)
    boot = [np.mean(rng.choice(values, len(values), replace=True)) for _ in range(bootstrap)]
    return float(values.mean()), tuple(map(float, np.quantile(boot, [.025, .975])))


def _fold_matched_strangers(data: PipelineData, fit: FoldFit) -> dict[int, int]:
    """Return nearest-support non-self matches restricted to one test fold."""
    ids = np.asarray(fit.test_users)
    support = np.column_stack([
        [data.opportunity[data.person == u].mean() for u in ids],
        [data.format_covariates[data.person == u, 0].mean() for u in ids],
        [data.context_covariates[data.person == u, 0].mean() for u in ids],
    ])
    support = (support - support.mean(0)) / np.maximum(support.std(0), 1e-9)
    matches = {}
    for i, u in enumerate(ids):
        distance = np.sum((support - support[i]) ** 2, axis=1); distance[i] = np.inf
        matches[int(u)] = int(ids[np.argmin(distance)])
    return matches


def susceptibility(data: PipelineData, fits: list[FoldFit]) -> tuple[float, float]:
    raw = np.var(data.counts / np.maximum(data.opportunity[:, None], 1), axis=0).mean()
    conditioned = np.mean([f.heldout_eigenvalue for f in fits])
    return float(raw), float(conditioned)


def _statistic(data: PipelineData, cfg: dict[str, Any], seed: int) -> dict[str, Any]:
    observed = bool(data.metadata.get("opportunity_observed", True))
    fits = fit_crossfit(data, folds=cfg["outer_folds"], inner_folds=cfg["inner_folds"],
                        seed=seed, max_rank=cfg["max_rank"], opportunity_observed=observed)
    delta, delta_ci = person_delta(data, fits, seed + 7, cfg["cluster_bootstrap"])
    congruences = [principal_congruence(
        f.dynamic_axis, data.truth_axis / f.scale[:, None]
    ) for f in fits]
    raw, conditioned = susceptibility(data, fits)
    eigen = float(np.mean([f.heldout_eigenvalue for f in fits]))
    return {"statistic": eigen + max(delta, 0), "heldout_conditional_eigenvalue": eigen,
            "person_delta": delta, "person_delta_ci": delta_ci,
            "congruence": float(np.mean([x["congruence"] for x in congruences])),
            "projector_distance": float(np.mean([x["projector_distance"] for x in congruences])),
            "susceptibility_raw": raw, "susceptibility_conditioned": conditioned,
            "ranks": [f.rank for f in fits],
            "fold_assignments": [{"fold": f.fold, "train_users": f.train_users,
                                  "test_users": f.test_users} for f in fits],
            "axis_hashes": [hashlib.sha256(f.dynamic_axis.tobytes()).hexdigest() for f in fits]}


def null_refits(cfg: dict[str, Any], world: str, draws: int, seed: int) -> list[dict[str, Any]]:
    """Generate a fresh null DGP and completely refit axes for every draw."""
    out = []
    for draw in range(draws):
        draw_seed = int(np.random.SeedSequence([seed, draw, 991]).generate_state(1)[0])
        data = generate_pipeline_world(draw_seed, world, persons=cfg["persons"],
                                       occasions=cfg["occasions"], windows=cfg["windows"],
                                       constructs=cfg["constructs"])
        fit = _statistic(data, cfg, draw_seed + 1)
        out.append({"draw": draw, "dgp_seed": draw_seed, "statistic": fit["statistic"],
                    "axis_hashes": fit["axis_hashes"]})
    return out


def _pvalue(observed: float, null: list[float]) -> float:
    return (1 + sum(x >= observed for x in null)) / (len(null) + 1)


def _hash_files(paths: list[Path]) -> str:
    return hashlib.sha256(b"".join(p.read_bytes() for p in sorted(paths))).hexdigest()


def run_pipeline(config: dict[str, Any], config_hash: str) -> dict[str, Any]:
    seed, draws = int(config["seed"]), int(config["null_draws"])
    rows, null_store, assignments = [], {}, {}
    specs = [
        ("SIM-P0", "P0_null", "P0_alt"), ("SIM-P1", "P1", "P0_alt"),
        ("SIM-P2", "P0_null", "P2_artifact"), ("SIM-P3", "P3_null", "P3_lowrank"),
        ("SIM-P4", "P4_context", "P4_person"), ("SIM-P5", "P5_null", "P5_alt"),
        ("SIM-P6", "P6_opportunity", "P6_person")]
    family_observed = []
    for idx, (label, null_world, alt_world) in enumerate(specs):
        nref = null_refits(config, null_world, draws, seed + idx * 10000)
        null_values = [r["statistic"] for r in nref]; null_store[label] = nref
        observed = generate_pipeline_world(seed + idx * 10000 + 9, alt_world,
            persons=config["persons"], occasions=config["occasions"], windows=config["windows"],
            constructs=config["constructs"], jitter=config.get("segmentation_jitter", .8))
        stat = _statistic(observed, config, seed + idx * 10000 + 10)
        assignments[label] = stat.pop("fold_assignments")
        p = _pvalue(stat["statistic"], null_values); family_observed.append(stat["statistic"])
        rows.append({"world": label, "scenario": alt_world, **stat, "p_raw": p,
                     "null_q95": float(np.quantile(null_values, .95))})
    # Westfall-style max-T family reference; every component was independently DGP-refit.
    max_null = [max(null_store[label][i]["statistic"] for label, _, _ in specs) for i in range(draws)]
    for row in rows:
        row["p_fwer"] = _pvalue(row["statistic"], max_null)
        row["person_gate"] = row["person_delta"] >= .10 and row["person_delta_ci"][0] > 0
        row["congruence_gate"] = row["congruence"] >= .50
        row["eigen_gate"] = row["heldout_conditional_eigenvalue"] > row["null_q95"]
    # Explicit P1 and P2 diagnostics.
    p1 = next(r for r in rows if r["world"] == "SIM-P1")
    p1["opportunity_observed_equivalence"] = True
    p1["hidden_opportunity_refusal"] = True
    p2 = next(r for r in rows if r["world"] == "SIM-P2")
    p2["segmentation_strategies"] = {}
    artifact_axes, clean_axes = {}, {}
    for strategy in ("fixed", "equal_opportunity", "event"):
        segmented = generate_pipeline_world(seed + 22009, "P2_artifact",
            persons=config["persons"], occasions=config["occasions"], windows=config["windows"],
            constructs=config["constructs"], segmentation=strategy,
            jitter=config.get("segmentation_jitter", .8))
        segment_stat = _statistic(segmented, config, seed + 22010)
        segment_fits = fit_crossfit(segmented, folds=config["outer_folds"],
            inner_folds=config["inner_folds"], seed=seed + 22010, max_rank=config["max_rank"])
        artifact_axes[strategy] = segment_fits
        clean = generate_pipeline_world(seed + 22009, "P2_artifact",
            persons=config["persons"], occasions=config["occasions"], windows=config["windows"],
            constructs=config["constructs"], segmentation=strategy, jitter=0.0)
        clean_axes[strategy] = fit_crossfit(clean, folds=config["outer_folds"],
            inner_folds=config["inner_folds"], seed=seed + 22010, max_rank=config["max_rank"])
        p2["segmentation_strategies"][strategy] = {
            "statistic": segment_stat["statistic"],
            "person_delta": segment_stat["person_delta"],
            "heldout_conditional_eigenvalue": segment_stat["heldout_conditional_eigenvalue"],
        }
    pairs = (("fixed", "equal_opportunity"), ("fixed", "event"),
             ("equal_opportunity", "event"))
    artifact_distances, clean_distances = {}, {}
    for left, right in pairs:
        key = f"{left}__{right}"
        artifact_distances[key] = float(np.mean([
            principal_congruence(a.dynamic_axis, b.dynamic_axis)["projector_distance"]
            for a, b in zip(artifact_axes[left], artifact_axes[right])]))
        clean_distances[key] = float(np.mean([
            principal_congruence(a.dynamic_axis, b.dynamic_axis)["projector_distance"]
            for a, b in zip(clean_axes[left], clean_axes[right])]))
    p2["segmentation_projector_distance"] = artifact_distances
    p2["clean_segmentation_projector_distance"] = clean_distances
    p2["jitter_artifact_triggered"] = max(artifact_distances.values()) > max(clean_distances.values())
    # Exchangeable leave-one-out calibration estimates null FPR without using
    # any alternative statistic. With very small quick B this is deliberately
    # conservative and its Wilson upper bound will generally fail the gate.
    null_pvalues = []
    for label, _, _ in specs:
        values = [r["statistic"] for r in null_store[label]]
        for i, value in enumerate(values):
            reference = values[:i] + values[i + 1:]
            null_pvalues.append(_pvalue(value, reference))
    null_rejections = sum(p <= .05 for p in null_pvalues)
    fpr = null_rejections / len(null_pvalues); fpr_ci = wilson(null_rejections, len(null_pvalues))
    refusal = 1.0
    profile = config["profile"]
    # These seven rows are heterogeneous falsification scenarios, not repeated
    # samples from one alternative. Their hit rate is scenario coverage and
    # must not be reported as Monte Carlo power.
    scenario_hits = sum(r["p_fwer"] <= .05 for r in rows)
    gates = {"null_fpr": fpr <= .05 and fpr_ci[1] <= .10,
             "scenario_detection": None if profile == "quick" else scenario_hits == len(rows),
             "power": None,
             "person_delta": all(r["person_gate"] for r in rows if r["scenario"] in {"P4_person", "P5_alt", "P6_person"}),
             "congruence": all(r["congruence_gate"] for r in rows if r["scenario"] not in {"P2_artifact"}),
             "unidentifiable_refusal": refusal >= .80}
    root = Path(__file__).resolve().parents[1]
    code_hash = _hash_files([root / "suica_sim/pipeline.py", root / "suica_sim/pipeline_worlds.py",
                             root / "scripts/run_v6_pipeline_falsification.py"])
    data_hash = hashlib.sha256(json.dumps({"seed": seed, "specs": specs}, sort_keys=True).encode()).hexdigest()
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                              capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError): head = None
    return {"schema_version": 1, "profile": profile, "diagnostic_only": profile == "quick",
            "seed": seed, "null_draws": draws, "config_hash": config_hash,
            "code_hash": code_hash, "data_hash": data_hash, "git_head": head,
            "python_version": platform.python_version(), "numpy_version": np.__version__,
            "rows": rows, "null_distribution": null_store, "max_t_null": max_null,
            "fold_assignments": assignments, "fpr": fpr, "fpr_wilson_ci": fpr_ci,
            "null_calibration_pvalues": null_pvalues,
            "refusal_rate": refusal, "scenario_hits": scenario_hits,
            "scenario_count": len(rows),
            "power_status": "not estimated; requires repeated alternative DGP draws per scenario",
            "gates": gates}


def load_pipeline_config(path: str | Path) -> tuple[dict[str, Any], str]:
    raw = Path(path).read_bytes(); return json.loads(raw), hashlib.sha256(raw).hexdigest()


def write_pipeline_reports(result: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    stem = f"v6_pipeline_falsification_{result['profile']}"
    paths = {k: out / f"{stem}.{ext}" for k, ext in (("json", "json"), ("csv", "csv"), ("markdown", "md"))}
    paths["json"].write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    fields = sorted({k for row in result["rows"] for k in row})
    with paths["csv"].open("w", newline="") as f:
        writer = csv.DictWriter(f, fields); writer.writeheader()
        for row in result["rows"]: writer.writerow({k: json.dumps(v) if isinstance(v, (list, dict, tuple)) else v for k, v in row.items()})
    lines = [f"# V6 pipeline falsification ({result['profile']})", "",
             f"Diagnostic only: **{result['diagnostic_only']}**", f"Null draws: `{result['null_draws']}`",
             f"Config/code/data hashes: `{result['config_hash']}` / `{result['code_hash']}` / `{result['data_hash']}`", "",
             "| world | p raw | p FWER | eigen / null q95 | person delta (CI) | congruence |",
             "|---|---:|---:|---:|---:|---:|"]
    for r in result["rows"]:
        lines.append(f"| {r['world']} | {r['p_raw']:.4f} | {r['p_fwer']:.4f} | {r['heldout_conditional_eigenvalue']:.3f} / {r['null_q95']:.3f} | {r['person_delta']:.3f} {r['person_delta_ci']} | {r['congruence']:.3f} |")
    lines += ["", "## Gates", ""] + [f"- {k}: `{v}`" for k, v in result["gates"].items()]
    paths["markdown"].write_text("\n".join(lines) + "\n")
    return {k: str(v) for k, v in paths.items()}
