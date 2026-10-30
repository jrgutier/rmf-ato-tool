---
interview_id: INT-055
run_id: example-synthetic-01
task: S-4
persona: PER-ISSE
date: 2026-10-29
topics: [si family, integrity, boot protection, input validation, information handling]
---
# INT-055 — S-4 — PER-ISSE

### Q1 {#INT-055.Q1}
Asked of: PER-ISSE · Task: S-4 · Control focus: si-7, si-7.1, si-7.7, si-7.8, si-7.9, si-7.10, si-7.15
How are software, firmware and boot integrity protected and checked?

**A1 {#INT-055.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#configuration]] [[product/architecture.md#components]]
> Only signed code installs: the station checks the signature on the integrator's quarterly
> bundle and on each GDT firmware image before install, and rejects anything unsigned or
> altered. The start-up compliance check, run again before each mission upload, verifies the
> image files and settings against the baseline; a mismatch is logged as an integrity event,
> raises a local alert, and the ISSO treats it under the incident procedure. The laptop uses
> secure boot with the TPM measuring the boot chain, and the firmware setup is
> password-protected, so firmware changes come only through signed bundles.

### Q2 {#INT-055.Q2}
Asked of: PER-ISSE · Task: S-4 · Control focus: si-10, si-10.3, si-10.6, si-11, si-15, si-16
What do the applications and the image enforce for input, errors, output and memory?

**A2 {#INT-055.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/conops.md#limitations]]
> The flight control application checks every command and route against the aircraft's limits
> before it uploads, and the planner and video applications validate imported files and
> fields. Both the flight control application and the planner behave predictably on bad input:
> the input is refused and the operator sees a plain message. Error messages show no internal
> detail; detail goes to the local log for the admin role. The video application only exports
> products with a valid release marking. The image enables data execution prevention and
> address randomization for all processes. One caveat: the planner's input handling is the
> vendor's and has not been independently assessed (its hardening was done by hand).

### Q3 {#INT-055.Q3}
Asked of: PER-ISSE · Task: S-4 · Control focus: si-12, si-12.1, si-12.3, si-18, si-18.1, si-18.3, si-18.4, si-18.5
How is station information kept and disposed of, and how are the user names kept accurate?

**A3 {#INT-055.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#information]] [[product/architecture.md#logging]] [[product/architecture.md#identity]]
> Mission products and logs are kept by the Component records schedule: logs 90 days locally,
> products until transferred to the intelligence system and then deleted. The only personal
> data is user names in accounts and audit records; the station stores no other personal
> fields. Names come from the brigade directory at each CAC sign-in, so a correction made in
> the directory reaches the station at the next sign-in; users ask the directory owner for
> corrections and the directory notifies them. Retired stations and drives are sanitized under
> the Component procedure.
