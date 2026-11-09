"""The non-vacuity ladder of FW-REQ-003: what an evidence entry proves.

Each evidence kind has one judge, and each judge returns a verdict. ``strong`` evidence can
carry ``covered``. ``weak`` evidence is real but cannot fail when the requirement is broken,
so it caps at ``partial``. ``denied`` and ``unresolved`` are errors at any status.

Evidence is judged against the entry it sits on and against its target: a rule must list the
entry in its ``enforces``, a schema property in its ``x-enforces`` and a pinned or template
entity in its ``enforces``; a pin must name a field whose value could be wrong; and
``asserts`` must say what the statement says in words the target is also about, so a claim
copied from the statement cannot ride on an unrelated schema field or entity.

``covered`` means a real test fails if the duty is broken, so (ADR-0005, 2026-11-02):

- a rule item names its negative fixture and a literal fragment of the failing message; the
  fixture must be the rule's own, list it in ``errors`` and declare that message, and the
  fragment must be in one failing message of the rule's source, with two content words or as a
  whole declared message. The negative-fixture test proves the fixture fails, so this judge
  stays static;
- a pin counts only beside a rule item that reads the same field (``read_by``);
- a schema property is held only if every property above it is required, or a rule makes the
  parent present (``read_by``);
- a field a decision type lists in ``requires`` is held by the triple pin, rule clause and
  schema shape, each strong on the same sentence, and by nothing less. The field comes from the
  fixture and the clause, never from the fragment an author chose;
- ``claim: presence`` caps at partial on prose; the judge classifies schema and rule items
  itself. A fixture that only deletes, or a clause that only tests absence, is presence;
- a rule that stays quiet unless an artifact is in play carries ``holds_when``.

A repo-scope rule (FW-*) is judged the same way, on a framework overlay under
``tests/fixtures/framework_neg/`` whose ``expect.yaml`` declares its messages (ADR-0005,
2026-11-08); an overlay has no mutations, so its claim comes from the clause alone.
"""

from __future__ import annotations

import ast
import inspect
import json
import re
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import Any

from rmf_tool.check import Rule, rules_by_id
from rmf_tool.framework.model import SCHEMA_DIR, Framework
from rmf_tool.refs.toc import compact
from rmf_tool.run.authorization import LEDGER_FILE
from rmf_tool.run.model import YamlError, read_yaml

STRONG, WEAK, DENIED, UNRESOLVED = "strong", "weak", "denied", "unresolved"
EXAMPLES = "examples/"
# They hold for any content, so a pass says nothing about one requirement. GEN-STALE-001 fails any
# edit to any generated file, so its message never names the element a requirement asks for.
GENERIC_RULES = ("FW-SCHEMA-001", "FW-CITE-", "TRACE-", "RUN-FM-001", "FW-REQ-", "FW-ID-",
                 "GEN-STALE-001")
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
PRESENCE, CONSTRAINT = "presence", "constraint"
TABLE_KIND = "table"  # an entry that names a field: presence of the field is the duty
# Schema keywords that refuse a wrong value; a bare string with minLength only refuses silence.
CONSTRAINT_KEYWORDS = ("enum", "const", "pattern", "format", "minimum", "maximum",
                       "exclusiveMinimum", "exclusiveMaximum", "minItems")
# What a clause reads when it tests that a value is absent; `not status.reached(...)` is no such
# read, it refuses a state of the run.
ABSENCE_READS = ("get", "strip", "isinstance", "any")
DELETE_FIELD, SET_FIELD = "delete_field", "set_field"
DELETE_FILE, REPLACE_TEXT = "delete_file", "replace_text"
MIN_EXPECT_WORDS = 2
NEGATIVE_FIXTURES = "tests/fixtures/negative/"
# A repo-scope rule's negative fixture: an overlay on tests/fixtures/framework_mini that
# test_framework_negative composes and validates, proving each message its expect.yaml declares.
FRAMEWORK_FIXTURES = "tests/fixtures/framework_neg/"
FRAMEWORK_EXPECT = "expect.yaml"
QUIET_UNLESS_IN_PLAY = "produced_or_seeded"  # a rule calling it returns [] for an absent artifact
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
_CALL = re.compile(r"\b(_?[a-z]\w*)\(")
_QUALIFIED_CALL = re.compile(r"\b([a-z_]\w*)\.(_?[a-z]\w*)\(")
_ADJACENT = re.compile(r"\"\s*\n\s*f?\"")


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
    sources: Mapping[str, str] = field(default_factory=dict)  # rule ID -> its source text

    @property
    def requires_fields(self) -> frozenset[str]:
        """Record fields some decision type requires."""
        return frozenset(f for e in self.framework.entities
                         if e.id.startswith("AD-") for f in e.data.get("requires") or ())


