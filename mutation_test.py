"""Prove the verifier can turn RED — including on the three attacks that beat v3.

HISTORY, BECAUSE IT IS THE POINT
    v2's verifier was defeated by corrupting raw data. v3 fixed that and added this file
    to prove it. v3 was then defeated three more ways by an auditor who attacked what its
    author had not imagined:

      H  all 36 saved risk intervals -> [0.900000, 0.999999], flags and counts untouched
      K  visible results table -> 0/26, with the correct rows hidden in an HTML comment
      F  one raw observation changed, then the local manifest regenerated

    All three returned 9/9 PASS. They are preserved below verbatim, alongside the earlier
    A-E, and each declares WHICH layer must catch it. A layer passing is acceptable only
    when another catches the same attack; a mutation caught by nothing fails this test.

    The lesson is not that the earlier verifiers were careless. A verifier only tests the
    attacks its author imagined, and the author is the worst-placed person to imagine
    them. This file is the record of what has actually been tried, not a proof of safety.

    v4 was then defeated twice more by the next audit, and P-U below are those cases:

      R  all 36 saved risk intervals -> NaN        13/13 PASS   -> derived (V4-01)
      U  the PDF a reader opens says 99.9 where    13/13 PASS   -> pdf     (V4-02)
         the manuscript says 10.9
      P  correct table inside a hidden <div>       stage 12 = 0 -> rendered (V4-03)
      Q  7/26 attributed to the wrong endpoint     stage 12 = 0 -> rendered (V4-03)
      S  n_seeds = 200.9, k = 3.9                  accepted     -> derived (V4-01)
      T  a duplicated circuit row                  accepted     -> derived (V4-01)

    Three rounds of repair later the prose scan was defeated again, and AC-AH are those
    cases. Every one of them turns on the same thing: the scan decided WHETHER a
    reader-visible number was a claim before deciding whether it was true, and everything
    it did not recognise it skipped in silence.

      AE  "7 out of 26" instead of "7 / 26"     13/13 PASS   -> rendered (F-01)
      AF  the same sentence in the built PDF    13/13 PASS   -> pdf     (F-01)
      AC  an injected row inherits the table's  stage 12 = 0 -> rendered (F-02)
          exemption by sitting inside it
      AG  "13 of 26 … have no spread at all"    stages 6, 7  -> rendered (F-03)
          set to any number                     and 12 green
      AH  the 12/26, 7/26 and 4/26 enumeration  stage 12 = 0 -> rendered (F-03)

A NONZERO EXIT IS NOT A CATCH (Astra V4-07)
    This file used to accept any nonzero return code as proof that a layer caught a
    mutation. It does not distinguish "the checker rejected the artifact" from "the
    checker crashed", so a fixture that broke an import would have been scored as
    successful regression coverage. Every layer prints `✗` when it REJECTS and prints no
    `✗` when it dies, so the two are separated here and only a rejection counts.

    On top of that, every mutation declares the REASON it must be rejected for, and the
    catching layer's output must contain it. A layer that fails for an unrelated reason
    is reported as MISSED, because that is what it is.

SAFETY
    Every mutation runs in a throwaway `git archive` snapshot in the system temp
    directory. Nothing here writes to the repository, and it refuses to run if the
    snapshot path resolves inside it.

USAGE
    python mutation_test.py            # all mutations
    python mutation_test.py --quick    # the three that defeated v3
    python mutation_test.py --only H   # one
"""

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import validation_result as vr                                       # noqa: E402

PY = sys.executable
ARM = "results/raw/prereg/knn_n67_heavy-hex_q200.jsonl"
SUMMARY = "results/summary/prereg_heavy-hex.csv"

LAYERS = {                      # name -> script
    "science":   "raw_endpoint.py",
    "integrity": "raw_integrity.py",
    "anchor":    "v2_anchor.py",
    "derived":   "derived_binding.py",
    "rendered":  "manuscript_binding.py",
    "pdf":       "pdf_binding.py",
}
# `derived` replays the original 400x400,000 Monte-Carlo bootstrap and costs about four
# minutes. Running it for all mutations would take an hour to learn nothing new, so it
# runs where it is REQUIRED to catch the attack, and where it is skipped the table says
# so rather than printing a pass it did not earn. `pdf` is skipped for the same reason:
# it needs the built artifact, which only the PDF mutations disturb.
SLOW = {"derived", "pdf"}
# publish/paper.pdf is the artifact stage 13 validates and is not tracked in git, so a
# `git archive` snapshot does not contain it. Copy it in, or the pdf layer exits nonzero
# because the file is missing -- which is an infrastructure error, not a detection.
UNTRACKED_ARTIFACTS = ["publish/paper.pdf", "publish/paper.html"]


def snapshot(dst):
    tar = subprocess.run(["git", "archive", "HEAD"], cwd=ROOT, capture_output=True)
    if tar.returncode:
        raise SystemExit("git archive failed: " + tar.stderr.decode()[:300])
    p = subprocess.run(["tar", "-x", "-C", dst], input=tar.stdout, capture_output=True)
    if p.returncode:
        raise SystemExit("tar failed: " + p.stderr.decode()[:300])
    for rel in UNTRACKED_ARTIFACTS:
        src = os.path.join(ROOT, rel.replace("/", os.sep))
        if os.path.isfile(src):
            dstf = os.path.join(dst, rel.replace("/", os.sep))
            os.makedirs(os.path.dirname(dstf), exist_ok=True)
            shutil.copy2(src, dstf)


