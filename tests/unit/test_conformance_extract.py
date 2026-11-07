"""Requirement candidates: what `rmf conformance extract` reads from a document and how the
register keeps reviewed fields, IDs and removed statements across re-extraction. Recall and
noise against hand-read pages are in test_conformance_recall.py."""

import copy

import pytest
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool.conformance import extract, register
from rmf_tool.conformance.extract import Item

DODI = (REPO_ROOT / "references/text/DODI8510.01.md").read_text(encoding="utf-8")
TEXT = """\
<!-- page 1 -->

2.1. PROGRAM MANAGER.

a. Decisions.

The PM:

b. Develops the plan.

c. The AOs must:

(1) Only be government personnel.

(2) Possess relevant expertise with the leveraged technology and this must be a
factor in their

<!-- page 2 -->

selection.

3. Unrelated paragraph that states nothing binding.

Nothing here binds anyone. The system will be registered. The sky is blue.

12 A footnote about nothing at all.

| Task | Outcome |
| --- | --- |
| P-1 Roles | Roles are assigned |
"""


def items(text=TEXT, pages=(1, 2), **kwargs):
    return extract.statement_items(extract.blocks(text), pages, **kwargs).items


def rejected(text=TEXT, pages=(1, 2), **kwargs):
    return extract.statement_items(extract.blocks(text), pages, **kwargs).rejected


def statements(text=TEXT, **kwargs):
    return [i.statement for i in items(text, **kwargs)]


def test_a_paragraph_continues_over_a_page_break_and_a_plain_footnote_states_nothing():
    found = statements()

    assert ("(2) Possess relevant expertise with the leveraged technology and this must be a "
            "factor in their selection.") in found
    assert not any("footnote" in s for s in found)


def test_lettered_items_carry_their_path_and_lead_in():
    by_start = {i.statement[:3]: i for i in items()}

    assert by_start["b. "].locator == "2.1.b"
    assert by_start["(1)"].locator == "2.1.c.(1)"
    assert by_start["(1)"].context == "PROGRAM MANAGER The AOs must:"
    assert by_start["(1)"].kind == "lettered"


def test_a_run_in_heading_and_a_short_lead_in_are_context_and_recorded_as_rejected():
    """The fake: 485 short labels were dropped with no record (`continue`), among them the
    enumerated contents of the authorization package."""
    found = statements()
    reasons = {r.text: r.reason for r in rejected()}

    assert "a. Decisions." not in found
    assert "c. The AOs must:" not in found
    assert reasons["a. Decisions."] == "label-only"
    assert reasons["c. The AOs must:"] == "lead-in"


def test_a_short_label_under_a_lead_in_that_enumerates_is_an_item():
    """SP 800-37r2 p159: `The authorization package includes the following:` then
    `• Executive summary;` (WI-11); DoDI 8510.01 p7: `integration between:` then
    `(2) Systems Engineering.`"""
    text = ("<!-- page 1 -->\n\nThe authorization package includes the following:\n\n"
            "• Executive summary;\n\n• Security and privacy plans;\n\nThe package is sent.\n\n"
            "• Terms;\n\na. Coordinates for consistent integration between:\n\n"
            "(1) The RMF policies.\n\n(2) Systems Engineering.\n\n(3) Developmental test.\n")

    found = statements(text, pages=(1, 1))
    reasons = {r.text: r.reason for r in rejected(text, pages=(1, 1))}

    assert "• Executive summary;" in found
    assert "• Security and privacy plans;" in found
    assert "(2) Systems Engineering." in found
    assert reasons["• Terms;"] == "label-only", "the plain paragraph ended the enumeration"


def test_a_lettered_item_that_is_a_noun_phrase_is_kept():
    """`(b) Participation in the RMF TAG` was dropped as a run-in heading; four title-case
    words or fewer with a period is a heading, anything longer is an item."""
    text = ("<!-- page 1 -->\n\n(a) Membership.\n\n(b) Participation in the RMF TAG.\n\n"
            "c. System Threat Analysis.\n\n(b)Validated online lifecycle threat reports.\n")

    found = statements(text, pages=(1, 1))

    assert found == ["(b) Participation in the RMF TAG.",
                     "(b)Validated online lifecycle threat reports."]


def test_a_paragraph_with_a_requirement_sentence_enters_whole_with_its_strongest_kind():
    """The prose unit is the paragraph: a reviewer reads the sentences around the one the
    regexes matched, so a sentence they miss cannot vanish."""
    kinds = {i.statement: i.kind for i in items() if i.kind not in ("lettered", "table")}

    assert kinds == {"Nothing here binds anyone. The system will be registered. The sky is "
                     "blue.": "modal"}


def test_a_paragraph_no_sentence_of_which_reads_as_a_requirement_is_recorded_as_rejected():
    found = {(r.reason, r.text) for r in rejected()}

    assert ("no-marker", "A footnote about nothing at all.") in found
    assert ("short", "The PM:") not in found  # a lead-in with a list body is context
    assert all(r.reason in extract.REJECT_REASONS for r in rejected())


@pytest.mark.parametrize("text, kind, reason", [
    ("The AO must approve. For example, a server may host several applications.", "modal", ""),
    ("Risk tolerance is the degree of uncertainty that is acceptable. The sky is blue.",
     None, "no-marker"),
    ("For example, the AO must approve the plan.", None, "not-normative"),
    ("Monitoring Strategy", None, "short"),
    ("The LSE, working for the PM, does the following:", None, "lead-in"),
    # a lead-in that carries the obligation enters; its list is context for what follows
    ("The PM will also dedicate program resources to the following by monitoring:", "modal", ""),
    ("AOs should be appointed from senior leadership. The AO renders the decision.",
     "indicative", ""),
])
def test_paragraph_kind_is_the_strongest_sentence_or_a_reason(text, kind, reason):
    assert extract.paragraph_kind(text) == (kind, reason)


