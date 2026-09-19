# v4 correction ledger — every Astra finding against v3, then against v4

> **Three audits, in order.** Part 1 is the v3 audit (A01–A14). Part 2 is the audit of
> the corrected v4 tree (V4-01…V4-10). Part 3 is the differential audit of Part 2's own
> repairs, which found that four of the ten were closed and six were not. Each part is
> the record of what the previous part's repairs still got wrong.

---

# Part 1 — every Astra finding against v3

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

---
---

# Part 2 — every Astra finding against v4

Audit: `audits/2026-09-13-astra-v4/` (`V4_FINAL_REPRODUCIBILITY_REVIEW.md`, SHA-256
`e19c245d7773f9ea…`), against v4 at `4531d97d754c9f116db567e1908cbb59d6016eb2`.

**Verdict as delivered: CORE SURVIVES MAJOR CORRECTIONS.** V4-01–V4-10; six of them
release-blocking; **no fatal counterexample to the empirical endpoint**.

**No raw measurement changed. No reported scientific number changed** except one that was
demonstrated wrong by recomputation from raw (V4-04: 14 → 13 deterministic circuits).

---

## The two that passed all thirteen stages

Part 1 closed with a verifier that had been shown to turn red for the attacks its author
had by then imagined. Astra found two states that were false and green end-to-end, and
two more that defeated the manuscript stage specifically.

| | attack | v4 | now caught by | mutation |
|---|---|---|---|---|
| **V4-01** | all 36 saved risk intervals → `NaN` | **13/13 PASS** | `derived_binding.check_schema` | **R** |
| **V4-02** | published PDF prints 99.9 where the source says 10.9 | **13/13 PASS** | `pdf_binding.check` | **U** |
| **V4-03a** | canonical table inside `<div style="display:none">` | stage 12 = 0 | `manuscript_binding.html_domain_violations` | **P** |
| **V4-03b** | 7/26 attributed to interval exclusion in the abstract | stage 12 = 0 | claim-identity binding | **Q** |

None of them touches the science. The endpoint reconstructs to 12/26, 7/26, 4/26
throughout, and Astra's own independent replay confirms all 36 original intervals to
≤ 5e-7.

---

## Findings

