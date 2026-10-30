---
artifact_id: ART-BND
run_id: example-synthetic-01
produced_by_task: P-11
touched_by: [P-11, P-16, C-1]
sources: [INT-012.A1, INT-012.A2, INT-012.A3, INT-013.A1, INT-013.A2, INT-019.A1, INT-019.A2, INT-022.A4, product/architecture.md#boundary]
---
# Authorization boundary

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Tactical UAS Ground Control Station | C-1 |
| Acronym | ETGCS | C-1 |
| System ID | ETGCS-REG-SIM-0001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ETGCS-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/MODERATE; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-M | S-1 |
<!-- END rmf:facts -->

## Authorization boundary

The boundary is one station kit: CMP-WS-HW, CMP-WS-OS, CMP-C2, CMP-PLANNER, CMP-VIDEO,
CMP-GDT, CMP-ROUTER and CMP-AV, with the router's uplink port as the edge [[INT-012.A1]]. All
stations share one configuration baseline and are authorized as one type-authorized system
[[INT-013.A1]]. The airframe is outside, covered by airworthiness [[INT-012.A1]]. The enclave and
the brigade intelligence system are outside because each is separately authorized and run by
the brigade, not the program [[INT-013.A2]]. Components are recorded in
`artifacts/data/boundary.yaml`.

## Network architecture

One isolated station segment joins the workstation, the GDT management port and the router;
the GDT management web service listens only there. The uplink permits only outbound TLS to the
intelligence system's product drop, syslog over TLS, LDAPS to the brigade directory and inbound
remote administration from the S6 management subnet; all else is denied. The encrypted aircraft
link is never routed to the uplink [[INT-012.A2]] [[product/architecture.md#network]].

## Data flows

Nine flows, DF-1 to DF-9 [[product/data-flows.md#top]]: the aircraft link flows (DF-1, DF-2)
use encrypted radio with per-mission keys; the uplink flows (DF-4 to DF-7) use TLS, LDAPS or
encrypted administration with CAC; DF-3 is a local file with an integrity hash; DF-8 brings
update bundles and maps on removable media with signature checks. DF-9, GDT configuration over
HTTPS with a single vendor administrator password, is the weakest internal flow
[[INT-012.A3]].

## External components

- **CMP-BTNE, Brigade Tactical Network Enclave:** provides boundary protection, intrusion
  detection, the brigade directory, log collection and incident response support; ATO
  2025-05-30 (fictional) [[product/architecture.md#leveraged]] [[INT-013.A2]]. C-1 records this
  ATO as leveraged authorization LA-01 on the component [[INT-022.A4]].
- **CMP-BIS, brigade intelligence system:** receives mission products over IC-1; ATO
  2025-08-14 (fictional); the interconnection agreement is an unsigned draft, which the AO
  expects signed before fielding [[product/architecture.md#interconnections]] [[INT-013.A2]].

## Enterprise architecture

The system is a mission system at the tactical edge behind the Brigade Tactical Network Enclave,
which provides the brigade directory, log collection, boundary protection and incident response
as shared services over IC-2; it feeds the brigade intelligence system over IC-1. It uses no
cloud service and no other shared service [[INT-019.A1]]. The architecture places the
disconnected-operation requirements in the station and the connected services in the enclave;
the one gap is that planner and GDT logs have no path to the enclave (REQ-06 in ART-REQ)
[[INT-019.A2]].
