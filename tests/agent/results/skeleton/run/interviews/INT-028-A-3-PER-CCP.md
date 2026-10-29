---
interview_id: INT-028
run_id: agent-skeleton
task: A-3
persona: PER-CCP
date: 2026-10-29
topics: [ICAM evidence for ia-2, enclave evidence for sc-7]
---
# INT-028 — A-3 — PER-CCP

### Q1 {#INT-028.Q1}
Asked of: PER-CCP · Task: A-3 · Control focus: ia-2
**A1 {#INT-028.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-018.A1]] [[product/architecture.md#leveraged]]
> Answering for the Installation Network Enclave, which also runs the ICAM service. The ESG relying
> party is registered in the identity service, the `esg-admin` and `esg-auditor` groups are
> provisioned through our account workflow after the ISSO's approval, and credentials are DoD PKI
> smart cards validated against current revocation data. That part is covered by the enclave ATO
> of 2025-11-20, which is current. We cover no local accounts on the gateways.

### Q2 {#INT-028.Q2}
Asked of: PER-CCP · Task: A-3 · Control focus: sc-7
**A2 {#INT-028.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-018.A2]] [[product/architecture.md#network]]
> Each ESG site switch port is on the ESG enclave VLAN behind our enclave firewall, intrusion
> detection and network access control. The firewall permits only the registered ESG flows to IODS,
> the CSSP collector and from the management VLAN; I can give you the rule export for those flows.
> We monitor the enclave edge; ESG must notify us before any new flow, and none has been requested.
