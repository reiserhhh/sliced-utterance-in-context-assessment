#!/usr/bin/env python3
"""SUICA D-open -- opening prospective seal #2: do the measured laws PREDICT?

Registered spec: docs/SUICA_DEFENSE_PHASE_PLAN.md section "D-open -- Opening
prospective seal #2" (REGISTERED 2026-08-10, BEFORE RUN, commit f0e89b9),
together with D1's committed opening protocol
(reports/SUICA_D1_PROSPECTIVE_SEAL_REPORT.md, "Opening protocol").
Executor standing: implementation and execution only.

THE BINDING ORDER OF OPERATIONS, ENFORCED IN CODE
-------------------------------------------------
STAGE 1 measures the five sealed configurations and persists
`results/dopen_seal_opening/measured.json` PLUS its SHA-256 and timestamp.
Only then may `results/d1_sealed/D1_SEALED_BUNDLE.json` be opened.  The
enforcement is not a convention: `builtins.open`, `io.open`, `os.open`,
`pathlib.Path.open/read_text/read_bytes` are all wrapped for the whole
process, and any access to the bundle path while the unseal permit is
withheld raises SystemExit and is logged to the append-only ordering log.
The permit is granted only by `stage2`, and only after re-hashing
measured.json from disk and matching the recorded pre-unseal hash.

USAGE (chunked foreground stages -- convention "chunked foreground stages")
    part0                       provenance, realizability pilots, enumeration
    stage1 --task m1m2          M-1/M-2  typed world at m=96, k_tau=4, G=5
    stage1 --task m3_48_512     M-3 (a)  T-arm ladder at (m=48, n=512)
    stage1 --task m3_192_256    M-3 (b)  T-arm ladder at (m=192, n=256)
    stage1 --task m4            M-4      K2b arm share .40, phi .90, 32 worlds
    stage1 --task m5            M-5      L3 taxometer at eta=.6, rho.45-eq
    seal                        assemble measured.json, hash it, stamp it
    stage2 [--dump-only]        unseal, verify the hash, score

Machinery reuse (rule 12): every measurement runs the PUBLISHED leg functions
unmodified.  Only the registration-fixed dimension constants of the reused
modules are re-pinned, by the transport rule pinned as RN-DO-1 in the report's
Part 0, inside a context manager that restores them afterwards.
"""

from __future__ import annotations

import argparse
import builtins
import hashlib
import importlib.util
import io
import json
import math
import os
import pathlib
import sys
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

BANNER = ("synthetic worlds calibrated to an opened-panel regime, exploratory; "
          "this leg MEASURES FIRST and UNSEALS SECOND")

OUT = ROOT / "results" / "dopen_seal_opening"
REPORT = ROOT / "reports" / "SUICA_DOPEN_SEAL_OPENING_REPORT.md"

BUNDLE = ROOT / "results" / "d1_sealed" / "D1_SEALED_BUNDLE.json"
COMMITTED_HASH = "3a1971b827210b7f3611b4769496f9d55d4ea815b6b8b577cae81f64b1fe00f8"

MEASURED = OUT / "measured.json"
MEASURED_STAMP = OUT / "measured.sha256.json"
ORDER_LOG = OUT / "ordering_log.jsonl"

# --- registration-fixed constants (D-open) ----------------------------------
MASTER_SEED = 20260825          # registration G3O: "seed = master_seed 20260825"
B_BOOT = 2000                   # registration G3O: "B=2000"
B_BOOT_HIGH = 20000             # registration G3O: ">=10xB at boundaries"

# --- the five configurations, verbatim from the registration ----------------
M1_M = 96
M1_K_TAU = 4
M1_G = 5
M1_N_OCC = 8
M1_WORLDS = 8
# RN-DO-8 (rule 9 + rule 17), pinned in Part 0 BEFORE Stage 1.  The registration
# says "512 authors", but the PUBLISHED equal-size group assignment
# (l2.type_geometry_l2, l2:220-224) fills `np.empty(n, int)` in G blocks of
# n // G and REQUIRES n % G == 0: at G = 5 and n = 512 the last two authors keep
# UNINITIALIZED memory as their group label.  There is no guard in the published
# function -- it never bit L1/L2/L3 because 512 % 4 == 0.  The registered author
# count is therefore realized as the largest multiple of G = 5 not exceeding it.
M1_N_AUTHORS_REGISTERED = 512
M1_N_AUTHORS = 510              # = 5 x 102
M1_ETAS = (0.0, 0.5, 1.0)

M3_SETTINGS = ((48, 512), (192, 256))

M4_SHARE = 0.40
M4_PHI = 0.90
M4_WORLDS = 32

M5_ETA = 0.6
M5_WORLDS = 8
M5_N_AUTHORS = 512

# --- RN-DO-1: the DIMENSION TRANSPORT rule (rule 9), pinned before Stage 1 ---
# k2a's generator constants are FUNCTIONS of (K_LATENT, DIM):
#   G_PROFILE  = linspace(0.85, 0.55, K_LATENT)      (k2a:91, from f2:164)
#   A_SCALE    = sqrt(2 / sum(G_PROFILE**2))         (k2a:92, from f2:165)
#   SIGMA_ISO  = sqrt(2 / DIM)                       (k2a:93, from f2:166)
#   loadings   = _orthonormal_loadings(rng, DIM, K_LATENT)  -- REQUIRES DIM >= m
# DIM = 64 is therefore UNREALIZABLE at m in {96, 192}: 96 orthonormal columns
# do not fit in R^64.  The transport that leaves every published FORMULA
# untouched is to carry the family's own design ratio DIM/m = 64/48 = 4/3:
DIM_NUM, DIM_DEN = 4, 3         # DIM(m) = 4m/3 -> 64, 128, 256 at m = 48, 96, 192


def dim_for(m: int) -> int:
    num = DIM_NUM * m
    if num % DIM_DEN != 0:
        raise SystemExit(f"REFUSED: DIM(m={m}) = {num}/{DIM_DEN} is not an integer")
    return num // DIM_DEN


# ---------------------------------------------------------------------------
# THE ORDERING GUARD (G1O).  Enforced, not asserted.

_UNSEAL_PERMIT = False
_GUARD_INSTALLED = False
_BUNDLE_READS: list[dict[str, Any]] = []


def _utc() -> str:
    return datetime.now(UTC).isoformat()


