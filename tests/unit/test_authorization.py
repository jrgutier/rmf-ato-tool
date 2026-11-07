"""The authorization ledger: what stands on a date, what a rule refuses that a one-mutation
negative fixture cannot express, and the move to the ledger with `rmf run migrate`."""

import datetime as dt
import shutil
from pathlib import Path

import pytest
from conftest import EXAMPLE_RUN, REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml
from ruamel.yaml import YAML

from rmf_tool.check import engine
from rmf_tool.check.context import Context
from rmf_tool.check.rules import authorization as rules
from rmf_tool.check.rules import config
from rmf_tool.run import authorization as ledger
from rmf_tool.run import status
from rmf_tool.run.migrate import migrate
from rmf_tool.run.model import open_run

FILE = "artifacts/data/authorizations.yaml"
EFFECTS = {"AD-IATT": "test", "AD-ATO": "authorize", "AD-DATO": "deny", "AD-CATO": "continuous",
           "AD-CONT": "continue", "AD-RCATO": "revoke-continuous", "AD-RESC": "rescind"}
ATO = {"id": "AUTH-001", "decision": "AD-ATO", "date": "2026-01-10",
       "authorization_termination_date": "2027-01-10"}
CATO = {"id": "AUTH-002", "decision": "AD-CATO", "date": "2026-03-01", "underlying": "AUTH-001"}
REVOKED = {"id": "AUTH-003", "decision": "AD-RCATO", "date": "2026-06-01",
           "underlying": "AUTH-001"}


def stands(records, on):
    return ledger.in_force(records, EFFECTS, dt.date.fromisoformat(on))


def test_cato_leaves_the_ato_in_the_ledger_and_lifts_its_date():
    now = stands([ATO, CATO], "2028-01-01")
    assert list(now) == ["AUTH-001"] and now["AUTH-001"].continuous == CATO
    assert now["AUTH-001"].expires is None


def test_revoking_a_cato_restores_the_ato_and_its_date():
    held = stands([ATO, CATO, REVOKED], "2026-07-01")["AUTH-001"]
    assert held.record == ATO and held.continuous is None
    assert held.expires == dt.date(2027, 1, 10)
    assert stands([ATO, CATO, REVOKED], "2027-02-01") == {}


def test_rescission_ends_the_authorization_on_its_date():
    rescind = {"id": "AUTH-002", "decision": "AD-RESC", "date": "2026-02-01",
               "underlying": "AUTH-001"}
    assert stands([ATO, rescind], "2026-01-31")
    assert not stands([ATO, rescind], "2026-02-01")


def test_a_later_ato_supersedes_the_earlier_one():
    later = {"id": "AUTH-002", "decision": "AD-ATO", "date": "2026-12-01",
             "supersedes": "AUTH-001", "authorization_termination_date": "2027-12-01"}
    assert list(stands([ATO, later], "2026-12-15")) == ["AUTH-002"]


def test_nothing_stands_before_the_first_decision_or_after_expiry():
    assert not stands([ATO], "2026-01-09")
    assert not stands([ATO], "2027-01-11")


def _set(run_dir: Path, **fields):
    edit_yaml(run_dir / FILE, lambda d: d["records"][-1].update(fields))


def _add(run_dir: Path, record: dict):
    edit_yaml(run_dir / FILE, lambda d: d["records"].append(record))


def _check(run_dir: Path, rule):
    return " | ".join(f.finding.message for f in rule(Context(open_run(run_dir, REPO_ROOT))))


def _m6_record(decision: str, **fields) -> dict:
    return {"id": "AUTH-003", "decision": decision, "subject": "system", "basis": "time-driven",
            "decided_by": "PER-AO", "task": "M-6", "date": "2026-12-15",
            "risk_level": "moderate", "risk_acceptance": "I accept the residual risk.",
            "signature": "pki", "conveyed_to": ["PER-PM"], "underlying": "AUTH-002",
            "review": {"frequency_days": 30, "events": ["significant change"]},
            "rationale": "Monitoring supports it.", "sources": ["INT-012.A1"], **fields}


