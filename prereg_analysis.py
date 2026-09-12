"""Analysis for the pre-registered multi-circuit replication. PREREGISTRATION.md §5.

⚠ THIS FILE WAS WRITTEN AND COMMITTED BEFORE THE DATA EXISTED. The git commit adding it
   predates the commit adding results/raw/prereg/*.jsonl. That ordering is the point:
   the analysis could not have been tuned to the result, and anyone can check the order
   with `git log --diff-filter=A -- prereg_analysis.py results/raw/prereg`.

IMPLEMENTS, WITHOUT DEVIATION
    §5.1 estimated long-run change = ratio of arm means; 95% percentile bootstrap over
         seeds, resampled JOINTLY across the paired arms, B = 4000. Never called ground
         truth.
    §5.2 verdict: REGRESSION if the interval lies entirely above the threshold,
         NO_REGRESSION if entirely below, else UNRESOLVED. Unresolved circuits are
         EXCLUDED from the error-rate analysis and reported as unresolved. Never
         reclassified.
    §5.3 error rate: false negative 1 - P(call) for REGRESSION, false positive P(call)
         for NO_REGRESSION. 95% seed bootstrap, B = 400.
    §5.4 BOUNDARY flag when the estimated change is within 3 pp of the threshold;
         reported separately, excluded from the headline.

    PRIMARY ENDPOINT: proportion of non-boundary, resolved circuits whose error interval
    EXCLUDES ZERO, with a Wilson 95% interval.

    SECONDARY: the distribution of error rates; the primary endpoint at
    k in {1,3,5,8,10,20}; and at thresholds {5%, 10%, 15%, 20%}.

    §7.1 EVERY selected circuit is reported, including zero-error, unresolved and
         crashed ones.

INTEGRITY GUARD ADDED 2026-09-04 (finding F2) — NOT AN ANALYSIS CHANGE
    analyse() now verifies that the two arms carry the IDENTICAL seed set before
    pairing them, and reports status MISALIGNED_SEEDS if they do not. §5.1's joint
    resampling assumes position i is the same seed in both arms; that assumption held
    for all 39 pre-registered pairs (verified: 0 mismatches, 0 duplicate seeds) but
    was never enforced. The guard does not fire on the committed data, and the output
    CSV is byte-for-byte unchanged -- verified by regenerating it after the change.

USAGE
    python prereg_analysis.py --out results/summary/prereg_heavy-hex.csv
"""

import argparse
import csv
import json
import os

import numpy as np

from deep import exact_rate_int, mc_rate
from intervals import wilson

RAW = os.path.join("results", "raw", "prereg")
BOOT_TRUTH = 4000
BOOT_ERR = 400
BOOT_ERR_MC = 400_000
BOUNDARY_PP = 3.0
# An endpoint this close to the cut IS the cut. See analyse(): the threshold is
# inclusive and an exact tie is UNRESOLVED, which float arithmetic does not give for
# free -- 110/100 - 1 is 0.10000000000000009, not 0.1.
TIE_EPS = 1e-9
EXACT_MAX_N = 200          # exact enumeration is affordable at n=200 for k<=3


def load_seeded(circuit, ver, topo="heavy-hex"):
    """(seeds, values, version), both arrays ordered by seed. The seed list is kept so
    analyse() can VERIFY the two arms are seed-aligned instead of assuming it (F2)."""
    path = os.path.join(RAW, f"{circuit}_{topo}_q{ver}.jsonl")
    if not os.path.isfile(path):
        return None, None, None
    vals, version = [], None
    for line in open(path):
        r = json.loads(line)
        if r.get("qiskit_version"):
            version = r["qiskit_version"]
        if r.get("record") == "run":
            vals.append((r["seed"], r["two_q"]))
    if not vals:
        return None, None, version
    ordered = sorted(vals)
    return (np.array([s for s, _ in ordered], dtype=np.int64),
            np.array([v for _, v in ordered], dtype=np.int64), version)


def load(circuit, ver, topo="heavy-hex"):
    """(values, version). Thin wrapper kept for callers that do not need the seeds."""
    _, vals, version = load_seeded(circuit, ver, topo)
    return vals, version


def rate(o, n, t, k, rng):
    if k <= 3 and o.size <= EXACT_MAX_N:
        return exact_rate_int(o, n, t, k)
    return mc_rate(o, n, t, k, rng, 4_000_000)


