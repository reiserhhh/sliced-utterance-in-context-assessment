#!/usr/bin/env python3
"""M4-E1 — convention gap on real-text relation fields.

Opened-panel adaptive chain, exploratory. Registered spec:
docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md section M4-E1; knob
substitution register-noted in reports/SUICA_M4_E1_CONVENTION_GAP_REPORT.md
Part 0 BEFORE this run.

The deployed V8 soft relation-field estimator is penalty-free; the substituted
convention knob (registered) is the module's own whitened relation estimator in
the full soft-projected space: J_c(lambda) = W_M(lambda) C_c W_K(lambda) with
W_F(lambda) = _inverse_sqrt(Sigma_F, ridge=lambda) on the pooled opened D1+D2
panel. Convention (i): lambda = 1e-5 fixed (module default, V2 semantics).
Convention (ii): lambda ~ 1/n anchored at the 1/4 event budget.

Label-free throughout: PANDORA via the existing V8 loader on the frozen
tier_u_comments.parquet (author/body/created_utc/subreddit only); Essays read
text-only (usecols user_id,text — the V6-E2 precedent). No label columns.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import suica_core.v8_realtext_relation_field as v8  # noqa: E402

BANNER = "opened-panel adaptive chain, exploratory"
MASTER_SEED = 20260802
BUDGET_FRACTIONS = (0.25, 0.5, 1.0)
SPLIT_DRAWS = 24
LAMBDA_DEFAULT = 1e-5  # must equal the module spec.ridge default (asserted).
MIN_HALVABLE_EVENTS = 8  # each half needs >= 4 events -> paths >= 2.
MATCHED_MIN_FULL_EVENTS = 14  # b(1/2) >= 8 <=> m >= 14 (even m from loader).
DEFAULT_CONFIG = ROOT / "configs" / "v8_realtext_relation_field.json"
PERSISTED_SCHEMA = (
    ROOT / "results" / "v8_realtext_relation_field" / "discovery_20260805"
    / "data_schema.json"
)
DEFAULT_OUTPUT = ROOT / "results" / "m4_e1_convention_gap"

# ---------------------------------------------------------------------------
# Runtime memoization of the frozen event vectorizer (bit-identical outputs;
# subsampling and split-halves re-consume the same texts many times).
_VECTOR_CACHE: dict[tuple[str, int], np.ndarray] = {}
_ORIGINAL_VECTOR = v8.frozen_event_vector


def _cached_event_vector(text: str, *, dimensions: int = 32) -> np.ndarray:
    key = (str(text or ""), int(dimensions))
    found = _VECTOR_CACHE.get(key)
    if found is None:
        found = _ORIGINAL_VECTOR(key[0], dimensions=dimensions)
        _VECTOR_CACHE[key] = found
    return found


v8.frozen_event_vector = _cached_event_vector


def _load_v8_script() -> Any:
    """Import the V8 realtext script module for its label-free loaders."""
    path = ROOT / "scripts" / "run_suica_v8_realtext_relation_field.py"
    spec = importlib.util.spec_from_file_location("v8rt_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Event-budget subsampling: author-stratified, seeded, nested.

def _budget_size(m: int, fraction: float) -> int:
    return int(min(m, max(4, 2 * int(fraction * m / 2 + 0.5))))


def subsample_budget(
    events: pd.DataFrame,
    *,
    corpus: str,
    fraction: float,
) -> pd.DataFrame:
    """Keep b(fraction) events per author; nested via one shared permutation."""
    pieces = []
    for author, group in events.groupby("author_id", observed=True, sort=False):
        group = group.sort_values("order", kind="stable")
        m = len(group)
        b = _budget_size(m, fraction)
        rng = np.random.default_rng(
            v8.stable_bucket(
                f"{corpus}-{author}",
                salt="m4e1-budget-perm",
                modulus=2**31 - 1,
            )
        )
        keep = np.sort(rng.permutation(m)[:b])
        sub = group.iloc[keep].copy()
        sub["order"] = np.arange(len(sub))
        pieces.append(sub)
    return pd.concat(pieces, ignore_index=True)


def split_half_frames(
    budget_events: pd.DataFrame,
    *,
    corpus: str,
    budget_label: str,
    draw: int,
    retained_authors: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Randomly halve each retained author's budgeted events (time order kept)."""
    pieces_a, pieces_b = [], []
    for author, group in budget_events.groupby(
        "author_id", observed=True, sort=False
    ):
        if str(author) not in retained_authors:
            continue
        group = group.sort_values("order", kind="stable")
        b = len(group)
        if b < MIN_HALVABLE_EVENTS:
            continue
        rng = np.random.default_rng(
            v8.stable_bucket(
                f"{corpus}-{author}-{budget_label}-{draw}",
                salt="m4e1-half-perm",
                modulus=2**31 - 1,
            )
        )
        perm = rng.permutation(b)
        half = b // 2
        for keep, pieces in (
            (np.sort(perm[:half]), pieces_a),
            (np.sort(perm[half:]), pieces_b),
        ):
            sub = group.iloc[keep].copy()
            sub["order"] = np.arange(len(sub))
            pieces.append(sub)
    return (
        pd.concat(pieces_a, ignore_index=True),
        pd.concat(pieces_b, ignore_index=True),
    )


