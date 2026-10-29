# Session units

A session is one agent conversation (for example one `claude -p` call). Each session does
one bounded unit of work and then ends, so no session runs out of context or budget halfway
through a file.

## Steps

1. **Know your unit.** The prompt names the RMF step (P, C, S, I, A, R or M) for this
   session. The unit is every active task of that step in the run's scope, in the order
   `rmf status` gives them.
2. **During S-4 and A-3, the unit is at most 3 families.** After the third family's
   CHECKPOINT, end the session even if the step has more families. Why: each family needs a
   catalog listing, interviews and a whole-file write; three is what fits safely.
3. **End after the CHECKPOINT** that completes the unit, or when `rmf status` names a task
   from another step. Do not start the next step's task. Why: the next session starts from a
   fresh context and `rmf status`, which is cheaper and safer than a long tail.
4. **End early when stuck.** Stop conditions are in `00-run-protocol.md`. Journal a NOTE
   saying why before you end.
5. **Make progress visible.** Each session must leave at least one new done task, covered
   control or determination. The harness compares `rmf status --format json` before and
   after; two sessions in a row without progress stop the run. Why: a stalled loop otherwise
   burns budget without result.

## Skeleton scenario units

| Session | Step | Tasks |
|---|---|---|
| 1 | P | P-10, P-11 |
| 2 | C | C-1, C-2, C-3 |
| 3 | S | S-1, S-4 (6 controls in 6 families; at most 3 families per session, so S may take 2 sessions) |
| 4 | A | A-2, A-3, A-6 |
| 5 | R | R-2, R-4 (run `rmf package` before R-2) |
