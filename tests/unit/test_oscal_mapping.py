"""Each row of oscal/mapping.yaml (plan §6.6) is written by the builders."""

import json
from pathlib import Path

import pytest
from conftest import VALID_MINIMAL
from ruamel.yaml import YAML

import rmf_tool.oscal

ROWS = YAML(typ="safe").load(
    (Path(rmf_tool.oscal.__file__).parent / "mapping.yaml").read_text())["rows"]
DOCS = {
    "ssp": json.loads((VALID_MINIMAL / "oscal/ssp.json").read_text())["system-security-plan"],
    "profile": json.loads((VALID_MINIMAL / "oscal/profile.json").read_text())["profile"],
}


def lookup(doc, path):
    node = doc
    for part in path.split("."):
        key, is_list = (part[:-2], True) if part.endswith("[]") else (part, False)
        node = node[key]
        if is_list:
            assert isinstance(node, list) and node, f"{key} is an empty list"
            node = node[0]
    return node


@pytest.mark.parametrize("row", ROWS, ids=[f"{r['model']}-{r['path']}" for r in ROWS])
def test_mapping_row_round_trip(row):
    models = ["ssp", "profile"] if row["model"] == "all" else [row["model"]]
    for model in models:
        assert lookup(DOCS[model], row["path"]) not in (None, "", [], {})
