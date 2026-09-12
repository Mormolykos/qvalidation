"""Assemble review artifacts from completed audit evidence, outside the repository."""
import json,re,hashlib,zipfile
from pathlib import Path
B=Path(__file__).resolve().parent;R=B/'snapshot'
def link(p,line=None):
    return f'[{p}'+(f':{line}' if line else '')+f']({(R/p).as_posix()}'+(f':{line}' if line else '')+')'
def artifact(p):return f'[{p}]({(B/p).as_posix()})'
F=[]
def add(id,severity,title,loc,claim,failure,evidence,repro,correction,endpoint='No change to the pinned primary endpoint.',block=False):
    F.append(dict(id=id,severity=severity,title=title,location=loc,claim=claim,failure=failure,evidence=evidence,reproduction=repro,correction=correction,endpoint=endpoint,publication_blocked=block))
add('A01','MAJOR','Saved bootstrap results can be replaced while all nine stages pass',link('raw_integrity.py',108)+'; '+link('raw_endpoint.py',178)+'; '+link('PAPER.md',637),
    'The summary is required to be reproducible from raw; every published figure has a fresh recomputation.',
    'The consistency check compares status, verdict, theta and a nonempty point-risk field. It does not compare the saved theta intervals, risk intervals, boundary flag, error_excludes_zero, p_call, sample count or full row membership. The new reconstruction also uses a different bootstrap stream: it omits the original inner Monte Carlo RNG consumption. Agreement of three counts cannot certify the saved intervals.',
    'Mutation H replaces every one of the 36 saved risk intervals with [0.900000, 0.999999]. Full verify.py returns 9/9 PASS. Pristine independent MC replay reproduces all 36 original intervals within 0.0000005 rounding error. Thus this is a verifier defect, not evidence that the original intervals were fabricated. New exact-stream intervals differ: bv_n280 [0.1177340704,0.2427296891] versus saved [0.115990,0.236869]; swap_test_n83 [0.0969299492,0.2123290094] versus [0.101924,0.227535].',
    'python mutations.py H --full; python bootstrap_replay.py. See mutH_full.log and bootstrap_replay.json.',
    'Validate every reported interval and classification field against its declared algorithm/stream, and validate exact row membership. Either reproduce the original MC bootstrap or deliberately replace and regenerate its results with an explicitly documented exact bootstrap. Register the actual primary 10.9-pp band as well; the inventory currently checks a different historical band dataset.',
    'Pinned endpoint unchanged. Corrupted interval artifacts falsely imply zero-exclusion even for genuinely zero-risk circuits; the cached flags and headline counts remain unchanged.',True)
add('A02','MAJOR','Invisible correct rows certify a false visible primary table',link('raw_endpoint.py',202)+'; '+link('paper_check.py',52)+'; '+link('PAPER.md',379),
    'The raw-to-paper check is bound to the specific results-table rows.',
    'Both checkers search raw Markdown text and accept the first matching rows. Neither excludes HTML comments nor establishes uniqueness or validates the rendered table. A hidden copy of the correct rows shadows the actual results table.',
    'Mutation K changes all three visible counts to 0 / 26 and prepends the original rows inside an HTML comment. Full verify.py returns 9/9 PASS. Pandoc with the specified markdown+pipe_tables+raw_html reader renders only the false 0 / 26 rows; the correct comment is invisible.',
    'python mutations.py K --full; pandoc mutK/PAPER.md --from=markdown+pipe_tables+raw_html --to=plain --wrap=none. See mutK_full.log and mutK_rendered.txt.',
    'Parse the manuscript structure/rendered document, reject duplicate or ambiguous endpoint tables, ignore comments, and compare every numerator, denominator and proportion in the actual designated table. Add this exact shadow-row mutation.',
    'Raw scientific endpoint stays 12/26,7/26,4/26; the published visible endpoint is changed to 0/26,0/26,0/26 while verification passes.',True)
