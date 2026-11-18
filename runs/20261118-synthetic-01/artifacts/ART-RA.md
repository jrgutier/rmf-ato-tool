---
artifact_id: ART-RA
run_id: 20261118-synthetic-01
produced_by_task: P-14
touched_by: [P-14]
sources: [INT-034.A1, INT-034.A2, INT-034.A3, INT-034.A4, INT-034.A5, INT-034.A6, INT-035.A1, INT-035.A2, INT-036.A1, INT-036.A2, INT-037.A1, INT-037.A2, INT-037.A3, INT-037.A4, INT-037.A5, INT-038.A1, INT-038.A2, INT-039.A1, INT-039.A2, INT-040.A1, INT-040.A2, ASM-010, ASM-012, ART-ORG-CONTEXT, ART-BIA, ART-INFOTYPES, ART-BND, ART-INV]
---
# System risk assessment

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| Authorization boundary | EFRAS-BND-1 | P-11 |
<!-- END rmf:facts -->

## Method and scope

This is the initial system risk assessment of the production environment, dated 2026-11-18. It
supports categorization, control selection and tailoring, POA&M priorities and the
authorization decision before MVCR deployment, and holds for one year or until a major release
or a change in threat [[INT-037.A1]]. Scope: the boundary of ART-BND and its seven external
connections; organization-level risk comes from ART-ORG-CONTEXT [[ART-BND]] [[ART-ORG-CONTEXT]].
It assumes the providers keep their authorizations and the ECAP and ECSSP keep working; its main
constraint is that no program-specific intelligence product exists [[INT-037.A1]].

The model is the Component's: SP 800-30 semi-quantitative, threat-oriented, five-level scales
(Tables G-5, H-3, I-2), likelihood of initiation and of adverse impact combined, a one-year
horizon [[INT-034.A5]]. Risk tolerance: moderate for operations and assets, low for individuals
[[ART-ORG-CONTEXT]]. Information sources: the Component naval aviation cyber threat assessment of
2026-07-15 (an Intelligence Community product) and ECSSP alerts for threat; pipeline, STIG and
penetration test results of October 2026 and the known limitations for vulnerability; the BIA
and the owners' impact levels for impact. The Component intelligence office's cyber threat
analyst and the program security officer were consulted on 2026-08-04 [[INT-034.A2]]. The team,
point of contact, decision rationales and the absence of tailoring are in
`artifacts/data/ra.yaml` [[INT-034.A5]].

## Threat sources and events

Threat sources: TS-01 nation-state actors (capability high, intent high, targeting moderate);
TS-02 criminal actors and phishers (moderate, moderate, low); TS-03 privileged insiders in error
(range of effects moderate); TS-04 structural failure of the cloud region (moderate)
[[INT-034.A1]].

| TE | Threat event | Source | Initiation | Adverse impact | Likelihood | Impact | Risk |
|---|---|---|---|---|---|---|---|
| TE-01 | exfiltration of readiness data and maintainer records through the API | TS-01 | moderate | moderate | moderate | moderate | moderate |
| TE-02 | re-identification from pseudonymized exports (confirmed, PT-2) | TS-02, TS-03 | moderate | high | moderate | moderate | moderate |
| TE-03 | exploitation of example-imagelib through report rendering | TS-01 | low | moderate | low | moderate | low |
| TE-04 | tampered EMIS extract | TS-01 | low | low | low | moderate | low |
| TE-05 | privileged insider error or break-glass misuse | TS-03 | low | moderate | low | moderate | low |
| TE-06 | regional outage beyond recovery objectives | TS-04 | low | moderate | low | low | low |
| TE-07 | incident older than 90 days not reconstructable | TS-01, TS-03 | low | low | low | low | low |
| TE-08 | training extract moved out through the sandbox | TS-03 | low | low | low | moderate | low |

Scenario SCN-01 couples TE-01 and TE-02: exfiltrated pseudonymized records become named records
[[INT-034.A3]] [[INT-035.A2]] [[INT-036.A1]].

## Vulnerabilities and predisposing conditions

