"""Experiment 1 — is the BACKEND a second, uncontrolled randomness source in Benchpress?

THE OBSERVATION THAT PROMPTED THIS
    benchpress/utilities/backends/flexible_backend.py:111 calls
        super().__init__(num_qubits, basis_gates=..., coupling_map=cmap,
                         control_flow=control_flow)
    on GenericBackendV2, whose signature is
        (num_qubits, basis_gates=None, coupling_map=None, control_flow=False,
         dtm=None, dt=None, seed=None, noise_info=True)
    No `seed` is passed, and `noise_info` defaults True -- so the Target's error rates
    and gate durations are drawn from an unseeded RNG at construction time.

    Qiskit's preset pass managers at optimization_level >= 1 use Target error rates for
    layout scoring (VF2Layout / VF2PostLayout). So a freshly constructed backend could
    change the chosen layout, and hence the two-qubit gate count, even with the
    transpiler seed held fixed.

    THIS IS A HYPOTHESIS. This script tests it and is written to be able to REFUTE it.

WHAT IT MEASURES
    A: same backend object, fixed seed, repeated       -> isolates nothing (control)
    B: NEW backend each time, fixed transpiler seed    -> isolates backend randomness
    C: same backend object, varying transpiler seed    -> isolates transpiler seed

    If B shows spread while A does not, the backend is a second randomness source.
    If B is flat, the hypothesis is refuted and Benchpress is safe on this axis.

USAGE
    python exp1_backend_randomness.py --qasm <file> --topology linear --repeats 10
"""

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

BENCHPRESS = os.environ.get("BENCHPRESS_PATH")
if not BENCHPRESS or not os.path.isdir(BENCHPRESS):
    sys.exit("ERROR: set BENCHPRESS_PATH to the benchpress repo root")
sys.path.insert(0, BENCHPRESS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qasm", required=True)
    parser.add_argument("--topology", default="linear")
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--opt-level", type=int, default=2)
    parser.add_argument("--require-qiskit", default=None,
                        help="Refuse to run unless qiskit.__version__ matches exactly. "
                             "Added 2026-09-02 after `uv pip install qiskit-ibm-runtime` "
                             "silently upgraded 2.0.2 -> 2.5.2 mid-session and an "
                             "experiment ran against a version it did not report.")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    import qiskit
    if args.require_qiskit and qiskit.__version__ != args.require_qiskit:
        sys.exit(f"ABORT: require-qiskit={args.require_qiskit} but this environment "
                 f"has qiskit {qiskit.__version__}. Refusing to produce a "
                 f"mislabelled measurement.")
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from benchpress.utilities.backends import FlexibleBackend

    circuit = QuantumCircuit.from_qasm_file(args.qasm)
    n = circuit.num_qubits

    def count_2q(compiled, gate_name):
        """Benchpress's own observable: qiskit_gym/utils/io.py."""
        return compiled.count_ops().get(gate_name, 0)

    def run(backend, seed):
        pm = generate_preset_pass_manager(optimization_level=args.opt_level,
                                          backend=backend, seed_transpiler=seed)
        out = pm.run(circuit)
        return count_2q(out, backend.two_q_gate_type), out.depth()

    # --- A: one backend, fixed seed, repeated -----------------------------------
    backend_fixed = FlexibleBackend(n, args.topology, control_flow=True)
    a_vals = [run(backend_fixed, args.seed)[0] for _ in range(args.repeats)]

    # --- B: NEW backend each time, fixed transpiler seed ------------------------
    b_vals = []
    for _ in range(args.repeats):
        fresh = FlexibleBackend(n, args.topology, control_flow=True)
        b_vals.append(run(fresh, args.seed)[0])

    # --- C: one backend, varying transpiler seed --------------------------------
    c_vals = [run(backend_fixed, args.seed + i)[0] for i in range(args.repeats)]

    def summarize(label, vals):
        lo, hi = min(vals), max(vals)
        spread = (hi - lo) / lo * 100 if lo else 0.0
        print(f"  {label:<46s} {lo:>8d}-{hi:<8d} spread {spread:>7.2f}%  "
              f"distinct {len(set(vals))}")
        return {"values": vals, "min": lo, "max": hi,
                "spread_pct": round(spread, 3), "distinct": len(set(vals))}

    print(f"\n  circuit={os.path.basename(args.qasm)} n={n} "
          f"topology={args.topology} opt={args.opt_level} qiskit={qiskit.__version__}")
    print(f"  2Q gate counted: '{backend_fixed.two_q_gate_type}' "
          f"(Benchpress semantics: count_ops().get(gate, 0))\n")

    res = {
        "A_same_backend_fixed_seed": summarize("A: same backend, FIXED seed (control)", a_vals),
        "B_new_backend_fixed_seed": summarize("B: NEW backend each run, FIXED seed", b_vals),
        "C_same_backend_varying_seed": summarize("C: same backend, VARYING seed", c_vals),
    }

    verdict = ("BACKEND IS A SECOND RANDOMNESS SOURCE"
               if res["B_new_backend_fixed_seed"]["distinct"] > 1
               else "REFUTED — backend construction does not change the result")
    print(f"\n  VERDICT: {verdict}")
    if res["A_same_backend_fixed_seed"]["distinct"] > 1:
        print("  WARNING: control A also varied — something else is non-deterministic; "
              "B cannot be attributed to the backend.")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as fh:
            json.dump({
                "experiment": "exp1_backend_randomness",
                "utc": datetime.now(timezone.utc).isoformat(),
                "circuit": os.path.basename(args.qasm), "n_qubits": n,
                "topology": args.topology, "opt_level": args.opt_level,
                "transpiler_seed": args.seed, "repeats": args.repeats,
                "qiskit_version": qiskit.__version__,
                "two_q_gate": backend_fixed.two_q_gate_type,
                "verdict": verdict, **res,
            }, fh, indent=2)
        print(f"  written: {args.out}")


if __name__ == "__main__":
    main()