@pytest.mark.parametrize("sentence, kind", [
    ("The authorizing official or designated representative, in collaboration with the senior "
     "agency official for privacy, common control provider, and finalizes the determination "
     "of risk.", "indicative"),
    ("A type authorization159 is an official authorization decision.", "indicative"),
    ("The RMF process described in this issuance is in accordance with NIST SP 800-37.",
     "modal"),
    ("DoD adopts the NIST RMF for DoD IT.", "indicative"),
    ("Product assessments are typically conducted by third parties.", "indicative"),
])
def test_role_lists_footnote_marks_and_accordance_are_read(sentence, kind):
    assert extract.classify(sentence) == kind


def test_a_footnote_mark_glued_to_a_period_still_ends_the_sentence():
    assert extract.sentences("The AO selects controls.60 This is binding. See section 3.2 for "
                             "more.") == ["The AO selects controls.60", "This is binding.",
                                          "See section 3.2 for more."]


def test_wrapped_table_cells_are_joined_into_their_row():
    text = ("<!-- page 1 -->\n\n| Step | Action |\n| --- | --- |\n"
            "| Eradicate | replacing compromised files with |\n|  | clean versions, installing "
            "patches, changing |\n|  | passwords. |\n| Recover | restore systems |\n")

    rows = [i.statement for i in items(text, pages=(1, 1)) if i.kind == "table"]

    assert rows == ["Eradicate | replacing compromised files with clean versions, installing "
                    "patches, changing passwords.", "Recover | restore systems"]


def test_a_table_row_under_three_words_is_rejected_as_a_fragment():
    text = "<!-- page 1 -->\n\n| A | B |\n| --- | --- |\n| x | y |\n"

    assert [(r.reason, r.text) for r in rejected(text, pages=(1, 1))] == [("fragment", "x | y")]


def test_figure_text_in_caps_keeps_the_section_number():
    text = ("<!-- page 1 -->\n\n## 2.3 RISK MANAGEMENT\n\nFigure 2 shows the cycle.\n\n"
            "RESPOND MONITOR\n\nOrganizations must respond to risk.\n")

    found = items(text, pages=(1, 1))

    assert [(i.locator, i.context) for i in found] == [("2.3", "RESPOND MONITOR")]


def test_dod_labels_nest_a_then_1_then_a_then_1():
    text = ("<!-- page 1 -->\n\n## 3.1 DUTIES\n\na. The PM will do the first thing.\n\n"
            "(1) The PM will do the second thing.\n\n(a) The PM will do the third thing.\n\n"
            "1. The PM will do the fourth thing.\n\n(b) The PM will do the fifth thing.\n")

    assert [i.locator for i in items(text, pages=(1, 1))] == [
        "3.1.a", "3.1.a.(1)", "3.1.a.(1).(a)", "3.1.a.(1).(a).1", "3.1.a.(1).(b)"]


def test_sp_800_160_activity_tasks_are_lettered_items_under_their_activity():
    text = ("<!-- page 1 -->\n\nVA-2\n\nPERFORM VALIDATION\n\nVA-2.1 Define the security aspects "
            "of the validation procedures.\n\nNote: This includes the methods.\n\n"
            "VA-2.2 Perform security validation procedures.\n")

    found = items(text, pages=(1, 1))

    assert [(i.kind, i.locator) for i in found] == [("lettered", "VA-2.1"), ("lettered", "VA-2.2")]
    assert found[0].context == "PERFORM VALIDATION"


@pytest.mark.parametrize("sentence, kind", [
    ("The authorizing official must approve the plan.", "modal"),
    ("Controls may not be tailored out due to inability to satisfy a control.", "modal"),
    ("The value of not applicable cannot be assigned to any security objective.", "modal"),
    ("The CISO is responsible for assessing quality.", "modal"),
    ("Contractors are required to report incidents within one hour.", "modal"),
    ("An ATU requires a completed ATO by the provider.", "modal"),
    ("AOs should be appointed from senior leadership positions.", "should"),
    ("Privacy controls may be assessed by an independent assessor.", "should"),
    ("The adoption of an approved software platform is critical.", "should"),
    ("Control assessors prepare security and privacy assessment reports.", "indicative"),
    ("Privacy plans are made available to system owners.", "indicative"),
    ("The authorization package includes an executive summary.", "indicative"),
    ("The guidance in this issuance applies to both paths equally.", "indicative"),
    ("Track the assessment and authorization status of systems.", "imperative"),
    ("Review monitoring results to determine security status.", "imperative"),
    ("Risk tolerance is the degree of uncertainty that is acceptable.", None),
    ("For example, a server may host several applications.", None),
    ("The sky is blue.", None),
    ("Organizations prioritize deficiencies using information from risk assessments:",
     "indicative"),
    ("Risk response consists of the following:", None),
])
def test_classify_tells_obligations_recommendations_and_descriptions_apart(sentence, kind):
    assert extract.classify(sentence) == kind


def test_headings_are_context_and_never_statements():
    """The fake: 617 bare headings were entries, and mixed-case headings were skipped while
    figure labels entered."""
    text = ("<!-- page 1 -->\n\n### Denial of Authorization\n\nAUTHORIZATION\n\nTO OPERATE\n\n"
            "## FIGURE F-1: TYPES OF AUTHORIZATION DECISIONS\n\n"
            "If the risk is unacceptable, the authorization is not granted.\n")

    found = items(text, pages=(1, 1))

    assert [i.statement for i in found] == ["If the risk is unacceptable, the authorization is "
                                            "not granted."]
    assert found[0].context == "FIGURE F-1: TYPES OF AUTHORIZATION DECISIONS"


