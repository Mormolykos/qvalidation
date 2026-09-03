"""Priority 2 — the paired calibration column, attacked and replaced.

THE DEFECT (DEFECTS.md D-2.1 / D-2.2)
    `calibrate.py` builds its "paired" arm as

        idx = k random indices
        a   = sum(vals[i]        for i in idx) / k
        b   = sum(vals[i]*(1+e)  for i in idx) / k

    Both sides are the SAME k values; only b carries the multiplier. So

        b = (1/k) * sum_i v_i*(1+e) = (1+e) * (1/k) * sum_i v_i = (1+e)*a
        (b - a)/a = e            for every index set, every circuit, every k

    and the decision rule `(b-a)/a >= t` collapses to `e >= t`. The paired column is
    the indicator function 1[e >= t]. It has zero variance, it never touches a
    compiler, and it does not depend on the measured data AT ALL. Feeding it a real
    circuit, a constant vector, or pure noise returns identical numbers.

    `--prove` demonstrates exactly that, and shows the one row that is not a clean
    step (e == t) is floating-point residue: in exact rational arithmetic it is 1.

WHAT WAS CLAIMED ON THE STRENGTH OF IT — and is hereby withdrawn
    sec 32 : "passing seed_transpiler removes every false positive across all 51
             circuits and raises power at every effect size"
    sec 34 : "Pairing achieves 0.0% at k=1"
    Neither is a measurement. Both restate 1[e >= t].

THE REPLACEMENT — `--measure`
    We do not need a synthetic effect at all. We have the same 12 seeds run against
    two Qiskit versions, so the paired comparison can be MEASURED:

        unpaired : a = mean of k draws from OLD, b = mean of k INDEPENDENT draws
                   from NEW                                  <- what Benchpress does
        paired   : draw k seed indices ONCE, a = mean of OLD at those indices,
                   b = mean of NEW at the SAME indices       <- what seed_transpiler
                                                                would give you

    In the paired arm b is now the real 2.0.2 measurement at that seed, not a*(1+e).
    It carries genuine variance because the per-seed between-version change is
    heterogeneous (sec 31: cc_n32 ranges -45.76% .. -18.64% across seeds). Both arms
    are computed EXACTLY by enumerating all n**k index tuples -- no trials, no
    sampling noise in the point estimate.

    This is a calibration of the decision procedure against the real between-version
    change. It is NOT a claim about what caused that change (see sec 39).

THE OUTER INTERVAL, AND A CORRECTION TO intervals.py
    `intervals.py` resampled the two arms INDEPENDENTLY. That is wrong: both arms
    were produced by the SAME 12 seeds (1000..1011, verified aligned in both files),
    so the uncertainty "which seeds did we happen to draw" is common to the arms.
    The outer bootstrap must therefore resample SEED INDICES and carry (old_i, new_i)
    together. `--bootstrap-mode` runs it either way so the difference is visible
    rather than assumed.

USAGE
    python paired.py --prove
    python paired.py --measure --old results/raw/bp_large_linear_q200.jsonl \
        --new results/raw/bp_large_linear_q202.jsonl --topology linear \
        --out results/summary/paired_linear.csv
"""

import argparse
import csv
import json
import os
import random
from collections import defaultdict
from fractions import Fraction

import numpy as np

from intervals import (BOOTSTRAP_B, CI_LEVEL, _grid, exact_call_rate, k_means,
                       load, wilson)


# ----------------------------------------------------------------- part A: proof

def _synthetic_paired(vals, effect, threshold, k, trials, rng):
    """The defect itself, executed. Imported from calibrate.py rather than copied, so
    the proof cannot drift away from the code it is about -- and so that re-enabling
    the column anywhere makes this proof fail loudly instead of quietly agreeing."""
    from calibrate import detect_rate
    return detect_rate(vals, effect, threshold, k, trials, rng, paired=True)


def _exact_rational_paired(vals, effect, threshold, k):
    """The same arm in exact arithmetic. Returns the single value (b-a)/a takes."""
    e = Fraction(effect).limit_denominator(10 ** 6)
    idx = [0, 1, min(2, len(vals) - 1)][:k]
    a = sum(Fraction(int(vals[i])) for i in idx) / k
    b = sum(Fraction(int(vals[i])) * (1 + e) for i in idx) / k
    ratio = (b - a) / a
    return ratio, ratio >= Fraction(threshold).limit_denominator(10 ** 6)


