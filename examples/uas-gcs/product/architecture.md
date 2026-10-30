# ETGCS architecture {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real system is described; vendors are fictional.

## Components {#components}

Component IDs are the program's configuration-item numbers; keep them unchanged.

| ID | Component | Type | Inside the boundary | Notes |
|---|---|---|---|---|
| CMP-WS-HW | Ruggedized workstation laptop | hardware | yes | one per station; encrypted disk; two Ethernet ports |
| CMP-WS-OS | Workstation operating system | software | yes | hardened Windows-based image built by the integrator |
| CMP-C2 | Flight control application | software | yes | aircraft command, telemetry display, lost-link settings |
| CMP-PLANNER | Mission planner (RouteCraft Planner 7) | software | yes | COTS route planning; no STIG (see `conops.md#limitations`) |
| CMP-VIDEO | Video exploitation and recording application | software | yes | records, clips and annotates sensor video |
| CMP-GDT | Ground data terminal | hardware | yes | line-of-sight radio to the aircraft, with vendor firmware and a management web service |
| CMP-ROUTER | Station router | network-device | yes | joins the workstation and GDT; uplink to the brigade network |
| CMP-AV | Kestrel-X air vehicle data link endpoint | hardware | yes | the aircraft's radio and flight computer interface (the airframe is covered by airworthiness, not by this boundary) |
| CMP-BTNE | Brigade Tactical Network Enclave | service | no | enclave firewall, IDS, brigade directory, log collection; separately authorized |
| CMP-BIS | Brigade intelligence system | interconnection | no | receives mission products; separately authorized |

## Authorization boundary {#boundary}

The ETGCS boundary is one station kit: the workstation with its operating system and three
applications (CMP-WS-HW, CMP-WS-OS, CMP-C2, CMP-PLANNER, CMP-VIDEO), the ground data terminal
(CMP-GDT), the station router (CMP-ROUTER) and the aircraft data link endpoint (CMP-AV). All
stations share one configuration baseline and are authorized as one type-authorized system.
The router's uplink port is the boundary edge: the brigade enclave and the brigade
intelligence system are outside and separately authorized.

## Network architecture {#network}

- **Station internal network:** the workstation, GDT management port and router on one
  isolated segment. The GDT management web service listens only on this segment.
- **Uplink:** the router permits outbound TLS to the brigade intelligence system's product
  drop (one port), outbound syslog over TLS to the enclave log collector, LDAPS to the brigade
  directory, and inbound remote administration from the brigade S6 management subnet only.
  Everything else is denied in both directions.
- **Aircraft link:** encrypted line-of-sight radio between the GDT and the aircraft using
  keys loaded before each mission; no IP routing from the aircraft link to the uplink.
- When the uplink is down the station keeps flying and recording; products queue for later
  transfer.

## Interconnections {#interconnections}

| ID | System | Direction | Agreement | Authorization |
|---|---|---|---|---|
| IC-1 | Brigade intelligence system (CMP-BIS) | ETGCS → BIS mission products | interconnection agreement draft, unsigned (planned before fielding) | ATO 2025-08-14 (fictional), valid to 2028-08-14 |
| IC-2 | Brigade Tactical Network Enclave (CMP-BTNE) | both | enclave connection approval process | enclave ATO (see `#leveraged`) |

## Leveraged authorizations {#leveraged}

| Provider | Covers | Decision | Date authorized |
|---|---|---|---|
| Brigade Tactical Network Enclave | enclave boundary protection and intrusion detection, brigade directory (account management for CAC users), central log collection and review, incident response support | ATO | 2025-05-30 (fictional) |

## Identity and access {#identity}

- Operators, mission commanders and remote administrators sign in to the workstation with
  CAC against the brigade directory; cached credentials allow CAC sign-in for 14 days while
  disconnected. Roles (`operator`, `commander`, `admin`) come from directory groups that the
  ISSO approves.
- The shared local maintenance account `gcsmaint` exists on the workstation and the router
  (see `conops.md#limitations`). One sealed break-glass administrator account per station is
  held by the platoon leader.
- The GDT management web service uses a single vendor administrator account whose password is
  set per station at installation.
- Screens lock after 15 minutes idle; 3 failed sign-ins lock a local account for 15 minutes.
- The ISSO reviews accounts quarterly; the last record is dated 2026-09-08.

## Logging {#logging}

- The workstation OS, flight control and video applications log sign-in, account and
  privilege events, configuration changes, mission upload, command sessions and product
  export. The router logs administrative sessions and denied traffic. The mission planner and
  the GDT keep only local application logs that are not forwarded.
- Logs are held locally for 90 days and forwarded to the enclave log collector when the uplink
  is available. The brigade S6 reviews the collector; the ETGCS ISSO reviews a weekly station
  report during test events.

## Configuration management {#configuration}

- The workstation image follows the Windows STIG and the applicable application guidance;
  the router follows the network device STIG. The integrator records deviations in the STIG
  summary. The mission planner was hardened by hand (see `conops.md#limitations`).
- A compliance check runs at every station start-up and before each mission upload and
  reports drift to the local log.
- Baseline changes go through the SUGS-PO configuration control board.

## Software updates {#updates}

- The integrator publishes a signed quarterly update bundle (OS, applications, router and GDT
  firmware) after regression testing. Field maintainers install it from removable media; the
  station checks the bundle signature before install.
- The GDT firmware fix 5.2.1 is pending regression testing (see `conops.md#limitations`).

## Physical protection {#physical}

Stations stay with the platoon under its physical control at all times; transport cases lock
and carry tamper seals checked at each setup. Removable media are controlled by the platoon.
