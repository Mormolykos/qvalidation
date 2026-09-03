"""Priority 3 — where k=3 came from, and whether the result depends on it.

PROVENANCE, ESTABLISHED FROM PRIMARY SOURCES (see sec 40)
    EXTERNAL, not arbitrary, but only half-verified.

    Qiskit issue #14402, verbatim: "This was verified by running Benchpress several
    times for each version to get statistics. E.g. over the full test suite the values
    returned for 3 runs was:". Three runs per version is stated by the reporter.

    Benchpress itself has NO run-count knob. Searched the whole repo for `n_runs`,
    `num_runs`, `repeat`, and pytest `addoption`: nothing. k is not a property of the
    tool; the three runs were a choice the reporter made by hand.

    What is NOT established, and D-1.4 stands: the issue calls the per-test figures
    "the avg. percent increase in 2Q gate counts" without saying what the average is
    over. Whether the per-circuit numbers are 3-run means, single-run values, or
    something else is NOT STATED in the issue. We assume 3-run means. That assumption
    is load-bearing and is now labelled as an assumption everywhere.

WHY THE SENSITIVITY TEST USES THE BAND AND NOT THE OLD FP RATE
    sec 34 swept k against the per-circuit false-positive rate. That statistic turned
    out to depend on which version is treated as the baseline (sec 41), so its k-curve
    inherits the same defect. The ambiguity band does not: it sweeps the true change
    itself, so it has no baseline to pick.

    The question this answers is the one a maintainer would ask: **how many unseeded
    runs per version would Benchpress need before its verdicts become reliable?**

    The answer is reported for whatever k says, in both directions. It is not selected.

USAGE
    python ksweep.py --old results/raw/bp_large_heavy-hex_q200.jsonl \
        --new results/raw/bp_large_heavy-hex_q202.jsonl --topology heavy-hex \
        --k-list 1,2,3,5,10,20,50 --out results/summary/ksweep_heavy-hex.csv
"""

import argparse
import csv
import os

import numpy as np

from intervals import load
from paired import BAND_HI, BAND_LO

EXACT_MAX = 300_000          # enumerate n**k tuples up to here; sample above it
MC_SAMPLES = 200_000


def _means(vals, k, rng):
    """All n**k means when that is affordable, otherwise MC_SAMPLES sampled ones.
    Returns (means, exact_flag). Sampling is only ever an approximation of the
    enumeration -- never of the data."""
    arr = np.asarray(vals, dtype=float)
    n = arr.size
    if k == 1:
        return arr, True, None
    if n ** k <= EXACT_MAX:
        from itertools import product
        g = np.array(list(product(range(n), repeat=k)))
        return arr[g].mean(axis=1), True, g
    g = rng.integers(0, n, size=(MC_SAMPLES, k))
    return arr[g].mean(axis=1), False, g


def _rates(old, new, t, k, rng):
    """(unpaired, paired) call rates. The paired arm reuses the SAME index tuples on
    both sides, which is the whole point; the unpaired arm draws each side freely."""
    o = np.asarray(old, dtype=float)
    n = np.asarray(new, dtype=float)
    a_all, exact, g = _means(o, k, rng)
    if g is None:
        b_paired = n
    else:
        b_paired = n[g].mean(axis=1)
    ok = a_all != 0
    paired = float(((b_paired[ok] - a_all[ok]) / a_all[ok] >= t).sum()) / int(ok.sum())

    b_all, _, _ = _means(n, k, rng)
    a_s = np.sort(a_all)
    b_s = np.sort(b_all)
    idx = np.searchsorted(b_s, a_s * (1.0 + t), side="left")
    unpaired = float((b_s.size - idx).sum()) / (a_s.size * b_s.size)
    return unpaired, paired, exact


