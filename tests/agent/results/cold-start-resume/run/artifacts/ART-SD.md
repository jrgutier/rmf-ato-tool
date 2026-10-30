---
artifact_id: ART-SD
run_id: agent-cold-start-resume
produced_by_task: C-1
touched_by: [C-1]
sources: [INT-005.A3, INT-005.A4, INT-005.A5, INT-006.A1, INT-006.A2, INT-006.A3, INT-006.A4, product/conops.md#mission, product/conops.md#environment, product/architecture.md#components]
---
# System description

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

## Mission and purpose

The system gives the installation security operations center (SOC) a near-real-time picture
of perimeter intrusion and environmental conditions (temperature, flooding, power loss) at
remote sites [[INT-005.A4]] [[product/conops.md#mission]]. It senses and forwards only: it
makes no decisions and actuates nothing, and operators act on alarms through separate
systems [[INT-005.A4]] [[INT-006.A1]].

## System description and functions

Each site has one ruggedized gateway appliance (CMP-GW-HW) running a hardened Linux-based OS
image with host firewall and audit daemon (CMP-GW-OS), a sensor collector service
(CMP-COLLECTOR), an admin web console (CMP-WEBUI) and a local buffer database (CMP-STORE),
paired with up to 40 battery-powered field sensor nodes (CMP-SENSOR-NET)
[[product/architecture.md#components]]. The collector receives readings over the encrypted
field radio, validates them, buffers up to 7 days locally while IODS is unreachable and
forwards them to IODS [[INT-005.A4]]. The system is in engineering and manufacturing
development: twelve pre-production units at test sites feed a test instance of IODS, none
has carried operational alarm traffic, and 60 units are to be fielded after an authorization
decision [[INT-005.A3]]. The eight inventory items are described in ART-INV [[ART-INV]].

## Users

User groups are recorded in `artifacts/data/users.yaml` [[INT-006.A2]]:

| Group | Access |
|---|---|
| USR-SOC-OPERATOR | no logical access; reads alarms in IODS [[INT-006.A1]] |
| USR-ADMIN | privileged, remote, DoD PKI through the identity service [[INT-006.A2]] |
| USR-FIELD-TECH | privileged, on site via the maintenance port, shared local account [[INT-006.A3]] |
| USR-AUDITOR | read-only, remote, DoD PKI through the identity service [[INT-006.A2]] |
| USR-BREAK-GLASS | sealed emergency local account, use logged and reported [[INT-006.A2]] |

Remote users are individually attributable; field technicians are not, because they share
the `fieldtech` account until per-technician accounts arrive in release 2.3 (planned
2027-03) [[INT-006.A3]] [[product/conops.md#limitations]]. The only personal data held are
user names in account and audit records [[INT-006.A4]].

## Operating environment

Gateways sit in locked, alarmed equipment shelters at fenced remote sites visited about once
a quarter; shelter keys are controlled by the installation facilities office
[[product/conops.md#environment]]. Each gateway connects through the site switch inside the
Installation Network Enclave, which provides the enclave firewall, intrusion detection and
network access control [[product/conops.md#environment]]. Fielded units are updated only at
quarterly site visits until remote update arrives in release 2.2 (planned 2026-12)
[[product/conops.md#limitations]].

## Interconnections and leveraged authorizations

Telemetry and alarms leave only to IODS (IC-1) under an interconnection agreement signed
2026-04-02, and audit records leave only to the CSSP SIEM [[INT-005.A5]] [[INT-006.A4]].
Remote sign-in uses the Installation ICAM Service (IC-2) under a service agreement
[[INT-005.A5]]. The system inherits controls from two leveraged authorizations recorded in
`artifacts/data/leveraged-authorizations.yaml`: LA-01, the Installation Network Enclave ATO
of 2025-11-20 (covering the ICAM service), and LA-02, the Installation CSSP ATO of
2026-01-30 [[INT-005.A5]]. IODS is separately authorized but is an interconnection, not a
leveraged authorization [[INT-005.A5]].
