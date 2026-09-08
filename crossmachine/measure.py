"""Measure the frozen six-circuit set on THIS machine, and record which machine it was.

WHY THIS EXISTS AND replication/replicate.py DOES NOT SUFFICE
    Two reasons, both discovered on 2026-09-08 while preparing a second-machine run.

    1. `replicate.py --stage measure` refuses any Qiskit outside its two reference arms:
       "qiskit 1.4.3 is not one of the reference arms ['2.0.0', '2.0.2']". That guard is
       correct for the artifact -- it exists so nobody silently measures a third version
       into a two-arm comparison -- and the artifact is NOT modified to work around it.
       But the paper's PRIMARY study is 1.4.3 -> 2.0.0, so a cross-machine check that
       covers only 2.0.0 -> 2.0.2 would test the artifact and not the experiment.

    2. The artifact's env record carries qiskit version, topology, seeds, optimisation
       level and the Benchpress pin -- and NO platform, CPU count or Python version.
       That is exactly why the "across machines" claim was unprovable from the record
       and had to be withdrawn (SETTLED.json S24). A file that cannot say which machine
       produced it cannot support a claim about two machines.

WHAT IS HELD IDENTICAL
    Circuits, seeds, topology, optimisation level and the source-QASM hash check are
    IMPORTED from replication/replicate.py, not restated here. If that selection ever
    changes, this changes with it and cannot drift.

USAGE
    BENCHPRESS_PATH=<repo> envs/bp143/Scripts/python.exe crossmachine/measure.py \
        --out crossmachine/desktop_q143.jsonl --require-qiskit 1.4.3
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "replication"))

from replicate import CIRCUITS, SEEDS, TOPOLOGY, EXPECTED, check_pin, die  # noqa: E402


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", required=True)
    p.add_argument("--require-qiskit", required=True,
                   help="abort unless the running Qiskit is exactly this. Not optional: "
                        "installing qiskit-ibm-runtime once upgraded 2.0.2 to 2.5.2 "
                        "silently and an experiment ran against a version it did not "
                        "report.")
    args = p.parse_args()

    import qiskit
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    from sweep_bp import BENCHPRESS
    from benchpress.config import Configuration
    from benchpress.utilities.backends import FlexibleBackend

    if qiskit.__version__ != args.require_qiskit:
        die(f"qiskit {qiskit.__version__} != required {args.require_qiskit}")

    expected = json.load(open(EXPECTED))
    pin = check_pin(expected)          # same Benchpress revision or it stops here

    version = qiskit.__version__
    machine = {"platform": platform.platform(),
               "machine": platform.machine(),
               "processor": platform.processor(),
               "cpu_count": os.cpu_count(),
               "python": platform.python_version()}
    proc = machine["processor"] or "processor not reported"
    print(f"  qiskit {version}  |  {len(CIRCUITS)} circuits x {len(SEEDS)} seeds "
          f"on {TOPOLOGY}")
    print(f"  machine: {machine['platform']} | {proc} | "
          f"{machine['cpu_count']} cpus\n")

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

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as fh:
        fh.write(json.dumps({"record": "env", "qiskit_version": version,
                             "topology": TOPOLOGY, "seeds": SEEDS,
                             "optimization_level": opt,
                             "benchpress_path": "<redacted local path>",
                             **machine, **pin}) + "\n")
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    print(f"\n  written: {args.out}  ({len(rows)} runs)")


if __name__ == "__main__":
    main()
