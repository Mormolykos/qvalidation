# v3 correction ledger — every hostile-audit finding, and what was done about it

Audit: `audits/2026-09-12-hostile/HOSTILE_AUDIT.md` (SHA-256
`34574eaa95162ec3314fc181ab955a78dcc6de7d2f9424b3c457fb4061311999`), against published v2
at `17e08f3e92533ff8266b1b586e35f20da2923da8`, DOI `10.5281/zenodo.22689920`.

**Verdict as delivered: CORE SURVIVES, MAJOR CORRECTIONS REQUIRED.** 22 findings, six
attacks defeated, **no fatal chain**.

**No raw measurement was changed, regenerated or re-run.** `results/raw/` is byte-identical
to the v2 published snapshot, and `raw_integrity.py` enforces that going forward. Every
correction below is to a claim, a statistic computed from unchanged data, or the
verification apparatus.

**A finding is not closed because the wording changed.** Where a defect was structural, the
row names the test that now fails if it returns.

---

## The one that mattered

**F01** is not one finding among 22. The audit corrupted a single raw arm file, moving the
true endpoint from 12/26 to 11/26 and the ≥5%/≥10% counts from 7/26 and 4/26 to 6/26 and
3/26 — and `verify.py` reported **6/6 PASS**.

The empirical result survived the audit. **The claim that our apparatus protected it did
not.** Everything in §"Verification rebuilt" exists because of that.

---

## Findings

