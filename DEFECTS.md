# Defects in this study — hostile review, 2026-09-03

An independent thread was given `RESEARCH_LANDSCAPE.md`, the code and the raw data, and
told to attack. It re-derived every number in §30–33 from `results/raw/*.jsonl` and
**mutation-tested** the test suite by reintroducing defects the tests exist to catch.

**This file is part of the study, not an appendix to it.** A project whose thesis is
that measurement instruments go unverified cannot suppress the audit of its own
instrument.

Status key: **CONFIRMED** — verified independently here · **ACCEPTED** — agreed without
independent re-derivation · **OPEN** — not yet actioned · **FIXED** — corrected, with
the correction recorded.

---

## The three that would end a review

### D-7.1 / D-7.2 — §30 does not reproduce from its own raw data · CONFIRMED · FIXED

§30's provenance line read *"58 of 58 circuits, 0 crashes, 0 timeouts, 587 run rows,
7 budget stops"*. `bp_large_linear_q202.jsonl` on disk contains **57 circuits, 639 run
rows, 6 budget stops, 1 process_crash (`square_root_n60`)**. Verified directly.

Cause: the census was **re-run** to fix the provenance defect (§26) and §30's numbers
were never recomputed. The headline distribution table likewise matches no file —
recomputed it is 30/12/14 median 0.90% (≥2 seeds) or 31/12/14 median 0.87% (all), not
the 32/12/14 median 0.77% recorded.

**This is the exact failure this project documents in others: a record that does not
match its data.** Every aggregate in §30 must be regenerated from the file it names, and
every table must carry its source filename.

### D-2.1 / D-2.2 — §32's paired column is defined into existence · CONFIRMED · OPEN

`calibrate.py:66-68` computes `b = Σ vals[i]·(1+effect)/k` from **the same indices** as
`a`, so `(b−a)/a ≡ effect` deterministically. The paired column is a step function with
zero variance at every effect size — not a measurement.

§32 conceded this **for the FP=0 row only** (honesty note 1). The power rows are the
identical tautology and were presented as findings:

> *"passing `seed_transpiler` removes every false positive across all 51 circuits and
> raises power at every effect size"*

**Nothing in that column touched a compiler.** Worse, the model is refuted by our own
§31 data: the paired arm assumes a code change scales the observable identically at
every seed, while the real 2.0.0→2.0.2 paired change is heterogeneous — `cc_n32`
−45.76%…−18.64% (27.1 pp spread), `cc_n64` −48.78%…−27.64%, 24 of 51 circuits non-zero.
Re-running the paired FP with each circuit's **measured residuals** gives `cc_n64`
paired FP = **0.021, not 0.000**.

**Direction survives — pairing is still far better. The magnitude ("every", "all 51",
"zero") is an artifact of the model.** Fix: draw the injected effect per-seed from the
measured residual distribution, or delete the paired column and cite §31's real paired
data, which is genuine measurement.

### D-6.1 / D-6.2 — two regression tests pass with their own defects reintroduced · CONFIRMED · OPEN

`test_hash_failure_does_not_discard_the_measurement` and
`test_census_records_child_crash_as_a_row` are **string greps over source text**. The
reviewer added `continue` to the except handler (reinstating the censoring defect
verbatim) and `break` after the crash row (reinstating the census-abort defect), kept
every grepped literal, and **all 11 tests passed**.

Confirmed here: the assertions are `assert '"qasm_sha256": qasm_hash' in source`. They
test that text exists in a file, not that behaviour is correct.

**Fix: behavioural tests that execute the path and assert on the output rows.**

---

## Statistical and framing defects

