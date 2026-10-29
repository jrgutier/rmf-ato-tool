# ESG data flows {#top}

> **FICTIONAL.** Invented for testing the `rmf` tool; no real system is described.

| ID | From | To | Path | Information | Protection |
|---|---|---|---|---|---|
| DF-1 | sensor node (CMP-SENSOR-NET) | collector (CMP-COLLECTOR) | field radio | sensor readings and alarms | paired, encrypted radio link; collector rejects unpaired nodes and malformed messages |
| DF-2 | collector (CMP-COLLECTOR) | buffer (CMP-STORE) | local | sensor readings and alarms | local only; buffer is on the encrypted data partition |
| DF-3 | collector (CMP-COLLECTOR) | IODS (CMP-IODS) | uplink, installation network | sensor readings and alarms | outbound TLS 1.3 with mutual certificate authentication |
| DF-4 | gateway (CMP-GW-OS, CMP-COLLECTOR, CMP-WEBUI) | CSSP SIEM (CMP-CSSP) | uplink | audit records | syslog over TLS |
| DF-5 | administrator workstation (management VLAN) | console (CMP-WEBUI) | uplink | configuration, account and update data | HTTPS; sign-in through the identity service (DF-6) |
| DF-6 | console (CMP-WEBUI) | identity service (CMP-ICAM) | uplink | authentication requests and assertions | TLS; signed assertions |
| DF-7 | technician laptop | console (CMP-WEBUI) | maintenance port, on site | diagnostics, configuration, update bundles | HTTPS on a link-local address; local sign-in |

## Telemetry flow {#telemetry}

Sensor nodes send readings every 30 seconds and alarms immediately (DF-1). The collector
writes every message to the buffer (DF-2) and forwards it to IODS (DF-3); if IODS is
unreachable it keeps forwarding from the buffer when the link returns, oldest first.

## Management flow {#management}

Remote administration (DF-5, DF-6) is the normal path. On-site maintenance (DF-7) is used for
sensor replacement, radio pairing and quarterly updates.

## Audit flow {#audit}

Every component logs locally and forwards to the CSSP SIEM (DF-4); see
`architecture.md#logging`.
