---
interview_id: INT-015
run_id: agent-skeleton
task: S-4
persona: PER-ISSE
date: 2026-10-30
topics: [user identification and authentication, boundary protection]
---
# INT-015 — S-4 — PER-ISSE

### Q1 {#INT-015.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: ia-2
How does the console uniquely identify and authenticate its users, and what part does the identity service provide?
**A1 {#INT-015.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#dt-2]] [[INT-012.A1]]
> Remote administrators and auditors authenticate with their DoD PKI smart card at the
> Installation ICAM Service; the console federates to it and maps the group claim to the
> `admin` or `auditor` role, so each remote session belongs to one named person. The ICAM
> service provides the PKI authentication; the console provides the federation, role mapping
> and session handling. DT-2 confirmed that users without an approved claim are refused.

### Q2 {#INT-015.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: ia-2
What does not meet unique identification today?
**A2 {#INT-015.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#account-review]]
> On the maintenance port the ten field technicians sign in with the shared local `fieldtech`
> password account, so those sessions are not tied to an individual and processes started in
> them act for the account, not a person. The sealed `esgadmin` break-glass account is used by
> one named person per logged and reported use. Release 2.3, planned for 2027-03, replaces
> `fieldtech` with per-technician local accounts with smart-card login that work without a
> path to the identity service.

### Q3 {#INT-015.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: sc-7
How are communications at the boundary monitored and controlled, and who does which part?
**A3 {#INT-015.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#network]] [[product/test-results.md#dt-2]] [[INT-012.A1]]
> The host firewall on each gateway denies by default and permits only outbound TLS 1.3 to
> IODS, outbound syslog over TLS to the CSSP, and inbound HTTPS to the console from the
> management VLAN. The maintenance port is off until the shelter key switch enables it, serves
> only a link-local console, and never routes to the uplink. Sensor nodes have no IP path. The
> enclave firewall, intrusion detection and network access control in front of every site
> switch enforce the same flows at the enclave edge. ESG has no publicly accessible
> component. The DT-2 port scans from both ports found only the documented ports and no routing.
