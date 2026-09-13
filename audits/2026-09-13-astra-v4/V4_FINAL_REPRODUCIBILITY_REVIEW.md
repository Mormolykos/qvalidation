# qvalidation v4: reproducibility and release-assurance review

Target: `4531d97d754c9f116db567e1908cbb59d6016eb2`.

The empirical endpoint survives. Release preparation is blocked by materially overstated validation and publication claims. Two independently controlled states completed the **unmodified 13-stage verifier with exit 0**: all 36 saved risk intervals replaced by NaN bounds, and a PDF displaying 99.9 where the manuscript says 10.9. These are completed executions, not inferred outcomes of interrupted work.

The pristine snapshot also passed all 13 stages. Its independent numerical reconstruction remains 36 resolved / 3 unresolved, 13 boundary flags overall, 26 eligible, and endpoints 12/26, 7/26 and 4/26. The 13 overall boundary flags include the 3 unresolved circuits; they are not 13 additional exclusions from the 36 resolved circuits.

No v4 ZIP exists. This review assesses the frozen repository and PDFs built from it. It does not certify an unpublished archive. All experiments were performed in disposable copies. The author's repository was not edited, committed, tagged, pushed or published.

## A. Fresh claim ledger and disposition

The preserved initial ledger was created before opening the v4 correction ledger or SETTLED explanations. Earlier conversation contained v3 context, and a search returned an earlier review excerpt; neither was treated as an independent source of numerical truth. The following dispositions update that ledger, rather than silently replacing its untested hypotheses with conclusions.

| Initial claim / question | Authority actually used | Completed disposition |
|---|---|---|
| Thirteen stages certify an intact publication | Subprocess exit codes and shared inputs | Two full 13/13 false-publication states demonstrated: findings V4-01 and V4-02 |
| Every quantitative figure is recomputed | Finite inventory; selected numeric comparisons and text searches | Scope overstatement; stages 6, 12 and 13 are not comprehensive claim validators |
| Every saved primary field reproduces | Original `prereg_analysis.analyse` replay, 18 named fields | Ordinary changed bounds rejected; NaN accepted; V4-01 |
| Membership and row count are checked | Circuit-keyed dictionary | Missing identity checked; duplicate identities collapsed before counting |
| Scalar types are enforced | Permissive bool and `int(float(...))` conversion | Fractional integer metadata accepted by conversion; nonfinite float comparison invalid |
| The visible Markdown table is validated | Comment stripping and pipe-line parsing | Comments and duplicate tables rejected; CSS-hidden table accepted; V4-03 |
| Contradictory prose is detected | Fraction search with numerator and paragraph exemptions | Wrong abstract attribution of 7/26 accepted; V4-03 |
| PDF semantics agree with source | Presence of fractions, version token and six phrases | Visible 99.9 substitution accepted by all 13 stages; V4-02 |
| Historical v2 identity is independent of current metadata | Actual v2 objects if present | Current anchor matches all 858 actual v2 blobs; changed measurement rejected with history |
| Offline anchor is itself bound to v2 | Local JSON list plus commit-name string | Authenticity is external to this check; V4-06 |
| Historical byte identity is portable | LF-normalized current content versus Git blobs | Canonical-content identity, not arbitrary checkout-byte identity |
| 858 files mean 78 arms plus 780 fragments | Independent record multiset comparison and loader trace | Confirmed: both representations contain the same 15,600 observations |
| Benchpress pin works across line endings | Five canonical hashes, HEAD and tracked cleanliness | Clean LF and CRLF sparse checkouts both pass; no-history helper/stage distinction remains |
| Built-in tests establish the intended failure reason | Required-stage nonzero exit | All eleven fixtures reject correctly today; unrelated exits also satisfy acceptance logic |
| PDF text and layout reproduce through tracked build inputs | Pandoc and Windows Chrome | Build succeeds, but stylesheet link resolves to a missing nested path; V4-08 |
| Primary values and transition width reproduce independently | Review code with no project analysis imports | Preserved numerical core and all 36 original intervals confirmed |
| Historical issue protocol was reproduced | Local simulation plus external issue | Numeric comparison survives; “own protocol” wording contradicts stated limitations |
| Every measurement was reproduced; a fixed seed removes variance | Finite controls and separately random backend construction | Controls do not establish universal claims; V4-05 |
| Commit order establishes when data existed | Local Git chronology | Only tracked commit order is established; active stronger wording remains |
| All current release surfaces agree | Root manuscript, README, LIVE research table, historical copies, built PDFs | Historical banner is valid; root active surfaces still disagree; V4-04 |

