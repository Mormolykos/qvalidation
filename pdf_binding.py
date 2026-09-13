"""The published PDF must carry the same active claims as the manuscript it came from.

WHY
    The PDF is what a reviewer actually opens. `manuscript_binding.py` checks `PAPER.md`;
    nothing checked that the rendered artifact agreed with it, so a stale PDF built before
    a correction would ship claims the source had already withdrawn. Astra A13 exposed the
    adjacent gap — the build inputs were not archived at all — and this closes the
    consistency half.

TWO REPRODUCIBILITY TARGETS, and only one is promised
    A. SEMANTIC — the PDF's extractable text carries the same active claims and the same
       primary numbers as PAPER.md. **Promised, and checked here.**
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


def pdf_text():
    if not os.path.isfile(PDF):
        sys.exit(f"  no {os.path.relpath(PDF, ROOT)} — run publish/build_paper.sh first")
    for tool in (["pdftotext", PDF, "-"],):
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


def main():
    txt = pdf_text()
    src = open(PAPER, encoding="utf-8").read()
    print(f"\n  PUBLISHED PDF BOUND TO THE MANUSCRIPT")
    print(f"  {os.path.getsize(PDF):,} bytes, {len(txt):,} extractable characters\n")

    fails = []

    # 1. the canonical endpoint table, as the READER sees it in the PDF
    from manuscript_binding import visible_text, parse_tables, find_endpoint_tables
    cand = find_endpoint_tables(parse_tables(visible_text(src)))
    if len(cand) != 1:
        fails.append(f"{len(cand)} canonical endpoint tables in PAPER.md; expected 1")
    else:
        _, body, _ = cand[0]
        for row in body:
            m = re.search(r"(\d+)\s*/\s*(\d+)", row[1] if len(row) > 1 else "")
            if not m:
                continue
            num, den = m.group(1), m.group(2)
            # pdftotext renders "12 / 26" with variable spacing
            pat = re.compile(rf"\b{num}\s*/\s*{den}\b")
            if not pat.search(txt):
                fails.append(f"row '{row[0]}': {num}/{den} is in PAPER.md but not in "
                             f"the PDF — the PDF is stale")

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
            print(f"  version line: {want}")

    print(f"  withdrawn claims checked: {len(WITHDRAWN)}")
    if fails:
        print(f"\n  ✗ PDF AND MANUSCRIPT DISAGREE — {len(fails)} problem(s):\n")
        for f in fails:
            print(f"      {f}")
        print()
        sys.exit(1)
    print("\n  ✓ the PDF carries the manuscript's active claims and primary numbers.")
    print("    (semantic reproduction; byte-identical PDFs are not promised)\n")


if __name__ == "__main__":
    main()
