---
artifact_id: ART-CMP
run_id: 20261118-synthetic-01
produced_by_task: S-4
touched_by: [S-4, I-2, M-1]
sources: [INT-122.A1, INT-122.A2, INT-123.A1, INT-123.A2, INT-126.A2, INT-093.A1, INT-094.A1, product/architecture.md#configuration, product/architecture.md#updates, product/test-results.md#stig-scan, ART-STIG, INT-138.A1, INT-139.A1, INT-202.A3, INT-203.A2, INT-204.A1, ART-CHG]
handling: CUI
---
# Configuration management plan

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

This plan governs security-focused configuration management (SecCM) of everything inside the
authorization boundary: the program-owned production account, its templates, images and managed
service settings. It implements the Component RMF policy's SecCM duties for the system and the
cm-2, cm-3, cm-6 and cm-8 statements; the platform internals of the cloud region and the
software factory stay under their own plans and boards [[INT-122.A1]] [[INT-093.A1]]. Because
the system holds CUI and maintainer PII with integrity first, every change is reviewed, gated
and signed off, and a change touching the privacy safeguards goes to the board
[[INT-094.A1]] [[product/architecture.md#configuration]]. The values behind this plan are in
`artifacts/data/cm-plan.yaml`. The PM approves the plan with the S-4 plan set by 2026-12-15
[[INT-126.A2]].

## Roles and responsibilities

- PER-PM (system owner): owns SecCM, chairs the board and approves this plan [[INT-122.A1]] [[INT-126.A2]].
- PER-ISSE: keeps the baselines and the STIG summary, performs the security impact analysis and
  the enterprise architecture review [[INT-122.A2]] [[INT-123.A1]].
- PER-ISSO: signs off every production deployment, watches drift and reviews what no tool reaches
  [[INT-094.A1]] [[INT-123.A1]].
- PER-ISSM: approves deviations and bypass procedures in writing and may hold a risky change for
  the AO's office [[INT-122.A1]] [[INT-123.A2]].
- PER-DEV (ERST engineers): implement changes only through pull requests and the pipeline
  [[INT-094.A1]].
- Users have no configuration rights. PER-AO receives significant changes through the ISSM
  [[INT-122.A1]].

## Configuration control board

The PM chairs the EFRAS board; members are the ISSM, the ISSE, the ERST technical lead and the
user representative, the ISSO attends as the deployment sign-off authority, and the privacy
office and the CSSP are guests when a change touches PII or monitoring. It meets monthly; the
chair or the ISSM calls an emergency meeting within one working day. Quorum is the chair (or
the ISSM), the ISSE and the ERST technical lead; it decides by consensus, failing which the chair decides, and the ISSM can hold any change
that raises risk until the AO's office has seen it. Significant changes go to the AO; changes to
the factory or the cloud region go to their own boards [[INT-122.A1]].

## Configuration items and component inventory

The system is decomposed into seven configuration items so that each one is rebuilt by one
template or pipeline job: the edge (CI-EDGE), the application containers with their open-source
libraries (CI-APP), the cluster platform with the node and base images (CI-PLATFORM), the data
tier (CI-DATA), the log pipeline (CI-LOGS), the sandbox (CI-SANDBOX), and CI-SECCM, which puts
the drift scan, scan profiles, gate policies and allow-lists under control as code. Every
inventory item sits in exactly one CI; the open-source libraries go with the container that
carries them, because they change only when that image is rebuilt [[INT-123.A1]]
[[product/architecture.md#configuration]].

## Baseline configurations

The basis is the DISA Kubernetes and PostgreSQL STIGs, the software factory's hardened base
images and the provider's hardened node image. The approved baseline of each CI is its template
and the release manifest at tag 1.5.0, which the board approved [[INT-122.A2]]. The
provider-managed control plane checks and the four database settings the managed service does
not expose are the cloud provider's settings; the STIG summary records them as not applicable to
the program's configuration, naming the provider, and no configuration exception has been
approved (wording corrected at I-2; see `## Implementation updates`) [[ART-STIG]]
[[INT-138.A1]] [[product/test-results.md#stig-scan]]. Two program-fixable database items
(STG-001 connection logging verbosity, STG-002 break-glass role password complexity) are open,
to be fixed in release 1.5.2 (cm-6, partial) [[INT-093.A1]]. A baseline is approved by the board
when it passes the gates and the STIG scan with no open program item other than one tracked for
a fix; a deviation the program keeps is an exception only the AO or the AODR approves
[[INT-122.A2]] [[INT-138.A1]].

## Configuration change control

A change starts as an issue and a pull request with a security and privacy impact note; a second
engineer reviews it; the ISSE checks it against the enterprise architecture; it brings to the
board its test plan, gate results, schedule and rollback steps; it is deployed to pre-production
first, then by the pipeline to production after ISSO sign-off; the drift scan verifies it and
the tracker records it. Significant changes are elevated through the ISSM to the AO. Rollback
redeploys the previous manifest and templates. The monthly node roll, routine dependency updates
and provider patch windows are preapproved but still gated, signed off and minuted. Emergency
patches deploy within 48 hours under the same gates and are analyzed, tested and approved
retroactively at the next meeting. Help desk requests become tracker issues, and patch
management runs through this same path (`change_control`, `procedures` in
`artifacts/data/cm-plan.yaml`) [[INT-122.A1]] [[INT-122.A2]] [[INT-094.A1]]
[[product/architecture.md#updates]].

## Security impact analysis

The ISSE analyzes each change before the board: what it touches (components, data flows,
interconnections, identity path, privacy safeguards), which controls it affects, the test
results, and whether it is significant. Significant means a new interconnection, a new data
type, a boundary or identity-path change, or a change to the safeguards in the PIA or SORN; such
a change is reported to the AO through the ISSM before deployment [[INT-122.A1]]
[[INT-094.A1]].

## Access restrictions for change

Only the pipeline can change the production account; engineers have no standing write access,
and console roles federated with CAC are read-only outside a break-glass event. The one bypass,
the two FIDO2 break-glass console accounts used when the identity broker is down, follows the
procedure BYP-01, coordinated with the ISSO and approved in writing by the ISSM on 2026-11-18
[[INT-123.A2]] [[product/architecture.md#identity]]. SecCM records are readable only by the
program and the AO's office, and edits are logged [[INT-123.A1]].

## Configuration monitoring

The hourly drift scan reports any difference from the templates to the ISSO, who opens an
issue and has it reverted or approved retroactively; the SCAP STIG scan runs monthly and at each
release; the factory scanners check images and dependencies at each build and daily against the
SBOMs. Findings go to the ISSO and the ISSM and, for vulnerabilities, to the remediation track of
ra-5 and si-2 [[INT-123.A1]] [[product/architecture.md#configuration]].

## Records and tools

Change requests, impact analyses, test results, board decisions, minutes, approved baselines and
scan results are kept in the issue tracker and the repository for the life of the system plus one
year, then deleted under the Component records schedule; the media library is the repository and
the factory artifact repository by release tag. Tools are automated first: the enterprise SCAP
scanner is SCAP-validated; the drift scan and the factory scanners have no SCAP-validated
equivalent, and their false positives go through a reviewed allow-list or an ISSO-approved
justification. What no tool reaches is reviewed by hand: the sandbox notebook service monthly and
the WAF rule set at each release (`tools`, `manual_monitoring`, `records` in
`artifacts/data/cm-plan.yaml`) [[INT-123.A1]].

## Plan maintenance and exceptions

The ISSE maintains this plan; the board reviews it annually and with each major release, and
after any change to the board, the tools or the baselines. An exception to the plan needs the
ISSM's written approval and a board entry, and an exception that bypasses a security mechanism
is recorded as a bypass with its procedure [[INT-123.A2]] [[INT-123.A3]].

## Implementation updates

**2026-11-18, I-2.** The STIG summary written at I-1 showed that the plan called the scan's
provider-managed items "deviations the ISSM approves". Only the AO or the AODR approves an
exception to configuration guidance, and these items are not program deviations but the cloud
provider's settings under its IL4 provisional authorization [[ART-STIG]] [[INT-136.A1]]
[[INT-137.A1]]. Corrected: `## Baseline configurations` above, the CI-PLATFORM and CI-DATA
baselines and the SCAP scanner's false-positive handling in `artifacts/data/cm-plan.yaml`
[[INT-138.A1]]. The CIs, the board, the change process, the bypass BYP-01 and the tools are
unchanged; release 1.5.1 (2026-11-07, PT-1 fix and server header) went through the same pipeline
and gates, and no inventory item was added or removed [[INT-139.A1]]. The PM's approval of this
plan is still due by 2026-12-15 [[INT-138.A1]].

## System and Environment Changes (M-1)

**2027-02-01, M-1.** The PM approved this plan on 2026-12-15, meeting the AODR's condition
(POAM-012); the plan text and `cm-plan.yaml`, which has no approval field, said otherwise until
now [[INT-202.A3]]. The change log for the first monitoring cycle is ART-CHG
(`artifacts/data/changes.yaml`): the board approved release 1.6 (CHG-003) on 2027-01-15 after
its gates and developmental test, with the security impact analysis rated significant and
presented to the AODR [[INT-204.A1]]; the provider's control plane patch (CHG-002) went through
as a pre-approved provider patch; and the drift scan caught one unauthorized console change
(CHG-001) [[ART-CHG]]. CHG-001 shows a gap in this plan's change control: the engineers' console
role can still write security groups, so a change can bypass the pipeline and the board, and the
emergency path in the procedures was not used. The plan's CIs, board, tools and baselines are
not changed here; the response to the root cause is M-3's, under RSK-004 [[INT-203.A2]]. The
container baseline check that release 1.6 added to the pipeline (POAM-008) is not yet written
into CI-APP's baseline; that is owed when the SCA verifies it.

<!-- I-2 appends "## Implementation updates" and M-1 appends "## Change updates" (dated:
     what changed in the plan, baselines or board, and why), each adding itself to
     touched_by. -->
