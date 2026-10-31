"""Run-rule negative fixtures (plan §4.1): each ``tests/fixtures/negative/<RULE>.yaml``
mutates a copy of a base run; ``rmf check --final`` must then report exactly the rule's
errors plus the listed ``also`` errors (and, for a warning rule, the listed ``warnings``).
Bases: ``minimal`` (valid_minimal, scope all), ``hybrid`` (hybrid_minimal, skeleton scope)
and ``example`` (the uas-gcs synthetic run, Phase 7). Copies are re-stamped to the current
upstream hash, so the bases start without findings."""

from pathlib import Path

import pytest
from _mutations import apply
from conftest import EXAMPLE_RUN, HYBRID_MINIMAL, REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml
from ruamel.yaml import YAML

from rmf_tool import build
from rmf_tool.check import engine, load_registry
from rmf_tool.run.model import open_run

NEGATIVE = REPO_ROOT / "tests/fixtures/negative"
BASES = {"minimal": VALID_MINIMAL, "hybrid": HYBRID_MINIMAL}
if (EXAMPLE_RUN / "run.yaml").is_file():  # a fork deletes examples/ (plan §4.3)
    BASES["example"] = EXAMPLE_RUN
SPECS = sorted(NEGATIVE.glob("*.yaml"))


def final_findings(run_dir: Path, severity: str) -> set[str]:
    run = open_run(run_dir, REPO_ROOT)
    return {f.rule for f in engine.select(run, engine.evaluate(run), final=True)
            if f.severity == severity}


@pytest.mark.parametrize("base", sorted(BASES))
def test_base_has_no_findings(base, tmp_path):
    run_dir = copy_run(BASES[base], tmp_path / base)
    run = open_run(run_dir, REPO_ROOT)
    ev = engine.evaluate(run)
    assert engine.select(run, ev, final=True) == []
    assert ev.status.done


@pytest.mark.parametrize("base", sorted(BASES))
def test_committed_base_has_no_errors(base):
    """The committed fixture itself; only RUN-STALE-001 may warn, as upstream files move."""
    run = open_run(BASES[base], REPO_ROOT)
    found = engine.select(run, engine.evaluate(run), final=True)
    assert {f.rule for f in found} <= {"RUN-STALE-001"}


