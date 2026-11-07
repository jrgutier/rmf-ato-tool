# AGENTS.md

Instructions for any AI agent (Claude Code, Codex, others) and for humans working in
this repository or a fork of it. Checked by `rmf ci` (DOC-001): the eight H2 sections
below are fixed, in this order, and the file stays at or under 250 lines.

## Purpose

This repository is a forkable template for the DoD Risk Management Framework (RMF)
on NIST SP 800-37r2, anchored to the DoD acquisition lifecycle. It holds:

- a pinned library of public reference documents with deterministic text extractions;
- the RMF roadmap as validated YAML (the single source of truth), rendered into a
  generated Markdown manual;
- agent-agnostic playbooks, persona cards and the deterministic `rmf` CLI, so an
  agent in a fork can interview simulated (`synthetic`) or partly real (`hybrid`)
  stakeholders and produce a consistent, OSCAL 1.2.1-validated **draft** ATO package;
- a memory system: this file, `docs/LESSONS.md`, and a journal per run.

Python does deterministic work only. Judgment and prose belong in playbooks and
persona cards. Outputs are drafts; they never replace a real SCA or AO.

## Repo layout

Upstream (this template) owns everything except `product/` and `runs/`, which the
fork owns. A fork may delete `examples/`.

| Path | Owner | Contents |
|---|---|---|
| `src/rmf_tool/` | upstream | the `rmf` CLI (Python, `uv`) |
| `tests/` | upstream | unit, integration, e2e (`slow`), agent lane (`agent`, local only) |
| `framework/` | upstream | RMF YAML: phases, milestones, reviews, steps, 47 tasks, 22 personas, artifacts; `schema/` holds the framework and run-data JSON schemas |
| `playbooks/` | upstream | one playbook per RMF task, plus `00-run-protocol.md` and `_shared/` |
| `personas/` | upstream | persona cards, one per DoD RMF role |
| `templates/` | upstream | artifact, interview, journal and workspace templates |
| `references/` | upstream | `pdf/` (Git LFS), `text/`, `oscal/`, `index.yaml`, generated `INDEX.md` |
| `conformance/` | upstream | requirements register: `sources.yaml`, `requirements/<REF>.yaml` (generated: entries plus the rejected in-scope paragraphs with reasons; reviewed fields set by `rmf conformance mark`), `text-hashes.yaml`, `policy.yaml`, `triage.yaml`, `bindings.yaml`, NIST task pin, vocabulary, waivers, work items, `schema/`. Outside the upstream hash, so a status change never stales a run |
| `MANUAL.md`, `docs/manual/` | generated | rendered from `framework/`; never hand-edited |
| `docs/LESSONS.md` | upstream | append-only lessons log |
| `docs/CHECKS.md` | generated | the rule catalog rendered from `registry.yaml` (`rmf checks-doc`) |
| `docs/adr/` | upstream | architecture decision records |
| `docs/audits/` | upstream | dated audits of the repository against its sources, with finding IDs |
| `.phases/` | upstream | `<phase>.closed` markers; their set selects the default CI profile |
| `scripts/` | upstream | `bootstrap.sh`, `agent-run.sh` (agent-lane harness, local only) |
| `docs/spikes/` | upstream | time-boxed investigations and their decisions |
| `examples/` | upstream | `uas-gcs`: a fictional example fork with a synthetic run (`rmf ci` checks it) |
| `product/` | fork | product material the agent ingests; `profile.yaml` holds proposed values only |
| `runs/<run-id>/` | fork | one simulated or hybrid run: facts, interviews, artifacts, OSCAL, journal |

## Invariants

- INV-1: YAML is the source of truth. `framework/*.yaml` holds process facts; prose
  docs, the manual, OSCAL and reports are derived from YAML.
- INV-2: Never hand-edit generated files (manual, OSCAL JSON, `baseline.json`, reports,
  package manifest, CLI-owned marker blocks). Change the source and regenerate.
- INV-3: IDs are stable. Never renumber or reuse a task, artifact, persona, decision,
  rule, lesson (`L-NNNN`), invariant or learned-rule ID.
- INV-4: `runs/<id>/facts.yaml` is the only home of system facts (identity, boundary,
  categorization, baseline ID). Front-matter and prose never restate them.
- INV-5: Every claim in a run carries a trace token to a transcript answer, a product
  file or a tagged `ASSUMPTION`; simulated answers are tagged `SIMULATED`.
