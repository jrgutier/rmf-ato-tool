# ETGCS data flows {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real system is described.

| ID | From | To | Path | Information | Protection |
|---|---|---|---|---|---|
| DF-1 | flight control (CMP-C2) | air vehicle (CMP-AV) via GDT (CMP-GDT) | aircraft link | routes and commands | encrypted radio link with per-mission keys; commands authenticated |
| DF-2 | air vehicle (CMP-AV) | flight control (CMP-C2) and video (CMP-VIDEO) via GDT | aircraft link | telemetry and sensor video | encrypted radio link |
| DF-3 | mission planner (CMP-PLANNER) | flight control (CMP-C2) | workstation, local file | mission plan | local only; file integrity hash checked on import |
| DF-4 | video (CMP-VIDEO) | brigade intelligence system (CMP-BIS) | uplink via router | mission products | TLS with mutual certificate authentication |
| DF-5 | workstation and router | enclave log collector (CMP-BTNE) | uplink | audit records | syslog over TLS |
| DF-6 | workstation (CMP-WS-OS) | brigade directory (CMP-BTNE) | uplink | authentication requests | LDAPS |
| DF-7 | brigade S6 management subnet | workstation and router | uplink | administration sessions | encrypted remote administration; CAC sign-in |
| DF-8 | maintainer removable media | workstation, router, GDT | local | update bundles and map data | bundle signature checked before install |
| DF-9 | workstation (CMP-WS-OS) | GDT management service (CMP-GDT) | station internal network | GDT configuration | HTTPS; vendor administrator password |

## Mission flow {#mission}

The crew plans a route (DF-3), uploads it and flies (DF-1), and watches and records video
(DF-2). After the flight the commander releases products, which go to the brigade
intelligence system when the uplink is up (DF-4) and queue otherwise.

## Management flow {#management}

Remote administration (DF-6, DF-7) is the normal path when connected. Updates and maps come
by removable media (DF-8). GDT configuration happens only from the workstation (DF-9).

## Audit flow {#audit}

See `architecture.md#logging`; DF-5 runs whenever the uplink is available.
