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

WHAT IT REFUSES (S31, 2026-09-09)
    An external audit demonstrated four inputs this script certified and should not have.
    All four were the same disease: the checker repaired or ignored what it could not
    compare, instead of stopping. It now refuses, in this order, before any count is
    compared:

        malformed    two env records, a record that is not a JSON object, a repeated
                     (circuit, seed), a non-integer or negative count, a row with no
                     source-QASM hash or counted gate. `int(two_q)` used to be applied
                     on load, so a candidate value of 60.9 was truncated to 60 and
                     matched a reference 60. And a dict assignment let a later duplicate
                     row overwrite an earlier contradicting one, so the disagreement was
                     erased before the comparison it was supposed to fail.
        incomparable a missing or differing qiskit version, topology, optimisation
                     level, seed list, Benchpress commit, module hashes, source-QASM
                     hash or COUNTED GATE; a checkout not known to be clean; or an env
                     record whose declared seeds contradict its own rows. PRESENT, then
                     equal: a field deleted from BOTH files compares equal to itself,
                     and removing `qiskit_version` from both used to pass and report
                     success "for qiskit None".
        incomplete   anything other than the frozen selection imported below. Two files
                     containing no measurements at all used to print
                     "ALL 0 per-seed gate counts are IDENTICAL".

    It also prints which machine produced each file, because "two machines" has to be
    checkable rather than asserted, and `--require-distinct-machines` turns that from a
    printed sentence into an exit code.

EXIT CODES
    0  every count identical, and every refusal above passed
    1  at least one count differs -- a finding; see PREREGISTRATION.md
    2  incomplete: the frozen selection is not fully covered by both files
    3  refused: malformed or incomparable input, nothing was concluded
    4  --require-distinct-machines was given and two distinct machines were not proven

USAGE
    python crossmachine/compare.py \
        --reference crossmachine/desktop_q200.jsonl \
        --candidate crossmachine/laptop_q200.jsonl \
        --require-distinct-machines
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "replication"))

from replicate import CIRCUITS, SEEDS, TOPOLOGY  # noqa: E402  the frozen selection

# Imported, never restated. PREREGISTRATION.md claims this check introduces no selection
# freedom; that claim is only true if the expected set comes from the artifact itself.
EXPECTED_KEYS = frozenset((c, s) for c in CIRCUITS for s in SEEDS)

# Every field the machine-identity test consults. Both the "is anything missing" test and
# the "is it the same box" test are derived from THIS tuple and nothing else.
#
# This is the shape of the fix, not a detail of it. On 2026-09-09 `same_box` compared
# platform, cpu_count and processor while the missing-data test looked at platform alone,
# so deleting `processor` from a file made it unequal to itself -- and the script
# announced desktop_q143.jsonl versus a copy of itself as "two distinct machines". That
# was the second time an absence was scored as evidence here (S30 was the first, on this
# same pair of tests). Patching a field at a time is what produced two occurrences; one
# list consulted by both tests is what stops a third.
MACHINE = ("platform", "processor", "cpu_count")

# Must agree before equality of counts carries any meaning. `benchpress_path` is
# deliberately excluded: it is a local directory and differs between machines by design.
#
# `benchpress_dirty` is here, and separately required to be False on both sides, because
# a pinned commit does not describe the code that ran if the checkout was modified, and
# `benchpress_module_sha256` covers only the five pinned modules -- an edit anywhere else
# in Benchpress would pass every other check in this file.
PROVENANCE = ("qiskit_version", "topology", "optimization_level", "seeds",
              "benchpress_commit", "benchpress_module_sha256", "benchpress_dirty")

# Per-run fields that must also agree, checked per circuit rather than per file.
# `two_q_gate` is the one that matters: `two_q` is a count OF this gate, so two files
# that counted different gates are not comparable no matter how equal the integers are.
RUN_FIELDS = {"input_qasm_sha256": "source QASM", "two_q_gate": "counted gate"}


def _is_int(x):
    """JSON ints only. bool is an int in Python and is not a gate count."""
    return isinstance(x, int) and not isinstance(x, bool)


