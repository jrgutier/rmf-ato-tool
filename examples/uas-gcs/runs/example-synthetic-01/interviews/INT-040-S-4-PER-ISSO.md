---
interview_id: INT-040
run_id: example-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-10-29
topics: [au family, event logging, storage, review, protection]
---
# INT-040 — S-4 — PER-ISSO

### Q1 {#INT-040.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: au-2, au-3, au-3.1, au-3.3, au-8, au-10, au-12, au-12.1, au-12.3, au-14, au-14.1, au-14.3
Which events are logged, with what content and time, on which components?

**A1 {#INT-040.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/test-results.md#dt-1]]
> The event list was agreed with the CSSP: sign-in, account and privilege events, configuration
> changes, mission upload, command sessions and product export on the workstation OS and the
> flight control application; administrative sessions and denied traffic on the router; and
> administrator sign-in and configuration changes on the GDT, kept in its local log. Each record
> has the time, component, user, event type, source and outcome, plus the mission ID in flight
> control records; personal data in records is limited to the user name. The workstation and
> router take time from the enclave time server when connected and from the GDT's GPS-derived
> time otherwise. The flight control application records each command session from start to end
> with its commands, and the admin role can watch a live session on the workstation and change
> which events are logged from one console. Records name the signed-in user, but `gcsmaint`
> actions cannot be tied to a person.

### Q2 {#INT-040.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: au-1, au-4, au-4.1, au-5, au-5.1, au-6, au-6.1, au-6.3, au-6.4, au-7, au-7.1, au-9, au-9.4, au-9.6, au-11, au-11.1, au-16, au-16.1, au-16.2
How are records stored, protected, reviewed and kept?

**A2 {#INT-040.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[INT-035.A1]] [[product/architecture.md#leveraged]]
> Policy comes from the Component cybersecurity program. The workstation holds 90 days of
> records locally, warns the operator at 75 % of log space and alerts on any logging failure;
> it and the router forward to the enclave log collector over TLS when the uplink is up. Only
> the admin role can read or delete local records, and the forwarded copies are protected and
> kept by the enclave under its ATO, which also reviews and correlates them daily with its
> automated tools and shares them with the CSSP. The workstation has a filter and report tool
> for local review. What is missing: the GDT and mission planner logs are not forwarded, so
> they are not reviewed or correlated; and my weekly station review while disconnected happens
> today only during test events. I will run it on every fielded station from first fielding.