def fixture_exists(repo: Path, fixture: str) -> bool:
    path, _, test = fixture.partition("::")
    target = repo / path
    if not target.exists():
        return False
    return not test or f"def {test}(" in target.read_text(encoding="utf-8")


def fixture_spec(repo: Path, fixture: str) -> Mapping[str, Any] | None:
    """A negative fixture's spec, or None when ``fixture`` is not one. A framework overlay's
    ``expect.yaml`` is read as one: every rule it fires (``rule`` and ``also``) is an error, and
    it has no mutations."""
    if fixture.startswith(FRAMEWORK_FIXTURES):
        return _framework_spec(repo, fixture.rstrip("/"))
    if not fixture.startswith(NEGATIVE_FIXTURES):
        return None
    try:
        spec = read_yaml(repo / fixture)
    except YamlError:
        return None
    return spec if isinstance(spec, Mapping) else None


def _framework_spec(repo: Path, overlay: str) -> Mapping[str, Any] | None:
    try:
        spec = read_yaml(repo / overlay / FRAMEWORK_EXPECT)
    except (YamlError, OSError):
        return None
    if not isinstance(spec, Mapping):
        return None
    return {"rule": spec.get("rule"),
            "expect": {"errors": [spec.get("rule"), *(spec.get("also") or ())],
                       "messages": list(spec.get("messages") or ())}}


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
    spoken = content_words(statement)
    shared = words & spoken
    if len(shared) < min(MIN_SHARED_WORDS, len(spoken)):
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


def _spec_problem(repo: Path, rule: str, item: Mapping[str, Any]) -> Verdict | None:
    """The fixture exists, fails on the rule itself, and declares the message ``expect`` names.
    An ``also`` rule fires beside the clause under test, so nothing proves its message."""
    fixture, expect = item["fixture"], item["expect"]
    spec = fixture_spec(repo, fixture)
    if spec is None:
        return Verdict(UNRESOLVED, f"{rule}: {fixture} is no negative fixture under "
                       f"{NEGATIVE_FIXTURES} or {FRAMEWORK_FIXTURES}")
    outcome = spec.get("expect") or {}
    if spec.get("rule") != rule or rule not in (outcome.get("errors") or ()):
        return Verdict(DENIED, f"{fixture} does not expect {rule} as its rule, in expect.errors")
    messages = outcome.get("messages") or ()
    if not any(expect in message for message in messages):
        return Verdict(DENIED, f"{fixture} does not declare the message {expect!r} in "
                       "expect.messages, so nothing proves it fails with it")
    if len(content_words(expect)) < MIN_EXPECT_WORDS and expect not in messages:
        return Verdict(DENIED, f"{rule}: expect {expect!r} needs {MIN_EXPECT_WORDS} content words "
                       "or one declared message whole, or it fits any clause")
    return None


@cache
def _parsed(source: str) -> ast.Module:
    return ast.parse(source)


def failing_clauses(source: str, expect: str) -> list[list[ast.expr]]:
    """For each call of a rule whose message holds ``expect``, the tests that lead to it. An
    ``else`` branch adds its test negated: it runs when that test fails."""
    def visit(node: ast.AST, tests: list[ast.expr]) -> Iterator[list[ast.expr]]:
        if isinstance(node, ast.If):
            for child in node.body:
                yield from visit(child, [*tests, node.test])
            for child in node.orelse:
                yield from visit(child, [*tests, ast.UnaryOp(ast.Not(), node.test)])
        elif isinstance(node, ast.Call) and any(
                isinstance(n, ast.Constant) and isinstance(n.value, str) and expect in n.value
                for n in ast.walk(node)):
            yield tests
        else:
            for child in ast.iter_child_nodes(node):
                yield from visit(child, tests)

    return list(visit(_parsed(source), []))


