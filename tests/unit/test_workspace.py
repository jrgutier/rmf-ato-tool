"""`rmf new` and `rmf run init` (plan §7.1, §4.4)."""

import re

import pytest
from conftest import REPO_ROOT

from rmf_tool.run import frontmatter, upstream_hash
from rmf_tool.run.model import read_yaml, schema_errors
from rmf_tool.workspace import (
    WorkspaceError,
    default_run_id,
    init_run,
    load_scenario,
    new_workspace,
    scenario_hash,
)

AS_OF = "2026-10-29T12:00:00Z"


def test_new_creates_layout(tmp_path):
    run_dir = new_workspace(tmp_path / "ws", "demo", REPO_ROOT, as_of=AS_OF)
    ws = tmp_path / "ws"
    assert (ws / "product").is_dir() and any((ws / "product").iterdir())
    assert run_dir.parent == ws / "runs"
    for rel in ("run.yaml", "facts.yaml", "assumptions.yaml", "journal.md",
                "artifacts/data", "interviews"):
        assert (run_dir / rel).exists(), rel
    assert (run_dir / "journal.md").read_text().startswith(f"# Journal — {run_dir.name}")
    config = read_yaml(run_dir / "run.yaml")
    assert schema_errors(REPO_ROOT, "run-config", config) == []
    assert config["product"] == "../../product"
    assert config["scope"] == {"tasks": "all"}


def test_new_refuses_nonempty_without_force(tmp_path):
    new_workspace(tmp_path, "demo", REPO_ROOT, as_of=AS_OF)
    with pytest.raises(WorkspaceError, match="not empty"):
        new_workspace(tmp_path, "demo", REPO_ROOT, as_of=AS_OF)
    run_dir = new_workspace(tmp_path, "demo", REPO_ROOT, force=True, as_of=AS_OF)
    assert run_dir.name.endswith("-02")


def test_run_id_default_format(tmp_path):
    (tmp_path / "product").mkdir()
    run_dir = init_run(tmp_path, REPO_ROOT, "hybrid", as_of=AS_OF)
    assert re.fullmatch(r"\d{8}-hybrid-01", run_dir.name)
    assert default_run_id(tmp_path / "runs", "hybrid").endswith("-hybrid-02")


def test_run_id_override_pattern(tmp_path):
    (tmp_path / "product").mkdir()
    assert init_run(tmp_path, REPO_ROOT, run_id="my-run", as_of=AS_OF).name == "my-run"
    for bad in ("My_Run", "ab"):
        with pytest.raises(WorkspaceError, match="must match"):
            init_run(tmp_path, REPO_ROOT, run_id=bad, as_of=AS_OF)
    with pytest.raises(WorkspaceError, match="already exists"):
        init_run(tmp_path, REPO_ROOT, run_id="my-run", as_of=AS_OF)
    with pytest.raises(WorkspaceError, match="--mode"):
        init_run(tmp_path, REPO_ROOT, mode="manual", as_of=AS_OF)


def test_run_yaml_stamps_upstream_hash(tmp_path):
    (tmp_path / "product").mkdir()
    config = read_yaml(init_run(tmp_path, REPO_ROOT, as_of=AS_OF) / "run.yaml")
    assert config["upstream_hash"] == upstream_hash.compute(REPO_ROOT, upstream_hash.UNION_GLOBS)
    assert config["upstream_hash_basis"] == {"variant": "union"}
    assert config["as_of"] == AS_OF
    assert config["oscal_version"] == "1.2.1"


def write_scenario(tmp_path, **extra):
    seeds = tmp_path / "seeds"
    (seeds / "artifacts").mkdir(parents=True)
    (seeds / "artifacts/ART-STAKE.md").write_text(
        "---\nartifact_id: ART-STAKE\nrun_id: seed-run\nproduced_by_task: P-9\n"
        "touched_by: [P-9]\nsources: []\n---\n# Stakeholders\n")
    (tmp_path / "prod").mkdir()
    body = {
        "name": "mini", "description": "test scenario", "product": "prod",
        "scope": {"tasks": ["P-10"]}, "seeds_dir": "seeds",
        "seeded": [{"artifact": "ART-STAKE", "from_task": "P-9",
                    "path": "artifacts/ART-STAKE.md"}],
        "hash_globs": ["prod/**"], **extra,
    }
    import json

    path = tmp_path / "mini.yaml"
    path.write_text(json.dumps(body))
    return path


def test_scenario_seeds_copied_and_hash_scoped(tmp_path):
    path = write_scenario(tmp_path, control_subset=["ac-2"])
    (tmp_path / "framework").symlink_to(REPO_ROOT / "framework")  # tmp_path acts as the repo
    run_dir = init_run(tmp_path / "ws", tmp_path, run_id="mini-run", scenario_path=path,
                       as_of=AS_OF)
    config = read_yaml(run_dir / "run.yaml")
    assert config["scope"] == {"tasks": ["P-10"]}
    assert config["control_subset"] == ["ac-2"]
    assert config["seeded"][0]["path"] == "artifacts/ART-STAKE.md"
    seed = frontmatter.parse((run_dir / "artifacts/ART-STAKE.md").read_text())
    assert seed.data["run_id"] == "mini-run"
    scenario = load_scenario(tmp_path, path)
    assert config["upstream_hash"] == scenario_hash(tmp_path, scenario)
    assert config["upstream_hash_basis"] == {"variant": "scenario", "scenario": "mini.yaml"}