def identity(v):
    """`v` normalised to what it IDENTIFIES, or None if it identifies nothing.

    The third occurrence of this file's recurring defect was that MACHINE fields were
    compared for equality without being validated first, so a difference in
    REPRESENTATION was read as a difference in HARDWARE. Comparing one machine's record
    against a copy of itself returned DISTINCT when the copy carried cpu_count as "16"
    instead of 16, or a processor string that was lowercased, or padded with a trailing
    space, or replaced by `[]` -- because `[]` is neither None nor "" and so counted as
    a recorded value (Astra, second audit, 2026-09-09).

    Equality is now asked of this function's output, never of the raw field, and the
    same function decides whether a field is present at all. A value that identifies
    nothing is absent, and absent is UNKNOWN, never DISTINCT.
    """
    if isinstance(v, bool) or not isinstance(v, (str, int, float)):
        return None                       # a list or a dict names no machine
    s = " ".join(str(v).split())
    if not s:
        return None
    try:                                  # 16, 16.0, "16" and " 16.0 " are one count
        f = float(s)
    except ValueError:
        return s.casefold()
    return str(int(f)) if f.is_integer() else repr(f)


def load(path):
    """(counts and QASM hash keyed by circuit+seed, the one env record, refusals).

    Nothing is coerced and nothing is overwritten. Both used to happen on this line and
    both destroyed evidence: `int(r["two_q"])` silently truncated a non-integer into
    agreement, and `vals[key] = ...` let a later row overwrite an earlier one that
    disagreed with it.
    """
    vals, envs, bad = {}, [], []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError as exc:
                bad.append(f"line {n}: not JSON ({exc.msg})")
                continue
            if not isinstance(r, dict):
                # A bare `null` or `[]` line parses fine and then has no .get, so this
                # used to leave the process on an AttributeError traceback -- exit 1,
                # which this script's own contract reserves for "the counts differ".
                bad.append(f"line {n}: JSON {type(r).__name__}, not an object")
                continue
            if r.get("record") == "env":
                envs.append(r)
            elif r.get("record") == "run":
                circuit, seed, two_q = r.get("circuit"), r.get("seed"), r.get("two_q")
                if not _is_int(seed):
                    bad.append(f"line {n}: seed {seed!r} is not an integer")
                    continue
                if not _is_int(two_q):
                    bad.append(f"line {n}: {circuit} seed {seed}: two_q {two_q!r} is "
                               f"not an integer")
                    continue
                if two_q < 0:
                    # A count of gates has no negative values. Every row set to -1 was
                    # "72 identical counts" before this line existed.
                    bad.append(f"line {n}: {circuit} seed {seed}: two_q {two_q} is "
                               f"negative, and a gate count cannot be")
                    continue
                missing = [f for f in RUN_FIELDS if r.get(f) is None]
                if missing:
                    # Required, not merely compared: a field absent from BOTH files
                    # compares equal to itself and used to pass.
                    bad.append(f"line {n}: {circuit} seed {seed}: no "
                               f"{', '.join(RUN_FIELDS[f] for f in missing)}")
                    continue
                if (circuit, seed) in vals:
                    bad.append(f"line {n}: {circuit} seed {seed} measured twice "
                               f"({vals[(circuit, seed)]['two_q']} then {two_q})")
                    continue
                vals[(circuit, seed)] = {"two_q": two_q,
                                         **{f: r.get(f) for f in RUN_FIELDS}}
    if len(envs) != 1:
        bad.append(f"{len(envs)} env records; exactly one is required, because the "
                   f"environment a file reports must be unambiguous")
    return vals, (envs[0] if len(envs) == 1 else {}), bad


def per_circuit(vals, field):
    """{circuit: set of values of `field` seen}. More than one means the file mixes."""
    out = {}
    for (circuit, _), row in vals.items():
        out.setdefault(circuit, set()).add(row[field])
    return out


