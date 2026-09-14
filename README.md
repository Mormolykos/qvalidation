# Seed variance in Qiskit Benchpress

Benchpress pins the seeds used to **build** circuits and passes no seed to the code that
**compiles** them. This repository measures what that costs.

> **A note on reviewer labels.** *Reviewer A*, *Reviewer B* and *Reviewer C* appear
> throughout `RESEARCH_LANDSCAPE.md`, `SETTLED.json` and the analysis scripts. They are
> three distinct large language models used as adversarial reviewers and as an
> independent code auditor. The specific products are not named: which tools were used is
> an implementation detail of how the review was run, not a scientific claim, and naming
> them would imply an endorsement none of them gave. What matters for the record is that
> each review was independent of the author and of the others, and that **every attack is
> recorded here with its outcome, whether or not it survived** — including the four
> claims it forced us to withdraw.

**Headline:** on `bv_n140` — a circuit Qiskit issue
[#14402](https://github.com/Qiskit/qiskit/issues/14402) itself names — mapped to a
heavy-hex lattice, the change from Qiskit 1.4.3 to 2.0.0 has a long-run mean of **+5.37%**
(95% CI +4.27% to +6.50%, **400 seeds per version across 21 processes**). The suite's own
protocol — **three unseeded runs per version — reports it as a ≥+10% regression 24.4% of
the time** (95% CI 19.5%–31.1%).

Two disjoint 200-seed samples agree: contiguous seeds in one process give 26.3%,
scattered seeds spanning 5.9 million to 1.08 billion across ten fresh processes give
22.6%, and each point falls inside the other's interval.

**Running more does not fix it.** Twenty runs per version — 20 × 2 versions × ~2 h per
suite run at the issue's own figure, so on the order of **80 compute hours** — still
leaves a **3.7%** false-positive rate. One `seed_transpiler` argument removes the
seed-attributable variance at one run.

The same circuit on `linear` changes **+31.0%** and is *missed* 2.98% of the time — a
false negative, which eight runs per version does remove.

And the issue's own reported figure for that circuit, **+46.14%**, is a single draw from
a distribution whose exact support runs from **−17.68% to +109.17%**. Its 95% range
reaches **below the +10% threshold**: the same real regression could have been reported
as no regression at all.

The two circuits in that issue with near-zero seed spread compare here to within
**+0.29 pp** and **−0.63 pp**. Only the noisy one disagrees, which is **consistent with**
seed variance rather than version drift — an observation about which circuits disagree,
not a demonstration that version drift is absent. The issue's Benchpress revision and
aggregation rule are not supplied, so these are numerical comparisons at our
configuration, not a reproduction of its protocol.

> ⚠ **This README is a summary. [`PAPER.md`](PAPER.md) is the authority**, and where the
> two disagree the manuscript is right. Claims corrected in v3 and v4 are listed in
> [`V3_CORRECTION_LEDGER.md`](V3_CORRECTION_LEDGER.md) and
> [`V4_ASTRA_CORRECTION_LEDGER.md`](V4_ASTRA_CORRECTION_LEDGER.md).
>
> ⚠ **An earlier headline here claimed a 27% false-positive rate on `qft_n320`. It is
> WITHDRAWN** — its 95% interval was [1.7%, 63.1%] at n=12, and the corpus statistic
> built on it turned out to depend on an undisclosed choice of which version was the
> baseline. See §38 and §41. Nothing was ever published. Every number below is
> direction-free and re-derives from raw data via `python inventory.py --check`.
>
> ⚠ **v4 corrections to this page (Astra V4-04).** It carried four claims the manuscript
> had already corrected and this page had not: the issue differences as +0.5 pp and
> +2.4 pp (the `knn_341` figure was misquoted and its difference has the wrong sign),
> 40 rather than 80 compute hours, "14 of 39 circuits are perfectly deterministic" when
> the raw data gives **13**, and a verifier described as five checks in 45 seconds when
> it is thirteen stages taking tens of minutes. A dated correction elsewhere does not
> neutralise a wrong number on the page a reader lands on.

---

## What was measured

| result | value | where |
|---|---|---|
| deterministic compilation ⇒ zero risk | 13/13 — but this is **arithmetic, not evidence** (§56) | §55, §56 |
| ⭐ risk vs distance from θ to the cut | Spearman **−0.833** among stochastic circuits — a **descriptive association**, not an identified mechanism | §55 |
| ⭐ median ambiguity band, 23 stochastic circuits | **10.9 pp** (max 25.2 pp) — θ-free and direction-free, but **constructed from this version pair's residuals and not independent of it** | §55 |
| circuits carrying risk ≥10% under this version pair | **4 of 26** (7 of 26 at ≥5%) | §55 |
| ⛔ suite-level failure rate | **withdrawn** — underpowered, effective n = 11 families | §55 |
| holds at every threshold 5%–20%; doubles under best-of-3 | min-of-3 raises `bv_n280` from 17.3% to 28.4% | §54 |
| all three circuits named in issue #14402 show an error rate | `bv_n140` 24.4%, `bv_n280` 17.3%, `knn_341` 4.7% | §52 |
| ⚠ but **13 of 39** circuits are perfectly deterministic | median eligible error rate **0.0000** — all 13 are eligible, so 13 of the 26 | §52 |
| **`bv_n140` real regression MISSED by the 3-run protocol** | **2.98%** of the time, 95% CI [1.72%, 4.99%] | §48 |
| `bv_n140` true change, 1.4.3 → 2.0.0, 200 seeds/arm | **+31.0%**, 95% CI [+28.4%, +33.8%] | §48 |
| what a single 3-run comparison of it can return | **−17.68% to +109.17%** (exact support) — ⚠ v3 corrected −10.5% to +100.0%, which were extrema of a finite *sample*, not support bounds | §48 |
| #14402 compared, low-seed-spread circuits | `bv_n280` **+0.29 pp**, `knn_341` **−0.63 pp** — numerical comparison at our configuration, not a protocol reproduction | §48 |
| decision instability, real change, forward direction | **5 of 51** circuits, Wilson [4.3%, 21.0%] | §48 |
| the error is not a threshold artifact | nonzero at **every** cut from +2% to +25% | §49 |
| ⚠ but it IS underpowering: error vs runs/version | k=1 16.1% → k=3 2.98% → **k=8 0.09%** | §49 |
| Benchpress gyms inspected for a compiler seed | **2 of 8** — Qiskit passes none, BQSKit passes `seed=0`; the other six are **not assessed**. ⚠ v4 corrected "0 of 8", which asserted something about all eight | §33 |
| Benchpress unseeded, `bv_n140-linear`, 20 runs | **17 distinct 2Q gate counts**, 244–340 | §27 |
| the seed is the entropy source | cross-process control, seeded 324×6 vs unseeded 6 values | §28 |
| **unpaired ambiguity band, heavy-hex** | **11.5–14.0 pp** across modelling choices | §42, §47 |
| **paired ambiguity band, heavy-hex** | **median 2.06 pp — 6.8× narrower** | §42 |
| ⚠ pairing on large-regression false negatives | **worse on 3 of 4 circuits** | §48 |
| backend error rates unseeded — effect on observable | **none**, 0 of 24 cases | §46 |
| circuits with an unpaired band ≥5 pp | **34 of 52**, Wilson 95% [0.518, 0.768] | §42 |
| unpaired band scales as | **1/√k** — k=1 → 23.8 pp, k=5 → 10.9 pp | §43 |
| runs needed to match paired k=1 unseeded | **≈49 per version** (≈200 h compute) | §43 |
| within-version seed spread, median | linear 0.90%, square 5.94%, heavy-hex 10.71% | §30 |
| replication from clean, 6 circuits × 12 seeds × 2 versions | **144/144 exact, 2/6 controls flat** | §44 |

Section numbers refer to [`RESEARCH_LANDSCAPE.md`](RESEARCH_LANDSCAPE.md), the full
research record, including every hypothesis that was **refuted** and every defect found
in this harness. [`DEFECTS.md`](DEFECTS.md) is the hostile review of this study, and
§45 is the current audit of what is *still* wrong.

**Start here:** [`replication/REPLICATE.md`](replication/REPLICATE.md) reproduces the
core of it in about a minute.

---

## Reproducing it

### 1. Environments — pin Qiskit *with* its dependencies

```bash
uv venv envs/bp202 --python 3.10
uv pip install --python envs/bp202/Scripts/python.exe \
    "qiskit==2.0.2" qiskit-ibm-runtime rustworkx scipy qiskit_qasm3_import pytest

uv venv envs/bp200 --python 3.10
uv pip install --python envs/bp200/Scripts/python.exe \
    "qiskit==2.0.0" qiskit-ibm-runtime rustworkx scipy

uv venv envs/bp143 --python 3.10
uv pip install --python envs/bp143/Scripts/python.exe \
    "qiskit==1.4.3" qiskit-ibm-runtime rustworkx scipy
```

> `bp143` is not optional. **The primary pre-registered study is 1.4.3 → 2.0.0**, so
> without it a fresh machine can reproduce the replication artifact (2.0.0 → 2.0.2) but
> not the experiment the paper is actually about. It was missing from these instructions
> until 2026-09-08, found while preparing a second-machine run.

> **Do not install `qiskit-ibm-runtime` separately.** Doing so silently upgraded Qiskit
> 2.0.2 → 2.5.2 during this work and an experiment ran against a version it did not
> report. Every script therefore takes `--require-qiskit` and **aborts** on a mismatch.

### 2. Benchpress

```bash
git clone https://github.com/Qiskit/benchpress.git
cd benchpress && git checkout b695f30e83a32bac05b9b4d8e98d37ba9aae5236 && cd ..
export BENCHPRESS_PATH=$PWD/benchpress
```

> **The checkout line is load-bearing and `--depth 1` must not come back.** This used to
> read `git clone --depth 1`, which fetches whatever Benchpress `main` happens to be
> today — not the pinned revision every number here was measured against. A fresh clone
> would then fail `verify.py` check 1 with a commit mismatch, and the failure would look
> like a broken repository rather than a broken instruction. A shallow clone also cannot
> check out an older commit, so the two lines have to be in this order. Found
> 2026-09-08 while preparing a second-machine run.

Benchpress's own `FlexibleBackend`, circuit loader, topologies and observable are
**imported and called**, never reimplemented, so equivalence is true by construction.
The observable is Benchpress's own, verbatim from `qiskit_gym/utils/io.py`:

```python
output_gate_count_2q = circuit.count_ops().get(two_qubit_gate, 0)
```

### 3. Run

```bash
# determinism: does a fixed seed fully determine the output?
python exp0_determinism.py --qasm <circuit.qasm> --repeats 5 --seed 12345

# is the backend a second randomness source?  (answer: no)
python exp1_backend_randomness.py --qasm <circuit.qasm> --require-qiskit 2.0.2

# does our path reproduce Benchpress's own unseeded observable?
python exp2_equivalence.py --qasm <circuit.qasm> --topology linear --n 20 \
    --require-qiskit 2.0.2
# --topology all-to-all is the negative control: no routing, so zero variance

# census: one OS process per circuit, so an OOM costs one circuit not the run
python census.py --python envs/bp202/Scripts/python.exe --size large \
    --topology linear --seeds 12 --require-qiskit 2.0.2 \
    --out results/raw/bp_large_linear_q202.jsonl

# analysis
python analyze.py --raw results/raw/bp_large_linear_q202.jsonl --out results/summary/s.csv
python flip_analysis.py --old results/raw/bp_large_linear_q200.jsonl \
    --new results/raw/bp_large_linear_q202.jsonl --threshold 0.10
python calibrate.py --raw results/raw/bp_large_linear_q202.jsonl --threshold 0.10

# the direction-free band, and the proof that the old paired column was a tautology
python paired.py --prove
python paired.py --band --band-ci 200 --topology heavy-hex     --old results/raw/bp_large_heavy-hex_q200.jsonl     --new results/raw/bp_large_heavy-hex_q202.jsonl

# A1: does the ambiguity cause a REAL wrong decision?  (needs the 1.4.3 arm)
python decision_error.py --old results/raw/bp_large_linear_q143.jsonl     --new results/raw/bp_large_linear_q200.jsonl --topology linear
python deep.py                    # 200 seeds/arm on the five decisive circuits

# A2: is the multiplicative noise model true?  (answer: no, and it does not matter)
python model_check.py --topology heavy-hex --pair 200:202
python model_check.py --topology heavy-hex --pair 200:202 --band-compare
```

### Everything at once

```bash
BENCHPRESS_PATH=<repo> envs/bp202/Scripts/python.exe verify.py
```

**Thirteen read-only stages, tens of minutes** — toolchain pin, test suite, inventory,
replication, tautology proof, paper claims, raw→endpoint, raw integrity, mutation test,
v2 evidence anchor, derived binding, rendered manuscript, published PDF. Exit 0 means
every stage passed. ⚠ v4 correction (Astra V4-04): this said "five read-only checks … in
about 45 seconds", which was true of v2 and describes neither the coverage nor the cost
of the current verifier — stage 9 alone rebuilds the repository eighteen times and stage
11 replays a 400 × 400,000 bootstrap.

**What exit 0 does and does not mean.** Each stage's scope is stated in its own file
header, and they are overlapping checks, not thirteen independent replications: several
share the same raw loader, selection list and classification constants, so one defect can
pass through more than one of them. `python mutation_test.py` is the evidence that they
turn red — eighteen corruptions, each required to be rejected by a named stage for a
named reason. Three of those corruptions defeated v3 and six defeated v4.

### 4. Tests

```bash
BENCHPRESS_PATH=<repo> envs/bp202/Scripts/python.exe -m pytest tests/ -v
```

Every test is a **regression test for a defect that actually occurred here**, not a
hypothetical. See "Defects in this harness" below.

---

## Data

`results/raw/*.jsonl` are **immutable observations**. One JSON object per line; every
run row carries its seed, circuit, topology, qubit count, the gate counted, the value,
the wall-clock time, and a hash of the emitted circuit. An `env` row carries the Qiskit
version, platform and configuration. `results/summary/*.csv` are **derived** and are
regenerable from the raw files alone.

Failures are data: `run_error`, `backend_error`, `load_error`, `budget_stop` and
`process_crash` rows are written, never silently dropped.

---

## Defects in this harness, and what each one hid

Listed because a study about measurement instruments that concealed its own instrument's
failures would be worth nothing.

| defect | what it silently did | test |
|---|---|---|
| QASM-2 export gated the measurement | deleted 40 rows / 4 circuits — **the control-flow ones** | `test_hash_failure_does_not_discard_the_measurement` |
| Rust OOM on `bwt_n37` aborted the process | lost 49 of 58 circuits — **the expensive ones** | `test_census_records_child_crash_as_a_row` |
| dependency install upgraded Qiskit underneath | an experiment ran on an unintended version | `test_version_guard_aborts_on_mismatch` |
| census merge stripped every `env` record | **the data file could not name its own toolchain** | `test_raw_rows_carry_everything_needed_to_reproduce` |

Two of these biased the corpus toward *easy* circuits, which would have **understated**
the finding. The provenance test was initially too weak to catch its own defect; it was
strengthened until it failed on the defective file, then the defect was fixed.

**Known limitation:** the per-circuit budget is a wall-clock budget, so the harness is
value-reproducible but **not sample-reproducible** — which circuits complete all 12 seeds
depends on machine load. Values for a given (circuit, seed) are deterministic and
reproduce across machines.

---

## What is *not* claimed

- **Not** that issue #14402's regression was caused by seed variance. Its root cause was
  deterministic (PR #14417, a wrong sentinel string in `ConsolidateBlocks`). #14402 is
  the reason we looked, nothing more.
- **Not** that the seed-variance method is novel. Pati & Simmhan
  ([arXiv:2605.07876](https://arxiv.org/abs/2605.07876)) established it; their rule
  governs *fidelity*, has no version axis, and was calibrated at 10 qubits and
  `SABRE(opt=0)`. They are cited, not contested.
- **Not** that any published cross-SDK ranking flipped. Only Qiskit is *measured*
  stochastic here; the ambiguity band is a resolving-power bound, not a demonstrated
  reversal. No other SDK has been measured at all.
- **Not** that "the benchmark is broken." Added 2026-09-03: this is stronger than it was.
  **In the direction that actually occurred — 2.0.0 → 2.0.2 — no circuit on any topology
  has an ambiguous verdict.** The exposure is to changes of a size that has not yet
  happened, not to one that has.
- ✅ **Superseded 2026-09-03.** This used to read "not that any real decision was ever
  wrong." §48 demonstrates one: `bv_n140`'s +31.0% regression is missed 2.98% of the
  time, 95% CI [1.72%, 4.99%], 21 pp clear of the threshold, at 200 seeds per arm.
  What is still **not** claimed is that any *published* Qiskit decision was wrong — we
  show the protocol errs at a measurable rate, not that a specific merge went the wrong
  way.
- **Not** that the multiplicative model is right — it is **rejected** on `linear` and
  `heavy-hex` (§47). An additive change fits better. The band was recomputed under both
  and moves by ≤1.34 pp, always narrower, so the reported figure is the conservative
  end of an 11.5–14.0 pp range.
- **Not** that Benchpress is broken or unfixable. The error is **underpowering, not
  incorrectness**: it falls from 16.1% at one run per version to 2.98% at three and
  **0.09% at eight** (§49). Anyone running eight times does not have this problem. The
  argument for `seed_transpiler` is therefore about **cost** — one argument versus ~16
  hours of extra compute per version comparison — not about correctness.
- **Not** that the 2.98% is precise. Split-half at n=100 gives 3.90% and 2.20%; the
  reported 95% CI [1.72%, 4.99%] covers every split, but the magnitude is known only to
  about a factor of two. **The existence of the error is established; its size is not.**
- **Not** that pairing fixes everything. `seed_transpiler` removes false positives and
  narrows the ambiguity band 6.8×, but on the four circuits with real missed
  regressions it is **worse on three of them** (§48).
- **Not** a claim about IBM hardware. `heavy-hex` here is
  `rustworkx.generators.heavy_hex_graph(dim)` sized to the circuit — the lattice family
  IBM uses, generated synthetically, with no device coupling map and no calibration.

---

## Licence

Code: MIT. Data and text: CC BY 4.0.
