# Finite-sample decision risk in unseeded quantum compiler benchmarking

**Panagiotis Gkilis** · BedVibe Studios, Oslo, Norway · <bedvibe@bedvibe.studio>
ORCID 0009-0007-3805-170X

*Draft, 2026-09-04. Not submitted. All data and code:* `qvalidation` *repository.*

---

## Abstract

Quantum compiler benchmarks are used to accept or reject changes to production
transpilers, but the compilers they measure are stochastic. We show that at the pinned
revision of IBM's Benchpress benchmark suite, its Qiskit gym compiles without passing
`seed_transpiler`, so every gate count it reports is one draw from an unmeasured
distribution — while the BQSKit gym in the same repository does seed its compiler. We
quantify the consequence as **finite-sample decision risk**: the probability that a
regression verdict computed from *k* runs per version disagrees with the verdict implied
by the same measurement's long-run mean.

In a pre-registered study of 39 QASMBench circuits (28–420 qubits) transpiled to a
heavy-hex lattice under Qiskit 1.4.3 and 2.0.0, using 200 independent transpiler seeds
per arm across ten operating-system processes, we find that circuits whose compilation is
deterministic carry zero risk by construction, while among the 23 resolved circuits whose
compilation is stochastic the risk falls with distance from the decision boundary — an
association that is largely induced by the decision rule itself and which we therefore do
not claim as a mechanism (§4.1). Seven of 26 eligible circuits
carry a risk of at least 5% and four carry at least 10% under a +10% threshold. The
median circuit admits an **ambiguity band of 10.9 percentage points** — a window of true
change the three-run protocol cannot resolve in either direction, independent of the
version pair.

Two of the three circuits named in Qiskit issue #14402 are affected. We reproduce that
issue's reported figures to within 0.5 and 2.4 percentage points on its two low-variance
circuits, and show that its remaining figure (+46.1% on `bv_n140`) is one draw from a
distribution its own protocol produces spanning −10.5% to +100.0%.

We do not claim a suite-level failure rate; our sample is underpowered for one. We claim
that finite-sample decision risk is measurable, reproducible, mechanistically explained,
and non-negligible on a benchmark used in production.

---

## 1. Introduction

Compiler benchmarks answer a binary question: is this change a regression? For classical
compilers the measurement is nearly deterministic and the question is nearly settled by
one run. For quantum compilers it is not. Routing a circuit onto a constrained qubit
topology is NP-hard, and production transpilers use stochastic heuristics — Qiskit's
SABRE among them. The same circuit, the same compiler and the same target produce
different gate counts on different runs.

This is well known. What has not been measured is what it costs the decisions built on
top of it.

This paper is also the first output of a validation apparatus we are building, and it is
written to expose that apparatus rather than only its result. The measurement pipeline,
the pre-registration mechanism, the numeric inventory that re-derives every published
figure from raw data, the replication artifact, and the adversarial audit are all part of
the contribution. **The Qiskit experiment is the demonstration case; the reusable object
is the method for quantifying decision risk in a stochastic benchmark.** Nothing in the
apparatus is specific to Qiskit: it requires only a benchmark whose observable is a
scalar, a source of run-to-run variation that can be enumerated or sampled, and a
decision rule.

Our contribution is threefold. First, a source-level finding: **Benchpress, IBM's
cross-SDK benchmark suite, sets no transpiler seed anywhere**, and performs no
aggregation over runs, so a reported figure is one sample and the choice of estimator is
left entirely to the reader. Second, a definition and measurement: **finite-sample
decision risk**, the probability that a *k*-run verdict disagrees with the long-run
verdict of the same measurement. Third, a pre-registered experiment that measures this
risk on 39 circuits and identifies the mechanism that governs it.

We are deliberately narrow about what follows. We do not claim any published decision was
wrong, we do not attribute anything to a specific commit, and we withdraw — in §5 — a
suite-level rate that an earlier draft of this work reported.

## 2. Background

### 2.1 Benchpress

Benchpress (Nation et al., *Nature Computational Science*, 2025;
doi:10.1038/s43588-025-00792-y) compiles a corpus of circuits against abstract
topologies and records circuit properties. Its 2-qubit gate observable is, verbatim from
`benchpress/qiskit_gym/utils/io.py`:

