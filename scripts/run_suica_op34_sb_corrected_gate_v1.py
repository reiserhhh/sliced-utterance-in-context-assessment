#!/usr/bin/env python
"""OP-34: SB-corrected (attenuation-corrected) flesh-purity gate sensitivity.

The v4 gate uses RAW class-disjoint retest, which is attenuation-limited by
the within-arm noise -> it UNDERCOUNTS F-family (round-10 note). This
sensitivity analysis disattenuates the class-disjoint coefficient using
each arm's internal split-half reliability, and re-runs the F/C/composite
gate. Constructs whose family CHANGES are FLAGGED as candidates; no registry
relabel here (relabels wait for the round-11 audit).

Disattenuation: r_true = r_obs / sqrt(rel_early * rel_late), where rel_h is
the within-arm even/odd split-half of the class-disjoint arm h, SB-lifted.
Clamp r_true to [-1, 1]. Gate re-applied with the SAME thresholds
(class-disjoint >= 0.15, share < 0.30) on the disattenuated class-disjoint.

Reads results/suica_c2_purity_all19_v1/all19_purity.csv (the corrected,
transported run) for baseline; recomputes per-arm reliabilities from the
frozen pass-A rebuild + transported wcl. Tier-U, label-free.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_suica_c2_purity_all19_v1 import rebuild_passA_with_text  # noqa: E402
from scripts.run_suica_op9_embedding_baseline_v3 import V3_BATTERY, OP5_KEPT  # noqa: E402
from scripts.suica_v2_lib import score_slices_v2  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
CLASS_MAP = ROOT / "results" / "suica_e3_e4_choice_class_v2_s128" / "condition_class_map.csv"
BASE = ROOT / "results" / "suica_c2_purity_all19_v1" / "all19_purity.csv"
OUT_DIR = ROOT / "results" / "suica_op34_sb_corrected_gate_v1"
REPORT = ROOT / "reports" / "suica_op34_sb_corrected_gate_v1.md"


def sb(r: float) -> float:
    return 2 * r / (1 + r) if np.isfinite(r) and r > -1 else np.nan


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame = rebuild_passA_with_text()
    scored = score_slices_v2(frame[["user_id", "condition", "half", "slice_text"]])
    import scripts.run_suica_dev_anchor_performance_v1 as dav
    _, wcl_transform = dav.pandora_style_fit_and_battery()
    wcl = pd.concat([frame[["user_id", "condition", "half"]].reset_index(drop=True),
                     wcl_transform(frame["slice_text"]).reset_index(drop=True)], axis=1)
    class_of = dict(zip(*[pd.read_csv(CLASS_MAP)[c] for c in ("condition", "class_id")]))
    base = pd.read_csv(BASE).set_index("construct")

    def arm_reliability(src, col):
        """even/odd split-half of the class-disjoint arm, per half, SB-lifted.
        Approximates each arm's internal reliability at the user level."""
        cell = (src.groupby(["user_id", "condition", "half"])[col].mean().unstack("half").dropna())
        cell.index.names = ["user", "condition"]
        rels = {}
        for h in ("early", "late"):
            eo = {}
            for u, g0 in cell.groupby(level="user"):
                g = g0.xs(u, level="user")
                conds = sorted(g.index)
                classes = sorted({class_of.get(c, -1) for c in conds})
                if len(classes) < 2:
                    continue
                inA = set(classes[0::2])
                A = [c for c in conds if class_of.get(c, -1) in inA]
                B = [c for c in conds if class_of.get(c, -1) not in inA]
                if A and B:
                    eo[u] = (g.loc[A, h].mean(), g.loc[B, h].mean())
            if len(eo) >= 30:
                d = pd.DataFrame(eo, index=["a", "b"]).T.dropna()
                r = float(d["a"].corr(d["b"]))
                rels[h] = sb(r)
        return rels

    rows = []
    for col in V3_BATTERY + OP5_KEPT:
        src = scored if col in V3_BATTERY else wcl
        obs = float(base.loc[col, "rho_class_disjoint"])
        share = base.loc[col, "c1_share"]
        rels = arm_reliability(src, col)
        rel_e, rel_l = rels.get("early", np.nan), rels.get("late", np.nan)
        denom = np.sqrt(max(1e-6, rel_e) * max(1e-6, rel_l)) if np.isfinite(rel_e) and np.isfinite(rel_l) else np.nan
        corrected = float(np.clip(obs / denom, -1, 1)) if np.isfinite(denom) and denom > 0 else np.nan
        base_fam = base.loc[col, "v4_family"]
        if pd.isna(share):
            new_fam = "undetermined"
        elif np.isfinite(corrected) and corrected >= 0.15 and share < 0.30:
            new_fam = "F-family (flesh trait)"
        elif share > 0.30 and (not np.isfinite(corrected) or corrected < 0.10):
            new_fam = "C-family (venue signature)"
        else:
            new_fam = "composite"
        rows.append({"construct": col, "class_disj_raw": round(obs, 4),
                     "rel_early": round(rel_e, 3) if np.isfinite(rel_e) else None,
                     "rel_late": round(rel_l, 3) if np.isfinite(rel_l) else None,
                     "class_disj_SBcorrected": round(corrected, 4) if np.isfinite(corrected) else None,
                     "share": None if pd.isna(share) else round(float(share), 3),
                     "family_raw": base_fam, "family_SBcorrected": new_fam,
                     "CHANGED": bool(base_fam != new_fam)})
    df = pd.DataFrame(rows)
    changed = df.loc[df["CHANGED"], ["construct", "family_raw", "family_SBcorrected"]]
    res = {"n_changed": int(df["CHANGED"].sum()),
           "changed": changed.to_dict(orient="records"),
           "note": "SENSITIVITY ONLY — no registry relabel; candidates for round-11 audit"}
    df.round(4).to_csv(OUT_DIR / "op34_gate.csv", index=False)
    (OUT_DIR / "op34_results.json").write_text(json.dumps(res, indent=2, default=float) + "\n")
    REPORT.write_text("# OP-34 SB-corrected gate sensitivity (no relabel)\n\n"
                      + df.to_markdown(index=False)
                      + f"\n\n{json.dumps(res, indent=2)}\n")
    print(df.to_string(index=False))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
