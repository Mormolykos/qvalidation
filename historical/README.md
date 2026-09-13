# Historical artifacts — SUPERSEDED, not current evidence

Everything under this directory is **kept for provenance and is not the current state of
the work**. No file here may be cited as scientific support, and no verifier stage treats
anything here as authoritative.

It is retained rather than deleted because deleting the record of what was once claimed
would make the correction history unauditable — which is the opposite of the point.

## `2026-09-04-v1-bundle/`

The publication bundle prepared for **Zenodo v1**, 2026-09-04. Its `PAPER.md` is the v1
manuscript and **contradicts the current one**. It still asserts claims that have since
been withdrawn on the record:

| claim in the v1 bundle | status now |
|---|---|
| "Benchpress … sets no transpiler seed anywhere" | withdrawn v2 — narrowed to the Qiskit gym at the pinned revision |
| "identifies the mechanism that governs it" | withdrawn v2 — no compiler mechanism is identified |
| "independent of the version pair" (ambiguity band) | withdrawn v2 — the band inherits this pair's residuals |
| risk is monotone decreasing in \|θ − t\| "for any distribution" | withdrawn v3 — **false**, with a counterexample and our own data against it |
| synthetic null, mean −0.661 over 30 trials | withdrawn v3 — no generator exists anywhere in the pinned tree |
| `knn_341` issue figure "+41.0%" | corrected v4 — the issue reports **+44.060%** |
| "6 of 1728 triples" | withdrawn v3 — no such sample ever existed |

It was moved here in v4 (Astra A04) because an obsolete reader-facing manuscript sitting
in `bundle/` at the repository root is indistinguishable, to anyone browsing the archive,
from the current one. The location is now unmistakable.

**For the current manuscript, read `PAPER.md` at the repository root.** For what changed
and why, read `V3_CORRECTION_LEDGER.md` and `V4_ASTRA_CORRECTION_LEDGER.md`.
