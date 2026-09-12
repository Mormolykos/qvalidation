"""Prove the verifier can turn RED — including on the three attacks that beat v3.

HISTORY, BECAUSE IT IS THE POINT
    v2's verifier was defeated by corrupting raw data. v3 fixed that and added this file
    to prove it. v3 was then defeated three more ways by an auditor who attacked what its
    author had not imagined:

      H  all 36 saved risk intervals -> [0.900000, 0.999999], flags and counts untouched
      K  visible results table -> 0/26, with the correct rows hidden in an HTML comment
      F  one raw observation changed, then the local manifest regenerated

    All three returned 9/9 PASS. They are preserved below verbatim, alongside the earlier
    A-E, and each declares WHICH layer must catch it. A layer passing is acceptable only
    when another catches the same attack; a mutation caught by nothing fails this test.

    The lesson is not that the earlier verifiers were careless. A verifier only tests the
    attacks its author imagined, and the author is the worst-placed person to imagine
    them. This file is the record of what has actually been tried, not a proof of safety.

SAFETY
    Every mutation runs in a throwaway `git archive` snapshot in the system temp
    directory. Nothing here writes to the repository, and it refuses to run if the
    snapshot path resolves inside it.

USAGE
    python mutation_test.py            # all mutations
    python mutation_test.py --quick    # the three that defeated v3
    python mutation_test.py --only H   # one
"""

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
ARM = "results/raw/prereg/knn_n67_heavy-hex_q200.jsonl"
SUMMARY = "results/summary/prereg_heavy-hex.csv"

LAYERS = {                      # name -> script
    "science":   "raw_endpoint.py",
    "integrity": "raw_integrity.py",
    "anchor":    "v2_anchor.py",
    "derived":   "derived_binding.py",
    "rendered":  "manuscript_binding.py",
}
# `derived` replays the original 400x400,000 Monte-Carlo bootstrap and costs about four
# minutes. Running it for all eleven mutations would take three quarters of an hour to
# learn nothing new, so it runs where it is REQUIRED to catch the attack, and where it is
# skipped the table says so rather than printing a pass it did not earn.
SLOW = {"derived"}


def snapshot(dst):
    tar = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, capture_output=True)
    if tar.returncode:
        raise SystemExit("git archive failed: " + tar.stderr.decode()[:300])
    p = subprocess.run(["tar", "-x", "-C", dst], input=tar.stdout, capture_output=True)
    if p.returncode:
        raise SystemExit("tar failed: " + p.stderr.decode()[:300])


def run(snap, script):
    env = dict(os.environ)
    env.setdefault("BENCHPRESS_PATH", r"C:\Users\User\Desktop\benchpress_test")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    parts = script.split()
    p = subprocess.run([PY, *parts], cwd=snap, capture_output=True, text=True,
                       env=env, timeout=3600)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# ---------------------------------------------------------------- the mutations

def _rows(snap, path):
    return [json.loads(l) for l in open(os.path.join(snap, path), encoding="utf-8")
            if l.strip()]


def _write_rows(snap, path, rows):
    open(os.path.join(snap, path), "w", encoding="utf-8").write(
        "\n".join(json.dumps(r) for r in rows) + "\n")


def mut_A(snap):
    """audit T7: every candidate count in one arm -> 100."""
    rs = _rows(snap, ARM)
    n = 0
    for r in rs:
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] = 100
            n += 1
    _write_rows(snap, ARM, rs)
    return f"{n} candidate counts -> 100"


def mut_B(snap):
    """one raw count +1."""
    rs = _rows(snap, ARM)
    for r in rs:
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] += 1
            break
    _write_rows(snap, ARM, rs)
    return "one raw count +1"


def mut_C(snap):
    """candidate arm x1.09 -- moves the verdict."""
    rs = _rows(snap, ARM)
    n = 0
    for r in rs:
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] = int(round(r["two_q"] * 1.09))
            n += 1
    _write_rows(snap, ARM, rs)
    return f"{n} candidate counts x1.09"


