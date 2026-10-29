"""Citation resolution for FW-CITE-002 (AC-8, AC-4a).

A citation is ``{ref, section}`` or ``{ref, page, anchor}``, resolved exactly as
``rmf refs show`` resolves it against the committed text extraction. Before p2x
(the Phase 2 exit gate), citations to ``pending-acquisition`` references are counted as
deferred instead of failing; from p2x on they must resolve. A citation to a
``degraded`` reference must carry a ``fallback`` citation that resolves (plan §7.6).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rmf_tool import refs
from rmf_tool.refs import show

OK, DEFERRED, ERROR = "ok", "deferred", "error"


@dataclass(frozen=True)
class Resolution:
    status: str  # OK | DEFERRED | ERROR
    message: str = ""


def describe(citation: Mapping[str, Any]) -> str:
    if "section" in citation:
        return f"{citation.get('ref')} section {citation['section']!r}"
    return f"{citation.get('ref')} page {citation.get('page')} anchor {citation.get('anchor')!r}"


class Resolver:
    """Resolves citations against ``references/``; ``strict`` is true from p2x on."""

    def __init__(self, repo: Path, index: Any, *, strict: bool) -> None:
        self.repo = repo
        self.strict = strict
        self._entries = {e["id"]: e for e in refs.entries(index)}
        self._located: dict[tuple[Any, ...], str | None] = {}

    def known(self, ref_id: Any) -> bool:
        return ref_id in self._entries

    def resolve(self, citation: Mapping[str, Any]) -> Resolution:
        problem = _form_problem(citation)
        if problem:
            return Resolution(ERROR, problem)
        ref_id = citation["ref"]
        entry = self._entries.get(ref_id)
        if entry is None:
            return Resolution(ERROR, f"unknown reference {ref_id!r}")
        status = entry["status"]
        if status == "pending-acquisition" and not self.strict:
            return Resolution(DEFERRED, f"{ref_id} is pending-acquisition (deferred before p2x)")
        if status == "degraded":
            fallback = citation.get("fallback")
            if not isinstance(fallback, Mapping):
                return Resolution(ERROR, f"{ref_id} is degraded; the citation needs a fallback")
            result = self.resolve(fallback)
            if result.status != OK:
                return Resolution(ERROR, f"fallback for degraded {ref_id}: {result.message}")
            return result
        if status != "ok":
            return Resolution(ERROR, f"{ref_id} is {status}, not ok")
        error = self._locate(entry, citation)
        return Resolution(ERROR, error) if error else Resolution(OK)

    def _locate(self, entry: Any, citation: Mapping[str, Any]) -> str | None:
        if "section" in citation:
            key: tuple[Any, ...] = (entry["id"], "section", str(citation["section"]))
        else:
            key = (entry["id"], "page", citation["page"], str(citation["anchor"]))
        if key not in self._located:
            try:
                if key[1] == "section":
                    show.section(self.repo, entry, key[2])
                else:
                    show.page(self.repo, entry, key[2], key[3])
                self._located[key] = None
            except show.NotFound as exc:
                self._located[key] = str(exc)
        return self._located[key]


def _form_problem(citation: Mapping[str, Any]) -> str | None:
    has_section, has_page, has_anchor = ("section" in citation, "page" in citation,
                                         "anchor" in citation)
    if has_section and (has_page or has_anchor):
        return "give either section or page+anchor, not both"
    if has_page and not has_anchor:
        return "a page citation requires an anchor"
    if has_anchor and not has_page:
        return "an anchor requires a page"
    if not has_section and not has_page:
        return "a citation needs a section or a page+anchor"
    return None
