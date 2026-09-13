#!/bin/bash
# Build paper.pdf from PAPER.md. Archived in v4 (Astra A13): before this, the PDF could
# not be regenerated from the repository at all -- paper_style.css lived outside it, on
# the author's desktop, so the published artifact depended on a file no reader had.
#
# THE STYLESHEET PATH (Astra V4-08). This script used to pass
# --css=publish/paper_style.css while emitting the HTML INTO publish/, so the href
# resolved to publish/publish/paper_style.css, which does not exist. Every PDF built by
# this script was therefore rendered with no stylesheet at all, silently: a missing
# stylesheet produces a readable page, not an error. Correcting it changes the document
# from 12 pages to 14. The href is relative to the HTML, so it must not carry the
# directory the HTML already lives in -- and the smoke check below now resolves it and
# fails the build rather than letting the next person discover this the same way.
#
# TWO REPRODUCIBILITY TARGETS, and only one of them is promised:
#
#   A. NUMERIC / CLAIM STRUCTURE  the PDF's extractable text carries the same numeric
#                           content as PAPER.md in both directions, the same canonical
#                           rows in place, and the same version line. This IS promised
#                           and is checked by pdf_binding.py.
#   B. BYTE-IDENTICAL PDF   NOT promised. Chromium embeds a creation timestamp and
#                           producer metadata, so two builds of identical input differ in
#                           bytes. Do not expect the SHA-256 to match a published one.
#
# LAYOUT IS NOT VERIFIED. pdf_binding.py reads extracted text; it does not compare page
# geometry, pagination or typography, and must not be described as doing so.
#
# Tool versions used for the v4 build, recorded because "pandoc" is not a version:
#   pandoc   3.9.0.2
#   chrome   152.0.7977.83  (headless, --print-to-pdf)
#   platform Windows-10-10.0.26200-SP0
set -e
cd "$(dirname "$0")/.."
OUT="${1:-publish/paper.pdf}"

pandoc PAPER.md \
  --from=markdown+pipe_tables+raw_html \
  --to=html5 --standalone \
  --css=paper_style.css \
  --output=publish/paper.html

# SMOKE CHECK: every local asset the generated HTML references must resolve, relative to
# the HTML itself. A build that silently drops its stylesheet is the defect above.
grep -o 'href="[^"#?:]*\.css"' publish/paper.html | sed 's/.*href="//; s/"$//' |
while read -r css; do
  if [ ! -f "publish/$css" ]; then
    echo "build_paper.sh: stylesheet href '$css' does not resolve to publish/$css" >&2
    exit 1
  fi
  echo "  stylesheet resolves: publish/$css"
done

"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf="$(pwd -W)/$OUT" \
  --print-to-pdf-no-header --no-pdf-header-footer \
  --virtual-time-budget=15000 \
  "file:///$(pwd -W)/publish/paper.html"
echo "built $OUT"
