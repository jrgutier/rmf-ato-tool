---
artifact_id: ART-BIA
run_id: 20261118-synthetic-01
produced_by_task: P-8
touched_by: [P-8]
sources: [INT-018.A1, INT-018.A2, INT-018.A3, INT-018.A4, INT-019.A1, product/conops.md#mission, product/conops.md#availability]
---
# Business impact and criticality analysis

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| Authorization boundary | EFRAS-BND-1 | P-11 |
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
