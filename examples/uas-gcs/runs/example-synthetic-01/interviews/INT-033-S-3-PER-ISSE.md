---
interview_id: INT-033
run_id: example-synthetic-01
task: S-3
persona: PER-ISSE
date: 2026-10-29
topics: [component capabilities per family, allocation to components]
---
# INT-033 — S-3 — PER-ISSE

### Q1 {#INT-033.Q1}
Asked of: PER-ISSE · Task: S-3
Context: per family, which components provide access control, identification, audit and
configuration capabilities.
**A1 {#INT-033.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-BND]] [[ART-REQ]] [[INT-020.A1]]
> Accounts, sign-in, least privilege, session controls and audit generation live in the
> workstation operating system; the station router and the GDT management service have their own
> local accounts and logs, so the account, access and audit-event controls go to those three.
> The flight control application writes its own command log, so audit content and
> non-repudiation also go to it. Audit storage, review tools and time stamps are the operating
> system's (the router keeps time too). Baseline configuration, settings, least functionality and
> inventory apply to every station component: hardware, OS, the three applications, the GDT and
> the router. Remote access and the external interface are the router's.

### Q2 {#INT-033.Q2}
Asked of: PER-ISSE · Task: S-3
**A2 {#INT-033.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-BND]] [[ART-REQ]]
> The aircraft link, its encryption and command authentication are the GDT and the air vehicle
> endpoint (REQ-02); the router carries the enclave link. Cryptographic key handling sits in the
> OS, the GDT and the air vehicle endpoint. Software and firmware integrity, signed bundles and
> flaw remediation touch the OS and the GDT firmware, and flaw remediation reaches every
> component through the integrator bundle (REQ-03, REQ-04). Denial-of-service protection is the
> router's and the GDT's.

### Q3 {#INT-033.Q3}
Asked of: PER-ISSE · Task: S-3
**A3 {#INT-033.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-BND]] [[ART-REQ]]
> Data at rest is the laptop's full-disk encryption with the OS (REQ-08). Ports and attached
> devices are the laptop hardware. Backups are taken by the OS onto the laptop's removable drive.
> Input validation and error handling belong to the flight control, mission planner and video
> applications.

### Q4 {#INT-033.Q4}
Asked of: PER-ISSE · Task: S-3
**A4 {#INT-033.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[ART-BND]]
> Training, personnel, physical, planning, assessment, maintenance procedure, media handling,
> incident response, contingency planning, risk assessment, acquisition, supply chain and the
> privacy processing controls have no single component home: allocate them to the system as a
> whole. Spare kits are environment of operation (REQ-10).
