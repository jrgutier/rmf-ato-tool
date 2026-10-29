# ESG concept of operations {#top}

> **FICTIONAL.** Invented for testing the `rmf` tool; no real system is described.

## Mission {#mission}

The Example Sensor Gateway (ESG) gives the installation security operations center a
near-real-time picture of perimeter intrusion and environmental conditions (temperature,
flooding, power loss) at remote sites of a fictional installation. Each ESG unit sits in a
locked equipment shelter at a remote site, collects readings from up to 40 field sensor nodes
over a short-range field radio network, buffers them, and forwards them over the installation
network to the Installation Operations Data Service (IODS), where operators watch alarms.

ESG is a sensing and forwarding system. It makes no decisions and actuates nothing: operators
act on alarms through separate systems outside ESG.

## Program and lifecycle {#program}

- Program office: the fictional Remote Site Sensing Program Office (RSSPO), which owns the
  system (the program manager is the system owner).
- Acquisition pathway: major capability acquisition, now in engineering and manufacturing
  development. Twelve pre-production units are installed at test sites; fielding of 60 units
  is planned after an authorization decision.
- Developer and integrator: the fictional Example Systems Integration Team (ESIT), under
  contract to RSSPO.
- Lifecycle state: under development. No unit has carried operational alarm traffic; the test
  sites feed a test instance of IODS.

## Users {#users}

| User group | Count | Access | What they do |
|---|---|---|---|
| SOC operators | ~25 | none to ESG directly | read ESG alarms in IODS; never log in to ESG |
| ESG system administrators | 3 | privileged, remote, through the admin web console | manage configuration, accounts and software updates; review logs |
| Field technicians | ~10 | privileged, on site, through the admin web console on the maintenance port | replace sensors, re-pair radios, run diagnostics during site visits |
| Auditors (ISSO staff) | 2 | read-only, remote, through the admin web console | review audit logs and configuration reports |

Remote administrators and auditors sign in through the installation identity service with
their DoD PKI credential (see `architecture.md#identity`). Field technicians sign in locally;
see the known limitation below.

## Operating environment {#environment}

- Remote sites are fenced; equipment shelters are locked and alarmed, with keys controlled by
  the installation facilities office. Sites are visited about once a quarter.
- Each ESG connects to the installation network through the site's network switch, inside the
  Installation Network Enclave, which provides the enclave firewall, intrusion detection and
  network access control as common controls.
- Field sensors talk to the ESG over a short-range, encrypted field radio network. Radio
  jamming or a dead site link stops alarms from that site; IODS flags a site that has been
  silent for 5 minutes.

## Information handled {#information}

- **Sensor telemetry and alarms:** intrusion, door, temperature, water and power events with
  site and sensor identifiers. Disclosure would reveal where the installation's perimeter
  sensing is weak; tampering could hide an intrusion or raise false alarms.
- **Configuration and security management data:** device configuration, firewall rules,
  account records and cryptographic keys of the ESG.
- **Audit records:** sign-in, administrative-action and configuration-change events.
- ESG stores no personally identifiable information beyond the user names in its account and
  audit records, and the program has asked the privacy office to confirm this.

## Availability need {#availability}

An ESG outage removes perimeter sensing at one site until it is restored; the SOC compensates
with guard patrols, which it can sustain for several days. The program's stated recovery goal
is a replacement unit on site within 72 hours.

## Known limitations {#limitations}

These are open engineering items the program office has disclosed to the RMF team.

1. **Shared field-technician account.** Field technicians sign in to the admin web console on
   the maintenance port with a single local account, `fieldtech`, whose password is shared by
   the technician team and changed every 90 days. Sites have no network path to the
   installation identity service during some maintenance tasks, so the program kept a local
   account. Individual technicians cannot be told apart in the audit records. The program
   plans per-technician local accounts with smart-card login in software release 2.3
   (planned for 2027-03).
2. **Field patch cadence.** The developer publishes a monthly software update bundle, but
   fielded units are updated only during quarterly site visits, because remote update over
   the installation network is not yet approved. At the last scan, two units ran an update
   bundle more than 60 days old (see `test-results.md#vuln-scan`). Remote update is planned
   for software release 2.2 (planned for 2026-12).
