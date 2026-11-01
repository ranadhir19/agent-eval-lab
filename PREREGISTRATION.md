# Pre-registration — agent-eval-lab measured experiment

Written before `experiment.py` was first run. The bounds below are the
claims the lab is allowed to make. If a result misses its bound, the lab
reports the miss — the bound does not move.

## Setup (frozen)

- Clean eval suite: 60 tasks (24 arithmetic, 18 extraction, 18
  classification), every expected output produced by a reference solver
  and cross-checked by an independent second implementation.
- Flawed eval suite: the same 60 tasks with 12 of their tests replaced
  by planted broken versions (`suite.PLANTED_FLAWS` is the ground-truth
  manifest), 60 tasks total.
- Agents: a reference agent (correct by construction), a degraded agent
  (three documented systematic errors), a null agent (returns the empty
  string), an echo agent (returns the prompt).
- Graders: exact string match; normalized match; a rubric grader
  (deterministic token-overlap + numeric-closeness scorer standing in
  for a cheap model judge — the procedure being tested is *validating a
  grader against labels*, which is grader-agnostic).
- Labelled subset: 150 items (30 tasks × 5 output variants) whose gold
  pass/fail labels are known by construction.

## Hypotheses and bounds

- **H1 — audit detection.** The audit procedure (reference-failure,
  probe-agent, mutation and duplication checks) flags at least 10 of
  the 12 planted flaws, and falsely flags at most 3 of the 60 clean
  tasks.
- **H2 — cheap-grader acceptance bound.** The rubric grader is accepted
  as the suite's primary grader only if it agrees with the gold labels
  on at least 90% of the labelled subset AND reaches Cohen's kappa of
  at least 0.75. Otherwise the lab falls back to the strictest grader
  that clears the bound, and says so.
- **H3 — false-pass cost.** On the clean suite the null agent scores 0.
  On the flawed suite it scores at least 2 tasks, and the reference
  agent's score drops by at least 4 percentage points versus the clean
  suite — points lost to test bugs, not to agent errors.

## Reporting rule

`experiment.py` prints every number and writes `RESULTS.md`. Whatever
the outcome, the numbers are published as measured — including a failed
hypothesis. A failed H2 is a result, not an embarrassment: it is the
reason the grader-validation step exists.