def run(snap, script):
    """(exit code, stdout, stderr) -- kept SEPARATE, see classify."""
    env = dict(os.environ)
    env.setdefault("BENCHPRESS_PATH", r"C:\Users\User\Desktop\benchpress_test")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    parts = script.split()
    p = subprocess.run([PY, *parts], cwd=snap, capture_output=True, text=True,
                       env=env, timeout=3600)
    return p.returncode, (p.stdout or ""), (p.stderr or "")


# REJECTED / PASSED / ERROR. The outcome is READ FROM THE LAYER'S TERMINAL VERDICT, not
# inferred from its console text.
#
# Round one of V4-07 replaced "any nonzero exit" with "nonzero exit and a ✗ somewhere in
# the output". Astra then made a layer print its expected rejection diagnostic and raise
# afterwards: still nonzero, still contained ✗, still scored REJECTED, and the declared
# reason was present. Scraping evidence ABOUT an outcome cannot distinguish a layer that
# finished from one that fell over after printing — and a layer that fell over did not
# finish, so it cannot vouch for anything.
#
# validation_result.classify requires the sentinel to be the LAST line of stdout and no
# traceback on stderr. See validation_result.py.
REJECTED, PASSED, ERROR = vr.REJECTED, vr.PASSED, vr.ERROR


def classify(code, out, err=""):
    return vr.classify(code, out, err)[0]


# ---------------------------------------------------------------- the mutations

def _rows(snap, path):
    return [json.loads(l) for l in open(os.path.join(snap, path), encoding="utf-8")
            if l.strip()]


def _write_rows(snap, path, rows):
    open(os.path.join(snap, path), "w", encoding="utf-8").write(
        "\n".join(json.dumps(r) for r in rows) + "\n")


def mut_A(snap):
    """audit T7: every candidate count in one arm -> 100."""
    rs = _rows(snap, ARM)
    n = 0
    for r in rs:
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] = 100
            n += 1
    _write_rows(snap, ARM, rs)
    return f"{n} candidate counts -> 100"


def mut_B(snap):
    """one raw count +1."""
    rs = _rows(snap, ARM)
    for r in rs:
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] += 1
            break
    _write_rows(snap, ARM, rs)
    return "one raw count +1"


def mut_C(snap):
    """candidate arm x1.09 -- moves the verdict."""
    rs = _rows(snap, ARM)
    n = 0
    for r in rs:
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] = int(round(r["two_q"] * 1.09))
            n += 1
    _write_rows(snap, ARM, rs)
    return f"{n} candidate counts x1.09"


def mut_D(snap):
    """derived summary only: one point risk -> 0.999999."""
    p = os.path.join(snap, SUMMARY)
    lines = open(p, encoding="utf-8").read().splitlines()
    i = lines[0].split(",").index("error_rate")
    row = lines[1].split(",")
    row[i] = "0.999999"
    lines[1] = ",".join(row)
    open(p, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return "one saved point risk -> 0.999999"


def mut_E(snap):
    """visible >=5% literal 7 -> 9."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    t2 = t.replace("| risk ≥ 5% | 7 / 26 |", "| risk ≥ 5% | 9 / 26 |", 1)
    if t2 == t:
        raise SystemExit("E: target row not found")
    open(p, "w", encoding="utf-8").write(t2)
    return "visible >=5% literal 7 -> 9"


def mut_F(snap):
    """ASTRA F: change one raw observation, then regenerate the local manifest."""
    p = "results/raw/prereg/multiplier_n45_heavy-hex_q200.jsonl"
    rs = _rows(snap, p)
    n = 0
    for r in rs:
        if r.get("record") != "env" and r.get("two_q") == 7315 and not n:
            r["two_q"] = 7316
            n = 1
    _write_rows(snap, p, rs)
    subprocess.run([PY, "raw_integrity.py", "--write"], cwd=snap, capture_output=True)
    return "multiplier_n45 7315 -> 7316, local manifest regenerated"


def mut_H(snap):
    """ASTRA H: all saved risk intervals -> [0.900000, 0.999999]."""
    p = os.path.join(snap, SUMMARY)
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    cols = list(rows[0].keys())
    n = 0
    for r in rows:
        if r.get("error_ci_lo") not in ("", None):
            r["error_ci_lo"], r["error_ci_hi"] = "0.900000", "0.999999"
            n += 1
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return f"all {n} saved risk intervals -> [0.900000, 0.999999]"


def mut_K(snap):
    """ASTRA K: visible table falsified, correct rows hidden in an HTML comment."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    real = ("| risk > 0 (pre-registered endpoint) | 12 / 26 | 46.2% | [28.8, 64.5] |\n"
            "| risk ≥ 5% | 7 / 26 | 26.9% | [13.7, 46.1] |\n"
            "| risk ≥ 10% | 4 / 26 | 15.4% | [6.2, 33.5] |")
    fake = ("| risk > 0 (pre-registered endpoint) | 0 / 26 | 0.0% | [0.0, 0.0] |\n"
            "| risk ≥ 5% | 0 / 26 | 0.0% | [0.0, 0.0] |\n"
            "| risk ≥ 10% | 0 / 26 | 0.0% | [0.0, 0.0] |")
    if real not in t:
        raise SystemExit("K: canonical table not found verbatim")
    t = t.replace(real, fake + "\n\n<!--\n" + real + "\n-->", 1)
    open(p, "w", encoding="utf-8").write(t)
    return "visible table -> 0/26; correct rows hidden in an HTML comment"


