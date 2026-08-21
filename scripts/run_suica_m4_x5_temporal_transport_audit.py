#!/usr/bin/env python3
"""Post-closure temporal transport audit for the M4-X5 atlas.

The prospective protocol is frozen in
``docs/SUICA_CROSS_LEVEL_INFERENCE_CONTRACT.md`` at commit ``b0b38c2``.
This script does not alter the historical X5 verdicts. It asks whether the
registered average-within slopes and their cross-level transport families are
stable when the same author pool is observed at 2, 4, and 8 nested temporal
segments.

Only X5's gitignored metadata cache is read. Text bodies, questionnaire
labels, and per-author outputs are forbidden. Every written result is an
aggregate over a cohort.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
X5_SCRIPT = ROOT / "scripts/run_suica_m4_x5_ergodicity_atlas.py"
PROTOCOL = ROOT / "docs/SUICA_CROSS_LEVEL_INFERENCE_CONTRACT.md"
PROTOCOL_COMMIT = "b0b38c2"

DEFAULT_CACHE = ROOT / "results/m4_x5_ergodicity_atlas/event_cache.npz"
DEFAULT_X5_RESULTS = ROOT / "results/m4_x5_ergodicity_atlas"
DEFAULT_OUTPUT = ROOT / "results/m4_x5_temporal_transport_audit"
DEFAULT_REPORT = ROOT / "reports/SUICA_M4_X5_TEMPORAL_TRANSPORT_AUDIT.md"

K_VALUES = (2, 4, 8)
MASTER_K = 8
BASE_HALF_MIN_EVENTS = 50
BASE_HALF_DEN_FLOOR = 1.0
EQUIVALENCE_MARGIN = 0.02
MIN_AUTHORS = {"disjoint": 500, "big5": 150}
B_BOOT = 500
SEED = 20260822
REPRO_TOL = 1e-9

CLASS_EQUIV = "TEMPORALLY_EQUIVALENT_AT_0.02"
CLASS_HET = "TEMPORAL_HETEROGENEITY_DETECTED"
CLASS_UNRESOLVED = "TEMPORAL_HETEROGENEITY_UNRESOLVED"
CLASS_INSUFFICIENT = "INSUFFICIENT_SUPPORT"

FAMILY_SIGN_FLIP = "SIGN_FLIP"
FAMILY_SAME_SIGN = "SAME_SIGN_GAP"
FAMILY_SIGN_UNRESOLVED = "GAP_SIGN_UNRESOLVED"
FAMILY_GAP_UNRESOLVED = "GAP_UNRESOLVED"


def load_module(name: str, path: Path):
    """Load a frozen script by file so this audit binds its exact objects."""

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:  # pragma: no cover
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


X5 = load_module("suica_m4_x5_for_temporal_audit", X5_SCRIPT)


def write_json(path: Path, payload: Any) -> None:
    """Write stable aggregate JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )


def config_hash(config: dict[str, Any]) -> str:
    """Hash the frozen runtime configuration."""

    raw = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def segment_requirements(k: int) -> tuple[int, float]:
    """Scale X5's per-half floors over nested subsegments."""

    if k not in K_VALUES:
        raise ValueError(f"unsupported K={k}")
    per_half = k // 2
    min_events = int(math.ceil(BASE_HALF_MIN_EVENTS / per_half))
    den_floor = BASE_HALF_DEN_FLOOR / per_half
    return min_events, den_floor


def assign_master_segments(
    cache: dict[str, Any], usable: np.ndarray, master_k: int = MASTER_K
) -> np.ndarray:
    """Assign nested contiguous usable-event blocks inside each X5 half.

    The first ``master_k/2`` blocks partition the original early half and the
    remaining blocks partition the original late half. Coarser K values are
    exact unions of adjacent master blocks.
    """

    if master_k < 2 or master_k % 2:
        raise ValueError("master_k must be positive and even")
    usable = np.asarray(usable, dtype=bool)
    if usable.size != int(cache["offsets"][-1]):
        raise ValueError("usable mask length does not match the cache")
    per_half = master_k // 2
    segments = np.full(usable.size, -1, dtype=np.int16)
    for start, stop, n_early in zip(
        cache["offsets"][:-1], cache["offsets"][1:], cache["n_early"]
    ):
        start = int(start)
        stop = int(stop)
        middle = start + int(n_early)
        for half_id, (left, right) in enumerate(
            ((start, middle), (middle, stop))
        ):
            indices = np.flatnonzero(usable[left:right]) + left
            for local_segment, block in enumerate(
                np.array_split(indices, per_half)
            ):
                segments[block] = half_id * per_half + local_segment
    if np.any(segments[usable] < 0):  # pragma: no cover
        raise RuntimeError("a usable event was not assigned to a segment")
    return segments


