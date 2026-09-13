"""The published PDF must carry the same numbers as the manuscript it came from.

WHY
    The PDF is what a reviewer actually opens. `manuscript_binding.py` checks `PAPER.md`;
    nothing checked that the rendered artifact agreed with it, so a stale PDF built before
    a correction would ship claims the source had already withdrawn. Astra A13 exposed the
    adjacent gap — the build inputs were not archived at all — and this closes the
    consistency half.

WHAT DEFEATED THE FIRST VERSION OF THIS FILE (Astra V4-02)
    It looked for the endpoint fractions SOMEWHERE in the extracted text, a version
    string, and six withdrawn phrases. Astra changed the reader-visible `10.9` to `99.9`
    — the abstract of the published PDF then printed a transition width of 99.9
    percentage points — and all thirteen stages returned exit 0. Every string the checker
    looked for was still present, because the attack did not remove strings; it added one.

    Presence of what you expect is not absence of what you do not. So the binding is now
    stated over the WHOLE numeric content in both directions:

        the set of distinct numeric tokens in the PDF == the set in PAPER.md

    Measured on the v4 build: 699 tokens in the PDF, 697 in the source, 272 distinct on
    each side, and the two distinct sets are equal. A number that appears in the PDF and
    nowhere in the manuscript is an invention; a number in the manuscript that reaches no
    page is a drop. Both now fail, and 99.9 is an invention.

    Placement is checked for the canonical endpoint rows specifically: each row's label,
    fraction, proportion and interval must appear TOGETHER and in order in the PDF, not
    merely somewhere in it.

WHAT THIS STILL DOES NOT ESTABLISH — state it, do not imply otherwise
    Equal numeric content is not semantic equivalence. This file does NOT establish that
    every number sits in the sentence that means it, that the prose reads the same, that
    the layout is right, or that a substitution reusing a value already present elsewhere
    in the document would be caught. A documented human reading of the built PDF against
    PAPER.md remains a release requirement, and this check does not replace it.

TWO REPRODUCIBILITY TARGETS, and only one is promised
    A. NUMERIC / CLAIM-STRUCTURE — the PDF's extractable text carries the same numeric
       content, the same canonical rows in place, the same version line, and none of the
       withdrawn claims. **Promised, and checked here.**
    B. BYTE-IDENTICAL — two builds of identical input produce identical bytes. **Not
       promised.** Chromium stamps a creation timestamp and producer string into every
       PDF, so the SHA-256 differs between builds of the same source. Claiming otherwise
       would be a reproducibility promise that fails on the first attempt to check it.

USAGE
    bash publish/build_paper.sh publish/paper.pdf && python pdf_binding.py
"""

import os
import re
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

PDF = os.path.join(ROOT, "publish", "paper.pdf")
PAPER = os.path.join(ROOT, "PAPER.md")

# claims withdrawn on the record. None may appear as an assertion in the PDF.
WITHDRAWN = [
    "sets no transpiler seed anywhere",
    "identifies the mechanism that governs",
    "mechanistically explained",
    "independent of the version pair",
    "largely induced by the decision rule",
    "6 of 1728",
]

NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")
KEEP = re.compile(r"[^a-z0-9.,%/<>\[\]()+-]+")


def numbers(text):
    """Distinct numeric tokens, thousands separators normalised away."""
    return {m.group(0).replace(",", "") for m in NUMBER.finditer(text)}


def flatten(text):
    """Lowercased, ASCII-folded, whitespace-collapsed — so a line break inside a table
    cell and a dropped `≥` glyph do not read as a different document."""
    return " ".join(KEEP.sub(" ", text.lower()).split())


def pdf_text():
    if not os.path.isfile(PDF):
        sys.exit(f"  no {os.path.relpath(PDF, ROOT)} — run publish/build_paper.sh first")
    # -layout, not the default flow mode. Without it pdftotext reads the endpoint table
    # COLUMN-WISE -- "criterion risk > 0 … risk 5% risk 10%" on one line and every
    # numerator on another -- so no row can be checked as a row, and it joins text across
    # boxes, which turned "0009-0007-3805-170X" into the number 00073805. Layout mode
    # preserves both. (Found when the V4-08 stylesheet fix changed the rendering.)
    for tool in (["pdftotext", "-layout", PDF, "-"],):
        try:
            r = subprocess.run(tool, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=300)
            if r.returncode == 0 and len(r.stdout) > 1000:
                return r.stdout
        except FileNotFoundError:
            pass
    try:
        import fitz
        d = fitz.open(PDF)
        return "".join(p.get_text() for p in d)
    except Exception as exc:
        sys.exit(f"  cannot extract text from the PDF: {exc}")


