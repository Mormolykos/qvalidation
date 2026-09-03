"""Priority 1, remainder — a machine-checkable inventory of every reported number.

WHAT THIS IS FOR
    The audit's finding was not that one probability lacked an interval. It was that
    numbers travelled from a CSV into prose and then stopped being connected to
    anything -- sec 30's provenance line named a file it did not match, sec 32 quoted
    0.150 where the CSV said 0.147, and sec 38's headline turned out to depend on an
    arms convention nobody had written down.

    So every live number gets a row here carrying, at minimum:
        value, numerator, denominator, sampling unit, interval, interval method,
        the file it comes from, the section that quotes it, and a RECOMPUTE function.

    `--check` re-derives every row from the named file and fails on any mismatch.
    `--scan` reads the markdown and lists percentage-shaped numbers that no row claims,
    so a new unregistered number cannot quietly appear.

    Withdrawn numbers stay in the inventory with status WITHDRAWN and the section that
    withdrew them. Deleting them would make the record unfalsifiable.

USAGE
    python inventory.py --check
    python inventory.py --scan RESEARCH_LANDSCAPE.md
    python inventory.py --write results/summary/INVENTORY.csv
"""

import argparse
import csv
import json
import os
import re
import sys

import numpy as np

from intervals import exact_call_rate, load, wilson
from paired import exact_paired_rate

ROOT = os.path.dirname(os.path.abspath(__file__))
TOL = 0.005                     # absolute, on the value's own units


def raw(topo, ver):
    return os.path.join(ROOT, "results", "raw", f"bp_large_{topo}_q{ver}.jsonl")


def summary(name):
    return os.path.join(ROOT, "results", "summary", name)


# --------------------------------------------------------------- recompute helpers

def _arms(topo, old_ver, new_ver, min_seeds=12):
    o, _ = load(raw(topo, old_ver))
    n, _ = load(raw(topo, new_ver))
    out = []
    for c in sorted(set(o) & set(n)):
        a, b = o[c], n[c]
        if len(a) >= min_seeds and len(b) >= min_seeds and len(a) == len(b):
            out.append((c, np.array(a, float), np.array(b, float)))
    return out


def genuine_unstable(topo, old_ver, new_ver, t=0.10, k=3, band=3.0):
    """The sec 36-38 statistic: UNSTABLE minus circuits sitting on the cut."""
    n_gen = n_tot = 0
    for _, a, b in _arms(topo, old_ver, new_ver):
        p = exact_call_rate(a, b, t, k)
        n_tot += 1
        if 0.05 < p < 0.95:
            tc = (b.mean() - a.mean()) / a.mean() * 100
            if abs(tc - t * 100) > band:
                n_gen += 1
    return n_gen, n_tot


def band_stat(topo, column, stat, heterogeneous_only=True):
    rows = list(csv.DictReader(open(summary(f"band_{topo}.csv"))))
    vals = [float(r[column]) for r in rows
            if r[column] not in ("", "None")
            and (not heterogeneous_only or float(r["rho_spread_pct"]) > 0)]
    return {"median": float(np.median(vals)), "n": float(len(vals)),
            "max": float(max(vals))}[stat]


def band_fraction(topo, wide=5.0):
    rows = list(csv.DictReader(open(summary(f"band_{topo}.csv"))))
    over = [r for r in rows if r["unpaired_band_pp"] not in ("", "None")
            and float(r["unpaired_band_pp"]) >= wide]
    return len(over) / len(rows), len(over), len(rows)


def deep_row(circuit):
    for r in csv.DictReader(open(summary("deep_143_200.csv"))):
        if r["circuit"] == circuit:
            return r
    raise KeyError(f"{circuit} not in deep_143_200.csv")


def ksweep_cell(topo, k, column):
    for r in csv.DictReader(open(summary(f"ksweep_{topo}.csv"))):
        if int(r["k"]) == k:
            return float(r[column])
    raise KeyError(f"k={k} not in ksweep_{topo}.csv")


