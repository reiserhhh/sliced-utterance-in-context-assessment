# V8 V3.7H.2 Independent Mathematical Audit

Date: 2026-07-26

Ruling:
`D2_PASS_CONFIRMATION_PROTOCOL_ELIGIBLE_NOT_SEALED`

## Core ruling

D2 is a valid prospective focused-tail audit. It used fresh seeds, did not
pool D1 results, retained \(Q=.01\), and tightened rather than relaxed the
false-refusal and material-power gates.

The repeated-opportunity estimator is approximately unbiased in the
registered high-correlation, strong-common-shock Gaussian and heteroskedastic
\(t_5\) worlds when \(K\ge2\):

\[
Q_K^{rep}
=
\frac{
\text{schedule-difference energy}
-\text{occasion-variance correction}
}{S_{\mathrm{score}}}.
\]

Evidence:

- \(K=2\) heavy-tail null: 11/1000, familywise upper .02224;
- every \(\eta=.10\) cell: 1000/1000, familywise lower .99494;
- \(K=2,\eta=.02\): 998/1000 Gaussian and 986/1000 heavy-tail;
- maximum simultaneous bias bounds: .000633 and .000584;
- legacy contaminated-null refusal: 100%;
- global shift separated into total, not author-relative, response;
- persistent response and persistent confound remained exactly
  observationally identical.

## Replication boundary

- \(K=1\): unidentifiable;
- \(K=2\): validated minimum identifiable configuration;
- \(K=3\): validated minimum robust configuration;
- \(K=4\): recommended confirmation default;
- \(K=8\): optional high-precision configuration.

\(K=4\) adds no new identification theorem over \(K=3\), but supplies lower
variance, symmetric replication, and more tolerance to departures from the
registered world.

## Seal ruling

The protocol is eligible for a bounded synthetic confirmation, not already
confirmed. Before opening a confirmation seed:

1. freeze the estimator, \(Q=.01\), score-space normalization, and D2 gates;
2. commit all relevant code and config;
3. record SHA-256 and an external timestamp;
4. generate a fresh unseen seed;
5. prohibit any later change to \(K\), thresholds, or noise cells.

The only confirmable statement is schedule-sensitivity identification in the
registered repeated-opportunity synthetic world. It is not a theorem that all
condition changes are detectable.

## Next priority

The next discovery target is minority-by-near-kernel response:

\[
g_u
=
I_u\left[
\sqrt{\alpha}\,g_{\operatorname{range}(W)}
+\sqrt{1-\alpha}\,g_{\ker(W)}
\right],
\]

where \(p=P(I_u=1)\) and \(\alpha\) is the scorer-observable fraction.
Population mean signal is approximately:

\[
\eta_{\mathrm{observable}}
\approx p\alpha\eta_{\mathrm{individual}}.
\]

A small \(p\alpha\) can create a dangerous false non-refusal even when
affected authors change strongly. Pairing integrity should be enforced as a
hard data contract; transient/reversal response follows after the minority
and near-kernel frontier.
