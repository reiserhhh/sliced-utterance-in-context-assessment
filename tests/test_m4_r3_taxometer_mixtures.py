"""Contract tests for M4-R3 -- the taxometer on identity mixtures.

Registered test list (the registration's own words): "C-R3a bit-identity;
oracle-reader correctness on the note's checked values; two-draw AUC on a hand
toy; G0 anchor -- the w = 0, eta0 = 0.25 cells reproduce the imported L3
pipeline's readings; grid/seed determinism".

Every test here is synthetic and label-free.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def r3():
    return _load("run_suica_m4_r3_taxometer_mixtures",
                 "scripts/run_suica_m4_r3_taxometer_mixtures.py")


# ---------------------------------------------------------------------------
# The registered predictions are the note's, and the band is L3's own budget
# ---------------------------------------------------------------------------

def test_registered_predictions_are_the_note_s_numbers(r3):
    """eta0/(1+w^2) on the registered grid -- the eight numbers written into
    the registration before this leg ran."""
    assert [round(r3.predicted_eta(0.25, w), 3) for w in r3.W_GRID] == \
        [0.250, 0.200, 0.125, 0.050]
    assert [round(r3.predicted_eta(0.60, w), 3) for w in r3.W_GRID] == \
        [0.600, 0.480, 0.300, 0.120]
    assert [round(r3.designed_style_share(w), 3) for w in r3.W_GRID] == \
        [0.0, 0.2, 0.5, 0.8]


def test_band_is_the_l3_certification_budget_not_a_new_tolerance(r3):
    assert r3.BAND == r3.l3().X2_TOL == 0.125


def test_oracle_zero_point_is_dT_over_D(r3):
    assert r3.l3().K_TAU == 3
    assert r3.k2a().K_LATENT == 48
    assert r3.l3().K_TAU / r3.k2a().K_LATENT == pytest.approx(0.0625)


# ---------------------------------------------------------------------------
# The oracle excess-alignment reader, against the note's checked values
# ---------------------------------------------------------------------------

def _identity_and_style(rng, n, dim, k_tau, sigma_b2, eta, w_style):
    """The L geometry's identity mixture plus the R3 style channel, in latent
    coordinates -- the same algebra as l2.latent_identity_l2 + style_latent_r3
    but standalone, so the reader is tested against the note and not against
    the pipeline that produced it."""
    basis = np.linalg.qr(rng.normal(size=(dim, k_tau)))[0]
    vec = np.zeros((n, dim))
    if eta < 1.0:
        vec = vec + math.sqrt((1.0 - eta) * sigma_b2 / dim) * rng.normal(
            size=(n, dim))
    if eta > 0.0:
        zeta = rng.normal(size=(n, dim))
        vec = vec + math.sqrt(eta * sigma_b2 / k_tau) * ((zeta @ basis) @ basis.T)
    if w_style > 0.0:
        vec = vec + math.sqrt(w_style ** 2 * sigma_b2 / dim) * rng.normal(
            size=(n, dim))
    return vec, basis


def test_oracle_reads_zero_on_pure_isotropic_identity(r3):
    """The note: 'pure isotropic reads -0.0001' -- the excess reader's zero
    point is d_T/D, not 0 raw share."""
    rng = np.random.default_rng(11)
    vec, basis = _identity_and_style(rng, 200_000, 48, 3, 16.0, 0.0, 0.0)
    raw = r3.raw_aligned_share(vec, basis)
    assert raw == pytest.approx(3 / 48, abs=0.003)      # raw share is d_T/D > 0
    assert r3.eta_oracle_reader(vec, basis) == pytest.approx(0.0, abs=0.01)


def test_oracle_recovers_eta_on_the_note_s_grid(r3):
    """The note: 'eta in {.25,.5,.75} read {.2515,.4981,.7521}'."""
    for eta in (0.25, 0.5, 0.75):
        rng = np.random.default_rng(int(1000 * eta))
        vec, basis = _identity_and_style(rng, 200_000, 48, 3, 16.0, eta, 0.0)
        assert r3.eta_oracle_reader(vec, basis) == pytest.approx(eta, abs=0.01)


def test_oracle_reads_one_on_pure_aligned_identity(r3):
    """The note's second forgery direction: content aligned with T by
    construction reads eta_hat = 1.0."""
    rng = np.random.default_rng(5)
    vec, basis = _identity_and_style(rng, 100_000, 48, 3, 16.0, 1.0, 0.0)
    assert r3.eta_oracle_reader(vec, basis) == pytest.approx(1.0, abs=0.01)


def test_oracle_reproduces_the_dilution_law_at_eta0_0p6(r3):
    """The note section 2's numeric check: read {.5994,.4803,.2983,.1198}
    against predicted {.60,.48,.30,.12} for w in {0,.5,1,2}."""
    got = []
    for w_style in r3.W_GRID:
        rng = np.random.default_rng(20260819 + int(100 * w_style))
        vec, basis = _identity_and_style(rng, 200_000, 48, 3, 16.0, 0.6, w_style)
        got.append(r3.eta_oracle_reader(vec, basis))
    for value, w_style in zip(got, r3.W_GRID):
        assert value == pytest.approx(r3.predicted_eta(0.6, w_style), abs=0.01)
    assert all(b < a for a, b in zip(got, got[1:]))


def test_oracle_reproduces_the_dilution_law_at_eta0_0p25(r3):
    got = []
    for w_style in r3.W_GRID:
        rng = np.random.default_rng(770 + int(100 * w_style))
        vec, basis = _identity_and_style(rng, 200_000, 48, 3, 16.0, 0.25,
                                         w_style)
        got.append(r3.eta_oracle_reader(vec, basis))
    for value, w_style in zip(got, r3.W_GRID):
        assert value == pytest.approx(r3.predicted_eta(0.25, w_style), abs=0.01)


# ---------------------------------------------------------------------------
# The two-draw AUC on a hand toy
# ---------------------------------------------------------------------------

def test_pooled_auc_hand_toy_exact_one_and_exact_zero(r3):
    """A hand toy whose AUC is exact and tie-free.  Two authors at [1,0] and
    [0,1]; after author-centering they are antipodal unit vectors, so every
    cosine is exactly +1 or -1.  Draw 2 = draw 1 puts both positives at +1 and
    both negatives at -1 (AUC exactly 1); draw 2 with the two authors swapped
    inverts it exactly (AUC exactly 0)."""
    cards = np.array([[1.0, 0.0], [0.0, 1.0]])
    assert r3.pooled_auc(cards, cards.copy()) == 1.0
    assert r3.pooled_auc(cards, cards[[1, 0]]) == 0.0


def test_pooled_auc_hand_toy_cyclic_shift_is_below_chance(r3):
    """Draw 2 cyclically shifted by one author: every positive is a
    cross-author cosine while n of the negatives are exact self-matches, so the
    reader must land clearly BELOW its 0.5 null.  Deterministic (no RNG): four
    authors on four orthogonal axes give exactly 7/24."""
    cards = np.eye(4)
    assert r3.pooled_auc(cards, np.roll(cards, 1, axis=0)) == \
        pytest.approx(7.0 / 24.0)


def test_pooled_auc_null_is_one_half(r3):
    """#68: the reader's null in this design is 0.5, stated not assumed."""
    rng = np.random.default_rng(3)
    a = rng.normal(size=(200, 16))
    b = rng.normal(size=(200, 16))
    assert r3.pooled_auc(a, b) == pytest.approx(0.5, abs=0.05)


