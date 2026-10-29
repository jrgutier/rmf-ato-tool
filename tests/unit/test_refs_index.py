from pathlib import Path

import pytest
from _refs_fixtures import SHA_A, SHA_B, entry, make_root
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import refs
from rmf_tool.cli import app
from rmf_tool.refs import index_render

runner = CliRunner()

TEXT = {"path": "references/text/DOC-A.md", "source_sha256": SHA_A, "extractor": "pymupdf",
        "extractor_version": "2.0", "rmf_extract_version": "1", "pages": 3, "sha256": SHA_B,
        "ocr": False, "ocr_pages": []}

GOLDEN = """\
# Reference library

Generated from `references/index.yaml` by `uv run rmf refs index`. Do not edit; regenerate.
PDFs live in `pdf/` (Git LFS), text extractions in `text/`, NIST OSCAL content in `oscal/`.
Status `pending-acquisition` entries are acquired browser-assisted by the user
(`playbooks/_ops/fetch-blocked-refs.md`).

## Documents

| ID | Title | Revision | Req. | Status | URL | Downloaded | SHA-256 | Text |
|---|---|---|---|---|---|---|---|---|
| DOC-A | A \\| B title | Rev. 1 | no | ok | <https://nvlpubs.nist.gov/DOC-A.pdf> | 2026-10-29 | `{a}` | [DOC-A.md](text/DOC-A.md) (3 pp.) |
| DOC-B | Title of DOC-B | Rev. 1 | yes | pending-acquisition | <https://www.esd.whs.mil/> | — | — | — |

## OSCAL

| ID | Title | Revision | Status | URL | Downloaded | SHA-256 |
|---|---|---|---|---|---|---|
| OSCAL-C | Title of OSCAL-C | Rev. 1 | missing | <https://raw.githubusercontent.com/usnistgov/c.json> | — | — |

## Citation only

| ID | Title | Revision | URL |
|---|---|---|---|
| WEB-D | Title of WEB-D | Rev. 1 | <https://public.cyber.mil/stigs/> |
""".replace("{a}", SHA_A)  # noqa: E501


def golden_entries():
    return [
        entry("DOC-A", title="A | B\n title", status="ok", sha256=SHA_A, size_bytes=10,
              downloaded="2026-10-29", text=TEXT),
        entry("DOC-B", required=True, acquisition="browser-assisted", urls=[],
              landing_url="https://www.esd.whs.mil/", status="pending-acquisition"),
        entry("OSCAL-C", kind="oscal-catalog",
              urls=["https://raw.githubusercontent.com/usnistgov/c.json"],
              local_path="references/oscal/c.json"),
        entry("WEB-D", kind="web", acquisition="none", urls=[],
              landing_url="https://public.cyber.mil/stigs/", local_path=None, status="ok"),
    ]


def test_index_schema_valid():
    index = refs.load_index(Path(REPO_ROOT))
    assert refs.schema_errors(Path(REPO_ROOT), index) == []
    ids = [e["id"] for e in index["references"]]
    assert len(ids) == len(set(ids))


def test_index_round_trip_is_canonical():
    text = (REPO_ROOT / refs.INDEX_PATH).read_text(encoding="utf-8")
    assert refs.dump_index(refs.load_index(Path(REPO_ROOT))) == text


def test_index_md_golden(tmp_path):
    rr = make_root(tmp_path, golden_entries())
    assert index_render.render(rr.index()) == GOLDEN


def test_real_index_md_current():
    assert index_render.check(Path(REPO_ROOT), refs.load_index(Path(REPO_ROOT))) == []


def test_pending_acquisition_status_valid():
    index = refs.load_index(Path(REPO_ROOT))
    for e in index["references"]:
        if e["acquisition"] == "browser-assisted" and e["status"] != "ok":
            assert e["status"] in ("pending-acquisition", "degraded"), e["id"]
        if e["status"] == "pending-acquisition":
            assert e["acquisition"] == "browser-assisted" and e["landing_url"], e["id"]


def test_blocked_hosts_are_browser_assisted():
    index = refs.load_index(Path(REPO_ROOT))
    for e in index["references"]:
        hosts = " ".join([*e["urls"], e["landing_url"] or ""])
        if any(h in hosts for h in ("esd.whs.mil", "cnss.gov", "dodcio.defense.gov")):
            assert e["acquisition"] == "browser-assisted", e["id"]


@pytest.mark.parametrize("overrides,needle", [
    ({"status": "lost"}, "status"),
    ({"status": "ok"}, "sha256"),  # ok needs sha256/size/date (null here)
    ({"kind": "oscal-catalog", "text": TEXT}, "text"),
    ({"status": "degraded"}, "degraded"),
    ({"acquisition": "auto", "urls": []}, "urls"),
    ({"surprise": 1}, "surprise"),
    ({"id": "lower-case"}, "id"),
    ({"sha256": "XYZ"}, "sha256"),
])
def test_schema_rejects(tmp_path, overrides, needle):
    rr = make_root(tmp_path, [entry(**overrides)])
    with pytest.raises(refs.IndexFileError, match="schema violation") as exc:
        rr.index()
    assert needle in str(exc.value)


def test_load_index_errors(tmp_path):
    rr = make_root(tmp_path)
    (rr.root / refs.INDEX_PATH).write_text("references: [unclosed\n", encoding="utf-8")
    with pytest.raises(refs.IndexFileError, match="not valid YAML"):
        rr.index()
    (rr.root / refs.INDEX_PATH).unlink()
    with pytest.raises(refs.IndexFileError, match="index.yaml"):
        rr.index()


def test_save_index_writes_only_on_change(tmp_path):
    rr = make_root(tmp_path)
    index = rr.index()
    assert refs.save_index(rr.root, index) is False
    index["references"][0]["revision_note"] = "changed"
    assert refs.save_index(rr.root, index) is True
    assert rr.entry("DOC-A")["revision_note"] == "changed"


def test_lfs_pointer_oid(tmp_path):
    ptr = tmp_path / "p.pdf"
    ptr.write_text(f"version https://git-lfs.github.com/spec/v1\noid sha256:{SHA_A}\n"
                   "size 12\n", encoding="utf-8")
    real = tmp_path / "r.pdf"
    real.write_bytes(b"%PDF-1.4")
    assert refs.lfs_pointer_oid(ptr) == SHA_A
    assert refs.lfs_pointer_oid(real) is None


def test_cli_index_write_and_check(tmp_path, monkeypatch):
    rr = make_root(tmp_path, golden_entries())
    monkeypatch.chdir(rr.root)

    stale = runner.invoke(app, ["refs", "index", "--check"])
    write = runner.invoke(app, ["refs", "index"])
    again = runner.invoke(app, ["refs", "index"])
    ok = runner.invoke(app, ["refs", "index", "--check", "--format", "json"])

    assert stale.exit_code == 1 and "REF-004" in stale.output
    assert write.exit_code == 0 and "written" in write.stdout
    assert "unchanged" in again.stdout
    assert ok.exit_code == 0 and '"errors": 0' in ok.stdout
    assert (rr.root / index_render.INDEX_MD).read_text(encoding="utf-8") == GOLDEN
    (rr.root / index_render.INDEX_MD).write_text("edited\n", encoding="utf-8")
    assert runner.invoke(app, ["refs", "index", "--check"]).exit_code == 1


def test_cli_bad_index_is_usage_error(tmp_path, monkeypatch):
    rr = make_root(tmp_path, [entry(status="lost")])
    monkeypatch.chdir(rr.root)

    result = runner.invoke(app, ["refs", "index"])

    assert result.exit_code == 2
    assert "schema violation" in result.output
