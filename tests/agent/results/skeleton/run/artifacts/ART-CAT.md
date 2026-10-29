---
artifact_id: ART-CAT
run_id: agent-skeleton
produced_by_task: C-2
touched_by: [C-2, C-3]
sources: [INT-007.A1, INT-007.A2, INT-007.A3, INT-007.A4, INT-008.A1, INT-008.A2, INT-008.A3, INT-009.A1, INT-009.A2, INT-009.A3, INT-009.A4, ART-INFOTYPES, ART-SD, ART-RA, ASM-002, INT-010.A1, INT-010.A2, INT-010.A3, INT-010.A4]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Impact per information type

Each information owner set the values of the types they own, following CNSSI 1253 §3.1: the
installation security operations organization for INF-01 and the program for INF-02 and
INF-03 [[ART-INFOTYPES]] [[INT-007.A4]].

| Information type | C | I | A | Basis |
|---|---|---|---|---|
| INF-01 Perimeter and environmental sensor telemetry and alarms | moderate | moderate | low | C [[INT-007.A1]], I [[INT-007.A2]], A [[INT-007.A3]]; provisional values kept |
| INF-02 ESG configuration and security management data | moderate | moderate | low | C raised from the low base for private keys and firewall rules, I and A kept [[INT-008.A1]] [[ART-INFOTYPES]] |
| INF-03 ESG audit records | moderate | moderate | low | provisional values kept [[INT-008.A2]] |

No owner adjusted a provisional value in this task; the one adjustment, INF-02
confidentiality, was made in the information-type analysis and the program confirmed it
[[INT-008.A1]]. The ISSM confirmed that no information type is missing [[INT-009.A3]].

## System categorization

The system categorization in the facts block is the high-water mark per objective over the
three types (CNSSI 1253 §3.1.2 step 1): confidentiality and integrity take the moderate value
every type carries, and availability takes the low value every type carries [[INT-007.A1]]
[[INT-008.A1]] [[INT-008.A2]]. No value was lowered to reduce the control set
[[INT-008.A3]], and the values agree with the risk assessment, whose only availability event
is rated low impact [[INT-009.A4]] [[ART-RA]]. The result matches the categorization the
product profile proposed [[product/profile.yaml]].

## Overlays

- Privacy overlay (CNSSI1253F-ATT6-PRIVACY): does not apply; the only personal data is the
  user names of the system's own users, pending the privacy office's confirmation
  [[INT-009.A1]] [[ASM-002]].
- Classified information overlay (CNSSI1253E-ATT5-CLASSIFIED): does not apply; the owner
  handles the telemetry as unclassified and no classified information is on the system
  [[INT-007.A4]] [[INT-009.A2]].
- Space platform overlay (CNSSI1253F-ATT2-SPACE): does not apply; the system is ground
  appliances in equipment shelters [[INT-009.A2]].
- No overlay is mandated by the organizational context [[INT-009.A2]].

## Review and approval

The AODR reviewed the categorization for the AO under delegation [[INT-010.A1]]. They checked
that every information type has its owner's value and that the one adjustment raised a value
for a concrete reason [[INT-010.A1]]; recomputed the high-water mark per objective and found
no value lowered for cost and no conflict with the risk assessment [[INT-010.A2]]; and checked
the reason for each overlay decision [[INT-010.A3]]. The review raised no finding, so no
correction was needed [[INT-010.A2]]. The AODR approved the categorization shown in the facts
block, on condition that it returns for the privacy overlay and the SAOP's approval if the
privacy office finds that the system processes PII (ASM-002) [[INT-010.A4]] [[ASM-002]].
