"""Each row of oscal/mapping.yaml (plan §6.6) is written by the builders."""

import json
from pathlib import Path

import pytest
from conftest import VALID_MINIMAL
from ruamel.yaml import YAML

import rmf_tool.oscal
from rmf_tool.oscal import schema_validate

ROWS = YAML(typ="safe").load(
    (Path(rmf_tool.oscal.__file__).parent / "mapping.yaml").read_text())["rows"]
DOCS = {}
for path in sorted((VALID_MINIMAL / "oscal").glob("*.json")):
    doc = json.loads(path.read_text())
    DOCS[schema_validate.model_of(doc)] = next(iter(doc.values()))
MODELS = ["profile", "ssp", "assessment-plan", "assessment-results", "poam"]


def lookup(doc, path):
    node = doc
    for part in path.split("."):
        key, is_list = (part[:-2], True) if part.endswith("[]") else (part, False)
        node = node[key]
        if is_list:
            assert isinstance(node, list) and node, f"{key} is an empty list"
            node = node[0]
    return node


def models(row):
    if row["model"] == "all":
        return MODELS
    return row["model"] if isinstance(row["model"], list) else [row["model"]]


def test_rows_cover_every_model():
    assert sorted(DOCS) == sorted(MODELS)
    assert {m for row in ROWS for m in models(row)} == set(MODELS)


@pytest.mark.parametrize("row", ROWS, ids=[f"{r['model']}-{r['path']}" for r in ROWS])
def test_mapping_row_round_trip(row):
    for model in models(row):
        value = lookup(DOCS[model], row["path"])
        assert value not in (None, "", [], {})
        if "expect" in row:
            assert value == row["expect"], (model, row["path"])
