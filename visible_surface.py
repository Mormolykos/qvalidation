"""The reader-visible surface of the manuscript, enumerated and registered.

WHY THIS FILE EXISTS (independent adversarial audit of f125dfa, finding B1)
    Four consecutive repairs of the prose scan asked "is this sentence a claim?" and
    answered it from the sentence's own words. Each repair narrowed the gap and none
    closed it, because the question is open-world: it asks the checker to recognise every
    way English can express "7 of 26". The auditor wrote nine that it could not:

        Seven of the twenty-six eligible circuits have an interval that excludes zero.
        Of the 26 eligible circuits in the pre-registered set, only seven have …
        The study resolves 26 eligible circuits, of which only seven have …
        … excludes zero in just 27% of eligible circuits.
        … in only ７ / ２６ eligible circuits.                (full-width digits)
        … in only seven (see §4.1) of the 26 eligible circuits.
        … in only __7__ / 26 eligible circuits.
        Barely a quarter of the 26 eligible circuits …
        | Summary | seven of the twenty-six eligible circuits exclude zero | | |

    None of these is a classification failure. The claim scan fails CLOSED once a quantity
    exists — but for these no quantity was ever instantiated, so the classifier was never
    asked. `twenty-six` is not in the number-word list; full-width digits fold to spaces;
    `__7__` is stopped by a word-boundary guard; `(see §4.1)` puts a digit in the gap;
    `27%` and `a quarter` have no denominator at all. Nine doors into one room, and a
    tenth exists that nobody here has thought of.

    So recall stops being a language problem. The question becomes closed-world:

        IS EVERY UNIT OF THIS MANUSCRIPT'S DECLARED SURFACE MODEL REGISTERED?

    A unit's identity is the SHA-256 of its normalised text. The registry is a committed
    file, written deliberately by `--write` and reviewed as a diff, never rebuilt during
    verification. A sentence that appears in a protected section and is not in the
    registry is REJECTED without anything reading it. Changing `12 / 26` to
    `Seven of the twenty-six` does not remove the sentence from the universe; it changes
    that unit's hash, which is the same rejection by a different route.

WHAT A UNIT IS
    A maximal run of consecutive non-blank lines, except that a heading and a table row
    are each a unit on their own, and a fenced code block is one unit including its
    fences. Blank lines separate. Nothing in this parse knows what a number is, what a
    claim is, or what vocabulary the manuscript uses — that is the point, and it is what
    makes the coverage measurement non-circular (finding B2). `quantities()` is not
    called here and must never be.

    HTML comments are removed first, and that removal is the model's one exclusion rule.
    Whether raw HTML may hide anything else is decided by
    `manuscript_binding.html_domain_violations`, which rejects the document rather than
    interpreting it.

WHERE THE MODEL AND THE RENDERED PAGE DISAGREE — measured, not supposed
    The closed world is closed over THIS PARSE of the Markdown, not over what pandoc and
    a browser put on paper. An independent audit of b5ba725 found two places where the
    two come apart, and neither is fixed by hashing harder:

    1. COMMENT STRIPPING RUNS BEFORE STRUCTURE. `COMMENT.sub("", raw)` is applied to the
       whole document, so a literal `<!-- … -->` typed INSIDE a fenced code block is
       removed here while pandoc renders it as visible text in a `<pre>`. Such a line is
       therefore reader-visible and is NOT a unit of this model. Stage 13 rejects it —
       the words reach the PDF and the registry does not carry them — so the pipeline
       holds, but this file alone does not.

    2. `normalise` DISCARDS INDENTATION AND LINE STRUCTURE. It is `" ".join(text.split())`,
       and `units` decides "table row" from `line.strip().startswith("|")`. A unit's
       identity therefore cannot distinguish a table from the same text indented into a
       code block, nor see hard line breaks, list merge/split, setext promotion, NBSP,
       U+2000, U+3000, U+0085, U+001C, CRLF↔LF or tab↔space. Indenting the canonical
       table by four spaces leaves every hash identical while destroying the table on the
       page. Whitespace cannot reorder words, so this family degrades PRESENTATION
       without falsifying a number — but "the table a reader sees" is not what this model
       checks, and it should not be described as though it were.

    Zero-width characters, combining marks and backslash hard breaks DO change a unit's
    identity and are caught. The honest statement of what this file establishes is:
    every unit of the declared Markdown surface model is registered, and the model is
    stated above so that the distance between it and the page can be argued about.

WHAT THIS DOES NOT DEFEND AGAINST — say it plainly
    Someone who edits PAPER.md and regenerates this registry in the same commit. That is
    the trust boundary `raw_integrity.py`'s manifest already has, and it is not closed by
    hashing. What the registry buys is that INSERTION AND ALTERATION STOP BEING SILENT:
    recall no longer depends on parsing English, and any change to the page is a line in
    a reviewable diff carrying the text that changed. A frozen release is reviewed once;
    this file is what makes "nothing else on the page moved" a checkable statement.

    It also does not decide whether a registered NON_CLAIM block really makes no
    quantitative assertion. That was a human judgement at freeze time. What it guarantees
    is that the judgement was made about THAT EXACT TEXT, and that the text has not moved
    since.

USAGE
    python visible_surface.py            # report the surface and its dispositions
    python visible_surface.py --write    # regenerate the registry (deliberate)
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

PAPER = os.path.join(ROOT, "PAPER.md")
LEDGER = os.path.join(ROOT, "manuscript_surface.json")

COMMENT = re.compile(r"<!--.*?-->", re.S)
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")

# RENDERING NORMALISATION — Markdown syntax that reaches no page.
#
# Used only to compare the registry against the PDF's extracted text. Every rule here is
# a statement about Markdown, not about this manuscript: a subscript tag renders as its
# contents, a fence and its info string render as nothing, and emphasis, escapes and code
# ticks are markers rather than characters. `*c*<sub>lo</sub>` is `clo` on the page, and
# a comparison that does not know this reports a difference that is not there.
#
# Measured on the v5 build: 7,723 word tokens in the registry, 7,723 in the PDF, the two
# multisets equal. This is a DECLARED normalisation, not a tolerance -- there is no
# residue budget, and any word the PDF carries that the registry does not is a failure.
SUBSUP = re.compile(r"</?su[bp]>")
FENCE_RUN = re.compile(r"(?:```+|~~~+)\S*")
MARKUP = re.compile(r"[\\_*`]")
WORD = re.compile(r"[a-z0-9]+")


def rendered_words(text):
    """The words a reader sees, as a multiset. Order and punctuation are not identity."""
    import collections
    t = MARKUP.sub("", FENCE_RUN.sub(" ", SUBSUP.sub("", text)))
    return collections.Counter(WORD.findall(t.lower()))

#: every disposition a registered unit may carry. There is no fifth state, and a unit
#: with no entry at all is UNKNOWN, which is a rejection.
DISPOSITIONS = ("BOUND", "CANONICAL", "PINNED_EXEMPTION", "NON_CLAIM")


def normalise(text):
    """Whitespace collapsed, and nothing else touched.

    Deliberately NOT `manuscript_binding.flat`: that folds non-ASCII to spaces so the
    PDF's dropped glyphs compare equal, which is right for reading a claim and wrong for
    identifying a unit. Here `７` must not equal `7` and `≥` must not equal a space —
    a unit that changed in any visible character has to get a different identity.
    """
    return " ".join(text.split())


def uid(text):
    return hashlib.sha256(normalise(text).encode("utf-8")).hexdigest()[:16]


def units(raw):
    """The reader-visible structural units of a Markdown document, in order.

    Returns a list of dicts: kind, line, text. No lexical knowledge of the content.
    """
    text = COMMENT.sub("", raw)
    lines = text.splitlines()
    out, i = [], 0

    def add(kind, first, body):
        if normalise(body):
            out.append({"kind": kind, "line": first + 1, "text": body})

    while i < len(lines):
        line = lines[i]
        if FENCE.match(line):
            mark = FENCE.match(line).group(1)[:3]
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(mark):
                j += 1
            j = min(j + 1, len(lines))
            add("code", i, "\n".join(lines[i:j]))
            i = j
            continue
        if not line.strip():
            i += 1
            continue
        if HEADING.match(line):
            add("heading", i, line)
            i += 1
            continue
        if line.strip().startswith("|"):
            add("table_row", i, line)
            i += 1
            continue
        j = i
        while (j < len(lines) and lines[j].strip()
               and not HEADING.match(lines[j]) and not FENCE.match(lines[j])
               and not lines[j].strip().startswith("|")):
            j += 1
        kind = "blockquote" if lines[i].lstrip().startswith(">") else "block"
        add(kind, i, "\n".join(lines[i:j]))
        i = j
    return out


def load_ledger(path=LEDGER):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def compare(doc_units, ledger):
    """Failures, and the disposition tally, for a document against its registry.

    The registry is an ORDERED list. Order is part of the identity of a surface: two
    paragraphs that swap places are a different page, and comparing multisets would not
    see it. `difflib` gives the minimal edit script so the report names exactly what was
    inserted, removed or altered rather than "something differs".
    """
    fails = []
    if ledger is None:
        return ([f"{os.path.relpath(LEDGER, ROOT)} is missing: the reader-visible "
                 f"surface of this manuscript has never been registered, so nothing can "
                 f"be said about what is on the page. Run "
                 f"`python visible_surface.py --write` deliberately and review the diff."],
                {}, [])

    entries = ledger.get("units", [])
    want = [e["uid"] for e in entries]
    got = [uid(u["text"]) for u in doc_units]
    unknown, missing = [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
            a=want, b=got, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        for k in range(j1, j2):
            unknown.append(doc_units[k])
        for k in range(i1, i2):
            missing.append(entries[k])

    for u in unknown:
        fails.append(
            f"line {u['line']}: a reader-visible {u['kind']} is NOT REGISTERED in the "
            f"manuscript surface — “{normalise(u['text'])[:110]}…”. Nothing read it: an "
            f"unregistered unit is refused before any claim recogniser is consulted, so "
            f"it cannot be hidden by spelling a number differently.")
    for e in missing:
        fails.append(
            f"a registered {e['kind']} ({e['disposition']}) is no longer present in the "
            f"manuscript — “{e['text'][:110]}…”. A registry that no longer describes "
            f"the page is a stale pin, which is a loud failure and not a widening.")
    for e in entries:
        if uid(e["text"]) != e["uid"]:
            fails.append(f"registry entry {e['uid']} does not hash its own text — the "
                         f"file has been edited by something other than --write")

    tally = {d: 0 for d in DISPOSITIONS}
    for e in entries:
        tally[e["disposition"]] = tally.get(e["disposition"], 0) + 1
    tally["UNKNOWN"] = len(unknown)
    return fails, tally, entries


def registered_claims(entries):
    """identity key -> the registered units that carry it."""
    out = {}
    for e in entries:
        for c in e.get("claims", ()):
            out.setdefault(c, []).append(e)
    return out


def registry_words(entries):
    """The whole registered page as a word multiset — what a faithful PDF must carry."""
    import collections
    total = collections.Counter()
    for e in entries:
        total += rendered_words(e["text"])
    return total


def unit_text_by_claim(doc_units, entries, claim):
    """The live text of the registered unit carrying `claim`, matched by UID.

    By UID, never by searching the document for a phrase: the point of the registry is
    that a claim lives in a unit whose identity is fixed, so the value check cannot be
    moved to a different sentence by an attacker who writes a better-looking one.
    """
    wanted = {e["uid"] for e in entries if claim in e.get("claims", ())}
    return [u["text"] for u in doc_units if uid(u["text"]) in wanted]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true",
                    help="regenerate the registry from the current manuscript")
    args = ap.parse_args()

    raw = open(PAPER, encoding="utf-8").read()
    doc = units(raw)

    if args.write:
        from surface_dispositions import classify_all
        entries = classify_all(raw, doc)
        json.dump({"source": "PAPER.md", "units": entries},
                  open(LEDGER, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(f"  wrote {os.path.relpath(LEDGER, ROOT)}: {len(entries)} registered "
              f"reader-visible unit(s)")
        print("  REVIEW THE DIFF. This file is the statement that nothing else on the "
              "page moved.")
        return

    fails, tally, entries = compare(doc, load_ledger())
    print(f"\n  DECLARED MARKDOWN SURFACE — {len(doc)} unit(s) parsed from PAPER.md")
    for k in DISPOSITIONS:
        print(f"    {k:<18}{tally.get(k, 0)}")
    print(f"    {'UNKNOWN':<18}{tally.get('UNKNOWN', 0)}")
    for f in fails:
        print(f"      ✗ {f}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