def log_event(phase: str, event: str, **extra: Any) -> dict[str, Any]:
    rec = {"utc": _utc(), "monotonic": time.monotonic(), "phase": phase,
           "event": event, "pid": os.getpid(), **extra}
    OUT.mkdir(parents=True, exist_ok=True)
    with _RAW_OPEN(ORDER_LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


_RAW_OPEN = builtins.open
_RAW_IO_OPEN = io.open
_RAW_OS_OPEN = os.open
_RAW_PATH_OPEN = pathlib.Path.open
_RAW_PATH_READ_TEXT = pathlib.Path.read_text
_RAW_PATH_READ_BYTES = pathlib.Path.read_bytes


def _is_bundle(target: Any) -> bool:
    try:
        p = Path(os.fspath(target))
    except TypeError:
        return False
    try:
        return p.resolve() == BUNDLE.resolve()
    except OSError:
        return str(p) == str(BUNDLE)


def _check(target: Any, how: str) -> None:
    if not _is_bundle(target):
        return
    rec = {"utc": _utc(), "how": how, "permit": _UNSEAL_PERMIT}
    _BUNDLE_READS.append(rec)
    if not _UNSEAL_PERMIT:
        log_event("GUARD", "BUNDLE_ACCESS_REFUSED", how=how)
        raise SystemExit(
            "REFUSED (G1O): the D1 sealed bundle was opened via "
            f"{how} before measured.json's hash was persisted.  "
            "The measure-first ordering is the product of this leg; STOP.")
    log_event("STAGE2", "BUNDLE_FIRST_READ", how=how)


def install_guard() -> None:
    global _GUARD_INSTALLED
    if _GUARD_INSTALLED:
        return

    def g_open(file, *a, **kw):            # noqa: ANN001
        _check(file, "builtins.open")
        return _RAW_OPEN(file, *a, **kw)

    def g_io_open(file, *a, **kw):         # noqa: ANN001
        _check(file, "io.open")
        return _RAW_IO_OPEN(file, *a, **kw)

    def g_os_open(path, *a, **kw):         # noqa: ANN001
        _check(path, "os.open")
        return _RAW_OS_OPEN(path, *a, **kw)

    def g_path_open(self, *a, **kw):       # noqa: ANN001
        _check(self, "Path.open")
        return _RAW_PATH_OPEN(self, *a, **kw)

    def g_path_read_text(self, *a, **kw):  # noqa: ANN001
        _check(self, "Path.read_text")
        return _RAW_PATH_READ_TEXT(self, *a, **kw)

    def g_path_read_bytes(self, *a, **kw):  # noqa: ANN001
        _check(self, "Path.read_bytes")
        return _RAW_PATH_READ_BYTES(self, *a, **kw)

    builtins.open = g_open
    io.open = g_io_open
    os.open = g_os_open
    pathlib.Path.open = g_path_open
    pathlib.Path.read_text = g_path_read_text
    pathlib.Path.read_bytes = g_path_read_bytes
    _GUARD_INSTALLED = True


def grant_permit() -> dict[str, Any]:
    """The ONLY way the guard opens.  Requires a persisted, matching stamp."""
    global _UNSEAL_PERMIT
    if not MEASURED.exists() or not MEASURED_STAMP.exists():
        raise SystemExit("REFUSED (G1O): measured.json / its stamp do not exist")
    stamp = json.loads(_RAW_PATH_READ_TEXT(MEASURED_STAMP, encoding="utf-8"))
    digest = hashlib.sha256(_RAW_PATH_READ_BYTES(MEASURED)).hexdigest()
    if digest != stamp["measured_sha256"]:
        raise SystemExit(
            "REFUSED (G1O): measured.json changed after it was stamped "
            f"({digest} != {stamp['measured_sha256']})")
    stamped = datetime.fromisoformat(stamp["stamped_utc"])
    now = datetime.now(UTC)
    if stamped >= now:
        raise SystemExit("REFUSED (G1O): the stamp is not strictly in the past")
    _UNSEAL_PERMIT = True
    return {"measured_sha256": digest, "stamped_utc": stamp["stamped_utc"],
            "permit_granted_utc": now.isoformat(),
            "seconds_between": (now - stamped).total_seconds()}


# ---------------------------------------------------------------------------
# Module loading (rule 12: the published leg scripts, imported UNMODIFIED)

_MODS: dict[str, Any] = {}


def _load(name: str) -> Any:
    if name in _MODS:
        return _MODS[name]
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _MODS[name] = module
    return module


# NOTE (rule 12, and the reason for the single chain): each leg script loads its
# own dependencies with importlib, so `_load("...l2")` and `l3().l2()` would be
# DISTINCT module objects with distinct constants.  Everything L-line therefore
# resolves through ONE chain rooted at L3, so a re-pinned constant is seen by
# every function that reads it.  K2b is deliberately OUTSIDE that chain: M-4
# runs at K2b's own 48/64 dimensions and must not see any re-pinning.

def l3() -> Any:
    return _load("run_suica_m4_l3_taxometer_meter")


def l2() -> Any:
    return l3().l2()


def l1() -> Any:
    return l2().l1()


def k2a() -> Any:
    return l1().k2a()


def k2b() -> Any:
    return _load("run_suica_m4_k2b_t4_branch")


# ---------------------------------------------------------------------------
# RN-DO-2: the SIMPLEX generalization (rule 9), pinned before Stage 1.
# l1.TETRAHEDRON is the G=4 regular simplex in R^3 at unit pairwise separation
# (l1:191-193), with sigma_tau^2 = (3/8) Delta^2 (l1:194).  The general object
# is the regular (G-1)-simplex: the G standard basis vectors of R^G, centred,
# scaled to unit pairwise separation, expressed in an orthonormal basis of the
# all-ones complement.  Then ||v_g||^2 = (G-1)/(2G) exactly -- 3/8 at G = 4,
# so the G=4 instance reproduces l1's own constant.

def simplex_vertices(g_groups: int) -> np.ndarray:
    eye = np.eye(g_groups)
    cent = eye - eye.mean(axis=0, keepdims=True)
    basis = np.linalg.qr(cent.T)[0][:, : g_groups - 1]      # (G, G-1) orthonormal
    verts = cent @ basis / math.sqrt(2.0)                   # unit pairwise distance
    return np.asarray(verts, dtype=float)


def simplex_audit(g_groups: int) -> dict[str, Any]:
    v = simplex_vertices(g_groups)
    pw = np.linalg.norm(v[:, None, :] - v[None, :, :], axis=2)
    off = pw[~np.eye(g_groups, dtype=bool)]
    return {"G": g_groups, "shape": list(v.shape),
            "pairwise_min": float(off.min()), "pairwise_max": float(off.max()),
            "pairwise_dev_from_1": float(np.abs(off - 1.0).max()),
            "sigma_tau2_per_delta2": float(np.mean(np.einsum("gi,gi->g", v, v))),
            "closed_form_(G-1)/(2G)": (g_groups - 1) / (2.0 * g_groups),
            "centroid_norm": float(np.linalg.norm(v.mean(axis=0)))}


@contextmanager
def latent_config(m: int, k_tau: int, g_groups: int, n_authors: int):
    """Re-pin the reused modules' registration-fixed dimension constants.
    The FUNCTION BODIES are untouched (rule 12); only the constants they read
    move, by RN-DO-1 / RN-DO-2, and every one is restored on exit."""
    ka, lg1, lg2, lg3 = k2a(), l1(), l2(), l3()
    dim = dim_for(m)
    gp = np.linspace(0.85, 0.55, m)
    saves: list[tuple[Any, str, Any]] = []

    def setattr_saved(obj: Any, name: str, value: Any) -> None:
        saves.append((obj, name, getattr(obj, name)))
        setattr(obj, name, value)

    setattr_saved(ka, "K_LATENT", m)
    setattr_saved(ka, "DIM", dim)
    setattr_saved(ka, "G_PROFILE", gp)
    setattr_saved(ka, "A_SCALE", math.sqrt(2.0 / float(np.sum(gp ** 2))))
    setattr_saved(ka, "SIGMA_ISO", math.sqrt(2.0 / float(dim)))
    setattr_saved(ka, "UNIT_ENTRY_VAR", 2.0 / float(dim))
    for mod in (lg1, lg2, lg3):
        setattr_saved(mod, "K_TAU", k_tau)
        setattr_saved(mod, "G_GROUPS", g_groups)
    setattr_saved(lg1, "TETRAHEDRON", simplex_vertices(g_groups))
    setattr_saved(lg1, "SIGMA_TAU2_PER_DELTA2", (g_groups - 1) / (2.0 * g_groups))
    for mod in (lg1, lg2, lg3):
        setattr_saved(mod, "N_AUTHORS", n_authors)
    # pred_population_l2's n_authors default was bound at DEFINITION time
    saves.append((lg2.pred_population_l2, "__defaults__",
                  lg2.pred_population_l2.__defaults__))
    lg2.pred_population_l2.__defaults__ = (n_authors,)
    try:
        yield {"m": m, "dim": dim, "k_tau": k_tau, "G": g_groups,
               "n_authors": n_authors}
    finally:
        for obj, name, value in reversed(saves):
            setattr(obj, name, value)


# ---------------------------------------------------------------------------
# shared helpers

def boot_index(b_draws: int, seed: int, n_blocks: int) -> np.ndarray:
    """L3's PN-8 world-block resample (l3:1651-1655), same construction."""
    rng = np.random.default_rng(seed)
    return rng.integers(0, n_blocks, size=(b_draws, n_blocks))


def boot_ci(values: np.ndarray, b_draws: int = B_BOOT,
            seed: int = MASTER_SEED) -> dict[str, float]:
    v = np.asarray(values, dtype=float)
    idx = boot_index(b_draws, seed, len(v))
    draws = v[idx].mean(axis=1)
    return {"mean": float(v.mean()), "lo": float(np.quantile(draws, 0.025)),
            "hi": float(np.quantile(draws, 0.975)), "sd": float(np.std(draws, ddof=1)),
            "n_blocks": int(len(v)), "B": int(b_draws), "seed": int(seed)}


def write_json(path: Path, obj: Any) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with _RAW_OPEN(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True, default=float)
        fh.write("\n")


def read_json(path: Path) -> Any:
    return json.loads(_RAW_PATH_READ_TEXT(path, encoding="utf-8"))


# ---------------------------------------------------------------------------
# THE ENERGY CONSTANTS (RN-DO-3): L2's term of art, transported unchanged.
#   sigma_b^2(rho-equivalent) = L1_SIGMA_TAU2 * rho/(1-rho),
#   L1_SIGMA_TAU2 = (3/8) * L1_DELTA^2                          (l2:126-129)

def energies() -> dict[str, float]:
    lg2 = l2()
    return {
        "L1_DELTA": lg2.L1_DELTA,
        "L1_SIGMA_TAU2": lg2.L1_SIGMA_TAU2,
        "SB2_RHO55": lg2.SB2_RHO55,
        "SB2_RHO45": lg2.L1_SIGMA_TAU2 * 0.45 / 0.55,
        "SB2_RHO35": lg2.SB2_RHO35,
        # RN-DO-4: the NAMED COMPANION of RN-D1-1/2 -- the Delta-free rho_id=.55
        # form at G=5's own simplex constant c_5 = (G-1)/(2G) = 0.4.  Computed,
        # reported, NEVER promoted (D1 report Part 0.3, RN-D1-1/2).
        "SB2_RHO55_G5_COMPANION": 0.4 * lg2.L1_DELTA ** 2 * 0.55 / 0.45,
    }


# ---------------------------------------------------------------------------
# M-1 / M-2 -- the typed world at m=96, k_tau=4, G=5, n_occ=8

def boundary_z_realized(world: dict, typ: dict, delta: float, sigma_b2: float,
                        eta: float) -> dict[str, Any]:
    """Per-boundary z = Delta_card/(2 sigma_u) on the REALIZED card geometry,
    computed by the SAME expression l2.predicted_boundary_error_l2 uses
    (l2:384-416, identity_only=True).  Verified bit-exact against that
    function's own output in every call (`phi_mean_residual`)."""
    ka, lg1, lg2 = k2a(), l1(), l2()
    w = ka.arm_weights(lg2.W_INT_ARM)
    tau = lg1.latent_type_vectors(typ["S"], delta)
    mmat = ka.A_SCALE * (world["loadings"] * ka.G_PROFILE)
    tau_card = w["mu"] * (tau @ mmat.T)
    zs, rates, seps = [], [], []
    for g in range(lg2.G_GROUPS):
        for h in range(g + 1, lg2.G_GROUPS):
            diff = tau_card[h] - tau_card[g]
            sep = float(np.linalg.norm(diff))
            u = diff / sep
            mtu = mmat.T @ u
            var = w["mu"] ** 2 * (
                (1.0 - eta) * (sigma_b2 / ka.K_LATENT) * float(mtu @ mtu)
                + eta * (sigma_b2 / lg2.K_TAU) * float(np.sum((typ["S"].T @ mtu) ** 2)))
            z = float("inf") if var <= 0.0 else sep / (2.0 * math.sqrt(var))
            zs.append(z)
            seps.append(sep)
            rates.append(0.0 if var <= 0.0 else 0.5 * math.erfc(z / math.sqrt(2.0)))
    ref = lg2.predicted_boundary_error_l2(world, typ, delta, sigma_b2, eta, True)
    return {"z_mean": float(np.mean(zs)), "z_min": float(np.min(zs)),
            "z_max": float(np.max(zs)), "sigma_u_mean": float(
                np.mean([s / (2.0 * z) for s, z in zip(seps, zs, strict=True)]))
            if all(np.isfinite(zs)) else float("nan"),
            "delta_card_mean": float(np.mean(seps)),
            "n_boundaries": len(zs),
            "rate_closed_form": float(np.mean(rates)),
            "phi_mean_residual": abs(float(np.mean(rates)) - ref)}


def m1_cell_specs(sb2: float, tag: str) -> list[dict[str, Any]]:
    lg2 = l2()
    return [{"cell": f"{tag}_eta{eta:g}", "kind": "C", "rung": -1, "energy": tag,
             "delta": lg2.L1_DELTA, "sigma_b2": sb2, "eta": float(eta)}
            for eta in M1_ETAS]


def run_m1_m2(worlds: tuple[int, ...], energy_tag: str, sb2: float) -> pd.DataFrame:
    lg1, lg2 = l1(), l2()
    if M1_N_AUTHORS % lg2.G_GROUPS != 0:          # RN-DO-8, enforced
        raise SystemExit(
            f"REFUSED: n_authors {M1_N_AUTHORS} is not a multiple of G "
            f"{lg2.G_GROUPS}; l2.type_geometry_l2 would leave authors unlabelled")
    rows = []
    specs = m1_cell_specs(sb2, energy_tag)
    for wi in worlds:
        wseed = lg2.world_seed_for(wi)
        world, typ = lg2.build_typed_world_l2(wseed, M1_N_AUTHORS)
        for spec in specs:
            row = lg2.measure_cell_world(world, typ, spec, wseed)
            row["world"] = wi
            row.update({f"z_{k}": v for k, v in boundary_z_realized(
                world, typ, spec["delta"], spec["sigma_b2"], spec["eta"]).items()})
            row["latent_sigma_u2"] = (spec["eta"] * spec["sigma_b2"] / lg2.K_TAU
                                      + (1.0 - spec["eta"]) * spec["sigma_b2"]
                                      / k2a().K_LATENT)
            row["latent_z"] = spec["delta"] / (2.0 * math.sqrt(row["latent_sigma_u2"]))
            row["latent_rate"] = 0.5 * math.erfc(row["latent_z"] / math.sqrt(2.0))
            row["ari_ambient_chk"] = row["ari_ambient"]
            rows.append(row)
    _ = lg1
    return pd.DataFrame(rows)


def task_m1m2(args: argparse.Namespace) -> dict[str, Any]:
    en = energies()
    worlds = tuple(range(M1_WORLDS))
    out: dict[str, Any] = {"config": {
        "m": M1_M, "k_tau": M1_K_TAU, "G": M1_G, "n_occ": M1_N_OCC,
        "DIM": dim_for(M1_M), "worlds": M1_WORLDS, "n_authors": M1_N_AUTHORS,
        "n_authors_registered": M1_N_AUTHORS_REGISTERED,
        "n_authors_pin": "RN-DO-8: largest multiple of G=5 not exceeding 512",
        "delta": en["L1_DELTA"], "eta_levels": list(M1_ETAS),
        "reading": "PRIMARY (RN-D1-1/2): sigma_b^2 and Delta transported UNCHANGED",
        "sigma_b2_primary": en["SB2_RHO55"],
        "sigma_b2_companion": en["SB2_RHO55_G5_COMPANION"]}}
    with latent_config(M1_M, M1_K_TAU, M1_G, M1_N_AUTHORS):
        frames = {}
        for tag, sb2 in (("rho55eq", en["SB2_RHO55"]),
                         ("rho55eqG5companion", en["SB2_RHO55_G5_COMPANION"])):
            t0 = time.time()
            df = run_m1_m2(worlds, tag, sb2)
            df.to_csv(OUT / f"m1_cells_{tag}.csv", index=False)
            frames[tag] = df
            print(f"  [{tag}] {len(df)} rows in {time.time() - t0:.1f}s", flush=True)
    for tag, df in frames.items():
        per_eta = {}
        for eta in M1_ETAS:
            sub = df[df["eta"] == eta].sort_values("world")
            per_eta[f"eta{eta:g}"] = {
                "eta": float(eta),
                "measured_boundary_err_true_card": boot_ci(
                    sub["boundary_err_true_card"].to_numpy(float)),
                "per_world_boundary_err_true_card": [
                    float(x) for x in sub["boundary_err_true_card"]],
                "measured_boundary_err_full_card": boot_ci(
                    sub["boundary_err_full_card"].to_numpy(float)),
                "realized_floor_pred_identity_card": boot_ci(
                    sub["floor_pred_identity"].to_numpy(float)),
                "latent_sigma_u2": float(sub["latent_sigma_u2"].iloc[0]),
                "latent_z": float(sub["latent_z"].iloc[0]),
                "latent_rate": float(sub["latent_rate"].iloc[0]),
                "realized_z_mean": boot_ci(sub["z_z_mean"].to_numpy(float)),
                "realized_delta_card_mean": boot_ci(
                    sub["z_delta_card_mean"].to_numpy(float)),
                "ari_ambient": boot_ci(sub["ari_ambient"].to_numpy(float)),
                "ari_oracleS": boot_ci(sub["ari_oracleS"].to_numpy(float)),
                "realized_eta": boot_ci(sub["realized_eta"].to_numpy(float)),
                "realized_sigma_b2": boot_ci(sub["realized_sigma_b2"].to_numpy(float)),
                "z_closed_form_residual_max": float(sub["z_phi_mean_residual"].max()),
            }
        out[tag] = {"per_eta": per_eta}
        # --- M-2: ISO (eta=0) vs ALIGNED (eta=1) at matched identity energy
        e0 = df[df["eta"] == 0.0].sort_values("world")
        e1 = df[df["eta"] == 1.0].sort_values("world")
        z0 = e0["z_z_mean"].to_numpy(float)
        z1 = e1["z_z_mean"].to_numpy(float)
        ari_drop = (e0["ari_ambient"].to_numpy(float) - e1["ari_ambient"].to_numpy(float))
        lg1 = l1()
        with latent_config(M1_M, M1_K_TAU, M1_G, M1_N_AUTHORS):
            lat_ratio_rho = {
                f"rho{r:g}": float(lg1.identity_only_z(M1_M, r)
                                   / lg1.identity_only_z(M1_K_TAU, r))
                for r in (0.15, 0.35, 0.55, 0.75)}
        out[tag]["m2"] = {
            "latent_z_ratio_sqrt_m_over_ktau": math.sqrt(M1_M / M1_K_TAU),
            "latent_z_ratio_via_l1_identity_only_z": lat_ratio_rho,
            "latent_z_ratio_max_abs_dev_from_sqrt24": max(
                abs(v - math.sqrt(M1_M / M1_K_TAU)) for v in lat_ratio_rho.values()),
            "latent_z2_ratio_m_over_ktau": float(M1_M) / float(M1_K_TAU),
            "realized_card_z_ratio": boot_ci(z0 / z1),
            "realized_card_z2_ratio": boot_ci((z0 / z1) ** 2),
            "measured_rate_ratio_eta1_over_eta0": (
                float(e1["boundary_err_true_card"].mean()
                      / e0["boundary_err_true_card"].mean())
                if float(e0["boundary_err_true_card"].mean()) > 0 else float("inf")),
            "ari_iso_eta0": boot_ci(e0["ari_ambient"].to_numpy(float)),
            "ari_aligned_eta1": boot_ci(e1["ari_ambient"].to_numpy(float)),
            "ari_drop_iso_minus_aligned": boot_ci(ari_drop),
            "ari_drop_direction_positive": bool(float(ari_drop.mean()) > 0.0),
            "ari_drop_per_world_all_positive": bool(bool((ari_drop > 0).all())),
            "eta_ordering_rates": [
                float(df[df["eta"] == e]["boundary_err_true_card"].mean())
                for e in M1_ETAS],
            "eta_ordering_strict_increasing": bool(all(
                float(df[df["eta"] == a]["boundary_err_true_card"].mean())
                < float(df[df["eta"] == b]["boundary_err_true_card"].mean())
                for a, b in zip(M1_ETAS[:-1], M1_ETAS[1:], strict=True))),
            "eta_ordering_strict_increasing_latent": bool(all(
                float(df[df["eta"] == a]["latent_rate"].iloc[0])
                < float(df[df["eta"] == b]["latent_rate"].iloc[0])
                for a, b in zip(M1_ETAS[:-1], M1_ETAS[1:], strict=True))),
        }
    _ = args
    return out


# ---------------------------------------------------------------------------
# M-3 -- the T-arm ladder at two (m, n) settings

def task_m3(args: argparse.Namespace, m: int, n: int) -> dict[str, Any]:
    lg2 = l2()
    t0 = time.time()
    with latent_config(m, 3, 4, n) as cfg:
        grid = lg2.ladder_grid()
        ladder = lg2.solve_ladder(grid)
        js = lg2.joint_satisfiability(grid, ladder["delta"])
    grid.to_csv(OUT / f"m3_grid_m{m}_n{n}.csv", index=False)
    ci = js["clause_delta_intervals"]
    amb = ci["W-1a (ambient < 0.30)"]
    orc = ci["W-1a (oracle-S > 0.80)"]
    upper = None if amb is None else float(amb[1])          # ambient < .30 up to here
    lower = None if orc is None else float(orc[0])          # oracle-S > .80 from here
    win = js["W1_window"]
    resolved = (upper is not None) and (lower is not None)
    width = (upper - lower) if resolved else None
    out = {
        "config": {**cfg, "gamma_d_over_n": float(m) / float(n),
                   "grid": {"lo": lg2.LADDER_GRID_LO, "hi": lg2.LADDER_GRID_HI,
                            "n": lg2.LADDER_GRID_N, "reps": lg2.LADDER_REPS},
                   "sigma_b2": lg2.SB2_RHO55, "eta": 0.0,
                   "d_pinned_to": "latent m (RN-D1-5)"},
        "ambient_edge_upper": upper,
        "oracleS_edge_lower": lower,
        "window_width_upper_minus_lower": width,
        "window_open": bool(win["satisfiable_anywhere_in_delta"]),
        "window_call": ("OPEN" if win["satisfiable_anywhere_in_delta"] else "EMPTY")
        if resolved else "UNRESOLVABLE",
        "window_n_grid_points": int(win["n_grid_points"]),
        "window_delta_interval": win["delta_interval"],
        "resolved": bool(resolved),
        "clause_delta_intervals": ci,
        "ladder": ladder,
        "ambient_curve_max": float(np.maximum.accumulate(
            grid["ambient"].to_numpy(float))[-1]),
        "oracleS_curve_max": float(np.maximum.accumulate(
            grid["oracleS"].to_numpy(float))[-1]),
        "oracle_centroid_curve_max": float(np.maximum.accumulate(
            grid["oracle_centroid"].to_numpy(float))[-1]),
        "seconds": time.time() - t0,
    }
    _ = args
    return out


# ---------------------------------------------------------------------------
# M-4 -- the K2b gauge arm (share .40, phi .90), 32 worlds

def task_m4(args: argparse.Namespace) -> dict[str, Any]:
    kb = k2b()
    w = kb.arm_weights(M4_SHARE, "zero")
    rows = []
    t0 = time.time()
    for wi in range(M4_WORLDS):
        wseed = kb.world_seed_for(wi)
        world = kb.build_k2b_world(wseed, M4_PHI)
        row = kb.run_field_world("DOPEN-S4", wi, world, w, verify=(wi == 0))
        row["world"] = wi
        rows.append(row)
        if (wi + 1) % 8 == 0:
            print(f"  m4: {wi + 1}/{M4_WORLDS} worlds, {time.time() - t0:.1f}s",
                  flush=True)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "m4_field_rows.csv", index=False)
    k2e = _load("run_suica_m4_k2e_double_matching")
    k2c = _load("run_suica_m4_k2c_matched_pairs")
    return {
        "config": {"share": M4_SHARE, "phi": M4_PHI, "w_int_arm": "zero",
                   "worlds": M4_WORLDS,
                   "instrument": "k2b.run_field_world (985-author K1-pinned panel, "
                                 "F2 m-multiset, 4 contexts)",
                   "arm_shares": kb.arm_shares(M4_SHARE, "zero")},
        "measured_recovery_b_only": boot_ci(df["recovery_b_only"].to_numpy(float)),
        "per_world_recovery_b_only": [float(x) for x in df["recovery_b_only"]],
        "measured_recovery_mixed": boot_ci(df["recovery_mixed"].to_numpy(float)),
        "measured_recovery_gap": boot_ci(
            df["recovery_gap_mixed_minus_b"].to_numpy(float)),
        "law_inputs": {
            "r_card_b_pred_raw": k2c.predicted_attenuation(M4_SHARE, M4_PHI),
            "V_person_design": k2e.person_share_design(M4_SHARE, 0.0),
        },
        "seconds": time.time() - t0,
    }


