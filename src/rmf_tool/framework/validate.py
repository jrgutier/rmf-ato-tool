"""`rmf validate`: the framework rules FW-* (plan §6.5) under a validation profile.

FW-SCHEMA-001 runs first; when the schema fails, the semantic rules are skipped because
they rely on the validated shape. Rule activation comes from the registry (a rule runs
when its phase is in the profile), and an active rule without an implementation is a
usage error, so a profile can never pass vacuously.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import jsonschema

from rmf_tool import playbooks_sync, refs
from rmf_tool.check import load_registry
from rmf_tool.conformance import evidence as conformance_evidence
from rmf_tool.conformance import register as conformance_register
from rmf_tool.conformance import rules as conformance_rules
from rmf_tool.findings import Finding
from rmf_tool.framework import graph, personas_check
from rmf_tool.framework.citations import DEFERRED, ERROR, Resolver, describe
from rmf_tool.framework.load import Loaded, display_path, load
from rmf_tool.framework.load import _read as read_yaml_rt
from rmf_tool.framework.model import (
    BASELINES_DIR,
    CITING_KINDS,
    COLLECTIONS,
    FRAMEWORK_SCHEMA,
    OPTIONAL_TASKS,
    SCHEMA_DIR,
    TASK_CITATION_REF,
    TASKS_80037,
    Entity,
    Framework,
    Location,
)
from rmf_tool.profiles import Profile, rule_active
from rmf_tool.run.model import schema_errors

FACTS_SCHEMA = f"{SCHEMA_DIR}/facts.schema.json"


class UnimplementedRules(RuntimeError):
    def __init__(self, rules: list[str]) -> None:
        super().__init__("active rule(s) not implemented in this version: " + ", ".join(rules))
        self.rules = rules


@dataclass
class Result:
    findings: list[Finding]
    rules_run: list[str]
    stats: dict[str, int]

    @property
    def ok(self) -> bool:
        return not any(f.severity == "E" for f in self.findings)


@dataclass
class Context:
    fw: Framework
    repo: Path
    resolver: Resolver | None
    deps: dict[str, list[str]] = field(default_factory=dict)
    ancestors: dict[str, frozenset[str]] = field(default_factory=dict)
    deferred: int = 0
    citations: int = 0
    # citing blocks of framework/baselines/*.yaml (not entities: no ID rules apply)
    cited: list[Entity] = field(default_factory=list)
    _register: conformance_register.Register | None = None
    _index: dict[str, Any] | None = None

    @property
    def register(self) -> conformance_register.Register:
        if self._register is None:
            self._register = conformance_register.load(self.repo)
        return self._register

    @property
    def index(self) -> dict[str, Any]:
        if self._index is None:
            self._index = conformance_register.index_entries(self.repo)
        return self._index

    @property
    def whole_framework(self) -> bool:
        """The register and the pin describe the complete task set, not a test subset."""
        return (self.fw.meta.get("task_set") or {}).get("mode") == "exact"


def _err(rule: str, entity: Entity | None, message: str, location: Location | None = None
         ) -> Finding:
    loc = location or (entity.location if entity else None)
    prefix = f"{entity.id}: " if entity is not None and entity.id else ""
    return Finding(rule, "E", prefix + message, loc.file if loc else None,
                   loc.line if loc else None)


def _values(data: Any, path: str) -> Iterator[Any]:
    """Values at a dotted path (a ``[]`` suffix marks a list). Lists are iterated and a
    scalar is yielded as is, so raci.A may be a string or a list."""
    head, _, rest = path.partition(".")
    node = data.get(head.removesuffix("[]")) if hasattr(data, "get") else None
    if node is None:
        return
    for item in node if isinstance(node, list) else [node]:
        if rest:
            yield from _values(item, rest)
        else:
            yield item


# kind -> (field path, target kinds); FW-REF-001
REFERENCES: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "tasks": (
        ("step", ("steps",)),
        ("primary_phase", ("phases",)),
        ("phases[]", ("phases",)),
        ("aligned_with.milestones[]", ("milestones",)),
        ("aligned_with.reviews[]", ("reviews",)),
        ("aligned_with.decisions[]", ("decisions",)),
        ("raci.R[]", ("personas",)),
        ("raci.A", ("personas",)),
        ("raci.C[]", ("personas",)),
        ("raci.I[]", ("personas",)),
        ("inputs[]", ("artifacts", "external_inputs")),
        ("outputs[]", ("artifacts",)),
        ("depends_on[]", ("tasks",)),
        ("feeds_back_to[]", ("tasks",)),
    ),
    "phases": (("entry_milestone", ("milestones",)), ("exit_milestone", ("milestones",))),
    "milestones": (("phase", ("phases",)), ("decision_authority", ("personas",))),
    "reviews": (("phase", ("phases",)),),
    "decisions": (("decided_by", ("personas",)), ("decided_in[]", ("tasks",)),
                  ("phases[]", ("phases",))),
    "artifacts": (("producer", ("tasks",)),),
    "pathways": (("phases[]", ("phases",)),),
}
META_REFERENCES = (("spine_pathway", ("pathways",)),)


def fact_paths(repo: Path) -> set[str]:
    """Writable facts: every object in facts.schema.json that carries ``set_by_task``,
    named by its dotted path (``categorization``, ``categorization.approved``)."""
    schema = json.loads((repo / FACTS_SCHEMA).read_text(encoding="utf-8"))
    defs = schema.get("$defs", {})
    found: set[str] = set()

    def walk(node: dict[str, Any], prefix: str) -> None:
        if "$ref" in node:
            node = defs[node["$ref"].removeprefix("#/$defs/")]
        props = node.get("properties", {})
        if prefix and "set_by_task" in props:
            found.add(prefix)
        for name, sub in props.items():
            if isinstance(sub, dict):
                walk(sub, f"{prefix}.{name}" if prefix else name)

    walk(schema, "")
    return found


# --- rules -------------------------------------------------------------------------------


def rule_id_unique(ctx: Context) -> list[Finding]:
    counts = Counter(e.id for e in ctx.fw.entities if e.id)
    seen: set[str] = set()
    out = []
    for e in ctx.fw.entities:
        if counts[e.id] > 1:
            if e.id in seen:
                out.append(_err("FW-ID-001", e, f"duplicate ID (also a {e.kind[:-1]} "
                                f"elsewhere; {counts[e.id]} definitions)"))
            seen.add(e.id)
    return out


def rule_id_pattern(ctx: Context) -> list[Finding]:
    patterns = {c.kind: c.pattern for c in COLLECTIONS}
    return [_err("FW-ID-002", e, f"ID does not match {patterns[e.kind].pattern} ({e.kind})")
            for e in ctx.fw.entities if not patterns[e.kind].match(e.id)]


def rule_references(ctx: Context) -> list[Finding]:
    out = []
    facts = fact_paths(ctx.repo)
    for e in ctx.fw.entities:
        for path, kinds in REFERENCES.get(e.kind, ()):
            known = ctx.fw.ids(*kinds)
            for value in _values(e.data, path):
                if value not in known:
                    out.append(_err("FW-REF-001", e, f"{path.removesuffix('[]')} references "
                                    f"unknown {'/'.join(kinds)} {value!r}"))
        if e.kind == "tasks":
            for fact in _values(e.data, "writes_facts[]"):
                if fact not in facts:
                    out.append(_err("FW-REF-001", e, f"writes_facts names unknown fact {fact!r} "
                                    f"(known: {', '.join(sorted(facts))})"))
    for path, kinds in META_REFERENCES:
        for value in _values(ctx.fw.meta, path):
            if value not in ctx.fw.ids(*kinds):
                out.append(_err("FW-REF-001", None, f"meta {path} references unknown "
                                f"{'/'.join(kinds)} {value!r}", ctx.fw.meta_location))
    return out


def _listers(fw: Framework) -> dict[str, list[str]]:
    """Artifact -> the tasks that list it in outputs (producer and updaters)."""
    listers: dict[str, list[str]] = {}
    for t in fw.of("tasks"):
        for art in t.data.get("outputs") or []:
            listers.setdefault(art, []).append(t.id)
    return listers


def rule_artifact_producer(ctx: Context) -> list[Finding]:
    listers = _listers(ctx.fw)
    out = []
    for a in ctx.fw.of("artifacts"):
        tasks = listers.get(a.id, [])
        producer = a.data.get("producer")
        if not tasks:
            out.append(_err("FW-ART-001", a, "no task lists this artifact in its outputs"))
        elif producer not in tasks:
            out.append(_err("FW-ART-001", a, f"producer {producer} does not list this artifact "
                            f"in its outputs (listed by {', '.join(tasks)})"))
    return out


def rule_template_sections(ctx: Context) -> list[Finding]:
    """FW-TPL-001: each required section of an artifact is an H2 heading of its template, so
    the heading a run must keep is the one the template hands it."""
    out = []
    for a in ctx.fw.of("artifacts"):
        required = a.data.get("required_sections") or ()
        template = a.data.get("template")
        if required and not template:
            out.append(_err("FW-TPL-001", a, "required_sections names headings, but the "
                            "artifact has no template"))
            continue
        path = ctx.repo / str(template)
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        headings = {line[3:].strip() for line in lines if line.startswith("## ")}
        for heading in required:
            if heading not in headings:
                out.append(_err("FW-TPL-001", a, f"required section {heading!r} is not a "
                                f"heading of {template}"))
    return out


def rule_producer_order(ctx: Context) -> list[Finding]:
    listers = _listers(ctx.fw)
    tasks = ctx.fw.index("tasks")
    out = []
    for a in ctx.fw.of("artifacts"):
        producer = a.data.get("producer")
        if producer not in tasks:
            continue
        for updater in listers.get(a.id, []):
            if updater != producer and producer not in ctx.ancestors.get(updater, ()):
                out.append(_err("FW-ORD-001", a, f"producer {producer} is not a strict ancestor "
                                f"of updater {updater} (add a depends_on path)"))
    return out


def rule_inputs(ctx: Context) -> list[Finding]:
    artifacts = ctx.fw.index("artifacts")
    tasks = ctx.fw.index("tasks")
    out = []
    for t in ctx.fw.of("tasks"):
        for kind, key in (("inputs", "inputs"), ("outputs", "outputs"),
                          ("facts", "writes_facts")):
            since = t.data.get(f"{kind}_since")
            listed = set(t.data.get(key) or [])
            for name in sorted(set(since) - listed) if isinstance(since, dict) else ():
                out.append(_err("FW-IO-001", t, f"{kind}_since names {name}, which is not "
                                f"in {key}"))
        for name in t.data.get("inputs") or []:
            art = artifacts.get(name)
            if art is None:
                continue  # EXT-* inputs are always available; unknown IDs are FW-REF-001's
            producer = art.data.get("producer")
            if producer in tasks and producer not in ctx.ancestors.get(t.id, ()):
                out.append(_err("FW-IO-001", t, f"input {name} is produced by {producer}, "
                                f"which is not a strict ancestor"))
    return out


def rule_raci(ctx: Context) -> list[Finding]:
    out = []
    for t in ctx.fw.of("tasks"):
        raci = t.data.get("raci") or {}
        accountable = raci.get("A")
        count = len(accountable) if isinstance(accountable, list) else int(bool(accountable))
        if count != 1:
            out.append(_err("FW-RACI-001", t, f"raci.A must name exactly one persona "
                            f"(found {count})"))
        if not raci.get("R"):
            out.append(_err("FW-RACI-001", t, "raci.R must name at least one persona"))
        named = {*(raci.get("R") or []), *(raci.get("C") or []),
                 *(accountable if isinstance(accountable, list) else [accountable])}
        for pid in raci.get("when") or {}:
            if pid not in named:
                out.append(_err("FW-RACI-001", t, f"raci.when conditions {pid}, which the task "
                                "does not name in R, A or C"))
    return out


def rule_dag(ctx: Context) -> list[Finding]:
    tasks = ctx.fw.index("tasks")
    return [_err("FW-DAG-001", tasks[c[0]], "depends_on cycle: " + " -> ".join(c))
            for c in graph.cycles(ctx.deps)]


def _citations(e: Entity) -> list[Any]:
    value = e.data.get("citations")
    return value if isinstance(value, list) else []


def rule_cite_present(ctx: Context) -> list[Finding]:
    assert ctx.resolver is not None
    out = []
    for e in [*ctx.fw.entities, *ctx.cited]:
        cites = _citations(e)
        if e.kind in CITING_KINDS and not cites:
            out.append(_err("FW-CITE-001", e, "no citation (cite at least one reference)"))
        for c in cites:
            if not ctx.resolver.known(c.get("ref")):
                out.append(_err("FW-CITE-001", e, f"citation to unknown reference "
                                f"{c.get('ref')!r}"))
    return out


def rule_cite_resolve(ctx: Context) -> list[Finding]:
    assert ctx.resolver is not None
    out = []
    for e in [*ctx.fw.entities, *ctx.cited]:
        for c in _citations(e):
            if not ctx.resolver.known(c.get("ref")):
                continue  # FW-CITE-001
            ctx.citations += 1
            result = ctx.resolver.resolve(c)
            if result.status == DEFERRED:
                ctx.deferred += 1
            elif result.status == ERROR:
                out.append(_err("FW-CITE-002", e, f"{describe(c)}: {result.message}"))
    return out


def rule_cite_required(ctx: Context) -> list[Finding]:
    """FW-CITE-003: a citation to a PDF that is not in the required set. Only required
    references are guaranteed present in every fork, so a citation to any other is unsound."""
    assert ctx.resolver is not None
    out = []
    for e in [*ctx.fw.entities, *ctx.cited]:
        for ref in dict.fromkeys(c.get("ref") for c in _citations(e)):
            entry = ctx.resolver.entry(ref)
            if entry is not None and entry["kind"] == "pdf" and not entry["required"]:
                out.append(_err("FW-CITE-003", e, f"cites {ref}, a PDF marked required: false; "
                                "mark it required (after import) or drop the citation"))
    return out + personas_check.optional_pdf_citations(ctx.fw, ctx.repo, ctx.resolver)


def _norm(name: str) -> str:
    return re.sub(r"\s*[-–—]\s*", "-", " ".join(name.split())).casefold()


def rule_task_set(ctx: Context) -> list[Finding]:
    out = []
    tasks = ctx.fw.index("tasks")
    task_set = ctx.fw.meta.get("task_set") or {}
    if task_set.get("mode") == "exact":
        missing = [t for t in TASKS_80037 if t not in tasks]
        if missing:
            out.append(_err("FW-TASK-001", None, f"task set is exact but {len(missing)} "
                            f"SP 800-37r2 task(s) are missing: {', '.join(missing)}",
                            ctx.fw.meta_location))
    for t in ctx.fw.of("tasks"):
        canonical = TASKS_80037.get(t.id)
        if canonical is None:
            out.append(_err("FW-TASK-001", t, "not an SP 800-37r2 task"))
            continue
        if _norm(str(t.data.get("name", ""))) != _norm(canonical):
            out.append(_err("FW-TASK-001", t, f"name {t.data.get('name')!r} differs from its "
                            f"SP 800-37r2 task name {canonical!r}"))
        if t.data.get("step") != t.id.split("-")[0]:
            out.append(_err("FW-TASK-001", t, f"step {t.data.get('step')} differs from its "
                            f"SP 800-37r2 step {t.id.split('-')[0]}"))
        org_level = t.id in {f"P-{n}" for n in range(1, 8)}
        if t.data.get("level") != ("organization" if org_level else "system"):
            out.append(_err("FW-TASK-001", t, "level must be "
                            f"{'organization' if org_level else 'system'}"))
        if bool(t.data.get("optional")) != (t.id in OPTIONAL_TASKS):
            out.append(_err("FW-TASK-001", t, f"optional must be {t.id in OPTIONAL_TASKS}"))
        wanted = f"TASK {t.id}"
        if not any(c.get("ref") == TASK_CITATION_REF and c.get("section") == wanted
                   for c in _citations(t)):
            out.append(_err("FW-TASK-001", t, f"must cite {{ref: {TASK_CITATION_REF}, "
                            f"section: {wanted!r}}}"))
    return out


def rule_task_contract(ctx: Context) -> list[Finding]:
    if not ctx.whole_framework:
        return []
    return conformance_rules.contract(ctx.repo, ctx.fw, ctx.register)


def rule_req_shape(ctx: Context) -> list[Finding]:
    assert ctx.resolver is not None
    if not ctx.whole_framework:
        return []
    return conformance_rules.shape(ctx.register, ctx.resolver, ctx.repo, ctx.index)


def rule_req_freeze(ctx: Context) -> list[Finding]:
    if not ctx.whole_framework:
        return []
    return conformance_rules.freeze(ctx.register, ctx.index,
                                    conformance_evidence.probe(ctx.repo, ctx.fw))


def rule_req_ladder(ctx: Context) -> list[Finding]:
    if not ctx.whole_framework:
        return []
    return conformance_rules.ladder(ctx.register, conformance_evidence.probe(ctx.repo, ctx.fw))


def rule_req_reasons(ctx: Context) -> list[Finding]:
    if not ctx.whole_framework:
        return []
    return conformance_rules.reasons(ctx.register, ctx.index,
                                     conformance_evidence.probe(ctx.repo, ctx.fw))


def rule_req_sync(ctx: Context) -> list[Finding]:
    return conformance_rules.sync(ctx.repo, ctx.register, ctx.index) \
        if ctx.whole_framework else []


def rule_persona_cards(ctx: Context) -> list[Finding]:
    return personas_check.missing_cards(ctx.fw, ctx.repo)


def rule_persona_card_content(ctx: Context) -> list[Finding]:
    assert ctx.resolver is not None
    return personas_check.card_problems(ctx.fw, ctx.repo, ctx.resolver)


def rule_playbook_coverage(ctx: Context) -> list[Finding]:
    return [f for f in playbooks_sync.findings(ctx.fw, ctx.repo) if f.rule == "FW-PB-001"]


def rule_playbook_sync(ctx: Context) -> list[Finding]:
    return [f for f in playbooks_sync.findings(ctx.fw, ctx.repo) if f.rule == "FW-PB-002"]


RULES: dict[str, Callable[[Context], list[Finding]]] = {
    "FW-ID-001": rule_id_unique,
    "FW-ID-002": rule_id_pattern,
    "FW-REF-001": rule_references,
    "FW-ART-001": rule_artifact_producer,
    "FW-TPL-001": rule_template_sections,
    "FW-ORD-001": rule_producer_order,
    "FW-IO-001": rule_inputs,
    "FW-RACI-001": rule_raci,
    "FW-DAG-001": rule_dag,
    "FW-CITE-001": rule_cite_present,
    "FW-CITE-002": rule_cite_resolve,
    "FW-CITE-003": rule_cite_required,
    "FW-TASK-001": rule_task_set,
    "FW-TASK-002": rule_task_contract,
    "FW-REQ-001": rule_req_shape,
    "FW-REQ-002": rule_req_freeze,
    "FW-REQ-003": rule_req_ladder,
    "FW-REQ-004": rule_req_reasons,
    "FW-REQ-005": rule_req_sync,
    "FW-PER-001": rule_persona_cards,
    "FW-PER-002": rule_persona_card_content,
    "FW-PB-001": rule_playbook_coverage,
    "FW-PB-002": rule_playbook_sync,
}
IMPLEMENTED = ("FW-SCHEMA-001", *RULES)
# FW-* rules that another command enforces (each has its own rmf ci step), not rmf validate.
CHECKED_ELSEWHERE = {"FW-MAN-001": "rmf render --check"}


# --- driver ------------------------------------------------------------------------------


def active_rules(profile: Profile) -> list[str]:
    """Registry rules of the framework family (FW-*) whose phase is in the profile, less
    those checked by another command."""
    return [r.id for r in load_registry()
            if r.id.startswith("FW-") and r.id not in CHECKED_ELSEWHERE
            and rule_active(r.phase, profile)]


def schema_findings(loaded: Loaded, repo: Path) -> list[Finding]:
    schema = json.loads((repo / FRAMEWORK_SCHEMA).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    out = []
    for err in sorted(validator.iter_errors(loaded.document),
                      key=lambda e: [str(p) for p in e.absolute_path]):
        path = list(err.absolute_path)
        loc = loaded.framework.meta_location
        label = ""
        if len(path) >= 2 and (path[0], path[1]) in loaded.origins:
            loc = loaded.origins[(path[0], path[1])]
            item = loaded.document[path[0]][path[1]]
            ident = item.get("id") if hasattr(item, "get") else None
            label = f"{ident}: " if isinstance(ident, str) else ""
            path = path[2:]
        where = "/".join(map(str, path)) or "(entry)"
        out.append(Finding("FW-SCHEMA-001", "E", f"{label}{where}: {err.message}", loc.file,
                           loc.line))
    return out


TAILORING_INPUTS = "tailoring-inputs.yaml"  # what S-2 tests a system against (TLR-003, TLR-005)
OVERLAY_SPECS = "overlay-specs.yaml"  # overlay Section 6 per control (OVS-001 to OVS-003)
PRIVACY_CONSIDERATIONS = "privacy-considerations.yaml"  # the column PIC-001 reads
NSS_PARAMETERS = "cnssi-1253-parameters.yaml"  # Appendix D Parameter Value column (WI-20)


def baseline_tables(fw_root: Path, repo: Path) -> tuple[list[Finding], list[Entity]]:
    """``baselines/*.yaml`` under the framework root (CNSSI 1253 tables, ADR-0002): schema
    errors as FW-SCHEMA-001 findings, and each citing block (the file, every table block and
    every overlay block) as a pseudo-entity for the FW-CITE rules. ``*.overrides.yaml`` files
    are generator input, not tables; ``tailoring-inputs.yaml`` has its own schema, and each of
    its assumptions and overlay conditions is a citing block."""
    findings: list[Finding] = []
    cited: list[Entity] = []
    for path in sorted((fw_root / BASELINES_DIR).glob("*.yaml")):
        if path.name.endswith(".overrides.yaml"):
            continue
        shown = display_path(path, repo)
        data = read_yaml_rt(path, shown, findings)
        if data is None:
            continue
        inputs = path.name == TAILORING_INPUTS
        specs = path.name == OVERLAY_SPECS
        pic = path.name == PRIVACY_CONSIDERATIONS
        params = path.name == NSS_PARAMETERS
        name = ("tailoring-inputs" if inputs else "overlay-specs" if specs
                else "privacy-considerations" if pic else path.stem if params else "baselines")
        errors = schema_errors(repo, name, data)
        findings += [Finding("FW-SCHEMA-001", "E", e, shown) for e in errors]
        if errors:
            continue
        if params:
            cited.append(Entity("baselines", {"id": path.stem, "citations": [data["citation"]]},
                                Location(shown, 1)))
            cited += [Entity("baselines", {"id": f"{path.stem} {c['control']}",
                                           "citations": [c["citation"]]},
                             Location(shown, c.lc.line + 1)) for c in data["controls"]]
            continue
        if specs:
            cited += [Entity("baselines", {"id": f"{o['overlay']} {s['control']}",
                                           "citations": [s["citation"]]},
                             Location(shown, s.lc.line + 1))
                      for o in data["overlays"] for s in o["specs"]]
            continue
        if pic:
            cited += [Entity("baselines", {"id": f"{path.stem} {d['ref']}",
                                           "citations": [d["citation"]]},
                             Location(shown, d.lc.line + 1)) for d in data["documents"]]
            cited += [Entity("baselines", {"id": f"{path.stem} {d['ref']} block",
                                           "citations": [b["citation"]]},
                             Location(shown, b.lc.line + 1))
                      for d in data["documents"] for b in d["blocks"]]
            continue
        if inputs:
            cited += [Entity("baselines", {"id": f"{path.stem} {i['id']}",
                                           "citations": [i["citation"]]},
                             Location(shown, i.lc.line + 1))
                      for i in [*data["assumptions"], *data["overlay_conditions"],
                                *data.get("policy_controls", []),
                                *data.get("dod_policy_controls", [])]]
            continue
        cited.append(Entity("baselines", {"id": data["baseline"],
                                          "citations": data["citations"]},
                            Location(shown, 1)))
        blocks = [(f"{data['baseline']} table {t['table']}", b) for t in data["tables"]
                  for b in t["blocks"]]
        blocks += [(f"overlay {o['id']}", b) for o in data["overlays"]
                   for b in [*(o.get("blocks") or []), *([o["unlisted"]] if "unlisted" in o
                                                          else [])]]
        cited += [Entity("baselines", {"id": label, "citations": [b["citation"]]},
                         Location(shown, b.lc.line + 1)) for label, b in blocks]
    return findings, cited


def validate(fw_root: Path, repo: Path, profile: Profile) -> Result:
    """Run the active FW-* rules on the framework at ``fw_root``. References, schemas and
    the facts schema always come from ``repo``. Raises UnimplementedRules, and
    refs.IndexFileError when citations cannot be checked."""
    rules = active_rules(profile)
    missing = [r for r in rules if r not in IMPLEMENTED]
    if missing:
        raise UnimplementedRules(missing)
    loaded = load(fw_root, repo)
    stats = loaded.framework.counts()
    findings: list[Finding] = []
    if not rules:
        return Result(findings, rules, {**stats, "citations": 0, "deferred_citations": 0})
    findings += loaded.findings + schema_findings(loaded, repo)
    table_findings, cited = baseline_tables(fw_root, repo)
    findings += table_findings
    resolver = None
    if any(r.startswith(("FW-CITE-", "FW-PER-", "FW-REQ-")) for r in rules):
        resolver = Resolver(repo, refs.load_index(repo), strict=profile.includes("p2x"))
    ctx = Context(loaded.framework, repo, resolver, cited=cited)
    if not findings:
        ctx.deps = graph.dependency_graph(ctx.fw)
        ctx.ancestors = graph.ancestors(ctx.deps)
        for rule in rules:
            if rule in RULES:
                findings += RULES[rule](ctx)
    stats.update(citations=ctx.citations, deferred_citations=ctx.deferred)
    return Result(findings, rules, stats)
