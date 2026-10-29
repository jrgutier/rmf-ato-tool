import ast
import hashlib
import json
import ssl
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from _refs_fixtures import entry, make_pdf, make_root
from conftest import REPO_ROOT
from typer.testing import CliRunner
from werkzeug import Response

from rmf_tool import refs
from rmf_tool.cli import app
from rmf_tool.refs import domains, fetch

PDF = make_pdf("one")
PDF2 = make_pdf("two")
runner = CliRunner()


def _allow_local(url, redirected_from=None):
    if urlsplit(url).hostname in ("localhost", "127.0.0.1"):
        return None
    return domains.disallowed_reason(url, redirected_from)


@pytest.fixture(autouse=True)
def local_allowed(monkeypatch):
    monkeypatch.setattr(fetch, "disallowed_reason", _allow_local)


def run(rr, **kw):
    return fetch.fetch(rr.root, today="2026-10-29", **kw)


def test_fetch_uses_ranged_get_never_head(tmp_path, httpserver):
    httpserver.expect_request("/a.pdf").respond_with_data(PDF, content_type="application/pdf")
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])

    [result] = run(rr)

    assert result.status == "downloaded"
    methods = [req.method for req, _ in httpserver.log]
    assert methods == ["GET", "GET"]
    probe, full = (req for req, _ in httpserver.log)
    assert probe.headers["Range"] == fetch.PROBE_RANGE
    assert "Range" not in full.headers
    assert probe.headers["User-Agent"].startswith("rmf-tool/")


def test_fetch_ok_records_sha_size_date_resolved_url(tmp_path, httpserver):
    httpserver.expect_request("/old.pdf").respond_with_response(
        Response(status=302, headers={"Location": "/new.pdf"}))
    httpserver.expect_request("/new.pdf").respond_with_data(PDF)
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/old.pdf")])])

    [result] = run(rr)
    e = rr.entry("DOC-A")

    assert result.status == "downloaded"
    assert e["sha256"] == hashlib.sha256(PDF).hexdigest()
    assert e["size_bytes"] == len(PDF)
    assert e["downloaded"] == "2026-10-29"
    assert e["resolved_url"] == httpserver.url_for("/new.pdf")
    assert e["status"] == "ok"
    assert (rr.root / "references/pdf/DOC-A.pdf").read_bytes() == PDF
    log = [json.loads(line) for line in (rr.root / "references/fetch-log.jsonl").open()]
    assert log[0]["result"] == "downloaded"
    assert [h["status"] for h in log[0]["attempts"][0]["hops"]] == [302, 200, 302, 200]


def test_rerun_noop_when_sha_matches(tmp_path, httpserver):
    httpserver.expect_request("/a.pdf").respond_with_data(PDF)
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])
    run(rr)
    index_before = (rr.root / "references/index.yaml").read_text()
    pdf = rr.root / "references/pdf/DOC-A.pdf"
    mtime = pdf.stat().st_mtime_ns

    [result] = fetch.fetch(rr.root, today="2030-01-01")

    assert result.status == "unchanged"
    assert (rr.root / "references/index.yaml").read_text() == index_before
    assert pdf.stat().st_mtime_ns == mtime
    assert not list(pdf.parent.glob(".fetch-*"))


def test_missing_only_skips_present_files(tmp_path, httpserver):
    httpserver.expect_request("/a.pdf").respond_with_data(PDF)
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])
    run(rr)
    httpserver.clear_log()

    [result] = run(rr, missing_only=True)

    assert result.status == "unchanged"
    assert httpserver.log == []


def test_html_masquerading_as_pdf_rejected(tmp_path, httpserver):
    httpserver.expect_request("/a.pdf").respond_with_data(
        b"<html><body>Access denied</body></html>", content_type="application/pdf")
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])

    [result] = run(rr)

    assert result.status == "manual-required"
    assert "not a PDF" in result.message
    assert not (rr.root / "references/pdf/DOC-A.pdf").exists()


def test_qpdf_check_failure_rejected(tmp_path, httpserver):
    httpserver.expect_request("/a.pdf").respond_with_data(b"%PDF-1.4\ngarbage\n")
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])

    [result] = run(rr)

    assert result.status == "manual-required"
    assert "qpdf --check failed" in result.message
    assert not list((rr.root / "references/pdf").iterdir())


def test_redirect_to_disallowed_domain_rejected(tmp_path, httpserver):
    httpserver.expect_request("/a.pdf").respond_with_response(
        Response(status=301, headers={"Location": "https://evil.example.com/a.pdf"}))
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])

    [result] = run(rr)

    assert result.status == "manual-required"
    assert "REF-006" in result.message and "evil.example.com" in result.message
    assert len(httpserver.log) == 1


def test_disallowed_configured_url_never_requested(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "disallowed_reason", domains.disallowed_reason)
    rr = make_root(tmp_path, [entry(urls=["https://example.com/a.pdf"])])

    [result] = run(rr)

    assert result.status == "manual-required"
    assert "REF-006" in result.message


def test_too_many_redirects(tmp_path, httpserver):
    httpserver.expect_request("/loop.pdf").respond_with_response(
        Response(status=302, headers={"Location": "/loop.pdf"}))
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/loop.pdf")])])

    [result] = run(rr)

    assert result.status == "manual-required"
    assert "redirects" in result.message


def test_404_falls_back_to_next_url(tmp_path, httpserver):
    httpserver.expect_request("/gone.pdf").respond_with_data("nope", status=404)
    httpserver.expect_request("/b.pdf").respond_with_data(PDF)
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/gone.pdf"),
                                          httpserver.url_for("/b.pdf")])])

    [result] = run(rr)

    assert result.status == "downloaded"
    assert rr.entry("DOC-A")["resolved_url"] == httpserver.url_for("/b.pdf")


