# V8 Spacetime Junction-Flow V3.6 Prospective Seal

Created after targeted tests and smoke, before full confirmation on
2026-07-26. This is an internal content-hash seal, not an immutable external
preregistration.

| Path | SHA-256 |
| --- | --- |
| `configs/v8_spacetime_junction_flow_v36.json` | `4618032d58a127a5c89b6dcf0075c8ce418bb888fea1806d6c9ac9456d9ccfe7` |
| `docs/V8_SPACETIME_JUNCTION_FLOW_V36_PLAN.md` | `47071846599ab3fbfb2ac8a6ee4321cdf1aef9427b81cd23dfa8195af74c5f81` |
| `suica_core/v7_governance.py` | `4bd06eba25abde2703d187b3c7ed89adefc481f484ba6ea780a0547ba3c21871` |
| `suica_core/v8_incidence_multiplicity.py` | `8450258e0572453d53238cb57e975e1ab90994627c9cb225e06525df451e24a5` |
| `suica_core/v8_incidence_incremental.py` | `5b1657239603e18f79c8e126874d40c15d4b86da045b6ed2e955fe55e056df7b` |
| `suica_core/v8_spacetime_junction_flow.py` | `39e24d0e6960bea05f3b72add7078a41ffbb07c74aafa5c6511f25376103e588` |
| `scripts/run_suica_v8_incidence_incremental.py` | `7d38c5566b38bc2ef16336cec7d8caa199e76fe9e2a35cac10fb149c123829c4` |
| `scripts/run_suica_v8_spacetime_junction_flow_v36.py` | `e017340ae8307c7f7ba7765c9ac844f6906ca48f1b22d6e966d053df8230bd3b` |
| `tests/test_v8_spacetime_junction_flow_v36.py` | `18eb94d03e3857d2932463f95fdfe4ca4be6cc2da98a237ae2b0f5f230641982` |

Frozen settings:

- discovery repetitions: 80 per primary world;
- confirmation repetitions: 500 per primary world;
- control repetitions: 200 per attack;
- branches: 3; depth: 3; authors: 24; episodes: 27; views: 4;
- primary policies: pass-through, random-branch, and cue-guided;
- attacks: cue shuffle, pass-through cue shuffle, time shuffle, tangent-view
  shuffle, and guided near miss;
- no confirmation-driven threshold changes.
