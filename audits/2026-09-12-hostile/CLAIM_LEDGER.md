# Claim ledger — frozen before defect-ledger inspection

Snapshot: 17e08f3e92533ff8266b1b586e35f20da2923da8. All locations below are PAPER.md line ranges at that snapshot. This ledger was constructed in session memory before reading SETTLED.json or prior reviews; it is exported here unchanged. 'Pending' describes evidence status when the ledger was constructed, not the final audit status.

| File:line | Proposition | Type | Evidence required | Evidence available at ledger creation |
|---|---|---|---|---|
| PAPER.md:12-16,66-71,94-113 | Pinned Qiskit unseeded; BQSKit seeded; no aggregation | source | Pinned source and complete parameter/config flow | Paper only; source pending |
| PAPER.md:17-19,134-151 | Risk compares independent k-arm means to ratio-of-expectations verdict | mathematical | defined sampling law, positive denominators | Definition explicit; seed law unspecified |
| PAPER.md:21-28,177-206 | 39 circuits, 200 independent seeds/arm, 10 processes,143→200 heavyhex; preregistered | procedural/empirical | raw record counts, seeds, configs and premeasurement history | Commit exists; raw and history pending |
| PAPER.md:24-27,254-278 | 13 eligible deterministic;23 stochastic resolved;rho -.833 p<.001 | quantitative | raw constancy, exclusions, ranks | Unverified |
| PAPER.md:29-31,306-326,444-445 | 10.9pp median ambiguity width independent of version pair; unresolvable | quantitative/mathematical | raw residual calculation, model and interpretation | Explicit contradiction at310-326; median population differs |
| PAPER.md:33-36,336-356 | Issue figures reproduced;46.1 compatible with own 3run protocol | empirical/causal | matched topology,versions,basis,circuit,aggregation,seeds and source issue | Paper admits unknown aggregation123-124; raw pending |
| PAPER.md:38-40,265-271,419-420 | Mechanistically explained but no compiler mechanism; decision-rule induced correlation | causal/mathematical | theorem or mechanistic experiment | Contradictory wording; no proof |
| PAPER.md:58-64,431-438,459-492 | Reusable generic apparatus;41 figures29raw12derived;complete fresh verification | reproducibility | inventory coverage and verifier mutation tests | Explicit partial-derived caveat; tooling pending |
| PAPER.md:155-173 | Exact rational rule;84/900 float discrepancies;0 integer failures;WR difference≤.0011 | mathematical/quantitative | first principles and raw/code independent enumeration | Cross multiplication valid for positive baseline; others pending |
| PAPER.md:177-191,467-469 | Prereg precedes any measurements;cost-only selection;runtime independent oftheta/risk | procedural/statistical | history, census chronology, frozen rule; independence evidence | Claim stronger than selection procedure; pending |
| PAPER.md:193-198 | Pairedtheta bootstrap4000,risk bootstrap400;resolved/nonboundary endpointCIexcludes0 | statistical/procedural | bootstrap code and resampling reimplementation | Unverified |
| PAPER.md:202-217 | 58 hashes;15600transpiles;backend/basis/observable identities;0/24 backend probes | empirical/source | raw counts provenance and controls | Unverified |
| PAPER.md:218-219 | Seeds independent from lag1-.22to.11 and spread comparison | statistical | seed generation and independence diagnostics | Lag1 alone insufficient |
| PAPER.md:136-138,220-246 | Seed determinism bitidentical;144artifact,216crossmachine;prereg before outputs | empirical/procedural | paired raw artifacts, full circuit equality if claimed, history | Paper explicitly mentions gatecounts; pending |
| PAPER.md:247-248 | No variance selection bias;medians .1126/.1234,p=.768 | statistical | census calculation and valid inference | Null test cannot establish independence |
| PAPER.md:265-271 | Risk universally decreases with absolute threshold distance;syntheticmean-.661,5/30 | mathematical/quantitative | theorem, counterexample, synthetic generator reproduction | Candidate counterexample pending |
| PAPER.md:282-302 | 12/26,7/26,4/26;Wilson intervals;familyCI;quantiles;five circuitpoint/intervals | quantitative/statistical | raw end-to-end independent estimates | Unverified |
| PAPER.md:310-321 | Multiplicative10.86 additive10.73;29/39betteradditive;1/23wider;p7514.8max25.2 | quantitative/model | raw residuals, fitting criterion, bisection convergence | Unverified |
| PAPER.md:329-332,416 | cc_n32 theta-8.28,CI[-9.13,-6.05];6/1728=.37%;band24.5;single49.5 | quantitative | exact source samples and counts | 6/1728 arithmetic already not .37% exactly |
| PAPER.md:338-340,352-356 | 400seedbv140HHtheta5.374risk24.4;200seedlinear31.0;range and percentile | quantitative | raw pooled samples and independent distributions | Unverified |
| PAPER.md:342-344 | Circuit-selective mismatch excludes Benchpress version difference | causal | controlled benchmark version comparison | Logic invalid absent such experiment |
| PAPER.md:360-384 | threshold endpoints,k sweep,MCerror,40hours,min3eight,scatter replication | quantitative | raw recomputation and resource arithmetic | Unverified |
| PAPER.md:375-376,417-418,448-455 | Fix seed removes sampling variance;pairing removesFP,worsens3/4FN | mathematical/empirical | conditional versus marginal estimand and randomness controls | Global determinism not established by finite probes |
| PAPER.md:288-291,390-415 | Descriptive sample only;11families;boundary included22/36;oneSDK limitation | statistical | family labels, raw eligibility and scope | Caveats explicit; numbers pending |
| PAPER.md:424-429,477-479 | Prior audit zeroinvalidating,6defects no numerical changes | procedural | reviews and beforeafter numerical verification | Deferred until ledger completed |