| ID | Sev | Defect | Accepted? | Correction | New test | Endpoint moves? | Status |
|---|---|---|---|---|---|---|---|
| **V4-01** | MAJOR | nonfinite values, fractional integers and duplicate rows all evaded saved-result validation | **ACCEPTED** — reproduced, 13/13 PASS | Parsing is now a **contract**, not a coercion. Every field declares the SET of values it admits (`prob`, `count`, `real`, `bool`, `str`) and a cell outside it is rejected by name **before** any comparison — because `abs(NaN − want) > tol` is False, so an out-of-domain value is not weakly checked, it is unchecked. Rows are read as a **list**: duplicate ids, embedded header rows and unknown columns fail. A third contract, SELF, was added: interval order, point inside its own interval, `error_excludes_zero` **recomputed** from the saved bound, `boundary` recomputed from the saved distance — all on the saved row alone, no replay | mutations **R**, **S**, **T**, **D**, **H**; 17 cases in `tests/test_v4_astra_regressions.py` | No | **CLOSED** |
| **V4-02** | MAJOR | PDF semantic agreement was token presence | **ACCEPTED** — reproduced, 13/13 PASS with a visibly false abstract | The binding is now over the **whole numeric content in both directions**: the set of distinct numeric tokens in the PDF must equal the set in `PAPER.md`. 272 distinct on each side; a number the PDF shows and the source lacks is an invention, one the source states and no page carries is a drop. Canonical rows are additionally checked **in place** — label, fraction, proportion and interval contiguous and in order — so correct numbers cannot be attached to wrong rows. Extraction switched to `pdftotext -layout`, without which the table extracts column-wise and no row can be checked as a row. **The claim is also narrowed**: equal numeric content is not semantic equivalence, and the output says so and states that a documented human reading of the built PDF remains a release requirement | mutation **U** (rebuilt through the real pandoc + Chromium path); 5 cases in `tests/test_v4_astra_regressions.py` | No | **CLOSED** |
| **V4-03** | MAJOR | Markdown source recognition described as reader-visible validation; a true numerator accepted for a false claim | **ACCEPTED** — both reproduced | Two repairs. (a) The **domain is declared**: `PAPER.md` is Markdown whose only raw HTML is a bare inline tag from a closed list. Anything else is REFUSED with the reason, because no amount of source reading decides whether a reader sees what arbitrary HTML governs — enumerating `display:none`, `hidden`, `visibility`, `font-size:0`, `aria-hidden` is the losing side of that game. Fenced code blocks are blanked before parsing. (b) **Claim identity**: every prose quantity over the eligible denominator is bound to the endpoint its own *sentence* names, by nearest claim phrase, so 7/26 is true of "risk ≥ 5%" and false of "excludes zero". The counterfactual exemption moved from paragraph to sentence scope — the abstract is one paragraph containing the word "withdrawn", which is exactly where Astra put the false attribution | mutations **P**, **Q**; 10 cases in `tests/test_v4_astra_regressions.py` | No | **CLOSED** |
| **V4-04** | MAJOR | active reader-facing summaries retained withdrawn and false claims | **ACCEPTED** | `README.md`: issue differences corrected to **+0.29 pp / −0.63 pp**, compute **40 → 80 hours**, support **−17.68% to +109.17%**, mechanism language demoted to descriptive association, band marked as not independent of this version pair, and the verifier described as **13 stages taking tens of minutes** instead of "five read-only checks in about 45 seconds". `RESEARCH_LANDSCAPE.md` LIVE table: four rows relabelled CORRECTED/NARROWED with what changed, plus a banner naming `PAPER.md` as the authority. `ATTACK_PACKET.md` banner: it still said "nothing published. No DOI, no repository, no paper" | — | **YES, one** — see below | **CLOSED** |
| **V4-05** | MAJOR | active manuscript assurances contradicted their own limitations | **ACCEPTED** | Seven sentences narrowed to the formulations the corrections beside them already used: "a distribution its own protocol produces" → the three-run distribution **at our configuration** (twice); "before the primary raw data existed" → **before the first tracked commit** of it (§3.3 and the cross-machine check); "each count was reproduced from its seed" → the **144** and **216** counts those finite controls actually compared; "removes the sampling variance" → the **seed-attributable** variance, with the unseeded backend and the 0-of-24 probe stated; "every published figure carries … a function that recomputes it" → the inventory's actual **44 values, 32 raw-recomputed and 12 re-read from derived CSVs** | — | No | **CLOSED** |
| **V4-06** | MAJOR | offline consistency reported as authenticated historical identity | **ACCEPTED** | The two modes now say different things, because they check different things. With v2 history: "HISTORICAL IDENTITY … establishing this falsely would require rewriting history at `17e08f3e`". Without it: "matches the supplied transcript. **HISTORICAL AUTHENTICITY IS NOT ESTABLISHED HERE** — anyone who changed both would pass this check." The transcript's own metadata carries `_not_authenticated_by_itself`, and the header records that Astra's externally published SHA-256 of it is the binding the offline mode lacks — deliberately **not** stored in the checker, since a reference beside what it authenticates has the same defect. "byte-identical" → "canonical content", which is what LF normalisation actually gives | mutations **F**, **N** (both exercise the fallback, as archives have no history) | No | **CLOSED** |
| **V4-07** | MINOR | negative-test acceptance could not distinguish rejection from crash | **ACCEPTED** | Three outcomes, not two: a layer that **REJECTS** prints `✗` and exits nonzero; a layer that **ERRORS** exits nonzero and prints no `✗`; only a rejection counts. On top of that every mutation declares, **per layer**, the reason it must be rejected for, quoted from the message that layer actually prints — so a layer that starts failing elsewhere stops counting as coverage. A fixture that errors a layer it does not target is itself a failure. Skipped fixtures are named in the output, never silent | mutation-table reasons; 2 cases in `tests/test_v4_astra_regressions.py`. Found immediately: the first scratch fixture written for V4-01 exited 1 on a missing import and would have scored as a catch | No | **CLOSED** |
| **V4-08** | MINOR | the documented build did not load its tracked stylesheet | **ACCEPTED** — measured: the href resolved to `publish/publish/paper_style.css`, which does not exist | `--css=paper_style.css`, since the HTML is emitted into `publish/`. A **smoke check** in the build script resolves every local stylesheet href and fails the build rather than producing a readable unstyled page. The PDF was rebuilt: **14 pages, 428,549 bytes**, correctly styled. Layout claims removed from `build_paper.sh` and `pdf_binding.py` — extracted text is compared, page geometry is not | the rebuild is the test; `pdf_binding.py` passes on the restyled artifact | No | **CLOSED** |
| **V4-09** | MINOR | the tie guard was a tolerance policy described as exact ordering | **ACCEPTED** | `prereg_analysis.py`'s header no longer says "IMPLEMENTS, WITHOUT DEVIATION". It states the rule as **"inclusive threshold with a 1e-9 tie band"**, gives the reason (`110/100 − 1` is `0.10000000000000009`), and states the cost Astra demonstrated: an endpoint strictly above or below but within 1e-9 of the cut is UNRESOLVED. Behaviour unchanged — the closest recorded endpoint is 2.3e-3, and `tests/test_threshold_ties.py` asserts that margin, so a future data set narrowing it fails rather than passing silently | 1 case in `tests/test_v4_astra_regressions.py` + the 8 existing tie tests | **No** | **CLOSED** |
| **V4-10** | MINOR | helper-level no-history hashing read as a stage-1 fallback | **ACCEPTED** | `pin_check.py` states the prerequisite: stage 1 requires a Benchpress **git checkout** at the pinned commit, not a copy of the files. Five matching hashes say the files have the expected content, not which revision they came from. A `None` commit now fails with that sentence rather than a bare mismatch. **No archive mode was added** — one that reported PASS on unattributable source would be the same conflation repaired in `v2_anchor.py` | the explicit `None` branch | No | **CLOSED** |

**10 of 10 accepted. None independently rejected.** Three were re-derived here rather than
taken on the auditor's word — V4-04's deterministic count (recomputed from raw: **13**,
not 14), V4-08's stylesheet path (resolved, and the rebuild moved the document from 12
pages to 14), and V4-07's crash-versus-rejection distinction, which the very first scratch
fixture written for V4-01 demonstrated by exiting 1 on a missing import.

---

## The one number that moved, and why

`README.md` and `RESEARCH_LANDSCAPE.md` said **"14 of 39 circuits are perfectly
deterministic"**. Recomputing from raw — both arms constant across all 200 seeds — gives
**13**, and all 13 are eligible, so 13 of the 26. The manuscript already said 13. The
summaries were wrong and are corrected; nothing downstream depended on 14.

No other reported number changed. The endpoint is 12/26, 7/26, 4/26, as it has been
through three audits and four independent reconstructions.

---

## The verifier, in layers — after v4

| # | layer | question it answers | what it does NOT answer |
|---|---|---|---|
| 10 | `v2_anchor.py` | is this the evidence v2 published? | without v2's git objects: nothing about authenticity |
| 8 | `raw_integrity.py` | do current bytes agree with the current manifest? | anything, if the manifest changed too — that is stage 10 |
| 7 | `raw_endpoint.py` | does raw data produce the headline, by a separate estimator? | it shares `load_seeded`, `BOUNDARY_PP` and `TIE_EPS`, so its independence is partial |
| 11 | `derived_binding.py` | is every saved field in its domain, coherent, and equal to a replay? | it replays the producer; it is a binding, not an independent recomputation |
| 12 | `manuscript_binding.py` | does the table a reader sees state that, and does each prose claim carry its own number? | anything, for a manuscript outside the declared HTML domain — it refuses instead of guessing |
| 13 | `pdf_binding.py` | does the PDF carry the same numbers, and the canonical rows in place? | semantic equivalence, placement of every number, layout |
| 9 | `mutation_test.py` | can each of the above actually turn red, for the right reason? | whether an attack nobody has thought of would pass |