def prove(args):
    real = [161608, 161608, 161608, 118440, 161608, 161608,
            161608, 118440, 161608, 118440, 161608, 161608]      # qft_n320, linear, 2.0.2
    datasets = [
        ("qft_n320 (real)", real),
        ("constant 1000s", [1000] * 12),
        ("extreme 1 vs 1e6", [1] * 11 + [10 ** 6]),
        ("uniform noise", [random.Random(7).randint(50, 5000) for _ in range(12)]),
    ]
    effects = [0.0, 0.02, 0.05, 0.10, 0.15, 0.30]
    t, k, trials = args.threshold, args.k, args.trials

    print(f"\n  PROOF: calibrate.py's paired arm, threshold {t:+.0%}, k={k}, "
          f"{trials} trials\n")
    header = "  " + f"{'true effect':>12s}" + "".join(f"{n:>20s}" for n, _ in datasets)
    print(header)
    print("  " + "-" * (len(header) - 2))

    table = {}
    for eff in effects:
        cells = []
        for name, vals in datasets:
            rng = random.Random(20260903)
            cells.append(_synthetic_paired(vals, eff, t, k, trials, rng))
        table[eff] = cells
        print(f"  {eff:>11.0%}" + "".join(f"{c:>20.4f}" for c in cells))

    print(f"\n  Every row is CONSTANT across four datasets that share nothing:")
    disagree = [eff for eff, cells in table.items() if len(set(cells)) > 1]
    for eff, cells in table.items():
        mark = "  <-- varies" if len(set(cells)) > 1 else ""
        print(f"    effect {eff:>5.0%}: {sorted(set(cells))}{mark}")

    print(f"\n  The rate is 1[effect >= threshold], not a measurement.")
    if disagree:
        print(f"  Rows that vary at all: {[f'{e:.0%}' for e in disagree]} "
              f"-- only e == t, and only in floating point.")

    print(f"\n  Exact rational arithmetic on the same arm:")
    for eff in effects:
        ratio, called = _exact_rational_paired(real, eff, t, k)
        print(f"    effect {eff:>5.0%}: (b-a)/a = {ratio}  = {float(ratio):.6f}  "
              f"called={called}")
    print(f"\n  (b-a)/a equals the injected effect EXACTLY, with no data dependence.")
    print(f"  In exact arithmetic the e == t row is 1.000; the {table[0.10][0]:.4f} "
          f"in the table is float residue.\n")

    for eff, cells in table.items():
        if eff != t:
            assert len(set(cells)) == 1, f"effect {eff} varied: {cells}"
        assert all(c == (1.0 if eff > t else 0.0) for c in cells) or eff == t, \
            f"effect {eff} is not the step function: {cells}"
    print("  ASSERTIONS PASS: the paired column is data-independent. "
          "It is withdrawn as evidence.\n")


# ----------------------------------------------------- part B: real measurement

def exact_paired_rate(old_vals, new_vals, threshold, k):
    """P(call) when the SAME k seed indices produce both arms. Exact over n**k."""
    o = np.asarray(old_vals, dtype=float)
    n = np.asarray(new_vals, dtype=float)
    if o.size != n.size:
        raise ValueError("paired comparison needs equal-length, seed-aligned arms")
    if k == 1:
        a, b = o, n
    else:
        g = _grid(o.size, k)
        a, b = o[g].mean(axis=1), n[g].mean(axis=1)
    ok = a != 0
    return float(((b[ok] - a[ok]) / a[ok] >= threshold).sum()) / int(ok.sum())


def bootstrap_both(old_vals, new_vals, threshold, k, rng, mode, b=BOOTSTRAP_B):
    """Outer interval for the unpaired and paired rates.

    mode='shared'      : resample seed INDICES once, carry (old_i, new_i) together.
                         Correct here -- both arms came from the same 12 seeds.
    mode='independent' : resample each arm separately (what intervals.py did).
    """
    o = np.asarray(old_vals, dtype=float)
    n = np.asarray(new_vals, dtype=float)
    m = o.size
    u = np.empty(b)
    p = np.empty(b)
    for i in range(b):
        if mode == "shared":
            j = rng.integers(0, m, m)
            ro, rn = o[j], n[j]
        else:
            ro, rn = o[rng.integers(0, m, m)], n[rng.integers(0, m, m)]
        u[i] = exact_call_rate(ro, rn, threshold, k)
        p[i] = exact_paired_rate(ro, rn, threshold, k)
    lo, hi = (100 - CI_LEVEL) / 2, 100 - (100 - CI_LEVEL) / 2
    return (float(np.percentile(u, lo)), float(np.percentile(u, hi)),
            float(np.percentile(p, lo)), float(np.percentile(p, hi)))


