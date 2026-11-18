---
interview_id: INT-193
run_id: 20261118-synthetic-01
task: R-3
persona: PER-PM
date: 2027-01-25
topics: [POA&M progress at the decision, slipped milestones, operator notice of residual risk, acquisition decisions]
---
# INT-193 — R-3 — PER-PM

### Q1 {#INT-193.Q1}
Asked of: PER-PM · Task: R-3
Where does each before-authorization POA&M item stand today, the day the AO decides?
**A1 {#INT-193.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-180.A1]] [[INT-180.A2]] [[INT-180.A3]] [[INT-180.A4]] [[ASM-025]]
> On plan, except two. I approved the contingency, incident response and configuration
> management plans on 2026-12-15 and the ISSM distributed them by 2026-12-18. Release 1.6 went to
> pre-production on 2027-01-15 with the salted pseudonyms, the archive tier, the documented
> container baseline and its pipeline check, and the two PostgreSQL settings; the privacy-trained
> assessor's re-identification retest on 2027-01-20 failed to re-identify anyone; the privacy
> office reviewed the PIA that day and the CIO approved it today. The two slips: the factory still
> has not published the hardened base image, so the report container is not rebuilt and its two
> highs remain; I have now requested the factory's patched intermediate image and set
> 2027-02-15. And EMIS legal has not finished its review of the memorandum, so it is unsigned; new
> date 2027-02-26, recording by 2027-03-05. The SCA has not yet verified any of the fixes, so I
> keep every item open until the first ongoing assessment closes the findings.

### Q2 {#INT-193.Q2}
Asked of: PER-PM · Task: R-3
How are the operators told of the risks that are not fully mitigated, and is there an acquisition decision that bears on them?
**A2 {#INT-193.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-192.A2]] [[product/conops.md#program]] [[product/stakeholders.md#roles]]
> The squadron maintenance officers and the information owner get a one-page notice with the
> decision: the report container is unpatched until 2027-02-15, the EMIS feed of real records
> waits for the signed agreement, and recovery from a regional outage is untested until the
> February tabletop and failover test. The decision authority's MVCR determination only fixes the
> 2027-02-01 deployment; it accepts no security risk, which is the AO's.
