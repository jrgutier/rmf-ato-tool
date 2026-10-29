"""Run-rule negative fixtures (plan §4.1): each ``tests/fixtures/negative/<RULE>.yaml``
mutates a copy of a base run; ``rmf check --final`` must then report exactly the rule's
errors plus the listed ``also`` errors (and, for a warning rule, the listed ``warnings``).
Bases: ``minimal`` (valid_minimal, scope all) and ``hybrid`` (hybrid_minimal, skeleton
scope); the ``example`` base arrives in Phase 7. Copies are re-stamped to the current
upstream hash, so the bases start without findings."""

from pathlib import Path

import pytest
from _mutations import apply
from conftest import HYBRID_MINIMAL, REPO_ROOT, VALID_MINIMAL, copy_run
from ruamel.yaml import YAML

from rmf_tool import build
from rmf_tool.check import engine, load_registry
from rmf_tool.run.model import open_run

NEGATIVE = REPO_ROOT / "tests/fixtures/negative"
BASES = {"minimal": VALID_MINIMAL, "hybrid": HYBRID_MINIMAL}
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
            apply(run_dir, mutation)
        if spec.get("build", True):
            build.build(open_run(run_dir, REPO_ROOT))
        errors = set(expect.get("errors") or []) | set(expect.get("also") or [])
        assert final_findings(run_dir, "E") == errors, (base, spec["description"])
        if "warnings" in expect:
            assert final_findings(run_dir, "W") == set(expect["warnings"]), (
                base, spec["description"])


def test_every_run_rule_is_implemented_with_a_fixture():
    run_rules = {r.id: r for r in load_registry() if r.scope == "run"}
    assert set(run_rules) == set(engine.IMPLEMENTED)
    specs = {p.stem for p in SPECS}
    for rid, rule in run_rules.items():
        assert rule.fixture, rid
        if rule.fixture.startswith("tests/fixtures/negative/"):
            assert rid in specs, rid