def mut_L(snap):
    """a SECOND visible endpoint table -- which one is the claim?"""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    dup = ("\n\n| criterion | circuits | proportion | Wilson 95% CI |\n"
           "|---|---:|---:|---|\n"
           "| risk > 0 (pre-registered endpoint) | 3 / 26 | 11.5% | [4.0, 29.0] |\n"
           "| risk ≥ 5% | 2 / 26 | 7.7% | [2.1, 24.1] |\n"
           "| risk ≥ 10% | 1 / 26 | 3.8% | [0.7, 18.9] |\n")
    open(p, "w", encoding="utf-8").write(t + dup)
    return "a second, contradicting visible endpoint table appended"


def mut_M(snap):
    """wrong DENOMINATOR only -- numerators all correct."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    t2 = t.replace("| risk > 0 (pre-registered endpoint) | 12 / 26 |",
                   "| risk > 0 (pre-registered endpoint) | 12 / 39 |", 1)
    if t2 == t:
        raise SystemExit("M: target row not found")
    open(p, "w", encoding="utf-8").write(t2)
    return "denominator 26 -> 39 on the primary row"


def mut_N(snap):
    """attacker also regenerates the obvious derived file."""
    rs = _rows(snap, ARM)
    for r in rs:
        if r.get("record") != "env" and "two_q" in r:
            r["two_q"] += 1
            break
    _write_rows(snap, ARM, rs)
    subprocess.run([PY, "raw_integrity.py", "--write"], cwd=snap, capture_output=True)
    return "one raw count +1, and the manifest regenerated to match"


def _csv_rows(snap):
    p = os.path.join(snap, SUMMARY)
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    return p, rows, list(rows[0].keys())


def _csv_write(p, rows, cols):
    with open(p, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)


def mut_R(snap):
    """ASTRA V4-01: every saved risk interval bound -> NaN. 13/13 PASS against v4."""
    p, rows, cols = _csv_rows(snap)
    n = 0
    for r in rows:
        if r.get("error_ci_lo") not in ("", None):
            r["error_ci_lo"], r["error_ci_hi"] = "NaN", "NaN"
            n += 1
    _csv_write(p, rows, cols)
    return f"all {n} saved risk intervals -> NaN"


def mut_S(snap):
    """ASTRA V4-01: fractional integer metadata, truncated by int(float(...))."""
    p, rows, cols = _csv_rows(snap)
    for r in rows:
        r["n_seeds"], r["k"] = "200.9", "3.9"
    _csv_write(p, rows, cols)
    return "n_seeds -> 200.9 and k -> 3.9 on every row"


def mut_T(snap):
    """ASTRA V4-01: a duplicated circuit row, collapsed by a dict before counting."""
    p, rows, cols = _csv_rows(snap)
    rows.append(dict(rows[0]))
    _csv_write(p, rows, cols)
    return f"circuit {rows[0]['circuit']} duplicated as a 40th row"


def mut_P(snap):
    """ASTRA V4-03: canonical table inside a hidden div, false statement left visible."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    real = ("| risk > 0 (pre-registered endpoint) | 12 / 26 | 46.2% | [28.8, 64.5] |\n"
            "| risk ≥ 5% | 7 / 26 | 26.9% | [13.7, 46.1] |\n"
            "| risk ≥ 10% | 4 / 26 | 15.4% | [6.2, 33.5] |")
    if real not in t:
        raise SystemExit("P: canonical table not found verbatim")
    fake = ("| risk > 0 (pre-registered endpoint) | 0 / 26 | 0.0% | [0.0, 0.0] |\n"
            "| risk ≥ 5% | 0 / 26 | 0.0% | [0.0, 0.0] |\n"
            "| risk ≥ 10% | 0 / 26 | 0.0% | [0.0, 0.0] |")
    t = t.replace(real, fake + '\n\n<div style="display:none">\n\n' + real +
                  "\n\n</div>\n", 1)
    open(p, "w", encoding="utf-8").write(t)
    return "correct table moved into a display:none div, 0/26 left visible"


def mut_Q(snap):
    """ASTRA V4-03: a true numerator attributed to the wrong endpoint in the abstract."""
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    old = "Seven of 26 eligible circuits\ncarry a risk of at least 5%"
    if old not in t:
        raise SystemExit("Q: abstract sentence not found verbatim")
    new = ("Seven of 26 eligible circuits have a risk interval that excludes zero. "
           "Seven of 26 eligible circuits\ncarry a risk of at least 5%")
    open(p, "w", encoding="utf-8").write(t.replace(old, new, 1))
    return "abstract attributes 7/26 to interval exclusion (true of >=5%, not of this)"


