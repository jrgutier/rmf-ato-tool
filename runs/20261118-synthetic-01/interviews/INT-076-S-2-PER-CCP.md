---
interview_id: INT-076
run_id: 20261118-synthetic-01
task: S-2
persona: PER-CCP
date: 2026-11-18
topics: [baseline controls the providers cover, provider parameter values]
---
# INT-076 — S-2 — PER-CCP

### Q1 {#INT-076.Q1}
Asked of: PER-CCP · Task: S-2
Speaking for Example GovCloud IL4 region: which parameter values apply to the controls EFRAS inherits from you whole, PE-3 and MP-6?
**A1 {#INT-076.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-071.A1]] [[product/architecture.md#physical]]
> For Example GovCloud IL4 region. Our values are in our authorized security plan: badge and
> biometric access at every data center entry, and media sanitized by NIST SP 800-88 purge or
> destruction before it leaves our control, which is a FIPS-validated technique as the Privacy
> Overlay asks. EFRAS records them as ours; it sets none of its own for those two.

### Q2 {#INT-076.Q2}
Asked of: PER-CCP · Task: S-2
Speaking for each provider: do the baseline controls stay in EFRAS's baseline where you cover part of them?
**A2 {#INT-076.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-071.A2]] [[INT-071.A3]] [[INT-071.A4]]
> Yes, all of them. For Example Enterprise Cloud Access Point, SC-7 and SI-4 stay; for Example
> Software Factory, SA-11, SR-3 and SR-11 stay. Inheriting part of a control does not take it out
> of your baseline: you still write your side in your plan, and S-3 records who does what.
