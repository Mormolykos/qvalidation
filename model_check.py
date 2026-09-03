"""Priority A2 — is the multiplicative noise model actually true?

THE ASSUMPTION UNDER TEST
    sec 42's ambiguity band builds a synthetic candidate as

        new_i = old_i * r * rho_i          rho = measured per-seed change, mean 1

    Two things are assumed and neither was ever checked:

      (M1) the between-version change is MULTIPLICATIVE -- it scales the observable
           rather than shifting it, so the per-seed ratio is independent of the
           circuit's magnitude at that seed;
      (M2) the residual SHAPE rho is stable as the change MAGNITUDE r varies -- i.e.
           a big code change scatters across seeds in the same relative pattern as a
           small one.

⛔ WHY THE OBVIOUS VALIDATION IS WORTHLESS
    "Set r to the observed change and check the model reproduces the observed call
    rate" is a TAUTOLOGY. rho is defined as ratio/mean(ratio), so at r = mean(ratio)
    the synthetic candidate is identically the real one. It would pass on any data.
    This is the same trap as D-2.1 and it must not be reported as validation.

    (M2) can only be tested OUT OF SAMPLE, and that needs a THIRD version. Fitting rho
    on one version pair and predicting a DIFFERENT pair -- one with a much larger real
    change -- is a genuine falsification test. Qiskit 1.4.3 exists for that reason:
    1.4.3 -> 2.0.0 is the real incident from issue #14402 and is a far larger change
    than 2.0.0 -> 2.0.2.

WHAT IS REPORTED
    M1a  Spearman correlation between old_i and ratio_i, per circuit.
         ⚠ THE SIGN DEPENDS ON THE DIRECTION OF THE CHANGE and an earlier draft of
         this file got it wrong. Under an additive model new_i = old_i + d, the ratio
         is 1 + d/old_i, whose derivative in old_i is -d/old_i**2. So additive predicts
         a POSITIVE correlation when d < 0 (an improvement) and a NEGATIVE one when
         d > 0. Multiplicative predicts a constant ratio, hence ~0 -- and slightly
         negative in practice, since old_i sits in the ratio's denominator.
         The test therefore compares the observed sign against sign(-d) per circuit,
         computed from that circuit's own measured change, not against a fixed claim.
    M1b  multiplicative vs additive fit, compared as residual sum of squares on the
         same scale, per circuit. Neither is assumed to win.
    M1c  variance scaling: CV(new)/CV(old) (should be ~1 if multiplicative) against
         SD(new)/SD(old) (should be ~1 if additive).
    M2   out-of-sample: fit rho on pair A, predict pair B's call rate and band, and
         compare to pair B's MEASURED values.

USAGE
    python model_check.py --pair 200:202 --pair 143:200 --topology linear
    python model_check.py --oos-fit 200:202 --oos-test 143:200 --topology linear
"""

import argparse
import csv
import os

import numpy as np
from scipy import stats

from intervals import exact_call_rate, load
from paired import BAND_HI, BAND_LO, _solve, exact_paired_rate

VERSIONS = {"143": "1.4.3", "200": "2.0.0", "202": "2.0.2"}


def raw(topo, ver):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "results", "raw", f"bp_large_{topo}_q{ver}.jsonl")


def arms(topo, old_ver, new_ver, min_seeds=12):
    o, vo = load(raw(topo, old_ver))
    n, vn = load(raw(topo, new_ver))
    out = []
    for c in sorted(set(o) & set(n)):
        a, b = o[c], n[c]
        if len(a) >= min_seeds and len(b) >= min_seeds and len(a) == len(b):
            a, b = np.array(a, float), np.array(b, float)
            if (a > 0).all() and (b > 0).all():
                out.append((c, a, b))
    return out, vo, vn


# ------------------------------------------------------------------ M1: shape tests