@pytest.fixture
def cato_run(minimal_run: Path) -> Path:
    """A run past M-5 with a complete cATO on top of its ATO."""
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("include_after_stop", ["M-6"]))
    _add(minimal_run, _m6_record(
        "AD-CATO", dod_ciso_approval={"date": "2026-12-10", "reference": "DoD CISO memo"},
        component_ciso_notification={"date": "2026-12-01"}))
    edit_yaml(minimal_run / "facts.yaml", lambda d: d.__setitem__(
        "acquisition", {"pathway": "PW-SWP", "product_kind": "software", "set_by_task": "M-6"}))
    return minimal_run


def test_complete_cato_passes(cato_run):
    for rule in (rules.records_valid, rules.parties_valid, rules.termination_valid, rules.chain,
                 rules.cato_eligible):
        assert _check(cato_run, rule) == ""


def test_cato_needs_dod_ciso_approval(cato_run):
    edit_yaml(cato_run / FILE, lambda d: d["records"][-1].pop("dod_ciso_approval"))
    assert "dod_ciso_approval" in _check(cato_run, rules.cato_eligible)


def test_cato_approval_must_precede_the_decision(cato_run):
    _set(cato_run, dod_ciso_approval={"date": "2026-12-20", "reference": "memo"})
    assert "follows the decision" in _check(cato_run, rules.cato_eligible)


def test_component_ciso_is_notified_first(cato_run):
    edit_yaml(cato_run / FILE, lambda d: d["records"][-1].pop("component_ciso_notification"))
    assert "Component CISO" in _check(cato_run, rules.cato_eligible)
    _set(cato_run, component_ciso_notification={"date": "2026-12-12"})
    assert "notice follows" in _check(cato_run, rules.cato_eligible)


@pytest.mark.parametrize("pathway, kind, words", [
    ("PW-MCA", "software", "limited to"),
    ("PW-SWP", "software-enabled-hardware", "software-enabled-hardware programs cannot"),
])
def test_cato_pathway_limits(cato_run, pathway, kind, words):
    edit_yaml(cato_run / "facts.yaml", lambda d: d["acquisition"].update(
        pathway=pathway, product_kind=kind))
    assert words in _check(cato_run, rules.cato_eligible)


def test_cato_without_the_acquisition_fact_is_refused(cato_run):
    edit_yaml(cato_run / "facts.yaml", lambda d: d.pop("acquisition"))
    assert "facts.acquisition" in _check(cato_run, rules.cato_eligible)


def test_seeded_ledger_excuses_only_tasks_the_run_does_not_carry_out(cato_run):
    edit_yaml(cato_run / "run.yaml", lambda d: d.setdefault("seeded", []).append(
        {"artifact": "ART-AUTHREC", "from_task": "A-2", "path": FILE}))
    assert _check(cato_run, rules.records_valid) == ""
    (cato_run / "artifacts/ART-RAR.md").unlink()
    assert "have not written their outputs" in _check(cato_run, rules.records_valid)


def test_conveyed_to_must_be_a_list(minimal_run):
    _set(minimal_run, conveyed_to="PER-PM and others")
    assert "not conveyed to PER-PM" in _check(minimal_run, rules.parties_valid)


def test_a_malformed_review_is_left_to_the_schema(minimal_run):
    _add(minimal_run, _m6_record("AD-CONT", review="monthly"))
    _add(minimal_run, _m6_record("AD-CONT", id="AUTH-004", date="2027-06-01"))
    assert "past its" not in _check(minimal_run, rules.termination_valid)


def test_a_rule_without_a_registry_entry_fails_clearly(minimal_run, monkeypatch):
    monkeypatch.setitem(engine.RULES, "NOPE-001", lambda ctx: [])
    with pytest.raises(ValueError, match="NOPE-001"):
        engine.evaluate(open_run(minimal_run, REPO_ROOT))