@pytest.mark.parametrize(("overlay", "expected"), [
    ("CNSSI1253F-ATT6-PRIVACY", "selected per control set"),
    ("CNSSI1253F-ATT2-SPACE", "not transcribed"),
])
def test_overlay_resolve_cannot_apply_reopens_c3(overlay, expected, tmp_path):
    """L-0035: an overlay S-1 could not apply is a FACTS-001 error charged to C-2 and C-3, so
    the approval reopens instead of S-1 stopping after it."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["categorization"].__setitem__("overlays", [overlay]))
    run = open_run(run_dir, REPO_ROOT)
    ev = engine.evaluate(run)
    found = [f for f in ev.findings if f.rule == "FACTS-001" and expected in f.finding.message]
    assert len(found) == 1 and found[0].owners == {"C-2", "C-3"}
    assert not ev.status.tasks["C-3"].done and ev.status.tasks["C-2"].done


def test_valid_minimal_is_non_vacuous():
    """PM-6: open findings carried by POA&M items and risks, a closed finding, an open CAT I
    STIG finding in the POA&M, inherited and not-applicable controls, an assumption, a
    conditional decision and scope all."""
    load = YAML(typ="safe").load
    run = VALID_MINIMAL
    sar = [f for p in sorted((run / "artifacts/sar/results").glob("*.yaml"))
           for f in load(p.read_text())["findings"]]
    poam = load((run / "artifacts/poam/items.yaml").read_text())["items"]
    rar = load((run / "artifacts/data/rar.yaml").read_text())["risks"]
    stig = load((run / "artifacts/data/stig-summary.yaml").read_text())["findings"]
    open_ids = {f["id"] for f in sar if f["status"] == "open"}
    refs = {i["finding_ref"] for i in poam}
    assert len(open_ids) >= 2 and open_ids <= refs
    assert open_ids <= {ref for r in rar for ref in r["finding_refs"]}
    assert any(f["status"] == "closed" for f in sar)
    assert any(f["category"] == "CAT I" and f["status"] == "open" and f["id"] in refs
               for f in stig)
    ssp = [c for p in sorted((run / "artifacts/ssp/controls").glob("*.yaml"))
           for c in load(p.read_text())["controls"]]
    assert any(c["status"] == "inherited" and c.get("inherited_from") for c in ssp)
    assert any(c["status"] == "not-applicable" and c.get("rationale") for c in ssp)
    assert load((run / "assumptions.yaml").read_text())["assumptions"]
    decision = load((run / "artifacts/data/decision.yaml").read_text())
    assert decision["decision"] == "AD-ATOC" and decision["conditions"]
    assert load((run / "run.yaml").read_text())["scope"]["tasks"] == "all"


def test_hybrid_minimal_exercises_tagging():
    """AC-15: human, simulated and fallback answers plus assumptions in a hybrid run."""
    text = "\n".join(p.read_text() for p in sorted((HYBRID_MINIMAL / "interviews").glob("*.md")))
    assert "respondent: human · tag: HUMAN" in text
    assert "respondent: simulated · tag: SIMULATED · fallback: human-unavailable" in text
    report = (HYBRID_MINIMAL / "reports/assumptions.md").read_text()
    assert "ASM-002" in report and "Dana Reyes" in report


@pytest.mark.parametrize("spec_path", SPECS, ids=[p.stem for p in SPECS])
def test_negative(spec_path, tmp_path):
    spec = YAML(typ="safe").load(spec_path.read_text(encoding="utf-8"))
    assert spec["rule"] == spec_path.stem
    bases = [b for b in spec.get("bases", ["minimal"]) if b in BASES]
    assert bases, "no base available"
    expect = spec["expect"]
    for base in bases:
        run_dir = copy_run(BASES[base], tmp_path / base)
        for mutation in spec["mutations"]:
            if base in mutation.get("only", [base]):
                apply(run_dir, mutation)
        if spec.get("build", True):
            build.build(open_run(run_dir, REPO_ROOT))
        errors = set(expect.get("errors") or []) | set(expect.get("also") or [])
        assert final_findings(run_dir, "E") == errors, (base, spec["description"])
        if "warnings" in expect:
            assert final_findings(run_dir, "W") == set(expect["warnings"]), (
                base, spec["description"])


def test_decision_must_be_one_decided_at_r4_or_m6(tmp_path):
    """C-2: AD-IATT is decided at A-2, so decision.yaml (written at R-4, updated at M-6)
    cannot carry it, though its other fields are valid."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/decision.yaml",
              lambda d: d.__setitem__("decision", "AD-IATT"))
    run = open_run(run_dir, REPO_ROOT)
    found = [f.finding.message for f in engine.evaluate(run).findings if f.rule == "AODM-001"]
    assert len(found) == 1
    assert "AD-IATT is decided in A-2, not in R-4" in found[0]


def _decision_findings(run_dir, decision, include_after_stop):
    edit_yaml(run_dir / "artifacts/data/decision.yaml", lambda d: d.__setitem__(
        "decision", decision))
    edit_yaml(run_dir / "run.yaml", lambda d: d.__setitem__(
        "include_after_stop", include_after_stop))
    run = open_run(run_dir, REPO_ROOT)
    return [f.finding.message for f in engine.evaluate(run).findings if f.rule == "AODM-001"]


