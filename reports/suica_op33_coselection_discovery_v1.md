# OP-33 co-selection (char n-gram) construct discovery

| axis   |   r_A |   residual_retest_A |   r_B | confirmed   |
|:-------|------:|--------------------:|------:|:------------|
| cos_14 | 0.634 |               0.259 | 0.595 | True        |
| cos_08 | 0.512 |               0.194 | 0.553 | False       |
| cos_15 | 0.57  |               0.223 | 0.548 | True        |
| cos_42 | 0.49  |               0.33  | 0.522 | True        |
| cos_03 | 0.495 |               0.273 | 0.516 | True        |
| cos_06 | 0.56  |               0.337 | 0.51  | True        |
| cos_45 | 0.553 |               0.199 | 0.505 | False       |
| cos_01 | 0.544 |               0.2   | 0.502 | False       |
| cos_31 | 0.457 |               0.312 | 0.496 | True        |
| cos_29 | 0.558 |               0.297 | 0.482 | True        |
| cos_11 | 0.41  |               0.231 | 0.457 | True        |
| cos_41 | 0.483 |               0.203 | 0.442 | True        |
| cos_24 | 0.432 |               0.186 | 0.425 | False       |
| cos_09 | 0.394 |               0.222 | 0.424 | True        |
| cos_07 | 0.413 |               0.279 | 0.422 | True        |
| cos_18 | 0.432 |               0.335 | 0.4   | True        |
| cos_23 | 0.407 |               0.25  | 0.387 | True        |
| cos_00 | 0.352 |               0.272 | 0.384 | True        |
| cos_43 | 0.384 |               0.22  | 0.38  | True        |
| cos_19 | 0.437 |               0.345 | 0.378 | True        |
| cos_16 | 0.346 |               0.183 | 0.376 | False       |
| cos_12 | 0.382 |               0.247 | 0.372 | True        |
| cos_47 | 0.41  |               0.27  | 0.371 | True        |
| cos_32 | 0.319 |               0.306 | 0.371 | True        |
| cos_05 | 0.378 |               0.281 | 0.37  | True        |
| cos_22 | 0.31  |               0.222 | 0.294 | True        |
| cos_40 | 0.333 |               0.155 | 0.281 | False       |
| cos_21 | 0.306 |               0.151 | 0.266 | False       |
| cos_17 | 0.311 |               0.22  | 0.246 | False       |

## Confirmed axis top n-grams

- **cos_14**: _i_, his, his_, _lo, this, _ho, _so_, ove, ome_, _!_, ks_, than
- **cos_15**: ate, cou, ate_, unt, ans, tat, ric, ern, mer, ount, lic, ans_
- **cos_42**: _the, he_, _an, nd_, and, and_, _and, ed_, _my, was, ad_, _was
- **cos_03**: _th, at_, is_, hat, _it, tha, _tha, hat_, _wh, that, _is, _no
- **cos_06**: _,_, re_, ly_, _be, ut_, thi, st_, _so, _re, me_, all, ll_
- **cos_31**: ist, ali, eli, ari, lis, tru, _na, lie, ani, ris, ist_, ize
- **cos_29**: _in_, an_, _le, ame, _pl, pla, _te, _la, lea, _pla, _ra, _ga
- **cos_11**: or_, for, _fo, _on, _for, for_, _go, _we, ay_, rs_, ear, ter_
- **cos_41**: _to, to_, _to_, _yo, you, _you, _wa, ou_, you_, _ca, ce_, can
- **cos_09**: on_, ion, tio, tion, ion_, ati, ns_, ons, atio, ons_, ions, rat
- **cos_07**: _a_, _bo, ook, rin, loo, _br, _bi, che, _loo, look, _dr, ok_
- **cos_18**: ey_, wor, _wor, ork, work, mon, car, rk_, _car, ork_, pri, _jo
- **cos_23**: so_, ur_, our_, eal, your, tra, als, str, hea, lso, also, lso_
- **cos_00**: ps_, tch, eme, _vi, ber, rem, atc, atch, wat, tch_, _wat, tps
- **cos_43**: _it_, _do, 't_, n't, n't_, any, _any, oes, sn', sn't, doe, _doe
- **cos_19**: _._, _)_, _(_, _:_, _/_, _am, _-_, htt, ttp, http, _ht, _htt
- **cos_12**: al_, cal, ica, tic, ic_, ical, call, led, nic, asi, led_, sic
- **cos_47**: ds_, end, rie, ien, nds, end_, nds_, _gi, rien, fri, frie, iend
- **cos_32**: _cl, ass, _sc, ol_, lle, stu, gra, _stu, cho, oll, ool, hoo
- **cos_05**: ing, ng_, the_, ing_, _wi, th_, ith, wit, _wit, with, ith_, et_
- **cos_22**: ve_, ave, hav, _hav, ave_, have, our, _ne, ver_, ind, _all, em_

```json
{
  "n_confirmed": 21,
  "SUCCESS": true
}
```