def segment_moments(
    cache: dict[str, Any],
    relation: Any,
    who: np.ndarray,
    usable: np.ndarray,
    master_segments: np.ndarray,
    k: int,
) -> dict[str, np.ndarray]:
    """Compute two-pass per-(author, segment) sufficient statistics."""

    if MASTER_K % k:
        raise ValueError("K must be a divisor of MASTER_K")
    x_all = cache[f"ev_{relation.x}"]
    y_all = cache[f"ev_{relation.y}"]
    x = x_all[usable].astype(np.float64, copy=False)
    y = y_all[usable].astype(np.float64, copy=False)
    who_u = who[usable].astype(np.int64, copy=False)
    segment = (
        master_segments[usable].astype(np.int64, copy=False) // (MASTER_K // k)
    )
    n_authors = int(cache["n_total"].size)
    size = n_authors * k
    key = who_u * k + segment

    count = np.bincount(key, minlength=size).astype(np.float64)
    sx = np.bincount(key, weights=x, minlength=size)
    sy = np.bincount(key, weights=y, minlength=size)
    with np.errstate(invalid="ignore", divide="ignore"):
        mean_x = np.where(count > 0, sx / count, 0.0)
        mean_y = np.where(count > 0, sy / count, 0.0)
    dev_x = x - mean_x[key]
    dev_y = y - mean_y[key]
    den = np.bincount(key, weights=dev_x * dev_x, minlength=size)
    num = np.bincount(key, weights=dev_x * dev_y, minlength=size)

    shape = (n_authors, k)
    return {
        "n": count.reshape(shape),
        "sx": sx.reshape(shape),
        "sy": sy.reshape(shape),
        "den": den.reshape(shape),
        "num": num.reshape(shape),
    }


def eligible_at_master(moments: dict[str, np.ndarray]) -> np.ndarray:
    """The fixed K=8 author pool used at every temporal resolution."""

    min_events, den_floor = segment_requirements(MASTER_K)
    return np.all(
        (moments["n"] >= min_events) & (moments["den"] >= den_floor),
        axis=1,
    )


def original_pool(
    moments_k2: dict[str, np.ndarray], relation_key: str,
    cache: dict[str, Any] | None = None,
) -> np.ndarray:
    """Reconstruct the committed X4/X5 pool predicate for K=2.

    R1 deliberately binds X4's float-path-sensitive ``np.std(x) > 0`` mask.
    Replacing it with the algebraically cleaner ``den > 0`` changes the pool
    by a handful of near-degenerate authors and fails the reproduction gate.
    """

    count_ok = np.all(moments_k2["n"] >= BASE_HALF_MIN_EVENTS, axis=1)
    if relation_key == "R1":
        if cache is None:
            raise ValueError("R1 reproduction requires the frozen X4 cache mask")
        return X5.x4_pool_mask(cache)
    return count_ok & np.all(
        moments_k2["den"] >= BASE_HALF_DEN_FLOOR, axis=1
    )


def point_estimates(
    moments: dict[str, np.ndarray], select: np.ndarray
) -> dict[str, np.ndarray]:
    """Segment between, within, and transport-gap estimates."""

    n = moments["n"][select]
    sx = moments["sx"][select]
    sy = moments["sy"][select]
    den = moments["den"][select]
    num = moments["num"][select]
    if n.shape[0] < 2:
        raise ValueError("at least two authors are required")
    xbar = sx / n
    ybar = sy / n
    n_authors = float(n.shape[0])
    sum_x = xbar.sum(axis=0)
    sum_y = ybar.sum(axis=0)
    cov = (xbar * ybar).sum(axis=0) - sum_x * sum_y / n_authors
    var_x = (xbar * xbar).sum(axis=0) - sum_x * sum_x / n_authors
    between = cov / var_x
    within = num.sum(axis=0) / den.sum(axis=0)
    return {
        "between": between,
        "within": within,
        "delta": between - within,
        "xbar": xbar,
        "ybar": ybar,
        "num": num,
        "den": den,
    }


