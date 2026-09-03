"""Experiment 2 — does our seeded path reproduce Benchpress's own unseeded observable?

THE CHECK
    Benchpress's actual call (qiskit_gym/abstract_transpile/test_qasmbench.py:49) is

        pm = generate_preset_pass_manager(optimization_level=OPTIMIZATION_LEVEL,
                                          backend=backend)

    with NO seed_transpiler. Our sweep adds one. That is the only intended difference.

    So equivalence is testable: run Benchpress's exact unseeded call many times, and run
    our seeded call across many seeds. If the two sets of values occupy the same range,
    the paths agree and the seed is doing what an unseeded run does anyway -- drawing
    from the same distribution. If the unseeded values fall OUTSIDE the seeded range,
    our path differs from theirs and every downstream number is suspect.

    This also measures something nobody has published: what an unseeded Benchpress run
    is actually sampling.

NEGATIVE CONTROL
    Pass --topology all-to-all. That layout needs no routing, so SABRE has nothing
    stochastic to do and BOTH arms should collapse to a single value. If they do not,
    the instrument is wrong and no other result here can be trusted.

USAGE
    BENCHPRESS_PATH=<repo> python exp2_equivalence.py --qasm <file> \
        --topology linear --n 20 --require-qiskit 2.0.2
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

BENCHPRESS = os.environ.get("BENCHPRESS_PATH")
if not BENCHPRESS or not os.path.isdir(BENCHPRESS):
    sys.exit("ERROR: set BENCHPRESS_PATH to the benchpress repo root")
sys.path.insert(0, BENCHPRESS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qasm", required=True)
    parser.add_argument("--topology", default="linear")
    parser.add_argument("--n", type=int, default=20)
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--require-qiskit", default=None)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    import qiskit
    if args.require_qiskit and qiskit.__version__ != args.require_qiskit:
        sys.exit(f"ABORT: require-qiskit={args.require_qiskit} but environment has "
                 f"qiskit {qiskit.__version__}.")

    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from benchpress.config import Configuration
    from benchpress.utilities.backends import FlexibleBackend

    opt_level = Configuration.options["qiskit"]["optimization_level"]
    circuit = QuantumCircuit.from_qasm_file(args.qasm)
    n = circuit.num_qubits
    backend = FlexibleBackend(n, args.topology, control_flow=True)
    gate = backend.two_q_gate_type

    def observable(compiled):
        return compiled.count_ops().get(gate, 0)

    # Arm 1 -- Benchpress's exact call, no seed.
    unseeded = []
    for _ in range(args.n):
        pm = generate_preset_pass_manager(optimization_level=opt_level, backend=backend)
        unseeded.append(observable(pm.run(circuit)))

    # Arm 2 -- our call, one seed per run.
    seeded = []
    for i in range(args.n):
        pm = generate_preset_pass_manager(optimization_level=opt_level, backend=backend,
                                          seed_transpiler=args.seed_start + i)
        seeded.append(observable(pm.run(circuit)))

    u_lo, u_hi = min(unseeded), max(unseeded)
    s_lo, s_hi = min(seeded), max(seeded)
    contained = u_lo >= s_lo and u_hi <= s_hi
    overlap = not (u_hi < s_lo or s_hi < u_lo)

    print(f"\n  circuit={os.path.basename(args.qasm)} n={n} topology={args.topology} "
          f"opt={opt_level} qiskit={qiskit.__version__} gate='{gate}'")
    print(f"  arm 1  Benchpress unseeded  : {u_lo}-{u_hi}  "
          f"distinct {len(set(unseeded))}/{args.n}")
    print(f"  arm 2  our seeded           : {s_lo}-{s_hi}  "
          f"distinct {len(set(seeded))}/{args.n}")

    if args.topology == "all-to-all":
        ok = len(set(unseeded)) == 1 and len(set(seeded)) == 1
        msg = ("PASS - both arms constant, as a routing-free layout requires" if ok
               else "FAIL - variance with no routing to do; instrument suspect")
        print(f"\n  NEGATIVE CONTROL: {msg}")
    else:
        verdict = ("paths agree - unseeded runs sample the seeded distribution" if overlap
                   else "PATHS DIFFER - investigate before trusting any sweep")
        print(f"\n  unseeded range inside seeded range: {contained}")
        print(f"  ranges overlap                     : {overlap}")
        print(f"  VERDICT: {verdict}")

    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as fh:
            json.dump({
                "experiment": "exp2_equivalence",
                "utc": datetime.now(timezone.utc).isoformat(),
                "circuit": os.path.basename(args.qasm), "n_qubits": n,
                "topology": args.topology, "opt_level": opt_level,
                "qiskit_version": qiskit.__version__, "two_q_gate": gate, "n_runs": args.n,
                "unseeded": unseeded, "seeded": seeded,
                "unseeded_range": [u_lo, u_hi], "seeded_range": [s_lo, s_hi],
                "contained": contained, "overlap": overlap,
            }, fh, indent=2)
        print(f"  written: {args.out}")


if __name__ == "__main__":
    main()