**Mutation results — 18 corruptions, each REJECTED by the layer that must catch it, for a
declared reason.** Pristine passes all six layers. New in this round: **P**, **Q**, **R**,
**S**, **T**, **U** (the six that defeated v4) and **V**.

**V** exists because R, D and H are now stopped by the schema and self-consistency
contracts before the replay runs — stricter, but it would have left the replay itself
unexercised. V widens one saved bound by 0.01: finite, inside [0, 1], above the point
estimate, every flag still correct. Nothing about the row is self-contradictory. It is
simply not what 400 × 400,000 resamples give, and only the replay can say so.

---

## Preserved science — unchanged, reconfirmed a fourth time

15,600 observations · 36 resolved / 3 unresolved · 26 eligible · **12/26, 7/26, 4/26** ·
all 36 original bootstrap intervals (Astra's independent replay, ≤ 5e-7) ·
ρ = −0.8329214038556598 descriptively · ~10.9 pp modelled transition width, scoped to this
version pair · k=20 `bv_n140` risk 3.741473676562272% · selection comparison 39 vs 13,
p = 0.455991 · 216/216 cross-machine gate counts · 858 anchored evidence files = 78
primary measurement arms + 780 fragments of the same observations.

---

## Open limitations — labelled, not closed

Carried forward from part 1: the seed law is described and not repaired; bootstrap
coverage is not established; the synthetic null is withdrawn and not replaced; the sweep
axis is disclosed and not renormalised; backend randomness was probed at 0/24 only; the
rustworkx build is an author assertion; byte-identical PDF reproduction is not promised.

Added by this round:

1. **Numeric-set equality is not semantic equivalence.** Stage 13 would not catch a
   substitution that reuses a value already present elsewhere in the document with
   identical spelling. A human reading of the built PDF is a release requirement.
2. **The offline anchor cannot authenticate itself.** Distributing the evidence together
   with its own transcript gives agreement, not identity. Only the v2 objects, or an
   externally published hash of the transcript, close that.
3. **Stage 9 needs `git archive HEAD`.** The 13-stage workflow is not archive-only
   runnable, and mutation fixtures therefore test the committed tree, not the working
   tree.
4. **Mutation U needs pandoc and Chromium.** Where they are absent it is named as
   skipped, and the coverage claim excludes it.
5. **Thirteen stages are not thirteen independent replications.** Several share a raw
   loader, a selection list and classification constants, so one defect can travel through
   more than one of them. Their individual scopes are stated in `verify.py`'s header.
6. **A verifier only tests the attacks someone thought of.** Four rounds have now each
   ended with a green verifier that a hostile auditor then broke. This ledger records what
   has been tried, not that nothing remains.

---
---

# Part 3 — the differential audit of Part 2's repairs

Audit: `audits/2026-09-14-astra-differential/` (`REVIEW.md`, SHA-256
`218f0adecf7d7202…`), against `3643bbcdb30c595c4a6caf0e8b41f179a3c15cdb`.

**Verdict as delivered: four CLOSED, six PARTIAL, one new defect. CORE SURVIVES MAJOR
CORRECTIONS.** No raw measurement changed. No reported scientific number changed.

Part 2 reported ten findings closed. Four were. The claim that all ten were is the thing
this part exists to correct, and the reason is worth stating plainly: **the repairs were
tested against fixtures written after reading the findings, not against the reproducers
Astra actually ran.** Two of those paraphrases passed where the originals did not.

---

## The two that Part 2 got wrong

| | what Astra ran | Part 2 | now |
|---|---|---|---|
| **V4-03** | `The primary risk interval excludes zero in only 7 / 26 eligible circuits.`, inserted after `## Abstract` | stages 12 **and** 13 returned 0 | mutation **W**, plus the positional fix below |
| **V4-07** | a layer printing its expected rejection diagnostic, then raising `RuntimeError` | classified **REJECTED**, declared reason present | terminal-verdict contract; classified **ERROR** |

**V4-03's cause was a one-line bug of mine.** The prose scan skipped any fraction whose
TEXT matched the canonical table's cells — `m.group(0) in tbl_span`, a substring test.
The canonical table legitimately contains `7 / 26`, so that string was skipped *wherever
in the document it appeared*, including the abstract. Part 2's fixture used the
word-number form ("Seven of 26"), which does not occur in the table, so it was caught and
the numeral form was not. Identity of a text occurrence is its **position**:
`parse_tables` now returns each table's character range and only the canonical table's own
range is excluded.

**V4-07's cause was the same mistake one level down.** Round one replaced "any nonzero
exit" with "nonzero exit and a `✗` in the output". Both read evidence *about* an outcome,
scraped after the fact, instead of the outcome itself — and neither can tell a layer that
finished and rejected from one that rejected and then fell over. A layer that fell over
did not finish, so it cannot vouch for anything.

---

## Findings

| ID | Prior | Defect remaining | Correction | New test | Status |
|---|---|---|---|---|---|
| **V4-01** | PARTIAL | a blank required cell CRASHED with `TypeError`; an extra unlabelled CSV cell passed the whole schema | Required vs `OPTIONAL` fields declared — only the four risk figures may be blank, and only on an `UNRESOLVED` circuit; a blank elsewhere is rejected by name. Row WIDTH is checked: `DictReader` files a surplus cell under the `None` key where no field-by-field check looks, and a short row leaves a `MISSING` sentinel; both are rejected. Column **order** is now part of the contract, not just the set | mutations **Y**, **Z**; 9 pytest cases | **CLOSED** |
| **V4-02** | CLOSED | — | — | — | **CLOSED** |
| **V4-03** | PARTIAL | the original numeral-form false abstract still passed; tags longer than 400 chars escaped the domain check | Canonical-table exclusion is **positional**, not textual. `TAG` bound removed (`[^<>]*`), and `UNTERMINATED` now anchors on `<|\Z` rather than `\Z` alone — writing the test revealed that an unterminated tag mid-document escaped entirely when another `<` preceded the next `>` | mutations **W**, **X**; 6 pytest cases | **CLOSED** |
| **V4-04** | PARTIAL | README "seed variance rather than version drift" and the old `−10.5% to +100.0%` range; LIVE rows for the 8 SDK gyms, the old range, and the categorical 11.5–14.0 pp window | README: inference narrowed to "consistent with", support corrected to **−17.68% to +109.17%**, and the gym row corrected to **2 of 8 inspected** (Qiskit passes no seed, BQSKit passes `seed=0`, the other six are **not assessed**) — "0 of 8" asserted something about all eight. LIVE rows relabelled CORRECTED/NARROWED. Inline SUPERSEDED markers added at the two historical sections a reader could still land on: §48's misquoted `knn_341` row and §49/§50's 40-hour figure | — | **CLOSED** |
| **V4-05** | PARTIAL | "every published figure" survived at PAPER.md:68; "before the primary data exists" at :678; `prereg_analysis.py`'s header still inferred that chronology ruled out tuning; `paper_check.py` still said "every quantitative claim" | All four corrected. The analysis header now states that commit order establishes **commit chronology and nothing more**, and that blindness is an attributed author process statement. `paper_check.py`'s header states its actual scope — 50 enumerated claims — and that **presence is not placement** | 1 pytest case | **CLOSED** |
| **V4-06** | CLOSED | — | — | — | **CLOSED** |
| **V4-07** | PARTIAL | expected diagnostic **then** crash still classified REJECTED | `validation_result.py`: every layer ends at `accept()` or `reject()`, which print a terminal `##QVALIDATION-RESULT##` line as the last thing before exit. A verdict is read only if that line is the final non-empty line of **stdout** and **stderr** carries no traceback — the two streams are kept separate so an ordinary warning cannot read as a crash. Each mutation declares an **invariant** (structural, emitted only by a completed routine) *and* a message fragment (which defect under it) | 5 pytest cases, one a real subprocess doing exactly what Astra did | **CLOSED** |
| **V4-08** | CLOSED | — | — | — | **CLOSED** |
| **V4-09** | PARTIAL | the code header disclosed the guard; PAPER.md still gave the entirely-above/below rule unqualified | §3.3 now states the rule **with** ε = 10⁻⁹, the reason (`110/100 − 1` is `0.10000000000000009`), the cost (an endpoint strictly outside but within 10⁻⁹ is `UNRESOLVED`), and the margin (2.3 × 10⁻³, 2.3 million ×). The exact integer comparison for the *k*-run decision event is stated as separate and untouched | 1 pytest case asserting the disclosure sits with the rule | **CLOSED** |
| **V4-10** | CLOSED | — | — | — | **CLOSED** |
| **NEW-BUILD-01** | — | a locked destination let Chromium fail while `build_paper.sh` exited 0 and printed "built", leaving the previous PDF in place for every downstream stage to validate | `publish/finalize_pdf.py`. The build goes to a unique temporary path; the fresh file is inspected (`%PDF-` magic, `%%EOF` trailer, size floor, page count); it is moved onto the destination; the destination is **re-read** and must now be that file. A locked destination fails nonzero with an explanation, leaves the old PDF intact and the fresh one on disk for retry. Success means an artifact exists, not that a command returned | 3 pytest cases, one taking a real Windows exclusive handle | **CLOSED** |

**11 of 11 accepted. None rejected.** Two were re-derived rather than taken on the
auditor's word: the 8-gym scope (the manuscript's own §6 says source inspection covers
**two** of eight), and the unterminated-tag hole, which the regression test for V4-03
exposed and which Astra had not reported.