add('A03','MAJOR','A regenerated manifest does not enforce v2 evidence identity',link('raw_integrity.py',49)+'; '+link('raw_integrity.py',66)+'; '+link('raw_integrity.py',86)+'; '+link('V3_CORRECTION_LEDGER.md',10),
    'Raw evidence remains byte-identical to v2 and raw_integrity.py enforces that going forward.',
    'The verifier hashes current checkout bytes against an equally mutable manifest. It never compares those hashes with the trusted v2 Git objects, nor rejects disagreement with the audited qvalidation HEAD. Numerical summary tolerances allow small changed observations to retain green checks.',
    'Mutation F changes multiplier_n45 candidate seed 663193 from 7315 to 7316 and runs raw_integrity.py --write, without updating the summary. Full verify.py returns 9/9 PASS. Independently computed risk changes from 0.028724114619140626 to 0.028726752145875, and theta from 0.07473276727488987 to 0.0747335005745402. The raw bytes no longer match v2.',
    'python mutations.py F; run verify.py in mutF with BENCHPRESS_PATH set. See mutF_full.log, edge_cases.json and metadata_checks.json.',
    'For the claimed immutable-v2 contract, verify against the externally trusted v2 commit/blob identities and compare the current worktree with that evidence. Alternatively narrow the assurance to manifest self-consistency and require an independently authenticated manifest for publication.',
    'Individual measured science changes; coarse primary counts do not.',True)
add('A04','MAJOR','Withdrawn evidence remains active in the staged archive',link('SETTLED.json',86)+'; '+link('bundle/PAPER.md',21)+'; '+link('bundle/PAPER.md',238)+'; '+link('followup3.py',100),
    'All 22 corrections are closed; the synthetic null and universal interpretation have been withdrawn.',
    'SETTLED S11 still endorses the ungenerated null (mean -0.661; 5 of 30 trials), describing a different mechanism claim as withdrawn. bundle/PAPER.md still asserts universal monotonicity, version-pair independence, categorical unresolvability, bit identity, independent seeds and the old issue comparison. Its draft date identifies age but does not mark these assertions as invalid or withdrawn. followup3.py still prints version-pair-free/true-change rhetoric.',
    'The user-supplied staged ZIP includes both manuscript versions. All 1,034 tracked files in that ZIP exactly match target Git archive content, so this is present in the proposed release, not debris outside the target. The root manuscript/PDF explicitly withdraw the synthetic-null numbers; this finding concerns the other still-authoritative artifacts.',
    'Read the cited files; run pdf_audit.py to confirm archive membership and byte identity. Inspect SETTLED S11 result and bundle/PAPER.md abstract and section 4.1.',
    'Mark historical artifacts prominently as superseded and their invalid assertions as withdrawn, or exclude obsolete reader-facing bundle copies from the release. Update active SETTLED claims and generated narrative. Do not erase the historical audit record.',block=True)
add('A05','MAJOR','Categorical unresolvability and true-change language survive their correction',link('PAPER.md',401)+'; '+link('PAPER.md',430)+'; staged PDF p.8',
    'A true change anywhere in an 11-point-wide window is unresolvable by a three-run comparison; the band contains no theta.',
    'A 5%-95% call-probability transition is not an impossibility theorem. Near an endpoint, one outcome has about 95% probability. The swept multiplier also differs from ratio-of-means change by C=(mean(B)/mean(A))/mean(B/A). The immediately preceding correction discloses this but the unchanged interpretation again calls the whole axis true change and unresolvable.',
    'Independent residual calculations give median parameter width 10.8685952 pp, median transformed mean-change width 10.8521192 pp. For cc_n64, C≈0.99103669 transforms 25.13409 to 24.90880 pp. These support the approximate scale, not the categorical sentence. The staged PDF carries the same sentence.',
    'python supplementary.py; inspect supplementary.json bands and PDF page 8.',
    'Replace the remaining categorical sentence with the operational transition definition and label the sweep parameter consistently. State width, population of 23 resolved stochastic circuits, version pair, residual model, k and threshold together.',block=True)
add('A06','MAJOR','The abstract retains an unsupported quantitative attribution',link('PAPER.md',27)+'; '+link('PAPER.md',362)+'; staged PDF pp.1,7',
    'The risk-distance association is largely induced by the decision rule itself.',
    'Largely asserts how much of the measured association is induced. The universal theorem is false; the synthetic null is withdrawn; the body explicitly says no quantitative claim about the induced amount is made. Neither a descriptive correlation nor a fixed-shape location argument establishes this abstract claim.',
    'Raw Spearman correlation reproduces -0.8329214039. Internal counterexample: bv_n280 distance 5.1102 pp/risk 17.3147% versus adder_n118 distance 3.5301 pp/risk 12.6743%. External construction gives distance 1 pp/risk zero versus distance 29.7 pp/risk 21.6%. These refute universality but do not quantify the origin of the empirical correlation.',
    'python independent.py snapshot independent.json; python supplementary.py; compare abstract with section 4.1.',
    'Describe the measured association without attributing a predominant induced component, unless a reproducible, explicitly scoped model establishes that attribution.',block=True)
