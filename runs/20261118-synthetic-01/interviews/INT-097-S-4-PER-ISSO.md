---
interview_id: INT-097
run_id: 20261118-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-11-18
topics: [identification and authentication (family ia), authenticator management (family ia)]
---
# INT-097 — S-4 — PER-ISSO

### Q1 {#INT-097.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: ia-2
How are users identified and authenticated, and where is there an exception?
**A1 {#INT-097.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#dt-2]] [[product/conops.md#limitations]]
> Every human user signs in with CAC at the enterprise identity broker; the broker's signed
> assertion carries the DoD ID number, which CMP-WEB and CMP-API bind to the session and to every
> audit event, so actions trace to a person. DT-2 passed CAC sign-in for all five roles. Engineers
> reach CMP-K8S through named console roles federated through the broker with CAC. The exception
> is the two break-glass console accounts: FIDO2 keys, not CAC, because the console cannot
> federate when the broker is down. They are sealed, unused so far, and any use alerts. The
> deviation is to be recorded and accepted; no fix is planned.

### Q2 {#INT-097.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: ia-5
How are authenticators managed?
**A2 {#INT-097.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#stig-scan]] [[product/architecture.md#components]]
> CACs are issued and revoked by the DoD credentialing process, outside EFRAS. Service accounts use
> workload identity with short-lived tokens; there are no long-lived access keys. Secrets and keys
> sit in CMP-KMS under program-owned keys, rotated yearly or on suspected compromise. I issue the
> two FIDO2 keys in person against ID and keep them sealed; I re-key them if anyone who knew the
> sealing changes role. The only passwords are the local break-glass database role's, which
> follows the CNSSI 1253 value: changed at least every 180 days. The open item is the local break-glass database role: the STIG scan found
> its password complexity short, fixed in release 1.5.2, planned 2026-12-10.
