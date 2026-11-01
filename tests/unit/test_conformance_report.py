"""`rmf conformance report` and the `rmf conformance` commands.

The report tests build a small in-memory register, so they pin nothing the phases change;
the command tests run against the committed register and assert only its shape.
"""

import json
import shutil

import _conformance_fixtures as fx
import pytest
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool.cli import app
from rmf_tool.conformance import register, report

runner = CliRunner()


@pytest.fixture(autouse=True)
def at_repo(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)


def small_register(count=12):
    reg = register.Register()
    reg.sources = {
        "DOC": {"ref": "DOC", "mode": "statement"},
        "CAT": {"ref": "CAT", "mode": "catalog"},
        "PEND": {"ref": "PEND", "mode": "statement"},
        "WEB": {"ref": "WEB", "mode": "excluded"},
    }
    entries = [{"id": f"REQ-DOC-{n:04d}", "citation": {"ref": "DOC", "page": 1, "anchor": "a"},
                "kind": "modal", "locator": "", "context": "", "statement": f"s{n}",
                "status": "candidate"} for n in range(1, count + 1)]
    reg.files["DOC"] = {"schema_version": 1, "ref": "DOC", "mode": "statement",
                        "requirements": entries}
    reg.files["CAT"] = {"schema_version": 1, "ref": "CAT", "mode": "catalog",
                        "catalog": "controls", "count": 3, "ids": ["AC-1", "AC-2", "AC-3"],
                        "requirements": [{**entries[0], "id": "REQ-CAT-0001"}]}
    reg.work_items = {"WI-01": {"id": "WI-01", "title": "Open one", "findings": ["N-1"],
                                "status": "open"},
                      "WI-02": {"id": "WI-02", "title": "Closed one", "findings": ["C-1"],
                                "status": "closed", "closed_by": "commit abc1234"}}
    reg.reference_list = [{"document": "DoD Directive 1", "disposition": "excluded",
                           "reason": "Outside the RMF."}]
    index = {"DOC": {"status": "ok", "tier": 2}, "CAT": {"status": "ok"},
             "PEND": {"status": "pending-acquisition", "tier": 1}, "WEB": {"status": "ok"}}
    return reg, index


def mark(reg, count, status):
    entries = [e for _, e in reg.live() if e["status"] == "candidate"]
    for entry in entries[:count]:
        entry["status"] = status


def test_the_summary_keys_the_p13_gate_reads_exist():
    result = runner.invoke(app, ["conformance", "report", "--format", "json"])
    data = json.loads(result.stdout)

    assert result.exit_code == 0
    assert isinstance(data["summary"]["candidate"], int)
    assert isinstance(data["summary"]["work_items"], int)
    assert set(data["summary"]["kinds"]) <= set(("lettered", "table", "modal", "should", "promoted",
                                                  "indicative", "imperative"))


def test_totals_add_up_per_document_and_overall():
    reg, index = small_register()
    data = report.build(reg, index)
    s = data["summary"]

    assert s["total"] == 13 == sum(d["total"] for d in data["documents"])
    assert s["total"] == sum(s[k] for k in register.STATUSES)
    assert s["candidate"] == sum(d["candidate"] for d in data["documents"])
    assert s["kinds"] == {"modal": 13}


def test_the_retired_share_of_each_document_is_reported():
    """However the statuses were set (FW-REQ-004 reads the same share)."""
    reg, index = small_register(12)
    mark(reg, 5, "not-applicable")  # CAT's one entry and four of DOC's twelve

    data = report.build(reg, index)
    row = next(d for d in data["documents"] if d["ref"] == "DOC")

    assert row["retired_share"] == 0.333
    assert any(line.startswith("DOC") and line.rstrip().endswith("33%")
               for line in report.render(data)), report.render(data)[:3]
    assert report.render(data)[0].rstrip().endswith("noise    retired")


