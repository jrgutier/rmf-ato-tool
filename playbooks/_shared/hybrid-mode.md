# Hybrid mode

A run's `run.yaml:mode` is `synthetic` (the agent role-plays every persona) or `hybrid`
(real people answer for some personas, the agent role-plays the rest). This file covers
what changes in hybrid mode. In synthetic mode, skip it.

## Steps

1. **Read the roster.** `run.yaml:humans` maps persona IDs to a person's name, or to `null`
   when nobody is assigned:

   ```yaml
   humans:
     PER-ISSO: Jordan Example
     PER-AO: null
   ```

   A persona with a name is answered by that human; a persona that is absent or `null` is
   role-played. Why: HYB-003 rejects a `respondent: human` answer for a persona not named
   here, so the roster is the only authority on who is real.
2. **Ask the human in chat.** For a named persona, put the questions to the user in the
   conversation, one interview at a time, and say which persona you are addressing. Record
   the reply verbatim (trim only greetings) as `respondent: human · tag: HUMAN`. Never
   rephrase a human answer into something they did not say. Why: a human answer is evidence
   only if it is their words.
3. **When the human cannot answer.** If the person says they don't know, or is unavailable,
   role-play the persona for that question and mark the answer
   `respondent: simulated · tag: SIMULATED · fallback: human-unavailable`. Why: the reader of
   the package must be able to see which answers a real person did not give.
4. **Never simulate a reserved decision.** If the human for PER-AO is unavailable, do not
   simulate the authorization decision (R-4) or the categorization approval (C-3): journal
   a NOTE and stop (`00-run-protocol.md`, stop conditions). Why: only the AO decides
   (DoDI 8510.01 §4.4.a(5)); a simulated decision in a hybrid package would read as real.
   In synthetic mode these decisions are simulated like every other answer.
5. **Tag every agent invention.** Anything the agent supplies that no human said and no
   product file states is either a `SIMULATED` answer or an `ASSUMPTION` in
   `assumptions.yaml`, cited by its token (`_shared/tagging-and-traceability.md`). Why:
   HYB-001 fails on untagged invented content, and `reports/assumptions.md` (HYB-002) is
   how reviewers find every invented claim.
6. **Build and check as usual.** `rmf build` regenerates `reports/assumptions.md`;
   `rmf check` runs HYB-001 and HYB-002 on every task.

## What counts as an assumption

Record an `ASSUMPTION` when a claim is needed for an output but neither an answer nor the
product material supports it, for example "the CSSP retains audit records for one year".
Give the persona who would confirm it in a real run. Prefer asking (a human, or another
persona in character) over assuming; an assumption is the last resort, and the report shows
how many there are.

## Citations

- DoDI 8510.01 §4.4.a(5), AO decisions are not delegated:
  `uv run rmf refs show DODI8510.01 --page 28 --anchor "Do not delegate authorization decisions"`.
- SP 800-37r2 Task R-4 (the AO's decision) and Task C-3 (categorization approval):
  `uv run rmf refs show SP800-37R2 --section "TASK R-4"`.
