"""Priority 6 — pin Benchpress. Writes results/raw/benchpress_pin.json.

WHY
    D-5.2: every provenance record named Benchpress only by a scratchpad PATH. A path
    is not a version. Benchpress supplies the circuits, the backend, the topologies and
    the observable -- it is as much of the toolchain as Qiskit, and our own rule
    (flip_analysis.py) is that a measurement file which cannot name its own toolchain is
    not evidence.

    Worse, found while fixing it: the `qasm_sha256` field in every existing raw row
    hashes the TRANSPILED OUTPUT. Nothing in the corpus ever pinned the INPUT circuits.

WHAT THIS PINS
    - the checkout: commit SHA + whether the working tree is dirty
    - the five files we call into: sha256 each
    - every source QASM in the size under test: sha256 each

    Together these let a replicator prove their Benchpress is byte-identical to ours
    without trusting a path, a tag, or this file's own prose.

HONEST LIMIT, STATED HERE AND IN THE RECORD
    The censuses in results/raw/*.jsonl were collected BEFORE this pin existed, so they
    do not carry it. The clone has been clean at one commit throughout and was never
    pulled, but that is an assertion about our process, not a fact stamped into those
    files. New runs carry the pin in their `env` record (sweep_bp.py). Old ones are
    covered only by this file plus that assertion, and the record says so.

USAGE
    BENCHPRESS_PATH=<repo> python pin_benchpress.py --size large \
        --out results/raw/benchpress_pin.json
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

from sweep_bp import BENCHPRESS, PINNED_MODULES, benchpress_pin


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--size", default="large")
    p.add_argument("--out", default="results/raw/benchpress_pin.json")
    args = p.parse_args()

    from benchpress.config import Configuration
    from benchpress.utilities.io import get_qasmbench_circuits

    pin = benchpress_pin()
    if any(str(v).startswith("ERROR") for v in pin["benchpress_module_sha256"].values()):
        sys.exit(f"ABORT: a pinned module is missing:\n"
                 f"{json.dumps(pin['benchpress_module_sha256'], indent=2)}")

    qasm_dir = Configuration.get_qasm_dir(f"qasmbench-{args.size}")
    paths, names = get_qasmbench_circuits(qasm_dir)
    circuits = {}
    for path, name in sorted(zip(paths, names), key=lambda x: x[1]):
        with open(path, "rb") as fh:
            data = fh.read()
        circuits[name] = {"sha256": hashlib.sha256(data).hexdigest(),
                          "bytes": len(data),
                          "relpath": os.path.relpath(path, BENCHPRESS).replace("\\", "/")}

    doc = {
        "record": "benchpress_pin",
        "utc": datetime.now(timezone.utc).isoformat(),
        "size": args.size,
        "n_circuits": len(circuits),
        "pinned_modules": PINNED_MODULES,
        **pin,
        "corpus_sha256": hashlib.sha256(
            "".join(f"{n}:{c['sha256']}\n" for n, c in sorted(circuits.items()))
            .encode()).hexdigest(),
        "circuits": circuits,
        "applies_retroactively": False,
        "note": ("The censuses in results/raw/*.jsonl predate this pin and do not carry "
                 "it. The clone was clean at this commit throughout the study and was "
                 "never pulled, but for those files that is an assertion about process, "
                 "not a stamped fact. Runs made after 2026-09-03 carry the pin in their "
                 "env record."),
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=False)

    print(f"\n  benchpress commit : {doc['benchpress_commit']}")
    print(f"  working tree dirty: {doc['benchpress_dirty']}")
    print(f"  pinned modules    : {len(PINNED_MODULES)}")
    print(f"  circuits pinned   : {len(circuits)} ({args.size})")
    print(f"  corpus sha256     : {doc['corpus_sha256']}")
    print(f"\n  written: {args.out}")


if __name__ == "__main__":
    main()