```python
benchmark.extra_info["output_gate_count_2q"] = circuit.count_ops().get(two_qubit_gate, 0)
```

Two properties matter here, both established by reading the source at commit
`b695f30e83a32bac05b9b4d8e98d37ba9aae5236`:

1. **The Qiskit gym compiles unseeded — and a sibling gym does not.** At commit
   `b695f30e`, the Qiskit-based gyms call `generate_preset_pass_manager(
   optimization_level=..., backend=...)` with no `seed_transpiler` anywhere.
   Circuit-*construction* seeds are pinned (`seed=12345`, 14 occurrences); the
   compilation seed is not.

   ⚠ We state this for the Qiskit gym only. `seed_transpiler` and
   `generate_preset_pass_manager` are **Qiskit-specific APIs**; the other six gyms cannot
   call them and use their own interfaces — TKET, for instance, calls
   `backend.default_compilation_pass(optimisation_level=...)`. More importantly, the
   **BQSKit gym explicitly seeds its compiler**:
   `bqskit_gym/device_transpile/test_summit.py:179` calls
   `compile(circuit, model=BACKEND, optimization_level=..., compiler=compiler, seed=0)`.
   **Whether the remaining SDKs compile deterministically is not assessed here.** This is
   a claim about one revision of one repository, not a permanent property of Benchpress.
2. **No aggregation exists anywhere in the repository.** There is no mean, no minimum, no
   best-of-*k*, and no run-count option. One invocation produces one number.

Consequently the aggregation is the user's choice, and different users may choose
differently.

### 2.2 Qiskit issue #14402

In May 2025 the lead author of Benchpress reported large 2-qubit gate count increases
between Qiskit 1.4.3 and 2.0, writing: *"This was verified by running Benchpress several
times for each version to get statistics. E.g. over the full test suite the values
returned for 3 runs was:"*. Per-test figures are described as *"the avg. percent increase
in 2Q gate counts"*; the basis of that average is not stated. The largest reported cases
are `bv_n140-linear` +46%, `bv_n280-linear` +44% and `knn_341-linear` +41%.

We take *k* = 3 from this report. It is an external choice, not ours, and Benchpress
itself offers no such parameter.

## 3. Methods

### 3.1 Estimand

For circuit *c*, topology *T* and compiler versions *A* (baseline) and *B* (candidate),
let *X<sub>A</sub>(s)*, *X<sub>B</sub>(s)* be the 2-qubit gate counts produced with
`seed_transpiler = s`. These are deterministic functions of *s*; we verify this across
processes and machines (§3.4). Define the **reference change**

> θ = E<sub>s</sub>[X<sub>B</sub>(s)] / E<sub>s</sub>[X<sub>A</sub>(s)] − 1

estimated by the ratio of arm means. The protocol draws *k* seeds per arm independently
and flags a regression when (mean<sub>B</sub> − mean<sub>A</sub>)/mean<sub>A</sub> ≥ *t*.
**Finite-sample decision risk** is the probability, over the protocol's own draw space,
that its verdict differs from the verdict implied by θ.

**θ is an estimated long-run mean of the same stochastic process, not external ground
truth.** The quantity is therefore the procedure's finite-sample error relative to its own
asymptote. This is weaker than an external criterion, and no external criterion exists:
the "true" gate count of a stochastic compiler is not defined independently of the
compiler. We use the phrase *decision risk*, never *wrong answer*.

### 3.2 Decision rule, computed exactly

Gate counts are integers, so the rule is exactly decidable. With arm sums
*S<sub>A</sub>*, *S<sub>B</sub>* over *k* draws and *t = p/q* in lowest terms,

> (S<sub>B</sub> − S<sub>A</sub>)/S<sub>A</sub> ≥ p/q  ⟺  q·S<sub>B</sub> ≥ (q+p)·S<sub>A</sub>

which involves no floating point. This matters: the natural float form `b ≥ a(1+t)` is
*not* the same expression as `(b−a)/a ≥ t`, and disagreed with it in 84 of 900 randomised
cases during development. The integer form was verified against exact-integer brute force
over 900 cases with zero disagreements. Risk is then computed by enumerating all
200³ = 8,000,000 sum-triples per arm for *k* ≤ 3, and by Monte Carlo above that.

