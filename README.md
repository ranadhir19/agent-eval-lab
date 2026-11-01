# agent-eval-lab

**Prove it works: an eval-integrity toolkit for agent builders.**

Companion lab to The Architect's AI Workshop, Agent Series Ep. 4 —
"Prove It Works: Building an Eval That Can Catch a Broken Agent
(and a Broken Benchmark)".

Most agent content teaches you to build the agent. This lab teaches
you to audit the proof: design a task suite, validate your graders
against labelled data, and run an audit that catches broken tests —
because a benchmark with flawed tests measures the tests. (The
field's object lesson: OpenAI stopped reporting SWE-bench Verified in
February 2026 after an audit found 59.4% of the reviewed problems had
flawed tests.)

Pure Python standard library. No dependencies, no API keys, fully
deterministic.

## What's in the box

| File | What it does |
|---|---|
| `suite.py` | A clean 60-task suite (arithmetic, extraction, classification) with gold answers cross-checked by an independent second implementation — and a flawed twin: the same suite with 12 tests replaced by planted broken versions. |
| `agents.py` | Four instruments: a reference agent (correct by construction), a degraded agent (three documented systematic errors), a null agent (returns nothing), an echo agent (returns the prompt). |
| `graders.py` | Task checkers, plus three graders (exact, normalized, rubric) whose accuracy is itself measured. The rubric grader is a deterministic stand-in for a cheap model judge; the procedure being taught — validate any grader against labels — is grader-agnostic. |
| `audit.py` | The audit: four checks that need no knowledge of which tests are broken. A: a known-correct agent failing a test makes the test the suspect. B: a test that null/echo/constant agents pass measures nothing. C: a test that deliberately wrong answers pass is too loose. D: an eval task duplicating a dev task is leakage. |
| `run_eval.py` | Scores every agent on both suites, with Wilson 95% intervals. |
| `experiment.py` | The pre-registered experiment; writes `RESULTS.md`. |
| `PREREGISTRATION.md` | The hypotheses and acceptance bounds, frozen before the first run. |
| `validate.py` | The harness: compile, unit tests, and an experiment re-run that must reproduce `RESULTS.md` byte for byte. |

## Run it

```bash
python3 validate.py        # harness: everything below, checked
python3 run_eval.py        # agent scores on both suites
python3 experiment.py      # full experiment; rewrites RESULTS.md
```

## What the experiment found (measured; see RESULTS.md)

- The reference agent scores **100%** on the clean suite and **91.7%**
  on the flawed suite. It did not get worse — five of its "failures"
  are test bugs (wrong gold, swapped labels, an impossible format).
- The null agent scores **0** on the clean suite and **2/60** on the
  flawed one. The echo agent — it returns the question as the answer —
  scores **4/60**. A broken benchmark pays agents that do nothing.
- The audit detects **11 of the 12** planted flaws and raises **zero**
  false flags on the clean suite. The one it misses is the
  shared-source flaw: the gold label and the reference solver were
  both generated from the same wrong table, so every output-based
  check passes. That class is only catchable by independently
  re-deriving the gold — which is why the clean suite's answers are
  cross-checked by a second implementation here.
- Grader validation on 150 labelled items: the **exact** grader
  agrees with gold labels only **80.0%** of the time (kappa 0.545) —
  it rejects correct answers for their formatting, and it *fails* the
  pre-registered acceptance bound. The boring **normalized** grader
  scores 100%. The cheap **rubric** grader scores **99.3%**
  (kappa 0.986) and is *accepted* under the frozen bound — with one
  documented miss: it passed a wrong extraction answer ("54", the
  shipment number from the prompt) because the number was close and
  appeared in the prompt. A judge that has been validated has a
  measured error rate; a judge that hasn't is a hope.

## The honest criteria

The bounds in `PREREGISTRATION.md` were written before the experiment
ran and they do not move. Had the rubric grader missed its bound, the
lab would have fallen back to the strictest grader that cleared it,
and said so. Had the audit detected fewer than 10 of 12, that would
be the headline. Report the measurement, not the hope.

## Method notes and limits

- The agents are instruments, not products: the degraded agent's
  errors are systematic and documented so score movements are
  attributable.
- At 60 tasks the Wilson intervals are wide (roughly ±10 points).
  That is itself one of the lab's results: differences smaller than
  the interval are not evidence, for anyone's benchmark.
- The rubric grader is a deterministic proxy. Re-run the same
  validation procedure with a real model judge before trusting one;
  the procedure, not the proxy, is the deliverable.
