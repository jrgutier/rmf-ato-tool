"""Phase 6 run rules beyond their one-mutation negative fixtures: the cases a run-copy
mutation cannot express (repository state, alternative branches, selection behaviour)."""

from pathlib import Path

import pytest
from conftest import REPO_ROOT, edit_yaml

from rmf_tool import build, refs
from rmf_tool.check import engine
from rmf_tool.check.context import Context
from rmf_tool.check.rules import authorization, config, consistency, coverage, hybrid, journal
from rmf_tool.run.model import open_run

LEDGER = "artifacts/data/authorizations.yaml"


def messages(run_dir: Path, rule) -> list[str]:
    return [f.finding.message for f in rule(Context(open_run(run_dir, REPO_ROOT)))]


def test_degraded_reference_warns_and_needs_disclosure(minimal_run, monkeypatch):
    """DEGRADED-001 (plan §7.6): a degraded reference cited by an active task warns, is never
    filtered out of a selection, and AODM-001 then requires a degraded disclosure."""
    real = refs.load_index

    def degraded_index(root):
        index = real(root)
        for r in index["references"]:
            if r["id"] == "SP800-37R2":
                r["status"] = "degraded"
        return index

    monkeypatch.setattr(refs, "load_index", degraded_index)
    run = open_run(minimal_run, REPO_ROOT)
    ev = engine.evaluate(run)
    degraded = [f for f in engine.select(run, ev, final=True) if f.rule == "DEGRADED-001"]
    assert degraded and degraded[0].severity == "W" and "SP800-37R2" in degraded[0].message
    assert any(f.rule == "DEGRADED-001"
               for f in engine.select(run, ev, rules=["TRACE-001"], final=True))
    assert any(f.rule == "DEGRADED-001" for f in engine.select(run, ev, task="P-1"))
    assert "DEGRADED-001" in engine.rules_run(["TRACE-001"])
    assert any("degraded_disclosure" in m for m in messages(minimal_run,
                                                            authorization.records_valid))
    edit_yaml(minimal_run / LEDGER, lambda d: d["records"][1].__setitem__(
        "degraded_disclosure", "SP 800-37r2 was unobtainable; the fallback edition was used."))
    assert messages(minimal_run, authorization.records_valid) == []


def test_no_index_means_no_degraded(minimal_run, monkeypatch):
    def broken(root):
        raise refs.IndexFileError("unreadable")

    monkeypatch.setattr(refs, "load_index", broken)
    assert messages(minimal_run, config.degraded) == []


def test_stale_upstream_variants(minimal_run):
    assert messages(minimal_run, config.stale_upstream) == []
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__(
        "upstream_hash_basis", {"variant": "scenario",
                                "scenario": "tests/agent/scenarios/skeleton.yaml"}))
    assert any("scenario skeleton hash differs" in m
               for m in messages(minimal_run, config.stale_upstream))
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__(
        "upstream_hash_basis", {"variant": "scenario", "scenario": "no/such/scenario.yaml"}))
    assert any("cannot recompute" in m for m in messages(minimal_run, config.stale_upstream))


def test_aodm_decision_checks(minimal_run):
    def edit(d):
        r = d["records"][1]
        r["decision"] = "AD-ATO"
        r["decided_by"] = "PER-AODR"
        del r["authorization_termination_date"]
        del r["rar_ref"]
    edit_yaml(minimal_run / LEDGER, edit)
    found = " | ".join(messages(minimal_run, authorization.records_valid)
                       + messages(minimal_run, authorization.parties_valid))
    assert "decided by PER-AO, not PER-AODR" in found
    assert "authorization_termination_date" in found and "no rar_ref" in found
    edit_yaml(minimal_run / LEDGER,
              lambda d: d["records"][1].__setitem__("decision", "AD-NOPE"))
    assert any("not one of" in m for m in messages(minimal_run, authorization.records_valid))


