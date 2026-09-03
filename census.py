"""Census driver — one OS process per circuit, so a hard crash costs one circuit.

WHY THIS EXISTS
    The in-process census died at circuit 9 of 58 with

        memory allocation of 280302560 bytes failed

    That is a Rust allocation failure inside Qiskit's transpiler on `bwt_n37` (37
    qubits, and also the slowest circuit in an earlier sweep at 276 s). It aborts the
    process. Python's try/except cannot catch it, so no error row was written and the
    remaining 49 circuits were never attempted.

    A measurement harness that loses 49 circuits because the 9th one crashed is not
    fit for purpose, and -- worse -- it loses them SILENTLY unless someone reads the
    log. So each (circuit, topology) now runs in its own subprocess:

      - a crash, an OOM, or a timeout is recorded as a row and the census continues
      - the failure mode is visible in the data, not only in a log tail
      - memory is returned to the OS between circuits rather than fragmenting

    This also matches the process discipline the entropy experiments established.

USAGE
    BENCHPRESS_PATH=<repo> python census.py --python envs/bp202/Scripts/python.exe \
        --size large --topology linear --seeds 12 --require-qiskit 2.0.2 \
        --out results/raw/bp_large_linear_q202.jsonl
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

BENCHPRESS = os.environ.get("BENCHPRESS_PATH")
if not BENCHPRESS or not os.path.isdir(BENCHPRESS):
    sys.exit("ERROR: set BENCHPRESS_PATH to the benchpress repo root")
sys.path.insert(0, BENCHPRESS)

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", required=True, help="Interpreter for the child runs")
    parser.add_argument("--size", default="large")
    parser.add_argument("--topology", default="linear")
    parser.add_argument("--seeds", type=int, default=12)
    parser.add_argument("--seed-start", type=int, default=1000)
    parser.add_argument("--max-seconds", type=float, default=120.0,
                        help="Per-circuit budget INSIDE the child")
    parser.add_argument("--timeout", type=float, default=400.0,
                        help="Hard wall-clock kill for the child process")
    parser.add_argument("--require-qiskit", default=None)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    from benchpress.config import Configuration
    from benchpress.utilities.io import get_qasmbench_circuits

    qasm_dir = Configuration.get_qasm_dir(f"qasmbench-{args.size}")
    _, names = get_qasmbench_circuits(qasm_dir)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    tmp_dir = os.path.join(os.path.dirname(args.out), "_parts")
    os.makedirs(tmp_dir, exist_ok=True)

    print(f"  {len(names)} circuits, topology={args.topology}, "
          f"{args.seeds} seeds, one process each\n", flush=True)

    n_ok = n_crash = 0
    env_written = False
    with open(args.out, "w") as sink:
        sink.write(json.dumps({
            "record": "census_env",
            "utc": datetime.now(timezone.utc).isoformat(),
            "driver": "census.py (one process per circuit)",
            "size": args.size, "topology": args.topology,
            "seeds": args.seeds, "seed_start": args.seed_start,
            "child_budget_s": args.max_seconds, "child_timeout_s": args.timeout,
            "require_qiskit": args.require_qiskit,
        }) + "\n")

        for idx, name in enumerate(names, 1):
            part = os.path.join(tmp_dir, f"{args.topology}__{name}.jsonl")
            cmd = [args.python, os.path.join(HERE, "sweep_bp.py"),
                   "--size", args.size, "--topologies", args.topology,
                   "--seeds", str(args.seeds), "--seed-start", str(args.seed_start),
                   "--max-seconds", str(args.max_seconds),
                   "--only", name, "--out", part]
            if args.require_qiskit:
                cmd += ["--require-qiskit", args.require_qiskit]

            t0 = time.perf_counter()
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True,
                                      timeout=args.timeout)
                rc, err, timed_out = proc.returncode, proc.stderr, False
            except subprocess.TimeoutExpired as exc:
                rc, err, timed_out = -9, (exc.stderr or b"").decode(errors="replace") \
                    if isinstance(exc.stderr, bytes) else (exc.stderr or ""), True
            elapsed = time.perf_counter() - t0

            # Keep the FIRST child's env record. Dropping every one of them lost the
            # qiskit version from the merged file entirely (found 2026-09-02): run rows
            # carry the seed but not the version, so the merged census could not say
            # which Qiskit produced it. A measurement file that cannot name its own
            # toolchain is not evidence.
            rows, child_env = [], None
            if os.path.isfile(part):
                with open(part) as fh:
                    for line in fh:
                        if json.loads(line).get("record") == "env":
                            child_env = child_env or line
                        else:
                            rows.append(line)
            if child_env and not env_written:
                sink.write(child_env)
                env_written = True

            if rc != 0 or timed_out:
                n_crash += 1
                sink.write(json.dumps({
                    "record": "process_crash", "circuit": name,
                    "topology": args.topology, "returncode": rc,
                    "timed_out": timed_out, "seconds": round(elapsed, 2),
                    "rows_salvaged": len(rows),
                    "stderr_tail": (err or "").strip()[-400:],
                }) + "\n")
                status = "TIMEOUT" if timed_out else f"CRASH rc={rc}"
                print(f"  [{idx}/{len(names)}] {name}: {status} after {elapsed:.1f}s "
                      f"({len(rows)} rows salvaged)", flush=True)
            else:
                n_ok += 1
                print(f"  [{idx}/{len(names)}] {name}: ok ({len(rows)} rows, "
                      f"{elapsed:.1f}s)", flush=True)

            for line in rows:          # partial results are kept either way
                sink.write(line)
            sink.flush()

    print(f"\n  {n_ok} ok, {n_crash} crashed/timed out -> {args.out}")


if __name__ == "__main__":
    main()