# ---------------------------------------------------------------------------
# M-5 -- the L3 taxometer at eta = 0.6, rho.45-equivalent

def task_m5(args: argparse.Namespace) -> dict[str, Any]:
    lg3, lg2 = l3(), l2()
    en = energies()
    spec = {"cell": "C_rho45eq_eta0.6", "kind": "C", "energy": "rho45eq",
            "delta": lg2.L1_DELTA, "sigma_b2": en["SB2_RHO45"], "eta": M5_ETA}
    rows = []
    t0 = time.time()
    for wi in range(M5_WORLDS):
        wseed = lg3.world_seed_for(wi)
        world, typ = lg2.build_typed_world_l2(wseed, M5_N_AUTHORS)
        row = lg3.measure_cell_world(world, typ, spec, wseed)
        row["world"] = wi
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "m5_cell_rho45eq_eta0.6.csv", index=False)
    keys = ("eta_hat_P", "eta_hat_S", "eta_hat_T", "etaw_oracle_P", "etaw_split_P",
            "etaw_flat_P", "etaw_marg_P", "eta_hat_angle_P", "realized_eta",
            "realized_sigma_b2", "ari_primary", "boundary_err_true_card",
            "floor_pred_identity", "whitener_condition")
    out = {"config": {"eta": M5_ETA, "energy": "rho.45-equivalent",
                      "sigma_b2": en["SB2_RHO45"], "delta": lg2.L1_DELTA,
                      "m": 48, "k_tau": 3, "G": 4, "worlds": M5_WORLDS,
                      "n_authors": M5_N_AUTHORS,
                      "primary_route": "eta_hat_P (state whitener, Lloyd grouping)",
                      "certified_tolerance_X2": lg3.X2_TOL},
           "measured": {k: boot_ci(df[k].to_numpy(float)) for k in keys if k in df},
           "per_world_eta_hat_P": [float(x) for x in df["eta_hat_P"]],
           "eta_hat_P_clipped": boot_ci(
               np.clip(df["eta_hat_P"].to_numpy(float), 0.0, 1.0)),
           "seconds": time.time() - t0}
    out["measured_eta_hat"] = out["measured"]["eta_hat_P"]
    return out


