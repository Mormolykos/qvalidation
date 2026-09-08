# Cross-machine pre-registration — written before the second machine existed

**Committed 2026-09-08, before any second machine had run a single circuit.** The point
of the file is the commit order, exactly as with `PREREGISTRATION.md` for the primary
study: `git log --diff-filter=A -- crossmachine/` shows this document was added before
`laptop_*.jsonl`. If it were written afterwards it would be a description of a result,
not a prediction about one.

## What is being tested, and what is not

**Being tested:** whether a fixed `seed_transpiler` produces the *same* 2-qubit gate
count on a second physical machine.

**NOT being tested:** the primary result. Nobody is re-running 39 circuits × 200 seeds ×
2 versions on a laptop. The paper's finding — that *unseeded* compilation produces
unstable verdicts — is a statement about variance on one machine and does not depend on
this check at all.

The reason to run it is narrower and worth stating plainly. §3.4 asserts determinism as a
control: the observable is a deterministic function of the seed. Until 2026-09-08 the
paper said that was verified "across processes and machines", which was **false** — all
196 environment records carry one platform string and the schema records no CPU vendor
(see `SETTLED.json` S24). The claim was corrected to one machine. This run is the
attempt to earn the stronger claim back with evidence instead of deleting it.

## Selection — deliberately zero new freedom

**Circuits and seeds are inherited, not chosen.** They are exactly the set already frozen
in `replication/expected.json`:

- **6 circuits:** `bv_n30`, `knn_n31`, `adder_n28`, `dnn_n33`, `cat_n35`, `ghz_n40`
- **12 seeds:** 1000–1011
- **1 topology:** heavy-hex

That set was fixed by a rule recorded in `replication/replicate.py` before any of it was
looked at again — the four fastest heterogeneous circuits plus two of the fastest with a
measured ρ spread of exactly zero. **Reusing it means this check introduces no selection
decision of its own.** Two of the six are deterministic negative controls, so a machine
difference that moved everything would be distinguishable from one that moved only the
stochastic circuits.

## Two runs, because they answer different questions

| run | versions | what it proves |
|---|---|---|
| **A** | 2.0.0 → 2.0.2 | The existing artifact reproduces on independent hardware. Run **unmodified**. |
| **B** | 1.4.3 → 2.0.0 | The **primary study's version pair** is fixed-seed deterministic across machines. |

Run A alone is not enough, and saying otherwise would be the error this file exists to
prevent: **the committed artifact tests 2.0.0 → 2.0.2, while the paper's primary study is
1.4.3 → 2.0.0.** Passing A would license "the replication artifact reproduces on a second
machine" and nothing more. Only B touches the version pair the paper is about.

## The prediction, stated in advance

**All 216 per-seed gate counts (6 circuits × 12 seeds × 3 versions) will be identical on
both machines.** Not close — identical. These are integer gate counts from a deterministic
pass sequence under a fixed seed.

## What each outcome means

- **Both runs match exactly** → §3.4 may say determinism was verified across two physical
  machines, and the second machine's platform string is recorded as the evidence.
- **Any mismatch** → the observable is **not** machine-independent. That is a more
  interesting result than a pass, it is reported as a finding rather than buried, and the
  determinism control in §3.4 is weakened accordingly, not quietly reworded.
- **The run cannot be completed** (environment, memory, time) → nothing is claimed. "We
  could not look" is not "there is no difference". See `feedback_unverified_is_not_negative`.

## Rules for the second machine

1. **`replication/replicate.py` is not to be modified.** Run A uses it exactly as
   committed. A changed artifact proves nothing about the committed one.
2. **The comparison is against values already in this repository**, committed from the
   desktop before the laptop ran. The laptop cannot influence its own reference.
3. **No circuit or seed is added, dropped or substituted** after seeing any laptop output.
4. **The platform string, CPU count and Python version of the second machine are recorded
   in the output**, so the claim "two machines" is checkable rather than asserted.
5. **A partial run is reported as partial.** If only run A completes, only run A is
   claimed.

## Why the observable might legitimately differ

Recorded in advance so that a mismatch is interpreted rather than explained away:

- a different Qiskit patch version, which `--require-qiskit` aborts on;
- a different Benchpress revision, which `verify.py` check 1 aborts on;
- a different `rustworkx` build, where the routing pass's own RNG or tie-breaking could
  differ by architecture — **this is the interesting one**, and the one this run exists
  to probe;
- floating-point differences in layout scoring that change a tie-break.

The first two are guarded and would be reported as setup failures, not as findings. The
last two would be genuine machine dependence.
