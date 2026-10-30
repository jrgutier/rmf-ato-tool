# Example fork run: Example Tactical UAS Ground Control Station (synthetic)

You are carrying one RMF run through its tasks, one RMF step per session. Everything you
need is in this repository; nobody will answer questions during the session.

## What to read, in order

1. `AGENTS.md` (invariants INV-1..INV-8 and the CLI table).
2. `playbooks/00-run-protocol.md`: the master loop. Follow it exactly.
3. The `playbooks/_shared/*.md` files it points to, when a step needs them.
4. For each task: its playbook `playbooks/<STEP>/<TASK>.md` and the persona cards its
   `## Interviews` section names.

Do not read reference PDFs or whole text extractions; read cited passages with
`uv run rmf refs show <REF> --section "<S>"` (or `--page N --anchor "<A>"`).

## This run

- **Run directory:** `examples/uas-gcs/runs/example-synthetic-01`. Pass it to every `rmf`
  command (`uv run rmf status examples/uas-gcs/runs/example-synthetic-01`). Mode:
  `synthetic`, so you role-play every persona and tag every answer `SIMULATED`.
- **Product:** the fictional Example Tactical UAS Ground Control Station (ETGCS) in
  `examples/uas-gcs/product/` (the run's `product` directory). Cite it as
  `product/<file>#<anchor>`; every heading has an explicit `{#anchor}`. Keep the product's
  `CMP-*` and `INV-###` IDs unchanged. Everything you write about it is fictional: never
  name a real product, vendor, unit or person.
- **Scope:** all tasks up to the lifecycle stop R-5, plus a simulated first continuous
  monitoring cycle (M-1, M-2, M-3, M-5). `rmf status` lists the rest as deferred.
- **Controls:** the full baseline that S-1 resolves (`uv run rmf baseline resolve`). There is
  no control subset: every selected control gets an SSP statement and an assessment.
- **ART-PKG is generated.** Run `uv run rmf package <run>` before R-2 (the R-2 playbook says
  so). Never write `package/manifest.yaml` yourself.
- **Be honest about weaknesses.** The product discloses known limitations
  (`product/conops.md#limitations`) and test results (`product/test-results.md`). Statements,
  determinations and risks must reflect them: a disclosed gap is `partial` in the SSP and
  `other-than-satisfied` with a finding in the SAR, and every open finding gets a POA&M item.
  Do not invent weaknesses the material does not support, and do not hide the ones it does.

## Tools and limits

- Bash is limited to `uv run rmf ...`. Use the Read, Write, Edit, Glob and Grep tools for
  files. There is no `date`, `ls` or `cat`.
- **Journal timestamps:** use the `now:` time from `uv run rmf status` (its first output
  line). Times must never go backwards.
- Write run files whole (INV-8); the journal is the one file you append to.
- Do not edit anything outside the run directory except `docs/LESSONS.md`. If an upstream
  file (framework, playbook, persona, template, tool) looks wrong, record it in a journal
  NOTE and, when it blocks you, as a lesson; the maintainers fix upstream files.
- If you cannot write to `docs/LESSONS.md`, put the six lesson lines in a journal NOTE.

## Session rules

- The line after this prompt names the **current step**. Work only on that step's active
  tasks, in the order `uv run rmf status <run>` gives (`playbooks/_shared/session-units.md`).
  During S-4 and A-3 do at most 3 families per session; the next session continues with the
  next families.
- End the session after the CHECKPOINT that completes your unit, or at a stop condition from
  `playbooks/00-run-protocol.md`, with a journal NOTE saying why.
- At the end of every session run `uv run rmf build <run>` and `uv run rmf check <run>`, and
  fix every error you introduced before you end.
- After R-5 and after the M tasks: run `uv run rmf build <run>` and
  `uv run rmf check <run> --final` and fix every error before you end.
