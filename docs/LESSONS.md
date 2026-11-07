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

## L-0025 · 2026-10-29 · run: phase-4 · tags: framework, ci
- Symptom: once a p4 `rmf ci` step for FW-MAN-001 existed, `rmf validate --profile p4` and the p3a ci step run under profile p4 stopped with "active rule(s) not implemented in this version: FW-MAN-001"; test_framework_rules_are_implemented_by_validate also failed.
- Root cause: `rmf validate` treats every active FW-* registry rule as its own, but FW-MAN-001 (`rmf render --check`) and FW-PB-002 (`rmf playbooks sync --check`) are enforced by other commands with their own ci steps.
- Fix: framework/validate.py has CHECKED_ELSEWHERE (rule -> command); active_rules() skips those rules, and the registry test accepts a rule found in IMPLEMENTED or CHECKED_ELSEWHERE. The ci-level guard (unimplemented_phases) still stops a vacuous pass.
- Rule: a FW-* rule enforced outside `rmf validate` is listed in CHECKED_ELSEWHERE in the same change that adds its ci step.
- Promotion: check: test_framework_rules_are_implemented_by_validate

## L-0026 · 2026-10-29 · run: phase-6 · tags: refs, cnssi, extraction
- Symptom: in references/text/CNSSI1253.md the Appendix D tables have between 23 and 42 columns per page. In AC-4's row ("√4 … X X X X") the text does not show which of the nine C/I/A L/M/H cells the marks sit in. pymupdf `find_tables` also shifted cells on rows whose ID sits in a different cell (AC-2(11), AC-3).
- Root cause: the text extractor drops empty table cells and splits merged ones, so the column position of a symbol is lost. The order of the symbols in a row survives.
- Fix: rmf_tool.cnssi1253 places each X/+/-- under the nearest L/M/H header using the PDF's word coordinates, then requires each row's symbol order to equal the text's. All 1,189 rows matched and no override was needed. X/-- per level also agrees with the 800-53B profiles, apart from 3 known `+` rows. The YAML is regenerated with `--check`.
- Rule: never read a table column from extracted text; take positions from PDF geometry, check them against the text, and commit the generator together with its output.
- Promotion: check: test_committed_yaml_is_regenerated_output

## L-0027 · 2026-10-29 · run: phase-3b · tags: framework, playbooks
- Symptom: Phase 3b changed only prose fields, but `rmf playbooks sync --check` then reported 21 FW-PB-002 errors, and `rmf validate` could not have caught an accidental structural edit, because a changed depends_on or RACI value is still valid YAML.
- Root cause: a task's `purpose` is copied into every playbook header (playbooks_sync.header), so prose and generated headers are coupled. The structural-diff guard that would stop a prose lane from editing structure is deferred to v1.1 (plan Phase 3b).
- Fix: the lane compared every non-prose field of framework/**/*.yaml with HEAD after each splice, checked that names were unchanged and that no existing citation was lost; it reported OK on all 13 files. The playbook owner (worker-p5b) was asked to re-run `rmf playbooks sync`.
- Rule: a prose-only framework edit is followed by a structural diff against HEAD and by `rmf playbooks sync`, in the same change.
- Promotion: none — the structural-diff guard is deferred to v1.1 by the plan; FW-PB-002 already catches stale headers

## L-0028 · 2026-10-29 · run: phase-5 · tags: personas, citations
- Symptom: three locations in the new persona cards were wrong on the first draft. DoDI 5000.85 was cited as "§3C.1" (it is §3.1.b(1)). The DoDI 5000.89 T&E WIPT and evaluation framework items were cited under §3.2 (they sit in §3.1). A DoDI 5000.88 anchor was given page 15 (it is on page 14).
- Root cause: section and page numbers were read from TOC entries and from surrounding `sed` output, not from the heading line and the `<!-- page N -->` marker just above the passage. Before Phase 5 nothing checked the citation commands in persona cards.
- Fix: corrected all three. FW-PER-002 (rmf_tool.framework.personas_check) now resolves every `uv run rmf refs show` command in a card's `## Citations`, the same way FW-CITE-002 resolves framework citations, and the 22 cards pass.
- Rule: give every cited claim in a card or playbook a `rmf refs show` command and run it; take section numbers from the heading line and pages from the nearest page marker above.
- Promotion: check: FW-PER-002

## L-0029 · 2026-10-29 · run: phase-3b · tags: framework, decisions
- Symptom: AD-IATT was `decided_in: [R-4]`, but A-3's entry criterion needs an IATT already in place for live-network test events, and R-4 comes after A-3 in the task DAG. The framework therefore modelled the interim test authorization as granted after the testing it authorizes.
- Root cause: in 3a all AO decisions were attached to R-4 (the authorization decision task). An IATT is a separate, earlier AO decision, made with assessment-plan approval, before DT&E on live networks.
- Fix: AD-IATT is now `decided_in: [A-2]` (the AO is Accountable for A-2). A-2's aligned_with.decisions includes AD-IATT; R-4's no longer does; A-3 keeps it, because A-3 consumes it. `rmf validate --profile p3b` reports 0 errors.
- Rule: a decision's decided_in task must precede every task whose entry criteria depend on that decision.
- Promotion: none — single modelling fix; candidate rule for v1.1 (decision ordering vs. entry criteria needs prose parsing)

## L-0030 · 2026-10-29 · run: phase-6 · tags: oscal, builders
- Symptom: With the POA&M builder wired into `rmf build`, the SAR-POAM-001 negative fixture (delete the only POA&M item) crashed `rmf check` with a pydantic ValidationError instead of reporting findings.
- Root cause: `items: []` is valid against poam-items.schema.json, but OSCAL requires at least one poam-item. The trestle model rejected the mapped body, and only NotBuildable was caught. A SAP that excludes every baseline control has the same gap (reviewed-controls needs include-controls).
- Fix: oscal.common.serialize turns any trestle ValidationError into NotBuildable, so the document is reported as "not built", never a crash. The POA&M and SAP builders also name the two known cases in their reasons.
- Rule: An OSCAL builder never assumes schema-valid run data maps to a valid OSCAL document. Check every OSCAL list with minItems that a run-data list feeds, and route trestle rejections through NotBuildable.
- Promotion: check: test_trestle_rejection_is_not_buildable