def test_the_noise_share_of_each_document_is_its_own_column_and_key():
    """Noise leaves the retired share, so it needs a figure of its own: a share of live entries."""
    reg, index = small_register(12)
    mark(reg, 6, "not-a-requirement")  # CAT's one entry and five of DOC's twelve

    data = report.build(reg, index)
    row = next(d for d in data["documents"] if d["ref"] == "DOC")
    line = next(li for li in report.render(data) if li.startswith("DOC"))

    assert row["noise_share"] == round(5 / 12, 3)
    assert line.split()[-2:] == ["42%", "0%"]


def test_a_pending_document_is_unassessed_and_an_excluded_one_is_neither():
    reg, index = small_register()
    data = report.build(reg, index)

    assert [u["ref"] for u in data["unassessed"]] == ["PEND"]
    assert {d["ref"] for d in data["documents"]} == {"CAT", "DOC"}
    assert data["summary"]["unassessed"] == 1


def test_a_catalog_document_reports_its_id_set_beside_its_prose_entries():
    data = report.build(*small_register())
    row = next(d for d in data["documents"] if d["ref"] == "CAT")

    assert row["mode"] == "catalog" and row["ids"] == 3 and row["total"] == 1


def test_open_work_items_are_listed_and_closed_ones_are_not():
    data = report.build(*small_register())

    assert [w["id"] for w in data["work_items"]] == ["WI-01"]
    assert data["summary"]["work_items"] == 1


def test_a_mostly_partial_register_is_called_out():
    reg, index = small_register()
    mark(reg, 10, "partial")
    mark(reg, 2, "covered")

    data = report.build(reg, index)
    text = "\n".join(report.render(data))

    assert data["summary"]["partial_share"] == pytest.approx(0.833)
    assert "WARNING: the register is mostly partial" in text


def test_a_mostly_covered_register_is_not():
    reg, index = small_register()
    mark(reg, 2, "partial")
    mark(reg, 10, "covered")

    assert "WARNING" not in "\n".join(report.render(report.build(reg, index)))


@pytest.mark.parametrize("kind, tier, blocks", [
    ("should", 1, True), ("table", 1, True), ("modal", None, True), ("lettered", 2, True),
    ("indicative", None, True), ("imperative", 2, True), ("should", None, False),
    ("should", 2, False), ("table", None, False), ("table", 2, False),
])
def test_what_blocks_the_p13_freeze(kind, tier, blocks):
    """FW-REQ-002 (ADR-0005): tier 1 and obligations block; should and table elsewhere warn."""
    assert report.blocks_freeze(kind, tier) is blocks


def test_the_report_splits_candidates_by_what_blocks_the_freeze():
    reg, index = small_register()
    entries = reg.files["DOC"]["requirements"]
    entries[0]["kind"] = "should"
    entries[1]["kind"] = "table"
    entries[2].update(kind="should", status="partial")
    reg.files["CAT"]["requirements"][0]["kind"] = "table"
    index["CAT"]["tier"] = 1
    text = "\n".join(report.render(report.build(reg, index)))

    assert report.build(reg, index)["summary"]["freeze"] == {
        "tier_1": 1, "obligations_elsewhere": 9, "advisory_elsewhere": 2, "deferred": 0,
        "partial_on_weak_evidence": 1}
    assert "1 in tier 1 documents and 9 obligations elsewhere block it; 2 should or table" in text
    assert "0 deferred, 1 partial on evidence that cannot fail" in text


def test_the_report_counts_what_was_set_aside_without_proof():
    """A loop of `mark --status deferred` on a tier 2 document had no line in the report."""
    reg, index = small_register()
    mark(reg, 4, "deferred")  # the catalog's one entry and DOC 1 to 3
    mark(reg, 2, "partial")  # DOC 4 and 5
    reg.files["DOC"]["requirements"][4]["evidence"] = [{"kind": "citation", "target": "P-18"}]

    freeze = report.build(reg, index)["summary"]["freeze"]

    assert (freeze["deferred"], freeze["partial_on_weak_evidence"]) == (4, 2)


