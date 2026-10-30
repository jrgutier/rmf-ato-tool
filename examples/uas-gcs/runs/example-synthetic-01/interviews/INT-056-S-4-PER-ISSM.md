---
interview_id: INT-056
run_id: example-synthetic-01
task: S-4
persona: PER-ISSM
date: 2026-10-29
topics: [sr family, supply chain risk management]
---
# INT-056 — S-4 — PER-ISSM

### Q1 {#INT-056.Q1}
Asked of: PER-ISSM · Task: S-4 · Control focus: sr-1, sr-2, sr-2.1, sr-3, sr-3.3, sr-5, sr-5.2, sr-6
How does the program manage supply chain risk for the station's components?

**A1 {#INT-056.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/architecture.md#updates]] [[product/conops.md#limitations]]
> Supply chain policy and procedures are the Component's. The program office keeps a supply
> chain risk management plan for the station, written by a team of the PM, me, the ISSE and
> the integrator; it is reviewed yearly. Hardware and firmware come only through the
> integrator's contract from approved suppliers, and the integrator's contract requires secure
> development, flaw notification and signed deliveries. We review the integrator and the two
> component vendors yearly. The weak point is the mission planner: its vendor ends support for
> version 7 in 2027-06 and no replacement is chosen yet, so we carry that as a supply chain risk.

### Q2 {#INT-056.Q2}
Asked of: PER-ISSM · Task: S-4 · Control focus: sr-4, sr-8, sr-10, sr-11, sr-11.1, sr-11.2, sr-12
How are provenance, notification, inspection, counterfeits and disposal handled?

**A2 {#INT-056.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/architecture.md#physical]]
> The integrator records the serial numbers and firmware versions of each kit's hardware in
> the configuration records at build, which gives us provenance per station. Notification
> agreements in the contract require the integrator and vendors to report compromises and
> flaws to the program office. Kits are inspected and tamper seals checked at receipt and at
> each setup. The integrator buys only from original manufacturers or authorized resellers,
> reports suspected counterfeits, and its staff are trained to spot them; components go back
> for service only through the integrator. Retired kits are sanitized and disposed of under the
> Component procedure.