# ---------------------------------------------------------------------------
# PART 0 -- provenance, realizability pilots (rule 17), enumeration (rule 16)

CELLS = ("PREDICTED", "MISSED", "UNRESOLVABLE")
ENTRIES = ("S-1", "S-2", "S-3", "S-4", "S-5")
LAW_ENTRIES = ("S-1", "S-2", "S-4", "S-5")


def route_reading_a(cells: dict[str, str]) -> str:
    """PRIMARY (registration-literal): >=4/5 PREDICTED over ALL FIVE entries."""
    return ("LAWS-PREDICT" if sum(1 for e in ENTRIES if cells[e] == "PREDICTED") >= 4
            else "PER-ENTRY-ADJUDICATION")


def route_reading_b(cells: dict[str, str]) -> str:
    """DECLARED SECOND READING: S-3 excluded from the numerator, so the bar is
    all four MEASURED-LAW entries PREDICTED."""
    return ("LAWS-PREDICT"
            if sum(1 for e in LAW_ENTRIES if cells[e] == "PREDICTED") >= 4
            else "PER-ENTRY-ADJUDICATION")


def s3_verdict(cell: str, open_at_192: bool | None,
               empty_at_48: bool | None) -> str:
    if cell == "UNRESOLVABLE":
        return "CONJECTURE-UNRESOLVED"
    if cell == "PREDICTED" and open_at_192 and empty_at_48:
        return "CONJECTURE-SUPPORTED"
    return "CONJECTURE-DEAD"


