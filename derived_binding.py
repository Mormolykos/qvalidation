"""Every saved primary field, bound to a replay of the analysis that produced it.

WHY (Astra A01)
    v3 reconstructed the endpoint from raw and compared the counts. It never compared the
    saved *uncertainty*. Astra replaced all 36 saved risk intervals with
    [0.900000, 0.999999], left every flag and count untouched, and the full verifier
    returned **9/9 PASS**.

    The published intervals are load-bearing: the primary endpoint is "risk interval
    excludes zero". A file whose intervals are fiction, whose counts are correct, and
    which passes every check, is worse than no file.

CONTRACT A — replay the original stream, do not substitute a better one
    The saved intervals came from the original Monte-Carlo bootstrap: 400 seed resamples,
    400,000-pair inner MC, `np.random.default_rng(20260905)`. Astra independently
    replayed all 36 and matched them to <= 5e-7.

    So this file replays THAT method — `prereg_analysis.analyse`, same seeds, same budget
    — and compares it to the saved rows field by field.

    It deliberately does NOT compare the saved intervals against `raw_endpoint.py`'s exact
    convolution bootstrap. Those are a different estimator and give slightly different
    endpoints; comparing them would either fail on correct data or need a tolerance wide
    enough to hide the attack. Silently checking historical MC intervals against a
    different stream is the mistake this file exists to avoid.

    `raw_endpoint.py` remains the independent scientific check on the HEADLINE. This is
    the binding check on the SAVED ARTIFACT. Different jobs; neither substitutes.

COST
    A full replay is about four minutes. That is the price of checking the numbers rather
    than a summary of them.

USAGE
    python derived_binding.py            # replay and bind every field
    python derived_binding.py --quick    # intervals and endpoint fields only
"""

import argparse
import csv
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import prereg_analysis as pa

SUMMARY = os.path.join(ROOT, "results", "summary", "prereg_heavy-hex.csv")
SELECTED = os.path.join(ROOT, "_selected.txt")

# field -> (kind, tolerance). Tolerances are the saved rounding, not slack: the CSV stores
# 4 or 6 decimals, so anything looser would let a real change hide inside it.
FIELDS = {
    "status":                   ("str", None),
    "verdict":                  ("str", None),
    "error_kind":               ("str", None),
    "qiskit_baseline":          ("str", None),
    "qiskit_candidate":         ("str", None),
    "boundary":                 ("bool", None),
    "error_excludes_zero":      ("bool", None),
    "n_seeds":                  ("int", None),
    "k":                        ("int", None),
    "threshold":                ("float", 1e-12),
    "est_long_run_change_pct":  ("float", 5e-5),
    "change_ci_lo_pct":         ("float", 5e-5),
    "change_ci_hi_pct":         ("float", 5e-5),
    "distance_to_cut_pp":       ("float", 5e-4),
    "p_call":                   ("float", 5e-7),
    "error_rate":               ("float", 5e-7),
    "error_ci_lo":              ("float", 5e-7),
    "error_ci_hi":              ("float", 5e-7),
}
QUICK = {"error_ci_lo", "error_ci_hi", "error_rate", "error_excludes_zero",
         "verdict", "boundary", "status"}


def coerce(kind, raw):
    if raw in ("", None):
        return None
    if kind == "str":
        return str(raw)
    if kind == "bool":
        return str(raw).strip().lower() in ("true", "1", "yes")
    if kind == "int":
        return int(float(raw))
    return float(raw)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    fields = {k: v for k, v in FIELDS.items() if not args.quick or k in QUICK}

    circuits = [c.strip() for c in open(SELECTED) if c.strip()]
    saved = {r["circuit"]: r for r in csv.DictReader(open(SUMMARY, encoding="utf-8"))}

    print(f"\n  SAVED SUMMARY BOUND TO A REPLAY OF ITS OWN ANALYSIS")
    print(f"  replaying prereg_analysis.analyse for {len(circuits)} circuits "
          f"(original MC bootstrap, original seeds)\n")

    fails, checked = [], 0

    # row membership, before any value is compared
    missing = [c for c in circuits if c not in saved]
    extra = [c for c in saved if c not in circuits]
    for c in missing:
        fails.append(f"{c}: in the frozen selection, ABSENT from the saved summary")
    for c in extra:
        fails.append(f"{c}: in the saved summary, NOT in the frozen selection")
    if len(saved) != len(circuits):
        fails.append(f"row count {len(saved)} != frozen selection {len(circuits)}")

    rng = np.random.default_rng(20260906)
    for c in circuits:
        if c not in saved:
            continue
        live = pa.analyse(c, 0.10, 3, rng)
        row = saved[c]
        for f, (kind, tol) in fields.items():
            if f not in row:
                fails.append(f"{c}: saved summary has no column '{f}'")
                continue
            want = live.get(f)
            got = coerce(kind, row[f])
            if want is None and got is None:
                continue
            if want is None or got is None:
                fails.append(f"{c}.{f}: saved {row[f]!r}, replay {want!r}")
                continue
            checked += 1
            if kind in ("str", "bool", "int"):
                if got != (want if kind != "bool" else bool(want)):
                    fails.append(f"{c}.{f}: saved {got!r} != replay {want!r}")
            else:
                if abs(float(got) - float(want)) > tol:
                    fails.append(f"{c}.{f}: saved {got!r} != replay {float(want):.10g} "
                                 f"(|diff| {abs(float(got)-float(want)):.3g} > {tol:g})")

    print(f"  {checked} saved values compared against the replay")
    if fails:
        iv = [f for f in fails if ".error_ci_" in f]
        print(f"\n  ✗ SAVED SUMMARY DOES NOT MATCH ITS OWN ANALYSIS — "
              f"{len(fails)} mismatch(es)")
        if iv:
            print(f"\n  RISK INTERVAL MISMATCH on {len(iv)} field(s). The published "
                  f"uncertainty is\n  not the uncertainty this data produces.")
        print()
        for f in fails[:30]:
            print(f"      {f}")
        if len(fails) > 30:
            print(f"      … and {len(fails) - 30} more")
        print()
        sys.exit(1)
    print("\n  ✓ every saved primary field reproduces from a replay of its own "
          "analysis.\n")


if __name__ == "__main__":
    main()
