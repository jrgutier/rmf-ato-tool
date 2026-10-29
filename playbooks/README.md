# Playbooks

Procedures an agent (or a person) follows to carry a run through the 47 RMF tasks of
NIST SP 800-37r2, as DoDI 8510.01 applies them. The facts about each task (inputs,
outputs, roles, dependencies, citations) live in `framework/tasks/*.yaml`; the playbooks say
how to do the work.

## Where to start

1. `AGENTS.md`, then [`00-run-protocol.md`](00-run-protocol.md): the master loop every
   session follows (status, playbook, inputs, interviews, outputs, build, check, journal).
2. The task playbook `rmf status` names. Each one starts with a CLI-generated header (the
   task's contract) and continues with a body in eight sections
   ([`_shared/front-matter-contract.md`](_shared/front-matter-contract.md)).
3. The shared procedures the playbook points to, in [`_shared/`](_shared/).

## Layout

| Path | Contents |
|---|---|
| `00-run-protocol.md` | master loop, stop conditions, run layout, artifact front-matter |
| `P/` `C/` `S/` `I/` `A/` `R/` `M/` | one playbook per task, `<STEP>/<TASK>.md`, and a README per step |
| `P/P-org-context.md` | the shared playbook of P-1 to P-7, one `## Task P-n` section each |
| `_shared/` | procedures several tasks use (below) |
| `_ops/` | maintainer procedures that are not part of a run (`fetch-blocked-refs.md`) |

## Steps

| Step | README | Tasks | Acquisition phases |
|---|---|---|---|
| P Prepare | [`P/README.md`](P/README.md) | P-1 .. P-18 | MSA, early TMRR |
| C Categorize | [`C/README.md`](C/README.md) | C-1 .. C-3 | MSA (approved by Milestone A) |
| S Select | [`S/README.md`](S/README.md) | S-1 .. S-6 | TMRR (by PDR and Milestone B) |
| I Implement | [`I/README.md`](I/README.md) | I-1, I-2 | EMD |
| A Assess | [`A/README.md`](A/README.md) | A-1 .. A-6 | EMD (plan approved before TRR) |
| R Authorize | [`R/README.md`](R/README.md) | R-1 .. R-5 | EMD (decision before Milestone C) |
| M Monitor | [`M/README.md`](M/README.md) | M-1 .. M-7 | O&S |

The phase alignment comes from `framework/rmf-steps.yaml`; the rendered manual
(`MANUAL.md`) shows it per task.

## Authored and generated bodies

A body is **authored** (`<!-- rmf:body authored -->`) where the task needs judgment that a
template cannot capture, and **generated** (`<!-- rmf:body generated -->`, rendered from
`templates/playbook-body.md.j2`) elsewhere. A generated body is complete and followable:
entry check, inputs, interviews, outputs with their templates and schemas, facts, the done
test, journal entries and citations, all derived from the task's YAML. It is generic, so
the inputs and cited passages carry more of the content. The marker in each file is
authoritative; the step READMEs list the current state.

To turn a generated body into an authored one, follow "Upgrading a generated playbook" in
`_shared/front-matter-contract.md`.

## Shared procedures

| File | Use it for |
|---|---|
| [`interviewing.md`](_shared/interviewing.md) | numbering, asking, answering in character and writing interview files |
| [`hybrid-mode.md`](_shared/hybrid-mode.md) | runs where some personas are real people |
| [`tagging-and-traceability.md`](_shared/tagging-and-traceability.md) | trace tokens, tags and assumptions |
| [`journaling-and-lessons.md`](_shared/journaling-and-lessons.md) | journal entries and lessons |
| [`resume.md`](_shared/resume.md) | starting on a half-done run |
| [`session-units.md`](_shared/session-units.md) | how much one session does |
| [`ssp-batching.md`](_shared/ssp-batching.md) | family-by-family SSP statements (S-4) and the file mechanics A-3 shares |
| [`assessment-batching.md`](_shared/assessment-batching.md) | assessing family by family (A-3, A-5, M-2): evidence, numbering, what each task may change |
| [`front-matter-contract.md`](_shared/front-matter-contract.md) | the playbook header and body contract the CLI enforces |

## Keeping playbooks in sync

- `uv run rmf playbooks sync` rewrites every header and generated body from `framework/`
  and creates a missing playbook with a generated body. Run it after any change to
  `framework/tasks/*.yaml`, `framework/artifacts.yaml` or the body template.
- `uv run rmf playbooks sync --check` (and `uv run rmf validate --profile p5`) report
  FW-PB-001 (a task without a playbook) and FW-PB-002 (stale or incomplete playbooks).

## Citations

- SP 800-37r2 Chapter 3 (the tasks): `uv run rmf refs show SP800-37R2 --section "TASK P-1"`.
- DoDI 8510.01 §3.2 (RMF steps and task tables):
  `uv run rmf refs show DODI8510.01 --page 13 --anchor "Organization Prepare Step Tasks"`.
