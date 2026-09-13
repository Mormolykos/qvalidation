# Attack packet — the pre-registered 46.2% result, stated completely enough to destroy

> ## ⛔ SUPERSEDED — this packet was written on 2026-09-04, for v1
>
> It is preserved as the record of what was handed to reviewers at that time. **Do not
> quote a number from it as current.** Three hostile audits have since forced corrections
> that this file predates, and several of its statements are now false, including the
> Status line below: the work **was** published, as
> [DOI 10.5281/zenodo.22689920](https://doi.org/10.5281/zenodo.22689920), and a
> repository exists.
>
> The current authority is [`PAPER.md`](PAPER.md) (Version 4). Every correction is
> itemised in [`V3_CORRECTION_LEDGER.md`](V3_CORRECTION_LEDGER.md) and
> [`V4_ASTRA_CORRECTION_LEDGER.md`](V4_ASTRA_CORRECTION_LEDGER.md).
> *(Astra V4-04: an old file's date does not neutralise a present-tense claim inside it.)*

**Purpose:** hand this to an adversarial reviewer. It is deliberately complete, including
every exclusion, every count, and every limitation known to the authors. Nothing is
omitted to make the result look better. If a number here is wrong, the study is wrong.

**Rule for any attacker, including us:** attack the *frozen* experiment. Do not modify
exclusions, do not re-run to get a nicer number, do not edit `PREREGISTRATION.md`. Any
new test is a labelled **follow-up attack**, reported separately from the frozen result.

**Status:** nothing published. No DOI, no repository, no paper.

---

## 1. The estimand, stated precisely — attack this first

For a circuit *c*, topology *T*, and two compiler versions *A* (baseline) and *B*
(candidate), let *X<sub>A</sub>(s)* and *X<sub>B</sub>(s)* be the 2-qubit gate count
produced by transpiling *c* onto *T* with `seed_transpiler = s`. These are deterministic
functions of *s* (verified: identical across processes and machines).

Define the **reference change**

&nbsp;&nbsp;&nbsp;&nbsp;θ = E<sub>s</sub>[X<sub>B</sub>(s)] / E<sub>s</sub>[X<sub>A</sub>(s)] − 1

estimated by the ratio of arm means over 200 seeds. **θ is an estimated long-run mean of
the same stochastic process. It is NOT external ground truth, and it is not a physical
fact about the compiler.**

The **protocol** draws *k* = 3 seeds per arm independently and flags a regression if
(mean<sub>B</sub> − mean<sub>A</sub>)/mean<sub>A</sub> ≥ *t* = 0.10.

The **decision-error rate** is the probability, over the protocol's own draw space, that
its verdict differs from the verdict implied by θ.

> **Therefore "wrong verdict" means exactly one thing: the finite-run procedure disagrees
> with what the same measurement would conclude with unlimited runs.** It does not mean
> the compiler regressed, that IBM erred, or that any published decision was incorrect.
> **Every use of "wrong" in this study should be read against that definition, and if the
> definition is unacceptable the result does not survive.**

**Known weakness of the estimand.** θ is estimated from the same process the protocol
samples. A reviewer may call this circular. Our position: it is a *self-consistency*
statement — the procedure's finite-sample error relative to its own asymptote — which is
a standard and well-defined quantity, but it is weaker than an external criterion, and no
external criterion exists here because the "true" gate count for a stochastic compiler is
not defined independently of the compiler.

---

## 2. Design, and the timestamps that make it a pre-registration

| commit | UTC+3 timestamp | content |
|---|---|---|
| `a36a34a` | 2026-09-03 23:51:08 | `PREREGISTRATION.md`: circuits, protocol, analysis, falsification criteria |
| `fbc573d` | 2026-09-03 23:52:38 | `prereg_analysis.py` and `_selected.txt` (the 39-circuit list) |
| `30224a0` | 2026-09-04 09:13:07 | raw data, 78 files, explicitly not yet analysed |
| `9ed0f46` | 2026-09-04 09:20:12 | the result |

Verify with `git log --diff-filter=A -- prereg_analysis.py results/raw/prereg`.

**Selection rule (outcome-blind):** every circuit in `qasmbench-large` whose *total
12-seed heavy-hex runtime under Qiskit 2.0.2*, in the pre-existing census, was ≤ 10.0 s.
Runtime is independent of both θ and the error rate; neither was consulted.
**39 circuits, 28–420 qubits.** `bv_n140` excluded because it had been chosen post-hoc.

**Measurement:** Qiskit **1.4.3 → 2.0.0**, forward, topology `heavy-hex`, observable
Benchpress's own `count_ops()[cz]`, Benchpress pinned at `b695f30e` with module and all
58 circuit hashes verified. **200 scattered seeds per arm** (range 663,193 – 1,105,794,431),
split across **10 OS processes per arm** with differing `PYTHONHASHSEED`.
**15,600 transpilations.**

---

## 3. The result

**Primary endpoint (pre-registered):** proportion of non-boundary, resolved circuits whose
decision-error interval excludes zero.

> **12 / 26 = 0.4615, Wilson 95% CI [0.2876, 0.6454].**
> Pre-registered label, computed by the script: **STRONG** (≥0.25 with interval excluding zero).

### Full accounting of all 39 circuits — nothing omitted

| bucket | n | why |
|---|---:|---|
| eligible, error interval **excludes** zero | **12** | the endpoint numerator |
| eligible, error interval **includes** zero | 14 | all have θ = 0.00% and zero seed spread |
| **BOUNDARY**, excluded per §5.4 | 10 | θ within 3 pp of the +10% cut |
| **UNRESOLVED**, excluded per §5.2 | 3 | θ interval straddles the cut |
| **total** | **39** | |

Note 26 = 12 + 14, and 39 = 26 + 10 + 3.

### The 12 hits, with intervals

| circuit | θ | 95% CI on θ | error kind | error rate | 95% CI |
|---|---:|---|---|---:|---|
| `bv_n280` | +4.89% | [+3.67, +6.11] | false positive | 17.31% | [11.60, 23.69] |
| `knn_n67` | +6.67% | [+5.83, +7.51] | false positive | 16.70% | [10.83, 23.81] |
| `swap_test_n83` | +6.76% | [+6.02, +7.50] | false positive | 15.67% | [10.19, 22.75] |
| `adder_n118` | +6.47% | [+5.70, +7.21] | false positive | 12.67% | [8.16, 19.25] |
| `adder_n64` | +6.12% | [+5.40, +6.85] | false positive | 9.71% | [5.95, 15.94] |
| `knn_129` | +6.46% | [+5.86, +7.03] | false positive | 9.34% | [6.00, 14.14] |
| `cc_n64` | −0.40% | [−2.06, +1.25] | false positive | 7.65% | [4.31, 12.48] |
| `knn_341` | +6.20% | [+5.69, +6.71] | false positive | 4.68% | [2.70, 7.68] |
| `adder_n28` | +4.69% | [+4.00, +5.39] | false positive | 4.41% | [2.46, 7.36] |
| `qft_n29` | +4.07% | [+3.36, +4.82] | false positive | 3.04% | [1.74, 5.01] |
| `swap_test_n361` | +5.74% | [+5.20, +6.26] | false positive | 2.59% | [1.32, 4.40] |
| `cc_n32` | −8.28% | [−9.79, −6.77] | false positive | 0.37% | [0.11, 0.83] |

**All 12 are false positives.** Every one is a circuit whose reference change is below the
threshold and which the protocol nonetheless calls a regression at a non-zero rate.

### The 10 BOUNDARY circuits — excluded, and they carry the LARGEST rates

`bv_n30` 39.78%, `bv_n70` 37.40%, `knn_n31` 33.13%, `qugan_n111` 33.07%,
`qugan_n39` 30.53%, `swap_test_n41` 30.27%, `knn_n41` 30.27%, `swap_test_n115` 18.27%,
`qft_n63` 16.44%, `multiplier_n45` 2.87%.

**Including them would roughly double the endpoint. They stay excluded** because the rule
was fixed before the data. This exclusion is conservative and works against the result.

### The 3 UNRESOLVED circuits

`dnn_n33` θ = +9.93% [+8.89, +10.96]; `dnn_n51` +9.73% [+8.67, +10.84];
`qugan_n71` +10.47% [+9.49, +11.46]. No verdict can be called wrong when the reference
itself straddles the threshold.

### Distribution — the number that most limits the claim

Over the 26 eligible circuits: **median error rate 0.0000**, p75 = 6.91%, p90 = 14.17%,
max = 17.31%. Half of the eligible circuits are exactly zero.

> **The endpoint counts circuits with a non-zero rate. It does not claim the typical rate
> is large.** Quoting 46.2% without this sentence misrepresents the result.

### Circuits named in Qiskit issue #14402

Two of the three are in the blind sample, selected by the cost rule:
`bv_n280` 17.31% and `knn_341` 4.68%. The third, `bv_n140`, was measured separately
(post-hoc, 400 seeds across 21 processes): θ = +5.374% [+4.272, +6.495], error 24.4%
[19.5, 31.1]. **`bv_n140` is not part of the pre-registered endpoint.**

---

## 4. Methods, in enough detail to check the arithmetic

- **Reference change θ:** ratio of arm means. 95% percentile bootstrap over seeds,
  resampled **jointly** across the paired arms (both arms share the same seed set), B = 4000.
- **Decision rule, integer-exact.** With arm sums *S<sub>A</sub>*, *S<sub>B</sub>* over *k*
  draws and *t = p/q* in lowest terms, the rule (S<sub>B</sub>−S<sub>A</sub>)/S<sub>A</sub> ≥ p/q
  is evaluated as **q·S<sub>B</sub> ≥ (q+p)·S<sub>A</sub>** — integer arithmetic, no
  floating point. This was a fix: the earlier float form `b ≥ a(1+t)` disagreed with the
  literal rule in 84 of 900 randomised cases. The integer form was verified against
  exact-integer brute force, **900 cases, 0 disagreements**.
- **Error rate:** exact enumeration over all 200³ = 8,000,000 sum-triples per arm for
  k ≤ 3; Monte Carlo with 4,000,000 pairs above that.
- **Error-rate interval:** seed bootstrap, B = 400, each replicate scored by 400,000
  Monte Carlo pairs. MC error per replicate is ~5×10⁻⁴, far below the seed uncertainty.
- **Endpoint interval:** Wilson score.

---

## 5. Follow-up attacks already run (labelled; the frozen result is untouched)

| # | attack | result |
|---|---|---|
| F1 | Does eligibility reproduce from the pre-registered rule? | **Yes.** 39 selected = 39 analysed; 26 eligible; 12 hits. |
| F2 | Exact duplicate circuits inflating the count? | `swap_test_n41` and `knn_n41` are **byte-identical seed-for-seed in both arms**. Both are BOUNDARY, so **the endpoint is unaffected**. No other duplicate pair. |
| F3 | Does family structure inflate 12/26? | Hits span **6 distinct families** (adder, knn, swap_test, qft, bv, cc). Clustering at family level gives **6/11 = 54.5%, Wilson [28.0, 78.7]** — same sign, wider interval, as expected with fewer units. |
| F4 | Are same-family circuits near-duplicates? | **No.** Zero same-family pairs with \|r\| > 0.5 on per-seed ratios (excluding the F2 pair). |
| F5 | Are the two interval methods independent? | **NO — and an earlier draft of §52 wrongly said "independent". They use the same 200 seeds.** They differ in *assumptions* (nonparametric bootstrap vs normal-theory t), not in data. Where both are defined, agreement is **13/13**; the other 13 eligible circuits have zero variance so the t-interval is undefined, not disagreeing. |
| F6 | Is 200 runs enough to call a rate non-zero? | Split-half on every eligible circuit: **max \|half₁ − half₂\| = 0.0618**, median 0.0000, and **0 of 26** circuits flip between zero and non-zero. Adequate for the binary determination the endpoint uses. |

---

## 6. Limitations we already assert — do not credit us for finding these

1. **One SDK** (Qiskit), **one version pair** (1.4.3 → 2.0.0), **one topology**
   (heavy-hex), **one machine**, one OS.
2. **Selection favours fast circuits**, which correlates with small, though 28–420 qubits.
   The slowest third of the corpus is untested.
3. **θ is estimated, not external.** See §1.
4. **The +10% threshold is ours.** Benchpress defines none. Sensitivity was measured on
   `bv_n140` only: error non-zero at every cut from +2% to +25%.
5. **No causal attribution** to any commit or PR, and none attempted.
6. **The 1.4.3 → 2.0.0 change conflates everything** that changed between two major
   releases. We do not claim to isolate a mechanism.
7. **Pairing (`seed_transpiler`) is not a universal fix** — it is worse on 3 of 4 circuits
   with false negatives, though it removes false positives.
8. **Prior withdrawn claims:** a 27.1% headline (interval [1.7%, 63.1%]), a corpus
   proportion that was a direction artifact, a "single commit" attribution that was false
   (31 commits, 64 files), and a calibration column that was an algebraic identity. All
   documented in `DEFECTS.md`. **The study has been wrong repeatedly and says so.**

---

## 7. What we most want attacked

1. **Is the estimand legitimate?** §1 is the load-bearing paragraph. If "disagrees with
   its own long-run mean" is not a defensible notion of a wrong decision, the headline
   must be rewritten as a precision result rather than an error result.
2. **Is 12/26 the right denominator?** 14 of the 26 are deterministic circuits that
   *cannot* err. A reviewer might argue the honest denominator is the 12 circuits with
   any seed variance, making the endpoint 12/12 — or that including 14 guaranteed-zero
   circuits deflates it. Either way the current framing may be wrong.
3. **Does excluding the 10 BOUNDARY circuits bias the result?** It excludes the largest
   effects. It is conservative for the endpoint, but it may mis-describe the phenomenon.
4. **Is the Wilson interval valid** given family-level dependence, given F3?
5. **Is 46.2% a meaningful summary** when the median rate is 0 and the max is 17.3%?
6. **Any reason the whole thing is an artifact** we have not considered.

---

## 8. Round two — results of the attacks by Reviewer B and Reviewer A, 2026-09-04

Six follow-up tests, `followup.py`. The frozen experiment was **not** modified.

| id | attack | outcome |
|---|---|---|
| **C3** | Wilson assumes independent circuits; family structure means it is too narrow | **CONFIRMED — our interval was wrong.** Families are *perfectly separated* (adder 3/3, knn 3/3, cc 2/2, swap_test 2/2, bv 1/1, qft 1/1 all hit; cat 0/3, ghz 0/3, ising 0/4, wstate 0/3, 32 0/1 all miss). Cluster bootstrap over families, B=20,000: **46.2%, 95% CI [17.4%, 81.0%]** vs Wilson [28.8%, 64.5%]. The cluster interval now replaces Wilson. |
| **G2** | 12/26 blends deterministic and stochastic populations | **CONFIRMED, and it sharpens the result.** Exactly 13 eligible circuits have zero per-seed variance (0 hits) and 13 have non-zero variance (12 hits). **Among stochastic circuits: 12/13 = 92.3%, Wilson [66.7%, 98.6%].** Reported alongside 12/26, not instead of it. |
| **G1** | the mean is a strawman; practice may be best-of-k | **REJECTED, and it inverts.** Benchpress performs no aggregation at all (source-verified). Under **min-of-3**, all 8 tested circuits still err and every rate roughly **doubles** (`bv_n280` 0.173 → 0.284). Best-of-k makes the problem worse. |
| **G3** | no formalised threshold, so a false positive is a hallucination | **REJECTED on the numbers**, conceded on wording. Endpoint recomputed at every cut: 5% → 36.4%, 7.5% → 22.2%, 10% → 46.2%, 12.5% → 60.0%, 15% → 60.5%, 20% → 46.2%. Non-zero everywhere, interval excludes zero everywhere. Terminology changed to **finite-sample decision risk relative to the long-run reference**. |
| **G4** | excluding boundary circuits destroys ecological validity | **ANSWERED.** Including them: 22/36 = **61.1%** [44.9, 75.2]. The exclusion costs ~15 points and **stays**, because the rule was fixed before the data. |
| **C2** | θ is a 200-seed plug-in; propagate its uncertainty | **ANSWERED.** Joint bootstrap recomputing θ, verdict, boundary and error each replicate: endpoint median 0.4615, CI [0.4167, 0.5000]. ⚠ This isolates θ-uncertainty **only** and is not a total-uncertainty interval; that is C3's [17.4%, 81.0%]. |
| **C1** | "wrong" overstates the estimand | **ADOPTED** throughout. |

### The claim after round two

> On heavy-hex, comparing Qiskit 1.4.3 with 2.0.0, **12 of 13 pre-registered circuits
> whose compilation is stochastic (92.3%, Wilson [66.7%, 98.6%]) exhibit a finite-sample
> decision risk demonstrably above zero** under the three-run protocol. Over all 26
> eligible circuits the proportion is 46.2% with a family-cluster-robust interval of
> **[17.4%, 81.0%]**. It holds at every threshold from 5% to 20% and roughly doubles under
> best-of-3 aggregation.

### Still open after round two

1. The perfect family separation means the real unit of analysis may be the **algorithm
   family**, not the circuit — 6 of 11 families. With 11 units, no interval will be tight.
2. Whether `cat`/`ghz`/`ising`/`wstate` being deterministic is a property of those
   algorithms or of this topology and qubit range. Untested.
3. One SDK, one version pair, one topology, one machine. Unchanged.