| ID | Sev | Claim | Accepted? | Independent evidence | Correction | Files | Number moved? | Test | Status |
|---|---|---|---|---|---|---|---|---|---|
| **F01** | MAJOR | "a single command re-checks the whole paper"; "a stale or altered source fails the check" | **ACCEPTED** | Reproduced: mutation A turns raw arm to constant 100, old chain passes all six stages. `paper_check.py:101` read the derived CSV as authority | Verification rebuilt from raw; claim narrowed and now itself tested | `raw_endpoint.py`, `raw_integrity.py`, `mutation_test.py`, `verify.py`, `PAPER.md` §6.1 | No | `mutation_test.py` A/C/E | **CLOSED** |
| **F02** | MAJOR | "200 independent transpiler seeds" | **ACCEPTED** | Confirmed from source *and* data: `scatter.py` draws 2n, dedupes, sorts, keeps smallest n. **6 of 200 realised seeds above range midpoint where ~100 expected**; mean 0.2462 of range | Seed law described exactly; IID/full-range representativeness withdrawn; results scoped to the recorded distributions | `PAPER.md` abstract, §3.4 | No | — | **CLOSED (claim narrowed; restoring it needs a rerun)** |
| **F03** | MAJOR | risk monotone decreasing in \|θ−t\| "for any distribution" | **ACCEPTED — the statement is false** | Counterexample verified; **and our own data break it**: `bv_n280` 5.1100 pp → 17.3147%, `adder_n118` 3.5300 pp → 12.6743% | Universal claim deleted, counterexample and our own violation printed in §4.1. ρ = −0.833 retained as descriptive | `PAPER.md` §4.1 | No | — | **CLOSED** |
| **F04** | MAJOR | ambiguity band "independent of the version pair" | **ACCEPTED** | Abstract contradicted the body, which had already withdrawn it | Removed from the abstract; band stated as inheriting this pair's residuals | `PAPER.md` abstract, §4.3 | No | — | **CLOSED** |
| **F05** | MAJOR | "mechanistically explained" | **ACCEPTED** | Manuscript identifies no compiler mechanism; its universal explanation is false under F03 | Removed from abstract; "we identify no compiler mechanism" stated instead | `PAPER.md` abstract | No | — | **CLOSED** |
| **F06** | MAJOR | risk bootstrap read as coverage for long-run risk | **ACCEPTED** | Replicates recompute P(call) but not θ's side, verdict, resolution or eligibility. Coverage counterexample: nominal 95% has ≤86.6% coverage | Conditioning stated explicitly; stability result *and* eligibility instability (22.0%/27.4%/8.6%) reported; coverage claim withdrawn | `PAPER.md` §3.3 | No | — | **CLOSED (as a scope statement; calibration not claimed)** |
| **F07** | MAJOR | all choices committed "before any measurement existed"; non-cherry-picking "a checkable fact" | **ACCEPTED** | Census and exploration preceded pre-registration; `c426338` already identifies heavy-hex as worst case | Narrowed to a frozen follow-up design after exploration; commit order no longer described as proof of non-access | `PAPER.md` §3.3, §6.1 | No | — | **CLOSED** |
| **F08** | MAJOR | "runtime is independent of both θ and the risk"; p = 0.768 | **ACCEPTED** | **Recomputed here, matching the audit exactly**: published test wrongly included excluded `bv_n140` — 40 vs 12, p = 0.767602. Correct 39 vs 13 gives 0.111467 / 0.126032, **p = 0.455991** | Groups corrected in code and paper; independence inference withdrawn | `PAPER.md` §3.2 §3.4 §5.2, `paper_check.py` | **Yes — a corrected statistic, not a measurement** | `paper_check.py` selection-bias rows | **CLOSED** |
| **F09** | MAJOR | issue reports knn_341 +41.0%, ours differs +2.4 pp | **ACCEPTED** | Issue reports **+44.060%**; our +43.426% → **−0.63 pp**, wrong magnitude *and* sign | Table corrected to +44.245/+44.060/+46.142 and differences +0.29/−0.63/−10.94; configuration stated | `PAPER.md` abstract, §4.4 | **Yes — corrected transcription** | — | **CLOSED** |
| **F10** | MAJOR | selective mismatch "not a Benchpress version difference, which would not be selective" | **ACCEPTED — invalid inference** | A version change can be circuit-specific; no controlled old/new comparison exists | Exclusion withdrawn; attribution explicitly not made | `PAPER.md` §4.4 | No | — | **CLOSED** |
| **F11** | MAJOR | "passing `seed_transpiler` removes false positives"; "the remedy is one argument" | **ACCEPTED** | `bv_n280` seed 663193 gives +11.25% against θ = +4.89% — reproducible and wrong-sided. Paired mean-of-3 risk 17.28% / 17.52% | Repeatability separated from correctness; guarantee removed; unseeded backend draws noted | `PAPER.md` §6, §5.2 | No | — | **CLOSED** |
| **F12** | MAJOR | fixed seeds reproduce "bit-identically" across machines | **ACCEPTED** | Records hold gate counts only — no output QASM hash, operation sequence, layout or mapping | Restricted to "all 216 tested gate counts matched"; "bit-identical" removed | `PAPER.md` §3.4 | No | — | **CLOSED** |
| **F13** | MAJOR | three runs "cannot resolve" a change within ~11 pp | **ACCEPTED** | The statistic is a 5%–95% call-probability transition region, not a confidence interval or an impossibility; endpoints need not be symmetric | Defined operationally by call-probability endpoints; "cannot resolve" removed | `PAPER.md` abstract, §6 | No | — | **CLOSED** |
| **F14** | MINOR | sweep parameter is "true change"; band "contains no θ" | **ACCEPTED** | Normalising by m = mean(B/A) gives realised multiplier C·r, C ≠ 1. `cc_n64`: 25.134 pp → 24.909 pp in mean-change units; median 10.852 pp | Parameter/estimand mismatch disclosed with the converted median | `PAPER.md` §4.3 | No | — | **CLOSED (disclosed; axis not renormalised)** |
| **F15** | MINOR | additive fits better on "29 of 39" | **ACCEPTED** | Recount gives **23 additive, 3 multiplicative, 13 ties**; truncated vs real-valued medians disclosed | Count corrected; truncation convention stated | `PAPER.md` §4.3 | **Yes — corrected count** | — | **CLOSED** |
| **F16** | MAJOR | synthetic null: mean −0.661, 5/30 trials | **ACCEPTED** | **Verified here**: `git grep` over the pinned tree returns **zero** `.py` files containing the figure or the trial design | **Numbers withdrawn, not replaced.** Regenerating a null now and presenting it as the original evidence would be worse than having none | `PAPER.md` §4.1 | **Yes — withdrawn** | — | **CLOSED by withdrawal** |
| **F17** | MINOR | `cc_n32` risk "rests on 6 of 1728 triples"; interval beside θ | **ACCEPTED** | Exact risk 239,417,152,405 / 64,000,000,000,000 = 0.374089%; × 1728 = 6.4643, rounded to 6 by a checker. Quoted t-interval targets mean(B/A−1), not the declared estimand | Effective-count framing removed; ratio-of-means bootstrap interval [−9.79%, −6.77%] reported | `PAPER.md` §4.4 §5.2, `paper_check.py` | **Yes — a fictitious count removed** | `paper_check.py` `cc_n32 exact risk pct` | **CLOSED** |
| **F18** | MINOR | `bv_n140` three-run span −10.5% to +100.0% | **ACCEPTED** | Exact support is **−17.68% to +109.17%**; the issue's value sits at percentile 87.76 | Sample extrema replaced by exact support bounds | `PAPER.md` abstract, §4.4 | **Yes — corrected bounds** | — | **CLOSED** |
| **F19** | MINOR | "no aggregation exists anywhere"; "no run-count option" | **ACCEPTED as overbroad** | Benchpress uses pytest-benchmark with `--benchmark-min-rounds=1`, which supports repetition and **timing** aggregation | Narrowed to no gate-count aggregation on the inspected path | `PAPER.md` §2.1 | No | — | **CLOSED** |
| **F20** | MAJOR | threshold sensitivity reports "the endpoint" at each cut | **ACCEPTED** | `followup.py` counts MC risk > 0, not bootstrap lower bound > 0, on a different stream. At 20% its MC reports 18/39 and misses six positive risks; exact point-positive is 24/39, interval analysis 22/39 | Figures removed; weak conclusion retained and labelled as a different statistic with a stated detection floor | `PAPER.md` §4.5 | **Yes — wrong statistic removed** | — | **CLOSED** |
| **F21** | MINOR | twenty runs ≈ 40 compute hours | **ACCEPTED** | 20 × 2 versions × ~2 h = **80** compute hours | Corrected; wall-clock vs compute distinguished; the ~2 h source noted as unconfirmed | `PAPER.md` §4.5 | **Yes — corrected arithmetic** | — | **CLOSED** |
| **F22** | MAJOR | "non-negligible on a benchmark used in production", implying a real regression gate | **ACCEPTED** | Neither the issue nor the suite defines the +10% gate or the aggregation | Restated as a suite used to evaluate a production compiler under an explicitly hypothetical threshold; "no published decision shown wrong" | `PAPER.md` abstract | No | — | **CLOSED** |