## L-0031 · 2026-10-29 · run: phase-5 · tags: playbooks, tooling
- Symptom: a quick inventory script reported all 47 playbooks as `authored`, including the 21 generated ones, because it checked whether the file contained `rmf:body authored`.
- Root cause: the generated-body banner says "change the marker above to `rmf:body authored`", so substring detection misread it. `playbooks_sync` had the same weakness: an authored body that quotes the generated marker would have been treated as generated and overwritten by the next `rmf playbooks sync`.
- Fix: `playbooks_sync._body_kind` takes the first `<!-- rmf:body authored|generated -->` that stands on a line of its own, and every sync and check path uses it.
- Rule: detect CLI-owned markers as whole lines, never as substrings, because docs and banners quote them.
- Promotion: check: test_marker_must_stand_on_its_own_line

## L-0032 · 2026-10-29 · run: phase-6 · tags: fixtures, upstream-hash
- Symptom: Run-rule tests on copies of valid_minimal began reporting RUN-STALE-001 as soon as other lanes edited framework/, playbooks/ or templates/. A test that compared every finding failed, although the run content was unchanged.
- Root cause: A fixture run commits an upstream_hash. Any upstream edit changes the union hash, so a committed hash can never stay current while the template evolves.
- Fix: tests copy fixture runs with conftest.copy_run, which re-stamps upstream_hash to the current union hash. The committed fixtures may show only the RUN-STALE-001 warning (test_committed_base_has_no_errors). ADR-0001 records the hash variant in run.yaml (upstream_hash_basis).
- Rule: Tests that mutate a fixture run start from copy_run, never a plain copytree, and assert on the findings the mutation causes; RUN-STALE-001 on a committed fixture is expected drift, never an error.
- Promotion: check: test_check_rules.py::test_base_has_no_findings

## L-0033 · 2026-10-29 · run: phase-5 · tags: baseline, facts
- Symptom: worker-p5b found that a tailoring add or remove under `control_subset` changed `baseline.json:baseline_id` (`-SUBSET-n` counted the post-tailoring selection), so FACTS-001 would fail against S-1's `baseline_id` fact, which S-2 is not allowed to write.
- Root cause: baseline_id mixed the selection basis with the tailoring result. One fact had two effective writers (S-1 by value, S-2 by side effect).
- Fix: baseline.py now suffixes `-SUBSET-{len(control_subset)}`, the configured size, so tailoring never changes the ID. The S-2 playbook step 5 now says the IDs must match and to stop only on a basis change. test_baseline and pipeline_minimal pass; valid_minimal `--final` has 0 errors.
- Rule: identifiers that are facts must derive only from inputs owned by the fact's single writer.
- Promotion: check: FACTS-001

## L-0034 · 2026-10-29 · run: phase-6 · tags: ci, profiles, tests
- Symptom: at fan-out integration, closing p3b/p4/p5/p6 made `rmf ci --profile p6` exit 2 ("profile p6 includes phase(s) with no checks: p3b"). Two test_framework_cli tests that pass `--profile p3a` then failed, because p5 rules (FW-PER/FW-PB) ran against framework_mini.
- Root cause: p3b's verify (`rmf validate --profile p3b`) never got a ci.STEPS entry. `--profile pX` means closed ∪ {pX}, so tests that pin only `--profile` still depend on which `.phases/*.closed` markers the repo has.
- Fix: added a p3b ci step (`rmf validate (p3b, all citations resolvable)`, p3a step `unless="p3b"`, p3b step `unless="p5"`). test_framework_cli now monkeypatches `profiles.closed_phases` to {p1, p2, p2x}. Full gate is green (776 tests; `rmf ci --profile p6` PASS).
- Rule: every phase in profiles.PHASES needs a ci step before its marker is created. Tests exercising a profile must pin `closed_phases`.
- Promotion: check: test_ci_profile_with_unimplemented_phase_exit_2

## L-0035 · 2026-10-29 · run: uas-gcs/example-synthetic-01 · tags: baseline, overlays
- Symptom: at S-1, `rmf baseline resolve` exited 1: "overlay CNSSI1253F-ATT6-PRIVACY (Privacy Overlay) is not transcribed in framework/baselines/cnssi-1253.yaml". C-2 had selected that overlay and C-3 approved it, so S-1 could not write baseline.json or the baseline_id fact, and two agent sessions stalled.
- Root cause: the framework lists the Privacy Overlay as a valid `categorization.overlays` value (C-2 may pick it, FACTS-001 accepted it) but its control blocks were never transcribed, and nothing before S-1 checked `transcribed`. The overlay also selects one of four control sets, which a single ID cannot express.
- Fix: transcribed Table 2 of CNSSI 1253F Att. 6 as four overlays, CNSSI1253F-ATT6-PRIVACY-{ACCT,LOW,MODERATE,HIGH} (ADR-0003); C-2 step 6 explains the two-question set selection. FACTS-001 now rejects any overlay resolve cannot apply, owned by C-2 and C-3, so the approval reopens at categorization time.
- Rule: an overlay a run can record must be one `rmf baseline resolve` can apply; the check runs at C-3, not at S-1.
- Promotion: check: test_overlay_resolve_cannot_apply_reopens_c3

