---
artifact_id: ART-BND
run_id: agent-skeleton
produced_by_task: P-11
touched_by: [P-11, C-1]
sources: [product/architecture.md#boundary, product/architecture.md#network, product/data-flows.md#top, INT-003.A1, INT-003.A2, INT-003.A3, INT-003.A4, INT-004.A1, INT-004.A2, INT-004.A3, INT-005.A5]
---
# Authorization boundary, network architecture and data flows

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

## Authorization boundary

The boundary holds the six components the inventory points to: the gateway appliance
(CMP-GW-HW), its operating system (CMP-GW-OS), the collector (CMP-COLLECTOR), the console
(CMP-WEBUI), the buffer (CMP-STORE) and the paired field sensor nodes (CMP-SENSOR-NET)
[[INT-003.A1]] [[ART-INV]]. All sites share one configuration baseline and are authorized as
one system; the installation network switch port is the edge [[product/architecture.md#boundary]].
The AO confirmed this set as everything the program builds and funds [[INT-004.A1]], and
stated that the maintenance port is inside the boundary and the laptop that uses it is an
entry point to assess; any new flow returns the boundary to the AO [[INT-004.A3]]. The
component records live in `artifacts/data/boundary.yaml`.

## Network architecture

The uplink, on the enclave VLAN, permits outbound TLS 1.3 to IODS, outbound syslog over TLS
to the CSSP and inbound HTTPS to the console from the management VLAN only; the host firewall
denies all other traffic in both directions [[INT-003.A2]]. The maintenance port is off unless
a technician enables it with the shelter key switch, serves only the console on a link-local
address and does not route to the uplink [[product/architecture.md#network]]. Sensor nodes
reach the gateway only over the paired, encrypted radio and have no IP connectivity; the
enclave firewall repeats the permitted flows at the enclave edge [[INT-003.A2]].

## Data flows

Seven flows are documented [[product/data-flows.md#top]] [[INT-003.A3]]:

| Flow | Path | Crosses the edge | Protection |
|---|---|---|---|
| DF-1 | sensor node to collector, field radio | no | paired encrypted link; unpaired nodes and malformed messages rejected |
| DF-2 | collector to buffer | no | local, encrypted data partition |
| DF-3 | collector to IODS, uplink | yes | TLS 1.3 with mutual certificates |
| DF-4 | gateway to CSSP SIEM, uplink | yes | syslog over TLS |
| DF-5 | admin workstation to console, uplink | yes | HTTPS; sign-in through the identity service |
| DF-6 | console to identity service, uplink | yes | TLS; signed assertions |
| DF-7 | technician laptop to console, maintenance port | enters on site | HTTPS on link-local; local sign-in |

Telemetry is buffered and forwarded oldest first when IODS returns
[[product/data-flows.md#telemetry]].

## External components

Four systems sit outside the boundary, each with its own authorization, so the AO does not
re-authorize them here [[INT-004.A2]] [[INT-003.A4]]:

- **CMP-IODS** receives telemetry over IC-1 under an interconnection agreement signed
  2026-04-02; ATO to 2029-03-15 [[product/architecture.md#interconnections]].
- **CMP-ICAM** authenticates remote administrators with DoD PKI and runs the account workflow;
  covered by the enclave authorization [[product/architecture.md#leveraged]].
- **CMP-ENCLAVE** provides the enclave firewall, intrusion detection and network access
  control; ATO 2025-11-20 [[product/architecture.md#leveraged]].
- **CMP-CSSP** collects and correlates logs and supports incident response; ATO 2026-01-30
  [[product/architecture.md#leveraged]].

Leveraged authorizations are recorded by C-1.

## Leveraged authorizations (C-1)

C-1 linked the external components to the leveraged authorizations in
`artifacts/data/leveraged-authorizations.yaml`: CMP-ENCLAVE and CMP-ICAM to LA-01 (the enclave
authorization, which covers the ICAM service) and CMP-CSSP to LA-02. CMP-IODS stays an
interconnection only, since the system sends data to it but inherits no controls from it
[[INT-005.A5]] [[product/architecture.md#leveraged]]. No component moved across the boundary.
