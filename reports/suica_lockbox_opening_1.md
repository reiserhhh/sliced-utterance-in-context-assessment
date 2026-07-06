# SUICA Lockbox Opening #1 — Preregistered Confirmatory Report

Opened: 2026-07-06T18:52:22.966004+00:00  |  git: `cd63d137128e86d0aa9a1bfda7e4f04f8de4fcad`  |  prereg seal: `dd5c7805689acd6d5351f7a22864b3ff45eb1d7d`

Eligible: Big5 1058 (est. 1,108), bridge 303 (est. 326)

| id | predictor | target | n | r | 95% CI | p | q(BH) | pred. sign | verdict |
|---|---|---|---|---|---|---|---|---|---|
| H1 | tension_core_v2 | Neuroticism | 1058 | +0.0516 | [-0.009,+0.112] | 0.0934 | 0.2178 | + | ns |
| H2 | first_person_usage_v2 | Neuroticism | 1058 | +0.1114 | [+0.051,+0.170] | 0.0003 | 0.0020 | + | PASS |
| H3 | novelty_play_v2 | Openness | 1058 | -0.0464 | [-0.106,+0.014] | 0.1317 | 0.2305 | + | ns |
| H4 | directive_action_v2 | Agreeableness | 1058 | +0.0294 | [-0.031,+0.089] | 0.3402 | 0.3969 | - | ns |
| H5 | directive_action_v2 | is_T | 303 | +0.0625 | [-0.051,+0.174] | 0.2782 | secondary | + | reported |
| H6 | choice_ax_06 | Openness | 1058 | +0.0959 | [+0.036,+0.155] | 0.0018 | 0.0063 | + | PASS |
| H7 | choice_entropy | Openness | 1058 | -0.0088 | [-0.069,+0.052] | 0.7760 | 0.7760 | + | ns |
| H8 | choice_ax_05 | Extraversion | 1058 | -0.0407 | [-0.101,+0.020] | 0.1856 | 0.2598 | - | ns |

**Confirmatory passes: 2/7 (rule: >=4 and no significant wrong-direction)**
**SUCCESS RULE MET: False**

## Non-confirmatory add-ons

```json
{
  "delta_r2": {
    "Neuroticism": {
      "n": 1058,
      "empath_r2": -0.15322986045761033,
      "empath_plus_battery_r2": -0.15815670862083753,
      "delta_r2": -0.004926848163227193
    },
    "Openness": {
      "n": 1058,
      "empath_r2": -0.24792992988526752,
      "empath_plus_battery_r2": -0.2815867972349386,
      "delta_r2": -0.033656867349671105
    }
  },
  "H7_robustness": {
    "H7_variant_choice_entropy_norm_v1": {
      "n": 1058,
      "r": -0.010908910605624152,
      "p": 0.7230209517714287,
      "ci_lo": -0.07113131123709664,
      "ci_hi": 0.04939273108359259
    },
    "H7_variant_choice_entropy_class": {
      "n": 1058,
      "r": -0.014940518589810851,
      "p": 0.6273773468099298,
      "ci_lo": -0.07514202416050599,
      "ci_hi": 0.0453695018997805
    }
  },
  "tf_flip_applied": true
}
```