def bootstrap_estimates(
    estimates: dict[str, np.ndarray], b_boot: int, seed: int
) -> dict[str, np.ndarray]:
    """Paired author-cluster bootstrap for every temporal segment."""

    xbar = estimates["xbar"]
    ybar = estimates["ybar"]
    num = estimates["num"]
    den = estimates["den"]
    n_authors, k = xbar.shape
    rng = np.random.default_rng(seed)
    between = np.empty((b_boot, k), dtype=np.float64)
    within = np.empty((b_boot, k), dtype=np.float64)
    block = 25
    for start in range(0, b_boot, block):
        rows = min(block, b_boot - start)
        indices = rng.integers(0, n_authors, size=(rows, n_authors))
        for segment in range(k):
            bx = xbar[:, segment][indices]
            by = ybar[:, segment][indices]
            sum_x = bx.sum(axis=1)
            sum_y = by.sum(axis=1)
            cov = (bx * by).sum(axis=1) - sum_x * sum_y / n_authors
            var_x = (bx * bx).sum(axis=1) - sum_x * sum_x / n_authors
            between[start : start + rows, segment] = cov / var_x
            within[start : start + rows, segment] = (
                num[:, segment][indices].sum(axis=1)
                / den[:, segment][indices].sum(axis=1)
            )
    return {"between": between, "within": within, "delta": between - within}


def percentile_columns(values: np.ndarray) -> np.ndarray:
    """Pointwise 95% intervals, one row per column."""

    return np.percentile(values, [2.5, 97.5], axis=0).T


def simultaneous_contrast_intervals(
    point_within: np.ndarray, boot_within: np.ndarray
) -> dict[str, Any]:
    """Familywise max-|t| intervals for segment-to-mean contrasts."""

    point = point_within - np.mean(point_within)
    boot = boot_within - np.mean(boot_within, axis=1, keepdims=True)
    se = np.std(boot, axis=0, ddof=1)
    safe = np.where(se > 0, se, np.inf)
    max_t = np.max(np.abs((boot - point) / safe), axis=1)
    critical = float(np.percentile(max_t, 95.0))
    lower = point - critical * se
    upper = point + critical * se
    intervals = np.column_stack((lower, upper))
    return {
        "contrast": point,
        "se": se,
        "critical": critical,
        "intervals": intervals,
    }


def temporal_classification(
    simultaneous: dict[str, Any], margin: float = EQUIVALENCE_MARGIN
) -> str:
    """Apply the registered temporal heterogeneity/equivalence rules."""

    contrast = np.asarray(simultaneous["contrast"])
    intervals = np.asarray(simultaneous["intervals"])
    equivalent = bool(
        np.all(intervals[:, 0] >= -margin)
        and np.all(intervals[:, 1] <= margin)
    )
    detected = bool(
        np.any(
            ((intervals[:, 0] > 0.0) | (intervals[:, 1] < 0.0))
            & (np.abs(contrast) > margin)
        )
    )
    if equivalent:
        return CLASS_EQUIV
    if detected:
        return CLASS_HET
    return CLASS_UNRESOLVED


def interval_excludes_zero(interval: Sequence[float]) -> bool:
    """Whether a closed interval excludes zero."""

    return bool(interval[0] > 0.0 or interval[1] < 0.0)


def transport_family(
    beta_between: float,
    beta_within: float,
    beta_between_ci: Sequence[float],
    beta_within_ci: Sequence[float],
    delta_ci: Sequence[float],
) -> str:
    """Map one segment to the registered coarse transport family."""

    if not interval_excludes_zero(delta_ci):
        return FAMILY_GAP_UNRESOLVED
    between_detected = interval_excludes_zero(beta_between_ci)
    within_detected = interval_excludes_zero(beta_within_ci)
    if not (between_detected and within_detected):
        return FAMILY_SIGN_UNRESOLVED
    if np.sign(beta_between) != np.sign(beta_within):
        return FAMILY_SIGN_FLIP
    return FAMILY_SAME_SIGN


