"""DOC-002: counts that README.md, AGENTS.md and the registry.yaml header state equal the
values computed from the registry, the framework and the reference index.

Each statement is a regex over one file. A file or sentence that is absent states nothing
and is not an error. README.md belongs to a fork, which may rewrite it; AGENTS.md and the
registry header are upstream-owned and the unit tests pin that they state their counts.
A statement whose count cannot be computed (unreadable index or framework) is one finding."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from rmf_tool import refs
from rmf_tool.check import REGISTRY_PATH, load_registry
from rmf_tool.findings import Finding
from rmf_tool.framework import load as framework_load
from rmf_tool.framework.model import FRAMEWORK_DIR

RULE = "DOC-002"
REGISTRY_REL = "src/rmf_tool/check/registry.yaml"
NIST_PUBLISHERS = ("NIST",)


class CountError(Exception):
    """The value a statement is checked against cannot be computed."""


@dataclass(frozen=True)
class Statement:
    file: str
    pattern: re.Pattern[str]
    labels: tuple[str, ...]  # one per capture group, keys of the computed values


STATEMENTS = (
    Statement(REGISTRY_REL, re.compile(
        r"^# Rule registry \(plan [^)]*\): (\d+) rules, (\d+) repo-scope and (\d+) run-scope",
        re.MULTILINE), ("rules", "repo rules", "run rules")),
    Statement("AGENTS.md", re.compile(r"\b(\d+) tasks\b"), ("tasks",)),
    Statement("AGENTS.md", re.compile(r"\b(\d+) personas\b"), ("personas",)),
    Statement("README.md", re.compile(r"\b[Tt]he (\d+) reference PDFs\b"), ("PDFs",)),
    Statement("README.md", re.compile(r"\b(\d+) NIST documents\b"), ("NIST PDFs",)),
    Statement("README.md", re.compile(r"\b(\d+) DoD and\s+CNSS documents\b"),
              ("DoD and CNSS PDFs",)),
)


def computed(root: Path) -> dict[str, Callable[[], int]]:
    """Lazy values, so a statement that is absent never triggers its computation."""
    def registry() -> tuple:
        path = root / REGISTRY_REL
        return load_registry(path if path.is_file() else REGISTRY_PATH)

    def counts() -> dict[str, int]:
        loaded = framework_load.load(root / FRAMEWORK_DIR, root)
        errors = [f for f in loaded.findings if f.severity == "E"]
        if errors:
            raise CountError(f"framework unreadable ({errors[0].message}, {errors[0].path})")
        return loaded.framework.counts()

    def pdfs() -> list:
        try:
            index = refs.load_index(root)
        except refs.IndexFileError as exc:
            raise CountError(str(exc)) from exc
        return [e for e in index["references"] if e["kind"] == "pdf" and e["status"] == "ok"]

    return {
        "rules": lambda: len(registry()),
        "repo rules": lambda: sum(r.scope == "repo" for r in registry()),
        "run rules": lambda: sum(r.scope == "run" for r in registry()),
        "tasks": lambda: counts()["tasks"],
        "personas": lambda: counts()["personas"],
        "PDFs": lambda: len(pdfs()),
        "NIST PDFs": lambda: sum(e["publisher"] in NIST_PUBLISHERS for e in pdfs()),
        "DoD and CNSS PDFs": lambda: sum(e["publisher"] not in NIST_PUBLISHERS for e in pdfs()),
    }


def check(root: Path) -> list[Finding]:
    values = computed(root)
    findings: list[Finding] = []
    for statement in STATEMENTS:
        path = root / statement.file
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in statement.pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            for group, label in enumerate(statement.labels, start=1):
                stated = int(match.group(group))
                try:
                    actual = values[label]()
                except CountError as exc:
                    findings.append(Finding(
                        RULE, "E", f"cannot compute {label} to check the {stated} stated: {exc}",
                        statement.file, line))
                    continue
                if stated != actual:
                    findings.append(Finding(
                        RULE, "E", f"states {stated} {label}; computed {actual}",
                        statement.file, line))
    return findings
