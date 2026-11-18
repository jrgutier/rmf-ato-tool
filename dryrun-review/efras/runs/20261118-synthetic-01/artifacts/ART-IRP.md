---
artifact_id: ART-IRP
run_id: 20261118-synthetic-01
produced_by_task: S-4
touched_by: [S-4, I-2]
sources: [INT-125.A1, INT-125.A2, INT-125.A3, INT-127.A2, INT-126.A2, INT-098.A1, INT-098.A2, INT-099.A1, INT-099.A2, INT-099.A3, INT-118.A2, INT-139.A2, INT-138.A1]
---
# Incident response plan

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

## Purpose and scope

The PM commits the program to detect, report, contain and recover from incidents on the system
with the CSSP, and approves this plan, after the ISSM's review and the Component CISO office's
concurrence, by 2026-12-15; until then it is a draft and ir-8 stays planned [[INT-099.A3]]
[[INT-126.A2]]. Its objectives: every incident reported within one hour, contained before it
spreads beyond the affected components, recovered without restoring a compromise, and turned
into lessons. It covers the production account inside the boundary, its users and
administrators, the ERST engineers, and the hand-offs with the CSSP, the cloud provider and the
access point. It gives the roadmap for the program's part of the Component's capability, which
the CSSP's service carries [[INT-099.A3]] [[INT-098.A1]].

## Definitions and prioritization

An event is any observable occurrence the logs record; an incident is an event the CSSP or the
ISSO confirms as a violation or imminent threat of violation of security or privacy policy,
including a suspected PII breach or a spillage. Priority comes from the data at risk (maintainer
PII or readiness data first), a privileged identity's involvement, whether the attack is active,
and its reach across components; categories follow the CSSP's playbook (unauthorized access,
malicious code, denial of service, improper usage, PII breach, spillage). The ISSO is the
incident lead and keeps the records. Third parties (the cloud provider, the access point, the
software factory) report to the CSSP operations center or the ISSO. Each ticket tracks detection
and report times, category, affected components and data, actions, decision maker, status and
closure. Evidence is preserved by the CSSP and the on-call engineer with a chain of custody the
ISSO logs. Containment holds until the CSSP sees no further activity for 72 hours, and
eradication is a rebuild with credential rotation (`triage` in
`artifacts/data/incident-response.yaml`) [[INT-125.A1]] [[INT-099.A1]].

## Roles, responsibilities and authorities

- PER-ISSO: incident lead; keeps the ticket and records; reports to the AO through the AODR and
  to the privacy office; leads notification [[INT-125.A1]] [[INT-099.A2]].
- ERST on-call engineers (PER-DEV): contain and recover inside the account; they may isolate a
  workload, revoke a workload identity or console role, or block a source at CMP-EDGE without
  waiting for approval [[INT-099.A1]].
- PER-ISSM: escalation, IG DoD and law enforcement referrals through Component legal, and the
  authority to take a component or the whole system offline with the PM [[INT-125.A2]].
- PER-PM: authorizes recovery and a shutdown of the system; approves this plan [[INT-125.A3]]
  [[INT-126.A2]].
- PER-PRIV (Component privacy office): handles PII breaches and notice to maintainers
  [[INT-127.A2]].
- Component legal office and public affairs: referrals to law enforcement and any public
  statement [[INT-125.A2]] [[INT-127.A2]].

## Shared responsibility with the CSSP and providers

The CSSP (SVA-001) is the system's cybersecurity point of contact with the cloud provider: it
monitors the forwarded logs 24x7, declares and categorizes incidents, supports handling, reports
to JFHQ-DODIN and receives the reports of any cyber protection team assigned to an EFRAS
incident; it cannot act inside the account [[INT-098.A1]] [[INT-118.A2]]. The program supports
the CSSP's handling, reports events and incidents to it, provides incident artifacts and
safeguards incident information; the cloud provider reports its own findings to the CSSP and
handles incidents in its infrastructure; damage assessment and post-incident feedback go to both
the program and the CSSP, as the cloud record's incident response split sets out
[[INT-118.A2]]. Information flows: logs and alerts to the CSSP, tickets to the ISSO and ISSM,
actions back through the ticket. The CSSP decides on declaration and onward reporting; the
program decides on actions in its account [[INT-098.A1]] [[INT-099.A1]].

