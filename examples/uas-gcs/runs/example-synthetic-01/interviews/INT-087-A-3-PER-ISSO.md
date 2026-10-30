---
interview_id: INT-087
run_id: example-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-10-29
topics: [ra vulnerability scanning evidence, sc boundary and router evidence, sc key and certificate records]
---
# INT-087 — A-3 — PER-ISSO

### Q1 {#INT-087.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ra-5, ra-5.2, ra-5.4, ra-5.5
Show the scan records for the six stations: dates, feed updates, the credential used and the open results.

**A1 {#INT-087.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#vuln-scan]]
> The scan log shows a credentialed scan of every station each month they were connected and on
> each reconnection; the last full one is 2026-09-15. Each run starts with a feed update from the
> enclave, logged with its date. The scans run under the dedicated scan account, not `gcsmaint`;
> you can see the account name in the scan header. Every report lists the services each station
> exposes on its uplink. The three medium workstation and router findings are gone from the
> reconnection scan after the 2026-10 bundle went on. Still open: the ground data terminal
> management web service vulnerability, waiting for firmware 5.2.1, and the two medium library
> findings in the mission planner, which have no vendor fix date. The planner's configuration is
> not covered by any compliance scan because there is no STIG for it.

### Q2 {#INT-087.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: sc-2, sc-5, sc-5.1, sc-5.2, sc-5.3, sc-7, sc-7.3, sc-7.4, sc-7.5, sc-7.7, sc-7.8, sc-7.9, sc-7.10, sc-7.11, sc-7.12, sc-7.13, sc-7.14, sc-7.25, sc-7.28, sc-7.29, sc-10, sc-15, sc-21, sc-41, sc-45, sc-45.1
Show the router and host firewall configuration, the denied-traffic records and the settings for sessions, devices and time.

**A2 {#INT-087.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]]
> Here is the router rule set export from the approved baseline: default deny both ways, one
> permit per listed flow (product drop, log collector, directory, remote administration from the
> S6 subnet only), the inbound rate limit on the uplink and logging on the deny rule. The CCB
> approved the current rule set; its minutes list each flow. The enclave collector holds the
> router's deny records, including the blocked outbound attempts from the DT-1 port scan. The
> workstation host firewall policy carries the same rules. On the internal segment the ground
> data terminal management port answers only to station addresses; you watched me try it from the
> uplink side and it did not answer. The router's idle administrative timeout is 10 minutes. The
> image disables the camera, microphone, unused ports and USB storage, except for the maintainer
> role installing signed bundles. Name lookups go only to the router, which forwards to the
> enclave resolvers. The router takes time from the enclave and its log shows the drift check
> after each reconnection, none over one second. Admin tools run only for the `admin` role.

### Q3 {#INT-087.Q3}
Asked of: PER-ISSO · Task: A-3 · Control focus: sc-12, sc-17, sc-38
Show the key loading and certificate records.

**A3 {#INT-087.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]]
> The key log records the aircraft link key load before each DT-1 mission, with the loader's
> name and the key's validity period. The certificate list shows every workstation and router
> certificate issued by DoD PKI with its expiry date; none expires within 90 days. The cases are
> sealed and the seal numbers match the hand receipts I checked at the last setup.
