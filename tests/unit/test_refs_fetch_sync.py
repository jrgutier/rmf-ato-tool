"""`rmf refs extract` orchestration (index text blocks) and `rmf refs sync`, with the
extractor faked at the extract.py contract boundary."""

import hashlib
import json
from urllib.parse import urlsplit

import pytest
from _refs_fixtures import entry, make_pdf, make_root, required_entries
from typer.testing import CliRunner

from rmf_tool.cli import app
from rmf_tool.refs import domains, extract, fetch, sync, verify

PDF = make_pdf("sync")
PDF_SHA = hashlib.sha256(PDF).hexdigest()
runner = CliRunner()

VERSIONS = """\
generated_oscal_version: 1.2.1
compliance_trestle: 5.2.0
schemas: {repo: usnistgov/OSCAL, tag: v1.2.1}
content: {repo: usnistgov/oscal-content, tag: v1.6.0}
input_minor: '1.2'
inputs: {}
"""


class FakeExtractor:
    """Stands in for extract.extract / is_current: writes <ID>.md + <ID>.toc.yaml."""

    def __init__(self, version="2.0"):
        self.version = version
        self.calls = []

    def is_current(self, text, source_sha256, extractor):
        return bool(text) and text["source_sha256"] == source_sha256 \
            and text["extractor_version"] == self.version

    def extract(self, doc_id, pdf_path, out_dir, *, source_sha256, extractor="pymupdf",
                ocr=False):
        self.calls.append((doc_id, extractor, ocr))
        out_dir.mkdir(parents=True, exist_ok=True)
        body = f"<!-- page 1 -->\n{doc_id} v{self.version}\n"
        (out_dir / f"{doc_id}.md").write_text(body, encoding="utf-8")
        (out_dir / f"{doc_id}.toc.yaml").write_text("[]\n", encoding="utf-8")
        return extract.ExtractResult(
            doc_id=doc_id, text_path=out_dir / f"{doc_id}.md",
            toc_path=out_dir / f"{doc_id}.toc.yaml", pages=1,
            sha256=hashlib.sha256(body.encode()).hexdigest(), extractor=extractor,
            extractor_version=self.version, rmf_extract_version="1", ocr=ocr, ocr_pages=[])


@pytest.fixture
def fake(monkeypatch):
    fx = FakeExtractor()
    monkeypatch.setattr(extract, "extract", fx.extract)
    monkeypatch.setattr(extract, "is_current", fx.is_current)
    monkeypatch.setattr(extract, "check", lambda *a, **kw: [])
    return fx


@pytest.fixture
def rr(tmp_path):
    rr = make_root(tmp_path, [
        entry("DOC-A", status="ok", sha256=PDF_SHA, size_bytes=len(PDF), downloaded="2026-10-29"),
        entry("DOC-B"),  # missing: not extracted
    ])
    rr.write("references/pdf/DOC-A.pdf", PDF)
    return rr


def test_extract_all_writes_text_block_then_skips_current(rr, fake):
    first = sync.extract_all(rr.root)
    text = dict(rr.entry("DOC-A")["text"])
    second = sync.extract_all(rr.root)
    forced = sync.extract_all(rr.root, ["DOC-A"], full=True)

    assert [(r.id, r.status) for r in first] == [("DOC-A", "extracted")]
    assert text == {
        "path": "references/text/DOC-A.md", "source_sha256": PDF_SHA, "extractor": "pymupdf",
        "extractor_version": "2.0", "rmf_extract_version": "1", "pages": 1,
        "sha256": hashlib.sha256(b"<!-- page 1 -->\nDOC-A v2.0\n").hexdigest(),
        "ocr": False, "ocr_pages": []}
    assert [r.status for r in second] == ["current"]
    assert [r.status for r in forced] == ["extracted"]
    assert len(fake.calls) == 2


def test_extract_all_reextracts_when_extractor_changes(rr, fake):
    sync.extract_all(rr.root)
    fake.version = "2.1"
    [result] = sync.extract_all(rr.root)
    assert result.status == "extracted"
    assert rr.entry("DOC-A")["text"]["extractor_version"] == "2.1"


def test_extract_all_unknown_id(rr, fake):
    with pytest.raises(KeyError, match="NOPE"):
        sync.extract_all(rr.root, ["NOPE"])


def test_extract_all_keeps_blocks_written_before_a_failure(tmp_path, fake, monkeypatch):
    rr = make_root(tmp_path, [
        entry(rid, status="ok", sha256=PDF_SHA, size_bytes=1, downloaded="2026-10-29")
        for rid in ("DOC-A", "DOC-B")])
    real = fake.extract

    def flaky(doc_id, *a, **kw):
        if doc_id == "DOC-B":
            raise extract.ExtractorUnavailable("boom")
        return real(doc_id, *a, **kw)

    monkeypatch.setattr(extract, "extract", flaky)
    with pytest.raises(extract.ExtractorUnavailable):
        sync.extract_all(rr.root)
    assert rr.entry("DOC-A").get("text") is not None
    assert rr.entry("DOC-B").get("text") is None


