---
interview_id: INT-205
run_id: 20261118-synthetic-01
task: M-1
persona: PER-PRIV
date: 2027-02-01
topics: [privacy impact of changes, PIA review]
---
# INT-205 — M-1 — PER-PRIV

### Q1 {#INT-205.Q1}
Asked of: PER-PRIV · Task: M-1
Which of the changes in the change log alter the privacy posture, and did the PIA follow them?
**A1 {#INT-205.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#privacy]] [[INT-196.A1]] [[ASM-011]] [[ASM-025]]
> Release 1.6 does: the salted, rotated pseudonyms change how the exports and the training
> extract identify maintainers, and the archive tier keeps audit records with user identifiers
> for a year. My office reviewed the PIA against release 1.6 on 2027-01-20, after the retest, and
> the CIO approved it on 2027-01-25. On 2027-02-01 I confirmed that the approved PIA describes the
> pseudonyms and the archive tier as deployed in pre-production, so no further PIA change is
> owed for release 1.6; record that review against the change. The console security group
> change and the provider's control plane patch touched no PII and no processing purpose.

### Q2 {#INT-205.Q2}
Asked of: PER-PRIV · Task: M-1
Does anything from the November monitoring records still hold?
**A2 {#INT-205.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/monitoring/cycle-2026-11.md#privacy]] [[INT-198.A1]]
> My record of 2026-11-13 said the PIA stayed unapproved pending the export fix and that exports
> to the sandbox stop until release 1.6. Both are overtaken: the PIA is approved and release 1.6
> is in pre-production. What still holds is COND-01: no real maintainer record until the SCA
> verifies the fix in the production configuration.
