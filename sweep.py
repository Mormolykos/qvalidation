"""Seed sweep over a QASM corpus — raw observations only, no conclusions.

WHY A CENSUS, NOT A SAMPLE
    The pilot (RESEARCH_LANDSCAPE.md sec 24) used the three circuits that issue #14402
    reported as WORST. That is a selection effect: circuits picked for having large
    reported regressions may also be the ones with unusual seed behaviour. Running the
    entire qasmbench-large set (58 circuits) removes the effect rather than reducing it,
    and 58 is small enough to make that affordable.

DESIGN RULES (RESEARCH_LANDSCAPE.md sec 10)
    - Every observation is written to JSONL. Raw rows are never overwritten or filtered.
    - Every row carries its seed, versions, config and a hash of the emitted circuit.
    - Failures are recorded as rows with an "error" field, never dropped silently.
    - No statistics are computed here. This file only measures.

USAGE
    python sweep.py --corpus <dir> --seeds 12 --out results/raw/sweep_2_0_2.jsonl
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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def two_qubit_count(circuit) -> int:
    """Count operations acting on exactly two qubits, excluding barriers/measures."""
    total = 0
    for instruction in circuit.data:
        name = instruction.operation.name
        if name in ("barrier", "measure", "delay", "reset"):
            continue
        if len(instruction.qubits) == 2:
            total += 1
    return total


def find_circuits(corpus_dir):
    """Yield (name, path) for each circuit, skipping pre-transpiled companions."""
    found = []
    for entry in sorted(os.listdir(corpus_dir)):
        sub = os.path.join(corpus_dir, entry)
        if not os.path.isdir(sub):
            continue
        for fname in sorted(os.listdir(sub)):
            if fname.endswith(".qasm") and "_transpiled" not in fname:
                found.append((fname[:-5], os.path.join(sub, fname)))
    return found


def load_circuit(path, qasm2, qasm3):
    try:
        return qasm2.load(path,
                          include_path=(os.path.dirname(path),),
                          custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
    except qasm2.QASM2ParseError:
        return qasm3.load(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--seeds", type=int, default=12,
                        help="Number of distinct transpiler seeds per circuit")
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--opt-level", type=int, default=2,
                        help="Benchpress default.conf [qiskit] optimization_level = 2")
    parser.add_argument("--max-seconds", type=float, default=90.0,
                        help="Skip remaining seeds for a circuit once its cumulative "
                             "time exceeds this. Recorded, not silent.")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    import qiskit
    from qiskit import qasm2, qasm3
    from qiskit.transpiler import CouplingMap
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    basis_gates = ["id", "sx", "x", "rz", "cz"]
    seeds = [args.seed_start + i for i in range(args.seeds)]

    env = {
        "qiskit_version": qiskit.__version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu_count": os.cpu_count(),
        "RAYON_NUM_THREADS": os.environ.get("RAYON_NUM_THREADS", "<unset>"),
        "opt_level": args.opt_level,
        "basis_gates": basis_gates,
        "topology": "linear (CouplingMap.from_line)",
        "utc": datetime.now(timezone.utc).isoformat(),
    }

    circuits = find_circuits(args.corpus)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)

    print(f"  {len(circuits)} circuits x {len(seeds)} seeds "
          f"= {len(circuits) * len(seeds)} transpilations")
    print(f"  qiskit {qiskit.__version__}, opt_level={args.opt_level}\n")

    n_rows = 0
    with open(args.out, "w") as sink:
        sink.write(json.dumps({"record": "env", **env}) + "\n")

        for idx, (name, path) in enumerate(circuits, 1):
            try:
                circuit = load_circuit(path, qasm2, qasm3)
            except Exception as exc:
                sink.write(json.dumps({
                    "record": "circuit_error", "circuit": name, "path": path,
                    "error": f"{type(exc).__name__}: {exc}",
                }) + "\n")
                print(f"  [{idx}/{len(circuits)}] {name}: LOAD FAILED — {type(exc).__name__}")
                continue

            n_qubits = circuit.num_qubits
            coupling = CouplingMap.from_line(n_qubits)
            spent = 0.0
            values = []

            for seed in seeds:
                if spent > args.max_seconds:
                    sink.write(json.dumps({
                        "record": "budget_stop", "circuit": name, "seed": seed,
                        "seconds_spent": round(spent, 2),
                        "seeds_completed": len(values),
                    }) + "\n")
                    break
                t0 = time.perf_counter()
                try:
                    pm = generate_preset_pass_manager(
                        optimization_level=args.opt_level,
                        basis_gates=basis_gates,
                        coupling_map=coupling,
                        seed_transpiler=seed,
                    )
                    out = pm.run(circuit)
                    elapsed = time.perf_counter() - t0
                    spent += elapsed
                    row = {
                        "record": "run", "circuit": name, "n_qubits": n_qubits,
                        "seed": seed,
                        "two_q": two_qubit_count(out),
                        "depth": out.depth(),
                        "size": out.size(),
                        "qasm_sha256": sha256_text(qasm2.dumps(out)),
                        "seconds": round(elapsed, 3),
                    }
                    values.append(row["two_q"])
                except Exception as exc:
                    elapsed = time.perf_counter() - t0
                    spent += elapsed
                    row = {
                        "record": "run_error", "circuit": name, "n_qubits": n_qubits,
                        "seed": seed, "seconds": round(elapsed, 3),
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
                print(f"  [{idx}/{len(circuits)}] {name} (n={n_qubits}, "
                      f"{len(values)} seeds, {spent:.1f}s): "
                      f"2Q {lo}-{hi}  spread {spread:.1f}%{flag}")
            else:
                print(f"  [{idx}/{len(circuits)}] {name} (n={n_qubits}): no successful runs")

    print(f"\n  {n_rows} rows written to {args.out}")


if __name__ == "__main__":
    main()
