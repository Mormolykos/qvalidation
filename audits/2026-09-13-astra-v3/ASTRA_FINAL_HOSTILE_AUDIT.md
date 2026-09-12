# ASTRA final hostile audit — qvalidation v3

Target: **839ac80cd36ac44c7bab12e3b5a19c9dceb95c76**. Audit dates: 2026-09-12–13.

**Publication should be blocked on the assurance and claim-consistency defects below. No fatal invalidation of the pinned empirical endpoint was found.**

The strongest new chain is executable: the visible primary table can say **0/26, 0/26, 0/26** while all nine verifier stages pass, because correct rows hidden in an HTML comment are treated as the manuscript. Independently, every saved risk interval can be corrupted while 9/9 passes, and one changed raw observation plus a regenerated manifest passes all nine stages. These are distinct failures; they do not show that the unmodified measurements or original intervals are wrong.

The original repository was not edited, committed, tagged or published. Work used a separate clone detached at the exact target; mutations used disposable sibling clones. Original HEAD and tracked cleanliness were checked again at completion. Initial HEAD/origin-master equality was a local tracking-ref check, not a fresh remote-server verification. No scientific compiler runs were repeated. No unrelated SDK development was inspected. The only external SDK source inspected was the pinned Benchpress flow required by the task.

The fresh ledger was written before reading the prior hostile review or correction ledger. Its original creation-time assessments remain in [FRESH_CLAIM_LEDGER.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/FRESH_CLAIM_LEDGER.md); final resolutions are appended there. The supplied final PDF and staged ZIP were inspected only after the user identified them. The stylesheet was used as an external input, without changing the repository.

## Independent numerical reconstruction

The primary implementation in [independent.py](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/independent.py) imports no project analysis code. It reads the 78 primary JSONL files, sorts and validates paired seed identities, computes arm means, and convolves **integer count histograms** for ordered with-replacement triples. The call event is **10·Sb ≥ 11·Sa**; the denominator is 200⁶ = 64,000,000,000,000. Baselines are positive. The selected panel is exactly the smallest 200 unique values from 400 candidate draws with RNG 20260904; all 78 arm files match that panel and have ten recorded process IDs.

Theta is mean(B)/mean(A)−1. Its interval uses 4,000 joint paired-index resamples with RNG 20260904 and NumPy linear-interpolated 2.5/97.5 percentiles. Strict above/below defines REGRESSION/NO_REGRESSION; otherwise UNRESOLVED. Boundary means absolute theta-to-0.1 distance ≤3 percentage points. Reference classification is frozen during the risk bootstrap. The original risk bootstrap uses RNG 20260905, 400 paired outer resamples, and independent arm draws for 400,000 inner mean-of-three trials. [bootstrap_replay.py](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/bootstrap_replay.py) replays that complete original stream; constant zero-risk rows are handled analytically. This is distinct from the verifier’s new exact-inner stream.

| Quantity | Independent result |
|---|---:|
| Raw primary observations | 15,600 |
| Resolved / unresolved | 36 / 3 |
| Boundary flags overall / among resolved | 13 / 10 |
| Eligible | 26 |
| Eligible intervals excluding zero | 12 / 26 |
| Eligible point risk ≥5% / ≥10% | 7 / 26; 4 / 26 |
| Constant eligible pairs / stochastic resolved pairs | 13 / 23 |
| Reproduced original risk intervals | 36 / 36; maximum saved-rounding error 0.0000005 |
| Risk–distance Spearman rho | −0.8329214038556598 |
| cc_n32 exact call numerator/denominator | 239,417,152,405 / 64,000,000,000,000 |
| 20-run pooled bv_n140 heavy-hex risk | 3.7414736766% |
| Largest WR versus WOR risk difference | 0.0010648980434 probability units |
| Family-bootstrap interval | [17.39130435%,80.95238095%] |
| Paired k=3 risk, bv_n280 / knn_n67 | 17.2809% / 17.51975% |
| Linear bv_n140 attainable support | [−17.67810026%,109.17431193%] |
| Issue value percentile in that linear distribution | 87.75733855% |

The first apparent divergence was boundary counting: 13 flags overall versus 10 resolved boundary exclusions. Resolving the overlap with the three unresolved circuits restores the same 26-circuit eligibility set; it is not an arithmetic failure. All original theta point estimates, reference verdicts, flags and theta intervals match their saved rounding. The new exact risk-bootstrap stream gives the same aggregate endpoint, but **does not reproduce the saved intervals**; see A01.

## Verifier trace and provenance

| Stage | Actual authority / operation | What a pass does not establish |
|---|---|---|
| 1 | External Benchpress HEAD, tracked status, five checkout-byte hashes | Portable Git-blob identity; A14 |
| 2 | Behavioral pytest suite on synthetic/fixture inputs | Exhaustive correctness or correctness of every artifact |
| 3 | 44 frozen inventory values; 32 RAW-RECOMPUTED and 12 DERIVED-READ | Every manuscript claim; interval fields/denominators are not generally validated merely by checking value |
| 4 | Saved two-version replication records against expected artifact | Rerun of compilation or the whole primary study; it is a 144-count artifact check |
| 5 | Algebraic/synthetic proof of the withdrawn paired-column identity | Empirical manuscript correctness |
| 6 | Mixture of primary derived CSV reads, raw recomputations and Markdown token searches | All intervals, all claim placement, PDF consistency, external issue values |
| 7 | Raw observations through shared loader/boundary constant, separate float-PMF estimator and bootstrap | Exact original CI reproduction or all per-circuit summary fields; it binds only four aggregate integers |
| 8 | Current raw bytes versus mutable manifest; subset of CSV fields versus raw | v2 object identity or complete derived-artifact validity |
| 9 | Five canned mutations in fresh **git archive HEAD** snapshots | Worktree mutations not covered by those cases, hidden Markdown rows, or arbitrary summary-field corruption |