def test_a_bullet_the_extraction_tagged_as_a_heading_is_an_item():
    text = ("<!-- page 1 -->\n\nThere are four types:\n\n## • Common control authorization;\n\n"
            "• Authorization to use; and\n")

    found = items(text, pages=(1, 1))

    assert [i.statement for i in found] == ["• Common control authorization;",
                                            "• Authorization to use; and"]
    assert found[0].context == "There are four types:"


def test_a_footnote_neither_blocks_a_page_break_rejoin_nor_hides_its_own_requirement():
    """CNSSI 1253 page 11: `must be` ends the page, two footnotes follow (one tagged as a
    heading), and the sentence continues on page 12."""
    text = ("<!-- page 11 -->\n\nAll decisions must be\n\n17 Processing PII is defined by NIST.\n\n"
            "# 18 For additional guidance, see NIST SP 800-53B.\n\n<!-- page 12 -->\n\n"
            "documented in the system security plan.\n\n"
            "135 If changes are made, system security plans are updated accordingly.\n")

    found = items(text, pages=(11, 12))

    assert [i.statement for i in found] == [
        "All decisions must be documented in the system security plan.",
        "If changes are made, system security plans are updated accordingly."]
    assert found[0].page == 11 and found[1].page == 12


def test_a_footnote_glued_to_a_paragraph_is_split_off():
    text = ("<!-- page 1 -->\n\nThe senior agency official for privacy\n118 Providers are listed "
            "in the glossary.\n\n<!-- page 2 -->\n\nhas oversight responsibility for "
            "common controls.\n")

    found = statements(text, pages=(1, 2))

    assert found == ["The senior agency official for privacy has oversight responsibility for "
                     "common controls."]


def test_a_lead_in_is_context_and_its_body_paragraph_is_the_statement():
    """FIPS 199: `The generalized format ... is:` followed by the formula."""
    text = ("<!-- page 1 -->\n\nThe generalized format for expressing the security category is:\n\n"
            "SC = {(confidentiality, impact)}, where the acceptable values are LOW or HIGH.\n\n"
            "Organizations must document it.\n")

    found = items(text, pages=(1, 1))

    assert [(i.kind, i.statement[:14]) for i in found] == [("indicative", "SC = {(confide"),
                                                           ("modal", "Organizations ")]
    assert found[0].context == "The generalized format for expressing the security category is:"


def test_pin_mode_skips_the_task_fields_and_reads_the_discussion():
    text = ("<!-- page 1 -->\n\n### TASK P-3\n\nAssess organization-wide security risk.\n\n"
            "Potential Inputs: Risk management strategy; the AO must read it.\n\n"
            "Expected Outputs: Risk assessment results.\n\n"
            "Discussion: The organization considers the totality of risk. The AO must act.\n")

    found = items(text, pages=(1, 1), skip_labels=register.PIN_SKIP_LABELS,
                  strip_labels=register.PIN_STRIP_LABELS)

    assert [i.statement for i in found] == [
        "Assess organization-wide security risk.",
        "The organization considers the totality of risk. The AO must act."]
    assert {i.locator for i in found} == {"TASK P-3"}, "an unnumbered heading is the locator"


def test_a_table_row_is_a_statement_and_its_header_is_not():
    rows = [i.statement for i in items() if i.kind == "table"]

    assert rows == ["P-1 Roles | Roles are assigned"]
    assert not [i for i in items(tables=False) if i.kind == "table"]


def test_a_modal_sentence_list_stays_whole():
    assert extract.sentences("Organizations must: (i) limit access; and (ii) protect media.") == [
        "Organizations must: (i) limit access; and (ii) protect media."]
    assert extract.sentences("See e.g. the plan. It will hold.") == [
        "See e.g. the plan.", "It will hold."]


def test_anchors_grow_until_unique_and_stay_on_the_cited_page():
    shared = "one two three four five six seven eight nine ten eleven twelve"
    first = Item("modal", 1, f"{shared} thirteen alpha", "", "")
    second = Item("modal", 1, f"{shared} thirteen beta", "", "")
    pages = {1: extract.compact(f"{first.statement} {second.statement}")}

    anchored = extract.identify([first, second], pages)

    assert [i.anchor for i in anchored] == [first.statement, second.statement]


def test_an_anchor_never_runs_past_the_page_a_statement_starts_on():
    item = Item("lettered", 1, "a. Opening words then the rest", "", "")
    pages = {1: extract.compact("Opening words"), 2: extract.compact("then the rest")}

    assert extract.identify([item], pages)[0].anchor == "Opening words"


def test_identical_statements_are_told_apart_by_occurrence():
    pages = {1: "same"}
    anchored = extract.identify([Item("modal", 1, "SAME", "", ""),
                                 Item("modal", 1, "SAME", "", "")], pages)

    assert [i.occurrence for i in anchored] == [1, 2]


def test_dodi_8510_lettered_items_are_read_with_their_paragraph_numbers():
    found = extract.extract(DODI, [{"pages": [4, 31]}]).items
    lettered = [i for i in found if i.kind == "lettered"]
    risk = next(i for i in found if "most severe threat" in i.statement)

    assert len(lettered) >= 168
    assert risk.locator == "3.3.a.(3)" and risk.page == 20
    assert all(i.anchor and "ACRONYM" not in i.statement for i in found)
    assert not any(i.statement.isupper() for i in found if i.kind != "table")


