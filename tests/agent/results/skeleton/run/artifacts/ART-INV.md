---
artifact_id: ART-INV
run_id: agent-skeleton
produced_by_task: P-10
touched_by: [P-10]
sources: [product/hw-sw-inventory.md#items, product/hw-sw-inventory.md#priority, product/architecture.md#components, INT-001.A1, INT-001.A2, INT-001.A3, INT-002.A1, INT-002.A3]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## How the inventory was compiled

The inventory starts from the program's configuration-item list, whose `INV-###` IDs are kept
unchanged [[product/hw-sw-inventory.md#items]], mapped to the components of the product
architecture [[product/architecture.md#components]]. The developer confirmed the list, the
release 2.1.4 versions and the component of every item, and stated that nothing else is
installed [[INT-001.A1]] [[INT-001.A2]] [[INT-001.A3]]. The program manager confirmed that the
program owns only the gateways and sensor nodes; IODS, the identity service, the enclave and
the CSSP are other programs' systems and are left to the boundary description, not this
inventory [[INT-002.A3]].

## Inventory summary

The records live in `artifacts/data/inventory.yaml`: 8 items in total
[[product/hw-sw-inventory.md#items]].

| By kind | Count | Items |
|---|---|---|
| hardware | 2 | INV-001, INV-007 |
| operating-system | 1 | INV-002 |
| software | 2 | INV-003, INV-004 |
| database | 1 | INV-005 |
| firmware | 2 | INV-006, INV-008 |

| By component | Items |
|---|---|
| CMP-GW-HW | INV-001, INV-006 |
| CMP-GW-OS | INV-002 |
| CMP-COLLECTOR | INV-003 |
| CMP-WEBUI | INV-004 |
| CMP-STORE | INV-005 |
| CMP-SENSOR-NET | INV-007, INV-008 |

The host firewall, audit daemon and nightly configuration check are part of the OS image
(INV-002), not separate items [[INT-001.A2]] [[INT-001.A3]]. Gateways are physical units named
by site; none is virtual or publicly reachable, and sensor nodes have no IP address
[[INT-001.A4]].

## Asset priority

The program manager ranks the gateway appliance, OS image, collector and console (INV-001 to
INV-004) high, because losing or corrupting them silences a whole site or sends false alarms
to the SOC [[INT-002.A1]] [[product/hw-sw-inventory.md#priority]]. The radio firmware, sensor
nodes, node firmware and buffer database (INV-005 to INV-008) are moderate: a failed node is a
local coverage gap, and the buffer only matters while IODS is unreachable [[INT-002.A1]].

## Uncertain items

No item's presence is in doubt [[INT-001.A3]]. Versions are those of release 2.1.4; because
fielded units are updated only at quarterly site visits, a site may run one monthly bundle
behind until its next visit, so the recorded versions are the approved baseline rather than a
guarantee for every unit at every moment [[INT-001.A3]]. Remote update (release 2.2) is planned
and adds no asset [[INT-002.A2]].
