---
artifact_id: ART-ORG-CONTEXT
run_id: 20261118-synthetic-01
produced_by_task: P-1
touched_by: [P-1, P-2, P-3, P-4, P-5, P-6, P-7]
sources: [INT-001.A1, INT-001.A2, INT-002.A1, INT-003.A1, INT-004.A2, INT-005.A1, INT-006.A1, product/stakeholders.md#roles, ASM-001, ASM-002, ASM-003, ASM-004]
---
# Organizational risk context

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

## RMF role assignments

The fictional naval aviation Component assigns the RMF roles below for its organization and
for the portfolio that holds this system. Holders are role labels, not people
[[product/stakeholders.md#roles]]; the Component-level appointments rest on the CIO's and the
privacy officer's statements, since the product package carries no appointment letters
[[INT-001.A1]] [[INT-002.A1]] [[ASM-001]]. The appointment instruments, position designations,
work role codes and qualifications of each record are in `artifacts/data/org-context.yaml`
(records RA-01 to RA-12) [[ASM-002]].

| Role | Persona ID | Assigned to (role label) | Appointed by | Trace |
|---|---|---|---|---|
| Component CIO | PER-CIO | Component CIO | DoD Component head | [[INT-001.A1]] |
| Component CISO (Component SCA) | PER-CISO | Component CISO | Component CIO | [[INT-001.A1]] |
| Risk executive (function) | PER-RE | Component risk board, chaired by the SAORM | DoD Component head (charter) | [[INT-001.A1]] |
| Senior component official for privacy | PER-PRIV | Component privacy officer | DoD Component head | [[INT-002.A1]] |
| Authorizing official | PER-AO | Naval Aviation Systems AO | DoD Component head | [[INT-001.A2]] |
| AO designated representative | PER-AODR | AODR, Aviation Business Systems | AO | [[INT-001.A2]] |
| Security control assessor (delegated) | PER-SCA | Business systems SCA team, independent component assessment activity | Component CISO | [[INT-001.A3]] |
| Program manager and system owner | PER-PM | Product Manager, ARSPO | Component Acquisition Executive | [[INT-001.A2]] |
| ISSM | PER-ISSM | ARSPO ISSM | PM / system owner | [[INT-001.A2]] |
| ISSO | PER-ISSO | EFRAS ISSO | PM / system owner | [[INT-001.A2]] |
| User representative | PER-UR | Maintenance officer, pilot squadron 1 | PM / system owner | [[INT-001.A2]] |
| ISSE (contractor) | PER-ISSE | ERST security engineer | PM / system owner | [[INT-001.A4]] |
| Common control provider (cloud) | PER-CCP | Example GovCloud | not an appointment: provides controls under its DoD provisional authorization | [[product/stakeholders.md#roles]] [[INT-001.A4]] |
| Common control provider (platform) | PER-CCP | Example Software Factory ISSM | not an appointment: provides controls under the factory's own ATO | [[product/stakeholders.md#roles]] [[INT-001.A4]] |
| Cybersecurity service provider | PER-CSSP | ECSSP | not an appointment: service agreement with the program | [[product/stakeholders.md#roles]] |

Separation of duties: no individual holds two roles that conflict. The AO is neither the system
owner nor a provider of the common controls EFRAS inherits, each of which is authorized
under its own authorization [[INT-001.A4]]. The SCA is a delegate of the CISO in an activity
that reports outside the PEO and ARSPO, which is the independence the AO requires
[[INT-001.A3]]. Security and privacy are held by different officials who coordinate monthly
[[INT-002.A3]]. The ARSPO ISSM also acts as the program's privacy representative for the PIA;
there is no separate system privacy officer [[INT-002.A2]]. Code-signing certificates are not
used by the organization; EFRAS images are signed by the software factory under its own ATO
[[INT-001.A5]].

<!-- P-2..P-7 each append their section below, in this order, and add themselves to
     touched_by. An optional task that is not performed (P-4, P-6) still appends its heading
     with one traced sentence saying the organization has none.
     - P-2 "## Risk management strategy and risk tolerance": how risk is framed, assessed,
       responded to and monitored; the SP 800-30 rating scale; the tolerance statement;
       which risk levels need Component CIO concurrence before an ATO; the maximum
       authorization period; the organizational remediation period for weaknesses; and how
       risk assessments are maintained: what triggers an update, how often, what is
       updated and how results are communicated (S-5 records it in conmon.yaml
       risk_assessment, M-4 applies it).
     - P-2 "## Privacy program": the Component privacy and civil liberties program, its SCOP
       and PCLO with their staffing and reporting lines to the DoD SAOP, complaint and
       alleged violation procedures, training and awareness, how privacy controls are
       designated (program management, common, system-specific, hybrid), and whether the
       SCOP approves or, in an OSD Component, primarily advises.
       P-2 also appends "## Software program": the Component's direction under DoWI 8430.01
       for software the organization develops or deploys: governance adapted to iterative
       development and continuous delivery, delegated decisions verified by automated
       evidence, the software workforce (DoW Cyber Workforce Framework work roles, training,
       career paths, performance assessments), records of software assets, and any exception
       to the issuance requested through the E2P Portal. Each system's software.yaml program
       section (S-4) applies it.
     - P-3 "## Organization-level risk assessment": enterprise threats, dependencies and
       aggregated risks, and when the assessment was last updated.
     - P-4 "## Organizationally tailored baselines and profiles": approved or directed
       tailored baselines, overlays and CSF profiles systems must start from; an overlay the
       organization develops itself also goes in org-context.yaml developed_overlays.
     - P-5 "## Common controls available for inheritance": table: provider | persona ID |
       controls offered | full or partial | provider authorization and its status.
     - P-6 "## Impact-level prioritization": how systems of the same impact level are
       placed in low, moderate and high sub-categories.
     - P-7 "## Organizational continuous monitoring strategy": the metrics, frequencies and
       reporting every system's strategy (S-5) must implement; and the Component's
       vulnerability management program (DoDI 8531.01 2.10) that S-5 and M-3 read: the
       organizations designated to direct and manage it and to coordinate with JFHQ-DODIN, the
       asset, configuration, remediation and mitigation programs that support it, the
       prioritization and scheduling plan for deploying patches, updates and directed
       actions, the guidance to system owners on mitigation deployment and who may accept
       risk, what the Component requires system owners to mitigate, and its audits of
       patching, compliance and reporting. -->

## Risk management strategy and risk tolerance

The Component Cybersecurity Risk Management Program, owned by the CIO, is organization-wide;
it implements CNSSP 22, its Annex A issuances and DoDI 8500.01, frames, assesses, responds to
and monitors risk, and is integrated with mission and business risk management, strategic and
operational planning and the budget [[INT-004.A1]]. Every Component system, this one among
them, is assigned to it [[INT-004.A1]].

**Framing.** The frame assumes persistent nation-state interest in readiness and logistics
data, reliance on commercial cloud and shared DoD platforms, and DoD boundary and CSSP services
in place; it is constrained by shared contract vehicles, inherited platform controls and fixed
fielding dates; its priorities are availability, then integrity of readiness information, then
the privacy of personnel records [[INT-005.A1]]. The enterprise refuses outright any system
that exposes CUI to the public internet or runs without a CSSP [[INT-005.A1]].

**Rating scale.** Risk is rated on the SP 800-30 Rev. 1 five-level scale (Very Low, Low,
Moderate, High, Very High), semi-quantitatively, by the ISSM with the ISSE and reviewed by the
SCA [[INT-005.A3]].

**Risk tolerance.** By type of loss the Component tolerates Moderate risk to mission operations
and organizational assets and Low risk to individuals, other organizations and the Nation
[[INT-004.A2]]. Concretely, for an AO [[INT-004.A2]]:

| Rule | Value |
|---|---|
| Risk an AO may accept alone | Very Low, Low, Moderate |
| Risk that needs Component CIO concurrence before an ATO | High, Very High (overall system risk) |
| Risk never accepted without the senior official for privacy | Very High risk to individuals' privacy |
| Maximum authorization period | 3 years (shorter for a decision with conditions) |
| Remediation or POA&M item with milestones, from the finding | Very High 15 days, High 30 days, Moderate 90 days, Low 180 days |

**Response and monitoring.** Responses are acceptance within the AO's limits, avoidance,
mitigation through controls and POA&M items, and sharing or transfer through providers and
agreements, chosen by comparing risk with the tolerance and the cost of each course of action
[[INT-005.A4]]. The risk executive function is the Component risk board, chaired by the
senior accountable official for risk management; its quarterly forum takes all types and
sources of risk, including aggregated risk, and it reports quarterly to AOs and senior leaders
[[INT-005.A2]].

**Keeping risk assessments current.** A system updates its risk assessment at least annually
and at once after a significant change, a new High or Very High finding, a relevant CSSP threat
advisory or a change in the organization-level assessment; the update covers threats,
vulnerabilities, likelihood, impact and the risk register, and the ISSM sends it to the AO and
the board's portfolio register within 30 days [[INT-005.A5]].

**External entities and references.** The cloud provider, the software factory, the CSSP and
the EMIS program are the external entities in an actual risk relationship; the AO accepted each
one's ongoing risk, EMIS on an interim e-mail approval until its agreement is signed
[[INT-004.A4]]. The enterprise cloud access point, left off that list at P-2, was added at C-1
as EXT-05, and the cloud entity carries its offering name, Example GovCloud IL4 region
[[INT-060.A7]]. The governing references were checked for later editions on 2026-11-02 and
none was found [[INT-004.A5]] [[ASM-004]]. The structured record is in
`artifacts/data/org-context.yaml` (program, policies, resources, risk_frame, governance,
risk_assessment_guidance, risk_response, external_entities, reference_currency) and the C-SCRM
frame in `artifacts/data/scrm-org.yaml` [[INT-003.A2]] [[INT-003.A3]].

## Privacy program

The Component runs its privacy and civil liberties program under DoDI 5400.11
[[INT-006.A1]]. The Component privacy officer is the senior component official for privacy
(SCOP); the privacy and civil liberties officer (PCLO) is the SCOP's deputy in the same office,
with three privacy analysts, and the SCOP reports to the DoD senior agency official for privacy
through the Department's privacy, civil liberties and transparency office [[INT-006.A1]]. The
Component is not an OSD Component, so the SCOP approves for the Component's privacy program
rather than only advising [[INT-006.A1]].

Complaints and alleged violations go to the PCLO, who logs each one, investigates within 30
days and reports breaches under the DoD breach response plan; all personnel take annual privacy
training and bulk PII handlers take role-based training before access [[INT-006.A2]]. Privacy
controls are designated as follows: privacy program management controls belong to the SCOP's
office; privacy awareness training and the complaint process are common controls; notice,
consent and authority to process are hybrid (SORN and notice templates common, the system's
own notice system-specific); PII minimization and retention are system-specific
[[INT-006.A3]]. Privacy risk to individuals is tolerated only at Low [[INT-006.A3]].

For a capability fielded under urgent capability acquisition (DoDI 5000.81), the AO of the
receiving portfolio makes the certification determination and may issue an IATT or ATO within
days; programs ask the CIO's office, which names that AO [[INT-004.A6]].

## Software program

For software the Component develops or deploys, governance follows the software acquisition
pathway: release decisions are delegated to programs whose pipelines produce automated evidence,
the software workforce is coded to DoD Cyber Workforce Framework work roles with training and
career paths, software assets are recorded in each program's inventory, and no exception to the
software issuance has been requested [[INT-004.A6]] [[ASM-004]].

## Organization-level risk assessment

The Component risk board's organization-level assessment was last updated on 2026-09-30; it is
redone each year at the end of the fiscal year, and between cycles when a threat advisory or an
incident changes a rating [[INT-007.A1]] [[ASM-005]]. It rates risk on the SP 800-30 scale
[[INT-005.A3]]:

| ID | Organization-level risk | Likelihood | Impact | Risk | Trace |
|---|---|---|---|---|---|
| ORG-R1 | Nation-state collection of aggregated readiness and logistics data from business systems | Moderate | High | High (aggregated fleet-wide data) | [[INT-007.A1]] |
| ORG-R2 | Compromise of a shared software factory or its base images reaching every program on it | Moderate | High | High | [[INT-007.A1]] |
| ORG-R3 | Outage of a commercial cloud region or cloud access point taking down many business systems | Low | Moderate | Low | [[INT-007.A1]] |
| ORG-R4 | Exposure of personnel PII held in bulk by business systems | Moderate | Moderate | Moderate | [[INT-007.A1]] |
| ORG-R5 | Interconnections operating on interim approvals without signed agreements | Moderate | Moderate | Moderate | [[INT-007.A1]] |
| ORG-R6 | Re-identification of de-identified PII data sets shared outside a system | Moderate | Moderate (to individuals) | Moderate, above the Low tolerance for individuals | [[INT-009.A1]] |

Threat sources are nation-state actors seeking logistics and readiness data, criminal groups
after personnel data, privileged insiders in cloud accounts and accidental operator
misconfiguration, drawn from CSSP alerts, DoD and CISA advisories and the supply chain sharing
communities [[INT-008.A1]]. Vulnerabilities and predisposing conditions that repeat across the
Component's POA&Ms are third-party library and base image vulnerabilities waiting on platform
releases, short program-held audit log retention, unexercised contingency plans,
interconnections running before their agreements are signed, and break-glass accounts that
cannot use CAC [[INT-008.A2]]. Other privacy risks the privacy officer records are use of bulk
PII beyond its notice, for example for model training, and retention beyond the records
schedule; every system that exports de-identified PII must show how it prevents
re-identification [[INT-009.A1]].

The Component's dependencies are the commercial cloud regions under DoD provisional
authorizations, the DoD software factories and their upstream image suppliers, the enterprise
cloud access points and identity broker, and the CSSPs [[INT-007.A2]]. Shared supply chain risk
information arrives with the CSSP threat feed, the threat input to this assessment and to each
system risk assessment (P-14), and does not change the current ratings [[INT-008.A3]]. System
risk assessments start from ORG-R1 to ORG-R6 and say which apply [[INT-007.A2]].

## Organizationally tailored baselines and profiles

The Component has approved no organizationally tailored baseline of its own and publishes no
CSF profile [[INT-010.A1]]; the capability sponsor's directorate has no mission-specific
baseline or profile for the readiness and maintenance capability area [[INT-011.A1]]. Systems
start from what the risk board directs, approved with the risk management strategy
[[INT-010.A2]]:

| Baseline or overlay | Scope | Approval | Trace |
|---|---|---|---|
| CNSSI 1253 security control baselines, with the DoD assignment values | every Component NSS, selected by its categorization | directed by the risk board with the strategy | [[INT-010.A1]] |
| NSS privacy control baseline (CNSSI 1253) | every Component NSS | directed by the risk board with the strategy | [[INT-010.A1]] |
| CNSSI 1253 Privacy Overlays | every system that processes PII, decided with the privacy officer from the overlay's applicability questions | directed by the risk board with the strategy | [[INT-010.A2]] |
| Other CNSSI 1253 overlays | where their applicability questions say so; none directed for all systems | — | [[INT-010.A2]] |

The Component develops no overlay of its own, so `org-context.yaml` holds no
`developed_overlays` [[INT-010.A2]]. The C-SCRM Risk Response Framework at Levels 1 and 2 is in
`artifacts/data/scrm-org.yaml` (`response_framework`) and changes no common control baseline
[[INT-003.A8]].

## Common controls available for inheritance

The Component CISO's common control list names four providers for business systems in the
cloud, each designated by the CISO and none appointed by a program [[INT-012.A1]]. Each
package (plan, assessment report and, where there are deficiencies, POA&M) was assessed by a
qualified assessor the provider arranged, approved by the AO accountable for those controls
before publication and made available to ARSPO at onboarding; providers report compliance
status monthly [[INT-012.A2]] [[ASM-006]]. A system inherits by citing the provider in its
SSP, configuring its own side and recording the leveraged authorization [[INT-012.A3]].

| Provider | Persona ID | Controls offered | Full or partial | Provider authorization and status | Trace |
|---|---|---|---|---|---|
| Example GovCloud IL4 region | PER-CCP | pe-2, pe-3, pe-6, pe-13, pe-14, mp-6 | full | DoD provisional authorization IL4, 2024-09-18; current | [[INT-013.A1]] [[product/architecture.md#leveraged]] |
| Example GovCloud IL4 region | PER-CCP | si-2, cp-9 | partial (managed service internals; the program patches its workloads and sets its own backups) | as above | [[INT-013.A1]] |
| Example Enterprise Cloud Access Point | PER-CCP | sc-7, si-4 | partial (the program controls its subnets, security groups and WAF) | ATO 2025-01-10; current | [[INT-013.A2]] [[product/architecture.md#leveraged]] |
| Example Software Factory | PER-CCP | sa-10, sa-11, sa-15, cm-14, sr-3, sr-11 | partial (the program owns its code, dependencies and admission policy) | ATO 2025-10-01; current, with an open POA&M item for the delayed hardened base image | [[INT-013.A3]] [[INT-012.A3]] |
| Example Cybersecurity Service Provider | PER-CSSP | si-4, au-6, ir-4, ir-6, ra-5 | partial (the program forwards its logs and reports incidents) | services under the CSSP's own ATO, ARSPO service agreement 2026-04-01; current | [[INT-013.A4]] [[product/architecture.md#leveraged]] |
| Component privacy office | PER-PRIV | pm-18, pm-19, pm-26, pm-27; the common part of pt-5 and the privacy part of at-2 | full for pm-18, pm-19, pm-26, pm-27; partial for pt-5 and at-2 | organization-level privacy program controls, not under a system authorization; status reported in the annual privacy program review | [[INT-014.A1]] |

The software factory's package is the only one with a deficiency that touches the controls
offered [[INT-012.A3]]. The privacy office's controls are program-level controls with no
separate authorization package, so `org-context.yaml` `common_controls` lists only the four
authorized providers [[INT-014.A1]].

## Impact-level prioritization

The Component does not place systems of one impact level in low, moderate and high
sub-categories and has no prioritization criteria of that kind [[INT-015.A1]]. Its systems are
national security systems that keep a separate confidentiality, integrity and availability value
under CNSSI 1253 rather than a high-water mark, and for portfolio reporting the risk board groups
them by their confidentiality impact value; resources follow the organization-level risk
ratings, not a sub-category [[INT-015.A1]].

## Organizational continuous monitoring strategy

The Component's continuous monitoring program has been in place since the risk board approved
its strategy on 2024-10-01; the board governs it and the CISO's continuous monitoring working
group runs it [[INT-016.A1]] [[ASM-007]]. Its objectives are to keep control effectiveness known
for every system and common control provider, detect unauthorized change, keep threat and
vulnerability awareness current and keep visibility of all assets; its results feed the
organization and system risk assessments [[INT-016.A1]].

Every system strategy (S-5) must meet these minimum frequencies, and may be more frequent but
never less [[INT-017.A1]]:

| Family | Minimum frequency | What | Applies to |
|---|---|---|---|
| ra | weekly | vulnerability scanning of cloud-hosted and internet-facing systems | systems, common controls |
| cm | monthly | configuration baseline checks | systems, common controls |
| au | weekly | audit log review | systems, common controls |
| ac | quarterly | account reviews | systems |
| si | monthly | flaw remediation status | systems, common controls |
| ir | annually | incident response plan test | systems |
| cp | annually | contingency plan test | systems |
| ca | annually | assessment of at least a third of each system's controls, all within the authorization period | systems, common controls |

Scanning, asset discovery and CSSP log correlation are automated; control assessments, account
reviews and POA&M reviews are manual procedures verified as repeatable [[INT-017.A2]]. Metrics
are scan coverage, overdue POA&M items by severity, configuration drift and mean time to
remediate; system owners report monthly to the AO and the Component dashboard, and the risk board
receives a quarterly posture report [[INT-017.A2]]. The program is reviewed annually (latest
2026-09-15, which shortened the scanning minimum to weekly) and was assessed against SP 800-137A
on 2026-03-16, with one finding owned by the CISO and due 2026-12-31 [[INT-016.A2]]. A system may
move to ongoing authorization once it holds an initial authorization and its monitoring meets the
Component program; none does so at its initial decision [[INT-016.A3]].

**Vulnerability management (DoDI 8531.01).** The CISO's office directs and manages the
Component's vulnerability management program and coordinates with JFHQ-DODIN through the CSSPs;
it rests on the asset inventory, configuration management, POA&M-tracked remediation and the
CSSP's mitigation support [[INT-017.A3]]. Patches and directed actions are scheduled by severity:
critical and high within the strategy's remediation periods (15 and 30 days), directed actions
by their stated deadline [[INT-017.A3]]. System owners deploy mitigations but may not accept risk
themselves; the AO accepts what is not mitigated in time, within the tolerance. The Component
requires owners to mitigate every critical and high vulnerability and every directed action, and
the CISO's office audits patching, compliance and reporting quarterly [[INT-017.A3]]. The C-SCRM
measures that complement this strategy are in `artifacts/data/scrm-org.yaml` (`measures`)
[[INT-003.A8]].