add('A07','MAJOR','The issue comparison still asserts an unavailable protocol and a wrong value',link('PAPER.md',39)+'; '+link('PAPER.md',138)+'; '+link('PAPER.md',485)+'; staged PDF pp.1,3,9',
    'knn_341 rose about 41%; the support describes the distribution the issue’s own protocol produces.',
    'The corrected table reports +44.060%, but section 2.2 retains +41%. The abstract and section 4.4 retain own-protocol language despite admitting that the historical aggregation/configuration is unavailable. A numerical comparison under this study’s linear 12-seed ratio-of-means design is not a reconstruction of the issue protocol.',
    'The primary issue reports knn_341 0.4406005221932115, bv_n280 0.4424514200298953, bv_n140 0.4614152373646045. Independent local means give 43.4259711%,44.5332002%,35.2065187%, respectively. The corrected table differences are right. Mutation I changes +44.060% to +94.060%; stages 6,7,8 all pass, showing this external value is not actually checked there.',
    'python supplementary.py; compare [Qiskit issue #14402](https://github.com/Qiskit/qiskit/issues/14402) with the cited source locations; python mutations.py I.',
    'Correct the remaining +41% and replace both own-protocol assertions with explicit model/configuration-specific comparisons. Preserve the admitted historical unknowns.',block=True)
add('A08','MAJOR','Determinism is asserted more broadly than the controls establish',link('PAPER.md',149)+'; '+link('PAPER.md',265)+'; '+link('PAPER.md',276)+'; '+link('PAPER.md',515)+'; '+link('DEFECTS.md',238),
    'Gate counts are deterministic functions of seed; one seed_transpiler argument removes sampling variance at k=1.',
    'The backend is generated with unseeded error rates. The 0/24 evidence is a limited research-log control without the original factorial generator/trial artifact, not proof that all other randomness is absent. The conclusion correctly narrows repeatability to this source, but the methods and fixed-seed sensitivity sentence remain unconditional. DEFECTS calls the confound dead/not a confound.',
    'The pinned FlexibleBackend forwards no backend seed. The log describes 6 circuits×4 seeds×4 distinct backend draws and zero observed count changes. The separate exp1 script is a different experiment, not the missing original factorial replay. All 216 recorded cross-machine gate counts do match. bv_n280 fixed seed 663193 yields 1040→1157 (+11.25%) although its empirical mean change is +4.89%.',
    'Read the pinned backend constructor, RESEARCH_LANDSCAPE.md:1568 onward and the cited claims; supplementary.py checks cross-machine counts; independent.py reads fixed-seed observations.',
    'State repeatability observed in the measured controls and removal of variation attributable to changing seed_transpiler. Describe the 0/24 result as a limited logged control, preserve other randomness as an explicit uncertainty, and remove universal determinism implications.',block=True)
add('A09','MINOR','Local commit order is again described as first-access evidence',link('PAPER.md',190)+'; '+link('PAPER.md',298)+'; '+link('PAPER.md',452)+'; '+link('prereg_analysis.py',3),
    'The analysis predates the existence of the data; the follow-up was blind; the second-machine document predates the machine’s existence.',
    'Git records committed chronology, not when data were first produced or inspected. The body correctly states this limit, but other sentences and the analysis header still infer that tuning was impossible. There is no evidence here of fabrication or tuning; the stronger inference simply does not follow.',
    'Local preregistration a36a34a 2026-09-03 23:51:08+03; analysis/list fbc573d 23:52:38; primary raw commit 30224a0 2026-09-04 09:13:07. Earlier census/exploration already existed. Later controls have separately later commits.',
    'python integrity_history.py; inspect integrity_history.json history and the cited sentences.',
    'Use before the primary raw-data commit / before the laptop-data commit and identify blindness/non-access as an author process assertion unless independently documented.')
add('A10','MINOR','Matching rustworkx versions/builds are not established by the measurement artifacts',link('PAPER.md',313)+'; '+link('PAPER.md',549)+'; crossmachine/*_{q143,q200,q202}.jsonl environment records',
    'Both machines ran rustworkx 0.18.1 / the same rustworkx build.',
    'The compared measurement records omit rustworkx metadata. Current software state or a later recorder change cannot establish the versions in the historical runs. Equal version numbers would also not alone establish identical builds.',
    'All six per-machine/per-version records were inspected; supplementary.json preserves their environment records. Gate counts and platform metadata are present, rustworkx version/build metadata is absent.',
    'python supplementary.py; inspect crossmachine environment records and manuscript sentences.',
    'Label the graph-library version as a retrospective author assertion with its actual provenance, or supply contemporaneous environment/build evidence. Keep the supported 216-count match.')