def test_page_count_reads_the_last_marker():
    assert extract.page_count("<!-- page 1 -->\nx\n<!-- page 7 -->\ny\n") == 7


# --- reconcile ---------------------------------------------------------------------------


def test_a_sentence_ending_in_a_glued_footnote_mark_is_not_joined_over_the_page_break():
    """`...risk of loss.26` ends its paragraph; the next page opens a new one."""
    text = ("<!-- page 1 -->\n\nThe AO must weigh the risk of loss.26\n\n<!-- page 2 -->\n\n"
            "The AO must sign the decision.\n")

    assert statements(text) == ["The AO must weigh the risk of loss.26",
                                "The AO must sign the decision."]


def test_a_caption_on_the_next_page_is_context_and_never_joined():
    text = ("<!-- page 1 -->\n\nThe figure below shows the types of\n\n<!-- page 2 -->\n\n"
            "FIGURE 3: TYPES OF DECISIONS\n\nThe risk must be acceptable.\n\n"
            "## Table 2-1: Summary of Tasks\n\nThe SO must prepare the plan.\n")

    found = items(text)

    assert [i.statement for i in found] == ["The risk must be acceptable.",
                                            "The SO must prepare the plan."]
    assert [i.context for i in found] == ["FIGURE 3: TYPES OF DECISIONS",
                                          "Table 2-1: Summary of Tasks"]
    assert [r.text for r in rejected(text)] == ["The figure below shows the types of"]


def test_a_footnote_is_located_outside_the_bullet_it_follows():
    text = ("<!-- page 1 -->\n\n1.2. SCOPE.\n\n• The AO must sign the decision.\n\n"
            "12 The AO must also date it.\n")

    found = {i.statement: i.locator for i in items(text, pages=(1, 1))}

    assert found == {"• The AO must sign the decision.": "1.2.•",
                     "The AO must also date it.": "1.2"}


def test_a_parenthetical_between_subject_and_verb_is_read():
    """A false reject of the p10 review. Its two companions (`was established`, `contingency
    planning`) stay misses in the recall set: the regexes written to hit them matched 23 noise
    sentences for 3 hits, so they were removed (test_conformance_recall.py)."""
    sentence = ("Security or privacy architects, in coordination with system security or privacy "
                "officers, advise authorizing officials on the allocation of controls.")

    assert extract.classify(sentence) == "indicative"


def test_a_caption_with_no_blank_line_after_it_does_not_swallow_the_paragraph():
    """SP 800-18r1 page 11 and 1,295 words in nine blocks elsewhere: the caption and the body
    text under it were one paragraph, matched as a caption and dropped with no record. A
    wrapped caption (its next line opens in lowercase) stays one caption."""
    text = ("<!-- page 1 -->\n\nFigure 1: Security Planning Process Inputs/Outputs\n"
            "Inputs flow from the left and outputs to the right.\n\n"
            "Table 2. Supply chain characteristics associated with a product or source\n"
            "of supply28\n\nThe AO must sign.\n")

    found = extract.statement_items(extract.blocks(text), (1, 1))

    assert [i.statement for i in found.items] == ["The AO must sign."]
    assert [r.text for r in found.rejected] == ["Inputs flow from the left and outputs to the "
                                                "right."]
    assert found.items[0].context == "Table 2. Supply chain characteristics associated with a " \
                                     "product or source of supply28"


def test_a_caption_or_a_contents_line_never_continues_onto_the_next_page():
    """SP 800-37r2 page 25: `FIGURE 1: ...` has no closing punctuation, so the first paragraph
    of page 26 was joined to it and dropped as a caption. SP 800-18r1 page 6: a contents line
    with dot leaders did the same to the Executive Summary."""
    text = ("<!-- page 1 -->\n\nFIGURE 1: ORGANIZATION-WIDE RISK MANAGEMENT APPROACH\n\n"
            "<!-- page 2 -->\n\nThe activities at Levels 1 and 2 must prepare the organization.\n\n"
            "APPENDIX C: REFERENCES.............................. 41\n\n<!-- page 3 -->\n\n"
            "Executive Summary\nThe protection of a system must be documented in a plan.\n")

    found = extract.statement_items(extract.blocks(text), (1, 3))

    assert [(i.page, i.statement) for i in found.items] == [
        (2, "The activities at Levels 1 and 2 must prepare the organization."),
        (3, "Executive Summary The protection of a system must be documented in a plan.")]


def test_a_paragraph_that_starts_on_an_excluded_page_is_read_by_the_scope_it_ends_in():
    """CNSSI 1253F Att. 2 page 2 to 3 and eight other sources: a paragraph rejoined over the
    edge of an exclusion started outside every scope and was dropped by all of them."""
    text = ("<!-- page 1 -->\n\nThe website provides a framework for analyzing attacks on\n\n"
            "<!-- page 2 -->\n\nspace systems. CNSS must reference it.\n\nThe AO must sign.\n")
    scopes = [{"pages": [2, 2]}]

    found = extract.extract(text, scopes)

    assert [(i.page, i.statement) for i in found.items] == [
        (1, "The website provides a framework for analyzing attacks on space systems. CNSS must "
            "reference it."),
        (2, "The AO must sign.")]
    both = extract.extract(text, [{"pages": [1, 1]}, {"pages": [2, 2]}])
    assert len(both.items) == 2, "a block in two scopes is read once, by the first"


