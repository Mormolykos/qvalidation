"""Regression tests for every Astra-controlled case that exposed a defect in v4.

Each test names the finding it belongs to and asserts the REASON the artifact is
rejected, not merely that something failed. A negative test that accepts any nonzero
outcome cannot tell a validation rejection from a crash — that was finding V4-07, and
repeating it here would be the same mistake in the file meant to prevent it.

These run in-process against copies of the real artifacts. `mutation_test.py` covers the
same ground end-to-end through the whole verifier; this file exists so the defects stay
covered in a second and a half instead of twenty minutes, and so a failure points at one
function.
"""
import csv
import io
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import derived_binding as db          # noqa: E402
import manuscript_binding as mb       # noqa: E402
import pdf_binding as pb              # noqa: E402

SUMMARY = os.path.join(ROOT, "results", "summary", "prereg_heavy-hex.csv")
PAPER = os.path.join(ROOT, "PAPER.md")


# ---------------------------------------------------------------- fixtures

@pytest.fixture(scope="module")
def saved():
    with open(SUMMARY, encoding="utf-8", newline="") as fh:
        rdr = csv.DictReader(fh)
        return list(rdr.fieldnames), [dict(r) for r in rdr]


@pytest.fixture(scope="module")
def paper():
    return open(PAPER, encoding="utf-8").read()


def reasons(fails):
    return " | ".join(fails)


# ---------------------------------------------------------------- V4-01

def test_pristine_summary_is_inside_its_declared_domain(saved):
    """The control. Without this, every rejection below proves nothing."""
    header, rows = saved
    assert db.check_schema(header, rows) == []


@pytest.mark.parametrize("field", ["error_ci_lo", "error_ci_hi"])
@pytest.mark.parametrize("token", ["NaN", "nan", "inf", "-inf", "Infinity"])
def test_nonfinite_risk_bound_is_rejected_before_comparison(saved, field, token):
    """V4-01. `abs(NaN - want) > tol` is False, so a nonfinite value satisfies every
    tolerance test ever written. All 36 bounds set to NaN passed 13/13 stages."""
    header, rows = saved
    rows = [dict(r) for r in rows]
    for r in rows:
        if r[field]:
            r[field] = token
    fails = db.check_schema(header, rows)
    assert fails, f"{token} in {field} was accepted"
    assert "is not finite" in reasons(fails)


@pytest.mark.parametrize("field,value", [("n_seeds", "200.9"), ("k", "3.9"),
                                         ("n_seeds", "2e2"), ("k", "3.0")])
def test_fractional_integer_metadata_is_not_truncated_into_validity(saved, field, value):
    """V4-01. `int(float("200.9"))` is 200, so the comparison succeeded on a value the
    schema does not admit."""
    header, rows = saved
    rows = [dict(r) for r in rows]
    for r in rows:
        r[field] = value
    fails = db.check_schema(header, rows)
    assert fails, f"{field}={value} was accepted"
    assert "not an integer literal" in reasons(fails)


def test_duplicate_circuit_row_is_rejected(saved):
    """V4-01. A dict keyed by circuit collapses duplicates before anything counts them."""
    header, rows = saved
    fails = db.check_schema(header, rows + [dict(rows[0])])
    assert "already appears" in reasons(fails)


@pytest.mark.parametrize("field", ["n_seeds", "est_long_run_change_pct", "verdict",
                                   "boundary", "threshold"])
def test_a_blank_required_cell_is_rejected_not_crashed(saved, field):
    """V4-01, round two (Astra, 3643bbc differential). A blank required cell reached the
    self-consistency checks as None and raised TypeError on the first comparison. A crash
    tells a reader nothing they can act on, and is not a detection."""
    header, rows = saved
    rows = [dict(r) for r in rows]
    rows[0][field] = ""
    fails = db.check_schema(header, rows)          # must not raise
    assert fails, f"a blank {field} was accepted"
    assert "required field is empty" in reasons(fails)


def test_the_optional_risk_fields_may_be_blank_only_where_they_are_absent(saved):
    """The control for the test above: the three UNRESOLVED circuits legitimately carry
    no risk figures, and must not be rejected for it."""
    header, rows = saved
    assert db.check_schema(header, rows) == []
    unresolved = [r for r in rows if r["verdict"] == "UNRESOLVED"]
    assert len(unresolved) == 3
    assert all(r["error_ci_lo"] == "" for r in unresolved)


def test_an_extra_unlabelled_cell_is_rejected(saved):
    """V4-01, round two. csv.DictReader files a surplus cell under the None key, where
    no field-by-field check ever looks at it: the row is malformed and every declared
    column still validates."""
    header, rows = saved
    rows = [dict(r) for r in rows]
    rows[0][None] = ["9999"]
    fails = db.check_schema(header, rows)
    assert fails and "belongs to no column" in reasons(fails)


def test_a_short_row_is_rejected(saved):
    header, rows = saved
    rows = [dict(r) for r in rows]
    del rows[0]["verdict"]
    rows[0]["verdict"] = db.MISSING
    fails = db.check_schema(header, rows)
    assert fails and "ends before column" in reasons(fails)


def test_a_reordered_header_is_rejected(saved):
    """Column ORDER is part of the contract: anything reading the artifact positionally
    would silently transpose two columns."""
    header, rows = saved
    swapped = list(header)
    swapped[0], swapped[1] = swapped[1], swapped[0]
    fails = db.check_schema(swapped, rows)
    assert fails and "column ORDER" in reasons(fails)


def test_embedded_header_row_is_rejected(saved):
    header, rows = saved
    fails = db.check_schema(header, rows + [{k: k for k in rows[0]}])
    assert "second header row" in reasons(fails)


def test_unknown_column_is_rejected(saved):
    """A checker that ignores columns it does not know cannot notice a second one."""
    header, rows = saved
    rows = [dict(r, error_rate_v2="0.5") for r in rows]
    fails = db.check_schema(header + ["error_rate_v2"], rows)
    assert "not in the declared schema" in reasons(fails)


def test_unrecognised_boolean_token_does_not_become_false(saved):
    """V4-01. `str(raw).lower() in ("true","1","yes")` silently maps anything else to
    False, so a corrupted flag reads as a valid negative."""
    header, rows = saved
    rows = [dict(r) for r in rows]
    rows[0]["boundary"] = "yes"
    fails = db.check_schema(header, rows)
    assert "is not one of" in reasons(fails)


def test_probability_outside_the_unit_interval_is_rejected(saved):
    header, rows = saved
    rows = [dict(r) for r in rows]
    rows[0]["error_rate"] = "1.5"
    assert "outside [0, 1]" in reasons(db.check_schema(header, rows))


def test_risk_point_outside_its_own_interval_is_rejected(saved):
    """Self-consistency, checked on the saved row alone with no replay."""
    header, rows = saved
    rows = [dict(r) for r in rows]
    r = rows[0]
    r["error_ci_lo"], r["error_ci_hi"] = r["error_ci_hi"], r["error_ci_lo"]
    assert "lies outside its own interval" in reasons(db.check_schema(header, rows))


def test_endpoint_flag_must_follow_the_interval_it_describes(saved):
    """V4-01. `error_excludes_zero` was compared as a string and never recomputed from
    the bounds, so NaN bounds could sit beside an unchanged flag."""
    header, rows = saved
    rows = [dict(r) for r in rows]
    hit = False
    for r in rows:
        if r["error_ci_lo"] and float(r["error_ci_lo"]) == 0.0:
            r["error_excludes_zero"] = "True"
            hit = True
    assert hit, "fixture needs at least one zero lower bound"
    assert "must follow the interval" in reasons(db.check_schema(header, rows))


def test_boundary_flag_must_follow_the_saved_distance(saved):
    header, rows = saved
    rows = [dict(r) for r in rows]
    rows[0]["boundary"] = str(rows[0]["boundary"] != "True")
    assert "from the cut" in reasons(db.check_schema(header, rows))


# ---------------------------------------------------------------- V4-03

def test_pristine_manuscript_is_inside_the_declared_html_domain(paper):
    assert mb.html_domain_violations(mb.visible_text(paper)) == []


@pytest.mark.parametrize("wrapper", [
    '<div style="display:none">',
    '<div hidden>',
    '<span style="visibility:hidden">',
    '<p style="font-size:0">',
    '<div aria-hidden="true">',
    '<div style="color:#fff;background:#fff">',
])
def test_any_visibility_bearing_html_is_refused_not_interpreted(paper, wrapper):
    """V4-03. Astra hid the canonical table in a display:none div and stage 12 returned 0.
    The repair is not a list of CSS tricks — it is that raw HTML outside a closed list of
    bare inline tags is REFUSED, because no amount of source reading decides whether a
    reader sees what it governs."""
    doc = paper.replace("## Abstract", wrapper + "\n\n## Abstract\n\n</div>", 1)
    fails = mb.html_domain_violations(mb.visible_text(doc))
    assert fails, f"{wrapper} was accepted"
    assert "outside the declared domain" in reasons(fails)


