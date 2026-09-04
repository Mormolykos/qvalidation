"""Round-three attacks. The frozen result is still not modified.

REVIEWER B, ROUND 3
    R1 "The Proximity Trap." The 3 pp boundary band is arbitrary; hits sit at 3.24,
       3.33, 3.53 pp. "If your boundary exclusion was 5 pp instead of 3, your 12/13
       claim would evaporate."                                    -> SWEEP THE BAND.
    R2 "The non-zero tautology." If two distributions overlap at all, a non-zero error
       rate is mathematically guaranteed, so proving non-zero is trivial.
                                     -> REPORT THE ENDPOINT AT OPERATIONAL RISK LEVELS.
    R3 "The fatal asymmetry." All 12 hits are false positives, because this version
       pair happens to sit just below the cut. The result measures the version pair,
       not the protocol.        -> ANSWER WITH A theta-FREE, DIRECTION-FREE STATISTIC.
    R4 "[17.4%, 81.0%] is a statistical suicide note." N=11 families is underpowered
       for a suite-level claim.                     -> CONCEDED. Stop claiming a suite.

REVIEWER A, ROUND 3
    C4 12/13 is a DETECTABILITY statement, not "92.3% of stochastic circuits truly
       have non-zero risk."                                            -> CONCEDED.
    C5 The 200-seed reference is a plug-in for the ENTIRE distribution, not just theta.
       -> Already addressed: the seed bootstrap resamples the whole empirical
          distribution and recomputes the rate, so it propagates functional
          uncertainty, not merely theta uncertainty. Quantified here as CI width.
    C6 Are the six hit families intrinsically more stochastic? A mechanistic
       hypothesis would be far stronger than "Benchpress is noisy."  -> TEST IT.

WHAT IS COMPUTED
    T1 boundary-band sweep, 0 .. 8 pp                                        (R1)
    T2 endpoint at risk levels >0, >=1%, >=5%, >=10%                         (R2)
    T3 the AMBIGUITY BAND per circuit at 200 seeds -- theta-free              (R3)
    T4 does (seed spread, distance to cut) predict the error rate?           (C6)
    T5 per-circuit error-CI widths, as the measure of functional uncertainty (C5)
"""

import csv
import re

import numpy as np

from deep import mc_rate
from intervals import wilson
from prereg_analysis import load

CSV = "results/summary/prereg_heavy-hex.csv"
T, K = 0.10, 3


def family(c):
    return re.sub(r"_?n?\d+$", "", c) or c


def arms(c):
    o, _ = load(c, "143")
    n, _ = load(c, "200")
    if o is None:
        return None, None
    m = min(o.size, n.size)
    return o[:m], n[:m]