def analyse(circuit, t, k, rng):
    s_o, o, v_o = load_seeded(circuit, "143")
    s_n, n, v_n = load_seeded(circuit, "200")
    if o is None or n is None:
        return {"circuit": circuit, "status": "MISSING_OR_CRASHED",
                "qiskit_baseline": v_o, "qiskit_candidate": v_n}
    # §5.1 resamples the two arms JOINTLY, which is only correct if position i means the
    # same seed in both. THREE ways that can fail, and all three are now refused rather
    # than worked around (F2 2026-09-04; hardened 2026-09-08 after an external audit):
    #
    #   unequal lengths  The first version of this guard took m = min(len(a), len(b)) and
    #                    compared only the first m seeds. A 200-seed arm paired with an
    #                    accidentally truncated 199-seed arm whose first 199 seeds match
    #                    therefore PASSED, and the good arm was then silently cut to 199
    #                    by `o, n = o[:m], n[:m]`. The guard was weaker than its own
    #                    comment claimed: it detected mispairing but not truncation.
    #   duplicate seeds  A seed recorded twice makes "identical seed sets" meaningless
    #                    and double-weights one measurement inside the bootstrap.
    #   different seeds  Equal length, different identities.
    #
    # A malformed pair is REPORTED per §7.1 with a machine-readable reason, never
    # analysed, and NEVER truncated. load_seeded() returns seeds sorted, so identical
    # sets imply identical arrays and a whole-array comparison is exact.
    if s_o.size != s_n.size:
        return {"circuit": circuit, "status": "MISALIGNED_SEEDS",
                "reason": f"unequal arm lengths: baseline {s_o.size}, candidate {s_n.size}",
                "n_seeds": 0, "qiskit_baseline": v_o, "qiskit_candidate": v_n}
    if np.unique(s_o).size != s_o.size or np.unique(s_n).size != s_n.size:
        return {"circuit": circuit, "status": "DUPLICATE_SEEDS",
                "reason": (f"duplicate seed ids: baseline {s_o.size - np.unique(s_o).size}, "
                           f"candidate {s_n.size - np.unique(s_n).size}"),
                "n_seeds": 0, "qiskit_baseline": v_o, "qiskit_candidate": v_n}
    if not np.array_equal(s_o, s_n):
        return {"circuit": circuit, "status": "MISALIGNED_SEEDS",
                "reason": "arms carry different seed identities",
                "n_seeds": 0, "qiskit_baseline": v_o, "qiskit_candidate": v_n}

    m = int(o.size)
    if m == 0 or not (o > 0).all():
        return {"circuit": circuit, "status": "UNUSABLE_ZERO_OR_EMPTY", "n_seeds": m}

    change = float(n.mean() / o.mean() - 1)
    ch = np.empty(BOOT_TRUTH)
    r1 = np.random.default_rng(20260904)
    for i in range(BOOT_TRUTH):
        j = r1.integers(0, m, m)
        ch[i] = n[j].mean() / o[j].mean() - 1
    c_lo, c_hi = np.percentile(ch, [2.5, 97.5])

    # §5.2 declares the threshold INCLUSIVE and an exact tie UNRESOLVED. A naive float
    # comparison breaks that: with A = 100 and B = 110 the change is mathematically
    # exactly +10%, but 110/100 - 1 evaluates to 0.10000000000000009, which is > 0.10, so
    # an exact tie was classified REGRESSION (Astra A12). The guard below treats an
    # endpoint within TIE_EPS of the cut as sitting ON it, so it is not strictly above or
    # below and the circuit is UNRESOLVED.
    #
    # This cannot change any recorded verdict: the closest CI endpoint to the threshold
    # anywhere in the 39 circuits is 2.3e-3, over two million times TIE_EPS away.
    above = (c_lo - t) > TIE_EPS
    below = (t - c_hi) > TIE_EPS
    verdict = ("REGRESSION" if above else
               "NO_REGRESSION" if below else "UNRESOLVED")
    boundary = abs(change - t) * 100 <= BOUNDARY_PP

    row = {"circuit": circuit, "status": "OK", "n_seeds": int(m),
           "qiskit_baseline": v_o, "qiskit_candidate": v_n,
           "k": k, "threshold": t,
           "est_long_run_change_pct": round(change * 100, 4),
           "change_ci_lo_pct": round(float(c_lo) * 100, 4),
           "change_ci_hi_pct": round(float(c_hi) * 100, 4),
           "verdict": verdict,
           "distance_to_cut_pp": round(abs(change - t) * 100, 3),
           "boundary": boundary}

    if verdict == "UNRESOLVED":
        row.update({"p_call": None, "error_kind": "N/A", "error_rate": None,
                    "error_ci_lo": None, "error_ci_hi": None,
                    "error_excludes_zero": False})
        return row

    p = rate(o, n, t, k, rng)
    err = (1 - p) if verdict == "REGRESSION" else p
    errs = np.empty(BOOT_ERR)
    r2 = np.random.default_rng(20260905)
    for i in range(BOOT_ERR):
        j = r2.integers(0, m, m)
        pc = mc_rate(o[j], n[j], t, k, r2, BOOT_ERR_MC)
        errs[i] = (1 - pc) if verdict == "REGRESSION" else pc
    e_lo, e_hi = np.percentile(errs, [2.5, 97.5])
    row.update({"p_call": round(p, 6),
                "error_kind": "FALSE_NEGATIVE" if verdict == "REGRESSION"
                              else "FALSE_POSITIVE",
                "error_rate": round(err, 6),
                "error_ci_lo": round(float(e_lo), 6),
                "error_ci_hi": round(float(e_hi), 6),
                "error_excludes_zero": bool(e_lo > 0)})
    return row


