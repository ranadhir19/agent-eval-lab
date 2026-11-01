"""The pre-registered experiment (see PREREGISTRATION.md).

Builds the labelled subset, validates the three graders against gold
labels, runs the audit on the clean and flawed suites, scores all
agents on both suites, and tests H1/H2/H3 against the frozen bounds.
Writes RESULTS.md with every number, pass or fail.
"""
import os
import suite, agents, graders
from audit import audit_suite
from run_eval import score

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------ labelled set
def labelled_subset():
    clean = suite.clean_suite()
    picked = ([t for t in clean if t["family"] == "arith"][:10]
              + [t for t in clean if t["family"] == "extract"][:10]
              + [t for t in clean if t["family"] == "classify"][:10])
    items = []  # (task, output, gold_pass)
    for t in picked:
        exp = t["expected"]
        items.append((t, exp, True))                                    # plain
        if t["family"] == "classify":
            items.append((t, exp.capitalize(), True))                   # formatted
            items.append((t, "negative" if exp == "positive" else "positive", False))  # delta
            items.append((t, "neutral", False))                         # swap
        else:
            v = int(exp)
            items.append((t, f"{v:,}" if v >= 1000 else f"{v}.00", True))  # formatted
            items.append((t, str(v + 1), False))                        # delta
            if t["family"] == "arith":
                a, b, op = t["a"], t["b"], t["op"]
                wrong = {"mul": a + b, "add": a - b, "sub": a + b}[op]
            else:
                import re
                wrong = re.findall(r"\d+", t["prompt"])[0]
            items.append((t, str(wrong), False))                        # swap
        items.append((t, "", False))                                    # empty
    return items

def kappa(pairs):
    tp = sum(1 for g, p in pairs if g and p); tn = sum(1 for g, p in pairs if not g and not p)
    fp = sum(1 for g, p in pairs if not g and p); fn = sum(1 for g, p in pairs if g and not p)
    n = len(pairs); po = (tp + tn) / n
    pe = ((tp + fn) * (tp + fp) + (fp + tn) * (fn + tn)) / (n * n)
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0

def main():
    clean, flawed, dev = suite.clean_suite(), suite.flawed_suite(), suite.dev_suite()
    L = []
    def w(s=""):
        L.append(s); print(s)

    w("# Results — agent-eval-lab experiment")
    w()
    w("All numbers measured by `experiment.py`; bounds frozen in PREREGISTRATION.md.")
    w()
    # ---- agent scores
    w("## Agent scores (Wilson 95% intervals)")
    scores = {}
    for sname, tasks in (("clean", clean), ("flawed", flawed)):
        for aname in agents.AGENTS:
            s = score(aname, tasks); scores[(sname, aname)] = s
            w(f"- {sname} / {aname}: {s['passed']}/{s['total']} = {100*s['rate']:.1f}% "
              f"(95% CI {100*s['lo']:.1f}-{100*s['hi']:.1f})")
    w()
    # ---- audit
    flags_clean = audit_suite(clean, dev)
    flags_flawed = audit_suite(flawed, dev)
    detected = sorted(set(suite.PLANTED_FLAWS) & set(flags_flawed))
    missed = sorted(set(suite.PLANTED_FLAWS) - set(flags_flawed))
    false_flags = sorted(set(flags_clean))
    w("## Audit (checks A-D in audit.py)")
    w(f"- planted flaws: 12; detected: {len(detected)} {detected}")
    w(f"- missed: {len(missed)} {missed}")
    for m in missed:
        w(f"  - {m}: {suite.PLANTED_FLAWS[m]}")
    w(f"- flags raised on the clean suite: {len(false_flags)} of 60 {false_flags}")
    for tid in sorted(flags_flawed):
        w(f"  - {tid}: {'; '.join(flags_flawed[tid])}")
    w()
    # ---- grader validation
    items = labelled_subset()
    w(f"## Grader validation on the labelled subset ({len(items)} items, "
      f"{sum(1 for _, _, g in items if g)} gold-pass / {sum(1 for _, _, g in items if not g)} gold-fail)")
    gres = {}
    for gname, gfn in graders.GRADERS.items():
        pairs = [(gold, gfn(out, t["expected"], t["prompt"])) for t, out, gold in items]
        agree, kap = kappa(pairs)
        gres[gname] = (agree, kap)
        w(f"- {gname}: agreement {100*agree:.1f}%, Cohen's kappa {kap:.3f}")
    w()
    # ---- hypotheses
    w("## Hypotheses (bounds frozen before the run)")
    h1 = len(detected) >= 10 and len(false_flags) <= 3
    w(f"- H1 audit detection: {'CONFIRMED' if h1 else 'NOT CONFIRMED'} — "
      f"detected {len(detected)}/12 (bound 10), false flags {len(false_flags)}/60 (bound 3)")
    rubric_ok = gres["rubric"][0] >= 0.90 and gres["rubric"][1] >= 0.75
    fallback = None
    if not rubric_ok:
        for gname in ("normalized", "exact"):
            if gres[gname][0] >= 0.90 and gres[gname][1] >= 0.75:
                fallback = gname; break
    h2_line = (f"rubric grader agreement {100*gres['rubric'][0]:.1f}% / kappa {gres['rubric'][1]:.3f} "
               f"vs bound 90% / 0.75 — ")
    if rubric_ok:
        w(f"- H2 grader acceptance: rubric ACCEPTED — " + h2_line + "bound met")
    else:
        w(f"- H2 grader acceptance: rubric REJECTED — " + h2_line +
          (f"bound missed; lab falls back to the {fallback} grader" if fallback
           else "bound missed and no grader clears it"))
    ref_drop = 100 * (scores[("clean", "reference")]["rate"] - scores[("flawed", "reference")]["rate"])
    h3 = scores[("clean", "null")]["passed"] == 0 and scores[("flawed", "null")]["passed"] >= 2 and ref_drop >= 4
    w(f"- H3 false-pass cost: {'CONFIRMED' if h3 else 'NOT CONFIRMED'} — "
      f"null agent 0/{scores[('clean','null')]['total']} on clean, "
      f"{scores[('flawed','null')]['passed']}/{scores[('flawed','null')]['total']} on flawed; "
      f"reference drops {ref_drop:.1f} points on the flawed suite")
    w()
    w(f"Degraded agent: {100*scores[('clean','degraded')]['rate']:.1f}% on clean, "
      f"{100*scores[('flawed','degraded')]['rate']:.1f}% on flawed.")
    open(os.path.join(HERE, "RESULTS.md"), "w").write("\n".join(L) + "\n")

if __name__ == "__main__":
    main()
