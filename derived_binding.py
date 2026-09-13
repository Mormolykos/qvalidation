"""Every saved primary field, bound to a replay of the analysis that produced it.

WHY (Astra A01)
    v3 reconstructed the endpoint from raw and compared the counts. It never compared the
    saved *uncertainty*. Astra replaced all 36 saved risk intervals with
    [0.900000, 0.999999], left every flag and count untouched, and the full verifier
    returned **9/9 PASS**.

    The published intervals are load-bearing: the primary endpoint is "risk interval
    excludes zero". A file whose intervals are fiction, whose counts are correct, and
    which passes every check, is worse than no file.

CONTRACT A — replay the original stream, do not substitute a better one
    The saved intervals came from the original Monte-Carlo bootstrap: 400 seed resamples,
    400,000-pair inner MC, `np.random.default_rng(20260905)`. Astra independently
    replayed all 36 and matched them to <= 5e-7.

    So this file replays THAT method — `prereg_analysis.analyse`, same seeds, same budget
    — and compares it to the saved rows field by field.

    It deliberately does NOT compare the saved intervals against `raw_endpoint.py`'s exact
    convolution bootstrap. Those are a different estimator and give slightly different
    endpoints; comparing them would either fail on correct data or need a tolerance wide
    enough to hide the attack. Silently checking historical MC intervals against a
    different stream is the mistake this file exists to avoid.

    `raw_endpoint.py` remains the independent scientific check on the HEADLINE. This is
    the binding check on the SAVED ARTIFACT. Different jobs; neither substitutes.

WHY THE SCHEMA IS DECLARED AND NOT INFERRED (Astra V4-01)
    v4's first version parsed every cell with `float(...)` or `int(float(...))` and then
    compared it. Astra set all 36 saved risk intervals to `NaN` and the full 13-stage
    verifier returned **exit 0**, because `abs(NaN - want) > tol` is False: a comparison
    against a value outside the domain is not a weak check, it is not a check at all.
    `n_seeds=200.9` and `k=3.9` passed the same way, truncated by `int(float(...))`, and a
    duplicated row vanished into a dict keyed by circuit before anything counted it.

    So the fix is not "also reject NaN". It is that PARSING IS A CONTRACT: every field
    declares the set of values it admits, and a cell outside that set is rejected by name
    BEFORE any comparison runs. Enumerating the bad inputs someone thought of is how this
    repository has now been bitten four times; declaring the admissible domain is the only
    form that covers the inputs nobody thought of. (`METHODOLOGY.md` R19.)

    Three contracts, kept separate so a failure says which one broke:
      DOMAIN     every cell is a member of its declared type's value set
      SELF       the row is internally coherent — interval order, flags recomputed from
                 the bounds they describe — checked on the SAVED row alone, with no replay
      REPLAY     the value equals what re-running its own analysis produces

COST
    A full replay is about four minutes. That is the price of checking the numbers rather
    than a summary of them.

USAGE
    python derived_binding.py            # replay and bind every field
    python derived_binding.py --quick    # intervals and endpoint fields only
    python derived_binding.py --schema   # domain + self-consistency only, no replay
"""

import argparse
import csv
import math
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import prereg_analysis as pa

SUMMARY = os.path.join(ROOT, "results", "summary", "prereg_heavy-hex.csv")
SELECTED = os.path.join(ROOT, "_selected.txt")

# ---------------------------------------------------------------- declared domains
#
# A kind is a NAME FOR A SET OF VALUES. `parse` returns a member of that set or raises
# Domain; there is no third outcome and no silent coercion into range.

INT_RE = re.compile(r"[+-]?\d+\Z")
BOOL_TOKENS = {"True": True, "False": False, "true": True, "false": False,
               "TRUE": True, "FALSE": False, "1": True, "0": False}


class Domain(Exception):
    """A cell is not a member of the set its field declares."""


def parse(kind, raw):
    """The declared domain of `kind`, or Domain. Empty means 'not applicable'."""
    if raw in ("", None):
        return None
    s = str(raw)
    if kind == "str":
        if not s.strip():
            raise Domain("blank where a string is required")
        return s
    if kind == "bool":
        if s not in BOOL_TOKENS:
            raise Domain(f"{s!r} is not one of {sorted(BOOL_TOKENS)} — an unrecognised "
                         f"token must not silently become False")
        return BOOL_TOKENS[s]
    if kind in ("int", "count"):
        if not INT_RE.match(s):
            raise Domain(f"{s!r} is not an integer literal — a fractional or "
                         f"exponent-form value must not be truncated into one")
        v = int(s)
        if kind == "count" and v < 1:
            raise Domain(f"{v} is not a positive count")
        return v
    # every remaining kind is a real number, and every real number must be FINITE:
    # NaN and ±inf compare False against everything, so they pass any tolerance test
    # ever written. They are rejected here, not compared later.
    try:
        v = float(s)
    except ValueError:
        raise Domain(f"{s!r} is not a number")
    if not math.isfinite(v):
        raise Domain(f"{s!r} is not finite — a nonfinite value satisfies every "
                     f"tolerance comparison and therefore cannot be validated")
    if kind == "prob" and not (0.0 <= v <= 1.0):
        raise Domain(f"{v!r} is outside [0, 1], which a probability must be in")
    return v


