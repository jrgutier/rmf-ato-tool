---
artifact_id: ART-BND
run_id: valid-minimal
produced_by_task: P-11
touched_by: [P-11, P-16, C-1]
sources: [INT-002.A1, product/architecture.md]
---
# Authorization boundary, network architecture and data flows

## Boundary

The boundary encloses the relay appliance and the operator console; the identity provider
and the analysis enclave are external [[INT-002.A1]] [[product/architecture.md#boundary]].

## Network and data flow

Two appliance interfaces separate the field network from the enclave; reports flow from
field units through the relay to the enclave over TLS [[product/architecture.md#network]]
[[product/architecture.md#data-flow]].

## Update at C-1

C-1 confirmed the external identity provider as a leveraged service [[INT-003.A1]].

## Enterprise architecture

FDR sits at the edge of the analysis enclave behind the enclave firewall [[INT-025.A1]].
