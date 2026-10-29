# {{ slug }} — product material

This directory holds what your program hands to its RMF team. Agents read it during a run
and cite it as `product/<file>#<anchor>`, where the anchor is the heading's slug
(`## Known limitations` becomes `#known-limitations`), so keep headings stable once a run
has cited them. Replace the guidance in each file with your system's material.

> **CUI rule (AGENTS.md INV-7):** put controlled unclassified information here only if this
> repository, the machines that hold it and the LLM endpoint the agent uses are all
> authorized for it. Otherwise describe the system at an unclassified, public level.

| File | What to put in it |
|---|---|
| `profile.yaml` | proposed name, acronym, pathway, phase and categorization (proposals only; tasks confirm them) |
| `conops.md` | mission, program and lifecycle, users, operating environment, information handled, availability need, known limitations |
| `architecture.md` | components with stable `CMP-*` IDs, boundary, network, interconnections, leveraged authorizations, identity, logging, configuration, updates, physical protection |
| `data-flows.md` | data flows (`DF-*`) with source, destination, path, information and protection |
| `hw-sw-inventory.md` | hardware, software and firmware items with stable `INV-###` IDs and their components |
| `test-results.md` | developer and developmental test results, scans and records the assessor may reuse |

## Stable identifiers

Give every component a `CMP-<NAME>` ID and every inventory item an `INV-###` ID here. Run
artifacts reuse them, and renumbering later breaks every reference (AGENTS.md INV-3).
