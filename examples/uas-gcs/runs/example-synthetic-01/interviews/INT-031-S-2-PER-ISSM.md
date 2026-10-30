---
interview_id: INT-031
run_id: example-synthetic-01
task: S-2
persona: PER-ISSM
date: 2026-10-29
topics: [overlays, scoping, compensating controls, parameter values, supplementation]
---
# INT-031 — S-2 — PER-ISSM

### Q1 {#INT-031.Q1}
Asked of: PER-ISSM · Task: S-2
**A1 {#INT-031.A1}** respondent: simulated · tag: SIMULATED · basis: [[ART-CAT]] [[INT-028.A3]] [[INT-015.A1]]
> Only the Privacy Overlay Accountability set applies; the privacy officer's determination stands
> behind it and there is no second overlay, so there is no overlay conflict to resolve.

### Q2 {#INT-031.Q2}
Asked of: PER-ISSM · Task: S-2
**A2 {#INT-031.A2}** respondent: simulated · tag: SIMULATED · basis: [[ART-BASELINE]] [[ART-RA]]
> Scoping: I am not removing anything. Every baseline control has some part that applies to a
> fielded station, even the alternate-site and contingency controls, which we meet with spare
> kits. Compensating: none either. Where the station cannot do something today, such as the
> shared account on the GDT management service, the control stays in and S-4 records the gap as
> planned so the risk reaches the POA&M; I will not hide it behind a compensating control.

### Q3 {#INT-031.Q3}
Asked of: PER-ISSM · Task: S-2
**A3 {#INT-031.A3}** respondent: simulated · tag: SIMULATED · basis: [[ART-REQ]] [[ART-RA]] [[INT-029.A2]]
> Supplementation: add code authentication under software integrity, si-7.15, because REQ-04 and
> the removable-media and update risks in the risk assessment say only signed bundles install.
> The signed-component control cm-14 is already in the baseline; set its components to the
> integrator's quarterly update bundle and the GDT firmware.

### Q4 {#INT-031.Q4}
Asked of: PER-ISSM · Task: S-2
**A4 {#INT-031.A4}** respondent: simulated · tag: SIMULATED · basis: [[ART-ORG-CONTEXT]] [[INT-007.A1]] [[INT-018.A3]]
> Parameter values: account reviews quarterly, per the organization's monitoring strategy.
> Vulnerability scans at least monthly when connected and on every reconnection. Alternate
> processing: a spare station takes over mission planning and flight control within 4 hours.
> The contingency plan is reviewed yearly. Audit review on the station weekly by the ISSO while
> disconnected; the enclave reviews what reaches its collector.