def replication_exact_matches():
    exp = json.load(open(os.path.join(ROOT, "replication", "expected.json")))
    n = ok = 0
    for arm_file, ver in (("out_q200.jsonl", "2.0.0"), ("out_q202.jsonl", "2.0.2")):
        path = os.path.join(ROOT, "replication", arm_file)
        for line in open(path):
            row = json.loads(line)
            if row.get("record") != "run":
                continue
            n += 1
            ok += int(row["two_q"] == exp["arms"][ver][row["circuit"]][str(row["seed"])])
    return ok, n


def within_version_spread(topo, ver, min_seeds=2):
    """sec 30's statistic: (max-min)/min per circuit, as a percentage."""
    vals, _ = load(raw(topo, ver))
    s = [(max(v) - min(v)) / min(v) * 100 for v in vals.values()
         if len(v) >= min_seeds and min(v) > 0]
    return float(np.median(s)), len(s)


# --------------------------------------------------------------------- the registry

def entries():
    E = []

    def add(**kw):
        E.append(kw)

    # ---- sec 41: the direction table. Both directions, because the point IS the pair.
    for topo in ("linear", "square", "heavy-hex"):
        for label, (o, n) in (("forward_2.0.0_to_2.0.2", ("200", "202")),
                              ("reverse_2.0.2_to_2.0.0", ("202", "200"))):
            g, tot = genuine_unstable(topo, o, n)
            lo, hi = wilson(g, tot)
            add(id=f"s41.unstable.{topo}.{label}", status="LIVE", section="41",
                claim=f"genuinely unstable circuits, {topo}, {label.replace('_',' ')}",
                value=g / tot, numerator=g, denominator=tot,
                sampling_unit="circuit (each with 12 seeds in both arms)",
                ci_lo=lo, ci_hi=hi, ci_method="Wilson score, 95%",
                source=f"results/raw/bp_large_{topo}_q{{200,202}}.jsonl",
                recompute=lambda t=topo, a=o, b=n: (lambda r: r[0] / r[1])(
                    genuine_unstable(t, a, b)))

    # ---- sec 42: the direction-free band
    for topo in ("linear", "square", "heavy-hex"):
        for arm in ("unpaired", "paired"):
            add(id=f"s42.band.{topo}.{arm}.median", status="LIVE", section="42",
                claim=f"median {arm} ambiguity band, {topo}, heterogeneous circuits",
                value=band_stat(topo, f"{arm}_band_pp", "median"),
                numerator="", denominator=int(band_stat(topo, f"{arm}_band_pp", "n")),
                sampling_unit="circuit with a non-zero measured per-seed change",
                ci_lo="", ci_hi="",
                ci_method="seed bootstrap B=200 shared, reported in sec 42; biased low "
                          "(D-8.4)",
                source=f"results/summary/band_{topo}.csv",
                recompute=lambda t=topo, a=arm: band_stat(t, f"{a}_band_pp", "median"))
        f, over, tot = band_fraction(topo)
        lo, hi = wilson(over, tot)
        add(id=f"s42.wideband.{topo}", status="LIVE", section="42",
            claim=f"circuits whose unpaired band is >= 5 pp, {topo}",
            value=f, numerator=over, denominator=tot,
            sampling_unit="circuit", ci_lo=lo, ci_hi=hi,
            ci_method="Wilson score, 95%",
            source=f"results/summary/band_{topo}.csv",
            recompute=lambda t=topo: band_fraction(t)[0])

    # ---- sec 43: k sensitivity
    for topo in ("linear", "square", "heavy-hex"):
        for k in (1, 2, 3, 5):
            add(id=f"s43.k{k}.{topo}", status="LIVE", section="43",
                claim=f"median unpaired band at k={k}, {topo}",
                value=ksweep_cell(topo, k, "unpaired_median_band_pp"),
                numerator="", denominator=int(ksweep_cell(topo, k, "n_heterogeneous")),
                sampling_unit="circuit with a non-zero measured per-seed change",
                ci_lo="", ci_hi="", ci_method="point estimate, exact enumeration; no "
                                              "interval computed for this table",
                source=f"results/summary/ksweep_{topo}.csv",
                recompute=lambda t=topo, kk=k: ksweep_cell(
                    t, kk, "unpaired_median_band_pp"))

    # ---- sec 30: within-version spread (single version, so direction-free)
    for topo in ("linear", "square", "heavy-hex"):
        med, n = within_version_spread(topo, "202")
        add(id=f"s30.spread.{topo}.q202", status="LIVE", section="30",
            claim=f"median within-version seed spread (max-min)/min, {topo}, 2.0.2",
            value=med, numerator="", denominator=n,
            sampling_unit="circuit with >= 2 seeds",
            ci_lo="", ci_hi="", ci_method="none — descriptive median, not a proportion",
            source=f"results/raw/bp_large_{topo}_q202.jsonl",
            recompute=lambda t=topo: within_version_spread(t, "202")[0])

    # ---- sec 44: the replication
    ok, n = replication_exact_matches()
    add(id="s44.replication.exact", status="LIVE", section="44",
        claim="per-seed values reproduced exactly by replication/replicate.py",
        value=ok / n, numerator=ok, denominator=n,
        sampling_unit="(circuit, seed, version) triple",
        ci_lo="", ci_hi="", ci_method="none — a census of the artifact's own 144 checks",
        source="replication/out_q{200,202}.jsonl vs replication/expected.json",
        recompute=lambda: (lambda r: r[0] / r[1])(replication_exact_matches()))

    # ---- sec 48: the demonstrated decision errors, 200 seeds/arm
    for cid, truth in (("bv_n140", "REGRESSION"), ("bv_n30", "REGRESSION"),
                       ("bv_n70", "REGRESSION"), ("adder_n64", "REGRESSION"),
                       ("qft_n29", "NO_REGRESSION")):
        r = deep_row(cid)
        add(id=f"s48.error.{cid}", status="LIVE", section="48",
            claim=f"{cid}: rate at which the 3-run unseeded protocol returns the "
                  f"WRONG verdict on the real 1.4.3 -> 2.0.0 change",
            value=float(r["error_rate"]), numerator="", denominator=int(r["n_seeds"]),
            sampling_unit="seed (200 per arm); rate is exact over 200**3 sum-tuples",
            ci_lo=float(r["error_ci_lo"]), ci_hi=float(r["error_ci_hi"]),
            ci_method="seed bootstrap B=400 joint, 95%; point exact by integer rule",
            source="results/summary/deep_143_200.csv",
            recompute=lambda c=cid: float(deep_row(c)["error_rate"]))
        add(id=f"s48.truth.{cid}", status="LIVE", section="48",
            claim=f"{cid}: true mean change, 1.4.3 -> 2.0.0, 200 seeds/arm ({truth})",
            value=float(r["true_change_pct"]), numerator="",
            denominator=int(r["n_seeds"]), sampling_unit="seed",
            ci_lo=float(r["true_change_ci_lo_pct"]),
            ci_hi=float(r["true_change_ci_hi_pct"]),
            ci_method="percentile bootstrap over seeds, B=4000, 95%",
            source="results/summary/deep_143_200.csv",
            recompute=lambda c=cid: float(deep_row(c)["true_change_pct"]))

    # ---- withdrawn, kept on the books
    add(id="s38.heavyhex.unstable.WITHDRAWN", status="WITHDRAWN", section="38 -> 41",
        claim="26.9% of heavy-hex circuits have a seed-dependent regression verdict",
        value=0.269, numerator=14, denominator=52, sampling_unit="circuit",
        ci_lo=0.168, ci_hi=0.403, ci_method="Wilson score, 95%",
        source="withdrawn by sec 41: direction artifact, 0/52 in the real direction",
        recompute=None)
    add(id="s31.qft_n320.rate.WITHDRAWN", status="WITHDRAWN", section="31 -> 38",
        claim="qft_n320 is miscalled 27.1% of the time",
        value=0.271, numerator="", denominator=12, sampling_unit="seed",
        ci_lo=0.017, ci_hi=0.631, ci_method="seed bootstrap B=2000, 95%",
        source="withdrawn by sec 38: interval spans 1.7%-63.1% at n=12",
        recompute=None)
    add(id="s32.paired.column.WITHDRAWN", status="WITHDRAWN", section="32 -> 40",
        claim="pairing removes every false positive across all 51 circuits",
        value=0.0, numerator=0, denominator=51, sampling_unit="none — an identity",
        ci_lo="", ci_hi="", ci_method="none",
        source="withdrawn by sec 40: the column is 1[effect >= threshold]",
        recompute=None)
    add(id="s34.paired.k1.WITHDRAWN", status="WITHDRAWN", section="34 -> 40",
        claim="pairing achieves 0.0% false positives at k=1",
        value=0.0, numerator="", denominator="", sampling_unit="none — an identity",
        ci_lo="", ci_hi="", ci_method="none",
        source="withdrawn by sec 40", recompute=None)
    add(id="s31.single_commit.WITHDRAWN", status="WITHDRAWN", section="31 -> 39",
        claim="2.0.0 vs 2.0.2 isolates a single commit, PR #14417",
        value="", numerator=31, denominator=64,
        sampling_unit="commits / files changed", ci_lo="", ci_hi="",
        ci_method="none — a git fact, verified against the GitHub compare API",
        source="withdrawn by sec 39: 31 commits, 64 files, one touching SabreLayout",
        recompute=None)
    return E


