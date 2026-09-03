"""Attacks on sec 48's headline that need no new measurement.

THE CLAIM UNDER ATTACK
    "bv_n140 carries a +31.0% regression that the 3-run unseeded protocol misses 2.98%
     of the time."

    Three analyst choices sit underneath it, and a reviewer will reach for all three:

    R1  THE THRESHOLD IS OURS, NOT BENCHPRESS'S (sec 45 B2). Benchpress defines no
        regression threshold at all; +10% is a reconstruction. If the finding only
        exists at +10%, it is an artifact of a number we chose.
    R2  k=3 IS INHERITED FROM THE ISSUE, and its averaging basis was never confirmed
        (D-1.4). If the error vanishes at k=5, the fix is "run more" and there is no
        finding worth reporting.
    R3  IS 200 SEEDS ENOUGH? The truth +31.0% is itself an estimate. Split the sample
        in half and see whether the two halves agree; if they do not, the ground truth
        is not established and neither is the error rate measured against it.

    None of these is answered by re-reading the record. All three are answered by
    re-running the arithmetic on data already on disk.

USAGE
    python robust.py --circuit bv_n140
"""

import argparse

import numpy as np

from deep import exact_rate_int, load_deep


def truth_ci(o, n, rng, b=4000):
    m = o.size
    ch = np.empty(b)
    for i in range(b):
        j = rng.integers(0, m, m)
        ch[i] = n[j].mean() / o[j].mean() - 1
    return float(np.percentile(ch, 2.5)), float(np.percentile(ch, 97.5))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--circuit", default="bv_n140")
    ap.add_argument("--seed", type=int, default=20260903)
    args = ap.parse_args()

    o, v_o = load_deep(args.circuit, "143")
    n, v_n = load_deep(args.circuit, "200")
    m = min(o.size, n.size)
    o, n = o[:m], n[:m]
    rng = np.random.default_rng(args.seed)
    change = float(n.mean() / o.mean() - 1)

    print(f"\n  {args.circuit}: qiskit {v_o} -> {v_n}, {m} seeds per arm")
    print(f"  measured true change {change:+.2%}\n")

    print("  R1 — THRESHOLD SENSITIVITY (the threshold is ours, not Benchpress's)")
    print(f"     {'threshold':>10s} {'dist to cut':>12s} {'truth':>16s} "
          f"{'error rate':>11s}")
    for t in (0.02, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20, 0.25, 0.30):
        p = exact_rate_int(o, n, t, 3)
        lo, hi = truth_ci(o, n, np.random.default_rng(args.seed + 1), 1500)
        truth = ("REGRESSION" if lo > t else
                 "NO_REGRESSION" if hi < t else "UNRESOLVED")
        err = (1 - p) if truth == "REGRESSION" else (
            p if truth == "NO_REGRESSION" else float("nan"))
        d = abs(change - t) * 100
        es = "  n/a" if np.isnan(err) else f"{err:.4f}"
        flag = "  <- boundary" if d <= 3.0 else ""
        print(f"     {t:>9.1%} {d:>11.1f}p {truth:>16s} {es:>11s}{flag}")

    print(f"\n  R2 — RUNS PER VERSION (k=3 is inherited, its basis unconfirmed)")
    print(f"     {'k':>3s} {'error rate':>11s} {'vs k=3':>9s}")
    base = 1 - exact_rate_int(o, n, 0.10, 3)
    for k in (1, 2, 3):
        e = 1 - exact_rate_int(o, n, 0.10, k)
        print(f"     {k:>3d} {e:>11.4f} {e/base if base else float('nan'):>8.2f}x")
    # k >= 4 by Monte Carlo: n**k enumeration is 1.6e9+ tuples
    from deep import mc_rate
    for k in (4, 5, 8, 10, 20):
        r = np.random.default_rng(args.seed + k)
        e = 1 - mc_rate(o, n, 0.10, k, r, 4_000_000)
        se = float(np.sqrt(max(e, 1e-9) * (1 - e) / 4_000_000))
        print(f"     {k:>3d} {e:>11.4f} {e/base if base else float('nan'):>8.2f}x   "
              f"(MC, se {se:.5f})")

    print(f"\n  R3 — IS 200 SEEDS ENOUGH? Split-half agreement on the truth AND the "
          f"error rate")
    h = m // 2
    for label, (oo, nn) in (("first half", (o[:h], n[:h])),
                            ("second half", (o[h:], n[h:])),
                            ("FULL", (o, n))):
        c = float(nn.mean() / oo.mean() - 1)
        lo, hi = truth_ci(oo, nn, np.random.default_rng(args.seed + 2), 2000)
        e = 1 - exact_rate_int(oo, nn, 0.10, 3)
        print(f"     {label:<12s} n={oo.size:<4d} change {c:+.2%} "
              f"[{lo:+.2%}, {hi:+.2%}]  error {e:.4f}")

    # odd/even seeds, a partition that cannot align with any drift in run order
    oe = [(o[::2], n[::2]), (o[1::2], n[1::2])]
    for label, (oo, nn) in zip(("odd seeds", "even seeds"), oe):
        c = float(nn.mean() / oo.mean() - 1)
        e = 1 - exact_rate_int(oo, nn, 0.10, 3)
        print(f"     {label:<12s} n={oo.size:<4d} change {c:+.2%}"
              f"{'':<20s}  error {e:.4f}")


if __name__ == "__main__":
    main()