def test_a_numbered_heading_is_not_a_footnote_and_the_header_comment_is_nobodys():
    """`# 1 Introduction` was read as a footnote, so the contents list before it joined the
    introduction; the extraction's header comment before page 1 joined the title page."""
    text = ("<!--\nglyph_map:\n-->\n\n<!-- page 1 -->\n\nDecember 2022\n[Insert Name] Overlay\n\n"
            "Figure 1: Phases ........ 3\n\n<!-- page 2 -->\n\n# 1 Introduction\n\n"
            "The Department must transform how software is built.\n\n"
            "# 18 For additional guidance, see NIST SP 800-53B.\n")

    document = extract.blocks(text)
    found = extract.statement_items(document, (1, 2))

    assert [b.kind for b in document] == ["paragraph", "paragraph", "heading", "paragraph",
                                          "footnote"]
    assert [i.statement for i in found.items] == [
        "The Department must transform how software is built."]
    assert [(r.reason, r.text) for r in found.rejected][:2] == [
        ("no-marker", "December 2022 [Insert Name] Overlay"),
        ("leader", "Figure 1: Phases ........ 3")]


def test_marked_sentences_are_the_obligations_evidence_must_cite():
    text = ("The AO must approve the plan. It is a short plan. Organizations should review it "
            "yearly. For example, the SO must read it.")

    assert extract.marked_sentences(text) == ["The AO must approve the plan.",
                                              "Organizations should review it yearly."]


def test_an_over_long_paragraph_splits_into_runs_of_whole_sentences(monkeypatch):
    monkeypatch.setattr(extract, "MAX_PARAGRAPH_WORDS", 16)
    text = ("<!-- page 1 -->\n\nThe AO must approve the plan before use. The SO must register "
            "the system first. The plan is then updated by the SO. Nothing else happens.\n")

    runs = extract.split_long(text.split("\n\n")[1].strip())
    found = items(text, pages=(1, 1))

    assert runs == ["The AO must approve the plan before use. The SO must register the system "
                    "first.", "The plan is then updated by the SO. Nothing else happens."]
    assert [i.statement for i in found] == runs
    assert [i.kind for i in found] == ["modal", "indicative"]
    assert extract.split_long("Short. Text.") == ["Short. Text."]


def test_a_legend_row_and_a_template_example_are_rejected_with_their_reasons():
    text = ("<!-- page 1 -->\n\n| ATP: Authority to Proceed DD: | Disposition Decision | "
            "FOC: Full Operational Capability |\n| MS: Milestone | MVP: Minimum Viable Product | "
            "OD: Outcome Determination |\n\nExample (delete when description is completed): "
            "A space system must be described here as a set of interrelated processes.\n\n"
            "Example of when a control is not selected: the AO must document the reason.\n")

    assert statements(text, pages=(1, 1)) == []
    assert [(r.reason, r.text[:12]) for r in rejected(text, pages=(1, 1))] == [
        ("legend", "ATP: Authori"), ("legend", "MS: Mileston"),
        ("not-a-statement", "Example (del"), ("not-a-statement", "Example of w")]


def candidate(statement, page=1, anchor=None, locator="1.a", **kwargs):
    return Item("lettered", page, statement, locator, "ctx", anchor or statement, **kwargs)


def first_run(*statements):
    entries, _ = register.reconcile("DOC", [], [candidate(s) for s in statements], [])
    return entries


def reviewed(entry, **fields):
    entry.update({"status": "covered", "evidence": [{"kind": "rule", "target": "X-001"}],
                  **fields})
    return entry


def test_first_extraction_numbers_in_document_order_and_stays_candidate():
    entries = first_run("alpha", "beta")

    assert [e["id"] for e in entries] == ["REQ-DOC-0001", "REQ-DOC-0002"]
    assert {e["status"] for e in entries} == {"candidate"}
    assert "reason" not in entries[0]


def test_reviewed_fields_survive_a_page_shift():
    entries = first_run("alpha")
    reviewed(entries[0], work_item="WI-01")

    again, changes = register.reconcile("DOC", entries, [candidate("alpha", page=9)], [])

    assert again[0]["citation"]["page"] == 9
    assert again[0]["status"] == "covered" and again[0]["work_item"] == "WI-01"
    assert again[0]["id"] == "REQ-DOC-0001" and not changes.added


def test_a_longer_anchor_keeps_the_entry_because_the_statement_matches():
    entries = first_run("alpha beta")
    reviewed(entries[0])

    again, _ = register.reconcile("DOC", entries, [candidate("alpha beta", anchor="alpha")], [])

    assert again[0]["id"] == "REQ-DOC-0001" and again[0]["status"] == "covered"


def test_a_changed_statement_with_the_same_locator_and_anchor_needs_review():
    entries = first_run("alpha one")
    entries[0]["citation"]["anchor"] = "alpha"
    reviewed(entries[0])
    item = candidate("alpha two", anchor="alpha")

    again, changes = register.reconcile("DOC", entries, [item], [])

    assert again[0]["needs_review"] is True and again[0]["statement"] == "alpha two"
    assert changes.changed == ["REQ-DOC-0001"]


def test_the_fake_duplicate_insertion_no_longer_shifts_statuses():
    """The fake: a statement repeated in the source paired by occurrence, so inserting a copy
    ahead of a reviewed one moved its status to the newcomer. Identity is now the locator and
    the statement, and a group whose size changed marks its reviewed members for review."""
    entries = first_run("same", "same")
    reviewed(entries[1], reason="the second one")
    items = [candidate("same"), candidate("same"), candidate("same")]

    again, changes = register.reconcile("DOC", entries, items, [])

    reviewed_now = [e for e in again if e["status"] == "covered"]
    assert len(reviewed_now) == 1 and reviewed_now[0]["needs_review"] is True
    assert [e["id"] for e in again] == ["REQ-DOC-0001", "REQ-DOC-0002", "REQ-DOC-0003"]
    assert changes.ambiguous == ["REQ-DOC-0002"]


