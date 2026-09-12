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

WHAT `--check` ACTUALLY PROVES, STATED EXACTLY (corrected 2026-09-04, finding F5)
    Every `value` is a FROZEN LITERAL in this file, and `--check` compares it against a
    fresh recomputation. Until 2026-09-04 that was not so: `value` was itself a call
    evaluated while the registry was built, and `recompute` re-ran the same call on the
    same file, so the comparison was f() against f() and no input could make it fail.
    Proved by falsifying every band in results/summary/band_heavy-hex.csv (x3, +40 pp):
    the tool still reported "41/41 live numbers reproduce".

    Provenance tiers, disclosed rather than glossed (vocabulary tightened in v3 after a
    hostile audit observed that "DERIVED" did not say whether a row was RECOMPUTED or
    merely READ BACK -- and it is the latter):
      RAW-RECOMPUTED  rows re-derived from results/raw/*.jsonl per-seed measurements.
      DERIVED-READ    the sec 43 k-sweep rows, re-read from results/summary/ksweep_*.csv.
               Re-deriving those means enumerating 12**5 mean tuples per bisection
               step, about half an hour per topology -- not affordable inside a check
               that has to run in under a minute. The frozen literal still catches a
               changed or corrupted CSV; it just cannot catch a CSV that was wrong when
               it was written. Rebuild them with `python ksweep.py --out ...`.
      NARRATIVE-N-A   withdrawn or prose-only rows carrying no live figure.

    ⚠ v3, audit F01. NO CENTRAL CLAIM MAY REST ON A DERIVED-READ ROW. The primary
    endpoint is now carried here as RAW-RECOMPUTED rows that call raw_endpoint.py, which
    rebuilds 12/26, 7/26 and 4/26 from the per-seed observations and reads no summary
    table. Before v3 the endpoint was not in this inventory at all: its 41 rows concerned
    earlier research-log results, so corrupting the primary raw data changed the science
    while every row here still reproduced.

    So: "every published figure is re-derived from raw data" would be FALSE and is not
    claimed anywhere. What is claimed is what this paragraph says.

    `--check` recomputes every row and fails on any mismatch.
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
import functools
import json
import os
import re
import sys

import numpy as np

from deep import exact_rate_int
from intervals import exact_call_rate, load, wilson
from paired import BAND_HI, BAND_LO, _solve, exact_paired_rate

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


@functools.lru_cache(maxsize=None)
def band_rows_raw(topo, k=3, t=0.10, min_seeds=12):
    """paired.band()'s per-circuit computation, re-executed HERE from the raw per-seed
    files. Certifying results/summary/band_*.csv by re-reading that same CSV was
    finding F5: the check could not detect a corrupted or stale summary."""
    old_all, _ = load(raw(topo, "200"))
    new_all, _ = load(raw(topo, "202"))
    rows = []
    for c in sorted(set(old_all) & set(new_all)):
        a, b = old_all[c], new_all[c]
        if len(a) < min_seeds or len(b) < min_seeds or len(a) != len(b):
            continue
        o = np.asarray(a, dtype=float)
        n = np.asarray(b, dtype=float)
        if not (o > 0).all():
            continue
        ratio = n / o
        rho = ratio / ratio.mean()
        rec = {"circuit": c, "rho_spread_pct": round((rho.max() - rho.min()) * 100, 3)}
        for pf in (False, True):
            lo = _solve(o, rho, BAND_LO, t, k, pf)
            hi = _solve(o, rho, BAND_HI, t, k, pf)
            rec["paired_band_pp" if pf else "unpaired_band_pp"] = (
                None if (np.isnan(lo) or np.isnan(hi)) else round((hi - lo) * 100, 3))
        rows.append(rec)
    return rows


def band_stat(topo, column, stat, heterogeneous_only=True):
    """RAW. Median/count/max of the ambiguity band over heterogeneous circuits."""
    vals = [r[column] for r in band_rows_raw(topo)
            if r[column] is not None
            and (not heterogeneous_only or r["rho_spread_pct"] > 0)]
    return {"median": float(np.median(vals)), "n": float(len(vals)),
            "max": float(max(vals))}[stat]


def band_fraction(topo, wide=5.0):
    """RAW. Fraction of circuits whose unpaired band reaches `wide` percentage points."""
    rows = band_rows_raw(topo)
    over = [r for r in rows if r["unpaired_band_pp"] is not None
            and r["unpaired_band_pp"] >= wide]
    return len(over) / len(rows), len(over), len(rows)


@functools.lru_cache(maxsize=None)
def deep_raw(circuit, t=0.10, k=3, seed=20260903, boot=4000):
    """RAW. deep.py's row for one circuit, re-derived from results/raw/deep_*.jsonl.

    Same estimator, same bootstrap seed, same integer decision rule, so this reproduces
    the committed CSV exactly -- but it reads the MEASUREMENTS, not the summary the row
    is certifying (F5)."""
    def arm(ver):
        vals = []
        with open(os.path.join(ROOT, "results", "raw",
                               f"deep_{circuit}_q{ver}.jsonl")) as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("record") == "run":
                    vals.append((r["seed"], r["two_q"]))
        return np.array([v for _, v in sorted(vals)], dtype=np.int64)

    o, n = arm("143"), arm("200")
    m = min(o.size, n.size)
    o, n = o[:m], n[:m]
    change = float(n.mean() / o.mean() - 1)
    r2 = np.random.default_rng(seed + 1)
    ch = np.empty(boot)
    for i in range(boot):
        j = r2.integers(0, m, m)
        ch[i] = n[j].mean() / o[j].mean() - 1
    c_lo, c_hi = np.percentile(ch, [2.5, 97.5])
    truth = ("REGRESSION" if c_lo > t else
             "NO_REGRESSION" if c_hi < t else "UNRESOLVED")
    p = exact_rate_int(o, n, t, k)
    err = (1 - p) if truth == "REGRESSION" else (
        p if truth == "NO_REGRESSION" else float("nan"))
    return {"ground_truth": truth, "n_seeds": int(m),
            "true_change_pct": round(change * 100, 3),
            "error_rate": round(err, 6)}


def ksweep_cell(topo, k, column):
    """DERIVED — reads results/summary/ksweep_*.csv rather than the raw files.

    Deliberate, and disclosed: the k-sweep band at k=5 enumerates 12**5 = 248,832 mean
    tuples per bisection step without a cached index grid, which costs roughly half an
    hour per topology. Re-deriving it inside a one-minute check is not affordable. The
    protection for these twelve rows is that `value` below is a FROZEN LITERAL, so a
    changed or corrupted CSV still fails the check -- it just fails against the
    recorded number rather than against the measurements."""
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



@functools.lru_cache(maxsize=1)
def _primary():
    """(eligible, excludes_zero, >=5%, >=10%) rebuilt FROM RAW. Cached: one pass costs
    about twenty seconds and all three rows share it."""
    import raw_endpoint as re_
    circuits = [c.strip() for c in open(os.path.join(ROOT, "_selected.txt"))
                if c.strip()]
    elig, excl, ge5, ge10 = re_.endpoint(re_.reconstruct(circuits))
    return len(elig), len(excl), len(ge5), len(ge10)


# --------------------------------------------------------------------- the registry

def entries():
    E = []

    def add(**kw):
        kw.setdefault("tier",
                      "RAW-RECOMPUTED" if kw.get("status") == "LIVE" else "NARRATIVE-N-A")
        E.append(kw)

    # ---- THE PRIMARY ENDPOINT, rebuilt from raw. Audit F01: this was absent before v3.
    #
    # These three rows are the reason the inventory exists. They call raw_endpoint.py,
    # which starts at the per-seed observations and reads no summary table, so corrupting
    # the raw data moves them. Every other row in this file could reproduce perfectly
    # while the headline result was wrong; that is exactly what the audit demonstrated.
    for _id, _idx, _claim in (
            ("s4.endpoint.excludes_zero", 1,
             "eligible circuits whose risk interval excludes zero (pre-registered "
             "primary endpoint)"),
            ("s4.endpoint.ge5", 2, "eligible circuits with point risk >= 5%"),
            ("s4.endpoint.ge10", 3, "eligible circuits with point risk >= 10%")):
        add(id=_id, status="LIVE", section="4.2", tier="RAW-RECOMPUTED",
            claim=_claim, value=(12, 7, 4)[_idx - 1], numerator=(12, 7, 4)[_idx - 1],
            denominator=26, sampling_unit="eligible circuit (resolved, non-boundary)",
            ci_lo="", ci_hi="",
            ci_method="count; Wilson intervals reported in PAPER.md sec 4.2",
            source="results/raw/prereg/*.jsonl via raw_endpoint.py",
            recompute=lambda i=_idx: _primary()[i])

    # ---- sec 41: the direction table. Both directions, because the point IS the pair.
    S41 = {("linear", "fwd"): (1, 51), ("linear", "rev"): (2, 51),
           ("square", "fwd"): (0, 52), ("square", "rev"): (10, 52),
           ("heavy-hex", "fwd"): (0, 52), ("heavy-hex", "rev"): (14, 52)}
    for topo in ("linear", "square", "heavy-hex"):
        for label, tag, (o, n) in (("forward_2.0.0_to_2.0.2", "fwd", ("200", "202")),
                                   ("reverse_2.0.2_to_2.0.0", "rev", ("202", "200"))):
            g, tot = S41[(topo, tag)]
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
    S42 = {("linear", "unpaired"): (2.5495, 24), ("linear", "paired"): (0.858, 24),
           ("square", "unpaired"): (9.775, 30), ("square", "paired"): (2.407, 30),
           ("heavy-hex", "unpaired"): (14.0435, 32),
           ("heavy-hex", "paired"): (2.0605, 32)}
    S42_WIDE = {"linear": (11, 51), "square": (27, 52), "heavy-hex": (34, 52)}
    for topo in ("linear", "square", "heavy-hex"):
        for arm in ("unpaired", "paired"):
            med, n_het = S42[(topo, arm)]
            add(id=f"s42.band.{topo}.{arm}.median", status="LIVE", section="42",
                claim=f"median {arm} ambiguity band, {topo}, heterogeneous circuits",
                value=med, numerator="", denominator=n_het,
                sampling_unit="circuit with a non-zero measured per-seed change",
                ci_lo="", ci_hi="",
                ci_method="seed bootstrap B=200 shared, reported in sec 42; biased low "
                          "(D-8.4)",
                source=f"results/raw/bp_large_{topo}_q{{200,202}}.jsonl",
                recompute=lambda t=topo, a=arm: band_stat(t, f"{a}_band_pp", "median"))
        over, tot = S42_WIDE[topo]
        lo, hi = wilson(over, tot)
        add(id=f"s42.wideband.{topo}", status="LIVE", section="42",
            claim=f"circuits whose unpaired band is >= 5 pp, {topo}",
            value=over / tot, numerator=over, denominator=tot,
            sampling_unit="circuit", ci_lo=lo, ci_hi=hi,
            ci_method="Wilson score, 95%",
            source=f"results/raw/bp_large_{topo}_q{{200,202}}.jsonl",
            recompute=lambda t=topo: band_fraction(t)[0])

    # ---- sec 43: k sensitivity. DERIVED tier -- see ksweep_cell's docstring for why.
    S43 = {"linear": ({1: 4.483, 2: 3.461, 3: 2.55, 5: 2.112}, 24),
           "square": ({1: 16.704, 2: 12.024, 3: 9.775, 5: 7.551}, 30),
           "heavy-hex": ({1: 23.803, 2: 17.222, 3: 14.043, 5: 10.862}, 32)}
    for topo in ("linear", "square", "heavy-hex"):
        by_k, n_het = S43[topo]
        for k in (1, 2, 3, 5):
            add(id=f"s43.k{k}.{topo}", status="LIVE", section="43", tier="DERIVED-READ",
                claim=f"median unpaired band at k={k}, {topo}",
                value=by_k[k], numerator="", denominator=n_het,
                sampling_unit="circuit with a non-zero measured per-seed change",
                ci_lo="", ci_hi="", ci_method="point estimate, exact enumeration; no "
                                              "interval computed for this table",
                source=f"results/summary/ksweep_{topo}.csv",
                recompute=lambda t=topo, kk=k: ksweep_cell(
                    t, kk, "unpaired_median_band_pp"))

    # ---- sec 30: within-version spread (single version, so direction-free)
    S30 = {"linear": (0.8958700664507562, 56), "square": (5.940159705959671, 56),
           "heavy-hex": (10.7094894120623, 56)}
    for topo in ("linear", "square", "heavy-hex"):
        med, n = S30[topo]
        add(id=f"s30.spread.{topo}.q202", status="LIVE", section="30",
            claim=f"median within-version seed spread (max-min)/min, {topo}, 2.0.2",
            value=med, numerator="", denominator=n,
            sampling_unit="circuit with >= 2 seeds",
            ci_lo="", ci_hi="", ci_method="none — descriptive median, not a proportion",
            source=f"results/raw/bp_large_{topo}_q202.jsonl",
            recompute=lambda t=topo: within_version_spread(t, "202")[0])

    # ---- sec 44: the replication
    add(id="s44.replication.exact", status="LIVE", section="44",
        claim="per-seed values reproduced exactly by replication/replicate.py",
        value=144 / 144, numerator=144, denominator=144,
        sampling_unit="(circuit, seed, version) triple",
        ci_lo="", ci_hi="", ci_method="none — a census of the artifact's own 144 checks",
        source="replication/out_q{200,202}.jsonl vs replication/expected.json",
        recompute=lambda: (lambda r: r[0] / r[1])(replication_exact_matches()))

    # ---- sec 48: the demonstrated decision errors, 200 seeds/arm.
    # error_rate and true_change re-derive from the raw per-seed files (deep_raw).
    # The bootstrap INTERVALS are frozen metadata, not recomputed: B=400 replicates x
    # 400,000 Monte-Carlo pairs per circuit is minutes of work and --check verifies
    # point values. Regenerate them with `python deep.py --out ...`.
    S48 = {"bv_n140": ("REGRESSION", 0.029801, 0.01722, 0.049909,
                       31.035, 28.377, 33.796),
           "bv_n30": ("REGRESSION", 0.007054, 0.002259, 0.014318,
                      24.18, 22.691, 25.724),
           "bv_n70": ("REGRESSION", 0.001496, 0.000196, 0.004053,
                      30.295, 28.525, 32.139),
           "adder_n64": ("REGRESSION", 0.215973, 0.152316, 0.289732,
                         10.818, 10.567, 11.071),
           "qft_n29": ("NO_REGRESSION", 7.3e-05, 5e-06, 0.00026,
                       0.491, -0.007, 0.994)}
    for cid, (truth, err, e_lo, e_hi, chg, c_lo, c_hi) in S48.items():
        add(id=f"s48.error.{cid}", status="LIVE", section="48",
            claim=f"{cid}: rate at which the 3-run unseeded protocol returns the "
                  f"WRONG verdict on the real 1.4.3 -> 2.0.0 change",
            value=err, numerator="", denominator=200,
            sampling_unit="seed (200 per arm); rate is exact over 200**3 sum-tuples",
            ci_lo=e_lo, ci_hi=e_hi,
            ci_method="seed bootstrap B=400 joint, 95%; point exact by integer rule",
            source=f"results/raw/deep_{cid}_q{{143,200}}.jsonl",
            recompute=lambda c=cid: deep_raw(c)["error_rate"])
        add(id=f"s48.truth.{cid}", status="LIVE", section="48",
            claim=f"{cid}: true mean change, 1.4.3 -> 2.0.0, 200 seeds/arm ({truth})",
            value=chg, numerator="", denominator=200, sampling_unit="seed",
            ci_lo=c_lo, ci_hi=c_hi,
            ci_method="percentile bootstrap over seeds, B=4000, 95%",
            source=f"results/raw/deep_{cid}_q{{143,200}}.jsonl",
            recompute=lambda c=cid: deep_raw(c)["true_change_pct"])

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
    """Compare each RECORDED value against a fresh recomputation.

    The `value` fields above are frozen literals. That is the whole point: until
    2026-09-04 each one was itself a function call evaluated when the registry was
    built, and `recompute` called the same function on the same file, so this loop
    compared f() with f() and could not fail. It was demonstrated: falsifying every
    band in results/summary/band_heavy-hex.csv (x3, +40 pp) still produced
    "41/41 live numbers reproduce". Frozen literals make a corrupted or stale source
    fail loudly whichever tier it belongs to."""
    bad = 0
    live = [e for e in E if e["status"] == "LIVE"]
    n_raw = sum(1 for e in live if e["tier"] == "RAW-RECOMPUTED")
    print(f"\n  {len(live)} recorded numbers, recomputed and compared to the literal "
          f"in this file")
    print(f"  RAW     {n_raw:>2d} re-derived from results/raw/*.jsonl per-seed "
          f"measurements")
    print(f"  DERIVED {len(live) - n_raw:>2d} re-read from a summary CSV "
          f"(too expensive to re-derive; see ksweep_cell)\n")
    for e in live:
        if e["recompute"] is None:
            print(f"  SKIP  {e['id']:<40s} no recompute defined")
            continue
        got = e["recompute"]()
        ok = abs(got - float(e["value"])) <= TOL
        bad += (not ok)
        mark = "ok  " if ok else "FAIL"
        print(f"  {mark}  {e['tier']:<15s} {e['id']:<40s} {float(e['value']):>9.4f}"
              + ("" if ok else f"   recomputed {got:.4f}"))
    n_w = len([e for e in E if e["status"] == "WITHDRAWN"])
    print(f"\n  {len(live) - bad}/{len(live)} recorded numbers match a fresh "
          f"recomputation ({n_raw} of them from raw measurements);")
    print(f"  {n_w} withdrawn numbers on the books.")
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
    cols = ["id", "status", "tier", "section", "claim", "value", "numerator",
            "denominator", "sampling_unit", "ci_lo", "ci_hi", "ci_method", "source"]
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
