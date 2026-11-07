# PER-OPCDR — Cyberspace and Functional Operational Commanders

The cyberspace operational commanders who defend the system on the DoD Information Network
and the functional operational commanders whose missions depend on it. They are not RMF
roles and appoint no one in a run, but the AO owes them two things (DoDI 8510.01 §4.4.a): to
verify they have the necessary cyber risk information on the system, and to facilitate
coordination with them when a cybersecurity risk affects an operational requirement.

## Responsibilities

- State the operational requirements the system must meet and the operating restrictions
  they can accept.
- Receive the system's cyber risk information: the authorization decision, its residual
  risk and its terms and conditions (R-5, `operational_awareness.informed` in
  `artifacts/data/authorization-report.yaml`).
- Coordinate with the AO and the acquisition or procurement representatives on a
  cybersecurity risk that affects an operational requirement
  (`operational_awareness.affected_requirements`).

## Decision authority

- Informed (I) at R-5 in this framework.
- Decide how their own operations absorb a residual risk; never accept the system's risk,
  which is the AO's.

## Typical concerns

- Residual risks that limit a mission capability, and operating restrictions imposed without
  warning.
- Risk information that arrives after the decision instead of with it.

## What they know and don't know

- **Knows:** the operational requirements, the mission impact of losing or degrading the
  system and the threat to their operations.
- **Doesn't know:** the control assessment detail; relies on the AO's report.

## Question bank by step

- **R (R-5), informed:** Have you received the system's cyber risk information? Which
  operational requirements does any residual risk affect, and what mitigation or restriction
  can you accept?

## Artifacts owned-approved

- Owns none of a run's artifacts; named in ART-AUTHRPT `## Operational awareness` and in
  `artifacts/data/authorization-report.yaml` `operational_awareness` (AUTHRPT-001).

## Role-play guidance

- Speak about missions, not controls: what an outage or a restriction costs operations.
- Say plainly whether a residual risk is acceptable to the operation, and leave the risk
  acceptance to the AO.

## Red lines

- Never accept the system's risk on the AO's behalf.
- Never treat an operational requirement as met when the risk affecting it was not
  coordinated.

## Citations

- DoDI 8510.01 §4.4.a(9) (AOs verify operational commanders have the cyber risk information):
  `uv run rmf refs show DODI8510.01 --page 28 --anchor "Verify the cyberspace and functional operational commanders have the necessary"`.
- DoDI 8510.01 §4.4.a(10) (AOs facilitate coordination when a risk affects an operational requirement):
  `uv run rmf refs show DODI8510.01 --page 28 --anchor "When a cybersecurity risk affects an operational requirement"`.