add('A11','MINOR','The no-aggregation scope remains inconsistent',link('PAPER.md',76)+'; '+link('PAPER.md',120)+'; '+link('PAPER.md',105),
    'The suite performs no aggregation over runs; the Qiskit-based gyms use the same preset-pass-manager path.',
    'The correction is about returned gate-count aggregation, while the introductory sentence still generalizes to all aggregation. Benchmark repetition/timing summaries are distinct. The transpiler-service gym also has a TranspilerService path rather than that exact preset-pass-manager call.',
    'The pinned QASMBench path creates its pass manager with optimization level/backend, runs it through the benchmark fixture and records count_ops on the returned circuit. The service gym has a different call flow. Explicit BQSKit seed=0 is verified for the cited sibling examples, not every BQSKit benchmark.',
    'Inspect the pinned benchpress/qiskit_gym/abstract_transpile/test_qasmbench.py, qiskit_gym/utils/io.py and qiskit_transpiler_service_gym/abstract_transpile/test_qasmbench.py.',
    'Restrict each source claim to the inspected local Qiskit compilation path and absence of repeated-run gate-count aggregation; avoid statements about every gym or timing aggregation.')
add('A12','MINOR','Exact threshold ties are mishandled by the floating reference classification',link('prereg_analysis.py',133)+'; '+link('raw_endpoint.py',143)+'; '+link('raw_endpoint.py',91),
    'An interval exactly at the threshold is unresolved; the new risk path uses exact integer convolution.',
    'The reference bootstrap compares floating ratios with 0.1. For constant A=100 and B=110, the exact reference is 1/10 but floating B/A-1 is 0.10000000000000009, so the strict rule labels REGRESSION instead of UNRESOLVED. Separately, raw_endpoint convolves float probabilities, not integer counts, although its decision inequality is evaluated with integer cutoffs.',
    'edge_cases.json records exact Fraction(1,10), the floating value and the differing classifications. The case remains boundary-excluded, so it cannot change this paper’s eligible endpoint. Independent integer convolution agrees with 150 ordered brute-force cases exactly; no such primary-data divergence was found.',
    'python edge_cases.py; inspect the reference comparison and raw_endpoint.ksum_pmf dtype.',
    'Handle equality in the reference classifier using exact sums/rational comparisons or a justified tie policy; add exact-cut tests. Describe float PMF convolution accurately or use integer-count convolution for k=3.')
add('A13','MINOR','The staged PDF needs an unarchived build input',link('PAPER.md',669)+'; staged publication archive',
    'The artifact is independently reproducible from the archived code/data.',
    'The PDF itself can reasonably be a publication-time build artifact, but paper_style.css and the complete build recipe/toolchain are absent from the archive. Rebuilding therefore requires a file supplied separately by the author.',
    'The user supplied C:/Users/User/Desktop/bad/paper_style.css. With that input, pandoc plus headless Chromium Edge produced 13 pages whose whitespace-normalized extracted text exactly matches the staged PDF. PDF hashes differ, as expected for browser/metadata-dependent builds; no content divergence was found. All three staged-file hashes match the user’s values.',
    'Run pdf_audit.py and the commands in REPRODUCTION.md; see pdf_audit.json and pdf_contact_sheet.png.',
    'Archive the stylesheet and an executable PDF-build command with tool versions. Define content/layout reproducibility separately from byte-identical PDF reproduction.')
add('A14','MAJOR','The toolchain hash pin still depends on CRLF checkout bytes',link('sweep_bp.py',70)+'; '+link('verify.py',91)+'; '+link('results/raw/benchpress_pin.json'),
    'A replicator can verify the pinned Benchpress revision with the integrity command.',
    'All five recorded Benchpress module hashes identify CRLF checkout bytes, not the pinned Git blob bytes. A normal LF checkout at the identical clean commit produces five mismatches. The new qvalidation raw-data -text attribute cannot change checkout behavior in the separate Benchpress repository.',
    'metadata_checks.json records all five recorded/checkout/Git/LF hashes. In every case CRLF→LF conversion exactly equals the pinned Git blob and fails the recorded hash comparison. This is an executable hash comparison, not a claim that a Linux host was run. The primary-data manifest itself passes both autocrlf settings.',
    'python metadata_checks.py; compare module_canonicalization entries. verify.py stage 1 explicitly rejects any of these five mismatches.',
    'Use canonical Git blob hashes for the external pin and separately check worktree semantic/canonical content, or specify and enforce an explicit portable source-byte policy. Do not silently rewrite raw historical metadata; version the corrected pin contract.',block=True)

