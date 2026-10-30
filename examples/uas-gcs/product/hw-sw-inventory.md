# ETGCS hardware and software list {#top}

> **FICTIONAL — FOR DEMONSTRATION.** Vendors and products are fictional.

Inventory IDs are the program's configuration-item numbers; keep them unchanged. One row
describes the item as installed in every station; quantities are per station.

## Items {#items}

| ID | Item | Kind | Component | Vendor | Product | Version | Qty per station | Priority |
|---|---|---|---|---|---|---|---|---|
| INV-001 | Ruggedized workstation laptop | hardware | CMP-WS-HW | Example Rugged Computing (fictional) | ERC-14 laptop | rev D | 1 | high |
| INV-002 | Workstation operating system image | operating-system | CMP-WS-OS | Example Avionics Integration Group (fictional) | ETGCS workstation image | 2.3.0 | 1 | high |
| INV-003 | Flight control application | software | CMP-C2 | Example Avionics Integration Group (fictional) | etgcs-flight | 2.3.0 | 1 | high |
| INV-004 | Mission planner | software | CMP-PLANNER | Example Geo Software (fictional) | RouteCraft Planner | 7.4 | 1 | moderate |
| INV-005 | Video exploitation application | software | CMP-VIDEO | Example Avionics Integration Group (fictional) | etgcs-video | 2.3.0 | 1 | moderate |
| INV-006 | Ground data terminal | hardware | CMP-GDT | Example Datalink Systems (fictional) | EDS-LOS ground terminal | rev B | 1 | high |
| INV-007 | Ground data terminal firmware | firmware | CMP-GDT | Example Datalink Systems (fictional) | EDS-LOS firmware | 5.1.8 | 1 | high |
| INV-008 | Station router | network-device | CMP-ROUTER | Example Network Gear (fictional) | ENG-T200 tactical router | OS 11.2 | 1 | high |
| INV-009 | Air vehicle data link module | hardware | CMP-AV | Example Datalink Systems (fictional) | EDS-LOS air module | rev B | 1 per aircraft | high |
| INV-010 | Map and terrain data set | software | CMP-PLANNER | published map products | mission map package | per mission | 1 | low |

## Asset priority {#priority}

The flight control path (INV-001..INV-003, INV-006..INV-009) is high: losing or corrupting it
grounds or endangers the aircraft. The planner and video application are moderate: a crew can
fly a pre-planned route without them. Map data is low: it is reloaded each mission.

## Hostnames {#hostnames}

Workstations are named `etgcs-<platoon>-ws` and routers `etgcs-<platoon>-rt` (for example
`etgcs-p1-ws`). None is reachable from the public internet.
