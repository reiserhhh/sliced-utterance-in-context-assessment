# T-GEO-P6 — personal axes (F10.3, label-free)

Leading eigenvector of within-person slice correlation, per user per half.
Self = |cos(u_early, u_late)|; stranger = cyclic-shift derangement pairing;
ceiling = within-half odd/even split; residualized = population top-4 slice-
level frame projected out first (the sharp F10.3 test).

| arm | variant | n | self | stranger | p(self>stranger) | ceil early | ceil late |
|---|---|---|---|---|---|---|---|
| pooled | raw | 2430 | 0.2567 | 0.2237 | 0.0 | 0.2554 | 0.2508 |
| pooled | residualized | 2430 | 0.2769 | 0.2155 | 0.0 | 0.2805 | 0.2917 |
| top1 | raw | 938 | 0.204 | 0.199 | 0.1733 | 0.2071 | 0.217 |
| top1 | residualized | 938 | 0.2435 | 0.2078 | 0.0 | 0.2408 | 0.2417 |

Alignment dispersion (pooled raw): median best |cos| vs population PC1-4 = 0.4929 (IQR 0.3944-0.5982); random-direction baseline median 0.3332 (p95 0.5475); best-match shares PC1..4 = [0.424, 0.273, 0.166, 0.136].
