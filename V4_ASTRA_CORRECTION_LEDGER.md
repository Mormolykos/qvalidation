# v4 correction ledger — every Astra finding against v3

Audit: `audits/2026-09-13-astra-v3/` (`ASTRA_FINAL_HOSTILE_AUDIT.md`, SHA-256
`b21fce40d95b1322…`), against v3 at `839ac80cd36ac44c7bab12e3b5a19c9dceb95c76`.

**Verdict as delivered: CORE SURVIVES MAJOR CORRECTIONS.** A01–A14, six attacks defeated
(N01–N06), **no fatal invalidation of the empirical endpoint**.

**No raw measurement changed.** `results/raw/prereg/*.jsonl` is byte-identical to v2, now
enforced against v2's git objects rather than a local file.

---

## The three that made v3's central claim false

v3's argument was that its verifier had been *shown* to turn red. Astra showed it turned
red only for the attacks v3's author had thought of.

| | attack | v3 | v4 catches it with | proof |
|---|---|---|---|---|
| **A01** | all 36 saved risk intervals → `[0.900000, 0.999999]` | **9/9 PASS** | `derived_binding.py` | mutation H |
| **A02** | visible table → `0/26`, correct rows in an HTML comment | **9/9 PASS** | `manuscript_binding.py` | mutation K |
| **A03** | one raw observation edited, manifest regenerated | **9/9 PASS** | `v2_anchor.py` | mutation F |

Each defeats a different layer, and none of them touches the science: the endpoint
reconstructs to 12/26, 7/26, 4/26 throughout.

---

## Findings

| ID | Sev | Defect | Accepted? | Correction | New test | Endpoint moves? | Status |
|---|---|---|---|---|---|---|---|
| **A01** | MAJOR | saved bootstrap intervals replaceable; nothing compared them | **ACCEPTED** — reproduced, 9/9 PASS | `derived_binding.py` replays the **original** MC stream (400 × 400,000, `rng(20260905)`) — contract A, not a substituted estimator — and binds **690 saved values** across 18 fields including row membership | mutation **H** → FAIL naming interval mismatch | No | **CLOSED** |
| **A02** | MAJOR | substring search certified a false visible table | **ACCEPTED** — reproduced | `manuscript_binding.py` strips HTML comments first, parses tables structurally, requires **exactly one** canonical endpoint table, checks numerator **and** denominator against a raw reconstruction, and scans prose for contradicting fractions | mutations **K**, **L** (duplicate table), **M** (denominator only) → FAIL | No | **CLOSED** |
| **A03** | MAJOR | a manifest beside the evidence cannot detect a change to both | **ACCEPTED** — reproduced | `v2_anchor.py` anchors to **v2's git objects** at `17e08f3`, on canonical LF bytes, over all **858** anchored evidence files — **78 primary measurement arms** (39 circuits x 2) plus the 780 per-process fragments they were merged from, which are the same observations before merge and not additional measurements. Offline transcript written *from* v2 objects, refusing to run without them. Self-consistency and historical identity are now separate contracts and the failure message says which was violated | mutations **F**, **N** → FAIL | No | **CLOSED** |
| **A04** | MAJOR | withdrawn claims still active in the staged archive | **ACCEPTED** | `bundle/` → `historical/2026-09-04-v1-bundle/` with a SUPERSEDED banner and a README listing all seven withdrawn claims. `SETTLED.json` S11 and S04 no longer offer withdrawn evidence as support and say so explicitly. Stale `+41%` removed from `decision_error.py` | — | No | **CLOSED** |
| **A05** | MAJOR | categorical "unresolvable" language survived its own correction | **ACCEPTED** | §4.3 restated as the 5%–95% transition width under the stated model, pair, k and threshold; asymmetry noted | — | No | **CLOSED** |
| **A06** | MAJOR | abstract kept "largely induced by the decision rule" | **ACCEPTED** | Removed. The quantitative attribution died with the synthetic null in v3 and is not reinstated; thresholding is described qualitatively | — | No | **CLOSED** |
| **A07** | MAJOR | issue comparison asserted an unavailable protocol; `+41%` survived in prose | **ACCEPTED** — v3 fixed the table and not the background | `PAPER.md` §2.2 and `decision_error.py` now carry **+44.060%**; protocol-reproduction wording removed | — | **No** — a corrected transcription | **CLOSED** |
| **A08** | MAJOR | determinism asserted beyond the controls | **ACCEPTED** | "deterministic function of *s*" → reproduced in every control we ran, with the unseeded backend constructor and the 0-of-24 probe stated as a limited negative result | — | No | **CLOSED** |
| **A09** | MINOR | commit order described as first-access evidence | **ACCEPTED** | Narrowed: git establishes committed order, not first access, not the absence of uncommitted data, not clock truthfulness | — | No | **CLOSED** |
| **A10** | MINOR | matching rustworkx build not established by the artifacts | **ACCEPTED** | The records contain no rustworkx field; "both ran 0.18.1" is labelled a retrospective author assertion. The limitation is unchanged and is the stronger reading | — | No | **CLOSED** |
| **A11** | MINOR | no-aggregation scope inconsistent | **ACCEPTED** | Narrowed to the inspected QASMBench gate-count path; the transpiler-service gym noted as a different path; the BQSKit claim scoped to inspected files | — | No | **CLOSED** |
| **A12** | MINOR | exact threshold ties misclassified by float comparison | **ACCEPTED** — `110/100−1 = 0.10000000000000009 > 0.10` | `TIE_EPS` guard in **both** reconstruction paths; an endpoint within 1e-9 of the cut sits *on* it → UNRESOLVED, per the declared inclusive policy. Estimator description corrected: exact **cutoff**, float **weights** | 8 tests in `tests/test_threshold_ties.py` | **No** — closest recorded endpoint is 2.3e-3, 2.3 million × the guard | **CLOSED** |
| **A13** | MINOR | PDF build input unarchived | **ACCEPTED** | `publish/paper_style.css` and `publish/build_paper.sh` tracked, with pandoc 3.9.0.2 and Chromium 152.0.7977.83 recorded. Two targets stated separately: semantic reproduction **promised**, byte-identical PDF **not** | — | No | **CLOSED** |
| **A14** | MAJOR | pin bound to CRLF checkout bytes | **ACCEPTED** — measured: **0 of 5** match on LF | `pin_check.py` compares canonical bytes from git blobs at `b695f30e`, falling back to LF-normalised working tree, reporting which source it used. `benchpress_pin.json` is **not** rewritten — it is what v1–v3 recorded and stays as evidence | line-ending test in `tests/test_threshold_ties.py` | No | **CLOSED** |

