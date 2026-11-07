"""FW-TPL-001: an artifact's required sections are headings of its template."""

import copy

from _framework_fixtures import REAL
from conftest import REPO_ROOT

from rmf_tool.framework.load import load as load_framework
from rmf_tool.framework.validate import Context, rule_template_sections


def _context():
    return Context(load_framework(REAL, REPO_ROOT).framework, REPO_ROOT, None)


def test_the_real_framework_names_only_template_headings():
    assert rule_template_sections(_context()) == []


def test_fw_tpl_001_fires_on_a_heading_the_template_lacks():
    ctx = _context()
    art = ctx.fw.index("artifacts")["ART-CP"]
    art.data["required_sections"] = [*copy.deepcopy(art.data["required_sections"]), "Annexes"]

    [finding] = rule_template_sections(ctx)

    assert finding.rule == "FW-TPL-001"
    assert "required section 'Annexes' is not a heading of templates/artifacts/ART-CP.md" \
        in finding.message


def test_cp_irp_and_cmp_require_every_heading_of_their_templates():
    artifacts = _context().fw.index("artifacts")
    for aid in ("ART-CP", "ART-IRP", "ART-CMP"):
        lines = (REPO_ROOT / artifacts[aid].data["template"]).read_text().splitlines()
        headings = [line[3:].strip() for line in lines if line.startswith("## ")]
        assert artifacts[aid].data["required_sections"] == headings, aid
