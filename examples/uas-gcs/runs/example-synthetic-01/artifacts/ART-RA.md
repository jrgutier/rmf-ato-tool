---
artifact_id: ART-RA
run_id: example-synthetic-01
produced_by_task: P-14
touched_by: [P-14, R-2, M-3]
sources: [INT-017.A1, INT-017.A2, INT-017.A3, INT-015.A1, ART-ORG-CONTEXT, ART-INFOTYPES, ART-BND, ASM-003, INT-100.A1, INT-101.A1, ART-SAR, INT-112.A1, INT-113.A1, INT-113.A2]
---
# System risk assessment

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

## Method and scope

SP 800-30 qualitative assessment of one station kit inside the boundary in ART-BND, with the
organization's threat themes as the threat input [[INT-017.A1]] [[ART-ORG-CONTEXT]] [[ASM-003]].
Likelihood and impact use the five-level scale (very low, low, moderate, high, very high) and
the Table I-2 matrix combines them into a risk level; ratings are compared with the AO's
tolerance in ART-ORG-CONTEXT [[INT-017.A1]]. Impact draws on the information types and their
provisional levels in ART-INFOTYPES [[ART-INFOTYPES]].

## Threat sources and events

| ID | Threat event | Threat source | Likelihood | Impact | Initial risk |
|---|---|---|---|---|---|
| TE-1 | Jamming or spoofing of the aircraft link causes loss of control or false telemetry | adversary electronic warfare | moderate | moderate | moderate |
| TE-2 | Captured station kit is used to extract mission data or keys | adversary, field capture | low | moderate | low |
| TE-3 | Malicious code on maintenance media enters the workstation, router or GDT | adversary, insider error | moderate | high | moderate |
| TE-4 | Compromised commercial component or integrator build is installed | supply chain adversary | low | high | low |
| TE-5 | Misuse or error under the shared maintenance account goes unattributed | insider | moderate | moderate | moderate |
| TE-6 | Adjacent-network attacker crashes the GDT management service | adversary on the station segment | moderate | moderate | moderate |
| TE-7 | Unpatched or misconfigured mission planner is exploited | adversary via removable media | low | moderate | low |
| TE-8 | Attacks go unnoticed while disconnected or in local-only logs | adversary | moderate | moderate | moderate |

Events and sources follow the organization's themes applied to the station [[INT-017.A1]];
ratings are the ISSM's [[INT-017.A3]].

## Vulnerabilities and predisposing conditions

- Mission planner (CMP-PLANNER) without a STIG; manual hardening unassessed; vendor support
  ends 2027-06 (TE-7) [[INT-017.A2]].
- Shared `gcsmaint` account on workstation and router: maintenance actions cannot be tied to a
  person (TE-5) [[INT-017.A2]].
- GDT firmware crash vulnerability in the management service; fix 5.2.1 in regression testing
  (TE-6) [[INT-017.A2]].
- Single vendor administrator password on the GDT management service (TE-6) [[INT-017.A2]].
- Planner and GDT logs are local only (TE-8); stations are often disconnected for days
  [[INT-017.A2]] [[ART-ORG-CONTEXT]].

## Mitigating conditions

The GDT management service listens only on the isolated station segment; the uplink is
deny-by-default; the aircraft link is encrypted with per-mission keys and never routed to the
uplink; disks are encrypted; transport cases carry tamper seals; update bundles are signed; the
enclave provides boundary protection, intrusion detection and log collection as common controls
[[INT-017.A3]] [[ART-BND]].

## Risk summary

1. TE-5 shared maintenance account (moderate): drives individual accountability requirements.
2. TE-6 GDT firmware vulnerability (moderate): drives flaw remediation and the GDT
   authenticator requirement.
3. TE-3 removable media (moderate): drives media and integrity requirements.
4. TE-1, TE-8 (moderate); TE-2, TE-4, TE-7 (low). TE-4 still drives the supply chain
   requirement because its impact is high.

No risk is rated high; TE-5 and TE-6 are the top two [[INT-017.A3]].

## Privacy risk

PII is limited to user names and CAC-derived identifiers in INF-05 [[INT-015.A1]]. The risk to
individuals is low: exposure of a captured kit's audit records (TE-2) reveals who operated it,
mitigated by disk encryption [[INT-017.A3]].

## Update after assessment (R-2)

The assessment confirmed every weakness listed above and the ratings are revised as follows,
with the risks themselves in `artifacts/data/rar.yaml` [[ART-SAR]] [[INT-101.A1]]:

- TE-5 confirmed and raised to impact high: the shared credential works on every workstation
  and router and the GDT administrator password never changed, so one disclosure reaches the
  whole fleet without a trace; likelihood moderate, risk moderate (RSK-001) [[INT-100.A1]].
- TE-8 confirmed at moderate/moderate: planner and GDT logs are local only and station logs
  are not reviewed while disconnected (RSK-002) [[INT-100.A3]].
- TE-6 confirmed at moderate/moderate: the crash reproduces from the station segment, not from
  the uplink; firmware 5.2.1 is still in regression testing (RSK-003) [[INT-100.A2]].
- TE-7 changed: likelihood raised from low to moderate for the planner library flaws that have
  no vendor fix (RSK-003); the unassessed planner hardening stays low (RSK-004)
  [[INT-100.A2]] [[INT-101.A1]].
- TE-4 confirmed low/high, now tied to the planner end of support in 2027-06 (RSK-006)
  [[INT-101.A1]].
- New, outside the original events: plans not written or tested (RSK-005, moderate) and
  continuous monitoring, interconnection and privacy approvals not yet in place (RSK-007 to
  RSK-009, low) [[INT-101.A1]].
- TE-1, TE-2 and TE-3: no finding changed their ratings [[ART-SAR]].

No risk is high; the overall risk is moderate, inside the AO's tolerance [[INT-101.A2]].

## Ongoing Risk Response (M-3)

The first monitoring cycle (2026-10-01 to 2026-10-28) was analyzed against the risks above. It
found no new finding, no incident, no tamper-seal exception and no new threat information from
the CSSP, so no rating changes and no new risk is added [[ART-SAR]] [[INT-112.A1]]:

- RSK-001 (TE-5) stays moderate: the 2026-10-14 screen-lock change under `gcsmaint` recurred
  and could not be attributed, but the pre-upload check caught it; release 2.4 stays the
  mitigation [[INT-112.A1]] [[INT-113.A3]].
- RSK-003 (TE-6, TE-7) stays moderate: the 2026-10-24 rescan confirmed the workstation and
  router fixes, but the GDT management-service flaw (firmware 5.1.8) and the two planner
  library flaws that drove the rating remain [[ART-SAR]] [[INT-112.A1]].
- RSK-002 (TE-8) stays moderate: the weekly hand review of planner and GDT logs now runs every
  week, but only on the test-range stations and without correlation [[INT-112.A1]].
- RSK-006 (TE-4) stays low/high: the planner vendor confirmed end of support for 2027-06 and no
  release 3.0 replacement is selected; a slip past the 2027-01-29 selection milestone goes to
  the AO as a change in risk [[INT-113.A2]].

Response: every risk keeps the response `mitigate` and its POA&M items. Delaying the GDT fix to
the 2026-12 bundle (firmware 5.2.1 still in regression testing) is the PM's decision,
coordinated with the requirements sponsor's representative, the AODR and the CSSP, with the
interim restriction to the station internal network confirmed in place through the cycle. The
planner library flaws stay under the AO's existing risk acceptance; nothing in the cycle calls
for a new decision [[INT-113.A1]]. The overall risk stays moderate, inside the AO's tolerance
[[INT-112.A1]].
