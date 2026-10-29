---
artifact_id: ART-SD
run_id: agent-skeleton
produced_by_task: C-1
touched_by: [C-1]
sources: [INT-005.A1, INT-005.A3, INT-005.A4, INT-005.A5, INT-006.A1, INT-006.A2, INT-006.A3, product/conops.md#mission, product/conops.md#users, product/conops.md#environment, product/architecture.md#components, product/architecture.md#interconnections, product/architecture.md#leveraged, ART-BND, ART-INV]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Mission and purpose

The system gives the installation security operations center (SOC) a near-real-time picture
of perimeter intrusion and environmental conditions (temperature, flooding, power loss) at
remote sites [[INT-005.A4]] [[product/conops.md#mission]]. It senses and forwards only: it makes
no decisions and actuates nothing, and operators act on alarms through other systems
[[product/conops.md#mission]]. The program is in engineering and manufacturing development;
twelve pre-production units at test sites feed a test instance of IODS, and 60 units are to be
fielded after an authorization decision [[INT-005.A3]].

## System description and functions

Each site has one gateway appliance (CMP-GW-HW) running a hardened operating system image with
a deny-by-default host firewall and local audit daemon (CMP-GW-OS), a collector service
(CMP-COLLECTOR), an HTTPS admin web console (CMP-WEBUI) and a local buffer database (CMP-STORE),
plus up to 40 paired field sensor nodes (CMP-SENSOR-NET) [[product/architecture.md#components]]
[[ART-INV]]. The collector receives and validates sensor messages over the encrypted field
radio, writes them to the buffer and forwards them to IODS over TLS 1.3 with mutual
certificates; the buffer holds up to 7 days of telemetry while IODS is unreachable
[[INT-005.A4]] [[ART-BND]]. Audit records go to the CSSP SIEM, and nothing else leaves the
system [[INT-006.A3]]. The boundary, network and data flows are described in ART-BND
[[ART-BND]].

## Users

Four user groups are recorded in `artifacts/data/users.yaml` [[INT-006.A1]] [[INT-006.A2]]:

| Group | Access | Privilege |
|---|---|---|
| USR-ADMIN | remote, DoD PKI through the identity service, role `admin` | privileged |
| USR-FIELDTECH | on site through the maintenance port, shared local account `fieldtech` | privileged |
| USR-AUDITOR | remote, DoD PKI through the identity service, role `auditor` (read-only) | non-privileged |
| USR-SOC | none; read alarms in IODS | no logical access |

A sealed break-glass local account is held for administrators [[product/architecture.md#identity]].
Field technicians share one account, so their actions cannot be attributed to an individual;
the program plans per-technician accounts with smart-card login in release 2.3 (2027-03)
[[INT-006.A2]] [[product/conops.md#limitations]].

## Operating environment

Gateways sit in locked, alarmed equipment shelters at fenced remote sites visited about once a
quarter; shelter keys are controlled by the installation facilities office
[[product/conops.md#environment]]. Each gateway connects through the site network switch inside
the Installation Network Enclave, which provides the enclave firewall, intrusion detection and
network access control [[product/conops.md#environment]]. Radio jamming or a dead site link
stops alarms from a site; IODS flags a site silent for 5 minutes
[[product/conops.md#environment]].

## Interconnections and leveraged authorizations

The system sends telemetry to IODS (IC-1) under an interconnection agreement signed 2026-04-02,
and uses the Installation ICAM Service (IC-2) under the installation service agreement
[[INT-005.A5]] [[product/architecture.md#interconnections]]. It inherits controls from two
separately authorized providers, recorded in `artifacts/data/leveraged-authorizations.yaml`:
LA-01, the Installation Network Enclave (ATO 2025-11-20, covering the ICAM service), and LA-02,
the Installation Cybersecurity Service Provider (ATO 2026-01-30) [[INT-005.A5]]
[[product/architecture.md#leveraged]]. IODS is an interconnected system, not a leveraged
authorization [[INT-005.A5]].
