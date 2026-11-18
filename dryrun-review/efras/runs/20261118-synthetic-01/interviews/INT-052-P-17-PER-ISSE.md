---
interview_id: INT-052
run_id: 20261118-synthetic-01
task: P-17
persona: PER-ISSE
date: 2026-11-18
topics: [allocation of requirements to components, providers and the environment]
---
# INT-052 — P-17 — PER-ISSE

### Q1 {#INT-052.Q1}
Asked of: PER-ISSE · Task: P-17
Where does each requirement land: which components, which providers, the environment, the
contract?
**A1 {#INT-052.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/architecture.md#leveraged]] [[ART-REQ]]
> - REQ-01 (CAC): the web front end and the API enforce the session. The identity broker, an
>   enterprise provider, does the CAC check.
> - REQ-02 (echelon access): the API, and the report service for exports.
> - REQ-03 (encryption): the edge for TLS; the database, object storage and keys for data at
>   rest.
> - REQ-04 (ingest checks): the ingest worker alone.
> - REQ-05 (audit): the log pipeline. The CSSP holds the one-year copy as a provider.
> - REQ-06 (recovery): the database and the cluster. The cloud region provides the standby and
>   backups.
> - REQ-07 (build integrity): the cluster's admission control. The software factory is the
>   provider of the gates, and ERST is bound to it by contract.
> - REQ-08 (STIG/SCAP): the cluster nodes and the database.
> - REQ-09 (marking): the web front end and the report service.
> - REQ-10 (ingress, segmentation): the edge and the cluster network. The access point is the
>   provider of the NIPRNet boundary.
> - REQ-11 (standards): the API and the ingest worker, which carry the interfaces.
> - REQ-12 (accessibility): the web front end.
> - REQ-13 (verification and traceability): the ERST contract.
> We split them this way because the program configures the components and inherits the rest
> from the providers' authorizations.

### Q2 {#INT-052.Q2}
Asked of: PER-ISSE · Task: P-17
Which cyber resilient engineering requirements does the ERST task order carry?
**A2 {#INT-052.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]]
> The task order modification of 2026-11-18 carries the PPP countermeasures CM-001 (factory
> gates, signed images, SBOMs) and CM-002 (boundary hardening). It also carries two cyber
> resilient requirements: immutable images rebuilt from source, and tested point-in-time
> restore. Its software assurance remediation is a 30-day fix of high findings through the
> factory gates. The program builds no hardware, so the order has no hardware assurance clause.
