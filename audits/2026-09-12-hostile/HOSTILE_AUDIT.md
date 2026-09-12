# Hostile audit of published v2

Audited commit: **17e08f3e92533ff8266b1b586e35f20da2923da8**.
Git tree: **033a31d04da404306805e69c7af1f36ff8820468**, 1,025 tracked entries.

The original repository was clean at the beginning and end. Its HEAD was already the requested commit. All computations and mutations used a separate git-archive extraction under `C:/Users/User/AppData/Local/Temp/qvalidation-hostile-17e08f3-g5cxxbw6` or separate temporary mutant copies. No repository files, commits, branches, or publications were changed. No later SDK experiments were used.

The claim ledger was created in session memory before reading SETTLED.json or previous reviews and subsequently exported, unchanged, to [CLAIM_LEDGER.md](C:/Users/User/AppData/Local/Temp/qvalidation-hostile-17e08f3-g5cxxbw6/CLAIM_LEDGER.md). “Pending” in that initial ledger records its creation-time evidence state. The findings and reproduction results below are the final evidence assessment.

## Independent reconstruction

The reconstruction used histograms of integer gate counts and polynomial convolution to count k-draw sums, rather than the repository's materialized-triple estimator. Rounded convolution coefficients were checked for non-negativity and the exact total number of combinations. The integer threshold was applied to sum values, retaining equality as a regression. The independent estimator also agreed with exact brute-force enumeration and the repository estimator in 900 independently generated small cases.

| Quantity | Independent result |
|---|---:|
| Selected circuits / raw arm files / run records | 39 / 78 / 15,600 |
| Runs per arm; seed alignment | 200; all 78 files use the same 200 distinct seed IDs |
| Recorded processes per circuit per arm | 10 |
| Resolved / unresolved | 36 / 3 |
| Resolved boundary exclusions | 10 |
| Eligible / both arms constant | 26 / 13 |
| Primary: risk interval excludes zero | **12/26** |
| Point risk at least 5% / at least 10% | **7/26 / 4/26** |
| Eligible risk median / p75 / p90 / maximum | 0 / 6.90530% / 14.17000% / 17.31471% |
| Stochastic resolved distance–risk Spearman correlation | −0.8329214039, n=23 |
| Largest with-/without-replacement risk difference | 0.0010648980, or 0.10649 percentage points |
| Family bootstrap interval, original sorted-family sampling scheme | [17.3913%, 80.9524%] |
| Cross-machine gate-count matches | 216/216 |

All reference changes, theta intervals, verdicts, exclusions and point risks matched the committed summary to its rounding. Replaying the original risk-bootstrap random stream independently reproduced **all 36 reported risk intervals** within 0.0000005 rounding error. Replacing the inner Monte Carlo calculation by an exact histogram calculation on those identical bootstrap samples moved interval endpoints by at most **0.0011574 in probability** and did not change the primary endpoint.

The empirical k-sweep was also reconstructed by probability convolution, without reading the reported sweep as input:

| k | Empirical risk |
|---:|---:|
| 1 | 34.579375% |
| 3 | 24.383936% |
| 5 | 18.564909% |
| 8 | 12.945475% |
| 10 | 10.357691% |
| 20 | 3.741474% |

This supports the reported scale and the 3.74% endpoint. It does not establish a universal rate of convergence as k increases.

## Reproduction commands and evidence keys

Run the following in the **scratch extraction**, not the user's repository. The interpreter used was `C:/Users/User/Desktop/research/qvalidation/envs/bp202/Scripts/python.exe`, with NumPy 2.2.6 and SciPy 1.15.3.

