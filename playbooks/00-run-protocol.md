# Run protocol (master loop)

The procedure every agent follows to carry a run (`runs/<run-id>/`) through its RMF tasks.
Start every session here, after `AGENTS.md`. In the commands below, `<run>` is the run
directory, for example `runs/20261105-synthetic-01`.

## Steps

1. **Orient.** Run `uv run rmf status <run>`. It prints the run's mode, the done, active
   and deferred tasks, and the **next action**: one task (or, during S-4 and A-3, one task
   and family). Why: state lives only on disk (`_shared/resume.md`), so a fresh session knows
   nothing until it asks.
2. **Check the session unit.** If this session was started for one RMF step (the prompt
   names it) and the next action belongs to another step, stop: append a NOTE to the
   journal and end the session.
   Why: one session covers one RMF step, or at most 3 control families
   (`_shared/session-units.md`); crossing that line is how context overflows.
3. **Load the task playbook** `playbooks/<STEP>/<TASK>.md` and every persona card it names
   in `personas/`. Read the CLI-generated header first (dependencies, inputs, outputs,
   facts written, minimum interviews, RACI, persona card links, purpose), then the body.
   Persona cards that do not exist yet are not needed: use the ones the body's
   `## Interviews` section names. Why: the header is synced from `framework/tasks/*.yaml`, so it
   is the authoritative contract; the body tells you how to meet it.
4. **Read only the listed inputs.** Open the files the playbook's `## Inputs` section names
   and the `## Outputs` files you will rewrite, and nothing else from the run. Read reference passages with
   `uv run rmf refs show <REF> --section "<S>"` and control text with
   `uv run rmf catalog show ...`. Why: every extra file costs context you need for the
   writing steps, and unlisted inputs produce untraceable claims.
5. **Interview.** Run the interviews the playbook lists, following
   `_shared/interviewing.md` (synthetic role-play) and, when `run.yaml:mode` is `hybrid`,
   `_shared/hybrid-mode.md`. Write each interview file whole before you use its answers.
   Why: artifacts cite answer anchors (`INT-###.A#`), which must exist first.
6. **Write the outputs.** Write each output file whole (INV-8):
   - a new artifact: Read `templates/artifacts/<ART-ID>.md`, replace every `<<FILL: ...>>`
     placeholder, delete the template comment, and Write the result to
     `artifacts/<ART-ID>.md` (the S-4 plan stubs have no template; their playbook gives the
     shape);
   - structured data: start from the matching `templates/data/*.yaml` and replace every
     example value; `uv run rmf schema show <name>` lists every field (required ones
     marked `*`) and `uv run rmf schema template <name>` prints a skeleton when no
     template exists, so you never need to read the schema or rule source;
   - an artifact an earlier task or a seed wrote: Read it, then Write the whole file back
     with your task appended to `touched_by` and your section added; never drop what is
     there;
   - facts: rewrite `facts.yaml` whole when the playbook says so, keeping every field other
     tasks wrote.
   - a data file an earlier task wrote (S-3 changing C-1's `leveraged-authorizations.yaml`):
     write it whole, add your answers to the changed records' `sources`, and journal a NOTE
     naming the file and the records. Data files carry no `touched_by`, and `rmf status`
     charges their findings to the task that owns the file.

   Tag and trace every claim per
   `_shared/tagging-and-traceability.md`. Why: the CLI derives OSCAL and status from these
   files and checks every claim's trace.
   - Write YAML in block style, one key per line, and double-quote every free-text value
     (`description: "..."`). Use flow style (`{...}`, `[...]`) only for short lists of IDs
     or tokens. Why: a comma or `: ` inside an unquoted flow-style value silently splits it
     into extra keys, and the schema check (RUN-FM-001) then fails.
7. **Build, then check.** Run `uv run rmf build <run>`, then
   `uv run rmf check <run> --task <TASK>`. Fix every error and repeat both commands until the
   check reports 0 errors. Never skip `build`: GEN-STALE-001 and HYB-002 compare against a
   fresh build and fail on stale output. Why: INV-6; a later task built on a failing one
   inherits its errors.
8. **Journal.** Append a CHECKPOINT entry to `<run>/journal.md`
   (`_shared/journaling-and-lessons.md`). If a fix in step 7 took more than one attempt,
   append a RETRY entry first and record a lesson. Why: JOURNAL-001 needs a CHECKPOINT per
   completed step, and the next session reads the journal to see what happened.
9. **Loop.** Go back to step 1. End the session after the CHECKPOINT that completes the
   session unit (step 2), or when `rmf status` reports the run done. Close each session's
   journal with a NOTE saying what the next session owes; it is the most useful hand-off.

## Simulated time

A synthetic run covers months in hours. When a task records events after the run's current
date (the assessment window, the decision, monitoring), first move the clock with
`uv run rmf run clock set YYYY-MM-DD` and journal a NOTE for what happened in between. Date
rules read the clock, so do not invent progress to satisfy them.

## Entering past P-1

A run starts at P-1 unless an assessment of risk and of the Prepare tasks puts it at a later
step (SP 800-37r2 2.4; DoDI 5000.90 lets the PM tailor the RMF with the AO's and DA's
concurrence). Record that determination in `run.yaml` as `entry` before the first task:
`step` and `task` entered, the `current_state` of the system, the tasks whose activities are
already `completed` (each before the entry task), the `gaps` found, the `decision` and its
rationale, the personas `notified`, and `approved_by` (PER-AO, or PER-AODR on the AO's
behalf). ENTRY-001 checks it. An existing system entering at A, R or M lists every Prepare task,
C-2, S-1, S-2 and I-1 as `completed` or keeps them in scope; entering at M also
needs `deficiencies: []` from the gap analysis, the entry `date` and a seeded ledger with an authorization in
force, or the run continues at assessment and authorization (OMP-001). Then seed the artifacts of the completed tasks (`seeded`) and
defer the rest (`deferred`), so `rmf status` names the entry task next.

## Stop conditions

Stop and journal a NOTE (do not guess) when:

- `rmf check` still reports the same error after 3 fix attempts. Record a lesson
  (`_shared/journaling-and-lessons.md`) and end the session. Why: a repeated failure means
  the playbook or the rule is wrong, and only a person can decide which.
- An input the playbook lists is missing and `rmf status` does not offer a task that
  produces it. Why: inventing an input breaks traceability (RUN-CFG-001 should have caught
  it; report that too).
- The run's mode is `hybrid` and a decision the playbook reserves for a human (an
  authorization decision, a categorization approval) has no human answer. Use the fallback in
  `_shared/hybrid-mode.md` only where it is allowed.

