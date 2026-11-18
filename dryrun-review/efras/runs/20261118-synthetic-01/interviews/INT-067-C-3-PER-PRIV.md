---
interview_id: INT-067
run_id: 20261118-synthetic-01
task: C-3
persona: PER-PRIV
date: 2026-11-18
topics: [PII determination, Privacy Overlays approval, logs with PII, categorization approval for a PII system]
---
# INT-067 — C-3 — PER-PRIV

### Q1 {#INT-067.Q1}
Asked of: PER-PRIV · Task: C-3
Do you approve the determination that the system processes PII?
**A1 {#INT-067.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[ART-INFOTYPES]] [[product/privacy.md#pii]]
> Yes. It processes PII: the maintainer records of INF-03, including the pseudonymized exports
> and training extract, which stay PII until the pseudonyms are salted, and the users' names and
> DoD ID numbers in the INF-05 audit records. I approve that determination as the Component's
> senior official for privacy, in my own name, not through a designee.

### Q2 {#INT-067.Q2}
Asked of: PER-PRIV · Task: C-3
Does any log include PII, and do you approve the Privacy Overlays selected: the Moderate set
and the Accountability set?
**A2 {#INT-067.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-064.A1]] [[INT-064.A4]] [[product/architecture.md#logging]]
> Yes, the logs include PII: sign-in, role change and export events record the user's name and
> DoD ID number, and the database audit extension records who read which records. That is why
> the Accountability set applies. I approve both control sets: the Moderate set from the risk
> analysis I made at C-2, five factors moderate and two low, and the Accountability set for the
> logs.

### Q3 {#INT-067.Q3}
Asked of: PER-PRIV · Task: C-3
Do you approve the security categorization shown in ART-CAT for this PII system?
**A3 {#INT-067.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-061.A2]]
> I approve it, today, before the AODR's review. Confidentiality and integrity at moderate cover
> the maintainer records. Availability low is acceptable to me: the owner lowered it for INF-03
> because EFRAS is not the authoritative copy, not to save controls, and no individual is harmed
> if our copy is unavailable. My approval does not approve the PIA, which is still with my office
> and must be approved before production deployment.
