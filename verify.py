"""One command that runs every check this repository has, and says which passed.
Read-only.

WHAT EXIT 0 IS AND IS NOT
    It is the conjunction of the thirteen stages below, each inside the scope its own
    file header declares. It is NOT a proof that the manuscript is correct, that the
    published PDF says what the source says in the order it says it, or that nothing
    outside these stages' declared domains has moved. Four audits have each ended with
    this command printing PASS on a repository an adversarial reader then broke, and the
    stage headers are where the boundary of each check is written down.

FOR A DELEGATED AGENT (Antigravity IDE, a CI job, a reviewer)
    Run this and report the PASS/FAIL table. Nothing else is needed, and nothing else
    should be done. It writes NO file inside the repository -- every check either reads
    or works in a system temp directory -- so it cannot corrupt the evidence it checks.

    ⛔ DO NOT clone Benchpress. A clone at the pinned commit already exists at
       C:\\Users\\User\\Desktop\\benchpress_test. Point BENCHPRESS_PATH at it. If you
       ever do clone one anywhere, DELETE it when finished -- a stray 786 MB checkout
       is exactly the kind of debris this project does not want.

    ⛔ DO NOT "fix" a failure. A failing check here is a finding, and findings are the
       product. Report the exact output and stop.

WHAT IT CHECKS — and what each stage does NOT establish (Astra V4, 2026-09-13)
    Thirteen stages are not thirteen independent replications. Several share the same raw
    loader, selection list and classification constants, so one defect can travel through
    more than one of them. The scope below is deliberately narrower than v4's first
    wording, which an audit showed was false for four stages.

    1 toolchain pin   Benchpress commit SHA, tracked-file cleanliness, 5 module hashes
                      over CANONICAL bytes. REQUIRES a git checkout: hashes alone cannot
                      say which revision the files came from. Not: dependency behaviour.
    2 test suite      pytest. A test suite, not a certificate for untested artifacts.
    3 inventory       44 recorded numbers vs a fresh recomputation -- 32 recomputed from
                      raw, 12 RE-READ from derived k-sweep CSVs. Not every figure, not
                      every interval, not prose.
    4 replication     144 recorded values (6 circuits x 12 seeds x 2 versions) compared
                      against the reference. An artifact comparison; it does not
                      transpile anything in this invocation.
    5 tautology proof the withdrawn paired column is still provably data-independent.
                      Says nothing about any other estimator.
    6 paper claims    paper_check.py -- 50 selected numeric values recomputed and located
                      in the source text. PRESENCE, not placement: it cannot prove a
                      number is quoted in the right claim. Not "every quantitative claim".

    7 raw endpoint   the primary result rebuilt FROM RAW by a separately implemented risk
                     estimator, bound to PAPER.md. Shares load_seeded, BOUNDARY_PP and
                     TIE_EPS with the producer, so its independence is partial.
    8 raw integrity  the 78 merged arms vs the CURRENT manifest, plus selected summary
                     fields vs a raw reconstruction. Self-consistency: an attacker who
                     updates the manifest too is caught by stage 10, not here.
    9 mutation test  every corruption in `mutation_test.MUTATIONS` -- the count is read
                     from that list and printed in the header at run time, never spelled
                     out here, because a number typed into prose goes stale the next time
                     the suite grows (Astra F-05) -- each REJECTED, not merely exited
                     on, by a named
                     stage under a named INVARIANT, read from that stage's terminal
                     verdict line rather than scraped from its console text. Evidence
                     this verifier turns red; not a proof that no other corruption passes.
   10 v2 anchor      canonical content of the raw evidence vs v2's GIT OBJECTS. Without
                     that history it falls back to a supplied transcript and says so:
                     that mode is agreement, not authenticity.
   11 derived binding every saved field against its declared domain, the row's internal
                     coherence, and a replay of the original analysis. Same analysis code
                     and MC budget as the producer -- a binding, not an independent
                     recomputation.
   12 rendered       the canonical table parsed from the manuscript, vs a reconstruction
                     from raw, for a document inside the declared raw-HTML domain; then
                     every unit of the DECLARED MARKDOWN SURFACE MODEL against the
                     REGISTERED surface in `manuscript_surface.json`. A block nobody
                     registered is refused before any recogniser reads it, so a false
                     sentence does not have to contain a number to be caught. The model
                     is not the rendered page: `visible_surface` names and measures the
                     two places they are known to differ.
   13 published pdf  the PDF's numeric content vs the manuscript's, both directions, the
                     canonical rows in place, the version line, and every WORD of the
                     artifact against the registered surface in both directions. NOT
                     semantic equivalence and NOT word order: a human reading of the
                     built PDF is still required.

THE FOURTH ROUND (2026-09-14, Astra differential against 3643bbc)
    Four of the ten repairs closed; six were partial, and one new build defect appeared.
    The two that mattered:

      the ORIGINAL false-abstract reproducer still passed. `manuscript_binding` excluded
      a prose fraction from the scan when its TEXT matched the canonical table's, and the
      table legitimately contains "7 / 26" — so the identical string anywhere in the
      document was skipped. Identity of a text occurrence is its POSITION; it is now a
      character range.

      a layer could print its expected rejection and then crash, and still be scored as
      a detection. Outcomes are no longer inferred from console text at all: every layer
      ends by emitting a terminal verdict through `validation_result.py`, and anything
      else — a crash before it, a crash after it, output continuing past it — is ERROR,
      which is neither a pass nor a detection.

    Also: a locked destination let the PDF build report success over yesterday's file
    (`publish/finalize_pdf.py`), and a tag longer than 400 characters escaped the
    manuscript's declared HTML domain.

WHY THE WORDING CHANGED — the third failure (2026-09-13, Astra v4)
    Stages 1-13 all passed on two separately controlled corrupt states:

      all 36 saved risk intervals replaced with NaN          -> stage 11 now rejects
      a PDF printing 99.9 where the manuscript says 10.9      -> stage 13 now rejects

    Both were accepted because a comparison was being made against a value outside the
    domain it was declared over, and because token presence was being read as semantic
    agreement. Two further stage-12 states passed: the canonical table inside a hidden
    <div>, and a true numerator attached to the wrong endpoint in the abstract.

    The stages were repaired, and so was this header. Several lines here claimed coverage
    the code did not have -- "every quantitative claim", "every saved primary field", "the
    table a READER sees" -- and an inaccurate description of what a verifier enforces is
    itself a defect, because it is what a reader relies on when the verifier says PASS.

WHY 10-12 EXIST — the second failure (2026-09-13)
    Checks 7-9 were built to prove this verifier could turn red, and they did, for the
    three attacks their author imagined. A hostile auditor then found three more, each
    returning a full 9/9 PASS:

      all 36 saved risk intervals replaced with [0.900000, 0.999999]  -> check 11
      visible results table set to 0/26, correct rows hidden in a comment -> check 12
      one raw observation edited and the local manifest regenerated   -> check 10

    Stage 1 was also bound to CRLF working-tree bytes and would have failed for every
    replicator on an LF checkout: 0 of 5 module hashes match across line-ending policies.
    It now compares canonical bytes from git objects.

WHY 7-9 EXIST — the failure that produced them (2026-09-12)
    A hostile audit corrupted one raw primary arm file, changing the true endpoint from
    12/26 to 11/26 and the >=5% / >=10% counts from 7/26 and 4/26 to 6/26 and 3/26.
    Checks 1-6 reported 6/6 PASS.

    Not a slip: check 6 read `results/summary/prereg_heavy-hex.csv` as the AUTHORITY for
    the primary numbers, and a derived summary cannot notice that the raw data beneath it
    changed. The whole chain sat downstream of a file the attack never touched.

    A verifier that always agrees with its authors is worthless. Check 9 is the evidence
    that this one does not: it corrupts data in throwaway snapshots and REQUIRES the
    relevant stage to fail. If check 9 ever passes trivially, it has stopped being a test.

WHAT CHECK 6 DOES NOT PROVE (added 2026-09-08, and stated here so nobody assumes more)
    paper_check.py recomputes each figure and then asserts the formatted value APPEARS
    in PAPER.md. Presence is not placement: a number can be found in an unrelated
    sentence and the check still passes. The section-bound assertions added alongside
    this stage narrow that for the load-bearing figures, but the weakness is structural,
    not fixed. Check 6 catches drift between the code and the manuscript. It does not
    prove a number is quoted in the right claim.

USAGE
    set BENCHPRESS_PATH, then:
        envs/bp202/Scripts/python.exe verify.py
    Exit code 0 = every one of these checks passed, within the scope each declares.
    Non-zero = the number of failed checks.
"""

