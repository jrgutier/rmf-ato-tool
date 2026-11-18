---
artifact_id: ART-INV
run_id: 20261118-synthetic-01
produced_by_task: P-10
touched_by: [P-10, I-2]
sources: [INT-023.A1, INT-023.A2, INT-023.A3, INT-023.A4, INT-024.A1, INT-024.A2, INT-024.A3, INT-024.A4, product/hw-sw-inventory.md#items, product/hw-sw-inventory.md#priority, INT-139.A1, ART-STIG]
---
# Hardware and software inventory

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Fleet Readiness Analytics Service | C-1 |
| Acronym | EFRAS | C-1 |
| System ID | EFRAS | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | EFRAS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-MODERATE, CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-50 | S-1 |
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Aviation Readiness Software Program Office (ARSPO), naval aviation PEO (fictional) | C-1 |
| System version | 1.5 (MVCR) (released 2026-10-27) | C-1 |
| Operational environment | production | C-1 |
| Life-cycle phase | PH-PD | C-1 |
<!-- END rmf:facts -->

## How the inventory was compiled

The inventory starts from the program's hardware and software list and component table
[[product/hw-sw-inventory.md#items]] [[product/architecture.md#components]]. The ERST
technical lead confirmed each item, its version and the component it runs on, and that nothing
installed in production is missing from the list [[INT-023.A1]] [[INT-023.A2]]. The system
owner confirmed the priorities, the owner of record and the authoritative repository, the
Component IT asset management repository record EFRAS-PROD [[INT-024.A1]] [[INT-024.A3]].
The records live in `artifacts/data/inventory.yaml`, together with the asset scope, the
non-inventory assets AST-001 to AST-007 and the high-value asset determination (not an HVA)
[[INT-024.A4]].

Each line of the product list is one configuration item, as the developer explained: replicas,
worker nodes and the database standby are running instances of one versioned image or service
configuration, so no record stands for several units [[INT-023.A4]].

## Inventory summary

Sixteen items, INV-001 to INV-016, all inside the boundary [[product/hw-sw-inventory.md#items]]:

| Kind | Count | Items |
|---|---|---|
| service | 6 | INV-001, INV-008, INV-011, INV-012, INV-013, INV-014 |
| software | 7 | INV-002 to INV-006, INV-015, INV-016 |
| operating-system | 1 | INV-007 |
| virtual-machine | 1 | INV-009 |
| database | 1 | INV-010 |

By component: CMP-API (INV-003, INV-016), CMP-REPORT (INV-006, INV-015), CMP-K8S (INV-007,
INV-008, INV-009), and one item each for CMP-EDGE, CMP-WEB, CMP-INGEST, CMP-FORECAST, CMP-DB,
CMP-OBJ, CMP-KMS, CMP-LOGS and CMP-SANDBOX [[INT-023.A1]]. No hardware or firmware is
program-owned; both are inherited from the cloud provider [[INT-023.A3]].

## Asset priority

| Priority | Items and assets | Reason |
|---|---|---|
| high | INV-001, INV-003, INV-004, INV-007 to INV-012, INV-016; AST-001, AST-003, AST-004 | the data path that holds or moves CUI and PII, the only ingress, and the platform every service runs on |
| moderate | INV-002, INV-005, INV-013; AST-002, AST-005 to AST-007 | losing them delays reporting within the 72-hour tolerance |
| low | INV-006, INV-014, INV-015 | low mission impact; INV-015 still carries the open vulnerabilities |

The system owner accepts this ranking [[INT-024.A1]] [[product/hw-sw-inventory.md#priority]].

## Uncertain items

No item's presence or version is uncertain [[INT-023.A1]]. Two changes are planned but not
fielded and are not in the inventory: release 1.5.2 replaces the base image and INV-015's
version (2026-12-10), and release 1.6 may add an audit archive storage item (2027-01-15)
[[INT-024.A2]].

## Update Control Implementation Information (I-2)

Implementation added or removed no item, so `inventory.yaml` is not rewritten: the same sixteen
items, base image 2026.09, node image 2026.10, PostgreSQL 16.4 and example-imagelib 2.9.1
[[INT-139.A1]]. Release 1.5.1 of 2026-11-07 (PT-1 export scoping fix, server header) runs in
pre-production; nothing is in production yet. The container records keep version 1.5.0, as the
program's inventory list does, because the inventory follows the release deployed to production
and the pipeline updates it at the next production release tag [[INT-139.A1]]
[[product/hw-sw-inventory.md#items]]. I-1 mapped every software, operating-system, database and
virtual-machine item to a secure configuration benchmark or a not-applicable reason in the STIG
summary (ART-STIG) [[ART-STIG]].