---

## Resource failures are not validation outcomes

Astra's pristine runs died at **99.98% commit charge** (115,302,940,672 of
115,322,265,600 bytes), and one stage exit includes reviewer intervention to clear
stalled `git archive` children. Two of this repository's own runs died the same way while
`q5_fuzz.py --f1` held 4.25 GB.

None of those are counted as verifier results, here or in the review. A `MemoryError` is
an **ERROR** under the contract added for V4-07 — neither a pass nor a detection — and
the mutation test reported it as exactly that: *"control: a pristine snapshot did not pass
derived (ERROR)"*. Before the certifying run, host memory was measured and recorded rather
than assumed.

---

## The verifier, in layers — after the differential

Unchanged in structure. What changed is how an outcome is **read**:

| | before | now |
|---|---|---|
| a layer passed | exit code 0 | terminal `PASSED` verdict **and** exit 0 |
| a layer rejected | nonzero exit containing `✗` | terminal `REJECTED <invariant>` verdict, no traceback on stderr, **and** nonzero exit |
| a layer crashed | indistinguishable from rejecting | **ERROR**, and never counted as either |

**22 mutations**, each REJECTED by the layer that must catch it, under its declared
invariant, for its declared reason. New in this round: **W**, **X**, **Y**, **Z**.

---

## Preserved science — unchanged, reconfirmed

15,600 observations · 36 resolved / 3 unresolved · 26 eligible · **12/26, 7/26, 4/26** ·
all 36 original bootstrap intervals · ρ = −0.8329214038556598 descriptively · ~10.9 pp
transition width, scoped to this version pair · k=20 `bv_n140` risk 3.741473676562272% ·
216/216 cross-machine gate counts · 858 anchored evidence files = 78 arms + 780 fragments.
Both revisions carry the identical `results/raw/prereg` tree object
`3114a270ccd78b0daaa2a1bc451dd15155d55c13`.

---

## Open limitations — labelled, not closed

Everything carried forward from Parts 1 and 2, plus:

1. **A paraphrased reproducer is not a reproducer.** Two repairs passed fixtures written
   from the findings while the auditor's own cases still failed. Every case Astra ran is
   now a standing fixture in its original form, and a test asserts they are all present.
2. **Numeric-set equality is still not semantic equivalence**, and a human reading of the
   built PDF remains a release requirement.
3. **The offline anchor still cannot authenticate itself.**
4. **Stage 9 still needs `git archive HEAD`**, so mutation fixtures test the committed
   tree, not the working tree.
5. **Mutation U still needs pandoc and Chromium**, and is named as skipped where absent.
6. **Historical sections of `RESEARCH_LANDSCAPE.md` are marked, not rewritten.** Two
   inline SUPERSEDED markers were added where a reader could land on a corrected number;
   the 231 KB record has not been swept sentence by sentence.