for id,title,claim,evidence,repro in [
 ('N01','Primary empirical chain survives','36 resolved, 3 unresolved, 10 resolved-boundary exclusions, 26 eligible; 12/26,7/26,4/26','Independent raw-only integer-count convolution and paired bootstrap reproduce the classifications, point risks, all 39 theta intervals and all 36 original risk intervals. There are 13 boundary flags overall because all 3 unresolved circuits are also boundary-flagged.','independent.py; bootstrap_replay.py'),
 ('N02','Raw measurement identity survives','No primary measurements changed from v2','All 78 worktree hashes equal target blobs, v2 blobs and manifest entries. No results/raw JSONL changed between the two commits. Both disposable autocrlf settings produce 78/78 identical primary raw files.','integrity_history.py'),
 ('N03','Conditional bootstrap scope and chosen estimand survive','The intervals concern a frozen empirical-panel classification, without established population coverage','The manuscript now explicitly freezes verdict/boundary/eligibility and disclaims population coverage. The rare-tail counterexample remains a limitation, not a contradiction of that narrowed claim. Two alternative-estimand point-side disagreements occur only in already-unresolved dnn_n33 and dnn_n51.','independent.py; edge_cases.py; supplementary.py'),
 ('N04','Corrected auxiliary numerical results survive','Approximately 10.9-pp model width; 3.7415% twenty-run risk; corrected selection comparison','Independent results: median unrounded multiplicative width 10.8685952 pp; truncated 10.8658241; additive 10.6794749/10.7331406. Pooled 400-seed bv_n140 heavy-hex k=20 risk 3.7414736766%; corrected selection 39/13, medians 0.1114670083/0.1260321599, p=0.4559911843. Fits 23 additive/3 multiplicative/13 ties.','supplementary.py'),
 ('N05','Pinned source and gate-count replication survive within their stated measurements','The inspected Qiskit path omits seed_transpiler; 216 cross-machine gate counts match','Pinned revision b695f30e83a32bac05b9b4d8e98d37ba9aae5236 and parameter flow inspected; 58 circuit hashes and 5 current-checkout module hashes match. All 72 counts for each of three versions match across the two machine files. This does not establish full-circuit identity or universal repeatability.','metadata_checks.py; supplementary.py; cited external source files'),
 ('N06','Staged PDF content and archive identity survive','The proposed PDF is built from the target manuscript','Staged PDF hash 687b57d7f34f9bad477a2352235f18245823570b7d9b9127baddb7bb070402f6 matches; rebuilt text matches after whitespace normalization; all 13 pages rendered and inspected via contact sheet plus detailed result pages. The ZIP has no differences from 1,034 target tracked files.','pdf_audit.py')]:
    add(id,'NOT ISSUE',title,link('PAPER.md'),claim,'The attempted invalidation did not establish a defect in this narrowed claim.',evidence,repro,'No correction to this supported result. Retain the stated scope and limitations.')

