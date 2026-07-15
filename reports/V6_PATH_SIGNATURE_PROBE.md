# SUICA V6 Path-Signature Geometry Probe

## Mathematical object

For each complete same-condition run, let \(X=(x_0,\ldots,x_n)\) be the
time-augmented, within-run normalized residual path in \(\mathbb{R}^3\): time
plus two discovery-only residual PCA coordinates. Its degree-three signature is

\[
S_{\le3}(X)=\left(\int dX,\ \int_{t_1<t_2}dX_{t_1}\otimes dX_{t_2},
\int_{t_1<t_2<t_3}dX_{t_1}\otimes dX_{t_2}\otimes dX_{t_3}\right).
\]

Whole-run signatures are averaged within author-half. This is a geometric path
object, not a rotated factor catalog. Degree one is endpoint displacement only;
degree two adds ordered pair interactions (including signed area / cross-coordinate
coupling); degree three adds ordered triple interactions (turning and sequence
asymmetry). The endpoint-preserving shuffle is therefore expected to leave degree
one unchanged and can only be beaten by higher-order ordered geometry.

## Results

|   signature_depth |   signature_dimension | variant                | control             |   auc |   ci_lo |   ci_hi |
|------------------:|----------------------:|:-----------------------|:--------------------|------:|--------:|--------:|
|                 1 |                     3 | ordered_signature      | unmatched           | 0.503 |   0.488 |   0.515 |
|                 1 |                     3 | ordered_signature      | opportunity_matched | 0.499 |   0.485 |   0.513 |
|                 1 |                     3 | shuffled_order_null    | unmatched           | 0.503 |   0.488 |   0.515 |
|                 1 |                     3 | shuffled_order_null    | opportunity_matched | 0.499 |   0.485 |   0.513 |
|                 1 |                     3 | ordered_minus_shuffled | opportunity_matched | 0.000 |   0.000 |   0.000 |
|                 2 |                    12 | ordered_signature      | unmatched           | 0.509 |   0.495 |   0.518 |
|                 2 |                    12 | ordered_signature      | opportunity_matched | 0.502 |   0.490 |   0.514 |
|                 2 |                    12 | shuffled_order_null    | unmatched           | 0.503 |   0.490 |   0.514 |
|                 2 |                    12 | shuffled_order_null    | opportunity_matched | 0.495 |   0.483 |   0.507 |
|                 2 |                    12 | ordered_minus_shuffled | opportunity_matched | 0.007 |   0.001 |   0.013 |
|                 3 |                    39 | ordered_signature      | unmatched           | 0.511 |   0.497 |   0.520 |
|                 3 |                    39 | ordered_signature      | opportunity_matched | 0.503 |   0.491 |   0.515 |
|                 3 |                    39 | shuffled_order_null    | unmatched           | 0.506 |   0.493 |   0.516 |
|                 3 |                    39 | shuffled_order_null    | opportunity_matched | 0.495 |   0.485 |   0.506 |
|                 3 |                    39 | ordered_minus_shuffled | opportunity_matched | 0.007 |   0.000 |   0.014 |

## Boundary

The full time-augmented signature has strong path-uniqueness properties under
bounded variation; these finite truncations do not. No materiality threshold was
preregistered for this exploratory screen. A future confirmation should freeze one
degree and require a matched `ordered_minus_shuffled` lower confidence bound above
zero, a predeclared practical margin, leave-one-community-out survival, and formal
familywise control. The PANDORA epoch x technical-replica feasibility audit leaves
stable-author dynamics versus persistent state unidentifiable, so no personality or
author-parameter claim is made.