7. **A verifier only tests the attacks someone thought of.** Four audits have each ended
   with a green verifier that a hostile auditor then broke, and this one broke the
   repairs rather than the science. That is a narrowing, not a finish.

---
---

# Part 4 — the independent adversarial audit of the claim scan

Audit: an independent adversarial review against
`2842dc37ae9d925f5154ec8b4b678dc04c94fe2e` — itself the repair of two release blockers
raised against `4d50a2bd8a27213d27dd39e98401dafc5f014403`.

**Verdict as delivered: one RELEASE BLOCKER, two MAJOR assurance defects, three MINOR.**
No raw measurement changed. No reported scientific number changed. The endpoint is still
`12/26, 7/26, 4/26` and the pre-registered raw tree is still
`3114a270ccd78b0daaa2a1bc451dd15155d55c13`.

**The manuscript was scientifically correct throughout. Every finding in this part is
about the apparatus that is supposed to protect it.** The blocker was reproduced
end-to-end: a false sentence inserted after `## Abstract`, the PDF rebuilt, all thirteen
stages PASS, exit 0, and the falsehood printed on page 1 of the artifact a reviewer opens.

---

## One cause, five costumes

Three consecutive repairs of the prose scan asked the same question first: **does this
sentence look like a claim worth checking?** Each answered it from something the author of
the sentence controls, and each SKIPPED IN SILENCE what it did not recognise:

| the repair asked | so it was defeated by |
|---|---|
| does the sentence contain a counterfactual keyword? | writing `The audit finds that` in front of it |
| does `n / 26` or `n of 26` appear? | writing `7 out of 26`, `7 in 26`, `7 ⁄ 26` (U+2044), `7 ∕ 26` (U+2215) |
| is a known claim phrase within 160 characters? | saying `bounded away from zero`, or putting the phrase 200 characters away |
| which claim phrase is NEAREST? | naming two endpoints so that the true one is nearer |
| is the number inside the canonical table's character range? | appending a row, which makes the range longer |

Five spellings of one defect: **the decision to check was taken from incidental evidence
rather than from the thing itself.** It is the pattern this project has now been bitten by
in five different places (`METHODOLOGY.md` R19), and the repair is the same one every
time — declare the domain and refuse what falls outside it, instead of enumerating what
to catch.

The measurement the auditor made is the part worth keeping. Of fifteen quantities over the
eligible denominator in the frozen manuscript: **2 bound, 9 explicitly exempt, 4 SILENTLY
UNCHECKED.** One of the four was `13 of 26 eligible circuits have no spread at all`, which
could be set to any number with stages 6, 7 and 12 all green.

---

## Findings

| ID | Severity | Defect | Correction | New fixtures | Status |
|---|---|---|---|---|---|
| **F-01** | BLOCKING | endpoint claims evade binding through separator, vocabulary, distance and rebinding variants | inclusion inverted: a quantity is located by pairing an independently found numerator with the denominator, and **every** one must resolve to a declared claim identity or be REFUSED | mutations **AE**, **AF**; nine parametrised attacks including both Unicode slashes, the >160-character distance and the two-endpoint rebinding | **CLOSED** |
| **F-02** | MAJOR | the table exemption was the table's character range, which grows with attacker content | only rows `canonical_key` can NAME are exempt, by their own row spans; an unrecognised row is prose between pipes | mutations **AC** (the injected row verbatim), **AD** (a differently worded row) | **CLOSED** |
| **F-03** | MAJOR | four current `n/26` quantities silently unchecked | two new identities reconstructed from raw (`no_spread`, `side_stable`), and the endpoint enumeration checked as one ordered claim; unclassified is a rejection | mutations **AG**, **AH**; a disposition test that prints every quantity and requires `unclassified = 0` | **CLOSED** |
| **F-04** | MINOR | the docstring claimed it bound *every* prose quantity while four went unchecked | the claim is now true, and is *proved* by the disposition test rather than asserted | `test_the_self_description_promises_what_the_disposition_test_proves` | **CLOSED** |
| **F-05** | MINOR | `verify.py` said 22 corruptions, `README.md` said eighteen, the suite held 24 | the count is read from `len(MUTATIONS)` and printed at run time; neither file states one | — | **CLOSED** |
| **F-06** | MINOR | the guard looped over sets that did not contain AA or AB, so deleting both left the tests green | the guard RUNS each preserved fixture and compares the hostile text it produces against `ASTRA_FIXTURES` | `test_removing_a_preserved_fixture_makes_the_guard_fail`, parametrised over all eight | **CLOSED** |

---

## What replaced lexical proximity

    A QUANTITY OVER THE ELIGIBLE POPULATION is a reader-visible number standing as
    numerator to the eligible-set denominator — either immediately before it across any
    separator, or immediately after an explicit reference to the population.

    EVERY such quantity gets exactly one disposition: bound to a declared CLAIM IDENTITY
    and compared against that identity's value reconstructed from raw, or covered by a
    pinned exemption passage quoted in full.

    A quantity with neither is REFUSED — by name, with its surrounding text.

Two consequences are worth stating, because they are what makes this different from the
three repairs before it:

1. **The predicate vocabulary carries no security weight.** An unrecognised predicate
   fails closed, so enlarging a vocabulary list can only turn a refusal into a
   comparison, never a comparison into a pass. The lists exist so the manuscript's own
   prose can resolve, not to catch attacks.
2. **Ambiguity is refused, not resolved.** A sentence naming two endpoints over one
   number is rejected rather than bound to the nearer one. Nearest-marker arithmetic is
   what let `excludes zero — that is, a decision risk ≥ 5% — in only 7 / 26` rebind
   itself to the endpoint that made it true.

Source and PDF run the same function over the same folded text, so a claim cannot be true
in one rendering and unexamined in the other. Folding is also what erases the two Unicode
slashes before anything looks at them.

---

## Two numbers the manuscript stated and nothing reconstructed

Both are now produced by the same pass over raw that produces the endpoint, at no extra
cost, and both agree with what §3 and §4.1 already said:

| claim | reconstructed | manuscript |
|---|---|---|
| eligible circuits with both arms constant across every seed | 13 | `13 of 26 … have no spread at all` |
| eligible circuits whose θ changes side of the threshold across 4,000 resamples | 0 | `none of the 26 … changed θ's side` |

