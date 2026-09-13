"""Priority A1 — does the ambiguity produce an ACTUAL WRONG DECISION on a real change?

THE QUESTION, AND WHY THE EARLIER WORK COULD NOT ANSWER IT
    sec 45 A1: "No real decision has been shown to be wrong." Everything up to now was
    either a synthetic injected effect (sec 32, withdrawn as a tautology; sec 42, a
    swept model) or the 2.0.0 -> 2.0.2 pair, whose real changes sit 15 points away from
    the +10% cut and therefore flip nothing.

    The real incident is NOT 2.0.0 -> 2.0.2. Issue #14402 compares **Qiskit 1.4.3
    against 2.0**, and reports bv_n140-linear +46%, bv_n280-linear +44%,
    knn_341-linear +44.060% (v1-v3 said +41%, a misquotation of the issue; see PAPER.md
    section 4.4). That is the version pair, the topology and the circuits where
    a wrong decision could actually have been made, and it had never been run.

DIRECTION IS FIXED BEFORE LOOKING
    baseline = 1.4.3 (earlier), candidate = 2.0.0 (later). Forward, as it happened.
    Not reversed, whatever that would do to the effect size.

THE FIVE CATEGORIES, KEPT SEPARATE
    1 seed variation observed          -- established, sec 27/28/30
    2 measurement ambiguity            -- established, sec 42
    3 decision INSTABILITY             -- 0.05 < P(call) < 0.95 for a circuit
    4 decision ERROR                   -- a verdict that is DEMONSTRABLY WRONG
    5 causal attribution to a commit   -- NOT attempted here

WHAT COUNTS AS (4), AND THE BAR IS DELIBERATELY HIGH
    A verdict is wrong only if the truth is not itself in doubt. So a circuit is a
    demonstrated decision error only when BOTH hold:

      (a) a bootstrap CI on the circuit's true mean change lies ENTIRELY on one side
          of the threshold -- the ground truth is not a boundary case; and
      (b) the protocol returns the OPPOSITE verdict with probability >= 0.05.

    Then the minority verdict is wrong about a change whose side is not in question,
    and the rate at which it occurs is the error rate. A circuit that merely straddles
    the cut is category (3), NOT (4), and is reported separately.

USAGE
    python decision_error.py --old results/raw/bp_large_linear_q143.jsonl \
        --new results/raw/bp_large_linear_q200.jsonl --topology linear \
        --out results/summary/decision_error_linear_143_200.csv
"""

import argparse
import csv
import json
import os

import numpy as np

from intervals import CI_LEVEL, exact_call_rate, load, wilson
from paired import exact_paired_rate

# The three tests #14402 names. Keys are Benchpress's OWN circuit names, which come
# from the QASM file stem and not the directory: the corpus directory is `knn_n341`
# but the circuit is `knn_341`, exactly as the issue's `knn_341-linear` test id spells
# it. An earlier draft here looked up `knn_n341`, found nothing, and would have
# reported one of the three decisive circuits as missing.
ISSUE_14402 = {"bv_n140": 0.4614, "bv_n280": 0.44, "knn_341": 0.41}


