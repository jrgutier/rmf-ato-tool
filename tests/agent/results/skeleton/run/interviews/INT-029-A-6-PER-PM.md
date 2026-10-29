---
interview_id: INT-029
run_id: agent-skeleton
task: A-6
persona: PER-PM
date: 2026-10-29
topics: [remediation plan for FND-004, remediation plan for FND-001 FND-002 FND-003, resources and dates]
---
# INT-029 — A-6 — PER-PM

### Q1 {#INT-029.Q1}
Asked of: PER-PM · Task: A-6 · Control focus: si-2 (FND-004)
**A1 {#INT-029.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[product/conops.md#limitations]] [[product/test-results.md#vuln-scan]]
> FND-004 is real and I own it. Two things. First, the two overdue units, esg-north-01 and
> esg-ridge-01: I am funding an unscheduled site visit for each out of the current field
> support contract with ESIT; both will get the current bundle by 2026-11-20, inside 30 days of
> today, and the ISSO will rescan them the same week. Second, the root cause: remote update over
> the uplink is in release 2.2, planned for 2026-12. That is a new flow on the installation
> network, so before we turn it on we need the enclave provider's rule change and the AO's
> agreement, since the AO said any new flow comes back to them. I plan the request in mid
> November so approval lands with the release, and remote update on all 12 units by the end of
> January 2027. Until then the quarterly visits continue and any unit past 30 days gets its own
> POA&M line.

### Q2 {#INT-029.Q2}
Asked of: PER-PM · Task: A-6 · Control focus: ac-2, ia-2 (FND-001, FND-002, FND-003)
**A2 {#INT-029.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[product/conops.md#limitations]]
> The shared fieldtech account is the one root cause behind FND-001, FND-002 and FND-003.
> The fix is per-technician local accounts with smart-card login that works without the
> identity service, in release 2.3, planned for 2027-03. It is funded in the current ESIT
> development task order; I cannot bring it earlier without dropping release 2.2, and remote
> update is the higher risk, so I will not trade it. Fielding 2.3 to the 12 units is done
> remotely once 2.2 is in, so I commit to end of March 2027 for all three. In the meantime
> the field team starts a site-visit log naming the technician for each maintenance session
> from 2026-11-15, and the ISSO reconciles it with the audit records monthly.

### Q3 {#INT-029.Q3}
Asked of: PER-PM · Task: A-6 · Control focus: ac-2 (FND-002)
**A3 {#INT-029.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[product/conops.md#limitations]]
> The out-of-cycle password change costs nothing but discipline. From now on the ISSO changes
> the fieldtech password whenever a technician leaves the team and records the change; I
> want that written into the ISSO's procedures by the end of November. The account itself goes
> away with release 2.3.
