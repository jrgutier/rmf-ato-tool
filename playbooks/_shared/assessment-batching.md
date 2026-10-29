# Assessment batching

Three tasks assess controls family by family: A-3 (the initial assessment), A-5
(reassessment of remediated controls) and M-2 (ongoing assessments). The file mechanics
(the gap list, chunking above 30 controls, whole-file writes, the per-family check and
CHECKPOINT) are the same as for the SSP and live in `_shared/ssp-batching.md`. This file
adds what is specific to assessing: evidence, numbering, reuse and what each task may change.

## Steps (one family)

1. **Take the assessor's stance.** Act as PER-SCA (`personas/PER-SCA.md`,
   `## Role-play guidance`). The SSP's claim and the program's statements are what you
   test, not evidence. Why: the AO relies on independent results (SP 800-53Ar5 §3.3).
2. **List the controls to assess.**
   - A-3: the family's scoped controls without a determination
     (`uv run rmf status <run> --family-gaps`).
   - A-5: the family's controls with an open finding the program says it fixed.
   - M-2: the family's controls that `conmon.yaml` makes due this cycle (the M-2 playbook
     says how), plus controls with POA&M milestones due.
3. **Get the objectives.**
   `uv run rmf catalog show --family <fam> --run <run> --fields title,objectives`
   (with `--chunk i/n` above 30 controls). Each objective is a determination statement
   you can answer satisfied or other than satisfied (SP 800-53Ar5 Appendix E).
4. **Collect evidence, reuse first.** Use, in this order: results the run already holds and
   that are still current (test results, scans, earlier determinations), the product
   material, then batched interviews, one per persona per family, with `Control focus:` on
   each question. Ask for records, settings, results and dates. Why: DoDI 8510.01 Table 5
   (A-3) tells assessors to reuse test events and prior results.
5. **Decide each control.** `satisfied` only when the evidence covers every objective;
   `other-than-satisfied` when any objective fails or has no evidence; `not-applicable`
   only with the reason the control does not apply. An SSP status of `partial` or
   `planned`, an open STIG finding mapped to the control, or a failed test means
   other-than-satisfied unless the evidence shows the gap closed.
6. **Write the family file whole** (`artifacts/sar/results/<fam>.yaml`, schema
   `sar-results`), keeping every record you did not assess unchanged.
7. **Build, check and CHECKPOINT the family** as `_shared/ssp-batching.md` steps 5 and 6
   describe, with your task's ID in the CHECKPOINT.

## Numbering and records

- Findings are `FND-###`, numbered across the whole run: take the highest number in any
  family file and add 1. Never reuse or renumber an ID (INV-3).
- A finding names one control and one weakness; a weakness in two controls is two findings.
- Every other-than-satisfied determination lists its findings in `finding_refs`.
- A finding's `severity` uses the SP 800-30 scale (`very-low` to `very-high`); its
  `recommendation` says what would close it.

## What each task may change

| Task | May change | Must not change |
|---|---|---|
| A-3 | everything in the family files it writes | the SSP (journal a NOTE instead) |
| A-4 | missing `recommendation` and `severity` values, `finding_refs` links | any `result`, finding `description` or `status` |
| A-5 | `status: closed` on a finding that passed reassessment, its `sources`; the determination's `result` and a summary that keeps the A-3 result | a finding's original `title`, `description` or `severity` |
| M-2 | determinations of controls due this cycle; new findings; closing findings on evidence | determinations of controls not due |

Why: the report keeps the original results and shows what changed after them
(SP 800-37r2 Task A-5: assessors update the report but do not change original results).

## Short forms

`_shared/ssp-batching.md` "Short forms" applies: a satisfied or inherited determination
takes one or two sentences naming the evidence. An other-than-satisfied determination and
every finding are written in full.

## Citations

- SP 800-53Ar5 §3.3 (conducting assessments):
  `uv run rmf refs show SP800-53AR5 --section "3.3 CONDUCT SECURITY AND PRIVACY CONTROL ASSESSMENTS"`.
- SP 800-53Ar5 Appendix E (assessment findings and reports):
  `uv run rmf refs show SP800-53AR5 --section "APPENDIX E"`.
- DoDI 8510.01 Table 5, Task A-3 (reuse test events and prior results):
  `uv run rmf refs show DODI8510.01 --page 17 --anchor "Task A-3 Control Assessments"`.
- SP 800-37r2 Task A-5 (reassessment does not change the original results):
  `uv run rmf refs show SP800-37R2 --section "TASK A-5"`.
