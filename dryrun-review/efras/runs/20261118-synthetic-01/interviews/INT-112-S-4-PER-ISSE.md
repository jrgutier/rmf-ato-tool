---
interview_id: INT-112
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-11-18
topics: [boundary protection inside the account, transmission protection, key management, protection at rest]
---
# INT-112 — S-4 — PER-ISSE

### Q1 {#INT-112.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-7
How do the edge, the cluster and the sandbox implement EFRAS's part of boundary protection?
**A1 {#INT-112.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#pentest]] [[INT-071.A2]]
> Ingress comes only from the access point to the load balancer on 443, where the WAF rules
> apply; no node has a public address. The virtual network has three subnet tiers, edge,
> application and data, logically separated by security groups that allow edge to application
> on 443 and application to data on the database port and the storage endpoints only; the
> load balancer is the only component the users reach, and it sits alone in the edge tier.
> Egress leaves through the NAT gateway to an allow-list; everything else is denied and logged.
> The sandbox sits in the application tier with its own security group and reads only the
> training extract. PT-3 found a wildcard on the allow-list that let the sandbox fetch packages
> from a public mirror; we narrowed it on 2026-11-03 and the red team's retest is pending.

### Q2 {#INT-112.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-8
How is information protected in transit on each path?
**A2 {#INT-112.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/architecture.md#interconnections]] [[product/test-results.md#dt-2]]
> Users reach the load balancer over TLS 1.2 or 1.3 with DoD-approved cipher suites. The load
> balancer re-encrypts to the services with TLS using certificates from the provider's private
> certificate authority, so nothing crosses the virtual network in clear. The ingest worker
> pulls the EMIS extract over mutual TLS and the supply status over TLS, and checks the extract's
> signature; DT-2 showed a tampered extract is rejected. The API reaches the database over TLS
> with certificate verification. The TLS modules are the provider's FIPS 140-validated ones.

### Q3 {#INT-112.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-12, sc-28
How are keys managed, and what is encrypted at rest?
**A3 {#INT-112.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/test-results.md#pipeline-1-5]] [[INT-074.A3]]
> Keys are program-owned customer-managed keys in the provider's key service, whose hardware
> security modules are FIPS 140 validated. Key generation, storage, access and destruction stay
> in the key service; no key material leaves it. Access to the keys is granted by policy to
> named workload identities and two key administrators, and every use is logged to CMP-LOGS. Keys
> rotate yearly, and a disabled key is destroyed after its 30-day waiting period. The database,
> its backups and snapshots, and every storage bucket are encrypted with those keys, AES-256 in
> an authenticated mode, so tampering is detected as well. The pipeline's policy check refuses a
> store without encryption; it passed for 1.5.0.
