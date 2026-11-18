---
interview_id: INT-106
run_id: 20261118-synthetic-01
task: S-4
persona: PER-PRIV
date: 2026-11-18
topics: [authority to process PII, purposes of PII processing, de-identified exports]
---
# INT-106 — S-4 — PER-PRIV

### Q1 {#INT-106.Q1}
Asked of: PER-PRIV · Task: S-4 · Control focus: pt-2
Which authority permits EFRAS to process maintainer PII, where is it documented, and how is processing kept to what it permits?
**A1 {#INT-106.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#authority]] [[product/privacy.md#pii]] [[INT-080.A1]]
> The authority is the Component's maintenance-records authority, cited in the existing
> Component SORN for aviation maintenance records and in the draft PIA. We confirmed by e-mail
> on 2026-08-19 that the SORN covers EFRAS's records. The processing it permits is to receive
> the maintainer data in the EMIS extract, store it, display qualification coverage per work
> center and join actions to people. EFRAS collects nothing from individuals and does not write
> back. The schema holds only the five data elements the SORN names; the ingest worker drops any
> other field in the extract, and a new element needs my review through the change process. The
> privacy office keeps the SORN and the authority; the program keeps the data inventory.

### Q2 {#INT-106.Q2}
Asked of: PER-PRIV · Task: S-4 · Control focus: pt-3
Which purposes are documented, are they in public notices, and how is processing kept compatible with them?
**A2 {#INT-106.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/privacy.md#pii]] [[product/privacy.md#minimization]] [[product/conops.md#limitations]] [[product/test-results.md#pentest]]
> Two purposes: showing qualification coverage per work center, and joining maintenance actions
> to the people who performed them for readiness analysis. Both are in the SORN's purpose and
> routine-use sections, which are public, and in the draft PIA. Fleet analysts' exports and the
> data scientists' training extract are allowed only de-identified, because neither purpose
> needs identities there. That is where processing goes beyond the purposes today: the exports
> keep an unsalted hash of the DoD ID number, and the red team re-identified records with 50 IDs
> (PT-2). Until release 1.6 (2027-01-15) brings salted, rotated pseudonyms, the exports are not
> restricted to compatible processing. For changes, the CCB routes any change that touches PII
> to me, and the PIA and SORN review in CM-3 catches a new purpose before release.
