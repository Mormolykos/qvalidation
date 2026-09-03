"""Confidence intervals for every reported probability. Priority 1 of the audit.

THE DEFECT THIS FIXES (DEFECTS.md D-1.1)
    The study reported "27.1%" to three decimals from TWELVE observations, with no
    interval anywhere. The reviewer's resampling put the 95% interval at 0.043 ... 0.331
    -- "27.1%" and "4.3%" are both inside the data.

    Every probability in this repository has the same problem, not just the headline.

WHAT THE SAMPLING UNIT ACTUALLY IS
    Not the bootstrap iteration. The bootstrap over draw-pairs only estimates the
    protocol's behaviour GIVEN the 12 seeds we happened to run. The real sampling
    error is WHICH 12 SEEDS WERE DRAWN. So the interval must resample seeds.

    Two levels, kept strictly separate:
      inner : P(call) given a fixed seed set -- computed EXACTLY, see below
      outer : resample the 12 seeds with replacement, recompute, take percentiles

WHY THE INNER LEVEL IS EXACT AND NOT BOOTSTRAPPED
    For k runs per version the protocol averages k draws each side. With n=12 seeds
    there are n**k possible means per side (1728 for k=3). The call rate is then

        P = (1/N^2) * sum over a in A, b in B  of  [ (b-a)/a >= t ]
          = (1/N^2) * sum over a in A of  |{ b in B : b >= a*(1+t) }|

    which is one sort plus one searchsorted. Exact, deterministic, and it removes
    bootstrap noise from the point estimate entirely. The reviewer computed 0.2710 this
    way against our bootstrap's 0.2705; this script reproduces the exact value.

METHOD, STATED ONCE AND USED THROUGHOUT
    Percentile bootstrap over seeds, B = 2000 outer resamples, 95% interval
    (2.5th / 97.5th percentiles). Chosen because:
      - the statistic is a bounded proportion with no closed-form variance here;
      - normal-approximation intervals (Wald) are known to fail badly for proportions
        near 0 or 1, and several of our rates are near 0;
      - the percentile bootstrap makes no distributional assumption, which matters
        because sec 30 measured these distributions as strongly non-normal
        (cc_n64 skew +2.99, Shapiro p = 0).
    Where a proportion is a simple count over circuits (e.g. "15 of 58 unstable"),
    a Wilson score interval is used instead -- also asymmetric, also valid near the
    bounds -- and is labelled as such in the output.

USAGE
    python intervals.py --old <old.jsonl> --new <new.jsonl> --topology heavy-hex \
        --threshold 0.10 --k 3 --out results/summary/ci_heavyhex.csv
"""

import argparse
import csv
import json
import math
import os
from collections import defaultdict
from itertools import product

import numpy as np


BOOTSTRAP_B = 2000
CI_LEVEL = 95.0
METHOD_INNER = "exact enumeration over n**k mean-triples"
METHOD_OUTER = f"percentile bootstrap over seeds, B={BOOTSTRAP_B}, {CI_LEVEL}% interval"


def load(path):
    vals, version = defaultdict(list), None
    with open(path) as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("qiskit_version"):
                version = row["qiskit_version"]
            if row.get("record") == "run":
                vals[row["circuit"]].append((row["seed"], row["two_q"]))
    if version is None:
        raise SystemExit(f"ABORT: {path} records no qiskit_version.")
    return {c: [v for _, v in sorted(p)] for c, p in vals.items()}, version


_GRID_CACHE = {}


def _grid(n, k):
    """Index grid for all n**k combinations, cached: the outer bootstrap calls this
    B x n_circuits times and rebuilding it each time dominated the runtime."""
    key = (n, k)
    if key not in _GRID_CACHE:
        _GRID_CACHE[key] = np.array(list(product(range(n), repeat=k)))
    return _GRID_CACHE[key]


def k_means(values, k):
    """All n**k means of k draws with replacement. Exact, no sampling."""
    arr = np.asarray(values, dtype=float)
    if k == 1:
        return arr
    return arr[_grid(len(arr), k)].mean(axis=1)


def exact_call_rate(old_vals, new_vals, threshold, k):
    """P((b-a)/a >= threshold) over ALL pairs of k-means. One sort + searchsorted."""
    a = np.sort(k_means(old_vals, k))
    b = np.sort(k_means(new_vals, k))
    if a.size == 0 or b.size == 0:
        return float("nan")
    cut = a * (1.0 + threshold)              # b must reach this to be a "regression"
    idx = np.searchsorted(b, cut, side="left")
    return float((b.size - idx).sum()) / (a.size * b.size)