def test_reached_tracks_the_outputs_of_earlier_tasks(minimal_run):
    run = open_run(minimal_run, REPO_ROOT)
    assert status.reached(run, "R-4")
    (minimal_run / "artifacts/ART-RAR.md").unlink()
    assert not status.reached(open_run(minimal_run, REPO_ROOT), "R-4")


def test_cato_rests_on_an_ato_in_force(cato_run):
    _set(cato_run, underlying="AUTH-001")
    assert "rests on an ATO, not AD-IATT" in _check(cato_run, rules.cato_eligible)
    _set(cato_run, underlying="AUTH-009")
    assert "AUTH-009 is not in force" in _check(cato_run, rules.chain)


def test_underlying_must_not_have_expired(cato_run):
    edit_yaml(cato_run / FILE, lambda d: d["records"][1].update(
        authorization_termination_date="2026-12-14"))
    assert "AUTH-002 is not in force on 2026-12-15" in _check(cato_run, rules.chain)


def test_atd_is_refused_where_the_type_forbids_it(cato_run):
    _set(cato_run, authorization_termination_date="2027-12-15")
    assert "carries no authorization_termination_date" in _check(cato_run, rules.termination_valid)


def test_ongoing_authorization_needs_review_and_acknowledgment(minimal_run):
    _add(minimal_run, _m6_record("AD-CONT"))
    assert "ongoing_acknowledgment" in _check(minimal_run, rules.termination_valid)
    edit_yaml(minimal_run / FILE, lambda d: d["records"][-1].pop("review"))
    assert "review" in _check(minimal_run, rules.termination_valid)


def test_ongoing_authorization_needs_a_complete_review_beneath_it(minimal_run):
    _add(minimal_run, _m6_record("AD-CONT", date="2026-11-25",
                                 ongoing_acknowledgment="I accept the process."))
    assert _check(minimal_run, rules.chain) == ""
    edit_yaml(minimal_run / FILE, lambda d: d["records"][-1].update(underlying="AUTH-001"))
    assert "basis test" in _check(minimal_run, rules.chain)


def test_time_driven_review_falls_within_the_frequency(minimal_run):
    _add(minimal_run, _m6_record("AD-CONT", ongoing_acknowledgment="I accept the process."))
    later = _m6_record("AD-CONT", id="AUTH-004", date="2027-01-14",
                       ongoing_acknowledgment="I accept the process.")
    _add(minimal_run, later)
    assert _check(minimal_run, rules.termination_valid) == ""
    _set(minimal_run, date="2027-01-15")
    assert "past its 30-day frequency" in _check(minimal_run, rules.termination_valid)


def test_ato_term_limit(minimal_run):
    _set(minimal_run, authorization_termination_date="2030-11-20")
    assert "exceeds AD-ATOC's limit of 1096" in _check(minimal_run, rules.termination_valid)


def test_cio_concurrence_precedes_the_decision(minimal_run):
    _set(minimal_run, risk_level="very-high", cio_concurrence={
        "by": "PER-CIO", "position": "concur", "date": "2026-11-21"})
    assert "follows the decision" in _check(minimal_run, rules.cio_concurrence)
    _set(minimal_run, cio_concurrence={"by": "PER-CISO", "position": "non-concur",
                                       "date": "2026-11-19"})
    found = _check(minimal_run, rules.cio_concurrence)
    assert "not PER-CIO" in found and "directions" in found
    _set(minimal_run, cio_concurrence={"by": "PER-CIO", "position": "non-concur",
                                       "date": "2026-11-19", "directions": "Close POAM-001."})
    assert _check(minimal_run, rules.cio_concurrence) == ""