The new primary path genuinely reads raw observations: it is not just a new derived-to-derived circular chain. Its separate probability estimator is a useful independent implementation, but shares the project loader and boundary constant; the audit’s own implementation does not. The inventory’s 12 historical k-sweep rows are accurately labelled DERIVED-READ. The inventory’s old band rows concern the 12-seed 2.0.0→2.0.2 study, not the primary 23-circuit 10.9-pp band. The paper’s remaining 41/29/12 inventory description is stale: current counts are 44/32/12.

| Important quantity | This audit’s provenance classification | Actual verifier coverage |
|---|---|---|
| Primary theta / point risks | RAW-RECOMPUTED | Stage 7 rebuilds; stage 8 compares saved points within tolerance |
| All primary bootstrap intervals | RAW-RECOMPUTED | Audit fully replays original; verifier does not compare saved intervals |
| 12/26,7/26,4/26 | RAW-RECOMPUTED | Stages 3/7 rebuild; manuscript binding defeated by K |
| 10.9-pp primary band | RAW-RECOMPUTED | No matching primary-band check in the inventory/paper stage |
| 3.7415% at k=20 | RAW-RECOMPUTED | Stage 6 independently Monte Carlo-checks printed 3.74 with tolerance; audit uses PMF convolution |
| Historical 12 k-sweep inventory cells | DERIVED-READ | CSV versus fixed literals; disclosed |
| Issue values | EXTERNAL | Not revalidated by the nine-stage command |
| Selection p-value | RAW-RECOMPUTED | Stage 6 recomputes corrected grouping |
| 216 cross-machine matches | RAW-RECOMPUTED | Audit compares raw records; stage 4 alone is not this full three-version check |
| 0/24 backend control | NARRATIVE / N-A | Logged assertion; original factorial artifact unavailable |
| Saved-summary-based primary rows used in stage 6 | DERIVED-READ / DERIVED-RECOMPUTED | Reads points and recomputes ranks/counts from those points; stages 7/8 supply only partial independent coverage |

The baseline returned **9/9 PASS**. Its stage times sum to about 535 seconds in this audit, not under one minute; concurrent workload makes that a runtime observation rather than a universal benchmark. No test/source was weakened to obtain any mutant pass.

## Mutations

[MUTATION_TEST_LEDGER.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/MUTATION_TEST_LEDGER.md) records the full A–J set plus C2 and K. Full nine-stage runs were completed for the pristine target, H, K and F. Other cases ran the directly affected stages 6,7,8; a nonzero stage is sufficient to defeat the full conjunction, but these are not misrepresented as complete nine-stage executions. The pristine stage-9 execution also reproduced the supplied five-case suite.

## Findings

### A01 — MAJOR — Saved bootstrap results can be replaced while all nine stages pass

**Location:** [raw_integrity.py:108](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/raw_integrity.py:108); [raw_endpoint.py:178](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/raw_endpoint.py:178); [PAPER.md:637](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:637)

**Exact claim under attack:** The summary is required to be reproducible from raw; every published figure has a fresh recomputation.

**Why it fails / why the attack fails:** The consistency check compares status, verdict, theta and a nonempty point-risk field. It does not compare the saved theta intervals, risk intervals, boundary flag, error_excludes_zero, p_call, sample count or full row membership. The new reconstruction also uses a different bootstrap stream: it omits the original inner Monte Carlo RNG consumption. Agreement of three counts cannot certify the saved intervals.

**Independent evidence:** Mutation H replaces every one of the 36 saved risk intervals with [0.900000, 0.999999]. Full verify.py returns 9/9 PASS. Pristine independent MC replay reproduces all 36 original intervals within 0.0000005 rounding error. Thus this is a verifier defect, not evidence that the original intervals were fabricated. New exact-stream intervals differ: bv_n280 [0.1177340704,0.2427296891] versus saved [0.115990,0.236869]; swap_test_n83 [0.0969299492,0.2123290094] versus [0.101924,0.227535].

**Reproduction:** python mutations.py H --full; python bootstrap_replay.py. See mutH_full.log and bootstrap_replay.json.

**Smallest valid correction:** Validate every reported interval and classification field against its declared algorithm/stream, and validate exact row membership. Either reproduce the original MC bootstrap or deliberately replace and regenerate its results with an explicitly documented exact bootstrap. Register the actual primary 10.9-pp band as well; the inventory currently checks a different historical band dataset.

**Primary endpoint impact:** Pinned endpoint unchanged. Corrupted interval artifacts falsely imply zero-exclusion even for genuinely zero-risk circuits; the cached flags and headline counts remain unchanged.

**Publication blocked by this finding:** Yes.

### A02 — MAJOR — Invisible correct rows certify a false visible primary table

**Location:** [raw_endpoint.py:202](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/raw_endpoint.py:202); [paper_check.py:52](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/paper_check.py:52); [PAPER.md:379](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:379)

**Exact claim under attack:** The raw-to-paper check is bound to the specific results-table rows.

**Why it fails / why the attack fails:** Both checkers search raw Markdown text and accept the first matching rows. Neither excludes HTML comments nor establishes uniqueness or validates the rendered table. A hidden copy of the correct rows shadows the actual results table.