Two conventions are stated explicitly. **Draws are enumerated with replacement**, so the
tuple (s, s, s) is included; a maintainer running *k* distinct seeds corresponds to
enumeration *without* replacement. We computed both: on the pre-registered data the
per-circuit risk differs by at most 0.0011 and the count of circuits at risk ≥ 5% is
unchanged at 7. **Equality at the threshold counts as a regression call**, consistent with
the ≥ in the decision rule. The integer path is unguarded against a zero baseline sum,
which is undefined; no circuit in this study has a zero 2-qubit gate count, so the branch
is never exercised.

### 3.3 Pre-registration

The circuit list, protocol, analysis code and falsification criteria were committed
before any measurement existed. Commit order is verifiable
(`git log --diff-filter=A -- prereg_analysis.py results/raw/prereg`):

| commit | timestamp | content |
|---|---|---|
| `a36a34a` | 2026-09-03 23:51:08 | pre-registration |
| `fbc573d` | 2026-09-03 23:52:38 | analysis code and circuit list |
| `30224a0` | 2026-09-04 09:13:07 | raw data, unanalysed |

**Selection was on compute cost only:** every `qasmbench-large` circuit whose 12-seed
heavy-hex runtime in a pre-existing census was ≤ 10 s. Runtime is independent of both θ
and the risk, and neither was consulted. This yielded **39 circuits, 28–420 qubits**. One
circuit, `bv_n140`, was excluded from the primary analysis because it had been selected
post-hoc in earlier exploratory work; it is reported separately in §4.4.

**Analysis, fixed in advance.** θ interval by percentile bootstrap over seeds, resampled
jointly across the paired arms, B = 4000. A circuit is `REGRESSION` if that interval lies
entirely above *t*, `NO_REGRESSION` if entirely below, otherwise `UNRESOLVED` and excluded.
A circuit whose θ lies within 3 percentage points of *t* is flagged `BOUNDARY` and
excluded. Risk interval by seed bootstrap, B = 400. The pre-registered primary endpoint is
the proportion of non-boundary, resolved circuits whose risk interval excludes zero.

### 3.4 Measurement and controls

Qiskit **1.4.3 → 2.0.0**, forward, topology `heavy-hex`, Benchpress pinned at
`b695f30e` with module and all 58 circuit hashes recorded. **200 seeds per arm**, drawn
from 7 … 2³¹ (realised range 663,193 – 1,105,794,431, zero consecutive pairs), split
across **ten OS processes per arm** with differing `PYTHONHASHSEED`. **15,600
transpilations.**

Controls, each of which could have invalidated the study:

- **Backend randomness.** `FlexibleBackend` draws error rates unseeded, differently on
  every construction, and the two arms build backends separately. At optimization level 2
  the layout passes score with error rates. Tested with four verified-distinct draws ×
  six circuits × four seeds: **0 of 24 cases changed the observable.**
- **Observable identity.** `two_q_gate_type` is `cz` in all three Qiskit versions and on
  all four topologies; transpiled output contains no other 2-qubit gate.
- **Backend identity.** Coupling map identical across versions (278 edges, hash
  `ef616023`), as are the basis gates.
- **Seed independence.** Lag-1 autocorrelation of consecutive seeds between −0.22 and
  +0.11; contiguous and scattered seed sets give matching spreads.
- **Determinism.** A fixed seed reproduces bit-identically across processes and machines;
  a six-circuit replication artifact reproduces **144 of 144** per-seed values from a
  clean state.
- **Selection bias.** The cost rule does not favour high-variance circuits: median seed
  spread 0.1126 among selected versus 0.1234 among excluded, Mann-Whitney p = 0.768.

## 4. Results

### 4.1 The mechanism

Of the 26 eligible circuits, **13 compile deterministically** — every seed gives the same
gate count in both arms. Their risk is zero *by arithmetic*, not by measurement, and we
do not report this as evidence.

Among the **23 resolved circuits whose compilation is stochastic** (note the denominator:
23 of the 36 *resolved* circuits, of which 13 are also non-boundary and therefore
*eligible*), risk falls with distance from the decision boundary:

