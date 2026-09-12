"""An exact tie at the threshold must be UNRESOLVED, not a regression.

WHY (Astra A12)
    PREREGISTRATION.md §5.2 declares the +10% threshold INCLUSIVE and an exact tie
    UNRESOLVED. Float arithmetic does not give that for free: with A = 100 and B = 110 the
    change is mathematically exactly 1/10, but `110/100 - 1` evaluates to
    0.10000000000000009, which is strictly greater than 0.10. A bootstrap interval sitting
    exactly on the cut was therefore classified REGRESSION.

    The decision rule itself was never affected -- `exact_rate_int` compares
    q*S_B >= (q+p)*S_A in integers -- so no recorded risk changes. The defect was in the
    verdict path only, and the closest CI endpoint in the 39 recorded circuits is 2.3e-3
    from the cut, two million times the guard width. These tests pin the policy so it
    cannot drift back.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prereg_analysis as pa
from deep import exact_rate_int


def _drive(monkeypatch, a_vals, b_vals):
    seeds = np.arange(1000, 1000 + len(a_vals), dtype=np.int64)

    def fake(circuit, ver, topo="heavy-hex"):
        vals = a_vals if ver == "143" else b_vals
        return seeds, np.array(vals, dtype=np.int64), ("1.4.3" if ver == "143"
                                                       else "2.0.0")
    monkeypatch.setattr(pa, "load_seeded", fake)
    return pa.analyse("synthetic", 0.10, 3, np.random.default_rng(0))


def test_float_representation_of_the_exact_cut_is_above_it():
    """The arithmetic fact the guard exists for. If this ever fails, the guard is
    unnecessary -- and the comment explaining it is wrong."""
    assert 110 / 100 - 1 > 0.10
    assert 110 / 100 - 1 == pytest.approx(0.10, abs=1e-15)


def test_exact_tie_is_unresolved_not_regression(monkeypatch):
    """A = 100, B = 110 everywhere: theta is exactly +10%, so no bootstrap resample can
    move it. Under an inclusive threshold this is a tie, and a tie is UNRESOLVED."""
    row = _drive(monkeypatch, [100] * 12, [110] * 12)
    assert row["status"] == "OK"
    assert row["verdict"] == "UNRESOLVED", row


def test_a_hair_above_the_cut_is_still_a_regression(monkeypatch):
    """The guard must not swallow real signal. 100 -> 111 is +11%, comfortably above."""
    row = _drive(monkeypatch, [100] * 12, [111] * 12)
    assert row["verdict"] == "REGRESSION", row


def test_a_hair_below_the_cut_is_still_no_regression(monkeypatch):
    row = _drive(monkeypatch, [100] * 12, [109] * 12)
    assert row["verdict"] == "NO_REGRESSION", row


def test_tie_eps_is_far_smaller_than_any_recorded_distance():
    """The guard cannot reclassify a recorded circuit. Closest recorded CI endpoint to the
    cut is 2.3e-3; TIE_EPS is 1e-9."""
    import csv
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = []
    with open(os.path.join(root, "results", "summary", "prereg_heavy-hex.csv"),
              encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            for k in ("change_ci_lo_pct", "change_ci_hi_pct"):
                if r.get(k) not in ("", None):
                    d.append(abs(float(r[k]) / 100 - 0.10))
    assert min(d) > pa.TIE_EPS * 1000, f"closest endpoint {min(d):.3e}"


def test_decision_rule_itself_fires_on_the_tie():
    """Separately from the verdict: the INCLUSIVE rule must call an exact tie. This is the
    part that was always correct, and it stays correct."""
    o = np.full(5, 100, dtype=np.int64)
    n = np.full(5, 110, dtype=np.int64)
    assert exact_rate_int(o, n, 0.10, 3) == 1.0
    assert 110 * 10 >= 100 * 11          # q*S_B >= (q+p)*S_A, in integers


def test_raw_endpoint_uses_the_same_tie_policy():
    """Two reconstruction paths with different tie policies would be a silent fork."""
    import raw_endpoint
    assert raw_endpoint.TIE_EPS is pa.TIE_EPS


def test_benchpress_pin_is_line_ending_independent():
    """Astra A14: the recorded module hashes were CRLF working-tree bytes -- 0 of 5 match
    on an LF checkout, so stage 1 was guaranteed to fail for every replicator who was not
    the author. The canonical contract must give the same answer for either checkout."""
    import hashlib
    from sweep_bp import canonical_bytes
    crlf = b'line one\r\nline two\r\n'
    lf = b'line one\nline two\n'
    assert crlf != lf
    assert canonical_bytes(crlf) == canonical_bytes(lf) == lf
    assert (hashlib.sha256(canonical_bytes(crlf)).hexdigest()
            == hashlib.sha256(canonical_bytes(lf)).hexdigest())
