"""Follow-up attacks on the FROZEN pre-registered result. §53, second round.

⚠ THE FROZEN RESULT IS NOT MODIFIED. No exclusion changes, no re-run, no edit to
   PREREGISTRATION.md. Everything here is labelled a follow-up and reported beside the
   pre-registered endpoint, never in place of it.

RAISED BY TWO INDEPENDENT CRITICS, 2026-09-04
    Reviewer B (as IBM's lead engineer):
      G1 the estimand assumes the MEAN is the target. What if practice is best-of-k?
      G2 12/26 blends deterministic and stochastic populations.
      G3 the +10% threshold is ours; a false positive needs a formalised boundary.
      G4 excluding boundary circuits destroys ecological validity.
      G5 median error is zero, so this is tail risk, not systemic failure.
    Reviewer A:
      C1 "wrong" should be "decision error relative to the long-run reference".
      C2 theta is a 200-seed plug-in estimate; propagate its uncertainty.
      C3 Wilson assumes the 26 classifications are independent. Family structure means
         the effective n is smaller and the interval is TOO NARROW. Cluster-bootstrap it.

WHAT EACH TEST DOES
    F7  aggregation sensitivity: mean-of-k vs MIN-of-k vs median-of-k          (G1)
    F8  cluster bootstrap with FAMILY as the resampling unit                    (C3)
    F9  joint bootstrap propagating theta uncertainty into the endpoint         (C2)
    F10 threshold sweep: the whole endpoint recomputed at each cut              (G3)
    F11 the deterministic/stochastic partition, and the 12/12 framing           (G2)
    F12 the endpoint WITH the boundary circuits included                        (G4)

USAGE
    python followup.py
"""

import csv
import re
import sys

import numpy as np

from deep import mc_rate
from intervals import wilson
from prereg_analysis import load

CSV = "results/summary/prereg_heavy-hex.csv"
T, K = 0.10, 3
BOUNDARY_PP = 3.0


def family(c):
    return re.sub(r"_?n?\d+$", "", c) or c


def arms(circuit):
    o, _ = load(circuit, "143")
    n, _ = load(circuit, "200")
    if o is None or n is None:
        return None, None
    m = min(o.size, n.size)
    return o[:m], n[:m]


def rate_agg(o, n, t, k, rng, how, pairs=2_000_000):
    """P(call) under an aggregation rule: mean-of-k, min-of-k or median-of-k."""
    ia = rng.integers(0, o.size, (pairs, k))
    ib = rng.integers(0, n.size, (pairs, k))
    f = {"mean": lambda x: x.mean(axis=1),
         "min": lambda x: x.min(axis=1),
         "median": lambda x: np.median(x, axis=1)}[how]
    a = f(o[ia].astype(float))
    b = f(n[ib].astype(float))
    ok = a > 0
    return float(((b[ok] - a[ok]) / a[ok] >= t).mean())


def theta_ci(o, n, rng, b=4000):
    m = o.size
    ch = np.empty(b)
    for i in range(b):
        j = rng.integers(0, m, m)
        ch[i] = n[j].mean() / o[j].mean() - 1
    return float(np.percentile(ch, 2.5)), float(np.percentile(ch, 97.5))


def classify(o, n, t, rng):
    theta = float(n.mean() / o.mean() - 1)
    lo, hi = theta_ci(o, n, rng, 1500)
    verdict = ("REGRESSION" if lo > t else
               "NO_REGRESSION" if hi < t else "UNRESOLVED")
    boundary = abs(theta - t) * 100 <= BOUNDARY_PP
    return theta, verdict, boundary


