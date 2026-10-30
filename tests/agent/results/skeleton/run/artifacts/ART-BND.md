---
artifact_id: ART-BND
run_id: agent-skeleton
produced_by_task: P-11
touched_by: [P-11, C-1]
sources: [product/architecture.md#boundary, product/architecture.md#network, product/data-flows.md#top, INT-003.A1, INT-003.A3, INT-004.A1, INT-004.A2, INT-005.A5]
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
| Security categorization | C/I/A MODERATE/MODERATE/LOW; overlays: CNSSI1253F-ATT6-PRIVACY-ACCT | C-2 |
| Categorization approved | yes (PER-AODR) | C-3 |
| Control baseline | CNSSI1253-M-M-L-SUBSET-6 | S-1 |
<!-- END rmf:facts -->

## Authorization boundary

The boundary holds six components: CMP-GW-HW, CMP-GW-OS, CMP-COLLECTOR, CMP-WEBUI and
CMP-STORE on the gateway appliance, and CMP-SENSOR-NET for the paired field sensor nodes
[[INT-003.A1]]. Every inventory item (INV-001..INV-008) belongs to one of them [[ART-INV]].
All site units share one configuration baseline and one program owner, so the AO authorizes
them as one system; a unit off the approved baseline is not covered until restored
[[INT-004.A1]]. The edge is the installation network switch port on the gateway uplink
[[product/architecture.md#boundary]]. IODS, the ICAM service, the enclave and the CSSP stay
outside because each holds its own authorization and runs no ESG software [[INT-004.A2]]
[[INT-003.A3]]. The AO requires the maintenance port to stay non-routing and any new external
interface to return for approval before it is enabled [[INT-004.A3]].

## Network architecture

The uplink, on the ESG VLAN of the installation enclave, permits only outbound TLS 1.3 to
IODS, outbound syslog over TLS to the CSSP SIEM, TLS to the identity service, and inbound
HTTPS to the console from the management VLAN; the host firewall denies everything else, and
the enclave firewall enforces the same flows at the enclave edge
[[product/architecture.md#network]] [[INT-003.A2]]. The maintenance port is disabled until a
technician turns the shelter key switch, serves the console on a link-local address and does
not route to the uplink. Sensor nodes have no IP connectivity; they reach only their paired
gateway over the encrypted field radio [[INT-003.A2]].

## Data flows

| Flow | Crosses the edge | Protection |
|---|---|---|
| DF-1 nodes → collector | no | paired, encrypted radio; unpaired nodes and malformed messages rejected |
| DF-2 collector → buffer | no | local; encrypted data partition |
| DF-3 collector → IODS | yes | TLS 1.3, mutual certificate authentication |
| DF-4 gateway → CSSP SIEM | yes | syslog over TLS |
| DF-5 admin workstation → console | yes | HTTPS, sign-in through the identity service |
| DF-6 console → identity service | yes | TLS, signed assertions |
| DF-7 technician laptop → console | no (on-site maintenance port) | HTTPS on link-local address, local sign-in |

Flows and protections are those of the product data-flow table [[product/data-flows.md#top]],
confirmed by the ISSE [[INT-003.A2]] [[INT-003.A4]].

## External components

| Component | Type | Relationship | Authorization |
|---|---|---|---|
| CMP-IODS | interconnection | receives telemetry (IC-1) under an interconnection agreement | separate ATO |
| CMP-ICAM | service | PKI sign-in for remote administrators and auditors (IC-2) | covered by the enclave authorization |
| CMP-ENCLAVE | service | enclave firewall, intrusion detection, network access control | separate ATO |
| CMP-CSSP | service | SIEM collection, monitoring, incident response | separate ATO |

Relationships and authorizations come from the architecture's interconnection and leveraged
authorization tables [[product/architecture.md#interconnections]]
[[product/architecture.md#leveraged]]; leveraged authorizations are recorded in C-1
[[INT-004.A2]].

C-1 linked the external components to the leveraged authorizations: CMP-ENCLAVE and
CMP-ICAM to LA-01 (the enclave ATO, which covers the ICAM service) and CMP-CSSP to LA-02;
CMP-IODS is an interconnection only, not a leveraged authorization [[INT-005.A5]].
