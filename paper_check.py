"""Verify every quantitative claim in PAPER.md against the raw data. Fails loudly.

A paper whose numbers were typed from a transcript is a paper with typos in it. This
re-derives each figure and asserts it appears in PAPER.md, so a drifted number is caught
before anyone reads it.
"""

import csv
import io
import json
import os
import re
import sys

import numpy as np
from scipy import stats

from deep import exact_rate_int, mc_rate
from intervals import wilson
from prereg_analysis import load

# Normalise typographic characters: the paper uses U+2212 MINUS and U+2013/2014 dashes,
# while format() emits ASCII. Comparing them naively produced four false failures.
PAPER = (io.open("PAPER.md", encoding="utf-8").read()
         .replace("−", "-").replace("–", "-").replace("—", "-"))
CSV = "results/summary/prereg_heavy-hex.csv"
T, K = 0.10, 3
FAIL = []
OK = 0


def check(label, value, fmt="{:.1f}", must_appear=True):
    """Assert the formatted value literally occurs in the paper."""
    global OK
    s = fmt.format(value)
    present = s in PAPER
    if present == must_appear:
        OK += 1
        print(f"  ok    {label:<52s} {s}")
    else:
        FAIL.append((label, s))
        print(f"  FAIL  {label:<52s} {s}  <-- not found in PAPER.md")


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
    res = [r for r in rows if r["verdict"] != "UNRESOLVED"]
    elig = [r for r in res if r["boundary"] == "False"]
    risk = {r["circuit"]: float(r["error_rate"] or 0) for r in elig}

    print("\n=== §3.3 design ===")
    check("selected circuits", len(rows), "{:d}")
    check("eligible circuits", len(elig), "{:d}")
    check("transpilations (39 x 200 x 2)", len(rows) * 200 * 2, "{:,d}")

    print("\n=== §4.1 mechanism ===")
    det = [r for r in elig if data[r["circuit"]][0].std(ddof=1) == 0]
    check("deterministic eligible circuits", len(det), "{:d}")
    sto_all = [r for r in res if data[r["circuit"]][0].std(ddof=1) > 0]
    check("stochastic resolved circuits", len(sto_all), "{:d}")
    d = np.array([float(r["distance_to_cut_pp"]) for r in res
                  if data[r["circuit"]][0].std(ddof=1) > 0])
    e = np.array([float(r["error_rate"] or 0) for r in res
                  if data[r["circuit"]][0].std(ddof=1) > 0])
    sp = stats.spearmanr(d, e)
    check("Spearman distance vs risk", sp.statistic, "{:.3f}")
    assert sp.pvalue < 0.001, f"p={sp.pvalue}"
    print(f"  ok    {'Spearman p < 0.001':<52s} p={sp.pvalue:.2e}")

    print("\n=== §4.2 magnitude ===")
    for lab, thr in (("risk > 0", 0.0), ("risk >= 5%", 0.05), ("risk >= 10%", 0.10)):
        h = sum(1 for c, v in risk.items() if (v > 0 if thr == 0 else v >= thr))
        lo, hi = wilson(h, len(elig))
        check(f"{lab} count", h, "{:d}")
        check(f"{lab} pct", h / len(elig) * 100, "{:.1f}")
        check(f"{lab} Wilson lo", lo * 100, "{:.1f}")
        check(f"{lab} Wilson hi", hi * 100, "{:.1f}")
    vals = sorted(risk.values())
    check("median risk (eligible)", float(np.median(vals)), "{:.0f}")
    check("p75 risk", float(np.percentile(vals, 75)) * 100, "{:.1f}")
    check("p90 risk", float(np.percentile(vals, 90)) * 100, "{:.1f}")
    check("max risk", max(vals) * 100, "{:.1f}")

    print("\n=== §4.2 top circuits table ===")
    for c in ("bv_n280", "knn_n67", "swap_test_n83", "adder_n118", "knn_341"):
        r = next(x for x in elig if x["circuit"] == c)
        check(f"{c} theta", float(r["est_long_run_change_pct"]), "{:+.2f}")
        check(f"{c} risk", float(r["error_rate"]) * 100, "{:.2f}")

    print("\n=== §4.3 cc_n32 ===")
    o, n = data["cc_n32"]
    th = float(n.mean() / o.mean() - 1)
    p = exact_rate_int(o, n, T, K)
    check("cc_n32 theta", th * 100, "{:.2f}")
    check("cc_n32 distance pp", abs(th - T) * 100, "{:.1f}")
    check("cc_n32 risk pct", p * 100, "{:.2f}")
    check("cc_n32 triples of 1728", round(p * 1728), "{:d}")
    hi = float(np.max(n)) / float(np.min(o)) - 1
    check("cc_n32 single-run worst case", hi * 100, "{:+.1f}")
    r_ = n / o - 1
    ti = stats.t.interval(0.95, o.size - 1, loc=r_.mean(), scale=stats.sem(r_))
    check("cc_n32 t-CI lo", ti[0] * 100, "{:.2f}")
    check("cc_n32 t-CI hi", ti[1] * 100, "{:.2f}")

    print("\n=== §3.4 controls ===")
    cen = {}
    for line in open("results/raw/bp_large_heavy-hex_q202.jsonl"):
        r = json.loads(line)
        if r.get("record") == "run":
            cen.setdefault(r["circuit"], []).append(r["two_q"])
    sel = set(c.strip() for c in open("_selected.txt") if c.strip()) | {"bv_n140"}
    ins = [(max(v) - min(v)) / min(v) for c, v in cen.items()
           if len(v) >= 12 and min(v) > 0 and c in sel]
    outs = [(max(v) - min(v)) / min(v) for c, v in cen.items()
            if len(v) >= 12 and min(v) > 0 and c not in sel]
    u = stats.mannwhitneyu(ins, outs)
    check("selection-bias median in", float(np.median(ins)), "{:.4f}")
    check("selection-bias median out", float(np.median(outs)), "{:.4f}")
    check("selection-bias Mann-Whitney p", u.pvalue, "{:.3f}")

    print("\n=== §4.4 bv_n140 heavy-hex, pooled 400 seeds ===")
    def loadraw(p):
        v = [(json.loads(l)["seed"], json.loads(l)["two_q"]) for l in open(p)
             if json.loads(l).get("record") == "run"]
        return np.array([x for _, x in sorted(v)], dtype=np.int64)
    o = np.concatenate([loadraw("results/raw/deep_bv_n140_heavy-hex_q143.jsonl"),
                        loadraw("results/raw/scatter_bv_n140_heavy-hex_q143.jsonl")])
    n = np.concatenate([loadraw("results/raw/deep_bv_n140_heavy-hex_q200.jsonl"),
                        loadraw("results/raw/scatter_bv_n140_heavy-hex_q200.jsonl")])
    th = float(n.mean() / o.mean() - 1)
    check("bv_n140 hh pooled theta", th * 100, "{:.3f}")
    for k, lab in ((1, "k=1"), (3, "k=3"), (5, "k=5"), (8, "k=8"), (10, "k=10"),
                   (20, "k=20")):
        # 4 x 50M and 2 dp: at 1 dp, k=5 and k=8 sit on a rounding boundary and the
        # reported digit flipped with the MC seed. Averaging pins them.
        vs = [mc_rate(o, n, T, k, np.random.default_rng(sd), 50_000_000)
              for sd in (1, 2, 3, 4)]
        check(f"bv_n140 hh {lab}", float(np.mean(vs)) * 100, "{:.2f}")

    print("\n" + "=" * 60)
    print(f"  {OK} checks passed, {len(FAIL)} FAILED")
    for lab, s in FAIL:
        print(f"    MISSING FROM PAPER: {lab} = {s}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