> **Spearman ρ = −0.833 between distance from θ to the threshold and the risk
> (p < 0.001, n = 23).**

⚠ **This is not a discovered mechanism, and we do not claim it as one.** Risk is a
monotone decreasing function of |θ − t| for *any* distribution, by the definition of the
decision rule. We verified the size of this induced effect by simulation: on synthetic
circuits with θ and spread drawn independently — containing no compiler at all — the same
statistic has mean −0.661 (30 trials of 23 circuits), and 5 of 30 trials reach −0.833 or
stronger. **The sign and rough magnitude of this correlation are properties of the
decision rule, not evidence about Qiskit.**

What *is* empirical is the **scale** of the seed-induced spreads that make the risk
non-negligible at a given distance — reported as ambiguity bands in §4.3 — and the fact
that 13 of 26 eligible circuits have no spread at all. The apparent clustering of outcomes by
algorithm family — `adder`, `knn`, `cc`, `swap_test`, `bv`, `qft` affected; `cat`, `ghz`,
`ising`, `wstate` not — is a consequence: the latter families compile deterministically on
this topology and therefore cannot err.

### 4.2 Magnitude

| criterion | circuits | proportion | Wilson 95% CI |
|---|---:|---:|---|
| risk > 0 (pre-registered endpoint) | 12 / 26 | 46.2% | [28.8, 64.5] |
| risk ≥ 5% | 7 / 26 | 26.9% | [13.7, 46.1] |
| risk ≥ 10% | 4 / 26 | 15.4% | [6.2, 33.5] |

The pre-registered endpoint's Wilson interval **assumes independent circuits and is
therefore too narrow**; a cluster bootstrap treating algorithm family as the resampling
unit gives [17.4%, 81.0%]. With eleven families this is uninformative, and we accordingly
**do not advance a suite-level rate** (§5.1). The distribution over eligible circuits has
**median 0**, p75 = 6.9%, p90 = 14.2%, max = 17.3%.

The highest-risk eligible circuits:

| circuit | θ | 95% CI | risk | 95% CI |
|---|---:|---|---:|---|
| `bv_n280` | +4.89% | [+3.67, +6.11] | 17.31% | [11.60, 23.69] |
| `knn_n67` | +6.67% | [+5.83, +7.51] | 16.70% | [10.83, 23.81] |
| `swap_test_n83` | +6.76% | [+6.02, +7.50] | 15.67% | [10.19, 22.75] |
| `adder_n118` | +6.47% | [+5.70, +7.21] | 12.67% | [8.16, 19.25] |
| `knn_341` | +6.20% | [+5.69, +6.71] | 4.68% | [2.70, 7.68] |

### 4.3 The ambiguity band — free of θ, not free of the version pair

The risk in §4.2 depends on where θ happens to sit. The **ambiguity band** does not: it is
the width of the interval of true change over which P(call) runs from 0.05 to 0.95, and
contains no θ and no direction.

⚠ **It is not, however, version-pair-free, and an earlier draft of this paper wrongly
called it that.** The band is computed by sweeping a synthetic change over the *measured
per-seed residual* of the 1.4.3 → 2.0.0 pair, so its shape is inherited from that pair
even though its location is not. It is also computed under a **multiplicative** residual
model. That model is not the better-fitting one on this topology — an additive model fits
better on 29 of 39 circuits — so we recomputed the band additively: the median moves from
**10.86 pp to 10.73 pp**, and is wider under the additive model on only 1 of 23 circuits.
The figure is therefore robust to the model choice, but the choice is a modelling
assumption and is stated here rather than buried.

> **Among the 23 stochastic circuits, the median ambiguity band is 10.9 percentage
> points** (p75 = 14.8, max = 25.2).

For the median stochastic circuit in this sample, a true change anywhere in an
11-point-wide window around the threshold is unresolvable by a three-run comparison, in
either direction. We claim this for the circuits, topology, SDK and version pair measured
here; extending it to other version pairs requires measuring their residuals.

