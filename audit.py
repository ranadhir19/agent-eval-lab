"""The benchmark audit: four checks that need no knowledge of which
tests are broken. Each check flags tasks with a stated reason; the
audit's worth is measured against planted ground truth it never sees.

  A. reference-failure — a task a known-correct agent fails is a
     suspect test, not a suspect agent.
  B. probe-pass — a task that a null, echo or constant agent passes
     is measuring nothing.
  C. mutation — if a deliberately wrong answer (off by one, times
     ten, flipped label, swapped entity) still passes, the checker
     is too loose to grade with.
  D. duplication — an eval task whose prompt duplicates a dev task
     (or another eval task) is leakage: the score partly measures
     memorization of the tuning split.
"""
import re
from agents import reference_agent, null_agent, echo_agent
from graders import passes

def _norm_prompt(p):
    return re.sub(r"\s+", " ", p.strip().lower())

def _tokens(s):
    return set(re.findall(r"[a-z0-9]+", s.lower()))

def _mutants(task, out):
    """Deliberately-wrong variants of a correct output."""
    import graders
    muts = []
    n = graders._first_number(out)
    if n is not None:
        muts.append(str(int(n) + 1) if n == int(n) else str(n + 1))
        muts.append(str(int(n) * 10) if n == int(n) else str(n * 10))
    if out.strip() == "positive":
        muts.append("negative")
    elif out.strip() == "negative":
        muts.append("positive")
    nums = re.findall(r"\d+", task["prompt"])
    if nums and out.strip() != nums[0]:
        muts.append(nums[0])
    return muts

def audit_suite(tasks, dev_tasks=()):
    flags = {}  # task_id -> list of reasons
    def flag(tid, reason):
        flags.setdefault(tid, []).append(reason)
    for t in tasks:
        ref_out = reference_agent(t)
        if not passes(ref_out, t):
            flag(t["id"], "A: reference agent fails this test")
        for name, probe in (("null", null_agent), ("echo", echo_agent)):
            if passes(probe(t), t):
                flag(t["id"], f"B: {name} agent passes this test")
        if passes("0", t):
            flag(t["id"], "B: constant agent passes this test")
        if any(passes(m, t) for m in _mutants(t, ref_out)):
            flag(t["id"], "C: a deliberately wrong answer passes")
    dev_norm = {_norm_prompt(d["prompt"]): d["id"] for d in dev_tasks}
    seen = {}
    for t in tasks:
        np_ = _norm_prompt(t["prompt"])
        if np_ in dev_norm:
            flag(t["id"], f"D: prompt duplicates dev task {dev_norm[np_]}")
        if np_ in seen:
            flag(t["id"], f"D: prompt duplicates eval task {seen[np_]}")
        seen[np_] = t["id"]
    return flags
