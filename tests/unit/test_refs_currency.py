"""REF-007, REF-008 and FW-CITE-003 (AC-25..AC-27, ADR-0005): reference currency, offline."""

import json
import shutil

import pytest
from _framework_fixtures import MINI, compose
from _refs_fixtures import SHA_A, entry, make_root
from conftest import REPO_ROOT

from rmf_tool import ci, refs
from rmf_tool.framework.model import SCHEMA_DIR
from rmf_tool.framework.validate import validate
from rmf_tool.profiles import Profile
from rmf_tool.refs import currency

P9 = Profile("p9", frozenset({"p1", "p2", "p3a", "p9"}))
TEXT = "references/text/DOC-A.md"
PAGES = "<!-- page 1 -->\n\nCover\n\n<!-- page 2 -->\n\nIncludes updates as of 12-10-2020\n"


STAMP = {"page": 2, "anchor": "Includes updates as of 12-10-2020"}


def ok_pdf(ref_id="DOC-A", **kw):
    text = {"path": f"references/text/{ref_id}.md", "source_sha256": SHA_A,
            "extractor": "pymupdf", "extractor_version": "2.0", "rmf_extract_version": "1",
            "pages": 2, "sha256": SHA_A, "ocr": False, "ocr_pages": []}
    fields = {"revision": "Rev. 1 (December 2020)", "revision_stamp": STAMP, **kw}
    fields = {k: v for k, v in fields.items() if v is not None}
    return entry(ref_id, status="ok", sha256=SHA_A, size_bytes=1, downloaded="2026-10-31",
                 text=text, **fields)


def findings(tmp_path, entries):
    rr = make_root(tmp_path, entries)
    rr.write(TEXT, PAGES)
    return currency.check(rr.root, rr.index())


def only(found):
    [f] = found
    assert (f.rule, f.severity) == ("REF-007", "E")
    return f.message


@pytest.mark.parametrize("revision", [
    "Rev. 5 (September 2020, with updates)", "January 23, 2020 (with changes)",
    "current (record the version at import)", "latest", "pending import",
    "Rev. 5 (September 2020, includes updates)", "Rev. 5 (September 2020, as amended)",
    "Rev. 5 (September 2020, updated)", "Rev. 5 (September 2020, draft)",
    "Rev. 5 (September 2020, changes)"])
def test_ref_007_flags_vague_revisions(tmp_path, revision):
    assert "vague" in only(findings(tmp_path, [ok_pdf(revision=revision)]))


@pytest.mark.parametrize("revision", ["Rev. 5", "2020", "Rev. 5 (2020)", "Rev. 1"])
def test_ref_007_requires_a_month_and_year_or_iso_date(tmp_path, revision):
    assert "no month and year" in only(findings(tmp_path, [ok_pdf(revision=revision)]))


@pytest.mark.parametrize("revision, year", [
    ("Rev. 5 (September 2020, includes updates as of 12-10-2020)", "2020"),
    ("January 23, 2020, Change 2, April 8, 2026", "2026"),
    ("Version 2.5 (approved October 16, 2024)", "2024"),
    ("29 July 2022", "2022"), ("2020-12-10", "2020"),
    ("Rev. 1 (May 2010, errata through 11/11/2010)", "2010")])
def test_ref_007_accepts_exact_revisions(tmp_path, revision, year):
    stamp = {"page": 2, "anchor": f"as of 12-10-{year}"}
    rr = make_root(tmp_path, [ok_pdf(revision=revision, revision_stamp=stamp)])
    rr.write(TEXT, PAGES.replace("2020", year))
    assert currency.check(rr.root, rr.index()) == []


def test_ref_007_does_not_flag_change_n(tmp_path):
    assert findings(tmp_path, [ok_pdf(revision="June 2020, with Change 1, December 2020")]) == []


def test_ref_007_flags_an_unresolved_stamp(tmp_path):
    bad = {"page": 1, "anchor": "Includes updates as of 12-10-2020"}
    msg = only(findings(tmp_path, [ok_pdf(revision_stamp=bad)]))
    assert "revision_stamp" in msg and "page 1" in msg


def test_ref_007_requires_a_stamp_unless_revision_source_gives_a_reason(tmp_path):
    assert "no revision_stamp" in only(findings(tmp_path, [ok_pdf(revision_stamp=None)]))

    exempt = ok_pdf(revision_stamp=None, revision_source={"reason": "the page footer is stripped"})
    assert findings(tmp_path / "e", [exempt]) == []

    both = ok_pdf(revision_source={"reason": "x"})
    assert "both" in only(findings(tmp_path / "b", [both]))


def test_the_schema_requires_a_reason_for_revision_source(tmp_path):
    rr = make_root(tmp_path, [ok_pdf(revision_stamp=None, revision_source={})])
    with pytest.raises(refs.IndexFileError):
        rr.index()


def test_ref_007_flags_a_revision_that_disagrees_with_its_stamp(tmp_path):
    msg = only(findings(tmp_path, [ok_pdf(revision="Rev. 1 (December 2021)")]))
    assert "2021" in msg and "does not show" in msg
    ok = ok_pdf(revision="Rev. 1 (September 2019, December 2020)")
    assert findings(tmp_path / "ok", [ok]) == []