class Skip(Exception):
    """This fixture cannot be BUILT here. Not a pass, not a failure — an absence."""


CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]


def _rebuild_pdf(snap, substitute=None):
    """Render the snapshot's PAPER.md to publish/paper.pdf through the tracked path.

    `substitute` is an optional (old, new) pair applied to the rendered HTML before
    Chromium runs, for mutations whose falsehood exists only in the PDF. The text in a
    PDF is stored as hex glyph codes, so there is no literal string in the byte stream to
    patch -- the substitution has to happen upstream of the render, which is why these
    fixtures need the same two tools publish/build_paper.sh needs.
    """
    pandoc = shutil.which("pandoc")
    chrome = next((c for c in CHROME if os.path.isfile(c)), None)
    if not pandoc or not chrome:
        raise Skip("needs pandoc and Chrome to rebuild the PDF")
    html = os.path.join(snap, "publish", "paper.html")
    pdf = os.path.join(snap, "publish", "paper.pdf")
    os.makedirs(os.path.dirname(html), exist_ok=True)
    r = subprocess.run([pandoc, "PAPER.md", "--from=markdown+pipe_tables+raw_html",
                        "--to=html5", "--standalone", "--css=paper_style.css",
                        "--output=publish/paper.html"],
                       cwd=snap, capture_output=True, text=True)
    if r.returncode:
        raise Skip("pandoc failed: " + (r.stderr or "")[:150])
    n = 0
    if substitute:
        old, new = substitute
        t = open(html, encoding="utf-8").read()
        n = t.count(old)
        if not n:
            raise SystemExit(f"no {old!r} in the rendered HTML to substitute")
        open(html, "w", encoding="utf-8").write(t.replace(old, new))
    url = "file:///" + html.replace("\\", "/")
    r = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                        f"--user-data-dir={os.path.join(snap, '_chrome')}",
                        f"--print-to-pdf={pdf}", "--print-to-pdf-no-header",
                        "--no-pdf-header-footer", "--virtual-time-budget=15000", url],
                       cwd=snap, capture_output=True, text=True, timeout=300)
    if not os.path.isfile(pdf) or os.path.getsize(pdf) < 10000:
        raise Skip("Chromium produced no PDF: " + (r.stderr or "")[:150])
    return n


def mut_U(snap):
    """ASTRA V4-02: the PDF a reader opens says 99.9 where the manuscript says 10.9."""
    n = _rebuild_pdf(snap, substitute=("10.9", "99.9"))
    return (f"{n} occurrence(s) of 10.9 -> 99.9 in the rendered HTML, then rebuilt "
            f"through publish/build_paper.sh's own pandoc + Chromium path. PAPER.md "
            f"and the raw data are untouched")


def mut_V(snap):
    """An interval that is INTERNALLY VALID but not the one the analysis produces.

    D, H and R are all now stopped by the schema and self-consistency contracts before
    the replay runs, which is stricter but leaves the replay itself unexercised. This
    mutation is the one that only the replay can catch: the bound stays finite, stays in
    [0, 1], stays above the point estimate and leaves every flag correct, so nothing about
    the row is self-contradictory. It is simply not what 400 x 400,000 resamples give.
    """
    p, rows, cols = _csv_rows(snap)
    for r in rows:
        if r.get("error_ci_hi") not in ("", None) and float(r["error_ci_hi"]) < 0.98:
            r["error_ci_hi"] = f"{float(r['error_ci_hi']) + 0.01:.6f}"
            target = r["circuit"]
            break
    else:
        raise SystemExit("V: no row with headroom to widen")
    _csv_write(p, rows, cols)
    return f"{target} error_ci_hi widened by 0.01 — valid interval, wrong interval"


def mut_Y(snap):
    """A required cell left blank. This used to CRASH the checker with a TypeError,
    which says nothing a reader can act on and is not a detection."""
    p, rows, cols = _csv_rows(snap)
    rows[0]["n_seeds"] = ""
    _csv_write(p, rows, cols)
    return f"{rows[0]['circuit']}.n_seeds blanked — a required field with no value"


def mut_Z(snap):
    """ASTRA, 3643bbc differential: one surplus cell, belonging to no column.

    csv.DictReader files the overflow under the None key, where no field-by-field check
    ever looks at it. The row is malformed and every declared column still validates.
    """
    p = os.path.join(snap, SUMMARY)
    lines = open(p, encoding="utf-8").read().splitlines()
    lines[1] = lines[1] + ",9999"
    open(p, "w", encoding="utf-8", newline="").write("\n".join(lines) + "\n")
    return "a 20th cell appended to a 19-column row, under no column name"


