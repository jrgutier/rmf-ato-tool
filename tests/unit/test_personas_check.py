"""AC-14: FW-PER-001 (a card for every persona) and FW-PER-002 (required sections and a
resolving citation), on the real cards and on the repo_neg fixtures."""

import shutil

import pytest
from _framework_fixtures import FIXTURES, MINI, REAL
from conftest import REPO_ROOT

from rmf_tool import refs
from rmf_tool.check import rules_by_id
from rmf_tool.framework import personas_check
from rmf_tool.framework.citations import Resolver
from rmf_tool.framework.load import load
from rmf_tool.framework.validate import IMPLEMENTED

REPO_NEG = FIXTURES / "repo_neg"


@pytest.fixture(scope="module")
def resolver():
    return Resolver(REPO_ROOT, refs.load_index(REPO_ROOT), strict=True)


def framework(root):
    return load(root, REPO_ROOT).framework


def test_every_real_persona_has_a_complete_card(resolver):
    fw = framework(REAL)
    assert len(fw.of("personas")) == 22
    assert personas_check.missing_cards(fw, REPO_ROOT) == []
    assert personas_check.card_problems(fw, REPO_ROOT, resolver) == []


def test_fw_per_001_fixture_fires_only_for_the_missing_card(resolver):
    root, fw = REPO_NEG / "FW-PER-001", framework(MINI)
    [finding] = personas_check.missing_cards(fw, root)
    assert finding.rule == "FW-PER-001"
    assert finding.message == "PER-IO: no persona card at personas/PER-IO.md"
    assert str(finding.path).endswith("personas.yaml")
    assert personas_check.card_problems(fw, root, resolver) == []


def test_fw_per_002_fixture_reports_each_defect(resolver):
    root, fw = REPO_NEG / "FW-PER-002", framework(MINI)
    assert personas_check.missing_cards(fw, root) == []
    found = personas_check.card_problems(fw, root, resolver)
    assert {f.rule for f in found} == {"FW-PER-002"}
    messages = [f.message for f in found]
    assert len(messages) == 4, messages
    assert "PER-AO: missing section '## Red lines'" in messages
    assert "PER-PM: section '## Typical concerns' is empty" in messages
    assert any(m.startswith("PER-ISSM: SP800-37R2 page 143 anchor 'NO SUCH ANCHOR")
               for m in messages)
    assert "PER-IO: '## Citations' has no `uv run rmf refs show ...` command" in messages


def test_a_card_named_after_another_persona_is_fw_per_001(tmp_path):
    shutil.copytree(MINI, tmp_path / "fw")
    personas = tmp_path / "fw" / "personas.yaml"
    personas.write_text(personas.read_text(encoding="utf-8").replace(
        "card: personas/PER-IO.md", "card: personas/PER-AO.md"), encoding="utf-8")
    [finding] = personas_check.missing_cards(framework(tmp_path / "fw"), REPO_ROOT)
    assert "PER-IO: card is 'personas/PER-AO.md'" in finding.message


@pytest.mark.parametrize("command, citation", [
    ('SP800-37R2 --section "TASK P-1"', {"ref": "SP800-37R2", "section": "TASK P-1"}),
    ('DODI8510.01 --page 26 --anchor "Communicate\n  organizational risk tolerance"',
     {"ref": "DODI8510.01", "page": 26, "anchor": "Communicate organizational risk tolerance"}),
])
def test_refs_show_commands_parse_as_citations(command, citation):
    assert personas_check._citation(command) == citation


@pytest.mark.parametrize("command", ["--page 3", "SP800-37R2 --page", "SP800-37R2 --page x",
                                     "SP800-37R2 --bogus 1"])
def test_malformed_refs_show_commands_are_rejected(command):
    with pytest.raises(ValueError):
        personas_check._citation(command)


def test_persona_rules_run_in_validate_and_point_at_their_fixtures():
    by_id = rules_by_id()
    for rule in ("FW-PER-001", "FW-PER-002"):
        assert rule in IMPLEMENTED
        assert by_id[rule].phase == "p5"
        assert by_id[rule].fixture == f"tests/fixtures/repo_neg/{rule}/"
        assert (REPO_ROOT / str(by_id[rule].fixture)).is_dir()
