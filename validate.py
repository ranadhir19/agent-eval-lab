#!/usr/bin/env python3
"""agent-eval-lab harness: compile + unit tests + experiment re-run
with a byte-exact RESULTS.md comparison (the experiment is
deterministic; if the numbers move, something changed and the harness
says so). Prints PASS/FAIL per stage."""
import subprocess, sys, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ok = True

def stage(name, fn):
    global ok
    try:
        fn(); print(f"PASS {name}")
    except Exception as e:
        ok = False; print(f"FAIL {name}: {e}")

def s_compile():
    r = subprocess.run([sys.executable, "-m", "compileall", "-q", HERE],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-500:]

def s_tests():
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s",
                        os.path.join(HERE, "tests"), "-v"],
                       capture_output=True, text=True, cwd=HERE)
    assert r.returncode == 0, (r.stdout + r.stderr)[-1500:]

def s_experiment():
    before = open(os.path.join(HERE, "RESULTS.md"), "rb").read()
    r = subprocess.run([sys.executable, os.path.join(HERE, "experiment.py")],
                       capture_output=True, text=True, cwd=HERE)
    assert r.returncode == 0, r.stderr[-1500:]
    after = open(os.path.join(HERE, "RESULTS.md"), "rb").read()
    assert before == after, "RESULTS.md changed on re-run (non-determinism or code drift)"

stage("compile", s_compile)
stage("unit tests", s_tests)
stage("experiment determinism (RESULTS.md byte-identical)", s_experiment)
print("OVERALL", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
