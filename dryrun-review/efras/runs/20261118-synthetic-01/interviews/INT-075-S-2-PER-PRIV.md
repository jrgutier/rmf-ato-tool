---
interview_id: INT-075
run_id: 20261118-synthetic-01
task: S-2
persona: PER-PRIV
date: 2026-11-18
topics: [privacy tailoring, Privacy Implementation Considerations, workforce privacy training assumption, privacy enhancing controls]
---
# INT-075 — S-2 — PER-PRIV

### Q1 {#INT-075.Q1}
Asked of: PER-PRIV · Task: S-2
Does the tailoring touch any privacy control, and does it leave a gap in compliance with privacy requirements or add privacy risk?
**A1 {#INT-075.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-074.A2]] [[INT-074.A4]] [[ART-REQ]] [[product/conops.md#limitations]]
> The tailoring removes nothing and substitutes nothing, so it takes no privacy control away and
> adds no privacy risk. The privacy values the ISSM set for AC-2, CM-2, CM-3, SC-8, SC-12 and SC-28
> are the overlay's or stricter, and I agree with them. There is a gap, but it does not come from
> tailoring: the dry-run set has no de-identification control, and the exports are
> re-identifiable today. That stays visible through RA-8 and PT-3 and goes to the POA&M; I do not
> want anyone to read "no gap" as "the exports are fine".

### Q2 {#INT-075.Q2}
Asked of: PER-PRIV · Task: S-2
Ten selected controls carry a Privacy Implementation Considerations checkmark in CNSSI 1253 Appendix D: AU-6, CM-6, IA-2, IA-5, PE-3, PS-3, PS-4, SC-7, SC-12 and SI-4. What do you find on each before it is implemented?
**A2 {#INT-075.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#logging]] [[product/architecture.md#identity]] [[product/architecture.md#network]] [[product/architecture.md#configuration]] [[product/architecture.md#physical]] [[ART-PIA]]
> AU-6: the weekly review reads users' names and DoD ID numbers; reviewers see only what the review
> needs, and misuse of PII found in review comes to my office. CM-6: settings such as log fields,
> export defaults and sandbox egress are design choices that decide how much PII leaves the
> system; the defaults must minimize it, and the sandbox egress wildcard must close. IA-2 and IA-5:
> the identity broker passes the DoD ID number in the assertion; EFRAS keeps it only as the
> account key and the audit identity, and the FIDO2 break-glass keys carry no personal data. PE-3:
> the provider's physical access records are about its own staff and stay with it. PS-3 and PS-4:
> screening and termination records of ERST staff stay with ERST and the security office, not in
> EFRAS. SC-7: PII must not flow to a system not authorized for it; the egress allow-list keeps
> the extracts inside, and the CSSP may receive log PII only under its agreement. SC-12: losing a
> key must not expose PII; the program-owned keys in the key service and their rotation meet
> that. SI-4: monitoring captures users' PII; notice is given at sign-in, the monitoring data is
> encrypted and the CSSP holds it under its agreement. No additional step beyond those, except
> the sandbox egress fix and the export pseudonyms already planned.

### Q3 {#INT-075.Q3}
Asked of: PER-PRIV · Task: S-2
The Privacy Overlay assumes the workforce completes privacy training and receives access permissions before accessing a system with PII. Does that hold for EFRAS?
**A3 {#INT-075.A3}** respondent: simulated · tag: SIMULATED · basis: [[INT-006.A2]] [[product/architecture.md#identity]]
> It holds. Component policy requires annual privacy training of all personnel, and role-based
> training before access for anyone handling bulk PII; EFRAS roles are requested and approved
> before the ISSO provisions them. The overlay's AC-2 value, disabling an account whose holder
> lets privacy training lapse, is recorded with the account management values.

### Q4 {#INT-075.Q4}
Asked of: PER-PRIV · Task: S-2
Do you want any of the Privacy Overlays' optional privacy enhancing controls tailored in, or AC-2(8)?
**A4 {#INT-075.A4}** respondent: simulated · tag: SIMULATED · basis: [[INT-074.A4]]
> Not in this dry run; the set is fixed. For the real selection I would recommend SI-19
> de-identification for the exports. AC-2(8), dynamic account management, is not selected, and I
> do not want it: the overlays justify leaving it out, and nothing here needs it.