## L-0036 · 2026-10-29 · run: uas-gcs/example-synthetic-01 · tags: monitor, inputs, scope
- Symptom: at M-2 the entry check failed: the run includes M-1, M-2, M-3 and M-5 (`include_after_stop`), but `examples/uas-gcs/product/` had no monitoring data (EXT-MONITORING, e.g. `product/monitoring/`), so no family due this cycle could be assessed and two sessions stopped after M-1. RUN-CFG-001 and `rmf status` did not report the missing input.
- Root cause: the example product was written for the lifecycle up to R-5 only; M-2's entry check requires monitoring data on disk, and nothing ties `include_after_stop: [M-2]` to the presence of EXT-MONITORING.
- Fix: added `examples/uas-gcs/product/monitoring/cycle-2026-10.md` (configuration checks, STIG and vulnerability scans after the 2026-10 bundle, weekly log reviews, account review, incidents, threat updates), consistent with the seeded weaknesses; the run resumed at M-2.
- Rule: a run that scopes in a task with an EXT-* input must have that input in its product directory, or the task's playbook must name a fallback, before the run reaches the task.
- Promotion: none — EXT-* inputs have no machine-checkable path in framework/artifacts.yaml yet; a RUN-CFG check needs that field first (v1.1 candidate, noted in the Phase 7 handoff)

## L-0037 · 2026-10-29 · run: phase-8 · tags: agent-lane, upstream-hash
- Symptom: the first cold-start-resume result reported RUN-STALE-001 (W) although nothing upstream had changed: "the scenario cold-start-resume hash differs".
- Root cause: the scenario's hash_globs cover its base_run (tests/agent/results/skeleton/run/**). The harness deletes tests/agent/results/ from its work copy after `rmf run init` so the agent cannot read results, so the final `rmf check` hashed a different file set than init did.
- Fix: scripts/agent-run.sh puts the base run back before the final `rmf build` / `rmf check`; the re-run reports 0 errors and 0 warnings ($0.53).
- Rule: any file a scenario's upstream hash covers must be present, unchanged, wherever the run's hash is recomputed.
- Promotion: none — harness (bash) behaviour; the committed cold-start result (0 warnings) is the evidence, and ADR-0004 records the sequence

## L-0038 · 2026-10-29 · run: phase-8 · tags: ci, extras, tests
- Symptom: `rmf ci --release` failed at pytest collection with `ModuleNotFoundError: No module named 'pymupdf'` after a plain `make bootstrap` (no `EXTRACT=1`).
- Root cause: tests/unit/test_refs_extract.py imported PyMuPDF, the optional AGPL [extract] extra, at module level; every earlier gate ran in a venv bootstrapped with `EXTRACT=1`, so a fork with the default bootstrap would fail `rmf ci`.
- Fix: the module uses `pytest.importorskip("pymupdf")`; without the extra its tests are skipped. Added tests/e2e/test_fork_template.py (clone without examples/, `rmf new`, `rmf ci --profile fork`), which bootstraps a fresh default environment.
- Rule: a test that needs an optional extra must skip, not fail, when the extra is absent; gate at least once in a default (no-extras) environment.
- Promotion: check: test_fork_without_examples_passes_fork_profile

## L-0039 · 2026-10-31 · run: phase-8 · tags: monitor, inputs, templates
- Symptom: a fork that reached M-2 stalled with no `product/monitoring/` and no hint where the data goes; `rmf check` did not report it (the stale-template gap behind L-0036, whose fix lived only in the example).
- Root cause: external inputs had no checkable location, and the fork template (`templates/workspace/product/`) had no guidance for them, so a fix made in one place did not reach the other.
- Fix: `framework/external-inputs.yaml` gives an input an optional `path` (set on EXT-MONITORING); RUN-CFG-001 reports an active task whose input path holds nothing but a README.md, owned by that task so it shows when the run reaches it; the template gained `product/monitoring/README.md`.
- Rule: an EXT-* input the fork supplies as files gets a `path` in the framework (only EXT-MONITORING has one so far; the other 12 task-read inputs have none) and guidance in the fork template; a fix to the example product is mirrored in the template.
- Promotion: check: test_task_needing_monitoring_data_reports_its_absence

## L-0040 · 2026-10-31 · run: phase-8 · tags: docs, counts, tests
- Symptom: README.md said "will provide" and "17 NIST documents fetched automatically; the DoD and CNSS PDFs are added by the user" while 32 PDFs were committed; tests hard-coded 63 rules.
- Root cause: counts and status statements were written once in prose and tests, and nothing recomputed them.
- Fix: DOC-002 compares the counts stated in README.md, AGENTS.md and the registry header with values computed from the registry, framework and reference index; the registry tests compute instead of hard-coding.
- Rule: a number in documentation is checked against a computed value; a test does not repeat a count the registry holds.
- Promotion: check: DOC-002

## L-0041 · 2026-10-31 · run: phase-8 · tags: tests, fixtures, audit
- Symptom: the audit counted 15 of 35 negative specs on the example; `grep example` counts 33, because 18 specs carry `example` only in a comment that says they are left out.
- Root cause: coverage was read from comments and prose, not from parsed data, and nothing enforced the "most specs also run on the example" intent.
- Fix: 17 specs gained example-base mutations (per-mutation `only:`), and `test_example_base_coverage_ge_80pct` parses the specs, requires at least 80% on the example and lists each exception with its reason.
- Rule: measure coverage from parsed data; a fixture left out of a base is listed with its reason in a test.
- Promotion: check: test_example_base_coverage_ge_80pct

## L-0042 · 2026-10-31 · run: phase-9 · tags: refs, revision, currency
- Symptom: `index.yaml` labelled DoDI 5000.02 and 5000.85 "(with changes)", SP 800-53 and 800-53B "(with updates)" and DevSecOps "current (record the version at import)"; the pinned PDFs carried Change 2 (2026-04-08), Change 1 (2021-11-04) and updates as of 12-10-2020, and nothing noticed the labels lagging.
- Root cause: `revision` is hand-curated, a placeholder passed every check, and no check compared a label with the text that was already extracted.
- Fix: exact revisions in the index; each pinned PDF gets a `revision_stamp {page, anchor}` pointing at the passage that shows it; REF-007 rejects vague labels and a stamp that does not resolve through `refs show`.
- Rule: a pinned PDF's `revision` states the edition, date and change number its text shows, with a `revision_stamp` to that passage; `currency_checked` is set only on a day the upstream was actually checked.
- Promotion: check: REF-007

