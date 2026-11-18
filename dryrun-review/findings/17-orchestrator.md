# Findings: orchestration and the fork CI (orchestrator, after session 16)

### F-17-1: `rmf ci --profile fork` never checks the fork's own run
- Where: `src/rmf_tool/ci.py` (steps list), AGENTS.md fork workflow step 6
- Kind: gap
- Severity: major
- What happened: after session 16, `uv run rmf ci --profile fork --no-tests` printed PASS on
  every step while `rmf check runs/20261118-synthetic-01 --final` still reported 1 error
  (MRPT-001). The fork profile runs the fixtures (`valid_minimal`, `hybrid_minimal`), golden
  OSCAL, the framework and references; no step evaluates `runs/*/`. Fork workflow step 6 reads as
  the fork's gate, so a fork can be green with a failing package.
- Workaround used: ran `rmf check --final` and `rmf oscal validate` on the run directly.
- Recommendation: under `--profile fork`, add a step that runs `rmf check --final` (and
  `rmf oscal validate`) on every `runs/*/run.yaml`, or at least on the newest run, and fail on
  errors.

### F-17-2: Session units are the right granularity, and on-disk state survived a restart
- Where: `playbooks/00-run-protocol.md`, `_shared/resume.md`
- Kind: positive
- Severity: note
- What happened: 16 fresh sessions, each started cold with only the brief, the journal and the
  findings files, picked up exactly where the last left off from `rmf status`. The container
  restarted in the middle of session 15; the resumed session re-derived its state from disk and
  finished without loss.
- Workaround used: none.
- Recommendation: keep it; note in the protocol that the journal's closing NOTE (what the next
  session owes) was the most useful hand-off, and ask for it explicitly.

### F-17-3: The run's real cost is high even with 50 controls
- Where: whole run
- Kind: friction
- Severity: major
- What happened: 16 sessions, about 5.5 hours of agent time, about 2,400 tool calls and
  roughly 3.7 million sub-agent tokens for 43 tasks, 216 interviews (533 simulated answers),
  27 assumptions and 30 artifacts on a 50-control subset. The 524-control example cost 31
  sessions. Roughly a third of each session went to discovering record fields that only the
  rule source or the schema names (F-01-13, F-03-10, F-08-5), and to cross-task regressions
  (F-02-3, F-04-1, F-09-1, F-15-5).
- Workaround used: none.
- Recommendation: the doc and data-template fixes in the review (every required field in a
  `templates/data/*.yaml`, every rule a task owns listed in its playbook) would cut the most
  cost; second, make a plain `rmf check` surface cross-task regressions.

### F-17-4: Every session broke the "Bash only for `uv run rmf`" rule, and most broke INV-8
- Where: session brief (from `tests/agent/prompts/example-uas-gcs.md`), INV-8
- Kind: friction
- Severity: minor
- What happened: all 16 sessions used Python or grep/sed through Bash to read schemas, rule
  source or JSON check output, and most used targeted Edit calls on run YAML instead of whole
  writes. They did so because the information the tasks needed was not in the playbooks, and
  because `rmf check` output is hard to filter (it prints the full rule roster on every run,
  F-01-18, F-07-2).
- Workaround used: deviations were recorded in each findings file.
- Recommendation: add `rmf check --errors-only` / `--format json` filters suitable for agents,
  `rmf schema show <file>` to print a data file's required fields, and either relax INV-8 to
  "the file is whole and valid after the write" or explain what partial edits break.

### F-17-5: The simulated timeline outruns the run's clock
- Where: `run.yaml as_of`, ASMT-010, MPOA-001, PRIV-003 (see F-12-2, F-14-6, F-15-1, F-16-1)
- Kind: gap
- Severity: major
- What happened: the run's clock stayed at 2026-11-18 while the assessment ran to 2026-12-11,
  the decision landed on 2027-01-25 and monitoring was recorded on 2027-02-01. Sessions had to
  invent two months of POA&M progress (ASM-025) to satisfy the date rules, and the only
  monitoring data predates the authorization.
- Workaround used: ASM-025 and ASM-026, stated uniformly rather than case by case.
- Recommendation: give a synthetic run a simulated clock (`rmf run clock set 2027-01-25`,
  recorded in the journal) that the date rules read, and let the product's monitoring folder
  be dated relative to the decision.

## Session summary

Ran `rmf ci --profile fork --no-tests` (PASS) and `rmf check --final` on the run (1 error,
MRPT-001); recorded the orchestration-level observations.