This also disposes of the objection that the effect is mere threshold proximity.
`cc_n32` has θ = −8.28% (per-seed t-CI [−9.13, −6.05]), **18.3 percentage points below**
the +10% threshold, and is nonetheless called a regression on 6 of 1728 sampled
triple-pairs (0.37%). Its ambiguity band is 24.5 points. A single-run comparison of the
same circuit can return +49.5%.

### 4.4 Issue #14402

Two of the three circuits named in #14402 fall in the blind pre-registered sample, chosen
by the cost rule: `bv_n280` (risk 17.31%) and `knn_341` (risk 4.68%). The third,
`bv_n140`, was measured separately at 400 seeds across 21 processes: θ = +5.374%
[+4.272, +6.495] on heavy-hex, risk **24.4%** [19.5, 31.1]. **It is not part of the
pre-registered endpoint.**

We reproduce the issue's reported figures where seed spread is small, and fail to where
it is large — the pattern predicted by our own account, and not by a Benchpress version
difference, which would not be selective:

| circuit | issue | ours | difference | seed spread |
|---|---:|---:|---:|---:|
| `bv_n280` | +44.0% | +44.5% | +0.5 pp | 0.6% |
| `knn_341` | +41.0% | +43.4% | +2.4 pp | 1.0% |
| `bv_n140` | +46.1% | +35.2% | −10.9 pp | 44.4% |

On `linear`, `bv_n140`'s reference change is +31.0% [+28.4, +33.8] at 200 seeds per arm.
A single three-run comparison of that circuit — the issue's own protocol — returns
anywhere from **−10.5% to +100.0%**, with a 95% range of [+9.3%, +57.2%]. The issue's
+46.1% sits at the 88th percentile of that distribution, and the same range extends below
the +10% threshold.

### 4.5 Sensitivity

**Threshold.** The endpoint is non-zero at every cut tested: 5% → 36.4%, 7.5% → 22.2%,
10% → 46.2%, 12.5% → 60.0%, 15% → 60.5%, 20% → 46.2%. The finding is not an artifact of
the +10% choice, though that choice remains ours.

**Runs per version.** On `bv_n140`/heavy-hex, pooled over 400 seeds (Monte Carlo,
4 × 50M samples per point; spread across seeds ≤ 0.012 pp):

| *k* | 1 | 3 | 5 | 8 | 10 | 20 |
|---|---:|---:|---:|---:|---:|---:|
| risk | 34.58% | 24.38% | 18.56% | 12.94% | 10.36% | **3.74%** |

Monte-Carlo standard error ≤ 0.02 pp per entry; the final digit of each is not
significant and should not be quoted alone.

**Twenty runs per version — on the order of 40 hours of compute at the issue's stated
~2 h per suite run — still leaves 3.74%.** By contrast, one `seed_transpiler` argument removes the sampling variance at
*k* = 1.

**Aggregation.** Under minimum-of-3 rather than mean-of-3, all eight tested circuits still
err and every rate roughly doubles (`bv_n280` 17.3% → 28.4%). Best-of-*k* practice does
not remove the problem.

**Sampling design.** A disjoint set of 200 scattered seeds across ten fresh processes
reproduces `bv_n140`/heavy-hex at 22.59% [16.37, 30.61] against 26.28% [18.45, 34.20]
from the contiguous single-process set; each point falls inside the other's interval.

## 5. Threats to validity

### 5.1 What we withdraw

An earlier draft of this work reported a suite-level rate. **We withdraw it.** With eleven
algorithm families and near-perfect within-family homogeneity, the effective sample size
is far below 26 and no interval we can compute is informative about a population of
circuits. The pre-registered 12/26 stands as a *descriptive count of these 26 circuits*.

We also withdraw a reported correlation of ρ = +0.876 between "compilation is stochastic"
and risk. Circuits with both arms constant have zero risk by arithmetic, so a correlation
computed over a sample containing them measures a definition, and Spearman with 13 ties
at zero is the wrong statistic. Only the ρ = −0.833 among stochastic circuits is
empirical.

### 5.2 Limitations

1. **One SDK, one version pair, one topology, one machine.** No other SDK was measured,
   though source inspection shows seven further gyms also pass no seed.
2. **θ is a plug-in estimate** from 200 seeds, not an external criterion (§3.1).
3. **The threshold is ours.** Benchpress defines none; #14402 states no formal cut.
4. **Selection favours fast circuits**, which correlates with small, though the sample
   spans 28–420 qubits and the variance test in §3.4 is null.