**Independent evidence:** Mutation K changes all three visible counts to 0 / 26 and prepends the original rows inside an HTML comment. Full verify.py returns 9/9 PASS. Pandoc with the specified markdown+pipe_tables+raw_html reader renders only the false 0 / 26 rows; the correct comment is invisible.

**Reproduction:** python mutations.py K --full; pandoc mutK/PAPER.md --from=markdown+pipe_tables+raw_html --to=plain --wrap=none. See mutK_full.log and mutK_rendered.txt.

**Smallest valid correction:** Parse the manuscript structure/rendered document, reject duplicate or ambiguous endpoint tables, ignore comments, and compare every numerator, denominator and proportion in the actual designated table. Add this exact shadow-row mutation.

**Primary endpoint impact:** Raw scientific endpoint stays 12/26,7/26,4/26; the published visible endpoint is changed to 0/26,0/26,0/26 while verification passes.

**Publication blocked by this finding:** Yes.

### A03 — MAJOR — A regenerated manifest does not enforce v2 evidence identity

**Location:** [raw_integrity.py:49](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/raw_integrity.py:49); [raw_integrity.py:66](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/raw_integrity.py:66); [raw_integrity.py:86](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/raw_integrity.py:86); [V3_CORRECTION_LEDGER.md:10](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/V3_CORRECTION_LEDGER.md:10)

**Exact claim under attack:** Raw evidence remains byte-identical to v2 and raw_integrity.py enforces that going forward.

**Why it fails / why the attack fails:** The verifier hashes current checkout bytes against an equally mutable manifest. It never compares those hashes with the trusted v2 Git objects, nor rejects disagreement with the audited qvalidation HEAD. Numerical summary tolerances allow small changed observations to retain green checks.

**Independent evidence:** Mutation F changes multiplier_n45 candidate seed 663193 from 7315 to 7316 and runs raw_integrity.py --write, without updating the summary. Full verify.py returns 9/9 PASS. Independently computed risk changes from 0.028724114619140626 to 0.028726752145875, and theta from 0.07473276727488987 to 0.0747335005745402. The raw bytes no longer match v2.

**Reproduction:** python mutations.py F; run verify.py in mutF with BENCHPRESS_PATH set. See mutF_full.log, edge_cases.json and metadata_checks.json.

**Smallest valid correction:** For the claimed immutable-v2 contract, verify against the externally trusted v2 commit/blob identities and compare the current worktree with that evidence. Alternatively narrow the assurance to manifest self-consistency and require an independently authenticated manifest for publication.

**Primary endpoint impact:** Individual measured science changes; coarse primary counts do not.

**Publication blocked by this finding:** Yes.

### A04 — MAJOR — Withdrawn evidence remains active in the staged archive

**Location:** [SETTLED.json:86](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/SETTLED.json:86); [bundle/PAPER.md:21](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/bundle/PAPER.md:21); [bundle/PAPER.md:238](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/bundle/PAPER.md:238); [followup3.py:100](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/followup3.py:100)

**Exact claim under attack:** All 22 corrections are closed; the synthetic null and universal interpretation have been withdrawn.

**Why it fails / why the attack fails:** SETTLED S11 still endorses the ungenerated null (mean -0.661; 5 of 30 trials), describing a different mechanism claim as withdrawn. bundle/PAPER.md still asserts universal monotonicity, version-pair independence, categorical unresolvability, bit identity, independent seeds and the old issue comparison. Its draft date identifies age but does not mark these assertions as invalid or withdrawn. followup3.py still prints version-pair-free/true-change rhetoric.

**Independent evidence:** The user-supplied staged ZIP includes both manuscript versions. All 1,034 tracked files in that ZIP exactly match target Git archive content, so this is present in the proposed release, not debris outside the target. The root manuscript/PDF explicitly withdraw the synthetic-null numbers; this finding concerns the other still-authoritative artifacts.

**Reproduction:** Read the cited files; run pdf_audit.py to confirm archive membership and byte identity. Inspect SETTLED S11 result and bundle/PAPER.md abstract and section 4.1.

**Smallest valid correction:** Mark historical artifacts prominently as superseded and their invalid assertions as withdrawn, or exclude obsolete reader-facing bundle copies from the release. Update active SETTLED claims and generated narrative. Do not erase the historical audit record.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** Yes.

### A05 — MAJOR — Categorical unresolvability and true-change language survive their correction

**Location:** [PAPER.md:401](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:401); [PAPER.md:430](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:430); staged PDF p.8

**Exact claim under attack:** A true change anywhere in an 11-point-wide window is unresolvable by a three-run comparison; the band contains no theta.

**Why it fails / why the attack fails:** A 5%-95% call-probability transition is not an impossibility theorem. Near an endpoint, one outcome has about 95% probability. The swept multiplier also differs from ratio-of-means change by C=(mean(B)/mean(A))/mean(B/A). The immediately preceding correction discloses this but the unchanged interpretation again calls the whole axis true change and unresolvable.

**Independent evidence:** Independent residual calculations give median parameter width 10.8685952 pp, median transformed mean-change width 10.8521192 pp. For cc_n64, C≈0.99103669 transforms 25.13409 to 24.90880 pp. These support the approximate scale, not the categorical sentence. The staged PDF carries the same sentence.

**Reproduction:** python supplementary.py; inspect supplementary.json bands and PDF page 8.

**Smallest valid correction:** Replace the remaining categorical sentence with the operational transition definition and label the sweep parameter consistently. State width, population of 23 resolved stochastic circuits, version pair, residual model, k and threshold together.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** Yes.

### A06 — MAJOR — The abstract retains an unsupported quantitative attribution

**Location:** [PAPER.md:27](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:27); [PAPER.md:362](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:362); staged PDF pp.1,7

