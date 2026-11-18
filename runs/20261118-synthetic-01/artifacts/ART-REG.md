---
artifact_id: ART-REG
run_id: 20261118-synthetic-01
produced_by_task: P-18
touched_by: [P-18]
sources: [INT-056.A1, INT-056.A2, INT-056.A3, INT-057.A1, ASM-014, ART-BND]
---
# System registration

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| Authorization boundary | EFRAS-BND-1 | P-11 |
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

Between those points, the ISSO keeps the contacts current. No update is recorded yet in
`registration.yaml` [[INT-056.A3]].
