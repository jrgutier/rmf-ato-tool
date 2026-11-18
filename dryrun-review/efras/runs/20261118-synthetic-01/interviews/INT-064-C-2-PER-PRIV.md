---
interview_id: INT-064
run_id: 20261118-synthetic-01
task: C-2
persona: PER-PRIV
date: 2026-11-18
topics: [Privacy Overlay questions, privacy risk factors, privacy risk level, logs with PII]
---
# INT-064 — C-2 — PER-PRIV

### Q1 {#INT-064.Q1}
Asked of: PER-PRIV · Task: C-2
Overlay Question 1: does the system process PII other than, or in addition to, audit logs and
account management records? Question 2: does it process audit logs or account records that
capture users' activity?
**A1 {#INT-064.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-INFOTYPES]] [[product/privacy.md#pii]] [[INT-029.A2]]
> Yes to both. INF-03, the maintainer records from EMIS, is PII beyond logs and accounts, so a
> Low, Moderate or High control set applies, chosen by the privacy risk analysis. INF-05, the
> audit records, carries names and DoD ID numbers of users, so the Accountability (ACCT) set
> applies as well. EFRAS is not an NSS, but the Component directs the CNSSI 1253 Privacy Overlays
> for every system with PII, so I use the overlay's risk analysis, and its result replaces a
> PII confidentiality impact level.

### Q2 {#INT-064.Q2}
Asked of: PER-PRIV · Task: C-2
Factors 1 to 3 of the overlay's Appendix: data elements, data quality and data use. Which risk
level do you select for each?
**A2 {#INT-064.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pii]] [[INT-029.A1]] [[ART-INFOTYPES]]
> Factor 1, data elements: moderate. Name with DoD ID number, rate or rank, qualifications and
> work center can cause harm in other contexts, chiefly phishing and identity misuse; there is
> no SSN, health or financial data that would make it high. Factor 2, data quality: low. The
> records come from EMIS, the authoritative source, are validated nightly, and an error shows a
> wrong qualification in a readiness view but no decision about the person rests on them.
> Factor 3, data use: low. The PII is used for qualification coverage per work center and to
> join actions to people; no benefit, discipline or personnel decision is made from EFRAS.

### Q3 {#INT-064.Q3}
Asked of: PER-PRIV · Task: C-2
Factors 4 and 5: data analytics, and data location and accessibility.
**A3 {#INT-064.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/conops.md#users]] [[product/conops.md#environment]]
> Factor 4, data analytics: moderate. The records of 30,000 people are aggregated, analysts run ad
> hoc queries across the fleet, and a forecasting model is trained on an extract whose
> pseudonyms are an unsalted hash, so the exports can be re-identified until release 1.6.
> Factor 5, location and accessibility: moderate. The data sits on an unclassified IL4 cloud
> network reached only with CAC multifactor sign-in, which points to low, but about 3,000 users
> sign in, analysts download exports, and reports leave by e-mail, which moves it up.

### Q4 {#INT-064.Q4}
Asked of: PER-PRIV · Task: C-2
Factors 6 and 7: potential harm to the individual and to the agency. Then the overall level.
**A4 {#INT-064.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-036.A1]] [[product/privacy.md#pii]] [[ART-RA]]
> Factor 6, harm to the individual: moderate. Exposure enables targeted phishing and identity
> misuse against maintainers and could embarrass them over qualification gaps; it would not
> endanger anyone's safety. Factor 7, harm to the agency: moderate. A breach of 30,000 records
> would trigger breach response and notification under the Privacy Act and cost the fleet's
> trust in the readiness program. I add no factor. I weigh the seven equally: five moderate and
> two low give an overall privacy risk level of moderate, so the Moderate control set applies,
> with the ACCT set for the logs. The re-identifiable exports are the outlying risk and are
> already tracked as a weakness; they do not push the level to high. As the Component's senior
> official for privacy, I set that level here; I give the formal approval of the overlays and
> the categorization at the review step.
