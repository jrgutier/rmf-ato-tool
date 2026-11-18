---
interview_id: INT-029
run_id: 20261118-synthetic-01
task: P-12
persona: PER-PRIV
date: 2026-11-18
topics: [PII determination, subjects, SORN, records, PIA determination, audit records]
---
# INT-029 — P-12 — PER-PRIV

### Q1 {#INT-029.Q1}
Asked of: PER-PRIV · Task: P-12
**A1 {#INT-029.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pii]] [[INT-027.A3]]
> EFRAS processes PII. The maintainer type holds name, DoD ID number, rate or rank,
> qualifications and work-center assignment about federal personnel. The DoD ID number identifies
> on its own; rate or rank, work center and qualifications identify a person in combination,
> especially in a small work center, so the "de-identified" exports that keep an unsalted hash of
> the DoD ID number are still PII. No SSNs, no PHI. We found the PII by walking the EMIS extract
> layout with the program and the draft PIA, field by field.

### Q2 {#INT-029.Q2}
Asked of: PER-PRIV · Task: P-12
**A2 {#INT-029.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/architecture.md#logging]]
> The audit records hold PII too: the identity broker's assertion carries each user's DoD ID
> number, and sign-in, role-change and export events record it with the user's name. That is
> PII about federal personnel and the ERST contractors who administer the system. I want it
> accounted for now, because it decides whether the accountability overlay applies at C-3.

### Q3 {#INT-029.Q3}
Asked of: PER-PRIV · Task: P-12
**A3 {#INT-029.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#authority]]
> The maintainer records are covered by the existing Component SORN for aviation maintenance
> records (fictional), published; my office confirmed coverage by e-mail on 2026-08-19. The
> audit records of users fall under the Component's existing SORN for computer access and
> security records (fictional). EFRAS is government-run with contractor developers; the
> contractor does not operate the system of records. No Privacy Act statement is needed because
> nothing is collected from individuals.

### Q4 {#INT-029.Q4}
Asked of: PER-PRIV · Task: P-12
**A4 {#INT-029.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pia]] [[product/privacy.md#minimization]]
> A PIA is required: EFRAS is a new DoD information system that holds PII about federal
> personnel in electronic form, and being a national security system does not exclude it,
> because the Component applies the privacy controls. It must be approved before production
> deployment of release 1.5 (MVCR), so no later than 2027-02-01. Handling must comply with DoD
> 5400.11-R and DoDI 5400.16, and records with DoDI 5015.02. The Component records management
> office has coordinated: maintainer data follows the aviation maintenance records schedule
> (fictional, 5-year analysis window, matching the monthly purge), audit records the general
> records schedule for system access records.
