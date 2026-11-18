---
interview_id: INT-128
run_id: 20261118-synthetic-01
task: S-4
persona: PER-DEV
date: 2026-11-18
topics: [pipeline, provenance, SBOM, AI-assisted development, cyber test events]
---
# INT-128 — S-4 — PER-DEV

### Q1 {#INT-128.Q1}
Asked of: PER-DEV · Task: S-4 · Control focus: sa-11, sr-3, sr-11, cm-3 (software)
How is EFRAS software built and deployed, what provenance and SBOM does the build produce, and is AI used in development?
**A1 {#INT-128.A1}** respondent: simulated · tag: SIMULATED · basis: [[INT-111.A1]] [[INT-116.A1]] [[product/architecture.md#configuration]] [[product/test-results.md#pipeline-1-5]]
> All EFRAS code and infrastructure is built on the Example Software Factory pipeline, which
> holds its own ATO: source in the factory repository, every merge reviewed, then static,
> dependency, image, dynamic and policy gates. The pipeline signs every image and writes a
> signed provenance attestation in the SLSA provenance format; the cluster admits only signed
> images. Production deployment needs a manual approval by the ISSO after the gates pass. The
> build generates a CycloneDX SBOM for each image with our code, the base image packages,
> third-party libraries and their transitive dependencies; the managed database and services
> are recorded from the provider's published component lists. SBOMs are stored with each
> release and rescanned daily. We do not use AI tools to write or test EFRAS code; the
> program has not approved any. The forecast model is our own statistical model, not
> generative AI.

### Q2 {#INT-128.Q2}
Asked of: PER-DEV · Task: S-4 · Control focus: sa-11, ca-8
Which cyber test events have been run and which are planned?
**A2 {#INT-128.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/test-results.md#dt-2]] [[product/test-results.md#pentest]]
> DT-2, the developmental test event of 2026-10-06 to 2026-10-17, run by the program's
> government test lead with ERST, and the penetration test of 2026-10-27 to 2026-10-31 by the
> Component's government red team, independent of the developer. The next independent cyber
> event is the retest of PT-3 before the assessment, then a government cyber test with each
> major release.