def test_deferring_a_core_producer_is_refused(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d["deferred"].__setitem__(
        "S-5", {"kind": "later-cycle", "rationale": "Monitoring strategy next cycle."}))
    assert any("S-5 produces core artifact ART-CONMON" in m
               for m in messages(minimal_run, consistency.deferrals))
    edit_yaml(minimal_run / "run.yaml", lambda d: d["deferred"]["P-6"].__setitem__(
        "rationale", "          "))
    assert any("deferral of P-6 has no rationale" in m
               for m in messages(minimal_run, consistency.deferrals))


def test_humans_crosscheck_branches(hybrid_run):
    assert messages(hybrid_run, hybrid.humans_crosscheck) == []
    int006 = hybrid_run / "interviews/INT-006-S-1-PER-ISSM.md"
    int006.write_text(int006.read_text().replace(" · fallback: human-unavailable", ""))
    assert any("simulates PER-ISSM, who is a listed human" in m
               for m in messages(hybrid_run, hybrid.humans_crosscheck))
    int012 = hybrid_run / "interviews/INT-012-R-4-PER-AO.md"
    int012.write_text(int012.read_text().replace("tag: SIMULATED",
                                                 "tag: SIMULATED · fallback: human-unavailable"))
    assert any("PER-AO has no named person" in m
               for m in messages(hybrid_run, hybrid.humans_crosscheck))
    edit_yaml(hybrid_run / "run.yaml", lambda d: d.__setitem__("mode", "synthetic"))
    assert any("but the run is synthetic" in m
               for m in messages(hybrid_run, hybrid.humans_crosscheck))


@pytest.mark.parametrize("old, new, needle", [
    ("interview_id: INT-013", "interview_id: INT-012", "file name says"),
    ("task: P-1\n", "task: Q-1\n", "unknown task"),
    ("persona: PER-CIO\n", "persona: PER-NOBODY\n", "unknown persona"),
    ("run_id: valid-minimal", "run_id: other-run", "is not this run"),
    ("{#INT-013.A1}", "{#INT-014.A1}", "does not belong to INT-013"),
    ("{#INT-013.Q1}", "{#INT-013.Q2}", "sits under question INT-013.Q2"),
    ("Asked of: PER-CIO · Task: P-1\n", "", "has no 'Asked of:' line"),
    ("Task: P-1\n", "Task: P-2\n", "names task P-2"),
    ("---\ninterview_id", "interview_id", "front-matter"),
])
def test_interview_structure(minimal_run, old, new, needle):
    path = minimal_run / "interviews/INT-013-P-1-PER-CIO.md"
    text = path.read_text()
    assert old in text
    path.write_text(text.replace(old, new, 1))
    assert any(needle in m for m in messages(minimal_run, hybrid.interviews_wellformed)), needle


def test_interview_duplicates_and_empty(minimal_run):
    src = minimal_run / "interviews/INT-013-P-1-PER-CIO.md"
    (minimal_run / "interviews/INT-013-P-2-PER-RE.md").write_text(
        src.read_text().replace("task: P-1", "task: P-2").replace("PER-CIO", "PER-RE"))
    (minimal_run / "interviews/notes.md").write_text(
        "---\ninterview_id: INT-099\nrun_id: valid-minimal\ntask: P-1\npersona: PER-CIO\n"
        "date: 2026-10-29\n---\n# notes\n")
    found = " | ".join(messages(minimal_run, hybrid.interviews_wellformed))
    assert "interview_id INT-013 also used" in found and "answer INT-013.A1 also in" in found
    assert "file name must be" in found and "no answers" in found
    assert "date" not in found  # an unquoted YAML date reads as its ISO string


def test_lesson_references(minimal_run):
    path = minimal_run / "journal.md"
    path.write_text(path.read_text() + "\n## 2026-10-30T09:00Z · CORRECTION · artifact ART-SAR"
                    " · lesson: L-9999\n\n## 2026-10-30T09:10Z · RETRY · task A-3 · lesson: "
                    "none — flaky scan rerun\n")
    found = messages(minimal_run, journal.lesson_refs)
    assert found == ["CORRECTION cites L-9999, which is not in docs/LESSONS.md"]
    (minimal_run / "journal.md").unlink()
    assert messages(minimal_run, journal.lesson_refs) == []


