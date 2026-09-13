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

OFFLINE DISTRIBUTION — AND WHAT IT DOES *NOT* ESTABLISH (Astra V4-06)
    A zip archive has no git objects. `--write-anchor` therefore emits
    `results/raw/V2_EVIDENCE_ANCHOR.json` **read out of the v2 commit**, never out of the
    working tree, so the anchor cannot be refreshed to match tampered files by anyone who
    does not also hold the v2 history. The checker prefers git and falls back to the
    anchor, saying which authority it used.

    That fallback is a WEAKER contract, and this file used to report it in the same words
    as the strong one. It is not:

      WITH v2 HISTORY   the evidence is compared to objects an edit to the working tree
                        cannot reach. Changing the data means rewriting history at
                        17e08f3e, which changes the commit id printed in every published
                        artifact. This IS historical identity.
      WITHOUT IT        the evidence is compared to a JSON file shipped beside it, whose
                        only claim to authority is a commit id it writes about itself.
                        Someone who changes both is not detected, and CANNOT be: a
                        transcript travelling with the data it describes authenticates
                        nothing. This is agreement with a supplied transcript, and the
                        success message now says exactly that.

    Astra confirmed the current transcript is correct against the real v2 objects and
    recorded its SHA-256 as cc31e9b2f43d9a4ca6332e0e300e7f0c391c59c17dfe32804269800446ab9827
    in `audits/2026-09-13-astra-v4/`. That hash is an EXTERNAL binding, published by a
    third party, and it is the kind of thing the offline mode would need. This file does
    not contain it, because a reference stored next to the transcript it authenticates
    would have precisely the defect described above.

CANONICAL CONTENT, NOT BYTES
    The comparison is on LF-normalised content, so it is portable across checkout
    policies. That means it establishes canonical-content identity, not byte identity of
    an arbitrary checkout, and the success message says "canonical content".

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
# Everything under here is anchored. NOTE the composition, because calling all of it
# "primary measurements" would overstate it: 78 merged arm files ARE the primary
# measurements the reconstruction opens (39 circuits x 2 arms), and 780 are the
# per-process fragments those 78 were merged from (x 10 processes) -- the same
# observations before merge, not additional ones.
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
    n_arm_w = sum(1 for k in files if "_scatter_parts" not in k)
    doc = {
        "_what": f"SHA-256 of every anchored raw evidence file AS PUBLISHED IN v2, read "
                 f"from git objects at the commit below — never from the working tree. "
                 f"{n_arm_w} of these are primary measurement arms (39 circuits x 2) and "
                 f"{len(files) - n_arm_w} are the per-process fragments those were merged "
                 f"from: the same observations before merge, NOT additional measurements.",
        "_authority": "The v2 git objects are the authority. This file is a transcript "
                      "for environments without git history (a zip archive). If the two "
                      "ever disagree, git wins and this file is wrong.",
        "_not_authenticated_by_itself": "Checking evidence against this file establishes "
                                        "agreement with THIS FILE, not historical "
                                        "authenticity. A transcript shipped beside the "
                                        "data it describes cannot authenticate it; that "
                                        "needs the v2 objects, or an externally "
                                        "published hash of this transcript.",
        "_rule": "Regenerating this from current files instead of from v2 would destroy "
                 "the only property it has. --write-anchor reads v2 objects and refuses "
                 "to run without them.",
        "v2_commit": V2,
        "count": len(files),
        "files": files,
    }
    json.dump(doc, open(ANCHOR, "w", encoding="utf-8"), indent=1, sort_keys=True)
    print(f"  wrote {os.path.relpath(ANCHOR, ROOT)}")
    n_arm = sum(1 for k in files if "_scatter_parts" not in k)
    print(f"  {len(files)} anchored files ({n_arm} primary measurement arms + "
          f"{len(files) - n_arm} fragments), hashed from git objects at {V2[:12]}")


def verify():
    print(f"\n  HISTORICAL EVIDENCE IDENTITY — anchored to v2 {V2[:12]}\n")
    use_git = git_available()
    if use_git:
        want = {p: hashlib.sha256(git("show", f"{V2}:{p}", binary=True)).hexdigest()
                for p in v2_primary_paths()}
        authority = f"git objects at {V2[:12]}"
    else:
        if not os.path.isfile(ANCHOR):
            return ([f"no git history for {V2[:12]} and no {os.path.basename(ANCHOR)}; "
                     f"historical identity cannot be established"], False)
        doc = json.load(open(ANCHOR, encoding="utf-8"))
        if doc.get("v2_commit") != V2:
            return ([f"anchor names commit {doc.get('v2_commit')}, expected {V2}"], False)
        want = {p: e["sha256"] for p, e in doc["files"].items()}
        authority = (f"the SUPPLIED TRANSCRIPT {os.path.basename(ANCHOR)}, which names "
                     f"commit {V2[:12]} — no git history is available here, so this "
                     f"run establishes agreement with that transcript and NOT the "
                     f"historical authenticity of the evidence")
    print(f"  authority: {authority}")

    fails = []
    # recursive: results/raw/prereg/_scatter_parts holds the per-process fragments the
    # merged arms were built from. Both are anchored, but they are NOT the same thing:
    # 78 merged arms are the primary measurements the reconstruction opens; the 780
    # fragments are those same observations before merge, not additional ones.
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
    n_arm = sum(1 for x in here if "_scatter_parts" not in x)
    n_frag = len(here) - n_arm
    print(f"  {len(here)} anchored evidence files compared against v2")
    print(f"    = {n_arm} primary measurement arms (39 circuits x 2) "
          f"+ {n_frag} per-process fragments they were merged from")
    return fails, use_git


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write-anchor", action="store_true")
    args = ap.parse_args()
    if args.write_anchor:
        write_anchor()
        return
    fails, use_git = verify()
    if fails:
        print(f"\n  ✗ {len(fails)} violation(s):\n")
        for f in fails[:30]:
            print(f"      {f}")
        if len(fails) > 30:
            print(f"      … and {len(fails) - 30} more")
        print()
        sys.exit(1)
    # Two different statements, because two different things were checked (Astra V4-06).
    if use_git:
        print("\n  ✓ HISTORICAL IDENTITY: the canonical content of the primary evidence "
              "is\n    identical to the objects committed at v2. Establishing this "
              "falsely would\n    require rewriting history at "
              f"{V2[:12]}, which changes the commit id.\n")
    else:
        print("\n  ✓ the primary evidence matches the supplied transcript "
              f"{os.path.basename(ANCHOR)}.\n"
              "    HISTORICAL AUTHENTICITY IS NOT ESTABLISHED HERE. A transcript "
              "distributed\n    beside the data it describes cannot authenticate it: "
              "anyone who changed\n    both would pass this check. To establish "
              "identity, run this where the v2\n    git objects are reachable, or "
              "compare the transcript against an externally\n    published hash of it.\n")


if __name__ == "__main__":
    main()
