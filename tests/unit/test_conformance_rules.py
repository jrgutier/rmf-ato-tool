"""FW-REQ-001/003/004/005 and FW-TASK-002, each with what makes it fire.

Most tests run on the synthetic register of _conformance_fixtures, so they pin nothing the
phases change. The mutation tests start from a claim the rule accepts and change one thing;
the ones named after the review's fakes reproduce each way the first register could be
satisfied without proving anything.
"""

import copy
import functools
import json
import re
import shutil

import _conformance_fixtures as fx
import pytest
from _framework_fixtures import MINI, REAL
from conftest import REPO_ROOT
from typer.testing import CliRunner

from rmf_tool import ci, refs
from rmf_tool.check import Rule
from rmf_tool.cli import app
from rmf_tool.conformance import evidence, extract, register, rules
from rmf_tool.framework.citations import Resolver
from rmf_tool.framework.load import load as load_framework
from rmf_tool.framework.model import Entity, Location
from rmf_tool.framework.validate import validate
from rmf_tool.gitutil import resolve_base, show_file
from rmf_tool.profiles import PHASES, Profile, resolve
from rmf_tool.refs.toc import compact

P10 = Profile("p10", frozenset({"p1", "p2", "p2x", "p3a", "p10"}))
DOC, TIER1 = fx.DOC, fx.TIER1


@pytest.fixture
def repo(tmp_path):
    return fx.build(tmp_path)


@pytest.fixture
def reg(repo):
    return fx.load(repo)


@pytest.fixture
def index():
    return fx.index()


@pytest.fixture
def framework():
    return load_framework(REAL, REPO_ROOT).framework


class _Resolver:
    """Resolves a citation when its text file exists; the real Resolver needs an index file."""

    def __init__(self, repo):
        self.repo = repo

    def resolve(self, citation):
        from rmf_tool.framework.citations import OK, Resolution
        from rmf_tool.refs.toc import compact
        entry = fx.INDEX.get(citation["ref"])
        if entry is None or entry["status"] != "ok":
            return Resolution("error", f"unknown or pending reference {citation['ref']}")
        text = (self.repo / entry["text"]["path"]).read_text(encoding="utf-8")
        pages = text.split("<!-- page ")
        page = next((p for p in pages if p.startswith(f"{citation['page']} ")), "")
        if compact(citation["anchor"]) not in compact(page):
            return Resolution("error", f"anchor not found on page {citation['page']}")
        return Resolution(OK, "")


def messages(findings):
    return [f.message for f in findings]


def shape(repo, reg, index):
    return messages(rules.shape(reg, _Resolver(repo), repo, index))


def ladder(reg, framework, extra_rules=(), repo=REPO_ROOT):
    probe = evidence.probe(repo, framework)
    probe = evidence.Probe(repo, framework, {**probe.rules, **{r.id: r for r in extra_rules}})
    return messages(rules.ladder(reg, probe))


def schema_repo(tmp_path, pointer="decision", **node):
    """A copy of framework/schema whose decision schema property ``pointer`` carries ``node``
    (an x-enforces link, a description), so schema evidence can be judged without editing
    the real schema."""
    shutil.copytree(REPO_ROOT / "framework/schema", tmp_path / "framework/schema")
    path = tmp_path / "framework/schema/decision.schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["properties"][pointer].update(node)
    path.write_text(json.dumps(data), encoding="utf-8")
    return tmp_path


@functools.lru_cache(maxsize=1)
def _framework():
    return load_framework(REAL, REPO_ROOT).framework


def reasons(reg, index, repo=REPO_ROOT):
    """FW-REQ-004 judges closure evidence as FW-REQ-003 does; the synthetic rule REG-001 is
    in the probe so a test can close a work item on strong evidence."""
    probe = evidence.probe(repo, _framework())
    probe = evidence.Probe(repo, _framework(), {**probe.rules, **{r.id: r for r in EXTRA_RULES}})
    return messages(rules.reasons(reg, index, probe))


def sync(repo, index, only=None):
    """Per reference: the pin and reference-list checks need the real repository."""
    reg = fx.load(repo)
    refs_ = [only] if only else [r for r, e in index.items() if e["status"] == "ok"]
    return [m for ref in refs_ for m in messages(rules.sync(repo, reg, index, ref))]


# --- the real register ----------------------------------------------------------------------


def test_the_real_register_passes_every_rule():
    result = validate(REAL, REPO_ROOT, P10)

    assert result.ok, [f.render() for f in result.findings][:10]
    assert {"FW-REQ-001", "FW-REQ-003", "FW-REQ-004", "FW-REQ-005", "FW-TASK-002"} <= set(
        result.rules_run)


def test_a_subset_framework_is_not_checked_against_the_whole_pin():
    assert validate(MINI, REPO_ROOT, P10).ok


def _reassigned(old: str, new: str) -> bool:
    """An ID now holds other text. Words gained or lost at an edge, as when a re-extraction
    drops a footer, keep the ID, and its review clears needs_review."""
    return compact(old) not in compact(new) and compact(new) not in compact(old)


def test_requirement_ids_and_statements_are_pinned_against_the_base():
    """INV-3: every ID at the base is still in the register, and an ID whose statement now says
    something else says so (needs_review) or is removed; an ID is never silently reassigned."""
    base = resolve_base(REPO_ROOT)
    if base.ref is None:
        pytest.skip("no merge base")
    now = register.load(REPO_ROOT)
    checked = 0
    for path in sorted((REPO_ROOT / register.REQUIREMENTS_DIR).glob("*.yaml")):
        old = show_file(REPO_ROOT, base.ref, f"{register.REQUIREMENTS_DIR}/{path.name}")
        if old is None:
            continue
        ids = re.findall(r'^  - id: "(REQ-[^"]+)"\n(?:    .*\n)*?    statement: (".*")$', old, re.M)
        for ident, statement in ids:
            entry = now.entry(ident)
            assert entry is not None, f"{ident} left the register"
            if _reassigned(json.loads(statement), entry["statement"]):
                assert entry.get("needs_review") or entry.get("removed"), ident
            checked += 1
    assert checked >= 0


@pytest.mark.parametrize("old, new, expected", [
    ("The AO must sign.", "The AO must sign.", False),
    ("3 The AO must sign.", "The AO must sign.", False),
    ("The AO must sign", "The AO must sign the decision.", False),
    ("The AO must sign.", "The ISSM must review the plan.", True),
])
def test_only_a_different_statement_counts_as_reassigning_an_id(old, new, expected):
    assert _reassigned(old, new) is expected


def test_every_audit_finding_has_a_work_item():
    audit = (REPO_ROOT / "docs/audits/2026-10-31-coverage-audit.md").read_text(encoding="utf-8")
    imports = (REPO_ROOT / "docs/audits/2026-11-01-import-findings.md").read_text(encoding="utf-8")
    findings = set(re.findall(r"^\| ([NDC]-\d+) \|", audit, re.M))
    added = set(re.findall(r"^\| (I-\d+) \|", imports, re.M))
    triage = (REPO_ROOT / "docs/audits/2026-11-triage/audit.md").read_text(encoding="utf-8")
    conflicts, _, later = triage.partition("## Left for later phases")
    routed = dict(re.findall(r"^\| (I-\d+) \|.*\| (WI-\d+) \| p\d+ \|$", conflicts, re.M))
    linked = {f for w in register.load(REPO_ROOT).work_items.values() for f in w["findings"]}

    assert len(findings) == 47
    assert findings | added <= linked
    assert linked - findings - added <= set(routed)
    assert set(re.findall(r"^\| (I-\d+) \|", conflicts, re.M)) == set(routed)
    assert set(routed.values()) <= set(register.load(REPO_ROOT).work_items)


def test_every_open_register_work_item_binds_an_entry():
    reg = register.load(REPO_ROOT)
    for ident, item in reg.work_items.items():
        if item.get("scope", "register") == "register":
            assert reg.bound(ident) or reg.waived(ident), ident


# --- FW-REQ-001 --------------------------------------------------------------------------


def test_the_synthetic_register_is_clean(repo, reg, index):
    assert shape(repo, reg, index) == []
    assert reasons(reg, index) == []
    assert sync(repo, index) == []


def test_fw_req_001_fires_when_a_statement_is_not_in_its_passage(repo, reg, index):
    fx.entry(reg)["statement"] = "A requirement the instruction never states."

    assert shape(repo, reg, index) == [f"REQ-{DOC}-0001: the statement is not in the passage on "
                                       "page 1"]


def test_fw_req_001_fires_when_a_citation_does_not_resolve(repo, reg, index):
    fx.entry(reg)["citation"]["page"] = 2

    assert "anchor not found on page 2" in shape(repo, reg, index)[0]


def test_fw_req_001_reports_ids_and_work_items(repo, reg, index):
    entry = fx.entry(reg)
    entry["work_item"] = "WI-999"
    other = copy.deepcopy(entry)
    other["id"] = "REQ-OTHER-0001"
    reg.files[DOC]["requirements"] += [copy.deepcopy(entry), other]

    found = shape(repo, reg, index)

    assert f"REQ-{DOC}-0001: duplicate ID" in found
    assert f"REQ-{DOC}-0001: unknown work item WI-999" in found
    assert f"REQ-OTHER-0001: ID must start with REQ-{DOC}-" in found


def test_fw_req_001_needs_a_source_for_every_pdf_and_web_reference(repo, reg, index):
    del reg.sources[TIER1]
    reg.sources["NOPE"] = {"ref": "NOPE", "mode": "statement"}
    index["PAGE"] = {"id": "PAGE", "kind": "web", "status": "ok"}
    index["OSCAL"] = {"id": "OSCAL", "kind": "oscal-catalog", "status": "ok"}
    del reg.files[TIER1]

    found = shape(repo, reg, index)

    assert f"reference(s) with no source entry: PAGE, {TIER1}" in found
    assert "source entries for unknown references: NOPE" in found


