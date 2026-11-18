---
interview_id: INT-169
run_id: 20261118-synthetic-01
task: A-3
persona: PER-ISSE
date: 2026-11-20
topics: [maintenance tools and session expiry, boundary rules and the sandbox allow-list, transmission and storage encryption, key management]
---
# INT-169 — A-3 — PER-ISSE

### Q1 {#INT-169.Q1}
Asked of: PER-ISSE · Task: A-3 · Control focus: ma-4
Which tools may engineers use for nonlocal maintenance, how do they sign in, and how are sessions ended?
**A1 {#INT-169.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#identity]]
> Only the provider console, the cluster command-line client and the pipeline, as the runbook
> and the security plan list. Engineers sign in with CAC through the identity broker from the
> ERST privileged access workstations over the provider's privileged access path; the console
> session ends at sign-out or after one hour, and the cluster credentials are short-lived and
> expire with it. The two sealed break-glass accounts use FIDO2 keys.

### Q2 {#INT-169.Q2}
Asked of: PER-ISSE · Task: A-3 · Control focus: sc-7
Show me the security group rules, the egress allow-list and what changed for the sandbox after PT-3.
**A2 {#INT-169.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#pentest]]
> The templates define the three tiers: edge to application on 443 only, application to data on
> the database port and the storage endpoints only, no public address on any node. The egress
> allow-list names the EMIS and supply endpoints, the identity broker, the CSSP collector and the
> factory registry; everything else is denied and logged. On 2026-11-03 I removed the wildcard
> that let the sandbox reach a public package mirror. The red team has not retested it; that
> was meant to happen in the penetration test.

### Q3 {#INT-169.Q3}
Asked of: PER-ISSE · Task: A-3 · Control focus: sc-8, sc-12, sc-28
Show me the TLS settings on each path, the key policy and the encryption settings of each store.
**A3 {#INT-169.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#components]] [[product/test-results.md#pipeline-1-5]]
> The load balancer policy allows TLS 1.2 and 1.3 with the DoD-approved suites; the services
> use certificates from the provider's private authority, ingest uses mutual TLS to EMIS and
> the API verifies the database certificate. Every key is a program-owned key in the key
> service, used only by the named workload identities and two key administrators, rotated yearly
> and logged on every use. The database, its snapshots and every bucket are encrypted under
> those keys, and the pipeline's policy check refuses a store without encryption.
