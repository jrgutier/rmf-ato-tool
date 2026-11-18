---
interview_id: INT-160
run_id: 20261118-synthetic-01
task: A-3
persona: PER-ISSE
date: 2026-11-23
topics: [baseline templates and drift, change records, configuration settings and scan, inventory review]
---
# INT-160 — A-3 — PER-ISSE

### Q1 {#INT-160.Q1}
Asked of: PER-ISSE · Task: A-3 · Control focus: cm-2, cm-3
Show me the baseline templates and release manifests, the drift scan reports, and the change records from release 1.5.0 to 1.5.1, including any emergency change.
**A1 {#INT-160.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/test-results.md#pipeline-1-5]]
> The templates and the 1.5.0 and 1.5.1 manifests of image digests are in the repository with
> their merge history; both releases updated them. The hourly drift scan reported nothing for
> the last 90 days except one manual node label change on 2026-09-03, reverted the same day with
> a ticket. Between 1.5.0 and 1.5.1 there were 23 merged pull requests, each with a second
> reviewer, a security and privacy impact note, green pipeline gates and my or the ISSO's
> sign-off; there was no emergency change. The configuration control board's monthly minutes
> for 2026-09 to 2026-11 record the 1.5.1 approval and the plan update. Records are kept in the
> repository and the pipeline with no deletion rule.

### Q2 {#INT-160.Q2}
Asked of: PER-ISSE · Task: A-3 · Control focus: cm-6
What did today's authenticated scan of release 1.5.1 show against the 2026-10-22 scan, and which settings are documented for the application containers?
**A2 {#INT-160.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#stig-scan]] [[ART-STIG]]
> Release 1.5.1 changed no node or database setting, and today's scan matches 2026-10-22: the
> nodes at 94% with only the provider-managed control plane checks open, the database with the
> same six items, the four engine settings the managed service does not expose and the two we
> fix in 1.5.2, connection logging verbosity and the break-glass role's password complexity. No
> CAT I item. For the five application containers we have the factory's base image standard and
> our build files; there is no documented secure configuration for them against the Application
> Security and Development STIG.

### Q3 {#INT-160.Q3}
Asked of: PER-ISSE · Task: A-3 · Control focus: cm-8
Show me the inventory and the record of its review at each release.
**A3 {#INT-160.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[ART-INV]]
> The inventory is the INV list; the ISSO and I review it monthly, and the review of 2026-11-02
> is on file. It still shows the five containers at 1.5.0: production has no release yet, and we
> did not update or review it when 1.5.1 went to pre-production on 2026-11-07. Everything
> deployed is in it, nothing is counted twice and nothing belongs to another system.