def test_a_dropped_reference_that_leaves_files_behind_is_named(repo, reg, index):
    """A fork that deletes a reference must take its source entry, requirements file and text
    hash with it; each one left behind is a finding, not a surprise."""
    del index[DOC]
    reg.text_hashes["GONE"] = "0" * 64

    found = shape(repo, reg, index)

    assert f"source entries for unknown references: {DOC}" in found
    assert any(f"{DOC}: requirements file for a reference with no source entry" in m
               for m in found) is False, "the source entry still names it; one finding per file"
    del reg.sources[DOC]
    found = shape(repo, reg, index)
    assert any(f"{DOC}: requirements file for a reference with no source entry" in m
               for m in found)
    assert any("GONE: text hash for a reference that is not in the index" in m for m in found)


def test_a_web_reference_is_excluded_and_a_pdf_cannot_be(repo, reg, index):
    index["PAGE"] = {"id": "PAGE", "kind": "web", "status": "ok"}
    reg.sources["PAGE"] = {"ref": "PAGE", "mode": "excluded", "basis": "no local copy"}
    assert shape(repo, reg, index) == []

    reg.sources[TIER1] = {"ref": TIER1, "mode": "excluded", "basis": "skipping it"}
    assert f"{TIER1} is a PDF; it cannot be mode: excluded" in shape(repo, reg, index)


def test_a_pending_document_has_no_requirement_entries(repo, reg, index):
    reg.files[fx.PENDING] = {"ref": fx.PENDING, "requirements": []}

    assert any("unassessed" in m for m in shape(repo, reg, index))


def test_an_imported_document_must_declare_scopes(repo, reg, index):
    del reg.sources[DOC]["scopes"]

    assert f"{DOC} is imported; declare its scopes" in shape(repo, reg, index)


def test_every_page_is_in_a_scope_or_an_exclusion(repo, reg, index):
    """The fake: narrowing a scope silently retires what it covered. Now the page it drops
    must be excluded with a reason, and FW-REQ-004 holds the retired entries (below)."""
    del reg.sources[DOC]["excluded"]
    assert f"{DOC}: pages 2 are in no scope and no exclusion; read them or exclude them with " \
           "a reason" in shape(repo, reg, index)

    reg.sources[DOC]["excluded"] = [{"pages": [1, 2], "reason": "Doubles page 1."}]
    assert f"{DOC}: pages 1 are in more than one range" in shape(repo, reg, index)

    reg.sources[DOC]["excluded"] = [{"pages": [2, 9], "reason": "Past the end."}]
    assert f"{DOC}: exclusion pages 2-9 are not within 1-2" in shape(repo, reg, index)


def test_a_removed_entry_is_not_checked_against_the_text(repo, reg, index):
    fx.entry(reg).update(statement="Gone from the source.", removed=True)

    assert shape(repo, reg, index) == []


def test_a_missing_text_file_is_a_finding_not_a_traceback(repo, reg, index):
    (repo / f"references/text/{TIER1}.md").unlink()

    found = shape(repo, reg, index)
    synced = sync(repo, index)

    assert any(f"{TIER1}: cannot read its text" in m for m in found)
    assert any(f"{TIER1}: cannot read its text" in m for m in synced)


def test_an_unreadable_file_is_one_finding_and_stops_only_that_file(tmp_path, index):
    conformance = tmp_path / "conformance"
    shutil.copytree(REPO_ROOT / "conformance/schema", conformance / "schema")
    (conformance / "sources.yaml").write_text("documents: [")
    (conformance / "work-items.yaml").write_text("schema_version: 1\nwork_items: []\n")
    (conformance / "triage.yaml").write_text("schema_version: 1\npatterns: [{id: bad}]\n")
    for name, text in fx.EMPTY.items():
        if name != "triage.yaml":
            (conformance / name).write_text(text)
    (conformance / "text-hashes.yaml").write_text("schema_version: 1\nhashes: {}\n")

    loaded = register.load(tmp_path)
    found = rules.shape(loaded, _Resolver(tmp_path), tmp_path, index)

    assert any("not valid YAML" in m for m in messages(found))
    assert any("triage.yaml" in (f.path or "") for f in found)


# --- FW-REQ-003: the ladder --------------------------------------------------------------

STATEMENT = ("a. Will register the system with the component registry before use.")
ENFORCING = Rule(id="REG-001", scope="repo", severity="E", ac=("AC-1",), phase="p10",
                 applies_after=None, summary="the system is not registered in the component "
                 "registry before use", hint="register it",
                 fixture="tests/unit/test_conformance_rules.py",
                 enforces=(f"REQ-{DOC}-0001",))
ASSERTS = "The system is registered with the component registry before it is used."
TEMPLATE_HEADING = "Approach to control implementation"
LINK = {"enforces": [f"REQ-{DOC}-0001"]}
SCHEMA_TARGET = "framework/schema/decision.schema.json#/properties/decision"
# Each strong claim with the setup that links its target back to the entry: a rule lists the
# entry in enforces (registry.yaml), a schema property in x-enforces, an entity in enforces.
STRONG_CLAIMS = {
    "rule": ({"kind": "rule", "target": "REG-001", "asserts": ASSERTS}, None),
    "schema": ({"kind": "schema", "target": SCHEMA_TARGET, "asserts": ASSERTS},
               lambda fw, tmp: schema_repo(tmp, **{"x-enforces": [f"REQ-{DOC}-0001"],
                                                   "description": "The decision recorded when "
                                                   "the system is registered."})),
    "pinned": ({"kind": "pinned", "target": "P-18", "field": "outputs", "value": ["ART-REG"],
                "asserts": "P-18 registers the system in the component registry."},
               lambda fw, tmp: fw.index("tasks")["P-18"].data.update(LINK)),
    "template": ({"kind": "template", "target": "ART-SSP", "heading": TEMPLATE_HEADING,
                  "asserts": "The plan records registration with the component registry "
                             "before use."},
                 lambda fw, tmp: fw.index("artifacts")["ART-SSP"].data.update(
                     required_sections=[TEMPLATE_HEADING], **LINK)),
}
VACUOUS = [
    ("rule", "without an asserts text", {"asserts": ""}, "does not say what it asserts"),
    ("rule", "a warning rule", {"target": "WARN-001"}, "WARN-001 only warns"),
    ("rule", "a rule with no fixture", {"target": "NOFIXTURE-001"},
     "NOFIXTURE-001 has no negative fixture"),
    ("schema", "an optional property", {"target": "framework/schema/decision.schema.json"
                                        "#/properties/conditions"}, "is optional"),
    ("schema", "a pointer that is not a property",
     {"target": "framework/schema/decision.schema.json#/required"}, "is not a property"),
    ("template", "a heading nothing requires", {"heading": "Open items"},
     "is not in ART-SSP required_sections"),
]
EXTRA_RULES = (
    ENFORCING,
    Rule(**{**ENFORCING.__dict__, "id": "RET-001", "summary": "the system is not retired when "
            "its authorization ends", "hint": "retire it"}),
    Rule(**{**ENFORCING.__dict__, "id": "WARN-001", "severity": "W"}),
    Rule(**{**ENFORCING.__dict__, "id": "NOFIXTURE-001", "fixture": None, "exempt_reason": "x"}),
)


def covered(reg, *items):
    entry = fx.entry(reg)
    entry.update(status="covered", evidence=list(items))
    return entry


def _strong(kind, framework, tmp_path):
    """The claim of ``kind`` with its target linked back; returns (claim, repo to judge in)."""
    claim, setup = STRONG_CLAIMS[kind]
    repo = (setup(framework, tmp_path) if setup else None) or REPO_ROOT
    return claim, repo


@pytest.mark.parametrize("kind", STRONG_CLAIMS)
def test_each_evidence_kind_can_carry_covered(reg, framework, tmp_path, kind):
    claim, repo = _strong(kind, framework, tmp_path)
    covered(reg, claim)

    assert ladder(reg, framework, (ENFORCING,) if kind == "rule" else (), repo) == []


@pytest.mark.parametrize("kind, label, change, needle", VACUOUS,
                         ids=[f"{v[0]}: {v[1]}" for v in VACUOUS])
def test_fw_req_003_rejects_each_vacuous_evidence_kind(reg, framework, tmp_path, kind, label,
                                                       change, needle):
    claim, repo = _strong(kind, framework, tmp_path)
    covered(reg, {**claim, **change})
    needed = [r for r in EXTRA_RULES if r.id == {**claim, **change}["target"]]

    found = [m for m in ladder(reg, framework, needed, repo) if m.startswith(f"REQ-{DOC}-")]

    assert len(found) == 1, found
    assert found[0].startswith(f"REQ-{DOC}-0001: covered needs") and needle in found[0]
    assert found[0].endswith("; use partial")


AO_STATEMENT = ("The authorizing official renders the authorization decision after reviewing "
                "the risk determination.")


@pytest.mark.parametrize("claim", [
    {"kind": "schema", "target": "framework/schema/allocation.schema.json#/properties/"
     "allocations", "asserts": AO_STATEMENT},
    {"kind": "pinned", "target": "ART-SSP", "field": "template", "asserts": AO_STATEMENT},
], ids=["schema", "pinned"])
def test_the_fake_target_about_something_else_is_denied(reg, framework, tmp_path, claim):
    """The fakes: an asserts text copied from an AO statement was strong on the allocation
    schema and on ART-SSP's template field. The target must link back to the entry, and the
    asserts must share a content word with what the target is about."""
    entry = fx.entry(reg)
    entry.update(statement=AO_STATEMENT, status="covered")
    if claim["kind"] == "pinned":
        claim = {**claim, "value": framework.index("artifacts")["ART-SSP"].data["template"]}
    entry["evidence"] = [claim]

    unlinked = ladder(reg, framework)
    assert any("does not list REQ-DOC-0001 in" in m for m in unlinked), unlinked

    if claim["kind"] == "pinned":
        framework.index("artifacts")["ART-SSP"].data.update(LINK)
        repo = REPO_ROOT
    else:
        repo = tmp_path
        shutil.copytree(REPO_ROOT / "framework/schema", repo / "framework/schema")
        path = repo / "framework/schema/allocation.schema.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["properties"]["allocations"]["x-enforces"] = [f"REQ-{DOC}-0001"]
        path.write_text(json.dumps(data), encoding="utf-8")
    linked = ladder(reg, framework, (), repo)

    assert any("shares no content word with what" in m and "is about" in m for m in linked), \
        linked