def test_threat_assessment_is_required_and_reviewed_by_the_pm(minimal_run):
    _set(minimal_run, threat_assessment={
        "issued_by": "DIA", "issued": "2026-06-15", "reviewed_by": "PER-ISSM",
        "reviewed": "2026-12-01", "sources": ["INT-012.A1"]})
    found = _check(minimal_run, rules.threat_assessment)
    assert "not PER-ISSM" in found and "does not fall between" in found
    edit_yaml(minimal_run / FILE, lambda d: d["records"][-1].pop("threat_assessment"))
    assert "needs threat_assessment" in _check(minimal_run, rules.threat_assessment)


def test_atu_needs_the_providers_completed_ato(minimal_run):
    _set(minimal_run, decision="AD-ATU")
    assert "provider" in _check(minimal_run, rules.chain)
    _set(minimal_run, provider={"organization": "DISA", "decision": "AD-ATO",
                                "date": "2026-12-01", "package": "eMASS 1"})
    assert "follows the decision" in _check(minimal_run, rules.chain)
    _set(minimal_run, provider={"organization": "DISA", "decision": "AD-ATO",
                                "date": "2026-01-01", "package": "eMASS 1"})
    assert _check(minimal_run, rules.chain) == ""


def test_common_control_authorization_needs_its_subject_and_provider(minimal_run):
    _set(minimal_run, decision="AD-CCA")
    assert "decides on common-controls, not system" in _check(minimal_run, rules.parties_valid)
    _set(minimal_run, subject="common-controls")
    assert "not conveyed to PER-CCP" in _check(minimal_run, rules.parties_valid)
    _set(minimal_run, conveyed_to=["PER-CCP"])
    assert _check(minimal_run, rules.parties_valid) == ""
    edit_yaml(minimal_run / FILE, lambda d: d["records"][-1].pop(
        "authorization_termination_date"))
    assert "needs an authorization_termination_date" in _check(minimal_run, rules.records_valid)


def test_new_ao_cannot_extend_the_termination_date(minimal_run):
    new = {**_m6_record("AD-ATOC"), "id": "AUTH-003", "task": "R-4", "basis": "ao-change",
           "supersedes": "AUTH-002", "authorization_termination_date": "2028-01-01",
           "ao_transfer": {"outgoing": "Col A", "reviewed": ["decision document"]}}
    del new["underlying"]
    _add(minimal_run, new)
    assert "cannot extend" in _check(minimal_run, rules.chain)
    _set(minimal_run, authorization_termination_date="2027-11-20")
    assert _check(minimal_run, rules.chain) == ""
    edit_yaml(minimal_run / FILE, lambda d: d["records"][-1].pop("ao_transfer"))
    assert "ao_transfer" in _check(minimal_run, rules.chain)


def test_a_system_has_a_single_authorization(minimal_run):
    second = {**_m6_record("AD-ATO"), "task": "R-4", "basis": "initial"}
    del second["underlying"]
    _add(minimal_run, second)
    assert "single authorization, and AUTH-002 is in force" in _check(minimal_run, rules.chain)
    _set(minimal_run, supersedes="AUTH-002", basis="reauthorization")
    assert _check(minimal_run, rules.chain) == ""


def test_rcato_needs_a_cato_and_a_reason(cato_run):
    revoke = _m6_record("AD-RCATO", id="AUTH-004", date="2026-12-20",
                        revocation_reason="incident")
    _add(cato_run, revoke)
    assert _check(cato_run, rules.chain) == ""
    edit_yaml(cato_run / FILE, lambda d: d["records"][-1].pop("revocation_reason"))
    assert "revocation_reason" in _check(cato_run, rules.chain)
    edit_yaml(cato_run / FILE, lambda d: d["records"].pop(-2))
    assert "no cATO to revoke" in _check(cato_run, rules.chain)


def test_denial_at_m6_names_what_it_denies(minimal_run):
    record = _m6_record("AD-DATO", rar_ref="ART-RAR")
    del record["underlying"]
    _add(minimal_run, record)
    assert "names the authorization" in _check(minimal_run, rules.chain)