def test_pooled_auc_is_a_proper_auc(r3):
    """Monotone in the shared signal, bounded, and reduces to the
    Mann-Whitney statistic on the cross-draw cosine matrix."""
    rng = np.random.default_rng(7)
    shared = rng.normal(size=(120, 24))
    prev = 0.0
    for weight in (0.0, 0.25, 0.5, 1.0, 4.0):
        a = weight * shared + rng.normal(size=(120, 24))
        b = weight * shared + rng.normal(size=(120, 24))
        value = r3.pooled_auc(a, b)
        assert 0.0 <= value <= 1.0
        assert value >= prev - 0.05
        prev = value
    assert prev > 0.99


# ---------------------------------------------------------------------------
# C-R3a -- the zero-default bit-identity (the A1-stop certification)
# ---------------------------------------------------------------------------

def test_c_r3a_bit_identity_at_w_zero(r3):
    cert = r3.certify_c_r3a(world_indices=(0,), eta_levels=(0.0, 0.25, 0.6))
    assert cert["status"] == "PASS"
    assert cert["A1_stop"] is False
    assert cert["n_objects_per_cell"] >= 20
    for check in cert["checks"]:
        assert check["all_identical"], check["failed_keys"]


def test_style_is_skipped_not_zero_scaled_at_w_zero(r3):
    """The mechanism C-R3a depends on: at w = 0 the style term is None, so no
    arithmetic touches the latent vector at all."""
    assert r3.style_latent_r3(12345, 8, 16.0, 0.0) is None
    assert r3.style_latent_r3(12345, 8, 16.0, 1.0) is not None


def test_style_variance_is_w_squared_times_sigma_b2_by_construction(r3):
    """V_s / V_b = w^2 BY CONSTRUCTION (the #76 operating point)."""
    sigma_b2 = 16.111540782194115
    for w_style in (0.5, 1.0, 2.0):
        style = r3.style_latent_r3(99, 400_000, sigma_b2, w_style)
        realized = float(np.mean(np.einsum("ij,ij->i", style, style)))
        assert realized == pytest.approx(w_style ** 2 * sigma_b2, rel=0.01)