# field -> (kind, tolerance). Tolerances are the saved rounding, not slack: the CSV stores
# 4 or 6 decimals, so anything looser would let a real change hide inside it.
FIELDS = {
    "status":                   ("str", None),
    "verdict":                  ("str", None),
    "error_kind":               ("str", None),
    "qiskit_baseline":          ("str", None),
    "qiskit_candidate":         ("str", None),
    "boundary":                 ("bool", None),
    "error_excludes_zero":      ("bool", None),
    "n_seeds":                  ("count", None),
    "k":                        ("count", None),
    "threshold":                ("prob", 1e-12),
    "est_long_run_change_pct":  ("real", 5e-5),
    "change_ci_lo_pct":         ("real", 5e-5),
    "change_ci_hi_pct":         ("real", 5e-5),
    "distance_to_cut_pp":       ("real", 5e-4),
    "p_call":                   ("prob", 5e-7),
    "error_rate":               ("prob", 5e-7),
    "error_ci_lo":              ("prob", 5e-7),
    "error_ci_hi":              ("prob", 5e-7),
}
# The saved artifact carries exactly these columns. An unexpected one is not harmless:
# a checker that ignores columns it does not know cannot notice a second `error_rate`
# spelled differently, and a reader cannot tell which column the paper quotes.
COLUMNS = {"circuit", *FIELDS}
# Closed value sets, taken from what prereg_analysis can emit. A verdict outside this set
# is not a value with an unexpected spelling; it is not a verdict.
ENUMS = {"verdict": {"REGRESSION", "NO_REGRESSION", "UNRESOLVED"},
         "error_kind": {"FALSE_POSITIVE", "FALSE_NEGATIVE", "N/A"}}

QUICK = {"error_ci_lo", "error_ci_hi", "error_rate", "error_excludes_zero",
         "verdict", "boundary", "status"}


def read_rows(path):
    """Rows as a LIST, plus the header, so nothing is collapsed before it is counted."""
    with open(path, encoding="utf-8", newline="") as fh:
        rdr = csv.DictReader(fh)
        return list(rdr.fieldnames or []), [dict(r) for r in rdr]


