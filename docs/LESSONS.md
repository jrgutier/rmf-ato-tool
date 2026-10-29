# Lessons

Append-only log of what went wrong, why, and the rule that prevents it.
`uv run rmf lessons check` enforces the format and append-only property (LES-002)
and rejects `Promotion: pending` (LES-003). The entry format and the promotion
rule are described in AGENTS.md (`## Learned rules`). Add new entries at the end
with the next ID; never edit or delete an existing entry.

## L-0001 · 2026-10-29 · run: planning · tags: refs, fetch
- Symptom: Liveness probe reported NIST PDFs missing (HTTP 404).
- Root cause: nvlpubs.nist.gov returns 404 on HEAD but 206 on GET.
- Fix: Liveness uses a ranged GET (Range: bytes=0-1023), never HEAD.
- Rule: Never use HEAD to probe reference URLs; use a ranged GET.
- Promotion: check: test_fetch_uses_ranged_get_never_head

## L-0002 · 2026-10-29 · run: planning · tags: refs, fetch
- Symptom: DoDI downloads from esd.whs.mil fail with HTTP 403.
- Root cause: esd.whs.mil blocks scripted fetches.
- Fix: Mark these entries acquisition: browser-assisted; import via playbooks/_ops/fetch-blocked-refs.md + rmf refs import.
- Rule: Blocked sources are acquired browser-assisted by the user; never spoof a User-Agent.
- Promotion: check: test_browser_assisted_entries_skipped_by_fetch

## L-0003 · 2026-10-29 · run: planning · tags: refs, tls
- Symptom: TLS verification fails for cnss.gov.
- Root cause: cnss.gov serves an incomplete certificate chain.
- Fix: Fetch CNSSI 1253 browser-assisted; keep TLS verification on.
- Rule: Never use verify=False; route TLS-broken sources through browser-assisted import.
- Promotion: AGENTS.md INV-7 | check: test_no_tls_verify_disable

## L-0004 · 2026-10-29 · run: planning · tags: oscal, versions
- Symptom: trestle model load rejects the oscal-content 800-53r5 catalog.
- Root cause: compliance-trestle 5.2.0 accepts only OSCAL 1.2.0/1.2.1; oscal-content v1.5.0/v1.6.0 catalogs are 1.2.2/1.2.3.
- Fix: Read catalogs/profiles as raw JSON with a same-minor (1.2.x) rule; generate 1.2.1 documents.
- Rule: Never load input catalogs/profiles through trestle models; pin generated OSCAL to trestle's version.
- Promotion: check: REF-005

## L-0005 · 2026-10-29 · run: planning · tags: oscal, schema
- Symptom: jsonschema validation crashes or skips patterns in the OSCAL 1.2.1 schemas.
- Root cause: The schemas use \p{L}, which Python re cannot compile.
- Fix: Extend the jsonschema pattern/patternProperties validators to use the regex package.
- Rule: OSCAL schema validation always uses the regex-backed validator plus FormatChecker.
- Promotion: check: test_all_schema_patterns_compile

## L-0006 · 2026-10-29 · run: planning · tags: agent-lane, tooling
- Symptom: Headless agent runs could not execute Bash, or failed on an unknown flag.
- Root cause: In claude 2.1.312 -p mode, --permission-mode acceptEdits denies Bash, and --max-turns does not exist.
- Fix: Use a scoped --allowedTools "Bash(uv run rmf:*)" Read Edit Write Glob Grep plus --max-budget-usd; never bypassPermissions.
- Rule: Headless agent runs use only a scoped allowlist and a budget cap.
- Promotion: check: test_agent_run_dry (argv assertions)

## L-0007 · 2026-10-29 · run: planning · tags: tooling
- Symptom: Planning-session state lost fields after an update.
- Root cause: The OMC state_write tool replaces the whole state object rather than merging.
- Fix: Read the state, merge locally, and write the full object back.
- Rule: Treat state_write as replace-all; always read-merge-write.
- Promotion: none — planning-tooling behaviour outside this repo's code

## L-0008 · 2026-10-29 · run: phase-1 · tags: ci, lfs
- Symptom: The planned CI job (checkout with lfs: true plus an LFS cache keyed on git lfs ls-files) would never save an LFS transfer.
- Root cause: actions/checkout with lfs: true downloads every LFS object before the cache restore step runs.
- Fix: Check out with lfs: false, list LFS oids into .lfs-assets-id, restore .git/lfs from the cache keyed on that file, then git lfs pull.
- Rule: In CI, restore the LFS cache before pulling LFS objects; never combine lfs: true with an LFS cache.
- Promotion: none — one-time CI workflow layout, explained inline in .github/workflows/ci.yml

## L-0009 · 2026-10-29 · run: phase-1 · tags: tooling, cli
- Symptom: rmf crashed at import with ModuleNotFoundError: No module named 'click'.
- Root cause: Typer >= 0.26 vendors Click as the private typer._click package and no longer installs click.
- Fix: Do not import click; walk typer.main.get_command(app) by its commands mapping, and test with typer.testing.CliRunner.
- Rule: Never import click directly; use only Typer's public API and duck-type the built command tree.
- Promotion: check: test_command_paths_from_typer_app

## L-0010 · 2026-10-29 · run: phase-1 · tags: team, git
- Symptom: Phase 1 ended up with two commits under the same message. The worker committed the phase, and the lead, believing it was uncommitted, committed a follow-up (pyright config) with a duplicate message.
- Root cause: commit ownership was changed mid-task by message. The worker acted on the first message ("commit at phase close") after its report was already sent, so the lead's view was stale and both parties committed.
- Fix: amended the lead's commit message to describe its real content (pyright venv config); history is otherwise correct.
- Rule: exactly one party owns the phase-close commit, and it is fixed in the worker's spawn prompt. The lead runs `git log` before committing and never commits while a worker is live in the same tree.
- Promotion: none — team-process rule; recorded in .omc/handoffs/team-plan.md
