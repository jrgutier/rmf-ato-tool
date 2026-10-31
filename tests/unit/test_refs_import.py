import hashlib
import subprocess

import pytest
from _refs_fixtures import entry, make_pdf, make_root
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool.cli import app
from rmf_tool.refs import importer

PDF = make_pdf("dodi")
runner = CliRunner()


def pending(ref_id="DODI-X", **kw):
    return entry(ref_id, publisher="DoD", acquisition="browser-assisted", urls=[],
                 landing_url="https://www.esd.whs.mil/Directives/issuances/dodi/",
                 status="pending-acquisition", **kw)


@pytest.fixture
def rr(tmp_path):
    return make_root(tmp_path, [pending(), entry("OSCAL-X", kind="oscal-catalog",
                                                 local_path="references/oscal/c.json")])


def test_import_from_inbox_verifies_magic_and_pins_sha(rr):
    src = rr.write("references/_inbox/download.pdf", PDF)

    e = importer.import_ref(rr.root, "DODI-X", src, today="2026-10-30")

    assert e["sha256"] == hashlib.sha256(PDF).hexdigest()
    assert (e["size_bytes"], e["downloaded"]) == (len(PDF), "2026-10-30")


def test_import_flips_pending_acquisition_to_ok(rr):
    src = rr.write("references/_inbox/download.pdf", PDF)
    url = "https://www.esd.whs.mil/Portals/54/x.pdf"

    importer.import_ref(rr.root, "DODI-X", src, url=url)

    e = rr.entry("DODI-X")
    assert (e["status"], e["resolved_url"]) == ("ok", url)


def test_import_rejects_html(rr):
    src = rr.write("references/_inbox/download.pdf", b"<!DOCTYPE html><html>403</html>")

    with pytest.raises(importer.ImportRejected, match="not a PDF"):
        importer.import_ref(rr.root, "DODI-X", src)
    assert rr.entry("DODI-X")["status"] == "pending-acquisition"
    assert src.exists()


def test_import_rejects_damaged_pdf(rr):
    src = rr.write("references/_inbox/download.pdf", b"%PDF-1.7\ntruncated")

    with pytest.raises(importer.ImportRejected, match="qpdf"):
        importer.import_ref(rr.root, "DODI-X", src)


def test_import_rejects_unknown_id(rr):
    src = rr.write("references/_inbox/download.pdf", PDF)

    with pytest.raises(importer.ImportRejected, match="unknown reference id"):
        importer.import_ref(rr.root, "NOPE", src)


@pytest.mark.parametrize("ref_id,path,url,match", [
    ("OSCAL-X", "references/_inbox/download.pdf", None, "only PDFs"),
    ("DODI-X", "references/_inbox/missing.pdf", None, "no such file"),
    ("DODI-X", "references/_inbox/download.pdf", "https://example.com/x.pdf", "REF-006"),
])
def test_import_rejections(rr, ref_id, path, url, match):
    rr.write("references/_inbox/download.pdf", PDF)
    with pytest.raises(importer.ImportRejected, match=match):
        importer.import_ref(rr.root, ref_id, rr.root / path, url=url)


def test_import_moves_into_lfs_path(rr):
    src = rr.write("references/_inbox/download.pdf", PDF)

    importer.import_ref(rr.root, "DODI-X", src)

    dest = rr.root / "references/pdf/DODI-X.pdf"
    assert dest.read_bytes() == PDF
    assert not src.exists()
    attr = subprocess.run(["git", "-C", str(REPO_ROOT), "check-attr", "filter", "--",
                           "references/pdf/DODI-X.pdf"], capture_output=True, text=True)
    assert attr.stdout.strip().endswith("filter: lfs")


def test_cli_import(rr, monkeypatch):
    monkeypatch.chdir(rr.root)
    rr.write("references/_inbox/download.pdf", PDF)
    rr.write("references/_inbox/bad.pdf", b"<html>")

    ok = runner.invoke(app, ["refs", "import", "DODI-X", "references/_inbox/download.pdf"])
    bad = runner.invoke(app, ["refs", "import", "DODI-X", "references/_inbox/bad.pdf"])

    assert ok.exit_code == 0 and "imported DODI-X" in ok.stdout
    assert bad.exit_code == 1 and "rejected" in bad.output


def test_import_drops_the_query_and_fragment_so_the_index_still_loads(rr):
    src = rr.write("references/_inbox/download.pdf", PDF)
    url = "https://www.cnss.gov/CNSS/openDoc.cfm?abc=1&doc=2#top"

    importer.import_ref(rr.root, "DODI-X", src, url=url)

    assert rr.entry("DODI-X")["resolved_url"] == "https://www.cnss.gov/CNSS/openDoc.cfm"
    assert rr.index()
