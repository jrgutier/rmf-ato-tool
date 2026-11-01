"""The non-vacuity ladder of FW-REQ-003: what an evidence entry proves.

Each evidence kind has one judge, and each judge returns a verdict. ``strong`` evidence can
carry ``covered``. ``weak`` evidence is real but cannot fail when the requirement is broken,
so it caps at ``partial``. ``denied`` and ``unresolved`` are errors at any status.

Evidence is judged against the entry it sits on and against its target: a rule must list the
entry in its ``enforces``, a schema property in its ``x-enforces`` and a pinned or template
entity in its ``enforces``; a pin must name a field whose value could be wrong; and
``asserts`` must say what the statement says in words the target is also about, so a claim
copied from the statement cannot ride on an unrelated schema field or entity.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rmf_tool.check import Rule, rules_by_id
from rmf_tool.framework.model import SCHEMA_DIR, Framework
from rmf_tool.refs.toc import compact

STRONG, WEAK, DENIED, UNRESOLVED = "strong", "weak", "denied", "unresolved"
EXAMPLES = "examples/"
# They hold for any content, so a pass says nothing about one requirement.
GENERIC_RULES = ("FW-SCHEMA-001", "FW-CITE-", "TRACE-", "RUN-FM-001", "FW-REQ-")
# Fields a pin may assert: each holds a value a wrong framework could get wrong. Identity and
# prose fields are not here, so `id: AD-ATO` proves nothing (see test_conformance_rules).
PINNED_FIELDS = frozenset({
    "decided_by", "decided_in", "produced_by", "updated_by", "owner", "inputs", "outputs",
    "consults", "raci", "class", "phase", "step", "tasks", "requires", "effect",
    "atd_forbidden", "max_term_days", "allowed_pathways", "excluded_product_kinds",
    "required_sections", "entry", "exit", "milestones", "reviews", "applies_to", "depends_on",
    "supersedes", "underlying", "baseline", "overlays", "parameters", "frequency", "cadence",
    "severity", "roles", "approves", "template", "schema", "kind",
})
PROSE_ROOTS = ("playbooks/", "personas/", "templates/", "docs/manual/", "MANUAL.md")
# What an entity says about itself, read when judging whether asserts is about it.
ENTITY_TEXT_FIELDS = ("name", "short", "description", "purpose", "summary", "title")
MIN_SHARED_WORDS = 2  # asserts with the statement
MIN_TARGET_WORDS = 1  # asserts with the target's own text
STEM_LENGTH = 6
SCHEMA_LINK = "x-enforces"
ENTITY_LINK = "enforces"
_STOP = frozenset("""
the and that with this from for are is be been being was were will shall must should may can
not have has had its their there which when where than then into onto upon also each every any
all such other these those within without about above below between through during before after
under over per via only both either neither nor but yet so if whether while until unless
organization organizations system systems information security privacy control controls
""".split())
_WORD = re.compile(r"[a-z][a-z-]{3,}")
_CAMEL = re.compile(r"(?<=[a-z])(?=[A-Z])")


@dataclass(frozen=True)
class Verdict:
    strength: str
    message: str = ""


@dataclass(frozen=True)
class Probe:
    """What a judge can look at."""
    repo: Path
    framework: Framework
    rules: Mapping[str, Rule]


def fixture_exists(repo: Path, fixture: str) -> bool:
    path, _, test = fixture.partition("::")
    target = repo / path
    if not target.exists():
        return False
    return not test or f"def {test}(" in target.read_text(encoding="utf-8")


def content_words(text: str) -> set[str]:
    """Lowercased words of four or more letters, crudely stemmed and cut to six letters, minus
    stop words and the nouns every requirement in this domain shares."""
    out = set()
    for word in _WORD.findall(text.casefold()):
        if word in _STOP:
            continue
        for suffix in ("ations", "ation", "ments", "ment", "ities", "ity", "ings", "ing", "ies",
                       "ers", "er", "ed", "es", "s"):
            if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                word = word[:-len(suffix)]
                break
        out.add(word[:STEM_LENGTH])
    return out


def _words_of_name(name: str) -> str:
    return _CAMEL.sub(" ", name).replace("_", " ").replace("-", " ")


def asserts_verdict(item: Mapping[str, Any], statement: str, target_text: str) -> Verdict | None:
    """``asserts`` must be a sentence that shares vocabulary with the statement it is
    evidence for and with what its target is about; otherwise a copied claim counts for
    anything."""
    asserts = str(item.get("asserts") or "").strip()
    if not asserts:
        return Verdict(WEAK, f"evidence on {item['target']} does not say what it asserts")
    words = content_words(asserts)
    shared = words & content_words(statement)
    if len(shared) < MIN_SHARED_WORDS:
        return Verdict(DENIED, f"asserts on {item['target']} shares {len(shared)} content "
                       f"word(s) with the statement; it must say what the statement says")
    about = words & content_words(target_text)
    if len(about) < MIN_TARGET_WORDS:
        return Verdict(DENIED, f"asserts on {item['target']} shares no content word with what "
                       f"{item['target']} is about ({' '.join(target_text.split()[:12])}...); "
                       "the target does not prove this statement")
    return None


def _linked(links: Any, entry: Mapping[str, Any], target: str, key: str) -> Verdict | None:
    if entry["id"] not in (links or ()):
        return Verdict(DENIED, f"{target} does not list {entry['id']} in {key}")
    return None


def _rule(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    target = item["target"]
    rule = probe.rules.get(target)
    if rule is None:
        return Verdict(UNRESOLVED, f"no rule {target}")
    if target.startswith(GENERIC_RULES):
        return Verdict(DENIED, f"{target} is generic and holds for any content")
    if entry["id"] not in rule.enforces:
        return Verdict(DENIED, f"{target} does not list {entry['id']} in enforces "
                       "(src/rmf_tool/check/registry.yaml)")
    if rule.fixture is None or not fixture_exists(probe.repo, rule.fixture):
        return Verdict(WEAK, f"{target} has no negative fixture")
    if rule.severity == "W":
        return Verdict(WEAK, f"{target} only warns")
    return asserts_verdict(item, entry["statement"], f"{rule.summary} {rule.hint}") \
        or Verdict(STRONG)


def schema_node(repo: Path, target: str) -> tuple[Any, Any, list[str]] | str:
    """The node a ``file#/pointer`` target names, its grandparent, and the pointer tokens; or
    the reason it does not resolve."""
    path, _, pointer = target.partition("#")
    file = repo / path
    if not path.startswith(f"{SCHEMA_DIR}/") or not file.is_file() or not pointer:
        return f"{target}: expected {SCHEMA_DIR}/<file>#/<pointer>"
    tokens = pointer.strip("/").split("/")
    node: Any = json.loads(file.read_text(encoding="utf-8"))
    parent: Any = None
    grandparent: Any = None
    for token in tokens:
        parent, grandparent = node, parent
        if not isinstance(node, Mapping) or token not in node:
            return f"{target}: no {token!r} in the schema"
        node = node[token]
    return node, grandparent, tokens


def _schema(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    target = item["target"]
    found = schema_node(probe.repo, target)
    if isinstance(found, str):
        return Verdict(UNRESOLVED, found)
    node, grandparent, tokens = found
    if len(tokens) < 2 or tokens[-2] != "properties":
        return Verdict(WEAK, f"{target} is not a property, so nothing requires it")
    if tokens[-1] not in (grandparent.get("required") or ()):
        return Verdict(WEAK, f"{target} is optional: its parent does not list it in required")
    denied = _linked(node.get(SCHEMA_LINK), entry, target, SCHEMA_LINK)
    if denied:
        return denied
    about = " ".join([_words_of_name(tokens[-1]), str(node.get("title") or ""),
                      str(node.get("description") or "")])
    return asserts_verdict(item, entry["statement"], about) or Verdict(STRONG)


def _entity(framework: Framework, ident: str) -> Any | None:
    return next((e for e in framework.entities if e.id == ident), None)


def _entity_text(entity: Any, *extra: str) -> str:
    return " ".join([*(str(entity.data.get(k) or "") for k in ENTITY_TEXT_FIELDS), *extra])


def _pinned(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    target, name = item["target"], item.get("field")
    entity = _entity(probe.framework, target)
    if entity is None or not name:
        return Verdict(UNRESOLVED, f"{target}.{name}: no such framework entity field")
    if name.split(".")[0] not in PINNED_FIELDS:
        return Verdict(DENIED, f"{target}.{name} is not a pinnable field (identity or prose); "
                       f"pinnable: {', '.join(sorted(PINNED_FIELDS))}")
    value: Any = entity.data
    for part in name.split("."):
        value = value.get(part) if isinstance(value, Mapping) else None
    if value in (None, "", [], {}) or "value" not in item:
        return Verdict(UNRESOLVED, f"{target}.{name} pins nothing")
    if value != item["value"]:
        return Verdict(UNRESOLVED, f"{target}.{name} is {value!r}, not {item['value']!r}")
    if item["value"] == target:
        return Verdict(DENIED, f"{target}.{name} pins the entity's own ID; that cannot be wrong")
    denied = _linked(entity.data.get(ENTITY_LINK), entry, target, ENTITY_LINK)
    if denied:
        return denied
    about = _entity_text(entity, _words_of_name(name), _words_of_name(json.dumps(value)))
    return asserts_verdict(item, entry["statement"], about) or Verdict(STRONG)


def _template(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    target, heading = item["target"], item.get("heading")
    entity = _entity(probe.framework, target)
    if entity is None or not heading:
        return Verdict(UNRESOLVED, f"{target}: no template or no heading named")
    path = entity.data.get("template")
    if not path:
        return Verdict(UNRESOLVED, f"{target}: no template or no heading named")
    file = probe.repo / path
    lines = file.read_text(encoding="utf-8").splitlines() if file.is_file() else []
    if not any(line.lstrip("#").strip() == heading for line in lines if line.startswith("#")):
        return Verdict(UNRESOLVED, f"{path} has no heading {heading!r}")
    if heading not in (entity.data.get("required_sections") or ()):
        return Verdict(WEAK, f"{heading!r} is not in {target} required_sections, so a run can "
                       "leave it out")
    denied = _linked(entity.data.get(ENTITY_LINK), entry, target, ENTITY_LINK)
    if denied:
        return denied
    return asserts_verdict(item, entry["statement"], _entity_text(entity, heading)) \
        or Verdict(STRONG)


def _citation(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    target = item["target"]
    if _entity(probe.framework, target) is None:
        return Verdict(UNRESOLVED, f"no framework entity {target}")
    return Verdict(WEAK, "a citation proves a passage exists, not that it is met")


def _prose(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    target = item["target"]
    if not target.startswith(PROSE_ROOTS) or not (probe.repo / target).is_file():
        return Verdict(UNRESOLVED, f"{target}: expected a playbook, persona, template or manual "
                       "file")
    return Verdict(WEAK, "prose cannot fail when the requirement is broken")


JUDGES: dict[str, Callable[[Probe, Mapping[str, Any], Mapping[str, Any]], Verdict]] = {
    "rule": _rule,
    "schema": _schema,
    "pinned": _pinned,
    "template": _template,
    "citation": _citation,
    "prose": _prose,
}


def citable(statement: str) -> list[str]:
    """The sentences an evidence item may name: the statement's marked sentences, or the whole
    statement when none of its sentences is marked (a noun-phrase list item, a table row)."""
    from rmf_tool.conformance.extract import marked_sentences

    return marked_sentences(statement) or [statement]


def judge(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    if any(isinstance(v, str) and v.startswith(EXAMPLES) for v in item.values()):
        return Verdict(DENIED, f"{item['target']}: examples/ cannot be evidence; a fork may "
                       "delete it")
    sentence = item.get("sentence")
    if sentence is not None and not any(cites(item, s) for s in citable(entry["statement"])):
        return Verdict(DENIED, f"{item['target']}: sentence {sentence[:40]!r}... is not a whole "
                       "marked sentence of the statement (a fragment or a clause, such as "
                       "'the', would cite every sentence)")
    return JUDGES[item["kind"]](probe, item, entry)


def cites(item: Mapping[str, Any], sentence: str) -> bool:
    """Whether an evidence item's ``sentence`` is this sentence of the statement, whole, up to
    case, spacing and punctuation. Containment either way let `the` cite every sentence."""
    own = compact(item.get("sentence") or "")
    return bool(own) and own == compact(sentence)


def reverse_links(probe: Probe) -> Iterator[tuple[str, str, str]]:
    """Every (kind, target, entry id) a rule, schema property or entity claims to enforce,
    so FW-REQ-003 can demand the entry cites it back."""
    for rule in sorted(probe.rules.values(), key=lambda r: r.id):
        for ident in rule.enforces:
            yield "rule", rule.id, ident
    for file in sorted((probe.repo / SCHEMA_DIR).glob("*.json")):
        yield from _schema_links(f"{SCHEMA_DIR}/{file.name}",
                                 json.loads(file.read_text(encoding="utf-8")), "")
    for entity in probe.framework.entities:
        for ident in entity.data.get(ENTITY_LINK) or () if hasattr(entity.data, "get") else ():
            yield "entity", entity.id, ident


def _schema_links(path: str, node: Any, pointer: str) -> Iterator[tuple[str, str, str]]:
    if isinstance(node, Mapping):
        for ident in node.get(SCHEMA_LINK) or ():
            yield "schema", f"{path}#{pointer}", ident
        for key, child in node.items():
            yield from _schema_links(path, child, f"{pointer}/{key}")
    elif isinstance(node, list):
        for n, child in enumerate(node):
            yield from _schema_links(path, child, f"{pointer}/{n}")


def probe(repo: Path, framework: Framework) -> Probe:
    return Probe(repo, framework, rules_by_id())
