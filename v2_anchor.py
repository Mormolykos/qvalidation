"""Historical evidence identity, anchored to v2's git objects — not to a file beside them.

WHY (Astra A03)
    v3 hashed the raw evidence into `results/raw/RAW_MANIFEST.json` and checked the bytes
    against it. Astra changed one observation — `multiplier_n45` seed 663193, 7315 → 7316
    — regenerated the manifest, and the full verifier returned **9/9 PASS**. The exact risk
    for that circuit moved from 0.028724114619 to 0.028726752146; only the coarse headline
    counts were unmoved.

    The defect is not a missing check. It is that a manifest stored beside the evidence
    it describes can never detect a change to both. Self-consistency is not identity, and
    v3 conflated them.

    So there are two different contracts here and they are kept apart:

      SELF-CONSISTENCY  current bytes agree with the current manifest. `raw_integrity.py`.
                        Catches accidental drift. Cannot survive an attacker who updates
                        the manifest, and is not claimed to.
      HISTORICAL        current primary evidence is byte-identical to the evidence
      IDENTITY          published as v2. THIS FILE. The authority is v2's git objects,
                        which no edit to the working tree can alter.

    An attacker who wants to pass this must rewrite git history at
    17e08f3e92533ff8266b1b586e35f20da2923da8 — which changes the commit id, which is
    printed in the failure message and recorded in every published artifact.

CANONICAL BYTES
    Comparison is against the git BLOB, which is LF and platform-independent, so this
    check gives the same answer under core.autocrlf true or false. v3's manifest hashed
    working-tree bytes and would have failed for every verifier on Linux or macOS.

OFFLINE DISTRIBUTION
    A zip archive has no git objects. `--write-anchor` therefore emits
    `results/raw/V2_EVIDENCE_ANCHOR.json` **read out of the v2 commit**, never out of the
    working tree, so the anchor cannot be refreshed to match tampered files by anyone who
    does not also hold the v2 history. The checker prefers git and falls back to the
    anchor, saying which authority it used.

USAGE
    python v2_anchor.py                 # verify current evidence against v2
    python v2_anchor.py --write-anchor  # regenerate the offline anchor FROM v2 objects
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
V2 = "17e08f3e92533ff8266b1b586e35f20da2923da8"
ANCHOR = os.path.join(ROOT, "results", "raw", "V2_EVIDENCE_ANCHOR.json")
PRIMARY = "results/raw/prereg"


def git(*args, binary=False):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout if binary else p.stdout.decode("utf-8", "replace")


def git_available():
    return git("rev-parse", "--git-dir") is not None and git("cat-file", "-e", V2) is not None


def v2_primary_paths():
    out = git("ls-tree", "-r", "--name-only", V2, PRIMARY)
    if out is None:
        return None
    return sorted(p for p in out.split() if p.endswith(".jsonl"))


def canonical_bytes(path):
    """Working-tree bytes normalised to LF, so the comparison is platform-independent.

    A CRLF checkout is a representation difference, not an evidence difference. Astra's
    mutation J changes only line endings; that is reported by raw_integrity.py under its
    byte-preservation contract, and is deliberately NOT treated here as a violation of
    historical identity.
    """
    with open(os.path.join(ROOT, path), "rb") as fh:
        return fh.read().replace(b"\r\n", b"\n")


def write_anchor():
    if not git_available():
        raise SystemExit("refusing: git objects for v2 are not reachable, so an anchor "
                         "written now would not be bound to v2")
    paths = v2_primary_paths()
    files = {}
    for p in paths:
        blob = git("show", f"{V2}:{p}", binary=True)
        if blob is None:
            raise SystemExit(f"cannot read {p} from {V2[:8]}")
        files[p] = {"sha256": hashlib.sha256(blob).hexdigest(), "bytes": len(blob)}
    doc = {
        "_what": "SHA-256 of every primary raw file AS PUBLISHED IN v2, read from git "
                 "objects at the commit below — never from the working tree.",
        "_authority": "The v2 git objects are the authority. This file is a transcript "
                      "for environments without git history (a zip archive). If the two "
                      "ever disagree, git wins and this file is wrong.",
        "_rule": "Regenerating this from current files instead of from v2 would destroy "
                 "the only property it has. --write-anchor reads v2 objects and refuses "
                 "to run without them.",
        "v2_commit": V2,
        "count": len(files),
        "files": files,
    }
    json.dump(doc, open(ANCHOR, "w", encoding="utf-8"), indent=1, sort_keys=True)
    print(f"  wrote {os.path.relpath(ANCHOR, ROOT)}")
    print(f"  {len(files)} primary files, hashed from git objects at {V2[:12]}")


def verify():
    print(f"\n  HISTORICAL EVIDENCE IDENTITY — anchored to v2 {V2[:12]}\n")
    use_git = git_available()
    if use_git:
        want = {p: hashlib.sha256(git("show", f"{V2}:{p}", binary=True)).hexdigest()
                for p in v2_primary_paths()}
        authority = f"git objects at {V2[:12]}"
    else:
        if not os.path.isfile(ANCHOR):
            return [f"no git history for {V2[:12]} and no {os.path.basename(ANCHOR)}; "
                    f"historical identity cannot be established"]
        doc = json.load(open(ANCHOR, encoding="utf-8"))
        if doc.get("v2_commit") != V2:
            return [f"anchor names commit {doc.get('v2_commit')}, expected {V2}"]
        want = {p: e["sha256"] for p, e in doc["files"].items()}
        authority = f"offline anchor bound to {V2[:12]} (no git history available)"
    print(f"  authority: {authority}")

    fails = []
    # recursive: results/raw/prereg/_scatter_parts holds the per-process fragments the
    # merged arms were built from, and they are primary evidence too -- 858 files in all,
    # not the 78 merged arms alone.
    here = []
    for root, _, files in os.walk(os.path.join(ROOT, PRIMARY)):
        for f in files:
            if f.endswith(".jsonl"):
                here.append(os.path.relpath(os.path.join(root, f), ROOT)
                            .replace("\\", "/"))
    here.sort()
    for p in sorted(set(want) | set(here)):
        if p not in here:
            fails.append(f"{p}: published in v2, MISSING now")
            continue
        if p not in want:
            fails.append(f"{p}: present now, NOT published in v2 — primary evidence "
                         f"may only be added by a documented new measurement")
            continue
        got = hashlib.sha256(canonical_bytes(p)).hexdigest()
        if got != want[p]:
            fails.append(
                f"{p}: TRUSTED HISTORICAL EVIDENCE ANCHOR VIOLATED — canonical content "
                f"differs from the bytes published in v2 ({V2[:12]}). "
                f"now {got[:16]}…, v2 {want[p][:16]}…. This is not a manifest mismatch: "
                f"the primary evidence itself is not the evidence the published result "
                f"was computed from.")
    print(f"  {len(here)} primary files compared against v2")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write-anchor", action="store_true")
    args = ap.parse_args()
    if args.write_anchor:
        write_anchor()
        return
    fails = verify()
    if fails:
        print(f"\n  ✗ {len(fails)} violation(s):\n")
        for f in fails[:30]:
            print(f"      {f}")
        if len(fails) > 30:
            print(f"      … and {len(fails) - 30} more")
        print()
        sys.exit(1)
    print("\n  ✓ primary evidence is byte-identical to v2 as published.\n")


if __name__ == "__main__":
    main()
