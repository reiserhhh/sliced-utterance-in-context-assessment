from __future__ import annotations

import numpy as np
import pandas as pd

from suica_core.factor_discovery import (
    align_loading_matrices,
    build_family_features,
    fit_opportunity_model,
    fit_stable_crossview,
    parallel_analysis,
    safe_corr,
    stable_user_split,
    subspace_similarity,
    transform_stable_crossview,
    varimax,
)
from scripts.run_suica_v6_factor_discovery_v2 import (
    analyze_shared_hybrid,
    conditional_residual,
    effective_rank,
    identity_diagnostics,
    permutation_strata,
    prepare_units,
    surface_features,
)


def test_user_split_is_deterministic_and_binary() -> None:
    assert stable_user_split("alice") == stable_user_split("alice")
    assert {stable_user_split(f"u{i}") for i in range(100)} == {"discovery", "confirmation"}


def test_safe_corr_guards_constant_and_recovers_signal() -> None:
    assert np.isnan(safe_corr(np.ones(30), np.arange(30)))
    assert safe_corr(np.arange(30), np.arange(30) + 0.01) > 0.99


def test_varimax_and_alignment_recover_permutation() -> None:
    raw = np.array([[0.8, 0.1], [0.7, 0.2], [0.1, 0.9], [0.2, 0.8]])
    rotated, _ = varimax(raw)
    candidate = rotated[:, [1, 0]] * np.array([-1.0, 1.0])
    _, congruence = align_loading_matrices(rotated, candidate)
    assert np.allclose(congruence, 1.0)


def test_parallel_analysis_detects_two_latent_factors() -> None:
    rng = np.random.default_rng(7)
    z = rng.normal(size=(600, 2))
    x = np.column_stack([
        z[:, 0] + rng.normal(scale=0.2, size=600),
        0.8 * z[:, 0] + rng.normal(scale=0.2, size=600),
        z[:, 1] + rng.normal(scale=0.2, size=600),
        0.7 * z[:, 1] + rng.normal(scale=0.2, size=600),
    ])
    k, _, _ = parallel_analysis(x, n_iter=30, seed=3)
    assert k == 2


def test_family_builder_separates_shared_condition_and_author_response() -> None:
    rng = np.random.default_rng(11)
    rows = []
    users = [f"u{i}" for i in range(80)]
    conditions = [f"c{i}" for i in range(6)]
    for ui, user in enumerate(users):
        author = (ui - 40) / 20
        for half in ("early", "late"):
            for ci, condition in enumerate(conditions):
                opportunity = (ci - 2.5) / 2
                for t in range(3):
                    rows.append({
                        "user_id": user, "half": half, "condition": condition,
                        "slice_index": t,
                        "f1": opportunity + author + 0.3 * author * opportunity + rng.normal(scale=0.05),
                        "f2": -opportunity + 0.5 * author + rng.normal(scale=0.05),
                    })
    frame = pd.DataFrame(rows)
    discovery = set(users[:40])
    model = fit_opportunity_model(frame, ["f1", "f2"], discovery,
                                  n_axes=1, min_condition_users=10)
    families = build_family_features(frame, model, min_slices=6,
                                     min_conditions_hybrid=4, ridge_alpha=0.2)
    assert set(families) == {"static", "dynamic", "hybrid"}
    assert len(families["static"]) == 160
    assert any(c.startswith("response_z1::") for c in families["hybrid"])
    static = families["static"].pivot(index="user_id", columns="half", values="level::f1")
    assert safe_corr(static["early"], static["late"]) > 0.95


def test_stable_crossview_recovers_repeated_latent_subspace() -> None:
    rng = np.random.default_rng(19)
    z = rng.normal(size=(700, 2))
    load = rng.normal(size=(8, 2))
    early = z @ load.T + rng.normal(scale=0.7, size=(700, 8))
    late = z @ load.T + rng.normal(scale=0.7, size=(700, 8))
    result = fit_stable_crossview(early, late, n_permutations=40, max_factors=4, seed=4)
    assert result.n_factors >= 1
    se = transform_stable_crossview(early, result)
    sl = transform_stable_crossview(late, result)
    assert safe_corr(se[:, 0], sl[:, 0]) > 0.5
    similarity, angle = subspace_similarity(result.directions, result.directions)
    assert similarity > 0.999
    assert angle < 1e-5