def test_a_schema_or_entity_link_must_be_cited_back(reg, framework, tmp_path):
    repo = schema_repo(tmp_path, **{"x-enforces": [f"REQ-{DOC}-0001", f"REQ-{DOC}-9999"]})
    framework.index("tasks")["P-18"].data.update(LINK)

    found = ladder(reg, framework, (), repo)

    assert f"{SCHEMA_TARGET} enforces REQ-{DOC}-0001, but that entry does not cite " \
           f"{SCHEMA_TARGET} as evidence" in found
    assert f"{SCHEMA_TARGET} enforces REQ-{DOC}-9999, which is not a live register entry" in found
    assert f"P-18 enforces REQ-{DOC}-0001, but that entry does not cite P-18 as evidence" in found


def test_the_fake_identity_pin_is_denied(reg, framework):
    """The fake: `{kind: pinned, target: AD-ATO, field: id, value: AD-ATO}` was strong."""
    for field, value in (("id", "AD-ATO"), ("name", framework.index("decisions")["AD-ATO"]
                                            .data["name"])):
        covered(reg, {"kind": "pinned", "target": "AD-ATO", "field": field, "value": value,
                      "asserts": ASSERTS})
        found = ladder(reg, framework)

        assert len(found) == 2 and "not a pinnable field" in found[0], found


def test_a_pin_that_asserts_a_real_value_must_still_match_the_statement(reg, framework):
    """`asserts: x` was strong. Now it must share vocabulary with the statement."""
    claim = {"kind": "pinned", "target": "P-18", "field": "outputs", "value": ["ART-REG"]}
    framework.index("tasks")["P-18"].data.update(LINK)
    for asserts in ("x", "The decision names an authorizing official and a termination date."):
        covered(reg, {**claim, "asserts": asserts})
        found = ladder(reg, framework)

        assert any("shares" in m and "content word" in m for m in found), (asserts, found)
    covered(reg, {**claim, "asserts": "P-18 registers the system in the component registry."})
    assert ladder(reg, framework) == []


def test_rule_evidence_needs_the_rule_to_list_the_entry(reg, framework):
    """The fake: 56 of 72 rules were strong with `asserts: x`. A rule is evidence only for the
    entries it lists in enforces, and a listed entry must cite the rule back."""
    unlisted = Rule(**{**ENFORCING.__dict__, "enforces": ()})
    covered(reg, {"kind": "rule", "target": "REG-001", "asserts": ASSERTS})
    found = ladder(reg, framework, (unlisted,))
    assert any("does not list REQ-DOC-0001 in enforces" in m for m in found)

    fx.entry(reg).update(status="candidate", evidence=[])
    found = ladder(reg, framework, (ENFORCING,))
    assert found == ["REG-001 enforces REQ-DOC-0001, but that entry does not cite REG-001 as "
                     "evidence"]

    dangling = Rule(**{**ENFORCING.__dict__, "enforces": ("REQ-DOC-9999",)})
    assert "REG-001 enforces REQ-DOC-9999, which is not a live register entry" in ladder(
        reg, framework, (dangling,))


@pytest.mark.parametrize("item, needle", [
    ({"kind": "rule", "target": "NO-SUCH-001", "asserts": ASSERTS}, "no rule NO-SUCH-001"),
    ({"kind": "schema", "target": "framework/schema/decision.schema.json#/properties/nope"},
     "no 'nope' in the schema"),
    ({"kind": "schema", "target": "conformance/schema/sources.schema.json#/required"},
     "expected framework/schema"),
    ({"kind": "pinned", "target": "AD-ATO", "field": "decided_by", "value": "PER-PM"},
     "is 'PER-AO', not 'PER-PM'"),
    ({"kind": "pinned", "target": "AD-NOPE", "field": "decided_by", "value": "x"},
     "no such framework entity field"),
    ({"kind": "pinned", "target": "AD-ATO", "field": "requires", "value": None},
     "pins nothing"),
    ({"kind": "template", "target": "ART-SSP", "heading": "No such heading"}, "has no heading"),
    ({"kind": "template", "target": "AD-ATO", "heading": "x"}, "no template"),
    ({"kind": "citation", "target": "ART-NOPE"}, "no framework entity ART-NOPE"),
    ({"kind": "prose", "target": "README.md"}, "expected a playbook"),
    ({"kind": "prose", "target": "playbooks/none.md"}, "expected a playbook"),
])
def test_evidence_that_does_not_resolve_fails_at_any_status(reg, framework, item, needle):
    fx.entry(reg).update(status="partial", reason="Part of it.", evidence=[item])

    found = ladder(reg, framework)

    assert len(found) == 1 and "evidence unresolved" in found[0] and needle in found[0], found


@pytest.mark.parametrize("target", ["FW-SCHEMA-001", "FW-CITE-002", "TRACE-001", "RUN-FM-001",
                                    "FW-REQ-003"])
def test_generic_rules_are_denied(reg, framework, target):
    covered(reg, {"kind": "rule", "target": target, "asserts": ASSERTS})

    found = ladder(reg, framework)

    assert "evidence denied" in found[0] and "generic" in found[0]


@pytest.mark.parametrize("item", [
    {"kind": "prose", "target": "examples/uas-gcs/README.md"},
    {"kind": "pinned", "target": "AD-ATO", "field": "decided_by", "value": "examples/x"},
])
def test_anything_under_examples_is_denied(reg, framework, item):
    fx.entry(reg).update(status="partial", reason="r", evidence=[item])

    assert "examples/ cannot be evidence" in ladder(reg, framework)[0]


@pytest.mark.parametrize("item", [
    {"kind": "citation", "target": "P-18"},
    {"kind": "prose", "target": "playbooks/P/P-18.md"},
    {"kind": "prose", "target": "MANUAL.md"},
])
def test_citations_and_prose_cap_at_partial(reg, framework, item):
    entry = covered(reg, item)
    assert "use partial" in ladder(reg, framework)[0]

    entry.update(status="partial", reason="Documented only.")
    assert ladder(reg, framework) == []


TWO = "The system is registered with the component registry before use. The owner must retire " \
      "the system when its authorization ends."


def test_the_fake_one_sentence_covering_a_two_obligation_paragraph_is_an_error(reg, framework):
    """The mutation: a paragraph with two marked sentences, strong evidence on one of them,
    cannot be covered; evidence must cite every marked sentence."""
    entry = covered(reg, {"kind": "rule", "target": "REG-001", "asserts": ASSERTS,
                          "sentence": "The system is registered with the component registry "
                                      "before use."})
    entry["kind"] = "modal"
    entry["statement"] = TWO
    assert extract.marked_sentences(TWO) == ["The system is registered with the component "
                                             "registry before use.",
                                             "The owner must retire the system when its "
                                             "authorization ends."]

    def about_coverage():
        return [m for m in ladder(reg, framework, EXTRA_RULES) if m.startswith(f"REQ-{DOC}")]

    assert about_coverage() == [f"REQ-{DOC}-0001: covered, but 1 of its 2 marked sentences are "
                                "cited by no strong evidence (evidence[].sentence): The owner "
                                "must retire the system when its authorization ends; use partial"]

    entry["evidence"].append({"kind": "rule", "target": "RET-001", "asserts": "The owner "
                              "retires the system when its authorization ends.",
                              "sentence": "the owner must retire the system when its "
                                          "authorization ends"})
    assert about_coverage() == [], "the whole sentence, up to case and punctuation, cites it"

    entry["status"] = "partial"
    entry["reason"] = "One of two."
    entry["evidence"].pop()
    assert about_coverage() == []


RETIRE = {"kind": "rule", "target": "RET-001",
          "asserts": "The owner retires the system when its authorization ends."}


@pytest.mark.parametrize("sentence", [
    "the", "retire the system when its authorization ends", "The system is registered",
    "The owner must retire the system when its authorization ends. The system is registered "
    "with the component registry before use.", TWO,
], ids=["the", "a clause", "an opening", "the two sentences swapped", "the whole statement"])
def test_the_fake_fragment_that_cites_every_sentence_is_denied(reg, framework, sentence):
    """The fake (fourth review): `cites` accepted containment either way, so `sentence: "the"`
    cited every marked sentence and one item covered a two-obligation paragraph. A sentence
    now equals one marked sentence of the statement, whole."""
    entry = covered(reg, {**RETIRE, "sentence": sentence})
    entry["kind"] = "modal"
    entry["statement"] = TWO

    found = [m for m in ladder(reg, framework, EXTRA_RULES) if m.startswith(f"REQ-{DOC}")]

    assert any("is not a whole marked sentence of the statement" in m for m in found), found
    assert any(m.endswith("; use partial") for m in found), "the denied item proves nothing"


def test_the_fake_one_item_reused_for_two_sentences_is_an_error(reg, framework):
    first = "The system is registered with the component registry before use."
    entry = covered(reg, {"kind": "rule", "target": "REG-001", "asserts": ASSERTS,
                          "sentence": first}, {**RETIRE, "sentence": first})
    entry["kind"] = "modal"
    entry["statement"] = TWO

    found = [m for m in ladder(reg, framework, EXTRA_RULES) if m.startswith(f"REQ-{DOC}")]

    assert found == [f"REQ-{DOC}-0001: covered, but 1 of its 2 marked sentences are cited by no "
                     "strong evidence (evidence[].sentence): The owner must retire the system "
                     "when its authorization ends; use partial"]
    entry["evidence"][1]["sentence"] = "The owner must retire the system when its authorization " \
                                       "ends."
    assert [m for m in ladder(reg, framework, EXTRA_RULES) if m.startswith(f"REQ-{DOC}")] == []