import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
PY200 = os.path.join(ROOT, "envs", "bp200", "Scripts", "python.exe")


def run(label, cmd, needs_bp=True):
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=1800)
        ok, out = p.returncode == 0, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:
        ok, out = False, f"{type(exc).__name__}: {exc}"
    return {"label": label, "ok": ok, "seconds": time.perf_counter() - t0,
            "tail": "\n".join(out.strip().splitlines()[-12:])}


def main():
    bp = os.environ.get("BENCHPRESS_PATH")
    # Read, not written down. Astra F-05 found this file claiming 22 corruptions and
    # README claiming eighteen while the suite held 24; a count that lives in prose is
    # wrong from the next commit onwards.
    from mutation_test import MUTATIONS
    print(f"\n  qvalidation — integrity check")
    print(f"  python          {sys.version.split()[0]}  ({PY})")
    print(f"  BENCHPRESS_PATH {bp or 'NOT SET'}")
    print(f"  mutation suite  {len(MUTATIONS)} corruptions (stage 9)")

    if not bp or not os.path.isdir(bp):
        print("\n  FAIL: set BENCHPRESS_PATH to a Benchpress checkout at the pinned "
              "commit.\n        A clone already exists at "
              "C:\\Users\\User\\Desktop\\benchpress_test — use it, do not make "
              "another.\n")
        sys.exit(1)

    checks = [
        run("1 toolchain pin", [PY, "pin_check.py"]),
        run("2 test suite", [PY, "-m", "pytest", "tests/", "-q"]),
        run("3 inventory", [PY, "inventory.py", "--check"]),
        run("4 replication", [PY, "replication/replicate.py", "--stage", "verify",
                              "--old", "replication/out_q200.jsonl",
                              "--new", "replication/out_q202.jsonl"]),
        run("5 tautology proof", [PY, "paired.py", "--prove"]),
        run("6 paper claims", [PY, "paper_check.py"]),
        # 7-9 exist because 1-6 all passed on a snapshot whose raw data had been
        # corrupted badly enough to change the headline result (audit F01). They are
        # ordered so the science is checked first and the byte-level checks support it,
        # never the other way round.
        run("7 raw -> endpoint", [PY, "raw_endpoint.py", "--cross-check"]),
        run("8 raw integrity", [PY, "raw_integrity.py"]),
        run("9 mutation test", [PY, "mutation_test.py"]),
        # 10-12 exist because 7-9 all passed while Astra corrupted the saved intervals,
        # falsified the visible table, and edited raw evidence with a regenerated
        # manifest (audits/2026-09-13-astra-v3/).
        run("10 v2 evidence anchor", [PY, "v2_anchor.py"]),
        run("11 derived binding", [PY, "derived_binding.py"]),
        run("12 rendered manuscript", [PY, "manuscript_binding.py"]),
        run("13 published pdf", [PY, "pdf_binding.py"]),
    ]

    print(f"\n  {'check':<20s} {'result':>7s} {'time':>8s}")
    print("  " + "-" * 38)
    for c in checks:
        print(f"  {c['label']:<20s} {'PASS' if c['ok'] else 'FAIL':>7s} "
              f"{c['seconds']:>7.1f}s")

    failed = [c for c in checks if not c["ok"]]
    for c in failed:
        print(f"\n  ---- {c['label']} output ----\n{c['tail']}")

    if failed:
        print(f"\n  {len(failed)} of {len(checks)} checks FAILED. Report this output "
              f"verbatim. Do not attempt a fix.\n")
    else:
        # NOT "the repository is intact" (independent audit of b5ba725). That sentence
        # was read as a semantic proof, and these thirteen stages do not make one: each
        # holds inside the domain its own file header declares, and stage 13 binds the
        # PDF's word multiset without binding its word order. What passed is what is
        # printed above, and nothing wider.
        print(f"\n  All {len(checks)} checks passed, each within the scope its own file "
              f"header\n  declares. That is what this run establishes and no more; a "
              f"documented human\n  reading of the built PDF against PAPER.md remains a "
              f"release requirement.\n")
    sys.exit(len(failed))


if __name__ == "__main__":
    main()
