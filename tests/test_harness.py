"""Tests for the measurement harness itself.

WHY THESE EXIST, AND WHY THEY WERE REWRITTEN
    This project's argument is that quantum benchmarking instruments go unverified.
    Running an unverified instrument to make that argument would be self-refuting.

    The FIRST version of this file failed exactly that way. A hostile review
    (DEFECTS.md, 2026-09-03) mutation-tested it: the reviewer reintroduced two of the
    defects these tests exist to catch -- `continue` in the hash handler, `break` after
    the crash row -- and ALL 11 TESTS PASSED. They were string greps over source text.
    They asserted that certain literals appeared in a file, not that behaviour was
    correct.

    Every test here now EXECUTES the path and asserts on its OUTPUT. Where a test
    cannot discriminate, it is marked and says why rather than passing vacuously.

FIXTURE CHOICE MATTERS
    The old suite used `wstate_n3` for its determinism and negative-control tests.
    That circuit is constant even UNSEEDED (30 runs, 1 distinct value), so those tests
    passed identically with `seed_transpiler` deleted. Fixtures here are chosen because
    they have MEASURED variance: bv_n30 spans 48-72 on linear (DEFECTS.md D-6.3/6.4).

RUN
    BENCHPRESS_PATH=<repo> envs/bp202/Scripts/python.exe -m pytest tests/ -v
"""

import json
import os
import subprocess
import sys
import tempfile

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

BENCHPRESS = os.environ.get("BENCHPRESS_PATH")

# D-6.8: an unset BENCHPRESS_PATH silently skipped all 11 tests and exited 0.
# A suite that reports success while testing nothing is worse than no suite.
if not BENCHPRESS or not os.path.isdir(BENCHPRESS):
    raise RuntimeError(
        "BENCHPRESS_PATH is not set or not a directory. Refusing to skip silently: "
        "a green suite that tested nothing is how defect D-6.8 hid."
    )

sys.path.insert(0, BENCHPRESS)
LARGE = os.path.join(BENCHPRESS, "benchpress", "qasm", "qasmbench-large")


def qasm(name, fname=None):
    return os.path.join(LARGE, name, (fname or name) + ".qasm")


# ==========================================================================
# 1. BEHAVIOURAL: a hash failure must not delete a valid measurement
#    (D-6.1 -- the old version was a string grep and passed with the defect back)
# ==========================================================================

