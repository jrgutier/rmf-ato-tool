"""`rmf playbooks sync`: playbook headers, and generated bodies, from framework/ YAML.

A playbook is ``playbooks/<step>/<task>.md``:

    <!-- BEGIN rmf:header -->
    ...generated: title, step, phases, dependencies, I/O, facts, RACI, persona cards...
    <!-- END rmf:header -->
    <!-- rmf:body authored -->        or        <!-- rmf:body generated -->
    ...procedure...

An authored body is never touched; it must hold the ``SECTIONS`` as H2 headings, in order.
A generated body is rendered from ``templates/playbook-body.md.j2`` and, like the header,
belongs to the CLI. To hand-tune a generated playbook, change its marker to authored.

Several tasks may share one authored playbook (P-1..P-7 share ``P/P-org-context.md``). Each
task's ``playbook:`` field then ends in an anchor (``#task-p-1``) that names a
``## Task P-1`` section; the section holds its own ``rmf:header P-1`` block and the
``SECTIONS`` as H3 headings.

``sync`` refreshes headers and generated bodies and creates a missing single-task playbook
with a generated body. ``check`` reports FW-PB-001 (a task whose playbook file or section
does not exist) and FW-PB-002 (CLI-owned text stale or edited by hand, no body marker, or
authored sections missing).
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import jinja2

from rmf_tool import labels
from rmf_tool.findings import Finding
from rmf_tool.framework.load import load
from rmf_tool.framework.model import FRAMEWORK_DIR, Framework

BEGIN = "<!-- BEGIN rmf:header -->"
END = "<!-- END rmf:header -->"
AUTHORED = "<!-- rmf:body authored -->"
GENERATED = "<!-- rmf:body generated -->"
_MARKER = re.compile(r"^<!-- rmf:body (authored|generated) -->$", re.M)
BODY_TEMPLATE = "templates/playbook-body.md.j2"
SECTIONS = ("Steps", "Interviews", "Inputs", "Outputs", "Facts", "Done when",
            "Journal and lessons", "Citations")
COVERAGE = "FW-PB-001"
RULE = "FW-PB-002"
# Inputs read through the CLI rather than as files.
CLI_INPUTS = {
    "EXT-CATALOG": "uv run rmf catalog show --family <fam> --run <run> --fields statement",
    "EXT-ASSESSMENT-PROCEDURES":
        "uv run rmf catalog show --family <fam> --run <run> --fields title,objectives",
    "EXT-BASELINES": "uv run rmf baseline resolve <run>",
}
# Generated artifacts (``generated: true``) and the command that writes them.
GENERATORS = {"ART-PKG": "uv run rmf package <run>"}


def _ids(items: list[str] | None) -> str:
    return ", ".join(items or []) or "—"


def _markers(task_id: str | None = None) -> tuple[str, str]:
    if task_id is None:
        return BEGIN, END
    return f"<!-- BEGIN rmf:header {task_id} -->", f"<!-- END rmf:header {task_id} -->"


def _block(task_id: str | None = None) -> re.Pattern[str]:
    begin, end = _markers(task_id)
    return re.compile(re.escape(begin) + r"\n.*?" + re.escape(end), re.S)


def _file(playbook: str) -> str:
    return playbook.partition("#")[0]


def _names(fw: Framework) -> dict[str, str]:
    """ID -> 'Name (ID)' for the entities a header names (tasks: 'Prepare 1: Name (P-1)')."""
    steps = {e.id: str(e.data.get("name", e.id)) for e in fw.of("steps")}
    out: dict[str, str] = {}
    for e in fw.of("tasks"):
        out[e.id] = labels.task_label(e.id, str(e.data.get("name", "")), steps)
    for kind in ("artifacts", "external_inputs"):
        for e in fw.of(kind):
            out[e.id] = labels.named(e.id, str(e.data.get("name", "")))
    for e in fw.of("phases"):
        out[e.id] = labels.named(e.id, str(e.data.get("name", "")))
    for e in fw.of("personas"):
        out[e.id] = labels.named(e.id, str(e.data.get("short") or e.data.get("name", "")))
    return out


def header(fw: Framework, task: dict[str, Any], playbook: str, section: bool = False) -> str:
    """The CLI-owned header; ``section`` gives the per-task block of a shared playbook."""
    steps = {e.id: e.data for e in fw.of("steps")}
    artifacts = fw.index("artifacts")
    names = _names(fw)

    def ids(values: Any) -> str:
        return ", ".join(names.get(str(v), str(v)) for v in values or []) or "—"

    step = steps.get(task["step"], {})
    phases = [p for p in task.get("phases") or [] if p != task.get("primary_phase")]
    def verb(a: str) -> str:
        return "produces" if artifacts[a].data.get("producer") == task["id"] else "updates"

    outputs = [f"{names.get(a, a)}, {verb(a)}" if a in artifacts else a
               for a in task.get("outputs") or []]
    raci = task.get("raci") or {}
    cards = []
    for pid in [*(raci.get("R") or []), raci.get("A"), *(raci.get("C") or [])]:
        if pid and pid not in [c[0] for c in cards]:
            card = os.path.relpath(f"personas/{pid}.md", os.path.dirname(_file(playbook)))
            cards.append((pid, Path(card).as_posix()))
    begin, end = _markers(task["id"] if section else None)
    label = labels.task_label(task["id"], task["name"], {k: str(v.get("name", k))
                                                         for k, v in steps.items()})
    title = f"**{label}**" if section else f"# {label}"
    lines = [
        begin,
        "<!-- Generated by `rmf playbooks sync` from framework/; edit the YAML, not here. -->",
        title,
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Step | {step.get('name', '')} ({task['step']}), {task.get('level', 'system')} level"
        f"{', optional' if task.get('optional') else ''} |",
        f"| Phases | {ids([task['primary_phase']]) if task.get('primary_phase') else '—'}"
        " (primary)" + (f", {ids(phases)}" if phases else "") + " |",
        f"| Depends on | {ids(task.get('depends_on'))} |",
        f"| Inputs | {ids(task.get('inputs'))} |",
        f"| Outputs | {'; '.join(outputs) or '—'} |",
        f"| Writes facts | {_ids(task.get('writes_facts'))} |",
        f"| Minimum interviews | {task.get('min_interviews', 0)} |",
        f"| RACI | R: {ids(raci.get('R'))} · A: {ids([raci['A']] if raci.get('A') else [])}"
        f" · C: {ids(raci.get('C'))} · I: {ids(raci.get('I'))}{_conditions(raci)} |",
        "| Persona cards | " + (", ".join(f"[{names.get(pid, pid)}]({path})"
                                         for pid, path in cards) or "—")
        + " |",
        "",
        f"Purpose: {' '.join(str(task.get('purpose', '')).split())}",
        end,
    ]
    return "\n".join(lines)


# --- generated bodies --------------------------------------------------------------------


def _command(cite: dict[str, Any]) -> str:
    if cite.get("section"):
        return f'uv run rmf refs show {cite["ref"]} --section "{cite["section"]}"'
    return (f'uv run rmf refs show {cite["ref"]} --page {cite.get("page")} '
            f'--anchor "{cite.get("anchor")}"')


def _named(fw: Framework, kind: str, ids: list[str] | None) -> list[dict[str, str]]:
    index = fw.index(kind)
    return [{"id": i, "name": str(index[i].data.get("name", "")) if i in index else ""}
            for i in ids or []]


def current_data(art: dict[str, Any]) -> list[dict[str, Any]]:
    """Data files on the current contract; an ``until`` entry serves older runs only."""
    return [d for d in art.get("data") or [] if "until" not in d]


def _data_files(root: Path, art: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for d in current_data(art):
        schema = d.get("schema")
        template = f"templates/data/{schema}.yaml" if schema else None
        out.append({"path": d["path"], "schema": schema,
                    "template": template if template and (root / template).is_file() else None})
    return out


# What a RACI condition means, in the words the header and the interview table show.
CONDITIONS = {"processes-pii": "only when the system processes PII"}


def _conditions(raci: dict[str, Any]) -> str:
    when = raci.get("when") or {}
    return "".join(f" · {pid} {CONDITIONS.get(c, c)}" for pid, c in when.items())


def context(fw: Framework, task: dict[str, Any], root: Path) -> dict[str, Any]:
    """What templates/playbook-body.md.j2 renders: the task's YAML, resolved to names,
    files and commands."""
    artifacts = fw.index("artifacts")
    externals = fw.index("external_inputs")
    personas = fw.index("personas")
    raci = task.get("raci") or {}
    roles: dict[str, list[str]] = {}
    for letter in ("R", "A", "C"):
        value = raci.get(letter)
        for pid in value if isinstance(value, list) else [value] if value else []:
            roles.setdefault(pid, []).append(letter)
    when = raci.get("when") or {}
    interviewees = [{"id": pid, "name": personas[pid].data.get("name", "") if pid in personas
                     else "", "roles": ", ".join(letters), "required": "R" in letters,
                     "when": CONDITIONS.get(when.get(pid, ""))}
                    for pid, letters in roles.items()]
    inputs = []
    for name in task.get("inputs") or []:
        if name in artifacts:
            art = artifacts[name].data
            files = [] if art.get("generated") else [f"artifacts/{name}.md"]
            files += [d["path"] for d in current_data(art)]
            inputs.append({"id": name, "name": art.get("name", ""), "kind": "artifact",
                           "files": files})
        elif name in externals:
            ext = externals[name].data
            inputs.append({"id": name, "name": ext.get("name", ""), "kind": ext.get("kind"),
                           "cli": CLI_INPUTS.get(name),
                           "cites": [_command(c) for c in ext.get("citations") or []]})
    outputs = []
    for name in task.get("outputs") or []:
        art = artifacts[name].data if name in artifacts else {}
        generated = bool(art.get("generated"))
        outputs.append({
            "id": name, "name": art.get("name", ""),
            "description": " ".join(str(art.get("description", "")).split()),
            "produces": art.get("producer") == task["id"], "generated": generated,
            "generator": GENERATORS.get(name), "md": None if generated else f"artifacts/{name}.md",
            "template": art.get("template"), "data": _data_files(root, art)})
    aligned = task.get("aligned_with") or {}
    alignment = [{**item, "kind": kind}
                 for kind, coll, key in (("milestone", "milestones", "milestones"),
                                         ("review", "reviews", "reviews"),
                                         ("decision", "decisions", "decisions"))
                 for item in _named(fw, coll, aligned.get(key))]
    step = fw.index("steps").get(task["step"])
    return {
        "task": task,
        "step": {"id": task["step"], "name": step.data.get("name", "") if step else ""},
        "deps": _named(fw, "tasks", task.get("depends_on")),
        "feeds_back": _named(fw, "tasks", task.get("feeds_back_to")),
        "alignment": alignment,
        "interviewees": interviewees,
        "inputs": inputs,
        "outputs": outputs,
        "citations": [{"ref": c["ref"], "where": c.get("section") or f"p. {c.get('page')}",
                       "command": _command(c)} for c in task.get("citations") or []],
    }


def body(fw: Framework, task: dict[str, Any], root: Path) -> str:
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(root / Path(BODY_TEMPLATE).parent),
                             undefined=jinja2.StrictUndefined, keep_trailing_newline=True,
                             trim_blocks=True, lstrip_blocks=True, autoescape=False)
    return env.get_template(Path(BODY_TEMPLATE).name).render(context(fw, task, root))


# --- playbook files ----------------------------------------------------------------------


def slug(heading: str) -> str:
    """The GitHub anchor of a heading (``Task P-1`` -> ``task-p-1``)."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def _headings(text: str, level: int) -> list[tuple[int, str]]:
    """(line number, title) of the ATX headings of exactly ``level``, outside code fences."""
    out, fence = [], False
    prefix = "#" * level + " "
    for i, line in enumerate(text.split("\n")):
        if line.startswith("```"):
            fence = not fence
        elif not fence and line.startswith(prefix):
            out.append((i, line[len(prefix):].strip()))
    return out


