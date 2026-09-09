# Reviewer C audit prompt — paste this whole block

---

You are auditing the `qvalidation` scientific software repository. Run every command from the repository root.

**AUDIT ONLY. DO NOT EDIT, REFACTOR, RENAME, REFORMAT OR "FIX" ANYTHING.** Produce a report. If you believe something must change, describe it; do not change it. Any write to any file is a failed audit.

## STEP 0 — MANDATORY, BEFORE ANY OTHER WORK

Read `SETTLED.json`. It records questions that have already been tested and closed, with the command that settled each and the result.

Then, for every concern you are about to investigate, run:

```
python settled.py --check "<your keywords>"
```

If it returns **ALREADY ANSWERED**, do not re-test it. Cite the entry ID and move on. **Thirty entries are already closed**, including: backend error-rate confounding, seed independence, PRNG/process-state artifacts, selection bias, the integer decision rule, with/without replacement, multiplicative vs additive residual models, bootstrap arm pairing, duplicate circuits, family clustering, the ρ = −0.833 tautology, observable identity across versions, pre-registration compliance, Benchpress aggregation, the six code-implementation findings F1–F6 (unsupported-k enumeration, seed-alignment enforcement, zero-baseline handling, Monte-Carlo chunk order, the inventory's circular self-check, scatter.py's abort-on-chunk-failure), **and the eight most recent, S23–S30**: the Benchpress seeding overclaim, the "across machines" contradiction, the "mechanism" overclaim, the seed-guard truncation hole, the raw-data overclaim, verify.py not running paper_check, the cross-machine determinism result, and two defects in the cross-machine tooling itself.

**Two prior audits already ran and their findings are fixed.** Re-reporting S17–S30 as new findings is the failure mode to avoid: those defects are gone from the code, and the entries record what the code does *now*, not what it used to do.

**Re-testing settled ground wastes the owner's paid quota. It is the single most common failure of external reviewers on this project.** Three separate reviews have re-raised the same closed questions.

## WHAT HAS ALREADY BEEN DONE — do not repeat it

- Three rounds of adversarial review by two other model families.
- A 16-phase red-team audit of the manuscript.
- A first-principles audit re-deriving every reported number from raw data (`audit.py`).
- `paper_check.py` — 49 quantitative claims in `PAPER.md` recomputed and compared to the text; 17 come from the raw per-seed files, 29 from `results/summary/prereg_heavy-hex.csv`, 3 from both.
- `inventory.py --check` — 41 recorded numbers compared against a fresh recomputation, 29 of them re-derived from `results/raw/*.jsonl` and 12 re-read from a summary table and labelled `DERIVED`.
- Four claims withdrawn on the record; see `DEFECTS.md` and `RESEARCH_LANDSCAPE.md`.

**The scientific claims have been attacked exhaustively. Do not re-litigate them.**

## YOUR ACTUAL TASK — the thing nobody has audited

**Does the code do what the paper says it does?**

Roughly 4,600 lines of Python have never been read by an independent auditor. Every prior review examined *claims*. You examine *implementation*.

### PRIORITY TARGET — `crossmachine/`

**Start here.** It is the newest code in the repository, it has had exactly one reviewer, and it underwrites a claim the paper now makes in §3.4: that a fixed seed reproduces bit-identically on two physical machines with different CPU vendors.

- `crossmachine/measure.py` — imports the circuit/seed selection from `replication/replicate.py` rather than restating it. Does it actually hold the selection identical? Does `--require-qiskit` fail closed? Is the recorded environment sufficient to identify a machine?
- `crossmachine/compare.py` — the same-machine test reads platform, cpu_count and processor. **Can it be fooled?** Can a genuine difference be reported as a match, or an absence as a difference? It got the second one wrong once already (S30).
- `crossmachine/PREREGISTRATION.md` vs what the code does. The document claims the check introduces **no selection freedom** because it inherits a frozen set. Verify that claim against the code.
- The paper's §3.4 claim vs the 216 committed measurements. **Does the evidence support the sentence?** The stated scope limit is that both machines ran rustworkx 0.18.1 — check whether any stronger reading has leaked into the wording.

### Then audit these:

### 1. Estimator correctness
- `intervals.py` — `exact_call_rate`, the integer path `q·Sb ≥ (q+p)·Sa`, `wilson`, `k_means`, `_grid` caching.
- `deep.py` — `exact_rate_int`, `mc_rate` chunking (does chunking change the estimate?), `_sums3` broadcasting.
- `paired.py` — `exact_paired_rate`, `band`, `_solve` bisection convergence and its termination condition.
- Does each function compute what its docstring claims? Is there an off-by-one, a wrong axis, a silent dtype overflow, a `searchsorted` side error?

### 2. Pre-registration compliance at code level
- `PREREGISTRATION.md` §5 vs `prereg_analysis.py`. Every constant, every rule, every exclusion.
- Does `analyse()` implement §5.1–5.4 exactly? Does `endpoint()` implement the stated primary endpoint?

### 3. Data-pipeline integrity
- `scatter.py`, `sweep_bp.py`, `census.py` — can any row be silently dropped, duplicated, or mislabelled?
- Are failures always recorded as rows rather than discarded?
- `load()` in `intervals.py` and `prereg_analysis.py` — do they agree on what a valid row is?

### 4. The verification layer itself
- `verify.py`, `paper_check.py`, `inventory.py`, `tests/test_harness.py`.
- **Can these pass while the underlying claim is false?** A checker that cannot fail is worse than none.
- Are the tests behavioural or do any merely assert that text exists in a file?

### 5. Numerical hazards
- int64 overflow in sum-triples; float comparisons on any decision path; RNG reuse across nested loops that should be independent; Monte Carlo estimates reported to more digits than their standard error supports.

## OUTPUT FORMAT

For each finding:

- **Severity:** CRITICAL (produces a wrong number) / MAJOR (could under other inputs) / MINOR / NOTE
- **File and line**
- **What the code does** vs **what the paper or docstring says**
- **A concrete input that exposes it**, or "not reachable with current data" and why
- **Whether any published number changes**

End with exactly:

```
CRITICAL: n
MAJOR: n
MINOR: n
NOTE: n
```

and one sentence: *"The implementation does / does not faithfully compute the quantities the paper reports, because ..."*

## RULES

1. **Do not edit any file.**
2. **Check `settled.py --check` before investigating anything.**
3. A claim being cautious is not evidence it is correct — but a claim being already-settled means you cite the entry rather than re-run it.
4. If you find nothing critical, say so plainly. Do not manufacture findings.
5. The owner pays for every token. Be efficient. Do not re-run experiments; read code.
