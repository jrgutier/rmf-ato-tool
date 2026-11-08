"""Cases the sources permit that CATG-001, CADJ-001 and PIIC-001 must not refuse: not
applicable on the confidentiality of an information type (FIPS 199, SP 800-60 v1r1 4.2), and the
approval of the PII determination by a designee of the SAOP (CNSSI 1253 2.3)."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, edit_yaml
from test_check_rules import base_copy

from rmf_tool.check import engine
from rmf_tool.run.model import open_run

INFOTYPES = "artifacts/data/infotypes.yaml"


def _found(run_dir, rule: str) -> list[str]:
    run = open_run(run_dir, REPO_ROOT)
    return [f.message for f in engine.select(run, engine.evaluate(run), final=True)
            if f.rule == rule or f.rule == "RUN-FM-001"]


def _all_types(level: str, objective: str = "confidentiality"):
    def edit(data):
        for info in data["information_types"]:
            info[objective] = {"base": level}
    return edit


def test_not_applicable_confidentiality_leaves_the_system_at_low(tmp_path):
    run_dir = base_copy("minimal", tmp_path / "run")
    edit_yaml(run_dir / INFOTYPES, _all_types("not-applicable"))
    edit_yaml(run_dir / "facts.yaml", lambda d: d["categorization"].__setitem__("c", "low"))
    assert _found(run_dir, "CATG-001") + _found(run_dir, "CADJ-001") == []


def test_not_applicable_confidentiality_does_not_lower_a_typed_mark(tmp_path):
    run_dir = base_copy("minimal", tmp_path / "run")

    def edit(data):
        data["information_types"][0]["confidentiality"] = {"base": "not-applicable"}
    edit_yaml(run_dir / INFOTYPES, edit)
    assert _found(run_dir, "CATG-001") + _found(run_dir, "CADJ-001") == []


@pytest.mark.parametrize("objective", ["integrity", "availability"])
def test_not_applicable_is_for_confidentiality_only(tmp_path, objective):
    run_dir = base_copy("minimal", tmp_path / "run")
    edit_yaml(run_dir / INFOTYPES, _all_types("not-applicable", objective))
    assert any("not-applicable" in m for m in _found(run_dir, "CATG-001"))


def test_a_designee_of_the_saop_may_approve(tmp_path):
    run_dir = base_copy("pii", tmp_path / "run")

    def edit(data):
        data["categorization"]["approved"]["privacy"].update(by="PER-ISSM",
                                                             designee_of="PER-PRIV")
    edit_yaml(run_dir / "facts.yaml", edit)
    assert _found(run_dir, "PIIC-001") == []


def test_the_designated_representative_may_review_the_categorization(tmp_path):
    run_dir = base_copy("minimal", tmp_path / "run")
    edit_yaml(run_dir / "facts.yaml",
              lambda d: d["categorization"]["approved"].__setitem__("approved_by", "PER-AODR"))
    assert _found(run_dir, "PIIC-001") == []
