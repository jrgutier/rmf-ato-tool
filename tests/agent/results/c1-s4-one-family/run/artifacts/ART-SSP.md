---
artifact_id: ART-SSP
run_id: agent-c1-s4-one-family
produced_by_task: S-4
touched_by: [S-4]
sources: [INT-011.A1, INT-011.A2, INT-012.A1, INT-013.A1, INT-013.A2, INT-013.A3, INT-014.A1, INT-015.A1, INT-015.A2, ART-BASELINE, product/conops.md#limitations]
---
# System security plan

<!-- BEGIN rmf:facts -->
| Fact | Value | Set by |
|---|---|---|
| System name | Example Sensor Gateway | C-1 |
| Acronym | ESG | C-1 |
| System ID | ESG-001 | C-1 |
| Aliases | none | C-1 |
| Life-cycle state | under-development | C-1 |
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-55 | S-1 |
<!-- END rmf:facts -->

## Approach to control implementation

The control statements live in `artifacts/ssp/controls/ac.yaml`, one per baseline control, each
allocated to the components named in `allocation.yaml` [[ART-BASELINE]]. Account, role, sign-in,
lockout and session controls are implemented in the admin web console (CMP-WEBUI); the gateway
OS (CMP-GW-OS) enforces service privileges, the deny-by-default host firewall and audit
generation; the collector and field radio enforce pairing on the sensor link [[INT-011.A1]]
[[INT-011.A2]] [[INT-014.A1]]. Of the 55 AC statements, 39 are implemented, 9 partial and 7 not
applicable; none is planned-only or fully inherited [[INT-012.A1]].

## Inheritance and shared responsibility

**Installation ICAM Service** (covered by the enclave ATO): authenticates remote administrators
and auditors with DoD PKI and runs the account workflow and account disabling (ac-2, ac-2.1,
ac-2.3, ac-2.13); ESG approves requests, maps group claims to its roles and manages its local
accounts [[INT-015.A1]] [[INT-013.A1]].

**Installation Network Enclave** (ATO 2025-11-20): enforces the permitted flows at the enclave
firewall and provides the managed access point and network access control (ac-4, ac-17,
ac-17.3); ESG keeps its host firewall rules consistent with the enclave's [[INT-015.A1]].

**Installation Cybersecurity Service Provider** (ATO 2026-01-30): correlates ESG events in the
SIEM and alerts the ISSO on atypical use and remote-session anomalies (ac-2.12, ac-17.1); ESG
generates and forwards the agreed events within one minute [[INT-015.A2]] [[INT-013.A3]].

## Open items

All nine partial controls trace to the two disclosed limitations or to the emergency account
[[product/conops.md#limitations]]:

- ac-2, ac-2.1, ac-2.3, ac-2.7, ac-2.9, ac-2.13, ac-6.5, ac-6.9: the shared `fieldtech` account
  cannot be attributed, managed or disabled per technician; per-technician local accounts with
  smart-card login are planned in release 2.3 (2027-03), and the risk goes to the POA&M
  [[INT-013.A2]].
- ac-2.2: the `esgadmin` emergency account is logged and reported on use but not disabled
  automatically; the ISSM is to plan automatic disabling [[INT-013.A2]].

The field patch-cadence limitation does not affect an AC control; it belongs to families outside
this run's control subset [[INT-012.A2]].