def test_full_get_failure_after_probe(tmp_path, httpserver):
    httpserver.expect_ordered_request("/a.pdf").respond_with_data(PDF[:1024], status=206)
    httpserver.expect_ordered_request("/a.pdf").respond_with_data("busy", status=503)
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])

    [result] = run(rr)

    assert result.status == "manual-required"
    assert "HTTP 503" in result.message


def test_all_urls_fail_marks_manual_required_exit1(tmp_path, httpserver, monkeypatch):
    httpserver.expect_request("/a.pdf").respond_with_data("nope", status=404)
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])
    monkeypatch.chdir(rr.root)

    result = runner.invoke(app, ["refs", "fetch", "--format", "json"])
    data = json.loads(result.stdout)

    assert result.exit_code == 1
    assert data["ok"] is False
    assert data["results"][0]["status"] == "manual-required"
    assert rr.entry("DOC-A")["status"] == "manual-required"


def test_browser_assisted_entries_skipped_by_fetch(tmp_path, httpserver):
    rr = make_root(tmp_path, [entry(acquisition="browser-assisted",
                                    urls=[httpserver.url_for("/x.pdf")],
                                    landing_url="https://www.esd.whs.mil/",
                                    status="pending-acquisition")])

    [result] = run(rr)

    assert result.status == "skipped"
    assert httpserver.log == []
    assert rr.entry("DOC-A")["status"] == "pending-acquisition"


def test_sha_mismatch_reports_changed_preserves_file(tmp_path, httpserver):
    httpserver.expect_request("/a.pdf").respond_with_data(PDF2)
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])
    pdf = rr.write("references/pdf/DOC-A.pdf", PDF)
    pinned = hashlib.sha256(PDF).hexdigest()
    index = rr.index()
    index["references"][0].update(sha256=pinned, size_bytes=len(PDF), downloaded="2026-01-01",
                                  status="ok")
    rr.write("references/index.yaml", refs.dump_index(index))

    [result] = run(rr)

    assert result.status == "changed"
    assert pdf.read_bytes() == PDF
    e = rr.entry("DOC-A")
    assert (e["status"], e["sha256"], e["downloaded"]) == ("changed", pinned, "2026-01-01")

    [accepted] = run(rr, accept_new=True, note="upd2 published")
    e = rr.entry("DOC-A")
    assert accepted.status == "accepted"
    assert pdf.read_bytes() == PDF2
    assert (e["status"], e["sha256"], e["revision_note"]) == (
        "ok", hashlib.sha256(PDF2).hexdigest(), "upd2 published")


def test_accept_new_requires_note(tmp_path, monkeypatch):
    rr = make_root(tmp_path)
    monkeypatch.chdir(rr.root)

    result = runner.invoke(app, ["refs", "fetch", "--accept-new"])

    assert result.exit_code == 2
    assert "--note" in result.output


def test_unknown_id_is_usage_error(tmp_path, monkeypatch):
    rr = make_root(tmp_path)
    monkeypatch.chdir(rr.root)

    result = runner.invoke(app, ["refs", "fetch", "--id", "NOPE"])

    assert result.exit_code == 2
    assert "NOPE" in result.output


def test_cli_fetch_text_output(tmp_path, httpserver, monkeypatch):
    httpserver.expect_request("/a.pdf").respond_with_data(PDF)
    rr = make_root(tmp_path, [entry(urls=[httpserver.url_for("/a.pdf")])])
    monkeypatch.chdir(rr.root)

    result = runner.invoke(app, ["refs", "fetch", "--id", "DOC-A"])

    assert result.exit_code == 0
    assert "downloaded" in result.stdout and "DOC-A" in result.stdout


@pytest.mark.parametrize("kind,body,ok", [
    ("oscal-catalog", b'{"catalog": {}}', True),
    ("oscal-catalog", b'{"profile": {}}', False),
    ("oscal-schema", b'{"$schema": "x"}', True),
    ("oscal-schema", b'{"title": "x"}', False),
    ("oscal-example", b'[1, 2]', False),
    ("oscal-profile", b'{"profile": ', False),
])
def test_json_kinds_validated(tmp_path, kind, body, ok):
    path = tmp_path / "x.json"
    path.write_bytes(body)
    assert (fetch.validate_file(path, kind) is None) is ok


def test_json_probe_rejects_html(tmp_path, httpserver):
    httpserver.expect_request("/c.json").respond_with_data("<html>")
    rr = make_root(tmp_path, [entry("OSCAL-X", kind="oscal-catalog",
                                    urls=[httpserver.url_for("/c.json")],
                                    local_path="references/oscal/c.json")])

    [result] = run(rr)

    assert result.status == "manual-required"
    assert "not JSON" in result.message


def test_qpdf_missing_is_reported(tmp_path, monkeypatch):
    path = tmp_path / "a.pdf"
    path.write_bytes(PDF)

    def no_qpdf(*a, **kw):
        raise FileNotFoundError("qpdf")

    monkeypatch.setattr(fetch.subprocess, "run", no_qpdf)
    assert "qpdf not found" in fetch.validate_file(path, "pdf")


def test_no_tls_verify_disable():
    client = fetch.make_client()
    assert client._transport._pool._ssl_context.verify_mode == ssl.CERT_REQUIRED
    for path in Path(REPO_ROOT / "src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "verify":
                value = node.value
                assert not (isinstance(value, ast.Constant) and value.value is False), path
            if isinstance(node, ast.Attribute):
                assert node.attr != "CERT_NONE", path
