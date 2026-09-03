"""Benchpress-matched seed sweep. Uses Benchpress's own code, not a reimplementation.

WHY THIS EXISTS
    The earlier sweep (sweep.py) approximated Benchpress: a plain linear CouplingMap,
    and a 2Q count over any two-qubit operation. Benchpress does neither. This script
    imports and calls Benchpress's own objects so equivalence is true by construction
    rather than something to be tested and hoped for:

      backend   benchpress.utilities.backends.FlexibleBackend(n, topo, control_flow=True)
      loader    benchpress.utilities.io.get_qasmbench_circuits
      observable  circuit.count_ops().get(backend.two_q_gate_type, 0)
                  and circuit.depth(filter_function=name == two_q_gate_type)
                  -- verbatim from benchpress/qiskit_gym/utils/io.py
      opt level Configuration.options["qiskit"]["optimization_level"]  (= 2)
      topologies Configuration.options["general"]["abstract_topologies"]
                  = ['all-to-all', 'square', 'heavy-hex', 'linear']

    Benchpress parametrises EVERY circuit against EVERY topology, with test ids of the
    form "<circuit>-<topology>" (workouts/abstract_transpile/qasmbench.py). So
    "bv_n140-linear" from issue #14402 is one of four tests for that circuit.

BUILT-IN NEGATIVE CONTROL
    'all-to-all' requires no routing, so SABRE has nothing stochastic to do and seed
    variance should be ~0. If it is not, the instrument is wrong and no other number
    here can be trusted. Always run it alongside the topology under test.

TWO DEFECTS FROM THE PREVIOUS SWEEP, FIXED HERE
    1. Censoring. Hashing used QASM-2 export, which cannot represent control flow, so
       an export failure discarded a VALID gate count -- preferentially deleting
       control-flow circuits (40 rows, 4 circuits lost). Hashing is now best-effort:
       failure records qasm_sha256=null plus hash_error, and the row is KEPT.
    2. Version drift. `uv pip install qiskit-ibm-runtime` silently upgraded qiskit
       2.0.2 -> 2.5.2 mid-session. --require-qiskit now refuses to run on a mismatch.

USAGE
    BENCHPRESS_PATH=<repo> python sweep_bp.py --size large --topologies linear,all-to-all \
        --seeds 12 --require-qiskit 2.0.2 --out results/raw/bp_large_q202.jsonl
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

BENCHPRESS = os.environ.get("BENCHPRESS_PATH")
if not BENCHPRESS or not os.path.isdir(BENCHPRESS):
    sys.exit("ERROR: set BENCHPRESS_PATH to the benchpress repo root")
sys.path.insert(0, BENCHPRESS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", default="large", choices=["small", "medium", "large"])
    parser.add_argument("--topologies", default="linear,all-to-all",
                        help="Comma-separated subset of Benchpress abstract_topologies")
    parser.add_argument("--seeds", type=int, default=12)
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--max-seconds", type=float, default=120.0,
                        help="Per (circuit, topology) cumulative budget. Recorded, "
                             "never silent.")
    parser.add_argument("--require-qiskit", default=None)
    parser.add_argument("--only", default=None,
                        help="Run a single circuit by name. Used by census.py, which "
                             "spawns one process per circuit so that a hard crash "
                             "(e.g. the Rust OOM on bwt_n37) costs one circuit rather "
                             "than the whole census. A Rust allocation failure aborts "
                             "the process and cannot be caught by try/except.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    import qiskit
    if args.require_qiskit and qiskit.__version__ != args.require_qiskit:
        sys.exit(f"ABORT: require-qiskit={args.require_qiskit} but environment has "
                 f"qiskit {qiskit.__version__}. Refusing to mislabel a measurement.")

    from qiskit import qasm2, QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from benchpress.config import Configuration
    from benchpress.utilities.backends import FlexibleBackend
    from benchpress.utilities.io import get_qasmbench_circuits

    opt_level = Configuration.options["qiskit"]["optimization_level"]
    all_topologies = Configuration.options["general"]["abstract_topologies"]
    topologies = [t.strip() for t in args.topologies.split(",")]
    for topo in topologies:
        if topo not in all_topologies:
            sys.exit(f"ABORT: '{topo}' not in Benchpress abstract_topologies "
                     f"{all_topologies}")

    qasm_dir = Configuration.get_qasm_dir(f"qasmbench-{args.size}")
    # get_qasmbench_circuits returns FILE PATHS and names, not circuit objects --
    # Benchpress loads them in the test body via qasm_circuit_loader, which for the
    # qiskit gym is QuantumCircuit.from_qasm_file (qiskit_gym/utils/io.py).
    # Names come from file.split(".")[0], which is why test id "knn_341" lives in a
    # directory called "knn_n341".
    qasm_paths, names = get_qasmbench_circuits(qasm_dir)
    if args.only:
        keep = [(p, n) for p, n in zip(qasm_paths, names) if n == args.only]
        if not keep:
            sys.exit(f"ABORT: no circuit named '{args.only}' in {qasm_dir}")
        qasm_paths, names = [k[0] for k in keep], [k[1] for k in keep]
    seeds = [args.seed_start + i for i in range(args.seeds)]

    env = {
        "record": "env",
        "utc": datetime.now(timezone.utc).isoformat(),
        "qiskit_version": qiskit.__version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "benchpress_path": BENCHPRESS,
        "opt_level": opt_level,
        "basis_gates": Configuration.options["general"]["basis_gates"],
        "all_topologies": all_topologies,
        "topologies_run": topologies,
        "size": args.size,
        "n_circuits": len(qasm_paths),
        "seeds": seeds,
        "apparatus": "benchpress FlexibleBackend + count_ops[two_q_gate_type]",
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    total = len(qasm_paths) * len(topologies) * len(seeds)
    print(f"  {len(qasm_paths)} circuits x {len(topologies)} topologies x {len(seeds)} "
          f"seeds = {total} transpilations")
    print(f"  qiskit {qiskit.__version__} | opt_level={opt_level} | "
          f"topologies={topologies}\n")

    n_rows = 0
    with open(args.out, "w") as sink:
        sink.write(json.dumps(env) + "\n")

        for topo in topologies:
            for idx, (qasm_path, name) in enumerate(zip(qasm_paths, names), 1):
                test_id = f"{name}-{topo}"
                try:
                    circuit = QuantumCircuit.from_qasm_file(qasm_path)
                except Exception as exc:
                    sink.write(json.dumps({
                        "record": "load_error", "test_id": test_id, "circuit": name,
                        "topology": topo, "path": qasm_path,
                        "error": f"{type(exc).__name__}: {exc}",
                    }) + "\n")
                    print(f"  [{topo}] {name}: LOAD FAILED — {type(exc).__name__}",
                          flush=True)
                    continue

                n_qubits = circuit.num_qubits
                try:
                    backend = FlexibleBackend(n_qubits, topo, control_flow=True)
                    two_q_gate = backend.two_q_gate_type
                except Exception as exc:
                    sink.write(json.dumps({
                        "record": "backend_error", "test_id": test_id,
                        "circuit": name, "topology": topo, "n_qubits": n_qubits,
                        "error": f"{type(exc).__name__}: {exc}",
                    }) + "\n")
                    print(f"  [{topo}] {name}: BACKEND FAILED — {type(exc).__name__}")
                    continue

                spent, values = 0.0, []
                for seed in seeds:
                    if spent > args.max_seconds:
                        sink.write(json.dumps({
                            "record": "budget_stop", "test_id": test_id,
                            "circuit": name, "topology": topo, "seed": seed,
                            "seconds_spent": round(spent, 2),
                            "seeds_completed": len(values),
                        }) + "\n")
                        break

                    t0 = time.perf_counter()
                    try:
                        pm = generate_preset_pass_manager(
                            optimization_level=opt_level, backend=backend,
                            seed_transpiler=seed)
                        out = pm.run(circuit)
                        elapsed = time.perf_counter() - t0
                        spent += elapsed

                        # Benchpress's observable, verbatim.
                        two_q = out.count_ops().get(two_q_gate, 0)
                        depth_2q = out.depth(
                            filter_function=lambda x: x.operation.name == two_q_gate)

                        # Hashing is best-effort and MUST NOT gate the measurement.
                        qasm_hash, hash_error = None, None
                        try:
                            qasm_hash = hashlib.sha256(
                                qasm2.dumps(out).encode()).hexdigest()
                        except Exception as exc:
                            hash_error = f"{type(exc).__name__}: {exc}"

                        row = {
                            "record": "run", "test_id": test_id, "circuit": name,
                            "topology": topo, "n_qubits": n_qubits,
                            "backend_qubits": backend.num_qubits,
                            "seed": seed, "two_q_gate": two_q_gate,
                            "two_q": two_q, "depth_2q": depth_2q,
                            "depth": out.depth(), "size": out.size(),
                            "qasm_sha256": qasm_hash, "hash_error": hash_error,
                            "seconds": round(elapsed, 3),
                        }
                        values.append(two_q)
                    except Exception as exc:
                        elapsed = time.perf_counter() - t0
                        spent += elapsed
                        row = {
                            "record": "run_error", "test_id": test_id, "circuit": name,
                            "topology": topo, "n_qubits": n_qubits, "seed": seed,
                            "seconds": round(elapsed, 3),
                            "error": f"{type(exc).__name__}: {exc}",
                            "traceback": traceback.format_exc(limit=3),
                        }
                    sink.write(json.dumps(row) + "\n")
                    sink.flush()
                    n_rows += 1

                if values:
                    lo, hi = min(values), max(values)
                    spread = (hi - lo) / lo * 100 if lo else 0.0
                    flag = "  <-- SPREAD" if spread >= 5.0 else ""
                    print(f"  [{topo} {idx}/{len(qasm_paths)}] {name} (n={n_qubits}, "
                          f"{len(values)} seeds, {spent:.1f}s): {lo}-{hi} "
                          f"spread {spread:.1f}%{flag}", flush=True)
                else:
                    print(f"  [{topo} {idx}/{len(qasm_paths)}] {name}: no successful runs",
                          flush=True)

    print(f"\n  {n_rows} rows written to {args.out}")


if __name__ == "__main__":
    main()