def mut_W(snap):
    """ASTRA, 3643bbc differential: the ORIGINAL false-abstract reproducer, verbatim.

    Q used the word-number form ("Seven of 26"), which the repaired scan caught -- and
    that masked the fact that the numeral form Astra actually ran still passed. The
    canonical table legitimately contains "7 / 26", and the prose scan skipped any
    occurrence whose TEXT matched the table's, wherever in the document it was. So the
    fixture is preserved in Astra's own words, not in a paraphrase that happens to work.
    """
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    if "## Abstract" not in t:
        raise SystemExit("W: abstract heading not found")
    sentence = ("The primary risk interval excludes zero in only 7 / 26 eligible "
                "circuits.")
    open(p, "w", encoding="utf-8").write(
        t.replace("## Abstract", "## Abstract\n\n" + sentence, 1))
    return ("abstract asserts 7 / 26 for interval exclusion, in numerals, where the "
            "canonical table carries the identical string")


def mut_AA(snap):
    """ASTRA, post-4d50a2b: the false attribution with a harmless-looking prose prefix.

    W is the same false claim without the prefix. Both are kept, because the pair is the
    finding: the checker rejected W and passed this, which means detection depended on
    the sentence's opening words rather than on what it asserts. "The audit finds that"
    put the word `audit` — one of nine on a counterfactual keyword blacklist — inside the
    attacker's own sentence, and bought a complete exemption from claim checking.
    """
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    if "## Abstract" not in t:
        raise SystemExit("AA: abstract heading not found")
    sentence = ("The audit finds that the primary risk interval excludes zero in only "
                "7 / 26 eligible circuits.")
    open(p, "w", encoding="utf-8").write(
        t.replace("## Abstract", "## Abstract\n\n" + sentence, 1))
    return ("abstract asserts 7 / 26 for interval exclusion behind the prefix "
            "\"The audit finds that\", which used to buy a blanket exemption")


def mut_AB(snap):
    """The same false attribution, checked in the REBUILT PDF rather than the source.

    Equal numeric content cannot see this: the false sentence reuses numbers the
    manuscript already carries, so both sides hold the same token set and the canonical
    rows are intact. The PDF is what a reviewer opens, so the claim has to be read there.
    """
    mut_AA(snap)
    _rebuild_pdf(snap)
    return ("abstract asserts 7 / 26 for interval exclusion, then rendered through "
            "publish/build_paper.sh's own pandoc + Chromium path — the falsehood is "
            "in the PDF a reviewer opens, not only in the source")


def _paper(snap, old, new, who):
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    if old not in t:
        raise SystemExit(f"{who}: target text not found verbatim: {old[:60]!r}")
    open(p, "w", encoding="utf-8").write(t.replace(old, new, 1))


LAST_CANONICAL_ROW = "| risk ≥ 10% | 4 / 26 | 15.4% | [6.2, 33.5] |"


def mut_AC(snap):
    """ASTRA F-02, post-2842dc37: an injected table row, verbatim.

    The exemption for the canonical table was the table's whole character range,
    `vis[tbl_range[0]:tbl_range[1]]` — a range that GROWS with whatever is appended to
    the table. So a row the checker could not name inherited the exemption of the rows it
    could, and a false endpoint claim passed stage 12 by being physically inside a table.
    Only rows whose identity this file recognises are exempt now; anything else in the
    table is prose between pipes and is read as prose.
    """
    _paper(snap, LAST_CANONICAL_ROW, LAST_CANONICAL_ROW + "\n"
           + "| Summary | the primary interval excludes zero in only 7 / 26 eligible "
             "circuits | | |", "AC")
    return ("an unrecognised 'Summary' row inside the canonical table asserts 7 / 26 "
            "for interval exclusion — Astra's injected row, verbatim")


def mut_AD(snap):
    """The same class, a different row: the repair must not be specific to Astra's text.

    Different label, different numerator, a spelled-out number, a different predicate
    spelling. If AC were closed by anything narrower than "an unknown row is not exempt",
    this one would still pass.
    """
    _paper(snap, LAST_CANONICAL_ROW, LAST_CANONICAL_ROW + "\n"
           + "| Aside | nine of 26 eligible circuits reach the pre-registered endpoint "
             "| | |", "AD")
    return ("a second unrecognised row, differently worded, asserts nine of 26 for the "
            "pre-registered endpoint")


def mut_AE(snap):
    """ASTRA F-01, post-2842dc37: the end-to-end reproducer, verbatim.

    "7 out of 26" rather than "7 / 26". The scan's quantity pattern spelled its own
    separator — `\\s*(?:/|of)\\s*` — so this was not a quantity at all and no claim was
    ever attributed. Every stage passed and the sentence printed on page 1 of the PDF.
    Numerator and denominator are found independently now and paired by nearness, so the
    separator, in any spelling, is not part of the decision.
    """
    _paper(snap, "## Abstract", "## Abstract\n\n"
           "The audit finds that the primary risk interval excludes zero in only 7 out "
           "of 26 eligible circuits.", "AE")
    return ("abstract asserts 7 out of 26 for interval exclusion — a separator the "
            "quantity pattern did not spell, so nothing saw a quantity at all")


def mut_AF(snap):
    """That reproducer in the PDF a reviewer opens, through the real build path."""
    mut_AE(snap)
    _rebuild_pdf(snap)
    return ("the 7-out-of-26 false attribution rendered through publish/build_paper.sh's "
            "own pandoc + Chromium path")


