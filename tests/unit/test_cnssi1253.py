"""framework/baselines/cnssi-1253.yaml: regenerated from CNSSI 1253 Appendix D (PDF geometry
checked against the text extraction), schema-valid, every table block cited and resolving,
and consistent with the SP 800-53r5 catalog and the 800-53B profiles."""

import shutil

import pytest
from _framework_fixtures import P3A, REAL
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool import catalog, cnssi1253
from rmf_tool.framework.validate import baseline_tables, validate
from rmf_tool.run.model import schema_errors


@pytest.fixture(scope="module")
def result():
    return cnssi1253.generate(REPO_ROOT)


@pytest.fixture(scope="module")
def tables():
    return YAML(typ="safe").load((REPO_ROOT / cnssi1253.YAML_PATH).read_text(encoding="utf-8"))


def test_committed_yaml_is_regenerated_output(result):
    assert (REPO_ROOT / cnssi1253.YAML_PATH).read_text(encoding="utf-8") == result.text
    assert cnssi1253.main(["--check", "--repo", str(REPO_ROOT)]) == 0


def test_tables_cover_appendix_d(tables):
    assert schema_errors(REPO_ROOT, "baselines", tables) == []
    assert [t["table"] for t in tables["tables"]] == [f"D-{n}" for n in range(1, 21)]
    rows = [r for t in tables["tables"] for b in t["blocks"] for r in b["controls"]]
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)) == 1189
    assert sum(bool(r.get("withdrawn")) for r in rows) == 182
    # the catalog (SP 800-53 5.2.0) adds seven controls after the 2022 tables
    assert sorted(set(catalog.load(REPO_ROOT).controls) - set(ids), key=catalog.sort_key) == [
        "ia-13", "ia-13.1", "ia-13.2", "ia-13.3", "sa-15.13", "sa-24", "si-2.7"]
    by_id = {r["id"]: r for r in rows}
    # spot checks against the PDF (pages 25, 26, 28, 136)
    assert by_id["ac-1"] == {"id": "ac-1", "privacy": "X", "c": "XXX", "i": "XXX", "a": "XXX"}
    assert by_id["ac-2.7"] == {"id": "ac-2.7", "privacy": ".", "c": "+++", "i": "+++",
                               "a": "..."}
    assert by_id["ac-4"] == {"id": "ac-4", "privacy": ".", "c": ".XX", "i": ".XX", "a": "..."}
    assert by_id["sc-18.2"]["i"] == "+++" and by_id["sc-18.2"]["c"] == "..."
    assert by_id["ac-2.10"] == {"id": "ac-2.10", "withdrawn": True}


def test_selection_is_monotonic_per_objective(tables):
    """Selected at low implies moderate implies high, for every objective (a placement check
    the text cross-check cannot make)."""
    for t in tables["tables"]:
        for b in t["blocks"]:
            for r in b["controls"]:
                for obj in ("c", "i", "a"):
                    picked = [ch in "X+" for ch in r.get(obj, "...")]
                    assert picked == sorted(picked), (r["id"], obj, r[obj])


def test_800_53b_profiles_agree_with_the_x_marks(result):
    """Every 800-53B control is marked X or -- at its level, except three the 2022 tables
    mark + (added to the profiles by later 800-53B releases); they are still selected."""
    assert result.nist == {
        "low": {"profile_only": [], "table_only": []},
        "moderate": {"profile_only": ["sa-15", "sc-7.8"], "table_only": []},
        "high": {"profile_only": ["si-4.22"], "table_only": []},
    }
    rows = {r.id: r for r in result.rows}
    for cid, level in (("sa-15", "M"), ("sc-7.8", "M"), ("si-4.22", "H")):
        assert any(rows[cid].cells[f"{o}{level}"] == "+" for o in cnssi1253.OBJECTIVES)


def test_classified_overlay_transcribed(tables):
    overlays = {o["id"]: o for o in tables["overlays"]}
    assert set(overlays) == set(cnssi1253.OVERLAYS)
    classified = overlays["CNSSI1253E-ATT5-CLASSIFIED"]
    added = [cid for b in classified["blocks"] for cid in b["add"]]
    assert len(added) == len(set(added)) == 108
    assert added[0] == "ac-1" and added[-1] == "sr-12"
    assert not overlays["CNSSI1253F-ATT6-PRIVACY"]["transcribed"]


def test_every_block_cites_a_page_that_resolves():
    findings, cited = baseline_tables(REAL, REPO_ROOT)
    assert findings == []
    assert len(cited) == 1 + 136 + 5  # file, Appendix D table pages, overlay pages
    assert all("page" in e.data["citations"][0] for e in cited[1:])
    result = validate(REAL, REPO_ROOT, P3A)
    assert not [f for f in result.findings if "baselines" in (f.path or "")]


def test_broken_anchor_is_fw_cite_002(tmp_path):
    fw = tmp_path / "framework"
    shutil.copytree(REAL, fw)
    path = fw / cnssi1253.YAML_PATH.removeprefix("framework/")
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('page: 26, anchor: "AC-2(6)"', 'page: 26, anchor: "AC-9(9)"'),
                    encoding="utf-8")
    result = validate(fw, REPO_ROOT, P3A)
    assert [f.rule for f in result.findings] == ["FW-CITE-002"]
    assert "page 26" in result.findings[0].message


def test_schema_error_is_fw_schema_001(tmp_path):
    fw = tmp_path / "framework"
    shutil.copytree(REAL, fw)
    path = fw / cnssi1253.YAML_PATH.removeprefix("framework/")
    path.write_text(path.read_text(encoding="utf-8").replace('c: "XXX"', 'c: "XX"', 1),
                    encoding="utf-8")
    result = validate(fw, REPO_ROOT, P3A)
    assert {f.rule for f in result.findings} == {"FW-SCHEMA-001"}


def _row(**cells):
    row = cnssi1253.Row(25, "AC-2")
    for key, value in cells.items():
        row.cells[key] = value
    return row


def test_text_disagreement_is_reported():
    row = _row(cM="X", cH="X")
    text = cnssi1253.TextTables({(25, "AC-2"): ["X", "X", "X"]}, {})
    problems = cnssi1253.cross_check_text([row], text, set())
    assert problems and "PDF geometry gives ['X', 'X']" in problems[0]
    assert cnssi1253.cross_check_text([row], text, {(25, "AC-2")}) == []


def test_overrides_apply_and_must_change_something():
    row = _row(cM="X")
    covered = cnssi1253.apply_overrides(
        [row], [{"page": 25, "table_id": "AC-2", "reason": "checked by eye", "c": ".XX"}])
    assert covered == {(25, "AC-2")} and row.objective("c") == ".XX"
    for bad, message in (
        ({"page": 25, "table_id": "AC-2", "reason": "x", "c": ".XX"}, "changes nothing"),
        ({"page": 99, "table_id": "AC-2", "reason": "x", "c": "XXX"}, "no such row"),
        ({"page": 25, "table_id": "AC-2", "c": "XXX"}, "reason are required"),
        ({"page": 25, "table_id": "AC-2", "reason": "x", "c": "XY"}, "three of"),
    ):
        with pytest.raises(cnssi1253.ExtractError, match=message):
            cnssi1253.apply_overrides([row], [bad])
    accepted = cnssi1253.apply_overrides(
        [row], [{"page": 25, "table_id": "AC-2", "reason": "text drops a cell",
                 "text_differs": True}])
    assert accepted == {(25, "AC-2")}