header=f'''# ASTRA final hostile audit — qvalidation v3

Target: **839ac80cd36ac44c7bab12e3b5a19c9dceb95c76**. Audit dates: 2026-09-12–13.

**Publication should be blocked on the assurance and claim-consistency defects below. No fatal invalidation of the pinned empirical endpoint was found.**

The strongest new chain is executable: the visible primary table can say **0/26, 0/26, 0/26** while all nine verifier stages pass, because correct rows hidden in an HTML comment are treated as the manuscript. Independently, every saved risk interval can be corrupted while 9/9 passes, and one changed raw observation plus a regenerated manifest passes all nine stages. These are distinct failures; they do not show that the unmodified measurements or original intervals are wrong.

The original repository was not edited, committed, tagged or published. Work used a separate clone detached at the exact target; mutations used disposable sibling clones. Original HEAD and tracked cleanliness were checked again at completion. Initial HEAD/origin-master equality was a local tracking-ref check, not a fresh remote-server verification. No scientific compiler runs were repeated. No unrelated SDK development was inspected. The only external SDK source inspected was the pinned Benchpress flow required by the task.

The fresh ledger was written before reading the prior hostile review or correction ledger. Its original creation-time assessments remain in {artifact('FRESH_CLAIM_LEDGER.md')}; final resolutions are appended there. The supplied final PDF and staged ZIP were inspected only after the user identified them. The stylesheet was used as an external input, without changing the repository.

## Independent numerical reconstruction

The primary implementation in {artifact('independent.py')} imports no project analysis code. It reads the 78 primary JSONL files, sorts and validates paired seed identities, computes arm means, and convolves **integer count histograms** for ordered with-replacement triples. The call event is **10·Sb ≥ 11·Sa**; the denominator is 200⁶ = 64,000,000,000,000. Baselines are positive. The selected panel is exactly the smallest 200 unique values from 400 candidate draws with RNG 20260904; all 78 arm files match that panel and have ten recorded process IDs.

Theta is mean(B)/mean(A)−1. Its interval uses 4,000 joint paired-index resamples with RNG 20260904 and NumPy linear-interpolated 2.5/97.5 percentiles. Strict above/below defines REGRESSION/NO_REGRESSION; otherwise UNRESOLVED. Boundary means absolute theta-to-0.1 distance ≤3 percentage points. Reference classification is frozen during the risk bootstrap. The original risk bootstrap uses RNG 20260905, 400 paired outer resamples, and independent arm draws for 400,000 inner mean-of-three trials. {artifact('bootstrap_replay.py')} replays that complete original stream; constant zero-risk rows are handled analytically. This is distinct from the verifier’s new exact-inner stream.

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

{artifact('MUTATION_TEST_LEDGER.md')} records the full A–J set plus C2 and K. Full nine-stage runs were completed for the pristine target, H, K and F. Other cases ran the directly affected stages 6,7,8; a nonzero stage is sufficient to defeat the full conjunction, but these are not misrepresented as complete nine-stage executions. The pristine stage-9 execution also reproduced the supplied five-case suite.

## Findings

'''
body=''
for f in F:
    body+=f"### {f['id']} — {f['severity']} — {f['title']}\n\n"
    for label,key in [('Location','location'),('Exact claim under attack','claim'),('Why it fails / why the attack fails','failure'),('Independent evidence','evidence'),('Reproduction','reproduction'),('Smallest valid correction','correction'),('Primary endpoint impact','endpoint')]:body+=f"**{label}:** {f[key]}\n\n"
    body+=f"**Publication blocked by this finding:** {'Yes' if f['publication_blocked'] else 'No'}.\n\n"

tail='''## Chronology and correction closure

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
'''
(B/'ASTRA_FINAL_HOSTILE_AUDIT.md').write_text(header+body+tail,encoding='utf-8')
(B/'findings.json').write_text(json.dumps(F,indent=2),encoding='utf-8')

