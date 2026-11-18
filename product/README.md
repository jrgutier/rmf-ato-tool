# Example Fleet Readiness Analytics Service (EFRAS) — product package {#top}

> **FICTIONAL — FOR DEMONSTRATION.** EFRAS, its program office, its cloud provider, its
> software factory, its vendors, its units and every person, date and result in this package
> are invented to dry-run the `rmf` tool's fork workflow. Nothing here describes a real
> product, vendor, organization or system.

This is the product material the program office hands to its RMF team. An agent cites it with
`product/<file>#<anchor>` trace tokens; every heading below carries an explicit `{#anchor}`.

| File | What it holds |
|---|---|
| `profile.yaml` | proposed identity and categorization (proposed values only; tasks confirm them) |
| `conops.md` | mission, program, users, operating environment, information, availability, known limitations |
| `stakeholders.md` | the program's named roles (all fictional) and who holds which RMF role |
| `architecture.md` | components (`CMP-*`), boundary, network, interconnections, leveraged authorizations, identity, logging, configuration, updates, physical protection |
| `data-flows.md` | data flows (`DF-*`) and the information they carry |
| `hw-sw-inventory.md` | software, service and virtual items (`INV-###`) mapped to components |
| `test-results.md` | pipeline, developmental test, scan, penetration test and review results the assessor may reuse |
| `privacy.md` | the PII EFRAS handles, its authority, notices and the draft privacy impact assessment status |
| `monitoring/cycle-2026-11.md` | monitoring records of the first monitoring cycle (EXT-MONITORING, used by M-2) |

## Stable identifiers {#identifiers}

The component IDs (`CMP-*`) in `architecture.md` and the inventory IDs (`INV-###`) in
`hw-sw-inventory.md` are the program's configuration-item numbers. Keep them unchanged in every
run artifact (AGENTS.md INV-3).

## Classification note {#classification}

EFRAS is described here at an unclassified, public level only. No CUI is in this package
(AGENTS.md INV-7). Where the real system would handle CUI, this package only says so.