def test_a_statement_moving_to_another_section_keeps_its_id_when_unique():
    entries = first_run("alpha")
    reviewed(entries[0])

    again, changes = register.reconcile("DOC", entries, [candidate("alpha", locator="2.b")], [])

    assert again[0]["id"] == "REQ-DOC-0001" and again[0]["status"] == "covered"
    assert not changes.added and "needs_review" not in again[0]


def test_a_vanished_statement_is_reported_kept_and_its_id_never_reused():
    entries = first_run("alpha", "beta")

    again, changes = register.reconcile("DOC", entries, [candidate("alpha")], [])
    later, more = register.reconcile("DOC", again, [candidate("alpha"), candidate("gamma")], [])

    assert changes.removed == ["REQ-DOC-0002"]
    assert again[1]["removed"] is True and again[1]["id"] == "REQ-DOC-0002"
    assert not more.removed
    assert [e["id"] for e in later] == ["REQ-DOC-0001", "REQ-DOC-0002", "REQ-DOC-0003"]
    assert later[2]["statement"] == "gamma"


def test_a_removed_entry_keeps_its_status_so_fw_req_004_can_ask_why():
    entries = first_run("alpha", "beta")
    reviewed(entries[1])

    again, _ = register.reconcile("DOC", entries, [candidate("alpha")], [])

    assert again[1]["removed"] is True and again[1]["status"] == "covered"


def test_a_statement_that_returns_gets_its_id_back():
    entries = first_run("alpha", "beta")
    gone, _ = register.reconcile("DOC", entries, [candidate("alpha")], [])

    back, changes = register.reconcile("DOC", gone, [candidate("alpha"), candidate("beta")], [])

    assert back[1]["id"] == "REQ-DOC-0002" and "removed" not in back[1]
    assert not changes.added


PATTERN = {"id": "TP-01", "ref": "DOC", "statement": "^alp", "reason": "Not an RMF matter.",
           "sample": ["REQ-DOC-0001"]}


def test_triage_marks_candidates_and_a_retired_pattern_returns_them():
    entries = first_run("alpha", "beta")

    triaged, _ = register.reconcile("DOC", entries, [candidate("alpha"), candidate("beta")],
                                    [PATTERN])
    restored, _ = register.reconcile("DOC", triaged, [candidate("alpha"), candidate("beta")], [])

    assert (triaged[0]["status"], triaged[0]["triaged_by"]) == ("not-applicable", "TP-01")
    assert triaged[0]["reason"] == PATTERN["reason"]
    assert triaged[1]["status"] == "candidate"
    assert restored[0]["status"] == "candidate"
    assert "reason" not in restored[0] and "triaged_by" not in restored[0]


def test_triage_leaves_a_reviewed_entry_alone_and_is_limited_to_its_ref_and_pages():
    entries = first_run("alpha", "alpine")
    reviewed(entries[0])
    other_ref = {**PATTERN, "ref": "OTHER"}
    other_page = {**PATTERN, "pages": [5, 6]}

    kept, _ = register.reconcile("DOC", entries, [candidate("alpha"), candidate("alpine")],
                                 [other_ref, other_page, PATTERN])

    assert kept[0]["status"] == "covered"
    assert kept[1]["status"] == "not-applicable"
    limited, _ = register.reconcile("DOC", first_run("alpha"), [candidate("alpha")],
                                    [other_ref, other_page])
    assert limited[0]["status"] == "candidate"


@pytest.mark.parametrize("patterns", [[], [PATTERN]])
def test_the_generator_never_assigns_covered(patterns):
    entries, _ = register.reconcile("DOC", [], [candidate("alpha"), candidate("beta")], patterns)

    assert "covered" not in {e["status"] for e in entries}


# --- mark --------------------------------------------------------------------------------


def small_register():
    reg = register.Register()
    reg.files["DOC"] = {"schema_version": 1, "ref": "DOC", "mode": "statement",
                        "requirements": first_run("alpha", "beta")}
    return reg


def test_mark_sets_reviewed_fields_and_drops_a_pattern_mark_when_a_status_is_set_by_hand():
    reg = small_register()
    entry = reg.entry("REQ-DOC-0001")
    entry.update(status="not-applicable", reason="r", triaged_by="TP-01")

    register.mark(reg, "REQ-DOC-0001", status="partial", reason="Half done.", work_item="WI-01")
    register.mark(reg, "REQ-DOC-0002", needs_review=None)

    assert entry["status"] == "partial" and entry["work_item"] == "WI-01"
    assert "triaged_by" not in entry


def test_mark_refuses_generated_fields_and_removed_or_unknown_entries():
    reg = small_register()
    reg.entry("REQ-DOC-0002")["removed"] = True

    with pytest.raises(register.MarkError, match="not a reviewed field"):
        register.mark(reg, "REQ-DOC-0001", statement="rewritten")
    with pytest.raises(register.MarkError, match="no live entry"):
        register.mark(reg, "REQ-DOC-0002", status="covered")
    with pytest.raises(register.MarkError, match="no live entry"):
        register.mark(reg, "REQ-DOC-0009", status="covered")


# --- rendering and catalogs --------------------------------------------------------------


def test_a_rendered_register_loads_back_unchanged():
    entries = first_run('quote " and: colon', "unicode – dash")
    reviewed(entries[0], reason="because")
    document = {"schema_version": 1, "ref": "DOC", "mode": "statement", "requirements": entries,
                "rejected": [{"page": 1, "locator": "1.a", "reason": "no-marker",
                              "text": 'quote " and: colon'}]}

    loaded = YAML(typ="safe").load(register.render_requirements(document))

    assert loaded == document


