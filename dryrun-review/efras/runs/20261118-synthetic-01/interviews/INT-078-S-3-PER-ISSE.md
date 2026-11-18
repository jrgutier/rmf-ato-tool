---
interview_id: INT-078
run_id: 20261118-synthetic-01
task: S-3
persona: PER-ISSE
date: 2026-11-18
topics: [allocation of controls to components, per family]
---
# INT-078 — S-3 — PER-ISSE

### Q1 {#INT-078.Q1}
Asked of: PER-ISSE · Task: S-3
Access control and identification: which components implement AC-2, AC-3, AC-6, AC-17, IA-2, IA-5 and MA-4?
**A1 {#INT-078.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/architecture.md#network]]
> The application roles and the squadron scoping live in the API (CMP-API); the report service
> (CMP-REPORT) enforces the same scope on exports and the sandbox (CMP-SANDBOX) limits data
> scientists to the training extract. Console and cluster accounts are named roles federated on
> the cluster (CMP-K8S); service accounts use workload identity there. Sign-in is CAC at the
> identity broker, which is outside our boundary; on our side the web front end and the API
> (CMP-WEB, CMP-API) accept only the broker's signed assertion and time sessions out. Remote
> access for users comes in through the edge (CMP-EDGE); engineers' remote maintenance reaches the
> private cluster API through the provider's privileged access path (CMP-K8S). Authenticators we
> manage are the workload identities, the secrets in the key service (CMP-KMS) and the two FIDO2
> break-glass keys.

### Q2 {#INT-078.Q2}
Asked of: PER-ISSE · Task: S-3
Audit, monitoring, boundary and cryptography: which components implement AU-2, AU-6, AU-9, AU-11, SI-4, SC-7, SC-8, SC-12 and SC-28?
**A2 {#INT-078.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/architecture.md#network]] [[product/architecture.md#components]]
> Events come from the edge, the API, the cluster audit log and the database audit extension, and
> all land in the log pipeline (CMP-LOGS); review, protection and retention of the records are on
> CMP-LOGS only, not on each source. Monitoring on our side is the log pipeline's alerts and the
> edge's WAF. Boundary protection inside the account is the edge, the cluster's security groups
> and the sandbox's egress rules (CMP-EDGE, CMP-K8S, CMP-SANDBOX). TLS terminates at the edge;
> the ingest worker pulls over mutual TLS and the API talks TLS to the database (CMP-EDGE,
> CMP-INGEST, CMP-API). Keys are in CMP-KMS; encryption at rest is on the database and object
> storage (CMP-DB, CMP-OBJ).

### Q3 {#INT-078.Q3}
Asked of: PER-ISSE · Task: S-3
Configuration, flaws, contingency, development and supply chain: which components carry CM-2, CM-3, CM-6, SI-2, RA-5, CP-4, CP-9, SA-11, SR-3 and SR-11?
**A3 {#INT-078.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#updates]] [[product/conops.md#availability]] [[product/test-results.md#stig-scan]]
> Baselines and settings are the worker nodes, the database and the edge, checked against the
> Kubernetes and PostgreSQL STIGs (CMP-K8S, CMP-DB, CMP-EDGE). Change control runs through the
> pipeline into the cluster (CMP-K8S). Flaw remediation on our side is the worker images and the
> containers, the report service's image-processing library first (CMP-K8S, CMP-REPORT).
> Scanning inside the account covers the nodes, the database and the edge. Backups are the
> database's point-in-time recovery and object storage versioning (CMP-DB, CMP-OBJ); a
> contingency test is a restore of CMP-DB and a failover of CMP-K8S. Developer testing covers the
> five application components (CMP-WEB, CMP-API, CMP-INGEST, CMP-FORECAST, CMP-REPORT); supply
> chain and authenticity checks are the factory's signing and our cluster's admission policy
> (CMP-K8S). The ingest worker also validates the signature, checksum and schema of each extract
> (CMP-INGEST).

### Q4 {#INT-078.Q4}
Asked of: PER-ISSE · Task: S-3
Which controls have no component home and are organizational or procedural?
**A4 {#INT-078.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-078.A1]] [[INT-078.A3]]
> The policy and procedure controls, the plans (security plan, contingency plan, incident response
> plan), assessment, POA&M and continuous monitoring, the risk assessment and the PIA, training,
> personnel screening and termination, the inventory, external services, and the privacy
> authority and purposes on the documentation side. Those belong to the system as a whole. PE-3
> and MP-6 are in the cloud provider's data centers (CMP-CSP).
