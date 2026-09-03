# Seed variance in Qiskit Benchpress

Benchpress pins the seeds used to **build** circuits and passes no seed to the code that
**compiles** them. This repository measures what that costs.

**Headline:** on `qft_n320`, Qiskit 2.0.0 and 2.0.2 produce **byte-identical output at
every seed tested**. The regression protocol used in Qiskit issue
[#14402](https://github.com/Qiskit/qiskit/issues/14402) — three runs per version,
averaged — reports it as a **double-digit regression 27% of the time**. Passing
`seed_transpiler` reduces that to **zero**.

---

## What was measured

| result | value | where |
|---|---|---|
| Benchpress unseeded, `bv_n140-linear`, 20 runs | **17 distinct 2Q gate counts**, 244–340 | §27 |
| `qft_n320`, paired by seed across 2.0.0 / 2.0.2 | **0.00% difference, 12/12 seeds** | §31 |
| `qft_n320`, unpaired 3-run protocol | **27.1% false-positive rate** | §31–32 |
| real +10.7% regression on `adder_n64` | **missed 19.7% of the time** | §31 |
| circuits with a seed-dependent verdict | **5 of 57** (linear, +10% threshold) | §31 |
| holds across thresholds 5%–30% | **4–9 circuits, never zero** | §31 |
| runs needed for every circuit <5% FP | **~50 per version** (≈200 h compute) | §34 |
| same reliability, paired | **k=1** | §34 |
| circuits ≥5% spread, `square` topology | **29 of 58** | §35 |
| independent replication, different machine and CPU vendor | **fixed seed → identical value** | §29 |

Section numbers refer to [`RESEARCH_LANDSCAPE.md`](RESEARCH_LANDSCAPE.md), the full
research record, including every hypothesis that was **refuted** and every defect found
in this harness.

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
  stochastic here; the ambiguity window is a bound, not a demonstrated reversal.
- **Not** that "the benchmark is broken." 24 circuits detect the real regression on
  essentially every draw. The failure is at the margins, and the margins are quantified.

---

## Licence

Code: MIT. Data and text: CC BY 4.0.