def measure(args):
    old, v_old = load(args.old)
    new, v_new = load(args.new)
    rng = np.random.default_rng(args.seed)

    rows = []
    for circuit in sorted(set(old) & set(new)):
        a, b = old[circuit], new[circuit]
        if len(a) < args.min_seeds or len(b) < args.min_seeds:
            continue
        if len(a) != len(b):
            continue
        mean_a, mean_b = float(np.mean(a)), float(np.mean(b))
        true_change = (mean_b - mean_a) / mean_a if mean_a else 0.0
        u = exact_call_rate(a, b, args.threshold, args.k)
        p = exact_paired_rate(a, b, args.threshold, args.k)
        ulo, uhi, plo, phi = bootstrap_both(a, b, args.threshold, args.k, rng,
                                            args.bootstrap_mode)
        # the ground truth for THIS circuit: does the full-sample change reach the cut?
        band = args.boundary_band / 100.0
        if abs(true_change - args.threshold) <= band:
            truth = "BOUNDARY"
        elif true_change >= args.threshold:
            truth = "REGRESSION"
        else:
            truth = "NO_REGRESSION"
        rows.append({
            "topology": args.topology, "circuit": circuit,
            "qiskit_old": v_old, "qiskit_new": v_new,
            "n_seeds": len(a), "k": args.k, "threshold": args.threshold,
            "true_change_pct": round(true_change * 100, 3), "ground_truth": truth,
            "unpaired_p": round(u, 4), "unpaired_lo": round(ulo, 4),
            "unpaired_hi": round(uhi, 4),
            "paired_p": round(p, 4), "paired_lo": round(plo, 4),
            "paired_hi": round(phi, 4),
            "paired_is_degenerate": p in (0.0, 1.0),
            "bootstrap_mode": args.bootstrap_mode,
            "method_point": "exact enumeration over n**k index tuples",
            "method_interval": f"percentile bootstrap over seeds, B={BOOTSTRAP_B}, "
                               f"{CI_LEVEL}%, {args.bootstrap_mode} resampling",
        })

    if not rows:
        raise SystemExit("ABORT: no circuit has full, equal-length arms in both files")

    print(f"\n  {args.topology}: qiskit {v_old} -> {v_new}, k={args.k}, "
          f"threshold {args.threshold:+.0%}, {len(rows)} circuits")
    n_tuples = rows[0]["n_seeds"] ** args.k
    print(f"  point: exact over {n_tuples} index tuples per circuit  |  "
          f"interval: bootstrap over seeds, {args.bootstrap_mode}\n")

    for truth in ("NO_REGRESSION", "REGRESSION", "BOUNDARY"):
        grp = [r for r in rows if r["ground_truth"] == truth]
        if not grp:
            continue
        label = {"NO_REGRESSION": "FALSE POSITIVE rate (true change below cut)",
                 "REGRESSION": "POWER (true change at or above cut)",
                 "BOUNDARY": "on the cut -- excluded from both, D-1.6"}[truth]
        mu = sum(r["unpaired_p"] for r in grp) / len(grp)
        mp = sum(r["paired_p"] for r in grp) / len(grp)
        print(f"  {label}")
        print(f"    {len(grp)} circuits | mean unpaired {mu:.4f} | mean paired {mp:.4f}")
        bad_u = [r for r in grp if (r["unpaired_p"] >= 0.05) != (truth == "REGRESSION")]
        bad_p = [r for r in grp if (r["paired_p"] >= 0.05) != (truth == "REGRESSION")]
        wu = wilson(len(bad_u), len(grp))
        wp = wilson(len(bad_p), len(grp))
        print(f"    circuits erring >=5% of the time: "
              f"unpaired {len(bad_u)}/{len(grp)} Wilson [{wu[0]:.3f}, {wu[1]:.3f}]  |  "
              f"paired {len(bad_p)}/{len(grp)} Wilson [{wp[0]:.3f}, {wp[1]:.3f}]")
        print()

    nondegenerate = [r for r in rows if not r["paired_is_degenerate"]]
    print(f"  Paired column is NOT a step function on real data: "
          f"{len(nondegenerate)}/{len(rows)} circuits take a value strictly "
          f"between 0 and 1.")
    if nondegenerate:
        print(f"\n  {'circuit':<18s} {'true d':>8s} {'unpaired':>9s} "
              f"{'95% CI':>16s} {'paired':>8s} {'95% CI':>16s}")
        for r in sorted(nondegenerate, key=lambda r: -r["paired_p"])[:12]:
            cu = f"[{r['unpaired_lo']:.2f},{r['unpaired_hi']:.2f}]"
            cp = f"[{r['paired_lo']:.2f},{r['paired_hi']:.2f}]"
            print(f"  {r['circuit']:<18s} {r['true_change_pct']:>+7.1f}% "
                  f"{r['unpaired_p']:>9.3f} {cu:>16s} {r['paired_p']:>8.3f} {cp:>16s}")

    disagree = [r for r in rows
                if (r["unpaired_p"] >= 0.5) != (r["paired_p"] >= 0.5)]
    print(f"\n  Circuits where paired and unpaired reach OPPOSITE majority verdicts: "
          f"{len(disagree)}")
    for r in disagree:
        print(f"    {r['circuit']:<18s} true {r['true_change_pct']:>+7.1f}%  "
              f"unpaired {r['unpaired_p']:.3f}  paired {r['paired_p']:.3f}  "
              f"({r['ground_truth']})")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


