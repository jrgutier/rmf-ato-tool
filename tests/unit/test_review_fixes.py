"""Regressions for the bug review of 2026-11-18: a check or build that meets run data of the
wrong shape reports it instead of raising, and commands that rewrite a fork's files keep them."""

import pytest
from conftest import REPO_ROOT, edit_yaml
from typer.testing import CliRunner

from rmf_tool import build
from rmf_tool.check import engine
from rmf_tool.ci import StepResult
from rmf_tool.cli import app
from rmf_tool.refs import fetch as fetch_mod
from rmf_tool.run import poam_dates
from rmf_tool.run.migrate import migrate, migrate_providers
from rmf_tool.run.model import open_run, read_yaml
from rmf_tool.workspace import new_workspace

runner = CliRunner()
DATA = "artifacts/data"
ORG = f"{DATA}/org-context.yaml"
ITEMS = "artifacts/poam/items.yaml"


def _evaluate(run_dir):
    return engine.evaluate(open_run(run_dir, REPO_ROOT)).findings


def _shape_errors(run_dir):
    return [f.finding.message for f in _evaluate(run_dir)
            if f.rule == engine.SHAPE_RULE and "could not judge" in f.finding.message]


MANGLES = {
    "a string where a mapping belongs": (f"{DATA}/rar.yaml",
                                         lambda d: d.update(determination="accepted")),
    "a mapping used as an ID": (f"{DATA}/authorizations.yaml",
                                lambda d: d["records"][0].update(id={"x": 1})),
    "a string where a list of records belongs": (ITEMS, lambda d: d.update(items="x")),
    "a number compared with text": (ITEMS, lambda d: d["items"][0].update(priority="x")),
    "run.yaml scope as text": ("run.yaml", lambda d: d.update(scope="x")),
}


@pytest.mark.parametrize("label", MANGLES)
def test_a_wrongly_typed_value_is_a_finding_not_a_traceback(minimal_run, label):
    rel, mangle = MANGLES[label]
    edit_yaml(minimal_run / rel, mangle)
    found = _evaluate(minimal_run)  # must not raise
    assert any(f.error and f.rule == engine.SHAPE_RULE for f in found)


def test_a_rule_stopped_by_bad_data_is_named_as_a_run_wide_error(minimal_run):
    edit_yaml(minimal_run / f"{DATA}/rar.yaml", lambda d: d.update(determination="accepted"))
    run = open_run(minimal_run, REPO_ROOT)
    ev = engine.evaluate(run)
    stopped = [f for f in ev.findings if "could not judge" in f.finding.message]
    assert stopped and all(f.run_wide and f.error for f in stopped)
    # a task selection cannot hide it
    first = run.order[0]
    assert any("could not judge" in f.message for f in engine.select(run, ev, task=first))


def test_valid_data_raises_no_shape_error(minimal_run):
    assert _shape_errors(minimal_run) == []


def test_a_document_that_is_not_text_is_reported(minimal_run):
    (minimal_run / "artifacts/ART-SSP.md").write_bytes(b"\xff\xfe\x00bad")
    found = _evaluate(minimal_run)
    assert any(f.rule == "RUN-FM-001" and f.finding.path == "artifacts/ART-SSP.md"
               and "UTF-8" in f.finding.message for f in found)


@pytest.mark.parametrize("rel", [ORG, ITEMS])
def test_build_and_check_survive_an_unparsable_data_file(minimal_run, rel):
    (minimal_run / rel).write_text("key: [unclosed\n\t- x: {\n", encoding="utf-8")
    build.build(open_run(minimal_run, REPO_ROOT))  # must not raise
    assert any(f.rule == "RUN-FM-001" and f.finding.path == rel for f in _evaluate(minimal_run))


def test_build_names_an_unreadable_file_instead_of_a_traceback(minimal_run):
    (minimal_run / "artifacts/ART-SSP.md").write_bytes(b"\xff\xfe\x00bad")
    result = runner.invoke(app, ["build", str(minimal_run)])
    assert result.exit_code == 1
    assert "cannot build" in result.output


# --- the POA&M date freeze ---------------------------------------------------------------

def _slip(run_dir):
    edit_yaml(run_dir / ITEMS,
              lambda d: d["items"][0].update(scheduled_completion="2029-01-29"))


def _asmt010(run_dir):
    build.build(open_run(run_dir, REPO_ROOT))
    return [f.finding.message for f in _evaluate(run_dir) if f.rule == "ASMT-010"]


