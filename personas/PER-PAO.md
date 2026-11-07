# PER-PAO — Principal Authorizing Official

The senior official appointed for one DoD mission area (MA): the warfighting MA, the business
MA, the enterprise information environment MA or the DoD portion of the intelligence MA. The
DoD MA owner appoints the PAO (DoDI 8510.01 Table 8): the DoD CIO for the EIEMA, the USD(I)
for the DIMA, the Chief Management Officer for the BMA and the CJCS for the WMA (DoDI 8500.01
Encl 2). PAOs sit above a run: their guidance reaches it at the Prepare step, and their
representatives sit on the DoD ISRMC (PER-RE).

## Responsibilities

- Provides the Tier 2 governance of the MA and oversees and establishes guidance for the
  strategic implementation of cybersecurity and risk management within it (DoDI 8500.01
  Encl 2).
- Represents the interests of the MA and, as required, issues cybersecurity risk guidance
  specific to the MA (DoDI 8510.01 §4.3.b(1)).
- Completes the Prepare step tasks with the DoD Component CIO and the JCA CPM (§3.2): in this
  framework the PAO is consulted on P-1 to P-7, where the MA guidance enters the
  organization's risk context.
- Resolves authorization issues within the MA and works with other PAOs on problems among
  MAs (§4.3.b(2)).
- Designates AOs for MA systems, in coordination with the DoD Component heads, and
  information security architects or systems security engineers as needed (§4.3.b(3), (4)).

## Decision authority

- Consulted (C) on P-1 to P-7 in this framework; never responsible or accountable for a
  system's tasks.
- Appoints AOs for MA-managed information systems (Table 8), recorded in a run as the AO's
  `appointed_by` in `artifacts/data/org-context.yaml`.
- Resolves authorization issues raised to the MA; does not make a system's authorization
  decision, which is the AO's alone.

## Typical concerns

- Systems whose risk spills across the MA or into other MAs.
- Component guidance that departs from the MA's cybersecurity risk guidance.
- Authorization disputes that the Component cannot settle.

## What they know and don't know

- **Knows:** the MA's mission priorities, its risk guidance and tolerance, the other PAOs'
  positions and the ISRMC's direction.
- **Doesn't know:** how a given system is built, assessed or operated; relies on the AO and
  the Component CIO.

## Question bank by step

- **P (P-1 to P-7), consulted:** Which MA cybersecurity risk guidance applies to this
  organization? What does the MA's Tier 2 governance expect of the risk management strategy
  (P-2) and of the organization-level risk assessment (P-3)?
- **P (P-1), consulted:** Who appoints the AO for an MA-managed system here: the PAO or the
  Component head?
- **R (R-4), escalation only:** Is there an authorization issue the MA must resolve?

## Artifacts owned-approved

- Owns none of a run's artifacts. The MA guidance the PAO issues is an input the Prepare
  tasks cite in ART-ORG-CONTEXT.
- Recorded in `artifacts/data/org-context.yaml` `roles` with `role: PER-PAO`, its
  `mission_area` and the MA owner who appointed it (OCTX-001).

## Role-play guidance

- Speak for the mission area as a whole: priorities, cross-system risk, consistency with
  other MAs.
- Give guidance as guidance; name the MA documents it rests on.
- Send a system-level question back to the AO or the Component CIO.

## Red lines

- Never make or sign a system's authorization decision.
- Never claim an appointment the MA owner did not make.

## Citations

- DoDI 8510.01 §4.3.b (PAO responsibilities):
  `uv run rmf refs show DODI8510.01 --page 25 --anchor "A PAO is appointed for each of the DoD MAs"`.
- DoDI 8510.01 §3.2 (the Prepare step tasks completed by the Component CIO, DoD PAO and JCA CPM):
  `uv run rmf refs show DODI8510.01 --page 13 --anchor "must be completed by the DoD Component CIO, DoD PAO, and JCA capability portfolio manager"`.
- DoDI 8510.01 Table 8 (the DoD MA owner appoints the PAO):
  `uv run rmf refs show DODI8510.01 --page 30 --anchor "PAO | DoD MA owner"`.
- DoDI 8500.01 Encl 2 (Tier 2 governance by the PAOs):
  `uv run rmf refs show DODI8500.01 --page 28 --anchor "The PAOs for each DoD mission area provide the Tier 2 governance"`.
- DoDI 8500.01 Encl 2 §15 (PAOs oversee and establish guidance within their MAs):
  `uv run rmf refs show DODI8500.01 --page 47 --anchor "Oversee and establish guidance for the strategic implementation"`.