def test_a_rendered_catalog_with_prose_entries_loads_back_unchanged():
    document = {"schema_version": 1, "ref": "DOC", "mode": "catalog", "catalog": "controls",
                "count": 2, "ids": ["AC-1", "AC-2(1)"], "requirements": first_run("alpha"),
                "rejected": []}

    assert YAML(typ="safe").load(register.render_requirements(document)) == document


def test_the_fast_reader_reads_what_render_writes_and_nothing_else():
    """register.read parses a rendered file without the YAML loader; a hand-edited file
    (INV-2) falls back to YAML and is judged as YAML."""
    entries = first_run('quote " and: colon', "unicode – dash")
    reviewed(entries[0], reason="because")
    document = {"schema_version": 1, "ref": "DOC", "mode": "catalog", "catalog": "controls",
                "count": 1, "ids": ["AC-1"], "requirements": entries,
                "rejected": [{"page": 1, "locator": "", "reason": "short", "text": "x: y"}]}
    text = register.render_requirements(document)

    assert register.read_generated(text) == document
    assert register.read_generated(text.replace('status: "candidate"', "status: candidate")) \
        == document, "a bare YAML word reads the same both ways"
    assert register.read_generated(text.replace('reason: "because"', "reason: {a: b}")) is None
    assert register.read_generated(text + "    - a nested list the renderer never writes\n") \
        is None


def test_rendered_text_hashes_load_back_unchanged():
    hashes = {"DOC": "a" * 64, "B": "b" * 64}

    assert YAML(typ="safe").load(register.render_text_hashes(hashes)) == {
        "schema_version": 1, "hashes": hashes}


def test_information_types_are_read_from_their_headings():
    source = {"catalog": "information-types"}
    text = "C.2.1.1 Corrective Action Information Type\nD.2.1 Border Information Type ... 108\n" \
           "C.2.1 Controls and Oversight\nTable D-1: Information Types\n"

    assert register.catalog_ids(source, text) == ["C.2.1.1", "D.2.1"]


def test_the_reference_list_keys_come_only_from_line_starts():
    text = ("## REFERENCES\nDoD Directive 3020.04, “Order of Succession Pursuant to Executive "
            "Order 13533”\nExecutive Order 13800, “Strengthening”\n")

    assert register.reference_list_keys(text) == ["DoD Directive 3020.04", "Executive Order 13800"]


def test_copy_of_the_real_register_round_trips_through_reconcile():
    """Re-extracting the committed register changes nothing (what FW-REQ-005 checks)."""
    reg = register.load(REPO_ROOT)
    index = register.index_entries(REPO_ROOT)
    for ref in ("FIPS199", "DODCIO-CATO"):
        before = copy.deepcopy(reg.files[ref])
        built = register.build(reg, reg.sources[ref], register.text_of(REPO_ROOT, index[ref]))

        assert built.document == before
        assert not built.changes.added and not built.changes.removed


FOOTERS = (r"^\d{1,3}$",)
CROSSING = ("<!-- page 1 -->\n\nThe organization must review the system already\n\n3\n\n"
            "<!-- page 2 -->\n\ndeployed in the Component. The AO must sign the plan.\n\n4\n\n"
            "<!-- page 3 -->\n\nThe AO must also record the decision.\n\n5\n")


def test_a_declared_footer_is_neither_joined_nor_in_the_way_of_a_join():
    """RECIPROCITY p. 5: the page number sat between the two halves of a sentence, and the second
    half joined to it, so the statement began with `3` and cited the wrong page."""
    document = extract.blocks(CROSSING, footers=FOOTERS)

    prose = [b for b in document if b.kind == "paragraph"]
    assert [b.text for b in document if b.kind == "footer"] == ["3", "4", "5"]
    assert prose[0].text == ("The organization must review the system already deployed in the "
                             "Component. The AO must sign the plan.")
    assert (prose[0].page, prose[0].end_page) == (1, 2)
    assert prose[1].text == "The AO must also record the decision."


def test_an_undeclared_page_number_still_absorbs_the_next_page():
    """What the declaration fixes, and what the check across the registers would catch."""
    assert "3 deployed in the Component. The AO must sign the plan." in \
        [b.text for b in extract.blocks(CROSSING)]


def test_a_statement_crossing_a_page_cites_its_first_page_and_the_footer_is_rejected():
    found = extract.extract(CROSSING, [{"pages": [1, 3]}], footers=FOOTERS)

    assert [(i.page, i.anchor) for i in found.items][:1] == \
        [(1, "The organization must review the system already")]
    assert not any(i.statement[0].isdigit() for i in found.items)
    assert [(r.reason, r.text) for r in found.rejected] == \
        [("footer", "3"), ("footer", "4"), ("footer", "5")]


def test_a_footer_of_several_blocks_is_skipped_whole():
    """CNSSP 22 p. 2: the address and the phone and email close the page in two blocks."""
    text = ("<!-- page 1 -->\n\nAnnex A identifies the documents, which include\n\n"
            "CNSS Secretariat (C074) Fort Meade\n\n(410)-854-6805\ncnss@nsa.gov\n\n"
            "<!-- page 2 -->\n\nNIST publications for a program. Annex A will be updated.\n")

    document = extract.blocks(text, footers=(r"^CNSS Secretariat", r"^\(410\)"))

    assert [b.kind for b in document] == ["paragraph", "footer", "footer"]
    assert document[0].text == ("Annex A identifies the documents, which include NIST "
                                "publications for a program. Annex A will be updated.")


