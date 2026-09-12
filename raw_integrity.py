"""Two things the scientific chain cannot do on its own.

WHY THIS IS SEPARATE FROM raw_endpoint.py
    `raw_endpoint.py` asks "does the manuscript state what the raw data produces?". That
    is the right primary question, and it catches corruption that changes the result.

    It does not catch two other things, and the mutation test proved it:

      B  One raw gate count changed by +1. The endpoint counts are coarse integers, so
         the science genuinely does not move -- and the raw chain correctly passes. But
         then NOTHING notices that the evidence was edited.
      D  The derived summary CSV corrupted while the raw data is pristine. The raw chain
         is indifferent to the summary by design, and the old chain trusted it. Nothing
         noticed at all.

    So this file adds the two layers that close those, and keeps them clearly subordinate
    to the scientific reconstruction:

      INTEGRITY  every raw primary file must hash to its committed manifest entry.
                 Any edit at all is a finding, whether or not it changes a number.
      CONSISTENCY the derived summary must be reproducible FROM the raw data. The
                 summary is checked as an OUTPUT of the raw chain, never as a source of
                 truth for it -- that inversion is what the audit broke.

    An integrity manifest alone would be security theatre: it proves bytes are unchanged
    since someone wrote the manifest, and nothing about whether the science is right.
    It is useful only underneath a reconstruction that checks the science.

USAGE
    python raw_integrity.py --write     # regenerate the manifest (deliberate act)
    python raw_integrity.py             # verify integrity + derived consistency
"""

import argparse
import csv
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

RAW_DIR = os.path.join(ROOT, "results", "raw", "prereg")
MANIFEST = os.path.join(ROOT, "results", "raw", "RAW_MANIFEST.json")
SUMMARY = os.path.join(ROOT, "results", "summary", "prereg_heavy-hex.csv")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def raw_files():
    out = []
    for f in sorted(os.listdir(RAW_DIR)):
        p = os.path.join(RAW_DIR, f)
        if os.path.isfile(p) and f.endswith(".jsonl"):
            out.append(f)
    return out


def write_manifest():
    entries = {f: {"sha256": sha256(os.path.join(RAW_DIR, f)),
                   "bytes": os.path.getsize(os.path.join(RAW_DIR, f))}
               for f in raw_files()}
    doc = {
        "_what": "SHA-256 of every raw primary arm file for the pre-registered study.",
        "_rule": ("These files are EVIDENCE. They are never edited. Regenerating this "
                  "manifest is a deliberate act that must accompany a commit explaining "
                  "why the evidence changed -- not a routine step to make a check pass."),
        "_scope": ("Integrity only. This says the bytes are unchanged; it says nothing "
                   "about whether the analysis of them is correct. raw_endpoint.py is "
                   "what checks the science."),
        "count": len(entries),
        "files": entries,
    }
    json.dump(doc, open(MANIFEST, "w", encoding="utf-8"), indent=1, sort_keys=True)
    print(f"  wrote {MANIFEST}")
    print(f"  {len(entries)} raw primary files hashed")


def check_integrity():
    fails = []
    if not os.path.isfile(MANIFEST):
        return ["no RAW_MANIFEST.json -- run --write once and commit it"]
    doc = json.load(open(MANIFEST, encoding="utf-8"))
    want = doc["files"]
    have = set(raw_files())
    for name in sorted(set(want) | have):
        if name not in have:
            fails.append(f"{name}: recorded in the manifest but MISSING from disk")
            continue
        if name not in want:
            fails.append(f"{name}: present on disk but NOT in the manifest")
            continue
        got = sha256(os.path.join(RAW_DIR, name))
        if got != want[name]["sha256"]:
            fails.append(f"{name}: sha256 {got[:16]}... != recorded "
                         f"{want[name]['sha256'][:16]}...  RAW EVIDENCE WAS EDITED")
    print(f"  integrity: {len(have)} raw files checked against the manifest")
    return fails


def check_derived_consistency():
    """The derived summary must agree with a fresh reconstruction FROM RAW.

    Direction matters: raw is the source, the CSV is the output under test. The v2
    apparatus had this backwards and could not see raw corruption at all.
    """
    from raw_endpoint import reconstruct
    circuits = [c.strip() for c in open(os.path.join(ROOT, "_selected.txt"))
                if c.strip()]
    rows = {r["circuit"]: r for r in reconstruct(circuits)}
    fails = []
    n = 0
    for rec in csv.DictReader(open(SUMMARY, encoding="utf-8")):
        c = rec["circuit"]
        live = rows.get(c)
        if live is None:
            fails.append(f"{c}: in the summary but not reconstructible from raw")
            continue
        if rec["status"] != live.get("status"):
            fails.append(f"{c}: status {rec['status']} != raw {live.get('status')}")
            continue
        if live.get("status") != "OK":
            continue
        n += 1
        if rec["verdict"] != live["verdict"]:
            fails.append(f"{c}: verdict {rec['verdict']} != raw {live['verdict']}")
        if rec["error_rate"] not in ("", None) and live["risk"] is not None:
            got, want = float(rec["error_rate"]), live["risk"]
            if abs(got - want) > 5e-6:
                fails.append(f"{c}: summary risk {got:.6f} != raw-reconstructed "
                             f"{want:.6f}")
        theta = float(rec["est_long_run_change_pct"])
        if abs(theta - live["theta_pct"]) > 5e-4:
            fails.append(f"{c}: summary theta {theta} != raw {live['theta_pct']:.4f}")
    print(f"  consistency: {n} summary rows regenerated from raw and compared")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="regenerate the manifest -- a deliberate act, see _rule")
    ap.add_argument("--integrity-only", action="store_true")
    args = ap.parse_args()

    if args.write:
        write_manifest()
        return

    print("\n  RAW EVIDENCE INTEGRITY AND DERIVED CONSISTENCY\n")
    fails = check_integrity()
    if not args.integrity_only:
        fails += check_derived_consistency()

    if fails:
        print(f"\n  ✗ {len(fails)} problem(s):\n")
        for f in fails[:40]:
            print(f"      {f}")
        if len(fails) > 40:
            print(f"      ... and {len(fails) - 40} more")
        print()
        sys.exit(1)
    print("\n  ✓ raw evidence unedited, and the derived summary is reproducible "
          "from it.\n")


if __name__ == "__main__":
    main()