5. **The boundary exclusion defines a restricted estimand.** Including boundary circuits
   raises the endpoint to 22/36; we report the pre-registered figure.
6. **`cc_n32`'s 0.37% rests on 6 of 1728 triples.**
7. **Pairing is not a universal remedy.** Passing `seed_transpiler` removes false
   positives but was worse on three of four circuits exhibiting false negatives.
8. **No causal attribution.** The 1.4.3 → 2.0.0 comparison spans two major releases and
   we isolate no mechanism within the compiler.

### 5.3 Adversarial review

The result was attacked in three rounds by two independent language models acting as
hostile reviewers, and by a first-principles audit that re-derived every reported number
from raw data. That audit returned **zero invalidating findings, three rewordings — two of
which are §5.1 — and two limitations**. The repository records every withdrawn claim,
including four from earlier phases of the work.

## 6. Conclusion

Unseeded stochastic compilation makes regression verdicts probabilistic, and the
probability is measurable. On a benchmark used to evaluate a production quantum compiler,
a three-run comparison cannot resolve a change within roughly eleven percentage points of
its decision threshold for the median stochastic circuit, and the two circuits from the
motivating bug report that we could evaluate blind both carry non-zero risk. Adding runs
reduces the risk slowly — on the demonstrated circuit, twenty runs per version still
leaves 3.74% — while setting a seed removes this source of sampling variance outright. We
report the measured k-sweep rather than fitting a scaling law: a log-log fit to those six
points has slope −0.70, and six points on one circuit do not establish an exponent.

The remedy is one argument. The measurement problem it solves is not exotic — it is the
ordinary consequence of treating a stochastic measurement as a scalar. We suggest that
benchmark suites for stochastic compilers should either fix seeds, or report the
distribution and the decision risk alongside any verdict.

### 6.1 The apparatus, and what it would take to generalise it

What we built is not specific to Qiskit. Given a benchmark with a scalar observable, a
enumerable source of run-to-run variation, and a decision rule, the same pipeline yields
a decision-risk estimate and an ambiguity band. Four components carried the weight and
are reusable:

1. **Toolchain pinning that includes the benchmark itself.** Our provenance records named
   only the compiler until an audit found it; the benchmark supplies the circuits, the
   backend, the topology and the observable, and is equally part of the measurement.
2. **A pre-registration mechanism with a verifiable timestamp.** Committing the circuit
   list and the analysis code before the data exists converts "we did not cherry-pick"
   from an assertion into a checkable fact.
3. **A numeric inventory.** Every published figure carries its numerator, denominator,
   sampling unit, interval, method, and a function that re-derives it from raw data. A
   single command re-checks the whole paper.
4. **Adversarial review as a required stage, not an optional one.** Three rounds of
   hostile review plus a first-principles audit removed four claims from this work,
   including two we had already published internally.

The obvious next step is more algorithm families and more SDKs; the sample here is
underpowered for population-level statements precisely because the outcome is homogeneous
within families. That is an experiment, not an analysis, and we do not pre-empt it.

## Data and code availability

All raw per-seed measurements, analysis code, the pre-registration, the defect record and
the complete research log are in the `qvalidation` repository. `verify.py` re-runs the
toolchain pin check, test suite, numeric inventory, replication artifact and a proof of a
withdrawn analytical claim in under a minute. `inventory.py --check` re-derives every
reported number from its raw source.

## References

1. Nation, P. D. et al. Benchmarking the performance of quantum computing software.
   *Nature Computational Science* (2025). doi:10.1038/s43588-025-00792-y
2. Qiskit issue #14402, *Significant increase in 2Q gate counts for many Benchpress tests
   when going from Qiskit 1.4 to 2.0*. https://github.com/Qiskit/qiskit/issues/14402
3. Li, G., Ding, Y. & Xie, Y. Tackling the qubit mapping problem for NISQ-era quantum
   devices. *ASPLOS* (2019). — SABRE
4. Pati, A. & Simmhan, Y. On the reproducibility of quantum circuit transpilation.
   arXiv:2605.07876