## L-0043 · 2026-10-31 · run: phase-9 · tags: refs, oscal, catalog
- Symptom: seven controls in the pinned OSCAL catalog (IA-13 and its three enhancements, SA-15(13), SA-24, SI-2(7)) are absent from the text of SP 800-53, 800-53A and 800-53B, so a citation to them cannot resolve.
- Root cause: the catalog (release 5.2.0) is newer than the PDFs, and the gap was found by one audit pass, not recorded where a later reader or check would see it.
- Fix: `oscal_only_controls` on the three entries (with a `revision_note`); REF-008 warns on a catalog control that is absent from a PDF's text and not declared, and on a declaration that no longer holds. 800-53A writes IDs as CM-02(01), so IDs are normalised before comparing.
- Rule: a difference between a pinned catalog and its PDF is declared in a structured field on the entry, never only in prose.
- Promotion: check: REF-008

## L-0044 · 2026-10-31 · run: phase-9 · tags: refs, required, citations
- Symptom: seven pinned PDFs that the framework cites (DoDI 5000.89, 5000.90, DevSecOps and four CNSSI 1253 overlays) were `required: false`, so a fork that skipped optional documents would fail FW-CITE-002 on a citation to a document that is allowed to be absent.
- Root cause: `required` and the citations were maintained separately, and `required: true` for a document still to be imported breaks `rmf ci` at once (REF-001 is an error from p2x on, and citing a pending reference fails FW-CITE-002).
- Fix: FW-CITE-003 rejects a citation to a PDF that is `required: false`. Entries awaiting an operator import are added `required: false` and pending, are not cited, and flip to `required: true` in `index.yaml` and `refs/required.py` in the commit that imports them.
- Rule: cite only required PDFs; make an entry required in the same commit that obtains it.
- Promotion: check: FW-CITE-003

## L-0045 · 2026-10-31 · run: phase-9 · tags: refs, revision, cnss
- Symptom: CNSSI 1253 was dated 2022-08-01 in the index but its cover says 29 July 2022, and the dates of Attachments 5 and 6 (2022-09-30, 2024-10-31) appeared nowhere in their extracted text. REF-007 treated a stamp as optional, so both passed.
- Root cause: these dates were copied from the cnss.gov listing at import, which publishes on a different day from the document's own date. ATT5 does print 09/30/2022 on every page, but the extractor strips it as page furniture; ATT6 prints no date at all.
- Fix: CNSSI 1253 carries the cover date and a stamp. REF-007 now requires a `revision_stamp` on every pinned PDF, and the stamp must show the revision's latest year. ATT5 and ATT6 declare `revision_source` with the reason no passage shows their date, and their `revision_note` says where the date comes from (the page footer, or the listing).
- Rule: a pinned PDF's `revision_stamp` points at text that states the revision; an entry that cannot have one declares `revision_source` with the reason, and a revision taken from a listing says so in `revision_note`.
- Promotion: check: REF-007

## L-0046 · 2026-10-31 · run: phase-10 · tags: conformance, rules, audit
- Symptom: all 63 rules passed while the audit found about 45 gaps; a citation proved a passage exists, and FW-TASK-001 pinned task names but not inputs, outputs or roles.
- Root cause: the rules checked structure, and nothing recorded which requirement of which document a rule, schema or template actually enforces.
- Fix: `conformance/` holds a register extracted from the text. FW-REQ-003 requires evidence that can fail before an entry is `covered`, and citations and prose cap at `partial`. FW-TASK-002 compares each task with its Chapter 3 block.
- Rule: a claim of coverage names a check that fails when the requirement is broken; a citation alone is never coverage.
- Promotion: check: FW-REQ-003

## L-0047 · 2026-10-31 · run: phase-10 · tags: conformance, extraction, text
- Symptom: `Organizations must:` was extracted 12 times from FIPS 200 with the requirement itself dropped, and a sentence cited to page 8 opened on page 9, so its one-word anchor did not resolve.
- Root cause: the sentence splitter broke at colons, separating a modal lead-in from its inline list, and a paragraph rejoined over a page break reported only its first page.
- Fix: sentences end at `.`, `?` and `!`; a short lead-in is context; an item whose opening words are on the next page cites that page; a rejoined block counts on both pages.
- Rule: extract into blocks once, use the same blocks to check a statement against its passage, and read the output for a document before trusting its count.
- Promotion: check: test_a_modal_sentence_list_stays_whole

## L-0048 · 2026-10-31 · run: phase-10 · tags: conformance, toc, text
- Symptom: `SP800-30R1.toc.yaml` lists 2.4.3 but not 3.1 or 2.4.1, CNSSI 1253's toc holds a footnote as a level 1 heading, and SP 800-37r2's Appendix F, the source of finding N-1, has no numbered headings at all.
- Root cause: the toc comes from an outline and guarded regexes tuned for citation lookup, so it is neither complete nor clean as a list of document units.
- Fix: the first fix read headings from the blocks instead of the toc, which made headings the register's unit for 617 entries and still missed every requirement sentence in Appendix F. Section mode is gone: headings are context only, and every prose page is read sentence by sentence in statement mode (`extract.classify`).
- Rule: use the toc to resolve a citation; do not use it, or any heading list, to enumerate a document's requirements.
- Promotion: check: test_headings_are_context_and_never_statements

## L-0049 · 2026-10-31 · run: phase-10 · tags: conformance, nist, parser
- Symptom: FW-TASK-002 reported seven SDLC disagreements on I-1 to A-5, all false: SP 800-37r2 prints `New – Development/Acquisition; Implementation/Assessment.` and the task notes use a comma.
- Root cause: the parser treated `;` as the end of the `New` value because the notes use it to separate `New` from `Existing`; the two forms differ only in where `Existing` starts.
- Fix: a value runs to the word `Existing` or the end of the field.
- Rule: when a new check fires on data that an earlier audit passed, test the parser against the source line before changing the data.
- Promotion: check: test_the_document_and_the_citation_notes_parse_alike

