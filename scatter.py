"""The last open attack — scattered seeds, fresh processes. §50, ChatGPT point 4.

THE THREAT BEING TESTED, IN THE CRITIC'S OWN WORDS
    "Your 200-seed sample may not represent the actual unseeded randomness distribution
     if Qiskit's RNG/environment differs across executions. Fix: independently reproduce
     the experiment across fresh processes/environments and RNG sources."

    It is a fair threat, because the headline sample is doubly narrow:
      - all 200 seeds for an arm came from ONE process, so any per-process state
        (hash randomisation, allocator layout, a cached RNG) is held constant;
      - the seeds are a CONTIGUOUS block, 1000-1199, so any structure in the seed
        sequence is not sampled against.

    §46 attack 8 tested contiguous vs scattered, but only at n=12 and only within one
    process. §44 showed the seed->value map is process-independent, but only for 12
    seeds. Neither covers the headline.

WHAT THIS RUNS
    200 seeds drawn from a WIDE range (7 .. 2**31), by a generator independent of
    anything in the study, split into CHUNKS that each run in their OWN OS process.
    If the contiguous single-process sample were unrepresentative, the false-positive
    rate would move.

    The comparison is against the committed deep_* files for the same circuit and
    topology, which are contiguous and single-process. Nothing is re-derived; the two
    samples are compared directly.

USAGE
    BENCHPRESS_PATH=<repo> python scatter.py --circuit bv_n140 --topology heavy-hex \
        --n 200 --chunks 10 --version 143 --python envs/bp143/Scripts/python.exe \
        --require-qiskit 1.4.3 --out results/raw/scatter_bv_n140_heavy-hex_q143.jsonl
"""

import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

WORKER = r'''
import json, os, sys
BP = os.environ["BENCHPRESS_PATH"]; sys.path.insert(0, BP)
import qiskit
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from benchpress.config import Configuration
from benchpress.utilities.backends import FlexibleBackend

req, circuit_name, topo, out, seeds = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], [int(x) for x in sys.argv[5].split(",")]
if req and qiskit.__version__ != req:
    sys.exit(f"ABORT: qiskit {qiskit.__version__} != required {req}")
qd = Configuration.get_qasm_dir("qasmbench-large")
opt = Configuration.options["qiskit"]["optimization_level"]
c = QuantumCircuit.from_qasm_file(os.path.join(qd, circuit_name, circuit_name + ".qasm"))
b = FlexibleBackend(c.num_qubits, topo, control_flow=True)
with open(out, "w") as fh:
    fh.write(json.dumps({"record": "env", "qiskit_version": qiskit.__version__,
                         "pid": os.getpid(), "topology": topo,
                         "hashseed": os.environ.get("PYTHONHASHSEED")}) + "\n")
    for s in seeds:
        pm = generate_preset_pass_manager(optimization_level=opt, backend=b,
                                          seed_transpiler=s)
        fh.write(json.dumps({"record": "run", "circuit": circuit_name, "topology": topo,
                             "seed": s, "two_q_gate": b.two_q_gate_type,
                             "two_q": int(pm.run(c).count_ops().get(b.two_q_gate_type, 0)),
                             "pid": os.getpid()}) + "\n")
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--circuit", required=True)
    ap.add_argument("--topology", required=True)
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--chunks", type=int, default=10)
    ap.add_argument("--version", required=True)
    ap.add_argument("--python", required=True)
    ap.add_argument("--require-qiskit", default=None)
    ap.add_argument("--seed", type=int, default=13371337,
                    help="seed for CHOOSING the scattered seeds, not for transpiling")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    seeds = sorted(set(int(x) for x in rng.integers(7, 2 ** 31 - 1, args.n * 2)))[:args.n]
    if len(seeds) < args.n:
        sys.exit("ABORT: could not draw enough distinct seeds")

    worker_path = os.path.join(HERE, "_scatter_worker.py")
    with open(worker_path, "w") as fh:
        fh.write(WORKER)

    parts, chunks = [], np.array_split(np.array(seeds), args.chunks)
    tmp = os.path.join(os.path.dirname(args.out), "_scatter_parts")
    os.makedirs(tmp, exist_ok=True)
    print(f"\n  {args.circuit} / {args.topology} / qiskit {args.version}: "
          f"{len(seeds)} scattered seeds in {args.chunks} separate processes")
    print(f"  seed range {min(seeds):,} .. {max(seeds):,}\n")

    for i, ch in enumerate(chunks):
        part = os.path.join(tmp, f"{args.circuit}_{args.topology}_{args.version}_{i}.jsonl")
        env = dict(os.environ)
        env["PYTHONHASHSEED"] = str(1000 + i)      # a different hash seed per process
        cmd = [args.python, worker_path, args.require_qiskit or "", args.circuit,
               args.topology, part, ",".join(str(int(s)) for s in ch)]
        p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=3600)
        if p.returncode != 0:
            sys.exit(f"ABORT: chunk {i} failed:\n{p.stderr[-800:]}")
        parts.append(part)
        print(f"    chunk {i+1}/{args.chunks}: {len(ch)} seeds ok")

    pids, n = set(), 0
    with open(args.out, "w") as sink:
        for part in parts:
            for line in open(part):
                row = json.loads(line)
                if row.get("pid"):
                    pids.add(row["pid"])
                if row.get("record") == "run":
                    n += 1
                sink.write(line)
    os.remove(worker_path)
    print(f"\n  {n} runs across {len(pids)} distinct OS processes -> {args.out}")


if __name__ == "__main__":
    main()