def _band(old, rho, t, k, rng, paired, lo=0.5, hi=3.0, iters=26):
    def rate(r):
        u, p, _ = _rates(old, np.asarray(old, float) * r * rho, t, k, rng)
        return p if paired else u

    def solve(target):
        if rate(hi) < target:
            return float("nan")
        a, b = lo, hi
        if rate(a) >= target:
            return a
        for _ in range(iters):
            m = (a + b) / 2
            if rate(m) >= target:
                b = m
            else:
                a = m
        return (a + b) / 2

    x, y = solve(BAND_LO), solve(BAND_HI)
    if np.isnan(x) or np.isnan(y):
        return None
    return (y - x) * 100


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--old", required=True)
    p.add_argument("--new", required=True)
    p.add_argument("--topology", required=True)
    p.add_argument("--threshold", type=float, default=0.10)
    p.add_argument("--k-list", default="1,2,3,5,10,20,50")
    p.add_argument("--min-seeds", type=int, default=12)
    p.add_argument("--wide-band", type=float, default=5.0)
    p.add_argument("--seed", type=int, default=20260903)
    p.add_argument("--out")
    args = p.parse_args()

    old_all, v_old = load(args.old)
    new_all, v_new = load(args.new)
    ks = [int(x) for x in args.k_list.split(",")]

    arms = []
    for c in sorted(set(old_all) & set(new_all)):
        a, b = old_all[c], new_all[c]
        if len(a) < args.min_seeds or len(b) < args.min_seeds or len(a) != len(b):
            continue
        o, n = np.asarray(a, float), np.asarray(b, float)
        if not (o > 0).all():
            continue
        ratio = n / o
        arms.append((c, o, ratio / ratio.mean(), ratio.max() != ratio.min()))

    print(f"\n  k SENSITIVITY, {args.topology}, {len(arms)} circuits, "
          f"threshold {args.threshold:+.0%}, qiskit {v_old} vs {v_new}")
    print(f"  band = width in pp of true change over which P(call) runs 0.05 -> 0.95")
    print(f"  smaller is better; a band of 0 means the verdict is never ambiguous\n")
    print(f"  {'k':>3s} {'exact':>6s} {'unpaired med':>13s} {'paired med':>11s} "
          f"{'ratio':>6s} {'>= ' + format(args.wide_band, 'g') + 'pp':>9s} "
          f"{'worst':>8s}")

    rows = []
    for k in ks:
        rng = np.random.default_rng(args.seed)
        exact = len(arms[0][1]) ** k <= EXACT_MAX or k == 1
        bu_all, bu_het, bp_het, wide = [], [], [], 0
        for name, o, rho, het in arms:
            u = _band(o, rho, args.threshold, k, rng, paired=False)
            if u is None:
                continue
            bu_all.append(u)
            if u >= args.wide_band:
                wide += 1
            if het:
                pb = _band(o, rho, args.threshold, k, rng, paired=True)
                if pb is not None:
                    bu_het.append(u)
                    bp_het.append(pb)
        mu = float(np.median(bu_het)) if bu_het else float("nan")
        mp = float(np.median(bp_het)) if bp_het else float("nan")
        ratio = mu / mp if mp else float("inf")
        frac = wide / len(bu_all) if bu_all else float("nan")
        rows.append({
            "topology": args.topology, "k": k, "exact": exact,
            "n_circuits": len(bu_all), "n_heterogeneous": len(bp_het),
            "unpaired_median_band_pp": round(mu, 3),
            "paired_median_band_pp": round(mp, 3),
            "narrowing_factor": round(ratio, 2) if np.isfinite(ratio) else "inf",
            "frac_band_ge_wide": round(frac, 4),
            "wide_band_pp": args.wide_band,
            "unpaired_max_band_pp": round(max(bu_all), 3) if bu_all else None,
            "qiskit_old": v_old, "qiskit_new": v_new,
            "threshold": args.threshold,
        })
        print(f"  {k:>3d} {'yes' if exact else 'MC':>6s} {mu:>10.2f} pp "
              f"{mp:>8.2f} pp {ratio:>5.1f}x {frac:>9.3f} "
              f"{max(bu_all) if bu_all else 0:>6.1f} pp")

    print(f"\n  k=3 is the protocol reported in issue #14402 (verbatim: 'the values "
          f"returned for 3 runs').")
    print(f"  Nothing here is selected on effect size: every k requested is printed.")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
