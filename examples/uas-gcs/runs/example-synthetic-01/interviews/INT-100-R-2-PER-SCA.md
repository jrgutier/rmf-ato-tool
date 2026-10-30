---
interview_id: INT-100
run_id: example-synthetic-01
task: R-2
persona: PER-SCA
date: 2026-10-29
topics: [finding context, exploitability, compensating factors, evidence confidence]
---
# INT-100 — R-2 — PER-SCA

### Q1 {#INT-100.Q1}
Asked of: PER-SCA · Task: R-2 · Control focus: FND-001, FND-003, FND-004, FND-006, FND-009, FND-019, FND-020, FND-027 to FND-035, FND-043, FND-047, FND-048, FND-060, STG-001, STG-002
How exploitable are the shared-account findings, and what limits them?

**A1 {#INT-100.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]]
> One shared `gcsmaint` credential works on every workstation and router, and the GDT
> administrator password has never changed. Anyone who learns them gets privileged access
> without leaving an attributable trace; STG-001 and STG-002 are the same weakness seen by the
> STIG check. What limits it: the accounts are reachable only from the station segment or the
> console, the kit is in the operators' custody, and disks are encrypted. I am highly confident
> in this evidence: I saw the accounts and the password age myself.

### Q2 {#INT-100.Q2}
Asked of: PER-SCA · Task: R-2 · Control focus: FND-054, FND-062, FND-063, FND-021, FND-059, FND-061, FND-068, STG-003 to STG-005
And the known vulnerabilities and the untested mission planner?

**A2 {#INT-100.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]]
> The GDT management web service crash is reproducible from the station segment but not from
> the uplink, which I confirmed. Firmware 5.2.1 fixes it and is still in regression testing.
> The planner library flaws have no vendor fix. The planner's hardening, documentation and
> input validation were never independently tested, and STG-003 to STG-005 were not reviewed, so
> my confidence in the planner's configuration is low: I cannot say it is weak, only that
> nobody has shown it is sound. Planner input arrives only through signed bundles and
> removable media.

### Q3 {#INT-100.Q3}
Asked of: PER-SCA · Task: R-2 · Control focus: log forwarding, plans, continuous monitoring, privacy, ca-3, end of support
What about the remaining groups of findings?

**A3 {#INT-100.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-SAR]]
> Logs from the planner and the GDT stay on the devices and station logs are not reviewed while
> disconnected, so an intrusion could go unseen for days. The contingency, incident response and
> configuration management plans are drafts, never tested, and nobody is trained. Continuous
> monitoring has not started, which is expected before a decision. The privacy findings are
> approvals pending, not missing protections. The IC-1 agreement is technically in place but
> unsigned. The planner's end of support in 2027-06 is the one gap that grows with time.
