# Playbook front-matter contract

Every task playbook starts with front matter that the CLI owns, followed by a body. This
file is the one home of that contract: what the CLI writes, what an author writes, and
what `rmf playbooks sync --check` and `rmf validate` (FW-PB-001, FW-PB-002) enforce.
Artifact front-matter, the five keys at the top of each `artifacts/ART-*.md` in a run, is a
different contract; it lives in `00-run-protocol.md` ("Artifact front-matter").

## Steps

1. **Read the header first.** Between `<!-- BEGIN rmf:header -->` and
   `<!-- END rmf:header -->` sits the task's contract, generated from
   `framework/tasks/<STEP>.yaml`: step, phases, dependencies, inputs, outputs (produced or
   updated), facts written, minimum interviews, RACI, persona card links and purpose. Why:
   the header cannot drift from the YAML, so where the body and the header disagree, the
   header is right (INV-1).
2. **Find the body marker** on the line after the header:
   - `<!-- rmf:body authored -->`: a person wrote the body; the CLI never touches it;
   - `<!-- rmf:body generated -->`: the CLI rendered the body from
     `templates/playbook-body.md.j2` and the same YAML; it is as binding as an authored
     body, only more generic.
3. **Follow the body's sections in order:** `Steps`, `Interviews`, `Inputs`, `Outputs`,
   `Facts`, `Done when`, `Journal and lessons`, `Citations`. Why: every playbook has the
   same shape, so a session can find the done test or the inputs list without reading all
   of it.
4. **Never edit inside CLI-owned text.** Change the YAML (or the body template) and run
   `uv run rmf playbooks sync`. Why: INV-2; the check reports any hand edit as stale.

## What the CLI enforces

| Rule | Fails when |
|---|---|
| FW-PB-001 | a task's `playbook:` field names a file that does not exist, or an anchor (`#task-p-3`) with no matching section |
| FW-PB-002 | a header is missing, stale or edited by hand; a generated body differs from a fresh render; a file has no body marker; an authored body lacks one of the eight sections or has them out of order |

`rmf playbooks sync` fixes everything the CLI owns: it rewrites headers and generated
bodies, and creates a missing single-task playbook with a generated body. It never writes
an authored body, so FW-PB-002 findings about authored sections need a person.

## Shared playbooks

Several tasks may share one authored playbook: P-1 to P-7 share
`playbooks/P/P-org-context.md`. Each task's `playbook:` field ends in an anchor such as
`#task-p-1`, which names an H2 section `## Task P-1`. Inside the section:

- the CLI keeps a per-task header block, `<!-- BEGIN rmf:header P-1 -->` to
  `<!-- END rmf:header P-1 -->`, right under the heading;
- the eight body sections are H3 headings (`### Steps` ... `### Citations`).

The file has one `<!-- rmf:body authored -->` marker, and may have H2 sections that are not
tasks (for example a common procedure).

## Upgrading a generated playbook

1. Change `<!-- rmf:body generated -->` to `<!-- rmf:body authored -->`.
2. Rewrite the body; keep the eight sections. Use an authored playbook in the same step as
   the style reference: numbered steps that each end with the reason, a "Question focus"
   column in the interview table, file paths and commands written out.
3. Run `uv run rmf playbooks sync --check`; it must report 0 errors.

## Citations

- SP 800-37r2 Chapter 3 gives each task's inputs, outputs and roles, which the header
  restates from the YAML: `uv run rmf refs show SP800-37R2 --section "TASK P-1"`.
- DoDI 8510.01 §3.2 tables give the DoD primary responsibility per task:
  `uv run rmf refs show DODI8510.01 --page 13 --anchor "Organization Prepare Step Tasks"`.