def _reads_field(node: ast.expr, plain: frozenset[str]) -> bool:
    """Whether ``node`` is a plain read of a named field. ``kinds.get(r.get("decision"))`` is a
    lookup: finding nothing there refuses a wrong value, not silence."""
    if isinstance(node, ast.Name):
        return node.id in plain
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
        return _reads_field(node.values[0], plain)  # r.get("x") or []
    if not isinstance(node, ast.Call) or not node.args:
        return False
    if isinstance(node.func, ast.Name) and node.func.id == "len":
        return _reads_field(node.args[0], plain)
    first = node.args[0]
    return isinstance(node.func, ast.Attribute) and node.func.attr == "get" \
        and isinstance(first, ast.Constant) and isinstance(first.value, str)


def _plain_reads(source: str) -> frozenset[str]:
    """Names only ever bound to a plain read of a field."""
    plain: set[str] = set()
    other: set[str] = set()
    for node in ast.walk(_parsed(source)):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            pairs: Iterable[tuple[ast.expr, ast.expr]] = [(target, node.value)]
            if isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple):
                pairs = zip(target.elts, node.value.elts, strict=False)
            for name, value in pairs:
                if isinstance(name, ast.Name):
                    (plain if _reads_field(value, frozenset()) else other).add(name.id)
    return frozenset(plain - other)


def _is_empty(node: ast.expr) -> bool:
    if isinstance(node, ast.Constant):
        return node.value is None or node.value in ("", 0)
    if isinstance(node, ast.Dict):
        return not node.keys
    return isinstance(node, ast.List | ast.Tuple | ast.Set) and not node.elts


def _compares_empty(test: ast.Compare, plain: frozenset[str], negated: bool) -> bool:
    if len(test.ops) != 1:
        return False
    op, left, right = test.ops[0], test.left, test.comparators[0]
    if isinstance(op, ast.In | ast.NotIn):
        subject, positive = left, isinstance(op, ast.In)
        empties = isinstance(right, ast.List | ast.Tuple | ast.Set) and right.elts \
            and all(_is_empty(e) for e in right.elts)
        held = bool(empties)
    elif isinstance(op, ast.Is | ast.Eq | ast.IsNot | ast.NotEq):
        subject, positive = (left if _is_empty(right) else right), isinstance(op, ast.Is | ast.Eq)
        held = _is_empty(left) or _is_empty(right)
    else:
        return False
    return held and _reads_field(subject, plain) and positive != negated


def _tests_absence(test: ast.expr, plain: frozenset[str], negated: bool = False) -> bool:
    """Whether a failing path through ``test`` means the value is absent, however it is spelt.
    A negated bare name is absence only when the name is a plain read of a field: in
    ``critical and p > q and not driver`` the loop's ``driver`` is no field read, so the clause
    refuses a wrong ``p``."""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return _tests_absence(test.operand, plain, not negated)
    if isinstance(test, ast.BoolOp):
        found = [_tests_absence(value, plain, negated) for value in test.values]
        return any(found) if isinstance(test.op, ast.And) != negated else all(found)
    if isinstance(test, ast.Compare):
        return _compares_empty(test, plain, negated)
    if not negated:
        return False
    if isinstance(test, ast.Call):
        callee = test.func
        name = callee.attr if isinstance(callee, ast.Attribute) else getattr(callee, "id", "")
        if name == "any" and isinstance(callee, ast.Name):
            # `not any(r.get("x") or [])` reads silence; `not any(... for ...)` over a computed
            # iterable asks whether a member matches, a comparison, as len() is in _reads_field.
            return bool(test.args) and _reads_field(test.args[0], plain)
        return name in ABSENCE_READS
    return isinstance(test, ast.Name) and test.id in plain


def _deletes(mutation: Mapping[str, Any]) -> bool:
    """A mutation that removes a value: a deleted field or file, a set to an empty value
    (``[]``, ``{}``, ``""`` or null), or a text replacement that only erases lines (a key with
    its value), which a rule refuses for the same silence. A list item deleted is not seen here:
    it leaves a set without that member, the list ``set_field`` to the remainder writes, a wrong
    value; the fixture that empties a list writes it as ``set_field: []`` (test_negative holds
    that)."""
    op = mutation["op"]
    if op in (DELETE_FIELD, DELETE_FILE):
        return True
    if op == SET_FIELD:
        return mutation.get("value") in (None, "", [], {})
    if op == REPLACE_TEXT:
        old = str(mutation.get("old") or "").splitlines()
        new = [line for line in str(mutation.get("new") or "").splitlines() if line.strip()]
        return all(line in old for line in new) and len(new) < len([o for o in old if o.strip()])
    return False


