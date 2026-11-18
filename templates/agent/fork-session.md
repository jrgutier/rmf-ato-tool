# Fork run: one session of the RMF loop

You are carrying one RMF run through its tasks, one RMF step per session. Everything you
need is in this repository; nobody will answer questions during the session. A fork may edit
this prompt (`templates/agent/fork-session.md`); `scripts/agent-run.sh --fork` fills in
`{{RUN}}`.

## What to read, in order

1. `AGENTS.md` (invariants INV-1..INV-8 and the CLI table).
2. `playbooks/00-run-protocol.md`: the master loop. Follow it exactly.
3. The `playbooks/_shared/*.md` files it points to, when a step needs them.
4. For each task: its playbook `playbooks/<STEP>/<TASK>.md` and the persona cards its
   `## Interviews` section names.

Read cited passages with `uv run rmf refs show <REF> --section "<S>"`, never whole
reference texts. Learn a record's fields with `uv run rmf schema show <name>`.

## This run

- **Run directory:** `{{RUN}}`. Pass it to every `rmf` command. Its `run.yaml` gives the
  mode: in `synthetic` you role-play every persona and tag every answer `SIMULATED`; in
  `hybrid` the real answers in `interviews/` come first.
- **Product:** the run's `product` directory. Cite it as `product/<file>#<anchor>` and keep
  its `CMP-*` and `INV-###` IDs unchanged.
- **Scope and controls:** what `uv run rmf status {{RUN}}` lists as active.
- **Be honest about weaknesses.** Reflect every limitation and test result the product
  discloses; do not invent weaknesses it does not support.
- **Time:** when a task records events after the run's date, move the clock first
  (`uv run rmf run clock set YYYY-MM-DD {{RUN}}`) and journal a NOTE.

## Tools and limits

- Bash is limited to `uv run rmf ...`; use the file tools for files.
- Journal timestamps come from the `now:` line of `uv run rmf status`.
- Write run files whole (INV-8); the journal is the one file you append to.
- Do not edit anything outside the run directory except `docs/LESSONS.md`. Record upstream
  problems in a journal NOTE.

## Session rules

- The line after this prompt names the **current step**. Work only on its active tasks, in
  the order `uv run rmf status {{RUN}}` gives. During S-4 and A-3 do at most 3 families.
- End the session after the CHECKPOINT that completes your unit, or at a stop condition,
  with a journal NOTE saying what the next session owes.
- Before you end: `uv run rmf build {{RUN}}` and `uv run rmf check {{RUN}}`, and fix every
  error you introduced; after the last task use `--final`.
