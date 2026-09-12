"""Reconstruct the primary endpoint FROM RAW DATA and bind it to the manuscript.

WHY THIS FILE EXISTS
    A hostile audit of published v2 (audits/2026-09-12-hostile/) demonstrated that the
    verification apparatus did not protect the experiment. Replacing every candidate gate
    count in ONE raw arm file -- results/raw/prereg/knn_n67_heavy-hex_q200.jsonl -- with
    the constant 100 changes that circuit's true long-run change to -82.7% and its true
    risk to zero, which moves the primary endpoint from 12/26 to 11/26 and the >=5% and
    >=10% counts from 7/26 and 4/26 to 6/26 and 3/26.

    `verify.py` still reported 6/6 PASS.

    The reason is structural, not a slip: `paper_check.py:101` reads
    `results/summary/prereg_heavy-hex.csv` as the AUTHORITY for the primary numbers. A
    derived summary cannot detect corruption of the raw data it was derived from -- it
    was written before the corruption and is simply believed afterwards. Every check in
    the old chain was downstream of a file that the mutation never touched.

WHAT THIS DOES INSTEAD
    Starts at the per-seed observations and walks the whole chain itself:

        raw per-seed gate counts
          -> per-arm empirical distributions
          -> theta (ratio of arm means)
          -> paired bootstrap interval for theta
          -> REGRESSION / NO_REGRESSION / UNRESOLVED
          -> boundary flag, eligibility
          -> finite-sample decision risk at k=3
          -> risk bootstrap interval
          -> 12/26, 7/26, 4/26
          -> the literals printed in PAPER.md

    It reads NO summary table, NO inventory, and NO expected-results file. If the raw
    data changes, every number here changes with it.

INDEPENDENT ESTIMATOR
    The risk is computed by convolving the k-fold sum distributions and applying the
    decision rule as an EXACT INTEGER comparison -- q*S_B >= (q+p)*S_A, no floats on the
    decision path. The probability weights themselves are float64, so this is exact in the
    CUTOFF and floating in the ARITHMETIC; v3's docstring called it "exact integer
    convolution", which overstates it (Astra A12). It is written independently of the
    repository's `exact_rate_int`; both share the exact cutoff, so they must agree to the
    last digit, and they are written differently on purpose so a defect in one cannot
    silently certify itself. `--cross-check` asserts the agreement on every circuit.

WHAT IT DOES NOT DO
    It does not establish that the bootstrap intervals have calibrated coverage for any
    population beyond the recorded samples (audit F06), and it does not repair the seed
    law (audit F02). It checks that the manuscript's numbers are the numbers the raw data
    produces. That is all it claims.

USAGE
    python raw_endpoint.py                 # reconstruct and compare to PAPER.md
    python raw_endpoint.py --cross-check   # also assert agreement with exact_rate_int
    python raw_endpoint.py --json out.json # write the reconstruction
"""

import argparse
import json
import os
import re
import sys
from fractions import Fraction

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from prereg_analysis import load_seeded, BOUNDARY_PP, TIE_EPS  # raw I/O + the frozen 3pp rule

PAPER = os.path.join(ROOT, "PAPER.md")
SELECTED = os.path.join(ROOT, "_selected.txt")

THRESHOLD = Fraction(1, 10)     # +10%, exact
K = 3
BOOT_TRUTH = 4000
BOOT_ERR = 400
RNG_TRUTH = 20260904            # the frozen streams, documented in PREREGISTRATION.md
RNG_ERR = 20260905


def ksum_pmf(values, k):
    """Exact pmf of the sum of k i.i.d. draws from `values`, as (offset, weights).

    Histogram then k-fold convolution. Integer supports only; the weights are exact
    rationals in float form, and the total is asserted to 1 within 1e-12.
    """
    v = np.asarray(values, dtype=np.int64)
    lo, hi = int(v.min()), int(v.max())
    counts = np.bincount(v - lo, minlength=hi - lo + 1).astype(np.float64)
    pmf = counts / counts.sum()
    out = pmf
    for _ in range(k - 1):
        out = np.convolve(out, pmf)
    return lo * k, out


