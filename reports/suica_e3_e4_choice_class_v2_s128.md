# SUICA E3/E4 Choice Scale + Class React (exploration)

> **AUDIT NOTICE (2026-07-05, rounds 3+5).** The E3 choice-axis results below are UPHELD
> (independently recomputed; see also OP-6a held-out confirmation). The E4 class-react
> results below are OVERTURNED as individual-signature evidence: the within-user
> permutation null is the wrong null (with ~4 shared classes its expectation is -1/(m-1),
> and the earlier "nulls ~0" note was false); against the correct STRANGER null the
> normative baseline is 0.25-0.31. The corrected signature evidence lives in E6
> (matched-estimator stranger null). Authoritative record: docs/SUICA_CLAIMS_LEDGER.md.


## Condition classes

|   class_id |   n_slices |   n_conditions | top_terms                                                                                                                                                        | top_subreddits                                                                                 |
|-----------:|-----------:|---------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|
|          0 |      10142 |            322 | weight, my, day, eat, calories, week, eating, your, body, days, fat, diet                                                                                        | ADHD, loseit, Fitness, trees, Drugs, xxfitness                                                 |
|          1 |      10434 |            441 | he, his, him, was, episode, show, she, season, her, character, the show, the                                                                                     | movies, WritingPrompts, asoiaf, gameofthrones, gifs, harrypotter                               |
|          2 |      16914 |            806 | use, using, thanks, skin, looks, for, on, windows, it, phone, used, price                                                                                        | pcmasterrace, MakeupAddiction, SkincareAddiction, Android, AsianBeauty, buildapc               |
|          3 |      14524 |            678 | if you, you, car, your, year, job, school, work, for, there, if, in                                                                                              | personalfinance, singapore, weddingplanning, Philippines, cars, financialindependence          |
|          4 |      10185 |            586 | album, song, love, music, songs, anime, favorite, book, like, great, albums, my favorite                                                                         | anime, books, femalefashionadvice, kpop, aww, Fantasy                                          |
|          5 |      24437 |            669 | game, play, the game, games, playing, players, damage, team, to play, played, player, level                                                                      | leagueoflegends, Overwatch, wow, gaming, DotA2, DnD                                            |
|          6 |      34444 |            692 | trump, people, they, their, are, we, is, government, of, not, the, by                                                                                            | politics, worldnews, news, todayilearned, funny, The_Donald                                    |
|          7 |       1445 |            272 | goodbye, pixiv, member_illust, php mode, illust_id, goodbye goodbye, member_illust php, pixiv member_illust, medium illust_id, mode medium, user_simulator, join | dankmemes, Fireteams, buildapcforme, CircleofTrust, AskOuija, androidcirclejerk                |
|          8 |       5394 |            229 | he, team, we, game, season, him, his, players, year, teams, league, play                                                                                         | nfl, nba, soccer, CFB, hockey, fantasyfootball                                                 |
|          9 |       1005 |            180 | thank, thank you, thanks, you, ll, trade, you so, thanks for, so much, you for, love, for                                                                        | pokemontrades, progresspics, redditgetsdrawn, ACTrade, RandomActsOfGaming, CasualPokemonTrades |
|         10 |       2506 |            196 | she, her, she was, was, he, season, love, that she, show, she is, of her, cat                                                                                    | rupaulsdragrace, JUSTNOMIL, TaylorSwift, thebachelor, BigBrother, cats                         |
|         11 |      73795 |            364 | type_mention, me, my, cogfunc_mention, feel, life, friends, she, an type_mention, people, things, myself                                                         | AskReddit, INTP, intj, infp, infj, mbti                                                        |

## Choice axis stability (early vs late)

