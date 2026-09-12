"""Prove the verifier can turn RED. A verifier that only ever agrees is worthless.

WHAT THIS IS
    The hostile audit of v2 (audits/2026-09-12-hostile/) found that corrupting a raw
    primary arm file changed the scientific result while `verify.py` still reported
    6/6 PASS. The audit's attack is preserved here verbatim as attack A, and four more
    mutations are added at different layers so it is recorded WHICH layer catches WHICH
    corruption -- and where a layer is still blind.

    Every mutation runs in a throwaway `git archive` snapshot in the system temp
    directory. **No file in this repository is ever modified by this script.** It refuses
    to run if the snapshot path resolves inside the repository.

REQUIRED BEHAVIOUR
    pristine snapshot  -> the raw chain PASSES
    mutated raw data   -> the raw chain FAILS, and fails because the reconstructed
                          science differs, not because a file hash moved

USAGE
    python mutation_test.py              # all mutations
    python mutation_test.py --quick      # attack A only (the audit's own)
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
ARM = "results/raw/prereg/knn_n67_heavy-hex_q200.jsonl"


def snapshot(dst):
    """git archive HEAD -> dst. Working-tree state is deliberately not used."""
    tar = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, capture_output=True)
    if tar.returncode != 0:
        raise SystemExit("git archive failed: " + tar.stderr.decode()[:300])
    p = subprocess.run(["tar", "-x", "-C", dst], input=tar.stdout, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("tar extract failed: " + p.stderr.decode()[:300])


def run(snap, script, *args):
    env = dict(os.environ)
    env.setdefault("BENCHPRESS_PATH", r"C:\Users\User\Desktop\benchpress_test")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    p = subprocess.run([PY, script, *args], cwd=snap, capture_output=True, text=True,
                       env=env, timeout=3600)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# --- the mutations ------------------------------------------------------------------

def mutate_raw_constant(snap):
    """A -- THE AUDIT'S OWN ATTACK (T7). Every candidate gate count in one arm -> 100.

    Changes that circuit's true long-run change to about -82.7% and its true risk to 0,
    moving the endpoint 12/26 -> 11/26, 7/26 -> 6/26, 4/26 -> 3/26. All derived
    summaries are left exactly as they are: that is the whole point of the attack."""
    p = os.path.join(snap, ARM)
    out, n = [], 0
    for line in open(p, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] = 100
            n += 1
        out.append(json.dumps(r))
    open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return f"{n} candidate gate counts -> constant 100 in {os.path.basename(ARM)}"


def mutate_raw_single(snap):
    """B -- ONE raw gate count, by one gate. The smallest possible corruption."""
    p = os.path.join(snap, ARM)
    lines = open(p, encoding="utf-8").read().splitlines()
    n = 0
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] = int(r["two_q"]) + 1
            lines[i] = json.dumps(r)
            n = 1
            break
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return f"one raw gate count incremented by 1 ({n} row)"


def mutate_eligibility(snap):
    """C -- push a circuit across the 3pp boundary rule by scaling one arm.

    Targets classification rather than a headline number: if only the endpoint literal
    is checked, a change to WHICH circuits are eligible can still slip through."""
    p = os.path.join(snap, ARM)
    out, n = [], 0
    for line in open(p, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] = int(round(int(r["two_q"]) * 1.09))
            n += 1
        out.append(json.dumps(r))
    open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
    return f"{n} candidate counts scaled by 1.09 (moves theta toward the threshold)"


def mutate_derived_only(snap):
    """D -- corrupt ONLY the derived summary, leaving raw pristine.

    The mirror image of A. The raw chain should be INDIFFERENT to this, because it never
    reads the summary; a derived-artifact check is what must catch it."""
    p = os.path.join(snap, "results/summary/prereg_heavy-hex.csv")
    lines = open(p, encoding="utf-8").read().splitlines()
    hdr = lines[0].split(",")
    i = hdr.index("error_rate")
    row = lines[1].split(",")
    row[i] = "0.999999"
    lines[1] = ",".join(row)
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return "one error_rate in the derived summary CSV -> 0.999999 (raw untouched)"


def mutate_paper_literal(snap):
    """E -- change a quantitative literal in PAPER.md, leaving all data pristine."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    t2 = t.replace("| risk ≥ 5% | 7 / 26 |", "| risk ≥ 5% | 9 / 26 |", 1)
    if t2 == t:
        raise SystemExit("mutation E could not find the table row it targets")
    open(p, "w", encoding="utf-8").write(t2)
    return "PAPER.md results table: risk >= 5% literal 7 -> 9 (data pristine)"


MUTATIONS = [
    ("A", "audit T7: whole raw arm -> constant", mutate_raw_constant, "RAW"),
    ("B", "one raw gate count +1", mutate_raw_single, "RAW"),
    ("C", "raw scaled, moves eligibility", mutate_eligibility, "RAW"),
    ("D", "derived summary only", mutate_derived_only, "DERIVED"),
    ("E", "PAPER.md literal only", mutate_paper_literal, "PAPER"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="run attack A only")
    args = ap.parse_args()

    muts = MUTATIONS[:1] if args.quick else MUTATIONS
    results, failures = [], []

    base = tempfile.mkdtemp(prefix="qval-mutation-")
    if os.path.commonpath([os.path.realpath(base), os.path.realpath(ROOT)]) == \
            os.path.realpath(ROOT):
        raise SystemExit("refusing to run: temp path is inside the repository")

    try:
        print(f"\n  scratch root: {base}")
        print("  the repository itself is never written to by this script\n")

        # --- control: pristine snapshot must PASS -----------------------------------
        snap = os.path.join(base, "pristine")
        os.makedirs(snap)
        snapshot(snap)
        code, out = run(snap, "raw_endpoint.py")
        ctrl_ok = code == 0
        print(f"  CONTROL  pristine snapshot -> raw chain "
              f"{'PASS' if ctrl_ok else 'FAIL'} (exit {code})")
        if not ctrl_ok:
            failures.append("control: pristine snapshot did not pass the raw chain")
            print(out[-1500:])

        # --- mutations ----------------------------------------------------------------
        print(f"\n  {'id':<3}{'layer':<9}{'mutation':<44}{'raw chain':<12}"
              f"{'old chain':<12}")
        for mid, label, fn, layer in muts:
            snap = os.path.join(base, f"mut{mid}")
            os.makedirs(snap)
            snapshot(snap)
            what = fn(snap)
            raw_code, raw_out = run(snap, "raw_endpoint.py")
            old_code, _ = run(snap, "paper_check.py")
            raw_v = "FAIL" if raw_code else "pass"
            old_v = "FAIL" if old_code else "pass"
            print(f"  {mid:<3}{layer:<9}{label:<44}{raw_v:<12}{old_v:<12}")
            results.append({"id": mid, "layer": layer, "mutation": what,
                            "raw_chain": raw_v, "old_chain": old_v})
            # required: every RAW mutation must be caught by the raw chain
            if layer == "RAW" and raw_code == 0:
                failures.append(f"{mid}: raw corruption NOT caught by the raw chain")
            if layer == "RAW" and raw_code != 0 and "disagree" not in raw_out.lower():
                failures.append(f"{mid}: raw chain failed, but not for a scientific "
                                f"reason -- check the message")
        print()
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
    print("  ✓ every raw-data corruption turns the raw chain RED, and the pristine")
    print("    snapshot stays green. The verifier has been shown to reject us.\n")


if __name__ == "__main__":
    main()