def exact_call_probability(a, b, t: Fraction, k):
    """P( q*S_B >= (q+p)*S_A ) exactly, by convolution. Lower gate count is better,
    so a 'call' is the decision rule firing: the candidate looks at least t worse."""
    p, q = t.numerator, t.denominator
    off_a, pa = ksum_pmf(a, k)
    off_b, pb = ksum_pmf(b, k)
    assert abs(pa.sum() - 1) < 1e-12 and abs(pb.sum() - 1) < 1e-12
    # cumulative over S_A so each S_B value costs O(1)
    csum_a = np.cumsum(pa)
    total = 0.0
    coef = q + p
    for i, w in enumerate(pb):
        if w == 0.0:
            continue
        sb = off_b + i
        # q*sb >= (q+p)*sa  <=>  sa <= q*sb/(q+p)
        limit = (q * sb) // coef
        idx = limit - off_a
        if idx < 0:
            continue
        if idx >= csum_a.size:
            total += w
        else:
            total += w * csum_a[idx]
    return float(total)


def reconstruct(circuits, cross_check=False):
    rows = []
    for c in circuits:
        s_o, o, v_o = load_seeded(c, "143")
        s_n, n, v_n = load_seeded(c, "200")
        if o is None or n is None:
            rows.append({"circuit": c, "status": "MISSING_OR_CRASHED"})
            continue
        if s_o.size != s_n.size or not np.array_equal(s_o, s_n) \
                or np.unique(s_o).size != s_o.size:
            rows.append({"circuit": c, "status": "MISALIGNED_SEEDS"})
            continue
        m = int(o.size)
        if m == 0 or not (o > 0).all():
            rows.append({"circuit": c, "status": "UNUSABLE_ZERO_OR_EMPTY"})
            continue

        theta = float(n.mean() / o.mean() - 1)
        r1 = np.random.default_rng(RNG_TRUTH)
        ch = np.empty(BOOT_TRUTH)
        for i in range(BOOT_TRUTH):
            j = r1.integers(0, m, m)
            ch[i] = n[j].mean() / o[j].mean() - 1
        c_lo, c_hi = (float(x) for x in np.percentile(ch, [2.5, 97.5]))

        t = float(THRESHOLD)
        # same inclusive-threshold tie policy as prereg_analysis (Astra A12)
        verdict = ("REGRESSION" if (c_lo - t) > TIE_EPS else
                   "NO_REGRESSION" if (t - c_hi) > TIE_EPS else "UNRESOLVED")
        boundary = abs(theta - t) * 100 <= BOUNDARY_PP

        row = {"circuit": c, "status": "OK", "n_seeds": m,
               "theta_pct": theta * 100, "ci_lo_pct": c_lo * 100,
               "ci_hi_pct": c_hi * 100, "verdict": verdict, "boundary": boundary,
               "distance_pp": abs(theta - t) * 100}

        if verdict == "UNRESOLVED":
            row.update({"risk": None, "risk_lo": None, "risk_hi": None,
                        "excludes_zero": False})
            rows.append(row)
            continue

        pcall = exact_call_probability(o, n, THRESHOLD, K)
        risk = (1 - pcall) if verdict == "REGRESSION" else pcall

        if cross_check:
            from deep import exact_rate_int
            ref = exact_rate_int(o, n, t, K)
            ref_risk = (1 - ref) if verdict == "REGRESSION" else ref
            if abs(ref_risk - risk) > 1e-9:
                raise SystemExit(
                    f"ESTIMATOR DISAGREEMENT on {c}: convolution {risk!r} vs "
                    f"exact_rate_int {ref_risk!r}. One of the two is wrong.")

        r2 = np.random.default_rng(RNG_ERR)
        errs = np.empty(BOOT_ERR)
        for i in range(BOOT_ERR):
            j = r2.integers(0, m, m)
            pc = exact_call_probability(o[j], n[j], THRESHOLD, K)
            errs[i] = (1 - pc) if verdict == "REGRESSION" else pc
        e_lo, e_hi = (float(x) for x in np.percentile(errs, [2.5, 97.5]))

        row.update({"risk": risk, "risk_lo": e_lo, "risk_hi": e_hi,
                    "excludes_zero": bool(e_lo > 0)})
        rows.append(row)
    return rows


def endpoint(rows):
    elig = [r for r in rows if r.get("status") == "OK"
            and r["verdict"] != "UNRESOLVED" and not r["boundary"]]
    excl = [r for r in elig if r["excludes_zero"]]
    ge5 = [r for r in elig if r["risk"] is not None and r["risk"] >= 0.05]
    ge10 = [r for r in elig if r["risk"] is not None and r["risk"] >= 0.10]
    return elig, excl, ge5, ge10


