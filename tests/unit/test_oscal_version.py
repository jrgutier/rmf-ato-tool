"""REF-005 negative cases on a tmp tree (the positive case runs on the real repo in
test_refs_oscal.py::test_oscal_versions_consistent)."""

import json

import pytest
from _refs_fixtures import SHA_A, entry, make_root

from rmf_tool.oscal import version

CAT = "references/oscal/catalog/cat.json"
SCHEMA = "references/oscal/schemas/oscal_ssp_schema.json"
CONTENT_URL = "https://raw.githubusercontent.com/usnistgov/oscal-content/v1.6.0/cat.json"
SCHEMA_URL = "https://github.com/usnistgov/OSCAL/releases/download/v1.2.1/oscal_ssp_schema.json"

VERSIONS = """\
generated_oscal_version: 1.2.1
compliance_trestle: 5.2.0
schemas: {repo: usnistgov/OSCAL, tag: v1.2.1}
content: {repo: usnistgov/oscal-content, tag: v1.6.0, fallback_tag: v1.5.0}
input_minor: '1.2'
inputs:
  references/oscal/catalog/cat.json: 1.2.3
"""


def ok(ref_id, **kw):
    return entry(ref_id, status="ok", sha256=SHA_A, size_bytes=1, downloaded="2026-10-29",
                 **kw)


def tree(tmp_path, versions=VERSIONS, cat_version="1.2.3", content_url=CONTENT_URL,
         schema_id="http://csrc.nist.gov/ns/oscal/1.2.1/oscal-ssp-schema.json"):
    rr = make_root(tmp_path, [
        ok("OSCAL-CAT", kind="oscal-catalog", urls=[content_url], local_path=CAT),
        ok("OSCAL-SCHEMA", kind="oscal-schema", urls=[SCHEMA_URL], local_path=SCHEMA),
        ok("DOC-A"),
    ])
    rr.write(CAT, json.dumps({"catalog": {"metadata": {"oscal-version": cat_version}}}))
    rr.write(SCHEMA, json.dumps({"$schema": "x", "$id": schema_id}))
    if versions is not None:
        rr.write(version.VERSIONS_PATH, versions)
    return rr


def messages(rr):
    findings = version.check(rr.root, rr.index())
    assert {f.rule for f in findings} <= {"REF-005"}
    return [f.message for f in findings]


def test_consistent_tree_passes(tmp_path):
    assert messages(tree(tmp_path)) == []


@pytest.mark.parametrize("kw,needle", [
    ({"versions": None}, "file not found"),
    ({"versions": VERSIONS.replace("generated_oscal_version: 1.2.1",
                                   "generated_oscal_version: 1.2.3")}, "generated_oscal_version"),
    ({"versions": VERSIONS.replace("tag: v1.2.1", "tag: v1.2.0")}, "schemas.tag"),
    ({"versions": VERSIONS.replace("tag: v1.6.0", "tag: v1.4.0")}, "content.tag"),
    ({"versions": VERSIONS.replace("cat.json: 1.2.3", "cat.json: 1.2.2")}, "inputs records"),
    ({"versions": VERSIONS + "  references/oscal/gone.json: 1.2.3\n"}, "gone.json"),
    ({"cat_version": "1.1.2"}, "is not 1.2.x"),
    ({"content_url": CONTENT_URL.replace("v1.6.0", "main")}, "not pinned to v1.6.0"),
    ({"schema_id": "http://csrc.nist.gov/ns/oscal/1.1.2/oscal-ssp-schema.json"},
     "is not an OSCAL 1.2.1 schema"),
])
def test_inconsistencies_detected(tmp_path, kw, needle):
    found = messages(tree(tmp_path, **kw))
    assert any(needle in m for m in found), found


def test_invalid_json_reported(tmp_path):
    rr = tree(tmp_path)
    rr.write(CAT, "{not json")
    assert any("not valid JSON" in m for m in messages(rr))


def test_trestle_mismatch_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(version, "_trestle_version", lambda: ("5.3.0", "1.2.2"))
    assert any("compliance-trestle 5.3.0" in m for m in messages(tree(tmp_path)))


def test_missing_input_file_left_to_ref002(tmp_path):
    rr = tree(tmp_path)
    (rr.root / CAT).unlink()
    assert messages(rr) == []


@pytest.mark.parametrize("v,ok", [("1.2.0", True), ("1.2.13", True), ("1.20.1", False),
                                  ("1.3.0", False), ("1.2", False)])
def test_same_minor(v, ok):
    assert version.same_minor(v) is ok


def test_document_version():
    assert version.document_version({"profile": {"metadata": {"oscal-version": "1.2.3"}}}) \
        == "1.2.3"
    assert version.document_version({"other": {}}) is None
