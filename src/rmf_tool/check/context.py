"""What run rules read, loaded once per evaluation."""

from __future__ import annotations

from functools import cached_property
from typing import Any

from rmf_tool import refs
from rmf_tool.run import assumptions, authorization, frontmatter, interviews, scope
from rmf_tool.run import facts as facts_mod
from rmf_tool.run.model import ARTIFACTS_DIR, Run
from rmf_tool.run.trace import Resolver


class Context:
    def __init__(self, run: Run) -> None:
        self.run = run

    @cached_property
    def facts(self) -> dict[str, Any]:
        return facts_mod.load(self.run)

    @cached_property
    def ledger(self) -> list[dict[str, Any]] | None:
        return authorization.load(self.run)

    @cached_property
    def interviews(self) -> list[interviews.Interview]:
        return interviews.load_all(self.run)

    @cached_property
    def assumptions(self) -> tuple[list[dict[str, Any]], list[str]]:
        return assumptions.load(self.run)

    @cached_property
    def docs(self) -> dict[str, frontmatter.Document]:
        """Every artifacts/*.md, parsed."""
        out = {}
        for path in sorted((self.run.dir / ARTIFACTS_DIR).glob("*.md")):
            out[self.run.rel(path)] = frontmatter.parse(path.read_text(encoding="utf-8"))
        return out

    @cached_property
    def resolver(self) -> Resolver:
        items, _ = self.assumptions
        return Resolver(self.run, interviews.answer_ids(self.interviews),
                        {str(a.get("id")) for a in items})

    @cached_property
    def degraded_refs(self) -> list[str]:
        """Degraded references (plan §7.6) cited by an active task or by an artifact in play;
        an unreadable index reads as none (REF-001 reports it at repo scope)."""
        try:
            index = refs.load_index(self.run.repo)
        except refs.IndexFileError:
            return []
        degraded = {str(r["id"]) for r in index["references"] if r.get("status") == "degraded"}
        if not degraded:
            return []
        cited: set[str] = set()
        entities = [self.run.framework.index("tasks")[t] for t in scope.active_tasks(self.run)]
        entities += [e for aid, e in self.run.framework.index("artifacts").items()
                     if scope.produced_or_seeded(self.run, aid)]
        for e in entities:
            cited |= {str(c.get("ref")) for c in e.data.get("citations") or []
                      if isinstance(c, dict)}
        return sorted(degraded & cited)

    def interview_task(self, rel: str) -> str | None:
        return next((i.task for i in self.interviews if i.rel == rel), None)

    def data(self, rel: str) -> Any:
        """A run data file, or None when missing or unreadable (RUN-FM-001 reports it)."""
        try:
            return self.run.data(rel) if self.run.path(rel).is_file() else None
        except ValueError:
            return None