# ---------------------------------------------------------------------------
# Field estimation (registered substituted knob) on top of the frozen map.

def calibrate_d0_soft(panel: v8.CorpusFeaturePanel) -> dict[str, SimpleNamespace]:
    """Per-budget D0-frozen soft calibration (deployed representation)."""
    d0 = panel.metadata["split"].eq("D0").to_numpy()
    if int(d0.sum()) < 24:
        raise ValueError(f"Only {int(d0.sum())} D0 authors at this budget.")
    calibration = {}
    for family in v8.FAMILY_NAMES:
        raw = panel.raw[family][d0]
        center, scale = v8._fit_standardizer(raw)
        standardized = v8._standardize(raw, center, scale)
        covariance = v8.replicated_covariance(
            standardized[:, 0], standardized[:, 1]
        )
        density, _positive, effective_rank = v8._positive_density(covariance)
        calibration[family] = SimpleNamespace(
            center=center,
            scale=scale,
            soft_filter=v8._density_sqrt(density),
            effective_rank=float(effective_rank),
        )
    return calibration


def project_soft(
    panel: v8.CorpusFeaturePanel,
    mask: np.ndarray,
    calibration: dict[str, SimpleNamespace],
) -> dict[str, np.ndarray]:
    out = {}
    for family in v8.FAMILY_NAMES:
        cal = calibration[family]
        standardized = v8._standardize(panel.raw[family][mask], cal.center, cal.scale)
        out[family] = np.einsum("nrd,dk->nrk", standardized, cal.soft_filter)
    return out


def whitened_field(
    projected: dict[str, np.ndarray],
    contexts: np.ndarray,
    resolved: list[str],
    lam: float,
) -> tuple[dict[str, np.ndarray], dict[str, float], dict[str, Any]]:
    """J_c(lambda) = W_M C_c W_K with pooled-panel whiteners (module algebra)."""
    sigma = {
        family: v8.replicated_covariance(
            projected[family][:, 0], projected[family][:, 1]
        )
        for family in v8.FAMILY_NAMES
    }
    whitener = {
        family: v8._inverse_sqrt(sigma[family], ridge=lam)
        for family in v8.FAMILY_NAMES
    }
    diagnostics = {}
    for family in v8.FAMILY_NAMES:
        values = np.linalg.eigvalsh(0.5 * (sigma[family] + sigma[family].T))
        top = float(np.max(values))
        diagnostics[family] = {
            "dim": int(len(values)),
            "lambda_max": top,
            "n_negative": int(np.sum(values < 0)),
            "n_below_floor": int(np.sum(values < lam * top)),
        }
    total = max(1, len(contexts))
    fields, weights = {}, {}
    for context in resolved:
        mask = contexts == context
        cross = v8._soft_cross_covariance(
            projected["M"][mask], projected["K"][mask]
        )
        fields[str(context)] = whitener["M"] @ cross @ whitener["K"]
        weights[str(context)] = float(mask.sum() / total)
    return fields, weights, diagnostics