def test_coverage_edge_cases(minimal_run):
    (minimal_run / "artifacts/data/sap.yaml").unlink()
    (minimal_run / "artifacts/data/conmon.yaml").unlink()
    assert messages(minimal_run, coverage.sap_coverage)[0].startswith("no readable SAP data")
    assert messages(minimal_run, coverage.conmon_frequencies)[0].startswith(
        "no readable conmon.yaml")
    sc = minimal_run / "artifacts/ssp/controls/sc.yaml"
    sc.write_text(sc.read_text().replace("status: inherited", "status: not-applicable"))
    assert messages(minimal_run, coverage.ssp_status) == ["sc-7 is not-applicable without a "
                                                         "rationale"]
    sc.write_text(sc.read_text().replace("status: not-applicable", "status: done"))
    assert "status 'done' is not one of" in messages(minimal_run, coverage.ssp_status)[0]


def test_sap_exclusion_needs_rationale(minimal_run):
    edit_yaml(minimal_run / "artifacts/data/sap.yaml", lambda d: d.__setitem__(
        "scope", {"include": "all", "excluded_controls": [{"control_id": "si-2",
                                                            "rationale": " "}]}))
    found = messages(minimal_run, coverage.sap_coverage)
    assert "scope.include must be 'baseline'" in found
    assert "excludes baseline control si-2 without a rationale" in found
    assert messages(minimal_run, coverage.sar_coverage) == []  # si-2 is out of the SAR scope


def test_package_listing_is_owned_by_the_producer(minimal_run):
    """A core artifact on disk but absent from the manifest blocks its producer, not R-1."""
    edit_yaml(minimal_run / "package/manifest.yaml", lambda d: d["package"].__setitem__(
        "artifacts", [a for a in d["package"]["artifacts"] if a["artifact_id"] != "ART-RAR"]))
    found = coverage.package_complete(Context(open_run(minimal_run, REPO_ROOT)))
    assert [(f.finding.message.split(";")[0], set(f.owners)) for f in found] == [
        ("core artifact ART-RAR is not in the manifest", {"R-2"})]


def test_stig_unknown_inventory_and_cat1(minimal_run):
    edit_yaml(minimal_run / "artifacts/data/stig-summary.yaml",
              lambda d: d["not_applicable"].append({"inventory_item": "INV-099",
                                                    "rationale": "Retired item."}))
    assert messages(minimal_run, consistency.stig_mapped) == [
        "not_applicable names INV-099, which is not in the inventory"]


def test_poam_unknown_control_and_contact(minimal_run):
    def edit(d):
        d["items"][0]["control_id"] = "zz-1"
        d["items"][0]["point_of_contact"] = "PER-NOBODY"
    edit_yaml(minimal_run / "artifacts/poam/items.yaml", edit)
    assert messages(minimal_run, consistency.poam_controls) == [
        "POAM-001: zz-1 is not an SP 800-53r5 control"]
    assert messages(minimal_run, consistency.poam_fields) == [
        "POAM-001: point_of_contact PER-NOBODY is not a framework persona"]


def test_rar_poam_link_mismatch(minimal_run):
    edit_yaml(minimal_run / "artifacts/data/rar.yaml",
              lambda d: d["risks"][0].__setitem__("poam_refs", ["POAM-002", "POAM-404"]))
    found = messages(minimal_run, consistency.rar_links)
    assert "RSK-001 links POA&M item POAM-404, which does not exist" in found
    assert any("RSK-001 links POAM-002, whose finding FND-002" in m for m in found)


def test_placeholders_in_data_and_interviews(minimal_run):
    path = minimal_run / "interviews/INT-013-P-1-PER-CIO.md"
    path.write_text(path.read_text() + "> <<FILL: follow-up answer>>\n")
    run = open_run(minimal_run, REPO_ROOT)
    build.build(run)
    found = [f for f in engine.select(run, engine.evaluate(run), final=True)
             if f.rule == "RUN-PH-001"]
    assert len(found) == 1 and found[0].path == "interviews/INT-013-P-1-PER-CIO.md"
