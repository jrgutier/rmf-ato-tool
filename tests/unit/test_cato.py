"""CATO-*: what the cATO Implementation Guide permits passes, and the record's optional file.

Negative fixtures prove each clause fires (tests/fixtures/negative/CATO-*.yaml); these tests
prove the rules leave alone what the guide allows: an objective row not fully met initially,
a row the organization does not select, a not-applicable row with a reason, and a revoked
cATO's conditions (IG p. 19)."""

from pathlib import Path

from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool import build
from rmf_tool.check import engine
from rmf_tool.framework.load import load
from rmf_tool.run.model import open_run

CATO = "artifacts/data/cato.yaml"
LEDGER = "artifacts/data/authorizations.yaml"
POAM = "artifacts/poam/items.yaml"


def _messages(run_dir: Path, rule: str) -> list[str]:
    build.build(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    return [f.message for f in engine.select(run, engine.evaluate(run), final=True)
            if f.rule == rule]


def _score(run_dir: Path, row: str, **fields) -> None:
    def edit(d):
        for s in d["assessment"]["scores"]:
            if s["requirement"] == row:
                s.update(fields)
    edit_yaml(run_dir / CATO, edit)


def _run(tmp_path: Path) -> Path:
    return copy_run(VALID_MINIMAL, tmp_path / "run")


def test_an_objective_row_not_fully_met_holds_no_practice_to_it(tmp_path):
    run_dir = _run(tmp_path)
    for row in ("SA03", "PP03", "TP02", "TP04", "TP08"):
        _score(run_dir, row, result="partially-met")

    def edit(d):
        d["platform"]["configuration_validation"] = "manual"
        d["monitoring"]["soc_strategy"] = "separate"
        d["people"]["position_descriptions"] = "in-progress"
        d["people"]["experience"].remove("assessing-security-practices")
        d["training"]["records"][0]["subjects"].remove("threat-actor-analysis")
    edit_yaml(run_dir / CATO, edit)
    for rule in ("CATO-001", "CATO-006", "CATO-007", "CATO-008", "CATO-009"):
        assert _messages(run_dir, rule) == [], rule


def test_an_objective_row_the_plan_does_not_select_need_not_be_scored(tmp_path):
    run_dir = _run(tmp_path)
    edit_yaml(run_dir / CATO, lambda d: d["assessment"].__setitem__(
        "scores", [s for s in d["assessment"]["scores"] if s["requirement"] != "SA03"]))
    assert _messages(run_dir, "CATO-001") == []


def test_any_row_may_be_not_applicable_with_a_reason(tmp_path):
    run_dir = _run(tmp_path)
    _score(run_dir, "PP06", result="not-applicable",
           reason="The DSOP shares no controls with this application.")
    assert _messages(run_dir, "CATO-001") == []


def test_a_revoked_cato_leaves_its_conditions_out_of_the_new_briefing(tmp_path):
    run_dir = _run(tmp_path)
    old = {"id": "AUTH-003", "decision": "AD-CATO", "subject": "system",
           "basis": "time-driven", "decided_by": "PER-AO", "task": "M-6", "date": "2026-11-21",
           "risk_level": "moderate", "risk_acceptance": "I accept the residual risk.",
           "signature": "pki", "conveyed_to": ["PER-PM"], "underlying": "AUTH-002",
           "review": {"frequency_days": 30, "events": ["significant change"]},
           "dod_ciso_approval": {"date": "2026-11-21", "reference": "DoD CISO memo"},
           "component_ciso_notification": {"date": "2026-11-21"},
           "conditions": [{"id": "COND-03", "description": "Old condition.", "due": "2027-01-01"}],
           "rationale": "Monitoring supports it.", "sources": ["INT-012.A1"]}
    revoke = {**{k: v for k, v in old.items() if k not in (
        "dod_ciso_approval", "component_ciso_notification", "conditions", "review")},
        "id": "AUTH-004", "decision": "AD-RCATO", "date": "2026-11-22"}
    edit_yaml(run_dir / LEDGER, lambda d: d["records"].extend([old, revoke]))
    assert _messages(run_dir, "CATO-012") == []


def test_a_high_finding_counts_against_a_reapplication_after_revocation(tmp_path):
    """An AD-CATO before this assessment belongs to an earlier pursuit, so the POA&M gate still
    applies to the cATO now sought."""
    run_dir = _run(tmp_path)
    old = {"id": "AUTH-003", "decision": "AD-CATO", "subject": "system",
           "basis": "time-driven", "decided_by": "PER-AO", "task": "M-6", "date": "2026-11-21",
           "risk_level": "moderate", "risk_acceptance": "I accept the residual risk.",
           "signature": "pki", "conveyed_to": ["PER-PM"], "underlying": "AUTH-002",
           "rationale": "Monitoring supports it.", "sources": ["INT-012.A1"]}
    edit_yaml(run_dir / LEDGER, lambda d: d["records"].append(old))
    edit_yaml(run_dir / POAM, lambda d: d["items"][1].update(residual_risk="high"))
    assert any("High or Very High" in m for m in _messages(run_dir, "CATO-002"))


def test_only_a_conditional_record_is_an_optional_data_file():
    """`optional: true` exempts a file from RUN-ART-001, so only a file a rule calls for, on a
    contract that has it, may carry it."""
    framework = load(REPO_ROOT / "framework", REPO_ROOT).framework
    optional = {(e.id, d["path"]) for e in framework.index("artifacts").values()
                for d in e.data.get("data") or () if d.get("optional")}
    assert optional == {("ART-AODM", "artifacts/data/cato.yaml"),
                        ("ART-RA", "artifacts/data/st-protection.yaml")}
    assert all(d.get("since") for e in framework.index("artifacts").values()
               for d in e.data.get("data") or () if d.get("optional"))


def test_a_practice_whose_row_is_not_owed_is_not_judged(tmp_path):
    """CATT-001 judges a threshold row's practice unless it is not-applicable, and an objective
    row's only once it is scored met (IG p. 19)."""
    run_dir = _run(tmp_path)
    _score(run_dir, "PP06", result="not-applicable",
           reason="The DSOP shares no controls with this application.")
    _score(run_dir, "CM01", result="partially-met")

    def edit(d):
        d["practices"]["inheritance"] = {"identified_by": "nobody", "model": "none"}
        d["practices"]["behavior_monitoring"] = "per-release"
        d["practices"]["proactive_capabilities"] = []
    edit_yaml(run_dir / CATO, edit)
    assert _messages(run_dir, "CATT-001") == []


def test_cm05_accepts_an_on_change_monitor_and_cm01_either_capability(tmp_path):
    """CM05 asks only that secure configurations are monitored for change, so an on-change
    monitor holds it (PP07's periodic checks are owed separately); CM01 reads "preventive /
    resiliency" as either."""
    run_dir = _run(tmp_path)
    _score(run_dir, "PP07", result="not-applicable",
           reason="The application runs outside the DSOP production system.")

    def edit(d):
        d["practices"]["configuration_checks"] = "on-change"
        d["practices"]["proactive_capabilities"] = ["resiliency"]
        d["practices"]["baseline_posture_evidence"] = ["penetration-test-report"]
    edit_yaml(run_dir / CATO, edit)
    assert _messages(run_dir, "CATT-001") == []
