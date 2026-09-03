# Seed variance in Qiskit Benchpress

Benchpress pins the seeds used to **build** circuits and passes no seed to the code that
**compiles** them. This repository measures what that costs.

**Headline:** the suite's regression protocol — three unseeded runs per version, as used
in Qiskit issue [#14402](https://github.com/Qiskit/qiskit/issues/14402) — **cannot
resolve a change smaller than a median 14-percentage-point window** around a +10%
decision threshold on a heavy-hex lattice. Passing `seed_transpiler` narrows that window
**6.8×**. One argument, one run per version, instead of roughly fifty.

> ⚠ **An earlier headline here claimed a 27% false-positive rate on `qft_n320`. It is
> WITHDRAWN** — its 95% interval was [1.7%, 63.1%] at n=12, and the corpus statistic
> built on it turned out to depend on an undisclosed choice of which version was the
> baseline. See §38 and §41. Nothing was ever published. Every number below is
> direction-free and re-derives from raw data via `python inventory.py --check`.

---

## What was measured

| result | value | where |
|---|---|---|
| Benchpress gyms passing `seed_transpiler` | **0 of 8**, source-verified | §33 |
| Benchpress unseeded, `bv_n140-linear`, 20 runs | **17 distinct 2Q gate counts**, 244–340 | §27 |
| the seed is the entropy source | cross-process control, seeded 324×6 vs unseeded 6 values | §28 |
| **unpaired ambiguity band, heavy-hex** | **median 14.04 pp** | §42 |
| **paired ambiguity band, heavy-hex** | **median 2.06 pp — 6.8× narrower** | §42 |
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
```

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
- **Not** that any real decision was ever wrong. No wrong call has been demonstrated on
  Qiskit, and #14402's own cases have never been reproduced as verdict flips (§45 A1).
- **Not** that a real code change behaves like the injected one. §42's band sweeps a
  multiplicative change with a *measured* per-seed residual. Nothing here verifies that
  real compiler changes act that way (§45 A2).
- **Not** a claim about IBM hardware. `heavy-hex` here is
  `rustworkx.generators.heavy_hex_graph(dim)` sized to the circuit — the lattice family
  IBM uses, generated synthetically, with no device coupling map and no calibration.

---

## Licence

Code: MIT. Data and text: CC BY 4.0.
