"""Verify an ENUMERATED LIST of quantitative claims in PAPER.md against the data.

A paper whose numbers were typed from a transcript is a paper with typos in it. This
re-derives each figure on that list and asserts it appears in PAPER.md, so a drifted
number is caught before anyone reads it.

WHAT IT DOES NOT DO — say the scope, because a PASS is read as a promise (Astra V4-05)
    This header said "every quantitative claim in PAPER.md". It checks the claims listed
    in this file: 50 of them at present, not every number in the manuscript, not the
    intervals, and no prose.

    PRESENCE IS NOT PLACEMENT. Each check asserts that a recomputed value APPEARS
    somewhere in the source text. A number found in an unrelated sentence satisfies it.
    Binding a claim to the endpoint it names is `manuscript_binding.py`'s job, and the
    reason that file exists.
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
# the k-sweep figures as printed in PAPER.md sec 4.5
REPORTED_K = {1: 34.58, 3: 24.38, 5: 18.56, 8: 12.94, 10: 10.36, 20: 3.74}
FAIL = []
OK = 0


def check_near(label, value, reported, tol):
    """Numeric comparison for Monte-Carlo estimates. String-matching the last digit of
    an MC estimate is the wrong test: k=5 sits at 18.565 and flips between 18.56 and
    18.57 with the sampling pattern. Assert the paper's figure is within tolerance
    instead, and confirm it literally appears."""
    global OK
    close = abs(value - reported) <= tol
    present = f"{reported:.2f}" in PAPER
    if close and present:
        OK += 1
        print(f"  ok    {label:<52s} paper {reported:.2f}  computed {value:.3f}"
              f"  (tol {tol})")
    else:
        FAIL.append((label, f"paper {reported:.2f} vs computed {value:.3f}"))
        print(f"  FAIL  {label:<52s} paper {reported:.2f} computed {value:.3f} "
              f"close={close} present={present}")


def check(label, value, fmt="{:.1f}", must_appear=True, near=None, window=140):
    """Assert the formatted value occurs in the paper.

    ⚠ WHAT PRESENCE DOES NOT PROVE (stated 2026-09-08 after an external audit). Without
    `near`, this asks only whether the formatted string appears ANYWHERE in PAPER.md.
    The token "26" occurs seventeen times, eight of them inside a larger number such as
    26.9 or 126. So a bare presence check can pass while the figure is quoted in the
    wrong sentence, or while the right sentence carries a different number entirely.

    `near` fixes that for one claim at a time: the value must appear within `window`
    characters AFTER the anchor string, which for a table is the row label. That binds
    the number to its row rather than to the document. Anchors are used on the
    load-bearing figures -- the endpoint table -- because those are small integers with
    many innocent collisions elsewhere in the prose.

    This is a narrowing, not a cure. A checker bound to a section can still pass on a
    number that is wrong in a way the section does not reveal.
    """
    global OK
    s = fmt.format(value)
    if near is None:
        present, scope = s in PAPER, ""
    else:
        i = PAPER.find(near)
        if i < 0:
            FAIL.append((label, f"anchor {near!r} missing from PAPER.md"))
            print(f"  FAIL  {label:<52s} anchor {near!r} not in PAPER.md")
            return
        present = s in PAPER[i:i + window]
        scope = f"  [in row {near!r}]"
    if present == must_appear:
        OK += 1
        print(f"  ok    {label:<52s} {s}{scope}")
    else:
        FAIL.append((label, s))
        print(f"  FAIL  {label:<52s} {s}  <-- not found"
              + (f" near {near!r}" if near else " in PAPER.md"))


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
    # Anchored to the table ROW, not the document: these are small integers (12, 26, 7,
    # 4) and two-digit percentages that collide with unrelated prose all over PAPER.md.
    # The leading pipe matters. "risk ≥ 5%" alone first matches §3.2's prose sentence
    # "the count of circuits at risk ≥ 5% is", 90 lines above the table -- which is
    # precisely the wrong-location failure this anchoring exists to catch. It caught it
    # on the first run.
    ROW = {0.0: "| risk > 0 (pre-registered endpoint) |",
           0.05: "| risk ≥ 5% |", 0.10: "| risk ≥ 10% |"}
    for lab, thr in (("risk > 0", 0.0), ("risk >= 5%", 0.05), ("risk >= 10%", 0.10)):
        h = sum(1 for c, v in risk.items() if (v > 0 if thr == 0 else v >= thr))
        lo, hi = wilson(h, len(elig))
        row = ROW[thr]
        check(f"{lab} count", h, "{:d}", near=row)
        check(f"{lab} pct", h / len(elig) * 100, "{:.1f}", near=row)
        check(f"{lab} Wilson lo", lo * 100, "{:.1f}", near=row)
        check(f"{lab} Wilson hi", hi * 100, "{:.1f}", near=row)
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
    # v3 (audit F17): the "6 of 1728 triples" check is REMOVED, not repaired. There was
    # no 1728-triple sample; 0.00374089 * 1728 = 6.4643, and rounding that to 6 is what
    # manufactured the sentence. The exact probability is checked instead.
    check("cc_n32 exact risk pct", p * 100, "{:.6f}")
    hi = float(np.max(n)) / float(np.min(o)) - 1
    check("cc_n32 single-run worst case", hi * 100, "{:+.1f}")
    # v3 (audit F17): the published interval was a t-interval for mean(B/A - 1), a
    # DIFFERENT estimand from the ratio of arm means the paper reports. Bootstrap the
    # declared estimand instead.
    rb = np.random.default_rng(20260904)
    bs = np.empty(4000)
    for i in range(4000):
        j = rb.integers(0, o.size, o.size)
        bs[i] = n[j].mean() / o[j].mean() - 1
    lo_, hi_ = np.percentile(bs, [2.5, 97.5])
    check("cc_n32 ratio-of-means CI lo", lo_ * 100, "{:.2f}")
    check("cc_n32 ratio-of-means CI hi", hi_ * 100, "{:.2f}")

    print("\n=== §3.4 controls ===")
    cen = {}
    for line in open("results/raw/bp_large_heavy-hex_q202.jsonl"):
        r = json.loads(line)
        if r.get("record") == "run":
            cen.setdefault(r["circuit"], []).append(r["two_q"])
    # v3 (audit F08): the published test put bv_n140 in the SELECTED group, although it
    # was excluded from the primary analysis -- 40 vs 12, p = 0.7676. The correct groups
    # are the 39 selected against the 13 complete-census circuits, p = 0.4560. Six further
    # census circuits lack the 12-run data this test needs and enter neither group.
    sel = set(c.strip() for c in open("_selected.txt") if c.strip())
    ins = [(max(v) - min(v)) / min(v) for c, v in cen.items()
           if len(v) >= 12 and min(v) > 0 and c in sel]
    outs = [(max(v) - min(v)) / min(v) for c, v in cen.items()
            if len(v) >= 12 and min(v) > 0 and c not in sel]
    u = stats.mannwhitneyu(ins, outs)
    check("selection-bias median in", float(np.median(ins)), "{:.4f}")
    check("selection-bias median out", float(np.median(outs)), "{:.4f}")
    check("selection-bias Mann-Whitney p", u.pvalue, "{:.4f}")
    check("selection-bias n selected", len(ins), "{:d}", near="39** selected")

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
        vs = [mc_rate(o, n, T, k, np.random.default_rng(sd), 20_000_000)
              for sd in (1, 2, 3, 4)]
        check_near(f"bv_n140 hh {lab}", float(np.mean(vs)) * 100,
                   REPORTED_K[k], tol=0.05)

    print("\n" + "=" * 60)
    print(f"  {OK} checks passed, {len(FAIL)} FAILED")
    for lab, s in FAIL:
        print(f"    MISSING FROM PAPER: {lab} = {s}")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