def mut_D(snap):
    """derived summary only: one point risk -> 0.999999."""
    p = os.path.join(snap, SUMMARY)
    lines = open(p, encoding="utf-8").read().splitlines()
    i = lines[0].split(",").index("error_rate")
    row = lines[1].split(",")
    row[i] = "0.999999"
    lines[1] = ",".join(row)
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return "one saved point risk -> 0.999999"


def mut_E(snap):
    """visible >=5% literal 7 -> 9."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    t2 = t.replace("| risk ≥ 5% | 7 / 26 |", "| risk ≥ 5% | 9 / 26 |", 1)
    if t2 == t:
        raise SystemExit("E: target row not found")
    open(p, "w", encoding="utf-8").write(t2)
    return "visible >=5% literal 7 -> 9"


def mut_F(snap):
    """ASTRA F: change one raw observation, then regenerate the local manifest."""
    p = "results/raw/prereg/multiplier_n45_heavy-hex_q200.jsonl"
    rs = _rows(snap, p)
    n = 0
    for r in rs:
        if r.get("record") != "env" and r.get("two_q") == 7315 and not n:
            r["two_q"] = 7316
            n = 1
    _write_rows(snap, p, rs)
    subprocess.run([PY, "raw_integrity.py", "--write"], cwd=snap, capture_output=True)
    return "multiplier_n45 7315 -> 7316, local manifest regenerated"


def mut_H(snap):
    """ASTRA H: all saved risk intervals -> [0.900000, 0.999999]."""
    p = os.path.join(snap, SUMMARY)
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    cols = list(rows[0].keys())
    n = 0
    for r in rows:
        if r.get("error_ci_lo") not in ("", None):
            r["error_ci_lo"], r["error_ci_hi"] = "0.900000", "0.999999"
            n += 1
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return f"all {n} saved risk intervals -> [0.900000, 0.999999]"


def mut_K(snap):
    """ASTRA K: visible table falsified, correct rows hidden in an HTML comment."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    real = ("| risk > 0 (pre-registered endpoint) | 12 / 26 | 46.2% | [28.8, 64.5] |\n"
            "| risk ≥ 5% | 7 / 26 | 26.9% | [13.7, 46.1] |\n"
            "| risk ≥ 10% | 4 / 26 | 15.4% | [6.2, 33.5] |")
    fake = ("| risk > 0 (pre-registered endpoint) | 0 / 26 | 0.0% | [0.0, 0.0] |\n"
            "| risk ≥ 5% | 0 / 26 | 0.0% | [0.0, 0.0] |\n"
            "| risk ≥ 10% | 0 / 26 | 0.0% | [0.0, 0.0] |")
    if real not in t:
        raise SystemExit("K: canonical table not found verbatim")
    t = t.replace(real, fake + "\n\n<!--\n" + real + "\n-->", 1)
    open(p, "w", encoding="utf-8").write(t)
    return "visible table -> 0/26; correct rows hidden in an HTML comment"


def mut_L(snap):
    """a SECOND visible endpoint table -- which one is the claim?"""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    dup = ("\n\n| criterion | circuits | proportion | Wilson 95% CI |\n"
           "|---|---:|---:|---|\n"
           "| risk > 0 (pre-registered endpoint) | 3 / 26 | 11.5% | [4.0, 29.0] |\n"
           "| risk ≥ 5% | 2 / 26 | 7.7% | [2.1, 24.1] |\n"
           "| risk ≥ 10% | 1 / 26 | 3.8% | [0.7, 18.9] |\n")
    open(p, "w", encoding="utf-8").write(t + dup)
    return "a second, contradicting visible endpoint table appended"


