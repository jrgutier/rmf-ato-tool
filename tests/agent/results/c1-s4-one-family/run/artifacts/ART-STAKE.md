---
artifact_id: ART-STAKE
run_id: agent-c1-s4-one-family
produced_by_task: P-9
touched_by: [P-9]
sources: [product/conops.md#program, product/conops.md#users]
---
# Stakeholder register — ESG

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

<!-- Seeded for the walking-skeleton scenario (P-9 is out of scope). FICTIONAL
     organization. -->

## Stakeholders and interview roster

Each stakeholder is represented in interviews by a persona; in synthetic mode the agent
role-plays the persona from its card in `personas/` [[product/conops.md#program]].

| Stakeholder | Persona | Interest in ESG | Interview for |
|---|---|---|---|
| RSSPO program manager (system owner) | PER-PM | cost, schedule, fielding after authorization; owner of the ESG configuration and audit information (INF-02, INF-03) | P-10, P-11, C-1, C-2, S-1, A-6 |
| ESG ISSM | PER-ISSM | authorization package, status reporting | P-10, P-11, C-1, C-2, S-1, S-4, A-6 |
| ESG ISSO | PER-ISSO | accounts, logs, patching, assessment evidence | S-4, A-3 |
| ESG systems security engineer | PER-ISSE | security architecture, boundary, control design | P-11, C-2, S-4 |
| Installation security operations (owner of the sensor telemetry) | PER-IO | confidentiality and integrity of alarm data | C-1, C-2, S-1 |
| Developer and integrator (ESIT) | PER-DEV | build pipeline, hardening, update bundles, test results | P-10, S-4, A-3 |
| Common control providers (enclave, ICAM, CSSP) | PER-CCP | what ESG inherits and what ESG must configure | S-1, S-4, A-6 |
| Component assessment team (delegated SCA) | PER-SCA | independent assessment | A-2, A-3 |
| AO designated representative | PER-AODR | categorization review, assessment plan review, risk analysis | C-3, A-2, R-2 |
| Authorizing Official | PER-AO | risk acceptance and the authorization decision | C-3, R-4 |

## Users represented

SOC operators, administrators, field technicians and auditors are described in the CONOPS
[[product/conops.md#users]]; the information owner speaks for the SOC operators' needs.
