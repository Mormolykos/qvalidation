"""Toolchain pin, checked on canonical bytes so it means the same on every platform.

WHY (Astra A14)
    `results/raw/benchpress_pin.json` records SHA-256 of five Benchpress modules as read
    from the WORKING TREE. On the authoring machine `core.autocrlf` is true, so those are
    CRLF bytes. On a normal LF checkout every one of them differs — measured, not
    assumed: **0 of 5 match**. Stage 1 was guaranteed to fail for every replicator on
    Linux or macOS while passing for its author.

    Same defect as the raw-evidence manifest and the preserved audit files: a hash taken
    over a checkout representation is a statement about one machine, not about content.

CONTRACT
    Compare canonical bytes — git's stored blob where history is available, otherwise the
    working tree normalised to LF. `results/raw/benchpress_pin_canonical.json` holds the
    reference, generated from git objects at the pinned commit.

    The historical `benchpress_pin.json` is NOT rewritten. It is what v1–v3 recorded and
    stays as evidence of what was actually pinned at the time; this file supersedes the
    contract without editing the record.

PREREQUISITE: BENCHPRESS_PATH MUST BE A GIT CHECKOUT (Astra V4-10)
    This stage does two different things, and only one of them survives without history:

      the five module hashes      computed over canonical (LF) bytes. `sweep_bp.py`'s
                                  helper reproduces all five from the source files alone,
                                  with or without `.git`. Astra confirmed this.
      the identity of the source  requires git: the live commit, and whether tracked files
                                  have been modified. Without `.git` the commit reads as
                                  None and this stage FAILS — correctly, because five
                                  matching hashes do not say which revision they came
                                  from, only that five files have the expected content.

    So: stage 1 requires a Benchpress *git checkout* at the pinned commit, not a copy of
    the files. The no-history hashing is a helper capability, not a weaker mode of this
    stage, and there is deliberately no flag to make it one — an archive mode that
    reported PASS on unattributable source would be the same conflation this repository
    has already had to repair in `v2_anchor.py`.

    Astra measured both: clean pinned sparse checkouts pass under LF *and* CRLF; the
    historyless copies reproduce 5/5 hashes and still exit 1 here.

USAGE
    python pin_check.py
    python pin_check.py --write   # regenerate the canonical reference from git objects
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from sweep_bp import benchpress_canonical_pin, benchpress_pin, PINNED_MODULES

CANON = os.path.join(ROOT, "results", "raw", "benchpress_pin_canonical.json")
HISTORIC = os.path.join(ROOT, "results", "raw", "benchpress_pin.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    want_commit = json.load(open(HISTORIC, encoding="utf-8"))["benchpress_commit"]

    if args.write:
        doc = benchpress_canonical_pin(want_commit)
        doc["_what"] = ("SHA-256 of the five pinned Benchpress modules over CANONICAL "
                        "(LF) bytes, resolved from git objects at the commit below.")
        doc["_why"] = ("benchpress_pin.json hashes the working tree, which is CRLF on a "
                       "Windows checkout: 0 of 5 of those hashes match on an LF "
                       "checkout. This file is the portable contract; that one is "
                       "preserved as the historical record and is not rewritten.")
        json.dump(doc, open(CANON, "w", encoding="utf-8"), indent=1, sort_keys=True)
        print(f"  wrote {os.path.relpath(CANON, ROOT)} from {doc['source']}")
        return

    print("\n  TOOLCHAIN PIN — canonical bytes\n")
    if not os.path.isfile(CANON):
        sys.exit("  no benchpress_pin_canonical.json; run --write once and commit it")
    want = json.load(open(CANON, encoding="utf-8"))
    got = benchpress_canonical_pin(want_commit)
    live = benchpress_pin()

    fails = []
    if live["benchpress_commit"] is None:
        fails.append(
            "BENCHPRESS_PATH has no git history, so the revision of this source cannot "
            "be established. The five canonical hashes may still match — that says the "
            "FILES have the expected content, not which commit they came from. Stage 1 "
            "requires a git checkout at " + want_commit[:12] + "; see this file's header.")
    elif live["benchpress_commit"] != want_commit:
        fails.append(f"commit {live['benchpress_commit']} != pinned {want_commit}")
    if live["benchpress_dirty"]:
        fails.append("the Benchpress checkout has modified tracked files")

    w = want["benchpress_module_canonical_sha256"]
    g = got["benchpress_module_canonical_sha256"]
    for m in PINNED_MODULES:
        if g.get(m) != w.get(m):
            fails.append(f"{m}: canonical {str(g.get(m))[:16]}… != "
                         f"pinned {str(w.get(m))[:16]}…")
    print(f"  commit {want_commit[:12]} | {len(PINNED_MODULES)} modules | "
          f"source: {got['source']}")

    # informational: how many would have matched under the old working-tree contract
    old = live["benchpress_module_sha256"]
    crlf_equal = sum(1 for m in PINNED_MODULES if old.get(m) == g.get(m))
    print(f"  working-tree hashes equal to canonical here: {crlf_equal}/"
          f"{len(PINNED_MODULES)} "
          f"({'LF checkout' if crlf_equal == len(PINNED_MODULES) else 'CRLF checkout'})"
          f" — the canonical check is unaffected either way")

    if fails:
        print(f"\n  ✗ {len(fails)} problem(s):\n")
        for f in fails:
            print(f"      {f}")
        print()
        sys.exit(1)
    print("\n  ✓ toolchain pin holds on canonical bytes.\n")


if __name__ == "__main__":
    main()