def fit_tests(topo, old_ver, new_ver):
    data, vo, vn = arms(topo, old_ver, new_ver)
    rows = []
    for c, o, n in data:
        ratio = n / o
        # M1a -- is the ratio independent of the magnitude?
        if len(set(o.tolist())) > 1 and len(set(ratio.tolist())) > 1:
            rho_s, p_s = stats.spearmanr(o, ratio)
        else:
            rho_s, p_s = float("nan"), float("nan")
        # M1b -- multiplicative (n = c*o) vs additive (n = o + d), same scale
        c_mult = (o * n).sum() / (o * o).sum()          # least squares through origin
        d_add = float((n - o).mean())
        rss_mult = float(((n - c_mult * o) ** 2).sum())
        rss_add = float(((n - (o + d_add)) ** 2).sum())
        # M1c -- variance scaling
        cv_o = o.std(ddof=1) / o.mean() if o.mean() else float("nan")
        cv_n = n.std(ddof=1) / n.mean() if n.mean() else float("nan")
        rows.append({
            "topology": topo, "circuit": c,
            "qiskit_old": vo, "qiskit_new": vn, "n_seeds": len(o),
            "mean_change_pct": round((n.mean() / o.mean() - 1) * 100, 3),
            "spearman_old_vs_ratio": None if np.isnan(rho_s) else round(float(rho_s), 4),
            "spearman_p": None if np.isnan(p_s) else round(float(p_s), 4),
            "rss_multiplicative": round(rss_mult, 3),
            "rss_additive": round(rss_add, 3),
            "better_fit": ("tie" if abs(rss_mult - rss_add) < 1e-9 else
                           "multiplicative" if rss_mult < rss_add else "additive"),
            "cv_old": round(float(cv_o), 5), "cv_new": round(float(cv_n), 5),
            "cv_ratio": round(float(cv_n / cv_o), 4) if cv_o else None,
            "sd_ratio": round(float(n.std(ddof=1) / o.std(ddof=1)), 4)
                        if o.std(ddof=1) else None,
        })
    return rows, vo, vn


def report_fit(rows, vo, vn, topo):
    var = [r for r in rows if r["cv_ratio"] is not None and r["cv_old"] > 0]
    print(f"\n  M1 — {topo}, qiskit {vo} -> {vn}, {len(rows)} circuits "
          f"({len(var)} with seed variance in both arms)")

    usable = [r for r in rows if r["spearman_old_vs_ratio"] is not None]
    if usable:
        sp = [r["spearman_old_vs_ratio"] for r in usable]
        # additive predicts sign(-d); d is the mean change, so sign(-d) = +1 when the
        # new version REDUCED the count. Computed per circuit from its own change.
        match = sum(1 for r in usable
                    if np.sign(r["spearman_old_vs_ratio"])
                    == np.sign(-r["mean_change_pct"]) and r["mean_change_pct"] != 0)
        sig = sum(1 for r in usable if r["spearman_p"] is not None
                  and r["spearman_p"] < 0.05)
        print(f"    M1a ratio vs magnitude: median Spearman {np.median(sp):+.3f}  |  "
              f"p<0.05 in {sig}/{len(usable)}")
        print(f"        sign matches the ADDITIVE prediction sign(-d) in "
              f"{match}/{len(usable)} circuits")
        print(f"        (multiplicative predicts a constant ratio, hence ~0 or "
              f"slightly negative)")

    varying = [r for r in rows if r["cv_old"] > 0 or r["cv_new"] > 0]
    mult = sum(1 for r in varying if r["better_fit"] == "multiplicative")
    add = sum(1 for r in varying if r["better_fit"] == "additive")
    tie = len(varying) - mult - add
    print(f"    M1b fit (circuits with any variance, n={len(varying)}): "
          f"multiplicative wins {mult}  |  additive wins {add}  |  tie {tie}")

    if var:
        cvr = [r["cv_ratio"] for r in var]
        sdr = [r["sd_ratio"] for r in var if r["sd_ratio"] is not None]
        print(f"    M1c CV(new)/CV(old) median {np.median(cvr):.3f}  "
              f"(multiplicative predicts 1.00)")
        print(f"        SD(new)/SD(old) median {np.median(sdr):.3f}  "
              f"(additive predicts 1.00)")


# --------------------------------------------------------- M2: out-of-sample test

