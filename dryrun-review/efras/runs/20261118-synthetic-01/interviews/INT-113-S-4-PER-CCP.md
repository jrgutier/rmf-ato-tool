---
interview_id: INT-113
run_id: 20261118-synthetic-01
task: S-4
persona: PER-CCP
date: 2026-11-18
topics: [access point boundary protection, cloud region flaw remediation]
---
# INT-113 — S-4 — PER-CCP

### Q1 {#INT-113.Q1}
Asked of: PER-CCP · Task: S-4 · Control focus: sc-7
Speaking for Example Enterprise Cloud Access Point: what do you implement for EFRAS's boundary, and what must EFRAS do?
**A1 {#INT-113.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-071.A2]] [[product/architecture.md#network]] [[product/architecture.md#leveraged]]
> For Example Enterprise Cloud Access Point. We are the managed interface between NIPRNet and the
> cloud: we inspect and filter every session to the EFRAS load balancer and block what our
> rules forbid, and we keep the traffic logs for the CSSP. EFRAS must keep its load balancer
> reachable only from our path, keep its own subnets, security groups, WAF and egress allow-list,
> and tell us before it opens a new port. Our evidence is our ATO package and our monthly
> report to the Component.

### Q2 {#INT-113.Q2}
Asked of: PER-CCP · Task: S-4 · Control focus: si-2
Speaking for Example GovCloud IL4 region: what flaw remediation do you perform, and what is left to EFRAS?
**A2 {#INT-113.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-071.A1]] [[product/architecture.md#updates]]
> For Example GovCloud IL4 region. We patch the hypervisor, the managed Kubernetes control
> plane and the database engine, and we publish the hardened node image each month. Patches go
> in announced windows, within the timelines of our provisional authorization, and our monthly
> deliverables report them. EFRAS rolls its worker nodes to the latest node image and patches
> its containers; we cannot do that for it.