def test_raw_unit_preparation_preserves_real_condition_runs() -> None:
    rows = []
    for i in range(40):
        rows.append({
            "author": "u1", "body": "ordinary discussion with enough words for analysis",
            "created_utc": float(i * 20 * 86400),
            "subreddit": "a" if i < 8 or 20 <= i < 28 else "b",
        })
    cfg = {
        "min_gap_days": 90, "dynamic_min_run_length": 4,
        "max_dynamic_comments_per_half": 32, "max_comments_per_half": 16,
    }
    units = prepare_units(pd.DataFrame(rows), cfg)
    assert set(units["half"]) == {"early", "late"}
    assert units["run_len"].max() >= 4
    assert units.sort_values(["half", "order"]).groupby("run_id")["run_pos"].apply(
        lambda x: np.all(np.diff(x) == 1)
    ).all()


def test_surface_features_are_finite_and_opportunity_only() -> None:
    out = surface_features("> quote\n- item 12 https://example.com?!")
    assert set(out) == {"log_tokens", "log_chars", "url_rate", "quote_rate", "list_rate",
                        "code_rate", "digit_rate", "question_rate", "exclamation_rate",
                        "punctuation_rate"}
    assert np.isfinite(list(out.values())).all()


def test_conditional_innovation_removes_static_shadow() -> None:
    users = [f"u{i}" for i in range(80)]
    rows_s, rows_h = [], []
    rng = np.random.default_rng(22)
    for i, user in enumerate(users):
        for half in ("early", "late"):
            s = i / 20 + (half == "late") * 0.01
            rows_s.append({"user_id": user, "half": half, "static::x": s})
            rows_h.append({"user_id": user, "half": half, "hybrid::y": 3 * s + rng.normal(scale=0.01)})
    discovery = set(users[:40])
    result = conditional_residual(pd.DataFrame(rows_h), [pd.DataFrame(rows_s)], "hybrid::", discovery)
    merged = result.merge(pd.DataFrame(rows_s), on=["user_id", "half"])
    in_discovery = merged["user_id"].isin(discovery)
    assert abs(safe_corr(merged.loc[in_discovery, "hybrid::y"],
                         merged.loc[in_discovery, "static::x"])) < 0.1


def test_permutation_strata_uses_volume_and_condition_support() -> None:
    frame = pd.DataFrame({
        "user_id": [f"u{i}" for i in range(120) for _ in range(2)],
        "half": [h for _ in range(120) for h in ("early", "late")],
        "meta_comments": [10 + i // 20 for i in range(120) for _ in range(2)],
        "meta_conditions": [2 + i // 40 for i in range(120) for _ in range(2)],
    })
    strata = permutation_strata(frame, [f"u{i}" for i in range(120)])
    assert len(strata) == 120
    assert len(np.unique(strata)) >= 2


def test_identity_diagnostics_preserve_distributed_signal_after_rotation() -> None:
    rng = np.random.default_rng(33)
    author = rng.normal(size=(120, 6))
    early = author + rng.normal(scale=0.2, size=author.shape)
    late = author + rng.normal(scale=0.2, size=author.shape)
    result = identity_diagnostics(early, late, seed=9)
    assert result["own_vs_stranger_auc"] > 0.9
    assert result["own_vs_stranger_auc_ci_lo"] > 0.9
    assert result["retrieval_top10"] > 0.8
    assert effective_rank(early.T @ late) > 1.0


def test_shared_hybrid_detects_one_score_in_static_and_dynamic_blocks() -> None:
    rng = np.random.default_rng(44)
    static_rows, dynamic_rows = [], []
    users = [f"u{i}" for i in range(700)]
    for user in users:
        z = rng.normal()
        for half in ("early", "late"):
            noise_s = rng.normal(scale=0.35, size=4)
            noise_d = rng.normal(scale=0.35, size=4)
            static_rows.append({"user_id": user, "half": half,
                                **{f"static::s{j}": z * (j + 1) / 4 + noise_s[j] for j in range(4)}})
            dynamic_rows.append({"user_id": user, "half": half,
                                 **{f"dynamic::d{j}": z * (4 - j) / 4 + noise_d[j] for j in range(4)}})
    cfg = {
        "seed": 42, "quick": True, "factor_permutations": 50,
        "factor_max_per_family": 4, "factor_min_stable_share": 0.05,
        "confirmation_min_subspace_similarity": 0.70,
        "confirmation_max_principal_angle": 45.0,
        "confirmation_min_own_stranger_auc": 0.55,
        "confirmation_min_reliability": 0.50,
        "confirmation_reliability_ci_floor": 0.30,
    }
    summary, rows = analyze_shared_hybrid(
        pd.DataFrame(static_rows), pd.DataFrame(dynamic_rows),
        set(users[:350]), set(users[350:]), cfg,
    )
    assert summary["n_factors"] >= 1
    assert rows[0]["cross_lag_relation"] > 0.5
    assert rows[0]["confirmation_reliability"] > 0.5