def test_a_lettered_item_with_two_marked_sentences_needs_both_cited(reg, framework):
    """Decision of the fourth review: the per-sentence rule applies to every kind with two or
    more marked sentences, rather than splitting long lettered items as prose is split."""
    entry = covered(reg, {"kind": "rule", "target": "REG-001", "asserts": ASSERTS,
                          "sentence": "Will register the system with the component registry "
                                      "before use."})
    entry["kind"] = "lettered"
    entry["statement"] = "a. Will register the system with the component registry before use. " \
                         "The owner must retire the system when its authorization ends."

    found = [m for m in ladder(reg, framework, EXTRA_RULES) if m.startswith(f"REQ-{DOC}")]

    assert any("1 of its 2 marked sentences are cited by no strong evidence" in m
               for m in found), found


def test_an_evidence_sentence_must_be_in_the_statement(reg, framework):
    covered(reg, {"kind": "rule", "target": "REG-001", "asserts": ASSERTS,
                  "sentence": "The AO must approve every registration."})

    found = ladder(reg, framework, EXTRA_RULES)

    assert any("evidence denied: REG-001: sentence 'The AO must approve every registration"
               in m and "not a whole marked sentence" in m for m in found), found


def test_covered_with_no_evidence_fails(reg, framework):
    covered(reg)

    assert "no evidence" in ladder(reg, framework)[0]


def _many_entries(reg, count):
    """Pad the synthetic document with copies of its first entry, so fan-out can be tested."""
    doc = reg.files[DOC]["requirements"]
    first = doc[0]
    for n in range(count):
        doc.append({**copy.deepcopy(first), "id": f"REQ-{DOC}-{100 + n:04d}"})
    return doc


@pytest.mark.parametrize("claim", [
    {"kind": "pinned", "target": "P-18", "field": "outputs", "value": ["ART-REG"]},
    {"kind": "prose", "target": "MANUAL.md"},
    {"kind": "citation", "target": "P-18"},
])
def test_the_fake_fan_out_is_an_error_for_every_evidence_kind(reg, framework, claim):
    """The fake: 1,500 identical pins gave 0 findings because only rule evidence was counted."""
    entries = _many_entries(reg, rules.FAN_OUT_CAP)
    for entry in entries[:rules.FAN_OUT_CAP + 1]:
        entry.update(status="partial", reason="r", evidence=[claim])

    found = ladder(reg, framework)

    assert any(f"{claim['kind']} {claim['target']} is evidence for {rules.FAN_OUT_CAP + 1} "
               "requirements, over its limit of 25" in m for m in found), found
    exception = {"kind": claim["kind"], "target": claim["target"], "limit": 30,
                 "reason": "One table proves every row."}
    reg.fan_out_exceptions.append(exception)
    found = ladder(reg, framework)
    assert any("over its limit" in m for m in found), "a reason alone does not lift the cap"
    assert any("needs approved_by: user" in m for m in found)

    exception["approved_by"] = "user"
    assert not any("over its limit" in m or "approved_by" in m for m in ladder(reg, framework))


# --- FW-REQ-004 --------------------------------------------------------------------------


@pytest.mark.parametrize("status", ["partial", "deferred", "not-applicable"])
def test_fw_req_004_needs_a_reason(reg, index, status):
    fx.entry(reg)["status"] = status
    if status == "partial":
        fx.entry(reg)["evidence"] = [{"kind": "citation", "target": "P-18"}]

    assert reasons(reg, index) == [f"REQ-{DOC}-0001: {status} needs a reason"]


def test_partial_needs_at_least_one_evidence_item(reg, index):
    """`mark --status partial --reason x` with no evidence retired an entry with no check."""
    fx.entry(reg).update(status="partial", reason="Half done.")

    assert reasons(reg, index) == [f"REQ-{DOC}-0001: partial needs at least one evidence item "
                                   "(a citation or prose at least); with none it is deferred "
                                   "or not-applicable, say which"]
    fx.entry(reg)["evidence"] = [{"kind": "citation", "target": "P-18"}]
    assert reasons(reg, index) == []


@pytest.mark.parametrize("entry, expected", [
    ({"status": "partial", "evidence": [{"kind": "citation", "target": "P-18"}]}, True),
    ({"status": "partial", "evidence": [{"kind": "prose", "target": "playbooks/x.md"}]}, True),
    ({"status": "partial", "evidence": [{"kind": "rule", "target": "AODM-001"}]}, False),
    ({"status": "covered", "evidence": [{"kind": "rule", "target": "AODM-001"}]}, False),
    ({"status": "candidate"}, False),
], ids=["citation", "prose", "rule", "covered", "candidate"])
def test_partial_on_evidence_that_cannot_fail_counts_as_retired(entry, expected):
    """The share could be dodged for the price of one citation (fifth review)."""
    assert rules.retired(entry) is expected


@pytest.mark.parametrize("fields", [
    {"status": "deferred", "reason": "Scripted away."},
    {"status": "partial", "reason": "Scripted away."},
], ids=["deferred", "partial without evidence"])
def test_the_fake_scripted_loop_of_deferrals_counts_as_retirement(reg, index, fields):
    """The fake (fourth review): the per-document share counted not-applicable only, so a
    loop of `mark --status deferred --reason x` on a tier 2 document, or of `--status partial`
    with no evidence, retired a document with no check."""
    entries = _many_entries(reg, 30)
    for entry in entries[:20]:
        register.mark(reg, entry["id"], **fields)

    found = reasons(reg, index)

    assert any(f"DOC: 20 of {len(entries)} requirements are retired ({rules.RETIRED}; "
               f"{20 / len(entries):.0%}), over 25% of the document" in m for m in found), found
    assert rules.retired_share(reg.files[DOC]) == (20, len(entries))


def test_fw_req_004_fires_on_a_tier_1_deferral_without_approval(reg, index):
    entry = fx.entry(reg, 1, TIER1)
    entry.update(status="deferred", reason="rmf-ks-not-public")

    assert reasons(reg, index) == [f"{entry['id']}: deferring a tier 1 document needs "
                                   "approved_by: user"]
    entry["approved_by"] = "user"
    assert reasons(reg, index) == []


def test_a_deferral_outside_tier_1_needs_only_a_reason(reg, index):
    fx.entry(reg).update(status="deferred", reason="rmf-ks-not-public")

    assert reasons(reg, index) == []


def test_covered_cannot_keep_an_open_work_item(reg, index):
    fx.entry(reg).update(status="covered")

    assert "covered with open work item WI-01" in reasons(reg, index)[0]


def test_the_fake_removal_of_a_reviewed_entry_needs_a_reason(reg, index):
    """The fake: a narrower scope retired 12 covered entries with 0 findings."""
    entry = fx.entry(reg, 2)
    entry.update(status="covered", evidence=[{"kind": "citation", "target": "P-18"}],
                 removed=True)

    assert reasons(reg, index) == [f"REQ-{DOC}-0002: a covered entry left its source; record "
                                   "removal_reason or restore the text"]
    entry["removal_reason"] = "The 2026 edition dropped the registry requirement."
    assert reasons(reg, index) == []


def test_a_removed_candidate_needs_nothing(reg, index):
    fx.entry(reg, 2)["removed"] = True

    assert reasons(reg, index) == []


PATTERN = {"id": "TP-01", "ref": DOC, "statement": "retire the system", "reason": "Retirement "
           "is outside the run.", "sample": [f"REQ-{DOC}-0002"]}


def triaged(reg, pattern=PATTERN):
    for entry in reg.files[pattern["ref"]]["requirements"]:
        if register._matches(pattern, pattern["ref"], entry):
            entry.update(status="not-applicable", reason=pattern["reason"],
                         triaged_by=pattern["id"])
    reg.patterns.append(pattern)


def test_a_specific_reviewed_pattern_on_a_tier_2_document_is_fine(reg, index):
    triaged(reg)

    assert reasons(reg, index) == []
    assert fx.entry(reg, 2)["status"] == "not-applicable"


def test_the_fake_catch_all_pattern_is_refused(reg, index):
    """The fake: `statement: "."` marked all 2,386 entries not-applicable."""
    for regex in (".", ".{8,}", "a|b|c|d|e|f|g|h"):
        reg.patterns = []
        triaged(reg, {**PATTERN, "statement": regex})

        assert any("needs at least 2 literal words" in m for m in reasons(reg, index)), regex


def test_a_pattern_on_a_tier_1_document_is_refused(reg, index):
    triaged(reg, {**PATTERN, "ref": TIER1, "statement": "appoint an authorizing official",
                  "sample": [f"REQ-{TIER1}-0001"]})

    assert any("refused on a tier 1 document" in m for m in reasons(reg, index))


def test_a_pattern_over_the_cap_is_refused(reg, index):
    entries = _many_entries(reg, rules.TRIAGE_CAP + 1)
    for entry in entries:
        entry["statement"] = "The owner will retire the system when its authorization ends."
    triaged(reg)

    assert any(f"over the cap of {rules.TRIAGE_CAP}" in m for m in reasons(reg, index))


def test_the_fake_regex_repeated_per_page_range_is_refused(reg, index):
    """The fake: the per-pattern cap was dodged by the same regex on several page ranges."""
    triaged(reg)
    triaged(reg, {**PATTERN, "id": "TP-02", "pages": [1, 1]})

    assert any("TP-02 (DOC): the same regexes as TP-01" in m for m in reasons(reg, index))