def endpoint(rows):
    """PRIMARY: proportion of non-boundary RESOLVED circuits whose error CI excludes 0."""
    elig = [r for r in rows if r.get("status") == "OK"
            and r["verdict"] != "UNRESOLVED" and not r["boundary"]]
    hit = [r for r in elig if r["error_excludes_zero"]]
    lo, hi = wilson(len(hit), len(elig)) if elig else (float("nan"), float("nan"))
    return hit, elig, lo, hi


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--threshold", type=float, default=0.10)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--circuits", default="_selected.txt")
    ap.add_argument("--out")
    args = ap.parse_args()
    rng = np.random.default_rng(20260906)
    circuits = [c.strip() for c in open(args.circuits) if c.strip()]

    print(f"\n  PRE-REGISTERED REPLICATION — {len(circuits)} circuits, heavy-hex, "
          f"1.4.3 -> 2.0.0, k={args.k}, threshold {args.threshold:+.0%}")
    print(f"  analysis frozen in PREREGISTRATION.md §5; this file predates the data\n")

    rows = [analyse(c, args.threshold, args.k, rng) for c in circuits]

    print(f"  {'circuit':<16s} {'est change':>11s} {'95% CI':>20s} {'verdict':>14s} "
          f"{'error':>9s} {'95% CI':>18s} {'>0':>4s}")
    for r in sorted(rows, key=lambda r: -(r.get("error_rate") or -1)):
        if r.get("status") != "OK":
            print(f"  {r['circuit']:<16s} {r.get('status'):>11s}")
            continue
        ci = f"[{r['change_ci_lo_pct']:+.2f},{r['change_ci_hi_pct']:+.2f}]"
        if r["error_rate"] is None:
            print(f"  {r['circuit']:<16s} {r['est_long_run_change_pct']:>+10.2f}% "
                  f"{ci:>20s} {r['verdict']:>14s} {'—':>9s} {'—':>18s} {'—':>4s}")
            continue
        eci = f"[{r['error_ci_lo']:.4f},{r['error_ci_hi']:.4f}]"
        mark = "YES" if r["error_excludes_zero"] else "no"
        bd = " B" if r["boundary"] else ""
        print(f"  {r['circuit']:<16s} {r['est_long_run_change_pct']:>+10.2f}% {ci:>20s} "
              f"{r['verdict']:>14s} {r['error_rate']:>9.4f} {eci:>18s} {mark:>4s}{bd}")

    ok = [r for r in rows if r.get("status") == "OK"]
    unres = [r for r in ok if r["verdict"] == "UNRESOLVED"]
    bound = [r for r in ok if r["boundary"] and r["verdict"] != "UNRESOLVED"]
    hit, elig, lo, hi = endpoint(rows)

    print(f"\n  reported: {len(rows)} selected | {len(ok)} usable | "
          f"{len(unres)} UNRESOLVED (excluded per §5.2) | "
          f"{len(bound)} BOUNDARY (excluded per §5.4)")
    print(f"\n  ⭐ PRIMARY ENDPOINT: {len(hit)}/{len(elig)} = "
          f"{len(hit)/len(elig) if elig else float('nan'):.4f}  "
          f"Wilson 95% CI [{lo:.4f}, {hi:.4f}]")
    label = ("REFUTED as a class" if lo <= 0 else
             "WEAK" if len(hit) / len(elig) < 0.10 else
             "STRONG" if len(hit) / len(elig) >= 0.25 else "SUPPORTED")
    print(f"     pre-registered label (§6): {label}")

    if elig:
        er = [r["error_rate"] for r in elig]
        print(f"\n  error-rate distribution over the {len(elig)} eligible circuits:")
        print(f"     median {np.median(er):.4f}  p75 {np.percentile(er,75):.4f}  "
              f"p90 {np.percentile(er,90):.4f}  max {max(er):.4f}")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        keys = sorted({k for r in rows for k in r})
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