def build_enumeration() -> tuple[pd.DataFrame, dict[str, Any]]:
    import itertools
    rows = []
    for combo in itertools.product(CELLS, repeat=5):
        cells = dict(zip(ENTRIES, combo, strict=True))
        rows.append({**{f"cell_{k}": v for k, v in cells.items()},
                     "n_predicted_all5": sum(1 for v in combo if v == "PREDICTED"),
                     "n_predicted_laws4": sum(
                         1 for e in LAW_ENTRIES if cells[e] == "PREDICTED"),
                     "route_A_primary": route_reading_a(cells),
                     "route_B_second": route_reading_b(cells)})
    df = pd.DataFrame(rows)
    audit = {
        "rows": int(len(df)), "expected": 3 ** 5,
        "unique_keys": int(df[[f"cell_{e}" for e in ENTRIES]]
                           .drop_duplicates().shape[0]),
        "all_routed_A": bool(df["route_A_primary"].isin(
            ["LAWS-PREDICT", "PER-ENTRY-ADJUDICATION"]).all()),
        "all_routed_B": bool(df["route_B_second"].isin(
            ["LAWS-PREDICT", "PER-ENTRY-ADJUDICATION"]).all()),
        "route_A_counts": {k: int(v) for k, v in
                           df["route_A_primary"].value_counts().items()},
        "route_B_counts": {k: int(v) for k, v in
                           df["route_B_second"].value_counts().items()},
        "readings_agree_rows": int((df["route_A_primary"]
                                    == df["route_B_second"]).sum()),
        "s3_subverdicts": ["CONJECTURE-SUPPORTED", "CONJECTURE-DEAD",
                           "CONJECTURE-UNRESOLVED"],
    }
    audit["no_gap_no_overlap"] = bool(
        audit["rows"] == audit["expected"] == audit["unique_keys"]
        and audit["all_routed_A"] and audit["all_routed_B"])
    return df, audit


def run_part0(args: argparse.Namespace) -> None:
    t0 = time.time()
    log_event("PART0", "start")
    OUT.mkdir(parents=True, exist_ok=True)
    en = energies()
    ka, lg1, lg2, lg3, kb = k2a(), l1(), l2(), l3(), k2b()

    prov = {
        "committed_hash": COMMITTED_HASH,
        "d1_public_hash_file": str(
            (ROOT / "results/d1_sealed/D1_PUBLIC_HASH.json").relative_to(ROOT)),
        "d1_public_hash_value": read_json(
            ROOT / "results/d1_sealed/D1_PUBLIC_HASH.json")["sha256_salted"],
        "bundle_present": BUNDLE.exists(),
        "bundle_bytes": BUNDLE.stat().st_size if BUNDLE.exists() else None,
        "machinery": {
            "M-1/M-2": "scripts/run_suica_m4_l1_typed_world.py + "
                       "scripts/run_suica_m4_l2_threshold_continuum.py",
            "M-3": "scripts/run_suica_m4_l2_threshold_continuum.py "
                   "(ladder_grid/solve_ladder/joint_satisfiability)",
            "M-4": "scripts/run_suica_m4_k2b_t4_branch.py (run_field_world)",
            "M-5": "scripts/run_suica_m4_l3_taxometer_meter.py (measure_cell_world)",
        },
        "baseline_constants": {
            "k2a.K_LATENT": ka.K_LATENT, "k2a.DIM": ka.DIM,
            "l1.K_TAU": lg1.K_TAU, "l1.G_GROUPS": lg1.G_GROUPS,
            "l1.SIGMA_TAU2_PER_DELTA2": lg1.SIGMA_TAU2_PER_DELTA2,
            "l2.L1_DELTA": lg2.L1_DELTA, "l2.SB2_RHO55": lg2.SB2_RHO55,
            "l2.SB2_RHO35": lg2.SB2_RHO35, "l3.X2_TOL": lg3.X2_TOL,
            "k2b.NOISE_SHARE": kb.NOISE_SHARE,
        },
        "energies": en,
    }

    # --- RN-DO-2 audit: the simplex generalization
    simplex = {f"G{g}": simplex_audit(g) for g in (4, 5)}
    simplex["G4_matches_l1_constant"] = bool(
        abs(simplex["G4"]["sigma_tau2_per_delta2"] - lg1.SIGMA_TAU2_PER_DELTA2) < 1e-15)

    # --- RN-DO-1 audit: the dimension transport
    transport = {f"m{m}": {"DIM": dim_for(m), "ratio": dim_for(m) / m,
                           "orthonormal_feasible": dim_for(m) >= m,
                           "dim64_feasible": 64 >= m}
                 for m in (48, 96, 192)}
    transport["m48_reproduces_k2a"] = bool(dim_for(48) == ka.DIM)

    # --- G2O realizability pilots (rule 17), on RESERVED pilot worlds only
    pilots: dict[str, Any] = {}

    t = time.time()
    with latent_config(M1_M, M1_K_TAU, M1_G, M1_N_AUTHORS):
        df = run_m1_m2(tuple(lg2.PILOT_WORLDS[:2]), "pilotA", en["SB2_RHO55"])
    pilots["m1m2"] = {
        "worlds": list(lg2.PILOT_WORLDS[:2]),
        "per_eta_rate": {f"eta{e:g}": float(
            df[df["eta"] == e]["boundary_err_true_card"].mean()) for e in M1_ETAS},
        "per_eta_latent_rate": {f"eta{e:g}": float(
            df[df["eta"] == e]["latent_rate"].iloc[0]) for e in M1_ETAS},
        "per_eta_ari_ambient": {f"eta{e:g}": float(
            df[df["eta"] == e]["ari_ambient"].mean()) for e in M1_ETAS},
        "all_finite": bool(np.isfinite(df["boundary_err_true_card"]).all()),
        "closed_form_residual_max": float(df["z_phi_mean_residual"].max()),
        "realized_eta_max_dev": float(np.max(np.abs(
            df["realized_eta"].to_numpy(float) - df["eta"].to_numpy(float)))),
        "realized_sigma_b2_mean": float(df["realized_sigma_b2"].mean()),
        "designed_sigma_b2": en["SB2_RHO55"],
        "informative_cells_eta_gt_0": bool(all(
            0.0 < float(df[df["eta"] == e]["boundary_err_true_card"].mean()) < 1.0
            for e in (0.5, 1.0))),
        "eta0_degenerate_precovered_by_sealed_absolute_band": True,
        "seconds": time.time() - t,
    }

    t = time.time()
    m3_probe = {}
    for m, n in M3_SETTINGS:
        with latent_config(m, 3, 4, n):
            pop = lg2.pred_population_l2(lg2.L1_DELTA, lg2.SB2_RHO55, 0.0,
                                         lg2.pred_seed(0))
            m3_probe[f"m{m}_n{n}"] = {
                "card_shape": list(pop["card"].shape),
                "gamma_d_over_n": float(m) / float(n),
                "sqrt_gamma": math.sqrt(float(m) / float(n)),
                "finite": bool(np.isfinite(pop["card"]).all()),
                "loadings_orthonormal_feasible": dim_for(m) >= m,
                "DIM": dim_for(m)}
    pilots["m3"] = {
        "probe": m3_probe,
        "note": "the fixed grid IS the realizability check: both clause sets "
                "(ambient<0.30, oracle-S>0.80) must be non-empty on "
                "geomspace(0.75, 9.0, 34); an empty set at a setting scores "
                "UNRESOLVABLE (pre-declared, never re-designed, grid never moved)",
        "seconds": time.time() - t}

    t = time.time()
    w = kb.arm_weights(M4_SHARE, "zero")
    prow = kb.run_field_world("DOPEN-PILOT", kb.PILOT_WORLDS[0],
                              kb.build_k2b_world(
                                  kb.world_seed_for(kb.PILOT_WORLDS[0]), M4_PHI),
                              w, verify=True)
    pilots["m4"] = {
        "pilot_world": int(kb.PILOT_WORLDS[0]),
        "recovery_b_only": float(prow["recovery_b_only"]),
        "recovery_mixed": float(prow["recovery_mixed"]),
        "finite": bool(np.isfinite(prow["recovery_b_only"])),
        "non_saturated": bool(0.0 < prow["recovery_b_only"] < 1.0),
        "reconstruction_residual": float(prow.get("g4b_reconstruction_residual", 0.0)),
        "truth_b_route_residual": float(prow.get("g4b_truth_b_route_residual", 0.0)),
        "realized_shares": prow.get("realized_shares"),
        "seconds": time.time() - t,
    }

    t = time.time()
    en45 = en["SB2_RHO45"]
    spec = {"cell": "PILOT_rho45eq_eta0.6", "kind": "C", "energy": "rho45eq",
            "delta": lg2.L1_DELTA, "sigma_b2": en45, "eta": M5_ETA}
    pw = lg3.PILOT_WORLDS[0]
    wobj, typ = lg2.build_typed_world_l2(lg3.world_seed_for(pw), M5_N_AUTHORS)
    prow5 = lg3.measure_cell_world(wobj, typ, spec, lg3.world_seed_for(pw))
    pilots["m5"] = {
        "pilot_world": int(pw), "sigma_b2": en45,
        "eta_hat_P": float(prow5["eta_hat_P"]),
        "realized_eta": float(prow5["realized_eta"]),
        "realized_sigma_b2": float(prow5["realized_sigma_b2"]),
        "finite": bool(np.isfinite(prow5["eta_hat_P"])),
        "whitener_condition": float(prow5["whitener_condition"]),
        "seconds": time.time() - t,
    }

    enum_df, enum_audit = build_enumeration()
    enum_df.to_csv(OUT / "part0_enumeration.csv", index=False)

    gates = {
        "leg": "D-open", "banner": BANNER, "part0_utc": _utc(),
        "master_seed": MASTER_SEED, "B_BOOT": B_BOOT, "B_BOOT_HIGH": B_BOOT_HIGH,
        "G0O_provenance": prov,
        "RN_DO_1_dimension_transport": transport,
        "RN_DO_2_simplex": simplex,
        "G2O_realizability_pilots": pilots,
        "G4O_enumeration": enum_audit,
        "seconds": time.time() - t0,
    }
    write_json(OUT / "part0_gates.json", gates)
    log_event("PART0", "done", seconds=time.time() - t0)
    print(json.dumps({"part0_seconds": gates["seconds"],
                      "enumeration_ok": enum_audit["no_gap_no_overlap"],
                      "pilots": {k: v.get("seconds") for k, v in pilots.items()}},
                     indent=1))
    _ = args


