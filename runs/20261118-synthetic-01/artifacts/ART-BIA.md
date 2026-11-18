---
artifact_id: ART-BIA
run_id: 20261118-synthetic-01
produced_by_task: P-8
touched_by: [P-8, C-2]
sources: [INT-018.A1, INT-018.A2, INT-018.A3, INT-018.A4, INT-019.A1, product/conops.md#mission, product/conops.md#availability, INT-065.A4, INT-066.A1, INT-066.A2]
---
# Business impact and criticality analysis

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

## Mission critical functions

No mission critical function is present within the system [[INT-018.A2]]. The service supports
the naval aviation readiness mission and the aircraft maintenance and readiness management
business function as decision support only: it does not write to the maintenance information
system, order parts or change aircraft status, and squadrons fall back to the maintenance
system's own reports when it is down [[INT-018.A2]] [[product/conops.md#mission]]. The record
is `artifacts/data/bia.yaml` (`mission_critical: false`, no `functions`) [[INT-018.A2]].

## Supported processes and disruption impact

The capability sponsor identified three processes and rated the disruption of each Low, a
limited adverse effect with a manual fallback [[INT-018.A1]] [[INT-018.A2]]. The users' recovery
time requirements come from the user representative [[INT-019.A1]]:

| Process | Impact of disruption | Users' recovery time requirement | Interdependencies | Trace |
|---|---|---|---|---|
| BP-01 Daily readiness reporting | low | 72 hours | maintenance information system extract, supply status pull, identity broker sign-in, cloud region | [[INT-018.A3]] [[INT-018.A4]] [[INT-019.A1]] |
| BP-02 Part failure forecasting | low | 168 hours (one week) | BP-01 data load, maintenance information system extract, cloud region | [[INT-018.A3]] [[INT-019.A1]] |
| BP-03 Fleet readiness analysis and de-identified export | low | 168 hours (one week) | BP-01 data load, identity broker sign-in, cloud region | [[INT-018.A3]] |

The users' recovery time for BP-01 matches the 72-hour outage tolerance in the concept of
operations; the program's own recovery time objective is shorter, 24 hours
[[product/conops.md#availability]]. The user representative stresses that wrong numbers, for
example tampered maintenance data, would hurt more than an outage; that is an integrity concern
for C-2 [[INT-019.A2]].

## External dependents

Senior leaders depend on BP-01 through the readiness briefing slides they receive by e-mail; they
learn of an outage from the fleet readiness directorate's daily readiness brief, which notes when
readiness data is late [[INT-018.A3]].

## Reevaluations

No reevaluation is recorded at P-8: the categorization is set at C-2, which compares each
process's disruption impact with the availability impact and records any reevaluation by the
mission owner and the data owner here [[INT-018.A2]].

## Criticality analysis

The Frame iteration of the criticality analysis was made with the capability sponsor on
2026-11-18 [[INT-018.A4]]. The prioritized list in `bia.yaml` ranks BP-01 first, BP-02 second
and BP-03 third, then the Example Maintenance Information System, whose nightly extract
underpins all three processes, and the enterprise identity broker, a defensive item every
process depends on for sign-in [[INT-018.A4]]. Boundary components join the list once P-11
records them, at the Assess iteration of C-2 [[INT-018.A4]].

## Categorization comparison and Assess iteration (C-2)

C-2 set the availability impact of the categorization (the facts block shows it). Each process's
disruption impact was compared with it: BP-01, BP-02 and BP-03 are all rated low, and none exceeds
the availability impact. No process needs a reevaluation by the mission and data owners, and the
`reevaluations` list stays empty. The sponsor confirmed that the 72-hour tolerance of BP-01 is
the most demanding, and that the program's 24-hour recovery objective is a target, not a reason
to raise availability [[INT-066.A1]].

The Assess iteration of the criticality analysis was made on 2026-11-18 [[INT-065.A4]]
[[INT-066.A2]]. The processes keep their Frame ranking, followed by EMIS and the identity
broker. Three boundary components were added because they underpin all three processes:

- rank 6, the ingest worker CMP-INGEST;
- rank 7, the database CMP-DB;
- rank 8, the key management service CMP-KMS, a defensive item.

The API and the web front end can be redeployed from the pipeline within the recovery
objective, so they were not added [[INT-065.A4]].
