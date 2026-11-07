"""framework/baselines/cnssi-1253.yaml: regenerated from CNSSI 1253 Appendix D (PDF geometry
checked against the text extraction), schema-valid, every table block cited and resolving,
and consistent with the SP 800-53r5 catalog and the 800-53B profiles."""

import shutil

import pytest
from _framework_fixtures import P3A, REAL
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool import baseline, catalog, cnssi1253, overlay_specs
from rmf_tool.framework.validate import baseline_tables, validate
from rmf_tool.run.model import schema_errors


@pytest.fixture(scope="module")
def result():
    pytest.importorskip("pymupdf")  # PDF geometry needs the optional [extract] extra (L-0038)
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


PRIVACY_SET_IDS = [f"{cnssi1253.PRIVACY}-{s}" for s, _ in cnssi1253.PRIVACY_SETS]


def test_classified_overlay_transcribed(tables):
    overlays = {o["id"]: o for o in tables["overlays"]}
    assert set(overlays) == set(cnssi1253.OVERLAYS) | set(PRIVACY_SET_IDS)
    classified = overlays["CNSSI1253E-ATT5-CLASSIFIED"]
    added = [cid for b in classified["blocks"] for cid in b["add"]]
    assert len(added) == len(set(added)) == 108
    assert added[0] == "ac-1" and added[-1] == "sr-12"
    assert not overlays["CNSSI1253F-ATT6-PRIVACY"]["transcribed"]


def test_privacy_overlay_control_sets(tables):
    """Table 2, one overlay per control set (ADR-0003). Low, Moderate and High nest, and the
    ACCT set (audit and account records) is inside Low."""
    overlays = {o["id"]: o for o in tables["overlays"]}
    sets = {i.rsplit("-", 1)[1]: [c for b in overlays[i]["blocks"] for c in b["add"]]
            for i in PRIVACY_SET_IDS}
    assert {s: len(ids) for s, ids in sets.items()} == {
        "ACCT": 92, "LOW": 121, "MODERATE": 169, "HIGH": 174}
    assert all(len(ids) == len(set(ids)) for ids in sets.values())
    assert set(sets["ACCT"]) <= set(sets["LOW"]) <= set(sets["MODERATE"]) <= set(sets["HIGH"])
    # joined split IDs (AC- / 3(14), PM- / 20(1)), errata rows and family-prefixed -1 rows
    assert {"ac-3.14", "ac-6.2", "ia-2.6", "ma-1", "pt-8", "si-18.5"} <= set(sets["HIGH"])
    assert {"ac-2.9", "ia-2.5", "pt-8"} <= set(sets["ACCT"])
    assert "ia-2.6" not in sets["LOW"] and "ac-2.1" not in sets["LOW"]
    # "GR" with no "+" (CP-6, CP-7 and enhancements at Mod/High) is guidance, not a selection
    assert not {"cp-6", "cp-6.1", "cp-6.3", "cp-7", "cp-7.1"} & set(sets["HIGH"])


def test_privacy_erratum_must_match(monkeypatch):
    monkeypatch.setitem(cnssi1253._PRIVACY_ERRATA, "ac-1", "no such erratum")
    known = catalog.load(REPO_ROOT).controls
    with pytest.raises(cnssi1253.ExtractError, match="erratum for ac-1 matched no row"):
        cnssi1253.privacy_overlay(REPO_ROOT / f"references/text/{cnssi1253.PRIVACY}.md", known)


def test_every_block_cites_a_page_that_resolves(tables):
    findings, cited = baseline_tables(REAL, REPO_ROOT)
    assert findings == []
    overlay_pages = sum(len(o.get("blocks") or []) for o in tables["overlays"])
    # Classified System Overlay, Privacy Overlay control sets, Space Platform Overlay
    assert overlay_pages == 5 + 55 + 9
    inputs = baseline.load_inputs(REPO_ROOT)  # tailoring-inputs.yaml: one block per entry
    blocks = len(inputs["assumptions"]) + len(inputs["overlay_conditions"]) \
        + len(inputs["policy_controls"])
    specs = sum(len(controls) for controls in overlay_specs.load(REPO_ROOT).values())
    assert specs == 108 + 315  # overlay-specs.yaml: one block per Section 6 control
    # file, tables, overlays, overlay specifications, inputs
    unlisted = 1  # the Space Platform Overlay's controls in neither of its tables
    from rmf_tool import cnssi1253_params
    params = 1 + len(cnssi1253_params.load(REPO_ROOT))  # the column's definition, one per row
    assert len(cited) == 1 + 136 + overlay_pages + unlisted + specs + blocks + params
    assert all("page" in e.data["citations"][0] for e in cited if e.data["id"] != "CNSSI-1253")
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


def _space_tables() -> tuple[dict[str, str], set[str]]:
    """Table 2 (control -> mark) and Table 3 of the Space Platform Overlay, read here without
    the generator: a row's first cell holding an ID, pipes inside names escaped."""
    import re

    text = (REPO_ROOT / f"references/text/{cnssi1253.SPACE}.md").read_text(encoding="utf-8")
    table2 = text.split("Table 2 - Summary of Control Specifications")[1].split("# 6.")[0]
    table3 = text.split("Table 3 - Space Platform Overlay Applicable Baseline Controls")[1]
    ident = re.compile(r"^([A-Z]{2})-(\d+)(?:\((\d+)\))?$")

    def rows(block: str):
        for line in block.splitlines():
            cells = [c.strip() for c in re.split(r"(?<!\\)\|", line)[1:-1]]
            if cells and (m := ident.match(re.sub(r"\s", "", cells[0] or cells[1]))):
                yield f"{m[1].lower()}-{int(m[2])}" + (f".{int(m[3])}" if m[3] else ""), cells

    return ({cid: cells[2] for cid, cells in rows(table2)}, {cid for cid, _ in rows(table3)})


def test_space_overlay_resolves_against_table_2_and_appendix_a(tables):
    """WI-21 closes on this diff: Table 2's 83 additions and 262 removals are what the YAML
    applies, and the H/H/H selection less the removals is Table 3's 306 kept controls plus the
    five CNSSI 1253 marks '+' that neither table lists."""
    marks, kept = _space_tables()
    space = next(o for o in tables["overlays"] if o["id"] == cnssi1253.SPACE)
    added = {c for b in space["blocks"] for c in b.get("add", [])}
    removed = {c for b in space["blocks"] for c in b.get("remove", [])}
    assert added == {c for c, m in marks.items() if m == "+G"} and len(added) == 83
    assert removed == {c for c, m in marks.items() if m == "--"} and len(removed) == 262
    assert space["tailors"] == {"c": "high", "i": "high", "a": "high"}
    high = {r["id"] for t in tables["tables"] for b in t["blocks"] for r in b["controls"]
            if not r.get("withdrawn") and any(r[o][2] in "X+" for o in "cia")}
    assert len(high) == 573 and removed <= high and not added & high
    assert len(kept) == 306
    assert high - removed - kept == set(space["unlisted"]["controls"]) == {
        "sa-8.1", "sa-8.3", "sa-8.4", "sa-9.3", "sc-7.13"}
