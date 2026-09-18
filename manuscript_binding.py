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

THE CLAIM DOMAIN (Astra F-01/F-03, post-2842dc37)
    Two repairs of the prose scan asked the wrong question first. Both started from "does
    this sentence look like a claim worth checking?", answered it from words near the
    quantity, and SILENTLY SKIPPED whatever they did not recognise. Astra measured the
    result on the frozen manuscript: of fifteen quantities over the eligible denominator,
    two were bound, nine were pinned exemptions, and FOUR WERE UNCHECKED — including
    "13 of 26 eligible circuits have no spread at all", which could be set to any number
    without a stage turning red. Separator spellings ("7 out of 26", "7 in 26", U+2044,
    U+2215), unfamiliar predicate wording ("bounded away from zero"), a claim phrase more
    than 160 characters away, and a sentence naming two endpoints at once all reached the
    same silence. Adding each of those to a list is the losing side of R19 again.

    So the question is inverted. The DOMAIN is declared, and everything in it is checked:

        A QUANTITY OVER THE ELIGIBLE POPULATION is a reader-visible number standing as
        numerator to the eligible-set denominator — either immediately before it across
        any separator, or immediately after an explicit reference to the population.

        EVERY such quantity gets exactly one disposition: bound to a declared CLAIM
        IDENTITY and compared against that identity's value reconstructed from raw, or
        covered by a pinned exemption passage quoted here in full.

        A quantity with neither is REFUSED. Not skipped: refused, by name, with its
        surrounding text, because a number this file cannot classify is a number it
        cannot check, and passing it would be a claim of coverage it has not earned.

    A claim identity is a structure, not a sentence form: population, metric, predicate,
    value. Which identity a quantity asserts is read from the predicate vocabulary its own
    SENTENCE uses, and a sentence naming two identities over one number is refused as
    ambiguous rather than resolved by distance — nearest-marker arithmetic is exactly what
    let "excludes zero — that is, a decision risk ≥ 5% — in only 7 / 26" rebind itself to
    the endpoint that made it true. Unrecognised vocabulary now fails closed, so the
    vocabulary lists below carry no security weight: they exist so the manuscript's own
    prose can resolve, and enlarging one can never turn a rejection into a pass.

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
    7. Gives every quantity over the eligible population exactly one disposition, as
       above, and refuses the document when any quantity has none. "Every" is meant in
       the sense the scanner defines, and `tests/test_v4_astra_regressions.py` prints the
       full disposition of the frozen manuscript so the word can be audited rather than
       believed.

USAGE
    python manuscript_binding.py
    python manuscript_binding.py --show    # print the table as parsed
