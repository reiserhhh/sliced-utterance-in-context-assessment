# SUICA V7 MEPS Fixed/Free Preflight

## Decision

`REFUSE_Q_OPPORTUNITY_UNOBSERVED` and
`REFUSE_B_INSUFFICIENT_INDEPENDENT_REPLICATION` for the current archive.

This is a design refusal, not a negative result about the 46 participants or
the quality of their text.

## Evidence Used

The existing private-data feasibility audit reports one observed MEPS response
per participant for each of Q1/Q2/Q3 and one free AI chat session. It does not
establish an event-level log of every unchosen free opportunity, and it does
not contain two independently randomized sessions per participant-condition.
Those facts are sufficient to refuse the new V7 estimands without loading
questionnaire values or treating the archive as training data.

| V7 object | Required design element | Current archive | Decision |
| --- | --- | --- | --- |
| `q_u(c)` free selection | exposed alternatives and selection flag for every opportunity | free chat transcript only | `REFUSE_Q_OPPORTUNITY_UNOBSERVED` |
| `B_u` fixed response operator | independently randomized condition assignment, at least two sessions/person-condition, full-rank design | one same-session Q1/Q2/Q3 set | `REFUSE_B_INSUFFICIENT_INDEPENDENT_REPLICATION` |

## Permitted Use

The archive remains eligible for the already documented narrow use: a
same-session, fixed-prompt **feasibility** comparison after a frozen Japanese
or multilingual representation is declared. It is not used for SUICA training,
external validity, trait inference, state monitoring, or the V7 q/B operator.

See `docs/V7_FIXED_FREE_OCCASION_PROTOCOL.md` and
`reports/MEPS_AI_CONV_FEASIBILITY_AUDIT.md`.
