import hashlib
import json
from pathlib import Path

import pytest
from _refs_fixtures import SHA_A, SHA_B, entry, make_pdf, make_root, required_entries
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import ci, refs
from rmf_tool.cli import app
from rmf_tool.profiles import Profile
from rmf_tool.refs import extract, verify

PDF = make_pdf("v")
PDF_SHA = hashlib.sha256(PDF).hexdigest()
runner = CliRunner()


def ok_entry(ref_id="DOC-A", **kw):
    return entry(ref_id, status="ok", sha256=PDF_SHA, size_bytes=len(PDF),
                 downloaded="2026-10-29", **kw)


def rules(findings, rule, sev=None):
    return [f for f in findings if f.rule == rule and (sev is None or f.severity == sev)]


@pytest.fixture
def rr(tmp_path):
    rr = make_root(tmp_path, [*required_entries(), ok_entry()])
    rr.write("references/pdf/DOC-A.pdf", PDF)
    return rr


def test_pending_required_is_warning_before_p2x_error_at_p2x(rr):
    loose = verify.verify(rr.root, rr.index())
    strict = verify.verify(rr.root, rr.index(), strict=True)

    assert len(rules(loose, "REF-001", "W")) == len(verify.REQUIRED_IDS)
    assert rules(loose, "REF-001", "E") == []
    assert len(rules(strict, "REF-001", "E")) == len(verify.REQUIRED_IDS)


def test_non_required_pending_stays_warning_when_strict(tmp_path):
    rr = make_root(tmp_path, [*required_entries(), entry(
        "OPT", acquisition="browser-assisted", urls=[], landing_url="https://www.cnss.gov/",
        status="pending-acquisition")])
    findings = verify.verify(rr.root, rr.index(), strict=True, ids=["OPT"])
    assert [f.severity for f in rules(findings, "REF-001")] == ["W"]


@pytest.mark.parametrize("status", ["missing", "manual-required", "changed"])
def test_auto_entry_not_ok_is_error(tmp_path, status):
    rr = make_root(tmp_path, [*required_entries(), entry(status=status)])
    findings = verify.verify(rr.root, rr.index(), ids=["DOC-A"])
    assert [f.severity for f in rules(findings, "REF-001")] == ["E"]


def test_degraded_is_warning(tmp_path):
    degraded = entry(status="degraded", degraded={
        "approved_by": "user", "date": "2026-11-01", "reason": "not public",
        "fallback_refs": ["SP800-53B"]})
    rr = make_root(tmp_path, [*required_entries(), degraded])
    findings = verify.verify(rr.root, rr.index(), strict=True, ids=["DOC-A"])
    assert [(f.severity, "not public" in f.message) for f in rules(findings, "REF-001")] == [
        ("W", True)]


def test_required_set_mismatch_is_error(tmp_path):
    rr = make_root(tmp_path, [*required_entries()[1:], ok_entry(required=True)])
    [finding] = rules(verify.verify(rr.root, rr.index()), "REF-001", "E")
    assert "SP800-37R2" in finding.message and "DOC-A" in finding.message


def test_sha_mismatch_and_missing_file(rr):
    assert rules(verify.verify(rr.root, rr.index()), "REF-002") == []
    (rr.root / "references/pdf/DOC-A.pdf").write_bytes(make_pdf("tampered"))
    [mismatch] = rules(verify.verify(rr.root, rr.index()), "REF-002")
    (rr.root / "references/pdf/DOC-A.pdf").unlink()
    [missing] = rules(verify.verify(rr.root, rr.index()), "REF-002")

    assert "!= pinned" in mismatch.message
    assert "file missing" in missing.message


def test_lfs_pointer_oid_accepted(rr):
    rr.write("references/pdf/DOC-A.pdf",
             f"version https://git-lfs.github.com/spec/v1\noid sha256:{PDF_SHA}\nsize 9\n")
    assert rules(verify.verify(rr.root, rr.index()), "REF-002") == []
    rr.write("references/pdf/DOC-A.pdf",
             f"version https://git-lfs.github.com/spec/v1\noid sha256:{SHA_A}\nsize 9\n")
    assert len(rules(verify.verify(rr.root, rr.index()), "REF-002")) == 1


def test_disallowed_urls(tmp_path):
    rr = make_root(tmp_path, [*required_entries(), entry(
        urls=["https://example.com/a.pdf"], landing_url="http://csrc.nist.gov/x",
        resolved_url="https://release-assets.githubusercontent.com/x")])
    messages = [f.message for f in rules(verify.verify(rr.root, rr.index()), "REF-006")]
    assert len(messages) == 3
    assert any("example.com" in m for m in messages)
    assert any("not https" in m for m in messages)
    assert any("redirect target" in m for m in messages)


def test_release_asset_resolved_url_allowed_after_usnistgov_url(tmp_path):
    rr = make_root(tmp_path, [*required_entries(), entry(
        kind="oscal-schema", local_path="references/oscal/s.json",
        urls=["https://github.com/usnistgov/OSCAL/releases/download/v1.2.1/s.json"],
        resolved_url="https://release-assets.githubusercontent.com/x")])
    assert rules(verify.verify(rr.root, rr.index()), "REF-006") == []


