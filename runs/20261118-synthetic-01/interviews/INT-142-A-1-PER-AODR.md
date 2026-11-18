---
interview_id: INT-142
run_id: 20261118-synthetic-01
task: A-1
persona: PER-AODR
date: 2026-11-18
topics: [assessor selection, type of assessment, technical expertise, independence basis]
---
# INT-142 — A-1 — PER-AODR

### Q1 {#INT-142.Q1}
Asked of: PER-AODR · Task: A-1 · Control focus: ca-2 (control assessments)
Which assessor or assessment team do you select for EFRAS, for what type of control assessment, and on what technical expertise?
**A1 {#INT-142.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/stakeholders.md#roles]] [[ART-ORG-CONTEXT]] [[INT-134.A1]]
> Acting for the AO under my written delegation, on 2026-11-18 I select the business systems SCA
> team of the Component's independent assessment activity, the team the Component CISO has
> delegated the SCA role to. The assessment is security and privacy together: the system holds
> maintainer PII and the two Privacy Overlay variants apply, so one plan and one team cover both.
> The expertise I required, and the team has: Kubernetes on a DoD Impact Level 4 cloud region and
> the inheritance from it; the managed PostgreSQL service and its STIG; a CI/CD pipeline in an
> authorized software factory, signed images and dependency scanning; CAC sign-in through a SAML
> identity broker; web application testing of an API with per-squadron data scoping; and the
> Privacy Act, the PIA and the Privacy Overlay. I did not pick the developer's or the program's
> own testers, because they built or run what is being assessed.

### Q2 {#INT-142.Q2}
Asked of: PER-AODR · Task: A-1 · Control focus: ca-2, pt-2, pt-3, at-2 (independence of the selected team)
What makes the selected team independent of EFRAS, and who assesses the privacy controls?
**A2 {#INT-142.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/stakeholders.md#roles]] [[ART-SSP]]
> The assessment activity reports to the Component CISO, outside the PEO, ARSPO and the
> developer, so nobody in the system owner's chain rates or funds them; ARSPO does not contract
> them, they are a Component service. None of them designed, built or operates any EFRAS
> component. For privacy, the Component privacy office is itself a provider: it runs the SORN,
> privacy training and the review of PII processing behind at-2, pt-2 and pt-3. So the privacy
> office does not assess its own controls; the SCA team's privacy-trained assessor assesses the
> privacy controls under the methodology and metrics the privacy office set in the privacy plan,
> and the privacy officer, for the senior agency official for privacy, stays accountable and
> receives the privacy results.
