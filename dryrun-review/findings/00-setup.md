# Findings: setup (orchestrator, before session 01)

### F-00-1: The agent harness cannot drive a fork's own run
- Where: `scripts/agent-run.sh`
- Kind: gap
- Severity: major
- What happened: `--run-dir` rejects any path under `runs/` (`$RUN_DIR != runs/*`), and
  scenario mode needs a `tests/agent/scenarios/<s>.yaml` file and a `tests/agent/prompts/<s>.md`
  file. A fork's run lives at `runs/<run-id>/` (AGENTS.md fork workflow step 3), so the one
  tool that automates "one agent session per RMF step" works for upstream's test scenarios and
  the example, but not for the fork workflow it exists to serve. The harness also needs the
  `claude` CLI logged in, which is Claude Code specific although the repository is meant to be
  agent-agnostic.
- Workaround used: the dry run drove sessions with a generic sub-agent per session unit,
  using `dryrun-review/session-prompt.md` (adapted from `tests/agent/prompts/example-uas-gcs.md`).
- Recommendation: add a fork mode (`scripts/agent-run.sh --fork runs/<id>`) that copies the
  repo, drives the run and copies it back, with a generic prompt in `templates/` that a fork can
  edit, and document how to run the same loop with another agent CLI.

### F-00-2: No supported way to scope a fork run's controls
- Where: `framework/schema/run-config.schema.json` (`control_subset`)
- Kind: gap
- Severity: minor
- What happened: `control_subset` is described as "Test scenarios only". A fork that wants a
  quick rehearsal (a dry run, a training run, a single-release delta) has no supported way to
  limit S-4 and A-3 to part of the baseline; the alternative is roughly 500 statements and
  assessments.
- Workaround used: set `control_subset` (50 controls, every family) in run.yaml by hand and
  recorded it as a deviation. `rmf baseline resolve` appends `-SUBSET-50` to the baseline ID,
  which keeps the deviation visible in every artifact.
- Recommendation: make a rehearsal scope a documented run option (for example
  `rmf run init --rehearsal --controls FILE`) that stamps the package as partial.

### F-00-3: Product template lacks files the example and tasks rely on
- Where: `templates/workspace/product/`
- Kind: gap
- Severity: minor
- What happened: the template has no stakeholder file and no privacy file. The example
  product (`examples/uas-gcs/product/stakeholders.md`) has a stakeholders file that P-9 and
  later tasks lean on, and a PII-handling system needs the PIA status, SORN and authority
  somewhere. A program office filling in the template would not know to provide either.
- Workaround used: wrote `product/stakeholders.md` and `product/privacy.md` following the
  example's shape.
- Recommendation: add `stakeholders.md` and `privacy.md` (and a short "leveraged services"
  table for cloud-hosted systems) to the product template and its README.

### F-00-4: Software pathway mapped onto MCA phases
- Where: `framework/pathways.yaml` (PW-SWP `phases`), `product-profile.schema.json` (`current_phase`)
- Kind: friction
- Severity: note
- What happened: the software acquisition pathway has a planning phase and an execution phase,
  but `current_phase` must be a `PH-*` ID from the MCA spine and PW-SWP lists all five MCA
  phases. A software program has to pick an MCA phase that does not describe it (this run used
  PH-PD for "execution phase, MVCR pending").
- Workaround used: PH-PD, with the real state in `product/conops.md#program`.
- Recommendation: let a pathway declare its own phases (or map SWP planning/execution to the
  spine explicitly) and accept them in `current_phase`.

### F-00-5: `rmf doctor` reports qpdf missing in a fresh cloud container
- Where: `rmf doctor`
- Kind: note
- Severity: note
- What happened: `qpdf MISSING` (needed only by `rmf refs fetch`). Runs do not need it.
  Every `uv run` also prints a `UV_NATIVE_TLS` deprecation warning from the environment, not
  the repository.
- Workaround used: none needed.
- Recommendation: have `rmf doctor` mark qpdf as needed only for reference fetching, so a fork
  doing runs does not think its setup is broken.

### F-00-6: `rmf new` scaffolds cleanly (positive)
- Where: `rmf new efras --dir .`
- Kind: positive
- Severity: note
- What happened: product templates and the first run were created in one command, and
  `rmf status` immediately listed all 44 active tasks with what each is missing.
- Workaround used: none.
- Recommendation: none.

## Session summary

Scaffolded the workspace, wrote the EFRAS product package (fictional), set the lifecycle stop
(R-5 plus M-1, M-2, M-3, M-5) and the control subset.
