# qvalidation differential validation — 3643bbc

Target: `3643bbcdb30c595c4a6caf0e8b41f179a3c15cdb`. Previous review: `4531d97d754c9f116db567e1908cbb59d6016eb2`. Review date: 2026-09-13.

**Four findings CLOSED; six PARTIAL.** The original false-abstract reproducer still passes. The repaired checks materially improve validation, but the claim that all ten findings are closed is unsupported.

This was a differential review of the ten repairs, using detached disposable copies, exact code/prose differences, original reproducers and nearby variants. The author’s repository was not edited, and nothing was published, tagged or pushed. The previously established endpoint (36 resolved / 3 unresolved; 26 eligible; 12/26, 7/26, 4/26) was not independently reconstructed again. No numerical discrepancy requiring that reconstruction emerged.

The author’s HEAD was the target and `git status --porcelain` was empty. Both revisions have the identical `results/raw/prereg` tree object: `3114a270ccd78b0daaa2a1bc451dd15155d55c13`.

**Full-suite certification was not obtained.** The first pristine run ended with 10 PASS and 3 FAIL (stages 9–11), during host memory commit exhaustion. Windows counters showed 115,302,940,672 committed bytes against a 115,322,265,600-byte limit (99.98%). Stage 9's subprocess reader raised MemoryError and left git archive stalled; the reviewer stopped those stalled archive children. Stage 10 then raised TypeError while hashing unavailable Git output, and stage 11 could not allocate a 9.16 MiB NumPy array. The stage-9 exit therefore includes reviewer intervention and is not an unassisted validation result. Its full console transcript is `evidence/pristine.log`.

A separate direct mutation run naturally failed: its derived control was ERROR and fixture A's raw input was missing. Independent snapshot probes subsequently succeeded. A diagnostic full rerun preserving original subprocess arguments/results was stopped after memory exhaustion was established; it is not counted as a completed run. The host resource condition prevents interpreting these events as confirmed repair regressions, and **neither 13/13 nor 18/18 is independently certified here**. The code's declared-reason predicates were inspected, focused negative cases were exercised, and built-in U was separately exercised successfully. The remaining infrastructure and prose findings independently preclude release readiness. No further scientific reconstruction was undertaken.

| Finding | CLOSED/PARTIAL/OPEN | Evidence | New issue? |
|---|---|---|---|
| V4-01 | PARTIAL | Original all-NaN intervals rejected as non-finite. Inf, fractional integers, invalid bool, duplicate IDs, reversed intervals, points outside intervals and inconsistent derived flags also rejected. | Required blank numeric cell crashes; an extra unlabelled CSV cell passes `--schema`. Newly observed schema gaps; no claim that the extra cell passes full replay. |
| V4-02 | CLOSED | Original 10.9→99.9 PDF rejected. Dropping 0.2462 rejected; swapping the 7/26 and 4/26 row fractions rejected despite unchanged numeric-token sets. Bidirectional token and intact canonical-row checks work. Explicit human review and limited scope replace full semantic-equivalence claims. | None within the narrowed PDF-content contract. |
| V4-03 | PARTIAL | Original CSS-hidden table and a raw `<section>` are rejected. The exact original false abstract with `7 / 26` still passes stage 12 and, when genuinely rebuilt, stage 13. “Seven of 26” is rejected. | Tags longer than the scanner’s 400-character bound escape its supported-domain check. Fresh PDF rendering of that hidden table is rejected by stage 13. |
| V4-04 | PARTIAL | 13 deterministic circuits, corrected issue differences, 13 stages, withdrawal of the version-pair-free claim and historical banners are repaired. Active README and LIVE research rows retain other previously identified claims. | No introduced regression established; incomplete prose cleanup. |
| V4-05 | PARTIAL | Seven target passages are narrowed. Nearby active “every published figure” and “before the primary data exists” assurances survive, as does the analysis-header claim that chronology rules out tuning. | No introduced regression established; contradictory assurances remain. |
| V4-06 | CLOSED | With actual v2 objects, changed evidence plus a regenerated manifest is rejected. Without history, both original and altered supplied transcripts explicitly say historical authenticity is not established. Anchor regeneration without history is refused. | None within the explicitly weaker offline contract. |
| V4-07 | PARTIAL | Plain runtime/import failures classify ERROR. PDF checks pass in PowerShell and Git Bash; controlled absence of all extractors produces ERROR. | Printing the expected rejection diagnostic and then raising RuntimeError still classifies REJECTED and satisfies the declared-reason substring check. |
| V4-08 | CLOSED | Stylesheet path resolves. Fresh PDF is styled A4, 14 pages, Georgia body text at 10.5 pt. Removing the stylesheet makes the build fail. | Separate build robustness gap: Chrome can fail to overwrite a locked PDF while the script exits 0 and prints “built”; observed during this review. Not established as introduced by the CSS repair. |
| V4-09 | PARTIAL | Analysis header now explicitly describes the 1e-9 guard. Exact tie and within-guard cases are UNRESOLVED; outside-guard case is REGRESSION. | PAPER.md still states unqualified entirely-above/below rules and omits the tolerance. No numerical regression found. |
| V4-10 | CLOSED | Complete stage 1 explicitly requires Git. Five-file LF and CRLF copies without history fail with the intended explanation; real checkout passes; an unborn Git repository with matching files fails. | None found. |