def test_a_removed_entry_leaves_the_totals_and_is_listed():
    reg, index = small_register()
    reg.files["DOC"]["requirements"][0]["removed"] = True

    data = report.build(reg, index)

    assert data["summary"]["total"] == 12
    assert data["removed"] == ["REQ-DOC-0001"]


def test_text_report_shows_the_committed_register():
    result = runner.invoke(app, ["conformance", "report"])

    assert result.exit_code == 0
    assert "DODI8510.01" in result.stdout


def test_text_report_names_a_pending_document_as_unassessed(tmp_path, monkeypatch):
    repo = fx.build(tmp_path)
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: repo)
    monkeypatch.setattr("rmf_tool.conformance.register.index_entries", lambda root: fx.index())

    result = runner.invoke(app, ["conformance", "report"])

    assert result.exit_code == 0
    for needle in (fx.DOC, "open work items:", "WI-01", "unassessed documents",
                   f"{fx.PENDING} (tier 1, pending-acquisition)"):
        assert needle in result.stdout


def test_extract_check_passes_on_the_committed_register():
    result = runner.invoke(app, ["conformance", "extract", "--check"])

    assert result.exit_code == 0, result.output
    assert "current" in result.stdout


def test_extract_check_for_one_reference():
    result = runner.invoke(app, ["conformance", "extract", "--id", "FIPS199", "--check"])

    assert result.exit_code == 0, result.output


def test_extract_refuses_an_unknown_reference():
    result = runner.invoke(app, ["conformance", "extract", "--id", "NOPE", "--check"])

    assert result.exit_code == 2
    assert "unknown source" in result.output


def test_extract_writes_and_leaves_a_pending_document_unassessed(tmp_path, monkeypatch):
    repo = fx.build(tmp_path)
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: repo)
    monkeypatch.setattr("rmf_tool.conformance.register.index_entries", lambda root: fx.index())
    target = repo / register.requirements_path(fx.DOC)
    target.unlink()

    written = runner.invoke(app, ["conformance", "extract", "--id", fx.DOC])
    unassessed = runner.invoke(app, ["conformance", "extract", "--id", fx.PENDING])

    assert written.exit_code == 0 and fx.DOC in written.stdout and target.is_file()
    assert unassessed.exit_code == 0
    assert f"{fx.PENDING}: pending-acquisition, unassessed" in unassessed.stdout
    assert not (repo / register.requirements_path(fx.PENDING)).exists()


def test_accept_text_and_mark_commands(tmp_path, monkeypatch):
    repo = fx.build(tmp_path)
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: repo)
    monkeypatch.setattr("rmf_tool.conformance.register.index_entries", lambda root: fx.index())
    text = repo / f"references/text/{fx.DOC}.md"
    text.write_text(text.read_text().replace("Appendix A", "Appendix B"))

    accepted = runner.invoke(app, ["conformance", "accept-text", "--id", fx.DOC])
    marked = runner.invoke(app, ["conformance", "mark", f"REQ-{fx.DOC}-0002", "--status",
                                 "partial", "--reason", "Half done.", "--evidence",
                                 '[{"kind": "citation", "target": "P-18"}]'])
    again = runner.invoke(app, ["conformance", "accept-text"])
    bad = runner.invoke(app, ["conformance", "mark", f"REQ-{fx.DOC}-0002", "--evidence", "{"])
    nothing = runner.invoke(app, ["conformance", "mark", f"REQ-{fx.DOC}-0002"])

    assert accepted.exit_code == 0 and f"{fx.DOC}: updated" in accepted.stdout
    assert marked.exit_code == 0, marked.output
    entry = fx.entry(fx.load(repo), 2)
    assert entry["status"] == "partial" and entry["evidence"][0]["target"] == "P-18"
    assert again.exit_code == 0 and "current" in again.stdout
    assert bad.exit_code == 2 and nothing.exit_code == 2


