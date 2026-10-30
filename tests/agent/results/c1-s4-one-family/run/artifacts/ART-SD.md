---
artifact_id: ART-SD
run_id: agent-c1-s4-one-family
produced_by_task: C-1
touched_by: [C-1]
sources: [INT-001.A1, INT-001.A3, INT-001.A4, INT-001.A5, INT-002.A1, INT-002.A2, INT-002.A3, product/conops.md#mission, product/architecture.md#components]
---
# System description

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

## Mission and purpose

The system gives the installation security operations center a near-real-time picture of
perimeter intrusion and environmental conditions at remote sites [[INT-001.A4]]
[[product/conops.md#mission]]. It senses and forwards only: it makes no decisions and actuates
nothing [[product/conops.md#mission]]. It is under development, with twelve pre-production
units at test sites and 60 units to be fielded after an authorization decision
[[INT-001.A3]].

## System description and functions

Each site has one ruggedized gateway appliance (CMP-GW-HW) running a hardened OS image
(CMP-GW-OS), the collector service (CMP-COLLECTOR), the admin web console (CMP-WEBUI) and a
local buffer database (CMP-STORE), plus up to 40 paired field sensor nodes (CMP-SENSOR-NET)
[[product/architecture.md#components]]. The collector receives and validates sensor messages
over the encrypted field radio, buffers up to 7 days of telemetry and forwards it to IODS over
mutually authenticated TLS 1.3 [[INT-001.A4]] [[ART-BND]]. Audit records go to the CSSP SIEM
over syslog with TLS [[product/architecture.md#logging]].

## Users

Four user groups are recorded in `artifacts/data/users.yaml` [[INT-002.A1]] [[INT-002.A2]]:
SOC operators (USR-SOC-OPS) with no logical access, remote administrators (USR-ADMIN) and on-site
field technicians (USR-FIELDTECH) with privileged access, and auditors (USR-AUDITOR) with
read-only access. Remote users sign in through the identity service with DoD PKI; technicians
share the local `fieldtech` account, a disclosed limitation [[product/conops.md#limitations]].

## Operating environment

Sites are fenced, and each gateway sits in a locked, alarmed shelter whose keys the
installation facilities office controls; sites are visited about once a quarter
[[product/conops.md#environment]]. Each gateway connects through the site switch inside the
installation network enclave [[product/conops.md#environment]] [[ART-BND]].

## Interconnections and leveraged authorizations

The system has one interconnection, IC-1 to IODS, under an agreement signed 2026-04-02
[[INT-001.A5]] [[product/architecture.md#interconnections]], and uses the identity service under
the installation service agreement. It inherits controls from LA-01 (the enclave authorization,
which covers the identity service) and LA-02 (the CSSP authorization), recorded in
`artifacts/data/leveraged-authorizations.yaml` [[INT-001.A5]]
[[product/architecture.md#leveraged]]. Information leaves the system only to IODS and the CSSP
[[INT-002.A3]].