# ---------------------------------------------------------------------------
# STAGE 1 / SEAL

TASKS = {"m1m2": task_m1m2, "m4": task_m4, "m5": task_m5,
         "m3_48_512": lambda a: task_m3(a, 48, 512),
         "m3_192_256": lambda a: task_m3(a, 192, 256)}


def run_stage1(args: argparse.Namespace) -> None:
    if MEASURED_STAMP.exists():
        raise SystemExit("REFUSED: measured.json is already stamped; Stage 1 is closed")
    name = args.task
    if name not in TASKS:
        raise SystemExit(f"REFUSED: unknown task {name!r}")
    log_event("STAGE1", "task_start", task=name)
    t0 = time.time()
    result = TASKS[name](args)
    result["_task"] = name
    result["_utc"] = _utc()
    result["_seconds"] = time.time() - t0
    write_json(OUT / f"stage1_{name}.json", result)
    log_event("STAGE1", "task_done", task=name, seconds=result["_seconds"])
    print(f"[{name}] done in {result['_seconds']:.1f}s -> stage1_{name}.json")


def run_seal(args: argparse.Namespace) -> None:
    """Assemble measured.json from the per-task artifacts, hash it, stamp it.
    This is the LAST act of Stage 1 and the gate on Stage 2."""
    if MEASURED_STAMP.exists():
        raise SystemExit("REFUSED: already stamped (never re-stamp)")
    parts = {}
    for name in TASKS:
        path = OUT / f"stage1_{name}.json"
        if not path.exists():
            raise SystemExit(f"REFUSED: missing Stage-1 artifact {path}")
        parts[name] = read_json(path)
    gates = read_json(OUT / "part0_gates.json")
    measured = {
        "leg": "D-open", "stage": "1 (MEASURE, written before any unsealing)",
        "banner": BANNER,
        "written_utc": _utc(),
        "master_seed": MASTER_SEED, "B": B_BOOT, "B_high": B_BOOT_HIGH,
        "part0_utc": gates["part0_utc"],
        "pins": {
            "RN-DO-1": "DIM(m) = 4m/3 (64/128/256 at m = 48/96/192); every k2a "
                       "generator constant recomputed by its own published formula",
            "RN-DO-2": "regular (G-1)-simplex at unit pairwise separation; "
                       "sigma_tau^2/Delta^2 = (G-1)/(2G) (3/8 at G=4 = l1's own)",
            "RN-DO-3": "rho-equivalent energies are L2's term of art: "
                       "sigma_b^2 = (3/8) L1_DELTA^2 * rho/(1-rho)",
            "RN-DO-4": "S-1 PRIMARY = RN-D1-1/2's reading (sigma_b^2 and Delta "
                       "transported UNCHANGED); the G=5-consistent Delta-free form "
                       "is measured as the NAMED COMPANION and cannot be promoted",
            "RN-DO-5": "S-3's d = the LATENT dimension m (RN-D1-5); window = "
                       "[oracle-S>0.80 edge, ambient<0.30 edge] off l2's own "
                       "joint_satisfiability clause intervals",
            "RN-DO-6": "S-2's measured content = (i) the latent z-ratio through "
                       "l1.identity_only_z (algebraic, 1e-12), (ii) the ARI-drop "
                       "direction, (iii) the strict eta-ordering of the rates; the "
                       "card-space realized ratio is a disclosed companion",
        },
        "M-1_M-2": parts["m1m2"],
        "M-3": {"(48,512)": parts["m3_48_512"], "(192,256)": parts["m3_192_256"],
                "measured_scale_factor_ambient_edge": (
                    parts["m3_192_256"]["ambient_edge_upper"]
                    / parts["m3_48_512"]["ambient_edge_upper"]
                    if parts["m3_192_256"]["ambient_edge_upper"]
                    and parts["m3_48_512"]["ambient_edge_upper"] else None),
                "bbp_scale_factor_(gamma2/gamma1)^0.25": (
                    (192.0 / 256.0) / (48.0 / 512.0)) ** 0.25},
        "M-4": parts["m4"],
        "M-5": parts["m5"],
    }
    write_json(MEASURED, measured)
    digest = hashlib.sha256(_RAW_PATH_READ_BYTES(MEASURED)).hexdigest()
    stamped = _utc()
    write_json(MEASURED_STAMP, {
        "measured_path": str(MEASURED.relative_to(ROOT)),
        "measured_sha256": digest,
        "measured_bytes": MEASURED.stat().st_size,
        "stamped_utc": stamped,
        "bundle_reads_before_stamp": len(_BUNDLE_READS),
        "note": "G1O: this stamp is the gate on any read of the D1 sealed bundle"})
    log_event("SEAL", "measured_stamped", sha256=digest)
    print(json.dumps({"measured_sha256": digest, "stamped_utc": stamped,
                      "bytes": MEASURED.stat().st_size}, indent=1))
    _ = args