## Run layout

| Path (relative to `<run>`) | Written by | Notes |
|---|---|---|
| `run.yaml` | `rmf run init` | mode, scope, seeded artifacts, humans; edit only `humans`, `scope`, `seeded`, `lifecycle_stop*`, `include_after_stop`, `deferred` |
| `facts.yaml` | tasks with `writes_facts` | the only home of system facts (INV-4); each field has `set_by_task` |
| `assumptions.yaml` | any task | `ASM-*` entries (`_shared/tagging-and-traceability.md`) |
| `interviews/INT-###-<TASK>-<PER>.md` | any task | one file per interview (`_shared/interviewing.md`) |
| `artifacts/ART-*.md` | the producing and updating tasks | exactly 5 front-matter keys |
| `artifacts/data/<name>.yaml` | per playbook | structured data; schemas in `framework/schema/` |
| `artifacts/ssp/controls/<fam>.yaml` | S-4 | one file per family (`_shared/ssp-batching.md`) |
| `artifacts/sar/results/<fam>.yaml` | A-3 | one file per family |
| `artifacts/poam/items.yaml` | A-6 | POA&M items |
| `baseline.json`, `oscal/`, `reports/`, `package/manifest.yaml` | `rmf build`, `rmf baseline resolve`, `rmf package` | generated; never hand-edit (INV-2) |
| `journal.md` | every task | append-only log |

The product material lives in the directory `run.yaml:product` names; cite it as
`product/<path>#<anchor>`.

## Artifact front-matter

Every `artifacts/ART-*.md` starts with these 5 keys (RUN-FM-001), plus `handling` (CUI or
the classification level) where its template carries it (ART-CMP, ART-POAM, ART-SAR,
ART-STIG):

```yaml
---
artifact_id: ART-SD
run_id: 20261105-synthetic-01
produced_by_task: C-1
touched_by: [C-1]
sources: [INT-004.A1, product/conops.md#users]
---
```

- `produced_by_task` is the artifact's producer in `framework/artifacts.yaml`, also when a
  seed or another task wrote the file first.
- `touched_by` lists every task that wrote the file, producer first; append yourself when you
  update it, and never remove an entry.
- `sources` lists the trace tokens the whole artifact rests on.
- No other key. System facts (name, categorization, baseline) never appear here or in prose;
  `rmf build` injects them from `facts.yaml` (INV-4).

Right under the H1 of every artifact sits the facts block, copied from the template:

```markdown
<!-- BEGIN rmf:facts -->
<!-- END rmf:facts -->
```

Keep both marker lines and never write between them; `rmf build` fills the block. No other
`rmf:` marker is allowed in run files. Structured records (inventory items, statements,
determinations, POA&M items) live only in their YAML files: summarize them in the Markdown
and name them by ID, never copy them, so each fact keeps one home.

## Commands

| Command | When |
|---|---|
| `uv run rmf status <run> [--format json] [--family-gaps]` | step 1; `--family-gaps` during S-4/A-3 |
| `uv run rmf build <run>` | step 7, before every check |
| `uv run rmf check <run> --task <T>` | step 7 |
| `uv run rmf check <run> --family <fam>` | during per-family batches (S-4, A-3) |
| `uv run rmf check <run> --final` | after the last task of the run |
| `uv run rmf baseline resolve <run>` | S-1, before writing the `baseline_id` fact |
| `uv run rmf catalog show --family <fam> --run <run> --missing --fields statement` | S-4 batches (`--missing`: controls without a statement) |
| `uv run rmf catalog show --family <fam> --run <run> --fields title,objectives` | A-2 and A-3 (assessment objectives) |
| `uv run rmf package <run>` | before R-2 (generates ART-PKG) |
| `uv run rmf refs show <REF> --section "<S>"` | to read a cited passage |

## Citations

- SP 800-37r2 §2 and Chapter 3 (the tasks): `uv run rmf refs show SP800-37R2 --section "TASK C-1"`.
- DoDI 8510.01 §3.2 (RMF steps and task tables), pages 13-19:
  `uv run rmf refs show DODI8510.01 --section "b. Categorize"`.