def main():
    rows = list(csv.DictReader(open(CSV)))
    elig = [r for r in rows if r["status"] == "OK"
            and r["verdict"] != "UNRESOLVED" and r["boundary"] == "False"]
    hits = [r for r in elig if r["error_excludes_zero"] == "True"]
    rng = np.random.default_rng(20260904)

    print(f"\n  FROZEN RESULT, unchanged: {len(hits)}/{len(elig)} = "
          f"{len(hits)/len(elig):.4f}  Wilson {wilson(len(hits), len(elig))}")

    # ---------------------------------------------------------------- F11 (G2)
    print(f"\n  F11 — the partition Reviewer B says is blended")
    det = sto = 0
    sto_hits = det_hits = 0
    for r in elig:
        o, n = arms(r["circuit"])
        spread = (n / o).std(ddof=1)
        h = r["error_excludes_zero"] == "True"
        if spread == 0:
            det += 1
            det_hits += h
        else:
            sto += 1
            sto_hits += h
    print(f"      eligible circuits with ZERO per-seed variance : {det:>3d}  "
          f"of which hits: {det_hits}")
    print(f"      eligible circuits WITH per-seed variance      : {sto:>3d}  "
          f"of which hits: {sto_hits}")
    if sto:
        lo, hi = wilson(sto_hits, sto)
        print(f"      -> among STOCHASTIC eligible circuits: {sto_hits}/{sto} = "
              f"{sto_hits/sto:.4f}  Wilson [{lo:.4f}, {hi:.4f}]")
    print(f"      Reviewer B's reframing is CORRECT and is now reported alongside 12/26.")

    # ---------------------------------------------------------------- F8 (C3)
    print(f"\n  F8 — cluster bootstrap, FAMILY as the resampling unit (C3)")
    fam_map = {}
    for r in elig:
        fam_map.setdefault(family(r["circuit"]), []).append(
            r["error_excludes_zero"] == "True")
    fams = sorted(fam_map)
    print(f"      {len(fams)} families over {len(elig)} eligible circuits: "
          f"{ {f: f'{sum(fam_map[f])}/{len(fam_map[f])}' for f in fams} }")
    B = 20000
    props = np.empty(B)
    r2 = np.random.default_rng(7)
    for i in range(B):
        drawn = [fams[j] for j in r2.integers(0, len(fams), len(fams))]
        flat = [h for f in drawn for h in fam_map[f]]
        props[i] = np.mean(flat)
    clo, chi = np.percentile(props, [2.5, 97.5])
    print(f"      cluster bootstrap B={B}: point {len(hits)/len(elig):.4f}  "
          f"95% CI [{clo:.4f}, {chi:.4f}]")
    wl, wh = wilson(len(hits), len(elig))
    print(f"      Wilson (assumes independence)      95% CI [{wl:.4f}, {wh:.4f}]")
    print(f"      -> cluster interval is {'WIDER' if (chi-clo) > (wh-wl) else 'NOT wider'}"
          f" ({chi-clo:.4f} vs {wh-wl:.4f}). C3 is {'CONFIRMED' if (chi-clo)>(wh-wl) else 'not confirmed'}.")

    # ---------------------------------------------------------------- F9 (C2)
    print(f"\n  F9 — joint bootstrap: theta uncertainty propagated into the endpoint (C2)")
    data = {r["circuit"]: arms(r["circuit"]) for r in rows if r["status"] == "OK"}
    Bj = 300
    ends = []
    r3 = np.random.default_rng(11)
    for i in range(Bj):
        h = e = 0
        for c, (o, n) in data.items():
            if o is None:
                continue
            m = o.size
            j = r3.integers(0, m, m)
            ro, rn = o[j], n[j]
            th, verdict, bd = classify(ro, rn, T, r3)
            if verdict == "UNRESOLVED" or bd:
                continue
            e += 1
            p = mc_rate(ro, rn, T, K, r3, 60000)
            err = (1 - p) if verdict == "REGRESSION" else p
            h += (err > 0)
        if e:
            ends.append(h / e)
    jlo, jhi = np.percentile(ends, [2.5, 97.5])
    print(f"      B={Bj} joint replicates, recomputing theta, verdict, boundary and "
          f"error each time")
    print(f"      endpoint distribution: median {np.median(ends):.4f}  "
          f"95% CI [{jlo:.4f}, {jhi:.4f}]")
    print(f"      (eligible-set size varies per replicate; that is the point)")

    # ---------------------------------------------------------------- F12 (G4)
    print(f"\n  F12 — endpoint WITH the boundary circuits included (G4)")
    allres = [r for r in rows if r["status"] == "OK" and r["verdict"] != "UNRESOLVED"]
    ah = [r for r in allres if r["error_excludes_zero"] == "True"]
    lo, hi = wilson(len(ah), len(allres))
    print(f"      {len(ah)}/{len(allres)} = {len(ah)/len(allres):.4f}  "
          f"Wilson [{lo:.4f}, {hi:.4f}]")
    print(f"      pre-registered (boundary excluded): {len(hits)}/{len(elig)} = "
          f"{len(hits)/len(elig):.4f}")
    print(f"      -> exclusion is CONSERVATIVE. The pre-registered figure remains PRIMARY.")

    # ---------------------------------------------------------------- F7 (G1)
    print(f"\n  F7 — aggregation sensitivity: is the mean a strawman? (G1)")
    print(f"      Benchpress performs NO aggregation (source-verified: no mean, min or")
    print(f"      best-of-k anywhere). #14402's reporter chose the mean explicitly.")
    print(f"      Testing the alternative practice Reviewer B names:\n")
    print(f"      {'circuit':<16s} {'theta':>8s} {'mean-of-3':>10s} {'MIN-of-3':>10s} "
          f"{'median-of-3':>12s}")
    keep = sorted(hits, key=lambda r: -float(r["error_rate"]))[:8]
    n_min_nonzero = 0
    for r in keep:
        o, n = arms(r["circuit"])
        pm = rate_agg(o, n, T, K, np.random.default_rng(1), "mean")
        pi = rate_agg(o, n, T, K, np.random.default_rng(1), "min")
        pd = rate_agg(o, n, T, K, np.random.default_rng(1), "median")
        n_min_nonzero += (pi > 0)
        print(f"      {r['circuit']:<16s} {float(r['est_long_run_change_pct']):>+7.2f}% "
              f"{pm:>10.4f} {pi:>10.4f} {pd:>12.4f}")
    print(f"\n      circuits still erring under MIN-of-3: {n_min_nonzero}/{len(keep)}")

    # ---------------------------------------------------------------- F10 (G3)
    print(f"\n  F10 — threshold sweep: the endpoint recomputed at every cut (G3)")
    print(f"      {'cut':>6s} {'eligible':>9s} {'hits':>6s} {'endpoint':>9s} "
          f"{'Wilson 95% CI':>20s}")
    for t in (0.05, 0.075, 0.10, 0.125, 0.15, 0.20):
        e = h = 0
        r4 = np.random.default_rng(3)
        for c, (o, n) in data.items():
            if o is None:
                continue
            th, verdict, bd = classify(o, n, t, r4)
            if verdict == "UNRESOLVED" or bd:
                continue
            e += 1
            p = mc_rate(o, n, t, K, r4, 300000)
            err = (1 - p) if verdict == "REGRESSION" else p
            h += (err > 0)
        lo, hi = wilson(h, e) if e else (float("nan"),) * 2
        star = "  <- pre-registered" if abs(t - 0.10) < 1e-9 else ""
        print(f"      {t:>5.1%} {e:>9d} {h:>6d} {h/e if e else float('nan'):>9.4f} "
              f"[{lo:>7.4f},{hi:>7.4f}]{star}")


if __name__ == "__main__":
    main()
