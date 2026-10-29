---
interview_id: INT-012
run_id: agent-skeleton
task: S-1
persona: PER-CCP
date: 2026-10-29
topics: [common controls, inheritance, provider authorizations]
---
# INT-012 — S-1 — PER-CCP

### Q1 {#INT-012.Q1}
Asked of: PER-CCP · Task: S-1 · Control focus: sc-7
**A1 {#INT-012.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#leveraged]] [[product/architecture.md#network]]
> For the Installation Network Enclave: we provide boundary protection at the enclave edge, the
> enclave firewall and network access control in front of every site switch. ESG inherits that
> part only; the system must still run its own host firewall, deny by default, so sc-7 is
> hybrid. Our ATO dated 2025-11-20 is current.

### Q2 {#INT-012.Q2}
Asked of: PER-CCP · Task: S-1 · Control focus: ia-2
**A2 {#INT-012.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#identity]] [[product/architecture.md#leveraged]]
> For the Installation ICAM Service: we provide DoD PKI authentication and identity assurance for
> remote organizational users, under the enclave ATO. ESG must federate its console and map our
> group claims to its roles; the local break-glass and fieldtech accounts are not ours. So ia-2 is
> hybrid, never full inheritance.

### Q3 {#INT-012.Q3}
Asked of: PER-CCP · Task: S-1 · Control focus: au-2
**A3 {#INT-012.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#logging]] [[product/architecture.md#leveraged]]
> For the Installation CSSP: we collect and correlate logs in the SIEM, monitor, and support
> incident response. For au-2 we agreed the event list with ESG and review it with them; ESG must
> generate the events and forward them to us. Hybrid. Our ATO dated 2026-01-30 is current.

### Q4 {#INT-012.Q4}
Asked of: PER-CCP · Task: S-1
**A4 {#INT-012.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]]
> None of the three providers offers ac-2, cm-6 or si-2 to ESG. Those are the system's own.