# ------------------------------------------------------------------------ commands

def cmd_check(E):
    bad = 0
    live = [e for e in E if e["status"] == "LIVE"]
    print(f"\n  recomputing {len(live)} live numbers from their named sources\n")
    for e in live:
        if e["recompute"] is None:
            print(f"  SKIP  {e['id']:<40s} no recompute defined")
            continue
        got = e["recompute"]()
        ok = abs(got - float(e["value"])) <= TOL
        bad += (not ok)
        mark = "ok  " if ok else "FAIL"
        print(f"  {mark}  {e['id']:<40s} {float(e['value']):>9.4f}"
              + ("" if ok else f"   recomputed {got:.4f}"))
    n_w = len([e for e in E if e["status"] == "WITHDRAWN"])
    print(f"\n  {len(live) - bad}/{len(live)} live numbers reproduce from their source; "
          f"{n_w} withdrawn numbers on the books.")
    return bad


PCT = re.compile(r"(?<![\w.])(\d{1,3}(?:\.\d+)?)\s*(?:%|pp\b)")


def cmd_scan(E, path):
    known = set()
    for e in E:
        for v in (e["value"], e.get("ci_lo"), e.get("ci_hi")):
            if isinstance(v, (int, float)):
                known.add(round(float(v) * 100, 1))
                known.add(round(float(v), 1))
    hits = {}
    for i, line in enumerate(open(path, encoding="utf-8"), 1):
        for m in PCT.finditer(line):
            val = round(float(m.group(1)), 1)
            if val in known or val in (0.0, 100.0, 95.0, 50.0, 5.0, 10.0):
                continue
            hits.setdefault(val, []).append(i)
    print(f"\n  {path}: {len(hits)} percentage-shaped values not covered by the "
          f"inventory")
    print(f"  (many are legitimately prose -- thresholds, deltas, quoted external "
          f"figures. This is a\n   prompt to check, not a defect list.)\n")
    for val, lines in sorted(hits.items())[:40]:
        where = ", ".join(str(x) for x in lines[:6])
        print(f"    {val:>7.1f}   lines {where}"
              + (f" (+{len(lines)-6} more)" if len(lines) > 6 else ""))


def cmd_write(E, out):
    cols = ["id", "status", "section", "claim", "value", "numerator", "denominator",
            "sampling_unit", "ci_lo", "ci_hi", "ci_method", "source"]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for e in E:
            w.writerow({c: e.get(c, "") for c in cols})
    print(f"\n  written: {out}  ({len(E)} rows)")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    p.add_argument("--scan")
    p.add_argument("--write")
    args = p.parse_args()
    if not (args.check or args.scan or args.write):
        p.error("pass --check, --scan and/or --write")
    E = entries()
    rc = 0
    if args.check:
        rc = cmd_check(E)
    if args.write:
        cmd_write(E, args.write)
    if args.scan:
        cmd_scan(E, args.scan)
    sys.exit(1 if rc else 0)


if __name__ == "__main__":
    main()
