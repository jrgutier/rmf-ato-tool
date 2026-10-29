---
artifact_id: ART-SSP
run_id: agent-skeleton
produced_by_task: S-4
touched_by: [S-4]
sources: [INT-013.A1, INT-013.A3, INT-013.A5, INT-014.A1, INT-014.A2, INT-015.A1, INT-016.A1, INT-016.A2, INT-016.A3, INT-017.A1, INT-017.A2, INT-018.A1, INT-018.A2, INT-019.A1, product/architecture.md#components, product/architecture.md#leveraged, product/conops.md#limitations, ART-ORG-CONTEXT]
---
# System security plan

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Authorization boundary | ESG-BND-1 | P-11 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: none | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | SP800-53B-MODERATE-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Approach to control implementation

Each of the six baseline controls has one statement in `artifacts/ssp/controls/<fam>.yaml`
(ac, au, cm, ia, sc, si), written for the components `allocation.yaml` assigns and with the
tailored parameter values. Controls are implemented mostly by the gateway itself: the signed,
SRG/STIG-hardened OS image applied by the build pipeline, the deny-by-default host firewall, the
console's federation and lockout settings, and local event generation on the OS, collector and
console [[INT-014.A1]] [[INT-016.A3]] [[INT-017.A1]] [[INT-013.A5]]. The ISSO runs the
operational parts (account approvals and quarterly reviews, weekly SIEM report, patch tracking),
and the RSSPO configuration control board approves every baseline change, including firewall
rules and update bundles [[INT-013.A1]] [[INT-014.A2]] [[INT-019.A1]]. The status mix is 3
implemented (au-2, cm-6, sc-7) and 3 partial (ac-2, ia-2, si-2); none is planned, inherited in
full or not applicable.

## Inheritance and shared responsibility

**Installation Network Enclave (sc-7).** The enclave provides the enclave firewall, intrusion
detection and network access control in front of every site switch and permits at the edge only
the registered ESG flows, under its ATO of 2025-11-20. ESG runs its own host firewall to the
same rules, keeps the maintenance port and radio separated from the uplink, and tells the
enclave before any new flow [[INT-018.A2]] [[INT-016.A3]] [[product/architecture.md#leveraged]].

**Installation ICAM Service (ia-2).** The ICAM service issues identities, validates the DoD PKI
credential, runs the account workflow for remote ESG users and asserts identity and group claim
to the console, covered by the enclave ATO. ESG configures the federation, maps claims to the
`admin` and `auditor` roles, refuses unauthenticated users, and owns the local accounts on the
maintenance port entirely [[INT-018.A1]] [[INT-016.A1]].

**Installation Cybersecurity Service Provider (au-2).** The CSSP agreed the ESG event list on
2026-05-20, collects and correlates ESG events in its SIEM and joins the annual event-list
review, under its ATO of 2026-01-30. ESG generates the events on its own components and forwards
them over TLS, and the ISSO reads the ESG-specific report weekly [[INT-015.A1]] [[INT-013.A5]].

## Open items

- **ac-2 (partial).** The shared `fieldtech` account used by about 10 field technicians is not
  attributable to a person, and its password changes every 90 days rather than when a technician
  leaves. Plan: per-technician local accounts with smart-card login in release 2.3, planned for
  2027-03 [[INT-013.A3]] [[product/conops.md#limitations]].
- **ia-2 (partial).** The same `fieldtech` account means technicians on the maintenance port are
  not uniquely identified and their sessions are not associated with a person; remote users are.
  Plan: the same release 2.3 change [[INT-016.A2]] [[INT-017.A1]].
- **si-2 (partial).** Fielded units are updated only at quarterly site visits, so the 30-day
  installation period is not met; two units ran a 63-day-old bundle at the last scan. Plan:
  remote update in release 2.2, planned for 2026-12, with each overdue unit tracked in a POA&M
  item until then [[INT-019.A1]] [[INT-017.A2]] [[ART-ORG-CONTEXT]].
