"""The cross-machine comparator must refuse the four inputs it used to certify.

WHY THIS FILE EXISTS
    An external code audit (Astra, 2026-09-09) demonstrated four inputs that
    `crossmachine/compare.py` accepted and reported as a successful cross-machine
    replication. All four were reproduced here before anything was changed, and the
    committed cross-machine data was separately checked against each failure mode and
    found clean -- the 216 identical counts stand and no published number moved
    (SETTLED.json S31). What was broken was the checker's ability to fail.

    These tests pin the four refusals so a checker that cannot fail cannot come back.
    They drive the real script as a subprocess and assert its EXIT CODE, because a
    verification tool that prints a warning and exits 0 is one an automated caller
    cannot distinguish from a pass -- which is how the first defect survived.

    Exit codes: 0 pass, 1 counts differ, 2 incomplete, 3 refused, 4 machines not distinct.
"""

import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

COMPARE = os.path.join(ROOT, "crossmachine", "compare.py")
DESKTOP = os.path.join(ROOT, "crossmachine", "desktop_q143.jsonl")
LAPTOP = os.path.join(ROOT, "crossmachine", "laptop_q143.jsonl")

sys.path.insert(0, os.path.join(ROOT, "crossmachine"))
import compare as C  # noqa: E402


def rows(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def write(tmp, name, rs):
    p = os.path.join(str(tmp), name)
    with open(p, "w", encoding="utf-8") as fh:
        for r in rs:
            fh.write(json.dumps(r) + "\n")
    return p


def run(ref, cand, *extra):
    r = subprocess.run([sys.executable, COMPARE, "--reference", ref,
                        "--candidate", cand, *extra],
                       capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout + r.stderr


def first_run_index(rs):
    return next(i for i, r in enumerate(rs) if r.get("record") == "run")


# --- the result this file exists to protect -------------------------------------------

def test_committed_pair_still_passes():
    """The real evidence must survive the repair. If this fails, the fix broke §3.4."""
    code, out = run(DESKTOP, LAPTOP, "--require-distinct-machines")
    assert code == 0, out
    assert "ALL 72 per-seed gate counts are IDENTICAL" in out
    assert "MACHINE VERDICT: DISTINCT" in out


# --- attack 1: an absence must never be read as a different machine --------------------

@pytest.mark.parametrize("field", C.MACHINE)
def test_A_missing_machine_field_is_unknown_not_distinct(tmp_path, field):
    """A file compared against a COPY OF ITSELF with one identifying field deleted was
    announced as 'Recorded on two distinct machines'. Every field the same-box test
    consults must also count as missing when it is absent."""
    rs = rows(DESKTOP)
    rs[0] = {k: v for k, v in rs[0].items() if k != field}
    twin = write(tmp_path, f"no_{field}.jsonl", rs)

    code, out = run(DESKTOP, twin)
    assert "MACHINE VERDICT: UNKNOWN" in out, out
    assert "distinct machines" not in out
    assert code == 0                      # values still compared and reported

    code, out = run(DESKTOP, twin, "--require-distinct-machines")
    assert code == 4, out                 # but no cross-machine claim is earned


def test_A_empty_string_processor_is_absent_not_a_value(tmp_path):
    """platform.processor() returns '' on some platforms. An empty string identifies
    no machine, so it must be treated as missing rather than as a comparable value."""
    rs = rows(DESKTOP)
    rs[0] = dict(rs[0], processor="")
    twin = write(tmp_path, "blank_proc.jsonl", rs)
    code, out = run(DESKTOP, twin, "--require-distinct-machines")
    assert "MACHINE VERDICT: UNKNOWN" in out, out
    assert code == 4


def test_A_identical_machine_is_same_not_distinct(tmp_path):
    """A file against a byte-identical copy is one machine twice."""
    twin = write(tmp_path, "twin.jsonl", rows(DESKTOP))
    code, out = run(DESKTOP, twin, "--require-distinct-machines")
    assert "MACHINE VERDICT: SAME" in out, out
    assert "repeatability" in out
    assert code == 4


# --- attack 2: contradictory measurements must not be erased --------------------------

def test_B_duplicate_contradicting_row_is_refused(tmp_path):
    """Dict assignment let a later matching row overwrite an earlier disagreeing one:
    61 then 60 against a reference 60 reported 'ALL 72 IDENTICAL'."""
    rs = rows(LAPTOP)
    i = first_run_index(rs)
    rs.insert(i, dict(rs[i], two_q=rs[i]["two_q"] + 1))
    p = write(tmp_path, "dup.jsonl", rs)
    code, out = run(DESKTOP, p)
    assert code == 3, out
    assert "measured twice" in out
    assert "IDENTICAL" not in out


def test_B_duplicate_agreeing_row_is_also_refused(tmp_path):
    """Even a duplicate that agrees is refused: whether the copies agree is not the
    point, an ambiguous record is."""
    rs = rows(LAPTOP)
    i = first_run_index(rs)
    rs.insert(i, dict(rs[i]))
    p = write(tmp_path, "dup_same.jsonl", rs)
    assert run(DESKTOP, p)[0] == 3


def test_B_non_integer_count_is_refused_not_truncated(tmp_path):
    """int() turned a candidate 60.9 into 60 and matched a reference 60."""
    rs = rows(LAPTOP)
    i = first_run_index(rs)
    rs[i] = dict(rs[i], two_q=rs[i]["two_q"] + 0.9)
    p = write(tmp_path, "float.jsonl", rs)
    code, out = run(DESKTOP, p)
    assert code == 3, out
    assert "is not an integer" in out


# --- attack 3: incomparable provenance must be refused --------------------------------

@pytest.mark.parametrize("field,value", [("topology", "linear"),
                                         ("optimization_level", 0),
                                         ("seeds", list(range(2000, 2012))),
                                         ("benchpress_commit", "0" * 40)])
def test_C_provenance_mismatch_is_refused(tmp_path, field, value):
    """Equality of counts between two different experiments means nothing. The script
    accepted a candidate declaring topology='linear' and optimization_level=0."""
    rs = rows(LAPTOP)
    rs[0] = dict(rs[0], **{field: value})
    p = write(tmp_path, f"prov_{field}.jsonl", rs)
    code, out = run(DESKTOP, p)
    assert code == 3, out
    assert "not comparable" in out and field in out


def test_C_second_env_record_is_refused(tmp_path):
    """Version used to be 'last row wins', so a file could carry a contradicting env
    record and still be read as the version of whichever row came last."""
    rs = rows(LAPTOP)
    rs.insert(1, dict(rs[0], qiskit_version="2.0.0"))
    rs.append(dict(rs[0]))
    p = write(tmp_path, "two_env.jsonl", rs)
    code, out = run(DESKTOP, p)
    assert code == 3, out
    assert "env records" in out


def test_C_changed_source_qasm_is_refused(tmp_path):
    """The counts are only comparable if both machines compiled the same circuit."""
    rs = rows(LAPTOP)
    i = first_run_index(rs)
    rs[i] = dict(rs[i], input_qasm_sha256="0" * 64)
    p = write(tmp_path, "qasm.jsonl", rs)
    code, out = run(DESKTOP, p)
    assert code == 3, out
    assert "source QASM" in out


def test_C_different_counted_gate_is_refused(tmp_path):
    """`two_q` is a count OF `two_q_gate`. Two files that counted different gates are
    not comparable however equal the integers are. Found while attacking the S31 fix."""
    rs = [dict(r, two_q_gate="ecr") if r.get("record") == "run" else r
          for r in rows(LAPTOP)]
    p = write(tmp_path, "gate.jsonl", rs)
    code, out = run(DESKTOP, p)
    assert code == 3, out
    assert "counted gate differs" in out


def test_C_dirty_benchpress_checkout_is_refused(tmp_path):
    """A pinned commit does not describe the code that ran if the checkout was edited,
    and the module hashes cover only five files. Found while attacking the S31 fix."""
    rs = rows(LAPTOP)
    rs[0] = dict(rs[0], benchpress_dirty=True)
    p = write(tmp_path, "dirty.jsonl", rs)
    code, out = run(DESKTOP, p)
    assert code == 3, out
    assert "benchpress_dirty" in out


def test_C_different_qiskit_versions_still_refused():
    """The one provenance check the old script did have."""
    code, out = run(DESKTOP, os.path.join(ROOT, "crossmachine", "laptop_q200.jsonl"))
    assert code == 3, out
    assert "different Qiskit versions" in out


# --- attack 4: an incomplete run earns no claim ---------------------------------------

def test_D_two_empty_files_do_not_pass(tmp_path):
    """Both files env-only printed 'ALL 0 per-seed gate counts are IDENTICAL' and
    announced two distinct machines."""
    a = write(tmp_path, "env_ref.jsonl", [rows(DESKTOP)[0]])
    b = write(tmp_path, "env_cand.jsonl", [rows(LAPTOP)[0]])
    code, out = run(a, b, "--require-distinct-machines")
    assert code == 2, out
    assert "INCOMPLETE" in out
    assert "IDENTICAL" not in out


def test_D_partial_coverage_does_not_pass(tmp_path):
    """71 of 72 on both sides is not the frozen selection."""
    a = write(tmp_path, "part_ref.jsonl", rows(DESKTOP)[:-1])
    b = write(tmp_path, "part_cand.jsonl", rows(LAPTOP)[:-1])
    code, out = run(a, b)
    assert code == 2, out
    assert "frozen selection is not covered" in out


def test_D_a_real_difference_outranks_incompleteness(tmp_path):
    """A partial run that already disagrees is a finding, not a shrug. Order matters:
    the diff is evaluated before the coverage refusal."""
    rs = rows(LAPTOP)[:-1]
    i = first_run_index(rs)
    rs[i] = dict(rs[i], two_q=rs[i]["two_q"] + 1)
    b = write(tmp_path, "diff_part.jsonl", rs)
    a = write(tmp_path, "diff_ref.jsonl", rows(DESKTOP)[:-1])
    code, out = run(a, b)
    assert code == 1, out
    assert "DIFFER" in out


def test_D_genuine_single_integer_difference_is_a_finding(tmp_path):
    """The headline promise: one differing integer fails the whole comparison."""
    rs = rows(LAPTOP)
    i = first_run_index(rs)
    rs[i] = dict(rs[i], two_q=rs[i]["two_q"] + 1)
    p = write(tmp_path, "one_off.jsonl", rs)
    code, out = run(DESKTOP, p)
    assert code == 1, out
    assert "1 of 72 DIFFER" in out


# --- second audit: a difference in REPRESENTATION is not a difference in HARDWARE -----

@pytest.mark.parametrize("field,value,expect", [
    ("cpu_count", "16", "SAME"),          # the same 16 cores, typed as a string
    ("processor", " ", "UNKNOWN"),        # whitespace identifies nothing
    ("processor", [], "UNKNOWN"),         # neither None nor "", so it used to be a value
    ("processor", {}, "UNKNOWN"),
    ("processor", True, "UNKNOWN"),       # bool is an int and names no CPU
    ("platform", "  Windows-10-10.0.26200-SP0  ", "SAME"),
    ("processor", "amd64 family 26 model 68 stepping 0, authenticamd", "SAME"),
])
def test_E_representation_change_is_not_a_second_machine(tmp_path, field, value, expect):
    """Third occurrence of this file's recurring defect: MACHINE fields were compared
    for equality without being validated first, so a file against a copy of ITSELF
    returned DISTINCT when the copy carried cpu_count as "16", a lowercased processor,
    a padded string, or []."""
    rs = rows(DESKTOP)
    rs[0] = dict(rs[0], **{field: value})
    twin = write(tmp_path, f"repr_{field}.jsonl", rs)
    code, out = run(DESKTOP, twin, "--require-distinct-machines")
    assert f"MACHINE VERDICT: {expect}" in out, out
    assert code == 4                      # never DISTINCT, never exit 0


def test_E_identity_normalises_without_erasing_a_real_difference():
    """Normalisation must not go so far that two genuinely different CPUs collide."""
    assert C.identity(16) == C.identity("16") == C.identity(" 16 ")
    assert C.identity(16) == C.identity(16.0) == C.identity(" 16.0 ")
    assert C.identity("A  B") == C.identity("a b")
    assert C.identity(None) is C.identity("") is C.identity("   ") is None
    assert C.identity([]) is C.identity({}) is C.identity(True) is None
    assert C.identity("AuthenticAMD") != C.identity("GenuineIntel")


# --- second audit: absent on BOTH sides is not agreement -------------------------------

@pytest.mark.parametrize("field", C.PROVENANCE)
def test_F_provenance_missing_from_both_files_is_refused(tmp_path, field):
    """A field deleted from both files compares equal to itself. Deleting
    `qiskit_version` from both used to pass and report success 'for qiskit None'."""
    a = rows(DESKTOP); a[0] = {k: v for k, v in a[0].items() if k != field}
    b = rows(LAPTOP);  b[0] = {k: v for k, v in b[0].items() if k != field}
    code, out = run(write(tmp_path, f"na_{field}.jsonl", a),
                    write(tmp_path, f"nb_{field}.jsonl", b))
    assert code == 3, out
    assert "IDENTICAL" not in out


@pytest.mark.parametrize("field", sorted(C.RUN_FIELDS))
def test_F_run_provenance_missing_from_both_files_is_refused(tmp_path, field):
    """Same hole one level down: strip the source hash or the counted gate from every
    row of both files and the per-circuit sets are equal because both are {None}."""
    a = [{k: v for k, v in r.items() if k != field} for r in rows(DESKTOP)]
    b = [{k: v for k, v in r.items() if k != field} for r in rows(LAPTOP)]
    code, out = run(write(tmp_path, f"ra_{field}.jsonl", a),
                    write(tmp_path, f"rb_{field}.jsonl", b))
    assert code == 3, out


def test_F_env_seeds_contradicting_the_rows_is_refused(tmp_path):
    """The env record declares which seeds were measured. Setting it to [999] on both
    sides while the rows stayed 1000-1011 used to pass: the two declarations were equal
    to each other and neither was checked against the data."""
    a = rows(DESKTOP); a[0] = dict(a[0], seeds=[999])
    b = rows(LAPTOP);  b[0] = dict(b[0], seeds=[999])
    code, out = run(write(tmp_path, "sa.jsonl", a), write(tmp_path, "sb.jsonl", b))
    assert code == 3, out
    assert "does not declare" in out


def test_F_an_unfinished_run_is_incomplete_not_a_contradiction(tmp_path):
    """The seed check is containment, not equality, so it does not swallow the
    INCOMPLETE verdict: a declared seed with no row is an unfinished run, and saying
    'incomplete' is more useful than saying 'contradictory'."""
    a = [r for r in rows(DESKTOP) if r.get("seed") != 1011]
    b = [r for r in rows(LAPTOP) if r.get("seed") != 1011]
    code, out = run(write(tmp_path, "ua.jsonl", a), write(tmp_path, "ub.jsonl", b))
    assert code == 2, out
    assert "INCOMPLETE" in out


def test_F_dirty_must_be_false_not_merely_falsy(tmp_path):
    """`if e.get("benchpress_dirty")` treats a missing key as clean. It is not clean;
    it is unknown, and this script does not conclude from unknowns."""
    a = rows(DESKTOP); a[0] = dict(a[0], benchpress_dirty=None)
    b = rows(LAPTOP)
    code, out = run(write(tmp_path, "da.jsonl", a), write(tmp_path, "db.jsonl", b))
    assert code == 3, out


# --- second audit: two MINOR defects --------------------------------------------------

def test_G_negative_gate_counts_are_refused(tmp_path):
    """Setting every count to -1 on both sides gave '72 identical counts'. A count of
    gates has no negative values."""
    a = [dict(r, two_q=-1) if r.get("record") == "run" else r for r in rows(DESKTOP)]
    b = [dict(r, two_q=-1) if r.get("record") == "run" else r for r in rows(LAPTOP)]
    code, out = run(write(tmp_path, "ga.jsonl", a), write(tmp_path, "gb.jsonl", b))
    assert code == 3, out
    assert "negative" in out


def test_G_non_object_json_record_refuses_rather_than_crashing(tmp_path):
    """A bare `null` line parses fine and then has no .get, so the process died on an
    AttributeError -- exit 1, which this script's contract reserves for differing
    counts. A crash that impersonates a finding is worse than a crash."""
    p = os.path.join(str(tmp_path), "null.jsonl")
    with open(p, "w", encoding="utf-8") as fh:
        for r in rows(LAPTOP):
            fh.write(json.dumps(r) + "\n")
        fh.write("null\n")
    code, out = run(DESKTOP, p)
    assert code == 3, out
    assert "not an object" in out
    assert "Traceback" not in out


# --- the frozen selection is imported, not restated -----------------------------------

def test_expected_set_comes_from_the_artifact():
    """PREREGISTRATION.md claims this check introduces no selection freedom. That is
    only true while the expected set is derived from replicate.py."""
    from replicate import CIRCUITS, SEEDS
    assert C.EXPECTED_KEYS == frozenset((c, s) for c in CIRCUITS for s in SEEDS)
    assert len(C.EXPECTED_KEYS) == 72
