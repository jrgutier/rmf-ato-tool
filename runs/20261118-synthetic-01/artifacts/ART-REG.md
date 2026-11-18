---
artifact_id: ART-REG
run_id: 20261118-synthetic-01
produced_by_task: P-18
touched_by: [P-18, C-1, C-3]
sources: [INT-056.A1, INT-056.A2, INT-056.A3, INT-057.A1, ASM-014, ART-BND, INT-058.A2, ART-SD, INT-069.A2, ART-CAT]
---
# System registration

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

## Registry and registration record

EFRAS has been registered in the Component's eMASS instance since 2025-10-01, as record
EFRAS-0001 (fictional). eMASS is both the Component's tool and the channel through which the
system reports to the DoD, so no ERS import is needed [[INT-056.A1]]. The product package holds
no registry extract, so the record rests on the ISSM's statement [[ASM-014]]. The PM confirms the
record and is accountable for keeping it current [[INT-057.A1]].

## Registered characteristics

The record holds:

- the system's purpose, fleet readiness decision support;
- its owner, the ARSPO product manager;
- its AO;
- the boundary reference of ART-BND;
- its life-cycle state, under development [[INT-056.A1]] [[ART-BND]].

EFRAS has one deployment, the production account. No other Component receives it under
reciprocity, so no deployment site is listed [[INT-057.A1]].

## Ports, protocols and services

EFRAS is a Component system, not an Enterprise system. The one port that crosses the DoD
boundary, HTTPS on 443 through the access point (connection CONN-01), was registered in the DoD
PPSM Registry on 2026-10-15 as PPSM-EFRAS-0443 (fictional), together with the DISA cloud
connection request [[INT-056.A2]]. The other connections in `boundary.yaml` run inside the cloud
and through that attachment [[ART-BND]].

## Registration updates owed

The ISSM updates the record at four points [[INT-056.A3]]:

- after C-1, with the characterization;
- after C-3, with the approved categorization;
- at the authorization decision (R-5);
- at disposal (M-7).

Between those points, the ISSO keeps the contacts current [[INT-056.A3]].

## Registration updates made

- C-1, 2026-11-18: the characterization from ART-SD entered in the record: the system
  identifier (the eMASS record number stays the registry record, not the identifier), version,
  owning organization, type, classification, users, interconnections, leveraged authorizations
  and CSSP alignment [[INT-058.A2]] [[ART-SD]].
- C-3, 2026-11-18: the approved categorization of ART-CAT and its Privacy Overlay sets, entered
  after the AODR's approval [[INT-069.A2]] [[ART-CAT]].
