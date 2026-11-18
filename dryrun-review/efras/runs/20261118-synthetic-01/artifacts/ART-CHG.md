---
artifact_id: ART-CHG
run_id: 20261118-synthetic-01
produced_by_task: M-1
touched_by: [M-1]
sources: [product/monitoring/cycle-2026-11.md#top, INT-202.A1, INT-203.A1, INT-204.A1, INT-205.A1, ASM-025, ASM-026]
---
# Change log and security impact analyses

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
| National security system | no | C-1 |
| Missions and business functions | MSN-01 Naval aviation readiness: keeping aircraft mission-capable; MSN-02 Aircraft maintenance and readiness management; MSN-03 Daily readiness reporting for squadron, air wing and fleet (BP-01); MSN-04 Part failure forecasting for early part orders (BP-02); MSN-05 Fleet readiness analysis and de-identified data set export (BP-03) | P-8 |
<!-- END rmf:facts -->

## Monitoring scope and sources

This is the first monitoring cycle under the approved strategy (ART-CONMON), covering 2026-11-01
to 2027-01-31 and recorded on 2027-02-01, one week after the authorization of 2027-01-25. Its
sources are the monitoring records the program handed over, which cover only 2026-11-01 to
2026-11-15 and the pre-production account (drift scans, image and node scans, log and alert
review, account review, privacy and threat records)
[[product/monitoring/cycle-2026-11.md#top]] [[INT-202.A1]]; the change board's account of
release 1.6 [[INT-204.A1]]; and the milestone records R-3 made under the stated progress rule
[[ASM-025]]. Pre-production is outside the authorization boundary but is built from the same
templates, so its records are read as evidence of how the templates and the change process
behave, not of the production account [[ASM-026]]. For 2026-11-16 to 2027-01-31 no monitoring
record exists in the run: no drift event, scan or production deployment is asserted for that
span, and the missing roll-up is itself a monitoring shortfall (POAM-024) [[INT-202.A1]].

## Change log

Three changes, recorded in `artifacts/data/changes.yaml` [[INT-203.A1]] [[INT-204.A1]]:

- CHG-001 (unauthorized, 2026-11-04): console widening of a security group in pre-production,
  detected by the drift scan and reverted within the hour; security impact limited; no board
  decision was needed after the revert; verified by a drift rescan; closed 2026-11-15.
- CHG-002 (requested by the provider, 2026-11-09): managed Kubernetes control plane patch,
  pre-approved under the CM plan; security impact limited; ISSO, on-call engineers and CSSP
  notified; closed 2026-11-15.
- CHG-003 (requested by the PM, 2026-12-16): release 1.6; security impact significant; tested in
  the gates and the developmental test event and presented to the board and the AODR on
  2027-01-15; approved by the board the same day and deployed to pre-production; still open
  pending the production deployment and the SCA's verification [[INT-204.A2]].

## Unauthorized changes and root causes

The drift scan compares the account with the templates hourly and the ISSO reconciles every
difference against the baseline, the inventory and the change requests [[INT-203.A1]]. One
unauthorized change was found in the records: CHG-001. Its root cause is a process failure: the
engineers' console role can still write security groups, so a change can bypass the pipeline
and the board, and the emergency change path was not used. Counseling does not remove the
permission; the response belongs with the configuration risk RSK-004 at M-3
[[INT-203.A2]]. For 2026-11-16 to 2027-01-31 the run holds no drift summary, so it can neither
assert nor rule out further unauthorized changes [[ASM-026]].

## Hosted and interconnected systems

Two interconnected systems, CON-001 and CON-002 in changes.yaml. EMIS holds an ATO valid to
2028-04-22; the exchange stays restricted to synthetic data because the decision's COND-03 keeps
real EMIS records out until the memorandum of agreement is signed (now due 2027-02-26).
The supply status service holds an ATO and its service-level agreement; the connection stands
[[product/architecture.md#interconnections]] [[INT-202.A4]] [[INT-198.A1]]. No system is
hosted.

## Privacy impact of changes

The system processes maintainer PII. CHG-001 and CHG-002 touch no PII and no purpose. CHG-003
changes the privacy posture: the pseudonyms change how exports and the training extract
identify maintainers, and the archive tier keeps audit records with user identifiers for a
year. The privacy office reviewed the PIA against release 1.6 on 2027-01-20, the CIO approved it
on 2027-01-25, and on 2027-02-01 the privacy officer confirmed that the approved PIA describes
the release as deployed; that review is recorded against CHG-003 in pia.yaml [[INT-205.A1]].

## Security impact analyses

- CHG-001: weakened subnet isolation (sc-7) for under an hour in an environment holding
  synthetic data; the drift scan and auto-revert worked; the lasting weakness is the console
  write permission in the change process (cm-3) [[INT-203.A2]].
- CHG-002: closes the vulnerability ECSSP alerted on in the inherited control plane (INV-008);
  no program setting changes; the 2026-11-14 node scan showed no high or critical item
  [[INT-203.A3]].
- CHG-003: changes pt-3, au-11, cm-6, ia-5 and sc-7 implementations; introduces no new
  interface, data type or interconnection; is meant to remove the weaknesses behind POAM-001,
  POAM-006, POAM-007, POAM-008, POAM-016 and POAM-019, unverified by the SCA; leaves the two
  report container highs (POAM-002, POAM-003) [[INT-204.A1]].

## Changes in the environment of operation

No change of mission or information types. ECSSP alerted on the managed Kubernetes version and
the provider patched it (CHG-002). The software factory has still not published the hardened
base image the report container waits on. The CSSP agreement was amended on 2027-01-08 for the
program's one-year log copy. The EMIS legal review has slipped again [[INT-202.A4]]
[[product/monitoring/cycle-2026-11.md#threat]].

## Resulting updates

CHG-003 updated the inventory to release 1.6 (ART-INV), the SSP statements of pt-3, au-11, cm-6
and ia-5 with plan change 1.3 (ART-SSP), and the Monitor iteration of the criticality analysis
(ART-BIA); the PM's plan approvals of 2026-12-15 reached the CM plan and the contingency plan
records, while the pl-2, cp-2 and ir-8 statements and the incident response plan record are
owed to M-4 [[INT-202.A3]]. The POA&M and SAR keep their items and findings open for M-2 and M-3. CHG-003 is a
significant change, but the authorization of 2027-01-25 was decided with it in the package and
its conditions carry the reassessment, so no new authorization decision is needed
[[INT-204.A1]] [[INT-198.A1]].