def test_full_check_compares_bytes(rr, fake):
    sync.extract_all(rr.root)
    assert sync.full_check(rr.root, rr.index()) == []
    (rr.root / "references/text/DOC-A.toc.yaml").write_text("edited\n", encoding="utf-8")
    [finding] = sync.full_check(rr.root, rr.index())
    assert finding.rule == "REF-003" and "DOC-A.toc.yaml" in finding.message


def test_cli_extract_outputs_and_full_check(rr, fake, monkeypatch):
    monkeypatch.chdir(rr.root)
    text = runner.invoke(app, ["refs", "extract", "--extractor", "pdfplumber"])
    as_json = runner.invoke(app, ["refs", "extract", "--format", "json"])
    check = runner.invoke(app, ["refs", "extract", "--check", "--full"])

    assert text.exit_code == 0 and "extracted  DOC-A (1 pages)" in text.stdout
    assert fake.calls[0] == ("DOC-A", "pdfplumber", False)
    assert json.loads(as_json.stdout)["results"][0]["id"] == "DOC-A"
    assert check.exit_code == 0


def test_cli_extract_without_extra_is_usage_error(rr, monkeypatch):
    def unavailable(*a, **kw):
        raise extract.ExtractorUnavailable("needs the optional [extract] extra")

    monkeypatch.setattr(extract, "extract", unavailable)
    monkeypatch.chdir(rr.root)

    result = runner.invoke(app, ["refs", "extract", "--full"])

    assert result.exit_code == 2
    assert "[extract]" in result.output


def test_cli_extract_unknown_id(rr, fake, monkeypatch):
    monkeypatch.chdir(rr.root)
    assert runner.invoke(app, ["refs", "extract", "--id", "NOPE"]).exit_code == 2


def _allow_local(url, redirected_from=None):
    if urlsplit(url).hostname in ("localhost", "127.0.0.1"):
        return None
    return domains.disallowed_reason(url, redirected_from)


def test_cli_sync_fetches_extracts_indexes_and_verifies(tmp_path, httpserver, fake,
                                                        monkeypatch):
    monkeypatch.setattr(fetch, "disallowed_reason", _allow_local)
    monkeypatch.setattr(verify, "disallowed_reason", _allow_local)
    httpserver.expect_request("/a.pdf").respond_with_data(PDF)
    rr = make_root(tmp_path, [*required_entries(),
                              entry("DOC-A", urls=[httpserver.url_for("/a.pdf")])])
    rr.write("references/oscal/VERSIONS.yaml", VERSIONS)
    monkeypatch.chdir(rr.root)

    first = runner.invoke(app, ["refs", "sync"])
    second = runner.invoke(app, ["refs", "sync", "--format", "json"])

    assert first.exit_code == 0, first.output
    assert "downloaded" in first.output and "extracted  DOC-A" in first.output
    assert (rr.root / "references/INDEX.md").is_file()
    assert rr.entry("DOC-A")["text"]["pages"] == 1
    assert second.exit_code == 0
    assert json.loads(second.stdout)["summary"]["errors"] == 0
    assert len(fake.calls) == 1  # second sync: nothing re-fetched or re-extracted


def test_cli_sync_reports_fetch_failure(tmp_path, httpserver, fake, monkeypatch):
    monkeypatch.setattr(fetch, "disallowed_reason", _allow_local)
    httpserver.expect_request("/a.pdf").respond_with_data("gone", status=404)
    rr = make_root(tmp_path, [*required_entries(),
                              entry("DOC-A", urls=[httpserver.url_for("/a.pdf")])])
    rr.write("references/oscal/VERSIONS.yaml", VERSIONS)
    monkeypatch.chdir(rr.root)

    result = runner.invoke(app, ["refs", "sync"])

    assert result.exit_code == 1
    assert "manual-required" in result.output


def test_cli_sync_without_extra_is_usage_error(rr, monkeypatch):
    def unavailable(*a, **kw):
        raise extract.ExtractorUnavailable("needs the optional [extract] extra")

    monkeypatch.setattr(extract, "is_current", lambda *a: False)
    monkeypatch.setattr(extract, "extract", unavailable)
    monkeypatch.setattr(fetch, "fetch", lambda root, **kw: [])
    monkeypatch.chdir(rr.root)

    assert runner.invoke(app, ["refs", "sync"]).exit_code == 2