Nothing in the manuscript was edited to make these pass. Had either disagreed, the
contradiction would have been reported instead of repaired.

---

## Preserved science — unchanged, reconfirmed a fifth time

36 resolved / 3 unresolved / 26 eligible; **12/26, 7/26, 4/26**; ρ = −0.8329214038556598;
ambiguity band ≈ 10.9 pp; k=20 risk 3.741473676562272%; 216/216 cross-machine.
`results/raw/prereg` remains `3114a270ccd78b0daaa2a1bc451dd15155d55c13`.

---

## Open limitations — labelled, not closed

Everything carried forward from Parts 1–3, plus:

1. **The disposition inventory is complete for the scanner's definition of a quantity,
   and that definition is a choice.** A number related to the eligible set by prose this
   scanner does not read as a numerator–denominator pair is outside the domain, not
   inside it and passing. The definition is stated in `manuscript_binding`'s docstring
   and printed by the disposition test, so it can be argued with rather than assumed.
2. **The PDF's exemptions are located by text, not by position**, because extracted text
   has no table to parse. Each exempt passage is a COMPLETE canonical row, so a duplicate
   asserts exactly what the original asserts — but this is weaker than the source-side
   rule, and it is stated rather than hidden.
3. **A verifier only tests the attacks someone thought of.** Five audits have now ended
   with a green verifier that an adversarial reader then broke. Four of the five broke
   the apparatus rather than the science. That is a narrowing, not a finish, and this
   file is the record of what has been tried — never a certificate.

---
---

# Part 5 — the independent adversarial audit of the claim scan's RECALL

Audit: an independent adversarial review against
`f125dfac8ca1c0dacab663fe30999fa4c1ee7d3f`, returning **INDEPENDENT ADVERSARIAL AUDIT:
RELEASE BLOCKED** — three blockers, B1, B2 and B3.

No raw measurement changed. No reported scientific number changed. The endpoint is still
`12/26, 7/26, 4/26`; the pre-registered raw tree is still
`3114a270ccd78b0daaa2a1bc451dd15155d55c13`. **The manuscript was scientifically correct
throughout, and remains byte-identical.** Everything in this part is about the apparatus.

---

## The finding under the finding

Part 4 replaced a keyword blacklist with a declared claim domain, and the domain FAILS
CLOSED: an endpoint quantity it cannot classify is refused, not skipped. That is true and
it was not enough, because it only holds *once a quantity exists*. The auditor wrote nine
reader-visible falsehoods for which one never did:

| the sentence | why no quantity was instantiated |
|---|---|
| `Seven of the twenty-six eligible circuits have an interval that excludes zero.` | `twenty-six` is not in the number-word list, so there was no denominator token |
| `Of the 26 eligible circuits in the pre-registered set, only seven have …` | seven words between denominator and numerator; the link window is three |
| `The study resolves 26 eligible circuits, of which only seven have …` | same, across a relative clause |
| `… excludes zero in just 27% of eligible circuits.` | a proportion has no denominator at all |
| `… in only ７ / ２６ eligible circuits.` | full-width digits fold to spaces before anything counts |
| `… in only seven (see §4.1) of the 26 eligible circuits.` | a digit inside the gap breaks the link |
| `… in only __7__ / 26 eligible circuits.` | `_` is a word character, so the boundary guard rejected the numeral |
| `Barely a quarter of the 26 eligible circuits …` | no numerator in any notation |
| `\| Summary \| seven of the twenty-six eligible circuits exclude zero \| \| \|` | the same, inside the canonical table |

Every one returned **13/13 PASS, exit 0**, with the false statement on page 1 of the
built PDF and the canonical table still reading `12 / 26`. All nine reproduce against
`f125dfa`; they were confirmed before anything was repaired.

**These are recall failures, not classification failures.** The classifier was never
asked. And the fix for a recall failure cannot be a better recogniser: four rounds have
now widened one, and each widening was defeated by the next spelling. "Recognise every
English sentence that could express seven of twenty-six" is not a question a regular
expression answers, and the tenth spelling exists whether or not anyone here has thought
of it.

**B2 is why nobody noticed.** Part 4's coverage test started from `quantities()` and
proved that everything it returned had been classified — which is also true of an empty
set. Inserting the hostile sentence left stage 12 printing the identical line,
`17 quantit(ies) … 0 ambiguous, 0 unclassified`, because the assertion was never in the
measured universe. A recogniser cannot be used to measure its own recall.

---

## The architectural change: a closed-world registered surface

The security question is no longer

> can we recognise every possible English quantitative sentence?

but

> is every reader-visible unit of this frozen page explicitly accounted for?

`visible_surface.py` parses `PAPER.md` into reader-visible structural units — a maximal
run of consecutive non-blank lines, with headings, table rows and fenced blocks as units
of their own. **It knows nothing about numbers, claims or vocabulary**, and a test asserts
that as a structural fact about the file: the strings `quantities(`, `CLAIM_IDENTITIES`,
`WORD_NUM`, `NUM_TOKEN`, `claim_inventory` and `DISTRIBUTION_STATS` do not appear in it.

Each unit's identity is the SHA-256 of its normalised text — whitespace collapsed and
**nothing else touched**, so `７` is not `7` and `≥` is not a space. `manuscript_surface.json`
is the committed, ordered registry of those identities, each carrying exactly one
disposition:

| | |
|---|---|
| `BOUND` | carries release-critical identities reconstructed from raw on every run |
| `CANONICAL` | the generated endpoint table, validated structurally against raw |
| `PINNED_EXEMPTION` | historical or counterfactual text, exempted by exact passage identity |
| `NON_CLAIM` | carries no identity in the release-critical registry |

There is no fifth state, and a unit with no entry is `UNKNOWN`, which is a rejection. The
registry is written only by `python visible_surface.py --write`, from a module that the
verification path does not import — a test asserts that too. Changing `12 / 26` to
`Seven of the twenty-six` does not remove the sentence from the universe; it changes that
unit's hash, which is the same rejection by a different road.

