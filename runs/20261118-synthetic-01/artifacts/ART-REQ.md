---
artifact_id: ART-REQ
run_id: 20261118-synthetic-01
produced_by_task: P-15
touched_by: [P-15, P-17]
sources: [INT-052.A1, INT-052.A2, INT-053.A1, INT-053.A2, INT-053.A3, INT-054.A1, INT-055.A1, INT-041.A1, INT-041.A2, INT-041.A3, INT-042.A1, INT-042.A2, INT-043.A1, INT-043.A2, INT-043.A3, INT-044.A1, INT-044.A2, INT-045.A1, INT-045.A2, INT-046.A1, INT-046.A2, INT-046.A3, ASM-013, ART-RA, ART-STAKE, ART-BIA, ART-INFOTYPES, ART-INV]
---
# Security and privacy requirements and allocation

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Fleet Readiness Analytics Service | C-1 |
| Acronym | EFRAS | C-1 |
| System ID | EFRAS | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | EFRAS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-MODERATE, CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-50 | S-1 |
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Aviation Readiness Software Program Office (ARSPO), naval aviation PEO (fictional) | C-1 |
| System version | 1.5 (MVCR) (released 2026-10-27) | C-1 |
| Operational environment | production | C-1 |
| Life-cycle phase | PH-PD | C-1 |
<!-- END rmf:facts -->

## Sources of requirements

The requirements come from five sources:

- the stakeholders' protection needs in ART-STAKE [[ART-STAKE]];
- the system risk assessment and its privacy assessment [[ART-RA]];
- the capability needs statement v1.0, which is not in the product package and rests on the
  sponsor's description [[INT-041.A2]] [[ASM-013]];
- the PPP countermeasures [[ART-RA]];
- the DoD design policy statements recorded in `artifacts/data/requirements.yaml`
  `design_policy`.

Twenty design policy statements apply, and each is carried by a requirement. The software
statements apply because ERST develops covered software for the program [[INT-046.A3]]. Eight
conditional statements do not apply:

- DP-BIOMETRICS: there is no biometric data.
- The six BIOS and TPM statements: the program procures no hardware [[ART-INV]].
- DP-SW-SAFETY: there is no operational technology, and the BIA rates no function
  mission-critical [[ART-BIA]].

`protection-requirements.yaml` records what P-15 read: PPP EFRAS-PPP, with no TAPP, S&T protection
plan or horizontal protection guidance. It also records the capability document's protection
content. SCRM and threat information are included and addressed by PRQ-001 and PRQ-002. Export
control, anti-tamper and counterintelligence support are absent. The sponsor accepts those gaps,
because there is no foreign release and no hardware [[INT-041.A2]].

## Protection needs

Seven protection needs, last assessed 2026-11-18:

| Need | Holder | Kind | Priority |
|---|---|---|---|
| NEED-01 | Sponsor | Readiness figures match EMIS | 1 |
| NEED-02 | Sponsor | No adversary sees the aggregate | 2 |
| NEED-03 | Data steward | Integrity, then confidentiality, of the data | 1 |
| NEED-04 | Data steward | Exports stay de-identified | 2 |
| NEED-05 | Privacy officer | PII processed as the SORN, PIA and Act allow | 2 |
| NEED-06 | User representative | Recovery within a day, CAC only, accessibility | 3 |
| NEED-07 | PM | Factory gates pass and provider authorizations hold | 3 |

The sources are [[INT-041.A1]] [[INT-042.A1]] [[INT-043.A1]] [[INT-044.A1]] [[INT-045.A1]]. Each
need's success criteria and rationale are in `requirements.yaml`.

## Security and privacy requirements