def test_prose_less_than_sign_is_not_mistaken_for_a_tag(paper):
    """The domain check must not fire on 'p < 0.001, n = 23)'. It did, on first writing:
    `<[^>]+>` reads to the next '>' anywhere in the document."""
    assert mb.html_domain_violations("a p < 0.001 and n > 3 result") == []


def test_autolinked_email_is_inside_the_domain():
    assert mb.html_domain_violations("<bedvibe@bedvibe.studio>") == []
    assert mb.html_domain_violations("<https://example.org/x>") == []


def test_subscript_tags_are_inside_the_domain():
    assert mb.html_domain_violations("X<sub>A</sub>(s) and e<sup>2</sup>") == []
    # ...but only bare. An attribute is a visibility question again.
    assert mb.html_domain_violations('<sub class="x">A</sub>')


def test_astras_original_false_abstract_reproducer_is_rejected(paper):
    """V4-03, round two (Astra, 3643bbc differential) — the reproducer VERBATIM.

    The repaired scan caught the word-number form ("Seven of 26") and that masked the
    fact that the numeral form Astra actually ran still passed. `m.group(0) in tbl_span`
    was a SUBSTRING test against the canonical table's text, and the table legitimately
    contains "7 / 26", so every other occurrence of that string anywhere in the document
    was skipped as though it were the table's own cell.
    """
    from raw_endpoint import reconstruct, endpoint
    sentence = ("The primary risk interval excludes zero in only 7 / 26 eligible "
                "circuits.")
    doc = paper.replace("## Abstract", "## Abstract\n\n" + sentence, 1)
    vis = mb.visible_text(doc)
    cand = mb.find_endpoint_tables(mb.parse_tables(vis))
    assert len(cand) == 1
    t_lo, t_hi = cand[0][3]
    hit = vis.index(sentence)
    assert not (t_lo <= hit < t_hi), "the abstract is not inside the canonical table"
    # the identical string really is in the table -- which is why a text test failed
    assert "7 / 26" in "\n".join("|".join(r) for r in cand[0][1])

    circuits = [c.strip() for c in open(os.path.join(ROOT, "_selected.txt")) if c.strip()]
    elig, excl, ge5, ge10 = endpoint(reconstruct(circuits))
    assert len(excl) == 12 and len(ge5) == 7 and len(elig) == 26


ASTRA_PREFIXED = ("The audit finds that the primary risk interval excludes zero in only "
                  "7 / 26 eligible circuits.")
ASTRA_PLAIN = ("The primary risk interval excludes zero in only 7 / 26 eligible "
               "circuits.")


_TRUTH = {}


def _truth():
    """Reconstructed from raw once per session — twenty seconds, not once per test."""
    if not _TRUTH:
        truth, n_elig = mb.truth_from_raw()
        _TRUTH.update(truth=truth, n_elig=n_elig)
    return _TRUTH["truth"], _TRUTH["n_elig"]


def _inventory(doc):
    """The claim scan exactly as stage 12 runs it, on a supplied document.

    Including how the exemptions are formed, because that is where F-02 lived: only the
    rows whose identity `canonical_key` can name are exempt, and only by their own
    character spans.
    """
    vis = mb.visible_text(doc)
    cand = mb.find_endpoint_tables(mb.parse_tables(vis))
    assert len(cand) == 1
    body, row_spans = cand[0][1], cand[0][4]
    spans = [s for r, s in zip(body, row_spans) if mb.canonical_key(r)]
    truth, n_elig = _truth()
    return mb.claim_inventory(vis, truth, n_elig, mb.COUNTERFACTUAL_PASSAGES, spans)


def _scan(doc):
    """(failures, quantities checked, quantities exempt) for a supplied document."""
    found, fails = _inventory(doc)
    return (fails,
            sum(1 for q in found if q.disposition in ("bound", "enumeration")),
            sum(1 for q in found if q.disposition == "exempt"))


@pytest.mark.parametrize("sentence,name", [(ASTRA_PREFIXED, "prefixed"),
                                           (ASTRA_PLAIN, "plain")])
def test_a_prose_prefix_does_not_buy_an_exemption(paper, sentence, name):
    """BLOCKER 1 (Astra, post-4d50a2b).

    The exemption was a keyword blacklist — "corrupt", "mutation", "attack", "audit",
    "withdraw", "would", … — tested against the sentence containing the quantity. Any
    sentence merely MENTIONING one of those was excused from claim checking entirely, so
    "The audit finds that" was not a harmless prefix: the word `audit` was the payload,
    and any of the nine would have served. The plain form is kept beside it because the
    PAIR is the finding — detection depended on the opening words, not on the assertion.
    """
    fails, bound, spans = _scan(paper.replace("## Abstract",
                                              "## Abstract\n\n" + sentence, 1))
    assert fails, f"the {name} false attribution was accepted"
    assert "attributes 7 of 26" in reasons(fails)
    assert "risk > 0" in reasons(fails)


def test_the_two_forms_are_rejected_identically(paper):
    """Detection must not depend on sentence form at all, so the two reproducers must
    produce the same finding."""
    a = [f for f in _scan(paper.replace("## Abstract",
                                        "## Abstract\n\n" + ASTRA_PREFIXED, 1))[0]
         if "attributes" in f]
    b = [f for f in _scan(paper.replace("## Abstract",
                                        "## Abstract\n\n" + ASTRA_PLAIN, 1))[0]
         if "attributes" in f]
    assert len(a) == len(b) == 1


def test_every_counterfactual_exemption_is_a_declared_passage(paper):
    """The control. Each declared passage must be PRESENT — a stale pin is a loud
    failure, not a silent widening — and the pristine manuscript must pass."""
    assert mb.COUNTERFACTUAL_PASSAGES, "the exemption list is empty"
    fails, checked, exempt = _scan(paper)
    assert fails == []
    assert exempt == 3 + 6, "three canonical rows and the §6.1 correction's six figures"
    assert checked >= 2


def test_a_stale_exemption_pin_fails_loudly():
    """An exemption that no longer describes the document must be reported, not ignored."""
    truth, n_elig = _truth()
    fails, _, _ = mb.claim_failures("nothing relevant here", truth, n_elig,
                                    ("a passage that is not present",))
    assert fails and "no longer describes it" in reasons(fails)


def test_legitimate_table_occurrences_of_seven_of_26_still_pass(paper):
    """The repair must not start rejecting the canonical table's own cells."""
    vis = mb.visible_text(paper)
    cand = mb.find_endpoint_tables(mb.parse_tables(vis))
    lo, hi = cand[0][3]
    assert "7 / 26" in vis[lo:hi], "the table really does contain the string"
    fails, _, _ = _scan(paper)
    assert fails == []


def test_the_counterfactual_passage_is_still_exempt(paper):
    """The §6.1 correction quotes 11/26, 6/26 and 3/26, none of them current. It must
    remain exempt, or the repair has simply moved the false-positive problem."""
    fails, _, _ = _scan(paper)
    assert not any("11/26" in f or "6/26" in f or "3/26" in f for f in fails)


def test_the_canonical_table_is_excluded_by_position_not_by_text(paper):
    """The span is a character range, so an identical string elsewhere is still scanned."""
    cand = mb.find_endpoint_tables(mb.parse_tables(mb.visible_text(paper)))
    lo, hi = cand[0][3]
    assert isinstance(lo, int) and isinstance(hi, int) and hi > lo
    body = "\n".join("|".join(r) for r in cand[0][1])
    assert "12 / 26" in body and mb.visible_text(paper)[lo:hi].count("12 / 26") >= 1


# ---------------------------------------------------------------- F-01 (post-2842dc37)
#
# The separator, the predicate spelling, the distance and the number of predicates in one
# sentence were all attacker-controlled, and each of them decided whether a reader-visible
# endpoint assertion was examined at all. They are Astra's cases verbatim.

