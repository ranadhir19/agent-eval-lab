# Results — agent-eval-lab experiment

All numbers measured by `experiment.py`; bounds frozen in PREREGISTRATION.md.

## Agent scores (Wilson 95% intervals)
- clean / reference: 60/60 = 100.0% (95% CI 94.0-100.0)
- clean / degraded: 44/60 = 73.3% (95% CI 61.0-82.9)
- clean / null: 0/60 = 0.0% (95% CI 0.0-6.0)
- clean / echo: 0/60 = 0.0% (95% CI 0.0-6.0)
- flawed / reference: 55/60 = 91.7% (95% CI 81.9-96.4)
- flawed / degraded: 39/60 = 65.0% (95% CI 52.4-75.8)
- flawed / null: 2/60 = 3.3% (95% CI 0.9-11.4)
- flawed / echo: 4/60 = 6.7% (95% CI 2.6-15.9)

## Audit (checks A-D in audit.py)
- planted flaws: 12; detected: 11 ['flaw-01', 'flaw-02', 'flaw-03', 'flaw-04', 'flaw-05', 'flaw-06', 'flaw-07', 'flaw-08', 'flaw-10', 'flaw-11', 'flaw-12']
- missed: 1 ['flaw-09']
  - flaw-09: gold and solver share one wrong source table
- flags raised on the clean suite: 0 of 60 []
  - flaw-01: A: reference agent fails this test; C: a deliberately wrong answer passes
  - flaw-02: B: null agent passes this test; B: echo agent passes this test; B: constant agent passes this test; C: a deliberately wrong answer passes
  - flaw-03: A: reference agent fails this test; B: null agent passes this test
  - flaw-04: B: echo agent passes this test; C: a deliberately wrong answer passes
  - flaw-05: C: a deliberately wrong answer passes
  - flaw-06: D: prompt duplicates dev task dev-arith-01
  - flaw-07: A: reference agent fails this test
  - flaw-08: B: echo agent passes this test; C: a deliberately wrong answer passes
  - flaw-10: A: reference agent fails this test; C: a deliberately wrong answer passes
  - flaw-11: A: reference agent fails this test; C: a deliberately wrong answer passes
  - flaw-12: B: echo agent passes this test; B: constant agent passes this test; C: a deliberately wrong answer passes

## Grader validation on the labelled subset (150 items, 60 gold-pass / 90 gold-fail)
- exact: agreement 80.0%, Cohen's kappa 0.545
- normalized: agreement 100.0%, Cohen's kappa 1.000
- rubric: agreement 99.3%, Cohen's kappa 0.986

## Hypotheses (bounds frozen before the run)
- H1 audit detection: CONFIRMED — detected 11/12 (bound 10), false flags 0/60 (bound 3)
- H2 grader acceptance: rubric ACCEPTED — rubric grader agreement 99.3% / kappa 0.986 vs bound 90% / 0.75 — bound met
- H3 false-pass cost: CONFIRMED — null agent 0/60 on clean, 2/60 on flawed; reference drops 8.3 points on the flawed suite

Degraded agent: 73.3% on clean, 65.0% on flawed.
