---
interview_id: INT-022
run_id: agent-cold-start-resume
task: A-3
persona: PER-CCP
date: 2026-10-30
topics: [enclave boundary protection evidence, identity service evidence]
---
# INT-022 — A-3 — PER-CCP

### Q1 {#INT-022.Q1}
Asked of: PER-CCP · Task: A-3 · Control focus: sc-7, ia-2
What evidence shows the enclave's and the identity service's parts are in place for ESG?
**A1 {#INT-022.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#leveraged]] [[product/architecture.md#network]] [[product/architecture.md#interconnections]]
> The Installation Network Enclave, which also covers the Installation ICAM Service, holds an
> ATO dated 2025-11-20, and that assessment covered the enclave firewall, intrusion detection
> and network access control at the edge, and PKI authentication at the identity service. The
> enclave firewall in front of every ESG site switch enforces the same permitted flows as the
> ESG host firewall. The console's link to the identity service runs under the installation
> service agreement (IC-2). I can attest to the provider side only; the ESG host firewall and the
> console's role mapping are the program's part.
