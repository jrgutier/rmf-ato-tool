"""Markdown front-matter (plan §6.4): a ``---`` YAML block at the top of the file."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ruamel.yaml import YAML

_FENCE = re.compile(r"^---[ \t]*$", re.M)


@dataclass(frozen=True)
class Document:
    data: Any  # the parsed mapping, or None
    error: str | None
    body: str
    body_line: int  # 1-based line number of the body's first line


def parse(text: str) -> Document:
    if not text.startswith("---"):
        return Document(None, "no front-matter (the file must start with ---)", text, 1)
    first = _FENCE.match(text)
    end = _FENCE.search(text, first.end() if first else 3)
    if first is None or end is None:
        return Document(None, "front-matter is not closed by ---", text, 1)
    raw = text[first.end():end.start()]
    body_start = text.find("\n", end.start())
    body = text[body_start + 1:] if body_start != -1 else ""
    body_line = text.count("\n", 0, body_start + 1) + 1 if body_start != -1 else 1
    try:
        data = YAML(typ="safe").load(raw)
    except Exception as exc:  # ruamel raises several unrelated parser error types
        return Document(None, f"front-matter is not valid YAML: {exc}", body, body_line)
    if not isinstance(data, dict):
        return Document(None, "front-matter must be a mapping", body, body_line)
    return Document(data, None, body, body_line)


def set_key(text: str, key: str, value: str) -> str:
    """Rewrite one top-level ``key: value`` line inside the front-matter, keeping the rest."""
    first = _FENCE.match(text)
    end = _FENCE.search(text, first.end()) if first else None
    if first is None or end is None:
        return text
    head = re.sub(rf"(?m)^{re.escape(key)}:.*$", f"{key}: {value}",
                  text[:end.start()], count=1)
    return head + text[end.start():]
