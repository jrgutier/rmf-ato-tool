---
artifact_id: ART-CAT
run_id: agent-c1-s4-one-family
produced_by_task: C-2
touched_by: [C-2, C-3]
sources: [INT-006.A3, INT-003.A1, INT-003.A2, INT-003.A3, INT-004.A1, INT-004.A2, INT-004.A3, INT-005.A1, INT-005.A2, INT-005.A3, ART-INFOTYPES]
---
# Security categorization

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-55 | S-1 |
<!-- END rmf:facts -->

## Impact per information type

| Information type | C | I | A | Basis |
|---|---|---|---|---|
| INF-01 sensor telemetry and alarms | moderate | moderate | low | owner (PER-IO) confirmed all three [[INT-003.A1]] [[INT-003.A2]] |
| INF-02 configuration and security management data | moderate (adjusted from low) | moderate | low | program owner (PER-PM) kept the confidentiality adjustment for keys and firewall rules [[INT-004.A1]] [[ART-INFOTYPES]] |
| INF-03 audit records | moderate | moderate | low | program owner (PER-PM) confirmed [[INT-004.A2]] |

No owner changed a provisional value; the one adjustment (INF-02 confidentiality) was made in
P-12 and confirmed here [[ART-INFOTYPES]] [[INT-004.A1]]. The ISSM found no missing type
[[INT-005.A3]].

## System categorization

Per CNSSI 1253 §3.1.2 step 1, each objective takes the highest value over the three types
(the high-water mark): confidentiality and integrity follow from all three types, and
availability is low for every type [[INT-003.A2]] [[INT-004.A1]] [[INT-004.A2]]. The result is
the system categorization in the facts block, which matches the proposal in
`product/profile.yaml` for C, I and A [[product/profile.yaml]].

## Overlays

- Privacy Overlays: apply, with control set CNSSI1253F-ATT6-PRIVACY-ACCT only, because the only
  PII is user names in account and audit records [[INT-004.A3]] [[INT-005.A1]]. This differs
  from the proposal's empty overlay list [[product/profile.yaml]].
- Classified Information Overlay: does not apply; nothing classified is processed [[INT-005.A2]].
- Space Platform Overlay: does not apply; the system is ground equipment [[INT-005.A2]].

## Review and approval

The AODR reviewed the categorization for the AO: every information type has its owner's
values, each system value is the high-water mark, and no value was lowered [[INT-006.A1]].
Every overlay decision has a reason; the pending privacy office confirmation is noted, and
other PII found by it would return the categorization for review [[INT-006.A2]]. With no open
findings, the AODR approved the categorization in the facts block [[INT-006.A3]].