def _section(text: str, anchor: str) -> tuple[int, int] | None:
    """Character span of the H2 section whose heading slugs to ``anchor``, after the
    heading line and up to the next H2 heading."""
    lines = text.split("\n")
    heads = _headings(text, 2)
    for k, (i, title) in enumerate(heads):
        if slug(title) == anchor:
            start = min(sum(len(line) + 1 for line in lines[:i + 1]), len(text))
            if k + 1 == len(heads):
                return start, len(text)
            return start, sum(len(line) + 1 for line in lines[:heads[k + 1][0]])
    return None


def _missing_sections(text: str, level: int) -> list[str]:
    titles = [t for _, t in _headings(text, level)]
    missing, pos = [], 0
    for name in SECTIONS:
        if name in titles[pos:]:
            pos = titles.index(name, pos) + 1
        else:
            missing.append(name)
    return missing


def _lacks(task_id: str, missing: list[str], level: int, path: str) -> list[Finding]:
    if not missing:
        return []
    heads = ", ".join(f"{'#' * level} {m}" for m in missing)
    return [Finding(RULE, "E", f"{task_id}: authored body lacks or misorders {heads}", path)]


def _body_kind(text: str) -> str | None:
    """``authored`` or ``generated``: the first body marker on a line of its own."""
    m = _MARKER.search(text)
    return m.group(1) if m else None