def mut_AG(snap):
    """ASTRA F-03: a current claim over the eligible denominator that nothing checked.

    §4.1 states how many eligible circuits compile deterministically. Astra changed 13 to
    7 and stages 6, 7 and 12 stayed green: the number named a predicate the checker had
    no identity for, so it was skipped in silence. The count is reconstructed from raw
    now — both arms constant across every seed — and the claim is bound to it.
    """
    _paper(snap, "13 of 26 eligible circuits have no spread at all",
           "7 of 26 eligible circuits have no spread at all", "AG")
    return "the deterministic-compilation count 13 of 26 -> 7 of 26 in §4.1"


def mut_AH(snap):
    """ASTRA F-03: the endpoint enumeration, which named no predicate at all.

    "the 12/26, 7/26 and 4/26 counts" is the endpoint written as an ordered triple. No
    sentence around it names an endpoint, so under a scan that bound quantities to nearby
    claim phrases all three were unchecked. Three adjacent quantities are one assertion
    and are compared as one.
    """
    _paper(snap, "the 12/26,\n   7/26 and 4/26 counts",
           "the 11/26,\n   7/26 and 4/26 counts", "AH")
    return "the endpoint enumeration in §6.1 reads 11/26, 7/26 and 4/26"


def mut_X(snap):
    """A tag longer than the scanner's old 400-character bound.

    The domain check used `[^<>]{0,400}`, so a sufficiently verbose attribute list was
    not a tag at all and passed unexamined. A limit on how much an attacker may type is
    not a domain, it is a budget.
    """
    p = os.path.join(snap, "PAPER.md")
    t = open(p, encoding="utf-8").read()
    padding = " ".join(f'data-x{i}="{"y" * 12}"' for i in range(60))   # ~1,200 chars
    if "## Abstract" not in t:
        raise SystemExit("X: abstract heading not found")
    open(p, "w", encoding="utf-8").write(
        t.replace("## Abstract",
                  f'<div style="display:none" {padding}>\n\n## Abstract', 1))
    return f"a {len(padding) + 40}-character opening tag, past the old 400-char bound"


MUTATIONS = [
    # id  label   fn   layer -> (INVARIANT the layer must reject under, message fragment)
    #
    # TWO declarations, because they answer different questions (Astra V4-07, 3643bbc).
    # The INVARIANT comes from the layer's terminal verdict line and is structural: it is
    # emitted only by validation_result.reject(), only after the routine ran to
    # completion, so it cannot be produced by a crash. The FRAGMENT is quoted from the
    # human-readable message and pins down WHICH defect within that invariant was seen,
    # so a layer that starts rejecting for an unrelated reason stops counting as coverage.
    ("A", "whole raw arm -> constant", mut_A,
     {"science": ("ENDPOINT_MATCHES_RAW", "raw data gives"),
      "integrity": ("RAW_SELF_CONSISTENT", "RAW EVIDENCE WAS EDITED"),
      "anchor": ("EVIDENCE_MATCHES_", "ANCHOR VIOLATED")}),
    ("B", "one raw count +1", mut_B,
     {"integrity": ("RAW_SELF_CONSISTENT", "RAW EVIDENCE WAS EDITED"),
      "anchor": ("EVIDENCE_MATCHES_", "ANCHOR VIOLATED")}),
    ("C", "raw x1.09, verdict moves", mut_C,
     {"science": ("ENDPOINT_MATCHES_RAW", "raw data gives"),
      "integrity": ("RAW_SELF_CONSISTENT", "RAW EVIDENCE WAS EDITED"),
      "anchor": ("EVIDENCE_MATCHES_", "ANCHOR VIOLATED")}),
    ("D", "derived summary point risk", mut_D,
     {"derived": ("SAVED_SCHEMA", "lies outside its own interval")}),
    ("E", "visible literal 7 -> 9", mut_E,
     {"science": ("ENDPOINT_MATCHES_RAW", "PAPER.md says 9"),
      "rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "numerator 9")}),
    ("F", "ASTRA: raw + manifest regenerated", mut_F,
     {"anchor": ("EVIDENCE_MATCHES_", "ANCHOR VIOLATED")}),
    ("H", "ASTRA: all saved intervals faked", mut_H,
     {"derived": ("SAVED_SCHEMA", "lies outside its own interval")}),
    ("K", "ASTRA: false visible table, correct rows hidden", mut_K,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "numerator 0")}),
    ("L", "second contradicting visible table", mut_L,
     {"rendered": ("CANONICAL_TABLE_UNIQUE", "visible tables carry the primary")}),
    ("M", "wrong denominator only", mut_M,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "denominator 39")}),
    ("N", "raw + manifest regenerated together", mut_N,
     {"anchor": ("EVIDENCE_MATCHES_", "ANCHOR VIOLATED")}),
    ("P", "ASTRA: canonical table inside a hidden div", mut_P,
     {"rendered": ("MANUSCRIPT_HTML_DOMAIN", "outside the declared domain")}),
    ("Q", "ASTRA: 7 of 26 attributed to the wrong endpoint", mut_Q,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "attributes 7 of 26")}),
    ("R", "ASTRA: all saved intervals -> NaN", mut_R,
     {"derived": ("SAVED_SCHEMA", "is not finite")}),
    ("S", "ASTRA: fractional n_seeds and k", mut_S,
     {"derived": ("SAVED_SCHEMA", "not an integer literal")}),
    ("T", "ASTRA: a duplicated circuit row", mut_T,
     {"derived": ("SAVED_SCHEMA", "already appears")}),
    ("U", "ASTRA: PDF says 99.9 where the source says 10.9", mut_U,
     {"pdf": ("PDF_MATCHES_MANUSCRIPT", "appears NOWHERE in PAPER.md")}),
    ("V", "a valid interval that the replay does not produce", mut_V,
     {"derived": ("SAVED_MATCHES_REPLAY", "error_ci_hi")}),
    ("W", "ASTRA: 7 / 26 attributed to the wrong endpoint, in numerals", mut_W,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "attributes 7 of 26")}),
    ("X", "ASTRA: a tag longer than the old 400-char scan bound", mut_X,
     {"rendered": ("MANUSCRIPT_HTML_DOMAIN", "outside the declared domain")}),
    ("Y", "a required cell left blank", mut_Y,
     {"derived": ("SAVED_SCHEMA", "required field is empty")}),
    ("Z", "ASTRA: an extra unlabelled CSV cell", mut_Z,
     {"derived": ("SAVED_SCHEMA", "belongs to no column")}),
    ("AA", "ASTRA: false attribution behind a prose prefix", mut_AA,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "attributes 7 of 26")}),
    ("AB", "ASTRA: that false attribution in the rebuilt PDF", mut_AB,
     {"pdf": ("PDF_MATCHES_MANUSCRIPT", "attributes 7 of 26")}),
    ("AC", "ASTRA: an injected row inherits the table's exemption", mut_AC,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "attributes 7 of 26")}),
    ("AD", "a second unknown row, differently worded", mut_AD,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "attributes 9 of 26")}),
    ("AE", "ASTRA: 7 out of 26 — a separator the pattern did not spell", mut_AE,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "attributes 7 of 26")}),
    ("AF", "ASTRA: that separator attack in the rebuilt PDF", mut_AF,
     {"pdf": ("PDF_MATCHES_MANUSCRIPT", "attributes 7 of 26")}),
    ("AG", "ASTRA: the unchecked deterministic-compilation count", mut_AG,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "no seed-to-seed spread")}),
    ("AH", "ASTRA: the unchecked endpoint enumeration", mut_AH,
     {"rendered": ("VISIBLE_CLAIMS_MATCH_RAW", "enumerates the endpoint as")}),
]
DEFEATED_V3 = {"F", "H", "K"}
DEFEATED_V4 = {"P", "Q", "R", "S", "T", "U"}
DEFEATED_V5 = {"W", "X", "Y", "Z"}
DEFEATED_V6 = {"AA", "AB"}
DEFEATED_V7 = {"AC", "AE", "AF", "AG", "AH"}   # Astra, post-2842dc37 (AD is the pair)

