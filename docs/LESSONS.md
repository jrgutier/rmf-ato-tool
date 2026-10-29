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

## L-0011 · 2026-10-29 · run: phase-2 · tags: oscal, versions
- Symptom: The trestle spike imported the oscal-content v1.6.0 catalog (OSCAL 1.2.3) without restamping, contradicting the plan's verified fact and L-0004's root cause.
- Root cause: compliance-trestle 5.2.0 defines OSCAL_VERSION_REGEX ^1\.2\.[0-1]$ but its OscalVersion validator sets strict_version = False and returns early, so any version loads. Planning read the regex, not the behaviour.
- Fix: Recorded the real behaviour in docs/spikes/trestle-author.md; kept L-0004's rule (inputs are read as raw JSON, generated OSCAL is 1.2.1) because a future trestle may turn strict mode on.
- Rule: Verify a tool-behaviour claim by running the tool on the real input before building on it; a constant in the source is not evidence of enforcement.
- Promotion: none — L-0004's rule is unchanged and already enforced by REF-005 (test_oscal_versions_consistent); this corrects only its stated cause

## L-0012 · 2026-10-29 · run: phase-2 · tags: refs, required
- Symptom: The plan's required set pinned SP800-18R1, which NIST withdrew on 2026-06-30 when it published SP 800-18 Rev. 2.
- Root cause: The reference inventory was written from memory with "check for r2" as a follow-up; the superseding revision appeared after the inventory was drafted.
- Fix: Added SP800-18R2 (auto, nvlpubs) to the index and to REQUIRED_IDS; kept SP800-18R1 required for AC-1 with a revision_note that it is withdrawn.
- Rule: When fetching references, check each landing page for "Withdrawn"/"Superseded by"; add the superseding revision to the required set rather than replacing the pinned ID.
- Promotion: check: test_required_reference_ids_pinned

## L-0013 · 2026-10-29 · run: phase-2 · tags: refs, extract
- Symptom: Under the plan's "outline when present, else regex" rule, SP800-37R2.toc.yaml had no RMF task headings, while bookmarked paragraphs ("Potential Inputs: ...") became headings. With the §6.7 regex added, tasks M-2..M-7 were still missing.
- Root cause: The Word-generated 800-37r2 outline bookmarks whole paragraphs instead of tasks and appends footnote marks ("3.2 CATEGORIZE73F"). The PDF prints "Task M-2" in mixed case, and the TASK pattern was case-sensitive. Most task statements run past the 14-word guard.
- Fix: Outline titles now pass the same §6.7 guards (no trailing punctuation or "...", Word "NNF" marks stripped), and each must be found on its page. The regex set runs alongside the outline, with the numbered pattern off when the outline numbers sections. TASK matches case-insensitively and emits "TASK X-n" as the heading, leaving the statement in the body.
- Rule: Treat a PDF outline as untrusted input. Filter it with the heading guards and confirm every heading against the page text.
- Promotion: check: test_80037_toc_has_all_47_task_headings

## L-0014 · 2026-10-29 · run: phase-2 · tags: refs, extract
- Symptom: Extracted text showed glued table words ("TASKP1 - RISKMANAGEMENTROLES"), broken words throughout 800-53A ("relaonships", "se?ngs"), out-of-order reference entries in 800-160v1r1, and the first body lines of SP 800-60 Vol. 2 stripped as "headers".
- Root cause: PDF geometry and encoding can't be taken at face value. PyMuPDF Table.extract() glues words in PDFs that position each glyph. 800-53A maps ligature glyphs (ti, tt, ft) to private-use code points, and the mapping differs per font. 800-160v1r1's font metrics inflate line boxes to about five line heights. A fixed 3-page repeat threshold treats a recurring first body line as a running header.
- Fix: Table cell text is built from words. Private-use glyphs are resolved per font against the document's own vocabulary (recorded as glyph_map in the preamble). Layout uses baselines, not line boxes. The repeat threshold is now 5% of pages, and short footers are caught as row mates of the page number.
- Rule: Derive layout from baselines and word boxes, and resolve glyphs against the document itself. Never trust line-box heights, Table.extract() text or private-use code points.
- Promotion: check: test_golden_excerpts