**The PDF gets the same treatment, one layer further back.** Binding the artifact to the
manuscript it was built from proves only that the build works — an attacker who edits
`PAPER.md` gets a faithful rendering of the edit. So stage 13 binds the PDF to the
REGISTRY: every word of the extracted text must be a word the registered page carries, in
the same multiplicity, and every registered word must reach a page. Measured on this
build: **7,723 word tokens on each side, the two multisets equal, zero residue.** The
rendering normalisation is declared (`<sub>` renders as its contents, fences and their
info strings render as nothing, emphasis and escapes are markers) — it is not a tolerance,
and there is no residue budget.

---

## Findings

| ID | Severity | Defect | Structural repair | Preserved reproducers | Status |
|---|---|---|---|---|---|
| **B1** | BLOCKING | claim-domain detection fails open: arbitrary readable English never reaches `quantities()` | recall removed from the security boundary — a closed-world registered reader-visible surface, refused by hash, plus the same closed world over the PDF's words | mutations **AJ**–**AT** (nine auditor sentences + the injected row), **AK** through the real pandoc + Chromium path | **CLOSED** |
| **B2** | BLOCKING | `silently unchecked = 0` measured the recogniser with the recogniser | coverage computed from the Markdown block structure, which cannot call the claim scan; the `len(found) >= 15` completeness claim deleted | three negative controls with no digits / no slash / no known vocabulary, and the headline sentence proved to move the inventory *and* to remain invisible to the recogniser | **CLOSED** |
| **B3** | BLOCKING | §4.2's four distribution statistics had no disposition; `paper_check` matched `6.9` inside `26.9` | four new identities reconstructed from raw, read inside the one unit that states them; `paper_check` now matches complete number tokens | mutations **AU** (A8 verbatim), **AV** (same, through the PDF path), **AW**, **AX**, and five parametrised statistic attacks | **CLOSED** |
| — | contract | a fixture that could not be built printed `NOT EXERCISED` and exited 0 | a skipped required mutation is an execution failure and fails the suite; it is never scored as a detection | a test that runs the real suite with pandoc and Chromium hidden and requires a nonzero exit | **CLOSED** |

---

## The four statistics, reconstructed

Percentiles of the eligible circuits' decision risks, numpy's default linear
interpolation — the convention is declared, because a percentile without one is not a
number.

| statistic | reconstructed | manuscript | bound by |
|---|---|---|---|
| median | 0.0000% | **median 0** | §4.2's own reader-visible unit |
| p75 | 6.9053% | p75 = 6.9% | same unit, label-anchored |
| p90 | 14.1700% | p90 = 14.2% | same unit, label-anchored |
| max | 17.3147% | max = 17.3% | same unit, label-anchored |

All four agree at the precision printed. Nothing in the manuscript was edited; had one
disagreed, the contradiction would have been reported instead of repaired.

**A live defect fell out of the `paper_check` repair.** With substring matching replaced
by complete-number-token matching, `cc_n32 risk pct = 0.37` failed — because the
manuscript never writes `0.37`. It writes `0.374089`, twice, and the old check passed on
a prefix of it. The redundant two-decimal check is deleted, not repaired: the line beside
it already binds the same computed value to the number the paper actually prints, at full
precision. The manuscript was right; the checker was not.

---

## Attacking the repaired architecture

Seven formulations invented after the repair, none of them in the audit report, none
added to any vocabulary first:

| | attack | caught by |
|---|---|---|
| S1 | `A minority of the eligible circuits carry a risk interval that is distinguishable from nothing at all.` — no digits at all | surface alone |
| S2 | `… excludes zero in only ⅶ of the ⅹⅹⅵ eligible circuits.` — Unicode Roman numerals | surface alone |
| S3 | `The pre-registered endpoint is met by 26.9% of eligible circuits.` — a percentage lifted from the canonical table | surface alone |
| S4 | a nested blockquote inserted inside an existing quote block | surface alone |
| S5 | §4.2's statistics restated qualitatively, with no false digits | surface, and the statistic binding |
| S6 | an insertion INSIDE an existing sentence rather than as a new block | surface alone |
| S7 | seven words added to a `### 4.2 Magnitude` heading | surface alone |

Six of the seven are invisible to every claim recogniser in the repository, which is the
result that matters: the registry is doing the work, not a phrase list.

---

## Preserved science — unchanged, reconfirmed a sixth time

36 resolved / 3 unresolved / 26 eligible; **12/26, 7/26, 4/26**; ρ = −0.8329214038556598;
ambiguity band ≈ 10.9 pp; k=20 risk 3.741473676562272%; 216/216 cross-machine; 13 with no
seed-to-seed spread; 0 changing θ's side under 4,000 resamples.
`results/raw/prereg` remains `3114a270ccd78b0daaa2a1bc451dd15155d55c13`.

---

## Open limitations — labelled, not closed

Everything carried forward from Parts 1–4, plus:

1. **The registry does not defend against someone who edits the manuscript and the
   registry in one commit.** That is the trust boundary `raw_integrity.py`'s manifest
   already has, and hashing does not close it. What the registry buys is that insertion
   and alteration stop being SILENT: recall no longer depends on parsing English, and
   every change to the page is a diff line carrying the text that changed.
2. **`NON_CLAIM` is a declaration, not a measurement.** It says no identity in
   `RELEASE_IDENTITIES` is asserted in that unit — not that the unit contains no numbers.
   136 units are `NON_CLAIM` and **107 of them carry digits**; §4.3's ambiguity-band
   quartiles are the clearest case, quantitative and registered and not independently
   reconstructed. Stage 12 prints that count on every run so the size of the human
   judgement made at freeze time is a number rather than a promise.
3. **The PDF is bound by word multiset, not word ORDER.** A rearrangement of the same
   words into a different claim would pass stage 13, and is caught only by stage 12 on the
   source. Equality of multisets is a strong statement about content and a weak one about
   syntax.
4. **The unit is a block, not a sentence.** An edit inside a paragraph changes that
   paragraph's hash and is refused, so this costs nothing in coverage — but the diff a
   reviewer reads is a whole block, and a one-word change inside a long block is a
   one-block diff.
