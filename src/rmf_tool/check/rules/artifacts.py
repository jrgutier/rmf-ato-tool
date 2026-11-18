"""RUN-FM-001 (artifact front-matter and data-file shape), RUN-ART-001 (core artifacts
present, scope-aware) and RUN-PH-001 (template placeholders left in run files)."""

from __future__ import annotations

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope
from rmf_tool.run.model import (
    ARTIFACTS_DIR,
    ASSUMPTIONS_FILE,
    FACTS_FILE,
    FAMILY_TOKEN,
    INTERVIEWS_DIR,
    JOURNAL_FILE,
    MANIFEST_FILE,
    YamlError,
    read_yaml,
)

FM = "RUN-FM-001"
ART = "RUN-ART-001"
PROFILE_FILE = "profile.yaml"
PH = "RUN-PH-001"
PLACEHOLDER = "<<FILL"  # templates/ placeholders: <<FILL: what to write>>


def front_matter(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    out: list[RunFinding] = []
    for rel, doc in ctx.docs.items():
        stem = rel.rsplit("/", 1)[-1][:-3]
        owners = set(run.writers(stem)) if stem in run.artifacts else set()

        def err(message: str, rel: str = rel, owners: set[str] = owners) -> None:
            out.append(make(FM, message, rel, 1, owners))

        if doc.data is None:
            err(doc.error or "no front-matter")
            continue
        for e in run.schema_errors("artifact-frontmatter", doc.data):
            err(f"front-matter {e}")
        aid = doc.data.get("artifact_id")
        if aid not in run.artifacts:
            err(f"unknown artifact_id {aid!r}")
            continue
        if aid != stem:
            err(f"artifact_id {aid} does not match the file name {stem}.md")
        if doc.data.get("run_id") != run.run_id:
            err(f"run_id {doc.data.get('run_id')!r} is not this run ({run.run_id})")
        writers = run.writers(aid)
        producer = run.artifacts[aid].get("producer")
        if doc.data.get("produced_by_task") != producer:
            err(f"produced_by_task {doc.data.get('produced_by_task')!r}; {aid} is produced "
                f"by {producer}")
        touched = doc.data.get("touched_by") or []
        if isinstance(touched, list) and touched and touched[0] != producer:
            err(f"touched_by must start with the producer {producer}")
        for t in touched if isinstance(touched, list) else []:
            if t not in writers:
                err(f"touched_by lists {t}, which neither produces nor updates {aid}")

    for aid in run.artifacts:
        owners = set(run.writers(aid))
        for rel, schema in run.data_files(aid):
            if schema is None or rel == MANIFEST_FILE:
                continue
            data = ctx.data(rel)
            if data is None:
                out.append(make(FM, "unreadable or empty data file", rel, None, owners))
                continue
            for e in run.schema_errors(schema, data):
                out.append(make(FM, f"{schema}.schema.json: {e}", rel, None,
                                _key_owner(schema, str(e), owners)))
            fam = rel.rsplit("/", 1)[-1].split(".")[0]
            if any(FAMILY_TOKEN in d["path"] and d.get("schema") == schema
                   for d in run.artifacts[aid].get("data") or []) \
                    and isinstance(data, dict) and data.get("family") != fam:
                out.append(make(FM, f"family {data.get('family')!r} does not match the file "
                               f"name ({fam})", rel, None, owners))
    if run.path(FACTS_FILE).is_file():
        try:
            data = run.data(FACTS_FILE)
        except ValueError as exc:
            out.append(make(FM, str(exc), FACTS_FILE))
        else:
            for e in run.schema_errors("facts", data if data is not None else {}):
                out.append(make(FM, f"facts.schema.json: {e}", FACTS_FILE))
    out += _product_profile(run)
    return out


def _product_profile(run) -> list[RunFinding]:
    """product/profile.yaml is optional; when present it has the shape of
    product-profile.schema.json (proposed values only)."""
    path = run.product_dir / PROFILE_FILE
    if not path.is_file():
        return []
    shown = f"{run.config.get('product')}/{PROFILE_FILE}"
    try:
        data = read_yaml(path)
    except YamlError as exc:
        return [make(FM, str(exc), shown, run_wide=True)]
    return [make(FM, f"product-profile.schema.json: {e}", shown, run_wide=True)
            for e in run.schema_errors("product-profile", data if data is not None else {})]


def core_present(ctx: Context) -> list[RunFinding]:
    run = ctx.run
    out: list[RunFinding] = []
    for aid, art in run.artifacts.items():
        if art.get("package") != "core" or not scope.produced_or_seeded(run, aid):
            continue
        owners = {art.get("producer")}
        md = run.artifact_md(aid)
        if art.get("template") and not md.is_file():
            out.append(make(ART, f"core artifact {aid} missing", run.rel(md), None, owners))
        for entry in art.get("data") or []:
            path = entry["path"]
            if path.startswith(f"{FACTS_FILE}#"):
                if facts_mod.get(ctx.facts, path.partition("#")[2]) is None:
                    out.append(make(ART, f"{aid}: {path} not set", FACTS_FILE, None, owners))
            elif FAMILY_TOKEN in path:
                parent, _, pattern = path.rpartition("/")
                if not list(run.path(parent).glob(pattern.replace(FAMILY_TOKEN, "*"))):
                    out.append(make(ART, f"{aid}: no {path} file", parent, None, owners))
            elif not run.path(path).is_file() and not entry.get("optional"):
                out.append(make(ART, f"{aid}: {path} missing", path, None, owners))
    return out


def placeholders(ctx: Context) -> list[RunFinding]:
    """Every agent-written file: artifacts (Markdown and data), interviews, facts,
    assumptions and the journal."""
    run = ctx.run
    paths = sorted(p for p in run.path(ARTIFACTS_DIR).rglob("*")
                   if p.is_file() and p.suffix in (".md", ".yaml", ".yml"))
    paths += sorted(run.path(INTERVIEWS_DIR).glob("*.md"))
    paths += [run.path(f) for f in (FACTS_FILE, ASSUMPTIONS_FILE, JOURNAL_FILE)]
    out: list[RunFinding] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(lines, start=1):
            if PLACEHOLDER in line:
                out.append(make(PH, f"unresolved placeholder: {line.strip()[:120]}",
                                run.rel(path), lineno))
    return out


# A shared record written section by section: a schema error in one section is charged to
# the task that writes it, so `rmf status` does not send the run back to the first writer
# (dry-run finding F-01-9).
_SECTION_KEYS = {"org-context": {"reference_currency": "P-2", "providers": "P-2",
                                 "posture_reviews": "P-3", "developed_overlays": "P-4"}}


def _key_owner(schema: str, message: str, owners: set[str]) -> set[str]:
    sections = dict(_SECTION_KEYS.get(schema) or {})
    if schema == "org-context":
        from rmf_tool.check.rules.org_context import SECTIONS
        sections.update(SECTIONS)
    key = message.split(":", 1)[0].split("/", 1)[0].split(".", 1)[0].strip()
    task = sections.get(key)
    return {task} if task and task in owners else owners
