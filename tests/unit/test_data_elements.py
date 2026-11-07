"""The CNSSI 1254 Annex C map in framework/artifacts.yaml (`data_elements`): every row of the
register has a home or an open work item in every core document it names, and every home resolves
in the templates and schemas a run is written from."""

import json
import re
import shutil

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml
from ruamel.yaml import YAML

from rmf_tool.check import engine
from rmf_tool.check.rules.coverage import CORE_DOCUMENTS
from rmf_tool.oscal import build_ssp
from rmf_tool.run.model import open_run

YAMLS = YAML(typ="safe")
FILE_SCHEMAS = {"artifacts/data/rar.yaml": "rar", "artifacts/data/ra.yaml": "ra",
                "artifacts/poam/items.yaml": "poam-items",
                "artifacts/data/ssp-records.yaml": "ssp-records",
                "artifacts/data/authorizations.yaml": "authorizations",
                "artifacts/data/boundary.yaml": "boundary", "artifacts/data/sap.yaml": "sap",
                "artifacts/data/infotypes.yaml": "infotypes",
                "artifacts/sar/results/*.yaml": "sar-results",
                "artifacts/data/sar-report.yaml": "sar-report",
                "artifacts/data/system-description.yaml": "system-description",
                "artifacts/data/users.yaml": "users", "artifacts/data/inventory.yaml": "inventory",
                "artifacts/data/sar-summary.yaml": "sar-summary",
                "artifacts/data/bia.yaml": "bia"}


def _load(name):
    return YAMLS.load((REPO_ROOT / name).read_text(encoding="utf-8"))


def _map():
    artifacts = _load("framework/artifacts.yaml")["artifacts"]
    return {a["id"]: a.get("data_elements") or [] for a in artifacts if a["id"] in CORE_DOCUMENTS}


def _rows():
    rows = {}
    for entry in _load("conformance/requirements/CNSSI1254.yaml")["requirements"]:
        if entry["kind"] == "table" and entry["status"] != "not-a-requirement":
            cells = [c.strip() for c in entry["statement"].split("|")]
            if len(cells) > 2:
                rows[entry["id"]] = cells[1]
    return rows


def test_every_annex_c_row_is_mapped_in_each_document_it_names():
    mapped = {(aid, e["req"]) for aid, elements in _map().items() for e in elements}
    for req, documents in _rows().items():
        for aid, name in CORE_DOCUMENTS.items():
            short = {"ART-AODM": "Authorization Decision Document"}.get(aid, name)
            if re.search(rf"(?<![A-Z]){re.escape(short)}(?![A-Z])", documents):
                assert (aid, req) in mapped, (aid, req)


def test_a_pending_element_names_an_open_work_item():
    status = {i["id"]: i["status"] for i in _load("conformance/work-items.yaml")["work_items"]}
    for elements in _map().values():
        for element in elements:
            if "pending" in element:
                assert status[element["pending"]] == "open", element


def _resolves(schema, node, path):
    while "$ref" in node:
        node = schema["$defs"][node["$ref"].rpartition("/")[2]]
    if not path:
        return True
    if path[0] == "*":
        return _resolves(schema, node["items"], path[1:])
    return path[0] in node["properties"] and _resolves(schema, node["properties"][path[0]],
                                                      path[1:])


@pytest.mark.parametrize("aid", CORE_DOCUMENTS)
def test_a_home_resolves(aid):
    for element in _map()[aid]:
        if "path" in element:
            name = FILE_SCHEMAS[element["file"]]
            schema = json.loads((REPO_ROOT / f"framework/schema/{name}.schema.json").read_text())
            assert _resolves(schema, schema, element["path"].split(".")), element
        elif "heading" in element:
            text = (REPO_ROOT / f"templates/artifacts/{element['artifact']}.md").read_text()
            assert f"## {element['heading']}\n" in text, element
        elif "fact" in element:
            facts = json.loads((REPO_ROOT / "framework/schema/facts.schema.json").read_text())
            assert element["fact"] in facts["properties"], element


def test_a_boundary_diagram_resolves_in_a_fork_shaped_run(tmp_path):
    """In a fork `product/` sits beside `runs/`: the spelling a trace token uses must reach it."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "fork/runs/first")
    shutil.move(run_dir / "product", tmp_path / "fork/product")
    edit_yaml(run_dir / "run.yaml", lambda d: d.__setitem__("product", "../../product"))
    run = open_run(run_dir, REPO_ROOT)
    found = engine.evaluate(run).findings
    assert not [f for f in found if f.rule == "PKG-003"]
    links = json.loads(build_ssp.build_ssp(run))["system-security-plan"][
        "system-characteristics"]["authorization-boundary"]["diagrams"][0]["links"]
    assert links[0]["href"] == "../../product/architecture.md"
    (tmp_path / "fork/product/architecture.md").unlink()
    assert [f for f in engine.evaluate(open_run(run_dir, REPO_ROOT)).findings
            if f.rule == "PKG-003"]