def test_ref_007_ignores_pdfs_that_are_not_pinned(tmp_path):
    pending = entry("DOC-B", revision="pending import", status="pending-acquisition")
    assert findings(tmp_path, [pending]) == []


def catalog(*ids):
    return json.dumps({"catalog": {"groups": [{"controls": [
        {"id": ids[0], "controls": [{"id": i} for i in ids[1:]]}]}]}})


CATALOG = "references/oscal/catalog.json"


def catalog_entry():
    return entry("OSCAL-CATALOG-53R5", kind="oscal-catalog", local_path=CATALOG,
                 status="ok", sha256=SHA_A, size_bytes=1, downloaded="2026-10-31")


def test_ref_008_flags_undeclared_oscal_only_controls(tmp_path):
    pdf = ok_pdf("SP800-53R5")
    rr = make_root(tmp_path, [catalog_entry(), pdf])
    rr.write(CATALOG, catalog("ac-1", "ac-1.1", "ia-13", "ia-13.1"))
    rr.write("references/text/SP800-53R5.md", "<!-- page 1 -->\nAC-01 and AC-01(01) only\n")
    [f] = [f for f in currency.check(rr.root, rr.index()) if f.rule == "REF-008"]
    assert f.severity == "W" and "IA-13, IA-13(1)" in f.message and "declare" in f.message

    declared = {**pdf, "oscal_only_controls": ["IA-13", "IA-13(1)"]}
    rr.write_index([catalog_entry(), declared])
    assert [f for f in currency.check(rr.root, rr.index()) if f.rule == "REF-008"] == []

    stale = {**pdf, "oscal_only_controls": ["IA-13", "IA-13(1)", "AC-1"]}
    rr.write_index([catalog_entry(), stale])
    [f] = [f for f in currency.check(rr.root, rr.index()) if f.rule == "REF-008"]
    assert "AC-1" in f.message and "remove" in f.message


def test_control_ids_normalise_across_the_three_notations():
    assert currency.text_controls("CM-02(01) and CM-2(1), SA-15(13)") == {"CM-2(1)", "SA-15(13)"}
    assert currency.text_controls("SA-240 and SA-24, IA-130") == {"SA-24"}
    cat = json.loads(catalog("cm-2", "cm-2.1"))
    assert currency.catalog_controls(cat) == {"CM-2", "CM-2(1)"}


def test_the_committed_index_passes_ref_007_and_ref_008():
    assert currency.check(REPO_ROOT, refs.load_index(REPO_ROOT)) == []


def test_ci_has_a_p9_step():
    assert any(s.phase == "p9" and s.rules == currency.RULES for s in ci.STEPS)


DECISION = """decisions:
  - id: AD-ATO
    name: Authorization to Operate
    short: ATO
    description: The risk is acceptable; the system may operate until the termination date.
    decided_by: PER-AO
    decided_in: [R-4]
    phases: [PH-EMD]
    atd_required: true
    conditions_required: false
    citations:
      - {ref: %s, section: x}
  - id: AD-DATO
    name: Denial of Authorization to Operate
    short: DATO
    description: The risk is unacceptable; the system may not operate.
    decided_by: PER-AO
    decided_in: [R-4]
    phases: [PH-EMD]
    atd_required: false
    conditions_required: false
    citations:
      - {ref: SP800-37R2, section: "TASK R-4"}
"""


def run_cite_rule(tmp_path, ref, card=None):
    """FW-CITE-003 on a synthetic index (DOC-OPT optional, DOC-REQ required), so no test
    depends on the state of a real entry."""
    rr = make_root(tmp_path, [entry("DOC-OPT", acquisition="browser-assisted", urls=[],
                                    landing_url="https://www.esd.whs.mil/"),
                              entry("DOC-REQ", required=True)])
    shutil.copytree(REPO_ROOT / SCHEMA_DIR, rr.root / SCHEMA_DIR)
    overlay = tmp_path / "overlay"
    overlay.mkdir()
    (overlay / "decisions.yaml").write_text(DECISION % ref, encoding="utf-8")
    if card is not None:
        rr.write("personas/PER-AO.md", card)
    result = validate(compose(overlay, tmp_path / "fw", MINI), rr.root, P9)
    return [f for f in result.findings if f.rule == "FW-CITE-003"]


CARD = "## Citations\n\n- `uv run rmf refs show %s --section 1`\n"


def test_fw_cite_003_fires_on_an_optional_pdf(tmp_path):
    [f] = run_cite_rule(tmp_path, "DOC-OPT")
    assert f.severity == "E" and f.message.startswith("AD-ATO:") and "DOC-OPT" in f.message


def test_fw_cite_003_is_quiet_for_a_required_pdf(tmp_path):
    assert run_cite_rule(tmp_path, "DOC-REQ") == []


def test_fw_cite_003_fires_on_a_persona_card(tmp_path):
    [f] = run_cite_rule(tmp_path, "DOC-REQ", CARD % "DOC-OPT")
    assert f.message.startswith("PER-AO:") and "DOC-OPT" in f.message
    assert f.path == "personas/PER-AO.md"


def test_fw_cite_003_is_quiet_for_a_required_citation_on_a_card(tmp_path):
    assert run_cite_rule(tmp_path, "DOC-REQ", CARD % "DOC-REQ") == []
