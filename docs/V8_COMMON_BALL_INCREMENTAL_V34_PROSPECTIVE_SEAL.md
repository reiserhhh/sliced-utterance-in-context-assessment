# V8 Common-Ball Incremental V3.4 Prospective Seal

Created after the V3.4 smoke test and before the full confirmation run on
2026-07-26.

This is an internal content-hash seal. The repository worktree is dirty and
the files are untracked, so it is not an immutable Git preregistration.

| Path | SHA-256 |
| --- | --- |
| `configs/v8_common_ball_incremental_v34.json` | `fd28ac961a922939b8e9cf04480dd7bd33c0027fcc34adfb50c9997a5b2239e4` |
| `docs/V8_COMMON_BALL_INCREMENTAL_V34_PLAN.md` | `1f57da4734d6407f9ef7f016d64665537936e040b7d903600612eac6af642b2f` |
| `suica_core/v7_governance.py` | `4bd06eba25abde2703d187b3c7ed89adefc481f484ba6ea780a0547ba3c21871` |
| `suica_core/v8_incidence_multiplicity.py` | `8450258e0572453d53238cb57e975e1ab90994627c9cb225e06525df451e24a5` |
| `suica_core/v8_incidence_incremental.py` | `5b1657239603e18f79c8e126874d40c15d4b86da045b6ed2e955fe55e056df7b` |
| `suica_core/v8_incidence_incremental_v31.py` | `fe4697ded63f15e0c02f1f9d8abf7f356244d3b2f573a0bbe841f9a62b4cab65` |
| `suica_core/v8_incidence_graph_fairness.py` | `5ba8e5b9a141d97bf568d5a923c483373a1225dbb31d69839f67419ca6863150` |
| `suica_core/v8_common_ball_incremental.py` | `ba35f22f48090d6e5f133e3f06e8a1bdc717db51b7ce637cf9a161efd3058130` |
| `scripts/run_suica_v8_incidence_incremental.py` | `7d38c5566b38bc2ef16336cec7d8caa199e76fe9e2a35cac10fb149c123829c4` |
| `scripts/run_suica_v8_common_ball_incremental_v34.py` | `6e2d42b75912cf783bd9e3a724ea290a8c6a8942988a733cd1d740020e095397` |
| `tests/test_v8_common_ball_incremental_v34.py` | `fecc352a5fd0737a226e047691afe7836b9e279e546f6de2cd91e5bdd1a148e8` |

Frozen confirmation settings:

- main paired populations: 500;
- each control: 200;
- fixed uncertainty radius: 1.0;
- epsilon grid: 1.00, 1.03, 1.06;
- positive regular-hexagon circumradius: 0.90;
- negative duplicated-triangle circumradius: 1.10;
- active conditions: 4 of 65;
- persistence threshold: 0.04;
- exact per-view adjacency matching is mandatory;
- no confirmation-driven parameter changes.
