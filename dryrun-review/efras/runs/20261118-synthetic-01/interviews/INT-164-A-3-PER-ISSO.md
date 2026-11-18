---
interview_id: INT-164
run_id: 20261118-synthetic-01
task: A-3
persona: PER-ISSO
date: 2026-11-20
topics: [user identification, break-glass accounts, authenticator management, secrets and keys]
---
# INT-164 — A-3 — PER-ISSO

### Q1 {#INT-164.Q1}
Asked of: PER-ISSO · Task: A-3 · Control focus: ia-2
Who can sign in without CAC, and how is each break-glass use tied to one person?
**A1 {#INT-164.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/architecture.md#identity]] [[product/test-results.md#account-review]]
> Every user and every engineer signs in with CAC through the broker, and the DoD ID number from
> the assertion is on the session and every audit event. The only exceptions are the two
> break-glass console accounts, which use a FIDO2 key because the console cannot federate when
> the broker is down. The keys are sealed in the program safe; the seal log names who may open
> them, and opening one requires two people to sign the log, so a use is tied to a person by the
> log and the alert, not by a PKI credential. Neither has been used. The deviation from the
> DoD requirement to use CAC has not yet been put to the AO.

### Q2 {#INT-164.Q2}
Asked of: PER-ISSO · Task: A-3 · Control focus: ia-5
Show me how each authenticator type is issued, protected, changed and revoked, and the state of the break-glass database password.
**A2 {#INT-164.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#stig-scan]] [[product/architecture.md#identity]]
> CACs are the DoD credentialing office's. Workloads use workload identity tokens that last one
> session; there are no long-lived access keys, and the key service's inventory shows none. The
> program keys in the key service were last rotated 2026-03-02 and are due annually. I issued the
> two FIDO2 keys in person against ID on 2026-03-10, the default PINs were changed at issue, and
> the issue record is signed. The local break-glass database role's password was last changed
> 2026-07-01, inside 180 days, and is held sealed; its complexity still falls short of the
> PostgreSQL STIG rule, and the fix is in release 1.5.2.