def deployed_soft_field(
    projected: dict[str, np.ndarray],
    contexts: np.ndarray,
    resolved: list[str],
) -> dict[str, np.ndarray]:
    """The deployed penalty-free estimator (reference row, outside the leans)."""
    fields = {}
    for context in resolved:
        mask = contexts == context
        fields[str(context)] = v8.soft_relation_matrix(
            projected["M"][mask], projected["K"][mask]
        )
    return fields


def field_agreement(
    first: dict[str, np.ndarray],
    second: dict[str, np.ndarray],
    weights: dict[str, float],
) -> float:
    if set(first) != set(second) or not first:
        raise ValueError("Field context sets differ or are empty.")
    total = sum(weights[c] for c in first)
    return float(
        sum(
            weights[c] * v8._matrix_cosine(first[c], second[c])
            for c in first
        )
        / max(total, 1e-12)
    )


# ---------------------------------------------------------------------------

def resolved_contexts(
    metadata: pd.DataFrame,
    floor: int,
) -> list[str]:
    counts = metadata["context"].astype(str).value_counts()
    return sorted(str(c) for c, n in counts.items() if int(n) >= floor)


def build_panel(
    frame: pd.DataFrame,
    *,
    corpus: str,
    schema: dict[str, Any],
    spec: v8.RealTextRelationSpec,
) -> v8.CorpusFeaturePanel:
    return v8.build_feature_panel(
        frame,
        corpus=corpus,
        context_role=schema["context_role"],
        replicate_type=schema["replicate_type"],
        spec=spec,
    )


