---
interview_id: INT-066
run_id: example-synthetic-01
task: A-2
persona: PER-SCA
date: 2026-10-29
topics: [assessment approach, methods, reuse of test results, schedule, rules of engagement]
---
# INT-066 — A-2 — PER-SCA

### Q1 {#INT-066.Q1}
Asked of: PER-SCA · Task: A-2 · Control focus: ca-2
What is in scope and how will you assess it?

**A1 {#INT-066.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-SSP]] [[INT-065.A3]]
> The whole tailored baseline, with no exclusions. Every control is examined against its SSP
> statement and the plans it cites. Controls with a technical mechanism (ac, au, cm, ia, sc,
> si) are also tested on at least two of the six stations, and on every station for account
> and configuration settings. Process controls get interviews with the ISSM, ISSO, maintainers
> and the brigade S6. For hybrid controls we assess only the system's part and examine the
> provider's authorization for the rest. Depth is focused, coverage is full, per SP 800-53A.

### Q2 {#INT-066.Q2}
Asked of: PER-SCA · Task: A-2 · Control focus: ca-2, ra-5, cm-6
Which developer and developmental test results will you reuse?

**A2 {#INT-066.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-1]] [[product/test-results.md#stig-scan]] [[product/test-results.md#vuln-scan]] [[product/test-results.md#account-review]]
> DT-1 (July 2026) for sign-in, lockout, link keying, lost-link and router port results; the
> STIG scan of 2026-09-15, which my team witnessed; the vulnerability scan of the same date;
> and the ISSO's 2026-09-08 account review. They ran on the as-built stations, so they are
> sound, but they are evidence, not determinations. We re-run a spot STIG and vulnerability
> scan on two stations to confirm currency, and we review the not-reviewed STIG items
> ourselves. Nothing covers the mission planner STIG or planner and GDT log forwarding; those
> we assess directly and expect to find gaps, as the product documents.

### Q3 {#INT-066.Q3}
Asked of: PER-SCA · Task: A-2 · Control focus: ca-2.1
Who is on the team?

**A3 {#INT-066.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-065.A2]]
> Me as lead assessor and SCA of record, one technical assessor for scans and testing, and a
> privacy analyst from the Component privacy officer's staff for the pt controls and the
> Privacy Overlay. All three sit outside the program and the brigade S6.

### Q4 {#INT-066.Q4}
Asked of: PER-SCA · Task: A-2 · Control focus: ca-2
What is the schedule?

**A4 {#INT-066.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-063.A2]]
> Kickoff 2026-09-14. Document examination and interviews 2026-09-15 to 2026-09-18. Spot scans
> on test stations 2026-09-22 and 2026-09-23. We examine the cp-4 and ir-3 plans and the
> tabletop schedule on 2026-09-21; the tabletops the program scheduled for the week of
> 2026-11-16 fall after the window. Out-brief 2026-10-01; SAR draft by 2026-10-09.

### Q5 {#INT-066.Q5}
Asked of: PER-SCA · Task: A-2 · Control focus: ca-2, ra-5
What are the rules of engagement?

**A5 {#INT-066.A5}** respondent: simulated · tag: SIMULATED · basis: [[INT-065.A3]]
> Scans and tests only on the six pre-production stations at the test range, never on the
> brigade enclave or a fielded station, and never with an aircraft powered or a GDT radiating.
> Credentialed scans use an assessor account the ISSO creates and removes afterwards. The ISSM
> and the brigade S6 get 48 hours notice before any scan; the ISSO may halt testing at any
> time for safety. Findings are shared with the ISSM daily; no data leaves the test range.
