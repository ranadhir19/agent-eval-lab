"""Checkers (score one task output against its test) and graders
(score an output against a gold answer, for grader validation).

The distinction matters: a *checker* is part of a benchmark — if it is
broken, the benchmark is broken. A *grader* is a measurement tool you
choose — and any grader, cheap or expensive, must itself be validated
against labelled data before its scores mean anything.
"""
import re

# ---------------------------------------------------------------- checkers
def _first_number(s):
    m = re.search(r"-?\d[\d,]*\.?\d*", str(s))
    return float(m.group(0).replace(",", "")) if m else None

def check_exact(out, task):
    return str(out).strip() == str(task["expected"]).strip()

def check_numeric(out, task):
    got, want = _first_number(out), _first_number(task["expected"])
    return got is not None and want is not None and abs(got - want) < 1e-9

def check_loose_numeric(out, task):
    got, want = _first_number(out), _first_number(task["expected"])
    return got is not None and want is not None and abs(got - want) <= 0.5 * abs(want)

def check_any(out, task):
    return True

def check_echo(out, task):
    out = str(out)
    if str(task["expected"]) in out:
        return True
    words = task["prompt"].split()
    return sum(w in out for w in words) >= 0.8 * len(words)

def check_contains(out, task):
    return str(task["expected"]) in str(out)

def check_has_digit(out, task):
    return any(c.isdigit() for c in str(out))

CHECKERS = {"exact": check_exact, "numeric": check_numeric,
            "loose_numeric": check_loose_numeric, "any": check_any,
            "echo": check_echo, "contains": check_contains,
            "has_digit": check_has_digit}

def passes(out, task):
    return CHECKERS[task["checker"]](out, task)

# ----------------------------------------------------------------- graders
def grade_exact(out, expected):
    return str(out).strip() == str(expected).strip()

def _normalize(s):
    s = str(s).lower().strip()
    s = s.replace(",", "")
    s = re.sub(r"\s+", " ", s)
    s = s.rstrip(".")
    n = _first_number(s)
    if n is not None and re.fullmatch(r"-?\d[\d,]*\.?\d*\s*(dollars)?", str(s).strip().lower().replace(",", "")):
        return f"num:{n:g}"
    return s

def grade_normalized(out, expected):
    return _normalize(out) == _normalize(expected)

def _tokens(s):
    return set(re.findall(r"[a-z0-9]+", str(s).lower()))

def grade_rubric(out, expected, prompt=""):
    """A deterministic stand-in for a cheap model judge, with its
    formula fixed a priori: similarity to the expected answer, numeric
    closeness, and a 'groundedness' term rewarding outputs whose
    tokens appear in the prompt. Pass at a score of 0.5 or above.

    It exists to be validated, not to be trusted: experiment.py
    measures its agreement with gold labels against the pre-registered
    acceptance bound in PREREGISTRATION.md."""
    jac = len(_tokens(out) & _tokens(expected)) / max(1, len(_tokens(out) | _tokens(expected)))
    got, want = _first_number(out), _first_number(expected)
    if got is not None and want is not None:
        closeness = 1.0 if got == want else max(0.0, 1.0 - abs(got - want) / max(1.0, abs(want)))
    elif got is None and want is None:
        closeness = 0.5
    else:
        closeness = 0.0
    ptoks = _tokens(prompt)
    echo = (sum(t in ptoks for t in _tokens(out)) / max(1, len(_tokens(out)))) if prompt else 0.0
    return 0.4 * jac + 0.3 * closeness + 0.3 * echo >= 0.5

GRADERS = {"exact": lambda out, exp, prompt="": grade_exact(out, exp),
           "normalized": lambda out, exp, prompt="": grade_normalized(out, exp),
           "rubric": grade_rubric}
