"""One command that says whether this repository is intact. Read-only.

FOR A DELEGATED AGENT (Antigravity IDE, a CI job, a reviewer)
    Run this and report the PASS/FAIL table. Nothing else is needed, and nothing else
    should be done. It writes NO file inside the repository -- every check either reads
    or works in a system temp directory -- so it cannot corrupt the evidence it checks.

    ⛔ DO NOT clone Benchpress. A clone at the pinned commit already exists at
       C:\\Users\\User\\Desktop\\benchpress_test. Point BENCHPRESS_PATH at it. If you
       ever do clone one anywhere, DELETE it when finished -- a stray 786 MB checkout
       is exactly the kind of debris this project does not want.

    ⛔ DO NOT "fix" a failure. A failing check here is a finding, and findings are the
       product. Report the exact output and stop.

WHAT IT CHECKS
    1 toolchain pin   Benchpress commit SHA, tracked-file cleanliness, 5 module hashes
    2 test suite      pytest, including the D-2.1 tautology and seed-integrity regressions
    3 inventory       41 recorded numbers vs a fresh recomputation (29 raw, 12 derived)
    4 replication     6 circuits x 12 seeds x 2 Qiskit versions against the reference
    5 tautology proof the withdrawn paired column is still provably data-independent
    6 paper claims    paper_check.py -- every quantitative claim in PAPER.md recomputed

WHAT CHECK 6 DOES NOT PROVE (added 2026-09-08, and stated here so nobody assumes more)
    paper_check.py recomputes each figure and then asserts the formatted value APPEARS
    in PAPER.md. Presence is not placement: a number can be found in an unrelated
    sentence and the check still passes. The section-bound assertions added alongside
    this stage narrow that for the load-bearing figures, but the weakness is structural,
    not fixed. Check 6 catches drift between the code and the manuscript. It does not
    prove a number is quoted in the right claim.

USAGE
    set BENCHPRESS_PATH, then:
        envs/bp202/Scripts/python.exe verify.py
    Exit code 0 = everything intact. Non-zero = the number of failed checks.
"""

import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
PY200 = os.path.join(ROOT, "envs", "bp200", "Scripts", "python.exe")


def run(label, cmd, needs_bp=True):
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800)
        ok, out = p.returncode == 0, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:
        ok, out = False, f"{type(exc).__name__}: {exc}"
    return {"label": label, "ok": ok, "seconds": time.perf_counter() - t0,
            "tail": "\n".join(out.strip().splitlines()[-12:])}


def main():
    bp = os.environ.get("BENCHPRESS_PATH")
    print(f"\n  qvalidation — integrity check")
    print(f"  python          {sys.version.split()[0]}  ({PY})")
    print(f"  BENCHPRESS_PATH {bp or 'NOT SET'}")

    if not bp or not os.path.isdir(bp):
        print("\n  FAIL: set BENCHPRESS_PATH to a Benchpress checkout at the pinned "
              "commit.\n        A clone already exists at "
              "C:\\Users\\User\\Desktop\\benchpress_test — use it, do not make "
              "another.\n")
        sys.exit(1)

    checks = [
        run("1 toolchain pin", [PY, "-c",
            "import json,sys;from sweep_bp import benchpress_pin,PINNED_MODULES;"
            "want=json.load(open('results/raw/benchpress_pin.json'));"
            "got=benchpress_pin();"
            "bad=[m for m in PINNED_MODULES if got['benchpress_module_sha256'].get(m)"
            "!=want['benchpress_module_sha256'].get(m)];"
            "assert got['benchpress_commit']==want['benchpress_commit'],"
            "f\"commit {got['benchpress_commit']} != {want['benchpress_commit']}\";"
            "assert not got['benchpress_dirty'],'tracked files modified';"
            "assert not bad,f'module hash mismatch: {bad}';"
            "print('commit',got['benchpress_commit'][:12],'| 5 modules matched')"]),
        run("2 test suite", [PY, "-m", "pytest", "tests/", "-q"]),
        run("3 inventory", [PY, "inventory.py", "--check"]),
        run("4 replication", [PY, "replication/replicate.py", "--stage", "verify",
                              "--old", "replication/out_q200.jsonl",
                              "--new", "replication/out_q202.jsonl"]),
        run("5 tautology proof", [PY, "paired.py", "--prove"]),
        run("6 paper claims", [PY, "paper_check.py"]),
    ]

    print(f"\n  {'check':<20s} {'result':>7s} {'time':>8s}")
    print("  " + "-" * 38)
    for c in checks:
        print(f"  {c['label']:<20s} {'PASS' if c['ok'] else 'FAIL':>7s} "
              f"{c['seconds']:>7.1f}s")

    failed = [c for c in checks if not c["ok"]]
    for c in failed:
        print(f"\n  ---- {c['label']} output ----\n{c['tail']}")

    if failed:
        print(f"\n  {len(failed)} of {len(checks)} checks FAILED. Report this output "
              f"verbatim. Do not attempt a fix.\n")
    else:
        print(f"\n  All {len(checks)} checks passed. The repository is intact.\n")
    sys.exit(len(failed))


if __name__ == "__main__":
    main()
