---
interview_id: INT-072
run_id: example-synthetic-01
task: A-3
persona: PER-CCP
date: 2026-10-29
topics: [enclave log collector, inherited audit controls]
---
# INT-072 — A-3 — PER-CCP

### Q1 {#INT-072.Q1}
Asked of: PER-CCP · Task: A-3 · Control focus: au-6, au-6.1, au-6.4, au-7, au-9, au-11, au-16
What does the enclave collector show for the ETGCS test stations?

**A1 {#INT-072.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/test-results.md#dt-1]]
> The collector holds workstation and router records from all six stations since DT-1, with
> station and user identity intact. Our daily automated review reports for those dates show
> the ETGCS sources included. Records are protected and retained under the enclave ATO's rules
> and shared with the CSSP feed. We have nothing from the GDT or the mission planner.
