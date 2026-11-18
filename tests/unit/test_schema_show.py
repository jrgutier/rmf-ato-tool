"""`rmf schema show` / `template`: every run-data schema yields an outline and a skeleton
that parses as YAML and holds each required top-level field."""

import pytest
from conftest import REPO_ROOT
from ruamel.yaml import YAML
from typer.testing import CliRunner

from rmf_tool import schema_show
from rmf_tool.cli import app

NAMES = schema_show.names(REPO_ROOT)


@pytest.mark.parametrize("name", NAMES)
def test_every_schema_has_an_outline_and_a_skeleton(name):
    schema = schema_show.load(REPO_ROOT, name)
    assert schema_show.outline(schema)[-1] == "(* required)"
    data = YAML(typ="safe").load(schema_show.skeleton(schema))
    if schema.get("type") == "object" and schema.get("required"):
        assert set(schema["required"]) <= set(data or {}), name


def test_show_accepts_a_data_path_and_marks_required():
    result = CliRunner().invoke(app, ["schema", "show", "artifacts/data/allocation.yaml"])
    assert result.exit_code == 0, result.output
    assert "* allocations[]: object" in result.stdout
    assert "    requirements[]: string" in result.stdout


def test_unknown_schema_is_a_usage_error():
    result = CliRunner().invoke(app, ["schema", "template", "no-such-record"])
    assert result.exit_code == 2