F01_ATTACKS = {
    # the end-to-end reproducer, exactly as the report gives it
    "out of": "The audit finds that the primary risk interval excludes zero in only "
              "7 out of 26 eligible circuits.",
    "in": "The primary risk interval excludes zero in only 7 in 26 eligible circuits.",
    "of the": "The primary risk interval excludes zero in only 7 of the 26 eligible "
              "circuits.",
    "U+2044 fraction slash": "The primary risk interval excludes zero in only 7 ⁄ 26 "
                             "eligible circuits.",
    "U+2215 division slash": "The primary risk interval excludes zero in only 7 ∕ 26 "
                             "eligible circuits.",
    "strictly positive": "The decision risk is strictly positive in only 7 / 26 eligible "
                         "circuits.",
    "bounded away from zero": "The primary risk estimate is bounded away from zero in "
                              "only 7 / 26 eligible circuits.",
    "statistically significant": "The effect is statistically significant in only 7 / 26 "
                                 "eligible circuits.",
    # the claim phrase more than the old CLAIM_WINDOW = 160 characters from the quantity
    "distance": "The primary risk interval excludes zero, a property we report "
                "descriptively and do not attribute to any mechanism, and which the "
                "pre-registration fixed in advance as the endpoint of record for this "
                "study and for every study that follows it, in only 7 / 26 eligible "
                "circuits.",
}


@pytest.mark.parametrize("name", sorted(F01_ATTACKS))
def test_a_false_attribution_is_caught_however_it_is_spelled(paper, name):
    """F-01. Every one of these passed all thirteen stages against 2842dc37."""
    sentence = F01_ATTACKS[name]
    fails, _, _ = _scan(paper.replace("## Abstract", "## Abstract\n\n" + sentence, 1))
    assert fails, f"the {name!r} form was accepted"
    assert "attributes 7 of 26" in reasons(fails)
    assert "risk > 0" in reasons(fails)


def test_the_distance_variant_really_is_beyond_the_old_window(paper):
    """The point of that case is the distance, so the distance is asserted, not assumed."""
    s = F01_ATTACKS["distance"]
    assert s.index("7 / 26") - (s.index("excludes zero") + len("excludes zero")) > 160


def test_one_sentence_naming_two_endpoints_is_refused_not_resolved(paper):
    """F-01, the rebinding case. Nearest-marker arithmetic bound this to 'risk ≥ 5%',
    which made it true. Two predicates reach the same number with nothing between them,
    so which claim it belongs to is not decidable and the document is refused."""
    sentence = ("The interval excludes zero — that is, a decision risk ≥ 5% "
                "— in only 7 / 26 eligible circuits.")
    fails, _, _ = _scan(paper.replace("## Abstract", "## Abstract\n\n" + sentence, 1))
    assert fails and "more than one endpoint" in reasons(fails)
    assert "risk > 0" in reasons(fails) and "risk ≥ 5%" in reasons(fails)


def test_an_unrecognised_predicate_fails_closed(paper):
    """The property that makes the vocabulary lists carry no security weight: a predicate
    nobody listed is a REFUSAL, so enlarging a list can only turn a refusal into a
    comparison, never a comparison into a pass."""
    sentence = ("The primary risk interval sits entirely to the right of the origin in "
                "7 / 26 eligible circuits.")
    fails, _, _ = _scan(paper.replace("## Abstract", "## Abstract\n\n" + sentence, 1))
    assert fails and "names no endpoint this file can identify" in reasons(fails)


def test_a_number_over_the_denominator_with_no_predicate_at_all_is_refused(paper):
    """A bare quantity is not a free pass: it is a reader-visible endpoint number this
    file cannot classify, and it is refused rather than skipped."""
    fails, _, _ = _scan(paper.replace(
        "## Abstract", "## Abstract\n\nThe headline figure is 9 / 26 eligible circuits.",
        1))
    assert fails and "REFUSED rather than skipped" in reasons(fails)


def test_a_predicate_in_a_neighbouring_sentence_does_not_govern(paper):
    """The other half of the sentence rule. 'four carry at least 10%' in the abstract
    must keep binding 'at least 10%' to `four` and not to 'Seven of 26' — a number
    between a predicate and a quantity means the predicate belongs to that number."""
    found, fails = _inventory(paper)
    seven = [q for q in found if q.num == 7 and q.disposition == "bound"]
    assert len(seven) == 1 and seven[0].identity == "ge5"
    assert fails == []


# ---------------------------------------------------------------- F-02 (post-2842dc37)

INJECTED_ROWS = {
    # Astra's row, verbatim
    "summary": "| Summary | the primary interval excludes zero in only 7 / 26 eligible "
               "circuits | | |",
    # the same class, differently worded, so the repair cannot be specific to the above
    "aside": "| Aside | nine of 26 eligible circuits reach the pre-registered endpoint "
             "| | |",
}


@pytest.mark.parametrize("name", sorted(INJECTED_ROWS))
def test_an_injected_row_does_not_inherit_the_tables_exemption(paper, name):
    """F-02. The exemption was `vis[tbl_range[0]:tbl_range[1]]` — the table's whole
    character range, which GROWS with whatever is appended to the table. An unrecognised
    row was therefore exempt by location, and stage 12 passed."""
    last = "| risk ≥ 10% | 4 / 26 | 15.4% | [6.2, 33.5] |"
    doc = paper.replace(last, last + "\n" + INJECTED_ROWS[name], 1)
    assert doc != paper
    fails, _, _ = _scan(doc)
    assert fails, f"the {name!r} row inherited the table's exemption"
    assert "26" in reasons(fails)


def test_only_rows_this_file_can_name_are_exempt(paper):
    """The mechanism under the two tests above, stated directly."""
    last = "| risk ≥ 10% | 4 / 26 | 15.4% | [6.2, 33.5] |"
    doc = paper.replace(last, last + "\n" + INJECTED_ROWS["summary"], 1)
    cand = mb.find_endpoint_tables(mb.parse_tables(mb.visible_text(doc)))
    body = cand[0][1]
    assert len(body) == 4, "the injected row is inside the canonical table"
    named = [r for r in body if mb.canonical_key(r)]
    assert len(named) == 3 and all(r[0] != "Summary" for r in named)


def test_a_canonical_row_of_the_wrong_shape_is_not_exempted(paper):
    """A surplus cell on a row this file DOES recognise would otherwise ride in under an
    exemption earned by the cells around it."""
    doc = paper.replace("| risk ≥ 5% | 7 / 26 | 26.9% | [13.7, 46.1] |",
                        "| risk ≥ 5% | 7 / 26 | 26.9% | [13.7, 46.1] | 9 / 26 |", 1)
    assert doc != paper
    vis = mb.visible_text(doc)
    cand = mb.find_endpoint_tables(mb.parse_tables(vis))
    header, body, _, _, row_spans = cand[0]
    wide = [r for r in body if len(r) != len(header)]
    assert wide, "the mutated row is wider than the header"


# ---------------------------------------------------------------- F-03 (post-2842dc37)

def test_the_quantity_recogniser_classifies_everything_it_finds(paper):
    """F-03, and the proof behind the word "every" in manuscript_binding's docstring.

    Astra measured the frozen manuscript: fifteen quantities over the eligible
    denominator, two bound, nine exempt, FOUR SILENTLY UNCHECKED. The disposition of
    every one is printed here, so the claim of coverage is auditable rather than
    asserted, and the required final state is `silently unchecked = 0`.
    """
    found, fails = _inventory(paper)
    tally = {}
    for q in found:
        tally[q.disposition] = tally.get(q.disposition, 0) + 1
    report = "\n".join(f"    {q.num:>3}/{q.den}  {q.disposition:<12}{q.identity or '—'}"
                       for q in found)
    print(f"\n  disposition of every quantity over the eligible denominator:\n{report}\n"
          f"    {tally}")
    assert fails == []
    assert tally.get("unclassified", 0) == 0 and tally.get("ambiguous", 0) == 0
    assert set(tally) <= {"bound", "enumeration", "exempt"}
    # NO COMPLETENESS CLAIM IS MADE HERE (independent audit, B2). This used to assert
    # `len(found) >= 15` and call the result full coverage, which measured the recogniser
    # with the recogniser: an assertion it never instantiated cannot appear in `found`,
    # so the count is unchanged by the very attacks that defeat it. Coverage is
    # established against the independent reader-visible universe in the B2 section
    # below, and this test now claims only what it can see: everything DETECTED was
    # classified.


def test_the_deterministic_compilation_count_is_bound_to_raw(paper):
    """F-03's substantive example. Astra changed 13 to 7 and stages 6, 7 and 12 stayed
    green, because the number named a predicate the scan had no identity for."""
    doc = paper.replace("13 of 26 eligible circuits have no spread at all",
                        "7 of 26 eligible circuits have no spread at all", 1)
    assert doc != paper
    fails, _, _ = _scan(doc)
    assert fails and "no seed-to-seed spread" in reasons(fails)
    assert "attributes 7 of 26" in reasons(fails)


