---
interview_id: INT-184
run_id: 20261118-synthetic-01
task: R-1
persona: PER-ISSM
date: 2026-12-14
topics: [digital identity acceptance statement, assurance levels, break-glass compensating controls]
---
# INT-184 — R-1 — PER-ISSM

### Q1 {#INT-184.Q1}
Asked of: PER-ISSM · Task: R-1 · Control focus: ia-2, ia-5
Which identity proofing, authentication and federation assurance levels does EFRAS accept, and why?
**A1 {#INT-184.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-123.A5]] [[INT-097.A1]] [[product/architecture.md#identity]] [[product/test-results.md#dt-2]]
> Every user and engineer signs in with a CAC at the enterprise identity broker. CAC issuance is
> the DoD credentialing process: in-person proofing against source documents with biometrics, so
> identity proofing is IAL3, and the CAC's PKI certificate on a hardware token with a PIN is a
> multi-factor cryptographic authenticator, so authentication is AAL3. Federation: the product
> shows only that the broker's assertions are signed and reach EFRAS over TLS; whether the
> onboarding profile also encrypts them to EFRAS is not in our records. So the DIAS states FAL1,
> the level we can show, and the ISSO confirms the profile with the broker before the decision.
> Nothing in EFRAS chose these levels by its own risk assessment: the enterprise service sets
> them, and the ia-2 and ia-5 statements in the plan rest on them.

### Q2 {#INT-184.Q2}
Asked of: PER-ISSM · Task: R-1 · Control focus: ia-2
Where can a level not be met, and what compensates?
**A2 {#INT-184.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-123.A2]] [[product/conops.md#limitations]]
> The two break-glass console accounts. Their FIDO2 keys are hardware, phishing-resistant
> authenticators, but they are not bound to a proofed identity the way a CAC is; attribution
> rests on the seal log. Compensating: the keys stay sealed, two people open them, the on-call
> engineer and the ISSO are paged at every use, every action is logged, and each use is reviewed
> against the seal log the next working day. The deviation goes to the AO with the package
> (POAM-020).
