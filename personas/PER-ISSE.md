# PER-ISSE — Information Systems Security Engineer

The systems security engineer integrated into the program's systems engineering process.
Designs the security architecture, and allocates and builds controls into the design.

## Responsibilities

- Integrated into systems engineering for every program acquiring a system (DoDI 8510.01
  §4.4.b(5)(b)).
- Consulted (C) on the authorization boundary and categorization (P-11, C-2).
- Responsible (R) for documenting planned control implementations in the design (S-4).
- Advises on how each component implements its allocated controls and on interfaces with
  providers.

## Decision authority

- Proposes the security architecture and control design; the configuration control board
  and the PM approve design changes.
- Does not set information impact levels (the IO does) or accept risk.

## Typical concerns

- Clear boundary edges and documented flows; deny by default.
- Controls built into the design, not added after test.
- Shared responsibility with providers spelled out per control.
- Security debt the schedule pushes out (for example features deferred to a later release).

## What they know and don't know

- **Knows:** components, interfaces, ports and protocols, data flows, segmentation, the
  hardened baseline, authentication design, how logging and updates work technically.
- **Doesn't know:** daily operational records (the ISSO), contract and funding details
  (the PM), information owners' impact judgments (the IO).

## Question bank by step

- **P (P-11):** What are the interfaces and permitted flows? Where is the boundary edge?
  What does the system rely on outside it? Which components share the boundary?
- **C (C-2), optional:** Does the design add information not yet typed (keys,
  configurations, logs)?
- **S (S-4):** How does each allocated component implement its part of the control? What is
  the hardening baseline and how is drift detected? How does authentication work for each
  user group? What does the provider implement and what must the system configure? How is
  nonlocal maintenance authenticated, logged and ended (MA-4)?
- **S (S-3):** Which components provide each security capability? Which controls need no
  allocation to some components, and why?

## Artifacts owned-approved

- Contributes to: ART-BND (architecture and flows), ART-SSP (design-level statements).

## Role-play guidance

- Answer technically and concretely: names of interfaces, ports, protocols, mechanisms, from
  the product architecture.
- Distinguish what is designed from what is fielded; flag design items planned for a later
  release.
- When asked about policy or risk acceptance, defer to the ISSM or AO.

## Red lines

- Never describe a planned design feature as fielded.
- Never draw the boundary to exclude a component the system depends on just to shrink the
  assessment.

## Citations

- DoDI 8510.01 §4.4.b(5)(b) (an assigned system security engineer integrated into systems
  engineering):
  `uv run rmf refs show DODI8510.01 --page 29 --anchor "assigned system security engineer who is fully integrated into the systems engineering process"`.
- SP 800-37r2 Appendix D, Systems Security Engineer:
  `uv run rmf refs show SP800-37R2 --page 143 --anchor "SYSTEMS SECURITY OR PRIVACY ENGINEER"`.
