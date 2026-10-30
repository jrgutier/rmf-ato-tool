# Cold start: resume an RMF run from disk

You are joining an RMF run that another session left part-way. Nobody will answer
questions, and no notes from earlier sessions exist beyond what is in the repository.

Read `AGENTS.md` first and follow it: it says where the run protocol is and how state is
derived from disk. The run is the only directory under `runs/`. Bring the run to the point
where `uv run rmf build <run>` and then `uv run rmf check <run> --final` report 0 errors,
without changing anything outside the run directory except `docs/LESSONS.md`.

Bash is limited to `uv run rmf ...`; use the Read, Write, Edit, Glob and Grep tools for
files. Write run files whole (INV-8); the journal is the one file you append to, using the
`now:` time from `uv run rmf status`.