def seed_bootstrap_ci(old_vals, new_vals, threshold, k, rng, b=BOOTSTRAP_B):
    """Resample WHICH SEEDS were drawn, recompute exactly, take percentiles."""
    n_old, n_new = len(old_vals), len(new_vals)
    o = np.asarray(old_vals, dtype=float)
    n = np.asarray(new_vals, dtype=float)
    rates = np.empty(b)
    for i in range(b):
        ro = o[rng.integers(0, n_old, n_old)]
        rn = n[rng.integers(0, n_new, n_new)]
        rates[i] = exact_call_rate(ro, rn, threshold, k)
    lo, hi = np.percentile(rates, [(100 - CI_LEVEL) / 2, 100 - (100 - CI_LEVEL) / 2])
    return float(lo), float(hi)


def wilson(successes, total, z=1.959963985):
    """Wilson score interval for a simple count-over-circuits proportion."""
    if total == 0:
        return (float("nan"), float("nan"))
    p = successes / total
    d = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / d
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True)
    parser.add_argument("--new", required=True)
    parser.add_argument("--topology", required=True)
    parser.add_argument("--threshold", type=float, default=0.10)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--min-seeds", type=int, default=12)
    parser.add_argument("--boundary-band", type=float, default=3.0,
                        help="D-1.6: true effects within this many percentage points "
                             "of the threshold are boundary artifacts, not findings")
    parser.add_argument("--seed", type=int, default=20260903)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    old, v_old = load(args.old)
    new, v_new = load(args.new)
    rng = np.random.default_rng(args.seed)

    shared = sorted(set(old) & set(new))
    rows = []
    for circuit in shared:
        a, b = old[circuit], new[circuit]
        if len(a) < args.min_seeds or len(b) < args.min_seeds:
            continue
        point = exact_call_rate(a, b, args.threshold, args.k)
        lo, hi = seed_bootstrap_ci(a, b, args.threshold, args.k, rng)
        mean_a, mean_b = float(np.mean(a)), float(np.mean(b))
        true_change = (mean_b - mean_a) / mean_a * 100 if mean_a else 0.0
        rows.append({
            "topology": args.topology,
            "circuit": circuit,
            "qiskit_old": v_old, "qiskit_new": v_new,
            "n_seeds_old": len(a), "n_seeds_new": len(b),
            "k": args.k, "threshold": args.threshold,
            "true_change_pct": round(true_change, 3),
            "p_call": round(point, 4),
            "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
            "ci_width": round(hi - lo, 4),
            "boundary_artifact": abs(true_change - args.threshold * 100)
                                 <= args.boundary_band,
            "verdict": ("STABLE_REGRESSION" if point >= 0.95 else
                        "STABLE_CLEAN" if point <= 0.05 else "UNSTABLE"),
            "ci_method_point": METHOD_INNER,
            "ci_method_interval": METHOD_OUTER,
        })

    unstable = [r for r in rows if r["verdict"] == "UNSTABLE"]
    genuine = [r for r in unstable if not r["boundary_artifact"]]
    w_lo, w_hi = wilson(len(genuine), len(rows))

    print(f"\n  {args.topology}: qiskit {v_old} -> {v_new}, k={args.k}, "
          f"threshold {args.threshold:+.0%}")
    print(f"  {len(rows)} circuits with >= {args.min_seeds} seeds in both arms")
    print(f"  point estimates: {METHOD_INNER}")
    print(f"  intervals:       {METHOD_OUTER}\n")
    print(f"  UNSTABLE {len(unstable)}  |  boundary {len(unstable)-len(genuine)}  "
          f"|  GENUINE {len(genuine)}")
    print(f"  genuine proportion {len(genuine)}/{len(rows)} = "
          f"{len(genuine)/len(rows):.3f}  Wilson 95% CI [{w_lo:.3f}, {w_hi:.3f}]\n")

    if genuine:
        print(f"  {'circuit':<18s} {'true Δ':>8s} {'P(call)':>8s} {'95% CI':>18s} "
              f"{'width':>7s}")
        for r in sorted(genuine, key=lambda r: -r["p_call"]):
            ci = f"[{r['ci_lo']:.3f}, {r['ci_hi']:.3f}]"
            print(f"  {r['circuit']:<18s} {r['true_change_pct']:>+7.1f}% "
                  f"{r['p_call']:>8.3f} {ci:>18s} {r['ci_width']:>7.3f}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
