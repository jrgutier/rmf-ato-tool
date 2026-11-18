---
interview_id: INT-070
run_id: 20261118-synthetic-01
task: S-1
persona: PER-ISSM
date: 2026-11-18
topics: [baseline selection, NSS privacy control baseline, organizational additions, requirements not covered, capabilities]
---
# INT-070 — S-1 — PER-ISSM

### Q1 {#INT-070.Q1}
Asked of: PER-ISSM · Task: S-1
Does the selected baseline follow from the approved categorization, and how do you want it recorded?
**A1 {#INT-070.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[ART-ORG-CONTEXT]] [[INT-068.A4]]
> Yes. The AODR approved moderate confidentiality, moderate integrity and low availability with
> the Privacy Overlays' Moderate and Accountability sets. The Component selects controls under
> CNSSI 1253, so the baseline is the per-objective selection: the Appendix D controls marked for
> confidentiality moderate, integrity moderate and availability low, joined, plus the NSS privacy
> control baseline, then the two overlay sets. No high-water mark: that is only the fallback when
> CNSSI 1253 cannot be used. For this dry run the program cut the set to the 50 controls in
> run.yaml; the baseline ID the tool generates carries that subset size, and that ID is what I
> enter in the registration record and in the facts.

### Q2 {#INT-070.Q2}
Asked of: PER-ISSM · Task: S-1
The P-4 record (INT-010.A1) says the Component's systems are NSS and directs the NSS privacy control baseline for every NSS, but the CIO determined at P-16 that EFRAS is not an NSS. Does the NSS privacy control baseline apply to EFRAS?
**A2 {#INT-070.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-010.A1]] [[INT-051.A1]] [[ART-CAT]] [[INT-068.A3]]
> It applies, but not for the reason INT-010.A1 gives. The Component categorizes and selects
> controls for every DoD system under CNSSI 1253, because DoDI 8510.01 tells Component heads to,
> NSS or not. CNSSI 1253's selection procedure has two parts in its S-1: the security baseline for
> the categorization, and the NSS privacy control baseline as a default. We take the procedure
> whole; I am not going to drop a privacy default from a system that holds 30,000 people's PII
> because its owner proved it is not an NSS. The words "its systems are national security
> systems" in INT-010.A1 are wrong for EFRAS, as the AODR noted at C-3; correcting the board's
> record is the risk executive's job, not mine, and the selection does not rest on it. I want the
> privacy officer to confirm she agrees before this goes in the artifact.

### Q3 {#INT-070.Q3}
Asked of: PER-ISSM · Task: S-1
Which organizational additions apply at selection: an organizationally tailored baseline, directed overlays, DoD values?
**A3 {#INT-070.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[INT-010.A2]]
> No tailored baseline and no CSF profile: the Component has none. The risk board directs the
> Privacy Overlays for every PII system, and those are already on the categorization. No other
> overlay applies. The DoD assignment values come in at tailoring and in the plan, as parameter
> values, not as extra controls. Nothing else is added at selection.

### Q4 {#INT-070.Q4}
Asked of: PER-ISSM · Task: S-1
Which requirements of ART-REQ does the selected set not obviously cover?
**A4 {#INT-070.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[product/conops.md#limitations]]
> Against the 50 controls, five stand out. REQ-04, the ingest signature, checksum and schema
> checks: input validation is SI-10, which the subset leaves out; SC-8 and developer testing only
> cover part of it. REQ-09, CUI marking on pages and exports: the marking controls (MP-3, AC-16)
> are not in the subset. REQ-11, standards from the DoD IT Standards Registry, and REQ-13,
> measurable and traced requirements: those sit in acquisition controls (SA-4, SA-8) that are not
> in the subset. REQ-12, Section 508 accessibility, has no SP 800-53 control at all; it is a
> design requirement the program verifies by test. REQ-14's de-identification would be SI-19,
> also outside the subset; PT-2, PT-3 and SI-12 carry the minimization and the five-year purge.
> I want S-2 to look at each of these. Because the subset is fixed for the dry run, I expect the
> answer to be "leave it, note it", not new controls.

### Q5 {#INT-070.Q5}
Asked of: PER-ISSM · Task: S-1
Did the organization define any security or privacy capabilities ahead of selection that controls should be mapped to?
**A5 {#INT-070.A5}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]]
> No. Neither the Component's strategy nor our requirements define capabilities as sets of
> controls; the requirements in ART-REQ do that job, and S-3 traces controls to them. So there is
> no capabilities file.
