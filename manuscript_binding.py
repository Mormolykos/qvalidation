"""What the READER sees, bound to what the data says.

WHY (Astra A02)
    v3 checked the manuscript with substring search. Astra set the visible results table
    to 0/26, 0/26, 0/26 and hid the correct rows in an HTML comment. Every string the
    checker looked for was present, so the full verifier returned **9/9 PASS** while the
    published primary claim read zero.

    Substring search asks "does this text exist somewhere in the file". A reader asks
    "what does the table say". Those are different questions, and only the second one is
    the claim. Presence is not placement -- a weakness this project has now been bitten by
    three times, and patched twice; this file replaces the approach instead.

WHAT THIS FILE CAN AND CANNOT SEE (Astra V4-03)
    Astra put the correct table inside a `<div style="display:none">`, printed a false
    0-of-26 statement beside it, and this stage returned 0. It also added an abstract
    sentence attributing 7/26 to interval exclusion — a numerator that is correct for a
    DIFFERENT endpoint — and the prose scan exempted it.

    The first defect is not "CSS was not handled". It is that this file reads Markdown
    source and described its result as what a reader sees, and no amount of source
    reading decides the visibility of arbitrary HTML. Enumerating `display:none`,
    `visibility:hidden`, `font-size:0`, `hidden`, `aria-hidden`, white-on-white … is the
    losing side of that game. So the DOMAIN is declared instead (`METHODOLOGY.md` R19):

        PAPER.md is Markdown whose only raw HTML is an inline formatting tag drawn from a
        closed list, carrying no attributes. Anything else is REJECTED, not interpreted.

    A document outside that domain is not judged unsafe; it is judged unvalidatable by
    this file, which says so and exits nonzero. That is a claim this file can keep.

    The second defect is that a fraction was checked against the SET of true numerators
    instead of against the endpoint its own sentence names. 7/26 is true of "risk ≥ 5%"
    and false of "excludes zero", and only the sentence says which one is meant.

WHAT THIS DOES
    1. Blanks fenced code blocks, then deletes HTML comments. Neither is a rendered claim.
    2. Requires every remaining raw HTML tag to be in the declared closed list.
    3. Parses GitHub-flavoured Markdown tables structurally -- header, alignment row, body
       -- rather than matching text.
    4. Requires EXACTLY ONE table carrying the primary endpoint rows. Two tables is an
       ambiguity, not a convenience: a second one lets an attacker leave a correct table
       somewhere while the read table lies. Zero is a missing claim.
    5. Parses "12 / 26" into numerator AND denominator and checks both.
    6. Compares them to a reconstruction from RAW, not to a stored expectation.
    7. Binds every prose quantity over the eligible denominator to the endpoint its own
       sentence names, so a true numerator cannot be attached to a false claim.

USAGE
    python manuscript_binding.py
    python manuscript_binding.py --show    # print the table as parsed
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


import validation_result as vr
PAPER = os.path.join(ROOT, "PAPER.md")
SELECTED = os.path.join(ROOT, "_selected.txt")

# the three canonical rows, by the label a reader reads
ROWS = {"risk > 0": "excl", "risk ≥ 5%": "ge5", "risk ≥ 10%": "ge10"}

# Phrases that NAME an endpoint in prose. A quantity is bound to the nearest one of these.
# They are the words the manuscript actually uses for each claim; a sentence using none of
# them is not making one of these three claims and is not checked against them.
CLAIM_PHRASES = {
    "excl": ("excludes zero", "exclude zero", "excluding zero", "excluded zero",
             "risk > 0", "pre-registered endpoint", "pre-registered 12"),
    "ge5":  ("at least 5%", "≥ 5%", "≥5%", ">= 5%", "of at least 5", "5% or more"),
    "ge10": ("at least 10%", "≥ 10%", "≥10%", ">= 10%", "of at least 10", "10% or more"),
}
CLAIM_WINDOW = 160        # characters; a claim named further away than this is not "near"

COMMENT = re.compile(r"<!--.*?-->", re.S)
FENCE = re.compile(r"^[ \t]*(```+|~~~+).*?^[ \t]*\1[ \t]*$", re.S | re.M)
FRACTION = re.compile(r"(\d+)\s*/\s*(\d+)")

# --- the declared raw-HTML domain -------------------------------------------------
# `<` immediately followed by a letter (optionally `/` or `!` first), no `<` or `>` inside.
# The immediacy matters: prose writes "p < 0.001, n = 23)" and the naive `<[^>]+>` reads
# everything up to the next `>` anywhere in the document as a tag.
# NO LENGTH BOUND (Astra, 3643bbc differential). This was `[^<>]{0,400}`, so a tag longer
# than 400 characters matched nothing and passed the domain check. A limit on how much an
# attacker may type is not a domain, it is a budget. `[^<>]*` is unbounded and still
# cannot run past the next angle bracket, so the scan stays linear. re.S so a tag broken
# across lines is one tag.
TAG = re.compile(r"<[!/?]?[A-Za-z][^<>]*>", re.S)
# A `<` that opens a tag-shaped construct and never closes it. TAG cannot match these,
# because `[^<>]*` stops at the next angle bracket of either kind, so without this they
# are not seen AT ALL. The lookahead is `<|\Z`, not just `\Z`: an unterminated tag in the
# middle of the document is followed by the next tag's `<` rather than by end-of-text, and
# an earlier version anchored only to `\Z` missed exactly that.
UNTERMINATED = re.compile(r"<[!/?]?[A-Za-z][^<>]*(?=<|\Z)", re.S)
ALLOWED_TAGS = {"sub", "/sub", "sup", "/sup"}
AUTOLINK = re.compile(r"\A<(?:[^\s<>@]+@[^\s<>@]+|https?://[^\s<>]+)>\Z")

# Words the manuscript spells out for small counts, so "Seven of 26" is a quantity.
WORD_NUM = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
            "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
            "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20}
QUANTITY = re.compile(r"\b(\d+|" + "|".join(WORD_NUM) + r")\s*(?:/|of)\s*(\d+)\b",
                      re.I)


def strip_fences(raw):
    """Fenced code blocks, blanked but line-preserving: code is displayed, not parsed."""
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), raw)


def visible_text(raw):
    """The manuscript with everything a reader cannot see removed.

    Only valid for a document inside the declared domain -- see `html_domain_violations`,
    which callers must run first. Outside it, this function has no defensible meaning.
    """
    return COMMENT.sub("", strip_fences(raw))


def html_domain_violations(text):
    """Raw HTML outside the closed list. Run on comment-stripped, fence-stripped text.

    The domain admits exactly two things: a BARE tag from ALLOWED_TAGS, and an autolink.
    Everything else — any attribute, any other element, any unterminated construct, at any
    length — is a violation. There is no size at which a tag stops being checked.
    """
    out = []

    def bad(pos, what, why):
        line = text.count("\n", 0, pos) + 1
        out.append(f"line {line}: {why} — {what[:80]!r}{'…' if len(what) > 80 else ''}. "
                   f"The declared domain is Markdown whose only raw HTML is a bare tag "
                   f"from {sorted(ALLOWED_TAGS)} or an autolink. Whether a reader sees "
                   f"the content anything else governs cannot be decided from the "
                   f"source, so this manuscript cannot be validated as what a reader "
                   f"sees.")

    for m in TAG.finditer(text):
        s = m.group(0)
        if AUTOLINK.match(s):
            continue
        inner = s[1:-1]
        if inner.strip().lower() in ALLOWED_TAGS and inner == inner.strip():
            continue
        bad(m.start(), s, f"raw HTML ({len(s)} chars) is outside the declared domain")

    for m in UNTERMINATED.finditer(text):
        bad(m.start(), m.group(0), "an HTML tag is opened and never closed")
    return out


def parse_tables(text):
    """Every GFM table, as (header, rows, line, span).

    `span` is the table's (start, end) CHARACTER offsets in `text`. It exists because the
    prose scan has to know WHERE the table is, not what it says — see main(). Callers that
    only want the cells can keep unpacking the first three.
    """
    lines = text.splitlines(keepends=True)
    starts, off = [], 0
    for ln in lines:
        starts.append(off)
        off += len(ln)
    starts.append(off)
    tables, i = [], 0
    while i < len(lines):
        if lines[i].strip().startswith("|") and i + 1 < len(lines) \
                and re.fullmatch(r"\s*\|[\s:|-]+\|\s*", lines[i + 1].rstrip("\r\n")):
            header = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            body, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                body.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            tables.append((header, body, i + 1, (starts[i], starts[j])))
            i = j
        else:
            i += 1
    return tables


def find_endpoint_tables(tables):
    """Tables whose first column carries the canonical endpoint labels."""
    out = []
    for t in tables:
        header, body = t[0], t[1]
        labels = [r[0] for r in body if r]
        if all(any(lbl.startswith(k) for lbl in labels) for k in ROWS):
            out.append(t)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    raw = open(PAPER, encoding="utf-8").read()
    vis = visible_text(raw)
    hidden = len(COMMENT.findall(raw))
    fenced = len(FENCE.findall(raw))

    print(f"\n  RENDERED MANUSCRIPT BOUND TO RAW DATA")
    print(f"  {len(raw):,} bytes, {hidden} HTML comment block(s) and {fenced} fenced "
          f"code block(s)\n  removed before parsing")

    # The domain, before anything is parsed. A document outside it is not judged false;
    # it is judged beyond what reading the source can establish, and that is the finding.
    outside = html_domain_violations(vis)
    print(f"  raw HTML: {len(TAG.findall(vis))} tag(s), "
          f"{'ALL inside' if not outside else f'{len(outside)} OUTSIDE'} the declared "
          f"domain\n")
    if outside:
        vr.reject("MANUSCRIPT_HTML_DOMAIN",
                  "THIS MANUSCRIPT CANNOT BE VALIDATED AS WHAT A READER SEES",
                  outside, limit=10)

    fails = []
    cand = find_endpoint_tables(parse_tables(vis))

    if len(cand) == 0:
        why = ["no VISIBLE table carries the primary endpoint rows"]
        if find_endpoint_tables(parse_tables(raw)):
            why.append("A table with those rows exists but is inside an HTML comment, "
                       "so the reader never sees it. A commented claim is not a claim.")
        vr.reject("CANONICAL_TABLE_PRESENT", "THE PRIMARY CLAIM IS NOT VISIBLE", why)
    if len(cand) > 1:
        vr.reject("CANONICAL_TABLE_UNIQUE", "THE PRIMARY CLAIM IS AMBIGUOUS", [
            f"{len(cand)} visible tables carry the primary endpoint rows "
            f"(lines {[c[2] for c in cand]})",
            "Exactly one canonical table is required: with two, which one is the claim "
            "is decided by the checker's search order, not by the author."])

    header, body, line, tbl_range = cand[0]
    print(f"  one canonical table, line {line}: {header}")

    from raw_endpoint import reconstruct, endpoint
    circuits = [c.strip() for c in open(SELECTED) if c.strip()]
    elig, excl, ge5, ge10 = endpoint(reconstruct(circuits))
    truth = {"excl": len(excl), "ge5": len(ge5), "ge10": len(ge10)}
    n_elig = len(elig)
    print(f"  reconstructed from raw: {truth['excl']}/{n_elig}, {truth['ge5']}/{n_elig}, "
          f"{truth['ge10']}/{n_elig}\n")

    seen = set()
    for row in body:
        label = row[0]
        key = next((v for k, v in ROWS.items() if label.startswith(k)), None)
        if key is None:
            continue
        seen.add(key)
        m = FRACTION.search(row[1] if len(row) > 1 else "")
        if not m:
            fails.append(f"row '{label}': no 'n / d' fraction in the circuits column")
            continue
        num, den = int(m.group(1)), int(m.group(2))
        if args.show:
            print(f"    {label:<34} {num}/{den}")
        if num != truth[key]:
            fails.append(f"row '{label}': numerator {num} != {truth[key]} "
                         f"reconstructed from raw")
        if den != n_elig:
            fails.append(f"row '{label}': denominator {den} != {n_elig} eligible "
                         f"circuits reconstructed from raw")
    for k in ROWS.values():
        if k not in seen:
            fails.append(f"canonical table is missing the '{k}' row")

    # A contradicting fraction elsewhere in visible prose. The manuscript legitimately
    # QUOTES numbers a corruption would produce -- §6.1 describes the audit that moved the
    # endpoint to 11/26 -- so a paragraph that is explicitly about an attack or a
    # withdrawal is exempt. The count of exemptions is printed: an exemption nobody can
    # see is how the next hole gets in.
    COUNTERFACTUAL = ("corrupt", "mutation", "attack", "audit", "withdraw", "would",
                      "v3 correction", "earlier versions", "changes the true endpoint")

    # WHERE the canonical table is, not WHAT IT SAYS (Astra, 3643bbc differential).
    #
    # This was `m.group(0) in tbl_span`, a SUBSTRING test against the table's text. The
    # canonical table legitimately contains "7 / 26", so every other occurrence of that
    # string anywhere in the manuscript was skipped as though it were the table's own
    # cell. Astra put "The primary risk interval excludes zero in only 7 / 26 eligible
    # circuits." in the abstract and both stage 12 and stage 13 returned 0 — the exact
    # defect the claim-identity check was added to close, still open because the scan
    # never reached it.
    #
    # Identity of a text occurrence is its POSITION. Only the canonical table's own
    # character range is excluded; any other table's cells are scanned as prose, because
    # a false claim smuggled into a second table is still a false claim.
    t_lo, t_hi = tbl_range

    def in_canonical_table(pos):
        return t_lo <= pos < t_hi

    paragraphs = [(mm.start(), mm.group(0)) for mm in re.finditer(r"[^\n]+(?:\n[^\n]+)*",
                                                                  vis)]

    def enclosing(pos):
        best = ""
        for start, text in paragraphs:
            if start <= pos < start + len(text):
                best = text
        return best.lower()

    exempt = 0
    for m in FRACTION.finditer(vis):
        num, den = int(m.group(1)), int(m.group(2))
        if den != n_elig or in_canonical_table(m.start()) or num in truth.values():
            continue
        para = enclosing(m.start())
        if any(w in para for w in COUNTERFACTUAL):
            exempt += 1
            continue
        ctx = vis[max(0, m.start() - 60):m.end() + 20].replace("\n", " ")
        fails.append(f"visible prose asserts {num}/{den}, which no endpoint supports "
                     f"— …{ctx.strip()[-90:]}")

    # CLAIM IDENTITY. The scan above asks whether a numerator is true of SOMETHING. That
    # is not the question a reader asks. 7 of 26 is true of "risk >= 5%" and false of
    # "excludes zero", so every quantity over the eligible denominator is bound to the
    # endpoint its own sentence names -- the nearest claim phrase within CLAIM_WINDOW.
    # A sentence naming no endpoint is not making one of these claims and is not checked
    # against them: "13 of 26 eligible circuits have no spread at all" is a different
    # true statement about the same 26 circuits.
    #
    # The counterfactual exemption is taken at SENTENCE level here, not paragraph level.
    # The abstract is a single paragraph that legitimately contains the word "withdrawn",
    # so a paragraph-level exemption hands an attacker the whole abstract -- which is
    # precisely where Astra put the false attribution.
    low = vis.lower()
    marks = [(mm.start(), key) for key, phrases in CLAIM_PHRASES.items()
             for p in phrases for mm in re.finditer(re.escape(p), low)]
    ends = [mm.end() for mm in re.finditer(r"(?<=[.!?:])\s+|\n\n", vis)]

    def sentence_at(pos):
        lo = max([e for e in ends if e <= pos], default=0)
        hi = min([e for e in ends if e > pos], default=len(vis))
        return vis[lo:hi].lower()

    bound = 0
    for m in QUANTITY.finditer(vis):
        tok, den = m.group(1), int(m.group(2))
        if den != n_elig or in_canonical_table(m.start()):
            continue
        num = int(tok) if tok.isdigit() else WORD_NUM[tok.lower()]
        if any(w in sentence_at(m.start()) for w in COUNTERFACTUAL):
            continue
        near = [(abs(pos - m.start()), key) for pos, key in marks
                if abs(pos - m.start()) <= CLAIM_WINDOW]
        if not near:
            continue
        key = min(near)[1]
        bound += 1
        if num != truth[key]:
            ctx = vis[max(0, m.start() - 40):m.end() + 120].replace("\n", " ")
            label = next(k for k, v in ROWS.items() if v == key)
            fails.append(f"visible prose attributes {num} of {den} to the "
                         f"'{label}' endpoint, which the raw data puts at "
                         f"{truth[key]} of {den} — …{ctx.strip()[:150]}")
    print(f"  prose scan: {exempt} endpoint-shaped fraction(s) exempted as explicitly "
          f"counterfactual;\n              {bound} prose quantit(ies) bound to the "
          f"endpoint their own sentence names")

    if fails:
        vr.reject("VISIBLE_CLAIMS_MATCH_RAW",
                  "THE VISIBLE MANUSCRIPT DOES NOT MATCH THE RAW DATA", fails, limit=20)
    vr.accept("  ✓ the table a reader sees states what the raw data produces.")


if __name__ == "__main__":
    main()