| id | defect | status |
|---|---|---|
| **D-1.1** | The 27.1% has no error bar. Three decimals off **12 observations**, carried by three low outliers against a cluster of nine near 160k. Resampling which 12 seeds were drawn gives a **95% interval of 0.043 … 0.331**. "27.1%" and "4.3%" are both inside the data, and §31's Limits list omits this. Fix: 200+ seeds on `qft_n320`, or report the interval. | ACCEPTED · OPEN |
| **D-1.2** | Four denominators for one census: §30 says 58, §33 says 57, the CSV has 56 rows, 51 have 12 seeds. "5 of 57 (8.8%)" should be 5/56 = 8.9%. | ACCEPTED · OPEN |
| **D-1.3** | `multiplier_n45` quoted as 0.150/"15.0%"; CSV says **0.147**. Rounded up into a headline table. Its mean cells are dashes in the record while the CSV holds 7647.2 / 8249.2. | ACCEPTED · OPEN |
| **D-1.4** | *"3 runs per version — what `nonhermitian` actually did"* is an **assumption stated as fact**. §16 establishes only that three full-suite runs and their totals were reported; nothing establishes the per-test figures were 3-run averages. Load-bearing: k=1 gives 22/26/**8**, k=3 gives 24/27/**5**. | ACCEPTED · OPEN |
| **D-1.5** | *"isolates a single commit — PR #14417"* is asserted, never shown. 2.0.0→2.0.2 spans two patch releases carrying multiple PRs. The positive control's "24 circuits register the genuine ConsolidateBlocks regression" inherits this unverified attribution. Fix: commit `git log 2.0.0..2.0.2` or the release notes. | ACCEPTED · OPEN |
| **D-1.6** | Three of five UNSTABLE circuits sit **on the cut**: `adder_n64` +10.68% (0.68 pp above), `multiplier_n75` +7.49%, `multiplier_n45` +7.87%. A threshold rule is unstable near its threshold — arithmetic, not a finding. Only `qft_n320` (Δ=0.00%) and `bv_n30` (+22.4%) are genuine. | ACCEPTED · OPEN |
| **D-1.7** | **The threshold table refutes the conclusion drawn from it.** Membership rotates: 18 distinct circuits are unstable at some threshold; exactly one (`qft_n320`) at all of them, and only because its true effect is zero. A constant count with rotating membership is evidence the cut **selects** the members. §31 reads it the opposite way. | ACCEPTED · OPEN |
| **D-1.8** | The thin-arm exclusion holds at 10% but **fails at 5% and 7.5%**, where `multiplier_n350`/`n400` (both budget_stop, <12 seeds) enter the unstable set. The robustness table defending the 10% choice partly rests on arms excluded elsewhere as unreliable. | ACCEPTED · OPEN |
| **D-1.9** | `qft_n320` **is not among #14402's reported cases** (`bv_n140`, `bv_n280`, `knn_341`). The strongest sentence is present-tense about their protocol, but what exists is a bootstrap of a *reconstructed* protocol on a circuit nobody ever miscalled. | ACCEPTED · OPEN |
| **D-2.3** | `calibrate.py:69-70` samples **both** arms from one version's distribution (2.0.2 only). Real pairs differ (`bv_n30`: 55.2 vs 67.5). "Realistic measured noise" means one version's noise on both arms. Unstated. | ACCEPTED · OPEN |
| **D-2.4** | §32 is **not independent** of §31: `qft_n320` unpaired FP 0.272 and §31's P=0.271 are the same statistic on the same 12 integers. Framed as "what this adds to §31". | ACCEPTED · OPEN |
| **D-3.1** | §33's "ambiguity window" is §30's two order statistics with a different denominator — 106.9% is (max−min)/min, 54.8% is (max−min)/median. No new information. Calling it "a computable bound" dresses a re-normalisation as a derivation. | ACCEPTED · OPEN |
| **D-3.2** | §33's window carries **no version stamp**, and §26 measured this circuit family's spread collapsing 45.26% (2.0.2) → 4.32% (2.5.2). If that generalises, the window is an order of magnitude too wide for the comparisons it is aimed at. | ACCEPTED · OPEN |
| **D-3.3** | **The flagship circuit's effect is topology-specific.** On `square`, `qft_n320` spread is **3.5%, not 106.9%** — the single cleanest result does not exist on the second topology. Meanwhile the corpus is *worse* there (29/56 ≥5%). Both must be said before writing up. | ACCEPTED · OPEN |
| **D-5.1** | §29's "INDEPENDENT REPLICATION" has **no artifact** — no log, no JSONL, no environment dump. The evidence is a pasted list of 20 integers from an LLM agent, and §0 of this very record documents these tools fabricating citations. §30 promotes it to **Established**. Fix: commit the replicator's raw output, or downgrade to "consistent with, unverified". | ACCEPTED · OPEN |
| **D-5.2** | **Benchpress is unpinned in every provenance record.** `benchpress_path` points at a session scratchpad; no commit SHA anywhere. Benchpress supplies the circuits, the backend, the topologies and the observable — it is as much the toolchain as Qiskit. Our own standard (`flip_analysis.py:64`) is *"a measurement file that cannot name its own toolchain is not evidence."* It names half. | ACCEPTED · OPEN |
| **D-6.3** | `test_fixed_seed_is_deterministic` has **zero discriminating power**: its fixture `wstate_n3` is constant unseeded (30 runs, 1 distinct value). Passes identically with `seed_transpiler` deleted. | ACCEPTED · OPEN |
| **D-6.4** | `test_all_to_all_has_no_seed_variance` is **vacuous on the same fixture**, and its docstring still claims all-to-all controls for routing — a wording §28 already recorded as corrected. | ACCEPTED · OPEN |
| **D-6.5** | `test_observable_matches_benchpress_definition` **never imports `sweep_bp.py`**. Its assertions are an identity, `>= 0`, `isinstance(int)`, and an inequality true by construction. Reverting the observable to any-2q counting leaves it passing. | ACCEPTED · OPEN |
| **D-6.6** | `test_two_q_gate_type_is_cz_under_default_config` **never reads `default.conf`**. | ACCEPTED · OPEN |
| **D-6.7** | The strengthened provenance test is still weak: `census.py` keeps only the **first** child's env row, so `version is not None` can only fail if circuit #1 crashes. It never checks the version against `require_qiskit`, nor consistency across children — precisely the §26 contamination mode. `flip_analysis.load()` and `calibrate.load()` share a last-wins overwrite: a mixed-version merged file would be silently analysed. | ACCEPTED · OPEN |
| **D-6.8** | With `BENCHPRESS_PATH` unset the suite **skips all 11 and exits 0** — a silent full-suite skip. | ACCEPTED · OPEN |
| **D-7.3** | §30 calls a tautology a confirmation. Seed-for-seed, **49 of 53 shared circuits are byte-identical** between the §24 and §30 files. The sentence explains why they must coincide, then treats the coincidence as validation. It is one measurement run twice. §26 correctly said §24 "are not evidence about Benchpress's workload"; §30 upgrades it to "validated measurement". | ACCEPTED · OPEN |

---

## What the review found sound

- §22 B2 — the #14402 deterministic root cause, recorded **against** our own position.
- §26 — the version-drift incident, self-reported, guard built **and tested**.
- §28 — the cross-process hash-pinned kill experiment; the attribution genuinely follows.
- §28 — backend fingerprinting **before** accepting the refutation: the one place the
  record tested that its own control could have failed.
- §32 honesty note 2 — the floating-point boundary artifact, correctly bounded.
- §31 — "all five have full 12 seeds in both arms": confirmed.
- §33 Q1–Q3 — the most disciplined section: which gyms pass a seed, and the refusal to
  claim the cross-SDK ranking is unreliable or to infer the paper's run count from code.

---

## The honest summary

**The central mechanism holds.** Benchpress compiles unseeded (source-verified), the
transpiler seed is the entropy source (§28's cross-process control), and pairing removes
the discrepancy on real data (§31's 12/12 byte-identical `qft_n320`).

**The magnitude does not yet hold.** The 27.1% has a 4.3–33.1% interval, rests on an
assumed protocol, on a circuit never implicated in the incident, on one topology where
the same circuit shows 3.5% on another. The record's own bar — *"must demonstrate at
least one real decision flip"* — is **not met**. What exists is a decision
*distribution*.

**Nothing is published. No claim has left this folder.** That is the one piece of luck
in this: every defect above was caught before it reached anyone.

---

# Second pass — 2026-09-03, priorities 1–6

The statuses above are the state at the time of the review and are **not rewritten**.
This section supersedes them. Where a defect was resolved, the resolution is named so it
can be checked; where it was not, it says so.

## Status after this pass

| id | status now | where |
|---|---|---|
| D-1.1 | **FIXED** — every probability now carries an interval; the headline was withdrawn | §38, `intervals.py` |
| D-1.2 | **FIXED** — one inclusion rule (≥12 seeds in both arms, exact enumeration) used everywhere; counts regenerate from the named file | §38, `intervals.py`, `paired.py` |
| D-1.3 | **SUPERSEDED** — the table it concerned is withdrawn by D-8.1 | §41 |
| D-1.4 | **NARROWED, still open** — k=3 is external and quoted verbatim from the issue; the *averaging basis* for per-test figures is not stated in the issue and remains an assumption | §43 |
| D-1.5 | **FIXED** — claim proven false: 31 commits, 64 files | §39 |
| D-1.6 | **SUPERSEDED and generalised** — boundary proximity is not an edge case, it is the whole effect | §41 |
| D-1.7 | **CONFIRMED by a stronger route** — the cut selects the members; direction selects them too | §41 |
| D-1.8 | **SUPERSEDED** — the threshold-robustness table rests on the withdrawn statistic | §41 |
| D-1.9 | **STANDS** — `qft_n320` is still not one of #14402's reported cases | — |
| D-2.1 / D-2.2 | **FIXED** — column removed, tautology proven, replacement built, 4 regression tests mutation-tested | §40, §42 |
| D-2.3 | **FIXED by removal** — the both-arms-from-one-version sampling only existed in the withdrawn calibration | §40 |
| D-2.4 | **FIXED by removal** — §32's independence claim is withdrawn with the column | §40 |
| D-3.1 / D-3.2 / D-3.3 | **SUPERSEDED** — §33's ambiguity window is replaced by §42's band, which is direction-free, carries a version stamp and is computed per topology | §42 |
| D-5.1 | **FIXED** — `replication/replicate.py` exists, was executed from clean, passed 144/144, and its failure path was tested | §44 |
| D-5.2 | **FIXED, and a second half found** — commit SHA + module hashes + 58 circuit hashes; `qasm_sha256` was hashing the *output* | §44 |
| D-6.1 / D-6.2 | **FIXED** — behavioural tests; both mutations now fail the suite | previous commit `7f0b232` |
| D-6.3 / D-6.4 | **FIXED** — fixtures replaced with circuits that have measured variance | `tests/test_harness.py` §3 |
| D-6.5 / D-6.6 | **FIXED** — the observable test executes `sweep_bp.py` | `tests/test_harness.py` §4 |
| D-6.7 | **PARTLY FIXED** — single-version and require-qiskit consistency are asserted; a mixed-version *merged* file is still only caught if the first child's env row disagrees | `tests/test_harness.py` §7 |
| D-6.8 | **FIXED** — unset `BENCHPRESS_PATH` now raises, it does not skip | `tests/test_harness.py` |
| D-7.1 / D-7.2 | **FIXED** — §30 regenerated from its own file; a test enforces it | previous commit `7f0b232` |
| D-7.3 | **STANDS** — §24 and §30 remain one measurement run twice | — |

## New defects found in this pass

### D-8.1 — the corpus headline is an artifact of which version is the baseline · CONFIRMED · FIXED by withdrawal

Found while building the D-2.1 replacement. The flip analysis ran with **2.0.2 as
baseline and 2.0.0 as candidate**, and no section said so. In the historically real
direction the same data gives **0 of 52 unstable on heavy-hex**, against the recorded
14 of 52. The 26.9% headline is withdrawn; §42 replaces it with a direction-free
statistic. **This is more serious than anything in the original review.**

### D-8.2 — `qasm_sha256` fingerprints the transpiled output, not the input · CONFIRMED · FIXED

Present on 3,561 of 3,849 rows and read throughout as a circuit fingerprint. All 54
hashable circuits carry many distinct values, because the field hashes `pm.run(circuit)`.
The input circuits were never pinned. `input_qasm_sha256` added; the old field keeps its
name and meaning.

### D-8.3 — `intervals.py` resampled the two arms independently · CONFIRMED · FIXED

Both arms came from the **same 12 seeds** (1000–1011, verified aligned in every file),
so the outer bootstrap must resample seed indices once and carry `(old_i, new_i)`
together. `paired.py` does, and exposes `--bootstrap-mode` so the difference is visible
rather than assumed.

### D-8.4 — the seed bootstrap is biased low for band width · CONFIRMED · DISCLOSED

Resampling seeds with replacement duplicates draws and shrinks the empirical spread, so
band intervals sit below their own point estimate (square: point 9.78 pp, interval
[6.99, 9.85]). Not corrected; stated in §42 as a floor rather than a symmetric interval.

### D-8.5 — degenerate circuits inflate the measured benefit of pairing · CONFIRMED · FIXED

20 of 52 heavy-hex circuits (27 of 51 on linear) are byte-identical at every seed across
the two versions, so ρ ≡ 1 and the paired band is 0.00 pp **by construction** — D-2.1
again. Including them made pairing look infinitely better; excluding them gives 6.8×.
Every §42 figure is on the heterogeneous subset, and a regression test enforces the
split.

---

# Third pass — 2026-09-03, priorities A1 and A2

## Defects closed by this pass

| id | status now | where |
|---|---|---|
| **D-1.1** | **CLOSED** — the 200+ seeds this defect asked for were finally run, on the five circuits that needed them. Every 12-seed per-circuit rate is superseded; `bv_n30` read 3.87% at n=12 and 0.71% at n=200 | §48, `deep.py` |
| **D-1.4** | **CLOSED for k, still open for the averaging basis** — three runs per version is quoted verbatim from the issue; nothing anywhere establishes what the per-test "avg." averages over | §43 |
| **D-1.9** | **CLOSED** — `qft_n320` was never one of #14402's cases, so the study now measures #14402's actual circuits: `bv_n140`, `bv_n280`, `knn_341`, on `linear`, against the version pair the issue actually names | §48 |
| **§45 A1** | **RESOLVED** — a real wrong decision is demonstrated, non-boundary, interval excluding zero | §48 |
| **§45 A2** | **RESOLVED against the model** — multiplicative rejected, band robust to ≤1.34 pp, always conservative | §47 |

## New defects found in this pass

### D-9.1 — the study measured the WRONG VERSION PAIR for two days · CONFIRMED · FIXED

Issue #14402 compares **1.4.3 against 2.0**. Every measurement before 2026-09-03 evening
used **2.0.0 against 2.0.2**, whose real changes sit ~15 pp from the decision threshold
and therefore cannot flip anything. The gating question could not have been answered by
any amount of analysis of that pair. Fixed by building a 1.4.3 environment and running
the full census (58/58 circuits, 0 crashes).

### D-9.2 — "the point estimates are EXACT" was false · CONFIRMED · FIXED

`exact_call_rate` tested `b >= a*(1+t)`; the protocol's rule is `(b-a)/a >= t`. Different
expressions in floating point: **84 disagreements in 900 randomised cases**, and
0.905002 vs 0.904327 on real `adder_n64` data. Never large enough to change a conclusion,
but the exactness *claim* was false. Replaced with the integer rule
`q*Sb >= (q+p)*Sa`, verified against exact-integer brute force: **900 cases, 0
disagreements**.

### D-9.3 — the backend draws unseeded error rates · CONFIRMED · NOT A CONFOUND

`FlexibleBackend` gives different error rates on every construction, in all three Qiskit
versions, and the two version arms build their backends separately. At optimization
level 2 the layout passes score with error rates, so this could have confounded every
between-version comparison in the study. Tested with 4 verified-distinct backend draws ×
6 circuits × 4 seeds: **0 of 24 cases changed**. Not a confound — but it was luck, not
design, and nothing in the harness had ever checked it.

### D-9.4 — an arbitrary 5% error-rate floor hid the main result · CONFIRMED · FIXED

`decision_error.py` originally reported only circuits erring at ≥5%. That floor was an
analyst choice with no justification, and it excluded `bv_n140` — the one circuit that is
both named in #14402 and demonstrably miscalled, at 2.0% (12 seeds) / 2.98% (200 seeds).
The best result in the study was suppressed by a threshold nobody had defended. Floor
removed; all nonzero rates are now reported with their distance to the cut.

### D-9.5 — pairing is WORSE on large-regression false negatives · CONFIRMED · DISCLOSED

The remedy this study recommends does not help uniformly. On the four circuits with real
missed regressions, `seed_transpiler` pairing gives a **higher** miss rate on three
(`bv_n140` 0.968 vs 0.980 unpaired, `bv_n30` 0.954 vs 0.961, `adder_n64` 0.859 vs 0.904).
§42's 6.8× band narrowing is about resolving power near the threshold and does **not**
transfer to detection of large regressions. Any recommendation of pairing must say so.

### D-9.6 — the enumeration draws k seeds WITH replacement · CONFIRMED · DISCLOSED

A real maintainer runs k *different* seeds. Enumerating with replacement includes
`[s,s,s]`. Quantified: without replacement the heavy-hex band is 12.71 pp against 14.04.
Like the model choice, the reported figure is the conservative end.