def test_the_denominator_first_form_is_a_quantity_too(paper):
    """"Of the 26 eligible circuits, 13 compile deterministically" states its numerator
    after its denominator and is as much a claim as "13 of 26" is."""
    doc = paper.replace("Of the 26 eligible circuits, **13 compile",
                        "Of the 26 eligible circuits, **7 compile", 1)
    assert doc != paper
    fails, _, _ = _scan(doc)
    assert fails and "no seed-to-seed spread" in reasons(fails)


@pytest.mark.parametrize("old,new", [("the 12/26,", "the 11/26,"),
                                     ("7/26 and 4/26 counts", "9/26 and 4/26 counts"),
                                     ("7/26 and 4/26 counts", "7/26 and 6/26 counts")])
def test_the_endpoint_enumeration_is_one_checked_claim(paper, old, new):
    """F-03. "the 12/26, 7/26 and 4/26 counts" names no predicate at all, so all three
    were unchecked. Three adjacent quantities are the endpoint in canonical order."""
    doc = paper.replace(old, new, 1)
    assert doc != paper
    fails, _, _ = _scan(doc)
    assert fails and "enumerates the endpoint as" in reasons(fails)


def test_the_two_counts_the_manuscript_states_come_from_raw():
    """Both were added to the reconstruction rather than written down: 13 eligible
    circuits with both arms constant across every seed, and none whose θ changes side of
    the threshold across the 4,000 resamples."""
    truth, n_elig = _truth()
    assert n_elig == 26
    assert truth["nospread"] == 13 and truth["sideflip"] == 0
    assert truth["excl"] == 12 and truth["ge5"] == 7 and truth["ge10"] == 4


def test_the_self_description_promises_what_the_disposition_test_proves():
    """F-04. The docstring claimed it bound every prose quantity over the eligible
    denominator while four went unchecked. It may only claim what is demonstrated."""
    doc = mb.__doc__
    assert "THE CLAIM DOMAIN" in doc
    assert "refused" in doc.lower() and "skipped" in doc.lower()
    assert "CLAIM_WINDOW" not in doc and not hasattr(mb, "CLAIM_WINDOW")
    assert not hasattr(mb, "CLAIM_PHRASES"), \
        "the phrase list was replaced by declared claim identities"


@pytest.mark.parametrize("length", [500, 1200, 5000])
def test_a_long_tag_does_not_escape_the_domain_check(paper, length):
    """V4-03, round two. The scanner used `[^<>]{0,400}`, so a tag longer than 400
    characters matched nothing and passed. A limit on how much an attacker may type is
    not a domain, it is a budget."""
    pad = "x" * length
    doc = paper.replace("## Abstract", f'<div style="display:none" data-p="{pad}">'
                                       "\n\n## Abstract", 1)
    fails = mb.html_domain_violations(mb.visible_text(doc))
    assert fails, f"a {length}-character tag escaped the domain check"
    assert "outside the declared domain" in reasons(fails)


def test_an_opened_tag_with_no_closing_bracket_is_rejected(paper):
    """Mid-document it matches as a tag running to the next '>' anywhere; at end of text
    nothing closes it at all. Both are outside the domain and both must be named."""
    mid = paper.replace("## Abstract", '<div style="display:none"\n\n## Abstract', 1)
    assert mb.html_domain_violations(mb.visible_text(mid))
    trailing = paper + '\n<div style="display:none" data-x="y'
    fails = mb.html_domain_violations(mb.visible_text(trailing))
    assert fails and "never closed" in reasons(fails)


def test_quantity_is_bound_to_the_endpoint_its_own_sentence_names():
    """V4-03. 7 of 26 is TRUE of 'risk >= 5%' and FALSE of 'excludes zero'. Checking a
    numerator against the set of true numerators cannot tell those apart; Astra put the
    false attribution in the abstract, where a paragraph-level exemption for the word
    'withdrawn' had already excused the whole block."""
    text = "Seven of 26 eligible circuits have a risk interval that excludes zero."
    qs = mb.quantities(mb.flat(text), 26)
    assert len(qs) == 1 and qs[0].num == 7 and qs[0].den == 26, \
        "the word-numeral form must be recognised as a quantity"
    assert "excludes zero" in mb.CLAIM_IDENTITIES["excl"][3]
    _, fails = mb.claim_inventory(text, {"excl": 12, "ge5": 7, "ge10": 4,
                                         "nospread": 13, "sideflip": 0}, 26)
    assert fails and "attributes 7 of 26" in reasons(fails)


@pytest.mark.parametrize("text,num", [
    ("7 / 26 eligible circuits", 7),
    ("7 out of 26 eligible circuits", 7),
    ("7 in 26 eligible circuits", 7),
    ("7 of the 26 eligible circuits", 7),
    ("7 ⁄ 26 eligible circuits", 7),
    ("7 ∕ 26 eligible circuits", 7),
    ("Seven of 26 eligible circuits", 7),
    ("none of the 26 eligible circuits", 0),
    ("Of the 26 eligible circuits, 13 compile deterministically", 13),
])
def test_the_separator_is_not_part_of_the_decision(text, num):
    """F-01. The old pattern spelled its own separator, so every spelling nobody thought
    of was not a quantity at all. Numerator and denominator are found independently now."""
    qs = mb.quantities(mb.flat(text), 26)
    assert len(qs) == 1 and qs[0].num == num and qs[0].den == 26


@pytest.mark.parametrize("text", [
    "AMD64 Family 26, AuthenticAMD",            # a model number, not a denominator
    "the effective sample size is far below 26 and no interval is informative",
    "a descriptive count of these 26 circuits",  # the population, with no numerator
    "reproduces bv_n140 at 22.59% against 26.28% from the contiguous run",
    "machine 2 | CPU | AMD64 Family 26",         # a number between two numbers
    "Version 5, 2026-09-17",                     # 26 is not a token inside 2026
])
def test_a_26_that_is_not_a_denominator_is_not_a_quantity(text):
    """The other side of failing closed: if every 26 were a claim, the pristine
    manuscript could not pass, and a checker that cries wolf gets switched off."""
    assert mb.quantities(mb.flat(text), 26) == []


# ---------------------------------------------------------------- V4-02

@pytest.mark.parametrize("bad,good", [("10.9", "99.9"), ("46.2", "64.2"),
                                      ("0.833", "0.933")])
def test_a_number_the_pdf_shows_and_the_source_lacks_is_rejected(paper, bad, good):
    """V4-02. The published PDF's abstract printed a transition width of 99.9 percentage
    points and all thirteen stages returned exit 0, because the checker only looked for
    strings it expected and an attack adds strings rather than removing them."""
    txt = mb.visible_text(paper).replace(bad, good)
    fails = pb.check(txt, paper, echo=lambda *a, **k: None)
    assert fails, f"{bad} -> {good} was accepted"
    assert "appears NOWHERE in PAPER.md" in reasons(fails)


def test_a_number_the_source_states_and_the_pdf_drops_is_rejected(paper):
    txt = mb.visible_text(paper).replace("10.9", "")
    fails = pb.check(txt, paper, echo=lambda *a, **k: None)
    assert "no page of the PDF carries it" in reasons(fails)


def test_the_source_text_itself_satisfies_its_own_binding(paper):
    """The control for the two above: a faithful rendering of the registered page must
    pass, or the rejections prove only that the comparison is over-strict.

    The stand-in for the PDF is the REGISTERED surface's own text, not
    `visible_text(paper)`: stage 13 now binds the artifact to the registry, and
    `visible_text` blanks fenced code blocks, which a real PDF renders.
    """
    import visible_surface as vs_
    rendered = "\n\n".join(e["text"] for e in vs_.load_ledger()["units"])
    assert pb.check(rendered, paper, echo=lambda *a, **k: None) == []


def test_canonical_rows_must_appear_together_not_merely_somewhere(paper):
    """Correct numbers attached to the wrong rows. Scrambling the fractions between rows
    leaves every value present in the document and every row false."""
    txt = mb.visible_text(paper)
    txt = (txt.replace("| 12 / 26 |", "| @A |").replace("| 7 / 26 |", "| @B |")
              .replace("| 4 / 26 |", "| @C |"))
    txt = txt.replace("| @A |", "| 4 / 26 |").replace("| @B |", "| 12 / 26 |") \
             .replace("| @C |", "| 7 / 26 |")
    fails = pb.check(txt, paper, echo=lambda *a, **k: None)
    assert fails and "does not appear as a row in the PDF" in reasons(fails)


