---
artifact_id: ART-INV
run_id: agent-skeleton
produced_by_task: P-10
touched_by: [P-10]
sources: [product/hw-sw-inventory.md#items, product/architecture.md#components, INT-001.A1, INT-001.A3, INT-002.A1]
---
# Hardware and software inventory

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ESG-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## How the inventory was compiled

The inventory starts from the program's hardware and software list
[[product/hw-sw-inventory.md#items]] and the component list in the architecture
[[product/architecture.md#components]]. The developer confirmed the eight items, their
versions and the component each runs on, and that nothing else is installed [[INT-001.A1]]
[[INT-001.A3]]; the program manager ranked the assets and confirmed no new items are planned
[[INT-002.A1]] [[INT-002.A2]]. The product list and the developer agreed; no item was added or
dropped [[INT-001.A1]].

## Inventory summary

The inventory in `artifacts/data/inventory.yaml` holds 8 items, all inside the boundary
[[INT-001.A3]]:

| Kind | Count | Items |
|---|---|---|
| hardware | 2 | INV-001, INV-007 |
| operating-system | 1 | INV-002 |
| software | 2 | INV-003, INV-004 |
| database | 1 | INV-005 |
| firmware | 2 | INV-006, INV-008 |

By component: CMP-GW-HW (INV-001, INV-006), CMP-GW-OS (INV-002), CMP-COLLECTOR (INV-003),
CMP-WEBUI (INV-004), CMP-STORE (INV-005), CMP-SENSOR-NET (INV-007, INV-008)
[[product/hw-sw-inventory.md#items]]. The host firewall, audit daemon and configuration check
are part of INV-002, not separate items [[INT-001.A1]]. Gateways are physical, named
`esg-<site>-01`, and not reachable from the public internet; sensor nodes have no IP address
[[INT-001.A4]]. Externally provided services (IODS, ICAM, enclave, CSSP) are not inventory
items [[INT-002.A3]].

## Asset priority

| Priority | Items | Reason |
|---|---|---|
| high | INV-001, INV-002, INV-003, INV-004 | losing or corrupting the gateway or its software removes or falsifies a whole site's sensing [[INT-002.A1]] |
| moderate | INV-005, INV-006, INV-007, INV-008 | a failed node leaves a coverage gap; the buffer matters only while IODS is unreachable [[product/hw-sw-inventory.md#priority]] |

## Uncertain items

The listed versions are the approved 2.1.4 baseline. Because fielded units are updated only at
quarterly site visits, an individual unit may run an older update bundle than the baseline;
which bundle each unit runs is an operational record the developer does not hold
[[INT-001.A2]] [[product/conops.md#limitations]]. No item's presence is uncertain
[[INT-001.A1]].
