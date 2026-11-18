"""`rmf run migrate` turns free-text provider names into PRV-## IDs (dry-run F-04-1)."""

from pathlib import Path

from conftest import edit_yaml

from rmf_tool.run.migrate import migrate_providers
from rmf_tool.run.model import open_run, read_yaml

ORG = "artifacts/data/org-context.yaml"
LA = "artifacts/data/leveraged-authorizations.yaml"
KEY = "leveraged_authorizations"


def _names_back(run_dir: Path) -> None:
    """Undo the fixture's migration: drop the registry, write names where IDs were."""
    org = run_dir / ORG
    text = org.read_text(encoding="utf-8")
    org.write_text(text[: text.index("\nproviders:")] + "\n", encoding="utf-8")
    edit_yaml(run_dir / LA, lambda d: d[KEY][0].update(provider="Enterprise IT"))


def test_names_become_registered_ids_and_a_rerun_changes_nothing(minimal_run):
    _names_back(minimal_run)
    run = open_run(minimal_run)
    lines = migrate_providers(run)
    assert any("Enterprise IT" in line for line in lines)
    org = read_yaml(minimal_run / ORG)
    ids = {p["name"]: p["id"] for p in org["providers"]}
    assert read_yaml(minimal_run / LA)[KEY][0]["provider"] == ids["Enterprise IT"]
    before = {p: (minimal_run / p).read_text(encoding="utf-8") for p in (ORG, LA)}
    assert migrate_providers(open_run(minimal_run)) == []
    assert before == {p: (minimal_run / p).read_text(encoding="utf-8") for p in (ORG, LA)}


def test_a_name_matching_a_registered_provider_takes_its_id(minimal_run):
    edit_yaml(minimal_run / LA,
              lambda d: d[KEY][0].update(provider="enterprise  it services"))
    migrate_providers(open_run(minimal_run))
    assert read_yaml(minimal_run / LA)[KEY][0]["provider"] == "PRV-02"