**Exact claim under attack:** The risk-distance association is largely induced by the decision rule itself.

**Why it fails / why the attack fails:** Largely asserts how much of the measured association is induced. The universal theorem is false; the synthetic null is withdrawn; the body explicitly says no quantitative claim about the induced amount is made. Neither a descriptive correlation nor a fixed-shape location argument establishes this abstract claim.

**Independent evidence:** Raw Spearman correlation reproduces -0.8329214039. Internal counterexample: bv_n280 distance 5.1102 pp/risk 17.3147% versus adder_n118 distance 3.5301 pp/risk 12.6743%. External construction gives distance 1 pp/risk zero versus distance 29.7 pp/risk 21.6%. These refute universality but do not quantify the origin of the empirical correlation.

**Reproduction:** python independent.py snapshot independent.json; python supplementary.py; compare abstract with section 4.1.

**Smallest valid correction:** Describe the measured association without attributing a predominant induced component, unless a reproducible, explicitly scoped model establishes that attribution.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** Yes.

### A07 — MAJOR — The issue comparison still asserts an unavailable protocol and a wrong value

**Location:** [PAPER.md:39](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:39); [PAPER.md:138](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:138); [PAPER.md:485](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:485); staged PDF pp.1,3,9

**Exact claim under attack:** knn_341 rose about 41%; the support describes the distribution the issue’s own protocol produces.

**Why it fails / why the attack fails:** The corrected table reports +44.060%, but section 2.2 retains +41%. The abstract and section 4.4 retain own-protocol language despite admitting that the historical aggregation/configuration is unavailable. A numerical comparison under this study’s linear 12-seed ratio-of-means design is not a reconstruction of the issue protocol.

**Independent evidence:** The primary issue reports knn_341 0.4406005221932115, bv_n280 0.4424514200298953, bv_n140 0.4614152373646045. Independent local means give 43.4259711%,44.5332002%,35.2065187%, respectively. The corrected table differences are right. Mutation I changes +44.060% to +94.060%; stages 6,7,8 all pass, showing this external value is not actually checked there.

