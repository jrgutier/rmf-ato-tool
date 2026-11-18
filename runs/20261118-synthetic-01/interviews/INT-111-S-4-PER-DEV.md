---
interview_id: INT-111
run_id: 20261118-synthetic-01
task: S-4
persona: PER-DEV
date: 2026-11-18
topics: [developer testing and evaluation, flaw remediation, supply chain protections, anti-counterfeit]
---
# INT-111 — S-4 — PER-DEV

### Q1 {#INT-111.Q1}
Asked of: PER-DEV · Task: S-4 · Control focus: sa-11
How does ERST test and evaluate EFRAS, what evidence does it keep, and how are flaws fixed?
**A1 {#INT-111.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#pipeline-1-5]] [[product/test-results.md#dt-2]] [[product/test-results.md#pentest]] [[product/conops.md#limitations]] [[INT-084.A4]]
> Our test and evaluation plan sits in the repository: unit and integration tests on every
> pipeline build, system and regression tests in each developmental test event before a
> release, plus the factory's static, dependency, image and dynamic scans on every build. Unit
> coverage of the API's role checks is complete; DT-2 covered all five roles, scoping, session
> timeout, inactivity disable, export audit, ingest tamper and restore. The pipeline keeps the
> evidence per build, and each DT event has a report. Flaws become tickets with a severity and a
> due date, the fix goes through the same pipeline, and the ticket closes only on a passing
> retest; PT-1 went that way. Open: the two highs in the report image wait on the factory, PT-3
> waits for its retest, and we have not tested against the IT standards registry profile or for
> Section 508; no result exists for either.

### Q2 {#INT-111.Q2}
Asked of: PER-DEV · Task: S-4 · Control focus: sr-3, sr-11
What protects the EFRAS build and deployment against supply chain weaknesses and counterfeit components?
**A2 {#INT-111.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/architecture.md#updates]] [[product/test-results.md#pipeline-1-5]] [[INT-071.A3]]
> Containers start only from the factory's hardened base images, which the factory signs; the
> cluster's admission policy refuses any unsigned or unknown image, and it passed that test in
> 1.5.0. We pin every dependency by version and hash and pull it only through the factory's
> artifact repository, so nothing comes from a public mirror; PT-3 showed the sandbox could, and
> that allow-list was narrowed on 2026-11-03. Worker nodes use the provider's hardened node image.
> We buy no hardware. If the scan or the signature check flags a tampered or counterfeit
> component, we stop the release and report it to the factory, the ISSM and the CSSP; the factory
> reports it to its source.