## B. Authority and scope of all 13 stages

“Indirect” below means a result follows through another computation or trusted input. It does not mean independent replication. A common raw loader, selection list, classification tolerance or analysis implementation can transmit the same defect to several stages.

| Stage | Directly validates | Indirectly validates / authority | Does not validate | Description accurate? |
|---|---|---|---|---|
| 1 `pin_check.py` | External Benchpress HEAD, tracked cleanliness, five canonical module hashes | Git blobs and the saved canonical reference | Full package/environment identity; all dependency behavior; source-archive commit identity | Line-ending claim confirmed; documented no-history fallback is only implemented in helper, not accepted by stage |
| 2 pytest | Assertions exercised by the repository's regression/unit tests | Fixtures and imported implementation | Complete scientific artifact consistency, universal input coverage, independent numerical replication | Accurate as a test suite; not a certificate for untested artifacts |
| 3 inventory | 44 selected frozen values versus designated calculations | 32 classified raw-recomputed; 12 reread from derived k-sweep CSVs; shared functions | Every manuscript number, every interval, all prose, rendering, complete k-sweep regeneration | Current 44/32/12 console distinction is useful and accurate in scope; broader “every published figure” claims are not |
| 4 replication | 144 recorded values for 6 circuits × 12 seeds × 2 versions versus `expected.json`; associated controls/bands | Committed replication outputs and reference | Fresh transpilation in this verify invocation; primary 39-circuit 1.4.3→2.0.0 study; all 15,600 observations | Correct as artifact comparison; “reproduced from clean” requires a separate measurement run |
| 5 paired proof | Assertions demonstrating the withdrawn paired statistic's construction | Same paired implementation and demonstration arrays | Correctness of other estimators; meaningful independence of empirical effects | Narrow proof is useful; not validation of the publication generally |
| 6 paper claims | Selected numeric values and their source-text presence or nearby occurrence | Saved summary for primary figures; raw calculations for selected auxiliaries | All values from raw; semantic attribution; rendering; whole abstract; complete PDF | Header and `verify.py` “every quantitative claim” overstate implementation |
| 7 raw endpoint | Raw reconstruction of classifications, eligibility, risk and intervals; three manuscript fractions; optional point-estimator cross-check | Shared `load_seeded`, `BOUNDARY_PP`, `TIE_EPS`; separately implemented risk estimator | Saved original-MC interval equality; every source field; human-visible placement; bootstrap coverage calibration | Estimator independence is partial and properly distinct from stage 11; “manuscript numbers” must be limited to checked claims |
| 8 raw integrity | SHA-256 of 78 merged arms against current manifest; selected summary status/verdict/risk/theta checks | Current local manifest and stage-7 reconstruction | Historical authenticity if manifest changes too; all 18 fields; duplicate/missing-row enforcement; fragments in this stage | Self-consistency description largely correct; “summary reproducible” must not imply complete coverage by this stage alone |
| 9 negative fixtures | Pristine control and required-stage nonzero exits on eleven fixture changes | `git archive HEAD` snapshots; five validation layers | Intended error reason; current worktree negative fixtures; PDF validation; Git-history branch of anchor | Archives have no history, so its anchor fixtures exercise fallback; exit-only acceptance needs qualification |
| 10 v2 anchor | All 858 canonicalized file hashes versus v2 objects when available | Hardcoded v2 commit; otherwise local JSON transcript | Independent offline authenticity; measurement truth; provenance before commits; byte equality across LF/CRLF | Git branch works; unconditional historical-identity wording overstates fallback |
| 11 derived binding | 18 named fields against the original analysis replay, subject to conversions/tolerances | Same analysis code, bootstrap seeds and original MC budget | Independent implementation of every saved value; nonfinite rejection; strict integer/bool schema; duplicate identities; arbitrary added columns | “Every saved primary field” is false for tested malformed values; V4-01 |
| 12 rendered manuscript | One recognized pipe table, canonical label prefixes, numerator/denominator and a limited prose scan | Shared stage-7 reconstruction | Browser visibility, CSS, full GFM semantics, complete prose attribution, all table percentages/intervals | “What the reader sees” is false; V4-03 |
| 13 PDF | Expected fractions somewhere in extracted text, matching version string, six phrase checks | Source table parser; textual extraction; source-side withdrawal context | Full semantic equivalence, row placement, every value, abstract agreement, layout or arbitrary stale claims | “Same active claims” is false; full 13-stage counterexample V4-02 |