def test_continuous_ato_needs_m6_in_this_run(tmp_path):
    """AD-CATO is decided at M-6; a run that stops at R-5 cannot record it (it has no ATD)."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    found = _decision_findings(run_dir, "AD-CATO", [])
    assert any("AD-CATO is decided in M-6, not in R-4" in m for m in found), found
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run2")
    found = _decision_findings(run_dir, "AD-CATO", ["M-6"])
    assert not any("is decided in" in m for m in found), found


@pytest.mark.parametrize("decision", ["AD-ATO", "AD-ATOC", "AD-DATO"])
def test_r4_decisions_pass_the_task_check(tmp_path, decision):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    assert not any("is decided in" in m for m in _decision_findings(run_dir, decision, []))


def test_task_needing_monitoring_data_reports_its_absence(tmp_path):
    """C-4 / L-0036: a run that includes M-2 needs product/monitoring/ (EXT-MONITORING); a
    README.md of guidance or a dot-file such as .DS_Store is not data. Owned by M-2."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "run.yaml", lambda d: d.__setitem__("include_after_stop", ["M-2"]))

    def reported():
        run = open_run(run_dir, REPO_ROOT)
        return [f for f in engine.evaluate(run).findings
                if f.rule == "RUN-CFG-001" and "EXT-MONITORING" in f.finding.message]

    found = reported()
    assert len(found) == 1 and found[0].owners == {"M-2"}
    assert "product/monitoring/" in found[0].finding.message
    monitoring = run_dir / "product/monitoring"
    monitoring.mkdir()
    (monitoring / "README.md").write_text("guidance only\n")
    assert len(reported()) == 1
    (monitoring / ".DS_Store").write_bytes(b"\x00")
    assert len(reported()) == 1
    (monitoring / "cycle-2026-10.md").write_text("# Cycle {#top}\n")
    assert reported() == []


BAD_PROFILE = "name: X\nacronym: X\npathway: PW-MCA\ncurrent_phase: PH-EMD\npii: yes\n"
BAD_BASELINE = {"op": "set_field", "file": "baseline.json", "path": "method", "value": "guess"}


@pytest.mark.parametrize(("mutation", "needle"), [
    (BAD_BASELINE, "baseline.schema.json"),
    ({"op": "write_file", "file": "product/profile.yaml", "content": BAD_PROFILE},
     "product-profile.schema.json"),
])
def test_baseline_and_product_profile_are_schema_checked(mutation, needle, tmp_path):
    """C-7: both schemas are enforced at run time under RUN-FM-001."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    apply(run_dir, mutation)
    run = open_run(run_dir, REPO_ROOT)

    messages = [f.finding.message for f in engine.evaluate(run).findings
                if f.rule == "RUN-FM-001"]

    assert any(needle in m for m in messages), messages


NOT_ON_EXAMPLE = {
    "HYB-003": "needs the named humans of a hybrid run; the example is synthetic",
    "RUN-CFG-001": "the example seeds nothing, so its seeded-file mutation has no target",
    "STIG-002": "the example has no open CAT I STIG finding to strip of its POA&M item",
}


def test_example_base_coverage_ge_80pct():
    """C-5: at least 80% of the mutation fixtures also run on the example, and each one
    left out is listed here with its reason. Every mutation applies to some base."""
    specs = {p.stem: YAML(typ="safe").load(p.read_text(encoding="utf-8")) for p in SPECS}
    left_out = {rule for rule, spec in specs.items() if "example" not in spec.get("bases", [])}

    assert left_out == set(NOT_ON_EXAMPLE)
    assert (len(specs) - len(left_out)) / len(specs) >= 0.8
    for rule, spec in specs.items():
        covered = {b for m in spec["mutations"] for b in m.get("only", spec["bases"])}
        assert covered == set(spec["bases"]), rule


def test_every_run_rule_is_implemented_with_a_fixture():
    run_rules = {r.id: r for r in load_registry() if r.scope == "run"}
    assert set(run_rules) == set(engine.IMPLEMENTED)
    specs = {p.stem for p in SPECS}
    for rid, rule in run_rules.items():
        assert rule.fixture, rid
        if rule.fixture.startswith("tests/fixtures/negative/"):
            assert rid in specs, rid
