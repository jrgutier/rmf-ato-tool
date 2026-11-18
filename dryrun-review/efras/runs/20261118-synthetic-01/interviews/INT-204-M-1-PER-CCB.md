---
interview_id: INT-204
run_id: 20261118-synthetic-01
task: M-1
persona: PER-CCB
date: 2027-02-01
topics: [board decisions since the last review, release 1.6, security impact analyses]
---
# INT-204 — M-1 — PER-CCB

### Q1 {#INT-204.Q1}
Asked of: PER-CCB · Task: M-1
Which changes did the board decide since the last review, and was a security impact analysis done for each?
**A1 {#INT-204.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-193.A1]] [[INT-194.A1]] [[ASM-025]] [[ART-POAM]]
> One release: 1.6. The PM raised it at the board on 2026-12-16 as the remediation release for
> the POA&M (salted rotated pseudonyms, the log archive tier, the PostgreSQL logging and
> password settings, the container baseline check and the sandbox egress probe). The ISSE's
> security impact analysis rated it significant because it changes privacy safeguards, which
> the strategy's EV-02 names. The gates and the developmental test event ran up to 2027-01-15;
> the results, with the analysis, went to the board and to the AODR. We approved it on
> 2027-01-15, told the PM, the ISSO, the ISSM and the AODR, and it went to pre-production that day
> without the rebuilt report container. These dates follow the R-3 progress rule (ASM-025); the
> board minutes are not in the product material.

### Q2 {#INT-204.Q2}
Asked of: PER-CCB · Task: M-1
Is release 1.6 closed?
**A2 {#INT-204.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-193.A1]] [[INT-198.A1]]
> No. A change request closes when the change is confirmed deployed without issues. Release 1.6
> is in pre-production only, and the AO's conditions want the SCA to verify the privacy and
> configuration fixes (COND-01, COND-05). It stays open until the production deployment and the
> SCA's verification.

### Q3 {#INT-204.Q3}
Asked of: PER-CCB · Task: M-1
Did the board review the 2026-11-04 console change?
**A3 {#INT-204.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-203.A1]] [[ART-CMP]]
> It was reverted within the hour, so there was nothing to approve after the fact. The record
> handed to me is the ISSO's summary; I have no board minute for it. The root cause belongs in
> the change log and the response in the risk response.