# ------------------------------------------------- part C: the direction-free band
#
# WHY PART C EXISTS
#     `--measure` above found that the corpus-level instability rate is almost entirely
#     an artifact of WHICH VERSION IS THE BASELINE. Same data, same circuits, same
#     threshold, opposite assignment:
#
#         2.0.0 -> 2.0.2 (what actually happened) : heavy-hex 0 of 52 unstable
#         2.0.2 -> 2.0.0 (what the record ran)    : heavy-hex 24 of 52 unstable
#
#     The cause is arithmetic, not physics. A one-sided rule "flag if the candidate is
#     >= +10%" measures the DISTANCE from the true change to the cut. A circuit that
#     really moved -5% sits 15 points from +10%; reverse the arms and the same circuit
#     sits 5 points away. Any claim of the form "X% of circuits are unstable" is
#     therefore a statement about where this particular version pair happened to land,
#     and it is not a property of the harness, the corpus or the topology.
#
# THE STATISTIC THAT DOES NOT DEPEND ON THE DIRECTION
#     Ask instead: how large must a real change be before the protocol can resolve it?
#     Sweep a synthetic true change r and find the interval of r over which the call
#     rate sits between 0.05 and 0.95. That interval -- the AMBIGUITY BAND -- is a
#     property of the circuit's seed noise and the threshold, not of the version pair.
#
#     The synthetic candidate is built as   new_i = old_i * r * rho_i   where rho is the
#     MEASURED per-seed change between 2.0.0 and 2.0.2, re-centred to mean 1. Both arms
#     see the identical candidate; the only difference is how they are compared:
#         unpaired: independent index draws each side   (Benchpress)
#         paired:   one index draw used for both sides  (seed_transpiler)
#     The paired arm is NOT a tautology here -- rho varies per seed, so the paired ratio
#     varies with the index set. That is the whole repair.

BAND_LO, BAND_HI = 0.05, 0.95


def _candidate(old, rho, r):
    return np.asarray(old, dtype=float) * r * rho


def _rate(old, rho, r, t, k, paired):
    new = _candidate(old, rho, r)
    return (exact_paired_rate(old, new, t, k) if paired
            else exact_call_rate(old, new, t, k))