def test_style_is_the_same_direction_across_w_so_cells_are_paired(r3):
    """The style base draw depends on the WORLD only: the w profile is an
    exactly paired within-world contrast."""
    one = r3.style_latent_r3(4242, 64, 9.0, 1.0)
    two = r3.style_latent_r3(4242, 64, 9.0, 2.0)
    assert np.allclose(two, 2.0 * one, rtol=0, atol=1e-12)


# ---------------------------------------------------------------------------
# G0 anchor
# ---------------------------------------------------------------------------

def test_g0_anchor_reproduces_the_l3_pipeline(r3):
    """The w = 0, eta0 = 0.25 cell run through THIS leg's pipeline on L3's own
    world seeds must reproduce L3's own reading conventions.  When L3's
    committed cell artifact is on disk the comparison is world-for-world;
    otherwise the self-consistency form (C-R3a) is reported."""
    anchor = r3.g0_anchor()
    assert anchor["status"] in {"PASS", "SELF_CONSISTENCY_ONLY"}
    assert anchor["n_worlds"] == r3.l3().WORLDS_PER_CELL
    if anchor.get("committed_artifact_readable"):
        assert anchor["n_matched_worlds"] == anchor["n_worlds"]
        assert anchor["max_abs_diff_eta_hat_P"] <= 1e-12
        assert anchor["max_abs_diff_eta_hat_T"] <= 1e-12
        assert anchor["cell_mean_bit_identical"] is True


# ---------------------------------------------------------------------------
# Grid / seed determinism
# ---------------------------------------------------------------------------

def test_world_seed_convention_is_deterministic_and_disjoint_from_l3(r3):
    seeds = [r3.world_seed_for(i) for i in range(r3.WORLDS_PER_CELL)]
    assert seeds == [r3.world_seed_for(i) for i in range(r3.WORLDS_PER_CELL)]
    assert len(set(seeds)) == r3.WORLDS_PER_CELL
    l3_seeds = {r3.l3().world_seed_for(i) for i in range(64)}
    assert not (set(seeds) & l3_seeds)


def test_grid_shape_is_the_registered_one(r3):
    assert r3.SEED == 20260819
    assert r3.WORLDS_PER_CELL == 8
    assert r3.W_GRID == (0.0, 0.5, 1.0, 2.0)
    assert r3.ETA0_GRID == (0.25, 0.6)
    assert r3.ENERGY_PRIMARY == "rho55eq"
    assert r3.l3().N_AUTHORS == 512


def test_one_world_cell_is_reproducible(r3):
    """Same seeds in, bit-identical readings out."""
    lg2, lg3 = r3.l2(), r3.l3()
    wseed = r3.world_seed_for(0)
    world, typ = lg2.build_typed_world_l2(wseed, lg3.N_AUTHORS)
    sigma_b2 = r3.sigma_b2_of("rho55eq")
    style = r3.style_latent_r3(wseed, lg3.N_AUTHORS, sigma_b2, 1.0)
    kwargs = dict(world=world, typ=typ, world_index=0, world_seed=wseed,
                  energy="rho55eq", sigma_b2=sigma_b2, eta0=0.25, w_style=1.0,
                  style=style)
    first = r3.measure_world_cell(**kwargs)
    second = r3.measure_world_cell(**kwargs)
    assert first == second
    assert first["style_share_designed"] == pytest.approx(0.5)
    assert first["style_share_realized"] == pytest.approx(0.5, abs=0.05)


# ---------------------------------------------------------------------------
# Routing logic (pure functions on synthetic cell tables)
# ---------------------------------------------------------------------------

def _fake_cells(r3, profiles, auc=None):
    import pandas as pd
    rows = []
    for eta0, seq in profiles.items():
        for w_style, value in zip(r3.W_GRID, seq):
            pred = r3.predicted_eta(eta0, w_style)
            rows.append({
                "energy": "rho55eq", "eta0": eta0, "w_style": w_style,
                "style_share": r3.designed_style_share(w_style),
                "pred_eta": pred, "eta_hat_mean": value,
                "eta_oracle_mean": pred,
                "in_band": abs(value - pred) <= r3.BAND,
                "auc_mean": (auc or {}).get(eta0, [0.9, 0.92, 0.94, 0.96])[
                    r3.W_GRID.index(w_style)],
                "auc_slow_mean": 0.9,
                "bias_abs_of_cellmean": abs(value - pred),
                "bias_signed_mean": value - pred,
                "mean_abs_bias": abs(value - pred),
                "bias_lo": value - pred - 0.01, "bias_hi": value - pred + 0.01,
            })
    return pd.DataFrame(rows)