def test_touched_task_must_record_a_decision(minimal_run):
    edit_yaml(minimal_run / FILE, lambda d: d["records"].pop())
    assert "R-4 touched ART-AUTHREC but recorded no decision" in _check(
        minimal_run, rules.records_valid)


def test_record_id_is_unique(minimal_run):
    _set(minimal_run, id="AUTH-001")
    assert "used twice" in _check(minimal_run, rules.records_valid)


def test_empty_ledger_is_valid_at_a2(minimal_run):
    edit_yaml(minimal_run / FILE, lambda d: d.__setitem__("records", []))
    run = open_run(minimal_run, REPO_ROOT)
    errors = run.schema_errors("authorizations", {"records": []})
    assert errors == []


def _legacy(tmp_path: Path, decision: dict) -> Path:
    """A run as the old contract left it."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "old")
    (run_dir / FILE).unlink()
    (run_dir / "artifacts/ART-AUTHREC.md").unlink()
    yaml = YAML()
    with (run_dir / ledger.LEGACY_FILE).open("w", encoding="utf-8") as out:
        yaml.dump(decision, out)
    edit_yaml(run_dir / "run.yaml", lambda d: d.__setitem__("framework_version", "0.1.0"))
    return run_dir


OLD = {"decision": "AD-ATOC", "decided_by": "PER-AO", "date": "2026-11-20",
       "authorization_termination_date": "2027-11-20",
       "conditions": [{"id": "COND-01", "description": "Close POAM-001."}], "risk_level": "high",
       "rar_ref": "ART-RAR", "rationale": "Within tolerance.", "sources": ["INT-012.A1"]}


def test_old_contract_run_keeps_decision_yaml_and_skips_newer_rules(tmp_path):
    run_dir = _legacy(tmp_path, OLD)
    run = open_run(run_dir, REPO_ROOT)
    assert "ART-AUTHREC" not in run.artifacts
    assert run.data_files("ART-AODM")[0][0] == ledger.LEGACY_FILE
    assert "ART-AUTHREC" not in run.tasks["R-4"]["outputs"]
    found = {f.rule for f in engine.evaluate(run).findings}
    assert "RUN-VER-001" in found
    assert not found & {"AODM-002", "AODM-003", "AODM-004", "AODM-005", "AODM-007"}


def test_old_contract_still_gets_aodm_001(tmp_path):
    run_dir = _legacy(tmp_path, {**OLD, "decision": "AD-IATT"})
    assert "AD-IATT is decided in A-2, not in R-4" in _check(run_dir, rules.records_valid)


def test_migrate_moves_the_decision_and_is_repeatable(tmp_path):
    run_dir = _legacy(tmp_path, OLD)
    run = open_run(run_dir, REPO_ROOT)
    lines = migrate(run)
    assert any("1 record" in line for line in lines)
    assert not (run_dir / ledger.LEGACY_FILE).exists()
    moved = open_run(run_dir, REPO_ROOT)
    assert moved.contract == str(moved.framework.meta["framework_version"])
    record = ledger.load(moved)[0]
    assert record["task"] == "R-4" and record["decision"] == "AD-ATOC"
    assert record["authorization_termination_date"] == OLD["authorization_termination_date"]
    assert _check(run_dir, rules.records_valid) == ""
    assert "cio_concurrence" in _check(run_dir, rules.cio_concurrence)
    assert record["risk_acceptance"] == OLD["rationale"]
    assert any("never recorded signature" in line for line in lines)
    assert "already on contract" in migrate(open_run(run_dir, REPO_ROOT))[0]


def test_migrate_adds_a_missing_framework_version(tmp_path):
    run_dir = _legacy(tmp_path, OLD)
    edit_yaml(run_dir / "run.yaml", lambda d: d.pop("framework_version"))
    migrate(open_run(run_dir, REPO_ROOT))
    moved = open_run(run_dir, REPO_ROOT)
    assert moved.contract == str(moved.framework.meta["framework_version"])


def test_migrate_finishes_after_a_crash_between_steps(tmp_path):
    run_dir = _legacy(tmp_path, OLD)
    migrate(open_run(run_dir, REPO_ROOT))
    edit_yaml(run_dir / "run.yaml", lambda d: d.__setitem__("framework_version", "0.1.0"))
    migrate(open_run(run_dir, REPO_ROOT))
    assert ledger.load(open_run(run_dir, REPO_ROOT))[0]["decision"] == "AD-ATOC"


def test_migrate_says_when_a_cato_lost_its_ato(tmp_path):
    cato = {k: v for k, v in OLD.items() if k != "authorization_termination_date"}
    run_dir = _legacy(tmp_path, {**cato, "decision": "AD-CATO"})
    assert any("add the ATO record" in line for line in migrate(open_run(run_dir, REPO_ROOT)))


@pytest.mark.skipif(not (EXAMPLE_RUN / "run.yaml").is_file(), reason="a fork deletes examples/")
def test_example_migrates_onto_the_ledger(tmp_path):
    """Old fixtures convert: a copy of the example leaves only what the old contract lacked."""
    run_dir = copy_run(EXAMPLE_RUN, tmp_path / "example")
    migrate(open_run(run_dir, REPO_ROOT))
    run = open_run(run_dir, REPO_ROOT)
    assert ledger.load(run)
    assert "have not written their outputs" in _check(run_dir, rules.records_valid)  # DIAS, SVCA
    for rel in ("artifacts/ART-DIAS.md", "artifacts/data/dias.yaml", "artifacts/ART-SVCA.md",
                "artifacts/data/service-agreements.yaml"):
        shutil.copy(VALID_MINIMAL / rel, run_dir / rel)
    assert _check(run_dir, rules.records_valid) == ""
    assert "needs threat_assessment" in _check(run_dir, rules.threat_assessment)


def test_dot_directories_are_not_material(minimal_run):
    monitoring = minimal_run / "product/monitoring"
    (monitoring / ".git").mkdir(parents=True)
    (monitoring / ".git/config").write_text("x")
    assert not config._has_input(monitoring)
    (monitoring / "scan.csv").write_text("x")
    assert config._has_input(monitoring)


def test_product_dir_defaults_when_run_yaml_leaves_it_empty(minimal_run):
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("product", None))
    assert open_run(minimal_run, REPO_ROOT).product_dir.name == "product"


def _pins() -> list[tuple[str, str]]:
    """Every decision field the register pins as evidence: a pin only proves anything if a rule
    or the ledger's replay reads the field."""
    found = set()
    for path in (REPO_ROOT / "conformance/requirements").glob("*.yaml"):
        if "AD-" not in path.read_text(encoding="utf-8"):
            continue
        for entry in YAML(typ="safe").load(path.read_text(encoding="utf-8"))["requirements"]:
            for item in entry.get("evidence") or []:
                if item["kind"] == "pinned" and item["target"].startswith("AD-"):
                    found.add((item["target"], item["field"]))
    return sorted(found)


