"""Every persona a task holds responsible (RACI R) appears in its playbook's Interviews table,
so WFQ-002 never asks for an interview the playbook does not name (dry-run finding F-05-6)."""

import re

import yaml
from conftest import REPO_ROOT


def _interviews(text: str) -> str:
    m = re.search(r"(?ms)^#{2,3} Interviews\n(.*?)^#{2,3} ", text)
    return m.group(1) if m else ""


def test_responsible_personas_are_in_the_interviews_table():
    missing = {}
    for path in sorted((REPO_ROOT / "framework" / "tasks").glob("*.yaml")):
        for task in yaml.safe_load(path.read_text(encoding="utf-8"))["tasks"]:
            playbook = REPO_ROOT / str(task.get("playbook", ""))
            if not playbook.is_file():
                continue
            responsible = task.get("raci", {}).get("R") or []
            responsible = responsible if isinstance(responsible, list) else [responsible]
            text = playbook.read_text(encoding="utf-8")
            if task["id"] in ("P-1", "P-2", "P-3", "P-4", "P-5", "P-6", "P-7"):
                text = text.split(f"## Task {task['id']}\n", 1)[-1]
            section = _interviews(text)
            gone = [p for p in responsible if p not in section]
            if gone:
                missing[task["id"]] = gone
    assert missing == {}
