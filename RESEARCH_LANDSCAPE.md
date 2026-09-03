# Quantum Software Validation — Research Landscape and Candidate Selection

**Author:** Panagiotis Gkilis · **Started:** 2026-09-02 · **Last audited:** 2026-09-03

**Verification standard:** every source below was checked against arXiv/ACM/Quantum-journal
listings by direct search. Sources I could not verify are listed in §11 and are NOT used
to support any argument.

---

## ⛔ READ THIS BEFORE ANY OTHER SECTION

**Sections are ordered newest-first, and later sections WITHDRAW earlier ones.** §31–§38
still read as live findings and several of them are not. Do not quote a number from this
file without checking it here first.

| status | claim | where |
|---|---|---|
| ✅ **LIVE** | Benchpress passes no `seed_transpiler` in any of its 8 SDK gyms | §33, source-verified |
| ✅ **LIVE** | The transpiler seed is the dominant entropy source | §28, cross-process control |
| ✅ **LIVE** | A fixed seed reproduces bit-identically; different seeds do not | §44, re-run from clean |
| ⭐ **LIVE** | **A REAL WRONG DECISION: `bv_n140` (+31.0% regression) is MISSED 2.98% of the time, 95% CI [1.72%, 4.99%], 200 seeds/arm, non-boundary** | §48 |
| ⭐ **LIVE** | #14402's own **+46.1%** for `bv_n140` is one draw from a range spanning **−10.5% to +100%**; the truth is **+31.0%** | §48 |
| ✅ **LIVE** | #14402's numbers **reproduce independently** — within 0.5 pp and 2.4 pp on the two low-variance circuits | §48 |
| ✅ **LIVE** | Unseeded 3-run comparison cannot resolve a change inside an **11.5–14.0 pp** window on heavy-hex (range across modelling choices) | §42, §47 |
| ✅ **LIVE** | Topology ordering linear < square < heavy-hex | §42, direction-free |
| ✅ **LIVE** | k=3 is external (quoted from #14402); no conclusion depends on it | §43 |
| ✅ **LIVE** | Backend error rates are unseeded but **do not affect the observable** — 0/24 cases, controls verified distinct | §46 |
| ⛔ **REJECTED** | the multiplicative noise model — additive fits better on linear and heavy-hex | §47 (band survives, ≤1.34 pp, conservative) |
| ⛔ **CORRECTED** | "point estimates are EXACT" — the float rule disagreed with the literal one in 84/900 cases; now exact integer arithmetic | §46 attack 10 |
| ⚠ **LIVE** | **Pairing does NOT fix the false negatives** — it is worse on 3 of 4 affected circuits | §48 |
| ⛔ **WITHDRAWN** | "26.9% of heavy-hex circuits have a seed-dependent verdict" | §41 — direction artifact; **0 of 52** in the real direction |
| ⛔ **WITHDRAWN** | "`qft_n320` is miscalled 27.1% of the time" | §38 — CI [0.017, 0.631] at n=12 |
| ⛔ **WITHDRAWN** | "pairing removes every false positive across all 51 circuits" | §40 — the column was `1[e ≥ t]` |
| ⛔ **WITHDRAWN** | "2.0.0 vs 2.0.2 isolates a single commit, PR #14417" | §39 — 31 commits, 64 files |
| ⛔ **SUPERSEDED** | "no real decision has been shown to be wrong" (§45 A1) | **§48 demonstrates one** |
| ⚠ **NOT ATTEMPTED** | causal attribution of any change to a specific commit or PR | §39, §48 category 5 |

**§45 is the current hostile audit. §12 and §25 do not exist.** Every live number above
re-derives from raw data via `python inventory.py --check` (31/31 as of 2026-09-03).

---

## 0. What happened before this document

Two deep-research reports (Gemini, ChatGPT) were commissioned on the same prompt.
Both were then checked source-by-source. **Both contain material errors.** The errors
matter, because three of ChatGPT's five "confirmed open problems" are already closed
in the literature, and Gemini's central theoretical claim is probably resolved.

This is not a complaint about the tools. It is the first useful result: the gap
analysis had to be redone against primary listings, and doing so changed the answer.

### Errors found in the pasted reports

| # | Report | Claim | Reality |
|---|---|---|---|
| 1 | ChatGPT | Qermit benchmark by "Askey et al. (2023)" | **Author name does not exist.** The paper is Cirstoiu, Dilkes, Mills, Sivarajah & Duncan, *Volumetric Benchmarking of Error Mitigation with Qermit*, Quantum **7**, 1059 (2023). The paper is real; the attribution is fabricated. |
| 2 | ChatGPT | Area 3 cross-framework equivalence = **CONFIRMED OPEN PROBLEM**, "no source found" | **False.** QITE (arXiv:2503.17322, 2025) tests Qiskit, PennyLane, Pytket and BQSKit for semantic equivalence via QASM round-trip and found 17 bugs (14 confirmed/fixed). Also arXiv:2406.06836 compares transpilers across qiskit-braket-provider, qBraid-SDK and Pytket extensions. This was ChatGPT's **#2 ranked** open question. It is dead as stated. |
| 3 | ChatGPT | Area 7 replication studies "essentially non-existent" | **False.** *Works on my QPU: Reproducibility in Quantum Computing Research* (arXiv:2607.08348) semi-automatically analysed ~5,000 QC papers 2021–2026 for reproduction packages. arXiv:2510.25839 reproduced key results from eighteen photonic/hybrid QML works. |
| 4 | ChatGPT | "No follow-ups" to MorphQ | **False.** MorphQ++ — a reproducibility study of metamorphic testing on quantum compilers — was published at the 2024 Workshop on Replications and Negative Results (DOI 10.1145/3695750.3695823). |
| 5 | ChatGPT | Area 9 LLM quantum code "nascent, no multi-model comparisons" | **Overstated.** QuanBench+ (arXiv:2604.08570) is explicitly a unified multi-framework benchmark; QCoder (INLG 2025), QHackBench, QCircuitBench and Qiskit QuantumKatas (arXiv:2605.27210) all exist. |
| 6 | ChatGPT | Area 8 "no source explicitly measuring seed sensitivity in QML" | **False.** Kakavand, Strohmeyer & Schlotter (arXiv:2604.18837) ran a dedicated seed-sensitivity phase and report mean CV 1.4%. This was ChatGPT's **#4 ranked** open question. |
| 7 | Gemini | A "profound theoretical contradiction" between NIBP theory and experiments showing non-unital noise prevents plateaus | **Probably already reconciled.** *Noise-induced shallow circuits and absence of barren plateaus* (arXiv:2403.13927) was published in **Nature Physics** (2026) and gives theory for exactly that: under non-unital noise, both barren-plateau signatures are avoided for local-observable cost functions. Gemini presents as an open contradiction something that has a published resolution. |
| 8 | Gemini | Cites "Wang, S., et al. (2024), *Beyond unital noise…*" | Unverified. The canonical NIBP reference is Wang et al., *Noise-induced barren plateaus in variational quantum algorithms*, **Nature Communications 12**, 6961 (2021). |

**The common failure:** I asked both tools to tell me whether the obvious next question
had already been answered. Neither actually checked. Both listed gaps by *absence of
evidence in their own search*, which is not the same thing.

### What the reports got right

Gemini's citations verified better than ChatGPT's. Kakavand et al. (arXiv:2604.18837)
is real and is exactly as described: 970 experiments, nine binary datasets, four quantum
feature maps, three classical kernels, nested cross-validation, **0 of 29 pairwise
quantum–classical comparisons significant at α=0.05**, hardware validation on IBM
`ibm_fez` (Heron r2) with kernel fidelity r ≥ 0.976, and a spectral explanation
(quantum eigenspectra too flat or too concentrated versus RBF's intermediate profile).
Gemini's feasibility triage (what needs a dilution refrigerator and what does not) is
sound and I have not found an error in it.

---

## 1. Map of the research landscape

The field splits into two layers, and they are not equally worked over.

**Layer 1 — "Does QML work?" (SATURATED).**
Between 2024 and 2026 this question was answered, negatively, at small scale, several
times over. Bowles, Ahmed & Schuld (arXiv:2403.07059) benchmarked 12 quantum models
across 6 tasks and 160 datasets: out-of-the-box classical models win, and removing
entanglement often does not hurt. Schnabel & Roth (*Quantum Machine Intelligence*,
doi 10.1007/s42484-025-00273-5) ran ~20,000 kernel models: no clear advantage.
Kakavand et al. (2026) closed the tabular case with statistical significance testing
and hardware validation. **Do not enter here.** The remaining questions in this layer
("find a dataset where quantum wins") are the ones the whole field is already racing
on, and losing.

**Layer 2 — "Does the software under the experiments work?" (THIN, and getting real
attention only since ~2023).**
This is where the unresolved questions are, and it is the layer where software
engineering, differential testing and measurement discipline are the required skills
rather than many-body physics. The existing corpus is small and enumerable:

- **QDiff** (Wang et al., ASE 2021) — differential testing across Qiskit, Cirq, PyQuil.
- **MorphQ** (Paltenghi & Pradel, ICSE 2023; arXiv:2206.01111) — metamorphic testing,
  8k program pairs in two days, 13 bugs, 9 confirmed. Qiskit only.
- **MorphQ++** (2024) — reproducibility study of the above.
- **QITE** (arXiv:2503.17322, 2025) — cross-platform, assembly-level. Qiskit,
  PennyLane, Pytket, BQSKit. 17 bugs, 14 confirmed/fixed. **Circuits fixed at 11 qubits
  and 15 gates. Cirq and Braket not covered.**
- **A Survey on Testing and Analysis of Quantum Software** (arXiv:2410.00650).
- **Detecting Flakiness in Quantum Software** (arXiv:2512.18088).
- Equivalence-checking machinery: MQT **QCEC**; ZX-calculus checking (arXiv:2208.12820);
  model counting (arXiv:2403.18813); MPO-based checking (arXiv:2410.10946); ZXNet
  (DAC 2025). Equivalence checking is **QMA-complete**; ZX is incomplete and cannot
  prove non-equivalence.

**Layer 2b — resource estimation (THINNEST).**
Four to five open estimators now exist — Azure QRE (`qsharp` package, runs locally),
Google **Qualtran**, Zapata **BenchQ**, MIT-LL **pyLIQTR**, plus QuRE. Papers using
them: arXiv:2311.05801 (Azure QRE), arXiv:2402.12434 (TUM/CDA), arXiv:2408.02587
(Krol et al., shift scheduling — **abstract confirms one problem, one algorithm**),
arXiv:2608.12936 (AutoQuREO). A three-tool comparison of Qualtran / BenchQ / Azure QRE
on the shift-scheduling problem appears as **a figure inside a broader applications
paper** (arXiv:2409.14183), not as a study in its own right.

**Layer 3 — physics-heavy (barren plateaus, error mitigation theory, noise models).**
Real open questions exist here, but they need the QM I do not yet have. Noted, not
recommended. See PHYSICS_KNOWLEDGE_MAP.md when the project starts.

---

## 2. Research-gap table

| Area | Verdict | Evidence |
|---|---|---|
| QML beats classical on small tasks | **NOT A GAP — answered negatively** | 2403.07059; s42484-025-00273-5; 2604.18837 |
| QML seed/split sensitivity (kernels) | **ALREADY WELL STUDIED** | 2604.18837 phase (iv), mean CV 1.4% |
| QML seed sensitivity (variational QNNs, not kernels) | **POSSIBLE OPPORTUNITY** | no equivalent study found; kernels ≠ variational |
| Metamorphic testing of Qiskit | **ALREADY WELL STUDIED** | 2206.01111; MorphQ++ 2024 |
| Cross-platform equivalence, small circuits | **ALREADY WELL STUDIED** | 2503.17322 (4 platforms) |
| Cross-platform equivalence, **as a function of circuit size/structure** | **CONFIRMED OPEN PROBLEM** | QITE fixed at 11 qubits / 15 gates; no scaling study found |
| Are "semantics-preserving" passes actually semantics-preserving? | **STRONG OPPORTUNITY** | QITE reports this as a *threat to validity* they had to fix by hand — nobody has measured it |
| Compiler quality **across SDK versions over time** | **CONFIRMED OPEN PROBLEM** | only API-drift for LLM codegen exists (2607.04072); no transpiler-output regression study found |
| Cirq / Braket under differential testing | **POSSIBLE (weak alone)** | explicitly excluded by QITE |
| Resource-estimator agreement, systematic | **CONFIRMED OPEN PROBLEM** | precedent exists as one figure on one problem (2409.14183); no multi-algorithm study |
| Error-mitigation method selection rule | **STRONG OPPORTUNITY (needs hardware)** | Quantum 7, 1059 and Quantum 7, 1034 disagree by circuit class |
| Vendor noise model predictiveness | **STRONG OPPORTUNITY (needs hardware)** | Quantum 7, 1059 states simple models fail qualitatively |
| Replication of QC papers | **ALREADY WELL STUDIED (paper level)** | 2607.08348 (~5,000 papers); 2510.25839 (18 works) |
| Replication at **artifact-execution** level | **POSSIBLE OPPORTUNITY** | 2607.08348 measures presence of packages; whether they *run* is a different measurement |
| LLM quantum code correctness | **ALREADY WELL STUDIED** | 2406.14712; 2604.08570; 2605.27210; QCoder |
| Barren plateaus, unital vs non-unital | **NOT A GAP as Gemini framed it** | 2403.13927 (Nature Physics 2026) |

---

## 3. Ten candidate research questions

Scores are 1–10. **Feas** = feasibility with current skills. **Value** = likely
scientific value. Full fields for the top four; the remainder are summarised because
they were rejected and detail would be waste.

---

### C1 — Where does compiler semantic equivalence break down? A scaling study.

**CORE QUESTION.** QITE established that four quantum SDKs disagree semantically at
11 qubits and 15 gates. At what circuit width, depth and structure does the rate of
semantic divergence between platforms rise, and does it rise faster than the
equivalence checker's ability to detect it?

**WHY IT MATTERS.** Every published NISQ result passes through a transpiler. If
divergence grows with circuit size, the results most likely to matter are the ones
least likely to be verified.

**WHAT THE LITERATURE DOES.** Tests at one fixed small size and reports bug counts.

**WHAT IS MISSING.** Size is never an independent variable. Nobody reports a
divergence-versus-size curve, and nobody reports the checker's *failure* rate (timeouts,
"unknown") as a function of size — which is itself the interesting quantity.

**HYPOTHESIS.** Divergence rate is non-decreasing in circuit depth; the equivalence
oracle's inconclusive-verdict rate grows faster than the divergence rate, producing a
region where miscompilation is undetectable in practice.

**EXPERIMENT.** Generate circuits over a controlled grid (qubits × depth × gate-set ×
entanglement structure). Round-trip through Qiskit, PennyLane, Pytket, BQSKit, +Cirq,
+Braket at optimisation levels 0–3. Verdict each pair with a layered oracle: QCEC (DD),
ZX, MPO, and — where all fail — statistical distribution testing over sampled outputs
with a pre-registered significance threshold. Report divergence rate, oracle-failure
rate, and the crossover.

**DATA.** Generated. No external dataset. **COMPUTE.** One workstation; tens of
thousands of CPU-hours worst case, controllable by the grid. **SOFTWARE.** Qiskit,
Cirq, PennyLane, pytket, BQSKit, Braket SDK, MQT QCEC, pyzx, quimb/MPO.

**FAILURE MODES.** The oracle wall arrives immediately (equivalence checking is
QMA-complete) and the study degenerates to "we could not tell." Generated circuits are
unrepresentative of real ones. Divergences turn out to be float tolerance, not semantics.

**RESULT A.** Clean monotone divergence curve with an identified crossover size →
strong paper. **RESULT B.** No growth in divergence; the 11-qubit result was
size-independent → still publishable as a negative result with a stated bound.
**RESULT C.** Oracle fails before any signal → the paper becomes about the
verifiability frontier, which is a legitimate and arguably more useful result.

**NOVELTY.** First characterisation of transpiler divergence as a function of circuit
scale, and first published measurement of practical verifiability limits.
**WOULD FAIL IF.** A 2026 paper already did the scaling study and I missed it.
**PHYSICS NEEDED.** Low. Unitaries, gate sets, measurement statistics. No Hamiltonians.
**DIFFICULTY 6 · FEAS 8 · PAPER 8 · VALUE 8**

---

### C2 — Does the quantum compiler get better? A longitudinal regression study across SDK versions.

**CORE QUESTION.** Across the released versions of Qiskit (and Pytket, and Cirq) over
the last three years, on a fixed benchmark corpus, does transpiler output improve
monotonically in gate count, depth, and semantic correctness — or are there releases
that regress?

**WHY IT MATTERS.** Results published in 2023 and results published in 2026 are
compiled by different software. If the compiler regressed on some axis in some release,
a chunk of the literature is not comparable across years, and nobody would know.

**WHAT THE LITERATURE DOES.** Compares transpilers *to each other at one moment*
(arXiv:2406.06836). Studies API drift for LLM code generation (arXiv:2607.04072).
One paper notes trends reproduced between Qiskit 1.1.0 and 2.2.3 as an aside
(arXiv:2603.29598).

**WHAT IS MISSING.** No study treats **SDK version as the independent variable** and
transpiler output quality as the dependent variable.

**HYPOTHESIS.** Improvement is not monotone; at least one release regresses on at
least one of {two-qubit gate count, depth, semantic equivalence rate, transpile time}
for at least one circuit class.

**EXPERIMENT.** Pin N versions in isolated environments (uv/conda/Docker). Fix a
circuit corpus (MQT Bench + generated). For each version × optimisation level × seed,
record gate counts, depth, wall time, and equivalence verdict vs. the untranspiled
circuit. Seeds fixed; SabreSwap is stochastic, so many seeds per cell and report
distributions, not points.

**DATA.** MQT Bench + generated. **COMPUTE.** Modest, embarrassingly parallel.
**SOFTWARE.** Qiskit (many versions), pytket, Cirq, MQT Bench, MQT QCEC, Docker.

**FAILURE MODES.** Old SDK versions will not install cleanly on modern Python — this
is the main engineering risk and the main engineering contribution. Improvements may be
so obviously monotone that there is no story. Stochastic passes could swamp the signal
if seed handling is sloppy.

**RESULT A.** Named regressions in named releases → immediately useful, cited by
practitioners. **RESULT B.** Monotone improvement → a clean, citable "the compiler is
trustworthy across versions" baseline, plus a reusable harness. **RESULT C.** Variance
across seeds exceeds variance across versions → the finding is that single-run
transpiler comparisons in the literature are underpowered. That is a strong result.

**NOVELTY.** First longitudinal compiler-regression study in quantum computing; a
reusable versioned benchmarking harness.
**WOULD FAIL IF.** Environment reconstruction proves impossible for enough versions.
**PHYSICS NEEDED.** Very low.
**DIFFICULTY 5 · FEAS 9 · PAPER 7 · VALUE 7**

---

### C3 — Do independent quantum resource estimators agree? (RECOMMENDED)

**CORE QUESTION.** Given the same algorithm, the same problem size, and the
same physical assumptions made as identical as the tools permit, how far apart are the
physical-qubit counts and runtime estimates produced by Azure QRE, Qualtran, BenchQ and
pyLIQTR — and what fraction of the spread is attributable to genuine modelling choices
versus undocumented defaults?

**WHY IT MATTERS.** Resource estimates are the numbers that governments, funders and
corporate strategy teams use to decide when quantum computing becomes relevant, and to
set post-quantum cryptography migration deadlines. They are quoted as if they were
measurements. If four open tools disagree by an order of magnitude on the same input,
every downstream claim inherits an uncertainty nobody is reporting.

**WHAT THE LITERATURE DOES.** Uses one tool per paper. arXiv:2311.05801 uses Azure QRE.
arXiv:2402.12434 uses resource estimation for application development. Krol et al.
(arXiv:2408.02587) study **one** algorithm on **one** problem — the abstract confirms
this. A three-tool comparison exists as a single figure inside a broader automotive
applications paper (arXiv:2409.14183).

**WHAT IS MISSING.** No systematic, multi-algorithm, multi-tool comparison with
controlled assumptions, no decomposition of where the disagreement comes from, and no
reproducible harness. The one existing comparison is a figure, not a study — which is
useful, because it means a reviewer already accepts that the comparison is meaningful.

**HYPOTHESIS.** H1: For the same algorithm and matched assumptions, physical-qubit
estimates across tools differ by more than a factor of 2 for a majority of test cases.
H0: Estimates agree within a factor of 2 once assumptions are matched.
H2: The dominant source of spread is magic-state distillation and layout assumptions,
not algorithm-level gate counting.

**EXPERIMENT.**
1. Select a fixed algorithm set with unambiguous specifications — QPE on a fixed
   Hamiltonian, Shor at several key sizes, Grover at several sizes, and one chemistry
   instance if the tools share a common input format.
2. For each tool, expose every settable assumption (code distance policy, error rates,
   gate times, distillation factory, connectivity) and construct a matched-assumption
   configuration plus each tool's own default configuration.
3. Record logical qubits, physical qubits, T-count, runtime, and every assumption the
   tool reports back.
4. Report spread as ratio-to-geometric-mean per case; decompose by ablating one
   assumption class at a time.
5. Pre-register the algorithm list and the factor-of-2 threshold before running.

**DATA.** None external — the tools are the instrument. **COMPUTE.** Laptop-scale;
these are cost models, not simulations. **SOFTWARE.** `qsharp` (Azure QRE runs locally,
no Azure account), `qualtran`, `benchq`, `pyliqtr`. All pip-installable.

**EXPECTED FAILURE MODES.** The tools may not accept a common algorithm input, forcing
me to re-express each algorithm per tool — which introduces *my* implementation as a
confounder. This is the single biggest threat and must be controlled by having each
algorithm implemented from the tool's own published example where one exists, and by
reporting T-counts as an intermediate checkpoint so an input-mismatch shows up before
the final number. Some tools may be unmaintained.

**RESULT A.** Large, systematic disagreement with an identified dominant cause →
genuinely important paper; directly relevant to PQC timeline policy.
**RESULT B.** Tools agree once assumptions are matched → also valuable: it means the
spread seen in the wild is a documentation problem, not a modelling problem, and the
paper becomes "here is the configuration that makes them agree."
**RESULT C.** Tools cannot be made comparable at all → a negative result about the
state of the field, publishable in a software-engineering venue.

**NOVELTY.** First systematic cross-tool resource-estimation agreement study.
**WOULD FAIL IF.** Such a study appeared in 2026 and I missed it (I searched; I did not
find one — but this must be re-checked immediately before committing).
**PHYSICS NEEDED.** Moderate but *bounded and nameable*: surface-code distance,
magic-state distillation, T-gate counting, logical vs physical qubits. I do not need to
derive these — I need to understand what each knob means well enough to match it across
tools. **This is exactly the boundary where a professor is the right person to ask.**
**DIFFICULTY 6 · FEAS 8 · PAPER 9 · VALUE 9**

---

### C4 — Are transformations documented as "semantics-preserving" actually semantics-preserving? A census.

**CORE QUESTION.** Across the optimisation and rebase passes of the major SDKs, what
fraction of passes documented as semantics-preserving demonstrably change circuit
semantics, and under what conditions?

**WHY IT MATTERS.** This is the assumption every quantum experiment rests on and nobody
tests directly.

**WHAT IS MISSING.** The QITE authors state, as a *threat to validity*, that some
platform transformations documented as semantics-preserving actually changed semantics,
and that they handled it by manual verification. Nobody turned that observation into a
measurement.

**HYPOTHESIS.** A non-trivial fraction of documented-safe passes violate semantics under
identifiable conditions (specific gate types, parameter values near boundaries,
multi-controlled gates).

**EXPERIMENT.** Enumerate passes per SDK from documentation. For each pass, generate
circuits targeted at that pass's trigger conditions. Apply pass in isolation. Check
equivalence. Classify each violation by cause.

**DATA/COMPUTE/SOFTWARE.** As C1. **PHYSICS NEEDED.** Low.
**FAILURE MODE.** Violations turn out to be documented-elsewhere caveats, making this
a documentation audit rather than a correctness result.
**DIFFICULTY 5 · FEAS 9 · PAPER 7 · VALUE 7**

---

### C5 — Seed and initialisation sensitivity of *variational* QML results

Kakavand did this for kernels (deterministic given data). Variational QNNs are the
stochastic case and were not covered. Question: what fraction of reported QNN accuracy
differences fall inside seed noise? Re-run models from Bowles et al.'s open PennyLane
package across many seeds and report effect-size distributions.
**Risk:** Bowles et al. already run multiple seeds; this may be a thin increment.
**DIFFICULTY 4 · FEAS 9 · PAPER 5 · VALUE 6**

### C6 — Artifact-execution audit of published QML repositories

arXiv:2607.08348 measured whether reproduction packages *exist*. Whether they *run* on
a clean machine, and what fraction reproduce their headline number, is a different
measurement. **Risk:** enormous manual labour; also a social-friction paper that makes
enemies. **DIFFICULTY 5 · FEAS 7 · PAPER 6 · VALUE 7**

### C7 — Extending cross-platform differential testing to Cirq and Braket

QITE explicitly excludes both. Straightforward, and almost certainly finds bugs.
**Risk:** pure increment on an existing method; reviewers will say "engineering."
**DIFFICULTY 3 · FEAS 9 · PAPER 4 · VALUE 5**

### C8 — Does Qiskit Aer's `NoiseModel.from_backend` predict hardware?

An independent audit of vendor noise-model predictiveness across circuit classes.
Quantum 7, 1059 already states simple models fail qualitatively. **Risk:** needs
substantial hardware time; free-tier IBM allocation is ~10 minutes/month, which is not
enough for a controlled study. **DIFFICULTY 7 · FEAS 4 · PAPER 8 · VALUE 8**

### C9 — A decision rule for error-mitigation method selection

Can circuit structure alone predict whether ZNE or CDR wins? **Risk:** hardware-bound,
and the physics of the mitigation methods is beyond me right now.
**DIFFICULTY 8 · FEAS 3 · PAPER 8 · VALUE 8**

### C10 — Semantic vs. execution correctness in LLM-generated quantum code

Do circuits that pass Qiskit HumanEval tests actually implement the intended unitary?
**Risk:** the area is now crowded (QuanBench+, QCoder, QCircuitBench, QuantumKatas),
and it is an LLM paper wearing a quantum hat. **DIFFICULTY 4 · FEAS 9 · PAPER 5 · VALUE 5**

---

## 4. Ranking

| Rank | Candidate | Diff | Feas | Paper | Value | Composite |
|---|---|---|---|---|---|---|
| **1** | **C3 — resource-estimator agreement** | 6 | 8 | 9 | 9 | **strongest** |
| 2 | C1 — divergence-vs-scale | 6 | 8 | 8 | 8 | strong |
| 3 | C2 — longitudinal compiler regression | 5 | 9 | 7 | 7 | strong, safest |
| 4 | C4 — semantics-preserving census | 5 | 9 | 7 | 7 | strong |
| 5 | C8 — noise-model audit | 7 | 4 | 8 | 8 | blocked by hardware |
| 6 | C6 — artifact-execution audit | 5 | 7 | 6 | 7 | viable, unpleasant |
| 7 | C5 — variational seed sensitivity | 4 | 9 | 5 | 6 | thin |
| 8 | C9 — mitigation decision rule | 8 | 3 | 8 | 8 | out of reach now |
| 9 | C10 — LLM semantic correctness | 4 | 9 | 5 | 5 | crowded |
| 10 | C7 — Cirq/Braket extension | 3 | 9 | 4 | 5 | increment only |

---

## 5. Recommendation — SUPERSEDED, see §13

> **C3 was REJECTED on 2026-09-02 after round two of the gap search.** Krol et al.
> (arXiv:2408.02587) do compare Azure QRE, Qualtran and Bench-Q side by side on the
> QISS algorithm under a surface-code scheme with a 0.001 error budget. The gap as
> formulated is closed. The original text is kept below unedited, because the reasoning
> about *why* that shape of project fits is still correct — only the topic died.
> **The live recommendation is now C2, with C1 second. See §13.**

**C3 — the resource-estimator agreement study — with C2 as the fallback.**

Reasons, in order of weight:

1. **It exploits the asymmetry precisely.** The instrument is four Python packages. The
   contribution is experimental design, controlled comparison, ablation and honest
   reporting of spread. That is the same shape as the 14-encoder benchmark already
   completed — a comparison nobody had run, run properly.
2. **The numbers matter outside the paper.** Resource estimates set PQC migration
   timelines. An unreported factor-of-N disagreement between the tools that produce
   those numbers is a real finding with a real audience.
3. **Every outcome is publishable.** Disagreement is a finding; agreement-after-matching
   is a finding; incomparability is a finding. There is no null result that wastes the work.
4. **The physics requirement is bounded and nameable.** Surface code distance, magic
   state distillation, T-counts. Four concepts, not a field. And the gap between
   "I measured the disagreement" and "I know which tool is right" is exactly the
   question to put to a professor.
5. **Compute is trivial.** These are cost models. No GPU, no queue, no hardware time.

C2 is the fallback because it is the lowest-risk of the four and needs almost no physics
at all — if C3's tools turn out to be incomparable in a way that kills the study within
the first two weeks, C2 can absorb the same harness discipline and still produce a paper.

---

## 6. Why the recommended project might fail — honestly

- **The input-equivalence problem may be fatal.** If the four tools cannot be fed the
  same algorithm without me re-implementing it four times, then I am measuring my own
  four implementations, not the tools. This is not a small risk. It is *the* risk. The
  mitigation — use each tool's own published example implementations, and checkpoint on
  T-count before comparing physical qubits — may not hold for every algorithm. If it
  holds for only two of five algorithms, the paper shrinks.
- **A reviewer can say "of course they disagree, they model different architectures."**
  This is the obvious objection and the paper lives or dies on answering it. The answer
  has to be the ablation: showing how much of the spread survives after matching every
  assumption the tools expose. If most of the spread comes from assumptions the tools
  do *not* expose, I can measure that but I cannot explain it — and "we found a big
  number and cannot explain it" is a weaker paper.
- **The tools may be unmaintained.** BenchQ came out of a DARPA program at a company
  (Zapata) that no longer exists in its original form. If it does not install, the study
  drops to three tools, and three is thin.
- **I may be wrong that nobody has done this.** I searched and found one figure inside
  one applications paper. That is not proof of absence. A single 2026 preprint I did not
  surface could make this a replication rather than a first study. **This must be
  re-checked, deliberately and adversarially, before any code is written** — and if it
  has been done, the honest move is to switch to C2, not to reframe.
- **The physics could bite deeper than expected.** If matching assumptions across tools
  requires genuinely understanding surface-code overhead derivations rather than just
  setting parameters, the timeline extends past when ΦΥΕ40 starts consuming attention.
- **Venue risk.** This is a software-engineering paper about a physics field. Physics
  venues may consider it out of scope; software venues may consider it out of domain.
  Realistic targets are IEEE QCE (Quantum Week), ACM TQC, or arXiv + Zenodo DOI, which
  is the route already used successfully.

---

## 7. Minimum quantum-physics knowledge required

Bounded. These four, and nothing beyond them, for C3:

| Concept | Why the paper needs it | Depth required |
|---|---|---|
| Logical vs physical qubits | The primary output quantity | Conceptual + the encoding-rate relation |
| Surface-code distance and error thresholds | Controls physical-qubit overhead; a key matched assumption | Enough to set it correctly and say what it means |
| Magic-state distillation / T-gate counts | Hypothesised dominant source of disagreement | Enough to identify the factory model each tool uses |
| Circuit depth → runtime under a gate-time model | The runtime output | Straightforward arithmetic |

**Not required for C3:** Hamiltonians, density matrices, entanglement measures,
many-body physics, quantum field theory, barren-plateau theory. This is the point of
choosing C3 over anything in Layer 3.

For C1/C2/C4 the requirement is lower still: unitary matrices, gate sets, and
measurement statistics.

---

## 8. Minimum software and hardware

**Hardware:** the existing workstation. No GPU needed. No quantum hardware needed.
Free-tier IBM Quantum access is optional and would only be used for a sanity check,
never for a headline number.

**Software:** Python 3.11+; `qsharp` (Azure QRE, local), `qualtran`, `benchq`,
`pyliqtr`; `qiskit`, `pytket`, `cirq`, `pennylane`, `amazon-braket-sdk`, `bqskit`
(for C1/C2/C4); `mqt.qcec`, `pyzx`; `numpy`, `scipy`, `pandas`, `matplotlib`;
Docker or `uv` for pinned multi-version environments; `pytest`; DVC or plain
content-hashed result files.

**Reproducibility apparatus** (built before results, not after): deterministic seeds,
recorded package versions, a single `run_all` entry point, raw results committed
separately from processed results, and a pre-registration file timestamped before the
first production run.

---

## 9. Roadmap from zero to first result

| Phase | Work | Output | Time |
|---|---|---|---|
| 0 | **Adversarial prior-work check.** Deliberately try to find the paper that kills C3. Search arXiv listings by category, not by keyword. If found → switch to C2. | Go / no-go, written down | 1–2 days |
| 1 | Install all four estimators in isolated environments. Reproduce one published number from each tool's own documentation. | "Tools install and behave" note; any tool that fails is dropped here, in writing | 3–5 days |
| 2 | Write PRE_REGISTRATION.md: algorithm list, assumption grid, hypotheses, factor-of-2 threshold, exclusion criteria, stopping rule. **Before any comparison is run.** | Frozen protocol | 2 days |
| 3 | Build the harness: one config → one result row, per tool. Checkpoint on T-count. | `run_all` works end to end on one algorithm | 1 week |
| 4 | **First result:** one algorithm, four tools, default assumptions. Look at it. Do not tune. | The first real number | ~2 weeks from start |
| 5 | Full grid, matched assumptions, ablations. | Results tables | 2–3 weeks |
| 6 | Adversarial pass: try to destroy the finding. Re-implementation confounder test, tool-version sensitivity, assumption-coverage audit. | Robustness section | 1 week |
| 7 | PHYSICS_KNOWLEDGE_MAP.md complete; PROFESSOR_BRIEF.md written. | The professor conversation | ongoing |
| 8 | Paper. | arXiv + Zenodo DOI | 2 weeks |

**First real number at roughly week 2.** Phase 0 can kill the project on day two, which
is the correct place for it to die.

---

## 10. Sources actually verified

Every item below was confirmed by direct search against arXiv, ACM DL, Quantum journal
or Nature listings during this session.

1. Bowles, Ahmed & Schuld — *Better than classical? The subtle art of benchmarking quantum machine learning models* — arXiv:2403.07059 (2024).
2. Kakavand, Strohmeyer & Schlotter — *Benchmarking Quantum Kernel SVMs Against Classical Baselines on Tabular Data* — arXiv:2604.18837 (2026).
3. Schnabel & Roth — *Quantum kernel methods under scrutiny: a benchmarking study* — Quantum Machine Intelligence, doi:10.1007/s42484-025-00273-5.
4. Paltenghi & Pradel — *MorphQ: Metamorphic Testing of the Qiskit Quantum Computing Platform* — ICSE 2023, arXiv:2206.01111, doi:10.1109/ICSE48619.2023.00202.
5. *MorphQ++: A Reproducibility Study of Metamorphic Testing on Quantum Compilers* — 2024 Workshop on Replications and Negative Results, doi:10.1145/3695750.3695823.
6. Wang et al. — *QDiff: Differential Testing of Quantum Software Stacks* — ASE 2021.
7. *QITE: Assembly-Level, Cross-Platform Testing of Quantum Computing Platforms* — arXiv:2503.17322 (2025).
8. *Comparative Study of Quantum Transpilers* — arXiv:2406.06836 (2024).
9. *A Survey on Testing and Analysis of Quantum Software* — arXiv:2410.00650 (2024).
10. *Detecting Flakiness in Quantum Software: A Dynamic Testing Approach* — arXiv:2512.18088.
11. Cirstoiu, Dilkes, Mills, Sivarajah & Duncan — *Volumetric Benchmarking of Error Mitigation with Qermit* — Quantum **7**, 1059 (2023).
12. *Unifying and benchmarking state-of-the-art quantum error mitigation techniques* — Quantum **7**, 1034 (2023).
13. Wang et al. — *Noise-induced barren plateaus in variational quantum algorithms* — Nature Communications **12**, 6961 (2021).
14. *Noise-induced shallow circuits and absence of barren plateaus* — arXiv:2403.13927, published Nature Physics (2026), doi:10.1038/s41567-026-03245-z.
15. *Experimental demonstration of the absence of noise-induced barren plateaus using information content landscape analysis* — arXiv:2602.22851.
16. *Using Azure Quantum Resource Estimator for Assessing Performance of Fault Tolerant Quantum Computation* — arXiv:2311.05801, doi:10.1145/3624062.3624211.
17. *Utilizing Resource Estimation for the Development of Quantum Computing Applications* — arXiv:2402.12434 (QCE 2024).
18. Krol, Erdmann, Munro, Luckow & Al-Ars — *Assessing the Requirements for Industry Relevant Quantum Computation* — arXiv:2408.02587 (2024). **One algorithm, one problem — confirmed from the abstract.**
19. *Quantum Computing for Automotive Applications: From Algorithms to Applications* — arXiv:2409.14183. **Contains the Qualtran / BenchQ / Azure QRE three-tool figure.**
20. *AutoQuREO: A Framework for Automated Quantum Resource Estimation and Optimization* — arXiv:2608.12936.
21. *Works on my QPU: Reproducibility in Quantum Computing Research* — arXiv:2607.08348.
22. *Establishing Baselines for Photonic Quantum Machine Learning* — arXiv:2510.25839.
23. Vishwakarma et al. — *Qiskit HumanEval* — arXiv:2406.14712.
24. *QuanBench+: A Unified Multi-Framework Benchmark for LLM-Based Quantum Code Generation* — arXiv:2604.08570.
25. *Qiskit QuantumKatas* — arXiv:2605.27210.
26. *Benchmarking API Drift in LLM-Generated Quantum Code Across Successive SDK Versions* — arXiv:2607.04072.
27. *Equivalence Checking of Quantum Circuits with the ZX-Calculus* — arXiv:2208.12820.
28. *Equivalence Checking of Quantum Circuits by Model Counting* — arXiv:2403.18813.
29. *Equivalence checking of quantum circuits via intermediary matrix product operator* — arXiv:2410.10946, Phys. Rev. Research.
30. *ZXNet* — DAC 2025, doi:10.1109/DAC63849.2025.11133226.
31. *Quantum vs. classical: a comprehensive benchmark study for predicting time series* — arXiv:2504.12416.

---

## 11. Cited in the pasted reports but NOT verified — do not rely on these

These appeared in the Gemini or ChatGPT reports and I could not confirm them in this
session. They may well be real. They are **not** load-bearing for anything above, and
none of them should be cited in a paper until independently confirmed.

- Guan & Ying — VeriQR (adversarial robustness verification tool)
- Ma et al. — Q-BRIDGE (backend-aware graph learning for denoising outcome distributions)
- Zhang — *Failure-Guided Fuzzing for Hybrid Quantum-Classical Programs*
- Yousuf & Sofi — *Characterizing Bugs and Quality Attributes in Quantum Software* (32,296 bug reports)
- Smith-Miles et al. — *A Quantitative Analysis of QAOA Implementations*
- Cajas Ordóñez et al. — *Quantum Kernel Advantage over Classical Collapse in Medical Foundation Model Embeddings*
- Dowarah et al. — *Mitigating Noise-Induced Barren Plateaus Using a Non-Unitary Ansatz*
- Yu et al. — *Quantum vs. Classical Machine Learning: A Unified Empirical Comparison*
- Wang, S. et al. (2024) — *Beyond unital noise in variational quantum algorithms*
- Egginger et al. (2024) — quantum kernel hyperparameter study
- Dey et al. — *Embedded Quantum Machine Learning (EQML): A Roadmap*
- AutoQML (2025)
- "Askey et al. (2023)" — **this attribution is wrong; see §0, error 1**

---

## 13. ROUND TWO — 2026-09-02 — what the second sweep killed

A second, deliberately adversarial gap search was run. Its instruction was to *kill*
candidate gaps rather than list them. It killed five, including my own recommendation.
Verifying its output then killed two of its three survivors as well.

### Killed by the round-two report (accepted)

| Gap | Killed by |
|---|---|
| Resource-estimator agreement (my C3) | Krol et al., arXiv:2408.02587 — Azure QRE, Qualtran and Bench-Q modelled side by side on QISS, surface code, error budget 0.001, gate times 140 ns → 1 ns, error rates 10⁻³ → 10⁻⁶ |
| Simulator-vs-simulator differential testing | Upadhyay, Fakorede & Farooq, arXiv:2603.22789 (394 bugs, 12 simulators, ~60% of critical failures in classical infrastructure); QDiff, ASE 2021 |
| Quantum ecosystem dependency rot | Ohto, Ishimoto, Matsumoto & Kusumoto, arXiv:2606.27124, ICSME 2026 RENE track — 77,700 executions, 37 Bugs4Q artifacts, 21 Qiskit versions; reproducibility 62.2% (v0.20.1) → 16.2% (v2.3.1); 93.6% of failures dependency-related |
| Cloud QPU calibration drift | multiple 2026 hardware studies; also hardware-bound, so excluded by constraints regardless |
| QV / CLOPS metric criticism | Wack, arXiv:2608.18044 (IBM, Aug 2026) — CLOPS_h, explicitly designed to close gaming loopholes |
| Circuit cutting / knitting correctness | saturated; and it is a statistics problem, not a validation-testing problem |

### Killed by my verification of the round-two report's own survivors

**Its survivor #2 — "scalable property-based testing and dynamic quantum assertions" —
is dead.** The report claimed no ecosystem-wide property-based testing framework exists
and that no mutation-score data exists. Both are false:

- **QuCheck: A Property-based Testing Framework for Quantum Programs in Qiskit** —
  arXiv:2503.22641, published in **ACM Transactions on Quantum Computing**,
  doi:10.1145/3815169. This is precisely the framework said not to exist.
- QSharpCheck — Honarvar, Mousavi & Nagarajan, *Property-based Testing of Quantum
  Programs in Q#*, ICSE Workshops 2020, doi:10.1145/3387940.3391459.
- *Generating Property-Based Tests for Quantum Algorithms* — Springer, 2025,
  doi:10.1007/978-981-96-7423-7_2.
- Mutation testing is a populated subfield, not an empty one: **QMutPy** (ISSTA 2022,
  doi:10.1145/3533767.3543296), **Muskit** (ASE 2021), *Mutation Testing of Quantum
  Programs: A Case Study with Qiskit* (IEEE), **QCRMut** (arXiv:2410.01415),
  **QuanForge** for QNNs (arXiv:2604.20706), *Efficient Mutation Testing of QML Models*
  (arXiv:2605.00107), *Quantum circuit mutants: empirical analysis and recommendations*
  (Empirical Software Engineering, doi:10.1007/s10664-025-10643-z), *Evaluating
  Mutation-based Fault Localization for Quantum Programs* (arXiv:2505.09059).

**Its survivor #1 — "statistical practice audit of quantum computing papers" — is
badly wounded.** The report claimed zero papers have quantified statistical malpractice
in the field. In fact **arXiv:2605.29872, *Claim against Measurement: Statistical
Artefacts in Quantum Error Mitigation Benchmarks*, systematically reviews 81
publications (2022–2026) against an eight-criterion statistical-reporting framework**
— sample size and its justification, variance and error bars, statistical evidence,
drift control, overhead quantification, and noise-model validation. Related: *The Cost
of Certainty: Shot Budgets in Quantum Program Testing* (arXiv:2510.22418), *How Many
Shots Are Enough for a Quantum Circuit?* (arXiv:2606.16965), *Estimating shots and
variance on noisy quantum circuits* (arXiv:2501.03194). A field-wide extension of the
81-paper audit is possible but would be an increment on a published method, and
"we ran their framework on more papers" is a weak paper.

**Its survivor #3 — decoder output isomorphism — is plausibly open but wrong for us.**
ECCentric (arXiv:2511.01062) compares BP-OSD and MWPM across codes and error models on
logical error rate, not bitwise agreement, so strict output isomorphism does appear
unmapped. But: the report itself argued the question is irrelevant because only the
threshold matters, and it is right that this is the reviewer's first objection.
More decisively, the physics load is **not** bounded — syndrome graphs, stabilizer
formalism, logical Pauli frames and code distance are core QEC theory, not four
nameable concepts. **Rejected on the physics constraint, not on novelty.**

**Unverified from the round-two report:** the "VERMICULAR" hardware noise study — the
described content surfaced but no arXiv identifier or canonical listing could be found.
Do not cite it. Bennink et al., *Uncertainty Quantification for Quantum Computing*
(arXiv:2603.25039) — not independently confirmed.

**Now verified, previously listed as unverified in §11:** Yousuf & Sofi,
*Characterizing Bugs and Quality Attributes in Quantum Software: A Large-Scale
Empirical Study* — **arXiv:2512.24656**. It is real.

### What this pattern actually means

Three sweeps, two of them by deep-research tools, have now each produced a list of
"open problems" that collapsed on verification. That is a finding about the field, not
bad luck: **quantum software engineering is small enough, and its SE community active
enough, that every obvious validation question already has a 2025–2026 paper on it.**
Searching for an unstudied *topic* is the wrong search.

The two most useful papers found across all three rounds — MorphQ++ and Ohto et al. —
are both **replication and negative-results papers**, and ICSME has a dedicated RENE
track that publishes exactly this. The field is young, its results are single-shot, and
almost nothing has been independently re-run. That is the durable opening, and it is the
same thing already done successfully in the speech work: take one specific published
claim, run it properly, extend one axis, report what survives.

### ROUND THREE — 2026-09-02 — C2 killed too, by tooling not by papers

**C2 as I formulated it is dead.** Panos found it, not me, and my search method was at
fault: I searched the paper literature and never searched repositories or vendor
engineering blogs. Corrected going forward — repos and vendor blogs are now part of
every phase-zero check.

What closes the broad form:

- **Qiskit/red-queen** — a benchmarking tool whose stated purpose is comparing
  "different quantum compilers, as well as different versions of the same quantum
  compiler," measuring depth, build/bind/transpile time and memory, reporting mean,
  median, range, variance and standard deviation. **Archived 2024-08-14, superseded by
  Benchpress, no longer maintained.**
- **Qiskit/benchpress** — 1,000+ tests. Compares **SDKs against each other at one
  moment**, not versions over time. Measures execution time (pytest-benchmark) and
  memory (pytest-memray). Docs mention no seeds, no variance, no significance testing,
  no regression detection. Multi-version results exist only in a side branch.
- **qiskit-community/qiskit-metriq** — creates a tox environment for **every Qiskit
  version from qiskit-terra v0.13.0 to latest**, batch-compiles circuits, tracks depth
  and gate count, uploads to metriq.info. A data pipeline, not an analysis.
- **Metriq: A Collaborative Platform for Benchmarking Quantum Computers** —
  arXiv:2603.08680 — describes the platform, not a regression study.
- IBM's own release blogs do adjacent-release comparisons (2.5 vs 2.4.2) across a large
  circuit collection, including transpilation speed and circuit quality.
- **Observing the Quantum Compiler through Automatic Experiment Tracking for Qiskit** —
  Stirbu & Meijer–van de Griend, arXiv:2608.05041 (2026-08-05). Autologging of
  transpilation provenance into MLflow. **Explicitly single-run observability: no
  cross-version tracking, no regression hunting, no circuit-family stratification, no
  multiple seeds, no significance testing.** The authors invite practitioners to say
  which analyses would be useful.

**What survives, precisely.** The longitudinal *data* exists or is cheap to regenerate;
the only tool designed for cross-version comparison is archived; its successor dropped
the capability; and no published analysis treats **release as the longitudinal
independent variable while hunting for regressions**, stratified by circuit family and
optimisation level, with statistics that respect SabreSwap's stochasticity. Prior art
for the statistics exists in adjacent work (recomputation across 25 transpiler seeds
with a 2σ routing-noise threshold before declaring a winner), which is a method to
borrow, not a competitor.

**Verdict: NOT an open problem. An unoccupied analysis niche.** Publishable, thin, and
vulnerable to being closed by an IBM blog post or by the Metriq team, who already hold
the data. Kept as a fallback, not a recommendation.

### Live recommendation after round two (SUPERSEDED by §14)

**C2 — longitudinal transpiler regression across SDK versions — is now first.**
**C1 — divergence versus circuit scale — is second.** **C4 is third.**

Neither C1, C2 nor C4 appeared in any kill list across three sweeps. Nothing found has
closed them. That is not proof they are open, but it is the strongest evidence on the
table, and it was arrived at by trying to destroy them rather than by failing to find them.

C2 gains rather than loses from Ohto et al.: they proved the method (21 pinned Qiskit
versions, tens of thousands of executions) and the venue, but they measured whether
**bugs reproduce**. They did not measure whether the **transpiler's output** — two-qubit
gate count, depth, semantic equivalence against the source circuit, compile time —
regresses across releases. That is a different dependent variable on a proven apparatus,
and their paper becomes the methodological citation rather than the competitor.

The honest risk on C2 is unchanged and stated in §3: environment reconstruction across
old SDK versions is the hard part, and Ohto et al.'s 93.6%-dependency-failure figure is
direct evidence of how hard. It is also direct evidence that the problem is real.

**Phase 0 for C2 before anything is built:** search specifically for a study treating
SDK version as the independent variable and transpiler output quality as the dependent
variable. If it exists, C1 is next in line.

---

## 48. ⭐⭐ PRIORITY A1 — A REAL WRONG DECISION IS DEMONSTRATED — 2026-09-03

**§45 A1 said: "no real decision has been shown to be wrong." That is no longer true.**

### The experiment, and why every previous one could not answer this

The real incident is **not** 2.0.0 → 2.0.2. Issue #14402 compares **Qiskit 1.4.3 against
2.0**, reporting `bv_n140-linear +46%`, `bv_n280-linear +44%`, `knn_341-linear +41%`.
Every measurement in this study up to now used the wrong version pair — 2.0.0 → 2.0.2,
whose real changes sit ~15 pp from the +10% cut and therefore flip nothing.

A Qiskit **1.4.3** environment was built and the full `linear` census run against it:
**58 of 58 circuits, 0 crashes, 51 with 12 seeds in both arms.** Direction fixed before
measuring: baseline = the earlier version.

Then, because 12 seeds proved too thin (every per-circuit error interval included zero),
**200 seeds per arm** were run on the five decisive circuits — the run D-1.1 asked for in
the first hostile review and never got.

### ⛔ The result. 200 seeds/arm, exact over 200³ = 8,000,000 sum-tuples per arm.

| circuit | true Δ | 95% CI | dist. to cut | truth | **error rate** | 95% CI | excludes 0 |
|---|---:|---|---:|---|---:|---|---|
| **`bv_n140`** | **+31.0%** | [+28.4, +33.8] | 21.0 pp | REGRESSION | **2.98%** | **[1.72, 4.99]** | **YES** |
| `bv_n30` | +24.2% | [+22.7, +25.7] | 14.2 pp | REGRESSION | 0.71% | [0.23, 1.43] | YES |
| `bv_n70` | +30.3% | [+28.5, +32.1] | 20.3 pp | REGRESSION | 0.15% | [0.02, 0.41] | YES |
| `adder_n64` | +10.8% | [+10.6, +11.1] | **0.8 pp** | REGRESSION | 21.60% | [15.2, 29.0] | YES ⚠ boundary |
| `qft_n29` | +0.5% | [−0.0, +1.0] | 9.5 pp | NO_REGRESSION | 0.01% FP | [0.00, 0.03] | YES |

> **`bv_n140` — a circuit issue #14402 itself names — carries a genuine +31.0%
> regression that Benchpress's 3-run unseeded protocol MISSES 2.98% of the time (95% CI
> 1.72%–4.99%).** The truth is 21 pp clear of the threshold, so this is not a boundary
> artifact, and the interval excludes zero. **That is category (4): an actual incorrect
> regression decision, on a real code change, in the real direction.**

