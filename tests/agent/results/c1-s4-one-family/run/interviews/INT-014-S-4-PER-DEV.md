---
interview_id: INT-014
run_id: agent-c1-s4-one-family
task: S-4
persona: PER-DEV
date: 2026-10-30
topics: [console enforcement, session handling, OS hardening]
---
# INT-014 — S-4 — PER-DEV

### Q1 {#INT-014.Q1}
Asked of: PER-DEV · Task: S-4
**A1 {#INT-014.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#dt-2]]
> The console checks the role on every request: `auditor` is read-only and cannot reach any
> configuration, account or update page; only `admin` can. Before sign-in it shows the DoD
> standard notice and consent banner, on the uplink and on the maintenance port, and the only page
> reachable without sign-in is the sign-in page itself. Each account may hold one session at a
> time; a new sign-in ends the older session.

### Q2 {#INT-014.Q2}
Asked of: PER-DEV · Task: S-4
**A2 {#INT-014.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#dt-2]]
> After 15 minutes idle the console locks the session behind a blank lock screen that hides the
> page; after 60 minutes idle, or when the user clicks Sign out, it ends the session and shows a
> "session ended" message. Five failed local sign-ins lock the account for 30 minutes.

### Q3 {#INT-014.Q3}
Asked of: PER-DEV · Task: S-4
**A3 {#INT-014.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#network]]
> The signed OS image runs the collector, console and database as separate unprivileged service
> accounts; only the update installer runs as root. The image disables USB mass storage, Wi-Fi and
> Bluetooth; the only radio is the paired field radio. Configuration and keys live on the
> encrypted data partition, readable only by the console service and root.
