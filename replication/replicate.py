"""Priority 5 — the smallest complete replication artifact. Built to be RUN.

WHAT THIS IS
    Six circuits, two Qiskit versions, twelve seeds, one topology. It reproduces the
    whole chain end to end in under a minute:

        1. the toolchain pin is verified before anything is measured
        2. a fixed seed reproduces a 2-qubit gate count exactly
        3. different seeds produce different counts on the SAME circuit and topology
        4. two of the six circuits show NO seed sensitivity at all -- the negative
           control, without which this is just a demonstration of the positive case
        5. the unpaired ambiguity band is recomputed and compared to the committed
           reference within a stated tolerance

    It exits non-zero on any mismatch. It is not documentation describing a
    replication; running it IS the replication.

WHY SIX CIRCUITS AND NOT FIFTY-TWO
    The full census is ~40 minutes per arm and needs process isolation because
    `bwt_n37` OOMs the Rust allocator. Nobody re-runs that to check a claim. These six
    total about three seconds per arm and were chosen before any of them was looked
    at again: the four fastest heterogeneous circuits plus two of the fastest circuits
    with a measured rho spread of exactly zero.

WHAT A FAILURE MEANS
    per-seed value mismatch  : your toolchain differs from ours somewhere the pin did
                               not catch. The report names the circuit and seed.
    band mismatch            : the derived statistic moved even though the raw values
                               did not -- a bug in the analysis, not the measurement.
    pin mismatch             : stop. Every number below is about a different Benchpress.

USAGE
    # once per version, in that version's environment
    BENCHPRESS_PATH=<repo> python replication/replicate.py --stage measure \
        --out replication/out_q202.jsonl
    BENCHPRESS_PATH=<repo> python replication/replicate.py --stage measure \
        --out replication/out_q200.jsonl        # with the 2.0.0 interpreter

    # then, in either
    python replication/replicate.py --stage verify \
        --old replication/out_q200.jsonl --new replication/out_q202.jsonl
"""

import argparse
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

EXPECTED = os.path.join(HERE, "expected.json")
TOPOLOGY = "heavy-hex"
SEEDS = list(range(1000, 1012))
CIRCUITS = ["bv_n30", "knn_n31", "adder_n28", "dnn_n33",   # seed-sensitive
            "cat_n35", "ghz_n40"]                          # negative controls
BAND_TOL_PP = 0.5


def die(msg):
    print(f"\n  FAIL: {msg}\n")
    sys.exit(1)


def check_pin(expected):
    """Refuse to measure against an unverified Benchpress. This runs FIRST."""
    from sweep_bp import PINNED_MODULES, benchpress_pin
    pin = benchpress_pin()
    want = expected["benchpress_pin"]
    problems = []
    if pin["benchpress_commit"] != want["benchpress_commit"]:
        problems.append(f"commit {pin['benchpress_commit']} != "
                        f"{want['benchpress_commit']}")
    if pin["benchpress_dirty"]:
        problems.append("benchpress working tree is DIRTY")
    for rel in PINNED_MODULES:
        got = pin["benchpress_module_sha256"].get(rel)
        exp = want["benchpress_module_sha256"].get(rel)
        if got != exp:
            problems.append(f"{rel}: {got} != {exp}")
    if problems:
        die("Benchpress does not match the pin:\n    " + "\n    ".join(problems))
    print(f"  pin OK   benchpress {pin['benchpress_commit'][:12]}, "
          f"{len(PINNED_MODULES)} modules hash-matched")
    return pin


def measure(args):
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    from sweep_bp import BENCHPRESS
    from benchpress.config import Configuration
    from benchpress.utilities.backends import FlexibleBackend

    expected = json.load(open(EXPECTED))
    pin = check_pin(expected)

    version = qiskit.__version__
    if version not in expected["arms"]:
        die(f"qiskit {version} is not one of the reference arms "
            f"{sorted(expected['arms'])}")
    print(f"  qiskit {version}  |  {len(CIRCUITS)} circuits x {len(SEEDS)} seeds "
          f"on {TOPOLOGY}\n")

    opt = Configuration.options["qiskit"]["optimization_level"]
    qasm_dir = Configuration.get_qasm_dir("qasmbench-large")

    rows = []
    for name in CIRCUITS:
        path = os.path.join(qasm_dir, name, name + ".qasm")
        if not os.path.isfile(path):
            die(f"circuit file missing: {path}")
        with open(path, "rb") as fh:
            in_hash = hashlib.sha256(fh.read()).hexdigest()
        exp_hash = expected["circuits"][name]["input_qasm_sha256"]
        if in_hash != exp_hash:
            die(f"{name}: source QASM hash {in_hash} != reference {exp_hash}")

        circuit = QuantumCircuit.from_qasm_file(path)
        backend = FlexibleBackend(circuit.num_qubits, TOPOLOGY, control_flow=True)
        two_q_gate = backend.two_q_gate_type
        t0 = time.perf_counter()
        for seed in SEEDS:
            pm = generate_preset_pass_manager(optimization_level=opt, backend=backend,
                                              seed_transpiler=seed)
            out = pm.run(circuit)
            rows.append({"record": "run", "circuit": name, "topology": TOPOLOGY,
                         "seed": seed, "two_q_gate": two_q_gate,
                         "two_q": out.count_ops().get(two_q_gate, 0),
                         "input_qasm_sha256": in_hash})
        vals = [r["two_q"] for r in rows if r["circuit"] == name]
        print(f"  {name:<12s} {len(set(vals))} distinct value(s) across "
              f"{len(SEEDS)} seeds  min {min(vals)} max {max(vals)}  "
              f"({time.perf_counter()-t0:.1f}s)")

    with open(args.out, "w") as fh:
        fh.write(json.dumps({"record": "env", "qiskit_version": version,
                             "topology": TOPOLOGY, "seeds": SEEDS,
                             "optimization_level": opt,
                             "benchpress_path": BENCHPRESS, **pin}) + "\n")
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"\n  written: {args.out}")