## L-0015 · 2026-10-29 · run: phase-2 · tags: refs, browser, ops
- Symptom: In the user's Chrome (Claude in Chrome), DODI8510.01 saved to ~/Downloads, but the next 9 browser-assisted PDFs never landed. Scripted anchor downloads, a real click on an injected link, and "allow automatic downloads" all produced no file. Posting the bytes to a 127.0.0.1 receiver hung. www.cnss.gov showed a browser error page for the whole site.
- Root cause: the browser gates every download after the first, and any page→localhost transfer (Local Network Access), behind interactive prompts that need the user present. cnss.gov fails in a real browser too, not only for scripted TLS clients.
- Fix: imported DODI8510.01 only. The other 9 stay pending-acquisition, with direct URLs recorded in the Phase 2 handoff. CNSSI1253 waits for a user-supplied copy or the §7.6 degraded policy. Declined Playwright or headless fetching to get past the 403s (bot-detection circumvention) and clicking through certificate errors.
- Rule: run the browser-assisted acquisition only while the user is at the machine. Expect one prompt per site for multiple downloads; one download per page load avoids the batch block.
- Promotion: none — operator procedure, documented in playbooks/_ops/fetch-blocked-refs.md "Practical notes"

## L-0016 · 2026-10-29 · run: phase-2 · tags: refs, tls, browser
- Symptom: www.cnss.gov failed TLS verification in curl, Python and the user's real browser (whole-site error page). Its openDoc.cfm links then redirected to error_page.cfm?EC=09 even with valid TLS.
- Root cause: L-0003's diagnosis ("incomplete chain") was wrong. cnss.gov serves a DoD PKI certificate (DOD SW CA-82, chaining to DoD Root CA 3–6), which public trust stores don't contain. openDoc tokens are bound to the session cookie set by the listing page.
- Fix: downloaded DISA's public DoD PKI bundle (dl.dod.cyber.mil, file hashes checked against its manifest) into the scratchpad. Used it as `curl --cacert` for these fetches only (full verification; no system or browser trust change; user approved). Loaded Instructions.cfm and the openDoc links within one cookie jar. Imported CNSSI1253 (2022-08-01) and split the overlay placeholder into 4 entries (1253E Att1/Att5, 1253F Att2 2025, Att6). Browser downloads (L-0015) now work as one download per fresh tab.
- Rule: a .mil/.gov TLS failure usually means a DoD PKI chain. Verify against DISA's DoD root bundle scoped to the call; never disable verification or change system trust. For cnss.gov, fetch documents within the listing page's session.
- Promotion: none — operator procedure, documented in playbooks/_ops/fetch-blocked-refs.md "Practical notes"

## L-0017 · 2026-10-29 · run: phase-3a · tags: framework, citations
- Symptom: Once the DoD instructions were imported (p2x), several planned acquisition entities had no source. DoDI 5000.88 3.5.a requires SRR or SFR, PDR, CDR, SVR/FCA, PRR and PCA, so the plan's RV-ASR (used in its C-2 task example) and an in-service review were unsupported. DoDI 5000.85 also marks phases and milestones only with lines like "3.6. MSA PHASE.", which its toc does not list as sections.
- Root cause: The plan's review, milestone and phase lists were written from memory of older acquisition guidance before the sources could be read; a section-only citation habit assumed every heading reaches the toc.
- Fix: Dropped RV-ASR and RV-ISR (tasks aligned to them now align to milestones only) and cited every phase, milestone, review, decision and pathway by page and anchor in the imported DoDI 5000.85/5000.88/5000.89/5000.02/5000.90 and DoD CIO cATO text.
- Rule: Add a structural framework entity only with a citation that resolves in the imported text (check it with rmf refs show); treat plan lists as a starting point, not a source, and use page+anchor where the toc has no heading.
- Promotion: none — FW-CITE-001 requires citations only on tasks, artifacts, personas and decisions (plan §6.5); every phase, milestone, review and pathway now cites a source that FW-CITE-002 resolves

## L-0018 · 2026-10-29 · run: phase-3.5 · tags: seeds, scope
- Symptom: With only the plan §7.3 seed set, a fresh skeleton run failed RUN-CFG-001: "C-1 needs ART-REQ (input), whose producer(s) P-15 are not in scope" (and the same for S-1).
- Root cause: The plan's seed table was written from the producers its author remembered, not derived from the in-scope tasks' inputs; Phase 3a made ART-REQ an input of C-1 and S-1.
- Fix: Seeded ART-REQ (from P-15) in tests/agent/seeds/esg-skeleton and scenarios/skeleton.yaml; tests/agent/README.md lists the full seed set.
- Rule: Derive a scenario's seed set by running rmf check --rules RUN-CFG-001 on a fresh run of the scenario, never from a hand-written table.
- Promotion: check: RUN-CFG-001

