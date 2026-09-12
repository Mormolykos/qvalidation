"""What the READER sees, bound to what the data says.

WHY (Astra A02)
    v3 checked the manuscript with substring search. Astra set the visible results table
    to 0/26, 0/26, 0/26 and hid the correct rows in an HTML comment. Every string the
    checker looked for was present, so the full verifier returned **9/9 PASS** while the
    published primary claim read zero.

    Substring search asks "does this text exist somewhere in the file". A reader asks
    "what does the table say". Those are different questions, and only the second one is
    the claim. Presence is not placement -- a weakness this project has now been bitten by
    three times, and patched twice; this file replaces the approach instead.

WHAT THIS DOES
    1. Deletes HTML comments FIRST. Anything a reader cannot see cannot satisfy a check.
    2. Parses GitHub-flavoured Markdown tables structurally -- header, alignment row, body
       -- rather than matching text.
    3. Requires EXACTLY ONE table carrying the primary endpoint rows. Two tables is an
       ambiguity, not a convenience: a second one lets an attacker leave a correct table
       somewhere while the read table lies. Zero is a missing claim.
    4. Parses "12 / 26" into numerator AND denominator and checks both.
    5. Compares them to a reconstruction from RAW, not to a stored expectation.

    It also scans the visible text for endpoint-shaped fractions outside that table which
    contradict it, so a false claim cannot be smuggled into prose.

USAGE
    python manuscript_binding.py
    python manuscript_binding.py --show    # print the table as parsed
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

PAPER = os.path.join(ROOT, "PAPER.md")
SELECTED = os.path.join(ROOT, "_selected.txt")

# the three canonical rows, by the label a reader reads
ROWS = {"risk > 0": "excl", "risk ≥ 5%": "ge5", "risk ≥ 10%": "ge10"}

COMMENT = re.compile(r"<!--.*?-->", re.S)
FRACTION = re.compile(r"(\d+)\s*/\s*(\d+)")


def visible_text(raw):
    """The manuscript with everything invisible removed."""
    return COMMENT.sub("", raw)


def parse_tables(text):
    """Every GFM table, as (header, rows) with cells split on '|'."""
    lines = text.splitlines()
    tables, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and i + 1 < len(lines) \
                and re.fullmatch(r"\s*\|[\s:|-]+\|\s*", lines[i + 1]):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            body, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                body.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            tables.append((header, body, i + 1))
            i = j
        else:
            i += 1
    return tables


def find_endpoint_tables(tables):
    """Tables whose first column carries the canonical endpoint labels."""
    out = []
    for header, body, line in tables:
        labels = [r[0] for r in body if r]
        if all(any(lbl.startswith(k) for lbl in labels) for k in ROWS):
            out.append((header, body, line))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    raw = open(PAPER, encoding="utf-8").read()
    vis = visible_text(raw)
    hidden = len(COMMENT.findall(raw))

    print(f"\n  RENDERED MANUSCRIPT BOUND TO RAW DATA")
    print(f"  {len(raw):,} bytes, {hidden} HTML comment block(s) removed before parsing\n")

    fails = []
    cand = find_endpoint_tables(parse_tables(vis))

    if len(cand) == 0:
        print("  ✗ no VISIBLE table carries the primary endpoint rows.")
        hidden_cand = find_endpoint_tables(parse_tables(raw))
        if hidden_cand:
            print("    A table with those rows exists but is inside an HTML comment, so")
            print("    the reader never sees it. A commented claim is not a claim.")
        sys.exit(1)
    if len(cand) > 1:
        print(f"  ✗ {len(cand)} visible tables carry the primary endpoint rows "
              f"(lines {[c[2] for c in cand]}).")
        print("    Exactly one canonical table is required: with two, which one is the")
        print("    claim is decided by the checker's search order, not by the author.")
        sys.exit(1)

    header, body, line = cand[0]
    print(f"  one canonical table, line {line}: {header}")

    from raw_endpoint import reconstruct, endpoint
    circuits = [c.strip() for c in open(SELECTED) if c.strip()]
    elig, excl, ge5, ge10 = endpoint(reconstruct(circuits))
    truth = {"excl": len(excl), "ge5": len(ge5), "ge10": len(ge10)}
    n_elig = len(elig)
    print(f"  reconstructed from raw: {truth['excl']}/{n_elig}, {truth['ge5']}/{n_elig}, "
          f"{truth['ge10']}/{n_elig}\n")

    seen = set()
    for row in body:
        label = row[0]
        key = next((v for k, v in ROWS.items() if label.startswith(k)), None)
        if key is None:
            continue
        seen.add(key)
        m = FRACTION.search(row[1] if len(row) > 1 else "")
        if not m:
            fails.append(f"row '{label}': no 'n / d' fraction in the circuits column")
            continue
        num, den = int(m.group(1)), int(m.group(2))
        if args.show:
            print(f"    {label:<34} {num}/{den}")
        if num != truth[key]:
            fails.append(f"row '{label}': numerator {num} != {truth[key]} "
                         f"reconstructed from raw")
        if den != n_elig:
            fails.append(f"row '{label}': denominator {den} != {n_elig} eligible "
                         f"circuits reconstructed from raw")
    for k in ROWS.values():
        if k not in seen:
            fails.append(f"canonical table is missing the '{k}' row")

    # A contradicting fraction elsewhere in visible prose. The manuscript legitimately
    # QUOTES numbers a corruption would produce -- §6.1 describes the audit that moved the
    # endpoint to 11/26 -- so a paragraph that is explicitly about an attack or a
    # withdrawal is exempt. The count of exemptions is printed: an exemption nobody can
    # see is how the next hole gets in.
    COUNTERFACTUAL = ("corrupt", "mutation", "attack", "audit", "withdraw", "would",
                      "v3 correction", "earlier versions", "changes the true endpoint")
    tbl_span = "\n".join("|".join(r) for r in body)
    paragraphs = [(mm.start(), mm.group(0)) for mm in re.finditer(r"[^\n]+(?:\n[^\n]+)*",
                                                                  vis)]

    def enclosing(pos):
        best = ""
        for start, text in paragraphs:
            if start <= pos < start + len(text):
                best = text
        return best.lower()

    exempt = 0
    for m in FRACTION.finditer(vis):
        num, den = int(m.group(1)), int(m.group(2))
        if den != n_elig or m.group(0) in tbl_span or num in truth.values():
            continue
        para = enclosing(m.start())
        if any(w in para for w in COUNTERFACTUAL):
            exempt += 1
            continue
        ctx = vis[max(0, m.start() - 60):m.end() + 20].replace("\n", " ")
        fails.append(f"visible prose asserts {num}/{den}, which no endpoint supports "
                     f"— …{ctx.strip()[-90:]}")
    print(f"  prose scan: {exempt} endpoint-shaped fraction(s) exempted as explicitly "
          f"counterfactual")

    if fails:
        print(f"  ✗ THE VISIBLE MANUSCRIPT DOES NOT MATCH THE RAW DATA — "
              f"{len(fails)} problem(s):\n")
        for f in fails[:20]:
            print(f"      {f}")
        print()
        sys.exit(1)
    print("  ✓ the table a reader sees states what the raw data produces.\n")


if __name__ == "__main__":
    main()