def test_invalid_scenario_and_missing_seed(tmp_path):
    (tmp_path / "framework").symlink_to(REPO_ROOT / "framework")
    bad = tmp_path / "bad.yaml"
    bad.write_text("name: x\n")
    with pytest.raises(WorkspaceError, match="scenario invalid"):
        init_run(tmp_path / "ws", tmp_path, scenario_path=bad, as_of=AS_OF)
    path = write_scenario(tmp_path)
    (tmp_path / "seeds/artifacts/ART-STAKE.md").unlink()
    with pytest.raises(WorkspaceError, match="seed file"):
        init_run(tmp_path / "ws", tmp_path, scenario_path=path, as_of=AS_OF)


def _base_run(tmp_path):
    """A started run to resume from, with an SAR result and an OSCAL document."""
    path = write_scenario(tmp_path)
    (tmp_path / "framework").symlink_to(REPO_ROOT / "framework")
    base = init_run(tmp_path / "ws", tmp_path, run_id="base-run", scenario_path=path,
                    as_of=AS_OF)
    (base / "artifacts/sar/results").mkdir(parents=True)
    (base / "artifacts/sar/results/ac.yaml").write_text("results: []\n")
    (base / "oscal").mkdir()
    (base / "oscal/ssp.json").write_text("{}\n")
    return path, base


def _resume_scenario(path, remove):
    import json

    body = json.loads(path.read_text())
    body.update(name="resume", base_run="ws/runs/base-run", remove=remove)
    resume = path.with_name("resume.yaml")
    resume.write_text(json.dumps(body))
    return resume


def test_base_run_scenario_resumes_a_copy(tmp_path):
    """ADR-0004: base_run copies a run, removes paths and renames the run everywhere."""
    path, base = _base_run(tmp_path)
    resume = _resume_scenario(path, ["oscal", "artifacts/sar/results/ac.yaml"])
    run_dir = init_run(tmp_path / "ws2", tmp_path, run_id="resumed", scenario_path=resume,
                       as_of="2030-01-01T00:00:00Z")
    config = read_yaml(run_dir / "run.yaml")
    assert config["run_id"] == "resumed" and config["as_of"] == AS_OF  # the base's start
    assert config["upstream_hash_basis"] == {"variant": "scenario", "scenario": "resume.yaml"}
    assert not (run_dir / "oscal").exists()
    assert not (run_dir / "artifacts/sar/results/ac.yaml").exists()
    assert (run_dir / "journal.md").is_file() and (base / "oscal/ssp.json").is_file()
    seed = frontmatter.parse((run_dir / "artifacts/ART-STAKE.md").read_text())
    assert seed.data["run_id"] == "resumed"


def test_base_run_remove_must_exist_and_stay_inside(tmp_path):
    path, _ = _base_run(tmp_path)
    with pytest.raises(WorkspaceError, match="not in base_run"):
        init_run(tmp_path / "ws2", tmp_path, run_id="resumed",
                 scenario_path=_resume_scenario(path, ["oscal/nope.json"]))
    with pytest.raises(WorkspaceError, match="scenario invalid"):
        init_run(tmp_path / "ws3", tmp_path, run_id="resumed",
                 scenario_path=_resume_scenario(path, ["../base-run"]))


def test_remove_requires_base_run(tmp_path):
    path = write_scenario(tmp_path, remove=["oscal"])
    (tmp_path / "framework").symlink_to(REPO_ROOT / "framework")
    with pytest.raises(WorkspaceError, match="scenario invalid"):
        init_run(tmp_path / "ws", tmp_path, scenario_path=path, as_of=AS_OF)


def test_outside_a_repository(tmp_path):
    with pytest.raises(WorkspaceError, match="not an rmf repository"):
        init_run(tmp_path, tmp_path, as_of=AS_OF)


@pytest.mark.parametrize("slug", ["demo", "tactical-gcs-sys-17", "17th-wing-gcs",
                                  "abcdefghijklmnop-qrs", "ab--", "a---"])
def test_new_profile_matches_its_schema_for_any_accepted_slug(tmp_path, slug):
    new_workspace(tmp_path / "ws", slug, REPO_ROOT, as_of=AS_OF)
    profile = read_yaml(tmp_path / "ws/product/profile.yaml")
    assert schema_errors(REPO_ROOT, "product-profile", profile) == []
    assert profile["name"] == slug


def test_new_renders_every_real_template(tmp_path):
    new_workspace(tmp_path / "ws", "demo", REPO_ROOT, as_of=AS_OF)
    monitoring = (tmp_path / "ws/product/monitoring/README.md").read_text()
    assert "{#anchor}" in monitoring and "{%" not in monitoring
    assert "{{" not in (tmp_path / "ws/product/README.md").read_text()
