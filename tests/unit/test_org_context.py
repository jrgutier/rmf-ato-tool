"""What the organizational risk context rules allow: each case below is one the sources permit,
so a rule that starts refusing it fails here. The clauses that refuse have their negative
fixtures."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml

from rmf_tool.check import engine
from rmf_tool.run.model import open_run

ORG = "artifacts/data/org-context.yaml"
SSP_CM = "artifacts/ssp/controls/cm.yaml"


def _rule_errors(run_dir, rule):
    run = open_run(run_dir, REPO_ROOT)
    return [f.finding.message for f in engine.evaluate(run).findings if f.rule == rule]


def _role(d, rid):
    return next(r for r in d["roles"] if r["id"] == rid)


def _cio_is_the_ao(d):
    """SP 800-37r2: for selected systems the CIO may be designated as authorizing official."""
    ao = _role(d, "RA-03")
    ao.update(name="Component CIO (fixture)", title="Chief Information Officer",
              appointed_by="dod-component-head")


def _military_ao(d):
    _role(d, "RA-03")["affiliation"] = "military"
    _role(d, "RA-03")["position"]["recorded_in"] = "military-personnel-system"


def _ciso_serves_as_aodr(d):
    """The senior agency information security officer may serve as AODR."""
    aodr = _role(d, "RA-04")
    aodr.update(name="Component CISO (fixture)", title="Chief Information Security Officer",
                affiliation="dod-civilian")
    aodr["position"]["recorded_in"] = "DCPDS"


def _aodr_approves_the_package(d):
    for name in ("plan", "sar"):
        d["common_controls"][0][name]["approved_by"] = "PER-AODR"


def _organization_chooses_the_assessor(d):
    d["common_controls"][0]["assessed_by"]["chosen_by"] = "organization"


def _deficiencies_with_a_poam(d):
    cc = d["common_controls"][0]
    cc["deficiencies"] = True
    cc["poam"] = {"reference": "Enclave POA&M", "approved_by": "PER-AO",
                  "approved_on": "2026-01-10", "available_to": ["PER-PM"],
                  "available_on": "2026-01-12"}


def _no_code_signing(d):
    d["code_signing"] = {"used": False}


def _potential_relationship_not_yet_accepted(d):
    d["external_entities"].append({"id": "EXT-02", "name": "Allied partner", "relationship":
                                   "potential", "trust_model": "mediated", "sharing": "None yet",
                                   "sources": ["INT-014.A1"]})


def _posture_factors_across_two_reviews(d):
    """The ongoing review is judged as a whole: two reviews may split the four factors."""
    first = d["posture_reviews"][0]
    first["considered"] = ["threats", "vulnerabilities"]
    d["posture_reviews"].append({**first, "date": "2026-12-15",
                                 "considered": ["technologies", "mission"]})


def _aodr_takes_part_in_the_allocation(d):
    d["resources"]["allocation"]["determined_by"] = ["PER-CIO", "PER-AODR"]


def _semi_annual_reviews_six_calendar_months_apart(d):
    """184 days apart, six calendar months: the cycle the organization states is met."""
    d["iscm"]["review_cycle"]["frequency"] = "semi-annually"
    d["iscm"]["reviews"] = [{**d["iscm"]["reviews"][0], "date": day}
                            for day in ("2025-07-01", "2026-01-01")]


def _contractor_program_manager(d):
    """The program manager holds no cybersecurity position, so no open function is needed."""
    _role(d, "RA-07")["affiliation"] = "contractor"


def _contractor_isso_opened_as_contractor_only(d):
    """A contractor is a contractor, not also non-DoD personnel."""
    d["open_functions"][0]["open_to"] = ["contractor"]


def _risk_executive_delegated(d):
    """SP 800-37r2: the SAORM may delegate the risk executive (function) to another official."""
    d["governance"]["risk_executive"].update(led_by="PER-CIO", delegated_to="PER-CIO")


def _unacceptable_relationship_with_a_response(d):
    d["external_entities"][0].update(risk_acceptable=False, accepted_by="PER-ISSM",
                                     response="Service withdrawn at the next renewal")


def _assessor_billet_in_another_organization(d):
    position = _role(d, "RA-10")["position"]
    position.update(manpower_id="IAA-12", manpower_of="Independent assessment activity")


def _privacy_official_holds_the_posture_review(d):
    d["posture_reviews"][0]["by"] = "PER-PRIV"


def _program_established_within_its_first_cycle(d):
    d["iscm"].update(established="2026-10-01", reviews=[], assessments=[])


def _reviews_within_frequency(d):
    d["iscm"]["reviews"].append({"date": "2027-01-20", "by": "PER-CISO", "considered":
                                 ["threats"], "strategy_adjusted": True})


@pytest.mark.parametrize(("rule", "edit"), [
    ("OCTX-001", _cio_is_the_ao),
    ("OCTX-001", _military_ao),
    ("OCTX-001", _ciso_serves_as_aodr),
    ("OCTX-005", _aodr_approves_the_package),
    ("OCTX-005", _organization_chooses_the_assessor),
    ("OCTX-005", _deficiencies_with_a_poam),
    ("OCTX-002", _no_code_signing),
    ("OCTX-004", _potential_relationship_not_yet_accepted),
    ("OCTX-008", _reviews_within_frequency),
    ("OCTX-011", _posture_factors_across_two_reviews),
    ("OCTX-004", _risk_executive_delegated),
    ("OCTX-004", _unacceptable_relationship_with_a_response),
    ("OCTX-013", _assessor_billet_in_another_organization),
    ("OCTX-011", _privacy_official_holds_the_posture_review),
    ("OCTX-008", _program_established_within_its_first_cycle),
    ("OCTX-008", _semi_annual_reviews_six_calendar_months_apart),
    ("OCTX-013", _contractor_program_manager),
    ("OCTX-013", _contractor_isso_opened_as_contractor_only),
    ("OCTX-012", _aodr_takes_part_in_the_allocation),
], ids=lambda v: v.__name__ if callable(v) else v)
def test_a_permitted_case_is_not_refused(rule, edit, tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / ORG, edit)
    assert _rule_errors(run_dir, rule) == []


def test_signed_components_alone_do_not_mean_certificates_are_issued(tmp_path):
    """cm-14 can be met by vendor signatures; DoDI 8500.01 binds the organization only "when code
    signing certificates are used"."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / ORG, _no_code_signing)
    edit_yaml(run_dir / SSP_CM, lambda d: d["controls"].append(
        {**d["controls"][0], "control_id": "cm-14", "status": "implemented"}))
    assert _rule_errors(run_dir, "OCTX-002") == []