## L-0019 · 2026-10-29 · run: phase-3.5 · tags: templates, workspace
- Symptom: Explicit Markdown heading anchors ({#mission}) in templates/workspace/product broke rendering: jinja reported "Missing end of comment tag".
- Root cause: rmf new renders every product template through jinja for {{ slug }}, and jinja reads Markdown's {#id} as the start of a comment.
- Fix: The product templates cite headings by GitHub-style slug instead of explicit anchors; the ESG test product, which is not rendered, keeps {#id}.
- Rule: Files under templates/workspace/ never contain "{#"; product headings are cited by slug.
- Promotion: none — rmf new aborts with a template error rather than failing silently, and templates/workspace/product/README.md states the slug convention

## L-0020 · 2026-10-29 · run: phase-3.5 · tags: yaml, run-data
- Symptom: A boundary.yaml written in YAML flow style ({description: ..., sources: [...]}) failed RUN-FM-001 with "Additional properties are not allowed"; an ESG seed file failed its schema the same way.
- Root cause: Commas inside an unquoted flow-mapping value split one description into several keys.
- Fix: Rewrote both files in block style with double-quoted free text; every templates/data file uses that style.
- Rule: Run-data YAML uses block style with double-quoted free text; flow style only for short lists of IDs or trace tokens.
- Promotion: none — RUN-FM-001 already catches it, and the rule is step 6 of playbooks/00-run-protocol.md

## L-0021 · 2026-10-29 · run: phase-3.5 · tags: agent-lane, tooling
- Symptom: The plan's isolation fallback (retry the probe with --bare) cannot work under the user's Claude Code login, and a bare session would not see AGENTS.md.
- Root cause: In claude 2.1.312, --bare reads Anthropic auth only from ANTHROPIC_API_KEY or an apiKeyHelper (never OAuth or the keychain) and skips CLAUDE.md auto-discovery.
- Fix: scripts/agent-run.sh falls back to --bare only when ANTHROPIC_API_KEY is set, passes AGENTS.md with --append-system-prompt, and otherwise stops with that reason.
- Rule: Check every claude flag the harness relies on against `claude --help` of the installed version before planning around it; --bare means API-key auth and no auto-loaded instructions.
- Promotion: none — harness behaviour, documented in the scripts/agent-run.sh header and enforced by its isolation probe at run time

## L-0022 · 2026-10-29 · run: phase-3.5 · tags: cli, agents
- Symptom: `rmf` output that an agent parses (findings, `next:` lines, the baseline id to copy into facts.yaml) broke across lines when not printed to a terminal.
- Root cause: rich.Console wraps text at 80 columns when stdout is not a TTY, which is always the case for agents and subprocess capture.
- Fix: The CLI consoles use soft_wrap=True, and the run commands print plain lines with typer.echo.
- Rule: CLI lines meant for agents or scripts are never wrapped; use typer.echo or a soft-wrapping console, and keep --format json for anything structured.
- Promotion: none — fixed once in rmf_tool.cli's shared consoles; there is no second place to repeat it

## L-0023 · 2026-10-29 · run: phase-3.5 · tags: agent-lane, tooling
- Symptom: the agent-run isolation probe failed. Under `--setting-sources project --strict-mcp-config`, the headless session still loaded the user's skills and slash commands, and the init event listed 3 plugins. A $0.10 probe then stopped with `error_max_budget_usd` after answering.
- Root cause: `--setting-sources project` does not stop user skills and commands from resolving, so it is not enough on its own. The 3 plugins were Claude Code's own (`source: <name>@builtin`), not user-installed. A minimal headless turn with the default system prompt costs about $0.16 cold.
- Fix: session argv adds `--disable-slash-commands`. The probe ignores plugins whose source ends in `@builtin`. Probe budget raised to $0.30. Verified: no user skills, commands or MCP, and a canary question about the global CLAUDE.md (oh-my-claudecode) answers NO. `check_argv` now refuses an argv without the flag.
- Rule: isolate headless agent runs with `--setting-sources project --strict-mcp-config --disable-slash-commands`, and judge leaks by plugin source, not plugin count.
- Promotion: check: test_agent_run_dry

## L-0024 · 2026-10-29 · run: phase-3.5 · tags: agent-lane, paths
- Symptom: after the first real skeleton agent run (8 sessions, 0 errors), test_committed_run_rechecks_clean failed with 347 TRACE-002 errors: "product file … not found under ../../../../tests/agent/products/esg".
- Root cause: agent-run.sh rewrote the copied run's `product:` path for a depth of four, but `tests/agent/results/<s>/run` is five levels below the repo root. The test could only exercise this after a real (paid) run, so the dry run and CI never covered it.
- Fix: the rewrite now uses five `../` levels; the committed result's run.yaml is corrected; `pytest -m agent tests/agent` passes; `rmf check tests/agent/results/skeleton/run --final` reports 0 errors.
- Rule: when a harness relocates a run, recompute relative paths from the destination's real depth, and re-check the relocated copy before reporting success.
- Promotion: check: test_committed_run_rechecks_clean
