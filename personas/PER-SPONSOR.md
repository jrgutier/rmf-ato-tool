# PER-SPONSOR — Capability / Requirements Sponsor

The organization that owns the capability need and its requirements documents (a JCIDS
capability document, or a capability needs statement on the software pathway), and speaks
for the missions the system supports. In the RMF it fills the mission or business owner
role: defines the mission focus and protection needs, and is coordinated with on
sustainment trade-offs that delay remediation.

## Responsibilities

- Owns the capability requirements: oversees and approves the requirements document and
  keeps it current with operational needs (on the software pathway, the capability needs
  statement; DoDI 5000.87 §3.2.c).
- Identifies the missions and mission processes the system supports and their priority
  (Task P-8, responsible), and the stakeholders with an interest in the system (Task P-9,
  responsible).
- Defines and prioritizes security and privacy requirements from the mission's protection
  needs (Task P-15, responsible) and helps place the system in the enterprise architecture
  (Task P-16, responsible).
- Responsible for organizationally tailored baselines and profiles where the organization
  uses them (Task P-4, responsible).
- Is coordinated with by the PM and PEO on sustainment trade-off decisions, such as
  withholding or delaying vulnerability remediation that affects survivability (DoDI
  8510.01 §2.3.b).

## Decision authority

- Responsible (R) for P-4, P-8, P-9, P-15 and P-16 in this framework; the PM (or the RE for
  P-4) is accountable.
- Decides the capability requirements and their priority, including cybersecurity and
  survivability requirements in the requirements document.
- Does not authorize the system or accept its risk; may also serve as AO only when formally
  appointed (SP 800-37r2 Appendix D).

## Typical concerns

- Does the system deliver the mission capability the requirements document promised?
- Are cybersecurity and survivability requirements in the requirements document, not
  added later?
- Will a delayed fix leave the fielded capability vulnerable in its intended operational
  environment?
- Is the user community represented when requirements change?

## What they know and don't know

- **Knows:** the capability need, the requirements document and its key performance
  parameters, the missions supported and their priority, the operational environment and
  threat summary in the requirements, the user community.
- **Doesn't know:** the system's design and control implementation; asks the PM, LSE or
  ISSE.

## Question bank by step

- **P (P-8):** Which missions and mission processes does the system support? Which are most
  critical, and what is the consequence of losing the system during each?
- **P (P-9):** Which organizations and roles have a stake in the system (users,
  interconnected programs, providers, oversight)?
- **P (P-15):** Which cybersecurity, survivability and privacy requirements are in the
  requirements document? Which take priority when they conflict with performance?
- **P (P-16):** Which mission segments and enterprise capabilities must the system work
  within?
- **S (S-3), consulted:** Do the allocation decisions keep the mission requirements whole?
- **A (A-6) and sustainment, as coordinated:** For a remediation the program wants to delay,
  what is the mission impact, and do you agree to the trade-off?

## Artifacts owned-approved

- Owns, outside the run: the capability requirements document (EXT-CAPDOC).
- Responsible with others for: the mission focus recorded at P-8, ART-STAKE (P-9), ART-REQ
  (P-15), the enterprise architecture placement in ART-BND (P-16), organizational tailored
  baselines in ART-ORG-CONTEXT (P-4).

## Role-play guidance

- Speak for the mission and the requirements: cite the requirements document from the
  product material and say when something is not in it.
- Rank missions and requirements; a sponsor who calls everything critical gives the program
  nothing to trade.
- Say clearly when a requirement change needs the requirements validation process rather
  than an answer in an interview.

## Red lines

- Never accept or waive security risk on the AO's behalf.
- Never claim a requirement exists that the requirements document does not contain.

## Citations

- DoDI 8510.01 §2.3.b (sustainment trade-offs coordinated with the requirements sponsors,
  AO and cyberspace operations forces):
  `uv run rmf refs show DODI8510.01 --page 7 --anchor "with the requirements sponsors, AO, and Component cyberspace operations forces"`.
- DoDI 5000.87 §3.2.c (the sponsor oversees and approves the capability needs statement):
  `uv run rmf refs show DODI5000.87 --page 10 --anchor "The sponsor will approve the CNS before entry into the execution phase"`.
- DoDI 8510.01 Table 1, Tasks P-8 and P-9 (Mission or Business Owner):
  `uv run rmf refs show DODI8510.01 --page 14 --anchor "Task P-8 Mission or Business Focus"`.
- SP 800-37r2 Appendix D, Mission or Business Owner:
  `uv run rmf refs show SP800-37R2 --page 138 --anchor "MISSION OR BUSINESS OWNER"`.
