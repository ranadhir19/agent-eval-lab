"""Task suites for agent-eval-lab.

A task is a dict: id, family, prompt, expected, checker, split.
Checkers are named grading functions in graders.py.

The CLEAN suite's expected outputs come from the reference solver in
agents.py and are cross-checked by `independent_expected()` below — a
second, deliberately differently-written implementation. validate.py
asserts the two agree on every clean task.

The FLAWED suite is the clean suite with 12 of its tests replaced by
planted broken versions. PLANTED_FLAWS is the ground-truth manifest
the audit is scored against; the audit itself never reads it.
"""
import random

# ---------------------------------------------------------------- clean data
_ARITH_TEMPLATES = [
    ("A crate holds {a} bottles. A shop orders {b} crates. How many bottles is that in total?", "mul"),
    ("Sara picked {a} apples and then picked {b} more. How many apples does she have now?", "add"),
    ("A tank had {a} litres of water. {b} litres were drained. How many litres remain?", "sub"),
    ("{a} workers each assemble {b} parts in a day. How many parts do they assemble in total?", "mul"),
    ("Tom had {a} stickers. He bought {b} more packs of stickers. How many stickers does he have now?", "add"),
    ("A rope is {a} metres long. A piece of {b} metres is cut off. How many metres are left?", "sub"),
]

def _arith_tasks():
    rng = random.Random(4101)
    tasks = []
    for i in range(24):
        tmpl, op = _ARITH_TEMPLATES[i % len(_ARITH_TEMPLATES)]
        if op == "mul":
            a, b = rng.randint(3, 14), rng.randint(3, 12)
            ans = a * b
        elif op == "add":
            a, b = rng.randint(15, 240), rng.randint(12, 180)
            ans = a + b
        else:
            a, b = rng.randint(60, 300), rng.randint(10, 59)
            ans = a - b
        tasks.append(dict(id=f"arith-{i+1:02d}", family="arith", op=op, a=a, b=b,
                          prompt=tmpl.format(a=a, b=b), expected=str(ans),
                          checker="numeric", split="eval"))
    return tasks

_EXTRACT_TEXTS = [
    ("Invoice 114, dated 2026-03-14. Customer: Northwind. Total due: 482 dollars.", "total", "482"),
    ("Order 77 shipped on 2026-01-05. Items: 3 cables. Amount paid: 129 dollars.", "amount", "129"),
    ("Ticket 9021 opened 2025-11-30. Priority: high. Fee charged: 75 dollars.", "fee", "75"),
    ("Booking 331, check-in 2026-06-18. Room rate: 210 dollars per night.", "rate", "210"),
    ("Invoice 208, dated 2026-02-01. Customer: Fabrikam. Total due: 967 dollars.", "total", "967"),
    ("Shipment 54 arrived 2026-04-22. Weight: 18 kg. Delivery charge: 46 dollars.", "charge", "46"),
    ("Order 618 shipped on 2025-12-09. Items: 12 notebooks. Amount paid: 240 dollars.", "amount", "240"),
    ("Membership 88 renewed 2026-05-11. Plan: annual. Renewal cost: 320 dollars.", "cost", "320"),
    ("Ticket 417 opened 2026-07-03. Priority: low. Fee charged: 25 dollars.", "fee", "25"),
    ("Invoice 522, dated 2026-08-19. Customer: Contoso. Total due: 154 dollars.", "total", "154"),
    ("Booking 905, check-in 2026-09-27. Room rate: 145 dollars per night.", "rate", "145"),
    ("Shipment 301 arrived 2026-10-02. Weight: 9 kg. Delivery charge: 38 dollars.", "charge", "38"),
    ("Order 246 shipped on 2026-03-29. Items: 7 lamps. Amount paid: 693 dollars.", "amount", "693"),
    ("Membership 19 renewed 2025-10-21. Plan: monthly. Renewal cost: 60 dollars.", "cost", "60"),
    ("Invoice 760, dated 2026-11-08. Customer: Adatum. Total due: 728 dollars.", "total", "728"),
    ("Ticket 655 opened 2026-01-17. Priority: medium. Fee charged: 90 dollars.", "fee", "90"),
    ("Booking 129, check-in 2025-12-25. Room rate: 380 dollars per night.", "rate", "380"),
    ("Shipment 812 arrived 2026-05-30. Weight: 27 kg. Delivery charge: 64 dollars.", "charge", "64"),
]
_FIELD_WORD = {"total": "total due", "amount": "amount paid", "fee": "fee charged",
               "rate": "room rate", "charge": "delivery charge", "cost": "renewal cost"}