**14 of 14 accepted. None independently rejected.** Four were re-derived here rather than
taken on the auditor's word — A12 (the float comparison), A14 (0/5, measured), A03 (mutation
F reproduced), A07 (the stale prose found by grep, which v3 had missed).

---

## Attacks Astra ran and defeated

| ID | Outcome |
|---|---|
| N01 | primary empirical chain survives — 15,600 observations, 36/3, 26 eligible, 12/26, 7/26, 4/26 |
| N02 | raw measurement identity survives |
| N03 | conditional bootstrap scope and chosen estimand survive |
| N04 | corrected auxiliary results survive |
| N05 | pinned source and gate-count replication survive within their stated measurements |
| N06 | staged PDF content and archive identity survive |

---

## The verifier, in layers

| # | layer | question it answers |
|---|---|---|
| 10 | `v2_anchor.py` | is this the evidence v2 published? (git objects, not a local file) |
| 8 | `raw_integrity.py` | do current bytes agree with the current manifest, and is the summary reproducible from raw? |
| 7 | `raw_endpoint.py` | does the raw data produce the headline, by an independent estimator? |
| 11 | `derived_binding.py` | does every saved field reproduce from a replay of its own analysis? |
| 12 | `manuscript_binding.py` | does the table a **reader sees** state that? |
| 9 | `mutation_test.py` | can any of the above actually turn red? |

No layer substitutes for another. Mutation B is the standing proof: one gate count changed
by 1 does not move a coarse integer endpoint, so `science` correctly passes and only
`integrity` and `anchor` catch it.

**Mutation results** — pristine passes all five layers:

| | mutation | science | integrity | anchor | derived | rendered |
|---|---|---|---|---|---|---|
| A | whole raw arm → constant | FAIL | FAIL | FAIL | — | pass |
| B | one raw count +1 | pass | FAIL | FAIL | — | pass |
| C | raw ×1.09, verdict moves | FAIL | FAIL | FAIL | — | pass |
| D | saved point risk | pass | pass | pass | **FAIL** | pass |
| E | visible literal 7→9 | FAIL | pass | pass | — | FAIL |
| **F** | raw + manifest regenerated | pass | pass | **FAIL** | — | pass |
| **H** | all saved intervals faked | pass | pass | pass | **FAIL** | pass |
| **K** | false visible table, correct rows hidden | FAIL | pass | pass | — | **FAIL** |
| L | second contradicting table | pass | pass | pass | — | **FAIL** |
| M | wrong denominator only | pass | pass | pass | — | **FAIL** |
| N | raw + manifest regenerated together | pass | pass | **FAIL** | — | pass |

---

## Preserved science — unchanged, reconfirmed

15,600 observations · 36 resolved / 3 unresolved · 10 boundary exclusions · 26 eligible ·
**12/26, 7/26, 4/26** · all 36 original bootstrap intervals · ρ = −0.8329214038556598 as a
descriptive association · ~10.9 pp modelled transition width, scoped · k=20 `bv_n140` risk
3.7414736766% · corrected selection comparison 39 vs 13, p = 0.4559911843 · 216/216
cross-machine gate counts · the pinned Qiskit path omits `seed_transpiler`.

---

## Open limitations — labelled, not closed

1. **Seed law described, not repaired.** Restoring representativeness needs a rerun.
2. **Bootstrap coverage not established.** The intervals are conditional on the observed
   classification.
3. **Synthetic null withdrawn, not replaced.** No quantitative attribution of ρ.
4. **Sweep axis disclosed, not renormalised** (v3 F14).
5. **Backend randomness** probed at 0/24 only; not globally eliminated.
6. **rustworkx build** is an author assertion, not contemporaneous evidence.
7. **Byte-identical PDF reproduction is not promised** — Chromium stamps a timestamp.
8. **A verifier only tests the attacks someone thought of.** Three rounds have each ended
   with a green verifier that a hostile auditor then broke. This ledger records what has
   been tried, not that nothing remains.
