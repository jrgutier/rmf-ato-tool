---
artifact_id: ART-RAR
run_id: example-synthetic-01
produced_by_task: R-2
touched_by: [R-2, R-3]
sources: [ART-SAR, ART-POAM, ART-RA, ART-ORG-CONTEXT, INT-100.A1, INT-100.A2, INT-100.A3, INT-101.A1, INT-101.A2, INT-101.A3, INT-102.A1, INT-102.A2, INT-103.A1]
---
# Risk assessment report

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

## Method

The 69 open SAR findings and the open or not-reviewed STIG items were grouped into nine risks
by shared threat event (TE-1 to TE-8 in ART-RA) and root cause; each risk lists its findings
and POA&M items in `artifacts/data/rar.yaml` [[ART-SAR]] [[ART-POAM]] [[INT-101.A1]]. The
assessor gave each group's exploitability, compensating factors and evidence confidence
[[INT-100.A1]] [[INT-100.A2]] [[INT-100.A3]]. The AODR, acting for the AO under delegation,
rated likelihood and impact separately on the SP 800-30 five-level scale and derived each level
from Table I-2 [[INT-101.A1]] [[ART-RA]]. Threat information is the threat events in ART-RA;
no newer threat assessment was supplied for this simulated run [[ART-RA]].

## Risks

Risks rated moderate (likelihood / impact):

- **RSK-001 Unattributable misuse of shared privileged accounts** (moderate / high, level
  moderate). One shared maintenance credential and an unchanged GDT administrator password give
  privileged access to every station with no attributable record; 20 findings plus CAT II STIG
  items STG-001 and STG-002. Limited by segment-only reachability, custody of the kit and disk
  encryption [[INT-100.A1]] [[INT-101.A1]].
- **RSK-002 Attacks go unnoticed in local-only and unreviewed logs** (moderate / moderate).
  Planner and GDT logs never leave the devices and station logs are not reviewed while
  disconnected; 13 findings. It compounds RSK-001, since misuse is both unattributed and unseen
  [[INT-100.A3]] [[INT-101.A2]].
- **RSK-003 Exploitation of known GDT and mission planner vulnerabilities** (moderate /
  moderate). The GDT web service crash reproduces from the station segment but not the uplink;
  firmware 5.2.1 is in regression testing; the planner library flaws have no vendor fix
  [[INT-100.A2]] [[INT-101.A1]].
- **RSK-005 Incidents and outages handled without written, tested plans** (moderate /
  moderate). Contingency, incident response and configuration management plans are drafts,
  untested, with no training given; 13 findings [[INT-100.A3]] [[INT-101.A1]].

Risks rated low: RSK-004 unassessed planner hardening (low / moderate), RSK-006 planner end of
support (low / high, rising after 2027-06), RSK-007 continuous monitoring and governance not yet
operating, RSK-008 unsigned IC-1 agreement and RSK-009 pending privacy approvals (each low /
low) [[INT-101.A1]].

## Risk determination

Overall risk: **moderate**. The highest single risk is moderate and none is high; the combined
mitigations do not lower the overall level because RSK-001 and RSK-002 reinforce each other
[[INT-101.A2]]. The organizational tolerance lets the AO accept low or moderate residual risk;
a high residual risk would need Component CIO concurrence [[ART-ORG-CONTEXT]]. The determination
is within tolerance, so no concurrence beyond the AO is needed [[INT-101.A2]]. This is the
AODR's analysis for the AO; the authorization decision stays with the AO [[INT-101.A1]].

## Recommended responses

- Mitigate all nine risks through their POA&M items, keeping the interim measures: the
  internal-segment restriction for the GDT management service, the named custodian and GDT
  password change, and log export at each reconnect [[INT-101.A3]] [[ART-POAM]].
- RSK-003: the residual risk of the planner library flaws without a vendor fix needs an explicit
  AO risk acceptance at R-3, conditioned on the internal-network-only restriction
  [[INT-101.A3]].
- RSK-006: time-limit the authorization so it is revisited before the planner's end of support
  on 2027-06-30, and approve the PM's milestone extension for POAM-058 and POAM-069
  [[INT-101.A3]] [[INT-098.A3]].

## Risk Response (R-3)

The responses are confirmed: all nine risks are mitigated through their POA&M items, which
already carry the milestones, and the PM commits to the interim measures [[INT-102.A1]]
[[INT-103.A1]]. Residual risk stays moderate until Release 2.4 (2027-03-31) and, for RSK-003,
until firmware 5.2.1 and the rescan (2027-01-15); the planner library flaws without a vendor
fix remain until the planner is replaced and go to the AO for explicit acceptance, conditioned
on the planner staying on the station segment and loading data only through signed bundles
[[INT-102.A1]]. Because these risks are not fully mitigated, the fielding units and enclave
operators are told the potential impacts: maintenance actions are unattributable, planner and
GDT activity is unmonitored while disconnected, the GDT management service can be crashed from
the station segment, and response rests on draft plans until 2026-12-18. The ISSM sends the
notice with the decision and repeats it monthly; the units accept the constraints
[[INT-102.A2]] [[INT-103.A2]].