def test_the_pdf_extractor_is_found_without_help_from_the_shells_path(monkeypatch):
    """Stage 13 passed under Git Bash and failed under PowerShell on the same file: one
    shell had /mingw64/bin on PATH and the other did not. A stage whose verdict depends
    on who invoked it is not checking the artifact. The requirement is declared instead."""
    monkeypatch.setenv("PATH", "")
    assert pb.find_pdftotext(), (
        "no extractor found with an empty PATH; PDFTOTEXT_CANDIDATES must name the "
        "usual install locations, and this machine has one at "
        r"C:\Program Files\Git\mingw64\bin\pdftotext.exe")


def test_a_missing_extractor_is_a_refusal_not_a_pass(monkeypatch):
    monkeypatch.setattr(pb, "find_pdftotext", lambda: None)
    monkeypatch.setitem(sys.modules, "fitz", None)
    with pytest.raises(SystemExit) as exc:
        pb.pdf_text()
    assert "STAGE 13 CANNOT RUN" in str(exc.value)


# ---------------------------------------------------------------- V4-07

def test_a_crash_is_not_scored_as_a_detection():
    """V4-07. `caught = {n for n, c in codes.items() if c}` credited any nonzero exit, so
    a fixture that broke an import would have counted as regression coverage."""
    import validation_result as v
    ok = f"  ✗ RAW EVIDENCE WAS EDITED\n{v.SENTINEL} REJECTED RAW_SELF_CONSISTENT\n"
    assert v.classify(1, ok, "") == (v.REJECTED, "RAW_SELF_CONSISTENT")
    assert v.classify(1, "", "Traceback (most recent call last):\n ImportError")[0] == v.ERROR
    assert v.classify(1, "  no publish/paper.pdf", "")[0] == v.ERROR
    assert v.classify(0, f"  ✓ fine\n{v.SENTINEL} PASSED\n", "")[0] == v.PASSED


def test_the_expected_diagnostic_followed_by_a_crash_is_an_error(tmp_path):
    """V4-07, round two (Astra, 3643bbc differential).

    Round one replaced "any nonzero exit" with "nonzero exit and a ✗ in the output".
    Astra then had a layer print its expected rejection diagnostic and raise afterwards:
    still nonzero, still contained ✗, still scored REJECTED, and the declared reason was
    present. A layer that fell over did not finish, so it cannot vouch for anything.

    This runs a real subprocess doing exactly that, and asserts the classifier is not
    fooled by it.
    """
    import subprocess
    import validation_result as v
    script = tmp_path / "diagnostic_then_crash.py"
    script.write_text("\n".join([
        "import sys",
        f"sys.path.insert(0, r'{ROOT}')",
        "import validation_result as vr",
        "print('  \\u2717 SAVED SUMMARY IS NOT A VALID ARTIFACT')",
        "print(\"      bv_n30.error_ci_lo: 'NaN' is not finite\")",
        "print(vr.SENTINEL + ' REJECTED SAVED_SCHEMA')",
        "raise RuntimeError('unrelated failure after the verdict was printed')",
    ]), encoding="utf-8")
    p = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert p.returncode != 0
    assert "✗" in p.stdout and "is not finite" in p.stdout          # the bait
    assert f"{v.SENTINEL} REJECTED" in p.stdout                     # and the verdict
    outcome, why = v.classify(p.returncode, p.stdout, p.stderr)
    assert outcome == v.ERROR, (
        "a layer that printed its verdict and then crashed was scored as a detection")
    assert "traceback" in why.lower()


def test_rejection_diagnostic_then_exit_23_is_an_error(tmp_path):
    """BLOCKER 2 (Astra, post-4d50a2b) — the exact reproducer.

    classify() accepted ANY nonzero status beside a REJECTED sentinel. Astra had a
    validator print its rejection diagnostic and then exit 23: nonzero, sentinel present,
    no traceback, scored REJECTED. "Nonzero" is a property shared by every abnormal death
    there is. reject() exits exactly REJECT_EXIT, so that is what a rejection looks like.
    """
    import subprocess
    import validation_result as v
    script = tmp_path / "diagnostic_then_exit_23.py"
    script.write_text("\n".join([
        "import os, sys",
        f"sys.path.insert(0, r'{ROOT}')",
        "import validation_result as vr",
        "print('  \\u2717 SAVED SUMMARY IS NOT A VALID ARTIFACT')",
        "print(\"      bv_n30.error_ci_lo: 'NaN' is not finite\")",
        "print(vr.SENTINEL + ' REJECTED SAVED_SCHEMA')",
        "sys.stdout.flush()",
        "os._exit(23)",
    ]), encoding="utf-8")
    p = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    assert p.returncode == 23
    assert f"{v.SENTINEL} REJECTED" in p.stdout        # the verdict really is there
    assert "Traceback" not in p.stderr                 # and there is no crash to spot
    outcome, why = v.classify(p.returncode, p.stdout, p.stderr)
    assert outcome == v.ERROR, "exit 23 beside a rejection verdict was scored REJECTED"
    assert "23" in why


@pytest.mark.parametrize("code", [2, 3, 23, 42, 127, 137, -1, 255])
def test_no_exit_status_but_the_contracts_own_counts_as_a_rejection(code):
    """Generic, not a patch for 23. Only the status reject() itself produces qualifies."""
    import validation_result as v
    out = f"  ✗ bad\n{v.SENTINEL} REJECTED SAVED_SCHEMA\n"
    assert v.classify(code, out, "")[0] == v.ERROR
    assert v.classify(v.REJECT_EXIT, out, "") == (v.REJECTED, "SAVED_SCHEMA")


def test_ordinary_rejections_and_passes_are_unaffected():
    """The repair must not turn real detections into errors."""
    import validation_result as v
    for inv in ("SAVED_SCHEMA", "VISIBLE_CLAIMS_MATCH_RAW", "PDF_MATCHES_MANUSCRIPT"):
        out = f"  ✗ something\n{v.SENTINEL} REJECTED {inv}\n"
        assert v.classify(v.REJECT_EXIT, out, "") == (v.REJECTED, inv)
    assert v.classify(v.PASS_EXIT, f"  ✓ ok\n{v.SENTINEL} PASSED\n", "")[0] == v.PASSED


def test_output_continuing_past_the_verdict_is_an_error():
    """The sentinel must be TERMINAL. Anything after it means the routine did not end
    where it said it did."""
    import validation_result as v
    out = f"  ✗ bad\n{v.SENTINEL} REJECTED SAVED_SCHEMA\nstill going\n"
    assert v.classify(1, out, "")[0] == v.ERROR


def test_a_verdict_disagreeing_with_the_exit_code_is_an_error():
    import validation_result as v
    assert v.classify(0, f"{v.SENTINEL} REJECTED X\n", "")[0] == v.ERROR
    assert v.classify(1, f"{v.SENTINEL} PASSED\n", "")[0] == v.ERROR


def test_a_stderr_warning_after_a_clean_pass_is_still_a_pass():
    """stdout and stderr must stay SEPARATE: concatenating them lets an ordinary
    warning land after the sentinel and read as a crash."""
    import validation_result as v
    assert v.classify(0, f"  ✓ ok\n{v.SENTINEL} PASSED\n",
                      "DeprecationWarning: something\n")[0] == v.PASSED


def test_every_layer_emits_a_terminal_verdict():
    """A layer with no verdict line can never be scored, so the contract has to hold for
    all of them, not just the ones a test happens to exercise."""
    import mutation_test as mt
    for name, script in mt.LAYERS.items():
        src = open(os.path.join(ROOT, script.split()[0]), encoding="utf-8").read()
        assert "validation_result" in src, f"{name} ({script}) has no terminal verdict"
        assert "vr.accept(" in src and "vr.reject(" in src, \
            f"{name} ({script}) does not both accept and reject through the contract"


def test_every_mutation_declares_an_invariant_and_a_reason():
    """Both, because they answer different questions: the invariant is structural and
    can only be produced by a completed validation routine; the fragment says which
    defect under that invariant was seen."""
    import mutation_test as mt
    ids = [m[0] for m in mt.MUTATIONS]
    assert len(ids) == len(set(ids)), "duplicate mutation id"
    for mid, label, fn, reasons_ in mt.MUTATIONS:
        assert reasons_, f"{mid} declares no required layer"
        for layer, declared in reasons_.items():
            assert layer in mt.LAYERS, f"{mid} names unknown layer {layer}"
            assert isinstance(declared, tuple) and len(declared) == 2, \
                f"{mid}/{layer} must declare (invariant, message fragment)"
            invariant, fragment = declared
            assert invariant.isupper() or "_" in invariant, \
                f"{mid}/{layer} invariant {invariant!r} is not an identifier"
            assert len(fragment) > 3, f"{mid}/{layer} has no usable reason string"