def paper_literals():
    """Pull the endpoint fractions out of the results table in PAPER.md.

    Bound to the specific table ROWS, not to loose prose. A pattern that can match
    anywhere in the manuscript is the same defect paper_check.py had: presence is not
    placement, and a number found in an unrelated sentence is not the number under test.
    The manuscript is the thing being checked; it is never the source of truth for the
    computation above.
    """
    txt = open(PAPER, encoding="utf-8").read()
    rows = {"excl": r"risk\s*>\s*0[^|]*\|\s*(\d+)\s*/\s*(\d+)\s*\|",
            "ge5": r"risk\s*≥\s*5\s*%\s*\|\s*(\d+)\s*/\s*(\d+)\s*\|",
            "ge10": r"risk\s*≥\s*10\s*%\s*\|\s*(\d+)\s*/\s*(\d+)\s*\|"}
    found, denoms = {}, set()
    for key, pat in rows.items():
        m = re.search(pat, txt)
        if m:
            found[key] = int(m.group(1))
            denoms.add(int(m.group(2)))
    found["_denominator"] = denoms.pop() if len(denoms) == 1 else None
    return found, txt


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cross-check", action="store_true",
                    help="assert the convolution estimator agrees with exact_rate_int")
    ap.add_argument("--json", help="write the full reconstruction here")
    args = ap.parse_args()

    circuits = [c.strip() for c in open(SELECTED) if c.strip()]
    print(f"\n  RAW RECONSTRUCTION — {len(circuits)} circuits, heavy-hex, 1.4.3 -> 2.0.0,"
          f" k={K}, threshold +10%")
    print(f"  source: results/raw/prereg/*.jsonl   (no summary table is read)\n")

    rows = reconstruct(circuits, cross_check=args.cross_check)
    elig, excl, ge5, ge10 = endpoint(rows)

    ok_rows = [r for r in rows if r.get("status") == "OK"]
    unres = [r for r in ok_rows if r["verdict"] == "UNRESOLVED"]
    bound = [r for r in ok_rows if r["verdict"] != "UNRESOLVED" and r["boundary"]]
    print(f"  resolved {len(ok_rows) - len(unres)} / unresolved {len(unres)}"
          f" | boundary exclusions {len(bound)} | ELIGIBLE {len(elig)}")
    print(f"  intervals excluding zero : {len(excl)}/{len(elig)}")
    print(f"  risk >= 5%               : {len(ge5)}/{len(elig)}")
    print(f"  risk >= 10%              : {len(ge10)}/{len(elig)}")

    lits, _ = paper_literals()
    print(f"\n  PAPER.md literals found: {lits}")

    fails = []
    want_denom = lits.get("_denominator")
    if want_denom is None:
        fails.append("PAPER.md's results table does not state one consistent denominator")
    elif len(elig) != want_denom:
        fails.append(f"eligible set reconstructed from raw is {len(elig)}, "
                     f"PAPER.md's table says {want_denom}")
    for label, got, key in (("intervals excluding zero", len(excl), "excl"),
                            ("risk >= 5%", len(ge5), "ge5"),
                            ("risk >= 10%", len(ge10), "ge10")):
        want = lits.get(key)
        if want is None:
            fails.append(f"could not locate the '{label}' literal in PAPER.md")
        elif want != got:
            fails.append(f"{label}: raw data gives {got}, PAPER.md says {want}")

    if args.json:
        json.dump({"rows": rows, "eligible": len(elig), "excludes_zero": len(excl),
                   "ge5": len(ge5), "ge10": len(ge10), "paper": lits},
                  open(args.json, "w"), indent=1)
        print(f"  written: {args.json}")

    if fails:
        print("\n  ✗ RAW DATA AND MANUSCRIPT DISAGREE:\n")
        for f in fails:
            print(f"      {f}")
        print("\n  This is the check that the v2 apparatus did not have. Either the raw")
        print("  data changed, or the manuscript states a number the data does not"
              " support.\n")
        sys.exit(1)

    print("\n  ✓ the manuscript's primary endpoint is what the raw data produces.\n")


if __name__ == "__main__":
    main()
