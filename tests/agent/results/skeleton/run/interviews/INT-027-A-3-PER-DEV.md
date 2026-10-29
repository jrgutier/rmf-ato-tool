---
interview_id: INT-027
run_id: agent-skeleton
task: A-3
persona: PER-DEV
date: 2026-10-29
topics: [federated sign-in, host firewall, update bundle testing]
---
# INT-027 — A-3 — PER-DEV

### Q1 {#INT-027.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: ia-2
**A1 {#INT-027.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/architecture.md#identity]]
> The console accepts remote sign-in only through the identity service; it maps the group claim to
> `admin` or `auditor` and refuses anyone without an approved claim, which DT-2 tested on all
> twelve units. Every console action runs under the asserted identity. The local store still has
> `fieldtech`; the console cannot know which technician typed the shared password. Per-technician
> local accounts with smart-card login are in release 2.3, planned for 2027-03.

### Q2 {#INT-027.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: sc-7
**A2 {#INT-027.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/architecture.md#network]]
> The image ships the host firewall deny-by-default with three permit rules: outbound TLS to IODS,
> outbound syslog over TLS to the CSSP, inbound HTTPS from the management VLAN. Forwarding between
> interfaces is disabled in the kernel. In DT-2 we scanned from the installation network and from
> the maintenance port on each unit; only the documented ports answered and nothing was routed
> between ports. The test case IDs and scan outputs are in the DT-2 report.

### Q3 {#INT-027.Q3}
Asked of: PER-DEV · Task: A-3 · Control focus: si-2
**A3 {#INT-027.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[INT-017.A2]]
> Each monthly bundle covers the OS, collector, console and database. It goes through the baseline
> pipeline, then a regression run on the pre-production units for the fix and for side effects,
> before the configuration control board approves release. Units check the signature before they
> install. The bundle itself is ready within the month; the delay on fielded units is the quarterly
> visit, not our release. Remote update over the uplink is in release 2.2, planned for 2026-12.