def check_schema(header, rows):
    """DOMAIN and SELF contracts. Saved artifact only — no replay, no raw data."""
    fails = []

    got_cols = set(header)
    for c in sorted(COLUMNS - got_cols):
        fails.append(f"header: declared column '{c}' is missing")
    for c in sorted(got_cols - COLUMNS):
        fails.append(f"header: column '{c}' is not in the declared schema — every "
                     f"column of the published artifact must be one this file validates")
    if len(header) != len(set(header)):
        fails.append("header: a column name is repeated")
    if fails:
        return fails                      # a wrong shape makes row checks meaningless

    seen = {}
    for i, row in enumerate(rows, start=2):        # line 1 is the header
        cid = (row.get("circuit") or "").strip()
        if not cid:
            fails.append(f"line {i}: row has no circuit id")
            continue
        if cid == "circuit":
            fails.append(f"line {i}: a second header row is embedded in the data")
            continue
        if cid in seen:
            fails.append(f"line {i}: circuit '{cid}' already appears on line {seen[cid]} "
                         f"— duplicate identities collapse before they are counted")
            continue
        seen[cid] = i

        vals = {}
        bad = False
        for f, (kind, _) in FIELDS.items():
            try:
                vals[f] = parse(kind, row.get(f))
            except Domain as exc:
                fails.append(f"{cid}.{f}: {exc}")
                bad = True
        if bad:
            continue
        for f, allowed in ENUMS.items():
            if vals.get(f) is not None and vals[f] not in allowed:
                fails.append(f"{cid}.{f}: {vals[f]!r} is not one of {sorted(allowed)}")

        # SELF — recomputable from the saved row alone. These are the relations that make
        # the row mean what its column names say, and they hold whatever the replay does.
        lo, hi, pt = vals["error_ci_lo"], vals["error_ci_hi"], vals["error_rate"]
        if (lo is None) != (hi is None) or (lo is None) != (pt is None):
            fails.append(f"{cid}: risk point and interval must be present together "
                         f"(lo={lo!r} hi={hi!r} point={pt!r})")
        elif lo is not None:
            if lo > hi:
                fails.append(f"{cid}: risk interval is inverted — [{lo}, {hi}]")
            if not (lo <= pt <= hi):
                fails.append(f"{cid}: saved risk {pt} lies outside its own interval "
                             f"[{lo}, {hi}]")
            if vals["error_excludes_zero"] != (lo > 0.0):
                fails.append(f"{cid}.error_excludes_zero is {vals['error_excludes_zero']} "
                             f"but the saved lower bound is {lo} — the primary endpoint "
                             f"flag must follow the interval it describes")
        elif vals["error_excludes_zero"]:
            fails.append(f"{cid}.error_excludes_zero is True with no saved interval")

        clo, chi, ch = (vals["change_ci_lo_pct"], vals["change_ci_hi_pct"],
                        vals["est_long_run_change_pct"])
        if clo > chi:
            fails.append(f"{cid}: change interval is inverted — [{clo}, {chi}]")
        if not (clo <= ch <= chi):
            fails.append(f"{cid}: saved change {ch} lies outside its own interval "
                         f"[{clo}, {chi}]")

        dist = abs(ch - vals["threshold"] * 100.0)
        if abs(dist - vals["distance_to_cut_pp"]) > 5e-4:
            fails.append(f"{cid}.distance_to_cut_pp is {vals['distance_to_cut_pp']} but "
                         f"|change − cut| is {dist:.4f}")
        # BOUNDARY_PP is a closed rule on the saved distance. Rows sitting within 1e-3 of
        # the 3 pp cut are left to the replay: the saved value is rounded and the nearest
        # recorded row is 0.237 pp away, so this guard costs nothing here.
        if abs(dist - pa.BOUNDARY_PP) > 1e-3:
            if vals["boundary"] != (dist <= pa.BOUNDARY_PP):
                fails.append(f"{cid}.boundary is {vals['boundary']} at {dist:.4f} pp "
                             f"from the cut (rule: ≤ {pa.BOUNDARY_PP} pp)")

        if (vals["verdict"] == "UNRESOLVED") != (lo is None):
            fails.append(f"{cid}: verdict {vals['verdict']} with "
                         f"{'no' if lo is None else 'a'} saved risk interval")
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--schema", action="store_true",
                    help="domain and self-consistency only; skip the 4-minute replay")
    args = ap.parse_args()
    fields = {k: v for k, v in FIELDS.items() if not args.quick or k in QUICK}

    circuits = [c.strip() for c in open(SELECTED) if c.strip()]
    header, rows = read_rows(SUMMARY)

    print(f"\n  SAVED SUMMARY BOUND TO A REPLAY OF ITS OWN ANALYSIS")
    print(f"  {len(rows)} rows, {len(header)} columns\n")

    # DOMAIN + SELF first. A value outside its declared set is not compared: comparing it
    # is what produced the 13/13 pass on an all-NaN interval column.
    fails = check_schema(header, rows)
    print(f"  schema: {len(FIELDS)} declared fields, {len(ENUMS)} closed value sets, "
          f"{'REJECTED' if fails else 'every cell inside its domain'}")
    if fails:
        report(fails, "SAVED SUMMARY IS NOT A VALID ARTIFACT")

    saved = {r["circuit"]: r for r in rows}
    for c in [c for c in circuits if c not in saved]:
        fails.append(f"{c}: in the frozen selection, ABSENT from the saved summary")
    for c in [c for c in saved if c not in circuits]:
        fails.append(f"{c}: in the saved summary, NOT in the frozen selection")
    if len(rows) != len(circuits):
        fails.append(f"row count {len(rows)} != frozen selection {len(circuits)}")
    if fails:
        report(fails, "SAVED SUMMARY IS NOT THE FROZEN SELECTION")

    if args.schema:
        print("\n  ✓ the saved summary is a valid artifact: every cell inside its "
              "declared\n    domain, every row internally coherent. The replay was not "
              "run (--schema).\n")
        return

    print(f"  replaying prereg_analysis.analyse for {len(circuits)} circuits "
          f"(original MC bootstrap, original seeds)")
    checked = 0
    rng = np.random.default_rng(20260906)
    for c in circuits:
        live = pa.analyse(c, 0.10, 3, rng)
        row = saved[c]
        for f, (kind, tol) in fields.items():
            want = live.get(f)
            got = parse(kind, row[f])          # already proved to be in-domain above
            if want is None and got is None:
                continue
            if want is None or got is None:
                fails.append(f"{c}.{f}: saved {row[f]!r}, replay {want!r}")
                continue
            checked += 1
            if kind in ("str", "bool", "int", "count"):
                if got != (want if kind != "bool" else bool(want)):
                    fails.append(f"{c}.{f}: saved {got!r} != replay {want!r}")
            else:
                if abs(float(got) - float(want)) > tol:
                    fails.append(f"{c}.{f}: saved {got!r} != replay {float(want):.10g} "
                                 f"(|diff| {abs(float(got)-float(want)):.3g} > {tol:g})")

    print(f"  {checked} saved values compared against the replay")
    if fails:
        iv = [f for f in fails if ".error_ci_" in f]
        if iv:
            print(f"\n  RISK INTERVAL MISMATCH on {len(iv)} field(s). The published "
                  f"uncertainty is\n  not the uncertainty this data produces.")
        report(fails, "SAVED SUMMARY DOES NOT MATCH ITS OWN ANALYSIS")
    print("\n  ✓ every saved primary field is inside its declared domain, internally "
          "coherent,\n    and equal to a replay of its own analysis.\n")


def report(fails, headline):
    print(f"\n  ✗ {headline} — {len(fails)} problem(s):\n")
    for f in fails[:30]:
        print(f"      {f}")
    if len(fails) > 30:
        print(f"      … and {len(fails) - 30} more")
    print()
    sys.exit(1)


if __name__ == "__main__":
    main()
