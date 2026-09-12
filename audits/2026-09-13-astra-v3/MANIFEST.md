# Astra final hostile audit of v3 — preserved evidence, 2026-09-13

Immutable audit evidence. Never edited, reformatted or corrected in place — including
where this project disputes a finding. Disputes go in `V4_ASTRA_CORRECTION_LEDGER.md`.

## Target

qvalidation v3 at `839ac80cd36ac44c7bab12e3b5a19c9dceb95c76`. The audit ran in disposable
sibling clones under `C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj`; this
repository was not modified.

## Verdict

**CORE SURVIVES MAJOR CORRECTIONS.** Findings A01–A14, attacks defeated N01–N06, **no
fatal invalidation of the empirical endpoint**.

Independently reproduced: 15,600 observations · 36 resolved / 3 unresolved · 26 eligible ·
**12/26, 7/26, 4/26** · all 36 original risk-bootstrap intervals · ~10.9 pp modelled
transition width · k=20 risk 3.7414736766%.

## The three attacks that defeated v3

The v3 verifier was built to prove it could turn red. It did — for the attacks v3's author
thought of. Astra found three it did not:

| | mutation | v3 result | finding |
|---|---|---|---|
| **H** | all 36 saved risk intervals → `[0.900000, 0.999999]`, flags and counts untouched | **9/9 PASS** | A01 |
| **K** | visible results table → `0/26, 0/26, 0/26`, correct rows hidden in an HTML comment | **9/9 PASS** | A02 |
| **F** | one raw observation `7315 → 7316`, then regenerate the manifest | **9/9 PASS** | A03 |

Each defeats a different layer. H corrupts derived science the reconstruction never
compared. K corrupts what the reader sees while satisfying a substring search. F changes
the evidence *and* the record of the evidence together, which a manifest stored beside the
data can never detect.

A fourth, **I**, changes the external issue figure `+44.060% → +94.060%` and is caught by
nothing — no stage binds external claims.

## Preserved bytes

| file | SHA-256 |
|---|---|
| `ASTRA_FINAL_HOSTILE_AUDIT.md` | `b21fce40d95b1322…` |
| `ASTRA_FINAL_HOSTILE_AUDIT_PACKAGE.zip` | `cfa7e43669186f44…` |
| `AUDIT_FILES_SHA256.txt` | `61a3a40c164ad6ee…` |
| `FRESH_CLAIM_LEDGER.md` | `52b4d9b2a7a40eda…` |
| `MUTATION_TEST_LEDGER.md` | `78f312e2a3fd8d22…` |
| `REPRODUCTION.md` | `645a3287a41a3bf3…` |

Full hashes are in `AUDIT_FILES_SHA256.txt`, which is itself hashed above. `package/`
holds all 101 extracted entries — 13 reproduction scripts, 47 logs, 31 evidence JSON —
byte-identical to the zip, extracted so they can be read and diffed rather than only
stored.

`FRESH_CLAIM_LEDGER.md` was built before the auditor read any prior review.

## Why this keeps happening, stated plainly

v2's verifier was defeated by corrupting raw data. v3 fixed that and was defeated by
corrupting the *saved analysis*, the *visible manuscript*, and the *evidence record*.

The pattern is not that each verifier was careless. It is that a verifier only tests the
attacks its author imagined, and the author is the worst-placed person to imagine them.
That is an argument for keeping a hostile auditor, not for trusting the next green run.