def test_unreadable_conformance_data_is_a_usage_error(tmp_path, monkeypatch):
    shutil.copytree(REPO_ROOT / "conformance/schema", tmp_path / "conformance/schema")
    shutil.copytree(REPO_ROOT / "references/schema", tmp_path / "references/schema")
    shutil.copy(REPO_ROOT / "references/index.yaml", tmp_path / "references/index.yaml")
    (tmp_path / "conformance/sources.yaml").write_text("schema_version: 2\n")
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: tmp_path)

    result = runner.invoke(app, ["conformance", "report"])

    assert result.exit_code == 2


def test_promote_and_page_commands(tmp_path, monkeypatch):
    repo = fx.build(tmp_path)
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: repo)
    monkeypatch.setattr("rmf_tool.conformance.register.index_entries", lambda root: fx.index())

    before = runner.invoke(app, ["conformance", "page", fx.DOC, "1"])
    promoted = runner.invoke(app, ["conformance", "promote", fx.DOC, "--page", "1", "--anchor",
                                   "The owner", "--reason", "It names who the list binds."])
    after = runner.invoke(app, ["conformance", "page", fx.DOC, "1"])
    report_ = runner.invoke(app, ["conformance", "report"])
    missing = runner.invoke(app, ["conformance", "promote", fx.DOC, "--page", "1", "--anchor",
                                  "not on the page", "--reason", "x"])
    unknown = runner.invoke(app, ["conformance", "page", "NOPE", "1"])

    assert before.exit_code == 0, before.output
    assert before.stdout.splitlines()[0] == f"{fx.DOC} page 1: 3 entries, 1 rejected"
    assert "rejected [lead-in] 2.1: The owner:" in before.stdout
    assert promoted.exit_code == 0, promoted.output
    assert promoted.stdout.strip() == f"REQ-{fx.DOC}-0004 p1 [promoted] 2.1: The owner:"
    assert after.stdout.splitlines()[0] == f"{fx.DOC} page 1: 4 entries, 0 rejected"
    assert f"REQ-{fx.DOC}-0004 [promoted] candidate 2.1: The owner:" in after.stdout
    assert fx.entry(fx.load(repo), 4)["promoted"] == {"reason": "It names who the list binds."}
    assert report_.exit_code == 0 and "promoted by a reviewer" in report_.stdout
    assert missing.exit_code == 2 and "in no rejection and no paragraph" in missing.output
    assert unknown.exit_code == 2


def test_sample_draws_by_status_with_the_same_seed_the_same_sample(tmp_path, monkeypatch):
    repo = fx.build(tmp_path)
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: repo)
    monkeypatch.setattr("rmf_tool.conformance.register.index_entries", lambda root: fx.index())
    reg = fx.load(repo)
    register.mark(reg, f"REQ-{fx.DOC}-0002", status="not-a-requirement", reason="A heading here.")
    register.mark(reg, f"REQ-{fx.DOC}-0003", status="not-a-requirement", reason="Another heading.")
    fx.write(repo, reg)
    args = ["conformance", "sample", "--seed", "7", "-n", "5", "--status", "not-a-requirement"]

    first = runner.invoke(app, args)
    second = runner.invoke(app, args)
    other = runner.invoke(app, [*args[:-1], "candidate"])

    assert first.exit_code == 0, first.output
    assert first.stdout == second.stdout
    assert first.stdout.splitlines()[0] == "population 2, seed 7, sample 2"
    assert f"REQ-{fx.DOC}-0002" in first.stdout and "A heading here." in first.stdout
    assert f"REQ-{fx.DOC}-0001" not in first.stdout and f"REQ-{fx.DOC}-0002" not in other.stdout


@pytest.mark.parametrize("extra, message", [
    (["--status", "nonsense"], "unknown status"),
    (["--status", "candidate", "--rejected"], "--status samples entries"),
])
def test_sample_refuses_a_status_it_cannot_draw(tmp_path, monkeypatch, extra, message):
    repo = fx.build(tmp_path)
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: repo)
    monkeypatch.setattr("rmf_tool.conformance.register.index_entries", lambda root: fx.index())

    result = runner.invoke(app, ["conformance", "sample", "--seed", "1", *extra])

    assert result.exit_code == 2 and message in result.output
