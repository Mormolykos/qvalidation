"""Derive per-circuit distribution statistics from a raw sweep. Regenerable from JSONL.

RULE (RESEARCH_LANDSCAPE.md sec 10): every number here must be reproducible from the
raw file alone. Nothing is computed during the sweep; nothing is cached here.

WHY SHAPE AND NOT JUST SIGMA
    The only published decision rule in this area (Pati & Simmhan, arXiv:2605.07876,
    analysis/statistical.py:247) is `gap > 2 * pooled_std`. A 2-sigma threshold carries
    an assumption about distribution shape. Two-qubit gate counts are discrete, bounded
    below, and may be skewed, so shape is the thing under test -- which means sigma
    alone cannot be the output.

USAGE
    python analyze.py --raw results/raw/sweep.jsonl --out results/summary/sweep.csv
"""

import argparse
import csv
import json
import os
from collections import defaultdict

import numpy as np

try:
    from scipy import stats as scipy_stats
except ImportError:  # scipy is optional; shape tests are skipped without it
    scipy_stats = None


def load_runs(path):
    runs = defaultdict(list)
    env = {}
    errors, budget_stops = [], []
    with open(path) as fh:
        for line in fh:
            row = json.loads(line)
            kind = row.get("record")
            if kind == "env":
                env = row
            elif kind == "run":
                runs[row["circuit"]].append(row)
            elif kind in ("run_error", "circuit_error"):
                errors.append(row)
            elif kind == "budget_stop":
                budget_stops.append(row)
    return env, runs, errors, budget_stops


def describe(values):
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    mean = float(arr.mean())
    lo, hi = float(arr.min()), float(arr.max())
    out = {
        "n_seeds": n,
        "distinct_values": int(len(set(values))),
        "min": lo,
        "max": hi,
        "mean": round(mean, 2),
        "median": round(float(np.median(arr)), 2),
        "std": round(float(arr.std(ddof=1)) if n > 1 else 0.0, 3),
        "iqr": round(float(np.percentile(arr, 75) - np.percentile(arr, 25)), 2),
        "cv_pct": round(float(arr.std(ddof=1) / mean * 100) if n > 1 and mean else 0.0, 3),
        "spread_pct": round((hi - lo) / lo * 100 if lo else 0.0, 2),
    }
    if scipy_stats is not None and n >= 3 and out["distinct_values"] > 1:
        out["skew"] = round(float(scipy_stats.skew(arr)), 3)
        out["kurtosis"] = round(float(scipy_stats.kurtosis(arr)), 3)
        if n >= 8:
            try:
                out["shapiro_p"] = round(float(scipy_stats.shapiro(arr).pvalue), 4)
            except Exception:
                out["shapiro_p"] = ""
        else:
            out["shapiro_p"] = ""
    else:
        out["skew"] = out["kurtosis"] = out["shapiro_p"] = ""
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--metric", default="two_q", choices=["two_q", "depth", "size"])
    args = parser.parse_args()

    env, runs, errors, budget_stops = load_runs(args.raw)

    rows = []
    for circuit, circuit_runs in sorted(runs.items()):
        values = [r[args.metric] for r in circuit_runs]
        stats = describe(values)
        distinct_hashes = len({r["qasm_sha256"] for r in circuit_runs})
        rows.append({
            "circuit": circuit,
            "n_qubits": circuit_runs[0]["n_qubits"],
            "metric": args.metric,
            "distinct_circuits": distinct_hashes,
            "median_seconds": round(float(np.median([r["seconds"] for r in circuit_runs])), 3),
            **stats,
        })

    rows.sort(key=lambda r: r["spread_pct"], reverse=True)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    spreads = [r["spread_pct"] for r in rows]
    n_flat = sum(1 for s in spreads if s < 1.0)
    n_mild = sum(1 for s in spreads if 1.0 <= s < 5.0)
    n_big = sum(1 for s in spreads if s >= 5.0)

    print(f"\n  qiskit {env.get('qiskit_version')} | opt_level={env.get('opt_level')} "
          f"| {env.get('topology')}")
    print(f"  {len(rows)} circuits analysed | metric = {args.metric}")
    print(f"  errors: {len(errors)} | budget stops: {len(budget_stops)}\n")

    print(f"  spread < 1%       : {n_flat:3d} circuits")
    print(f"  spread 1-5%       : {n_mild:3d} circuits")
    print(f"  spread >= 5%      : {n_big:3d} circuits")
    if spreads:
        print(f"  median spread     : {np.median(spreads):.2f}%")
        print(f"  max spread        : {max(spreads):.2f}%")

    print(f"\n  Top 15 by spread:")
    print(f"  {'circuit':<26s} {'n':>5s} {'seeds':>5s} {'min':>7s} {'max':>7s} "
          f"{'spread%':>8s} {'CV%':>7s} {'skew':>7s} {'shapiro_p':>10s}")
    for r in rows[:15]:
        print(f"  {r['circuit']:<26s} {r['n_qubits']:>5d} {r['n_seeds']:>5d} "
              f"{r['min']:>7.0f} {r['max']:>7.0f} {r['spread_pct']:>8.2f} "
              f"{r['cv_pct']:>7.2f} {str(r['skew']):>7s} {str(r['shapiro_p']):>10s}")

    print(f"\n  written: {args.out}")
    if errors:
        print(f"\n  {len(errors)} errors (first 5):")
        for e in errors[:5]:
            print(f"    {e.get('circuit')}: {e.get('error','')[:100]}")


if __name__ == "__main__":
    main()
