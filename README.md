# Seed variance in Qiskit Benchpress

Benchpress pins the seeds used to **build** circuits and passes no seed to the code that
**compiles** them. This repository measures what that costs.

**Headline:** on `bv_n140` — a circuit Qiskit issue
[#14402](https://github.com/Qiskit/qiskit/issues/14402) itself names — mapped to a
heavy-hex lattice, the change from Qiskit 1.4.3 to 2.0.0 is **+5.75%** (95% CI +4.10% to
+7.38%, 200 seeds per version). The suite's own protocol — **three unseeded runs per
version — reports it as a ≥+10% regression 26.3% of the time** (95% CI 18.9%–34.9%).

**Running more does not fix it.** Twenty runs per version, about 40 hours of compute at
the issue's own "about 2 hours each", still leaves a **4.8%** false-positive rate. One
`seed_transpiler` argument removes it at one run.

The same circuit on `linear` changes **+31.0%** and is *missed* 2.98% of the time — a
false negative, which eight runs per version does remove.

And the issue's own reported figure for that circuit, **+46.1%**, is a single draw from a
distribution running from **−10.5% to +100.0%**. Its 95% range reaches **below the +10%
threshold**: the same real regression could have been reported as no regression at all.

The two circuits in that issue with near-zero seed spread reproduce here to within
**0.5 pp** and **2.4 pp**. Only the noisy one disagrees — which is what makes this seed
variance rather than version drift.

> ⚠ **An earlier headline here claimed a 27% false-positive rate on `qft_n320`. It is
> WITHDRAWN** — its 95% interval was [1.7%, 63.1%] at n=12, and the corpus statistic
> built on it turned out to depend on an undisclosed choice of which version was the
> baseline. See §38 and §41. Nothing was ever published. Every number below is
> direction-free and re-derives from raw data via `python inventory.py --check`.

---

## What was measured

| result | value | where |
|---|---|---|
| **`bv_n140` real regression MISSED by the 3-run protocol** | **2.98%** of the time, 95% CI [1.72%, 4.99%] | §48 |
| `bv_n140` true change, 1.4.3 → 2.0.0, 200 seeds/arm | **+31.0%**, 95% CI [+28.4%, +33.8%] | §48 |
| what a single 3-run comparison of it can return | **−10.5% to +100.0%** | §48 |
| #14402 reproduced, low-seed-spread circuits | `bv_n280` +0.5 pp, `knn_341` +2.4 pp | §48 |
| decision instability, real change, forward direction | **5 of 51** circuits, Wilson [4.3%, 21.0%] | §48 |
| the error is not a threshold artifact | nonzero at **every** cut from +2% to +25% | §49 |
| ⚠ but it IS underpowering: error vs runs/version | k=1 16.1% → k=3 2.98% → **k=8 0.09%** | §49 |
| Benchpress gyms passing `seed_transpiler` | **0 of 8**, source-verified | §33 |
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
```

> **Do not install `qiskit-ibm-runtime` separately.** Doing so silently upgraded Qiskit
> 2.0.2 → 2.5.2 during this work and an experiment ran against a version it did not
> report. Every script therefore takes `--require-qiskit` and **aborts** on a mismatch.

### 2. Benchpress

```bash
git clone --depth 1 https://github.com/Qiskit/benchpress.git
export BENCHPRESS_PATH=$PWD/benchpress
```

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

Five read-only checks — toolchain pin, test suite, inventory, replication, tautology
proof — in about 45 seconds. Exit 0 means the repository is intact.

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