def machine_verdict(ref_env, cand_env):
    """('DISTINCT' | 'SAME' | 'UNKNOWN', explanation).

    UNKNOWN whenever any field in MACHINE is absent on either side. An unrecorded
    machine is unknown, not different: replication/out_q*.jsonl record no platform at
    all, and a naive inequality test reads None != "Windows-..." as two machines.
    """
    absent = {}
    for name, env in (("reference", ref_env), ("candidate", cand_env)):
        gone = [f for f in MACHINE if identity(env.get(f)) is None]
        if gone:
            absent[name] = gone
    if absent:
        return "UNKNOWN", "; ".join(f"the {n} file records no usable "
                                    f"{', '.join(f)}" for n, f in absent.items())
    if all(identity(ref_env.get(f)) == identity(cand_env.get(f)) for f in MACHINE):
        return "SAME", "both files identify the same " + ", ".join(MACHINE)
    return "DISTINCT", ""


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reference", required=True, help="the run recorded on machine 1")
    p.add_argument("--candidate", required=True, help="the run recorded on machine 2")
    p.add_argument("--require-distinct-machines", action="store_true",
                   help="exit 4 unless both files identify a machine and the two "
                        "machines differ. Use this whenever the output is going to "
                        "support a cross-machine sentence.")
    args = p.parse_args()

    for f in (args.reference, args.candidate):
        if not os.path.isfile(f):
            print(f"ABORT: {f} does not exist")
            sys.exit(3)

    ref, ref_env, ref_bad = load(args.reference)
    cand, cand_env, cand_bad = load(args.candidate)

    print(f"\n  reference  {args.reference}")
    print(f"    qiskit {ref_env.get('qiskit_version')} | {ref_env.get('platform')} | "
          f"{ref_env.get('processor') or 'processor not recorded'} | "
          f"cpu_count {ref_env.get('cpu_count')} | python {ref_env.get('python')}")
    print(f"  candidate  {args.candidate}")
    print(f"    qiskit {cand_env.get('qiskit_version')} | {cand_env.get('platform')} | "
          f"{cand_env.get('processor') or 'processor not recorded'} | "
          f"cpu_count {cand_env.get('cpu_count')} | python {cand_env.get('python')}")

    # ---- refusal 1: malformed ------------------------------------------------------
    malformed = ([f"{args.reference}: {m}" for m in ref_bad]
                 + [f"{args.candidate}: {m}" for m in cand_bad])
    if malformed:
        print("\n  ✗ REFUSED — the input is malformed. Nothing was compared:\n")
        for m in malformed[:20]:
            print(f"    {m}")
        if len(malformed) > 20:
            print(f"    ... and {len(malformed) - 20} more")
        print()
        sys.exit(3)

    # ---- refusal 2: incomparable ---------------------------------------------------
    ref_ver, cand_ver = ref_env.get("qiskit_version"), cand_env.get("qiskit_version")
    if ref_ver != cand_ver:
        print(f"\n  ✗ REFUSED: different Qiskit versions ({ref_ver} vs {cand_ver}). "
              f"This compares one version across two machines, not two versions.\n")
        sys.exit(3)

    # Present, THEN equal. A field missing from both files compares equal to itself:
    # deleting `qiskit_version` from both used to pass and report success "for qiskit
    # None" (Astra, second audit). Absence is not agreement, on either side or both.
    absent = [f"{n}: no {f}" for n, e in ((args.reference, ref_env),
                                          (args.candidate, cand_env))
              for f in PROVENANCE if e.get(f) is None]
    differing = [f for f in PROVENANCE if ref_env.get(f) != cand_env.get(f)]
    # `is not False`, not falsy: a missing or null value is not a clean checkout.
    dirty = [n for n, e in ((args.reference, ref_env), (args.candidate, cand_env))
             if e.get("benchpress_dirty") is not False]
    # The env record declares which seeds were measured, and every row must be covered
    # by that declaration: setting both files' seed lists to [999] while the rows stayed
    # at 1000-1011 used to pass, because the two declarations were equal to each other
    # and neither was ever checked against the data.
    #
    # Containment, not equality. A row the env never declared is a file contradicting
    # itself and is refused here; a declared seed with no row is an unfinished run and
    # belongs to the INCOMPLETE verdict below, which says so far more usefully.
    inconsistent = []
    for n, e, v in ((args.reference, ref_env, ref), (args.candidate, cand_env, cand)):
        undeclared = sorted({s for _, s in v} - set(e.get("seeds") or ()))
        if undeclared:
            inconsistent.append(f"{n}: rows carry seeds {undeclared} that the env "
                                f"record does not declare ({e.get('seeds')})")
    mixed, run_diff = [], []
    for field, label in RUN_FIELDS.items():
        ref_f, cand_f = per_circuit(ref, field), per_circuit(cand, field)
        mixed += [f"{c}: one file reports more than one {label} ({sorted(s)})"
                  for f in (ref_f, cand_f) for c, s in f.items() if len(s) > 1]
        run_diff += [f"{c}: {label} differs between the two files "
                     f"({sorted(ref_f[c])} vs {sorted(cand_f[c])})"
                     for c in sorted(set(ref_f) & set(cand_f))
                     if ref_f[c] != cand_f[c]]
    if absent or differing or dirty or mixed or run_diff or inconsistent:
        print("\n  ✗ REFUSED — the two runs are not comparable, so equality of their "
              "counts would mean nothing:\n")
        for a in absent:
            print(f"    {a}")
        for f in differing:
            print(f"    '{f}' differs: {ref_env.get(f)!r} vs {cand_env.get(f)!r}")
        for n in dirty:
            print(f"    {n}: benchpress_dirty is not false, so the pinned commit does "
                  f"not describe the code that ran")
        for m in mixed + run_diff + inconsistent:
            print(f"    {m}")
        print()
        sys.exit(3)

    if ref_env.get("topology") != TOPOLOGY:
        print(f"\n  ✗ REFUSED: both files declare topology "
              f"{ref_env.get('topology')!r}, not the frozen {TOPOLOGY!r}.\n")
        sys.exit(3)

    # ---- the comparison ------------------------------------------------------------
    shared = sorted(set(ref) & set(cand))
    diffs = [(c, s, ref[(c, s)]["two_q"], cand[(c, s)]["two_q"])
             for c, s in shared if ref[(c, s)]["two_q"] != cand[(c, s)]["two_q"]]

    print(f"\n  {len(shared)} (circuit, seed) pairs present in both, of "
          f"{len(EXPECTED_KEYS)} in the frozen selection")

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

    # ---- refusal 3: incomplete -----------------------------------------------------
    #
    # Checked AFTER the diff, so a partial run that already disagrees is reported as a
    # disagreement rather than dismissed as partial. Checked against the frozen set
    # rather than against the other file: two files can agree perfectly on the empty
    # set, and this script used to call that "ALL 0 per-seed gate counts are IDENTICAL".
    gaps = []
    for name, vals in ((args.reference, ref), (args.candidate, cand)):
        missing = sorted(EXPECTED_KEYS - set(vals))
        extra = sorted(set(vals) - EXPECTED_KEYS)
        if missing:
            gaps.append(f"{name}: {len(missing)} of {len(EXPECTED_KEYS)} frozen "
                        f"(circuit, seed) pairs missing, e.g. {missing[:4]}")
        if extra:
            gaps.append(f"{name}: {len(extra)} pairs outside the frozen selection, "
                        f"e.g. {extra[:4]}")
    if gaps:
        print("\n  ✗ INCOMPLETE — the frozen selection is not covered. Nothing is "
              "claimed:\n")
        for g in gaps:
            print(f"    {g}")
        print("\n    PREREGISTRATION.md: an uncompleted run earns no claim.\n")
        sys.exit(2)

    # ---- the verdict ---------------------------------------------------------------
    verdict, why = machine_verdict(ref_env, cand_env)
    print(f"\n  ✓ ALL {len(shared)} per-seed gate counts are IDENTICAL "
          f"for qiskit {ref_ver}.")
    print(f"  MACHINE VERDICT: {verdict}")
    if verdict == "UNKNOWN":
        print(f"    {why}.")
        print("    Values match, but this pair CANNOT support a cross-machine claim:")
        print("    an unrecorded machine is unknown, not different. Use")
        print("    crossmachine/measure.py, which records platform, CPU and vendor.")
    elif verdict == "SAME":
        print(f"    {why}.")
        print("    This shows repeatability on one machine, not machine-independence.")
    else:
        print("    Recorded on two distinct machines:")
        for e in (ref_env, cand_env):
            print(f"      {e.get('platform')} | {e.get('processor')} | "
                  f"{e.get('cpu_count')} cpus | rustworkx "
                  f"{e.get('rustworkx') or 'not recorded'}")
    print()

    if args.require_distinct_machines and verdict != "DISTINCT":
        print(f"  ✗ --require-distinct-machines was given and the verdict is "
              f"{verdict}.\n")
        sys.exit(4)


if __name__ == "__main__":
    main()
