"""`rmf render [--check]`: generate ``MANUAL.md`` and ``docs/manual/PH-*.md`` from
``framework/`` (AC-9, AC-10). ``--check`` is FW-MAN-001 (AC-11): every committed file must
equal a fresh render byte for byte, and no other ``PH-*.md`` may linger in docs/manual.

The output is a pure function of the framework YAML and ``references/index.yaml``: no
dates, no environment, every list in a fixed order. MANUAL.md is the whole manual; each
phase file repeats one phase chapter so a reader can open just the phase they are in.
"""

from __future__ import annotations

import posixpath
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import jinja2

from rmf_tool import refs
from rmf_tool.findings import Finding
from rmf_tool.framework import graph
from rmf_tool.framework.load import display_path, load
from rmf_tool.framework.model import FRAMEWORK_DIR, STEP_ORDER, Framework, task_sort_key
from rmf_tool.framework.validate import schema_findings

MANUAL_MD = "MANUAL.md"
PHASE_DIR = "docs/manual"
RULE = "FW-MAN-001"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "manual"
RACI = (("R", "Responsible"), ("A", "Accountable"), ("C", "Consulted"), ("I", "Informed"))
PERSONA_RACI = ("Responsible for", "Accountable for", "Consulted on", "Informed of")
# Link label per entity kind; tasks, artifacts, external inputs and references use the ID.
_LABEL_FIELD = {"phases": "short", "milestones": "short", "reviews": "short",
                "decisions": "short", "personas": "short", "pathways": "short", "steps": "name"}


class RenderError(RuntimeError):
    """The framework cannot be rendered: it does not load or fails its schema."""

    def __init__(self, findings: list[Finding]) -> None:
        super().__init__(f"{len(findings)} framework error(s); run `rmf validate`")
        self.findings = findings


def text(value: Any) -> str:
    """One line of prose: YAML folding and indentation collapsed."""
    return "" if value is None else " ".join(str(value).split())


def cell(value: Any) -> str:
    return text(value).replace("|", "\\|")