def test_patterns_together_cannot_retire_more_than_a_share_of_a_document(reg, index):
    entries = _many_entries(reg, 60)
    for n, entry in enumerate(entries):
        entry["statement"] = f"The owner will retire the system {n} when its authorization ends."
    for n in range(0, 60, 20):
        triaged(reg, {**PATTERN, "id": f"TP-{n + 10:02d}", "statement": f"retire the system "
                      f"(?:{'|'.join(str(k) for k in range(n, n + 20))}) when"})

    found = reasons(reg, index)

    assert not any("over the cap of" in m for m in found), "each pattern is under its own cap"
    assert any(f"DOC: 60 of {len(entries)} requirements are retired ({rules.RETIRED}; "
               f"{60 / len(entries):.0%}), over 25% of the document" in m for m in found), found


def test_noise_is_not_counted_in_the_retired_share(reg, index):
    """About a quarter of all entries are extraction noise; marking them must not trip the
    per-document limit, and a document of real requirements must still trip it."""
    entries = _many_entries(reg, 40)
    for entry in entries[:20]:
        register.mark(reg, entry["id"], status="not-a-requirement", reason="A heading.")
    assert not [m for m in reasons(reg, index) if "are retired (" in m]

    for entry in entries[20:31]:
        register.mark(reg, entry["id"], status="not-applicable", reason="Binds nobody here.")
    real = len(entries) - 20
    assert rules.retired_share(reg.files[DOC]) == (11, real)
    assert any(f"11 of {real} requirements are retired" in m for m in reasons(reg, index))


def test_noise_needs_a_reason(reg, index):
    entry = _many_entries(reg, 1)[0]
    register.mark(reg, entry["id"], status="not-a-requirement")
    assert f"{entry['id']}: not-a-requirement needs a reason" in reasons(reg, index)


@pytest.mark.parametrize("statement, reason, flagged", [
    ("The ISSM must review the plan.", "A definition of the plan.", True),
    ("The ISSM shall review the plan.", "An example; this shall binds no one.", False),
    ("The ISSM will review the plan.", "The source says what will happen, no duty.", False),
    ("A topic heading.", "A heading.", False),
    ("The ISSM should review the plan.", "A definition of the plan.", True),
    ("The ISSM is responsible for the plan.", "A definition of the plan.", True),
    ("The ISSM is required to review the plan.", "A definition of the plan.", True),
    ("The review is required.", "A definition of the plan.", True),
    ("Reviews are recommended.", "A definition of the plan.", True),
    ("Reviews are recommended.", "The source says recommended of itself, no duty.", False),
    ("The ISSM Should review it.", "A quotation; this should binds no one.", False),
    ("The ISSM is responsible for it.", "A definition: responsible for names the role.", False),
])
def test_noise_holding_a_duty_word_must_answer_for_it(reg, index, statement, reason, flagged):
    entry = _many_entries(reg, 1)[0]
    entry["statement"] = statement
    register.mark(reg, entry["id"], status="not-a-requirement", reason=reason)
    assert any("a not-a-requirement reason must" in m for m in reasons(reg, index)) is flagged


def noise_fake(reg, count=30, marked=20):
    entries = _many_entries(reg, count)
    for entry in entries[:marked]:
        register.mark(reg, entry["id"], status="not-a-requirement", reason="A heading.")
    return entries


def test_a_document_cannot_be_turned_to_noise_without_a_record(reg, index):
    """The fake: every entry marked noise with one reason, and the retired share read (0, 0)."""
    entries = noise_fake(reg, marked=10**6)
    live = len([e for e in reg.files[DOC]["requirements"] if not e.get("removed")])
    assert rules.retired_share(reg.files[DOC]) == (0, 0)
    assert rules.noise_share(reg.files[DOC]) == (len(entries), live) and len(entries) == live

    assert [m for m in reasons(reg, index) if "not-a-requirement (" in m] == [
        f"DOC: {live} of {live} live entries are not-a-requirement (100%), over 50% of the "
        "document; that much noise needs a noise record with approved_by user in "
        "conformance/policy.yaml"]


def test_a_noise_record_lifts_the_limit_and_is_handled_like_a_retirement(reg, index):
    entries = noise_fake(reg)
    reg.noise.append({"ref": DOC, "reason": "An appendix of headings the extractor read."})
    assert any("noise record for DOC needs approved_by: user" in m for m in reasons(reg, index))

    reg.noise[0]["approved_by"] = "user"
    assert not [m for m in reasons(reg, index) if "not-a-requirement (" in m or "noise rec" in m]

    for entry in entries[:15]:
        register.mark(reg, entry["id"], status="candidate", reason=None)
    assert any("DOC: noise record is not needed" in m for m in reasons(reg, index))

    reg.noise.append({"ref": "NOPE", "reason": "No such document here.", "approved_by": "user"})
    assert any("noise record for unknown document NOPE" in m for m in reasons(reg, index))


def test_half_noise_and_a_short_document_are_within_the_limit(reg, index):
    noise_fake(reg, count=7, marked=10**6)
    assert rules.noise_share(reg.files[DOC])[0] == 10, "the floor: TRIAGE_DOC_FLOOR"
    assert not [m for m in reasons(reg, index) if "not-a-requirement (" in m]


def test_exactly_half_noise_passes_and_one_more_fails(reg, index):
    entries = _many_entries(reg, 37)
    live = len(reg.files[DOC]["requirements"])
    half = live // 2
    for entry in entries[:half]:
        register.mark(reg, entry["id"], status="not-a-requirement", reason="A heading.")
    assert not [m for m in reasons(reg, index) if "not-a-requirement (" in m]

    register.mark(reg, entries[half]["id"], status="not-a-requirement", reason="A heading.")
    assert [m for m in reasons(reg, index) if "not-a-requirement (" in m]


def test_noise_and_retired_together_cannot_pass_under_each_limit(reg, index):
    """Each noise mark shrinks the base of the retired share, so 34 noise and 10 retired of 69
    live entries pass both limits apart while setting aside two thirds of a document."""
    entries = _many_entries(reg, 40)
    live = len(entries)
    noise = live // 2 - 3
    for entry in entries[:noise]:
        register.mark(reg, entry["id"], status="not-a-requirement", reason="A heading.")
    for entry in entries[noise:noise + 2]:
        register.mark(reg, entry["id"], status="not-applicable", reason="Binds nobody here.")
    assert not [m for m in reasons(reg, index) if "set aside" in m]

    for entry in entries[noise + 2:noise + 9]:
        register.mark(reg, entry["id"], status="not-applicable", reason="Binds nobody here.")
    message = f"{noise} noise and 9 retired entries set aside"
    assert any(message in m for m in reasons(reg, index))

    reg.retirements.append({"ref": DOC, "approved_by": "user",
                            "reason": "Reviewed: mostly front matter and outside duties."})
    assert not [m for m in reasons(reg, index) if "set aside" in m or "not needed" in m]


def test_a_work_item_cannot_close_on_noise(reg):
    entry = _many_entries(reg, 1)[0]
    register.mark(reg, entry["id"], status="not-a-requirement", reason="A heading.")
    assert rules.unresolved_at_close(None, entry)


def test_the_fake_scripted_loop_of_marks_cannot_retire_a_document_without_a_record(reg, index):
    """The fake: the per-document cap counted `triaged_by` only, and `mark --status` strips
    it, so a loop of `rmf conformance mark --status not-applicable` retired a document
    uncapped. The share is read from the statuses, however they were set."""
    entries = _many_entries(reg, 30)
    for entry in entries[:20]:
        register.mark(reg, entry["id"], status="not-applicable", reason="Scripted away.")
    assert not any(e.get("triaged_by") for e in entries)

    found = reasons(reg, index)
    assert [m for m in found if "are retired (" in m] == [
        f"DOC: 20 of {len(entries)} requirements are retired ({rules.RETIRED}; "
        f"{20 / len(entries):.0%}), over 25% of the document; "
        "retiring that much of a document needs a retirements record with approved_by user in "
        "conformance/policy.yaml"]

    reg.retirements.append({"ref": DOC, "reason": "Mostly about system retirement, which the "
                            "run never does."})
    assert any("retirements record for DOC needs approved_by: user" in m
               for m in reasons(reg, index))

    reg.retirements[0]["approved_by"] = "user"
    assert reasons(reg, index) == []

    for entry in entries[:15]:
        register.mark(reg, entry["id"], status="candidate", reason=None)
    assert any("DOC: retirements record is not needed" in m for m in reasons(reg, index))


def test_a_pattern_sample_must_match_and_exist(reg, index):
    triaged(reg, {**PATTERN, "sample": [f"REQ-{DOC}-0001", f"REQ-{DOC}-0099"]})

    found = reasons(reg, index)

    assert any(f"sample REQ-{DOC}-0001 does not match" in m for m in found)
    assert any(f"sample REQ-{DOC}-0099 is not a live entry" in m for m in found)


def test_the_fake_work_item_binding_nothing_is_an_error(reg, index):
    """The fake: 30 of 41 open work items bound nothing, so closing one needed only closed_by."""
    fx.entry(reg).pop("work_item")

    assert reasons(reg, index) == ["WI-01 (open) binds no register entry and no FW-TASK-002 "
                                   "waiver; set work_item on the entries it closes, or scope: "
                                   "internal with the reason"]

    reg.waivers.append({"task": "P-18", "field": "outputs", "entity": "ART-REG",
                        "work_item": "WI-01"})
    assert reasons(reg, index) == [], "a pin field is not an entry; its waiver binds the item"


CLOSED = "WI-01 is closed, but bound entries are candidate, deferred, not-applicable, or carry " \
         f"no evidence that judges strong: REQ-{DOC}-0001"


