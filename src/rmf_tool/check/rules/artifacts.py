"""RUN-FM-001 (artifact front-matter and data-file shape) and RUN-ART-001 (core artifacts
present, scope-aware)."""

from __future__ import annotations

from rmf_tool.check.context import Context
from rmf_tool.check.findings import RunFinding, make
from rmf_tool.run import facts as facts_mod
from rmf_tool.run import scope
from rmf_tool.run.model import BASELINE_FILE, FACTS_FILE, FAMILY_TOKEN, MANIFEST_FILE

FM = "RUN-FM-001"
ART = "RUN-ART-001"


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
            if schema is None or rel in (BASELINE_FILE, MANIFEST_FILE):
                continue
            data = ctx.data(rel)
            if data is None:
                out.append(make(FM, "unreadable or empty data file", rel, None, owners))
                continue
            for e in run.schema_errors(schema, data):
                out.append(make(FM, f"{schema}.schema.json: {e}", rel, None, owners))
            fam = rel.rsplit("/", 1)[-1].split(".")[0]
            if any(FAMILY_TOKEN in d["path"] for d in run.artifacts[aid].get("data") or []) \
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
    return out


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
            elif not run.path(path).is_file():
                out.append(make(ART, f"{aid}: {path} missing", path, None, owners))
    return out