## L-0050 · 2026-10-31 · run: phase-10 · tags: fork, tests, readme
- Symptom: `rmf ci --profile fork` failed five `test_doc_counts.py` tests on a fork that had rewritten README.md, though AGENTS.md and doc_counts.py both say the README is the fork's to rewrite.
- Root cause: the tests copied the real README.md and edited sentences in it, and the e2e fork test deleted examples/ but kept the README, so nothing exercised a rewritten one.
- Fix: the `tree` fixture writes its own README from computed counts, and `test_fork_without_examples_passes_fork_profile` rewrites README.md.
- Rule: a test that runs in a fork reads no fork-owned file; the e2e fork test changes every file a fork may change.
- Promotion: check: test_fork_without_examples_passes_fork_profile

## L-0051 · 2026-10-31 · run: phase-10 · tags: conformance, extraction, recall
- Symptom: the first extractor passed its tests while recall on nine hand-read pages was 53 of 82 (35% missed), section mode returned headings only, and `Authorization to Use` (31 source mentions) had no entry; the tests asserted counts and sample statements the extractor itself had produced.
- Root cause: nothing measured the extractor against a label it did not write, so a drop in recall changed no test.
- Fix: `tests/fixtures/conformance/recall/` holds 26 hand-read pages with 215 requirements and one probe per audit finding; `test_conformance_recall.py` computes recall per unit and per mode (floor 95% on lettered, table, pin and catalog; prose at its measured level, since L-0053), probes (100%) and noise (ceiling 35%) on every run, and checks that every in-scope line of every source is an entry or a recorded rejection.
- Rule: an extractor's test set is labelled by reading the source before the extractor changes, and a label is never edited to fit the extractor.
- Promotion: check: test_recall_by_unit_and_by_mode_holds_its_floor

## L-0052 · 2026-10-31 · run: phase-10 · tags: conformance, evidence, rules
- Symptom: `{kind: pinned, target: AD-ATO, field: id, value: AD-ATO}` was strong evidence, 1,500 copies of it raised no finding because the fan-out warning counted rule evidence only, `asserts: x` satisfied 56 rules, a triage pattern of `.` retired every entry, and closing a work item needed only `closed_by`.
- Root cause: evidence pointed one way (entry to target) and the target never had to agree, so any well-formed claim counted.
- Fix: a rule lists the entries it `enforces` and FW-REQ-003 refuses evidence the rule does not list and an `enforces` the entry does not cite back; pins are limited to `evidence.PINNED_FIELDS`; `asserts` must share two content words with the statement; the fan-out cap is an error for every evidence kind with exceptions in `conformance/policy.yaml`; triage patterns are document-scoped, need two literal words, a cap, a sample, and never apply to tier 1; a document over a quarter not-applicable, however the statuses were set, needs a user-approved record; a work item binds entries and closes only when their evidence judges strong.
- Rule: a claim is linked in both directions, and the thing claimed about names what it proves; a check that counts claims must count every kind of claim.
- Promotion: check: FW-REQ-003

## L-0053 · 2026-11-01 · run: phase-10 · tags: conformance, extraction, recall, tests
- Symptom: `test_nothing_in_scope_is_dropped_silently` reported 13,141 of 13,141 blocks accounted for while 139 raw lines of nine sources (1,295 words in paragraphs a caption had absorbed, the SP 800-18r1 Executive Summary joined to a contents line on an excluded page) were in no entry and no rejection. Two regexes added to hit two freshly written recall labels (`was|were`, `contingency planning`) matched 23 noise sentences for 3 hits.
- Root cause: the test read the document through `extract.blocks()`, `block.page` and `heading_like`, the same reader whose joins it was meant to check, so a paragraph the reader swallowed was invisible to it; and a label written after the extractor change is a target, not a measurement.
- Fix: the test reads raw page lines from `references/text` with its own stated exclusions and reports 0 lost lines; `blocks()` never continues a caption, an all-caps line or a leader line onto the next page, a caption line is its own paragraph, and a block that starts outside every scope is read by the scope it ends in. The two regexes are gone and their labels count as misses; prose keeps a floor at the level measured (91/94) and is otherwise reported, since extraction is a first pass that `rmf conformance promote` completes.
- Rule: a recall or completeness test reads the source with its own reader, never the extractor's; a label is written before the extractor is tuned, and a miss stays a miss.
- Promotion: check: test_no_raw_line_in_scope_is_dropped_silently

## L-0054 · 2026-11-01 · run: phase-10 · tags: tests, refs, conformance
- Symptom: importing the last 22 pending references failed `test_text_report_shows_every_section`, which looked for `pending-acquisition)` in the report of the real register, and `test_extract_writes_and_leaves_a_pending_document_unassessed`, which raised StopIteration looking for a real pending source.
- Root cause: both tests needed a state the repository is meant to leave, although `_conformance_fixtures` already builds a pending reference.
- Fix: both behaviours are tested on `fx.build` with its PENDING reference; scratch mutations of the report and of `cli_support.extract` each fail one of the tests.
- Rule: a test of a state the repository is meant to leave builds that state in a fixture.
- Promotion: none — a rule for writing upstream tests with no step in a fork; a checker cannot tell a transient repository state from a permanent one

## L-0055 · 2026-11-01 · run: phase-10 · tags: refs, extraction, conformance
- Symptom: CNSSP 12 passed `refs verify`, REF-003 and REF-007 with OCR errors in its text (`C SSP 12`, `ational`); the CSRMC graphic extracted scrambled and nine of ten tenets were rejected. No check raised a finding on any of them.
- Root cause: the checks prove a text is the extraction of the pinned PDF, not that the extraction reads correctly.
- Fix: the pages were read at import, the CSRMC scope has `tables: false`, and `docs/audits/2026-10-31-operator-imports.md` lists each case for triage.
- Rule: at import, read the PDF's rendered pages beside its text; a passing extraction proves provenance, not legibility.
- Promotion: none — legibility of a text layer takes a reader; no offline check can judge it

