---
interview_id: INT-127
run_id: 20261118-synthetic-01
task: S-4
persona: PER-PRIV
date: 2026-11-18
topics: [privacy plan, privacy control assessment methods, PII breach reporting]
---
# INT-127 — S-4 — PER-PRIV

### Q1 {#INT-127.Q1}
Asked of: PER-PRIV · Task: S-4 · Control focus: pl-2, pt-2, pt-3, ra-8 (privacy plan)
Which privacy requirements does the privacy plan meet, and how will the privacy controls be assessed?
**A1 {#INT-127.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-106.A1]] [[INT-109.A1]] [[product/privacy.md#authority]] [[product/privacy.md#pia]] [[product/privacy.md#minimization]]
> Keep it with the security plan: the privacy plan is the part of ART-SSP that covers the
> Privacy Act and DoDI 5400.11 duties for the maintainer PII: collection only under the
> existing Component SORN and only its five data elements, notice through the SORN and the
> sign-in banner, use limited to the purposes in the SORN, the PIA (draft 0.9, approval due
> before production data), retention and disposal per the records schedule with the monthly
> purge, the de-identification of exports (fixed in release 1.6), breach response through
> our office, and the privacy controls the Privacy Overlay adds. Assessment: the SCA examines
> the SORN, the PIA and the data map, tests the ingest field filter and the purge job, and
> tests re-identification of a sample export; we count PII elements outside the SORN found in
> the database (target zero), purge runs completed on time, exports re-identifiable in the
> sample (target zero after 1.6), and breach reports made within one hour. I review and
> approve the privacy plan before the AO sees it.

### Q2 {#INT-127.Q2}
Asked of: PER-PRIV · Task: S-4 · Control focus: ir-6 (PII breach)
How is a PII breach reported?
**A2 {#INT-127.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-099.A2]] [[INT-106.A1]]
> The ISSO tells us within one hour of a suspected or confirmed breach. We report under DoD
> 5400.11-R and the Component breach procedure to the Component senior official for privacy
> and, as required, to the DoD Privacy and Civil Liberties office; we decide on notice to the
> affected maintainers and coordinate any public statement with public affairs.