def check(txt, src, echo=print):
    """Every binding between an extracted PDF text and its manuscript source.

    Split out from main() so a regression test can exercise the logic on a supplied text
    without a 20-second Chromium build — the V4-02 counterexample is a property of this
    function, and a test that cannot reach it is not a test of the defect.
    """
    fails = []

    from manuscript_binding import visible_text, parse_tables, find_endpoint_tables
    vis = visible_text(src)

    # 1. NUMERIC CONTENT, both directions. This is the binding; everything else narrows it.
    in_pdf, in_src = numbers(txt), numbers(vis)
    invented, dropped = sorted(in_pdf - in_src), sorted(in_src - in_pdf)
    echo(f"  numeric content: {len(in_pdf)} distinct tokens in the PDF, "
         f"{len(in_src)} in PAPER.md")
    for n in invented[:12]:
        ctx = next((m for m in re.finditer(rf"(?<![\d.]){re.escape(n)}(?![\d])", txt)),
                   None)
        where = txt[max(0, ctx.start() - 70):ctx.end() + 40].replace("\n", " ") \
            if ctx else ""
        fails.append(f"the PDF shows the number {n}, which appears NOWHERE in PAPER.md "
                     f"— a reader is being given a value the source does not contain"
                     + (f" — …{where.strip()}" if where else ""))
    for n in dropped[:12]:
        fails.append(f"PAPER.md states {n} and no page of the PDF carries it — the PDF "
                     f"is not a rendering of this manuscript")
    if len(invented) > 12 or len(dropped) > 12:
        fails.append(f"… {len(invented) - 12 if len(invented) > 12 else 0} further "
                     f"invented and {len(dropped) - 12 if len(dropped) > 12 else 0} "
                     f"further dropped numbers not listed")

    # 2. the canonical endpoint table, IN PLACE — label, fraction, proportion, interval
    #    contiguous and in order, so correct numbers cannot be attached to wrong rows
    flat = flatten(txt)
    cand = find_endpoint_tables(parse_tables(vis))
    if len(cand) != 1:
        fails.append(f"{len(cand)} canonical endpoint tables in PAPER.md; expected 1")
    else:
        _, body, _ = cand[0]
        placed = 0
        for row in body:
            want = flatten(" ".join(row))
            if not want:
                continue
            if want in flat:
                placed += 1
            else:
                fails.append(f"row '{row[0]}' does not appear as a row in the PDF: "
                             f"expected “{want[:70]}” — its cells are missing, "
                             f"reordered, or split across different rows")
        echo(f"  canonical table: {placed}/{len(body)} rows found intact in the PDF")

    # 2. no withdrawn claim asserted. Correction notes legitimately QUOTE them, so a hit
    #    is only a failure if PAPER.md does not also contain it inside a correction.
    for w in WITHDRAWN:
        in_pdf = w.lower() in txt.lower()
        if not in_pdf:
            continue
        near = [m.start() for m in re.finditer(re.escape(w), src, re.I)]
        quoted = all(
            any(k in src[max(0, i - 400):i + 200].lower()
                for k in ("correction", "withdraw", "earlier versions", "v1–v3",
                          "v1-v3", "superseded"))
            for i in near) if near else False
        if not quoted:
            fails.append(f"withdrawn claim asserted in the PDF: “{w}”")

    # 3. version line agreement
    m = re.search(r"\*Version (\d+), (\d{4}-\d{2}-\d{2})", src)
    if m:
        want = f"Version {m.group(1)}, {m.group(2)}"
        if want not in txt:
            fails.append(f"PDF does not carry the manuscript's version line “{want}” — "
                         f"it was built from a different source")
        else:
            echo(f"  version line: {want}")

    echo(f"  withdrawn claims checked: {len(WITHDRAWN)}")
    return fails


def main():
    txt = pdf_text()
    src = open(PAPER, encoding="utf-8").read()
    print(f"\n  PUBLISHED PDF BOUND TO THE MANUSCRIPT")
    print(f"  {os.path.getsize(PDF):,} bytes, {len(txt):,} extractable characters\n")

    fails = check(txt, src)
    if fails:
        print(f"\n  ✗ PDF AND MANUSCRIPT DISAGREE — {len(fails)} problem(s):\n")
        for f in fails:
            print(f"      {f}")
        print()
        sys.exit(1)
    print("\n  ✓ the PDF's numeric content equals the manuscript's in both directions,")
    print("    the canonical rows appear intact, the version line agrees, and no")
    print("    withdrawn claim is asserted.")
    print("    NOT established here: that each number sits in the sentence that means")
    print("    it, prose equivalence, or layout. A documented human reading of the")
    print("    built PDF against PAPER.md is still required before release.")
    print("    (byte-identical PDFs are not promised)\n")


if __name__ == "__main__":
    main()
