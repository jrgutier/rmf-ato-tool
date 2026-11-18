# EFRAS developer and developmental test results {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real test is described.

Results the program offers the assessor for reuse (DoDI 8510.01 asks assessors to reuse
developer and developmental test results; DoDI 5000.87 asks programs to maximize automated
testing). All tests ran against release 1.5.0 in the pre-production environment, which is built
from the same templates as production.

## Pipeline security gates, release 1.5.0 (2026-10-20) {#pipeline-1-5}

| Gate | Result |
|---|---|
| Static code analysis | pass; 0 high, 4 medium (accepted by the ISSE with rationale in the pipeline record) |
| Dependency scan | pass for efras-api, efras-web, efras-ingest, efras-forecast; efras-report: 2 high (example-imagelib 2.9.1, see `conops.md#limitations` item 2) |
| Container image scan | same 2 high in efras-report; all other images 0 high or critical |
| Infrastructure policy checks | pass: no public IPs, encryption at rest on all stores, logging enabled on all services |
| Dynamic scan (authenticated) | pass; 1 low (verbose server header) fixed in 1.5.1 |
| Image signature verification at admission | pass |

## Developmental test event DT-2 (2026-10-06 to 2026-10-17) {#dt-2}

| Test | Result |
|---|---|
| CAC sign-in through the identity broker for all five roles | pass; users without an approved group are refused |
| Squadron scoping: a `viewer` cannot read another squadron's data through the UI or API | pass (UI); pass (API, 212 crafted requests) |
| Session timeout at 15 minutes | pass |
| Inactive account disabled after 35 days | pass |
| Export audit events reach ECSSP within 5 minutes | pass |
| Ingest rejects a tampered EMIS extract (bad signature) | pass |
| Database point-in-time restore to a new instance | pass; restored in 3 h 10 min |
| Regional failover of the cluster | not tested (see `conops.md#limitations` item 4) |

## STIG and SRG compliance scan (2026-10-22) {#stig-scan}

SCA-witnessed scan of the pre-production cluster: worker nodes against the Kubernetes STIG
(94% compliant; open items are provider-managed control plane checks marked inherited) and the
database against the PostgreSQL STIG (88%; 6 open items, 4 of them not configurable on the
managed service and marked inherited, 2 program-fixable: connection logging verbosity and
password complexity for the local break-glass database role, fix in 1.5.2).

## Penetration test (2026-10-27 to 2026-10-31) {#pentest}

Performed by the fictional component red team against pre-production from NIPRNet through the
access point:

- No unauthenticated access; no injection or cross-site scripting found.
- **Finding PT-1 (moderate):** an `officer` could request a report export for another air wing
  by changing an identifier in the export request; the report service did not repeat the API's
  scoping check. Fixed in 1.5.1 (2026-11-07) and retested pass on 2026-11-10.
- **Finding PT-2 (moderate):** the de-identified export re-identification risk in
  `conops.md#limitations` item 1, demonstrated with a list of 50 DoD ID numbers.
- **Finding PT-3 (low):** the sandbox notebook environment allowed outbound package downloads
  from a public mirror through the NAT gateway allow-list wildcard. Allow-list narrowed
  2026-11-03; retest pending.

## Account review record (2026-10-06) {#account-review}

The ISSO's quarterly review of pre-production: 141 user accounts (all with approved requests),
4 app-admins, 6 cloud console roles, 2 sealed break-glass accounts (not used), 9 service
identities. Two accounts of users who left a pilot squadron were removed during the review
(they had been inactive less than 35 days).
