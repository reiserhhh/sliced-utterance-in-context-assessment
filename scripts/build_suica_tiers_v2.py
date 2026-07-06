#!/usr/bin/env python
"""Freeze SUICA v2 data tiers (SUICA_METHOD_VALIDATION_PLAN_V2 section 2).

Tier U (development): MBTI-axis users minus bridge minus Big5. Label VALUES are
never loaded here — only user membership. Tier L (lockbox): Big5 + bridge
users; their text and labels are excluded from all v2 development work.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data_sets" / "prepared" / "suica_tiers_v2"


def user_set(path: Path) -> set[str]:
    return set(pd.read_csv(path, usecols=["user_id"])["user_id"].astype(str))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mbti = user_set(ROOT / "data_sets/prepared/pandora_official/mbti_axes/pandora_official_EI_cont_prepared.csv")
    big5 = user_set(ROOT / "data_sets/prepared/pandora_official/pandora_official_big5_prepared.csv")
    bridge_strict = user_set(ROOT / "data_sets/prepared/pandora_official/bridge/pandora_official_bridge_strict377.csv")
    bridge_supp = user_set(ROOT / "data_sets/prepared/pandora_official/bridge/pandora_official_bridge_supplementary393.csv")
    lockbox = big5 | bridge_strict | bridge_supp
    tier_u = sorted(mbti - lockbox)
    tier_l = sorted(lockbox)
    pd.DataFrame({"user_id": tier_u}).to_csv(OUT_DIR / "tier_u_users.csv", index=False)
    pd.DataFrame({"user_id": tier_l}).to_csv(OUT_DIR / "tier_l_users.csv", index=False)
    manifest = {
        "created": "2026-07-04",
        "plan": "docs/SUICA_METHOD_VALIDATION_PLAN_V2.md",
        "mbti_axis_users": len(mbti),
        "big5_users": len(big5),
        "bridge_strict_users": len(bridge_strict),
        "bridge_supplementary_users": len(bridge_supp),
        "tier_u_users": len(tier_u),
        "tier_l_users": len(tier_l),
        "rule": "tier_u = mbti_axis - (big5 | bridge_strict | bridge_supp); label values not read",
        "lockbox_opening_budget_remaining": 2,
    }
    (OUT_DIR / "tier_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
