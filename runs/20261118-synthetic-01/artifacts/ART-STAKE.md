---
artifact_id: ART-STAKE
run_id: 20261118-synthetic-01
produced_by_task: P-9
touched_by: [P-9]
sources: [INT-020.A1, INT-020.A2, INT-020.A3, INT-021.A1, INT-021.A2, INT-022.A1, product/stakeholders.md#roles, ART-ORG-CONTEXT]
---
# Stakeholder register

<!-- BEGIN rmf:facts -->
_No system facts are set yet (facts.yaml)._
<!-- END rmf:facts -->

## Stakeholders and interview roster

The register follows the program's stakeholder list, confirmed by the system owner for this
release [[INT-020.A1]] [[product/stakeholders.md#roles]], with the Component officials of
ART-ORG-CONTEXT [[ART-ORG-CONTEXT]]. All holders are fictional role labels.

| Stakeholder | Persona ID | Interest in the system | Security concerns, loss concerns and trust expectations | Interviewed for | Trace |
|---|---|---|---|---|---|
| Fleet readiness directorate (mission owner, capability sponsor) | PER-SPONSOR | owns the capability needs statement and the readiness mission | adversary seeing aggregated fleet readiness; wrong readiness figures from altered data; expects readiness shown exactly as the maintenance system records it | P-4, P-8, P-9, P-15, P-16 | [[INT-021.A2]] |
| Fleet maintenance data steward (information owner: maintenance and readiness data, maintainer PII, derived forecasts and reports) | PER-IO | sets the rules and impact values for the data the service holds | integrity first, then confidentiality of aggregated data and maintainer records; exports follow the release rules and de-identified exports stay de-identified | P-9, C-1, C-2 | [[INT-022.A1]] [[INT-020.A2]] |
| Supply status data owner, Example Supply Status Service (information owner: supply status) | PER-IO (answers only for supply status) | provides supply status under a service-level agreement | its data used only as agreed; to be asked for its own information type at C-2 | C-2 | [[INT-020.A2]] [[INT-022.A1]] |
| ARSPO product manager (PM and system owner; owns audit records) | PER-PM | owns the system, its POA&M and its schedule | MVCR deployment by 2027-02-01, the release cadence, closing known limitations on time; expects providers to keep their authorizations current and EMIS to sign its agreement | P-9 to P-17, C-1, S-4, A-6 | [[INT-020.A3]] [[INT-020.A2]] |
| ARSPO ISSM, EFRAS ISSO | PER-ISSM, PER-ISSO | run the RMF effort and day-to-day security | security posture and evidence for the package | P-14 onward | [[INT-020.A1]] |
| ERST technical lead and security engineer (developer, contractor) | PER-DEV, PER-ISSE | build and operate the service | secure design, pipeline gates, approved dependencies | P-16, S-4, I-1 | [[INT-020.A1]] [[ART-ORG-CONTEXT]] |
| ARSPO test lead | PER-CDT | runs developmental test events the assessor may reuse | test evidence reused in assessment | A-2, A-3 | [[INT-020.A1]] |
| Naval Aviation Systems AO and AODR, Aviation Business Systems | PER-AO, PER-AODR | decide on authorization | residual risk within the Component tolerance | C-3, R-2 to R-4 | [[INT-020.A1]] [[ART-ORG-CONTEXT]] |
| Business systems SCA team | PER-SCA | independent assessment | independence and access to evidence | A-1 to A-4 | [[INT-020.A1]] |
| Component CIO, CISO, risk board, privacy officer | PER-CIO, PER-CISO, PER-RE, PER-PRIV | organization-level risk context, common controls, privacy | system within the Component's tolerance; privacy of maintainer data | P-1 to P-7; PER-PRIV also P-12 to P-17, C-3 | [[ART-ORG-CONTEXT]] [[INT-021.A2]] |
| Example GovCloud, Example Enterprise Cloud Access Point, Example Software Factory | PER-CCP | provide inherited controls | systems configuring their side; their own authorizations stay current | S-1, S-4, A-3 | [[INT-020.A1]] [[ART-ORG-CONTEXT]] |
| Example Cybersecurity Service Provider | PER-CSSP | boundary monitoring and incident support | logs forwarded and incidents reported | S-4, S-5, M-2 | [[INT-020.A1]] |
| EMIS program (source system) | not interviewed (see below) | provides the nightly maintenance extract | interconnection under an interim approval until the agreement is signed | — | [[INT-020.A2]] [[INT-020.A3]] |
| Squadron maintenance personnel, maintenance officers and chiefs, fleet readiness analysts | PER-UR | daily users | trustworthy dashboards and forecasts; availability within 72 hours | P-8, P-15, C-1 | [[INT-021.A1]] [[INT-019.A1]] |

Every information owner is identified: the fleet maintenance data steward for the maintenance,
readiness and maintainer data and what is derived from them, the supply status data owner for
supply status, and ARSPO for the system's own audit records [[INT-020.A2]] [[INT-022.A1]].

## Users represented

The user communities are squadron maintenance personnel, maintenance officers and chiefs, and
fleet readiness analysts, all non-privileged web users; the maintenance officer from pilot
squadron 1 speaks for them as user representative (PER-UR) [[INT-021.A1]]
[[product/stakeholders.md#roles]]. Application administrators, cloud operations engineers and
data scientists are ERST or ARSPO staff and are represented by the program and developer
personas [[INT-020.A1]].

## Stakeholders not interviewed

Senior leaders receive briefing slides by e-mail and never log in; the capability sponsor speaks
for them [[INT-021.A1]]. Air wing and fleet staff who consume readiness reports are represented
by the sponsor and the user representative [[INT-021.A1]]. The EMIS program is informed through
the interconnection agreement and ISSM-to-ISSM coordination, and the data steward, not EMIS, sets
the rules for the data [[INT-020.A2]]. The PEO, the program's decision authority on the software
pathway (PER-MDA), is kept informed through program reviews rather than RMF interviews
[[INT-020.A3]].
