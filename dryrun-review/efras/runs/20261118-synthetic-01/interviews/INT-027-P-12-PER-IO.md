---
interview_id: INT-027
run_id: 20261118-synthetic-01
task: P-12
persona: PER-IO
date: 2026-11-18
topics: [maintenance and readiness data, maintainer PII, forecasts and reports, provisional impact levels]
---
# INT-027 — P-12 — PER-IO

Respondent: the fleet maintenance data steward (information owner of the maintenance and
readiness data, the maintainer personal data and the forecasts and reports derived from them).

### Q1 {#INT-027.Q1}
Asked of: PER-IO · Task: P-12
**A1 {#INT-027.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[INT-022.A1]]
> My types are three: the maintenance and readiness data (maintenance actions, part removals,
> aircraft status by tail number and unit), the maintainer personal data that comes with each
> action, and the forecasts and reports derived from both. All three are CUI and unclassified.
> None of it is controlled technical information: it is operational maintenance history, not
> technical data about the aircraft's design. EFRAS holds no source code or design data of
> military application.

### Q2 {#INT-027.Q2}
Asked of: PER-IO · Task: P-12
**A2 {#INT-027.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[product/conops.md#mission]]
> For the maintenance and readiness data I start from the SP 800-60 facilities, fleet and
> equipment management type, low across the board, and I raise it. Confidentiality moderate:
> aggregated across a fleet the data reveals readiness trends an adversary would value, which is
> serious, not limited, harm. Integrity moderate: tampering could hide degraded readiness or set
> off wasteful part orders, and integrity is my first concern. Availability stays low: EFRAS is
> decision support, EMIS keeps the source records, and squadrons fall back to EMIS reports.

### Q3 {#INT-027.Q3}
Asked of: PER-IO · Task: P-12
**A3 {#INT-027.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pii]] [[product/conops.md#information]]
> The maintainer personal data is name, DoD ID number, rate or rank, qualifications and
> work-center assignment for about 30,000 maintainers, uniformed and civilian, all federal
> personnel; contractor maintainers do not record actions in EMIS. No Social Security numbers and
> no health information. The provisional values of the personal identity and authentication type
> are moderate for all three; I confirm moderate confidentiality and integrity, because
> disclosure enables phishing and identity misuse and a wrong qualification record misleads the
> work centers. I lower availability to low: EFRAS is not the authoritative copy, EMIS is, and
> losing EFRAS's copy for days harms no one.

### Q4 {#INT-027.Q4}
Asked of: PER-IO · Task: P-12
**A4 {#INT-027.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[product/privacy.md#minimization]]
> The forecasts and reports I treat like logistics management information, low provisionally,
> and I raise confidentiality and integrity to moderate for the same aggregation and tampering
> reasons as the source data; availability low. The de-identified exports and the training
> extract are still maintainer personal data until they are truly de-identified, so they belong
> with the personal data type, not with the reports.