def oos(topo, fit_pair, test_pair, threshold, k):
    """Fit rho on `fit_pair`, predict `test_pair`, compare to what it measured."""
    fo, fn = fit_pair
    to, tn = test_pair
    fit_data, fvo, fvn = arms(topo, fo, fn)
    test_data, tvo, tvn = arms(topo, to, tn)
    fit_rho, fit_change = {}, {}
    for c, o, n in fit_data:
        r = n / o
        fit_rho[c] = r / r.mean()
        fit_change[c] = float(n.mean() / o.mean() - 1.0)

    rows = []
    for c, o, n in test_data:
        if c not in fit_rho:
            continue
        rho_fit = fit_rho[c]
        rho_true = (n / o) / (n / o).mean()
        r_obs = float(n.mean() / o.mean())

        pred_new = o * r_obs * rho_fit          # same magnitude, BORROWED shape
        rows.append({
            "topology": topo, "circuit": c,
            "fit_pair": f"{fvo}->{fvn}", "test_pair": f"{tvo}->{tvn}",
            "test_change_pct": round((r_obs - 1) * 100, 3),
            "fit_change_pct": round(fit_change[c] * 100, 3),
            "rho_spread_fit_pct": round(float(rho_fit.max() - rho_fit.min()) * 100, 3),
            "rho_spread_true_pct": round(float(rho_true.max() - rho_true.min()) * 100,
                                         3),
            "actual_unpaired": round(exact_call_rate(o, n, threshold, k), 4),
            "pred_unpaired": round(exact_call_rate(o, pred_new, threshold, k), 4),
            "actual_paired": round(exact_paired_rate(o, n, threshold, k), 4),
            "pred_paired": round(exact_paired_rate(o, pred_new, threshold, k), 4),
        })
        lo_t = _solve(o, rho_true, BAND_LO, threshold, k, False)
        hi_t = _solve(o, rho_true, BAND_HI, threshold, k, False)
        lo_f = _solve(o, rho_fit, BAND_LO, threshold, k, False)
        hi_f = _solve(o, rho_fit, BAND_HI, threshold, k, False)
        rows[-1]["actual_band_pp"] = (None if np.isnan(lo_t) or np.isnan(hi_t)
                                      else round((hi_t - lo_t) * 100, 3))
        rows[-1]["pred_band_pp"] = (None if np.isnan(lo_f) or np.isnan(hi_f)
                                    else round((hi_f - lo_f) * 100, 3))
    return rows


def report_oos(rows, threshold, k):
    if not rows:
        print("\n  M2 — no circuits shared by both pairs")
        return
    print(f"\n  M2 OUT OF SAMPLE — rho fitted on {rows[0]['fit_pair']}, "
          f"used to predict {rows[0]['test_pair']}")
    print(f"  threshold {threshold:+.0%}, k={k}, {len(rows)} circuits. "
          f"This is the only non-circular test of the model.\n")

    du = [r["pred_unpaired"] - r["actual_unpaired"] for r in rows]
    dp = [r["pred_paired"] - r["actual_paired"] for r in rows]
    bands = [(r["pred_band_pp"], r["actual_band_pp"]) for r in rows
             if r["pred_band_pp"] is not None and r["actual_band_pp"] is not None]
    print(f"    P(call) unpaired, predicted - actual: median {np.median(du):+.4f}  "
          f"MAE {np.mean(np.abs(du)):.4f}  worst {max(np.abs(du)):.4f}")
    print(f"    P(call) paired,   predicted - actual: median {np.median(dp):+.4f}  "
          f"MAE {np.mean(np.abs(dp)):.4f}  worst {max(np.abs(dp)):.4f}")
    if bands:
        db = [p - a for p, a in bands]
        print(f"    band width pp,    predicted - actual: median {np.median(db):+.3f}  "
              f"MAE {np.mean(np.abs(db)):.3f}  worst {max(np.abs(db)):.3f}  "
              f"(n={len(bands)})")

    disagree = [r for r in rows
                if (r["pred_unpaired"] >= 0.5) != (r["actual_unpaired"] >= 0.5)]
    print(f"\n    circuits where the borrowed shape flips the majority verdict: "
          f"{len(disagree)}/{len(rows)}")
    worst = sorted(rows, key=lambda r: -abs(r["pred_band_pp"] - r["actual_band_pp"])
                   if r["pred_band_pp"] is not None and r["actual_band_pp"] is not None
                   else -1)[:8]
    print(f"\n    {'circuit':<16s} {'test d':>8s} {'act band':>9s} {'pred band':>10s} "
          f"{'rho true':>9s} {'rho fit':>8s}")
    for r in worst:
        if r["pred_band_pp"] is None or r["actual_band_pp"] is None:
            continue
        print(f"    {r['circuit']:<16s} {r['test_change_pct']:>+7.1f}% "
              f"{r['actual_band_pp']:>8.2f}  {r['pred_band_pp']:>9.2f}  "
              f"{r['rho_spread_true_pct']:>8.2f}% {r['rho_spread_fit_pct']:>7.2f}%")