## L-0056 · 2026-11-01 · run: phase-10 · tags: conformance, extraction, citations
- Symptom: eight entries of DODCIO-RECIPROCITY and CNSSP22 passed `rmf validate` while `rmf refs show` with the real passage at the cited page exited 1: statements opened with a page number (`3 deployed in the Department...`) or held a footer's phone and email, and the anchor was the footer.
- Root cause: the extractor strips only margin-band lines and lines recurring on enough pages, so these footers stayed in the text as paragraphs, and `blocks()` joined the next page to them. FW-REQ-001 compares a statement with passages built by the same joiner, so it could not see this.
- Fix: `footers` in conformance/sources.yaml declares such a footer per document; a match is neither joined nor in the way of a join, and an entry that loses words at its edge keeps its ID and review. Only the three documents with such footers changed.
- Rule: a check of a citation reads the page as a reader would, not through the code that made the citation.
- Promotion: check: test_no_statement_starts_on_a_page_number_or_holds_a_footer

## L-0057 · 2026-11-01 · run: phase-10 · tags: refs, ci, fetch
- Symptom: eight fetch tests passed locally and failed on GitHub with `qpdf: open ...: Permission denied`, on a file the same user had just written, while the importer's tests passed with real qpdf on the same runner.
- Root cause: Ubuntu 26.04 ships an AppArmor profile for qpdf that denies names not ending in `.pdf`, and fetch validated a `.fetch-*.part` temp file. A probe of name and mode on the runner, with the kernel log, showed the suffix alone decides; the dot prefix and the mode do not.
- Fix: a downloaded PDF is validated under a `.pdf` name.
- Rule: when a tool refuses a file its owner can read, suspect mandatory access control, and probe each difference on the failing host before changing more than one.
- Promotion: check: test_qpdf_reads_the_download_under_a_plain_pdf_name

## L-0058 · 2026-11-01 · run: phase-10 · tags: ci, tests
- Symptom: pytest workers cut the local gate from 54 minutes to 15 and raised the GitHub run from 49 minutes to 65.
- Root cause: a private repository's hosted runner has few cores, and workers repeat module fixtures while the fork test runs a nested suite, so they cost more than they save there.
- Fix: `rmf ci` uses workers only from `MIN_WORKER_CPUS` cores up.
- Rule: measure a speedup on every host it will run on, not only the one it was built on.
- Promotion: check: test_ci_runs_pytest_in_series_on_few_cores

## L-0059 · 2026-11-01 · run: phase-10 · tags: conformance, triage
- Symptom: `conformance/sources.yaml` excluded the Privacy overlay's Section 6 as "Section 5" and "work item WI-32", Classified's Section 6 as control text a run already had, and chapter-opening prose in SP 800-53, 53A and 53B as tables. 512 entries entered when the reasons were read against their pages, 330 of them per-control values that feed baselines.
- Root cause: exclusion reasons were written at import from the table of contents, and FW-REQ-001 checks that a reason exists and covers the pages, not that it is true of them.
- Fix: every exclusion read against its pages; false ones rescoped or rewritten, and the new entries triaged (docs/audits/2026-11-triage/).
- Rule: an exclusion reason is a claim about pages: write it after opening the first and last page of the range, and treat a range that opens with prose as in scope until read.
- Promotion: none — whether a reason is true of a page needs a reader; the sampled audit carries it, and a rule could only test that the reason exists.

## L-0060 · 2026-11-01 · run: phase-11 · tags: conformance, evidence
- Symptom: `AD-CATO.requires` was judged strong evidence for the DoD CISO approval while AODM-007 hardcoded the approval and never read the field, so changing the pinned value changed nothing a run saw.
- Root cause: FW-REQ-003 can prove a pinned value equals what the entry says, not that any code consumes it.
- Fix: AODM-007 reads `requires`; a test takes every decision field the register pins, changes it, and requires the rule output or `in_force` to change.
- Rule: A pin counts as evidence only if changing the value changes what a run gets.
- Promotion: check: test_each_pinned_decision_field_changes_what_the_run_gets

## L-0061 · 2026-11-02 · run: phase-11 · tags: conformance, evidence
- Symptom: Fable found a quarter of sampled `covered` entries did not hold, though every one judged strong: one rule fixture vouched for every clause, a required free-text field stood for a duty, and an item read closed with half its entries partial.
- Root cause: the judge asked whether a test could fail somewhere on the target, not whether this clause's test fails when this duty is broken.
- Fix: a rule item names its fixture and failing message, verified statically and proved by `test_negative`; presence caps at partial on prose; pins and optional parents count only beside the rule reading them; `closed-partial` is a status of its own.
- Rule: Evidence names the test that fails for this clause, or it is partial.
- Promotion: check: test_a_rule_item_is_tied_to_its_fixture

## L-0062 · 2026-11-02 · run: phase-11 · tags: oscal, fixtures
- Symptom: the first boundary diagram any fixture listed reached the OSCAL SSP as `product/product/architecture.md`, although the schema says the path is relative to the run directory.
- Root cause: `_diagrams` prefixed `product/`, and no fixture had ever held a diagram, so the golden never showed it.
- Fix: the link is the path as written; valid_minimal lists the boundary diagram, and PKG-003 fails when its file is not in the run.
- Rule: An optional field no fixture sets is untested, however green its golden.
- Promotion: check: PKG-003

## L-0063 · 2026-11-02 · run: phase-11 · tags: conformance, evidence
- Symptom: rule items on SVCA-001 and SSPR-001 judged weak with "provider is a decision's required field", though no decision record was in sight; the clauses were about service agreements and the review date.
- Root cause: FW-REQ-003 finds a `requires` field by name in the declared message and in the clause's string constants, so an ordinary English word that happens to name a required field (`provider`, `review`) reads as that field.
- Fix: the messages say CSSP and "Security Review Date", and the party enum says `service-provider`; the judge stays strict, since loosening it would let a real required field out through a reworded message.
- Rule: When a rule item is weak on a required field it does not touch, reword the message; never relax the judge.
- Promotion: none — a wording trap of the judge, reported by the judge itself with the field named, and it does not reach forks.