# ---------------------------------------------------------------------------
# STAGE 2 -- unseal, verify, score

def find_salt(bundle: dict[str, Any], predictions: Any) -> dict[str, Any]:
    """Schema-agnostic: recover the salt by RECOMPUTING the committed hash.
    Nothing about the bundle's field names is assumed."""
    canonical = json.dumps(predictions, sort_keys=True)
    cands: list[tuple[str, str]] = []

    def walk(obj: Any, path: str) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(v, f"{path}/{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")
        elif isinstance(obj, str):
            cands.append((path, obj))

    walk(bundle, "")
    cands.sort(key=lambda kv: (0 if "salt" in kv[0].lower() else 1, len(kv[0])))
    for path, value in cands:
        digest = hashlib.sha256((value + canonical).encode()).hexdigest()
        if digest == COMMITTED_HASH:
            return {"salt_field": path, "recomputed_sha256": digest, "match": True,
                    "candidates_tried": cands.index((path, value)) + 1}
    return {"salt_field": None, "recomputed_sha256": None, "match": False,
            "candidates_tried": len(cands)}


def run_stage2(args: argparse.Namespace) -> None:
    permit = grant_permit()
    log_event("STAGE2", "permit_granted", **permit)
    bundle = read_json(BUNDLE)
    first_read = _BUNDLE_READS[0] if _BUNDLE_READS else None
    predictions = bundle.get("predictions")
    if predictions is None:
        raise SystemExit("REFUSED: bundle has no 'predictions' key")
    verdict = find_salt(bundle, predictions)
    view = {"top_level_keys": sorted(bundle.keys()),
            "hash_verification": {**verdict, "committed": COMMITTED_HASH,
                                  "MATCH": bool(verdict["match"])},
            "permit": permit,
            "first_bundle_read": first_read,
            "predictions": predictions}
    write_json(OUT / "opened_bundle_view.json", view)
    print(json.dumps({"MATCH": verdict["match"], "salt_field": verdict["salt_field"],
                      "entries": list(predictions) if isinstance(predictions, dict)
                      else len(predictions)}, indent=1))
    if not verdict["match"]:
        raise SystemExit("SEAL-TAMPERED: the recomputed hash does not match the "
                         "committed hash.  This is a leg-stopping event.")
    if args.dump_only:
        return
    score(bundle, predictions, permit, first_read)


def _cell(inside: bool | None) -> str:
    if inside is None:
        return "UNRESOLVABLE"
    return "PREDICTED" if inside else "MISSED"


# --- THE PART-0 MAPPING TABLE (pinned BEFORE Stage 1; see the report Part 0.5).
# Each sealed entry's own quantity -> the measured.json field that carries it.
# The scorer below implements exactly this mapping against the field NAMES the
# bundle turns out to use; it has no other freedom, and it never touches a band.
MAPPING = {
    "S-1": "M-1_M-2/rho55eq/per_eta/eta{E}/measured_boundary_err_true_card/mean",
    "S-2": ("M-1_M-2/rho55eq/m2/latent_z_ratio_via_l1_identity_only_z (algebraic), "
            "ari_drop_direction_positive, eta_ordering_strict_increasing"),
    "S-3": ("M-3/(48,512)|(192,256)/{oracleS_edge_lower, ambient_edge_upper, "
            "window_width_upper_minus_lower, window_call}"),
    "S-4": "M-4/measured_recovery_b_only/mean",
    "S-5": "M-5/measured_eta_hat/mean",
}


def dig(obj: Any, *path: str) -> Any:
    for key in path:
        obj = obj[key]
    return obj


def inside(value: float, lo: float, hi: float) -> bool:
    """Closed interval: the sealed bands are stated as [lo, hi]."""
    return bool(lo <= value <= hi)


def interp_edges(m: int, n: int) -> dict[str, Any]:
    """DISCLOSED POST-HOC COMPANION (never scored).  L2 itself reads its
    fidelity-row break points with np.interp (l2:876-880) while its rule-18
    clause intervals -- the fields D1's baseline edges are quoted from, and the
    reading pinned as RN-DO-5 before Stage 1 -- are GRID points.  This function
    reports what the interpolated reading would have said."""
    df = pd.read_csv(OUT / f"m3_grid_m{m}_n{n}.csv", float_precision="round_trip")
    d = df["delta"].to_numpy(float)
    amb = np.maximum.accumulate(df["ambient"].to_numpy(float))
    orc = np.maximum.accumulate(df["oracleS"].to_numpy(float))
    upper = float(np.interp(0.30, amb, d))          # ambient reaches .30 here
    lower = float(np.interp(0.80, orc, d))          # oracle-S reaches .80 here
    return {"ambient_edge_upper_interp": upper, "oracleS_edge_lower_interp": lower,
            "width_interp": upper - lower,
            "call_interp": "OPEN" if upper > lower else "EMPTY"}


