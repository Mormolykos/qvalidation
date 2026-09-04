"""A1, settled — 200 seeds per arm on the five decisive circuits.

WHY THIS RUN EXISTS
    At 12 seeds the demonstrated decision errors had bootstrap intervals that included
    ZERO: bv_n30 3.87% [0.0%, 20.5%], bv_n140 2.01% [0.0%, 15.9%]. So the 12-seed
    census could not distinguish "this regression is sometimes missed" from "it never
    is". That is defect D-1.1 in its final form, and the only cure is more seeds.

    D-1.1 asked for 200+ seeds on the affected circuits in the first hostile review.
    This is that run: 200 seeds x 2 Qiskit versions x 5 circuits, forward direction,
    baseline 1.4.3 -> candidate 2.0.0, which is the version pair issue #14402 actually
    reports.

METHOD
    point estimate : EXACT over all 200**3 = 8,000,000 sum-triples per arm, using the
                     integer decision rule q*Sb >= (q+p)*Sa (no floating point, see
                     intervals.exact_call_rate). One sort plus one searchsorted.
    interval       : seed bootstrap, resampling WHICH 200 seeds were drawn, jointly
                     across the paired arms; each replicate scored by Monte Carlo over
                     MC_PAIRS random triple-pairs, whose own error is reported so it
                     cannot be confused with the seed uncertainty.

USAGE
    python deep.py --threshold 0.10 --k 3 --out results/summary/deep_143_200.csv
"""

import argparse
import csv
import json
import os
from fractions import Fraction

import numpy as np

from intervals import CI_LEVEL, wilson

CIRCUITS = ["bv_n30", "bv_n70", "bv_n140", "adder_n64", "qft_n29"]
MC_PAIRS = 4_000_000
BOOT_B = 400
BOOT_MC = 400_000


def load_deep(circuit, ver):
    path = os.path.join("results", "raw", f"deep_{circuit}_q{ver}.jsonl")
    vals, version = [], None
    for line in open(path):
        r = json.loads(line)
        if r.get("qiskit_version"):
            version = r["qiskit_version"]
        if r.get("record") == "run":
            vals.append((r["seed"], r["two_q"]))
    if version is None:
        raise SystemExit(f"ABORT: {path} names no qiskit version")
    return np.array([v for _, v in sorted(vals)], dtype=np.int64), version


def _sums3(v):
    """All n**3 sums, built by broadcasting so no n**3 x 3 index grid is materialised."""
    return (v[:, None, None] + v[None, :, None] + v[None, None, :]).ravel()


def exact_rate_int(o, n, threshold, k):
    """P((b-a)/a >= t) exactly, integer arithmetic, k in {1,2,3}."""
    fr = Fraction(threshold).limit_denominator(10 ** 9)
    p, q = fr.numerator, fr.denominator
    if k == 3:
        sa, sb = _sums3(o), _sums3(n)
    elif k == 2:
        sa = (o[:, None] + o[None, :]).ravel()
        sb = (n[:, None] + n[None, :]).ravel()
    else:
        sa, sb = o, n
    sa = np.sort(sa.astype(np.int64) * (q + p))
    sb = np.sort(sb.astype(np.int64) * q)
    idx = np.searchsorted(sb, sa, side="left")
    return float((sb.size - idx).sum()) / (float(sa.size) * float(sb.size))


MC_CHUNK_ELEMS = 40_000_000       # cap the index array at ~320 MB of int64


