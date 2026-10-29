# Example Sensor Gateway (ESG) — product package {#top}

> **FICTIONAL.** ESG, its program office, its vendors, its installation and every person,
> date and result in this package are invented for testing the `rmf` tool. Nothing here
> describes a real product, vendor, organization or system.

This is the product material a program office hands to its RMF team: enough to run the
walking-skeleton scenario (12 RMF tasks, 6 controls: AC-2, AU-2, CM-6, IA-2, SC-7, SI-2).
An agent cites it with `product/<file>#<anchor>` trace tokens; every heading below carries an
explicit `{#anchor}`.

| File | What it holds |
|---|---|
| `profile.yaml` | proposed identity and categorization (proposed values only; tasks confirm them) |
| `conops.md` | mission, users, operating environment, known limitations |
| `architecture.md` | components (`CMP-*`), interfaces, identity, logging, configuration, patching |
| `data-flows.md` | data flows (`DF-*`) and the information they carry |
| `hw-sw-inventory.md` | hardware and software items (`INV-###`) mapped to components |
| `test-results.md` | developer and developmental test results available to the assessor |

## Stable identifiers {#identifiers}

The component IDs (`CMP-*`) in `architecture.md` and the inventory IDs (`INV-###`) in
`hw-sw-inventory.md` are the program's configuration-item numbers. Keep them unchanged in
every run artifact: seeded data (control allocation, STIG results) refers to them.
