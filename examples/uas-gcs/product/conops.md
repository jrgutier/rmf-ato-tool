# ETGCS concept of operations {#top}

> **FICTIONAL — FOR DEMONSTRATION.** No real system, unit or program is described.

## Mission {#mission}

The Example Tactical UAS Ground Control Station (ETGCS) lets a fictional Army aviation
platoon fly the fictional "Kestrel-X" small unmanned aircraft for reconnaissance. Crews use
ETGCS to plan a route, upload it to the aircraft, monitor and command the flight over a
line-of-sight data link, watch and record the aircraft's sensor video, and hand finished
mission products (video clips, still images, flight logs) to the brigade's tactical network.

ETGCS controls one aircraft at a time. It carries no weapons and makes no targeting
decisions; analysts act on its products through separate intelligence systems outside ETGCS.
If ETGCS fails, the aircraft flies its pre-loaded lost-link route home and the platoon loses
reconnaissance coverage until a spare station is set up.

## Program and lifecycle {#program}

- Program office: the fictional Small UAS Ground Systems Product Office (SUGS-PO). The product
  manager is the system owner.
- Acquisition pathway: major capability acquisition, now in engineering and manufacturing
  development (EMD). Six pre-production stations support developmental testing at a test
  range; fielding of 48 stations to 16 platoons is planned after Milestone C and an
  authorization decision.
- Developer and integrator: the fictional Example Avionics Integration Group (EAIG), under
  contract to SUGS-PO.
- Lifecycle state: under development. No station has supported a real operation; test
  stations connect only to a test instance of the brigade network at the range.

## Users {#users}

| User group | Count per station | Access | What they do |
|---|---|---|---|
| Air vehicle operators | 2 | non-privileged, local | plan routes, fly the aircraft, operate the sensor |
| Mission commander | 1 | non-privileged, local | approves the mission plan, releases mission products |
| Field maintainers | ~4 per platoon | privileged, local | install updates, replace hardware, run diagnostics |
| System administrator (brigade S6) | 2 per brigade | privileged, remote over the tactical network | manage accounts and configuration, review logs |
| Intelligence analysts | many | none to ETGCS | receive products on the brigade network; never log in |

Operators, commanders and administrators sign in with their DoD Common Access Card (CAC); see
`architecture.md#identity`. Field maintainers use a shared local account; see the known
limitations below.

## Operating environment {#environment}

- Each station is a two-case transportable kit (laptop workstation, ground data terminal,
  antenna and router) set up in the field from a tactical vehicle. Stations move with the
  platoon and run on vehicle or generator power.
- The station's router connects to the brigade tactical network through the Brigade Tactical
  Network Enclave, which provides the enclave firewall, intrusion detection, the brigade
  directory and log collection as common controls (see `architecture.md#leveraged`).
- The aircraft link is line-of-sight radio up to about 10 km. Jamming or terrain masking
  drops the link; the aircraft then flies its lost-link route.
- Stations are often disconnected from the brigade network for days during exercises.

## Information handled {#information}

- **Command and control data:** routes, commands and aircraft telemetry. Tampering could crash
  or misdirect the aircraft; disclosure reveals where the platoon is looking.
- **Sensor video and still images:** imagery of the area of operations. Disclosure reveals
  coverage and interest; loss means the mission must be flown again.
- **Mission plans and flight logs:** planned and flown routes, times and altitudes.
- **Map and terrain data:** published map products loaded before a mission.
- **Security management data:** accounts, configuration, cryptographic keys and audit records.
- ETGCS holds no personally identifiable information beyond the user names in its account and
  audit records. The program processes this example at the unclassified level only.

## Availability need {#availability}

A station outage stops reconnaissance for one platoon. The unit can tolerate an outage of a
few hours by moving a spare station from another platoon; the program's recovery goal is a
replacement station operating within 4 hours, using a spare kit from brigade stock.

## Known limitations {#limitations}

These are open engineering items the program office has disclosed to the RMF team.

1. **Legacy mission planner without a STIG.** Route planning uses a licensed commercial
   off-the-shelf product, "RouteCraft Planner 7" (fictional vendor Example Geo Software). No
   DISA STIG or vendor security guide exists for it. The integrator hardened it by hand
   against the Application Security and Development SRG and recorded the settings, but nobody
   has assessed the hardening. The vendor ends support for version 7 in 2027-06; the program
   is evaluating a replacement for software release 3.0.
2. **Shared maintenance account.** Field maintainers sign in to the workstation and the router
   with one shared local account, `gcsmaint`, because maintenance often happens without a
   connection to the brigade directory and maintainer CACs are not yet registered with the
   station. The password is shared by the platoon's maintainers and changed every 60 days.
   Maintenance actions in the audit log cannot be tied to a person. The program plans
   per-maintainer local accounts with CAC sign-in that works offline in release 2.4
   (planned 2027-02).
3. **Pending vendor patch for the ground data terminal.** The ground data terminal firmware
   (fictional vendor Example Datalink Systems) has a published vulnerability in its management
   web service that allows a crash from an adjacent network. The vendor's fixed firmware
   (5.2.1) was released 2026-09-21 but has not finished the program's regression testing; it
   is scheduled for the 2026-12 update bundle. Until then the management service is reachable
   only from the station's internal network (see `architecture.md#network`).
