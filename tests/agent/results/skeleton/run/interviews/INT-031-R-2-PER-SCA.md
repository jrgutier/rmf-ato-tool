---
interview_id: INT-031
run_id: agent-skeleton
task: R-2
persona: PER-SCA
date: 2026-10-29
topics: [finding exploitability, compensating factors, evidence confidence]
---
# INT-031 — R-2 — PER-SCA

### Q1 {#INT-031.Q1}
Asked of: PER-SCA · Task: R-2 · Control focus: ac-2
**A1 {#INT-031.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[product/conops.md#limitations]] [[product/architecture.md#physical]]
> FND-001 and FND-003 are one weakness seen from two controls: the shared fieldtech account on
> the maintenance port, also open as STG-004. Exploiting it needs someone who knows the shared
> password and stands at a unit, so it is an insider or contractor action, not a remote one.
> What we observed is that the audit trail names only the account, so a misuse would be
> detected as an event but could not be pinned on a person. The site-visit log the program
> started is an interim record outside the audit trail; I have not assessed it yet.

### Q2 {#INT-031.Q2}
Asked of: PER-SCA · Task: R-2 · Control focus: ac-2
**A2 {#INT-031.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[product/architecture.md#physical]]
> FND-002 is narrower: a technician who leaves the group keeps a working password for up to
> 90 days. To use it they still need physical access to a fenced remote shelter, and the
> sign-in would show in the SIEM. I found no evidence it has happened, and no record of an
> out-of-cycle change either, so I cannot say it has not.

### Q3 {#INT-031.Q3}
Asked of: PER-SCA · Task: R-2 · Control focus: si-2
**A3 {#INT-031.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[ART-STIG]] [[product/test-results.md#vuln-scan]] [[product/architecture.md#network]]
> FND-004 is the most serious finding. At the 2026-09-30 scan two units ran a 63-day-old
> bundle with 4 high and 9 medium vulnerabilities, and STG-001 is open; any unit can drift to
> about 90 days. The compensating factors I observed are the enclave firewall, the
> deny-by-default host firewall that allows only the registered flows, and CSSP monitoring.
> They reduce who can reach a unit; they do not remove the vulnerabilities. An attacker
> already on the installation network who can reach a registered port is the realistic path.

### Q4 {#INT-031.Q4}
Asked of: PER-SCA · Task: R-2 · Control focus: all findings
**A4 {#INT-031.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]] [[ART-SAP]]
> Confidence is high for all four findings: each rests on records plus a team test or a
> credentialed scan, and the program disclosed the same gaps itself. The team tests ran on two
> pre-production units, not fielded ones, so for si-2 I rely on the program's fielded scan,
> which I examined. Nothing in evidence shows any of the findings fixed today.