- INV-6: Run `rmf build` and then `rmf check` before moving on. Never proceed with errors.
- INV-7: Use only public references from the allowed domains (`refs/domains.py`; ADR-0006),
  with TLS verification on (no `verify=False`, no User-Agent spoofing). Put CUI in a fork only if the host, the
  machines and the LLM endpoint are all authorized for it.
- INV-8: Write run-data files whole; never append to or patch them partially.

## CLI commands

Run every command as `uv run rmf ...`. Exit codes: 0 OK, 1 violations, 2 usage or I/O
error. Commands that report support `--format json`.

| Command | What it does |
|---|---|
| `rmf --version` | print the tool version |
| `rmf doctor` | check required tools (python, uv, git, git-lfs, jq, qpdf, LFS hooks); report optional extract/OCR tools |
| `rmf ci [--profile P] [--slow] [--release] [--no-tests]` | fast lane (ruff, pytest with coverage >= 85%) plus every check of the profile's phases; `--no-tests` leaves out pytest; only `--release` repeats the suite in a fork clone (marker `release`) |
| `rmf lessons check` | LES-002 (LESSONS.md format, IDs, dates, append-only vs `resolve_base()`), LES-003 (no `pending`) |
| `rmf refs fetch [--id ID] [--accept-new --note TEXT]` | download `acquisition: auto` references (ranged-GET probe, allowed domains on every redirect hop, `%PDF-` + `qpdf --check`), pin SHA-256; a changed upstream is reported and kept unless `--accept-new` |
| `rmf refs import ID PATH [--url URL]` | pin a browser-assisted PDF from `references/_inbox/` (see `playbooks/_ops/fetch-blocked-refs.md`) |
| `rmf refs verify [--required] [--id ID]` | offline: REF-001 status (`--required`: pending is an error), REF-002 SHA-256, REF-005 OSCAL pins, REF-006 domains |
| `rmf refs extract [--id ID] [--extractor E] [--ocr] [--check] [--full]` | PDF to `references/text/<ID>.md` + `.toc.yaml`, recorded in index.yaml; `--check` is REF-003 (needs `EXTRACT=1` only to extract) |
| `rmf refs index [--check]` | render `references/INDEX.md` from index.yaml; `--check` is REF-004 |
| `rmf refs sync` | fetch missing, extract stale, render INDEX.md, verify |
| `rmf refs show ID --section S` / `--page N --anchor A` | print a cited passage from the text extraction |
| `rmf validate [--profile P] [--stats] [--format json] [--root DIR]` | framework rules FW-* active in the profile (schema, IDs, references, producers and order, I/O, RACI, DAG, citations, 47-task set); `--stats` adds counts |
| `rmf new SLUG [--dir D] [--mode M] [--run-id ID] [--force]` | scaffold a workspace: `product/` from `templates/workspace/product/`, `runs/`, and a first run |
| `rmf run init [--mode synthetic\|hybrid] [--run-id ID] [--scenario FILE]` | start `runs/<run-id>/` in the cwd; stamps run.yaml (`upstream_hash` and its `upstream_hash_basis`, versions); a scenario adds product, scope, seeds and control subset |
| `rmf run migrate [RUN]` | move a run to the current framework contract: `decision.yaml` becomes the `authorizations.yaml` ledger plus ART-AUTHREC, `framework_version` is bumped; safe to repeat; what the old contract never recorded (the R-2 determination, the risk executive, the deployment scope, ART-DIAS, the R-5 report, the ledger's `system_status`) is reported by `rmf check`, not invented |
| `rmf status [RUN] [--family-gaps]` | task completion derived from disk (outputs touched, facts, interviews, rules) and the next action; writes `reports/status.md` and `reports/metrics.json` |
| `rmf baseline resolve [RUN] [--method M]` | `baseline.json` from facts.yaml (approved categorization: CNSSI 1253 per-objective C/I/A selection plus the privacy baseline, then overlays), `tailoring.yaml` and `control_subset` |
| `rmf catalog show [--family F] [--control C] [--run RUN [--missing]] [--fields F,..] [--chunk i/n]` | compact SP 800-53r5 control text, per family or the run's baseline |
| `rmf assemble [RUN] [--check]` | fill the `rmf:facts` marker blocks in artifact Markdown from facts.yaml |
| `rmf oscal build [RUN] [--check]` | `oscal/` profile, SSP, assessment plan, assessment results and POA&M (trestle models, uuid5, OSCAL 1.2.1); each is built once its inputs exist |
| `rmf oscal validate [RUN\|DIR]` | OSCAL-001 (NIST v1.2.1 schema) and OSCAL-002 (trestle load) on the run's `oscal/*.json`, or on a directory of OSCAL JSON |
| `rmf build [RUN]` | assemble + oscal build + `reports/assumptions.md` (+ refresh `package/manifest.yaml`); always before `rmf check` |
| `rmf package [RUN]` | `package/manifest.yaml` (ART-PKG): the DoDI 8510.01 authorization package, every artifact (class, status, files with SHA-256, OSCAL), OSCAL documents, reports, degraded references |
| `rmf check [RUN] [--task T] [--family F] [--rules R,..] [--final]` | run rules; `--task T` only what applies at T, `--final` everything (scope-aware); writes `reports/check.{json,md}`; DEGRADED-001 is never filtered out |
| `rmf report assumptions [RUN]` | write `reports/assumptions.md` (every assumption and tagged answer, HYB-002); also part of `rmf build` |
| `rmf checks-doc [--check]` | render `docs/CHECKS.md` from the rule registry; `--check` fails when it is stale |
| `rmf playbooks sync [--check]` | regenerate playbook headers and generated bodies from framework/, create missing playbooks; `--check` is FW-PB-001/002 |
| `rmf render [--check]` | render `MANUAL.md` and `docs/manual/PH-*.md` from framework/ (byte-identical on rerun); `--check` is FW-MAN-001 |
| `rmf conformance extract [--id ID] [--check]` | regenerate `conformance/requirements/*.yaml` and `nist-tasks.yaml` from `references/text/` (offline); reviewed fields survive, a statement gone from its source stays as `removed: true` and its ID is retired, an entry whose statement or pairing changed gets `needs_review`, and `covered` is never assigned; `--check` is FW-REQ-005 |
| `rmf conformance accept-text [--id ID]` | record the SHA-256 of each imported reference text in `conformance/text-hashes.yaml` after reviewing a change; FW-REQ-005 fails while a text differs from its recorded hash |
| `rmf conformance mark REQ-ID [--status S] [--reason R] [--work-item WI] [--evidence JSON] [--ruling-sought JSON] [--approved-by user] [--removal-reason R] [--reviewed] [--clear FIELD]` | set reviewed fields on one register entry. `--ruling-sought` takes `[{sentence, reason}]`: a whole marked sentence that is a permission or an open list of examples, never a duty that is merely hard to test; it leaves `unresolved`, the entry stays `partial` and its work item open until the user records `approved_by: user`, an agent never does. Evidence items carry `sentence`, one marked sentence of the statement, whole; an entry of any kind with several marked sentences is `covered` only when a distinct strong item cites each. `partial` needs at least one evidence item. `rmf validate` then judges the evidence (FW-REQ-003) and the reasons (FW-REQ-004) |
| `rmf conformance bind [--check]` | set `work_item` on the one live entry each binding in `conformance/bindings.yaml` names; a phrase matching no entry or several is a finding (FW-REQ-004), never a guess |
| `rmf conformance sample --seed N [-n 30] [--kind prose\|lettered\|table\|promoted\|all] [--rejected] [--status S] [--id REF]` | a seeded sample of entries (noise) or of the rejected in-scope paragraphs and rows (false rejects) to read against the source; `--status not-a-requirement` draws noise marks with their reasons, the audit FW-REQ-004 cannot do; the same seed on the same register gives the same sample |
| `rmf conformance page REF N` | every entry and every rejection on one page of a document, to read against `rmf refs show REF --page N --anchor A` before promoting or marking |
| `rmf conformance promote REF --page N --anchor WORDS --reason TEXT [--sentence]` | extraction is a first pass: turn the rejection on page N holding the words, else the paragraph of the text that does, into a live candidate with the next ID, kind `promoted` and `promoted: {reason}`; `--sentence` takes only the sentence holding the words and exits 2 when they are in no sentence or several; it survives `rmf conformance extract`, is flagged `needs_review` when its passage no longer resolves, is counted by `report`, and FW-REQ-001 checks its citation |
| `rmf conformance report [--format json]` | status distribution per document and in total (`summary.candidate`, `summary.work_items`, `summary.partial_share`, `summary.kinds`, `summary.promoted`, `summary.freeze` with its `deferred` and `partial_without_evidence` counts, `summary.rejected_by_reason`), each document's `retired_share` of real requirements (not-applicable, deferred or partial on evidence that cannot fail over 25% needs a `retirements` record with `approved_by: user` in `conformance/policy.yaml`, FW-REQ-004; noise marked `not-a-requirement` does not count) and its `noise_share` of live entries (over 50% needs a `noise` record there), open work items, unassessed documents, `summary.conditional` (covered under a `holds_when`), `summary.tier1_debt` and `unresolved` (each partial entry's sentences with no strong item, computed), `summary.awaiting_ruling` and `awaiting_ruling` (sentences pending the user's ruling, outside the debt), `summary.closed_items`, `summary.closed_partial_items` |

RUN defaults to the cwd when it holds run.yaml, else the newest `runs/*/`.

Profiles (`--profile`): `p1 p2 p2x p3a p35 p3b p4 p5 p6 p7 p8 p9 p10 p11 release fork`. A phase
profile evaluates the closed phases (`.phases/*.closed`) plus that phase; no profile
evaluates the closed phases only. `rmf ci` exits 2 if the profile includes a phase whose
checks are not implemented yet. Phase checks: p1 LES-002, LES-003, DOC-001; p2
`refs verify` (REF-001 warns for `pending-acquisition`), `refs extract --check`,
`refs index --check`, REF-002..006; p2x makes REF-001 an error for every required
reference and FW-CITE-002 strict; p3a `rmf validate` (FW-SCHEMA-001, FW-ID-001/002,
FW-REF-001, FW-ART-001, FW-ORD-001, FW-IO-001, FW-RACI-001, FW-DAG-001, FW-CITE-001/002,
FW-TASK-001); p35 `rmf check --final` on `tests/fixtures/runs/valid_minimal` (RUN-CFG-001,
RUN-FM-001, RUN-ART-001, FACTS-001, GEN-STALE-001, SSP-COV-001, SAR-POAM-001, TRACE-001/002,
HYB-001/002, OSCAL-001/002, JOURNAL-001), `rmf playbooks sync --check`, AGENT-001 (W);
p4 `rmf render --check` (FW-MAN-001); p5 adds FW-PB-001/002 and FW-PER-001/002 to
`rmf validate`; p6 `rmf check --final` with every run rule on `valid_minimal` (scope all)
and `hybrid_minimal` (hybrid, skeleton scope), `rmf checks-doc --check`, golden OSCAL;
p7 `rmf check --final` with every run rule on `examples/uas-gcs/runs/example-synthetic-01`
(skipped under `--profile fork`); p8 DOC-002, the counts stated in README.md, AGENTS.md
and the registry header equal the registry, framework and reference index; p9 REF-007
(exact `revision`, resolving `revision_stamp`, every change, updates-as-of and errata date the text shows), REF-008 (OSCAL-only controls declared) and
FW-CITE-003 (no citation to a `required: false` PDF, run by `rmf validate`); p10 FW-REQ-001
(register shape, every page scoped or excluded with a reason, citations, statements in their
passages), FW-REQ-003 (evidence linked both ways through `enforces` and `x-enforces`, `asserts`
in the words of the statement and of the failing message or property title, `covered` means a
real test fails: a rule item names its negative fixture, which lists the rule in `errors`, and a
literal `expect` of two content words or a whole declared message, one fixture per clause;
`claim: presence` caps at partial on prose, and the judge classifies rule and schema items
itself; a pin or optional schema parent counts only beside the rule item reading it (`read_by`),
on the same sentence; a decision's `requires` field, read from the fixture and the clause, needs
pin, rule and schema, each strong on one sentence; `covered` cites every marked sentence, whole,
with a distinct item; fan-out capped for
every evidence kind, exceptions approved by the user; ADR-0005, 2026-11-02), FW-REQ-004 (reasons, tier 1 approvals, removal reasons,
triage patterns bounded per pattern, a user-approved record behind any document over a quarter
retired or over half noise, a noise reason that answers the extractor's duty words, `partial` with evidence, work items that bind entries or waivers: `closed` means every entry covered,
`closed-partial` leaves honest partials none of them tier 1, and a tier 1 partial stays open), FW-REQ-005 (source text hashes
reviewed, a fresh extraction equals the register, scopes yield) and FW-TASK-002 (tasks hold the
entities their Chapter 3 block maps to, or a waiver names an open work item or a task-scoped
rationale), all run by `rmf validate`. Recall of the extractor against hand-read pages, the
audit probes, and every raw line of every in-scope page landing in an entry or a rejection is
`tests/unit/test_conformance_recall.py`; prose recall is reported, not guaranteed, and triage
promotes what the extractor missed. p11 run contracts: the fixtures on the current
`framework_version`, and at `--release` the example too (RUN-VER-001 as an error).
Rules, phases and fixtures are listed in `src/rmf_tool/check/registry.yaml` and rendered
into `docs/CHECKS.md`.

## Fork workflow

1. Create a repository from this template and clone it (README.md has the LFS note).
2. `make bootstrap` (add `EXTRACT=1` for the AGPL PDF extractor, `OCR=1` for OCR tools).
3. `uv run rmf new <slug> --dir .` scaffolds `product/` and `runs/` and starts the first
   run (`--mode synthetic|hybrid`). Use `rmf run init` only for a further run.
4. Fill in `product/` with your system's material (mind the CUI rule, INV-7).
5. Follow `playbooks/00-run-protocol.md` until the run reports done.
6. `uv run rmf ci --profile fork`.
7. Send lessons that touch upstream files back upstream as a pull request.

## Run protocol pointer

The master loop for a run lives in `playbooks/00-run-protocol.md`: ask `rmf status`
for the next task, load its playbook and persona cards, read only the listed inputs,
interview, write whole files, then `rmf build` and `rmf check --task T` until 0 errors,
and append a journal CHECKPOINT. S-4 writes each plan as Markdown beside a judged record
(`artifacts/data/cm-plan.yaml`, `contingency.yaml`, `incident-response.yaml`,
`service-agreements.yaml`, `ssp-records.yaml`). Session units are one RMF step (at most 3 control
families). State is always derived from disk, so a fresh session can resume. C-1 writes
`artifacts/data/system-description.yaml`, P-2 `org-context.yaml`, A-3 `sar-summary.yaml`;
a run entering past P-1 records `entry` in run.yaml first (ENTRY-001).

## Learned rules

Rules promoted from `docs/LESSONS.md` that every fork must follow. Each line reads
`- LR-nn: <rule> (from L-NNNN)`. A lesson is triaged in the same change that adds it:
a checkable rule becomes a checker rule plus a fixture (preferred), a rule for all forks
becomes an `LR-nn` or an invariant here, anything else gets `Promotion: none — <reason>`.
Two lessons with the same tag and rule force a promotion.

None yet.

Of the seed lessons, L-0003 is promoted to INV-7 and L-0007 is `none`
(planning-tooling behaviour outside this repo); the others are promoted to checks.

## Bumping OSCAL / references

- Generated OSCAL is pinned to `1.2.1`, the version `compliance-trestle==5.2.0` accepts.
  Bump `OSCAL_VERSION`, the NIST schemas and trestle together, never one alone.
- Input catalogs and profiles (NIST oscal-content) may be any `1.2.x`; they are read as
  raw JSON, never through trestle models (L-0004).
- OSCAL schema validation uses the `regex`-backed validator plus `FormatChecker` (L-0005).
- Pins live in `rmf_tool.oscal.version` and `references/oscal/VERSIONS.yaml`; REF-005
  fails when they, trestle, the index URLs or the fetched files disagree.
- Reference PDFs: add or update the entry in `references/index.yaml`, run
  `rmf refs fetch` (or the browser-assisted import for blocked sites, L-0002/L-0003),
  `rmf refs extract`, `rmf refs index`, and commit the PDF (LFS), text and index together.
  Set `revision` to what the PDF shows and add a `revision_stamp` (or a `revision_source`
  reason when no passage can show it; REF-007), and flip `required` (with `refs/required.py`)
  in the commit that obtains the document before anything cites it (FW-CITE-003). Give an
  imported document `scopes` and `excluded` pages in `conformance/sources.yaml` covering every
  page with a reason, then run `rmf conformance extract` and `rmf conformance accept-text`
  (FW-REQ-001, FW-REQ-005). A fork that drops a reference removes its index entry, its
  `sources.yaml` entry, its `requirements/<REF>.yaml` and its text hash in one commit;
  FW-REQ-001 names whichever is left behind, and a work item or rule that rested on its
  entries then fails FW-REQ-003/004 rather than passing silently.
  Probe URLs with a ranged GET, never HEAD (L-0001).
