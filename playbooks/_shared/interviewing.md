# Interviewing

How to run and record the interviews a task playbook asks for. Interviews are the evidence
behind most run claims: artifacts cite their answers as `INT-###.A#`.

## Steps

1. **Pick the respondents.** Use the personas in the playbook's `## Interviews` section.
   Look up each one's stakeholder in `artifacts/ART-STAKE.md` (from P-9 on; before P-9 writes it, use the product's `stakeholders.md` and ART-ORG-CONTEXT). Why: the RACI in the header
   says who is responsible or consulted; the register says who speaks for them in this run.
2. **Number the interview.** Find the highest `INT-###` under `interviews/` and add 1
   (start at `INT-001`). Numbers are global to the run, never per task, and never reused.
   Why: trace tokens must resolve to exactly one answer (TRACE-002).
3. **Prepare questions.** Take 3 to 8 questions from the persona card's
   `## Question bank by step` and the playbook's question focus, and adapt them to what the
   inputs leave open. Ask about facts the outputs need, not about what the product material
   already states. Why: an interview that repeats the product file adds no evidence.
4. **Ask and answer.**
   - **Synthetic mode (and hybrid personas without a human):** answer in character, from the
     persona card's `## Role-play guidance`, using only what that persona would know
     (`## What they know and don't know`). Ground each answer in the product material or an
     earlier answer, and list that grounding in `basis`. Why: an ungrounded simulated
     answer is invention that later reviewers cannot check.
   - **Hybrid mode, persona listed in `run.yaml:humans` with a name:** ask the human in chat
     and record their words (`_shared/hybrid-mode.md`).
   - When the persona would not know the answer, say so in character and either ask the
     persona who would know, or record an assumption (`_shared/tagging-and-traceability.md`).
     Never make a persona answer outside their role.
5. **Write the file whole** at `interviews/INT-###-<TASK>-<PERSONA>.md`
   (example: `interviews/INT-007-S-4-PER-ISSO.md`), using `templates/interview.md`.
   Why: INV-8; a half-written interview leaves dangling anchors.
6. **Cite the answers** you use, by anchor, in the artifacts and data you write next.

## File format

```markdown
---
interview_id: INT-007
run_id: 20261105-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-11-05
topics:
  - "account management"
  - "audit logging"
---
# INT-007 — S-4 — PER-ISSO

### Q1 {#INT-007.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ac-2
**A1 {#INT-007.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]]
> Remote accounts are created by the identity service workflow after I approve the
> access request; I review the console account list every quarter.
```

Rules (INT-001, HYB-001, HYB-003 check them):

- Front-matter has exactly `interview_id`, `run_id`, `task`, `persona`, `date`, and
  optionally `topics`. `persona` is the one respondent; interview a second persona in a
  second file.
- Each question is an H3 `### Q<n> {#INT-###.Q<n>}`, numbered from 1 within the file.
- The line after it is `Asked of: <PER-ID> · Task: <TASK>`, plus ` · Control focus: <id>`
  when the question is about one control (OSCAL form: `ac-2`, `ac-2.1`).
- The answer header is `**A<n> {#INT-###.A<n>}** respondent: <simulated|human> · tag: <SIMULATED|HUMAN>`,
  then ` · basis: [[token]] [[token]]` when the answer rests on a file or another answer,
  then ` · fallback: human-unavailable` in the hybrid fallback case only.
- The answer text follows as a `>` block quote.
- `A<n>` answers `Q<n>`: one answer per question, same number.
- Tags are required in **both** modes. A simulated answer is always `tag: SIMULATED`.

## Interview counts

Each task needs at least its `min_interviews` (header) interviews with `task: <TASK>`;
the playbook may ask for more. Batch questions to one persona into one interview per task.
Why: the "done" test in `rmf status` counts interview files per task.

## Citations

- SP 800-37r2 Appendix D defines the roles personas stand for, and each task's "Potential
  Inputs" and roles say who supplies what:
  `uv run rmf refs show SP800-37R2 --section "ROLES AND RESPONSIBILITIES"`.
- DoDI 8510.01 §4.4 assigns the system-level roles that personas represent:
  `uv run rmf refs show DODI8510.01 --page 28 --anchor "activities of the SO, PM, UR, ISSM, and ISSO at the system level"`.
