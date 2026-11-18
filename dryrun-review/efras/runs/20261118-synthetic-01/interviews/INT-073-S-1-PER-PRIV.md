---
interview_id: INT-073
run_id: 20261118-synthetic-01
task: S-1
persona: PER-PRIV
date: 2026-11-18
topics: [NSS privacy control baseline for a non-NSS PII system, Privacy Overlay control set, privacy requirements not covered]
---
# INT-073 — S-1 — PER-PRIV

### Q1 {#INT-073.Q1}
Asked of: PER-PRIV · Task: S-1
EFRAS is not an NSS but is categorized under CNSSI 1253. Do you agree that its baseline includes the NSS privacy control baseline?
**A1 {#INT-073.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-070.A2]] [[ART-CAT]] [[ART-ORG-CONTEXT]]
> I agree, and I want it recorded as my position, not as a side effect of the P-4 wording. The
> privacy control baseline is how CNSSI 1253 manages organizational PII risk, and the Component
> uses CNSSI 1253 for all its systems. A system holding maintainer PII that drops it because of
> its NSS status would have fewer privacy controls than an NSS holding the same data. Keep it.

### Q2 {#INT-073.Q2}
Asked of: PER-PRIV · Task: S-1
Which privacy controls in the selected set come from the privacy baseline or the Privacy Overlays, and which privacy requirements does the set leave uncovered?
**A2 {#INT-073.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[product/privacy.md#pia]] [[product/conops.md#limitations]]
> In your 50, the Moderate and Accountability sets bring PT-2, PT-3 and RA-8, and select AC-2,
> AC-3, AC-6, AC-17, AU-6, the configuration, contingency, identification, media, personnel and
> encryption controls with privacy justifications. PM-5 is the one control only the privacy
> baseline brings in. Uncovered: REQ-14's de-identification has no control of its own in your
> set; PT-2, PT-3 and SI-12 carry minimization and the five-year purge, and RA-8 carries the PIA
> of REQ-16. REQ-15's Privacy Act rules sit in PT-2 and PT-3 and the contract. I will take the
> tailoring of privacy controls with the ISSM at S-2.
