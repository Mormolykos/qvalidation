"""The seed-alignment guard must refuse malformed arm pairs, not work around them.

WHY THIS FILE EXISTS
    §5.1 resamples the two arms JOINTLY. That is only valid if position i is the same
    seed in both arms. The first version of the guard (F2, 2026-09-04) compared only
    `s_o[:m]` against `s_n[:m]` with `m = min(len(a), len(b))`, which detected mispairing
    but NOT truncation: a 200-seed arm and a 199-seed arm with a matching prefix passed,
    and the 200-seed arm was then silently cut down to 199. An external code audit found
    this on 2026-09-08.

    These tests pin the three refusals and the one acceptance so the weaker guard cannot
    come back. They need no Benchpress, no Qiskit and no network: `analyse()` is driven
    through a stubbed `load_seeded`.
"""

import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import prereg_analysis  # noqa: E402


def _drive(monkeypatch, seeds_a, vals_a, seeds_b, vals_b):
    """Run analyse() against a synthetic pair of arms."""
    def fake(circuit, ver, topo="heavy-hex"):
        if ver == "143":
            return (np.array(seeds_a, dtype=np.int64),
                    np.array(vals_a, dtype=np.int64), "1.4.3")
        return (np.array(seeds_b, dtype=np.int64),
                np.array(vals_b, dtype=np.int64), "2.0.0")
    monkeypatch.setattr(prereg_analysis, "load_seeded", fake)
    return prereg_analysis.analyse("synthetic", 0.10, 3, np.random.default_rng(0))


def test_A_truncated_arm_with_matching_prefix_is_refused(monkeypatch):
    """200 seeds against 199 that match on the prefix. The OLD guard passed this and
    silently truncated the good arm; it must now be refused."""
    a_seeds = list(range(1000, 1200))            # 200
    b_seeds = list(range(1000, 1199))            # 199, identical prefix
    row = _drive(monkeypatch, a_seeds, [100] * 200, b_seeds, [110] * 199)
    assert row["status"] == "MISALIGNED_SEEDS", row
    assert "unequal arm lengths" in row["reason"]
    assert "200" in row["reason"] and "199" in row["reason"]
    assert "verdict" not in row, "a refused pair must not be analysed"


def test_B_equal_length_different_seed_is_refused(monkeypatch):
    """Same count, one differing identity."""
    a_seeds = list(range(1000, 1012))
    b_seeds = list(range(1000, 1011)) + [9999]
    row = _drive(monkeypatch, a_seeds, [100] * 12, b_seeds, [110] * 12)
    assert row["status"] == "MISALIGNED_SEEDS", row
    assert "different seed identities" in row["reason"]
    assert "verdict" not in row


def test_C_duplicate_seed_in_one_arm_is_refused(monkeypatch):
    """A seed recorded twice double-weights one measurement inside the bootstrap."""
    a_seeds = [1000, 1001, 1002, 1002]           # 1002 twice
    b_seeds = [1000, 1001, 1002, 1003]
    row = _drive(monkeypatch, a_seeds, [100] * 4, b_seeds, [110] * 4)
    assert row["status"] == "DUPLICATE_SEEDS", row
    assert "duplicate seed ids" in row["reason"]
    assert "verdict" not in row


def test_D_identical_unique_seed_arrays_are_accepted(monkeypatch):
    """The valid case must still go all the way through to a verdict, and must keep
    every seed — no truncation."""
    seeds = list(range(1000, 1012))
    row = _drive(monkeypatch, seeds, [100] * 12, seeds, [150] * 12)
    assert row["status"] == "OK", row
    assert row["n_seeds"] == 12, "all 12 seeds must survive"
    assert row["verdict"] in ("REGRESSION", "NO_REGRESSION", "UNRESOLVED")


def test_E_refusal_never_truncates_the_good_arm(monkeypatch):
    """The specific regression: the old code reported n_seeds = 199 for the pair in
    test A, having already cut the 200-seed arm down. A refusal reports no usable
    seed count at all."""
    row = _drive(monkeypatch, list(range(1000, 1200)), [100] * 200,
                 list(range(1000, 1199)), [110] * 199)
    assert row["n_seeds"] == 0, "a refused pair has no analysed seed count"


@pytest.mark.parametrize("bad", ["A", "B", "C"])
def test_F_no_refusal_path_reaches_the_endpoint(monkeypatch, bad):
    """endpoint() counts only status == OK. A refused row must never be eligible."""
    cases = {
        "A": (list(range(1000, 1200)), [100] * 200, list(range(1000, 1199)), [110] * 199),
        "B": (list(range(1000, 1012)), [100] * 12,
              list(range(1000, 1011)) + [9999], [110] * 12),
        "C": ([1000, 1001, 1002, 1002], [100] * 4, [1000, 1001, 1002, 1003], [110] * 4),
    }
    row = _drive(monkeypatch, *cases[bad])
    hit, elig, _, _ = prereg_analysis.endpoint([row])
    assert elig == [] and hit == [], "a refused row must not enter the endpoint"