@pytest.mark.parametrize("state", [
    {"status": "candidate"},
    {"status": "deferred", "reason": "Later."},
    {"status": "not-applicable", "reason": "The run never registers anything, it says here."},
    {"status": "partial", "reason": "Registered, not before use."},
    {"status": "partial", "reason": "Cited.", "evidence": [{"kind": "citation", "target": "P-18"}]},
    {"status": "covered", "evidence": [{"kind": "prose", "target": "playbooks/P/P-18.md"}]},
    {"status": "partial", "reason": "Warned.", "evidence": [
        {"kind": "rule", "target": "WARN-001", "asserts": ASSERTS}]},
    {"status": "partial", "reason": "Not listed.", "evidence": [
        {"kind": "rule", "target": "AODM-001", "asserts": ASSERTS}]},
], ids=["candidate", "deferred", "not-applicable", "no evidence", "citation only", "prose only",
        "a rule that only warns", "a rule that does not list the entry"])
def test_the_fake_closure_over_an_undecided_entry_is_an_error(reg, index, state):
    """The fakes: a closed work item passed when its entries were not-applicable with any
    reason, or partial on a citation that cannot fail, or (the p10 review) partial on rule
    evidence that judged weak or denied, because closure tested the evidence kind, not the
    verdict."""
    reg.work_items["WI-01"].update(status="closed", closed_by="commit abc1234: registration")
    fx.entry(reg).update(state)

    assert CLOSED in reasons(reg, index)


def test_closing_a_work_item_needs_evidence_that_can_fail_on_its_entries(reg, index):
    reg.work_items["WI-01"].update(status="closed", closed_by="commit abc1234: registration")
    fx.entry(reg).update(status="partial", reason="Registered, not before use.",
                         evidence=[{"kind": "citation", "target": "P-18"},
                                   {"kind": "rule", "target": "REG-001", "asserts": ASSERTS}])

    assert reasons(reg, index) == []


def test_bindings_name_one_entry_each_and_bind_writes_the_work_item(repo, reg, index):
    reg.bindings = [{"work_item": "WI-01", "ref": DOC, "phrase": "register the system"},
                    {"work_item": "WI-01", "ref": DOC, "phrase": "no such phrase anywhere"}]
    found = reasons(reg, index)
    assert any("'no such phrase anywhere' matches 0 live entries, not one" in m for m in found)

    reg.bindings[1] = {"work_item": "WI-02", "ref": DOC, "phrase": "register the system"}
    assert any("is already bound to WI-01; an entry carries one work item" in m
               for m in reasons(reg, index))

    fx.entry(reg).pop("work_item")
    reg.bindings.pop()
    assert any("carries work item None; run rmf conformance bind" in m
               for m in reasons(reg, index))

    marks = register.binding_marks(reg)
    assert marks == {f"REQ-{DOC}-0001": {"work_item": "WI-01"}}
    for ident, fields in marks.items():
        register.mark(reg, ident, **fields)
    assert reasons(reg, index) == []
    assert register.binding_marks(reg) == {}, "bind is idempotent"


def test_an_internal_work_item_binds_nothing_by_design(reg, index):
    assert reg.work_items["WI-02"]["scope"] == "internal"
    assert not any("WI-02" in m for m in reasons(reg, index))


# --- FW-REQ-005 --------------------------------------------------------------------------


def accept(repo):
    reg = fx.load(repo)
    hashes = {ref: register.text_hash(register.text_of(repo, fx.INDEX[ref]))
              for ref in (DOC, TIER1)}
    (repo / register.TEXT_HASHES).write_text(register.render_text_hashes(hashes))
    return reg


def test_extraction_is_idempotent(repo, index):
    before = (repo / register.requirements_path(DOC)).read_bytes()

    fx.extract(repo)

    assert (repo / register.requirements_path(DOC)).read_bytes() == before
    assert sync(repo, index) == []


def test_fw_req_005_fires_when_a_source_document_changes(repo, index):
    text = repo / f"references/text/{DOC}.md"
    text.write_text(text.read_text().replace("Will retire", "Must decommission"))

    found = sync(repo, index, DOC)

    assert any("the text differs from the reviewed one (hash)" in m for m in found)
    assert any("differs from a fresh extraction" in m and "1 new" in m
               and f"1 no longer in the source (REQ-{DOC}-0002)" in m for m in found)


def test_the_fake_edit_outside_every_extracted_unit_is_noticed(repo, index):
    """The fake: a change the extractor does not see left the register identical."""
    text = repo / f"references/text/{DOC}.md"
    text.write_text(text.read_text().replace("Appendix A references", "Appendix A refs"))
    fx.extract(repo)

    found = sync(repo, index, DOC)

    assert found == [f"{DOC}: the text differs from the reviewed one (hash); read the change, "
                     "re-review, then rmf conformance accept-text"]
    accept(repo)
    assert sync(repo, index, DOC) == []


def test_a_vanished_statement_stays_as_removed_after_rerun(repo, index):
    text = repo / f"references/text/{DOC}.md"
    text.write_text(text.read_text().split("b. Will retire")[0] + "The end.\n")
    fx.extract(repo)
    accept(repo)
    doc = fx.load(repo).files[DOC]

    assert sync(repo, index, DOC) == []
    assert (doc["requirements"][1]["id"], doc["requirements"][1].get("removed")) == (
        f"REQ-{DOC}-0002", True)


def test_a_register_edited_by_hand_is_noticed(repo, index):
    path = repo / register.requirements_path(DOC)
    path.write_text(path.read_text().replace("retire", "dispose of"))

    assert any("differs" in m for m in sync(repo, index, DOC))


def test_a_reviewed_entry_whose_statement_changed_stays_flagged_after_rerun(repo, index):
    reg = fx.load(repo)
    register.mark(reg, f"REQ-{DOC}-0002", status="partial", reason="Done in part.")
    fx.write(repo, reg)
    text = repo / f"references/text/{DOC}.md"
    text.write_text(text.read_text().replace("Will retire the system when its authorization "
                                             "ends", "Will retire the system when its "
                                             "authorization ends or lapses"))
    fx.extract(repo)
    accept(repo)

    entry = fx.entry(fx.load(repo), 2)
    assert entry["needs_review"] is True and "lapses" in entry["statement"]
    assert any("clear needs_review" in m for m in sync(repo, index, DOC))


def test_a_scope_that_yields_too_little_fails_unless_sparse(repo, index):
    reg = fx.load(repo)
    text = repo / f"references/text/{DOC}.md"
    text.write_text(text.read_text().replace("<!-- page 2 -->", "<!-- page 2 -->\n\nFiller.\n\n"
                                             "<!-- page 3 -->\n\n<!-- page 4 -->\n\n<!-- page 5 -->"
                                             "\n\n<!-- page 6 -->\n\n<!-- page 7 -->\n"))
    reg.sources[DOC]["scopes"].append({"pages": [3, 7], "note": "Empty pages"})
    body = '      - {pages: [1, 1], note: "The body"}\n'
    assert fx.SOURCES.count(body) == 2
    (repo / register.SOURCES).write_text(fx.SOURCES.replace(
        body, body + '      - {pages: [3, 7], note: "Empty pages"}\n', 1))
    fx.extract(repo)
    accept(repo)
    assert any("yields 0 entries, under 1" in m for m in sync(repo, index, DOC))

    (repo / register.SOURCES).write_text((repo / register.SOURCES).read_text().replace(
        'note: "Empty pages"}', 'note: "Empty pages", sparse: "Blank leaves in the scan."}'))
    assert sync(repo, index, DOC) == []


def test_a_stale_scope_fails_loudly(repo, index):
    (repo / f"references/text/{DOC}.md").unlink()

    assert "cannot read its text" in sync(repo, index, DOC)[0]


def test_the_reference_list_must_match_the_document():
    reg = register.load(REPO_ROOT)
    index = register.index_entries(REPO_ROOT)
    reg.reference_list = [r for r in reg.reference_list if "3020.04" not in r["document"]]
    reg.reference_list.append({"document": "DoD Instruction 9999.99", "disposition": "excluded",
                               "reason": "Not printed in the instruction."})

    found = rules._reference_list_sync(REPO_ROOT, reg, index)

    assert "no disposition for DoD Directive 3020.04" in found[0].message
    assert "not printed: DoD Instruction 9999.99" in found[0].message


def test_every_listed_document_has_a_disposition_with_a_reason_or_a_ref():
    listed = register.load(REPO_ROOT).reference_list

    assert len(listed) == 36
    assert all(i.get("ref") or len(i["reason"]) > 10 for i in listed)


# --- FW-TASK-002 -------------------------------------------------------------------------


@pytest.fixture
def real_reg():
    return register.load(REPO_ROOT)


def contract(framework, reg, repo=REPO_ROOT):
    return rules.contract(repo, framework, reg)


def test_fw_task_002_fires_when_a_task_loses_an_input(framework, real_reg):
    framework.index("tasks")["S-6"].data["inputs"].remove("ART-RA")

    assert messages(contract(framework, real_reg)) == ["S-6 inputs: lacks ART-RA"]


def test_an_input_may_move_to_consults(framework, real_reg):
    task = framework.index("tasks")["S-6"].data
    task["inputs"].remove("ART-RA")
    task["consults"] = ["ART-RA"]

    assert contract(framework, real_reg) == []


def test_a_lost_output_and_a_lost_role_fire(framework, real_reg):
    tasks = framework.index("tasks")
    tasks["A-2"].data["outputs"].remove("ART-SAP")
    tasks["S-6"].data["raci"]["R"].remove("PER-AODR")
    tasks["S-6"].data["raci"]["A"] = "PER-PM"

    found = messages(contract(framework, real_reg))

    assert "A-2 outputs: lacks ART-SAP" in found
    assert "S-6 primary: lacks PER-AO|PER-AODR" in found


def test_a_supporting_role_may_hold_any_raci_letter(framework, real_reg):
    raci = framework.index("tasks")["S-5"].data["raci"]
    raci["C"].remove("PER-CISO")
    raci["I"] = ["PER-CISO"]

    assert contract(framework, real_reg) == []