def test_an_unreadable_freeze_record_is_kept_and_reported(minimal_run):
    _slip(minimal_run)
    assert any("should not be changed" in m for m in _asmt010(minimal_run))
    record = minimal_run / poam_dates.ORIGINAL_FILE
    record.write_text("items: {bad\n", encoding="utf-8")
    messages = _asmt010(minimal_run)
    assert record.read_text(encoding="utf-8") == "items: {bad\n"  # build did not refreeze
    assert any("cannot be read" in m for m in messages)


def test_a_freeze_record_of_the_wrong_shape_is_not_overwritten(minimal_run):
    record = minimal_run / poam_dates.ORIGINAL_FILE
    record.write_text("items: x\n", encoding="utf-8")
    assert poam_dates.freeze(open_run(minimal_run, REPO_ROOT)) is None
    assert any("cannot be read" in m for m in _asmt010(minimal_run))


# --- rmf new --force -------------------------------------------------------------------------

def test_force_keeps_the_product_files_already_filled_in(tmp_path):
    new_workspace(tmp_path, "demo", REPO_ROOT, as_of="2026-10-29T12:00:00Z")
    profile = tmp_path / "product/profile.yaml"
    filled = profile.read_text(encoding="utf-8") + "# filled in by the fork\n"
    profile.write_text(filled, encoding="utf-8")
    (tmp_path / "product/README.md").unlink()
    new_workspace(tmp_path, "demo", REPO_ROOT, force=True, as_of="2026-10-29T12:00:00Z")
    assert profile.read_text(encoding="utf-8") == filled
    assert (tmp_path / "product/README.md").is_file()  # a missing template file comes back


# --- rmf run migrate ---------------------------------------------------------------------------

def _names_back(run_dir, registry: str):
    """Undo the fixture's provider migration, leaving ``registry`` where the list was."""
    org = run_dir / ORG
    text = org.read_text(encoding="utf-8")
    org.write_text(text[: text.index("\nproviders:")] + "\n" + registry, encoding="utf-8")
    edit_yaml(run_dir / f"{DATA}/leveraged-authorizations.yaml",
              lambda d: d["leveraged_authorizations"][0].update(provider="Enterprise IT"))


@pytest.mark.parametrize("registry", ["providers: []\n", "providers:\n",
                                      "providers: []  # none yet\n", ""])
def test_an_empty_provider_registry_is_filled_not_duplicated(minimal_run, registry):
    _names_back(minimal_run, registry)
    migrate_providers(open_run(minimal_run, REPO_ROOT))
    text = (minimal_run / ORG).read_text(encoding="utf-8")
    assert text.count("\nproviders:") == 1
    org = read_yaml(minimal_run / ORG)  # still parses
    assert "Enterprise IT" in {p["name"] for p in org["providers"]}


def test_one_migrate_brings_an_old_run_all_the_way(minimal_run):
    _names_back(minimal_run, "")
    run_yaml = minimal_run / "run.yaml"
    text = run_yaml.read_text(encoding="utf-8")
    current = read_yaml(run_yaml)["framework_version"]
    run_yaml.write_text(text.replace(f"framework_version: {current}",
                                     "framework_version: 0.1.0"), encoding="utf-8")
    lines = migrate(open_run(minimal_run, REPO_ROOT))
    assert any(line.startswith("registered provider") for line in lines)
    la = read_yaml(minimal_run / f"{DATA}/leveraged-authorizations.yaml")
    assert la["leveraged_authorizations"][0]["provider"].startswith("PRV-")
    again = migrate(open_run(minimal_run, REPO_ROOT))
    assert len(again) == 1 and "already on contract" in again[0]


# --- rmf refs fetch, rmf ci ----------------------------------------------------------------------

def test_a_failed_download_keeps_the_status_of_a_file_that_is_pinned_and_present(tmp_path):
    pdf = tmp_path / "references/pdf/doc.pdf"
    pdf.parent.mkdir(parents=True)
    pdf.write_bytes(b"%PDF-1.7 pinned")
    entry = {"id": "DOC-A", "acquisition": "auto", "kind": "pdf", "urls": [],
             "local_path": "references/pdf/doc.pdf", "sha256": fetch_mod.sha256_file(pdf),
             "status": "ok"}
    result = fetch_mod.fetch_entry(None, tmp_path, entry)
    assert result.failed and entry["status"] == "ok"
    pdf.unlink()
    assert fetch_mod.fetch_entry(None, tmp_path, entry).failed
    assert entry["status"] == "manual-required"


def test_a_step_that_stood_down_is_not_a_pass():
    assert StepResult("example", (), True, output="examples/x skipped (fork profile)").skipped
    assert not StepResult("ruff", (), True).skipped
    assert not StepResult("checks-doc", (), False, output="stale").skipped
