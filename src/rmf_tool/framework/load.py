"""Read ``framework/*.yaml`` and ``framework/tasks/*.yaml`` into one merged document.

Every file is a mapping with one collection key (``phases: [...]``); ``meta.yaml`` is the
meta mapping itself. The merged document ``{meta, phases, ..., tasks}`` is what
``framework.schema.json`` validates. Unreadable files are FW-SCHEMA-001 findings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from rmf_tool.findings import Finding
from rmf_tool.framework.model import (
    COLLECTIONS,
    META_FILE,
    STEP_ORDER,
    TASKS_DIR,
    Entity,
    Framework,
    Location,
)


@dataclass
class Loaded:
    document: dict[str, Any]  # the merged document validated by the schema
    framework: Framework
    findings: list[Finding] = field(default_factory=list)
    # merged-document path prefix -> location, used to place schema errors
    origins: dict[tuple[str, int], Location] = field(default_factory=dict)


def display_path(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _line(node: Any, key: Any = None) -> int | None:
    """1-based line of ``node`` (or of its ``key``: a mapping key or a list index)."""
    lc = getattr(node, "lc", None)
    if lc is None:
        return None
    try:
        if key is None:
            return lc.line + 1
        return (lc.item(key) if isinstance(node, list) else lc.key(key))[0] + 1
    except (KeyError, IndexError, TypeError, AttributeError):
        return None


def _read(path: Path, shown: str, findings: list[Finding]) -> Any:
    try:
        return YAML(typ="rt").load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        findings.append(Finding("FW-SCHEMA-001", "E", f"cannot read: {exc.strerror or exc}",
                                shown))
    except Exception as exc:  # ruamel raises several unrelated parser error types
        findings.append(Finding("FW-SCHEMA-001", "E", f"not valid YAML: {exc}", shown))
    return None


def _task_files(root: Path) -> list[Path]:
    files = sorted((root / TASKS_DIR).glob("*.yaml"))
    rank = {s: i for i, s in enumerate(STEP_ORDER)}
    return sorted(files, key=lambda p: (rank.get(p.stem, len(rank)), p.name))


def load(root: Path, repo: Path) -> Loaded:
    findings: list[Finding] = []
    document: dict[str, Any] = {}
    entities: list[Entity] = []
    origins: dict[tuple[str, int], Location] = {}

    meta_path = root / META_FILE
    meta_shown = display_path(meta_path, repo)
    if not meta_path.is_file():
        findings.append(Finding("FW-SCHEMA-001", "E", "file not found", meta_shown))
    meta = _read(meta_path, meta_shown, findings) if meta_path.is_file() else None
    document["meta"] = meta if meta is not None else {}

    for coll in COLLECTIONS:
        if coll.kind == "tasks":
            paths = _task_files(root)
            if not paths:
                findings.append(Finding("FW-SCHEMA-001", "E", "no task files",
                                        display_path(root / TASKS_DIR, repo)))
        else:
            paths = [root / coll.file]
        items: list[Any] = []
        for path in paths:
            shown = display_path(path, repo)
            if not path.is_file():
                findings.append(Finding("FW-SCHEMA-001", "E", "file not found", shown))
                continue
            data = _read(path, shown, findings)
            if data is None:
                continue
            if not hasattr(data, "get") or coll.kind not in data:
                findings.append(Finding("FW-SCHEMA-001", "E",
                                        f"expected a mapping with key {coll.kind!r}", shown))
                continue
            seq = data[coll.kind]
            if not isinstance(seq, list):
                findings.append(Finding("FW-SCHEMA-001", "E", f"{coll.kind!r} must be a list",
                                        shown, _line(data, coll.kind)))
                continue
            for i, item in enumerate(seq):
                loc = Location(shown, _line(item) or _line(seq, i))
                origins[(coll.kind, len(items))] = loc
                items.append(item)
                if hasattr(item, "get"):
                    entities.append(Entity(coll.kind, item, loc))
        document[coll.kind] = items

    framework = Framework(meta=document["meta"], meta_location=Location(meta_shown, 1),
                          entities=entities)
    return Loaded(document, framework, findings, origins)
