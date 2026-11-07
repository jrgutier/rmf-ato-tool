"""AC-14/AC-17: an artifact template for every non-generated artifact, following the
template conventions (5-key front-matter naming the producer, the rmf:facts block,
``<<FILL: ...>>`` placeholders with no angle brackets inside, one in every ## section)."""

import json
import re

import jsonschema
import pytest
from _framework_fixtures import REAL
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool.framework.load import load

ARTIFACTS = [a.data for a in load(REAL, REPO_ROOT).framework.of("artifacts")]
TEMPLATED = [a for a in ARTIFACTS if a["template"]]
FILL = re.compile(r"<<FILL: ([^\n]*?)>>")
FACTS = "<!-- BEGIN rmf:facts -->\n<!-- END rmf:facts -->"


def split(text):
    _, head, body = text.split("---\n", 2)
    return YAML(typ="safe").load(head), body


def test_every_hand_written_artifact_has_a_template():
    assert {a["id"] for a in ARTIFACTS if not a["generated"]} == {a["id"] for a in TEMPLATED}
    for a in TEMPLATED:
        assert a["template"] == f"templates/artifacts/{a['id']}.md"
        assert (REPO_ROOT / a["template"]).is_file(), a["template"]


@pytest.mark.parametrize("art", TEMPLATED, ids=lambda a: a["id"])
def test_template_follows_the_conventions(art):
    text = (REPO_ROOT / art["template"]).read_text(encoding="utf-8")
    front, body = split(text)
    assert list(front) == ["artifact_id", "run_id", "produced_by_task", "touched_by", "sources"]
    assert front["artifact_id"] == art["id"]
    assert front["produced_by_task"] == art["producer"]
    assert front["touched_by"] == [art["producer"]]
    assert body.startswith("# ")
    assert body.count(FACTS) == 1

    placeholders = FILL.findall(text)
    assert placeholders, "no <<FILL: ...>> placeholder"
    for inner in placeholders:
        assert not re.search(r"[<>]", inner), inner
    assert text.count("<<") == text.count(">>") == len(placeholders)

    sections = re.split(r"^## .*$", re.sub(r"<!--.*?-->", "", body, flags=re.S), flags=re.M)
    assert len(sections) >= 2
    for part in sections[1:]:
        assert FILL.search(part), "a ## section without a placeholder"


DATA_TEMPLATES = sorted((REPO_ROOT / "templates/data").glob("*.yaml"))


@pytest.mark.parametrize("path", DATA_TEMPLATES, ids=lambda p: p.stem)
def test_data_template_loads_and_meets_its_schema(path):
    """A data template an agent copies is valid YAML, and valid against its schema where one
    exists: a FILL sits only where the schema takes free text."""
    data = YAML(typ="safe").load(path.read_text(encoding="utf-8"))
    schema = REPO_ROOT / "framework/schema" / f"{path.stem}.schema.json"
    if schema.is_file():
        validator = jsonschema.Draft202012Validator(json.loads(schema.read_text()))
        assert [e.message for e in validator.iter_errors(data)] == []
