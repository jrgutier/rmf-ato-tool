---
interview_id: INT-045
run_id: 20261118-synthetic-01
task: P-15
persona: PER-PM
date: 2026-11-18
topics: [program needs, constraints, priorities, issues, agreement]
---
# INT-045 — P-15 — PER-PM

### Q1 {#INT-045.Q1}
Asked of: PER-PM · Task: P-15
What protection need does the program hold, and which constraints bind the solution?
**A1 {#INT-045.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#environment]] [[product/architecture.md#leveraged]]
> The program needs to keep inheriting from authorized providers, and to have every release
> go through the factory's security gates. I judge it met when each release has passing gates,
> an SBOM and signed images, and no provider authorization lapses. The constraints are these:
> - The service runs in the IL4 cloud region and is reached only over NIPRNet through ECAP.
> - Sign-in goes through the enterprise identity broker with CAC, and the provider console uses
>   FIDO2 break-glass keys because it cannot federate when the broker is down.
> - Builds come only from the software factory.
> - The MVCR must deploy by 2027-02-01.
> - Data comes from EMIS under an interim e-mail approval until the agreement is signed.

### Q2 {#INT-045.Q2}
Asked of: PER-PM · Task: P-15
Which requirements issues came up, and how were they resolved?
**A2 {#INT-045.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]]
> Three issues came up.
> - Audit retention: the program keeps 90 days and the Component wants one year. We kept the
>   one-year requirement (REQ-05) and track the gap until release 1.6 adds the archive tier.
> - CAC everywhere conflicts with the break-glass keys. We wrote the authentication requirement
>   for all human users through the broker, and recorded the console exception as a constraint
>   the AO must accept.
> - REQ-16 asks for an approved PIA before production use with real PII, while the PIA is a
>   draft. We kept REQ-16 as written, so MVCR deployment depends on PIA approval, planned for
>   January 2027.
> I agree to the set and its priorities as of 2026-11-18. Integrity of readiness data comes first,
> then the privacy and confidentiality requirements, then recovery and the rest.
