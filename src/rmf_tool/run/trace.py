"""Trace tokens (INV-5, plan §7.4, frozen decision 6).

A token names an interview answer (``INT-007.A3``), an assumption (``ASM-012``,
``ASM-BASELINE-001``), a product file with an optional anchor
(``product/architecture.md#identity``) or an artifact (``ART-SSP``). Prose writes tokens as
``[[TOKEN]]``; YAML ``sources`` lists and front-matter hold bare tokens.

Product anchors are GitHub-style heading slugs or explicit ``{#id}`` heading suffixes
(Markdown), or mapping keys and ``id`` values (YAML).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from functools import cached_property
from pathlib import Path
from typing import Any

from rmf_tool.run.model import ARTIFACTS_DIR, MANIFEST_FILE, Run, YamlError, read_yaml

TOKEN = re.compile(
    r"INT-\d{3}\.A\d+|ASM-(?:[A-Z]+-)?\d{3}|product/[^\s#\[\]]+(?:#[A-Za-z0-9_.-]+)?"
    r"|ART-[A-Z]+(?:-[A-Z]+)*"
)
PROSE = re.compile(r"\[\[([^\[\]\n]*)\]\]")
MARKER_BLOCK = re.compile(r"<!-- BEGIN rmf:([a-z-]+)[^>]*-->.*?<!-- END rmf:\1 -->", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
EXPLICIT_ID = re.compile(r"\s*\{#([A-Za-z0-9_.-]+)\}\s*$")


def prose_tokens(text: str, first_line: int = 1) -> Iterator[tuple[str, int]]:
    """``[[...]]`` contents with their 1-based line numbers."""
    for lineno, line in enumerate(text.splitlines(), start=first_line):
        for m in PROSE.finditer(line):
            yield m.group(1).strip(), lineno


def strip_generated(text: str) -> str:
    """Blank out CLI marker blocks and comments, keeping line numbers."""
    def blank(m: re.Match[str]) -> str:
        return "\n" * m.group(0).count("\n")
    return COMMENT.sub(blank, MARKER_BLOCK.sub(blank, text))


def slug(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"[^a-z0-9 _-]", "", text)
    return text.replace(" ", "-")


def markdown_anchors(text: str) -> set[str]:
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        m = HEADING.match(line)
        if in_fence or not m:
            continue
        title = m.group(2)
        explicit = EXPLICIT_ID.search(title)
        if explicit:
            anchors.add(explicit.group(1))
            title = title[:explicit.start()]
        base = slug(title)
        n = seen.get(base, 0)
        seen[base] = n + 1
        anchors.add(base if n == 0 else f"{base}-{n}")
    return anchors


def yaml_anchors(data: Any) -> set[str]:
    anchors: set[str] = set()
    if isinstance(data, dict):
        for key, val in data.items():
            anchors.add(str(key))
            if key == "id" and isinstance(val, str):
                anchors.add(val)
            anchors |= yaml_anchors(val)
    elif isinstance(data, list):
        for item in data:
            anchors |= yaml_anchors(item)
    return anchors


class Resolver:
    """Resolves tokens against one run: answers, assumptions, product files, artifacts."""

    def __init__(self, run: Run, answers: set[str], assumptions: set[str]) -> None:
        self.run = run
        self.answers = answers
        self.assumptions = assumptions
        self._anchors: dict[Path, set[str] | None] = {}

    @cached_property
    def present_artifacts(self) -> set[str]:
        present = {p.stem for p in (self.run.dir / ARTIFACTS_DIR).glob("ART-*.md")}
        for aid, art in self.run.artifacts.items():
            if art.get("generated") and any(
                    (self.run.dir / d["path"]).is_file() for d in art.get("data") or []):
                present.add(aid)
        if (self.run.dir / MANIFEST_FILE).is_file():
            present.add("ART-PKG")
        return present

    def _file_anchors(self, path: Path) -> set[str] | None:
        if path not in self._anchors:
            try:
                if path.suffix in (".md", ".markdown"):
                    self._anchors[path] = markdown_anchors(path.read_text(encoding="utf-8"))
                elif path.suffix in (".yaml", ".yml"):
                    self._anchors[path] = yaml_anchors(read_yaml(path))
                else:
                    self._anchors[path] = None
            except (OSError, UnicodeDecodeError, YamlError):
                self._anchors[path] = None
        return self._anchors[path]

    def problem(self, token: str) -> str | None:
        """Why ``token`` does not resolve, or None when it does."""
        if not TOKEN.fullmatch(token):
            return f"malformed trace token {token!r}"
        if token.startswith("INT-"):
            return None if token in self.answers else f"no interview answer {token}"
        if token.startswith("ASM-"):
            return None if token in self.assumptions else \
                f"no assumption {token} in assumptions.yaml"
        if token.startswith("ART-"):
            if token not in self.run.artifacts:
                return f"unknown artifact {token}"
            return None if token in self.present_artifacts else f"artifact {token} not in the run"
        rel, _, anchor = token[len("product/"):].partition("#")
        base = self.run.product_dir
        path = (base / rel).resolve()
        if base != path and base not in path.parents:
            return f"{token} points outside the product directory"
        if not path.is_file():
            return f"product file {rel} not found under {self.run.config.get('product')}"
        if anchor:
            anchors = self._file_anchors(path)
            if anchors is None:
                return f"{token}: anchors resolve only in Markdown or YAML product files"
            if anchor not in anchors:
                return f"{token}: no heading or key {anchor!r} in {rel}"
        return None
