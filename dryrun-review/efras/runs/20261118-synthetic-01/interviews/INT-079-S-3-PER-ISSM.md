---
interview_id: INT-079
run_id: 20261118-synthetic-01
task: S-3
persona: PER-ISSM
date: 2026-11-18
topics: [designation common, hybrid, system-specific, program management; requirement traceability]
---
# INT-079 — S-3 — PER-ISSM

### Q1 {#INT-079.Q1}
Asked of: PER-ISSM · Task: S-3
Which controls are common, which hybrid, and from which provider?
**A1 {#INT-079.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-071.A1]] [[INT-071.A2]] [[INT-071.A3]] [[INT-071.A4]] [[INT-072.A1]] [[ART-ORG-CONTEXT]]
> Common: PE-3 and MP-6 from Example GovCloud IL4 region, nothing else. Hybrid: SI-2 and CP-9 with
> the cloud region; SC-7 with the access point; SA-11, SR-3 and SR-11 with the software factory;
> AU-6, IR-4, IR-6, RA-5 and SI-4 with the CSSP. SI-4 is shared with the access point too, but the
> CSSP carries most of it, so I record the CSSP as its provider and the access point's inspection
> in the narrative. I use the provider names exactly as the Component's common control list gives
> them.

### Q2 {#INT-079.Q2}
Asked of: PER-ISSM · Task: S-3
What about AT-2, PM-5 and the control families' policy controls?
**A2 {#INT-079.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[INT-006.A2]] [[ART-REG]]
> AT-2 is hybrid with the Component privacy office: its annual privacy training is the common part,
> our own awareness briefing for EFRAS users is ours. PM-5 is the Component's system inventory,
> kept by the CIO's office in eMASS, where EFRAS is registered; it is an organizational program
> management control, not something a component of ours implements. AC-1 is system-specific: the
> Component's policy is the parent, but EFRAS writes its own access control procedures and nobody
> offers them for inheritance.

### Q3 {#INT-079.Q3}
Asked of: PER-ISSM · Task: S-3
Which requirement of ART-REQ does each control satisfy, and which requirements does no control in the set satisfy?
**A3 {#INT-079.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[ART-BASELINE]] [[INT-074.A4]]
> Most trace cleanly: REQ-01 to IA-2, IA-5, AC-2 and AC-17; REQ-02 to AC-2, AC-3, AC-6 and MA-4;
> REQ-03 to SC-8, SC-12 and SC-28; REQ-04 partly to SC-8, CA-3 and SA-11; REQ-05 to the AU
> controls; REQ-06 to the contingency controls; REQ-07 to SA-11, SR-3, SR-11 and CM-3; REQ-08 to
> CM-2, CM-6, RA-5 and SI-2; REQ-10 to SC-7, AC-17 and CA-3; REQ-13 to PL-2, CA-2 and RA-3;
> REQ-14 to PT-3 and SI-12; REQ-15 to PT-2, PT-3 and AT-2; REQ-16 to RA-8. REQ-09, CUI marking,
> has no marking control in the set; SI-12 covers handling of output only in part, and I trace it
> there with that caveat. REQ-11, the standards registry, and REQ-12, Section 508, have no control
> in the set, and REQ-12 has none in the catalog: they are verified by analysis and test, not by a
> security control. I will not pretend a control satisfies them. REQ-17 to REQ-19 are contract
> requirements; SR-3 carries REQ-17, SA-9 REQ-18 and AT-3 and PS-3 REQ-19.
