---
interview_id: INT-092
run_id: example-synthetic-01
task: A-3
persona: PER-DEV
date: 2026-10-29
topics: [si integrity mechanisms, input validation, radio link, supply chain records]
---
# INT-092 — A-3 — PER-DEV

### Q1 {#INT-092.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: si-7, si-7.1, si-7.7, si-7.8, si-7.9, si-7.10, si-7.15, si-16
Demonstrate the integrity mechanisms on a test station.

**A1 {#INT-092.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]], [[product/architecture.md#configuration]]
> On the witnessed demonstration an altered bundle and an unsigned GDT image were both rejected
> by the installer; a changed baseline file was flagged at the next start-up, logged as an
> integrity event and alerted. Secure boot and the TPM measured boot are on in the firmware
> settings, the firmware setup is password-protected, and the STIG scan shows data execution
> prevention and address randomization enabled.

### Q2 {#INT-092.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: si-8, si-10, si-10.3, si-10.6, si-11, si-15, si-4.14, si-4.15
Show the input validation and error-handling tests, and how the radio link is protected.

**A2 {#INT-092.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-1]], [[product/conops.md#limitations]]
> Our developer tests cover the flight control and video applications' validation: out-of-limit
> routes and malformed files are refused with a plain message and the detail goes to the admin
> log. The planner's validation is the vendor's; we have only its release notes and never tested
> it independently. DT-1 showed the GDT rejecting commands from an unkeyed terminal; the GDT logs
> the attempt locally only. The aircraft link has no IP route to the uplink. The image has no
> mail or chat client. The video application refuses export without a valid release marking.

### Q3 {#INT-092.Q3}
Asked of: PER-DEV · Task: A-3 · Control focus: sr-3.3, sr-4, sr-5, sr-5.2, sr-10, sr-11, sr-11.1, sr-11.2
Show the integrator's supply chain records for the six kits.

**A3 {#INT-092.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#physical]]
> The build records list serial numbers and firmware versions for every kit; all purchases are
> from original manufacturers or authorized resellers under the contract, which has the
> secure-development, notification and signed-delivery clauses. Receipt inspection sheets record
> seal checks for all six kits; our counterfeit-awareness training roster is current, and
> repairs return only through us.