The stages provide useful overlapping checks, not thirteen independent scientific replications. In particular, stage 11 deliberately replays the producer, whereas this review's preserved reconstruction and bootstrap replay use separate code. Stage 7's independent risk estimator still shares raw loading and classification constants with the producer.

## D. Historical trust model and evidence-file accounting

Independent `git cat-file --batch` comparison confirms the current anchor's 858 hash/byte-count entries match the actual v2 objects at `17e08f3e92533ff8266b1b586e35f20da2923da8`. The anchor file's review-time SHA-256 is `cc31e9b2f43d9a4ca6332e0e300e7f0c391c59c17dfe32804269800446ab9827`. Recording that hash here is evidence from this review; the checker itself does not contain or authenticate such an external reference.

The available-history path compares current content to historical Git blobs, normalizing current CRLF to LF. Updating the current manifest does not change that historical authority. Authenticity ultimately relies on a trusted commit/repository identity and trustworthy Git object interpretation, not on the word “historical” in metadata.

Without v2 history, the checker loads `V2_EVIDENCE_ANCHOR.json` and checks its `v2_commit` string. It establishes agreement with that supplied transcript. A trusted copy of this pinned v4 tree can establish the transcript's identity externally; an unauthenticated archive carrying both data and its own transcript cannot do so internally. `--write-anchor` correctly refuses without history, but manually changed transcript contents are not thereby authenticated.

A pristine source archive passed stages 8 and 10. Its `--write-anchor` call refused as intended. Stage 9 failed because `git archive HEAD` could not run. Thus a source archive can perform data/manifest and transcript consistency checks; the complete 13-stage workflow is not archive-only runnable. There is no full-13-pass claim for the historyless experiment.

The independently verified file composition is:

| Quantity | Result |
|---|---:|
| Circuits | 39 |
| Version arms per circuit | 2 |
| Merged primary measurement-arm files | 78 |
| Fragments per merged arm | 10 |
| Fragment files | 780 |
| Run records in merged arms | 15,600 |
| Run records across fragments | The same 15,600 |
| Full record multisets, including metadata, matching | 78/78 arms |
| Files opened by traced `load_seeded` calls | Exactly 78 merged arms; no fragments |

There are not 171,600 or 31,200 independent measurements here. The fragments are another representation of the same runs. “858 anchored evidence files” is correct; “858 primary measurement arms” would be false. Current stage-10 console output correctly prints the 78+780 decomposition. Its anchor `_what` metadata still calls every entry a “primary raw file,” which is less precise than that console output. The major provenance issue is authenticity scope, not inflated numerical sample size in the actual loader.

The process count is **ten per circuit/version arm**, as `scatter.py:107–139` launches and merges the ten chunks for one arm. All 78 arms have ten distinct recorded PID numbers each. Across the study there are 359 distinct recorded PID numbers in the baseline version and 355 in the candidate version; PID reuse means those numbers are not a count of unique process lifetimes. Do not describe the entire study as ten total process executions. This clarification does not add observations or establish statistical independence between process fragments.

## E. Saved-field coverage

The saved CSV has 18 declared non-identity fields. The ordinary baseline stage-11 run reports 690 non-null comparisons; unresolved fields account for the difference from 39×18. This is a count of comparisons, not evidence that the comparison handles all input values correctly.

