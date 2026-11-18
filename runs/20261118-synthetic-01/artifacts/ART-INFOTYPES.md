---
artifact_id: ART-INFOTYPES
run_id: 20261118-synthetic-01
produced_by_task: P-12
touched_by: [P-12, P-13]
sources: [INT-031.A1, INT-031.A2, INT-031.A3, INT-031.A4, INT-032.A1, INT-032.A2, INT-032.A3, INT-033.A1, INT-033.A2, ASM-009, ART-BND, INT-027.A1, INT-027.A2, INT-027.A3, INT-027.A4, INT-028.A1, INT-028.A2, INT-029.A1, INT-029.A2, INT-029.A3, INT-029.A4, INT-030.A1, INT-030.A2, INT-030.A3, product/conops.md#information, product/privacy.md#pii]
---
# Information types and information life cycle

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
| Classification and handling markings | unclassified; markings: CUI | C-1 |
| IT type | major-application, networked | C-1 |
| Owning organization | Aviation Readiness Software Program Office (ARSPO), naval aviation PEO (fictional) | C-1 |
| System version | 1.5 (MVCR) (released 2026-10-27) | C-1 |
| Operational environment | production | C-1 |
| Life-cycle phase | PH-PD | C-1 |
<!-- END rmf:facts -->

## Information types

Six information types are processed, stored and transmitted; the records, with selection basis
and handling, live in `artifacts/data/infotypes.yaml` [[product/conops.md#information]].
Provisional values are the SP 800-60 Vol. II recommendations; the adjusted values are each
owner's [[INT-027.A2]] [[INT-028.A2]] [[INT-030.A3]].

| ID | Information type | SP 800-60 | Provisional C / I / A | Adjusted C / I / A | Reason for adjustment |
|---|---|---|---|---|---|
| INF-01 | Maintenance and readiness data | C.3.1.1 | L / L / L | M / M / L | aggregation reveals fleet readiness; tampering hides degraded readiness [[INT-027.A2]] |
| INF-02 | Supply status | C.3.4.2 | L / L / L | L / M / L | wrong status misdirects part orders [[INT-028.A2]] |
| INF-03 | Maintainer PII | C.2.8.9, C.3.3.10 | M / M / M | M / M / L | EMIS holds the authoritative copy [[INT-027.A3]] |
| INF-04 | Forecasts and reports | C.3.4.3 | L / L / L | M / M / L | same aggregation and tampering harm as INF-01 [[INT-027.A4]] |
| INF-05 | Audit records | C.3.5.8 | M / M / L | none | [[INT-030.A2]] |
| INF-06 | System security information | C.3.5.5 | L / M / L | M / M / L | system information held at the most sensitive user level [[INT-030.A3]] |

All six are unclassified CUI; none is controlled technical information or software artifacts
of military application [[INT-027.A1]] [[INT-028.A1]] [[INT-030.A3]]. The provisional high-water
mark across adjusted values is moderate confidentiality, moderate integrity and low availability;
C-2 decides the categorization.

## Privacy

The system processes PII [[INT-029.A1]]. INF-03 holds maintainer name, DoD ID number, rate or
rank, qualifications and work center about federal personnel; INF-05 holds user names and DoD ID
numbers of federal personnel and contractor administrators [[INT-029.A2]]. Neither holds PHI or
SSNs [[INT-027.A3]]. The PII was found by walking the EMIS extract layout field by field, and
attributes that identify only in combination keep the pseudonymized exports PII [[INT-029.A1]].

Handling complies with DoD 5400.11-R, DoDI 5400.16 and DoDI 5015.02. The records are covered by
published Component SORNs for aviation maintenance records and for computer access and security
records; no Privacy Act statement is needed because nothing is collected from individuals
[[INT-029.A3]] [[product/privacy.md#authority]]. The Component records management office has
coordinated the schedules [[INT-029.A4]]. PIA determination: required (new DoD system holding PII
about federal personnel in electronic form; the NSS exclusion is not used), due before MVCR
production deployment and no later than 2027-02-01; the draft PIA v0.9 is with the privacy
office [[INT-029.A4]] [[product/privacy.md#pia]]. This determination goes to the SAOP's designee
for approval at C-3.

## Information owners

| Owner (persona) | Organization | Types | Input |
|---|---|---|---|
| PER-IO, fleet maintenance data steward | fictional fleet maintenance directorate | INF-01, INF-03, INF-04 | INT-027 |
| PER-IO, supply status data owner | Example Supply Status Service | INF-02 | INT-028 |
| PER-PM, ARSPO product manager | ARSPO | INF-05, INF-06 | INT-030 |

Each owner set the impact levels of its own types in the interview named [[INT-027.A2]]
[[INT-028.A2]] [[INT-030.A1]].

## Information Life Cycle (P-13)

Every type's stages, with the components at each, are in the `life_cycle` records of
`artifacts/data/infotypes.yaml`, from the privacy officer, the system owner and the data steward
[[INT-031.A1]] [[INT-032.A1]] [[INT-033.A1]]. The stages follow the boundary's flows DF-1 to
DF-10 [[ART-BND]].

| Type | Enters by | Stored in | Leaves by | Disposition |
|---|---|---|---|---|
| INF-01 | collection from EMIS (DF-3) | CMP-DB, landing files in CMP-OBJ | reports and dashboards only | monthly purge outside 5 years; landing files after 7 days |
| INF-02 | collection from the supply service (DF-4) | CMP-DB | forecasts and dashboards | purged with linked maintenance records |
| INF-03 | collection in the EMIS extract (DF-3) | CMP-DB | pseudonymized exports (DF-7) and training extract (DF-8) | monthly purge; exports after 30 days; extract on replacement |
| INF-04 | creation by CMP-FORECAST and CMP-REPORT | CMP-DB, CMP-OBJ cache | exports (DF-7) and e-mailed slides | cache after 30 days; forecasts with INF-01 |
| INF-05 | creation by the components, collection by CMP-LOGS | CMP-LOGS (90 days) | disclosure to ECSSP (DF-9) | deleted after 90 days |
| INF-06 | creation by the pipeline and CMP-KMS | CMP-KMS | not disseminated | scheduled key deletion |

[[INT-032.A3]] [[INT-033.A2]] [[INT-031.A4]]

Points the life cycle brings out for later tasks: maintainer PII leaves the database in the
DF-7 exports and the DF-8 training extract in a form that is still re-identifiable until release
1.6 [[INT-031.A2]] [[product/conops.md#limitations]]; briefing slides leave EFRAS by e-mail, after
which the recipients' CUI handling applies [[INT-033.A2]]; the program's audit copy is kept 90
days, short of the one-year Component retention [[INT-031.A4]]. The retention periods of the
landing files, exports, report cache and training extract come from the system owner, not the
product material, and the privacy officer asked for them in writing with the PIA [[ASM-009]]
[[INT-031.A3]] [[INT-032.A2]].
