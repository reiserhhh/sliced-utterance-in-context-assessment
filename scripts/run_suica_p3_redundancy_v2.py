#!/usr/bin/env python
"""P3: are the emerging SUICA v3 scores redundant with a generic lexicon space?

Predict each v3 component from the full Empath category space (194 categories,
user level, Tier U) with ridge + 5-fold CV R^2.
Pre-committed criterion (plan v2): CV R^2 <= 0.75 for the majority of
components -> non-redundant. Components tested:
  raw base (v1-style), FE base (rescued deviation channel), choice axes (E3).
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

from empath import Empath  # noqa: E402
from sklearn.linear_model import Ridge  # noqa: E402
from sklearn.model_selection import KFold  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

from scripts.suica_v2_lib import V2_CONSTRUCTS  # noqa: E402
from scripts.run_suica_e1_e2_centering_rescue_v2 import twoway_fe_condition_effects  # noqa: E402

TIER_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"
TAG = "s128"
CHAR_CAP = 24000
SEED = 42


def cv_r2(x: np.ndarray, y: np.ndarray, *, alpha: float = 10.0, folds: int = 5) -> float:
    kf = KFold(n_splits=folds, shuffle=True, random_state=SEED)
    ss_res, ss_tot = 0.0, 0.0
    for tr, te in kf.split(x):
        scaler = StandardScaler().fit(x[tr])
        model = Ridge(alpha=alpha).fit(scaler.transform(x[tr]), y[tr])
        pred = model.predict(scaler.transform(x[te]))
        ss_res += float(np.sum((y[te] - pred) ** 2))
        ss_tot += float(np.sum((y[te] - np.mean(y[tr])) ** 2))
    return 1.0 - ss_res / max(1e-12, ss_tot)


def main() -> None:
    lex = Empath()
    comments = pd.read_parquet(TIER_DIR / "tier_u_comments.parquet", columns=["author", "body"])
    comments["author"] = comments["author"].astype(str)
    joined_text = comments.groupby("author")["body"].apply(lambda s: "\n".join(s.astype(str))[:CHAR_CAP])
    print(f"users with text: {len(joined_text)}")
    empath_rows = {u: lex.analyze(t, normalize=True) or {} for u, t in joined_text.items()}
    empath_frame = pd.DataFrame(empath_rows).T.fillna(0.0)
    empath_frame.index.name = "user_id"
    print(f"empath matrix: {empath_frame.shape}")

    passb = pd.read_parquet(TIER_DIR / f"phase2_passB_scored_{TAG}.parquet")
    users_per_cond = passb.groupby("condition")["user_id"].nunique()
    passb = passb.loc[passb["condition"].map(users_per_cond).ge(3)]
    targets: dict[str, pd.Series] = {}
    for construct in V2_CONSTRUCTS:
        cell = passb.groupby(["user_id", "condition"], as_index=False)[construct].mean()
        targets[f"raw_base::{construct}"] = cell.groupby("user_id")[construct].mean()
        w = passb[["user_id", "condition", construct]].copy()
        c_fe = twoway_fe_condition_effects(w, construct)
        w["_fe"] = w[construct] - c_fe.reindex(w["condition"]).to_numpy()
        cell_fe = w.groupby(["user_id", "condition"], as_index=False)["_fe"].mean()
        targets[f"fe_base::{construct}"] = cell_fe.groupby("user_id")["_fe"].mean()

    choice_path = ROOT / "results" / f"suica_e3_e4_choice_class_v2_{TAG}" / "choice_axis_scores.csv"
    if choice_path.exists():
        choice = pd.read_csv(choice_path, dtype={"user_id": str}).set_index("user_id")
        keep = [c for c in choice.columns if c.startswith("choice_ax_")]
        var_ok = choice[keep].std() > 1e-8
        for col in np.array(keep)[var_ok.to_numpy()]:
            targets[f"choice::{col}"] = choice[col]

    rows = []
    for name, series in targets.items():
        joined = empath_frame.join(series.rename("y"), how="inner").dropna(subset=["y"])
        if len(joined) < 300 or joined["y"].std() < 1e-10:
            continue
        r2 = cv_r2(joined.drop(columns=["y"]).to_numpy(float), joined["y"].to_numpy(float))
        rows.append({"target": name, "n_users": int(len(joined)), "empath_cv_r2": r2})
    result = pd.DataFrame(rows).sort_values("empath_cv_r2", ascending=False)
    out_dir = ROOT / "results" / f"suica_p3_redundancy_v2_{TAG}"
    out_dir.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_dir / "p3_redundancy.csv", index=False)
    frac_below = float((result["empath_cv_r2"] <= 0.75).mean())
    criteria = {
        "n_targets": int(len(result)),
        "fraction_r2_le_075": frac_below,
        "max_r2": float(result["empath_cv_r2"].max()),
        "P3_verdict": "pass" if frac_below > 0.5 else "fail",
    }
    (out_dir / "p3_results.json").write_text(json.dumps(criteria, indent=2) + "\n")
    (ROOT / "reports" / f"suica_p3_redundancy_v2_{TAG}.md").write_text(
        "# SUICA P3 Redundancy vs Empath (v2)\n\n" + result.round(4).to_markdown(index=False)
        + "\n\n```json\n" + json.dumps(criteria, indent=2) + "\n```\n"
    )
    print(result.round(3).to_string(index=False))
    print(json.dumps(criteria, indent=2))


if __name__ == "__main__":
    main()
