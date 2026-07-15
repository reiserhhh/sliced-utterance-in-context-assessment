"""Leakage-safe simulations for the V6 P7--P10 extended feature claims."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
import subprocess
from pathlib import Path
from typing import Any

import numpy as np


def wilson_interval(k: int, n: int) -> tuple[float, float]:
    if n == 0:
        return math.nan, math.nan
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def add_one_p(observed: float, null: list[float] | np.ndarray) -> float:
    values = np.asarray(null)
    return float((1 + np.sum(values >= observed)) / (len(values) + 1))


def assert_timestamp_order(timestamp: np.ndarray) -> None:
    if len(timestamp) > 1 and np.any(np.diff(timestamp) <= 0):
        raise ValueError("timestamps must be strictly increasing")


def fit_var_ols(series: np.ndarray) -> dict[str, np.ndarray | float]:
    """Fit VAR(1), returning equation-wise sigma^2 (X'X)^-1 standard errors."""
    y = np.asarray(series, float)
    if y.ndim != 2 or len(y) < y.shape[1] + 3:
        raise ValueError("series is too short for VAR(1)")
    x = np.column_stack([np.ones(len(y) - 1), y[:-1]])
    target = y[1:]
    xtx_inv = np.linalg.inv(x.T @ x)
    beta = xtx_inv @ x.T @ target
    residual = target - x @ beta
    dof = len(x) - x.shape[1]
    sigma = residual.T @ residual / dof
    se = np.column_stack([
        np.sqrt(np.maximum(np.diag(sigma)[j] * np.diag(xtx_inv), 0))
        for j in range(target.shape[1])
    ])
    return {"intercept": beta[0], "A": beta[1:].T, "se": se[1:].T,
            "innovation_cov": sigma, "loglik": gaussian_loglik(residual, sigma)}


def gaussian_loglik(residual: np.ndarray, covariance: np.ndarray) -> float:
    covariance = np.asarray(covariance) + np.eye(covariance.shape[0]) * 1e-9
    sign, logdet = np.linalg.slogdet(covariance)
    if sign <= 0:
        return -math.inf
    quad = np.einsum("ni,ij,nj->n", residual, np.linalg.inv(covariance), residual)
    return float(np.mean(-.5 * (residual.shape[1] * math.log(2 * math.pi) + logdet + quad)))


def generate_var_world(rng: np.random.Generator, n: int, coupling: float,
                       zero_probability: float = .25, intensity: float = .35,
                       return_latent: bool = False) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
    """VAR counts with fixed diagonal persistence and marginal zero inflation."""
    latent = np.zeros((n + 100, 3))
    a = np.diag([.62, .54, .46])
    a[1, 0] = coupling
    noise_cov = np.array([[.55, .08, 0], [.08, .50, .04], [0, .04, .45]])
    for t in range(1, len(latent)):
        latent[t] = a @ latent[t - 1] + rng.multivariate_normal(np.zeros(3), noise_cov)
    latent = latent[100:]
    counts = rng.poisson(np.exp(np.clip(intensity + .42 * latent, -2, 4.5))).astype(float)
    counts[rng.random(counts.shape) < zero_probability] = 0
    observed = np.log1p(counts)
    return (observed, latent) if return_latent else observed


def _var_fold_metrics(series: np.ndarray, folds: int) -> dict[str, Any]:
    blocks = np.array_split(np.arange(1, len(series)), folds)
    estimates, zscores, gains = [], [], []
    for block in blocks:
        test_start = int(block[0])
        train = series[:test_start]
        if len(train) < 20:
            train = series[:int(block[-1]) + 1]
            test = series[int(block[-1]) + 1:]
        else:
            test = series[test_start - 1:int(block[-1]) + 1]
        if len(test) < 3:
            continue
        full = fit_var_ols(train)
        restricted_series = train[:, 1]
        xr = np.column_stack([np.ones(len(restricted_series) - 1), restricted_series[:-1]])
        br = np.linalg.lstsq(xr, restricted_series[1:], rcond=None)[0]
        restricted_var = float(np.mean((restricted_series[1:] - xr @ br) ** 2)) + 1e-9
        pred = full["intercept"] + test[:-1] @ full["A"].T
        full_ll = gaussian_loglik(test[1:] - pred, full["innovation_cov"])
        restricted_resid = test[1:, 1] - (br[0] + br[1] * test[:-1, 1])
        restricted_ll = float(np.mean(-.5 * (math.log(2 * math.pi * restricted_var) + restricted_resid ** 2 / restricted_var)))
        full_target_ll = gaussian_loglik((test[1:, 1] - pred[:, 1])[:, None],
                                         np.array([[full["innovation_cov"][1, 1]]]))
        estimate = float(full["A"][1, 0]); se = float(full["se"][1, 0])
        estimates.append(estimate); zscores.append(estimate / max(se, 1e-12))
        gains.append(full_target_ll - restricted_ll)
    direction = float(max(np.mean(np.asarray(estimates) > 0), np.mean(np.asarray(estimates) < 0)))
    return {"coupling": float(np.mean(estimates)), "max_t": float(np.max(np.abs(zscores))),
            "likelihood_gain": float(np.mean(gains)), "direction_stability": direction}


def evaluate_p7(rng: np.random.Generator, cfg: dict[str, Any]) -> dict[str, Any]:
    null_stats, null_reject, alt_reject, gains, stability = [], 0, 0, [], []
    oracle_gains, oracle_stability = [], []
    for _ in range(cfg["mc"]):
        per_null = []
        for _edge in range(3):
            metric = _var_fold_metrics(generate_var_world(rng, cfg["var_n"], 0), cfg["folds"])
            per_null.append(metric["max_t"])
        null_stats.append(max(per_null))
    cutoff = float(np.quantile(null_stats, .95))
    for value in null_stats:
        null_reject += value > cutoff
    alt_t = []
    for _ in range(cfg["mc"]):
        observed, latent = generate_var_world(
            rng, cfg["var_n"], cfg["var_coupling"], return_latent=True)
        metric = _var_fold_metrics(observed, cfg["folds"])
        oracle = _var_fold_metrics(latent, cfg["folds"])
        alt_t.append(metric["max_t"]); gains.append(metric["likelihood_gain"])
        stability.append(metric["direction_stability"]); alt_reject += metric["max_t"] > cutoff
        oracle_gains.append(oracle["likelihood_gain"])
        oracle_stability.append(oracle["direction_stability"])
    ladder = {}
    for zero_probability in (0.0, .10, .25):
        ladder[str(zero_probability)] = {}
        for intensity in (.35, 1.5, 3.0):
            ladder_gains = []
            for _ in range(min(cfg["mc"], 100)):
                observed = generate_var_world(
                    rng, cfg["var_n"], cfg["var_coupling"],
                    zero_probability=zero_probability, intensity=intensity)
                ladder_gains.append(
                    _var_fold_metrics(observed, cfg["folds"])["likelihood_gain"])
            ladder[str(zero_probability)][str(intensity)] = float(np.mean(ladder_gains))
    fpr_ci, power_ci = wilson_interval(null_reject, cfg["mc"]), wilson_interval(alt_reject, cfg["mc"])
    return {"feature": "P7", "fpr": null_reject / cfg["mc"], "fpr_ci": fpr_ci,
            "power": alt_reject / cfg["mc"], "power_ci": power_ci,
            "heldout_likelihood_gain": float(np.mean(gains)),
            "direction_stability": float(np.mean(stability)),
            "oracle_likelihood_gain": float(np.mean(oracle_gains)),
            "oracle_direction_stability": float(np.mean(oracle_stability)),
            "measurement_boundary_gain": ladder,
            "alt_add_one_p": add_one_p(float(np.mean(alt_t)), null_stats), "max_t_cutoff": cutoff}


def generate_change_point_world(rng: np.random.Generator, n: int, scenario: str,
                                cp: int | None = None, opportunity_multiplier: float = 1.0
                                ) -> dict[str, np.ndarray | int | None]:
    cp = n // 2 if cp is None else cp
    latent = np.zeros(n); fmt = np.zeros(n); opportunity = rng.poisson(10, n) + 2
    scale = np.ones(n)
    if scenario == "latent": latent[cp:] += 1.25
    elif scenario == "heteroskedastic": scale[cp:] = 2.0
    elif scenario == "format_only": fmt[cp:] = 1.0
    elif scenario == "opportunity_only": opportunity[cp:] += 14
    elif scenario != "null": raise ValueError(scenario)
    z = latent + .9 * fmt + rng.normal(0, scale)
    opportunity = np.maximum(1, np.rint(opportunity * opportunity_multiplier)).astype(int)
    probability = 1 / (1 + np.exp(-(-1 + z)))
    counts = rng.binomial(opportunity, probability)
    counts[rng.random(n) < .18] = 0
    return {"counts": counts, "opportunity": opportunity, "format": fmt,
            "timestamp": np.arange(n), "truth_cp": cp if scenario == "latent" else None,
            "latent_score": z - .9 * fmt}


def discover_change_point_series(series: np.ndarray, train_end: int,
                                 min_segment: int = 16) -> int:
    """Locate one mean change in an already residualized continuous series."""
    residual = np.asarray(series, float)
    candidates = np.arange(min_segment, train_end - min_segment + 1)
    scores = np.array([
        abs(residual[:c].mean() - residual[c:train_end].mean()) /
        math.sqrt(residual[:c].var() / c + residual[c:train_end].var() /
                  (train_end - c) + 1e-9)
        for c in candidates])
    return int(candidates[np.argmax(scores)])


def discover_change_point(data: dict[str, Any], train_end: int, min_segment: int = 16) -> dict[str, Any]:
    assert_timestamp_order(np.asarray(data["timestamp"]))
    count = np.asarray(data["counts"], float); opp = np.asarray(data["opportunity"], float)
    fmt = np.asarray(data["format"], float)
    y = np.log((count + .5) / (opp - count + .5))
    nuisance = np.column_stack([np.ones(len(y)), fmt, np.log1p(opp)])
    beta = np.linalg.lstsq(nuisance[:train_end], y[:train_end], rcond=None)[0]
    residual = y - nuisance @ beta
    candidates = np.arange(min_segment, train_end - min_segment + 1)
    scores = np.array([abs(residual[:c].mean() - residual[c:train_end].mean()) /
                       math.sqrt(residual[:c].var() / c + residual[c:train_end].var() / (train_end - c) + 1e-9)
                       for c in candidates])
    selected = int(candidates[np.argmax(scores)])
    return {"cp": selected, "train_score": float(scores.max()), "residual": residual}


def evaluate_p8(rng: np.random.Generator, cfg: dict[str, Any]) -> dict[str, Any]:
    located = confirmed = format_false = 0
    errors, oracle_errors = [], []
    n, train_end = cfg["cp_n"], cfg["cp_train_end"]
    for _ in range(cfg["mc"]):
        latent = generate_change_point_world(rng, n, "latent", cfg["cp_location"])
        fit = discover_change_point(latent, train_end)
        error = abs(fit["cp"] - cfg["cp_location"]) / cfg["cp_window"]
        errors.append(error); located += error <= 1
        oracle_cp = discover_change_point_series(
            np.asarray(latent["latent_score"]), train_end)
        oracle_errors.append(abs(oracle_cp - cfg["cp_location"]) / cfg["cp_window"])
        r = fit["residual"]; c = fit["cp"]
        pre = r[max(0, c - cfg["cp_window"]):c]
        post = r[train_end:train_end + cfg["cp_window"]]
        se = math.sqrt(pre.var() / len(pre) + post.var() / len(post) + 1e-9)
        confirmed += abs(post.mean() - pre.mean()) / se > 1.96
        fmt = discover_change_point(generate_change_point_world(rng, n, "format_only"), train_end)
        format_false += fmt["train_score"] > 3.0
    opportunity_ladder = {str(multiplier): [] for multiplier in (1.0, 4.0, 16.0)}
    # Pair the latent path and nuisance draws across opportunity levels.
    for _ in range(min(cfg["mc"], 100)):
        paired_seed = int(rng.integers(0, 2**32 - 1))
        for multiplier in (1.0, 4.0, 16.0):
            data = generate_change_point_world(
                np.random.default_rng(paired_seed), n, "latent",
                cfg["cp_location"], multiplier)
            cp_hat = discover_change_point(data, train_end)["cp"]
            opportunity_ladder[str(multiplier)].append(
                abs(cp_hat - cfg["cp_location"]) / cfg["cp_window"])
    opportunity_ladder = {
        key: float(np.mean(values)) for key, values in opportunity_ladder.items()
    }
    return {"feature": "P8", "location_error_windows": float(np.mean(errors)),
            "oracle_location_error_windows": float(np.mean(oracle_errors)),
            "opportunity_ladder_location_error": opportunity_ladder,
            "location_within_one_rate": located / cfg["mc"], "confirmation_rate": confirmed / cfg["mc"],
            "format_only_fpr": format_false / cfg["mc"],
            "format_only_fpr_ci": wilson_interval(format_false, cfg["mc"])}


def multiscale_signal(rng: np.random.Generator, n: int = 256) -> tuple[np.ndarray, np.ndarray]:
    t = np.arange(n)
    basis = np.column_stack([(-1.0) ** t, np.sin(2 * np.pi * t / 4), np.sin(2 * np.pi * t / 16)])
    weights = np.array([.7, 1.0, .8])
    return basis @ weights + rng.normal(0, .35, n), basis


def recover_scale_energy(signal: np.ndarray, scales: tuple[int, ...] = (1, 4, 16)) -> dict[int, float]:
    n = len(signal); spectrum = np.abs(np.fft.rfft(signal - np.mean(signal))) ** 2
    total = max(float(spectrum[1:].sum()), 1e-12)
    out = {}
    for scale in scales:
        index = n // 2 if scale == 1 else int(round(n / scale))
        out[scale] = float(spectrum[min(index, len(spectrum) - 1)] / total)
    return out


def alias_auc(scores_a: np.ndarray, scores_b: np.ndarray) -> float:
    comparisons = (scores_a[:, None] > scores_b[None, :]).mean()
    ties = (scores_a[:, None] == scores_b[None, :]).mean()
    return float(max(comparisons + .5 * ties, 1 - comparisons - .5 * ties))


def evaluate_p9(rng: np.random.Generator, cfg: dict[str, Any]) -> dict[str, Any]:
    errors, subspace, alias_a, alias_b = [], [], [], []
    for _ in range(cfg["mc"]):
        fine, basis = multiscale_signal(rng, 256)
        truth = recover_scale_energy(fine)
        for n in (32, 64, 128, 256):
            observed = fine[:n]
            identifiable = [s for s in (1, 4, 16) if n >= 4 * s]
            recovered = recover_scale_energy(observed)
            errors.extend(abs(recovered[s] - truth[s]) for s in identifiable)
            q1, _ = np.linalg.qr(basis[:n, [i for i, s in enumerate((1, 4, 16)) if s in identifiable]])
            design = np.column_stack([((-1.) ** np.arange(n)) if s == 1 else np.sin(2*np.pi*np.arange(n)/s) for s in identifiable])
            q2, _ = np.linalg.qr(design)
            subspace.append(float(np.mean(np.linalg.svd(q1.T @ q2, compute_uv=False))))
        phase = rng.uniform(0, 2 * math.pi); t = np.arange(32)
        equivalent = np.sin(2 * np.pi * t / 2.4 + phase)
        alias = np.sin(2 * np.pi * t * (1 - 1 / 2.4) - phase)
        alias_a.append(float(np.max(np.abs(np.fft.rfft(equivalent)))))
        alias_b.append(float(np.max(np.abs(np.fft.rfft(alias)))))
    auc = alias_auc(np.asarray(alias_a), np.asarray(alias_b))
    return {"feature": "P9", "scale_energy_error": float(np.mean(errors)),
            "subspace_congruence": float(np.mean(subspace)), "alias_auc": auc,
            "alias_refusal": auc <= .55, "minimum_cycles": 4}


def generate_choice_world(rng: np.random.Generator, persons: int, length: int,
                          occupancy_matched_null: bool = False) -> dict[str, np.ndarray]:
    rows = []
    for person in range(persons):
        context = rng.integers(0, 2, length)
        transition = np.array([[.75, .20, .05], [.12, .70, .18], [.08, .22, .70]])
        transition = np.roll(transition, person % 3, axis=1)
        states = np.zeros(length, int); states[0] = rng.integers(0, 3)
        for t in range(1, length):
            probs = transition[states[t-1]].copy()
            probs = np.roll(probs, context[t]); probs /= probs.sum()
            states[t] = rng.choice(3, p=probs)
        if occupancy_matched_null:
            states = rng.permutation(states)
        rows.extend((person, t, int(context[t]), int(states[t])) for t in range(length))
    array = np.asarray(rows, int)
    return {"person": array[:, 0], "timestamp": array[:, 1], "context": array[:, 2], "choice": array[:, 3]}


def occupancy_preserving_shuffle(choice: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    return rng.permutation(np.asarray(choice))


def _transition_profile(states: np.ndarray, contexts: np.ndarray, classes: int = 3) -> np.ndarray:
    counts = np.ones((2, classes, classes))
    for t in range(1, len(states)): counts[contexts[t], states[t-1], states[t]] += 1
    return counts / counts.sum(axis=2, keepdims=True)


def evaluate_choice(data: dict[str, np.ndarray], train_fraction: float = .6) -> dict[str, float]:
    people = np.unique(data["person"]); gains, own_delta = [], []
    profiles: dict[int, tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
    for p in people:
        idx = np.flatnonzero(data["person"] == p)
        order = np.argsort(data["timestamp"][idx]); idx = idx[order]
        assert_timestamp_order(data["timestamp"][idx])
        split = int(len(idx) * train_fraction)
        middle = max(2, split // 2)
        tr_a, tr_b, tr, te = idx[:middle], idx[middle:split], idx[:split], idx[split-1:]
        # The class map is fixed from train labels only; unseen test labels are refused.
        labels = np.unique(data["choice"][tr]); class_map = {int(v): i for i, v in enumerate(labels)}
        if any(int(v) not in class_map for v in data["choice"][te]): continue
        train_states = np.array([class_map[int(v)] for v in data["choice"][tr]])
        test_states = np.array([class_map[int(v)] for v in data["choice"][te]])
        states_a = np.array([class_map[int(v)] for v in data["choice"][tr_a]])
        states_b = np.array([class_map[int(v)] for v in data["choice"][tr_b]])
        profile_a = _transition_profile(states_a, data["context"][tr_a], len(labels))
        profile_b = _transition_profile(states_b, data["context"][tr_b], len(labels))
        profile = _transition_profile(train_states, data["context"][tr], len(labels))
        occupancy = (np.bincount(train_states, minlength=len(labels)) + 1) / (len(train_states) + len(labels))
        support = np.r_[occupancy, np.mean(data["context"][tr])]
        profiles[int(p)] = (profile_a, profile_b, support)
        transition_score, occupancy_score = [], []
        for t in range(1, len(test_states)):
            transition_score.append(math.log(profile[data["context"][te][t], test_states[t-1], test_states[t]]))
            occupancy_score.append(math.log(occupancy[test_states[t]]))
        gains.append(np.mean(transition_score) - np.mean(occupancy_score))
    ids = sorted(profiles)
    for p in ids:
        others = [q for q in ids if q != p]
        profile_a, profile_b, support = profiles[p]
        stranger = min(others, key=lambda q: np.linalg.norm(profiles[q][2] - support))
        own_distance = np.linalg.norm(profile_a - profile_b)
        stranger_distance = np.linalg.norm(profile_a - profiles[stranger][1])
        own_delta.append(stranger_distance - own_distance)
    return {"logscore_gain": float(np.mean(gains)), "person_delta": float(np.mean(own_delta))}


def evaluate_p10(rng: np.random.Generator, cfg: dict[str, Any]) -> dict[str, Any]:
    gains, deltas, null_gains = [], [], []
    for _ in range(cfg["mc"]):
        result = evaluate_choice(generate_choice_world(rng, cfg["choice_persons"], cfg["choice_length"]))
        null = evaluate_choice(generate_choice_world(rng, cfg["choice_persons"], cfg["choice_length"], True))
        gains.append(result["logscore_gain"]); deltas.append(result["person_delta"]); null_gains.append(null["logscore_gain"])
    boot = [float(np.mean(rng.choice(deltas, len(deltas), replace=True))) for _ in range(cfg["bootstrap"])]
    return {"feature": "P10", "logscore_gain": float(np.mean(gains)),
            "null_logscore_gain": float(np.mean(null_gains)), "person_delta": float(np.mean(deltas)),
            "person_delta_ci": tuple(map(float, np.quantile(boot, [.025, .975]))),
            "gain_add_one_p": add_one_p(float(np.mean(gains)), null_gains)}


def run_extended(config: dict[str, Any], config_hash: str) -> dict[str, Any]:
    children = np.random.SeedSequence(config["seed"]).spawn(4)
    rows = [evaluate_p7(np.random.default_rng(children[0]), config),
            evaluate_p8(np.random.default_rng(children[1]), config),
            evaluate_p9(np.random.default_rng(children[2]), config),
            evaluate_p10(np.random.default_rng(children[3]), config)]
    by = {r["feature"]: r for r in rows}; full = config["profile"] == "full"
    gates = {
        "P7_fpr": by["P7"]["fpr"] <= .05 and by["P7"]["fpr_ci"][1] <= .10,
        "P7_power": by["P7"]["power_ci"][0] >= .80 if full else None,
        "P7_prediction": by["P7"]["heldout_likelihood_gain"] > 0 and by["P7"]["direction_stability"] >= .75,
        "P8_location": by["P8"]["location_error_windows"] <= 1,
        "P8_format_guard": by["P8"]["format_only_fpr"] <= .05 and by["P8"]["format_only_fpr_ci"][1] <= .10,
        "P9_scale": by["P9"]["scale_energy_error"] <= .10,
        "P9_alias": by["P9"]["alias_auc"] <= .55 and by["P9"]["alias_refusal"],
        "P10_choice": by["P10"]["logscore_gain"] > 0 and by["P10"]["person_delta"] >= .10 and by["P10"]["person_delta_ci"][0] > 0,
    }
    root = Path(__file__).resolve().parents[1]
    code_paths = [root / "suica_sim/extended_features.py", root / "scripts/run_v6_extended_features.py"]
    code_hash = hashlib.sha256(b"".join(p.read_bytes() for p in code_paths)).hexdigest()
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError): head = None
    return {"schema_version": 1, "profile": config["profile"], "diagnostic_only": not full,
            "seed": config["seed"], "config_hash": config_hash, "code_hash": code_hash,
            "git_head": head, "python_version": platform.python_version(), "numpy_version": np.__version__,
            "rows": rows, "gates": gates}


def load_extended_config(path: str | Path) -> tuple[dict[str, Any], str]:
    raw = Path(path).read_bytes(); return json.loads(raw), hashlib.sha256(raw).hexdigest()


def write_extended_reports(result: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    stem = f"v6_extended_features_{result['profile']}"
    paths = {k: out / f"{stem}.{ext}" for k, ext in (("json", "json"), ("csv", "csv"), ("markdown", "md"))}
    paths["json"].write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    fields = sorted({k for row in result["rows"] for k in row})
    with paths["csv"].open("w", newline="") as f:
        writer = csv.DictWriter(f, fields); writer.writeheader()
        for row in result["rows"]:
            writer.writerow({k: json.dumps(v) if isinstance(v, (dict, list, tuple)) else v for k, v in row.items()})
    lines = [f"# V6 extended features ({result['profile']})", "",
             f"Diagnostic only: **{result['diagnostic_only']}**",
             f"Config/code hash: `{result['config_hash']}` / `{result['code_hash']}`", "", "## Results", ""]
    lines += [f"- **{r['feature']}**: `{json.dumps(r, sort_keys=True)}`" for r in result["rows"]]
    lines += ["", "## Frozen gates", ""] + [f"- {k}: `{v}`" for k, v in result["gates"].items()]
    paths["markdown"].write_text("\n".join(lines) + "\n")
    return {k: str(v) for k, v in paths.items()}
