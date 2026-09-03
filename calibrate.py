"""Calibrate the regression detector: false-positive and false-negative rates.

WHAT THIS ANSWERS
    Sections 30-31 establish that unseeded comparison produces wrong verdicts on real
    data. That is a demonstration, not a calibration. Both independent critics asked for
    the same missing piece:

        "validate a reproducible regression-audit procedure against synthetic
         regressions, estimating false-positive/false-negative behaviour and
         calibrated power"                                    -- ChatGPT, sec 23 C4

    So: take each circuit's REAL measured seed distribution, inject a regression of
    KNOWN size, and ask how often the protocol detects it.

WHY INJECT AFTER COMPILATION
    Gemini (sec 23 G3) pointed out that injecting a synthetic regression before or
    during transpilation lets the optimiser alter it, so the "known" effect size is not
    known. Applying it to the recorded observable afterwards makes the injected delta
    exact by construction. That is what happens here: the effect is a multiplier on a
    measured two-qubit gate count, never a modification of a circuit.

    The cost of that choice, stated plainly: this calibrates the DECISION PROCEDURE
    given realistic noise. It does not model how a real code change would interact with
    routing. Those are different questions and only the first is claimed.

THE TWO ARMS
    unpaired : draw k seeds for A and k INDEPENDENT seeds for B  -- what Benchpress does
    paired   : draw k seed INDICES and use the same ones for A and B -- what passing
               seed_transpiler would give you

    At a true effect of ZERO, any call is a false positive. At a true effect at or above
    the threshold, any miss is a false negative.

USAGE
    python calibrate.py --raw results/raw/bp_large_linear_q202.jsonl --threshold 0.10
"""

import argparse
import csv
import json
import os
import random
from collections import defaultdict


def load(path):
    values, version = defaultdict(list), None
    with open(path) as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("qiskit_version"):
                version = row["qiskit_version"]
            if row.get("record") == "run":
                values[row["circuit"]].append((row["seed"], row["two_q"]))
    if version is None:
        raise SystemExit(f"ABORT: {path} records no qiskit_version.")
    return {c: [v for _, v in sorted(vs)] for c, vs in values.items()}, version


def detect_rate(vals, effect, threshold, k, trials, rng, paired):
    """Fraction of trials calling a regression when the true effect is `effect`."""
    n, hits = len(vals), 0
    for _ in range(trials):
        if paired:
            idx = [rng.randrange(n) for _ in range(k)]
            a = sum(vals[i] for i in idx) / k
            b = sum(vals[i] * (1 + effect) for i in idx) / k
        else:
            a = sum(rng.choice(vals) for _ in range(k)) / k
            b = sum(rng.choice(vals) * (1 + effect) for _ in range(k)) / k
        if a and (b - a) / a >= threshold:
            hits += 1
    return hits / trials


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True)
    parser.add_argument("--threshold", type=float, default=0.10)
    parser.add_argument("--runs-per-version", type=int, default=3)
    parser.add_argument("--trials", type=int, default=4000)
    parser.add_argument("--min-seeds", type=int, default=12,
                        help="Skip circuits with thin arms rather than let them dilute "
                             "the aggregate")
    parser.add_argument("--seed", type=int, default=20260903)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    effects = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30]
    vals_by_circuit, version = load(args.raw)
    usable = {c: v for c, v in vals_by_circuit.items() if len(v) >= args.min_seeds}
    rng = random.Random(args.seed)

    print(f"\n  qiskit {version} | threshold {args.threshold:+.0%} | "
          f"k={args.runs_per_version} runs/version | {args.trials} trials")
    print(f"  {len(usable)} circuits with >= {args.min_seeds} seeds "
          f"(of {len(vals_by_circuit)})\n")

    rows = []
    for circuit, vals in sorted(usable.items()):
        row = {"circuit": circuit, "n_seeds": len(vals)}
        for eff in effects:
            row[f"unpaired_{eff:g}"] = round(
                detect_rate(vals, eff, args.threshold, args.runs_per_version,
                            args.trials, rng, paired=False), 4)
            row[f"paired_{eff:g}"] = round(
                detect_rate(vals, eff, args.threshold, args.runs_per_version,
                            args.trials, rng, paired=True), 4)
        rows.append(row)

    def mean(key):
        return sum(r[key] for r in rows) / len(rows)

    print(f"  Detection rate averaged over {len(rows)} circuits")
    print(f"  {'true effect':>12s} {'UNPAIRED':>10s} {'PAIRED':>10s}   interpretation")
    for eff in effects:
        u, p = mean(f"unpaired_{eff:g}"), mean(f"paired_{eff:g}")
        if eff == 0.0:
            note = "FALSE POSITIVE rate"
        elif eff < args.threshold:
            note = "should be near 0 (sub-threshold)"
        elif eff == args.threshold:
            note = "at threshold"
        else:
            note = f"POWER (miss rate = {1-u:.1%} unpaired)"
        print(f"  {eff:>11.0%} {u:>10.3f} {p:>10.3f}   {note}")

    fp_u = mean("unpaired_0")
    fp_p = mean("paired_0")
    print(f"\n  FALSE POSITIVE at zero real change: "
          f"unpaired {fp_u:.1%}  vs  paired {fp_p:.1%}")

    worst = sorted(rows, key=lambda r: -r["unpaired_0"])[:8]
    print(f"\n  Worst circuits by false-positive rate (true effect = 0):")
    print(f"  {'circuit':<24s} {'unpaired':>9s} {'paired':>8s}")
    for r in worst:
        print(f"  {r['circuit']:<24s} {r['unpaired_0']:>9.3f} {r['paired_0']:>8.3f}")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