|   class_id |   axis_retest_r | top_terms                                                                                                                                                        | top_subreddits                                                                                 |
|-----------:|----------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------|
|          0 |           0.495 | weight, my, day, eat, calories, week, eating, your, body, days, fat, diet                                                                                        | ADHD, loseit, Fitness, trees, Drugs, xxfitness                                                 |
|          1 |           0.508 | he, his, him, was, episode, show, she, season, her, character, the show, the                                                                                     | movies, WritingPrompts, asoiaf, gameofthrones, gifs, harrypotter                               |
|          2 |           0.532 | use, using, thanks, skin, looks, for, on, windows, it, phone, used, price                                                                                        | pcmasterrace, MakeupAddiction, SkincareAddiction, Android, AsianBeauty, buildapc               |
|          3 |           0.533 | if you, you, car, your, year, job, school, work, for, there, if, in                                                                                              | personalfinance, singapore, weddingplanning, Philippines, cars, financialindependence          |
|          4 |           0.484 | album, song, love, music, songs, anime, favorite, book, like, great, albums, my favorite                                                                         | anime, books, femalefashionadvice, kpop, aww, Fantasy                                          |
|          5 |           0.703 | game, play, the game, games, playing, players, damage, team, to play, played, player, level                                                                      | leagueoflegends, Overwatch, wow, gaming, DotA2, DnD                                            |
|          6 |           0.571 | trump, people, they, their, are, we, is, government, of, not, the, by                                                                                            | politics, worldnews, news, todayilearned, funny, The_Donald                                    |
|          7 |           0.357 | goodbye, pixiv, member_illust, php mode, illust_id, goodbye goodbye, member_illust php, pixiv member_illust, medium illust_id, mode medium, user_simulator, join | dankmemes, Fireteams, buildapcforme, CircleofTrust, AskOuija, androidcirclejerk                |
|          8 |           0.679 | he, team, we, game, season, him, his, players, year, teams, league, play                                                                                         | nfl, nba, soccer, CFB, hockey, fantasyfootball                                                 |
|          9 |           0.278 | thank, thank you, thanks, you, ll, trade, you so, thanks for, so much, you for, love, for                                                                        | pokemontrades, progresspics, redditgetsdrawn, ACTrade, RandomActsOfGaming, CasualPokemonTrades |
|         10 |           0.367 | she, her, she was, was, he, season, love, that she, show, she is, of her, cat                                                                                    | rupaulsdragrace, JUSTNOMIL, TaylorSwift, thebachelor, BigBrother, cats                         |
|         11 |           0.33  | type_mention, me, my, cogfunc_mention, feel, life, friends, she, an type_mention, people, things, myself                                                         | AskReddit, INTP, intj, infp, infj, mbti                                                        |
|         12 |           0.373 | nan                                                                                                                                                              | nan                                                                                            |

## Class-level react signatures

| construct             |   n_users |   median_signature_r |   null_median |   n_disattenuable |   median_disattenuated |
|:----------------------|----------:|---------------------:|--------------:|------------------:|-----------------------:|
| novelty_play_v2       |        62 |                0.308 |         0.013 |                20 |                  1     |
| directive_action_v2   |        62 |                0.395 |        -0.23  |                23 |                  0.923 |
| adversity_recovery_v2 |        59 |                0.053 |        -0.057 |                19 |                 -0.045 |
| first_person_usage_v2 |        62 |                0.502 |        -0.147 |                43 |                  0.818 |
| tension_core_v2       |        62 |               -0.03  |        -0.017 |                18 |                  0.413 |

```json
{
  "choice_axes_adopted_r_ge_050": [
    1,
    2,
    3,
    5,
    6,
    8
  ],
  "n_axes_adopted": 6,
  "profile_auc": 0.8386139711440599,
  "react_observed_ge_030_count": 3,
  "react_disattenuated_ge_030_count": 4,
  "n_users": 3204,
  "profile_auc_logratio": 0.8386139711440599,
  "mean_abs_interaxis_r": 0.1313294857306743,
  "max_abs_interaxis_r": 0.35190400469901567
}
```