def run_corpus(
    *,
    corpus: str,
    loader: Any,
    data_config: dict[str, Any],
    spec: v8.RealTextRelationSpec,
    persisted: dict[str, Any] | None,
    draws: int,
) -> dict[str, Any]:
    started = time.time()
    events, schema = loader(data_config)
    gates = {}
    if persisted is not None:
        gates["panel_authors_match"] = bool(
            schema["authors"] == persisted["authors"]
        )
        gates["panel_events_match"] = bool(schema["events"] == persisted["events"])
        if not (gates["panel_authors_match"] and gates["panel_events_match"]):
            raise AssertionError(
                f"{corpus}: rebuilt panel ({schema['authors']} authors, "
                f"{schema['events']} events) != persisted V8 panel "
                f"({persisted['authors']}, {persisted['events']})."
            )
    author_events = events.groupby("author_id", observed=True).size()
    total_events = int(author_events.sum())

    budget_frames = {
        fraction: subsample_budget(events, corpus=corpus, fraction=fraction)
        for fraction in BUDGET_FRACTIONS
    }
    # Gate 2: the full budget must be the identity subsample.
    full = budget_frames[1.0]
    if len(full) != len(events) or not (
        full["author_id"].to_numpy() == events["author_id"].to_numpy()
    ).all() or not (full["text"].to_numpy() == events["text"].to_numpy()).all():
        raise AssertionError(f"{corpus}: full-budget subsample is not identity.")
    gates["full_budget_identity"] = True

    gap_rows: list[dict[str, Any]] = []
    internal_rows: list[dict[str, Any]] = []
    diagnostic_rows: list[dict[str, Any]] = []
    split_map = None
    n_events_by_fraction: dict[float, int] = {}
    lambda_by_fraction: dict[float, dict[str, float]] = {}
    budget_state: dict[float, dict[str, Any]] = {}

    for fraction in BUDGET_FRACTIONS:
        frame = budget_frames[fraction]
        panel = build_panel(frame, corpus=corpus, schema=schema, spec=spec)
        if split_map is None:
            split_map = panel.metadata.set_index("author_id")["split"].to_dict()
        calibration = calibrate_d0_soft(panel)
        eval_mask = panel.metadata["split"].isin(["D1", "D2"]).to_numpy()
        eval_meta = panel.metadata.loc[eval_mask]
        resolved = resolved_contexts(eval_meta, spec.minimum_context_authors)
        if not resolved:
            raise ValueError(f"{corpus}: no resolved contexts at {fraction}.")
        rmask = eval_mask & panel.metadata["context"].astype(str).isin(
            resolved
        ).to_numpy()
        projected = project_soft(panel, rmask, calibration)
        meta_r = panel.metadata.loc[rmask]
        contexts_arr = meta_r["context"].astype(str).to_numpy()
        n_events = int(meta_r["event_count"].sum())
        n_events_by_fraction[fraction] = n_events
        lam_i = LAMBDA_DEFAULT
        lam_ii = LAMBDA_DEFAULT * (
            n_events_by_fraction[BUDGET_FRACTIONS[0]] / n_events
        )
        lambda_by_fraction[fraction] = {"v2_fixed": lam_i, "lambda_inv_n": lam_ii}

        fields_i, weights, diag_i = whitened_field(
            projected, contexts_arr, resolved, lam_i
        )
        fields_ii, _, diag_ii = whitened_field(
            projected, contexts_arr, resolved, lam_ii
        )
        per_context = {
            c: float(v8._matrix_cosine(fields_i[c], fields_ii[c]))
            for c in fields_i
        }
        agreement = field_agreement(fields_i, fields_ii, weights)
        # UNREGISTERED COMPANION DIAGNOSTIC (labeled): the conventions produce a
        # large Frobenius SCALE difference that the field's own scale-invariant
        # statistic cannot see; record it so the mechanism is quantitative.
        norm_ratio = {
            c: float(
                np.linalg.norm(fields_ii[c])
                / max(np.linalg.norm(fields_i[c]), 1e-300)
            )
            for c in fields_i
        }
        weighted_norm_ratio = float(
            sum(weights[c] * norm_ratio[c] for c in fields_i)
            / max(sum(weights[c] for c in fields_i), 1e-12)
        )
        gap_rows.append(
            {
                "banner": BANNER,
                "corpus": corpus,
                "budget_fraction": fraction,
                "achieved_fraction": float(n_events / (
                    events.loc[
                        events["author_id"].isin(meta_r["author_id"])
                    ].groupby("author_id", observed=True).size().sum()
                )),
                "n_eval_authors": int(rmask.sum()),
                "n_eval_events": n_events,
                "lambda_v2_fixed": lam_i,
                "lambda_inv_n": lam_ii,
                "weighted_matrix_cosine": agreement,
                "between_convention_gap": float(1.0 - agreement),
                "per_context_cosine": json.dumps(per_context),
                "companion_weighted_frobenius_ratio_invn_over_v2": (
                    weighted_norm_ratio
                ),
                "companion_predicted_scale_ratio_if_projective": float(
                    lam_i / lam_ii
                ),
                "per_context_frobenius_ratio": json.dumps(norm_ratio),
            }
        )
        for family in v8.FAMILY_NAMES:
            diagnostic_rows.append(
                {
                    "corpus": corpus,
                    "budget_fraction": fraction,
                    "family": family,
                    "d0_effective_rank": calibration[family].effective_rank,
                    **{f"{k}_v2": v for k, v in diag_i[family].items()},
                    "n_below_floor_inv_n": diag_ii[family]["n_below_floor"],
                }
            )
        budget_state[fraction] = {
            "frame": frame,
            "calibration": calibration,
            "resolved": resolved,
            "eval_authors": set(meta_r["author_id"].astype(str)),
            "lambdas": {"v2_fixed": lam_i, "lambda_inv_n": lam_ii},
        }

    # ----- internal split-half agreement rows -----
    m_by_author = author_events.astype(int).to_dict()
    _draw_cache: dict[tuple[float, frozenset], dict[str, list[float]]] = {}

    def internal_row(
        fraction: float,
        scope: str,
        scope_authors: set[str],
    ) -> None:
        state = budget_state[fraction]
        frame = state["frame"]
        sizes = frame.groupby("author_id", observed=True).size()
        halvable = {
            str(a)
            for a, b in sizes.items()
            if int(b) >= MIN_HALVABLE_EVENTS and str(a) in scope_authors
        }
        retained = halvable & state["eval_authors"]
        base = {
            "banner": BANNER,
            "corpus": corpus,
            "budget_fraction": fraction,
            "scope": scope,
            "retained_authors": int(len(retained)),
            "draws": draws,
        }
        if not retained:
            for convention in ("v2_fixed", "lambda_inv_n", "penalty_free_deployed"):
                internal_rows.append(
                    {
                        **base,
                        "convention": convention,
                        "lambda": float("nan"),
                        "measurable": 0,
                        "reason": (
                            "budgeted events per author < 8; the frozen feature "
                            "map needs >= 2 events per replicate path per half"
                        ),
                        "mean_agreement": float("nan"),
                        "sd_agreement": float("nan"),
                        "mean_disagreement": float("nan"),
                    }
                )
            return
        # Resolved contexts on the retained sub-panel.
        retained_meta = frame.loc[
            frame["author_id"].astype(str).isin(retained)
        ].groupby("author_id", observed=True).first().reset_index()
        sub_resolved = resolved_contexts(
            retained_meta, spec.minimum_context_authors
        )
        if not sub_resolved:
            for convention in ("v2_fixed", "lambda_inv_n", "penalty_free_deployed"):
                internal_rows.append(
                    {
                        **base,
                        "convention": convention,
                        "lambda": float("nan"),
                        "measurable": 0,
                        "reason": "no resolved context on the retained sub-panel",
                        "mean_agreement": float("nan"),
                        "sd_agreement": float("nan"),
                        "mean_disagreement": float("nan"),
                    }
                )
            return
        retained_in_resolved = {
            str(a)
            for a in retained_meta.loc[
                retained_meta["context"].astype(str).isin(sub_resolved),
                "author_id",
            ]
        }
        conventions = {
            "v2_fixed": state["lambdas"]["v2_fixed"],
            "lambda_inv_n": state["lambdas"]["lambda_inv_n"],
            "penalty_free_deployed": None,
        }
        cache_key = (fraction, frozenset(retained_in_resolved))
        if cache_key in _draw_cache:
            values = _draw_cache[cache_key]
            for name, lam in conventions.items():
                sample = np.asarray(values[name], dtype=float)
                internal_rows.append(
                    {
                        **base,
                        "retained_authors": int(len(retained_in_resolved)),
                        "convention": name,
                        "lambda": float("nan") if lam is None else float(lam),
                        "measurable": 1,
                        "reason": "deduplicated: identical retained panel",
                        "mean_agreement": float(sample.mean()),
                        "sd_agreement": float(sample.std(ddof=1)),
                        "mean_disagreement": float(1.0 - sample.mean()),
                    }
                )
            return
        values: dict[str, list[float]] = {name: [] for name in conventions}
        for draw in range(draws):
            frame_a, frame_b = split_half_frames(
                frame,
                corpus=corpus,
                budget_label=f"f{fraction}",
                draw=draw,
                retained_authors=retained_in_resolved,
            )
            panels = [
                build_panel(part, corpus=corpus, schema=schema, spec=spec)
                for part in (frame_a, frame_b)
            ]
            halves = []
            for part_panel in panels:
                all_mask = np.ones(len(part_panel.metadata), dtype=bool)
                projected = project_soft(
                    part_panel, all_mask, state["calibration"]
                )
                ctx = part_panel.metadata["context"].astype(str).to_numpy()
                halves.append((projected, ctx))
            counts = panels[0].metadata["context"].astype(str).value_counts()
            weights = {
                c: float(counts.get(c, 0) / max(1, int(counts.sum())))
                for c in sub_resolved
            }
            for name, lam in conventions.items():
                if lam is None:
                    fa = deployed_soft_field(halves[0][0], halves[0][1], sub_resolved)
                    fb = deployed_soft_field(halves[1][0], halves[1][1], sub_resolved)
                else:
                    fa, _, _ = whitened_field(
                        halves[0][0], halves[0][1], sub_resolved, lam
                    )
                    fb, _, _ = whitened_field(
                        halves[1][0], halves[1][1], sub_resolved, lam
                    )
                values[name].append(field_agreement(fa, fb, weights))
        _draw_cache[cache_key] = values
        for name, lam in conventions.items():
            sample = np.asarray(values[name], dtype=float)
            internal_rows.append(
                {
                    **base,
                    "retained_authors": int(len(retained_in_resolved)),
                    "convention": name,
                    "lambda": float("nan") if lam is None else float(lam),
                    "measurable": 1,
                    "reason": "",
                    "mean_agreement": float(sample.mean()),
                    "sd_agreement": float(sample.std(ddof=1)),
                    "mean_disagreement": float(1.0 - sample.mean()),
                }
            )

    all_authors = {str(a) for a in author_events.index}
    matched_authors = {
        str(a) for a, m in m_by_author.items() if int(m) >= MATCHED_MIN_FULL_EVENTS
    }
    for fraction in BUDGET_FRACTIONS:
        internal_row(fraction, "all", all_authors)
    if matched_authors and matched_authors != all_authors:
        for fraction in (0.5, 1.0):
            internal_row(fraction, f"matched_m{MATCHED_MIN_FULL_EVENTS}", matched_authors)

    return {
        "schema": schema,
        "gates": gates,
        "gap_rows": gap_rows,
        "internal_rows": internal_rows,
        "diagnostic_rows": diagnostic_rows,
        "n_events_by_fraction": {
            str(k): v for k, v in n_events_by_fraction.items()
        },
        "lambda_by_fraction": {
            str(k): v for k, v in lambda_by_fraction.items()
        },
        "total_events": total_events,
        "runtime_seconds": float(time.time() - started),
    }


