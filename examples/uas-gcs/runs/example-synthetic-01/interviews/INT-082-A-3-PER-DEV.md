---
interview_id: INT-082
run_id: example-synthetic-01
task: A-3
persona: PER-DEV
date: 2026-10-29
topics: [mp-7 media control mechanism, pl-8 architecture evidence]
---
# INT-082 — A-3 — PER-DEV

### Q1 {#INT-082.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: mp-7, mp-4
How does the workstation image enforce the registered-media rule and protect stored data?

**A1 {#INT-082.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]]
> The image has a device-control policy that mounts only media whose identifiers the ISSO has
> registered, and the endpoint scanner checks each one before it mounts. Both settings are in
> the signed bundle and were covered by the 2026-09-15 STIG scan. The workstation disk is
> fully encrypted.

### Q2 {#INT-082.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: pl-8, pl-8.1, pl-8.2
Show the architecture description and evidence that the protection layers come from different suppliers.

**A2 {#INT-082.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]]
> The architecture description covers components, boundary, network, identity, logging and
> updates, and shows the layers: enclave firewall and IDS, station router, isolated internal
> segment, CAC sign-in, encrypted disk. We have not yet added the supplier of each layer; the
> enclave layers are run by the enclave and we do not hold their supplier records. So supplier
> diversity is not shown in the document today.