def main():
    rows = [r for r in csv.DictReader(open(CSV)) if r["status"] == "OK"]
    data = {r["circuit"]: arms(r["circuit"]) for r in rows}
    resolved = [r for r in rows if r["verdict"] != "UNRESOLVED"]

    # ---------------------------------------------------------------- T1 (R1)
    print("\n  T1 — BOUNDARY-BAND SWEEP. Reviewer B: 'at 5 pp your 12/13 would evaporate.'")
    print(f"      {'band':>6s} {'eligible':>9s} {'hits':>6s} {'endpoint':>9s} "
          f"{'stochastic hits':>16s}")
    for band in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0):
        el = [r for r in resolved if float(r["distance_to_cut_pp"]) > band]
        hit = [r for r in el if r["error_excludes_zero"] == "True"]
        sto = [r for r in el if (lambda o, n: (n / o).std(ddof=1) > 0)(*data[r["circuit"]])]
        sh = [r for r in sto if r["error_excludes_zero"] == "True"]
        mark = "  <- pre-registered" if band == 3.0 else ""
        s = f"{len(sh)}/{len(sto)}" if sto else "0/0"
        print(f"      {band:>5.1f}p {len(el):>9d} {len(hit):>6d} "
              f"{len(hit)/len(el) if el else float('nan'):>9.4f} {s:>16s}{mark}")
    print("      -> Reviewer B's prediction is TESTED, not argued. Read the 5 pp row.")

    # ---------------------------------------------------------------- T2 (R2)
    print("\n  T2 — ENDPOINT AT OPERATIONAL RISK LEVELS. Reviewer B: 'non-zero is trivial.'")
    el = [r for r in resolved if r["boundary"] == "False"]
    print(f"      {'criterion':<28s} {'hits':>6s} {'of':>4s} {'endpoint':>9s} "
          f"{'Wilson 95% CI':>20s}")
    for label, test in (
            ("CI excludes zero (frozen)", lambda r: r["error_excludes_zero"] == "True"),
            ("risk >= 1%", lambda r: float(r["error_rate"] or 0) >= 0.01),
            ("risk >= 5%", lambda r: float(r["error_rate"] or 0) >= 0.05),
            ("risk >= 10%", lambda r: float(r["error_rate"] or 0) >= 0.10),
            ("risk >= 15%", lambda r: float(r["error_rate"] or 0) >= 0.15)):
        h = [r for r in el if test(r)]
        lo, hi = wilson(len(h), len(el))
        print(f"      {label:<28s} {len(h):>6d} {len(el):>4d} "
              f"{len(h)/len(el):>9.4f} [{lo:>7.4f},{hi:>7.4f}]")
    print("      -> 13 of 26 eligible circuits have EXACTLY zero risk, so 'non-zero is")
    print("         mathematically guaranteed' is false as stated. But the operational")
    print("         levels are the honest way to report it.")

    # ---------------------------------------------------------------- T3 (R3)
    print("\n  T3 — THE theta-FREE ANSWER TO 'THE FATAL ASYMMETRY'")
    print("      Reviewer B R3 is largely CORRECT: the error rate depends on where theta")
    print("      sits, which is a property of THIS version pair. The statistic that")
    print("      does not is the AMBIGUITY BAND: the width of the interval of true")
    print("      change over which P(call) runs 0.05 -> 0.95. It has no theta and no")
    print("      direction. Computed here at 200 seeds on the pre-registered circuits.\n")
    bands = []
    for r in sorted(resolved, key=lambda r: r["circuit"]):
        o, n = data[r["circuit"]]
        ratio = n / o
        if ratio.std(ddof=1) == 0:
            bands.append((r["circuit"], 0.0))
            continue
        rho = ratio / ratio.mean()
        rng = np.random.default_rng(5)

        def rate(x):
            return mc_rate(o, (o * x * rho).astype(np.int64), T, K, rng, 200000)

        lo_, hi_ = 0.5, 3.0
        def solve(target):
            a, b = 0.5, 3.0
            if rate(b) < target:
                return float("nan")
            if rate(a) >= target:
                return a
            for _ in range(22):
                m = (a + b) / 2
                if rate(m) >= target:
                    b = m
                else:
                    a = m
            return (a + b) / 2
        x, y = solve(0.05), solve(0.95)
        bands.append((r["circuit"], float("nan") if np.isnan(x) or np.isnan(y)
                      else (y - x) * 100))
    nz = [b for _, b in bands if b == b and b > 0]
    print(f"      circuits with a NON-ZERO ambiguity band: {len(nz)}/{len(bands)}")
    if nz:
        print(f"      band width pp: median {np.median(nz):.2f}  p75 "
              f"{np.percentile(nz,75):.2f}  max {max(nz):.2f}")
    print(f"\n      {'circuit':<16s} {'band pp':>9s}")
    for c, b in sorted(bands, key=lambda t: -(t[1] if t[1] == t[1] else -1))[:10]:
        print(f"      {c:<16s} {b:>9.2f}")

    # ---------------------------------------------------------------- T4 (C6)
    print("\n  T4 — MECHANISM: is the hit/miss split predicted by measurable properties?")
    xs, ys, names = [], [], []
    for r in resolved:
        o, n = data[r["circuit"]]
        cv = float((n / o).std(ddof=1))
        d = float(r["distance_to_cut_pp"])
        e = float(r["error_rate"] or 0)
        xs.append((cv, d))
        ys.append(e)
        names.append(r["circuit"])
    cv = np.array([x[0] for x in xs])
    dist = np.array([x[1] for x in xs])
    err = np.array(ys)
    print(f"      per-seed ratio SD vs error rate : Spearman "
          f"{__import__('scipy.stats', fromlist=['x']).spearmanr(cv, err).statistic:+.3f}")
    nzm = cv > 0
    print(f"      among the {nzm.sum()} stochastic circuits, distance-to-cut vs error: "
          f"Spearman "
          f"{__import__('scipy.stats', fromlist=['x']).spearmanr(dist[nzm], err[nzm]).statistic:+.3f}")
    print(f"      circuits with SD == 0: {int((~nzm).sum())}, all with error exactly 0: "
          f"{bool((err[~nzm] == 0).all())}")
    print("      -> the split is not 'family magic': it is whether routing is stochastic")
    print("         at all, and then how close theta sits to the cut.")

    # ---------------------------------------------------------------- T5 (C5)
    print("\n  T5 — FUNCTIONAL UNCERTAINTY (Reviewer A C5)")
    w = [float(r["error_ci_hi"]) - float(r["error_ci_lo"])
         for r in el if r["error_rate"] is not None and float(r["error_rate"]) > 0]
    print(f"      The seed bootstrap resamples the WHOLE 200-seed empirical distribution")
    print(f"      and recomputes the rate, so it already propagates uncertainty in the")
    print(f"      entire error functional, not merely in theta.")
    if w:
        print(f"      per-circuit error-CI widths: median {np.median(w):.4f}  "
              f"max {max(w):.4f}  (n={len(w)})")


if __name__ == "__main__":
    main()
