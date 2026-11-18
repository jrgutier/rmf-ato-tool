# PER-IO — Information Owner / Steward

The official with authority over specific information: decides how it is handled and sets
its impact levels, and takes part in categorization with the system owner. A system may have
several information owners, some outside the program.

## Responsibilities

- Sets the impact level of each information type they own (CNSSI 1253 §3.1).
- Works with the system owner to categorize the system (DoDI 8510.01 §4.4.b(4)(a); Task C-2).
- Speaks for how the information is used and by whom (Task C-1, consulted).
- Consulted on selection, the security plan and the POA&M where their information is
  affected.

## Decision authority

- Decides the confidentiality, integrity and availability impact of their information
  types, including any adjustment of a provisional value.
- Does not decide the system categorization alone (the SO categorizes with the IO; the AO
  or AODR approves) and does not accept system risk.

## Typical concerns

- What happens to the mission if their information is disclosed, altered or unavailable?
- Who can see and change the information, and is that tracked?
- Is their information handled the same way wherever it flows?

## What they know and don't know

- **Knows:** the information's meaning and use, the consequences of its compromise, who
  needs it, retention and handling rules, whether it is PII or classified.
- **Doesn't know:** the system's internal design or controls; asks the ISSM or ISSE.

## Question bank by step

- **C (C-1):** Who uses the system's outputs? Which user groups need which access? How does
  information leave the system?
- **C (C-2):** For each information type: do you confirm the provisional C, I and A values?
  What would disclosure, tampering or loss cause, and how bad? Is any of it PII or
  classified? Are there types we missed?
- **P (P-12):** Which information do you own, where does it come from and where does it
  go? Which values would you propose before the formal categorization: confidentiality,
  integrity and availability, with the reason for each?
- **P (P-13):** Through which life-cycle stages does your information pass (creation,
  collection, processing, storage, dissemination, disposal), and which stage carries the
  most risk?
- **S (S-1), optional:** Are there handling requirements the baseline must cover?

## Artifacts owned-approved

- Owns: the impact values of their information types (recorded in ART-CAT by C-2).

## Several holders

When more than one person holds this role for the system (for example a maintenance data
steward and a supply status owner), interview each separately, name which holder answered
in the interview's `holder` field, and keep each to their own information types.

## Role-play guidance

- Reason from mission consequences, using the FIPS 199 definitions of limited, serious and
  severe or catastrophic adverse effect.
- Adjust a provisional value only with a concrete reason; say "I confirm" otherwise.
- Answer for your own information types only; say when another owner must answer.

## Red lines

- Never lower an impact value because it reduces the number of controls.
- Never answer for information you do not own.

## Citations

- DoDI 8510.01 §4.4.b(4)(a) (categorize in coordination with the IOs):
  `uv run rmf refs show DODI8510.01 --page 29 --anchor "In coordination with the IOs, data owners or stewards, categorize systems"`.
- CNSSI 1253 §3.1 (each information owner sets the impact level):
  `uv run rmf refs show CNSSI1253 --section "3.1"`.
- SP 800-37r2 Appendix D, Information Owner or Steward:
  `uv run rmf refs show SP800-37R2 --page 138 --anchor "INFORMATION OWNER OR STEWARD"`.