def test_closing_a_gap_makes_its_waiver_an_error(framework, real_reg):
    """The rule tightens: p11 cannot close a gap and leave the waiver behind."""
    framework.index("tasks")["M-1"].data["outputs"].append("ART-SSP")

    assert messages(contract(framework, real_reg)) == [
        "waiver no longer needed: M-1 outputs: lacks ART-SSP"]


def test_a_forward_ordered_input_is_a_task_scoped_omission_with_a_rationale(real_reg):
    """FW-IO-001 forbids ART-RA as an input before P-14 produces it, so these waivers can never
    close through a work item; each carries a rationale instead and names no work item."""
    waivers = register.read(REPO_ROOT, register.NIST_WAIVERS, "nist-waivers", [])["waivers"]
    scoped = {(w["task"], w["entity"]) for w in waivers if "rationale" in w}

    assert {("P-3", "ART-RA"), ("P-7", "ART-RA"), ("C-1", "ART-CAT")} <= scoped
    assert all("work_item" not in w for w in waivers if "rationale" in w)


def test_every_work_item_waiver_names_an_open_item_and_the_cloud_omission_has_one(real_reg):
    waivers = register.read(REPO_ROOT, register.NIST_WAIVERS, "nist-waivers", [])["waivers"]
    words = register.read(REPO_ROOT, register.NIST_VOCABULARY, "nist-vocabulary", [])
    cloud = next(p for p in words["phrases"] if p["phrase"].startswith("plans to use cloud"))

    assert all(real_reg.work_items[w["work_item"]]["status"] == "open"
               for w in waivers if "work_item" in w)
    assert cloud["work_item"] == "WI-12" and "omit" in cloud
    assert not any("ART-MISSION" in str(p) for p in words["phrases"] + words["planned"])


def test_a_waiver_on_a_closed_work_item_fails(framework, real_reg):
    waivers = register.read(REPO_ROOT, register.NIST_WAIVERS, "nist-waivers", [])["waivers"]
    item = next(w["work_item"] for w in waivers if "work_item" in w)
    real_reg.work_items[item]["status"] = "closed"

    assert any("is not an open work item" in m for m in messages(contract(framework, real_reg)))


def small_pin(tmp_path, **changes):
    conformance = tmp_path / "conformance"
    shutil.copytree(REPO_ROOT / "conformance", conformance,
                    ignore=shutil.ignore_patterns("requirements"))
    for name, (old, new) in changes.items():
        path = conformance / f"{name.replace('_', '-')}.yaml"
        text = path.read_text(encoding="utf-8")
        assert old in text
        path.write_text(text.replace(old, new), encoding="utf-8")
    return tmp_path


def test_an_unknown_phrase_fails(framework, real_reg, tmp_path):
    repo = small_pin(tmp_path, nist_tasks=("organizational charts", "organizational pie charts"))

    assert "no vocabulary entry for 'organizational pie charts'" in messages(
        contract(framework, real_reg, repo))


def test_a_vocabulary_entry_for_an_unknown_entity_fails(framework, real_reg, tmp_path):
    repo = small_pin(tmp_path,
                     nist_vocabulary=('entities: ["ART-CMP"]', 'entities: ["ART-CMPP"]'))

    assert any("maps to unknown entity ART-CMPP" in m for m in messages(
        contract(framework, real_reg, repo)))


def test_a_planned_entity_that_arrives_must_leave_planned(framework, real_reg):
    words = register.read(REPO_ROOT, register.NIST_VOCABULARY, "nist-vocabulary", [])
    planned = words["planned"][0]["id"]
    framework.entities.append(Entity("artifacts", {"id": planned},
                                     Location("framework/artifacts.yaml", 1)))

    assert any(f"planned entity {planned} now exists" in m for m in messages(
        contract(framework, real_reg)))


def test_an_sdlc_disagreement_fails(framework, real_reg):
    task = framework.index("tasks")["A-6"]
    citation = next(c for c in task.data["citations"] if c.get("section") == "TASK A-6")
    citation["note"] = "SDLC phase: New – Disposal; Existing – Operations/Maintenance."

    found = messages(contract(framework, real_reg))

    assert len(found) == 1 and found[0].startswith("A-6: TASK citation note says SDLC")


def test_all_47_tasks_are_compared(framework):
    pin = register.read(REPO_ROOT, register.NIST_TASKS, "nist-tasks", [])

    assert len(pin["tasks"]) == 47
    assert {t["id"] for t in pin["tasks"]} == set(framework.index("tasks"))


# --- phase wiring and fork safety --------------------------------------------------------


def test_p10_is_a_phase_with_a_ci_step():
    assert "p10" in PHASES
    assert any(s.phase == "p10" and "FW-REQ-005" in s.rules for s in ci.STEPS)
    for name in ("release", "fork"):
        assert ci.unimplemented_phases(resolve(REPO_ROOT, name)) == []


def test_the_p5_validate_step_stands_down_for_p10():
    profile = Profile("p10", frozenset(PHASES))
    run = [s.name for s in ci.STEPS if s.phase and profile.includes(s.phase)
           and not (s.unless and profile.includes(s.unless))]

    assert sum(n.startswith("rmf validate") for n in run) == 1


def test_a_fork_without_examples_or_readme_keeps_a_valid_register(tmp_path):
    """A fork deletes examples/ and rewrites README.md; every FW rule still passes there."""
    for path in REPO_ROOT.iterdir():
        if path.name not in ("examples", "README.md", ".git", ".venv"):
            (tmp_path / path.name).symlink_to(path)
    fork = Profile("fork", frozenset(PHASES), examples=False, agent_severity=None)

    result = validate(tmp_path / "framework", tmp_path, fork)

    assert result.ok, [f.render() for f in result.findings][:5]
    assert "FW-REQ-003" in result.rules_run


def test_conformance_stays_outside_the_upstream_hash():
    from rmf_tool.run import upstream_hash

    assert not any(glob.startswith("conformance") for glob in upstream_hash.UNION_GLOBS)
    assert not [p for p in upstream_hash.expand(REPO_ROOT, upstream_hash.UNION_GLOBS)
                if p.startswith("conformance")]


def test_the_resolver_stub_agrees_with_the_real_resolver_on_a_real_citation():
    """The synthetic tests resolve citations with _Resolver; this keeps it honest."""
    real = Resolver(REPO_ROOT, refs.load_index(REPO_ROOT), strict=True)
    entry = next(e for _, e in register.load(REPO_ROOT).live())

    assert real.resolve(entry["citation"]).status != "error"


# --- promotion ---------------------------------------------------------------------------


def promote(repo, reg, page=1, anchor="The owner", reason="The lead-in names who the lettered "
            "obligations under it bind.", **options):
    return register.promote(reg, DOC, register.text_of(repo, fx.INDEX[DOC]), page, anchor, reason,
                            **options)


def test_a_promoted_rejection_becomes_a_live_entry_that_survives_re_extraction(repo, index):
    """Extraction is a first pass (plan, Nov 1): triage promotes what it rejected."""
    reg = fx.load(repo)
    assert [r["text"] for r in reg.files[DOC]["rejected"]] == ["The owner:"]

    made = promote(repo, reg)
    fx.write(repo, reg)
    fx.extract(repo)
    after = fx.load(repo)
    entry = after.entry(made["id"])

    assert made["id"] == f"REQ-{DOC}-0004" and made["kind"] == register.PROMOTED_KIND
    assert entry == {"id": made["id"], "citation": {"ref": DOC, "page": 1, "anchor": "The owner:"},
                     "kind": "promoted", "locator": "2.1", "context": "",
                     "statement": "The owner:", "status": "candidate",
                     "promoted": {"reason": made["promoted"]["reason"]}}
    assert after.files[DOC]["rejected"] == []
    assert shape(repo, after, index) == [], "FW-REQ-001 resolves the citation like any other"
    assert sync(repo, index, DOC) == [], "FW-REQ-005 sees a current register"
    assert fx.extract(repo) is None and fx.load(repo).entry(made["id"]) == entry, "idempotent"


def test_a_promoted_entry_whose_passage_changes_is_flagged_and_never_dropped(repo, index):
    reg = fx.load(repo)
    made = promote(repo, reg)
    fx.write(repo, reg)
    text = repo / f"references/text/{DOC}.md"
    text.write_text(text.read_text().replace("The owner:", "The system owner:"))
    fx.extract(repo)
    accept(repo)
    after = fx.load(repo)
    entry = after.entry(made["id"])

    assert entry["needs_review"] is True and not entry.get("removed")
    assert entry["statement"] == "The owner:"
    assert any(f"re-review entries whose statement or pairing changed, then clear needs_review: "
               f"{made['id']}" in m for m in sync(repo, index, DOC))
    found = shape(repo, after, index)
    assert any(m.startswith(f"{made['id']}: ") and "anchor" in m for m in found), \
        "FW-REQ-001 fails the citation until the reviewer resolves it"


def test_a_passage_the_extractor_read_as_context_can_be_promoted_and_a_bad_anchor_cannot(repo,
                                                                                         index):
    reg = fx.load(repo)

    made = promote(repo, reg, page=2, anchor="Appendix A references",
                   reason="The appendix lists what the register reads.")

    assert made["statement"] == "Appendix A references, which the register never reads."
    assert made["citation"] == {"ref": DOC, "page": 2, "anchor": "Appendix A references, which "
                                "the register never reads."}
    assert made["locator"] == ""
    with pytest.raises(register.MarkError, match="in no rejection and no paragraph"):
        promote(repo, reg, page=1, anchor="nowhere on this page")
    with pytest.raises(register.MarkError, match=f"REQ-{DOC}-0003 already states that passage"):
        promote(repo, reg, page=1, anchor="must approve every registration")
    with pytest.raises(register.MarkError, match="no requirements file"):
        register.promote(reg, "NOPE", "", 1, "x", "y")


