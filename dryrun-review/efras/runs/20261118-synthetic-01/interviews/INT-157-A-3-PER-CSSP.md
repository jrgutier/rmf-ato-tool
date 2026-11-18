---
interview_id: INT-157
run_id: 20261118-synthetic-01
task: A-3
persona: PER-CSSP
date: 2026-11-20
topics: [log delivery, correlation and tickets, CSSP log retention]
---
# INT-157 — A-3 — PER-CSSP

### Q1 {#INT-157.Q1}
Asked of: PER-CSSP · Task: A-3 · Control focus: au-6, au-11
What evidence shows your part of audit review is in place for EFRAS, and how long do you keep its forwarded records?
**A1 {#INT-157.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/test-results.md#dt-2]]
> The EFRAS stream has arrived without a gap since onboarding; our ingestion dashboard shows the
> last 90 days with no outage longer than our 15-minute alert threshold. The EFRAS use cases
> (export volume, privileged actions outside a change window, break-glass use, repeated denied
> requests) run 24x7, and the three tickets we opened in the last quarter went to the ISSO. We
> keep forwarded records one year under our own retention schedule for our analysis; they are
> retrievable for EFRAS only by a request through the ticket path, and our schedule can change
> without the program's agreement.
