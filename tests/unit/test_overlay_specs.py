"""framework/baselines/overlay-specs.yaml: Section 6 of the Classified System Overlay and the
Privacy Overlays, regenerated from the text and consistent with the overlays' summary tables
as transcribed in cnssi-1253.yaml. Then OVS-001 to OVS-003 on the cases the overlays permit;
the negative fixtures (tests/fixtures/negative/OVS-*.yaml) prove each clause fails."""

import copy

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml
from ruamel.yaml import YAML
from typer.testing import CliRunner

from rmf_tool import build, catalog, overlay_specs
from rmf_tool.check import engine
from rmf_tool.cli import app
from rmf_tool.cnssi1253 import CLASSIFIED, PRIVACY
from rmf_tool.run.model import open_run, schema_errors

TAILORING = "artifacts/data/tailoring.yaml"
ACCT = f"{PRIVACY}-ACCT"
LAW = {"reviewed": ["legislation", "regulation", "policy", "omb-policy"],
       "requires_control": False, "sources": ["INT-028.A3"]}
PRV_1 = {"id": "AS-PRV-1", "holds": True, "rationale": "Training precedes access.",
         "sources": ["INT-028.A2"]}
AC2_VALUES = {f"ac-02_odp.{n:02d}": "a value" for n in range(4, 11)}


@pytest.fixture(scope="module")
def data():
    return YAML(typ="safe").load((REPO_ROOT / overlay_specs.YAML_PATH).read_text("utf-8"))


@pytest.fixture(scope="module")
def tables():
    return YAML(typ="safe").load((REPO_ROOT / "framework/baselines/cnssi-1253.yaml")
                                 .read_text("utf-8"))


def _adds(tables, overlay_id):
    overlay = next(o for o in tables["overlays"] if o["id"] == overlay_id)
    return {c for b in overlay["blocks"] for c in b["add"]}


def test_committed_yaml_is_regenerated_output():
    assert (REPO_ROOT / overlay_specs.YAML_PATH).read_text("utf-8") == \
        overlay_specs.generate(REPO_ROOT).text
    assert overlay_specs.main(["--check", "--repo", str(REPO_ROOT)]) == 0


def test_specs_match_the_summary_tables(data, tables):
    """Section 6 specifies exactly the controls each overlay's table selects, per control set."""
    assert schema_errors(REPO_ROOT, "overlay-specs", data) == []
    specs = {o["overlay"]: o["specs"] for o in data["overlays"]}
    assert {s["control"] for s in specs[CLASSIFIED]} == _adds(tables, CLASSIFIED)
    for suffix in ("ACCT", "LOW", "MODERATE", "HIGH"):
        selected = {s["control"] for s in specs[PRIVACY] for st in s.get("statements") or ()
                    if st["kind"] == "justification" and st["disposition"] == "select"
                    and suffix in st["sets"]}
        assert selected == _adds(tables, f"{PRIVACY}-{suffix}"), suffix
    known = catalog.load(REPO_ROOT).controls
    assert all(s["control"] in known for o in data["overlays"] for s in o["specs"])
    assert all(s.get("authorities") for o in data["overlays"] for s in o["specs"]
               if s.get("references"))


def test_spot_checks_against_the_pdf(data):
    by = {(o["overlay"], s["control"]): s for o in data["overlays"] for s in o["specs"]}
    ac11 = by[(CLASSIFIED, "ac-11")]
    assert [st["kind"] for st in ac11["statements"]] == ["justification", "parameter"]
    assert "not to exceed 15 minutes of inactivity" in ac11["statements"][1]["text"]
    assert ac11["authorities"] == ["EO 13526", "EO 13587"]
    assert ac11["citation"] == {"ref": CLASSIFIED, "page": 12, "anchor": "AC-11, Device Lock"}
    ac28 = by[(PRIVACY, "ac-2.8")]["statements"][0]
    assert ac28["disposition"] == "not-select"
    assert ac28["sets"] == ["ACCT", "LOW", "MODERATE", "HIGH"]
    ac2 = [st for st in by[(PRIVACY, "ac-2")]["statements"] if st["kind"] == "parameter"]
    assert [st["sets"] for st in ac2] == [["ACCT", "LOW", "MODERATE"], ["HIGH"]]
    assert "at least quarterly for privileged accounts" in ac2[1]["text"]
    # page 39: the extraction moved AC-16's guidance box under AC-16(3); the repair puts it back
    ac16 = [st["kind"] for st in by[(PRIVACY, "ac-16")]["statements"]]
    assert ac16 == ["justification", "guidance", "parameter"]
    assert [st["kind"] for st in by[(PRIVACY, "ac-16.3")]["statements"]] == \
        ["justification", "parameter"]
    assert by[(PRIVACY, "au-3.3")].get("in_privacy_baseline") is True
    enhancing = by[(PRIVACY, "ac-2.6")]["statements"][0]
    assert (enhancing["disposition"], enhancing["sets"]) == ("recommend", ["ENHANCING"])


def test_applied_reads_only_the_runs_control_set():
    acct = overlay_specs.applied(REPO_ROOT, [ACCT])
    ac2 = acct["ac-2"][0]
    params = [st for st in ac2.statements if st["kind"] == "parameter"]
    assert len(params) == 1 and params[0]["sets"] == ["ACCT", "LOW", "MODERATE"]
    assert "ac-2.1" not in acct  # Moderate and High only
    assert acct["ac-2.8"][0].disposition == "not-select"
    assert acct["ac-2.6"][0].disposition == "recommend"
    high = overlay_specs.applied(REPO_ROOT, [f"{PRIVACY}-HIGH"])
    assert [st["sets"] for st in high["ac-2"][0].statements
            if st["kind"] == "parameter"] == [["HIGH"]]
    assert overlay_specs.applied(REPO_ROOT, [PRIVACY, "not-an-overlay", 7]) != {}
    assert overlay_specs.applied(REPO_ROOT, []) == {}


