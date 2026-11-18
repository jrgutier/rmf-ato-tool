---
interview_id: INT-172
run_id: 20261118-synthetic-01
task: A-3
persona: PER-DEV
date: 2026-12-03
topics: [report container vulnerabilities and release 1.5.2, developer testing and the REQ-11 and REQ-12 procedures, image admission and dependency pinning]
---
# INT-172 — A-3 — PER-DEV

### Q1 {#INT-172.Q1}
Asked of: PER-DEV · Task: A-3 · Control focus: ra-5, si-2
Where are the two high findings in the report container, and what does the fix depend on?
**A1 {#INT-172.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/conops.md#limitations]] [[product/test-results.md#pipeline-1-5]] [[product/architecture.md#updates]]
> Both are in example-imagelib 2.9.1 inside efras-report, found by the dependency and image scans
> on 2026-10-20. Release 1.5.1 did not touch them. The upstream fix is out, but we may only build
> from the software factory's hardened base image, and the one carrying the fix is late; release
> 1.5.2 is planned for 2026-12-10 once it arrives. The tickets show the due date of 2026-11-19
> passed. I cannot show you 1.5.2 in pre-production yet.

### Q2 {#INT-172.Q2}
Asked of: PER-DEV · Task: A-3 · Control focus: sa-11 (APR-001, APR-002)
Show me the test and evaluation plan, the evidence of the DT-2 cases you re-ran with us, and anything that verifies REQ-11 and REQ-12.
**A2 {#INT-172.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/test-results.md#pipeline-1-5]] [[product/test-results.md#pentest]]
> The plan is in the repository and covers security and privacy testing: unit and integration
> on every build, system and regression in each DT event, with the API scoping and export paths
> as the privacy cases. The pipeline keeps every build's results and DT-2 has its report; the
> twelve cases you re-ran gave the DT-2 results again. Flaws are tickets with a severity and due
> date and close only on a passing retest, as PT-1 did. Open: the two report container highs and
> the PT-3 retest. We have never tested REQ-11 or REQ-12; I have no standards list checked
> against the registry and no accessibility report to give you.

### Q3 {#INT-172.Q3}
Asked of: PER-DEV · Task: A-3 · Control focus: sr-3, sr-11
How does an image or a dependency get into the cluster, and what stops a counterfeit one?
**A3 {#INT-172.A3}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#configuration]] [[product/test-results.md#pipeline-1-5]] [[ART-SVCA]]
> Only from the factory's signed hardened base images, built by the pipeline; dependencies are
> pinned by version and hash and pulled through the factory's artifact repository. The admission
> policy refuses an unsigned or unknown image, which passed in the 1.5.0 gates. If a signature
> or hash check fails we stop the release and report it to the factory, which reports to the
> source and the Component's supply chain office, and we tell the ISSM and the CSSP.