| Requested field | Stored / reconstructed representation | Coverage and limitation |
|---|---|---|
| Theta | `est_long_run_change_pct` | Stage 11 tolerance 5e-5 on saved rounded value; stage 8 looser 5e-4; NaN comparison defect applies |
| Theta interval | `change_ci_lo_pct`, `change_ci_hi_pct` | Original paired 4,000-resample replay, 5e-5; finite-value/schema checks absent |
| Reference classification | `verdict` | Exact string against producer; stage 7 independently recomputes with shared tolerance |
| Boundary | `boundary` | Compared after permissive bool conversion; unknown nonempty tokens become False |
| Eligibility | Derived from status, resolved verdict and boundary | No separate saved eligibility column; aggregate consistency through these components |
| Risk point | `error_rate`, also `p_call` | Original algorithm rounded comparison 5e-7; stage 8 risk 5e-6; independent review point values agree within saved rounding |
| Risk interval | `error_ci_lo`, `error_ci_hi` | Correct MC stream reproduced; ordinary changes rejected; NaN bounds accepted by all 13 stages |
| Zero exclusion | `error_excludes_zero` | Compared after permissive bool conversion; not recomputed from saved bounds, allowing NaN bounds alongside unchanged flag |
| Sample / seed count | `n_seeds` | Producer checks 200 paired distinct seeds on this data; CSV comparator uses `int(float(raw))`, not strict integer parsing |
| Threshold | `threshold` | Hardcoded replay parameter 0.10, comparison 1e-12; NaN defect applies |
| k | `k` | Hardcoded replay 3; fractional CSV values truncate before comparison |
| Version identifiers | `qiskit_baseline`, `qiskit_candidate` | Exact strings from producer's loaded environment records; no universal environment reconstruction |
| Topology | Implicit heavy-hex filename/path and raw records | No saved topology column and no field entry for an added one; history anchors raw content, not a general topology-schema check |
| Circuit identity | `circuit`, `_selected.txt` | Missing/extra unique identities detected; duplicate rows collapsed before count comparison |
| Status / error direction | `status`, `error_kind` | Exact strings; useful guard but shared producer |

The review's independent calculation confirms the ordinary saved values. That does not cure a validator accepting materially invalid values. Sample count, unique seed count, process count and compilation-repeat count should be separately named in any future schema; `n_seeds` alone does not prove all four.

## F. Publication surfaces and rendered PDF

The documented Windows Pandoc/Chrome command successfully built a 12-page PDF from the frozen manuscript. Its review-time SHA-256 is `ed159523c23832542d13ab0c36a2818e02bfc9f5b924ae4e9111b5d764897ffe`; this identifies this build only. It is not an expected hash for future builds. The visible endpoint table, corrected issue values, version-4 designation and 10.9 transition-width statement were inspected. A contact sheet and full-resolution selected pages are included.

The standard build's stylesheet URL is wrong: `publish/paper.html` refers to `publish/paper_style.css`, resolving to `publish/publish/paper_style.css`. That file does not exist. Correcting only the href in a disposable HTML output changes the document from 12 to 14 pages. The standard PDF is readable, but it is not using the intended stylesheet, and stage 13 does not inspect layout.

The mutated PDF was also visually inspected: its abstract visibly prints **99.9 percentage points**. The replacement affects six occurrences of the `10.9` text sequence on pages 1, 8 and 9, including occurrences within longer numbers. That additional corruption only reinforces the disagreement; the primary demonstrated false claim is the abstract's transition width. All 13 unmodified stages pass.

The v3-source PDF, built through the same publication script and then supplied beside unchanged v4 Markdown, is rejected by stage 13. This is a successful version/phrase check, not proof of general stale-PDF detection. The same-version false PDF passes.

`historical/2026-09-04-v1-bundle/PAPER.md` carries an explicit SUPERSEDED banner and directs readers to the root manuscript. Its old content is valid historical evidence, not an active scientific claim. A newly supplied root `BUNDLED_PAPER.md` containing that older content is outside the designated root-file checks; the controlled test is not evidence that such a v4 release bundle currently exists.

The root README and the research log's front-page LIVE table are different: they explicitly present old claims as current. They retain the version-pair-free band, incorrect issue differences, old sample/compute claims and broader repeatability/causal assertions. Moving one historical bundle did not make those active surfaces consistent.

## G. Independent numerical findings and primary-source comparison

The completed raw-only reconstruction uses no project analysis imports. Its integer histogram convolution counts the ordered with-replacement triples using the exact comparison `10*S_B >= 11*S_A`; it uses separate raw loading and paired bootstrap code. The original risk-interval replay preserves the published 400×400,000 MC procedure and random stream; analytical zero intervals are used for constant arms. It does not substitute a different estimator's interval and then declare a mismatch.

- 39 circuits, 78 arms, 200 distinct paired seeds per arm, 15,600 observations.
- 36 resolved, 3 unresolved; 13 boundary flags overall; 26 eligible.
- Risk-interval exclusion: 12/26; risk at least 5%: 7/26; risk at least 10%: 4/26.
- All 36 original risk intervals reproduce within 5e-7 saved rounding; maximum observed difference is approximately 5e-7.
- Spearman risk–distance association: −0.8329214038556598, descriptive rather than mechanistic.
- The preserved auxiliary calculations include the transition bands, pooled k-sweep, selection calculation, local issue-comparison means and 216 cross-machine integer-count matches. They are not universal determinism proofs.

