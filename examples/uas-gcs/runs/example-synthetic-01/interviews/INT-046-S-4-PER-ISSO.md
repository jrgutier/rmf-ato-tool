---
interview_id: INT-046
run_id: example-synthetic-01
task: S-4
persona: PER-ISSO
date: 2026-10-29
topics: [mp family, pe family, removable media, physical protection, field environment]
---
# INT-046 — S-4 — PER-ISSO

### Q1 {#INT-046.Q1}
Asked of: PER-ISSO · Task: S-4 · Control focus: mp-1, mp-2, mp-3, mp-4, mp-5, mp-6, mp-7
How are removable media and the workstation disk controlled, marked, stored, moved and sanitized?

**A1 {#INT-046.A1}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#physical]] [[product/architecture.md#updates]] [[product/conops.md#information]] [[ART-ORG-CONTEXT]]
> Media policy and the sanitization procedure come from the Component cybersecurity program.
> The only removable media are the update-bundle media and the media that carry map data in
> and mission products out when the uplink is down. The platoon controls them: only the crew
> and the authorized maintainers handle them, each is labeled with its handling marking for
> unclassified information, and they are kept and moved in the locked, sealed transport
> cases. The workstation disk is encrypted, so a lost kit does not expose its data. Media
> leaving the platoon, and a station's disk before it is turned in or repaired, are sanitized
> under the Component procedure and the ISSO records it. The workstation image allows only
> media the ISSO has registered and scans each one before use.

### Q2 {#INT-046.Q2}
Asked of: PER-ISSO · Task: S-4 · Control focus: pe-1, pe-2, pe-3, pe-3.1, pe-4, pe-5, pe-6, pe-6.1, pe-8, pe-8.3, pe-9, pe-10, pe-11, pe-12, pe-13, pe-13.1, pe-13.2, pe-14, pe-15, pe-16, pe-17, pe-22, pe-23
How is the station physically protected, given that it is a field kit and not a building?

**A2 {#INT-046.A2}** respondent: simulated · tag: SIMULATED · basis: [[product/architecture.md#physical]] [[product/conops.md#environment]] [[product/conops.md#availability]] [[product/architecture.md#components]] [[ART-ORG-CONTEXT]]
> Physical and environmental policy comes from the Component program. The station is a
> two-case kit that stays with the platoon under its physical control at all times; there is
> no fixed facility, server room or building of our own. The platoon leader keeps the roster
> of crew and maintainers allowed at the station, and the crew on shift watches the kit, its
> screens and its cables while it is set up. The cases lock and carry tamper seals that are
> checked at each setup and each move, and kits move only in platoon vehicles. Every case and
> component carries its configuration-item label. Power comes from the vehicle or a generator
> through the kit's own cables. Because there is no facility, the building controls (alarms,
> visitor logs, emergency shutoff, lighting, fire and water protection, climate control,
> facility siting) have nothing to apply to; a station lost to power, weather or damage is
> replaced from the brigade spare stock within 4 hours, and the aircraft flies its lost-link
> route home. Nobody runs the station from home or another work site.