| ID | Requirement (short) | Traces to | Priority | Measure, criticality | Verification |
|---|---|---|---|---|---|
| REQ-01 | CAC through the identity broker | NEED-02, NEED-06; DP-IDENTITY-ASSURANCE | 2 | performance, 2 | test |
| REQ-02 | Echelon-limited access, least privilege | NEED-02; DP-SW-SECURE-ARCH | 2 | performance, 2 | test |
| REQ-03 | TLS in transit, program-key encryption at rest | NEED-02, NEED-03; DP-DATA-PROTECTION, DP-CRYPTO-INTEROP | 2 | performance, 2 | inspection |
| REQ-04 | Ingest signature, checksum and schema checks stop bad loads | NEED-01, NEED-03; DP-SW-INPUT-VALIDATION | 1 | performance, 1 | test |
| REQ-05 | Audit logging, CSSP forwarding, one-year retention | NEED-03; DP-RESILIENCE-AUDIT | 2 | performance, 2 | inspection |
| REQ-06 | Recovery within 24 hours, one load at most lost | NEED-06; DP-SW-RESILIENCE | 3 | performance, 3 | demonstration |
| REQ-07 | Factory-only builds, gates, SBOM, signed images | NEED-07; DP-SW-PRACTICES, DP-SW-SECURITY-QUALITY, DP-SW-COMMON-REQUIREMENTS | 2 | assurance, 2 | inspection |
| REQ-08 | STIG/SRG configuration checked by SCAP | NEED-07; DP-SCAP | 3 | performance, 3 | test |
| REQ-09 | CUI marking and metadata on pages and exports | NEED-03; DP-MARKING-METADATA | 3 | performance, 3 | inspection |
| REQ-10 | ECAP-only ingress, segmentation, egress allow-list | NEED-02; DP-CYBER-ARCH, DP-ENTERPRISE-ARCH, DP-ARCH-PRINCIPLES | 2 | performance, 2 | test |
| REQ-11 | Standards from the DoD IT Standards Registry | NEED-07; DP-STANDARDS-REGISTRY, DP-STANDARDS-SUFFICIENT | 4 | assurance, 4 | analysis |
| REQ-12 | Section 508 accessibility | NEED-06; DP-ASSISTIVE-TECH | 4 | performance, 4 | test |
| REQ-13 | Every requirement measurable, traced, reviewed for zero trust | NEED-01, NEED-07; DP-SW-TRACEABLE | 3 | assurance, 3 | inspection |
| REQ-14 | Effective de-identification, minimization review, 5-year purge | NEED-04, NEED-05 | 1 | performance, 1 | test |
| REQ-15 | Privacy Act and SORN handling, Privacy Act clauses in the task order | NEED-05 | 2 | assurance, 2 | inspection |
| REQ-16 | PIA approved before production use with real PII | NEED-05 | 2 | assurance, 2 | inspection |

The requirements trace to the following answers: [[INT-041.A3]] [[INT-042.A2]] [[INT-043.A1]]
[[INT-044.A1]] [[INT-045.A1]] [[INT-046.A3]].

REQ-14 to REQ-16 carry the privacy requirements the risk assessment found applicable: OMB A-130
and the FIPPs, the Privacy Act and DoDI 5400.16 [[ART-RA]]. EFRAS does not meet REQ-05, REQ-14 or
REQ-16 today. Audit retention is 90 days, de-identification arrives with release 1.6, and the PIA
is a draft. Each is listed as a known limitation [[INT-045.A2]] [[INT-042.A1]] [[INT-043.A3]].

## Privacy Act rules

EFRAS keeps records in a system of records under an existing Component SORN. REQ-15 carries every
Privacy Act rule no control states [[INT-043.A2]]:

- the bar on disclosure without consent;
- the bar on records of First Amendment activity;
- referral of access and amendment requests and their appeals to the privacy office;
- rules of conduct and penalties;
- Privacy Act clauses in the ERST task order.