def _check_preserved_fixtures(mutations, tmp_path, monkeypatch):
    """Astra's fixtures are DEFINED, REGISTERED, still hostile, and still aimed.

    Four separate claims, because F-06 was a guard that made only the weakest of them.
    Each fixture is RUN against a copy of the manuscript and the text it must produce is
    compared against `ASTRA_FIXTURES` — a fixture softened into a paraphrase fails here,
    and so does one that is quietly dropped from the executed suite.

    Raises AssertionError, so the two tests below can call it with a pruned suite and
    require it to complain.
    """
    import mutation_test as mt
    monkeypatch.setattr(mt, "_rebuild_pdf", lambda *a, **k: 0)   # PDF rebuild, not content
    registered = {m[0]: m for m in mutations}
    for mid, (layer, must_contain) in mt.ASTRA_FIXTURES.items():
        assert mid in registered, \
            (f"{mid} is a preserved auditor reproducer and is NOT in the executed "
             f"mutation suite — removing it removes the coverage it stands for")
        _id, _label, fn, reasons_ = registered[mid]
        assert layer in reasons_, \
            f"{mid} no longer declares the {layer} layer it must be caught by"
        snap = tmp_path / mid
        snap.mkdir()
        (snap / "PAPER.md").write_text(open(PAPER, encoding="utf-8").read(),
                                       encoding="utf-8")
        fn(str(snap))
        got = (snap / "PAPER.md").read_text(encoding="utf-8")
        assert must_contain in got, \
            (f"{mid} no longer puts its hostile content in the manuscript: expected "
             f"{must_contain[:70]!r}")


def test_the_astra_reproducers_are_all_present_as_fixtures():
    """Every case Astra actually ran is a standing fixture, not a paraphrase of one."""
    import mutation_test as mt
    ids = {m[0] for m in mt.MUTATIONS}
    for mid in (mt.DEFEATED_V3 | mt.DEFEATED_V4 | mt.DEFEATED_V5 | mt.DEFEATED_V6
                | mt.DEFEATED_V7 | mt.DEFEATED_V8):
        assert mid in ids, f"mutation {mid} is declared defeated but is not defined"
    assert {"W", "X", "Y", "Z"} <= ids, "the 3643bbc differential cases are missing"
    assert set(mt.ASTRA_FIXTURES) <= ids, "a preserved reproducer left the suite"


def test_the_preserved_fixtures_are_registered_and_still_hostile(tmp_path, monkeypatch):
    """The control: against the real suite the guard is satisfied."""
    import mutation_test as mt
    _check_preserved_fixtures(mt.MUTATIONS, tmp_path, monkeypatch)


@pytest.mark.parametrize("dropped", ["AA", "AB", "AC", "AE", "AF", "AG", "AH", "W",
                                     "AJ", "AK", "AL", "AN", "AP", "AR", "AT",
                                     "AU", "AV"])
def test_removing_a_preserved_fixture_makes_the_guard_fail(dropped, tmp_path, monkeypatch):
    """F-06, and Astra's exact reproducer: remove AA and AB from MUTATIONS and run the
    supposed guard.

    The old guard looped over DEFEATED_V3 | V4 | V5 — sets that do not contain AA or AB —
    so deleting both left the tests green. A guard nobody can make fail is not evidence
    that anything is preserved; this one is required to complain about every id it names.
    """
    import mutation_test as mt
    pruned = [m for m in mt.MUTATIONS if m[0] != dropped]
    assert len(pruned) == len(mt.MUTATIONS) - 1
    with pytest.raises(AssertionError, match="NOT in the executed mutation suite"):
        _check_preserved_fixtures(pruned, tmp_path, monkeypatch)


def test_softening_a_fixture_into_a_paraphrase_makes_the_guard_fail(tmp_path, monkeypatch):
    """The other way a reproducer is lost: the id survives and the attack does not."""
    import mutation_test as mt

    def toothless(snap):
        p = os.path.join(snap, "PAPER.md")
        t = open(p, encoding="utf-8").read()
        open(p, "w", encoding="utf-8").write(
            t.replace("## Abstract", "## Abstract\n\nSeven of 26 eligible circuits.", 1))
        return "a paraphrase"

    pruned = [(m[0], m[1], toothless, m[3]) if m[0] == "AA" else m for m in mt.MUTATIONS]
    with pytest.raises(AssertionError, match="no longer puts its hostile content"):
        _check_preserved_fixtures(pruned, tmp_path, monkeypatch)


def test_every_mutation_that_edits_the_manuscript_declares_a_rendered_or_pdf_layer():
    """A source-level fixture caught by no reader-facing layer is coverage of nothing."""
    import mutation_test as mt
    for mid, (layer, _text) in mt.ASTRA_FIXTURES.items():
        assert layer in ("rendered", "pdf")


# ---------------------------------------------------------------- V4-09

def test_the_tie_band_is_documented_where_the_rule_is_stated():
    """V4-09. The guard was documented at the line that implements it, while the file
    header still said the pre-registered rule was implemented 'without deviation'."""
    import prereg_analysis as pa
    doc = pa.__doc__
    assert "TIE_EPS" in doc and "1e-9" in doc
    assert "without deviation" not in doc.lower()
    assert pa.TIE_EPS == 1e-9


def test_the_manuscript_states_the_tolerance_where_it_states_the_rule(paper):
    """V4-09, round two (Astra, 3643bbc differential). The code header disclosed the
    guard; PAPER.md still gave the entirely-above/entirely-below rule unqualified, and
    the manuscript is what a reader sees. This assertion exists so the disclosure cannot
    quietly disappear again."""
    import prereg_analysis as pa
    i = paper.find("A circuit is `REGRESSION` if that interval lies")
    assert i > 0, "the classification rule is no longer stated in these words"
    window = paper[i:i + 2500]
    assert "10⁻⁹" in window or "1e-9" in window or "1e-09" in window, \
        "the classification rule is stated without its numerical tolerance"
    assert f"{pa.TIE_EPS:g}".replace("1e-09", "10⁻⁹") or True
    assert "UNRESOLVED" in window and "tolerance" in window.lower()


# ---------------------------------------------------------------- NEW-BUILD-01

def _exclusive_handle(path):
    """A real Windows lock: CreateFileW with dwShareMode = 0, which is what a PDF viewer
    holds. Python's own open() shares read and write, so it locks nothing."""
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.CreateFileW.restype = wintypes.HANDLE
    k32.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD,
                                wintypes.HANDLE]
    h = k32.CreateFileW(str(path), 0x80000000, 0, None, 3, 0, None)   # GENERIC_READ
    return k32, h


@pytest.mark.skipif(sys.platform != "win32", reason="Windows file-locking semantics")
def test_a_locked_destination_never_reports_a_successful_build(tmp_path):
    """NEW-BUILD-01 (Astra, 3643bbc differential).

    Chromium printed straight to publish/paper.pdf. With that file locked it could not
    write, said so on stderr, and exited 0 — so the build script announced success over
    the top of the previous PDF and every downstream stage validated a stale artifact.
    Success must mean an artifact exists, not that a command returned.
    """
    import shutil
    import subprocess
    real = os.path.join(ROOT, "publish", "paper.pdf")
    if not os.path.isfile(real):
        pytest.skip("no built PDF to use as a fixture")
    dest = tmp_path / "dest.pdf"
    shutil.copy(real, dest)
    fresh = tmp_path / "fresh.pdf"
    fresh.write_bytes(dest.read_bytes() + b"\n%% a genuinely different build\n")
    before = dest.read_bytes()
    assert fresh.read_bytes() != before

    k32, h = _exclusive_handle(dest)
    assert h != -1 and h is not None, "could not take an exclusive handle"
    try:
        p = subprocess.run(
            [sys.executable, os.path.join(ROOT, "publish", "finalize_pdf.py"),
             str(fresh), str(dest)], capture_output=True, text=True,
            encoding="utf-8", errors="replace")
    finally:
        k32.CloseHandle(h)

    assert p.returncode != 0, "a locked destination reported a successful build"
    assert "Traceback" not in (p.stdout + p.stderr), \
        "it failed, but by crashing rather than by explaining"
    assert "COULD NOT PUBLISH" in (p.stdout + p.stderr)
    assert dest.read_bytes() == before, "the old PDF was corrupted by a failed publish"
    assert fresh.is_file(), "the fresh build was discarded and cannot be retried"

    # and once the lock is gone, the same call must publish
    p2 = subprocess.run(
        [sys.executable, os.path.join(ROOT, "publish", "finalize_pdf.py"),
         str(fresh), str(dest)], capture_output=True, text=True)
    assert p2.returncode == 0
    assert dest.read_bytes() != before


