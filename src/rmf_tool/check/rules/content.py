"""Content rules: FACTS-001, SSP-COV-001, SAR-POAM-001, TRACE-001, TRACE-002, HYB-001."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from rmf_tool import baseline as baseline_mod
from rmf_tool.catalog import family
from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope
from rmf_tool.run.model import ASSUMPTIONS_FILE, BASELINE_FILE, FACTS_FILE
from rmf_tool.run.trace import HEADING, PROSE, prose_tokens, strip_generated

SSP_DIR = "artifacts/ssp/controls"
SAR_DIR = "artifacts/sar/results"
POAM_FILE = "artifacts/poam/items.yaml"


def family_records(ctx: Context, directory: str, key: str) -> Iterator[tuple[str, dict]]:
    for path in sorted(ctx.run.path(directory).glob("*.yaml")):
        data = ctx.data(ctx.run.rel(path))
        for item in (data or {}).get(key) or [] if isinstance(data, dict) else []:
            if isinstance(item, dict):
                yield ctx.run.rel(path), item


# --- FACTS-001 --------------------------------------------------------------------------

CATEGORIZATION_APPROVERS = ("PER-AO", "PER-AODR")


def facts_complete(ctx: Context) -> list[RunFinding]:
    run, facts = ctx.run, ctx.facts
    out: list[RunFinding] = []
    active = set(scope.active_tasks(run))
    for fact, writer in run.fact_writers.items():
        if writer not in active:
            continue
        node = facts_mod.get(facts, fact)
        if not isinstance(node, dict):
            out.append(make("FACTS-001", f"fact {fact} not set ({writer} writes it)",
                            FACTS_FILE, None, {writer}))
        elif node.get("set_by_task") != writer:
            out.append(make("FACTS-001", f"fact {fact} set_by_task is "
                            f"{node.get('set_by_task')!r}; {writer} writes it, not another task",
                            FACTS_FILE, None, {writer}))
    # An overlay S-1 cannot apply is C-2's error. FACTS-001 applies from C-3, so the approval
    # reopens there instead of S-1 failing after it (L-0035).
    cat = facts_mod.get(facts, "categorization")
    overlays = cat.get("overlays") if isinstance(cat, dict) else None
    if overlays and isinstance(overlays, list):
        owners = {run.fact_writers.get("categorization", "C-2"),
                  run.fact_writers.get("categorization.approved", "C-3")}
        try:
            tables = baseline_mod.load_tables(run)
        except baseline_mod.BaselineError as exc:
            out.append(make("FACTS-001", str(exc), FACTS_FILE, None, owners))
        else:
            obtained = baseline_mod.obtained_overlays(run)
            for name in overlays:
                problem = baseline_mod.overlay_problem(tables, str(name), obtained)
                if problem:
                    out.append(make("FACTS-001", problem, FACTS_FILE, None, owners))
    approval = facts_mod.get(facts, "categorization.approved")
    if isinstance(approval, dict) and approval.get("value") is not True:
        approver = run.fact_writers.get("categorization.approved", "C-3")
        selector = run.fact_writers.get("baseline_id", "S-1")
        out.append(make("FACTS-001", "categorization is not approved "
                        "(categorization.approved.value must be true before S-1)",
                        FACTS_FILE, None, {approver, selector}))
    # CNSSI 1253 Section 2.1 step 4: the AO's or the AO's designated representative's approval.
    by = approval.get("approved_by") if isinstance(approval, dict) else None
    if isinstance(approval, dict) and approval.get("value") is True \
            and by not in CATEGORIZATION_APPROVERS:
        out.append(make("FACTS-001", f"categorization is approved by {by}, not the AO or the "
                        "AO's designated representative", FACTS_FILE, None,
                        {run.fact_writers.get("categorization.approved", "C-3")}))
    fact_id = facts_mod.value(facts, "baseline_id")
    base = baseline_mod.load(run)
    if fact_id and base and base.get("baseline_id") != fact_id:
        out.append(make("FACTS-001", f"baseline_id fact {fact_id!r} differs from baseline.json "
                        f"{base.get('baseline_id')!r}", FACTS_FILE, None,
                        {run.fact_writers.get("baseline_id", "S-1")}))
    return out


# --- coverage ---------------------------------------------------------------------------

def ssp_coverage(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    if baseline_mod.load(run) is None:
        return [make("SSP-COV-001", "no baseline.json; S-1 runs `rmf baseline resolve`",
                     BASELINE_FILE, None, {"S-4"})]
    stated = {item.get("control_id") for _, item in family_records(ctx, SSP_DIR, "controls")}
    return [make("SSP-COV-001", f"baseline control {cid} has no SSP statement in the security "
                 "and privacy plan",
                 f"{SSP_DIR}/{family(cid)}.yaml")
            for cid in baseline_mod.control_ids(run) if cid not in stated]


def inconsequential(finding: dict[str, Any]) -> bool:
    """A finding the system owner decided presents no significant risk stays in the SAR and
    needs no POA&M item or risk (SP 800-37r2 Task A-5); ASMT-006 judges the decision."""
    triage = finding.get("triage")
    return isinstance(triage, dict) and triage.get("action") == "inconsequential"


def sar_poam(ctx: Context) -> list[RunFinding]:
    poam = ctx.data(POAM_FILE)
    linked = {i.get("finding_ref") for i in (poam or {}).get("items") or []
              if isinstance(i, dict)} if isinstance(poam, dict) else set()
    out = []
    for _, f in family_records(ctx, SAR_DIR, "findings"):
        if f.get("status") != "closed" and f.get("id") not in linked \
                and not inconsequential(f):
            cid = str(f.get("control_id", ""))
            out.append(make("SAR-POAM-001", f"SAR finding {f.get('id')} ({cid}, "
                            f"{f.get('status')}) has no POA&M item", POAM_FILE,
                            family=family(cid) if cid else None))
    return out


# --- trace ------------------------------------------------------------------------------

def sections(body: str, first_line: int) -> Iterator[tuple[str, int, list[str]]]:
    """(heading, line, prose lines) per heading-delimited section of generated-free text."""
    heading, line, lines = "(preamble)", first_line, []
    for lineno, text in enumerate(strip_generated(body).splitlines(), start=first_line):
        if m := HEADING.match(text):
            yield heading, line, lines
            heading, line, lines = m.group(2), lineno, []
        elif text.strip():
            lines.append(text)
    yield heading, line, lines


def trace_present(ctx: Context) -> list[RunFinding]:
    out: list[RunFinding] = []
    for rel, doc in ctx.docs.items():
        if doc.data is None:
            continue
        for heading, line, prose in sections(doc.body, doc.body_line):
            if prose and not any(PROSE.search(p) for p in prose):
                out.append(make("TRACE-001", f"section {heading!r} has no trace token "
                                "([[INT-…]], [[ASM-…]], [[product/…]] or [[ART-…]])",
                                rel, line))
    poam = ctx.data(POAM_FILE)
    for item in (poam or {}).get("items") or [] if isinstance(poam, dict) else []:
        if isinstance(item, dict) and not item.get("sources"):
            out.append(make("TRACE-001", f"POA&M item {item.get('id')} has no sources",
                            POAM_FILE))
    return out


def _sources(data: Any) -> Iterator[str]:
    if isinstance(data, dict):
        for key, val in data.items():
            if key in ("sources", "basis") and isinstance(val, list):
                yield from (str(v) for v in val)
            else:
                yield from _sources(val)
    elif isinstance(data, list):
        for item in data:
            yield from _sources(item)


def trace_resolves(ctx: Context) -> list[RunFinding]:
    run, res = ctx.run, ctx.resolver
    out: list[RunFinding] = []

    def check(token: str, rel: str, line: int | None = None,
              owners: set[str] | None = None) -> None:
        problem = res.problem(token)
        if problem:
            out.append(make("TRACE-002", problem, rel, line, owners))

    for rel, doc in ctx.docs.items():
        if doc.data is None:
            continue
        for token in doc.data.get("sources") or []:
            check(str(token), rel, 1)
        for token, line in prose_tokens(strip_generated(doc.body), doc.body_line):
            check(token, rel, line)
    for aid in run.artifacts:
        for rel, schema in run.data_files(aid):
            if schema is None or rel == BASELINE_FILE:
                continue
            for token in _sources(ctx.data(rel)):
                check(token, rel)
    for key, node in ctx.facts.items():
        owner = run.fact_writers.get(key)
        for token in _sources({key: node}):
            check(token, FACTS_FILE, None, {owner} if owner else None)
    items, _ = ctx.assumptions
    for a in items:
        for token in _sources(a):
            check(token, ASSUMPTIONS_FILE, None, {a["task"]} if a.get("task") else None)
    for interview in ctx.interviews:
        owners = {interview.task} if interview.task else None
        text = run.path(interview.rel).read_text(encoding="utf-8")
        for token, line in prose_tokens(text):
            check(token, interview.rel, line, owners)
    return out


# --- HYB-001 ----------------------------------------------------------------------------

def tagged(ctx: Context) -> list[RunFinding]:
    out: list[RunFinding] = []
    expected = {"simulated": "SIMULATED", "human": "HUMAN"}
    for interview in ctx.interviews:
        owners = {interview.task} if interview.task else None
        for a in interview.answers:
            respondent, tag = a.fields.get("respondent"), a.fields.get("tag")
            if respondent not in expected:
                problem = f"answer {a.id}: respondent must be simulated or human"
            elif tag is None:
                problem = f"answer {a.id} ({respondent}) has no tag"
            elif tag != expected[respondent]:
                problem = f"answer {a.id}: respondent {respondent} needs tag {expected[respondent]}"
            else:
                continue
            out.append(make("HYB-001", problem, interview.rel, a.line, owners))
    _, problems = ctx.assumptions
    out += [make("HYB-001", f"assumptions.yaml: {p}", ASSUMPTIONS_FILE) for p in problems]
    return out