def mut_M(snap):
    """wrong DENOMINATOR only -- numerators all correct."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    t2 = t.replace("| risk > 0 (pre-registered endpoint) | 12 / 26 |",
                   "| risk > 0 (pre-registered endpoint) | 12 / 39 |", 1)
    if t2 == t:
        raise SystemExit("M: target row not found")
    open(p, "w", encoding="utf-8").write(t2)
    return "denominator 26 -> 39 on the primary row"


def mut_N(snap):
    """attacker also regenerates the obvious derived file."""
    rs = _rows(snap, ARM)
    for r in rs:
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] += 1
            break
    _write_rows(snap, ARM, rs)
    subprocess.run([PY, "raw_integrity.py", "--write"], cwd=snap, capture_output=True)
    return "one raw count +1, and the manifest regenerated to match"


MUTATIONS = [
    ("A", "whole raw arm -> constant", mut_A, {"science", "integrity", "anchor"}),
    ("B", "one raw count +1", mut_B, {"integrity", "anchor"}),
    ("C", "raw x1.09, verdict moves", mut_C, {"science", "integrity", "anchor"}),
    ("D", "derived summary point risk", mut_D, {"derived"}),
    ("E", "visible literal 7 -> 9", mut_E, {"science", "rendered"}),
    ("F", "ASTRA: raw + manifest regenerated", mut_F, {"anchor"}),
    ("H", "ASTRA: all saved intervals faked", mut_H, {"derived"}),
    ("K", "ASTRA: false visible table, correct rows hidden", mut_K, {"rendered"}),
    ("L", "second contradicting visible table", mut_L, {"rendered"}),
    ("M", "wrong denominator only", mut_M, {"rendered"}),
    ("N", "raw + manifest regenerated together", mut_N, {"anchor"}),
]
DEFEATED_V3 = {"F", "H", "K"}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="only F, H, K")
    ap.add_argument("--only", help="a single mutation id")
    args = ap.parse_args()

    muts = MUTATIONS
    if args.only:
        muts = [m for m in MUTATIONS if m[0] == args.only.upper()]
    elif args.quick:
        muts = [m for m in MUTATIONS if m[0] in DEFEATED_V3]

    base = tempfile.mkdtemp(prefix="qval-mutation-")
    if os.path.realpath(base).startswith(os.path.realpath(ROOT)):
        raise SystemExit("refusing: temp path is inside the repository")

    results, failures = [], []
    order = ["science", "integrity", "anchor", "derived", "rendered"]
    try:
        print(f"\n  scratch: {base}")
        print("  the repository is never written to by this script\n")

        snap = os.path.join(base, "pristine")
        os.makedirs(snap)
        snapshot(snap)
        ctrl = {n: run(snap, LAYERS[n])[0] for n in order}
        print("  CONTROL  " + "  ".join(
            f"{n}={'PASS' if c == 0 else 'FAIL'}" for n, c in ctrl.items()))
        if any(ctrl.values()):
            failures.append("control: a pristine snapshot did not pass every layer")

        hdr = f"\n  {'id':<4}{'mutation':<44}" + "".join(f"{n:<11}" for n in order)
        print(hdr)
        for mid, label, fn, must in muts:
            snap = os.path.join(base, f"m{mid}")
            os.makedirs(snap)
            snapshot(snap)
            what = fn(snap)
            codes = {}
            for n in order:
                if n in SLOW and n not in must:
                    codes[n] = None          # not run; see SLOW
                else:
                    codes[n] = run(snap, LAYERS[n])[0]
            caught = {n for n, c in codes.items() if c}
            star = " *" if mid in DEFEATED_V3 else ""
            cell = lambda c: "—" if c is None else ("FAIL" if c else "pass")
            print(f"  {mid:<4}{(label + star)[:42]:<44}" +
                  "".join(f"{cell(codes[n]):<11}" for n in order))
            results.append({"id": mid, "mutation": what, "required": sorted(must),
                            "caught_by": sorted(caught)})
            missed = must - caught
            if missed:
                failures.append(f"{mid}: NOT caught by {', '.join(sorted(missed))}")
            if not caught:
                failures.append(f"{mid}: caught by NOTHING — this corruption would ship")
        print("\n  * defeated v3 with a full 9/9 PASS\n")
        for r in results:
            print(f"    {r['id']}: {r['mutation']}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print()
    if failures:
        print("  ✗ MUTATION TEST FAILED:")
        for f in failures:
            print(f"      {f}")
        sys.exit(1)
    print("  ✓ every mutation is caught by the layer that must catch it, and the")
    print("    pristine snapshot stays green.\n")


if __name__ == "__main__":
    main()
