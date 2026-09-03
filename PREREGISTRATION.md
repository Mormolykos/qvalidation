# Pre-registration — multi-circuit replication of the §51 anchor result

**Written and committed BEFORE the experiment was run.** The git commit that adds this
file is the timestamp. Nothing below may be changed after results exist; if something
must change, it is added as a dated amendment with the reason, and the original stays.

**Author:** Panagiotis Gkilis · **Date:** 2026-09-03

---

## 1. Why this exists

The anchor result (§51) is one circuit. `bv_n140` was chosen **after** looking at which
circuits had large seed spread. A reviewer is entitled to say: *you ran 58 circuits,
found the noisiest one, and built a finding on it.* **That objection is currently
correct and it is fatal.** Post-hoc selection cannot be argued away; it can only be
replaced by a design that never had the chance to select.

This study therefore fixes the circuit list, the protocol and the analysis **before**
any of the new measurements exist, and commits to reporting **every** circuit — including
those that show nothing.

## 2. The question, stated once

> Across a circuit sample chosen without reference to its results, at what rate does
> Benchpress's three-run unseeded protocol return a regression verdict that disagrees
> with the estimated long-run mean change of the same measurement?

This is **not** a question about Qiskit's quality, and no causal attribution to any
commit is attempted.

## 3. Circuit selection rule — outcome-blind, fixed here

**Population:** all 58 circuits in `qasmbench-large` at Benchpress commit
`b695f30e83a32bac05b9b4d8e98d37ba9aae5236` (hashes in `results/raw/benchpress_pin.json`).

**Selection rule:** include every circuit whose **total wall-clock time for 12 seeds on
`heavy-hex` under Qiskit 2.0.2**, as already recorded in
`results/raw/bp_large_heavy-hex_q202.jsonl`, is **≤ 10.0 seconds**.

**Justification and its cost, stated plainly.** The rule selects on **compute cost only**.
Runtime is recorded in the existing census and is independent of the change between
versions and of the error rate — neither quantity is consulted. This makes the rule
outcome-blind, which is the property that matters.

Its cost is a real bias and is **not** hidden: fast circuits are systematically *smaller*
circuits. The sample is therefore a convenience sample of small circuits, and the result
generalises to the corpus only under the assumption — untested here — that decision-error
behaviour does not depend on circuit size. §48 found errors on circuits of 30, 64, 70 and
140 qubits, which is weak evidence against a strong size dependence, but it is not a test.

**`bv_n140` is excluded from the primary analysis** even if it satisfies the rule, because
it was selected post-hoc. It is reported separately as the anchor, never pooled with the
pre-registered sample.

**No circuit may be added or removed after results exist.** A circuit that crashes or
times out is reported as a crash, not dropped.

## 4. Protocol — frozen, identical to §48–§51

| item | value |
|---|---|
| baseline | Qiskit **1.4.3** (the earlier version) |
| candidate | Qiskit **2.0.0** |
| direction | forward, baseline → candidate. **Never reversed.** |
| topology | `heavy-hex` |
| observable | Benchpress's own `count_ops()[two_q_gate_type]` |
| seeds | **200 per arm**, drawn from 7 … 2³¹ by `np.random.default_rng(20260904)` |
| process structure | **10 chunks, one OS process each**, distinct `PYTHONHASHSEED` |
| runs per version, k | **3** |
| decision threshold | **+10%** |
| decision rule | integer-exact `q·Sb ≥ (q+p)·Sa`, enumerated or Monte-Carlo sampled |

## 5. Analysis plan — fixed before the data exists

For each circuit:

1. **Estimated long-run change** = ratio of arm means. Its 95% interval by percentile
   bootstrap over seeds, jointly resampled across the paired arms, B = 4000.
   *This is an estimated long-run mean, not ground truth.*
2. **Verdict classification.** `REGRESSION` if the interval lies entirely above +10%;
   `NO_REGRESSION` if entirely below; otherwise **`UNRESOLVED`** — and unresolved
   circuits are **excluded from the error-rate analysis and reported as unresolved**,
   never reclassified.
3. **Decision-error rate.** For `REGRESSION`, the false-negative rate 1 − P(call); for
   `NO_REGRESSION`, the false-positive rate P(call). 95% interval by seed bootstrap,
   B = 400.
4. **Boundary flag.** A circuit whose estimated change is within **3 pp** of +10% is
   flagged `BOUNDARY` and reported separately, per D-1.6. It is not counted in the
   headline.

**Primary endpoint:** the proportion of non-boundary, resolved circuits whose
decision-error interval **excludes zero**, with a Wilson 95% interval.

**Secondary endpoints, all pre-specified:** the distribution of error rates; the same
proportion at k ∈ {1, 3, 5, 8, 10, 20}; the same at thresholds {5%, 10%, 15%, 20%}.

## 6. What would falsify the anchor result's generality

Stated **before** seeing anything, so it cannot be moved afterwards:

- **REFUTED as a class:** the primary endpoint's Wilson interval includes zero — i.e. no
  circuit besides the post-hoc anchor shows a decision-error rate distinguishable from
  zero. The anchor then stands as a single anomaly and must be described that way.
- **WEAK:** primary endpoint below 0.10. Real but rare; the anchor was an outlier.
- **SUPPORTED:** primary endpoint at or above 0.10 with the interval excluding zero.
- **STRONG:** at or above 0.25 with the interval excluding zero.

These labels are for the write-up. **The measured proportion and its interval are
reported regardless**, and no label changes any number.

## 7. Commitments

1. **Every selected circuit is reported**, including those with a zero error rate,
   unresolved truth, or a crash.
2. **No circuit is added, removed, or reclassified after results exist.**
3. **No threshold, k, estimator or inclusion rule is changed** because of what the
   results show. Any change is an amendment below, dated, with its reason.
4. Raw per-seed data for every circuit is committed.
5. If the result refutes the generality of the anchor, that is written in the record and
   in the README with the same prominence the positive result would have received.

## 8. Amendments

*(none — any amendment must be appended here with its date and reason, and must not
alter the text above)*