All vulnerabilities are ones the program has disclosed or its tests found [[INT-034.A3]]
[[product/conops.md#limitations]] [[product/test-results.md#pentest]]:

| ID | Weakness | Severity | Events |
|---|---|---|---|
| VUL-01 | unsalted DoD ID hash in exports and training extract | moderate | TE-02 |
| VUL-02 | two high vulnerabilities in example-imagelib | high | TE-01, TE-03 |
| VUL-03 | no signed EMIS agreement | moderate | TE-04 |
| VUL-04 | break-glass accounts without CAC | low | TE-05 |
| VUL-05 | failover untested, contingency plan not exercised | moderate | TE-06 |
| VUL-06 | 90-day program audit retention | moderate | TE-07 |
| VUL-07 | PIA not approved | moderate | TE-02 |
| VUL-08 | sandbox egress wildcard, retest pending | low | TE-08 |
| VUL-09 | two program-fixable PostgreSQL STIG items | low | TE-05 |

Predisposing conditions: PC-01 a single cloud region (pervasiveness high) and PC-02 about 3,000
users over NIPRNet (moderate) [[INT-034.A3]]; PC-03 dependence on separately authorized services
EFRAS does not run or see inside (access point, identity broker, factory, CSSP, supply status
service) and PC-04 third-party and open-source components in every ERST-built image, both
moderate [[INT-034.A6]]. PT-1 was fixed and retested and is not carried [[INT-034.A3]].

## Mitigating conditions

Inherited and implemented conditions that lower likelihood: ECAP-only ingress, three-tier
segmentation and an egress allow-list; CAC sign-in and squadron scoping (DT-2 pass); mutual TLS
and signed extracts from EMIS (DT-2 pass); signed images verified at admission and the pipeline
security gates; encryption at rest with program keys; ECSSP monitoring and a one-year copy of the
audit records [[product/test-results.md#dt-2]] [[product/test-results.md#pipeline-1-5]]
[[ART-BND]]. Operational workarounds the ISSO runs: sealed, alerted break-glass accounts and a
quarterly account review [[INT-035.A1]].

## External and supply chain risk

EMIS is the riskiest connection (moderate), because maintainer PII arrives over it under an
interim approval only; the other six connections are low; they carry no open weakness, only PC-01 (cloud region) or
PC-03 (the five enterprise and data services) [[INT-034.A4]] [[INT-034.A6]]. The five external
service providers (EXP-01 cloud region, EXP-02 access point, EXP-03 identity broker, EXP-04
software factory, EXP-05 CSSP) meet the requirements through their own authorizations or
agreement, trust is sufficient and no response is needed; the factory's open POA&M is watched
[[INT-034.A4]]. Supply chain records SC-01 to SC-05 cover every inventory item; the example-imagelib
open-source supply chain is moderate (VUL-02), the others low, with ERST and the web framework
carrying only PC-04 [[INT-034.A6]]. Third-party components (example-imagelib,
the web framework, the factory base image) were reviewed against the six DoWI 8430.01 factors,
and the open-source ones for governance, community and license [[INT-038.A2]]. The forecast model
is an AI-enabled capability: its use-case risk, benchmarks, pre-deployment verification,
monitoring and bias handling are in `ra.yaml` [[INT-038.A1]]. The supplier records, threat
analysis and the PM's SCRM actions (moderate supply chain risk tolerance) are in
`artifacts/data/scrm.yaml` [[INT-037.A5]]. The BIA rates no EFRAS function mission-critical.
The C-SCRM record must still name one function, so it names CF-01, the nightly ingest and the
integrity of the readiness data it loads, which is the program's most important function and not a
mission-critical one [[INT-039.A1]] [[ASM-012]]. Following from that entry, ERST (SUP-01) and the
cloud provider (SUP-03) are treated as critical suppliers. Their supply chain risk assessments
SA-01 and SA-02 cover every Table 28 factor and find low, non-adversarial risk at SCRSS level 1,
within tolerance and accepted [[INT-040.A1]] [[INT-040.A2]]. A threat analysis request (TAC-01) went
through the Component TSN focal point on 2026-11-18 and has no report yet [[INT-039.A2]].

Program protection and strategy records the assessment read: `protection.yaml` holds the tailored
PPP EFRAS-PPP v1.1 (critical item CI-001, countermeasures CM-001 and CM-002, technical risks
TR-001 and TR-002) and `cybersecurity-strategy.yaml` the cybersecurity strategy v1.1 with its
Component CIO approval and reviews; neither document is in the product package and both rest on
the PM's statements [[INT-037.A3]] [[INT-037.A4]] [[ASM-010]]. No S&T protection plan applies,
because EFRAS is a new start, not an S&T transition [[INT-037.A3]].

## Risk summary

Priority order: TE-02, TE-01 (moderate); then TE-04, TE-08, TE-05, TE-03, TE-07, TE-06 (low).
Among equal levels, risks that harm individuals or the fleet's trust right away come first, then
integrity, then risks whose harm lies in the future; borderline values were rounded up when they
touch personal data [[INT-037.A2]] [[INT-034.A5]]. The designated system risk is moderate, set by
TE-01, the most severe threat to any component (the database behind the API) [[INT-035.A2]].
TE-02 drives the privacy requirements and the release 1.6 fixes; TE-01 and TE-03 drive the
application and dependency requirements. Results go to the AO, AODR and PM as this report, and
source data and intermediate results are shared inside the Component under CUI rules
[[INT-037.A1]]. Elements needing attention in test events: the report service and its export
scoping, the export pseudonymization, the EMIS ingest path and the regional failover
[[INT-034.A3]].

## Privacy risk

The processing is the bulk ingest of about 30,000 maintainers' records, kept five years and shared
pseudonymized with analysts and data scientists; the impact on individuals is moderate until
release 1.6 [[INT-036.A1]]. Legal and policy requirements evaluated: OMB A-130 applies, and the
privacy baseline leaves two obligations to separate steps (effective de-identification and a
minimization review of exports); the Privacy Act applies to the system of records; the FIPPs were
considered; DoDI 5400.16 requires the PIA (ART-PIA, draft). The ART-REQ requirements that carry
them (REQ-14 to REQ-16) are written at P-15 [[INT-036.A2]] [[INT-029.A4]].

## Maintenance

The threat sources, the open vulnerabilities and the connections are monitored on the Component
minimum frequencies of ART-ORG-CONTEXT; the assessment is updated at R-2 with the assessment
findings, at each major release, after a significant change in threat and at least yearly
[[ART-ORG-CONTEXT]] [[INT-037.A1]]. The purpose, scope and assumptions hold as of 2026-11-18
[[INT-037.A1]].