def _extract_tasks():
    tasks = []
    for i, (text, field, ans) in enumerate(_EXTRACT_TEXTS):
        tasks.append(dict(id=f"extract-{i+1:02d}", family="extract", field=field,
                          prompt=f"{text} What is the {_FIELD_WORD[field]}? Answer with the number only.",
                          expected=ans, checker="numeric", split="eval"))
    return tasks

_CLASSIFY_ITEMS = [
    ("The battery lasts all day and the screen is gorgeous", "positive"),
    ("The update broke my saved files and support never replied", "negative"),
    ("Setup took two minutes and everything just worked", "positive"),
    ("It is not fast, and the fan is not quiet either", "negative"),
    ("The camera is superb in low light, truly impressive", "positive"),
    ("Delivery was late and the box arrived damaged", "negative"),
    ("Not bad at all — the keyboard feels great", "positive"),
    ("The app crashes every time I open settings", "negative"),
    ("Customer service resolved it within an hour, excellent", "positive"),
    ("The instructions were confusing and the parts did not fit", "negative"),
    ("It is not expensive, and the quality is not poor", "positive"),
    ("Battery drains in an hour, a real disappointment", "negative"),
    ("The new model is faster and noticeably lighter", "positive"),
    ("Not impressed — the hinge feels loose already", "negative"),
    ("A wonderful gift, she uses it every single day", "positive"),
    ("The screen flickers and the speakers crackle", "negative"),
    ("Honestly the best purchase I have made this year", "positive"),
    ("It stopped working after a week, very frustrating", "negative"),
]

def _classify_tasks():
    return [dict(id=f"classify-{i+1:02d}", family="classify",
                 prompt=f"Classify the sentiment of this review as positive or negative: \"{text}\" Answer with one word.",
                 text=text, expected=label, checker="exact", split="eval")
            for i, (text, label) in enumerate(_CLASSIFY_ITEMS)]

def clean_suite():
    return _arith_tasks() + _extract_tasks() + _classify_tasks()

# A small dev split, used only to demonstrate leakage detection.
# Its tasks are generated with a different seed, so no dev prompt
# coincides with an eval prompt — except the one planted leak.
def dev_suite():
    rng = random.Random(777)
    dev = []
    for i in range(6):
        tmpl, op = _ARITH_TEMPLATES[i % len(_ARITH_TEMPLATES)]
        if op == "mul":
            a, b = rng.randint(3, 14), rng.randint(3, 12); ans = a * b
        elif op == "add":
            a, b = rng.randint(15, 240), rng.randint(12, 180); ans = a + b
        else:
            a, b = rng.randint(60, 300), rng.randint(10, 59); ans = a - b
        dev.append(dict(id=f"dev-arith-{i+1:02d}", family="arith", op=op, a=a, b=b,
                        prompt=tmpl.format(a=a, b=b), expected=str(ans),
                        checker="numeric", split="dev"))
    return dev

