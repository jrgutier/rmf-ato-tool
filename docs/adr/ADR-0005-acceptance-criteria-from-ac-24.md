# ADR-0005: record acceptance criteria from AC-24 here

Date: 2026-10-31 · Status: accepted · Phase: 8

## Context

AC-1 to AC-23 are defined in the original plan under `.omc/plans/`, which is gitignored.
The coverage work (`docs/audits/2026-10-31-coverage-audit.md`) adds rules, and every rule in
`src/rmf_tool/check/registry.yaml` names an AC.

## Decision

Acceptance criteria from AC-24 on are defined in this ADR, one line each, and extended in
later phases by appending below. A rule that cites an AC points here.

| AC | Phase | Criterion | Rule |
|---|---|---|---|
| AC-24 | p8 | The counts that README.md, AGENTS.md and the registry header state equal the values computed from the registry, framework and reference index | DOC-002 |

## Consequences

- `docs/CHECKS.md` lists AC-24 for DOC-002, and this file says what it means.
- An AC is never renumbered or reused (INV-3).
