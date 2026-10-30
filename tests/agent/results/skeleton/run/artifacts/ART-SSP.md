---
artifact_id: ART-SSP
run_id: agent-skeleton
produced_by_task: S-4
touched_by: [S-4]
sources: [INT-012.A1, INT-012.A2, INT-013.A1, INT-013.A2, INT-013.A3, INT-014.A1, INT-015.A1, INT-015.A2, INT-015.A3, INT-016.A1, INT-016.A2, INT-016.A3, ART-BASELINE]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Approach to control implementation

The plan holds one statement for each of the six baseline controls, in one file per family
under `artifacts/ssp/controls/` (ac, au, cm, ia, sc, si). Each statement names the allocated
components from `artifacts/data/allocation.yaml` and uses the tailored parameter values from
`artifacts/data/tailoring.yaml` [[ART-BASELINE]]. The controls are built into the gateway
software: the signed, SRG/STIG-hardened OS image sets the configuration of the OS, collector,
console and buffer and is checked nightly for drift [[INT-014.A1]]; the console federates
remote sign-in to the installation identity service and enforces lockout and session lock
[[INT-015.A1]] [[INT-016.A3]]; the OS, collector and console generate the agreed audit events
and forward them to the CSSP SIEM [[INT-013.A3]]; the host firewall denies by default
[[INT-015.A3]]; and flaws are fixed in a signed, tested monthly update bundle under the
configuration control board [[INT-016.A1]]. Status mix: 3 implemented (cm-6; au-2 and sc-7
shared with a provider), 3 partial (ac-2, ia-2, si-2), 0 planned, 0 inherited, 0 not
applicable.

## Inheritance and shared responsibility

All three providers hold current authorizations, and every inheritance is partial
[[INT-012.A1]] [[INT-012.A2]].

**Installation Network Enclave (sc-7).** The enclave firewall, intrusion detection and network
access control in front of every site switch enforce ESG's permitted flows at the enclave
edge. ESG keeps its own deny-by-default host firewall, the non-routing maintenance port and
the IP-less field radio [[INT-015.A3]].

**Installation ICAM Service (ia-2).** The identity service authenticates remote
administrators and auditors with DoD PKI and issues the group claims. ESG federates its
console to the service, maps claims to the `admin` and `auditor` roles, and handles local
authentication on the maintenance port [[INT-015.A1]].

**Installation Cybersecurity Service Provider (au-2).** The CSSP collects and correlates events
in its SIEM and co-owns the event list agreed on 2026-05-20. ESG generates the events on the
OS, collector and console and forwards them over TLS within one minute; the ESG ISSO reviews
the ESG report weekly [[INT-013.A3]].

## Open items

- **ac-2 (partial):** the shared `fieldtech` account is used by ten technicians, is not
  attributable, and its password is not changed when a technician leaves the team. Plan:
  per-technician accounts with smart-card login in release 2.3, planned for 2027-03
  [[INT-013.A2]].
- **ia-2 (partial):** maintenance-port sessions under `fieldtech` are not uniquely identified
  or associated with a person. Plan: the same release 2.3 change, which works without a path
  to the identity service [[INT-015.A2]].
- **si-2 (partial):** fielded units are updated only at quarterly site visits, beyond the
  30-day period; at the 2026-09-30 scan two of 12 units ran a 63-day-old bundle with 4 high
  and 9 medium vulnerabilities. Plan: remote update over the uplink in release 2.2, planned
  for 2026-12 [[INT-016.A2]].