# ------------------------------------------- M3: does the band survive the model?

def _additive_candidate(o, eps, r):
    """new_i = old_i + D + eps_i, with D chosen so the MEAN change is r-1, and eps the
    measured additive residual re-centred to zero. The additive twin of sec 42's
    new_i = old_i * r * rho_i, expressed on the same relative-change axis so the two
    band widths are directly comparable."""
    return o + (r - 1.0) * o.mean() + eps


def band_compare(topo, old_ver, new_ver, threshold, k):
    data, vo, vn = arms(topo, old_ver, new_ver)
    rows = []
    for c, o, n in data:
        ratio = n / o
        rho = ratio / ratio.mean()
        diff = n - o
        eps = diff - diff.mean()
        het = ratio.max() != ratio.min()

        def solve(builder, target):
            def rate(r):
                return exact_call_rate(o, builder(r), threshold, k)
            lo, hi = 0.5, 3.0
            if rate(hi) < target:
                return float("nan")
            if rate(lo) >= target:
                return lo
            for _ in range(40):
                m = (lo + hi) / 2
                if rate(m) >= target:
                    hi = m
                else:
                    lo = m
            return (lo + hi) / 2

        mult = lambda r: o * r * rho                       # noqa: E731
        add = lambda r: _additive_candidate(o, eps, r)     # noqa: E731
        out = {"topology": topo, "circuit": c, "qiskit_old": vo, "qiskit_new": vn,
               "heterogeneous": het,
               "mean_change_pct": round((n.mean() / o.mean() - 1) * 100, 3)}
        for tag, b in (("mult", mult), ("add", add)):
            lo_, hi_ = solve(b, BAND_LO), solve(b, BAND_HI)
            out[f"band_{tag}_pp"] = (None if np.isnan(lo_) or np.isnan(hi_)
                                     else round((hi_ - lo_) * 100, 3))
        rows.append(out)
    return rows, vo, vn


def report_band_compare(rows, topo, vo, vn):
    het = [r for r in rows
           if r["heterogeneous"] and r["band_mult_pp"] is not None
           and r["band_add_pp"] is not None]
    print(f"\n  M3 — {topo}, qiskit {vo} -> {vn}: does sec 42's band survive the "
          f"model swap?")
    if not het:
        print("    no heterogeneous circuits with both bands defined")
        return
    m = [r["band_mult_pp"] for r in het]
    a = [r["band_add_pp"] for r in het]
    d = [x - y for x, y in zip(a, m)]
    print(f"    {len(het)} heterogeneous circuits")
    print(f"    median band, multiplicative (sec 42) : {np.median(m):6.2f} pp")
    print(f"    median band, ADDITIVE                : {np.median(a):6.2f} pp")
    print(f"    per-circuit difference additive-mult : median {np.median(d):+6.2f} pp, "
          f"MAE {np.mean(np.abs(d)):.2f} pp, worst {max(np.abs(d)):.2f} pp")
    worse = sum(1 for x in d if x > 0)
    print(f"    additive gives a WIDER band on {worse}/{len(het)} circuits")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--band-compare", action="store_true")
    p.add_argument("--topology", default="linear")
    p.add_argument("--pair", action="append", default=[],
                   help="old:new version keys, e.g. 200:202")
    p.add_argument("--oos-fit", help="version pair to fit rho on, e.g. 200:202")
    p.add_argument("--oos-test", help="version pair to predict, e.g. 143:200")
    p.add_argument("--threshold", type=float, default=0.10)
    p.add_argument("--k", type=int, default=3)
    p.add_argument("--out")
    args = p.parse_args()

    all_rows = []
    for pair in args.pair:
        o, n = pair.split(":")
        if args.band_compare:
            rows, vo, vn = band_compare(args.topology, o, n, args.threshold, args.k)
            report_band_compare(rows, args.topology, vo, vn)
        else:
            rows, vo, vn = fit_tests(args.topology, o, n)
            report_fit(rows, vo, vn, args.topology)
        all_rows += rows

    oos_rows = []
    if args.oos_fit and args.oos_test:
        fo, fn = args.oos_fit.split(":")
        to, tn = args.oos_test.split(":")
        oos_rows = oos(args.topology, (fo, fn), (to, tn), args.threshold, args.k)
        report_oos(oos_rows, args.threshold, args.k)

    if args.out and (all_rows or oos_rows):
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        rows = all_rows or oos_rows
        with open(args.out, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