"""

import argparse
import bisect
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

# THE POPULATION every quantity checked here is taken over. The denominator is not a
# literal in this file: it is reconstructed from raw and passed in, so a manuscript that
# renames its own denominator does not thereby leave the domain.
POPULATION = "eligible circuits"
POPULATION_NOUNS = ("eligible", "circuits")

# THE DECLARED CLAIM IDENTITIES.
#
#     key -> (reader-facing label, metric, predicate, predicate vocabulary)
#
# Each is a structured claim over the population above: a metric, a predicate on it, and
# a value reconstructed from raw (`truth_from_raw`). The vocabulary is how the MANUSCRIPT
# spells that predicate — it decides WHICH identity a quantity asserts, never WHETHER the
# quantity is checked. A quantity whose sentence matches no vocabulary is refused, so an
# attacker gains nothing from a spelling nobody listed, and a later editor adding a
# synonym can only turn a refusal into a comparison, never a comparison into a pass.
CLAIM_IDENTITIES = {
    "excl": ("risk > 0", "decision risk", "interval excludes zero", (
        "excludes zero", "exclude zero", "excluding zero", "excluded zero",
        "does not contain zero", "does not contain 0", "bounded away from zero",
        "strictly positive", "lower bound above zero", "lower bound above 0",
        "statistically significant", "risk > 0",
        "pre-registered endpoint", "pre-registered 12")),
    "ge5": ("risk ≥ 5%", "decision risk", "at least 5%", (
        "at least 5%", "of at least 5", "5% or more", "5 percent or more",
        "risk ≥ 5%", ">= 5%")),
    "ge10": ("risk ≥ 10%", "decision risk", "at least 10%", (
        "at least 10%", "of at least 10", "10% or more", "10 percent or more",
        "risk ≥ 10%", ">= 10%")),
    "nospread": ("no seed-to-seed spread", "gate-count spread across seeds", "none", (
        "no spread", "no seed-to-seed spread", "compile deterministically",
        "compiles deterministically", "same gate count in both arms")),
    "sideflip": ("θ changed side of the threshold under resampling",
                 "sign of θ − t across 4,000 resamples", "ever changes", (
                     "side of the threshold", "changed θ's side",
                     "crossed the threshold")),
}
# The manuscript also writes the endpoint as an ordered triple — "the 12/26, 7/26 and
# 4/26 counts". Three adjacent quantities with nothing but connectors between them are
# that triple, and are checked as one claim in this order. Before this existed, those
# three numbers named no predicate at all and were three of Astra's four unchecked
# quantities.
ENUMERATION = ("excl", "ge5", "ge10")
LINK_WORDS = 3          # how far a numerator may stand from its denominator, in words

# PASSAGES WHERE THE MANUSCRIPT DELIBERATELY QUOTES NON-CURRENT ENDPOINT VALUES.
#
# WHY THIS IS A LIST AND NOT A RULE (Astra, post-4d50a2b)
#     This used to be a keyword blacklist — "corrupt", "mutation", "attack", "audit",
#     "withdraw", "would", … — tested against the sentence containing the quantity. Any
#     sentence merely MENTIONING one of those words was excused from claim checking
#     entirely. Astra prefixed the false attribution with "The audit finds that" and both
#     stage 12 and stage 13 passed. The prefix was not harmless; the word `audit` WAS the
#     payload, and any of the nine would have done.
#
#     A blacklist of contexts that excuse a claim is the same error as a blacklist of
#     inputs that fail a parser (R19): it enumerates what the author thought of, and the
#     attacker only has to think of one more. So the domain is declared instead:
#
#         EVERY endpoint quantity in the rendered text is a CURRENT CLAIM,
#         except inside these passages, quoted here in full.
#
#     Each entry must be FOUND in the document or this check fails — a stale pin is a
#     loud error, not a silent widening. Adding a new counterfactual passage is therefore
#     a deliberate edit to this list, visible in the diff, and not something a sentence
#     can arrange for itself.
#
#     An attacker editing PAPER.md can of course also edit this tuple. That is not what it
#     defends against: it removes the ability to buy an exemption with PROSE, which is
#     what the blacklist sold. Editing the checker is a code change, and the mutation
#     suite runs against the committed checker.
COUNTERFACTUAL_PASSAGES = (
    # §6.1 — the v3 correction describing what the hostile audit's corruption did to the
    # endpoint. Quotes 12/26 -> 11/26 and 7/26, 4/26 -> 6/26, 3/26, none of them current.
    "Replacing every candidate gate count in one raw arm file with a constant changes "
    "the true endpoint from 12/26 to 11/26 and the ≥5% and ≥10% counts from 7/26 and "
    "4/26 to 6/26 and 3/26",
)

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

# Words the manuscript spells out for small counts, so "Seven of 26" is a quantity and
# "none of the 26 eligible circuits changed θ's side" is a quantity of zero.
WORD_NUM = {"zero": 0, "none": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
            "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20}

# A COMPLETE number token, and nothing that is part of a longer one.
#
# There is no separator in this pattern, and that is the point: the old QUANTITY regex
# spelled the separator out (`\s*(?:/|of)\s*`), so "7 out of 26", "7 in 26", "7 of the
# 26", "7 ⁄ 26" (U+2044) and "7 ∕ 26" (U+2215) were not quantities at all. Numerator and
# denominator are found INDEPENDENTLY here and paired by nearness in words, so whatever
# an author or an attacker writes between them is irrelevant to whether the pair is seen.
#
# The guards are about number boundaries, not about separators: `26.9` and `26.28` are one
# number and not the denominator, `2026-09-17` does not contain the token 26, `4,000` is
# four thousand rather than a stray 000, and `AMD64` carries no token at all.
NUM_TOKEN = re.compile(
    r"(?<![\w.,])(?:(\d{1,3}(?:,\d{3})+|\d+)(?!\.?\d)|("
    + "|".join(sorted(WORD_NUM, key=len, reverse=True)) + r"))(?![\w])", re.I)

# Text that ends the link between a numerator and its denominator: a clause terminator,
# or any digit. The digit rule is what keeps "machine 2 | CPU | AMD64 Family 26" from
# reading as two of twenty-six — a number between two numbers means they are not a pair,
# whatever the words in between happen to be.
LINK_BREAK = re.compile(r"[.;:!?\d]")

# Sentence boundaries on the folded text: a terminator, then a space, then something that
# opens a sentence. The sentence is the unit an assertion is made in, and it is what
# scopes the search for the predicate a quantity is asserted under.
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[\"'(\[*]*[A-Z0-9§])")


def strip_fences(raw):
    """Fenced code blocks, blanked but line-preserving: code is displayed, not parsed."""
    return FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), raw)


def visible_text(raw):
    """The manuscript with everything a reader cannot see removed.

    Only valid for a document inside the declared domain -- see `html_domain_violations`,
    which callers must run first. Outside it, this function has no defensible meaning.
    """
    return COMMENT.sub("", strip_fences(raw))


def flat_map(text):
    """The folded text, and the source offset of each character in it.

    Whitespace collapsed, non-ASCII folded to a space. The claim scan runs on THIS form
    for both the manuscript and the PDF's extracted text, so the two are checked by
    identical computation rather than by two scanners that happen to agree. A line break
    inside a sentence must not change what the sentence claims, and neither must a glyph
    the PDF text layer drops: `pdftotext` renders "risk ≥ 5%" as "risk 5%", so a
    comparison that keeps the ≥ finds nothing in the PDF and silently scans the table's
    own rows as if they were prose. Folding also erases the difference between "7 / 26",
    "7 ⁄ 26" (U+2044) and "7 ∕ 26" (U+2215) before anything looks at them.

    The offset map exists so an exemption can be a POSITION rather than a string. Folding
    without carrying offsets forward would push the canonical table's exemption back into
    a text comparison, and a text comparison is what V4-03 was.
    """
    out, src, gap = [], [], True
    for i, c in enumerate(text):
        ch = c if c.isascii() else " "
        if ch.isspace():
            if not gap:
                out.append(" ")
                src.append(i)
                gap = True
        else:
            out.append(ch)
            src.append(i)
            gap = False
    while out and out[-1] == " ":
        out.pop()
        src.pop()
    return "".join(out), src


def flat(text):
    return flat_map(text)[0]


def _words(segment):
    return [w for w in segment.split(" ") if w]


def _num_tokens(norm):
    """(start, end, value) for every complete number token in the folded text."""
    out = []
    for m in NUM_TOKEN.finditer(norm):
        digits, word = m.group(1), m.group(2)
        out.append((m.start(), m.end(),
                    int(digits.replace(",", "")) if digits else WORD_NUM[word.lower()]))
    return out


def _population_follows(norm, end):
    """Does an explicit reference to the population follow this denominator token?

    "Of the 26 eligible circuits, 13 compile deterministically" puts its numerator AFTER
    the denominator and is as much a quantity over the population as "13 of 26" is. The
    population reference is what distinguishes it from a 26 that is not a denominator at
    all — "AMD64 Family 26", "the effective sample size is far below 26".
    """
    return any(w.strip("*_`,.;:()[]").lower() in POPULATION_NOUNS
               for w in _words(norm[end:end + 60])[:2])


class Quantity:
    """One number standing as numerator to the eligible-set denominator."""

    def __init__(self, num, den, start, end, anchor):
        self.num, self.den = num, den
        self.start, self.end, self.anchor = start, end, anchor
        self.identity = None
        self.disposition = "unclassified"

    def context(self, norm):
        return norm[max(0, self.start - 60):self.end + 110].strip()[:170]

    def __repr__(self):
        return (f"<{self.num}/{self.den} {self.disposition}"
                + (f":{self.identity}" if self.identity else "") + ">")


def quantities(norm, n_elig):
    """Every quantity over the eligible population, in document order.

    Numerator and denominator are located INDEPENDENTLY and paired by nearness in words.
    Nothing here knows what a separator looks like, which is why "7 out of 26", "7 in 26",
    "7 of the 26" and the two Unicode slashes are all found by a rule that was written
    before any of them was reported.
    """
    toks = _num_tokens(norm)
    out = []
    for i, (s, e, v) in enumerate(toks):
        if v != n_elig:
            continue
        pair = None
        if i:                                   # "7 / 26", "7 out of 26", "Seven of 26"
            ps, pe, pv = toks[i - 1]
            gap = norm[pe:s]
            if len(_words(gap)) <= LINK_WORDS and not LINK_BREAK.search(gap):
                pair = (pv, ps, pe)
        if pair is None and i + 1 < len(toks) and _population_follows(norm, e):
            ns, ne, nv = toks[i + 1]            # "Of the 26 eligible circuits, 13 …"
            gap = norm[e:ns]
            if len(_words(gap)) <= LINK_WORDS and not LINK_BREAK.search(gap):
                pair = (nv, ns, ne)
        if pair is not None:
            out.append(Quantity(pair[0], v, min(pair[1], s), max(pair[2], e), s))
    return out


def _markers(low):
    """(start, end, identity key) for every predicate spelling the manuscript uses."""
    out = []
    for key, (_label, _metric, _predicate, vocab) in CLAIM_IDENTITIES.items():
        for phrase in sorted({flat(v).lower() for v in vocab}):
            if not phrase:
                continue
            pat = re.escape(phrase)
            if phrase[0].isdigit():
                # a folded "5%" must not match inside "46.15%" or "0.5%"
                pat = r"(?<![\d.])" + pat
            out += [(m.start(), m.end(), key) for m in re.finditer(pat, low)]
    return out


def _sentences(norm):
    return [0] + [m.end() for m in SENTENCE.finditer(norm)] + [len(norm)]


def claim_inventory(text, truth, n_elig, exempt_passages=(), exempt_spans=()):
    """Every quantity over the eligible population, each with ONE disposition.

    `exempt_spans` are character ranges in `text`: the canonical table's own rows, whose
    exemption is a matter of WHERE they are. `exempt_passages` are declared texts, each
    of which must be FOUND — a stale pin is a loud failure, not a silent widening.

    Returns (quantities, failures). A quantity is `exempt`, `enumeration`, `bound`,
    `ambiguous` or `unclassified`, and each of the last two is itself a failure: this
    file refuses a document whose reader-visible endpoint numbers it cannot classify,
    rather than reporting a pass it did not establish.
    """
    norm, src = flat_map(text)
    low = norm.lower()
    fails, spans = [], []

    for a, b in exempt_spans:
        lo, hi = bisect.bisect_left(src, a), bisect.bisect_left(src, b)
        if hi > lo:
            spans.append((lo, hi))

    for entry in exempt_passages:
        # An entry may be a string, or a tuple of ALTERNATIVE spellings of the same
        # passage -- a canonical row keeps its pipes in Markdown and loses them in the
        # PDF's extracted text, and that is one passage in two renderings, not two
        # passages of which one is missing. At least one alternative must be found.
        alternatives = (entry,) if isinstance(entry, str) else tuple(entry)
        located = False
        for passage in alternatives:
            needle = flat(passage)
            if not needle:
                continue
            i = norm.find(needle)
            while i >= 0:
                spans.append((i, i + len(needle)))
                located = True
                i = norm.find(needle, i + 1)
        if not located:
            shown = flat(alternatives[0])[:90]
            fails.append(f"a declared exempt passage is not present in this document, so "
                         f"the exemption list no longer describes it: “{shown}…”")

    toks = _num_tokens(norm)
    marks = _markers(low)
    bounds = _sentences(norm)
    found = quantities(norm, n_elig)

    for q in found:
        if any(a <= q.start and q.end <= b for a, b in spans):
            q.disposition = "exempt"
    live = [q for q in found if q.disposition != "exempt"]

    # THE ORDERED TRIPLE, before single claims. "the 12/26, 7/26 and 4/26 counts" names
    # no predicate at all, and three of Astra's four unchecked quantities were exactly
    # that sentence. Three adjacent quantities are ONE assertion -- the endpoint, in the
    # canonical order -- and are checked as one.
    run = []
    for q in live + [None]:
        if run and q is not None:
            gap = norm[run[-1].end:q.start]
            joined = len(_words(gap)) <= LINK_WORDS and not LINK_BREAK.search(gap)
        else:
            joined = q is not None
        if not joined:
            if len(run) == len(ENUMERATION):
                got = tuple(x.num for x in run)
                want = tuple(truth[k] for k in ENUMERATION)
                for x, k in zip(run, ENUMERATION):
                    x.disposition, x.identity = "enumeration", k
                if got != want:
                    fails.append(
                        "visible prose enumerates the endpoint as "
                        + ", ".join(f"{n}/{n_elig}" for n in got)
                        + ", which the raw data puts at "
                        + ", ".join(f"{n}/{n_elig}" for n in want)
                        + f" — …{run[0].context(norm)}")
            run = []
        if q is not None:
            run.append(q)

    def governing(q):
        """Identities whose predicate governs this quantity.

        A predicate governs a quantity when it stands in the same SENTENCE and no other
        number comes between the two. The second half is what separates "Seven of 26 …
        carry a risk of at least 5% and four carry at least 10%", where "at least 10%"
        plainly belongs to `four`, from "excludes zero — that is, a decision risk ≥ 5% —
        in only 7 / 26", where both predicates reach the same number and which one is
        meant is not decidable. Distance decides neither case: the first resolves because
        a number intervenes, the second is REFUSED because none does.
        """
        i = bisect.bisect_right(bounds, q.anchor) - 1
        lo, hi = bounds[i], bounds[i + 1]
        out = set()
        for ms, me, key in marks:
            if ms < lo or me > hi:
                continue
            if me <= q.start:
                a, b = me, q.start
            elif ms >= q.end:
                a, b = q.end, ms
            else:
                out.add(key)            # the predicate names the number itself
                continue
            if any(a <= ts and te <= b
                   and not any(xs <= ts and te <= xe for xs, xe, _ in marks)
                   for ts, te, _v in toks):
                continue
            out.add(key)
        return out

    for q in live:
        if q.disposition == "enumeration":
            continue
        keys = governing(q)
        if len(keys) == 1:
            q.disposition, q.identity = "bound", keys.pop()
            if q.num != truth[q.identity]:
                fails.append(
                    f"visible prose attributes {q.num} of {q.den} to the "
                    f"'{CLAIM_IDENTITIES[q.identity][0]}' endpoint, which the raw data "
                    f"puts at {truth[q.identity]} of {q.den} — …{q.context(norm)}")
        elif not keys:
            q.disposition = "unclassified"
            fails.append(
                f"visible prose states {q.num} of {q.den} over the {POPULATION} and "
                f"names no endpoint this file can identify, so the claim cannot be "
                f"checked and is REFUSED rather than skipped — …{q.context(norm)}")
        else:
            q.disposition = "ambiguous"
            names = ", ".join(sorted(CLAIM_IDENTITIES[k][0] for k in keys))
            fails.append(
                f"visible prose states {q.num} of {q.den} in one sentence naming more "
                f"than one endpoint ({names}), so which claim the number belongs to is "
                f"not decidable and it is REFUSED — …{q.context(norm)}")
    return found, fails


def claim_failures(text, truth, n_elig, exempt_passages=(), exempt_spans=()):
    """(failures, quantities checked, quantities exempt) — see claim_inventory."""
    found, fails = claim_inventory(text, truth, n_elig, exempt_passages, exempt_spans)
    checked = sum(1 for q in found if q.disposition in ("bound", "enumeration"))
    return fails, checked, sum(1 for q in found if q.disposition == "exempt")


def truth_from_raw():
    """Every declared identity's value, reconstructed from the raw per-seed data.

    No literal in this file, and no summary table: `reconstruct` walks the raw
    observations, and the two counts §3 and §4.1 state over the eligible set fall out of
    the same pass that produces the endpoint.
    """
    from raw_endpoint import reconstruct, endpoint
    circuits = [c.strip() for c in open(SELECTED, encoding="utf-8") if c.strip()]
    elig, excl, ge5, ge10 = endpoint(reconstruct(circuits))
    return {"excl": len(excl), "ge5": len(ge5), "ge10": len(ge10),
            "nospread": sum(1 for r in elig if r["no_spread"]),
            "sideflip": sum(1 for r in elig if not r["side_stable"])}, len(elig)


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
    """Every GFM table, as (header, rows, line, span, row_spans).

    `span` is the table's (start, end) CHARACTER offsets in `text`, and `row_spans` the
    offsets of each BODY ROW. The prose scan has to know WHERE the table is, not what it
    says — and, since the differential audit, where each row is: exempting the table's
    whole character range handed an injected row an exemption it had not earned, because
    the range grows to cover whatever an attacker appends to the table (Astra F-02).
    Callers that only want the cells can keep unpacking the first three.
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
            body, row_spans, j = [], [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                body.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                row_spans.append((starts[j], starts[j + 1]))
                j += 1
            tables.append((header, body, i + 1, (starts[i], starts[j]), row_spans))
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


def canonical_key(row):
    """The identity a table row states, or None if this file does not recognise the row.

    Not recognising a row is a finding, not a default. A row the canonical table carries
    and this function cannot name is prose that happens to sit between two pipes, and it
    is scanned as prose — Astra's `| Summary | the primary interval excludes zero in only
    7 / 26 eligible circuits | | |` passed stage 12 purely by being inside the table.
    """
    label = row[0] if row else ""
    return next((v for k, v in ROWS.items() if label.startswith(k)), None)


def canonical_row_passages(body):
    """Each recognised canonical row, in both renderings it can appear in.

    Used where positions are not available — the PDF's extracted text has no table to
    parse. Exempting every occurrence is safe here in a way that exempting a character
    range is not: each passage is a COMPLETE canonical row, so a second copy of one
    asserts exactly what the first asserts, and nothing else inherits the exemption.
    """
    return [(" ".join(r), "| " + " | ".join(r) + " |")
            for r in body if canonical_key(r)]


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

    header, body, line, tbl_range, row_spans = cand[0]
    print(f"  one canonical table, line {line}: {header}")

    truth, n_elig = truth_from_raw()
    print(f"  reconstructed from raw: {truth['excl']}/{n_elig}, {truth['ge5']}/{n_elig}, "
          f"{truth['ge10']}/{n_elig}  (+ {truth['nospread']} with no seed-to-seed "
          f"spread, {truth['sideflip']} changing θ's side)\n")

    seen, exempt_spans = set(), []
    for row, span in zip(body, row_spans):
        key = canonical_key(row)
        if key is None:
            continue                 # NOT exempt — scanned as prose, see canonical_key
        label = row[0]
        seen.add(key)
        # Exempt exactly the row this file recognised and is about to check itself, and
        # only if it is the shape the header declares. A canonical row with a surplus
        # cell would otherwise carry an unchecked cell under an exemption earned by the
        # cells around it.
        if len(row) != len(header):
            fails.append(f"row '{label}': {len(row)} cells under a {len(header)}-column "
                         f"header — the row is not the shape the table declares")
        else:
            exempt_spans.append(span)
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

    # CLAIM IDENTITY, over the whole rendered text. Every quantity over the eligible
    # population gets one disposition and none is skipped -- see THE CLAIM DOMAIN in the
    # module docstring. Two kinds of exemption, and they are not interchangeable:
    #
    #   POSITIONS  the canonical rows this file recognised and checked above, by their
    #              character spans. Not the table's whole range: that range grows with
    #              whatever is appended to the table, which is how an injected row
    #              inherited an exemption it had not earned (Astra F-02).
    #   PASSAGES   COUNTERFACTUAL_PASSAGES, quoted in full, each of which must be found.
    #
    # pdf_binding runs the same function over the PDF's extracted text with the row
    # passages instead of the row positions, because that text has no table to parse.
    found, cfails = claim_inventory(vis, truth, n_elig, COUNTERFACTUAL_PASSAGES,
                                    exempt_spans)
    fails += cfails
    tally = {d: sum(1 for q in found if q.disposition == d)
             for d in ("bound", "enumeration", "exempt", "ambiguous", "unclassified")}
    print(f"  claim domain: {len(found)} quantit(ies) over the {n_elig} {POPULATION} — "
          f"{tally['bound']} bound to a\n                declared identity, "
          f"{tally['enumeration']} in the endpoint enumeration, {tally['exempt']} inside "
          f"{len(exempt_spans)} canonical\n                row(s) and "
          f"{len(COUNTERFACTUAL_PASSAGES)} pinned counterfactual passage(s), "
          f"{tally['ambiguous']} ambiguous, {tally['unclassified']} unclassified")

    if fails:
        vr.reject("VISIBLE_CLAIMS_MATCH_RAW",
                  "THE VISIBLE MANUSCRIPT DOES NOT MATCH THE RAW DATA", fails, limit=20)
    vr.accept("  ✓ the table a reader sees states what the raw data produces.")


if __name__ == "__main__":
    main()
