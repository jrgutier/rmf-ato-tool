---
interview_id: INT-048
run_id: 20261118-synthetic-01
task: P-16
persona: PER-LSE
date: 2026-11-18
topics: [hosting decision, enterprise services reused, enclave application option]
---
# INT-048 — P-16 — PER-LSE

Respondent: ERST technical lead, acting as lead systems engineer.

### Q1 {#INT-048.Q1}
Asked of: PER-LSE · Task: P-16
Where is EFRAS hosted, and why there?
**A1 {#INT-048.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#environment]] [[product/architecture.md#leveraged]]
> In the IL4 cloud region, in a program-owned account. We followed the cloud-first direction.
> The cloud hosting assessment in the acquisition strategy (2026-02-16) found the service can
> be cloud-hosted without compromising security or integrity, because the region holds an IL4
> provisional authorization for CUI. We did not pick a Defense Enterprise Computing Center
> because cloud comes first for a new start. The managed Kubernetes, database and pipeline model
> we build on needs the cloud services.

### Q2 {#INT-048.Q2}
Asked of: PER-LSE · Task: P-16
Could EFRAS have been an application inside an existing authorized enclave, and which enterprise
services did you reuse?
**A2 {#INT-048.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#identity]]
> No. The Component has no authorized enclave that offers a managed Kubernetes and database
> platform for business applications at IL4. The data steward also wants the maintainer data in
> an account the program controls. So EFRAS is a major application with its own authorization.
> Before building anything unique, we considered and reused the following:
> - the authorized cloud region;
> - the enterprise cloud access point, rather than our own boundary;
> - the enterprise identity broker, rather than our own sign-in;
> - the software factory, rather than our own pipeline;
> - the Component CSSP, rather than our own monitoring.