def rule_claim(spec: Mapping[str, Any], source: str, expect: str) -> str:
    """What a rule item can refuse, read from its fixture and clause: a fixture that only deletes
    and a clause that only tests absence refuse silence, not a wrong value. With no clause to
    read, nothing shows a wrong value is refused."""
    mutations = spec.get("mutations") or ()
    if mutations and all(_deletes(m) for m in mutations):
        return PRESENCE
    clauses = failing_clauses(source, expect)
    plain = _plain_reads(source)
    tested = any(_tests_absence(test, plain) for tests in clauses for test in tests)
    return PRESENCE if tested or not clauses else CONSTRAINT


def _rule_fields(probe: Probe, item: Mapping[str, Any]) -> frozenset[str]:
    """The ``requires`` fields a rule item's fixture breaks: a mutated path, a declared message
    naming one, or a field the clause's own tests read. Never the fragment the author chose,
    which can leave the name out. A ``requires`` field lives on a ledger record, so a fixture
    that leaves the ledger alone breaks none, whatever its fields are called (a SAP's
    ``assessor_independence.review`` is not the cATO ``review``)."""
    expect = item.get("expect")
    spec = fixture_spec(probe.repo, item.get("fixture") or "")
    if spec is None or not expect:
        return frozenset()
    on_ledger = [m for m in spec.get("mutations") or () if m.get("file") == LEDGER_FILE]
    if not on_ledger:
        return frozenset()
    fields = probe.requires_fields
    source = probe.sources.get(item["target"], "")
    named = {m["path"].rpartition(".")[2] for m in on_ledger
             if m["op"] in (DELETE_FIELD, SET_FIELD)}
    named |= {n.value for tests in failing_clauses(source, expect)
              for test in tests for n in ast.walk(test)
              if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    declared = [m for m in (spec.get("expect") or {}).get("messages") or () if expect in m]
    worded = _wording(source)
    # A declared message names a field the rule reads, or one it put there; the rule's own
    # wording ("assessors review ...") names none.
    return frozenset(f for f in fields if f in named or (
        (f'"{f}"' in source or not re.search(rf"\b{f}\b", worded))
        and any(re.search(rf"\b{f}\b", m) for m in declared)))


def _wording(source: str) -> str:
    """The rule's own message wording: a word there is the rule's prose, not a field it put in
    the message, so "assessors review" names no `review`. A bare ``"review"`` is a read.
    Limit: a rule that reads a field through a variable and reuses the field's word in its
    prose drops it from this route; only a fixture mutating that field then still names it."""
    return " ".join(n.value for n in ast.walk(_parsed(source))
                    if isinstance(n, ast.Constant) and isinstance(n.value, str) and " " in n.value)


def _same_sentence(one: Mapping[str, Any], other: Mapping[str, Any],
                   entry: Mapping[str, Any]) -> bool:
    if len(citable(entry["statement"])) < 2:
        return True
    return one.get("sentence") is not None and one.get("sentence") == other.get("sentence")


def _paired_rules(item: Mapping[str, Any], entry: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """The rule items of this entry a pin or schema item leans on through ``read_by``."""
    return [other for other in entry.get("evidence") or ()
            if other["kind"] == "rule" and other["target"] == item.get("read_by")
            and _same_sentence(item, other, entry)]


def _rule_item_in_entry(probe: Probe, read_by: str | None, name: str,
                        item: Mapping[str, Any], entry: Mapping[str, Any]) -> bool:
    """A strong rule item of this entry, on the same sentence, whose rule reads ``name``."""
    if not read_by or f'"{name}"' not in probe.sources.get(read_by, ""):
        return False
    return any(_verdict(probe, other, entry).strength == STRONG
               for other in _paired_rules(item, entry))


def _held_fields(probe: Probe, item: Mapping[str, Any],
                 entry: Mapping[str, Any]) -> frozenset[str]:
    """The ``requires`` fields a strong item speaks for, directly or through its rule item."""
    if item["kind"] == "rule":
        return _rule_fields(probe, item)
    if item["kind"] not in ("pinned", "schema"):
        return frozenset()
    held = frozenset(f for rule in _paired_rules(item, entry) for f in _rule_fields(probe, rule))
    if item["kind"] == "schema":
        tokens = item["target"].partition("#")[2].split("/")
        own = tokens[tokens.index("properties") + 1]
        return held | ({own} & probe.requires_fields)
    return held


def _triple_missing(probe: Probe, name: str, item: Mapping[str, Any],
                    entry: Mapping[str, Any]) -> str | None:
    """What ``item``'s sentence lacks of pin, rule clause and schema shape for a ``requires``
    field. Each leg must judge strong there, so a leg is judged without the triple itself."""
    legs = [i for i in entry.get("evidence") or () if _same_sentence(i, item, entry)
            and _verdict(probe, i, entry).strength == STRONG]
    if not any(i["kind"] == "pinned" and i.get("field") == "requires"
               and name in (i.get("value") or ()) for i in legs):
        return "the pin on requires"
    if not any(i["kind"] == "rule" and name in _rule_fields(probe, i) for i in legs):
        return "the rule clause"
    if not any(i["kind"] == "schema" and f"/properties/{name}" in i["target"] for i in legs):
        return "the schema shape"
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
    if not item.get("fixture") or not item.get("expect"):
        return Verdict(WEAK, f"{target}: the item names no fixture and expected message, so "
                       "nothing ties the claim to a clause of the rule")
    if problem := _spec_problem(probe.repo, target, item):
        return problem
    source = probe.sources.get(target, "")
    clauses = failing_clauses(source, item["expect"])
    if not clauses:
        return Verdict(DENIED, f"{target}: {item['expect']!r} is not literal in a failing message "
                       "in the rule's source")
    if rule.severity == "W":
        return Verdict(WEAK, f"{target} only warns")
    if QUIET_UNLESS_IN_PLAY in source and not item.get("holds_when"):
        return Verdict(WEAK, f"{target} stays quiet unless its artifact is in play: record "
                       "holds_when")
    spec = fixture_spec(probe.repo, item["fixture"]) or {}
    claim = rule_claim(spec, source, item["expect"])
    if item.get("claim") != claim:
        return Verdict(DENIED, f"{item['fixture']} is {claim} by its fixture and clause, not "
                       f"{item.get('claim')}")
    return asserts_verdict(item, entry["statement"], item["expect"]) or Verdict(STRONG)


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


def schema_claim(repo: Path, target: str) -> str:
    """What a schema property can refuse, read from the schema itself."""
    path = target.partition("#")[0]
    root = json.loads((repo / path).read_text(encoding="utf-8"))
    node: Any = schema_node(repo, target)[0]
    while "$ref" in node:
        node = root["$defs"][node["$ref"].rpartition("/")[2]]
    return CONSTRAINT if any(k in node for k in CONSTRAINT_KEYWORDS) else PRESENCE


def _optional_parents(repo: Path, target: str) -> list[str]:
    """Properties on the way to ``target``, itself included, that their parent leaves optional."""
    path, _, pointer = target.partition("#")
    tokens = pointer.strip("/").split("/")
    node: Any = json.loads((repo / path).read_text(encoding="utf-8"))
    optional = []
    parent: Any = {}
    for n, token in enumerate(tokens):
        if n > 0 and tokens[n - 1] == "properties" and token not in (parent.get("required") or ()):
            optional.append(token)
        if token == "properties":
            parent = node
        node = node[token]
    return optional


def _schema(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    target = item["target"]
    found = schema_node(probe.repo, target)
    if isinstance(found, str):
        return Verdict(UNRESOLVED, found)
    node, _, tokens = found
    if len(tokens) < 2 or tokens[-2] != "properties":
        return Verdict(WEAK, f"{target} is not a property, so nothing requires it")
    for name in _optional_parents(probe.repo, target):
        if not _rule_item_in_entry(probe, item.get("read_by"), name, item, entry):
            return Verdict(WEAK, f"{target} is optional at {name}: its parent does not list it "
                           "in required and no rule item of this entry makes it present")
    denied = _linked(node.get(SCHEMA_LINK), entry, target, SCHEMA_LINK)
    if denied:
        return denied
    claim = schema_claim(probe.repo, target)
    if item.get("claim") != claim:
        return Verdict(DENIED, f"{target} is {claim} by its schema, not {item.get('claim')}")
    return asserts_verdict(item, entry["statement"], str(node.get("title") or "")) \
        or Verdict(STRONG)


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
    verdict = asserts_verdict(item, entry["statement"], about)
    if verdict:
        return verdict
    if not _rule_item_in_entry(probe, item.get("read_by"), name.split(".")[0], item, entry):
        return Verdict(WEAK, f"{target}.{name}: a pin proves a word exists; it counts only beside "
                       "a rule item of this entry that reads the field (read_by)")
    return Verdict(STRONG)


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


PRESENCE_CAP = " holds presence, which caps at partial on prose"


def _verdict(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    """An item's verdict on its own, before the triple asks for its fellow legs."""
    if any(isinstance(v, str) and v.startswith(EXAMPLES) for v in item.values()):
        return Verdict(DENIED, f"{item['target']}: examples/ cannot be evidence; a fork may "
                       "delete it")
    sentence = item.get("sentence")
    if sentence is not None and not any(cites(item, s) for s in citable(entry["statement"])):
        return Verdict(DENIED, f"{item['target']}: sentence {sentence[:40]!r}... is not a whole "
                       "marked sentence of the statement (a fragment or a clause, such as "
                       "'the', would cite every sentence)")
    verdict = JUDGES[item["kind"]](probe, item, entry)
    if verdict.strength == STRONG and item.get("claim") == PRESENCE \
            and entry.get("kind") != TABLE_KIND:
        return Verdict(WEAK, f"{item['target']}{PRESENCE_CAP}")
    return verdict


def presence_capped(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> bool:
    """Whether an item would judge strong but for its presence claim: the cap group B of
    ``freeze_debt`` rests on. An optional parent, a pin or a bare rule item is weak for another
    reason, so it is not."""
    return judge(probe, item, entry).message.endswith(PRESENCE_CAP)


def judge(probe: Probe, item: Mapping[str, Any], entry: Mapping[str, Any]) -> Verdict:
    verdict = _verdict(probe, item, entry)
    if verdict.strength != STRONG:
        return verdict
    for name in sorted(_held_fields(probe, item, entry)):
        if missing := _triple_missing(probe, name, item, entry):
            return Verdict(WEAK, f"{name} is a decision's required field, held by pin, rule "
                           f"clause and schema shape on one sentence; {missing} is missing")
    return verdict


def sought(entry: Mapping[str, Any], sentence: str) -> Mapping[str, Any] | None:
    """The ``ruling_sought`` record on this sentence of the entry, if any."""
    return next((r for r in entry.get("ruling_sought") or () if cites(r, sentence)), None)


def ruled_out(entry: Mapping[str, Any], sentence: str) -> bool:
    """Whether the user ruled that this sentence needs no evidence (ADR-0005, 2026-11-02)."""
    record = sought(entry, sentence)
    return record is not None and record.get("approved_by") == "user"


def pending_rulings(entry: Mapping[str, Any]) -> list[str]:
    """The sentences of an entry that wait on the user's ruling."""
    return [r["sentence"] for r in entry.get("ruling_sought") or ()
            if r.get("approved_by") != "user"]


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


def _source(function: Callable[..., Any], *, across: bool = False) -> str:
    """A rule's source with the helpers it calls in its own module, adjacent string literals
    joined. ``across`` also follows ``module.helper(`` into another rmf_tool module: a repo-scope
    rule is often a one-line call into the module that holds its clauses."""
    seen: dict[str, str] = {}
    todo = [function]
    while todo:
        current = todo.pop()
        key = f"{current.__module__}.{current.__name__}"
        if key in seen:
            continue
        module = sys.modules[current.__module__]
        seen[key] = inspect.getsource(current)
        for name in _CALL.findall(seen[key]):
            helper = getattr(module, name, None)
            if inspect.isfunction(helper) and helper.__module__ == module.__name__:
                todo.append(helper)
        for alias, name in _QUALIFIED_CALL.findall(seen[key]) if across else ():
            other = getattr(module, alias, None)
            helper = getattr(other, name, None) if inspect.ismodule(other) else None
            if inspect.isfunction(helper) and helper.__module__.startswith("rmf_tool."):
                todo.append(helper)
    return _ADJACENT.sub("", "\n".join(seen.values()))


def rule_sources() -> dict[str, str]:
    """Each rule's source, run rules and the repo-scope rules of `rmf validate`, so a message
    can be found whole."""
    from rmf_tool.check.rules import RULES
    from rmf_tool.framework.validate import RULES as FRAMEWORK_RULES

    out = {ident: _source(function) for ident, function in RULES.items()}
    out.update({ident: _source(function, across=True)
                for ident, function in FRAMEWORK_RULES.items()})
    return out


def probe(repo: Path, framework: Framework) -> Probe:
    return Probe(repo, framework, rules_by_id(), rule_sources())
