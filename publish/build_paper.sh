#!/bin/bash
# Build paper.pdf from PAPER.md. Archived in v4 (Astra A13): before this, the PDF could
# not be regenerated from the repository at all -- paper_style.css lived outside it, on
# the author's desktop, so the published artifact depended on a file no reader had.
#
# TWO REPRODUCIBILITY TARGETS, and only one of them is promised:
#
#   A. SEMANTIC / TEXT      the PDF's extractable text and layout reproduce from PAPER.md.
#                           This IS promised and is checked by pdf_binding.py.
#   B. BYTE-IDENTICAL PDF   NOT promised. Chromium embeds a creation timestamp and
#                           producer metadata, so two builds of identical input differ in
#                           bytes. Do not expect the SHA-256 to match a published one.
#
# Tool versions used for the v4 build, recorded because "pandoc" is not a version:
#   pandoc   3.9.0.2
#   chrome   152.0.7977.83  (headless, --print-to-pdf)
#   platform Windows-10-10.0.26200-SP0
set -e
cd "$(dirname "$0")/.."
OUT="${1:-publish/paper.pdf}"
pandoc PAPER.md   --from=markdown+pipe_tables+raw_html   --to=html5 --standalone   --css=publish/paper_style.css   --output=publish/paper.html
"/c/Program Files/Google/Chrome/Application/chrome.exe"   --headless=new --disable-gpu --no-sandbox   --print-to-pdf="$(pwd -W)/$OUT"   --print-to-pdf-no-header --no-pdf-header-footer   --virtual-time-budget=15000   "file:///$(pwd -W)/publish/paper.html"
echo "built $OUT"
