# ESG architecture {#top}

> **FICTIONAL.** Invented for testing the `rmf` tool; no real system is described.

## Components {#components}

Component IDs are the program's configuration-item numbers; keep them unchanged.

| ID | Component | Type | Inside the boundary | Notes |
|---|---|---|---|---|
| CMP-GW-HW | ESG gateway appliance | hardware | yes | ruggedized fanless appliance with two Ethernet ports (uplink, maintenance) and a field radio module |
| CMP-GW-OS | Gateway operating system | software | yes | hardened Linux-based OS image built by the developer; host firewall; local audit daemon |
| CMP-COLLECTOR | Sensor collector service | software | yes | receives sensor messages from the field radio, validates them, writes them to the buffer and forwards them to IODS |
| CMP-WEBUI | Admin web console | software | yes | HTTPS console for configuration, accounts, diagnostics and update upload |
| CMP-STORE | Local buffer database | software | yes | embedded database holding up to 7 days of telemetry while IODS is unreachable |
| CMP-SENSOR-NET | Field sensor network | hardware | yes | up to 40 battery-powered sensor nodes per site and their firmware |
| CMP-IODS | Installation Operations Data Service | interconnection | no | receives telemetry; a separately authorized system (see `#interconnections`) |
| CMP-ICAM | Installation ICAM Service | service | no | installation identity provider; DoD PKI authentication for remote ESG administrators |
| CMP-ENCLAVE | Installation Network Enclave | service | no | enclave firewall, intrusion detection and network access control in front of every ESG |
| CMP-CSSP | Installation Cybersecurity Service Provider | service | no | log collection (SIEM), monitoring and incident response for the installation |

## Authorization boundary {#boundary}

The ESG boundary is one gateway appliance per site with its operating system, collector,
console and buffer (CMP-GW-HW, CMP-GW-OS, CMP-COLLECTOR, CMP-WEBUI, CMP-STORE), plus the
field sensor nodes paired with it (CMP-SENSOR-NET). All ESG units share one configuration
baseline and are authorized as one system. The installation network switch port is the
boundary edge: IODS, the identity service, the enclave and the CSSP are outside the boundary
and are separately authorized.

## Network architecture {#network}

- **Uplink port** (installation network, enclave VLAN for ESG): outbound TLS 1.3 to IODS on
  one port; outbound syslog over TLS to the CSSP collector; inbound HTTPS to the console only
  from the installation management VLAN. The host firewall denies all other traffic in both
  directions (deny by default, permit by exception).
- **Maintenance port** (on site only): disabled unless a technician enables it with the
  shelter key switch; serves the console to a technician laptop over HTTPS on a link-local
  address; no routing between the maintenance port and the uplink.
- **Field radio**: encrypted, paired link between each sensor node and its gateway; sensor
  nodes have no IP connectivity and cannot reach the uplink.
- The enclave firewall in front of every site switch (CMP-ENCLAVE) enforces the same
  permitted flows at the enclave edge.

## Interconnections {#interconnections}

| ID | System | Direction | Agreement | Authorization |
|---|---|---|---|---|
| IC-1 | Installation Operations Data Service (IODS) | ESG → IODS telemetry | interconnection agreement signed 2026-04-02 | ATO granted 2026-03-15 by the installation AO (fictional), valid to 2029-03-15 |
| IC-2 | Installation ICAM Service | console ↔ identity service | installation service agreement | covered by the enclave authorization (see `#leveraged`) |

## Leveraged authorizations {#leveraged}

ESG inherits controls from two separately authorized providers:

| Provider | Covers | Decision | Date authorized |
|---|---|---|---|
| Installation Network Enclave | enclave boundary protection, network access control, and the Installation ICAM Service | ATO | 2025-11-20 |
| Installation Cybersecurity Service Provider | SIEM log collection and correlation, monitoring, incident response support | ATO | 2026-01-30 |

## Identity and access {#identity}

- Remote administrators and auditors sign in to the console through the installation identity
  service with DoD PKI (smart card); the console maps the identity service's group claims to
  the ESG roles `admin` and `auditor`. Accounts for remote users are created by the identity
  service's account workflow after the ISSO approves an ESG access request.
- The console's local account store holds one break-glass account (`esgadmin`, sealed
  envelope in the program office safe, use logged and reported) and the shared field
  technician account `fieldtech` (see `conops.md#limitations`).
- Console sessions lock after 15 minutes of inactivity. Five failed local sign-ins lock the
  account for 30 minutes.
- The ISSO reviews the console's account list every quarter against the access request
  records; the last review record is dated 2026-09-12.

## Logging {#logging}

- The OS audit daemon, the collector and the console log sign-in success and failure,
  account changes, privilege use, configuration changes, update installation, service start
  and stop, and radio pairing events.
- Logs are forwarded over TLS to the CSSP's SIEM within one minute and held locally for 30
  days. The CSSP reviews and correlates them (CMP-CSSP); the ESG ISSO reviews the ESG-specific
  report weekly.
- The event list was agreed with the CSSP on 2026-05-20 and is reviewed every year.

## Configuration management {#configuration}

- Every unit runs the same signed OS image built by the developer from the General Purpose
  Operating System SRG and the applicable application and web server guidance; the build
  pipeline applies the hardening settings and records deviations.
- A configuration check runs on each unit nightly and reports drift from the approved
  baseline to the SIEM.
- Changes to the baseline go through the RSSPO configuration control board.

## Software updates {#updates}

- The developer publishes a signed monthly update bundle (OS, collector, console, database).
- Units verify the bundle signature before installing it.
- Fielded units are updated during quarterly site visits (see `conops.md#limitations`);
  remote update over the uplink is planned for release 2.2.

## Physical protection {#physical}

Each gateway is in a locked, alarmed equipment shelter; shelter keys are controlled by the
installation facilities office. The appliance case has tamper-evident seals checked at every
site visit.
