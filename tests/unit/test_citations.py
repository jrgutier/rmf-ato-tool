"""FW-CITE-002 citation resolution (AC-8, AC-4a): exact `rmf refs show` semantics,
pending-acquisition deferral before p2x, the page/anchor form and degraded fallbacks."""

import shutil

import pytest
from _framework_fixtures import MINI, P3A, P3A_BEFORE_P2X
from _refs_fixtures import SHA_A, entry, make_root
from conftest import REPO_ROOT
from test_refs_show import ENTRIES, MD

from rmf_tool.framework.citations import DEFERRED, ERROR, OK, Resolver, describe
from rmf_tool.framework.model import SCHEMA_DIR
from rmf_tool.framework.validate import validate
from rmf_tool.profiles import resolve
from rmf_tool.refs import toc

TEXT = {"path": "references/text/DOC-A.md", "source_sha256": SHA_A, "extractor": "pymupdf",
        "extractor_version": "2.0", "rmf_extract_version": "1", "pages": 2, "sha256": SHA_A,
        "ocr": False, "ocr_pages": []}
DEGRADED = {"approved_by": "user", "date": "2026-10-29", "reason": "unobtainable",
            "fallback_refs": ["DOC-A"]}


@pytest.fixture
def rr(tmp_path):
    rr = make_root(tmp_path, [
        entry("DOC-A", status="ok", sha256=SHA_A, size_bytes=1, downloaded="2026-10-29",
              text=TEXT),
        entry("DOC-P", acquisition="browser-assisted", urls=[],
              landing_url="https://www.esd.whs.mil/", status="pending-acquisition"),
        entry("DOC-D", status="degraded", degraded=DEGRADED),
        entry("DOC-M"),
    ])
    rr.write("references/text/DOC-A.md", MD)
    rr.write("references/text/DOC-A.toc.yaml", toc.render_toc("DOC-A", ENTRIES))
    return rr


def resolver(rr, strict):
    return Resolver(rr.root, rr.index(), strict=strict)


def test_section_and_page_anchor_resolve_like_refs_show(rr):
    r = resolver(rr, strict=True)
    assert r.resolve({"ref": "DOC-A", "section": "1.1"}).status == OK
    assert r.resolve({"ref": "DOC-A", "section": "1.2 Target Audience"}).status == OK
    assert r.resolve({"ref": "DOC-A", "page": 1, "anchor": "purpose of this publication"}
                     ).status == OK
    missing = r.resolve({"ref": "DOC-A", "section": "9.9"})
    assert missing.status == ERROR and "no section '9.9'" in missing.message
    wrong_page = r.resolve({"ref": "DOC-A", "page": 2, "anchor": "purpose of this publication"})
    assert wrong_page.status == ERROR and "not found on page 2" in wrong_page.message


def test_pending_acquisition_citations_deferred_before_p2x(rr):
    result = resolver(rr, strict=False).resolve({"ref": "DOC-P", "section": "3"})
    assert result.status == DEFERRED


def test_pending_acquisition_citations_error_from_p3b(rr):
    # p3b requires p2x closed, so every p3b profile includes p2x: resolution is strict.
    (rr.root / ".phases").mkdir()
    for phase in ("p1", "p2", "p2x"):
        (rr.root / ".phases" / f"{phase}.closed").write_text("closed\n")
    profile = resolve(rr.root, "p3b")
    result = resolver(rr, strict=profile.includes("p2x")).resolve({"ref": "DOC-P",
                                                                   "section": "3"})
    assert result.status == ERROR and "pending-acquisition" in result.message


def test_page_requires_anchor(rr):
    r = resolver(rr, strict=True)
    result = r.resolve({"ref": "DOC-A", "page": 1})
    assert result.status == ERROR and result.message == "a page citation requires an anchor"
    assert r.resolve({"ref": "DOC-A", "anchor": "x"}).message == "an anchor requires a page"
    assert r.resolve({"ref": "DOC-A", "section": "1", "page": 1, "anchor": "x"}).message == \
        "give either section or page+anchor, not both"
    assert r.resolve({"ref": "DOC-A"}).message == "a citation needs a section or a page+anchor"


def test_degraded_reference_needs_a_resolving_fallback(rr):
    r = resolver(rr, strict=True)
    assert r.resolve({"ref": "DOC-D", "section": "1"}).status == ERROR
    ok = r.resolve({"ref": "DOC-D", "section": "1", "fallback": {"ref": "DOC-A",
                                                                  "section": "2"}})
    assert ok.status == OK
    bad = r.resolve({"ref": "DOC-D", "section": "1", "fallback": {"ref": "DOC-A",
                                                                   "section": "7"}})
    assert bad.status == ERROR and bad.message.startswith("fallback for degraded DOC-D")


def test_unknown_and_not_ok_references(rr):
    r = resolver(rr, strict=False)
    assert not r.known("NOPE")
    assert r.resolve({"ref": "NOPE", "section": "1"}).message == "unknown reference 'NOPE'"
    assert r.resolve({"ref": "DOC-M", "section": "1"}).message == "DOC-M is missing, not ok"


def test_describe():
    assert describe({"ref": "X", "section": "3"}) == "X section '3'"
    assert describe({"ref": "X", "page": 4, "anchor": "a"}) == "X page 4 anchor 'a'"


def test_validate_counts_deferred_citations(rr, tmp_path):
    """End to end: a citation to a pending reference is counted, not reported, before p2x
    and reported from p2x on."""
    fw = tmp_path / "fw"
    shutil.copytree(MINI, fw)
    shutil.copytree(REPO_ROOT / SCHEMA_DIR, rr.root / SCHEMA_DIR)
    tasks_r = fw / "tasks" / "R.yaml"
    tasks_r.write_text(tasks_r.read_text().replace(
        '      - {ref: SP800-37R2, section: "TASK R-4"}',
        '      - {ref: SP800-37R2, section: "TASK R-4"}\n      - {ref: DOC-P, section: "3"}'))

    before = validate(fw, rr.root, P3A_BEFORE_P2X)
    after = validate(fw, rr.root, P3A)

    # Every other citation in the mini framework names a reference this tmp index lacks.
    assert before.stats["deferred_citations"] == 1
    assert not any("DOC-P" in f.message for f in before.findings)
    assert any(f.rule == "FW-CITE-002" and "DOC-P" in f.message for f in after.findings)