Direct collection does not apply, because EFRAS collects nothing from individuals
[[product/privacy.md#pii]].

The privacy officer asked for the contract provisions because ERST contractors operate the
cluster and database that hold the records. The categorization record says `contractor_operated:
false` [[INT-043.A2]]. That was fed back to P-12 as a journal note.

## Derivation and security engineering

The ERST technical lead, acting as lead systems engineer, derived the requirements from four
documents: the capability needs statement, the ConOps, and the ConOps mission section and user
journeys, which stand in for an operational mode summary and mission profiles [[INT-046.A1]]
[[ASM-013]]. Three methods together cover design, implementation, interfaces and access points:

- threat modeling of the architecture and data flows;
- misuse cases on the API and the export function;
- the PPP criticality analysis.

There is no exportability requirement, because nothing is planned for foreign release
[[INT-046.A1]].

Two key attributes of the capability needs statement set the measures:

- availability (24-hour recovery) for survivability and sustainment;
- data protection (integrity-checked loads, encryption) for security, based on confidentiality
  and integrity [[INT-046.A2]].

Every security requirement is in the performance specification, which is the release
acceptance criteria. REQ-05 to REQ-08 are also in the product support needs.

Practices cover cybersecurity, cyber resilience and cyber survivability in design, test,
manufacture (the factory's signed builds) and sustainment. They also cover program protection
(CM-001, CM-002) and privacy engineering (pseudonymization and minimization). They apply least
privilege, defense in depth, domain separation, protective defaults, protective recovery and
least sharing [[INT-046.A3]]. The level of assurance is moderate, from the factory's automated
evidence on each release. It is commensurate with a mature cloud stack, a software pathway
program, a moderate-impact system and a decision-support mission. REQ-07 and REQ-13 carry it
[[INT-046.A3]].

## Operational constraints

Five constraints bind the solution [[INT-045.A1]] [[INT-045.A2]]:

- CON-01 (security): IL4 region, reached only over NIPRNet through ECAP.
- CON-02 (operation): FIDO2 break-glass console accounts instead of CAC, for the AO to accept.
- CON-03 (implementation): software factory builds only.
- CON-04 (stakeholder): MVCR deployment by 2027-02-01.
- CON-05 (integration): the EMIS extract runs under an interim e-mail approval until the
  interconnection agreement is signed.

## Analysis and agreement

Each need was checked for at least one tracing requirement, and each requirement for a measure
and a verification method. The set was also checked against the constraints. Each stakeholder
was shown their requirements, the priorities and the known gaps. Three issues were resolved
[[INT-045.A2]]:

- Audit retention keeps the one-year requirement, and the gap is tracked.
- The break-glass exception became constraint CON-02.
- REQ-16 is kept as written, so MVCR deployment depends on PIA approval.

The sponsor, the data steward, the privacy officer, the user representative and the PM each
agreed on 2026-11-18 [[INT-041.A3]] [[INT-042.A2]] [[INT-043.A3]] [[INT-044.A2]] [[INT-045.A2]].

## Requirements Allocation (P-17)

### Allocation

| ID | Allocated to |
|---|---|
| REQ-01 | CMP-WEB, CMP-API; identity broker (common control provider) |
| REQ-02 | CMP-API, CMP-REPORT |
| REQ-03 | CMP-EDGE, CMP-DB, CMP-OBJ, CMP-KMS |
| REQ-04 | CMP-INGEST |
| REQ-05 | CMP-LOGS; CSSP (common control provider) |
| REQ-06 | CMP-DB, CMP-K8S; cloud region (common control provider) |
| REQ-07 | CMP-K8S; software factory (common control provider); ERST contract |
| REQ-08 | CMP-K8S, CMP-DB |
| REQ-09 | CMP-WEB, CMP-REPORT |
| REQ-10 | CMP-EDGE, CMP-K8S; access point (common control provider) |
| REQ-11 | CMP-API, CMP-INGEST |
| REQ-12 | CMP-WEB |
| REQ-13 | ERST contract |
| REQ-14 | CMP-REPORT, CMP-SANDBOX, CMP-INGEST; privacy office reviews (environment) |
| REQ-15 | privacy office (environment); ERST contract |
| REQ-16 | Component PIA process (environment) |
| REQ-17 to REQ-19 | contracts |

Each requirement goes to the component the program configures to meet it. Where a provider
carries part of it under its own authorization, that part goes to the provider as a common
control provider [[INT-052.A1]]. Each privacy requirement also goes to the parts of the privacy
office's process it relies on [[INT-054.A1]]. The trace still runs both ways: from need to
requirement to component to the verification method in the table above.

The ISSO carries the operational side of four requirements:

- REQ-02: role reviews.
- REQ-05: the weekly report.
- REQ-07: release sign-off.
- REQ-08: tracking of SCAP results.

Until release 1.6, the one-year audit copy under REQ-05 depends on the CSSP [[INT-055.A1]].

### Contract requirements

The ERST development task order (CA-001, modification of 2026-11-18) carries the following
[[INT-052.A2]] [[INT-053.A1]]:

- REQ-07 and the C-SCRM requirement REQ-17, whose terms are the qualifying condition,
  revalidation, reporting, response roles and termination. There is no flow-down, because ERST
  has no subcontractors.
- The PPP countermeasures CM-001 and CM-002.
- Two cyber resilient engineering requirements.
- Software assurance remediation through the factory gates. The program builds no hardware.
- The Privacy Act clauses of REQ-15.

`scrm-acquisition.yaml` records the terms, yearly revalidation and C-SCRM in each procurement
step. It also records the selection of all five suppliers: each was screened against every
prohibited supplier list on 2026-11-18 and found clear, and the open-source projects come only
from the factory's vetted library [[INT-053.A2]] [[INT-053.A3]].

The cloud task order carries the seven DTM 24-001 clauses as REQ-18; S-4 records them on the
contract [[INT-053.A1]].

Contractors perform two cyberspace work roles: system administrators (the cloud operations
engineers) and software developers. REQ-19 sets their qualification under DFARS Subpart 239.71,
and ERST documents each person's qualification for the COR to check [[INT-053.A1]].