def anchor(kind: str, ident: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", ident.lower()).strip("-")
    return {"tasks": "task-", "steps": "step-", "refs": "ref-"}.get(kind, "") + slug


def plain(value: Any) -> Any:
    """ruamel round-trip nodes as plain dicts, lists and scalars."""
    if isinstance(value, Mapping):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [plain(v) for v in value]
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        return int(value)
    return str(value)


class Links:
    """Markdown links as seen from one output document. In MANUAL.md every anchor is
    local; a phase file links its own chapter locally, other chapters to their phase
    files and everything else into MANUAL.md."""

    def __init__(self, doc: str, kinds: Mapping[str, tuple[str, str]],
                 homes: Mapping[str, str]) -> None:
        self.doc = doc
        self.kinds = kinds  # id -> (kind, label)
        self.homes = homes  # anchor -> phase file, used by phase files only

    def path(self, target: str) -> str:
        """A repo-relative path as seen from this document."""
        return posixpath.relpath(target, posixpath.dirname(self.doc) or ".")

    def href(self, ident: str) -> str:
        kind, _ = self.kinds[ident]
        key = anchor(kind, ident)
        target = MANUAL_MD if self.doc == MANUAL_MD else self.homes.get(key, MANUAL_MD)
        return f"#{key}" if target == self.doc else f"{self.path(target)}#{key}"

    def __call__(self, ident: str, label: str | None = None) -> str:
        if ident not in self.kinds:
            return ident  # dangling IDs are FW-REF-001's to report
        return f"[{label or self.kinds[ident][1]}]({self.href(ident)})"

    def many(self, idents: Iterable[str], empty: str = "—") -> str:
        return ", ".join(self(i) for i in idents) or empty

    def file(self, target: str, label: str | None = None) -> str:
        path, _, fragment = target.partition("#")
        href = self.path(path) + (f"#{fragment}" if fragment else "")
        return f"[{label or target}]({href})"

    def cite(self, c: Mapping[str, Any]) -> str:
        if "section" in c:
            section = text(c["section"])
            where = (f"section {section}" if re.fullmatch(r"[\d.]+", section)
                     else f'section "{section}"')
        else:
            where = f'p. {c.get("page")}, "{text(c.get("anchor"))}"'
        out = f"{self(str(c['ref']))}, {where}"
        if c.get("note"):
            out += f" ({text(c['note'])})"
        if isinstance(c.get("fallback"), Mapping):
            out += f"; fallback: {self.cite(c['fallback'])}"
        return out


def _raci(task: Mapping[str, Any], key: str) -> list[str]:
    """The persona IDs in one RACI column of a task (A holds a single ID)."""
    value = (task.get("raci") or {}).get(key)
    if key == "A":
        return [value] if value else []
    return list(value or [])


def _task_order(fw: Framework) -> list[str]:
    try:
        return graph.topo_order(graph.dependency_graph(fw))
    except graph.CycleError:  # FW-DAG-001 reports it; render in RMF order meanwhile
        return sorted(fw.index("tasks"), key=task_sort_key)


def _citations(data: Any) -> Iterable[Mapping[str, Any]]:
    for c in data.get("citations") or []:
        yield c
        if isinstance(c.get("fallback"), Mapping):
            yield c["fallback"]


def model(fw: Framework, index: Any, source: str) -> dict[str, Any]:
    """Everything the templates show, with every cross-reference precomputed."""
    def of(kind: str) -> list[dict[str, Any]]:
        return [plain(e.data) for e in fw.of(kind)]

    phases = sorted(of("phases"), key=lambda p: p["order"])
    milestones = sorted(of("milestones"), key=lambda m: m["order"])
    reviews = sorted(of("reviews"), key=lambda r: r["order"])
    steps = sorted(of("steps"), key=lambda s: s["order"])
    decisions, personas, artifacts = of("decisions"), of("personas"), of("artifacts")
    externals, pathways = of("external_inputs"), of("pathways")
    by_id = {t["id"]: t for t in of("tasks")}
    tasks = [by_id[t] for t in _task_order(fw)]
    step_names = {s["id"]: s["name"] for s in steps}
    artifact_ids = {a["id"] for a in artifacts}

    def where(test: Any) -> list[str]:
        return [t["id"] for t in tasks if test(t)]

    for t in tasks:
        tid = t["id"]
        aligned = t.get("aligned_with") or {}
        t["step_name"] = step_names.get(t["step"], t["step"])
        t["other_phases"] = [p for p in t.get("phases") or [] if p != t["primary_phase"]]
        t["raci_rows"] = [(label, _raci(t, k)) for k, label in RACI if _raci(t, k)]
        t["required_by"] = where(lambda x, tid=tid: tid in (x.get("depends_on") or []))
        t["fed_back_from"] = where(lambda x, tid=tid: tid in (x.get("feeds_back_to") or []))
        t["aligned"] = {k: list(aligned.get(k) or []) for k in ("milestones", "reviews",
                                                               "decisions")}
        t["output_rows"] = [
            (a, "produces" if any(x["id"] == a and x["producer"] == tid for x in artifacts)
             else "updates") for a in t.get("outputs") or []]
        t["input_producers"] = {a: [x["producer"] for x in artifacts if x["id"] == a]
                                for a in t.get("inputs") or [] if a in artifact_ids}

    for a in artifacts:
        a["updated_by"] = where(lambda t, a=a: a["id"] in (t.get("outputs") or [])
                                and t["id"] != a["producer"])
        a["used_by"] = where(lambda t, a=a: a["id"] in (t.get("inputs") or []))
    for x in externals:
        x["used_by"] = where(lambda t, x=x: x["id"] in (t.get("inputs") or []))

    for p in personas:
        pid = p["id"]
        p["raci"] = [(phrase, where(lambda t, k=k, pid=pid: pid in _raci(t, k)))
                     for (k, _), phrase in zip(RACI, PERSONA_RACI, strict=True)]
        p["decides"] = [d["id"] for d in decisions if d["decided_by"] == pid]
        p["milestone_authority"] = [m["id"] for m in milestones
                                    if m.get("decision_authority") == pid]
    for m in milestones:
        m["tasks"] = where(lambda t, m=m: m["id"] in t["aligned"]["milestones"])
    for r in reviews:
        r["tasks"] = where(lambda t, r=r: r["id"] in t["aligned"]["reviews"])
    for t in tasks:
        t["decides"] = [d["id"] for d in decisions if t["id"] in d["decided_in"]]
    for d in decisions:
        d["aligned_tasks"] = where(lambda t, d=d: d["id"] in t["aligned"]["decisions"]
                                   and t["id"] not in d["decided_in"])
    for s in steps:
        s["tasks"] = where(lambda t, s=s: t["step"] == s["id"])
        s["primary_phases"] = [p["id"] for p in phases
                               if any(by_id[t]["primary_phase"] == p["id"] for t in s["tasks"])]
    ms_names = {m["id"]: m["name"] for m in milestones}
    for p in phases:
        p["entry_name"] = ms_names.get(p["entry_milestone"], "")
        p["exit_name"] = ms_names.get(p["exit_milestone"], "")
        p["milestones"] = [m for m in milestones if m["phase"] == p["id"]]
        p["reviews"] = [r for r in reviews if r["phase"] == p["id"]]
        p["tasks"] = [t for t in tasks if t["primary_phase"] == p["id"]]
        p["also_tasks"] = where(lambda t, p=p: p["id"] in t["other_phases"])
        p["decisions"] = [d["id"] for d in decisions if p["id"] in d["phases"]]
        p["steps"] = sorted({by_id[t]["step"] for t in [*(x["id"] for x in p["tasks"]),
                                                        *p["also_tasks"]]},
                            key=lambda s: STEP_ORDER.index(s) if s in STEP_ORDER else 99)
        p["pathways"] = [w["id"] for w in pathways if p["id"] in w["phases"]]

    cited: set[str] = set()
    for e in fw.entities:
        cited.update(str(c.get("ref")) for c in _citations(e.data))
    references = [plain(r) for r in refs.entries(index) if r["id"] in cited]

    kinds: dict[str, tuple[str, str]] = {}
    for kind, items in (("phases", phases), ("milestones", milestones), ("reviews", reviews),
                        ("decisions", decisions), ("steps", steps), ("personas", personas),
                        ("artifacts", artifacts), ("external_inputs", externals),
                        ("pathways", pathways), ("tasks", tasks), ("refs", references)):
        field = _LABEL_FIELD.get(kind)
        for item in items:
            kinds[item["id"]] = (kind, str(item[field]) if field else item["id"])

    return {
        "meta": plain(fw.meta), "source": source, "phases": phases,
        "milestones": milestones, "reviews": reviews, "steps": steps,
        "decisions": decisions, "personas": personas, "artifacts": artifacts,
        "externals": externals, "pathways": pathways, "tasks": tasks,
        "references": references, "kinds": kinds,
        "personas_by_id": {p["id"]: p for p in personas},
        "artifacts_by_id": {a["id"]: a for a in artifacts},
        "externals_by_id": {x["id"]: x for x in externals},
        "raci_tables": _raci_tables(steps, tasks, personas),
        "mermaid": _mermaid(phases, milestones, decisions, by_id, step_names),
    }


def _raci_tables(steps: list[dict[str, Any]], tasks: list[dict[str, Any]],
                 personas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One matrix per RMF step, with only the personas that step involves as columns."""
    tables = []
    for s in steps:
        rows = [t for t in tasks if t["step"] == s["id"]]
        letters: dict[tuple[str, str], str] = {}
        for t in rows:
            for k, _ in RACI:
                for pid in _raci(t, k):
                    prior = letters.get((t["id"], pid))
                    letters[(t["id"], pid)] = f"{prior}/{k}" if prior else k
        cols = [p["id"] for p in personas if any(pid == p["id"] for _, pid in letters)]
        tables.append({"step": s, "columns": cols, "rows": [
            (t["id"], t["name"], [letters.get((t["id"], c), "") for c in cols])
            for t in rows]})
    return [t for t in tables if t["rows"]]


def _mermaid(phases: list[dict[str, Any]], milestones: list[dict[str, Any]],
             decisions: list[dict[str, Any]], tasks: Mapping[str, Any],
             step_names: Mapping[str, str]) -> str:
    """Phases chained through their entry and exit milestones; other milestones hang off
    their phase; each deciding task fans out to the decisions it can make."""
    def node(ident: str) -> str:
        return re.sub(r"[^A-Za-z0-9]", "_", ident)

    def label(*parts: str) -> str:
        return '"' + "<br/>".join(p.replace("&", "#amp;").replace('"', "#quot;")
                                  for p in parts) + '"'

    ms = {m["id"]: m for m in milestones}
    boundary = {p[k] for p in phases for k in ("entry_milestone", "exit_milestone") if p[k]}
    lines = ["flowchart LR"]
    emitted: set[str] = set()

    def milestone(mid: str) -> str:
        if mid in emitted or mid not in ms:
            return node(mid)
        emitted.add(mid)
        return f"{node(mid)}{{{{{label(ms[mid]['short'])}}}}}"

    prev: str | None = None
    for p in phases:
        entry = p["entry_milestone"]
        if entry and entry not in emitted:
            first = milestone(entry)
            lines.append(f"  {prev} --> {first}" if prev else f"  {first}")
            prev = node(entry)
        steps = ", ".join(step_names.get(s, s) for s in p["steps"])
        parts = [f"{p['short']}: {p['name']}", *([f"RMF: {steps}"] if steps else [])]
        here = f"{node(p['id'])}[{label(*parts)}]"
        lines.append(f"  {prev} --> {here}" if prev else f"  {here}")
        prev = node(p["id"])
        for m in p["milestones"]:
            if m["id"] not in boundary:
                lines.append(f"  {prev} -.- {milestone(m['id'])}")
        exit_ = p["exit_milestone"]
        if exit_:
            lines.append(f"  {prev} --> {milestone(exit_)}")
            prev = node(exit_)
    deciders = list(dict.fromkeys(t for d in decisions for t in d["decided_in"]))
    for tid in deciders:
        task = tasks.get(tid)
        if task is None:
            continue
        lines.append(f"  {node(task['primary_phase'])} -.-> "
                     f"{node(tid)}{{{label(tid + ' ' + task['name'])}}}")
        for d in decisions:
            if tid in d["decided_in"]:
                lines.append(f"  {node(tid)} --> {node(d['id'])}([{label(d['short'])}])")
    return "\n".join(lines)


def _env() -> jinja2.Environment:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
        autoescape=False,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=jinja2.StrictUndefined,
    )
    env.filters.update(text=text, cell=cell, yesno=lambda v: "yes" if v else "no")
    env.globals.update(anchor=anchor, h=lambda n: "#" * n)
    return env


def _tidy(rendered: str) -> str:
    """At most one blank line in a row, no trailing spaces, one final newline."""
    lines = [line.rstrip() for line in rendered.splitlines()]
    out: list[str] = []
    for line in lines:
        if line == "" and (not out or out[-1] == ""):
            continue
        out.append(line)
    while out and out[-1] == "":
        out.pop()
    return "\n".join(out) + "\n"


def render(fw_root: Path, repo: Path) -> dict[str, str]:
    """Repo-relative output path -> text: MANUAL.md and one file per phase. Raises
    RenderError for a framework that does not load or fails its schema, and
    refs.IndexFileError for an unreadable references/index.yaml."""
    loaded = load(fw_root, repo)
    problems = loaded.findings or schema_findings(loaded, repo)
    if problems:
        raise RenderError(problems)
    m = model(loaded.framework, refs.load_index(repo), display_path(fw_root, repo))
    env = _env()
    docs = {p["id"]: f"{PHASE_DIR}/{p['id']}.md" for p in m["phases"]}
    homes: dict[str, str] = {}
    for p in m["phases"]:
        homes[anchor("phases", p["id"])] = docs[p["id"]]
        for kind in ("milestones", "reviews", "tasks"):
            for item in p[kind]:
                homes[anchor(kind, item["id"])] = docs[p["id"]]
    out = {MANUAL_MD: _tidy(env.get_template("MANUAL.md.j2").render(
        m=m, L=Links(MANUAL_MD, m["kinds"], homes), docs=docs))}
    for p in m["phases"]:
        doc = docs[p["id"]]
        out[doc] = _tidy(env.get_template("phase_file.md.j2").render(
            m=m, p=p, L=Links(doc, m["kinds"], homes), docs=docs))
    return out


def _strays(root: Path, expected: Mapping[str, str]) -> list[str]:
    """Phase files in docs/manual that no longer correspond to a phase."""
    found = sorted((root / PHASE_DIR).glob("PH-*.md"))
    return [f"{PHASE_DIR}/{p.name}" for p in found if f"{PHASE_DIR}/{p.name}" not in expected]


def write(root: Path) -> tuple[list[str], list[str]]:
    """Write the changed outputs and delete stray phase files: (written, removed)."""
    expected = render(root / FRAMEWORK_DIR, root)
    written = []
    for rel, body in expected.items():
        path = root / rel
        data = body.encode("utf-8")
        if path.is_file() and path.read_bytes() == data:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        written.append(rel)
    removed = _strays(root, expected)
    for rel in removed:
        (root / rel).unlink()
    return written, removed


def check(root: Path) -> list[Finding]:
    """FW-MAN-001: the committed manual equals a fresh render, byte for byte."""
    try:
        expected = render(root / FRAMEWORK_DIR, root)
    except RenderError as exc:
        return [Finding(RULE, "E", f"cannot render: {exc}", FRAMEWORK_DIR)]
    except refs.IndexFileError as exc:
        return [Finding(RULE, "E", f"cannot render: {exc}", refs.INDEX_PATH)]
    findings = []
    for rel, body in expected.items():
        path = root / rel
        if not path.is_file():
            findings.append(Finding(RULE, "E", "missing; run `rmf render`", rel))
        elif path.read_bytes() != body.encode("utf-8"):
            findings.append(Finding(RULE, "E", "stale or edited by hand; run `rmf render` "
                                    "(never hand-edit the manual, INV-2)", rel))
    for rel in _strays(root, expected):
        findings.append(Finding(RULE, "E", "no such phase in framework/; run `rmf render` "
                                "to remove it", rel))
    return findings
