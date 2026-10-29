"""`rmf catalog show`: compact control text, family filter, missing-only, chunking."""

import json

import pytest
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import catalog
from rmf_tool.cli import app

runner = CliRunner()


def test_compact_view_inserts_parameters():
    cat = catalog.load(REPO_ROOT)
    v = catalog.view(cat, "ac-2", ("title", "statement", "params"))
    assert v["title"] == "Account Management"
    assert v["statement"].startswith("a. Define and document the types of accounts")
    assert "[Assignment: organization-defined prerequisites and criteria]" in v["statement"]
    assert "\n  1. Authorized users of the system;" in v["statement"]
    assert "ac-02_odp.01" in v["params"]
    assert catalog.sort_key("ac-2.10") > catalog.sort_key("ac-2.9")


def test_chunking():
    items = list("abcdefg")
    parts = [catalog.chunk(items, f"{i}/3") for i in (1, 2, 3)]
    assert parts == [list("abc"), list("de"), list("fg")]
    with pytest.raises(ValueError):
        catalog.chunk(items, "4/3")


def test_cli_family_filter_json(monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    result = runner.invoke(app, ["catalog", "show", "--family", "AU", "--chunk", "1/4",
                                 "--fields", "title", "--format", "json"])
    assert result.exit_code == 0
    ids = [c["id"] for c in json.loads(result.stdout)["controls"]]
    assert ids[0] == "au-1" and all(i.startswith("au-") for i in ids)


def test_cli_missing_only(minimal_run, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    (minimal_run / "artifacts/ssp/controls/sc.yaml").unlink()
    result = runner.invoke(app, ["catalog", "show", "--run", str(minimal_run), "--missing",
                                 "--fields", "title,statement,guidance,objectives"])
    assert result.exit_code == 0
    assert result.stdout.startswith("sc-7 Boundary Protection")
    assert "objectives:" in result.stdout and "1 control(s)" in result.stdout


@pytest.mark.parametrize("args", [
    ["catalog", "show"], ["catalog", "show", "--missing", "--family", "ac"],
    ["catalog", "show", "--family", "ac", "--fields", "nope"],
    ["catalog", "show", "--control", "zz-99"], ["catalog", "show", "--family", "ac",
                                                "--chunk", "0/2"],
])
def test_cli_usage_errors(args, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    assert runner.invoke(app, args).exit_code == 2
