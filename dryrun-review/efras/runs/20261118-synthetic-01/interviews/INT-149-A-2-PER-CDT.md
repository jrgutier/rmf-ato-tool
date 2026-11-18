---
interview_id: INT-149
run_id: 20261118-synthetic-01
task: A-2
persona: PER-CDT
date: 2026-11-18
topics: [test strategy, developmental test events, cybersecurity test events, test conditions]
---
# INT-149 — A-2 — PER-CDT

### Q1 {#INT-149.Q1}
Asked of: PER-CDT · Task: A-2 · Control focus: ca-2, sa-11 (test strategy and DT events)
What test planning document governs EFRAS, who approved it, and which developmental cybersecurity test events has it planned and held?
**A1 {#INT-149.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#top]] [[product/test-results.md#pipeline-1-5]] [[product/test-results.md#dt-2]] [[product/test-results.md#stig-scan]] [[product/test-results.md#pentest]]
> EFRAS is on the software acquisition pathway, so we have a test strategy, not a TEMP: version
> 1.1 of 2026-02-16, approved by the Component on 2026-02-27, before the program entered
> execution on 2026-03-02. It is not on DOT&E or USD(R&E) oversight. It sets cybersecurity test
> objectives (confidentiality of maintainer PII, squadron scoping, integrity of EMIS extracts,
> recovery within the objectives) and entry and exit criteria for each release, under a
> developmental evaluation framework, with an operational evaluation framework the Component
> operational test agency added for the MVCR. Held so far, all on release 1.5.0 in
> pre-production with synthetic data and the three pilot squadrons: the pipeline security gates
> on every build (cooperative vulnerability identification, run by ERST with my team, 2026-10-20);
> DT-2 from 2026-10-06 to 2026-10-17, my team's functional cybersecurity tests; the STIG scan of
> 2026-10-22, witnessed by the SCA; and the component red team's penetration test from
> 2026-10-27 to 2026-10-31, against the externally reachable surface from NIPRNet through the
> access point. That test did not set out to evaluate the CSSP's detection and response, so the
> strategy plans a second penetration and exploitation test with the CSSP in play during the
> assessment window. Pre-production is built from the same templates as production and reached
> by the pilot squadrons over NIPRNet, so it represents production; DT-2 did not test the
> regional failover.

### Q2 {#INT-149.Q2}
Asked of: PER-CDT · Task: A-2 · Control focus: ca-2 (sharing test events with the assessment)
Can the assessment team share your events, and what data will they produce?
**A2 {#INT-149.A2}** respondent: simulated · tag: SIMULATED · basis: [[INT-147.A2]]
> Yes. The SCA has all DT-2 test cards and logs and may re-run any of them in pre-production; my
> team will support the re-performance on 2026-12-02. The penetration test in the assessment
> window is a shared event: the red team runs it, the SCA observes, the CSSP responds, and the
> report goes to the SCA, me and the operational test agency.
