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
fork owns. Paths marked † are created by later build phases and may not exist yet.

| Path | Owner | Contents |
|---|---|---|
| `src/rmf_tool/` | upstream | the `rmf` CLI (Python, `uv`) |
| `tests/` | upstream | unit, integration, e2e (`slow`), agent lane (`agent`, local only) |
| `framework/` † | upstream | RMF YAML: phases, milestones, reviews, steps, 47 tasks, personas, artifacts |
| `playbooks/` † | upstream | one playbook per RMF task, plus `00-run-protocol.md` and `_shared/` |
| `personas/` † | upstream | persona cards, one per DoD RMF role |
| `templates/` † | upstream | artifact, interview, journal and workspace templates |
| `references/` † | upstream | `pdf/` (Git LFS), `text/`, `oscal/`, `index.yaml`, generated `INDEX.md` |
| `MANUAL.md`, `docs/manual/` † | generated | rendered from `framework/`; never hand-edited |
| `docs/LESSONS.md` | upstream | append-only lessons log |
| `.phases/` | upstream | `<phase>.closed` markers; their set selects the default CI profile |
| `scripts/` | upstream | `bootstrap.sh` (and the agent-lane harness †) |
| `product/` † | fork | product material the agent ingests; `profile.yaml` holds proposed values only |
| `runs/<run-id>/` † | fork | one simulated or hybrid run: facts, interviews, artifacts, OSCAL, journal |

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
- INV-7: Use only public references from the allowed domains, with TLS verification on
  (no `verify=False`, no User-Agent spoofing). Put CUI in a fork only if the host, the
  machines and the LLM endpoint are all authorized for it.
- INV-8: Write run-data files whole; never append to or patch them partially.

## CLI commands

Run every command as `uv run rmf ...`. Exit codes: 0 OK, 1 violations, 2 usage or I/O
error. Commands that report support `--format json`.

| Command | What it does |
|---|---|
| `rmf --version` | print the tool version |
| `rmf doctor` | check required tools (python, uv, git, git-lfs, jq, qpdf, LFS hooks); report optional extract/OCR tools |
| `rmf ci [--profile P] [--slow] [--release]` | fast lane (ruff, pytest with coverage >= 85%) plus every check of the profile's phases |
| `rmf lessons check` | LES-002 (LESSONS.md format, IDs, dates, append-only vs `resolve_base()`), LES-003 (no `pending`) |

Profiles (`--profile`): `p1 p2 p2x p3a p35 p3b p4 p5 p6 p7 release fork`. A phase
profile evaluates the closed phases (`.phases/*.closed`) plus that phase; no profile
evaluates the closed phases only. `rmf ci` exits 2 if the profile includes a phase whose
checks are not implemented yet. Phase p1 checks: LES-002, LES-003, DOC-001.

## Fork workflow

Steps marked † use commands that later build phases add; see `## CLI commands` for what
exists today.

1. Create a repository from this template and clone it (README.md has the LFS note).
2. `make bootstrap` (add `EXTRACT=1` for the AGPL PDF extractor, `OCR=1` for OCR tools).
3. † `uv run rmf new <slug> --dir .` scaffolds `product/` and `runs/`.
4. Fill in `product/` with your system's material (mind the CUI rule, INV-7).
5. † `uv run rmf run init --mode synthetic|hybrid`.
6. † Follow `playbooks/00-run-protocol.md` until the run reports done.
7. † `uv run rmf ci --profile fork`.
8. Send lessons that touch upstream files back upstream as a pull request.

## Run protocol pointer

† The master loop for a run lives in `playbooks/00-run-protocol.md`: ask `rmf status`
for the next task, load its playbook and persona cards, read only the listed inputs,
interview, write whole files, then `rmf build` and `rmf check --task T` until 0 errors,
and append a journal CHECKPOINT. Session units are one RMF step (at most 3 control
families). State is always derived from disk, so a fresh session can resume.

## Learned rules

Rules promoted from `docs/LESSONS.md` that every fork must follow. Each line reads
`- LR-nn: <rule> (from L-NNNN)`. A lesson is triaged in the same change that adds it:
a checkable rule becomes a checker rule plus a fixture (preferred), a rule for all forks
becomes an `LR-nn` or an invariant here, anything else gets `Promotion: none — <reason>`.
Two lessons with the same tag and rule force a promotion.

None yet.

L-0003 is promoted to INV-7; the other seed lessons are promoted to checks.

## Bumping OSCAL / references

- Generated OSCAL is pinned to `1.2.1`, the version `compliance-trestle==5.2.0` accepts.
  Bump `OSCAL_VERSION`, the NIST schemas and trestle together, never one alone.
- Input catalogs and profiles (NIST oscal-content) may be any `1.2.x`; they are read as
  raw JSON, never through trestle models (L-0004).
- OSCAL schema validation uses the `regex`-backed validator plus `FormatChecker` (L-0005).
- † Reference PDFs: add or update the entry in `references/index.yaml`, run
  `rmf refs fetch` (or the browser-assisted import for blocked sites, L-0002/L-0003),
  `rmf refs extract`, `rmf refs index`, and commit the PDF (LFS), text and index together.
  Probe URLs with a ranged GET, never HEAD (L-0001).
