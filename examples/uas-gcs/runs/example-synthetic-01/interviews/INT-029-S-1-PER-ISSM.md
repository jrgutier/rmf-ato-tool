---
interview_id: INT-029
run_id: example-synthetic-01
task: S-1
persona: PER-ISSM
date: 2026-10-29
topics: [baseline selection, privacy overlay, requirements not covered]
---
# INT-029 — S-1 — PER-ISSM

### Q1 {#INT-029.Q1}
Asked of: PER-ISSM · Task: S-1
Context: `rmf baseline resolve` produced baseline.json with method cnssi1253 from the approved
categorization and the Privacy Overlay ACCT control set.
**A1 {#INT-029.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-028.A3]]
> The approved categorization is moderate for confidentiality, integrity and availability, so
> the starting point is the union of the CNSSI 1253 Appendix D moderate columns for the three
> objectives, plus the NSS privacy control baseline, which CNSSI 1253 makes a default for every
> NSS. On top of that goes the Privacy Overlay Accountability set only, as the AODR approved. I
> confirm the baseline ID the tool recorded is the one we select; there is no classified or space
> overlay, as the categorization already ruled them out.

### Q2 {#INT-029.Q2}
Asked of: PER-ISSM · Task: S-1
**A2 {#INT-029.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[ART-REQ]]
> The organization has no tailored baseline of its own, so nothing is added at selection. Looking
> at the requirements list, most map straight onto baseline controls. Three need a deliberate
> look in tailoring: REQ-04 (signed bundles only) leans on software integrity and signed-component
> controls, which we should confirm are selected at the right enhancement; REQ-07 (individual
> authenticators on the GDT management service) needs the identification controls applied to a
> device interface the vendor ships with a shared account; and REQ-10 (a spare station within
> 4 hours) has to be written into the contingency plan assignment values, not left to the default.

### Q3 {#INT-029.Q3}
Asked of: PER-ISSM · Task: S-1
**A3 {#INT-029.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]]
> REQ-09 (PII minimization in account and audit records) is covered by the privacy baseline and
> the ACCT set. I see nothing in the requirements that the baseline leaves without any control.
