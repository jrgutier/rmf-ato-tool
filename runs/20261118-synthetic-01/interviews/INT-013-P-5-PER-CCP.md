---
interview_id: INT-013
run_id: 20261118-synthetic-01
task: P-5
persona: PER-CCP
date: 2026-11-18
topics: [controls offered fully or in part, provider authorizations]
---
# INT-013 — P-5 — PER-CCP

### Q1 {#INT-013.Q1}
Asked of: PER-CCP · Task: P-5
**A1 {#INT-013.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#physical]]
> For the Example GovCloud IL4 region: we provide physical and environmental protection in
> full (pe-2, pe-3, pe-6, pe-13, pe-14) and media sanitization of our storage in full (mp-6).
> We patch the managed Kubernetes control plane and database engine, which is our part of
> si-2, and keep storage durable and backed up inside the managed services, our part of cp-9;
> the customer configures and patches its own workloads and sets its own backups.

### Q2 {#INT-013.Q2}
Asked of: PER-CCP · Task: P-5
**A2 {#INT-013.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#network]]
> For the Example Enterprise Cloud Access Point: boundary protection between NIPRNet and the
> cloud and traffic inspection, our part of sc-7 and si-4; the program still controls its own
> subnets, security groups and application firewall.

### Q3 {#INT-013.Q3}
Asked of: PER-CCP · Task: P-5
**A3 {#INT-013.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#configuration]]
> For the Example Software Factory: pipeline integrity and configuration management of the
> pipeline (sa-10), static and dynamic code scanning (sa-11), the development process and
> tooling (sa-15), image signing and admission verification support (cm-14), and the hardened
> base images and their provenance (sr-3, sr-11). Each is shared: the program owns its code,
> its own dependencies and its admission policy. Our hardened image carrying the fix for the
> image-processing library is late; that is on our POA&M.

### Q4 {#INT-013.Q4}
Asked of: PER-CCP · Task: P-5
**A4 {#INT-013.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#logging]]
> For the Example Cybersecurity Service Provider: 24x7 monitoring of forwarded logs (our part of
> si-4 and au-6), incident response support and reporting to JFHQ-DODIN (our part of ir-4 and
> ir-6) and vulnerability alerts (our part of ra-5). Programs must forward their logs and
> report incidents to us.
