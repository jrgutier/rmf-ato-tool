---
interview_id: INT-151
run_id: 20261118-synthetic-01
task: A-2
persona: PER-AODR
date: 2026-11-18
topics: [assurance requirements, sampling direction, exclusions, reuse approval, third-party assessor, plan approval]
---
# INT-151 — A-2 — PER-AODR

### Q1 {#INT-151.Q1}
Asked of: PER-AODR · Task: A-2 · Control focus: all 50 baseline controls (assurance and direction)
What assurance do you, for the AO, need from the assessment, and what direction do you give the assessors on what and how much to sample?
**A1 {#INT-151.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[ART-RA]] [[ART-SSP]]
> Three assurance requirements, all mine for the AO. AR-001: for every control, enough to know it
> is implemented correctly and operating as intended, which means at least focused depth and
> coverage. AR-002: for the controls behind the moderate risks in the risk assessment, the
> exfiltration and re-identification scenario, and for every control the program itself calls
> partial, comprehensive depth and coverage, so the POA&M rests on what the assessors saw, not
> on the program's word. AR-003: for the two inherited controls, basic is enough against the
> provider's authorization package. On sampling I conferred with the SCA lead: sample each role
> at least once by interview; sample configuration at least two components per tier and every
> component that touches PII; take the specific objects that matter (the report service, the
> API's scoping check, the ingest filter, the sandbox egress, the break-glass accounts)
> besides a random draw; the factors are the three-week window, the funded ERST hours, and the
> fact that this is the first assessment before the MVCR.

### Q2 {#INT-151.Q2}
Asked of: PER-AODR · Task: A-2 · Control focus: ca-2 (exclusions, reuse, third-party assessor)
Are any controls excluded? Do you approve the reuse the SCA proposes, and do you accept the cloud provider's third-party assessor?
**A2 {#INT-151.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-147.A2]] [[INT-147.A3]] [[ART-ORG-CONTEXT]]
> No control is excluded: all 50 are assessed. I approve reusing the SCA-witnessed STIG scan of
> 2026-10-22 and the red team's penetration test with the PT-1 retest, with the SCA's own scan
> and the second penetration test as supplements; the PM and I agreed on that with the SCA
> today, 2026-11-18. I agree the pipeline gates, DT-2 and the account review are examined and
> partly re-performed rather than reused, as the AO asked. For the commercial cloud region I
> accept the accredited third-party assessment organization behind its DoD provisional
> authorization as acceptable to the AO, on 2026-11-18.

### Q3 {#INT-151.Q3}
Asked of: PER-AODR · Task: A-2 · Control focus: ca-2 (plan review and approval)
Having reviewed the SCA's plan, do you approve it for the AO?
**A3 {#INT-151.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-147.A1]] [[INT-147.A4]] [[INT-147.A5]] [[INT-148.A1]] [[INT-149.A1]]
> Yes. The SCA reviewed the plan and I approve it on 2026-11-18, acting for the AO under my
> delegation, which covers assessment plans. The methods are deep enough where it matters: the
> partial controls, the API scoping and the export re-identification get comprehensive testing,
> and the four items the program left to the assessor are named with dates. The schedule ends on
> 2026-12-11, which leaves time for the report, the POA&M and the risk analysis before the
> decision ahead of the 2027-02-01 deployment. One constraint: if the release 1.5.2 fixes land
> on 2026-12-10 as planned, the SCA verifies them only if time allows; otherwise they stay open
> findings with POA&M items.