## Detection and analysis

Incidents are detected from the CMP-LOGS stream the CSSP correlates in its SIEM with the access
point's traffic logs, from the program's own alerts (break-glass use, export volume spikes,
drift), and from reports by users, engineers and providers. Up-to-date threat intelligence from
the CSSP's feeds and JFHQ-DODIN advisories, the software factory's advisories and the cloud
provider's bulletins is used in log analysis, in correlating events across log sources and in
analyzing adverse events (`detection`). A possible incident is analyzed by the CSSP analyst and
the ISSO, who estimate its impact and scope from the affected components and data and confirm
or close it [[INT-118.A2]] [[INT-125.A1]] [[product/architecture.md#logging]].

## Response and reporting

Every suspected incident goes to the CSSP and the ISSO within one hour. The CSSP reports to
JFHQ-DODIN under CNSSI 1010 within the DoD timelines; the ISSO informs the AO through the AODR
and the chain of command; a PII breach goes to the Component privacy office within one hour
under DoD 5400.11-R; an unauthorized CUI disclosure to the Component CUI program office under
DoDM 5200.01 Volume 4; a classified compromise or spillage, though the system holds no
classified information, to the Component security manager at once under DoDM 5200.01 Volume 3,
identified as a negligent discharge and investigated as willful, negligent or inadvertent; a
loss on ERST's corporate systems to DCSA under DoD 5220.22-M; an apparent federal crime to the
defense criminal investigative organization, law enforcement and the IG DoD; anomalous user
activity to the Component investigative authority with its audit data under chain of custody;
and a cybersecurity deficiency behind a breach to the IG DoD (`reporting_paths`) [[INT-125.A2]]
[[INT-098.A2]] [[INT-127.A2]]. Containment and eradication follow the runbooks in Definitions.
The ISSO keeps the PM, the information owner and the fleet readiness directorate informed; the
privacy office decides on notice to maintainers; public statements go only through public
affairs (`notifications`) [[INT-125.A1]] [[INT-127.A2]].

## Recovery

Recovery starts when the CSSP and the ISSO agree that containment holds and the PM authorizes
it, with the AODR told. The ISSO and the ISSE choose between redeploying in place and a rebuild
and reassess after each step; signatures and snapshot hashes are checked before use, and only a
snapshot from before the compromise is restored, in the contingency plan's order (database,
ingest, API, web); a rebuild in the second region activates ART-CP. The restored account is
scanned against the templates and the data validated before users return; the CSSP watches it
closely for 30 days. Recovery ends when the checks pass and the PM declares normal operations
(`recovery`) [[INT-125.A3]].

## Lessons learned

The ISSO writes an after-action report within 10 working days of each incident and each
exercise; the ISSM reviews it with the CSSP, and its lessons update this plan, the runbooks, the
contingency plan, training and the next exercise. No incident and no exercise has happened yet
[[INT-125.A3]] [[INT-099.A3]].

## Training, testing and plan maintenance

Everyone named in the plan is trained on it when it is approved and yearly, and new on-call
engineers before they join the rotation. The plan is first exercised in the tabletop of 2027-02,
held with the contingency tabletop, and then yearly. Measures: time from discovery to report
(target 1 hour), time to contain, and after-action items closed. The ISSM maintains the plan,
reviews it annually and after every incident or exercise, updates it for system and
organizational changes, and sends each change to the plan's holders, the CSSP and the privacy
office [[INT-099.A3]] [[INT-124.A3]].

## Implementation updates

**2026-11-18, I-2.** Implementation changed nothing in this plan, so `incident-response.yaml`
is not rewritten. As built: export audit events reach the CSSP within 5 minutes (DT-2), which
supports the one-hour reporting target; release 1.5.1 changed nothing in logging or response
[[INT-139.A2]] [[product/test-results.md#dt-2]]. The open database item STG-001 (connection
logging verbosity below the STIG value) narrows what the database logs show an analyst until
release 1.5.2 on 2026-12-10 [[ART-STIG]]. No incident and no exercise has happened yet. The PM's
approval of this plan is still due by 2026-12-15 [[INT-138.A1]].

<!-- I-2 appends "## Implementation updates" (dated: what changed during implementation and
     why) and adds I-2 to touched_by. -->
