# V6 simulation-world specification

The executable matrix is `scripts/run_v6_simulation_matrix.py`; configurations are in
`configs/sim_v6/`. Full mode uses 500 Monte Carlo repetitions, 1,000 paths per repetition,
199 null permutations, and 999 nested variance bootstraps.

This specification records the final audit-frozen matrix. It was produced through
iterative development and must not be described as preregistered.

| World | Question | License / refusal gate |
|---|---|---|
| SIM-W0 | Are T1-prime/T2-prime identities algebraically correct? | error <= 1e-10 |
| SIM-W1 | Does the stationary mean formula recover iid/MA1/AR1/AR2 worlds? | bias <= max(.04,15%); nominal coverage |
| SIM-W2 | Can short-memory guards reject wrong worlds without fabricating serial signal under zero inflation? | FPR <= .10; power/guard >= .70/.80 |
| SIM-W3 | Is m=3 non-identifiability real and is lag-aware endpoint flow recoverable? | AUC within .05 of .5; bias and coverage gates |
| SIM-W4 | Can opportunity and response be separated? | observed-O recovery; hidden-O thinning AUC <= .55 |
| SIM-W5 | Can off-diagonal lag coupling be recovered? | calibrated null FPR and alternative power |
| SIM-W6 | What survives sampling? | above-Nyquist equivalence; below-Nyquist recovery |
| SIM-W7 | When is a response operator identifiable? | condition-number sweep and recovery error |
| SIM-W8 | When is conditional innovation rank decidable? | recover away from boundary; guard boundary band |

Completion means the estimator recovers truth in licensed worlds and refuses
observationally equivalent or ill-conditioned worlds. It does not mean every world is
identifiable, nor that the human data-generating process has been established.