mutation_rows=[
 ('A','One knn_n67 candidate observation 619→10,000,000','Yes: unresolved;11/25,6/25,3/25','Yes','7 FAIL;8 FAIL;6 PASS','Correct: raw classifications/counts and hash disagree'),
 ('B','One knn_n67 candidate observation 619→620','Yes: small individual risk/theta change;headline unchanged','Yes','7 PASS;8 FAIL;6 PASS','Correct: integrity rejects bytes/summary drift'),
 ('C','Supplied-style candidate arm×1.09 rounded','Yes: verdict/risk change;eligibility unchanged','Yes','7 FAIL;8 FAIL;6 PASS','Caught, but the supplied label claiming eligibility movement is inaccurate'),
 ('C2','One candidate observation 619→3619','Yes: becomes boundary/unresolved;eligible25','Yes','7 FAIL;8 FAIL;6 PASS','Correct: actual boundary/eligibility-changing case'),
 ('D','First saved summary point risk→.999999','Published derived science changes;raw unchanged','No','7 PASS;8 FAIL;6 PASS','Correct: summary point-risk mismatch'),
 ('E','Visible ≥5% count7→9 only','Published claim changes;raw unchanged','No','7 FAIL;8 PASS;6 PASS','Correct: new science stage catches this simple literal edit'),
 ('F','multiplier_n45 candidate7315→7316;regenerate manifest','Yes:exact risk .028724114619→.028726752146;headline unchanged','Yes relative to v2;new manifest self-consistent','FULL 9/9 PASS','Missed immutable-evidence violation;A03'),
 ('G','knn_n67 candidate619→620;regenerate its row with prereg_analysis.analyse and manifest','Yes:individual risk/theta/intervals;headline unchanged','Yes relative to v2','7 PASS;8 PASS;6 FAIL','Correct detection at printed risk rounding16.71 versus16.70'),
 ('H','All36 saved risk intervals→[.900000,.999999],flags/counts unchanged','Published uncertainty changes;raw unchanged','No','FULL 9/9 PASS','Missed interval inconsistency;A01'),
 ('I','Issue knn_341 value+44.060%→+94.060%','Published external numeric claim changes','No','7 PASS;8 PASS;6 PASS','Uncovered claim;no full9-stage claim for this case'),
 ('J','One raw file LF→CRLF;semantic records identical','No','Yes:representation changes','7 PASS;8 FAIL;6 PASS','Correct under byte-preservation contract;not a scientific discrepancy'),
 ('K','Visible headline fractions→0/26;correct rows in invisible HTML comment','Published primary claim changes;raw unchanged','No','FULL 9/9 PASS','Missed visible-table corruption;A02'),
]
ml='''# Mutation-test ledger

Target 839ac80cd36ac44c7bab12e3b5a19c9dceb95c76. All mutations are in disposable sibling clones. Source checker code is unchanged except the deliberately mutated data/document. A full-pass result means the actual unmodified verify.py completed all nine stages with exit success. Individual-stage results mean those exact stage programs ran, not a simulated nine-stage result. The full baseline also passes the supplied A–E self-test using git-archive snapshots.

“Science changed” distinguishes actual raw empirical changes from false published claims or uncertainty artifacts. Updating a local manifest never restores identity with the trusted v2 raw bytes.

| ID | Mutation | Scientific impact | Raw integrity impact | Observed result | Reason |
|---|---|---|---|---|---|
'''
ml+='\n'.join('| '+' | '.join(r)+' |' for r in mutation_rows)
ml+='\n\nThe supplied whole-arm constant-100 attack is additionally executed by baseline stage9 and caught; it yields11/26,6/26,3/26. Our single-observation A yields11/25,6/25,3/25, because the circuit becomes unresolved. C2 supplements the supplied C because ×1.09 changes reference side, not boundary/eligibility.\n\n'
ml+='Reproduction: '+artifact('mutations.py')+'; '+artifact('REPRODUCTION.md')+'. Per-case exact changes, return codes and durations are in mut*_result.json, with complete stage output in mut*_*.log. Full verifier logs: baseline.log,mutH_full.log,mutK_full.log,mutF_full.log. Mutation K’s rendered false rows are in mutK_rendered.txt.\n'
(B/'MUTATION_TEST_LEDGER.md').write_text(ml,encoding='utf-8')

commands=f'''# Exact reproduction commands

All original/audited-source files are read-only inputs. Output is confined to this audit directory and disposable copies. Interpreter: Python3.10.10,NumPy2.2.6,SciPy1.15.3. PDF tooling was installed only into this audit directory’s pdfdeps. The pinned snapshot was created with git clone --no-hardlinks --no-checkout, then a detached checkout of the full target hash.

```powershell
$audit = '{B}'
$py = 'C:\\Users\\User\\Desktop\\research\\qvalidation\\envs\\bp202\\Scripts\\python.exe'
$env:BENCHPRESS_PATH = 'C:\\Users\\User\\Desktop\\benchpress_test'
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
Set-Location $audit
& $py independent.py snapshot independent.json
& $py bootstrap_replay.py
& $py supplementary.py
& $py integrity_history.py
& $py metadata_checks.py
& $py final_numeric_checks.py
```

integrity_history.py creates autocrlf_true and autocrlf_false disposable clones. Run in a fresh audit directory when reproducing, as scripts refuse to overwrite existing mutation copies. independent.py checks saved summaries **only after** constructing all raw-derived rows. Its counts.boundary field is the all-circuit flag count13; resolved boundary exclusions are10. The original bootstrap stream is replayed separately, not substituted by the exact-inner stream.

```powershell
Set-Location "$audit\\snapshot"
& $py verify.py
Set-Location $audit
& $py mutations.py A
& $py mutations.py B
& $py mutations.py C
& $py mutations.py C2
& $py mutations.py D
& $py mutations.py E
& $py mutations.py F
& $py mutations.py G
& $py mutations.py H --full
& $py mutations.py I
& $py mutations.py J
& $py mutations.py K --full
& $py edge_cases.py
Set-Location "$audit\\mutF"
& $py verify.py
Set-Location $audit
pandoc mutK/PAPER.md --from=markdown+pipe_tables+raw_html --to=plain --wrap=none --output=mutK_rendered.txt
```

Mutation G calls the actual prereg_analysis.analyse function for the changed circuit and rewrites that row using its returned values; all other rows are untouched. No tests are disabled. Stage9 deliberately archives HEAD, so its own test snapshots remain pristine regardless of current worktree mutation. This is documented behavior, not an audit workaround.

PDF commands used (the stylesheet is an external author-supplied input absent from the target):

```powershell
pandoc snapshot/PAPER.md --from=markdown+pipe_tables+raw_html --to=html5 --standalone --css='C:/Users/User/Desktop/bad/paper_style.css' --output=rebuilt.html
pandoc snapshot/PAPER.md --from=markdown+pipe_tables+raw_html --to=plain --wrap=none --output=manuscript_plain.txt
```

Headless Microsoft Edge (Chromium) was launched with a separate scratch user-data directory and arguments --headless=new --disable-gpu --no-pdf-header-footer --virtual-time-budget=15000 --print-to-pdf=<audit>/rebuilt.pdf file:///<audit>/rebuilt.html. The process was launched with WindowStyle Hidden. The supplied original PDF was not overwritten. PyMuPDF renders/compares the results in pdf_audit.py. Its extracted-character count differs by extractor from the user’s quoted count; whitespace-normalized staged/rebuilt text is identical.

```powershell
& 'C:\\Users\\User\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' pdf_audit.py
```

PDF/ZIP paths and hashes are captured in pdf_audit.json. All1,034 archived tracked files were compared with a fresh git archive HEAD, not with the mutable original working tree. The new external toolchain portability check is in metadata_checks.py: each source Git blob equals the CRLF checkout converted to LF, and all five LF hashes fail the recorded comparison.

Read ASTRA_FINAL_HOSTILE_AUDIT.md for exact claim locations, caveats and conclusions. Findings and results are also available as JSON. The report can be regenerated using build_report.py; this writes review artifacts only.
'''
(B/'REPRODUCTION.md').write_text(commands,encoding='utf-8')