`adder_n64` is excluded from the headline **despite the largest error rate (21.6%)**,
because at 0.8 pp from the cut it is exactly the D-1.6 boundary case this record refuses
to count. At 12 seeds it was the *only* candidate and its classification flipped between
interval methods (t-interval [+9.97%, +12.49%] includes the cut). The deep run resolves
the truth but not the objection.

### ⭐ And #14402's own headline number is itself a seed artifact

`bv_n140`'s true change is **+31.0%**. A single 3-run unseeded comparison — their exact
protocol — returns:

```
  min -10.5%   p5 +12.3%   p25 +22.9%   p50 +30.9%   p75 +39.6%   p95 +52.8%   max +100.0%
```

**A 48-point-wide 95% range on one number.** The issue's reported **+46.1% sits at the
88th percentile** (P(estimate ≥ 46.1%) = 0.122). Their figure is not wrong — it is one
draw from a distribution whose 95% range reaches **down to +9.3%, below their own
threshold**. The same circuit, same real regression, could have been reported as no
regression at all.

### The alternative explanation, tested and rejected

The discrepancy could be Benchpress version drift — the issue is from May 2025 and our
checkout is `b695f30e` (July 2026). If so, **all three** circuits would disagree:

| circuit | issue | ours (12 seeds) | diff | seed spread 1.4.3 | seed spread 2.0.0 |
|---|---:|---:|---:|---:|---:|
| `bv_n280` | +44.0% | +44.5% | **+0.5 pp** | 0.6% | 0.0% |
| `knn_341` | +41.0% | +43.4% | **+2.4 pp** | 1.0% | 0.4% |
| `bv_n140` | +46.1% | +35.2% | **−10.9 pp** | **44.4%** | **46.2%** |