def score_entries(predictions: Any, measured: dict[str, Any]) -> dict[str, Any]:
    """The Part-0 mapping table, applied.  No band is touched, no value refitted."""
    ents = {e["id"]: e for e in predictions["entries"]}
    prim = measured["M-1_M-2"]["rho55eq"]["per_eta"]
    m2 = measured["M-1_M-2"]["rho55eq"]["m2"]
    card: dict[str, Any] = {"entries": {}}

    # --- S-1 -----------------------------------------------------------------
    s1 = ents["S-1"]
    rows, ok = [], True
    for key in ("eta0", "eta0.5", "eta1"):
        band = s1["primary"][key]["falsification_band"]
        val = prim[key]["measured_boundary_err_true_card"]["mean"]
        cell_ok = inside(val, band["lo"], band["hi"])
        ok = ok and cell_ok
        rows.append({"eta": key, "measured": val,
                     "sealed_predicted": s1["primary"][key]["predicted_per_boundary_rate"],
                     "band_lo": band["lo"], "band_hi": band["hi"],
                     "band_kind": band["kind"], "inside": cell_ok,
                     "ci": prim[key]["measured_boundary_err_true_card"],
                     "on_band_edge": bool(val in (band["lo"], band["hi"]))})
    card["entries"]["S-1"] = {
        "grade": s1["grade"], "cell": _cell(ok), "rows": rows,
        "sealed_band_rule": s1["band_rule"],
        "companion_reported_not_promoted": {
            key: {"measured": measured["M-1_M-2"]["rho55eqG5companion"]["per_eta"][key][
                "measured_boundary_err_true_card"]["mean"],
                  "sealed": s1["companion_delta_free_G5_consistent"][key][
                      "predicted_per_boundary_rate"]}
            for key in ("eta0", "eta0.5", "eta1")},
        "sealed_boundary_z_vs_measured_latent_z": {
            key: {"sealed": s1["primary"][key]["boundary_z"],
                  "measured_latent": prim[key]["latent_z"],
                  "residual": abs(s1["primary"][key]["boundary_z"] - prim[key]["latent_z"])}
            for key in ("eta0", "eta0.5", "eta1")},
    }

    # --- S-2 -----------------------------------------------------------------
    s2 = ents["S-2"]
    tol = s2["falsification_band"]["algebraic_tolerance"]
    ratio_dev = m2["latent_z_ratio_max_abs_dev_from_sqrt24"]
    z2_dev = abs(m2["latent_z2_ratio_m_over_ktau"] - s2["predicted_z2_ratio"])
    aris = [prim[k]["ari_ambient"]["mean"] for k in ("eta0", "eta0.5", "eta1")]
    ari_strict_drop = bool(aris[0] > aris[1] > aris[2])
    rate_strict_up = bool(m2["eta_ordering_strict_increasing"])
    ok2 = bool(ratio_dev <= tol and z2_dev <= tol and ari_strict_drop and rate_strict_up)
    card["entries"]["S-2"] = {
        "grade": s2["grade"], "cell": _cell(ok2),
        "sealed_z_ratio": s2["predicted_z_ratio"],
        "measured_z_ratio_latent": m2["latent_z_ratio_via_l1_identity_only_z"],
        "max_abs_dev": ratio_dev, "algebraic_tolerance": tol,
        "ratio_within_tolerance": bool(ratio_dev <= tol),
        "sealed_z2_ratio": s2["predicted_z2_ratio"],
        "measured_z2_ratio": m2["latent_z2_ratio_m_over_ktau"],
        "z2_within_tolerance": bool(z2_dev <= tol),
        "sealed_direction_claim": s2["falsification_band"]["direction_claim"],
        "measured_ari_eta0_eta05_eta1": aris,
        "ari_strictly_decreasing_in_eta": ari_strict_drop,
        "measured_rates_eta0_eta05_eta1": m2["eta_ordering_rates"],
        "rate_strictly_increasing_in_eta": rate_strict_up,
        "ari_drop_ci": m2["ari_drop_iso_minus_aligned"],
        "kill_condition_fired": not ok2,
        "disclosed_companion_realized_card_z_ratio": m2["realized_card_z_ratio"]["mean"],
    }

    # --- S-3 -----------------------------------------------------------------
    s3 = ents["S-3"]
    settings = {(s["d"], s["n"]): s for s in s3["settings"]}
    rows3, all_ok, calls = [], True, {}
    for (d, n), key in (((48, 512), "(48,512)"), ((192, 256), "(192,256)")):
        sealed = settings[(d, n)]
        band = sealed["falsification_band"]
        meas = measured["M-3"][key]
        lo_ok = inside(meas["oracleS_edge_lower"], *band["lower_edge_interval"])
        hi_ok = inside(meas["ambient_edge_upper"], *band["upper_edge_interval"])
        call_ok = meas["window_call"] == sealed["predicted_state"]
        calls[key] = call_ok
        all_ok = all_ok and lo_ok and hi_ok and call_ok
        rows3.append({
            "setting": key, "gamma": sealed["gamma"],
            "sealed_lower_edge": sealed["predicted_lower_edge_delta"],
            "measured_lower_edge": meas["oracleS_edge_lower"],
            "lower_band": band["lower_edge_interval"], "lower_inside": lo_ok,
            "sealed_upper_edge": sealed["predicted_upper_edge_delta"],
            "measured_upper_edge": meas["ambient_edge_upper"],
            "upper_band": band["upper_edge_interval"], "upper_inside": hi_ok,
            "sealed_width": sealed["predicted_window_width"],
            "measured_width": meas["window_width_upper_minus_lower"],
            "sealed_state": sealed["predicted_state"],
            "measured_state": meas["window_call"],
            "PRIMARY_FALSIFIER_binary_call_ok": call_ok,
            "sealed_scale_vs_baseline": sealed["scale_vs_baseline"],
            "interp_companion_post_hoc": interp_edges(d, n)})
    card["entries"]["S-3"] = {
        "grade": s3["grade"], "cell": _cell(all_ok), "settings": rows3,
        "sealed_primary_falsifier": settings[(192, 256)][
            "falsification_band"]["primary_falsifier"],
        "measured_scale_factor": measured["M-3"]["measured_scale_factor_ambient_edge"],
        "sealed_scale_factor": measured["M-3"]["bbp_scale_factor_(gamma2/gamma1)^0.25"],
        "oracleS_edge_invariance_claim": "the sealed formula asserts the oracle-S "
                                         "edge does NOT scale with (d,n)",
        "oracleS_edge_moved_by": (measured["M-3"]["(192,256)"]["oracleS_edge_lower"]
                                  - measured["M-3"]["(48,512)"]["oracleS_edge_lower"]),
    }
    card["s3_open_at_192"] = bool(measured["M-3"]["(192,256)"]["window_call"] == "OPEN")
    card["s3_empty_at_48"] = bool(measured["M-3"]["(48,512)"]["window_call"] == "EMPTY")

    # --- S-4 -----------------------------------------------------------------
    s4 = ents["S-4"]
    b4 = s4["falsification_band"]
    v4 = measured["M-4"]["measured_recovery_b_only"]["mean"]
    ok4 = inside(v4, b4["lo"], b4["hi"])
    card["entries"]["S-4"] = {
        "grade": s4["grade"], "cell": _cell(ok4),
        "sealed_predicted": s4["predicted_b_only_field_recovery"],
        "sealed_level_term": s4["predicted_level_term"],
        "sealed_band": [b4["lo"], b4["hi"]], "band_width": b4["band"],
        "measured": v4, "measured_ci": measured["M-4"]["measured_recovery_b_only"],
        "inside": ok4,
        "signed_distance_from_nearest_edge": (
            v4 - b4["hi"] if v4 > b4["hi"] else (v4 - b4["lo"] if v4 < b4["lo"] else 0.0)),
        "distance_in_band_widths": (
            (v4 - b4["hi"]) / b4["band"] if v4 > b4["hi"]
            else ((v4 - b4["lo"]) / b4["band"] if v4 < b4["lo"] else 0.0)),
        "sealed_inputs_vs_measured_inputs": {
            "r_sealed": s4["inputs"]["r_predicted_attenuation"],
            "r_measured": measured["M-4"]["law_inputs"]["r_card_b_pred_raw"],
            "V_person_sealed": s4["inputs"]["V_person_design_share"],
            "V_person_measured": measured["M-4"]["law_inputs"]["V_person_design"]},
        "sealed_constants": s4["constants"],
    }

    # --- S-5 -----------------------------------------------------------------
    s5 = ents["S-5"]
    b5 = s5["falsification_band"]
    v5 = measured["M-5"]["measured_eta_hat"]["mean"]
    ok5 = inside(v5, b5["lo"], b5["hi"])
    card["entries"]["S-5"] = {
        "grade": s5["grade"], "cell": _cell(ok5),
        "sealed_predicted": s5["predicted_eta_hat"],
        "sealed_band": [b5["lo"], b5["hi"]], "band_width": b5["band"],
        "measured": v5, "measured_ci": measured["M-5"]["measured_eta_hat"],
        "abs_error": abs(v5 - s5["predicted_eta_hat"]), "inside": ok5,
        "sealed_cell_energy": s5["cell_energy_sigma_b2"],
        "measured_cell_energy": measured["M-5"]["config"]["sigma_b2"],
        "pole_bias_note_carried": s5["falsification_band"]["pole_bias_note"]["statement"],
    }

    # --- rule 13: >=10xB stability on every interval this report quotes -------
    hi_ci = {}
    for tag, per_world in (
            ("S-1 eta0", prim["eta0"]["per_world_boundary_err_true_card"]),
            ("S-1 eta0.5", prim["eta0.5"]["per_world_boundary_err_true_card"]),
            ("S-1 eta1", prim["eta1"]["per_world_boundary_err_true_card"]),
            ("S-4", measured["M-4"]["per_world_recovery_b_only"]),
            ("S-5", measured["M-5"]["per_world_eta_hat_P"])):
        lo_b = boot_ci(np.asarray(per_world, float), B_BOOT)
        hi_b = boot_ci(np.asarray(per_world, float), B_BOOT_HIGH)
        hi_ci[tag] = {"B2000": [lo_b["lo"], lo_b["hi"]],
                      "B20000": [hi_b["lo"], hi_b["hi"]],
                      "max_endpoint_shift": max(abs(lo_b["lo"] - hi_b["lo"]),
                                                abs(lo_b["hi"] - hi_b["hi"]))}
    card["rule13_stability_10xB"] = hi_ci
    return card


def score(bundle: dict[str, Any], predictions: Any, permit: dict[str, Any],
          first_read: Any) -> None:
    """Scoring is mechanical: the Part-0 mapping table sends each sealed entry's
    own quantity to the measured field, and the entry's OWN band decides.
    NO re-fitting, NO band edits."""
    measured = read_json(MEASURED)
    card = score_entries(predictions, measured)
    cells = {e: card["entries"][e]["cell"] for e in ENTRIES}
    routing = {
        "reading_A_primary": route_reading_a(cells),
        "reading_B_second": route_reading_b(cells),
        "n_predicted_all5": sum(1 for e in ENTRIES if cells[e] == "PREDICTED"),
        "n_predicted_laws4": sum(1 for e in LAW_ENTRIES if cells[e] == "PREDICTED"),
        "s3_verdict": s3_verdict(cells["S-3"],
                                 card.get("s3_open_at_192"),
                                 card.get("s3_empty_at_48")),
    }
    out = {"utc": _utc(), "permit": permit, "first_bundle_read": first_read,
           "hash": {"committed": COMMITTED_HASH, "MATCH": True},
           "cells": cells, "routing": routing, "scorecard": card}
    write_json(OUT / "scorecard.json", out)
    print(json.dumps({"cells": cells, "routing": routing}, indent=1))
    _ = bundle


# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("part0")
    s1 = sub.add_parser("stage1")
    s1.add_argument("--task", required=True, choices=sorted(TASKS))
    sub.add_parser("seal")
    s2 = sub.add_parser("stage2")
    s2.add_argument("--dump-only", action="store_true")
    args = ap.parse_args()
    install_guard()
    log_event(args.cmd.upper(), "process_start", argv=sys.argv[1:])
    {"part0": run_part0, "stage1": run_stage1,
     "seal": run_seal, "stage2": run_stage2}[args.cmd](args)


if __name__ == "__main__":
    main()
