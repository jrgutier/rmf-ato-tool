import typer
from conftest import REPO_ROOT

from rmf_tool import agents_md
from rmf_tool.cli import app


def cli():
    return typer.main.get_command(app)


def real_text():
    return (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")


def messages(text):
    return [f.message for f in agents_md.check_text(text, cli())]


def test_real_agents_md_passes():
    assert agents_md.check(REPO_ROOT, cli()) == []


def test_sections_fixed_and_ordered():
    text = real_text()
    lines = text.splitlines()
    sections = [line[3:] for line in lines if line.startswith("## ")]

    assert tuple(sections) == agents_md.SECTIONS
    assert len(lines) <= agents_md.MAX_LINES
    assert messages(text.replace("## Fork workflow", "## Forking"))
    assert messages(text.replace("## Purpose", "## Learned rules", 1))


def test_length_limit():
    padded = real_text() + "\n" * agents_md.MAX_LINES
    assert any("limit is 250" in m for m in messages(padded))


def test_invariants_required():
    assert messages(real_text().replace("INV-5:", "INV-five:")) == [
        "Invariants section is missing INV-5"
    ]


def test_learned_rule_format():
    text = real_text().replace("None yet.", "- LR-01: Always do the thing (from L-0003)")
    assert messages(text) == []
    bad = real_text().replace("None yet.", "- LR-01: Always do the thing")
    assert len(messages(bad)) == 1


def test_command_paths_from_typer_app():
    paths = agents_md.command_paths(cli())

    assert {("doctor",), ("ci",), ("lessons",), ("lessons", "check")} <= paths
    assert ("lessons",) not in agents_md.leaf_paths(cli())


def test_commands_registered_and_documented():
    unregistered = real_text().replace(
        "| `rmf doctor` |", "| `rmf render --check` | x |\n| `rmf doctor` |"
    )
    assert messages(unregistered) == ["CLI section documents unregistered command: rmf render"]

    lines = [line for line in real_text().splitlines() if "`rmf lessons check`" not in line]
    assert messages("\n".join(lines)) == [
        "registered command not documented in CLI section: rmf lessons check"
    ]


def test_missing_file(tmp_path):
    assert [f.message for f in agents_md.check(tmp_path, cli())] == ["file not found"]
