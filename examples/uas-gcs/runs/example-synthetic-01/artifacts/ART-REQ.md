---
artifact_id: ART-REQ
run_id: example-synthetic-01
produced_by_task: P-15
touched_by: [P-15, P-17]
sources: [INT-018.A1, INT-018.A2, INT-018.A3, INT-020.A1, ASM-008, ART-RA, ART-INFOTYPES, ART-STAKE]
---
# Security and privacy requirements and allocation

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

## Sources of requirements

No capability document or organizational policy is supplied [[ASM-008]]. Requirements come from
DoDI 8510.01 and the CNSSI 1253 baseline that S-1 will select, the system risk assessment
(ART-RA), the information types and privacy determination (ART-INFOTYPES) and the stakeholders
in ART-STAKE [[INT-018.A1]] [[ART-RA]] [[ART-INFOTYPES]] [[ART-STAKE]].

## Security and privacy requirements

| ID | Requirement | Source | Priority | Allocated to |
|---|---|---|---|---|
| REQ-01 | Every privileged action, including offline maintenance, is attributable to an individual | ART-RA TE-5 | 1 | CMP-WS-OS, CMP-ROUTER; CMP-BTNE directory when connected |
| REQ-02 | The aircraft link is encrypted and commands are authenticated | ART-RA TE-1, INF-01 | 1 | CMP-GDT, CMP-AV |
| REQ-03 | Flaws in every component, GDT firmware included, are remediated in the quarterly bundle, critical flaws sooner | ART-RA TE-6 | 1 | all components, via the integrator bundle |
| REQ-04 | Only signed update bundles and checked media are installed | ART-RA TE-3, TE-4 | 2 | CMP-WS-OS, CMP-ROUTER, CMP-GDT |
| REQ-05 | Every component runs a STIG or an assessed hardening baseline | ART-RA TE-7 | 2 | all components; CMP-PLANNER needs an assessed baseline |
| REQ-06 | Audit records from every component reach the enclave collector when connected | ART-RA TE-8 | 2 | station generates and holds; CMP-BTNE collects and reviews |
| REQ-07 | The GDT management service uses individual, strong authenticators | ART-RA TE-6 | 2 | CMP-GDT |
| REQ-08 | Mission and security data are protected at rest | INF-01..INF-05, ART-RA TE-2 | 2 | CMP-WS-HW |
| REQ-09 | PII in account and audit records is limited to what operations need | INF-05 privacy determination | 3 | CMP-WS-OS, CMP-ROUTER |
| REQ-10 | A replacement station operates within 4 hours of an outage | availability need | 3 | environment of operation (spare kits) |

Requirements and their order are the system owner's [[INT-018.A2]]; allocation is the ISSE's
[[INT-020.A1]].

## Operational constraints

Stations operate disconnected for days, so nothing that blocks flight may depend on the uplink;
CAC sign-in must work offline; maintainers work without network access; the kit runs on vehicle
or generator power; a spare kit must be up within 4 hours [[INT-018.A3]].

## Allocation

The station carries every function that must work disconnected (REQ-01, REQ-02, REQ-04, REQ-05,
REQ-08); the enclave (CMP-BTNE) provides the connected directory, log collection and review as
inherited services, so REQ-01 and REQ-06 are split between the station and the enclave. REQ-03
is delivered for all components through the integrator's signed bundle. REQ-10 falls to the
environment of operation through brigade spare stock [[INT-020.A1]].
