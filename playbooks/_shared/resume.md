# Resume

Any session may start on a run another session left half-done, after a crash, a budget stop
or compaction. Resuming is safe because all state is on disk and every write is whole.

## Steps

1. **Ask the CLI, not your memory.** Run `uv run rmf status <run>`; its next action is the
   only starting point. Why: a summary of an earlier session can be stale; `rmf status`
   reads the files.
2. **Read the journal tail.** Read the last 20 lines of `<run>/journal.md` for RETRY and
   NOTE entries about the next task. Why: they record what went wrong last time and which
   lesson applies.
3. **Rebuild and check before writing.** Run `uv run rmf build <run>`, then
   `uv run rmf check <run> --task <next task>`. Why: a file cut short mid-write fails its
   schema or front-matter check; you need to know before you build on it.
4. **Redo broken files whole.** A file that fails its schema, or a family file missing
   controls it should have, is rewritten from its inputs: never patched, never appended.
   Why: INV-8; appending after a partial write duplicates records (SSP-DUP-001).
5. **Keep what passes.** Do not rewrite interviews, assumptions or artifacts that pass their
   checks; cite them as they are. Interview and assumption numbers continue from the highest
   on disk. Why: rewriting renumbers anchors that other files cite.
6. **Delete generated output if in doubt.** `oscal/`, `reports/`, `baseline.json` and
   `package/manifest.yaml` are deterministic; `rmf build`, `rmf baseline resolve` and
   `rmf package` recreate them.
7. Continue with `00-run-protocol.md` step 2.

## Done is derived

A task is done when all of these hold (`rmf status` computes it):

1. every output artifact exists and lists the task in `touched_by`;
2. every fact the task writes has `set_by_task: <task>`;
3. at least `min_interviews` interviews have `task: <task>`;
4. every rule that applies to the task's artifacts passes.

Nothing else marks a task done: not a journal entry, not a message.