@pytest.mark.parametrize("make,expect", [
    (lambda p: p.write_bytes(b"%PDF-1.4\n" + b"x" * 100), "below the"),
    (lambda p: p.write_bytes(b"not a pdf at all" + b"x" * 100_000), "%PDF-"),
])
def test_a_bad_build_output_is_never_published(tmp_path, make, expect):
    import subprocess
    fresh = tmp_path / "fresh.pdf"
    make(fresh)
    dest = tmp_path / "dest.pdf"
    dest.write_bytes(b"previous build")
    p = subprocess.run(
        [sys.executable, os.path.join(ROOT, "publish", "finalize_pdf.py"),
         str(fresh), str(dest)], capture_output=True, text=True,
        encoding="utf-8", errors="replace")
    assert p.returncode != 0
    assert expect in (p.stdout + p.stderr)
    assert dest.read_bytes() == b"previous build"


# =================================================================== B1 (post-f125dfa)
#
# The independent adversarial audit wrote nine false reader-visible statements that the
# claim scan never instantiated as claims. Not one is a classification failure: the
# classifier fails closed, and was never asked. These are the auditor's sentences
# verbatim, and what refuses them is that nobody registered them — no recogniser reads a
# word of them.

import json                                                            # noqa: E402
import subprocess                                                      # noqa: E402

import visible_surface as vs                                           # noqa: E402

AUDIT_BYPASSES = {
    # the strongest reproducer: word-numbers on BOTH sides of the fraction
    "A1b word numerator and denominator":
        "Seven of the twenty-six eligible circuits have an interval that excludes zero.",
    "A3b numerator seven words away":
        "Of the 26 eligible circuits in the pre-registered set, only seven have an "
        "interval that excludes zero.",
    "B1 split across a relative clause":
        "The study resolves 26 eligible circuits, of which only seven have an interval "
        "that excludes zero.",
    "A2b a percentage, no denominator":
        "The primary risk interval excludes zero in just 27% of eligible circuits.",
    "A4 full-width digits":
        "The primary risk interval excludes zero in only ７ / ２６ eligible "
        "circuits.",
    "A5 a cross-reference inside the quantity":
        "The primary risk interval excludes zero in only seven (see §4.1) of the 26 "
        "eligible circuits.",
    "B8 Markdown emphasis around the numeral":
        "The primary risk interval excludes zero in only __7__ / 26 eligible circuits.",
    "B3 a qualitative quantifier":
        "Barely a quarter of the 26 eligible circuits have an interval that excludes "
        "zero.",
}
T8_ROW = "| Summary | seven of the twenty-six eligible circuits exclude zero | | |"
LAST_CANONICAL_ROW = "| risk ≥ 10% | 4 / 26 | 15.4% | [6.2, 33.5] |"


def _surface(doc):
    """The closed-world check exactly as stage 12 runs it, on a supplied document."""
    return vs.compare(vs.units(doc), vs.load_ledger())[0]


def _into_abstract(paper, sentence):
    out = paper.replace("## Abstract", "## Abstract\n\n" + sentence, 1)
    assert out != paper
    return out


@pytest.mark.parametrize("name", sorted(AUDIT_BYPASSES))
def test_an_unregistered_reader_visible_unit_is_refused(paper, name):
    """B1. Each of these returned 13/13 PASS and exit 0 against f125dfa."""
    fails = _surface(_into_abstract(paper, AUDIT_BYPASSES[name]))
    assert fails, f"{name!r} is still outside the validator's universe"
    assert "NOT REGISTERED in the manuscript surface" in reasons(fails)


def test_the_injected_table_row_in_word_numbers_is_refused(paper):
    """B1/T8. The row check has no label to recognise and the claim scan has no digits
    to read, so the row was invisible to both."""
    doc = paper.replace(LAST_CANONICAL_ROW, LAST_CANONICAL_ROW + "\n" + T8_ROW, 1)
    assert doc != paper
    fails = _surface(doc)
    assert fails and "NOT REGISTERED in the manuscript surface" in reasons(fails)
    assert "table_row" in reasons(fails)


@pytest.mark.parametrize("name", sorted(AUDIT_BYPASSES))
def test_the_claim_recogniser_still_cannot_see_these(paper, name):
    """The finding, kept as a standing fact rather than a memory.

    These are NOT caught by understanding them better. The recogniser is as blind to
    them today as it was at f125dfa, and that is the point: recall was moved off the
    security boundary instead of being widened again. If a later change makes this test
    fail, the recogniser grew — which is not forbidden, but it is not what protects the
    page, and this test is here so nobody mistakes the one for the other.
    """
    doc = _into_abstract(paper, AUDIT_BYPASSES[name])
    fails, _checked, _exempt = _scan(doc)
    assert fails == [], (f"{name!r} is now visible to the claim scan — fine, but the "
                         f"registry is still what refuses it")


def test_the_registry_is_not_rebuilt_during_verification():
    """B1/B2. A registry regenerated from the document it protects proves only that the
    document equals itself. The write path is a separate module, reached from one branch
    of one CLI flag, and nothing on the verification path imports it."""
    src = open(os.path.join(ROOT, "visible_surface.py"), encoding="utf-8").read()
    where = [ln for ln in src.splitlines() if "surface_dispositions" in ln]
    assert len(where) == 1 and where[0].strip().startswith("from surface_dispositions")
    body = src.split("if args.write:")[1].split("return")[0]
    assert "surface_dispositions" in body, "the import must sit inside --write"
    for mod in ("manuscript_binding.py", "pdf_binding.py"):
        text = open(os.path.join(ROOT, mod), encoding="utf-8").read()
        assert "surface_dispositions" not in text, f"{mod} can rebuild the registry"


def test_the_surface_parser_knows_nothing_about_claims():
    """B2. The universe must not be established by the machinery being tested. This is a
    structural fact about the file, so it is asserted as one."""
    import ast
    src = open(os.path.join(ROOT, "visible_surface.py"), encoding="utf-8").read()
    forbidden = {"quantities", "CLAIM_IDENTITIES", "WORD_NUM", "NUM_TOKEN",
                 "claim_inventory", "DISTRIBUTION_STATS", "manuscript_binding"}
    # the NAMES the code touches, not the words the prose uses -- the docstring says
    # "`quantities()` is not called here", and a grep cannot tell that from a call
    used = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute):
            used.add(node.attr)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            used.add(getattr(node, "module", "") or "")
            used |= {a.name for a in node.names}
    assert not (used & forbidden), f"the surface parser reaches for {used & forbidden}"


# =================================================================== B2 (post-f125dfa)

def test_the_reader_visible_universe_is_completely_registered(paper):
    """B2. Coverage measured against a universe the claim recogniser did not produce.

    The old disposition test started from `quantities()` and proved every object it
    returned had been classified — which is true of an empty set. The universe here is
    the Markdown block structure of the page; `test_the_surface_parser_knows_nothing_
    about_claims` is what makes that claim checkable rather than asserted.
    """
    doc_units = vs.units(paper)
    fails, tally, entries = vs.compare(doc_units, vs.load_ledger())
    print(f"\n  protected visible units = {len(doc_units)}")
    for k in vs.DISPOSITIONS:
        print(f"    {k:<18}{tally.get(k, 0)}")
    print(f"    {'UNKNOWN':<18}{tally.get('UNKNOWN', 0)}")
    assert fails == []
    assert tally["UNKNOWN"] == 0
    assert sum(tally.get(k, 0) for k in vs.DISPOSITIONS) == len(doc_units)
    assert tally["BOUND"] and tally["CANONICAL"] and tally["PINNED_EXEMPTION"]


def test_every_release_critical_identity_has_a_registered_home(paper):
    """The other half of coverage: nothing declared has fallen off the page."""
    entries = vs.load_ledger()["units"]
    homes = vs.registered_claims(entries)
    unbound = [k for k in mb.RELEASE_IDENTITIES if k not in homes]
    print(f"\n  release-critical quantitative identities = "
          f"{len(mb.RELEASE_IDENTITIES)}")
    print(f"    bound   = {len(mb.RELEASE_IDENTITIES) - len(unbound)}")
    print(f"    unbound = {len(unbound)}")
    assert unbound == []
    assert len(mb.RELEASE_IDENTITIES) == 9


NEGATIVE_CONTROLS = {
    "no ASCII digit anywhere":
        "A minority of the eligible circuits carry a risk interval that is "
        "distinguishable from nothing at all.",
    "no slash and no digit":
        "Barely a quarter of them exclude zero, and the deterministic ones do not.",
    "no recognised predicate vocabulary":
        "The headline figure of this study sits entirely to the right of the origin for "
        "seven circuits.",
}


