"""The agents under test. All deterministic, all documented — the lab
measures the *suite and the graders*, so the agents are instruments,
not the object of study.

- reference_agent: correct by construction on the clean suite. One
  deliberate exception: for tasks marked `shared_table`, it reads its
  answer from SHARED_TABLE — the same source the gold labels were
  generated from. When that source is wrong, agent and gold are wrong
  together, and no output-based check can see it. That is the point.
- degraded_agent: a plausible weaker agent with three systematic
  errors (no random noise — systematic errors are what evals exist
  to catch):
    * multiplication: computes a*(b-1) when b is greater than 5;
    * extraction: on total/amount questions it returns the day of
      the month from the date in the text instead of the money;
    * classification: a lexicon with no negation handling.
- null_agent: returns the empty string. Scores 0 on any honest suite.
- echo_agent: returns the prompt verbatim.
"""
import re

# The shared source: gold labels for shared_table tasks were generated
# from this table, and the reference agent reads it too. Its flaw-09
# entry is wrong (the task text says 315) — by design.
SHARED_TABLE = {"flaw-09": "300"}

_POS = {"gorgeous", "superb", "impressive", "impressed", "excellent",
        "great", "wonderful", "best", "faster", "lighter", "worked",
        "resolved", "fast", "quiet"}
_NEG = {"broke", "damaged", "crashes", "confusing", "drains",
        "disappointment", "loose", "flickers", "crackle", "frustrating",
        "stopped", "late", "bad", "expensive", "poor"}

_FIELD_PHRASE = {"total": "Total due:", "amount": "Amount paid:",
                 "fee": "Fee charged:", "rate": "Room rate:",
                 "charge": "Delivery charge:", "cost": "Renewal cost:"}

def _classify(text, use_negation):
    toks = re.findall(r"[a-z']+", text.lower())
    score = 0
    for i, tok in enumerate(toks):
        val = 1 if tok in _POS else -1 if tok in _NEG else 0
        if val and use_negation and i > 0 and toks[i - 1] == "not":
            val = -val
        score += val
    return "positive" if score > 0 else "negative"

def _extract(task, date_confusion=False):
    if date_confusion and task["field"] in ("total", "amount"):
        m = re.search(r"\d{4}-\d{2}-(\d{2})", task["prompt"])
        if m:
            return str(int(m.group(1)))
    phrase = _FIELD_PHRASE[task["field"]]
    m = re.search(re.escape(phrase) + r"\s*(\d+)", task["prompt"])
    return m.group(1) if m else ""

def _arith(task, degraded=False):
    a, b, op = task["a"], task["b"], task["op"]
    if op == "add":
        return str(a + b)
    if op == "sub":
        return str(a - b)
    if degraded and b > 5:
        return str(a * (b - 1))
    return str(a * b)

def reference_agent(task):
    if task["family"] == "arith":
        return _arith(task)
    if task["family"] == "extract":
        # The reference pipeline reads shared-source tables where they
        # exist — the same source the gold labels came from.
        if task.get("shared_table"):
            return SHARED_TABLE[task["id"]]
        return _extract(task)
    return _classify(task["text"], use_negation=True)

def degraded_agent(task):
    if task["family"] == "arith":
        return _arith(task, degraded=True)
    if task["family"] == "extract":
        return _extract(task, date_confusion=True)
    return _classify(task["text"], use_negation=False)

def null_agent(task):
    return ""

def echo_agent(task):
    return task["prompt"]

AGENTS = {"reference": reference_agent, "degraded": degraded_agent,
          "null": null_agent, "echo": echo_agent}
