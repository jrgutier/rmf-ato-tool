---
interview_id: INT-038
run_id: 20261118-synthetic-01
task: P-14
persona: PER-DEV
date: 2026-11-18
topics: [forecast model, third-party and open-source components]
---
# INT-038 — P-14 — PER-DEV

### Q1 {#INT-038.Q1}
Asked of: PER-DEV · Task: P-14
**A1 {#INT-038.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#components]] [[product/conops.md#users]]
> The forecast job runs model v3, a gradient-boosted classifier trained on the pseudonymized
> training extract, which predicts part failures over 30 days. Its use-case risk is a wrong
> forecast: parts ordered for nothing, or a failure not flagged. It only advises maintenance
> officers, who decide in EMIS. Before v3 went to pre-production we measured precision and recall
> on a held-out year of data against the program's acceptance thresholds from the model test
> plan; we have no external AI benchmark standard beyond the DoD responsible AI toolkit checklist
> the program follows. In operation the job logs weekly precision against actual removals, and a
> drop below threshold opens a ticket to retrain. Bias here means squadrons or aircraft types with
> sparse data getting worse forecasts; we check performance per aircraft type at each retrain and
> tell the maintenance officers in the release notes where a forecast is weak.

### Q2 {#INT-038.Q2}
Asked of: PER-DEV · Task: P-14
**A2 {#INT-038.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/hw-sw-inventory.md#items]] [[product/test-results.md#pipeline-1-5]] [[product/conops.md#limitations]]
> example-imagelib 2.9.1 is a widely used open-source project with an active maintainer group,
> releases signed by its maintainers and pulled through the factory's mirror with checksum
> checks; it bundles two codec sub-libraries; it has a public security policy and fixed both
> high findings upstream, which we cannot pick up until the factory's base image carries the fix;
> its permissive license was reviewed by ARSPO counsel. The example web framework 4.2 is a large,
> foundation-governed project with long-term support to 2028, signed releases, a published
> security process and a permissive license; no open findings. The factory base image is
> government software, signed by the factory and rebuilt monthly. Nothing in the stack is under a
> foreign adversary's control as far as the factory's provenance checks show, and no NIAP-validated
> product applies to these components.