- **T1:** `python independent_audit.py` — reconstruct all primary classifications, exact point risks, independent exact bootstrap intervals, replacement sensitivity and endpoint; outputs `independent_results.json`.
- **T2:** `python bootstrap_replay.py` — replay all 36 original risk-bootstrap streams, independently calculate both exact and Monte Carlo intervals; outputs `bootstrap_replay.json`.
- **T3:** `python band_floor_audit.py` — deterministic 45-step bisection, multiplicative/additive, both real-valued and integer-truncated candidates; outputs `band_floor.log` and `band_results.json`.
- **T4:** `python additional_checks.py` — seed-generation reconstruction, selection rule, selection-bias groups, model fits, issue comparison, cross-machine counts, mathematical counterexamples and k-sweep; outputs `additional_checks.log`.
- **T5:** `python threshold_audit.py` — repeat the theta-interval / boundary / risk-interval definition at all six thresholds, with exact inner risk calculations; outputs `threshold_results.json`.
- **T6:** `python verify.py` with `BENCHPRESS_PATH=C:/Users/User/Desktop/benchpress_test`, `PYTHONUTF8=1` and `PYTHONDONTWRITEBYTECODE=1`. Pristine result: **6/6 PASS**, recorded in `verifier_baseline.log`.
- **T7:** In a separate snapshot copy, replace every candidate `two_q` in `results/raw/prereg/knn_n67_heavy-hex_q200.jsonl` with 100, keeping all other fields and all derived files intact; run T6. The tested mutant is `C:/Users/User/AppData/Local/Temp/qvalidation-mutant-1vhh6ui7/snapshot`; result: **6/6 PASS**, in `verifier_mutant_strong.log`.
- **T8:** Copy `ksweep_linear.csv` to a separate temporary location, increase its first `unpaired_median_band_pp` by 40, and redirect only `inventory.summary('ksweep_linear.csv')` to that copy. `inventory.main()` with `--check` exits 1: **40/41**, specifically rejecting `s43.k1.linear: 4.483 → 44.483`. Evidence: `C:/Users/User/AppData/Local/Temp/qvalidation-derived-mutant-39d9reo4/result.txt`.
- **T9:** Read history with `git log 17e08f3 --reverse --format=fuller -- <path>` and compare `git diff fbc573d 17e08f3 -- PREREGISTRATION.md _selected.txt prereg_analysis.py`. These are read-only operations.
- **T10:** Inspect Benchpress using `git -C C:/Users/User/Desktop/benchpress_test show b695f30e:<path>`. The checkout is exactly `b695f30e83a32bac05b9b4d8e98d37ba9aae5236`. All 58 recorded input-circuit hashes matched the available checkout.
- **T11:** Independently read [Qiskit issue #14402](https://github.com/Qiskit/qiskit/issues/14402) and [pytest-benchmark's documented options](https://pytest-benchmark.readthedocs.io/en/latest/usage.html).

## Findings

All manuscript locations below refer to **PAPER.md at the audited commit**, not an unspecified current copy. Severity applies to the precise claim identified, not automatically to the entire experiment.

| ID | Severity | Exact claim | File:line | Attack performed | Independent evidence | Reproduction command/test | Verdict | Minimal correction or required experiment |
|---|---|---|---|---|---|---|---|---|
| F01 | **MAJOR** | “A single command re-checks the whole paper”; “A stale or altered source fails the check” | PAPER.md:470–476; paper_check.py:101–105,150–153; verify.py:72–90 | Corrupt a complete primary candidate arm while leaving the published summaries unchanged | T7 still passes all six stages. The corrupted circuit's actual theta becomes −82.7123% and exact risk becomes 0, which changes the genuine endpoint to 11/26 and the ≥5% / ≥10% counts to 6/26 and 3/26. The verifier still certifies the old numbers. | T6–T7 | **Confirmed.** Primary results are read from the derived prereg CSV; the inventory's 41 entries chiefly concern earlier research-log results, not a fresh primary-endpoint calculation. | Regenerate the primary classifications, intervals and endpoints from raw data in verification; bind manuscript numbers to their actual claims; add the demonstrated mutation regression. |
| F02 | **MAJOR** | “200 independent transpiler seeds”; seeds drawn across the stated wide range | PAPER.md:22,203–205; scatter.py:99 | Reconstruct the seed-selection algorithm exactly | It draws 400 integers, deduplicates, sorts, and keeps the smallest 200. The retained IDs match the raw data exactly. Only 6/200 lie in the upper half of the nominal range; their mean is 0.2462 of the range. These are dependent lower order statistics, not an IID full-range sample. | T4 | **Confirmed design defect.** Different IDs and zero adjacent pairs do not establish the claimed sampling law. | Describe the actual design. For claims about uniformly sampled seed space or unseeded operation, rerun using a specified, correctly sampled seed law and test representativeness. |
| F03 | **MAJOR** | “Risk is a monotone decreasing function of \|θ − t\| for any distribution” | PAPER.md:265–271 | Construct exact integer-count counterexamples and inspect recorded distributions | The proposed counterexample gives risk 0 at distance 1 pp but risk 21.6% at distance 29.7 pp. Recorded data also violate the ordering: adder_n118 has distance 3.5301 pp and risk 12.6743%; bv_n280 is farther away, 5.1102 pp, with higher risk 17.3147%. | T1, T4; derivation below | **False.** A location-shift argument under fixed shape and other assumptions cannot justify a theorem across arbitrary distributions. | Delete the universal claim. Retain the observed correlation as descriptive; state any narrower theorem with its assumptions and proof. |
| F04 | **MAJOR** | Ambiguity window is “independent of the version pair” | PAPER.md:29–31 versus 310–326; RESEARCH_LANDSCAPE.md:885–889 | Compare abstract, correction and actual residual construction | Candidate residuals come directly from the measured pair. The body explicitly withdraws the same claim that remains in the abstract and research log. | T3; followup3.py:109–117 | **Direct contradiction.** It is defensible only as removal of the original mean location under a specified synthetic sweep, not independence from version-pair residuals. | Remove version-pair independence wherever it survives; specify pair, topology, k, residual model and sample. |
| F05 | **MAJOR** | “mechanistically explained” | PAPER.md:39 versus 25–27,265–271,419–420 | Compare headline wording with withdrawn attribution and mathematical evidence | The manuscript explicitly identifies no compiler mechanism, and its universal decision-rule explanation is false under F03. | T4; manuscript comparison | **Unsupported as written.** A narrower explanation that finite sampling can cause disagreement is defensible, but it is not a demonstrated compiler mechanism. | Remove the mechanistic headline or supply a controlled mechanistic study. |
| F06 | **MAJOR** | Risk “95%” bootstrap intervals as uncertainty for long-run decision risk | PAPER.md:193–198,410; prereg_analysis.py:141–169 | Inspect resampling and test coverage with an explicit bounded integer distribution | Each replicate resamples both arms jointly and recomputes P(call), but never recomputes theta's side, long-run verdict, resolution or boundary eligibility. An eligible all-100 observed sample yields interval [0,0], while an underlying 99% at 100 / 1% at 2100 candidate law has risk 97.0299%; that misleading sample occurs with probability 13.398%. | T2, T4; coverage construction below | **Conditional bootstrap, not demonstrated unconditional coverage.** Plug-in estimation is not automatically circular. Actual population undercoverage for these measured circuits has not been established; the universal coverage interpretation is refuted. | State the conditioning and target distribution explicitly. Add coverage/sensitivity work under justified sampling and support assumptions before interpreting these as calibrated population-risk intervals. |
| F07 | **MAJOR** | All choices committed “before any measurement existed”; commit order makes absence of cherry-picking “a checkable fact” | PAPER.md:177–191,467–469 | Reconstruct preregistration and earlier experiment chronology | The census and exploratory results existed before preregistration. Commit c426338, earlier on September 3, already identifies heavy-hex as the worst case. The 39-circuit list and bv_n140 exclusion were frozen before primary raw-data addition and subsequently unchanged apart from a newline. Git records file/commit order, not first access to outputs or independently trusted wall-clock times. | T9 | **Overclaim.** The record supports a frozen follow-up design after exploration, not global outcome blindness or proof that no earlier measurements existed. | Identify exploratory choices and narrow preregistration to the new primary measurements. Do not describe local commit timestamps as independent proof of non-access. |
| F08 | **MAJOR** | “Runtime is independent of both θ and the risk”; selection test p=0.768 | PAPER.md:188–189,247–248; paper_check.py:176 | Recompute the rule and statistical comparison using the actual selected set | The ≤10 s rule reproduces all 39 names. However, the published test adds excluded bv_n140: 40 versus 12 complete-census circuits gives p=.767602. The actual 39 versus 13 complete-census groups give medians .111467 / .126032 and p=.455991. Neither nonsignificant test establishes independence; neither directly tests independence from theta and risk. | T4 | **Confirmed group mismatch and invalid inference.** Six other census circuits lack the complete 12-run data used by this test. | Correct the groups and statistics. Replace independence with the narrower statement that the implemented selection rule uses runtime, while acknowledging prior exploratory visibility. |
| F09 | **MAJOR** | Issue reports knn_341 +41.0%; ours differs by +2.4 pp | PAPER.md:125,349; abstract:33–35 | Read the primary issue and trace all three “ours” values to raw linear data | The issue reports knn_341 **44.060052%**, bv_n280 **44.245142%**, and bv_n140 **46.141524%**. Raw 12-seed ratio-of-means values are 43.425971%, 44.533200%, and 35.206519%. Actual differences are approximately −0.6341, +0.2881, and −10.9350 pp. | T4, T11 | **Confirmed misquotation.** The suspected heavy-hex substitution is absent. | Correct source figures and differences. Describe these as matched-topology numerical comparisons, with the historical configuration limits stated. |
| F10 | **MAJOR** | Selective disagreement is “not” a Benchpress version difference, “which would not be selective” | PAPER.md:342–344 | Test the logic of causal exclusion against circuit-specific compiler or harness changes | A version change can affect one circuit and leave others unchanged. No controlled old-/new-Benchpress comparison establishes the exclusion. The historical issue's exact aggregation is also not supplied; “average percent increase” does not uniquely specify ratio of means. | T11; source/configuration trace | **Invalid causal inference and overstated protocol identity.** | Remove the exclusion. To attribute the mismatch, reproduce the historical benchmark revision, circuits, backend, basis, optimization settings and aggregation. |
| F11 | **MAJOR** | “Passing seed_transpiler removes false positives”; “The remedy is one argument” | PAPER.md:375–376,417–418,448–455; scatter.py:69–76 | Use a recorded fixed seed and distinguish conditional repeatability from agreement with the mean verdict | bv_n280 seed 663193 gives A=1040, B=1157: +11.25%, a regression call against empirical theta +4.8898%. Pairing seed draws does not remove the primary risks: paired mean-of-3 risk is 17.2809% on bv_n280 and 17.51975% on knn_n67. Backend error draws are separately unseeded. | T1; recorded seed row; paired sum-distribution calculation | **False as a guarantee of correct reference verdicts.** Fixing all relevant randomness can remove repeat-to-repeat sampling variance, while freezing a discordant verdict. | Separate fixed-seed reproducibility, paired random-seed evaluation and estimating mean performance. Qualify the variance claim by other randomness; remove the false-positive guarantee. |
| F12 | **MAJOR** | Fixed seeds reproduce “bit-identically” across machines | PAPER.md:220–239; crossmachine/compare.py:207,432 | Inspect both measurement schemas and all compared records | All 216 integers match, but these files contain no output operation sequence, output QASM hash, layout or mapping. Their hashes identify input QASM. Earlier local probes contain output hashes, but cannot establish cross-machine circuit identity. None of the eight committed cross-machine JSONL files records rustworkx, despite the later recorder supporting it. | T4; raw schema inspection; T9 | **Gate-count agreement established; full-output identity unsupported.** Claims about the exact graph-library build rely on narrative metadata, not these raw records. | Say “all 216 tested gate counts matched.” Record dependency versions/builds in future runs; compare serialized outputs and layouts before claiming full identity. |
| F13 | **MAJOR** | A three-run comparison “cannot resolve” changes in the ambiguity interval; conclusion says “within roughly eleven percentage points” of threshold | PAPER.md:29–31,306–308,323–326,444–445 | Interpret the actual 5%/95% call-probability construction | The statistic is a 90-point transition region of a particular binary detector's call probability. It is not a confidence interval or an impossibility theorem. An approximately 10.9 pp total width is not ±10.9 pp around the threshold; the interval need not be symmetric. | T3 | **Overstated decision-theoretic interpretation and ambiguous doubled-width wording.** | Define the interval operationally by P(call) endpoints; state total width and asymmetric endpoints, not impossibility of resolution. |
| F14 | **MINOR** | The sweep parameter is “true change” and the band “contains no θ” | PAPER.md:306–316; followup3.py:109–117 | Derive the normalization analytically and rerun bisection without Monte Carlo | With m=mean(B/A), the multiplicative candidate is rB/m, so its ratio-of-means multiplier is Cr, where C=(mean B/mean A)/m, not r. Integer truncation adds another change. For cc_n64, C=.99103669; its 25.13409 pp unrounded parameter width is 24.90880 pp in mean-change units. The corrected unrounded median is 10.85212 pp. | T3 | **Parameter/estimand mismatch.** Numerically small for the headline, but not identically theta-free under the stated estimand. | Normalize by ratio of arm means when labeling the parameter as mean change, or convert the horizontal axis explicitly; document truncation. |
| F15 | **MINOR** | Additive fits better on “29 of 39 circuits”; 10.86→10.73 pp is a model comparison | PAPER.md:314–321; model_check.py:95–111,281–282 | Recompute paired least-squares fits and four band implementations | The recorded 39 circuits give **23 additive, 3 multiplicative, 13 ties**, not 29 additive. The median 10.73314 pp additive value is reproduced with integer truncation; the real-valued additive model gives 10.67947 pp. Multiplicative medians are 10.86582 pp truncated and 10.86860 pp unrounded. Only one of the 23 resolved stochastic circuits has a wider unrounded additive band. | T3–T4 | **Wrong fit count; hidden discretization convention.** The approximately eleven-point scale survives. | Correct the count and disclose rounding/model conventions and numerical precision. |
| F16 | **MAJOR** | Synthetic null gives mean correlation −.661 and 5/30 trials at least as extreme | PAPER.md:267–271; SETTLED.json:S11 | Search the pinned snapshot for the generating algorithm, parameters, random seed and trial outputs | The numbers recur in manuscripts and the defect ledger. No reproducible generator/trial record for this experiment was located. The available model_check and followup scripts do not implement this claimed null. | Pinned-snapshot search for 0.661 / 30 trials and inspection of implicated scripts | **Unverified numerical experiment, not independently reproducible.** Even a genuine run would establish a result under its chosen null, not a universal property of the decision rule. | Supply the complete generator, parameters, RNG state and trial output, or remove the numerical null claim. |
| F17 | **MINOR** | cc_n32 risk “rests on 6 of 1728 triples” and its quoted interval accompanies theta | PAPER.md:329–332,416; paper_check.py:162–166 | Derive the exact count and identify the interval's estimand | Exact risk is 239,417,152,405 / 64,000,000,000,000 = .003740893006. Multiplying by 1728 gives 6.46426, which the checker rounds to 6; no six-hit sample supports this sentence. The quoted t interval targets mean(B/A−1), not mean(B)/mean(A)−1. The latter's recorded bootstrap interval is [−9.7874%,−6.7707%]. | T1; exact numerator calculation; paper_check.py:162–166 | **Invented effective count and mismatched interval estimand.** Neither removes this circuit's nonzero empirical risk. | Remove the 6/1728 claim; report actual draw-space probability and the interval for the declared estimand. |
| F18 | **MINOR** | bv_n140's three-run distribution spans −10.5% to +100.0% | PAPER.md:35–36,352–355 | Compute extrema of the recorded 200-seed linear draw space | With replacement, repeating the minimum/maximum draw three times is allowed. Exact support extrema are **−17.6781% and +109.1743%**. The 2.5%/97.5% quantiles are about 9.2754% and 57.3127%; the issue's value is at percentile 87.7573. | Exact weighted sum-distribution calculation on deep_bv_n140_q143/q200 | **Reported extrema are not full support bounds.** Central-range and percentile claims are approximately supported. | Label any sampled extrema with sample size/RNG, or report exact support bounds. |
| F19 | **MINOR** | “No aggregation exists anywhere”; “no run-count option” | PAPER.md:112–113 | Follow the benchmark fixture and distinguish timing statistics from gate-count extraction | The gate count comes from one returned circuit, with no gate-count mean/minimum aggregation found. But Benchpress uses pytest-benchmark and sets --benchmark-min-rounds=1; its documented interface supports repetition and timing aggregation. | T10–T11; Benchpress pytest.ini:2 and qiskit_gym/abstract_transpile/test_qasmbench.py:91–100 | **Overbroad source claim.** The narrower gate-count statement survives. | Say no aggregation of repeated gate-count measurements is implemented on the inspected path; distinguish timing rounds. |
| F20 | **MAJOR** | Threshold sensitivity reports “the endpoint” at each cut | PAPER.md:360–362; followup.py:149–175,209–225 | Compare the sensitivity implementation with the preregistered endpoint and exact probabilities | It counts Monte Carlo err>0, not bootstrap lower bound>0; it also uses a different theta-bootstrap stream/budget. At 20%, its 300,000-pair Monte Carlo reports 18/39 but misses six positive empirical risks. Exact point-positive count is 24/39; a 400-resample exact-inner interval analysis yields 22/39. | T5; direct replay of followup.py F10 | **Different endpoint and simulation-resolution artifact.** The weak conclusion that some risk remains at every tested cut survives. | Recompute sensitivity using the stated endpoint or label the alternative statistic; quantify Monte Carlo detection limits. |
| F21 | **MINOR** | Twenty runs per version cost roughly 40 compute hours at two hours per suite run | PAPER.md:374–375 | Multiply the stated run counts and per-run cost | 20×2 versions×2 hours = **80 compute hours**. Forty wall-clock hours could describe two simultaneous machines, but that is not the stated compute total. The browser-visible issue text did not independently establish the cited two-hour figure. | Arithmetic conditional on the manuscript's own cost premise | **Factor-of-two accounting error.** | Correct compute versus wall-clock accounting and provide the source for runtime. |
| F22 | **MAJOR** | “non-negligible on a benchmark used in production” and implied actual regression-gate consequences | PAPER.md:12–19,38–40 | Compare source evidence with the formal rule actually evaluated | The issue establishes use in tracking Qiskit performance. Neither it nor the inspected benchmark defines this +10% gate or uniquely specifies the paper's aggregation. The manuscript itself concedes that no published decision is shown wrong and no formal threshold was supplied. | T10–T11; PAPER.md:77–79,123–128,411 | **A plausible workflow example is presented too close to an established production decision rule.** | Describe a benchmark used to evaluate a production compiler and an explicitly hypothetical threshold/aggregation policy; obtain workflow evidence before claiming deployed-gate impact. |
| N01 | **NOT AN ISSUE** | Primary descriptive 12/26, 7/26 and 4/26 | PAPER.md:193–198,282–302 | Rebuild the full chain from raw records with an independent estimator and replay bootstrap streams | All classifications, point values and 36 saved risk intervals reproduce. The primary count survives exact inner-bootstrap risk evaluation. | T1–T2 | **Attack defeated for the recorded empirical distributions and stated frozen selection.** | Retain as a descriptive result with the sampling and conditioning restrictions above. |
| N02 | **NOT AN ISSUE** | “Ours” issue-comparison values might secretly be heavy-hex | PAPER.md:348–350 | Trace values and topology field to raw census files | All three values come from **linear**, 12 seeds per arm, Qiskit 1.4.3→2.0.0. The separate heavy-hex primary numbers are not the source of this comparison table. | T4 | **Suspected topology substitution disproved.** Source-number and historical-configuration defects remain under F09–F10. | Retain topology identification explicitly in the corrected table. |
| N03 | **NOT AN ISSUE** | Integer threshold and replacement approximation | PAPER.md:155–173 | Prove cross-multiplication for positive baselines; independent enumeration; without-replacement calculation | All primary baselines are positive. The exact integer method agrees in 900 independent small tests. Maximum replacement effect is .001064898; the ≥5% count stays 7. | T1; brute-force test | **Core arithmetic survives.** Unsupported generic zero/overflow cases do not invalidate these data. | Keep domain restrictions explicit. |
| N04 | **NOT AN ISSUE** | Family dependence destroys the already-restricted descriptive count | PAPER.md:288–291,390–415 | Recompute family bootstrap and boundary sensitivity | The family interval reproduces [17.4%,81.0%]. Including boundary cases gives 22/36; using a 4 pp boundary gives 6/20 and 5 pp gives 5/19. Those change the target population, not the frozen 3 pp endpoint. | T1, T4 | **No invalidation of a descriptive count.** Population-rate claims remain unwarranted, as already conceded in v2. | Retain the restriction; do not rehabilitate suite-wide Wilson inference. |
| N05 | **NOT AN ISSUE** | Pinned Qiskit gym omits seed_transpiler; a BQSKit path passes seed=0 | PAPER.md:94–111 | Follow imports, configuration, backend construction, pass-manager arguments, output dispatch and sibling source | Ordinary Qiskit paths call generate_preset_pass_manager without a compiler seed; configuration supplies optimization level/backend, not a hidden seed. The inspected API default is None. BQSKit test_summit.py:179 and :201 explicitly pass seed=0. The separate transpiler-service gym uses TranspilerService, not the same compilation path; it shares output handling. | T10; exact pinned files and installed API signatures | **Narrow source claim supported.** It is not proof about all gyms, all versions or all output randomness. | Keep scope to inspected paths and revision. |
| N06 | **NOT AN ISSUE** | The recorded cross-machine count comparison and commit ordering | PAPER.md:226–230 | Independently compare all keyed raw counts and history | 72/72 counts match in each of three versions. Local history adds preregistration at df09a07 on September 8 and laptop output at e3362fb on September 9. | T4, T9 | **Recorded agreement and local ordering supported.** This does not prove full-circuit identity, first access time, or a complete independent rerun of the primary experiment. | State exactly the evidence earned. |

## Mathematical attacks and their limits

### Universal monotonicity

For A identically 100 and t=.10, the three-run call condition is S_B≥330.

- B identically 109 gives S_B=327, theta=.09, distance 1 pp and risk zero.
- For B=200 with probability .3 and B=29 with probability .7, theta=−.197. If J is the number of high draws, S_B=87+171J. A call occurs exactly when J≥2, giving 3(.3)^2(.7)+(.3)^3=.216.

Thus risk increases from 0 to 21.6% while distance increases from 1 to 29.7 pp. This directly refutes the asserted universal ordering.

It does **not** refute the independently recovered sample correlation −.8329214. It does refute interpreting that correlation's sign or magnitude as a distribution-free property of the decision rule. A synthetic null can show that a negative correlation arises without compiler physics under that particular generator. Its reported numbers cannot be checked without that generator, and one chosen null is not a theorem.

### Bootstrap conditioning and undercoverage

The original risk bootstrap performs these operations:

| Operation on each resample | Done? |
|---|---|
| Jointly resample seed-indexed A and B values | Yes |
| Recompute empirical P(call) | Yes, with 400,000-pair Monte Carlo |
| Recompute theta for choosing the risk side | No |
| Recompute reference REGRESSION/NO_REGRESSION verdict | No |
| Recompute UNRESOLVED classification | No |
| Recompute BOUNDARY eligibility | No |
| Switch between P(call) and 1−P(call) if theta changes sides | No |

Within the original empirical distributions, none of the 26 eligible circuits changed theta's threshold side in the independent 4,000-resample calculation. That is a useful stability result, not proof about unseen seeds. Eligibility is materially less stable: knn_n67 crossed the 3 pp boundary in 22.0% of those resamples, swap_test_n83 in 27.425%, and adder_n118 in 8.55%.

The finite-support coverage counterexample uses A=100 and B=100 with probability .99 or 2100 with probability .01. Its population theta is +20%; the true three-run false-negative risk is .99^3=.970299. With probability .99^200=.1339797, the entire observed candidate sample is 100. The paper's procedure then declares a non-boundary NO_REGRESSION with risk interval [0,0]. Consequently this example's nominal 95% interval has coverage **at most 86.602%**. A sample size of 200 alone is not a valid answer to the coverage attack.

This is not evidence that these actual compiler populations have such a tail. It is an explicit demonstration that calibrated population coverage and global determinism do not follow merely from the recorded finite sample. A sound interpretation must state its seed-space, support and resampling assumptions.

### Ambiguity-band reconstruction

For the 23 resolved stochastic circuits:

| Construction | Median width, pp |
|---|---:|
| Multiplicative, integer-truncated candidate | 10.865824 |
| Additive, integer-truncated candidate | 10.733141 |
| Multiplicative, real-valued candidate | 10.868595 |
| Additive, real-valued candidate | 10.679475 |
| Multiplicative real-valued width converted to ratio-of-means change units | 10.852119 |

The approximately 10.9 pp headline scale survives. Version-pair independence, universal inability to resolve, and exact equivalence of the horizontal parameter to theta do not.

The recorded implementation uses new Monte Carlo draws at successive bisection evaluations. Those evaluations need not be monotone even though the underlying model's call probability is monotone. A 22-step bisection interval is therefore not a numerical accuracy certificate for that stochastic oracle. The deterministic reconstruction removes this issue and reveals last-digit differences, especially in maxima. Model and sampling uncertainty should not be replaced by bisection precision.

## Provenance and reproducibility limits

The primary raw records preserve counts, seed identities, versions, topology and process IDs. They do not independently certify that the compiler executions occurred at the claimed wall-clock times. The available circuit hashes match the pinned checkout, but the pin file explicitly says the early censuses predate its creation and their historical pin is a process assertion. The issue's old Benchpress revision, circuit hashes, complete historical configuration and exact aggregation are not supplied by the comparison.

The source QASM hashes of the three compared circuits at the available pin are:

| Circuit | SHA-256 |
|---|---|
| bv_n280 | 3f3ff9c4986217d895acad447aaf00572951cf8b478daf2365ac9e12ff88de23 |
| knn_341 | 2297b416f035c96e5bf3ab6a114e471053a05514944ef0c4ea547c040d53ca18 |
| bv_n140 | 83ced89de51c8627b2b48bbab11e1788ef4c2833598da15bbdf94b7929f5ca4f |

The “ours” table uses the pinned harness's optimization level 2, basis id/sx/x/rz/cz, 12 fixed seed integers 1000–1011 per version, and **ratio of arm means**. These facts reproduce the values; they do not establish identity to the issue's unspecified averaging operation or original source hashes.

The 12 historical k-band inventory cells are **DERIVED-ONLY in the shipped verification path**: their CSV values are compared to frozen literals, not regenerated from raw measurements. They concern older 2.0.0→2.0.2 research-log experiments, not the primary 39-circuit endpoint. This audit does not relabel those checks as raw reproductions. The primary endpoint and the 400-seed heavy-hex risk k-sweep, in contrast, were independently reconstructed from raw measurements here.

The synthetic-null experiment remains unverified because a reproducible generator was not located. The 0/24 backend-randomness claim is recorded as a research-log result, not a complete independently replayed factorial experiment in this audit; the standalone exp1 artifacts cover narrower linear probes under 2.0.2/2.5.2. No inference of global backend irrelevance is justified by these negative probes.

## A. CORE VERDICT

**CORE SURVIVES, MAJOR CORRECTIONS REQUIRED**

This verdict applies to the empirical result under the recorded seed distributions and frozen eligibility rule. It does not certify population coverage, uniform-seed representativeness, a compiler mechanism, or a deployed production gate.

## B. SMALLEST FATAL CHAIN

**No fatal chain found.**

The shortest successful attack on the claimed verification apparatus is: copy the snapshot → replace knn_n67 candidate counts with 100 → its real risk becomes zero and the headline counts change → verify.py still reports 6/6 PASS. That destroys the verifier's assurance claim, not the independently reconstructed original data result.

## C. MANDATORY v3 CHANGES

1. Correct the seed-generation description and remove IID/full-range representativeness claims. A properly sampled follow-up is required to restore those claims.
2. Remove the universal monotonicity theorem, version-pair independence and mechanistic headline. Retain only the measured association and explicitly scoped synthetic-model statements.
3. State exactly what the risk bootstrap conditions on; distinguish empirical-distribution calculations from calibrated population-risk inference. Publish justified coverage/sampling sensitivity before claiming the latter.
4. Correct preregistration scope: distinguish earlier exploration, the frozen primary follow-up, local commit order and independently established timing.
5. Correct the selection-test groups and remove the inference of runtime independence.
6. Correct the issue's source figures, comparison differences and protocol qualifications; withdraw the claim that a circuit-specific mismatch excludes benchmark-version effects.
7. Replace full-output cross-machine determinism with gate-count agreement. Record missing dependency/build provenance in future replication.
8. Separate reproducibility from agreement with a mean-based verdict. Remove guarantees that supplying a seed eliminates false positives or all relevant randomness.
9. Define ambiguity bands by call-probability endpoints; correct total-width wording, normalization, truncation conventions, fit counts and numerical precision.
10. Supply the missing synthetic-null generator and trial evidence or remove its numerical claims.
11. Correct cc_n32's fictitious 6/1728 count and wrong-estimand interval, the linear bv_n140 extrema, threshold-sensitivity estimator and compute-hour accounting.
12. Rebuild primary verification from raw inputs, verify relevant intervals and denominators, and add the demonstrated raw-mutation failure test. Narrow claims about inventory coverage and benchmark aggregation.

## D. WHAT REMAINS PROVEN

Conditional on the **recorded measurements**, uniformly resampling their empirical arms independently with replacement, using k=3, a +10% inclusive threshold, and the frozen resolution/3 pp eligibility rules, **12 of 26 eligible circuits have bootstrap intervals excluding zero; 7 have estimated risk at least 5%, and 4 at least 10%**. Independent reconstruction reproduces the reported point values and intervals.

The recorded data demonstrate that gate-count variability can produce differing mean-based regression verdicts. For the 23 resolved stochastic circuits, the specified synthetic constructions have median call-probability transition widths near eleven percentage points. For the separate pooled bv_n140/heavy-hex data, the empirical twenty-run risk is about 3.7415%.

At the pinned Benchpress revision, the inspected ordinary Qiskit compilation path does not supply seed_transpiler; inspected BQSKit paths explicitly supply seed=0. The two recorded machines agree on all 216 tested gate counts.

These are descriptive, configuration-specific findings. They do not establish a universal mechanism, suite-wide failure rate, actual erroneous published decision, version-independent ambiguity width, fully deterministic compilation, or validated uncertainty for the intended unseeded population.