def _load(path):
    vals, version = {}, None
    for line in open(path):
        row = json.loads(line)
        if row.get("qiskit_version"):
            version = row["qiskit_version"]
        if row.get("record") == "run":
            vals.setdefault(row["circuit"], {})[row["seed"]] = row["two_q"]
    if version is None:
        die(f"{path} records no qiskit_version")
    return vals, version


def verify(args):
    import numpy as np
    from paired import _solve, BAND_LO, BAND_HI

    expected = json.load(open(EXPECTED))
    old, v_old = _load(args.old)
    new, v_new = _load(args.new)
    print(f"\n  comparing qiskit {v_old} -> {v_new} against the committed reference\n")

    failures, checks = [], 0
    for arm, (vals, version) in (("old", (old, v_old)), ("new", (new, v_new))):
        ref = expected["arms"].get(version)
        if ref is None:
            die(f"no reference arm for qiskit {version}")
        for name in CIRCUITS:
            for seed in SEEDS:
                checks += 1
                got = vals.get(name, {}).get(seed)
                want = ref[name][str(seed)]
                if got != want:
                    failures.append(f"{version} {name} seed {seed}: {got} != {want}")

    n_bad_values = len(failures)
    print(f"  per-seed values : {checks - n_bad_values}/{checks} match exactly")

    # 2. determinism and variability, asserted on THIS run's own numbers
    sensitive = [c for c in CIRCUITS
                 if len({new[c][s] for s in SEEDS}) > 1]
    flat = [c for c in CIRCUITS if c not in sensitive]
    print(f"  seed-sensitive  : {len(sensitive)}/{len(CIRCUITS)} "
          f"({', '.join(sensitive) or 'none'})")
    print(f"  negative control: {len(flat)}/{len(CIRCUITS)} constant across all 12 "
          f"seeds ({', '.join(flat) or 'none'})")
    if not sensitive:
        failures.append("NO circuit varied with the seed -- the central claim did "
                        "not reproduce at all")
    if not flat:
        failures.append("every circuit varied -- the negative control is gone, so "
                        "this run cannot distinguish the effect from a global one")

    # 3. the derived statistic
    print(f"\n  {'circuit':<12s} {'band now':>10s} {'reference':>10s} {'delta':>8s}")
    for name in CIRCUITS:
        o = np.array([old[name][s] for s in SEEDS], dtype=float)
        n = np.array([new[name][s] for s in SEEDS], dtype=float)
        ratio = n / o
        rho = ratio / ratio.mean()
        lo = _solve(o, rho, BAND_LO, expected["threshold"], expected["k"], False)
        hi = _solve(o, rho, BAND_HI, expected["threshold"], expected["k"], False)
        got = 0.0 if (np.isnan(lo) or np.isnan(hi)) else (hi - lo) * 100
        want = expected["band_unpaired_pp"][name]
        delta = got - want
        flag = "" if abs(delta) <= BAND_TOL_PP else "   <-- MISMATCH"
        if abs(delta) > BAND_TOL_PP:
            failures.append(f"{name}: unpaired band {got:.2f} pp != "
                            f"{want:.2f} pp (tolerance {BAND_TOL_PP} pp)")
        print(f"  {name:<12s} {got:>7.2f} pp {want:>7.2f} pp {delta:>+7.2f}{flag}")

    if failures:
        print(f"\n  {len(failures)} FAILURE(S):")
        for f in failures[:20]:
            print(f"    - {f}")
        if len(failures) > 20:
            print(f"    ... and {len(failures) - 20} more")
        sys.exit(1)
    print(f"\n  REPLICATION PASSED — every per-seed value, both controls, and every "
          f"band matched.\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=["measure", "verify"], required=True)
    p.add_argument("--out")
    p.add_argument("--old")
    p.add_argument("--new")
    args = p.parse_args()
    if args.stage == "measure":
        if not args.out:
            p.error("--stage measure needs --out")
        measure(args)
    else:
        if not (args.old and args.new):
            p.error("--stage verify needs --old and --new")
        verify(args)


if __name__ == "__main__":
    main()
