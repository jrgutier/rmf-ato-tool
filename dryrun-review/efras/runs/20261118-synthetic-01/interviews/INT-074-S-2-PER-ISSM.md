---
interview_id: INT-074
run_id: 20261118-synthetic-01
task: S-2
persona: PER-ISSM
date: 2026-11-18
topics: [overlays, scoping, compensating controls, parameter values, supplementation, baseline assumptions, assurance]
---
# INT-074 — S-2 — PER-ISSM

### Q1 {#INT-074.Q1}
Asked of: PER-ISSM · Task: S-2
Which overlays apply, and do any two of them conflict over a control?
**A1 {#INT-074.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-073.A2]]
> The Privacy Overlays' Moderate set and the Accountability set, as approved at C-3; nothing else.
> They are two sets of the same overlay and both only select controls in our set, so there is no
> conflict to take to the AO and the privacy officer.

### Q2 {#INT-074.Q2}
Asked of: PER-ISSM · Task: S-2
Does any baseline control not apply to EFRAS's technology, environment or mission, so that it could be scoped out? Is there a control the system cannot implement that needs a compensating control?
**A2 {#INT-074.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]] [[product/architecture.md#physical]] [[product/conops.md#limitations]]
> Nothing is scoped out. Every one of the 50 has a home: the physical and media controls live with
> the cloud provider, and maintenance is the engineers' remote console work, so MA-4 applies. The
> nearest thing to a compensating control is the two FIDO2 break-glass accounts, but IA-2 is still
> met with multi-factor authentication; it is a deviation from the CAC policy that the AO accepts
> at authorization, not a baseline control we cannot implement. So no compensating action. The
> audit retention, the untested failover and the PIA are gaps in controls we keep, and they go to
> the plan as partial and to the POA&M, not out of the baseline.

### Q3 {#INT-074.Q3}
Asked of: PER-ISSM · Task: S-2
Which organization-defined parameter values do you set now, for the controls where the Privacy Overlays or the Component assign a value?
**A3 {#INT-074.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[product/architecture.md#identity]] [[product/architecture.md#configuration]] [[product/architecture.md#network]] [[INT-017.A1]]
> The ones the overlay assigns, plus the retention the Component requires. AC-2: notify the
> account managers and the ISSO within 24 hours when an account is no longer needed, a user leaves
> or transfers, or need-to-know changes; review accounts quarterly, which is stricter than the
> overlay's annual minimum and is the Component's account review frequency. CM-2: review the
> baseline configuration at least annually and at each release, and whenever a change touches
> the safeguards in the PIA or the SORN. CM-3: our configuration control board is the change
> control element; it meets monthly and whenever a change touches PIA or SORN safeguards, and
> every major release goes to it. SC-8: confidentiality and integrity. SC-12: keys generated,
> stored and destroyed centrally in the provider's key service under program-owned keys,
> following SP 800-57. SC-28: confidentiality and integrity of the PII and all CUI at rest in the
> database, object storage and backups. AU-11: one year. We do not meet that today, 90 days in our
> store, but the value is the requirement; the gap is the plan's and the POA&M's. MP-6 and PE-3
> carry the provider's values, since they are inherited whole.

### Q4 {#INT-074.Q4}
Asked of: PER-ISSM · Task: S-2
For the requirements S-1 listed as not obviously covered, do you supplement the baseline?
**A4 {#INT-074.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-BASELINE]] [[INT-070.A4]] [[ART-RA]]
> No additions. In a real run I would add SI-10 for REQ-04 and SI-19 for REQ-14, and I would want
> MP-3 for REQ-09; those risks are real (VUL-01 is the de-identification weakness). But the dry run
> fixed the set at 50 and every control in it gets a statement and an assessment; an addition
> outside it would not survive the subset. So I record the gaps here and in the baseline artifact,
> the de-identification gap goes to the POA&M through RA-8 and PT-3, and the next real selection
> adds them. REQ-11, REQ-12 and REQ-13 are acquisition and design requirements verified by the
> program's own tests and reviews; no security control is missing for them.

### Q5 {#INT-074.Q5}
Asked of: PER-ISSM · Task: S-2
Do the assumptions under the SP 800-53B and CNSSI 1253 baselines hold for EFRAS, and do any of the additional situations apply?
**A5 {#INT-074.A5}** respondent: simulated · tag: SIMULATED · basis: [[ART-RA]] [[ART-CAT]] [[ART-SD]] [[product/conops.md#information]]
> They all hold. The data is persistent (five years in the database), the system is multi-user
> with about 3,000 users, users may not see each other's squadrons, it is networked and general
> purpose in the sense the baselines mean, and the program, ERST and the providers carry the
> controls. Insider threats and advanced persistent threats are in our risk assessment as
> threat sources, and the Component wants the NSS practices beyond NIST, which is why we select
> under CNSSI 1253. Of the three situations the baselines do not address: no classified
> information and no cross-domain connection, but the PII under the Privacy Act and the CUI do
> need protection that law and policy specify. The Privacy Overlays answer the PII part, with
> PT-2, PT-3 and RA-8 and the encryption controls; the CUI part is carried by SC-8 and SC-28 and,
> outside the subset, by the marking controls.

### Q6 {#INT-074.Q6}
Asked of: PER-ISSM · Task: S-2
Are additional assurance-related controls needed to reach the trustworthiness the system requires?
**A6 {#INT-074.A6}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[product/test-results.md#pipeline-1-5]]
> No. The level of assurance we need is moderate, and it comes from the software factory's
> automated evidence on every release, SA-11's developer testing and the supply chain controls in
> the set. A decision-support system at moderate does not need more assurance controls than the
> baseline brings.