def _playbooks(fw: Framework) -> dict[str, list[tuple[dict[str, Any], str]]]:
    """Playbook file -> [(task, anchor)], in task order."""
    out: dict[str, list[tuple[dict[str, Any], str]]] = {}
    for e in fw.of("tasks"):
        playbook = e.data.get("playbook")
        if playbook:
            path, _, anchor = str(playbook).partition("#")
            out.setdefault(path, []).append((e.data, anchor))
    return out


def _single(fw: Framework, root: Path, path: str, task: dict[str, Any], text: str | None
            ) -> tuple[str | None, list[Finding]]:
    head = header(fw, task, path)
    kind = None if text is None else _body_kind(text)
    if text is None or kind == "generated":
        return f"{head}\n{GENERATED}\n{body(fw, task, root)}", []
    if kind is None:
        return None, [Finding(RULE, "E", f"{task['id']}: no body marker ({AUTHORED} or "
                                         f"{GENERATED})", path)]
    block = _block()
    new = block.sub(lambda m: head, text, count=1) if block.search(text) else f"{head}\n{text}"
    authored = new[_MARKER.search(new).end():]  # type: ignore[union-attr]
    return new, _lacks(task["id"], _missing_sections(authored, 2), 2, path)


def _shared(fw: Framework, path: str, tasks: list[tuple[dict[str, Any], str]],
            text: str | None) -> tuple[str | None, list[Finding]]:
    if text is None:
        return None, [Finding(COVERAGE, "E", f"{t['id']}: playbook {path} not found", path)
                      for t, _ in tasks]
    findings = []
    if _body_kind(text) != "authored":
        findings.append(Finding(RULE, "E", f"a shared playbook needs the {AUTHORED} marker",
                                path))
    for task, anchor in tasks:
        span = _section(text, anchor) if anchor else None
        if span is None:
            why = (f"has no section #{anchor} (## Task {task['id']})" if anchor
                   else "is shared, so the playbook field needs a #anchor")
            findings.append(Finding(COVERAGE, "E", f"{task['id']}: {path} {why}", path))
            continue
        start, end = span
        section, head, block = text[start:end], header(fw, task, path, True), _block(task["id"])
        section = (block.sub(lambda m, head=head: head, section, count=1)
                   if block.search(section) else f"{head}\n{section}")
        findings += _lacks(task["id"], _missing_sections(section, 3), 3, path)
        text = text[:start] + section + text[end:]
    return text, findings