def _solve(old, rho, target, t, k, paired, lo=0.5, hi=2.0, iters=40):
    """Smallest r with call-rate >= target. Monotone in r, so bisection is exact
    to the tolerance printed. Returns nan if the target is unreachable in [lo, hi]."""
    if _rate(old, rho, hi, t, k, paired) < target:
        return float("nan")
    if _rate(old, rho, lo, t, k, paired) >= target:
        return lo
    for _ in range(iters):
        mid = (lo + hi) / 2
        if _rate(old, rho, mid, t, k, paired) >= target:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def band(args):
    old_all, v_old = load(args.old)
    new_all, v_new = load(args.new)
    rows = []
    for circuit in sorted(set(old_all) & set(new_all)):
        a, b = old_all[circuit], new_all[circuit]
        if len(a) < args.min_seeds or len(b) < args.min_seeds or len(a) != len(b):
            continue
        o = np.asarray(a, dtype=float)
        n = np.asarray(b, dtype=float)
        if not (o > 0).all():
            continue
        ratio = n / o
        rho = ratio / ratio.mean()                    # measured residual, re-centred
        rec = {"topology": args.topology, "circuit": circuit,
               "qiskit_old": v_old, "qiskit_new": v_new,
               "n_seeds": len(a), "k": args.k, "threshold": args.threshold,
               "measured_change_pct": round((n.mean() / o.mean() - 1) * 100, 3),
               "rho_spread_pct": round((rho.max() - rho.min()) * 100, 3)}
        for paired in (False, True):
            tag = "paired" if paired else "unpaired"
            lo = _solve(o, rho, BAND_LO, args.threshold, args.k, paired)
            hi = _solve(o, rho, BAND_HI, args.threshold, args.k, paired)
            rec[f"{tag}_r05_pct"] = None if np.isnan(lo) else round((lo - 1) * 100, 3)
            rec[f"{tag}_r95_pct"] = None if np.isnan(hi) else round((hi - 1) * 100, 3)
            rec[f"{tag}_band_pp"] = (None if (np.isnan(lo) or np.isnan(hi))
                                     else round((hi - lo) * 100, 3))
        rows.append(rec)

    # A circuit whose measured per-seed change is IDENTICAL at every seed has rho == 1
    # exactly, and then the paired ratio is r for every index set -- the same identity
    # that made calibrate.py's paired column worthless. Those circuits must not be
    # counted as evidence that pairing works; on them it is true by construction.
    het = [r for r in rows if r["rho_spread_pct"] > 0.0]
    deg = [r for r in rows if r["rho_spread_pct"] == 0.0]

    def widths(tag, src=None):
        src = rows if src is None else src
        return [r[f"{tag}_band_pp"] for r in src if r[f"{tag}_band_pp"] is not None]

    wu, wp = widths("unpaired"), widths("paired")
    print(f"\n  AMBIGUITY BAND, {args.topology}: how big must a change be to be "
          f"resolved?")
    print(f"  qiskit {v_old} -> {v_new} supplies the per-seed residual only. "
          f"k={args.k}, threshold {args.threshold:+.0%}")
    print(f"  {len(rows)} circuits | band = width in percentage points over which "
          f"P(call) runs 0.05 -> 0.95\n")
    for tag, w in (("unpaired (Benchpress)", wu), ("paired (seed_transpiler)", wp)):
        if not w:
            print(f"  {tag:<26s} no circuit resolved in the search range")
            continue
        q = np.percentile(w, [25, 50, 75])
        print(f"  {tag:<26s} n={len(w):<3d} median {q[1]:6.2f} pp   "
              f"IQR [{q[0]:.2f}, {q[2]:.2f}]   max {max(w):.2f} pp")
    print(f"\n  ! {len(deg)}/{len(rows)} circuits are byte-identical at every seed "
          f"between {v_old} and {v_new} (rho spread 0).")
    print(f"    On those the paired band is 0.00 pp BY CONSTRUCTION, not by "
          f"measurement -- the same\n    identity that invalidated calibrate.py's "
          f"paired column. They are excluded below.")
    hu, hp = widths("unpaired", het), widths("paired", het)
    if hu and hp:
        mu, mp = float(np.median(hu)), float(np.median(hp))
        ratio = mu / mp if mp else float("inf")
        print(f"\n  On the {len(het)} circuits where the version change really does "
              f"vary by seed:")
        print(f"    unpaired median {mu:.2f} pp   paired median {mp:.2f} pp   "
              f"pairing narrows the band {ratio:.1f}x")
        worse = [r for r in het
                 if r["paired_band_pp"] is not None and r["unpaired_band_pp"] is not None
                 and r["paired_band_pp"] >= r["unpaired_band_pp"] - 1e-9]
        print(f"    circuits pairing does NOT help: {len(worse)}/{len(het)}"
              + (f" ({', '.join(r['circuit'] for r in worse[:6])})" if worse else ""))
    over = [r for r in rows if (r["unpaired_band_pp"] or 0) >= args.wide_band]
    w_lo, w_hi = wilson(len(over), len(rows))
    print(f"  Circuits whose unpaired band is >= {args.wide_band:g} pp: "
          f"{len(over)}/{len(rows)} = {len(over)/len(rows):.3f} "
          f"Wilson 95% CI [{w_lo:.3f}, {w_hi:.3f}]")

    if args.band_ci:
        arms = []
        for circuit in sorted(set(old_all) & set(new_all)):
            a, b = old_all[circuit], new_all[circuit]
            if len(a) < args.min_seeds or len(b) < args.min_seeds or len(a) != len(b):
                continue
            o = np.asarray(a, dtype=float)
            if not (o > 0).all():
                continue
            arms.append((o, np.asarray(b, dtype=float)))
        rng = np.random.default_rng(args.seed)
        med_u, med_p, prop = [], [], []
        for _ in range(args.band_ci):
            j = rng.integers(0, arms[0][0].size, arms[0][0].size)   # shared seed draw
            bu, bp, wide, tot = [], [], 0, 0
            for o, n in arms:
                ro, rn = o[j], n[j]
                ratio = rn / ro
                rho = ratio / ratio.mean()
                u_lo = _solve(ro, rho, BAND_LO, args.threshold, args.k, False, iters=20)
                u_hi = _solve(ro, rho, BAND_HI, args.threshold, args.k, False, iters=20)
                tot += 1
                if not (np.isnan(u_lo) or np.isnan(u_hi)):
                    w = (u_hi - u_lo) * 100
                    if w >= args.wide_band:
                        wide += 1
                    if ratio.max() != ratio.min():
                        bu.append(w)
                        p_lo = _solve(ro, rho, BAND_LO, args.threshold, args.k, True,
                                      iters=20)
                        p_hi = _solve(ro, rho, BAND_HI, args.threshold, args.k, True,
                                      iters=20)
                        if not (np.isnan(p_lo) or np.isnan(p_hi)):
                            bp.append((p_hi - p_lo) * 100)
            if bu:
                med_u.append(np.median(bu))
            if bp:
                med_p.append(np.median(bp))
            prop.append(wide / tot)
        lo, hi = (100 - CI_LEVEL) / 2, 100 - (100 - CI_LEVEL) / 2
        print(f"\n  Seed bootstrap, B={args.band_ci}, shared resampling, "
              f"{CI_LEVEL:.0f}% percentile intervals:")
        for name, s in (("median unpaired band (heterogeneous)", med_u),
                        ("median paired band (heterogeneous)", med_p),
                        (f"fraction with unpaired band >= {args.wide_band:g} pp", prop)):
            if s:
                a_, b_ = np.percentile(s, [lo, hi])
                unit = "" if name.startswith("fraction") else " pp"
                print(f"    {name:<44s} [{a_:.3f}{unit}, {b_:.3f}{unit}]")

    worst = sorted((r for r in rows if r["unpaired_band_pp"] is not None),
                   key=lambda r: -r["unpaired_band_pp"])[:10]
    print(f"\n  {'circuit':<18s} {'unpaired band':>14s} {'paired band':>12s} "
          f"{'rho spread':>11s}")
    for r in worst:
        pb = "n/a" if r["paired_band_pp"] is None else f"{r['paired_band_pp']:.2f} pp"
        print(f"  {r['circuit']:<18s} {r['unpaired_band_pp']:>11.2f} pp {pb:>12s} "
              f"{r['rho_spread_pct']:>10.2f}%")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prove", action="store_true")
    parser.add_argument("--measure", action="store_true")
    parser.add_argument("--band", action="store_true")
    parser.add_argument("--band-ci", type=int, default=0,
                        help="bootstrap replicates for the band aggregates (0 = skip)")
    parser.add_argument("--wide-band", type=float, default=5.0,
                        help="report the fraction of circuits whose unpaired band is "
                             "at least this many percentage points wide")
    parser.add_argument("--old")
    parser.add_argument("--new")
    parser.add_argument("--topology", default="linear")
    parser.add_argument("--threshold", type=float, default=0.10)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--trials", type=int, default=4000)
    parser.add_argument("--min-seeds", type=int, default=12)
    parser.add_argument("--boundary-band", type=float, default=3.0)
    parser.add_argument("--bootstrap-mode", choices=["shared", "independent"],
                        default="shared")
    parser.add_argument("--seed", type=int, default=20260903)
    parser.add_argument("--out")
    args = parser.parse_args()

    if args.prove:
        prove(args)
    if args.measure:
        if not (args.old and args.new):
            raise SystemExit("--measure needs --old and --new")
        measure(args)
    if args.band:
        if not (args.old and args.new):
            raise SystemExit("--band needs --old and --new")
        band(args)
    if not (args.prove or args.measure or args.band):
        parser.error("pass --prove, --measure and/or --band")


if __name__ == "__main__":
    main()
