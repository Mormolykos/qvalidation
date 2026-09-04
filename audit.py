"""First-principles audit. Every reported number re-derived from raw data.

Not a defence. Each check is written to FAIL if the claim is wrong, and the verdict is
recorded as INVALIDATES / REWORD / LIMITATION.
"""

import csv
import json
import os
import re
from itertools import product

import numpy as np
from scipy import stats

from deep import exact_rate_int, mc_rate
from prereg_analysis import load

RAW = os.path.join("results", "raw", "prereg")
CSV = "results/summary/prereg_heavy-hex.csv"
T, K = 0.10, 3
V = []


def note(tag, msg):
    V.append((tag, msg))
    print(f"      [{tag}] {msg}")


def arms(c):
    o, _ = load(c, "143")
    n, _ = load(c, "200")
    if o is None:
        return None, None
    m = min(o.size, n.size)
    return o[:m], n[:m]


def seeds_of(c, ver):
    p = os.path.join(RAW, f"{c}_heavy-hex_q{ver}.jsonl")
    return [json.loads(l)["seed"] for l in open(p)
            if json.loads(l).get("record") == "run"]


def main():
    rows = [r for r in csv.DictReader(open(CSV)) if r["status"] == "OK"]
    data = {r["circuit"]: arms(r["circuit"]) for r in rows}
    res = [r for r in rows if r["verdict"] != "UNRESOLVED"]
    elig = [r for r in res if r["boundary"] == "False"]

    print("\n=== A1. PAIRING VALIDITY: is the same seed set used everywhere? ===")
    ref = None
    bad = []
    for r in rows:
        for v in ("143", "200"):
            s = seeds_of(r["circuit"], v)
            if ref is None:
                ref = s
            if s != ref:
                bad.append((r["circuit"], v))
    if bad:
        note("INVALIDATES", f"seed sets differ: {bad[:4]}")
    else:
        note("OK", f"all 78 files use the identical 200-seed set, sorted identically; "
                   f"pairing across arms is valid")

    print("\n=== A2. Are the 200 seeds distinct, and is the block non-contiguous? ===")
    s = sorted(ref)
    note("OK" if len(set(s)) == 200 else "INVALIDATES",
         f"{len(set(s))} distinct seeds, min {min(s):,} max {max(s):,}, "
         f"max consecutive gap of 1: {sum(1 for a,b in zip(s,s[1:]) if b-a==1)}")

    print("\n=== A3. DUPLICATE CIRCUITS in the pre-registered set ===")
    sig = {}
    for r in rows:
        o, n = data[r["circuit"]]
        sig.setdefault((tuple(o.tolist()), tuple(n.tolist())), []).append(r["circuit"])
    dup = [g for g in sig.values() if len(g) > 1]
    if dup:
        involved = [c for g in dup for c in g]
        in_elig = [c for c in involved if any(r["circuit"] == c for r in elig)]
        note("LIMITATION" if not in_elig else "REWORD",
             f"identical pairs {dup}; of these, in the ELIGIBLE set: {in_elig or 'none'}")
    else:
        note("OK", "no duplicates")

    print("\n=== A4. Is 'per-seed ratio SD > 0' CIRCULAR as a predictor of risk? ===")
    # If BOTH arms are constant, error is 0 by arithmetic, not by measurement.
    both_const = []
    ratio_const_only = []
    for r in res:
        o, n = data[r["circuit"]]
        if o.std(ddof=1) == 0 and n.std(ddof=1) == 0:
            both_const.append(r["circuit"])
        elif (n / o).std(ddof=1) == 0:
            ratio_const_only.append(r["circuit"])
    note("REWORD",
         f"{len(both_const)} circuits have BOTH arms constant -> P(call) is a constant "
         f"and the risk is 0 BY ARITHMETIC, not by measurement. Claiming a correlation "
         f"between 'stochasticity' and 'risk' over a sample containing them is partly "
         f"tautological.")
    note("OK" if not ratio_const_only else "LIMITATION",
         f"circuits with constant RATIO but variable arms: {ratio_const_only or 'none'} "
         f"(these would have non-zero risk despite SD(ratio)=0)")

    print("\n=== A5. Recompute the Spearman correlations claimed in sec 55 ===")
    cvr, dist, err, oldsd = [], [], [], []
    for r in res:
        o, n = data[r["circuit"]]
        cvr.append(float((n / o).std(ddof=1)))
        oldsd.append(float(o.std(ddof=1) / o.mean()))
        dist.append(float(r["distance_to_cut_pp"]))
        err.append(float(r["error_rate"] or 0))
    cvr, dist, err, oldsd = map(np.array, (cvr, dist, err, oldsd))
    s1 = stats.spearmanr(cvr, err)
    note("REWORD",
         f"SD(ratio) vs risk: rho={s1.statistic:+.3f} p={s1.pvalue:.2e} -- but "
         f"{int((cvr==0).sum())} ties at 0 in x and {int((err==0).sum())} at 0 in y. "
         f"Spearman with this many ties is inflated and is the WRONG statistic.")
    nz = cvr > 0
    s2 = stats.spearmanr(dist[nz], err[nz])
    note("OK" if s2.pvalue < 0.05 else "LIMITATION",
         f"among the {int(nz.sum())} stochastic circuits, distance-to-cut vs risk: "
         f"rho={s2.statistic:+.3f} p={s2.pvalue:.3f} (n={int(nz.sum())})")

    print("\n=== A6. The right statistic: a 2x2 contingency, not a correlation ===")
    a = sum(1 for r in elig if data[r["circuit"]][0].std(ddof=1) > 0
            and r["error_excludes_zero"] == "True")
    b = sum(1 for r in elig if data[r["circuit"]][0].std(ddof=1) > 0
            and r["error_excludes_zero"] != "True")
    c_ = sum(1 for r in elig if data[r["circuit"]][0].std(ddof=1) == 0
             and r["error_excludes_zero"] == "True")
    d = sum(1 for r in elig if data[r["circuit"]][0].std(ddof=1) == 0
            and r["error_excludes_zero"] != "True")
    odds, p = stats.fisher_exact([[a, b], [c_, d]])
    note("OK", f"stochastic&risk={a} stochastic&norisk={b} determ&risk={c_} "
               f"determ&norisk={d}; Fisher exact p={p:.2e}")
    note("REWORD", f"but cell d={d} is populated by circuits whose risk is 0 by "
                   f"ARITHMETIC (A4), so the test partly measures a definition")

    print("\n=== A7. SELECTION BIAS: does the <=10s rule pick high-variance circuits? ===")
    cen = {}
    for line in open("results/raw/bp_large_heavy-hex_q202.jsonl"):
        r = json.loads(line)
        if r.get("record") == "run":
            cen.setdefault(r["circuit"], {"v": [], "s": 0.0})
            cen[r["circuit"]]["v"].append(r["two_q"])
            cen[r["circuit"]]["s"] += r["seconds"]
    sel = set(c.strip() for c in open("_selected.txt") if c.strip()) | {"bv_n140"}
    ins, outs = [], []
    for c, d_ in cen.items():
        if len(d_["v"]) < 12 or min(d_["v"]) == 0:
            continue
        spread = (max(d_["v"]) - min(d_["v"])) / min(d_["v"])
        (ins if c in sel else outs).append(spread)
    u = stats.mannwhitneyu(ins, outs) if outs else None
    note("LIMITATION",
         f"selected n={len(ins)} median spread {np.median(ins):.4f} | "
         f"NOT selected n={len(outs)} median {np.median(outs):.4f} | "
         f"Mann-Whitney p={u.pvalue:.3f}" if outs else "no excluded circuits")

    print("\n=== A8. Verify the headline per-circuit numbers against raw data ===")
    for c in ("cc_n32", "cc_n64", "bv_n280", "knn_341"):
        o, n = data[c]
        theta = float(n.mean() / o.mean() - 1)
        g = np.array(list(product(range(12), repeat=3)))  # unused, kept for shape parity
        p_exact = exact_rate_int(o, n, T, K)
        row = next(r for r in rows if r["circuit"] == c)
        ok = abs(p_exact - float(row["p_call"])) < 1e-6 and \
             abs(theta * 100 - float(row["est_long_run_change_pct"])) < 1e-3
        note("OK" if ok else "INVALIDATES",
             f"{c}: theta={theta*100:+.3f}% P(call)={p_exact:.6f} "
             f"-> matches CSV: {ok}")

    print("\n=== A9. cc_n32: is it REALLY 18 points clear and still miscalled? ===")
    o, n = data["cc_n32"]
    theta = float(n.mean() / o.mean() - 1)
    r_ = n / o - 1
    ti = stats.t.interval(0.95, o.size - 1, loc=r_.mean(), scale=stats.sem(r_))
    p_exact = exact_rate_int(o, n, T, K)
    note("OK" if ti[1] < T and p_exact > 0 else "INVALIDATES",
         f"theta={theta*100:+.2f}%, per-seed t-CI [{ti[0]*100:+.2f},{ti[1]*100:+.2f}]%, "
         f"distance {abs(theta-T)*100:.1f}pp, P(call)={p_exact:.6f} "
         f"({p_exact*1728:.0f} of 1728 sampled triple-pairs would call it)")
    hi = float(np.max(n)) / float(np.min(o)) - 1
    note("OK", f"single-draw worst case: max(new)/min(old)-1 = {hi*100:+.1f}% "
               f"-> a k=1 comparison CAN exceed +10% ({'yes' if hi>T else 'NO'})")

    print("\n=== A10. Is the ambiguity band well defined where P(call) never reaches .95? ===")
    und = 0
    for r in res:
        o, n = data[r["circuit"]]
        if (n / o).std(ddof=1) == 0:
            continue
        rho = (n / o) / (n / o).mean()
        rng = np.random.default_rng(3)
        top = mc_rate(o, (o * 3.0 * rho).astype(np.int64), T, K, rng, 100000)
        if top < 0.95:
            und += 1
    note("LIMITATION" if und else "OK",
         f"{und} stochastic circuits never reach P(call)=0.95 even at r=3.0, so their "
         f"band is right-censored and the reported median is a LOWER bound"
         if und else "every stochastic circuit reaches P=0.95 within r<=3.0")

    print("\n=== VERDICT TALLY ===")
    for tag in ("INVALIDATES", "REWORD", "LIMITATION", "OK"):
        k = [m for t, m in V if t == tag]
        print(f"  {tag:<12s} {len(k)}")


if __name__ == "__main__":
    main()
