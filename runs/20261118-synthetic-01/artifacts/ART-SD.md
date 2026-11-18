---
artifact_id: ART-SD
run_id: 20261118-synthetic-01
produced_by_task: C-1
touched_by: [C-1]
sources: [INT-058.A1, INT-058.A2, INT-058.A3, INT-058.A4, INT-058.A5, INT-058.A6, INT-059.A1, INT-059.A2, INT-059.A3, INT-060.A1, INT-060.A2, INT-060.A3, INT-060.A4, INT-060.A5, INT-060.A6, ASM-015, ASM-016, product/conops.md#mission, product/conops.md#users, product/conops.md#environment, product/architecture.md#components, product/architecture.md#leveraged, product/architecture.md#interconnections, ART-BND, ART-INV, ART-REQ]
---
# System description

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

## Mission and purpose

The system helps the naval aviation community keep aircraft mission-capable. It turns the
nightly maintenance and supply records into squadron, air wing and fleet readiness views and a
30-day part-failure forecast, so maintenance officers can order parts before aircraft go down
[[INT-058.A5]] [[product/conops.md#mission]]. It is decision support only: it does not write
back to EMIS, order parts or change aircraft status. If it is down, squadrons fall back to
EMIS reports and fleet readiness reporting slips by a day or more, but no aircraft is grounded
[[product/conops.md#mission]]. It supports the missions and processes MSN-01 to MSN-05 that P-8
recorded; none is mission essential [[ART-BIA]].

## System description and functions

The system is a government-owned application operated day to day by the developer's contractor
team under program direction, inside one program-owned production cloud account
[[INT-058.A4]]. Its twelve components (ART-BND) work end to end as follows [[ART-BND]]
[[product/architecture.md#components]]:

- **Ingest.** The nightly ingest worker (CMP-INGEST) pulls the signed EMIS extract and the
  supply status, validates them and loads the managed database (CMP-DB). Landing files sit in
  object storage (CMP-OBJ).
- **Forecast.** The forecast batch job (CMP-FORECAST) scores the part-failure model each night.
- **Serve.** Users reach the web front end (CMP-WEB) and the readiness API (CMP-API) through
  the load balancer and web application firewall (CMP-EDGE). The API enforces the five roles.
- **Report.** The report rendering service (CMP-REPORT) produces PDF and slide exports and
  de-identified data sets. Its base image carries two disclosed high-severity vulnerabilities,
  to be fixed in release 1.5.2 [[product/conops.md#limitations]].
- **Platform.** Everything runs on the managed Kubernetes cluster (CMP-K8S), with program-owned
  keys and secrets (CMP-KMS) and the log pipeline (CMP-LOGS), which forwards to the CSSP.
- **Sandbox.** The analytics sandbox (CMP-SANDBOX) holds the pseudonymized training extract
  for model building.

The sixteen inventory items INV-001 to INV-016 are the configuration items of these components
[[ART-INV]]. The system is networked, not stand-alone. Its one DODIN attachment is the
enterprise cloud access point to NIPRNet [[INT-047.A1]]. The security and privacy requirements
it must meet, REQ-01 to REQ-19, are in ART-REQ [[ART-REQ]]. The version being authorized is the
minimum viable capability release; release 1.6 (2027-01-15) fixes the re-identifiable exports
and the audit retention gap [[INT-058.A3]] [[ASM-015]]. The narrative, ownership and physical
setting are recorded in `artifacts/data/system-description.yaml`.

## Users

Eight user groups, USR-MAINTAINERS to USR-LEADERS, are recorded in `artifacts/data/users.yaml`
[[INT-059.A1]] [[INT-060.A4]]:

- **Non-privileged, through CAC sign-in at the identity broker.** About 2,400 squadron
  maintainers (`viewer`), 600 maintenance officers and chiefs (`officer`) and 40 fleet analysts
  (`analyst`). Maintainers and officers see only their own squadron or air wing. The information
  owner approves each `analyst` role with the user's supervisor [[INT-059.A1]]
  [[product/architecture.md#identity]].
- **Privileged.** Four application administrators (`app-admin`); six contractor cloud
  operations engineers, who also keep the two sealed break-glass console accounts; three
  contractor data scientists, privileged only inside the sandbox; and the ISSO and ISSM
  (`auditor`). Each holds the DoD 8140 qualification for the work role and has signed the
  privileged access agreement [[INT-060.A4]].
- **No logical access.** Senior leaders receive CUI-marked briefing slides by e-mail and never
  log in [[INT-059.A2]].

No user needs a clearance. Every user holding an account is a U.S. citizen with a CAC, trained
before provisioning; no foreign national or coalition user has access [[INT-060.A5]]
[[INT-059.A1]]. Information leaves through reports, analyst exports and the sandbox training
extract. The information owner treats the exports and the extract as PII until release 1.6
[[INT-059.A2]] [[product/conops.md#limitations]].

## Operating environment

The authorization covers the production account in the Example GovCloud IL4 region. Release 1.5
runs today in the separate pre-production account for three pilot squadrons, about 140 users,
on synthetic data. That account is outside this authorization [[INT-058.A3]] [[INT-058.A4]]
[[product/conops.md#environment]]. The program owns no data center or building. Physical and
environmental protection is inherited from the cloud provider. The only program-held equipment
is the ERST privileged access workstations, kept in the program's controlled office space
[[INT-058.A5]] [[product/architecture.md#physical]].

The system is a GENSER system. It is aligned to the Component NOSC and to ECSSP, a CSSP that
USCYBERCOM authorized. The CSSP agreement is SVA-001 in `service-agreements.yaml`, and the
alignment is recorded in the CSSP section of the eMASS record. Its mission criticality is
mission support [[INT-060.A2]] [[INT-060.A3]] [[ASM-016]].

## Interconnections and leveraged authorizations

**Interconnections** (`system-description.yaml`), all with DoD Component systems over HTTPS on
443, with no security domain crossed [[INT-058.A6]] [[INT-060.A6]]
[[product/architecture.md#interconnections]]:

| Record | System | Agreement | Its authorization |
|---|---|---|---|
| ICX-01 | EMIS (nightly extract) | memorandum of agreement drafted, in legal review, not signed; connection on the EMIS ISSM's interim e-mail approval of 2026-09-15; target signature 2026-12-31 | ATO 2025-04-22 to 2028-04-22 |
| ICX-02 | Supply status service (nightly API pull) | service-level agreement signed 2026-06-30 | ATO 2024-11-05 |
| ICX-03 | Enterprise identity broker (CAC federation) | enterprise onboarding approval 2026-05-12 | enterprise service ATO |

The unsigned EMIS agreement is a disclosed limitation. The record holds the interim approval
only because the schema needs a date and a signatory; no one has signed the agreement
[[product/conops.md#limitations]] [[ASM-016]].

**Leveraged authorizations** (`leveraged-authorizations.yaml`). The system inherits from four
providers, each an approved common control provider of P-5 [[INT-060.A1]] [[ART-ORG-CONTEXT]]
[[product/architecture.md#leveraged]]:

- LA-01, the cloud region: DoD provisional authorization IL4, 2024-09-18. An external service
  under the Component enterprise cloud contract.
- LA-02, the cloud access point: ATO 2025-01-10, under an enterprise service-level agreement.
- LA-03, the software factory: ATO 2025-10-01, under its tenant service-level agreement. The
  factory has an open POA&M item on the delayed hardened base image.
- LA-04, the CSSP: service agreement of 2026-04-01 under the CSSP's authorization.

**Reciprocity** (`reciprocity.yaml`). There are no Receiving organizations and no received
systems. The system is deployed only into its own production account, and its providers are
inherited, not received [[INT-057.A1]] [[INT-060.A1]].
