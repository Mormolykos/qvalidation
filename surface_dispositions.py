"""Assign a disposition to every reader-visible unit — at WRITE time only.

This module runs when a human regenerates `manuscript_surface.json` and never during
verification. That separation is the whole point of finding B2: a registry rebuilt from
the document it is meant to protect proves only that the document equals itself. The
output is committed, and the diff is what a reviewer reads.

THE FOUR DISPOSITIONS, and what each one is claiming

    BOUND              carries one or more release-critical quantitative identities whose
                       values are reconstructed from raw on every verification run.
    CANONICAL          part of the generated endpoint table, validated structurally: its
                       numerators, denominator and row identity are checked against raw.
    PINNED_EXEMPTION   historical or counterfactual text that deliberately quotes
                       non-current values, exempted by exact passage identity.
    NON_CLAIM          carries no identity in the release-critical registry.

NON_CLAIM IS A DECLARATION, NOT A MEASUREMENT — and it is the honest weak point
    It does not say "this text contains no numbers". It says "no identity in
    RELEASE_IDENTITIES is asserted here". §4.3's ambiguity-band quartiles are the clear
    example: they are quantitative, they are registered, and they are NOT independently
    reconstructed by this apparatus. That is a human judgement made at freeze time about
    THAT EXACT TEXT, and the registry's contribution is that the judgement cannot drift —
    any edit changes the unit's hash and is refused. `manuscript_binding` prints how many
    NON_CLAIM units contain digits, so the size of this judgement is a number a reader
    can see rather than something they have to take on trust.
"""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import visible_surface as vs        # noqa: E402


def classify_all(raw, doc):
    """Registry entries for every unit in `doc`, in document order."""
    import manuscript_binding as mb

    vis = mb.visible_text(raw)
    cand = mb.find_endpoint_tables(mb.parse_tables(vis))
    if len(cand) != 1:
        raise SystemExit("refusing to write a registry for a manuscript that does not "
                         "carry exactly one canonical endpoint table")
    header, body, _line, tbl_span, row_spans = cand[0]

    # the canonical table's own lines, as they stand in this rendering
    canonical = {}
    for line in vis[tbl_span[0]:tbl_span[1]].splitlines():
        if not vs.normalise(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        canonical[vs.normalise(line)] = mb.canonical_key(cells)

    counterfactual = [mb.flat(p) for p in mb.COUNTERFACTUAL_PASSAGES]
    truth, n_elig = mb.truth_from_raw()
    stats = mb.distribution_from_raw()

    entries = []
    for u in doc:
        norm = vs.normalise(u["text"])
        claims, disposition = [], "NON_CLAIM"

        if norm in canonical:
            disposition = "CANONICAL"
            key = canonical[norm]
            if key:
                claims = [key]
        elif any(c and c in mb.flat(u["text"]) for c in counterfactual):
            disposition = "PINNED_EXEMPTION"
        else:
            # per-unit claim scan. A sentence does not cross a block boundary, so running
            # the recogniser on one unit gives the identities that unit asserts. This is
            # a LABELLING aid at write time; recall at verification time comes from the
            # registry, never from here.
            found, _fails = mb.claim_inventory(u["text"], truth, n_elig)
            claims = sorted({q.identity for q in found
                             if q.disposition in ("bound", "enumeration") and q.identity})
            # ALL FOUR labels, the same carrier rule `distribution_failures` applies.
            # A partial match is not the §4.2 sentence: §4.3's blockquote gives a median,
            # a p75 and a max of a DIFFERENT distribution, and labelling it with these
            # identities would have pointed the binding at the wrong population.
            if len(mb.read_distribution(u["text"])) == len(mb.DISTRIBUTION_STATS):
                claims += sorted(stats)
            if claims:
                disposition = "BOUND"

        # The unit's FULL normalised text, not an excerpt. Three things need it: the
        # diff a reviewer reads is then the page itself, the uid is checkable against
        # the entry that carries it, and `pdf_binding` can bind the built artifact to
        # the registry rather than to a manuscript an attacker has already edited.
        entries.append({"uid": vs.uid(u["text"]), "kind": u["kind"],
                        "disposition": disposition, "claims": claims, "text": norm})
    return entries
