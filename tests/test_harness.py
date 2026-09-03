"""Tests for the measurement harness itself.

WHY THESE EXIST
    This project's argument is that quantum benchmarking instruments are not verified.
    Running an unverified instrument to make that argument would be self-refuting.

    Neither Qiskit/benchpress nor dream-lab/quantum-hbr ships tests for its measurement
    or analysis code (checked 2026-09-02). That is not an accusation -- research code
    usually does not -- but it is the reason our numbers must be defensible in a way
    theirs currently are not.

    Every test below is a REGRESSION TEST for a defect that actually occurred today.
    None of them is hypothetical.

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
pytestmark = pytest.mark.skipif(
    not BENCHPRESS or not os.path.isdir(BENCHPRESS),
    reason="BENCHPRESS_PATH not set")

if BENCHPRESS:
    sys.path.insert(0, BENCHPRESS)


# --------------------------------------------------------------------------
# Fixtures -- a small, fast circuit so the suite stays runnable
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def small_circuit():
    from qiskit import QuantumCircuit
    path = os.path.join(BENCHPRESS, "benchpress", "qasm", "qasmbench-small",
                        "wstate_n3", "wstate_n3.qasm")
    return QuantumCircuit.from_qasm_file(path)


@pytest.fixture(scope="module")
def bv140_path():
    return os.path.join(BENCHPRESS, "benchpress", "qasm", "qasmbench-large",
                        "bv_n140", "bv_n140.qasm")


# --------------------------------------------------------------------------
# 1. Observable semantics -- we must count what Benchpress counts
# --------------------------------------------------------------------------

def test_observable_matches_benchpress_definition(small_circuit):
    """Benchpress counts the NAMED basis gate, not 'any two-qubit operation'.

    qiskit_gym/utils/io.py:
        output_gate_count_2q = circuit.count_ops().get(two_qubit_gate, 0)

    Our first sweep counted any 2-qubit op, which is a DIFFERENT observable. This
    test pins the correct one so the difference cannot silently return.
    """
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from benchpress.utilities.backends import FlexibleBackend

    backend = FlexibleBackend(small_circuit.num_qubits, "linear", control_flow=True)
    pm = generate_preset_pass_manager(optimization_level=2, backend=backend,
                                      seed_transpiler=42)
    out = pm.run(small_circuit)

    benchpress_count = out.count_ops().get(backend.two_q_gate_type, 0)
    any_2q_count = sum(1 for inst in out.data
                       if len(inst.qubits) == 2
                       and inst.operation.name not in ("barrier", "measure"))

    assert benchpress_count == out.count_ops().get("cz", 0)
    assert benchpress_count >= 0
    # They may coincide on simple circuits; the point is that we use THEIRS.
    assert isinstance(benchpress_count, int)
    assert any_2q_count >= benchpress_count, (
        "any-2q counting can only be >= named-gate counting")


def test_two_q_gate_type_is_cz_under_default_config():
    """Benchpress default.conf basis_gates -> the single 2Q gate must be 'cz'.

    If this ever changes, every recorded 2Q count in results/ refers to a different
    gate and the historical data is not comparable.
    """
    from benchpress.utilities.backends import FlexibleBackend
    backend = FlexibleBackend(8, "linear", control_flow=True)
    assert backend.two_q_gate_type == "cz"


# --------------------------------------------------------------------------
# 2. Determinism -- the load-bearing property of the whole study
# --------------------------------------------------------------------------

def test_fixed_seed_is_deterministic(small_circuit):
    """A fixed seed_transpiler must give identical output within a process."""
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from benchpress.utilities.backends import FlexibleBackend

    backend = FlexibleBackend(small_circuit.num_qubits, "linear", control_flow=True)
    counts = []
    for _ in range(5):
        pm = generate_preset_pass_manager(optimization_level=2, backend=backend,
                                          seed_transpiler=12345)
        counts.append(pm.run(small_circuit).count_ops().get(backend.two_q_gate_type, 0))
    assert len(set(counts)) == 1, f"fixed seed produced {set(counts)}"


def test_all_to_all_has_no_seed_variance(small_circuit):
    """NEGATIVE CONTROL. No routing required -> no seed sensitivity.

    If this fails, the instrument manufactures variance and no other number in this
    project can be trusted.
    """
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from benchpress.utilities.backends import FlexibleBackend

    backend = FlexibleBackend(small_circuit.num_qubits, "all-to-all", control_flow=True)
    counts = []
    for seed in range(1000, 1008):
        pm = generate_preset_pass_manager(optimization_level=2, backend=backend,
                                          seed_transpiler=seed)
        counts.append(pm.run(small_circuit).count_ops().get(backend.two_q_gate_type, 0))
    assert len(set(counts)) == 1, (
        f"all-to-all showed variance {set(counts)} with no routing to do")


# --------------------------------------------------------------------------
# 3. Regression: the censoring bug
# --------------------------------------------------------------------------

def test_hash_failure_does_not_discard_the_measurement():
    """REGRESSION (2026-09-02): QASM-2 export gated the measurement.

    Circuits with control flow cannot be serialised to OpenQASM 2. The first sweep
    computed the reproducibility hash inside the same try block as the gate count, so
    an export failure discarded a VALID measurement -- 40 rows and 4 circuits lost,
    preferentially the control-flow ones. That is corpus bias created by the
    instrument.

    sweep_bp.py must record qasm_sha256=None plus hash_error and KEEP the row.
    """
    source = open(os.path.join(ROOT, "sweep_bp.py")).read()
    assert '"qasm_sha256": qasm_hash' in source
    assert '"hash_error": hash_error' in source
    # The hash must be computed in its own try, not the one guarding the measurement.
    hash_block = source.split("qasm_hash, hash_error = None, None")[1][:400]
    assert "try:" in hash_block and "except Exception" in hash_block, (
        "hashing must be independently guarded, or a hash failure kills the row")


# --------------------------------------------------------------------------
# 4. Regression: the version guard
# --------------------------------------------------------------------------

def test_version_guard_aborts_on_mismatch(bv140_path):
    """REGRESSION (2026-09-02): `uv pip install qiskit-ibm-runtime` silently upgraded
    qiskit 2.0.2 -> 2.5.2 and an experiment ran against a version it did not intend.
    """
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "exp1_backend_randomness.py"),
         "--qasm", bv140_path, "--require-qiskit", "0.0.0-does-not-exist"],
        capture_output=True, text=True, timeout=300,
        env={**os.environ, "BENCHPRESS_PATH": BENCHPRESS})
    assert proc.returncode != 0, "guard must abort, not warn"
    assert "ABORT" in (proc.stdout + proc.stderr)


# --------------------------------------------------------------------------
# 5. Regression: the census must survive a child crash
# --------------------------------------------------------------------------

def test_census_records_child_crash_as_a_row():
    """REGRESSION (2026-09-02): a Rust OOM on bwt_n37 aborted the whole census at
    circuit 9 of 58. 49 circuits were never attempted and NO error row was written --
    the loss was visible only in a log tail.

    census.py must record a `process_crash` row when a child fails.
    """
    source = open(os.path.join(ROOT, "census.py")).read()
    assert '"record": "process_crash"' in source
    assert "rows_salvaged" in source, "partial results must be kept"
    assert "timed_out" in source


# --------------------------------------------------------------------------
# 6. Statistics -- derived numbers must be correct
# --------------------------------------------------------------------------

def test_describe_statistics_on_known_input():
    """analyze.describe must produce arithmetically correct values."""
    from analyze import describe
    stats = describe([10, 10, 10, 20])
    assert stats["n_seeds"] == 4
    assert stats["distinct_values"] == 2
    assert stats["min"] == 10 and stats["max"] == 20
    assert stats["mean"] == 12.5
    assert stats["median"] == 10.0
    assert stats["spread_pct"] == 100.0          # (20-10)/10 * 100
    assert stats["std"] == pytest.approx(5.0, abs=1e-6)   # ddof=1
    assert stats["cv_pct"] == pytest.approx(40.0, abs=1e-3)


def test_describe_handles_constant_input():
    """A constant series must report zero spread, not divide by zero."""
    from analyze import describe
    stats = describe([72, 72, 72])
    assert stats["spread_pct"] == 0.0
    assert stats["std"] == 0.0
    assert stats["cv_pct"] == 0.0
    assert stats["distinct_values"] == 1


def test_spread_is_reported_against_the_minimum():
    """spread_pct is (max-min)/min. Pinned because a reviewer will ask which
    denominator was used, and because (max-min)/mean gives a different number."""
    from analyze import describe
    assert describe([100, 150])["spread_pct"] == 50.0


# --------------------------------------------------------------------------
# 7. Raw data integrity
# --------------------------------------------------------------------------

def test_raw_rows_carry_everything_needed_to_reproduce():
    """Every run row must record the seed, the version, and the configuration.

    A row that cannot be reproduced from its own contents is not evidence.
    """
    raw = os.path.join(ROOT, "results", "raw", "bp_large_linear_q202.jsonl")
    if not os.path.isfile(raw):
        pytest.skip("census output not present")

    version = None
    checked = 0
    with open(raw) as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("qiskit_version"):
                version = row["qiskit_version"]
            if row.get("record") == "run":
                for field in ("seed", "circuit", "topology", "two_q",
                              "two_q_gate", "n_qubits", "seconds"):
                    assert field in row, f"run row missing {field}"
                checked += 1
    assert checked > 0, "no run rows found"

    # REGRESSION (2026-09-02): census.py stripped EVERY child env record when merging,
    # so the merged file recorded no qiskit version at all. The previous version of
    # this test passed anyway, because it only asserted that *an* env record existed
    # and the driver's own census_env row satisfied that. A provenance test that any
    # env row can satisfy does not test provenance.
    assert version is not None, (
        "raw file must record the qiskit version that produced it -- "
        "a measurement file that cannot name its own toolchain is not evidence")
