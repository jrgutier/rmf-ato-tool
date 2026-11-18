# EFRAS stakeholders {#top}

> **FICTIONAL — FOR DEMONSTRATION.** Every organization and role holder below is invented.
> Names are role labels, not people.

## Roles {#roles}

| Role | Holder | Organization | Notes |
|---|---|---|---|
| Authorizing official (AO) | Naval Aviation Systems AO (fictional) | fictional naval aviation PEO, AO office | signs the authorization decision |
| AO designated representative | AODR, Aviation Business Systems | AO office | prepares the decision; reviews packages |
| Program manager / system owner | Product Manager, ARSPO | ARSPO | owns the system and the POA&M |
| Mission owner / sponsor | Fleet readiness requirements officer | fictional fleet readiness directorate | owns the capability needs statement; mission owner for the cloud offering |
| Information system security manager (ISSM) | ARSPO ISSM | ARSPO | manages the RMF effort |
| Information system security officer (ISSO) | EFRAS ISSO | ARSPO | day-to-day security operations, account and log reviews |
| Information system security engineer (ISSE) | ERST security engineer | ERST (developer) | security architecture, pipeline security gates |
| Security control assessor (SCA) | Business systems SCA team | fictional independent component assessment activity | independent assessment |
| Privacy officer | Component privacy officer | fictional component privacy office | PIA approval, SORN, privacy controls |
| User representative | Maintenance officer, pilot squadron 1 | fictional pilot squadron | speaks for maintainers and officers |
| Common control provider (cloud) | Example GovCloud | fictional cloud service provider | IL4 provisional authorization; inherited physical, infrastructure controls |
| Common control provider (platform) | Example Software Factory ISSM | fictional software factory | pipeline, image hardening, inherited SA/SR/CM controls |
| Cybersecurity service provider | ECSSP | fictional CSSP | boundary monitoring, incident support |
| Developer | ERST technical lead | ERST | builds releases |
| Chief developmental tester | ARSPO test lead | ARSPO | runs DT events whose results the SCA may reuse |
| Information owner | Fleet maintenance data steward | fictional fleet maintenance directorate | owns maintenance data rules and release decisions |

## Governance {#governance}

- The ARSPO configuration control board (chair: product manager; members: ISSM, ISSE, ERST
  technical lead, user representative) approves major releases and baseline changes; minor
  releases deploy through the pipeline's automated gates with ISSO sign-off.
- The ISSM briefs the AODR monthly; the product manager briefs the mission owner each quarter.
