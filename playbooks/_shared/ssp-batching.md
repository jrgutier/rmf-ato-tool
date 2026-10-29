# SSP and SAR batching

S-4 writes one SSP control statement per baseline control, and A-3 writes one assessment
determination per scoped control. A moderate baseline has about 290 controls, so both tasks
work **one control family at a time** in files the agent writes whole. This file is the
procedure for one family; the S-4 and A-3 playbooks say what goes in each record.

## Steps (one family)

1. **Find the gap.** `uv run rmf status <run> --family-gaps` lists, per family, the
   baseline controls without a statement (S-4) or without a determination (A-3). Take the
   next family it names. Why: the list is derived from disk, so it is correct after a resume.
2. **Get the control text.**
   `uv run rmf catalog show --family <fam> --run <run> --missing --fields statement`.
   Above 30 controls, add `--chunk 1/<n>`, `--chunk 2/<n>`, ... and work one chunk at a time.
   Why: 30 controls is about the most one write can hold with room for evidence.
3. **Interview in a batch.** One interview per persona per family (or chunk), covering all
   its controls, with `Control focus:` on each question. Why: one file per persona keeps
   anchors stable and interviews countable.
4. **Write the whole family file**, never a partial one and never an append:
   - S-4: `artifacts/ssp/controls/<fam>.yaml` (chunk n: `<fam>.<n>.yaml` with `chunk: n`),
     schema `framework/schema/ssp-controls.schema.json`, template
     `templates/data/ssp-controls.yaml`.
   - A-3: `artifacts/sar/results/<fam>.yaml` (chunk n: `<fam>.<n>.yaml`), schema
     `framework/schema/sar-results.schema.json`, template `templates/data/sar-results.yaml`.
   - Each control appears in exactly one file (SSP-DUP-001). Why: INV-8; a partial file is
     detected and redone, an appended one duplicates.
5. **Build and check the family.** `uv run rmf build <run>`, then
   `uv run rmf check <run> --family <fam>`, which runs every implemented rule and reports
   only the family's findings (for S-4 coverage SSP-COV-001 and duplicates SSP-DUP-001;
   for A-3 SAR-COV-001; for both TRACE-001 and TRACE-002, as the phase enforces them). Fix
   until it reports 0 errors. Do not pass `--rules` with a rule the CLI does not implement
   yet; it exits with a usage error.
6. **Journal** a CHECKPOINT naming the task and family, for example
   `## 2026-11-05T15:10Z · CHECKPOINT · task S-4 · family: ac`.
7. **Next family**, until `--family-gaps` reports none, or the session has done 3 families
   (`_shared/session-units.md`).

## Short forms

Keep routine records short so the long ones get the context:

- **Inherited control (S-4):** `status: inherited`, `inherited_from:` the provider, a
  one-sentence statement of what the system still does, and the provider's artifact or the
  answer as source.
- **Satisfied or inherited determination (A-3):** a one- or two-sentence summary naming the
  evidence examined, tested or heard.
- Statements for `partial`, `planned` and `other-than-satisfied` records are full: what
  exists, what is missing, and the evidence for both.

## Citations

- SP 800-18r2 §4.3.2 (documenting planned control implementations):
  `uv run rmf refs show SP800-18R2 --section "4.3.2. Identification of Planned Control Implementations"`.
- SP 800-53Ar5 §3.3 (conducting assessments):
  `uv run rmf refs show SP800-53AR5 --section "3.3 CONDUCT SECURITY AND PRIVACY CONTROL ASSESSMENTS"`.
