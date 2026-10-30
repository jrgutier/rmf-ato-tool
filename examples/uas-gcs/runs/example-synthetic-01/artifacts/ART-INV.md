---
artifact_id: ART-INV
run_id: example-synthetic-01
produced_by_task: P-10
touched_by: [P-10, I-2, M-1]
sources: [INT-107.A1, INT-108.A1, INT-064.A1, ART-STIG, product/hw-sw-inventory.md#items, product/architecture.md#components, INT-010.A1, INT-011.A1]
---
# Hardware and software inventory

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Tactical UAS Ground Control Station | C-1 |
| Acronym | ETGCS | C-1 |
| System ID | ETGCS-REG-SIM-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ETGCS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/MODERATE; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-M | S-1 |
<!-- END rmf:facts -->

## How the inventory was compiled

The inventory is the program's configuration-item list for release 2.3.0
[[product/hw-sw-inventory.md#items]], mapped to the architecture's components
[[product/architecture.md#components]]. The integrator's software lead confirmed it complete
and that every station carries the same items [[INT-010.A1]]; the system owner ranked the
assets [[INT-011.A1]]. The records live in `artifacts/data/inventory.yaml`.

## Inventory summary

Ten items, all inside the boundary [[INT-010.A1]]:

- by kind: 3 hardware (INV-001, INV-006, INV-009); 1 operating system
  (INV-002); 4 software (INV-003, INV-004, INV-005, INV-010); 1 firmware (INV-007); 1 network
  device (INV-008) [[product/hw-sw-inventory.md#items]];
- by component: CMP-WS-HW (INV-001), CMP-WS-OS (INV-002), CMP-C2 (INV-003), CMP-PLANNER
  (INV-004, INV-010), CMP-VIDEO (INV-005), CMP-GDT (INV-006, INV-007), CMP-ROUTER (INV-008),
  CMP-AV (INV-009) [[product/architecture.md#components]].

The GDT management web service is part of the firmware INV-007, not a separate item
[[INT-010.A2]]. The enclave (CMP-BTNE) and the brigade intelligence system (CMP-BIS) are
outside the boundary and are not inventory items [[INT-011.A2]].

## Asset priority

- **High:** the flight control path, INV-001, INV-002, INV-003, INV-006, INV-007, INV-008 and
  INV-009; losing or corrupting any of them grounds or endangers the aircraft [[INT-011.A1]].
- **Moderate:** INV-004 and INV-005; a crew can fly a pre-planned route without them
  [[INT-011.A1]].
- **Low:** INV-010; map data is reloaded each mission [[product/hw-sw-inventory.md#priority]].

## Uncertain items

None. The map package INV-010 has no fixed version by design and is tracked as a package
[[INT-010.A3]]; the planned planner replacement is not chosen and is not listed [[INT-011.A2]].

## Update Control Implementation Information (I-2)

The inventory matches the as-built 2.3.0 test stations; no item or version changed during
implementation, and GDT firmware INV-007 stays at 5.1.8 until 5.2.1 passes regression testing
for the 2026-12 bundle [[INT-064.A1]]. Each software, operating-system and firmware item now
has a benchmark or a not-applicable rationale in the STIG summary [[ART-STIG]]. `inventory.yaml`
is unchanged.

## System and Environment Changes (M-1)

No item was added, removed or replaced in the first monitoring cycle. CR-2026-10 patches the
existing workstation and router items (INV-002, INV-008) without changing an item, and
CR-2026-12 will move INV-007 from 5.1.8 to 5.2.1 only when the board approves installation
after regression testing [[INT-107.A1]] [[INT-108.A1]]. `inventory.yaml` is unchanged; it is
rewritten at that installation (ART-CHG).
