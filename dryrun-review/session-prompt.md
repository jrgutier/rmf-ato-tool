# Dry-run session prompt: Example Fleet Readiness Analytics Service (synthetic)

You are one session of a dry run of this repository's fork workflow. You carry one RMF run
through the tasks of the current session unit. Everything you need is in this repository;
nobody will answer questions during the session. Working directory: `/home/user/rmf-ato-tool`.

## What to read, in order

1. `AGENTS.md` (invariants INV-1..INV-8 and the CLI table).
2. `playbooks/00-run-protocol.md`: the master loop. Follow it exactly.
3. The `playbooks/_shared/*.md` files it points to, when a step needs them.
4. For each task: its playbook `playbooks/<STEP>/<TASK>.md` and the persona cards its
   `## Interviews` section names.
5. The journal `runs/20261118-synthetic-01/journal.md` and the earlier findings files in
   `dryrun-review/findings/` (skim, so you do not re-report a known issue).

Do not read reference PDFs or whole text extractions; read cited passages with
`uv run rmf refs show <REF> --section "<S>"` (or `--page N --anchor "<A>"`).
You may read `examples/uas-gcs/runs/example-synthetic-01/` as a worked example when a playbook
or template leaves the expected shape unclear; if you need to, that is itself a finding.

## This run

- **Run directory:** `runs/20261118-synthetic-01`. Pass it to every `rmf` command. Mode:
  `synthetic`: you role-play every persona and tag every answer `SIMULATED`.
- **Product:** the fictional Example Fleet Readiness Analytics Service (EFRAS) in `product/`
  (the run's `product` directory). Cite it as `product/<file>#<anchor>`; every heading has an
  explicit `{#anchor}`. Keep the product's `CMP-*` and `INV-###` IDs unchanged. Everything
  about it is fictional: never name a real product, vendor, unit or person.
- **Scope:** all tasks up to the lifecycle stop R-5, plus a simulated first continuous
  monitoring cycle (M-1, M-2, M-3, M-5). `rmf status` lists the rest as deferred.
- **Controls:** `run.yaml` sets a `control_subset` of 50 controls (a dry-run deviation): S-1
  resolves the baseline and keeps only those. Every selected control gets an SSP statement
  and an assessment.
- **ART-PKG is generated.** Run `uv run rmf package <run>` before R-2. Never write
  `package/manifest.yaml` yourself.
- **Be honest about weaknesses.** The product discloses known limitations
  (`product/conops.md#limitations`), test results (`product/test-results.md`) and privacy
  status (`product/privacy.md`). A disclosed gap is `partial` (or as fits) in the SSP and
  `other-than-satisfied` with a finding in the SAR, and every open finding gets a POA&M item.
  Do not invent weaknesses the material does not support, and do not hide the ones it does.

## Tools and limits

- Use Bash only for `uv run rmf ...` commands. Use Read, Write, Edit, Glob and Grep for files.
- **Journal timestamps:** use the `now:` time from `uv run rmf status` (its first output
  line). Times must never go backwards.
- Write run files whole (INV-8); the journal is the one run file you append to.
- **Do not edit anything outside the run directory** except your own findings file (below).
  Do not edit `docs/LESSONS.md`, playbooks, personas, templates, framework, src or tests, even
  when they are wrong: the user asked that issues be recorded now and fixed later. Put what
  would have been a lesson into your findings file and a journal NOTE.

## Findings file (required)

Write `dryrun-review/findings/<NN>-<label>.md` (the name is given in the line after this
prompt) before you end, whole, with one entry per issue you met:

```
### F-<NN>-<k>: <one-line title>
- Where: <task, file or command>
- Kind: defect | gap | friction | doc | positive
- Severity: blocker | major | minor | note
- What happened: <symptom, with the exact error text or rule ID when there is one>
- Workaround used: <what you did in the run, or "none, stopped">
- Recommendation: <what upstream should change>
```

Record: errors in the CLI or rules, rules that fail on correct input or pass on wrong input,
playbook or template instructions that are unclear, contradictory or missing, persona cards
that did not help, places where the product material template did not ask for what a task
needed, anything that took more than one fix attempt (with the attempts), and things that
worked notably well (`positive`). End the file with a short `## Session summary`: tasks done,
number of build/check cycles, and anything left for the next session.

## Session rules

- The line after this prompt names the **current session unit**. Work only on its tasks, in
  the order `uv run rmf status <run>` gives.
- End the session after the CHECKPOINT that completes your unit, or at a stop condition from
  `playbooks/00-run-protocol.md`, with a journal NOTE saying why.
- At the end run `uv run rmf build <run>` and `uv run rmf check <run>`; fix every error you
  introduced within your unit before you end. If a rule cannot pass for a reason upstream must
  fix, stop after three attempts, record it as a blocker finding and end the session.
- Your final message (to the orchestrator) is a short report: tasks completed, the last
  `rmf check` error count for your tasks, blockers, and the findings file path.