GLOSSARY = ("MDA A designated individual with overall responsibility. The MDA will establish "
            "procedures for its programs. The MDA will report progress each quarter. release")


@pytest.fixture
def glossary(repo):
    """Page 2, which the scopes exclude, holds a two-column glossary read line by line."""
    text = repo / f"references/text/{DOC}.md"
    text.write_text(text.read_text().replace(
        "Appendix A references, which the register never reads.", GLOSSARY))
    accept(repo)
    return repo


def test_sentence_takes_one_sentence_of_a_glued_glossary_paragraph(glossary, index):
    reg = fx.load(glossary)

    made = promote(glossary, reg, page=2, anchor="will establish procedures", sentence=True)
    last = promote(glossary, reg, page=2, anchor="report progress each quarter", sentence=True)
    fx.write(glossary, reg)

    assert made["statement"] == "The MDA will establish procedures for its programs."
    assert made["kind"] == register.PROMOTED_KIND and made["locator"] == ""
    assert last["statement"] == "The MDA will report progress each quarter.", "no trailing label"
    assert shape(glossary, fx.load(glossary), index) == [], "FW-REQ-001 finds it in its passage"
    assert sync(glossary, index, DOC) == []


def test_a_promoted_sentence_survives_re_extraction(glossary, index):
    reg = fx.load(glossary)
    made = promote(glossary, reg, page=2, anchor="will establish procedures", sentence=True)
    fx.write(glossary, reg)
    entry = fx.load(glossary).entry(made["id"])

    fx.extract(glossary)

    assert fx.load(glossary).entry(made["id"]) == entry
    assert sync(glossary, index, DOC) == []


def test_a_promoted_sentence_whose_passage_changes_is_flagged(glossary, index):
    reg = fx.load(glossary)
    made = promote(glossary, reg, page=2, anchor="will establish procedures", sentence=True)
    fx.write(glossary, reg)
    text = glossary / f"references/text/{DOC}.md"
    text.write_text(text.read_text().replace("will establish procedures", "will set procedures"))

    fx.extract(glossary)
    entry = fx.load(glossary).entry(made["id"])

    assert entry["needs_review"] is True and not entry.get("removed")


@pytest.mark.parametrize("anchor, count", [
    ("overall responsibility. The MDA will establish", 0), ("The MDA will", 2)])
def test_sentence_refuses_an_anchor_outside_one_sentence(glossary, anchor, count):
    reg = fx.load(glossary)
    before = copy.deepcopy(reg.files[DOC])

    with pytest.raises(register.MarkError, match=f"is in {count} sentences of that paragraph"):
        promote(glossary, reg, page=2, anchor=anchor, sentence=True)

    assert reg.files[DOC] == before


def test_a_sentence_of_a_rejection_leaves_the_rest_rejected(repo, index):
    text = repo / f"references/text/{DOC}.md"
    paragraph = "The register holds records. The register lists owners."
    results = "Assessors may reuse prior results.\n"
    text.write_text(text.read_text().replace(results, f"{results}\n{paragraph}\n"))
    fx.extract(repo)
    accept(repo)
    reg = fx.load(repo)

    made = promote(repo, reg, anchor="lists owners", sentence=True)
    fx.write(repo, reg)

    assert made["statement"] == "The register lists owners."
    assert paragraph in [r["text"] for r in fx.load(repo).files[DOC]["rejected"]]
    assert sync(repo, index, DOC) == [], "a re-extraction finds the same rejection"


def test_promote_sentence_command(glossary, monkeypatch):
    monkeypatch.setattr("rmf_tool.cli.repo_root", lambda: glossary)
    monkeypatch.setattr("rmf_tool.conformance.register.index_entries", lambda root: fx.index())
    base = ["conformance", "promote", DOC, "--page", "2", "--reason", "It directs the MDA."]

    none = CliRunner().invoke(app, [*base, "--anchor", "responsibility. The MDA", "--sentence"])
    many = CliRunner().invoke(app, [*base, "--anchor", "The MDA will", "--sentence"])
    made = CliRunner().invoke(app, [*base, "--anchor", "will establish", "--sentence"])
    whole = CliRunner().invoke(app, [*base, "--anchor", "report progress"])

    assert made.exit_code == 0, made.output
    assert made.stdout.strip().endswith(": The MDA will establish procedures for its programs.")
    assert none.exit_code == 2 and "is in 0 sentences" in none.output
    assert many.exit_code == 2 and "is in 2 sentences" in many.output
    assert whole.exit_code == 0 and whole.stdout.strip().endswith(f": {GLOSSARY}")


@pytest.mark.parametrize("sentence, expected", [
    ("The MDA will set procedures. program manager", "The MDA will set procedures."),
    ("Use tools, e.g. scanners", "Use tools, e.g. scanners"),
    ("see Paragraph 3.2. of this issuance", "see Paragraph 3.2. of this issuance"),
    ("The MDA will set procedures.", "The MDA will set procedures."),
])
def test_a_trailing_label_is_dropped_and_an_abbreviation_is_not(sentence, expected):
    assert extract.without_trailing_label(sentence) == expected


def test_an_entry_that_loses_a_page_number_keeps_its_id_and_its_review():
    """A footer dropped from the front of a statement: the shorter statement is the same one."""
    old = {"id": f"REQ-{DOC}-0001", "citation": {"ref": DOC, "page": 1, "anchor": "3"},
           "kind": "modal", "locator": "4.1", "context": "", "status": "not-applicable",
           "reason": "Product behaviour, no duty.",
           "statement": "3 Users can search for systems in eMASS."}
    new = extract.Item("modal", 2, "Users can search for systems in eMASS.", "4.1", "",
                       anchor="Users can search")

    entries, changes = register.reconcile(DOC, [old], [new], [])

    assert [e["id"] for e in entries] == [old["id"]] and changes.removed == []
    assert changes.changed == [old["id"]]
    assert entries[0]["status"] == "not-applicable" and entries[0]["needs_review"] is True
    assert entries[0]["reason"] == old["reason"]


def test_a_shorter_statement_inside_two_old_ones_is_not_guessed():
    olds = [{"id": f"REQ-{DOC}-000{n}", "citation": {"ref": DOC, "page": 1, "anchor": str(n)},
             "kind": "modal", "locator": "4.1", "context": "", "status": "candidate",
             "statement": f"{n} Users can search for systems in eMASS."} for n in (1, 2)]
    new = extract.Item("modal", 2, "Users can search for systems in eMASS.", "4.2", "",
                       anchor="Users can search")

    entries, changes = register.reconcile(DOC, olds, [new], [])

    assert len(changes.added) == 1 and len(changes.removed) == 2


@pytest.mark.parametrize("pattern, message", [
    ("no footer reads like this", "matches no page-closing paragraph"),
    ("[", "is not a regex"),
])
def test_a_footer_pattern_that_cannot_work_is_a_finding(repo, index, pattern, message):
    reg = fx.load(repo)
    reg.sources[DOC]["footers"] = [{"pattern": pattern, "reason": "The page footer of the test."}]

    assert any(message in m for m in shape(repo, reg, index))


def containment(old_statement, new_statement, *, page=1, new_page=1, **old_fields):
    old = {"id": f"REQ-{DOC}-0001", "citation": {"ref": DOC, "page": page, "anchor": "3"},
           "kind": "modal", "locator": "4.1", "context": "", "status": "candidate",
           "statement": old_statement, **old_fields}
    new = extract.Item("modal", new_page, new_statement, "4.2", "", anchor="words")
    return register.reconcile(DOC, [old], [new], [])


SHORT = "The AO must sign."


@pytest.mark.parametrize("dead", [f"3 Users can search for systems. {SHORT}", f"3 {SHORT}"])
def test_a_removed_entry_is_never_resurrected_by_containment(dead):
    """A short new sentence inside a dead paragraph took its ID and its review."""
    entries, changes = containment(dead, SHORT, page=9, new_page=9, removed=True,
                                   status="not-applicable", reason="Product behaviour.")

    assert len(changes.added) == 1 and entries[0].get("removed")
    assert entries[1]["statement"] == SHORT and entries[1]["status"] == "candidate"


def test_a_short_sentence_inside_a_long_old_one_is_a_new_entry():
    long = f"{SHORT} " + " ".join(f"The owner will file record {n}." for n in range(9))
    assert len(containment(long, SHORT)[1].added) == 1


@pytest.mark.parametrize("new_page, kept", [(1, True), (2, True), (3, False)])
def test_containment_holds_on_the_same_or_an_adjacent_page(new_page, kept):
    changes = containment(f"3 {SHORT}", SHORT, new_page=new_page)[1]
    assert (changes.added == []) is kept


def test_a_footer_pattern_refuses_a_paragraph_that_states_a_duty(repo, index):
    reg = fx.load(repo)
    reg.sources[DOC]["footers"] = [{"pattern": "authorizing official",
                                    "reason": "A pattern that catches a duty by mistake."}]

    assert any("matches a paragraph that states a duty" in m for m in shape(repo, reg, index))


def test_a_promoted_entry_the_extractor_later_finds_keeps_its_id_and_its_mark():
    old = [{"id": f"REQ-{DOC}-0001", "citation": {"ref": DOC, "page": 1, "anchor": "a. Decisions."},
            "kind": "promoted", "locator": "2.1.a", "context": "", "statement": "a. Decisions.",
            "status": "partial", "reason": "r", "promoted": {"reason": "p"}}]
    item = extract.Item("lettered", 1, "a. Decisions.", "2.1.a", "Owners", anchor="a. Decisions.")

    entries, changes = register.reconcile(DOC, old, [item], [])

    assert [(e["id"], e["kind"], e["status"], e["promoted"]) for e in entries] == [
        (f"REQ-{DOC}-0001", "lettered", "partial", {"reason": "p"})]
    assert changes.added == [] and changes.removed == []