## L-0064 · 2026-11-02 · run: phase-11 · tags: fixtures, rules
- Symptom: every rule on M-1 and M-5 was silent on both fixture runs, which stop at R-5, so a clause could pass its negative test only with a fixture that first built a monitoring cycle by hand.
- Root cause: a supporting artifact out of play holds nothing a rule reads, and no fixture seeded one.
- Fix: valid_minimal seeds ART-CHG and ART-SECRPT, so `test_base_has_no_findings` proves the positive case of each Monitor rule and each negative fixture needs one mutation.
- Rule: A rule's positive case runs in a base run, not only its negative one.
- Promotion: none — a fixture habit, already enforced for this cluster by test_base_has_no_findings; it binds no fork.

## L-0065 · 2026-11-06 · run: phase-11 · tags: framework, contracts
- Symptom: listing ART-CONMON as an output of S-6, so S-6 could record the AO's approval of the monitoring strategy, made the example's S-6 undone, and AODM-001 refused its R-4 decision because the tasks before R-4 had not written their outputs.
- Root cause: task status is derived from `touched_by` on every output, so a new output reopens the task in every run already past it, whatever its `framework_version`.
- Fix: the approval lives in conmon.yaml from S-5, which SP 800-37 Task S-5 places it in (the AO approves the strategy, possibly with the plan); ISCM-004 is gated with `since`.
- Rule: Never add an output to an existing task; put the new record in an artifact the task already writes, or in a new task.
- Promotion: none — the example check (p7) already fails on it; the rule saves the round trip.

## L-0066 · 2026-11-06 · run: phase-11 · tags: tailoring, baseline
- Symptom: tailoring.yaml accepted compensating actions, but `rmf baseline resolve` ignored them, so a compensating control had no baseline entry and no required SSP statement, and nothing checked its source, reason or risk acceptance.
- Root cause: the schema admitted an action kind that no reader consumed; validating the shape passed for a record that changed nothing.
- Fix: from contract 0.2.0 a catalog compensating control joins baseline.json (origin `compensating`), and TLR-001 checks the action's target, source, reason and AO risk acceptance.
- Rule: Every action kind a run-data schema admits is read by the resolver or a rule; one that only passes the schema is a gap.
- Promotion: check: TLR-001 and test_catalog_compensating_control_reaches_the_baseline_from_its_contract

## L-0067 · 2026-11-07 · run: phase-11 · tags: rules, dates
- Symptom: a first cut of the POA&M rules compared dates with `run.yaml:as_of` and refused every fixture: as_of is when the run starts, and a simulated run schedules its assessment after it.
- Root cause: as_of reads like today, but a simulated run has no today.
- Fix: a rule that needs the present uses the latest date the run vouches for, its newest authorization record, and a rule that bounds an event compares it with the plan's own schedule.
- Rule: Compare a run's dates with each other, never with as_of as if it were now.
- Promotion: none — it shapes how a rule is written, and test_valid_minimal fails at once on the mistake.

## L-0068 · 2026-11-07 · run: phase-11 · tags: run-data, rules
- Symptom: a run could delete the new `artifacts/data/ra.yaml` and pass every check, and its PKG-003 data elements for the RAR were the only sign.
- Root cause: RUN-ART-001 checks the files of core artifacts only; ART-RA is `package: supporting`, so a data file added to it is required by nothing.
- Fix: SRA-001 reports a missing ra.yaml whenever ART-RA is produced or seeded on a contract that has the file, with a negative fixture.
- Rule: A data file added to a supporting artifact needs a rule that reports it missing; RUN-ART-001 does not.
- Promotion: check: SRA-001

## L-0069 · 2026-11-07 · run: phase-11 · tags: conformance, references
- Symptom: DoDI 8530.01 Encl. 4 §d.(5) cites Reference (ch), which the issuance's reference list gives as DoD 5220.22-R, the Industrial Security Regulation; triage read it as the DISN Connection Process Guide, which the list gives as (cg).
- Root cause: the body on pp. 37-38 runs one letter ahead of the list: it cites 5220.22-R as (ci), FAR Subpart 4.4 as (cj), DoDI 8582.01 as (ck) and DFARS 252.204-7012 as (cl), so a body letter there cannot be looked up in the list as printed.
- Fix: CONN-001 holds mission partner interconnections to the DISN connection process; REQ-DODI8530.01-0300 stays partial, with the drift stated, until the user rules on the reading.
- Rule: Before building on "in accordance with Reference (x)", read (x) in the issuance's own reference list and check the neighbouring body citations agree with it.
- Promotion: none — whether body and list letters agree is a reading of one document's drift; no rule can tell a misprint from a citation.

## L-0070 · 2026-11-07 · run: phase-11 · tags: facts, contract
- Symptom: the six system facts C-1 now records (classification, IT type, owning organization, version, operational environment, life-cycle phase) could not go into `writes_facts` without FACTS-001 and `rmf status` refusing the example run, which is at contract 0.1.0; making `roles` required in users.schema.json likewise broke a valid older users record.
- Root cause: `writes_facts` and a schema's `required` hold every run whatever its contract; only rules carried `since`.
- Fix: a task's `facts_since` dates a fact it writes, and `Run.writes_facts` drops a fact the run's contract predates, for FACTS-001 and status alike; new run-data fields stay optional in the schema and a rule with `since` requires them.
- Rule: A new required run field is gated by the run's contract (`since`, `facts_since`), never by `required` in a schema an older run is validated against.
- Promotion: check: FACTS-001 on the example run at contract 0.1.0 (p7), which fails when a new fact lacks facts_since

