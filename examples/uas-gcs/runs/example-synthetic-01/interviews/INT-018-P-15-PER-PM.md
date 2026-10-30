---
interview_id: INT-018
run_id: example-synthetic-01
task: P-15
persona: PER-PM
date: 2026-10-29
topics: [requirement sources, security and privacy requirements, operational constraints]
---
# INT-018 — P-15 — PER-PM

### Q1 {#INT-018.Q1}
Asked of: PER-PM · Task: P-15
**A1 {#INT-018.A1}** respondent: simulated · tag: SIMULATED · basis: [[ASM-008]] [[ART-RA]] [[ART-INFOTYPES]] [[ART-STAKE]]
> We have no capability document in the package, so the requirements come from DoDI 8510.01 and
> the CNSSI 1253 baseline the categorization will select, the system risk assessment, the
> information types and the privacy determination, and what the stakeholders told us.

### Q2 {#INT-018.Q2}
Asked of: PER-PM · Task: P-15
**A2 {#INT-018.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]] [[product/conops.md#limitations]]
> The must-haves, in order: every privileged action tied to a person, including maintenance
> offline; the aircraft link encrypted and commands authenticated; flaws in any component,
> GDT firmware included, fixed in the quarterly bundle or sooner for critical ones; only signed
> bundles and checked media installed; a STIG or assessed hardening for every component; audit
> from every component reaching the enclave when connected; PII in account and audit data
> limited to what operations need; mission data protected at rest; and a replacement station
> working within 4 hours.

### Q3 {#INT-018.Q3}
Asked of: PER-PM · Task: P-15
**A3 {#INT-018.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#environment]] [[product/conops.md#availability]] [[product/conops.md#users]]
> The constraints: stations go disconnected for days, so nothing that blocks flight may depend
> on the uplink; CAC sign-in must keep working offline; field maintainers work without network
> access; the kit runs on vehicle or generator power; and a spare kit has to be up in 4 hours.
