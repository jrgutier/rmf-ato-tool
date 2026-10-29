# Walking-skeleton run: Example Sensor Gateway (synthetic)

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

- **Run directory:** the only directory under `runs/` (`uv run rmf status` finds it and
  prints its ID). Mode: `synthetic`, so you role-play every persona and tag every answer
  `SIMULATED`.
- **Product:** the fictional Example Sensor Gateway (ESG) in `tests/agent/products/esg/`
  (the run's `product` directory). Cite it as `product/<file>#<anchor>`; every heading has
  an explicit `{#anchor}`. Keep the product's `CMP-*` and `INV-###` IDs unchanged.
- **Scope:** 12 tasks: P-10, P-11, C-1, C-2, C-3, S-1, S-4, A-2, A-3, A-6, R-2, R-4. Every
  other task is out of scope; `rmf status` shows them as deferred.
- **Controls:** the baseline is restricted to 6 controls (`run.yaml:control_subset`): ac-2,
  au-2, cm-6, ia-2, sc-7, si-2. That is 6 families with one control each.
- **Seeded artifacts** (outputs of out-of-scope tasks, already in the run; read them, do not
  recreate them): ART-ORG-CONTEXT, ART-STAKE, ART-INFOTYPES (with `infotypes.yaml`),
  ART-REQ, ART-RA, ART-STIG (with `stig-summary.yaml`), and the tailoring and allocation
  parts of ART-BASELINE (`tailoring.yaml`, `allocation.yaml`). Two in-scope tasks update a
  seeded artifact: A-3 updates ART-STIG and R-2 updates ART-RA (append your task to
  `touched_by` and add a section, as their playbooks say).
- **S-4 plans are minimal stubs.** In this skeleton, ART-CMP, ART-CP and ART-IRP are minimal
  stubs: the standard 5-key front-matter, the facts block, an H1, and one traced
  `## Plan summary` section of 3 to 6 sentences, with no placeholders. Do not write full
  plans; spend the effort on the SSP statements.
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
- If you cannot write to `docs/LESSONS.md`, put the six lesson lines in a journal NOTE.

## Session rules

- The line after this prompt names the **current step**. Work only on that step's active
  tasks, in the order `uv run rmf status <run>` gives (`playbooks/_shared/session-units.md`).
  During S-4 and A-3 do at most 3 families per session.
- End the session after the CHECKPOINT that completes your unit, or at a stop condition from
  `playbooks/00-run-protocol.md`, with a journal NOTE saying why.
- At the R step, after R-4: run `uv run rmf build <run>` and `uv run rmf check <run> --final`
  and fix every error before you end.