def historical_family(cell: str) -> str:
    """Coarsen an immutable X5 cell label without rewriting the artifact."""

    mapping = {
        "NONERGODIC_SIGN_FLIP": FAMILY_SIGN_FLIP,
        "NONERGODIC_SAME_SIGN": FAMILY_SAME_SIGN,
        "NONERGODIC_SIGN_UNRESOLVED": FAMILY_SIGN_UNRESOLVED,
        "LEVELS_INDISTINGUISHABLE": FAMILY_GAP_UNRESOLVED,
    }
    if cell not in mapping:
        raise ValueError(f"unknown historical X5 cell: {cell}")
    return mapping[cell]


def trend_statistics(within: np.ndarray) -> tuple[float, float]:
    """Registered raw and normalized event-order segment trends."""

    z = np.linspace(-1.0, 1.0, len(within))
    raw = float(np.sum(z * (within - np.mean(within))) / np.sum(z * z))
    normalized = raw / max(abs(float(np.mean(within))), EQUIVALENCE_MARGIN)
    return raw, normalized


def drift_energy_decomposition(
    between: Sequence[float], within: Sequence[float]
) -> dict[str, float]:
    """Decompose centered transport-gap drift without assigning a construct.

    For centered segment paths ``b`` and ``w``, the centered transport gap is
    ``d = b - w``. Its squared path energy therefore has the exact identity
    ``||d||^2 = ||b||^2 + ||w||^2 - 2<b,w>``. The cross term can cancel or
    amplify the two marginal paths, so the components are not variance shares
    and need not lie in ``[0, 1]`` after normalization.
    """

    between_array = np.asarray(between, dtype=np.float64)
    within_array = np.asarray(within, dtype=np.float64)
    if between_array.shape != within_array.shape or between_array.ndim != 1:
        raise ValueError("between and within must be equal-length vectors")
    if between_array.size < 2:
        raise ValueError("at least two temporal segments are required")
    b = between_array - np.mean(between_array)
    w = within_array - np.mean(within_array)
    d = b - w
    energy_between = float(np.dot(b, b))
    energy_within = float(np.dot(w, w))
    cross_term = float(-2.0 * np.dot(b, w))
    energy_transport = float(np.dot(d, d))
    identity_error = abs(
        energy_transport - (energy_between + energy_within + cross_term)
    )
    if energy_transport > 0.0:
        normalized = {
            "between_energy_ratio": energy_between / energy_transport,
            "within_energy_ratio": energy_within / energy_transport,
            "cross_energy_ratio": cross_term / energy_transport,
        }
    else:
        normalized = {
            "between_energy_ratio": float("nan"),
            "within_energy_ratio": float("nan"),
            "cross_energy_ratio": float("nan"),
        }
    return {
        "between_range": float(np.ptp(between_array)),
        "within_range": float(np.ptp(within_array)),
        "transport_gap_range": float(np.ptp(between_array - within_array)),
        "between_energy": energy_between,
        "within_energy": energy_within,
        "cross_energy": cross_term,
        "transport_gap_energy": energy_transport,
        "identity_error": identity_error,
        "between_within_path_correlation": float(
            np.corrcoef(between_array, within_array)[0, 1]
        ),
        **normalized,
    }


def sign_sequence(values: np.ndarray) -> str:
    """Compact segment sign sequence."""

    return "".join("+" if value > 0 else "-" if value < 0 else "0" for value in values)