@pytest.mark.parametrize("name", sorted(NEGATIVE_CONTROLS))
def test_an_arbitrary_sentence_changes_the_universe_and_is_refused(paper, name):
    """B2's required negative controls. The inventory itself must move."""
    sentence = NEGATIVE_CONTROLS[name]
    assert not any(c.isdigit() for c in sentence) or "/" not in sentence
    doc = _into_abstract(paper, sentence)
    before, after = vs.units(paper), vs.units(doc)
    assert len(after) == len(before) + 1, "the universe did not change"
    fails = _surface(doc)
    assert fails and "NOT REGISTERED in the manuscript surface" in reasons(fails)


def test_the_headline_reproducer_moves_the_inventory_before_anything_reads_it(paper):
    """B2, named explicitly in the brief: this exact sentence must change the surface
    inventory and fail there, not in a lexical recogniser."""
    doc = _into_abstract(paper, AUDIT_BYPASSES["A1b word numerator and denominator"])
    assert len(vs.units(doc)) == len(vs.units(paper)) + 1
    assert _surface(doc)
    assert _scan(doc)[0] == [], "the claim recogniser is not what caught it"


def test_editing_a_unit_in_place_changes_its_identity(paper):
    """Insertion is one way in; alteration is the other. A unit that is edited is a unit
    the registry does not know, whatever the edit was."""
    doc = paper.replace("### 4.2 Magnitude", "### 4.2 Magnitude (seven of twenty-six)", 1)
    assert doc != paper and len(vs.units(doc)) == len(vs.units(paper))
    fails = _surface(doc)
    assert fails and "heading" in reasons(fails)


def test_a_registry_entry_must_hash_its_own_text():
    """The registry is self-verifying, so hand-editing one entry's text is caught."""
    ledger = json.loads(json.dumps(vs.load_ledger()))
    ledger["units"][5]["text"] = ledger["units"][5]["text"] + " and one more thing"
    fails, _tally, _entries = vs.compare(vs.units(open(PAPER, encoding="utf-8").read()),
                                         ledger)
    assert fails and "does not hash its own text" in reasons(fails)


def test_a_missing_registry_is_a_refusal_not_a_pass():
    """No registry means nothing is known about the page, which is not the same as
    nothing being wrong with it."""
    fails, _tally, _entries = vs.compare(vs.units("# x\n\nhello\n"), None)
    assert fails and "never been registered" in reasons(fails)


# =================================================================== B3 (post-f125dfa)

_STATS = {}


def _stats():
    """Reconstructed once per session: `reconstruct` is twenty seconds a call."""
    if not _STATS:
        _STATS.update(mb.distribution_from_raw())
    return dict(_STATS)


def test_the_distribution_statistics_are_reconstructed_from_raw():
    """B3. Four scientific assertions over the eligible population that had no
    disposition: they carry no `n / 26`, so the claim scan never saw them."""
    stats = _stats()
    print(f"\n  median {stats['dist_median']:.4f}  p75 {stats['dist_p75']:.4f}  "
          f"p90 {stats['dist_p90']:.4f}  max {stats['dist_max']:.4f}")
    assert round(stats["dist_median"], 1) == 0.0
    assert round(stats["dist_p75"], 1) == 6.9
    assert round(stats["dist_p90"], 1) == 14.2
    assert round(stats["dist_max"], 1) == 17.3


DISTRIBUTION = "**median 0**, p75 = 6.9%, p90 = 14.2%, max = 17.3%."

DISTRIBUTION_ATTACKS = {
    # the auditor's A8 reproducer
    "A8 permutation": "**median 0**, p75 = 14.2%, p90 = 17.3%, max = 17.3%.",
    "p75 and p90 swapped": "**median 0**, p75 = 14.2%, p90 = 6.9%, max = 17.3%.",
    # 26.9 is the canonical table's own proportion -- and the substring that satisfied a
    # presence check for 6.9
    "p75 replaced by 26.9": "**median 0**, p75 = 26.9%, p90 = 14.2%, max = 17.3%.",
    "max replaced by 46.2": "**median 0**, p75 = 6.9%, p90 = 14.2%, max = 46.2%.",
    "median replaced by 15.4": "**median 15.4**, p75 = 6.9%, p90 = 14.2%, max = 17.3%.",
}


@pytest.mark.parametrize("name", sorted(DISTRIBUTION_ATTACKS))
def test_a_false_distribution_statistic_is_bound_and_rejected(paper, name):
    """Every replacement value here already appears elsewhere in the manuscript, so the
    document's numeric token set stays compatible and nothing downstream notices."""
    doc = paper.replace(DISTRIBUTION, DISTRIBUTION_ATTACKS[name], 1)
    assert doc != paper
    stats = _stats()
    fails, bound = mb.distribution_failures(vs.units(doc), stats)
    assert fails, f"{name!r} was accepted"
    assert "which the raw data puts at" in reasons(fails)


def test_the_pristine_distribution_sentence_binds(paper):
    """The control."""
    fails, bound = mb.distribution_failures(vs.units(paper), _stats())
    assert fails == [] and bound == 4


def test_six_point_nine_is_not_satisfied_by_twenty_six_point_nine():
    """B3, named in the brief. `"6.9" in PAPER` is true of the canonical table's own
    "26.9%", so a presence check could pass while the figure was absent entirely."""
    import re
    haystack = "| risk ≥ 5% | 7 / 26 | 26.9% | [13.7, 46.1] |"
    assert "6.9" in haystack, "the substring really is there"
    token = re.compile(r"(?<![\d.])" + re.escape("6.9") + r"(?![\d.]*\d)")
    assert not token.search(haystack), "the token form must not match inside 26.9"
    assert token.search("p75 = 6.9%, p90")


def test_paper_check_uses_the_token_form_not_a_substring():
    """The same repair where the audit found it."""
    src = open(os.path.join(ROOT, "paper_check.py"), encoding="utf-8").read()
    assert "present, scope = s in PAPER" not in src
    assert "present = s in PAPER[i:i + window]" not in src
    assert "token = re.compile(" in src


def test_the_distribution_must_be_stated_exactly_once(paper):
    """Zero means the claim has left the page; two means the document says it twice and
    which one a reader believes is not decidable."""
    stats = _stats()
    doubled = paper.replace(DISTRIBUTION, DISTRIBUTION + "\n\n" + DISTRIBUTION, 1)
    fails, _bound = mb.distribution_failures(vs.units(doubled), stats)
    assert fails and "exactly one must" in reasons(fails)
    gone = paper.replace(DISTRIBUTION, "The distribution is described in §4.2.", 1)
    fails, _bound = mb.distribution_failures(vs.units(gone), stats)
    assert fails and "exactly one must" in reasons(fails)


# ============================================ the mutation execution contract

def test_a_required_fixture_that_cannot_be_built_fails_the_suite():
    """A fixture that was never built did not test anything, so the suite cannot certify
    anything — but it exited 0 while printing that it had not run, which is the V4-07
    defect in its third costume. Missing pandoc must never leave stage 9 green.

    This runs the real suite with the tools hidden, so it tests the contract rather than
    a description of it.
    """
    code = (
        "import sys; sys.path.insert(0, r'%s');"
        "import mutation_test as mt;"
        "mt.shutil.which = lambda *a, **k: None;"
        "mt.CHROME = [];"
        "sys.argv = ['mutation_test.py', '--only', 'AK'];"
        "mt.main()" % ROOT)
    p = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True,
                       text=True, timeout=900)
    assert p.returncode != 0, "a skipped required mutation left the suite green"
    assert "NOT EXERCISED" in p.stdout
    assert "execution\n    failure" in p.stdout or "execution failure" in p.stdout
    # and it must NOT be scored as a detection
    assert "REJECTED" not in p.stdout.split("NOT EXERCISED")[1][:400]


def test_a_skipped_fixture_is_never_counted_as_a_rejection():
    """The classification half of the same contract, stated where it is decided."""
    src = open(os.path.join(ROOT, "mutation_test.py"), encoding="utf-8").read()
    body = src.split("if skipped:")[1].split("if failures:")[0]
    code = "\n".join(ln for ln in body.splitlines() if not ln.strip().startswith("#"))
    assert "failures.append" in code, "a skipped fixture must fail the suite"
    # the CODE, not the comment that explains why: the block says out loud that a skip
    # never becomes a REJECTED, and the assertion has to be about what it does
    assert "REJECTED" not in code, "a skipped fixture must not be scored as a detection"
    assert "results.append" not in code, "a skipped fixture must not join the results"