# ---------------------------------------------------------------------------

def _lookup_internal(
    rows: list[dict[str, Any]],
    corpus: str,
    fraction: float,
    scope: str,
    convention: str,
) -> dict[str, Any] | None:
    for row in rows:
        if (
            row["corpus"] == corpus
            and row["budget_fraction"] == fraction
            and row["scope"] == scope
            and row["convention"] == convention
        ):
            return row
    return None


def _lookup_gap(
    rows: list[dict[str, Any]], corpus: str, fraction: float
) -> dict[str, Any] | None:
    for row in rows:
        if row["corpus"] == corpus and row["budget_fraction"] == fraction:
            return row
    return None


def adjudicate(
    gap_rows: list[dict[str, Any]],
    internal_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    # Lean (a): monotone internal agreement with n, both whitened conventions,
    # PANDORA, matched panel, measurable budgets {1/2, 1}.
    scope = f"matched_m{MATCHED_MIN_FULL_EVENTS}"
    lean_a = {"lean": "a", "corpus": "pandora", "scope": scope}
    per_convention = {}
    for convention in ("v2_fixed", "lambda_inv_n"):
        half = _lookup_internal(
            internal_rows, "pandora", 0.5, scope, convention
        ) or _lookup_internal(internal_rows, "pandora", 0.5, "all", convention)
        fullr = _lookup_internal(
            internal_rows, "pandora", 1.0, scope, convention
        ) or _lookup_internal(internal_rows, "pandora", 1.0, "all", convention)
        if not half or not fullr or not half["measurable"] or not fullr["measurable"]:
            per_convention[convention] = {"status": "NOT_MEASURABLE"}
            continue
        per_convention[convention] = {
            "agreement_half": half["mean_agreement"],
            "agreement_full": fullr["mean_agreement"],
            "monotone_increase": bool(
                fullr["mean_agreement"] > half["mean_agreement"]
            ),
        }
    lean_a["per_convention"] = per_convention
    measurable = [
        v for v in per_convention.values() if "monotone_increase" in v
    ]
    lean_a["quarter_budget"] = (
        "NOT_MEASURABLE (b=4 < 8; frozen feature-map path floor)"
    )
    if not measurable:
        lean_a["verdict"] = "NOT_MEASURABLE"
    elif all(v["monotone_increase"] for v in measurable):
        lean_a["verdict"] = "HOLD (restricted to measurable budgets {1/2, 1})"
    else:
        lean_a["verdict"] = "MISS"
    result["lean_a"] = lean_a

    # Lean (b) + pivot: full-n gap vs internal disagreement, PANDORA, all scope.
    ratios = {}
    for corpus in ("pandora", "essays"):
        gap_row = _lookup_gap(gap_rows, corpus, 1.0)
        dis = {}
        for convention in ("v2_fixed", "lambda_inv_n"):
            row = _lookup_internal(internal_rows, corpus, 1.0, "all", convention)
            dis[convention] = (
                row["mean_disagreement"] if row and row["measurable"] else None
            )
        if gap_row is None or any(v is None for v in dis.values()):
            ratios[corpus] = {"status": "NOT_MEASURABLE"}
            continue
        gap = gap_row["between_convention_gap"]
        dmax = max(dis.values())
        dmin = min(dis.values())
        ratios[corpus] = {
            "gap_full_n": gap,
            "internal_disagreement_v2": dis["v2_fixed"],
            "internal_disagreement_inv_n": dis["lambda_inv_n"],
            "ratio_vs_max": float(gap / dmax) if dmax > 0 else float("inf"),
            "ratio_vs_min": float(gap / dmin) if dmin > 0 else float("inf"),
            "excess_sign": int(np.sign(gap - dmax)),
        }
    result["full_n_ratios"] = ratios

    pandora = ratios.get("pandora", {})
    lean_b = {"lean": "b", "corpus": "pandora"}
    pivot = {"registered_rule": "gap < 1.2 x min internal disagreement at full n"}
    if "gap_full_n" not in pandora:
        lean_b["verdict"] = "NOT_MEASURABLE"
        pivot["fires"] = False
        pivot["status"] = "NOT_MEASURABLE"
    else:
        lean_b["threshold"] = "gap > 2 x max(internal disagreement of either convention)"
        lean_b["gap"] = pandora["gap_full_n"]
        lean_b["ratio_vs_max"] = pandora["ratio_vs_max"]
        lean_b["verdict"] = "HOLD" if pandora["ratio_vs_max"] > 2.0 else "MISS"
        pivot["ratio_vs_min"] = pandora["ratio_vs_min"]
        pivot["fires"] = bool(pandora["ratio_vs_min"] < 1.2)
    result["lean_b"] = lean_b
    result["pivot"] = pivot

    essays = ratios.get("essays", {})
    lean_c = {"lean": "c", "corpus": "essays", "rule": "same sign as PANDORA, direction only"}
    if "excess_sign" not in essays or "excess_sign" not in pandora:
        lean_c["verdict"] = "NOT_MEASURABLE"
    else:
        lean_c["pandora_sign"] = pandora["excess_sign"]
        lean_c["essays_sign"] = essays["excess_sign"]
        lean_c["verdict"] = (
            "HOLD" if essays["excess_sign"] == pandora["excess_sign"] else "MISS"
        )
    result["lean_c"] = lean_c

    if result["lean_b"].get("verdict") == "HOLD":
        verdict = (
            "SELF_INFLICTION_OPERATES_ON_REAL_TEXT_VIA_SUBSTITUTED_WHITENED_KNOB"
        )
    elif result["pivot"].get("fires"):
        verdict = (
            "PENALTY_CHOICE_IMMATERIAL_AT_REAL_TEXT_SCALE_"
            "SELF_INFLICTION_LESSON_STAYS_SYNTHETIC_SCOPED"
        )
    else:
        verdict = "INTERMEDIATE_ZONE_NEITHER_LEAN_B_NOR_PIVOT_FIRES"
    result["verdict"] = verdict
    result["substituted_knob_caveat"] = (
        "The deployed V8 soft relation-field estimator is penalty-free; both "
        "conventions act on the registered substituted knob (whitened variant "
        "in the full soft-projected space, module _inverse_sqrt relative-floor "
        "semantics). Any 'operates' reading is scoped to that knob."
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--draws", type=int, default=SPLIT_DRAWS)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    spec = v8.RealTextRelationSpec(**config["spec"])
    if abs(spec.ridge - LAMBDA_DEFAULT) > 0:
        raise AssertionError(
            f"Module default ridge {spec.ridge} != registered lambda "
            f"{LAMBDA_DEFAULT}."
        )
    draws = args.draws
    output_dir = args.output_dir
    persisted_all = None
    if args.smoke:
        draws = min(4, draws)
        output_dir = args.output_dir / "_smoke"
        config["data"]["pandora"]["maximum_authors_per_context"] = 40
        config["data"]["essays"]["maximum_authors"] = 160
    else:
        persisted_all = {
            entry["corpus"]: entry
            for entry in json.loads(PERSISTED_SCHEMA.read_text(encoding="utf-8"))
        }
    if draws < 20 and not args.smoke:
        raise AssertionError("Registered design requires >= 20 split-half draws.")
    output_dir.mkdir(parents=True, exist_ok=True)

    script = _load_v8_script()
    loaders = {
        "pandora": script.load_pandora_events,
        "essays": script.load_essays_events,
    }
    started = time.time()
    all_gap, all_internal, all_diag = [], [], []
    corpus_summaries = {}
    for corpus, loader in loaders.items():
        summary = run_corpus(
            corpus=corpus,
            loader=loader,
            data_config=config["data"][corpus],
            spec=spec,
            persisted=None if persisted_all is None else persisted_all[corpus],
            draws=draws,
        )
        all_gap.extend(summary.pop("gap_rows"))
        all_internal.extend(summary.pop("internal_rows"))
        all_diag.extend(summary.pop("diagnostic_rows"))
        corpus_summaries[corpus] = summary
        print(
            f"[{corpus}] done in {summary['runtime_seconds']:.1f}s "
            f"(events {summary['total_events']})",
            flush=True,
        )

    adjudication = adjudicate(all_gap, all_internal)

    pd.DataFrame(all_gap).to_csv(output_dir / "convention_gap_rows.csv", index=False)
    pd.DataFrame(all_internal).to_csv(
        output_dir / "internal_agreement_rows.csv", index=False
    )
    pd.DataFrame(all_diag).to_csv(output_dir / "diagnostic_rows.csv", index=False)
    ratio_rows = []
    for corpus, values in adjudication["full_n_ratios"].items():
        ratio_rows.append({"corpus": corpus, "budget_fraction": 1.0, **values})
    pd.DataFrame(ratio_rows).to_csv(output_dir / "ratio_rows.csv", index=False)

    decision = {
        "experiment": "M4-E1_convention_gap",
        "banner": BANNER,
        "tier": "EXPLORATORY",
        "registered_spec": (
            "docs/SUICA_M4_D_CURVATURE_AND_RELATION_BRIDGE_PLAN.md#M4-E1"
        ),
        "knob_substitution_registered_in": (
            "reports/SUICA_M4_E1_CONVENTION_GAP_REPORT.md Part 0 (before run)"
        ),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "smoke": bool(args.smoke),
        "master_seed": MASTER_SEED,
        "split_half_draws": draws,
        "budget_fractions": list(BUDGET_FRACTIONS),
        "lambda_default": LAMBDA_DEFAULT,
        "corpus_summaries": corpus_summaries,
        "adjudication": adjudication,
        "runtime_seconds": float(time.time() - started),
        "label_free": True,
        "claim_boundary": config["claim_boundary"],
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(decision["adjudication"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
