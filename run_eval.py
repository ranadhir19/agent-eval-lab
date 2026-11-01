"""Run agents against suites and report scores with Wilson score
intervals. A pass rate without an interval is a marketing number:
at 60 tasks, a 95% interval is roughly ±10 points wide."""
import math
from agents import AGENTS
from graders import passes

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, cen - half), min(1.0, cen + half)

def score(agent_name, tasks):
    fn = AGENTS[agent_name]
    k = sum(1 for t in tasks if passes(fn(t), t))
    p, lo, hi = wilson(k, len(tasks))
    return dict(agent=agent_name, passed=k, total=len(tasks),
                rate=p, lo=lo, hi=hi)

def main():
    import suite
    for sname, tasks in (("clean", suite.clean_suite()),
                         ("flawed", suite.flawed_suite())):
        print(f"--- {sname} suite ({len(tasks)} tasks)")
        for aname in AGENTS:
            s = score(aname, tasks)
            print(f"{aname:>10}: {s['passed']:>2}/{s['total']}  "
                  f"{100*s['rate']:5.1f}%  (95% CI {100*s['lo']:.1f}-{100*s['hi']:.1f})")

if __name__ == "__main__":
    main()