def test_a_footer_pattern_matches_only_the_close_of_a_page():
    text = "<!-- page 1 -->\n\n12\n\nThe AO must sign the plan.\n\n3\n"

    assert [(b.text, b.kind) for b in extract.blocks(text, footers=FOOTERS)] == \
        [("12", "paragraph"), ("The AO must sign the plan.", "paragraph"), ("3", "footer")]


def test_a_list_item_keeps_its_place_across_a_footer():
    text = ("<!-- page 1 -->\n\n4.1 Duties\n\nThe owner:\n\na. Will sign the plan.\n\n3\n\n"
            "<!-- page 2 -->\n\nb. Will file the plan.\n")

    found = extract.extract(text, [{"pages": [1, 2]}], footers=FOOTERS)

    assert [i.locator for i in found.items] == ["a", "b"]


CUT = """<!-- page 1 -->

# 4. USE CASES

f. Ensure the Enterprise system complies with Information Assurance Vulnerability

Management (IAVM) Program directions.

o Ensure assignment of an accredited CSSP to maintain continuous monitoring, Event Management (SIEM)

<!-- page 2 -->

monitoring, operational orders and POA&Ms.

• Development of a new capability or system

The engineering effort includes concept exploration.

# 5. ROLE OF VARIOUS TYPES OF AOS

a. The AO will review the body of evidence.
"""


def test_a_cut_item_joins_only_where_the_source_declares_it():
    """WI-56 (I-7): a list item cut by a blank line inside a page, or ending `)` before a page
    that opens in lowercase, is one sentence where sources.yaml declares cut_items; elsewhere a
    blank line still ends a paragraph, and a bullet with no closing punctuation keeps the
    paragraph after it apart."""
    declared = [b.text for b in extract.blocks(CUT, cut_items=True) if b.kind == "paragraph"]
    plain = [b.text for b in extract.blocks(CUT) if b.kind == "paragraph"]

    assert "f. Ensure the Enterprise system complies with Information Assurance Vulnerability " \
        "Management (IAVM) Program directions." in declared
    assert "o Ensure assignment of an accredited CSSP to maintain continuous monitoring, Event " \
        "Management (SIEM) monitoring, operational orders and POA&Ms." in declared
    assert "• Development of a new capability or system" in plain
    assert "Management (IAVM) Program directions." in plain and "monitoring, operational " \
        "orders and POA&Ms." in plain


def test_a_cut_item_never_swallows_a_heading_or_a_short_label():
    text = "<!-- page 1 -->\n\n5. ROLE OF VARIOUS TYPES OF AOS IN RECIPROCITY\n\nTo maintain " \
        "scope, we identified roles.\n\nc. Decisions\n\nThe AO decides.\n"
    found = [b.text for b in extract.blocks(text, cut_items=True)]

    assert found == ["5. ROLE OF VARIOUS TYPES OF AOS IN RECIPROCITY",
                     "To maintain scope, we identified roles.", "c. Decisions", "The AO decides."]


RUN_IN = """<!-- page 1 -->

# SECTION 2: RESPONSIBILITIES

2.4. DIRECTOR, OPERATIONAL TEST AND EVALUATION (DOT&E). The DOT&E:

a. Monitors all urgent capability acquisition programs.

2.5. UNDER SECRETARY OF DEFENSE FOR INTELLIGENCE. The Under Secretary of
Defense for Intelligence:

a. Advises the USD(A&S) on security requirements.

2.6. USD(C)/CFO. The USD(C)/CFO assesses Component funding strategies.

# 5. ROLE OF AOS

a. The AO will review the body of evidence.
"""


def test_run_in_headings_set_the_section_of_what_follows_only_where_declared():
    """WI-54 (I-5): `2.5. CAPS TITLE. Prose` and `5. CAPS TITLE` head a section where the
    source declares run_in_headings; the paragraph's own statement is unchanged."""
    declared = extract.statement_items(extract.blocks(RUN_IN), (1, 1), run_in_headings=True)
    plain = extract.statement_items(extract.blocks(RUN_IN), (1, 1))
    where = {i.statement[:12]: (i.locator, i.context) for i in declared.items}
    before = {i.statement[:12]: i.locator for i in plain.items}

    assert where["a. Advises t"] == ("2.5.a", "UNDER SECRETARY OF DEFENSE FOR INTELLIGENCE "
                                     "The Under Secretary of Defense for Intelligence:")
    assert [r.locator for r in declared.rejected if r.text.startswith("2.6.")] == ["2.6"]
    assert where["a. The AO wi"][0] == "5.a"
    assert before["a. Advises t"] == "2.4.a" and before["a. The AO wi"] != "5.a"
    assert [r.text for r in declared.rejected if r.text.startswith("2.6.")] == \
        ["2.6. USD(C)/CFO. The USD(C)/CFO assesses Component funding strategies."]


def test_a_declared_running_header_neither_joins_nor_stops_a_join():
    """WI-50: CNSSP12's running header `CNSSP 12` opens each page and stopped every sentence
    that crossed one; declared as a header it is set aside and the sentence joins."""
    text = "<!-- page 1 -->\n\ng. Systems must meet guidelines, standards, and\n\n" \
        "<!-- page 2 -->\n\nCNSSP 12\n\npolicies issued by the Heads of Agencies.\n"
    declared = extract.blocks(text, headers=(r"^C ?N?SSP 12$",))
    plain = extract.blocks(text)

    assert [(b.text, b.kind) for b in declared] == [
        ("g. Systems must meet guidelines, standards, and policies issued by the Heads of "
         "Agencies.", "paragraph"), ("CNSSP 12", "footer")]
    assert [b.text for b in plain][0] == "g. Systems must meet guidelines, standards, and"