CHANGED = {"decided_by": lambda v: "PER-CIO", "decided_in": lambda v: ["P-1"],
           "max_term_days": lambda v: 10, "requires": lambda v: [],
           "effect": lambda v: "authorize" if v in ("deny", "rescind") else "rescind",
           "atd_forbidden": lambda v: not v,
           "applies_to": lambda v: ["common-controls"] if v == ["system"] else ["system"],
           "allowed_pathways": lambda v: ["PW-MCA"], "excluded_product_kinds": lambda v: []}
ATD = {"authorization_termination_date": "2027-12-01"}
AT_R4 = {"AD-ATO": {"decision": "AD-ATO"},
         "AD-ATU": {"decision": "AD-ATU", **ATD, "provider": {
             "organization": "DISA", "decision": "AD-ATO", "date": "2026-01-01", "package": "1"}},
         "AD-CCA": {"decision": "AD-CCA", "subject": "common-controls",
                    "conveyed_to": ["PER-CCP"]},
         "AD-DCCA": {"decision": "AD-DCCA", "subject": "common-controls",
                     "conveyed_to": ["PER-CCP"], "authorization_termination_date": None},
         "AD-DATO": {"decision": "AD-DATO", "authorization_termination_date": None}}


def _ledger_with(run_dir: Path, decision: str, field: str):
    edit_yaml(run_dir / "facts.yaml", lambda d: d.__setitem__("acquisition", {
        "pathway": "PW-SWP", "product_kind": "software-enabled-hardware", "set_by_task": "M-6"}))

    def write(data):
        if decision in AT_R4:
            for key, value in AT_R4[decision].items():
                if value is None:
                    data["records"][-1].pop(key)
                else:
                    data["records"][-1][key] = value
            if field == "requires":
                data["records"][-1].pop("threat_assessment", None)
                data["records"][-1].pop("provider", None)
        else:
            record = _m6_record(decision, revocation_reason="incident",
                                ongoing_acknowledgment="I accept.", **ATD)
            if field == "requires":  # a requirement only shows on a record that lacks it
                del record["review"]
            data["records"].append(record)
    edit_yaml(run_dir / FILE, write)


