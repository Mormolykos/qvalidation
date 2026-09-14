# Astra differential review of the v4 repairs — preserved evidence

**Target reviewed:** `3643bbcdb30c595c4a6caf0e8b41f179a3c15cdb`
**Previous review:** `4531d97d754c9f116db567e1908cbb59d6016eb2`
**Verdict as delivered:** four findings CLOSED (V4-02, V4-06, V4-08, V4-10), six PARTIAL,
one new build-robustness defect. **CORE SURVIVES MAJOR CORRECTIONS.**

| SHA-256 | bytes | file |
|---|---:|---|
| `218f0adecf7d7202fb7ab0205fa65754ab4ce922041843d1247d196f9aee96e0` | 10,181 | `REVIEW.md` |
| `f6510c25f2a3403f9d7f9ba87829f7fc238e6e49557385e60bd76608bef9b794` | 7,443 | `SHA256SUMS.txt` — the reviewer's own hashes of its evidence |
| — | 3.5 MB | `evidence/` — 85 files: scripts, per-case logs, rendered PNGs and PDFs |

Copied verbatim. They are **not** edited to agree with the repairs made in response to
them. `SHA256SUMS.txt` is the reviewer's hash list for its own evidence tree; it is
preserved so a third party can check that this copy is what Astra produced.

`audits/** -text` in `.gitattributes` keeps a checkout from rewriting line endings, so
those hashes hold on every platform — the defect recorded as A14, which this directory
would otherwise repeat.

## What this review established that the previous one could not

It re-ran the ORIGINAL reproducers rather than the repaired fixtures, and that is what
found the two material misses:

- **`evidence/abstract_original.md` / `abstract_original_render.png`** — the false
  abstract sentence, in numerals, visibly rendered in a freshly built PDF. Both stage 12
  and stage 13 returned 0. The repaired fixture used the word-number form and passed,
  which masked it.
- **`evidence/fault_diagnostic_then_runtime.log`** — a layer printing its expected
  rejection diagnostic and then raising, still classified REJECTED.

Both are now standing fixtures: mutations **W** and **X**, and the subprocess regression
`test_the_expected_diagnostic_followed_by_a_crash_is_an_error`.

## What it explicitly did NOT establish

- **Neither 13/13 nor 18/18 was certified here.** The reviewer's pristine runs died
  during host memory-commit exhaustion — 115,302,940,672 of 115,322,265,600 bytes
  committed, 99.98% — and one stage exit includes reviewer intervention to clear stalled
  `git archive` children. Those are host-resource events, not validation outcomes, and
  the review says so.
- The empirical endpoint was not independently reconstructed again. No discrepancy
  requiring it emerged, and both revisions carry the identical `results/raw/prereg` tree
  object `3114a270ccd78b0daaa2a1bc451dd15155d55c13`.
- A PATH-empty PDF check still finds an extractor by absolute candidate path, so its
  passing is **not** evidence of missing-tool handling; a separate controlled injection
  removing both discovery paths produced the intended prerequisite ERROR.
- One long-HTML PDF attempt reused a stale file because the reviewer's own PyMuPDF handle
  blocked the overwrite. Its apparent stage-13 PASS is marked invalid in the review, and
  that accident is what exposed the build defect now fixed as NEW-BUILD-01.

## Response

Every finding is dispositioned in
[`../../V4_ASTRA_CORRECTION_LEDGER.md`](../../V4_ASTRA_CORRECTION_LEDGER.md), Part 3.