def test_p1_routes_holds_shape_shifts_and_fails(r3):
    exact = {e: [r3.predicted_eta(e, w) for w in r3.W_GRID]
             for e in r3.ETA0_GRID}
    assert r3.adjudicate_p1(_fake_cells(r3, exact), "rho55eq")["cell"] == \
        "DILUTION_LAW_HOLDS"

    shifted = {e: [v + (0.2 if i == 0 else 0.0) for i, v in enumerate(seq)]
               for e, seq in exact.items()}
    assert r3.adjudicate_p1(_fake_cells(r3, shifted), "rho55eq")["cell"] == \
        "DILUTION_SHAPE_SHIFTS"

    bumped = {e: list(seq) for e, seq in exact.items()}
    bumped[0.25][1] = bumped[0.25][0] + 0.01          # a rise at the first step
    assert r3.adjudicate_p1(_fake_cells(r3, bumped), "rho55eq")["cell"] == \
        "DILUTION_FAILS"

    flat = {e: [0.30, 0.29, 0.28, 0.27] for e in r3.ETA0_GRID}
    p1_flat = r3.adjudicate_p1(_fake_cells(r3, flat), "rho55eq")
    assert p1_flat["cell"] == "DILUTION_FAILS"
    assert p1_flat["any_flat"] is True


def test_p2_routes_confirmed_partial_and_fails(r3):
    falling = {e: [r3.predicted_eta(e, w) for w in r3.W_GRID]
               for e in r3.ETA0_GRID}
    rising = {e: [0.90, 0.93, 0.96, 0.99] for e in r3.ETA0_GRID}
    flat_auc = {e: [1.0, 1.0, 1.0, 1.0] for e in r3.ETA0_GRID}
    assert r3.adjudicate_p2(_fake_cells(r3, falling, rising),
                            "rho55eq")["cell"] == "SIGNED_DISSOCIATION_CONFIRMED"
    partial = r3.adjudicate_p2(_fake_cells(r3, falling, flat_auc), "rho55eq")
    assert partial["cell"] == "PARTIAL"
    assert partial["flag_73"] is True
    flat_eta = {e: [0.3, 0.3, 0.3, 0.3] for e in r3.ETA0_GRID}
    assert r3.adjudicate_p2(_fake_cells(r3, flat_eta, flat_auc),
                            "rho55eq")["cell"] == "FAILS"


def test_p3_routes_budget_holds_and_bound_measured(r3):
    exact = {e: [r3.predicted_eta(e, w) for w in r3.W_GRID]
             for e in r3.ETA0_GRID}
    assert r3.adjudicate_p3(_fake_cells(r3, exact), "rho55eq")["cell"] == \
        "BUDGET_HOLDS"
    blown = {e: [r3.predicted_eta(e, w) + (0.3 if w == 2.0 else 0.0)
                 for w in r3.W_GRID] for e in r3.ETA0_GRID}
    p3 = r3.adjudicate_p3(_fake_cells(r3, blown), "rho55eq")
    assert p3["cell"] == "BOUND_MEASURED"
    assert p3["crossings"]
    assert 0.5 < p3["crossings"][0]["crossing_style_share"] <= 0.8


# ---------------------------------------------------------------------------
# The #83 ID gate's own contract
# ---------------------------------------------------------------------------

def test_id_scan_word_boundary_and_head_policy(r3, tmp_path):
    """Leg-authored files (no HEAD version) carry zero tolerance; the boundary
    test must not fire on a substring."""
    target = tmp_path / "leg_authored.md"
    target.write_text("alpha bravo charlie\n")
    ROOT_SAVE = r3.ROOT
    try:
        r3.ROOT = tmp_path
        clean = r3.scan_for_cohort_ids([target], ["delta", "brav"])
        assert clean["status"] == "PASS" and clean["n_hits"] == 0
        dirty = r3.scan_for_cohort_ids([target], ["bravo"])
        assert dirty["status"] == "FAIL"
        assert dirty["n_hits"] == 1
        assert dirty["hits"][0]["line"] == 1
        assert dirty["leg_authored_files"] == ["leg_authored.md"]
    finally:
        r3.ROOT = ROOT_SAVE


def test_committed_files_carry_no_new_cohort_ids(r3):
    """The gate as it is actually run: over the widened universe when it is
    readable, on this leg's committed file set."""
    universe = r3.id_universe()
    if not universe["names"]:
        pytest.skip("the ID universe is not on disk in this checkout")
    scan = r3.scan_for_cohort_ids(
        [ROOT / "scripts/run_suica_m4_r3_taxometer_mixtures.py",
         Path(__file__),
         ROOT / "reports/SUICA_M4_R3_TAXOMETER_MIXTURES_REPORT.md"],
        universe["names"])
    assert scan["status"] == "PASS", scan["hits"]
