---
interview_id: INT-036
run_id: 20261118-synthetic-01
task: P-14
persona: PER-PRIV
date: 2026-11-18
topics: [privacy risk to individuals, legal requirements, OMB A-130, Privacy Act, PIA status]
---
# INT-036 — P-14 — PER-PRIV

### Q1 {#INT-036.Q1}
Asked of: PER-PRIV · Task: P-14
**A1 {#INT-036.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pii]] [[product/conops.md#limitations]] [[product/test-results.md#pentest]]
> The processing is the bulk ingest of about 30,000 maintainers' records, kept five years, used
> to show qualifications and join actions to people, and shared in pseudonymized form with
> analysts and data scientists. The red team re-identified records from 50 DoD ID numbers, so
> exposure of an export is exposure of named people: phishing, identity misuse and embarrassment
> from qualification gaps. Alteration would show a maintainer as unqualified. I rate the risk to
> individuals moderate until release 1.6 salts the pseudonyms.

### Q2 {#INT-036.Q2}
Asked of: PER-PRIV · Task: P-14
**A2 {#INT-036.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-029.A3]] [[INT-029.A4]]
> OMB A-130 applies, as to every federal system. The privacy baseline and overlays cover most of
> it; what they leave to us is the A-130 Appendix II expectation that de-identification is
> effective before data is treated as non-PII, and the minimization review of the exports. The
> Privacy Act applies because the records are retrieved by DoD ID number from a system of
> records: use only for the purposes the SORN states, accounting of disclosures, and no disclosure
> outside routine uses. A contractor builds the system but does not operate the system of
> records. The FIPPs were each considered in the draft PIA.

### Q3 {#INT-036.Q3}
Asked of: PER-PRIV · Task: P-14
**A3 {#INT-036.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pia]] [[product/conops.md#limitations]]
> The PIA on DD Form 2930 is drafted, version 0.9 of 2026-09-30. The PM coordinated it through the
> ISSM on 2026-09-22, through my office on 2026-09-30 and with the records office on 2026-09-28.
> It is not complete: my office's question on the de-identified exports is open, so neither the
> CISO's review nor mine has happened and the CIO has not approved it. Our plan is my review and
> the CISO's on 2027-01-20 after the 1.6 design is fixed, CIO approval on 2027-01-25, submission
> to the DoD CIO and section 1 publication on the Component's public PIA page the same week.
> Those are planned dates, not events.