**Agreement is excellent exactly where seed spread is near zero, and fails only where it
is ~45%.** Version drift is not selective like that. This is also the **first independent
reproduction of #14402's numbers by anyone.**

### The five categories, scored

| # | category | status |
|---|---|---|
| 1 | seed variation observed | ESTABLISHED (§27, §28, §30) |
| 2 | measurement ambiguity | ESTABLISHED (§42, §47) |
| 3 | decision INSTABILITY | ESTABLISHED — 5/51 circuits, Wilson [4.3%, 21.0%] |
| 4 | **decision ERROR** | **ESTABLISHED — `bv_n140` 2.98% [1.72, 4.99], non-boundary** |
| 5 | causal attribution to a commit | **NOT ATTEMPTED, NOT CLAIMED** |

### ⚠ What must be said with it

1. **Pairing does not fix this.** `seed_transpiler` gives P(call) 0.968 vs 0.980 unpaired
   on `bv_n140` at 12 seeds — pairing is *worse* on 3 of the 4 false-negative circuits.
   §42's 6.8× narrowing is about resolving power near the threshold; it does not follow
   that pairing reduces misses of large regressions, and here it does not.
2. **One version pair, one topology, five circuits at depth.** The 2.98% is `bv_n140` on
   `linear`, not a corpus rate.
3. **The 12-seed estimates were unreliable and are superseded.** `bv_n30` read 3.87% at
   n=12 and 0.71% at n=200 — a 5× error, though inside its own [0%, 20.5%] interval.
   Every per-circuit rate in §31–§38 carries that flaw.

---

## 47. PRIORITY A2 — the multiplicative model is REJECTED; the band survives anyway — 2026-09-03

**§45 A2:** §42's band assumes `new_i = old_i · r · ρ_i`. Never tested. Now tested three
ways on all three topologies, and the obvious test was refused as circular: setting
`r` to the observed change reproduces the data **by construction**, because ρ is defined
from it. That would pass on any data — the D-2.1 trap again.

### M1 — the assumption fails, and it fails differently by topology

| test | multiplicative predicts | `linear` | `square` | `heavy-hex` |
|---|---|---|---|---|
| Spearman(old, ratio) | ≈ 0 | **+0.734** | +0.084 | **+0.444** |
| sign matches additive `sign(−d)` | — | **17/19** | 17/30 | **29/32** |
| better fit (circuits with variance) | multiplicative | **add 16 : mult 3** | mult 16 : add 14 | **add 29 : mult 3** |
| CV(new)/CV(old) | 1.00 | **1.470** | 1.045 | 1.106 |
| SD(new)/SD(old) | additive predicts 1.00 | 1.295 | **1.005** | **1.044** |

**Rejected on `linear` and `heavy-hex`; not rejected on `square`.** The change behaves
more like a shift than a scaling on two of three topologies. ⚠ An earlier draft of
`model_check.py` asserted additive predicts a *negative* correlation — wrong. The sign
is `sign(−d)`, so for an improvement (d < 0) additive predicts **positive**. The test now
computes the expected sign per circuit from its own measured change.

### M3 — but the conclusion does not depend on it

Recomputing §42's band with an additive candidate `new_i = old_i + D + ε_i`:

| topology | multiplicative (§42) | additive | without replacement | **floor: additive + w/o repl** |
|---|---:|---:|---:|---:|
| `linear` | 2.55 pp | 2.24 pp | 2.42 pp | **2.20 pp** |
| `square` | 9.78 pp | 9.08 pp | 8.86 pp | **8.24 pp** |
| **`heavy-hex`** | **14.04 pp** | 12.70 pp | 12.71 pp | **11.50 pp** |

**Additive is narrower on all 86 heterogeneous circuits tested — never wider.** A second,
independent modelling choice found in the same pass (§46 attack 9: the enumeration draws
k seeds *with* replacement, but a maintainer runs k *different* seeds) moves it the same
way.

> **The honest statement: heavy-hex's band is 11.5–14.0 pp across every defensible
> modelling combination, and §42 reports the conservative end.** The topology ordering
> holds under all four. The residual error from the wrong model is **≤1.34 pp, always in
> the safe direction** — which is the quantification §45 A2 demanded.

---

## 46. ADVERSARIAL PASS — ten attacks on the apparatus itself — 2026-09-03

Not on the conclusions — on the machinery. Eight held, one found a real defect, one was
the model rejection above.

### ⛔ ATTACK 3 — the unseeded backend error rates. Nearly fatal, and it held.

`FlexibleBackend` draws error rates **randomly and unseeded**: two constructions with
identical arguments in one process give different rates, confirmed in all three Qiskit
versions. At optimization level 2 the layout passes score with error rates. The two
version arms built their backends separately. **If those rates fed the observable, every
between-version comparison in this study would be confounded.**

Tested directly: 6 circuits × 4 seeds × **4 independent backend constructions**, with the
draws verified distinct (4/4 per circuit).

```
  NO EFFECT: 0/24 (circuit,seed) cases changed with the error-rate draw
```

**The confound is dead and the test had power** — the negative condition was verified,
not assumed.

### The rest

| # | attack | result |
|---|---|---|
| 1 | Is `two_q_gate_type = cz` real, or is the output in another basis? | HELD — output contains only `cz`; no `cx`/`ecr`/`swap` in any version |
| 2 | Do the three Qiskit versions see the same backend? | HELD — identical 278-edge coupling map, sha `ef616023617489a3`, identical basis |
| 7 | Is the observable the same gate on every topology? | HELD — `cz` on all-to-all, square, heavy-hex, linear |
| 8 | Are consecutive seeds 1000–1011 independent? | HELD — lag-1 r = +0.11, −0.22, −0.15, −0.10; spreads match a scattered seed set |
| 9 | With- vs without-replacement k-tuples | REAL, quantified — see §47; conservative direction |
| — | Are the two Benchpress clones equivalent? | HELD — **58/58 circuits byte-identical** between the scratchpad clone and `Desktop\benchpress_test` |

### ⛔ ATTACK 10 — "the point estimates are EXACT" was FALSE

§38 claims exactness. `exact_call_rate` tested `b >= a·(1+t)`; the protocol's rule is
`(b−a)/a >= t`. **In floating point these are different expressions.** Brute-forced over
900 randomised cases they disagreed in **84**, and on real `adder_n64` data gave 0.905002
against 0.904327.

The magnitude never mattered — the *claim* did. Fixed exactly, not approximately: gate
counts are integers, so with `a = Sa/k`, `b = Sb/k` and `t = p/q` in lowest terms,

```
    (Sb − Sa)/Sa >= p/q   ⟺   q·Sb >= (q + p)·Sa
```

which is integer arithmetic with no rounding. Verified against exact-integer brute force:
**900 cases, 0 disagreements.** Non-integral inputs (§42's swept candidates) keep the
float path and are documented as such.

---

## 45. ⛔ GLOBAL ADVERSARIAL AUDIT — what is still wrong after all six priorities — 2026-09-03

Not a list of what was fixed. This is an attack on **what survives**, written as a
reviewer who wants to reject. Classification: **A fatal · B material · C minor ·
D cosmetic.**

### A — fatal if unaddressed

**A1. No real decision has been shown to be wrong, and the record's own bar says one
must be.** §22 set the gate: *"must demonstrate at least one real decision flip."*
After §41, in the direction that actually occurred, **zero circuits on any topology have
an unstable verdict**. What exists is a *sensitivity* result — a change of a certain
size would be unresolvable — not an observed error. Nobody has been shown to have made a
wrong call on Qiskit, and #14402's own cases (`bv_n140`, `bv_n280`, `knn_341`) have
never been reproduced as flips. **The engineering claim survives; the "broken toys"
framing does not.** Any writeup that implies a benchmark produced a wrong answer in the
field is unsupported by this evidence.

**A2. §42's band rests on a model, and it is the same species of model that killed
§32.** `new_i = old_i · r · ρ_i` assumes a compiler change scales the observable
multiplicatively, with a per-seed residual whose *shape* is borrowed from one version
pair and whose *magnitude* is swept freely. ρ is measured, which is the difference that
matters — but **nothing verifies that real compiler changes act multiplicatively on 2Q
counts**, and §31's own data shows the real change is heterogeneous in ways a single ρ
cannot capture. Stated honestly: the band measures *the decision rule's resolving power
under a measured noise model*, not *what a real PR would do*. A reviewer is entitled to
ask for one real code change to be run through it. That experiment does not exist.

**A3. One version pair, one SDK, one benchmark, one observable, one machine.**
Everything derives from Qiskit 2.0.0 vs 2.0.2, `count_ops()[cz]`, Benchpress
`b695f30e`, on one Windows box. §33 establishes from source that seven other gyms also
pass no seed, but **no other SDK has been measured**. Generalisation beyond Qiskit is
unsupported, and the cross-SDK work is deliberately deferred.

### B — material

**B1. `knn_n41` and `swap_test_n41` are not independent observations.** Their 2Q counts
are **identical seed-for-seed on all three topologies** (verified; their source QASM
files differ — 1,926 vs 1,592 bytes, different hashes — so this is structural, not a
duplicate file). Effective corpus size is therefore **≤51, not 52**, and every Wilson
interval computed on 52 is marginally too narrow. No other duplicate group exists. The
effect on the reported proportions is small but the assumption of independence is
formally violated and was not checked before this audit.

**B2. The +10% threshold is ours, not Benchpress's.** Benchpress defines **no**
regression threshold — it records counts. The decision rule under test is a
reconstruction of what a maintainer might apply, and #14402 never states one. Every
"false positive" in this study is relative to a rule nobody has adopted. This is
defensible only if stated in exactly those words.

**B3. Six circuits are excluded from every census, and they are the slow ones.**
`bwt_n37` (OOM), `multiplier_n350`, `multiplier_n400`, `square_root_n45`,
`square_root_n60`, `vqe_uccsd_n28` never reach 12 seeds. The two multipliers are the
**largest circuits in the corpus** (350 and 400 qubits), where routing entropy should be
greatest. Exclusion therefore most likely **understates** the effect — the conservative
direction — but the sample is a time-filtered convenience sample, not the corpus.

**B4. "Heavy-hex is IBM's actual hardware connectivity" was an overstatement.**
CORRECTED in §35 and §42 during this audit. `FlexibleBackend` calls
`rustworkx.generators.heavy_hex_graph(dim)` with `dim` solved to fit the circuit. It is
the *lattice family* IBM uses, generated synthetically, with no device coupling map and
no calibration data. The topology ordering is unaffected; the rhetorical weight is.

**B5. n=12 seeds is thin for everything except the medians.** Per-circuit band values
have no interval at all, and the aggregate intervals are biased low (D-8.4). The study
has never run the 200+ seeds D-1.1 asked for on even one circuit.

**B6. The record withdraws its own claims in sections a reader may never reach.**
`RESEARCH_LANDSCAPE.md` is 3,000+ lines, ordered newest-first, and §31–§38 still read as
live findings until §39–§41 overturn them. A reader who stops early leaves with
withdrawn numbers. Mitigated by the inventory's WITHDRAWN rows and this section, not
solved.

### C — minor

- **C1.** §30's within-version spread medians (linear 0.90%, square 5.94%, heavy-hex
  10.71%) carry no interval; they are descriptive medians and the inventory says so.
- **C2.** Four analyst choices are unregistered as choices: the 0.05/0.95 band cut, the
  3 pp boundary exclusion, the 5 pp "wide band" reporting line, and `min_seeds=12`.
  None is derived from anything; each was picked and then held fixed.
- **C3.** `inventory.py --scan` finds **92 percentage-shaped values** in the record that
  no inventory row claims. Most are prose, quoted external figures, or sit in superseded
  sections — but they are unchecked.
- **C4.** Bootstrap B is 2,000 for §38's intervals and 200 for §42's bands. Defensible on
  cost, inconsistent as method.

### D — cosmetic

- **D1.** Sections are numbered newest-first and §12 and §25 do not exist.
- **D2.** `results/summary/tmp_linear.csv` and `tmp_square.csv` are working files sitting
  in a results directory.

### What an honest abstract can say after this audit

> Qiskit's Benchpress benchmark suite compiles without setting `seed_transpiler`
> (source-verified across all eight SDK gyms). The transpiler seed is the dominant
> entropy source, confirmed by a cross-process control. On the 52-circuit
> `qasmbench-large` corpus, a 3-run unseeded comparison against a +10% threshold cannot
> resolve a change smaller than a median 14 pp window on a heavy-hex lattice; pairing
> the seeds narrows that window 6.8×. Between Qiskit 2.0.0 and 2.0.2, in the direction
> that actually occurred, no circuit's verdict was ambiguous — the exposure is to
> changes of a size that has not yet happened, not to one that has.

Every clause of that is measured, direction-free, and reproduces from the raw data via
`inventory.py --check`.

---

## 44. PRIORITIES 5 & 6 — the replication artifact RAN, and Benchpress is pinned — 2026-09-03

### D-5.2 — Benchpress was never versioned anywhere, and it is half the toolchain

Every provenance record named Benchpress by a **scratchpad path**. A path is not a
version. Benchpress supplies the circuits, the backend, the topologies and the
observable; our own rule (`flip_analysis.py`) is that a measurement file which cannot
name its own toolchain is not evidence. It named Qiskit and nothing else.

`sweep_bp.py` now emits, in every `env` record: the commit SHA, whether the working
tree is dirty, and sha256 of the five files this study calls into —
`flexible_backend.py`, `qasmbench.py`, `qiskit_gym/utils/io.py`, `config.py`,
`default.conf`. `pin_benchpress.py` writes `results/raw/benchpress_pin.json`, which adds
the sha256 of **all 58 `qasmbench-large` circuits** plus a single `corpus_sha256`.

```
benchpress commit : b695f30e83a32bac05b9b4d8e98d37ba9aae5236   (2026-07-29)
working tree dirty: False
circuits pinned   : 58
corpus sha256     : a02a41468e1a6a19505cc929f087c7f6008c6699724cfcaf84194c55e1330866
```

> ⚠ **The existing censuses predate the pin and do not carry it.** The clone was clean
> at this commit throughout and was never pulled, but for those files that is an
> assertion about our process, not a fact stamped into the data. It is recorded as such
> in `benchpress_pin.json` (`"applies_retroactively": false`). Runs made from now on
> carry it.

### ⛔ And a second half to D-5.2, found while fixing the first

`qasm_sha256` — present on 3,561 of 3,849 run rows and read as a circuit fingerprint —
**hashes the transpiled OUTPUT**, not the input. Checked directly: all 54 hashable
circuits have many distinct values across the corpus, because the output changes with
the seed. That field pins a *result*. **Nothing in the entire corpus ever pinned the
input circuits.** `sweep_bp.py` now records `input_qasm_sha256` from the file on disk
before Qiskit touches it, alongside the existing field, which keeps its meaning and its
continuity with the old data.

### D-5.1 — the replication artifact exists, and it was executed

Not a document describing a replication. `replication/replicate.py` + `expected.json` +
`REPLICATE.md`. Six circuits × 12 seeds × 2 Qiskit versions on `heavy-hex`, **about
three seconds per arm**, run from a clean state on 2026-09-03:

```
  per-seed values : 144/144 match exactly
  seed-sensitive  : 4/6 (bv_n30, knn_n31, adder_n28, dnn_n33)
  negative control: 2/6 constant across all 12 seeds (cat_n35, ghz_n40)
  every band matched the reference to within 0.01 pp   REPLICATION PASSED
```

It verifies the pin **before** measuring, then the circuit hashes, then determinism,
then seed sensitivity, then the negative control, then the derived statistic. `dnn_n33`
returns **12 distinct gate counts from 12 seeds**; `cat_n35` and `ghz_n40` return one.

**The failure path was tested, not assumed.** Corrupting one reference value and one
control band produces `2.0.2 bv_n30 seed 1003: 52 != 53` and
`cat_n35: unpaired band 0.00 pp != 4.00 pp`, exit code **1**; the clean run exits **0**.

Six circuits on one topology cannot support a corpus proportion, and `REPLICATE.md`
says so in a scope section. The full censuses remain the evidence; this is the door.

---

## 43. PRIORITY 3 — where k=3 came from, and it does not matter — 2026-09-03

### Provenance: external, half-verified. D-1.4 stands, narrowed.

Issue #14402, **verbatim from the issue itself**: *"This was verified by running
Benchpress several times for each version to get statistics. E.g. over the full test
suite the values returned for 3 runs was:"*. Three runs per version is stated by the
reporter, so k=3 is **not arbitrary and not ours**.

**Benchpress has no run-count knob at all.** Searched the whole repo for `n_runs`,
`num_runs`, `repeat`, and pytest `addoption`: nothing. k is not a property of the tool.

**What is still not established:** the issue calls the per-test figures *"the avg.
percent increase in 2Q gate counts"* without saying what the average is over. Whether
`bv_n140-linear +46%` is a 3-run mean, a single run, or something else **is not stated
in the issue**. We assume 3-run means. That assumption is load-bearing and is labelled
as an assumption wherever it appears.

### Sensitivity — every k requested is printed, none is selected

Swept on the direction-free band (§42), not on the old false-positive rate, because
that statistic inherited the §41 defect.

