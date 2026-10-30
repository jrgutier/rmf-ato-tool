---
artifact_id: ART-STAKE
run_id: example-synthetic-01
produced_by_task: P-9
touched_by: [P-9]
sources: [INT-009.A1, INT-009.A2, INT-009.A3, INT-009.A4, product/stakeholders.md#roles]
---
# Stakeholder register

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

## Stakeholders and interview roster

| Stakeholder | Persona ID | Interest in the system | Interviewed for | Trace |
|---|---|---|---|---|
| Army Aviation Mission Area AO (fictional) | PER-AO | signs the authorization decision | C-3, R-2, R-3, R-4 | [[INT-009.A1]] [[product/stakeholders.md#roles]] |
| AODR, Aviation Systems | PER-AODR | prepares the decision, reviews packages | C-3, S-6, R-2 | [[INT-009.A1]] |
| Product Manager, SUGS-PO (system owner) | PER-PM | owns the system and the POA&M | P-9..P-18, C-1, A-5, A-6, R-3 | [[INT-009.A1]] |
| SUGS-PO ISSM | PER-ISSM | manages the RMF effort for the program | P-10..P-18, S-1..S-5, M tasks | [[INT-009.A1]] |
| ETGCS ISSO | PER-ISSO | day-to-day security operations, account reviews | S-4, I-1, I-2, M-1 | [[INT-009.A1]] |
| EAIG lead security engineer | PER-ISSE | security design and hardening | P-16, P-17, S-4, I-1 | [[INT-009.A1]] |
| EAIG software lead | PER-DEV | builds software releases and update bundles | I-1, M-1 | [[INT-009.A1]] |
| Aviation Systems SCA team | PER-SCA | independent assessment | A-1..A-4 | [[INT-009.A1]] |
| Brigade S6 (Brigade Tactical Network Enclave) | PER-CCP | provides inherited enclave controls; remote administration | P-11, S-3, S-4 | [[INT-009.A1]] [[INT-009.A3]] |
| SUGS-PO chief developmental tester | PER-CDT | DT events whose results the SCA may reuse | A-2, A-3 | [[INT-009.A1]] |
| Supported brigade operations staff (information owner, mission data) | PER-IO | owner of command and control data, imagery, plans and logs | P-12, P-13, C-2 | [[INT-009.A2]] [[ASM-006]] |
| Test platoon leader (user representative) | PER-UR | speaks for operators, commanders and maintainers | P-8, P-15, C-1, A-3 | [[INT-009.A3]] |
| Capability sponsor | PER-SPONSOR | the capability need and mission focus | P-8, P-15 | [[INT-008.A1]] |

## Users represented

The test platoon leader (PER-UR) speaks for the air vehicle operators, mission commanders and
field maintainers; the brigade S6 (PER-CCP) speaks for its remote system administrators
[[INT-009.A3]] [[product/conops.md#users]]. Intelligence analysts never sign in; the brigade
intelligence system's owner represents them for interconnection IC-1 [[INT-009.A3]].

## Stakeholders not interviewed

The milestone decision authority (PER-MDA) is informed through milestone reviews, and the
Component privacy officer (PER-PRIV) reviews the categorization only, since ETGCS holds no PII
beyond user names in account and audit records [[INT-009.A4]]. The geospatial provider that
owns map data is informed only [[INT-009.A2]].