def change_ci(o, n, rng, b=5000):
    """Percentile CI on the true mean relative change, resampling SEEDS jointly
    (the arms share seeds 1000-1011, so the resample must carry pairs together)."""
    m = o.size
    vals = np.empty(b)
    for i in range(b):
        j = rng.integers(0, m, m)
        a, c = o[j], n[j]
        vals[i] = (c.mean() - a.mean()) / a.mean()
    lo, hi = np.percentile(vals, [(100 - CI_LEVEL) / 2, 100 - (100 - CI_LEVEL) / 2])
    return float(lo), float(hi)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--old", required=True, help="BASELINE = the EARLIER version")
    p.add_argument("--new", required=True, help="CANDIDATE = the LATER version")
    p.add_argument("--topology", required=True)
    p.add_argument("--threshold", type=float, default=0.10)
    p.add_argument("--k", type=int, default=3)
    p.add_argument("--min-seeds", type=int, default=12)
    p.add_argument("--error-rate-floor", type=float, default=0.05)
    p.add_argument("--seed", type=int, default=20260903)
    p.add_argument("--out")
    args = p.parse_args()

    old, v_old = load(args.old)
    new, v_new = load(args.new)
    rng = np.random.default_rng(args.seed)
    t, k = args.threshold, args.k

    print(f"\n  A1 — {args.topology}, BASELINE qiskit {v_old} -> CANDIDATE {v_new}, "
          f"k={k}, threshold {t:+.0%}")
    print(f"  direction fixed before measuring: earlier version is the baseline\n")

    rows = []
    for c in sorted(set(old) & set(new)):
        a, b = old[c], new[c]
        if len(a) < args.min_seeds or len(b) < args.min_seeds or len(a) != len(b):
            continue
        o, n = np.array(a, float), np.array(b, float)
        if not (o > 0).all():
            continue
        true_change = float((n.mean() - o.mean()) / o.mean())
        lo, hi = change_ci(o, n, rng)
        p_call = exact_call_rate(o, n, t, k)
        p_paired = exact_paired_rate(o, n, t, k)

        truth = ("REGRESSION" if lo > t else
                 "NO_REGRESSION" if hi < t else "TRUTH_UNRESOLVED")
        unstable = 0.05 < p_call < 0.95
        if truth == "REGRESSION":
            err_rate = 1.0 - p_call            # missing a real regression
            err_kind = "FALSE_NEGATIVE"
        elif truth == "NO_REGRESSION":
            err_rate = p_call                  # calling one that is not there
            err_kind = "FALSE_POSITIVE"
        else:
            err_rate, err_kind = float("nan"), "N/A"
        demonstrated = (truth != "TRUTH_UNRESOLVED"
                        and err_rate >= args.error_rate_floor)

        rows.append({
            "topology": args.topology, "circuit": c,
            "qiskit_baseline": v_old, "qiskit_candidate": v_new,
            "n_seeds": len(o), "k": k, "threshold": t,
            "true_change_pct": round(true_change * 100, 3),
            "true_change_ci_lo_pct": round(lo * 100, 3),
            "true_change_ci_hi_pct": round(hi * 100, 3),
            "ground_truth": truth,
            "p_call_unpaired": round(p_call, 4),
            "p_call_paired": round(p_paired, 4),
            "unstable_cat3": unstable,
            "error_kind": err_kind,
            "error_rate": None if np.isnan(err_rate) else round(err_rate, 4),
            "demonstrated_error_cat4": demonstrated,
            "in_issue_14402": c in ISSUE_14402,
        })

    n_tot = len(rows)
    cat3 = [r for r in rows if r["unstable_cat3"]]
    cat4 = [r for r in rows if r["demonstrated_error_cat4"]]
    unres = [r for r in rows if r["ground_truth"] == "TRUTH_UNRESOLVED"]
    w3 = wilson(len(cat3), n_tot)
    w4 = wilson(len(cat4), n_tot)

    print(f"  {n_tot} circuits with {args.min_seeds} seeds in both arms\n")
    print(f"  category 3  decision INSTABILITY (0.05 < P < 0.95):  "
          f"{len(cat3)}/{n_tot} = {len(cat3)/n_tot:.3f}  "
          f"Wilson [{w3[0]:.3f}, {w3[1]:.3f}]")
    print(f"  category 4  demonstrated decision ERROR:             "
          f"{len(cat4)}/{n_tot} = {len(cat4)/n_tot:.3f}  "
          f"Wilson [{w4[0]:.3f}, {w4[1]:.3f}]")
    print(f"              (truth CI entirely one side of the cut AND the opposite "
          f"verdict at rate >= {args.error_rate_floor:.0%})")
    print(f"  truth unresolved at n={args.min_seeds} (excluded from cat 4): "
          f"{len(unres)}/{n_tot}")

    if cat4:
        print(f"\n  ⛔ DEMONSTRATED WRONG DECISIONS")
        print(f"  {'circuit':<16s} {'true Δ':>8s} {'95% CI':>18s} {'verdict':>14s} "
              f"{'P(call)':>8s} {'error':>7s} {'paired':>7s}")
        for r in sorted(cat4, key=lambda r: -r["error_rate"]):
            ci = f"[{r['true_change_ci_lo_pct']:+.1f},{r['true_change_ci_hi_pct']:+.1f}]"
            print(f"  {r['circuit']:<16s} {r['true_change_pct']:>+7.1f}% {ci:>18s} "
                  f"{r['error_kind']:>14s} {r['p_call_unpaired']:>8.3f} "
                  f"{r['error_rate']:>6.1%} {r['p_call_paired']:>7.3f}")
    else:
        print(f"\n  NO demonstrated wrong decision on this pair. "
              f"Reported as a negative result.")

    print(f"\n  #14402's own reported cases")
    print(f"  {'circuit':<16s} {'issue Δ':>8s} {'measured Δ':>11s} {'95% CI':>18s} "
          f"{'P(call)':>8s} {'error':>7s}")
    for name, issue_pct in sorted(ISSUE_14402.items()):
        r = next((x for x in rows if x["circuit"] == name), None)
        if r is None:
            print(f"  {name:<16s} {issue_pct:>+7.1%}   NOT MEASURED — absent or "
                  f"under {args.min_seeds} seeds in this census")
            continue
        ci = f"[{r['true_change_ci_lo_pct']:+.1f},{r['true_change_ci_hi_pct']:+.1f}]"
        er = "—" if r["error_rate"] is None else f"{r['error_rate']:.1%}"
        print(f"  {name:<16s} {issue_pct:>+7.1%} {r['true_change_pct']:>+10.1f}% "
              f"{ci:>18s} {r['p_call_unpaired']:>8.3f} {er:>7s}")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