| topology | k=1 | k=2 | **k=3** | k=5 | pairing narrows by |
|---|---:|---:|---:|---:|---|
| `linear` | 4.48 pp | 3.46 pp | **2.55 pp** | 2.11 pp | 2.6× → 3.1× |
| `square` | 16.70 pp | 12.02 pp | **9.78 pp** | 7.55 pp | 4.0× → 4.1× |
| `heavy-hex` | 23.80 pp | 17.22 pp | **14.04 pp** | 10.86 pp | 7.0× → 6.9× |

Median unpaired ambiguity band, exact enumeration over all n^k index tuples.

**Three things, and none of them favours k=3.** The band shrinks monotonically as
1/√k — 23.80/√3 = 13.74 against a measured 14.04. k=3 sits on a smooth curve and is
neither the best nor the worst case. And **pairing's advantage is flat in k**: about
6.9× on heavy-hex whether you take one run or five, so the remedy does not depend on
the assumption we could not verify.

### The cost argument, re-derived from a statistic that shares no machinery with §34

To reach heavy-hex's *paired k=1* band of 3.40 pp by adding unseeded runs instead:
(23.80/3.40)² = **k ≈ 49**. §34 got "~50 runs" from per-circuit false-positive rates —
a different statistic, a different direction convention, the same number. That
agreement was not designed and is the strongest internal consistency check in the
study.

---

## 42. ⭐ THE DIRECTION-FREE REPLACEMENT — the ambiguity band — 2026-09-03

§41 kills every claim of the form *"X% of circuits are unstable"*. This is what is left,
and it is a better statistic than the one it replaces.

**Definition.** Sweep a synthetic true change `r` and find the interval of `r` over
which the call rate runs 0.05 → 0.95. That width — the **ambiguity band**, in
percentage points — is how large a change must be before the protocol can resolve it.
It has no baseline to pick, so it cannot have §41's defect.

The candidate is built as `new_i = old_i · r · ρ_i`, where ρ is the **measured** per-seed
change between 2.0.0 and 2.0.2, re-centred to mean 1. Both arms see the identical
candidate; only the comparison differs — independent index draws (Benchpress) versus one
index draw used on both sides (`seed_transpiler`). Exact enumeration over all 1,728
index tuples, bisection to 1e-4 in `r`.

| topology | unpaired median | paired median | narrowing | circuits with band ≥ 5 pp |
|---|---:|---:|---:|---|
| `linear` | 2.55 pp | 0.86 pp | 3.0× | 11/51 = 0.216 Wilson [0.125, 0.346] |
| `square` | 9.78 pp | 2.41 pp | 4.1× | 27/52 = 0.519 Wilson [0.387, 0.649] |
| **`heavy-hex`** | **14.04 pp** | **2.06 pp** | **6.8×** | 34/52 = 0.654 Wilson [0.518, 0.768] |

Seed bootstrap, B=200, **shared** resampling, 95%: heavy-hex unpaired median
[9.82, 13.70] pp, paired [1.60, 2.07] pp, fraction ≥5 pp [0.577, 0.673].

### ⚠ Three things that must be said with it

1. **The medians exclude the degenerate circuits, and that halves the apparent
   benefit.** 20 of 52 heavy-hex circuits (27 of 51 on linear) are byte-identical at
   every seed between the two versions. For those ρ ≡ 1, so the paired band is 0.00 pp
   **by construction** — the same identity that invalidated §32. Counting them would
   restate the tautology. Every figure above is on the heterogeneous subset.
2. **Pairing does not always help.** On `linear`, five circuits — `bv_n280`, `cc_n151`,
   `cc_n301`, `cc_n32`, `cc_n64` — have paired bands equal to their unpaired bands
   (`cc_n32`: 17.25 pp both ways). Where the version change itself is strongly
   seed-dependent, pairing removes nothing.
3. **The bootstrap is biased low for this statistic.** Resampling seeds with
   replacement duplicates draws and shrinks the empirical spread, so the intervals sit
   below the point estimate (square: point 9.78 pp, interval [6.99, 9.85]). Read them
   as a floor, not as symmetric error bars.

### The claim, stated so it cannot be dismissed on direction

> On `heavy-hex`, the lattice family IBM's hardware uses, Benchpress's unseeded 3-run
> protocol
> cannot resolve a change smaller than a **median 14.0 pp wide window** around its own
> +10% decision threshold. Passing `seed_transpiler` narrows that window **6.8×**, on
> the circuits where the comparison is a measurement rather than an identity.

No version is baseline. No pull request is implicated. Nothing depends on which of the
two Qiskit releases came first.

---

## 41. ⛔⛔ PRIORITY 2 SIDE-EFFECT — the corpus headline is a DIRECTION ARTIFACT — 2026-09-03

**This is the most serious defect found in the study, and it was found by building the
fix for a smaller one.** It supersedes §38's surviving claim, §37, §36 and §35.

`paired.py --measure` was written to compare paired against unpaired on real data. Run
in the historically real direction — 2.0.0 as baseline, 2.0.2 as candidate — it returned
**zero unstable circuits on every topology**, flatly contradicting §38's 14/52 on
heavy-hex. The CSVs explain why: `ci_heavy-hex.csv` records `qiskit_old = 2.0.2`,
`qiskit_new = 2.0.0`. **The entire flip analysis was run with the newer release as the
baseline and the older one as the candidate, and the record never says so.**

Same data, same circuits, same threshold, arms swapped:

| topology | direction | circuits | UNSTABLE | boundary | genuine | mean FP |
|---|---|---:|---:|---:|---:|---:|
| `linear` | 2.0.0 → 2.0.2 *(what happened)* | 51 | 1 | 0 | **1** | 0.0057 |
| `linear` | 2.0.2 → 2.0.0 *(what was run)* | 51 | 5 | 3 | **2** | 0.0290 |
| `square` | 2.0.0 → 2.0.2 | 52 | 0 | 0 | **0** | 0.0012 |
| `square` | 2.0.2 → 2.0.0 | 52 | 15 | 5 | **10** | 0.0605 |
| **`heavy-hex`** | **2.0.0 → 2.0.2** | 52 | **0** | 0 | **0** | 0.0013 |
| **`heavy-hex`** | **2.0.2 → 2.0.0** | 52 | 24 | 10 | **14** | 0.1074 |

### The cause is arithmetic, and it generalises D-1.6 to the whole corpus

A one-sided rule "flag if the candidate is ≥ +10%" measures the **distance from the true
change to the cut**. 2.0.2 reduced 2-qubit counts on most circuits, so forward the
changes sit at −4% to −6% — fifteen points from +10%, unreachable by seed noise.
Reversed, the same circuits sit at +4% to +6%, five points away, and seed noise reaches
it often:

| circuit | forward Δ | forward P | reverse Δ | reverse P |
|---|---:|---:|---:|---:|
| `cc_n32` | −5.9% | 0.030 | +6.3% | **0.344** |
| `bv_n140` | −4.7% | 0.007 | +4.9% | **0.220** |
| `bv_n280` | −3.6% | 0.003 | +3.7% | **0.112** |
| `bv_n30` | −8.0% | 0.011 | +8.6% | **0.458** |

D-1.6 said three of five unstable circuits sat on the cut. It is worse than that: **the
instability rate is a function of where this particular version pair happened to land
relative to the threshold.** It is not a property of the harness, the corpus, or the
topology.

### ⛔ Withdrawn

> *"On heavy-hex, 26.9% of circuits (95% CI 16.8%–40.3%) have a regression verdict that
> depends on which seeds were drawn"* — **WITHDRAWN.** In the direction that actually
> occurred the figure is **0 of 52**. The 26.9% is conditional on treating 2.0.2 as
> baseline, which the record never disclosed.

The topology *ordering* (linear < square < heavy-hex) survives, because §42 reproduces
it from a statistic with no direction at all. The **proportions do not**, in either
direction: forward they are ~0 and say nothing; reversed they describe an accident of
this version pair.

**Not a fabrication and not a rigged direction** — 2.0.2 → 2.0.0 is a legitimate
question (a revert *is* a regression, and it is the same measured data). The defect is
that it was **run in one direction, reported without naming it, and interpreted as a
property of the benchmark.**

### What this does NOT touch

§28's cross-process entropy control, §30's within-version seed spread, the source
reading that no Benchpress gym passes `seed_transpiler`, and §44's replication are all
single-version or direction-free. **The mechanism is untouched. The consequence
measurement is rebuilt.**

---

## 40. PRIORITY 2 — the paired calibration column is a tautology. Withdrawn. — 2026-09-03

**D-2.1 / D-2.2 CONFIRMED, and the resolution is removal, not repair.**

`calibrate.py` built its paired arm from the same k indices on both sides:

```
a = (1/k) Σ_{i∈I} v_i
b = (1/k) Σ_{i∈I} v_i(1+e) = (1+e)·a        ⇒   (b−a)/a ≡ e
```

The decision rule `(b−a)/a ≥ t` therefore collapses to `e ≥ t`. **The column was the
indicator function `1[e ≥ t]`.** It never touched a compiler and did not depend on the
data.

`paired.py --prove` executes `calibrate.detect_rate` — the real function, imported, not
a copy — on four datasets that share nothing:

| true effect | `qft_n320` (real) | constant 1000s | 1 vs 10⁶ | uniform noise |
|---:|---:|---:|---:|---:|
| 0%, 2%, 5% | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| **10% = t** | 1.0000 | 1.0000 | **0.9300** | 1.0000 |
| 15%, 30% | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

The one row that moves is `e == t`, and exact rational arithmetic settles it:
`(b−a)/a = 1/10` exactly, so the true value is 1.000 and 0.9300 is float residue —
which also confirms §32's honesty note 2.

### ⛔ Withdrawn with it

> §32: *"passing `seed_transpiler` removes every false positive across all 51 circuits
> and raises power at every effect size"* — **WITHDRAWN.**
> §34: *"Pairing achieves 0.0% at k=1"* — **WITHDRAWN.**

Neither is a measurement. Both restate `1[e ≥ t]`.

### The resolution

**Removed, not repaired.** `calibrate.py` no longer computes or emits a paired column,
and its docstring records why. Its **unpaired** column was always legitimate — there the
two sides are drawn independently and the ratio genuinely scatters — and is unchanged.
`detect_rate(..., paired=True)` is kept solely so the proof can execute the defect.
The already-written `results/summary/cal_*.csv` keep their paired columns as historical
record and are **not** rewritten; the record says they must not be quoted.

The honest replacement is §42, which builds the candidate arm from the measured
per-seed change so that the paired comparison carries real variance.

### The regression tests, and their mutation test

Four tests in `tests/test_harness.py` §8. The generic check is
`_is_data_independent(fn, datasets)` — a "measurement" whose answer does not move when
the data is replaced wholesale is not a measurement.

- `test_calibrate_paired_arm_is_provably_a_tautology` — documents the defect by
  executing it.
- `test_calibrate_no_longer_reports_a_paired_column` — runs `calibrate.main()` and
  inspects the CSV header.
- `test_real_paired_comparison_is_NOT_a_tautology` — the replacement must move when the
  per-seed change moves, and must land strictly between 0 and 1 on heterogeneous data.
- `test_paired_band_reports_the_identity_circuits_separately` — the band CSV must carry
  `rho_spread_pct`, and circuits with ρ spread 0 must have a paired band of exactly 0.

**Both were mutation-tested, as the reviewer mutation-tested ours.** Restoring the
paired column to `calibrate.py` fails test 2. Rebuilding the paired arm as a constant
multiple of `a` fails test 3 with *"a paired arm that only ever answers 0 or 1 is the
old defect"*. Suite: **16 passed, 1 skipped.**

---

## 39. ⛔ PRIORITY 4 — the "single commit" claim is FALSE — 2026-09-03

**D-1.5 CONFIRMED.** §31 asserted that *"2.0.0 vs 2.0.2 isolates a single commit —
PR #14417"*. Verified against the GitHub compare API for `Qiskit/qiskit`, tags
`2.0.0...2.0.2`:

```
total commits between tags: 31
files changed:              64
```

**Thirty-one commits, sixty-four files. The claim is withdrawn.**

### ⛔ And one of the 31 touches the pass under study

```
Fix circuit-metadata propagation in `SabreLayout` (#14186) (#14189)
```

**`SabreLayout` is the layout/routing pass whose stochastic behaviour is this entire
study's subject.** A change to it lies between the two versions being compared.

Whether #14186 alters routing *decisions* (as opposed to metadata carried alongside
them) is **not established** and must not be assumed either way. But its presence means:

