# Replicate this study in about a minute

This is the smallest complete artifact that reproduces the central claim, including its
negative control. It was **executed from a clean state on 2026-09-03 and passed**:
144/144 per-seed values matched exactly, both flat circuits stayed flat, and all six
derived bands matched to within 0.01 pp of a 0.5 pp tolerance.

Running `replicate.py` *is* the replication. It exits `0` on success and `1` on any
mismatch — verified both ways by corrupting the reference file and confirming the
failure is caught and named (`2.0.2 bv_n30 seed 1003: 52 != 53`).

## What it checks, in order

1. **The toolchain pin, before any measurement.** Benchpress commit SHA, a clean
   working tree, and sha256 of the five files this study calls into. A mismatch stops
   the run — every later number would be about a different Benchpress.
2. **Every source circuit's QASM hash** against the reference.
3. **Determinism.** A fixed `seed_transpiler` must reproduce the 2-qubit gate count
   exactly, for all 6 circuits × 12 seeds × 2 versions.
4. **Seed sensitivity.** On the same circuit and the same topology, different seeds
   must give different counts. `dnn_n33` gives **12 distinct values from 12 seeds**.
5. **The negative control.** `cat_n35` and `ghz_n40` must be *constant* across all 12
   seeds. Without this the run cannot distinguish the effect from something global,
   and a suite that only ever demonstrates the positive case is not a control.
6. **The derived statistic.** The unpaired ambiguity band is recomputed from the fresh
   measurements and compared to the committed reference.

## Requirements

- Two Python environments, one per Qiskit version under comparison (2.0.0 and 2.0.2).
  Install `qiskit==<version>` together with `qiskit-ibm-runtime rustworkx scipy` in a
  **single** resolution — installing the runtime afterwards silently upgrades Qiskit,
  which is how defect §26 happened here.
- A Benchpress checkout at commit `b695f30e83a32bac05b9b4d8e98d37ba9aae5236`:

  ```
  git clone https://github.com/Qiskit/benchpress
  git -C benchpress checkout b695f30e83a32bac05b9b4d8e98d37ba9aae5236
  ```

  The working tree must be clean. `results/raw/benchpress_pin.json` carries the module
  hashes and the sha256 of all 58 `qasmbench-large` circuits if you want to verify the
  checkout independently.

## Run it

```sh
export BENCHPRESS_PATH=/path/to/benchpress

# once per version, using that version's interpreter
<py-2.0.2> replication/replicate.py --stage measure --out replication/out_q202.jsonl
<py-2.0.0> replication/replicate.py --stage measure --out replication/out_q200.jsonl

# then, in either environment
<py-2.0.2> replication/replicate.py --stage verify \
    --old replication/out_q200.jsonl --new replication/out_q202.jsonl
```

Measurement is about 3 seconds per arm. On Windows, use `envs/bp202/Scripts/python.exe`
and `envs/bp200/Scripts/python.exe`.

## Expected output

```
  pin OK   benchpress b695f30e83a3, 5 modules hash-matched
  qiskit 2.0.2  |  6 circuits x 12 seeds on heavy-hex

  bv_n30       10 distinct value(s) across 12 seeds  min 48 max 70
  knn_n31      11 distinct value(s) across 12 seeds  min 195 max 224
  adder_n28    11 distinct value(s) across 12 seeds  min 387 max 440
  dnn_n33      12 distinct value(s) across 12 seeds  min 347 max 406
  cat_n35       1 distinct value(s) across 12 seeds  min 34 max 34
  ghz_n40       1 distinct value(s) across 12 seeds  min 39 max 39
```

```
  per-seed values : 144/144 match exactly
  seed-sensitive  : 4/6 (bv_n30, knn_n31, adder_n28, dnn_n33)
  negative control: 2/6 constant across all 12 seeds (cat_n35, ghz_n40)

  circuit        band now  reference    delta
  bv_n30         26.83 pp   26.83 pp   -0.00
  knn_n31        11.43 pp   11.43 pp   -0.00
  adder_n28      10.69 pp   10.69 pp   -0.00
  dnn_n33        13.50 pp   13.50 pp   +0.00
  cat_n35         0.00 pp    0.00 pp   +0.00
  ghz_n40         0.00 pp    0.00 pp   +0.00

  REPLICATION PASSED
```

## What a failure means

| failure | reading |
|---|---|
| pin mismatch | Stop. Every number below it is about a different Benchpress. |
| circuit QASM hash mismatch | Your corpus differs from ours; the comparison is void. |
| per-seed value mismatch | Your toolchain differs somewhere the pin did not catch. The report names circuit and seed. Report it — cross-platform value drift would be a finding in its own right. |
| no circuit varied with the seed | The central claim did not reproduce. |
| every circuit varied | The negative control is gone; this run cannot separate the effect from a global one. |
| band mismatch with values matching | A bug in the analysis, not the measurement. |

## Why six circuits and not fifty-two

The full census is roughly 40 minutes per arm and needs process isolation, because
`bwt_n37` exhausts the Rust allocator and takes the whole run down with it (that is why
`census.py` exists). Nobody re-runs 40 minutes to check a claim, so nobody checks it.

These six run in about three seconds: the four fastest circuits whose measured
between-version change varies by seed, plus two of the fastest whose change is
identical at every seed. The full censuses in `results/raw/` remain the evidence; this
is the entry point.

## Scope — what this artifact does NOT show

- It does not show that any Qiskit version is better or worse than another. It uses the
  2.0.0 → 2.0.2 pair only as a source of a **measured per-seed residual**.
- It does not attribute anything to a specific pull request. See §39.
- Six circuits on one topology cannot support a corpus-level proportion. For that, use
  the full censuses and `paired.py --band`.