def reproduction_rows(
    cache: dict[str, Any],
    who: np.ndarray,
    arms: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, np.ndarray]]]:
    """Reproduce every committed K=2 early/late within-person slope."""

    rows: list[dict[str, Any]] = []
    prepared: dict[str, dict[str, np.ndarray]] = {}
    is_big5 = cache["pool_is_big5"].astype(bool)
    for relation in X5.RELATIONS:
        x = cache[f"ev_{relation.x}"]
        y = cache[f"ev_{relation.y}"]
        usable = np.isfinite(x) & np.isfinite(y)
        segments = assign_master_segments(cache, usable)
        moments2 = segment_moments(
            cache, relation, who, usable, segments, 2
        )
        pool = original_pool(moments2, relation.key, cache)
        prepared[relation.key] = {
            "usable": usable,
            "segments": segments,
        }
        for cohort in ("disjoint", "big5"):
            select = pool & (is_big5 if cohort == "big5" else ~is_big5)
            observed = point_estimates(moments2, select)["within"]
            expected = np.array(
                [
                    arms[f"{relation.key}:{cohort}"]["beta_within_early"],
                    arms[f"{relation.key}:{cohort}"]["beta_within_late"],
                ],
                dtype=np.float64,
            )
            error = np.abs(observed - expected)
            rows.append(
                {
                    "relation": relation.key,
                    "cohort": cohort,
                    "authors": int(select.sum()),
                    "observed_early": float(observed[0]),
                    "expected_early": float(expected[0]),
                    "observed_late": float(observed[1]),
                    "expected_late": float(expected[1]),
                    "max_abs_error": float(np.max(error)),
                    "status": "PASS" if float(np.max(error)) <= REPRO_TOL else "FAIL",
                }
            )
    return rows, prepared


def table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    """Render a compact Markdown table."""

    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def fmt(value: float, digits: int = 4) -> str:
    """Finite numeric formatter."""

    return f"{value:+.{digits}f}" if np.isfinite(value) else "NA"


def format_counts(counts: dict[str, int]) -> str:
    """Render a deterministic compact count map for Markdown."""

    return "; ".join(f"{key}={counts[key]}" for key in sorted(counts))