## L-0071 · 2026-11-07 · run: phase-11 · tags: conformance, rules
- Symptom: rule items on org-context.yaml judged weak with "review is a decision's required field" and "provider is a decision's required field", though no decision record was in play: a fixture's process was named "Account review", an assessment element "External service provider monitoring", and the rules read keys named `review` and `provider`.
- Root cause: FW-REQ-003 finds a decision's `requires` field in a fixture's mutated paths, its declared message and the fields the rule reads; a run-data key or a fixture value spelled like one of those fields is read as that field.
- Fix: the keys became `review_cycle` and `provided_by`, the fixture values lost the words, and one message was reworded so it names no such field.
- Rule: Name run-data keys and fixture values apart from the decision `requires` fields (risk_executive, underlying, review, provider, threat_assessment, deployment, ongoing_acknowledgment, revocation_reason, the CISO approval fields) unless the rule does judge that field.
- Promotion: none — FW-REQ-003 already reports it on the first validate, naming the field; the rule saves the round trip.

## L-0072 · 2026-11-07 · run: phase-11 · tags: rules, should
- Symptom: a first cut of PPROT-002 and PPROT-004 refused every contract award with no PPP update and every RFP without PPP countermeasures, though DoDI 5000.83 5.3.c.(2)(b) says lead systems engineers *should* do both; the register showed the items as plain lettered entries.
- Root cause: the extractor cuts a lead-in from its items, so an item under a should lead-in reads like a will, and the modal sits in the lead-in's context, not in the item.
- Fix: those clauses accept a recorded reason for not updating or a deviation on the RFP, and tests/unit/test_protection.py holds each permitted case.
- Rule: Before writing a clause from a lettered item, read its lead-in; a clause from a should accepts a recorded reason, a clause from a will or must does not.
- Promotion: none — the permitted-case tests hold it for these rules, and a register-wide check would need the lead-in's modal on each item, which the extractor does not record.

## L-0073 · 2026-11-07 · run: phase-11 · tags: run-data, schema, trace
- Symptom: valid_minimal failed TRACE-002 with "malformed trace token 'cve'" once conmon.yaml held `vulnerability_management.identification.sources: [cve, vendor-bulletins]` and `patching.sources`.
- Root cause: TRACE-002 reads every key named `sources` anywhere in run data as a list of trace tokens, so a schema that names a list of origin kinds `sources` makes every run that fills it fail.
- Fix: the lists became `identified_from` and `patch_sources`; a schema test asserts every `sources` property in framework/schema holds `#/$defs/source` items.
- Rule: In a run-data schema, `sources` means trace tokens and nothing else; name any other list of origins for what it holds.
- Promotion: check: tests/unit/test_framework_schema.py::test_sources_properties_hold_trace_tokens

## L-0074 · 2026-11-07 · run: phase-11 · tags: conformance, rules
- Symptom: FW-REQ-003 denied every SWA-001 rule item: "'the SBOM leaves out third-party components' is not literal in a failing message in the rule's source", though the rule reported exactly that message and the negative fixture declared it.
- Root cause: the messages lived in a dict of duty to message and the rule appended `err(message)` in a loop; the judge finds a clause by the string constant inside the failing call, and a variable holds none.
- Fix: each SBOM and AI tool clause of SWA-001 writes its message inline in its own `if` and call.
- Rule: Write each failing message of a rule inline in the call that reports it, so the clause that leads to it can be found and judged.
- Promotion: none — FW-REQ-003 already refuses such an item as denied, so the mistake cannot reach the register.

## L-0075 · 2026-11-07 · run: phase-11 · tags: fixtures, privacy
- Symptom: the privacy rules apply only to a system processing PII, valid_minimal processes none, and the two older privacy fixtures had set `privacy: true` on minimal, so every new privacy rule fired in them too and each fixture had to restate the whole privacy record to fail on one clause.
- Root cause: a fixture base fixes the system's conditions; a rule gated on a condition no base meets has no clean base to mutate, and copying a run to make one would drift from the run it copies.
- Fix: tests/unit/test_check_rules.py derives a base `pii` from valid_minimal by the mutations in tests/fixtures/runs/pii.yaml; test_base_has_no_findings holds it clean, and the PRIV fixtures, AODM-010.privacy and RAR-002.privacy mutate it.
- Rule: For a rule gated on a system condition the committed bases lack, derive a base by mutations of a committed one rather than copying a run or piling the condition into each fixture.
- Promotion: none — a test-suite habit that binds no fork; test_base_has_no_findings[pii] fails when the derived base drifts.

## L-0076 · 2026-11-07 · run: phase-11 · tags: references, extraction
- Symptom: the first transcription of the Privacy Overlays' Section 6 gave AC-16 no guidance and AC-16(3) one, against Table 2's marks, and ran the rest of AC-16's guidance into its justification.
- Root cause: the PDF prints AC-16's Guidance as a two-column box; the text extraction made it a table and placed it after the next heading, so reading Section 6 in line order files it under the wrong control.
- Fix: rmf_tool.overlay_specs checks every specification against its summary-table marks (G, V, R, E per control set), and a named repair puts the box back under AC-16, failing when the text no longer matches it.
- Rule: A per-control transcription is checked against the document's own summary of it, and a repair of the extraction is named and fails when the text changes.
- Promotion: check: test_specs_match_the_summary_tables and the generator's mark cross-check, which fail on a misfiled subheading

## L-0077 · 2026-11-07 · run: phase-11 · tags: conformance, extraction
- Symptom: joining a list item cut by a blank line inside a page (I-7) across the whole register changed 175 statements, retired 110 entries and flagged 127 for review in 22 documents, most of them NIST bullets wrongly joined to the paragraph after them.
- Root cause: a layout quirk of one PDF (DODCIO-RECIPROCITY breaks a step after its first line; CNSSP12's OCR layer does the same and repeats a running header) looks like ordinary prose structure in every other document, so a global rule cannot tell them apart.
- Fix: the reader takes per-document options from conformance/sources.yaml, each with a reason: `cut_items`, `run_in_headings` and `headers`; only the documents that declare them change, and register diffs are measured before marking.
- Rule: Fix a layout defect of one document with a declared reading option for that document, and measure the register diff of any extractor change before accepting it.
- Promotion: check: conformance/schema/sources.schema.json requires a reason on each option, and tests/unit/test_conformance_extract.py::test_a_cut_item_joins_only_where_the_source_declares_it fails if the join turns global.