## Evidence for the remaining material issues

**V4-03 — false scientific attribution still accepted.** Insert directly after `## Abstract`:

> The primary risk interval excludes zero in only 7 / 26 eligible circuits.

The correct primary numerator is 12. Both `manuscript_binding.py` and `pdf_binding.py` returned 0 on this modified source and its fresh PDF. The incorrect sentence is visibly present in `evidence/abstract_original_render.png`. No claim is made that an altered full 13-stage run was performed. At `manuscript_binding.py:261,296`, `m.group(0) in tbl_span` compares matched text with table text instead of checking the occurrence’s position. The abstract’s fraction is therefore skipped because that same fraction occurs in the valid table. The repaired word-number fixture does not reproduce this original defect.

**V4-04 — active summaries still conflict.** README.md:41–43 continues to infer “seed variance rather than version drift” from the noisy/disagreement pattern; line 81 retains −10.5% to +100.0%. RESEARCH_LANDSCAPE.md’s explicitly LIVE front table retains the “any of its 8 SDK gyms” seed statement at line 27, the old range at line 44, and categorical inability to resolve changes within an 11.5–14.0 pp window at line 46. A historical banner on later material does not make those LIVE rows historical.

**V4-05 — scope and chronology remain overstated.** PAPER.md:68 still describes an inventory rechecking “every published figure”; line 678 says committing before primary data exists makes the freeze auditable. Those conflict with the repaired limitations elsewhere. The prereg_analysis.py opening still says “WRITTEN AND COMMITTED BEFORE THE DATA EXISTED” and infers that the analysis could not have been tuned. paper_check.py’s opening likewise retains an every-quantitative-claim description. The seven replacements are real but do not remove the underlying active assurances.

**V4-07 — error classification remains diagnostic-based.** A real failing subprocess printed `✗ is not finite` and then raised an unrelated RuntimeError. Production `mutation_test.classify` returned REJECTED, and the NaN fixture’s required phrase was present. This is a focused test of the actual classifier and reason predicate, not a claim that a modified full harness was run. The logic at mutation_test.py:118 accepts any nonzero exit containing `✗`, even if the process subsequently crashes. Plain crashes are now correctly handled, which is a substantial improvement.

**V4-09 — reader-facing tolerance omission.** PAPER.md:244–246 still gives the entirely-above/below rule without a guard. Analysis-header disclosure is accurate, but the manuscript has no `1e-9`/`TIE_EPS` qualification. Constant-arm tests at the threshold, within the guard and outside it confirm the distinction is executable behavior.

## Environment and interpretation limits

Python 3.10.10, NumPy 2.2.6, SciPy 1.15.3; pandoc 3.9.0.2 and Chrome 152.0.7977.83. The tracked build was used. A PATH-empty PDF check still finds an installed extractor by absolute candidate path, so it correctly passes; that is not evidence of missing-tool handling. A separate controlled injection removed both pdftotext discovery and the fitz fallback and produced the explicit prerequisite ERROR. The built-in U fixture was separately built successfully and rejected for its declared PDF reason.

The first long-HTML PDF attempt reused a stale file because the reviewer’s open PyMuPDF handle blocked overwrite. Its apparent stage-13 PASS is invalid evidence for that variant. The build log exposes this, and the fresh-output rerun rejects the missing canonical rows. Both logs are retained, with the correction explicit. This also reveals the build script’s failure to establish that an output was actually replaced. The false-abstract PDF was the first fresh build and is unaffected.

Scripts and focused logs are in `evidence/`. They use local paths recorded in the scripts and disposable snapshots; the source repository was not modified. Newly observed cases are not automatically labelled regressions introduced by the repairs. The remaining major issues concern validation coverage and active assurance wording; they do not overturn the independently established empirical endpoint.

**CORE SURVIVES MAJOR CORRECTIONS**