The primary [Qiskit issue #14402](https://github.com/Qiskit/qiskit/issues/14402) reports the following linear-topology comparisons. The local column is this study's independently reconstructed 12-seed ratio of arm means, not a reproduction of the issue's unavailable full configuration or aggregation protocol.

| Circuit | External issue (%) | Local study (%) | Local minus issue (pp) |
|---|---:|---:|---:|
| bv_n140 | 46.1415237365 | 35.2065186850 | −10.9350050514 |
| bv_n280 | 44.2451420030 | 44.5332001997 | +0.2880581967 |
| knn_341 | 44.0600522193 | 43.4259710710 | −0.6340811483 |

The root manuscript's corrected issue table agrees after rounding. Its remaining +41% mentions are explicitly correction quotations. The research record contains old +41% values and its active front table/README still advertise the obsolete +2.4 pp difference. Historical sections can be preserved if their active status is corrected.

Exact-threshold testing used constant 200-observation arrays and a rational arithmetic oracle. A=100/B=109 yields NO_REGRESSION, A=100/B=110 yields UNRESOLVED, and A=100/B=111 yields REGRESSION in both actual implementations. With A=10,000,000,000 and B=11,000,000,000±1, the oracle is strictly below/above the threshold but both implementations return UNRESOLVED because of their 1e-9 guard. All synthetic cases are boundary cases. No recorded primary classification changes; this is a small policy/tolerance issue, not a failure of the empirical endpoint.

## H. Confirmed findings

### V4-01 — MAJOR — Nonfinite values evade saved-result validation

1. **Location:** `derived_binding.py:82–86, 103, 141–150`; `coerce`, `main`.
2. **Exact claim:** “every saved primary field reproduces from a replay of its own analysis.”
3. **Procedure:** In a disposable copy, set both risk interval bounds to `NaN` for all 36 resolved rows; leave raw evidence, point risks, flags and Markdown unchanged; run unmodified `verify.py`.
4. **Observed result:** Exit 0, all 13 stages PASS. The comparator evaluates `abs(NaN - want) > tolerance` as False. Ordinary single-bound and exchanged-interval variants are correctly rejected by stage 11, confirming that this is not a missing invocation. Separately, `n_seeds=200.9` and `k=3.9` are accepted by stages 6, 8 and 11 because the latter truncates their values. A duplicate row is accepted by stages 8 and 11 but rejected by stage 6 through changed numerical aggregates; it is not an additional full-pass example.
5. **Reproduction:** `python v4_mutations.py H_nan --full`; inspect `H_nan_result.json`, `H_nan_full.log` and the preserved altered CSV. Fresh-directory setup is described in REPRODUCTION.md.
6. **Why it matters:** The publication can carry meaningless uncertainty values while claiming every saved field was reproduced. Point flags remaining unchanged do not make the saved intervals valid.
7. **Smallest valid correction:** Reject nonfinite numeric fields before comparison; enforce valid probability bounds/order and typed integer/boolean schema; explicitly reject duplicate IDs and headers. Retain original-stream replay and rounding tolerances.
8. **Primary endpoint effect:** Raw reconstruction remains 12/26, 7/26, 4/26; saved uncertainty is invalid.
9. **Release-blocking:** YES.

### V4-02 — MAJOR — PDF semantic agreement is not enforced

1. **Location:** `pdf_binding.py:10–16, 75–116, 123–124`; `main`.
2. **Exact claim:** “the PDF's extractable text carries the same active claims and the same primary numbers as PAPER.md. Promised, and checked here.”
3. **Procedure:** Change reader-visible PDF text from 10.9 to 99.9, without changing Markdown or raw data; inspect rendered page; run all 13 unmodified stages.
4. **Observed result:** Exit 0, 13/13 PASS. The abstract visibly gives a false transition width. The checker only needs expected fraction strings somewhere, a version string and six phrase conditions.
5. **Reproduction:** `python v4_mutations.py PDF_false --full`; see `PDF_false_result.json`, `PDF_false_full.log`, `false_detail.png` and the altered PDF.
6. **Why it matters:** A completed full validation can approve a materially incorrect reader-facing scientific artifact. This is independent of PDF timestamps or byte identity.
7. **Smallest valid correction:** Bind a freshly rendered reference's normalized content and designated claim/table structure to the supplied PDF; compare all designated scientific fields and summaries. Otherwise explicitly narrow the check and require a documented human semantic review before release. Never equate token presence with full semantic reproduction.
8. **Primary endpoint effect:** Recorded endpoint unchanged; the displayed transition-width claim is false.
9. **Release-blocking:** YES.

### V4-03 — MAJOR — Markdown source recognition is described as reader-visible validation

1. **Location:** `manuscript_binding.py:14–25, 47–85, 151–181`; `visible_text`, `parse_tables`, `main`.
2. **Exact claim:** “The manuscript with everything invisible removed”; “the table a reader sees states what the raw data produces.”
3. **Procedure:** Put the correct table inside a CSS-hidden div and display a false zero-of-26 statement; independently add a false abstract sentence assigning 7/26 to interval exclusion; render through the tracked publication path.
4. **Observed result:** Both stage 12 and stage 13 return 0 for these variants. Rendered inspection confirms the table is absent in the hidden-div case and the wrong abstract sentence is visible. These are stage-specific results, not additional asserted full-13 runs. Comments and duplicate canonical tables are rejected successfully.
5. **Reproduction:** `python document_qa.py`; inspect `document_qa.json`, `hidden_detail.png`, `abstract_detail.png`, per-stage logs and secondary-stage results.
6. **Why it matters:** Only HTML comments are removed. CSS visibility is not evaluated; a correct numerator from a different endpoint is exempted in prose. The implementation cannot support its visible-document assurance.
7. **Smallest valid correction:** Validate a designated rendered claim structure or render-derived representation, enforce explicit claim identity, and reject hidden/ambiguous canonical tables. Check abstract claims against their own endpoint keys, not a set of numerators.
8. **Primary endpoint effect:** Raw values unchanged; visible endpoint meaning becomes false.
9. **Release-blocking:** YES.

### V4-04 — MAJOR — Active reader-facing summaries retain withdrawn claims

1. **Location:** `README.md:18–40, 61–88, 187–188`; `RESEARCH_LANDSCAPE.md:18–42`; root review packet and linked historical sections.
2. **Exact claims:** “version-pair-free” marked LIVE; “14 of 39 circuits are perfectly deterministic”; “0.5 pp” and “2.4 pp”; “Five read-only checks ... in about 45 seconds.”
3. **Procedure:** Read root reader entry points and the research log's explicit current-status table; compare with raw reconstruction, primary issue values, actual 13-stage execution and root manuscript corrections.
4. **Observed result:** Active summaries retain false or superseded values and interpretations. The root manuscript instead has 13 constant pairs, corrected issue differences, a pair-dependent band, and a 13-stage verifier that took tens of minutes in this review. Its pristine full verifier passes while these active pages remain inconsistent.
5. **Reproduction:** See `reader_claim_matches.txt`; inspect the indicated pinned files and compare `baseline.log`, `independent.json`, `supplementary.json` and the primary issue.
6. **Why it matters:** Readers are directed to these summaries as current. An old section's historical date does not neutralize a front-page LIVE label or an active README claim.
7. **Smallest valid correction:** Update current summaries and LIVE status rows; label preserved historical sections as superseded where appropriate; make the current manuscript the explicit authority. Correct the actual runtime/stage description.
8. **Primary endpoint effect:** None to raw endpoint; current publication interpretation and reproducibility instructions are misleading.
9. **Release-blocking:** YES.

### V4-05 — MAJOR — Active manuscript assurances contradict their own limitations

1. **Location:** `PAPER.md:40–43, 206–222, 285–292, 319–320, 514, 548–549, 664–670`; `prereg_analysis.py:3–6`.
2. **Exact claims:** “distribution its own protocol produces”; “each count was reproduced from its seed”; “before the primary 39-circuit raw data existed.”
3. **Procedure:** Compare each active assertion with the manuscript's stated missing historical protocol, finite controls, unseeded backend, and explicit admission that Git establishes only commit order. Inspect the recorded replication/control scope.
4. **Observed result:** The stronger sentences remain alongside their narrower corrections. The controls cover finite subsets, not a fresh reproduction of all 15,600 observations. Local simulation is not the issue's established protocol. Git order does not prove data nonexistence or non-access. Unqualified variance-removal wording also survives at 548–549 despite separate backend randomness.
5. **Reproduction:** Read the cited pinned line ranges, `reader_claim_matches.txt`, `replication/replicate.py:164–230` and `supplementary.json` cross-machine count summaries.
6. **Why it matters:** A correction paragraph does not remove a contradictory active assertion. These statements concern what was measured, reproduced and known before analysis.
7. **Smallest valid correction:** Replace the active statements with the already available narrower formulations: local hypothetical protocol; tested integer-count agreement; commit order plus attributed process history; seed-attributable variance only. Remove “every figure” promises unsupported by the coverage map.
8. **Primary endpoint effect:** No change to the recorded empirical endpoint; provenance and interpretation must be narrowed.
9. **Release-blocking:** YES.

### V4-06 — MAJOR — Offline consistency is reported as authenticated historical identity

1. **Location:** `v2_anchor.py:31–36, 132–139, 192`; fallback branch and final success message.
2. **Exact claim:** “offline anchor bound to [v2]”; “primary evidence is byte-identical to v2 as published.”
3. **Procedure:** Independently compare the original anchor against all actual v2 blobs; test a changed measurement plus regenerated current manifest with history; test a shallow copy without v2 objects using an updated local transcript.
4. **Observed result:** The original transcript is correct. Available-history validation rejects the changed measurement. The no-history path authenticates no transcript beyond its commit-name string; a correspondingly updated transcript is accepted. It therefore reports a stronger property than it checked. A source archive also cannot run stage 9, so this is not described as a full-13 historyless success.
5. **Reproduction:** `python archive_qa.py`; `python v4_mutations.py F`; `python v4_mutations.py anchor_offline`; inspect their result JSON and anchor logs.
6. **Why it matters:** The verifier explicitly distinguishes current consistency from historical identity, then conflates them in its fallback success language. Authenticity requires an external trusted binding.
7. **Smallest valid correction:** Report “matches supplied v2 transcript; historical authenticity not established here” in fallback mode, or require a trusted externally authenticated transcript/commit binding. Keep the functioning Git-object path and say “canonical content” where LF normalization is allowed.
8. **Primary endpoint effect:** No defect in the original anchored evidence or endpoint; false assurance is possible for a supplied changed transcript and data.
9. **Release-blocking:** YES.

### V4-07 — MINOR — Negative-test acceptance does not distinguish validation failure from execution error

1. **Location:** `mutation_test.py:main`, especially construction of `caught` and `missed`.
2. **Exact claim:** “every mutation is caught by the layer that must catch it.”
3. **Procedure:** Execute every required layer on all eleven built-in fixtures and retain its reason. Separately feed the exact acceptance expression actual subprocess return codes from unrelated `RuntimeError` failures for each required layer.
4. **Observed result:** All eleven original fixtures currently fail for intended validation reasons with no traceback. For all eleven, unrelated nonzero exits also satisfy the acceptance expression. The latter is a focused acceptance-logic test, not a claimed full-verifier run or a claim that current baseline fixture results were crashes.
5. **Reproduction:** `python negative_reason_qa.py`; see all `negative_*.json` and per-layer logs.
6. **Why it matters:** A future fixture-specific runtime error could be credited as successful regression coverage. The clean control does not classify errors unique to changed fixtures.
7. **Smallest valid correction:** Use structured invariant IDs and distinguish validation rejection from infrastructure/runtime errors; assert the expected reason in each negative fixture.
8. **Primary endpoint effect:** None; currently observed built-in detections are genuine.
9. **Release-blocking:** NO, independently of the major findings.

### V4-08 — MINOR — The documented PDF build does not load its tracked stylesheet

1. **Location:** `publish/build_paper.sh:21–22`; generated stylesheet URL; layout promise at lines 7–8.
2. **Exact claim:** “the PDF's extractable text and layout reproduce from PAPER.md ... checked by pdf_binding.py.”
3. **Procedure:** Resolve the generated HTML stylesheet href; rebuild an otherwise identical disposable HTML file with the correct relative href.
4. **Observed result:** Standard link resolves to absent `publish/publish/paper_style.css`. Correcting href changes 12 pages to 14. Stage 13 has no layout checks. The original build was visually readable.
5. **Reproduction:** `python pdf_visual_qa.py`; see `pdf_visual_qa.json`, `baseline_contact.png`, `fixed_css_first.png`.
6. **Why it matters:** Tracked styling is not actually applied, and layout verification is overclaimed. This is separate from expected timestamp-driven PDF hash changes.
7. **Smallest valid correction:** Use `--css=paper_style.css` for HTML emitted into `publish/`; add a build smoke check that assets resolve and inspect rendered pages. Narrow the layout-check description.
8. **Primary endpoint effect:** None.
9. **Release-blocking:** NO by itself; fix before preparing the final PDF.

### V4-09 — MINOR — Equality repair also introduces a near-threshold classification band

1. **Location:** `prereg_analysis.py:TIE_EPS, analyse`; `raw_endpoint.py:reconstruct`.
2. **Exact claim:** Classification follows the strictly above / strictly below threshold rule “without deviation.”
3. **Procedure:** Compare both actual implementations with a rational oracle on constant arrays at exact equality and at ±1e-10 from the threshold.
4. **Observed result:** Exact equality is correctly UNRESOLVED. Both immediately adjacent rational examples inside the 1e-9 guard are also UNRESOLVED, despite being strictly above/below. Ordinary 9% and 11% cases classify correctly.
5. **Reproduction:** `python portability_threshold_qa.py`; see its threshold result table.
6. **Why it matters:** A tolerance policy is not literal exact ordering. The guard is documented locally, but broader “without deviation” descriptions omit it.
7. **Smallest valid correction:** Explicitly state the numerical tolerance in the analysis contract, or compare bootstrap endpoints with an exact/sufficiently accurate method that preserves intended strict ordering.
8. **Primary endpoint effect:** None on recorded data; synthetic examples are boundary cases.
9. **Release-blocking:** NO.

### V4-10 — MINOR — Source-archive hashing fallback is not a stage-1 fallback

1. **Location:** `pin_check.py:16–18, 72–76`; `sweep_bp.py:benchpress_canonical_pin`.
2. **Exact claim:** Canonical bytes use Git blobs “otherwise the working tree normalised to LF.”
3. **Procedure:** Test clean pinned sparse Git checkouts under LF and CRLF; separately test the five identical canonical source files without `.git`.
4. **Observed result:** Both clean Git checkouts pass stage 1. Both no-history helpers reproduce all five hashes, but stage 1 exits 1 because live commit is None. This does not invalidate the repaired cross-platform Git-checkout behavior.
5. **Reproduction:** `python git_checkout_qa.py`; `python portability_threshold_qa.py`; see `git_checkout_qa.json` and `pin_no_git_*.log`.
6. **Why it matters:** Helper-level source equivalence and complete stage identity have different prerequisites.
7. **Smallest valid correction:** State that stage 1 requires a pinned Git checkout; describe no-history canonical hashing only as a helper capability, or introduce an explicitly weaker authenticated archive mode.
8. **Primary endpoint effect:** None.
9. **Release-blocking:** NO.

Each finding's ID and severity are in its heading; the numbered fields supply location, claim, procedure, result, reproduction, importance, correction, endpoint effect and release-blocking status—the requested eleven attributes in total.

## I. Search for a failure of the narrowed empirical result

No fatal counterexample to the recorded empirical endpoint was found. Independent point calculations, the original uncertainty replay, correct pairing, evidence identity and the 78-arm/780-fragment relationship all support it. The reported original intervals are reproducible; this review does not assert calibrated population coverage beyond the recorded sampling scheme.

The demonstrated failures concern saved-artifact validity, reader-visible content and assurance scope. They are material enough to block release preparation even while the underlying raw result survives. Exact-threshold equality, ordinary interval changes, the original negative fixtures, version-mismatched PDF detection, canonical LF/CRLF hashing and explicit historical-manuscript labeling survived their respective checks.

## J. Minimal correction set and release gate

1. Enforce finite, typed saved fields and unique row identities; add NaN and fractional-metadata regression cases with explicit validation reasons.
2. Replace PDF token-presence assurance with a defined content/claim binding, or explicitly require a documented human semantic review instead of claiming automatic equivalence.
3. Make manuscript checks aware of rendered visibility and claim identity. Add the wrong-abstract and CSS-hidden-table cases.
4. Correct active README and LIVE research summaries and remove the manuscript's remaining contradictory protocol, chronology and reproduction claims.
5. Accurately label the historical anchor's offline trust boundary; preserve its working Git-object comparison.
6. Fix the stylesheet path and qualify layout, threshold-tolerance and no-history source claims. Improve negative-test error classification.
7. Rerun the relevant controlled cases and the unmodified complete verifier on the corrected frozen revision. Then prepare final PDF and ZIP, inventory their actual contents, and review their reader-facing surfaces. No absent ZIP should receive a PASS.

The review establishes readiness defects; it does not implement repairs or authorize publication. The next release gate should require both numerical correctness and an accurate statement of what the verification system actually enforces.
