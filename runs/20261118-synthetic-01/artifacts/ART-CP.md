---
artifact_id: ART-CP
run_id: 20261118-synthetic-01
produced_by_task: S-4
touched_by: [S-4]
sources: [INT-124.A1, INT-124.A2, INT-124.A3, INT-095.A1, INT-095.A2, INT-096.A1, INT-126.A2, ART-BIA, product/conops.md#availability, product/conops.md#limitations, product/test-results.md#dt-2]
---
# Contingency plan

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

## Introduction and scope

This is the EFRAS information system contingency plan (ISCP), version 1.0 draft. It restores
daily readiness reporting and then forecasting and analysis after a disruption, under the
Component RMF policy and the policy statement, activation criteria and backup policy in
`policy` of `artifacts/data/contingency.yaml` [[INT-095.A1]] [[INT-124.A1]]. It covers the
production account inside the boundary at the availability impact shown in the facts block.
It assumes the cloud provider's second IL4 region, the access point, the identity broker and the
software factory are available for a rebuild. It does not cover the providers' own platforms
(their plans do), the source systems, or the response to an incident itself, which the incident
response plan governs until it hands over a rebuild. It is coordinated with the incident
response and configuration management plans, the provider's contingency guidance and the EMIS
contingency plan (`scope.related_plans`) [[INT-124.A2]] [[INT-096.A1]].

The plan is a draft: the PM approves it with the S-4 plan set by 2026-12-15, and until the
exercises of 2027-02 it is not tested. The regional failover in particular has never been
tested (`product/conops.md#limitations` item 4), so cp-2 and cp-4 stay partial
[[INT-126.A2]] [[product/conops.md#limitations]].

## Concept of operations

The plan restores the components and data flows described in ART-SD and ART-BND: the edge, the
application services, the cluster, the database, object storage, the key service, the log
pipeline and the sandbox, all rebuilt from templates and signed images [[INT-124.A2]]. It runs
in three phases: activation and notification (outage assessment, decision, notices), recovery
(zone recovery, or a rebuild in the second region in the BIA order) and reconstitution
(validation, return to normal, fresh backups, deactivation and after-action report)
[[INT-124.A3]].

## Business impact analysis

The analysis builds on ART-BIA: readiness reporting (BP-01) tolerates 72 hours, with a 24-hour
recovery time, a 24-hour recovery point (one nightly ingest) and about 4 hours of reprocessing;
forecasting (BP-02) and fleet analysis (BP-03) tolerate 168 hours and come back within 48. None
supports a mission essential function [[INT-124.A1]] [[ART-BIA]]
[[product/conops.md#availability]]. Recovery needs the database and snapshots, the key service,
the cluster, object storage, the templates and images, two on-call engineers and the source
extracts; the impact categories are reporting delay, lost forecasts and data integrity, and the
EMIS program, the supply service, the identity broker and the fleet readiness directorate were
the points of contact [[INT-124.A1]]. The optimum point is a 24-hour recovery point with a cold
alternate region: copies are cheap, and a warm region would cost about four times the run cost
for a 72-hour need (`bia` in `artifacts/data/contingency.yaml`) [[INT-124.A2]].

## Preventive controls

The program owns no hardware: power, UPS, generators, fire and water protection are inherited
from the cloud region under its provisional authorization [[INT-096.A1]]. Within the account,
the database runs with a managed standby in a second zone and node groups span three zones, so a
zone loss fails over automatically; object storage is versioned and keys are replicated to the
second region. The single region remains the one single point of failure, and the regional
failover is a manual rebuild that has never been tested (`preventive`) [[INT-124.A2]]
[[product/conops.md#limitations]].

## Recovery strategy

Three alternatives were compared: a cold rebuild in the second IL4 region from templates and
copied snapshots (about $6K a year, estimated 18 hours plus 4 hours reprocessing), a warm
standby region (about four times the run cost, 2 hours) and an active-active design (higher
still). The cold rebuild was chosen: it meets the 24-hour objective and the 72-hour tolerance if
the estimate holds, it fits a low availability impact, and it is inside the sustainment budget
[[INT-124.A2]] [[INT-126.A1]]. The offsite store and alternate site are the provider's second
region under the same contract and task order (SVA-002) and the same provisional authorization;
backups are managed point-in-time recovery and snapshots, copied daily, encrypted with program
keys replicated to that region [[INT-124.A2]] [[INT-096.A1]]. No process has a recovery time
objective plus reprocessing time above its tolerable downtime on paper, so `strategy.rto_gaps`
is empty; but the 18-hour regional rebuild is an estimate, not a measurement. The dynamic
reallocation to the second region is to be proved by the failover test EX-02 in 2027-02; until
then it is unproven, and cp-4 says so [[INT-124.A2]] [[product/conops.md#limitations]].

## Roles and responsibilities

The PM (PER-PM) is the activating authority and ISCP director, with the ISSM (PER-ISSM) as
successor; the ISSE (PER-ISSE) is the ISCP coordinator. The recovery team is led by the ERST
technical lead (PER-DEV) with the senior on-call engineer as alternate, staffed by the cloud
operations engineers for their template, Kubernetes, PostgreSQL and key skills; the
notification and security team is led by the ISSO (PER-ISSO) with the ISSM as alternate. The
cloud provider (SVA-002) and the software factory (SVA-004) are the vendor contacts, under their
contract and tenant SLA (`teams`) [[INT-124.A3]] [[INT-095.A1]].

## Activation and notification

The plan is activated by the PM, or the ISSM as successor, when the system or its database is
down or expected to be for more than 12 hours, when the region, the account or its connectivity
is lost, when an incident needs the account rebuilt, or when the ingest cannot correct corrupted
data. With notice, users and the fleet readiness directorate are told a day ahead; without
notice, the on-call engineer pages the ISSE and the ISSO at any hour, and the call tree follows
by pager and phone, not e-mail. An alternate acts after 30 minutes without an answer. Messages
say what happened, what is affected, the expected recovery time, the fallback and the next
update. The outage assessment team (recovery team leader and ISSE) covers cause, further damage,
affected components and data, the state of the region, access point and broker, what to
rebuild and time to restore, and its result decides the course (`activation`) [[INT-124.A3]]
[[INT-095.A1]].

## Recovery

Recovery follows the BIA priorities: keys and network, the database restore, the ingest and its
data check (BP-01 within 24 hours), the API and web, the edge and routing, then forecasting,
reports and the sandbox within 48 hours. Each step is a runbook checklist per configuration item
with its pipeline job and check. Nothing is shipped: backups, images and plans move as data. If
the rebuild is not done in 12 hours the ISSE tells the PM and the fleet readiness directorate,
and past 48 hours the PM informs the AO. During the outage squadrons use EMIS's own reports
(`recovery`) [[INT-124.A1]] [[INT-124.A3]] [[product/conops.md#mission]].

## Reconstitution

The ingest re-runs the missed extracts and row counts and checksums are compared with the
sources; the release smoke tests run; the ISSO scans the restored account against the templates
and the ISSE signs off before users return. The PM declares normal operations; running from the
second region is judged for significance by the ISSE, with the AO's concurrence before it
becomes permanent. Temporary resources are removed, a fresh snapshot is taken, cross-region
copying resumes, the ISSE logs the event and writes the after-action report within 10 working
days, and the plan is deactivated (`reconstitution`) [[INT-124.A3]] [[INT-125.A3]].

## Testing, training and exercises

Three exercises (`exercises`): EX-01, a tabletop in 2027-02 on a ransomware-style compromise
that takes the whole account and its connectivity offline, held under realistic cyber
conditions and testing the work-arounds and the fallback to EMIS reports, with both critical
suppliers and the CSSP; EX-02, a functional regional failover test in 2027-02 that rebuilds the
pre-production account in the second region and measures the time against the 18-hour
estimate; EX-03, the annual database restore test. A tabletop is the depth a low availability
impact requires; EX-02 is added because the failover is unproven [[INT-124.A3]]
[[product/conops.md#limitations]]. The latest test result is the DT-2 restore of 2026-10-17:
3 h 10 min, inside the objective; no tabletop and no failover test have been held
[[product/test-results.md#dt-2]] [[INT-095.A2]]. Training covers roles, the call tree,
activation criteria and the runbook, yearly and before a new person joins the rotation
(`training`) [[INT-124.A3]].

## Plan maintenance

The ISSE maintains the plan and reviews it annually and after any significant change, exercise
or activation, checking the BIA, contacts, strategy, runbook, agreements and exercise results;
contacts are checked quarterly. The plan is marked CUI, its holders are recorded, and a copy
with the contact list sits with the templates, readable from either region. Changes are
coordinated with the CSSP, the providers and the EMIS program and versioned in the repository;
the BIA is updated on a significant change, and the plan is kept until disposal. The PM signs it
once complete; it is affirmed as tested only after EX-01 and EX-02 (`maintenance`)
[[INT-124.A3]] [[INT-126.A2]].

## Appendices

The contact list is kept with the plan in the repository; the diagrams are those of ART-BND and
the product data flows; the inventory is ART-INV with the configuration items of the CM plan;
the interconnections are IC-1 (EMIS), IC-2 (supply status) and IC-3 (identity broker), each with
its POC; recovery is constrained by the access point, the identity broker and the software
factory (`appendices`) [[INT-124.A1]] [[product/architecture.md#interconnections]].

<!-- I-2 appends "## Implementation updates" (dated: what changed during implementation and
     why) and adds I-2 to touched_by. -->