def mc_rate(o, n, threshold, k, rng, pairs):
    """Monte-Carlo call rate, evaluated in CHUNKS so memory is bounded.

    The unchunked version allocated a (pairs, k) index array per arm, which is
    pairs*k*8 bytes *twice*. At pairs=50e6 and k=20 that is 7.45 GiB per arm and it
    raised ArrayMemoryError inside paper_check.py. Memory now depends on the chunk
    size only, never on `pairs` or `k`, and the result is identical because the
    estimate is a mean over independent draws.
    """
    fr = Fraction(threshold).limit_denominator(10 ** 9)
    p, q = fr.numerator, fr.denominator
    per = max(1, MC_CHUNK_ELEMS // max(k, 1))
    hits = done = 0
    while done < pairs:
        m = int(min(per, pairs - done))
        sa = o[rng.integers(0, o.size, (m, k))].sum(axis=1) * (q + p)
        sb = n[rng.integers(0, n.size, (m, k))].sum(axis=1) * q
        hits += int((sb >= sa).sum())
        done += m
    return hits / float(pairs)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--threshold", type=float, default=0.10)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--seed", type=int, default=20260903)
    ap.add_argument("--out")
    args = ap.parse_args()
    t, k = args.threshold, args.k
    rng = np.random.default_rng(args.seed)

    print(f"\n  A1 SETTLED — 200 seeds/arm, BASELINE 1.4.3 -> CANDIDATE 2.0.0, "
          f"linear, k={k}, threshold {t:+.0%}")
    print(f"  point: exact over 200**{k} sum-tuples per arm, integer rule "
          f"q*Sb >= (q+p)*Sa")
    print(f"  interval: seed bootstrap B={BOOT_B} (joint), each scored by "
          f"{BOOT_MC:,} MC pairs\n")

    rows = []
    for c in CIRCUITS:
        o, v_o = load_deep(c, "143")
        n, v_n = load_deep(c, "200")
        m = min(o.size, n.size)
        o, n = o[:m], n[:m]
        change = float(n.mean() / o.mean() - 1)

        # truth, from the deep sample
        r2 = np.random.default_rng(args.seed + 1)
        ch = np.empty(4000)
        for i in range(4000):
            j = r2.integers(0, m, m)
            ch[i] = n[j].mean() / o[j].mean() - 1
        c_lo, c_hi = np.percentile(ch, [(100 - CI_LEVEL) / 2,
                                        100 - (100 - CI_LEVEL) / 2])
        truth = ("REGRESSION" if c_lo > t else
                 "NO_REGRESSION" if c_hi < t else "UNRESOLVED")

        p_call = exact_rate_int(o, n, t, k)
        err = (1 - p_call) if truth == "REGRESSION" else (
            p_call if truth == "NO_REGRESSION" else float("nan"))

        # seed bootstrap on the ERROR RATE
        errs = np.empty(BOOT_B)
        for i in range(BOOT_B):
            j = rng.integers(0, m, m)
            pc = mc_rate(o[j], n[j], t, k, rng, BOOT_MC)
            errs[i] = (1 - pc) if truth == "REGRESSION" else pc
        e_lo, e_hi = np.percentile(errs, [(100 - CI_LEVEL) / 2,
                                          100 - (100 - CI_LEVEL) / 2])
        mc_err = float(np.sqrt(max(p_call, 1e-9) * (1 - p_call) / BOOT_MC))

        rows.append({
            "circuit": c, "qiskit_baseline": v_o, "qiskit_candidate": v_n,
            "n_seeds": int(m), "k": k, "threshold": t,
            "true_change_pct": round(change * 100, 3),
            "true_change_ci_lo_pct": round(float(c_lo) * 100, 3),
            "true_change_ci_hi_pct": round(float(c_hi) * 100, 3),
            "ground_truth": truth,
            "distance_to_cut_pp": round(abs(change - t) * 100, 2),
            "p_call_exact": round(p_call, 6),
            "error_rate": None if np.isnan(err) else round(err, 6),
            "error_ci_lo": round(float(e_lo), 6), "error_ci_hi": round(float(e_hi), 6),
            "error_ci_excludes_zero": bool(e_lo > 0),
            "mc_se_per_replicate": round(mc_err, 6),
            "method_point": f"exact over {m}**{k} sum-tuples, integer rule",
            "method_interval": f"seed bootstrap B={BOOT_B}, MC {BOOT_MC} pairs each",
        })

    print(f"  {'circuit':<11s} {'true Δ':>8s} {'95% CI':>18s} {'dist':>6s} "
          f"{'truth':>14s} {'error':>8s} {'95% CI on error':>20s} {'>0?':>5s}")
    for r in rows:
        ci = f"[{r['true_change_ci_lo_pct']:+.1f},{r['true_change_ci_hi_pct']:+.1f}]"
        eci = f"[{r['error_ci_lo']:.4f},{r['error_ci_hi']:.4f}]"
        er = "—" if r["error_rate"] is None else f"{r['error_rate']:.4f}"
        print(f"  {r['circuit']:<11s} {r['true_change_pct']:>+7.1f}% {ci:>18s} "
              f"{r['distance_to_cut_pp']:>5.1f}p {r['ground_truth']:>14s} {er:>8s} "
              f"{eci:>20s} {'YES' if r['error_ci_excludes_zero'] else 'no':>5s}")

    est = [r for r in rows if r["error_ci_excludes_zero"]]
    nb = [r for r in est if r["distance_to_cut_pp"] > 3.0]
    print(f"\n  circuits with an error rate whose 95% CI EXCLUDES ZERO: "
          f"{len(est)}/{len(rows)}")
    print(f"  of those, away from the threshold (>3 pp, so not a D-1.6 boundary "
          f"case): {len(nb)}/{len(rows)}")
    for r in nb:
        if r["ground_truth"] == "REGRESSION":
            what = (f"a {r['true_change_pct']:+.1f}% regression is MISSED")
        else:
            what = (f"a {r['true_change_pct']:+.1f}% NON-regression is FALSELY "
                    f"CALLED")
        print(f"    {what} {r['error_rate']:.2%} of the time "
              f"[{r['error_ci_lo']:.2%}, {r['error_ci_hi']:.2%}]  ({r['circuit']})")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