**Findings accepted: 22 of 22. Independently defeated: none.** Every one reproduced, and
the four I re-derived myself (F03, F08, F16, F17) matched the audit to the digit. I have
no finding I believe is wrong.

---

## Attacks the audit ran and defeated — these survived

| ID | Attack | Outcome |
|---|---|---|
| N01 | primary 12/26, 7/26, 4/26 | **Defeated.** Full chain rebuilt from raw with an independent estimator; all classifications, point risks and all 36 saved intervals reproduce |
| N02 | "ours" values secretly heavy-hex | **Disproved.** All three are `linear`, 12 seeds, 1.4.3→2.0.0 |
| N03 | integer threshold / replacement approximation | **Survives.** All baselines positive; exact method agrees in 900 independent tests; max replacement effect 0.001065, ≥5% count unchanged |
| N04 | family dependence destroys the count | **No invalidation.** Family interval reproduces [17.4%, 81.0%]; boundary variants change the target population, not the frozen endpoint |
| N05 | pinned Qiskit gym unseeded, BQSKit seeds | **Supported** for the inspected paths and revision |
| N06 | cross-machine comparison and commit ordering | **Supported** as recorded agreement and local ordering — not full-circuit identity |

---

## Verification rebuilt

| layer | file | what it does | proven by |
|---|---|---|---|
| science | `raw_endpoint.py` | raw per-seed → θ → verdict → boundary → eligibility → risk → interval → 12/26, 7/26, 4/26 → PAPER.md literals. Reads **no** summary, inventory or expected-results file. Risk by exact integer convolution, written independently of `exact_rate_int`; `--cross-check` asserts they agree | mutations A, C, E |
| integrity | `raw_integrity.py` | SHA-256 of all 78 raw arm files vs `RAW_MANIFEST.json`; derived summary required to be reproducible **from** raw | mutations A, B, C, D |
| proof | `mutation_test.py` | corrupts data in throwaway snapshots, **requires** the relevant layer to fail | itself |

**Mutation results.** Pristine passes both layers. Then:

| | mutation | science | integrity | old v2 chain |
|---|---|---|---|---|
| A | audit's T7: whole raw arm → constant | **FAIL** | **FAIL** | pass |
| B | one raw gate count +1 | pass | **FAIL** | pass |
| C | raw scaled, moves eligibility | **FAIL** | **FAIL** | pass |
| D | derived summary only | pass | **FAIL** | pass |
| E | PAPER.md literal only | **FAIL** | pass | pass |

**The old chain passes all five.** B is the instructive row: one gate count does not move a
coarse integer endpoint, so the science layer correctly passes — and without the integrity
layer that edit would be invisible. A layer passing is acceptable only when another catches
the same attack; `mutation_test.py` fails if any mutation is caught by nothing.

**Provenance vocabulary** (`inventory.py`): `RAW-RECOMPUTED` / `DERIVED-READ` /
`NARRATIVE-N-A`. The 12 k-sweep rows are `DERIVED-READ` and were already disclosed as such;
the audit accepted that disclosure. **The primary endpoint is now in the inventory at all** —
three `RAW-RECOMPUTED` rows calling `raw_endpoint.py`. Before v3 it was absent, which is why
every row could reproduce while the headline was wrong.

---

## What remains open, stated as limitations rather than closed

1. **The seed law is not repaired, only described.** Restoring any claim about the seed
   space a user meets requires a rerun under a specified sampling law. Not done.
2. **Bootstrap coverage is not established.** The intervals are conditional on the observed
   classification. Calibration would need justified support and sampling assumptions.
3. **The synthetic null is gone, not replaced.** We therefore make no quantitative claim
   about how much of ρ = −0.833 the decision rule induces.
4. **F14's horizontal axis is disclosed, not renormalised.** The sweep parameter remains
   the normalised candidate multiplier; the conversion is given rather than applied.
5. **The 0/24 backend-randomness probe** is a research-log result, not a replayed factorial
   experiment. No claim of global backend irrelevance is made.
6. **The issue comparison is a numerical comparison at our configuration**, not a
   reproduction of the issue's protocol, whose revision and aggregation are unavailable.