1. The "true effect" attributed to `ConsolidateBlocks` (#14417) throughout §31, §36 and
   §37 is a **mixture of ≥31 changes**, not one.
2. §31's positive control — *"24 circuits register the genuine ConsolidateBlocks
   regression"* — **cannot attribute those 24 to #14417**. They register *some*
   difference between 2.0.0 and 2.0.2.
3. Every `mean_change_pct` in every flip table is a between-version difference, **not a
   single-commit effect.**

### What this does and does not break

**Does NOT break:** the seed-variance measurements themselves (§30, §35, §37, §38).
Those are *within-version* — spread across seeds at a fixed Qiskit version — and no
version-comparison claim enters them. The corpus proportions and their Wilson intervals
in §38 stand.

**Does break:** any sentence attributing a measured change to PR #14417 specifically,
and the framing of 2.0.0→2.0.2 as a controlled single-variable comparison. It is a
two-patch-release comparison with a known routing-adjacent change inside it.

### Required corrections

- Replace "isolates a single commit" with "spans 31 commits including a `SabreLayout`
  change" wherever it appears.
- Rename "true effect" → **"between-version change"** in all flip tables and prose.
- Downgrade the positive control from *"detects the ConsolidateBlocks regression"* to
  *"detects the aggregate 2.0.0→2.0.2 difference"*.
- If a genuinely single-commit comparison is wanted, it must be built from adjacent
  commits on `main`, not from release tags.

**Evidence recorded:** `https://api.github.com/repos/Qiskit/qiskit/compare/2.0.0...2.0.2`,
retrieved 2026-09-03, 31 commits / 64 files.

---

## 38. ⛔ PRIORITY 1 — CONFIDENCE INTERVALS. The headline does not survive. — 2026-09-03

`intervals.py`. Resolves **D-1.1**, and it is the most consequential correction in the
study.

### Method, chosen once and applied everywhere

**Point estimates are EXACT, not bootstrapped.** For k runs per version and n seeds
there are n^k possible means per side (1,728 for k=3, n=12). The call rate is
`(1/N²)·Σ_a |{b : b ≥ a(1+t)}|` — one sort plus one `searchsorted`. This removes
bootstrap noise from the estimate entirely and reproduces the reviewer's independent
exact figure (0.2710 vs our earlier bootstrap's 0.2705).

**Intervals resample THE SEEDS, not the iterations.** The bootstrap over draw-pairs only
describes behaviour *given* the 12 seeds we ran; the actual sampling error is which 12
seeds were drawn. Percentile bootstrap, **B = 2,000**, 95% interval. Chosen because the
statistic is a bounded proportion with no closed form here, Wald intervals fail near 0
(several rates are near 0), and §30 measured these distributions as strongly non-normal
(`cc_n64` skew +2.99, Shapiro p = 0) so no distributional assumption is safe.

For simple counts over circuits, **Wilson score intervals** — also asymmetric, also
valid near the bounds. Labelled as such in the CSVs.

### ⛔ The per-circuit rates are NOT interpretable at 12 seeds

| topology | circuit | true Δ | P(call) | **95% CI** | width |
|---|---|---:|---:|---|---:|
| linear | `qft_n320` | +0.0% | 0.271 | **[0.017, 0.631]** | 0.615 |
| linear | `bv_n30` | +22.4% | 0.930 | [0.702, 1.000] | 0.298 |
| heavy-hex | `cc_n32` | +6.3% | 0.344 | [0.066, 0.744] | 0.678 |
| heavy-hex | `bv_n140` | +4.9% | 0.220 | [0.026, 0.601] | 0.575 |
| square | `bv_n280` | +2.2% | 0.061 | [0.000, 0.279] | 0.279 |

**Interval widths run 0.25 to 0.68. Lower bounds sit at or near zero.**

> **The claim "`qft_n320` has a 27% false-positive rate" is WITHDRAWN.** Its interval is
> [1.7%, 63.1%]. Every sentence in this record quoting a per-circuit probability to
> three decimals overstated what 12 observations can support, and every such sentence is
> superseded by this section.

### ✅ What survives: the corpus-level proportion, and the topology ordering

| topology | genuine unstable / circuits | proportion | **95% Wilson CI** |
|---|---|---:|---|
| `linear` | 2 / 51 | 0.039 | **[0.011, 0.132]** |
| `square` | 10 / 52 | 0.192 | **[0.108, 0.319]** |
| **`heavy-hex`** | **14 / 52** | **0.269** | **[0.168, 0.403]** |

**`linear`'s interval [0.011, 0.132] and `heavy-hex`'s [0.168, 0.403] do not overlap.**
The topology ordering is supported by the data, not an artifact of point estimates.

### The restructured claim

**Not:** *"this circuit is miscalled 27% of the time"* — unsupportable at n=12.

**But:** *"on heavy-hex, IBM's own hardware connectivity, 26.9% of circuits (95% CI
16.8%–40.3%) have a regression verdict that depends on which seeds were drawn, after
excluding circuits whose true effect lies within 3 pp of the decision threshold."*

The per-circuit rates are individually noise. **The fraction of the corpus affected is
the finding**, and it is the quantity with a usable interval.

### Note on the small count difference vs §37

§37 reported 15 genuine on heavy-hex; this section reports 14. `flip_analysis.py`
bootstraps and includes circuits with ≥2 seeds; `intervals.py` computes exactly and
requires ≥12 seeds in **both** arms. **`intervals.py` is authoritative** — the exact
computation and the stricter inclusion rule are both improvements. §37's counts are
superseded.

### Still open in Priority 1

- [ ] Machine-checkable inventory of every probability in the repository and its CI.
- [ ] §32's calibration rates (FP/FN by effect size) have no intervals yet.
- [ ] §34's runs-sensitivity table has no intervals yet.

---

## 37. ALL THREE ROUTED TOPOLOGIES — complete, and heavy-hex is the worst — 2026-09-03

All four censuses finished: `square` and `heavy-hex` on 2.0.0 and 2.0.2, 58 circuits ×
12 seeds each, **0 crashes across all four**. `all-to-all` needs no run (routing-free,
verified constant, §27).

### Seed spread by topology, Qiskit 2.0.2

| topology | <1% | 1–5% | **≥5%** | median spread | max |
|---|---:|---:|---:|---:|---:|
| `linear` | 31 | 12 | 14 | 0.87% | 106.92% |
| `square` | 21 | 8 | 29 | 4.70% | 32.71% |
| **`heavy-hex`** | 17 | 4 | **37** | **10.11%** | 53.68% |

**On heavy-hex, 37 of 58 circuits exceed 5% seed spread and the median circuit varies by
over 10%.**

### Decision instability, D-1.6 boundary filter applied

| topology | UNSTABLE (k=3) | boundary artifact | **genuine** |
|---|---:|---:|---:|
| `linear` | 5 | 3 | **2** |
| `square` | 15 | 5 | **10** |
| **`heavy-hex`** | **26** | 11 | **15** |

### ⭐ Why heavy-hex is the operationally important case

**Heavy-hex is the lattice family IBM's hardware uses — but Benchpress builds it
synthetically, not from a device.** ⚠ CORRECTED 2026-09-03 (§45 B4): `FlexibleBackend`
calls `rustworkx.generators.heavy_hex_graph(dim)` with `dim` solved to fit the circuit.
It is not an IBM device coupling map and carries no device's calibration. `linear` and
`square` are abstract
stress topologies; heavy-hex is what real IBM devices are. It is also the topology where
the regression protocol is least reliable.

### The pattern across topologies — instability is not driven by spread alone

`linear` has the **largest** single spread (106.9%) and the **fewest** genuine unstable
verdicts (2). `heavy-hex` has a smaller maximum (53.7%) and the **most** (15). The reason
is visible in the data: on `linear` the ConsolidateBlocks effect is large (24 stable
regressions, most circuits clearly over the cut), while on `heavy-hex` the true effect is
small — mostly +3% to +10% — and the noise is high.

**Verdicts become unreliable where the true effect is comparable to the noise, not where
the noise is largest.** That is why §31's threshold-table reasoning was wrong in the way
D-1.7 identified, and it is the correct general statement.

### #14402's own circuits, across topologies

| circuit | reported in #14402 | genuine unstable on |
|---|---|---|
| `bv_n140` | ✅ +46% | `square` (+3.0%, P=0.12), `heavy-hex` (+4.9%, P=0.22) |
| `bv_n280` | ✅ +44% | `square` (+2.2%, P=0.07), `heavy-hex` (+3.7%, P=0.11) |
| `swap_test_n361` | used by `mtreinish` as **evidence the fix worked** | `heavy-hex` (+5.7%, P=0.10) |

`swap_test_n361` is the test `mtreinish` cited in the issue thread — *"2334 on my old run
with 2.0.0 and 1622 in my new run today"* — to demonstrate #14417 had fixed the
regression. On heavy-hex that same test's verdict is seed-dependent 10% of the time.

**This retires D-1.9 properly.** The evidence no longer rests on `qft_n320`, a circuit
nobody implicated. It rests on the circuits the maintainers themselves reported, and on
the one they used to close the issue.

### Limits

1. 12 seeds per circuit; **D-1.1's interval problem is unaddressed for every P value in
   this section.** No confidence intervals have been computed.
2. The 3 pp boundary band is a judgement; raw tables are committed so it can be re-cut.
3. Census coverage differs between arms in places (§30 table).
4. D-1.4 (k=3 assumed), D-1.5 (single-commit unverified), D-2.1/2.2, D-5.1, D-5.2 all
   remain open and gate any writeup.

---

## 36. SQUARE FLIP ANALYSIS — and the review's D-1.6 applied to both topologies — 2026-09-03

`flip_square_q202_vs_q200.csv`. Same pre-registered rule as §31, threshold +10%,
3 runs/version, 2,000 bootstrap draws.

| topology | STABLE_REG | STABLE_CLEAN | **UNSTABLE (k=3)** | UNSTABLE (k=1) |
|---|---:|---:|---:|---:|
| `linear` | 24 | 27 | **5** | 8 |
| `square` | **0** | 41 | **15** | 24 |

**The decision failure reproduces on a second routed topology and is 3× more common
there.** Note `square` has **zero** stable regressions: the ConsolidateBlocks effect is
weaker there (most true changes <10%), while the noise is higher (§35) — weaker signal
plus louder noise is precisely the regime where verdicts become unreliable.

### ⚠ D-1.6 applied — boundary artifacts separated from genuine false positives

The review's D-1.6 is correct and is now enforced: *a threshold rule is unstable near
its threshold; that is arithmetic, not a finding about Benchpress.* Circuits whose true
effect lies within 3 pp of the 10% cut are **boundary artifacts** and are excluded from
the claim.

| topology | UNSTABLE | boundary (excluded) | **genuine** |
|---|---:|---:|---:|
| `linear` | 5 | 3 | **2** |
| `square` | 15 | 5 | **10** |

**This weakens §31 and strengthens §36.** §31's "5 of 57" was carried by 3 boundary
cases and 2 real ones — exactly as the review said. The square result survives the same
filter with 10 of 15 intact.

### ⭐ The genuine square cases — and they include #14402's own circuits

| circuit | true change | P(called ≥10% regression) | distance from cut |
|---|---:|---:|---:|
| `bv_n30` | +6.3% | **0.31** | 3.7 pp |
| `bv_n70` | +4.0% | **0.21** | 6.0 pp |
| `cc_n32` | +3.9% | 0.13 | 6.1 pp |
| **`bv_n140`** | **+3.0%** | **0.12** | 7.0 pp |
| `swap_test_n83` | +6.2% | 0.11 | 3.8 pp |
| `swap_test_n115` | +6.3% | 0.10 | 3.7 pp |
| `cc_n64` | +5.0% | 0.10 | 5.0 pp |
| **`bv_n280`** | **+2.2%** | **0.07** | 7.8 pp |
| `knn_129` | +5.3% | 0.06 | 4.7 pp |
| `adder_n118` | +5.9% | 0.06 | 4.1 pp |

### This answers the review's D-1.9

D-1.9 objected — correctly — that `qft_n320` **is not among #14402's reported cases**
(`bv_n140-linear`, `bv_n280-linear`, `knn_341-linear`), so the flagship example was a
circuit nobody ever miscalled.

**`bv_n140` and `bv_n280` are two of those three**, and on `square` both are genuine
sub-threshold false positives: real changes of +3.0% and +2.2%, reported as double-digit
regressions 12% and 7% of the time.

**The strongest evidence is therefore not the circuit the record has been leading with,
and not on the topology it has been analysing.** §31's framing should be demoted and
this section promoted.

### Limits, stated with the same discipline

1. `square` still has only 12 seeds per circuit; D-1.1's interval problem applies here
   too and no interval has yet been computed for these P values.
2. The 3 pp boundary band is a judgement, not a derived quantity. A different band moves
   the genuine/boundary split; the raw table is given so anyone can re-cut it.
3. The 2.0.0 square census covers **53** circuits to 2.0.2's 58 (§30 table) — coverage
   differs between arms and has not been reconciled.
4. Still unaddressed from DEFECTS.md: D-1.4 (k=3 assumed), D-1.5 (single-commit
   unverified), D-2.1/2.2 (paired column tautological), D-5.1 (replication artifact
   missing), D-5.2 (Benchpress unpinned).

---

## 35. TOPOLOGY SENSITIVITY — not a `linear` artifact; worse on `square` — 2026-09-03

Qiskit 2.0.2, 58 circuits, 12 seeds, Benchpress apparatus. Both topologies are members
of `Configuration.options["general"]["abstract_topologies"]`, so both are part of the
suite as shipped.

| topology | <1% | 1–5% | **≥5%** | median spread | max spread | source file |
|---|---:|---:|---:|---:|---:|---|
| `linear` | 31 | 12 | **14** | 0.87% | 106.92% | `bp_large_linear_q202.jsonl` |
| **`square`** | 21 | 8 | **29** | **4.70%** | 32.71% | `bp_large_square_q202.jsonl` |

### The "it's only linear" objection is dead

**On `square`, 29 of 58 circuits — more than half — show ≥5% seed spread, against 14 on
`linear`. The median spread is 5.4× higher.** The effect is not confined to the one
topology where #14402 reported its worst cases; it is *more widespread* on the other
routed topology tested.

The shape differs: `square` affects more circuits but has a smaller extreme
(32.7% vs 106.9%). Plausibly because a 2-D grid gives the router more freedom than a
line, so more circuits have multiple viable routings while no single circuit is as
catastrophically constrained as `qft_n320` on a line. **That explanation is a
conjecture and is not established.**

### ⚠ Provenance note — two `linear` censuses exist and they differ slightly

§30 reports 32/12/14 with median 0.77% from the **first** 2.0.2 linear census (587 run
rows). This section reports 31/12/14 with median 0.87% from the **re-run** with the
provenance fix (639 run rows). The difference is **which circuits hit their wall-clock
budget**, not the measurements — values for a given (circuit, seed) are deterministic
and reproduce across machines (§29).

**This is the sample-reproducibility limitation stated in the method: our harness is
value-reproducible but not sample-reproducible, because the per-circuit budget is a time
budget.** Every figure must therefore cite its source file. The re-run file
(`bp_large_linear_q202.jsonl`, qiskit_version recorded) is the one to use going forward,
since the earlier file cannot name its own toolchain.

### Still outstanding

- [ ] `square` on 2.0.0 → enables the flip analysis on a second topology
- [ ] `heavy-hex` on both versions → the third routed topology
- [ ] `all-to-all` needs no run: routing-free, verified constant (§27)

---

## 34. ⭐ RUNS SENSITIVITY AND AGGREGATE MASKING — the practical result — 2026-09-03

Two questions, answered from the existing 2.0.2 linear census with no new
transpilation: *how many runs does the unseeded protocol need?* and *does the
suite-level mean hide per-circuit failure?*

False-positive rate at **zero real change**, threshold +10%, 51 circuits, 3,000 trials:

| circuit | k=1 | k=3 | k=5 | k=10 | k=20 | k=50 |
|---|---:|---:|---:|---:|---:|---:|
| `qft_n320` | 25.0% | **27.3%** | 21.3% | 12.8% | **5.2%** | 0.8% |
| `cc_n64` | 8.3% | 19.2% | 4.2% | 2.3% | 0.3% | 0.0% |
| `bv_n140` | 29.4% | 17.4% | 12.4% | 5.5% | 0.9% | 0.0% |
| `bv_n70` | 23.1% | 15.0% | 8.8% | 2.9% | 0.1% | 0.0% |
| `cc_n32` | 9.2% | 11.8% | 4.0% | 1.0% | 0.1% | 0.0% |
| `bv_n30` | 20.5% | 12.6% | 8.2% | 2.4% | 0.4% | 0.0% |
| **SUITE MEAN** | **2.7%** | **2.1%** | **1.2%** | **0.5%** | **0.1%** | **0.0%** |
| circuits still ≥5% FP | 8/51 | 6/51 | 4/51 | 2/51 | 1/51 | 0/51 |

### ⚠ Aggregate masking is severe and is a reporting trap

**At the real protocol (k=3) the suite mean is 2.1% — which reads as acceptable — while
`qft_n320` sits at 27.3%, thirteen times worse.** At k=20 the suite mean is 0.14%,
which reads as essentially perfect, and that circuit is still wrong 5.2% of the time.

A benchmark that reports suite-level aggregates can therefore look healthy while
individual circuits are unusable for regression detection. **Any published summary
statistic here understates the per-circuit error by more than an order of magnitude.**

### The cost argument — this is the sentence for the maintainers

**~50 runs per version are needed before every circuit falls below a 5% false-positive
rate.** `nonhermitian` states in #14402 that a full suite run takes *"about 2 hours
each"*. Fifty runs per version is therefore on the order of **200 hours of compute for a
single version comparison.**

**Pairing achieves 0.0% at k=1.** One `seed_transpiler` argument, one run per version,
outperforms fifty unseeded runs — at 1/50th the compute.

### ⚠ An unexplained non-monotonicity — reported, not explained

For three of the six worst circuits, **k=3 is WORSE than k=1**: `cc_n64` 8.3% → 19.2%,
`cc_n32` 9.2% → 11.8%, `qft_n320` 25.0% → 27.3%. With 3,000 trials the standard error is
≈0.7%, so these are real, not sampling noise.

Averaging more draws would normally reduce the false-positive rate monotonically. It
does not here at small k. These circuits are strongly skewed (`cc_n64` skew **+2.99**,
§30), which is the obvious suspect — **but the mechanism is not established and is not
claimed.** It is flagged as an open question because "take more runs" is the intuitive
remedy and on this evidence it can make matters worse before it makes them better.

---

## 33. CROSS-SDK AUDIT — what the source establishes, and what it does not — 2026-09-03

Traced through the actual execution path in every gym's
`abstract_transpile/test_qasmbench.py` — the QASMBench comparison path. **Nothing below
is inferred from configuration files.**

### Q2 — which gyms pass an explicit compilation seed? **NONE.**

| gym | the compile call, as written | seed |
|---|---|---|
| `qiskit_gym` | `generate_preset_pass_manager(optimization_level=OPT, backend=backend)` → `pm.run(circuit)` | **none** |
| `tket_gym` | `backend.default_compilation_pass(optimisation_level=OPT)` → `pm.apply(new_circ)` | **none** |
| `bqskit_gym` | `compile(circuit, model=BACKEND, optimization_level=OPT, compiler=compiler)` | **none** |
| `staq_gym` | `subprocess.run(RUN_ARGS_COMMON + ["-m","--device",device,input_qasm_file])` | **none** |
| `qpanda_gym` | `pm.transpile(prog, topo, {}, OPT, basic_gates)` | **none** |
| `qiskit_transpiler_service_gym` | `TranspilerService(..., ai=True, optimization_level=OPT).run(circuit)` | **none** |
| `cirq_gym`, `braket_gym` | no compile call present — base class marks these *"Not implemented"* | n/a |

**An inconsistency inside a single SDK:** `bqskit_gym/device_transpile/test_summit.py`
passes **`seed=0`** to the same `compile()` function (lines ~179, ~201), while
`bqskit_gym/abstract_transpile/test_qasmbench.py` passes nothing (lines ~51, ~74, ~97).
So the omission is **not a uniform deliberate policy** — the same SDK is seeded in one
test family and unseeded in another. BQSKit's `compile()` accepting a `seed` also
establishes that it *has* stochastic components.

### Q1 — which SDKs are actually stochastic? Only one is established.

| SDK | status | basis |
|---|---|---|
| **Qiskit** | **STOCHASTIC — measured** | this study, 57 circuits, §30–31 |
| TKET | reported deterministic | Pati & Simmhan: *"TKET routing is deterministic (σ=0 across seeds)"* — **their measurement, at opt=0 and n=10, not ours** |
| BQSKit, Staq, QPanda, Transpiler Service | **UNKNOWN** | not measured; source cannot establish it |

**We must not claim the cross-SDK ranking is unreliable.** That requires knowing which
competitors are stochastic, and we do not.

### Q3 — unpaired draws?

The code passes no seed, so successive runs draw independently — established for Qiskit
by measurement. **Whether the published Nature Comp. Sci. comparison used a single run
per SDK is NOT established by the code** and must not be inferred. That is a property
of how the authors ran it, not of the repository.

### Q4 — can randomness change a ranking? A computable bound: the ambiguity window

If Qiskit is stochastic and a competitor is deterministic, the comparison is a random
draw against a constant. **Any competitor scoring inside Qiskit's own [min, max] beats
it on some runs and loses on others.** That window is computable from our data alone,
without needing the other SDKs:

| circuit | Qiskit min | max | median | **window as % of median** |
|---|---:|---:|---:|---:|
| `qft_n320` | 83,566 | 172,915 | 163,124 | **54.8%** |
| `bv_n140` | 226 | 379 | 316 | **48.5%** |
| `bv_n30` | 48 | 72 | 54 | **44.4%** |
| `cc_n64` | 126 | 178 | 126 | **41.3%** |
| `bv_n70` | 100 | 145 | 114 | **39.6%** |
| `cc_n32` | 64 | 96 | 91 | **35.2%** |
| `qft_n160` | 32,923 | 42,568 | 41,893 | **23.0%** |

**13 of 51 circuits have an ambiguity window ≥5% of their median.** Median window
across all 51: 0.92%.

**What this shows and what it does not.** It establishes that a window exists in which
the published ranking would be decided by the draw rather than by compiler quality, and
gives its width. **It does NOT show that any actual published ranking flipped** — that
would require the competitors' real scores, which we have not measured. The honest claim
is the window, not a flip.

### The next experiment this implies

Install TKET and BQSKit, run the same QASMBench circuits, and check how many
competitor scores land inside Qiskit's ambiguity window. **That converts a bound into a
count** — and it is the difference between "a ranking could be decided by noise" and
"these rankings were."

---

## 32. CALIBRATION — detection curves, and the fix quantified — 2026-09-03

`calibrate.py`. Both critics required this (§23 C4): not a demonstration but a
*calibrated* procedure with measured error rates. Injection is applied to the recorded
observable **after** compilation, per Gemini's §23 G3, so the effect size is exact by
construction and the optimiser cannot alter it.

**Scope claimed, precisely:** this calibrates the *decision procedure* under realistic
measured noise. It does **not** model how a real code change would interact with
routing. Those are different questions and only the first is claimed.

Qiskit 2.0.2, `linear`, 51 circuits with ≥12 seeds, 3 runs/version, 4,000 trials each,
threshold +10%.

| true effect | **unpaired** (what Benchpress does) | **paired** (with `seed_transpiler`) |
|---:|---:|---:|
| **0%** | **0.021** | **0.000** |
| 2% | 0.027 | 0.000 |
| 5% | 0.040 | 0.000 |
| 10% *(at threshold)* | **0.746** | 0.926 ⚠ |
| 15% | 0.959 | **1.000** |
| 20% | 0.977 | **1.000** |
| 30% | 0.994 | **1.000** |

### The average hides the damage — the tail is the finding

Mean false-positive rate at zero real change is 2.1%, which sounds tolerable. Per
circuit it is not:

| circuit | unpaired FP | paired FP |
|---|---:|---:|
| `qft_n320` | **0.272** | 0.000 |
| `cc_n64` | **0.184** | 0.000 |
| `bv_n140` | **0.180** | 0.000 |
| `bv_n70` | **0.150** | 0.000 |
| `cc_n32` | **0.129** | 0.000 |
| `bv_n30` | **0.127** | 0.000 |

**Six circuits exceed a 12% false-positive rate. All six go to exactly zero when
paired.** Quoting the 2.1% aggregate would understate the problem by an order of
magnitude on the affected circuits — a reporting trap worth naming in the paper.

### Power is also worse unpaired

At a **15%** true regression, unpaired **misses 4.1%**; paired misses none. At the
threshold itself, unpaired power is only **0.746** — a genuine one-in-four miss rate,
because the two sides are drawn independently and the ratio scatters around the cut.

### ⚠ Two honesty notes on our own analysis

1. **Paired FP = 0.000 at zero effect is ANALYTIC, not empirical.** Pairing makes the
   two sides identical by construction, so the ratio is exactly 0. That is precisely
   why pairing is the correct fix, but it is a mathematical fact, not a measurement,
   and must not be presented as a surprising result.
2. **Paired 0.926 at exactly 10% is a floating-point boundary artifact**, not a miss
   rate. Verified directly: `(b-a)/a` evaluates to `0.10000000000000002` for one worked
   example — above the cut — while other value sets round marginally below. In exact
   arithmetic the paired at-threshold row is 1.000. **The unpaired 0.746 on the same
   row is NOT an artifact**: there the two sides use independent draws, so the ratio
   genuinely scatters. Any published at-threshold figure needs a tolerance-aware
   comparison; the artifact touches only that row.

### What this adds to §31

§31 showed the failure happens on real data. §32 gives the rate as a function of true
effect size, and quantifies the remedy: **passing `seed_transpiler` removes every
false positive across all 51 circuits and raises power at every effect size.**

---

## 31. ⭐ THE DECISION FLIP — measured, both error types — 2026-09-03

The gating question is answered. **Seed variance changes regression verdicts on a real
IBM benchmark, at a measurable rate, using the exact protocol from issue #14402.**

### Design, pre-registered before the two-version data existed

The classification rule is written into `flip_analysis.py`'s docstring and was fixed
before either census was compared:

- regression call: `(new − old) / old ≥ 0.10` — matching #14402's *"there should not be
  double-digit gate count increases"*
- protocol simulated: **3 runs per version, averaged** — what `nonhermitian` actually did
- 2,000 bootstrap draws, RNG seeded 20260902 so the analysis is itself reproducible
- **STABLE_REGRESSION** ≥95% of draws call it · **STABLE_CLEAN** ≤5% · **UNSTABLE** between

**Versions: 2.0.0 vs 2.0.2**, which isolates a *single commit* — PR #14417, the
`ConsolidateBlocks` sentinel-string fix. Both censuses: 58 circuits, 12 seeds,
`linear`, opt 2, Benchpress apparatus, version guard armed, provenance recorded.
2.0.0 → 640 run rows, 0 crashes. 2.0.2 → 639 run rows.

### ✅ Positive control passes — real effects ARE reliably detected

Direction 2.0.2 → 2.0.0, so the known bug appears as an increase:

| verdict | circuits |
|---|---|
| **STABLE_REGRESSION** | **24** |
| STABLE_CLEAN | 27 |
| **UNSTABLE** | **5** |

24 circuits register the genuine ConsolidateBlocks regression on essentially every
draw. **The protocol is not broken — it detects real, large effects reliably.** That
matters: without this, "the benchmark is noisy" would be unfalsifiable hand-waving.

### ⭐ 5 of 57 circuits (8.8%) have a verdict that depends on the seed

All five have the **full 12 seeds in both arms** — none is a thin-sample artifact.

| circuit | old mean | new mean | true Δ | P(regression called) | error |
|---|---:|---:|---:|---:|---|
| `bv_n30` | 55.2 | 67.5 | **+22.4%** | 0.932 | **false negative 6.8%** — a real 22% regression missed 1 time in 15 |
| `adder_n64` | 755.2 | 835.8 | **+10.7%** | 0.803 | **false negative 19.7%** — a real regression missed 1 time in 5 |
| **`qft_n320`** | **147,718.4** | **147,718.4** | **0.00%** | **0.271** | **false positive 27.1%** |
| `multiplier_n75` | 23,589.9 | 25,355.9 | +7.5% | 0.270 | false positive 27.0% — a sub-threshold change reported as double-digit |
| `multiplier_n45` | — | — | +7.9% | 0.150 | false positive 15.0% — same |

### The cleanest single result in the study

**`qft_n320`'s two version means are identical to one decimal place: 147,718.4 and
147,718.4. Nothing changed between the two Qiskit versions for this circuit. The
#14402 protocol reports it as a double-digit regression 27% of the time.**

There is no real effect to flip. The false positive is generated entirely by
within-version seed variance: draw three low seeds on one side and three high on the
other, and a 10% "regression" appears out of nothing.

**Symmetry check:** running the comparison in the *other* direction (2.0.0 → 2.0.2)
gives `qft_n320` **P = 0.27 again**, with 0 stable regressions and 55 stable-clean —
exactly what pure noise with zero real change must do. A one-directional artifact would
have shown asymmetry. It does not.

### What is now established

> **On Qiskit's own Benchpress suite, comparing two Qiskit releases that differ by a
> single commit, the regression protocol used by Benchpress's own author produces
> false positives at rates up to 27% and false negatives at rates up to 20%, on
> 8.8% of the circuits tested — because compilation is unseeded.**

Both error types. Measured, not asserted. With a passing positive control.

### ⭐⭐ PAIRED vs UNPAIRED — the attack that made the finding stronger

**The obvious attack:** *"If you ran both versions with the same seed, the difference
would vanish — so this is an artifact of how you compared, not a property of the
benchmark."*

**The first half is true. The second half is exactly backwards, and testing it produced
the cleanest result in the study.**

Same seed, both versions, per circuit:

| circuit | identical value at same seed | paired change (min … max) | unpaired P(call ≥10%) |
|---|---|---|---|
| **`qft_n320`** | **12 / 12** | **+0.00% … +0.00%** | **0.271** |
| `multiplier_n75` | 0 / 12 | −7.50% … −6.25% | 0.270 |
| `bv_n30` | 0 / 12 | −27.27% … −7.69% | 0.932 |

`qft_n320` values, seeds 1000–1005:
```
2.0.0: 110278, 166776, 164943, 172915, 157814, 170592
2.0.2: 110278, 166776, 164943, 172915, 157814, 170592
```

**Seed-for-seed the two versions are byte-identical on this circuit. The correct answer
is "no change", and a paired comparison returns it every single time. Benchpress's
actual unpaired protocol returns "double-digit regression" 27% of the time.**

Why the attack fails: Benchpress **does not fix the seed**. Each run draws its own,
independently, on each version. So the draws genuinely *are* independent, and the
unpaired model is not our modelling choice — it is a faithful description of what their
code does. The paired result is the *counterfactual*: what they would get if they passed
`seed_transpiler`.

**This converts the study from criticism into a fix.** The entire 27% false-positive
rate on `qft_n320` is produced by omitting one keyword argument, and passing it
collapses the error to zero on that circuit.

`multiplier_n75` sharpens the point further: paired, the fix produces a tight,
consistent **−6.25% to −7.50%** — a real effect, correctly *below* a 10% threshold.
Unpaired, the same data yields a spurious double-digit call **27%** of the time. Pairing
does not merely reduce noise; it changes the verdict from wrong to right.

### ✅ Threshold sensitivity — the finding is not an artifact of choosing 10%

Direction 2.0.2 → 2.0.0, 3-run protocol, same data, threshold varied:

| threshold | STABLE_REGRESSION | STABLE_CLEAN | **UNSTABLE** |
|---:|---:|---:|---:|
| 5.0% | 26 | 23 | **7** |
| 7.5% | 26 | 24 | **6** |
| **10.0%** | 24 | 27 | **5** |
| 15.0% | 20 | 31 | **5** |
| 20.0% | 14 | 33 | **9** |
| 25.0% | 14 | 38 | **4** |
| 30.0% | 13 | 38 | **5** |

**At every threshold from 5% to 30%, 4–9 circuits (7–16% of 57) have a seed-dependent
verdict. It never reaches zero.** The 10% figure came from #14402's own wording
(*"double-digit gate count increases"*); the result does not depend on it. As the
threshold rises the stable-regression count falls monotonically (26 → 13), as it must,
while the unstable count stays in a narrow band — consistent with instability being
driven by within-version spread rather than by where the cut sits.

### Limits, stated before anyone else states them

1. 12 seeds per circuit per version; 5 circuits have thin arms (all STABLE_CLEAN, so
   they cannot inflate the headline, but they cannot be ruled *in* either).
2. One topology (`linear`) of Benchpress's four. All-to-all needs no routing and is
   known-constant; `square` and `heavy-hex` are untested.
3. 2.0.0 vs 2.0.2, not #14402's 1.4.3 vs 2.0. Chosen deliberately for the isolated
   commit; the original pair is confounded by BackendV1 removal and pass-manager
   changes (§23 G1).
4. The 10% threshold comes from #14402's own wording. Other thresholds will give other
   rates; a sensitivity sweep over the threshold is the obvious next analysis.
5. `qasmbench-large` only.

### Consequence

The study now has what both critics said it lacked. **This is no longer "the compiler
is stochastic", which Qiskit documents. It is "the documented stochasticity produces
wrong regression verdicts at a measured rate in IBM's own benchmark, and here is the
rate."**

---

## 30. MATCHED CENSUS — the phenomenon is confirmed, not invalidated — 2026-09-02

> ## ⛔ CORRECTED 2026-09-03 — this section did not reproduce from its own data
>
> The hostile review (DEFECTS.md **D-7.1 / D-7.2**) found that the numbers below
> described the **first** 2.0.2 census, while the file on disk is the **re-run** made to
> fix the provenance defect (§26). The aggregates were never recomputed.
>
> | | as originally written | **actual, regenerated from the named file** |
> |---|---|---|
> | circuits | 58 | **57** |
> | run rows | 587 | **639** |
> | budget stops | 7 | **6** |
> | crashes | 0 | **1** (`square_root_n60`) |
> | <1% / 1–5% / ≥5% | 32 / 12 / 14 | **31 / 12 / 14** |
> | median spread | 0.77% | **0.87%** |
>
> **This is the exact failure this project documents in others.** The original figures
> are left visible rather than silently swapped. A test now enforces regeneration
> (`test_summary_numbers_regenerate_from_raw`), and it caught a second instance
> immediately: the summary CSV had `multiplier_n75` min = 22,570 against a raw 22,568.
> All derived artifacts have been regenerated.

`census.py` (one OS process per circuit) → `sweep_bp.py`, Benchpress's own
`FlexibleBackend`, observable `count_ops().get("cz", 0)`, `optimization_level=2`,
`linear` topology, version guard armed.

### Distribution of seed-induced spread — regenerated, every row naming its file

| census | circuits | <1% | 1–5% | **≥5%** | median | max |
|---|---:|---:|---:|---:|---:|---:|
| `bp_large_linear_q200.jsonl` (2.0.0) | 58 | 34 | 15 | **9** | **0.10%** | 106.92% |
| `bp_large_linear_q202.jsonl` (2.0.2) | 57 | 31 | 12 | **14** | **0.87%** | 106.92% |
| `bp_large_square_q202.jsonl` (2.0.2) | 58 | 21 | 8 | **29** | 4.70% | 32.71% |
| `bp_large_square_q200.jsonl` (2.0.0) | 53 | 16 | 8 | **29** | 5.86% | 35.14% |
| `sweep_q2_0_2_large.jsonl` (§24, non-Benchpress apparatus) | 54 | 31 | 11 | 12 | 0.48% | 106.92% |

### ⭐ New observation the correction exposed — 2.0.2 is MORE seed-variable than 2.0.0

On `linear`, 2.0.0 has **9** circuits at ≥5% spread with a median of **0.10%**; 2.0.2 has
**14** with a median of **0.87%**. **The ConsolidateBlocks fix reduced gate counts and
appears to have increased seed spread.**

This was invisible until the correction forced the 2.0.0 census to be analysed on its own
rather than only as the "old" arm of a comparison. It is **an observation, not a claim** —
one topology, 12 seeds, and the two censuses differ in circuit coverage (58 vs 57), which
alone could move the bands.

### ⚠ D-7.3 — the §24-vs-§30 agreement was a tautology, not a validation

Seed-for-seed, **49 of the 53 shared circuits are byte-identical** between the §24 and
§30 files; only four `multiplier_*` circuits differ, by 2–70 gates. The original text
explained why the two *must* coincide (Benchpress's `linear` is `grid_graph(1, n)`, the
same graph as `CouplingMap.from_line(n)`) and then treated the coincidence as
confirmation. **It is one measurement run twice.** §26's earlier and more careful
statement — that §24's numbers "are not evidence about Benchpress's workload" — stands;
§30's upgrade of them to "validated measurement" is withdrawn.

**The matched apparatus confirms the phenomenon rather than invalidating it.** The two
instruments agree closely — as they should, since Benchpress's `linear` layout is
`rx.generators.grid_graph(1, n)`, the same graph as `CouplingMap.from_line(n)`, and for
circuits transpiled into the `cz` basis the two counting rules coincide. **§24 was not
wrong, it was merely not theirs.** It now stands as a validated measurement.

**Roughly one circuit in four is meaningfully seed-sensitive.**

| circuit | qubits | 2Q min | 2Q max | spread | CV | skew | Shapiro p |
|---|---:|---:|---:|---:|---:|---:|---:|
| `qft_n320` | 320 | 83,566 | 172,915 | **106.9%** | 19.8% | −1.14 | 0.007 |
| `bv_n140` | 140 | 226 | 379 | **67.7%** | 13.4% | −0.11 | 0.79 |
| `bv_n30` | 30 | 48 | 72 | **50.0%** | 11.5% | +1.51 | 0.017 |
| `cc_n32` | 32 | 64 | 96 | **50.0%** | 9.6% | −2.29 | 0.0006 |
| `bv_n70` | 70 | 100 | 145 | **45.0%** | 11.4% | +0.76 | 0.078 |
| `cc_n64` | 64 | 126 | 178 | **41.3%** | 11.3% | **+2.99** | **0.0** |
| `qft_n160` | 160 | 32,923 | 42,568 | **29.3%** | 6.4% | **−2.69** | **0.0** |

`qft_n320`'s compiled circuit **more than doubles** on seed choice alone.

### The distributions are not normal — which matters for the only published rule

`cc_n64` skew **+3.0**, `qft_n160` skew **−2.7**, both with Shapiro p ≈ 0. The only
published decision rule in this area (Pati & Simmhan, `gap > 2*pooled_std`) is
σ-based. On circuits shaped like these, a 2σ threshold is not calibrated — and
`jakelishman` asked in #14402 for *"statistical significance testing accounting for
non-normal distributions"* precisely because nobody knew the shape. **Now we do.**

### Harness defects found today — all fixed, all regression-tested

| # | defect | what it silently did |
|---|---|---|
| 1 | QASM-2 export gated the measurement | deleted 40 rows / 4 circuits — **the control-flow ones** |
| 2 | Rust OOM on `bwt_n37` aborted the process | lost 49 of 58 circuits — **the expensive ones** |
| 3 | relative interpreter path in the driver | lost everything, but loudly |
| 4 | merge stripped every child `env` record | **the merged file did not record its own Qiskit version** |

Defects 1, 2 and 4 degraded the data *quietly*, and 1 and 2 both biased the corpus
toward easy circuits — exactly the direction that would have understated the finding.
**`tests/test_harness.py`: 11 tests, one per defect plus the negative control and the
statistics.** Defect 4's test was initially too weak (it accepted any `env` row, which
the driver's own row satisfied); it was strengthened until it **failed on the defective
file**, then the defect was fixed.

### Where this leaves the study

**Established:** Benchpress compiles unseeded; the entropy source is the transpiler
seed (matched fresh-process arms, hash seed pinned); a fixed seed reproduces
bit-identically across two machines and two CPU vendors; independently replicated by a
third party; ~1 circuit in 4 shows ≥5% seed spread; several distributions are strongly
non-normal.

**The single remaining question, and it decides the paper:**

> **Can this variance flip a real version-to-version regression decision?**

---

## 29. INDEPENDENT REPLICATION — different machine, different CPU vendor — 2026-09-02

Executed by a third party (Gemini 3.1 Pro in an agentic environment) from a written
protocol, on their own hardware, with a fresh clone and a fresh environment. They were
told not to trust our numbers and to re-derive them.

**Their environment:** Windows 10, **AMD64 Family 26 Model 68 (AuthenticAMD)**,
Python 3.10.10, Qiskit 2.0.2 confirmed exact.
**Ours:** Windows 11, different CPU, Python 3.10.10, Qiskit 2.0.2.

| arm | theirs | ours |
|---|---|---|
| **unseeded**, 20 runs | 247–385, **15 distinct** | 244–340, **17 distinct** |
| **fixed seed 777**, 6 separate processes | **324, 324, 324, 324, 324, 324** | **324, 324, 324, 324, 324, 324** |

Their full unseeded sample:
`[247, 250, 252, 263, 270, 281, 282, 291, 301, 310, 316, 316, 316, 320, 320, 320, 341, 341, 364, 385]`

### What this establishes

1. **The qualitative result replicates independently.** Unseeded output varies widely;
   a fixed seed is perfectly constant across separate process invocations.
2. **Cross-machine, cross-CPU-vendor determinism.** A fixed `seed_transpiler` produces
   **the identical integer, 324**, on different hardware from a different vendor under a
   different Windows build. This is stronger than anything we could establish alone and
   it is exactly what a reviewer would demand.
3. Absolute unseeded values differ between machines, as they must — the two runs are
   different draws from the same distribution. Their range is in fact *wider* than ours
   (247–385 vs 244–340), so our number is not an outlier in the optimistic direction.

### Their criticism — judged

**Flaw 1: "You confounded the process model — unseeded ran as a loop in one process,
seeded ran as six separate processes."**
**PARTIALLY ACCEPTED — the flaw is in the protocol I wrote, not in the experiment I
ran.** `entropy_probe` (§28) ran **both** arms as fresh processes, six each, matched:
seeded `324×6`, unseeded `250, 320, 316, 316, 357, 261`. The process model was matched
there. But the replication protocol I sent described Arm 1 as an in-process loop and
Arm 2 as separate processes, which is an unmatched design and a sloppy instruction.
**Fix: publish only the matched-process comparison; rewrite the replication protocol so
both arms use identical process models.**

**Flaw 2: "`PYTHONHASHSEED=0` is superfluous and confounding — seeded runs give 324
even with it unset."**
**ACCEPTED, and their extra test is valuable.** They re-ran the seeded arm with
`PYTHONHASHSEED` unset (default randomised) and still got 324 every time. That is an
experiment we did not run and it **strengthens** the conclusion: hash-ordering is
irrelevant to this result, so the entropy isolation is cleaner than we claimed.
One correction to their framing: the variable was not added because we believed hash
order mattered — it was added because two independent critics demanded that control
(§28). Their result retires the concern properly, by measurement.

### Consequence for the claim set

The attribution — that the transpiler seed is the entropy source — now rests on:
- matched fresh-process arms on our machine (§28),
- a fixed seed reproducing bit-identically across **two machines and two CPU vendors**,
- and a third party showing the result survives with hash randomisation left on.

**This part of the study is now solid.** The weak point remains unchanged and unaddressed:
**no demonstrated decision flip.** Variance is established; consequence is not.

---

## 28. SECOND CRITIC ROUND — the attribution hole, and closing it — 2026-09-02

Both critics independently found **the same defect**, and it was real:

> **"Unseeded" does not prove SABRE is the entropy source.** Python hash randomisation
> (`PYTHONHASHSEED` → dict/set iteration order → DAG traversal order) or thread
> scheduling could be the actual driver. — *Gemini and ChatGPT, independently.*

ChatGPT's proposed kill experiment: fresh processes with hash seed and threading fixed,
unseeded vs explicitly seeded. *"If variability remains only in the former, your central
attribution is wrong."*

### The kill experiment — run, and the attribution survives

`bv_n140`, linear, opt 2, Qiskit 2.0.2, **a separate OS process per run**,
`PYTHONHASHSEED=0` pinned in every one:

| arm | values | distinct |
|---|---|---|
| fixed `seed_transpiler=777` | **324, 324, 324, 324, 324, 324** | **1** |
| unseeded | **250, 320, 316, 316, 357, 261** | **5** |

Fresh process both arms. Hash seed pinned both arms. Same backend construction, same
threading. **The only difference is whether a seed is supplied.**

**Conclusion: the entropy source is the transpiler seed.** Hash-ordering and
process-level state are excluded by construction, not by argument. The critics' defect
is closed by measurement.

Note also: within-process reasoning already pointed here — `PYTHONHASHSEED` is fixed
*within* a process, all 20 arm-1 runs were in one process, and arm A of `exp1` (fixed
seed, same process, repeated) was perfectly constant. The cross-process test removes
any remaining doubt about allocation-order effects.

### Backend refutation — challenged, verified, upheld

ChatGPT: *"identical output under fixed seed shows backend construction isn't observable
stochasticity, not that backend randomness cannot influence layout... hash/record the
complete Target/error-rate data each run."* **Accepted and done.**

Fingerprinted every gate's `error` and `duration` across the whole Target for two
`FlexibleBackend(140, "linear", control_flow=True)` instances:

```
backend A: c4970ae901fe6c4bd78b...
backend B: 8390c078be7eacb0c0d8...   DIFFERENT: True
```

The two backends **genuinely differ** in their random error rates, and still produce
identical compiled output under a fixed seed. **The refutation is valid** — it was not
an artifact of two identical backends. Had this come back `False`, `exp1` would have
proved nothing.

### Accepted without dispute

- **Negative control is weaker than claimed.** `all-to-all` bypasses routing entirely,
  so it shows the instrument does not *invent* variance — it does **not** control for
  routing stochasticity. The cross-process fixed-seed arm above is the stronger control
  and supersedes it. Wording corrected wherever `all-to-all` was described as
  controlling for routing.
- **Motivation is still the weak point** (both critics). Qiskit already documents that
  preset pass managers are stochastic and recommends `seed_transpiler`. #14402 supplies
  no false-positive example, because its cause was deterministic. **A demonstrated
  decision flip is required**, plus calibrated false-positive rates. This is the gating
  item before any writeup, and it is not yet done.
- **Synthetic regressions injected post-compilation test our statistics, not the
  compiler's response** (Gemini). Both are needed: post-compilation injection calibrates
  the detector; a real version pair (2.0.0 vs 2.0.2, isolating #14417) tests the
  compiler.

### What is now established versus still open

| claim | status |
|---|---|
| Benchpress's unseeded call returns 17 distinct 2Q counts in 20 runs on `bv_n140-linear`, 244–340 | **measured** |
| The entropy source is the transpiler seed | **established by cross-process test** |
| Backend error-rate randomness does not affect output | **established, backends verified different** |
| Instrument does not manufacture variance | **established** |
| Seed variance causes false regression calls in practice | **NOT established — gating item** |
| 2.0.2 → 2.5.2 stability change | **hypothesis, n=1 circuit** |
| #14402's 46% was seed-driven | **rejected — deterministic root cause** |

---

## 27. APPARATUS VALIDATED — and the strongest number yet — 2026-09-02

`exp2_equivalence.py`, Qiskit **2.0.2** (guard enforced), Benchpress `FlexibleBackend`,
opt level 2, observable `count_ops().get("cz", 0)`, circuit `bv_n140`.

### Negative control — PASS

`all-to-all` needs no routing, so a correct instrument must show zero variance.

| arm | result |
|---|---|
| Benchpress unseeded × 12 | **72 – 72**, 1 distinct |
| our seeded × 12 | **72 – 72**, 1 distinct |

Both arms constant. **The instrument does not manufacture variance.** Had this failed,
nothing else in this file would be trustworthy.

### Equivalence — PASS

`linear`, 20 runs per arm:

| arm | range | distinct |
|---|---|---|
| **Benchpress's exact unseeded call** | **244 – 340** | **17 / 20** |
| our seeded call | 226 – 379 | 15 / 20 |

The unseeded range is **contained inside** the seeded range. The paths agree: seeding
samples the same distribution an unseeded Benchpress run already draws from.

### ⭐ The narrowest, strongest statement available

Arm 1 uses **no seed argument, no reimplementation, and no interpretation.** It is
Benchpress's own call — `generate_preset_pass_manager(optimization_level=2,
backend=FlexibleBackend(140, "linear", control_flow=True))` — executed twenty times:

> **Benchpress's own unseeded transpilation of `bv_n140-linear` returns 17 different
> two-qubit gate counts in 20 runs, spanning 244 to 340 — a 39.3% spread.**

This requires no argument about apparatus fidelity, because it *is* their apparatus.
It is the sentence to defend, and everything else is supporting detail.

**Still not licensed by this:** that the 46% figure in #14402 was caused by seed
variance. #14402 had a verified deterministic root cause (§22 B2). The correspondence
in magnitude is a **hypothesis generated by the pilot**, not a finding, and the writeup
must say so in those words.

### Status of the apparatus

- [x] Censoring bug fixed — hashing is best-effort in `sweep_bp.py`; failure records
      `qasm_sha256: null` + `hash_error` and **keeps the row**.
- [x] Version guard on every measurement script, verified to abort on mismatch.
- [x] Benchpress's own backend, loader, topologies and observable imported, not
      reimplemented.
- [x] Negative control passes.
- [x] Equivalence check passes.
- [ ] Matched census across topologies and both versions — next.

---

## 26. BENCHPRESS APPARATUS — and an incident in our own instrument — 2026-09-02

### ⛔ INCIDENT — our environment drifted under us, mid-session

`uv pip install qiskit-ibm-runtime` **silently upgraded Qiskit 2.0.2 → 2.5.2** in
`envs/q2_0_2`. Experiment 1 ran and reported `qiskit=2.5.2` while the environment was
named for 2.0.2. Nothing was falsified — every artifact records its own version — but an
experiment executed against a version we did not intend.

**This is the exact failure class the project exists to detect, and it happened to us
inside one session.** It is recorded here rather than quietly fixed.

Two fixes, both applied:

1. **Pinned resolution.** `envs/bp202` installs `qiskit==2.0.2` *together with*
   `qiskit-ibm-runtime rustworkx scipy qiskit_qasm3_import` in one resolution, so the
   solver cannot upgrade Qiskit to satisfy a sibling. Result: qiskit 2.0.2 +
   qiskit-ibm-runtime 0.45.1.
2. **A refusal guard.** `--require-qiskit <version>` aborts before measuring if the
   running version differs. Verified: it correctly aborts on mismatch.
   **Every future measurement script gets this argument.**

### ✅ Backend randomness hypothesis — REFUTED, on both versions

`flexible_backend.py:111` passes no `seed` to `GenericBackendV2`
(`seed=None`, `noise_info=True` by default), so the Target's error rates are drawn
unseeded at construction. Since layout passes are error-rate aware, this *could* have
been a second uncontrolled randomness source.

`exp1_backend_randomness.py`, `bv_n140`, linear, opt 2, 10 repeats per arm:

| arm | 2.0.2 | 2.5.2 |
|---|---|---|
| **A** same backend, fixed seed (control) | 292 – 292, **0.00%** | 352 – 352, **0.00%** |
| **B** NEW backend each run, fixed seed | 292 – 292, **0.00%** | 352 – 352, **0.00%** |
| **C** same backend, varying seed | 232 – 337, **45.26%** | 347 – 362, **4.32%** |

**Arm B is flat. The hypothesis is refuted on both versions.** Constructing a fresh
`FlexibleBackend` does not change the compiled result. The suspicion was mine, the test
was designed so it could fail, and it did. Recorded as closed.

### ⭐ The headline number, now on Benchpress's own apparatus

Arm C, Qiskit **2.0.2**, using Benchpress's `FlexibleBackend(140, "linear",
control_flow=True)`, Benchpress's `optimization_level=2`, and Benchpress's own
observable `circuit.count_ops().get("cz", 0)`:

> **`bv_n140` ranges 232 – 337 two-qubit gates across 10 transpiler seeds — a 45.26%
> spread, 9 distinct values from 10 seeds.**
>
> **The regression reported for `bv_n140-linear` in issue #14402 was 46%.**

This is no longer my approximation of their setup. It is their backend, their
optimisation level, their counting semantics.

⚠ It remains **one circuit, 10 seeds, one version**. It is not a corpus claim.

### ⭐ An accidental clean comparison — 2.0.2 vs 2.5.2

The contamination incident produced a genuinely single-variable comparison: identical
script, identical backend, identical counting, identical seeds, identical repeats —
**only the Qiskit version differs.**

**Seed spread on `bv_n140` collapses from 45.26% (2.0.2) to 4.32% (2.5.2)** — roughly
a factor of ten more stable.

If that holds across the corpus it is a substantial and useful result: **Qiskit's
routing became dramatically more seed-stable between 2.0.2 and 2.5.2**, which nobody
has reported. It also means any seed-variance finding must state its version, because
the answer changes by an order of magnitude.

**Do not state this as a finding yet.** One circuit, 10 seeds, and the pair was produced
by accident rather than by design. It becomes a claim only after a census on both
versions with the guard in place.

### Corrected measurement path — differences from the earlier census

| element | earlier census (§24) | Benchpress-matched |
|---|---|---|
| backend | `CouplingMap.from_line(n)` | `FlexibleBackend(n, layout, control_flow=True)` |
| 2Q count | any 2-qubit operation | `count_ops().get(backend.two_q_gate_type, 0)` |
| loader | `qasm2.load` / `qasm3.load` | `QuantumCircuit.from_qasm_file` (their `qiskit_qasm_loader`) |
| version guard | none | `--require-qiskit` |

**§24's numbers are therefore relabelled *pre-Benchpress validation*, not Benchpress
results.** They stand as evidence that seed sensitivity exists under a reasonable
compiler configuration; they are not evidence about Benchpress's workload.

### Still to fix before the matched census

- [ ] **The censoring bug.** QASM-2 export must not gate a measurement — 40 rows were
      dropped and 4 circuits lost entirely because circuits with control flow cannot be
      serialised to QASM 2. Hash failure must record `qasm_sha256: null` and keep the
      row. **This preferentially deleted control-flow circuits, which is corpus bias
      created by the instrument.**
- [ ] Rebuild `sweep.py` on the matched path, with the version guard.
- [ ] Equivalence check on a known circuit before the full census.

---

## 24. FIRST MEASUREMENTS — Experiment 0 and the pilot — 2026-09-02

Code: `exp0_determinism.py`. Env: `envs/q2_0_2` (uv, Python 3.10.10, **Qiskit 2.0.2**),
16 CPUs, Windows. Circuits: the three worst-reported tests from issue #14402, taken from
the Benchpress clone. Config mirrors `default.conf`: `optimization_level=2`,
basis `[id, sx, x, rz, cz]`, **linear** topology.

⚠ **Deliberate deviation:** the coupling map is `CouplingMap.from_line(n)`, not
Benchpress's `FlexibleBackend`. Absolute counts therefore do **not** match Benchpress's.
Experiment 0 asks only about *variability*, not about reproducing their numbers.

### Result 1 — Gemini's threading hypothesis (§23 G2) is REJECTED by measurement

`bv_n140`, seed fixed at 12345, 5 repeats, both thread conditions:

| condition | distinct QASM hashes | 2Q count |
|---|---|---|
| `RAYON_NUM_THREADS` unset (16 cores) | **1** | 292 |
| `RAYON_NUM_THREADS=1` | **1** | 292 |

Bit-identical within each condition **and identical across them** — the same SHA-256
(`6b8b50a284be`) in both. **A fixed `seed_transpiler` fully determines the output;
thread count does not affect it.** The hypothesis was accepted as a test, the test was
run, and it came back negative. Threads need not be pinned. Recorded as a resolved
question, not carried forward as a caveat.

### Result 2 — the pilot, and it is sharper than "variance is large"

8 seeds (16, 18, 20, 22, 24, 42, 12345, 99999), Qiskit 2.0.2, one version:

| circuit | qubits | 2Q min | 2Q max | mean | spread (max/min) | CV | regression reported in #14402 |
|---|---|---:|---:|---:|---:|---:|---:|
| `bv_n140` | 140 | 241 | 327 | 299.8 | **+35.7%** | 9.2% | +46% |
| `bv_n280` | 280 | 665 | 669 | 667.0 | **+0.6%** | 0.32% | +44% |
| `knn_341` | 341 | 1532 | 1547 | 1537.6 | **+1.0%** | 0.48% | +41% |

**Seed sensitivity is violently circuit-specific and is not predictable from circuit
size or family.** Two Bernstein-Vazirani circuits, 140 and 280 qubits, both reported
with ~45% regressions: one moves 36% on seed choice alone, the other 0.6%. A factor of
roughly **60× between them.**

What that implies, stated carefully:

- For `bv_n140`, seed spread (36%) is **the same order as the reported regression**
  (46%). A per-circuit regression percentage computed from three *unseeded* runs of this
  circuit carries an error bar nobody reports.
- For `bv_n280` and `knn_341`, seed spread is ~1% against ~40% reported. **Those calls
  look solid.** This is not a story about the benchmark being broken.
- Therefore: **you cannot know whether a per-circuit regression call is trustworthy
  without measuring that circuit's seed distribution, and the answer varies by more
  than an order of magnitude between circuits that look alike.** That is the
  contribution, and it is a decision-support result, not a descriptive one.

Also noted: on `knn_341` the 2Q count is nearly fixed (1.0%) while **depth** ranges
4766–4935 (**3.5%**). Metric choice changes the conclusion; both must be reported.

### ChatGPT's C3 concern is answered

Best-of-k at optimisation level 2 does **not** collapse the variance to nothing — on
`bv_n140` it is large. The pivot/stop rule is not triggered. The study has a subject.

### Honest limits on everything above

1. **8 seeds, 3 circuits, one version.** This is a pilot, not a distribution. No shape,
   skew or normality claim can be made yet.
2. **Circuits were chosen because they were the worst-reported** — a selection effect.
   A random sample of the corpus is required before any statement about "circuits in
   general".
3. `CouplingMap.from_line` ≠ `FlexibleBackend`; absolute counts are not Benchpress's.
4. No version comparison yet. 2.0.0 vs 2.0.2 (§23 G1) is still to run.
5. A bug found and fixed in `exp0_determinism.py`: a bare `except` around the QASM
   loaders turned "file not found" into a misleading "wrong QASM version" error. The
   file for test `knn_341-linear` is `knn_n341/knn_341.qasm` — directory and file names
   disagree.

### Next

- [ ] Random sample of the corpus, not just the worst-reported three, to kill the
      selection effect.
- [ ] Enough seeds per circuit for a shape claim; power-calculate from the pilot CVs.
- [ ] 2.0.0 vs 2.0.2 on the same circuits — the isolated-commit comparison.
- [ ] Reproduce with Benchpress's own `FlexibleBackend` so counts are comparable.

---

## 23. INDEPENDENT ATTACK — two critics, 8 points, 8 accepted — 2026-09-02

Critic browser recovered by spawning **chrome.exe itself** detached via `Win32_Process`
(spawning the `.cmd` detached fails — the launcher documents this, measured today).
Chrome 152.0.7977.65 on port 9222. Both critics answered. **Reported separately, never
merged**, per the tool's own instruction.

### Gemini Pro

**G1 — 1.4.3 vs 2.0 is structurally confounded (BackendV1 removal, overhauled default
pass managers). Fix: restrict to the 2.x line or isolated commits. → ACCEPTED.**
I had logged the confound but my mitigation was weak ("state it as a limitation").
Its fix is better than mine. **And it produces something we did not have:**
**2.0.0 → 2.0.2 isolates PR #14417 inside one major version** — no BackendV1 change, no
pass-manager overhaul, one known deterministic cause, known direction. That is a
**real-world ground-truth regression to calibrate the detector against**, not a
synthetic one. Adopted as the primary version pair.

**G2 — SABRE at optimisation level 2 runs trials in parallel; OS-level thread
non-determinism may override `seed_transpiler`. Fix: pin `RAYON_NUM_THREADS=1`.
→ ACCEPTED AS A TEST, NOT AS A FACT.**
The mechanism is plausible — Qiskit's SABRE is Rust and uses Rayon for parallel trials,
and tie-breaks could depend on completion order — but I have not verified it. It becomes
**Experiment 0: run one circuit at one fixed seed N times, single-threaded and
multi-threaded, and check bit-identical output.** If seeding alone does not give
determinism, every reproducibility claim in the design is void until threads are pinned.
**I did not have this. It is the most valuable point either critic made about
mechanism.**

**G3 — Injecting a synthetic regression before or during compilation lets the optimiser
alter it, invalidating the known effect size. Fix: append it as a rigid pass strictly
after standard compilation. → ACCEPTED.**
Correct and I had not thought it through. Pre-transpile injection means the optimiser may
remove or restructure the injected gates, so the "known" effect size is not known.
Post-compilation appending makes the injected delta exact.

### ChatGPT

**C1 — Claim 7 is an absence claim, killable by one counterexample; "we found no
published X" is not a contribution. Fix: make the contribution the validated procedure;
the literature gap is only motivation. → ACCEPTED.** Same discipline Panos already
imposed. The absence claim moves to Motivation and stops being a result.

**C2 — #14402's deterministic root cause leaves the causal motivation unsupported. Fix:
use it only as evidence that regression detection matters, then demonstrate seed-induced
decision instability directly. → ACCEPTED.** We already conceded the premise (§22 B2).
The useful addition is the prescription: **we must show a decision actually flipping
under reseeding**, not merely publish a distribution.

**C3 — Optimisation level 2 may collapse variance via best-of-k; you cannot know before
measuring. Fix: pilot MULTIPLE circuits; if variance is negligible, pivot to
version × optimisation-level interaction, or stop. → ACCEPTED.** Matches §16. Two
changes adopted: pilot several circuits rather than one, and **write the pivot/stop rule
into the pre-registration before running.**

**C4 — "First published distributions" is descriptive and easily dismissed. Fix:
validate a reproducible regression-audit procedure against synthetic regressions,
estimating false-positive and false-negative behaviour and calibrated power.
→ ACCEPTED. This is the single most important point either critic made.**
It converts the deliverable from *"here is a histogram nobody had"* — which a reviewer
dismisses as descriptive — into *"here is an audit procedure with measured FP/FN rates
at known effect sizes."* That is a validated instrument, it is what `jakelishman`
actually asked for, and it is what makes the thing usable by the Qiskit team.
**This replaces the headline deliverable.**

**C5 — Version comparison is confounded; call them "version-associated changes", add
within-version repeated-seed baselines, and refuse causal regression claims.
→ ACCEPTED.** Overlaps G1. The terminology discipline is adopted verbatim:
**"version-associated change", never "regression", unless a single isolated commit is
the only difference.**

### Revised design after the attack

1. **Experiment 0 — determinism check.** Fixed seed, N repeats, `RAYON_NUM_THREADS=1`
   vs default. Is output bit-identical? Everything downstream depends on the answer.
2. **Primary version pair: 2.0.0 vs 2.0.2** (isolates #14417). 1.4.3 vs 2.0 demoted to
   a secondary, explicitly confounded comparison.
3. **Pilot on several circuits**, not one. Pre-registered pivot/stop rule if variance is
   negligible.
4. **Headline deliverable = a validated audit procedure** with measured false-positive
   and false-negative rates at known injected effect sizes, and calibrated power.
   Distributions become supporting evidence, not the product.
5. **Synthetic regressions appended post-compilation** so the injected effect size is
   exact.
6. **Absence claim demoted to Motivation.**
7. **Must demonstrate at least one real decision flip** under reseeding, or report
   honestly that none occurs — which is itself a result, and a reassuring one.

**Why 8/8 acceptance is not deference:** G2 and C4 are things I did not have and they
change the design; G1 supplied a better version pair than mine; G3 fixed a control I had
specified wrongly. C1, C2, C3, C5 confirm concerns already in §16 and §22 but sharpen
each into an action. None was rejected because none was wrong — and G2 is accepted only
as a test to run, not as an established fact.

---

## 22. FROZEN CLAIM SET — verification complete — 2026-09-02

**Verification is finished. These claims are frozen. Nothing may be broadened without
new evidence, and any change to them must be dated and justified here.**

### A. Verified against the paper's own text (downloaded, stripped, grepped — not summarised)

| # | claim | paper line, verbatim |
|---|---|---|
| A1 | 25 seeds, 16–64 | *"we recompute all SDKs across 25 transpiler seeds (16, 18, 20, …, 64) with a 300 s timeout per seed"* |
| A2 | only Qiskit is stochastic | *"H and B are deterministic. Only Qiskit's SABRE routing is stochastic… TKET routing is deterministic (σ=0 across seeds)"* |
| A3 | the decision rule | *"a winner is defined only when the inter-SDK gap exceeds both the 0.5-decade comparability threshold and 2σ of routing noise"* |
| A4 | variance measured at 10 qubits, opt 0 | *"Table 10: 25-seed transpiler variance on IBM (n=10, opt=0)"* |
| A5 | attribution also at opt 0 | *"Table 6: Per-phase fidelity attribution (n=10, seed=42, opt=0)"* |
| A6 | TKET deterministic too | *"TKET's GraphPlacement and RoutingPass stage is also deterministic (σ=0 across seeds)"* |

### ⚠ B. Two corrections AGAINST our position — record them, do not bury them

**B1. They do scale beyond 10 qubits.** *"Scaling is evaluated over n∈[3,20] with a
300 s timeout."* The **variance** characterisation (Table 10) is at n=10, opt=0 — that
claim stands — but the paper as a whole reaches **20 qubits**, not 10. Saying "they only
went to 10 qubits" would be a misrepresentation. The honest statement is: *their seed-
variance table is at n=10 and opt=0, while their scaling study reaches n=20; Benchpress
regressions are reported at 140–930 qubits at optimisation level 2.*

**B2. The #14402 root cause was DETERMINISTIC, not stochastic.** Verified:

- **Issue #14413** — *"Transpilation result of RZZ gate by Qiskit 2.0 is less optimal
  compared with Qiskit 1.4"*, `t-imamichi`, opened and closed 2025-05-21, labels
  `bug`, `mod: transpiler`. RZZ at π/2 and π, optimisation level 3, basis
  `[rz, cz, sx, x]`: 2.0 emits **two CZ** where 1.4.3 emitted **zero or one**.
- **PR #14417** — *"Fix ConsolidateBlocks pass for collecting non-CX KAK gate"*,
  `mtreinish`, **merged 2025-05-21** into `main`. Root cause: a bug introduced in
  **#13884** where the KAK gate name passed from Python to Rust used the internal
  sentinel `"USER_GATE"` instead of the real basis gate name, so `ConsolidateBlocks`
  *"miss[ed] opportunities for consolidation."* It references **#14413**, not #14402;
  `mtreinish` asserted in the #14402 thread that it fixed that too.

**Consequence, and it must appear in any writeup:** the regression in #14402 had a
deterministic root cause — a wrong string constant. **#14402 is therefore NOT evidence
that seed variance affects regression calls.** It is the thing that led us to look, and
nothing more. Our motivation must rest on the maintainers' own stated need and on the
unseeded transpile path, never on #14402 being noise-driven. It was not.

### C. The frozen claim set

1. **Method ownership.** Pati & Simmhan own seed-variance methodology for compiler
   comparison. Cited, not contested, not claimed.
2. **Their rule's scope.** Their 2σ rule governs **fidelity** (`log10_F`) only. Verified
   in code (`statistical.py:213–258`) and in the paper (A3). **Gate-count σ is computed
   and reported but never enters a decision rule.**
3. **Their measurement regime.** Seed variance measured at `SABRE(opt=0)`, n=10, 3 SDKs,
   one Qiskit version, SDK-vs-SDK. Scaling elsewhere to n=20.
4. **The target regime.** Qiskit regression calls are made on **2Q gate counts**, at
   Benchpress's `optimization_level = 2`, on circuits of 140–930 qubits, **across
   versions**.
5. **The structural gap.** Their tool cannot express (4): comparison key is
   `algo+sdk+backend` (`statistical.py:80`) — there is no version axis.
6. **The source-verified gap — the strongest single fact, and the limit of our claim.**
   **Benchpress fixes circuit-construction seeds (`seed=12345` throughout `qiskit_gym`)
   but passes no `seed_transpiler` anywhere.** Compilation randomness is uncontrolled
   while construction randomness is pinned.
7. **The absence claim, stated narrowly.** We have not found a published decision rule,
   or a published distribution, for 2Q gate count under transpiler-seed variation at
   Benchpress's operating point. **Not** "nobody measures seed variance" — they do.
8. **The stated need.** `jakelishman` asked in #14402 for a curated ~10-test subset,
   many seeds, persisted seeds, and significance testing for non-normal distributions.
   `repo:Qiskit/benchpress` + `seed` → **0 issues, 0 PRs**. Qiskit PR **#16157** (open,
   Aug 2026) still benchmarks 1,021 circuits at `QISKIT_TRANSPILER_SEED=1` with no
   confidence intervals.

### D. Order of operations from here

`verify` ✅ → `freeze` ✅ → **`independent attack` ← next** → `code`

The second-opinion check remains **NOT OBTAINED**. A failed connection is an open item,
never a pass.

---

## 21. BRICKS VERIFIED — line-by-line read of the actual source — 2026-09-02

Both repos cloned and read with a file reader, not a summariser.
`analysis/statistical.py` (430 lines) and `configs/experiment.py` (35 lines) read in full.

### Confirmed exactly as recorded in §19–§20

| claim | line | verdict |
|---|---|---|
| `significant = gap > 2 * pooled_std if pooled_std > 0 else True` | `statistical.py:247` | **exact** |
| comparison key `f"{algo_name}+{sdk_name}+{backend_name}"` — no version axis | `statistical.py:80` | **exact** |
| descriptive statistics only — mean, std(ddof=1), min, max | `statistical.py:145–148` | **exact** |
| no non-parametric test, no bootstrap, no IQR, no normality test | whole file | **confirmed by full read** |
| seeds `list(range(16, 68, 2))[:25]` | `experiment.py:14` | **exact** |
| `R:SABRE(opt=0)` | `experiment.py:7`, in `FAIRNESS_LOCKS` | **exact** |
| all 8 algorithms at `n_qubits: 10` | `experiment.py:23–33` | **exact** |
| 300 s per-seed timeout | `statistical.py:32` | **exact** |

### ⛔ CORRECTION to §20 — I had this wrong

**The 2σ rule is applied to FIDELITY ONLY, never to gate counts.**
`winner_validity_check` (`statistical.py:213–258`) computes `_fidelity_mean` and
`_fidelity_std` from `log10_F` and compares only those. Gate-count σ — including
`#2Q_physical_std` — is computed and printed in the variance table, but **never enters
any decision rule.**

This is a *better* fact for us, not a worse one. It means **no published decision rule
exists for the metric IBM actually tracks regressions on.** §20's framing — "audit their
2σ rule on gate counts" — was wrong, because they never applied it there. The accurate
framing is: their rule governs fidelity; the regression decisions in #14402 are made on
2Q gate counts; **nothing governs those.**

### Three new observations from the real code — flagged as questions, not defects

**1. Pooled σ is pooled across SDKs, two of which are deterministic.**
`statistical.py:218` groups by `algo+backend`, then pools variance across the SDKs in
that group (`242–246`). Their own note (`statistical.py:270–271`) says *"Only the
R-stage (SABRE routing) is stochastic"* — i.e. among Qiskit, PennyLane and TKET, only
Qiskit's routing varies with seed. **If the deterministic SDKs contribute σ≈0, pooling
lowers `pooled_std`, which makes gaps easier to call significant.** Whether that is
defensible depends on intent — pooled variance normally assumes comparable spread across
groups. **Record as a question to test empirically, not as an error.**

**2. A first-seed timeout discards the entire stack.**
`statistical.py:108–110`: `if i == 0: … break`. The hardest circuits — slowest to
transpile — drop out completely, and plausibly they are the ones with the largest
variance. Surviving stacks are aggregated over a **censored** sample (`n_skipped` is
recorded, which is good practice). At 10 qubits nothing times out; **at 341 qubits it
would.** This directly reinforces the regime argument.

**3. The timeout is a no-op on Windows.**
`statistical.py:51`: `if seconds <= 0 or not hasattr(signal, "SIGALRM")` → yields
without limit. POSIX-only. Platform-dependent behaviour in a reproducibility artifact.
Minor, but it belongs in a fair writeup.

### The claim set, restated after verification

1. Pati & Simmhan own seed-variance methodology for compiler comparison. **Cited, not
   contested.**
2. Their 2σ decision rule governs **fidelity**, and is validated at `SABRE(opt=0)`,
   10 qubits, 8 algorithms, 3 SDKs, one Qiskit version.
3. Qiskit regression decisions (#14402) are made on **2Q gate counts**, at
   `optimization_level=2` with internal best-of-k SABRE trials, on Benchpress circuits
   of **140–930 qubits**, across versions.
4. **No published decision rule, and no published distribution, exists for (3).**
5. Their tool cannot express (3): no version axis, and gate-count σ never reaches a rule.

### ✅ RESOLVED — the §17 "fixed seeds" discrepancy

Read from the clone. `benchpress/qiskit_gym/abstract_transpile/test_qasmbench.py:38,46–51`:

```python
OPTIMIZATION_LEVEL = Configuration.options["qiskit"]["optimization_level"]
...
backend = FlexibleBackend(circuit.num_qubits, circ_and_topo[1], control_flow=True)
pm = generate_preset_pass_manager(optimization_level=OPTIMIZATION_LEVEL, backend=backend)
```

**No `seed_transpiler`. Confirmed from source, not inferred.**

And a grep for `seed` across the whole of `benchpress/qiskit_gym/` returns **only
circuit-construction seeds** — `QuantumVolume(100, 100, seed=12345)`,
`dtc_unitary(..., seed=12345)`, `random_clifford_circuit(..., seed=12345)`,
`SEED = 12345` in `construct/test_build.py`. **There is no transpiler seed anywhere in
the Qiskit gym.**

**So Benchpress fixes the randomness in how circuits are BUILT and leaves the randomness
in how they are COMPILED completely free.** That is the precise resolution: when
`nonhermitian` said runs are done "with fixed seeds", that is consistent with fixed
*circuit* seeds, or with a separate internal harness — but the public transpile path is
unseeded. This is the sharpest single fact in the whole investigation, and it is now
verified rather than inferred.

### Still open

- [ ] Confirm PRs #14417 and #14413.
- [ ] Re-verify the §19 paper extractions against the paper text — the code is now
      verified, the *paper* claims are not.
- [ ] **Second-opinion critique NOT OBTAINED** — critic browser would not attach on
      127.0.0.1:9222 even after `start_critic_chrome.cmd` exited 0 with empty output.
      **This is a failed check, not a pass.** The claim set in §21 has not been
      independently attacked. Retry before anything is written up.

---

## 20. THE SURVIVING OBJECT — read from their source code — 2026-09-02

Read from `github.com/dream-lab/quantum-hbr`. **These are extraction summaries of source
files, not manual reads. Before any of this is published, the actual files must be read
line by line.** Flagged, not assumed.

### What `analysis/statistical.py` actually implements

```python
agg[f"{metric}_mean"] = round(float(np.mean(values)), 2)
agg[f"{metric}_std"]  = round(float(np.std(values, ddof=1)) if len(values) > 1 else 0.0, 2)
```

```python
significant = gap > 2 * pooled_std if pooled_std > 0 else True
```

```python
stack_key = f"{algo_name}+{sdk_name}+{backend_name}"
```

```python
TRANSPILATION_METRICS = [
    "#2Q", "#1Q", "#total", "depth_after", "depth_physical",
    "#2Q_physical", "SWAP_overhead",
    "N_2Q_H", "N_2Q_B", "N_2Q_R",
]
```

- **Descriptive statistics only:** mean, std (ddof=1), min, max, pooled std across SDKs.
- **Not implemented:** non-parametric tests (Mann-Whitney, Kruskal-Wallis), bootstrap,
  IQR, normality tests (Shapiro-Wilk, Anderson-Darling).
- **Comparison key is `algo+sdk+backend`.** There is **no version axis.** The script
  cannot express "version A vs version B" at all.
- ⚠ Note the fallback: when `pooled_std == 0`, `significant` is set **True**. Zero
  measured variance yields an automatic significance call. Record it; do not
  characterise it as a defect until the surrounding code is read properly — it may be
  deliberate for deterministic SDKs.

### What `configs/experiment.py` fixes

- Seeds: `list(range(16, 68, 2))[:25]` → exactly 16, 18, …, 64. Confirms §19.
- **Qiskit routing stage: `SABRE(opt=0)`.**
- 8 algorithms, **all at 10 qubits**. Backends `ibm_heron`, `ionq_forte`.
- Confidence level 0.95; transpiler seed 42 and simulator seed 42 for the non-sweep runs.

### ⭐ The two regime gaps — this is the whole result

Their variance characterisation and the Benchpress regression regime are **not the same
operating point**, on two independent axes:

| axis | Pati & Simmhan measured σ at | Benchpress regression calls are made at |
|---|---|---|
| **optimisation** | `SABRE(opt=0)` — a **single** routing trial | preset pass manager at **`optimization_level = 2`**, which runs **multiple internal SABRE trials and keeps the best** |
| **scale** | **10 qubits**, 8 algorithms | **140–930 qubits**; the worst reported regressions are `bv_n140` (140q), `bv_n280` (280q), `knn_341` (341q), across ~1,000 tests |

Both matter, and the first is the sharper one. A best-of-k statistic has a **different
distribution shape** from a single draw — lower variance, and skew in the opposite
direction. **A σ measured at opt=0 on 10 qubits cannot be assumed to describe the
distribution at opt=2 on 341 qubits.** Nobody has measured the latter.

### The surviving object, stated so it survives a crowbar

> **The per-circuit distribution of two-qubit gate count under transpiler-seed variation,
> measured at Benchpress's actual operating point — `optimization_level = 2`, real
> Benchpress circuits at 140+ qubits, declared topologies including `linear` — its
> shape, and whether the 2σ decision rule implemented in the only published tool that
> does this is calibrated in that regime.**

What we claim, and nothing more:

- We **do not** claim the seed-variance method. Pati & Simmhan own it and are cited.
- We **do not** claim "nobody measures seed variance." They do.
- We **do** claim: their σ was measured at opt=0 and 10 qubits; regression calls on
  Benchpress happen at opt=2 and 140–930 qubits; and **no published measurement exists
  in that second regime.**
- We **do** provide the version axis their tool structurally lacks
  (`algo+sdk+backend`, no version key).
- We **do** provide the distribution-free testing Lishman asked for and their script
  does not implement.

### Why every outcome is publishable

- Distribution is approximately normal at opt=2 → the 2σ rule transfers; we have
  validated an existing published method outside its measured regime. Useful.
- Distribution is skewed or heavy-tailed at opt=2 → the 2σ rule is mis-calibrated
  there, and so is every informal three-run comparison; we quantify by how much.
- Variance at opt=2 is near zero because of internal best-of-k trials → then per-circuit
  regression calls are **more** reliable than feared, which contradicts our own
  expectation and is exactly the sort of result that makes the rest credible.

### Status

- Kill check → **PASS**
- Prior-art check → **PASS, general method claim surrendered**
- Exact repurposing question → **ANSWERED.** Their script has no version axis, uses
  descriptive statistics only, and measured variance in a different regime on two axes.
- Code → **not yet.** Remaining reads first: verify these extractions by reading the
  files properly; `FlexibleBackend` and the "fixed seeds" discrepancy in §17; PRs
  #14417 and #14413.

---

## 19. METHOD COMPARISON — Pati & Simmhan vs. the proposed instrument — 2026-09-02

Source: `arxiv.org/html/2605.07876v1`. **Read via HTML extraction, not a full manual
read.** Section numbers and quoted phrases must be re-verified against the paper before
any of this is cited in writing.

### Their method, on the seven axes

| # | axis | Pati & Simmhan |
|---|---|---|
| 1 | **randomised** | **Transpiler seed only.** "H and B are deterministic. Only Qiskit's SABRE routing is stochastic." Layout/placement deterministic within each SDK. |
| 2 | **measured** | 2Q gate count `N₂Q`; 1Q physical gate count; total depth `D_tot`; 2Q layer depth `D₂Q`; 1Q layer depth; **Δlog₁₀(F)** per stage (H, B, R) and total; compile time (Tier 2); execution correctness / Hellinger fidelity |
| 3 | **variance estimate** | **Standard deviation σ across the 25 seeds.** Report `Gap/σ` ratios. No bootstrap, no IQR, no distribution-shape analysis reported. |
| 4 | **decision rule** | Winner declared only when inter-SDK gap exceeds **both** a **0.5-decade** comparability threshold in Δlog₁₀(F) — a decade being a base-10 log unit in fidelity space — **and 2σ** of routing noise. |
| 5 | **seeds** | Fixed arithmetic sequence **16, 18, 20, …, 64** (25 values), 300 s timeout each. **The paper gives no justification for that range or count.** Code at `github.com/dream-lab/quantum-hbr`. |
| 6 | **per-circuit vs aggregate** | Per-circuit: fidelity decomposition per algorithm/SDK/backend. Aggregate: rank ordering across the 8 circuits, mean Pearson r = 0.993. |
| 7 | **statistical script** | Not described in the text. Repo exists; contents unverified. |

**Setup:** Qiskit **2.3.0**, PennyLane 0.44.0, TKET 2.15.0 · 8 circuits (GHZ, Grover,
QDRIFT, QFT, QPE, Trotter, BV, QAOA) · IBM Heron heavy-hex 156q + IonQ Forte
all-to-all 36q · validated on FakeFez, IonQ simulator, and real IBM Fez.

### Line-by-line against what we proposed

| axis | theirs | ours | same or different |
|---|---|---|---|
| independent variable | **SDK identity**, one Qiskit version | **Qiskit version**, one SDK | **DIFFERENT — the core distinction** |
| randomised | transpiler seed | transpiler seed | **identical** |
| seed count | 25, fixed, unjustified | chosen by power calculation | different, and ours is defensible |
| primary metric | Δlog₁₀(F) fidelity proxy | **2Q gate count** — the KPI IBM actually tracks (`nonhermitian`, #14402) | different |
| variance statistic | σ only | full distribution: median, IQR, quantiles, CV, bootstrap CI, **and shape** | superset |
| decision rule | 0.5 decade **AND** 2σ | distribution-free — the thing Lishman explicitly asked for | different |
| circuits | 8 hand-picked algorithms | Benchpress corpus, curated subset (~10, per Lishman) | different |
| topology | heavy-hex 156q, all-to-all 36q | Benchpress declared topologies incl. **linear**, where the worst regressions were reported | different |
| optimisation level | not stated | **designed axis** — higher levels run internal SABRE trials and keep the best | they do not treat it |
| what is the product | a ranking | **the distributions themselves** | different |

**They used a single Qiskit version. Version-vs-version regression detection is
completely untouched by them.** CONFIRMED.

### ⭐ The opening this read actually revealed — better than the one we had

Their decision rule is **σ-based**. A 2σ threshold carries an implicit assumption about
distribution shape. But 2Q gate counts are **discrete, bounded below, and plausibly
right-skewed** — a bad routing draw can be far worse than a good draw is good.
**Nobody has published the shape of these distributions.** Lishman asked, in the same
thread, for "statistical significance testing accounting for non-normal distributions" —
which is precisely an admission that the shape is unknown.

So the sharpest question is no longer "is the regression real":

> **What is the shape of the per-circuit 2Q-gate-count distribution under seed
> variation, and is a 2σ rule correctly calibrated on it?**

Why this is the right question:

- **Both outcomes are results.** Approximately normal → Pati & Simmhan's rule is
  validated, and that is a useful, publishable confirmation of an existing method.
  Skewed or heavy-tailed → their 2σ gate is mis-calibrated, and so is every informal
  three-run comparison in the ecosystem, and we can say by how much.
- **It audits an instrument rather than claiming a gap.** Exactly the §15 mission,
  now aimed at a specific published decision rule instead of a vague target.
- **It needs no method novelty.** We adopt their method, cite it, and measure the thing
  it assumes.
- **It exposes a second, concrete audit target:** whether **25 seeds** is enough. If the
  tail is heavy, 25 draws underestimates σ, and the sequence 16–64 has no stated
  justification. Sample-size adequacy is directly testable by subsampling our own larger
  sweep.

### Design consequences, fixed before any code

1. Metric is **2Q gate count** — it is the KPI in #14402 and it is what regression calls
   are made on. Depth secondary.
2. Report **shape** first: histogram, skewness, kurtosis, normality test, and the
   empirical quantiles. σ alone is what we are auditing, so σ alone cannot be the output.
3. **Optimisation level is a designed factor**, not a constant, because internal SABRE
   trials at higher levels make the observed variable a best-of-k statistic whose
   distribution differs in shape from the underlying one.
4. **Subsample our sweep at n=25** to test their sample size directly, using their own
   seed sequence 16–64 as one of the draws.
5. Versions: at minimum 1.4.3, 2.0, 2.0.2 — the last one because #14417 landed there, so
   it separates "regression" from "fix" on the same corpus.

### Before code — remaining, unchanged

- [ ] Verify these extractions against the actual paper text; the section numbers came
      from a summariser.
- [ ] Inspect `github.com/dream-lab/quantum-hbr` — if their statistical script is
      published, read it rather than infer it.
- [ ] `FlexibleBackend` / topology definitions; the "fixed seeds" discrepancy in §17.
- [ ] Confirm PRs #14417 and #14413.

---

## 18. KILL CHECK RESULT — instrument survives, method does not — 2026-09-02

### ⛔ The method is NOT novel. Prior art found, and it must be cited.

**Pati & Simmhan, *Per-Phase Fidelity Attribution for Quantum Compilers using HBR
Decomposition*, arXiv:2605.07876 (May 2026)** already does the core statistics:

- **25 transpiler seeds** (16, 18, 20, …, 64), 300 s timeout per seed
- explicitly to **quantify routing-induced variance**
- declares a winner **only** when the inter-SDK gap exceeds both a 0.5-decade
  comparability threshold **and 2σ of routing noise**
- notes only Qiskit's SABRE is stochastic among the SDKs compared

**Any claim that "nobody measures seed variance in compiler benchmarking" is FALSE and
would be destroyed on first contact with a reviewer.** Delete that framing everywhere.

**What it does NOT do**, and this is the whole remaining opening:

- it compares **SDK against SDK**, not **version against version** — it is not
  regression detection over time
- the seed sweep is a **gating device inside a paper about fidelity attribution**, not
  a published study of the variance itself; the per-circuit distributions are not the
  product
- it is **not Benchpress-based** and does not address the maintainers' curated-subset
  regression-audit request

### ✅ Evidence the instrument itself does not exist

- **`repo:Qiskit/benchpress` + `seed` → 0 issues, 0 PRs.** Not one. Fifteen months after
  the maintainers' thread, nobody has even filed an issue about seeding Benchpress.
- **Qiskit PR #16157** (`hfwen0502`, opened 2026-05-08, updated 2026-08-11, still open)
  benchmarks **1,021 circuits** for a level-2 optimisation change using
  **`QISKIT_TRANSPILER_SEED=1`** — a single deterministic seed, aggregate metrics, **no
  confidence intervals and no significance testing**. Two circuits with upstream
  non-determinism were excluded from analysis.
  **This is a live, current example of exactly the practice Lishman said needed fixing,
  in the Qiskit repository, fifteen months later.** It is the strongest single piece of
  evidence that the instrument is still missing and still wanted.
- No Benchpress-focused seeded-distribution study found in the literature.

### The narrow claim — the only version that survives a crowbar

> **We have not found a published Benchpress-focused per-circuit seed-distribution
> study, nor a seeded cross-version regression-audit instrument for Qiskit.**

Not "nobody measures seed variance." Not "the benchmarks are broken." Not "quantum
software is unvalidated." That sentence, and nothing wider.

### What the contribution actually is, ranked by how well it holds up

1. **Strongest — the empirical object.** First published **per-circuit transpiler
   variance distributions** on the Benchpress corpus at optimisation level 2, linear
   and other declared topologies. Nobody has published these. An empirical distribution
   is hard to argue with.
2. **Strong — the problem transfer.** Applying variance-gated comparison to
   **cross-version regression detection** rather than cross-SDK ranking. Different
   question, different failure mode, and the one the maintainers actually asked about.
3. **Weakest, and must be stated honestly — the method.** Seed sweep plus a
   noise-threshold gate is Pati & Simmhan's. We adopt it and cite it. **We do not claim
   it.** A reviewer who finds that paper before we cite it ends the discussion.

### Still open — do not skip before building

- [ ] Read `FlexibleBackend` and topology definitions; resolve the "fixed seeds"
      discrepancy in §17.
- [ ] Confirm PRs **#14417** and **#14413** say what the comment summary claims.
- [ ] Read Pati & Simmhan in full — the PDF would not extract; get the HTML at
      `arxiv.org/html/2605.07876v1`. **Their exact method must be known before ours is
      designed, or we will reinvent it badly.**
- [ ] Check whether the Benchpress Nature Comp. Sci. paper
      (doi:10.1038/s43588-025-00792-y) already reports run-to-run variance.

---

## 17. THE PIVOT — from audit to commission — 2026-09-02

### The regression is fixed. That target is dead.

Issue #14402: opened 2025-05-19, **closed 2025-05-22, state_reason `completed`**, 8
comments. Root cause traced to #14413; **fixed by PR #14417**; fix shipped in **2.0.2**.
`mtreinish` posted before/after evidence (`swap_test_n361-linear`: 2334 → 1622 on
stable/2.0). `ElePT` posted graphical confirmation. Three days from report to fix.

**There is no live regression to audit, and we should not pretend otherwise.**

### What is in that thread is worth more than the regression was

**`jakelishman` (core Qiskit maintainer), 2025-05-20**, proposed — publicly, in the
issue — the following instrument:

- a **curated subset of ~10 tests** (full suites take many hours)
- **multiple seeds** to estimate the distribution
- **seeds stored** for full reproducibility
- **statistical significance testing that accounts for non-normal distributions**
- runtime target **~30 minutes to a couple of hours**

He also asked (2025-05-20, second comment) for observability into *which compilation
stage* the variation comes from — PassManager callbacks or custom passes to separate
layout/routing variation from optimisation variation.

**`ElePT`, 2025-05-20:** ~3% variation is typical and **difficult to distinguish from
algorithmic variance**. Gave cross-release regression counts: v1.3 vs v1.2 — 245
regressions, max 232.47%; v2.0 vs v1.3 — 528 regressions, max 46.08%.

**`nonhermitian`, 2025-05-20:** warns about the **compounding effect** of accepting a
"~3% change" every release. Also (2025-05-20, later) says the benchmarking team is *not*
working on Benchpress, tracks 2Q gate counts as a KPI, sees a "general move in the
direction of increased 2Q gate counts since 1.3 or so", and that runs take about two
hours each **with fixed seeds**.

> ⚠ **Unresolved discrepancy — record, do not explain yet.** `nonhermitian` refers to
> runs "with fixed seeds", but `default.conf` contains **no seed parameter** and
> `test_qasmbench.py` calls `generate_preset_pass_manager` with **no `seed_transpiler`**.
> Either an internal KPI harness differs from the public repo, or seeding happens
> somewhere not yet read. **Do not assert either.**

### Benchpress configuration — CONFIRMED from `default.conf` at repo root

```
[general]
basis_gates = ['id', 'sx', 'x', 'rz', 'cz']
backend_name = 'fake_torino'
abstract_topologies = ['all-to-all', 'square', 'heavy-hex', 'linear']
[qiskit]
optimization_level = 2
```

So: **optimisation level 2**, `fake_torino` for device transpilation, and `linear` is a
genuine entry in `abstract_topologies` — the `-linear` suffix on `bv_n140-linear` is
that topology, **verified, not assumed**. **No seed or trial-count parameter exists in
the configuration.**

### The new target

Not "audit IBM's broken instrument." It is:

> **Build the seeded, statistically-principled compiler-regression detector that Qiskit
> maintainers specified in May 2025 and that nobody appears to have built — and publish
> the first empirical distributions of per-circuit transpiler variance.**

Why this is stronger than everything in §13–§16:

1. **Novelty is defensible without arguing.** A named core maintainer specified the
   instrument publicly. We are not claiming a gap; we are filling a stated one.
2. **It is a tool, not a critique.** That matches what he actually ships —
   `trainproof`, `ttsproof`, `spkproof`, `notchecked` are all instruments for proving
   claims. This is the same object in a new domain.
3. **Adoption is a realistic outcome.** The people who would use it asked for it. That
   is a route to contact, contribution, citation, and plausibly work — which a critique
   paper is not.
4. **Feasible on the hardware he has.** The maintainers' own runtime target is 30
   minutes to two hours.
5. **No physics.** Gate counts, seeds, and non-parametric statistics.
6. The **empirical distributions themselves are the paper** — per-circuit transpiler
   variance at optimisation level 2 has never been published.

### Before a line of code — the kill checks

- [ ] Has it been built since May 2025? Search Benchpress commits, PRs, issues, and
      release notes; check `qiskit/qiskit` for a seeded benchmark harness.
- [ ] Did IBM build it internally and publish results anywhere?
- [ ] Read `FlexibleBackend` and the topology definitions to resolve the seeding
      discrepancy above.
- [ ] Confirm `#14417` and `#14413` say what the comment summary claims.

If it exists, we do not reframe — we report it and stop.

---

## 16. PHASE ZERO — FIRST MEASUREMENTS ON ISSUE #14402 — 2026-09-02

Read from the issue and from Benchpress source. **All of it needs one confirmation pass
before anything is built on it** — the source readings are summaries of single files,
not full reads. Marked PRELIMINARY throughout.

### What the issue actually contains — CONFIRMED

- Filed by **@nonhermitian** (Paul Nation, lead author of Benchpress itself),
  **19 May 2025**. **Status: CLOSED.** How it was closed is not yet established.
- Three full-suite runs per version, total 2Q gate counts:
  - **Qiskit 1.4.3:** 31,052,380 / 30,956,316 / 31,106,370 → mean ≈ 31,038,355
  - **Qiskit 2.0:** 32,689,074 / 32,693,565 / 32,704,283 → mean ≈ 32,695,641
- Roughly 400+ individual tests show increases. Worst reported: `bv_n140-linear` +46%,
  `bv_n280-linear` +44%, `knn_341-linear` +41%.

### First result — and it goes AGAINST our hypothesis at the aggregate level

Run-to-run spread within each version, as a fraction of that version's mean:

| version | range across 3 runs | as % of mean |
|---|---|---|
| 1.4.3 | 150,054 | **0.48%** |
| 2.0 | 15,209 | **0.05%** |

The between-version gap is far larger than either. **At the aggregate level the
regression is cleanly separated from run-to-run noise. "The measurement is
underpowered" is false as applied to the headline aggregate, and that must be stated
plainly in any writeup.** A control that kills the first hypothesis is the control
working.

> ⚠ Arithmetic note: the difference of the two means is ≈1.66M gates, ≈5.3% of the
> 1.4.3 mean, while the issue is summarised as "~3%, ~1 million". This may be a
> summarisation artifact of how the issue was read, a different denominator, or a
> subset figure. **Do not repeat either number until the issue text is read directly.**

### The live question, which is sharper than the one we started with — PRELIMINARY

`benchpress/qiskit_gym/abstract_transpile/test_qasmbench.py` calls:

```
pm = generate_preset_pass_manager(optimization_level=OPTIMIZATION_LEVEL, backend=backend)
```

**No `seed_transpiler` is passed.** Qiskit's own documentation states: *"The preset pass
managers almost always include stochastic, heuristic-based passes. If you need to
ensure reproducibility of a compilation, pass a known integer to the `seed_transpiler`
argument."*

Two consequences, and the second is the project:

1. The three runs are genuine independent draws, not repeats of one seed. That is why
   the aggregate is trustworthy — and the stability is fully explained by summing ~1,000
   tests, where the relative error of a sum shrinks like 1/√n. No seeding needed to
   explain it.
2. **Per test, each version has exactly three unseeded samples.** The per-test figures —
   including the 46%, 44% and 41% headline regressions — rest on n=3 draws per version
   from an unmeasured distribution. **Nobody has measured the per-circuit seed variance.**
   The aggregate being solid says nothing about any individual circuit, and the
   per-circuit numbers are the ones a developer would chase.

### A second, unclaimed observation

1.4.3's aggregate spread (0.48%) is **~10× larger** than 2.0's (0.05%). On three points
each this is far too thin to assert, but it suggests 2.0 may be *more deterministic* than
1.4.3 — possibly trading average gate count for consistency. If that holds per-circuit
it is a finding nobody has stated, and it is measurable with the same apparatus.

### Corrected experiment design

Supersedes the "1,000 seeds on 3–5 circuits" plan, which picked N before knowing the
variance or the cost per run.

1. **Confirm the source readings.** Full read of `test_qasmbench.py`, `config.py`,
   `default` config, `FlexibleBackend`, and the topology definitions
   (`SMALL_/MEDIUM_/LARGE_CIRC_TOPO`). Establish the real optimisation level and what
   "-linear" means. Read the issue text directly and resolve the 3%-vs-5.3% discrepancy.
   Find out how and why the issue was closed — if it was fixed, that changes the target.
2. **Pilot:** one circuit, ~30 seeds, both versions. Measure per-circuit spread AND
   wall-clock cost per transpilation.
3. **Choose N by power calculation** against the effect sizes actually reported, not by
   assertion.
4. **Primary axis: optimisation level.** Higher levels run multiple internal SABRE
   trials and keep the best, so the spread is a function of the level, and a best-of-k
   distribution is not the same shape as the underlying one. This is a designed factor,
   not a footnote.
5. **Headline question:** of the per-test regressions reported in #14402, what fraction
   survive when each circuit is measured across a proper seed distribution?

### Threats to validity, stated before running

- 1.4.3 → 2.0 is **not** a single-variable change. 2.0 removed BackendV1 and altered
  default pass managers. Some of the difference is not the router. This may not be
  fully removable; say so rather than discover it later.
- The issue is closed. If the regression was subsequently fixed, the interesting target
  becomes the *measurement practice*, not the regression.
- Paul Nation wrote both Benchpress and the issue. This is a careful person publicly
  reporting a regression in his own employer's product. **The writeup says that.** The
  finding, if any, is about statistical power in per-test reporting, not about anyone
  being careless.

---

## 15. ROUTE 3 — AUDIT THE INSTRUMENTS. This supersedes §14. — 2026-09-02

**§14 was built on a flawed premise and its two routes are withdrawn.** Every kill in
§0, §13 and §14 was made on the *existence* of a tool or a paper. Not one was made on
whether the tool is *correct*. Those are different questions and the second one was
never asked. Panos caught this; the correction is his.

The prior work is not a wall. It is a target list.

### The question

Not "what validation problem has nobody studied?" but:

> **Do the existing quantum-software benchmarking instruments actually measure what
> they claim, and do the conclusions drawn from them survive conditions that should
> not change the answer?**

### Evidence already in hand that the instruments are soft

- **Qiskit issue #14402** — a documented **~3% aggregate increase in two-qubit gate
  counts across Benchpress tests from Qiskit 1.4.3 to 2.0**, with double-digit
  increases on individual tests. A real regression, surfaced by the apparatus.
- **SabreSwap is stochastic.** The same circuit compiled twice gives different depth
  and gate counts. Benchpress's documentation describes execution time and memory
  measurement (pytest-benchmark, pytest-memray) and does not describe seed replication,
  variance reporting or significance testing. **This is currently an inference from
  docs — it must be confirmed against the code before it is stated anywhere.**
- Adjacent work already recomputes across **25 transpiler seeds** and requires the
  inter-SDK gap to exceed **2σ of routing noise** before declaring a winner — direct
  evidence that practitioners who thought about it consider single-run comparison unsafe.
- **Benchpress' own paper** (Nature Computational Science, doi:10.1038/s43588-025-00792-y)
  discusses tests that fail or are skipped for practical reasons — unsupported formats,
  memory exhaustion. Skipped tests are a selection effect on every aggregate it reports.
- **Red Queen** ships a self-declared warning that it "is no longer maintained and may
  contain errors," having been the cross-version comparison tool.
- **QASMBench** warns in its own documentation that its Hellinger-fidelity figure of
  merit does not generalise to large systems and may not represent real circuits on
  real hardware.
- **Bugs4Q** reproduces at **16.2%** on current Qiskit (arXiv:2606.27124), yet is the
  benchmark under LLM-repair and debugging papers (e.g. arXiv:2607.09007, QBugLM
  arXiv:2606.07314).
- **QITE** patched semantics-violating "semantics-preserving" transformations by hand
  inside an otherwise automated 5,000-program study.
- An 81-paper review titled *Claim against Measurement: Statistical Artefacts in
  Quantum Error Mitigation Benchmarks* (arXiv:2605.29872) already found the numbers
  soft in one subfield. Nobody has checked the others.

### Experiment 1 — the noise floor of the instrument

**Question.** What is the seed-induced standard deviation of two-qubit gate count and
depth on the Benchpress circuit corpus, per optimisation level and per circuit family —
and how does it compare to the effect sizes the community reports as regressions?

**Why this one first.** It is cheap, it is purely classical, it needs no physics beyond
gate counting, and issue #14402 supplies a real, documented, independently-sourced
effect size (~3%) to measure against. The headline is a single number: **the fraction
of reported benchmark conclusions that do not survive reseeding.**

**Pre-registered before running:** circuit subset, seed count (N≥30), optimisation
levels, SDK versions, and the flip-rate threshold that would count as a finding.

**Known confound that must be handled first.** Qiskit's higher optimisation levels
already run *multiple internal Sabre trials and keep the best*. That may suppress
seed variance substantially at `optimization_level=3` and leave it large at level 1.
Measuring variance per optimisation level is therefore not a nice-to-have — it is the
control that decides whether the study has a subject at all. **If variance is small
everywhere, Experiment 1 returns a negative result and the honest move is to publish
that and move to Experiment 2.**

### Experiment 2 — metric versus semantics

Construct circuit families where the benchmark's figure of merit improves while a
semantic or hardware-meaningful measure degrades. QASMBench's own Hellinger caveat is
the documented opening. This is the stronger paper if it lands, and the harder one.

### Honest risks

- IBM may answer "we know, that is what expected-fail tests are for." The reply has to
  be a number, not an argument.
- Framing matters: this is *how robust are conclusions drawn from these instruments*,
  not *IBM is lying*. The Qiskit team documented #14402 themselves — they are careful
  people, and the paper should say so.
- If seed variance turns out negligible, Experiment 1 is a negative result. That is an
  acceptable outcome and must be pre-registered as such, not quietly redesigned.

### Method correction, standing

A gap is only closed by a tool that has been *verified*, not by a tool that *exists*.
Every future kill must state which of the two it is.

---

## 14. THE DIAGNOSIS AFTER FOUR ROUNDS — 2026-09-02 — WITHDRAWN, see §15

Four adversarial sweeps. Every candidate died: C3 to Krol et al., C2 to Red Queen and
Metriq, the round-two survivors to QuCheck and an 81-paper statistics review. C1 and C4
remain unkilled, but I no longer trust "unkilled" to mean much — three of the four
things that died were killed *after* I recommended them.

**The diagnosis is not that we searched badly. It is that the target is wrong.**

Quantum software validation is swept continuously by two well-resourced groups: IBM
Quantum's benchmarking team, who ship tooling and blog release comparisons, and an
active academic SE community publishing at ICSE, ASE, ICSME and ISSTA. Any gap findable
by literature search in an afternoon is either already taken or thin by construction.
Competing there means competing with a vendor's full-time staff on their home ground,
with no differentiated asset.

### Two honest routes forward

**Route 1 — Replicate on purpose. Stop hunting virgin territory.**
The field is young, its results are single-shot, and almost nothing has been
independently re-run. ICSME runs a Replication and Negative Results track; MorphQ++ and
Ohto et al. both published there. A replication is not a consolation prize in a field
this immature — it is the scarce good. The concrete target is **C1**: QITE established
cross-platform semantic divergence at a fixed 11 qubits and 15 gates; re-run it,
scale circuit size as the independent variable, and report both the divergence curve and
the equivalence oracle's inconclusive-verdict rate. Low physics load, unkilled across
four sweeps, and the replication framing makes prior art an asset instead of a threat.

**Route 2 — Compete where the asset is rare, not where the field is hot.**
Generic software-engineering skill is not a differentiator here; a great many people
have it. What is rare is three published PyPI libraries — `trainproof`, `ttsproof`,
`spkproof` — that exist specifically to *prove claims about training and evaluation*,
plus a demonstrated ritual of adversarial self-verification, plus a real research line
behind them. Nobody in quantum ML has shipped that. The move is a validation
instrument for QML experimental claims — the quantum analogue of `trainproof` — which
produces a tool **and** a paper, and where the contribution is the instrument rather
than a gap in someone else's benchmark. Slower to first result; far more defensible;
and it compounds with work already done instead of starting cold.

### Recommendation

**Route 1 with C1 as the target, and Route 2 as what it feeds.** C1 gets a real result
in weeks with almost no physics, which is what the ΦΥΕ40 timetable demands. Route 2 is
where the durable position is, and C1's apparatus is a legitimate first component of it.

**Standing correction to method:** every phase-zero check from here searches
repositories, vendor engineering blogs and conference tooling tracks — not only papers.
Three of the four kills came from outside the paper literature.

---

## 12. Open decisions for review

1. Confirm C3 as the direction, or switch to C2.
2. Phase 0 is a hard gate: if a systematic resource-estimator comparison already exists,
   the project switches rather than reframes. Agreed in advance?
3. Repository location and name — nothing created until this document is approved.
