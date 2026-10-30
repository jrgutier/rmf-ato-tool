# Example Tactical UAS Ground Control Station (ETGCS) — product package {#top}

> **FICTIONAL — FOR DEMONSTRATION.** ETGCS, its aircraft, its program office, its vendors,
> its units and every person, date and result in this package are invented to demonstrate
> the `rmf` tool. Nothing here describes a real product, vendor, organization or system.

This is the product material a program office hands to its RMF team for the example
synthetic run (`runs/example-synthetic-01`). An agent cites it with `product/<file>#<anchor>`
trace tokens; every heading below carries an explicit `{#anchor}`.

| File | What it holds |
|---|---|
| `profile.yaml` | proposed identity and categorization (proposed values only; tasks confirm them) |
| `conops.md` | mission, program, users, operating environment, information, known limitations |
| `stakeholders.md` | the program's named roles (all fictional) and who holds which RMF role |
| `architecture.md` | components (`CMP-*`), boundary, network, interfaces, identity, logging, configuration, updates |
| `data-flows.md` | data flows (`DF-*`) and the information they carry |
| `hw-sw-inventory.md` | hardware and software items (`INV-###`) mapped to components |
| `test-results.md` | developer and developmental test results available to the assessor |
| `monitoring/cycle-2026-10.md` | monitoring records of the first monitoring cycle (EXT-MONITORING, used by M-2) |

## Stable identifiers {#identifiers}

The component IDs (`CMP-*`) in `architecture.md` and the inventory IDs (`INV-###`) in
`hw-sw-inventory.md` are the program's configuration-item numbers. Keep them unchanged in
every run artifact (AGENTS.md INV-3).

## Classification note {#classification}

ETGCS is described here at an unclassified, public level only. No CUI is in this package
(AGENTS.md INV-7).
