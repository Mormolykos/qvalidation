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


def test_quantity_is_bound_to_the_endpoint_its_own_sentence_names():
    """V4-03. 7 of 26 is TRUE of 'risk >= 5%' and FALSE of 'excludes zero'. Checking a
    numerator against the set of true numerators cannot tell those apart; Astra put the
    false attribution in the abstract, where a paragraph-level exemption for the word
    'withdrawn' had already excused the whole block."""
    from manuscript_binding import CLAIM_PHRASES, WORD_NUM, QUANTITY
    m = QUANTITY.search("Seven of 26 eligible circuits have a risk interval that "
                        "excludes zero.")
    assert m, "the word-numeral form must be recognised as a quantity"
    assert WORD_NUM[m.group(1).lower()] == 7 and int(m.group(2)) == 26
    assert "excludes zero" in CLAIM_PHRASES["excl"]


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
    """The control for the two above: PAPER.md's own visible text must pass, or the
    rejections prove only that the comparison is over-strict."""
    assert pb.check(mb.visible_text(paper), paper, echo=lambda *a, **k: None) == []


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
    """V4-07. `caught = {n for n, c in codes.items() if c}` credits any nonzero exit, so
    a fixture that broke an import would have counted as regression coverage."""
    import mutation_test as mt
    assert mt.classify(1, "  ✗ RAW EVIDENCE WAS EDITED\n") == mt.REJECTED
    assert mt.classify(1, "Traceback (most recent call last):\n  ImportError") == mt.ERROR
    assert mt.classify(1, "  no publish/paper.pdf — run build_paper.sh first") == mt.ERROR
    assert mt.classify(0, "  ✓ fine") == mt.PASSED


def test_every_mutation_declares_the_reason_it_must_be_rejected_for():
    import mutation_test as mt
    for mid, label, fn, reasons_ in mt.MUTATIONS:
        assert reasons_, f"{mid} declares no required layer"
        for layer, why in reasons_.items():
            assert layer in mt.LAYERS, f"{mid} names unknown layer {layer}"
            assert why and len(why) > 3, f"{mid}/{layer} has no usable reason string"


# ---------------------------------------------------------------- V4-09

def test_the_tie_band_is_documented_where_the_rule_is_stated():
    """V4-09. The guard was documented at the line that implements it, while the file
    header still said the pre-registered rule was implemented 'without deviation'."""
    import prereg_analysis as pa
    doc = pa.__doc__
    assert "TIE_EPS" in doc and "1e-9" in doc
    assert "without deviation" not in doc.lower()
    assert pa.TIE_EPS == 1e-9