def _observed(run_dir: Path, decision: str = "", field: str = "") -> tuple:
    run = open_run(run_dir, REPO_ROOT)
    if field:
        kind = run.framework.index("decisions")[decision].data
        kind[field] = CHANGED[field](kind[field])
    context = Context(run)
    messages = sorted(f.finding.message for rule in (
        rules.records_valid, rules.parties_valid, rules.termination_valid, rules.chain,
        rules.threat_assessment, rules.cato_eligible) for f in rule(context))
    stands = ledger.in_force(ledger.load(run), ledger.effects(run))
    return messages, sorted(stands), [bool(s.continuous or s.ongoing) for s in stands.values()]


@pytest.mark.parametrize(("decision", "field"), _pins(), ids=lambda part: part)
def test_each_pinned_decision_field_changes_what_the_run_gets(minimal_run, decision, field):
    """Mutation proof: a pin that nothing reads would pass FW-REQ-003 and prove nothing."""
    edit_yaml(minimal_run / "run.yaml", lambda d: d.__setitem__("include_after_stop", ["M-6"]))
    _ledger_with(minimal_run, decision, field)
    assert _observed(minimal_run, decision, field) != _observed(minimal_run)


def test_business_days_leave_out_weekends_and_federal_holidays():
    """DoD CIO reciprocity memo 4.2.1.h: 60 business days, so a holiday does not count."""
    friday, next_monday = dt.date(2026, 11, 6), dt.date(2026, 11, 9)
    assert rules.business_days_between(friday, next_monday) == 1
    veterans_day = dt.date(2026, 11, 11)
    assert rules.business_days_between(veterans_day - dt.timedelta(1),
                                       veterans_day + dt.timedelta(1)) == 1
    july_3_observed = dt.date(2026, 7, 3)
    assert rules.business_days_between(july_3_observed - dt.timedelta(1),
                                       july_3_observed + dt.timedelta(3)) == 1


def test_a_single_course_of_action_stands_when_evaluated_adequate(minimal_run):
    """SP 800-39 p. 52: a lone course is evaluated for adequacy, so alternatives are not forced."""
    def one_course(data):
        course = data["risks"][0]["courses_of_action"][0]
        data["risks"][0]["courses_of_action"] = [{**course, "adequacy": "adequate"}]

    edit_yaml(minimal_run / "artifacts/data/rar.yaml", one_course)
    run = open_run(minimal_run, REPO_ROOT)
    assert not [f for f in engine.evaluate(run).findings if f.rule == "RAR-003"]