# ------------------------------------------------------------- flawed suite
# The flawed suite is the clean suite with 12 of its tests replaced by
# broken versions — the way real benchmarks break: the task stays, the
# test is wrong. Each flaw is a class from the SWE-bench audit style:
# wrong gold, degenerate checker, leakage, loose checker, impossible
# format. PLANTED_FLAWS is the ground-truth manifest the audit is
# scored against; the audit never reads it.
def _flawed_replacements():
    arith = {t["id"]: t for t in _arith_tasks()}
    ext = {t["id"]: t for t in _extract_tasks()}
    cls = {t["id"]: t for t in _classify_tasks()}
    rep = {}

    t = dict(arith["arith-02"]); t.update(id="flaw-01",
        expected=str(int(t["expected"]) + 1)); rep["arith-02"] = t      # wrong gold (+1)
    t = dict(ext["extract-03"]); t.update(id="flaw-02", checker="any"); rep["extract-03"] = t  # checker accepts everything
    t = dict(cls["classify-05"]); t.update(id="flaw-03", expected=""); rep["classify-05"] = t  # only the empty answer passes
    t = dict(ext["extract-06"]); t.update(id="flaw-04", checker="echo"); rep["extract-06"] = t  # parroting the prompt passes
    t = dict(arith["arith-01"]); t.update(id="flaw-05", checker="loose_numeric"); rep["arith-01"] = t  # ±50% tolerance
    t = dict(dev_suite()[0]); t.update(id="flaw-06", split="eval"); rep["arith-04"] = t  # dev task leaked into eval, displacing arith-04
    t = dict(arith["arith-05"]); t.update(id="flaw-07", checker="exact",
        expected=f" {int(t['expected']):,} dollars "); rep["arith-05"] = t   # format no correct answer can match
    t = dict(ext["extract-01"]); t.update(id="flaw-08", checker="contains"); rep["extract-01"] = t  # substring: "482" also matches "4820"
    # flaw-09: the gold comes from the same lookup the reference solver
    # uses, and the lookup is wrong — a shared-source error. The task
    # text says the amount is 315; the shared table (and gold) say 300.
    t = dict(ext["extract-02"])
    t.update(id="flaw-09", shared_table=True,
             prompt="Order 77 shipped on 2026-01-05. Items: 3 cables. Amount paid: 315 dollars. "
                    "What is the amount paid? Answer with the number only.",
             expected="300"); rep["extract-02"] = t
    a = dict(cls["classify-01"]); a.update(id="flaw-10", expected="negative"); rep["classify-01"] = a  # swapped gold labels
    b = dict(cls["classify-02"]); b.update(id="flaw-11", expected="positive"); rep["classify-02"] = b
    t = dict(arith["arith-03"]); t.update(id="flaw-12", checker="has_digit"); rep["arith-03"] = t  # any answer containing a digit passes
    return rep

PLANTED_FLAWS = {
    "flaw-01": "wrong gold value",
    "flaw-02": "checker accepts any output",
    "flaw-03": "only the empty answer passes",
    "flaw-04": "echoing the prompt passes",
    "flaw-05": "numeric tolerance of ±50 percent",
    "flaw-06": "dev task duplicated into the eval split",
    "flaw-07": "expected format no correct answer can match",
    "flaw-08": "substring checker (482 also matches 4820)",
    "flaw-09": "gold and solver share one wrong source table",
    "flaw-10": "swapped gold label (pair, 1 of 2)",
    "flaw-11": "swapped gold label (pair, 2 of 2)",
    "flaw-12": "any answer containing a digit passes",
}

def flawed_suite():
    rep = _flawed_replacements()
    return [rep.get(t["id"], t) for t in clean_suite()]

# --------------------------------------- independent cross-check of the gold
def independent_expected(task):
    """Second implementation of every clean task's expected output,
    written differently from agents.reference_agent on purpose."""
    import re
    if task["family"] == "arith":
        a, b, op = task["a"], task["b"], task["op"]
        return str({"add": a + b, "sub": a - b, "mul": a * b}[op])
    if task["family"] == "extract":
        m = re.search(r"(\d+) dollars", task["prompt"])
        return m.group(1) if m else None
    if task["family"] == "classify":
        neg = ("not ", "never", "broke", "damaged", "crashes", "confusing",
               "drains", "disappointment", "loose", "flickers", "crackle",
               "frustrating", "stopped working", "late and")
        pos = ("gorgeous", "just worked", "superb", "great", "excellent",
               "impressive", "wonderful", "best purchase", "faster and noticeably")
        text = task["text"].lower()
        if "not bad" in text or "not expensive" in text:
            return "positive"
        score = sum(w in text for w in pos) - sum(w in text for w in neg)
        return "positive" if score > 0 else "negative"
    return None