fresh=(B/'FRESH_CLAIM_LEDGER.md').read_text(encoding='utf-8')
if '\n## Final resolution' not in fresh:
    fresh+='''
## Final resolution (initial ledger above preserved)

| Initial proposition group | Resolution |
|---|---|
| Pinned source/aggregation | Inspected local Qiskit path supported; broad aggregation/service-gym phrasing A11; CRLF pin A14 |
| Panel/sample/seed law | All78 panels,200 seeds each,10 process IDs each match;39 circuits;15,600 records; N01/N03 |
| Induced association | rho reproduces, predominant attribution unsupported; A06 |
| Ambiguity | Numerical scale reproduces; categorical and axis interpretation A05 |
| Issue comparison | Corrected local means/source table reproduce; surviving+41%/own-protocol claims A07 |
| Verifier/manifest | Baseline9/9; full false passes H,K,F; A01–A03,A14 |
| Estimand/determinism | Chosen plug-in estimand disclosed; determinism overclaim A08; tie defect A12 |
| Integer rule/replacement | Positive-baseline integer event verified independently,150 brute-force cases;WR is the declared law |
| Chronology | Local order supported; first-access inference not established,A09 |
| Bootstrap | All36 original intervals replay; frozen conditional scope valid; verifier new-stream mismatch A01 |
| Backend/seed independence | Seed law explicit;0/24 is logged limited control,not a universal proof,A08 |
| Cross-machine | 216/216 counts match;rustworkx build metadata absent,A10 |
| Selection | Exact rule/grouping and p=.455991 reproduce |
| Primary | All counts survive with10 resolved-boundary exclusions,N01 |
| Monotonicity/null withdrawal | Main withdrawals explicit; SETTLED/bundle still endorse old claims,A04/A06 |
| Family/dependence | Descriptive scope and family caveat retained;no suite-population rate licensed |
| Bands |23additive/3multiplicative/13ties and four constructions reproduce,N04/A05 |
| cc_n32 | Exact239417152405/64000000000000;theta interval matches,N01 |
| bv_n140/issue | Pooled k-sweep supported;historical protocol unknown,A07 |
| Sensitivity | Wrong threshold endpoint withdrawn;20-run3.74147%reproduces;80compute-hours arithmetic corrected |
| Fixed seed | Repeatability does not guarantee mean-reference agreement;residual overclaim A08 |
| Inventory/audit apparatus |44live rows32raw/12derived,not41/29/12;field/claim coverage incomplete,A01/A02 |

The detailed evidence, all22 prior-finding closure assessments, all26 requested attack dispositions and per-finding publication implications are in ASTRA_FINAL_HOSTILE_AUDIT.md.
'''
    (B/'FRESH_CLAIM_LEDGER.md').write_text(fresh,encoding='utf-8')

print('Report written:',len((header+body+tail).split()),'words;',len(F),'findings')
