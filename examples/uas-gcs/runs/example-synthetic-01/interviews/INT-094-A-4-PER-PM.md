---
interview_id: INT-094
run_id: example-synthetic-01
task: A-4
persona: PER-PM
date: 2026-10-29
topics: [system owner response to significant findings, planned remediation]
---
# INT-094 — A-4 — PER-PM

### Q1 {#INT-094.Q1}
Asked of: PER-PM · Task: A-4 · Control focus: FND-001, FND-009, FND-027 to FND-035
What is the program's response to the shared `gcsmaint` and GDT administrator account findings?

**A1 {#INT-094.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> We accept them; we disclosed the shared maintenance account ourselves. Release 2.4 replaces
> `gcsmaint` with per-maintainer accounts and offline CAC sign-in. Until it fields, the GDT
> administrator password gets a named custodian and is changed after every maintainer
> rotation. I want the report to say the fix is planned, not that it is done.

### Q2 {#INT-094.Q2}
Asked of: PER-PM · Task: A-4 · Control focus: FND-007, FND-008, FND-054, FND-062, FND-063
And the log-forwarding and open-vulnerability findings?

**A2 {#INT-094.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-091.A2]] [[product/test-results.md#vuln-scan]]
> Planner and GDT log forwarding to the enclave collector is a release 2.4 item too; until
> then the ISSO exports and reviews the logs at each reconnect. GDT firmware 5.2.1 goes into
> the 2026-12 bundle and we rescan all six stations after it. For the planner library findings
> there is no vendor fix date, so we will ask the AO to accept that risk with the
> internal-network-only exposure as the mitigating factor.

### Q3 {#INT-094.Q3}
Asked of: PER-PM · Task: A-4 · Control focus: FND-058, FND-069, FND-023, FND-036
What about planner end of support and the unwritten contingency and incident response plans?

**A3 {#INT-094.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-093.A1]]
> The release 3.0 planner selection is the program's biggest schedule risk; I owe a selection
> date by 2027-01 so it can field before 2027-06. The contingency and incident response plans
> are being drafted now and will be exercised in the next test event. I agree with the
> severities as rated.
