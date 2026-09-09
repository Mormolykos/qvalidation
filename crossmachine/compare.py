"""Did a second physical machine produce the same gate counts? Answer with integers.

WHAT THIS IS FOR
    §3.4 claims the observable is a deterministic function of `seed_transpiler`. Until
    2026-09-08 the paper said that was verified "across processes and machines". It was
    not: every one of the 196 environment records carries the same platform string and
    the schema records no CPU vendor, so no cross-hardware claim was supportable
    (SETTLED.json S24). The claim was corrected down to one machine. This script is the
    attempt to earn the stronger version back with evidence.

    The design is fixed in `crossmachine/PREREGISTRATION.md`, committed before any second
    machine ran anything. Read it first; it says what a mismatch would mean, in advance.

WHAT IT COMPARES
    Per (circuit, seed) 2-qubit gate counts, as integers, between a reference run and a
    second-machine run of the SAME Qiskit version. Not "close" -- identical. A single
    differing integer is a finding, not a rounding artifact.

    It also prints the platform, CPU count and Python of both runs, because "two
    machines" has to be checkable rather than asserted. If both files report the same
    platform string, this script says so and the claim is NOT earned.

USAGE
    python crossmachine/compare.py \
        --reference replication/out_q200.jsonl \
        --candidate crossmachine/laptop_q200.jsonl
"""

import argparse
import json
import os
import sys


def load(path):
    """(values keyed by circuit+seed, environment metadata, qiskit version)."""
    vals, env, ver = {}, {}, None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if r.get("qiskit_version"):
                ver = r["qiskit_version"]
            if r.get("record") == "env":
                env = {k: r.get(k) for k in
                       ("platform", "processor", "machine", "cpu_count", "python",
                        "topology", "hashseed")}
            if r.get("record") == "run":
                vals[(r["circuit"], int(r["seed"]))] = int(r["two_q"])
    return vals, env, ver


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reference", required=True, help="the run recorded on machine 1")
    p.add_argument("--candidate", required=True, help="the run recorded on machine 2")
    args = p.parse_args()

    for f in (args.reference, args.candidate):
        if not os.path.isfile(f):
            sys.exit(f"ABORT: {f} does not exist")

    ref, ref_env, ref_ver = load(args.reference)
    cand, cand_env, cand_ver = load(args.candidate)

    print(f"\n  reference  {args.reference}")
    print(f"    qiskit {ref_ver} | {ref_env.get('platform')} | "
          f"cpu_count {ref_env.get('cpu_count')} | python {ref_env.get('python')}")
    print(f"  candidate  {args.candidate}")
    print(f"    qiskit {cand_ver} | {cand_env.get('platform')} | "
          f"cpu_count {cand_env.get('cpu_count')} | python {cand_env.get('python')}")

    if ref_ver != cand_ver:
        sys.exit(f"\n  ABORT: different Qiskit versions ({ref_ver} vs {cand_ver}). "
                 f"This compares one version across two machines, not two versions.")

    # "Two machines" is a claim, so it gets checked like one.
    #
    # UNKNOWN IS NOT DIFFERENT. replication/out_q*.jsonl record no platform at all, so a
    # naive inequality test reads None != "Windows-..." as two machines and prints
    # "recorded on two distinct configurations: None / None cpus". That is the same
    # defect class this whole audit has been chasing -- an absence scored as evidence.
    # Caught on this script's first run, 2026-09-08.
    # `processor` is part of this test, not decoration. Comparing only platform and
    # cpu_count was wrong: on 2026-09-09 both machines reported the byte-identical
    # platform string "Windows-10-10.0.26200-SP0", and the check resolved correctly only
    # because the core counts happened to differ (16 vs 8). Two boxes with the same OS
    # build and the same core count would have been flagged as possibly-one-machine even
    # with AuthenticAMD on one and GenuineIntel on the other. The vendor string was
    # already being recorded and simply was not consulted.
    unknown = [n for n, e in (("reference", ref_env), ("candidate", cand_env))
               if not e.get("platform")]
    same_box = (bool(ref_env.get("platform"))
                and ref_env.get("platform") == cand_env.get("platform")
                and ref_env.get("cpu_count") == cand_env.get("cpu_count")
                and ref_env.get("processor") == cand_env.get("processor"))
    if unknown:
        print(f"\n  ⚠ NO MACHINE RECORDED in the {' and '.join(unknown)} file.")
        print("    Values may still be compared, but this pair CANNOT support a")
        print("    cross-machine claim: an unrecorded machine is unknown, not different.")
        print("    Use crossmachine/measure.py, which records platform and CPU.")
    if same_box:
        print("\n  ⚠ BOTH RUNS REPORT THE SAME PLATFORM AND CPU COUNT.")
        print("    Matching values here do NOT support a cross-machine claim: this may")
        print("    be one machine twice. The schema records no CPU vendor or model, so")
        print("    it cannot distinguish two identical configurations. State the")
        print("    hardware separately, or record a vendor field, before claiming two.")

    missing_c = sorted(set(ref) - set(cand))
    missing_r = sorted(set(cand) - set(ref))
    shared = sorted(set(ref) & set(cand))
    diffs = [(c, s, ref[(c, s)], cand[(c, s)])
             for c, s in shared if ref[(c, s)] != cand[(c, s)]]

    print(f"\n  {len(shared)} (circuit, seed) pairs present in both")
    if missing_c:
        print(f"  {len(missing_c)} present in the reference but MISSING from the "
              f"candidate: {missing_c[:6]}")
    if missing_r:
        print(f"  {len(missing_r)} present in the candidate but not the reference: "
              f"{missing_r[:6]}")

    if diffs:
        print(f"\n  ✗ {len(diffs)} of {len(shared)} DIFFER — the observable is NOT "
              f"machine-independent for this version:\n")
        print(f"    {'circuit':<14s} {'seed':>6s} {'reference':>10s} {'candidate':>10s}")
        for c, s, a, b in diffs[:25]:
            print(f"    {c:<14s} {s:>6d} {a:>10d} {b:>10d}")
        if len(diffs) > 25:
            print(f"    ... and {len(diffs) - 25} more")
        print("\n  This is a FINDING, not a failure to be retried until it passes.")
        print("  PREREGISTRATION.md records in advance what it means. Report it.\n")
        sys.exit(1)

    if missing_c or missing_r:
        print("\n  INCOMPLETE: the two runs do not cover the same set. A partial run is "
              "reported as partial; nothing is claimed beyond the pairs compared.\n")
        sys.exit(2)

    print(f"\n  ✓ ALL {len(shared)} per-seed gate counts are IDENTICAL "
          f"for qiskit {ref_ver}.")
    if unknown:
        print("    Values match. NO cross-machine claim is earned here — see the "
              "warning above.")
    elif same_box:
        print("    Both runs report the same machine, so this shows repeatability, "
              "not machine-independence.")
    else:
        print("    Recorded on two distinct machines:")
        for e in (ref_env, cand_env):
            print(f"      {e.get('platform')} | {e.get('processor') or '?'} | "
                  f"{e.get('cpu_count')} cpus")
    print()


if __name__ == "__main__":
    main()
