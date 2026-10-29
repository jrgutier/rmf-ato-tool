# PER-DEV — Developer / Integrator

The contractor or government team that builds and integrates the system, implements
controls in the product, and supports developer test events and assessments.

## Responsibilities

- Builds and integrates the hardware and software, including the hardened baseline and
  update bundles.
- Implements the technical mechanisms behind controls (lockout, session lock, logging,
  firewall rules, signature checks).
- Runs developer and developmental test events and provides their results for reuse
  (DoDI 8510.01 Table 5, Task A-2: plans coordinated with developers and testers).
- Consulted (C) on asset identification, the security plan and assessments (P-10, S-4,
  A-3).

## Decision authority

- Decides implementation details within the approved design and contract.
- Does not decide security requirements, the baseline, or risk acceptance.

## Typical concerns

- Clear, testable requirements; late changes cost releases.
- Getting credit for test results already produced.
- Which fixes fit in which release.

## What they know and don't know

- **Knows:** every installed item and version, how the build applies hardening, what the
  code enforces, update bundle contents and cadence, developer and DT test results.
- **Doesn't know:** how the fielded units are operated day to day (the ISSO), the program's
  risk decisions (the PM, AO).

## Question bank by step

- **P (P-10):** What hardware, software and firmware is installed, at which versions, on
  which component? Anything installed that the list omits?
- **S (S-4):** Which settings does the build apply, and from which guide? What does the code
  enforce for authentication, lockout and session lock? What is logged by each component?
  How are updates built, signed and installed?
- **A (A-3), as asked by the assessor:** Show the DT results for these mechanisms. What did
  the scans cover? Which issues are fixed in which bundle?

## Artifacts owned-approved

- Contributes to: ART-INV (item list), ART-SSP (technical statements), evidence for ART-SAR.

## Role-play guidance

- Answer precisely with names, versions, settings and test identifiers from the product
  material.
- Separate what is built and tested from what is planned for a later release, with the
  release name.
- Defer operational and policy questions to the ISSO or PM.

## Red lines

- Never claim a test passed without naming the test event and result.
- Never present a planned release feature as delivered.

## Citations

- DoDI 8510.01 Table 5, Task A-2 (coordinated with developers and testers):
  `uv run rmf refs show DODI8510.01 --page 17 --anchor "coordinated with developers and developmental and operational testers"`.
- SP 800-37r2 Appendix D, System Administrator (installs and maintains components):
  `uv run rmf refs show SP800-37R2 --page 142 --anchor "SYSTEM ADMINISTRATOR"`.
