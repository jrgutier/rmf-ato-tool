---
artifact_id: ART-SD
run_id: example-synthetic-01
produced_by_task: C-1
touched_by: [C-1, I-2]
sources: [INT-061.A1, INT-062.A1, INT-064.A1, INT-022.A1, INT-022.A2, INT-022.A3, INT-022.A4, INT-023.A1, INT-023.A2, product/conops.md#mission, product/conops.md#users, product/conops.md#environment, product/architecture.md#components]
---
# System description

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

## Mission and purpose

The system lets a platoon plan, fly and exploit reconnaissance missions with one Kestrel-X small
unmanned aircraft at a time, and hands finished mission products to the brigade network. It
carries no weapons and makes no targeting decisions; if a station fails, the aircraft flies its
lost-link route home and the platoon loses coverage until a spare is set up
[[INT-022.A3]] [[product/conops.md#mission]]. It is under development in EMD with six test
stations; 48 stations for 16 platoons follow Milestone C and an authorization decision
[[INT-022.A2]].

## System description and functions

One station kit holds the workstation (CMP-WS-HW, CMP-WS-OS) with the flight control
(CMP-C2), mission planner (CMP-PLANNER) and video (CMP-VIDEO) applications, the ground data
terminal (CMP-GDT), the station router (CMP-ROUTER) and the aircraft data link endpoint
(CMP-AV) [[product/architecture.md#components]]. Crews plan a route, upload it over an
encrypted line-of-sight link, command the aircraft, record and clip sensor video, and release
products over the router uplink [[INT-022.A3]]. The mission planner is a COTS product with no
STIG, hardened by hand and not yet assessed [[product/conops.md#limitations]]. Components and
flows are recorded in ART-BND and ART-INV.

## Users

Six user groups are recorded in `artifacts/data/users.yaml`: USR-OPERATOR and USR-COMMANDER
(non-privileged, CAC), USR-ADMIN (privileged, remote with CAC), USR-MAINTAINER (privileged,
through the shared `gcsmaint` account, so maintenance actions are not attributable),
USR-BREAKGLASS (sealed emergency account) and USR-ANALYST (no logical access; receives
products elsewhere) [[INT-023.A1]] [[INT-023.A2]] [[product/conops.md#users]].

## Operating environment

Stations are two-case transportable kits set up in the field from tactical vehicles, running on
vehicle or generator power, kept under platoon physical control, and often disconnected from
the brigade network for days [[product/conops.md#environment]]. During EMD they connect only
to a test instance of the brigade network at the range [[INT-022.A2]].

## Interconnections and leveraged authorizations

IC-1 sends mission products to the brigade intelligence system (CMP-BIS); its interconnection
agreement is an unsigned draft to be signed before fielding. IC-2 connects to the Brigade
Tactical Network Enclave (CMP-BTNE) under its connection approval process [[INT-022.A4]].
The system inherits boundary protection, intrusion detection, the directory, log collection
and incident response support from the enclave's ATO, recorded as LA-01 in
`artifacts/data/leveraged-authorizations.yaml`; the intelligence system is an interconnection
only [[INT-022.A4]] [[product/architecture.md#leveraged]].

## Update Control Implementation Information (I-2)

The six test stations are built as described here, at release 2.3.0, with no change to the
components, users or interconnections during implementation [[INT-061.A1]] [[INT-064.A1]].
DT-1 confirmed the inherited enclave services in place: CAC groups in the brigade directory and
workstation and router logs collected after reconnect; planner and GDT logs are still not
forwarded [[INT-062.A1]]. `users.yaml` and `leveraged-authorizations.yaml` are unchanged.
