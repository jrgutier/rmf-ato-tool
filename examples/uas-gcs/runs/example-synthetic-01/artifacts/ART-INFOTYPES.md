---
artifact_id: ART-INFOTYPES
run_id: example-synthetic-01
produced_by_task: P-12
touched_by: [P-12, P-13]
sources: [INT-014.A1, INT-014.A2, INT-014.A3, INT-015.A1, INT-016.A1, INT-016.A2, ASM-007, product/conops.md#information]
---
# Information types and information life cycle

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

## Information types

| ID | Information type | SP 800-60 identifier | Provisional C / I / A | Adjustment |
|---|---|---|---|---|
| INF-01 | Command and control data | D.1.3 | moderate / moderate / moderate | none |
| INF-02 | Sensor video and still images | D.1.3 | moderate / moderate / low | none |
| INF-03 | Mission plans and flight logs | D.1.3 | moderate / moderate / low | none |
| INF-04 | Map and terrain data | organization-defined | low / moderate / low | none |
| INF-05 | Security management data | C.3.5.5, C.3.5.8 | moderate / moderate / low | none |

The five types come from the information owner [[INT-014.A1]] [[product/conops.md#information]];
the provisional levels and their reasons are the owner's [[INT-014.A2]]. The SP 800-60 mapping
is an assumption pending the categorization in C-2 [[ASM-007]]. Records live in
`artifacts/data/infotypes.yaml`.

## Privacy

Only INF-05 contains PII: names and CAC-derived identifiers of DoD users in account and audit
records. Imagery is of an area of operations, nothing is retrieved by name and the system is not
a system of records; the Privacy Overlay applies to INF-05. This determination goes to the
SAOP's designee for approval through a privacy threshold analysis [[INT-015.A1]].

## Information owners

INF-01, INF-02 and INF-03 belong to the supported brigade's operations staff as information
owner [[INT-014.A3]] [[ASM-006]]. INF-04 belongs to the brigade geospatial cell that publishes
it, and INF-05 to the system owner, kept by the ISSM [[INT-014.A3]].

## Information life cycle

- **INF-01:** created in CMP-C2 from the imported plan, sent and returned over CMP-GDT and
  CMP-AV, displayed and logged, deleted at kit reset; mission keys zeroized after each mission
  [[INT-016.A1]] [[INT-016.A2]].
- **INF-02:** collected through CMP-AV and CMP-GDT, recorded and clipped in CMP-VIDEO, stored on
  the encrypted CMP-WS-HW disk, released through CMP-ROUTER to the intelligence system (queued
  while disconnected), deleted after verified transfer [[INT-016.A1]] [[INT-016.A2]].
- **INF-03:** created in CMP-PLANNER, imported into CMP-C2 with an integrity hash, sent with
  the products, deleted after transfer [[INT-016.A1]] [[product/data-flows.md#top]].
- **INF-04:** arrives on signed removable media, used in CMP-PLANNER, replaced by the next
  package [[INT-016.A2]].
- **INF-05:** created by CMP-WS-OS, CMP-ROUTER and the applications, held 90 days, forwarded to
  the enclave collector over TLS, aged out; disks sanitized before a kit leaves the program
  [[INT-016.A2]] [[product/architecture.md#logging]].

Stages and components per type are recorded in `artifacts/data/infotypes.yaml`.
