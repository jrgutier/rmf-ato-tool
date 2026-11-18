# EFRAS concept of operations {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real system, unit or program is described.

## Mission {#mission}

The Example Fleet Readiness Analytics Service (EFRAS) helps a fictional naval aviation
community keep aircraft mission-capable. Every night EFRAS pulls maintenance actions, part
removals and aircraft status from the separately authorized Example Maintenance Information
System (EMIS), joins them with supply status, and shows squadron, air wing and fleet readiness
dashboards. A forecasting job predicts which parts are likely to fail in the next 30 days so
maintenance officers can order them early.

EFRAS is decision support only. It does not write back to EMIS, order parts, or change aircraft
status; maintainers act in EMIS and the supply system. If EFRAS is down, squadrons fall back to
EMIS's own reports, which are slower and lack forecasts: readiness reporting to the fleet slips
by a day or more, but no aircraft is grounded by an EFRAS outage.

## Program and lifecycle {#program}

- Program office: the fictional Aviation Readiness Software Program Office (ARSPO), under a
  fictional naval aviation PEO. The ARSPO product manager is the system owner.
- Acquisition pathway: software acquisition pathway (DoDI 5000.87). The program entered the
  execution phase on 2026-03-02 (fictional); its minimum viable capability release (MVCR,
  release 1.5) is ready and must be deployed to an operational environment by 2027-02-01.
- Developer: the fictional Example Readiness Software Team (ERST), a government-contractor team
  that builds on the Example Software Factory (see `architecture.md#leveraged`).
- Lifecycle state: under development. Release 1.5 runs in a pre-production environment with
  three pilot squadrons (about 140 users) using copies of real-shaped but synthetic data. The
  program seeks an ATO for the production environment before MVCR deployment; it intends to
  pursue a continuous ATO (cATO) once its automated monitoring matures, not for this decision.
- Release cadence: a minor release every three weeks through the software factory pipeline; a
  major release roughly every six months.

## Users {#users}

| User group | Count (production plan) | Access | What they do |
|---|---|---|---|
| Squadron maintenance personnel | ~2,400 | non-privileged, remote (web) | view their squadron's readiness and part forecasts |
| Maintenance officers and chiefs | ~600 | non-privileged, remote (web) | view air wing views, acknowledge forecasts, export reports |
| Fleet readiness analysts | ~40 | non-privileged, remote (web) | fleet views, ad hoc queries, export de-identified data sets |
| EFRAS application administrators | 4 | privileged in the application, remote (web) | manage roles, reference data, feature flags |
| Cloud operations engineers (ERST) | 6 | privileged in the cloud account, remote | operate the cluster, database and pipelines |
| Data scientists (ERST) | 3 | non-privileged to production; privileged in the analytics sandbox | build and retrain the forecast model |
| Senior leaders | many | none to EFRAS | receive exported briefing slides by email; never log in |

All human users sign in with their DoD Common Access Card (CAC) through the enterprise
identity broker (see `architecture.md#identity`). Cloud operations engineers reach the cloud
management console through a privileged access workstation; two break-glass console accounts
exist (see `#limitations`).

## Operating environment {#environment}

- EFRAS runs in a fictional commercial cloud region (Example GovCloud, DoD provisional
  authorization at Impact Level 4) in a program-owned cloud account, as a containerized
  application on a managed Kubernetes service with a managed PostgreSQL database and object
  storage.
- Users reach EFRAS over NIPRNet only: all traffic enters through the fictional Example
  Enterprise Cloud Access Point (ECAP), which provides boundary protection and inspection. The
  application is not reachable from the public internet.
- Boundary cyber defense (monitoring, incident response support, vulnerability alerts) is
  provided by the fictional Example Cybersecurity Service Provider (ECSSP) under a service
  agreement.
- Code, container images and infrastructure definitions are built, scanned and deployed by the
  Example Software Factory, which holds its own ATO.

## Information handled {#information}

- **Maintenance and readiness data:** maintenance actions, part removals, aircraft status by
  tail number and unit. Controlled unclassified information (CUI). Aggregated across a fleet it
  reveals readiness trends that an adversary would value; tampering could hide degraded
  readiness or trigger wasteful part orders.
- **Supply status:** part numbers, requisitions and expected delivery. CUI.
- **Maintainer PII:** name, DoD ID number, rate or rank, qualifications and work-center
  assignment of the maintainer recorded on each action (about 30,000 people). Used to show who
  holds which qualification and to join records. Disclosure enables phishing and identity
  misuse; see `privacy.md`.
- **Forecasts and reports:** derived predictions and exported reports. CUI.
- **Audit records** of users and administrators.
- No classified information. No health information.

## Availability need {#availability}

Daily readiness reporting tolerates an outage of up to 72 hours; beyond that, fleet reporting
falls back to manual EMIS reports. The program's recovery goals are a recovery time objective
of 24 hours and a recovery point objective of 24 hours (one nightly ingest).

## Known limitations {#limitations}

Items the program has already identified, with the release or date that fixes each:

1. **De-identified exports re-identifiable.** The fleet analysts' "de-identified" export and the
   data scientists' training extract replace names but keep a stable hash of the DoD ID number
   as the join key, unsalted. Anyone with a list of DoD ID numbers could re-identify records.
   Fix: salted, rotated pseudonyms in release 1.6 (planned 2027-01-15).
2. **Container base image vulnerabilities.** Two high-severity vulnerabilities in a
   third-party image-processing library inside the report-rendering container (CMP-REPORT);
   the upstream fix is released but the hardened base image that carries it is not yet
   available from the software factory. Fix: release 1.5.2 (planned 2026-12-10).
3. **No signed interconnection agreement with EMIS.** The memorandum of agreement with the EMIS
   program is drafted and under legal review; the connection runs under an interim e-mail
   approval from the EMIS ISSM. Target signature: 2026-12-31.
4. **Contingency plan not exercised.** A contingency plan is drafted; database point-in-time
   restore was tested once in pre-production, but a full regional failover of the cluster has
   never been tested. Tabletop and failover test planned for 2027-02.
5. **Break-glass console accounts without CAC.** Two cloud console break-glass accounts use a
   hardware security key (FIDO2) instead of CAC because the provider console cannot federate
   when the identity broker is down. Credentials are sealed; use is alerted. Deviation to be
   recorded and accepted, no fix planned.
6. **Audit retention short of policy.** Application and cluster audit logs are kept 90 days in
   the log store and forwarded to ECSSP, which keeps them one year; the program's own copy is
   shorter than the one-year retention the DoD component requires. Fix: archive tier in
   release 1.6.
7. **Privacy impact assessment not yet approved.** The PIA is drafted and with the component
   privacy office; the system of records notice that covers the maintainer data is an existing
   component SORN (see `privacy.md`).