def test_a_section_is_demanded_only_while_its_task_is_in_scope(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / ORG, lambda d: d.pop("risk_frame"))
    assert _rule_errors(run_dir, "OCTX-004")
    edit_yaml(run_dir / "run.yaml", lambda d: d["scope"].update(
        tasks=[t for t in ("P-1", "P-10", "P-11", "C-1", "C-2", "C-3", "S-1", "S-4")]))
    assert not any("risk_frame" in m for m in _rule_errors(run_dir, "OCTX-004"))


def test_an_old_contract_run_is_not_held_to_the_record(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    (run_dir / ORG).unlink()
    assert _rule_errors(run_dir, "OCTX-001")
    edit_yaml(run_dir / "run.yaml", lambda d: d.update(framework_version="0.1.0"))
    assert _rule_errors(run_dir, "OCTX-001") == []


def test_a_control_inherited_through_a_leveraged_authorization_rests_on_its_package(tmp_path):
    """An inherited control may come from an external provider whose authorization the system
    leverages (C-1), not only from an organizational common control provider."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    provider = "Analysis enclave boundary (common control)"
    edit_yaml(run_dir / ORG, lambda d: d["common_controls"][0].update(provided_by="Other"))
    assert _rule_errors(run_dir, "OCTX-006")
    edit_yaml(run_dir / "artifacts/data/leveraged-authorizations.yaml",
              lambda d: d["leveraged_authorizations"][0].update(provider=provider))
    edit_yaml(run_dir / ORG, lambda d: d["external_entities"][0].update(name=provider))
    assert _rule_errors(run_dir, "OCTX-006") == []


def _leaves(node, path=()):
    """Every value of the record, with its path: scalars, lists and mappings."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield (*path, key), value
            yield from _leaves(value, (*path, key))
    elif isinstance(node, list):
        for n, value in enumerate(node):
            yield (*path, n), value
            yield from _leaves(value, (*path, n))


def test_a_malformed_value_anywhere_is_never_a_traceback(tmp_path):
    """Each value of org-context.yaml replaced by a mapping, and each list by a list holding one,
    leaves every OCTX rule reporting findings, never raising; RUN-FM-001 reports the shape."""
    import copy

    from ruamel.yaml import YAML

    from rmf_tool.check.context import Context
    from rmf_tool.check.rules import RULES

    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    yaml = YAML(typ="safe")
    good = yaml.load((run_dir / ORG).read_text(encoding="utf-8"))
    rules = {rid: fn for rid, fn in RULES.items() if rid.startswith("OCTX-")}
    for path, value in list(_leaves(good)):
        bad = copy.deepcopy(good)
        parent = bad
        for part in path[:-1]:
            parent = parent[part]
        parent[path[-1]] = [{"x": 1}] if isinstance(value, list) else {"x": 1}
        with (run_dir / ORG).open("w", encoding="utf-8") as fh:
            yaml.dump(bad, fh)
        ctx = Context(open_run(run_dir, REPO_ROOT))
        for rid, rule in rules.items():
            try:
                rule(ctx)
            except Exception as exc:  # noqa: BLE001
                pytest.fail(f"{rid} raised {exc!r} on a malformed {'.'.join(map(str, path))}")


def test_an_event_driven_family_is_not_ranked_against_a_periodic_floor(tmp_path):
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "artifacts/data/conmon.yaml", lambda d: next(
        f for f in d["frequencies"] if f["family"] == "ia").update(frequency="event-driven"))
    assert _rule_errors(run_dir, "OCTX-009") == []


def test_no_posture_review_is_due_on_the_day_operations_start(tmp_path):
    """valid_minimal's newest record is the authorization itself: operations have not run yet."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / "run.yaml", lambda d: d.update(include_after_stop=["M-6"]))
    edit_yaml(run_dir / ORG, lambda d: d.update(posture_reviews=[]))
    assert _rule_errors(run_dir, "OCTX-011") == []
