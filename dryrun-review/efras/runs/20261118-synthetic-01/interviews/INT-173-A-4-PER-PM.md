---
interview_id: INT-173
run_id: 20261118-synthetic-01
task: A-4
persona: PER-PM
date: 2026-12-11
topics: [response to the significant findings, planned remediation, receipt of the report]
---
# INT-173 — A-4 — PER-PM

### Q1 {#INT-173.Q1}
Asked of: PER-PM · Task: A-4
You received the assessment results at the out-brief today. Do you accept the findings as the assessor wrote them?
**A1 {#INT-173.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#top]]
> Yes. I received the report and the family results at the out-brief on 2026-12-11 and I do not
> dispute any finding. Most of them are the limitations we disclosed ourselves in the CONOPS;
> the leaver timing and the container configuration findings are new to me, and I accept them.

### Q2 {#INT-173.Q2}
Asked of: PER-PM · Task: A-4 · Control focus: pt-3
What is the program's response to FND-018, the re-identifiable exports?
**A2 {#INT-173.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/privacy.md#pia]]
> Salted, rotated pseudonyms ship in release 1.6, planned for 2027-01-15. No real maintainer
> data flows before then: the pilot runs on synthetic data, and production ingest waits for the
> PIA approval. I would like the report to say that exports stay limited to the analysts and data
> scientists who need them until 1.6.

### Q3 {#INT-173.Q3}
Asked of: PER-PM · Task: A-4 · Control focus: si-2
What is the response to FND-019, FND-024, FND-007 and FND-013, the items release 1.5.2 carries?
**A3 {#INT-173.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#stig-scan]] [[INT-172.A1]]
> Release 1.5.2 is planned for 2026-12-10 and carries the two PostgreSQL settings and the new
> report container. It is waiting on the software factory's hardened base image, so it did not
> reach the assessed environment before the out-brief. I accept that the assessor could not
> verify it. The release goes out as soon as the factory delivers the image.

### Q4 {#INT-173.Q4}
Asked of: PER-PM · Task: A-4 · Control focus: cp-4
What is the response to FND-011 (failover never tested) and to the plans still unapproved (FND-010, FND-015, FND-016)?
**A4 {#INT-173.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[INT-167.A2]]
> I approve the contingency, incident response and configuration management plans by 2026-12-15,
> as the AODR's condition requires. The tabletop and the regional failover test are planned for
> 2027-02; I cannot move them earlier without taking the operations team off the 1.6 work.

### Q5 {#INT-173.Q5}
Asked of: PER-PM · Task: A-4 · Control focus: ia-2
What is the response to FND-012, the break-glass accounts?
**A5 {#INT-173.A5}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> We will not fix it: the provider console cannot federate when the identity broker is down,
> and that is the case the accounts exist for. I will put the deviation with its compensating
> measures to the AO for acceptance.