def _plan(fw: Framework, root: Path, path: str, tasks: list[tuple[dict[str, Any], str]]
          ) -> tuple[str | None, str | None, list[Finding]]:
    """(current text, synced text, structural findings) for one playbook file."""
    file = root / path
    text = file.read_text(encoding="utf-8") if file.is_file() else None
    if len(tasks) == 1 and not tasks[0][1]:
        return text, *_single(fw, root, path, tasks[0][0], text)
    return text, *_shared(fw, path, tasks, text)


def _framework(root: Path) -> Framework:
    return load(root / FRAMEWORK_DIR, root).framework


def sync(root: Path) -> list[str]:
    fw = _framework(root)
    changed = []
    for path, tasks in _playbooks(fw).items():
        text, new, _ = _plan(fw, root, path, tasks)
        if new is not None and new != text:
            (root / path).parent.mkdir(parents=True, exist_ok=True)
            (root / path).write_text(new, encoding="utf-8")
            changed.append(path)
    return changed


def findings(fw: Framework, root: Path) -> list[Finding]:
    """FW-PB-001 and FW-PB-002 for the playbooks of ``fw`` under ``root``."""
    out = []
    for path, tasks in _playbooks(fw).items():
        text, new, found = _plan(fw, root, path, tasks)
        out += found
        if text is None and new is not None:
            out.append(Finding(COVERAGE, "E", f"{tasks[0][0]['id']}: playbook not found; run "
                                              "`rmf playbooks sync`", path))
        elif text is not None and new is not None and new != text:
            if _body_kind(text) == "generated":
                why = "generated playbook stale or edited by hand"
            elif _block().search(text) or "rmf:header " in text:
                why = "header stale or edited by hand"
            else:
                why = "header missing"
            out.append(Finding(RULE, "E", f"{why}; run `rmf playbooks sync`", path))
    return out


def check(root: Path) -> list[Finding]:
    return findings(_framework(root), root)
