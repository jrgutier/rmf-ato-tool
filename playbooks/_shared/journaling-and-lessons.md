# Journaling and lessons

Every run keeps `journal.md`, an append-only log of what happened. Lessons go to
`docs/LESSONS.md` when something went wrong in a way the next agent should not repeat.

## Steps

1. **After each completed task (or S-4/A-3 family): append a CHECKPOINT.** State what was
   written and the check result. Why: JOURNAL-001 fails a completed step without one, and the
   next session reads it to resume.
2. **When a fix needed a second attempt: append a RETRY** before the CHECKPOINT, naming the
   rule that failed and the lesson. Why: LES-001 requires every RETRY to cite a lesson or
   say why none applies.
3. **When you change something already written for a reason other than the current task's
   own work: append a CORRECTION**, with its lesson or `none — <reason>`.
4. **When a persona makes a decision** (a categorization approval, a risk response, the
   authorization decision): **append a DECISION** naming who decided and the answer anchor.
5. **For anything else worth telling the next session** (a stop, a doubt, a skipped
   optional step): **append a NOTE**.
6. **Record a lesson** in `docs/LESSONS.md` when a RETRY's cause could happen again, or a
   stop condition fired (format below). Why: a lesson that stays in one run's journal is
   lost to the next run.

## Journal format

```markdown
# Journal — 20261105-synthetic-01

## 2026-11-05T14:02Z · CHECKPOINT · task C-2
Categorization written to facts.yaml (set_by C-2); ART-CAT written; rmf build + rmf check --task C-2: 0 errors.

## 2026-11-05T15:10Z · CHECKPOINT · task S-4 · family: ac

## 2026-11-05T15:40Z · RETRY · task S-4 · lesson: L-0021
SSP-DUP-001: ac-2 appeared in ac.yaml and ac.2.yaml; rewrote both files whole.

## 2026-11-05T16:10Z · DECISION · task C-3 · by: PER-AODR (simulated, INT-009.A2)

## 2026-11-05T16:30Z · CORRECTION · artifact ART-SAR · lesson: none — typo only
```

- The file starts with `# Journal — <run-id>`; `rmf run init` writes it from
  `templates/journal.md`.
- Each entry is an H2: `## <UTC time to the minute>Z · <TYPE> · <subject>[ · <extra>]`,
  then an optional body of one to three lines.
- The time is UTC: use the `now:` time from `uv run rmf status` (its first output line;
  `"now"` in `--format json`). Run `rmf status` again before an entry if time has passed.
  Times never go backwards.
- TYPE is one of CHECKPOINT, DECISION, RETRY, CORRECTION, NOTE.
- Subject is `task <TASK>`, `artifact <ART-ID>`, or `run` (for a NOTE about the whole
  run). A CHECKPOINT always names a task.
- Extras are ` · key: value` pairs with a lowercase key: ` · family: ac` for a family
  batch, ` · lesson: ...`, ` · by: ...`.
- RETRY and CORRECTION end with ` · lesson: L-NNNN` or ` · lesson: none — <reason>`.
- DECISION ends with ` · by: <PER-ID> (<simulated|human>, <INT-###.A#>)`.
- Append only: never edit or delete an earlier entry. The journal is the one run file you
  append to rather than rewrite; that is its purpose.

## Lesson format

Append to `docs/LESSONS.md` with the next free number (`rmf lessons check` verifies it):

```markdown
## L-0021 · 2026-11-05 · run: esg/20261105-synthetic-01 · tags: ssp, resume
- Symptom: SSP-DUP-001 reported ac-2 twice after a resumed session.
- Root cause: the resumed session wrote ac.2.yaml without reading which controls ac.yaml already held.
- Fix: rewrote both files whole from the catalog listing.
- Rule: on resume, list a family's existing files before writing a chunk.
- Promotion: none — covered by SSP-DUP-001 and ssp-batching.md step 4
```

- All six lines are required. `Promotion:` is one of: `AGENTS.md INV-n`, `LR-nn`,
  `check: <rule or test>`, or `none — <reason>`; never `pending` (LES-003).
- Never edit an existing lesson (LES-002).
- In a headless agent run you may lack write access to `docs/`; then put the six lines in a
  journal NOTE instead, and the operator copies them.

## Citations

- SP 800-37r2 Task M-4 and Task R-5 (keeping records current and reported):
  `uv run rmf refs show SP800-37R2 --section "TASK M-4"`.
- DoDI 8510.01 §4.4.a(11)(b), decisions recorded and tracked through the life cycle:
  `uv run rmf refs show DODI8510.01 --page 28 --anchor "Are recorded, tracked, and made available to all parties"`.
