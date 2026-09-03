"""Does seed variance flip a version-to-version regression call?

THE QUESTION THIS SETTLES
    Everything measured so far establishes that Benchpress's compilation is unseeded
    and that the resulting spread is large on ~1 circuit in 4. That is a fact without
    a consequence. Both independent critics said the same thing: variance alone is not
    publishable, because Qiskit already documents that its pass managers are stochastic.

    What would make it matter is a DECISION FLIP -- a case where the same two compiler
    versions, on the same circuit, are judged "regressed" or "fine" depending only on
    which seeds happened to come up.

HOW A REGRESSION CALL IS ACTUALLY MADE
    In Qiskit issue #14402 the per-test figures were percentage increases in two-qubit
    gate count between two versions, and the concern was stated as "there should not be
    double-digit gate count increases". So the operational rule is:

        call_regression(a, b) := (b - a) / a >= threshold        (default 0.10)

    where `a` is the old version's count and `b` the new version's.

    Benchpress runs unseeded, so each version's number is a single draw from that
    circuit's seed distribution. We therefore evaluate the call over ALL pairs of
    draws (12 x 12 = 144 per circuit) and ask how often it comes out each way.

    We also simulate the actual protocol used in #14402: THREE runs per version,
    averaged. That is the realistic case, and it is the one that matters.

CLASSIFICATION (pre-registered before looking at the two-version data)
    STABLE_REGRESSION : >= 95% of draws call a regression
    STABLE_CLEAN      : <= 5%  of draws call a regression
    UNSTABLE          : anything in between -- the verdict depends on the seed

    The headline is the count of UNSTABLE circuits. A single one is a demonstrated
    decision flip; zero is an honest negative result that the calls are robust.

USAGE
    python flip_analysis.py --old results/raw/bp_large_linear_q200.jsonl \
        --new results/raw/bp_large_linear_q202.jsonl --threshold 0.10
"""

import argparse
import csv
import itertools
import json
import os
import random
from collections import defaultdict


def load(path):
    """Return {circuit: [two_q, ...]} plus the qiskit version that produced them."""
    values = defaultdict(list)
    version = None
    with open(path) as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("qiskit_version"):
                version = row["qiskit_version"]
            if row.get("record") == "run":
                values[row["circuit"]].append(row["two_q"])
    if version is None:
        raise SystemExit(
            f"ABORT: {path} does not record a qiskit_version. A measurement file that "
            f"cannot name its own toolchain is not evidence. Re-run the census.")
    return values, version


def classify(fraction, lo=0.05, hi=0.95):
    if fraction >= hi:
        return "STABLE_REGRESSION"
    if fraction <= lo:
        return "STABLE_CLEAN"
    return "UNSTABLE"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old", required=True, help="Census from the OLDER version")
    parser.add_argument("--new", required=True, help="Census from the NEWER version")
    parser.add_argument("--threshold", type=float, default=0.10,
                        help="Relative increase counted as a regression (#14402 used "
                             "'double-digit percentages', i.e. 0.10)")
    parser.add_argument("--runs-per-version", type=int, default=3,
                        help="#14402 used 3 runs per version, averaged")
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260902,
                        help="RNG seed for the bootstrap, so this analysis is itself "
                             "reproducible")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    old, v_old = load(args.old)
    new, v_new = load(args.new)
    rng = random.Random(args.seed)

    shared = sorted(set(old) & set(new))
    print(f"\n  OLD = qiskit {v_old}   NEW = qiskit {v_new}")
    print(f"  {len(shared)} circuits in both censuses | "
          f"regression threshold = {args.threshold:+.0%}")
    print(f"  protocol simulated: {args.runs_per_version} run(s) per version, averaged, "
          f"{args.bootstrap} bootstrap draws\n")

    rows = []
    for circuit in shared:
        a_vals, b_vals = old[circuit], new[circuit]
        if len(a_vals) < 2 or len(b_vals) < 2:
            continue

        # (1) Every single-draw pair -- the exhaustive case.
        pairs = list(itertools.product(a_vals, b_vals))
        single_hits = sum(1 for a, b in pairs if a and (b - a) / a >= args.threshold)
        single_frac = single_hits / len(pairs)

        # (2) The protocol actually used in #14402: k runs per version, averaged.
        k = args.runs_per_version
        boot_hits = 0
        for _ in range(args.bootstrap):
            a = sum(rng.choice(a_vals) for _ in range(k)) / k
            b = sum(rng.choice(b_vals) for _ in range(k)) / k
            if a and (b - a) / a >= args.threshold:
                boot_hits += 1
        boot_frac = boot_hits / args.bootstrap

        mean_a = sum(a_vals) / len(a_vals)
        mean_b = sum(b_vals) / len(b_vals)
        rows.append({
            "circuit": circuit,
            "n_old": len(a_vals), "n_new": len(b_vals),
            "old_min": min(a_vals), "old_max": max(a_vals),
            "new_min": min(b_vals), "new_max": max(b_vals),
            "old_mean": round(mean_a, 1), "new_mean": round(mean_b, 1),
            "mean_change_pct": round((mean_b - mean_a) / mean_a * 100, 2) if mean_a else 0,
            "p_call_single": round(single_frac, 4),
            "p_call_k_runs": round(boot_frac, 4),
            "verdict_single": classify(single_frac),
            "verdict_k_runs": classify(boot_frac),
        })

    unstable_single = [r for r in rows if r["verdict_single"] == "UNSTABLE"]
    unstable_k = [r for r in rows if r["verdict_k_runs"] == "UNSTABLE"]

    print(f"  === VERDICT, single run per version ===")
    print(f"    STABLE_REGRESSION : {sum(1 for r in rows if r['verdict_single']=='STABLE_REGRESSION'):3d}")
    print(f"    STABLE_CLEAN      : {sum(1 for r in rows if r['verdict_single']=='STABLE_CLEAN'):3d}")
    print(f"    UNSTABLE          : {len(unstable_single):3d}   <-- decision depends on the seed")

    print(f"\n  === VERDICT, {args.runs_per_version} runs per version averaged (#14402 protocol) ===")
    print(f"    STABLE_REGRESSION : {sum(1 for r in rows if r['verdict_k_runs']=='STABLE_REGRESSION'):3d}")
    print(f"    STABLE_CLEAN      : {sum(1 for r in rows if r['verdict_k_runs']=='STABLE_CLEAN'):3d}")
    print(f"    UNSTABLE          : {len(unstable_k):3d}   <-- decision depends on the seed")

    if unstable_k:
        print(f"\n  Circuits whose regression call is NOT stable under reseeding:")
        print(f"  {'circuit':<24s} {'old range':>15s} {'new range':>15s} "
              f"{'mean Δ':>8s} {'P(call)':>8s}")
        for r in sorted(unstable_k, key=lambda x: -x["p_call_k_runs"]):
            print(f"  {r['circuit']:<24s} "
                  f"{str(r['old_min'])+'-'+str(r['old_max']):>15s} "
                  f"{str(r['new_min'])+'-'+str(r['new_max']):>15s} "
                  f"{r['mean_change_pct']:>7.1f}% {r['p_call_k_runs']:>8.2f}")
    else:
        print(f"\n  NO UNSTABLE CIRCUITS. Every regression call survives reseeding at "
              f"this threshold.\n  That is a negative result and it must be reported "
              f"as one.")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        rows.sort(key=lambda r: -r["p_call_k_runs"])
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
