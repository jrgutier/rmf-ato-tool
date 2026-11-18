---
interview_id: INT-180
run_id: 20261118-synthetic-01
task: A-6
persona: PER-PM
date: 2026-12-14
topics: [fix and release per weakness, resources, dates, interim mitigations, completion before or after authorization]
---
# INT-180 — A-6 — PER-PM

### Q1 {#INT-180.Q1}
Asked of: PER-PM · Task: A-6 · Control focus: si-2
Release 1.5.2 was planned for 2026-12-10 and has not shipped. What is its date now?
**A1 {#INT-180.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[INT-178.A1]] [[INT-182.A1]]
> The 2026-12-10 date stands in the POA&M as the original; it slipped because the factory's
> hardened base image is late, and the factory gives no date. My new date is 2027-01-15 at the
> latest: if the image comes earlier, 1.5.2 ships within days; if not, the two PostgreSQL settings
> and the rebuilt report container ride with release 1.6 on 2027-01-15. The ERST contract and
> the operations team cover it; no new money is needed. Interim: the report renderer has no
> outbound access and only signed-in users reach it.

### Q2 {#INT-180.Q2}
Asked of: PER-PM · Task: A-6 · Control focus: pt-3
What does release 1.6 carry, and is its work started?
**A2 {#INT-180.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[INT-173.A2]]
> Salted, rotated pseudonyms for the exports and the training extract, and the audit archive
> tier. ERST is building both now for 2027-01-15 under the current contract. I have asked the SCA
> team's privacy-trained assessor to retest re-identification on 2027-01-20, ahead of the privacy
> office's PIA review that day. Until then exports stay limited to the analysts and data scientists
> who need them, and only synthetic data is loaded.

### Q3 {#INT-180.Q3}
Asked of: PER-PM · Task: A-6 · Control focus: cm-6
Who documents the container configuration (FND-008), and when?
**A3 {#INT-180.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-161.A1]] [[ASM-021]]
> ERST's developer lead completes the Application Security and Development STIG checklist for
> the five containers by 2027-01-08, and the documented baseline and the pipeline check go in
> with release 1.6 on 2027-01-15, after the change board approves them. It is inside the current
> contract.

### Q4 {#INT-180.Q4}
Asked of: PER-PM · Task: A-6 · Control focus: cp-4
What are the dates for the contingency and incident items?
**A4 {#INT-180.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[INT-173.A4]]
> I approve the contingency, incident response and configuration management plans on 2026-12-15
> and the ISSM distributes them by 2026-12-18. The combined incident and contingency tabletop is
> on 2027-02-12 and the regional failover test on 2027-02-26, with the after-action report by
> 2027-03-01. The failover test needs a weekend with the operations team and the provider
> notified; it is funded in the sustainment line.

### Q5 {#INT-180.Q5}
Asked of: PER-PM · Task: A-6
Which items should be complete before the authorization decision, and which may follow it?
**A5 {#INT-180.A5}** respondent: simulated · tag: SIMULATED · basis: [[INT-176.A2]] [[product/conops.md#limitations]]
> Before: everything that touches real maintainer data or the release we field, so the PII
> exports, the PIA, the release 1.5.2 fixes, the leaver step, the container baseline, the EMIS
> agreement, the plan approvals, the retests and REQ-11 and REQ-12, and the AO's decision on the
> break-glass deviation. All of them are dated by 2027-01-25, ahead of the decision I need before
> the 2027-02-01 deployment. After: the failover and tabletop in 2027-02, the archive tier's
> replacement of the CSSP copy, the inventory procedure, and the monitoring items that can only
> start after the decision.