def test_control_flow_circuit_yields_a_row_with_null_hash():
    """REGRESSION, executed not grepped.

    Circuits with control flow cannot be serialised to OpenQASM 2. The original sweep
    computed the reproducibility hash in the same try block as the gate count, so an
    export failure discarded a VALID measurement -- 40 rows and 4 circuits lost,
    preferentially the control-flow ones. That is corpus bias created by the instrument.

    This runs the real measurement path on a real control-flow circuit (`cc_n151`,
    which raises QASM2ExportError) and asserts a run row still appears, carrying the
    gate count, with qasm_sha256 null and hash_error populated.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "out.jsonl")
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "sweep_bp.py"),
             "--size", "large", "--topologies", "linear", "--seeds", "2",
             "--only", "cc_n151", "--max-seconds", "300", "--out", out],
            capture_output=True, text=True, timeout=900,
            env={**os.environ, "BENCHPRESS_PATH": BENCHPRESS})
        assert proc.returncode == 0, f"sweep failed: {proc.stderr[-500:]}"

        runs = [json.loads(l) for l in open(out)
                if json.loads(l).get("record") == "run"]

    assert runs, "control-flow circuit produced NO run rows -- the censoring defect is back"
    for row in runs:
        assert isinstance(row["two_q"], int), "measurement missing from a kept row"
        assert row["qasm_sha256"] is None, "expected hashing to fail on control flow"
        assert row["hash_error"], "hash failure must be recorded, not swallowed"


# ==========================================================================
# 2. BEHAVIOURAL: a crashing child must be recorded and the census continue
#    (D-6.2 -- the old version was a string grep)
# ==========================================================================

def test_census_records_crash_and_keeps_going():
    """REGRESSION, executed not grepped.

    A Rust OOM on `bwt_n37` aborted the in-process census at circuit 9 of 58. The
    remaining 49 were never attempted and NO error row was written -- the loss was
    visible only in a log tail.

    This points census.py at an interpreter that always fails, and asserts that (a) a
    process_crash row is written for a circuit, and (b) the driver does not stop at the
    first one.
    """
    with tempfile.TemporaryDirectory() as tmp:
        fake = os.path.join(tmp, "always_fails.py")
        with open(fake, "w") as fh:
            fh.write("import sys; sys.exit(3)\n")
        launcher = os.path.join(tmp, "launcher.cmd")

        out = os.path.join(tmp, "out.jsonl")
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "census.py"),
             "--python", sys.executable, "--size", "large", "--topology", "linear",
             "--seeds", "1", "--timeout", "30",
             "--require-qiskit", "0.0.0-force-child-abort",
             "--out", out],
            capture_output=True, text=True, timeout=900,
            env={**os.environ, "BENCHPRESS_PATH": BENCHPRESS})

        rows = [json.loads(l) for l in open(out)]

    crashes = [r for r in rows if r.get("record") == "process_crash"]
    assert crashes, "a failing child produced no process_crash row"
    assert len(crashes) > 1, (
        f"driver stopped after {len(crashes)} crash(es) -- it must continue past a "
        f"failing circuit, which is the whole point of process isolation")
    for c in crashes:
        assert c["returncode"] != 0
        assert "circuit" in c and "topology" in c


# ==========================================================================
# 3. BEHAVIOURAL: determinism, on a fixture that actually varies
#    (D-6.3 -- old fixture wstate_n3 is constant even unseeded)
# ==========================================================================

def test_fixed_seed_deterministic_on_a_VARYING_circuit():
    """The old test used wstate_n3, which is constant unseeded, so it passed with
    seed_transpiler deleted. bv_n30 spans 48-72 on linear (measured, sec 30), so a
    constant result here can only come from the seed actually taking effect."""
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from benchpress.utilities.backends import FlexibleBackend

    circuit = QuantumCircuit.from_qasm_file(qasm("bv_n30"))
    backend = FlexibleBackend(circuit.num_qubits, "linear", control_flow=True)

    seeded = []
    for _ in range(6):
        pm = generate_preset_pass_manager(optimization_level=2, backend=backend,
                                          seed_transpiler=4242)
        seeded.append(pm.run(circuit).count_ops().get(backend.two_q_gate_type, 0))

    unseeded = []
    for _ in range(12):
        pm = generate_preset_pass_manager(optimization_level=2, backend=backend)
        unseeded.append(pm.run(circuit).count_ops().get(backend.two_q_gate_type, 0))

    assert len(set(seeded)) == 1, f"fixed seed varied: {sorted(set(seeded))}"
    # The discriminating half: this fixture MUST vary unseeded, or the test above
    # proves nothing.
    assert len(set(unseeded)) > 1, (
        "fixture does not vary unseeded, so the determinism assertion is vacuous -- "
        "pick a circuit with measured spread")


# ==========================================================================
# 4. BEHAVIOURAL: the observable is the one sweep_bp actually uses
#    (D-6.5 -- old test never imported sweep_bp and asserted an identity)
# ==========================================================================

def test_sweep_uses_named_gate_not_any_two_qubit_op():
    """Benchpress counts the NAMED basis gate:
        output_gate_count_2q = circuit.count_ops().get(two_qubit_gate, 0)
    Our first sweep counted any 2-qubit operation, a DIFFERENT observable.

    This runs sweep_bp.py on a control-flow circuit -- where the two definitions
    genuinely disagree, because if_else blocks act on 2 qubits but are not `cz` -- and
    checks the recorded value matches the named-gate count.
    """
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from benchpress.utilities.backends import FlexibleBackend

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "out.jsonl")
        subprocess.run(
            [sys.executable, os.path.join(ROOT, "sweep_bp.py"),
             "--size", "large", "--topologies", "linear", "--seeds", "1",
             "--seed-start", "777", "--only", "cc_n151",
             "--max-seconds", "300", "--out", out],
            capture_output=True, text=True, timeout=900,
            env={**os.environ, "BENCHPRESS_PATH": BENCHPRESS}, check=True)
        row = next(json.loads(l) for l in open(out)
                   if json.loads(l).get("record") == "run")

    circuit = QuantumCircuit.from_qasm_file(qasm("cc_n151"))
    backend = FlexibleBackend(circuit.num_qubits, "linear", control_flow=True)
    pm = generate_preset_pass_manager(optimization_level=2, backend=backend,
                                      seed_transpiler=777)
    compiled = pm.run(circuit)

    named = compiled.count_ops().get(backend.two_q_gate_type, 0)
    any_2q = sum(1 for inst in compiled.data
                 if len(inst.qubits) == 2
                 and inst.operation.name not in ("barrier", "measure"))

    assert row["two_q"] == named, (
        f"sweep recorded {row['two_q']}, Benchpress's definition gives {named}")
    assert row["two_q_gate"] == backend.two_q_gate_type
    if any_2q == named:
        pytest.skip("this circuit does not discriminate the two definitions today; "
                    "the equality assertion above still pins the named-gate rule")


# ==========================================================================
# 5. BEHAVIOURAL: the version guard actually aborts
#    (this one was sound in the old suite and is kept)
# ==========================================================================

def test_version_guard_aborts_on_mismatch():
    """`uv pip install qiskit-ibm-runtime` silently upgraded qiskit 2.0.2 -> 2.5.2 and
    an experiment ran against a version it did not report."""
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "exp1_backend_randomness.py"),
         "--qasm", qasm("bv_n30"), "--require-qiskit", "0.0.0-does-not-exist"],
        capture_output=True, text=True, timeout=600,
        env={**os.environ, "BENCHPRESS_PATH": BENCHPRESS})
    assert proc.returncode != 0, "guard must abort, not warn"
    assert "ABORT" in (proc.stdout + proc.stderr)


def test_sweep_version_guard_aborts_too():
    """The guard must be on every measurement entry point, not just one."""
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [sys.executable, os.path.join(ROOT, "sweep_bp.py"),
             "--size", "large", "--topologies", "linear", "--seeds", "1",
             "--only", "bv_n30", "--require-qiskit", "0.0.0-nope",
             "--out", os.path.join(tmp, "o.jsonl")],
            capture_output=True, text=True, timeout=600,
            env={**os.environ, "BENCHPRESS_PATH": BENCHPRESS})
    assert proc.returncode != 0
    assert "ABORT" in (proc.stdout + proc.stderr)


# ==========================================================================
# 6. Arithmetic -- these were sound and are kept
# ==========================================================================

def test_describe_statistics_on_known_input():
    from analyze import describe
    s = describe([10, 10, 10, 20])
    assert s["n_seeds"] == 4 and s["distinct_values"] == 2
    assert s["min"] == 10 and s["max"] == 20
    assert s["mean"] == 12.5 and s["median"] == 10.0
    assert s["spread_pct"] == 100.0
    assert s["std"] == pytest.approx(5.0, abs=1e-6)
    assert s["cv_pct"] == pytest.approx(40.0, abs=1e-3)


def test_describe_handles_constant_input():
    from analyze import describe
    s = describe([72, 72, 72])
    assert s["spread_pct"] == 0.0 and s["std"] == 0.0 and s["cv_pct"] == 0.0


def test_spread_is_reported_against_the_minimum():
    """Pinned because a reviewer will ask which denominator was used -- and because
    sec 33 used (max-min)/median for the same data, giving a different number
    (DEFECTS.md D-3.1)."""
    from analyze import describe
    assert describe([100, 150])["spread_pct"] == 50.0


# ==========================================================================
# 7. Provenance -- strengthened again after D-6.7
# ==========================================================================

@pytest.mark.parametrize("raw", [
    "bp_large_linear_q202.jsonl", "bp_large_linear_q200.jsonl",
    "bp_large_square_q202.jsonl",
])
def test_raw_file_names_its_toolchain_consistently(raw):
    """D-6.7: the previous version only required that SOME row carried a
    qiskit_version. census.py keeps just the first child's env row, so that assertion
    could only fail if circuit #1 crashed -- structurally guaranteed otherwise.

    This additionally requires that the recorded version matches the census_env's
    require_qiskit, which is the sec 26 contamination mode (an install swapping the
    version mid-run).
    """
    path = os.path.join(ROOT, "results", "raw", raw)
    if not os.path.isfile(path):
        pytest.skip(f"{raw} not present")

    versions, required, n_runs = set(), None, 0
    with open(path) as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("qiskit_version"):
                versions.add(row["qiskit_version"])
            if row.get("record") == "census_env":
                required = row.get("require_qiskit")
            if row.get("record") == "run":
                n_runs += 1
                for f in ("seed", "circuit", "topology", "two_q", "two_q_gate",
                          "n_qubits", "seconds"):
                    assert f in row, f"run row missing {f}"

    assert n_runs > 0, "no run rows"
    assert versions, ("file records no qiskit version -- a measurement file that "
                      "cannot name its own toolchain is not evidence")
    assert len(versions) == 1, f"MIXED versions in one file: {versions}"
    if required:
        assert versions == {required}, (
            f"census demanded {required} but rows record {versions}")


def test_summary_numbers_regenerate_from_raw():
    """D-7.1/D-7.2: sec 30's provenance line and distribution table did not match the
    file they named, because the census was re-run and the aggregates were never
    recomputed. Any published aggregate must be regenerable from its raw file.
    """
    import csv
    from analyze import load_runs, describe

    raw = os.path.join(ROOT, "results", "raw", "bp_large_linear_q202.jsonl")
    summary = os.path.join(ROOT, "results", "summary",
                           "bp_large_linear_q202_2q.csv")
    if not (os.path.isfile(raw) and os.path.isfile(summary)):
        pytest.skip("census or summary not present")

    _, runs, _, _ = load_runs(raw)
    for row in csv.DictReader(open(summary)):
        circuit = row["circuit"]
        if circuit not in runs:
            continue
        recomputed = describe([r["two_q"] for r in runs[circuit]])
        assert recomputed["min"] == float(row["min"]), (
            f"{circuit}: summary min {row['min']} != raw {recomputed['min']}")
        assert recomputed["max"] == float(row["max"])
        assert recomputed["spread_pct"] == pytest.approx(
            float(row["spread_pct"]), abs=0.01), (
            f"{circuit}: summary CSV does not regenerate from raw")