5. **A verifier only tests the attacks someone thought of.** Six audits have now ended
   with a green verifier that an adversarial reader then broke. Five of the six broke the
   apparatus rather than the science. This round moved a whole class of attack off the
   boundary rather than patching instances of it, which is a better kind of narrowing —
   and it is still a narrowing. This file is the record of what has been tried, never a
   certificate.

---
---

# Part 6 — audit closure, and what the apparatus does not establish

Frozen candidate audited: `b5ba725e5ddbc9ad97ab07e93e71a150e7e37cfa`.

Independent hostile verdict, delivered in full:

> `INDEPENDENT ADVERSARIAL AUDIT: NO RELEASE-BLOCKING DEFECT FOUND`

The auditor re-ran and independently confirmed, rather than accepting the reported
numbers: 13/13 verifier stages PASS; 44/44 mutation fixtures REJECTED with 0 NOT
EXERCISED and 0 ERROR and all 51 declared reasons observed; the raw pre-registered tree
`3114a270ccd78b0daaa2a1bc451dd15155d55c13`; the endpoint 12/26, 7/26, 4/26 reconstructed
from raw; the four §4.2 statistics at 0.0000 / 6.9053 / 14.1700 / 17.3147; nine of nine
release identities bound; the registry writer isolated from the verification path by an
AST walk; and that denying the host pandoc turns a required PDF fixture into a visible
NOT EXERCISED with exit 1 rather than a pass.

It also attacked the registry directly — reordering, deletion, duplication, stale
entries, hash alteration, text alteration, cross-mapping one unit to another's hash, and
content edits inside `NON_CLAIM` units — and found all of them rejected.

**This part is not a certificate.** The apparatus is not complete, not exhaustive and not
perfect, and the three findings below are the reasons stated in the auditor's own terms.

---

## Three documented residual limitations — assurance, not science

None of these makes a reported number wrong. Every attack that put false science on the
*page* was rejected by some layer; the raw evidence, the endpoint and the manuscript's
scientific prose are untouched by this round.

**F1 — a literal `<!-- -->` inside a fenced code block is not a unit of the model.**
`visible_surface.units()` runs `COMMENT.sub("", raw)` over the whole document before
structure is parsed, so a comment typed inside a fence is stripped here while pandoc
renders it as visible text in a `<pre>`. Stage 12 therefore returns 0 UNKNOWN on a
document that has gained a reader-visible line. **Stage 13 rejects it** — twice, on the
claim recogniser and on twelve word tokens the registry does not carry — so the pipeline
holds and the artifact gate does not pass it. What was wrong was the *wording*: stage 12's
success line and `README.md` said "every reader-visible unit", and the implementation
establishes "every unit of the declared Markdown surface model". Both are narrowed in the
release-preparation commit. The implementation was deliberately **not** expanded to
preserve the stronger sentence.

**F2 — whitespace transformations preserve unit identity while changing rendering.**
`normalise` is `" ".join(text.split())` and `units` decides "table row" from
`line.strip().startswith("|")`, so a unit's hash cannot distinguish a table from the same
text indented into a code block. Indenting the canonical table's five lines by four
spaces leaves the registry byte-identical, stages 12 and 13 both PASS, and the results
table is destroyed on the page. The same blindness was confirmed for hard line breaks,
list merge/split, setext promotion and demotion, NBSP, U+2000, U+3000, U+0085, U+001C,
CRLF↔LF and tab↔space. Zero-width characters, combining marks and backslash hard breaks
DO change a unit's identity and are caught. Because whitespace cannot reorder words, this
family degrades presentation without falsifying a number — but "the table a reader sees"
is not what the model checks, and it is no longer described as though it were.

**F3 — the PDF word-multiset binding does not prove semantic word order.** Through the
tracked `publish/build_paper.sh` (pandoc 3.9.0.2 + headless Chromium), the auditor
produced a PDF stating `p75 = 25.2, max = 14.8` — a maximum smaller than its own 75th
percentile — together with a reversal of which residual model fits better and of the
direction of the additive-model shift, while `PAPER.md` and `manuscript_surface.json`
stayed byte-identical to the frozen SHA. **Stage 13 returned PASSED**: 275 = 275 numeric
tokens, 3/3 canonical rows intact, 7,723 = 7,723 words. Equality of multisets is a strong
statement about content and a weak one about order. This was already declared in three
places before the audit; the audit demonstrated it rather than discovering it.

**The compensating control is a human, and only a human.** A documented reading of the
built PDF against `PAPER.md` is a release requirement, it cannot be closed by any check in
this repository, and no automated result in this ledger should be read as closing it.

### Minor findings, recorded and not repaired in this commit

- **F4** — `compare()` tallies `e["disposition"]` with `dict.get` instead of testing it
  against the declared `DISPOSITIONS` set, so an out-of-domain label is counted rather
  than refused and the printed buckets need not sum to the parsed unit count. The field is
  read nowhere else (`registered_claims` reads `claims`), so this misreports the inventory
  rather than weakening a check, and deleting the key entirely *is* rejected. It is
  `METHODOLOGY.md` R19 in miniature — a declared domain that was never made a predicate —
  and it is recorded here rather than fixed, because this commit is restricted to wording
  and to this record.
- **F5** — a passing run prints no scope narrowing beside its PASS table. Fixed in this
  commit as part of item 1: the success line now states the scope instead of "the
  repository is intact".
- **F6** — `publish/paper.pdf` and `paper.html` are untracked, so the freeze pins the
  build inputs and not the artifact. The rationale is stated in `pdf_binding.py`: Chromium
  stamps a creation timestamp into every build, so byte-identical PDFs are not promised
  and pinning one would be a reproducibility claim that fails on first check.

---

## The standing distinction

| | |
|---|---|
| automated assurance | **passed** — 13/13 stages, 44/44 fixtures, 0 skipped, 0 ERROR, on `b5ba725` and re-confirmed on the release SHA |
| final human artifact reading | **still required**, and not performed at the time of writing |

The science is unchanged and was never in question in this round: raw tree
`3114a270ccd78b0daaa2a1bc451dd15155d55c13`, endpoint **12/26, 7/26, 4/26**.