def test_assigned_params_follow_the_items_the_value_names():
    cat = catalog.load(REPO_ROOT)
    assert overlay_specs.assigned_params(cat, "ac-11", "a. Prevent further access ...") == \
        ["ac-11_odp.01", "ac-11_odp.02"]
    assert overlay_specs.assigned_params(cat, "ac-2.9", "Only permit the use ...") == \
        ["ac-02.09_odp"]
    # an aggregate parameter stands for the ODPs it aggregates
    assert "mp-4_prm_1" not in overlay_specs.assigned_params(cat, "mp-4", "a. Physically ...")
    assert overlay_specs.named("EO 13526", ["EO 13526, Sec 4.1, para. (a)"])
    assert not overlay_specs.named("EO 13587", ["EO 13526"])


# --- the rules on permitted cases -------------------------------------------------------


def _privacy_run(tmp_path, ac2_values=AC2_VALUES):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["categorization"].__setitem__("overlays", [ACCT]))
    edit_yaml(run_dir / TAILORING, lambda d: d["assumptions"].append(dict(PRV_1)))
    if ac2_values is not None:
        edit_yaml(run_dir / "artifacts/ssp/controls/ac.yaml",
                  lambda d: d["controls"][0].__setitem__("parameters", dict(ac2_values)))
    return run_dir


def _ovs(run_dir):
    build.build(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    return [f.message for f in engine.select(run, engine.evaluate(run), final=True)
            if f.rule.startswith("OVS-")]


def _add_action(run_dir, action):
    edit_yaml(run_dir / TAILORING, lambda d: d["actions"].append(copy.deepcopy(action)))


def test_privacy_run_with_values_and_named_authorities_is_clean(tmp_path):
    run_dir = _privacy_run(tmp_path)
    _add_action(run_dir, {
        "control_id": "ac-3", "action": "remove", "basis": "scoping",
        "scoping": {"consideration": "technology"},
        "law_policy": {**LAW, "authorities": ["5 U.S.C. 552a(b)", "EO 14028 Sec 3(a)"]},
        "rationale": "No records to protect.", "sources": ["INT-028.A3"]})
    # a recommended (Privacy Enhancing) control is optional, so its removal names nothing
    _add_action(run_dir, {
        "control_id": "ac-2.6", "action": "remove", "basis": "no-risk", "law_policy": LAW,
        "rationale": "Optional.", "sources": ["INT-028.A3"]})
    assert _ovs(run_dir) == []


def test_values_may_come_from_tailoring_or_be_set_by_a_provider(tmp_path):
    run_dir = _privacy_run(tmp_path, ac2_values=None)
    for n in range(4, 10):  # odp.10 is the fixture's own parameter action
        _add_action(run_dir, {"control_id": "ac-2", "action": "parameter",
                              "parameter": {"param_id": f"ac-02_odp.{n:02d}", "value": "v"},
                              "rationale": "Overlay value.", "sources": ["INT-028.A3"]})
    assert _ovs(run_dir) == []
    run_dir = _privacy_run(tmp_path / "inherited", ac2_values=None)
    edit_yaml(run_dir / "artifacts/ssp/controls/ac.yaml", lambda d: d["controls"][0].update(
        status="inherited", inherited_from="Enterprise identity provider"))
    assert not [m for m in _ovs(run_dir) if m.startswith("ac-2 records")]


def test_coordinated_not_select_control_and_malformed_input_report_no_crash(tmp_path):
    run_dir = _privacy_run(tmp_path)
    edit_yaml(run_dir / "run.yaml", lambda d: d["control_subset"].append("ac-2.8"))
    _add_action(run_dir, {
        "control_id": "ac-2.8", "action": "add", "rationale": "Coalition accounts.",
        "privacy_coordination": {"by": "PER-PRIV", "finding": "Limited to need.",
                                 "sources": ["INT-028.A3"]},
        "sources": ["INT-028.A3"]})
    from rmf_tool import baseline

    run = open_run(run_dir, REPO_ROOT)
    (run_dir / "baseline.json").write_text(baseline.render(baseline.resolve(run)), "utf-8")
    assert not [m for m in _ovs(run_dir) if "ac-2.8" in m]
    edit_yaml(run_dir / "artifacts/ssp/controls/ac.yaml",
              lambda d: d["controls"][0].__setitem__("parameters", "not a mapping"))
    _add_action(run_dir, {"control_id": "ac-2", "action": "parameter",
                          "parameter": {"param_id": ["x"], "value": "v"}})
    assert any(m.startswith("ac-2 records no value") for m in _ovs(run_dir))


def test_catalog_show_prints_the_overlay_specification(tmp_path, monkeypatch):
    monkeypatch.chdir(REPO_ROOT)
    run_dir = _privacy_run(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["catalog", "show", "--run", str(run_dir), "--control", "ac-2",
                                 "--fields", "title,overlay"])
    assert result.exit_code == 0, result.stdout
    assert f"overlay {PRIVACY} (select):" in result.stdout
    assert "authorities: 5 U.S.C. 552a; FISA; EO 12333" in result.stdout
    assert runner.invoke(app, ["catalog", "show", "--family", "ac", "--fields",
                               "overlay"]).exit_code == 2
