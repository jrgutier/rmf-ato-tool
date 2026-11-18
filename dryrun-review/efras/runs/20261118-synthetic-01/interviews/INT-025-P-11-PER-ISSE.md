---
interview_id: INT-025
run_id: 20261118-synthetic-01
task: P-11
persona: PER-ISSE
date: 2026-11-18
topics: [boundary edge, interfaces, permitted flows, segmentation, external dependencies, diagrams]
---
# INT-025 — P-11 — PER-ISSE

### Q1 {#INT-025.Q1}
Asked of: PER-ISSE · Task: P-11
**A1 {#INT-025.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#boundary]] [[product/architecture.md#components]] [[ART-INV]]
> The edge is the program-owned production cloud account. Inside it are the twelve components
> we configure: CMP-EDGE, CMP-WEB, CMP-API, CMP-INGEST, CMP-FORECAST, CMP-REPORT, CMP-K8S,
> CMP-DB, CMP-OBJ, CMP-KMS, CMP-LOGS and CMP-SANDBOX, which hold every inventory item. Outside
> are the cloud provider's own infrastructure and managed-service internals (CMP-CSP), the
> access point (CMP-ECAP), the identity broker (CMP-IDB), the software factory (CMP-SWF), ECSSP
> (CMP-ECSSP) and the two source systems, EMIS (CMP-EMIS) and the supply status service
> (CMP-SUPPLY). The pre-production account is a separate environment with synthetic data and
> stays out of this authorization.

### Q2 {#INT-025.Q2}
Asked of: PER-ISSE · Task: P-11
**A2 {#INT-025.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]]
> One virtual private network with three subnet tiers. Edge holds only the load balancer;
> application holds the cluster nodes; data holds the database endpoint and the private
> endpoints to object storage and the key service. Security groups allow edge to application on
> 443 and application to data on the database port and the storage endpoints only. Ingress comes
> only from the ECAP on 443 with TLS 1.2 or 1.3 and DoD-approved suites; no node has a public
> address. Egress leaves the application tier through a managed NAT gateway to an allow-list:
> EMIS and supply endpoints, the identity broker, the ECSSP collector and the factory registry;
> everything else is denied and logged. The cluster API is private and reached only through the
> provider's privileged access path from the ERST privileged access workstations after CAC
> sign-in.

### Q3 {#INT-025.Q3}
Asked of: PER-ISSE · Task: P-11
**A3 {#INT-025.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/data-flows.md#top]] [[product/data-flows.md#main]]
> The ten flows DF-1 to DF-10 are the complete set. Four cross the boundary inbound: users
> through the ECAP (DF-1), identity assertions (DF-2), the EMIS extract with maintainer personal
> data (DF-3) and supply status (DF-4); two cross outbound: audit records to ECSSP (DF-9) and,
> inbound again, signed images from the factory (DF-10). DF-5 to DF-8 stay inside. Every flow
> is TLS-protected; DF-3 is mutual TLS with a signed, checksummed extract; DF-10 images are
> signature-checked at admission. The maintainer personal data rides DF-3, DF-5 and DF-6, and in
> pseudonymized form DF-7 exports and DF-8 to the sandbox.

### Q4 {#INT-025.Q4}
Asked of: PER-ISSE · Task: P-11
**A4 {#INT-025.A4}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/data-flows.md#top]]
> We have no drawn diagrams in the product package, only the component, network and flow tables.
> I accept diagrams drawn from those tables for the package, as long as they show exactly what
> the tables say and nothing more. EFRAS is not a complex system: it has no subsystems with
> their own categorization, and every internal component runs at the same impact level.