def test_real_repo_verify_has_no_errors():
    findings = verify.verify(Path(REPO_ROOT), refs.load_index(Path(REPO_ROOT)))
    assert [f for f in findings if f.severity == "E"] == []


def test_cli_verify_required_exit_codes(rr, monkeypatch):
    monkeypatch.chdir(rr.root)
    loose = runner.invoke(app, ["refs", "verify", "--id", "DOC-A", "--format", "json"])
    strict = runner.invoke(app, ["refs", "verify", "--required"])

    assert loose.exit_code == 0
    assert json.loads(loose.stdout)["summary"]["errors"] == 0
    assert strict.exit_code == 1
    assert "REF-001" in strict.output


# --- REF-003 (rmf refs extract --check) ------------------------------------------------

TEXT_MD = "<!-- preamble -->\n\n<!-- page 1 -->\nbody\n"


def with_text(rr, text_sha=None, source=PDF_SHA):
    index = rr.index()
    e = refs.find(index, "DOC-A")
    e["text"] = {"path": "references/text/DOC-A.md", "source_sha256": source,
                 "extractor": "pymupdf", "extractor_version": "2.0", "rmf_extract_version": "1",
                 "pages": 1, "ocr": False, "ocr_pages": [],
                 "sha256": text_sha or hashlib.sha256(TEXT_MD.encode()).hexdigest()}
    refs.save_index(rr.root, index)
    rr.write("references/text/DOC-A.md", TEXT_MD)


@pytest.fixture
def fake_check(monkeypatch):
    calls = []

    def check(doc_id, pdf_path, out_dir, *, source_sha256, extractor, text_sha256=None):
        calls.append((doc_id, pdf_path.name, out_dir.name, source_sha256, extractor,
                      text_sha256))
        return []

    monkeypatch.setattr(extract, "check", check)
    return calls


def test_check_texts_missing_text_block(rr, fake_check):
    [f] = verify.check_texts(rr.root, rr.index())
    assert f.rule == "REF-003" and "no text extraction" in f.message
    assert fake_check == []


def test_check_texts_ok_calls_extract_check(rr, fake_check):
    with_text(rr)
    assert verify.check_texts(rr.root, rr.index()) == []
    assert fake_check == [("DOC-A", "DOC-A.pdf", "text", PDF_SHA, "pymupdf",
                           hashlib.sha256(TEXT_MD.encode()).hexdigest())]


def test_check_texts_passes_recorded_text_sha(rr, fake_check):
    with_text(rr, text_sha=SHA_B)
    verify.check_texts(rr.root, rr.index())
    assert fake_check[0][-1] == SHA_B


def test_check_texts_detects_source_mismatch(rr, fake_check):
    with_text(rr, source=SHA_A)
    [f] = verify.check_texts(rr.root, rr.index())
    assert "source_sha256" in f.message


def test_check_texts_reports_extract_problems(rr, monkeypatch):
    with_text(rr)
    monkeypatch.setattr(extract, "check", lambda *a, **kw: ["DOC-A: stale text"])
    [f] = verify.check_texts(rr.root, rr.index())
    assert (f.rule, f.message, f.path) == ("REF-003", "DOC-A: stale text",
                                           "references/text/DOC-A.md")


def test_cli_extract_check(rr, fake_check, monkeypatch):
    monkeypatch.chdir(rr.root)
    missing = runner.invoke(app, ["refs", "extract", "--check"])
    with_text(rr)
    ok = runner.invoke(app, ["refs", "extract", "--check", "--id", "DOC-A"])

    assert missing.exit_code == 1 and "REF-003" in missing.output
    assert ok.exit_code == 0


# --- ci steps for p2 / p2x ---------------------------------------------------------------


def _ctx(root):
    return ci.Context(root, None, slow=False, capture=True)


def test_ci_p2_steps_and_p2x_strictness(rr):
    rr.write("references/INDEX.md", "stale\n")
    p2 = Profile("p2", frozenset({"p1", "p2"}))
    p2x = Profile("p2x", frozenset({"p1", "p2", "p2x"}))
    steps = tuple(s for s in ci.STEPS if s.phase in ("p2", "p2x"))

    by_name = {r.name: r for r in ci.run(p2, _ctx(rr.root), steps)}
    strict = {r.name: r for r in ci.run(p2x, _ctx(rr.root), steps)}

    assert set(by_name) == {"refs verify", "refs extract --check", "refs index --check"}
    assert not by_name["refs index --check"].ok  # stale INDEX.md
    assert not by_name["refs extract --check"].ok  # DOC-A has no text
    assert not by_name["refs verify"].ok  # REF-005: no VERSIONS.yaml in the tmp root
    assert {f.severity for f in by_name["refs verify"].findings
            if f.rule == "REF-001"} == {"W"}
    assert "refs verify" not in strict and "refs verify (strict)" in strict
    assert {f.severity for f in strict["refs verify (strict)"].findings
            if f.rule == "REF-001"} == {"E"}


def test_ci_refs_step_reports_bad_index(tmp_path):
    rr = make_root(tmp_path, [entry(status="lost")])
    p2 = Profile("p2", frozenset({"p2"}))
    step = next(s for s in ci.STEPS if s.name == "refs verify")
    [result] = ci.run(p2, _ctx(rr.root), (step,))
    assert not result.ok and result.findings[0].rule == "REF-001"