# WHAT EACH PRESERVED FIXTURE MUST STILL PUT IN THE MANUSCRIPT, id -> (layer, text).
#
# Astra F-06: the old guard asserted that these ids appeared in `MUTATIONS`, and then
# looped over DEFEATED_V3 | V4 | V5 — which does not contain AA or AB. Deleting both from
# the suite left every test green. A guard that checks a name against a list it forgot to
# include is not a guard, so this one declares the HOSTILE CONTENT itself: the test runs
# each fixture against a copy of the manuscript and requires the text below to be what
# lands in it. A fixture that is renamed, unregistered, or quietly softened into a
# paraphrase fails, and so does one that no longer reaches the layer named here.
ASTRA_FIXTURES = {
    "W": ("rendered", "The primary risk interval excludes zero in only 7 / 26 eligible "
                      "circuits."),
    "AA": ("rendered", "The audit finds that the primary risk interval excludes zero in "
                       "only 7 / 26 eligible circuits."),
    "AB": ("pdf", "The audit finds that the primary risk interval excludes zero in only "
                  "7 / 26 eligible circuits."),
    "AC": ("rendered", "| Summary | the primary interval excludes zero in only 7 / 26 "
                       "eligible circuits | | |"),
    "AD": ("rendered", "| Aside | nine of 26 eligible circuits reach the pre-registered "
                       "endpoint | | |"),
    "AE": ("rendered", "The audit finds that the primary risk interval excludes zero in "
                       "only 7 out of 26 eligible circuits."),
    "AF": ("pdf", "The audit finds that the primary risk interval excludes zero in only "
                  "7 out of 26 eligible circuits."),
    "AG": ("rendered", "7 of 26 eligible circuits have no spread at all"),
    "AH": ("rendered", "the 11/26,\n   7/26 and 4/26 counts"),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="only F, H, K")
    ap.add_argument("--only", help="a single mutation id")
    args = ap.parse_args()

    muts = MUTATIONS
    if args.only:
        muts = [m for m in MUTATIONS if m[0] == args.only.upper()]
    elif args.quick:
        muts = [m for m in MUTATIONS if m[0] in DEFEATED_V3]

    base = tempfile.mkdtemp(prefix="qval-mutation-")
    if os.path.realpath(base).startswith(os.path.realpath(ROOT)):
        raise SystemExit("refusing: temp path is inside the repository")

    results, failures, skipped = [], [], []
    order = ["science", "integrity", "anchor", "derived", "rendered", "pdf"]
    try:
        print(f"\n  scratch: {base}")
        print("  the repository is never written to by this script\n")

        snap = os.path.join(base, "pristine")
        os.makedirs(snap)
        snapshot(snap)
        ctrl = {n: vr.classify(*run(snap, LAYERS[n]))[0] for n in order}
        print("  CONTROL  " + "  ".join(f"{n}={s}" for n, s in ctrl.items()))
        for n, s in ctrl.items():
            if s != PASSED:
                failures.append(f"control: a pristine snapshot did not pass {n} ({s})")

        print(f"\n  {'id':<4}{'mutation':<44}" + "".join(f"{n:<11}" for n in order))
        for mid, label, fn, reasons in muts:
            must = set(reasons)
            snap = os.path.join(base, f"m{mid}")
            os.makedirs(snap)
            snapshot(snap)
            try:
                what = fn(snap)
            except Skip as exc:
                skipped.append(f"{mid} ({label}): {exc}")
                print(f"  {mid:<4}{(label + ' — SKIPPED')[:42]:<44}"
                      f"fixture could not be built here")
                continue
            state, outs, got_inv = {}, {}, {}
            for n in order:
                if n in SLOW and n not in must:
                    state[n] = None          # not run; see SLOW
                else:
                    code, out, err = run(snap, LAYERS[n])
                    state[n], got_inv[n] = vr.classify(code, out, err)
                    outs[n] = out
            caught = {n for n, s in state.items() if s == REJECTED}
            errored = {n for n, s in state.items() if s == ERROR}
            star = (" *" if mid in DEFEATED_V3 else " †" if mid in DEFEATED_V4 else
                    " ‡" if mid in DEFEATED_V5 else
                    " §" if mid in DEFEATED_V6 else
                    " ¶" if mid in DEFEATED_V7 else "")
            cell = {None: "—", PASSED: "pass", REJECTED: "REJECT", ERROR: "error"}
            print(f"  {mid:<4}{(label + star)[:42]:<44}" +
                  "".join(f"{cell[state[n]]:<11}" for n in order))

            # BOTH declarations, not just the exit code (V4-07, twice over). The invariant
            # is structural and comes from the terminal verdict; the fragment says which
            # defect under that invariant was actually seen.
            why = {}
            for n in must & caught:
                want_inv, frag = reasons[n]
                why[n] = got_inv.get(n, "").startswith(want_inv) and frag in outs.get(n, "")
            results.append({"id": mid, "mutation": what, "required": sorted(must),
                            "caught_by": sorted(caught), "reasons": reasons,
                            "invariants": got_inv,
                            "reason_seen": sorted(n for n, ok in why.items() if ok)})
            for n in sorted(must - caught):
                failures.append(
                    f"{mid}: {n} did not REJECT it — "
                    f"{'it errored out (' + got_inv.get(n, '') + '), which is not a detection' if n in errored else 'it passed'}")
            for n in sorted(must & caught):
                if not why[n]:
                    want_inv, frag = reasons[n]
                    failures.append(
                        f"{mid}: {n} rejected it, but not as declared — expected "
                        f"invariant {want_inv!r} and {frag!r}; got invariant "
                        f"{got_inv.get(n, '')!r}")
            if errored - must:
                failures.append(f"{mid}: {', '.join(sorted(errored - must))} errored; a "
                                f"fixture must not break a layer it does not target")
            if not caught:
                failures.append(f"{mid}: caught by NOTHING — this corruption would ship")
        print("\n  * defeated v3 (9/9 PASS)   † defeated v4 (Astra 2026-09-13)   "
              "‡ defeated the v4 repairs (Astra differential, 3643bbc)\n"
              "  § defeated the differential repairs (Astra, post-4d50a2b)   "
              "¶ defeated the claim scan (Astra, post-2842dc37)\n")
        for r in results:
            print(f"    {r['id']}: {r['mutation']}")
            for n in sorted(r["reasons"]):
                mark = "✓" if n in r["reason_seen"] else "✗"
                inv, frag = r["reasons"][n]
                print(f"        {mark} {n}: {r['invariants'].get(n, '—')} — {frag!r}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print()
    if skipped:
        # Named, never silent. A mutation that did not run is a hole in the coverage this
        # file claims, and a reader of the output is entitled to see which one.
        print(f"  ⚠ {len(skipped)} mutation(s) NOT EXERCISED on this machine — the "
              f"coverage below\n    excludes them:")
        for s in skipped:
            print(f"      {s}")
        print()
    if failures:
        print("  ✗ MUTATION TEST FAILED:")
        for f in failures:
            print(f"      {f}")
        sys.exit(1)
    print(f"  ✓ {len(results)} of {len(muts)} mutations REJECTED — not merely exited "
          f"on — by the\n    layer that must catch each, for the reason it declares, "
          f"and the pristine\n    snapshot stays green.\n")


if __name__ == "__main__":
    main()
