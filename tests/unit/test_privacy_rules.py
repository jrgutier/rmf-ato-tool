"""What the privacy rules allow: each case below is one the sources permit, so a rule that starts
refusing it fails here, and malformed data reads as a finding, never a crash. The clauses that
refuse have their negative fixtures on the derived ``pii`` base."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, VALID_MINIMAL, copy_run, edit_yaml
from test_check_rules import base_copy

from rmf_tool.check import engine
from rmf_tool.run.model import open_run

INFOTYPES = "artifacts/data/infotypes.yaml"
PIA = "artifacts/data/pia.yaml"
CONMON = "artifacts/data/conmon.yaml"
PLAN_REVIEWS = "artifacts/data/plan-reviews.yaml"
PRIV = tuple(f"PRIV-{n:03d}" for n in range(1, 12))


def _privacy(run_dir):
    run = open_run(run_dir, REPO_ROOT)
    return [f.finding.message for f in engine.evaluate(run).findings if f.rule in PRIV]


@pytest.fixture
def pii(tmp_path):
    return base_copy("pii", tmp_path / "pii")


def test_a_system_with_no_pii_owes_no_privacy_record(tmp_path):
    """valid_minimal processes no PII: no PIA, PCM strategy, privacy plan or PER-PRIV
    interviews are asked of it, and PER-PRIV is not primary anywhere (RACI when)."""
    assert _privacy(copy_run(VALID_MINIMAL, tmp_path / "run")) == []


def test_an_nss_may_be_excluded_from_the_pia(pii):
    """DoDI 5400.16 1d(2): an NSS on its Privacy Overlay control set, its privacy implications
    considered and no ra-8 in its baseline, needs no PIA."""
    def nss(d):
        d["privacy"]["pia"].update(determination="not-required", basis="nss",
                                   privacy_implications="Considered under the Privacy Overlay.")
    edit_yaml(pii / INFOTYPES, nss)
    edit_yaml(pii / "facts.yaml",
              lambda d: d["categorization"].update(overlays=["CNSSI1253F-ATT6-PRIVACY-ACCT"]))
    messages = [m for m in _privacy(pii) if "PIA" in m and "NSS" in m]
    assert messages == []


def test_an_exclusion_holds_for_pii_about_the_subjects_a_pia_covers(pii):
    """DoDI 5400.16 1d: a matching agreement that addresses every PIA element excludes the PIA
    even for PII about federal personnel."""
    edit_yaml(pii / INFOTYPES, lambda d: d["privacy"]["pia"].update(
        determination="not-required", basis="matching-agreement"))
    assert not [m for m in _privacy(pii) if "is no basis for excluding it" in m]


def test_pii_about_foreign_nationals_abroad_alone_needs_no_pia(pii):
    """DoDI 8500.01 E3.j names foreign nationals employed at U.S. facilities abroad; others
    need a PIA only in some cases, so no PIA on another basis is not refused."""
    edit_yaml(pii / INFOTYPES, lambda d: (
        d["information_types"][1]["pii"].update(subjects=["foreign-nationals-other"]),
        d["privacy"]["pia"].update(determination="not-required", basis="new-system")))
    assert not [m for m in _privacy(pii) if "is no basis for excluding it" in m]


def test_a_reviewing_official_may_approve_the_pia(pii):
    """DoDI 5400.16 E3 2e: the Component CIO or the reviewing official approves."""
    edit_yaml(pii / PIA, lambda d: d["approval"].update(by="PER-AODR", role="reviewing-official"))
    assert _privacy(pii) == []


def test_publication_may_be_restricted_for_a_stated_reason(pii):
    """DoDI 5400.16 E3 3c: the Component can restrict publication of section 1."""
    edit_yaml(pii / PIA, lambda d: d["publication"].update(
        status="restricted", reason="Section 1 names a classified mission."))
    assert _privacy(pii) == []


def test_an_added_privacy_control_the_saop_approved_is_monitored(pii):
    """SP 800-37r2 S-5: a control the PCM strategy lacked joins it once the SAOP is consulted."""
    edit_yaml(pii / CONMON, lambda d: d["privacy"]["controls"].append({
        "control": "ac-2", "frequency": "quarterly", "origin": "added",
        "consultation": {"by": "PER-PRIV", "date": "2026-09-01", "appropriate": True,
                         "sources": ["INT-042.A1"]}}))
    assert _privacy(pii) == []


def test_a_system_without_pii_logs_security_only_plan_updates(tmp_path):
    """PRIV-010 asks the privacy plan in an update only of a system processing PII."""
    run_dir = copy_run(VALID_MINIMAL, tmp_path / "run")
    edit_yaml(run_dir / PLAN_REVIEWS, lambda d: d["changes"][1].update(plans=["security"]))
    assert _privacy(run_dir) == []


@pytest.mark.parametrize(("rel", "path", "value"), [
    (INFOTYPES, ("privacy", "compliance"), [["DOD5400.11-R"]]),
    (INFOTYPES, ("privacy", "pia", "basis"), ["nss"]),
    (INFOTYPES, ("information_types", 1, "pii", "subjects"), [{"public": True}]),
    (PIA, ("coordination", 0, "party"), ["issm"]),
    (PIA, ("approval", "role"), {"cio": 1}),
    (CONMON, ("privacy", "controls", 0, "control"), ["au-2"]),
    (PLAN_REVIEWS, ("changes", 0, "plans"), "privacy"),
    ("artifacts/data/changes.yaml", ("changes", 1, "privacy_impact"), ["yes"]),
])
def test_malformed_privacy_data_is_a_finding_not_a_crash(pii, rel, path, value):
    def set_value(d):
        node = d
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
    edit_yaml(pii / rel, set_value)
    run = open_run(pii, REPO_ROOT)
    assert engine.evaluate(run).findings  # schema findings at least, and no exception