**Reproduction:** python supplementary.py; compare [Qiskit issue #14402](https://github.com/Qiskit/qiskit/issues/14402) with the cited source locations; python mutations.py I.

**Smallest valid correction:** Correct the remaining +41% and replace both own-protocol assertions with explicit model/configuration-specific comparisons. Preserve the admitted historical unknowns.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** Yes.

### A08 — MAJOR — Determinism is asserted more broadly than the controls establish

**Location:** [PAPER.md:149](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:149); [PAPER.md:265](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:265); [PAPER.md:276](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:276); [PAPER.md:515](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:515); [DEFECTS.md:238](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/DEFECTS.md:238)

**Exact claim under attack:** Gate counts are deterministic functions of seed; one seed_transpiler argument removes sampling variance at k=1.

**Why it fails / why the attack fails:** The backend is generated with unseeded error rates. The 0/24 evidence is a limited research-log control without the original factorial generator/trial artifact, not proof that all other randomness is absent. The conclusion correctly narrows repeatability to this source, but the methods and fixed-seed sensitivity sentence remain unconditional. DEFECTS calls the confound dead/not a confound.

**Independent evidence:** The pinned FlexibleBackend forwards no backend seed. The log describes 6 circuits×4 seeds×4 distinct backend draws and zero observed count changes. The separate exp1 script is a different experiment, not the missing original factorial replay. All 216 recorded cross-machine gate counts do match. bv_n280 fixed seed 663193 yields 1040→1157 (+11.25%) although its empirical mean change is +4.89%.

**Reproduction:** Read the pinned backend constructor, RESEARCH_LANDSCAPE.md:1568 onward and the cited claims; supplementary.py checks cross-machine counts; independent.py reads fixed-seed observations.

**Smallest valid correction:** State repeatability observed in the measured controls and removal of variation attributable to changing seed_transpiler. Describe the 0/24 result as a limited logged control, preserve other randomness as an explicit uncertainty, and remove universal determinism implications.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** Yes.

### A09 — MINOR — Local commit order is again described as first-access evidence

**Location:** [PAPER.md:190](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:190); [PAPER.md:298](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:298); [PAPER.md:452](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:452); [prereg_analysis.py:3](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/prereg_analysis.py:3)

**Exact claim under attack:** The analysis predates the existence of the data; the follow-up was blind; the second-machine document predates the machine’s existence.

**Why it fails / why the attack fails:** Git records committed chronology, not when data were first produced or inspected. The body correctly states this limit, but other sentences and the analysis header still infer that tuning was impossible. There is no evidence here of fabrication or tuning; the stronger inference simply does not follow.

**Independent evidence:** Local preregistration a36a34a 2026-09-03 23:51:08+03; analysis/list fbc573d 23:52:38; primary raw commit 30224a0 2026-09-04 09:13:07. Earlier census/exploration already existed. Later controls have separately later commits.

**Reproduction:** python integrity_history.py; inspect integrity_history.json history and the cited sentences.

**Smallest valid correction:** Use before the primary raw-data commit / before the laptop-data commit and identify blindness/non-access as an author process assertion unless independently documented.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### A10 — MINOR — Matching rustworkx versions/builds are not established by the measurement artifacts

**Location:** [PAPER.md:313](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:313); [PAPER.md:549](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:549); crossmachine/*_{q143,q200,q202}.jsonl environment records

**Exact claim under attack:** Both machines ran rustworkx 0.18.1 / the same rustworkx build.

**Why it fails / why the attack fails:** The compared measurement records omit rustworkx metadata. Current software state or a later recorder change cannot establish the versions in the historical runs. Equal version numbers would also not alone establish identical builds.

**Independent evidence:** All six per-machine/per-version records were inspected; supplementary.json preserves their environment records. Gate counts and platform metadata are present, rustworkx version/build metadata is absent.

**Reproduction:** python supplementary.py; inspect crossmachine environment records and manuscript sentences.

**Smallest valid correction:** Label the graph-library version as a retrospective author assertion with its actual provenance, or supply contemporaneous environment/build evidence. Keep the supported 216-count match.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### A11 — MINOR — The no-aggregation scope remains inconsistent

**Location:** [PAPER.md:76](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:76); [PAPER.md:120](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:120); [PAPER.md:105](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:105)

**Exact claim under attack:** The suite performs no aggregation over runs; the Qiskit-based gyms use the same preset-pass-manager path.

**Why it fails / why the attack fails:** The correction is about returned gate-count aggregation, while the introductory sentence still generalizes to all aggregation. Benchmark repetition/timing summaries are distinct. The transpiler-service gym also has a TranspilerService path rather than that exact preset-pass-manager call.

**Independent evidence:** The pinned QASMBench path creates its pass manager with optimization level/backend, runs it through the benchmark fixture and records count_ops on the returned circuit. The service gym has a different call flow. Explicit BQSKit seed=0 is verified for the cited sibling examples, not every BQSKit benchmark.

**Reproduction:** Inspect the pinned benchpress/qiskit_gym/abstract_transpile/test_qasmbench.py, qiskit_gym/utils/io.py and qiskit_transpiler_service_gym/abstract_transpile/test_qasmbench.py.

**Smallest valid correction:** Restrict each source claim to the inspected local Qiskit compilation path and absence of repeated-run gate-count aggregation; avoid statements about every gym or timing aggregation.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### A12 — MINOR — Exact threshold ties are mishandled by the floating reference classification

**Location:** [prereg_analysis.py:133](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/prereg_analysis.py:133); [raw_endpoint.py:143](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/raw_endpoint.py:143); [raw_endpoint.py:91](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/raw_endpoint.py:91)

**Exact claim under attack:** An interval exactly at the threshold is unresolved; the new risk path uses exact integer convolution.

**Why it fails / why the attack fails:** The reference bootstrap compares floating ratios with 0.1. For constant A=100 and B=110, the exact reference is 1/10 but floating B/A-1 is 0.10000000000000009, so the strict rule labels REGRESSION instead of UNRESOLVED. Separately, raw_endpoint convolves float probabilities, not integer counts, although its decision inequality is evaluated with integer cutoffs.

**Independent evidence:** edge_cases.json records exact Fraction(1,10), the floating value and the differing classifications. The case remains boundary-excluded, so it cannot change this paper’s eligible endpoint. Independent integer convolution agrees with 150 ordered brute-force cases exactly; no such primary-data divergence was found.

**Reproduction:** python edge_cases.py; inspect the reference comparison and raw_endpoint.ksum_pmf dtype.

**Smallest valid correction:** Handle equality in the reference classifier using exact sums/rational comparisons or a justified tie policy; add exact-cut tests. Describe float PMF convolution accurately or use integer-count convolution for k=3.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### A13 — MINOR — The staged PDF needs an unarchived build input

**Location:** [PAPER.md:669](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md:669); staged publication archive

**Exact claim under attack:** The artifact is independently reproducible from the archived code/data.

**Why it fails / why the attack fails:** The PDF itself can reasonably be a publication-time build artifact, but paper_style.css and the complete build recipe/toolchain are absent from the archive. Rebuilding therefore requires a file supplied separately by the author.

**Independent evidence:** The user supplied C:/Users/User/Desktop/bad/paper_style.css. With that input, pandoc plus headless Chromium Edge produced 13 pages whose whitespace-normalized extracted text exactly matches the staged PDF. PDF hashes differ, as expected for browser/metadata-dependent builds; no content divergence was found. All three staged-file hashes match the user’s values.

**Reproduction:** Run pdf_audit.py and the commands in REPRODUCTION.md; see pdf_audit.json and pdf_contact_sheet.png.

**Smallest valid correction:** Archive the stylesheet and an executable PDF-build command with tool versions. Define content/layout reproducibility separately from byte-identical PDF reproduction.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### A14 — MAJOR — The toolchain hash pin still depends on CRLF checkout bytes

**Location:** [sweep_bp.py:70](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/sweep_bp.py:70); [verify.py:91](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/verify.py:91); [results/raw/benchpress_pin.json](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/results/raw/benchpress_pin.json)

**Exact claim under attack:** A replicator can verify the pinned Benchpress revision with the integrity command.

**Why it fails / why the attack fails:** All five recorded Benchpress module hashes identify CRLF checkout bytes, not the pinned Git blob bytes. A normal LF checkout at the identical clean commit produces five mismatches. The new qvalidation raw-data -text attribute cannot change checkout behavior in the separate Benchpress repository.

**Independent evidence:** metadata_checks.json records all five recorded/checkout/Git/LF hashes. In every case CRLF→LF conversion exactly equals the pinned Git blob and fails the recorded hash comparison. This is an executable hash comparison, not a claim that a Linux host was run. The primary-data manifest itself passes both autocrlf settings.

**Reproduction:** python metadata_checks.py; compare module_canonicalization entries. verify.py stage 1 explicitly rejects any of these five mismatches.

**Smallest valid correction:** Use canonical Git blob hashes for the external pin and separately check worktree semantic/canonical content, or specify and enforce an explicit portable source-byte policy. Do not silently rewrite raw historical metadata; version the corrected pin contract.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** Yes.

### N01 — NOT ISSUE — Primary empirical chain survives

**Location:** [PAPER.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md)

**Exact claim under attack:** 36 resolved, 3 unresolved, 10 resolved-boundary exclusions, 26 eligible; 12/26,7/26,4/26

**Why it fails / why the attack fails:** The attempted invalidation did not establish a defect in this narrowed claim.

**Independent evidence:** Independent raw-only integer-count convolution and paired bootstrap reproduce the classifications, point risks, all 39 theta intervals and all 36 original risk intervals. There are 13 boundary flags overall because all 3 unresolved circuits are also boundary-flagged.

**Reproduction:** independent.py; bootstrap_replay.py

**Smallest valid correction:** No correction to this supported result. Retain the stated scope and limitations.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### N02 — NOT ISSUE — Raw measurement identity survives

**Location:** [PAPER.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md)

**Exact claim under attack:** No primary measurements changed from v2

**Why it fails / why the attack fails:** The attempted invalidation did not establish a defect in this narrowed claim.

**Independent evidence:** All 78 worktree hashes equal target blobs, v2 blobs and manifest entries. No results/raw JSONL changed between the two commits. Both disposable autocrlf settings produce 78/78 identical primary raw files.

**Reproduction:** integrity_history.py

**Smallest valid correction:** No correction to this supported result. Retain the stated scope and limitations.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### N03 — NOT ISSUE — Conditional bootstrap scope and chosen estimand survive

**Location:** [PAPER.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md)

**Exact claim under attack:** The intervals concern a frozen empirical-panel classification, without established population coverage

**Why it fails / why the attack fails:** The attempted invalidation did not establish a defect in this narrowed claim.

**Independent evidence:** The manuscript now explicitly freezes verdict/boundary/eligibility and disclaims population coverage. The rare-tail counterexample remains a limitation, not a contradiction of that narrowed claim. Two alternative-estimand point-side disagreements occur only in already-unresolved dnn_n33 and dnn_n51.

**Reproduction:** independent.py; edge_cases.py; supplementary.py

**Smallest valid correction:** No correction to this supported result. Retain the stated scope and limitations.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### N04 — NOT ISSUE — Corrected auxiliary numerical results survive

**Location:** [PAPER.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md)

**Exact claim under attack:** Approximately 10.9-pp model width; 3.7415% twenty-run risk; corrected selection comparison

**Why it fails / why the attack fails:** The attempted invalidation did not establish a defect in this narrowed claim.

**Independent evidence:** Independent results: median unrounded multiplicative width 10.8685952 pp; truncated 10.8658241; additive 10.6794749/10.7331406. Pooled 400-seed bv_n140 heavy-hex k=20 risk 3.7414736766%; corrected selection 39/13, medians 0.1114670083/0.1260321599, p=0.4559911843. Fits 23 additive/3 multiplicative/13 ties.

**Reproduction:** supplementary.py

**Smallest valid correction:** No correction to this supported result. Retain the stated scope and limitations.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### N05 — NOT ISSUE — Pinned source and gate-count replication survive within their stated measurements

**Location:** [PAPER.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md)

**Exact claim under attack:** The inspected Qiskit path omits seed_transpiler; 216 cross-machine gate counts match

**Why it fails / why the attack fails:** The attempted invalidation did not establish a defect in this narrowed claim.

**Independent evidence:** Pinned revision b695f30e83a32bac05b9b4d8e98d37ba9aae5236 and parameter flow inspected; 58 circuit hashes and 5 current-checkout module hashes match. All 72 counts for each of three versions match across the two machine files. This does not establish full-circuit identity or universal repeatability.

**Reproduction:** metadata_checks.py; supplementary.py; cited external source files

**Smallest valid correction:** No correction to this supported result. Retain the stated scope and limitations.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

### N06 — NOT ISSUE — Staged PDF content and archive identity survive

**Location:** [PAPER.md](C:/Users/User/AppData/Local/Temp/astra-v3-839ac80-h1_mhdhj/snapshot/PAPER.md)

**Exact claim under attack:** The proposed PDF is built from the target manuscript

**Why it fails / why the attack fails:** The attempted invalidation did not establish a defect in this narrowed claim.

**Independent evidence:** Staged PDF hash 687b57d7f34f9bad477a2352235f18245823570b7d9b9127baddb7bb070402f6 matches; rebuilt text matches after whitespace normalization; all 13 pages rendered and inspected via contact sheet plus detailed result pages. The ZIP has no differences from 1,034 target tracked files.

**Reproduction:** pdf_audit.py

**Smallest valid correction:** No correction to this supported result. Retain the stated scope and limitations.

**Primary endpoint impact:** No change to the pinned primary endpoint.

**Publication blocked by this finding:** No.

## Chronology and correction closure

Author and committer timestamps are recorded separately in integrity_history.json; they agree for the principal milestones. These establish local commit order only.

| Phase | Commit / local timestamp (+03:00) | Implication |
|---|---|---|
| Initial measurements/censuses | e7b7a02, Sep 3 09:07:19 | Exploration predates preregistration |
| Heavy-hex identified as worst case | c426338, Sep 3 13:18:22 | Topology choice was informed by earlier exploration |
| Issue/initial deep analyses | 006bd52, Sep 3 21:57:27 | These are not blinded primary follow-up results |
| Scattered-seed follow-up | 4f35fd7, Sep 3 23:44:18 | Also predates primary registration |
| Primary preregistration | a36a34a, Sep 3 23:51:08 | Frozen follow-up design |
| Analysis and circuit list | fbc573d, Sep 3 23:52:38 | Committed before primary raw files |
| Primary raw files | 30224a0, Sep 4 09:13:07 | First tracked primary data |
| Sensitivity rounds | 21fc983 / 0c6c1f3, Sep 4 09:40:53 / 09:55:21 | Later, not part of initial preregistered evidence |
| Cross-machine design/desktop metadata | df09a07, Sep 8 19:40:19 | Separately preregistered later check |
| Laptop measurements | e3362fb, Sep 9 15:32:13 | Later recorded data |
| Cross-machine manuscript claims | b5567cb, Sep 9 15:44:31 | Follow-up reporting |
| Published-v2 target | 17e08f3, Sep 10 14:49:07 | Comparison baseline |
| v3 claims/correction ledger | 0eeb82e / d5b5adb, Sep 12 14:29:10 / 14:36:38 | Post-publication corrections |
| Audited raw-newline correction | 839ac80, Sep 12 16:02:47 | Exact target |

Each F-ID below refers to the prior audit’s finding, not the new A-IDs. Original defects and claimed fixes were located in V3_CORRECTION_LEDGER.md rows 35–56 and the preserved prior audit after the fresh ledger existed.

| Prior finding | Claimed fix / independent closure assessment |
|---|---|
| F01 verifier independence | **OPEN:** raw endpoint path added, original corruption caught; new H/K/F passes defeat full closure (A01–A03) |
| F02 IID seeds | Main manuscript accurately narrows to the order-statistic panel; all raw seed IDs match. Obsolete bundle remains (A04) |
| F03 universal monotonicity | Main theorem explicitly withdrawn; both counterexamples reproduce. Bundle still asserts it (A04); abstract attribution remains (A06) |
| F04 version-pair independence | Main abstract corrected; residual dependency explicit. Bundle and generated narrative remain wrong (A04) |
| F05 mechanism | Explicit compiler-mechanism claim withdrawn, but “largely induced” remains unsupported (A06) |
| F06 bootstrap population coverage | Conditional/frozen scope accurately disclosed. Original intervals reproduce. Verifier’s interval contract remains defective (A01), a different issue |
| F07 preregistration | Local chronology corrected in one paragraph; first-existence/blindness implications survive elsewhere (A09) |
| F08 selection | **Numerical fix verified:** exact 39/13 grouping and p=.455991; no valid independence proof inferred |
| F09 issue transcription | Corrected table verified; +41% remains in section 2.2 (A07) |
| F10 selective mismatch excludes version effects | Main causal exclusion withdrawn. No new evidence identifies a compiler mechanism; own-protocol wording still needs correction (A07) |
| F11 fixed seed guarantees correctness | Correctness separated in conclusion; unqualified sampling-variance/determinism language survives (A08) |
| F12 bit identity | Main count-only correction supported by all 216 counts; obsolete bundle remains. rustworkx assertion lacks recorded metadata (A10) |
| F13 cannot resolve | **OPEN:** exact categorical synonym “unresolvable” remains in main results/PDF (A05) |
| F14 true-change axis | Conversion disclosed and independently reproduced, but contradictory axis/interpretation prose survives (A05) |
| F15 29/39 fits | **Verified correction:** 23 additive,3 multiplicative,13 ties; both truncation conventions reproduced |
| F16 synthetic null | Main/PDF numbers clearly labelled withdrawn. Active SETTLED S11 and bundle still endorse them (A04) |
| F17 six of 1728 | Main fictitious-count framing removed; exact probability and declared-estimand theta interval reproduce |
| F18 bv_n140 support | Main support correction is consistent with raw extrema and ordered with-replacement support; old bundle remains stale |
| F19 no aggregation anywhere | Narrow correction added, broad introduction remains (A11) |
| F20 threshold sensitivity | Wrong endpoint table withdrawn; distinction between MC point-positive and CI-excluding-zero counts is now explicit |
| F21 compute hours | 20×2×approximately 2 h = 80 compute hours; corrected, approximate runtime source still disclosed as unconfirmed |
| F22 production gate | Main abstract now labels a hypothetical gate and says no published decision is shown wrong. Obsolete bundle still generalizes (A04) |

## Contradiction matrix

| Locations | Surviving assertion | Inconsistent limitation / result |
|---|---|---|
| Abstract 27–29 / Results 362–368 | Association largely induced by rule | No quantitative claim about how much the rule induces |
| Abstract 39 / Results 485 / Abstract 41–42 | Issue’s own protocol | Historical aggregation/configuration not reproduced |
| Background 138 / Results 476 | knn_341 +41% | Correct source +44.060% |
| Methods 149,265 / controls 276 / Conclusion 604–620 | Deterministic function of transpiler seed; removes sampling variance | Backend unseeded; only source-specific repeatability supported |
| Results 403–405,430 / Results 420–425 / Conclusion 595–600 | True-change window unresolvable | Sweep parameter differs from theta; operational 5%-95% transition |
| Methods 190 / correction 193–202 | Before primary data existed | Commit order does not prove non-access |
| Verification 637–655 / H,K,F | Every published figure / summary reproducibility / protected evidence | Full green checks on corrupt intervals, false visible table, changed raw plus manifest |
| Main Results 362–368 / SETTLED S11 and bundle | Null withdrawn | Same unsupported null retained as active evidential support |
| Inventory prose 575–589,672–677 / current inventory | 41 figures,29 raw,12 derived | 44 live,32 raw,12 derived; primary band still absent |

## Fatal counterexample and estimand search

The risk is coherent as a probability for a specified finite empirical distribution, positive baseline, independent with-replacement k-tuples, threshold and fixed reference side. The probability measure and estimand matter; that is a scope condition, not a contradiction. A zero-risk deterministic pair is expected. High risk for a stable *wrong-sided* k-run decision is also coherent: this statistic measures disagreement with the chosen reference, not mere run-to-run variation.

The multimodal construction A=100, B=200 with probability .3 and 29 otherwise has theta=-19.7% and risk .216. It refutes a universal distance theorem but not the risk definition. The rare-tail construction A=100, B=100 with probability .99 and 2100 otherwise has population theta=20%, risk .970299, and probability .99^200=.13397967 of an all-low observed panel with a degenerate zero-risk bootstrap. It defeats an unconditional population-coverage claim; v3 now disclaims that claim. It does not invalidate the empirical-panel calculation.

Exact theta=t is unresolved under the mathematical strict reference rule; the observed floating implementation defect is A12. It stays boundary-excluded. Empty/zero-baseline data are outside the ratio estimand and are rejected, rather than a universal positive-baseline theorem being extended to them. Near-zero positive baselines can produce large ratios, but no logical contradiction follows. Ordered integer brute-force tests including ties and discrete supports agree with the independent convolution in all 150 cases.

Ratio of means, mean of per-seed ratios, median per-seed ratio and ratio of medians were compared on all 39 raw pairs. The paired mean difference normalized by the baseline mean is algebraically the ratio-of-means estimand, not an independent alternative. Point-side changes among the tested alternatives occur in dnn_n33 and dnn_n51, already unresolved and boundary-flagged; no eligible point-side reversal was found. Quantile targets can differ by design and should not be silently substituted. The chosen plug-in estimand is now explicitly disclosed; no external objective truth was established or required for the narrowed claim.

The data support this recorded panel, one SDK/version comparison, heavy-hex topology, selected circuits and stated decision rule. They do not establish IID sampling from unseeded compiler behavior, industry prevalence, a suite-wide population rate, a causal compiler mechanism, general backend irrelevance, or a universal 11-pp barrier.

## Coverage of the requested attacks

| Attack | Disposition and evidence |
|---|---|
| 1 raw-to-paper | Independently reconstructed; N01, integer conventions above |
| 2 verifier independence | Full stage trace; genuine raw path but incomplete binding, A01–A03 |
| 3 mutations | A–J plus C2/K executed; separate ledger and logs |
| 4 manifest/platform | 78/78 v2 identity verified; two autocrlf checkouts; J flags CRLF; F defeats identity assurance; external pin still CRLF-sensitive (A14) |
| 5 seed law | All 78 arms exactly match selected order statistics; 6 seeds above midpoint; explicit empirical scope |
| 6 bootstrap | All 36 original intervals replayed; frozen classifications confirmed; new-stream mismatch A01 |
| 7 monotonicity | Main withdrawal valid, both counterexamples verified; residual artifact resurrection A04/A06 |
| 8 mechanism | No causal identification; unsupported abstract attribution A06 |
| 9 version-pair scope | Model depends on measured residuals; main limitation present, stale artifacts A04 |
| 10 ambiguity | Four independently recomputed constructions and mean-change conversion; A05 |
| 11 twenty-run risk | 3.7414736766% for pooled deep+scatter 400-seed heavy-hex bv_n140,1.4.3→2.0.0,k=20,t=.1,WR independent arms; floating PMF convolution, not observed event counts |
| 12 synthetic null | Main/PDF explicitly withdrawn; active SETTLED/bundle fail A04 |
| 13 chronology | Commit table plus full per-path history; A09 |
| 14 selection | Exact selection-rule set equality; corrected and old tests both reproduce |
| 15 issue | Primary external source consulted; three local means recomputed; A07 |
| 16 fixed seed | Repeatability versus correctness distinguished; remaining overclaim A08 |
| 17 backend | Limited 0/24 log traced; missing original factorial record; A08 |
| 18 cross-machine | 216/216 raw counts independently matched; no output-circuit hashes; metadata limitation A10 |
| 19 external source | Exact pinned local Benchpress source/configuration inspected,58 corpus hashes verified; scope A11 and portability A14 |
| 20 PDF | Supplied PDF hash verified, rebuild text equality,all13 pages rendered/inspected; A13 |
| 21 provenance | Five-category audit table and actual nine-stage authority trace; missing coverage A01 |
| 22 corrections | Every F01–F22 mapped above; CLOSED labels not accepted at face value |
| 23 consistency | Cross-section matrix above, including PDF propagation |
| 24 fatal edge cases | Discrete/ties/deterministic/zero/near-zero/multimodal/rare-tail cases; A12 is bounded, no fatal empirical contradiction |
| 25 estimands | All39 alternative point-estimand comparisons; no eligible reversal in tested alternatives |
| 26 generality | Main scope narrows result appropriately; specific residual overclaims and stale production assertions identified |

## Evidence limits

No new quantum compilations were run; the audit concerns recorded measurements, algorithms, evidence and claims. No physical Linux/macOS host was tested: raw checkout invariance was executed under both autocrlf settings on Windows, and the external-source LF mismatch was established byte-for-byte against Git blobs. Independent k=20 and real-valued band calculations use checked floating PMFs; they are numerical evaluations of finite-distribution probabilities, not an arbitrary-precision rational certificate. The raw primary k=3 probabilities use integer counts. Historical backend controls and library versions cannot be recovered from absent metadata. A fresh remote server state was not asserted.

No FATAL finding is established. The empirical counts survive; the remaining MAJOR findings block the proposed publication until corrected and retested.

CORE SURVIVES MAJOR CORRECTIONS