def write_report(
    path: Path,
    config: dict[str, Any],
    reproduction: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
    segments: list[dict[str, Any]],
    drift_rows: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    """Write the aggregate post-closure audit report."""

    repro_rows = [
        [
            row["relation"],
            row["cohort"],
            row["authors"],
            f"{row['max_abs_error']:.3e}",
            row["status"],
        ]
        for row in reproduction
    ]
    class_rows = [
        [
            row["relation"],
            row["cohort"],
            row["k"],
            row["authors"],
            row["temporal_class"],
            row["within_sign_sequence"],
            row["historical_family"],
            "yes" if row["all_segments_match_historical_family"] else "no",
            fmt(row["raw_time_trend"]),
        ]
        for row in classifications
    ]
    segment_rows = [
        [
            row["relation"],
            row["cohort"],
            row["k"],
            row["segment"],
            fmt(row["beta_between"]),
            fmt(row["beta_within"]),
            fmt(row["delta_transport"]),
            row["transport_family"],
        ]
        for row in segments
        if row["k"] == MASTER_K
    ]
    finest_rows = [
        [
            cohort,
            format_counts(
                summary["finest_resolution"][cohort]["temporal_class_counts"]
            ),
            summary["finest_resolution"][cohort][
                "all_segments_match_historical"
            ],
            summary["finest_resolution"][cohort]["arms"],
        ]
        for cohort in ("disjoint", "big5")
    ]
    drift_table_rows = [
        [
            row["relation"],
            row["cohort"],
            fmt(row["between_range"]),
            fmt(row["within_range"]),
            fmt(row["transport_gap_range"]),
            fmt(row["between_within_path_correlation"]),
            f"{row['between_energy_ratio']:.2f}",
            f"{row['within_energy_ratio']:.2f}",
            f"{row['cross_energy_ratio']:.2f}",
        ]
        for row in drift_rows
    ]
    text = "\n".join(
        [
            "# SUICA M4-X5-T Temporal Transport Audit",
            "",
            f"**VERDICT: `{summary['verdict']}`.** This is a post-closure "
            "diagnostic of projection stability, not a rewrite of X5 and not "
            "a psychological claim.",
            "",
            f"Protocol commit: `{PROTOCOL_COMMIT}`. Seed {config['seed']}; "
            f"B_boot={config['b_boot']}; K={config['k_values']}; "
            f"configuration sha256 `{config['sha256'][:16]}...`.",
            "",
            "## Reproduction gate",
            "",
            table(
                ["relation", "cohort", "authors", "max abs error", "status"],
                repro_rows,
            ),
            "",
            "Every committed K=2 early/late within-person slope must reproduce "
            "before multisegment estimates are licensed.",
            "",
            "## Finest-resolution decision view",
            "",
            table(
                [
                    "cohort",
                    "K=8 within-slope classes",
                    "all 8 segment families match X5",
                    "relations",
                ],
                finest_rows,
            ),
            "",
            "K=2/4/8 are nested views of the same authors and events, not "
            "independent replications. The table above is therefore the main "
            "resolution-specific reading; the full table below is a sensitivity "
            "path.",
            "",
            "## Temporal classifications",
            "",
            table(
                [
                    "relation",
                    "cohort",
                    "K",
                    "authors",
                    "within-slope temporal class",
                    "signs",
                    "historical family",
                    "all segment families match",
                    "raw trend",
                ],
                class_rows,
            ),
            "",
            "## K=8 segment transport map",
            "",
            table(
                [
                    "relation",
                    "cohort",
                    "K",
                    "segment",
                    "beta_B",
                    "beta_W",
                    "Delta_T",
                    "family",
                ],
                segment_rows,
            ),
            "",
            "## Exploratory drift-energy decomposition",
            "",
            "This post-registered mechanism readout does not change the temporal "
            "classification. For centered K=8 paths, let "
            "`b=beta_B-mean(beta_B)` and `w=beta_W-mean(beta_W)`. Then "
            "`||b-w||^2 = ||b||^2 + ||w||^2 - 2<b,w>`. Ratios can be negative "
            "or exceed one because the cross term records cancellation or "
            "amplification; they are not variance shares.",
            "",
            table(
                [
                    "relation",
                    "cohort",
                    "range beta_B",
                    "range beta_W",
                    "range Delta_T",
                    "corr paths",
                    "B/E_D",
                    "W/E_D",
                    "cross/E_D",
                ],
                drift_table_rows,
            ),
            "",
            "The decomposition distinguishes two gates that the old wording "
            "compressed: temporal persistence of the average within-person "
            "response and temporal persistence of the cross-level transport "
            "family. Either can hold while the other changes.",
            "",
            "## Reading boundary",
            "",
            "- `TEMPORAL_HETEROGENEITY_DETECTED` means the X5 aggregate "
            "within-person slope is a horizon average. It is not personality "
            "change.",
            "- `TEMPORALLY_EQUIVALENT_AT_0.02` is equivalence only for this "
            "projection, pool, horizon, and nested partition family.",
            "- Segments are equal usable-event-count blocks, so every reported "
            "trend is an event-order trend, not a calendar-time trend. Boundaries "
            "can differ across relations when their usable events differ.",
            "- Segment family changes narrow the cross-level transport claim; "
            "they do not invalidate the observed aggregate relation. Family "
            "retention uses pointwise intervals and is descriptive, not a second "
            "familywise test.",
            "- Metadata only, aggregate only, no text bodies, no external "
            "labels, no person-level output.",
            "",
            "## Files",
            "",
            "- `results/m4_x5_temporal_transport_audit/reproduction.json`",
            "- `results/m4_x5_temporal_transport_audit/summary.json`",
            "- `results/m4_x5_temporal_transport_audit/temporal_classifications.csv`",
            "- `results/m4_x5_temporal_transport_audit/segment_estimates.csv`",
            "- `results/m4_x5_temporal_transport_audit/drift_decomposition.csv`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the registered audit and write aggregate artifacts."""

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    cache, meta = X5.load_cache(Path(args.cache))
    arms = json.loads((Path(args.x5_results) / "arms.json").read_text("utf-8"))
    cells = json.loads((Path(args.x5_results) / "cells.json").read_text("utf-8"))

    config = {
        "protocol": str(PROTOCOL),
        "protocol_commit": PROTOCOL_COMMIT,
        "cache": str(args.cache),
        "x5_results": str(args.x5_results),
        "k_values": list(K_VALUES),
        "master_k": MASTER_K,
        "base_half_min_events": BASE_HALF_MIN_EVENTS,
        "base_half_den_floor": BASE_HALF_DEN_FLOOR,
        "equivalence_margin": EQUIVALENCE_MARGIN,
        "min_authors": MIN_AUTHORS,
        "b_boot": int(args.b_boot),
        "seed": int(args.seed),
        "reproduction_tolerance": REPRO_TOL,
        "metadata_only": True,
        "labels_opened": False,
        "text_bodies_opened": False,
    }
    config["sha256"] = config_hash(config)
    write_json(output / "config.json", config)

    anchors = {
        "cache_version": int(meta["cache_version"]),
        "candidate_authors": int(cache["n_total"].size),
        "cached_events": int(cache["offsets"][-1]),
        "relations": [relation.key for relation in X5.RELATIONS],
        "status": "PASS",
    }
    if anchors["candidate_authors"] != 9124 or anchors["cached_events"] != 17577863:
        anchors["status"] = "FAIL"
    write_json(output / "anchors.json", anchors)
    if anchors["status"] != "PASS":
        raise SystemExit("STOP: X5 cache anchors do not match the registered cache")

    who, _ = X5.event_author_and_half(cache)
    reproduction, prepared = reproduction_rows(cache, who, arms)
    write_json(output / "reproduction.json", reproduction)
    if not all(row["status"] == "PASS" for row in reproduction):
        raise SystemExit("STOP: K=2 reproduction gate failed")
    if args.stop_after_reproduction:
        return {"status": "REPRODUCTION_ONLY_PASS", "reproduction": reproduction}

    is_big5 = cache["pool_is_big5"].astype(bool)
    classifications: list[dict[str, Any]] = []
    segment_rows: list[dict[str, Any]] = []
    support_rows: list[dict[str, Any]] = []

    for relation_index, relation in enumerate(X5.RELATIONS):
        usable = prepared[relation.key]["usable"]
        segments8 = prepared[relation.key]["segments"]
        moments8 = segment_moments(cache, relation, who, usable, segments8, 8)
        master_pool = eligible_at_master(moments8)
        moments_by_k = {8: moments8}
        for k in (2, 4):
            moments_by_k[k] = segment_moments(
                cache, relation, who, usable, segments8, k
            )

        for cohort_index, cohort in enumerate(("disjoint", "big5")):
            select = master_pool & (is_big5 if cohort == "big5" else ~is_big5)
            n_authors = int(select.sum())
            support_rows.append(
                {
                    "relation": relation.key,
                    "cohort": cohort,
                    "authors": n_authors,
                    "events": int(moments8["n"][select].sum()),
                    "minimum": MIN_AUTHORS[cohort],
                    "status": "PASS" if n_authors >= MIN_AUTHORS[cohort] else CLASS_INSUFFICIENT,
                }
            )
            historical_cell = cells[f"{relation.key}:{cohort}"]["delta_cell"]
            old_family = historical_family(historical_cell)
            for k in K_VALUES:
                if n_authors < MIN_AUTHORS[cohort]:
                    classifications.append(
                        {
                            "relation": relation.key,
                            "cohort": cohort,
                            "k": k,
                            "authors": n_authors,
                            "events": int(moments_by_k[k]["n"][select].sum()),
                            "temporal_class": CLASS_INSUFFICIENT,
                            "within_sign_sequence": "",
                            "historical_cell": historical_cell,
                            "historical_family": old_family,
                            "all_segments_match_historical_family": False,
                            "raw_time_trend": float("nan"),
                            "normalized_time_trend": float("nan"),
                        }
                    )
                    continue

                point = point_estimates(moments_by_k[k], select)
                boot = bootstrap_estimates(
                    point,
                    int(args.b_boot),
                    int(args.seed) + 10000 * relation_index + 1000 * cohort_index + k,
                )
                ci_between = percentile_columns(boot["between"])
                ci_within = percentile_columns(boot["within"])
                ci_delta = percentile_columns(boot["delta"])
                simultaneous = simultaneous_contrast_intervals(
                    point["within"], boot["within"]
                )
                temporal_class = temporal_classification(simultaneous)
                raw_trend, normalized_trend = trend_statistics(point["within"])
                families: list[str] = []
                for segment in range(k):
                    family = transport_family(
                        float(point["between"][segment]),
                        float(point["within"][segment]),
                        ci_between[segment],
                        ci_within[segment],
                        ci_delta[segment],
                    )
                    families.append(family)
                    segment_rows.append(
                        {
                            "relation": relation.key,
                            "cohort": cohort,
                            "k": k,
                            "segment": segment + 1,
                            "authors": n_authors,
                            "beta_between": float(point["between"][segment]),
                            "beta_between_ci_lo": float(ci_between[segment, 0]),
                            "beta_between_ci_hi": float(ci_between[segment, 1]),
                            "beta_within": float(point["within"][segment]),
                            "beta_within_ci_lo": float(ci_within[segment, 0]),
                            "beta_within_ci_hi": float(ci_within[segment, 1]),
                            "delta_transport": float(point["delta"][segment]),
                            "delta_ci_lo": float(ci_delta[segment, 0]),
                            "delta_ci_hi": float(ci_delta[segment, 1]),
                            "within_contrast": float(simultaneous["contrast"][segment]),
                            "within_simultaneous_ci_lo": float(simultaneous["intervals"][segment, 0]),
                            "within_simultaneous_ci_hi": float(simultaneous["intervals"][segment, 1]),
                            "transport_family": family,
                        }
                    )
                classifications.append(
                    {
                        "relation": relation.key,
                        "cohort": cohort,
                        "k": k,
                        "authors": n_authors,
                        "events": int(moments_by_k[k]["n"][select].sum()),
                        "temporal_class": temporal_class,
                        "within_sign_sequence": sign_sequence(point["within"]),
                        "historical_cell": historical_cell,
                        "historical_family": old_family,
                        "segment_families": "/".join(families),
                        "all_segments_match_historical_family": bool(
                            all(family == old_family for family in families)
                        ),
                        "raw_time_trend": raw_trend,
                        "normalized_time_trend": normalized_trend,
                        "max_abs_within_contrast": float(
                            np.max(np.abs(simultaneous["contrast"]))
                        ),
                        "max_t_critical": float(simultaneous["critical"]),
                    }
                )

    classifications_df = pd.DataFrame(classifications)
    segments_df = pd.DataFrame(segment_rows)
    support_df = pd.DataFrame(support_rows)
    classifications_df.to_csv(output / "temporal_classifications.csv", index=False)
    segments_df.to_csv(output / "segment_estimates.csv", index=False)
    support_df.to_csv(output / "support.csv", index=False)

    drift_rows: list[dict[str, Any]] = []
    finest_segments = segments_df[segments_df["k"] == MASTER_K]
    for (relation, cohort), group in finest_segments.groupby(
        ["relation", "cohort"], sort=True
    ):
        values = group.sort_values("segment")
        drift_rows.append(
            {
                "relation": relation,
                "cohort": cohort,
                "k": MASTER_K,
                **drift_energy_decomposition(
                    values["beta_between"].to_numpy(),
                    values["beta_within"].to_numpy(),
                ),
            }
        )
    drift_df = pd.DataFrame(drift_rows)
    drift_df.to_csv(output / "drift_decomposition.csv", index=False)

    primary = classifications_df[classifications_df["cohort"] == "disjoint"]
    finest_resolution: dict[str, Any] = {}
    for cohort in ("disjoint", "big5"):
        cohort_finest = classifications_df[
            (classifications_df["cohort"] == cohort)
            & (classifications_df["k"] == MASTER_K)
        ]
        finest_resolution[cohort] = {
            "temporal_class_counts": cohort_finest["temporal_class"]
            .value_counts()
            .to_dict(),
            "all_segments_match_historical": int(
                cohort_finest["all_segments_match_historical_family"].sum()
            ),
            "arms": int(len(cohort_finest)),
        }
    summary = {
        "verdict": "POST_CLOSURE_TEMPORAL_DIAGNOSTIC_COMPLETE",
        "reproduction_gate": "PASS",
        "support_gate": "PASS" if (support_df["status"] == "PASS").all() else "PARTIAL",
        "primary_temporal_class_counts": primary["temporal_class"].value_counts().to_dict(),
        "primary_all_segments_match_historical": int(
            primary["all_segments_match_historical_family"].sum()
        ),
        "primary_arms": int(len(primary)),
        "primary_counts_are_nested_not_independent": True,
        "finest_resolution": finest_resolution,
        "metadata_only": True,
        "labels_opened": False,
        "text_bodies_opened": False,
    }
    write_json(output / "summary.json", summary)
    write_report(
        Path(args.report),
        config,
        reproduction,
        classifications,
        segment_rows,
        drift_rows,
        summary,
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """CLI parser."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--x5-results", type=Path, default=DEFAULT_X5_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--b-boot", type=int, default=B_BOOT)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--stop-after-reproduction", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line entry point."""

    args = build_parser().parse_args(argv)
    summary = run(args)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
