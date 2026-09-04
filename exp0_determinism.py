"""Experiment 0 — does seed_transpiler alone make Qiskit transpilation deterministic?

WHY THIS RUNS FIRST
    Reviewer B's critique (RESEARCH_LANDSCAPE.md sec 23, G2) raised a mechanism we had not
    considered: SABRE runs several routing trials, and if those trials are executed in
    parallel, thread scheduling could decide which one wins. If that is true, a fixed
    `seed_transpiler` does NOT give reproducible output, and every downstream claim in
    this project is void until threads are pinned.

    This is accepted as a TEST, not as a fact. This script settles it by measurement.

WHAT IT DOES
    One circuit, one fixed seed, R repeated transpilations in a single process.
    Records 2Q gate count, depth, and a SHA-256 of the emitted QASM.
    If all R hashes are identical, transpilation is deterministic under this
    configuration. If they differ, it is not.

    Run it twice -- once with RAYON_NUM_THREADS unset, once with it set to 1 -- and
    compare. The environment variable must be set BEFORE this process starts, because
    the Rust thread pool is built at import time.

CONFIGURATION
    Mirrors Benchpress's declared operating point rather than importing Benchpress:
      optimization_level = 2      (benchpress/default.conf, [qiskit])
      basis_gates        = id, sx, x, rz, cz   (default.conf, [general])
      topology           = linear (default.conf abstract_topologies)
    Benchpress builds its coupling map through FlexibleBackend; here it is a plain
    linear CouplingMap. That difference is deliberate and is recorded in the results,
    because Experiment 0 only asks about determinism, not about reproducing counts.

USAGE
    python exp0_determinism.py --qasm <path> --seed 12345 --repeats 8
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_2q(circuit) -> int:
    """Two-qubit gate count, counted from the operation table."""
    return sum(n for inst, n in circuit.count_ops().items()
               if inst not in ("barrier", "measure", "delay")
               and _arity(circuit, inst) == 2)


def _arity(circuit, name):
    for instruction in circuit.data:
        if instruction.operation.name == name:
            return len(instruction.qubits)
    return -1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qasm", required=True, help="Path to the input .qasm file")
    parser.add_argument("--seed", type=int, default=12345,
                        help="seed_transpiler value, held fixed across repeats")
    parser.add_argument("--repeats", type=int, default=8)
    parser.add_argument("--opt-level", type=int, default=2,
                        help="Benchpress default.conf [qiskit] optimization_level = 2")
    parser.add_argument("--out", default=None, help="Path to write JSON results")
    args = parser.parse_args()

    # Read the thread setting BEFORE importing qiskit, and record what it was.
    rayon_threads = os.environ.get("RAYON_NUM_THREADS", "<unset>")
    qiskit_threads = os.environ.get("QISKIT_NUM_PROCS", "<unset>")

    import qiskit
    from qiskit import qasm2, qasm3
    from qiskit.transpiler import CouplingMap
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    basis_gates = ["id", "sx", "x", "rz", "cz"]

    if not os.path.isfile(args.qasm):
        # Fail loudly on a missing path. A bare try/except around the loaders turns
        # "file not found" into a misleading "wrong QASM version" error -- that cost
        # a debugging cycle on knn_341, whose directory is knn_n341 but whose file
        # is knn_341.qasm.
        sys.exit(f"ERROR: no such file: {args.qasm}")

    try:
        circuit = qasm2.load(args.qasm,
                             include_path=(os.path.dirname(args.qasm),),
                             custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
    except qasm2.QASM2ParseError:
        circuit = qasm3.load(args.qasm)

    n_qubits = circuit.num_qubits
    coupling = CouplingMap.from_line(n_qubits)

    runs = []
    for i in range(args.repeats):
        t0 = time.perf_counter()
        pm = generate_preset_pass_manager(
            optimization_level=args.opt_level,
            basis_gates=basis_gates,
            coupling_map=coupling,
            seed_transpiler=args.seed,
        )
        out = pm.run(circuit)
        elapsed = time.perf_counter() - t0

        qasm_text = qasm2.dumps(out)
        runs.append({
            "repeat": i,
            "two_q": count_2q(out),
            "depth": out.depth(),
            "size": out.size(),
            "qasm_sha256": sha256_text(qasm_text),
            "seconds": round(elapsed, 3),
        })
        print(f"  repeat {i}: 2Q={runs[-1]['two_q']} depth={runs[-1]['depth']} "
              f"sha={runs[-1]['qasm_sha256'][:12]} ({elapsed:.1f}s)")

    hashes = {r["qasm_sha256"] for r in runs}
    two_qs = {r["two_q"] for r in runs}

    result = {
        "experiment": "exp0_determinism",
        "utc": datetime.now(timezone.utc).isoformat(),
        "qasm": os.path.basename(args.qasm),
        "n_qubits": n_qubits,
        "seed_transpiler": args.seed,
        "optimization_level": args.opt_level,
        "basis_gates": basis_gates,
        "topology": "linear",
        "repeats": args.repeats,
        "env": {
            "RAYON_NUM_THREADS": rayon_threads,
            "QISKIT_NUM_PROCS": qiskit_threads,
            "qiskit_version": qiskit.__version__,
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
        },
        "runs": runs,
        "distinct_qasm_hashes": len(hashes),
        "distinct_two_q_counts": len(two_qs),
        "two_q_values": sorted(two_qs),
        "deterministic": len(hashes) == 1,
    }

    verdict = ("DETERMINISTIC — all repeats bit-identical"
               if result["deterministic"]
               else f"NON-DETERMINISTIC — {len(hashes)} distinct circuits from one seed")
    print(f"\n  RAYON_NUM_THREADS={rayon_threads}  ->  {verdict}")
    print(f"  distinct 2Q counts: {sorted(two_qs)}")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as fh:
            json.dump(result, fh, indent=2)
        print(f"  written: {args.out}")


if __name__ == "__main__":
    main()
