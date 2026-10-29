---
interview_id: INT-017
run_id: agent-skeleton
task: S-4
persona: PER-DEV
date: 2026-10-29
topics: [authentication enforcement, update bundles, flaw remediation]
---
# INT-017 — S-4 — PER-DEV

### Q1 {#INT-017.Q1}
Asked of: PER-DEV · Task: S-4 · Control focus: ia-2
**A1 {#INT-017.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#identity]] [[product/test-results.md#dt-2]]
> The console code refuses a remote sign-in unless the identity service returns a DoD PKI
> authentication and an approved group claim; DT-2 confirmed that users without an approved claim
> were refused. Local sign-ins lock for 30 minutes after five failures, and any session locks after
> 15 minutes idle; both passed in DT-2. Per-technician local accounts with smart-card login are a
> release 2.3 feature, planned for 2027-03, and are not in the current build.

### Q2 {#INT-017.Q2}
Asked of: PER-DEV · Task: S-4 · Control focus: si-2
**A2 {#INT-017.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#updates]] [[product/architecture.md#configuration]]
> We track flaws in the OS, collector, console and database from vendor advisories and our own
> scans, and fix them in a signed monthly update bundle that covers all four. Each bundle is built
> by the same pipeline as the baseline image and runs through our regression test on the
> pre-production units before release. The unit checks the bundle signature before it installs
> anything. Remote update over the uplink is planned for release 2.2 (2026-12); today a technician
> installs the bundle on site.

### Q3 {#INT-017.Q3}
Asked of: PER-DEV · Task: S-4 · Control focus: si-2
**A3 {#INT-017.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#vuln-scan]]
> At the 2026-09-30 scan, 10 of 12 units ran the 2026-09 bundle with no vulnerabilities found.
> `esg-north-01` and `esg-ridge-01` still ran the 2026-07 bundle, 63 days old, and showed 4 high and
> 9 medium vulnerabilities, all fixed in later bundles. The fixes existed; they had not reached
> those units.
