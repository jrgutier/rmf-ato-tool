---
artifact_id: ART-CAT
run_id: agent-cold-start-resume
produced_by_task: C-2
touched_by: [C-2, C-3]
sources: [INT-007.A1, INT-007.A2, INT-007.A3, INT-008.A1, INT-008.A2, INT-009.A2, INT-009.A3, ART-INFOTYPES, INT-010.A4]
---
# Security categorization

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

## Impact per information type

Each information owner confirmed the values for their types; no value was adjusted in C-2
[[INT-007.A1]] [[INT-008.A1]]:

| Information type | C | I | A | Basis |
|---|---|---|---|---|
| INF-01 Sensor telemetry and alarms (owner: installation security operations) | moderate | moderate | low | [[INT-007.A1]] [[INT-007.A2]] [[INT-007.A3]] |
| INF-02 Configuration and security management data (owner: program) | moderate (raised from low in P-12) | moderate | low | [[INT-008.A1]] [[ART-INFOTYPES]] |
| INF-03 Audit records (owner: program) | moderate | moderate | low | [[INT-008.A2]] |

The ISSM found no missing information type [[INT-009.A1]].

## System categorization

The system categorization in the facts block is the high-water mark per objective over the
three types: every type is moderate for confidentiality and integrity and low for
availability, so each system value equals the common value of its column [[INT-007.A3]]
[[INT-008.A1]] [[INT-008.A2]]. No value was lowered to reduce controls, and the result
matches the risk assessment's impact ratings [[INT-009.A3]].

## Overlays

- Privacy Overlay: applies with the audit-log and account-record set only, because the only
  PII is user names in account and audit records; no low, moderate or high privacy set
  applies [[INT-009.A2]] [[INT-008.A3]].
- Classified Information Overlay: does not apply; no information is classified
  [[INT-007.A4]] [[INT-009.A2]].
- Space Platform Overlay: does not apply; the system is ground-based [[INT-009.A2]].
- No other overlay is mandated by the organizational context [[INT-009.A2]].

## Review and approval

The AODR reviewed the categorization for the AO. They confirmed each information type has
its owner's values [[INT-010.A1]], that each system value is the high-water mark and nothing
was lowered for cost (they challenged availability and upheld it) [[INT-010.A2]], and that
each overlay decision is reasoned [[INT-010.A3]]. The review raised no finding. The AODR
approved the categorization and overlay selection, on the condition that a privacy office
result showing additional PII reopens it [[INT-010.A4]].
