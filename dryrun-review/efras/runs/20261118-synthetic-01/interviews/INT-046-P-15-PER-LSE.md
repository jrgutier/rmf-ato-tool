---
interview_id: INT-046
run_id: 20261118-synthetic-01
task: P-15
persona: PER-LSE
date: 2026-11-18
topics: [requirements derivation, key performance parameters, engineering practices, assurance level]
---
# INT-046 — P-15 — PER-LSE

Respondent: ERST technical lead, acting as lead systems engineer for the program.

### Q1 {#INT-046.Q1}
Asked of: PER-LSE · Task: P-15
How were the security requirements derived, and from what documents?
**A1 {#INT-046.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#top]] [[product/architecture.md#components]] [[product/data-flows.md#main]]
> We used four documents: the capability needs statement v1.0, the EFRAS concept of operations,
> and two sections of it that serve as our operational mode summary and mission profiles. Those
> two are the nightly ingest and daily reporting cycle in the mission section, and the three
> user journeys (squadron view, air wing view, analyst export). There are no separate OMS/MP
> documents on the software pathway. We used three methods.
> - Threat modeling of the architecture and data flows, covering design, interfaces and access
>   points.
> - Misuse cases on the API and the export function, covering implementation and access points.
> - The PPP criticality analysis of the readiness data processing function, covering design and
>   implementation.
> Nothing is planned for foreign release, so we derived no exportability requirement.

### Q2 {#INT-046.Q2}
Asked of: PER-LSE · Task: P-15
Which key performance parameters or attributes set the survivability, sustainment and security
measures, and where do the requirements land?
**A2 {#INT-046.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#availability]]
> The capability needs statement has two key attributes. Availability is recovery within 24 hours
> with at most one nightly load lost, which sets survivability and sustainment. Data protection
> is integrity-checked loads plus encryption in transit and at rest with program keys, which sets
> security and rests on confidentiality and integrity. Requirements the system must perform go
> into the performance specification, which is the release acceptance criteria in the backlog.
> Recovery, audit retention and patching also go into the product support needs.

### Q3 {#INT-046.Q3}
Asked of: PER-LSE · Task: P-15
Which system security engineering practices does the program use, and to what level of assurance?
**A3 {#INT-046.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pipeline-1-5]] [[product/architecture.md#configuration]]
> - Cybersecurity: threat modeling at design; SAST, dependency and image scans and DAST in the
>   pipeline at test; signed, SBOM-tagged image builds as our manufacture; monthly node rolls and
>   patching in sustainment.
> - Cyber resilience: three-tier segmentation and a database standby at design; restore tests;
>   immutable images rebuilt from source; backup and point-in-time restore in sustainment.
> - Cyber survivability: ECAP-only ingress and an egress allow-list at design; the developmental
>   test event and penetration test; reproducible builds; CSSP monitoring in sustainment.
> - Program protection: the PPP countermeasures CM-001 and CM-002.
> - Privacy engineering: pseudonymization and minimization of exports, in design, test and
>   sustainment.
> The principles we apply are least privilege, defense in depth, domain separation, protective
> defaults and protective recovery. The level of assurance is moderate, as the software
> factory's gates give it: automated evidence on each release, not formal methods. That fits a
> mature cloud stack, a software pathway program, a moderate-impact system and a decision-support
> mission with a 72-hour tolerance. REQ-07 and REQ-13 carry it.
