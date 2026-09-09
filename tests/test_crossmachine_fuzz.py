"""Attack the comparator mechanically, instead of waiting for an auditor to do it.

WHY THIS FILE EXISTS
    Three consecutive repairs of `crossmachine/compare.py` were declared finished and
    then broken by an external auditor: missing fields, then differences in
    representation, then values that were present but meaningless -- `cpu_count` as
    "NaN", `qiskit_version` as "", a duplicate JSON member erasing the measurement it
    contradicted. Each round was fixed by teaching the checker one more specific thing
    to reject, and each round the next value nobody had thought of walked through.

    Enumerating hostile values by hand is what failed. So this file stops enumerating
    and states the PROPERTIES that must hold for every mutation of a real evidence file,
    then generates thousands of mutations and checks them. The point is not that these
    particular mutations matter; it is that the properties are checked by something that
    does not share the author's blind spots, and that a future edit to compare.py which
    reopens any of these holes fails here rather than in an audit.

THE THREE PROPERTIES
    1. One machine cannot become two. No corruption of a file -- blanking a field,
       retyping it, changing its case or spacing, feeding it NaN -- may turn a
       comparison of a machine against a copy of itself into DISTINCT. (Mutations that
       install a plausible DIFFERENT machine are excluded: a file that claims another
       platform must be believed, since forgery is not detectable here.)
    2. A changed measurement is never reported as identical.
    3. The process only ever exits with a documented code, and never on a traceback.
       Exit 1 means "the counts differ"; a crash must not impersonate a finding.
"""

import contextlib
import io
import json
import os
import random
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "crossmachine"))

import compare as C  # noqa: E402

DESKTOP = os.path.join(ROOT, "crossmachine", "desktop_q143.jsonl")
LAPTOP = os.path.join(ROOT, "crossmachine", "laptop_q143.jsonl")
DOCUMENTED_EXITS = {0, 1, 2, 3, 4}

# Values that are hostile but never amount to "a different real machine": blanks, wrong
# types, impossible numbers, and re-spellings of a value the file already carries.
HOSTILE = ["", " ", "\t", "\n ", [], {}, [1], {"a": 1}, None, True, False,
           0, -1, -1.0, 2.5, "NaN", "Infinity", "-inf", "1e400", 1e308 * 10,
           10 ** 30, "0" * 64, "z" * 64, "0" * 40, "null", "None", 0.0, "0"]


