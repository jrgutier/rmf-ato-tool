"""Run-rule negative fixtures (plan §4.1): each ``tests/fixtures/negative/<RULE>.yaml``
mutates a copy of a base run; ``rmf check --final`` must then report exactly the rule's
errors plus the listed ``also`` errors. The ``example`` base arrives in Phase 7."""

import shutil
from pathlib import Path

import pytest
from _mutations import apply
from conftest import REPO_ROOT
from ruamel.yaml import YAML

from rmf_tool import build
from rmf_tool.check import engine, load_registry
from rmf_tool.run.model import open_run

NEGATIVE = REPO_ROOT / "tests/fixtures/negative"
BASES = {"minimal": REPO_ROOT / "tests/fixtures/runs/valid_minimal"}
SPECS = sorted(NEGATIVE.glob("*.yaml"))


def final_errors(run_dir: Path) -> set[str]:
    run = open_run(run_dir, REPO_ROOT)
    return {f.rule for f in engine.select(run, engine.evaluate(run), final=True)
            if f.severity == "E"}


def copy_base(base: str, tmp_path: Path) -> Path:
    return Path(shutil.copytree(BASES[base], tmp_path / base))


def test_valid_minimal_zero_errors():
    run = open_run(BASES["minimal"], REPO_ROOT)
    ev = engine.evaluate(run)
    assert engine.select(run, ev, final=True) == []
    assert ev.status.done


def test_valid_minimal_is_non_vacuous():
    """PM-6 where the skeleton allows: an open finding carried by a POA&M item."""
    run = open_run(BASES["minimal"], REPO_ROOT)
    sar = YAML(typ="safe").load((run.dir / "artifacts/sar/results/ac.yaml").read_text())
    poam = YAML(typ="safe").load((run.dir / "artifacts/poam/items.yaml").read_text())
    open_ids = {f["id"] for f in sar["findings"] if f["status"] == "open"}
    assert open_ids and open_ids <= {i["finding_ref"] for i in poam["items"]}


@pytest.mark.parametrize("spec_path", SPECS, ids=[p.stem for p in SPECS])
def test_negative(spec_path, tmp_path):
    spec = YAML(typ="safe").load(spec_path.read_text(encoding="utf-8"))
    assert spec["rule"] == spec_path.stem
    bases = [b for b in spec.get("bases", ["minimal"]) if b in BASES]
    assert bases, "no base available"
    for base in bases:
        run_dir = copy_base(base, tmp_path)
        for mutation in spec["mutations"]:
            apply(run_dir, mutation)
        if spec.get("build", True):
            build.build(open_run(run_dir, REPO_ROOT))
        expected = set(spec["expect"]["errors"]) | set(spec["expect"].get("also") or [])
        assert final_errors(run_dir) == expected, spec["description"]


def test_every_skeleton_rule_has_a_negative_spec():
    run_rules = {r.id for r in load_registry() if r.scope == "run" and r.phase == "p35"}
    assert run_rules == set(engine.IMPLEMENTED)
    assert {p.stem for p in SPECS} >= run_rules