def rows(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def compare(ref, cand, strict=True):
    """Run the real main() in-process and return (exit code, output, crashed?)."""
    argv = ["compare.py", "--reference", ref, "--candidate", cand]
    if strict:
        argv.append("--require-distinct-machines")
    buf, old = io.StringIO(), sys.argv
    sys.argv = argv
    try:
        with contextlib.redirect_stdout(buf):
            C.main()
        return 0, buf.getvalue(), False
    except SystemExit as exc:
        return (exc.code or 0), buf.getvalue(), False
    except Exception as exc:                                        # noqa: BLE001
        return None, f"{buf.getvalue()}\n{type(exc).__name__}: {exc}", True
    finally:
        sys.argv = old


def write(path, rs, raw=None):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(raw if raw is not None
                 else "".join(json.dumps(r) + "\n" for r in rs))
    return path


def respellings(v):
    """The same value written differently. Never a different machine."""
    if not isinstance(v, str):
        return []
    return [v.upper(), v.lower(), f"  {v}  ", v.replace(" ", "   "), v + "\t"]


def mutate(rs, rng):
    """One random corruption of a loaded evidence file. Returns (rows, description)."""
    rs = [dict(r) for r in rs]
    i = rng.randrange(len(rs))
    row = rs[i]
    kind = rng.choice(["set", "delete", "duplicate_row", "drop_row", "extra_env",
                       "respell", "reorder"])
    if kind == "delete" and len(row) > 1:
        f = rng.choice(sorted(row))
        rs[i] = {k: v for k, v in row.items() if k != f}
        return rs, f"delete {f} from row {i}"
    if kind == "duplicate_row":
        rs.insert(i, dict(row))
        return rs, f"duplicate row {i}"
    if kind == "drop_row":
        rs.pop(i)
        return rs, f"drop row {i}"
    if kind == "extra_env":
        rs.insert(rng.randrange(len(rs) + 1), dict(rs[0]))
        return rs, "a second env record"
    if kind == "reorder":
        rng.shuffle(rs)
        return rs, "records shuffled"
    if kind == "respell":
        f = rng.choice(sorted(row))
        alts = respellings(row[f])
        if alts:
            rs[i] = dict(row, **{f: rng.choice(alts)})
            return rs, f"respell {f} in row {i}"
    f = rng.choice(sorted(row))
    v = rng.choice(HOSTILE)
    rs[i] = dict(row, **{f: v})
    return rs, f"set {f}={v!r} in row {i}"


@pytest.mark.parametrize("seed", range(6))
def test_one_machine_never_becomes_two(tmp_path, seed):
    """PROPERTY 1. A machine compared against a corrupted copy of ITSELF may be SAME or
    UNKNOWN, and may be refused. It may never be DISTINCT: no amount of editing one
    record turns one box into two."""
    rng = random.Random(seed)
    base = rows(DESKTOP)
    p = os.path.join(str(tmp_path), "mutant.jsonl")
    for _ in range(120):
        mutant, what = mutate(base, rng)
        code, out, crashed = compare(DESKTOP, write(p, mutant))
        assert not crashed, f"{what}\n{out}"
        assert code in DOCUMENTED_EXITS, f"exit {code} for {what}\n{out}"
        assert "MACHINE VERDICT: DISTINCT" not in out, f"{what}\n{out}"


@pytest.mark.parametrize("seed", range(6))
def test_a_changed_measurement_is_never_identical(tmp_path, seed):
    """PROPERTY 2. Alter one gate count in an otherwise valid file. The comparison must
    not succeed -- it may report the difference (1) or refuse the file (3), but exit 0
    would mean a changed measurement was certified as unchanged."""
    rng = random.Random(1000 + seed)
    base = rows(LAPTOP)
    runs = [i for i, r in enumerate(base) if r.get("record") == "run"]
    p = os.path.join(str(tmp_path), "changed.jsonl")
    for _ in range(60):
        rs = [dict(r) for r in base]
        i = rng.choice(runs)
        rs[i] = dict(rs[i], two_q=rs[i]["two_q"] + rng.choice([1, -1, 7, 100]))
        code, out, crashed = compare(DESKTOP, write(p, rs), strict=False)
        assert not crashed, out
        assert code != 0, f"a changed count exited 0\n{out}"
        assert "per-seed gate counts are IDENTICAL" not in out, out


@pytest.mark.parametrize("seed", range(4))
def test_raw_text_corruption_never_crashes_or_certifies(tmp_path, seed):
    """PROPERTY 3, at the byte level: truncated lines, repeated JSON members, stray
    scalars. A duplicate member is the one that mattered -- `{"two_q": 61, "two_q": 60}`
    is valid JSON and every default decoder keeps 60, so the contradiction was resolved
    before the duplicate-row guard could ever see it."""
    rng = random.Random(2000 + seed)
    lines = open(LAPTOP, encoding="utf-8").read().splitlines()
    run_lines = [i for i, l in enumerate(lines) if '"record": "run"' in l]
    p = os.path.join(str(tmp_path), "raw.jsonl")
    for _ in range(60):
        ls = list(lines)
        j = rng.choice(run_lines)
        obj = json.loads(ls[j])
        choice = rng.randrange(4)
        if choice == 0:                                  # a repeated member
            ls[j] = ls[j].replace(f'"two_q": {obj["two_q"]}',
                                  f'"two_q": {obj["two_q"] + 1}, '
                                  f'"two_q": {obj["two_q"]}', 1)
        elif choice == 1:                                # a truncated line
            ls[j] = ls[j][:rng.randrange(1, len(ls[j]))]
        elif choice == 2:                                # a stray scalar record
            ls.insert(j, rng.choice(["null", "[]", "17", '"text"', "true", "{}"]))
        else:                                            # a blank and a repeat
            ls.insert(j, "")
            ls.insert(j, ls[j + 1])
        code, out, crashed = compare(DESKTOP, write(p, None, raw="\n".join(ls) + "\n"))
        assert not crashed, out
        assert code in DOCUMENTED_EXITS, f"exit {code}\n{out}"
        # Every corruption above genuinely damages the evidence -- a repeated member, a
        # truncated line, a record that is not env or run, a repeated row. None of them
        # may be certified.
        assert code != 0, f"corruption {choice} certified\n{out}"


def test_the_genuine_pair_survives_all_of_this():
    """The properties above must not have been satisfied by making the checker refuse
    everything. The real evidence still passes, unmodified."""
    code, out, crashed = compare(DESKTOP, LAPTOP)
    assert not crashed and code == 0, out
    assert "ALL 72 per-seed gate counts are IDENTICAL" in out
    assert "MACHINE VERDICT: DISTINCT" in out
